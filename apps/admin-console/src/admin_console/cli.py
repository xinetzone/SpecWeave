"""命令行入口：admin-console serve / doctor / seed-admin。"""

import argparse
import asyncio
import getpass
import json
import os
import sys
from typing import Any, Dict, List

from .config import Config
from .store import build_store


def _wsgi_adapter(app):
    """WSGI -> ASGI 适配，供本地零依赖启动（复用 support-agent 范式）。"""

    def wsgi(environ, start_response):
        body = b""
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
            if length > 0:
                body = environ["wsgi.input"].read(length)
        except (TypeError, ValueError):
            body = b""

        headers: List[tuple] = []
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                name = key[5:].replace("_", "-").lower()
                headers.append((name.encode("latin-1"), str(value).encode("latin-1")))
        if environ.get("CONTENT_TYPE"):
            headers.append((b"content-type", environ["CONTENT_TYPE"].encode("latin-1")))

        scope = {
            "type": "http",
            "method": environ.get("REQUEST_METHOD", "GET"),
            "path": environ.get("PATH_INFO", "/") or "/",
            "query_string": (environ.get("QUERY_STRING", "") or "").encode("latin-1"),
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

    return wsgi


def _cmd_serve(args: argparse.Namespace) -> int:
    from wsgiref.simple_server import make_server

    from .asgi import build_app

    app = build_app()
    host = args.host or os.environ.get("HOST", "127.0.0.1")
    port = args.port or int(os.environ.get("PORT", "8000"))
    print(f"admin-console 已启动： http://{host}:{port}  （登录页 /login，后台 /app）")
    with make_server(host, port, _wsgi_adapter(app)) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    cfg = Config.from_env()
    store = build_store(cfg)
    report = {
        "cloud_ready": cfg.cloud_ready,
        "session_secret_persistent": not cfg.ephemeral_secret,
        "bucket": cfg.supabase_bucket,
        "max_upload_mb": round(cfg.max_upload_bytes / 1024 / 1024, 1),
        "storage": store.health(),
        "admins": store.count_admins() if hasattr(store, "count_admins") else None,
        "python": sys.version.split()[0],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not cfg.cloud_ready:
        print("\n提示：未配置 Supabase，当前为内存降级模式（数据不持久化）。")
        print("      配置 SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 后重跑本命令。")
    if cfg.ephemeral_secret:
        print("警告：未配置 SESSION_SECRET，会话密钥为进程内随机值，重启后需重新登录。")
    return 0 if cfg.cloud_ready else 1


def _cmd_seed_admin(args: argparse.Namespace) -> int:
    cfg = Config.from_env()
    store = build_store(cfg)
    email = (args.email or os.environ.get("ADMIN_EMAIL") or "").strip().lower()
    if not email:
        email = input("管理员邮箱：").strip().lower()
    if not email or "@" not in email:
        print("邮箱格式不正确")
        return 2
    password = args.password or os.environ.get("ADMIN_PASSWORD") or ""
    if not password:
        password = getpass.getpass("管理员口令（至少 8 位，输入不回显）：")
        if password != getpass.getpass("再次确认口令："):
            print("两次输入不一致")
            return 2
    if len(password) < 8:
        print("口令至少 8 位")
        return 2
    existing = store.admin_by_email(email)
    if existing and not args.force:
        print(f"账号 {email} 已存在（如需重置口令请加 --force）")
        return 1
    if existing:
        store.admins.pop(str(existing.get("id")), None)
    admin = store.create_admin(email, password, display_name=args.name or "", role=args.role)
    print(f"已{'重置' if existing else '创建'}管理员：{admin.get('email')}（角色 {admin.get('role')}）")
    if not cfg.cloud_ready:
        print("注意：当前为内存降级模式，该账号不会持久化。")
    return 0


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(prog="admin-console", description="通用内容管理后台")
    sub = parser.add_subparsers(dest="cmd")

    serve = sub.add_parser("serve", help="启动本地 Web 服务")
    serve.add_argument("--host", default="")
    serve.add_argument("--port", type=int, default=0)
    serve.set_defaults(func=_cmd_serve)

    doctor = sub.add_parser("doctor", help="检查云端与会话密钥配置")
    doctor.set_defaults(func=_cmd_doctor)

    seed = sub.add_parser("seed-admin", help="创建/重置管理员账号")
    seed.add_argument("--email", default="")
    seed.add_argument("--password", default="")
    seed.add_argument("--name", default="")
    seed.add_argument("--role", default="admin", choices=("admin", "editor"))
    seed.add_argument("--force", action="store_true", help="已存在时重置口令")
    seed.set_defaults(func=_cmd_seed_admin)

    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 2
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
