"""OpenAI 兼容大模型客户端。

只做一件事：把「系统提示 + 用户提示」换回一段文本。刻意不做流式、不做函数
调用、不做重试编排——这些都是**传输层**复杂度，而本应用的降级策略是
「拿不到就走启发式」，重试只会把一次快速降级拖成一次慢速降级。

失败语义统一为 :class:`LLMError`，由 :mod:`info_butler.pipeline` 捕获后降级。
调用方永远不需要区分「网络超时」还是「模型返回了空」。
"""

import json

import httpx

from .config import LLMOverride, Settings
from .http_client import http_client


class LLMError(RuntimeError):
    """大模型调用失败：网络、鉴权、空响应统一归于此。"""


class LLMClient:
    """大模型客户端：同时支持 OpenAI 兼容端点与云端免密钥通道。

    两条通道的**对外契约相同**（``chat`` 返回一段文本），差别在协议：

    - OpenAI 兼容端点：一次性 JSON 响应，带 ``Authorization: Bearer``；
    - 云端通道：只有流式（SSE），鉴权头是 ``x-wb-webapp-access-key``，
      且 publishableKey **不能**当 Bearer 用。

    优先级：请求级 BYOK > 云端通道 > 服务端 OpenAI 兼容配置。
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def _resolve(self, override: LLMOverride | None) -> tuple[str, str, str]:
        """服务端配置与请求级 BYOK 合并：BYOK 有 Key 才整体接管。"""
        settings = self._settings
        if override is not None and override.active:
            base_url = (override.base_url or settings.llm_base_url).rstrip("/")
            model = override.model or settings.llm_model
            return base_url, override.api_key, model
        return settings.llm_base_url, settings.llm_api_key, settings.llm_model

    def available(self, override: LLMOverride | None = None) -> bool:
        """当前凭据下大模型是否可用——决定是否走降级分支。

        BYOK 最优先；没有 BYOK 时，云端免密钥通道也算「可用」——用户不需要
        自己的 API Key 就能拿到模型能力，这是平台托管环境的核心价值。
        """
        if override is not None and override.active:
            return True
        if self._settings.wb_llm_ready:
            return True
        _, api_key, _ = self._resolve(override)
        return bool(api_key)

    def _use_cloud_channel(self, override: LLMOverride | None) -> bool:
        """该次请求是否走云端通道。"""
        if override is not None and override.active:
            return False
        return self._settings.wb_llm_ready

    def probe(self, override: LLMOverride | None = None) -> dict:
        """打一次最小探针，回答「我填的对不对」，返回 ``{ok, model, reason}``。

        刻意不抛异常：填错 Key 是**用户输入错误**，不是服务端故障。若这里抛
        LLMError，HTTP 层就会变成 5xx，而页面真正想展示的是一句可执行的提示。
        所以探针的请求永远是成功的（200），验证结果放在响应体里。

        代价控制：``max_tokens=1``，一次探针只烧一个 token。用 chat 而不是
        ``/models``，是因为只有 chat 才能同时验出「Key 有效」与「模型名存在」——
        后者是 BYOK 场景下最常见的填错项。
        """
        if self._use_cloud_channel(override):
            return self._probe_cloud()

        base_url, api_key, model = self._resolve(override)
        if not api_key:
            return {"ok": False, "model": model, "reason": "还没有填 API Key"}
        if not base_url:
            return {"ok": False, "model": model, "reason": "还没有填 Base URL"}

        payload: dict[str, object] = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            with http_client(f"{base_url}/chat/completions", self._settings.llm_timeout) as client:
                response = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        except httpx.HTTPError as exc:  # pragma: no cover - 由测试用假 client 覆盖
            return {"ok": False, "model": model, "reason": f"连不上这个地址（{type(exc).__name__}）"}

        status = response.status_code
        if status in (401, 403):
            return {"ok": False, "model": model, "reason": f"API Key 无效（端点返回 {status}）"}
        if status == 404:
            return {"ok": False, "model": model, "reason": "地址或模型名不对（端点返回 404）"}
        if status == 429:
            return {"ok": False, "model": model, "reason": "被限流了（429），稍后再试"}
        if status >= 500:
            return {"ok": False, "model": model, "reason": f"模型服务端出错（{status}），暂时不可用"}
        if status >= 400:
            return {"ok": False, "model": model, "reason": f"端点返回 {status}：{response.text[:120]}"}
        return {"ok": True, "model": model, "reason": ""}

    def _cloud_headers(self) -> dict[str, str]:
        """云端通道鉴权头。

    publishableKey 只能放 ``x-wb-webapp-access-key``——它不是 Bearer 令牌，
    当成 ``Authorization: Bearer`` 用会被服务端判为「仅 publishableKey」而拒绝。
    """
        return {
            "x-wb-webapp-access-key": self._settings.wb_publishable_key,
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

    def _probe_cloud(self) -> dict:
        """云端通道探针：最小流式请求，确认链路通不通。"""
        model = self._settings.wb_llm_model
        url = f"{self._settings.wb_cloud_endpoint.rstrip('/')}/.cloud/llm/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "stream": True,
            "max_tokens": 1,
        }
        try:
            with http_client(url, self._settings.llm_timeout) as client:
                with client.stream(
                    "POST", url, json=payload, headers=self._cloud_headers()
                ) as response:
                    if response.status_code >= 400:
                        body = response.read().decode("utf-8", "replace")[:120]
                        return {
                            "ok": False,
                            "model": model,
                            "reason": f"云端通道返回 {response.status_code}：{body}",
                        }
                    for _ in response.iter_lines():
                        pass
        except httpx.HTTPError as exc:  # pragma: no cover - 依赖外部网络
            return {"ok": False, "model": model, "reason": f"连不上云端通道（{type(exc).__name__}）"}
        return {"ok": True, "model": model, "reason": ""}

    def _chat_cloud(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> str:
        """云端通道对话：只有流式，需自行聚合 SSE 分片。

        帧序（官方约定）：首个 role 帧 → content 增量帧 → finish 帧 → ``[DONE]``。
        这里只取 ``delta.content`` 拼接，``reasoning_content`` 属思考过程、
        不并入可见回复。
        """
        model = self._settings.wb_llm_model
        url = f"{self._settings.wb_cloud_endpoint.rstrip('/')}/.cloud/llm/chat/completions"
        payload: dict[str, object] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        parts: list[str] = []
        try:
            with http_client(url, self._settings.llm_timeout) as client:
                with client.stream(
                    "POST", url, json=payload, headers=self._cloud_headers()
                ) as response:
                    if response.status_code >= 400:
                        body = response.read().decode("utf-8", "replace")[:200]
                        raise LLMError(f"云端大模型返回 {response.status_code}：{body}")
                    for line in response.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            frame = json.loads(data)
                        except ValueError:
                            continue
                        error = frame.get("error")
                        if error:
                            message = error.get("message") if isinstance(error, dict) else str(error)
                            raise LLMError(f"云端大模型报错：{message}")
                        choices = frame.get("choices") or []
                        if not choices:
                            continue
                        delta = choices[0].get("delta") or {}
                        content = delta.get("content")
                        if content:
                            parts.append(str(content))
        except httpx.HTTPError as exc:  # pragma: no cover - 依赖外部网络
            raise LLMError(f"云端大模型请求失败：{exc}") from exc

        text = "".join(parts).strip()
        if not text:
            raise LLMError("云端大模型返回空内容")
        return text

    def chat(
        self,
        system: str,
        user: str,
        *,
        override: LLMOverride | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> str:
        """发起一次对话，返回 assistant 的文本内容。

        :raises LLMError: 未配置凭据、网络异常、非 2xx、响应结构异常。
        """
        if self._use_cloud_channel(override):
            return self._chat_cloud(
                system,
                user,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            )

        base_url, api_key, model = self._resolve(override)
        if not api_key:
            raise LLMError("未配置大模型密钥")

        payload: dict[str, object] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            with http_client(url, self._settings.llm_timeout) as client:
                response = client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:  # pragma: no cover - 网络分支依赖外部
            raise LLMError(f"大模型请求失败：{exc}") from exc

        if response.status_code >= 400:
            raise LLMError(f"大模型返回 {response.status_code}：{response.text[:200]}")

        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError("大模型响应不是合法 JSON") from exc

        choices = data.get("choices") or []
        if not choices:
            raise LLMError("大模型响应缺少 choices")
        content = (choices[0].get("message") or {}).get("content")
        if not content:
            raise LLMError("大模型返回空内容")
        return str(content)

    def chat_json(
        self,
        system: str,
        user: str,
        *,
        override: LLMOverride | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> dict | None:
        """要求模型返回 JSON 对象。

        端点不支持 ``response_format`` 时（相当多的兼容层不支持），退化为
        「普通对话 + 从文本里挖出第一个 JSON 对象」；仍失败则返回 ``None``，
        由调用方走启发式。
        """
        raw = self.chat(
            system,
            user,
            override=override,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        parsed = _loads_object(raw)
        if parsed is not None:
            return parsed

        raw = self.chat(
            system + "\n只输出一个 JSON 对象，不要任何解释文字。",
            user,
            override=override,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return _loads_object(raw)


def _loads_object(raw: str) -> dict | None:
    """从模型输出里解析出第一个 JSON 对象，容忍包围的散文与代码围栏。"""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        parsed = json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(text[start : end + 1])
        except ValueError:
            return None
    return parsed if isinstance(parsed, dict) else None
