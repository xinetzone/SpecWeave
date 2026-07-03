"""forum-bot CLI入口。

提供argparse命令行解析和命令分发。
"""

from __future__ import annotations

import argparse
import sys
import time

from .auth import do_login
from .logger import fail, logger, setup_logging
from .operations import do_clean_drafts, do_edit, do_read, do_reply

CLI_EPILOG = """使用方式：
  # 首次登录（打开有头浏览器，手动登录后按 Enter 保存状态）
  python forum-bot.py login

  # 读取帖子内容
  python forum-bot.py read 44601

  # 编辑帖子（从文件读取内容替换正文）
  python forum-bot.py edit 44601 --file new-content.md

  # 编辑帖子（直接指定文本，追加到开头）
  python forum-bot.py edit 44601 --prepend "📅 最新更新：2026年6月29日"

  # 发布回复
  python forum-bot.py reply 44601 --content "测试回复"

  # 发布回复（从文件读取内容）
  python forum-bot.py reply 44601 --file reply.md

  # 清理所有草稿
  python forum-bot.py clean-drafts

  # 试运行（不实际提交写操作）
  python forum-bot.py edit 44601 --content "测试" --dry-run

  # 调试模式（输出更详细日志）
  python forum-bot.py --debug read 44601
"""


def main() -> None:
    raw_args = sys.argv[1:]
    debug = "--debug" in raw_args or "-d" in raw_args
    if debug:
        raw_args = [a for a in raw_args if a not in ("--debug", "-d")]

    setup_logging(debug=debug)
    logger.info("forum-bot 启动 | Python %s | Playwright", sys.version.split()[0])
    logger.debug("命令行参数: %s", raw_args)

    parser = argparse.ArgumentParser(
        description="forum.trae.cn 论坛自动化操作工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CLI_EPILOG,
    )
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式（输出详细日志）")
    subparsers = parser.add_subparsers(dest="command", help="操作命令")

    sub_login = subparsers.add_parser("login", help="首次登录并保存状态")
    sub_login.add_argument("--headless", action="store_true", help="无头模式（不推荐）")

    sub_read = subparsers.add_parser("read", help="读取帖子内容")
    sub_read.add_argument("topic_id", type=int, help="帖子ID（如 44601）")
    sub_read.add_argument("--headless", action="store_true", default=True, help="无头模式（默认开启）")

    sub_edit = subparsers.add_parser("edit", help="编辑帖子正文")
    sub_edit.add_argument("topic_id", type=int, help="帖子ID")
    sub_edit.add_argument("--content", type=str, help="直接指定新内容")
    sub_edit.add_argument("--file", type=str, help="从Markdown文件读取内容")
    sub_edit.add_argument("--prepend", type=str, help="在帖子开头追加文本")
    sub_edit.add_argument("--dry-run", action="store_true", help="试运行，不提交")
    sub_edit.add_argument("--headless", action="store_true", default=False, help="无头模式（默认关闭）")
    sub_edit.add_argument("--no-notice", action="store_true", help="不自动添加AI发布声明（默认自动添加）")

    sub_reply = subparsers.add_parser("reply", help="发布回复")
    sub_reply.add_argument("topic_id", type=int, help="帖子ID")
    sub_reply.add_argument("--content", type=str, help="回复内容")
    sub_reply.add_argument("--file", type=str, help="从文件读取回复内容")
    sub_reply.add_argument("--dry-run", action="store_true", help="试运行，不提交")
    sub_reply.add_argument("--headless", action="store_true", default=False, help="无头模式（默认关闭）")
    sub_reply.add_argument("--no-notice", action="store_true", help="不自动添加AI发布声明（默认自动添加）")

    sub_clean = subparsers.add_parser("clean-drafts", help="清理所有草稿")
    sub_clean.add_argument("--headless", action="store_true", default=True, help="无头模式（默认开启）")

    args = parser.parse_args(raw_args)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    start_time = time.time()
    logger.info("执行命令: %s", args.command)

    try:
        if args.command == "login":
            do_login(headless=getattr(args, "headless", False), debug=debug)
        elif args.command == "read":
            do_read(args.topic_id, headless=getattr(args, "headless", True), debug=debug)
        elif args.command == "edit":
            do_edit(
                args.topic_id,
                content=args.content,
                content_file=args.file,
                prepend_text=args.prepend,
                dry_run=args.dry_run,
                headless=args.headless,
                debug=debug,
                add_notice=not args.no_notice,
            )
        elif args.command == "reply":
            do_reply(
                args.topic_id,
                content=args.content,
                content_file=args.file,
                dry_run=args.dry_run,
                headless=args.headless,
                debug=debug,
                add_notice=not args.no_notice,
            )
        elif args.command == "clean-drafts":
            do_clean_drafts(headless=getattr(args, "headless", True), debug=debug)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        logger.warning("用户中断 (Ctrl+C)")
        sys.exit(130)
    except Exception as e:
        logger.error("未捕获异常: %s: %s", type(e).__name__, e, exc_info=debug)
        fail(f"脚本异常退出: {e}")
        sys.exit(1)

    elapsed = time.time() - start_time
    logger.info("命令 %s 完成，耗时 %.1fs", args.command, elapsed)
