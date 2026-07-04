# Agnes AI 与 Pavo 创作平台学习 Wiki 教程 Spec

## Why
Agnes AI 采取激进的免费策略（文本、图片、视频三个核心模型 API 全部免费开放），3周内单周 Token 调用量从 1 万亿增长到 5 万亿，图片模型一周生成 567 万张图，视频模型一周生成 237 万秒（约 650 小时）。其新产品 Pavo 是一个 PC 端 AI 创作平台，将图片生成、视频生成、短剧创作整合进一个工作流，由 Agent 总指挥，实现从想法到成片一站式完成。需要系统学习该网页内容并沉淀为一份结构清晰、通俗易懂的 wiki 教程，便于读者理解这套免费 AI 创作方案及其核心优势。

## What Changes
- 新增 wiki 教程文档 `docs/knowledge/learning/agnes-pavo-creative-platform-wiki.md`，作为 Agnes AI 与 Pavo 平台的系统性学习资料
- 文档包含目录导航系统，覆盖核心数据、四大模块、剧情短片工作流、Agent 功能、模型升级等核心内容
- 整理关键功能点、操作流程、技术亮点与实用信息
- 提供内容三维评估（专业性/准确性/时效性）与 FAQ 常见问题解答
- 汇总相关资源链接（官网、Pavo平台、API平台、开发者文档、GitHub）
- 在 `docs/knowledge/README.md` 知识库索引中登记新增的学习文档
- **BREAKING**: 无破坏性变更（纯新增文档）

## Impact
- Affected specs: 无（独立新增学习文档）
- Affected code:
  - 新增 `docs/knowledge/learning/agnes-pavo-creative-platform-wiki.md`
  - 修改 `docs/knowledge/README.md`（追加索引条目）

## Background & Context
- **产品名称**: Agnes AI（免费多模态模型API）+ Pavo（PC端AI创作平台）
- **文章来源**: 微信公众号"逛逛 GitHub"
- **核心策略**: 免费开放文本、图片、视频三个核心模型 API，撬动全网创作者和开发者
- **关键数据**: 单周调用量 5 万亿 Token、图片模型 567 万张/周、视频模型 237 万秒/周（约650小时）
- **Pavo 定位**: PC 端 AI 创作平台，整合图片/视频/短剧工作流，由 Agent 总指挥
- **核心亮点**: 剧情短片全流水线（剧本→人设→分镜→视频→成片）、Harness 框架 Agent、Agnes-Video-2.5-preview 模型升级
- **原文来源**: https://mp.weixin.qq.com/s/Gslh5H5D9hqHnHxk8GzLFQ

## ADDED Requirements

### Requirement: Wiki 教程文档主框架
系统 SHALL 提供一份 Markdown 格式的 wiki 教程文档，放置在 `docs/knowledge/learning/agnes-pavo-creative-platform-wiki.md`，文档顶部包含完整的目录导航系统，所有章节通过锚点链接支持跳转。

#### Scenario: 用户打开文档导航
- **WHEN** 用户打开 `agnes-pavo-creative-platform-wiki.md`
- **THEN** 文档顶部展示完整目录，覆盖概述与核心数据、Pavo平台介绍、四大核心模块、剧情短片工作流、Agent指挥系统、视频模型升级、社区反馈、内容评估、FAQ、资源链接等章节
- **AND** 每个目录条目是可点击的锚点链接，能跳转到对应章节

### Requirement: Agnes AI 概述与核心数据
系统 SHALL 在文档开篇阐述 Agnes AI 的免费策略与爆发式增长数据，包括：3周前免费开放三个核心模型API、首周1万亿Token、3周后单周5万亿Token、图片模型567万张/周、视频模型237万秒/周（约650小时）。

#### Scenario: 读者理解产品背景
- **WHEN** 读者阅读文档的"概述与核心数据"章节
- **THEN** 能够准确复述 Agnes AI 的免费策略
- **AND** 知晓三项核心使用数据：5万亿Token、567万张图、237万秒视频
- **AND** 理解免费策略如何撬动全网创作者和开发者

### Requirement: Pavo 平台定位介绍
系统 SHALL 详细介绍 Pavo 平台的定位：PC端AI创作平台，将图片生成、视频生成、短剧创作塞进一个工作流，由Agent当总指挥，实现从想法到成片在一个浏览器里搞定。

#### Scenario: 读者理解平台定位
- **WHEN** 读者阅读"Pavo平台概述"章节
- **THEN** 理解 Pavo 的核心价值是不用到处切工具
- **AND** 知晓平台包含四个核心模块（Agent、图片生成、视频生成、剧情短片）

### Requirement: 四大核心模块讲解
系统 SHALL 逐一讲解 Pavo 的四个核心模块：
1. Agent：一句话下需求，基于自研Harness框架
2. 图片生成：海报、商品图、写真
3. 视频生成：文生视频、图生视频
4. 剧情短片：从剧本到成片的短剧工作流

