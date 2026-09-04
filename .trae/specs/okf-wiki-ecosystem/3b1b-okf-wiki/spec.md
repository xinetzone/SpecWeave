---
id: "3b1b-okf-wiki"
title: "3Blue1Brown 生态 OKF Wiki 教程生成"
source: "User Request"
---

# 3Blue1Brown 生态 OKF Wiki 教程生成 - Product Requirement Document

## Overview
- **Summary**: 使用 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）和 seven-concepts 方法论编排，系统学习 `external/dao/action/3b1b/` 目录下 4 个 3Blue1Brown 子项目（manim、videos、caption_ops、3Blue1Brown.com）的源码，并在 `projects/awesome-okf-xs/doc/bundles/` 下生成符合 OKF v0.2 规范的结构化中文 Wiki 教程。新增 `viz/` 技术域（数学可视化与创意编程）和 `viz/3b1b/` 分组来组织这些知识包。
- **Purpose**: 3Blue1Brown（Grant Sanderson）是数学可视化领域的标杆，其 Manim 动画引擎和视频创作工作流具有极高的学习价值。通过系统化的源码阅读与 OKF 知识包沉淀，为中文社区提供可溯源、结构清晰的 Manim 数学动画引擎与 3Blue1Brown 内容创作生态中文教程。
- **Target Users**: 数学可视化爱好者、Manim 动画引擎学习者、Python 创意编程开发者、教育技术工作者、对 3Blue1Brown 视频制作技术感兴趣的开发者。

## Goals
- 为 `external/dao/action/3b1b/manim`（ManimGL 动画引擎）生成完整 OKF 知识包，覆盖核心架构、动画系统、Mobject 对象模型、相机与渲染、配置系统、着色器等模块
- 为 `external/dao/action/3b1b/videos`（3Blue1Brown 视频场景源码）生成 OKF 知识包，覆盖场景组织模式、自定义组件、数学可视化实践、工作流技巧
- 为 `external/dao/action/3b1b/caption_ops`（字幕处理工具集）生成 OKF 知识包，覆盖字幕转录、翻译、时间轴调整、批量处理工作流
- 为 `external/dao/action/3b1b/3Blue1Brown.com`（官方网站）生成 OKF 知识包，覆盖 React Router v7 框架模式、MDX 数学内容处理、MathJax 集成、Tailwind v4 样式体系
- 在 awesome-okf-xs 中新增 `viz/` 技术域与 `viz/3b1b/` 分组，更新相关索引文件
- 所有知识包遵循 source-code-to-okf-wiki 规范：事实可溯源、无虚构 API、结构完整（concepts/examples/references/spec）、通过 V 阶段 Grep 验证

## Non-Goals (Out of Scope)
- 不生成 Manim Community Edition（manimCommunity/manim）的文档，仅覆盖 3b1b 原始版本 ManimGL
- 不翻译 3Blue1Brown 视频内容本身，仅生成代码/技术层面的 Wiki 教程
- 不对源码进行任何修改或重构（只读分析）
- 不生成视频内容或字幕成品，仅分析 caption_ops 工具的使用方式与代码结构
- 不深度分析 bucket/ 目录（3Blue1Brown.com 的云存储同步脚本）的运维细节

