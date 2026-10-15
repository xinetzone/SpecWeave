"""mdpy 命令行入口。

五个子命令：

- ``render``：Markdown -> 微信兼容 HTML（文件/标准输入 -> 片段或完整文档）；
- ``serve``：同源托管前端 dist 与 API（T19）；
- ``upload``：通过指定图床（web 端 13 家）上传本地图片并打印 URL；
- ``mcp``：启动 stdio MCP Server（T18）；
- ``migrate``：初始化/升级 SQLite 数据库（T3）。

上游对齐：packages/md-cli（Express 版仅绑 127.0.0.1、默认 8800）。
"""

import argparse
import html
import json
import mimetypes
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .user_config import (
    ENV_UPLOAD_FILE,
    ENV_UPLOAD_PROVIDER,
    UserConfigError,
    load_user_config,
)

__all__ = ["main"]

_SUBCOMMANDS = ("render", "serve", "upload", "mcp", "migrate")

# 上传器 HTTP 超时（上游浏览器 fetch 无显式超时，Python 侧给宽松值）
UPLOAD_HTTP_TIMEOUT = 30.0

DEFAULT_DOCUMENT_TITLE = "doocs/md 文档"

# ``--full-document`` 的完整 HTML 文档外壳（默认输出为库返回的片段）
FULL_DOCUMENT_TEMPLATE = (
    "<!DOCTYPE html>\n"
    '<html lang="zh-CN">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<title>{title}</title>\n"
    "</head>\n"
    "<body>\n{body}\n</body>\n"
    "</html>\n"
)


class CliUsageError(Exception):
    """CLI 使用性错误（输入文件缺失、图床未配置、参数非法等），退出码 2。"""


