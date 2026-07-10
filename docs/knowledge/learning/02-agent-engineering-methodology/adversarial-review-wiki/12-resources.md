---
id: "adversarial-review-resources-index"
title: "12、延伸阅读与资源索引"
category: "knowledge"
date: "2026-07-10"
version: "1.0"
status: "completed"
---

# 对抗性审查：延伸阅读与资源索引

---

## 1. 说明

本文档按主题分类整理对抗性审查相关的外部资源链接，包括官方标准文档、开源工具文档、优质技术博客、学习路径资源，以及项目内关联文档。学术论文资源请参见[09-academic-resources.md](09-academic-resources.md)。

可信度标记说明：
- 🟢A级：官方组织/标准文档/头部科技公司官方资源
- 🔵B级：权威厂商实践/社区优质文档
- 🟡C级：优质博客/个人分享

---

## 2. 官方文档与标准

### 2.1 OWASP系列文档 🟢A级

| 资源名称 | 链接 | 内容简介 |
|---------|------|---------|
| OWASP LLM Top 10 (2025) | https://owasp.org/Top10/2025/ | LLM应用十大风险清单，2025版新增系统提示泄露和向量/嵌入弱点 |
| OWASP Gen AI Red Teaming Guide | https://owasp.org/www-project-gen-ai-red-teaming-guide/ | 生成式AI红队测试正式指南，五阶段方法论 |
| OWASP Secure Code Review Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html | 安全代码审查速查表，六大类核心安全问题检查清单 |
| OWASP Code Review Guide v2 | https://owasp.org/www-project-code-review-guide/ | 完整代码审查指南（200+页），方法论、技术控制审查、框架特定审查 |
| OWASP Testing Guide | https://owasp.org/www-project-web-security-testing-guide/ | Web安全测试指南，渗透测试方法论参考 |

### 2.2 NIST标准文档 🟢A级

| 资源名称 | 链接 | 内容简介 |
|---------|------|---------|
| NIST AI Risk Management Framework (AI RMF) | https://www.nist.gov/artificial-intelligence/risk-management-framework | NIST AI风险管理框架，将持续红队列为核心安全措施 |
| NIST AI RMF Playbook | https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook | AI RMF配套实践手册，具体操作指引 |
| NIST SP 800-161 (Supply Chain Risk) | https://csrc.nist.gov/publications/detail/sp/800-161/rev-1/final | 供应链风险管理，对抗供应链攻击参考 |

### 2.3 MITRE标准文档 🟢A级

| 资源名称 | 链接 | 内容简介 |
|---------|------|---------|
| MITRE ATLAS (AI系统威胁全景) | https://atlas.mitre.org/ | AI系统对抗性威胁知识库，战术/技术/案例矩阵 |
| MITRE ATT&CK | https://attack.mitre.org/ | 网络威胁战术技术知识库，传统红队参考 |
| MITRE Engenuity Center for Threat-Informed Defense | https://ctid.mitre-engenuity.org/ | 威胁情报驱动防御研究 |

### 2.4 法规与政策文档 🟢A级

| 资源名称 | 链接 | 内容简介 |
|---------|------|---------|
| EU AI Act 官方文本 | https://artificialintelligenceact.eu/ | 欧盟人工智能法案全文，高风险AI系统对抗性测试合规要求 |
| NIST AI Safety Institute Consortium | https://www.nist.gov/aisi | NIST AISI联盟，AI安全标准制定 |
| ISO/IEC 42001 (AI管理体系) | https://www.iso.org/standard/81230.html | AI管理体系国际标准 |

---

## 3. 开源工具官方文档

### 3.1 Garak（NVIDIA）🟢A级

| 资源 | 链接 |
|------|------|
| GitHub仓库 | https://github.com/leondz/garak |
| 官方文档 | https://docs.garak.ai/ |
| 快速开始指南 | https://github.com/leondz/garak#quick-start |

**简介**：NVIDIA官方开源LLM漏洞扫描器，基于探针架构，单命令启动基线扫描，适合CI门禁快速扫描。

### 3.2 PyRIT（Microsoft）🟢A级

| 资源 | 链接 |
|------|------|
| GitHub仓库 | https://github.com/Azure/PyRIT |
| 官方文档 | https://azure.github.io/PyRIT/ |
| 教程Notebooks | https://github.com/Azure/PyRIT/tree/main/doc/tutorials |

**简介**：Microsoft官方开源红队攻击编排框架，支持Crescendo/TAP/PAIR等多轮攻击算法，适合深度红队研究。

### 3.3 Promptfoo（OpenAI）🟢A级

