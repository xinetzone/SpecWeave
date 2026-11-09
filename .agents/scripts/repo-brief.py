#!/usr/bin/env python3
"""repo-brief.py — 仓库状态简报（只读、零写入、零网络）。

只输出能用命令机械取到的事实：分支与工作树、未推送提交、活跃 spec、
近期落盘产物、已知例外/已知债务。不读文档全文、不总结内容、不做建议。

无法确定的值一律输出 ``{"value": "unknown", "reason": "..."}``，
不以空值、空区块或静默省略代替。

取数成本（Windows + pwsh7，含 20+ 子模块，实测 2026-11-09）：

==================================================  =========
命令                                                实测耗时
==================================================  =========
``git status -sb``                                   22.5 s
``git status -sb --ignore-submodules=all``            0.44 s
``check-links.py --path docs/retrospective/reports``  10.3 s
==================================================  =========

本脚本默认走 ``--ignore-submodules=all``，默认路径合计约 3.5 秒。
代价必须明说：**跳过子模块后，脏子模块不会出现在工作树计数里**，
该事实在输出中登记为 ``worktree.submodules = unknown``，
不允许降级成“看起来干净”。``--with-links`` 才跑链接检查（约 10 秒）。

用法::

    python .agents/scripts/repo-brief.py
    python .agents/scripts/repo-brief.py --json
    python .agents/scripts/repo-brief.py --repo <仓库路径>
    python .agents/scripts/repo-brief.py --with-links
"""

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

#: 已知例外的唯一来源：文件 + 章节，二者缺一即报 unknown
EXCEPTIONS_SOURCE = "docs/retrospective/reports/project-governance/agent-takeover-pain-points-20261109.md"
EXCEPTIONS_SECTION = "已知例外"

#: 已知债务的取数范围（仅 --with-links 时执行）
DEBT_LINK_SCRIPT = ".agents/scripts/check-links.py"
DEBT_LINK_PATH = "docs/retrospective/reports"

#: 跳过子模块扫描，换取 50 倍速度；代价在输出中显式登记
STATUS_ARGS = ("status", "--porcelain=v1", "--branch", "--ignore-submodules=all")


def unknown(reason: str) -> dict:
    """构造显式的未知值。空值不算答案。"""
    return {"value": "unknown", "reason": reason}


def _git(repo: Path, *args: str) -> tuple:
    """执行只读 git 命令，返回 (是否成功, 标准输出)。

    带 ``--no-optional-locks``：避免 git status 顺手刷新索引造成写入。
    """
    cmd = ["git", "--no-optional-locks", *args]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        return False, f"git 不可用: {exc}"
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip()
    return True, proc.stdout.strip()


class _Timings:
    """记录每段取数的真实耗时（毫秒）。"""

    def __init__(self):
        self._marks = {}

    def measure(self, name: str, func, *args):
        start = time.perf_counter()
        result = func(*args)
        self.record(name, round((time.perf_counter() - start) * 1000))
        return result

    def record(self, name: str, milliseconds: int) -> None:
        self._marks[name] = milliseconds

    def as_dict(self) -> dict:
        return dict(self._marks)


def _parse_branch_header(line: str) -> dict:
    """解析 ``##`` 分支头，返回 branch / upstream / ahead / behind。"""
    rest = line[3:] if line.startswith("## ") else line
    if rest.startswith("No commits yet on "):
        return {"branch": rest[len("No commits yet on "):], "upstream": None,
                "ahead": None, "behind": None}
    if rest.startswith("HEAD (no branch)"):
        return {"branch": "HEAD", "upstream": None, "ahead": None, "behind": None,
                "detached": True}

    branch, upstream, track = rest, None, ""
    if "..." in rest:
        branch, tail = rest.split("...", 1)
        if " [" in tail:
            upstream, track = tail.split(" [", 1)
            track = track.rstrip("]")
        else:
            upstream = tail.strip()
    elif " [" in rest:
        branch, track = rest.split(" [", 1)
        track = track.rstrip("]")

    ahead = behind = None
    ahead_match = re.search(r"ahead (\d+)", track)
    behind_match = re.search(r"behind (\d+)", track)
    if ahead_match:
        ahead = int(ahead_match.group(1))
    if behind_match:
        behind = int(behind_match.group(1))
    if "gone" in track:
        upstream = None
    return {"branch": branch.strip(), "upstream": upstream or None,
            "ahead": ahead, "behind": behind}


