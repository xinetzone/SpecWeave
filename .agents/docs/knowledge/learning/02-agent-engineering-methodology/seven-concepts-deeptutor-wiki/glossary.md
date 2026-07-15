---
id: seven-concepts-deeptutor-glossary
title: 七概念×DeepTutor实践教程 - 术语表
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [七概念, 方法论, DeepTutor, 教程, 术语表]
---

# 术语表 Glossary

---

## 第一部分：DeepTutor 术语（38个）

| 术语名 | 精确定义（来自原文） | 禁止替换的同义词 |
|--------|---------------------|------------------|
| **Agent引擎** | 六种学习模式（Chat、Quiz、Research、Solve、Visualize、Mastery Path）共享的runtime核心，Agent循环写在底层，数据在所有工作流里共享 | 智能体引擎、runtime引擎、核心引擎 |
| **Partners** | 可以在任意对话轮次里接入本地跑的Claude Code或Codex的模块，Partner有自己的Persona、私有知识库和技能，保持独立记忆 | 合作伙伴、外部Agent、插件模块 |
| **My Agents** | 创建和管理自定义Agent的独立空间，给每个Agent配不同的Persona、知识库和技能，Agent之间记忆隔离，但可以通过Chat统一调度 | 我的智能体、自定义Agent、私人Agent |
| **Co-Writer** | 支持多文档协同写作的模块，同时打开多个文档，AI根据知识库内容辅助写作，支持智能编辑、自动标注和TTS朗读，写完后可以直接保存到笔记本或导出Markdown | 协同写作、合著者、写作助手 |
| **Book Engine** | 活书编译器，能把笔记和对话内容编译成HTML书籍，左边章节导航，右边内容区，支持插入文本、标注、测验、代码、时间线、闪卡、图表、交互式动画和深度探索，每个章节都可以直接对话提问 | 书籍引擎、活书、编译器 |
| **Knowledge Center** | 管理知识库和检索引擎的模块，RAG支持LlamaIndex、PageIndex、GraphRAG、LightRAG，还能链Obsidian Vault，文档支持PDF、DOCX、XLSX、PPTX，浏览器里直接预览，索引做了版本管理，重新建不会覆盖旧的 | 知识中心、知识库管理、RAG中心 |
| **Learning Space** | 技能管理和学习路径的入口，Skills面板展示已安装的技能，可以从EduHub导入社区技能，Mastery Path是掌握练习的仪表盘 | 学习空间、技能市场、学习中心 |
| **Memory** | 三层记忆系统，比聊天记录复杂，L1存原始对话，L2做摘要，L3做综合提炼，Memory Graph能把每条结论追溯到原始证据，v1.4.6升到了顶级导航，随时可查可编辑，三层独立管理，删错记忆也不会影响其他层 | 记忆系统、记忆面板、记忆模块 |
| **Memory Graph** | 记忆图谱，能把每条结论追溯到原始证据的图结构 | 记忆图谱、溯源图、证据链 |
| **三层记忆** | L1/L2/L3三层独立管理的记忆架构：L1存原始对话，L2做摘要，L3做综合提炼 | 三级记忆、L1-L2-L3、记忆分层 |
| **L1记忆** | 三层记忆的第一层，存储原始对话记录 | 第一层记忆、原始对话层、Level 1 |
| **L2记忆** | 三层记忆的第二层，对原始对话做摘要处理 | 第二层记忆、摘要层、Level 2 |
| **L3记忆** | 三层记忆的第三层，对内容做综合提炼 | 第三层记忆、提炼层、Level 3 |
| **Mastery Path** | 掌握练习的仪表盘，每类题目必须达标才能往下走 | 掌握路径、精通路径、掌握练习仪表盘 |
| **掌握练习** | Mastery Path中的练习模式，每类题目必须达标才能往下走 | 精通练习、达标练习、掌握训练 |
| **Skills** | Learning Space中的技能面板，展示已安装的技能 | 技能、已安装技能、技能面板 |
| **EduHub** | 社区技能导入源，可以从中导入社区技能 | 教育中心、社区技能库、技能Hub |
| **RAG** | 检索增强生成（Retrieval-Augmented Generation），Knowledge Center支持多引擎RAG | 检索增强、检索生成、RAG检索 |
| **LlamaIndex** | Knowledge Center支持的四种RAG引擎之一 | Llama索引、Llama引擎 |
| **PageIndex** | Knowledge Center支持的四种RAG引擎之一 | 页面索引、Page引擎 |
| **GraphRAG** | Knowledge Center支持的四种RAG引擎之一 | 图RAG、图谱检索、Graph检索 |
| **LightRAG** | Knowledge Center支持的四种RAG引擎之一 | 轻量RAG、Light检索 |
| **Obsidian Vault** | 可以链接到Knowledge Center的知识库格式 | Obsidian库、Obsidian知识库、Vault |
| **Persona** | Agent的人格设定，Partner和自定义Agent都有自己的Persona | 人设、人格、角色设定 |
| **Mattermost** | Partners模块后来新增的对话通道 | Mattermost通道、MM通道 |
| **TTS** | 文本转语音（Text-To-Speech），Co-Writer和Settings中支持的朗读功能 | 语音朗读、文本朗读、文字转语音 |
| **Settings** | 统一配置面板，把模型、嵌入、TTS、搜索、端口配置全收进一个面板 | 设置、配置、配置面板 |
| **PyPI** | Python包索引安装方式，五分钟即可跑起来 | pip安装、PyPI安装、Python包安装 |
| **Docker** | 容器化部署方式，有官方镜像ghcr.io/hkuds/deeptutor:latest，挂个卷就能跑 | Docker部署、容器部署、Docker镜像 |
| **Ollama** | 本地模型运行工具，Settings支持的本地模型提供商之一 | Ollama本地、Ollama模型 |
| **LM Studio** | 本地模型运行工具，Settings支持的本地模型提供商之一 | LM Studio本地、LM模型 |
| **CLI** | 命令行界面（Command Line Interface），提供CLI-only模式 | 命令行、终端、命令行模式 |
| **REPL** | 交互式命令行环境（Read-Eval-Print Loop），`deeptutor chat`可进入 | 交互式环境、交互终端、REPL模式 |
| **BGE-M3** | Embedding嵌入模型，可以单独配置不跟LLM绑死 | BGE嵌入、M3模型、BGE-M3嵌入 |
| **DeepSeek** | LLM提供商之一，可以配置为聊天模型 | DeepSeek模型、深度求索 |
| **Next.js中间件** | 在容器内部转发API和WebSocket的中间件，Docker部署时只需要暴露3782端口 | Next中间件、前端中间件 |
| **前端3782端口** | DeepTutor默认前端运行端口 | 3782端口、前端端口、默认前端端口 |
| **后端8001端口** | DeepTutor默认后端运行端口 | 8001端口、后端端口、默认后端端口 |
| **HKUDS** | 香港大学数据科学实验室（Hong Kong University Data Science Laboratory）的缩写，DeepTutor项目的维护方 | 港大实验室、港大数据科学实验室、香港大学DS实验室 |
| **Chat模式** | 六种学习模式的入口，表面看是个聊天窗口，实际上六种学习模式都从这里进，切换模式时上下文保持，引擎不变 | 聊天模式、对话模式、Chat入口 |

