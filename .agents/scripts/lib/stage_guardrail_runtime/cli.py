import argparse

from lib.cli import print_error, add_common_args

from .demo import run_demo, run_full_flow
from .check import run_check
from .export_logs import run_export_logs
from .status import run_status


def main():
    parser = argparse.ArgumentParser(
        description='阶段守卫运行时强制执行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_common_args(parser)
    parser.add_argument('--demo', action='store_true',
                        help='使用内置demo演示运行时拦截功能（基础模式）')
    parser.add_argument('--full-flow', action='store_true',
                        help='演示完整S1→S8生命周期（含审批跳转、绕过检测）')
    parser.add_argument('--check', action='store_true',
                        help='单步拦截检查模式')
    parser.add_argument('--stage', type=str, help='阶段ID（S1~S8），--check模式必填')
    parser.add_argument('--role', type=str, help='执行角色')
    parser.add_argument('--op', type=str, help='操作类型（如write_code, clarify_requirement）')
    parser.add_argument('--detail', type=str, default='', help='操作描述文本')
    parser.add_argument('--export-logs', type=str, metavar='PATH',
                        help='将demo生成的SG-LOG日志导出到指定文件')
    parser.add_argument('--status', action='store_true',
                        help='显示运行时组件状态信息')
    parser.add_argument('--strict', action='store_true',
                        help='严格模式：WARN级别拦截返回非零退出码')
    parser.add_argument('--no-color', action='store_true',
                        help='禁用终端彩色输出')

    args = parser.parse_args()
    enable_color = not args.no_color

    mode_count = sum([args.demo, args.full_flow, args.check, bool(args.export_logs), args.status])
    if mode_count == 0:
        parser.print_help()
        return 0
    if mode_count > 1:
        print_error('只能选择一种模式（--demo/--full-flow/--check/--export-logs/--status）')
        return 2

    if args.demo:
        return run_demo(json_output=args.json, strict=args.strict, enable_color=enable_color)

    if args.full_flow:
        return run_full_flow(json_output=args.json, strict=args.strict, enable_color=enable_color)

    if args.check:
        if not args.stage or not args.role or not args.op:
            print_error('--check模式需要同时指定 --stage、--role、--op 参数')
            return 2
        return run_check(args.stage, args.role, args.op, detail=args.detail,
                         json_output=args.json, strict=args.strict, enable_color=enable_color)

    if args.export_logs:
        return run_export_logs(args.export_logs, enable_color=enable_color)

    if args.status:
        return run_status(json_output=args.json, enable_color=enable_color)

    return 0
