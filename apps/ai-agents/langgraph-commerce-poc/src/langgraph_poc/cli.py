"""对话 CLI：演示 StateGraph + 会话持久化。

用法：
    langgraph-poc                 # 自动模式：有 DEEPSEEK_API_KEY 用 DeepSeek，否则演示模式
    langgraph-poc --model demo    # 强制演示模式（无 Key 也可跑）
    langgraph-poc --model deepseek --thread order-42   # 指定会话 ID

会话内命令：
    /quit              退出
    /thread <id>       切换/新建会话（thread_id 隔离验证）
    /reset             清空当前会话记忆（新 thread_id）
"""

import argparse
import os
import sys
import uuid

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langgraph_poc.graph import build_graph
from langgraph_poc.llm import build_llm


def _print_reply(state) -> None:
    messages = state["messages"]
    last = messages[-1]
    if isinstance(last, AIMessage) and last.content:
        print(f"\n[AI] {last.content}\n")
    elif isinstance(last, ToolMessage):
        print(f"\n[AI] （工具结果）{last.content}\n")
    else:
        print(f"\n[AI] （{type(last).__name__}，无文本回复）\n")


def _run_session(graph, thread_id: str) -> None:
    print(f"当前会话: {thread_id}（输入 /quit 退出，/thread <id> 切换，/reset 清空）")
    while True:
        try:
            user_input = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not user_input:
            continue
        if user_input == "/quit":
            print("再见。")
            break
        if user_input == "/reset":
            thread_id = f"th-{uuid.uuid4().hex[:8]}"
            print(f"已清空并新建会话: {thread_id}")
            continue
        if user_input.startswith("/thread"):
            parts = user_input.split(maxsplit=1)
            if len(parts) < 2:
                print("用法: /thread <会话ID>")
                continue
            thread_id = parts[1].strip()
            print(f"已切换会话: {thread_id}")
            continue
        state = graph.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        _print_reply(state)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LangGraph 商业化 PoC 对话 CLI")
    parser.add_argument(
        "--model",
        choices=("auto", "deepseek", "demo"),
        default="auto",
        help="auto=有 Key 用 DeepSeek 否则演示；deepseek=强制真实调用；demo=强制演示模式",
    )
    parser.add_argument("--thread", default=None, help="会话 ID（默认随机生成）")
    args = parser.parse_args(argv)

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if args.model == "deepseek" and not api_key:
        print("错误: --model deepseek 需要设置环境变量 DEEPSEEK_API_KEY", file=sys.stderr)
        return 2

    llm, mode = build_llm(api_key=api_key, force_demo=(args.model == "demo"))
    graph = build_graph(llm)
    print(f"模型模式: {mode}（{'DeepSeek 真实调用' if mode == 'deepseek' else '规则演示模型，未调用外部 API'}）")
    print("StateGraph: chat -> (tools <-> chat) -> end | checkpointer: MemorySaver")
    _run_session(graph, args.thread or f"th-{uuid.uuid4().hex[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
