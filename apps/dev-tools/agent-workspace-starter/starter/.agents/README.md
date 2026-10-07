---
id: "agents-readme"
title: ".agents 目录说明"
source: "templates/agent-workspace-hub/.agents/README.md + .agents/README.md"
---

# .agents 目录说明

本目录是项目 AI 智能体规范的容器，存放角色定义、规则、协议、工作流、模板、指令集、检查清单与技能门面。所有智能体在任务前应先通过项目根目录的 `AGENTS.md` 进行上下文路由，再进入本目录加载对应规范。

## 目录结构

```
.agents/
├── ONBOARDING.md             # [Core] 入门指南（L0 入口）
├── capability-registry.md    # [Core] 能力索引（L1 静态索引）
├── global-core-rules.md      # [Core] 全局核心规则
├── context-routing.md        # [Core] 上下文路由表
├── roles/  rules/            # [Core] 角色定义 / 规则体系
├── protocols/  workflows/    # [Core] 协作协议 / 标准工作流
├── templates/  commands/     # [Core] 模板资产 / 标准化指令集
├── checklists/               # [Core] 标准化检查清单
├── modules/ teams/ prompts/  # [Core] 自我演进 / 团队 / 提示词（导览）
├── tools/ worlds/            # [Core] 工具规范 / 协作环境（导览）
├── capabilities/ cases/      # [Core] 渐进式披露 / 复用案例（导览）
├── systems/                  # [Core] 系统架构（导览）
└── skills/                   # [Tools] Skill 技能门面
```

> 标记说明：`[Core]` = 核心规范层（稳定规则/协议/定义），`[Tools]` = 执行工具层。

## 规范分层治理（Core vs Tools）

| 维度 | Core 层（规范核心） | Tools 层（执行工具） |
|------|---------------------|----------------------|
| 定位 | 定义"应该怎么做"的稳定规范 | 实现"具体怎么做"的可执行工具 |
| 依赖方向 | 不依赖 Tools 层 | 必须遵循 Core 层规范 |
| 面向对象 | 认知层（决策依据） | 执行层（操作实现） |

依赖方向单向（Tools → Core）。Skill 门面规范见 [skills/README.md](skills/README.md)。

## 与 AGENTS.md 的关系

- `AGENTS.md` 是精简入口，定义启动协议与核心规范入口导航，是智能体启动时首先读取的最高优先级契约。
- `.agents/` 是详细规范容器，承载各角色、规则、协议、流程、模板与技能门面的具体内容。
- 两者关系为「入口 ↔ 容器」：`AGENTS.md` 负责路由与全局约束，`.agents/` 负责具体规范与可执行细节。
- 信息架构遵循 L0/L1/L2 渐进式披露：AGENTS.md + ONBOARDING.md(L0) → capability-registry.md + context-routing.md(L1) → 详细规范文档(L2)。