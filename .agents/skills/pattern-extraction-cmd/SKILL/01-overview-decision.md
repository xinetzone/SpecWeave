---
id: "pattern-extraction-overview-decision"
title: "Skill概述、功能描述与方案选择决策树"
source: "SKILL.md#01-overview-decision"
x-toml-ref: "../../../../.meta/toml/.agents/skills/pattern-extraction-cmd/SKILL/01-overview-decision.toml"
---
# Skill概述、功能描述与方案选择决策树

## 1. Skill ID
`pattern-extraction-cmd`


## 2. 功能描述

提供从洞察/复盘中标准化萃取可复用模式的能力，完成"识别→分类→生成→入库→验证"闭环：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **全新模式创建** | ⭐ 从洞察/经验中提炼新模式 | 标准frontmatter+完整结构，符合分类规范 |
| **现有模式更新** | ⭐ 模式被验证/复用后更新成熟度 | 自动更新validation_count/reuse_count/maturity字段 |
| **模式合并/重构** | ⭐ 多个相似模式需要合并或拆分 | 遵循模式合并边界判断标准 |

核心功能：识别可复用模式→判断分类归属→生成标准TOML frontmatter→生成模式文档结构→更新索引README→运行质量检查→更新成熟度统计。

> **为什么用本Skill而非手动写模式文档？** 手动写模式容易遗漏frontmatter必填字段、放错分类目录、忘记更新索引、不遵循正反例结构要求；本Skill封装了184个模式沉淀的最佳实践和3个自动化脚本（pattern-maturity.py/check-pattern-quality.py/pattern-maturity-stats.py），确保模式质量可预测。


## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "模式沉淀"、"萃取模式"、"模式入库"、"沉淀为模式"
- "可复用模式"、"生成模式文档"、"更新模式库"
- "pattern extraction"、"pattern 沉淀"
- 复盘/洞察完成后，用户说"把这个经验沉淀下来"、"这个可以做成模式"
- 需要更新模式成熟度、validation_count、reuse_count

> **关于触发**：即使没有明确说"用模式萃取命令"，只要涉及从经验/洞察/复盘中提炼可复用知识并入库到docs/retrospective/patterns/，就应该使用本Skill。模式沉淀是知识复利的核心环节——"产出价值=基础×抽象层级^复用次数"，不要跳过。


## 4. 方案选择决策树

```
需要沉淀模式？
├─ 从新洞察/经验提炼全新模式？ → 全新模式创建（第5节）
│  ├─ 架构相关？ → architecture-patterns/
│  ├─ 具体代码技巧？ → code-patterns/
│  └─ 方法论/流程/AI协作？ → methodology-patterns/<子主题>/
├─ 模式被成功应用/复用需要更新成熟度？ → 现有模式更新（第6节）
├─ 多个模式相似需要合并/拆分？ → 模式合并/重构（第7节）
└─ 只是想查找/阅读已有模式？ → 直接查阅 docs/retrospective/patterns/ 对应目录README
```

**与其他Skill的关系**：
- 复盘流程S5步骤使用本Skill沉淀模式
- 洞察萃取完成后使用本Skill入库
- 模式文档过大时使用 `atomization-cmd` 拆分
- 沉淀完成后使用 `docgen-cmd` 更新导航索引

### ⚠️ 强制：触发时必须记录输入参数日志

每次本Skill被触发、进入决策树**之前**，必须输出一条CMD-LOG日志记录完整输入参数，方便后续排查逻辑分支选择问题：

```
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S0 | event=CMD_START | session=<SESSION_ID> | msg=开始模式萃取：<操作简述> | ctx={"trigger_phrase":"<用户触发短语>","operation_type":"<create|update|merge|query>","source":"<来源文件/对话>","pattern_name":"<模式名称>","user_explicit":<true|false>,"dry_run":<true|false>,"auto_classify":<true|false>}
```

**ctx字段必填说明**（第9节执行日志有完整规范）：
- `trigger_phrase`：用户触发时的原始短语（如"把这个洞察沉淀成模式"）
- `operation_type`：决策树选择的操作类型（create=新建/update=更新/merge=合并/query=查询）
- `source`：来源文件路径或对话上下文标识
- `pattern_name`：用户指定的模式名称（可空）
- `user_explicit`：用户是否明确指定了操作类型（true=用户说"新建模式"/false=自动判断）
- `dry_run`：是否为预览模式
- `auto_classify`：是否自动分类目录（true=自动判断/false=用户指定）

> **为什么必须在决策前记录参数？** 模式萃取涉及多层分类决策（架构/代码/方法论→子主题→成熟度初始值），如果后续发现分类错误或选错了操作类型，没有触发时的输入参数日志就无法回溯"当时为什么选了这个分支"。CMD_START日志在决策前输出，记录原始输入，是排查分支逻辑问题的关键证据。


---

## 相关模式

- - [insight-cmd Skill](../../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)

**[返回索引](../SKILL.md)** | 下一章 → [核心步骤与全新模式创建方案](02-core-steps-create.md)
