"""Workspace 模块：Workspace-first 架构的核心工作区单元。

对应 Zleap-Agent 设计中的 Workspace 概念：
- 每个工作区是一个独立的运行环境单元，包含独立的 prompt/tools/memory/history/model/permission
- Main Workspace 是调度台，不直接承担所有上下文
- 先选工作区，再组装上下文
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class Workspace:
    """工作区单元，承载独立的上下文、工具、记忆、模型与权限。

    Attributes:
        workspace_id: 工作区唯一标识
        name: 工作区名称
        system_prompt: 全局系统提示词（保持行为风格）
        workspace_prompt: 当前工作区的说明提示词
        model: 绑定的模型（支持多模型协作）
        permission: 权限标识（用于边界检查）
        private: 是否私有（数据不出内网）
    """

    def __init__(
        self,
        workspace_id: str,
        name: str,
        workspace_prompt: str = "",
        system_prompt: str = "",
        model: str = "default",
        permission: str = "",
        private: bool = False,
    ) -> None:
        self.workspace_id = workspace_id
        self.name = name
        self.workspace_prompt = workspace_prompt
        self.system_prompt = system_prompt
        self.model = model
        self.permission = permission
        self.private = private
        # 工具注册表：tool_name -> Tool 对象
        self.tools: Dict[str, Any] = {}
        # 记忆分区引用：由 MemoryManager 注入
        self.memory: Optional[Any] = None
        # 历史记录：最近若干轮轨迹
        self.history: List[Dict[str, Any]] = []

    def bind_tool(self, tool: Any) -> None:
        """绑定工具到当前工作区（工具不全局暴露）。"""
        self.tools[tool.name] = tool

    def get_visible_tools(self) -> List[Any]:
        """获取当前工作区可见的工具列表。"""
        return list(self.tools.values())

    def get_tool_schemas(self) -> List[Dict[str, str]]:
        """获取当前工作区可见的工具 schema（计入上下文）。"""
        return [tool.schema for tool in self.tools.values()]

    def add_history(self, entry: Dict[str, Any]) -> None:
        """追加一条历史轨迹记录。"""
        self.history.append(entry)

    def __repr__(self) -> str:
        return (
            f"Workspace(id={self.workspace_id}, name={self.name}, "
            f"model={self.model}, tools={len(self.tools)}, private={self.private})"
        )


class WorkspaceRegistry:
    """工作区注册中心，负责创建、注册与查询工作区。"""

    def __init__(self) -> None:
        self._workspaces: Dict[str, Workspace] = {}
        self._main_workspace_id: Optional[str] = None

    def register(self, workspace: Workspace) -> Workspace:
        """注册一个工作区。"""
        self._workspaces[workspace.workspace_id] = workspace
        return workspace

    def set_main(self, workspace: Workspace) -> None:
        """设置 Main 调度台工作区。"""
        self._main_workspace_id = workspace.workspace_id
        self.register(workspace)

    def get(self, workspace_id: str) -> Workspace:
        """按 ID 查询工作区。"""
        if workspace_id not in self._workspaces:
            raise KeyError(f"Workspace {workspace_id!r} 不存在")
        return self._workspaces[workspace_id]

    def get_main(self) -> Workspace:
        """获取 Main 调度台工作区。"""
        if self._main_workspace_id is None:
            raise RuntimeError("尚未设置 Main 工作区")
        return self._workspaces[self._main_workspace_id]

    def all(self) -> List[Workspace]:
        """返回全部工作区。"""
        return list(self._workspaces.values())

    def __len__(self) -> int:
        return len(self._workspaces)