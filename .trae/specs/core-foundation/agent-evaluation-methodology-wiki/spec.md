---
title: "Agent评测体系化建设方法论 Wiki 教程"
source: "deep-research:agent-evaluation-industry-best-practices"
x-toml-ref: "../../../../.meta/toml/.trae/specs/core-foundation/agent-evaluation-methodology-wiki/spec.toml"
date: "2026-08-05"
tags: ["agent-evaluation", "llm-eval", "llm-as-judge", "benchmark", "ci-cd", "rag-eval", "agent-native", "metrics", "continuous-evaluation", "knowledge-base"]
---

# Agent评测体系化建设方法论 Wiki 教程 - 产品需求文档

## Why

随着AI Agent从Demo走向生产环境，"如何科学、系统、自动化地评测Agent"成为制约Agent工程化落地的核心瓶颈。现有知识库中缺乏从理论框架到落地实践的完整评测方法论教程——学术界有论文但工程性不足，工业界有实践但体系化不够。本任务通过深度研究（deep-research）调研学术界与产业界最新进展（2022-2026），构建一套完整、可落地的Agent评测知识体系Wiki教程，填补项目知识库在Agent工程化评测领域的空白。

## 场景链路（seven-concepts-cmd）

* **场景4：知识沉淀（R→I→E）**：复盘深度调研采集的22+权威事实来源 → 洞察评测体系化建设本质规律 → 萃取可复用方法论与模式并以Wiki教程输出
* **场景5：创新突破（F→V）**：对抗审查验证方法论完整性（C/A平衡、信效度、鲁棒性）→ 验证验收标准可落地性

* 概念链路：F（事实采集：22+论文/报告/开源项目）→ V（完整性验证）→ R（复盘结构化整理）→ I（洞察五层架构规律）→ E（萃取为原子化Wiki教程+可复用模式）→ V（质量验证60+检查项）→ C（闭环：更新知识库索引）

## What Changes