#### Scenario: 读者掌握四大模块
- **WHEN** 读者阅读"四大核心模块"章节
- **THEN** 能够列出四个模块的名称与功能定位
- **AND** 理解剧情短片模块是 Pavo 区别于其他 AI 工具的核心特色

### Requirement: 剧情短片全流水线讲解
系统 SHALL 详细讲解剧情短片模块的六步流水线工作流：剧本创作→人物和场景设定→分镜设计→角色场景配图→分镜脚本与关键帧→分镜视频生成→成片渲染。包含实际测试案例（UFO入侵场景）的流程演示。

#### Scenario: 读者掌握短剧工作流
- **WHEN** 读者按顺序阅读"剧情短片工作流"章节
- **THEN** 能够复述从一句话创意到成片的完整流程
- **AND** 理解每一步的人机交互点（需求确认→剧本确认→角色确认→配图确认→分镜确认→合成）
- **AND** 知晓适用场景（热点短剧、职场轻喜剧、情侣剧情、萌宠拟人、品牌剧情广告）
- **AND** 了解当前局限性（追求电影级质感还差点意思，需要人工介入调整）

### Requirement: Agent 指挥系统讲解
系统 SHALL 详细讲解 Pavo Agent 的功能：基于自研 Harness 框架，一句话描述需求即可自动规划步骤、调模型、出素材；支持上下文记忆与多轮对话调整，不用每次重新描述项目背景。包含香水广告案例。

#### Scenario: 读者掌握 Agent 功能
- **WHEN** 读者阅读"Agent指挥系统"章节
- **THEN** 理解 Agent 基于 Harness 框架实现任务自动拆解
- **AND** 知晓一句话即可跑完广告片制作流程
- **AND** 理解上下文记忆功能的价值（多轮调整无需重复描述背景）

### Requirement: Agnes-Video-2.5-preview 模型升级
系统 SHALL 讲解视频模型升级的核心改进点：生成速度提升一倍、运镜更流畅（减少僵硬突兀）、物理规律还原增强（减少漂浮/穿模/不自然碰撞）、新增多参考图能力（人物商品保持一致）、字幕乱码改善。

#### Scenario: 读者理解模型升级
- **WHEN** 读者阅读"视频模型升级"章节
- **THEN** 能够列出五项核心改进
- **AND** 理解这些升级瞄准批量生产场景（广告投放、短视频矩阵）

### Requirement: 社区反馈与已知问题
系统 SHALL 客观呈现社区反馈的问题：首Token响应时间有时不理想、图片模型高峰期偶发503、Codex等客户端接入配置不当问题；同时说明Agnes公开GitHub Issues和Projects看板的透明化做法。

#### Scenario: 读者了解已知问题
- **WHEN** 读者阅读"社区反馈"章节
- **THEN** 知晓当前存在的三个主要问题
- **AND** 理解开源透明化的bug跟踪方式

### Requirement: 核心信息汇总表
系统 SHALL 整理 Agnes AI 与 Pavo 的关键信息为表格形式，包含：类别、关键数据/功能、备注说明。

#### Scenario: 数据可快速查阅
- **WHEN** 读者查阅核心信息汇总表
- **THEN** 能够快速对比核心数据、功能模块、模型升级点、适用场景

### Requirement: 内容三维评估章节
系统 SHALL 对网页内容进行三维评估：
1. **专业性**：基于实际产品体验，功能描述具体可验证
2. **准确性**：数据明确（5万亿Token等），但属于产品推广文章，存在宣传倾向
3. **时效性**：文章发布于近期（Agnes-Video-2.5-preview即将上线阶段），信息较新
同时评估实用价值与潜在局限性。

#### Scenario: 读者了解内容可信度
- **WHEN** 读者阅读"内容评估"章节
- **THEN** 能够从专业/准确/时效三个维度判断信息价值
- **AND** 知晓哪些信息可通过官网体验验证，哪些需要进一步考证
- **AND** 理解免费策略对创作者和开发者的实际价值

### Requirement: FAQ 常见问题解答
系统 SHALL 提供 FAQ 章节，解答读者学习 Agnes AI 与 Pavo 时可能遇到的常见问题。

#### Scenario: 读者疑问被解答
- **WHEN** 读者查阅 FAQ
- **THEN** 至少覆盖以下问题：Agnes AI 真的完全免费吗、Pavo 如何访问、剧情短片能达到什么质量水平、Agent 支持哪些类型的创作任务、与其他AI视频工具的差异、适合什么用户群体、API如何接入

### Requirement: 资源链接汇总
系统 SHALL 在文档末尾汇总所有相关资源链接，包括：原文链接、Agnes官网、Pavo平台地址、API平台、开发者文档、GitHub Issues看板、GitHub Projects看板。

#### Scenario: 链接有效可达
- **WHEN** 用户点击资源链接
- **THEN** 链接指向正确的资源页面
- **AND** 链接以 Markdown 标准链接格式呈现

