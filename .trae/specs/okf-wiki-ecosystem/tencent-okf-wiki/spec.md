---
title: "腾讯 AI 生态 OKF Wiki 教程 - 产品需求文档"
status: "draft"
---

# 腾讯 AI 生态 OKF Wiki 教程 - 产品需求文档

## Overview
- **Summary**: 基于 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C），系统学习腾讯 CodeBuddy 产品矩阵（IDE/CLI/NPC/WorkBuddy/Security）和三个开源子项目（AI-Infra-Guard、WorkBuddy/Octop、ncnn），在 `projects/awesome-okf-xs/bundles/tencent/` 下生成符合 OKF v0.2 规范的中文 Wiki 教程束。
- **Purpose**: 将腾讯 AI 编程与安全生态的产品知识和开源项目源码架构，转化为结构化、可溯源、可验证的中文知识束，纳入 awesome-okf-xs 文档库。
- **Target Users**: AI 编程工具使用者、开源项目学习者、安全研究人员、智能体开发者。

## Goals
- 在 `bundles/tencent/` 下创建生态分组索引，统一导航腾讯 AI 相关知识束
- 为 **CodeBuddy 产品矩阵**（6个网页来源）生成产品概念教程束（无源码，采用外部文档分析模式）
- 为 **AI-Infra-Guard**（Go/Python 混合 AI 红队平台）生成源码级 Wiki 教程束
- 为 **WorkBuddy/Octop**（Python 自托管多用户 AI 助手）生成源码级 Wiki 教程束
- 为 **ncnn**（C++ 高性能神经网络推理框架）生成源码级 Wiki 教程束
- 所有文档遵循 OKF v0.2 frontmatter 规范，信源可溯源，API 经 Grep 验证无虚构

## Non-Goals (Out of Scope)
- **OpenSourceTalent** 子项目仅含一份犀牛鸟开源人才计划 README，无源码，不生成独立知识束（在 tencent/index.md 中作为生态项目提及即可）
- 不生成 CodeBuddy 闭源产品的源码分析（仅基于公开网页文档生成产品概念教程）
- 不修改 `external/libs/ai/Tencent/` 下的任何源码文件（只读学习）
- 不更新 awesome-okf-xs 根 `bundles/index.md`（由后续 docgen 流程统一更新）
- 不执行 C 阶段模式萃取入库（本次聚焦知识束生成，模式沉淀为可选后续任务）

## Background & Context
- awesome-okf-xs 是 Xuanspace 项目的 OKF 文档库，已有 217 个知识束分 22 组，但尚无腾讯生态分组
- CodeBuddy 是腾讯云推出的 AI 编程助手产品矩阵，包含 IDE（桌面端）、插件、CLI（Code）、NPC（Cloud Agent）、WorkBuddy（Web AI 助手）、Security（代码安全审计）六种形态
- AI-Infra-Guard 是腾讯朱雀实验室开源的 AI 红队平台（Apache-2.0），Go+Python 混合架构，支持 AI 基础设施漏洞扫描、MCP/Agent Skill 扫描、越狱评估
- WorkBuddy/Octop 是腾讯云开源的自托管 AI 助手（MIT），Python 3.12+，基于 harness-agent 运行时，支持多用户多 Agent、IM 通道、ACP 协议
- ncnn 是腾讯开源的高性能神经网络推理框架（BSD-3-Clause），纯 C++ 实现，无第三方依赖，支持 CPU/Vulkan 双后端，覆盖全架构 SIMD 优化
- source-code-to-okf-wiki Skill 提供 R→I→E→V→C 五阶段防护机制，杜绝虚构 API

## Functional Requirements
- **FR-1**: 创建 `bundles/tencent/index.md` 生态分组索引，含 okf_version frontmatter 和各知识束导航
- **FR-2**: 生成 `bundles/tencent/codebuddy/` 知识束，覆盖 IDE/CLI/NPC/WorkBuddy/Security 五大产品形态的概念文档、使用示例和网页信源
- **FR-3**: 生成 `bundles/tencent/ai-infra-guard/` 知识束，覆盖分布式 Server-Agent 架构、四种任务类型、指纹规则 DSL、漏洞结构、Python 子系统的概念文档、代码示例和源码信源
- **FR-4**: 生成 `bundles/tencent/octop/` 知识束，覆盖四层架构、OctopServer 编排器、AgentManager、Gateway、DI 容器、ACP 双向集成、CLI 命令体系的概念文档、代码示例和源码信源
- **FR-5**: 生成 `bundles/tencent/ncnn/` 知识束，覆盖 Net/Extractor 推理流程、Mat 张量系统、Layer 算子基类、Allocator 内存池、Vulkan GPU 后端、SIMD 打包存储、Python 绑定的概念文档、代码示例和源码信源
- **FR-6**: 每个知识束包含 `references/`（信源先行）、`concepts/`（概念文档）、`examples/`（示例文档）、`index.md`（根索引）、`log.md`（变更日志）
- **FR-7**: 每个非保留 .md 文件包含完整 YAML frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）

