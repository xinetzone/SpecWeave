"""CLI 测试：serve 的 WSGI 适配器、doctor 体检、seed-faq 守卫。

为什么补这一层：cli.py 曾是 0% 覆盖（89 条语句），是仓库 80% 覆盖率硬门
最大的单点缺口；且 serve 的 WSGI 适配器是「本地零依赖启动」的唯一入口，
一旦环境变量解析或 header 拼装出错，部署端才会暴露。
"""

import io
import json

import pytest

from support_agent import cli


ENV_KEYS = (
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_KEY",
    "LLM_BASE_URL",
    "LLM_API_KEY",
    "LLM_MODEL",
    "ADMIN_TOKEN",
    "APP_BRAND",
    "HOST",
    "PORT",
)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """清空外部环境变量，避免开发者本机配置污染断言。"""
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


class FakeServer:
    """替身：捕获 host/port 与 WSGI 可调用对象，不真正监听端口。"""

    def __init__(self, host, port, handler):
        self.host = host
        self.port = port
        self.handler = handler
        self.served = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def serve_forever(self):
        self.served = True


def test_main_without_subcommand_prints_help(capsys):
    """无子命令时应打印帮助并返回 2（供 CLI 约定判定用法错误）。"""
    assert cli.main([]) == 2
    assert "usage" in capsys.readouterr().out.lower()


def test_doctor_reports_degraded_state(capsys):
    """未配置云端时 doctor 应报告降级且以非零码退出。"""
    code = cli.main(["doctor"])
    report = json.loads(capsys.readouterr().out)
    assert code == 1
    assert report["cloud_ready"] is False
    assert report["faq_count"] > 0
    assert report["storage"]["ok"] is True


def test_doctor_reports_configured_state(monkeypatch, capsys):
    """配置齐备时 doctor 应退出 0，并如实反映管理员令牌与大模型状态。"""
    monkeypatch.setenv("SUPABASE_URL", "https://example.test")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "secret")
    monkeypatch.setenv("ADMIN_TOKEN", "admintoken")
    monkeypatch.setenv("LLM_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODEL", "deepseek-chat")

    code = cli.main(["doctor"])
    report = json.loads(capsys.readouterr().out)
    assert code == 0
    assert report["cloud_ready"] is True
    assert report["llm_ready"] is True
    assert report["admin_token"] is True
    assert report["llm_model"] == "deepseek-chat"


def test_seed_faq_skips_without_cloud(capsys):
    """未配置 Supabase 时不得静默写入，应明确跳过并返回非零码。"""
    code = cli.main(["seed-faq"])
    assert code == 1
    assert "跳过" in capsys.readouterr().out


def test_serve_binds_host_and_port_from_env(monkeypatch, capsys):
    """serve 必须认 PORT/HOST 环境变量（部署沙箱靠 PORT 注入端口）。"""
    import wsgiref.simple_server as simple_server

    captured = {}

    def fake_make_server(host, port, handler):
        server = FakeServer(host, port, handler)
        captured["server"] = server
        return server

    monkeypatch.setattr(simple_server, "make_server", fake_make_server)
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "9123")

    assert cli.main(["serve"]) == 0
    server = captured["server"]
    assert server.host == "0.0.0.0"
    assert server.port == 9123
    assert server.served is True
    assert "已启动" in capsys.readouterr().out


def test_serve_wsgi_adapter_handles_post_json(monkeypatch):
    """WSGI 适配器须正确搬运 body / query / header，并返回 ASGI 的响应体。"""
    import wsgiref.simple_server as simple_server

    captured = {}
    monkeypatch.setattr(
        simple_server,
        "make_server",
        lambda host, port, handler: captured.setdefault("server", FakeServer(host, port, handler)),
    )
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "9124")
    monkeypatch.setenv("ADMIN_TOKEN", "admintoken")
    cli.main(["serve"])

    handler = captured["server"].handler
    body = json.dumps({"message": "我要退款"}).encode("utf-8")
    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": "/api/chat",
        "QUERY_STRING": "",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.input": io.BytesIO(body),
    }
    seen = {}

    def start_response(status, headers):
        seen["status"] = status
        seen["headers"] = headers

    chunks = handler(environ, start_response)
    data = json.loads(b"".join(chunks).decode("utf-8"))

    assert seen["status"].startswith("200")
    assert data["session_id"].startswith("s_")
    assert data["intent"] == "refund"
    header_names = {name for name, _ in seen["headers"]}
    assert "content-type" in header_names


def test_serve_wsgi_adapter_forwards_request_headers(monkeypatch):
    """请求头必须被搬运成 ASGI header：HTTP_X_ADMIN_TOKEN -> x-admin-token。

    用管理员鉴权做功能断言——只有 header 真的转成了小写连字符形式，
    /api/admin/overview 才可能鉴权通过。
    """
    import wsgiref.simple_server as simple_server

    captured = {}
    monkeypatch.setattr(
        simple_server,
        "make_server",
        lambda host, port, handler: captured.setdefault("server", FakeServer(host, port, handler)),
    )
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "9126")
    monkeypatch.setenv("ADMIN_TOKEN", "admintoken")
    cli.main(["serve"])

    handler = captured["server"].handler

    def call_admin(token):
        environ = {
            "REQUEST_METHOD": "GET",
            "PATH_INFO": "/api/admin/overview",
            "QUERY_STRING": "",
            "wsgi.input": io.BytesIO(b""),
        }
        if token is not None:
            environ["HTTP_X_ADMIN_TOKEN"] = token
        seen = {}
        chunks = handler(environ, lambda status, headers: seen.update(status=status))
        return seen["status"], json.loads(b"".join(chunks).decode("utf-8"))

    status, data = call_admin("admintoken")
    assert status.startswith("200")
    assert "totals" in data or "sessions" in data or isinstance(data, dict)

    status, _data = call_admin("wrong-token")
    assert status.startswith("401")

    status, _data = call_admin(None)
    assert status.startswith("401")


def test_serve_wsgi_adapter_tolerates_bad_content_length(monkeypatch):
    """CONTENT_LENGTH 非法时不得抛异常，按空 body 处理。"""
    import wsgiref.simple_server as simple_server

    captured = {}
    monkeypatch.setattr(
        simple_server,
        "make_server",
        lambda host, port, handler: captured.setdefault("server", FakeServer(host, port, handler)),
    )
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "9125")
    cli.main(["serve"])

    handler = captured["server"].handler
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/api/health",
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "not-a-number",
        "wsgi.input": io.BytesIO(b""),
    }
    seen = {}
    chunks = handler(environ, lambda status, headers: seen.update(status=status))
    data = json.loads(b"".join(chunks).decode("utf-8"))
    assert seen["status"].startswith("200")
    assert data["ok"] is True
