"""Markdown文档生成器。

将MDIDocument重新生成为格式统一的人类友好Markdown文档。
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument, Interface, Section
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import sanitize_identifier


class MarkdownGenerator(BaseGenerator):
    """Markdown文档格式化生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        content = self._build_markdown(doc)
        name = doc.frontmatter.get("name", "output")
        file_path = output_dir / f"{sanitize_identifier(name).replace('_', '-')}.md"
        self._write_file(file_path, content)
        return [file_path]

    def _build_markdown(self, doc: MDIDocument) -> str:
        """构建完整的Markdown文档。"""
        lines: list[str] = []

        lines.append("---")
        for key, value in doc.frontmatter.items():
            if isinstance(value, str):
                lines.append(f"{key}: {value}")
            elif isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")

        if doc.title:
            lines.append(f"# {doc.title}")
            lines.append("")

        if doc.description:
            lines.append(doc.description.strip())
            lines.append("")

        for section in doc.sections:
            lines.extend(self._render_section(section))

        if doc.interfaces:
            lines.append("## API 接口")
            lines.append("")
            for iface in doc.interfaces:
                lines.extend(self._render_interface(iface))

        return "\n".join(lines).rstrip() + "\n"

    def _render_section(self, section: Section, indent_level: int = 0) -> list[str]:
        """渲染单个章节。"""
        lines: list[str] = []
        prefix = "#" * section.level
        lines.append(f"{prefix} {section.title}")
        lines.append("")

        if section.content:
            content = section.content.strip()
            if content:
                lines.append(content)
                lines.append("")

        for cb in section.code_blocks:
            lang = cb.language or ""
            meta = f" {cb.meta}" if cb.meta else ""
            lines.append(f"```{lang}{meta}")
            lines.append(cb.content)
            lines.append("```")
            lines.append("")

        for table in section.tables:
            lines.extend(self._render_table(table))

        for lst in section.lists:
            lines.extend(self._render_list(lst))

        for sub in section.subsections:
            lines.extend(self._render_section(sub))

        return lines

    def _render_table(self, table: dict[str, Any]) -> list[str]:
        """渲染表格。"""
        lines: list[str] = []
        header = table.get("header", [])
        rows = table.get("rows", [])
        alignments = table.get("alignments", [])

        if not header:
            return lines

        col_widths = [len(str(h)) for h in header]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        def align_cell(cell: str, width: int, align: str | None) -> str:
            cell_str = str(cell)
            pad = width - len(cell_str)
            if align == "center":
                left = pad // 2
                right = pad - left
                return " " * left + cell_str + " " * right
            elif align == "right":
                return " " * pad + cell_str
            else:
                return cell_str + " " * pad

        header_line = "| " + " | ".join(
            align_cell(str(h), col_widths[i], alignments[i] if i < len(alignments) else None)
            for i, h in enumerate(header)
        ) + " |"
        lines.append(header_line)

        sep_parts = []
        for i, w in enumerate(col_widths):
            align = alignments[i] if i < len(alignments) else None
            if align == "center":
                sep_parts.append(":" + "-" * (w - 2) + ":")
            elif align == "right":
                sep_parts.append("-" * (w - 1) + ":")
            else:
                sep_parts.append("-" * w)
        lines.append("| " + " | ".join(sep_parts) + " |")

        for row in rows:
            row_cells = []
            for i in range(len(header)):
                cell = row[i] if i < len(row) else ""
                align = alignments[i] if i < len(alignments) else None
                row_cells.append(align_cell(str(cell), col_widths[i], align))
            lines.append("| " + " | ".join(row_cells) + " |")

        lines.append("")
        return lines

    def _render_list(self, lst: dict[str, Any]) -> list[str]:
        """渲染列表。"""
        lines: list[str] = []
        list_type = lst.get("type", "unordered")
        items = lst.get("items", [])

        if list_type == "checklist":
            for item in items:
                if hasattr(item, "checked"):
                    checked = "x" if item.checked else " "
                    text = item.text or ""
                elif isinstance(item, dict):
                    checked = "x" if item.get("checked") else " "
                    text = item.get("text", "")
                else:
                    checked = " "
                    text = str(item)
                lines.append(f"- [{checked}] {text}")
        elif list_type == "ordered":
            start = lst.get("start", 1)
            for i, item in enumerate(items):
                lines.append(f"{i + start}. {item}")
        else:
            for item in items:
                lines.append(f"- {item}")

        lines.append("")
        return lines

    def _render_interface(self, iface: Interface) -> list[str]:
        """渲染API接口章节。"""
        lines: list[str] = []

        method = iface.method.upper() if iface.method else ""
        path = iface.path or ""
        title_parts = []
        if method and path:
            title_parts.append(f"`{method} {path}`")
        title_parts.append(iface.name)
        lines.append(f"### {' '.join(title_parts)}")
        lines.append("")

        if iface.summary:
            lines.append(f"**{iface.summary}**")
            lines.append("")

        if iface.description:
            lines.append(iface.description.strip())
            lines.append("")

        all_params = list(iface.parameters)
        if iface.request_body:
            all_params.append(iface.request_body)

        if all_params:
            lines.append("#### 参数")
            lines.append("")
            lines.append("| 参数名 | 类型 | 必填 | 描述 |")
            lines.append("|--------|------|------|------|")
            for param in all_params:
                req = "是" if param.required else "否"
                desc = param.description.replace("|", "\\|") if param.description else ""
                lines.append(f"| {param.name} | {param.type} | {req} | {desc} |")
            lines.append("")

        if iface.responses:
            lines.append("#### 响应")
            lines.append("")
            lines.append("| 状态码 | 描述 |")
            lines.append("|--------|------|")
            for resp in iface.responses:
                desc = resp.description.replace("|", "\\|") if resp.description else ""
                lines.append(f"| {resp.status_code} | {desc} |")
            lines.append("")

        if iface.errors:
            lines.append("#### 错误码")
            lines.append("")
            lines.append("| 错误码 | 消息 | 描述 |")
            lines.append("|--------|------|------|")
            for err in iface.errors:
                msg = err.message.replace("|", "\\|") if err.message else ""
                desc = err.description.replace("|", "\\|") if err.description else ""
                lines.append(f"| {err.code} | {msg} | {desc} |")
            lines.append("")

        for example in iface.examples:
            lang = example.language or ""
            lines.append(f"```{lang}")
            lines.append(example.content)
            lines.append("```")
            lines.append("")

        return lines
