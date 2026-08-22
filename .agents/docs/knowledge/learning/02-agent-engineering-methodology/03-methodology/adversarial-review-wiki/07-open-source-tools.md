---
id: "adversarial-review-tools"
title: "07、开源工具链指南"
category: "knowledge"
date: "2026-07-10"
version: "1.0"
status: "completed"
---

## 1. 概述

LLM/AI系统红队测试工具正在快速发展，覆盖从快速扫描到深度编排的不同需求。本文档汇总当前主流开源红队测试工具，为工具选型和使用提供参考。

核心工具包括：Garak、PyRIT、Promptfoo（2026年被OpenAI收购）、Inspect AI、DeepTeam、Purple Llama。

可信度标记说明：
- 🟢A级：官方组织/头部科技公司维护的开源项目
- 🔵B级：社区/创业公司维护的开源项目
- 🟡C级：个人项目、实验性工具

---

## 2. 核心工具详解

### 2.1 Garak 🟢A级（NVIDIA官方开源）

- **开发方**：NVIDIA
- **定位**：LLM漏洞扫描器（类似Nessus for LLMs）
- **核心能力**：基于探针的自动化扫描，覆盖OWASP LLM Top 10，单命令基线扫描，低学习曲线，可自定义探针
- **优点**：上手快（分钟级）、覆盖已知攻击模式、适合CI回归测试
- **缺点**：多轮攻击能力有限、深度定制需要Python
- **适用场景**：快速基线扫描、CI/CD回归测试、已知攻击模式覆盖
- **GitHub**：https://github.com/leondz/garak
- **快速上手**：`pip install garak && python -m garak --model_type huggingface --model_name gpt2`

Garak由NVIDIA安全团队开发，是目前最成熟的LLM漏洞扫描器之一。它采用"探针（probe）"架构，内置数百个探针覆盖OWASP LLM Top 10等已知风险类别。Garak的设计理念是"零配置起步"，安装后单命令即可启动基线扫描，非常适合作为CI/CD流水线中的安全门禁。

### 2.2 PyRIT 🟢A级（Microsoft官方开源）

- **开发方**：Microsoft
- **定位**：红队攻击编排框架（Python框架）
- **核心能力**：多轮攻击编排（Crescendo/Tree of Attacks With Pruning等），转换器+编排器架构，AI vs AI攻击（用一个LLM攻击另一个），高灵活性
- **优点**：多轮攻击能力强、高度可定制、支持复杂攻击研究、Azure AI Foundry内置集成
- **缺点**：学习曲线陡峭（需要Python开发）、小时级上手时间
- **适用场景**：深度定制评估、复杂多轮攻击研究、红队专家使用、企业级安全团队
- **GitHub**：https://github.com/Azure/PyRIT

PyRIT（Python Risk Identification Tool for generative AI）是微软Azure AI安全团队开发的红队攻击编排框架。它采用转换器（Converter）+编排器（Orchestrator）的模块化架构，支持实现复杂的多轮攻击算法，如Crescendo攻击、Tree of Attacks With Pruning（TAP）、PAIR（Prompt Automatic Iterative Refinement）等。PyRIT还支持"AI vs AI"模式——使用一个LLM作为攻击者自动生成针对目标LLM的攻击payload。适合有Python开发能力的专业安全团队进行深度红队研究。

### 2.3 Promptfoo 🟢A级（Promptfoo，2026年被OpenAI收购）

- **开发方**：Promptfoo（2026年被OpenAI收购）
- **定位**：开发者友好的红队测试平台
- **核心能力**：自动生成应用特定攻击、YAML声明式配置、Web UI可视化报告、CI/CD内置集成、50+漏洞类型覆盖、OWASP/NIST/MITRE合规映射、支持多种LLM提供商
- **优点**：上手最快（分钟级）、CI/CD集成开箱即用、Web UI友好、开发者体验好、工程团队首选
- **缺点**：深度多轮攻击编排不如PyRIT灵活
- **适用场景**：工程团队持续测试、DevSecOps集成、快速上手、团队协作
- **GitHub**：https://github.com/promptfoo/promptfoo
- **快速上手**：`npx promptfoo@latest init`

