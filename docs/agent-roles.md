# 智能体角色体系

> **来源**：从 `README.md` "智能体角色体系"章节拆分

## 角色概览

本项目定义了 5 个核心智能体角色，各司其职、互不越权：

| 角色 | ID | 职责 | 能力边界（Non-Goals） |
|---|---|---|---|
| 编排协调者 | `orchestrator` | 任务分解、流程协调、冲突仲裁 | 不编写业务代码、不做技术决策 |
| 架构师 | `architect` | 技术方案设计、架构决策 | 不负责代码实现细节、不编写测试 |
| 开发者 | `developer` | 代码实现、重构、缺陷修复 | 不擅自变更架构、不绕过审查合并 |
| 代码审查者 | `reviewer` | 代码质量审查、规范校验 | 不直接修改业务代码、不执行验收测试 |
| 测试工程师 | `tester` | 测试用例编写、执行、覆盖率 | 不负责生产部署、不修改业务逻辑 |

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

对应的系统提示词与 few-shot 示例位于 `.agents/prompts/<role>/`。

## 详细定义

| 角色 | 定义文件 | 系统提示词 | Few-shot 示例 |
|------|---------|-----------|-------------|
| orchestrator | [.agents/roles/orchestrator.md](../.agents/roles/orchestrator.md) | [system-prompt.md](../.agents/prompts/orchestrator/system-prompt.md) | [few-shot.md](../.agents/prompts/orchestrator/few-shot.md) |
| architect | [.agents/roles/architect.md](../.agents/roles/architect.md) | [system-prompt.md](../.agents/prompts/architect/system-prompt.md) | [few-shot.md](../.agents/prompts/architect/few-shot.md) |
| developer | [.agents/roles/developer.md](../.agents/roles/developer.md) | [system-prompt.md](../.agents/prompts/developer/system-prompt.md) | [few-shot.md](../.agents/prompts/developer/few-shot.md) |
| reviewer | [.agents/roles/reviewer.md](../.agents/roles/reviewer.md) | [system-prompt.md](../.agents/prompts/reviewer/system-prompt.md) | [few-shot.md](../.agents/prompts/reviewer/few-shot.md) |
| tester | [.agents/roles/tester.md](../.agents/roles/tester.md) | [system-prompt.md](../.agents/prompts/tester/system-prompt.md) | [few-shot.md](../.agents/prompts/tester/few-shot.md) |

> **关联模块**：
> - `../README.md`
> - `collaboration.md`
> - `../.agents/roles/README.md`
> - `../AGENTS.md`