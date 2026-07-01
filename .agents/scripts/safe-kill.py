#!/usr/bin/env python3

import argparse
import json
import sys

from lib.cli import setup_safe_output
from lib.process import safe_kill, get_process_cmdline


def main() -> int:
    setup_safe_output()

    parser = argparse.ArgumentParser(description="安全终止进程：kill 前先校验 cmdline 身份")
    parser.add_argument("--pid", type=int, required=True, help="目标 PID")
    parser.add_argument(
        "--contains",
        action="append",
        default=[],
        help="cmdline 必须包含的关键字（可重复指定）",
    )
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--kill", action="store_true", help="实际终止进程（默认仅校验 dry-run）")

    args = parser.parse_args()

    cmdline_res = get_process_cmdline(args.pid)
    ok, message = safe_kill(args.pid, args.contains, kill=args.kill)

    if args.json:
        payload = {
            "ok": ok,
            "pid": args.pid,
            "kill": bool(args.kill),
            "must_contain": list(args.contains),
            "message": message,
            "cmdline_ok": cmdline_res.ok,
            "cmdline_source": cmdline_res.source,
            "cmdline": cmdline_res.cmdline if cmdline_res.ok else None,
            "cmdline_error": None if cmdline_res.ok else cmdline_res.error,
        }
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"pid: {args.pid}")
        print(f"kill: {args.kill}")
        print(f"must_contain: {args.contains}")
        if cmdline_res.ok and cmdline_res.cmdline:
            print(f"cmdline({cmdline_res.source}): {cmdline_res.cmdline}")
        else:
            print(f"cmdline({cmdline_res.source}): <unavailable> {cmdline_res.error}")
        print(f"result: {message}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

