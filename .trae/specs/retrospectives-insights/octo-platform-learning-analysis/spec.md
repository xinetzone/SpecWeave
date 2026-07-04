---
title: "明略科技 Octo 平台学习与 Wiki 教程文档"
source: "微信公众号文章《Octo：当 Agent 不再只活在对话框里》"
date: "2026-07-04"
tags: ["octo", "mininglamp", "private-ai", "agent-collaboration", "a2a", "matter", "taste", "orchestration", "multi-agent", "trustworthy-ai"]
---

# 明略科技 Octo 平台学习与 Wiki 教程文档 Spec

## Why

明略科技推出的 Octo 平台提出了一种在 Private AI 时代构建人机协作新范式的思路：当企业开始拥有成百上千 Agent 时，传统 IM 工具无法承载复杂长程任务、无法沉淀组织判断、无法精细控制协作拓扑。系统学习该文章有助于沉淀"多 Agent 协作基础设施"的设计方法论，为项目内多 Agent 协作体系（如 SpecWeave、flexloop 等）提供可借鉴的产品形态与协作模式参考。

## What Changes

- 新增一份结构化的 Wiki 教程文档，系统整理 Octo 平台的核心概念、产品形态、协作模式与技术细节
- 文档将包含目录导航系统，便于不同技术水平读者跳转阅读
- 整理 Octo 提出的 O.C.T.O. 四维度框架（Open/Context/Taste/Orchestration）
- 详解六种协作模式（Solo/Roundtable/Critic/Pipeline/Split/Swarm）及其信息拓扑
- 解析 Matter（事项）作为复杂任务承载单元的设计要点
- 阐释 Taste（品味）的实战沉淀机制
- 介绍产品四层结构（结构层/入口层/环境接入层/行为约束层）
- 说明 Private AI 与 Trustworthy AI 的产品哲学
- 更新知识库索引 `docs/knowledge/README.md`，新增本教程入口

## Impact

- **Affected specs**: 无直接影响其他 spec 文档，本任务为独立的知识沉淀工作
- **Affected code**: 无代码改动，仅产出 Markdown 文档
  - 新增：`docs/knowledge/learning/octo-platform-wiki.md`（主教程文档）
  - 修改：`docs/knowledge/README.md`（知识库索引新增条目）
- **Affected knowledge**: 丰富项目对"多 Agent 协作基础设施"设计模式的知识储备

## ADDED Requirements

### Requirement: Wiki 教程文档创建

系统 SHALL 在 `docs/knowledge/learning/` 目录下创建一份名为 `octo-platform-wiki.md` 的 Markdown 教程文档，系统整理微信公众号文章中关于 Octo 平台的全部核心内容。

#### Scenario: 文档基础信息完整

- **WHEN** 用户打开 `octo-platform-wiki.md`
- **THEN** 文档顶部包含 YAML frontmatter，字段包括 title、source、date、tags
- **AND** frontmatter 字段格式符合项目 MDI v1.0 规范（`---` 包裹，`key: "value"` 语法）

#### Scenario: 目录导航系统可用

- **WHEN** 用户查看文档顶部
- **THEN** 文档包含完整的目录导航，列出所有章节
- **AND** 每个目录项为可点击的 Markdown 锚点链接，可跳转到对应章节

#### Scenario: 原文与项目链接可访问

- **WHEN** 用户查看文档开头
- **THEN** 文档包含原文微信公众号链接
- **AND** 文档包含 GitHub 开源组织链接（https://github.com/Mininglamp-OSS）

### Requirement: 项目背景与定位章节

系统 SHALL 编写"项目背景与定位"章节，介绍 Octo 平台诞生的行业背景与核心定位。

#### Scenario: 行业背景阐述清晰

- **WHEN** 用户阅读背景章节
- **THEN** 用户能理解 Agent 等数字劳动力爆发的趋势
- **AND** 用户能理解明略科技将 Octo 打造为 Private AI 时代组织基础设施的定位

