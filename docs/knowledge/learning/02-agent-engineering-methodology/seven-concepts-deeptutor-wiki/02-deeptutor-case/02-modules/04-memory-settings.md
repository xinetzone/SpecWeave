---
id: seven-concepts-deeptutor-02-modules-memory
title: Memory + Settings 模块
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 模块, Memory, Settings]
---

# Memory + Settings 模块

---

## Memory：三层记忆与Graph溯源

Memory是DeepTutor的记忆系统，比普通的聊天记录复杂得多，采用三层架构设计，并通过Memory Graph实现证据溯源。

### 三层记忆架构

> Memory比聊天记录复杂，L1存原始对话，L2做摘要，L3做综合提炼，Memory Graph能把每条结论追溯到原始证据。
>
> ——§2.8.0 三层记忆架构

Memory的三层架构分工明确：

| 层级 | 名称 | 内容 |
|------|------|------|
| **L1** | 原始对话层 | 存储完整的原始对话记录 |
| **L2** | 摘要层 | 对原始对话做摘要处理 |
| **L3** | 综合提炼层 | 对内容做综合提炼 |

### Memory Graph溯源

**Memory Graph**是记忆图谱结构，能够将每条结论追溯到原始证据。打开Memory面板时，它不仅记录了之前问过的内容，还会告诉用户某条结论是从哪段对话里摘出来的。

> 打开面板，它确实记了之前问过的内容，而且告诉我是从哪段对话里摘出来的。这比那些只会说"我记住了"的AI实在。
>
> ——§2.8.1 记忆面板特性

### 记忆面板特性

Memory面板在v1.4.6版本升到了顶级导航，具有以下特性：

- **随时可查可编辑**：不需要进入深层菜单，随时可以查看和编辑记忆
- **三层独立管理**：L1、L2、L3三层独立管理
- **删错不影响其他层**：删除某一层的错误记忆不会影响其他层的数据

> Memory面板在v1.4.6升到了顶级导航，随时可查可编辑。删错记忆也不会影响其他层，三层独立管理。
>
> ——§2.8.1 记忆面板特性

---

## Settings：统一配置面板

Settings是DeepTutor的统一配置面板，将所有配置项集中管理。

> Settings把模型、嵌入、TTS、搜索、端口配置全收进一个面板。
>
> ——§2.9.0 配置范围

### LLM提供商配置

> LLM提供商支持OpenAI、Anthropic、Google、Azure等主流接口，也支持Ollama、LM Studio、llama.cpp、VLLM等本地模型。
>
> ——§2.9.1 LLM提供商

LLM支持两大类提供商：

| 类型 | 支持的提供商 |
|------|-------------|
| **云端主流接口** | OpenAI、Anthropic、Google、Azure |
| **本地模型** | Ollama、LM Studio、llama.cpp、VLLM |

### Embedding独立配置

> Embedding可以单独配置，不跟LLM绑死。我配了DeepSeek当聊天模型，BGE-M3当嵌入模型，互不干扰。
>
> ——§2.9.2 Embedding配置

Embedding模型可以与LLM分开独立配置，两者不绑死。例如可以使用DeepSeek作为聊天模型，同时使用BGE-M3作为嵌入模型，互不干扰。

### 其他配置项

Settings面板还统一管理以下配置：
- **TTS**：文本转语音配置
- **搜索**：搜索相关配置
- **端口**：服务端口配置

### 界面配置

> 还可以自定义选择界面主题，深色/浅色，还可以选择展示的语言中文/英文。
>
> ——§2.9.3 界面配置

界面支持以下自定义选项：
- **主题**：深色主题 / 浅色主题
- **语言**：中文 / 英文切换

---

## Memory与Settings的关系

Memory和Settings构成了DeepTutor的基础配置层：
- **Memory**负责系统的"记忆"：三层记忆存储、Memory Graph溯源、记忆的查看和编辑
- **Settings**负责系统的"配置"：模型选择、嵌入配置、TTS、端口、界面主题和语言

两者都是系统正常运行的基础设施，为上层的对话协作、写作输出、知识学习模块提供底层支撑。

---

**上一章**：[Knowledge Center + Learning Space](03-knowledge-learning.md) ｜ **下一章**：[快速开始](../03-quick-start.md)
