---
id: "agent-engineering-methodology-index"
title: "Agent工程方法论"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/README.toml"
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

## 📚 子Wiki索引（5个专题）

| 子Wiki目录 | 文件数 | 核心主题 |
|-----------|--------|---------|
| [agent-skills-wiki/](agent-skills-wiki/00-overview.md) | 8篇 | **Addy Osmani Agent Skills教程**：谷歌Gemini团队主管开源的生产级AI编程代理人工程技能库（GitHub 1.9万+星），6阶段生命周期模型、20个核心技能、7个斜杠命令、深度融入Google工程文化 |
| [harness-engineering-wiki/](harness-engineering-wiki/00-overview.md) | 10篇 | **Harness Engineering驾驭工程**：阿里技术发布的三代AI工程范式演进，四条反直觉铁律、六大工程模式、悟空AI招聘实战案例、行业标杆地图、未来趋势与六条心法 |
| [headroom-context-compression-wiki/](headroom-context-compression-wiki/00-overview.md) | 11篇 | **Headroom上下文压缩中间件**：给Agent装"压缩层"的完整技术方案，1万Token压到1千且质量不降反升，六种压缩算法、CCR可逆机制、四种接入方式、跨Agent记忆与自动学习 |
| [karpathy-llm-coding-guidelines/](karpathy-llm-coding-guidelines/00-overview.md) | 8篇 | **Karpathy LLM编程准则**：GitHub 61.6k星爆火项目，四条行为准则（编码前先思考/简约至上/精确编辑/目标驱动）管住AI编程最常犯的毛病，四种分发格式（CLAUDE.md/Cursor Rules/SKILL.md/插件），Multica平台与multica-cli Skill详解 |
| [longcat-agent-learning-wiki/](longcat-agent-learning-wiki/00-overview.md) | 9篇 | **LongCat-2.0 Agent实测**：美团1.6T参数MoE模型接入Claude Code完整流程，架构解析、配置指南、BI数据看板项目实战、Token效率对比、Loop Engineering方法论 |

---

## 📄 根级文档索引（8篇专题）

| 文档 | 一句话摘要 | 核心价值 |
|------|-----------|---------|
| [agent-skills-wiki.md](agent-skills-wiki.md) | Addy Osmani Agent Skills完整教程索引 | 谷歌工程文化+20个技能+7个斜杠命令，8章原子化文档导航 |
| [harness-engineering-wiki.md](harness-engineering-wiki.md) | Harness Engineering驾驭工程系统性学习Wiki | 三代范式演进+四条铁律+六大模式+悟空案例，10章导航 |
| [headroom-context-compression-wiki.md](headroom-context-compression-wiki.md) | Headroom上下文压缩中间件完整教程索引 | 六种算法+CCR机制+四种接入，11章导航+快速上手 |
| [karpathy-llm-coding-guidelines-tutorial.md](karpathy-llm-coding-guidelines-tutorial.md) | Karpathy LLM编程准则完整教程 | 四条准则+正反代码例+四种安装方式+Multica生态 |
| [longcat-agent-learning-wiki.md](longcat-agent-learning-wiki.md) | LongCat-2.0 Agent能力实测Wiki教程 | MoE架构+Claude Code接入+BI实战+Token效率+Loop Engineering |
| [dspark-paper-wiki.md](dspark-paper-wiki.md) | DeepSeek DSpark论文系统化学习Wiki | 10个递进式概念拆解，单用户提速85%、高并发吞吐翻4倍，Eagle+DFlash+马尔可夫头核心技术 |
| [four-engineering-concepts-wiki.md](four-engineering-concepts-wiki.md) | AI四大工程概念演进：Prompt→Context→Harness→Loop | 瓶颈外移规律深度解析，四代范式关系总结，关键人物原话引用 |
| [vibe-coding-prompts-learning-analysis.md](vibe-coding-prompts-learning-analysis.md) | Vibe Coding两大神级Prompt学习分析 | 第一性原理（管生成）+对抗式审查（管验证）构成完整闭环，非程序员也能稳定产出可用产品的方法论 |

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
  → harness-engineering-wiki/03-six-patterns.md
  → harness-engineering-wiki/04-wukong-case-study.md
  → headroom-context-compression-wiki/00-overview.md
  → headroom-context-compression-wiki/02-compression-algorithms.md
  → headroom-context-compression-wiki/03-ccr-mechanism.md
```

1. 建立Harness Engineering的系统认知
2. 掌握六大可复用工程模式
3. 通过悟空AI招聘案例理解落地实践
4. 学习上下文压缩技术解决Token瓶颈
5. 深入六种压缩算法与CCR可逆机制

### 路径四：前沿技术与性能优化路径

> **目标**：了解大模型推理加速前沿，掌握Loop Engineering方法论

```
dspark-paper-wiki.md
  → longcat-agent-learning-wiki/00-overview.md
  → longcat-agent-learning-wiki/04-token-efficiency.md
  → longcat-agent-learning-wiki/05-loop-engineering.md
```

1. 学习DSpark论文的推测解码与系统工程优化
2. 了解LongCat-2.0国产大模型的Agent能力
3. 对比Token效率数据
4. 掌握Loop Engineering迭代修复方法论

---

## 🧭 快速导航（按场景分组）

| 场景分类 | 推荐阅读 |
|---------|---------|
| 🚫 **AI编程反模式** | [karpathy-llm-coding-guidelines/01-four-principles.md](karpathy-llm-coding-guidelines/01-four-principles.md)（四条准则）→ [karpathy-llm-coding-guidelines/02-code-examples.md](karpathy-llm-coding-guidelines/02-code-examples.md)（正反例） |
| 🏗️ **Agent架构设计** | [harness-engineering-wiki/03-six-patterns.md](harness-engineering-wiki/03-six-patterns.md)（六大模式）→ [harness-engineering-wiki/04-wukong-case-study.md](harness-engineering-wiki/04-wukong-case-study.md)（实战案例） |
| 📦 **上下文管理** | [headroom-context-compression-wiki/02-compression-algorithms.md](headroom-context-compression-wiki/02-compression-algorithms.md)（压缩算法）→ [headroom-context-compression-wiki/03-ccr-mechanism.md](headroom-context-compression-wiki/03-ccr-mechanism.md)（CCR机制） |
| 🧪 **工程文化** | [agent-skills-wiki/04-google-engineering-culture.md](agent-skills-wiki/04-google-engineering-culture.md)（Hyrum定律等8个术语） |
| ⚡ **性能优化** | [dspark-paper-wiki.md](dspark-paper-wiki.md)（DSpark推理加速）→ [longcat-agent-learning-wiki/04-token-efficiency.md](longcat-agent-learning-wiki/04-token-efficiency.md)（Token效率） |
| 🔄 **人机协作循环** | [vibe-coding-prompts-learning-analysis.md](vibe-coding-prompts-learning-analysis.md)（两大神级Prompt）→ [longcat-agent-learning-wiki/05-loop-engineering.md](longcat-agent-learning-wiki/05-loop-engineering.md)（Loop Engineering） |
| 📐 **方法论全景** | [four-engineering-concepts-wiki.md](four-engineering-concepts-wiki.md)（四代范式演进） |

---

## 🔗 相关资源

- [📁 知识库首页](../../README.md) - 返回知识库总入口
- [📁 Agent协议与接口](../01-agent-protocols-interfaces/README.md) - Agent互联互通的协议基础
- [📁 Agent平台与工具](../03-agent-platforms-tools/README.md) - 主流Agent平台与工具生态调研
- [📁 团队最佳实践库](../../best-practices/README.md) - 代码审查、工具配置等最佳实践
