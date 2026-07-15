---
id: "agent-engineering-methodology-index"
title: "Agent工程方法论"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/README.toml"
category: "learning"
date: "2026-07-09"
---
# Agent工程方法论

## 🎯 主题概述

> **Agent工程方法论是构建高质量AI Agent的工程实践体系**。随着AI Agent从玩具走向生产，单纯的Prompt Engineering已经不够——我们需要一整套从上下文管理、运行时驾驭到迭代循环的系统工程方法。本模块系统梳理四代AI工程范式演进，汇集业界顶尖实践者（Karpathy/Addy Osmani/阿里技术等）的实战经验与方法论。

### 四代工程范式演进

AI工程方法论遵循**瓶颈外移规律**：每当模型变强一截，整个系统的瓶颈就往外移一层：

| 范式演进 | 核心瓶颈 | 关注重点 | 标志性成果 |
|---------|---------|---------|-----------|
| 1️⃣ **Prompt Engineering** | 你怎么说 | 提示词技巧、思维链、Few-shot | 各种提示词模板与配方 |
| 2️⃣ **Context Engineering** | 你给什么 | 上下文窗口管理、RAG、记忆系统 | 检索增强、上下文压缩 |
| 3️⃣ **Harness Engineering** | 它干活的环境 | 运行时框架、工具链、沙箱环境 | Deep Agents、Agent Harness |
| 4️⃣ **Loop Engineering** | 你自己身上 | 人机协作循环、验证反馈闭环 | 第一性原理+对抗式审查 |

> **核心洞察**：为什么同样用GPT、用Claude，有的团队做出来的Agent又稳又能打，到别人手里却一跑就崩？差距不在模型本身，而在模型之外的那一整套工程体系——Harness。

---

## 📚 子Wiki索引（9个专题）

| 子Wiki目录 | 文件数 | 核心主题 |
|-----------|--------|---------|
| [agent-skills-wiki/](agent-skills-wiki/00-overview.md) | 8篇 | **Addy Osmani Agent Skills教程**：谷歌Gemini团队主管开源的生产级AI编程代理人工程技能库（GitHub 1.9万+星），6阶段生命周期模型、20个核心技能、7个斜杠命令、深度融入Google工程文化 |
| [harness-engineering-wiki/](harness-engineering-wiki/00-overview.md) | 10篇 | **Harness Engineering驾驭工程**：阿里技术发布的三代AI工程范式演进，四条反直觉铁律、六大工程模式、悟空AI招聘实战案例、行业标杆地图、未来趋势与六条心法 |
| [harness-seven-components-wiki/](harness-seven-components-wiki/00-overview.md) | 14篇 | **Harness七大组件**：曲凯提出的AI Agent业务运行底座七大组件——模型网关、工具注册表、知识库引擎、记忆系统、策略引擎、可观测性、配置管理；含理论详解、文章Agent实战案例、实践指南、FAQ、速查手册 |
| [headroom-context-compression-wiki/](headroom-context-compression-wiki/00-overview.md) | 11篇 | **Headroom上下文压缩中间件**：给Agent装"压缩层"的完整技术方案，1万Token压到1千且质量不降反升，六种压缩算法、CCR可逆机制、四种接入方式、跨Agent记忆与自动学习 |
| [karpathy-llm-coding-guidelines/](karpathy-llm-coding-guidelines/00-overview.md) | 8篇 | **Karpathy LLM编程准则**：GitHub 61.6k星爆火项目，四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动）管住AI编程最常犯的毛病，四种分发格式（CLAUDE.md/Cursor Rules/SKILL.md/插件），Multica平台与multica-cli Skill详解 |
| [longcat-agent-learning-wiki/](longcat-agent-learning-wiki/00-overview.md) | 9篇 | **LongCat-2.0 Agent实测**：美团1.6T参数MoE模型接入Claude Code完整流程，架构解析、配置指南、BI数据看板项目实战、Token效率对比、Loop Engineering方法论 |
| [adversarial-review-wiki/](adversarial-review-wiki/00-overview.md) | 15篇 | **对抗性审查方法论知识库**：证伪主义驱动的质量保障方法论，两大应用场景（知识研究+AI协作代码审查），七模块验证协议、12类认知偏差防御、六大开源工具、AIHOT实战案例，自举验证达标（一级来源75.0%、🟢A级69.8%、关键事实100%交叉验证） |
| [seven-concepts-prompt-wiki/](seven-concepts-prompt-wiki/00-overview.md) | 16篇 | **七概念×GPT-5.6新Prompt工程范式**：OpenAI官方Prompting指南+SpecWeave七概念方法论（R-I-E-C-A-F-V）深度整合，GCOB四要素框架、10条减法原则、6组Before/After对照、Chat/Work/Codex三场景实战（含8个Codex模板）、25个反模式、6个可复制模板、一页纸速查表，Token减少41-66%、Eval提升10-15% |
| [seven-concepts-deeptutor-wiki/](seven-concepts-deeptutor-wiki/00-overview.md) | 33篇 | **七概念×DeepTutor实践教程**：七概念方法论与HKUDS开源AI学习助手DeepTutor的深度映射分析，理论→案例→融合分析→实践四段式结构，38个术语表、42个CLN精确引文、三层"哪里体现→机制→好处"分析框架、3条核心组合链路（R→I→E/A→V→C/F→V→I）、分级练习与20项自检清单 |