---

## 第二部分：七概念方法论术语（7个）

| 术语名 | 一句话公理 | 4个基础要素 | 禁止替换的同义词 |
|--------|-----------|------------|------------------|
| **R 复盘** | 对已发生事件的结构化反事实推理，将时序经验转化为因果知识 | 事实采集、时序结构化、反事实推演、因果转化 | 回顾、总结、回顾总结、事后分析 |
| **I 洞察** | 跨情境可迁移规律，最小形式为「C→M→A→B」四元组 | 条件识别、机制揭示、结论生成、迁移验证 | 洞见、感悟、心得、发现 |
| **E 萃取** | 知识从隐性经验到显性模式的形式化转换，四层漏斗逐级精炼 | 显化转换、抽象提升、漏斗过滤、形式化编码 | 提炼、提取、总结、抽象 |
| **C 原子提交** | 变更集的不可分割单一职责单元，同因同果、可独立回滚、review无认知跳跃 | 职责内聚、因果闭合、独立回滚、认知平滑 | 提交、git commit、代码提交、保存更改 |
| **A 原子化** | 复杂系统向最优信息粒度的收敛，平衡认知负荷与导航成本 | 粒度寻优、单元独立、链接完整、双向收敛 | 拆分、分解、文件拆分、文档拆分 |
| **F 第一性原理** | 从不可证伪公理出发，自下而上重构方案的思维方式 | 假设剥离、要素拆解、公理自洽、重构推导 | 本质思考、底层逻辑、根本原理、元思考 |
| **V 对抗性审查** | 主动寻找证伪证据的认知防御机制，构造反例暴露确认偏误 | 证伪导向、多角攻击、偏差防御、审计可溯 | 审查、评审、代码审查、安全审查 |

---

**统计**：DeepTutor术语 38 个，七概念术语 7 个，总计 45 个术语。
