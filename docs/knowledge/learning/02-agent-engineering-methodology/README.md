---
id: "agent-engineering-methodology-index"
title: "Agent工程方法论"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/README.toml"
category: "learning"
date: "2026-07-09"
last_updated: "2026-08-22"
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

## 📚 主题分组索引（6大主题域）

| 分组目录 | Wiki数 | 核心主题 |
|---------|--------|---------|
| [01-paradigms/](01-paradigms/README.md) | 4个wiki+2索引 | **范式演进与Agent架构**：四代工程范式、Harness Engineering驾驭工程、Harness七大组件、Loop Engineering深度分析 |
| [02-prompt-coding/](02-prompt-coding/README.md) | 3个wiki+3文档 | **AI编程与Prompt工程**：Karpathy四条准则、Addy Osmani Agent Skills、七概念×新Prompt范式、Vibe Coding |
| [03-methodology/](03-methodology/README.md) | 2个wiki+1分析 | **七概念方法论体系**：七概念×DeepTutor实践教程、对抗性审查方法论知识库、WorkBuddy跨体系分析 |
| [04-context-optimization/](04-context-optimization/README.md) | 3个wiki+1索引 | **上下文与Token优化**：LLM Token优化体系、Trae IDE特化模式、Headroom上下文压缩中间件 |
| [05-evaluation/](05-evaluation/README.md) | 2个wiki | **Agent评测体系**：评测工程手册（生命周期组织）+评测方法论档案（R-F-I-E-V链路） |
| [06-performance/](06-performance/README.md) | 2个wiki+1文档+1索引 | **推理加速与性能优化**：DSpark推测解码、LongCat-2.0实测、Intel Neural Compressor量化 |

> **💡 同主题双入口引导**：`05-evaluation/` 下两个wiki同为主标题"Agent评测体系化建设方法论"，但定位互补：
> - **📘 agent-evaluation-wiki（工程手册）**：面向落地，按评测生命周期组织，是教程主体与长期维护入口
> - **📐 agent-eval-methodology-wiki（方法论创作档案）**：面向方法论链路（R-F-I-E-V）与创作过程，核心价值在附录产出与知乎文章

---

## 🚀 推荐学习路径

### 路径一：范式演进全景（推荐新手建立认知）

> **目标**：理解AI工程范式的演进脉络，建立全局认知

```
01-paradigms/four-engineering-concepts-wiki.md
  → 01-paradigms/harness-engineering-wiki/01-paradigm-evolution.md
  → 01-paradigms/harness-engineering-wiki/02-four-iron-laws.md
  → 02-prompt-coding/vibe-coding-prompts-learning-analysis.md
```

### 路径二：AI编程实战路径

> **目标**：提升AI辅助编程的质量与效率，解决乱猜/过度设计/乱改问题

```
02-prompt-coding/karpathy-llm-coding-guidelines/00-overview.md
  → 02-prompt-coding/karpathy-llm-coding-guidelines/01-four-principles.md
  → 02-prompt-coding/karpathy-llm-coding-guidelines/02-code-examples.md
  → 02-prompt-coding/agent-skills-wiki/00-overview.md
```

### 路径三：生产级Agent构建路径

> **目标**：构建稳定、高效的生产级Agent系统

```
01-paradigms/harness-engineering-wiki/00-overview.md
  → 01-paradigms/harness-seven-components-wiki/00-overview.md
  → 01-paradigms/harness-seven-components-wiki/09-practice-guide.md
  → 01-paradigms/harness-engineering-wiki/03-six-patterns.md
  → 04-context-optimization/headroom-context-compression-wiki/00-overview.md
```

### 路径四：方法论与质量保障路径

> **目标**：掌握七概念方法论与对抗性审查，构建质量闭环

```
03-methodology/seven-concepts-deeptutor-wiki/00-overview.md
  → 03-methodology/adversarial-review-wiki/00-overview.md
  → 03-methodology/adversarial-review-wiki/03-methodology-framework.md
  → 01-paradigms/harness-loop-engineering-article-analysis.md
```

