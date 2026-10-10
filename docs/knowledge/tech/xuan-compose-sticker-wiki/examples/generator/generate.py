# SPDX-License-Identifier: GPL-2.0-only
"""手帐贴纸风格照片生成 —— 生图工作容器（教学示例）。

同一个脚本提供两种形态，由 xuan-compose 编排：

* 长驻 API：``uvicorn generate:app``（compose 的 generator 服务默认命令）；
* 一次性 CLI：``python generate.py card <照片> [关键词...]`` /
  ``python generate.py stickers``（用 ``xuan-compose run --rm --entrypoint ...`` 触发）。

供应商端点全部来自环境变量，编排文件不焊死任何供应商细节：

* ``ARK_BASE_URL``  默认 https://ark.cn-beijing.volces.com/api/v3
* ``ARK_MODEL``     默认 doubao-seedream-5-0-pro-260628
* ``OUTPUT_SIZE``   默认 1248x832（3:2，1K 档）
* 密钥：优先读文件 secret ``/run/secrets/ark_key``，其次环境变量 ``ARK_API_KEY``。

请求体字段（model/prompt/size/output_format/response_format/image/watermark）
依据火山方舟 Seedream 5.0 pro 官方「Image generation API」文档：
POST {ARK_BASE_URL}/images/generations，Authorization: Bearer <ARK_API_KEY>。

注意：``image`` 字段官方示例传可访问 URL。本脚本对容器内本地文件改用 data URI
上传（多数 OpenAI 兼容端点支持）；若你的端点仅接受 URL，请把输入图放到对象存储/
画廊服务后改传 image_url——这是唯一需要按供应商适配的点。
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

WORK = Path(os.environ.get("WORK_DIR", "/work"))
PHOTOS = WORK / "photos"
OUT = WORK / "out"
PROMPTS = WORK / "prompts"


# --------------------------------------------------------------------------- #
# 配置与密钥
# --------------------------------------------------------------------------- #
def read_api_key() -> str:
    """文件 secret（xuan-compose 挂到 /run/secrets/<name>）优先，环境变量兜底。"""
    secret_file = Path("/run/secrets/ark_key")
    if secret_file.is_file():
        key = secret_file.read_text(encoding="utf-8").strip()
        if key:
            return key
    key = os.environ.get("ARK_API_KEY", "").strip()
    if key:
        return key
    raise RuntimeError(
        "未找到 API Key：请提供文件 secret /run/secrets/ark_key 或环境变量 ARK_API_KEY"
    )


def config() -> dict[str, str]:
    return {
        "base_url": os.environ.get(
            "ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
        ).rstrip("/"),
        "model": os.environ.get("ARK_MODEL", "doubao-seedream-5-0-pro-260628"),
        "size": os.environ.get("OUTPUT_SIZE", "1248x832"),
    }


# --------------------------------------------------------------------------- #
# 参考图：URL 直传；本地文件转 data URI（按供应商支持情况，文件头注释已说明）
# --------------------------------------------------------------------------- #
def _sniff_mime(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


def to_image_ref(image_url: str | None, local_path: str | Path | None) -> str:
    if image_url:
        return image_url
    if local_path is None:
        raise ValueError("需要 image_url 或本地参考图路径二选一")
    p = Path(local_path)
    data = p.read_bytes()
    mime = _sniff_mime(data)
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


# --------------------------------------------------------------------------- #
# Seedream 5.0 pro 调用
# --------------------------------------------------------------------------- #
def seedream_generate(prompt: str, image_ref: str | None = None) -> bytes:
    """调用 images/generations，返回 PNG 字节。"""
    cfg = config()
    body: dict[str, Any] = {
        "model": cfg["model"],
        "prompt": prompt,
        "size": cfg["size"],
        "output_format": "png",
        "response_format": "url",
        "watermark": False,
    }
    if image_ref:
        body["image"] = image_ref  # 图生图（I2I）：记忆卡与贴纸稿都以原图/卡为参考

    resp = requests.post(
        f"{cfg['base_url']}/images/generations",
        headers={
            "Authorization": f"Bearer {read_api_key()}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=300,
    )
    resp.raise_for_status()
    item = resp.json()["data"][0]
    if item.get("url"):
        img = requests.get(item["url"], timeout=120)
        img.raise_for_status()
        return img.content
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    raise RuntimeError(f"响应中既无 url 也无 b64_json：{json.dumps(item)[:200]}")


# --------------------------------------------------------------------------- #
# 提示词装配（方法论见 Wiki 06 章；模板文件即 travel-memory-card-duo 规范的落地）
# --------------------------------------------------------------------------- #
def load_prompt(name: str, mapping: dict[str, str]) -> str:
    text = (PROMPTS / name).read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace(f"{{{k}}}", v)
    return text


def make_card(photo_ref: str, keywords: list[str]) -> bytes:
    kw = (keywords + ["", "", ""])[:3]
    prompt = load_prompt(
        "card.txt",
        {"KW1": kw[0], "KW2": kw[1], "KW3": kw[2]},
    )
    return seedream_generate(prompt, image_ref=photo_ref)


def make_stickers(card_ref: str) -> bytes:
    chroma = os.environ.get("CHROMA_KEY", "#00ff00")
    prompt = load_prompt("stickers.txt", {"CHROMA_KEY": chroma})
    return seedream_generate(prompt, image_ref=card_ref)


def pipeline(photo_path: str | Path, keywords: list[str]) -> None:
    """完整双产物流水线：照片 → 记忆卡 → 色幕贴纸稿（去底交给 keychroma 任务）。"""
    OUT.mkdir(parents=True, exist_ok=True)
    photo_ref = to_image_ref(None, photo_path)

    card_bytes = make_card(photo_ref, keywords)
    card_path = OUT / "card.png"
    card_path.write_bytes(card_bytes)
    print(f"[generator] 记忆卡已写出: {card_path}")

    card_ref = to_image_ref(None, card_path)
    stickers_bytes = make_stickers(card_ref)
    sheet_path = OUT / "stickers-chroma.png"
    sheet_path.write_bytes(stickers_bytes)
    print(f"[generator] 色幕贴纸稿已写出: {sheet_path}（下一步：keychroma 去底）")


# --------------------------------------------------------------------------- #
# 长驻 API 形态
# --------------------------------------------------------------------------- #
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    app = FastAPI(title="sticker-studio generator")

    class GenerateRequest(BaseModel):
        mode: str = "pipeline"  # card | stickers | pipeline
        photo_path: str | None = None       # 容器内路径，如 /work/photos/in.jpg
        image_url: str | None = None
        keywords: list[str] = []

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/generate")
    def generate(req: GenerateRequest) -> dict[str, str]:
        try:
            photo_ref = to_image_ref(req.image_url, req.photo_path)
            if req.mode == "card":
                (OUT / "card.png").write_bytes(make_card(photo_ref, req.keywords))
            elif req.mode == "stickers":
                card_ref = to_image_ref(None, OUT / "card.png")
                (OUT / "stickers-chroma.png").write_bytes(make_stickers(card_ref))
            else:
                if req.photo_path:
                    pipeline(req.photo_path, req.keywords)
                else:
                    raise ValueError("pipeline 模式需要 photo_path")
            return {"status": "ok", "out_dir": str(OUT)}
        except Exception as exc:  # noqa: BLE001 - 教学示例把错误回传调用方
            raise HTTPException(status_code=500, detail=str(exc)) from exc

except ImportError:  # 允许在只跑 CLI 的精简环境里缺 fastapi
    app = None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
# 一次性 CLI 形态
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="手帐贴纸双产物生图")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_card = sub.add_parser("card", help="照片 → 3:2 记忆卡")
    p_card.add_argument("photo")
    p_card.add_argument("keywords", nargs="*", help="恰好三个英文关键词短语")
    p_sheet = sub.add_parser("stickers", help="记忆卡 → 色幕贴纸稿")
    p_sheet.add_argument("--card", default=str(OUT / "card.png"))
    p_all = sub.add_parser("pipeline", help="一次生成两张图")
    p_all.add_argument("photo")
    p_all.add_argument("keywords", nargs="*")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    if args.cmd == "card":
        ref = to_image_ref(None, args.photo)
        (OUT / "card.png").write_bytes(make_card(ref, args.keywords))
    elif args.cmd == "stickers":
        ref = to_image_ref(None, args.card)
        (OUT / "stickers-chroma.png").write_bytes(make_stickers(ref))
    else:
        pipeline(args.photo, args.keywords)
    return 0


if __name__ == "__main__":
    sys.exit(main())
