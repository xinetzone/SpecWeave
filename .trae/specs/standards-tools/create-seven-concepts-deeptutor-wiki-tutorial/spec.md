---
version: 1.0
id: create-seven-concepts-deeptutor-wiki-tutorial
title: 七概念理论与DeepTutor实践案例Wiki教程
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
source_type: "wechat-article"
theme: standards-tools
---

# 七概念理论与DeepTutor实践案例Wiki教程 - Product Requirement Document

## Overview

* **Summary**: 创建一份系统性的Wiki教程，整合SpecWeave项目的"七概念"（R-I-E-C-A-F-V）方法论理论框架与微信公众号文章介绍的DeepTutor（香港大学开源AI学习工作空间）实践案例。教程将采用"理论+案例深度解读"的双轨结构，通过对DeepTutor架构设计、功能模块、工程实践的七概念视角分析，帮助读者在理解七概念理论的同时，掌握其在真实开源项目分析与个人知识管理中的应用方法。

* **Purpose**: 解决七概念理论抽象难懂、缺乏实战案例的问题，提供一份既有理论高度又有实践指导价值的学习资料。通过DeepTutor这一优质开源项目作为剖析对象，让读者能够：(1)系统学习七概念方法论体系；(2)掌握用七概念分析真实系统的方法；(3)获得可迁移的知识管理与AI协作能力。

* **Target Users**:

  * SpecWeave项目新贡献者（学习方法论）

  * AI智能体开发者（理解Agent协作框架）

  * 知识管理爱好者（构建个人学习体系）

  * 开源项目分析者（深度解读优秀项目架构）

## Goals

* 系统阐述七概念（R-复盘、I-洞察、E-萃取、C-原子提交、A-原子化、F-第一性原理、V-对抗性审查）的核心理论

* 准确还原DeepTutor项目的功能特性、架构设计、使用方式

* 用七概念框架对DeepTutor进行深度案例分析，建立理论与实践的桥梁

* 提供可操作的学习路径与实践练习，帮助读者掌握七概念应用方法

* 形成完整、可导航、可扩展的Wiki教程文档体系

* 遵循SVA模式（Source-Verify-Assemble）确保外部内容事实准确性

* 防御术语漂移，关键术语与原文保持一致

## Non-Goals (Out of Scope)

* DeepTutor项目源码的完整复刻或二次开发

* 七概念理论的原创性扩展（仅基于现有文档进行教学化表达）

* DeepTutor的部署运维指南（仅引用官方快速开始内容）

* 其他AI学习工具（如ChatGPT、Claude等）的对比评测

* 视频教程、交互式课件等多媒体内容（纯Markdown文档）

* 付费内容或商业培训材料制作

## Background & Context

* **七概念方法论体系**：SpecWeave项目经过18天1258次提交实战验证的项目管理与知识沉淀方法论，包含复盘(R)、洞察(I)、萃取(E)、原子提交(C)、原子化(A)、第一性原理(F)、对抗性审查(V)七个核心概念，形成从感知到认知、验证、执行、沉淀的完整闭环。现有文档包括定位模型、决策树、核心工作流、交互规范、质量标准等，但缺乏结合真实项目案例的系统性教程。

* **DeepTutor项目**：香港大学数据科学实验室开源的AI学习工作空间（GitHub 25k+ Stars），将Chat、Quiz、Research、Solve、Visualize、Mastery Path六种学习模式整合在统一Agent引擎中，支持本地模型部署，具有Partners（外部Agent接入）、My Agents（自定义Agent）、Co-Writer（协同写作）、Book（活书编译器）、Knowledge Center（多引擎RAG）、Learning Space（技能市场）、Memory（三层记忆）等模块，是优秀的Agent原生应用案例。

* **内容来源**：微信公众号"极客之家"发布的DeepTutor介绍文章，包含9大功能模块详解、快速开始指南、优缺点评价。

* **方法论文档基础**：现有七概念文档位于`docs/retrospective/patterns/methodology-patterns/governance-strategy/`，包括索引、速查手册、定位模型、决策树、核心工作流、交互规范、质量标准、对抗审查报告、实战演练材料等。

## Functional Requirements

* **FR-1**: 教程必须包含七概念核心理论的系统性阐述，每个概念需有定义、公理、要素、层级归属、应用场景

* **FR-2**: 教程必须准确反映DeepTutor文章中的所有功能模块信息（Chat、Partners、My Agents、Co-Writer、Book、Knowledge Center、Learning Space、Memory、Settings）

* **FR-3**: 教程必须包含DeepTutor的快速开始指南（PyPI安装、Docker部署、CLI模式）

* **FR-4**: 每个七概念必须配有DeepTutor中的对应实践案例分析（理论→案例映射）

* **FR-5**: 教程必须包含七概念在DeepTutor中的组合应用分析（如R→I→E知识沉淀链路、A→V→C原子化验证等）

* **FR-6**: 教程必须提供学习路径指南（入门→进阶→实战）

* **FR-7**: 教程必须包含实践练习环节（参考现有exercises材料设计）

* **FR-8**: 所有引用DeepTutor原文的内容必须标注来源位置，遵循CLN（Citation-Line-Number）规则

* **FR-9**: 教程采用原子化文档结构，每个主题独立文件，通过README导航

* **FR-10**: 文档必须遵循项目Markdown规范（相对路径引用、YAML frontmatter、无file:///绝对路径）

* **FR-11**: 必须执行独立事实核查V（未参与组装的子代理逐条比对引文与原文）

* **FR-12**: 必须建立关键术语表（glossary），防御术语漂移