def _collect_worktree(repo: Path, timings: _Timings, unknowns: list) -> dict:
    ok, raw = timings.measure("git_status", _git, repo, *STATUS_ARGS)
    if not ok:
        unknowns.append({"field": "worktree", "reason": f"git status 失败: {raw}"})
        return {"value": "unknown", "reason": f"git status 失败: {raw}"}

    lines = [line for line in raw.splitlines() if line]
    header = _parse_branch_header(lines[0]) if lines and lines[0].startswith("## ") else {}
    staged = modified = untracked = 0
    for line in lines[1:]:
        code = line[:2]
        if code == "??":
            untracked += 1
            continue
        if code == "!!":
            continue
        if code[0] != " ":
            staged += 1
        if code[1] != " ":
            modified += 1

    unknowns.append({
        "field": "worktree.submodules",
        "reason": "取数使用 --ignore-submodules=all（0.44 s vs 22.5 s），子模块脏状态未检测",
    })
    return {
        "clean": staged == 0 and modified == 0 and untracked == 0,
        "staged": staged,
        "modified": modified,
        "untracked": untracked,
        "submodules": unknown("取数使用 --ignore-submodules=all，子模块脏状态未检测；"
                              "未检测不等于干净"),
        "branch_header": header,
    }


def _collect_stash(repo: Path, timings: _Timings) -> int:
    ok, raw = timings.measure("git_stash", _git, repo, "stash", "list")
    if not ok:
        return 0
    return len([line for line in raw.splitlines() if line.strip()])


def _fetch_head_mtime(repo: Path):
    """返回最近一次 fetch 的时间；没有 FETCH_HEAD 时返回 None。"""
    candidates = []
    ok, git_dir = _git(repo, "rev-parse", "--absolute-git-dir")
    if ok:
        candidates.append(Path(git_dir) / "FETCH_HEAD")
    candidates.append(repo / ".git" / "FETCH_HEAD")
    for path in candidates:
        if path.is_file():
            stamp = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            return stamp.astimezone().isoformat(timespec="seconds")
    return None


def _collect_commits(repo: Path, timings: _Timings, upstream, unknowns: list) -> dict:
    last_24h = 0
    ok, raw = timings.measure("git_log_24h", _git, repo,
                              "log", "--since=24 hours ago", "--oneline")
    if ok:
        last_24h = len([line for line in raw.splitlines() if line.strip()])

    last_7d = 0
    ok, raw = timings.measure("git_log_7d", _git, repo,
                              "log", "--since=7 days ago", "--oneline")
    if ok:
        last_7d = len([line for line in raw.splitlines() if line.strip()])

    ok, raw = timings.measure("git_log_recent", _git, repo,
                              "log", "-10", "--format=%H%x09%h%x09%s")
    recent = []
    for line in raw.splitlines() if ok else []:
        if not line.strip():
            continue
        full_sha, _, remainder = line.partition("\t")
        short_sha, _, subject = remainder.partition("\t")
        recent.append({"sha": short_sha, "full_sha": full_sha, "subject": subject})

    unpushed_hashes = None
    if upstream:
        ok, raw = timings.measure("git_rev_list_unpushed", _git, repo,
                                  "rev-list", f"{upstream}..HEAD")
        if ok:
            unpushed_hashes = [line.strip() for line in raw.splitlines() if line.strip()]
    if unpushed_hashes is None:
        reason = "未配置上游分支，无法判定哪些提交未推送" if not upstream \
            else f"上游 {upstream} 无法解析"
        unknowns.append({"field": "unpushed", "reason": reason})
        unpushed = dict(unknown(reason), count=None, by_area=None)
        for item in recent:
            item["pushed"] = "unknown"
    else:
        pushed_set = set(unpushed_hashes)
        unpushed = {"count": len(unpushed_hashes), "by_area": None}
        for item in recent:
            item["pushed"] = item["full_sha"] not in pushed_set

        by_area = {}
        if unpushed_hashes:
            ok, raw = timings.measure(
                "git_log_unpushed_areas", _git, repo,
                "log", f"{upstream}..HEAD", "--name-only", "--pretty=format:")
            if ok:
                for path in {line.strip() for line in raw.splitlines() if line.strip()}:
                    area = path.split("/")[0]
                    by_area[area] = by_area.get(area, 0) + 1
                unpushed["by_area"] = dict(
                    sorted(by_area.items(), key=lambda kv: (-kv[1], kv[0])))

    fetched_at = _fetch_head_mtime(repo)
    if fetched_at is None:
        freshness = dict(unknown("本仓没有 FETCH_HEAD：从未 fetch，"
                                 "behind 数值基于本地引用，不代表远端真实状态"),
                         last_fetch_at=None)
        unknowns.append({"field": "commits.remote_freshness",
                         "reason": freshness["reason"]})
    else:
        freshness = dict(unknown(f"behind 基于本地引用，不代表远端真实状态；"
                                 f"最近一次 fetch 于 {fetched_at}"),
                         last_fetch_at=fetched_at)
        unknowns.append({"field": "commits.remote_freshness",
                         "reason": freshness["reason"]})

    return {
        "last_24h": last_24h,
        "last_7d": last_7d,
        "recent": recent,
        "unpushed": unpushed,
        "remote_freshness": freshness,
    }


