"""API 层测试：健康检查、问答、降级路径与静态页面托管。"""

import pytest
from fastapi.testclient import TestClient

from okfqa import llm
from okfqa.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------- 健康检查


def test_health_reports_ready(client, kb_db) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["db_ready"] is True
    assert data["stats"]["chunk_count"] == "4"
    assert data["llm_ready"] is False


def test_health_reports_missing_index(client) -> None:
    """索引缺失时健康检查如实上报，且接口本身不 500。"""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["db_ready"] is False
    assert "build_index.py" in (data["error"] or "")


# ---------------------------------------------------------------- 问答：降级路径


def test_ask_degrades_without_llm(client, kb_db, no_llm) -> None:
    res = client.post("/api/ask", json={"question": "道法自然是什么"})
    assert res.status_code == 200
    data = res.json()
    assert data["degraded"] is True
    assert data["hit_count"] > 0
    assert "未配置大模型凭据" in data["answer"]
    assert data["citations"][0]["bundle"] == "guoxue/daojia/laozi"


def test_ask_returns_503_when_index_missing(client) -> None:
    """索引缺失是部署问题，必须 503 显式报错，不能伪装成「知识库里没有答案」。"""
    res = client.post("/api/ask", json={"question": "任意问题"})
    assert res.status_code == 503
    assert "build_index.py" in res.json()["detail"]


def test_error_responses_leak_no_server_paths(client) -> None:
    """对外错误响应不得包含服务端目录结构。"""
    health = client.get("/api/health").json()
    assert "db_path" not in health
    assert health["error"]
    assert ":\\" not in health["error"] and "/vercel" not in health["error"]

    detail = client.post("/api/ask", json={"question": "任意问题"}).json()["detail"]
    assert ":\\" not in detail and "/vercel" not in detail


def test_ask_no_hit_is_not_degraded(client, kb_db, no_llm) -> None:
    res = client.post("/api/ask", json={"question": "量子纠缠超弦理论"})
    assert res.status_code == 200
    data = res.json()
    assert data["hit_count"] == 0
    assert data["citations"] == []
    assert "未检索到" in data["answer"]


# ---------------------------------------------------------------- 问答：大模型路径


def test_ask_uses_llm_when_configured(client, kb_db, monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    async def fake_chat(system: str, user: str, **kwargs) -> str:
        assert "参考资料" in user
        return "道法自然是道家思想的核心[1]。"

    monkeypatch.setattr(llm, "chat", fake_chat)

    res = client.post("/api/ask", json={"question": "道法自然是什么"})
    assert res.status_code == 200
    data = res.json()
    assert data["degraded"] is False
    assert data["answer"] == "道法自然是道家思想的核心[1]。"
    assert len(data["citations"]) >= 1


def test_ask_degrades_on_llm_failure(client, kb_db, monkeypatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    async def broken_chat(system: str, user: str, **kwargs) -> str:
        raise llm.LLMError("大模型请求超时（45s）")

    monkeypatch.setattr(llm, "chat", broken_chat)

    res = client.post("/api/ask", json={"question": "道法自然是什么"})
    assert res.status_code == 200
    data = res.json()
    assert data["degraded"] is True
    assert "超时" in data["error"]
    # 调用失败不得伪装成「未配置凭据」——两者处置手段完全不同
    assert "大模型调用失败" in data["answer"]
    assert "未配置大模型凭据" not in data["answer"]


# ---------------------------------------------------------------- 入参与静态资源


def test_ask_rejects_empty_question(client, kb_db) -> None:
    assert client.post("/api/ask", json={"question": ""}).status_code == 422


def test_ask_rejects_oversized_question(client, kb_db) -> None:
    assert client.post("/api/ask", json={"question": "问" * 501}).status_code == 422


def test_ask_clamps_top_k(client, kb_db, no_llm) -> None:
    res = client.post("/api/ask", json={"question": "知识包结构", "top_k": 99})
    assert res.status_code == 422  # 超出 1-20 白名单


def test_index_page_served(client) -> None:
    """Vercel Python 运行时不自动托管静态文件，必须由 FastAPI 显式提供（V4）。"""
    res = client.get("/")
    assert res.status_code == 200
    assert "OKF 知识库问答" in res.text


def test_static_asset_served(client) -> None:
    res = client.get("/static/app.js")
    assert res.status_code == 200
