"""pytest 公共夹具：临时数据目录、存储、应用与已种 CSRF cookie 的客户端。"""

import pytest
from fastapi.testclient import TestClient

from travel_planner.config import LLMConfig, ensure_data_dir
from travel_planner.llm import LLMClient
from travel_planner.storage import TripStore
from travel_planner.web.app import create_app


@pytest.fixture()
def data_dir(tmp_path):
    return ensure_data_dir(tmp_path / "data")


@pytest.fixture()
def store(data_dir):
    return TripStore(data_dir)


@pytest.fixture()
def llm_cfg():
    return LLMConfig()


@pytest.fixture()
def client(store, llm_cfg):
    app = create_app(store, llm_cfg)
    with TestClient(app) as test_client:
        test_client.get("/trips")  # 首次 GET 签发 CSRF cookie
        yield test_client


@pytest.fixture()
def csrf(client):
    return client.cookies.get("tp_csrf")


@pytest.fixture()
def configured_llm_cfg():
    return LLMConfig(
        base_url="http://llm.test/v1",
        api_key="sk-test-SECRET",
        model="test-model",
        timeout=5.0,
    )


@pytest.fixture()
def mock_llm_client(configured_llm_cfg):
    """返回 (工厂, 请求捕获列表, 可替换的响应函数)。"""
    captured = []
    responder = {"fn": None}

    def handler(request):
        captured.append(request)
        fn = responder["fn"]
        if fn is None:
            return _default_draft_response()
        return fn(request)

    def factory():
        import httpx

        return LLMClient(configured_llm_cfg, transport=httpx.MockTransport(handler))

    return factory, captured, responder


def _default_draft_response():
    import httpx
    import json

    payload = {
        "days": [
            {
                "day_index": 1,
                "items": [
                    {
                        "type": "sight",
                        "start_time": "09:00",
                        "end_time": "11:30",
                        "title": "西湖环湖",
                        "location": "西湖",
                        "cost": 0,
                        "notes": "早上人少",
                    },
                    {
                        "type": "meal",
                        "start_time": "12:00",
                        "title": "楼外楼",
                        "location": "孤山路",
                        "cost": 120,
                    },
                ],
            },
            {
                "day_index": 2,
                "items": [
                    {
                        "type": "sight",
                        "title": "灵隐寺",
                        "cost": 45,
                        "notes": "需预约",
                    }
                ],
            },
        ]
    }
    content = json.dumps(payload, ensure_ascii=False)
    return httpx.Response(
        200, json={"choices": [{"message": {"role": "assistant", "content": content}}]}
    )


def create_trip(client, csrf, **overrides):
    """通过 Web 表单创建一个 3 天行程，返回 trip_id。"""
    data = {
        "name": "测试行程",
        "destination": "杭州",
        "start_date": "2026-10-01",
        "end_date": "2026-10-03",
        "currency": "CNY",
        "budget_total": "8000",
        "status": "planning",
        "notes": "",
        "csrf_token": csrf,
    }
    data.update(overrides)
    resp = client.post("/trips", data=data, follow_redirects=False)
    assert resp.status_code == 303, resp.text
    return resp.headers["location"].rsplit("/", 1)[-1]


def add_item(client, csrf, trip_id, **overrides):
    data = {
        "day_index": "1",
        "type": "sight",
        "title": "测试条目",
        "start_time": "",
        "end_time": "",
        "location": "",
        "cost": "",
        "notes": "",
        "csrf_token": csrf,
    }
    data.update(overrides)
    resp = client.post(
        f"/trips/{trip_id}/items", data=data, follow_redirects=False
    )
    assert resp.status_code == 303, resp.text
