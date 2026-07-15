---
id: "fable5-cost-optimization-wiki-07"
title: "资源与参考链接"
version: "1.0"
source: "https://mp.weixin.qq.com/s/YirJ8-6_TZuFe9cLepFNSg?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/fable5-cost-optimization-wiki/07-resources.toml"
---
# 资源与参考链接

本章分类整理Fable 5成本优化相关的所有资源，包括原文来源、开源项目、官方文档、相关讨论以及Wiki内部交叉引用。

## 一、原文来源

| 资源 | 链接/位置 | 说明 |
|------|----------|------|
| 微信公众号原文 | https://mp.weixin.qq.com/s/YirJ8-6_TZuFe9cLepFNSg?from=industrynews&color_scheme=light#rd | 《天才程序员体验卡+5！》原文 |
| 本文原始存档 | [article-content.md](article-content.md) | 本地Markdown格式存档 |

---

## 二、开源项目地址（按文中出现顺序）

| 项目 | GitHub地址 | Star | 说明 |
|------|-----------|------|------|
| fable-5-train-opus-skills-after-it-retires | https://github.com/tomicz/fable-5-train-opus-skills-after-it-retires | 小火 | 技能蒸馏提示词，趁Fable 5退休前训练Opus技能 |
| oh-my-fable | https://github.com/didrod205/oh-my-fable | 起步阶段 | Fable方法论抽象框架，每步自动存档，支持断点续跑 |
| pxpipe | https://github.com/teamchong/pxpipe | 4.8k | 文字转图片压缩代理，利用图片与文字计费价差，账单直降59%~70% |
| fable-token-saving-skills-orchestrator | https://github.com/100yenadmin/fable-token-saving-skills-orchestrator | 新项目 | 包工头模式调度器，Fable定策略把关，便宜模型做执行 |

---

## 三、官方资源

| 资源 | 链接 | 说明 |
|------|------|------|
| Anthropic官方定价文档 | https://www.anthropic.com/pricing | 请前往官网查询最新价格信息（价格可能调整） |
| Anthropic Prompt Cache文档 | https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching | 缓存机制详细说明，包括TTL、写入溢价、命中刷新等规则 |
| Anthropic Batch API文档 | https://docs.anthropic.com/en/docs/build-with-claude/batch-api | 批量接口使用指南，输入输出全部半价 |

> **提示**：官方文档是最权威的信息来源，使用前建议查阅最新版本确认价格和机制是否有变化。

---

## 四、相关讨论

| 讨论 | 来源 | 说明 |
|------|------|------|
| 技能蒸馏方案来源 | Reddit热帖 | fable-5-train-opus-skills项目的最初出处 |
| Vaibhav Sisinty的Twitter/X帖子 | X (Twitter) | 将Reddit方案搬到推特后出圈，近30万浏览 |
| Simon Willison关于额度的帖子 | X (Twitter) | 知名开发者晒出100%拉满的额度条，大呼后悔（为了榨干最后额度结果延期了） |
| Anthropic工程师Thariq的表态 | X (Twitter) | 表示一旦容量允许会努力让Fable 5回到订阅套餐 |

---

## 五、相关Wiki交叉引用

以下是SpecWeave知识库中与本主题相关的Wiki，建议延伸阅读：

| 主题 | 链接 | 相关性说明 |
|------|------|-----------|
| 上下文压缩（Headroom） | [headroom-context-compression-wiki](../../02-agent-engineering-methodology/headroom-context-compression-wiki/README.md) | 算法维度的上下文压缩，与pxpipe的模态压缩形成互补 |
| Agent技能系统 | [agent-skills-wiki](../../02-agent-engineering-methodology/agent-skills-wiki/README.md) | SpecWeave技能系统设计理念，与技能蒸馏方案理念同构 |
| Harness工程方法论 | [harness-engineering-wiki](../../02-agent-engineering-methodology/harness-engineering-wiki/README.md) | "驾驭工程"理念，包工头模式是harness的典型实践 |
| LongCat Token效率 | [longcat-agent-learning-wiki](../../02-agent-engineering-methodology/longcat-agent-learning-wiki/README.md) | LongCat的Token效率优化与循环工程，与缓存感知编排相关 |
| Agent通信协议 | [agent-communication-protocols](../../01-agent-protocols-interfaces/agent-communication-protocols/README.md) | 多模型协作需要理解Agent间通信机制 |
| Agent接口深度解析 | [agent-interface-deep-dive](../../01-agent-protocols-interfaces/agent-interface-deep-dive/README.md) | 理解API/ABI/Protocol分层，有助于理解Batch API等官方机制 |

---

## 六、本Wiki导航

| 章节 | 内容 |
|------|------|
| [00 - 概述](00-overview.md) | 主题背景、核心问题、五大方法速览、读者收益 |
| [01 - 定价背景](01-pricing-background.md) | 延期公告、按量计费时间节点、定价详情、订阅vs按量心理差异 |
| [02 - 社区开源方案](02-community-solutions.md) | 技能蒸馏、pxpipe文字转图片、包工头调度模式三大社区方案详解 |
| [03 - 官方优化机制](03-official-optimizations.md) | 缓存经济学、批量接口两大官方省钱秘诀、叠加优惠计算 |
| [04 - 选型指南](04-selection-guide.md) | 场景化选型决策树、方案组合建议、常见选型误区 |
| [05 - 核心洞察](05-core-insights.md) | 五大工程洞察：Token价差套利、模型分层协作、知识沉淀传承、缓存感知编排、成本意识范式转移 |
| [06 - FAQ](06-faq.md) | 常见问题解答（基础问题+进阶问题） |

---

## Changelog

<!-- changelog -->
- 2026-07-09 | docs | 初始版本创建，完成资源与参考链接章节编写（原文来源、开源项目、官方资源、相关讨论、交叉引用、Wiki导航）
