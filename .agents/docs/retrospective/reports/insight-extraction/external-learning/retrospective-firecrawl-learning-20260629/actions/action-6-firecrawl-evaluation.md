---
id: "firecrawl-action-6-firecrawl-evaluation"
title: "行动6：Firecrawl 能力引入评估"
source: "../export-suggestions.md"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-firecrawl-learning-20260629/actions/action-6-firecrawl-evaluation.toml"
---
# 行动6：Firecrawl 能力引入评估

**优先级**：🟢 低
**预计工作量**：不适用（评估项，待需要时执行）
**状态**：暂缓（当前无批量网页抓取需求）

## 目标

评估是否需要在 SpecWeave 项目中集成 Firecrawl 作为网页数据获取能力。

## 评估维度

| 维度 | 判断标准 |
|------|---------|
| 需求频率 | 未来是否有大量网页抓取/内容提取需求？ |
| 成本 | Free 层 1k credits 是否够用？自托管运维成本如何？ |
| 替代方案 | Playwright 直接使用 vs Firecrawl 封装，哪个更适合？ |
| 集成复杂度 | SDK 引入是否简单？与现有工具链是否冲突？ |

## 当前建议

当前阶段暂不引入，待有明确的网页数据批量获取需求时再评估。届时可直接使用 Keyless 模式快速 PoC。
