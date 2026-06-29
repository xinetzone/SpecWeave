#!/usr/bin/env python3
"""仓库合规检查统一工具。

合并 check-gitignore、check-vendor、check-mermaid、check-filename-convention、check-role-permissions
五个检查脚本为一个统一工具，提供子命令入口。

子命令:
  gitignore   Git 忽略规则检查
  vendor      vendor 目录合规性检查
  mermaid     Mermaid 语法安全检查
  filename    文件名命名规范检查
  roles       角色权限声明校验
  all         按 CI 顺序执行所有检查

用法示例:
  python repo-check.py all                    # 运行所有检查
  python repo-check.py gitignore              # 仅检查 .gitignore
  python repo-check.py vendor --fix           # 修复 vendor 目录缺失文件
  python repo-check.py mermaid --fix          # 自动修复 Mermaid 语法问题
  python repo-check.py filename --staged      # 仅检查暂存区文件名
  python repo-check.py roles --json           # JSON 格式输出角色权限
"""

import argparse
import sys
from pathlib import Path

from lib.project import resolve_project_root
from lib.cli import setup_safe_output
from lib.checks import gitignore as check_gitignore
from lib.checks import vendor as check_vendor
from lib.checks import mermaid as check_mermaid
from lib.checks import filename as check_filename
from lib.checks import roles as check_roles


CHECKS_CI_ORDER = [
    ("gitignore", "Git 忽略规则", check_gitignore),
    ("vendor", "vendor 目录合规", check_vendor),
    ("mermaid", "Mermaid 语法", check_mermaid),
    ("filename", "文件名规范", check_filename),
    ("roles", "角色权限声明", check_roles),
]


def _add_path_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--path", type=str, default=None, help="指定检查路径（默认项目根目录）")


def _add_json_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="仓库合规检查统一工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="运行 'repo-check.py <子命令> --help' 查看各子命令详细参数",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用子命令")

    # --- gitignore ---
    p_gi = subparsers.add_parser("gitignore", help="Git 忽略规则检查")
    _add_path_arg(p_gi)

    # --- vendor ---
    p_v = subparsers.add_parser("vendor", help="vendor 目录合规性检查")
    _add_path_arg(p_v)
    p_v.add_argument("--fix", action="store_true", help="自动创建缺失的标准模板文件")
    p_v.add_argument("--scan-refs", action="store_true", help="扫描代码中对 vendor 目录的引用")
    p_v.add_argument("--deep", action="store_true", help="执行 submodule 深度集成验证（初始化、清洁度、元数据、非法引用、测试隔离）")

    # --- mermaid ---
    p_m = subparsers.add_parser("mermaid", help="Mermaid 语法安全检查")
    _add_path_arg(p_m)
    p_m.add_argument("--exclude", nargs="*", default=[], help="排除的目录路径（相对于项目根）")
    p_m.add_argument("--fix", action="store_true", help="自动修复可修复问题")
    p_m.add_argument("--dry-run", action="store_true", help="预览修复效果但不写入文件")
    p_m.add_argument("--debug", action="store_true", help="输出详细调试日志（用于排查边界情况）")
    _add_json_arg(p_m)

    # --- filename ---
    p_fn = subparsers.add_parser("filename", help="文件名命名规范检查")
    p_fn.add_argument("--directory", type=str, default=None, help="指定检查目录（默认项目根目录）")
    p_fn.add_argument("--fix", action="store_true", help="自动修复（保留接口，当前需手动修复中文文件名）")
    p_fn.add_argument("--staged", action="store_true", help="仅检查 git 暂存区文件")

    # --- roles ---
    p_r = subparsers.add_parser("roles", help="角色权限声明校验")
    _add_path_arg(p_r)
    _add_json_arg(p_r)

    # --- all ---
    p_all = subparsers.add_parser("all", help="按 CI 顺序执行所有检查")
    p_all.add_argument("--path", type=str, default=None, help="指定项目根目录路径")

    return parser


def run_all(project_root: Path, args) -> int:
    overall = 0
    for cmd_name, label, module in CHECKS_CI_ORDER:
        print(f"\n{'=' * 60}")
        print(f"  [{cmd_name}] {label}")
        print(f"{'=' * 60}")
        sub_args = argparse.Namespace()
        sub_args.path = getattr(args, "path", None)
        sub_args.fix = False
        sub_args.dry_run = False
        sub_args.scan_refs = False
        sub_args.exclude = []
        sub_args.directory = None
        sub_args.staged = False
        sub_args.json = False
        sub_args.deep = False
        ret = module.run(project_root, sub_args)
        if ret != 0:
            overall = 1
    print(f"\n{'=' * 60}")
    if overall == 0:
        print("[PASS] 所有检查通过！")
    else:
        print("[FAIL] 部分检查未通过，请查看上方详细信息。")
    print("=" * 60)
    return overall


def main() -> int:
    setup_safe_output()
    parser = build_parser()
    args = parser.parse_args()

    project_root = resolve_project_root(__file__)
    if getattr(args, "path", None):
        project_root = Path(args.path).resolve()

    if args.command is None or args.command == "all":
        return run_all(project_root, args)

    dispatch = {
        "gitignore": check_gitignore,
        "vendor": check_vendor,
        "mermaid": check_mermaid,
        "filename": check_filename,
        "roles": check_roles,
    }
    module = dispatch.get(args.command)
    if module is None:
        parser.print_help()
        return 1
    return module.run(project_root, args)


if __name__ == "__main__":
    sys.exit(main())
