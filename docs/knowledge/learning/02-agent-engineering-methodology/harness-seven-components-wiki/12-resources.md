---
id: "harness-seven-components-wiki-12"
title: "延伸资源与推荐阅读"
source: "https://mp.weixin.qq.com/s/IOBCNtztxpinWrYW_AtYew?from=industrynews&color_scheme=light#rd"
date: "2026-07-13"
category: "learning"
tags: ["harness", "资源", "推荐阅读", "进阶"]
---

## 一、本文来源

本文核心理论框架和案例来源于微信公众号文章《从Prompt到Harness：AI Agent的七大组件》（作者：曲凯/五年产品经理）。该文从产品经理视角系统性地提出了Harness七大组件框架。

原文链接：https://mp.weixin.qq.com/s/IOBCNtztxpinWrYW_AtYew

## 二、按组件分类的推荐资源

### 模型网关（Model Gateway）
- LiteLLM：统一调用100+LLM的开源库，支持fallback和负载均衡
- Portkey：AI模型网关平台，支持路由、缓存、可观测性
- 关键词：LLM routing、model gateway、multi-model strategy

### 工具注册表（Tool Registry / Function Calling）
- OpenAI Function Calling官方文档
- LangChain Tools文档
- MCP（Model Context Protocol）：模型上下文协议，标准化工具定义

### 知识库引擎（Knowledge Base / RAG）
- LlamaIndex：RAG框架，支持多种数据源和检索策略
- LangChain Retrieval文档
- 关键词：RAG、retrieval-augmented generation、vector database、semantic search
- 核心原则：质量>数量，知识库是判断力缓存而非资料堆

### 记忆系统（Memory System）
- LangChain Memory模块文档
- MemGPT（现Letta）：面向LLM的分层记忆系统研究
- 关键词：LLM memory、context management、long-term memory、conversation memory
- 核心原则：不是记得越多越好，遗忘机制同样重要

### 策略引擎（Policy Engine / Guardrails）
- Guardrails AI：LLM输出验证和护栏框架
- NeMo Guardrails（NVIDIA）：开源LLM护栏工具包
- 关键词：LLM guardrails、content safety、policy enforcement、AI alignment
- 核心原则：安全红线是硬约束不是软提示

### 可观测性（Observability）
- LangSmith（LangChain）：LLM应用追踪和评估平台
- Langfuse：开源LLM可观测性平台
- Phoenix（Arize）：LLM追踪和评估
- 关键词：LLM observability、tracing、evaluation、LLMOps
- 核心原则：没有可观测性就没有运营，Badcase闭环是优化的核心

### 配置管理（Configuration Management）
- 关键词：prompt management、feature flags、A/B testing for LLM、configuration as code
- 核心原则：业务参数配置化，避免每次调整都发版

## 三、进阶主题

### 从单Agent到多Agent
当你掌握了单Agent的Harness设计后，可以探索：
- 多Agent协作（Multi-Agent Collaboration）
- Agent编排（Agent Orchestration）
- Agent间通信协议
- 注意：多Agent不是银弹，单Agent能解决的问题不要硬上多Agent

### Agent评估体系
- 自动化评估（LLM-as-Judge）
- 人工评估流程
- A/B测试框架
- 线上反馈闭环

### Agent安全
- Prompt Injection防护
- 数据泄露防护
- 工具调用权限控制
- 输出内容审核

## 四、SpecWeave相关资源
- [Harness工程化Wiki](../harness-engineering-wiki/00-overview.md)：从工程实现角度深入Harness
- [Agent能力边界讨论](../README.md)：理解Agent能做什么不能做什么

## 五、学习路径建议

### 入门路径（1-2周）
1. 读完本Wiki教程全部章节
2. 用你最熟悉的业务场景，定义一个最小Agent（参考实践指南的阶段一）
3. 跑通一个最小闭环（不需要全部七个组件）
4. 记录第一个Badcase并尝试归因

### 进阶路径（1-2月）
1. 补全七大组件的最小实现
2. 积累20+Badcase，做一次系统性归因分析
3. 开始追踪业务指标（不只是技术指标）
4. 尝试不同模型的路由策略，对比成本和效果

### 精通路径（持续）
1. 建立完整的Badcase闭环运营机制
2. 探索多Agent协作场景
3. 沉淀自己的Agent设计模式和组件复用库
4. 关注Agent评估和安全的前沿实践

---

[🏠 返回总览](00-overview.md) | [⬅️ 常见问题](11-faq.md) | [➡️ 速查手册](13-cheatsheet.md)
