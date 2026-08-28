#!/usr/bin/env python3
"""自动修复 docs/ 目录下所有 index.md 的 toctree。

策略：
1. 为每个目录计算应列入 toctree 的条目（子目录 index + 直接 .md 文件 + log.md）
2. 已存在的 toctree 保留选项（:maxdepth:/:caption:/:hidden:），替换条目列表
3. 无 toctree 的 index.md 在文件末尾追加
4. 缺失的 index.md 自动创建
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {"_build", "_static", "_templates", ".git", "__pycache__"}
INDEX_NAME = "index.md"

_FENCE_OPEN = re.compile(
    r"^(?P<fence>`{3,}|:{3,})\s*\{toctree\}(?:\s*\{[^}]*\})?\s*$",
    re.MULTILINE,
)
_FENCE_CLOSE = re.compile(r"^(?:`{3,}|:{3,})\s*$", re.MULTILINE)
_OPTION = re.compile(r"^\s*:")


def should_skip(name: str) -> bool:
    return name.startswith(".") or name in EXCLUDE_DIRS


def compute_entries(directory: Path) -> list[str]:
    """计算目录应列入 toctree 的条目（docname 形式）。"""
    entries: list[str] = []
    try:
        items = sorted(directory.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return entries

    # 子目录
    for item in items:
        if item.is_dir() and not should_skip(item.name):
            if (item / INDEX_NAME).exists():
                entries.append(f"{item.name}/index")
            else:
                # 子目录无 index.md，列出其直接 .md 文件
                for f in sorted(item.glob("*.md")):
                    if f.name.lower() != "readme.md":
                        entries.append(f"{item.name}/{f.stem}")

    # 直接 .md 文件
    for item in items:
        if item.is_file() and item.suffix == ".md":
            if item.name == INDEX_NAME or item.name.lower() == "readme.md":
                continue
            entries.append(item.stem)

    return entries


def extract_toctree_options(text: str) -> list[str]:
    """提取现有 toctree 的选项行。"""
    lines = text.splitlines()
    options: list[str] = []
    i = 0
    while i < len(lines):
        if _FENCE_OPEN.match(lines[i]):
            i += 1
            while i < len(lines) and not _FENCE_CLOSE.match(lines[i]):
                body = lines[i].strip()
                if body and _OPTION.match(body):
                    options.append(body)
                i += 1
            return options
        i += 1
    return options


def replace_or_append_toctree(text: str, entries: list[str], title: str = "") -> str:
    """替换现有 toctree 内容或追加新 toctree。"""
    options = extract_toctree_options(text)
    if not options:
        options = [":maxdepth: 2"]

    toctree_block = "```{toctree}\n"
    for opt in options:
        toctree_block += f"{opt}\n"
    toctree_block += "\n"
    for e in entries:
        toctree_block += f"{e}\n"
    toctree_block += "```\n"

    # 尝试替换现有 toctree
    lines = text.splitlines()
    new_lines: list[str] = []
    i = 0
    replaced = False
    while i < len(lines):
        if _FENCE_OPEN.match(lines[i]):
            # 找到 toctree 开始，跳过整个块
            new_lines.append(toctree_block.rstrip("\n"))
            i += 1
            while i < len(lines) and not _FENCE_CLOSE.match(lines[i]):
                i += 1
            i += 1  # 跳过闭围栏
            replaced = True
        else:
            new_lines.append(lines[i])
            i += 1

    result = "\n".join(new_lines)
    if not replaced:
        # 追加到文件末尾
        if result and not result.endswith("\n"):
            result += "\n"
        result += "\n" + toctree_block

    return result


def ensure_index_for_dir(directory: Path, is_root: bool = False) -> None:
    """确保目录有 index.md，且 toctree 完整。"""
    idx = directory / INDEX_NAME
    entries = compute_entries(directory)

    if not idx.exists():
        # 创建新 index.md
        rel = directory.relative_to(ROOT)
        title = f"# {rel.name.replace('-', ' ').title()}\n"
        if is_root:
            title = "# SpecWeave 文档中心\n"
        content = title + "\n"
        if entries:
            content += "```{toctree}\n:maxdepth: 2\n:hidden:\n\n"
            for e in entries:
                content += f"{e}\n"
            content += "```\n"
        idx.write_text(content, encoding="utf-8")
        print(f"  CREATED {idx.relative_to(ROOT)}")
        return

    text = idx.read_text(encoding="utf-8")
    new_text = replace_or_append_toctree(text, entries)
    if new_text != text:
        idx.write_text(new_text, encoding="utf-8")
        print(f"  UPDATED {idx.relative_to(ROOT)}")
    else:
        print(f"  OK      {idx.relative_to(ROOT)}")


def find_content_dirs() -> list[Path]:
    """找到所有含 .md 文件或含子目录的目录。"""
    dirs: list[Path] = []
    for d in sorted(ROOT.rglob("*")):
        if not d.is_dir():
            continue
        if any(part in EXCLUDE_DIRS or part.startswith(".") for part in d.relative_to(ROOT).parts):
            continue
        # 检查是否有 .md 文件或非空的子目录
        has_content = False
        try:
            for item in d.iterdir():
                if should_skip(item.name):
                    continue
                if item.is_file() and item.suffix == ".md":
                    has_content = True
                    break
                if item.is_dir() and not should_skip(item.name):
                    # 检查子目录是否有内容
                    try:
                        for sub in item.rglob("*"):
                            if sub.is_file() and sub.suffix == ".md":
                                has_content = True
                                break
                    except OSError:
                        pass
                    if has_content:
                        break
        except OSError:
            pass
        if has_content:
            dirs.append(d)
    return dirs


def main():
    print("Fixing toctrees...\n")

    # 先处理根目录
    ensure_index_for_dir(ROOT, is_root=True)

    # 处理所有含内容的目录
    for d in find_content_dirs():
        if d == ROOT:
            continue
        ensure_index_for_dir(d)

    print("\nDone.")


if __name__ == "__main__":
    main()
