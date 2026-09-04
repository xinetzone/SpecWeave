---
status: "draft"
okf_version: "0.2"
type: spec
title: "Coze 开发平台生态 OKF Wiki 教程生成"
description: "学习 external/libs/ai/coze-dev 全部子项目源码，在 projects/awesome-okf-xs/bundles 中生成 OKF v0.2 规范的中文源码教程"
generated: true
---

# Coze 开发平台生态 OKF Wiki 教程生成 - Product Requirements Document

## Overview
- **Summary**: 系统化学习 `external/libs/ai/coze-dev/` 目录下全部子项目（coze-py、coze-studio、cozeloop-python、cozeloop-examples）源码，使用 source-code-to-okf-wiki 技能（R→I→E→V→C 五阶段链路）和 seven-concepts-cmd 方法论，在 `projects/awesome-okf-xs/bundles/coze/` 目录下生成符合 OKF v0.2 规范的结构化中文源码教程知识束。
- **Purpose**: 为 Coze（扣子）AI Agent 开发平台生态建立可溯源、可验证的中文源码级知识库，覆盖 Python SDK、开源 Studio 平台、可观测性 SDK 三大核心组件，帮助开发者深入理解 Coze 平台架构与 API 设计。
- **Target Users**: AI 应用开发者、需要集成 Coze API 的 Python 工程师、对 AI Agent 平台架构感兴趣的开发者、开源 Coze Studio 二次开发者。

## Goals
- 在 `bundles/coze/` 下创建新的知识束分组，包含 3 个知识束：coze-py、coze-studio、cozeloop-python
- cozeloop-examples 作为示例资源整合进 cozeloop-python 知识束的 examples/ 目录
- 每个知识束遵循 OKF v0.2 规范，包含 concepts/（概念文档）、examples/（实战示例）、references/（信源登记）三层结构
- 所有 API 引用经 Grep 级源码验证，杜绝虚构内容
- 更新 bundles/index.md 和必要的分组索引，将 coze 分组纳入总导航

## Non-Goals
- 不覆盖 coze-dev 以外的 Coze 商业版闭源功能
- 不深入 coze-studio 前端 135+ 个 Rush.js 包的每个包的逐行分析（采用架构级分层采样策略）
- 不生成 cozeloop-examples 独立知识束（内容过少，作为 cozeloop-python 的示例整合）
- 不修改源码文件本身
- 不生成 C 阶段模式沉淀文档（仅在有显著新模式值得沉淀时进行）

## Background & Context
- 此前已成功为 ONNX 生态（8个知识束、150个.md文件）和 deepseek 生态生成 OKF wiki，验证了 R→I→E→V→C 五阶段工作流的有效性
- coze-dev 是字节跳动开源的 Coze（扣子）AI Agent 开发平台的开发工具集合，包含：
  - **coze-py**: Coze 开放 API 的 Python SDK，覆盖 Bot/Chat/Workflow/Conversation/Audio/WebSocket/Auth 等完整 API 面
  - **coze-studio**: 一站式开源 AI Agent 开发平台，Go 后端（Hertz+DDD）+ React 前端（Rush.js monorepo 135+ 包），含 Thrift IDL、Docker 部署、Helm Chart
  - **cozeloop-python**: CozeLoop AI 应用可观测性 Python SDK，提供 Trace 上报、Prompt 管理、PTaaS 功能
  - **cozeloop-examples**: CozeLoop 使用示例（Go/Python/JS），内容极简
- 现有 bundles 已有 agnes-ai（AI大模型API）和 ai-agent（Agent框架）两个AI相关分组，coze 作为 AI Agent 开发平台生态独立成组

## Functional Requirements
- **FR-1**: 创建 `bundles/coze/` 分组目录和 `bundles/coze/index.md` 分组索引
- **FR-2**: 为 coze-py 生成完整 OKF 知识束，包含 concepts/、examples/、references/、index.md、log.md
- **FR-3**: 为 coze-studio 生成完整 OKF 知识束（后端 Go 架构+前端架构+IDL+部署），采用分层采样策略聚焦核心架构
- **FR-4**: 为 cozeloop-python 生成完整 OKF 知识束，将 cozeloop-examples 内容整合进 examples/
- **FR-5**: 每个知识束遵循 R→I→E→V→C 五阶段流程：R阶段采集编号事实→I阶段提炼架构洞察→E阶段信源先行分批生成→V阶段Grep验证→必要时C阶段沉淀
- **FR-6**: 更新 `bundles/index.md` 总索引，纳入 coze 分组及各知识束简介
- **FR-7**: 所有文档使用中文撰写，英文技术术语首次出现时括号注释
- **FR-8**: 交叉链接使用 `/` 开头的 bundle-relative 路径

