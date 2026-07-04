# LibTV AI 短剧创作工具学习 Wiki 教程 Spec

## Why
AI 漫剧普遍存在人物缺少真人质感、有"AI 味"的痛点，LibTV（liblib.tv）针对该问题推出了人像调节、情绪调节、虚拟角色、新版脚本、3D 导演台等一系列功能，大幅降低 AI 短剧创作门槛。需要系统学习该网页内容并沉淀为一份结构清晰、通俗易懂的 wiki 教程，便于不同技术水平的读者快速理解这套 AI 短剧创作方案，并为后续应用或讨论提供参考。

## What Changes
- 新增 wiki 教程文档 `docs/knowledge/learning/libtv-ai-shortdrama-wiki.md`，作为 LibTV 工具的系统性学习资料
- 文档包含目录导航系统，覆盖五大核心功能的递进式讲解
- 整理关键功能点、操作流程、技术亮点与实用信息
- 提供 FAQ 常见问题解答与相关资源链接
- 对网页内容的准确性、权威性与实用性进行评估
- 在 `docs/knowledge/README.md` 知识库索引中登记新增的学习文档
- **BREAKING**: 无破坏性变更（纯新增文档）

## Impact
- Affected specs: 无（独立新增学习文档）
- Affected code:
  - 新增 `docs/knowledge/learning/libtv-ai-shortdrama-wiki.md`
  - 修改 `docs/knowledge/README.md`（追加索引条目）

## Background & Context
- **工具名称**: LibTV（官网 liblib.tv）
- **文章作者**: 阿枫（公众号）
- **核心问题**: AI 视频模型生成的人物缺少真人质感，10 部 AI 漫剧中 8 部存在"AI 味"，根源在于缺少对人物细节的掌控
- **解决思路**: 用可视化按钮替代专业提示词，让新手也能生成有质感的人物与短剧
- **成功案例**: 《荒年开局：我靠空间当大佬》登顶抖音漫剧榜日榜第一，全网收获 7 亿播放量
- **原文来源**: https://mp.weixin.qq.com/s/PEHYzcSbDdwPYF0VGo-DDA

## ADDED Requirements

### Requirement: Wiki 教程文档主框架
系统 SHALL 提供一份 Markdown 格式的 wiki 教程文档，放置在 `docs/knowledge/learning/libtv-ai-shortdrama-wiki.md`，文档顶部包含完整的目录导航系统，所有章节通过锚点链接支持跳转。

#### Scenario: 用户打开文档导航
- **WHEN** 用户打开 `libtv-ai-shortdrama-wiki.md`
- **THEN** 文档顶部展示完整目录，覆盖核心问题、五大功能、操作流程、技术亮点、FAQ、资源链接等章节
- **AND** 每个目录条目是可点击的锚点链接，能跳转到对应章节

### Requirement: 核心问题与背景阐述
系统 SHALL 在文档开篇阐述 LibTV 要解决的核心问题：AI 漫剧人物缺少真人质感，以及该问题的根源（缺少对人物细节的掌控、新手难以掌握专业提示词）。

#### Scenario: 读者理解问题背景
- **WHEN** 读者阅读文档的"核心问题"章节
- **THEN** 能够准确复述"10 部 AI 漫剧中 8 部有 AI 味"的现状
- **AND** 理解问题根源不是模型能力不足，而是用户缺少对人物细节的掌控

### Requirement: 人像调节功能讲解
系统 SHALL 详细讲解 LibTV 的人像调节功能，包括：功能定位、使用方式（图片生成前/后均可使用）、可调节参数（皮肤质感、纹理、光影等）、与"大白话提示词"的对比效果。

#### Scenario: 读者掌握人像调节
- **WHEN** 读者阅读"人像调节"章节
- **THEN** 理解该功能通过预设按钮封装大量专业提示词
- **AND** 知晓如何在图片节点下方找到"预设"按钮并进入"人像质感调节"界面
- **AND** 理解已生成的图片也可通过左上角按钮增强人物质感

### Requirement: 情绪调节功能讲解
系统 SHALL 详细讲解 LibTV 的情绪调节功能，包括：十字无极调节方式的设计理念、四个方向的情绪含义（上=激动、下=平静、左=亲近、右=疏离）、复杂情绪的组合原理、调节效果的前后对比。