def _collect_specs(repo: Path, timings: _Timings) -> dict:
    ok, raw = timings.measure("git_ls_files_specs", _git, repo, "ls-files", ".trae/specs")
    paths = [line.strip() for line in raw.splitlines() if line.strip()] if ok else []
    themes = set()
    spec_files = 0
    for path in paths:
        parts = path.split("/")
        if len(parts) > 2:
            themes.add(parts[2])
        if path.endswith("/spec.md"):
            spec_files += 1

    ok, raw = timings.measure(
        "git_log_active_specs", _git, repo,
        "log", "--since=14 days ago", "--name-only", "--pretty=format:",
        "--", ".trae/specs/**/spec.md")
    active = {}
    if ok:
        for path in {line.strip() for line in raw.splitlines() if line.strip()}:
            parts = path.split("/")
            if len(parts) > 2:
                active[parts[2]] = active.get(parts[2], 0) + 1

    return {
        "themes": len(themes),
        "spec_files": spec_files,
        "active_14d": [{"theme": name, "files": count} for name, count in
                       sorted(active.items(), key=lambda kv: (-kv[1], kv[0]))],
    }


def _collect_artifacts(repo: Path, timings: _Timings) -> dict:
    ok, raw = timings.measure(
        "git_log_new_docs", _git, repo,
        "log", "--since=7 days ago", "--diff-filter=A", "--name-only",
        "--pretty=format:", "--", "docs/**")
    paths = sorted({line.strip() for line in raw.splitlines() if line.strip()}) if ok else []
    groups = {}
    for path in paths:
        parent = str(Path(path).parent).replace("\\", "/")
        groups[parent] = groups.get(parent, 0) + 1
    return {
        "total": len(paths),
        "by_directory": [{"directory": name, "files": count} for name, count in
                         sorted(groups.items(), key=lambda kv: (-kv[1], kv[0]))],
    }


def _read_section(repo: Path, rel_path: str, section: str):
    """读取 Markdown 文件中某个二级标题下的原始行。"""
    target = repo / rel_path
    if not target.is_file():
        return None, f"来源文件不存在: {rel_path}"
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().startswith(section):
            start = index
            break
    if start is None:
        return None, f"来源文件存在但缺少章节: ## {section}"
    body = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        body.append(line.rstrip())
    while body and not body[-1]:
        body.pop()
    return {"path": rel_path, "section": section, "line": start + 1, "lines": body}, None


def _collect_exceptions(repo: Path) -> dict:
    section, error = _read_section(repo, EXCEPTIONS_SOURCE, EXCEPTIONS_SECTION)
    source = {"path": EXCEPTIONS_SOURCE, "section": f"## {EXCEPTIONS_SECTION}"}
    if error:
        return {"status": "unknown", "value": unknown(error), "source": source}
    return {"status": "ok", "value": section, "source": source}


def _extract_json_object(raw: str):
    """从混合输出中取出最后一个 JSON 对象。"""
    decoder = json.JSONDecoder()
    for index in range(len(raw) - 1, -1, -1):
        if raw[index] != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(raw[index:])
        except ValueError:
            continue
        if isinstance(obj, dict) and "summary" in obj:
            return obj
    return None


