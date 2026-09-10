---
type: Concept
title: OpenMAIC 技能系统
description: OpenMAIC 内置超过 20 个开源技能，支持跨平台导入到其他 Agent 工具
tags: [openmaic, skills, agent-interoperability, open-source]
generated:
  by: agent-agnes
  at: "2026-09-09T10:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-09T10:00:00+08:00"
status: draft
stale_after: "2027-09-09"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: "微信公众号文章《短短5个月暴涨3.3万Star》"
---

# OpenMAIC 技能系统

OpenMAIC 的技能（Skill）架构是其病毒式传播和生态扩展的核心机制。技能是模块化、可复用的能力单元，既可独立运行，也可导入到其他 Agent 工具中使用。

## 内置技能清单

OpenMAIC 内置超过 20 个技能，全部开源。文章明确提到的技能包括：

| 技能名称 | 功能描述 |
|---------|---------|
| 系列课规划 | 规划完整的课程体系结构 |
| 深度调研 | 对特定主题进行深入资料收集和分析 |
| 费曼学习法 | 通过角色扮演生成通俗易懂的讲解课件 |
| 事实核查 | 验证信息准确性 |
| 教学设计 | 设计教学流程和互动环节 |
| 大师讲授 | 模拟专家视角进行内容讲解 |
| OpenMAIC 官方 Skill | 引导式 SOP，覆盖课堂生成、本地部署和二次开发 |

## 技能的可移植性

OpenMAIC 技能的最大特色是**跨平台可移植性**——技能可以导入到其他 Agent 工具中使用：

- DeepSeek Harness
- Codex
- WorkBuddy
- 其他支持 Skill 导入的 Agent 工具

这意味着用户可以在自己熟悉和常用的 Agent 环境中直接使用 OpenMAIC 生成的课程内容，无需切换到 OpenMAIC 平台。

## 技能的设计哲学

### 开源策略

所有技能开源，允许开发者：
1. 查看技能实现逻辑
2. 修改和定制技能
3. 为自己的场景开发新技能
4. 将技能组合使用

### 官方 Skill 的价值

OpenMAIC 官方 Skill 内含引导式 SOP（标准操作流程），覆盖三个关键场景：
- **课堂生成**：从教材到完整课程的标准化流程
- **本地部署**：自托管 OpenMAIC 的操作指南
- **二次开发**：定制和扩展技能的开发指引

这一设计降低了新用户的学习成本和开发者的上手门槛。

## 对 AI 教育产品设计的启示

OpenMAIC 的技能系统体现了一个重要设计原则：**能力开源 + 接口可移植 = 网络效应**。每个使用 OpenMAIC 技能的第三方工具都在间接推广 OpenMAIC 的能力，形成自我扩散的增长飞轮。

> **事实溯源**：F-019 ~ F-021

## 相关概念

- [OpenMAIC 项目概览](/concepts/00-project-overview.md)
- [OpenMAIC 核心功能详解](/concepts/01-core-features.md)
- [AI 教育智能体的内容生产力范式](/concepts/04-paradigm-insight.md)