Promptfoo是目前开发者体验最好的LLM红队测试工具，2026年被OpenAI收购进一步验证了其技术价值。它采用YAML声明式配置，无需编写代码即可定义测试用例，内置50+漏洞类型检测，自动生成应用特定的攻击payload，并提供美观的Web UI可视化报告。Promptfoo对CI/CD集成支持开箱即用，是工程团队将红队测试融入日常开发流程的首选工具。

### 2.4 Inspect AI 🔵B级

- **开发方**：UK AI Safety Institute (AISI)
- **定位**：AI安全评估框架
- **核心能力**：任务+求解器架构、灵活评分机制、英国AISI官方使用工具、适合标准化安全评估
- **优点**：评估设计灵活、评分机制可定制、政府级安全评估框架
- **缺点**：社区生态较小、中文资源少
- **适用场景**：安全研究、标准化评估、合规审计
- **GitHub**：https://github.com/UKGovernmentBEIS/inspect_ai

Inspect AI是英国AI安全研究所（AISI）开发的AI安全评估框架，是AISI进行前沿模型安全评估的官方工具。它采用任务（Task）+求解器（Solver）的架构，提供灵活的评分机制，适合设计和执行标准化的AI安全评估，特别适合合规审计场景。

### 2.5 DeepTeam 🔵B级

- **开发方**：Confident AI
- **定位**：多轮对话红队框架
- **核心能力**：专为多轮对话设计、"红队即代码"理念、支持对话系统深度测试
- **优点**：对话场景优化、API简洁、易于集成
- **缺点**：项目较新、生态尚在建设中
- **适用场景**：对话系统、聊天机器人测试
- **GitHub**：https://github.com/confident-ai/deepteam

DeepTeam由Confident AI开发，是专为多轮对话系统设计的红队测试框架。它秉持"红队即代码"（Red Teaming as Code）的理念，使用简洁的API即可定义复杂的多轮对话攻击场景，特别适合聊天机器人、智能客服等对话型AI系统的安全测试。

### 2.6 Purple Llama 🟢A级（Meta官方开源）

- **开发方**：Meta
- **定位**：Meta AI安全评估套件
- **核心能力**：包含Llama Guard等安全分类器、CyberSecEval基准测试、负责任AI工具集
- **优点**：Meta官方维护、与Llama生态深度集成、安全分类器质量高
- **缺点**：偏向Meta生态、通用红队编排能力较弱
- **适用场景**：Meta/Llama生态模型评估、安全分类器使用
- **GitHub**：https://github.com/meta-llama/PurpleLlama

Purple Llama是Meta开源的AI安全评估套件，包含Llama Guard（输入输出安全分类器）、CyberSecEval（网络安全基准测试）等工具。Llama Guard是目前最常用的开源LLM安全分类器之一，可用于对模型输入输出进行实时安全过滤，也可作为红队测试的自动评分器。

---

## 3. 工具选型对比矩阵

| 对比维度 | Garak | PyRIT | Promptfoo | Inspect AI | DeepTeam | Purple Llama |
|---------|-------|-------|-----------|------------|----------|--------------|
| **开发方** | NVIDIA | Microsoft | Promptfoo(OpenAI) | UK AISI | Confident AI | Meta |
| **可信度** | 🟢A级 | 🟢A级 | 🟢A级 | 🔵B级 | 🔵B级 | 🟢A级 |
| **上手时间** | 分钟级 | 小时级 | 分钟级 | 小时级 | 分钟级 | 小时级 |
| **多轮攻击能力** | 弱 | 强 | 中 | 中 | 强 | 弱 |
| **CI/CD集成** | 好 | 需定制 | 开箱即用 | 需定制 | 好 | 需定制 |
| **学习曲线** | 平缓 | 陡峭 | 平缓 | 中等 | 平缓 | 中等 |
| **Web UI** | 无 | 无 | 有 | 无 | 无 | 无 |
| **自定义探针** | Python | Python | YAML/Prompt | Python | Python | Python |
| **最佳场景** | 快速扫描/CI门禁 | 深度红队研究 | 工程团队DevSecOps | 标准化评估/合规 | 对话系统测试 | Llama生态/分类器 |

---

## 4. 选型建议（按场景）

