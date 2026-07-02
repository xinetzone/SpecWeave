"""MCP Domain for MyST Markdown - 数据模型与解析器。

实现报告第9章中提出的"文档即MCP Server"原型：
从使用 mcp: 前缀 directive 的 MyST 文档中解析 MCP Server 定义。

支持两种围栏语法：
1. 冒号围栏（MyST 标准），内层使用更多冒号::
    :::{mcp:server} server-name      <- 3 colons (outermost)
    :version: 1.0.0
    :transport: stdio

    服务器描述文本。

    ::::{mcp:tool} tool-name        <- 4 colons (nested)
    :description: 工具描述
    ::::
    :::

2. 反引号围栏（通用 Markdown 兼容），内层通过围栏深度计数嵌套:
    ```{mcp:server} server-name
    :version: 1.0.0

    服务器描述文本。

    ```{mcp:tool} tool-name
    :description: 工具描述
    ```
    ```

Directive 类型：
- mcp:server  — 服务器根定义，内含 tool/resource/prompt
- mcp:tool    — 工具定义，内含 mcp:param/mcp:arg
- mcp:resource — 资源定义，支持 :uri: :mime-type: 选项，body 为资源内容
- mcp:prompt  — 提示模板定义，内含 mcp:param/mcp:arg，body 为模板文本
- mcp:param   — 工具/提示的参数定义
- mcp:arg     — mcp:param 的别名（提示参数语义更清晰）
"""

from __future__ import annotations

import json as _json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from markdown_it import MarkdownIt
    from mdit_py_plugins.colon_fence import colon_fence_plugin
    from mdit_py_plugins.front_matter import front_matter_plugin
    HAS_MDIT = True
except ImportError:
    HAS_MDIT = False


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

@dataclass
class McpParam:
    """MCP 工具/提示的参数定义。"""
    name: str
    type: str = "string"
    required: bool = True
    description: str = ""
    default: str | None = None
    enum: list[str] = field(default_factory=list)


@dataclass
class McpTool:
    """MCP Tool 定义。"""
    name: str
    description: str = ""
    params: list[McpParam] = field(default_factory=list)
    body: str = ""


@dataclass
class McpResource:
    """MCP Resource 定义。"""
    uri: str = ""
    name: str = ""
    description: str = ""
    mime_type: str = "text/plain"
    body: str = ""


@dataclass
class McpPrompt:
    """MCP Prompt 定义。"""
    name: str = ""
    description: str = ""
    arguments: list[McpParam] = field(default_factory=list)
    template: str = ""


@dataclass
class McpServer:
    """MCP Server 定义，从 MyST 文档解析的根对象。"""
    name: str = "myst-mcp-server"
    version: str = "0.1.0"
    description: str = ""
    transport: str = "stdio"
    tools: list[McpTool] = field(default_factory=list)
    resources: list[McpResource] = field(default_factory=list)
    prompts: list[McpPrompt] = field(default_factory=list)
    source_path: Path | None = None


# ---------------------------------------------------------------------------
# 正则与辅助
# ---------------------------------------------------------------------------

_DIRECTIVE_RE = re.compile(r'^\{(\w[\w:.-]*)\}\s*(.*)$')
_OPTION_RE = re.compile(r'^:([\w][\w\s\-]*?)(\??)\s*:\s*(.*)$')
_COLON_OPEN_RE = re.compile(r'^(:{3,})(\{[\w][\w:.-]*\})\s*(.*)$')
_COLON_CLOSE_RE = re.compile(r'^(:{3,})\s*$')
_BACKTICK_OPEN_RE = re.compile(r'^(`{3,})(\{[\w][\w:.-]*\})\s*(.*)$')
_BACKTICK_CLOSE_RE = re.compile(r'^(`{3,})\s*$')

_JSON_SCHEMA_TYPE_MAP: dict[str, dict[str, Any]] = {
    "string": {"type": "string"},
    "str": {"type": "string"},
    "integer": {"type": "integer"},
    "int": {"type": "integer"},
    "number": {"type": "number"},
    "float": {"type": "number"},
    "boolean": {"type": "boolean"},
    "bool": {"type": "boolean"},
    "array": {"type": "array", "items": {"type": "string"}},
    "object": {"type": "object"},
}

