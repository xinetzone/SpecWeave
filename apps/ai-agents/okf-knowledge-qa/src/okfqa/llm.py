"""大模型调用封装：OpenAI 兼容协议 /chat/completions。

刻意不引入任何厂商 SDK，直接用 httpx 打兼容端点，
从而一套环境变量同时适配 OpenAI、DeepSeek、通义、Moonshot 等一切 OpenAI 兼容服务。

失败一律抛 LLMError，由调用方决定降级策略——
遵守「显式报错优于静默降级」，不把大模型故障伪装成"知识库里没有答案"。
"""

import httpx

from .config import llm_api_key, llm_base_url, llm_model, llm_timeout


class LLMError(RuntimeError):
    """大模型调用失败（未配置凭据、超时、非 2xx、响应格式异常）。"""


def _endpoint() -> str:
    return llm_base_url().rstrip("/") + "/chat/completions"


async def chat(
    system: str,
    user: str,
    temperature: float = 0.2,
    max_tokens: int = 1200,
) -> str:
    """发起一次对话补全，返回助手文本。"""
    key = llm_api_key()
    if not key:
        raise LLMError("未配置 LLM_API_KEY，无法调用大模型")

    payload = {
        "model": llm_model(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=llm_timeout()) as client:
            resp = await client.post(_endpoint(), json=payload, headers=headers)
    except httpx.TimeoutException as exc:
        raise LLMError(f"大模型请求超时（{llm_timeout():.0f}s）") from exc
    except httpx.HTTPError as exc:
        raise LLMError(f"大模型请求失败：{exc}") from exc

    if resp.status_code >= 400:
        raise LLMError(f"大模型返回 HTTP {resp.status_code}：{resp.text[:300]}")

    try:
        data = resp.json()
        return str(data["choices"][0]["message"]["content"]).strip()
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"大模型响应格式异常：{resp.text[:300]}") from exc
