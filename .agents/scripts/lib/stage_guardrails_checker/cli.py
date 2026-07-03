import argparse
from pathlib import Path

from lib.cli import print_error, add_common_args, setup_safe_output

from .demo import DEMO_LOGS
from .reporter import run_analysis


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description='阶段守卫日志分析工具')
    add_common_args(parser)
    parser.add_argument('--log-file', type=str, help='会话日志文件路径')
    parser.add_argument('--demo', action='store_true', help='使用内置示例日志演示分析功能')
    parser.add_argument('--strict', action='store_true', help='严格模式: WARN级别异常也返回非零退出码')
    args = parser.parse_args()

    if args.demo:
        print("=== 使用内置示例日志进行演示分析 ===\n")
        return run_analysis(DEMO_LOGS, json_output=args.json, strict=args.strict)

    if not args.log_file:
        print_error("必须指定 --log-file <路径> 或使用 --demo")
        parser.print_help()
        return 1

    log_path = Path(args.log_file)
    if not log_path.exists():
        print_error(f"日志文件不存在: {log_path}")
        return 1

    try:
        content = log_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        print_error(f"读取日志文件失败: {e}")
        return 1

    return run_analysis(content, json_output=args.json, strict=args.strict)