---
id: "p-arch-002"
source: "export-suggestions.md#p-arch-002"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-architecture-priority-20260629/export/patterns/p-arch-002-markdown-as-interface.toml"
---
# P-ARCH-002 Markdown即接口

**问题**：Markdown 文档是叙事结构（适合人类阅读），但 Agent 需要接口结构（可调用）。

**解决方案**：用 Markdown 表达接口结构——SKILL.md 同时满足人类可读和机器可调用：
- frontmatter：结构化元数据（id、触发词、参数类型）
- 触发词描述：自然语言触发条件（Agent-First）
- 决策树：明确的分支判断逻辑
- 核心步骤：可执行的操作序列
- 安全检查清单：执行前后的验证点

**成熟度**：L3（有 forum-posting 成功实例，有 SKILL-TEMPLATE 模板）
