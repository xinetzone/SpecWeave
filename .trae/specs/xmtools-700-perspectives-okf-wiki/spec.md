---
type: Spec
title: XMTools 700视角 OKF Wiki 解读工程
generated:
  by: trae-spec-mode
  at: 2026-08-23
status: draft
stale_after: 2027-02-23
---

# XMTools 700视角 OKF Wiki 解读工程 - 产品需求文档

## Overview

- **Summary**：对 `d:\AI\.chaos\xmtools` 下两个企业级 NPU 项目（`npu_tvm` 深度学习编译器分支与 `npuusertools` XMNN 用户工具链）进行系统化源码解读，产出 **700 篇**（全局 200 篇 + `vta_hw` 专项 500 篇）符合 OKF v0.2 规范的中文 Wiki 概念文档。每篇文档以一个独立分析视角切入，基于源码事实给出合情合理的分析与 NPU 建议，按主题归入若干 Bundle，最终统一输出到 `d:\AI\.chaos\docs`。
- **Purpose**：这两个项目是浙江芯劢微电子 NPU 软件栈的核心，但代码量大、模块多、版本分支复杂（vta 1.0→4.0 多版本共存）、缺乏系统化中文解读。700 个视角旨在建立一套覆盖硬件微架构、运行时、编译器、工具链、部署全栈的、可溯源、可验证的知识库，为 NPU 芯片设计改进、部署优化、工具链演进与版本收敛提供事实依据与决策参考。
- **Target Users**：NPU 硬件架构师、编译器/运行时工程师、模型部署工程师、工具链开发者、新入职工程师的 onboarding 学习材料。

## Goals

- G1：建立覆盖两个项目的 **700 个不重复分析视角**，其中 `vta_hw` 专项 500 个、全局（npu_tvm 编译器栈+vta 上层+npu_tvm apps+npuusertools）200 个。
- G2：每篇文档严格遵循 OKF v0.2 规范（完整 frontmatter、信源 sources、bundle-relative 交叉链接），并通过 `source-code-to-okf-wiki` 的 R→I→E→V→C 五阶段质量门。
- G3：内容**真实可靠**——所有引用的类名、方法名、文件名、配置项必须可在源码中 Grep 验证；事实与推断分离；杜绝虚构 API。
- G4：每篇文档给出**与该视角领域匹配的 NPU 建议**，覆盖四个方向：硬件架构设计、部署与性能优化、工具链与编译器改进、版本演进与兼容性。
- G5：主题分类合理——输出目录按项目→主题 Bundle→概念文档三级组织，配有根索引、Bundle 索引与分类导航。
- G6：采用分阶段推进——先建分类法+R阶段事实+试点样本经审批，再批量生成，最后独立验证，确保大规模产出下的质量可控。

## Non-Goals (Out of Scope)

- **不修改任何源码**：本任务是只读解读，不改动 `npu_tvm`/`npuusertools` 的任何源代码、配置或构建脚本。
- **不产出新的可运行代码/示例程序**：文档中可引用源码片段，但不新建可执行工程。
- **不做模型训练/量化调优实验**：NPU 建议基于源码静态分析与行业经验，不进行实测（标注为"经验性建议，以实测为准"）。
- **不解读 3rdparty 第三方依赖源码**（cnpy/rang 等）及 `.git/` 内部数据。
- **不翻译 Apache TVM 上游通用文档**：聚焦芯劢 NPU 定制部分与企业工具链本身。
- **不覆盖二进制产物**（`.so`/`.a`/`.pt`/`.caffemodel`/`.onnx`/PDF）的逆向解读。

## Background & Context

- **项目结构**：
  - `npu_tvm/`：Apache TVM 定制分支，含完整 TVM 源码树（src/include/python/topi/relay/tir 等）、`vta/`（VTA 加速器集成）、`apps/`、`wiki/`（已有 9 篇文档可复用）。
  - `npu_tvm/vta/vta_hw/`：VTA 硬件设计栈，含 Chisel/Scala 核心 25 模块+8 shell+DPI+AXI+util 共 41 个主源码文件、11 个测试文件、5 个版本运行时（v2/v3/v4/vta3.0）、5 套 include 头文件、23 个 FPGA 配置、4 个应用示例、多平台驱动。
  - `npuusertools/`：XMNN 用户工具链，六大命令（compile/infer/accuracy/performance/bandwidth/excelreport）、AdaRound 量化、CLI、C++ 预编译库、示例模型。
