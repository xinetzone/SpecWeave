"""MCP Tool定义导出器。

为每个可调用接口生成MCP (Model Context Protocol) Tool定义。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument, Interface, Parameter
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import map_json_schema_type, sanitize_identifier


class MCPGenerator(BaseGenerator):
    """MCP Tool定义生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        tools = self._build_tools(doc)
        content = json.dumps(tools, ensure_ascii=False, indent=2)

        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "mcp_tools")
        ).replace("-", "_")
        file_path = output_dir / f"{module_name}_mcp_tools.json"
        self._write_file(file_path, content)
        return [file_path]

    def _build_tools(self, doc: MDIDocument) -> list[dict[str, Any]]:
        """构建MCP tools数组。"""
        tools: list[dict[str, Any]] = []

        if doc.interfaces:
            for iface in doc.interfaces:
                tool = self._interface_to_tool(iface)
                tools.append(tool)
        else:
            section_tools = self._build_tools_from_sections(doc)
            tools.extend(section_tools)

        return tools

    def _interface_to_tool(self, iface: Interface) -> dict[str, Any]:
        """将Interface转换为MCP Tool定义。"""
        properties: dict[str, Any] = {}
        required: list[str] = []

        all_params = list(iface.parameters)
        if iface.request_body:
            all_params.append(iface.request_body)

        for param in all_params:
            prop_schema = map_json_schema_type(param.type)
            if param.description:
                prop_schema["description"] = param.description
            if param.default is not None:
                prop_schema["default"] = param.default
            properties[param.name] = prop_schema
            if param.required:
                required.append(param.name)

        input_schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }
        if required:
            input_schema["required"] = required

        tool_name = sanitize_identifier(iface.name).replace("-", "_")
        description = iface.description or iface.summary or iface.name
        if iface.method and iface.path:
            description = f"[{iface.method.upper()} {iface.path}] {description}"

        return {
            "name": tool_name,
            "description": description.strip(),
            "inputSchema": input_schema,
        }

    def _build_tools_from_sections(self, doc: MDIDocument) -> list[dict[str, Any]]:
        """从章节（非Web API场景）构建tools。"""
        tools: list[dict[str, Any]] = []

        def walk(section):
            params = self._collect_params(section)
            if params or section.level in (2, 3):
                tool_name = sanitize_identifier(section.title).replace("-", "_")
                if tool_name and not tool_name.startswith("_"):
                    properties: dict[str, Any] = {}
                    required: list[str] = []
                    for param in params:
                        prop_schema = map_json_schema_type(param.type)
                        if param.description:
                            prop_schema["description"] = param.description
                        properties[param.name] = prop_schema
                        if param.required:
                            required.append(param.name)

                    input_schema: dict[str, Any] = {
                        "type": "object",
                        "properties": properties,
                    }
                    if required:
                        input_schema["required"] = required

                    desc = section.content[:200].strip() if section.content else section.title
                    tools.append({
                        "name": tool_name,
                        "description": desc,
                        "inputSchema": input_schema,
                    })
            for sub in section.subsections:
                walk(sub)

        for section in doc.sections:
            walk(section)

        return tools

    def _collect_params(self, section) -> list[Parameter]:
        """从章节收集参数。"""
        params: list[Parameter] = []
        for table in section.tables:
            if table.get("type") == "parameter":
                params.extend(table.get("parsed_items", []))
        return params
