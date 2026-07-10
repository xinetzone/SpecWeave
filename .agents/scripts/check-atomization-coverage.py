#!/usr/bin/env python3
"""原子化前置检查：搜索已有模式库，判断新洞察是否被已有模式覆盖。

在创建新模式文件之前运行，对给定的关键词/概念描述在 patterns/ 目录中搜索匹配，
输出三级分类建议（新建模式/已有覆盖/原地保留）。

用法：
  python check-atomization-coverage.py "auto generate manual maintain"
  python check-atomization-coverage.py --concept "跨任务学习曲线 加速效应"
  python check-atomization-coverage.py --all  # 列出所有模式的关键词索引
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_header

# 模式文件目录
PATTERNS_DIR_NAME = "docs/retrospective/patterns"

# 从模式文件中提取关键信息的正则
TITLE_RE = re.compile(r"^# (.+)$", re.MULTILINE)
SECTION_RE = re.compile(r"^## (.+)$", re.MULTILINE)


def build_keyword_index(root_dir: Path) -> dict[str, list[str]]:
    """构建模式关键词倒排索引：关键词 → [模式文件路径, ...]"""
    patterns_dir = root_dir / PATTERNS_DIR_NAME
    if not patterns_dir.exists():
        print_warn(f"模式目录不存在: {patterns_dir}")
        return {}

    index: dict[str, list[str]] = defaultdict(list)
    for md_file in patterns_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        content = md_file.read_text(encoding="utf-8")

        # 提取标题作为主关键词
        title_match = TITLE_RE.search(content)
        if title_match:
            title = title_match.group(1)
            for word in extract_keywords(title):
                index[word.lower()].append(str(md_file.relative_to(root_dir)))

        # 提取各章节标题作为次关键词，关联到该模式
        for section_match in SECTION_RE.finditer(content):
            section = section_match.group(1)
            for word in extract_keywords(section):
                index[word.lower()].append(str(md_file.relative_to(root_dir)))

    return index


def extract_keywords(text: str) -> list[str]:
    """从中文文本中提取关键词（中文字符序列 + 英文单词）。"""
    # 去除标点和特殊字符
    cleaned = re.sub(r"[()（）\[\]【】{}，。、：；！？""''《》\->]", " ", text)
    words = []
    # 提取中文字符序列（2+ 字符）
    for match in re.finditer(r"[\u4e00-\u9fff]{2,}", cleaned):
        words.append(match.group())
    # 提取英文单词（3+ 字符，过滤常见停用词）
    stopwords = {"the", "and", "for", "with", "from"}
    for match in re.finditer(r"[a-zA-Z]{3,}", cleaned):
        word = match.group().lower()
        if word not in stopwords:
            words.append(word)
    return words


def search_patterns(
    keywords: list[str], index: dict[str, list[str]], top_n: int = 5
) -> dict[str, int]:
    """搜索与关键词匹配的模式文件，返回 {文件路径: 匹配分数}。"""
    scores: dict[str, int] = defaultdict(int)
    for keyword in keywords:
        kw_lower = keyword.lower()
        for indexed_kw, files in index.items():
            if kw_lower in indexed_kw or indexed_kw in kw_lower:
                for f in files:
                    scores[f] += 1
            # 部分匹配：关键词包含索引词的前缀或反之
            elif len(kw_lower) >= 3 and len(indexed_kw) >= 3:
                if kw_lower[:3] == indexed_kw[:3]:
                    for f in files:
                        scores[f] += 1

    # 按匹配分数排序，取 top_n
    return dict(sorted(scores.items(), key=lambda x: -x[1])[:top_n])


def classify(
    matches: dict[str, int], min_score: int = 2
) -> tuple[str, list[str] | None]:
    """
    三级分类判断。

    返回: ("new" | "covered" | "keep", 匹配到的模式列表或 None)
    - min_score >= 3 且有匹配 → "covered"（已有覆盖）
    - min_score >= 1 且有匹配 → "covered"（可能有覆盖，需人工判断）
    - 无匹配 → "new"（新建模式）
    """
    if not matches:
        return ("new", None)

    best_score = max(matches.values())
    if best_score >= 3:
        return ("covered", list(matches.keys()))
    elif best_score >= 1:
        return ("covered", list(matches.keys()))
    else:
        return ("new", None)


def list_all_patterns(root_dir: Path, index: dict[str, list[str]]):
    """列出所有模式及其关键词索引。"""
    patterns_dir = root_dir / PATTERNS_DIR_NAME
    all_files: dict[str, list[str]] = defaultdict(list)
    for kw, files in index.items():
        for f in files:
            all_files[f].append(kw)

    print_header("模式关键词索引")
    for file_path in sorted(all_files.keys()):
        pattern = patterns_dir / file_path
        title_match = TITLE_RE.search(pattern.read_text(encoding="utf-8"))
        title = title_match.group(1) if title_match else file_path
        keywords = ", ".join(sorted(set(all_files[file_path])))
        print(f"  [{title}] → {keywords}")


def main():
    parser = argparse.ArgumentParser(description="原子化前置检查：搜索已有模式库覆盖情况")
    parser.add_argument("keywords", nargs="*", help="要搜索的关键词（空格分隔）")
    parser.add_argument(
        "--concept", "-c", help="用完整概念描述搜索（自动提取关键词）"
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="列出所有模式的关键词索引"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=2,
        help="判定'已有覆盖'的最低匹配分数（默认 2）",
    )
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    index = build_keyword_index(root_dir)

    if args.all:
        list_all_patterns(root_dir, index)
        return

    if args.concept:
        search_keywords = extract_keywords(args.concept)
    elif args.keywords:
        search_keywords = list(args.keywords)
    else:
        parser.print_help()
        sys.exit(1)

    if not search_keywords:
        print_warn("未能从输入中提取有效关键词")
        sys.exit(1)

    print_header(f"原子化前置检查: {' '.join(search_keywords)}")
    print(f"  搜索模式库: {sum(len(v) for v in index.values())} 个关键词索引条目")

    matches = search_patterns(search_keywords, index)

    if not matches:
        print_pass("建议：新建模式 — 未找到匹配的已有模式")
        return

    print(f"\n  找到 {len(matches)} 个可能相关的模式:")
    for file_path, score in matches.items():
        pattern_full = root_dir / file_path
        title_match = TITLE_RE.search(pattern_full.read_text(encoding="utf-8"))
        title = title_match.group(1) if title_match else file_path
        print(f"    [{score} 分] {title} ({file_path})")

    classification, covered = classify(matches, args.min_score)
    if classification == "covered":
        print_pass(f"建议：已有模式覆盖 — 引用已有模式即可，无需新建 (匹配分数 ≥ {args.min_score})")
    else:
        print_warn(f"建议：人工判断 — 匹配分数较低，需阅读匹配到的模式后决定")


if __name__ == "__main__":
    main()
