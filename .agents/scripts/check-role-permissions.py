#!/usr/bin/env python3
"""扫描 .agents/roles/ 目录下的角色定义文件，校验 TOML frontmatter 中的权限声明完整性。

校验规则：
  1. 所有角色文件必须有有效的 TOML frontmatter（+++ ... +++）
  2. tier 字段为可选，未声明时默认为 "standard"
  3. 当 tier = "co-founder" 时，[permissions] 表必须存在，且必须包含 view 和 manage 字段
  4. tier 字段值只能是 "co-founder" 或 "standard"，其他值报错
  5. [permissions] 表中的 view 和 manage 字段值不能为空
"""

import argparse
import re
import sys
import json
from pathlib import Path

from constants import VALID_TIERS, ROLE_EXCLUDED_FILES as EXCLUDED_FILES
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field
from lib.project import resolve_project_root
from lib.cli import print_header, print_pass, print_warn, print_error, print_summary, add_common_args

# 匹配 [permissions] 表（支持表后跟随其他表或位于 frontmatter 末尾两种情况）
PERMISSIONS_TABLE_RE = re.compile(r'^\[permissions\]\s*\n(.*?)(?=\n\[|\Z)', re.MULTILINE | re.DOTALL)
# 匹配 view 字段: view = "..."
VIEW_FIELD_RE = re.compile(r'^view\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
# 匹配 manage 字段: manage = "..."
MANAGE_FIELD_RE = re.compile(r'^manage\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def find_role_files(roles_dir: Path) -> list[Path]:
    """查找角色目录下的所有 .md 角色文件（排除 README.md 等非角色文件）。"""
    role_files = []
    for md_path in roles_dir.glob("*.md"):
        if md_path.name in EXCLUDED_FILES:
            continue
        role_files.append(md_path)
    return sorted(role_files)


def extract_tier(frontmatter: str) -> str:
    """从 frontmatter 中提取 tier 字段值，未声明时默认为 "standard"。

    复用 lib.frontmatter.extract_frontmatter_field。
    """
    value = extract_frontmatter_field(frontmatter, "tier")
    return value if value else "standard"


def extract_permissions(frontmatter: str) -> tuple[bool, str | None, str | None]:
    """从 frontmatter 中提取 [permissions] 表的 view 与 manage 字段。

    返回: (has_permissions_table, view_value, manage_value)
    """
    perm_match = PERMISSIONS_TABLE_RE.search(frontmatter)
    if not perm_match:
        return (False, None, None)

    perm_block = perm_match.group(1)
    view_match = VIEW_FIELD_RE.search(perm_block)
    manage_match = MANAGE_FIELD_RE.search(perm_block)

    view_value = view_match.group(1) if view_match else None
    manage_value = manage_match.group(1) if manage_match else None

    return (True, view_value, manage_value)


def validate_role_file(file_path: Path) -> dict:
    """校验单个角色文件的权限声明完整性。

    返回包含校验结果与字段详情的字典。
    """
    result = {
        "file": file_path.name,
        "tier": "standard",
        "has_permissions": False,
        "view": None,
        "manage": None,
        "valid": True,
        "errors": [],
    }

    frontmatter = parse_toml_frontmatter(file_path)
    if frontmatter is None:
        result["valid"] = False
        result["errors"].append("缺少有效的 TOML frontmatter（+++ ... +++）")
        return result

    tier = extract_tier(frontmatter)
    result["tier"] = tier

    # 校验 tier 字段值合法性
    if tier not in VALID_TIERS:
        result["valid"] = False
        result["errors"].append(f'tier 字段值非法: "{tier}"，仅允许 "co-founder" 或 "standard"')

    has_perm, view_value, manage_value = extract_permissions(frontmatter)
    result["has_permissions"] = has_perm
    result["view"] = view_value
    result["manage"] = manage_value

    # 当 tier = "co-founder" 时，校验 [permissions] 表完整性
    if tier == "co-founder":
        if not has_perm:
            result["valid"] = False
            result["errors"].append("缺少 [permissions] 表")
        else:
            if view_value is None:
                result["valid"] = False
                result["errors"].append("[permissions] 表缺少 view 字段")
            if manage_value is None:
                result["valid"] = False
                result["errors"].append("[permissions] 表缺少 manage 字段")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描 .agents/roles/ 角色文件，校验 TOML frontmatter 中的权限声明完整性。"
    )
    add_common_args(parser)
    args = parser.parse_args()

    roles_dir = args.path or (resolve_project_root(__file__) / ".agents" / "roles")
    if not roles_dir.exists():
        print(f"错误: 路径不存在: {roles_dir}", file=sys.stderr)
        return 1

    role_files = find_role_files(roles_dir)
    results = [validate_role_file(fp) for fp in role_files]

    total_files = len(results)
    co_founder_count = sum(1 for r in results if r["tier"] == "co-founder")
    standard_count = sum(1 for r in results if r["tier"] == "standard")
    error_count = sum(1 for r in results if not r["valid"])
    warning_count = 0

    if args.json:
        print(json.dumps({
            "summary": {
                "total_files": total_files,
                "co_founder_count": co_founder_count,
                "standard_count": standard_count,
                "errors": error_count,
                "warnings": warning_count,
            },
            "files": results,
        }, ensure_ascii=False, indent=2))
        return 0 if error_count == 0 else 1

    # 文本模式输出
    print_header("角色权限声明校验")
    print(f"\n扫描目录: {roles_dir}")
    print(f"角色文件数: {total_files}")

    # 步骤 1: 校验 frontmatter 有效性
    print("\n1. 校验 frontmatter 有效性...")
    fm_valid = [r for r in results if not any("frontmatter" in e for e in r["errors"])]
    fm_invalid = [r for r in results if any("frontmatter" in e for e in r["errors"])]
    if fm_invalid:
        for r in fm_invalid:
            print_error(f"{r['file']} frontmatter 无效")
        print(f"   失败: {len(fm_invalid)} 个文件")
    else:
        print_pass(f"{len(fm_valid)} 个文件 frontmatter 有效")

    # 步骤 2: 校验 tier 字段合法性
    print("\n2. 校验 tier 字段合法性...")
    tier_invalid = [r for r in results if any("tier 字段值非法" in e for e in r["errors"])]
    if tier_invalid:
        for r in tier_invalid:
            print_error(f"{r['file']}: tier = \"{r['tier']}\"")
    else:
        print_pass("所有 tier 字段值合法")

    # 步骤 3: 校验联合创始角色权限声明完整性
    print("\n3. 校验联合创始角色权限声明完整性...")
    co_founder_results = [r for r in results if r["tier"] == "co-founder"]
    co_founder_invalid = [r for r in co_founder_results if not r["valid"]]
    if co_founder_invalid:
        for r in co_founder_invalid:
            for err in r["errors"]:
                print_error(f"{r['file']}: {err}")
        print(f"   失败: 以下文件权限声明不完整")
    else:
        print_pass(f"{len(co_founder_results)} 个联合创始角色权限声明完整")

    # 总结
    print()
    if error_count == 0:
        print_summary(total_files, warning_count, error_count)
    else:
        print_summary(0, warning_count, error_count)

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
