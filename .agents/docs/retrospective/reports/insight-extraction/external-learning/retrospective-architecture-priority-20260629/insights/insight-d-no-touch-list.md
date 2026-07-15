---
id: "architecture-priority-insight-d"
title: "洞察 D：不重构决策的价值被严重低估"
source: "insight-extraction.md#洞察-d"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/insights/insight-d-no-touch-list.toml"
---
# 洞察 D：不重构决策的价值被严重低估

**现象**：本次评估明确列出了 6 个不重构项，这和 8 个重构项同样重要。

**深层洞察**：
- 架构评估的常见陷阱是"重构癖"——看到什么都想改
- 明确"什么不改"的价值在于：
  1. 防止范围蔓延（scope creep）
  2. 保护已验证的成熟设计不被破坏
  3. 让团队把精力集中在真正的瓶颈上
- Firecrawl 的 Open Core 模式也是类似思路：核心开源能力（crawl/scrape）稳定不动，商业差异化在托管层做
- 阶段守卫（stage-guardrails）是最典型的例子——它的设计已经非常成熟，如果为了"Agent-First"去重构它，反而会破坏最稳固的基石

**可复用模式**：**不重构清单（No-Touch List）**
> 任何架构评估必须输出：
> - ✅ 重构清单（按优先级排序）
> - ❌ 不重构清单（每个项都必须有理由）
> - ⏸️ 暂缓清单（条件不满足，等时机成熟再说）
