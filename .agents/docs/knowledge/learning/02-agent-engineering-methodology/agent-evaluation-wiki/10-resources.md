---
id: "agent-evaluation-resources"
title: "第10章：术语表与参考资源"
source: "spec:agent-evaluation-methodology-wiki"
category: "learning"
tags: ["agent-evaluation", "glossary", "references", "resources", "further-reading"]
date: "2026-08-05"
status: "draft"
author: "SpecWeave"
summary: "AI Agent评测核心术语表、权威参考来源分类整理、按难度分级的扩展阅读建议、项目内相关wiki交叉引用，为持续深入学习提供索引。"
---

# 第10章：术语表与参考资源

> **方法论视角**：如需从方法论链路视角速查核心术语与 FAQ 解答，可参阅 [方法论Wiki · 术语表](../agent-eval-methodology-wiki/glossary.md)与[常见问题解答](../agent-eval-methodology-wiki/06-faq/06-faq-overview.md)。

---

## 10.1 核心术语表

以下是Agent评测领域的核心术语，按通俗解释整理：

| 术语 | 通俗解释 |
|---|---|
| **Agent（智能体）** | 能感知环境、自主决策、调用工具完成复杂任务的AI系统，不只是问答，还能多步执行实际工作 |
| **LLM-as-Judge** | 用大语言模型当"裁判"来自动评分，代替人工判断输出好坏，是自动化评测的核心方法 |
| **pass@k** | 代码生成评测指标：生成k个答案，只要至少有一个对就算通过，k通常取1、10、100 |
| **轨迹评估（Trajectory Evaluation）** | 不只看最终结果对不对，还看Agent走的每一步（思考、工具调用、中间结果）是否合理 |
| **基准污染（Benchmark Contamination）** | 测试题被偷偷放进了模型训练数据里，导致模型"背答案"考高分，实际能力没那么强 |
| **SWE-bench** | 软件工程领域权威基准，让Agent解决真实GitHub仓库里的issue，是Coding Agent的"高考" |
| **RAG（检索增强生成）** | 先从知识库搜相关资料再回答，减少幻觉，评测时要同时考检索准不准和回答对不对 |
| **CoT（思维链）** | 让模型"把思考过程写出来"再给答案，能提升推理能力，评测时可检查推理逻辑是否正确 |
| **ReAct** | "推理+行动"交替的Agent框架：想一步→做一步→看结果→再想下一步，是最经典的Agent范式 |
| **Tool Use（工具使用）** | Agent调用外部工具（搜索、计算器、API、数据库）的能力，评测重点是会不会选工具、参数对不对 |
| **影子评测（Shadow Evaluation）** | 新版本不直接服务用户，而是复制真实流量在后台跑，和旧版本对比，不影响用户但能发现真实问题 |
| **CI/CD门禁** | 把评测集成到代码提交流水线里，指标不达标直接不让合并代码，从流程上保障质量 |
| **信度（Reliability）** | 评测结果的稳定性/一致性——同一个东西多次测，或者不同人测，结果应该差不多 |
| **效度（Validity）** | 评测真的在测你想测的东西吗？比如"回答长度"不能代表"回答质量"，这就是效度问题 |
| **Cohen's Kappa** | 衡量两个人标注/评分一致性的统计指标，去掉"碰巧一致"的情况，>0.6算不错，>0.8算很好 |
| **Gold Set（黄金集）** | 精心标注、反复验证的高质量测试集，是评测的"锚点"，每次都先跑它确保基础能力没退化 |
| **对抗样本（Adversarial Examples）** | 专门设计的"刁难"问题，能测出模型的弱点和边界，正常人不会这么问但能暴露安全漏洞 |
| **提示注入（Prompt Injection）** | 用户通过特殊输入绕过系统指令，让Agent做不该做的事，是安全评测的核心场景 |
| **MVE评测成熟度** | Minimum Viable Evaluation，最小可行评测体系——不用完美，先搞一个简单能用的版本跑起来 |
| **EDD（评测驱动开发）** | Evaluation-Driven Development，类似TDD但不是写测试，而是先定义怎么算好、怎么测量，再去优化 |
| **回归（Regression）** | 以前能做对的题现在突然做错了——能力退步，是持续评测要抓的核心问题 |
| **A/B测试** | 新旧版本同时跑，一部分用户用新版一部分用旧版，对比真实业务指标，用统计显著性判断差异 |
| **幻觉（Hallucination）** | 模型一本正经地胡说八道，编造不存在的事实、引用不存在的来源，是事实性评测的核心指标 |
| **北极星指标** | 最核心的那个评测指标，代表产品最终价值，比如"用户任务完成率"，其他指标都要服务于它 |
| **温度参数（Temperature）** | 控制模型输出随机性的参数，0是最确定，越高越有创意但也越容易出错，评测时通常固定为0保证可复现 |
| **few-shot（少样本）** | 在Prompt里给几个例子，让模型照着做，评测时要固定例子数量和顺序保证公平对比 |
| **思维树（ToT）** | Tree of Thoughts，不只是一条路走到黑，而是同时探索多条推理路径，选最好的，评测时看路径选择是否合理 |
| **工具调用错误率** | Agent调用工具时出错的比例，包括选了错的工具、参数填错、调用时机不对等，是核心过程指标 |
| **任务完成率** | Agent成功完成用户指定任务的比例，是最直观也是最重要的端到端效果指标 |

