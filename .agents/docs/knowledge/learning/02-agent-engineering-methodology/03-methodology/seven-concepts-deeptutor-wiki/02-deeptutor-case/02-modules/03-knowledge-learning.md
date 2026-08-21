---
id: seven-concepts-deeptutor-02-modules-knowledge
title: Knowledge Center + Learning Space 模块
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [DeepTutor, 模块, Knowledge, Learning]
---

# Knowledge Center + Learning Space 模块

---

## Knowledge Center：多引擎RAG与知识库版本管理

Knowledge Center是DeepTutor的知识库管理和检索引擎模块，负责管理所有知识库和RAG检索能力。

> Knowledge Center管理知识库和检索引擎，RAG支持LlamaIndex、PageIndex、GraphRAG、LightRAG，还能链Obsidian Vault。文档支持PDF、DOCX、XLSX、PPTX，浏览器里直接预览，索引做了版本管理，重新建不会覆盖旧的。
>
> ——§2.6.0 多引擎RAG

### 多引擎RAG支持

Knowledge Center的RAG检索支持四种引擎，用户可以根据需要选择：

| RAG引擎 | 说明 |
|---------|------|
| **LlamaIndex** | 四种RAG引擎之一 |
| **PageIndex** | 四种RAG引擎之一 |
| **GraphRAG** | 四种RAG引擎之一（基于图谱的检索） |
| **LightRAG** | 四种RAG引擎之一（轻量版RAG） |

### 外部知识库链接

Knowledge Center支持链接外部知识库格式：
- **Obsidian Vault**：可以直接链接Obsidian知识库

### 文档格式支持

支持多种文档格式上传和管理：
- **PDF**
- **DOCX**
- **XLSX**
- **PPTX**

所有文档支持在浏览器里直接预览，无需下载。

### 索引版本管理

Knowledge Center的索引做了版本管理：重新建立索引时**不会覆盖旧的索引**。这意味着用户可以安全地重建索引而不用担心丢失之前的索引数据，也方便对比不同版本索引的检索效果。

---

## Learning Space：技能市场与掌握路径

Learning Space是DeepTutor的技能管理和学习路径入口模块。

> Learning Space是技能管理和学习路径的入口，Skills面板展示已安装的技能，可以从EduHub导入社区技能。Mastery Path是掌握练习的仪表盘，每类题目必须达标才能往下走。
>
> ——§2.7.0 技能与路径

### Skills面板

Skills面板用于展示和管理已安装的技能。

### EduHub社区技能导入

用户可以从**EduHub**导入社区贡献的技能，扩展DeepTutor的能力。EduHub是社区技能的导入源。

### Mastery Path（掌握练习）

Mastery Path是掌握练习的仪表盘，其核心规则是：**每类题目必须达标才能往下走**。这是一种强制掌握的学习机制——用户必须在当前类别的题目上达到达标标准，才能进入下一类题目的练习，确保学习效果不打折。

---

## Knowledge Center与Learning Space的关系

Knowledge Center和Learning Space构成了DeepTutor的知识学习层：
- **Knowledge Center**负责知识的管理和检索：多引擎RAG、文档管理、索引版本控制、Obsidian Vault链接
- **Learning Space**负责技能和学习路径：技能管理、社区技能导入、Mastery Path掌握练习

前者是"知识基础设施"，后者是"学习流程控制"，两者配合构成了DeepTutor的知识学习闭环。

---

**上一章**：[Co-Writer + Book Engine](02-cowriter-book.md) ｜ **下一章**：[Memory + Settings](04-memory-settings.md)
