# 团队规范（Standards）

> 本目录存放团队级执行规范文档，定义跨命令集、跨模块的统一标准，确保执行一致性和可审计性。

## 规范文档索引

| 规范文档 | 说明 | 适用范围 |
|---------|------|---------|
| [CMD-LOG命令集执行日志规范](cmd-log-specification.md) | 5大命令集Skill门面的结构化执行日志格式、事件枚举、解析方法和实施检查清单 | retrospective/insight/export-report/atomization/atomic-commit 全部命令集 |

## 规范分类体系

团队规范按以下维度组织：

| 分类 | 前缀 | 存放位置 | 说明 |
|------|------|---------|------|
| 日志规范 | `*-log-*.md` | docs/standards/ | 各类结构化日志的格式、字段、事件定义 |
| 流程规范 | `*-process-*.md` | docs/standards/ | 跨命令集的执行流程标准 |
| 格式规范 | `*-format-*.md` | docs/standards/ | 输出物格式、命名、元数据标准 |

## 与其他规范的关系

```
docs/standards/          ← 团队级执行规范（跨命令集、跨模块）
├── cmd-log-specification.md
└── ...

.agents/rules/           ← AI智能体治理规则（约束AI行为）
.agents/commands/        ← 命令集详细文档（单命令集SOP）
.agents/skills/          ← Skill门面（触发词+执行指引+日志）
docs/development-standards.md  ← 开发规范（代码风格、提交规范）
docs/knowledge/          ← 技术知识库（架构决策、故障排查）
docs/retrospective/patterns/  ← 可复用模式（代码/架构/方法论模式）
```

## 新增规范流程

1. 在 `.agents/rules/` 或 `.agents/commands/` 中先形成执行经验
2. 经验经至少1次实际执行验证后，提炼为团队规范
3. 在本目录创建规范文档，使用TOML frontmatter标注id/domain/source
4. 更新本README索引表
5. 同步更新所有引用该规范的Skill门面/命令文档