## Non-Functional Requirements
- **NFR-1**: 所有文档 frontmatter 符合 OKF v0.2 规范（type/title/description/tags/generated/verified/status/stale_after/sources）
- **NFR-2**: 所有类名、方法名、API 调用经 Grep 源码验证存在性，零虚构 API
- **NFR-3**: 所有内部交叉链接有效，无断链
- **NFR-4**: 每批生成文档数 ≤ 7，防止上下文过载
- **NFR-5**: references/ 信源文件必须先于 concepts/ 生成（信源先行原则）
- **NFR-6**: 各级 index.md 在内容文档定稿后最后生成

## Constraints
- **Technical**:
  - 源码路径：`d:\spaces\SpecWeave\external\libs\ai\coze-dev\`
  - 输出路径：`d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\coze\`
  - 遵循 OKF v0.2 规范
  - Windows 环境下 Grep 路径使用正确分隔符
- **Business**: 无
- **Dependencies**:
  - source-code-to-okf-wiki skill（R→I→E→V→C 工作流）
  - seven-concepts-cmd skill（R→I→E 方法论指导）
  - 现有 bundles 结构作为格式参考
  - awesome-okf-xs AGENTS.md 规范

## Assumptions
- coze-dev 各子项目的 git submodule 已初始化且源码可读
- coze-studio 前端虽然庞大（135+包），但架构文档和核心入口文件足以支撑架构级教程
- cozeloop-examples 内容足够精简，整合进 cozeloop-python 不影响知识束完整性
- 用户期望的文档深度与已有的 onnx/agnes-ai 知识束相当（每个子项目约10-20个内容文档）

## Acceptance Criteria

### AC-1: coze-py 知识束完整性
- **Type**: `rule`
- **Given**: coze-py 源码目录存在且可读
- **When**: R→I→E→V 四阶段完成
- **Then**: `bundles/coze/coze-py/` 下存在完整的 OKF 知识束结构
- **Pass Condition**: 包含 concepts/（≥8篇概念文档）、examples/（≥3篇示例文档）、references/（≥4篇信源登记）、index.md、log.md；子目录含 index.md
- **Evidence**: 目录结构检查 + 文件计数

### AC-2: coze-studio 知识束完整性
- **Type**: `rule`
- **Given**: coze-studio 源码目录存在且可读
- **When**: R→I→E→V 四阶段完成
- **Then**: `bundles/coze/coze-studio/` 下存在完整的 OKF 知识束结构
- **Pass Condition**: 包含 concepts/（≥8篇概念文档，覆盖后端DDD架构+前端monorepo架构+IDL+部署）、examples/（≥2篇示例文档）、references/（≥4篇信源登记）、index.md、log.md；子目录含 index.md
- **Evidence**: 目录结构检查 + 文件计数

### AC-3: cozeloop-python 知识束完整性
- **Type**: `rule`
- **Given**: cozeloop-python 和 cozeloop-examples 源码存在且可读
- **When**: R→I→E→V 四阶段完成
- **Then**: `bundles/coze/cozeloop-python/` 下存在完整的 OKF 知识束结构
- **Pass Condition**: 包含 concepts/（≥5篇概念文档）、examples/（≥2篇示例文档，含cozeloop-examples整合内容）、references/（≥3篇信源登记）、index.md、log.md；子目录含 index.md
- **Evidence**: 目录结构检查 + 文件计数

### AC-4: OKF 规范合规性
- **Type**: `rule`
- **Given**: 所有知识束文档已生成
- **When**: 执行 frontmatter 和结构检查
- **Then**: 所有文档符合 OKF v0.2 规范
- **Pass Condition**: 所有 .md 文件 frontmatter 字段完整且合法（type/title/description/sources等）；子目录 index.md 不含 frontmatter；根 index.md 含 okf_version；交叉链接无断链
- **Evidence**: frontmatter 检查 + 链接验证

### AC-5: API 真实性零虚构
- **Type**: `rule`
- **Given**: 所有知识束文档已生成
- **When**: 对文档中引用的关键类名/方法名/API执行 Grep 源码验证
- **Then**: 所有引用的 API 在源码中存在
- **Pass Condition**: Grep 验证通过率 100%，零虚构 API
- **Evidence**: Grep 命令输出 + 验证报告

### AC-6: 分组索引与总导航更新
- **Type**: `rule`
- **Given**: 3个知识束全部完成
- **When**: 更新导航文件
- **Then**: `bundles/coze/index.md` 和 `bundles/index.md` 正确反映新增的 coze 分组
- **Pass Condition**: bundles/coze/index.md 存在且列出3个知识束；bundles/index.md 包含 coze 分组条目和生态关系图更新
- **Evidence**: 文件内容检查

### AC-7: 文档质量与可读性
- **Type**: `rubric`
- **Dimension**: 文档内容质量、结构清晰度、学习路径合理性
- **Scale**: 1-5
- **Anchors**: 1 = 内容混乱、大量虚构、结构缺失；3 = 内容基本准确但组织松散、缺少上下文；5 = 架构洞察深刻、学习路径清晰、代码示例可运行、信源追溯完整
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查时的内容质量评估

## Open Questions
- 无（基于前期探索，源码结构和输出格式均已明确）
