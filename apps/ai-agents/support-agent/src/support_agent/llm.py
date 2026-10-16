"""大模型接入：OpenAI 兼容 Chat Completions 协议（DeepSeek / 通义 / 混元 / OpenAI / Moonshot）。"""

import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from .config import Config
from .http_client import HttpError, request_json

_JSON_BLOCK = re.compile(r"\{.*\}", re.S)


class LLMError(RuntimeError):
    """大模型调用失败。"""


def endpoint(base_url: str) -> str:
    base = (base_url or "").rstrip("/")
    if not base:
        raise LLMError("未配置 LLM_BASE_URL")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def chat(
    cfg: Config,
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.4,
    max_tokens: int = 600,
    timeout: Optional[float] = None,
) -> Tuple[str, int]:
    """调用大模型，返回 (回复文本, 耗时毫秒)。"""
    if not cfg.llm_ready:
        raise LLMError("未配置 LLM_API_KEY")

    payload: Dict[str, Any] = {
        "model": cfg.llm_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {cfg.llm_api_key}",
        "Accept": "application/json",
    }
    started = time.time()
    try:
        data = request_json(
            "POST",
            endpoint(cfg.llm_base_url),
            headers=headers,
            payload=payload,
            timeout=timeout or cfg.request_timeout,
            retries=1,
        )
    except HttpError as exc:
        raise LLMError(f"大模型调用失败：{exc}") from exc
    latency_ms = int((time.time() - started) * 1000)

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"大模型响应格式异常：{str(data)[:200]}") from exc
    return (content or "").strip(), latency_ms


def extract_json(text: str) -> Dict[str, Any]:
    """从可能带噪声的文本中抽取第一个 JSON 对象。"""
    raw = (text or "").strip()
    candidates = [raw]
    match = _JSON_BLOCK.search(raw)
    if match:
        candidates.append(match.group(0))
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S)
    if fenced:
        candidates.append(fenced.group(1))
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    raise LLMError(f"无法从响应解析 JSON：{raw[:200]}")


__all__ = ["LLMError", "chat", "extract_json", "endpoint"]
