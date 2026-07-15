# .agents/docs 文档边界说明

> 本目录是统一文档容器，承载迁移后的人类文档与 `.agents/` 体系内的智能体专属文档。

## 本目录定位

`.agents/docs/` 统一承载两类内容：

- 原根目录 `docs/` 迁移而来的人类可读文档
- 原生服务于 agent 路由、规则装载、脚本发现的智能体专属文档

## 适用对象

| 文档类型 | 主要读者 | 主要用途 | 典型发现方式 |
|------|----------|----------|--------------|
| 人类文档 | 项目维护者、开发者、贡献者、普通读者 | 阅读说明、知识检索、学习导航、人工维护 | 通过 README、主题索引、人工浏览进入 |
| 智能体专属文档 | agent、自动化脚本、路由流程、治理流程 | 上下文装载、规则读取、程序发现、自动执行 | 通过 `AGENTS.md`、路由表、脚本逻辑进入 |

## 维护原则

- 迁移后的物理文档根路径统一为 `.agents/docs/`。
- 人类文档与智能体专属文档必须通过目录结构、索引或边界说明区分。
- 新增文档时，先判断主要读者与主要用途，再决定归类位置。
- 当 `.agents/` 路由、规则、协议引用知识入口时，优先链接到 `.agents/docs/` 下的对应文档。

## 禁止事项

- 禁止生成嵌套目录 `.agents/docs/docs/`。
- 禁止在无边界说明的情况下混放人类文档与智能体专属文档。
- 禁止沿用已失效的旧根目录 `docs/` 路由口径。
- 禁止覆盖既有智能体专属文档路径。

## 目录归类决策表

| 判定维度 | 默认归为人类文档 | 默认归为智能体专属文档 |
|---|---|---|
| 主要读者 | 项目维护者、开发者、贡献者、普通读者 | agent、自动化脚本、路由流程、治理流程 |
| 主要用途 | 阅读说明、知识检索、学习导航、人工维护 | 上下文装载、规则读取、程序发现、自动执行 |
| 发现方式 | 通过 README、主题索引、人工浏览进入 | 通过 `AGENTS.md` 路由、规则入口、脚本逻辑发现 |
| 维护方式 | 以人工编写、人工审阅、人工导航为主 | 以规则约束、程序读取、流程调用为主 |

## 归类规则

1. 若主要读者与主要用途都偏向人工阅读，则默认归为人类文档。
2. 若主要读者与主要触发方式都偏向 agent 或脚本调用，则默认归为智能体专属文档。
3. 若文件来自原根目录 `docs/`，迁移后默认继承人类文档属性，除非另有显式说明。
4. 若文件来自 `.agents/` 原生体系，默认继承智能体专属文档属性，除非另有显式说明。
5. 若内容同时被人阅读且被流程引用，先看主要读者，再看主要触发方式；仍模糊时，必须补充归类说明。

## 快速查找入口

- 人类文档：按迁移后的主题结构导航，例如 `knowledge/`、`retrospective/`、`templates/`、`task-summaries/`。
- 智能体入口：按 `AGENTS.md`、`.agents/context-routing.md`、规则与协议入口导航。
- 混合型说明文档：在保留人工可读性的同时，必须显式声明是否可被 agent 路由或脚本依赖。

## 目录树

```
.agents/docs/
├── README.md                         ← 目录索引（本文件）
├── project-overview.md               ← 项目概述：定位、设计理念、核心特性
├── project-highlights.md             ← 项目亮点：核心优势、技术创新点、量化成果
├── roadmap.md                        ← 项目蓝图：短期目标、战略方向、技术路线
├── reuse-and-generalization.md       ← 泛化与复用：资产清单、泛化路径、落地案例
├── project-structure.md              ← 项目结构：目录树与职责说明
├── tech-stack.md                     ← 技术栈：技术选型与环境要求
├── agent-roles.md                    ← 智能体角色体系：5 个核心角色概览
├── collaboration.md                  ← 协作体系：4 项协议 + 3 个工作流
├── development-standards.md          ← 开发规范：代码风格、提交规范、测试要求
├── verification-automation.md        ← 验证与自动化：临时依赖治理、验证脚本
├── knowledge-base.md                 ← 知识库：技术知识库与复盘体系概览
├── related-links.md                  ← 相关链接：外部标准、工具文档、项目仓库
├── knowledge/                        ← 技术知识库
│   ├── README.md                     · 知识库索引
│   ├── decisions/                    · 架构决策记录（ADR）
│   ├── operations/                   · 运维操作手册
│   ├── troubleshooting/              · 故障排查指南
│   └── template.md                   · 知识条目模板
├── retrospective/                    ← 复盘文档体系
│   ├── README.md                     · 复盘体系索引
│   ├── prompt-extraction.md          · 提示词工程可迁移模式
│   ├── reports/                      · 项目复盘报告（5 份）
│   ├── patterns/                     · 可复用模式（代码/架构/方法论）
│   ├── frameworks/                   · 决策框架矩阵
│   ├── concepts/                     · 核心知识概念
│   ├── templates/                    · 文档模板
│   └── assets/                       · 资产清单
├── templates/                        ← 文档模板（面向人类读者）
│   ├── README.md                     · 模板索引
│   └── document-governance-checklist.md · 文档治理质量门禁Checklist
├── standards/                        ← 团队规范
│   ├── README.md                     · 规范索引
│   └── cmd-log-specification.md      · CMD-LOG命令集执行日志规范
└── task-summaries/                   ← 任务执行总结
    └── task-summary-readme-creation-20260623.md
```

