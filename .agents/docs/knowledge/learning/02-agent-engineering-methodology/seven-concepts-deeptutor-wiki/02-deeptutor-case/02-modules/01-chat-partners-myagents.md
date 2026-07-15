---
id: seven-concepts-deeptutor-02-modules-chat
title: Chat + Partners + My Agents 模块
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 模块, Chat, Partners]
---

# Chat + Partners + My Agents 模块

---

## Chat：六种学习模式的统一入口

Chat表面上是一个聊天窗口，但它实际上是六种学习模式（Chat、Quiz、Research、Solve、Visualize、Mastery Path）的统一入口。

> Chat表面看是个聊天窗口，实际上六种学习模式都从这里进。切到解题模式，刚才聊过的知识点还在上下文里，切到测验模式，系统自动把讨论内容收进题库，换目标，引擎是不会变的。
>
> ——§2.1.1 Chat本质

Chat的关键特性是**模式切换时上下文保持**：
- 切到Solve（解题）模式：刚才聊过的知识点还在上下文里
- 切到Quiz（测验）模式：系统自动把讨论内容收进题库
- 切换的是学习目标，底层Agent引擎不变

这意味着用户可以在一个连续的对话流中自由切换学习模式，不需要开新窗口或重新描述问题。

---

## Partners：接入本地Claude Code和Codex

Partners模块允许在任意对话轮次里接入本地运行的Claude Code或Codex。

### Partner的独立性

> Partners可以在任意对话轮次里接入本地跑的Claude Code或Codex，Partner有自己的Persona、私有知识库和技能，保持独立记忆。
>
> ——§2.2.0 Partners核心能力

每个Partner拥有独立的配置：
- **Persona**：独立的人格设定
- **私有知识库**：自己专属的知识库
- **技能**：独立的技能配置
- **独立记忆**：记忆与主对话和其他Partner隔离

### 对话操作特性

> 对话支持分支、续聊、删除，带可回放的操作轨迹，后来又加了Mattermost通道。在DeepTutor里问代码问题，它调的是我本地跑的Claude Code，上下文全在，不用复制粘贴到IDE再粘回来。
>
> ——§2.2.1 对话特性

Partners对话支持以下操作：
- **分支**：可以从对话的任意节点创建分支
- **续聊**：可以回到历史节点继续对话
- **删除**：支持删除不需要的对话分支
- **可回放轨迹**：对话的操作轨迹可以回放
- **Mattermost通道**：后来新增了Mattermost对话通道接入

典型使用场景：在DeepTutor里问代码问题时，直接调用本地运行的Claude Code，上下文全在，不需要在IDE和聊天窗口之间复制粘贴。

---

## My Agents：自定义Agent的独立空间

My Agents模块用于创建和管理用户自己的自定义Agent。

### 创建自定义Agent

> My Agents 这里可以创建和管理我们自己的Agent，给每个Agent配不同的Persona、知识库和技能。
>
> ——§2.3.0 自定义Agent

用户可以在My Agents中：
- 创建多个自定义Agent
- 为每个Agent配置不同的Persona
- 为每个Agent挂载不同的知识库
- 为每个Agent配置不同的技能

### 记忆隔离与统一调度

> Agent之间记忆隔离，但可以通过Chat统一调度。
>
> ——§2.3.1 记忆隔离

自定义Agent的关键设计：
- **记忆隔离**：不同Agent之间的记忆互不干扰
- **Chat统一调度**：所有Agent可以通过Chat入口统一调用

---

## 三者关系

Chat、Partners、My Agents三者构成了DeepTutor的对话协作层：
- **Chat**是统一入口，所有模式和Agent都通过Chat调度
- **Partners**是预定义的外部能力接入点（Claude Code/Codex/Mattermost）
- **My Agents**是用户自定义的Agent管理空间，每个Agent有独立Persona/知识库/技能/记忆

---

**上一章**：[9大模块导航](README.md) ｜ **下一章**：[Co-Writer + Book Engine](02-cowriter-book.md)
