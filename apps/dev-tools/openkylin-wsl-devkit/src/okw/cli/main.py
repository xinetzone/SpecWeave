"""okw CLI 的装配与分发（运行时层）。

职责边界：解析 argv → 计算注册表键 → 调用 handler；这里是 OkwError 的
唯一收口点。parser 装配在 okw.cli.parser，handler 在 okw.commands。
非 OkwError 异常不伪装、不吞（属程序缺陷，保留 traceback）。
"""

import sys

from okw.cli.parser import build_parser
from okw.commands import COMMAND_HANDLERS
from okw.errors import OkwError


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2

    if args.command == "ai":
        if not args.ai_cmd:
            args._group_help()
            return 2
        key = f"ai {args.ai_cmd}"
    elif args.command == "podman":
        if not args.podman_cmd:
            args._group_help()
            return 2
        key = f"podman {args.podman_cmd}"
    elif args.command == "compose":
        if not args.compose_cmd:
            args._group_help()
            return 2
        key = f"compose {args.compose_cmd}"
    elif args.command == "image":
        if not args.image_cmd:
            args._group_help()
            return 2
        key = f"image {args.image_cmd}"
    elif args.command == "desktop":
        if not args.desktop_cmd:
            args._group_help()
            return 2
        key = f"desktop {args.desktop_cmd}"
    else:
        key = args.command

    # KeyError 不可达：顶层/子命令键的有效性由 argparse choices 在解析期保证，
    # 未知命令先以 SystemExit(2) 退出；注册表键集又经 build_parser 叶子集交叉测试锁定。
    handler = COMMAND_HANDLERS[key]
    try:
        return handler(args)
    except OkwError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
