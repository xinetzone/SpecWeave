"""sg-dashboard 命令行入口。

提供argparse解析和main()函数，串联解析→聚合→渲染流程。
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project import resolve_project_root
from lib.cli import setup_safe_output

from .aggregator import aggregate_entries
from .demo import generate_demo_entries
from .parser import collect_log_files, parse_log_file
from .renderer import generate_html_dashboard


def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description='阶段守卫日志聚合可视化仪表盘生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--log-dir', type=str, help='日志目录（默认: .agents/logs/）')
    parser.add_argument('--output', type=str, help='输出HTML路径')
    parser.add_argument('--demo', action='store_true', help='使用内置demo数据生成')
    parser.add_argument('--open', action='store_true', help='生成后自动打开浏览器')
    parser.add_argument('--json', action='store_true', dest='json_output', help='输出JSON数据')
    parser.add_argument('--title', type=str, default='阶段守卫日志仪表盘', help='仪表盘标题')
    args = parser.parse_args()

    project_root = resolve_project_root(SCRIPTS_DIR)

    if args.demo:
        entries = generate_demo_entries()
        source_desc = '内置Demo数据（8个模拟会话）'
    else:
        log_dir = Path(args.log_dir) if args.log_dir else (project_root / '.agents' / 'logs')
        log_files = collect_log_files(log_dir)
        if not log_files:
            print(f'⚠️ 日志目录 {log_dir} 中未找到 .log 文件')
            print('   提示: 使用 --demo 生成内置demo仪表盘，或先用 check-stage-guardrail-runtime.py --export-logs 生成日志')
            return 1
        entries = []
        for f in log_files:
            entries.extend(parse_log_file(f))
        source_desc = f'{log_dir} ({len(log_files)} 个文件)'

    if not entries:
        print('❌ 未解析到任何 [SG-LOG]/[PDR-LOG] 日志条目')
        return 1

    stats = aggregate_entries(entries)

    if args.json_output:
        data = {
            'summary': {
                'total_sessions': stats.total_sessions,
                'total_entries': stats.total_entries,
                'interception_rate': round(stats.interception_rate, 2),
                'approval_rate': round(stats.approval_rate, 2),
                'completion_rate': round(stats.completion_rate, 2),
                'total_intercepted': stats.total_intercepted,
                'total_bypasses': stats.total_bypasses,
                'total_errors': stats.total_errors,
            },
            'event_counts': dict(stats.event_counts),
            'top_intercept_reasons': stats.top_intercept_reasons,
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        if not args.output:
            return 0

    output_path = Path(args.output) if args.output else (project_root / '.agents' / 'reports' / 'sg-dashboard.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = generate_html_dashboard(stats, title=args.title, generated_from=source_desc)
    output_path.write_text(html, encoding='utf-8')

    print(f'✅ 仪表盘已生成: {output_path}')
    print(f'   会话数: {stats.total_sessions}')
    print(f'   日志条目: {stats.total_entries}')
    print(f'   拦截率: {stats.interception_rate:.1f}%')
    print(f'   审批通过率: {stats.approval_rate:.1f}%')
    print(f'   绕过检测: {stats.total_bypasses} | ERROR: {stats.total_errors}')

    if args.open:
        webbrowser.open(output_path.as_uri())

    return 0
