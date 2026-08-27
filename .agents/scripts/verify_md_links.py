#!/usr/bin/env python3
"""
验证脚本：检查是否还有不带 .md 后缀的 /concepts/、/examples/、/references/ 链接
正确跳过代码块
"""

import re
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


def check_file(file_path: Path) -> list:
    """检查单个文件，返回问题行列表"""
    issues = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        in_code_block = False
        link_pattern = re.compile(
            r"\]\(/(?:concepts|examples|references)/([^)#?]+)(#[^)]*)?\)"
        )
        resource_pattern = re.compile(
            r'resource:\s*"/(?:concepts|examples|references)/([^"#?]+)(#[^"]*)?"'
        )

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            for match in link_pattern.finditer(line):
                path = match.group(1)
                if not path.endswith(".md") and not path.endswith("/"):
                    issues.append((line_num, line.rstrip(), f"链接缺少 .md: {match.group(0)}"))

            for match in resource_pattern.finditer(line):
                path = match.group(1)
                if not path.endswith(".md") and not path.endswith("/"):
                    issues.append((line_num, line.rstrip(), f"resource 缺少 .md: {match.group(0)}"))

    except Exception as e:
        print(f"读取失败 {file_path}: {e}", file=sys.stderr)

    return issues


def main():
    total_issues = 0
    for bundle in TARGET_BUNDLES:
        bundle_path = BUNDLES_BASE / bundle
        if not bundle_path.exists():
            print(f"警告: bundle 不存在 {bundle_path}")
            continue

        bundle_issues = 0
        for md_file in bundle_path.rglob("*.md"):
            issues = check_file(md_file)
            if issues:
                print(f"\n{bundle} / {md_file.relative_to(bundle_path)}:")
                for line_num, line, desc in issues:
                    print(f"  L{line_num}: {desc}")
                    print(f"    {line[:100]}")
                bundle_issues += len(issues)

        total_issues += bundle_issues
        if bundle_issues == 0:
            print(f"✓ {bundle}: 无问题")

    print(f"\n验证完成，共发现 {total_issues} 个问题。")
    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
