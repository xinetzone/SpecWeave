# Declarative Partial Updates 学习与 Wiki 教程文档 - 实施计划

## [x] Task 1: 创建 Wiki 教程文档基础框架与目录导航
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 docs/knowledge/learning/ 目录下创建 declarative-partial-updates-wiki.md 文件
  - 添加符合规范的 YAML frontmatter（title/source/date/tags），遵循 MDI v1.0 规范
  - 创建完整的目录导航系统，包含所有章节的锚点链接
  - 添加原文参考和 Chrome 官方文档链接的开头引用
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-12]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径 docs/knowledge/learning/declarative-partial-updates-wiki.md
  - `programmatic` TR-1.2: frontmatter 包含所有必填字段（title/source/date/tags），使用 YAML 格式（---包裹）
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节链接可跳转
  - `programmatic` TR-1.4: 包含原文 URL 和 Chrome 官方文档 URL
- **Notes**: 参考 text-to-cad-wiki.md 的文档结构和格式

## [x] Task 2: 编写技术概述与核心价值章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 介绍 Declarative Partial Updates 的定位：HTML 十年来最值得关注的升级
  - 说明核心变化：HTML 开始接管原本属于 JavaScript 的页面局部更新能力
  - 用一句话概括核心价值：服务端直接流式输出 HTML 片段，浏览器自动补到页面指定位置
  - 引出"HTML 不再只是首屏外壳，它开始重新参与 UI 更新"的方向变化
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 定位阐述准确（HTML 十年来最值得关注升级）
  - `human-judgement` TR-2.2: 核心价值概括清晰易懂
  - `human-judgement` TR-2.3: 适当引用原文内容
  - `human-judgement` TR-2.4: 方向变化阐述到位

## [x] Task 3: 编写痛点分析章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 详细解析传统 JavaScript 局部更新的链路过长问题
  - 展示传统更新流程：服务端查数据库 → 返回 JSON → 前端 fetch() → JS 解析数据 → 查找 DOM → 手动更新页面
  - 提供传统代码示例（fetch + querySelector + innerHTML）
  - 分析3个核心问题：链路过长、Web 页面变重、客户端 runtime 依赖
  - 说明"不是业务本身复杂，而是页面更新链路被拉长了"的本质
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 清晰阐述传统更新链路的6个步骤
  - `human-judgement` TR-3.2: 代码示例准确展示 fetch+DOM 操作模式
  - `human-judgement` TR-3.3: 3个核心问题分析到位
  - `human-judgement` TR-3.4: 适当引用原文内容

## [x] Task 4: 编写核心机制详解章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 详细解析 Declarative Partial Updates 的工作机制
  - 机制1：声明式更新区域 - `<?start name="order-status">` 和 `<?end>` 语法定义可更新区域
  - 机制2：template patch - `<template for="order-status">` 携带更新内容，浏览器自动匹配并替换
  - 机制3：流式输出 - 同一个 HTML 响应体持续流式输出，浏览器边接收边解析边 patch
  - 提供完整代码示例：订单状态从"查询中..."到"已支付"的更新过程
  - 对比新旧路径：以前（服务端→JSON→JS→DOM）vs 现在（服务端→HTML patch→浏览器自动更新）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 3个核心机制每个都有详细说明
  - `human-judgement` TR-4.2: 代码示例完整展示声明区域和 patch 机制
  - `human-judgement` TR-4.3: 新旧路径对比清晰
  - `human-judgement` TR-4.4: 技术术语解释准确

## [x] Task 5: 编写乱序流式更新章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 说明真实业务场景：一个页面慢通常是几个模块拖后腿（基础信息快/支付状态一般/风控结果较慢/操作日志最慢）
  - 分析传统两个选择的痛点（全等完首屏慢 vs 多接口前端逻辑复杂）
  - 介绍第三种方式：页面先出来，模块谁先准备好谁先补上
  - 提供多模块代码示例：支付状态和风控结果独立加载
  - 说明业务价值：慢模块不再拖死整页，用户先看到页面结构，内容一块一块长出来
  - 列举适用场景：后台详情页/订单页/商品页/评论区/搜索结果页/文档导航/CMS 模块
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 真实业务场景描述准确
  - `human-judgement` TR-5.2: 传统两个选择的痛点分析到位
  - `human-judgement` TR-5.3: 第三种方式阐述清晰
  - `human-judgement` TR-5.4: 业务价值说明具体
  - `human-judgement` TR-5.5: 适用场景列举完整

## [x] Task 6: 编写与现有技术对比章节
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 明确区分 Declarative Partial Updates 与 SSE、WebSocket、HTTP/2 Server Push、轮询的本质差异
  - 强调核心特点：一个 request、一个 response、HTML 响应体持续流式输出、浏览器边接收边解析边 patch
  - 使用对比表格清晰呈现各技术的差异（通信模式/协议/使用场景/复杂度）
  - 说明重点不是"实时通信"，而是"HTML 文档本身开始支持后续 patch"
  - 强调这是 HTML 交付方式的升级
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 4种现有技术（SSE/WebSocket/HTTP2 Push/轮询）都有对比
  - `human-judgement` TR-6.2: 本质差异阐述准确（单 request 单 response 流式 HTML）
  - `human-judgement` TR-6.3: 对比表格清晰易读
  - `human-judgement` TR-6.4: "HTML 交付方式升级"定位准确

