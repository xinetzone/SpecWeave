---
version: 1.0
id: myst-unified-ecosystem-implementation
title: "06、Implementation：具体实现"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/myst-unified-ecosystem/06-implementation.toml"
---
# 06、Implementation：具体实现

## 概念模板

| 字段 | 内容 |
|------|------|
| **名称** | Implementation（具体实现） |
| **分类层** | 设计抽象层 (Design) |
| **核心定义** | 接口或协议的具体编码实现，定义"如何做" |
| **解决的问题** | 将抽象契约转化为可执行的代码 |
| **关键属性** | `name`、`implements`（引用目标）、`language`、`runtime`、`repository`、`version` |
| **关系** | implements → Interface/Protocol；constrained-by → ABI；described-by → IDL；carried-by → MDI |
| **MyST Directive** | `{implementation} of="..." lang="..."` |
| **MDI 示例** | `{implementation} of="MCP" lang="Python"` 包裹实现仓库、运行时要求、版本信息 |

## 核心定义

Implementation 是设计抽象层中**唯一直接产出可执行代码**的概念。它承担着将抽象契约（Interface/Protocol）转化为具体运行实体的职责。Implementation 实现了 Interface 或 Protocol（implements 关系），同时受 ABI 约束（constrained-by 关系），确保编译或运行时的兼容性。

Implementation 在四个概念中处于"兑现承诺"的位置：Interface 声明契约，Protocol 定义规则，API 暴露端点，ABI 约束兼容性，而 Implementation 是这一切的**编码落地**。

## Implementation 与 Interface/Protocol 的 implements 关系

### implements 关系的本质

```
Interface ("calculate" 能力契约)
    ▲
    │ implements
    │
Implementation ("calculator-server" v1.0.0, Python)
```

implements 关系意味着：
- **契约兑现**：Implementation 必须完整实现 Interface 声明的所有行为——Interface 定义的每个参数、每个返回值、每个错误都必须有对应的代码处理
- **多对一映射**：一个 Interface 可以有多个 Implementation（例如同一个 MCP Tool 接口可以用 Python、Node.js、Go 分别实现）
- **可替换性**：只要遵守相同的 Interface，不同 Implementation 可以互相替换，调用方无需感知差异

### 实现 Protocol 的场景

当 Implementation 的目标是 Protocol 时，它需要实现 Protocol 组合的全部内容——API 方法 + ABI 序列化约定 + 握手流程 + 状态机 + 错误处理。例如，一个 MCP Server 实现实质上实现了 MCP Protocol 的全部规范。

## 受 ABI constrains 的约束说明

constrains 关系是 ABI 对 Implementation 的**硬约束**。Implementation 在编码时必须遵守其声明的 ABI 约定：

| ABI 约束 | Implementation 必须遵守 |
|---------|----------------------|
| `data_format: JSON` | 所有消息必须序列化为合法 JSON |
| `encoding: UTF-8` | 字节流必须使用 UTF-8 编码 |
| `transport: STDIO` | 通过标准输入输出通信，不使用网络端口 |
| `transport: HTTP` | 必须监听 HTTP 端点，接受 POST 请求 |
| `calling_convention: JSON-RPC 2.0` | 消息必须包含 `jsonrpc`、`method`、`id`/`params` 字段 |

违反 ABI 约束的后果：如果 Implementation 声称使用 JSON ABI 却产出了非 JSON 格式的输出，Client 端将无法解析，导致通信失败。这与传统 ABI 中调用约定不匹配导致段错误的逻辑一致——只是错误更加可控（JSON 解析失败 vs 内存访问违规）。

## MCP Server 实现作为示例

以下是最简 MCP Server 实现的核心结构，展示 Implementation 如何兑现 Interface + Protocol + ABI 三个层次的承诺：

```python
# MCP Server Implementation (Python)
# implements: MCP Protocol
# constrained-by: JSON ABI + STDIO transport

from mcp.server.fastmcp import FastMCP

# 1. 实例化 Server（兑现 Protocol 的握手/生命周期）
mcp = FastMCP("calculator-server")

# 2. 注册 Tool（兑现 Interface 的行为契约）
@mcp.tool()
def calculate(expression: str, precision: int = 2) -> str:
    """执行数学计算，支持加减乘除和基本函数"""
    result = eval(expression)  # 简化示例
    return f"{result:.{precision}f}"

# 3. 启动 Server（兑现 ABI 的传输约定）
# STDIO 传输：stdin 读取 JSON-RPC 请求，stdout 输出 JSON-RPC 响应
mcp.run(transport="stdio")
```

这个实现同时兑现了三层承诺：
- **Interface 层**：`calculate` 函数实现了"数学计算"的能力契约（输入 `expression` + `precision`，输出 `str`）
- **Protocol 层**：`FastMCP` 框架自动处理 `initialize` 握手、`tools/list` 发现、错误响应格式
- **ABI 层**：`transport="stdio"` 确保所有消息通过 STDIO 管道以 JSON 格式传输，与任何语言编写的 Client 兼容

## 章节导航

| 章节 | 内容 |
|------|------|
| [00 - 总览](00-overview.md) | 可行性分析、架构图、关系全景 |
| [01 - IDL](01-idl.md) | 接口描述语言：元概念层定义 |
| [02 - Interface](02-interface.md) | 接口：行为契约的抽象声明 |
| [03 - API](03-api.md) | 应用程序编程接口：可调用方法端点 |
| [04 - ABI](04-abi.md) | 应用程序二进制接口：二进制兼容约定 |
| [05 - Protocol](05-protocol.md) | 协议：完整通信规则集 |
| [06 - Implementation](06-implementation.md) | 实现：接口/协议的具体编码（当前章节） |
| [07 - MCP](07-mcp.md) | Model Context Protocol：Agent↔Tool 连接 |
| [08 - ACP](08-acp.md) | Agent Communication Protocol：本地 P2P |
| [09 - A2A](09-a2a.md) | Agent-to-Agent：跨组织协作 |
| [10 - ANP](10-anp.md) | Agent Network Protocol：去中心化网络 |
| [11 - MDI](11-mdi.md) | Markdown Document Interface：载体层 |
| [12 - 关系全景](12-relationships.md) | 7 类关系定义、关系矩阵、交互场景 |

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：Implementation 具体实现定义与三层承诺模型