#### Scenario: 核心问题阐述清晰

- **WHEN** 用户阅读背景章节
- **THEN** 用户能说明传统 IM 工具在多 Agent 协作中的局限（信息淹没、难以追溯、缺乏协作拓扑控制）
- **AND** 用户能说明 Octo 想解决的三个层次问题：连接、干活、沉淀

### Requirement: O.C.T.O. 四维度框架章节

系统 SHALL 编写"O.C.T.O. 四维度框架"章节，详解 Octo 名字背后的四个核心维度。

#### Scenario: 四维度定义清晰

- **WHEN** 用户阅读四维度章节
- **THEN** 用户能解释 O（Open，开放生态）、C（Context，共享上下文）、T（Taste，偏好进化）、O（Orchestration，多 Agent 编排）的含义
- **AND** 每个维度配有原文中的具体说明

#### Scenario: 四维度关系阐述

- **WHEN** 用户阅读四维度章节
- **THEN** 用户能说明 Matter 作为共同基座承载 Context、Taste、Orchestration 的关系
- **AND** 用户能理解没有 Matter 时各维度的散落状态

### Requirement: Matter 事项设计章节

系统 SHALL 编写"Matter（事项）"章节，详解复杂任务的承载单元设计。

#### Scenario: Matter 价值阐述

- **WHEN** 用户阅读 Matter 章节
- **THEN** 用户能说明普通 IM 信息淹没问题与 Matter 的解决方案
- **AND** 用户能说明 Matter 将任务沉淀为"决策卡"的设计

#### Scenario: Matter 结构清晰

- **WHEN** 用户阅读 Matter 章节
- **THEN** 用户能说明 Matter 包含的要素：任务缘起（Brief）、过程时间线（Timeline）、关键产出、人的反馈、验收结论
- **AND** 用户能说明 Matter 作为组织决策资产的价值

### Requirement: Taste 偏好进化章节

系统 SHALL 编写"Taste（品味）"章节，详解 Agent 通过实战反馈学习组织偏好的机制。

#### Scenario: Taste 形成机制清晰

- **WHEN** 用户阅读 Taste 章节
- **THEN** 用户能说明"偏好对齐必须在实战中完成"的设计思路
- **AND** 用户能说明人的打回、修改、确认如何成为 Bot 学习素材

#### Scenario: Taste 价值阐述

- **WHEN** 用户阅读 Taste 章节
- **THEN** 用户能说明 Taste 如何让 Agent 越用越懂团队
- **AND** 用户能说明隐性判断向可复用偏好沉淀的过程

### Requirement: 六种协作模式章节

系统 SHALL 编写"六种协作模式"章节，详解 Octo 提出的六种信息拓扑。

#### Scenario: 六种模式定义完整

- **WHEN** 用户阅读六种协作模式章节
- **THEN** 文档以表格或列表形式完整说明六种模式：
  - Solo：单干模式
  - Roundtable：圆桌讨论
  - Critic：生成-验证模式
  - Pipeline：流水线模式
  - Split：分头干模式
  - Swarm：撒网竞选模式

#### Scenario: 每种模式信息拓扑清晰

- **WHEN** 用户阅读每种模式说明
- **THEN** 每种模式包含：适用场景、信息流转方式、参与者可见性、典型用例
- **AND** 用户能区分"该互见时互见，该互盲时互盲"的隔离设计

#### Scenario: 与传统群聊对比

- **WHEN** 用户阅读六种协作模式章节
- **THEN** 用户能说明 Octo 协作模式相比飞书/Slack 群聊的差异
- **AND** 用户能说明群聊擅长"都看见"但难以做到精细隔离的局限

### Requirement: 产品四层结构章节

系统 SHALL 编写"产品四层结构"章节，解析 Octo 的产品形态。

#### Scenario: 四层结构清晰

- **WHEN** 用户阅读产品四层结构章节
- **THEN** 用户能说明四层结构：
  - 结构层：Space/Category/Channel/Thread
  - 入口层：私聊、语音输入
  - 环境接入层：浏览器插件（Cmd+K）
  - 行为约束层：GROUP.md