---

## 📄 根级文档索引（11篇专题）

| 文档 | 一句话摘要 | 核心价值 |
|------|-----------|---------|
| [agent-skills-wiki.md](agent-skills-wiki.md) | Addy Osmani Agent Skills完整教程索引 | 谷歌工程文化+20个技能+7个斜杠命令，8章原子化文档导航 |
| [harness-engineering-wiki.md](harness-engineering-wiki.md) | Harness Engineering驾驭工程系统性学习Wiki | 三代范式演进+四条铁律+六大模式+悟空案例，10章导航 |
| [harness-seven-components-wiki.md](harness-seven-components-wiki.md) | Harness七大组件：从Prompt到业务交付 | 模型网关/工具注册表/知识库/记忆/策略/可观测性/配置七大组件详解，文章Agent实战案例+实践指南+FAQ+速查手册，14章导航 |
| [headroom-context-compression-wiki.md](headroom-context-compression-wiki.md) | Headroom上下文压缩中间件完整教程索引 | 六种算法+CCR机制+四种接入，11章导航+快速上手 |
| [karpathy-llm-coding-guidelines-tutorial.md](karpathy-llm-coding-guidelines-tutorial.md) | Karpathy LLM编程准则完整教程 | 四条准则+正反代码例+四种安装方式+Multica生态 |
| [longcat-agent-learning-wiki.md](longcat-agent-learning-wiki.md) | LongCat-2.0 Agent能力实测Wiki教程 | MoE架构+Claude Code接入+BI实战+Token效率+Loop Engineering |
| [dspark-paper-wiki.md](dspark-paper-wiki.md) | DeepSeek DSpark论文系统化学习Wiki | 10个递进式概念拆解，单用户提速85%、高并发吞吐翻4倍，Eagle+DFlash+马尔可夫头核心技术 |
| [four-engineering-concepts-wiki.md](four-engineering-concepts-wiki.md) | AI四大工程概念演进：Prompt→Context→Harness→Loop | 瓶颈外移规律深度解析，四代范式关系总结，关键人物原话引用 |
| [harness-loop-engineering-article-analysis.md](harness-loop-engineering-article-analysis.md) | Loop Engineering与AI系统工程范式转移深度分析 | Hugging Face对照实验（同模型76.6分差距）、Karpathy AutoResearch（700次实验）、双层自动研究架构 |
| [workbuddy-four-layers-seven-concepts-analysis.md](workbuddy-four-layers-seven-concepts-analysis.md) | WorkBuddy四层工程×七概念框架跨体系深度分析 | 七概念与WorkBuddy四层工程映射强度4.7/5，28组子概念细粒度对照，提炼5条元原则（含两轮事实核查记录） |
| [vibe-coding-prompts-learning-analysis.md](vibe-coding-prompts-learning-analysis.md) | Vibe Coding两大神级Prompt学习分析 | 第一性原理（管生成）+对抗式审查（管验证）构成完整闭环，非程序员也能稳定产出可用产品的方法论 |
| [seven-concepts-prompt-wiki/](seven-concepts-prompt-wiki/README.md) | 七概念×GPT-5.6新Prompt工程范式完整Wiki | OpenAI官方指南+七概念方法论整合，16章原子化教程，GCOB框架/6组Before-After/三场景实战（含8个Codex模板）/25反模式/一页纸速查表 |
| [seven-concepts-deeptutor-wiki/](seven-concepts-deeptutor-wiki/README.md) | 七概念×DeepTutor实践教程完整Wiki | 七概念方法论与DeepTutor开源AI学习助手的33篇深度映射分析，理论→案例→融合→实践四段式，含三层分析框架/3条组合链路/分级练习/20项自检清单 |

