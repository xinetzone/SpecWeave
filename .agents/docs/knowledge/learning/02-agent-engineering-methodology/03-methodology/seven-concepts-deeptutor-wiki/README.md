---
id: seven-concepts-deeptutor-index
title: "七概念×DeepTutor实践教程"
category: "learning"
date: "2026-07-14"
version: "1.0"
status: "completed"
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
tags: [七概念, 方法论, DeepTutor, 教程]
---

# 七概念×DeepTutor实践教程

> **L2级Agent工程方法论实践教程**，将SpecWeave R-I-E-C-A-F-V七概念方法论系统映射到DeepTutor AI学习助手的真实产品实践中。通过剖析一个完整的Agent应用架构，展示七概念方法论在实际产品设计、模块划分、工作流设计中的具体体现，帮助读者从理论到实践建立完整的认知。

## 🎯 教程简介

本教程以DeepTutor（香港大学数据科学实验室HKUDS开发的开源AI学习助手）为案例，系统讲解SpecWeave七概念方法论（R-复盘/I-洞察/E-萃取/C-原子提交/A-原子化/F-第一性原理/V-对抗性审查）在真实Agent产品中的落地应用。

与纯理论教程不同，本教程采用"理论→案例→映射→实践"的四段式结构：
- **理论篇**：重温七概念核心公理与要素
- **案例篇**：深入剖析DeepTutor的9大模块架构
- **映射篇**：逐个展示七概念在DeepTutor中的具体体现
- **实践篇**：提供学习路径、练习与自检工具

## 👥 目标读者

| 读者类型 | 阅读目标 | 预计耗时 |
|---------|---------|---------|
| **Agent开发者** | 理解如何用七概念指导Agent架构设计 | 6-8小时 |
| **方法论实践者** | 看到七概念在真实产品中的具体落地 | 4-6小时 |
| **AI产品经理** | 学习优秀Agent产品的模块划分思路 | 3-5小时 |
| **DeepTutor用户** | 深入理解产品设计理念，更好地使用工具 | 2-3小时 |

<!-- README_INDEX_START -->
## 📄 文档索引

### 根目录文件

| 文档 | 说明 | 标签 |
|------|------|------|
| [README.md](README.md) | 本索引文件，文档导航入口 | 索引 |
| [00-overview.md](00-overview.md) | 教程简介、阅读指南 | 入门 |
| [glossary.md](glossary.md) | 术语表（DeepTutor术语38个+七概念术语7个） | 参考 |

### 01-七概念理论

| 文档 | 说明 | 标签 |
|------|------|------|
| [01-seven-concepts-theory/README.md](01-seven-concepts-theory/README.md) | 七概念理论模块索引 | 理论 |
| [01-r-retrospective.md](01-seven-concepts-theory/01-r-retrospective.md) | R 复盘 | 理论 |
| [02-i-insight.md](01-seven-concepts-theory/02-i-insight.md) | I 洞察 | 理论 |
| [03-e-extraction.md](01-seven-concepts-theory/03-e-extraction.md) | E 萃取 | 理论 |
| [04-c-atomic-commit.md](01-seven-concepts-theory/04-c-atomic-commit.md) | C 原子提交 | 理论 |
| [05-a-atomization.md](01-seven-concepts-theory/05-a-atomization.md) | A 原子化 | 理论 |
| [06-f-first-principles.md](01-seven-concepts-theory/06-f-first-principles.md) | F 第一性原理 | 理论 |
| [07-v-adversarial-review.md](01-seven-concepts-theory/07-v-adversarial-review.md) | V 对抗性审查 | 理论 |

### 02-DeepTutor案例

| 文档 | 说明 | 标签 |
|------|------|------|
| [02-deeptutor-case/README.md](02-deeptutor-case/README.md) | DeepTutor案例模块索引 | 案例 |
| [00-deeptutor-overview.md](02-deeptutor-case/00-deeptutor-overview.md) | 项目简介 | 案例 |
| [01-core-architecture.md](02-deeptutor-case/01-core-architecture.md) | 核心架构 | 案例 |
| [02-modules/README.md](02-deeptutor-case/02-modules/README.md) | 9大模块索引 | 案例 |
| [02-modules/01-chat-partners-myagents.md](02-deeptutor-case/02-modules/01-chat-partners-myagents.md) | Chat+Partners+My Agents | 案例 |
| [02-modules/02-cowriter-book.md](02-deeptutor-case/02-modules/02-cowriter-book.md) | Co-Writer+Book | 案例 |
| [02-modules/03-knowledge-learning.md](02-deeptutor-case/02-modules/03-knowledge-learning.md) | Knowledge Center+Learning Space | 案例 |
| [02-modules/04-memory-settings.md](02-deeptutor-case/02-modules/04-memory-settings.md) | Memory+Settings | 案例 |
| [03-quick-start.md](02-deeptutor-case/03-quick-start.md) | 快速开始 | 实践 |
| [04-pros-cons.md](02-deeptutor-case/04-pros-cons.md) | 优缺点评价 | 分析 |

