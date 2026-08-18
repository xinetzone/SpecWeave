#!/usr/bin/env python3
"""CATEGORIES.md 自动重建工具。

从 methodology-patterns 目录扫描实际 `.md` 文件，重建
`methodology-patterns/CATEGORIES.md` 的主题分类索引：
- 汇总表「模式数量」= 各主题目录实际模式文件数（排除 README.md 与子目录）
- 每个主题「模式文件清单」= 该目录下全量模式文档（文件名 + 说明 + 成熟度）
- 保留现有 CATEGORIES.md 中人工撰写的「核心关注点」「边界说明」「核心关注点简述」

用法：
  python .agents/scripts/generate-categories.py --path <项目根> [--dry-run]
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import logging
import re
from datetime import date
from pathlib import Path

# 抑制 x-toml-ref 外部 TOML 缺失的无害警告（不影响 title/maturity 提取）
logging.getLogger().setLevel(logging.ERROR)

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in _sys.path:
    _sys.path.insert(0, str(SCRIPTS_DIR))

from lib.frontmatter import parse_frontmatter_unified
from lib.markdown import extract_title
from lib.project import resolve_project_root
from lib.cli import setup_safe_output, print_pass, print_warn

# 8 个主题目录，顺序与现有 CATEGORIES.md 一致
THEME_DIRS = [
    "retrospective-knowledge",
    "research-knowledge",
    "document-architecture",
    "tools-automation",
    "governance-strategy",
    "ai-collaboration",
    "creative-design",
    "product-growth",
]


def get_categories_path(root: Path) -> Path:
    return (
        root
        / ".agents"
        / "docs"
        / "retrospective"
        / "patterns"
        / "methodology-patterns"
        / "CATEGORIES.md"
    )


def get_title(meta, md_path: Path) -> str:
    if meta:
        t = meta.get("title")
        if t and str(t).strip():
            return str(t).strip()
    t = extract_title(md_path)
    if t:
        return t
    return md_path.stem.replace("-", " ").replace("_", " ")


def get_maturity(meta) -> str:
    if meta:
        m = meta.get("maturity")
        if m and str(m).strip():
            return str(m).strip()
    return "-"


def scan_theme(theme_dir: Path) -> list[tuple[str, str, str]]:
    """扫描主题目录，返回 (filename, title, maturity) 列表（按文件名排序）。"""
    entries = []
    if not theme_dir.exists():
        return entries
    for item in sorted(theme_dir.iterdir()):
        if item.name.startswith("."):
            continue
        if item.name == "README.md":
            continue
        if item.is_file() and item.suffix.lower() == ".md":
            meta = parse_frontmatter_unified(item)
            title = get_title(meta, item)
            maturity = get_maturity(meta)
            entries.append((item.name, title, maturity))
    return entries


def parse_existing(categories_path: Path):
    """解析现有 CATEGORIES.md，返回 (themes, existing_summaries)。

    themes: {dir: {"anchor": str, "name": str, "brief": str, "focus": str, "boundary": str}}
    existing_summaries: {dir: {filename: summary}}
    """
    themes = {}
    existing = {}
    if not categories_path.exists():
        return themes, existing

    content = categories_path.read_text(encoding="utf-8")

    # 1. 汇总表：提取 anchor / name / brief
    for m in re.finditer(
        r"^\|\s*\[([a-z-]+)\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*\d+\s*\|\s*([^|]+?)\s*\|",
        content,
        re.MULTILINE,
    ):
        d = m.group(1)
        themes.setdefault(d, {
            "anchor": m.group(2).strip(),
            "name": m.group(3).strip(),
            "brief": m.group(4).strip(),
            "focus": "",
            "boundary": "",
        })

    # 2. 每个主题章节：提取 focus / boundary
    for d in themes:
        m = re.search(
            r"## "
            + re.escape(d)
            + r"\s*—\s*[^\n]*\n\n\*\*核心关注点\*\*：([^\n]+)\n\n\*\*边界说明\*\*：([^\n]+)",
            content,
        )
        if m:
            themes[d]["focus"] = m.group(1).strip()
            themes[d]["boundary"] = m.group(2).strip()

    # 3. 每个主题章节：提取现有说明映射 {filename: summary}
    for d in themes:
        existing[d] = {}
        sec_start = content.find("## " + d + " —")
        if sec_start == -1:
            continue
        next_sec = content.find("\n---\n", sec_start)
        section = content[sec_start:] if next_sec == -1 else content[sec_start:next_sec]
        for line in section.split("\n"):
            m = re.match(
                r"^\|\s*\[([^\]]+)\]\([^)]*\)\s*\|\s*([^|]+?)\s*\|", line.strip()
            )
            if m:
                existing[d][m.group(1).strip()] = m.group(2).strip()

    return themes, existing


def build_categories(themes, existing, patterns_root: Path) -> str:
    lines: list[str] = []
    lines.append("# 方法论模式主题分类说明")
    lines.append("")
    lines.append(
        "基于模式的核心主题思想进行分类，而非成熟度等级或来源。共划分为8个主题类别，便于按场景快速定位相关模式。"
    )
    lines.append("")
    today = date.today().isoformat()
    lines.append(
        f"> **数据来源**：以下计数基于各目录实际 `.md` 文件数（排除README.md与子目录），由 `generate-categories.py` 自动重建，最后更新：{today}。"
    )
    lines.append("")
    lines.append("## 分类索引")
    lines.append("")
    lines.append("| 主题目录 | 中文名称 | 模式数量 | 核心关注点 |")
    lines.append("|---------|---------|---------|-----------|")

    counts = {}
    for d in THEME_DIRS:
        entries = scan_theme(patterns_root / d)
        counts[d] = len(entries)
        meta = themes.get(d, {
            "anchor": f"#{d}",
            "name": d,
            "brief": "",
            "focus": "",
            "boundary": "",
        })
        lines.append(
            f"| [{d}]({meta['anchor']}) | {meta['name']} | {counts[d]} | {meta['brief']} |"
        )

    lines.append("")

    for d in THEME_DIRS:
        meta = themes.get(d, {"anchor": f"#{d}", "name": d, "focus": "", "boundary": ""})
        entries = scan_theme(patterns_root / d)
        lines.append("---")
        lines.append("")
        lines.append(f"## {d} — {meta['name']}")
        lines.append("")
        lines.append(f"**核心关注点**：{meta['focus']}")
        lines.append("")
        lines.append(f"**边界说明**：{meta['boundary']}")
        lines.append("")
        lines.append("| 模式文件 | 一句话说明 | 成熟度 |")
        lines.append("|---------|-----------|-------|")
        for filename, title, maturity in entries:
            summary = existing.get(d, {}).get(filename) or title
            lines.append(f"| [{filename}]({d}/{filename}) | {summary} | {maturity} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(description="重建 methodology-patterns/CATEGORIES.md")
    parser.add_argument("--path", type=Path, default=None, help="项目根目录（默认自动解析）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    args = parser.parse_args()

    root = args.path or resolve_project_root(__file__)
    categories_path = get_categories_path(root)
    patterns_root = categories_path.parent

    if not categories_path.exists():
        print_warn(f"未找到 CATEGORIES.md：{categories_path}")
        return 1

    themes, existing = parse_existing(categories_path)
    new_content = build_categories(themes, existing, patterns_root)

    # 打印各主题计数摘要
    counts = {}
    for d in THEME_DIRS:
        counts[d] = len(scan_theme(patterns_root / d))
    total = sum(counts.values())
    print(f"8 个主题目录，共 {total} 个模式文件：")
    for d in THEME_DIRS:
        print(f"  {d}: {counts[d]}")

    # 解析健康检查：确认人工撰写的 focus/boundary/brief 已正确保留
    print("\n解析健康检查（name/brief/focus/boundary 应全部非空）：")
    for d in THEME_DIRS:
        meta = themes.get(d, {})
        ok = all(meta.get(k) for k in ("name", "brief", "focus", "boundary"))
        flag = "OK  " if ok else "MISS"
        print(
            f"  [{flag}] {d}: name={bool(meta.get('name'))} brief={bool(meta.get('brief'))} "
            f"focus={bool(meta.get('focus'))} boundary={bool(meta.get('boundary'))} "
            f"现有说明保留={len(existing.get(d, {}))}"
        )

    if args.dry_run:
        print("\n（dry-run）未写入文件。")
        return 0

    categories_path.write_text(new_content, encoding="utf-8")
    print_pass(f"已重建 {categories_path.name}（{total} 个模式）")
    return 0


if __name__ == "__main__":
    _sys.exit(main())