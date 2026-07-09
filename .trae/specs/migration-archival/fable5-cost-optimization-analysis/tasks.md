---
version: "1.0"
---

# Fable 5 成本优化技巧深度分析 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建wiki目录结构和原始文章存档
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 docs/knowledge/learning/03-agent-platforms-tools/ 下创建 fable5-cost-optimization-wiki/ 目录
  - 将defuddle提取的文章内容保存为 article-content.md，携带YAML frontmatter（source、title、extracted_at）
  - 创建wiki骨架文件：00-overview.md、01-pricing-background.md、02-community-solutions.md、03-official-optimizations.md、04-selection-guide.md、05-core-insights.md、06-faq.md、07-resources.md、README.md
  - 为每个骨架文件添加基础frontmatter
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在且包含9个.md文件（article-content + 8个wiki章节 + README）
  - `programmatic` TR-1.2: 每个文件都有合法的YAML frontmatter，包含version和source字段
  - `human-judgement` TR-1.3: article-content.md内容完整，与提取内容一致
- **Notes**: 参考同目录下其他wiki的结构（如longcat-agent-learning-wiki、headroom-context-compression-wiki）

## [x] Task 2: 编写概览和背景章节（00-overview + 01-pricing-background）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 00-overview.md: 主题概述、核心问题、5大方法速览、读者收益、wiki导航
  - 01-pricing-background.md: Fable 5延期公告、按量计费时间节点、定价详情（输入/输出价格对比Opus 4.8）、订阅vs按量的成本心理差异
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 概览清晰说明文章主题和价值，导航链接指向正确章节
  - `human-judgement` TR-2.2: 背景信息准确，价格数据与原文一致，时间节点清晰
  - `programmatic` TR-2.3: 内部链接使用相对路径，无file://绝对路径

## [x] Task 3: 编写社区开源方案章节（02-community-solutions）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 分三个子节分别记录三个开源方案：
    1. 技能蒸馏（fable-5-train-opus-skills-after-it-retires）：提示词设计、三步执行流程（通读项目→并行生成skills→评审修复）、oh-my-fable的工程化扩展
    2. 文字转图片（pxpipe）：Token价差原理（图片token装载率3.1字符/token vs 文本1字符/token）、本地代理架构、59%-70%节省效果、有损压缩局限性（哈希/密钥识别准确率、Fable 5视觉能力依赖）
    3. 包工头模式（fable-token-saving-skills-orchestrator）：判断力vs执行力的分工、派工单机制、摘要压缩反馈、安装方式
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每个方案包含项目地址、核心原理、执行步骤/架构、优缺点、适用场景
  - `human-judgement` TR-3.2: 技术细节准确（如pxpipe的压缩率、技能蒸馏的三步流程）
  - `programmatic` TR-3.3: 所有GitHub链接格式正确

## [x] Task 4: 编写官方优化机制章节（03-official-optimizations）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 分两个子节记录官方技巧：
    1. 缓存经济学（Prompt Cache）：缓存价格机制（写缓存1.25倍、读缓存0.1倍=省90%）、默认5分钟TTL、命中刷新续命、冷启动成本、续命策略（空请求保活vs放弃缓存）、多模型协作节奏排期
    2. 批量接口（Batch API）：适用场景（非紧急任务）、半价优势（$5/$25）、与缓存叠加效果（输入低至$0.5/百万token=0.5折）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 缓存机制讲解清晰，包含价格、TTL、刷新、续命策略等细节
  - `human-judgement` TR-4.2: 批量接口的适用场景和叠加优惠计算正确
  - `human-judgement` TR-4.3: 包含实操建议（何时保活、何时放弃缓存）

