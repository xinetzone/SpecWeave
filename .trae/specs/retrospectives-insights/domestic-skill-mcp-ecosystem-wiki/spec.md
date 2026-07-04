---
title: "国内 Skill/MCP 生态盘点学习与 Wiki 教程文档"
source: "微信公众号文章《国内 Skill/MCP 生态盘点：16 个品牌的 Agent 化浪潮》"
date: "2026-07-04"
tags: ["skill", "mcp", "cli", "ai-agent", "ecosystem", "domestic", "wechat", "feishu", "dingtalk", "payment"]
---

# 国内 Skill/MCP 生态盘点学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习微信公众号文章介绍的国内 Skill/MCP 生态盘点内容，理解 Skill、MCP、CLI 三种 Agent 集成方式的差异，梳理 16 个品牌的 Agent 化产品布局（餐饮/出行/办公/支付/内容等），分析支付环节"最后一公里"信任难题与行业窗口期机遇，基于学习成果创建一份结构清晰、内容详实的 wiki 教程文档。
- **Purpose**: 为项目团队提供国内 Agent 生态现状的完整学习资料，帮助开发者、产品经理、技术决策者理解 Skill/MCP/CLI 的概念差异与各品牌集成方案，把握 Agent 化浪潮的趋势与机会。
- **Target Users**: AI Agent 技术爱好者、应用开发者、产品经理、技术决策者、关注国内 AI 生态发展的研究者。

## Goals
- 创建包含目录导航系统的 wiki 教程文档
- 解释 Skill、MCP、CLI 三种 Agent 集成方式的概念与差异
- 按行业分类详细盘点 16 个品牌的 Agent 产品（餐饮/出行/跑腿/办公协作/支付/内容创作）
- 解析每个产品的核心能力、集成形态与使用体验
- 分析支付环节"最后一公里"信任难题的技术可行性与社会信任维度
- 总结 Agent 化浪潮的窗口期机遇与未来趋势
- 整理常见问题解答
- 汇总相关资源链接（官方平台/GitHub 仓库）

## Non-Goals (Out of Scope)
- 不对各品牌的 Skill/MCP 进行源码级深度分析
- 不提供各品牌 Skill 的完整安装部署教程（仅提供入口链接）
- 不进行国内外 Agent 生态的横向对比
- 不预测具体的市场份额与商业数据
- 不包含未在原文中提及的品牌或产品

## Background & Context
- 文章作者：卡兹克、可达
- 文章性质：国内 Skill/MCP 生态的行业观察与盘点
- 核心论点：Agent 化时代正在到来，Skill/MCP/CLI 是 Agent 基建的三种形态
- 关键洞察：支付环节大家都不敢让 Agent 直接替用户付款，这是社会信任问题而非技术问题
- 历史类比：当前阶段类似 2017 年小程序刚出来时的窗口期
- 三种集成方式说明：
  - **Skill**：面向 Agent 使用者的能力封装，类似"插件"，用户一句话即可安装使用
  - **MCP**：Model Context Protocol，面向开发者的标准化上下文协议，能力更强但需技术接入
  - **CLI**：命令行工具，面向开发者，可被 Claude Code 等编程 Agent 调用
- 原文参考：https://mp.weixin.qq.com/s/08Z-Jk4nccaBAbh65aqtKA

## Functional Requirements
- **FR-1**: 创建 wiki 教程文档主页面，包含完整的目录导航系统
- **FR-2**: 编写概念入门章节，清晰解释 Skill、MCP、CLI 三种集成方式的定义、差异与适用人群
- **FR-3**: 编写餐饮行业章节，盘点瑞幸咖啡（Skill）、麦当劳（MCP）的 Agent 化方案与使用体验
- **FR-4**: 编写出行行业章节，盘点飞猪、滴滴、高德地图、腾讯地图的 Skill/MCP 方案
- **FR-5**: 编写跑腿服务章节，介绍美团跑腿 Skill 的地址簿匹配与订单预览设计
- **FR-6**: 编写办公协作章节，盘点飞书、钉钉、企业微信、腾讯文档的 Skill/CLI/MCP 全形态布局
- **FR-7**: 编写支付能力章节，盘点支付宝、微信支付的 Skill/MCP 方案，重点分析"支付最后一公里"信任难题
- **FR-8**: 编写内容创作章节，盘点微信读书、网易云音乐、美图的 Skill/CLI 方案
- **FR-9**: 编写第三方集成章节，介绍千问、豆包、WorkBuddy 等 AI 产品内置第三方 Skill 的模式
- **FR-10**: 编写趋势洞察章节，分析 Agent 化窗口期、贾维斯愿景与生态演进方向
- **FR-11**: 编写常见问题解答章节
- **FR-12**: 编写相关资源链接章节，汇总 16 个品牌的官方平台与 GitHub 仓库
- **FR-13**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（开发者/产品经理/研究者）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据
- **NFR-3**: 文档结构清晰，按行业分类组织，便于阅读和导航
- **NFR-4**: 文档格式符合项目规范（Markdown 格式，kebab-case 命名，YAML frontmatter）
- **NFR-5**: 技术术语准确，Skill/MCP/CLI 概念区分清晰
- **NFR-6**: 客观呈现各品牌方案差异，不进行商业评价或排名

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，放置在 docs/knowledge/learning/ 目录下
- **Business**: 基于公开文章内容创建，不得添加未验证的信息，客观说明各品牌方案差异
- **Dependencies**: 依赖已获取的网页内容，无需额外网络请求

