---
title: "DeepSeek-AI 开源项目 OKF Wiki 教程生成 - Product Requirements Document"
status: "draft"
---

# DeepSeek-AI 开源项目 OKF Wiki 教程生成 - Product Requirements Document

## Overview

- **Summary**: 在 `projects/awesome-okf-xs/bundles/` 下创建新的 `deepseek/` 知识束分组，为 DeepSeek-AI 组织开源的 12 个子项目生成符合 OKF v0.2 规范的中文源码学习 Wiki 教程。
- **Purpose**: 系统化学习 DeepSeek-AI 在大模型基础设施（MoE通信、GPU kernel优化、投机解码、注意力机制、流水线并行、负载均衡等）方向的核心开源项目，产出可溯源、可验证、结构化的中文教程，填补国内深度系统学习 DeepSeek 基础设施源码的空白。
- **Target Users**: 需要深入理解 DeepSeek-V3/R1 技术栈的 AI 系统工程师、GPU kernel 开发者、大模型推理优化工程师、对 MoE/EP/注意力/投机解码等核心技术感兴趣的研究人员。

## Goals

1. 在 `bundles/deepseek/` 下创建分组索引 `index.md`，与现有分组（jupyter/、sphinx/、pydata/ 等）平级
2. 为 7 个核心代码库项目（DeepEP、DeepGEMM、FlashMLA、TileKernels、LPLB、DeepSpec、DualPipe）生成完整 OKF bundle（含 concepts/、examples/、references/ 三层结构）
3. 为 5 个轻量项目（DeepSeek-OCR、DeepSeek-OCR-2、awesome-deepseek-agent、DeepSeek-Math-V2、Engram）生成适当深度的 OKF bundle
4. 所有文档严格遵循 OKF v0.2 frontmatter 规范和 source-code-to-okf-wiki 工作流（R→I→E→V→C）
5. 更新 `bundles/index.md` 总索引，添加 deepseek 分组
6. 每个代码库 bundle 包含根 index.md（含 okf_version、快速导航、学习路径、核心洞察）

## Non-Goals

1. 不修改 `external/libs/ai/deepseek-ai/` 下的任何源码（这些是第三方子模块）
2. 不翻译或改写项目官方 README，而是基于源码深度分析产出独立教程
3. 不为 paper-only 项目（DeepSeek-Math-V2、Engram）生成过多概念文档——这些项目核心价值在论文而非代码
4. 不生成英文文档，所有内容均为中文
5. 不修改 awesome-okf-xs 中已有 bundle 的内容
6. 不在本次任务中执行 git commit（除非用户明确要求）

## Background & Context

DeepSeek-AI 开源了一系列大模型基础设施项目，这些项目是 DeepSeek-V3/R1 等模型高性能训练和推理的核心技术支撑：

- **DeepEP**: MoE 专家并行通信库，高吞吐/低延迟 all-to-all GPU kernel
- **DeepGEMM**: 统一高性能 tensor core kernel 库，涵盖 FP8/FP4 GEMM、Mega MoE
- **FlashMLA**: MLA 注意力解码 kernel，H800 上达 3000GB/s 带宽
- **TileKernels**: 基于 TileLang DSL 的 LLM 操作优化 kernel 集合
- **LPLB**: 基于线性规划的 MoE 专家并行负载均衡器
- **DeepSpec**: 投机解码草稿模型训练与评估全栈代码
- **DualPipe**: 双向流水线并行调度算法参考实现
- **DeepSeek-OCR/OCR-2**: OCR 模型（vLLM/HF 推理集成代码）
- **awesome-deepseek-agent**: DeepSeek 集成到 AI 工具的指南列表
- **DeepSeek-Math-V2 / Engram**: 论文配套仓库

现有 bundles/ 目录已包含 10 个分组（meta/python/conda/jupyter/sphinx/tooling/cmake/agnes-ai/ai-agent/pydata）共 36 个知识束。deepseek 分组将是第 11 个分组，聚焦 AI 基础设施/GPU 系统层。

## Functional Requirements

