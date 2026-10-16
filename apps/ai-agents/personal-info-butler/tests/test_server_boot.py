"""真·启动测试：uvicorn 能把这个 ASGI 应用跑起来并对外服务。

TestClient 只在进程内调用 ASGI，绕过了 uvicorn 的服务器装配与端口绑定；
而「发布上线」要求的是后者。缺口留着，就会出现「测试全绿但容器起不来」。
"""

import socket
import threading
import time

import httpx
import pytest
import uvicorn

from info_butler.api import create_app
from info_butler.config import Settings
from info_butler.llm import LLMClient
from info_butler.store import MemoryStore


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_uvicorn_serves_the_app():
    settings = Settings()
    app = create_app(settings=settings, store=MemoryStore(), llm=LLMClient(settings))
    port = _free_port()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(200):  # 最多等 10 秒
        if server.started:
            break
        time.sleep(0.05)

    try:
        assert server.started, "uvicorn 未能启动"
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5.0) as client:
            assert client.get("/api/health").json()["status"] == "ok"
            response = client.post(
                "/api/items", json={"content": "记得明天把定价方案发给客户"}
            )
            assert response.status_code == 201
            assert response.json()["item"]["kind"] == "todo"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def test_cli_builds_parser():
    """CLI 是可执行入口，至少要保证参数面没被改坏。"""
    from info_butler.cli import build_parser

    args = build_parser().parse_args(["serve", "--host", "0.0.0.0", "--port", "8080"])
    assert args.host == "0.0.0.0"
    assert args.port == 8080


def test_cli_rejects_unknown_command():
    from info_butler.cli import build_parser

    with pytest.raises(SystemExit):
        build_parser().parse_args([])
