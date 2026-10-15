"""默认图床（upstream: services/upload/client.ts，走 md-api ``POST /upload``）。

登录可选（Bearer 令牌提高限流档位）；失败体 message→error→HTTP 原因短语
逐级回退，抛出携带状态码与响应体的 UploadApiError。
"""

from dataclasses import dataclass

import httpx

from .base import UploadFile


class UploadApiError(RuntimeError):
    """upstream: client.ts:6-15 UploadApiError。"""

    def __init__(self, status: int, message: str, body: dict | None = None):
        super().__init__(message)
        self.status = status
        self.body = body


@dataclass(slots=True)
class DefaultConfig:
    api_base: str  # 等价 MD_API_URL（无尾斜杠）
    token: str = ""


def default_upload(
    config: DefaultConfig,
    file: UploadFile,
    http_client: httpx.Client,
) -> str:
    headers = {"Authorization": f"Bearer {config.token}"} if config.token else {}
    response = http_client.post(
        f"{config.api_base}/upload",
        files={"file": (file.name, file.content, file.content_type)},
        headers=headers,
    )
    if response.status_code // 100 != 2:
        message = response.reason_phrase
        body: dict | None = None
        try:
            body = response.json()
            if isinstance(body, dict):
                if isinstance(body.get("message"), str):
                    message = body["message"]
                elif isinstance(body.get("error"), str):
                    message = body["error"]
        except ValueError:
            pass
        raise UploadApiError(response.status_code, message, body)

    data = response.json()
    if not data.get("url"):
        raise UploadApiError(response.status_code, "upload_failed")
    return data["url"]