- **FR-1**: 创建 `bundles/deepseek/` 分组目录和 `index.md`，包含分组描述、生态关系概览、知识束列表导航
- **FR-2**: 为每个核心代码库项目创建独立 bundle 目录，遵循 OKF bundle 结构：`<bundle>/index.md`、`<bundle>/concepts/`、`<bundle>/examples/`、`<bundle>/references/`
- **FR-3**: 每个 bundle 的 `references/` 目录包含源码信源登记文件，列出核心源文件路径和模块索引
- **FR-4**: 每个 bundle 的 `concepts/` 目录包含按学习路径编号的概念文档，覆盖架构总览、核心模块、关键算法、API 接口等
- **FR-5**: 每个 bundle 的 `examples/` 目录包含可运行的代码示例（基于源码中的 tests/ 和 examples/）
- **FR-6**: 所有概念文档包含规范的 YAML frontmatter（type, title, description, tags, generated, verified, status, stale_after, sources）
- **FR-7**: 所有文档交叉链接使用 `/` 开头的 bundle-relative 绝对路径
- **FR-8**: 每个概念文档结尾包含"## 相关概念"章节
- **FR-9**: 更新 `bundles/index.md`，在分组导航表和分组详情中添加 deepseek 分组
- **FR-10**: R 阶段产出的 facts.md（事实清单）和 I 阶段产出的 insights.md（架构洞察）存放在各 bundle 的 `spec/` 子目录中，作为可审计中间产物

## Non-Functional Requirements

- **NFR-1（准确性）**: 文档中引用的所有类名、方法名、API 签名必须可通过 Grep 在源码中验证存在，零虚构 API
- **NFR-2（完整性）**: 核心代码库 bundle 的概念文档覆盖项目所有主要模块和公开 API
- **NFR-3（可读性）**: 中文撰写，英文术语首次出现附中文注释；代码块标注语言；每篇概念文档 500-5000 字
- **NFR-4（一致性）**: 所有 bundle 遵循统一的文档模板和格式规范，与现有 katex、cmake、numpy 等 bundle 风格一致
- **NFR-5（可溯源）**: 每个事实引用具体源码文件路径，sources 字段指向 references/ 信源文件
- **NFR-6（学习路径）**: 每个 bundle 根 index.md 提供清晰的学习路径推荐（入门→核心→高级）

## Constraints

- **Technical**:
  - 必须遵循 OKF v0.2 规范（详见 `projects/awesome-okf-xs/.agents/rules/frontmatter.md`）
  - 必须遵循 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）
  - 正文中文，文件名 kebab-case 英文
  - 交叉链接使用 `/` 开头的 bundle-relative 路径
  - 子目录 index.md 不含 frontmatter（仅 bundle 根 index.md 带 okf_version）
  - references/ 信源文件必须在 concepts/ 之前生成
  - index.md 必须最后生成
  - 每批生成文档 ≤7 个，防止上下文过载