## Non-Functional Requirements
- **NFR-1**: 所有源码引用的类名/函数名/方法签名必须经 Grep 在源码中验证存在，零虚构 API
- **NFR-2**: 网页来源内容必须标注具体 URL 和抓取日期，产品特性描述忠实于原文
- **NFR-3**: 交叉链接使用 `/` 开头 bundle-relative 绝对路径，不使用 `../` 相对路径
- **NFR-4**: 正文中文撰写，英文技术术语首次出现时括号注释；文件名 kebab-case 纯英文
- **NFR-5**: 每批生成文档数 ≤ 7，防止上下文过载导致质量下降
- **NFR-6**: references/ 信源文件必须先于 concepts/examples 生成

## Constraints
- **Technical**: 运行环境 Windows；源码路径使用 `external/libs/ai/Tencent/`；输出路径 `projects/awesome-okf-xs/bundles/tencent/`
- **Business**: 遵循 awesome-okf-xs AGENTS.md 规范；OKF v0.2 frontmatter 规范；不修改外部源码
- **Dependencies**: source-code-to-okf-wiki Skill 提供方法论；七个概念方法论编排提供质量门；网页内容已通过 browser_use 抓取完毕

## Assumptions
- CodeBuddy 产品网页内容为公开可访问的产品介绍和文档，无访问控制
- 三个开源项目（A.I.G/Octop/ncnn）源码已完整 clone 到本地 `external/libs/ai/Tencent/`
- Octop 依赖的 harness-agent/gateway/memory 为腾讯内部包，源码不在本地，文档中标注为外部依赖即可，不虚构其 API
- ncnn 源码规模大（src/layer/ 下数百个算子），采用分层采样策略：核心运行时全部覆盖，算子层按类别代表性覆盖
- CodeBuddy 产品矩阵无本地源码，采用"外部文档分析模式"，信源为 6 个已抓取的网页 URL

## Acceptance Criteria

### AC-1: tencent 生态分组索引
- **Given**: bundles/tencent/ 目录已创建
- **When**: 查看 index.md
- **Then**: 包含 okf_version: "0.2" frontmatter、四个知识束导航卡片、生态关系概述
- **Verification**: `programmatic`
- **Notes**: 参考 bundles/onnx/index.md 和 bundles/deepseek/index.md 的分组索引风格

### AC-2: CodeBuddy 产品矩阵知识束完整性
- **Given**: codebuddy/ 知识束已生成
- **When**: 检查目录结构和内容
- **Then**: 包含至少 5 个概念文档（IDE/CLI/NPC/WorkBuddy/Security）、2+ 使用示例、6 个信源文件、各级 index.md、log.md；每个产品的核心特性与抓取的网页内容一致
- **Verification**: `programmatic` + `human-judgment`

### AC-3: AI-Infra-Guard 源码知识束准确性
- **Given**: ai-infra-guard/ 知识束已生成
- **When**: 对文档中引用的每个 Go 结构体/函数/Python 入口执行 Grep 验证
- **Then**: 所有引用的类名（OctopServer→应为 AIG 相关结构体如 TaskManager/Runner/FingerprintParser/VulnStruct）在源码中存在；四种任务类型描述与 cmd/cli/main.go 和 common/ 一致；规则 DSL 语法与 common/fingerprints/parser/ 实现一致
- **Verification**: `programmatic`

### AC-4: Octop 源码知识束准确性
- **Given**: octop/ 知识束已生成
- **When**: Grep 验证 OctopServer、AgentManager、Gateway、SharedServices、RepoBundle、_LazyCLI、PathLayout 等核心类
- **Then**: 所有类名和关键方法签名在 src/octop/ 中存在；四层架构依赖流向与 AGENTS.md 禁令一致；20 个 CLI 子命令与 registry.py COMMANDS 一致
- **Verification**: `programmatic`

### AC-5: ncnn 源码知识束准确性
- **Given**: ncnn/ 知识束已生成
- **When**: Grep 验证 Net、Extractor、Mat、Layer、Blob、Option、Allocator、PoolAllocator、VkAllocator 等核心类
- **Then**: 所有类名和关键方法在 src/ 中存在；Mat 维度系统（dims/w/h/d/c/elempack）描述与 mat.h 一致；Layer 虚函数签名与 layer.h 一致；Allocator 继承体系与 allocator.h 一致
- **Verification**: `programmatic`

### AC-6: OKF v0.2 规范合规
- **Given**: 所有知识束文档已生成
- **When**: 检查每个 .md 文件
- **Then**: 非保留文件含 type 字段和完整 frontmatter；子目录 index.md 无 frontmatter；根 index.md 含 okf_version；交叉链接无 `../`；无断链
- **Verification**: `programmatic`

### AC-7: 信源先行与分批生成纪律
- **Given**: 审查生成过程记录
- **When**: 检查文件创建顺序和批次
- **Then**: references/ 文件先于 concepts/examples 创建；index.md 最后生成；每批 ≤ 7 文件
- **Verification**: `human-judgment`

## Open Questions
- [ ] ncnn 算子层有 120+ 通用算子和 600+ 平台优化文件，概念文档应覆盖多少算子？（建议：核心运行时全覆盖，算子层按类别选 5-8 个代表性算子深入，其余在 references 中列表登记）
- [ ] CodeBuddy 产品迭代快，stale_after 建议设为多久？（建议：2027-02-23，半年后重新评估产品形态）
