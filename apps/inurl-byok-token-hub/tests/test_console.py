"""精简控制台端到端测试：会话重定向、四页渲染、明文不外泄、偏好与订单写回。"""

from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from inurl_byok_token_hub.api.app import create_app
from inurl_byok_token_hub.config import load_settings
from inurl_byok_token_hub.models import STRATEGIES, User
from inurl_byok_token_hub.services.hub import Hub, build_hub
from inurl_byok_token_hub.web.console import mount_console

#: 断言用的明文厂商 Key：任何页面 HTML 都不得出现该串
PLAIN_KEY = "sk-test-plain-key-123"
PASSWORD = "Console-Pass-1!"
PROVIDER_ID = "openai"

#: 目录文件不随 tmp 数据目录迁移，显式指向随包种子文件
CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "catalog.json"

#: 控制台四个页面的路径
PAGE_PATHS = ("/console/keys", "/console/usage", "/console/routes", "/console/plans")


@dataclass(frozen=True)
class ConsoleEnv:
    """测试夹具：已装配好控制台路由的 app 与一份用户数据。"""

    app: FastAPI
    hub: Hub
    user: User
    token: str

    def client(self) -> TestClient:
        return TestClient(self.app)

    def login(self) -> TestClient:
        """登录并返回已持有会话 Cookie 的客户端（TestClient 默认跟随重定向）。"""
        client = self.client()
        response = client.post("/console/login", data={"token": self.token}, follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/console/keys"
        return client


@pytest.fixture
def console(tmp_path: Path) -> ConsoleEnv:
    settings = load_settings(env={}, data_dir=tmp_path, catalog_path=CATALOG_PATH)
    hub = build_hub(settings)
    app = create_app(settings, hub=hub)
    mount_console(app, hub)

    result = hub.tokens.register("console@example.com", PASSWORD, vault=hub.vault)
    master = hub.unlock(result.user.id, PASSWORD)
    hub.vault.add_key(
        result.user.id,
        PROVIDER_ID,
        PLAIN_KEY,
        master,
        display_name="演示厂商",
        quota_total=5000,
    )
    hub.usage.record(
        user_id=result.user.id,
        provider_id=PROVIDER_ID,
        model_id="inurl",
        prompt_tokens=10,
        completion_tokens=20,
    )
    return ConsoleEnv(app=app, hub=hub, user=result.user, token=result.token)


def test_pages_require_session(console: ConsoleEnv) -> None:
    client = console.client()
    response = client.get("/console/keys", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/console/login"


def test_pages_hide_plaintext_key(console: ConsoleEnv) -> None:
    client = console.login()
    for path in PAGE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path
        body = response.text
        assert PLAIN_KEY not in body, f"{path} 泄露明文厂商 Key"
        assert console.token not in body, f"{path} 泄露统一令牌"


def test_routes_page_lists_all_strategies(console: ConsoleEnv) -> None:
    client = console.login()
    body = client.get("/console/routes").text
    missing = [key for key in STRATEGIES if key not in body]
    assert not missing, f"策略选项缺失：{missing}"


def test_routes_save_persists_strategy(console: ConsoleEnv) -> None:
    client = console.login()
    response = client.post(
        "/console/routes",
        data={
            "strategy": "round_robin",
            "combo": "轮询>随机",
            "compression": "ultra",
            "auto_models": "gpt-4o-mini",
            "auto_provider_order": "openai\nanthropic",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    saved = console.hub.store.settings.find(lambda s: s.user_id == console.user.id)
    assert saved is not None
    assert saved.strategy == "round_robin"
    assert saved.compression.value == "ultra"
    assert saved.combo == "轮询>随机"
    assert saved.auto_models == ("gpt-4o-mini",)
    assert saved.auto_provider_order == ("openai", "anthropic")


def test_plans_create_order_shows_id(console: ConsoleEnv) -> None:
    client = console.login()
    response = client.post(
        "/console/plans",
        data={"action": "create", "plan_key": "standard"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    order = console.hub.store.orders.find(lambda o: o.user_id == console.user.id)
    assert order is not None
    assert order.plan_key == "standard"

    body = client.get("/console/plans").text
    assert order.id in body
