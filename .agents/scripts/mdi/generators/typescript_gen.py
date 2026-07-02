"""TypeScript类型生成器。

为每个Interface生成interface定义。
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
    make_interface_name,
    map_typescript_type,
    to_jsdoc_comment,
    sanitize_identifier,
    snake_to_pascal,
)


class TypeScriptGenerator(BaseGenerator):
    """TypeScript类型代码生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        generated_files: list[Path] = []
        interfaces_content: list[str] = []
        exports: list[str] = []

        for iface in doc.interfaces:
            iface_name = make_interface_name(iface.name)
            if not iface_name:
                continue
            exports.append(iface_name)
            interfaces_content.append(self._generate_interface(iface))

        section_types = self._generate_section_types(doc)
        interfaces_content.extend(section_types)

        if not interfaces_content:
            module_name = sanitize_identifier(
                doc.frontmatter.get("name", "types")
            ).replace("_", "-")
            name = doc.frontmatter.get("name", "types")
            desc = doc.description or doc.title or f"Types for {name}"
            interfaces_content.append(
                f"/**\n * {desc}\n */\n"
                f"// Auto-generated from MDI document: {name}\n"
                f"// No interfaces with parameter tables found.\n"
            )

        content = "\n\n".join(interfaces_content)
        if exports:
            content += "\n\nexport {\n"
            for name in exports:
                content += f"    {name},\n"
            content += "};\n"

        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "types")
        ).replace("_", "-")
        file_path = output_dir / f"{module_name}.ts"
        generated_files.append(self._write_file(file_path, content))

        return generated_files

    def _generate_interface(self, iface: Interface) -> str:
        """为单个Interface生成TypeScript interface。"""
        iface_name = make_interface_name(iface.name)
        lines: list[str] = []

        doc = iface.description or iface.summary or iface.name
        if doc:
            lines.append(to_jsdoc_comment(doc, indent=""))

        lines.append(f"export interface {iface_name} {{")

        all_params = list(iface.parameters)
        if iface.request_body:
            all_params.append(iface.request_body)

        for param in all_params:
            ts_type = map_typescript_type(param.type)
            param_name = sanitize_identifier(param.name)
            optional = "?" if not param.required else ""

            if param.description:
                lines.append(to_jsdoc_comment(param.description))
            lines.append(f"    {param_name}{optional}: {ts_type};")

        if not all_params:
            lines.append("    [key: string]: any;")

        lines.append("}")
        return "\n".join(lines)

    def _generate_section_types(self, doc: MDIDocument) -> list[str]:
        """从章节提取参数生成interface。"""
        result: list[str] = []

        def walk(section):
            params = self._collect_params(section)
            if params:
                iface_name = snake_to_pascal(sanitize_identifier(section.title))
                lines: list[str] = []
                if section.content:
                    desc = section.content[:200].strip()
                    if desc:
                        lines.append(to_jsdoc_comment(desc, indent=""))
                lines.append(f"export interface {iface_name} {{")
                for param in params:
                    ts_type = map_typescript_type(param.type)
                    param_name = sanitize_identifier(param.name)
                    optional = "?" if not param.required else ""
                    if param.description:
                        lines.append(to_jsdoc_comment(param.description))
                    lines.append(f"    {param_name}{optional}: {ts_type};")
                lines.append("}")
                result.append("\n".join(lines))
            for sub in section.subsections:
                walk(sub)

        for section in doc.sections:
            walk(section)

        return result

    def _collect_params(self, section) -> list[Parameter]:
        """从章节收集参数。"""
        params: list[Parameter] = []
        for table in section.tables:
            if table.get("type") == "parameter":
                params.extend(table.get("parsed_items", []))
        return params
