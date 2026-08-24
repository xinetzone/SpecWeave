# GraphQL 系统化学习 OKF Wiki 教程 - 产品需求文档

## Overview

- **Summary**: 基于 GraphQL 官方规范源码（`external/libs/GraphQL/graphql-spec/`）、GraphQL AI 工作组资料（`external/libs/GraphQL/ai-wg/`）以及 GraphQL 官网多个页面，使用 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）和七概念方法论编排（知识沉淀场景 R→I→E），在 `projects/awesome-okf-xs/bundles/graphql/graphql/` 生成符合 OKF v0.2 规范的系统化中文 Wiki 教程。教程覆盖 GraphQL 查询语言、类型系统、Schema 定义、验证规则、执行引擎、内省系统、响应格式、Python 生态（客户端/服务端库）以及 GraphQL + AI（MCP 服务器、语义内省）等完整知识体系。

- **Purpose**: 解决 GraphQL 学习资料分散（官网、规范文档、WG 笔记、各语言库文档各自独立）的问题，提供一个事实可溯源、结构统一、遵循渐进学习路径的中文知识库。所有内容均溯源至官方规范文档章节或实际源码文件，杜绝 AI 虚构 API 或行为。

- **Target Users**: 
  - 希望系统学习 GraphQL 规范而非仅停留在"会写 query"层面的中文开发者
  - 需要在 Python 生态中选型 GraphQL 客户端/服务端库的工程师
  - 关注 GraphQL 与 AI/LLM 集成方向（MCP、语义内省）的技术人员
  - 需要可溯源的 GraphQL 参考资料进行教学或培训的团队

## Goals

- G1: 完整覆盖 GraphQL 规范的 7 个核心章节（Overview/Language/Type System/Introspection/Validation/Execution/Response），每个规范章节至少有一个对应的概念文档
- G2: 覆盖 GraphQL Python 生态，包括客户端库和服务端库的选型指南与核心用法
- G3: 覆盖 GraphQL + AI 方向，包括 AI WG 的 MCP 服务器实现和语义内省 RFC
- G4: 所有技术事实均可溯源至官方规范文档（章节级引用）或实际源码文件（文件路径+行号）
- G5: 遵循 OKF v0.2 规范，目录结构、frontmatter、交叉链接格式完全合规
- G6: 概念文档按学习路径编号（00-NN），形成从入门到高级的渐进式知识地图
- G7: 提供可运行的示例文档，包含 GraphQL 查询、Schema 定义、Python 客户端/服务端代码

## Non-Goals (Out of Scope)

- 不实现 GraphQL 服务器或客户端库代码（仅学习和文档生成）
- 不覆盖非 Python 语言的 GraphQL 库实现细节（JS/Java/Go 等仅在生态概览中提及）
- 不翻译全部规范文本（规范是英文的事实源，Wiki 是中文的概念解释和架构洞察，非逐句翻译）
- 不覆盖 GraphQL 历史版本的变更细节（changelog 仅在 references 中登记，不展开）
- 不创建与 GraphQL 无关的通用 API 设计教程
- 不修改 `external/libs/GraphQL/` 下的任何子模块文件
- 不更新 `projects/awesome-okf-xs/bundles/index.md` 总索引（除非用户后续要求）

## Background & Context

### 信源资产

**本地源码资产**（`d:\spaces\SpecWeave\external\libs\GraphQL\`）：

| 子目录 | 类型 | 核心内容 |
|--------|------|----------|
| `graphql-spec/spec/` | 官方规范文档 | Section 1-7（Overview/Language/Type System/Introspection/Validation/Execution/Response）+ Appendix A-D |
| `graphql-spec/changelogs/` | 变更日志 | October2021.md, September2025.md |
| `ai-wg/mcp/` | Python 源码 | MCP 服务器（server.py）、Schema 索引器（schema_indexer.py）、GraphQL Schema（schema.graphql）、测试服务器 |
| `ai-wg/rfcs/` | RFC 文档 | semantic-introspection.md、relay_style_mock_store.pdf |
| `ai-wg/agendas/` + `notes/` | WG 会议记录 | 2025-10 至 2026-11 的议程和会议纪要 |

**官网 URL 资产**：

| URL | 内容 |
|-----|------|
| `https://graphql.org/` | 官网首页，生态概览 |
| `https://graphql.org/learn/introduction/` | 入门教程 |
| `https://graphql.org/community/tools-and-libraries/?tags=python&tags=client` | Python 客户端库列表 |
| `https://graphql.org/community/tools-and-libraries/?tags=server&tags=python` | Python 服务端库列表 |
| `https://graphql.org/resources/backend/` | 后端资源 |
| `https://graphql.org/resources/frontend/#documentation` | 前端/文档资源 |
| `https://graphql.org/ai/` | GraphQL + AI 专题页 |

### OKF Bundle 组织规范

参考已有成熟 bundle（如 `bundles/onnx/onnx/` 含 14 概念 + 4 示例 + 8 信源共 26 文档），本 bundle 的目标位置为：