def build_parser() -> argparse.ArgumentParser:
    """构造顶层参数解析器与五个子命令。"""
    parser = argparse.ArgumentParser(
        prog="mdpy",
        description="doocs/md 的 Python 复刻：渲染库、自托管 API、图床上传器与 MCP 服务",
    )
    parser.add_argument("--version", action="version", version=f"mdpy {_pkg_version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="{render,serve,upload,mcp,migrate}")

    render_parser = subparsers.add_parser("render", help="将 Markdown 渲染为微信兼容 HTML")
    render_parser.add_argument("-i", "--input", help="Markdown 文件路径（缺省读标准输入）")
    render_parser.add_argument("-o", "--output", help="输出文件路径（缺省写标准输出）")
    render_parser.add_argument("--theme", help="主题标识（default/grace/simple）")
    render_parser.add_argument("--primary-color", help="主题色（如 #0F4C81）")
    render_parser.add_argument("--font-family", help="正文字体族")
    render_parser.add_argument("--font-size", help="正文字号（如 16px）")
    render_parser.add_argument("--line-height", help="行高（如 1.75）")
    render_parser.add_argument("--block-spacing", help="段间距（如 1）")
    render_parser.add_argument("--link-color", help="链接色（如 #576b95）")
    render_parser.add_argument("--blockquote-background", help="引用块底色")
    render_parser.add_argument("--legend", help="图注样式（alt/title/off）")
    render_parser.add_argument("--code-block-theme", help="代码块高亮主题 URL")
    render_parser.add_argument("--theme-mode", choices=["light", "dark"], help="明暗模式")
    render_parser.add_argument("--heading-styles", help='标题样式 JSON（如 {"h1":"color:#333"}）')
    render_parser.add_argument("--custom-css", help="自定义 CSS 文件路径")
    render_parser.add_argument("--mac-code-block", action="store_true", help="苹果风格代码块")
    render_parser.add_argument("--show-line-number", action="store_true", help="代码块显示行号")
    render_parser.add_argument("--cite-status", action="store_true", help="文末显示引用来源")
    render_parser.add_argument("--count-status", action="store_true", help="文首显示字数统计")
    render_parser.add_argument("--use-indent", action="store_true", help="正文首行缩进")
    render_parser.add_argument("--use-justify", action="store_true", help="正文两端对齐")
    render_parser.add_argument(
        "--full-document",
        action="store_true",
        help="输出完整 HTML 文档（缺省仅输出库返回的片段）",
    )

    serve_parser = subparsers.add_parser("serve", help="同源托管前端静态资产与 API 服务")
    serve_parser.add_argument("--host", default="127.0.0.1", help="监听地址（默认仅本机；外部暴露需显式指定）")
    serve_parser.add_argument("--port", type=int, default=8800, help="监听端口（默认 8800，占用自动递增）")

    upload_parser = subparsers.add_parser("upload", help="通过指定图床上传图片")
    upload_parser.add_argument(
        "--provider",
        help=f"图床标识（{_provider_ids()}）；也可由 {ENV_UPLOAD_PROVIDER} 提供",
    )
    upload_parser.add_argument("--file", help=f"待上传图片路径；也可由 {ENV_UPLOAD_FILE} 提供")
    upload_parser.add_argument(
        "--config",
        help="用户配置文件路径（缺省 ~/.config/doocs-md-py/config，可被 MD_CONFIG_FILE 覆盖）",
    )

    subparsers.add_parser("mcp", help="启动 stdio MCP Server")
    migrate_parser = subparsers.add_parser("migrate", help="初始化或升级 SQLite 数据库")
    migrate_parser.add_argument(
        "--db",
        default=str(Path("data") / "doocs-md-py.db"),
        help="SQLite 数据库路径（默认 data/doocs-md-py.db）",
    )
    return parser


def _provider_ids() -> str:
    from .uploaders import UPLOAD_PROVIDERS

    return "/".join(provider.id for provider in UPLOAD_PROVIDERS)


def _code_css_fetcher(url: str) -> str:
    """代码块高亮主题 CSS 抓取（与 MCP ``render_markdown`` 同一实现）。"""
    from .render.code_themes import fetch_code_block_css

    return fetch_code_block_css(url)


def _read_text_file(path: str, flag: str) -> str:
    file = Path(path).expanduser()
    if not file.is_file():
        raise CliUsageError(f"{flag} 指向的文件不存在：{file}")
    return file.read_text(encoding="utf-8")


def _read_markdown(path: str | None) -> str:
    if path is None:
        return sys.stdin.read()
    return _read_text_file(path, "-i/--input")


def _write_output(path: str | None, text: str) -> None:
    if path is None:
        sys.stdout.write(text)
        return
    target = Path(path).expanduser()
    if str(target.parent) not in ("", "."):
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _wrap_full_document(front_matter: object, body: str) -> str:
    raw_title = front_matter.get("title") if isinstance(front_matter, dict) else None
    title = str(raw_title).strip() if raw_title else DEFAULT_DOCUMENT_TITLE
    return FULL_DOCUMENT_TEMPLATE.format(title=html.escape(title), body=body)


def _handle_render(args: argparse.Namespace) -> int:
    """渲染 Markdown（upstream: packages/mcp-server render-article.ts 的 CLI 形态）。"""
    from .render.article import RenderArticleInput, build_rendered_output

    heading_styles = None
    if args.heading_styles:
        try:
            heading_styles = json.loads(args.heading_styles)
        except json.JSONDecodeError as exc:
            raise CliUsageError(f"--heading-styles 不是合法 JSON：{exc}") from exc
    custom_css = _read_text_file(args.custom_css, "--custom-css") if args.custom_css else None

    payload = RenderArticleInput(
        markdown=_read_markdown(args.input),
        theme=args.theme,
        primary_color=args.primary_color,
        font_family=args.font_family,
        font_size=args.font_size,
        line_height=args.line_height,
        block_spacing=args.block_spacing,
        link_color=args.link_color,
        blockquote_background=args.blockquote_background,
        legend=args.legend,
        code_block_theme=args.code_block_theme,
        theme_mode=args.theme_mode,
        heading_styles=heading_styles,
        custom_css=custom_css,
        # store_true 缺省 False；转成 None 以落回库默认值（上游 ``?? default`` 语义）
        is_mac_code_block=True if args.mac_code_block else None,
        is_show_line_number=True if args.show_line_number else None,
        cite_status=True if args.cite_status else None,
        count_status=True if args.count_status else None,
        is_use_indent=True if args.use_indent else None,
        is_use_justify=True if args.use_justify else None,
    )
    try:
        article = build_rendered_output(payload, code_css_fetcher=_code_css_fetcher)
    except ValueError as exc:
        raise CliUsageError(str(exc)) from exc

    rendered = article.html
    if args.full_document:
        rendered = _wrap_full_document(article.front_matter, rendered)
    _write_output(args.output, rendered)
    return 0


def _handle_serve(args: argparse.Namespace) -> int:
    """同源托管 dist + API（upstream: packages/md-cli/index.js:15-54）。"""
    from .server.app import serve

    return serve(host=args.host, port=args.port)


def _handle_upload(args: argparse.Namespace) -> int:
    """按 provider 分发到 uploaders（upstream: providers.ts UPLOAD_HANDLERS）。"""
    import httpx

    from . import uploaders
    from .uploaders import UPLOAD_PROVIDERS

    known = {provider.id for provider in UPLOAD_PROVIDERS}
    if args.provider not in known:
        raise CliUsageError(
            f"未知图床标识 {args.provider!r}；可选：{', '.join(sorted(known))}"
        )

    source = Path(args.file).expanduser()
    if not source.is_file():
        raise CliUsageError(f"--file 指向的文件不存在：{source}")

    try:
        settings = load_user_config(args.config)
    except UserConfigError as exc:
        raise CliUsageError(str(exc)) from exc

    provider = uploaders.resolve_upload_provider(args.provider)
    if provider.config_key:
        config = settings.get(provider.config_key)
        if config is None:
            raise CliUsageError(
                f"图床 {args.provider} 需要配置文件中的 [{provider.config_key}] 段"
                "（或经环境变量提供；凭证请勿入版本库）"
            )
    else:
        config = settings.get("config", {})

    content_type = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
    upload_file = uploaders.UploadFile(source.name, content_type, source.read_bytes())
    with httpx.Client(timeout=UPLOAD_HTTP_TIMEOUT) as client:
        url = uploaders.file_upload(provider.id, upload_file, config, client)
    print(url)
    return 0


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


_HANDLERS = {
    "render": _handle_render,
    "serve": _handle_serve,
    "upload": _handle_upload,
    "migrate": _handle_migrate,
    "mcp": _handle_mcp,
}


def _pkg_version() -> str:
    """延迟读取包版本，避免 argparse 构造期硬依赖。"""
    try:
        from doocs_md_py import __version__

        return __version__
    except ImportError:  # pragma: no cover
        return "unknown"


def _resolve_upload_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """``upload`` 的 --provider/--file/--config 支持环境变量回退。"""
    args.provider = args.provider or os.environ.get(ENV_UPLOAD_PROVIDER)
    args.file = args.file or os.environ.get(ENV_UPLOAD_FILE)
    args.config = args.config or os.environ.get("MD_CONFIG_FILE")
    missing = [flag for flag, value in (("--provider", args.provider), ("--file", args.file)) if not value]
    if missing:
        # argparse 语义：缺必需参数退出码 2
        parser.error(f"the following arguments are required: {', '.join(missing)}")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 入口，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "upload":
        _resolve_upload_args(parser, args)
    try:
        return _HANDLERS[args.command](args)
    except CliUsageError as exc:
        print(f"mdpy: error: {exc}", file=sys.stderr)
        return 2