| 资源 | 链接 |
|------|------|
| GitHub仓库 | https://github.com/promptfoo/promptfoo |
| 官方文档 | https://www.promptfoo.dev/docs/intro/ |
| CI/CD集成指南 | https://www.promptfoo.dev/docs/integrations/ci-cd/ |
| 红队测试文档 | https://www.promptfoo.dev/docs/red-team/ |

**简介**：开发者友好的红队测试平台（2026年被OpenAI收购），YAML声明式配置，Web UI可视化，工程团队CI/CD首选。

### 3.4 Inspect AI（UK AISI）🔵B级

| 资源 | 链接 |
|------|------|
| GitHub仓库 | https://github.com/UKGovernmentBEIS/inspect_ai |
| 官方文档 | https://inspect.ai-safety-institute.org.uk/ |
| 入门教程 | https://inspect.ai-safety-institute.org.uk/tutorial.html |

**简介**：英国AI安全研究所官方评估框架，适合标准化安全评估和合规审计。

### 3.5 其他工具文档

| 工具 | 链接 | 可信度 | 简介 |
|------|------|--------|------|
| DeepTeam | https://github.com/confident-ai/deepteam | 🔵B级 | 多轮对话红队框架，"红队即代码" |
| Purple Llama | https://github.com/meta-llama/PurpleLlama | 🟢A级 | Meta Llama生态安全评估套件，含Llama Guard |
| Llama Guard | https://llama.meta.com/trust-and-safety/ | 🟢A级 | Meta开源安全分类器 |

---

## 4. 优质技术博客与厂商实践

### 4.1 NVIDIA安全博客 🟢A级

| 资源 | 链接 | 内容 |
|------|------|------|
| NVIDIA AI Security Blog | https://developer.nvidia.com/blog/tag/security/ | NVIDIA AI安全研究、Garak更新、LLM安全实践 |

### 4.2 Microsoft Azure AI安全文档 🟢A级

| 资源 | 链接 | 内容 |
|------|------|------|
| Azure AI Red Teaming | https://learn.microsoft.com/en-us/azure/ai-services/red-teaming/ | Azure官方AI红队测试指南与最佳实践 |
| PyRIT技术博客 | https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/bg-p/AzureAIServicesBlog | PyRIT更新、红队技术分享 |
| Microsoft Security Blog | https://www.microsoft.com/en-us/security/blog/ | 微软安全响应中心、AI安全研究 |

### 4.3 OpenAI安全研究 🟢A级

| 资源 | 链接 | 内容 |
|------|------|------|
| OpenAI Safety Research | https://openai.com/safety | OpenAI安全研究主页 |
| OpenAI Red Teaming Network | https://openai.com/index/red-teaming-network/ | OpenAI外部红队网络项目 |
| Promptfoo Blog（OpenAI收购后） | https://www.promptfoo.dev/blog/ | Promptfoo工程实践、CI/CD红队集成 |

### 4.4 BeyondScale持续红队博客 🔵B级

| 资源 | 链接 | 内容 |
|------|------|------|
| BeyondScale AI Security | https://www.beyondscale.ai/blog | 2026年AI红队基准报告、行业数据、持续红队实践（已验证链接） |

### 4.5 其他优质资源

| 资源 | 链接 | 可信度 | 简介 |
|------|------|--------|------|
| Google DeepMind Safety | https://deepmind.google/safety/ | 🟢A级 | DeepMind AI安全研究 |
| Anthropic Safety | https://www.anthropic.com/safety | 🟢A级 | Anthropic Constitutional AI、红队研究 |
| LLM Security News | https://llmsecurity.net/ | 🔵B级 | LLM安全新闻聚合 |
| Embrace The Red | https://embracethered.com/blog/ | 🔵B级 | 个人博客，提示注入与LLM安全深度文章 |
| Simon Willison's Weblog | https://simonwillison.net/ | 🔵B级 | 知名开发者博客，LLM安全实践 |

---

## 5. 学习路径资源

### 5.1 LLM红队入门教程

| 资源 | 链接 | 难度 | 可信度 |
|------|------|------|--------|
| OWASP Gen AI Red Teaming Guide（入门首选） | https://owasp.org/www-project-gen-ai-red-teaming-guide/ | 入门 | 🟢A级 |
| Promptfoo Getting Started | https://www.promptfoo.dev/docs/intro/ | 入门 | 🟢A级 |
| Garak Quick Start | https://github.com/leondz/garak#quick-start | 入门 | 🟢A级 |
| "Red Teaming LLMs" 实践指南 | https://learn.microsoft.com/en-us/azure/ai-services/red-teaming/ | 进阶 | 🟢A级 |
| Awesome LLM Red Teaming（GitHub Awesome列表） | https://github.com/topics/llm-red-teaming | 参考 | 🔵B级 |

