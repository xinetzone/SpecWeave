---
id: seven-concepts-deeptutor-02-modules-cowriter
title: Co-Writer + Book Engine 模块
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 模块, Co-Writer, Book]
---

# Co-Writer + Book Engine 模块

---

## Co-Writer：多文档协同写作

Co-Writer是DeepTutor的多文档协同写作模块，支持同时打开多个文档，AI根据知识库内容辅助写作。

> Co-Writer支持多文档协同写作，同时打开多个文档，AI根据知识库内容辅助写作。支持智能编辑、自动标注和TTS朗读，写完后可以直接保存到笔记本，或者导出Markdown。
>
> ——§2.4.0 协同写作

### 核心功能

Co-Writer提供以下写作辅助能力：

- **多文档协同**：可以同时打开多个文档进行编辑
- **AI辅助写作**：AI根据挂载的知识库内容辅助写作，不是凭空生成
- **智能编辑**：AI辅助进行文本编辑
- **自动标注**：自动为内容添加标注
- **TTS朗读**：支持文本转语音朗读功能

### 输出方式

写作完成后，内容可以通过两种方式保存和导出：
1. 直接保存到笔记本
2. 导出为Markdown格式

---

## Book Engine：活书编译器

Book Engine（活书编译器）是DeepTutor的书籍生成模块，能够将笔记和对话内容编译成HTML格式的交互式书籍。

> Book Engine能把笔记和对话内容编译成HTML书籍。左边章节导航，右边内容区，支持插入文本、标注、测验、代码、时间线、闪卡、图表、交互式动画和深度探索。
>
> ——§2.5.0 Book Engine

### 书籍结构

Book Engine生成的HTML书籍采用双栏布局：
- **左侧**：章节导航
- **右侧**：内容区

### 支持的内容类型

Book Engine支持在书籍中插入多种富内容类型：

| 内容类型 | 说明 |
|----------|------|
| 文本 | 普通文本内容 |
| 标注 | 注释和标注 |
| 测验 | 交互式测验 |
| 代码 | 代码块 |
| 时间线 | 时间线组件 |
| 闪卡 | 闪卡（用于记忆复习） |
| 图表 | 数据图表 |
| 交互式动画 | 交互动画组件 |
| 深度探索 | 深度探索模块 |

### 章节对话功能

> 每个章节都可以直接对话提问。
>
> ——§2.5.1 章节对话

Book Engine生成的书籍不仅是静态内容，每个章节都支持直接对话提问，将阅读和互动问答融为一体。

---

## Co-Writer与Book Engine的关系

Co-Writer和Book Engine构成了DeepTutor的写作输出链路：
- **Co-Writer**负责内容的创作阶段：多文档编辑、AI辅助写作、智能编辑
- **Book Engine**负责内容的编译输出阶段：将笔记和对话编译成交互式HTML书籍

两者衔接使得学习内容可以从零散的笔记和对话，最终整理编译为结构化、可交互的"活书"。

---

**上一章**：[Chat + Partners + My Agents](01-chat-partners-myagents.md) ｜ **下一章**：[Knowledge Center + Learning Space](03-knowledge-learning.md)
