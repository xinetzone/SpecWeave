"""Python类型生成器。

为每个Interface生成TypedDict类型定义。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument, Interface, Parameter
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import (
    escape_docstring,
    make_interface_name,
    map_python_type,
    snake_to_pascal,
    sanitize_identifier,
)


class PythonGenerator(BaseGenerator):
    """Python类型代码生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        type_names: list[str] = []
        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "types").replace("-", "_")
        )

        for iface in doc.interfaces:
            class_name = make_interface_name(iface.name)
            if not class_name:
                continue
            type_names.append(class_name)
            content = self._generate_typed_dict(iface)
            file_path = output_dir / f"{module_name}_{sanitize_identifier(iface.name).lower()}.py"
            generated_files.append(self._write_file(file_path, content))

        section_types_content = self._generate_params_types(doc)
        if section_types_content.strip():
            file_path = output_dir / f"{module_name}_types.py"
            generated_files.append(self._write_file(file_path, section_types_content))

        if not generated_files:
            init_content = self._generate_empty_module(doc)
            init_path = output_dir / f"{module_name}.py"
            generated_files.append(self._write_file(init_path, init_content))
        elif doc.interfaces:
            init_content = self._generate_init(type_names, module_name)
            init_path = output_dir / "__init__.py"
            generated_files.append(self._write_file(init_path, init_content))

        return generated_files

    def _generate_typed_dict(self, iface: Interface) -> str:
        """为单个Interface生成TypedDict。"""
        class_name = make_interface_name(iface.name)
        lines: list[str] = []

        lines.append("from __future__ import annotations")
        lines.append("")
        lines.append("from typing import TypedDict, Literal, Any")
        lines.append("")

        doc = iface.description or iface.summary or iface.name
        lines.append(f"class {class_name}(TypedDict):")
        if doc:
            lines.append(f'    """{escape_docstring(doc)}"""')
            lines.append("")

        if not iface.parameters and not iface.request_body:
            lines.append("    pass")
        else:
            all_params = list(iface.parameters)
            if iface.request_body:
                all_params.append(iface.request_body)

            for param in all_params:
                py_type = map_python_type(param.type)
                if not param.required:
                    py_type = f"{py_type} | None"
                param_name = sanitize_identifier(param.name)
                desc = param.description
                if desc:
                    lines.append(f"    {param_name}: {py_type}")
                    lines.append(f'    """{escape_docstring(desc)}"""')
                else:
                    lines.append(f"    {param_name}: {py_type}")
                lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def _generate_params_types(self, doc: MDIDocument) -> str:
        """从章节表格提取参数生成类型。"""
        lines: list[str] = [
            "from __future__ import annotations",
            "",
            "from typing import TypedDict, Literal, Any",
            "",
        ]
        found_types = False

        for section in doc.sections:
            params = self._collect_params_from_section(section)
            if params:
                found_types = True
                class_name = snake_to_pascal(sanitize_identifier(section.title))
                lines.append(f"class {class_name}(TypedDict):")
                if section.content:
                    desc = section.content[:200].strip()
                    if desc:
                        lines.append(f'    """{escape_docstring(desc)}"""')
                        lines.append("")
                for param in params:
                    py_type = map_python_type(param.type)
                    if not param.required:
                        py_type = f"{py_type} | None"
                    param_name = sanitize_identifier(param.name)
                    lines.append(f"    {param_name}: {py_type}")
                    if param.description:
                        lines.append(f'    """{escape_docstring(param.description)}"""')
                    lines.append("")
                if not params:
                    lines.append("    pass")
                lines.append("")

        return "\n".join(lines) if found_types else ""

    def _collect_params_from_section(self, section) -> list[Parameter]:
        """从章节收集参数。"""
        params: list[Parameter] = []
        for table in section.tables:
            if table.get("type") == "parameter":
                params.extend(table.get("parsed_items", []))
        for sub in section.subsections:
            params.extend(self._collect_params_from_section(sub))
        return params

    def _generate_init(self, type_names: list[str], module_prefix: str) -> str:
        """生成__init__.py导出文件。"""
        lines: list[str] = []
        for name in type_names:
            lines.append(f"from .{module_prefix}_{name.lower()} import {name}")
        lines.append("")
        lines.append("__all__ = [")
        for name in type_names:
            lines.append(f'    "{name}",')
        lines.append("]")
        return "\n".join(lines) + "\n"

    def _generate_empty_module(self, doc: MDIDocument) -> str:
        """生成空模块（当没有interfaces/参数表时）。"""
        lines: list[str] = []
        name = doc.frontmatter.get("name", "module")
        desc = doc.description or doc.title or f"Types for {name}"
        lines.append(f'"""Types for {name}.')
        lines.append("")
        lines.append(escape_docstring(desc))
        lines.append('"""')
        lines.append("")
        lines.append("from __future__ import annotations")
        lines.append("")
        lines.append("from typing import TypedDict, Literal, Any")
        lines.append("")
        lines.append("")
        lines.append(f"# Auto-generated from MDI document: {name}")
        lines.append(f"# No interfaces with parameter tables found in the source document.")
        lines.append("")
        return "\n".join(lines)