| 场景 | 推荐工具 | 理由 |
|------|---------|------|
| 快速基线扫描（想先跑起来看看） | Garak | 单命令启动，覆盖已知漏洞，NVIDIA官方维护 |
| 工程团队持续测试（要集成CI） | Promptfoo | 开发者友好，CI/CD开箱即用，Web UI可视化，OpenAI收购背书 |
| 深度红队研究（安全专家使用） | PyRIT | 最灵活的多轮攻击编排，支持前沿攻击算法，Microsoft官方维护 |
| 多轮对话系统测试 | DeepTeam | 专为对话设计，"红队即代码"理念 |
| Meta/Llama生态 | Purple Llama | 官方工具，Llama Guard分类器质量高 |
| 合规/标准化评估 | Inspect AI | AISI官方框架，适合政府/合规场景 |
| 初创团队快速起步 | Promptfoo | 上手最快，无需编程，覆盖主流风险 |
| 企业级安全团队 | PyRIT + Garak | PyRIT深度测试 + Garak CI回归，覆盖全场景 |

---

## 5. CI/CD集成建议

### 5.1 推荐Pipeline分层策略

```
代码提交 → Promptfoo/Garak快速扫描（<5分钟）→ 阻断高危漏洞合并
    ↓
每日夜间构建 → PyRIT深度多轮攻击（小时级）→ 生成详细报告
    ↓
版本上线前 → 全量红队测试（人工+自动化）→ 合规审查签字
    ↓
生产环境 → 持续监控+定期红队演练→ 漏洞闭环管理
```

### 5.2 阈值建议

根据BeyondScale 2026年发布的行业基准数据：
- 未采取防御措施的系统：首次攻击成功率（ASR）约17.8%，200次迭代后达78.6%
- 建议目标：攻击成功率（ASR）< 20%（基线门槛），< 10%（成熟目标）
- 高危漏洞（如提示注入导致数据泄露）：ASR必须为0%

### 5.3 持续红队四组件

构建持续红队能力需要四个核心组件：
1. **探针库**：维护不断更新的攻击payload库，覆盖最新攻击技术
2. **测试运行器**：自动化执行测试，支持并行和分布式运行
3. **结果存储**：存储历史测试结果，支持趋势分析和对比
4. **告警路由**：将发现的漏洞自动路由到对应团队跟踪修复

---

## 6. 关键数据参考

| 数据点 | 数值 | 来源 | 可信度 |
|--------|------|------|--------|
| 角色扮演提示注入攻击成功率 | 89.6% | arXiv:2505.04806 (2025) | 🔵B级 |
| GPT-4平均越狱时间 | < 17分钟 | arXiv:2505.04806 (2025) | 🔵B级 |
| PAIR算法10次迭代对Gemini成功率 | 73% | BeyondScale 2026 | 🔵B级 |
| 未防御系统首次攻击ASR | 17.8% | BeyondScale 2026 | 🔵B级 |
| 未防御系统200次迭代后ASR | 78.6% | BeyondScale 2026 | 🔵B级 |
| 有效代码审查缺陷发现率 | 高达90% | 软件工程行业数据 | 🟢A级 |
| 缺陷流入生产后修复成本增加 | 10-100倍 | IBM Systems Sciences Institute | 🟢A级 |

---

## 7. 参考资料

1. Garak - NVIDIA LLM Vulnerability Scanner - https://github.com/leondz/garak 🟢A级
2. PyRIT - Microsoft AI Red Team Framework - https://github.com/Azure/PyRIT 🟢A级
3. Promptfoo - LLM Red Teaming Platform - https://github.com/promptfoo/promptfoo 🟢A级
4. Inspect AI - UK AISI AI Safety Evaluation - https://github.com/UKGovernmentBEIS/inspect_ai 🔵B级
5. DeepTeam - Multi-turn Red Teaming - https://github.com/confident-ai/deepteam 🔵B级
6. Purple Llama - Meta AI Safety Toolkit - https://github.com/meta-llama/PurpleLlama 🟢A级
7. arXiv:2505.04806 - Jailbreaking Leading LLMs (2025) 🔵B级
8. BeyondScale - AI Red Teaming Benchmark Report (2026) 🔵B级
