"""mdpy 命令行入口。

五个子命令（T1 阶段为骨架占位，随任务推进逐一接线）：

- ``render``：Markdown -> 微信兼容 HTML（T5-T9）；
- ``serve``：同源托管前端 dist 与 API（T19）；
- ``upload``：通过指定图床上传本地图片（T14/T19）；
- ``mcp``：启动 stdio MCP Server（T18）；
- ``migrate``：初始化/升级 SQLite 数据库（T3）。

上游对齐：packages/md-cli（Express 版仅绑 127.0.0.1、默认 8800）。
"""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

__all__ = ["main"]

_SUBCOMMANDS = ("render", "serve", "upload", "mcp", "migrate")


def _not_implemented(name: str) -> int:
    """占位处理器：明确告知子命令尚未实现（T1 骨架阶段）。"""
    print(f"mdpy {name}: 该子命令将在后续任务中实现（见 .trae/specs/doocs-md-py/tasks.md）", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    """构造顶层参数解析器与五个子命令占位。"""
    parser = argparse.ArgumentParser(
        prog="mdpy",
        description="doocs/md 的 Python 复刻：渲染库、自托管 API、图床上传器与 MCP 服务",
    )
    parser.add_argument("--version", action="version", version=f"mdpy {_pkg_version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="{render,serve,upload,mcp,migrate}")

    render_parser = subparsers.add_parser("render", help="将 Markdown 渲染为微信兼容 HTML")
    render_parser.add_argument("-i", "--input", help="Markdown 文件路径（缺省读标准输入）")
    render_parser.add_argument("-o", "--output", help="输出文件路径（缺省写标准输出）")

    serve_parser = subparsers.add_parser("serve", help="同源托管前端静态资产与 API 服务")
    serve_parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认仅本机；外部暴露需显式指定）")
    serve_parser.add_argument("--port", type=int, default=8800, help="监听端口（默认 8800，占用自动递增）")

    upload_parser = subparsers.add_parser("upload", help="通过指定图床上传图片")
    upload_parser.add_argument("--provider", required=True, help="图床标识（github/qiniu/s3/mp/...）")
    upload_parser.add_argument("--file", required=True, help="待上传图片路径")

    subparsers.add_parser("mcp", help="启动 stdio MCP Server")
    migrate_parser = subparsers.add_parser("migrate", help="初始化或升级 SQLite 数据库")
    migrate_parser.add_argument(
        "--db",
        default=str(Path("data") / "doocs-md-py.db"),
        help="SQLite 数据库路径（默认 data/doocs-md-py.db）",
    )
    return parser


def _handle_migrate(args: argparse.Namespace) -> int:
    """初始化/升级 SQLite（upstream: wrangler d1 migrations apply 的本地等价物）。"""
    from .server import db

    db_path = Path(args.db)
    if str(db_path.parent) not in ("", "."):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = db.connect(db_path)
    try:
        applied = db.apply_migrations(conn)
    finally:
        conn.close()
    if applied:
        print(f"已应用迁移：{', '.join(str(n) for n in applied)}")
    else:
        print("数据库已是最新，无新增迁移。")
    print(f"数据库路径：{db_path}")
    return 0


def _handle_mcp(_args: argparse.Namespace) -> int:
    """启动 stdio MCP Server（upstream: packages/mcp-server/src/index.ts:433-437）。"""
    from .mcp_server import main as mcp_main

    return mcp_main()


def _pkg_version() -> str:
    """延迟读取包版本，避免 argparse 构造期硬依赖。"""
    try:
        from doocs_md_py import __version__

        return __version__
    except ImportError:  # pragma: no cover
        return "unknown"


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 入口，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "migrate":
        return _handle_migrate(args)
    if args.command == "mcp":
        return _handle_mcp(args)
    return _not_implemented(args.command)
