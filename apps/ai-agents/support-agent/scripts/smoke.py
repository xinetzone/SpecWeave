"""端到端冒烟脚本：本地起服务，走完 对话→转人工→评价→后台统计 全链路。

用法：PYTHONPATH=src python scripts/smoke.py
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://127.0.0.1:8321"
ADMIN = "smoke-admin"


def call(path, method="GET", payload=None, headers=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def main() -> int:
    run_env = dict(os.environ)
    run_env.update({"PYTHONPATH": str(ROOT / "src"), "ADMIN_TOKEN": ADMIN})
    proc = subprocess.Popen(
        [sys.executable, "-m", "support_agent.cli", "serve", "--port", "8321"],
        cwd=str(ROOT),
        env=run_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                call("/api/health")
                break
            except OSError:
                time.sleep(0.4)

        checks = []

        status, body = call("/api/health")
        checks.append(("health", status == 200, body[:80]))

        status, body = call("/api/chat", "POST", {"message": "我要申请退款", "session_id": "smoke-1"})
        data = json.loads(body)
        checks.append(("chat-refund-intent", data.get("intent") == "refund", data.get("intent")))

        status, body = call("/api/chat", "POST", {"message": "转人工", "session_id": "smoke-1"})
        data = json.loads(body)
        checks.append(("chat-human-ticket", bool(data.get("ticket_id")), data.get("ticket_id")))

        status, body = call("/api/feedback", "POST", {"rating": 5, "session_id": "smoke-1"})
        checks.append(("feedback", json.loads(body).get("ok") is True, body[:60]))

        status, body = call("/api/history?session_id=smoke-1")
        checks.append(("history", len(json.loads(body).get("messages", [])) >= 4, body[:60]))

        status, body = call("/")
        checks.append(("page-index", status == 200 and "<html" in body.lower(), str(status)))

        status, body = call("/admin")
        checks.append(("page-admin", status == 200 and "<html" in body.lower(), str(status)))

        status, body = call("/static/styles.css")
        checks.append(("static-css", status == 200, str(status)))

        status, body = call("/api/admin/overview", "GET", None, {"X-Admin-Token": ADMIN})
        stats = json.loads(body)
        checks.append(
            (
                "admin-overview",
                stats.get("sessions", 0) >= 1 and stats.get("avg_rating") == 5.0,
                f"sessions={stats.get('sessions')} rating={stats.get('avg_rating')}",
            )
        )

        status, body = call("/api/admin/sessions/smoke-1", "GET", None, {"X-Admin-Token": ADMIN})
        detail = json.loads(body)
        checks.append(("admin-detail", len(detail.get("messages", [])) >= 4, str(len(detail.get("messages", [])))))

        failed = [name for name, ok, _ in checks if not ok]
        for name, ok, info in checks:
            print(f"{'PASS' if ok else 'FAIL'}  {name}  {info}")
        return 1 if failed else 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