### 5.2 代码审查最佳实践

| 资源 | 链接 | 难度 | 可信度 |
|------|------|------|--------|
| OWASP Secure Code Review Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html | 入门 | 🟢A级 |
| Google Code Review Guide | https://google.github.io/eng-practices/review/ | 进阶 | 🟢A级 |
| "Best Kept Secrets of Peer Code Review"（SmartBear） | https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/ | 进阶 | 🔵B级 |
| Conventional Comments（代码评论规范） | https://conventionalcomments.org/ | 入门 | 🔵B级 |

### 5.3 认知心理学入门

| 资源 | 链接 | 难度 | 可信度 |
|------|------|------|--------|
| 《思考，快与慢》（卡尼曼）- 系统1/系统2 | 书籍 | 入门 | 🟢A级 |
| 《穷查理宝典》- 人类误判心理学 | 书籍 | 入门 | 🟢A级 |
| "Cognitive Biases in Software Engineering"（研究论文） | https://arxiv.org/abs/2103.00732 | 专业 | 🔵B级 |
| 认知偏差百科（Wikipedia） | https://en.wikipedia.org/wiki/List_of_cognitive_biases | 参考 | 🟢A级 |

---

## 6. 项目内关联资源

以下为知识库内相关文档，使用相对路径链接：

### 6.1 第一性原理知识库相关文档

| 文档 | 路径 | 简介 |
|------|------|------|
| 对抗性审查协议原始规范 | [../../first-principles/00-adversarial-review-protocol.md](../../first-principles/00-adversarial-review-protocol.md) | 知识研究场景对抗审查协议原始版本 |
| 第一性原理核心概念术语表 | [../../first-principles/06-concepts-glossary.md](../../first-principles/06-concepts-glossary.md) | 第一性原理思维相关术语，含确认偏差等认知偏差定义 |
| 第一性原理知识库总览 | [../../first-principles/README.md](../../first-principles/README.md) | 第一性原理知识库入口 |

### 6.2 对抗性审查知识库内部文档

| 文档 | 路径 | 简介 |
|------|------|------|
| 知识库总览 | [00-overview.md](00-overview.md) | 项目简介、可信度评级、阅读路径 |
| 核心概念定义 | [01-core-concepts.md](01-core-concepts.md) | 对抗性审查精确定义、两大分支、四大攻击者角色 |
| 哲学起源 | [02-philosophy-origins.md](02-philosophy-origins.md) | 证伪主义、红队历史、认知心理学革命 |
| 认知偏差防御 | [04-cognitive-biases-defense.md](04-cognitive-biases-defense.md) | 10+类认知偏差识别与防御 |
| 行业标准 | [06-industry-standards.md](06-industry-standards.md) | OWASP/NIST/MITRE/EU AI Act详解 |
| 开源工具链 | [07-open-source-tools.md](07-open-source-tools.md) | Garak/PyRIT/Promptfoo等工具对比选型 |
| 实战案例 | [08-practice-cases.md](08-practice-cases.md) | AIHOT项目40Agent审查案例、典型BUG案例 |
| 学术资源 | [09-academic-resources.md](09-academic-resources.md) | 学术论文、研究报告（本文档收录非学术资源） |
| 核心术语表 | [11-glossary.md](11-glossary.md) | 本文件配套术语表 |
| 快速参考速查表 | [13-quick-reference.md](13-quick-reference.md) | 打印版速查卡 |

### 6.3 模式文档与实践指南

| 文档 | 路径 | 简介 |
|------|------|------|
| 对抗式审查Prompt模式 | [../../../../retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.md](../../../../retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.md) | AI协作场景对抗审查Prompt标准模式 |
| Agent通信协议速查表 | [../../01-agent-protocols-interfaces/agent-communication-protocols/11-quick-reference.md](../../01-agent-protocols-interfaces/agent-communication-protocols/11-quick-reference.md) | MCP/A2A/ACP/ANP协议速查（格式参考） |

---

## 7. 资源更新说明

本文档将随知识库建设持续更新。发现优质资源请补充并标注可信度。

**验证状态**：所有官方标准链接（OWASP/NIST/MITRE/EU AI Act）和开源工具GitHub链接均已验证可访问（2026-07-10）。

---

*本文件版本：v1.0 | 创建日期：2026-07-10 | 可信度：官方资源均为🟢A级，社区资源标注对应等级*
