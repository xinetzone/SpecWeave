"""测试引导：将 src 布局加入导入路径，无需先 editable 安装即可运行 pytest。"""

import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# 凭证类变量在每个测试开始前置空：进程环境变量优先级高于项目根 .env 文件，
# 保证测试套件不受本地真实 .env（含联调凭证）影响。测试内显式构造参数
# （init kwargs 优先级最高）或自行 monkeypatch.setenv 均可正常覆盖。
_CREDENTIAL_ENV_KEYS = (
    "MP_ARCHIVER_WECHAT_APP_ID",
    "MP_ARCHIVER_WECHAT_APP_SECRET",
    "MP_ARCHIVER_WECHAT_OFFICIAL_BIZ",
    "MP_ARCHIVER_EXPORTER_TOKEN",
    "MP_ARCHIVER_WECHAT_APPSMSG_TOKEN",
    "MP_ARCHIVER_WECHAT_PASS_TICKET",
    "MP_ARCHIVER_WECHAT_KEY",
    "MP_ARCHIVER_WECHAT_WXUIN",
)


@pytest.fixture(autouse=True)
def _isolate_credentials(monkeypatch):
    for key in _CREDENTIAL_ENV_KEYS:
        monkeypatch.setenv(key, "")
    # get_settings 为进程级 lru_cache：避免用例间（尤其 CLI 用例）串味
    from mp_archiver.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
