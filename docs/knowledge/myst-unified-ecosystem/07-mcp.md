---
version: 1.0
id: myst-ecosystem-mcp
title: "07、MCP：Model Context Protocol"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../.meta/toml/docs/knowledge/myst-unified-ecosystem/07-mcp.toml"
---
# 07、MCP：Model Context Protocol

## 概念模板

| 字段 | 内容 |
|------|------|
| **名称** | MCP（Model Context Protocol，模型上下文协议） |
| **分类层** | 协议实例层 (Instance) |
| **核心定义** | Agent 与外部工具/数据源之间的标准化连接协议，Agent 生态的"USB-C 接口"，协议栈 L1 层 |
| **解决的问题** | 统一 Agent 调用外部工具的接口，解决 N×M 工具集成碎片化问题：每个 Agent 框架各自定义工具调用方式，导致同一工具需为不同框架重复开发适配器 |
| **关键属性** | version: `2024-11-05`; transport: `stdio` / `Streamable HTTP` / `SSE`; message_format: `JSON-RPC 2.0`; architecture: `Client-Server`; security: `stdio 天然安全` / `远程 OAuth 2.1`; primitives: `Tools` / `Resources` / `Prompts`; governance: `Linux 基金会` |
| **关系** | `instantiates` → Protocol; `described-by` → IDL; `carried-by` → MDI |
| **MyST Directive** | `{protocol} type="mcp" version="2024-11-05"` |
| **MDI 示例** | 见下文"MDI 示例"章节 |

## 1. 协议概述

MCP 由 Anthropic 于 2024 年 11 月发布，2025 年捐赠给 Linux 基金会进行中立治理，是四层协议栈中最成熟、应用最广泛的协议。目前已覆盖数千个现成 MCP Server，主流 IDE（Claude Desktop、Cursor、Windsurf、VS Code）原生支持。

### 核心定位：纵向连接层

MCP 解决的是**纵向连接**问题——Agent 如何像计算机通过 USB-C 连接外设一样，标准化地连接各类工具、数据库、文件系统和 SaaS 服务。与 ACP/A2A/ANP 的横向 Agent-Agent 通信有本质区别：MCP 的通信对象是**被动执行的工具**，而非自主决策的智能体。

## 2. 三大核心原语

| 原语 | 类型 | 操作性质 | 用途 |
|------|------|---------|------|
| **Tools** | 可执行函数 | 可读写/有副作用 | 写操作、调用 API、计算、触发副作用 |
| **Resources** | URI 寻址数据 | 只读 | 读文件、查数据库、获取 API 响应 |
| **Prompts** | 模板 | 生成提示词 | 标准化常见任务提示词、封装领域知识 |

## 3. 架构设计

MCP 采用 Client-Server 架构，划分 Host、Client、Server 三层职责：

- **Host**：用户交互的宿主应用（如 Claude Desktop、VS Code），包含 Agent 和 MCP Client
- **MCP Client**：Host 内部的协议处理层，负责与 Server 通信
- **MCP Server**：提供 Tools/Resources/Prompts 能力，连接外部系统

### 传输方式

| 传输方式 | 适用场景 | 性能 | 规范状态 |
|---------|---------|------|---------|
| **stdio** | 本地进程通信 | 最快 | 稳定 |
| **Streamable HTTP** | 远程/生产部署 | 高 | 2025 年 3 月新增 |
| **SSE** | 流式响应场景 | 中 | 稳定 |

## 4. Interface / API / ABI 在 MCP 中的体现

MCP 是 Protocol 概念的实例化，其内部完整包含了 Interface、API、ABI 三层抽象：

### Interface（契约层）

MCP 的 Interface 体现为 **Tool 的 `inputSchema`**——每个 Tool 通过 JSON Schema 声明其接受的参数类型、必填字段和约束。这构成了 Tool 调用方和被调用方之间的行为契约：

