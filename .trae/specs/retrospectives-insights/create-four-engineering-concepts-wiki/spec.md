---
title: "AI 四大工程概念演进学习与 Wiki 教程文档"
source: "微信公众号文章《Prompt → Context → Harness → Loop：AI 圈这四个新词，一次性讲清楚》 by AllenTang"
date: "2026-07-04"
tags: ["prompt-engineering", "context-engineering", "harness-engineering", "loop-engineering", "ai-agent", "bottleneck-shift", "methodology"]
---

# AI 四大工程概念演进学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习微信公众号文章（作者 AllenTang）关于 AI 圈四个"Engineering"概念演进脉络的内容，理解 Prompt Engineering、Context Engineering、Harness Engineering、Loop Engineering 四者的核心定义、解决瓶颈、层层包含关系，以及"瓶颈外移"这一核心规律。基于学习成果创建一份结构清晰、洞察深入的结构化学习笔记与分析报告。
- **Purpose**: 为项目团队提供 AI Agent 工程演进脉络的完整学习资料，帮助开发者理解为何"同样用 GPT、用 Claude，有的团队做出来的 Agent 又稳又能打，到别人手里却一跑就崩"的根本原因，并指导 harness 与 loop 的工程实践。
- **Target Users**: AI Agent 开发者、提示词工程师、对 AI 工程方法论感兴趣的技术人员、希望提升 Agent 稳定性的团队负责人、需要理解 AI 工程演进趋势的技术决策者。

## Goals
- 创建包含目录导航系统的结构化学习笔记 wiki 文档
- 完整阐述"瓶颈外移"核心规律及其反直觉特点
- 逐一解析四个工程概念的定义、解决瓶颈、核心做法与适用场景
- 深度解析 Harness Engineering 这一"关键一跃"的内涵与公式（Agent = 模型 + Harness）
- 阐明四者"层层包含"关系（Prompt ⊂ Context ⊂ Harness）
- 整理文章引用的关键人物观点与原话
- 萃取实践启示与方法论价值
- 整理常见问题解答与相关资源链接

## Non-Goals (Out of Scope)
- 不对四个概念进行超出原文范围的扩展或臆测
- 不涉及具体 harness 工具链的安装教程
- 不进行 prompt/context/harness/loop 的代码级实现示例
- 不评判原文观点的对错，保持客观转述与结构化整理
- 不重复造轮子，若项目已有相关概念文档则建立引用

## Background & Context
- 原文由 AllenTang 撰写，发布于微信公众号
- 原文链接：https://mp.weixin.qq.com/s/eeB14yOtDU6akQUp0Mkauw
- 文章核心论点：四个"Engineering"概念不是四个互相换皮的赛道，而是同一条线上的四个路标
- 核心规律：每当模型变强一截，整个系统的瓶颈就被迫往外移一层（你怎么说 → 你给什么 → 它干活的环境 → 你自己）
- 关键一跃：Harness Engineering 第一次把工程重心从"调教模型"搬到"设计模型外面的世界"
- 引用的关键人物：
  - Mitchell Hashimoto（Terraform 作者）— Harness 概念点响者
  - Peter Steinberger（OpenClaw 作者）— Loop 概念点响者之一
  - Addy Osmani（Google AI 总监）— Loop 正式定义者
  - Boris Cherny（Claude Code 创始人）— "我已经不 prompt Claude 了"观点
- 引用的关键概念：
  - Anthropic 的 context rot（上下文腐化）
  - Anthropic Agent Skills 的渐进式披露
  - 公式：Agent = 模型 + Harness

## Functional Requirements
- **FR-1**: 创建 wiki 文档主页面，包含完整的目录导航系统
- **FR-2**: 编写核心论点章节，阐述"瓶颈外移"规律及四者作为"同一条线上四个路标"的关系
- **FR-3**: 编写 Prompt Engineering 章节，解析"瓶颈卡在你怎么说"（角色设定/背景/参考资料/明确任务/约束/输出格式配方）
- **FR-4**: 编写 Context Engineering 章节，解析"瓶颈移到你给什么"（上下文窗口、context rot、渐进式披露、给得准而非给得多）
- **FR-5**: 编写 Harness Engineering 章节（重点章节），解析"瓶颈移到它干活的环境"（Mitchell Hashimoto 定义、复利效应、Agent=模型+Harness 公式、关键一跃内涵）
- **FR-6**: 编写 Loop Engineering 章节，解析"瓶颈移到你自己身上"（回合制→循环、三位点响者观点、loop 是 harness 逻辑的自然延伸）
- **FR-7**: 编写四者关系总结章节，阐明"层层包含"（Prompt ⊂ Context ⊂ Harness）与瓶颈外移终点
- **FR-8**: 编写关键人物与原话引用章节，整理四位关键人物的观点原文
- **FR-9**: 编写实践启示章节，萃取"复利式修补""环境沉淀而非脑内记忆""人的判断仍是主战场"等方法论价值
- **FR-10**: 编写常见问题解答章节
- **FR-11**: 编写相关资源链接章节（原文、引用人物相关资料、Anthropic Agent Skills 等）
- **FR-12**: 更新知识库索引（docs/knowledge/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（AI Agent 开发者/技术决策者/方法论爱好者）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据，关键原话需准确引用
- **NFR-3**: 文档结构清晰，便于阅读和导航，章节间逻辑递进
- **NFR-4**: 文档格式符合项目规范（Markdown 格式，kebab-case 命名，YAML frontmatter + x-toml-ref 引用外部 TOML）
- **NFR-5**: 技术术语准确，关键概念（context rot、渐进式披露、harness、loop）提供清晰解释
- **NFR-6**: 保持客观转述立场，不添加未在原文中出现的信息，分析与启示部分明确标注为"基于原文的延伸思考"

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，放置在 docs/knowledge/learning/ 目录下，文件名为 four-engineering-concepts-wiki.md
- **Business**: 基于公开文章内容创建，准确转述原文观点，关键原话需引用到位
- **Dependencies**: 依赖已获取的网页内容（通过 defuddle 提取），无需额外网络请求

