---
id: "prompts-orchestrator-few-shot"
title: "Orchestrator Few-shot 示例"
source: "AGENTS.md#提示词"
x-toml-ref: "../../../.meta/toml/.agents/prompts/orchestrator/few-shot.toml"
---
# Orchestrator Few-shot 示例

## 示例 1: 功能开发任务分解与分配

**输入**: 用户需求：实现一个用户登录功能，支持邮箱密码登录与第三方 OAuth 登录。

**输出**:
任务分解与分配方案如下：

| 任务 ID | 任务描述 | 目标角色 | 输入依赖 | 预期输出 | 验收标准 |
|---|---|---|---|---|---|
| T-001 | 登录模块架构设计 | architect | 用户需求文档 | 架构设计文档、技术选型说明 | 方案评审通过，覆盖邮箱与 OAuth 两种场景 |
| T-002 | 登录功能代码实现 | developer | T-001 架构文档 | 可运行的登录模块代码 | 通过单元测试，符合编码规范 |
| T-003 | 登录功能测试用例 | tester | T-001 架构文档 | 测试用例集与执行报告 | 覆盖率不低于 85%，包含异常场景 |
| T-004 | 代码质量审查 | reviewer | T-002 代码产出 | 审查报告与改进建议 | 无严重与高危问题遗留 |

执行顺序：T-001 → (T-002, T-003 并行) → T-004。

## 示例 2: 角色冲突仲裁

**输入**: developer 与 reviewer 就某段代码是否需要重构产生分歧。developer 认为当前实现满足功能需求，reviewer 认为存在重复代码需重构。

**输出**:
冲突仲裁结论：

- 冲突描述：登录模块中存在两处相似的参数校验逻辑，reviewer 建议抽取公共方法，developer 认为当前实现可读性可接受。
- 涉及角色：developer、reviewer。
- 裁决依据：依据 `.agents/protocols/messaging.md` 第 3 条，重复代码超过 10 行应进行重构。
- 最终决定：支持 reviewer 建议，要求 developer 抽取公共校验方法，并在交接时附带重构后的单元测试。
- 升级条件：若重构工作量超过 2 人日，则升级至人工评估。
