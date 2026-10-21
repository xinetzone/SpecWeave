"""StateGraph 组装：双节点（chat / tools）+ 条件边循环 + MemorySaver 会话持久化。

这是本 PoC 的核心商业化验证件：
- 显式状态图（StateGraph + 节点/边/条件边）
- 工具调用循环（ReAct 模式：LLM 决定 -> ToolNode 执行 -> 回到 LLM，直到无工具调用）
- checkpointer（MemorySaver）实现 thread_id 级会话隔离与多轮记忆
- 模型无关：任意 ChatModel 均可注入
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from langgraph_poc.tools import get_current_time, safe_calculator

TOOLS = [get_current_time, safe_calculator]

# 工具名导出，供 CLI 与测试引用
TOOL_NAMES = ("get_current_time", "safe_calculator")


class AgentState(TypedDict):
    """图状态：消息列表，add_messages 归约器负责追加与去重（checkpointer 依赖）。"""

    messages: Annotated[list[AnyMessage], add_messages]


def _chat_node(state: AgentState, llm):
    """LLM 节点：绑定工具后调用，产出 AIMessage（可能携带 tool_calls）。"""
    response = llm.bind_tools(TOOLS).invoke(state["messages"])
    return {"messages": [response]}


def _should_continue(state: AgentState) -> str:
    """条件边：最新消息带 tool_calls -> 进入 tools 节点；否则结束。"""
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else "end"


def build_graph(llm, checkpointer=None):
    """组装并编译状态图。

    llm: 任意 ChatModel（DeepSeek / 规则演示模型均可）。
    checkpointer: 不传则用 MemorySaver（内存态，进程结束即失；
                  生产环境应换 SQLite/Postgres checkpointer，见 README）。
    返回编译后的可调用图。
    """
    graph = StateGraph(AgentState)
    graph.add_node("chat", lambda state: _chat_node(state, llm))
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_edge(START, "chat")
    graph.add_conditional_edges("chat", _should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "chat")
    return graph.compile(checkpointer=checkpointer or MemorySaver())
