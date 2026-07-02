#!/usr/bin/env python3
"""docgov - 文档元数据治理统一 CLI 工具。

将 6 个元数据治理脚本整合为统一的命令行入口，提供：
- 子命令分发（check/fix/add-id/add-title/audit/links）
- doctor 一键全量治理
- 所有子命令透传原始参数

用法:
    python .agents/scripts/docgov.py <command> [options]
    python .agents/scripts/docgov.py doctor --dir docs/
"""

import argparse
import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

SUBCOMMANDS = {
    'check': {
        'module': 'check_frontmatter',
        'script': 'check-frontmatter.py',
        'help': 'Frontmatter 完整性校验（必填字段、x-toml-ref路径、禁止字段等）',
    },
    'fix': {
        'module': 'fix_x_toml_ref',
        'script': 'fix-x-toml-ref.py',
        'help': '修复 x-toml-ref 相对路径错误，自动创建缺失的 TOML 元数据文件',
    },
    'add-id': {
        'module': 'add_frontmatter_id',
        'script': 'add-frontmatter-id.py',
        'help': '批量为缺失 id 字段的 Markdown 文件添加 kebab-case 格式 id',
    },
    'add-title': {
        'module': 'add_frontmatter_title',
        'script': 'add-frontmatter-title.py',
        'help': '批量为缺失 title 字段的 Markdown 文件从 H1 标题提取 title',
    },
    'audit': {
        'module': 'audit_metadata_ecosystem',
        'script': 'audit-metadata-ecosystem.py',
        'help': '元数据生态健康度双向审计（孤儿 TOML、缺失 TOML、镜像一致性、id 匹配等）',
    },
    'links': {
        'module': 'check_links',
        'script': 'check-links.py',
        'help': 'Markdown 链接有效性检查（本地文件引用 + 可选外部 URL）',
    },
}


def _load_module(cmd_name: str):
    """动态加载子命令对应的脚本模块。"""
    info = SUBCOMMANDS[cmd_name]
    script_path = SCRIPT_DIR / info['script']
    spec = importlib.util.spec_from_file_location(info['module'], script_path)
    if spec is None or spec.loader is None:
        print(f'错误: 无法加载模块 {info["script"]}', file=sys.stderr)
        sys.exit(1)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[info['module']] = mod
    spec.loader.exec_module(mod)
    return mod


def _run_command(cmd_name: str, argv: list[str]) -> None:
    """执行子命令，透传参数。"""
    mod = _load_module(cmd_name)
    if not hasattr(mod, 'main'):
        print(f'错误: 模块 {cmd_name} 没有 main() 函数', file=sys.stderr)
        sys.exit(1)
    mod.main(argv)


