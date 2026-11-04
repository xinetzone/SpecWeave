"""同源部署形态的测试。

发布平台只暴露**一个**公网端口，因此「前端与 API 同源」不是可选优化，
而是发布的硬前提。本组测试守住三件事：

1. 静态站点挂上后，``/api/*`` 仍由 API 路由处理（不被静态处理器截走）；
2. 首页直达工作台，不必在文档里翻两级；
3. 前端没构建时给出**可诊断**的说明页，而不是空白页或 404 谜语。
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from info_butler.config import Settings
from info_butler.llm import LLMClient
from info_butler.store import MemoryStore
from info_butler.web import WORKBENCH_PAGE, create_web_app, resolve_static_dir

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _app(static_dir=None):
    settings = Settings()
    return create_web_app(
        settings=settings, store=MemoryStore(), llm=LLMClient(settings), static_dir=static_dir
    )


def test_missing_static_dir_returns_diagnostic_page(tmp_path):
    """没有前端时也要有可读的页面——空白页会被误读成「产品坏了」。"""
    app = _app(static_dir=tmp_path / "nope")
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "前端尚未构建" in response.text
    assert "/api/health" in response.text


def test_api_still_works_when_static_is_mounted(tmp_path):
    """静态挂载不能吃掉 API 路由——路由顺序错了这里就会 404。"""
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html>docs</html>", encoding="utf-8")
    (site / WORKBENCH_PAGE).write_text("<html>workbench</html>", encoding="utf-8")

    app = _app(static_dir=site)
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"
        created = client.post("/api/items", json={"content": "同源测试"})
        assert created.status_code == 201


def test_root_redirects_to_workbench(tmp_path):
    """首页应直达工作台——产品主界面不该藏在文档两级之下。"""
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html>docs</html>", encoding="utf-8")
    (site / WORKBENCH_PAGE).write_text("<html>workbench</html>", encoding="utf-8")

    app = _app(static_dir=site)
    with TestClient(app) as client:
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (302, 307)
        assert response.headers["location"].endswith(WORKBENCH_PAGE)

        followed = client.get("/")
        assert followed.status_code == 200
        assert "workbench" in followed.text


def test_resolve_static_dir_prefers_explicit_path(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<html>x</html>", encoding="utf-8")
    assert resolve_static_dir(site) == site


def test_resolve_static_dir_returns_none_when_incomplete(tmp_path):
    """缺 index.html 的目录不算构建产物——否则会挂载出一个残缺站点。"""
    incomplete = tmp_path / "site"
    incomplete.mkdir()
    assert resolve_static_dir(incomplete) is None


def test_cli_exposes_static_flags():
    from info_butler.cli import build_parser

    args = build_parser().parse_args(["serve", "--static", "--static-dir", "/tmp/site"])
    assert args.static is True
    assert args.static_dir == "/tmp/site"


def test_cli_default_is_api_only():
    """默认仍是纯 API——本地开发者不该被迫先构建站点。"""
    from info_butler.cli import build_parser

    args = build_parser().parse_args(["serve"])
    assert args.static is False
    assert args.static_dir is None


@pytest.mark.skipif(
    not (PROJECT_ROOT / "_build" / "html" / WORKBENCH_PAGE).is_file(),
    reason="尚未构建 Sphinx 站点",
)
def test_built_site_is_served():
    """真实构建产物：工作台页面与 API 在同一个服务上。"""
    app = _app()
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        page = client.get(f"/{WORKBENCH_PAGE}")
        assert page.status_code == 200
        # 前端挂载点必须在页面里，否则按钮点了没反应
        for anchor in ('id="composer"', 'id="btn-capture"', 'id="item-list"'):
            assert anchor in page.text, f"工作台缺少挂载点 {anchor}"
