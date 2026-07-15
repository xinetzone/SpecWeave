---
id: "firecrawl-insight-3-tiered-credit"
title: "洞察3：多层级 PLG 定价漏斗与 Credit 经济学"
source: "https://www.firecrawl.dev/pricing"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-firecrawl-learning-20260629/insights/insight-3-tiered-credit.toml"
---
# 洞察3：多层级 PLG 定价漏斗与 Credit 经济学

**来源**：定价页六档方案 + Credit 消耗规则表

## 事实

Firecrawl 设计了六个定价层级（Free→Hobby→Standard→Growth→Scale→Enterprise），不同 API 端点消耗不同数量的 Credit。

## 分析

**定价层级设计**体现了精细的 PLG（Product-Led Growth）漏斗思维：

| 层级 | 月费(年付) | Credits | 并发 | 核心作用 |
|------|-----------|---------|------|---------|
| Free | $0 | 1k | 2 | 完全无门槛体验，获客入口 |
| Hobby | $16 | 5k | 5 | 个人开发者/副业项目，首次付费转化 |
| Standard | $83 | 100k | 50 | 小团队主力使用，"推荐"标签锚定 |
| Growth | $333 | 500k | 100 | 高体量场景，优先支持 |
| Scale | $599 | 1M | 150 | 规模化数据管道 |
| Enterprise | 定制 | 定制 | 定制 | 零数据保留、SSO、SLA，高溢价 |

**Credit 经济学**的精髓在于**不同端点差异化定价**：
- 基础操作（Scrape/Crawl/Map）：1 credit/页 — 锚定"1页=1信用"的基本心智
- 搜索（Search）：2 credits/10结果 — 因为搜索背后有搜索引擎成本
- 浏览器交互（Interact）：2 credits/分钟 — 因为长时间占用浏览器资源
- Agent：动态定价 — 因为 Agent 可能多次调用底层端点，成本不确定

这种设计让用户直观理解"什么操作更贵"，自然引导用户优化调用方式。

## 可复用模式萃取

**模式名称**：Tiered Credit Economy（层级化 Credit 经济体系）

**核心原则**：
1. **免费层足够做 demo**：1k credits 可以完成一个完整的小项目，让用户体验到价值
2. **首付费门槛极低**：$16/月是"不用审批"的价位，开发者可自掏腰包
3. **推荐档锚定**：Standard 标注"Recommended"，锚定团队购买决策
4. **端点差异化定价**：资源消耗高的端点收费更高，反映真实成本
5. **并发数随价格增长**：不仅给更多 credits，还给更高并发，满足规模化需求
6. **Enterprise 不标价**：定制价格意味着销售介入，适合高溢价谈判

**成熟度**：L3（在 SaaS 领域成熟，但可迁移到 AI Agent 资源调度领域）

**关联洞察**：
- [洞察2：开源+托管](insight-2-open-core.md) — 定价漏斗是开源引流的变现出口
- [洞察7：双模型策略](insight-7-dual-model.md) — 模型选择也是成本控制的一种方式
