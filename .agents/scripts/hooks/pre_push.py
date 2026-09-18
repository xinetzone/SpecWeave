#!/usr/bin/env python3
"""Pre-push 钩子入口：Git tree 对象规范序预检。

为什么拦在 pre-push 而不是 pre-commit：
坏 tree 的代价在「推送」这一步才兑现——本地 commit 完全正常，但启用 fsck
的接收端会整包拒绝（``treeNotSorted: not properly sorted``），且
``git push -f`` 无法绕过（对象被可达提交引用就必须进包上传）。pre-push
阶段推送范围已知，按真实范围校验成本最低、命中率最高。

stdin 输入（git 每行一条）:
    <local ref> <local sha> <remote ref> <remote sha>

检查范围构造:
    git rev-list --objects <local sha...> --not --remotes <remote sha...>
    - local sha 全零 → 删除分支，跳过
    - remote sha 全零或本地不存在 → 不加入排除集（新建分支/强推场景）

失败安全（宁可放行也不误伤正常推送）:
    - 非 git 仓库 / 无 HEAD / 检查脚本缺失 / 检查超时 → 警告并放行
    - 跳过开关: TREE_ORDER_CHECK_SKIP=1 或 SKIP=tree-order-check

环境变量:
    TREE_ORDER_CHECK_SKIP=1   完全跳过本检查

使用方式:
    由 .githooks/pre-push 自动调用（git push 时触发）
    手动复现: echo "<local ref> <sha> <remote ref> <sha>" | python .agents/scripts/hooks/pre_push.py
"""
from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import os
import subprocess
import sys
from pathlib import Path

ZERO_SHA = "0" * 40
CHECK_TIMEOUT = 900


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _skip_requested() -> tuple[bool, str]:
    if _env_truthy("TREE_ORDER_CHECK_SKIP"):
        return True, "TREE_ORDER_CHECK_SKIP=1"
    skip_env = os.environ.get("SKIP", "").strip().lower()
    if "tree-order" in skip_env or "tree_order" in skip_env:
        return True, f"SKIP={os.environ.get('SKIP', '')}"
    return False, ""


def find_project_root() -> Path:
    """以钩子文件位置定位项目根：`.agents/scripts/hooks/pre_push.py` 上溯三级。

    不用 `git rev-parse --show-toplevel`：core.hooksPath 可以指向仓库外目录
    （全局模板、跨仓库验证），此时 cwd 所属仓库并非钩子文件的所属仓库。
    """
    return Path(__file__).resolve().parents[3]


def _has_commit(sha: str) -> bool:
    """本地是否已有该提交对象（远端 sha 可能尚未拉取，不能进排除集）。"""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"],
        capture_output=True,
    )
    return result.returncode == 0


def parse_push_specs(stdin_text: str) -> list[tuple[str, str, str, str]]:
    """解析 git 传入的推送规格行。"""
    specs = []
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) == 4:
            specs.append((parts[0], parts[1], parts[2], parts[3]))
    return specs


def build_rev_args(specs: list[tuple[str, str, str, str]]) -> list[str] | None:
    """由推送规格构造 rev-list 参数；无可检查对象时返回 None。"""
    local_shas = list(dict.fromkeys(s[1] for s in specs if s[1] != ZERO_SHA))
    if not local_shas:
        return None  # 纯删除推送：没有新对象要上传

    rev_args = [*local_shas, "--not", "--remotes"]
    for remote_sha in dict.fromkeys(s[3] for s in specs if s[3] != ZERO_SHA):
        if _has_commit(remote_sha):
            rev_args.append(remote_sha)
    return rev_args


def main() -> int:
    skip, reason = _skip_requested()
    print("=" * 60)
    print("🌳 Git tree 规范序预检 (Pre-push Hook)")
    print("=" * 60)

    if skip:
        print(f"\n⚠️  检测到 {reason}，已跳过 tree 规范序预检。")
        print("   请自行确认本次推送不含非规范序 tree（远端 fsck 会整包拒绝）。\n")
        return 0

    project_root = find_project_root()
    check_script = project_root / ".agents" / "scripts" / "check-tree-order.py"
    if not check_script.exists():
        print("\n⚠️  未找到 check-tree-order.py，跳过本检查。\n")
        return 0

    specs = parse_push_specs(sys.stdin.read())
    rev_args = build_rev_args(specs)
    if rev_args is None:
        print("\n✅ 无可检查对象（删除分支或空推送）。\n")
        return 0

    range_spec = " ".join(rev_args)
    print(f"\n📋 推送范围: {range_spec}\n")

    try:
        result = subprocess.run(
            [sys.executable, str(check_script), f"--range={range_spec}"],
            timeout=CHECK_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        print("\n⚠️  tree 规范序预检超时，已放行。\n")
        return 0
    except OSError as exc:
        print(f"\n⚠️  无法执行检查脚本，已放行: {exc}\n")
        return 0

    if result.returncode != 0:
        print("\n" + "=" * 60)
        print("❌ 推送已阻断：检测到非规范序 tree 对象")
        print("  远端 fsck 会以 treeNotSorted 整包拒绝本次推送（git push -f 也无法绕过）")
        print("")
        print("🔓 确认风险后可临时跳过:")
        print("  TREE_ORDER_CHECK_SKIP=1 git push")
        print("=" * 60)
        return 1

    print("\n✅ tree 规范序预检通过。\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())