---
id: "adversarial-review-academic"
title: "09、学术资源与推荐阅读"
category: "knowledge"
date: "2026-07-10"
version: "1.0"
status: "completed"
---

# 09、学术资源与推荐阅读

## 1. 概述

本文件收录经过筛选的学术论文、权威书籍、研究报告和厂商实践资源，为对抗式审查方法论提供理论基础和深入学习材料。

**可信度评级说明**：
| 评级 | 说明 | 使用建议 |
|------|------|----------|
| 🟢 A级 | 奠基性经典、同行评审顶会/顶刊论文、官方权威标准 | 核心学习材料，理论基础，可直接引用 |
| 🔵 B级 | 重要研究、预印本、厂商实践报告、高质量技术博客 | 辅助学习材料，建议交叉验证 |
| 🟡 C级 | 参考资料、二手来源、存在一定争议 | 仅作参考，建议追溯原始来源 |

所有资源尽可能提供开放获取链接。

---

## 2. 认知偏差与判断心理学（奠基性文献）🟢A级

对抗式审查的核心理论基础来自认知心理学——理解为什么人类（和AI）会自审失效，才能设计出有效的对抗机制。

| 资源 | 作者 | 发表 | 可信度 | 核心贡献 | 链接/获取方式 |
|------|------|------|--------|---------|--------------|
| **"Judgment under Uncertainty: Heuristics and Biases"** | Tversky, A., & Kahneman, D. | Science, 1974 | 🟢A级 | 认知心理学奠基论文（50000+引用），系统阐述三种启发式（代表性/可得性/锚定）及其导致的系统性偏差。Kahneman因此获2002年诺贝尔经济学奖。对抗式审查中"攻击者视角"的设计，正是为了克服这些启发式导致的盲区。 | https://doi.org/10.1126/science.185.4157.1124 |
| **"Confirmation Bias: A Ubiquitous Phenomenon in Many Guises"** | Nickerson, R. S. | Review of General Psychology, 1998 | 🟢A级 | 确认偏差里程碑式综述（7000+引用），系统梳理确认偏差在科学推理、医学诊断、司法判断、代码审查等多领域的表现形式。**单Agent自审失效的核心心理学依据——人们倾向于寻找支持自己信念的证据，而非反驳证据。** | https://doi.org/10.1037/1089-2680.2.2.175 |
| **《思考，快与慢》*Thinking, Fast and Slow*** | Daniel Kahneman | Farrar, Straus and Giroux, 2011 | 🟢A级 | 双系统理论（System 1快思考/System 2慢思考）普及著作，系统阐述各种认知偏差。为什么"看起来简单的任务更容易出错"？System 1自动走直觉捷径，跳过验证步骤——这是对抗式审查需要强制打断的机制。适合非心理学背景读者。 | 书籍（中信出版社有中译本） |
| **"Cognitive Biases in Software Engineering: A Systematic Mapping Study"** | 多作者 | IEEE Access, 2021 | 🔵B级 | 系统梳理软件工程领域已被实证的认知偏差，包括锚定效应、过度自信、确认偏差在需求分析、设计、编码、测试、审查各阶段的表现。 | IEEE Xplore（机构访问） |

---

## 3. LLM红队测试与AI安全研究

### 3.1 核心奠基论文

| 资源 | 作者/机构 | 发表 | 可信度 | 核心贡献 | 链接 |
|------|----------|------|--------|---------|------|
| **"Summon a demon and bind it: A grounded theory of LLM red teaming"** | NVIDIA+华盛顿大学+CHAI等 | PLOS One, 2025 | 🟢A级 | **LLM红队领域目前最扎实的定性研究**——基于对数十名从业者数千分钟访谈的扎根理论，定义LLM红队五大特征、三大攻击策略类别（语言攻击/修辞攻击/虚构攻击），明确区分安全红队vs内容红队，提出红队成熟度模型。所有做LLM对抗测试的人都应该读。 | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0314658 （开放获取） |
| **"Towards debiasing code review support"** | Jetzen et al., 那慕尔大学 | IEEE/ACM International Conference on Program Comprehension, 2025 | 🟢A级 | 学术研究**实证证明确认偏差和决策疲劳在代码审查中的影响**——开发者在审查自己写的或自己熟悉的代码时，问题发现率显著下降。论文提出去偏化原型设计，为"为什么多Agent/多角色审查比自审有效"提供了直接的软件工程实证依据。 | https://xdevroey.be/publication/jetzen-2025/jetzen-2025.pdf （作者开放获取版） |

### 3.2 重要研究与预印本

