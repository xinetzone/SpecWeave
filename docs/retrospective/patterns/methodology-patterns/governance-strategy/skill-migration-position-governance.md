+++
id = "skill-migration-position-governance"
domain = "methodology"
layer = "methodology"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/reports/task-reports/retrospective-kg-skill-migration-20260710/insight-extraction.md"

[bindings]
rules = []
references = ["format-evidence-over-memory-pattern.md", "convention-driven-creation.md"]
skills = ["knowledge-graph-generator"]
related_patterns = ["format-evidence-over-memory-pattern.md", "convention-driven-creation.md"]
+++

# Skill迁移位置治理：统一Skill存放位置的五步标准化流程

## 模式概述

当项目存在多个Skill存放位置（如 `.trae/skills/` 和 `.agents/skills/`）时，Skill可能分散在不同目录，导致可发现性差、管理不一致、依赖关系断裂。本模式提供从分散位置到统一位置的标准化五步迁移流程，确保所有项目Skill纳入统一管理体系。

## 问题现象

- Skill被创建在 `.trae/skills/`（Trae IDE平台默认位置），但项目Skill管理在 `.agents/skills/`
- 一个Skill孤立在非标准位置，README索引中找不到
- Skill引用的脚本在 `.agents/scripts/`，但Skill本身在 `.trae/skills/`——依赖关系跨命名空间
- 新Skill创建时不知道应该放在哪个目录

## 解决方案

### 五步迁移流程

```
步骤1：分析 → 对比两个目录的Skill数量和类型，判断迁移方向
步骤2：决策 → 基于"依赖内聚+分类归属+一致性"三原则做决策
步骤3：迁移 → 创建新位置SKILL.md，更新内部路径引用
步骤4：索引更新 → 更新README.md索引表、changelog、计数
步骤5：旧目录清理 → 删除旧位置文件，清理空目录
```

### 三原则决策框架

| 原则 | 说明 | 本次应用 |
|------|------|---------|
| **依赖内聚** | Skill引用的脚本/模板/配置应在同一命名空间 | 脚本在 `.agents/scripts/`，Skill应在 `.agents/skills/` |
| **分类归属** | Skill应放在与同类Skill相同的目录 | 14个Skill在 `.agents/skills/`，知识图谱生成器也是脚本门面 |
| **一致性** | 同类事物应有相同管理方式 | 避免一个Skill在 `.trae/skills/` 其余在 `.agents/skills/` |

### 位置归属判定决策树

```
Skill应该放在哪里？
├─ Skill引用的脚本在 .agents/scripts/？ → .agents/skills/（依赖内聚）
├─ 同类Skill（脚本门面/命令门面/完整Skill）已集中在某个目录？ → 跟随同类（分类归属）
├─ 项目有Skill管理规范指定了位置？ → 遵循规范（一致性）
└─ 以上都不适用？ → .agents/skills/（默认位置）
```

## 适用场景

- 从Trae IDE平台生成的Skill需要纳入项目统一管理
- 新创建的Skill需要确定存放位置
- 重构时发现Skill散落在非标准位置
- 项目Skill目录结构变更后的迁移

## 实际案例

### 案例：knowledge-graph-generator 迁移

**背景**：`knowledge-graph-generator` Skill最初通过Trae IDE创建，默认放在 `.trae/skills/`，而项目其余14个Skill均在 `.agents/skills/`。

**迁移过程**：
1. 分析：`.trae/skills/` 仅1个Skill，`.agents/skills/` 14个Skill，迁移方向明确
2. 决策：三原则全部指向 `.agents/skills/`（脚本在 `.agents/scripts/`、同类在 `.agents/skills/`、管理规范在 `.agents/skills/`）
3. 迁移：创建 `.agents/skills/knowledge-graph-generator/SKILL.md`（243行，五要素格式）
4. 索引：README.md 脚本命令门面 5→6，新增 v1.5 changelog
5. 清理：删除 `.trae/skills/knowledge-graph-generator/` 目录

**效果**：Skill纳入统一管理体系，可发现性提升（README索引可见），依赖关系内聚（与 `.agents/scripts/` 在同一命名空间）。

## 反模式

1. **仅移动文件不更新索引**：Skill文件移动后README索引未更新，导致"索引中找不到但文件存在"的幽灵状态
2. **迁移后不清理旧位置**：旧位置残留文件，后续可能被误认为"还有一个Skill"，造成混淆
3. **跳过决策分析直接迁移**：不分析两个目录的现状就做迁移，可能迁移到错误方向

## 相关模式

- [format-evidence-over-memory-pattern.md](format-evidence-over-memory-pattern.md)：创建文件时以现有文件格式为准，不以记忆为准——本模式在迁移时也需遵循此原则
- [convention-driven-creation.md](convention-driven-creation.md)：基于规范驱动创建——本模式为Skill创建提供了位置规范