def cmd_doctor(args) -> None:
    """一键全量治理：按安全顺序执行全套检查与修复。

    执行顺序:
    1. add-title  -- 补全缺失 title（dry-run 模式预览，需确认后写入）
    2. add-id     -- 补全缺失 id
    3. fix        -- 修复 x-toml-ref 路径 + 创建缺失 TOML
    4. audit --fix -- 双向审计 + 自动修复
    5. audit      -- 最终审计确认 0 错误
    6. check      -- frontmatter 校验
    7. links      -- 链接检查（仅本地）
    """
    target_dir = args.dir
    dry_run = args.dry_run

    print('=' * 60)
    print('docgov doctor - 文档元数据一键治理')
    print(f'目标目录: {target_dir}')
    print(f'模式: {"预览（不写入）" if dry_run else "执行（写入变更）"}')
    print('=' * 60)

    steps = [
        {
            'name': 'Step 1/7: 补全 title 字段',
            'cmd': 'add-title',
            'argv': ['--dir', target_dir] + (['--dry-run'] if dry_run else ['--write']),
        },
        {
            'name': 'Step 2/7: 补全 id 字段',
            'cmd': 'add-id',
            'argv': ['--dir', target_dir] + ([] if dry_run else ['--write']),
        },
        {
            'name': 'Step 3/7: 修复 x-toml-ref + 创建 TOML',
            'cmd': 'fix',
            'argv': ['--dir', target_dir] + (
                ['--dry-run'] if dry_run else ['--write', '--create-toml']
            ),
        },
        {
            'name': 'Step 4/7: 元数据生态审计 + 自动修复',
            'cmd': 'audit',
            'argv': ['--dir', target_dir] + ([] if dry_run else ['--fix']),
        },
        {
            'name': 'Step 5/7: 最终审计验证',
            'cmd': 'audit',
            'argv': ['--dir', target_dir],
            'continue_on_error': True,
        },
        {
            'name': 'Step 6/7: Frontmatter 校验',
            'cmd': 'check',
            'argv': ['--dir', target_dir],
            'continue_on_error': True,
        },
    ]

    if not args.no_links:
        steps.append({
            'name': 'Step 7/7: 本地链接检查',
            'cmd': 'links',
            'argv': ['--path', target_dir],
            'continue_on_error': True,
        })

    failures = []
    for step in steps:
        print(f'\n{"─" * 60}')
        print(f'▶ {step["name"]}')
        print(f'{"─" * 60}')
        try:
            mod = _load_module(step['cmd'])
            old_argv = sys.argv[:]
            sys.argv = [f'docgov {step["cmd"]}'] + step['argv']
            try:
                mod.main(step['argv'])
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 0
                if code != 0 and not step.get('continue_on_error'):
                    failures.append(f'{step["name"]}: 退出码 {code}')
                    break
                elif code != 0:
                    failures.append(f'{step["name"]}: 退出码 {code}（已继续）')
            finally:
                sys.argv = old_argv
        except Exception as e:
            failures.append(f'{step["name"]}: 异常 {e}')
            if not step.get('continue_on_error'):
                break

    print(f'\n{"=" * 60}')
    print('治理完成')
    print(f'{"=" * 60}')
    if failures:
        print(f'\n⚠ 以下步骤报告了问题（不影响最终结果）:')
        for f in failures:
            print(f'  - {f}')
    else:
        print('\n✅ 所有步骤均成功完成')

    if dry_run:
        print('\n提示: 这是预览模式。确认无误后去掉 --dry-run 执行实际变更。')


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='docgov',
        description='文档元数据治理统一工具 - 整合 frontmatter 校验、TOML 元数据管理、链接检查等功能',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令:
  check       Frontmatter 完整性校验
  fix         修复 x-toml-ref 路径 + 创建缺失 TOML
  add-id      批量添加 id 字段
  add-title   批量添加 title 字段
  audit       元数据生态双向审计
  links       Markdown 链接检查
  doctor      一键全量治理（推荐）

示例:
  docgov doctor --dir docs/                  # 一键治理 docs/ 目录
  docgov doctor --dir docs/ --dry-run        # 预览模式，不写入
  docgov check --dir docs/                   # 仅校验 frontmatter
  docgov audit --dir docs/ --fix             # 审计并自动修复
  docgov links --path docs/                  # 检查本地链接

每个子命令的详细参数: docgov <command> --help
        """,
    )
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    for cmd_name, info in SUBCOMMANDS.items():
        sp = subparsers.add_parser(cmd_name, help=info['help'], add_help=False)
        sp.set_defaults(_cmd=cmd_name)

    doctor_parser = subparsers.add_parser(
        'doctor',
        help='一键全量治理：按顺序执行全套检查与修复',
        description='按安全顺序依次执行 add-title → add-id → fix → audit --fix → audit → check → links',
    )
    doctor_parser.add_argument('--dir', required=True, help='目标目录（相对于项目根）')
    doctor_parser.add_argument('--dry-run', action='store_true', help='预览模式，不写入文件')
    doctor_parser.add_argument('--no-links', action='store_true', help='跳过链接检查步骤')
    doctor_parser.set_defaults(_cmd='doctor')

    args, remaining = parser.parse_known_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args._cmd == 'doctor':
        cmd_doctor(args)
    else:
        _run_command(args._cmd, remaining)


if __name__ == '__main__':
    main()
