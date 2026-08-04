---
id: create-codewhale-wiki-tutorial
title: CodeWhale Wiki 教程生成 Spec
source: "https://codewhale.net/zh + d:\\AI\\external\\tools\\CodeWhale"
methodology: "七概念方法论·场景4：知识沉淀（R→I→E→V→C）"
created: 2026-07-06
---

# CodeWhale Wiki 教程生成 Spec

## Why

CodeWhale 是一个 MIT 开源的终端 AI 编程调度系统（39k+ Star），以"模型路由"和"嵌套宪法"为核心机制，实现模型无关的 AI 编程体验。当前项目知识库中已有 CodeWhale 相关文章分析（[analyze-wechat-article-Vykbw](../analyze-wechat-article-Vykbw/)），但缺少面向实操的 Wiki 教程。本任务基于官网（`https://codewhale.net/zh`）和本地源码（`d:\AI\external\tools\CodeWhale`），系统性学习后生成结构化 Wiki 教程，沉淀为可复用的技术知识资产。

## What Changes

- 新增 `docs/knowledge/learning/codewhale/` 目录，包含完整的 Wiki 教程页面
- Wiki 教程遵循知识库模板规范（[knowledge-base-wiki-template](../../knowledge-base-wiki-template/template/)），包含 tech/、general/、topics/ 三大模块
- 覆盖内容：项目概述、安装指南、核心概念（模型路由/嵌套宪法/三种模式）、架构设计、提供商配置、Fleet 工作流、TUI 使用指南、源码导读
- 更新知识库索引文件，注册新教程

## Impact

- Affected specs: 无（新增独立教程）
- Affected code: 无代码变更，纯文档产出
- Affected docs: `docs/knowledge/learning/codewhale/`（新增目录）

## ADDED Requirements

### Requirement: 信息采集与事实记录（R阶段）
系统 SHALL 从两个来源全面采集 CodeWhale 的客观事实信息：
- 官网 `https://codewhale.net/zh`：产品定位、功能介绍、安装方式、运行时说明
- 本地源码 `d:\AI\external\tools\CodeWhale`：项目结构、核心模块、架构设计、配置示例

#### Scenario: 官网信息采集
- **WHEN** 采集官网内容
- **THEN** 应覆盖产品定位、安装方式、核心功能（模型路由、嵌套宪法、三种模式）、运行时界面（TUI/exec/web/API/Fleet）、提供商配置、产品名词表

#### Scenario: 源码结构分析
- **WHEN** 分析本地源码
- **THEN** 应覆盖项目整体结构（crates/ 模块划分）、核心模块功能（tui/config/agent/lane/fleet/workflow）、关键配置文件（config.example.toml、constitution.json）、文档资源（docs/ 目录）

### Requirement: 核心洞察提炼（I阶段）
系统 SHALL 基于采集的事实，提炼 CodeWhale 的核心设计洞察，每条洞察包含四元组（陈述/证据/反常识/行动）。

#### Scenario: 洞察提炼
- **WHEN** 事实采集完成后
- **THEN** 应提炼至少 3 条核心洞察，覆盖模型路由架构价值、嵌套宪法安全设计、终端优先交互哲学

### Requirement: Wiki 教程结构化萃取（E阶段）
系统 SHALL 将学习成果萃取为符合知识库模板规范的结构化 Wiki 教程，包含以下页面：

#### Scenario: Wiki 教程生成
- **WHEN** 洞察提炼完成后
- **THEN** 应生成以下 Wiki 页面：
  - `index.md`：知识库首页，含架构总览 Mermaid 图
  - `tech/intro.md`：项目概述（定位、核心价值、技术栈）
  - `tech/quickstart.md`：安装与首次使用指南
  - `tech/features.md`：核心功能详解（模型路由、嵌套宪法、三种模式、Fleet）
  - `tech/deploy.md`：安装渠道与提供商配置
  - `tech/changelog.md`：版本演进记录
  - `general/domain/index.md`：终端 AI 编程助手领域知识
  - `topics/index.md`：设计哲学与行业洞察

### Requirement: 对抗审查（V阶段）
系统 SHALL 对生成的 Wiki 教程执行四视角对抗审查（魔鬼代言人/新人/老板/未来），确保教程质量。

#### Scenario: 新人视角验证
- **WHEN** Wiki 教程初稿完成后
- **THEN** 应从零基础用户视角验证教程的可读性和可操作性，确保每个步骤都有明确的操作指引

### Requirement: 原子提交（C阶段）
系统 SHALL 将所有 Wiki 教程文件按单一职责原则原子提交。

#### Scenario: 原子提交
- **WHEN** 对抗审查通过后
- **THEN** 应将 Wiki 教程文件按模块分组原子提交，每个提交遵循 Conventional Commits 规范

## 非功能需求

- **NFR-1**：Wiki 教程语言为中文，专业术语保留英文原文并附中文解释
- **NFR-2**：所有页面使用 YAML frontmatter，遵循 MDI v1.0 规范
- **NFR-3**：Wiki 教程文件命名遵循 kebab-case 规范
- **NFR-4**：教程内容覆盖"安装→配置→使用→进阶"的完整学习路径

## 验收标准

- **AC-1**：官网信息采集完整，覆盖产品定位、功能、安装、运行时四个维度
- **AC-2**：源码结构分析覆盖核心模块与关键配置
- **AC-3**：至少提炼 3 条核心洞察，每条包含完整四元组
- **AC-4**：Wiki 教程至少包含 8 个页面（index + tech/ × 6 + general/ + topics/）
- **AC-5**：新人视角验证通过，零基础用户可按教程完成安装和首次使用
- **AC-6**：所有 Wiki 页面通过链接有效性检查
- **AC-7**：所有文件通过文件名规范检查
- **AC-8**：按原子提交原则完成所有变更提交