## [x] Task 7: 编写框架影响分析章节
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 客观说明该能力不是"哪个框架要被替代"
  - 阐述前端框架解决的工程问题：组件组织、状态管理、路由、构建、复用、复杂交互、团队协作
  - 说明这些不是 HTML 提案能直接吃掉的
  - 分析真正改变的是：过去很多页面局部更新能力是框架和库在替浏览器补课
  - 说明新提案想把路径缩短：HTML 声明更新位置 + template 携带更新内容 + 浏览器原生完成 patch
  - 客观结论：不会让复杂前端消失，但会吃掉部分纯胶水代码（"把服务端内容塞回页面"的代码）
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 框架价值阐述客观
  - `human-judgement` TR-7.2: "替浏览器补课"观点阐述清晰
  - `human-judgement` TR-7.3: 胶水代码定义明确
  - `human-judgement` TR-7.4: 结论客观中立

## [x] Task 8: 编写 Declarative Shadow DOM 关联章节
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 介绍已落地的 Declarative Shadow DOM 能力
  - 对比传统 JavaScript 创建 Shadow DOM（element.attachShadow）与声明式方式
  - 提供声明式 Shadow DOM 代码示例（template shadowrootmode="open"）
  - 分析趋势：Declarative Shadow DOM 让组件封装回到 HTML，Declarative Partial Updates 让局部更新回到 HTML
  - 说明一个解决组件结构，一个解决内容更新
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-8.1: Declarative Shadow DOM 介绍准确
  - `human-judgement` TR-8.2: 新旧方式对比清晰
  - `human-judgement` TR-8.3: 代码示例正确
  - `human-judgement` TR-8.4: 趋势分析到位

## [x] Task 9: 编写内容评估章节
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 从三个维度评估原文内容：
  - 准确性评估：原文引用 Chrome 官方文档，技术细节与官方说明一致，语法示例准确
  - 权威性评估：来源为 Chrome 官方推进的能力，引用 developer.chrome.com 官方博客，权威性高
  - 实用性评估：当前处于开发者测试阶段，需通过实验性 flag 开启，暂不可用于生产环境，但概念预研价值高
  - 客观指出原文的优点（通俗易懂、对比清晰、趋势洞察）和不足（缺少兼容性说明、无性能数据）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 准确性评估有明确结论
  - `human-judgement` TR-9.2: 权威性评估有明确结论
  - `human-judgement` TR-9.3: 实用性评估有明确结论
  - `human-judgement` TR-9.4: 优缺点分析客观

## [x] Task 10: 编写个人理解与见解章节
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 提出对 HTML 平台化能力下沉的思考
  - 见解1：浏览器平台把框架层能力下沉到 HTML 标准是长期趋势
  - 见解2：声明式 > 命令式的设计哲学回归（从 JS 命令式回到 HTML 声明式）
  - 见解3："浏览器补课"现象 - 过去很多框架能力本质是弥补浏览器原生能力不足
  - 见解4：对前端工程的影响 - 简单场景可能不再需要引入完整框架
  - 见解5：对后端渲染的重新审视 - 服务端渲染 HTML 可能迎来复兴
  - 见解6：当前局限性的客观认识 - 实验阶段、标准化不确定、浏览器兼容性未知
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 见解有深度，非简单复述原文
  - `human-judgement` TR-10.2: 至少提出4个独立见解
  - `human-judgement` TR-10.3: 见解具有趋势性思考
  - `human-judgement` TR-10.4: 客观认识当前局限性

## [x] Task 11: 编写 FAQ 常见问题解答章节
- **Priority**: medium
- **Depends On**: Task 10
- **Description**: 
  - 整理常见问题并提供解答，如：
    - Q: Declarative Partial Updates 现在能在生产环境使用吗？
    - Q: 它和 SSE/WebSocket 有什么区别？
    - Q: 它会替代 React/Vue 等前端框架吗？
    - Q: 如何在 Chrome 中开启实验性测试？
    - Q: 服务端需要做什么改造？
    - Q: 它和 HTMX 等现有方案有什么关系？
    - Q: 浏览器兼容性如何？
    - Q: 与服务端渲染（SSR）是什么关系？
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 至少包含8个 FAQ 问题
  - `human-judgement` TR-11.2: 问题具有实际参考价值
  - `human-judgement` TR-11.3: 解答清晰准确

## [x] Task 12: 编写相关资源链接章节
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 
  - Chrome 官方文档：https://developer.chrome.com/blog/declarative-partial-updates?hl=zh-cn
  - 原文链接：微信公众号文章 URL
  - Declarative Shadow DOM 相关资源
  - Web Platform Features 相关文档
  - 流式 HTML 输出相关技术资料
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-12.1: Chrome 官方文档链接正确
  - `programmatic` TR-12.2: 原文链接正确
  - `human-judgement` TR-12.3: 资源分类清晰

## [x] Task 13: 更新知识库索引 README.md
- **Priority**: high
- **Depends On**: Task 12
- **Description**: 
  - 在 docs/knowledge/README.md 的 learning 分类表格中新增 Declarative Partial Updates 教程条目
  - 条目包含：标题、摘要、日期（2026-07-04）、标签（declarative-partial-updates、html、chrome、web-platform、streaming、html-patch、declarative-shadow-dom、frontend）
  - 遵循现有索引格式，保持表格结构一致
  - 更新统计摘要中的条目数
- **Acceptance Criteria Addressed**: [AC-13]
- **Test Requirements**:
  - `programmatic` TR-13.1: README.md 中 learning 分类新增了条目
  - `human-judgement` TR-13.2: 摘要准确概括教程内容
  - `human-judgement` TR-13.3: 标签设置合理
  - `programmatic` TR-13.4: 表格格式保持一致
  - `programmatic` TR-13.5: 统计摘要条目数已更新

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 4]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 6]
- [Task 8] depends on [Task 7]
- [Task 9] depends on [Task 8]
- [Task 10] depends on [Task 9]
- [Task 11] depends on [Task 10]
- [Task 12] depends on [Task 11]
- [Task 13] depends on [Task 12]
