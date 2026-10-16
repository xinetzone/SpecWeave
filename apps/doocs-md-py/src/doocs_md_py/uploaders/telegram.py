"""Telegram 图床（upstream: providers.ts:565-607）。

两步：sendPhoto（multipart chat_id/photo）取 ``result.photo`` 最后一档的
``file_id`` → getFile 取 ``file_path`` → 拼本地 Bot API 文件 URL。
"""

from dataclasses import dataclass

import httpx

from .base import UploadFile

TELEGRAM_API_BASE = "https://api.telegram.org"


@dataclass(slots=True)
class TelegramConfig:
    token: str
    chat_id: str


def telegram_upload(
    config: TelegramConfig,
    file: UploadFile,
    http_client: httpx.Client,
) -> str:
    send_response = http_client.post(
        f"{TELEGRAM_API_BASE}/bot{config.token}/sendPhoto",
        data={"chat_id": config.chat_id},
        files={"photo": (file.name, file.content, file.content_type)},
    )
    send_res = send_response.json()
    photos = (send_res.get("result") or {}).get("photo") or []
    if not send_res.get("ok") or not photos:
        raise RuntimeError("upload.provider.telegramSendPhotoFailed")
    file_id = photos[-1]["file_id"]

    file_response = http_client.get(
        f"{TELEGRAM_API_BASE}/bot{config.token}/getFile",
        params={"file_id": file_id},
    )
    file_res = file_response.json()
    if not file_res.get("ok"):
        raise RuntimeError("upload.provider.telegramGetFileFailed")

    file_path = file_res["result"]["file_path"]
    return f"{TELEGRAM_API_BASE}/file/bot{config.token}/{file_path}"