## Background & Context
- **源码位置**: `d:\spaces\SpecWeave\external\dao\action\3b1b\`，包含 4 个独立 git 仓库：
  1. `manim/` — ManimGL（3b1b 版）数学动画引擎核心，Python 包名 `manimgl`，核心代码在 `manimlib/` 下
  2. `videos/` — 3Blue1Brown 历年视频场景源码（2015-2018+），基于 ManimGL 构建，含大量自定义组件和数学可视化实践
  3. `caption_ops/` — 字幕/转录/翻译工具集，Python 脚本集合，用于 YouTube 字幕自动化处理
  4. `3Blue1Brown.com/` — 官方网站源码，使用 Bun + React 19 + React Router v7（框架模式）+ Vite + Tailwind v4 + MDX + MathJax 技术栈
- **目标位置**: `d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\`
- **现有分类**: 当前 awesome-okf-xs 有 10 个技术域（ai/build/comm/data/document/meta/ml/python/think/web），无专门的可视化/创意编程分类
- **OKF 规范**: 遵循 OKF v0.2，每个知识包含 concepts/、examples/、references/、spec/（facts.md+insights.md）、index.md、log.md

## Functional Requirements
- **FR-1**: manim 知识包生成
  - R 阶段：逐模块阅读 `manimlib/` 核心代码（animation、camera、mobject、renderer、scene、shaders、utils、config.py 等），提取编号事实清单
  - I 阶段：提炼 3-5 个核心架构洞察
  - E 阶段：生成 references/（信源登记）、concepts/（核心概念文档，按学习路径排序）、examples/（关键使用示例）、各级 index.md、log.md
  - 核心覆盖：Mobject 对象体系、Animation 动画机制、Scene 场景生命周期、Camera 相机系统、Renderer 渲染管线（含 GPU/Shader）、配置系统、LaTeX 支持

- **FR-2**: videos 知识包生成
  - R 阶段：分析目录结构（按年份组织 _2015/_2016/_2017/_2018/）、典型视频项目结构、自定义扩展（custom/ 目录）、常用模式
  - I 阶段：提炼场景组织模式、自定义组件复用模式、数学可视化实践洞察
  - E 阶段：生成 concepts/（场景结构、工作流、自定义组件模式）、examples/（典型视频场景拆解）、references/（核心工具文件）
  - 核心覆盖：InteractiveScene 交互式开发模式、checkpoint_paste 工作流、PiCreature 角色系统、常用数学可视化组件

- **FR-3**: caption_ops 知识包生成
  - R 阶段：分析核心脚本（transcribe.py、translate.py、gpt_translate.py、srt_ops.py、download.py、upload.py 等）、数据流与工具链
  - I 阶段：提炼字幕处理工作流洞察
  - E 阶段：生成 concepts/（字幕处理管线、SRT 操作、转录/翻译流程）、examples/（典型使用场景）、references/（核心脚本信源）

- **FR-4**: 3Blue1Brown.com 知识包生成
  - R 阶段：分析 app/ 目录结构（api/components/data/pages/util）、路由系统、MDX 配置、MathJax 集成、组件体系
  - I 阶段：提炼 React Router v7 框架模式、MDX+MathJax 数学内容方案洞察
  - E 阶段：生成 concepts/（项目架构、路由与页面、组件系统、MDX 数学内容处理、样式体系）、examples/（典型页面模式）、references/（核心配置与组件）

- **FR-5**: 新增 viz/ 技术域与索引更新
  - 创建 `doc/bundles/viz/` 目录及其 index.md
  - 创建 `doc/bundles/viz/3b1b/` 目录及其 index.md
  - 更新 `doc/bundles/index.md`，在十域导航中添加 viz 域
  - 确保所有新增目录通过 toctree 完整性检查

## Non-Functional Requirements
- **NFR-1**: 所有代码引用必须可溯源——每个类名、方法名、API 签名必须通过 Grep 在源码中验证存在性，禁止虚构
- **NFR-2**: 文档格式严格遵循 OKF v0.2 规范——frontmatter 完整、目录结构正确、交叉链接使用 `/` 开头 bundle-relative 路径
- **NFR-3**: 中文撰写，英文技术术语首次出现时附原文括号注释；文件名使用 kebab-case
- **NFR-4**: 每个知识包 V 阶段必须运行 `invoke gates.toctrees` 和 `invoke gates.utf8` 验证通过
- **NFR-5**: 事实采集阶段零推测——facts.md 中只记录"代码里有什么"，不出现"用于"/"目的是"等推断词

## Constraints
- **Technical**:
  - Python 3.14+ 环境（awesome-okf-xs 使用 py314 conda 环境）
  - 遵循 awesome-okf-xs 的 Invoke 任务体系（`invoke build`、`invoke gates.*`）
  - 源码为只读分析，不修改 external/ 下任何文件
  - Windows 环境路径分隔符注意事项（Grep 命令中使用 `/` 或正确转义）
- **Business**: 无特殊时间/预算约束，质量优先
- **Dependencies**:
  - source-code-to-okf-wiki Skill（五阶段工作流方法论）
  - seven-concepts-cmd Skill（方法论编排，识别为知识沉淀场景 R→I→E）
  - awesome-okf-xs 现有构建与质量门工具链

## Assumptions
- `external/dao/action/3b1b/` 下 4 个子目录均已正确克隆/初始化，源码可读
- awesome-okf-xs 子项目已正确初始化，`invoke` 命令可用
- 现有 OKF 知识包（如 ncnn、lplb）可作为格式与结构参考模板
- videos/ 目录下代码因版本较老（2015-2018）可能与当前 ManimGL 不完全兼容，文档中需标注版本差异
- 3Blue1Brown.com 使用较新技术栈（React 19、React Router v7 框架模式、Tailwind v4），文档中需注意版本特性

## Acceptance Criteria

### AC-1: manim 知识包结构完整且内容准确
- **Given**: manim 源码在 `external/dao/action/3b1b/manim/` 可读
- **When**: 完成 R→I→E→V 四阶段流程
- **Then**: 
  - `doc/bundles/viz/3b1b/manim/` 目录存在，包含 index.md、log.md、concepts/、examples/、references/、spec/facts.md、spec/insights.md
  - concepts/ 至少覆盖：整体架构、Mobject 对象系统、Animation 动画、Scene 场景、Camera 相机、Renderer 渲染、配置系统
  - examples/ 至少包含 2-3 个关键使用示例（如简单场景、自定义动画、LaTeX 使用）
  - references/ 包含核心模块信源登记
  - spec/facts.md 包含至少 50 条编号事实，无推断性表述
  - V 阶段 Grep 验证：所有引用的类名/方法名在 manimlib/ 中真实存在
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 以 manimlib/ 为核心阅读范围，tests/ 和 docs/ 作为辅助参考

### AC-2: videos 知识包结构完整且内容准确
- **Given**: videos 源码在 `external/dao/action/3b1b/videos/` 可读
- **When**: 完成 R→I→E→V 四阶段流程
- **Then**:
  - `doc/bundles/viz/3b1b/videos/` 目录存在，结构完整
  - 覆盖 InteractiveScene 开发模式、checkpoint_paste 工作流、典型年份项目结构
  - spec/facts.md 包含核心模式事实，标注版本兼容性注意事项
- **Verification**: `programmatic` + `human-judgment`

### AC-3: caption_ops 知识包结构完整且内容准确
- **Given**: caption_ops 源码在 `external/dao/action/3b1b/caption_ops/` 可读
- **When**: 完成 R→I→E→V 四阶段流程
- **Then**:
  - `doc/bundles/viz/3b1b/caption-ops/` 目录存在，结构完整
  - 覆盖字幕处理管线、SRT 操作、转录/翻译/同步工作流
  - spec/facts.md 记录核心脚本功能与调用关系
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 目录名使用 kebab-case `caption-ops` 而非 `caption_ops`

### AC-4: 3Blue1Brown.com 知识包结构完整且内容准确
- **Given**: 3Blue1Brown.com 源码在 `external/dao/action/3b1b/3Blue1Brown.com/` 可读
- **When**: 完成 R→I→E→V 四阶段流程
- **Then**:
  - `doc/bundles/viz/3b1b/3blue1brown-com/` 目录存在，结构完整
  - 覆盖项目架构、React Router v7 框架模式、MDX+MathJax 数学内容、组件体系
  - spec/facts.md 记录核心组件、路由、配置事实
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 目录名使用 kebab-case `3blue1brown-com`

### AC-5: viz 技术域与 3b1b 分组索引正确
- **Given**: 4 个知识包已生成
- **When**: 更新各级 index.md
- **Then**:
  - `doc/bundles/viz/index.md` 存在，作为技术域入口，包含分组导航和 toctree
  - `doc/bundles/viz/3b1b/index.md` 存在，作为分组入口，包含 4 个知识包导航和 toctree
  - `doc/bundles/index.md` 已更新，在十域列表中添加 viz 域（第十一域）
  - `invoke gates.toctrees` 运行通过，无孤立文档、无断链
- **Verification**: `programmatic`
- **Notes**: 需更新 mermaid 生态关系图和推荐入门路径图

### AC-6: 所有文档通过质量门验证
- **Given**: 所有知识包和索引文件已生成
- **When**: 运行 awesome-okf-xs 质量门
- **Then**:
  - `invoke gates.utf8` 通过，所有文件 UTF-8 编码无 BOM
  - `invoke gates.toctrees` 通过，零断链、零孤立文档
  - 每个知识包根 index.md 包含正确的 `okf_version: "0.2"` frontmatter
  - 子目录 index.md（concepts/examples/references）不含 frontmatter
  - 所有交叉链接使用 `/` 开头 bundle-relative 路径
- **Verification**: `programmatic`

## Open Questions
- [ ] videos 知识包的覆盖深度：是覆盖所有年份的所有视频，还是选取代表性项目（如 eola/线性代数系列、eoc/微积分系列、nn/神经网络系列）进行模式提炼？建议：提炼通用模式，选取 2-3 个代表性系列作为 examples。
- [ ] 3Blue1Brown.com 的 bucket/ 目录（云存储同步脚本）是否纳入分析范围？建议：简单提及，不作为重点。
- [ ] viz 域是否需要在 mermaid 生态关系图中与 data/pydata（matplotlib/plotly）和 document（数学排版）建立关联？建议：是，建立可视化与数据科学、数学排版的关联。
