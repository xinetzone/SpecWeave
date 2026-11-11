---
id: "workflows"
title: "工作流索引"
source: ".agents/workflows/README.md"
---
# 工作流索引

本目录定义多智能体协作的标准工作流，用于规范各角色在常见开发场景中的协作方式。

| 工作流 | 适用场景 | 参与角色 | 入口 |
|---|---|---|---|
| 功能开发 | 新功能开发 | 全部角色 | [feature-development.md](feature-development.md) |
| 代码审查 | PR 审查 | developer, reviewer, orchestrator | [code-review.md](code-review.md) |
| 测试流程 | 测试执行 | tester, developer, reviewer | 见 SpecWeave 开源仓库 |

## 使用说明

1. 根据任务类型选择对应工作流，通过流程图了解执行顺序。
2. 查阅角色参与表确认各角色的输入、输出与职责。
3. 按步骤说明执行，确保每步完成标志达成。
4. 步骤间交接时使用 [../templates/handoff-template.md](../templates/handoff-template.md) 模板。
5. 角色能力定义与职责边界参见 [../roles/README.md](../roles/README.md)；交接与通信遵循 `protocols/` 目录下的协议。