---

## 🚀 推荐学习路径

根据学习目标选择适合的路径：

### 路径一：范式演进全景（推荐新手建立认知）

> **目标**：理解AI工程范式的演进脉络，建立全局认知

```
four-engineering-concepts-wiki.md
  → harness-engineering-wiki/01-paradigm-evolution.md
  → harness-engineering-wiki/02-four-iron-laws.md
  → vibe-coding-prompts-learning-analysis.md
```

1. 先读四代工程概念演进，理解瓶颈外移规律
2. 深入Harness Engineering的范式演进与铁律
3. 学习Vibe Coding的两大神级Prompt，建立生成+验证闭环思维

### 路径二：AI编程实战路径

> **目标**：提升AI辅助编程的质量与效率，解决乱猜/过度设计/乱改问题

```
karpathy-llm-coding-guidelines/00-overview.md
  → karpathy-llm-coding-guidelines/01-four-principles.md
  → karpathy-llm-coding-guidelines/02-code-examples.md
  → karpathy-llm-coding-guidelines/03-quickstart.md
  → agent-skills-wiki/00-overview.md
```

1. 从Karpathy四条准则开始（61.6k星验证）
2. 理解每条原则的具体要求和检验标准
3. 研究真实代码正反例，识别反模式
4. 选择一种格式安装到你的开发环境
5. 进阶学习Addy Osmani的20个工程技能

### 路径三：生产级Agent构建路径

> **目标**：构建稳定、高效的生产级Agent系统

```
harness-engineering-wiki/00-overview.md
  → harness-seven-components-wiki/00-overview.md
  → harness-seven-components-wiki/09-practice-guide.md
  → harness-engineering-wiki/03-six-patterns.md
  → harness-engineering-wiki/04-wukong-case-study.md
  → harness-seven-components-wiki/10-case-study.md
  → headroom-context-compression-wiki/00-overview.md
```

1. 建立Harness Engineering的系统认知
2. 深入七大组件：理解模型网关→配置管理每个组件的职责和设计原则
3. 学习实践指南：四阶段落地路线图和七步搭建法
4. 掌握六大可复用工程模式
5. 通过悟空AI招聘案例理解工程化落地
6. 通过文章Agent案例理解组件协作和Badcase闭环
7. 学习上下文压缩技术解决Token瓶颈

### 路径四：前沿技术与性能优化路径

> **目标**：了解大模型推理加速前沿，掌握Loop Engineering方法论与对抗性审查

```
dspark-paper-wiki.md
  → longcat-agent-learning-wiki/00-overview.md
  → longcat-agent-learning-wiki/04-token-efficiency.md
  → longcat-agent-learning-wiki/05-loop-engineering.md
  → adversarial-review-wiki/00-overview.md
  → adversarial-review-wiki/03-methodology-framework.md
  → adversarial-review-wiki/08-practice-cases.md
```

1. 学习DSpark论文的推测解码与系统工程优化
2. 了解LongCat-2.0国产大模型的Agent能力
3. 对比Token效率数据
4. 掌握Loop Engineering迭代修复方法论
5. 深入对抗性审查：证伪主义驱动的质量保障体系（七模块协议+攻击者视角）
6. 通过AIHOT实战案例理解对抗审查如何发现正常路径遗漏的BUG

---

## 🧭 快速导航（按场景分组）