* 新增目录式Wiki：`d:\AI\.agents\docs\knowledge\learning\02-agent-engineering-methodology\agent-evaluation-wiki\`（多文件原子化结构，含README.md与00-10章节文件）

* 更新 `02-agent-engineering-methodology/README.md` 子Wiki索引，新增agent-evaluation-wiki目录条目

* 覆盖评测理论基础、指标体系、基准测试、自动化框架、人工评估、数据治理、行业案例、工具选型、持续评测等完整内容

## Goals

* 构建Agent评测理论体系：从定义、与LLM评测的区别、发展脉络、多套能力维度框架（学术界五维/产业界CLEAR/六维轨迹/IETF安全/AWS三层）、信效度理论

* 详解指标体系设计：14大类指标分类、pass@k/pass^k一致性指标、RAG专用四指标、Agent专用轨迹指标、效率/成本/安全指标、指标选择方法论

* 详解基准测试构建：六大类20+主流基准（SWE-bench Verified/GAIA/WebArena/AgentBench/τ-bench/GuardianAgentBench等）、基准污染问题、自定义Gold Set构建、对抗样本

* 详解自动化评测范式：LLM-as-Judge方法论、规则评测、执行轨迹分析三种范式对比、6大主流框架深度对比（LangSmith/Braintrust/DeepEval/Phoenix/Future AGI/OpenAI Evals）、选型决策树

* 详解人工评估体系：评估维度设计、标注规范、评估员培训、Cohen's Kappa/Fleiss' Kappa一致性检验、质量控制机制

* 详解评测数据治理：数据生命周期、采样策略、标注质量管理、版本控制（DVC）、隐私脱敏、数据质量审计

* 提供行业实践案例：Coding Agent、RAG Agent、多工具Agent、多Agent协作、AWS Motorway CI/CD五大场景案例，总结7个常见反模式警示

* 详解评测工具链选型：开源vs商用vs自研决策框架、分阶段技术栈推荐、CI/CD集成方案

* 构建持续评测体系：Agent-Native CI/CD理念、五门质量门禁（Lint→离线评测→成本检查→影子评测→灰度发布）、回归检测、A/B测试、评测驱动开发（EDD）、中小团队MVE方案、成熟度矩阵

* 提供术语表与参考资源：29条核心术语解释、38个权威参考来源（14篇学术论文+11篇行业分析+13个官方开源项目）、三级阅读路径

* 萃取可复用实现模式（L1候选）

## Non-Goals (Out of Scope)

* 不提供具体评测框架的完整API文档（给出官方文档链接）

* 不进行单个Agent产品的评测（聚焦方法论）

* 不深入统计学理论细节（只讲评测必需的统计方法如Kappa系数）

* 不涉及模型训练或微调方法（聚焦评测而非模型优化）

* 不重复项目中已有的harness-engineering-wiki或adversarial-review-wiki内容（交叉引用而非重复）

## Background & Context

* Agent评测正经历三代范式演进：结果优先（2022前）→ 过程优先（2023）→ 轨迹优先（2024-2025）→ Agent-Native CI/CD（2026）

* 学术界与产业界已形成共识：单一指标不够，需要多维度平衡评测框架；自动化评测+人工评估结合；离线基准+在线A/B测试结合

* 关键事实来源（R阶段已采集）：
  * 学术论文：SWE-bench Verified、GAIA、WebArena、AgentBench、τ-bench、AgentBoard、FlexRAG等14篇
  * 行业分析：AWS Bedrock Agent Evaluation、LangSmith评测指南、Braintrust最佳实践、Weights & Biases、Arize Phoenix、Future AGI State of Agent Eval 2025等11篇
  * 开源项目：LangSmith、DeepEval、Phoenix、OpenAI Evals、SWE-bench、AgentBench等13个

* 现有知识体系缺口：项目中已有harness-engineering-wiki（测试工程）、adversarial-review-wiki（对抗评审），但缺乏系统性的Agent评测方法论教程

## Constraints

* **Technical**: 文档使用Markdown + YAML frontmatter（MDI v1.0），文件名kebab-case纯英文数字前缀，目录放置于 `.agents/docs/knowledge/learning/02-agent-engineering-methodology/agent-evaluation-wiki/`；单文件<400行；所有内部链接使用相对路径；Mermaid图表遵循六规则安全编码

* **Business**: 基于权威来源编写，所有技术观点标注来源；量化数据（如SOTA准确率）需有引用；方法论需可落地（中小团队可执行）

* **Dependencies**: 无需额外网络请求，基于已完成的深度调研结果编写；与现有wiki（ffi-wiki、harness-engineering-wiki、adversarial-review-wiki）交叉引用

## Assumptions

* 用户具备基本的AI/LLM/Agent概念基础

* 用户目标是构建生产级Agent评测体系，而非学术研究

* 教程面向工程团队，技术细节深度适中（架构级+关键代码片段级，非完整源码级）

* Mermaid图表可在支持Mermaid的Markdown渲染器中正常显示

## Acceptance Criteria

### AC-1: 目录式Wiki教程创建完成
- **Given**: spec中功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: `agent-evaluation-wiki/`目录包含README.md与00-overview.md到10-resources.md共11个章节文件，覆盖理论基础、指标、基准、自动化、人工评估、数据治理、行业实践、工具选型、持续评测、资源
- **Verification**: `programmatic`

### AC-2: 目录导航与README索引可用
- **Given**: 用户打开agent-evaluation-wiki/README.md
- **When**: 用户查看文档顶部索引
- **Then**: 索引包含所有章节文件链接，点击可跳转对应章节，上级目录02-agent-engineering-methodology/README.md已更新包含本wiki条目
- **Verification**: `programmatic`

### AC-3: 评测理论基础讲解准确完整
- **Given**: 用户阅读第1章理论基础
- **When**: 用户理解Agent评测核心概念
- **Then**: 能说明Agent评测定义、与传统LLM评测的五维区别、发展时间线、学术界五维框架与产业界CLEAR框架、信效度要求、5大核心挑战
- **Verification**: `human-judgment`

### AC-4: 指标体系设计完整实用
- **Given**: 用户阅读第2章指标设计
- **When**: 用户为自己的Agent选择指标
- **Then**: 能理解14大类指标、pass@k/pass^k计算方法、RAG四指标、Agent轨迹指标、AWS三层评估框架，并能根据场景选择合适指标
- **Verification**: `human-judgment`

### AC-5: 基准测试构建方法讲解清晰
- **Given**: 用户阅读第3章基准测试
- **When**: 用户构建或选择基准
- **Then**: 能了解六大类20+主流基准适用场景、基准污染问题防范、自定义Gold Set构建方法、对抗样本构造思路
- **Verification**: `human-judgment`

### AC-6: 自动化评测框架对比全面
- **Given**: 用户阅读第4章自动化评测
- **When**: 用户选型自动化评测工具
- **Then**: 能理解三种评测范式、6大主流框架优劣势、通过Mermaid决策树选择适合自己的框架
- **Verification**: `human-judgment`

### AC-7: 人工评估方法论可落地
- **Given**: 用户阅读第5章人工评估
- **When**: 用户组织人工评估
- **Then**: 能设计评估维度、编写标注规范、计算Kappa一致性系数、建立质量控制机制
- **Verification**: `human-judgment`

### AC-8: 数据治理体系完整
- **Given**: 用户阅读第6章数据治理
- **When**: 用户管理评测数据
- **Then**: 能理解数据生命周期、采样策略、标注质量管理、DVC版本控制、PII隐私脱敏、数据质量审计方法
- **Verification**: `human-judgment`

### AC-9: 行业实践案例真实可借鉴
- **Given**: 用户阅读第7章行业实践
- **When**: 用户参考案例落地
- **Then**: 能从Coding/RAG/多工具/多Agent/AWS Motorway五大案例中获得启发，避开7个常见错误
- **Verification**: `human-judgment`

### AC-10: 工具链选型指导实用
- **Given**: 用户阅读第8章工具选型
- **When**: 用户搭建评测工具链
- **Then**: 能根据团队规模和阶段选择开源/商用/自研方案，完成CI/CD集成
- **Verification**: `human-judgment`

### AC-11: 持续评测体系可落地
- **Given**: 用户阅读第9章持续评测
- **When**: 用户构建Agent-Native CI/CD
- **Then**: 能理解五门质量门禁、MVE最小可行评测方案、评测驱动开发（EDD）、使用成熟度矩阵自评
- **Verification**: `human-judgment`

### AC-12: 术语表与参考资源实用
- **Given**: 用户查阅第10章资源
- **When**: 用户遇到不熟悉的术语或想深入学习
- **Then**: 能找到29条核心术语解释、38个权威参考来源、三级阅读路径建议
- **Verification**: `human-judgment`

### AC-13: Mermaid图表丰富准确
- **Given**: 用户阅读全教程
- **When**: 用户查看图表
- **Then**: 教程包含至少6个Mermaid图表（概念层次图、发展时间线、选型决策树、流程图、甘特图等），语法正确可渲染
- **Verification**: `programmatic`

### AC-14: 双向导航完整
- **Given**: 用户在任意章节阅读
- **When**: 用户需要跳转章节
- **Then**: 00章有开始阅读链接，01-09章有上一章/返回目录/下一章双向导航，10章有上一章/返回目录导航
- **Verification**: `programmatic`

## Impact

- **Affected specs**: 无直接影响的其他spec
- **Affected code**: 仅新增文档文件，不涉及任何代码改动
- **Affected docs**: `.agents/docs/knowledge/learning/02-agent-engineering-methodology/agent-evaluation-wiki/`（新建目录，12个文件）、`.agents/docs/knowledge/learning/02-agent-engineering-methodology/README.md`（更新索引新增条目）