## Non-Functional Requirements

* **NFR-1**: 事实准确性：引用DeepTutor原文的内容准确率100%，通过独立V核查

* **NFR-2**: 术语一致性：关键术语使用与原文一致，近义词替换率0%

* **NFR-3**: 导航完整性：原子化文档间链接100%有效，无断链

* **NFR-4**: 可读性：理论部分有案例辅助理解，案例部分有理论框架支撑，避免纯理论或纯描述

* **NFR-5**: 可扩展性：文档结构支持未来新增案例或概念扩展

* **NFR-6**: 单文件粒度：遵循原子化原则，单文件不超过500行

* **NFR-7**: 完成时限：遵循标准Spec Mode流程，规划审批后执行

## Constraints

* **Technical**:

  * 使用Markdown格式（遵循项目myst-parser偏好）

  * YAML frontmatter（不使用TOML）

  * 相对路径交叉引用，禁止`file:///`绝对路径

  * Mermaid图表用于可视化（如适用）

* **Business**:

  * 最终产出物存放在`docs/knowledge/`或`docs/`下合适目录（待确认具体子目录）

  * 需通过项目CI检查（链接检查等）

* **Dependencies**:

  * 现有七概念方法论文档（作为理论来源）

  * DeepTutor微信公众号文章内容（作为案例来源）

  * 项目docgen工具用于索引更新

  * check-links.py用于链接验证

## Assumptions

* DeepTutor文章内容可公开引用，属于公开发布的技术介绍

* 七概念现有文档足够支撑教程编写，无需新增理论内容

* 读者具备基本的AI/LLM概念，无需解释基础术语

* docs/knowledge/是合适的最终存放目录（如不合适可调整）

* 不需要获取DeepTutor源码进行深度分析，基于文章内容即可完成案例解读

* 允许引用文章中的图片URL（微信公众号图片链接）

## Acceptance Criteria

### AC-1: 七概念理论完整准确

* **Given**: 教程理论章节完成

* **When**: 读者阅读七概念核心理论部分

* **Then**: 七个概念（R/I/E/C/A/F/V）均有清晰定义、公理、4个基础要素、层级归属说明，且与现有七概念文档内容一致

* **Verification**: `programmatic` + `human-judgment`

* **Notes**: 通过grep比对关键术语、交叉引用现有方法论文档验证一致性

### AC-2: DeepTutor内容事实准确

* **Given**: 教程案例章节完成

* **When**: 独立核查子代理比对教程引文与原文

* **Then**: (a)所有>块引用均可在原文定位；(b)功能描述（9大模块）与原文一致；(c)安装命令、配置参数准确无误；(d)无张冠李戴的案例/数据归属；(e)无虚构概念/框架/数字

* **Verification**: `programmatic`

* **Notes**: 使用SVA模式的V阶段，委派新子代理逐条核查

### AC-3: 理论与案例深度融合

* **Given**: 教程完整完成

* **When**: 审阅者检查每个概念章节

* **Then**: 每个七概念至少有1个DeepTutor中的对应实践案例，案例分析不是简单贴原文，而是用七概念框架进行解读（指出DeepTutor哪里体现了该概念、为什么这么设计、带来什么好处）

* **Verification**: `human-judgment`

* **Notes**: 评审检查是否有"理论是理论、案例是案例"的两张皮问题

### AC-4: 原子化文档结构合理

* **Given**: 所有教程文档编写完成

* **When**: 检查文档结构

* **Then**: (a)每个主题独立文件；(b)单文件≤500行；(c)有README.md作为导航入口；(d)文件间链接100%有效（通过check-links.py验证）

* **Verification**: `programmatic`

* **Notes**: 遵循项目原子化规范

### AC-5: 术语一致性保障

* **Given**: 教程完成且建立术语表

* **When**: 检查术语使用

* **Then**: (a)关键术语（如Agent引擎、Partners、三层记忆、Mastery Path等）与原文一致；(b)无近义词替换导致的概念外延改变；(c)术语表glossary完整列出所有关键术语

* **Verification**: `programmatic`

* **Notes**: 防御术语漂移问题

### AC-6: 学习路径清晰可执行

* **Given**: 教程导航与练习章节完成

* **When**: 新读者按教程学习

* **Then**: (a)有明确的入门→进阶→实战学习路径；(b)包含至少1个可动手的实践练习；(c)有质量检查清单用于自学验收

* **Verification**: `human-judgment`

### AC-7: 文档规范合规

* **Given**: 教程文档全部完成

* **When**: 运行项目规范检查

* **Then**: (a)所有Markdown文件有完整YAML frontmatter（id/title/source等）；(b)无`file:///`绝对路径引用；(c)Changelog章节用`<!-- changelog -->`标记包裹；(d)通过链接有效性检查

* **Verification**: `programmatic`

### AC-8: 索引与导航更新

* **Given**: 教程文件全部就位

* **When**: 检查项目索引

* **Then**: (a)教程目录在docs/下正确位置；(b)如需要，更新相关README.md导航表指向新教程

* **Verification**: `human-judgment`

## Open Questions

* [ ] 最终教程文档存放在docs/下哪个具体子目录？（docs/knowledge/ 还是新建 docs/tutorials/ 或其他？）

* [ ] 教程中是否需要包含Mermaid图表（如七概念五层模型图、DeepTutor架构映射图、学习路径图等）？

* [ ] 实践练习的设计深度：参考现有exercises的90分钟-3小时模块化演练，还是设计更轻量化的练习？

* [ ] 是否需要为教程配置独立的README导航看板，还是接入现有docs/knowledge/的索引体系？

