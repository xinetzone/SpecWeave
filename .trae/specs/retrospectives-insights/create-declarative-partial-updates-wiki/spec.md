---
title: "Declarative Partial Updates 学习与 Wiki 教程文档"
source: "微信公众号文章《HTML 最值得关注的一次升级：声明式局部更新》"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/create-declarative-partial-updates-wiki/spec.toml"
date: "2026-07-04"
tags: ["declarative-partial-updates", "html", "chrome", "web-platform", "streaming", "html-patch", "declarative-shadow-dom", "frontend"]
---
# Declarative Partial Updates 学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习微信公众号文章介绍的 Chrome 正在推进的 Declarative Partial Updates（声明式局部更新）能力，理解其核心概念、技术原理、语法机制、应用场景及与现有技术栈的关系，基于学习成果创建一份结构清晰、内容详实的 wiki 教程文档，并完成对原文内容的准确性、权威性和实用性评估。
- **Purpose**: 为前端开发者、Web 平台技术爱好者和项目团队提供 Declarative Partial Updates 的完整学习资料，帮助理解 HTML 重新参与 UI 更新的趋势，以及该能力对现有前端架构的潜在影响。
- **Target Users**: 前端开发者、Web 平台技术爱好者、全栈工程师、技术决策者、关注 Web 标准演进的开发者。

## Goals
- 创建包含目录导航系统的 wiki 教程文档
- 解释 Declarative Partial Updates 解决的核心痛点和设计理念
- 详细解析技术原理（声明式更新区域、template patch 机制、流式输出）
- 对比传统 JavaScript 局部更新方案的差异
- 说明乱序流式更新的实际业务价值
- 分析与 Declarative Shadow DOM 的趋势关联
- 评估内容的准确性、权威性和实用性
- 提出个人理解与见解
- 整理常见问题解答
- 汇总相关资源链接

## Non-Goals (Out of Scope)
- 不包含 Chrome 浏览器源码的深度分析
- 不涉及 W3C/WHATWG 标准制定流程的详细讨论
- 不提供完整的前端框架迁移指南
- 不进行性能基准测试
- 不包含 polyfill 或兼容性方案实现
- 不涉及非 Chrome 浏览器的实现计划

## Background & Context
- Declarative Partial Updates 是 Chrome 正在推进的新 HTML 能力
- 核心思路：让 HTML 自己完成局部更新，服务端直接流式输出 HTML 片段
- 使用 `<?start name="...">` 和 `<?end>` 定义可更新区域
- 使用 `<template for="...">` 携带更新内容
- 浏览器自动将 patch 内容补到页面指定位置
- 支持乱序流式更新，慢模块不再拖死整页
- 当前状态：开发者测试阶段，需通过 Chrome 实验性 Web Platform Features flag 开启
- 相关能力：Declarative Shadow DOM（已落地）
- 官方文档：https://developer.chrome.com/blog/declarative-partial-updates?hl=zh-cn
- 原文参考：https://mp.weixin.qq.com/s/MpJSwf9wbB14uVlNo6YyWA

## Functional Requirements
- **FR-1**: 创建 wiki 教程文档主页面，包含完整的目录导航系统
- **FR-2**: 编写技术概述章节，介绍 Declarative Partial Updates 的定位和核心价值主张
- **FR-3**: 编写痛点分析章节，详细解析传统 JavaScript 局部更新的链路过长问题（服务端→JSON→fetch→JS解析→DOM操作）
- **FR-4**: 编写核心机制章节，详细解析 `<?start?>`/`<?end>` 声明区域、`<template for>` patch 机制、流式输出原理
- **FR-5**: 编写乱序流式更新章节，说明多模块独立加载的业务价值（详情页/订单页/商品页/评论区等场景）
- **FR-6**: 编写与现有技术对比章节，明确区分 SSE/WebSocket/HTTP/2 Server Push/轮询的本质差异
- **FR-7**: 编写框架影响分析章节，客观说明该能力不会替代前端框架，但会吃掉部分胶水代码
- **FR-8**: 编写 Declarative Shadow DOM 关联章节，分析"HTML 重新变强"的趋势
- **FR-9**: 编写内容评估章节，从准确性、权威性、实用性三个维度评估原文
- **FR-10**: 编写个人理解与见解章节，提出对 HTML 平台化能力下沉的思考
- **FR-11**: 编写常见问题解答章节
- **FR-12**: 编写相关资源链接章节
- **FR-13**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（前端开发者/全栈工程师/技术决策者）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据
- **NFR-3**: 文档结构清晰，便于阅读和导航
- **NFR-4**: 文档格式符合项目规范（Markdown格式，kebab-case命名，YAML frontmatter）
- **NFR-5**: 技术术语准确，关键概念提供清晰解释
- **NFR-6**: 评估部分客观中立，既肯定创新价值也指出当前局限性

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，放置在 docs/knowledge/learning/ 目录下，使用 YAML frontmatter（遵循 MDI v1.0 规范）
- **Business**: 基于公开文章内容创建，客观说明当前处于实验阶段不可用于生产环境
- **Dependencies**: 依赖已获取的网页内容，无需额外网络请求

