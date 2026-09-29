"""公共 fixture：临时数据目录 + Settings + Hub + TestClient。

运行期数据一律落在 ``tmp_path``，不污染仓库；目录使用应用内置种子数据。
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from inurl_byok_token_hub.api.app import create_app
from inurl_byok_token_hub.config import load_settings
from inurl_byok_token_hub.services.hub import build_hub

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "catalog.json"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    target = tmp_path / "runtime"
    target.mkdir(parents=True, exist_ok=True)
    return target


@pytest.fixture
def settings(data_dir: Path):
    return load_settings(data_dir=data_dir, catalog_path=CATALOG_PATH)


@pytest.fixture
def hub(settings):
    return build_hub(settings)


@pytest.fixture
def client(settings, hub) -> TestClient:
    return TestClient(create_app(settings, hub=hub))


@pytest.fixture
def registered(hub):
    """注册一个普通用户并解锁密钥库，返回 (result, master_key)。"""
    result = hub.tokens.register("user@local", "user-password", vault=hub.vault)
    master = hub.unlock(result.user.id, "user-password")
    return result, master