## Assumptions
- 用户了解基本的 AI Agent 概念（如 Claude Code、ChatGPT 等）
- 用户对国内主流互联网产品（微信、支付宝、飞书等）有基本认知
- 用户可以访问互联网获取各品牌的官方平台信息
- 用户理解"插件/扩展"类产品的基本使用方式

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki 教程文档包含目录导航、概念入门、行业盘点（6 大类）、第三方集成、趋势洞察、FAQ 和资源链接等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在 docs/knowledge/learning/ 目录下，文件名为 domestic-skill-mcp-ecosystem-wiki.md

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 锚点链接实现

### AC-3: Skill/MCP/CLI 三种概念解释清晰
- **Given**: 用户阅读概念入门章节
- **When**: 用户理解三种集成方式
- **Then**: 用户能够说明 Skill（面向使用者的能力封装）、MCP（面向开发者的标准化协议）、CLI（面向开发者的命令行工具）的定义、差异与适用人群
- **Verification**: `human-judgment`
- **Notes**: 引用原文"对于大家来说，其实都是把网址扔过去然后说给我安装其实就行了"的通俗解释

### AC-4: 16 个品牌盘点完整准确
- **Given**: 用户阅读行业盘点章节
- **When**: 用户了解各品牌的 Agent 化方案
- **Then**: 用户能够列举 16 个品牌及其集成形态（餐饮 2 个、出行 4 个、跑腿 1 个、办公协作 4 个、支付 2 个、内容创作 3 个）
- **Verification**: `human-judgment`
- **Notes**: 每个品牌需包含核心能力、集成形态、官方平台链接

### AC-5: 支付最后一公里信任难题分析深入
- **Given**: 用户阅读支付能力章节
- **When**: 用户理解支付环节的信任问题
- **Then**: 用户能够说明"技术上轻轻松松就能做到，但社会信任上还没到那一步"的核心论点，并列举瑞幸（扫码支付）、麦当劳（跳 app）、美团跑腿（打开 app）三种支付跳转方式
- **Verification**: `human-judgment`
- **Notes**: 引用原文相关论述

### AC-6: 第三方集成模式说明清晰
- **Given**: 用户阅读第三方集成章节
- **When**: 用户理解 AI 产品内置第三方 Skill 的模式
- **Then**: 用户能够说明千问（接入阿里生态+开放第三方）、豆包（接曹操出行）、WorkBuddy（集成腾讯系能力）三种集成模式的差异
- **Verification**: `human-judgment`
- **Notes**: 区分"独立发布 Skill"与"在 AI 产品中集成第三方服务"两种模式

### AC-7: 趋势洞察章节有深度
- **Given**: 用户阅读趋势洞察章节
- **When**: 用户理解 Agent 化浪潮的趋势
- **Then**: 用户能够说明 2017 年小程序类比、窗口期机遇、贾维斯愿景三个核心观点
- **Verification**: `human-judgment`
- **Notes**: 引用原文"它在慢慢变成你在数字世界里的另一个自己"

### AC-8: FAQ 章节实用
- **Given**: 用户遇到问题
- **When**: 用户查阅 FAQ 章节
- **Then**: 用户能够找到对应的解决方案或解释
- **Verification**: `human-judgment`
- **Notes**: FAQ 应覆盖 Skill/MCP/CLI 概念、安装、支付、生态等常见问题

### AC-9: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的官方平台或 GitHub 仓库
- **Verification**: `programmatic`
- **Notes**: 至少包含 16 个品牌的官方平台链接和原文链接

### AC-10: 知识库索引更新完成
- **Given**: wiki 文档创建完成
- **When**: 查看 docs/knowledge/README.md
- **Then**: 学习分类中新增本教程条目，包含标题、摘要、日期和标签
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

## Open Questions
- [ ] 是否需要创建原子化的子目录结构来组织 wiki 文档？
- [ ] 是否需要补充各品牌 Skill 的实际安装命令示例？
