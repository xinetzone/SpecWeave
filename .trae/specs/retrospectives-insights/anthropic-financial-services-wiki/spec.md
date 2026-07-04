# Anthropic Financial Services 金融Agent仓库 Wiki教程 - Product Requirement Document

## Overview
- **Summary**: 系统学习并整理微信公众号文章介绍的Anthropic官方financial-services仓库（GitHub 3.2万Star），这是一套面向金融服务行业的Claude工作流模板，涵盖投行、股票研究、私募股权、财富管理四大垂直领域。本Wiki将系统解析其四层架构设计（Agent/Skill/Slash Command/MCP Connector）、10大核心功能模块、快速上手步骤、企业定制化方法及法律免责声明，为AI Agent在金融垂直领域落地提供参考样板。
- **Purpose**: 帮助读者理解Anthropic官方如何设计垂直行业Agent解决方案，学习金融Agent的架构分层思想、Skill标准化方法、Slash Command工作流设计、MCP数据集成模式，以及企业级部署（Managed Agents）的正确思路。
- **Target Users**: AI Agent开发者、金融科技从业者、Claude生态使用者、企业级AI应用架构师、对垂直行业Agent落地感兴趣的技术人员。

## Goals
- 完整提取并系统梳理原文核心观点、10大功能模块详解、关键术语
- 清晰解释金融领域专业术语（DCF/LBO/comps/三表模型/KYC/GL对账等）
- 提供可复现的快速上手安装步骤和插件选择建议
- 客观说明该仓库的定位（模板而非成品）、局限性和企业定制化路径
- 补充内容三维评估（准确性/权威性/实用性）和个人见解
- 整理FAQ和相关资源链接（GitHub仓库、Anthropic官方文档等）

## Non-Goals (Out of Scope)
- 不提供金融投资建议或任何金融专业意见
- 不深入讲解金融建模理论（DCF/LBO等仅作概念解释）
- 不破解或绕过FactSet/PitchBook等付费数据源
- 不开发可直接运行的金融分析代码
- 不保证该仓库未来版本的兼容性

## Background & Context
- **资源来源**: 微信公众号「极客之家」文章，介绍Anthropic官方GitHub仓库 anthropics/financial-services
- **仓库数据**: GitHub 3.2万 Star，由Anthropic官方发布和维护
- **行业背景**: 金融是AI Agent落地的重点垂直领域，但金融行业对合规、审计、准确性要求极高，不能简单用通用聊天机器人
- **技术背景**: 该仓库展示了Anthropic推荐的垂直行业Agent最佳实践：四层架构 + 插件化 + 企业级部署 + 办公软件入口
- **关键洞察**: 文章反复强调"这是模板不是产品"，需要企业投入定制化、对接数据源、建立人工审核机制——这是垂直行业Agent落地的真实路径，而非"开箱即用"的神话

## Functional Requirements
- **FR-1**: 提供完整的目录导航系统，包含11个主要章节
- **FR-2**: 系统介绍项目背景、定位（AI金融工具箱而非聊天页面）、核心价值
- **FR-3**: 清晰解释四层架构（Agent/Skill/Slash Command/MCP Connector）
- **FR-4**: 详解10大功能模块：Pitch Agent、financial-analysis、Skill系统、Slash Command、equity-research、GL Reconciler、KYC Screener、MCP Connector、Managed Agents、Microsoft 365集成
- **FR-5**: 提供分步骤的快速上手指南，包含插件安装顺序建议和避坑提示
- **FR-6**: 说明项目源码结构导航（不同学习目的该看哪些目录）
- **FR-7**: 详细讲解5种企业定制化方法：换数据连接器、加公司上下文、用自己的模板、调整代理范围、加自定义工作流
- **FR-8**: 突出法律免责声明和人工审核要求的重要性
- **FR-9**: 包含内容三维评估（准确性/权威性/实用性）
- **FR-10**: 提供个人理解与见解章节，分析该项目对Agent行业的启示
- **FR-11**: 整理FAQ（8个读者可能遇到的问题）
- **FR-12**: 提供相关资源链接（GitHub仓库、相关Wiki等）

## Non-Functional Requirements
- **NFR-1**: 语言通俗易懂，金融术语需配解释，适合不同技术水平读者
- **NFR-2**: 结构逻辑清晰，遵循"概述→架构→功能→上手→定制→评估→FAQ→资源"递进关系
- **NFR-3**: 客观中立，明确说明局限性，不夸大功能
- **NFR-4**: 所有安装命令可直接复制使用
- **NFR-5**: 严格遵守法律免责声明，不构成任何投资建议
- **NFR-6**: frontmatter使用YAML格式（---分隔），字段完整
- **NFR-7**: 文件名使用kebab-case，纯英文无中文

