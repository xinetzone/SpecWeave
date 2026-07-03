---
id: "pattern-extraction-errors-gotchas-reference"
title: "错误处理、Gotchas陷阱与参考速查表"
source: "SKILL.md#05-errors-gotchas-reference"
x-toml-ref: "../../../../.meta/toml/.agents/skills/pattern-extraction-cmd/SKILL/05-errors-gotchas-reference.toml"
---
# 错误处理、Gotchas陷阱与参考速查表

## 11. 常见错误处理

| 问题场景 | 处理方式 |
|---------|---------|
| 不确定应该归到哪个分类 | 先看CATEGORIES.md的核心关注点和边界说明，仍不确定时放到governance-strategy/并标注"待分类" |
| 类似模式已存在 | 使用模式合并判断标准，考虑更新现有模式而非新建 |
| 模式太抽象没有具体案例 | 停留在洞察层面，不要强行沉淀为模式；等有第二个验证案例再创建 |
| frontmatter字段校验失败 | 运行check-pattern-quality.py查看具体错误，按提示补全字段 |
| 索引更新冲突 | 先运行check-index --fix自动修复，仍有冲突时手动检查README.md |


## 12. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **模式必须放在正确分类目录**：三个顶层目录（methodology-patterns/、architecture-patterns/、code-patterns/）有严格的分类边界，放错目录不会被索引脚本识别，成熟度统计也不会计入。方法论模式还需放到正确的7个子主题目录下，分类不确定时先查CATEGORIES.md。
- **frontmatter必须含maturity字段**：新创建的模式默认maturity="L1"，此字段缺失会导致质量检查失败。成熟度等级影响推荐使用优先级——L0初始（不推荐直接使用）、L1验证（至少1次验证）、L2成熟（多次验证可复用）、L3优化（跨场景复用）、L4标准化（已集成CI）。
- **模式名称用kebab-case英文小写**：文件名和frontmatter中的id字段必须使用kebab-case格式（如`markdown-as-interface`、`three-layer-architecture`），与Skill命名规则一致。不要使用中文、驼峰、下划线或空格，否则索引和引用链接会断裂。
- **提取模式前先检查是否已存在**：创建新模式前务必先用`check-duplication-cmd`或直接搜索`docs/retrospective/patterns/`目录，避免重复创建相似模式。如果已有类似模式，应更新现有模式的validation_count或考虑合并，而不是新建。
- **反模式章节必须包含**：每个模式文档必须有"反模式"章节，说明什么情况下不应使用此模式、常见的错误用法是什么。缺少反模式章节的模式会被质量检查扣分，因为它无法帮助使用者判断适用边界。


## 13. 关键参考速查表

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 模式文档标准结构（frontmatter/章节/案例） | L1 | [第6.1节](#61-模式文档标准结构) | 创建新模式时 |
| 模式库总索引与成熟度标准 | L2 | [patterns/README.md](../../../../docs/retrospective/patterns/README.md) | 了解成熟度定义和统计 |
| 方法论模式7个子主题分类边界 | L2 | [CATEGORIES.md](../../../../docs/retrospective/patterns/methodology-patterns/CATEGORIES.md) | 判断方法论模式归属时 |
| 模式合并边界判断标准 | L2 | [pattern-merge-boundary.md](../../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md) | 合并/拆分模式时 |
| 洞察萃取漏斗 | L2 | [extraction-four-layer-funnel.md](../../../../docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/extraction-four-layer-funnel.md) | 从洞察萃取模式时 |
| 质量检查脚本 | L2 | [check-pattern-quality.py](../../../../.agents/scripts/check-pattern-quality.py) | 验证模式格式 |
| 成熟度管理脚本 | L2 | [pattern-maturity.py](../../../../.agents/scripts/pattern-maturity.py) | 更新validation_count/reuse_count |


## 14. Changelog

- **v1.1.0** (2026-07-01): 添加CMD-LOG执行日志规范。在决策树前强制记录触发输入参数（trigger_phrase/operation_type/source等7个字段），方便后续排查逻辑分支选择问题；新增9个特有事件定义（CMD_START/BRANCH_SELECTED/CLASSIFY_AUTO等），支持决策路径回溯。
- **v1.0.0** (2026-07-01): 初始版本。基于markdown-as-interface五要素模型，封装模式沉淀标准化流程，整合3个现有自动化脚本。


---

## 相关模式

- - [insight-cmd Skill](../../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)

← 上一章: [CMD-LOG执行日志与质量安全清单](04-cmd-log-quality.md) | **[返回索引](../SKILL.md)**
