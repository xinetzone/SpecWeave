"""A-01 行动项单元测试：Workspace-first 上下文治理模式。

覆盖 Workspace、ContextAssembler、Tools 三大模块的核心行为：
- 工作区注册与查询（先选工作区）
- 上下文装配公式（Context = System + Workspace + Tools + Memory + History）
- 工具按工作区绑定（不全局暴露）
- 两种加载模式（prefetch / agentic）
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from workspace import Workspace, WorkspaceRegistry
from context import ContextAssembler
from tools import Tool, ToolRegistry, build_default_registry
from memory import MemoryManager


class TestWorkspaceRegistry(unittest.TestCase):
    """工作区注册中心测试。"""

    def setUp(self) -> None:
        self.registry = WorkspaceRegistry()
        self.main = Workspace("main", "Main 调度台", model="strong-model")
        self.file_ws = Workspace("file", "文件编辑工作区", model="cheap-model")
        self.registry.set_main(self.main)
        self.registry.register(self.file_ws)

    def test_register_and_get(self):
        ws = self.registry.get("file")
        self.assertEqual(ws.workspace_id, "file")
        self.assertEqual(ws.name, "文件编辑工作区")

    def test_set_main_and_get_main(self):
        self.assertEqual(self.registry.get_main().workspace_id, "main")

    def test_get_nonexistent_raises(self):
        with self.assertRaises(KeyError):
            self.registry.get("not_exist")

    def test_all_returns_all(self):
        self.assertEqual(len(self.registry.all()), 2)


class TestContextAssembler(unittest.TestCase):
    """上下文装配公式测试。"""

    def setUp(self) -> None:
        self.assembler = ContextAssembler()
        self.assembler.set_global_system_prompt("你是默认助手。")
        self.ws = Workspace("ws1", "测试工作区", workspace_prompt="负责测试。")
        self.memory = MemoryManager()
        self.memory.write_people_note("语言偏好", "中文")
        self.memory.write_core_record("项目", "测试")
        self.ws.memory = self.memory

    def test_assemble_contains_all_parts(self):
        context = self.assembler.assemble(self.ws, memory=self.memory)
        self.assertIn("system_prompt", context)
        self.assertIn("workspace_prompt", context)
        self.assertIn("tools", context)
        self.assertIn("memory", context)
        self.assertIn("history", context)

    def test_system_prompt_default(self):
        context = self.assembler.assemble(self.ws, memory=self.memory)
        self.assertEqual(context["system_prompt"], "你是默认助手。")

    def test_workspace_prompt(self):
        context = self.assembler.assemble(self.ws, memory=self.memory)
        self.assertEqual(context["workspace_prompt"], "负责测试。")

    def test_prefetch_mode_loads_all_memory(self):
        context = self.assembler.assemble(self.ws, memory=self.memory, load_mode="prefetch")
        self.assertIn("people", context["memory"])
        self.assertIn("task", context["memory"])
        self.assertIn("experience", context["memory"])

    def test_agentic_mode_loads_people_first(self):
        context = self.assembler.assemble(self.ws, memory=self.memory, load_mode="agentic")
        self.assertIn("people_notes", context["memory"])

    def test_history_excluded_when_disabled(self):
        self.ws.add_history({"role": "user", "content": "hi"})
        context = self.assembler.assemble(self.ws, memory=self.memory, include_history=False)
        self.assertEqual(context["history"], [])

    def test_to_text_contains_all_sections(self):
        context = self.assembler.assemble(self.ws, memory=self.memory)
        text = self.assembler.to_text(context)
        self.assertIn("System Prompt", text)
        self.assertIn("Workspace Prompt", text)
        self.assertIn("可见工具", text)
        self.assertIn("记忆", text)
        self.assertIn("历史轨迹", text)


class TestToolBoundary(unittest.TestCase):
    """工具按工作区绑定（不全局暴露）测试。"""

    def setUp(self) -> None:
        self.registry = ToolRegistry()
        self.tool_registry = build_default_registry()
        self.ws_file = Workspace("file", "文件工作区")
        self.ws_web = Workspace("web", "网页工作区")

    def test_tool_bound_to_workspace_only(self):
        # 只给 file 工作区绑定 read_file，web 工作区不绑定
        self.tool_registry.bind_to_workspace(self.ws_file, "read_file")
        visible = [t.name for t in self.ws_file.get_visible_tools()]
        self.assertIn("read_file", visible)
        # web 工作区看不到 read_file
        self.assertNotIn("read_file", [t.name for t in self.ws_web.get_visible_tools()])

    def test_tool_not_globally_exposed_by_default(self):
        # 新工作区默认无工具
        empty_ws = Workspace("empty", "空工作区")
        self.assertEqual(empty_ws.get_visible_tools(), [])

    def test_bind_many(self):
        self.tool_registry.bind_many(self.ws_file, ["read_file", "write_file"])
        self.assertEqual(len(self.ws_file.get_visible_tools()), 2)

    def test_get_tool_schemas(self):
        self.tool_registry.bind_to_workspace(self.ws_file, "read_file")
        schemas = self.ws_file.get_tool_schemas()
        self.assertEqual(schemas[0]["name"], "read_file")
        self.assertIn("description", schemas[0])

    def test_bind_unregistered_raises(self):
        with self.assertRaises(KeyError):
            self.tool_registry.bind_to_workspace(self.ws_file, "not_registered")


if __name__ == "__main__":
    unittest.main()