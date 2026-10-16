"""本地冒烟：未配置云端时全链路自检（登录 → 看板 → 新建 → 编辑 → 删除 → 上传 → 登出）。

不联网、不需要 Supabase；退出码 0 表示全链路通过。
用法：python scripts/smoke.py
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from admin_console.asgi import Request, build_context, dispatch  # noqa: E402
from admin_console.config import Config  # noqa: E402
from admin_console.store import MemoryStore  # noqa: E402

HOST = "127.0.0.1:8000"
ORIGIN = f"http://{HOST}"
FAILED = []


def call(ctx, method, path, body=b"", headers=None, query=""):
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": query.encode("utf-8"),
        "headers": [(k.encode("latin-1"), v.encode("latin-1")) for k, v in (headers or {}).items()],
    }
    status, resp_headers, payload = dispatch(ctx, Request(scope, body))
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        data = {}
    return status, resp_headers, data


def check(label, condition, detail=""):
    mark = "OK  " if condition else "FAIL"
    print(f"[{mark}] {label}{(' — ' + detail) if detail else ''}")
    if not condition:
        FAILED.append(label)


def main() -> int:
    os.environ.pop("SUPABASE_URL", None)
    os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)
    cfg = Config.from_env()
    cfg.session_secret = "smoke-secret"  # nosec 本地冒烟专用，非真实密钥
    store = MemoryStore(cfg)
    ctx = build_context(cfg, store)

    print("== 1. 健康检查 ==")
    status, _, data = call(ctx, "GET", "/api/health")
    check("health 返回 200", status == 200)
    check("未配置云端时标记 degraded", data.get("degraded") is True)

    print("== 2. 登录认证 ==")
    status, headers, data = call(ctx, "POST", "/api/auth/login",
                                 body=json.dumps({"email": "admin@example.com", "password": "wrong"}).encode(),
                                 headers={"content-type": "application/json", "host": HOST, "origin": ORIGIN})
    check("错误口令被拒绝", status == 401, data.get("message", ""))

    status, headers, data = call(ctx, "POST", "/api/auth/login",
                                 body=json.dumps({"email": cfg.demo_admin_email,
                                                  "password": cfg.demo_admin_password}).encode(),
                                 headers={"content-type": "application/json", "host": HOST, "origin": ORIGIN})
    check("正确口令登录成功", status == 200)
    cookies = {}
    for key, value in headers:
        if key.lower() == b"set-cookie":
            name, _, raw = value.decode("latin-1").partition("=")
            cookies[name] = raw.split(";")[0]
    check("下发会话与 CSRF Cookie", bool(cookies.get("ac_session")) and bool(cookies.get("ac_csrf")))

    auth_headers = {
        "cookie": f"ac_session={cookies.get('ac_session','')}; ac_csrf={cookies.get('ac_csrf','')}",
        "x-csrf-token": cookies.get("ac_csrf", ""),
        "host": HOST,
        "origin": ORIGIN,
        "content-type": "application/json",
    }

    print("== 3. 鉴权边界 ==")
    status, _, _ = call(ctx, "GET", "/api/items")
    check("未登录访问 API 返回 401", status == 401)
    no_csrf = dict(auth_headers)
    no_csrf.pop("x-csrf-token")
    status, _, _ = call(ctx, "POST", "/api/items", body=json.dumps({"title": "x"}).encode(), headers=no_csrf)
    check("缺 CSRF 返回 403", status == 403)

    print("== 4. 数据看板 ==")
    status, _, data = call(ctx, "GET", "/api/dashboard", headers=auth_headers)
    check("看板聚合可用", status == 200 and "by_status" in data)
    check("看板含 14 天趋势", len(data.get("trend", [])) == 14)

    print("== 5. 列表与表单 ==")
    status, _, data = call(ctx, "POST", "/api/items",
                           body=json.dumps({"title": "冒烟内容", "status": "draft", "tags": ["冒烟"]}).encode(),
                           headers=auth_headers)
    check("新建内容成功", status == 200, str(data.get("item", {}).get("title", "")))
    item = data.get("item", {})
    status, _, data = call(ctx, "GET", "/api/items", headers=auth_headers, query="q=%E5%86%92%E7%83%9F")
    check("关键词搜索命中", status == 200 and data.get("total", 0) >= 1, f"total={data.get('total')}")
    status, _, data = call(ctx, "PATCH", f"/api/items/{item.get('id','')}",
                           body=json.dumps({"status": "published",
                                            "expected_updated_at": item.get("updated_at", "")}).encode(),
                           headers=auth_headers)
    check("编辑并发布成功", status == 200 and data.get("item", {}).get("status") == "published")

    print("== 6. 云端存储（降级态） ==")
    status, _, data = call(ctx, "POST", "/api/uploads", body=b"\x89PNG\r\n", headers={
        "cookie": auth_headers["cookie"],
        "x-csrf-token": cookies.get("ac_csrf", ""),
        "x-file-name": "smoke.png",
        "content-type": "image/png",
        "host": HOST,
        "origin": ORIGIN,
    })
    check("附件上传成功（降级为 memory://）", status == 200, str(data.get("attachment", {}).get("url", "")))
    status, _, data = call(ctx, "POST", "/api/uploads", body=b"MZ", headers={
        "cookie": auth_headers["cookie"],
        "x-csrf-token": cookies.get("ac_csrf", ""),
        "x-file-name": "bad.exe",
        "content-type": "application/x-msdownload",
        "host": HOST,
        "origin": ORIGIN,
    })
    check("非法类型被拒（415）", status == 415)

    print("== 7. 删除与日志 ==")
    status, _, _ = call(ctx, "DELETE", f"/api/items/{item.get('id','')}", body=b"{}", headers=auth_headers)
    check("删除内容成功", status == 200)
    status, _, data = call(ctx, "GET", "/api/logs", headers=auth_headers, query="limit=5")
    check("操作日志落库", status == 200 and len(data.get("logs", [])) >= 1,
          f"{len(data.get('logs', []))} 条")

    print("== 8. 登出 ==")
    status, _, _ = call(ctx, "POST", "/api/auth/logout", body=b"{}", headers=auth_headers)
    check("登出成功", status == 200)

    print()
    if FAILED:
        print(f"冒烟失败 {len(FAILED)} 项：" + "、".join(FAILED))
        return 1
    print("冒烟全部通过（内存降级模式，未联网）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
