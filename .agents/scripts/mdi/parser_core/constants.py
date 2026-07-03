from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
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

logger = logging.getLogger(__name__)

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