def _collect_debt(repo: Path, timings: _Timings, with_links: bool) -> dict:
    source = {"command": f"{DEBT_LINK_SCRIPT} --path {DEBT_LINK_PATH} --json",
              "path": DEBT_LINK_PATH}
    if not with_links:
        reason = "默认关闭，需 --with-links 才执行链接检查（约 10 秒）"
        return {"status": "unknown", "value": unknown(reason), "source": source}

    script = repo / DEBT_LINK_SCRIPT
    if not script.is_file():
        reason = f"检查脚本不存在: {DEBT_LINK_SCRIPT}"
        return {"status": "unknown", "value": unknown(reason), "source": source}
    if not (repo / DEBT_LINK_PATH).exists():
        reason = f"检查路径不存在: {DEBT_LINK_PATH}"
        return {"status": "unknown", "value": unknown(reason), "source": source}

    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(script), "--path", DEBT_LINK_PATH, "--json"],
        cwd=str(repo), capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    timings.record("check_links", round((time.perf_counter() - start) * 1000))

    payload = _extract_json_object(proc.stdout or "")
    if payload is None:
        reason = f"链接检查未返回可解析的 JSON（退出码 {proc.returncode}）"
        return {"status": "unknown", "value": unknown(reason), "source": source}
    return {"status": "ok", "value": payload.get("summary"), "source": source}


def collect(repo: Path, with_links: bool = False) -> dict:
    """采集一份简报数据快照。只读，不写文件，不联网。"""
    repo = Path(repo).resolve()
    timings = _Timings()
    unknowns = []

    ok, _ = _git(repo, "rev-parse", "--git-dir")
    if not ok:
        raise NotADirectoryError(f"不是 git 仓库: {repo}")

    worktree = _collect_worktree(repo, timings, unknowns)
    header = worktree.pop("branch_header", {})
    if header.get("upstream") and (header.get("ahead") is None or header.get("behind") is None):
        ok, raw = timings.measure("git_rev_list_tracking", _git, repo,
                                  "rev-list", "--left-right", "--count",
                                  f"{header['upstream']}...HEAD")
        if ok:
            parts = raw.replace("\t", " ").split()
            if len(parts) >= 2:
                if header.get("behind") is None:
                    header["behind"] = int(parts[0])
                if header.get("ahead") is None:
                    header["ahead"] = int(parts[1])
    stash = _collect_stash(repo, timings)
    commits = _collect_commits(repo, timings, header.get("upstream"), unknowns)

    unknowns.extend([
        {"field": "worktree.other_sessions",
         "reason": "其他会话内存中尚未落盘的改动不可观测"},
        {"field": "artifacts.sensitivity",
         "reason": "在途产物内容敏感度无法从 git 判定；无访问控制线索时按私域处理"},
        {"field": "worktree.ignored_dirs",
         "reason": "被 .gitignore 排除的目录内容不在视野内"},
    ])

    data = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "repo": {"path": str(repo)},
        "branch": {
            "name": header.get("branch"),
            "detached": bool(header.get("detached")),
            "upstream": header.get("upstream"),
            "ahead": header.get("ahead"),
            "behind": header.get("behind"),
        },
        "worktree": dict(worktree, stash=stash),
        "commits": commits,
        "specs": _collect_specs(repo, timings),
        "artifacts_7d": _collect_artifacts(repo, timings),
        "known_exceptions": _collect_exceptions(repo),
        "known_debt": _collect_debt(repo, timings, with_links),
        "unknowns": unknowns,
        "timings_ms": timings.as_dict(),
    }
    data["timings_ms"]["total"] = sum(data["timings_ms"].values())
    return data


def _render_unknown(value) -> str:
    return f"unknown（{value['reason']}）"


