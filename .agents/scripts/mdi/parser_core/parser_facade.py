from __future__ import annotations

import json
import logging
import re
import sys
import traceback
from dataclasses import fields
from pathlib import Path
from typing import Any

import tomllib
import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from .constants import (
    logger,
    CheckItem,
    CodeBlock,
    DecisionNode,
    ErrorCode,
    Interface,
    MDIDocument,
    Parameter,
    Response,
    Section,
)
from .block_parser import BlockParserMixin
from .directive_parser import DirectiveParserMixin


class MDIParser(BlockParserMixin, DirectiveParserMixin):
    """Markdown Interface文档解析器。

    将Markdown文档解析为MDIDocument结构化对象，支持frontmatter解析、
    block-level元素提取、章节树构建、表格分类、MyST-style directives、接口提取等功能。

    Args:
        profile_type: Profile类型，"auto"自动检测或指定"skill"/"webapi"/"clitool"。
    """

    def __init__(self, profile_type: str = "auto") -> None:
        self.profile_type = profile_type
        self._md = MarkdownIt("commonmark", {"html": False})
        self._md.use(front_matter_plugin)
        self._md.use(tasklists_plugin)
        self._md.enable(["table"])
        self._warnings: list[str] = []

    def parse_file(self, path: str | Path) -> MDIDocument:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        doc = self.parse_text(text, source=str(file_path))
        doc.source_path = file_path
        self._load_toml_ref(doc, file_path.parent)
        doc.warnings = list(self._warnings)
        return doc

    def parse_text(self, text: str, source: str = "<string>") -> MDIDocument:
        self._warnings = []
        self._source_text = text

        frontmatter, body = self._parse_frontmatter(text)
        doc = MDIDocument(
            frontmatter=frontmatter,
            source_path=Path(source) if source != "<string>" else None,
        )

        tokens = self._md.parse(body)
        blocks = self._tokens_to_blocks(tokens, body)
        self._build_document(doc, blocks)

        has_directive_endpoints = any(
            b.get("type") == "directive" and b.get("directive_name") in ("endpoint", "command")
            for b in blocks
        )
        has_directive_commands = any(
            b.get("type") == "directive" and b.get("directive_name") == "command"
            for b in blocks
        )
        is_cli = self.profile_type == "clitool" or (
            self.profile_type == "auto" and has_directive_commands
        )
        is_webapi = self.profile_type == "webapi" or (
            self.profile_type == "auto" and (self._detect_webapi(doc) or (has_directive_endpoints and not is_cli))
        )

        if has_directive_endpoints:
            self._extract_interfaces_from_directives(blocks, doc)
        if is_webapi:
            self._extract_interfaces(doc)

        doc.warnings = list(self._warnings)

        return doc

    def to_json(self, doc: MDIDocument, indent: int = 2) -> str:
        def _serialize(obj: Any) -> Any:
            if hasattr(obj, "__dataclass_fields__"):
                result = {}
                for f in fields(obj):
                    val = getattr(obj, f.name)
                    if f.name == "source_path" and val is not None:
                        result[f.name] = str(val)
                    elif f.name == "edges" and isinstance(val, list):
                        result[f.name] = [list(e) for e in val]
                    else:
                        result[f.name] = _serialize(val)
                return result
            if isinstance(obj, list):
                return [_serialize(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, tuple):
                return list(obj)
            return obj

        return json.dumps(_serialize(doc), ensure_ascii=False, indent=indent)

    def batch_parse(self, paths: list[str | Path]) -> list[MDIDocument]:
        return [self.parse_file(p) for p in paths]

    def _warn(self, message: str, line: int = 0) -> None:
        prefix = f"[line {line}] " if line > 0 else ""
        self._warnings.append(f"{prefix}{message}")

    def _parse_frontmatter(self, text: str) -> tuple[dict[str, Any], str]:
        tokens = self._md.parse(text)
        for t in tokens:
            if t.type == "front_matter":
                fm_text = t.content
                end_line = t.map[1] if t.map else 0
                lines = text.split("\n")
                body_start = 0
                for i, line in enumerate(lines):
                    if line.strip() == "---" and i > 0:
                        body_start = i + 1
                        break
                body = "\n".join(lines[body_start:]) if body_start > 0 else text
                return self._parse_yaml_fm(fm_text), body
        return {}, text

    def _parse_yaml_fm(self, fm_text: str) -> dict[str, Any]:
        try:
            result = yaml.safe_load(fm_text)
            if isinstance(result, dict):
                return result
            if result is None:
                return {}
            self._warn(f"YAML frontmatter解析结果不是dict: {type(result)}")
            return {}
        except Exception as e:
            self._warn(f"YAML frontmatter解析失败: {e}")
            return {}

    def _load_toml_ref(self, doc: MDIDocument, base_dir: Path) -> None:
        ref = doc.frontmatter.get("x-toml-ref")
        if not ref:
            logger.debug("x-toml-ref: 未配置，跳过外部TOML加载")
            return
        doc_name = doc.source_path or Path("<unknown>")
        logger.debug("x-toml-ref: 开始处理，doc=%s, ref=%r (type=%s)", doc_name, ref, type(ref).__name__)
        toml_path: Path | None = None
        toml_rel_path: str = ""
        sub_key: str | None = None
        try:
            if isinstance(ref, str):
                toml_rel_path = ref
                toml_path = (base_dir / ref).resolve()
                sub_key = None
            elif isinstance(ref, dict):
                toml_rel_path = ref.get("path", "")
                sub_key = ref.get("key")
                toml_path = (base_dir / toml_rel_path).resolve() if toml_rel_path else None
                if not toml_rel_path:
                    msg = "x-toml-ref对象形式缺少path字段"
                    logger.error("x-toml-ref: %s (doc=%s, ref=%r)", msg, doc_name, ref)
                    self._warn(f"{msg}")
                    return
            else:
                msg = f"x-toml-ref格式无效，应为字符串或对象，实际类型: {type(ref).__name__}"
                logger.error("x-toml-ref: %s (doc=%s, ref=%r)", msg, doc_name, ref)
                self._warn(msg)
                return
            if not toml_path.exists():
                msg = f"x-toml-ref引用的TOML文件不存在: {toml_path} (相对路径: {toml_rel_path}, base_dir: {base_dir.resolve()})"
                logger.error("x-toml-ref: 文件不存在，doc=%s\n  尝试路径: %s\n  base_dir: %s\n  相对路径: %s", doc_name, toml_path, base_dir.resolve(), toml_rel_path)
                self._warn(f"x-toml-ref引用的TOML文件不存在: {toml_path}")
                return
            if not toml_path.is_file():
                msg = f"x-toml-ref路径存在但不是文件: {toml_path}"
                logger.error("x-toml-ref: 路径不是文件: %s (doc=%s)", toml_path, doc_name)
                self._warn(msg)
                return
            with open(toml_path, "rb") as f:
                toml_data = tomllib.load(f)
            if sub_key:
                current = toml_data
                traversed: list[str] = []
                for part in sub_key.split("."):
                    traversed.append(part)
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        available = list(current.keys()) if isinstance(current, dict) else f"<非dict>"
                        self._warn(f"x-toml-ref子键路径不存在: {sub_key}")
                        return
                toml_data = current
            if not isinstance(toml_data, dict):
                self._warn(f"x-toml-ref解析结果不是dict: {type(toml_data).__name__}")
                return
            merged = {**toml_data, **doc.frontmatter}
            doc.frontmatter = merged
        except tomllib.TOMLDecodeError as e:
            self._warn(f"x-toml-ref TOML解析失败: {e}")
        except OSError as e:
            self._warn(f"x-toml-ref读取TOML文件失败: {e}")
        except Exception as e:
            logger.error("x-toml-ref: 未预期异常，doc=%s\n  ref=%r\n  toml_path=%s\n  %s", doc_name, ref, toml_path, traceback.format_exc())
            self._warn(f"x-toml-ref加载失败: {type(e).__name__}: {e}")

    def _build_document(self, doc: MDIDocument, blocks: list[dict]) -> None:
        if not blocks:
            return

        first_heading_idx = 0
        for i, b in enumerate(blocks):
            if b["type"] == "heading" and b.get("level") == 1:
                doc.title = b.get("text", "")
                first_heading_idx = i
                break
            if b["type"] == "paragraph" and not doc.description:
                doc.description = b.get("text", "")

        section_stack: list[Section] = []
        current_section: Section | None = None
        pending_paragraphs: list[str] = []
        pending_code_blocks: list[CodeBlock] = []
        pending_lists: list[Any] = []
        pending_tables: list[dict[str, Any]] = []
        pending_directives: list[dict] = []

        def _flush_content() -> None:
            if current_section is not None:
                if pending_paragraphs:
                    current_section.content += "\n".join(pending_paragraphs)
                current_section.code_blocks.extend(pending_code_blocks)
                current_section.lists.extend(pending_lists)
                current_section.tables.extend(pending_tables)
                for d in pending_directives:
                    cb = CodeBlock(
                        language=f"directive:{d['directive_name']}",
                        meta=d.get("args", ""),
                        content=d.get("body", ""),
                        purpose="directive",
                    )
                    current_section.code_blocks.append(cb)

        for block in blocks[first_heading_idx:]:
            bt = block["type"]

            if bt == "heading":
                level = block["level"]
                heading_text = block["text"]

                _flush_content()
                pending_paragraphs = []
                pending_code_blocks = []
                pending_lists = []
                pending_tables = []
                pending_directives = []

                new_section = Section(level=level, title=heading_text)

                while section_stack and section_stack[-1].level >= level:
                    section_stack.pop()

                if section_stack:
                    section_stack[-1].subsections.append(new_section)
                else:
                    doc.sections.append(new_section)

                section_stack.append(new_section)
                current_section = new_section

            elif bt == "paragraph":
                ptext = block.get("text", "")
                if ptext:
                    pending_paragraphs.append(ptext)

            elif bt == "block_code":
                lang = block.get("language", "")
                meta = block.get("meta", "")
                content = block.get("content", "")
                purpose = block.get("purpose", "")
                if not purpose:
                    purpose = self._detect_code_purpose(lang, meta) or self._infer_code_purpose(lang, meta, content)
                cb = CodeBlock(
                    language=lang,
                    meta=meta,
                    content=content,
                    purpose=purpose,
                )
                pending_code_blocks.append(cb)

                if lang == "mermaid" and purpose == "":
                    self._parse_mermaid_flowchart(content, pending_lists)

            elif bt == "directive":
                pending_directives.append(block)

            elif bt == "admonition":
                pending_paragraphs.append(f"> [{block['admonition_type'].upper()}] {block.get('text', '')}")

            elif bt == "list":
                ordered = block.get("ordered", False)
                items = block.get("items", [])
                check_items: list[CheckItem] = []
                list_items: list[str] = []
                has_checkbox = False
                line_no = block.get("line", 0)

                for item in items:
                    is_cb = item.get("is_task") or item.get("checked") is not None
                    if is_cb and not has_checkbox:
                        has_checkbox = True
                        for prev_text in list_items:
                            check_items.append(CheckItem(text=prev_text, checked=False, line=line_no))
                        list_items = []
                    if has_checkbox:
                        check_items.append(CheckItem(
                            text=item.get("text", ""),
                            checked=bool(item.get("checked", False)),
                            line=line_no,
                        ))
                    else:
                        list_items.append(item.get("text", ""))

                if has_checkbox and check_items:
                    pending_lists.append({"type": "checklist", "items": check_items})
                elif ordered:
                    pending_lists.append({"type": "ordered", "items": list_items, "start": block.get("start", 1)})
                else:
                    pending_lists.append({"type": "unordered", "items": list_items})

            elif bt == "table":
                table_info = self._classify_and_parse_table(block)
                if table_info:
                    pending_tables.append(table_info)

            elif bt == "block_quote":
                qtext = block.get("text", "")
                if qtext:
                    pending_paragraphs.append(f"> {qtext}")

        _flush_content()

        if not doc.description and doc.sections:
            first_section = doc.sections[0]
            if first_section.content:
                doc.description = first_section.content.split("\n")[0][:200]
