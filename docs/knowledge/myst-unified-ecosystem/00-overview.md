---
version: 1.0
id: myst-unified-ecosystem-overview
title: "00、总览：MyST Markdown 统一化接口生态体系"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../.meta/toml/docs/knowledge/myst-unified-ecosystem/00-overview.toml"
---
# 00、总览：MyST Markdown 统一化接口生态体系

## 引言

SpecWeave 项目中已积累了丰富但分散的技术资产：

- **MDI v1.0 规范**（[mdi-spec-v1.0.md](../mdi-spec-v1.0.md)）：Markdown 即接口，三种 Profile（Skill/WebAPI/CLI）
- **四层概念抽象**（[interface-api-abi-protocol-wiki](../learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md)）：Interface→API→ABI→Protocol
- **Agent 四层协议栈**（[agent-communication-protocols](../learning/01-agent-protocols-interfaces/agent-communication-protocols/00-overview.md)）：MCP(L1)→ACP(L2)→A2A(L3)→ANP(L4)
- **Agent 四层技术栈**（[agent-interface-deep-dive](../learning/01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md)）：Agent Interface→Agent API→Agent ABI→Agent Protocol

这些资产各自独立，缺乏统一的元模型。**MyST Markdown 统一化接口生态体系**的目标就是：利用 MyST Markdown 的 directive、角色、交叉引用、YAML frontmatter 等特性，将 11 个核心概念纳入一个标准化、可互操作的框架。

## 可行性分析

### 技术可行性