```
projects/awesome-okf-xs/bundles/graphql/graphql/
├── index.md              # 根索引（含 okf_version: "0.2" frontmatter）
├── log.md                # 变更日志
├── concepts/             # 概念文档（00-NN 编号）
│   └── index.md          # 概念索引（无 frontmatter）
├── examples/             # 示例文档
│   └── index.md
├── references/           # 信源登记
│   └── index.md
└── spec/                 # R/I 阶段工作文件
    ├── facts.md          # R 阶段：编号事实清单
    └── insights.md       # I 阶段：架构洞察与知识地图
```

### 方法论约束

- **source-code-to-okf-wiki**：严格遵循 R→I→E→V→C 五阶段，references/ 先于 concepts/ 生成，index 最后写，每批≤7文件
- **seven-concepts-cmd**：场景4（知识沉淀），链路 R→I→E，质量门 G1（事实无推断）、G2（洞察四元组完整）、G3（模式可迁移）
- 本任务的特殊性：主要信源是规范文档（Markdown）而非传统编程语言源码，因此 R 阶段的"事实"是规范中的定义、规则、语法产生式等可验证陈述；V 阶段的 Grep 验证改为规范文档内容核验

## Functional Requirements

- **FR-1**: R 阶段——通读 GraphQL 规范 7 个章节和 AI WG MCP 源码，提取编号事实 F-xxx 写入 `spec/facts.md`，每条事实指向具体规范章节或源码文件
- **FR-2**: I 阶段——基于事实清单提炼 3-5 个核心架构洞察，设计知识地图（入门/核心/高级分组），写入 `spec/insights.md`
- **FR-3**: E 阶段——按信源先行原则生成 references/ 信源登记文件，再分批生成 concepts/ 概念文档和 examples/ 示例文档，最后生成各级 index.md
- **FR-4**: 概念文档覆盖 GraphQL 设计原则、查询语言语法、类型系统（Scalar/Object/Interface/Union/Enum/Input/Directive）、Schema 定义、内省系统、验证规则、执行引擎（Resolve 管线/错误处理）、响应格式
- **FR-5**: 概念文档覆盖 Python GraphQL 生态，包括客户端库（gql、python-graphql-client 等）和服务端库（Strawberry、Ariadne、Graphene、tartiflette 等）的选型对比和核心用法
- **FR-6**: 概念文档覆盖 GraphQL + AI，包括 MCP 服务器架构、Schema 索引器、语义内省 RFC 核心思想
- **FR-7**: 示例文档提供可运行代码：第一个 GraphQL 查询、Schema 设计与 Resolver、Python 客户端调用、Python 服务端搭建
- **FR-8**: V 阶段——独立审查所有文档：结构完整性、frontmatter 必填字段、交叉链接有效性、事实溯源准确性（对照规范文档和源码核验）、代码示例正确性
- **FR-9**: 所有文档使用中文撰写，英文技术术语首次出现时括号注释
- **FR-10**: 根 index.md 含 `okf_version: "0.2"` frontmatter，子目录 index.md 无 frontmatter

## Non-Functional Requirements

- **NFR-1**: 每个概念文档 500-5000 字，使用 `##` 二级标题分节，不使用 `#`（留给文件标题）
- **NFR-2**: 每个文档结尾有"## 相关概念"章节，交叉链接使用 `/` 开头的 bundle-relative 路径
- **NFR-3**: 代码块标注语言（`graphql`、`python`、`json`、`bash` 等），API 调用必须与 facts.md 中事实一致
- **NFR-4**: frontmatter 包含 `type`、`title`、`description`、`sources` 字段；`type` 取值为 `concept`/`example`/`reference`
- **NFR-5**: 每批生成文档数 ≤ 7，防止上下文过载
- **NFR-6**: 信源文件先于内容文档生成，index.md 最后统一生成
- **NFR-7**: 文件名使用 kebab-case 英文命名，概念文档按 `NN-kebab-name.md` 编号
- **NFR-8**: 禁止虚构规范中不存在的类型、字段、指令或 API——拿不准的回到 facts.md 核对

## Constraints

- **Technical**: 
  - 产出物为 Markdown 文件，遵循 OKF v0.2 规范
  - 工作目录在 Windows 系统，路径使用正斜杠
  - 不修改 `external/libs/GraphQL/` 下的 git submodule 文件
  - 不修改 `projects/awesome-okf-xs/` 子项目内除 bundle 目录外的其他文件
- **Business**: 
  - 内容为公开技术知识（GraphQL 规范采用 OWFa 1.0 许可证），无访问控制
  - 中文撰写
- **Dependencies**: 
  - 本地 GraphQL 规范文档可读
  - 本地 AI WG MCP Python 源码可读
  - 官网 URL 可访问（用于补充生态信息）

## Assumptions