#### Scenario: 读者掌握情绪调节
- **WHEN** 读者阅读"情绪调节"章节
- **THEN** 理解系统会自动识别图片中的所有人脸
- **AND** 理解十字无极调节方式如何通过两两组合演变出复杂表情（如左上角=难以置信→欣然喜悦）
- **AND** 知晓调节表情时其他元素不会被改变

### Requirement: 虚拟角色功能讲解
系统 SHALL 详细讲解 LibTV 的虚拟角色库功能，包括：角色官方优化特点（皮肤光滑水润但保留小颗粒）、首批上线角色数量（20+）、覆盖人物类型、入口位置（下方工具栏）、与短剧场景的适配关系。

#### Scenario: 读者掌握虚拟角色
- **WHEN** 读者阅读"虚拟角色"章节
- **THEN** 知晓首批上线了 20 多个角色，几乎涵盖各个类型的人物
- **AND** 理解角色质感经过官方优化，符合真实人物皮肤状态
- **AND** 知晓该功能专为短剧场景准备，可快速复用有质感的角色

### Requirement: 新版脚本工具讲解
系统 SHALL 详细讲解新版脚本工具的完整工作流程，包括：文本节点生成大纲、脚本节点生成脚本、自动标注人物/场景/台词/道具、一键生成角色设定图、一键生成提示词、批量生成视频。

#### Scenario: 读者掌握新版脚本工作流
- **WHEN** 读者按顺序阅读"新版脚本"章节
- **THEN** 能够理解完整的六步工作流：创意输入→大纲生成→脚本生成→角色设定→提示词生成→批量视频生成
- **AND** 知晓整个流程不需要手搓提示词，只需点几下鼠标
- **AND** 理解角色可以从画布已有角色中添加（如虚拟角色库中的角色）

### Requirement: 3D 导演台功能讲解
系统 SHALL 详细讲解 3D 导演台功能，包括：功能定位（解决复杂站位难以用语言描述的问题）、添加角色与形状、3D 空间位置调整、摄像机视角选择、截图与发送到画布、参考图与视频生成的关联。

#### Scenario: 读者掌握 3D 导演台
- **WHEN** 读者阅读"3D 导演台"章节
- **THEN** 理解该功能通过 3D 空间调整角色站位，产出参考图供视频生成模型参考
- **AND** 知晓无需 3D 软件基础即可上手（一秒上手）
- **AND** 理解参考图可以指定每种颜色角色对应的具体人物

### Requirement: 关键功能对比与数据汇总
系统 SHALL 整理 LibTV 五大功能的关键信息为表格形式，包含：功能名称、解决的核心问题、使用方式、技术亮点、适用场景。

#### Scenario: 数据可追溯
- **WHEN** 读者查阅功能汇总表
- **THEN** 能够快速对比五大功能的定位与使用场景
- **AND** 包含成功案例数据（如《荒年开局》7 亿播放量、抖音漫剧榜日榜第一）

### Requirement: 内容评估章节
系统 SHALL 对网页内容的准确性、权威性与实用性进行评估，包括：信息来源可靠性、功能描述可验证性、实用价值判断、潜在局限性。

#### Scenario: 读者了解内容可信度
- **WHEN** 读者阅读"内容评估"章节
- **THEN** 能够了解该文章属于产品介绍性质，存在推广倾向
- **AND** 知晓哪些信息可通过官网体验验证，哪些需要进一步考证
- **AND** 理解该工具对新手与老手的不同价值

### Requirement: FAQ 常见问题解答
系统 SHALL 提供 FAQ 章节，解答读者学习 LibTV 时可能遇到的常见问题。

#### Scenario: 读者疑问被解答
- **WHEN** 读者查阅 FAQ
- **THEN** 至少覆盖以下问题：LibTV 适合什么用户、是否需要专业提示词基础、人像调节与情绪调节能否叠加、3D 导演台是否需要 3D 基础、如何快速上手短剧制作、与同类工具的差异

### Requirement: 资源链接汇总
系统 SHALL 在文档末尾汇总所有相关资源链接，包括原文、官网、成功案例等。

