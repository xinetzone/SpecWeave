"""LLM 工厂：DeepSeek 真实模式 + 规则演示模式（无 Key 可跑）。

商业化验证点：LangGraph 是模型无关的——真实模式用官方 langchain-deepseek 包，
演示模式用任意自定义 ChatModel 也能走完整状态图链路。
"""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_deepseek import ChatDeepSeek

_TIME_KEYWORDS = ("时间", "几点", "现在", "日期", "今天几号", "time", "date")


class RuleBasedChatModel(BaseChatModel):
    """无 Key 演示模型：按规则决定是否调用工具（非真实 LLM，仅验证状态图全链路）。

    行为：
    - 用户消息含时间类关键词 -> 返回 tool_call(get_current_time)
    - 否则 -> 直接文本回复（演示模式标识）
    """

    model: str = "rule-based-demo"

    @property
    def _llm_type(self) -> str:
        return "rule-based-demo"

    def bind_tools(
        self,
        tools,
        *,
        tool_choice: str | None = None,
        **kwargs,
    ):
        """规则模型自行决定 tool_calls，绑定工具为无操作（保持接口与真实模型一致）。"""
        del tools, tool_choice, kwargs
        return self

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs,
    ) -> ChatResult:
        del stop, run_manager, kwargs
        last = messages[-1]
        content = str(getattr(last, "content", ""))
        if any(keyword in content for keyword in _TIME_KEYWORDS):
            message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_current_time",
                        "args": {},
                        "id": "demo-tool-call-1",
                        "type": "tool_call",
                    }
                ],
            )
        else:
            snippet = content.strip().replace("\n", " ")[:24]
            message = AIMessage(content=f"（演示模式，未配置 DEEPSEEK_API_KEY）已收到：{snippet}…")
        return ChatResult(generations=[ChatGeneration(message=message)])


def build_deepseek_llm(api_key: str, model: str = "deepseek-chat") -> ChatDeepSeek:
    """构建 DeepSeek 真实 LLM（官方 langchain-deepseek 包，默认 api.deepseek.com）。"""
    return ChatDeepSeek(model=model, api_key=api_key)


def build_llm(api_key: str | None = None, force_demo: bool = False):
    """按环境选择模型：有 DEEPSEEK_API_KEY 且未强制演示 -> DeepSeek；否则规则演示模型。

    返回 (llm, mode_name)，mode_name 为 "deepseek" 或 "demo"。
    """
    if not force_demo and api_key:
        return build_deepseek_llm(api_key), "deepseek"
    return RuleBasedChatModel(), "demo"