#### Scenario: 各层设计要点阐述

- **WHEN** 用户阅读每层说明
- **THEN** 每层包含设计目的、核心机制和实际价值
- **AND** 语音输入章节说明其不仅是 STT，还是持续进化的系统

#### Scenario: GROUP.md 机制清晰

- **WHEN** 用户阅读 GROUP.md 部分
- **THEN** 用户能说明 GROUP.md 作为 Bot 行为准则的作用
- **AND** 用户能说明"进什么庙，念什么经"的切换机制

### Requirement: Private AI 与 Trustworthy AI 章节章节

系统 SHALL 编写"Private AI 与 Trustworthy AI"章节，解析 Octo 的产品哲学。

#### Scenario: Private AI 理念清晰

- **WHEN** 用户阅读 Private AI 章节
- **THEN** 用户能说明 Private AI 不仅是本地化部署，更是数据主权、知识主权、协作主权的回归
- **AND** 用户能说明 Octo 通过 CLI 接入端侧模型与本地环境的实现方式

#### Scenario: Trustworthy AI 理念清晰

- **WHEN** 用户阅读 Trustworthy AI 章节
- **THEN** 用户能说明 Trustworthy AI 的三大特征：开源、白盒、可审计
- **AND** 用户能说明"能力可以流动，但数据不外流"的设计原则

### Requirement: 关键术语表

系统 SHALL 整理一份关键术语表，汇总文章中的专业术语及其定义。

#### Scenario: 术语表完整

- **WHEN** 用户查阅术语表
- **THEN** 术语表至少包含：Octo、Matter、Taste、Runtime Agent、Bot、A2A、GROUP.md、Private AI、Trustworthy AI、Open/Closed Agent 等术语
- **AND** 每个术语配有简洁明确的定义

### Requirement: FAQ 常见问题章节

系统 SHALL 编写 FAQ 章节，整理关于 Octo 平台的常见问题与解答。

#### Scenario: FAQ 实用性

- **WHEN** 用户遇到问题查阅 FAQ
- **THEN** FAQ 至少包含 6 个常见问题及解答
- **AND** 问题覆盖：适用场景、与现有 IM 工具差异、私有化部署、Agent 接入方式、协作模式选择、Taste 沉淀机制等

### Requirement: 相关资源链接章节

系统 SHALL 编写相关资源链接章节，汇总与 Octo 平台相关的资源。

#### Scenario: 资源链接有效

- **WHEN** 用户查看资源链接章节
- **THEN** 章节包含 GitHub 开源组织地址（https://github.com/Mininglamp-OSS）
- **AND** 章节包含原文微信公众号链接
- **AND** 章节包含相关的明略科技可信 AI 方向资源（如适用）

### Requirement: 知识库索引更新

系统 SHALL 更新 `docs/knowledge/README.md`，在 learning 分类中新增本教程条目。

#### Scenario: 索引条目格式一致

- **WHEN** 查看 `docs/knowledge/README.md` 的 learning 分类表格
- **THEN** 表格新增 octo-platform-wiki 条目
- **AND** 条目包含：标题、摘要、日期（2026-07-04）、标签
- **AND** 条目格式与现有 learning 分类条目保持一致

## MODIFIED Requirements

### Requirement: 知识库索引分类

知识库索引文件 `docs/knowledge/README.md` 的 learning 分类表格需新增 Octo 平台教程条目，保持表格结构与其他条目一致。

## REMOVED Requirements

无移除需求。

## Open Questions

- [ ] 是否需要创建原子化的子目录结构来组织 Wiki 文档（参考 mopmonk-security-agent-wiki 的原子化模式）？
- [ ] 是否需要补充明略科技其他产品（如 OpenClaw）的关联分析？
- [ ] 是否需要将 Octo 的六种协作模式与项目内 SpecWeave/flexloop 的协作场景做对比分析？
