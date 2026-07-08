---
version: 1.0
id: myst-unified-interface-ecosystem
title: "MyST Markdown 统一化接口生态体系 Spec"
category: standards-tools
source: "user-request:2026-07-04"
x-toml-ref: "../../../../.meta/toml/.trae/specs/standards-tools/myst-unified-interface-ecosystem/spec.toml"
---
# MyST Markdown 统一化接口生态体系 Spec

## Why

当前 SpecWeave 项目中已积累了丰富但分散的技术资产：MDI v1.0 规范（Markdown 即接口）、四层概念抽象（Interface→API→ABI→Protocol）、Agent 四层协议栈（MCP→ACP→A2A→ANP）、Agent 四层技术栈等。这些资产各自独立，缺乏统一的元模型将它们关联起来。MyST Markdown 具备指令（directives）、角色（roles）、交叉引用、YAML frontmatter 等丰富特性，可作为统一的描述语言，将所有接口相关概念纳入一个标准化、可互操作的体系之中。

## What Changes

- 定义统一化体系中的 11 个核心概念的形式化规范：Interface、Protocol、Implementation、API、ABI、MCP、ACP、A2A、ANP、IDL、MDI
- 建立概念的层次化分类体系（元概念层 / 设计抽象层 / 协议实例层 / 载体层）
- 定义 MyST 指令扩展方案，使每个概念可通过 MyST directive 在 Markdown 中声明
- 明确各概念之间的关系映射（实例化、实现、承载、组合等）
- 分析可行性（技术可行性 + 生态可行性 + 项目可行性）
- 提出分阶段实施方案

## Impact

- Affected specs: 扩展 MDI Spec v1.0（新增 Protocol Profile 与概念元模型）
- Affected code: `.agents/scripts/mdi/` — 扩展 models.py 增加概念元模型，扩展 parser.py 支持 MyST directive 解析
- Affected docs: 新增 `docs/knowledge/myst-unified-ecosystem/` 知识库条目

---

## ADDED Requirements

### Requirement: 统一化体系核心概念定义

系统 SHALL 提供 11 个核心概念的标准化定义，明确每个概念在统一体系中的位置、职责和边界。

#### 概念分类架构

系统 SHALL 将 11 个概念组织为四层分类：

| 分类层 | 包含概念 | 职责 |
|--------|---------|------|
| **元概念层** (Meta) | IDL | 定义"如何定义接口"的元语言 |
| **设计抽象层** (Design) | Interface、Protocol、Implementation、API、ABI | 通用软件工程抽象，与具体技术无关 |
| **协议实例层** (Instance) | MCP、ACP、A2A、ANP | 具体协议规范，是 Protocol 的实例化 |
| **载体层** (Carrier) | MDI | IDL 的具体承载格式，基于 MyST Markdown |

#### Scenario: 概念分类查询

- **WHEN** 开发者需要理解某个概念在体系中的位置
- **THEN** 系统提供四层分类定位，明确该概念属于元概念、设计抽象、协议实例还是载体层

---

### Requirement: 统一化体系可行性分析

系统 SHALL 提供完整的可行性分析，覆盖技术可行性、生态可行性和项目可行性三个维度。

#### Scenario: 技术可行性评估

- **WHEN** 评估 MyST Markdown 作为统一描述语言的技术能力
- **THEN** 系统给出以下结论：
  - **MyST Directive 机制**：原生支持自定义指令（`{concept_name}` 语法），可直接映射各概念为 directive
  - **交叉引用**：MyST 的 `{ref}` 角色可实现概念间关系的形式化引用
  - **YAML Frontmatter**：可承载每个概念的元数据（版本、作者、类型等）
  - **表格/列表/代码块**：MDI v1.0 已验证 Markdown 结构映射到结构化模型的可行性
  - **已有实现基础**：`.agents/scripts/mdi/` 的 Parser/Validator/Generator 架构可复用

#### Scenario: 生态可行性评估

- **WHEN** 评估统一化体系在现有生态中的兼容性
- **THEN** 系统给出以下结论：
  - MDI v1.0 已验证 Markdown→OpenAPI/MCP 的生成路线，证明生成方向可行
  - MyST 生态（myst-parser、Sphinx）提供成熟的解析基础设施
  - 现有知识库（agent-communication-protocols、agent-interface-deep-dive、interface-api-abi-protocol-wiki）已覆盖全部概念的教学内容，可直接作为概念定义的素材来源

#### Scenario: 项目可行性评估

- **WHEN** 评估在 SpecWeave 项目中的落地可行性
- **THEN** 系统给出以下结论：
  - 已有代码基础：`.agents/scripts/mdi/` 提供 parser/models/validator/generator 完整链路
  - 已有知识基础：知识库中每个概念均已存在独立的深入文档
  - 缺失部分：概念元模型定义、MyST directive 扩展、统一关系映射

---

### Requirement: 概念间关系映射体系

系统 SHALL 定义 11 个概念之间的 7 类关系，并提供形式化的关系映射规则。

#### 七类关系定义

