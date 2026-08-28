#!/usr/bin/env python3
"""CI gate：扫描 docs/ 的 index.md/toctree 导航完整性。

检查项：
  1) 每个 toctree 引用都能解析到真实存在的 .md（无断链）；
  2) 从 docs/index.md 沿 index.md 的 toctree 链 BFS，所有 .md 内容文档均可达（无孤立）；
  3) 目录文件清单一致性：含 toctree 的 index.md 须收录其目录内全部内容；
  4) 含子目录的目录必须存在 index.md（导航完整性）。

用法:
    python scripts/check-toctrees.py               # 扫描 docs/（默认）
    python scripts/check-toctrees.py [PATH...]     # 扫描指定 index.md/目录（仅断链检查）
    python scripts/check-toctrees.py --self-test   # 破坏性探针双向自检

退出码:
    0  全部通过（CI 通过）；或自检通过
    1  存在问题（CI gate 拦截）；或自检发现 gate 失效
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCAN = (ROOT,)
EXCLUDE_DIRS = {"_build", "_static", "_templates", ".git", "__pycache__"}
INDEX_NAME = "index.md"

_FENCE_OPEN = re.compile(r"^(?P<fence>`{3,}|:{3,})\s*\{toctree\}(?:\s*\{(?:hidden|glob)\})?\s*$")
_FENCE_CLOSE = re.compile(r"^(?:`{3,}|:{3,})\s*$")
_SKIP_ENTRY = re.compile(r"^(https?://|mailto:|[#{\[]|genindex|modindex|search)$")
_OPTION = re.compile(r"^\s*:")


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def iter_index_files(paths) -> list[Path]:
    files: list[Path] = []
    for base in paths:
        p = Path(base)
        if not p.exists():
            print(f"错误: 路径不存在: {p}", file=sys.stderr)
            continue
        if p.is_file():
            if p.name == INDEX_NAME:
                files.append(p)
        else:
            for f in p.rglob(INDEX_NAME):
                if f.is_file() and not any(part in EXCLUDE_DIRS for part in f.parts):
                    files.append(f)
    return sorted(set(files))


def extract_entries(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"读取失败: {_display(path)}: {exc}", file=sys.stderr)
        return []
    lines = text.splitlines()
    entries: list[str] = []
    i, n = 0, len(lines)
    while i < n:
        if not _FENCE_OPEN.match(lines[i]):
            i += 1
            continue
        i += 1
        while i < n and not _FENCE_CLOSE.match(lines[i]):
            body = lines[i].strip()
            if body and not _OPTION.match(body):
                entries.append(body)
            i += 1
        i += 1
    return entries


def resolve_target(src_dir: Path, entry: str, srcdir: Path) -> Path | None:
    e = entry.strip()
    if not e or _SKIP_ENTRY.match(e):
        return None
    tm = re.match(r"^.+\s*<\s*([^>]+?)\s*>$", e)
    if tm:
        e = tm.group(1)
    e = e.replace("\\", "/")
    is_abs = e.startswith("/")
    pure = re.sub(r"\.(md|rst|txt)$", "", e).lstrip("/")
    base = srcdir if is_abs else src_dir
    cand = base / (pure + ".md")
    if cand.exists():
        return cand
    d = base / pure
    if d.is_dir():
        idx = d / INDEX_NAME
        if idx.exists():
            return idx
    return None


def check_broken(index_files: list[Path], srcdir: Path) -> tuple[list[str], dict[Path, set[Path]]]:
    errors: list[str] = []
    edges: dict[Path, set[Path]] = {}
    for idx in index_files:
        src_dir = idx.parent
        targets: set[Path] = set()
        for ent in extract_entries(idx):
            t = resolve_target(src_dir, ent, srcdir)
            if t is None:
                hint = "（目录缺 index.md）" if ent.endswith("/index") else ""
                errors.append(f"断链: {_display(idx)} 的 toctree 引用不存在: 「{ent}」{hint}")
            else:
                targets.add(t)
        edges[idx] = targets
    return errors, edges


def all_md_under(srcdir: Path) -> set[Path]:
    return {
        f
        for f in srcdir.rglob("*")
        if f.is_file()
        and f.suffix == ".md"
        and f.name.lower() != "readme.md"
        and not any(part in EXCLUDE_DIRS for part in f.parts)
    }


def check_reachable(
    srcdir: Path, edges: dict[Path, set[Path]], all_md: set[Path]
) -> list[str]:
    seed = srcdir / INDEX_NAME
    if not seed.exists():
        return [f"缺失根 index.md: {_display(seed)}"]
    reached: set[Path] = set()
    frontier = [seed]
    while frontier:
        f = frontier.pop()
        if f in reached:
            continue
        reached.add(f)
        for t in edges.get(f, ()):
            if t not in reached:
                frontier.append(t)
    unreached = sorted(all_md - reached, key=str)
    return [f"未收录(不可达): {_display(u)}" for u in unreached]


def expected_entries(src_dir: Path) -> set[str]:
    expected: set[str] = set()
    try:
        items = list(src_dir.iterdir())
    except OSError:
        return expected
    for item in items:
        if item.name.startswith(".") or item.name in EXCLUDE_DIRS:
            continue
        if item.is_dir():
            if (item / INDEX_NAME).exists():
                expected.add(f"{item.name}/index")
            else:
                for f in item.glob("*.md"):
                    if f.name.lower() != "readme.md":
                        expected.add(f"{item.name}/{f.stem}")
        elif item.is_file() and item.suffix == ".md":
            if item.name != INDEX_NAME and item.name.lower() != "readme.md":
                expected.add(item.stem)
    return expected


def _to_docname(entry: str) -> str | None:
    e = entry.strip()
    if not e or _SKIP_ENTRY.match(e):
        return None
    tm = re.match(r"^.+\s*<\s*([^>]+?)\s*>$", e)
    if tm:
        e = tm.group(1)
    e = e.replace("\\", "/")
    if e.startswith("/"):
        return None
    return re.sub(r"\.(md|rst|txt)$", "", e)


def check_consistency(index_files: list[Path]) -> list[str]:
    errors: list[str] = []
    for idx in index_files:
        entries = extract_entries(idx)
        if not entries:
            continue
        listed = {
            d
            for e in entries
            if (d := _to_docname(e)) is not None
        }
        for m in sorted(expected_entries(idx.parent) - listed):
            errors.append(f"缺失条目: {_display(idx)} 的 toctree 未收录 {m}")
    return errors


def check_dir_index(srcdir: Path) -> list[str]:
    """含非隐藏子目录的目录必须存在 index.md。"""
    errors: list[str] = []
    for d in srcdir.rglob("*"):
        if not d.is_dir():
            continue
        if any(part in EXCLUDE_DIRS or part.startswith(".") for part in d.relative_to(srcdir).parts):
            continue
        if (d / INDEX_NAME).exists():
            continue
        has_content_subdir = any(
            it.is_dir() and it.name not in EXCLUDE_DIRS and not it.name.startswith(".")
            for it in d.iterdir()
        )
        if has_content_subdir:
            errors.append(f"缺失 index.md: {_display(d)}")
    return errors


def run_scan(srcdir: Path) -> list[str]:
    index_files = iter_index_files([srcdir])
    if not index_files:
        return ["未找到任何 index.md"]
    errors, edges = check_broken(index_files, srcdir)
    errors += check_reachable(srcdir, edges, all_md_under(srcdir))
    errors += check_consistency(index_files)
    errors += check_dir_index(srcdir)
    return errors


def self_test() -> bool:
    ok = True
    tmp = Path(tempfile.mkdtemp("checktoctrees-docs"))
    try:
        a = tmp / "pass"
        (a / "notes").mkdir(parents=True)
        (a / "notes" / "x.md").write_text("# x\n", encoding="utf-8")
        (a / INDEX_NAME).write_text("```{toctree}\n:hidden:\n\nnotes/x\n```\n", encoding="utf-8")

        b = tmp / "broken"
        b.mkdir()
        (b / INDEX_NAME).write_text("```{toctree}\n\nmissing\n```\n", encoding="utf-8")

        c = tmp / "orphan"
        (c / "notes").mkdir(parents=True)
        (c / "notes" / "x.md").write_text("# x\n", encoding="utf-8")
        (c / "notes" / "y.md").write_text("# y\n", encoding="utf-8")
        (c / INDEX_NAME).write_text("```{toctree}\n\nnotes/x\n```\n", encoding="utf-8")

        for name, expect_ok in (("pass", True), ("broken", False), ("orphan", False)):
            errors = run_scan(tmp / name)
            actual_ok = not errors
            if actual_ok == expect_ok:
                state = "放行" if expect_ok else "拦截"
                print(f"自检: {name} → {state} 正确")
            else:
                print(f"自检失败: {name} 期望{'放行' if expect_ok else '拦截'}，实际{'通过' if actual_ok else '拦截'}")
                ok = False
        print("自检通过: check-toctrees.py 既能拦截断链/孤立，也能放行完整 toctree 链。")
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    args = sys.argv[1:]
    if "--self-test" in args:
        return 0 if self_test() else 1

    path_args = [a for a in args if not a.startswith("--")]
    default_mode = not path_args
    targets = list(DEFAULT_SCAN) if default_mode else [Path(a) for a in path_args]

    if default_mode:
        errors = run_scan(ROOT)
    else:
        index_files = iter_index_files(targets)
        if not index_files:
            print("未找到任何 index.md", file=sys.stderr)
            return 1
        errors, _ = check_broken(index_files, ROOT)

    if errors:
        print(f"\n检测到 {len(errors)} 处 toctree 导航问题，CI gate 拦截：")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