- **Business**:
  - 源码位于 `d:\spaces\SpecWeave\external\libs\ai\deepseek-ai\`，不修改任何源文件
  - 产出物位于 `d:\spaces\SpecWeave\projects\awesome-okf-xs\bundles\deepseek\`
- **Dependencies**:
  - 依赖 OKF v0.2 规范（meta/okf-spec bundle 已存在）
  - 依赖 source-code-to-okf-wiki skill 的五阶段方法论
  - 依赖 seven-concepts-cmd 的场景识别和质量门编排

## Assumptions

1. deepseek-ai 下的 12 个子项目已完整 clone 到本地，源码可读
2. awesome-okf-xs 子项目已初始化且目录结构完整
3. 对于 CUDA kernel 项目（DeepEP/DeepGEMM/FlashMLA），重点分析 Python API 层和架构设计，CUDA C++ kernel 内部实现不做逐行解析（那需要硬件环境验证）
4. 对于轻量项目（paper/resource-list），bundle 深度适当降低，侧重 references 索引和关键概念概述
5. Windows 环境下路径使用正斜杠或正确转义的反斜杠进行 Grep 验证

## Acceptance Criteria

### AC-1: 分组结构正确创建
- **Type**: `rule`
- **Given**: `bundles/deepseek/` 目录不存在
- **When**: 完成 FR-1 和 FR-9
- **Then**: 存在 `bundles/deepseek/index.md` 且包含 okf_version frontmatter 和分组导航；`bundles/index.md` 已更新包含 deepseek 分组
- **Pass Condition**: `bundles/deepseek/index.md` 存在且可解析；`bundles/index.md` 包含 "deepseek" 分组条目和 `groups: 11`
- **Evidence**: 文件系统检查 + 文件内容验证

### AC-2: 核心代码库 bundle 结构完整
- **Type**: `rule`
- **Given**: 7 个核心项目（DeepEP、DeepGEMM、FlashMLA、TileKernels、LPLB、DeepSpec、DualPipe）
- **When**: 完成 FR-2 到 FR-5
- **Then**: 每个核心项目 bundle 包含 index.md、concepts/index.md、examples/index.md、references/index.md，且 concepts/ 下至少有 3 篇概念文档
- **Pass Condition**: 7 个核心 bundle 目录结构完整，每个 concepts/ 下文档数 ≥ 3，references/ 下至少有 1 个信源文件
- **Evidence**: 目录结构遍历 + 文件计数

### AC-3: Frontmatter 规范合规
- **Type**: `rule`
- **Given**: 所有生成的 .md 文件
- **When**: 完成所有文档生成
- **Then**: 每个非保留 .md 文件包含可解析的 YAML frontmatter，含 type 字段；根 index.md 含 okf_version: "0.2"；子目录 index.md 无 frontmatter
- **Pass Condition**: 所有文档 frontmatter 验证通过，无缺失必填字段
- **Evidence**: 逐文件 frontmatter 解析检查

### AC-4: API 真实性零虚构
- **Type**: `rule`
- **Given**: 所有概念文档和示例文档中引用的类名、函数名、方法名
- **When**: V 阶段验证
- **Then**: 文档中引用的每个公开 API（类/函数/方法）均可在对应源码中通过 Grep 找到定义
- **Pass Condition**: V 阶段 Grep 验证未发现虚构 API，发现的虚构 API 修复率 100%
- **Evidence**: Grep 验证脚本输出 + 修复记录

### AC-5: 交叉链接无断裂
- **Type**: `rule`
- **Given**: 所有文档中的交叉链接（`/concepts/xxx.md`、`/examples/xxx.md`、`/references/xxx.md`）
- **When**: V 阶段验证
- **Then**: 所有链接目标文件存在
- **Pass Condition**: 断链数为 0
- **Evidence**: 链接检查脚本输出

### AC-6: 文档质量与学习价值
- **Type**: `rubric`
- **Dimension**: 文档内容的技术准确性、结构清晰度和学习价值
- **Scale**: 1-5
- **Anchors**: 1 = 内容肤浅/错误多，无学习价值；3 = 基本准确覆盖主要 API，但缺乏深度洞察和架构理解；5 = 深入准确，架构洞察清晰，学习路径设计合理，示例可运行，读完能理解项目核心设计
- **Pass Threshold**: >= 4
- **Evidence**: 独立审查者评估

### AC-7: 轻量项目适当覆盖
- **Type**: `rule`
- **Given**: 5 个轻量项目（DeepSeek-OCR、DeepSeek-OCR-2、awesome-deepseek-agent、DeepSeek-Math-V2、Engram）
- **When**: 完成生成
- **Then**: 每个轻量项目有 bundle 目录和 index.md，包含项目概述、核心内容索引和信源参考；有代码的项目（OCR）至少 1 篇概念文档覆盖模型架构
- **Pass Condition**: 5 个轻量 bundle 存在且 index.md 完整
- **Evidence**: 文件系统检查

## Open Questions

- [ ] DeepSeek-OCR 和 DeepSeek-OCR-2 是否合并为一个 bundle（两者架构相似）？建议：分开为两个 bundle，OCR-2 作为 OCR 的演进版本
- [ ] CUDA C++ kernel 内部实现的深度如何把握？建议：Python API 层和架构设计为主，CUDA kernel 做架构级描述（线程块组织、内存层级、优化策略），不逐行解析 PTX/SASS
