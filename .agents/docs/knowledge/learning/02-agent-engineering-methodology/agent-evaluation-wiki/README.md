---
id: "agent-evaluation-methodology-wiki-index"
title: "Agent评测体系化建设方法论"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/02-agent-engineering-methodology/agent-evaluation-wiki/README.toml"
category: "learning"
date: "2026-08-05"
tags: ["agent-evaluation", "evaluation-methodology", "benchmark", "metrics", "ci-cd", "llm-as-judge"]
source: "spec:agent-evaluation-methodology-wiki"
summary: "AI Agent评测体系化建设方法论系统性教程，从理论基础到工程实践，覆盖评测维度、指标体系、基准测试、自动化框架、人工评估、数据治理、行业案例、工具选型、持续评测全流程。"
---
# Agent评测体系化建设方法论

> 本目录包含AI Agent评测体系化建设的完整方法论教程，共11篇原子化文档，从评测理论到工程实践形成完整闭环。

## 📄 文档索引

| 文档 | 标题 | 内容概要 | 标签 |
|------|------|---------|------|
| [教程总览](00-overview.md) | AI Agent 评测体系化建设方法论教程总览 | 评测体系四层结构（战略层→方法论层→执行层→基础设施层）、11章导航、目标读者、三档阅读路径、项目内关联指引 | `overview` `evaluation` `tutorial` |
| [评测理论基础](01-theory-foundations.md) | Agent评测的定义、范式演进与理论框架 | 标准定义、Agent评测vs传统LLM评测五维区别、2022-2026发展时间线、五维平衡/CLEAR两套能力框架、结果→过程→轨迹三阶段演进、信效度理论、伦理原则、5大核心挑战 | `theory` `foundation` `paradigm` `reliability` `validity` |
| [指标体系设计](02-metrics-design.md) | 评测指标分类、计算方法与选择指南 | 14大类指标概览、pass@k/pass^k一致性指标、RAG四指标（Context Precision/Recall/Faithfulness/Answer Relevance）、Agent专用指标、效率/成本/安全指标、AWS三层评估框架、指标选择决策 | `metrics` `pass@k` `rag-metrics` `aws-framework` |
| [基准测试构建](03-benchmark-construction.md) | 主流基准详解与自定义评测集构建 | 六大类20+主流基准（SWE-bench Verified/GAIA/WebArena/AgentBench/τ-bench/GuardianAgentBench等）、基准污染问题与Verified版重要性、自定义任务集设计、对抗样本构造、基准维护策略、选型指南 | `benchmark` `swe-bench` `gaia` `webarena` `agentbench` `contamination` |
| [自动化评测框架](04-automated-evaluation.md) | LLM-as-Judge与自动化评测技术 | LLM-as-Judge范式（优势/局限/校准）、规则评测（精确匹配/正则/程序验证）、执行轨迹分析、6大主流框架深度对比（LangSmith/Braintrust/DeepEval/Phoenix/OpenAI Evals等）、补充工具、评分聚合、选型决策树 | `automated-evaluation` `llm-as-judge` `frameworks` `langsmith` `deepeval` |
| [人工评估方法论](05-human-evaluation.md) | 人工评估体系设计与质量控制 | 人工评估不可替代性、评估维度设计、标注规范制定、评估员培训流程、Cohen's Kappa/Fleiss' Kappa一致性检验、双盲/抽查/分歧仲裁质量控制、人机协作评估策略 | `human-evaluation` `annotation` `inter-rater-reliability` `cohens-kappa` `quality-control` |
| [评测数据治理](06-data-governance.md) | 评测数据全生命周期管理 | 数据生命周期（采集→标注→版本→使用→迭代）、采集采样策略、标注质量管理（Gold Set构建）、DVC数据版本管理、数据卡、PII隐私脱敏、数据质量审计（去重/去污染/偏差检测）、数据集迭代策略 | `data-governance` `data-versioning` `privacy` `gold-set` `data-quality` |
| [行业实践案例](07-industry-practices.md) | 五类Agent场景的评测实践与反模式 | Coding Agent/RAG Agent/多工具Agent/多Agent协作/AWS Motorway CI/CD五大案例详解、7个常见错误警示（反模式）、行业经验总结 | `industry-practices` `case-studies` `coding-agent` `rag-agent` `anti-patterns` |
| [评测工具链选型](08-toolchain-selection.md) | 开源vs商用vs自研决策与集成方案 | 开源/商用/自研决策框架、开源工具详细对比、商用平台评估维度、自研框架架构设计要点、分阶段技术栈推荐（入门/成长/成熟）、与CI/CD/实验跟踪/模型监控的集成方案 | `tool-selection` `open-source` `commercial-tools` `build-vs-buy` `integration` |
| [持续评测体系](09-continuous-evaluation.md) | CI/CD集成与评测驱动开发 | Agent-Native CI/CD理念、五门质量门禁（Lint→离线评测→成本检查→影子评测→灰度发布）、五门流水线流程图、回归检测告警、A/B测试统计显著性、趋势可视化、评测驱动开发（EDD）、落地路线图甘特图、中小团队MVE方案、成熟度自评矩阵 | `continuous-evaluation` `ci-cd` `shadow-deployment` `canary-release` `edd` `mve` |
| [术语表与参考资源](10-resources.md) | 核心术语、权威来源与扩展阅读 | 29条核心术语通俗解释、38个权威参考（14篇学术论文+11篇行业分析+13个官方开源项目）、三级难度阅读建议（入门/进阶/研究级）、项目内相关wiki交叉引用 | `glossary` `references` `academic-papers` `further-reading` |

---

## 🎯 教程核心价值

本教程系统回答了以下关键问题：

| 问题 | 解答章节 |
|------|---------|
| 为什么传统LLM评测不够，Agent评测需要什么？ | [01-theory-foundations.md](01-theory-foundations.md) |
| 应该评测哪些维度？如何设计指标体系？ | [02-metrics-design.md](02-metrics-design.md) |
| 有哪些现成基准？如何构建自定义测试集？ | [03-benchmark-construction.md](03-benchmark-construction.md) |
| 如何搭建自动化评测？LLM-as-Judge怎么用？ | [04-automated-evaluation.md](04-automated-evaluation.md) |
| 哪些维度必须人工评？如何保证评估质量？ | [05-human-evaluation.md](05-human-evaluation.md) |
| 如何管理评测数据？如何应对基准污染？ | [06-data-governance.md](06-data-governance.md) |
| 行业领先团队是怎么做的？有哪些坑要避开？ | [07-industry-practices.md](07-industry-practices.md) |
| 选什么工具？LangSmith/DeepEval/Braintrust怎么选？ | [08-toolchain-selection.md](08-toolchain-selection.md) |
| 如何把评测融入CI/CD？怎么从小做起？ | [09-continuous-evaluation.md](09-continuous-evaluation.md) |

---

## 🔗 相关资源

- [🏠 返回上级：Agent工程方法论](../README.md)
- [📚 知识库首页](../../../../README.md)
- [🛡️ 对抗性审查方法论](../adversarial-review-wiki/00-overview.md) — 红队测试与对抗性评测思想
- [🏗️ Harness七大组件](../harness-seven-components-wiki/00-overview.md) — 可观测性组件与评测体系的关联
- [⚙️ Karpathy LLM编程准则](../karpathy-llm-coding-guidelines/00-overview.md) — "先写测试"思想与评测驱动开发