### 路径五：性能优化路径

> **目标**：了解推理加速前沿与Token优化实践

```
06-performance/dspark-paper-wiki.md
  → 04-context-optimization/llm-token-optimization/README.md
  → 06-performance/longcat-agent-learning-wiki/04-token-efficiency.md
```

---

## 🧭 快速导航（按场景分组）

| 场景分类 | 推荐阅读 |
|---------|---------|
| 🚫 **AI编程反模式** | [karpathy-llm-coding-guidelines/01-four-principles.md](02-prompt-coding/karpathy-llm-coding-guidelines/01-four-principles.md) → [02-code-examples.md](02-prompt-coding/karpathy-llm-coding-guidelines/02-code-examples.md) |
| 🏗️ **Agent架构设计** | [harness-engineering-wiki/03-six-patterns.md](01-paradigms/harness-engineering-wiki/03-six-patterns.md) → [harness-seven-components-wiki/00-overview.md](01-paradigms/harness-seven-components-wiki/00-overview.md) |
| 📦 **上下文管理** | [headroom-context-compression-wiki/](04-context-optimization/headroom-context-compression-wiki/README.md) → [llm-token-optimization/](04-context-optimization/llm-token-optimization/README.md) |
| 🧪 **工程文化** | [agent-skills-wiki/04-google-engineering-culture.md](02-prompt-coding/agent-skills-wiki/04-google-engineering-culture.md) |
| ⚡ **性能优化** | [dspark-paper-wiki.md](06-performance/dspark-paper-wiki.md) → [llm-token-optimization/](04-context-optimization/llm-token-optimization/README.md) |
| 🔄 **人机协作循环** | [vibe-coding-prompts-learning-analysis.md](02-prompt-coding/vibe-coding-prompts-learning-analysis.md) → [Loop Engineering分析](01-paradigms/harness-loop-engineering-article-analysis.md) |
| 🛡️ **质量保障/对抗审查** | [adversarial-review-wiki/](03-methodology/adversarial-review-wiki/README.md) → [04-cognitive-biases-defense.md](03-methodology/adversarial-review-wiki/04-cognitive-biases-defense.md) |
| 📐 **方法论全景** | [four-engineering-concepts-wiki.md](01-paradigms/four-engineering-concepts-wiki.md) |
| 🧠 **七概念方法论实践** | [seven-concepts-deeptutor-wiki/](03-methodology/seven-concepts-deeptutor-wiki/README.md) → [03-analysis/08-combined-workflows.md](03-methodology/seven-concepts-deeptutor-wiki/03-analysis/08-combined-workflows.md) |
| ✍️ **Prompt工程新范式** | [seven-concepts-prompt-wiki/](02-prompt-coding/seven-concepts-prompt-wiki/README.md) → [05-before-after-examples.md](02-prompt-coding/seven-concepts-prompt-wiki/05-before-after-examples.md) |
| 🧪 **Agent评测** | [agent-evaluation-wiki/](05-evaluation/agent-evaluation-wiki/README.md) → [agent-eval-methodology-wiki/](05-evaluation/agent-eval-methodology-wiki/README.md) |

---

## 🔗 相关资源

- [📁 知识库首页](../../README.md) - 返回知识库总入口
- [📁 Agent协议与接口](../01-agent-protocols-interfaces/README.md) - Agent互联互通的协议基础
- [📁 Agent平台与工具](../03-agent-platforms-tools/README.md) - 主流Agent平台与工具生态调研
- [📁 团队最佳实践库](../../best-practices/README.md) - 代码审查、工具配置等最佳实践

---

## Changelog

- 2026-08-21 | refactor | 目录分组归类：14个平铺wiki+12个散落文件按6大主题域分组（paradigms/prompt-coding/methodology/context-optimization/evaluation/performance），物理结构与逻辑认知模型对齐
- 2026-07-09 | create | 初始版本，11个专题wiki索引