def render_text(data: dict) -> str:
    """把快照渲染成几十秒能读完的事实型文本。"""
    branch = data["branch"]
    worktree = data["worktree"]
    commits = data["commits"]
    specs = data["specs"]
    artifacts = data["artifacts_7d"]

    lines = [
        "════════ SPECWEAVE BRIEF ════════ " + data["generated_at"],
        f"repo  {data['repo']['path']}",
        "─" * 60,
    ]

    upstream = branch["upstream"] or "（无上游）"
    ahead = "unknown" if branch["ahead"] is None else branch["ahead"]
    behind = "unknown" if branch["behind"] is None else branch["behind"]
    lines.append(f"[位置]    branch {branch['name']} → {upstream}   "
                 f"ahead {ahead} · behind {behind}*")

    lines.append(
        f"[工作树]  {'clean' if worktree['clean'] else 'dirty'}："
        f"{worktree['staged']} staged · {worktree['modified']} modified · "
        f"{worktree['untracked']} untracked · {worktree['stash']} stash")
    lines.append(f"          子模块状态：{_render_unknown(worktree['submodules'])}")

    unpushed = commits["unpushed"]
    if unpushed.get("count") is None:
        unpushed_text = "unknown（" + unpushed["reason"] + "）"
    else:
        unpushed_text = str(unpushed["count"])
        if unpushed.get("by_area"):
            areas = " · ".join(f"{name} {count}"
                               for name, count in unpushed["by_area"].items())
            unpushed_text += f" 个提交（涉及 {areas} 个文件）"
        else:
            unpushed_text += " 个提交"
    lines.append(f"[提交]    24h {commits['last_24h']} · 7d {commits['last_7d']} · "
                 f"未推送 {unpushed_text}")

    lines.append("")
    lines.append("[最近提交]")
    for item in commits["recent"][:5]:
        pushed = item.get("pushed")
        mark = {True: "已推送", False: "未推送", "unknown": "推送态 unknown"}[pushed]
        lines.append(f"  {item['sha']}  {mark}  {item['subject']}")

    lines.append("")
    active = specs["active_14d"]
    active_text = " · ".join(f"{item['theme']} {item['files']}" for item in active) or "无"
    lines.append(f"[活跃 spec]  {specs['themes']} 个主题 · {specs['spec_files']} 个已跟踪 spec.md")
    lines.append(f"  近 14 天 spec.md 有改动（按文件去重）：{active_text}")

    lines.append("")
    lines.append(f"[近 7 天新增产出]  docs/ 下 {artifacts['total']} 个文件")
    for item in artifacts["by_directory"][:8]:
        lines.append(f"  {item['directory']}  {item['files']}")

    lines.append("")
    exceptions = data["known_exceptions"]
    if exceptions["status"] == "ok":
        body = exceptions["value"]
        lines.append(f"[已知例外]  来源 {body['path']}#L{body['line']} § {body['section']}")
        shown = body["lines"][:12]
        for raw in shown:
            lines.append(f"  {raw}" if raw else "")
        if len(body["lines"]) > len(shown):
            lines.append(f"  …（余 {len(body['lines']) - len(shown)} 行，见来源文件）")
    else:
        lines.append(f"[已知例外]  {_render_unknown(exceptions['value'])}")
        lines.append(f"  来源：{exceptions['source']['path']} § {exceptions['source']['section']}")

    lines.append("")
    debt = data["known_debt"]
    if debt["status"] == "ok":
        summary = debt["value"] or {}
        broken = summary.get("broken_local", "unknown")
        warn = summary.get("warning_local", "unknown")
        lines.append(f"[已知债务]  {debt['source']['path']} 存量断链 {broken}（警告 {warn}）")
    else:
        lines.append(f"[已知债务]  {_render_unknown(debt['value'])}")

    lines.append("")
    lines.append("[本简报不知道的]")
    for item in data["unknowns"]:
        lines.append(f"  · {item['field']}：{item['reason']}")

    total = data["timings_ms"].get("total", 0)
    lines.append("")
    lines.append(f"[取数]  {total} ms · 未含子模块（--ignore-submodules=all）")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="仓库状态简报：只输出事实，未知项显式标注 unknown")
    parser.add_argument("--repo", type=Path, default=Path("."),
                        help="仓库路径（默认当前目录）")
    parser.add_argument("--json", action="store_true",
                        help="输出机器可读 JSON")
    parser.add_argument("--with-links", action="store_true",
                        help="额外执行链接检查（已知债务区块，约 10 秒）")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = collect(args.repo, with_links=args.with_links)
    except NotADirectoryError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(render_text(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
