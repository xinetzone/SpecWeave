"""Context 模块：上下文装配过程。

对应 Zleap-Agent 设计中的 Context 概念：
- 不要问能塞多少，先问这一轮该看什么
- 核心公式：Context = System Prompt + Workspace Prompt + Tools + Memory + History
- 两种加载方式：Prefetch（预取，短/准/可控）+ Agentic（按需读取）
"""

from __future__ import annotations

from typing import Any, Dict, List

from workspace import Workspace


class ContextAssembler:
    """按公式装配上下文。

    公式：Context = System Prompt + Workspace Prompt + Tools + Memory + History
    """

    def __init__(self) -> None:
        self._global_system_prompt: str = "你是一个遵循 Workspace-first 的智能体助手。"

    def set_global_system_prompt(self, prompt: str) -> None:
        """设置全局 System Prompt。"""
        self._global_system_prompt = prompt

    def assemble(
        self,
        workspace: Workspace,
        memory: Any = None,
        include_history: bool = True,
        load_mode: str = "prefetch",
    ) -> Dict[str, Any]:
        """装配指定工作区的完整上下文。

        Args:
            workspace: 目标工作区
            memory: 记忆管理器（可选，默认为工作区已注入的记忆）
            include_history: 是否包含历史轨迹
            load_mode: 'prefetch'（预取）或 'agentic'（按需读取）

        Returns:
            装配后的上下文字典，各组成部分独立存放。
        """
        mem = memory or workspace.memory
        parts: Dict[str, Any] = {}

        # 1. System Prompt：全局行为风格
        parts["system_prompt"] = workspace.system_prompt or self._global_system_prompt

        # 2. Workspace Prompt：当前工作区说明
        parts["workspace_prompt"] = workspace.workspace_prompt

        # 3. Tools：只暴露当前工作区的工具
        parts["tools"] = workspace.get_tool_schemas()

        # 4. Memory：只取相关记忆
        parts["memory"] = self._load_memory(mem, load_mode)

        # 5. History：保留必要近期轨迹
        parts["history"] = workspace.history[-5:] if include_history else []

        return parts

    def _load_memory(self, memory: Any, mode: str) -> Dict[str, Any]:
        """按加载模式读取记忆。

        - prefetch：一次取全部分区（短、准、可控）
        - agentic：按需读取（这里演示先取 people 分区，其余按需）
        """
        if memory is None:
            return {}
        if mode == "agentic":
            # Agentic 模式：先取 A 线 people notes（用户偏好），其余按需
            return {
                "people_notes": memory.read_partition("people"),
                "note": "按需读取模式：其余分区按需加载",
            }
        # prefetch 模式：一次取全部分区
        return memory.all_partitions()

    def to_text(self, context: Dict[str, Any]) -> str:
        """将装配好的上下文转换为可发送给模型的文本。"""
        lines: List[str] = []
        lines.append(f"【System Prompt】\n{context['system_prompt']}")
        lines.append(f"\n【Workspace Prompt】\n{context['workspace_prompt']}")
        lines.append(f"\n【可见工具】\n{context['tools']}")
        lines.append(f"\n【记忆】\n{context['memory']}")
        lines.append(f"\n【历史轨迹】\n{context['history']}")
        return "\n".join(lines)