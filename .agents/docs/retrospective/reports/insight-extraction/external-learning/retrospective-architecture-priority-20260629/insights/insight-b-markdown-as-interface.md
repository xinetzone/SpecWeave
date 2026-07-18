---
id: "architecture-priority-insight-b"
title: "洞察 B：Human-First 文档天然不是 Agent-First 服务"
source: "insight-extraction.md#洞察-b"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/insights/insight-b-markdown-as-interface.toml"
---
# 洞察 B：Human-First 文档天然不是 Agent-First 服务

**现象**：当前 5 个指令集（retrospective/insight/atomization/export-report/atomic-commit）是写得很好的 Markdown 文档，但 Agent 无法"调用"它们，只能"阅读理解"后执行。

**深层洞察**：
- Markdown 文档是**叙事结构**（章节→段落→解释），适合人类线性阅读
- Agent 可调用服务需要**接口结构**（触发词→输入→输出→错误处理→检查清单）
- 两者不是同一维度——把 Markdown 文档改得再好也无法变成可调用服务
- Firecrawl 的 `/agent-onboarding/SKILL.md` 证明了一个关键设计：**用 Markdown 表达接口结构**——SKILL.md 本身是 Markdown，但它的结构（frontmatter元数据+触发词+决策树+检查清单）是机器可解析的

**可复用模式**：**Markdown即接口（Markdown-as-Interface）**
> SKILL.md 的五要素模型（Trigger-Ready Description + Decision Tree + Progressive Disclosure + Why-Explanation + Safety Checklist）解决了"人类可读"和"机器可调用"的矛盾。一个 SKILL.md 同时满足：
> - 人类读：能理解这个能力是做什么的、为什么这么设计
> - Agent 用：有明确的触发词、决策路径、执行步骤、安全检查
> - 机器解析：frontmatter 中有结构化元数据（id、触发词、参数类型）
