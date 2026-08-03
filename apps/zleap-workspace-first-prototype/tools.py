"""Tools 模块：工具注册与工作区绑定机制。

对应 Zleap-Agent 设计中的 Tools 概念：
- 工具不是越多越好，关键是当前可见
- 工具与 Workspace 绑定，不全局暴露
- 模型进入哪个工作区就只看当前工作区的工具
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from workspace import Workspace


class Tool:
    """一个可调用的工具，包含名称、描述、schema 与实现函数。"""

    def __init__(self, name: str, description: str, func: Callable[..., Any]) -> None:
        self.name = name
        self.description = description
        self.func = func
        self.schema: Dict[str, str] = {
            "name": name,
            "description": description,
        }

    def execute(self, **kwargs: Any) -> Any:
        """执行工具函数。"""
        return self.func(**kwargs)

    def __repr__(self) -> str:
        return f"Tool(name={self.name}, desc={self.description})"


class ToolRegistry:
    """工具注册中心。工具按工作区绑定，不全局暴露。"""

    def __init__(self) -> None:
        # 全局工具池：tool_name -> Tool
        self._global_pool: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """注册一个工具到全局池。"""
        self._global_pool[tool.name] = tool

    def bind_to_workspace(self, workspace: Workspace, tool_name: str) -> None:
        """将工具绑定到指定工作区（工具不全局暴露）。"""
        if tool_name not in self._global_pool:
            raise KeyError(f"工具 {tool_name!r} 未注册")
        workspace.bind_tool(self._global_pool[tool_name])

    def bind_many(self, workspace: Workspace, tool_names: List[str]) -> None:
        """批量绑定工具到工作区。"""
        for name in tool_names:
            self.bind_to_workspace(workspace, name)

    def get_global(self, tool_name: str) -> Tool:
        """从全局池获取工具（不绑定到工作区）。"""
        if tool_name not in self._global_pool:
            raise KeyError(f"工具 {tool_name!r} 未注册")
        return self._global_pool[tool_name]

    def visible_to(self, workspace: Workspace) -> List[Tool]:
        """获取指定工作区可见的全部工具。"""
        return workspace.get_visible_tools()


# 内置工具示例
def read_file(path: str) -> str:
    """读取本地文件内容（演示用）。"""
    return f"[file:{path}] 读取成功"


def search_web(query: str) -> str:
    """搜索网页（演示用）。"""
    return f"[web-search] 查询结果: {query}"


def write_file(path: str, content: str) -> str:
    """写入本地文件（演示用）。"""
    return f"[file:{path}] 写入成功"


def run_sql(sql: str) -> str:
    """执行 SQL 查询（演示用，数据边界内）。"""
    return f"[sql] 执行结果: {sql}"


def process_receipt(image_path: str) -> str:
    """处理票据（敏感数据，走本地模型）。"""
    return f"[receipt:{image_path}] 本地处理完成"


def build_default_registry() -> ToolRegistry:
    """构建默认工具注册中心，注册常用工具。"""
    registry = ToolRegistry()
    registry.register_tool(Tool("read_file", "读取本地文件", read_file))
    registry.register_tool(Tool("write_file", "写入本地文件", write_file))
    registry.register_tool(Tool("search_web", "搜索网页", search_web))
    registry.register_tool(Tool("run_sql", "执行 SQL 查询", run_sql))
    registry.register_tool(Tool("process_receipt", "处理票据（本地）", process_receipt))
    return registry