| 资源 | 作者/机构 | 发表 | 可信度 | 核心贡献 | 链接 |
|------|----------|------|--------|---------|------|
| **"Replicating TEMPEST at Scale: Multi-Turn Adversarial Attacks Against Trillion-Parameter Frontier Models"** | 多机构（含MIT、CMU等） | arXiv, 2025 | 🔵B级（预印本） | 对10个前沿万亿参数模型进行1000种有害行为、97000+次查询的大规模红队测试。结论：**多轮攻击可以突破几乎所有模型的安全护栏**，单轮测试通过率高不代表安全，多轮链式攻击成功率显著更高。 | https://arxiv.org/pdf/2512.07059 （开放获取） |
| **"An End-to-End Overview of Red Teaming for Large Language Models"** | 多作者 | TrustNLP 2025 (ACL Workshop) | 🔵B级 | LLM红队端到端综述，覆盖攻击策略分类、防御方法、评估指标、自动化红队工具全流程。入门红队的全景图。 | https://aclanthology.org/2025.trustnlp-main.23.pdf （开放获取） |
| **"Redefining AI Red Teaming in the Agentic Era: From Weeks to Hours"** | Dreadnode | arXiv, 2026 | 🔵B级（预印本） | 智能体时代红队测试框架，提出自然语言驱动的自动化红队方法，将传统数周的红队流程压缩到数小时，覆盖45+种攻击类型。适合关注Agent安全的读者。 | https://arxiv.org/pdf/2605.04019v1 （开放获取） |
| **"Jailbroken: How Does LLM Safety Training Fail?"** | Qi et al. | arXiv, 2023 | 🔵B级 | 早期经典越狱论文，分析安全训练失效的两种模式：Competing Objectives（安全目标与有用性目标冲突）和Mismatched Generalization（训练分布与攻击分布不匹配）。理解为什么对抗测试必要的基础文献。 | https://arxiv.org/pdf/2307.02483 （开放获取） |
| **"Universal and Transferable Adversarial Attacks on Aligned Language Models"** | Zou et al. | arXiv, 2023 | 🔵B级 | 提出GCG（Greedy Coordinate Gradient）攻击方法，可以自动生成通用对抗后缀，实现黑盒迁移攻击。自动化对抗攻击的开山之作。 | https://arxiv.org/pdf/2307.15043 （开放获取） |

### 3.3 间接提示注入与Agent安全

| 资源 | 作者/机构 | 发表 | 可信度 | 核心贡献 | 链接 |
|------|----------|------|--------|---------|------|
| **"Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"** | Greshake et al. | AISec 2023 | 🟢A级 | 间接提示注入的奠基性论文——首次系统论证恶意网页、文档、邮件等外部内容可以劫持LLM代理行为。EchoLeak等零交互漏洞的理论前瞻性研究。 | https://arxiv.org/pdf/2302.12173 （开放获取） |
| **"Examining the Consequences of Adversarial Prompting on the Security of LLM-Integrated Systems"** | 多机构 | USENIX Security, 2025 | 🟢A级 | USENIX Security顶会论文，系统评估对抗提示对LLM集成系统的安全影响，包含多个真实系统的案例研究。 | USENIX官网（开放获取） |

---

## 4. 代码审查与软件工程质量

对抗式审查本质上是代码审查和安全审计在AI时代的升级，这些经典软件工程文献依然是重要基础。

| 资源 | 作者 | 发表 | 可信度 | 核心贡献 | 链接 |
|------|------|------|--------|---------|------|
| **OWASP Code Review Guide v2** | OWASP Foundation | 2017（持续更新） | 🟢A级 | 开源安全代码审查权威指南，提供完整的方法论和检查清单。对抗式审查的安全攻击者角色检查项很大程度上基于OWASP指南。 | https://owasp.org/www-project-code-review-guide/ （开放获取） |
| **OWASP Top 10 for LLM Applications** | OWASP Foundation | 2025（v1.5持续更新） | 🟢A级 | LLM应用十大安全风险的事实标准，包括提示注入、不安全输出处理、数据泄露等。对抗式审查检查清单的重要依据。 | https://owasp.org/www-project-top-10-for-large-language-model-applications/ （开放获取） |
| **MITRE ATLAS (Adversarial Threat Landscape for AI Systems)** | MITRE | 持续更新 | 🟢A级 | 对抗性AI威胁态势矩阵，类比ATT&CK框架，系统化AI系统的攻击战术、技术和案例库。AI红队的战术手册。 | https://atlas.mitre.org/ （开放获取） |
| **《程序员修炼之道》*The Pragmatic Programmer*** | Hunt & Thomas | Addison-Wesley, 1999（2019新版） | 🟢A级 | 防御性编程、程序员思维训练经典。"要有敬畏心"、"不要假设"、"早崩溃"等原则与对抗式审查思想高度一致。 | 书籍（电子工业出版社有中译本） |
| **《代码大全》*Code Complete*** | Steve McConnell | Microsoft Press, 2004（第二版） | 🟢A级 | 软件工程百科全书式经典，代码审查、边界条件分析、防御式编程等章节有极高实践价值。第22章"开发者测试"和第24章"代码评审"与对抗式审查直接相关。 | 书籍（电子工业出版社有中译本） |
| **"Best Kept Secrets of Peer Code Review"** | Jason Cohen | Smart Bear, 2006 | 🔵B级 | 基于实践数据的代码审查最佳实践——代码评审大小与发现率关系（超过400行的审查发现率急剧下降）、评审速率、发现缺陷密度等实证研究。数据驱动的代码审查方法论。 | 书籍/白皮书（可在线免费获取） |

