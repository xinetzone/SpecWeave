---
id: "roles"
title: "角色定义索引"
source: ".agents/roles/README.md"
---
# 角色定义索引

本目录包含多智能体协作系统中所有角色定义文件。每个角色通过 YAML frontmatter 声明其绑定关系，并通过 Markdown 正文描述职责边界。

## 角色职责矩阵

| 角色 | ID | 领域 | 层级 | 层级标记 | 核心职责 |
|---|---|---|---|---|---|
| 编排协调者 | orchestrator | coordination | orchestration | 标准 | 任务分配、流程协调 |
| 架构师 | architect | engineering | design | 标准 | 方案设计、架构决策 |
| 开发者 | developer | engineering | implementation | 标准 | 代码实现、重构 |
| 代码审查者 | reviewer | quality | assurance | 标准 | 质量审查、规范校验 |
| 测试工程师 | tester | quality | verification | 标准 | 测试编写、覆盖率 |
| Token优化专家 | token-optimizer | optimization | specialist | 💡 专家 | LLM Token 优化、成本-质量-延迟权衡、缓存策略 |
| 联合创始者 | co-founder | governance | founding | 🏛️ 联合创始 | 愿景确立、协作契约奠基 |

## 文件结构说明

```
.agents/roles/
├── README.md                    # 本文件，角色索引
├── orchestrator.md              # 编排协调者
├── architect.md                 # 架构师
├── developer.md                 # 开发者
├── reviewer.md                  # 代码审查者
└── tester.md                    # 测试工程师
```

## 使用方法

1. 每个角色文件包含 YAML frontmatter，用于声明绑定的规则、引用与技能。
2. Markdown 正文分为 Description、Responsibilities、Non-Goals 三部分，明确角色定位与边界。
3. 在工作流编排时，通过 `id` 字段引用对应角色。
4. 角色之间通过 Non-Goals 明确职责边界，避免职责重叠。

> 完整角色清单（含领域专属角色与协作场景）见 SpecWeave 开源仓库。