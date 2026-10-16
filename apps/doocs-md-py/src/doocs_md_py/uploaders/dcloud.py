"""DCloud unicloud 图床（upstream: packages/md-cli/util.js dcloud()，Q4 通道）。

四步：anonymousAuthorize → generateProximalSign → OSS form POST → report。
签名为 ``HMAC-MD5``：键名字典序、``k=v&k=v``（值原样字符串化，不做 URL 编码）
hex 摘要，放 ``x-serverless-sign`` 头。两个历史拼写逐字保留：
① 最终 OSS 表单头 ``X-OSS-server-side-encrpytion``（encrpytion 少一个 y）；
② params 字段里的 JSON 字符串为手拼/预置字面。
"""

import hashlib
import hmac
import json
import time
from collections.abc import Callable
from dataclasses import dataclass

import httpx

from .base import UploadFile

BSPCAPP_ENDPOINT = "https://api.bspapp.com/client"
# 逐字 md-cli util.js:136（历史拼写，禁止“修正”）
OSS_ENCRYPTION_HEADER = "X-OSS-server-side-encrpytion"


def dcloud_sign(data: dict, secret: str) -> str:
    """upstream util.js:58-64：sorted keys → ``k=v&k=v`` → HMAC-MD5 hex。

    JS 模板字符串将数字值直接字符串化；Python ``str()`` 对 int 输出一致。
    """
    pairs = [f"{key}={data[key]}" for key in sorted(data.keys())]
    raw = "&".join(pairs)
    return hmac.new(
        secret.encode("utf-8"), raw.encode("utf-8"), hashlib.md5
    ).hexdigest()


@dataclass(slots=True)
class DcloudConfig:
    space_id: str
    client_secret: str


def _post_json(
    http_client: httpx.Client, body: str, headers: dict[str, str]
) -> dict:
    response = http_client.post(
        BSPCAPP_ENDPOINT, content=body.encode("utf-8"), headers=headers
    )
    return response.json()


def dcloud_upload_file(
    config: DcloudConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    name: str = "unnamed.file",
    clock_ms: Callable[[], int] | None = None,
) -> str:
    if not (config.space_id and config.client_secret):
        raise ValueError("请填写 spaceInfo")

    object_name = name

    # 1) anonymousAuthorize（body 为手拼 JSON，非 JSON.stringify，逐字）
    ts1 = clock_ms() if clock_ms is not None else int(time.time() * 1000)
    auth_data = {
        "method": "serverless.auth.user.anonymousAuthorize",
        "params": "{}",
        "spaceId": config.space_id,
        "timestamp": ts1,
    }
    auth_body = (
        '{"method":"serverless.auth.user.anonymousAuthorize","params":"{}",'
        f'"spaceId":"{config.space_id}","timestamp":{ts1}}}'
    )
    auth_res = _post_json(
        http_client,
        auth_body,
        {"x-serverless-sign": dcloud_sign(auth_data, config.client_secret)},
    )
    token = auth_res["data"]["accessToken"]

    # 2) generateProximalSign（JSON.stringify，params 内嵌手拼 JSON）
    ts2 = clock_ms() if clock_ms is not None else int(time.time() * 1000)
    sign_data = {
        "method": "serverless.file.resource.generateProximalSign",
        "params": f'{{"env":"public","filename":"{object_name}"}}',
        "spaceId": config.space_id,
        "timestamp": ts2,
        "token": token,
    }
    sign_res = _post_json(
        http_client,
        json.dumps(sign_data, separators=(",", ":"), ensure_ascii=False),
        {
            "x-basement-token": token,
            "x-serverless-sign": dcloud_sign(sign_data, config.client_secret),
        },
    )
    data = sign_res["data"]

    # 3) OSS form POST（九字段全集 + 原拼写加密头）
    http_client.post(
        f"https://{data['host']}",
        data={
            "Cache-Control": "max-age=2592000",
            "Content-Disposition": "attachment",
            "OSSAccessKeyId": data["accessKeyId"],
            "Signature": data["signature"],
            "host": data["host"],
            "id": data["id"],
            "key": data["ossPath"],
            "policy": data["policy"],
            "success_action_status": "200",
        },
        files={"file": (object_name, file.content, file.content_type)},
        headers={OSS_ENCRYPTION_HEADER: "AES256"},
    )
    # 逐字 md-cli util.js:134-140：OSS 响应不检查状态码，直接进入 report

    # 4) report（fire-and-forget 语义：md-cli await，此处同样等待但不校验）
    ts3 = clock_ms() if clock_ms is not None else int(time.time() * 1000)
    report_data = {
        "method": "serverless.file.resource.report",
        "params": f'{{"id":"{data["id"]}"}}',
        "spaceId": config.space_id,
        "timestamp": ts3,
        "token": token,
    }
    _post_json(
        http_client,
        json.dumps(report_data, separators=(",", ":"), ensure_ascii=False),
        {
            "x-basement-token": token,
            "x-serverless-sign": dcloud_sign(report_data, config.client_secret),
        },
    )

    return f"https://{data['cdnDomain']}/{data['ossPath']}"