| 关系类型 | 源概念 | 目标概念 | 语义 | 示例 |
|---------|--------|---------|------|------|
| **实例化** (instantiates) | Protocol | MCP/ACP/A2A/ANP | 具体协议是 Protocol 抽象概念的实例 | MCP 是 Protocol 的一个实例 |
| **实现** (implements) | Implementation | Interface/Protocol | 实现是对接口或协议的具体编码 | MCP Server 实现 实现了 MCP 协议 |
| **承载** (carries) | MDI | 所有概念 | MDI 作为 IDL 承载所有概念的定义 | MDI 文件承载 Interface 定义 |
| **描述** (describes) | IDL | 所有概念 | IDL 是描述接口的元语言 | MDI 是一种 IDL 的具体实现 |
| **组合** (composes) | Protocol | API/ABI | 协议由 API 方法和 ABI 约束组合而成 | A2A 协议包含 Task API 和 JSON ABI |
| **依赖** (depends-on) | API | Interface | API 依赖 Interface 定义参数和返回值契约 | REST API 依赖 Interface 定义的 JSON Schema |
| **约束** (constrains) | ABI | Implementation | ABI 约束不同实现的二进制兼容性 | JSON ABI 约束 Python/Node.js 实现的数据格式 |

#### Scenario: 关系一致性验证

- **WHEN** 在 MDI 文件中声明概念间关系
- **THEN** Validator 自动验证关系合法性：不允许循环实例化、不允许未定义概念的引用、关系方向必须符合类型约束

---

### Requirement: MyST Directive 扩展方案

系统 SHALL 定义一套 MyST directive 用于在 Markdown 中声明各概念及其关系，扩展 MDI v1.0 的 Profile 体系。

#### 新增 Protocol Profile

MDI v1.0 已有的三种 Profile（skill/webapi/clitool）基础上，新增第四种 Profile：

```yaml
---
type: protocol
protocol_type: mcp | acp | a2a | anp   # 协议类型
---
```

#### 新增 MyST Directive 清单

| Directive | 用途 | 示例 |
|-----------|------|------|
| `{interface}` | 声明一个 Interface 定义 | `{interface} name="ToolSchema"` |
| `{protocol}` | 声明一个 Protocol 定义 | `{protocol} type="mcp" version="2024-11-05"` |
| `{implementation}` | 声明一个实现 | `{implementation} of="mcp" lang="python"` |
| `{api}` | 声明 API 端点 | `{api} method="tools/call" protocol="mcp"` |
| `{abi}` | 声明 ABI 约束 | `{abi} format="json-rpc" encoding="utf-8" ` |
| `{idl}` | 声明 IDL 元信息 | `{idl} name="MDI" version="2.0"` |
| `{mdi}` | 声明 MDI 文档元信息 | `{mdi} profile="protocol"` |

#### Scenario: 使用 Protocol Profile 定义 MCP 协议

- **WHEN** 开发者创建 MCP 协议的 MDI 文档
- **THEN** frontmatter 声明 `type: protocol` 和 `protocol_type: mcp`
- **THEN** 文档中可使用 `{protocol}`、`{api}`、`{abi}` 等 directive 声明协议的各个组成部分

---

### Requirement: 统一化体系分层架构图

系统 SHALL 提供统一化体系的分层架构图，展示 11 个概念在四层分类中的位置及其关系。

#### 架构图

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

#### Scenario: 架构图导航

- **WHEN** 开发者需要理解统一化体系的整体架构
- **THEN** 系统提供分层架构图，展示四层分类、概念归属和关键关系连线

---

### Requirement: 各概念统一化接口定义规范

系统 SHALL 为每个概念提供统一的结构化定义模板，包含：概念名称、所属分类层、核心定义、关键属性、与其他概念的关系、MyST Directive 声明方式、MDI 文档示例。

#### 概念定义模板

每个概念定义 SHALL 包含以下字段：

| 字段 | 说明 |
|------|------|
| 名称 | 概念的标准名称 |
| 分类层 | 元概念层 / 设计抽象层 / 协议实例层 / 载体层 |
| 核心定义 | 一句话定义 |
| 解决的问题 | 该概念在系统中解决的核心问题 |
| 关键属性 | 定义该概念必须包含的属性列表 |
| 关系 | 与其他概念的 7 类关系映射 |
| MyST Directive | 该概念对应的 MyST directive 声明方式 |
| MDI 示例 | 最小可行的 MDI 文档示例 |

#### Scenario: 按模板定义 Interface 概念

- **WHEN** 定义 Interface 概念
- **THEN** 按模板填写：分类层=设计抽象层，核心定义="行为契约的抽象声明，定义能做什么"，关键属性=[name, description, parameters, responses]，关系=[depends-on: none, composes: none, described-by: IDL, carried-by: MDI]

---

### Requirement: 分阶段实施路线图

系统 SHALL 提供分阶段实施计划，确保每一步可落地、可验证。

#### 阶段划分

| 阶段 | 内容 | 产出物 | 依赖 |
|------|------|--------|------|
| **阶段 1：概念规范定义** | 完成 11 个概念的标准化定义文档 | `docs/knowledge/myst-unified-ecosystem/` 系列文档 | 无 |
| **阶段 2：MDI 扩展** | 扩展 MDI v1.0 为 v2.0，增加 Protocol Profile 和概念元模型 | 更新后的 MDI Spec v2.0 | 阶段 1 |
| **阶段 3：Parser 扩展** | 在 `.agents/scripts/mdi/` 中增加 MyST directive 解析和概念元模型 | 扩展后的 mdi 包 | 阶段 2 |
| **阶段 4：关系验证** | 实现概念间关系的自动验证（7 类关系约束） | 扩展后的 Validator | 阶段 3 |
| **阶段 5：统一看板** | 生成概念关系可视化看板 | 概念关系 Dashboard | 阶段 4 |

#### Scenario: 当前阶段聚焦

- **WHEN** 本 spec 首次执行
- **THEN** 优先完成阶段 1（概念规范定义），产出 11 个概念的标准化定义文档
- **THEN** 阶段 2-5 的详细设计在阶段 1 完成后根据实际产出调整

---

## REMOVED Requirements

无

---

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：MyST Markdown 统一化接口生态体系 Spec v1.0