### Requirement: 知识库索引登记
系统 SHALL 在 `docs/knowledge/README.md` 的学习类目下登记新增的 Agnes Pavo 学习文档条目。

#### Scenario: 索引可发现
- **WHEN** 用户浏览 `docs/knowledge/README.md`
- **THEN** 能够在 learning 类目下看到 Agnes Pavo 学习 wiki 的条目
- **AND** 条目包含文档标题与相对路径链接

## Non-Functional Requirements
- **NFR-1**: 文档语言使用标准现代汉语，逻辑严谨，对不同技术水平的读者友好
- **NFR-2**: 在适当位置引用原网页内容作为参考依据，不添加未经验证的信息
- **NFR-3**: 文档结构清晰，使用 Markdown 标准标题层级（H1/H2/H3）、列表、表格、引用块
- **NFR-4**: 文件命名遵循 kebab-case 纯英文规范（`agnes-pavo-creative-platform-wiki.md`），通过 `python .agents/scripts/check-filename-convention.py` 校验
- **NFR-5**: 文档篇幅适中（预估 3000–5000 字），重点突出，避免冗余
- **NFR-6**: 客观呈现产品优缺点，不回避已知问题

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，frontmatter 使用 YAML 格式
- **Business**: 基于公开文章内容创建，不得添加未验证的推测性信息
- **Dependencies**: 网页内容已通过 defuddle 工具成功获取并解析

## Assumptions
- 读者对 AI 生成内容（AIGC）有基础认知
- 读者可以访问互联网体验 Pavo 平台与 Agnes 官网
- 读者对 AI 创作工具或短剧制作有兴趣或需求

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: `docs/knowledge/learning/agnes-pavo-creative-platform-wiki.md` 包含目录导航、概述数据、平台介绍、四大模块、剧情短片工作流、Agent系统、模型升级、社区反馈、内容评估、FAQ、资源链接等完整章节
- **Verification**: `human-judgment`

### AC-2: 核心数据完整准确
- **Given**: 用户阅读概述章节
- **When**: 用户查阅核心数据
- **Then**: 包含 5万亿Token、567万张图、237万秒视频三项关键数据
- **Verification**: `human-judgment`

### AC-3: 剧情短片六步工作流清晰
- **Given**: 用户阅读剧情短片章节
- **When**: 用户理解工作流
- **Then**: 用户能够复述从剧本创作到成片渲染的完整流程，包含人机交互确认节点
- **Verification**: `human-judgment`

### AC-4: Agent 功能讲解完整
- **Given**: 用户阅读 Agent 章节
- **When**: 用户理解 Harness 框架与多轮记忆
- **Then**: 用户能够阐述 Agent 的自动任务拆解与上下文记忆能力
- **Verification**: `human-judgment`

### AC-5: 模型升级点完整
- **Given**: 用户阅读模型升级章节
- **When**: 用户查阅五项改进
- **Then**: 速度翻倍、运镜流畅、物理还原、多参考图、字幕改善五项改进均有说明
- **Verification**: `human-judgment`

### AC-6: 内容三维评估客观
- **Given**: 用户阅读内容评估章节
- **When**: 用户了解文章性质
- **Then**: 用户能够从专业性、准确性、时效性三个维度评估信息价值，知晓推广倾向
- **Verification**: `human-judgment`

### AC-7: FAQ 章节实用
- **Given**: 用户遇到疑问
- **When**: 用户查阅 FAQ
- **Then**: 至少 7 个常见问题被解答
- **Verification**: `human-judgment`

### AC-8: 资源链接完整
- **Given**: 用户点击资源链接
- **When**: 用户访问链接
- **Then**: 包含原文、官网、Pavo、API平台、文档、GitHub Issues、GitHub Projects共7类链接
- **Verification**: `human-judgment`

### AC-9: 知识库索引已登记
- **Given**: wiki 文档创建完成
- **When**: 用户浏览 `docs/knowledge/README.md`
- **Then**: learning 类目下出现 Agnes Pavo 学习文档条目
- **Verification**: `programmatic`

### AC-10: 文件命名规范合规
- **Given**: wiki 文档创建完成
- **When**: 运行 `python .agents/scripts/check-filename-convention.py`
- **Then**: `agnes-pavo-creative-platform-wiki.md` 通过命名规范校验
- **Verification**: `programmatic`

### AC-11: 已知问题客观呈现
- **Given**: 用户阅读社区反馈章节
- **When**: 用户了解局限性
- **Then**: 首Token延迟、503错误、客户端配置三个问题均有说明
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要在文档中加入 Mermaid 流程图来可视化剧情短片的六步工作流？（倾向：加入 1 张图增强可读性）
- [ ] 是否需要对比 Pavo 与 LibTV 等同类 AI 短剧工具的差异？（倾向：在FAQ中简要对比，不单独开章节）