---

## 5. 科学方法论与证伪主义

对抗式审查的哲学根基来自批判理性主义——科学不是去证实，而是去证伪。

| 资源 | 作者 | 发表 | 可信度 | 核心贡献 | 链接/获取 |
|------|------|------|--------|---------|----------|
| **《科学发现的逻辑》*The Logic of Scientific Discovery*** | Karl Popper | 1934（1959英译本） | 🟢A级 | **证伪主义奠基作**——科学与非科学的划界标准不是"可证实"而是"可证伪"。科学的方法不是寻找支持自己的证据，而是寻找反驳自己的证据。这正是对抗式审查的核心哲学：不去"证明代码正确"，而是"证明代码有问题"。 | 书籍（中国美术学院出版社有中译本） |
| **《猜想与反驳》*Conjectures and Refutations*** | Karl Popper | 1963 | 🟢A级 | 波普尔后期著作，系统阐述"猜想-反驳"方法论：科学通过提出大胆猜想，然后尽力反驳它们而进步。对抗式审查就是软件工程中的"反驳"环节。 | 书籍（上海译文出版社有中译本） |
| **《新工具》*Novum Organum*** | Francis Bacon | 1620 | 🟢A级 | 四假象说（种族假象/洞穴假象/市场假象/剧场假象）系统阐述人类认知的系统性偏差来源。比现代认知心理学早400年的偏差分类。归纳法与科学实验方法论奠基。 | 书籍（商务印书馆有中译本） |
| **《第一哲学沉思集》*Meditations on First Philosophy*** | René Descartes | 1641 | 🟢A级 | **普遍怀疑方法**——系统怀疑一切可怀疑之物，直到找到不可怀疑的基石。对抗式审查中的"攻击者视角"本质上就是笛卡尔式怀疑在软件工程中的应用：假设一切可被攻击，直到证明不能。 | 书籍（商务印书馆有中译本） |

---

## 6. 厂商实践博客与官方文档 🔵B级

这些厂商实践虽然不是同行评审学术论文，但来自一线实践者，有很高参考价值。

| 资源 | 发布方 | 内容 | 链接 |
|------|--------|------|------|
| **"Hardening Atlas against prompt injection"** | OpenAI官方博客 | OpenAI如何用AI红队加固Atlas浏览器代理，对抗间接提示注入。AI驱动自动化红队的官方实践。 | https://openai.com/index/hardening-atlas-against-prompt-injection/ |
| **"Defining LLM Red Teaming"** | NVIDIA Developer Blog | NVIDIA官方对LLM红队的定义、分类和实践框架，与PLOS One论文配套的实践指南。 | https://developer.nvidia.com/blog/defining-llm-red-teaming/ |
| **"AI Red Teaming Agent (preview)"** | Microsoft Azure Azure AI Foundry文档 | Azure内置AI红队工具官方文档，包括风险分类、扫描方法、评估指标。 | https://learn.microsoft.com/en-gb/azure/ai-foundry/concepts/ai-red-teaming-agent |
| **"Continuous LLM Red Teaming"** | BeyondScale | 持续红队架构实践，包含ASR（攻击成功率）基准数据、自动化流水线设计、与CI/CD集成方法。 | https://beyondscale.tech/blog/continuous-llm-red-teaming |
| **"Approaches to LLM Red Teaming at Anthropic"** | Anthropic | Anthropic对LLM红队的方法论、负责任扩展政策（RSP）、红队与模型训练的结合方式。 | https://www.anthropic.com/index/approaches-to-llm-red-teaming |
| **"Red Teaming Language Models to Reduce Harms"** | DeepMind (Google) | DeepMind在LLM红队方面的方法、分类法、经验教训，含21类有害行为分类。 | https://arxiv.org/pdf/2209.07858 （预印本开放获取） |

---

## 7. 工具文档与实践指南 🔵B级