| 场景分类 | 推荐阅读 |
|---------|---------|
| 🚫 **AI编程反模式** | [karpathy-llm-coding-guidelines/01-four-principles.md](karpathy-llm-coding-guidelines/01-four-principles.md)（四条准则）→ [karpathy-llm-coding-guidelines/02-code-examples.md](karpathy-llm-coding-guidelines/02-code-examples.md)（正反例） |
| 🏗️ **Agent架构设计** | [harness-engineering-wiki/03-six-patterns.md](harness-engineering-wiki/03-six-patterns.md)（六大模式）→ [harness-seven-components-wiki/00-overview.md](harness-seven-components-wiki/00-overview.md)（七大组件）→ [harness-engineering-wiki/04-wukong-case-study.md](harness-engineering-wiki/04-wukong-case-study.md)（悟空案例）→ [harness-seven-components-wiki/10-case-study.md](harness-seven-components-wiki/10-case-study.md)（文章Agent案例） |
| 📦 **上下文管理** | [headroom-context-compression-wiki/02-compression-algorithms.md](headroom-context-compression-wiki/02-compression-algorithms.md)（压缩算法）→ [headroom-context-compression-wiki/03-ccr-mechanism.md](headroom-context-compression-wiki/03-ccr-mechanism.md)（CCR机制） |
| 🧪 **工程文化** | [agent-skills-wiki/04-google-engineering-culture.md](agent-skills-wiki/04-google-engineering-culture.md)（Hyrum定律等8个术语） |
| ⚡ **性能优化** | [dspark-paper-wiki.md](dspark-paper-wiki.md)（DSpark推理加速）→ [longcat-agent-learning-wiki/04-token-efficiency.md](longcat-agent-learning-wiki/04-token-efficiency.md)（Token效率） |
| 🔄 **人机协作循环** | [vibe-coding-prompts-learning-analysis.md](vibe-coding-prompts-learning-analysis.md)（两大神级Prompt）→ [longcat-agent-learning-wiki/05-loop-engineering.md](longcat-agent-learning-wiki/05-loop-engineering.md)（Loop Engineering）→ [adversarial-review-wiki/03-methodology-framework.md](adversarial-review-wiki/03-methodology-framework.md)（对抗性审查七模块协议） |
| 🛡️ **质量保障/对抗审查** | [adversarial-review-wiki/00-overview.md](adversarial-review-wiki/00-overview.md)（知识库概览）→ [adversarial-review-wiki/04-cognitive-biases-defense.md](adversarial-review-wiki/04-cognitive-biases-defense.md)（12类认知偏差防御）→ [adversarial-review-wiki/05-checklists-templates.md](adversarial-review-wiki/05-checklists-templates.md)（检查清单模板）→ [adversarial-review-wiki/08-practice-cases.md](adversarial-review-wiki/08-practice-cases.md)（AIHOT实战案例） |
| 📐 **方法论全景** | [four-engineering-concepts-wiki.md](four-engineering-concepts-wiki.md)（四代范式演进） |
| 🧠 **七概念方法论实践** | [seven-concepts-deeptutor-wiki/](seven-concepts-deeptutor-wiki/README.md)（七概念×DeepTutor案例教程）→ [seven-concepts-deeptutor-wiki/03-analysis/08-combined-workflows.md](seven-concepts-deeptutor-wiki/03-analysis/08-combined-workflows.md)（组合工作流分析）→ [seven-concepts-deeptutor-wiki/04-learning-path/01-practice-exercises.md](seven-concepts-deeptutor-wiki/04-learning-path/01-practice-exercises.md)（实践练习） |
| ✍️ **Prompt工程新范式** | [seven-concepts-prompt-wiki/](seven-concepts-prompt-wiki/README.md)（GPT-5.6新写法+七概念整合）→ [seven-concepts-prompt-wiki/05-before-after-examples.md](seven-concepts-prompt-wiki/05-before-after-examples.md)（6组Before/After）→ [seven-concepts-prompt-wiki/13-quick-reference.md](seven-concepts-prompt-wiki/13-quick-reference.md)（一页纸速查表） |

---

## 🔗 相关资源

- [📁 知识库首页](../../README.md) - 返回知识库总入口
- [📁 Agent协议与接口](../01-agent-protocols-interfaces/README.md) - Agent互联互通的协议基础
- [📁 Agent平台与工具](../03-agent-platforms-tools/README.md) - 主流Agent平台与工具生态调研
- [📁 团队最佳实践库](../../best-practices/README.md) - 代码审查、工具配置等最佳实践