### 03-融合分析

| 文档 | 说明 | 标签 |
|------|------|------|
| [03-analysis/README.md](03-analysis/README.md) | 融合分析模块索引 | 分析 |
| [00-framework-mapping.md](03-analysis/00-framework-mapping.md) | 映射总览表 | 分析 |
| [01-r-in-deeptutor.md](03-analysis/01-r-in-deeptutor.md) | R在DeepTutor中的体现 | 分析 |
| [02-i-in-deeptutor.md](03-analysis/02-i-in-deeptutor.md) | I在DeepTutor中的体现 | 分析 |
| [03-e-in-deeptutor.md](03-analysis/03-e-in-deeptutor.md) | E在DeepTutor中的体现 | 分析 |
| [04-c-in-deeptutor.md](03-analysis/04-c-in-deeptutor.md) | C在DeepTutor中的体现 | 分析 |
| [05-a-in-deeptutor.md](03-analysis/05-a-in-deeptutor.md) | A在DeepTutor中的体现 | 分析 |
| [06-f-in-deeptutor.md](03-analysis/06-f-in-deeptutor.md) | F在DeepTutor中的体现 | 分析 |
| [07-v-in-deeptutor.md](03-analysis/07-v-in-deeptutor.md) | V在DeepTutor中的体现 | 分析 |
| [08-combined-workflows.md](03-analysis/08-combined-workflows.md) | 组合工作流分析 | 分析 |

### 04-学习路径与练习

| 文档 | 说明 | 标签 |
|------|------|------|
| [04-learning-path/README.md](04-learning-path/README.md) | 学习路径模块索引 | 实践 |
| [00-reading-guide.md](04-learning-path/00-reading-guide.md) | 阅读路径 | 实践 |
| [01-practice-exercises.md](04-learning-path/01-practice-exercises.md) | 实践练习 | 实践 |
| [02-self-checklist.md](04-learning-path/02-self-checklist.md) | 自检清单 | 工具 |
| [03-further-reading.md](04-learning-path/03-further-reading.md) | 延伸阅读 | 参考 |

<!-- README_INDEX_END -->

## 🗺️ 建议阅读路径

### 🌱 路径一：快速了解（适合新手）
```
README.md（本文件）
→ 00-overview.md（建立全局认知）
→ 02-deeptutor-case/00-deeptutor-overview.md（了解DeepTutor是什么）
→ 03-analysis/00-framework-mapping.md（看映射总览表建立直觉）
→ glossary.md（查阅术语）
```

### 👨‍💻 路径二：系统学习（适合开发者/产品经理）
```
README.md → 00-overview.md
→ 01-seven-concepts-theory/（重温七概念理论，按需选读）
→ 02-deeptutor-case/（完整阅读DeepTutor架构与模块）
→ 03-analysis/（逐个概念深入分析映射关系）
→ 04-learning-path/01-practice-exercises.md（动手练习）
→ 04-learning-path/02-self-checklist.md（自检）
```

### 🧠 路径三：方法论研究者（适合深度实践者）
```
完整通读 + 03-analysis/08-combined-workflows.md（组合工作流）
→ 结合自己的项目做04-learning-path/01-practice-exercises.md中的练习
→ 参考04-learning-path/03-further-reading.md拓展阅读
→ 尝试用七概念分析其他Agent产品
```

---

## 🔗 相关资源

- [🏠 返回上级：Agent工程方法论](../README.md)
- [📚 知识库首页](../../../README.md)
- [🧬 七概念方法论：七概念指令集](../../../../../commands/seven-concepts.md)
- [📖 七概念Prompt工程Wiki](../seven-concepts-prompt-wiki/README.md)
- [🔄 方法论模式库](../../../../retrospective/patterns/README.md)
- [🌐 DeepTutor GitHub](https://github.com/HKUDS/DeepTutor)

---

*本教程版本：v1.0 | 创建日期：2026-07-14 | 状态：✅ 教程完成*
