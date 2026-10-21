"""LangGraph 商业化 PoC：StateGraph 双节点 + MemorySaver 会话持久化 + DeepSeek 接入。

验证 LangGraph 商业化硬需求：显式状态图、工具调用循环、checkpointer 会话持久化、
模型无关性（任意 ChatModel 可接入）。
"""

__version__ = "0.1.0"
