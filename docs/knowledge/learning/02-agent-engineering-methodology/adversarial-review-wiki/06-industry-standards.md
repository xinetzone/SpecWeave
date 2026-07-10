---
id: "adversarial-review-standards"
title: "06、行业标准与合规要求"
category: "knowledge"
date: "2026-07-10"
version: "1.0"
status: "completed"
---

## 1. 概述

对抗性审查/红队测试正在从"最佳实践"演变为"合规要求"。主要标准组织包括：OWASP、NIST、MITRE，以及EU AI Act等法规。本文档汇总当前主流的行业标准和合规要求，为对抗性审查实践提供权威参考依据。

可信度标记说明：
- 🟢A级：标准组织官方文档、法规文本
- 🔵B级：厂商实践、社区文档
- 🟡C级：博客文章、个人经验分享

---

## 2. OWASP系列标准 🟢A级

OWASP（Open Web Application Security Project，开放Web应用安全项目）是全球最具影响力的Web应用安全组织，其发布的系列标准是安全审查领域的事实基准。

### 2.1 OWASP Secure Code Review Cheat Sheet

- **来源**：OWASP官方，🟢A级
- **核心要点**：安全代码审查方法论、常见漏洞模式、审查技术、检查清单（输入验证/认证/授权/加密/业务逻辑/配置）、SDLC集成
- **链接**：https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html
- **适用场景**：传统代码安全审查基础

该速查表提供了简明的代码审查检查清单，适合在日常代码审查中快速查阅。覆盖了从输入验证到配置管理的六大类核心安全问题。

### 2.2 OWASP Code Review Guide v2

- **来源**：OWASP官方，🟢A级
- **核心要点**：完整代码审查指南（200+页），方法论、技术控制审查、框架特定审查、OWASP Top 10对应检查项
- **链接**：https://owasp.org/www-project-code-review-guide/
- **适用场景**：建立正式代码审查流程

这是一份系统化的代码审查指南，详细介绍了代码审查的完整方法论，包括如何组建审查团队、执行审查流程、记录发现、跟踪修复等，是建立正式安全审查流程的权威参考。

### 2.3 OWASP LLM Top 10 (2025)

- **来源**：OWASP官方，🟢A级
- **核心要点**：LLM应用十大风险——提示注入(LLM01)、不安全输出处理(LLM02)、训练数据投毒(LLM03)、模型拒绝服务(LLM04)、供应链漏洞(LLM05)、敏感信息泄露(LLM06)、不安全插件设计(LLM07)、过度代理(LLM08)、过度依赖(LLM09)、模型盗窃(LLM10)。2025年新增系统提示泄露和向量/嵌入弱点
- **链接**：https://owasp.org/Top10/2025/
- **适用场景**：LLM应用安全审查基准

OWASP LLM Top 10是LLM应用安全领域最权威的风险清单，2025版在2023版基础上进行了重要更新，新增了系统提示泄露和向量/嵌入弱点等新兴风险类别，是LLM应用对抗性审查的核心基准。

### 2.4 OWASP Gen AI Red Teaming Guide (2025)

- **来源**：OWASP官方，🟢A级
- **核心要点**：生成式AI红队测试正式指南，区分模型级漏洞vs系统级漏洞，七类漏洞分类法，五阶段方法论（侦察→攻击生成→执行→验证→缓解重测）
- **链接**：https://owasp.org/www-project-gen-ai-red-teaming-guide/
- **适用场景**：AI系统红队测试流程设计

这是OWASP发布的首份生成式AI红队测试正式指南，明确区分了模型级漏洞和系统级漏洞，提供了结构化的五阶段红队方法论，是设计AI系统红队测试流程的标准参考。

---

## 3. NIST标准 🟢A级

NIST（美国国家标准与技术研究院）发布的AI风险管理框架是企业级AI治理的重要参考。

### 3.1 NIST AI Risk Management Framework (AI RMF 100-5e2025)

