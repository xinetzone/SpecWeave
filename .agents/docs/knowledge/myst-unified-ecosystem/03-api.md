---
version: 1.0
id: myst-unified-ecosystem-api
title: "03、API：应用程序编程接口"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/myst-unified-ecosystem/03-api.toml"
---
# 03、API：应用程序编程接口

## 概念模板

| 字段 | 内容 |
|------|------|
| **名称** | API（Application Programming Interface） |
| **分类层** | 设计抽象层 (Design) |
| **核心定义** | 源码/服务级的可调用方法端点，定义"怎么调用" |
| **解决的问题** | 提供具体的调用入口、方法签名、参数格式和返回值结构 |
| **关键属性** | `method_name`、`endpoint`、`parameters`、`return_type`、`error_codes`、`auth_required` |
| **关系** | depends-on → Interface；composes → 无；described-by → IDL；carried-by → MDI |
| **MyST Directive** | `{api} method="..." protocol="..."` |
| **MDI 示例** | `{api} method="tools/call" protocol="JSON-RPC 2.0"` 包裹请求/响应格式定义 |

## 核心定义

API 是 Interface 的**具体可调用暴露**。如果 Interface 回答了"能做什么"，API 则回答了"怎么调用"——通过什么方法名、走什么传输协议、传什么格式的参数、收到什么格式的返回值。API 是 Interface 与调用方之间的**具体桥梁**。

## API 与 Interface 的 depends-on 关系

API 依赖 Interface（depends-on），这是设计抽象层中最核心的一对关系：

- **Interface 先于 API**：先定义行为契约（输入什么、输出什么），再设计具体的调用端点（方法名、传输方式）
- **API 是 Interface 的投影**：同一个 Interface 可以有多个 API 投影——例如同一个 Tool Interface 可以同时暴露为 STDIO 端点和 HTTP 端点
- **Interface 稳定，API 可演进**：Interface 的行为语义保持稳定，API 的端点路径、方法名、版本号可以随协议升级而变化

```
Interface ("calculate" 能力契约)
    │
    │ depends-on
    ▼
API ("tools/call" JSON-RPC 方法 + "POST /mcp" HTTP 端点)
```

## Agent 生态中的 API 体现

### 1. MCP JSON-RPC 方法

MCP 协议的 API 层以 JSON-RPC 2.0 为标准，定义了以下核心方法：

| 方法分类 | 方法名 | 功能 |
|---------|--------|------|
| 生命周期 | `initialize` | 握手协商版本和能力 |
| 生命周期 | `notifications/initialized` | 通知握手完成 |
| Tool | `tools/list` | 获取所有 Tool Interface 列表 |
| Tool | `tools/call` | 调用指定 Tool |
| Resource | `resources/list` / `resources/read` | 资源管理 |
| Prompt | `prompts/list` / `prompts/get` | 提示词模板管理 |

每个方法都有明确的参数格式（`params` 对象）、返回格式（`result` 对象）和错误格式（`error` 对象，含 `code`、`message`、`data` 字段）。

### 2. A2A Task API

A2A 协议围绕 Task 生命周期设计 API：

| 方法 | 功能 |
|------|------|
| `tasks/send` | 发送任务给另一个 Agent |
| `tasks/get` | 查询任务状态和结果 |
| `tasks/cancel` | 取消运行中的任务 |
| `tasks/subscribe` | 通过 SSE 订阅任务更新 |

A2A 的 API 设计体现了"长时任务"的异步特性——任务提交后不是立即返回结果，而是通过状态查询和 SSE 推送跟踪进度。

### 3. ACP REST 端点

ACP 采用更传统的 RESTful 风格，使用 HTTP 方法（GET/POST/PUT/DELETE）和 URL 路径标识操作，适合本地 Agent Runtime 之间的消息通信。

## 章节导航

| 章节 | 内容 |
|------|------|
| [00 - 总览](00-overview.md) | 可行性分析、架构图、关系全景 |
| [01 - IDL](01-idl.md) | 接口描述语言：元概念层定义 |
| [02 - Interface](02-interface.md) | 接口：行为契约的抽象声明 |
| [03 - API](03-api.md) | 应用程序编程接口：可调用方法端点（当前章节） |
| [04 - ABI](04-abi.md) | 应用程序二进制接口：二进制兼容约定 |
| [05 - Protocol](05-protocol.md) | 协议：完整通信规则集 |
| [06 - Implementation](06-implementation.md) | 实现：接口/协议的具体编码 |
| [07 - MCP](07-mcp.md) | Model Context Protocol：Agent↔Tool 连接 |
| [08 - ACP](08-acp.md) | Agent Communication Protocol：本地 P2P |
| [09 - A2A](09-a2a.md) | Agent-to-Agent：跨组织协作 |
| [10 - ANP](10-anp.md) | Agent Network Protocol：去中心化网络 |
| [11 - MDI](11-mdi.md) | Markdown Document Interface：载体层 |
| [12 - 关系全景](12-relationships.md) | 7 类关系定义、关系矩阵、交互场景 |

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：API 可调用方法端点定义与 Agent 生态映射