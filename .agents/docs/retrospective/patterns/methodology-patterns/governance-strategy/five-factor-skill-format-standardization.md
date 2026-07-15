+++
id = "five-factor-skill-format-standardization"
domain = "methodology"
layer = "methodology"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "../../../reports/task-reports/retrospective-kg-skill-migration-20260710/insight-extraction.md"

[bindings]
rules = []
references = ["skill-migration-position-governance.md"]
skills = ["knowledge-graph-generator", "link-check-cmd"]
related_patterns = ["skill-migration-position-governance.md", "convention-driven-creation.md"]
+++

# 五要素Skill格式标准化：从通用工具文档到项目标准Skill的改造

## 模式概述

从外部或平台生成的Skill通常是通用工具文档格式（API参考+使用教程），不符合项目标准Skill格式要求。本模式提供五要素改造清单，将通用工具文档升级为项目标准脚本命令门面格式。

## 问题现象

- Skill文件只有name+description frontmatter，缺少version/argument-hint/paths等字段
- 只有完整教程，没有触发词、决策树、安全检查清单、Gotchas
- 信息密度低，执行层知识不足
- AI Agent无法快速定位解决方案，需要阅读全文

## 解决方案

### 五要素改造清单

| 要素 | 必须包含 | 作用 |
|------|----------|------|
| **Frontmatter** | name/version/description/argument-hint/user-invocable/paths/x-toml-ref | 完整元数据，符合项目Schema |
| **决策树** | 方案选择分支（如：TOML配置 vs Python API） | 帮助AI Agent快速选择方案 |
| **安全检查清单** | 生成前逐项确认要点 | 防止常见配置错误，提升质量 |
| **Why解释** | 关键设计意图的 Why 引用块 | 解释"为什么要这样做"，便于理解约束 |
| **Gotchas** | 5-10条隐性陷阱（反直觉行为、易踩坑点） | 避免重复踩坑，减少错误概率 |

### 六个关键参考表格

所有Skill都应包含一个结构化的关键参考表：

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整参数文档 | L2 | 路径 | 需要高级参数时 |
| 核心源码 | L2 | 路径 | 需要理解实现细节时 |
| 模板文件 | L2 | 路径 | 需要参考配置写法时 |
| 生成结果示例 | L2 | 路径 | 需要查看生成效果时 |
| 关联指令集 | L1 | 路径 | 需要方法论协同参考时 |
| 关联知识库 | L2 | 路径 | 需要更多背景知识时 |

### 行数约束

- L1门面（SKILL.md）必须 ≤ 500行
- 完整详细内容放在L2层（脚本源码或单独文档）
- L1只放执行层决策支持，不重复L2内容

## 适用场景

- 从外部平台（Trae IDE）导入的Skill需要改造为项目格式
- 新创建的Skill需要遵循标准格式
- 现有Skill格式不符合要求，需要重构

## 实际案例

### 案例：knowledge-graph-generator 格式改造

**背景**：旧SKILL.md（213行）是通用工具文档，仅有API参考和使用教程，没有决策树、安全检查、Gotchas。

**改造前后对比**：

| 维度 | 旧版 | 新版 |
|------|------|------|
| Frontmatter | 仅name+description | 完整版（version/argument-hint/paths等） |
| 架构定位 | 无 | L0/L1/L2三层声明 |
| 决策树 | 无 | 4分支方案选择决策树 |
| 质量保障 | 无 | 9项安全检查清单 |
| 陷阱预防 | 无 | 5条Gotchas |
| 关键参考 | 零散 | 7条目结构化表格（含L1/L2层级） |

**效果**：行数从213增加到243（+14%），但信息密度显著提升，AI Agent可以更快做出决策，常见错误可以提前预防。

## 反模式

1. **L1包含过多L2内容**：把所有详细内容都放在L1，导致L1超过500行，违反渐进式披露三层架构
2. **省略安全检查清单**：认为"用户会自己检查"，但实际没有检查清单容易遗漏关键点
3. **省略Gotchas**：认为"这些都是常识"，但隐性陷阱正是最容易踩的坑

## 相关模式

- [skill-migration-position-governance.md](skill-migration-position-governance.md)：本模式是Skill迁移过程中的格式改造环节
- [convention-driven-creation.md](convention-driven-creation.md)：基于规范驱动创建新格式