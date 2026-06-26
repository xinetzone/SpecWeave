# 智能体角色体系

> **来源**：从 `README.md` "智能体角色体系"章节拆分

## 角色概览

本项目定义了 7 个智能体角色，分为核心开发角色（5 个）与治理角色（2 个），各司其职、互不越权：

| 角色 | ID | 层级 | 职责 | 能力边界（Non-Goals） |
|---|---|---|---|---|
| 编排协调者 | `orchestrator` | 核心 | 任务分解、流程协调、冲突仲裁 | 不编写业务代码、不做技术决策 |
| 架构师 | `architect` | 核心 | 技术方案设计、架构决策 | 不负责代码实现细节、不编写测试 |
| 开发者 | `developer` | 核心 | 代码实现、重构、缺陷修复 | 不擅自变更架构、不绕过审查合并 |
| 代码审查者 | `reviewer` | 核心 | 代码质量审查、规范校验 | 不直接修改业务代码、不执行验收测试 |
| 测试工程师 | `tester` | 核心 | 测试用例编写、执行、覆盖率 | 不负责生产部署、不修改业务逻辑 |
| 联合创始者 | `co-founder` | 治理 | 愿景确立、协作契约奠基、关键决策仲裁 | 不负责日常任务分配、不负责代码实现 |
| 团队管理员 | `team-admin` | 治理 | 团队创建管理、权限分配、新角色自动创建 | 不编写业务代码、不越权管理其他团队 |

## 角色定义文件

每个角色定义文件位于 `.agents/roles/<role>.md`，使用 TOML frontmatter 声明绑定关系：

```toml
+++
id = "orchestrator"
domain = "coordination"
layer = "orchestration"

[bindings]
rules = [".agents/protocols/handoff.md", ".agents/protocols/messaging.md"]
references = [".agents/workflows/feature-development.md"]
skills = []
+++
```

对应的系统提示词与 few-shot 示例位于 `.agents/prompts/<role>/`（治理角色 co-founder 与 team-admin 的提示词内嵌于角色定义文件中）。

## 详细定义

| 角色 | 定义文件 | 系统提示词 | Few-shot 示例 |
|------|---------|-----------|-------------|
| orchestrator | [.agents/roles/orchestrator.md](../.agents/roles/orchestrator.md) | [system-prompt.md](../.agents/prompts/orchestrator/system-prompt.md) | [few-shot.md](../.agents/prompts/orchestrator/few-shot.md) |
| architect | [.agents/roles/architect.md](../.agents/roles/architect.md) | [system-prompt.md](../.agents/prompts/architect/system-prompt.md) | [few-shot.md](../.agents/prompts/architect/few-shot.md) |
| developer | [.agents/roles/developer.md](../.agents/roles/developer.md) | [system-prompt.md](../.agents/prompts/developer/system-prompt.md) | [few-shot.md](../.agents/prompts/developer/few-shot.md) |
| reviewer | [.agents/roles/reviewer.md](../.agents/roles/reviewer.md) | [system-prompt.md](../.agents/prompts/reviewer/system-prompt.md) | [few-shot.md](../.agents/prompts/reviewer/few-shot.md) |
| tester | [.agents/roles/tester.md](../.agents/roles/tester.md) | [system-prompt.md](../.agents/prompts/tester/system-prompt.md) | [few-shot.md](../.agents/prompts/tester/few-shot.md) |
| co-founder | [.agents/roles/co-founder.md](../.agents/roles/co-founder.md) | （内嵌于定义文件） | — |
| team-admin | [.agents/teams/team-admin.md](../.agents/teams/team-admin.md) | （内嵌于定义文件） | — |

> **关联模块**：
> - `../README.md`
> - `collaboration.md`
> - `../.agents/roles/README.md`
> - `../AGENTS.md`