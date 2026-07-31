---
id: "volcengine-agentkit-wiki-readme"
title: "火山引擎 AgentKit Wiki 教程"
source: "seven-concepts: volcengine-agentkit-wiki"
category: "learning"
tags: ["AgentKit", "VeADK", "火山引擎", "AI Agent", "wiki教程"]
date: "2026-07-31"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "火山引擎 AgentKit 企业级 AI Agent 基础设施平台从入门到精通的结构化 wiki 教程，覆盖产品全貌、架构、开发框架、工具链、场景集成与选型评估。"
last_verified: "2026-07-31"
wiki_version: "1.0"
agentkit_version_target: "2026Q3"

---

# 火山引擎 AgentKit Wiki 教程

企业级 AI Agent 基础设施平台从入门到精通的结构化教程。

## 适用人群

| 序号 | 人群 | 核心诉求 |
|------|------|---------|
| 1 | AI 应用开发者 | 快速构建和部署企业级智能体，掌握 VeADK SDK 与 CLI 工具链 |
| 2 | 架构师与技术决策者 | 评估 AgentKit 与现有技术栈的融合方案，完成平台选型决策 |
| 3 | 平台工程师 | 负责智能体平台化建设与治理，落地 Identity/Gateway/Observability 体系 |
| 4 | 产品经理 | 理解 AI Agent 工程化能力边界，规划企业智能体产品路线 |

## 11 章快速导航

| 章号 | 文件名 | 标题 | 一句话简介 |
|------|--------|------|-----------|
| 00 | [00-overview.md](./00-overview.md) | 教程总览与知识地图 | AgentKit 四层生态全景图、11章导航、三条阅读路径与知识库交叉引用 |
| 01 | [01-product-intro.md](./01-product-intro.md) | 产品介绍与核心概念 | 产品定义、工程化四大痛点、八大功能模块、四大产品优势 |
| 02 | [02-core-architecture.md](./02-core-architecture.md) | 产品架构与核心能力 | Agent Ready 分层架构、Harness 编排、Serverless 底座、安全与评测闭环 |
| 03 | [03-veadk-framework.md](./03-veadk-framework.md) | VeADK 智能体开发框架 | 三语言 SDK 安装、VeADK Family 产品矩阵、DeepResearch 构建特性 |
| 04 | [04-agentkit-sdk-cli.md](./04-agentkit-sdk-cli.md) | AgentKit SDK & CLI 工具链 | 装饰器 API、CLI 全命令、Local/Hybrid/Cloud 三种部署模式 |
| 05 | [05-quickstart.md](./05-quickstart.md) | 快速入门指南 | 前置条件、五步标准上手指南、每步命令示例与常见错误排查 |
| 06 | [06-application-scenarios.md](./06-application-scenarios.md) | 应用场景与落地方案 | 四大典型场景架构、五大行业落地框架、标准化 vs 定制化选型决策 |
| 07 | [07-core-features-detailed.md](./07-core-features-detailed.md) | 核心功能深度解析 | Identity/Gateway/A2A/Session-Memory/Knowledge 五大模块深度集成 |
| 08 | [08-comparison-ecosystem.md](./08-comparison-ecosystem.md) | 竞品对比与生态定位 | 十维度五平台对比、八维度选型评估框架、火山引擎 AI 矩阵定位 |
| 09 | [09-faq-best-practices.md](./09-faq-best-practices.md) | FAQ 与最佳实践 | 十五常见问题、八条最佳实践、Demo 到生产十二项检查清单 |
| 10 | [10-resources-glossary.md](./10-resources-glossary.md) | 术语表与参考资源 | 二十条术语表、官方文档链接汇总、知识库交叉引用扩展 |

## 内容快照声明

> 本教程基于 2026 年 7 月火山引擎官方公开资料（产品主页、开发者文档、VeADK GitHub 开源仓库、SDK 参考文档等）整理而成，为结构化知识快照性质。产品功能与 API 会持续演进，后续请以火山引擎官方文档最新版本为准。

## R-I-E-V 方法论执行记录

本教程通过七概念方法论（R-I-E-C-A-F-V）全流程质量门：R 阶段完成 60 条客观事实采集（6 大类覆盖产品定位/功能模块/VeADK 栈/SDK CLI/应用场景/产品生态），G1 质量门通过；I 阶段提炼 5 条核心洞察（战略层 1 + 架构层 2 + 实践层 2），反常识发现均挑战常见认知，G2 质量门通过；E 阶段萃取 3 个跨平台可复用模式（选型框架/改造 SOP/Demo→生产清单），每模式含触发场景+核心步骤+反模式+迁移验证四要素，G3 质量门通过；V 阶段完成 16 条对抗性攻击评审，采纳 6 条优化建议，V 门验证通过。
