---
version: 1.0
id: myst-unified-ecosystem-interface
title: "02、Interface：行为契约"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/myst-unified-ecosystem/02-interface.toml"
---
# 02、Interface：行为契约

## 概念模板

| 字段 | 内容 |
|------|------|
| **名称** | Interface（接口） |
| **分类层** | 设计抽象层 (Design) |
| **核心定义** | 行为契约的抽象声明，定义"能做什么" |
| **解决的问题** | 定义组件间交互的契约，确保调用方和被调用方对行为有共同理解 |
| **关键属性** | `name`、`description`、`parameters`（输入 Schema）、`responses`（输出 Schema）、`errors` |
| **关系** | depends-on → 无；composes → 无；described-by → IDL；carried-by → MDI |
| **MyST Directive** | `{interface} name="..."` |
| **MDI 示例** | `{interface} name="calculate"` 包裹 Tool 的输入输出 Schema 定义 |

## 核心定义

Interface 是设计抽象层的最基础概念。它不涉及任何具体实现，仅声明一个组件"能做什么"——接收什么输入、产出什么输出、可能抛出什么错误。Interface 是组件间交互的**契约文本**，调用方依此契约构造请求，实现方依此契约提供服务。

Interface 在概念层级中处于"零依赖"位置：它不依赖任何其他概念，但其他概念依赖它。API 依赖 Interface 定义契约（depends-on），Protocol 通过 API 间接引用 Interface，Implementation 实现对 Interface 的承诺（implements）。

## Interface vs API vs ABI 三者区别

| 维度 | Interface | API | ABI |
|------|-----------|-----|-----|
| **关注层面** | 行为契约（"能做什么"） | 调用端点（"怎么调用"） | 二进制兼容（"如何链接"） |
| **抽象层级** | 最高（纯声明） | 中等（含具体端点） | 最低（机器码约定） |
| **消费者** | 设计者、架构师 | 开发者、LLM/Agent | 编译器、链接器、运行时 |
| **表达形式** | JSON Schema / 自然语言 | 方法签名 / HTTP 端点 | 寄存器约定 / 序列化格式 |
| **稳定性** | 高（行为语义不易变） | 中（端点可版本化演进） | 极高（ABI 变更即不兼容） |
| **在 Agent 生态中** | Tool inputSchema、Agent Card | JSON-RPC 方法、Task API | JSON + STDIO/HTTP |

## Interface 在 Agent 生态中的具体体现

### 1. MCP Tool inputSchema

MCP 协议中每个 Tool 的 `inputSchema` 就是 Interface 的典型实现。它用 JSON Schema 声明工具的参数契约：

```json
{
  "name": "search_docs",
  "description": "搜索知识库文档，返回匹配结果列表",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "搜索关键词" },
      "max_results": { "type": "integer", "default": 10, "minimum": 1, "maximum": 100 }
    },
    "required": ["query"]
  }
}
```

这个 Interface 回答了三个问题：工具叫什么（`name`）、干什么（`description`）、需要什么参数（`inputSchema`）。LLM 读到这个声明后就知道如何构造 `tools/call` 请求，而无需知道 Tool 的实现细节。

### 2. A2A Agent Card

A2A 协议中，每个 Agent 通过 Agent Card 声明自身能力 Interface。Agent Card 包含 Agent 的 `name`、`description`、`skills`（能力列表）、`url`（端点地址）等元数据，使其他 Agent 能在运行时发现并理解其能力范围。

### 3. SKILL.md

本系统中的 Skill 描述文件（`SKILL.md`）是一种轻量级的 Interface 声明。它通过 frontmatter 中的 `name`、`description`、`triggers` 字段，声明了 Skill 能处理什么任务、由什么关键词触发。Agent Runtime 读取这些声明后，即可将用户意图路由到匹配的 Skill。

```yaml
---
name: mcp-builder
description: 构建高质量MCP Server的指南
triggers:
  -   - "创建MCP Server"
  -   - "开发MCP工具"
---
```

## 章节导航

| 章节 | 内容 |
|------|------|
| [00 - 总览](00-overview.md) | 可行性分析、架构图、关系全景 |
| [01 - IDL](01-idl.md) | 接口描述语言：元概念层定义 |
| [02 - Interface](02-interface.md) | 接口：行为契约的抽象声明（当前章节） |
| [03 - API](03-api.md) | 应用程序编程接口：可调用方法端点 |
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
- 2026-07-04 | spec | 初始创建：Interface 行为契约定义与 Agent 生态映射