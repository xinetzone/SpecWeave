"""角色权限声明校验（来自 check-role-permissions.py）。"""

import json
import re
import sys
from pathlib import Path

from constants import VALID_TIERS, ROLE_EXCLUDED_FILES as EXCLUDED_FILES
from lib.cli import print_header, print_pass, print_error, print_summary
from lib.frontmatter import (
    parse_frontmatter_unified,
    parse_toml_frontmatter,
    parse_yaml_frontmatter,
    extract_frontmatter_field,
    extract_yaml_field,
)
from lib.project import resolve_project_root

PERMISSIONS_TABLE_RE = re.compile(r'^\[permissions\]\s*\n(.*?)(?=\n\[|\Z)', re.MULTILINE | re.DOTALL)
VIEW_FIELD_RE = re.compile(r'^view\s*=\s*"([^"]+)"\s*$', re.MULTILINE)
MANAGE_FIELD_RE = re.compile(r'^manage\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def _find_role_files(roles_dir: Path) -> list[Path]:
    role_files = []
    for md_path in roles_dir.glob("*.md"):
        if md_path.name in EXCLUDED_FILES:
            continue
        role_files.append(md_path)
    return sorted(role_files)


def _extract_tier(frontmatter_or_fields) -> str:
    if isinstance(frontmatter_or_fields, dict):
        value = frontmatter_or_fields.get("tier")
        return str(value) if value else "standard"
    if isinstance(frontmatter_or_fields, str) and frontmatter_or_fields:
        value = extract_frontmatter_field(frontmatter_or_fields, "tier")
        return value if value else "standard"
    return "standard"


def _get_raw_toml_text(file_path: Path) -> str | None:
    toml_fm = parse_toml_frontmatter(file_path)
    if toml_fm is not None:
        return toml_fm
    yaml_fm = parse_yaml_frontmatter(file_path)
    if yaml_fm is not None:
        x_toml_ref = extract_yaml_field(yaml_fm, "x-toml-ref")
        if x_toml_ref:
            ref_path = (file_path.parent / x_toml_ref.replace('\\', '/')).resolve()
            if ref_path.exists():
                try:
                    return ref_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    return None
    return None


def _extract_permissions(toml_text: str | None) -> tuple[bool, str | None, str | None]:
    if not toml_text:
        return (False, None, None)
    perm_match = PERMISSIONS_TABLE_RE.search(toml_text)
    if not perm_match:
        return (False, None, None)
    perm_block = perm_match.group(1)
    view_match = VIEW_FIELD_RE.search(perm_block)
    manage_match = MANAGE_FIELD_RE.search(perm_block)
    return (
        True,
        view_match.group(1) if view_match else None,
        manage_match.group(1) if manage_match else None,
    )


def _validate_role_file(file_path: Path) -> dict:
    result = {
        "file": file_path.name,
        "tier": "standard",
        "has_permissions": False,
        "view": None,
        "manage": None,
        "valid": True,
        "errors": [],
    }
    fields = parse_frontmatter_unified(file_path)
    if fields is None:
        result["valid"] = False
        result["errors"].append("缺少有效的 frontmatter")
        return result
    tier = _extract_tier(fields)
    result["tier"] = tier
    if tier not in VALID_TIERS:
        result["valid"] = False
        result["errors"].append(f'tier 字段值非法: "{tier}"，仅允许 "co-founder" 或 "standard"')
    toml_text = _get_raw_toml_text(file_path)
    has_perm, view_value, manage_value = _extract_permissions(toml_text)
    result["has_permissions"] = has_perm
    result["view"] = view_value
    result["manage"] = manage_value
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


def run(project_root: Path, args) -> int:
    roles_dir = getattr(args, "path", None)
    if roles_dir:
        roles_dir = Path(roles_dir).resolve()
    else:
        roles_dir = resolve_project_root(__file__) / ".agents" / "roles"
    if not roles_dir.exists():
        print(f"错误: 路径不存在: {roles_dir}", file=sys.stderr)
        return 1

    role_files = _find_role_files(roles_dir)
    results = [_validate_role_file(fp) for fp in role_files]

    total_files = len(results)
    co_founder_count = sum(1 for r in results if r["tier"] == "co-founder")
    error_count = sum(1 for r in results if not r["valid"])
    warning_count = 0

    if getattr(args, "json", False):
        print(json.dumps({
            "summary": {
                "total_files": total_files,
                "co_founder_count": co_founder_count,
                "standard_count": total_files - co_founder_count,
                "errors": error_count,
                "warnings": warning_count,
            },
            "files": results,
        }, ensure_ascii=False, indent=2))
        return 0 if error_count == 0 else 1

    print_header("角色权限声明校验")
    print(f"\n扫描目录: {roles_dir}")
    print(f"角色文件数: {total_files}")

    print("\n1. 校验 frontmatter 有效性...")
    fm_valid = [r for r in results if not any("frontmatter" in e for e in r["errors"])]
    fm_invalid = [r for r in results if any("frontmatter" in e for e in r["errors"])]
    if fm_invalid:
        for r in fm_invalid:
            print_error(f"{r['file']} frontmatter 无效")
        print(f"   失败: {len(fm_invalid)} 个文件")
    else:
        print_pass(f"{len(fm_valid)} 个文件 frontmatter 有效")

    print("\n2. 校验 tier 字段合法性...")
    tier_invalid = [r for r in results if any("tier 字段值非法" in e for e in r["errors"])]
    if tier_invalid:
        for r in tier_invalid:
            print_error(f"{r['file']}: tier = \"{r['tier']}\"")
    else:
        print_pass("所有 tier 字段值合法")

    print("\n3. 校验联合创始角色权限声明完整性...")
    co_founder_results = [r for r in results if r["tier"] == "co-founder"]
    co_founder_invalid = [r for r in co_founder_results if not r["valid"]]
    if co_founder_invalid:
        for r in co_founder_invalid:
            for err in r["errors"]:
                print_error(f"{r['file']}: {err}")
        print("   失败: 以下文件权限声明不完整")
    else:
        print_pass(f"{len(co_founder_results)} 个联合创始角色权限声明完整")

    print()
    if error_count == 0:
        print_summary(total_files, warning_count, error_count)
    else:
        print_summary(0, warning_count, error_count)

    return 0 if error_count == 0 else 1