## Assumptions
- 用户具备基本的 AI 大模型使用经验（了解 ChatGPT、Claude 等）
- 用户对 Agent 概念有基本认知
- 用户了解软件工程的基本概念（测试、钩子、规则文件等）
- 用户可以访问互联网查阅相关资源链接

## Acceptance Criteria

### AC-1: Wiki 文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: wiki 文档包含目录导航、核心论点、四个概念分章解析、关系总结、关键人物引用、实践启示、FAQ 和资源链接等完整章节
- **Verification**: `human-judgment`
- **Notes**: 文档应放置在 docs/knowledge/learning/ 目录下，文件名为 four-engineering-concepts-wiki.md

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 锚点链接实现

### AC-3: 核心论点阐述清晰
- **Given**: 用户阅读核心论点章节
- **When**: 用户理解"瓶颈外移"规律
- **Then**: 用户能够说明四个概念为何是"同一条线上四个路标"而非"四个换皮赛道"，并能复述瓶颈外移的四层路径（怎么说→给什么→干活环境→你自己）
- **Verification**: `human-judgment`
- **Notes**: 需突出规律的反直觉特点

### AC-4: Prompt Engineering 章节完整
- **Given**: 用户阅读 Prompt Engineering 章节
- **When**: 用户理解该概念
- **Then**: 用户能够说明"模型预测下一个字"的本质、"提示词配方"六要素（角色/背景/参考/任务/约束/格式）、以及该范式的适用边界（短链路一问一答）
- **Verification**: `human-judgment`

### AC-5: Context Engineering 章节完整
- **Given**: 用户阅读 Context Engineering 章节
- **When**: 用户理解该概念
- **Then**: 用户能够解释上下文窗口、context rot（上下文腐化）、渐进式披露三个关键概念，并说明"给得准而非给得多"的核心要义
- **Verification**: `human-judgment`

### AC-6: Harness Engineering 章节深度达标（重点）
- **Given**: 用户阅读 Harness Engineering 章节
- **When**: 用户理解该概念
- **Then**: 用户能够复述 Mitchell Hashimoto 的定义原话、解释"复利效应"机制、说明 Agent=模型+Harness 公式含义、并阐明"关键一跃"为何是从输入侧转向模型外部世界
- **Verification**: `human-judgment`
- **Notes**: 此章节为全文关键，需重点展开

### AC-7: Loop Engineering 章节完整
- **Given**: 用户阅读 Loop Engineering 章节
- **When**: 用户理解该概念
- **Then**: 用户能够说明"回合制→循环"的范式转变、复述三位点响者（Peter Steinberger/Addy Osmani/Boris Cherny）的观点、并解释 loop 为何是 harness 逻辑的自然延伸
- **Verification**: `human-judgment`

### AC-8: 四者关系总结准确
- **Given**: 用户阅读关系总结章节
- **When**: 用户理解四者关系
- **Then**: 用户能够说明"层层包含"（Prompt ⊂ Context ⊂ Harness）关系、瓶颈外移到"你自己"后的终点判断、以及"模型决定上限、harness 决定落地"的核心结论
- **Verification**: `human-judgment`

### AC-9: 关键人物原话引用准确
- **Given**: 用户阅读关键人物章节
- **When**: 用户查看引用内容
- **Then**: 四位关键人物（Mitchell Hashimoto/Peter Steinberger/Addy Osmani/Boris Cherny）的原话均被准确引用，并标注其身份
- **Verification**: `human-judgment`

### AC-10: 实践启示具有方法论价值
- **Given**: 用户阅读实践启示章节
- **When**: 用户理解方法论价值
- **Then**: 用户能够说出至少 3 条可执行的实践启示（如复利式修补、环境沉淀、保持人的判断）
- **Verification**: `human-judgment`

### AC-11: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面
- **Verification**: `programmatic`
- **Notes**: 至少包含原文链接和 Anthropic Agent Skills 相关资源

### AC-12: 知识库索引更新完成
- **Given**: wiki 文档创建完成
- **When**: 查看 docs/knowledge/README.md
- **Then**: 学习分类中新增本教程条目，包含标题、摘要、日期和标签
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

## Open Questions
- [ ] 是否需要为 Harness Engineering 章节单独创建原子化子文档（因其为重点且篇幅较长）？
- [ ] 是否需要在实践启示章节补充与项目已有 harness 实践（如 .agents/ 规范体系）的关联说明？
