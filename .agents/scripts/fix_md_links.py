#!/usr/bin/env python3
"""
批量修复 Markdown 文件中缺少 .md 后缀的内部链接。
处理 /concepts/、/examples/、/references/ 开头的链接，保留锚点，
跳过代码块，不修改已有 .md 后缀和外部链接。
"""

import re
import os
import sys
from pathlib import Path

TARGET_BUNDLES = [
    "home-assistant",
    "apache-tvm",
    "ai-agent-skills",
    "tuya-iot",
    "okf-ecosystem",
    "mobile-use",
    "veadk-python",
    "english-grammar",
    "laozi-lineage",
]

BUNDLES_BASE = Path(r"d:\spaces\SpecWeave\bundles\chaos")


def fix_links_in_content(content: str) -> tuple[str, int]:
    """修复内容中的链接，返回修复后的内容和修改次数"""
    lines = content.split("\n")
    modified_count = 0
    in_code_block = False
    in_frontmatter = False
    frontmatter_ended = False
    result_lines = []

    link_pattern = re.compile(
        r"(\]\()(/(?:concepts|examples|references)/)([^)#?]+)(#[^)]*)?(\))"
    )
    resource_pattern = re.compile(
        r'(resource:\s*")(/(?:concepts|examples|references)/)([^"#?]+)(#[^"]*)?(")'
    )

    for line in lines:
        original_line = line

        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue

        if not frontmatter_ended and line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_frontmatter = False
                frontmatter_ended = True
            result_lines.append(line)
            continue

        if in_code_block:
            result_lines.append(line)
            continue

        def replace_link(match):
            nonlocal modified_count
            prefix = match.group(1)
            base = match.group(2)
            path = match.group(3)
            anchor = match.group(4) or ""
            suffix = match.group(5)

            if path.endswith(".md"):
                return match.group(0)

            modified_count += 1
            return f"{prefix}{base}{path}.md{anchor}{suffix}"

        def replace_resource(match):
            nonlocal modified_count
            prefix = match.group(1)
            base = match.group(2)
            path = match.group(3)
            anchor = match.group(4) or ""
            suffix = match.group(5)

            if path.endswith(".md"):
                return match.group(0)

            modified_count += 1
            return f"{prefix}{base}{path}.md{anchor}{suffix}"

        line = link_pattern.sub(replace_link, line)
        line = resource_pattern.sub(replace_resource, line)

        result_lines.append(line)

    return "\n".join(result_lines), modified_count


def process_file(file_path: Path) -> int:
    """处理单个文件，返回修改次数"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        fixed_content, count = fix_links_in_content(content)

        if count > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            print(f"  修复 {count} 处链接: {file_path}")

        return count
    except Exception as e:
        print(f"  处理失败 {file_path}: {e}", file=sys.stderr)
        return 0


def process_bundle(bundle_name: str) -> int:
    """处理单个 bundle，返回总修改次数"""
    bundle_path = BUNDLES_BASE / bundle_name
    if not bundle_path.exists():
        print(f"警告: bundle 不存在 {bundle_path}")
        return 0

    total = 0
    md_files = list(bundle_path.rglob("*.md"))
    print(f"\n处理 {bundle_name} ({len(md_files)} 个 Markdown 文件)...")

    for md_file in md_files:
        total += process_file(md_file)

    return total


def main():
    total_modified = 0
    for bundle in TARGET_BUNDLES:
        total_modified += process_bundle(bundle)

    print(f"\n完成! 总共修复 {total_modified} 处链接。")


if __name__ == "__main__":
    main()
