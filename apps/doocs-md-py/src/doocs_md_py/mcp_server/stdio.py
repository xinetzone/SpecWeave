"""MCP stdio 传输层（换行分隔的 JSON-RPC 2.0）。

实现路径决策（T18 I 阶段，依据 spec A6 回退条款）：venv 实测 ``mcp`` 为 2.3.0，
v2 已删除上游 1:1 复刻所依赖的 ``mcp.server.fastmcp``（导入即抛 ModuleNotFoundError
并提示改名 ``mcp.server.mcpserver.MCPServer``），且 v1 的内存直连测试助手
``create_connected_server_and_client_session`` 亦已不存在；而原先声明的 ``mcp>=1.2``
上下界既无法表达「必须是 v1 形态」，该包又会拖入 ``cryptography`` 等白名单外依赖。
故按 MCP 规范手写最小传输层：零新增运行时依赖、
入参校验与 payload 字面值可逐字控制、可在进程内以真实 JSON-RPC 帧断言
initialize/tools/list/tools/call。

依赖状态：``mcp`` 已从 ``pyproject.toml`` 运行期依赖中移除（T18 决策），本次替换登记为
行为差异 ``CD-21``（见 ``docs/contract-differences.md`` §7.10 第 ⑥ 条）；运行期白名单为
8 项、不含 ``mcp``（见 ``.agents/rules/engineering-redlines.md`` §2）。

upstream: packages/mcp-server/src/index.ts:139-441（McpServer + StdioServerTransport）
"""

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import IO, Any, BinaryIO

from .tools import (
    SERVER_NAME,
    SERVER_VERSION,
    TOOLS_BY_NAME,
    ToolInputError,
    call_tool,
    list_tools_payload,
)

JSONRPC_VERSION = "2.0"

# JSON-RPC 2.0 错误码
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602

# 协商版本：命中客户端请求值则回显，否则回退到最新支持版本
SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
DEFAULT_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]

# upstream: index.ts:436
STARTUP_LINE = "[md-mcp-server] running on stdio"

# upstream: index.ts:440（fatal 行前缀）
FATAL_PREFIX = "[md-mcp-server] fatal:"


def json_dumps(value: Any) -> str:
    """upstream: index.ts:139-143 ``JSON.stringify`` 等价（紧凑分隔符、不转义非 ASCII）。"""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _content_result(payload_text: str, *, is_error: bool = False) -> dict[str, Any]:
    """upstream: index.ts:139-143 ``{content:[{type:'text', text}]}``。"""
    result: dict[str, Any] = {"content": [{"type": "text", "text": payload_text}]}
    if is_error:
        result["isError"] = True
    return result


@dataclass(slots=True)
class McpStdioServer:
    """单连接 MCP 服务：消息分发与 stdio 主循环。"""

    code_css_fetcher: Callable[[str], str] | None = None
    protocol_version: str = DEFAULT_PROTOCOL_VERSION

    # ---- 信封 ----
    @staticmethod
    def _result(message_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": JSONRPC_VERSION, "id": message_id, "result": result}

    @staticmethod
    def _error(message_id: Any, code: int, message: str) -> dict[str, Any]:
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": message_id,
            "error": {"code": code, "message": message},
        }

    def _negotiate(self, params: Any) -> str:
        requested = params.get("protocolVersion") if isinstance(params, dict) else None
        if isinstance(requested, str) and requested in SUPPORTED_PROTOCOL_VERSIONS:
            return requested
        return DEFAULT_PROTOCOL_VERSION

    # ---- 方法分发 ----
    def handle_message(self, message: Any) -> dict[str, Any] | None:
        """处理单条 JSON-RPC 消息；通知（无 id）且无需应答时返回 None。"""
        if not isinstance(message, dict) or not isinstance(message.get("method"), str):
            return self._error(None, INVALID_REQUEST, "Invalid Request")

        method = message["method"]
        message_id = message.get("id")

        if method == "initialize":
            result = {
                "protocolVersion": self._negotiate(message.get("params")),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            }
            return self._result(message_id, result)
        if method == "tools/list":
            return self._result(message_id, {"tools": list_tools_payload()})
        if method == "tools/call":
            return self._handle_call_tool(message_id, message.get("params"))
        if method == "ping":
            return self._result(message_id, {})
        if "id" not in message:
            # notifications/initialized、notifications/cancelled 等通知按 JSON-RPC 静默
            return None
        return self._error(message_id, METHOD_NOT_FOUND, f"Method not found: {method}")

    def _handle_call_tool(self, message_id: Any, params: Any) -> dict[str, Any]:
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return self._error(message_id, INVALID_PARAMS, "Invalid params")
        name = params["name"]
        if name not in TOOLS_BY_NAME:
            return self._error(message_id, INVALID_PARAMS, f"Unknown tool: {name}")

        arguments = params.get("arguments")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return self._error(message_id, INVALID_PARAMS, "Invalid params: arguments must be an object")

        try:
            payload = call_tool(name, arguments, code_css_fetcher=self.code_css_fetcher)
        except ToolInputError as err:
            return self._result(message_id, _content_result("\n".join(err.messages), is_error=True))
        except Exception as err:  # MCP 规范：工具执行错误以 isError 结果返回
            return self._result(
                message_id,
                _content_result(f"{type(err).__name__}: {err}", is_error=True),
            )
        return self._result(message_id, _content_result(json_dumps(payload)))

    # ---- 传输 ----
    def handle_line(self, raw: bytes) -> dict[str, Any] | None:
        """解析一行并分发；坏 JSON 按 -32700 报错。"""
        try:
            message = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._error(None, PARSE_ERROR, "Parse error")
        return self.handle_message(message)

    def serve(
        self,
        reader: BinaryIO,
        writer: BinaryIO,
        *,
        stderr: IO[str] | None = None,
    ) -> int:
        """stdin/stdout 主循环（upstream: index.ts:433-437）。"""
        sink = stderr if stderr is not None else sys.stderr
        sink.write(STARTUP_LINE + "\n")
        sink.flush()

        for raw in reader:
            line = raw.strip()
            if not line:
                continue
            response = self.handle_line(line)
            if response is None:  # 通知无应答
                continue
            writer.write(json_dumps(response).encode("utf-8") + b"\n")
            writer.flush()
        return 0

    def main(self) -> int:
        """进程入口；异常按 upstream 打印 fatal 行并返回 1。"""
        try:
            return self.serve(sys.stdin.buffer, sys.stdout.buffer)
        except Exception as err:  # upstream: index.ts:439-442
            sys.stderr.write(f"{FATAL_PREFIX} {err}\n")
            sys.stderr.flush()
            return 1


def main() -> int:
    """mdpy mcp / python -m doocs_md_py.mcp_server 的入口。"""
    return McpStdioServer().main()
