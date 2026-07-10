---
id: "ai-agent-workspace-handbook"
source: "external: 已迁移-.agents/insights/packaging/notebook-nuitka-build-retrospective-20260704.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/ai-agent-workspace-handbook.toml"
---
# AI Agent 工作手册模式：.agents/ 目录让智能体高效参与项目

## 模式概述

在项目根目录创建 `.agents/` 目录，存放专门面向 AI 智能体的工作手册，包括架构文档、不可变约束、常用命令、排障指南、角色定义等。让 AI Agent 进入项目后先读手册，减少摸索，避免踩坑，提高协作效率。

## 问题现象

AI 智能体参与项目开发时常见的痛点：

1. **信息摸索成本高**：AI 需要花大量时间翻代码理解项目结构
2. **重复踩坑**：人类都踩过的坑，AI 还要再踩一遍
3. **方向跑偏**：AI 不知道项目的"禁区"和"红线"，瞎改一气
4. **上下文碎片化**：项目知识散落在代码注释、PR 描述、文档各处
5. **输出不合规**：AI 产出的代码/文档不符合项目规范，需要大量返工

## 解决方案

在项目根目录创建 `.agents/` 目录，结构如下：

```
项目根/
├── .agents/                    # ← AI 智能体工作手册
│   ├── README.md              # 入口索引（总导航）
│   ├── architecture.md        # 架构与文件地图
│   ├── constraints.md         # 不可变约束（踩坑清单）
│   ├── commands.md            # 常用命令与验证
│   ├── postmortems/           # 任务复盘报告
│   │   └── task-summary-YYYYMMDD.md
│   ├── roles/                 # 角色定义
│   │   └── xxx-debugger.md    # 专项排障角色
│   ├── rules/                 # 规则与规范
│   ├── templates/             # 模板
│   └── tools/                 # 工具说明
├── AGENTS.md                  # ← AI Agent 入口协议
├── src/                       # 源码
├── docs/                      # 人类用文档
└── ...
```

### 入口协议（AGENTS.md）

在项目根目录放 `AGENTS.md`，作为 AI Agent 的第一入口：

```markdown
# AI Agent Instructions

## 启动协议
当你进入本项目时，先执行以下步骤：
1. 读取本文件全文
2. 按导航表读取需要的规范
3. 确认理解后再开始任务

## 导航索引
| 文档 | 用途 |
|------|------|
| `.agents/architecture.md` | 项目架构、文件地图、分层设计 |
| `.agents/constraints.md` | 不可变约束（违反必失败） |
| `.agents/commands.md` | 构建命令、诊断命令、产物验证 |
| `.agents/roles/xxx-debugger.md` | Nuitka 排障专家指南 |

## 文档边界
- AGENTS.md / .agents/ 面向 AI 智能体
- README.md / docs/ 面向人类读者
- 职责分离，互不替代
```

### 四大核心文档

| 文档 | 内容 | AI 必读时机 |
|------|------|------------|
| **architecture.md** | 架构图、文件地图、关键设计决策 | 新进入项目时 |
| **constraints.md** | 不可变约束、踩坑历史、代码位置 | 动手改代码前 |
| **commands.md** | 构建/测试/调试命令、验证方法 | 执行任务前 |
| **roles/xxx.md** | 专项角色指南（排障/审查/优化） | 对应类型任务 |

## 模式价值

### 对 AI Agent 的价值

1. **上手快**：读 10 分钟手册，胜过翻 2 小时代码
2. **不踩坑**：已知坑点提前知道，少走弯路
3. **方向准**：知道什么能做什么不能做，不瞎试
4. **产出规范**：符合项目规范，减少返工
5. **可排障**：遇到问题有指南，不是两眼一抹黑

### 对人类团队的价值

1. **知识沉淀**：隐性经验 → 显性文档
2. **新人培养**：新人也可以读手册，不只是 AI
3. **协作成本低**：和 AI 沟通有共同语境
4. **可审计**：AI 的行为有依据，出问题可追溯

## 文档边界

非常重要的一点：`.agents/` 和 `docs/` 是两套体系，职责分离。

| 维度 | `.agents/`（AI 用） | `docs/`（人用） |
|------|---------------------|-----------------|
| **读者** | AI 智能体 | 人类开发者 |
| **风格** | 结构化、列表化、便于检索 | 叙事性、讲解性、便于理解 |
| **内容** | 约束、命令、排障、角色 | 背景、原理、教程、API |
| **更新频率** | 高（每次踩坑都更新） | 低（版本发布时更新） |
| **深度** | 实用导向，怎么干活 | 认知导向，为什么这么做 |

**不是替代关系，是互补关系**。人类读的文档 AI 也可以读，但 `.agents/` 是专门为 AI 优化的"快速上手包"。

## 适用场景

- 有 AI 智能体参与开发的项目
- 踩坑多、约束多的复杂项目
- 需要快速上手的新项目
- 人员流动大、知识传承难的团队
- 多个 AI 角色协作的项目

## 正反例

### 正例

```
notebook/
├── AGENTS.md              # AI 入口协议（必读）
└── .agents/
    ├── architecture.md    # 架构 + 文件地图
    ├── constraints.md     # 17 条不可变约束
    ├── commands.md        # 常用命令速查
    ├── postmortems/       # 复盘报告
    └── roles/
        └── nuitka-debugger.md  # 排障指南
```

→ **结构清晰，职责明确，AI 进来就知道先读什么**

### 反例

```
project/
├── README.md              # 只有人类用的文档
└── docs/                  # 全是原理性文档
    ├── architecture.md
    └── tutorial.md
```

→ **AI 进来瞎摸索，不知道约束，容易踩坑，产出返工率高**

## 模式扩展

### 扩展 A：多角色分工

复杂项目可以定义多个 AI 角色，各有专长：

```
.agents/roles/
├── orchestrator.md        # 协调者（任务分配）
├── developer.md           # 开发者（写代码）
├── reviewer.md            # 审查者（代码审查）
├── tester.md              # 测试者（写测试）
└── nuitka-debugger.md     # 专项专家（Nuitka 排障）
```

### 扩展 B：复盘沉淀

每次任务完成后写复盘，存入 `postmortems/`：

```
.agents/postmortems/
├── task-summary-20260701.md    # 2026-07-01 任务总结
├── task-summary-20260702.md    # 2026-07-02 任务总结
└── ...
```

知识持续积累，模式库持续丰富。

### 扩展 C：模板化产出

在 `.agents/templates/` 中放常用模板：

```
.agents/templates/
├── task-summary.md       # 任务总结模板
├── handoff.md            # 任务交接模板
├── code-review.md        # 代码审查模板
└── bug-report.md         # Bug 报告模板
```

AI 产出更规范，格式更统一。

## 与其他模式的关系

- **不可变约束清单（immutable-constraint-documentation）**：
  工作手册包含约束清单，约束清单是工作手册的核心组件

- **渐进式上下文披露（progressive-context-disclosure）**：
  工作手册是"第一层上下文"，AI 按需深入，不是一上来全塞给它

- **双区开发模型（dual-zone-development-model）**：
  `.agents/` 是"安全区"，源码是"生产区"，两区分离
