# 项目文档

> 本目录存放项目文档，按主题分类组织，便于查阅、维护与独立引用。

## 目录树

```
docs/
├── README.md                         ← 目录索引（本文件）
├── project-overview.md               ← 项目概述：定位、设计理念、核心特性
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
├── templates/                        ← 文档模板
│   ├── readme-template-spec.md       · spec 类 README 模板
│   ├── readme-template-library.md    · library 类 README 模板
│   └── readme-template-app.md        · app 类 README 模板
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
| [项目概述](project-overview.md) | 项目定位、设计理念、核心特性 |
| [项目结构](project-structure.md) | 完整目录树与职责说明 |
| [相关链接](related-links.md) | 外部标准、工具文档、项目仓库 |
| [技术栈与环境要求](tech-stack.md) | 技术选型、环境依赖 |
| [验证与自动化](verification-automation.md) | 临时依赖治理、验证脚本 |
| [贡献指南](../CONTRIBUTING.md) | 贡献流程、分支命名、PR 规范 |

<!-- NAV_TABLE_END -->

### 技术知识库

| 入口 | 说明 |
|------|------|
| [knowledge/README.md](knowledge/README.md) | 知识库索引，含决策记录、操作手册、故障排查 |

### 复盘文档体系

| 入口 | 说明 |
|------|------|
| [retrospective/README.md](retrospective/README.md) | 复盘体系索引，含报告、模式、框架、概念、模板 |
| [retrospective/reports/](retrospective/reports/) | 项目复盘分析报告（5 份） |
| [retrospective/patterns/](retrospective/patterns/) | 可复用模式（代码/架构/方法论） |
| [retrospective/frameworks/](retrospective/frameworks/) | 决策框架矩阵 |
| [retrospective/concepts/](retrospective/concepts/) | 核心知识概念 |
| [retrospective/templates/](retrospective/templates/) | 可复用文档模板 |
| [retrospective/prompt-extraction.md](retrospective/prompt-extraction.md) | 提示词工程可迁移模式与方法论 |

### 文档模板

| 文件 | 说明 |
|------|------|
| [templates/readme-template-spec.md](templates/readme-template-spec.md) | spec 类 README 模板 |
| [templates/readme-template-library.md](templates/readme-template-library.md) | library 类 README 模板 |
| [templates/readme-template-app.md](templates/readme-template-app.md) | app 类 README 模板 |

> **关联模块**：
> - `../README.md`
> - `../AGENTS.md`
> - `../CONTRIBUTING.md`