- **来源**：NIST（美国国家标准与技术研究院），🟢A级
- **核心要点**：将持续红队演练列为Measure功能下的核心安全措施，明确红队是"压力条件下的对抗性测试"，是持续活动而非上线前一次性门禁
- **链接**：https://www.nist.gov/artificial-intelligence/risk-management-framework
- **适用场景**：企业级AI风险管理体系建设

NIST AI RMF将AI风险管理分为Govern（治理）、Map（映射）、Measure（测量）、Manage（管理）四大核心功能。在Measure功能中，明确将对抗性测试（红队演练）作为评估AI系统安全性的核心手段，并强调这是一项贯穿全生命周期的持续活动，而非产品上线前的一次性验收。

---

## 4. MITRE标准 🟢A级

MITRE是全球知名的安全研究机构，其ATT&CK框架已成为网络威胁领域的事实标准。

### 4.1 MITRE ATLAS (Adversarial Threat Landscape for AI Systems)

- **来源**：MITRE，🟢A级
- **核心要点**：针对AI系统的攻击技术知识库，类似ATT&CK矩阵，可用于红队测试用例映射、攻击场景构建
- **链接**：https://atlas.mitre.org/
- **适用场景**：AI系统威胁建模、红队测试用例设计

MITRE ATLAS（AI系统对抗性威胁全景）是专门针对AI系统的攻击技术知识库，采用与ATT&CK类似的矩阵结构，包含战术、技术、案例研究等完整信息。可用于：
- AI系统威胁建模
- 红队测试用例映射
- 攻击场景构建
- 防御措施有效性验证

---

## 5. 法规要求 🟢A级

随着AI技术的快速发展，全球范围内的AI监管法规正在加速落地，对抗性测试已成为明确的合规要求。

### 5.1 EU AI Act（2026年8月生效）

- **来源**：欧盟官方公报，🟢A级
- **核心要点**：高风险AI系统必须实施"贯穿全生命周期的迭代测试"，对抗性测试为强制性要求，违规罚款最高达全球营业额6%或3000万欧元
- **适用场景**：面向欧盟市场的AI产品合规

《欧盟人工智能法案》（EU AI Act）是全球首部综合性AI监管法规，将于2026年8月正式生效。该法案将AI系统按风险等级分为四类：不可接受风险、高风险、有限风险、最小风险。对于高风险AI系统，法案明确要求：
- 在上市前进行系统性的对抗性测试
- 在整个生命周期中持续进行迭代测试
- 建立风险管理体系，覆盖从开发到部署的全流程
- 违规企业将面临最高达全球年营业额6%或3000万欧元的罚款（以较高者为准）

---

## 6. 标准选择建议

| 场景 | 推荐标准 | 优先级 |
|------|---------|--------|
| 传统代码安全审查 | OWASP Secure Code Review Cheat Sheet | 高 |
| LLM应用审查 | OWASP LLM Top 10 + OWASP Gen AI Red Teaming | 高 |
| 企业AI风险管理 | NIST AI RMF | 中 |
| 威胁建模/攻击用例 | MITRE ATLAS | 中 |
| 欧盟合规 | EU AI Act | 按业务需要 |

---

## 7. 参考资料

1. OWASP Secure Code Review Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html 🟢A级
2. OWASP Code Review Guide v2 - https://owasp.org/www-project-code-review-guide/ 🟢A级
3. OWASP LLM Top 10 (2025) - https://owasp.org/Top10/2025/ 🟢A级
4. OWASP Gen AI Red Teaming Guide (2025) - https://owasp.org/www-project-gen-ai-red-teaming-guide/ 🟢A级
5. NIST AI Risk Management Framework - https://www.nist.gov/artificial-intelligence/risk-management-framework 🟢A级
6. MITRE ATLAS - https://atlas.mitre.org/ 🟢A级
7. EU AI Act - 欧盟官方公报 🟢A级
