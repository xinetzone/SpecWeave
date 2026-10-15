"""自定义图床入口（upstream: providers.ts:687-733 formCustomUpload）。

上游把用户配置的 **JavaScript 源码** 用 ``new Function`` 在浏览器里执行
（CUSTOM_ARG 注入 file/util/okCb/errCb）。Python 复刻不内嵌 JS 引擎：
自定义上传器改为显式注册的 Python 可调用对象（entry point），获得同等 util
能力（日期命名、四家签名原语、S3 presign），但杜绝任意 JS 执行面。

注册方式::

    from doocs_md_py.uploaders.form_custom import register_form_custom

    @register_form_custom("my-host")
    def _my_host(file, content_b64, util, config):
        token = util["qiniu_token"]("AK", "SK", {"scope": "b", "deadline": ...})
        ...
        return url

随后 ``file_upload("formCustom", file, config=FormCustomConfig("my-host", raw))``
即调用注册项；未知名抛 KeyError（等价上游脚本运行时错误）。
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from .base import UploadFile, get_date_filename, get_dir
from .cloudinary import cloudinary_signature
from .dcloud import dcloud_sign
from .qiniu import qiniu_upload_token
from .s3_presign import build_presigned_put_url
from .upyun import upyun_signature

FormCustomUploader = Callable[
    [UploadFile, str, dict[str, Any], "FormCustomConfig", httpx.Client], str
]

_REGISTRY: dict[str, FormCustomUploader] = {}


def register_form_custom(name: str) -> Callable[[FormCustomUploader], FormCustomUploader]:
    """装饰器：注册命名自定义上传器（等价 formCustomConfig 选择槽位）。"""

    def deco(fn: FormCustomUploader) -> FormCustomUploader:
        _REGISTRY[name] = fn
        return fn

    return deco


@dataclass(slots=True)
class FormCustomConfig:
    """``name`` 为注册名；``raw`` 承载原 JS 配置（仅留档，Python 不解释执行）。"""

    name: str
    raw: str = ""


def build_util_bundle() -> dict[str, Any]:
    """等价上游 CUSTOM_ARG.util（仅保留可安全纯函数化的能力）。"""
    return {
        "getDir": get_dir,
        "getDateFilename": get_date_filename,
        "qiniu_token": qiniu_upload_token,
        "upyun_signature": upyun_signature,
        "cloudinary_signature": cloudinary_signature,
        "dcloud_sign": dcloud_sign,
        "s3_presigned_put": build_presigned_put_url,
    }


def form_custom_upload(
    config: FormCustomConfig,
    file: UploadFile,
    http_client: httpx.Client,
    *,
    content_b64: str | None = None,
) -> str:
    import base64

    uploader = _REGISTRY.get(config.name)
    if uploader is None:
        raise KeyError(f"form custom uploader not registered: {config.name!r}")
    encoded = content_b64 or base64.b64encode(file.content).decode("ascii")
    return uploader(file, encoded, build_util_bundle(), config, http_client)