## 文档导航

### 项目文档

<!-- NAV_TABLE_START -->

| 文档 | 说明 |
|------|------|
| [智能体角色体系](agent-roles.md) | 5 个核心角色定义与绑定关系 |
| [协作体系](collaboration.md) | 4 项协作协议、3 个标准工作流 |
| [开发规范](development-standards.md) | 代码风格、提交规范、测试要求、文档边界 |
| [知识库](knowledge-base.md) | 技术知识库、复盘文档体系 |
| [「复盘+洞察+萃取+导出」与「原子化+模块化」方法论全面分析](methodology-analysis-report.md) | 「复盘+洞察+萃取+导出」与「原子化+模块化」方法论全面分析 |
| [项目亮点](project-highlights.md) | 本文件汇总 SpecWeave 规范体系的核心优势、技术创新点与量化成果数据。数据截至2026-07-05（800... |
| [项目概述](project-overview.md) | 项目定位、设计理念、核心特性 |
| [项目结构](project-structure.md) | 完整目录树与职责说明 |
| [RACI 治理规范与模板](raci-governance-standards.md) | RACI 治理规范与模板 |
| [相关链接](related-links.md) | 外部标准、工具文档、项目仓库 |
| [泛化与资产复用](reuse-and-generalization.md) | 本规范体系的设计目标不仅是"描述一个项目"，更是"可以迁移到任何项目"的**元规范框架**。本文件说明可复用资产清... |
| [项目蓝图与路线图](roadmap.md) | 本文件定义 SpecWeave 规范体系的短期目标、中长期战略方向、技术路线演进与功能迭代计划。 |
| [技术栈与环境要求](tech-stack.md) | 技术选型、环境依赖 |
| [Trae 应用优化分析与实施指南](trae-project-adaptation-guide.md) | Trae 应用优化分析与实施指南 |
| [验证与自动化](verification-automation.md) | 临时依赖治理、验证脚本 |
| [贡献指南](../../CONTRIBUTING.md) | 贡献流程、分支命名、PR 规范 |

<!-- NAV_TABLE_END -->

### 团队规范

| 入口 | 说明 |
|------|------|
| [standards/README.md](standards/README.md) | 团队规范索引，含日志规范、流程规范、格式规范 |
| [CMD-LOG命令集执行日志规范](standards/cmd-log-specification.md) | 5大命令集Skill门面的结构化执行日志标准 |

### 技术知识库

| 入口 | 说明 |
|------|------|
| [knowledge/README.md](knowledge/README.md) | 知识库索引，含决策记录、操作手册、故障排查 |

### 复盘文档体系

| 入口 | 说明 |
|------|------|
| [retrospective/README.md](retrospective/README.md) | 复盘体系索引，含报告、模式、框架、概念、模板 |
| [retrospective/reports/](retrospective/reports/README.md) | 项目复盘分析报告（5 份） |
| [retrospective/patterns/](retrospective/patterns/README.md) | 可复用模式（代码/架构/方法论） |
| [retrospective/frameworks/](retrospective/frameworks/README.md) | 决策框架矩阵 |
| [retrospective/concepts/](retrospective/concepts/README.md) | 核心知识概念 |
| [retrospective/templates/](retrospective/templates/README.md) | 可复用文档模板 |
| [retrospective/prompt-extraction.md](retrospective/prompt-extraction.md) | 提示词工程可迁移模式与方法论 |

### 文档模板

| 文件 | 说明 |
|------|------|
| [templates/](templates/README.md) | 文档模板目录索引（含治理Checklist、README模板等） |
| [templates/document-governance-checklist.md](templates/document-governance-checklist.md) | 文档治理质量门禁Checklist（frontmatter合规+工具清单+原则速查） |

> **关联模块**：
> - `../README.md`
> - `../AGENTS.md`
> - `../CONTRIBUTING.md`