---

## 10.2 权威参考来源分类整理

### 10.2.1 学术论文（含arXiv）

| 论文/资源 | 核心价值 | 链接/出处 |
|---|---|---|
| SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | Coding Agent评测奠基性工作，提出真实软件工程基准 | arXiv:2310.06770 |
| AgentBench: Evaluating LLMs as Agents | 首个系统化Agent能力基准，覆盖8个真实环境 | arXiv:2308.03688 |
| LLM-as-Judge: Customized Judges for Customized Evaluation | 系统研究用LLM做裁判的方法论、偏差与校准 | arXiv:2306.05685 |
| Judging LLM-as-Judge with MT-Bench and Chatbot Arena | 提出MT-Bench基准和竞技场盲评方法 | arXiv:2306.05685（LMSYS） |
| Toolformer: Language Models Can Teach Themselves to Use Tools | 工具使用能力的开创性工作 | arXiv:2302.04761 |
| ReAct: Synergizing Reasoning and Acting in Language Models | ReAct范式原始论文，推理+行动交替框架 | arXiv:2210.03629 |
| Chain-of-Thought Prompting Elicits Reasoning in LLMs | CoT思维链原始论文 | NeurIPS 2022 |
| Tree of Thoughts: Deliberate Problem Solving with LLMs | ToT思维树框架，多路径推理 | arXiv:2305.10601 |
| RAGAS: Automated Evaluation of Retrieval Augmented Generation | RAG评测专用框架，从上下文相关性、忠实度等维度评测 | arXiv:2309.15217 |
| A Survey on Evaluation of Large Language Models | LLM评测综述论文，系统梳理评测维度与方法 | arXiv:2307.03109 |
| Benchmarking Large Language Models in Retrieval-Augmented Generation | RAG评测基准与方法研究 | arXiv:2309.01431 |
| Adversarial Prompting for Black Box Foundation Models | 对抗样本与提示注入的系统化研究 | arXiv:2402.12328 |
| Can Large Language Models be Good Judges? A Study on Position Bias | LLM-as-Judge的位置偏差问题研究 | arXiv:2310.00866 |
| WebArena: A Realistic Web Environment for Building Autonomous Agents | 网页Agent真实环境基准 | arXiv:2307.13854 |

### 10.2.2 行业深度分析与报告

| 来源 | 报告/文章 | 核心内容 |
|---|---|---|
| **Future AGI** | Agent工程化系列文章 | 从生产实践角度讲Agent评测、质量保障体系 |
| **InfoQ** | AI Agent工程落地专题 | 国内技术社区对Agent评测的实践总结 |
| **Databricks** | MLOps for LLM Applications Blog | 企业级LLM/Agent评测流水线建设经验 |
| **AWS Machine Learning** | Building Production-Ready LLM Agents | AWS Motorway团队生产Agent五门门禁方法论 |
| **Weights & Biases (W&B)** | LLM Evaluation Series | W&B的LLM评测最佳实践与工具链指南 |
| **OpenAI Cookbook** | Evaluation techniques | OpenAI官方评测技术指南与代码示例 |
| **Anthropic** | Building Effective Agents | Claude团队的Agent构建与评测原则 |
| **Google DeepMind** | Gemini Evaluation Report | Gemini模型评测方法论与能力报告 |
| **Hugging Face** | Evaluate Library Documentation | Hugging Face评测库文档与最佳实践 |
| **Lilian Weng Blog** | LLM Powered Autonomous Agents | 经典的Agent系统综述，包含评测思考 |
| **Chip Huyen Blog** | Evaluating LLM applications | MLOps专家视角的LLM应用评测方法论 |

