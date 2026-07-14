---
id: seven-concepts-deeptutor-02-architecture
title: DeepTutor核心架构
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 架构, 案例]
---

# DeepTutor核心架构

---

## Agent引擎设计

DeepTutor最核心的架构决策是**将Agent循环写在底层**。Chat、Quiz、Research、Solve、Visualize、Mastery Path六种学习模式不是各自独立的对话系统，而是共享同一个runtime的Agent引擎。

> Agent循环写在底层，Chat、Quiz、Research、Solve、Visualize、Mastery Path六种模式共享一个runtime，支持本地模型和Docker一键部署。
>
> ——§0.1 导语核心事实

这种"一个引擎、多种模式"的设计意味着：

- Agent循环是底层runtime的核心机制，不是上层应用逻辑
- 六种模式只是同一个引擎的不同"工作模式"切换，而非启动不同的对话系统
- 数据在所有工作流里共享，模式切换时上下文不需要迁移

> DeepTutor是一个开源的AI学习工作空间，辅导、解题、测验、研究、可视化、掌握练习六种学习模式塞进同一个Agent引擎，数据在所有工作流里共享。
>
> ——§1.1 核心定义

---

## 导航栏九个模块概览

打开DeepTutor，左边导航栏挂着九个模块：

| 序号 | 模块 | 分组 | 功能概述 |
|------|------|------|----------|
| 1 | **Home** | 首页 | — |
| 2 | **Partners** | 对话协作 | 接入本地Claude Code/Codex，Partner有独立Persona/知识库/技能/记忆 |
| 3 | **My Agents** | 对话协作 | 创建管理自定义Agent，配不同Persona/知识库/技能，记忆隔离 |
| 4 | **Co-Writer** | 写作输出 | 多文档协同写作，AI辅助写作，支持智能编辑/标注/TTS |
| 5 | **Book** | 写作输出 | Book Engine活书编译器，将笔记/对话编译成HTML书籍 |
| 6 | **Learning Space** | 知识学习 | 技能管理和学习路径入口，含Skills面板和Mastery Path |
| 7 | **Memory** | 基础配置 | 三层记忆系统和Memory Graph，可查可编辑 |
| 8 | **Knowledge Center** | 知识学习 | 知识库管理和多引擎RAG检索 |
| 9 | **Settings** | 基础配置 | 统一配置面板（模型/嵌入/TTS/搜索/端口） |

> 打开DeepTutor，左边导航栏挂着九个模块：Home、Partners、My Agents、Co-Writer、Book、Learning Space、Memory、Knowledge Center、Settings。
>
> ——§2.1.0 导航模块

九个模块按功能可分为四组：
- **对话协作组**：Partners、My Agents（Chat为统一入口，非独立导航模块）
- **写作输出组**：Co-Writer、Book（Book Engine）
- **知识学习组**：Knowledge Center、Learning Space
- **基础配置组**：Memory、Settings

各模块的详细说明见[功能模块详解](02-modules/README.md)。

---

## 模式切换不换引擎的设计

DeepTutor的六种学习模式虽然功能目标不同，但切换模式时**引擎不换**，上下文保持。这是其架构的关键设计：

> Chat表面看是个聊天窗口，实际上六种学习模式都从这里进。切到解题模式，刚才聊过的知识点还在上下文里，切到测验模式，系统自动把讨论内容收进题库，换目标，引擎是不会变的。
>
> ——§2.1.1 Chat本质

具体表现为：
- 从Chat模式切到Solve（解题）模式：之前聊过的知识点仍保留在上下文中
- 从Chat模式切到Quiz（测验）模式：系统自动把讨论内容收进题库，切换目标但引擎不变
- 模式切换对用户而言是"换个目标继续"，而不是"开个新对话重来"

这种设计的优势在于用户学习过程不会因为切换模式而中断，数据在工作流之间自然流动。

---

## 部署支持

DeepTutor在部署层面支持两种方式：

1. **本地模型支持**：支持Ollama、LM Studio、llama.cpp、VLLM等本地模型运行工具
2. **Docker一键部署**：提供官方Docker镜像，挂个卷就能跑，配置和知识库不会丢失

> LLM提供商支持OpenAI、Anthropic、Google、Azure等主流接口，也支持Ollama、LM Studio、llama.cpp、VLLM等本地模型。
>
> ——§2.9.1 LLM提供商

> Docker也有官方镜像，ghcr.io/hkuds/deeptutor:latest，挂个卷就能跑，配置和知识库不会丢。
>
> ——§3.1 Docker部署

具体的安装部署步骤见[快速开始](03-quick-start.md)。

---

**上一章**：[项目简介](00-deeptutor-overview.md) ｜ **下一章**：[9大模块导航](02-modules/README.md)