## [x] Task 5: 编写选型指南与核心洞察（04-selection-guide + 05-core-insights）
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - 04-selection-guide.md: 场景化选型决策矩阵
    - 长上下文场景 → pxpipe
    - 重复固定流程任务 → 技能蒸馏
    - 混合难度团队协作 → 包工头模式
    - 缓存续命最佳实践
    - 批量接口适用时机
    - 方案组合建议
  - 05-core-insights.md: 提取超越文章本身的工程洞察
    - Token价差套利思维（模态间计费差异利用）
    - 模型分层协作架构（贵模型做决策、便宜模型做执行）
    - 知识沉淀传承方法论（退休前蒸馏）
    - 缓存感知的任务编排
    - 按量计费时代的成本意识转变
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 选型指南提供清晰的if-then决策逻辑，覆盖主要场景
  - `human-judgement` TR-5.2: 核心洞察有深度，不是简单复述原文，而是提炼方法论
  - `human-judgement` TR-5.3: 洞察与SpecWeave现有方法论（如技能系统、多agent协作）有呼应

## [x] Task 6: 编写FAQ和资源章节（06-faq + 07-resources）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 06-faq.md: 常见问题解答
    - 这些方案现在还能用吗？（7月12日前订阅期、7月12日后按量期）
    - pxpipe对其他模型有效吗？
    - 技能蒸馏生成的skills质量如何保证？
    - 包工头模式如何配置？
    - 缓存续命具体怎么操作？
  - 07-resources.md: 资源汇总
    - 原文链接
    - 三个GitHub项目链接
    - Anthropic官方定价文档
    - 相关讨论链接（Reddit、Twitter/X）
    - 相关wiki交叉引用（headroom-context-compression、longcat-agent等）
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-6.1: FAQ覆盖用户可能的疑问，解答基于原文信息
  - `programmatic` TR-6.2: 所有外部链接格式正确
  - `programmatic` TR-6.3: 内部交叉引用使用正确的相对路径

## [x] Task 7: 更新README和索引同步
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 编写fable5-cost-optimization-wiki/README.md作为wiki入口，包含导航表
  - 更新 docs/knowledge/learning/03-agent-platforms-tools/README.md，添加新wiki入口
  - 如有必要，更新 docs/knowledge/learning/README.md 添加索引
  - 运行 generate-readme.py --update 或 --target-dir 自动生成索引
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-7.1: README.md导航表包含所有8个章节链接
  - `programmatic` TR-7.2: 父目录README已更新，新wiki可见
  - `programmatic` TR-7.3: 运行check-links.py验证无断链

## [x] Task 8: 链接验证和质量检查
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 运行 python .agents/scripts/check-links.py --path docs/knowledge/learning/03-agent-platforms-tools/fable5-cost-optimization-wiki 检查内部链接
  - 验证所有frontmatter的source字段格式正确
  - 检查frontmatter中是否有需要验证的路径引用（--check-frontmatter-paths）
  - 确认所有文档遵循单一职责原则，无内容重复
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-8.1: check-links.py通过，无断链
  - `programmatic` TR-8.2: frontmatter路径检查通过
  - `human-judgement` TR-8.3: 文档无明显内容重复，每个章节聚焦独立主题

## [ ] Task 9: 原子化提交
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 按原子化提交原则拆分提交：
    1. docs(learning): 添加Fable 5成本优化wiki原始文章存档
    2. docs(learning): 添加Fable 5定价背景和概览章节
    3. docs(learning): 添加社区开源成本优化方案章节（技能蒸馏+pxpipe+包工头模式）
    4. docs(learning): 添加官方优化机制章节（缓存经济学+批量接口）
    5. docs(learning): 添加选型指南和核心工程洞察
    6. docs(learning): 添加FAQ和资源章节
    7. docs(learning): 更新README索引同步
  - 使用 atomic-commit-cmd 技能确保每个提交单一职责
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-9.1: 每个commit只包含相关文件，遵循单一职责
  - `programmatic` TR-9.2: commit message符合Conventional Commits格式（中文描述）
  - `programmatic` TR-9.3: git status显示工作区干净，无未提交变更