## Constraints
- **Technical**: 基于Claude CLI插件系统，需要Claude订阅才能使用完整功能；MCP连接器大多需要付费金融数据源API Key
- **Business**: 金融行业合规要求严格，所有输出必须人工审核；不构成投资/法律/税务建议
- **Dependencies**: anthropics/financial-services GitHub仓库、Claude CLI、（可选）金融数据服务商API

## Assumptions
- 读者具备基础的AI Agent概念和Markdown阅读能力
- 读者对金融领域有基本认知，或愿意通过术语解释理解相关概念
- 原文内容准确反映了该GitHub仓库的实际情况
- 单文件Wiki形式适合本主题（预计250-320行，章节关联性强）

## Acceptance Criteria

### AC-1: 内容完整性
- **Given**: 已完成Wiki文档生成
- **When**: 对照原文和需求清单检查
- **Then**: 六大要素齐全（概述/核心概念/操作指南/FAQ/资源链接/学习目标），10大功能模块无遗漏，关键术语均有解释
- **Verification**: `human-judgment`

### AC-2: 格式规范
- **Given**: Wiki文档已创建
- **When**: 检查frontmatter和文件格式
- **Then**: frontmatter使用YAML（---），title/source/date/tags字段完整；文件名符合kebab-case规范；无中文文件名
- **Verification**: `programmatic` + `human-judgment`

### AC-3: 快速上手可复现
- **Given**: Wiki中提供的安装命令
- **When**: 有Claude CLI环境的读者按步骤操作
- **Then**: 命令语法正确，插件安装顺序建议清晰，避坑提示明确
- **Verification**: `human-judgment`

### AC-4: 局限性客观真实
- **Given**: Wiki中的局限性和注意事项章节
- **When**: 读者阅读
- **Then**: 明确说明"模板而非产品"的定位，MCP连接器非免费数据源，所有输出需人工审核，不构成投资建议
- **Verification**: `human-judgment`

### AC-5: 法律免责声明突出
- **Given**: Wiki文档
- **When**: 查看免责声明部分
- **Then**: 明确标注Anthropic官方免责内容，强调人工审核责任
- **Verification**: `human-judgment`

### AC-6: 资源链接有效
- **Given**: Wiki中的资源链接
- **When**: 点击验证
- **Then**: GitHub仓库链接正确，相关Wiki链接使用相对路径
- **Verification**: `programmatic`

## Open Questions
- 无。原始文章内容完整清晰，需求明确。

## 信息架构设计

### 章节划分（单文件Wiki）

| 章节 | 标题 | 核心内容 |
|------|------|---------|
| 一 | 项目概述与背景 | GitHub 3.2万Star、Anthropic官方出品、四大金融垂直领域覆盖 |
| 二 | 核心定位与四层架构 | Agent/Skill/Slash Command/MCP Connector四层设计，不是空壳AI助手 |
| 三 | 十大核心功能模块详解 | Pitch Agent到Microsoft 365集成，每个模块的价值和适用场景 |
| 四 | 快速上手指南 | 插件市场添加、核心插件安装、顺序建议、避坑提示 |
| 五 | 源码结构与学习路径 | 不同学习目的该看哪些目录 |
| 六 | 企业定制化方法 | 5种定制方式：数据连接器/公司上下文/模板/代理范围/自定义工作流 |
| 七 | 法律免责与人工审核 | 强调draft定位、人工签字责任、合规要求 |
| 八 | 内容三维评估 | 准确性/权威性/实用性评分与说明 |
| 九 | 个人见解与行业启示 | 对垂直行业Agent落地的思考 |
| 十 | 常见问题FAQ | 8个高频问题解答 |
| 十一 | 相关资源链接 | GitHub仓库、相关学习资源 |

### 逻辑组织方式
- [x] 线性递进（适合教程类）：从是什么→架构→功能→怎么用→怎么改→注意事项→评估→见解→FAQ→资源

### 原子化决策

| 判断维度 | 拆分阈值 | 本wiki预估 |
|---------|---------|-----------|
| 内容长度 | 预计&gt;300行建议拆分，&lt;200行可保持单文件 | 预计约280-320行 |
| 章节独立性 | 各章节是否可单独阅读/引用？ | 否，章节间逻辑递进强 |
| 未来扩展 | 是否预期会持续新增章节/内容？ | 否，基于单篇文章 |
| 复用需求 | 单个章节是否会被其他文档引用？ | 可能性低 |

**决策结果**：
- [x] **保持单文件**：所有内容在一个md文件中，不进入原子化拆分阶段。理由：内容基于单篇文章，章节关联性强，预计篇幅约300行左右，单文件阅读体验更佳。