_PY_TYPE_MAP: dict[str, type] = {
    "string": str, "str": str,
    "integer": int, "int": int,
    "number": float, "float": float,
    "boolean": bool, "bool": bool,
    "array": list,
    "object": dict,
}


def _make_parser() -> "MarkdownIt":
    return MarkdownIt("commonmark").use(front_matter_plugin).use(colon_fence_plugin)


def _parse_options(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """从行列表中解析 :key: value 选项，返回 (选项dict, 剩余内容行)。"""
    options: dict[str, str] = {}
    remaining: list[str] = []
    for line in lines:
        m = _OPTION_RE.match(line.strip())
        if m:
            key = m.group(1).strip().lower().replace(" ", "-")
            optional = bool(m.group(2))
            val = m.group(3).strip()
            if optional:
                options["required"] = "false"
            options[key] = val
        else:
            remaining.append(line)
    return options, remaining


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """提取 YAML frontmatter（简易实现，不依赖 PyYAML）。

    返回 (metadata_dict, remaining_text)。仅支持简单的 key: value 标量。
    """
    meta: dict[str, str] = {}
    if not text.startswith("---\n"):
        return meta, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return meta, text
    fm_text = text[4:end]
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().lower()
            val = val.strip().strip('"').strip("'")
            if val:
                meta[key] = val
    return meta, text[end + 5:]


# ---------------------------------------------------------------------------
# 围栏块解析（同时支持冒号围栏和反引号围栏）
# ---------------------------------------------------------------------------

def _parse_fence_blocks(text: str) -> list[dict[str, Any]]:
    """递归解析文本中的 ::: 和 ``` 围栏块，返回 directive 列表。

    使用栈跟踪嵌套围栏：
    - 冒号围栏：内层必须使用更多冒号（MyST 规范），长度匹配开闭
    - 反引号围栏：通过深度计数嵌套（同 markdown-it 行为）
    """
    lines = text.split("\n")

    def parse_colon(start: int, min_fence_len: int) -> tuple[list[dict[str, Any]], int]:
        """解析冒号围栏块。"""
        results: list[dict[str, Any]] = []
        i = start
        while i < len(lines):
            line = lines[i]
            cm = _COLON_OPEN_RE.match(line)
            ccm = _COLON_CLOSE_RE.match(line)

            if cm and not ccm:
                fence_len = len(cm.group(1))
                if fence_len < min_fence_len:
                    i += 1
                    continue
                info = (cm.group(2) + " " + cm.group(3)).strip()
                dm = _DIRECTIVE_RE.match(info)
                if dm:
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    i += 1
                    inner_start = i
                    children, i = parse_colon(i, fence_len + 1)
                    inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                    options, content_lines = _parse_options(inner_lines)
                    content = "\n".join(content_lines).strip()
                    results.append({
                        "name": directive_name,
                        "args": directive_args,
                        "options": options,
                        "content": content,
                        "children": children,
                        "fence_type": "colon",
                    })
                    continue
            elif ccm:
                fence_len = len(ccm.group(1))
                if fence_len >= min_fence_len - 1 and min_fence_len > 3:
                    return results, i + 1
            i += 1
        return results, i

    def parse_backtick(start: int) -> tuple[list[dict[str, Any]], int]:
        """解析反引号围栏块，通过深度计数处理嵌套。

        与冒号围栏不同：反引号开闭都用 ``` ，通过深度计数器嵌套。
        返回 (children_directives, end_position)。
        调用方负责通过行范围提取内容。
        """
        children: list[dict[str, Any]] = []
        i = start
        depth = 1
        while i < len(lines):
            line = lines[i]
            is_close = bool(_BACKTICK_CLOSE_RE.match(line)) and not bool(_BACKTICK_OPEN_RE.match(line))
            is_open = bool(_BACKTICK_OPEN_RE.match(line))

            if is_close:
                depth -= 1
                if depth == 0:
                    return children, i + 1
                i += 1
            elif is_open:
                bm = _BACKTICK_OPEN_RE.match(line)
                info = (bm.group(2) + " " + bm.group(3)).strip()
                dm = _DIRECTIVE_RE.match(info)
                if dm:
                    depth += 1
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    i += 1
                    inner_start = i
                    grandkids, i = parse_backtick(i)
                    inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                    opts, clines = _parse_options(inner_lines)
                    c = "\n".join(clines).strip()
                    children.append({
                        "name": directive_name,
                        "args": directive_args,
                        "options": opts,
                        "content": c,
                        "children": grandkids,
                        "fence_type": "backtick",
                    })
                else:
                    i += 1
            else:
                i += 1
        return children, i

    def parse_mixed(start: int, min_colon_len: int) -> tuple[list[dict[str, Any]], int]:
        """顶层混合解析：同时识别冒号围栏和反引号围栏。"""
        results: list[dict[str, Any]] = []
        i = start
        while i < len(lines):
            line = lines[i]
            cm = _COLON_OPEN_RE.match(line)
            bm = _BACKTICK_OPEN_RE.match(line)
            ccm = _COLON_CLOSE_RE.match(line)

            if cm and not ccm:
                fence_len = len(cm.group(1))
                if fence_len >= min_colon_len:
                    info = (cm.group(2) + " " + cm.group(3)).strip()
                    dm = _DIRECTIVE_RE.match(info)
                    if dm:
                        directive_name = dm.group(1).lower()
                        directive_args = dm.group(2).strip()
                        i += 1
                        inner_start = i
                        children, i = parse_colon(i, fence_len + 1)
                        inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                        options, content_lines = _parse_options(inner_lines)
                        content = "\n".join(content_lines).strip()
                        results.append({
                            "name": directive_name,
                            "args": directive_args,
                            "options": options,
                            "content": content,
                            "children": children,
                            "fence_type": "colon",
                        })
                        continue
            elif bm:
                info = (bm.group(2) + " " + bm.group(3)).strip()
                dm = _DIRECTIVE_RE.match(info)
                if dm:
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    i += 1
                    inner_start = i
                    children, i = parse_backtick(i)
                    inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                    options, content_lines = _parse_options(inner_lines)
                    content = "\n".join(content_lines).strip()
                    results.append({
                        "name": directive_name,
                        "args": directive_args,
                        "options": options,
                        "content": content,
                        "children": children,
                        "fence_type": "backtick",
                    })
                    continue
            elif ccm and min_colon_len > 3:
                fence_len = len(ccm.group(1))
                if fence_len >= min_colon_len - 1:
                    return results, i + 1
            i += 1
        return results, i

    parsed, _ = parse_mixed(0, 3)
    return parsed


# ---------------------------------------------------------------------------
# 主解析函数
# ---------------------------------------------------------------------------

def parse_myst_mcp(content: str, source_path: Path | None = None) -> McpServer | None:
    """解析 MyST 格式的 MCP 文档，返回 McpServer 对象。

    同时支持冒号围栏（:::{mcp:server}）和反引号围栏（```{mcp:server}）语法。
    不依赖 markdown-it-py（纯 Python 正则解析），也不需要可选依赖即可工作。
    """
    meta, body_text = _parse_frontmatter(content)

    server = McpServer(source_path=source_path)
    if meta.get("name"):
        server.name = meta["name"]
    if meta.get("version"):
        server.version = meta["version"]
    if meta.get("description"):
        server.description = meta["description"]
    if meta.get("transport"):
        server.transport = meta["transport"].lower()

    all_blocks = _parse_fence_blocks(body_text)

    found_server = False
    for block in all_blocks:
        if block["name"] == "mcp:server":
            if found_server:
                _warn(source_path, 0, "multiple mcp:server directives, using first")
                continue
            found_server = True
            if block["args"]:
                server.name = block["args"]
            _apply_server_options(server, block["options"], block["content"])
            _process_server_children(server, block["children"], block["content"], source_path)

    if not found_server:
        return None
    return server


def _process_server_children(
    server: McpServer,
    children: list[dict],
    server_content: str,
    source: Path | None,
):
    """处理 server 的子 directives。"""
    for child in children:
        name = child["name"]
        args = child["args"]
        options = child["options"]
        content = child["content"]
        grandkids = child["children"]

        if name == "mcp:tool":
            tool = McpTool(name=args or "unnamed_tool")
            if "description" in options:
                tool.description = options["description"]
            else:
                tool.description = content[:200] if content else ""
            tool.body = content
            _add_params_to(tool.params, grandkids)
            server.tools.append(tool)

        elif name == "mcp:resource":
            uri = options.get("uri", args or f"resource://{server.name}/{args or 'unnamed'}")
            res_name = options.get("name", args or uri.split("/")[-1] if "/" in uri else uri)
            res = McpResource(
                uri=uri,
                name=res_name,
                description=options.get("description", content[:200] if content else ""),
                mime_type=options.get("mime-type", options.get("mimetype", "text/plain")),
                body=content,
            )
            server.resources.append(res)

        elif name == "mcp:prompt":
            prompt = McpPrompt(name=args or "unnamed_prompt")
            if "description" in options:
                prompt.description = options["description"]
            else:
                prompt.description = content[:200] if content else ""
            _add_params_to(prompt.arguments, grandkids, allow_arg_alias=True)
            prompt.template = content
            server.prompts.append(prompt)


def _add_params_to(
    target: list[McpParam],
    children: list[dict],
    *,
    allow_arg_alias: bool = False,
):
    """从子 directives 中提取参数列表。

    当 allow_arg_alias=True 时，mcp:arg 作为 mcp:param 的别名被接受。
    """
    valid_names = {"mcp:param"}
    if allow_arg_alias:
        valid_names.add("mcp:arg")

    for child in children:
        if child["name"] not in valid_names:
            continue
        param = McpParam(name=child["args"] or "unnamed")
        opts = child["options"]
        if "type" in opts:
            param.type = opts["type"]
        if "required" in opts:
            param.required = opts["required"].lower() not in ("false", "no", "0", "optional")
        elif "optional" in opts:
            param.required = False
        if "default" in opts:
            param.default = opts["default"]
        if "enum" in opts:
            param.enum = [v.strip().strip('"\'') for v in opts["enum"].split(",") if v.strip()]
        desc = child["content"].strip()
        if desc and "description" not in opts:
            param.description = desc
        elif "description" in opts:
            param.description = opts["description"]
        target.append(param)


def _apply_server_options(server: McpServer, options: dict[str, str], content: str):
    """应用 server 级选项。"""
    if "version" in options:
        server.version = options["version"]
    if "transport" in options:
        server.transport = options["transport"].lower()
    if content and not server.description:
        server.description = content


def _warn(source: Path | None, line: int, msg: str):
    src = str(source) if source else "<string>"
    print(f"[WARN] {src}:{line}: {msg}", file=__import__("sys").stderr)


# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------

def parse_file(path: str | Path) -> McpServer | None:
    """从 MyST 文件解析 MCP Server 定义。"""
    p = Path(path)
    content = p.read_text(encoding="utf-8")
    return parse_myst_mcp(content, p)


def build_input_schema(tool: McpTool) -> dict[str, Any]:
    """将 McpTool.params 转换为 MCP JSON Schema。"""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in tool.params:
        prop = _json_schema_type(p.type)
        if p.description:
            prop["description"] = p.description
        if p.default is not None:
            prop["default"] = _cast_value(p.default, p.type)
        if p.enum:
            prop["enum"] = list(p.enum)
        properties[p.name] = prop
        if p.required:
            required.append(p.name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema


def py_type(type_str: str) -> type:
    """将 MCP 类型字符串映射为 Python 类型。"""
    type_str = type_str.strip().lower()
    if type_str.startswith("array<"):
        return list
    return _PY_TYPE_MAP.get(type_str, str)


def json_schema_type(type_str: str) -> dict[str, Any]:
    """将类型字符串映射为 JSON Schema 片段。"""
    return dict(_json_schema_type(type_str))


def _json_schema_type(type_str: str) -> dict[str, Any]:
    type_str = type_str.strip().lower()
    if type_str.startswith("array<"):
        inner = type_str[6:-1] if type_str.endswith(">") else "string"
        return {"type": "array", "items": _json_schema_type(inner)}
    return dict(_JSON_SCHEMA_TYPE_MAP.get(type_str, {"type": "string"}))


def cast_value(val: Any, type_str: str) -> Any:
    """将字符串值转换为对应 Python 类型。"""
    if val is None:
        return None
    if isinstance(val, str):
        t = py_type(type_str)
        try:
            if t is bool:
                return val.lower() in ("true", "1", "yes")
            if t is list:
                return _json.loads(val) if val.startswith("[") else [x.strip() for x in val.split(",")]
            return t(val)
        except (ValueError, TypeError, _json.JSONDecodeError):
            return val
    return val


# 别名兼容：PoC 旧名称
_cast_value = cast_value
_json_schema_type = _json_schema_type  # type: ignore[no-redef]  # noqa: E305