```json
{
  "name": "send_email",
  "description": "发送电子邮件",
  "inputSchema": {
    "type": "object",
    "properties": {
      "to": { "type": "string" },
      "subject": { "type": "string" },
      "body": { "type": "string" }
    },
    "required": ["to", "subject", "body"]
  }
}
```

### API（方法端点层）

MCP 的 API 体现为 **JSON-RPC 2.0 方法集**。核心方法包括：

| 方法 | 用途 | 类别 |
|------|------|------|
| `initialize` | 初始化连接，交换协议版本和能力 | 生命周期 |
| `tools/list` | 获取所有工具列表 | 能力发现 |
| `tools/call` | 调用指定工具 | 核心操作 |
| `resources/list` | 获取所有资源列表 | 能力发现 |
| `resources/read` | 读取指定资源 | 核心操作 |
| `prompts/list` | 获取所有提示模板列表 | 能力发现 |
| `prompts/get` | 获取指定提示模板 | 核心操作 |

### ABI（二进制兼容层）

MCP 的 ABI 体现为 **JSON + 传输协议** 的组合约束：
- **数据格式**：所有消息必须为合法的 JSON-RPC 2.0 格式，这是跨语言实现的二进制兼容基础
- **传输绑定**：stdio 方式下，消息以换行符分隔的 JSON 行协议（JSON Lines）在 stdin/stdout 上传输；HTTP 方式下，通过标准 HTTP POST 传递 JSON body
- **兼容性保证**：任何语言的 MCP 实现只要遵循 JSON-RPC 2.0 + 所选传输协议的编码约定，即可互操作

## 5. 纵向连接 vs 横向通信的本质区别

MCP 与 ACP/A2A/ANP 的根本差异在于**通信方向**和**对方角色**：

| 维度 | 纵向（MCP） | 横向（ACP/A2A/ANP） |
|------|------------|-------------------|
| 通信双方 | Agent ↔ 工具/数据源 | Agent ↔ Agent |
| 对方角色 | 被动执行的"工具" | 自主决策的"对等智能体" |
| 交互确定性 | 确定性：调用 X 得到 Y | 非确定性：Agent 自主决策 |
| 状态模型 | 无状态调用为主 | 有状态任务/会话 |
| 典型类比 | USB-C：连接外设 | 网络：连接计算机 |

## 6. MDI 示例

以下是一个最小可行的 MCP 协议 MDI 文档：

```markdown
---
mdi_version: "1.0"
profile: "Protocol"
id: "example-mcp-server"
title: "Simple Calculator MCP Server"
protocol: "mcp"
version: "2024-11-05"
---
# Simple Calculator MCP Server

{protocol} type="mcp" version="2024-11-05"

## Tools

{tool} name="add"
### Description
计算两个数的和。

### Input Schema
{input_schema}
- `a` (number, required): 第一个加数
- `b` (number, required): 第二个加数
{/input_schema}

### Output
{output}
- `result` (number): 两数之和
{/output}
{/tool}
```

## 章节导航

| 章节 | 内容 |
|------|------|
| [00 - 总览](00-overview.md) | 可行性分析、架构图、关系全景 |
| [05 - Protocol](05-protocol.md) | 协议：完整通信规则集（MCP 的抽象父概念） |
| [06 - Implementation](06-implementation.md) | 实现：接口/协议的具体编码 |
| [07 - MCP](07-mcp.md) | Model Context Protocol：Agent↔Tool 连接（当前） |
| [08 - ACP](08-acp.md) | Agent Communication Protocol：本地 P2P |
| [09 - A2A](09-a2a.md) | Agent-to-Agent：跨组织协作 |
| [10 - ANP](10-anp.md) | Agent Network Protocol：去中心化网络 |
| [11 - MDI](11-mdi.md) | Markdown Document Interface：载体层 |
| [12 - 关系全景](12-relationships.md) | 7 类关系定义、关系矩阵、交互场景 |

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：MCP 协议在 MyST 统一化生态体系中的概念定义