- **方法论文档**：`source-code-to-okf-wiki` Skill 提供 R→I→E→V→C 五阶段链路与 Grep 级 API 验证；`seven-concepts-cmd` 提供知识沉淀场景编排（R→I→E 为主链路，V 对抗审查加固）。
- **已有资产**：`npu_tvm/wiki/` 已有 9 篇 Wiki（00-overview 至 08-glossary），`npuusertools/.agents/docs/` 有 5 篇内部文档，可作为事实来源与交叉引用基础，但不替代本次 700 视角的重新解读。
- **内容敏感度**：含 `xmsilicon` 私有头文件、`xm_runtime`/`xmfpga` 等企业定制代码与预编译库，属**私域内容**。产出物按用户指定存放于 `d:\AI\.chaos\docs`，不发布到公开仓库。

## Functional Requirements

- **FR-1 视角分类法注册表**：建立 700 个视角的完整注册表，每个视角含唯一编号、所属项目、主题 Bundle、视角标题、分析透镜类型、对应源码路径、NPU 建议方向。
- **FR-2 R阶段事实采集**：对 vta_hw 全部核心源码文件与 npu_tvm/npuusertools 关键模块，提取编号事实（F-xxx），每个事实指向源码路径与行号，零推断词。
- **FR-3 OKF Bundle 组织**：输出目录按主题划分 Bundle，每个 Bundle 含 `index.md`、`concepts/`、`references/`（信源登记），概念文档存放于 `concepts/`。
- **FR-4 概念文档生成**：每篇 600-1200 字，包含：视角概述、源码事实依据（引用 F-xxx）、分析（架构/数据流/设计权衡）、NPU 建议、相关概念交叉链接。
- **FR-5 NPU 建议**：每篇文档至少包含一条与该视角领域匹配的 NPU 建议，明确标注建议方向（硬件/部署/工具链/版本演进），经验性建议须标注"行业经验估计，实测为准"。
- **FR-6 信源溯源**：每篇文档 frontmatter 的 `sources` 字段指向对应 references 信源文件，references 登记源码路径与关键符号。
- **FR-7 批量生成纪律**：每批生成 ≤7 篇文档，references 信源先行，index 最后写。
- **FR-8 V阶段验证**：Grep 验证文档中引用的每个类名/方法名/文件名在源码中存在；检查链接、frontmatter、index 完整性。
- **FR-9 根索引导航**：生成 `d:\AI\.chaos\docs\README.md` 根索引，按项目与主题分类导航全部 700 篇文档，含学习路径建议。
- **FR-10 进度追踪**：在 tasks.md/checklist.md 中增量更新每批完成状态。

## Non-Functional Requirements

- **NFR-1 真实性**：文档中所有源码符号引用 100% 通过 Grep 验证存在性；零虚构 API/类/方法。
- **NFR-2 不重复性**：700 个视角之间无实质性内容重复（标题与分析角度不同，相同事实可引用但分析结论须有差异）。
- **NFR-3 格式一致性**：所有文档遵循统一 OKF frontmatter 与章节模板，交叉链接统一使用 `/` 开头的 bundle-relative 路径。
- **NFR-4 可导航性**：从根索引到任一文档不超过 3 次点击；每个 Bundle 有 index。
- **NFR-5 规模可验证**：最终文档数量可通过文件计数客观验证（vta_hw 500±2、全局 200±2）。
- **NFR-6 语言规范**：简体中文撰写，英文技术术语首次出现括注；专业术语在 Bundle 级术语表解释。
- **NFR-7 执行可恢复**：分批次生成，中断后可从最后完成批次续做，不重复劳动。

## Constraints

- **Technical**：
  - 源码语言含 Scala/Chisel、C/C++、Python、Verilog、OpenCL、JSON/TOML、Makefile/CMake/sbt。
  - Windows 平台，路径分隔符与 Grep 命令需注意转义。
  - 不修改源码，不安装新依赖（仅读文件与 Grep）。
- **Business**：
  - 私域内容，产出物不得提交到公开仓库。
  - 分阶段交付，Phase 1 试点须经用户审批后才进入 Phase 2。
- **Dependencies**：
  - `source-code-to-okf-wiki` Skill 规范（已加载）。
  - `seven-concepts-cmd` Skill 编排（已加载）。
  - 现有源码树可读。
  - `link-check-cmd` Skill 用于 V 阶段链接验证。

## Assumptions

- A1：`d:\AI\.chaos\xmtools` 下源码完整可读，无加密/权限障碍。
- A2：用户认可"单篇概念文档+主题Bundle"的粒度（已确认）。
- A3：用户认可分阶段推进（已确认），Phase 1 试点审批是硬关卡。
- A4：每篇 600-1200 字的精炼深度适合 700 篇规模，核心模块可适当上浮但不超过 1500 字。
- A5：NPU 建议为静态分析+行业经验，非实测数据，须显式标注。
- A6：700 篇数量允许 ±2 的计数误差（文件系统/分类边界）。
- A7：`vta_hw` 的 500 篇是在全局 200 篇之外的额外深度解读，总计 700 篇。

