#!/usr/bin/env python3
"""check-tree-order.py: Git tree 对象规范序预检。

背景（2026-09-17 推送事故根因）：
git 要求 tree 条目严格按 name 的字节序排列（目录名等价于 name + "/"，
0x2F）。任何绕过 index/write-tree 直接向对象库写入 tree 的工具（手写对象
脚本、在大小写不敏感排序下遍历目录的实现等）都会产出「顺序不合规」的
tree。此类对象在本地毫无症状，但推送到启用 fsck 的接收端（gitcode 等）
会整包被拒：

    remote: error: object <sha>: treeNotSorted: not properly sorted
    remote unpack failed: index-pack abnormal exit

且 `git push -f` 无法绕过——只要该对象被可达提交引用，就必须进包上传。
本预检把问题拦在推送之前，而不是等到远端拒绝后重写历史。

判定依据（等价于接收端 fsck）：
- 条目排序键 = name 字节；目录条目为 name + "/"
- 相邻键出现 key[i] >= key[i+1] 即判定违规

实现要点：
- 枚举用 `git rev-list --objects`，类型过滤用 `git cat-file --batch-check`
  （只读对象头），tree 内容用一次 `git cat-file --batch` 读原始字节，
  全程两个常驻子进程，不做逐对象进程调用。

用法:
    python check-tree-order.py                    # 自动推导范围
    python check-tree-order.py --range origin/main..HEAD
    python check-tree-order.py --range HEAD       # 全量历史（慢，审计用）
    python check-tree-order.py --json
退出码: 0=全部规范序（或无对象可查）, 1=发现不合规 tree
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import shlex
import subprocess
import sys

from lib.cli import (
    print_error,
    print_header,
    print_pass,
    print_summary,
    print_warn,
    setup_safe_output,
)

# 单个 git 调用超时（全量扫描历史时 rev-list 可能较慢）
GIT_TIMEOUT = 300

# 文本输出中最多展开的违规 tree 数（其余仅计数，避免刷屏）
MAX_REPORTED_TREES = 10

# 目录条目的 mode（git 原始字节，4 位/6 位两种写法）
DIR_MODES = (b"40000", b"040000")


class GitError(RuntimeError):
    """git 命令执行失败。"""


def _git(*args: str) -> bytes:
    """运行只读 git 命令并返回 stdout 原始字节。

    返回 bytes 而非 str：tree 条目名不做编码假设，避免非 UTF-8 路径被
    自动解码时抛异常。
    """
    result = subprocess.run(
        ["git", "--no-optional-locks", *args],
        capture_output=True,
        timeout=GIT_TIMEOUT,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def _git_ok(*args: str) -> bool:
    """探测型 git 调用：失败不抛异常，仅返回 False。"""
    try:
        _git(*args)
    except (GitError, OSError, subprocess.SubprocessError):
        return False
    return True


def resolve_default_range() -> tuple[str, str]:
    """推导默认检查范围，返回 (rev-list 参数串, 范围说明)。

    优先「未推送提交」——推送事故的正中靶心；若已与远端同步（或本地无
    远端跟踪 ref），退化为校验 HEAD 提交树：成本仅当前工作树规模，
    仍能拦住从远端拉入或合并进来的坏对象。
    """
    if _git_ok("rev-parse", "--verify", "HEAD"):
        has_remote = bool(_git("for-each-ref", "--count=1", "refs/remotes").strip())
        if has_remote:
            count = int(_git("rev-list", "--count", "HEAD", "--not", "--remotes").strip() or b"0")
            if count > 0:
                return "HEAD --not --remotes", f"未推送提交（{count} 个）"
            return "-1 HEAD", "HEAD 提交树（无未推送提交）"
        return "-1 HEAD", "HEAD 提交树（无远端跟踪 ref）"
    return "-1 HEAD", "HEAD 提交树"


def list_objects(rev_args: list[str]) -> tuple[list[str], dict[str, str]]:
    """枚举范围内的全部对象，返回 (sha 列表, sha→路径 映射)。"""
    out = _git("rev-list", "--objects", *rev_args)
    shas: list[str] = []
    paths: dict[str, str] = {}
    for line in out.split(b"\n"):
        if not line.strip():
            continue
        sha, _, path = line.partition(b" ")
        hexsha = sha.decode("ascii", "replace")
        shas.append(hexsha)
        if path and hexsha not in paths:
            # 同一 tree 对象可出现在多个路径，取首次出现位置用于报错定位
            paths[hexsha] = path.decode("utf-8", "replace")
    return shas, paths


def read_types(shas: list[str]) -> dict[str, str]:
    """批量查询对象类型（--batch-check 只读对象头，不读内容）。"""
    if not shas:
        return {}
    payload = "".join(f"{s}\n" for s in shas).encode("ascii")
    out = subprocess.run(
        ["git", "--no-optional-locks", "cat-file", "--batch-check"],
        input=payload,
        capture_output=True,
        timeout=GIT_TIMEOUT,
    ).stdout
    types: dict[str, str] = {}
    for line in out.split(b"\n"):
        parts = line.split()
        if len(parts) >= 2:
            types[parts[0].decode("ascii", "replace")] = parts[1].decode("ascii", "replace")
    return types


def read_trees(tree_shas: list[str]) -> dict[str, bytes]:
    """批量读取 tree 对象原始字节。

    `git cat-file --batch` 输出格式: ``<sha> tree <size>\\n<size 字节>\\n``，
    入参已按类型过滤，故不再判断返回类型。
    """
    if not tree_shas:
        return {}
    payload = "".join(f"{s}\n" for s in tree_shas).encode("ascii")
    out = subprocess.run(
        ["git", "--no-optional-locks", "cat-file", "--batch"],
        input=payload,
        capture_output=True,
        timeout=GIT_TIMEOUT,
    ).stdout
    trees: dict[str, bytes] = {}
    pos = 0
    while pos < len(out):
        nl = out.find(b"\n", pos)
        if nl < 0:
            break
        header = out[pos:nl].split()
        pos = nl + 1
        if len(header) < 3:
            # "<sha> missing"：对象在枚举后被回收，跳过
            continue
        size = int(header[2])
        trees[header[0].decode("ascii", "replace")] = out[pos:pos + size]
        pos += size + 1  # 跳过对象内容后的换行
    return trees


def parse_entries(content: bytes) -> list[tuple[bytes, bytes]]:
    """解析 tree 原始格式: ``<mode> SP <name> NUL <20 字节 sha>``。"""
    entries: list[tuple[bytes, bytes]] = []
    pos = 0
    while pos < len(content):
        sp = content.index(b" ", pos)
        mode = content[pos:sp]
        nul = content.index(b"\x00", sp + 1)
        entries.append((mode, content[sp + 1:nul]))
        pos = nul + 21
    return entries


def sort_key(mode: bytes, name: bytes) -> bytes:
    """git base_name_compare 的等价排序键：目录名视为 name + "/"。"""
    return name + (b"/" if mode in DIR_MODES else b"")


def find_violations(content: bytes) -> list[dict]:
    """返回首个违规位置起的相邻越序条目（每条违规一个 dict）。"""
    entries = parse_entries(content)
    keys = [sort_key(mode, name) for mode, name in entries]
    violations = []
    for i in range(len(entries) - 1):
        if keys[i] >= keys[i + 1]:
            violations.append({
                "index": i,
                "left": entries[i][1].decode("utf-8", "replace"),
                "right": entries[i + 1][1].decode("utf-8", "replace"),
                "duplicate": keys[i] == keys[i + 1],
            })
    return violations


def check_tree_order(rev_args: list[str], label: str) -> dict:
    """校验指定范围内所有 tree 对象的条目顺序。"""
    shas, paths = list_objects(rev_args)
    types = read_types(shas)
    tree_shas = [s for s in shas if types.get(s) == "tree"]
    trees = read_trees(tree_shas)

    violations = []
    for sha in tree_shas:
        content = trees.get(sha)
        if content is None:
            continue
        bad = find_violations(content)
        if bad:
            violations.append({
                "tree": sha,
                "path": paths.get(sha, ""),
                "entries": bad,
            })

    return {
        "range": " ".join(rev_args),
        "range_label": label,
        "object_count": len(shas),
        "tree_count": len(tree_shas),
        "violation_count": len(violations),
        "violations": violations,
    }


def print_report(result: dict) -> None:
    """输出人类可读报告。"""
    print_header(" Git tree 对象规范序预检")
    print(f"  检查范围: {result['range']}  [{result['range_label']}]")
    print(f"  对象: {result['object_count']} 个（其中 tree {result['tree_count']} 个）")
    print()

    if result["violation_count"] == 0:
        print_pass("通过 — 所有 tree 条目均为 git 规范序")
        print_summary(pass_count=1, warn_count=0, error_count=0)
        return

    print_error(
        f"发现 {result['violation_count']} 个不合规 tree — "
        "推送到启用 fsck 的远端将被整包拒绝（treeNotSorted）"
    )
    print("-" * 60)
    for item in result["violations"][:MAX_REPORTED_TREES]:
        path = item["path"] or "(提交的根 tree)"
        print(f"\n  ✗ {item['tree']}")
        print(f"     路径: {path}")
        for bad in item["entries"][:3]:
            if bad["duplicate"]:
                print(f"     条目重复: '{bad['left']}'")
            else:
                print(f"     越序: '{bad['left']}' 排在 '{bad['right']}' 之前")
    if result["violation_count"] > MAX_REPORTED_TREES:
        print(f"\n  ... 及其余 {result['violation_count'] - MAX_REPORTED_TREES} 个不合规 tree")

    print()
    print("💡 成因: 绕过 index/write-tree 直接写对象库的工具（大小写不敏感排序等）产出非规范序 tree")
    print("💡 修复: 重写引入该对象的提交，让 git 重新生成 tree（rebase / cherry-pick），")
    print("        或改用 `git mktree` 生成规范序 tree；修复后重跑本检查复核")
    print_summary(pass_count=0, warn_count=0, error_count=result["violation_count"])


def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(description="Git tree 对象规范序预检（treeNotSorted 门禁）")
    parser.add_argument(
        "--range",
        dest="rev_range",
        default=None,
        help="git rev-list 范围表达式（如 'origin/main..HEAD'；'HEAD' 表示全量历史）",
    )
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = parser.parse_args()

    if not _git_ok("rev-parse", "--git-dir"):
        print_warn("当前目录不是 git 仓库，跳过 tree 规范序预检。")
        return 0

    if not _git_ok("rev-parse", "--verify", "HEAD"):
        print_warn("仓库尚无提交（HEAD 不存在），跳过 tree 规范序预检。")
        return 0

    if args.rev_range:
        rev_args = shlex.split(args.rev_range)
        label = "显式指定范围"
    else:
        spec, label = resolve_default_range()
        rev_args = shlex.split(spec)

    try:
        result = check_tree_order(rev_args, label)
    except (GitError, OSError, subprocess.SubprocessError) as exc:
        # 失败安全：钩子场景下环境异常不应阻塞推送，但必须显式暴露
        print_warn(f"检查范围无法解析或不完整（{exc}），跳过 tree 规范序预检。")
        return 0

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)

    return 1 if result["violation_count"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())