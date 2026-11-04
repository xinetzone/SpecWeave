"""命令行入口：``info-butler serve``。

默认绑定 ``127.0.0.1``——个人信息管家存的是私人内容，不该在装好就默认
监听 0.0.0.0。要对外提供（容器内、云端实例）由部署侧显式传 ``--host 0.0.0.0``。

``--static`` 切换到**同源模式**：同一个进程既提供 API 也提供前端站点。
发布平台只暴露一个公网端口，同源是唯一免 CORS、免手填基址的形态。
"""

import argparse

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="info-butler", description="个人信息管家 Agent 服务端")
    parser.add_argument("--version", action="version", version=f"info-butler {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="启动 API 服务")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8787)
    serve.add_argument("--reload", action="store_true", help="开发模式热重载")
    serve.add_argument(
        "--static",
        action="store_true",
        help="同源模式：同时提供前端站点（需已构建 _build/html）",
    )
    serve.add_argument(
        "--static-dir",
        default=None,
        help="前端构建产物目录（默认 _build/html，可用 BUTLER_STATIC_DIR 覆盖）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "serve":
        import uvicorn

        if args.static:
            from .web import create_web_app

            app = create_web_app(static_dir=args.static_dir)
            uvicorn.run(app, host=args.host, port=args.port)
        else:
            uvicorn.run(
                "info_butler.api:create_app",
                factory=True,
                host=args.host,
                port=args.port,
                reload=args.reload,
            )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