## Assumptions
- 用户具备基本的 HTML 和 JavaScript 知识
- 用户了解传统 AJAX/fetch 局部更新的工作方式
- 用户对前端框架（React/Vue 等）有基本认知
- 用户可以访问互联网查阅 Chrome 官方文档

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki 教程文档包含目录导航、技术概述、痛点分析、核心机制、乱序流式更新、技术对比、框架影响、Shadow DOM 关联、内容评估、个人见解、FAQ 和资源链接等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在 docs/knowledge/learning/ 目录下，文件名为 declarative-partial-updates-wiki.md

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 锚点链接实现

### AC-3: 痛点分析阐述清晰
- **Given**: 用户阅读痛点分析章节
- **When**: 用户理解传统 JavaScript 局部更新的问题
- **Then**: 用户能够说明传统更新链路（服务端→JSON→fetch→JS→DOM）的3个核心问题：链路过长、Web 页面变重、客户端 runtime 依赖
- **Verification**: `human-judgment`
- **Notes**: 引用原文中的代码示例和流程对比

### AC-4: 核心机制解析完整
- **Given**: 用户阅读核心机制章节
- **When**: 用户理解 Declarative Partial Updates 的工作原理
- **Then**: 用户能够解释 `<?start?>`/`<?end>` 声明区域语法、`<template for>` patch 机制、流式输出原理，并能写出基本的使用示例
- **Verification**: `human-judgment`
- **Notes**: 包含订单状态更新的完整代码示例

### AC-5: 乱序流式更新价值阐述到位
- **Given**: 用户阅读乱序流式更新章节
- **When**: 用户理解多模块独立加载的业务价值
- **Then**: 用户能够说明在后台详情页/订单页/商品页等场景下，慢模块不再拖死整页的机制，以及页面"先出来再补内容"的体验优势
- **Verification**: `human-judgment`
- **Notes**: 使用支付状态/风控结果/操作日志等多模块示例

### AC-6: 技术对比区分准确
- **Given**: 用户阅读技术对比章节
- **When**: 用户理解与现有技术的区别
- **Then**: 用户能够准确区分 Declarative Partial Updates 与 SSE、WebSocket、HTTP/2 Server Push、轮询的本质差异（单 request 单 response 的流式 HTML 输出）
- **Verification**: `human-judgment`
- **Notes**: 使用对比表格清晰呈现差异

### AC-7: 框架影响分析客观
- **Given**: 用户阅读框架影响分析章节
- **When**: 用户理解对前端框架的影响
- **Then**: 用户能够说明该能力不会替代前端框架（组件组织/状态管理/路由/构建等），但会吃掉部分"把服务端内容塞回页面"的胶水代码
- **Verification**: `human-judgment`
- **Notes**: 客观分析，不夸大也不贬低

### AC-8: Shadow DOM 关联阐述清晰
- **Given**: 用户阅读 Declarative Shadow DOM 关联章节
- **When**: 用户理解两者关系
- **Then**: 用户能够说明 Declarative Shadow DOM（组件封装回 HTML）和 Declarative Partial Updates（内容更新回 HTML）共同体现的"HTML 重新变强"趋势
- **Verification**: `human-judgment`
- **Notes**: 包含 Declarative Shadow DOM 的代码示例

### AC-9: 内容评估三维度完整
- **Given**: 用户阅读内容评估章节
- **When**: 用户查看准确性、权威性、实用性评估
- **Then**: 用户能够了解原文内容的准确度（引用官方 Chrome 文档）、权威性（Chrome 官方推进）、实用性（实验阶段不可生产使用）的客观评价
- **Verification**: `human-judgment`
- **Notes**: 三维度评估各有明确结论

### AC-10: 个人见解有洞察力
- **Given**: 用户阅读个人理解与见解章节
- **When**: 用户理解作者的观点
- **Then**: 用户能够看到关于"HTML 平台化能力下沉""浏览器补课""框架层能力回归标准"等趋势性思考
- **Verification**: `human-judgment`
- **Notes**: 见解应有深度，避免简单复述原文

### AC-11: FAQ 章节实用
- **Given**: 用户遇到问题
- **When**: 用户查阅 FAQ 章节
- **Then**: 用户能够找到对应的解决方案或解释
- **Verification**: `human-judgment`
- **Notes**: FAQ 应覆盖常见问题

### AC-12: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面
- **Verification**: `programmatic`
- **Notes**: 至少包含 Chrome 官方文档链接和原文链接

### AC-13: 知识库索引更新完成
- **Given**: wiki 文档创建完成
- **When**: 查看 docs/knowledge/README.md
- **Then**: learning 分类中新增 Declarative Partial Updates 教程条目，包含标题、摘要、日期和标签
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

## Open Questions
- [ ] 是否需要补充 W3C/WHATWG 标准化进展信息？
- [ ] 是否需要添加与其他浏览器厂商立场的对比？
