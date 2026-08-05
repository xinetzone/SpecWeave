---
id: "agent-eval-methodology-index"
title: "Agent评测方法论系统化资料档案"
category: "learning"
date: "2026-08-05"
version: "0.1"
status: "draft"
---

# Agent评测方法论系统化资料档案

> **L2级方法论模式知识库**。本知识库系统梳理Agent评测方法论，覆盖方法论概述→核心框架对比→关键指标体系→八阶段实施步骤→8个行业案例→常见问题解答的完整体系。

> **⚠️ 定位说明**：本目录是**方法论驱动**的创作档案——基于 R-F-I-E-V 七概念链路构建，核心价值在附录（R阶段事实清单/公理洞察/创作过程记录/V阶段对抗审查）与知乎文章输出。
> 如需**工程化落地**的完整评测方案（指标计算方法、基准构建、工具选型、CI/CD 集成），请以 [📘 工程手册 · Agent评测体系化建设方法论](../agent-evaluation-wiki/00-overview.md) 为准；本目录教程模块（1-6）为方法论视角的补充总览，与工程手册互为参阅。

<!-- README_INDEX_START -->
## 📄 文档索引

| 文档 | 说明 | 标签 |
|------|------|------|
| [README.md](README.md) | 本索引文件，文档导航入口 | 索引 |
| [glossary.md](glossary.md) | 核心术语表，Agent评测相关术语定义 | 参考 |
| [01-overview/01-methodology-overview.md](01-overview/01-methodology-overview.md) | 方法论概述：定义、价值、成熟度模型0-5级、4个误区 | 入门 |
| [02-frameworks/02-core-frameworks.md](02-frameworks/02-core-frameworks.md) | 核心框架对比：HELM/MT-Bench/AgentBench等6大框架对比与选型 | 进阶 |
| [03-metrics/03-metrics-overview.md](03-metrics/03-metrics-overview.md) | 关键指标体系总览：四维结构、北极星与分层原则 | 进阶 |
| [03-metrics/03-metrics-capability.md](03-metrics/03-metrics-capability.md) | 能力维度指标：任务完成率、工具调用、规划等11项 | 进阶 |
| [03-metrics/03-metrics-efficiency.md](03-metrics/03-metrics-efficiency.md) | 效率维度指标：延迟、成本、Token消耗、吞吐等12项 | 进阶 |
| [03-metrics/03-metrics-security.md](03-metrics/03-metrics-security.md) | 安全维度指标：IETF四层安全框架关键20项 | 进阶 |
| [03-metrics/03-metrics-human-commercial.md](03-metrics/03-metrics-human-commercial.md) | 人本与商业维度指标：CSAT/NPS/ROI等9项 | 进阶 |
| [04-implementation/04-implementation-overview.md](04-implementation/04-implementation-overview.md) | 八阶段实施步骤：每阶段输入/输出/工具/验收/坑点，0-8周落地清单 | 进阶-实践 |
| [05-cases/05-cases-overview.md](05-cases/05-cases-overview.md) | 8个行业案例：OpenAI/LangChain/Nubank/AWS等实践 | 实践 |
| [06-faq/06-faq-overview.md](06-faq/06-faq-overview.md) | 常见问题解答：22条FAQ，覆盖选型/实施/踩坑三类 | 参考 |
| [appendices/fact-list.md](appendices/fact-list.md) | R阶段事实清单：63条客观事实（F-001~F-063） | 附录 |
| [appendices/first-principles-and-insights.md](appendices/first-principles-and-insights.md) | F/I阶段分析：6条公理、假设剥离、3条核心洞察 | 附录 |
| [appendices/creation-process-record.md](appendices/creation-process-record.md) | 创作过程记录：资料收集/框架搭建/内容撰写/审核修订全流程 | 附录 |
| [appendices/adversarial-review.md](appendices/adversarial-review.md) | V阶段对抗审查（Wiki）：四视角17条意见与5条修订对比 | 附录 |
| [appendices/adversarial-review-zhihu-article.md](appendices/adversarial-review-zhihu-article.md) | V阶段对抗审查（知乎文章）：四视角13条意见与5条修订对比 | 附录 |
| [appendices/seven-concepts-cmd-practical-guide.md](appendices/seven-concepts-cmd-practical-guide.md) | seven-concepts-cmd 实操避坑指南：五大高频坑与质量门实战检查 | 附录 |
| [zhihu-article-agent-eval-methodology.md](zhihu-article-agent-eval-methodology.md) | 知乎文章：Agent评测体系化建设方法论 + 创作经验分享 | 输出 |
| [zhihu-article-seven-concepts-wiki-creation.md](zhihu-article-seven-concepts-wiki-creation.md) | 知乎文章：复盘用seven-concepts-cmd方法论编排产出Wiki教程的过程 | 输出 |
| [zhihu-article-seven-concepts-wiki-creation-publish.md](zhihu-article-seven-concepts-wiki-creation-publish.md) | 知乎发布版：去除内部链接与元信息，可直接粘贴到知乎编辑器 | 输出 |

<!-- README_INDEX_END -->

## 🔗 相关资源

- [📘 工程手册 · Agent评测体系化建设方法论](../agent-evaluation-wiki/00-overview.md) — 完整工程化评测方案（指标计算/基准构建/工具选型/CI-CD 集成）
- [🏠 返回上级：Agent工程方法论](../README.md)
- [📚 知识库首页](../../../README.md)

---

*本档案版本：v0.1 | 创建日期：2026-08-05 | 状态：草稿*