## Acceptance Criteria

### AC-1: 视角分类法完整
- **Given**：两个项目源码树可访问
- **When**：Phase 1 完成分类法注册表
- **Then**：注册表包含 700 条记录（vta_hw 500 + 全局 200），每条有唯一编号、项目、Bundle、视角标题、透镜类型、源码路径、建议方向；编号无重复、无遗漏
- **Verification**: `programmatic`
- **Notes**：注册表为单一 CSV/Markdown 表格，可脚本统计数量与唯一性

### AC-2: 事实基础零推测
- **Given**：R 阶段完成
- **When**：审查 facts.md
- **Then**：vta_hw 全部核心源码文件有对应事实条目；事实中不出现"用于/目的是/设计为/以便"等推断词；每条事实有源码路径+行号
- **Verification**: `programmatic`

### AC-3: 试点样本获批
- **Given**：Phase 1 生成 20-30 篇代表性样本
- **When**：提交用户审批
- **Then**：样本覆盖 vta_hw 与全局、覆盖四类 NPU 建议方向、覆盖不同源码语言；用户明确批准后方可进入 Phase 2
- **Verification**: `human-judgment`

### AC-4: OKF 格式合规
- **Given**：全部文档生成完毕
- **When**：运行 frontmatter 与结构检查
- **Then**：每篇文档 frontmatter 含 type/title/description/tags/generated/verified/status/sources 字段；Bundle 有 index.md；子目录 index 无 frontmatter；交叉链接用 `/` 开头
- **Verification**: `programmatic`

### AC-5: 源码符号真实
- **Given**：V 阶段 Grep 验证
- **When**：对文档中引用的每个类名/方法名/文件名在源码树中 Grep
- **Then**：所有引用符号在源码中可定位；虚构符号数为 0；发现的虚构项已修复并复验
- **Verification**: `programmatic`

### AC-6: 链接无断裂
- **Given**：全部文档与索引生成
- **When**：运行链接检查
- **Then**：所有内部交叉链接与 sources 引用可解析到存在的文件；无 file:/// 绝对路径；无 ../ 相对路径
- **Verification**: `programmatic`

### AC-7: NPU 建议覆盖四方向
- **Given**：全部文档
- **When**：统计 NPU 建议方向
- **Then**：硬件架构、部署性能、工具链编译器、版本演进四方向均有文档覆盖；每篇至少一条建议；经验性建议有"实测为准"标注
- **Verification**: `programmatic` + `human-judgment`

### AC-8: 数量达标
- **Given**：产出物完成
- **When**：统计 concepts/ 下 .md 文件数
- **Then**：vta_hw Bundle 下 500±2 篇；全局 Bundle 下 200±2 篇；总计 700±4 篇
- **Verification**: `programmatic`

### AC-9: 根索引可导航
- **Given**：根索引生成
- **When**：用户从 README.md 出发
- **Then**：可按项目→主题→视角三级导航到任一篇文档；含学习路径建议；3 次点击内到达
- **Verification**: `human-judgment`

### AC-10: 视角无实质重复
- **Given**：700 篇文档
- **When**：随机抽查每个 Bundle 5% 文档
- **Then**：同 Bundle 内文档标题与分析角度不同，无整段复制；相同事实可引用但结论有差异
- **Verification**: `human-judgment`

### AC-11: 产出位置正确
- **Given**：任务完成
- **When**：检查输出目录
- **Then**：全部产出物位于 `d:\AI\.chaos\docs` 下；未在项目根目录或 .trae/specs 之外散落执行期文件
- **Verification**: `programmatic`

## Open Questions

- [ ] Q1：试点样本的具体篇目是否由 AI 按代表性选取后报审，还是用户指定篇目？（默认 AI 选取代表性样本）
- [ ] Q2：`npu_tvm/wiki/` 已有 9 篇文档是否需要在本次产出中引用/交叉链接，还是完全独立新建？（默认交叉链接引用，不重复其内容）
- [ ] Q3：vta_hw 的 500 篇是否需要严格均分到各子主题，还是按源码丰富度自然分配（如 Chisel 核心多、构建系统少）？（默认按丰富度自然分配）
- [ ] Q4：NPU 建议是否需要标注优先级（P0/P1/P2）？（默认标注优先级）