### 10.2.3 官方文档与GitHub仓库

| 项目 | 类型 | 核心价值 | 地址 |
|---|---|---|---|
| **LangChain Evaluations** | 框架文档 | LangChain官方评测模块，支持轨迹评估、LLM-as-Judge | python.langchain.com/docs/guides/evaluation/ |
| **LlamaIndex Evaluation** | 框架文档 | LlamaIndex RAG与Agent评测模块，响应/相关性/忠实度评估 | docs.llamaindex.ai/en/stable/module_guides/evaluating/ |
| **DeepEval** | 开源框架 | 简单易用的LLM评测框架，支持多种指标、CI集成 | github.com/confident-ai/deepeval |
| **OpenAI Evals** | 开源框架 | OpenAI官方开源评测框架，可自定义评测任务 | github.com/openai/evals |
| **LMSYS/FastChat** | 开源项目 | MT-Bench、Chatbot Arena竞技场盲评平台 | github.com/lm-sys/FastChat |
| **RAGAS** | 开源框架 | RAG评测专用框架，自动化RAG质量评估 | github.com/explodinggradients/ragas |
| **TruLens** | 开源工具 | LLM应用可观测性与评测工具，跟踪幻觉、相关性等 | github.com/truera/trulens |
| **LangSmith** | 商用平台 | LangChain官方LLM/Agent评测与可观测性平台 | smith.langchain.com |
| **Langfuse** | 开源平台 | 开源LLM可观测性与评测平台，支持自托管 | github.com/langfuse/langfuse |
| **promptfoo** | 开源工具 | Prompt测试与评测工具，支持回归测试、A/B对比 | github.com/promptfoo/promptfoo |
| **SWE-bench** | 基准仓库 | 官方SWE-bench基准与评测代码 | github.com/princeton-nlp/SWE-bench |
| **AgentBench** | 基准仓库 | AgentBench官方代码与数据集 | github.com/THUDM/AgentBench |
| **WebArena** | 基准仓库 | 网页Agent基准环境 | github.com/web-arena-x/webarena |

---

## 10.3 扩展阅读建议（按难度分级）

### 10.3.1 入门级（刚接触Agent评测）

适合对象：评测新手，需要快速建立基本概念，跑通第一个评测

**阅读建议（1-2周）**：
1. 先读完本教程全部10章，建立体系化认知
2. DeepEval官方文档Quickstart —— 30分钟跑通第一个LLM评测
3. OpenAI Cookbook: Evaluation techniques —— 了解基础评测方法
4. LangChain Evaluation Quickstart —— 学习如何评测LangChain Agent
5. 文章：*How to evaluate LLM applications*（Chip Huyen）—— 建立评测方法论直觉
6. 动手：用100行Python写一个简单的LLM-as-Judge脚本，评自己的Agent

**目标**：理解为什么要评测、评测什么、怎么简单测，能跑通基础评测

### 10.3.2 进阶级（有基础，要建设生产级评测体系）

适合对象：已经能跑评测，要建设团队的完整评测流水线，落地到生产

**阅读建议（1-2个月）**：
1. 论文：*LLM-as-Judge* 原始论文 —— 理解裁判模型的偏差与校准
2. 论文：*SWE-bench* + *AgentBench* —— 理解学术基准是怎么设计的
3. 论文：*RAGAS* —— 掌握RAG评测的专门方法
4. AWS/Building Production-Ready LLM Agents —— 学习生产环境五门门禁
5. 浏览DeepEval/TruLens/promptfoo源码，理解框架设计
6. Langfuse/LangSmith文档，学习可观测性与评测如何结合
7. 文章系列：Future AGI Agent工程化文章 —— 国内团队的落地经验
8. 动手：按本教程第9章的MVE方案，两周内搭建团队的最小可行评测体系，集成到CI

