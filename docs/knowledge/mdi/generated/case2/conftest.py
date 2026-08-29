"""pytest配置和共享fixture。

base_url 覆盖优先级：命令行 --base-url > 环境变量 API_BASE_URL > frontmatter 默认值
api_token 覆盖优先级：命令行 --api-token > 环境变量 API_TOKEN > 无token
"""

import os
import pytest
import requests


def pytest_addoption(parser):
    """注册自定义命令行参数（幂等：重复调用不报错）。"""
    def _safe_addoption(*args, **kwargs):
        try:
            parser.addoption(*args, **kwargs)
        except ValueError:
            pass
    _safe_addoption(
        "--base-url",
        action="store",
        default=None,
        help="API基础URL，覆盖默认配置（也可通过API_BASE_URL环境变量设置）",
    )
    _safe_addoption(
        "--api-token",
        action="store",
        default=None,
        help="API认证Token，设置后自动加入Authorization头（也可通过API_TOKEN环境变量设置）",
    )


@pytest.fixture(scope="session")
def base_url(request):
    """API基础URL。优先级：命令行 > 环境变量 > 默认值。"""
    cli_url = request.config.getoption("--base-url")
    if cli_url:
        return cli_url.rstrip("/")
    env_url = os.environ.get("API_BASE_URL")
    if env_url:
        return env_url.rstrip("/")
    return "https://jsonplaceholder.typicode.com"


@pytest.fixture(scope="session")
def api_client(request):
    """共享requests session，自动配置Content-Type和认证头。"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    cli_token = request.config.getoption("--api-token")
    token = cli_token or os.environ.get("API_TOKEN")
    if token:
        session.headers.update({"Authorization": f"Bearer {token}"})
    yield session
    session.close()
