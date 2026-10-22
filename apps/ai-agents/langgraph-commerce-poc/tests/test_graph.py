"""StateGraph 全链路单元测试：工具循环、直答路径、会话持久化、线程隔离、工具安全。

全部测试在无 DEEPSEEK_API_KEY 条件下运行（规则演示模型），不产生任何外部 API 调用。
"""

import ast
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from langgraph_poc.graph import TOOL_NAMES, build_graph
from langgraph_poc.llm import RuleBasedChatModel, build_llm
from langgraph_poc.tools import get_current_time, safe_calculator

SRC_DIR = Path(__file__).resolve().parents[1] / "src"


def _graph():
    return build_graph(RuleBasedChatModel())


def _invoke(graph, text: str, thread_id: str):
    return graph.invoke(
        {"messages": [HumanMessage(content=text)]},
        config={"configurable": {"thread_id": thread_id}},
    )


class TestToolLoop:
    def test_time_question_triggers_tool_cycle(self):
        """问时间 -> LLM 决定调工具 -> ToolNode 执行 -> LLM 汇总 -> 结束。"""
        state = _invoke(_graph(), "现在几点", "th-loop")
        messages = state["messages"]
        assert any(isinstance(m, ToolMessage) for m in messages), "应执行工具节点"
        assert messages[-1].content.startswith("（演示模式"), "最终应有 LLM 文本汇总"
        assert messages[-1].tool_calls == [], "最终消息不应再请求工具"

    def test_plain_question_answers_directly(self):
        """普通问题 -> 无工具调用 -> 直答结束。"""
        state = _invoke(_graph(), "你好，介绍一下你自己", "th-direct")
        messages = state["messages"]
        assert isinstance(messages[-1], AIMessage)
        assert messages[-1].tool_calls == []
        assert len(messages) == 2  # Human + AI，无工具环节

    def test_graph_metadata(self):
        """图结构：双节点 + 条件边存在。"""
        graph = _graph()
        assert set(graph.get_graph().nodes) >= {"chat", "tools"}
        assert len(TOOL_NAMES) == 2


class TestCheckpointer:
    def test_memory_persistence_same_thread(self):
        """同一 thread_id 多轮：历史消息持续累积（checkpointer 生效）。"""
        graph = _graph()
        first = _invoke(graph, "你好", "th-persist")
        second = _invoke(graph, "再聊一句", "th-persist")
        assert len(second["messages"]) == len(first["messages"]) + 2, (
            "第二轮应追加 HumanMessage + AIMessage，历史不得丢失"
        )

    def test_thread_isolation(self):
        """不同 thread_id 完全隔离，互不可见。"""
        graph = _graph()
        state_a = _invoke(graph, "甲说", "th-a")
        state_b = _invoke(graph, "乙说", "th-b")
        assert all(m.content != "甲说" for m in state_b["messages"])
        assert len(state_b["messages"]) == 2
        assert len(state_a["messages"]) == 2


class TestTools:
    def test_get_current_time_shape(self):
        value = get_current_time()
        assert len(value) == 19 and value[4] == "-" and value[13] == ":"

    @pytest.mark.parametrize(
        ("expr", "expected"),
        [
            ("2 * (3 + 4)", "14"),
            ("10 / 4", "2.5"),
            ("2 ** 10", "1024"),
            ("-5 + 3", "-2"),
            ("17 % 5", "2"),
            ("7 // 2", "3"),
        ],
    )
    def test_safe_calculator_ok(self, expr, expected):
        assert safe_calculator(expr) == expected

    @pytest.mark.parametrize(
        "expr",
        [
            "__import__('os').system('echo pwned')",  # 任意代码执行
            "().__class__",  # 属性访问
            "[1,2,3]",  # 字面量容器
            "open('/etc/passwd')",  # 函数调用
            "9**9**9",  # 幂 DoS
            "1 + 'x'",  # 类型错误
            "",  # 空表达式
        ],
    )
    def test_safe_calculator_reject(self, expr):
        result = safe_calculator(expr)
        assert result.startswith("计算失败"), f"危险表达式应被拒绝: {expr!r}"


class TestLLMFactory:
    def test_demo_mode_without_key(self):
        llm, mode = build_llm(api_key=None)
        assert mode == "demo"

    def test_deepseek_mode_with_key(self):
        llm, mode = build_llm(api_key="sk-test")
        assert mode == "deepseek"


class TestNoFutureAnnotations:
    """项目红线守护：src 下禁止 from __future__ import annotations（PEP 563 样板）。"""

    def test_no_future_imports(self):
        offenders = []
        for py in SRC_DIR.rglob("*.py"):
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
            for node in tree.body:
                if (
                    isinstance(node, ast.ImportFrom)
                    and node.module == "__future__"
                ):
                    offenders.append(str(py))
        assert offenders == [], f"禁止 __future__ 导入: {offenders}"
