---
title: "BrowserAct 官网完整学习教程：Cloud+Local双模式Agent浏览器平台"
source: "BrowserAct官方网站 https://www.browseract.com/?co-from=QD"
date: "2026-08-03"
tags: ["browseract", "ai-agent", "browser-automation", "web-scraping", "cloud", "skillhub", "data-api", "zapier", "n8n", "residential-proxy"]
---

# BrowserAct 官网完整学习教程 - 产品需求文档

## Overview
- **Summary**: 基于BrowserAct官方网站（https://www.browseract.com）的完整内容，系统学习BrowserAct产品的最新形态——已从单一CLI工具进化为Cloud+Local双模式平台，涵盖可复用云端爬虫构建、本地Agent浏览器能力、SkillHub技能生态、Data API、多场景模板、自动化平台集成等完整产品体系，创建一份全面的wiki教程文档。
- **Purpose**: 为项目团队提供BrowserAct产品的完整学习资料，帮助AI Agent开发者、数据采集工程师、自动化从业者全面理解BrowserAct Cloud和Local双版本的能力边界、使用场景、集成方式及资源入口。
- **Target Users**: AI Agent开发者、数据采集工程师、RPA开发者、电商运营、市场研究人员、需要网页自动化的产品经理和技术爱好者。

## Goals
- 创建包含目录导航系统的官网wiki教程文档
- 阐述BrowserAct的产品定位与最新标语
- 详细对比Cloud版本与Local Agent版本的区别和适用场景
- 解析7大核心功能特性（从提示词到爬虫、浏览器选择、自适应页面、受保护页面访问、平台集成、住宅代理、结构化输出）
- 讲解完整工作流程（环境准备→页面验证→提取→输出）
- 详细介绍4大使用场景（产品/供应商研究、客户/竞品研究、线索生成、创作者/新品/就业市场）
- 介绍SkillHub技能生态和Templates模板库
- 说明集成生态（Zapier/n8n/Make + Claude Code/Codex/Cursor）
- 介绍Data API、Multi-Account Social等高级能力
- 整理完整资源导航（Docs/Blog/API/LinkedIn爬虫等）
- 更新知识库索引添加本教程入口

## Non-Goals (Out of Scope)
- 不包含BrowserAct源码深度分析
- 不涉及Playwright/Puppeteer底层教学
- 不提供BrowserAct Cloud的具体定价信息（官网未展示）
- 不进行BrowserAct产品的竞品对比分析
- 不包含注册/付费流程的实操教程

## Background & Context
- BrowserAct官网标语已更新为："Build reusable web scrapers in the cloud, or give your local Agent a browser."
- 产品已进化为双模式架构：
  - **BrowserAct Cloud**：云端运行，无需安装，无本地存储，从提示词构建可复用爬虫
  - **Local Agent（AI Agents CLI）**：给本地Agent提供浏览器能力，支持Claude Code/Codex/Cursor
- 核心产品模块：Cloud、AI Agents CLI、SkillHub、Pricing、Affiliate
- 资源中心：Docs、Blog、Data API、Multi-Account Social、Templates、LinkedIn Profile/Comments Scraper
- 自动化集成：Zapier、n8n、Make（可运行已发布的Bots）
- 云合作伙伴：AWS、Microsoft Azure、Google Cloud、Oracle、Alibaba Cloud、Huawei Cloud、BytePlus、Baidu AI Cloud
- 示例能力：收集Amazon前20名无线耳机数据（价格/评分/库存/来源URL），18秒完成20条数据采集
- 社交渠道：X(Twitter)、LinkedIn、Discord、YouTube
- 联系邮箱：support@browseract.com
- 此前已创建基于微信公众号文章的browseract-wiki.md，本教程基于官网最新内容，更全面地覆盖产品生态

## Functional Requirements
- **FR-1**: 创建wiki教程文档主页面，包含完整目录导航系统
- **FR-2**: 编写产品概览章节，介绍BrowserAct最新定位、标语和双模式架构
- **FR-3**: 编写Cloud vs Local对比章节，详细说明两种模式的区别、入口和适用场景
- **FR-4**: 编写7大核心功能章节，逐一解析每个特性
- **FR-5**: 编写工作流程章节，演示从提示词到数据输出的完整链路
- **FR-6**: 编写4大使用场景章节，详细说明每个场景的应用方式
- **FR-7**: 编写产品生态章节，介绍SkillHub、Templates、Data API、Multi-Account Social
- **FR-8**: 编写集成生态章节，说明Zapier/n8n/Make集成和本地Agent支持
- **FR-9**: 编写快速开始章节，说明Cloud和Local两种入口的使用方式
- **FR-10**: 编写资源导航章节，整理所有官方资源链接
- **FR-11**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平读者
- **NFR-2**: 基于官网公开内容，不添加未验证信息
- **NFR-3**: 文档结构清晰，便于阅读和导航
- **NFR-4**: 文档格式符合项目规范（Markdown、YAML frontmatter、kebab-case命名）
- **NFR-5**: 技术术语准确，功能描述与官网一致
- **NFR-6**: 客观呈现产品能力，不夸大不贬低