#### Scenario: 链接有效可达
- **WHEN** 用户点击资源链接
- **THEN** 链接指向正确的资源页面（原文、官网）
- **AND** 链接以 Markdown 标准链接格式呈现

### Requirement: 知识库索引登记
系统 SHALL 在 `docs/knowledge/README.md` 的学习类目下登记新增的 LibTV 学习文档条目。

#### Scenario: 索引可发现
- **WHEN** 用户浏览 `docs/knowledge/README.md`
- **THEN** 能够在 learning 类目下看到 LibTV 学习 wiki 的条目
- **AND** 条目包含文档标题与相对路径链接

## Non-Functional Requirements
- **NFR-1**: 文档语言使用标准现代汉语，逻辑严谨，对不同技术水平的读者友好
- **NFR-2**: 在适当位置引用原网页内容作为参考依据，不添加未经验证的信息
- **NFR-3**: 文档结构清晰，使用 Markdown 标准标题层级（H1/H2/H3）、列表、表格、引用块
- **NFR-4**: 文件命名遵循 kebab-case 纯英文规范（`libtv-ai-shortdrama-wiki.md`），通过 `python .agents/scripts/check-filename-convention.py` 校验
- **NFR-5**: 文档篇幅适中（预估 3000–5000 字），重点突出，避免冗余

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范与原子化原则
- **Business**: 基于公开文章内容创建，不得添加未验证的推测性信息
- **Dependencies**: 网页内容已通过 defuddle 工具成功获取并解析

## Assumptions
- 读者对 AI 视频生成有基础认知
- 读者可以访问互联网体验 LibTV 官网
- 读者对短剧创作有兴趣或需求

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: `docs/knowledge/learning/libtv-ai-shortdrama-wiki.md` 包含目录导航、核心问题、五大功能、功能汇总、内容评估、FAQ、资源链接等完整章节
- **Verification**: `human-judgment`

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录包含所有章节的锚点链接，点击可跳转
- **Verification**: `programmatic`

### AC-3: 五大功能讲解完整
- **Given**: 用户阅读功能章节
- **When**: 用户按顺序阅读人像调节、情绪调节、虚拟角色、新版脚本、3D 导演台
- **Then**: 用户能够阐述每个功能的定位、使用方式与技术亮点
- **Verification**: `human-judgment`

### AC-4: 新版脚本工作流清晰
- **Given**: 用户阅读新版脚本章节
- **When**: 用户理解六步工作流
- **Then**: 用户能够复述从创意输入到批量视频生成的完整流程
- **Verification**: `human-judgment`

### AC-5: 功能汇总表可追溯
- **Given**: 用户查阅功能汇总表
- **When**: 用户检查每个功能条目
- **Then**: 表格包含功能名称、解决问题、使用方式、技术亮点、适用场景五列
- **Verification**: `human-judgment`

### AC-6: 内容评估客观
- **Given**: 用户阅读内容评估章节
- **When**: 用户了解文章性质
- **Then**: 用户能够区分哪些信息可验证、哪些需要考证
- **Verification**: `human-judgment`

### AC-7: FAQ 章节实用
- **Given**: 用户遇到疑问
- **When**: 用户查阅 FAQ
- **Then**: 至少 6 个常见问题被解答
- **Verification**: `human-judgment`

### AC-8: 资源链接有效
- **Given**: 用户点击资源链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面（原文、官网）
- **Verification**: `programmatic`

### AC-9: 知识库索引已登记
- **Given**: wiki 文档创建完成
- **When**: 用户浏览 `docs/knowledge/README.md`
- **Then**: learning 类目下出现 LibTV 学习文档条目
- **Verification**: `programmatic`

### AC-10: 文件命名规范合规
- **Given**: wiki 文档创建完成
- **When**: 运行 `python .agents/scripts/check-filename-convention.py`
- **Then**: `libtv-ai-shortdrama-wiki.md` 通过命名规范校验
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在文档中加入 Mermaid 流程图来可视化新版脚本的六步工作流？（倾向：加入 1 张图增强可读性）
- [ ] 是否需要为情绪调节的十字无极调节方式绘制示意图？（倾向：用文字描述配合表格说明即可，避免绘制不准确的示意图）
