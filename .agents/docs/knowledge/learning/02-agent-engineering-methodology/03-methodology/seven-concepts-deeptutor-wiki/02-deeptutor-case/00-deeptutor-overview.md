---
id: seven-concepts-deeptutor-02-overview
title: DeepTutor项目简介
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 案例, 简介]
---

# DeepTutor项目简介

---

## DeepTutor是什么

DeepTutor是一个开源的AI学习工作空间。辅导、解题、测验、研究、可视化、掌握练习六种学习模式塞进同一个Agent引擎，数据在所有工作流里共享，项目由港大数据科学实验室维护。

> DeepTutor是一个开源的AI学习工作空间，辅导、解题、测验、研究、可视化、掌握练习六种学习模式塞进同一个Agent引擎，数据在所有工作流里共享，项目由港大数据科学实验室维护。
>
> ——§1.1 核心定义

---

## 核心定位

DeepTutor的核心定位是**智能体原生的学习工作区**，提供终身个性化辅导——出题、解题、辅导学习全包了干，是一款非常具有普惠意义的AI工具。

> 这是一个智能体原生的学习工作区，提供终身个性化辅导，出题、解题、辅导学习全包了干，非常具有普惠意义的AI工具。
>
> ——§0.2 导语定位

---

## 六种学习模式

DeepTutor将六种学习模式统一塞进同一个Agent引擎：

| 模式 | 中文名称 | 说明 |
|------|----------|------|
| **Chat** | 辅导/对话 | 聊天窗口形式的辅导对话，是所有模式的统一入口 |
| **Quiz** | 测验 | 自动将讨论内容收入题库进行测验 |
| **Research** | 研究 | 基于知识库进行研究性学习 |
| **Solve** | 解题 | 切换到解题模式时，之前讨论的知识点保持在上下文中 |
| **Visualize** | 可视化 | 支持图表、交互式动画等可视化内容 |
| **Mastery Path** | 掌握练习 | 掌握练习的仪表盘，每类题目必须达标才能往下走 |

> Agent循环写在底层，Chat、Quiz、Research、Solve、Visualize、Mastery Path六种模式共享一个runtime，支持本地模型和Docker一键部署。
>
> ——§0.1 导语核心事实

六种模式共享一个runtime的关键设计在于：切换模式时**引擎不变**，上下文保持连贯，系统自动将讨论内容适配到新模式的目标上。

---

## 项目维护方

DeepTutor由**香港大学数据科学实验室（HKUDS）**维护。该项目在GitHub上获得了25k Star，开源100天左右冲到20k Star，增长速度显著。

---

## 核心特点

DeepTutor最核心的设计特点有两点：

1. **Agent循环写在底层**：Agent循环不是上层应用逻辑，而是底层runtime的核心机制。六种学习模式共用同一个Agent引擎，而非为每种模式单独实现对话逻辑。

2. **数据在所有工作流里共享**：不同学习模式之间数据是贯通的。在Chat模式下讨论的知识点，切换到Solve模式时仍然在上下文中；切换到Quiz模式时，系统自动把讨论内容收进题库，无需用户手动迁移数据。

> 我翻了代码，Agent循环写在底层，Chat、Quiz、Research、Solve、Visualize、Mastery Path六种模式共享一个runtime，支持本地模型和Docker一键部署。
>
> ——§0.1 导语核心事实

这两个特点使得DeepTutor不同于那些"在传统软件外面套一层LLM接口"的产品，而是一个从底层就围绕Agent设计的原生AI学习工具。

---

**上一章**：[案例模块导航](README.md) ｜ **下一章**：[核心架构](01-core-architecture.md)
