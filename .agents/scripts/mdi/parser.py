"""MDI Markdown Interface Parser核心实现。

将Markdown文档解析为结构化的MDIDocument对象，支持Skill/WebApi/CliTool三种Profile。
使用markdown-it-py（CommonMark 100%兼容）进行解析，提供frontmatter提取、章节树构建、
表格分类、代码块识别、复选框提取、Mermaid流程图解析、MyST-style directives等能力。

MyST-style directives 语法（在fenced code block中使用）:
    ```{directive-name} arguments
    :option1: value1
    :option2: value2

    Directive body content (markdown)
    ```

支持的directives:
- {endpoint} METHOD /path  —  Web API端点定义
- {param} name: type       —  参数定义（可在endpoint内或独立）
- {response} status_code   —  响应定义
- {error} code             —  错误码定义
- {note}/{warning}/{danger}/{tip}  —  提示块
"""

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

logger = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import (
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

_PARAM_TABLE_KEYWORDS = {
    "参数名", "name", "param", "parameter",
    "字段", "field", "参数表", "属性",
}
_RESPONSE_TABLE_KEYWORDS = {
    "状态码", "status code", "响应码", "返回码", "statuscode",
    "响应表",
}
_ERROR_TABLE_KEYWORDS = {
    "错误码", "error code", "errcode", "errorcode",
    "错误码表",
}

_PARAM_COLUMN_MAP = {
    "name": {"name", "参数名", "名称", "参数", "字段名", "field", "key", "变量名"},
    "type": {"type", "类型", "数据类型", "字段类型"},
    "required": {"required", "必填", "是否必填", "必须", "必选"},
    "description": {"description", "描述", "说明", "含义", "备注", "comment"},
    "default": {"default", "默认值", "缺省值", "默认"},
    "location": {"location", "位置", "in", "参数位置", "来源"},
}

_RESPONSE_COLUMN_MAP = {
    "status_code": {"code", "状态码", "status", "响应码", "返回码", "statuscode", "http码"},
    "description": {"description", "描述", "说明", "含义"},
    "schema": {"schema", "模式", "结构", "数据结构"},
    "example": {"example", "示例", "响应示例", "返回示例"},
}

_ERROR_COLUMN_MAP = {
    "code": {"code", "错误码", "errcode", "errorcode", "码值"},
    "message": {"message", "消息", "错误消息", "提示", "错误信息"},
    "description": {"description", "描述", "说明", "处理方式", "解决方案"},
}

_CODE_PURPOSE_KEYWORDS = {"example", "schema", "mock", "test", "request", "response"}

_HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
_METHOD_PATH_RE = re.compile(
    r"`?(GET|POST|PUT|PATCH|DELETE)\s+(/[\w/\-{}.]*)`?"
)

_MERMAID_FLOWCHART_RE = re.compile(
    r"flowchart\s+(TD|LR|RL|BT)",
    re.IGNORECASE,
)
_MERMAID_NODE_RE = re.compile(
    r'^\s*([A-Za-z0-9_]+)\s*(?:\[|\(|\{|\[\[|\(\()([^\]\)\}]+)(?:\]|\)|\}|\]\]|\)\))\s*$'
)
_MERMAID_SHAPE_CAP = r'(?:\[([^\]]*)\]|\(([^)]*)\)|\{([^}]*)\}|\[\[([^\]]*)\]\]|\(\(([^)]*)\)\))'
_MERMAID_EDGE_RE = re.compile(
    r'^\s*([A-Za-z0-9_]+)' + _MERMAID_SHAPE_CAP + r'?\s*(-->|-.->|==>|--->)\s*(?:\|([^|]+)\|\s*)?([A-Za-z0-9_]+)' + _MERMAID_SHAPE_CAP + r'?\s*$'
)

_DIRECTIVE_RE = re.compile(r'^\{(\w[\w-]*)\}\s*(.*)$')
_OPTION_LINE_RE = re.compile(r'^:([\w][\w\s\-]*?)(\??)\s*:\s*(.*)$')

_ADMONITION_TYPES = {"note", "warning", "danger", "tip", "important", "caution", "hint", "info", "seealso"}


def _normalize_header(text: str) -> str:
    return re.sub(r"\s+", "", text.strip().lower())


def _match_column(header: str, column_map: dict[str, set[str]]) -> str | None:
    normalized = _normalize_header(header)
    for col_name, keywords in column_map.items():
        for kw in keywords:
            if _normalize_header(kw) in normalized or normalized in _normalize_header(kw):
                return col_name
    return None


def _extract_inline_text(tokens: list, start: int, end: int) -> str:
    parts: list[str] = []
    for i in range(start, end):
        t = tokens[i]
        if t.type == "text":
            parts.append(t.content)
        elif t.type == "code_inline":
            parts.append(f"`{t.content}`")
        elif t.type == "softbreak" or t.type == "hardbreak":
            parts.append("\n")
        elif t.type == "strong_open" or t.type == "strong_close":
            parts.append("**")
        elif t.type == "em_open" or t.type == "em_close":
            parts.append("*")
        elif t.type == "link_open":
            pass
        elif t.type == "link_close":
            pass
        elif t.type == "image":
            parts.append(t.content or "")
        elif t.type == "html_inline":
            parts.append(t.content)
        elif t.children:
            parts.append(_extract_inline_text(t.children, 0, len(t.children)))
    return "".join(parts)


class MDIParser:
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
            b.get("type") == "directive" and b.get("directive_name") == "endpoint"
            for b in blocks
        )
        is_webapi = self.profile_type == "webapi" or (
            self.profile_type == "auto" and (self._detect_webapi(doc) or has_directive_endpoints)
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

    def _tokens_to_blocks(self, tokens: list, body: str) -> list[dict]:
        blocks: list[dict] = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            line = t.map[0] + 1 if t.map else 0

            if t.type == "front_matter":
                i += 1
                continue

            if t.type == "heading_open":
                level = int(t.tag[1])
                j = i + 1
                heading_text = ""
                while j < len(tokens) and tokens[j].type != "heading_close":
                    if tokens[j].type == "inline":
                        heading_text = _extract_inline_text(tokens[j].children or [], 0, len(tokens[j].children or []))
                    j += 1
                blocks.append({"type": "heading", "level": level, "text": heading_text, "line": line})
                i = j + 1
                continue

            if t.type == "paragraph_open":
                j = i + 1
                ptext = ""
                while j < len(tokens) and tokens[j].type != "paragraph_close":
                    if tokens[j].type == "inline":
                        ptext = _extract_inline_text(tokens[j].children or [], 0, len(tokens[j].children or []))
                    j += 1
                blocks.append({"type": "paragraph", "text": ptext, "line": line})
                i = j + 1
                continue

            if t.type == "fence":
                info = t.info or ""
                content = t.content.rstrip("\n") if t.content else ""
                lang = ""
                meta = ""
                is_directive = False
                directive_name = ""
                directive_args = ""
                directive_options: dict[str, str] = {}
                directive_body = ""

                dm = _DIRECTIVE_RE.match(info.strip())
                if dm:
                    is_directive = True
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    directive_options_raw, directive_body = self._parse_directive_content(content)
                    directive_options: dict[str, str] = {}
                    directive_options_optional: dict[str, bool] = {}
                    for k, (v, is_opt) in directive_options_raw.items():
                        directive_options[k] = v
                        directive_options_optional[k] = is_opt
                    if directive_name in _ADMONITION_TYPES:
                        blocks.append({
                            "type": "admonition",
                            "admonition_type": directive_name,
                            "title": directive_args,
                            "text": directive_body,
                            "options": directive_options,
                            "line": line,
                        })
                        i += 1
                        continue
                    blocks.append({
                        "type": "directive",
                        "directive_name": directive_name,
                        "args": directive_args,
                        "options": directive_options,
                        "options_optional": directive_options_optional,
                        "body": directive_body,
                        "content": content,
                        "line": line,
                    })
                    i += 1
                    continue
                else:
                    if info:
                        parts = info.strip().split(None, 1)
                        lang = parts[0] if parts else ""
                        meta = parts[1] if len(parts) > 1 else ""
                    purpose = self._detect_code_purpose(info, meta)
                    blocks.append({
                        "type": "block_code",
                        "language": lang,
                        "meta": meta,
                        "content": content,
                        "line": line,
                        "purpose": purpose,
                    })
                    i += 1
                    continue

            if t.type == "bullet_list_open" or t.type == "ordered_list_open":
                ordered = t.type == "ordered_list_open"
                start = t.attrs.get("start", 1) if t.attrs else 1
                items, j = self._parse_list_tokens(tokens, i + 1)
                blocks.append({
                    "type": "list",
                    "ordered": ordered,
                    "start": start,
                    "items": items,
                    "line": line,
                })
                i = j + 1
                continue

            if t.type == "blockquote_open":
                j = i + 1
                depth = 1
                quote_parts: list[str] = []
                while j < len(tokens) and depth > 0:
                    if tokens[j].type == "blockquote_open":
                        depth += 1
                    elif tokens[j].type == "blockquote_close":
                        depth -= 1
                        if depth == 0:
                            break
                    elif tokens[j].type == "inline":
                        quote_parts.append(_extract_inline_text(tokens[j].children or [], 0, len(tokens[j].children or [])))
                    j += 1
                quote_text = "\n".join(quote_parts)
                blocks.append({"type": "block_quote", "text": quote_text, "line": line})
                i = j + 1
                continue

            if t.type == "table_open":
                table_data, j = self._parse_table_tokens(tokens, i)
                table_data["line"] = line
                blocks.append(table_data)
                i = j + 1
                continue

            i += 1

        return blocks

    def _parse_list_tokens(self, tokens: list, start: int) -> tuple[list[dict], int]:
        items: list[dict] = []
        i = start
        while i < len(tokens):
            t = tokens[i]
            if t.type in ("bullet_list_close", "ordered_list_close"):
                return items, i
            if t.type == "list_item_open":
                checked: bool | None = None
                is_task = False
                item_text_parts: list[str] = []
                nested_lists: list[dict] = []
                j = i + 1
                while j < len(tokens) and tokens[j].type != "list_item_close":
                    ct = tokens[j]
                    if ct.type == "paragraph_open":
                        k = j + 1
                        while k < len(tokens) and tokens[k].type != "paragraph_close":
                            if tokens[k].type == "inline":
                                children = tokens[k].children or []
                                task_checked, item_text = self._extract_task_item_from_children(children)
                                if task_checked is not None:
                                    is_task = True
                                    checked = task_checked
                                if item_text:
                                    item_text_parts.append(item_text)
                            k += 1
                        j = k
                    elif ct.type in ("bullet_list_open", "ordered_list_open"):
                        nested_ordered = ct.type == "ordered_list_open"
                        nested_items, nj = self._parse_list_tokens(tokens, j + 1)
                        nested_lists.append({
                            "ordered": nested_ordered,
                            "items": nested_items,
                        })
                        j = nj
                    elif ct.type == "inline":
                        children = ct.children or []
                        task_checked, item_text = self._extract_task_item_from_children(children)
                        if task_checked is not None:
                            is_task = True
                            checked = task_checked
                        if item_text:
                            item_text_parts.append(item_text)
                    j += 1
                text = " ".join(item_text_parts).strip()
                if not is_task:
                    checkbox_info = self._extract_checkbox(text)
                    if checkbox_info:
                        is_task = True
                        checked = checkbox_info[0]
                        text = checkbox_info[1]
                items.append({
                    "text": text,
                    "checked": checked if is_task else None,
                    "is_task": is_task,
                    "nested": nested_lists,
                })
                i = j + 1
            else:
                i += 1
        return items, i

    def _extract_task_item_from_children(self, children: list) -> tuple[bool | None, str]:
        has_checkbox = False
        checked = False
        text_parts: list[str] = []
        for child in children:
            if child.type == "html_inline" and "task-list-item-checkbox" in (child.content or ""):
                has_checkbox = True
                if "checked" in (child.content or "").lower():
                    checked = True
            elif child.type == "text":
                txt = child.content
                if has_checkbox and txt.startswith(" "):
                    txt = txt[1:]
                text_parts.append(txt)
            elif child.type == "softbreak" or child.type == "hardbreak":
                text_parts.append("\n")
            elif child.type == "code_inline":
                text_parts.append(f"`{child.content}`")
            elif child.type == "strong_open" or child.type == "strong_close":
                text_parts.append("**")
            elif child.type == "em_open" or child.type == "em_close":
                text_parts.append("*")
        text = "".join(text_parts).strip()
        if has_checkbox:
            return checked, text
        return None, text

    def _extract_checkbox(self, text: str) -> tuple[bool, str] | None:
        for prefix in ("[x] ", "[X] ", "[ ] "):
            if text.startswith(prefix):
                checked = prefix in ("[x] ", "[X] ")
                return checked, text[len(prefix):]
        return None

    def _parse_table_tokens(self, tokens: list, start: int) -> tuple[dict, int]:
        header: list[str] = []
        alignments: list[str | None] = []
        rows: list[list[str]] = []
        i = start + 1
        in_thead = False
        in_tbody = False

        while i < len(tokens):
            t = tokens[i]
            if t.type == "table_close":
                break
            if t.type == "thead_open":
                in_thead = True
            elif t.type == "thead_close":
                in_thead = False
            elif t.type == "tbody_open":
                in_tbody = True
            elif t.type == "tbody_close":
                in_tbody = False
            elif t.type == "tr_open":
                cells: list[str] = []
                j = i + 1
                is_header_row = in_thead
                while j < len(tokens) and tokens[j].type != "tr_close":
                    ct = tokens[j]
                    if ct.type in ("th_open", "td_open"):
                        align = None
                        if ct.attrs:
                            style = ct.attrs.get("style", "")
                            if "center" in style:
                                align = "center"
                            elif "right" in style:
                                align = "right"
                            elif "left" in style:
                                align = "left"
                        cell_text = ""
                        k = j + 1
                        while k < len(tokens) and tokens[k].type not in ("th_close", "td_close"):
                            if tokens[k].type == "inline":
                                cell_text = _extract_inline_text(tokens[k].children or [], 0, len(tokens[k].children or []))
                            k += 1
                        cells.append(cell_text.strip())
                        if is_header_row:
                            alignments.append(align)
                        j = k
                    j += 1
                if is_header_row:
                    header = cells
                else:
                    rows.append(cells)
                i = j
            i += 1

        return {
            "type": "table",
            "header": header,
            "alignments": alignments,
            "rows": rows,
        }, i

    def _parse_directive_content(self, content: str) -> tuple[dict[str, tuple[str, bool]], str]:
        options: dict[str, tuple[str, bool]] = {}
        lines = content.split("\n")
        body_start = 0
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                body_start = idx + 1
                break
            if not stripped.startswith(":"):
                body_start = idx
                break
            colon_pos = line.find(":", 1)
            if colon_pos == -1:
                body_start = idx
                break
            raw_key = line[1:colon_pos].strip()
            val = line[colon_pos + 1:].strip()
            is_optional = False
            if raw_key.endswith("?"):
                is_optional = True
                raw_key = raw_key[:-1].strip()
            options[raw_key] = (val, is_optional)
            body_start = idx + 1
        else:
            body_start = len(lines)

        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        body = "\n".join(lines[body_start:]).strip()
        return options, body

    def _detect_code_purpose(self, info: str, meta: str) -> str:
        combined = (info + " " + meta).lower()
        for keyword in _CODE_PURPOSE_KEYWORDS:
            if keyword in combined:
                return keyword
        return ""

    def _infer_code_purpose(self, lang: str, meta: str, content: str) -> str:
        """当_detect_code_purpose无结果时，基于meta和内容推断code block用途。"""
        meta_lower = meta.lower()
        lang_lower = (lang or "").lower()
        if "status=" in meta_lower or "status_code=" in meta_lower:
            return "example"
        if lang_lower in ("json",) and content.strip().startswith(("{", "[")):
            return "example"
        if lang_lower in ("python", "py"):
            return "test"
        if lang_lower in ("bash", "sh", "shell", "curl"):
            return "example"
        return ""

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

    def _classify_and_parse_table(self, table_block: dict) -> dict[str, Any] | None:
        header = table_block.get("header", [])
        rows = table_block.get("rows", [])
        alignments = table_block.get("alignments", [])
        line = table_block.get("line", 0)

        if not header:
            self._warn("表格缺少表头", line)
            return None

        header_text = " ".join(header).lower()

        param_cols = self._try_match_columns(header, _PARAM_COLUMN_MAP, "name")
        response_cols = self._try_match_columns(header, _RESPONSE_COLUMN_MAP, "status_code")
        error_cols = self._try_match_columns(header, _ERROR_COLUMN_MAP, "code")

        table_type = "generic"
        parsed_items: list[Any] = []

        is_error_table = bool(error_cols and "message" in error_cols)

        if param_cols:
            table_type = "parameter"
            parsed_items = self._parse_parameter_table_with_cols(header, rows, line, param_cols)
        elif is_error_table:
            table_type = "error"
            parsed_items = self._parse_error_table_with_cols(header, rows, line, error_cols)
        elif response_cols:
            table_type = "response"
            parsed_items = self._parse_response_table_with_cols(header, rows, line, response_cols)
        elif any(kw in header_text for kw in _PARAM_TABLE_KEYWORDS):
            table_type = "parameter"
            parsed_items = self._parse_parameter_table(header, rows, line)
        elif any(kw in header_text for kw in _ERROR_TABLE_KEYWORDS):
            table_type = "error"
            parsed_items = self._parse_error_table(header, rows, line)
        elif any(kw in header_text for kw in _RESPONSE_TABLE_KEYWORDS):
            table_type = "response"
            parsed_items = self._parse_response_table(header, rows, line)

        return {
            "type": table_type,
            "header": header,
            "rows": rows,
            "alignments": alignments,
            "parsed_items": parsed_items,
            "line": line,
        }

    def _try_match_columns(
        self, header: list[str], column_map: dict[str, set[str]], required_key: str
    ) -> dict[str, int] | None:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, column_map)
            if col:
                col_map[col] = i
        if required_key in col_map:
            return col_map
        return None

    def _parse_parameter_table(
        self, header: list[str], rows: list[list[str]], line: int
    ) -> list[Parameter]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, _PARAM_COLUMN_MAP)
            if col:
                col_map[col] = i
        if "name" not in col_map:
            self._warn(f"参数表缺少name列，表头: {header}", line)
            return []
        return self._parse_parameter_table_with_cols(header, rows, line, col_map)

    def _parse_parameter_table_with_cols(
        self, header: list[str], rows: list[list[str]], line: int, col_map: dict[str, int]
    ) -> list[Parameter]:
        params: list[Parameter] = []
        for row_idx, row in enumerate(rows):
            if len(row) < len(header):
                self._warn(
                    f"参数表第{row_idx + 1}行列数不匹配（期望{len(header)}列，实际{len(row)}列），跳过",
                    line,
                )
                continue
            if len(row) > len(header):
                row = row[:len(header)]
            name = row[col_map["name"]].strip()
            if not name:
                continue
            ptype = row[col_map["type"]].strip() if "type" in col_map else "string"
            required = False
            if "required" in col_map:
                req_val = row[col_map["required"]].strip().lower()
                required = req_val in ("yes", "true", "是", "必填", "required", "y")
            desc = row[col_map["description"]].strip() if "description" in col_map else ""
            default = row[col_map["default"]].strip() if "default" in col_map else None
            if default == "":
                default = None
            location = row[col_map["location"]].strip() if "location" in col_map else "body"
            params.append(Parameter(
                name=name,
                type=ptype,
                required=required,
                description=desc,
                default=default,
                location=location,
            ))
        return params

    def _parse_response_table(
        self, header: list[str], rows: list[list[str]], line: int
    ) -> list[Response]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, _RESPONSE_COLUMN_MAP)
            if col:
                col_map[col] = i
        if "status_code" not in col_map:
            self._warn(f"响应表缺少status_code列，表头: {header}", line)
            return []
        return self._parse_response_table_with_cols(header, rows, line, col_map)

    def _parse_response_table_with_cols(
        self, header: list[str], rows: list[list[str]], line: int, col_map: dict[str, int]
    ) -> list[Response]:
        responses: list[Response] = []
        for row_idx, row in enumerate(rows):
            if len(row) < len(header):
                self._warn(f"响应表第{row_idx + 1}行列数不匹配，跳过", line)
                continue
            if len(row) > len(header):
                row = row[:len(header)]
            code_val = row[col_map["status_code"]].strip()
            desc = row[col_map["description"]].strip() if "description" in col_map else ""
            try:
                status_code: str | int = int(code_val) if code_val.isdigit() else code_val
            except (ValueError, TypeError):
                status_code = code_val
            responses.append(Response(status_code=status_code, description=desc))
        return responses

    def _parse_error_table(
        self, header: list[str], rows: list[list[str]], line: int
    ) -> list[ErrorCode]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, _ERROR_COLUMN_MAP)
            if col:
                col_map[col] = i
        if "code" not in col_map:
            self._warn(f"错误码表缺少code列，表头: {header}", line)
            return []
        return self._parse_error_table_with_cols(header, rows, line, col_map)

    def _parse_error_table_with_cols(
        self, header: list[str], rows: list[list[str]], line: int, col_map: dict[str, int]
    ) -> list[ErrorCode]:
        errors: list[ErrorCode] = []
        for row_idx, row in enumerate(rows):
            if len(row) < len(header):
                self._warn(f"错误码表第{row_idx + 1}行列数不匹配，跳过", line)
                continue
            if len(row) > len(header):
                row = row[:len(header)]
            code_val = row[col_map["code"]].strip()
            message = row[col_map["message"]].strip() if "message" in col_map else ""
            desc = row[col_map["description"]].strip() if "description" in col_map else ""
            try:
                code: str | int = int(code_val) if code_val.isdigit() else code_val
            except (ValueError, TypeError):
                code = code_val
            errors.append(ErrorCode(code=code, message=message, description=desc))
        return errors

    def _parse_mermaid_flowchart(self, content: str, pending_lists: list[Any]) -> None:
        m = _MERMAID_FLOWCHART_RE.search(content)
        if not m:
            return
        nodes: dict[str, DecisionNode] = {}
        edges: list[tuple[str, str, str]] = []

        def _first_nonempty(*groups: str | None) -> str:
            for g in groups:
                if g is not None:
                    return g.strip()
            return ""

        def _ensure_node(nid: str, label: str = "") -> None:
            if nid not in nodes:
                nodes[nid] = DecisionNode(id=nid, label=label or nid, edges=[])
            elif label and (not nodes[nid].label or nodes[nid].label == nid):
                nodes[nid].label = label

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("flowchart"):
                continue
            edge_m = _MERMAID_EDGE_RE.match(line)
            if edge_m:
                src = edge_m.group(1)
                src_label = _first_nonempty(edge_m.group(2), edge_m.group(3), edge_m.group(4), edge_m.group(5), edge_m.group(6))
                label = (edge_m.group(8) or "").strip()
                dst = edge_m.group(9)
                dst_label = _first_nonempty(edge_m.group(10), edge_m.group(11), edge_m.group(12), edge_m.group(13), edge_m.group(14))
                _ensure_node(src, src_label)
                _ensure_node(dst, dst_label)
                edges.append((src, dst, label))
                continue
            node_m = _MERMAID_NODE_RE.match(line)
            if node_m:
                nid = node_m.group(1)
                label = node_m.group(2).strip()
                _ensure_node(nid, label)

        for src, dst, label in edges:
            if src in nodes:
                nodes[src].edges.append((dst, label))
            if dst not in nodes:
                _ensure_node(dst)

        if nodes:
            pending_lists.append({
                "type": "mermaid_flowchart",
                "nodes": list(nodes.values()),
            })

    def _detect_webapi(self, doc: MDIDocument) -> bool:
        fm_type = doc.frontmatter.get("type", "")
        if isinstance(fm_type, str) and fm_type.lower() == "webapi":
            return True
        has_base_url = "baseurl" in doc.frontmatter or "baseUrl" in doc.frontmatter
        if has_base_url:
            return True
        return False

    def _extract_interfaces(self, doc: MDIDocument) -> None:
        def _walk(sections: list[Section]) -> None:
            for section in sections:
                self._extract_interfaces_from_section(section, doc)
                _walk(section.subsections)
        _walk(doc.sections)

    def _extract_interfaces_from_section(self, section: Section, doc: MDIDocument) -> None:
        if section.level != 3:
            return
        method = ""
        path = ""
        name = section.title
        m = _METHOD_PATH_RE.search(section.title)
        if m:
            method = m.group(1)
            path = m.group(2)
            name = section.title.replace(m.group(0), "").strip() or path
        else:
            m2 = _METHOD_PATH_RE.search(section.content)
            if m2:
                method = m2.group(1)
                path = m2.group(2)
        if not method or not path:
            return
        parameters: list[Parameter] = []
        responses: list[Response] = []
        errors: list[ErrorCode] = []
        examples: list[CodeBlock] = []
        for table in section.tables:
            if table["type"] == "parameter":
                parameters.extend(table.get("parsed_items", []))
            elif table["type"] == "response":
                responses.extend(table.get("parsed_items", []))
            elif table["type"] == "error":
                errors.extend(table.get("parsed_items", []))
        for cb in section.code_blocks:
            if cb.purpose in ("example", "mock", "request", "response"):
                examples.append(cb)
        self._infer_param_locations(parameters, path, method)
        iface = Interface(
            name=name,
            method=method,
            path=path,
            description=section.content[:200] if section.content else "",
            parameters=parameters,
            responses=responses,
            errors=errors,
            examples=examples,
        )
        doc.interfaces.append(iface)

    def _extract_interfaces_from_directives(self, blocks: list[dict], doc: MDIDocument) -> None:
        for idx, block in enumerate(blocks):
            if block.get("type") != "directive":
                continue
            dname = block.get("directive_name", "")
            if dname != "endpoint":
                continue
            args = block.get("args", "")
            options = block.get("options", {})
            options_optional = block.get("options_optional", {})
            body = block.get("body", "")
            line = block.get("line", 0)

            parts = args.split(None, 1)
            method = parts[0].upper() if parts else ""
            path = parts[1] if len(parts) > 1 else ""
            if not method:
                self._warn(f"endpoint directive缺少方法: {args}", line)
                continue
            if not path:
                self._warn(f"endpoint directive缺少路径/命令名: {args}", line)
                continue

            summary = options.get("summary", "")
            description = body
            tags_str = options.get("tags", "")
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

            parameters: list[Parameter] = []
            responses: list[Response] = []
            errors: list[ErrorCode] = []
            examples: list[CodeBlock] = []
            check_items: list[CheckItem] = []

            for opt_key, opt_val in options.items():
                if opt_key in ("summary", "tags", "deprecated", "name"):
                    continue
                is_optional = options_optional.get(opt_key, False)
                if opt_key.startswith("param"):
                    param = self._parse_directive_param(opt_key, opt_val, is_optional, line)
                    if param:
                        parameters.append(param)
                elif opt_key.startswith("query"):
                    param_name = opt_key[5:].strip() if len(opt_key) > 5 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "query"
                            parameters.append(param)
                elif opt_key.startswith("path"):
                    param_name = opt_key[4:].strip() if len(opt_key) > 4 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "path"
                            param.required = True
                            parameters.append(param)
                elif opt_key.startswith("body"):
                    param_name = opt_key[4:].strip() if len(opt_key) > 4 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "body"
                            parameters.append(param)
                    elif opt_key == "body":
                        pass
                elif opt_key.startswith("header"):
                    param_name = opt_key[6:].strip() if len(opt_key) > 6 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "header"
                            parameters.append(param)
                elif opt_key.startswith("response"):
                    resp = self._parse_directive_response(opt_key, opt_val, line)
                    if resp:
                        responses.append(resp)
                elif opt_key.startswith("error"):
                    err = self._parse_directive_error(opt_key, opt_val, line)
                    if err:
                        errors.append(err)

            existing_error_codes = {int(e.code) for e in errors if isinstance(e.code, int) or (isinstance(e.code, str) and e.code.isdigit())}
            for resp in responses:
                code_int = None
                try:
                    code_int = int(resp.status_code)
                except (ValueError, TypeError):
                    continue
                if code_int >= 400 and code_int not in existing_error_codes:
                    errors.append(ErrorCode(
                        code=code_int,
                        message="",
                        description=resp.description or f"HTTP {code_int}",
                    ))
                    existing_error_codes.add(code_int)

            context_hint = ""
            for nxt in blocks[idx + 1:]:
                if nxt.get("type") in ("heading", "directive"):
                    break
                if nxt.get("type") == "paragraph":
                    ptext = nxt.get("text", "")
                    if "请求" in ptext or "request" in ptext.lower():
                        context_hint = "request"
                    elif "响应" in ptext or "response" in ptext.lower():
                        context_hint = "response"
                    continue
                if nxt.get("type") == "list" and nxt.get("ordered") is False:
                    for item in nxt.get("items", []):
                        if item.get("is_task"):
                            check_items.append(CheckItem(
                                text=item.get("text", ""),
                                checked=bool(item.get("checked", False)),
                                line=nxt.get("line", 0),
                            ))
                    continue
                if nxt.get("type") == "block_code":
                    lang = nxt.get("language", "")
                    meta = nxt.get("meta", "")
                    content = nxt.get("content", "")
                    purpose = nxt.get("purpose", "") or self._detect_code_purpose(lang, meta)
                    if not purpose:
                        purpose = self._infer_code_purpose(lang, meta, content)
                    if not purpose and context_hint:
                        purpose = context_hint
                    if purpose == "example" and context_hint in ("request", "response"):
                        purpose = context_hint
                    if purpose in ("example", "mock", "request", "response", "test", "schema"):
                        cb = CodeBlock(language=lang, meta=meta, content=content, purpose=purpose)
                        examples.append(cb)

            name = options.get("name", "") or path
            self._infer_param_locations(parameters, path, method)
            iface = Interface(
                name=name,
                method=method,
                path=path,
                summary=summary,
                description=description,
                parameters=parameters,
                responses=responses,
                errors=errors,
                examples=examples,
                check_items=check_items,
                tags=tags,
            )
            doc.interfaces.append(iface)

    def _parse_directive_param(self, key: str, val: str, is_optional: bool, line: int) -> Parameter | None:
        name = key[5:].strip() if key.startswith("param") else key.strip()
        if not name:
            return None
        required = not is_optional
        ptype = "string"
        default = None
        desc = ""

        def _strip_optional(t: str) -> tuple[str, bool]:
            t = t.strip()
            opt = False
            if t.endswith("?"):
                t = t[:-1].strip()
                opt = True
            return t, opt

        type_match = re.match(r'^(\S+)\s*=\s*(.+?)\s*-\s*(.*)$', val)
        if type_match:
            raw_type = type_match.group(1)
            ptype, type_opt = _strip_optional(raw_type)
            if type_opt:
                required = False
            default = type_match.group(2).strip()
            desc = type_match.group(3).strip()
        else:
            type_match2 = re.match(r'^(\S+)\s*-\s*(.*)$', val)
            if type_match2:
                raw_type = type_match2.group(1)
                ptype, type_opt = _strip_optional(raw_type)
                if type_opt:
                    required = False
                desc = type_match2.group(2).strip()
            else:
                eq_match = re.match(r'^(.+?)\s*=\s*(.*)$', val)
                if eq_match:
                    default = eq_match.group(1).strip()
                    desc = eq_match.group(2).strip()
                else:
                    desc = val.strip()
        return Parameter(
            name=name,
            type=ptype,
            required=required,
            description=desc,
            default=default,
        )

    def _parse_directive_response(self, key: str, val: str, line: int) -> Response | None:
        code_str = key[8:].strip() if key.startswith("response") else key.strip()
        try:
            status_code: str | int = int(code_str) if code_str.isdigit() else code_str
        except (ValueError, TypeError):
            status_code = code_str
        desc = val.strip()
        schema_type = None
        schema_match = re.match(r'^(\w+)\s*-\s*(.*)$', val)
        if schema_match:
            schema_type = schema_match.group(1).strip()
            desc = schema_match.group(2).strip()
        return Response(status_code=status_code, description=desc)

    def _parse_directive_error(self, key: str, val: str, line: int) -> ErrorCode | None:
        code_str = key[5:].strip() if key.startswith("error") else key.strip()
        try:
            code: str | int = int(code_str) if code_str.isdigit() else code_str
        except (ValueError, TypeError):
            code = code_str
        msg = ""
        desc = val.strip()
        msg_match = re.match(r'^(.+?)\s*-\s*(.*)$', val)
        if msg_match:
            msg = msg_match.group(1).strip()
            desc = msg_match.group(2).strip()
        return ErrorCode(code=code, message=msg, description=desc)

    def _infer_param_locations(self, params: list[Parameter], path: str, method: str = "GET") -> None:
        """根据path模板和HTTP方法自动推断参数location。

        规则：
        1. 出现在path中的{param}标记为path location，强制required=True
        2. GET/HEAD/DELETE/OPTIONS请求的非path参数默认为query location
        3. POST/PUT/PATCH请求的非path参数保持默认body location
        4. 已显式设置location（非body默认值）的参数不被覆盖
        """
        import re as _re
        path_param_names = set(_re.findall(r'\{(\w+)\}', path))
        path_param_set = set()

        query_methods = {"GET", "HEAD", "DELETE", "OPTIONS"}
        default_loc = "query" if method.upper() in query_methods else "body"

        for p in params:
            if p.name in path_param_names:
                p.location = "path"
                p.required = True
                path_param_set.add(p.name)
            elif p.location == "body":
                p.location = default_loc

        body_duplicates = [i for i, p in enumerate(params) if p.location == "body" and p.name in path_param_set]
        for i in reversed(body_duplicates):
            params.pop(i)