**目标**：能独立设计生产级评测方案，搭建自动化评测流水线，建立持续评测机制

### 10.3.3 研究级（要做前沿研究或深度优化）

适合对象：评测体系已经成熟，要做方法创新、解决前沿问题

**阅读建议（3-6个月+）**：
1. LLM评测综述论文（*A Survey on Evaluation of Large Language Models*）—— 建立学术全局视野
2. 跟踪arXiv cs.CL和cs.AI的最新评测相关论文（每周刷）
3. 深入研究信度/效度理论、心理测量学基础（评测本质是测量）
4. LLM-as-Judge偏差校准、自动评测集生成、对抗性评测方向的前沿论文
5. 研究多Agent系统、具身智能、长程任务等前沿场景的评测方法
6. 参与LMSYS Chatbot Arena等开源评测项目
7. 动手：针对自己的业务场景，设计新的评测指标或方法，在生产中验证有效

**目标**：能提出新的评测方法，解决评测领域的前沿难题，指导团队评测体系持续进化

---

## 10.4 项目内相关Wiki交叉引用

本教程是Agent工程方法论体系的一部分，建议结合以下wiki交叉阅读：

### 前置与基础方法论

- **[harness-engineering-wiki](../harness-engineering-wiki/00-overview.md)**：Harness工程方法论
  - 评测是Harness体系「可观测性」组件的核心
  - Harness四铁律（可复现、可测量、可验证、可回滚）直接指导评测设计
  - 六模式中的「质量护栏」模式就是评测在工程化中的落地

- **[harness-seven-components-wiki](../harness-seven-components-wiki/00-overview.md)**：Harness七大组件
  - 可观测性（Observability）组件：评测是其中的质量测量部分
  - 配置管理、实验管理组件支撑评测的版本化与对比

### 互补方法论

- **[adversarial-review-wiki](../adversarial-review-wiki/00-overview.md)**：对抗性评审方法论
  - 红队测试思想直接用于对抗性评测用例设计
  - 认知偏差防御帮助识别评测者本身的偏差（如位置偏差、锚定偏差）
  - 对抗性评审流程可直接用于人工评估环节的质量控制

- **[agent-skills-wiki](../agent-skills-wiki/00-overview.md)**：Agent技能体系
  - 评测维度设计需对齐技能分类，覆盖各类技能的掌握程度
  - 技能组合能力是高阶Agent评测的重点
  - 技能迭代效果依赖评测数据验证

### 评测驱动的工程实践

- **[seven-concepts-prompt-wiki](../seven-concepts-prompt-wiki/00-overview.md)**：七概念方法论
  - 「复盘（R）-洞察（I）-萃取（E）」闭环需要评测数据作为输入
  - 「验证（V）」环节就是小型评测循环
  - 七概念的迭代节奏与持续评测周期相匹配

- **[karpathy-llm-coding-guidelines](../karpathy-llm-coding-guidelines/00-overview.md)**：Karpathy LLM编码指南
  - 「先写测试」思想与EDD评测驱动开发高度契合
  - 编码规范中强调的可复现性、确定性直接对应评测的信度要求
  - Coding Agent的评测方法可参考该wiki中的实践

---

## 章节导航

| 上一章 | 当前章节 | 下一章 |
|---|---|---|
| [← 第9章：持续评测体系](09-continuous-evaluation.md) | 第10章：术语表与参考资源 | *（教程结束）* |
| | [📚 返回教程目录](00-overview.md) | |

---

> **本章小结**：本章整理了Agent评测领域的核心术语表（29个核心概念）、分类整理了22+权威参考来源（学术论文、行业报告、开源项目）、提供了入门/进阶/研究三级扩展阅读路径，并给出了项目内相关wiki的交叉引用索引。评测方法论是一门快速发展的交叉学科，需要持续学习和实践——从MVE最小可行评测开始，在实践中不断迭代深化，比追求完美方案更重要。

> **教程结语**：恭喜你完成了《AI Agent评测体系化建设方法论教程》的全部学习！评测不是一次性项目，而是持续迭代的旅程。从两周MVE开始，逐步建设五门门禁，用数据驱动优化，你的Agent系统会在评测的护航下越来越可靠。
