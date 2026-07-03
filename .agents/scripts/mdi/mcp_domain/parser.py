"""MCP Domain MyST 文档主解析器。
STATUS: UNVERIFIED - 未经实战验证，参考pytest_gen/mdi.parser使用
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import (
    _DIRECTIVE_RE,
    _COLON_OPEN_RE,
    _COLON_CLOSE_RE,
    _BACKTICK_OPEN_RE,
    _BACKTICK_CLOSE_RE,
)
from .models import (
    McpServer,
    McpTool,
    McpResource,
    McpPrompt,
    McpParam,
)
from .parser_helpers import _parse_options, _parse_frontmatter
from .fence_parser import parse_fence_blocks


def _warn(source: Path | None, line: int, msg: str):
    src = str(source) if source else "<string>"
    print(f"[WARN] {src}:{line}: {msg}", file=__import__("sys").stderr)


def _strip_nested_directives(text: str) -> str:
    """从内容文本中移除嵌套的 directive 围栏块（:::{} 和 ```{}），返回干净内容。

    用于从 tool/prompt/resource 的 body 中排除嵌套的 mcp:param/mcp:arg 等指令块，
    保留纯描述/模板文本。
    """
    if not text:
        return ""
    lines = text.split("\n")
    result: list[str] = []
    depth = 0
    for line in lines:
        is_colon_open = bool(_COLON_OPEN_RE.match(line))
        is_bt_open = bool(_BACKTICK_OPEN_RE.match(line)) and bool(
            _DIRECTIVE_RE.match(
                (_BACKTICK_OPEN_RE.match(line).group(2) + " " +
                 _BACKTICK_OPEN_RE.match(line).group(3)).strip()
            )
        ) if _BACKTICK_OPEN_RE.match(line) else False
        is_colon_close = bool(_COLON_CLOSE_RE.match(line))
        is_bt_close = bool(_BACKTICK_CLOSE_RE.match(line)) and not bool(_BACKTICK_OPEN_RE.match(line))

        if is_colon_open or is_bt_open:
            depth += 1
            continue
        if is_colon_close or is_bt_close:
            if depth > 0:
                depth -= 1
                continue
        if depth == 0:
            result.append(line)
    return "\n".join(result).strip()


def _apply_server_options(server: McpServer, options: dict[str, str], content: str):
    """应用 server 级选项。"""
    if "version" in options:
        server.version = options["version"]
    if "transport" in options:
        server.transport = options["transport"].lower()
    if content and not server.description:
        server.description = content


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
            clean_body = _strip_nested_directives(content)
            if "description" in options:
                tool.description = options["description"]
            else:
                tool.description = clean_body[:200] if clean_body else ""
            tool.body = clean_body
            _add_params_to(tool.params, grandkids)
            server.tools.append(tool)

        elif name == "mcp:resource":
            uri = options.get("uri", args or f"resource://{server.name}/{args or 'unnamed'}")
            res_name = options.get("name", args or uri.split("/")[-1] if "/" in uri else uri)
            clean_body = _strip_nested_directives(content)
            res = McpResource(
                uri=uri,
                name=res_name,
                description=options.get("description", clean_body[:200] if clean_body else ""),
                mime_type=options.get("mime-type", options.get("mimetype", "text/plain")),
                body=clean_body,
            )
            server.resources.append(res)

        elif name == "mcp:prompt":
            prompt = McpPrompt(name=args or "unnamed_prompt")
            clean_body = _strip_nested_directives(content)
            if "description" in options:
                prompt.description = options["description"]
            else:
                prompt.description = clean_body[:200] if clean_body else ""
            _add_params_to(prompt.arguments, grandkids, allow_arg_alias=True)
            prompt.template = clean_body
            server.prompts.append(prompt)


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

    all_blocks = parse_fence_blocks(body_text)

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
