---
id: "longcat-agent-learning-wiki"
title: "LongCat-2.0 Agent能力实测Wiki教程"
category: learning
tags: ["longcat", "agent", "claude-code", "moe", "loop-engineering", "ai-coding", "meituan"]
date: "2026-07-04"
status: draft
summary: "基于郭震AI实测经验，系统学习美团LongCat-2.0（1.6T参数MoE模型）接入Claude Code的完整流程，涵盖架构解析、配置指南、BI数据看板项目实战、Token效率对比和Loop Engineering方法论。"
source: "https://mp.weixin.qq.com/s/ymt9W64FD5IwCDNeQFuheA"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/longcat-agent-learning-wiki.toml"
---
# LongCat-2.0 Agent能力实测Wiki教程

> 基于郭震AI实测经验，系统学习美团LongCat-2.0大模型接入Claude Code的完整流程。

## 文档导航

| 章节 | 文件 | 内容概要 |
|------|------|---------|
| 概述与学习目标 | [00-overview.md](longcat-agent-learning-wiki/00-overview.md) | 背景介绍、核心主题、学习目标、前置知识、文档导航 |
| LongCat-2.0核心概念 | [01-core-concepts.md](longcat-agent-learning-wiki/01-core-concepts.md) | MoE架构、稀疏注意力、1.6T参数、国产算力训练、Agent原生设计 |
| Claude Code接入指南 | [02-claude-code-integration.md](longcat-agent-learning-wiki/02-claude-code-integration.md) | API Key获取、环境变量配置（含完整JSON）、模型切换步骤 |
| BI数据看板实战 | [03-bi-dashboard-demo.md](longcat-agent-learning-wiki/03-bi-dashboard-demo.md) | 项目需求、开发流程、任务拆解、报错修复、最终成果 |
| Token效率对比 | [04-token-efficiency.md](longcat-agent-learning-wiki/04-token-efficiency.md) | LongCat-2.0 vs Codex+GPT-5.5消耗对比、缓存机制 |
| Loop Engineering方法论 | [05-loop-engineering.md](longcat-agent-learning-wiki/05-loop-engineering.md) | 概念解析、迭代修复流程、与传统编程的对比 |
| 总结与回顾 | [06-summary.md](longcat-agent-learning-wiki/06-summary.md) | 核心要点回顾、关键takeaway、下一步学习建议 |
| 常见问题（FAQ） | [07-faq.md](longcat-agent-learning-wiki/07-faq.md) | 8个常见问题及详细解答 |
| 资源与参考链接 | [08-resources.md](longcat-agent-learning-wiki/08-resources.md) | 原文、LongCat平台、API文档、相关工具链接 |

## 学习路径建议

1. **新手入门**：按顺序阅读 00 → 01 → 02，了解模型基本概念和配置方法
2. **实战进阶**：阅读 03 → 04 → 05，深入理解项目实战过程和方法论
3. **快速查阅**：按需跳转到对应章节，所有章节可独立阅读