| 资源 | 类型 | 内容 | 链接 |
|------|------|------|------|
| **Promptfoo Documentation** | 开源工具 | 最流行的LLM红队和测试工具之一，文档包含大量红队测试方法论、Payload示例、CI集成指南。 | https://www.promptfoo.dev/docs/red-team/ |
| **Garak Documentation** | 开源工具 | NVIDIA开源的LLM漏洞扫描器，文档包含50+插件的攻击类型说明和使用指南。 | https://docs.garak.ai/ |
| **MITRE ATLAS Case Studies** | 威胁矩阵 | MITRE ATLAS收录的真实AI系统攻击案例库，每个案例包含攻击链、TTP映射、缓解措施。 | https://atlas.mitre.org/studies |
| **NIST AI Risk Management Framework** | 标准框架 | NIST AI风险管理框架，系统化AI风险治理、测量、管理方法。 | https://www.nist.gov/itl/ai-risk-management-framework |

---

## 8. 阅读路径建议

根据不同背景和目标，推荐以下阅读路径：

### 8.1 入门路径（工程实践导向，1-2周）

适合只想快速上手对抗式审查的工程师：

1. **Day 1-2**：先读《思考，快与慢》前5章，理解System 1/System 2和基本认知偏差概念
2. **Day 3-4**：读卡兹克《Vibe Coding两大神级Prompt》+ 本Wiki第08章实战案例，建立直观认识
3. **Day 5-6**：读OWASP Top 10 LLM，了解LLM应用安全风险分类
4. **Day 7+**：选一个工具（Promptfoo或Garak），按照文档跑通第一个红队测试

### 8.2 进阶路径（理解理论基础，2-4周）

适合想深入理解方法论为什么有效的读者：

1. 入门路径全部内容
2. 读Tversky & Kahneman 1974奠基论文和Nickerson 1998确认偏差综述
3. 读NVIDIA PLOS One 2025扎根理论论文，理解LLM红队的学术框架
4. 读Jetzen et al. 2025代码审查去偏论文，理解多角色审查的软件工程实证
5. 读波普尔《猜想与反驳》前三章，理解证伪主义哲学基础

### 8.3 安全工程师/红队路径（专业深入，1-2月）

适合专注AI安全和红队的专业人员：

1. 进阶路径全部内容
2. MITRE ATLAS矩阵精读 + 所有案例研究
3. 精读间接提示注入相关论文（Greshake et al. 2023）
4. 多轮攻击论文（TEMPEST at Scale 2025）
5. 至少一个工具深度源码阅读（Garak或Promptfoo）
6. 跟踪arXiv cs.CR和cs.AI分类最新预印本

### 8.4 理论研究路径（学术导向）

适合做相关研究的学者和研究生：

1. 从Tversky & Kahneman 1974开始，系统阅读认知心理学经典
2. 波普尔证伪主义→库恩范式理论→费耶阿本德认识论无政府主义，理解科学方法论谱系
3. 所有LLM红队核心论文按时间顺序阅读（2023年越狱论文→2024年调查→2025年PLOS One等扎根理论）
4. 关注USENIX Security、CCS、S&P、NDSS四大安全顶会的AI安全相关论文
5. 关注ACL、EMNLP等NLP顶会的TrustNLP等Workshop

---

## 9. 资源获取提示

### 9.1 开放获取资源优先

- 优先选择arXiv、PLOS One、ACL Anthology等开放获取平台
- 厂商官方博客和工具文档绝大多数是开放的
- MITRE、OWASP、NIST等标准框架全部免费开放

### 9.2 付费资源合法获取途径

- 学术论文通过大学图书馆、研究机构访问获取
- 书籍建议购买正版或通过图书馆借阅
- 不要传播盗版资源

### 9.3 预印本注意事项

- arXiv等预印本平台论文**尚未经过同行评审**，可信度标注为🔵B级
- 预印本代表最新研究方向，但结论可能在正式发表时修改
- 如果预印本后续在顶会/顶刊正式发表，以正式发表版本为准

---

## 本Wiki完整索引

- [00-overview.md](00-overview.md) 概述与导航
- [01-core-concepts.md](01-core-concepts.md) 核心概念
- [02-philosophy-origins.md](02-philosophy-origins.md) 哲学溯源
- [03-methodology-framework.md](03-methodology-framework.md) 方法论框架
- [04-cognitive-biases-defense.md](04-cognitive-biases-defense.md) 认知偏差与防御
- [05-checklists-templates.md](05-checklists-templates.md) 检查清单与模板
- [06-industry-standards.md](06-industry-standards.md) 行业标准与框架
- [07-open-source-tools.md](07-open-source-tools.md) 开源工具生态
- [08-practice-cases.md](08-practice-cases.md) 实战案例集
- **[09-academic-resources.md](09-academic-resources.md)** 学术资源与推荐阅读（本文件）