## Constraints
- **Technical**: Markdown格式，YAML frontmatter，放置于docs/knowledge/learning/目录
- **Business**: 基于官网公开内容，定价等未展示信息不猜测
- **Dependencies**: 依赖已通过浏览器提取的官网内容

## Assumptions
- 用户具备基本的AI Agent和网页自动化概念
- 用户可以访问BrowserAct官网
- 用户理解数据采集和爬虫的基本概念

## Acceptance Criteria

### AC-1: Wiki教程文档创建完成
- **Given**: spec.md中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki教程包含目录导航、产品概览、双模式对比、核心功能、工作流程、使用场景、产品生态、集成生态、快速开始、资源导航等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文件名为browseract-official-wiki.md，放置在docs/knowledge/learning/目录

### AC-2: 目录导航系统可用
- **Given**: 用户打开wiki教程文档
- **When**: 用户查看顶部目录导航
- **Then**: 目录包含所有章节锚点链接，点击可跳转
- **Verification**: `programmatic`

### AC-3: 产品定位与标语准确
- **Given**: 用户阅读产品概览
- **When**: 用户理解BrowserAct最新定位
- **Then**: 用户能够准确说出官网标语"Build reusable web scrapers in the cloud, or give your local Agent a browser"
- **Verification**: `human-judgment`

### AC-4: Cloud与Local双模式对比清晰
- **Given**: 用户阅读双模式对比章节
- **When**: 用户理解两种模式的区别
- **Then**: 用户能够对比Cloud（无需安装、云端运行、可复用爬虫）和Local（本地Agent浏览器、实时连接、CLI工具）的特点和适用场景
- **Verification**: `human-judgment`
- **Notes**: 使用对比表格呈现

### AC-5: 7大核心功能解析完整
- **Given**: 用户阅读核心功能章节
- **When**: 用户理解每个功能
- **Then**: 用户能够说明：提示词→可复用爬虫、Private/Standard浏览器选择、页面自适应、隐身浏览+验证码、Zapier/n8n/Make集成、住宅代理、结构化数据输出
- **Verification**: `human-judgment`

### AC-6: 工作流程演示清晰
- **Given**: 用户阅读工作流程章节
- **When**: 用户理解完整链路
- **Then**: 用户能够描述从提示词描述→选择浏览器/代理→构建Bot→环境准备→页面验证→数据提取→输出CSV/文件的完整流程（以Amazon耳机采集为示例）
- **Verification**: `human-judgment`

### AC-7: 4大使用场景说明详细
- **Given**: 用户阅读使用场景章节
- **When**: 用户了解应用方向
- **Then**: 用户能够说明产品/供应商研究、客户/竞品研究、线索生成、创作者/新品/就业市场四大场景的具体用途和数据类型
- **Verification**: `human-judgment`

### AC-8: 产品生态介绍完整
- **Given**: 用户阅读产品生态章节
- **When**: 用户了解SkillHub、Templates、Data API等
- **Then**: 用户知道SkillHub是技能市场、Templates提供模板、Data API提供数据接口、Multi-Account Social支持多账号社交管理
- **Verification**: `human-judgment`

### AC-9: 集成生态说明准确
- **Given**: 用户阅读集成章节
- **When**: 用户了解集成能力
- **Then**: 用户知道支持Zapier/n8n/Make运行Bots，支持Claude Code/Codex/Cursor本地Agent，以及8家云合作伙伴
- **Verification**: `human-judgment`

### AC-10: 资源导航链接完整
- **Given**: 用户点击资源链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的官网页面
- **Verification**: `programmatic`
- **Notes**: 包含官网、Docs、Blog、GitHub、社交链接等

### AC-11: 知识库索引更新完成
- **Given**: wiki文档创建完成
- **When**: 查看docs/knowledge/README.md
- **Then**: learning分类新增BrowserAct官网教程条目
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要与之前的微信文章版browseract-wiki.md做内容整合或互链？
- [ ] 是否需要补充BrowserAct Cloud实际使用的截图或更详细的操作步骤？
