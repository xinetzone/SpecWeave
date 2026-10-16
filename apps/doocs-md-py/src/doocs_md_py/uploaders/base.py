"""图床上传器公共基础设施（upstream: apps/web/src/services/upload/providers.ts）。

与 ``server/upload_github.py`` 的 API 侧上传不同，本包复刻的是 **Web 客户端**
13 家图床（providers.ts UPLOAD_HANDLERS）+ md-cli 的 dcloud 通道：
配置全部由调用方传入（上游为浏览器 localStorage），HTTP 统一走注入的
``httpx.Client``（测试注入 MockTransport 录制请求）。
"""

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(slots=True)
class UploadFile:
    """等价 providers.ts 用到的 File(name/type/arrayBuffer)。"""

    name: str
    content_type: str
    content: bytes


# upstream: providers.ts:47-53（本地时区 → Python 显式 UTC，见 T21 差异台账）
def get_dir(now_sec: float | None = None) -> str:
    """``YYYY/MM/DD`` 日期目录。"""
    return time.strftime("%Y/%m/%d", time.gmtime(now_sec if now_sec is not None else time.time()))


# upstream: providers.ts:56-60
def get_date_filename(
    filename: str,
    *,
    clock_ms: Callable[[], int] | None = None,
    uuid_factory: Callable[[], uuid.UUID] | None = None,
) -> str:
    """``<epoch_ms>-<uuid4>.<最后一个 . 后原文>``；无扩展名时尾段为空串（逐字 split/pop，不做大小写转换）。"""
    current_ms = clock_ms() if clock_ms is not None else int(time.time() * 1000)
    file_suffix = filename.split(".")[-1]
    u = uuid_factory() if uuid_factory is not None else uuid.uuid4()
    return f"{current_ms}-{u}.{file_suffix}"


def trim_trailing_slash(value: str) -> str:
    """upstream: cdnHost.endsWith('/') ? slice(0, -1)。"""
    return value[:-1] if value.endswith("/") else value


def require_config(value, name: str):
    """safeJsonParse 的缺失/坏 JSON 错误在配置解析层抛，消息保留上下文。"""
    if value is None:
        raise ValueError(f"{name} is missing or empty")
    return value
