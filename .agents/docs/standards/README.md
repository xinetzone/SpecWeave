# 团队规范（Standards）

> **文档边界说明**：成熟的AI智能体规范已归档至 `.agents/` 目录。本目录保留为人类读者的规范导航与待成熟规范暂存区。
> - 权威规范（机器可读，AI智能体必须遵循）→ [`.agents/rules/`](../../rules/README.md)
> - 本目录（人类可读导航/暂存）→ 当前位置

## 规范文档索引

| 规范文档 | 说明 | 权威版本位置 |
|---------|------|-------------|
| [CMD-LOG命令集执行日志规范](cmd-log-specification.md) | 5大命令集Skill门面的结构化执行日志格式、事件枚举、解析方法和实施检查清单 | [.agents/rules/cmd-log-specification.md](../../rules/cmd-log-specification.md) |

## 规范分类体系

团队规范按以下维度组织：

| 分类 | 前缀 | 成熟后归档位置 | 说明 |
|------|------|-------------|------|
| 日志规范 | `*-log-*.md` | `.agents/rules/` | 各类结构化日志的格式、字段、事件定义 |
| 流程规范 | `*-process-*.md` | `.agents/protocols/` 或 `.agents/rules/` | 跨命令集的执行流程标准 |
| 格式规范 | `*-format-*.md` | `.agents/rules/` | 输出物格式、命名、元数据标准 |

## 规范成熟度生命周期

```
执行经验形成(.agents/commands/或.agents/skills/)
    → 提炼为待成熟规范(.agents/docs/standards/暂存)
    → 至少1次实际执行验证
    → 归档至.agents/对应子目录（权威版本）
    → .agents/docs/standards/保留导航指针
```

## 与其他目录的关系

```
 .agents/docs/standards/  ← 人类读者导航+待成熟规范暂存
└── (导航指针指向.agents/)

.agents/rules/           ← AI智能体治理规则（权威版本）
.agents/protocols/       ← 协作协议（权威版本）
.agents/commands/        ← 命令集详细文档（单命令集SOP）
.agents/skills/          ← Skill门面（触发词+执行指引+日志）
`.agents/docs/development-standards.md` ← 开发规范（代码风格、提交规范）
 .agents/docs/knowledge/  ← 技术知识库（架构决策、故障排查、操作指南）
 .agents/docs/retrospective/patterns/  ← 可复用模式（代码/架构/方法论模式）
```