| 能力 | MyST Markdown 支持 | 在统一化体系中的应用 |
|------|-------------------|---------------------|
| **自定义指令** | `{directive_name}` 语法 | 每个概念映射为一个 directive（如 `{interface}`、`{protocol}`） |
| **交叉引用** | `{ref}` 角色 | 概念间关系的形式化引用（如 `{ref} instantiates`） |
| **YAML Frontmatter** | `---` 分隔的 YAML 元数据 | 承载每个概念的元数据（版本、作者、类型） |
| **表格** | Markdown 原生表格 | 属性列表、对比表、关系矩阵 |
| **代码块** | 围栏代码块 ` ``` ` | 示例代码、Schema 定义 |
| **列表** | 有序/无序列表 | 参数列表、场景描述 |
| **标题层级** | H1-H6 | 文档结构组织 |

**已有实现基础**：`.agents/scripts/mdi/` 的 Parser/Validator/Generator 架构可直接复用，仅需扩展 MyST directive 解析和概念元模型。

### 生态可行性

- **MDI v1.0 验证**：已证明 Markdown→OpenAPI/MCP 的生成路线可行
- **MyST 生态**：myst-parser、Sphinx 提供成熟的解析基础设施
- **知识库完备**：现有知识库已覆盖全部 11 个概念的教学内容，可直接作为概念定义的素材来源

### 项目可行性

| 维度 | 现状 | 评估 |
|------|------|------|
| 代码基础 | `.agents/scripts/mdi/` 完整链路 | 可直接复用 |
| 知识基础 | 每个概念均有独立深入文档 | 素材充足 |
| 缺失部分 | 概念元模型、MyST directive 扩展、统一关系映射 | 本阶段产出 |

## 统一化体系分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      元概念层 (Meta)                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  IDL (接口描述语言)                                        │  │
│  │  "如何定义接口的元语言"                                     │  │
│  │  └── describes ──────────────────────────────────────┐    │  │
│  └──────────────────────────────────────────────────────│───┘  │
├────────────────────────────────────────────────────────│──────┤
│                   设计抽象层 (Design)                    │      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │      │
│  │  Interface   │  │  Protocol    │  │Implementa-   │  │      │
│  │  "能力契约"   │  │  "通信规则集" │  │tion "具体实现" │  │      │
│  │              │  │              │  │              │  │      │
│  │  depends-on──┼──┤  API         │  │  implements──┼──┤      │
│  │              │  │  "可调用方法" │  │              │  │      │
│  │              │  │  ABI         │  │  constrained │  │      │
│  │              │  │  "二进制兼容" │  │  -by─┐       │  │      │
│  └──────────────┘  └──────┬───────┘  └──────│───────┘  │      │
│                           │instantiates     │          │      │
├───────────────────────────┼─────────────────┼──────────│──────┤
│                   协议实例层 (Instance)        │          │      │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │          │      │
│  │ MCP  │ │ ACP  │ │ A2A  │ │ ANP  │        │          │      │
│  │ L1   │ │ L2   │ │ L3   │ │ L4   │        │          │      │
│  │Agent │ │Agent │ │Agent │ │Agent │        │          │      │
│  │↔Tool │ │↔Agent│ │↔Agent│ │↔Agent│        │          │      │
│  └──────┘ └──────┘ └──────┘ └──────┘        │          │      │
├─────────────────────────────────────────────┼──────────│──────┤
│                      载体层 (Carrier)         │          │      │
│  ┌───────────────────────────────────────────┼──────────│──┐  │
│  │  MDI (Markdown Document Interface) ◄──────┘          │  │  │
│  │  "基于 MyST Markdown 的 IDL 具体承载格式"             │  │  │
│  │  carries ─────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 关系全景

### 七类关系定义

| 关系类型 | 方向 | 语义 | 示例 |
|---------|------|------|------|
| **实例化** (instantiates) | Protocol → MCP/ACP/A2A/ANP | 具体协议是抽象概念的实例 | MCP 是 Protocol 的一个实例 |
| **实现** (implements) | Implementation → Interface/Protocol | 编码实现 | MCP Server 实现了 MCP 协议 |
| **承载** (carries) | MDI → 所有概念 | MDI 承载所有概念的定义 | MDI 文件承载 Interface 定义 |
| **描述** (describes) | IDL → 所有概念 | IDL 描述接口 | MDI 是一种 IDL 的具体实现 |
| **组合** (composes) | Protocol → API/ABI | 协议由 API+ABI 组合 | A2A 包含 Task API 和 JSON ABI |
| **依赖** (depends-on) | API → Interface | API 依赖 Interface 契约 | REST API 依赖 JSON Schema 参数定义 |
| **约束** (constrains) | ABI → Implementation | ABI 约束兼容性 | JSON ABI 约束跨语言实现的数据格式 |

### 关系矩阵

| | IDL | Interface | API | ABI | Protocol | Impl | MCP | ACP | A2A | ANP | MDI |
|---|-----|-----------|---|---|---|------|---|------|-----|-----|-----|-----|
| **IDL** | - | describes | describes | describes | describes | describes | describes | describes | describes | describes | describes |
| **Interface** | - | - | depends-on | - | - | - | - | - | - | - | - |
| **API** | - | depends-on | - | - | - | - | - | - | - | - | - |
| **ABI** | - | - | - | - | - | constrains | - | - | - | - | - |
| **Protocol** | - | - | composes | composes | - | - | instantiates | instantiates | instantiates | instantiates | - |
| **Impl** | - | implements | - | - | implements | - | - | - | - | - | - |
| **MCP** | - | - | - | - | - | - | - | - | - | - | - |
| **ACP** | - | - | - | - | - | - | - | - | - | - | - |
| **A2A** | - | - | - | - | - | - | - | - | - | - | - |
| **ANP** | - | - | - | - | - | - | - | - | - | - | - |
| **MDI** | carries | carries | carries | carries | carries | carries | carries | carries | carries | carries | - |

> 行 = 源概念，列 = 目标概念。空单元格表示无直接关系（MCP/ACP/A2A/ANP 之间是互补关系，非形式化关系）。

## 阅读路径指南

| 路径 | 适合人群 | 推荐顺序 |
|------|---------|---------|
| **快速入门** | 想快速了解体系全貌 | 00 总览 → 12 关系全景 |
| **概念学习** | 想深入理解每个概念 | 按 01-11 顺序阅读 |
| **协议选型** | 需要选择 Agent 通信协议 | 05 Protocol → 07-10 协议实例 → 12 关系全景 |
| **扩展开发** | 想基于 MDI 扩展工具链 | 01 IDL → 11 MDI → 参考 [mdi-spec-v1.0.md](../mdi-spec-v1.0.md) |

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

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：MyST Markdown 统一化接口生态体系总览