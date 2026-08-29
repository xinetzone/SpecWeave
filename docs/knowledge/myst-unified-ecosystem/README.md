---
version: 1.0
id: myst-unified-ecosystem-readme
title: "MyST Markdown 统一化接口生态体系 — 入口索引"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../.meta/toml/docs/knowledge/myst-unified-ecosystem/README.toml"
---
# MyST Markdown 统一化接口生态体系

> 基于 MyST Markdown 的统一化接口描述体系，将 11 个核心概念纳入标准化、可互操作的框架之中。

## 四层分类架构

```
┌──────────────────────────────────────────────────────────────┐
│                     元概念层 (Meta)                           │
│  IDL — "如何定义接口的元语言"                                  │
│  └── describes ── 描述所有概念                                │
├──────────────────────────────────────────────────────────────┤
│                   设计抽象层 (Design)                          │
│  Interface · Protocol · Implementation · API · ABI           │
│  通用软件工程抽象，与具体技术无关                                │
│  Protocol ── instantiates ──→ MCP/ACP/A2A/ANP               │
├──────────────────────────────────────────────────────────────┤
│                   协议实例层 (Instance)                        │
│  MCP (L1) · ACP (L2) · A2A (L3) · ANP (L4)                 │
│  具体协议规范，是 Protocol 的实例化                              │
├──────────────────────────────────────────────────────────────┤
│                     载体层 (Carrier)                          │
│  MDI — 基于 MyST Markdown 的 IDL 具体承载格式                  │
│  carries ── 承载所有概念的定义                                 │
└──────────────────────────────────────────────────────────────┘
```

## 概念速查表

| # | 概念 | 分类层 | 一句话定义 | 文档 |
|---|------|--------|-----------|------|
| 1 | **IDL** | 元概念层 | 定义"如何定义接口"的元语言 | [01-idl.md](01-idl.md) |
| 2 | **Interface** | 设计抽象层 | 行为契约的抽象声明，定义"能做什么" | [02-interface.md](02-interface.md) |
| 3 | **API** | 设计抽象层 | 源码/服务级的可调用方法端点 | [03-api.md](03-api.md) |
| 4 | **ABI** | 设计抽象层 | 二进制级的兼容性约定 | [04-abi.md](04-abi.md) |
| 5 | **Protocol** | 设计抽象层 | 完整的通信规则集 | [05-protocol.md](05-protocol.md) |
| 6 | **Implementation** | 设计抽象层 | 接口或协议的具体编码实现 | [06-implementation.md](06-implementation.md) |
| 7 | **MCP** | 协议实例层 | Agent↔Tool 的标准化连接协议 | [07-mcp.md](07-mcp.md) |
| 8 | **ACP** | 协议实例层 | 本地 Agent↔Agent 的 P2P 通信协议 | [08-acp.md](08-acp.md) |
| 9 | **A2A** | 协议实例层 | 跨组织 Agent↔Agent 的协作协议 | [09-a2a.md](09-a2a.md) |
| 10 | **ANP** | 协议实例层 | 去中心化公网 Agent 网络协议 | [10-anp.md](10-anp.md) |
| 11 | **MDI** | 载体层 | 基于 MyST Markdown 的 IDL 承载格式 | [11-mdi.md](11-mdi.md) |

## 七类关系速查

| 关系 | 源 → 目标 | 语义 |
|------|----------|------|
| **实例化** (instantiates) | Protocol → MCP/ACP/A2A/ANP | 具体协议是抽象概念的实例 |
| **实现** (implements) | Implementation → Interface/Protocol | 编码实现 |
| **承载** (carries) | MDI → 所有概念 | MDI 承载所有概念的定义 |
| **描述** (describes) | IDL → 所有概念 | IDL 是描述接口的元语言 |
| **组合** (composes) | Protocol → API/ABI | 协议由 API+ABI 组合 |
| **依赖** (depends-on) | API → Interface | API 依赖 Interface 定义契约 |
| **约束** (constrains) | ABI → Implementation | ABI 约束二进制兼容性 |

## 阅读路径

| 路径 | 适合人群 | 推荐顺序 |
|------|---------|---------|
| **快速入门** | 想快速了解体系全貌 | 00 总览 → 12 关系全景 |
| **概念学习** | 想深入理解每个概念 | 按 01-11 顺序阅读 |
| **协议选型** | 需要选择 Agent 通信协议 | 05 Protocol → 07-10 协议实例 → 12 关系全景 |
| **扩展开发** | 想基于 MDI 扩展工具链 | 01 IDL → 11 MDI → 参考现有知识库 |

## 章节导航

| 章节 | 内容 |
|------|------|
| [00 - 总览](00-overview.md) | 可行性分析、架构图、关系全景 |
| [01 - IDL](01-idl.md) | 接口描述语言：元概念层定义 |
| [02 - Interface](02-interface.md) | 接口：行为契约的抽象声明 |
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

## 关联资产

| 资产 | 链接 |
|------|------|
| MDI Spec v1.0 | [../mdi-spec-v1.0.md](../mdi-spec-v1.0.md) |
| MDI 研究报告 | [../mdi-research-report.md](../mdi-research-report.md) |
| Agent 通信协议总览 | [../learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md](../learning/01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) |
| Interface/API/ABI/Protocol 概念 Wiki | [../learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md](../learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md) |
| Agent 四层技术栈 | [../learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md](../learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md) |

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：MyST Markdown 统一化接口生态体系入口索引