- A1: GraphQL 规范文档（Markdown 格式）是本教程的主要权威信源，其章节结构直接映射为概念文档分组
- A2: AI WG MCP 服务器代码量较小（server.py + schema_indexer.py），适合全量阅读提取事实
- A3: 官网工具库页面提供的 Python 库列表是选型参考的权威来源，无需逐一深入每个库的源码
- A4: 用户希望在 `bundles/graphql/graphql/` 单 bundle 中集中管理所有 GraphQL 相关知识（而非拆分为多个 bundle）
- A5: 规范文档中的语法产生式（Grammar Productions）以代码块形式引用，不做逐字符解释
- A6: `spec/` 工作文件（facts.md、insights.md）是过程产物，保留在 bundle 内供溯源（参考 katex、myst 等已有 bundle 的做法）

## Acceptance Criteria

### AC-1: R 阶段事实清单完整且零推测
- **Given**: GraphQL 规范 7 章节和 AI WG MCP 源码已通读
- **When**: 审查 `spec/facts.md`
- **Then**: 包含覆盖所有 7 个规范章节和 MCP 源码的编号事实 F-xxx，每条事实指向具体文件路径/章节，无"用于"/"目的是"/"设计为"等推断性表述
- **Verification**: `human-judgment`
- **Notes**: G1 质量门

### AC-2: I 阶段洞察四元组完整
- **Given**: facts.md 已完成
- **When**: 审查 `spec/insights.md`
- **Then**: 包含 3-5 个核心洞察，每个含陈述/证据（F-xxx 引用）/反常识/行动四元组；知识地图有明确的入门→核心→高级学习路径
- **Verification**: `human-judgment`
- **Notes**: G2 质量门

### AC-3: references/ 信源登记先于内容文档生成
- **Given**: E 阶段启动
- **When**: 检查文件生成顺序
- **Then**: references/ 下所有信源文件在 concepts/ 和 examples/ 任何文件之前创建；每个信源文件登记对应的规范章节或源码文件路径
- **Verification**: `programmatic`

### AC-4: 概念文档覆盖 GraphQL 规范核心章节
- **Given**: concepts/ 目录已生成
- **When**: 对照规范 Section 1-7 检查
- **Then**: 每个规范章节至少有一个概念文档覆盖其核心内容；概念文档编号形成连续学习路径
- **Verification**: `human-judgment`

### AC-5: Python 生态文档准确
- **Given**: Python 生态概念文档已生成
- **When**: 检查引用的库名称和核心 API
- **Then**: 库名称与官网 tools-and-libraries 页面一致；核心 API 描述有事实溯源
- **Verification**: `human-judgment`

### AC-6: GraphQL + AI 文档覆盖 MCP 和语义内省
- **Given**: AI 相关概念文档已生成
- **When**: 检查内容
- **Then**: MCP 服务器架构描述与 server.py 源码一致；语义内省 RFC 核心思想有准确概述
- **Verification**: `programmatic`（通过源码核验）

### AC-7: 示例文档代码完整可运行
- **Given**: examples/ 目录已生成
- **When**: 审查代码示例
- **Then**: 每个示例包含完整代码（非片段），GraphQL 示例语法正确，Python 示例 import 和 API 调用与事实一致
- **Verification**: `human-judgment`

### AC-8: V 阶段无虚构 API/类型/指令
- **Given**: 所有文档已生成
- **When**: 对文档中引用的每个 GraphQL 类型、字段、指令、Python 类/方法，对照 facts.md 和原始信源核验
- **Then**: 无虚构内容；发现的问题全部修复
- **Verification**: `programmatic`（Grep/Read 核验）
- **Notes**: G4 质量门，最关键检查项

### AC-9: OKF v0.2 格式合规
- **Given**: 所有文档已生成
- **When**: 检查目录结构和 frontmatter
- **Then**: 目录结构符合 bundle 规范；每个 .md 文件有 `type` 字段；根 index.md 有 `okf_version: "0.2"`；子目录 index.md 无 frontmatter；交叉链接使用 `/` 开头路径
- **Verification**: `programmatic`

### AC-10: 交叉链接无断裂
- **Given**: 所有文档已生成
- **When**: 检查所有内部链接
- **Then**: 所有交叉链接的目标文件存在；无 `../` 相对路径风格
- **Verification**: `programmatic`

### AC-11: 分批生成遵守批次限制
- **Given**: E 阶段执行
- **When**: 检查执行记录
- **Then**: 每批生成文档数 ≤ 7；index.md 在所有内容文档之后生成
- **Verification**: `programmatic`

## Open Questions

- [ ] 是否需要更新 `bundles/graphql/index.md` 分组索引和 `bundles/index.md` 总索引？（当前 spec 默认不更新，仅生成 bundle 内部文件）
- [ ] Python 生态部分是否需要深入特定库（如 Strawberry/Ariadne）的源码进行 fact 提取，还是基于官方文档做概览级介绍？（当前 spec 假设为概览级）
- [ ] 官网页面内容是否需要使用浏览器工具抓取，还是基于 URL 已知信息和本地规范文档生成？（部分页面内容可能需要实时抓取）
