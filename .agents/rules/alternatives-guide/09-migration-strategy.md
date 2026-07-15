---
id: "rules-alt-migration-strategy"
title: "09 迁移策略"
source: "alternatives-guide.md#migration-strategy"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/09-migration-strategy.toml"
---
# 09 迁移策略


从现有硬编码代码迁移到上述替代方案，应采用渐进式策略，避免一次性大规模重构带来的回归风险。

## 1. 先识别，后迁移

- 使用静态分析工具或手动审查识别当前代码库中的硬编码位置。
- 按类型标识（`HARD-CFG`、`HARD-NUM` 等）分类记录，建立硬编码清单。
- 迁移前确保已有充分测试覆盖，作为功能等价的回归保障。
- **不打散已有功能**：单次迁移聚焦同一模块的同一类硬编码，不影响其他功能。

## 2. 新代码零容忍

- 代码审查阶段强制检查：任何新增代码不得包含硬编码值。
- 在 CI 流水线中集成硬编码检测规则（如自定义 lint 规则），自动拦截违规提交。
- 团队规范明确：所有配置项、常量、消息文本、正则模式必须走替代方案路径。

## 3. 按风险等级分批次重构

| 批次 | 优先级 | 硬编码类型 | 迁移范围 | 理由 |
|---|---|---|---|---|
| 第 1 批 | P0 | `HARD-CFG`、`HARD-NUM`、`HARD-URL` | 配置参数、业务常量、API 端点 | 影响范围最大，更改频率最高，安全风险最突出 |
| 第 2 批 | P1 | `HARD-PATH`、`HARD-STR`（错误信息） | 路径定义、错误消息 | 提升可移植性，为国际化打基础 |
| 第 3 批 | P2 | `HARD-STR`（UI 文本）、`HARD-REGEX`、`HARD-STYLE`、`HARD-ENC` | UI 文本、正则模式、样式、编码常量 | 完善工程化体系，非阻塞性问题 |

## 4. 每次迁移后验证

- 运行全量单元测试与集成测试，确保功能等价。
- 对比迁移前后的行为（输入输出、边界条件、异常路径）。
- 更新相关文档与注释，注明配置项来源与引用路径。
- 迁移完成的硬编码清单项标记为"已消除"，纳入知识库存档。
---

## 相关模式

- [硬编码治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/)
- [三级问题解决](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [08 模板与脚手架](08-project-scaffold.md) | **[返回索引](../alternatives-guide.md)** | 下一章: [10 附录：硬编码检测清单](10-detection-checklist.md) →
