"""命令行入口：support-agent serve / doctor / seed-faq。"""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List

from .config import Config
from .faq import BUILTIN_FAQ, FaqIndex
from .store import build_store


def _cmd_serve(args: argparse.Namespace) -> int:
    from wsgiref.simple_server import make_server

    from .asgi import build_app

    app = build_app()

    def wsgi(environ, start_response):
        """WSGI -> ASGI 适配，供本地零依赖启动。"""
        body = b""
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            if length > 0:
                body = environ["wsgi.input"].read(length)
        except (TypeError, ValueError):
            body = b""

        path = environ.get("PATH_INFO", "/") or "/"
        query = environ.get("QUERY_STRING", "") or ""
        headers = []
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                name = key[5:].replace("_", "-").lower()
                headers.append((name.encode("latin-1"), str(value).encode("latin-1")))
        if environ.get("CONTENT_TYPE"):
            headers.append((b"content-type", environ["CONTENT_TYPE"].encode("latin-1")))

        scope = {
            "type": "http",
            "method": environ.get("REQUEST_METHOD", "GET"),
            "path": path,
            "query_string": query.encode("latin-1"),
            "headers": headers,
        }
        queue: List[Dict[str, Any]] = [{"type": "http.request", "body": body, "more_body": False}]

        async def receive() -> Dict[str, Any]:
            return queue.pop(0) if queue else {"type": "http.disconnect"}

        sent: List[Dict[str, Any]] = []

        async def send(message: Dict[str, Any]) -> None:
            sent.append(message)

        asyncio.run(app(scope, receive, send))

        start_msg = next(m for m in sent if m["type"] == "http.response.start")
        body_msg = next((m for m in sent if m["type"] == "http.response.body"), None)
        start_response(
            f"{start_msg['status']} OK",
            [(k.decode("latin-1"), v.decode("latin-1")) for k, v in start_msg["headers"]],
        )
        return [body_msg["body"]] if body_msg else [b""]

    host = args.host or os.environ.get("HOST", "127.0.0.1")
    port = args.port or int(os.environ.get("PORT", "8000"))
    print(f"智能客服 Agent 已启动： http://{host}:{port}  （管理后台 /admin）")
    with make_server(host, port, wsgi) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    cfg = Config.from_env()
    store = build_store(cfg)
    faq = FaqIndex.load(cfg, store)
    report = {
        "cloud_ready": cfg.cloud_ready,
        "llm_ready": cfg.llm_ready,
        "admin_token": bool(cfg.admin_token),
        "storage": store.health(),
        "faq_count": len(faq.entries),
        "llm_model": cfg.llm_model,
        "llm_base_url": cfg.llm_base_url,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if cfg.cloud_ready else 1


def _cmd_seed_faq(args: argparse.Namespace) -> int:
    cfg = Config.from_env()
    if not cfg.cloud_ready:
        print("未配置 Supabase，跳过种子写入。")
        return 1
    store = build_store(cfg)
    added = 0
    existing = {str(row.get("id")) for row in (store.list_faq() or [])}
    for entry in BUILTIN_FAQ:
        if entry.id in existing:
            continue
        store.add_faq(entry.to_dict())
        added += 1
    print(f"已写入 {added} 条知识库条目到云端。")
    return 0


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(prog="support-agent", description="智能客服 Agent")
    sub = parser.add_subparsers(dest="cmd")

    serve = sub.add_parser("serve", help="启动本地 Web 服务")
    serve.add_argument("--host", default="")
    serve.add_argument("--port", type=int, default=0)
    serve.set_defaults(func=_cmd_serve)

    doctor = sub.add_parser("doctor", help="检查云端/大模型配置")
    doctor.set_defaults(func=_cmd_doctor)

    seed = sub.add_parser("seed-faq", help="把内置知识库写入云端")
    seed.set_defaults(func=_cmd_seed_faq)

    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
