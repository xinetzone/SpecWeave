---
type: Spec
title: VTA-HW 文档与源码偏差审计 PRD
created: 2026-08-26
status: draft
---

# VTA-HW 文档与源码偏差审计 - Product Requirement Document

## Overview
- **Summary**: 系统性审计 `d:\AI\.chaos\docs\xmnn\vta-hw\` 目录下约500篇VTA硬件解读文档，与真实源码 `d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\` 进行逐模块对比，识别事实错误、描述偏差、遗漏内容，并结合git历史分析偏差来源，最终产出偏差分析报告和修正建议。
- **Purpose**: 当前文档标注为 `verified: false` 且存在初步发现的偏差（如Core模块后同步信号链描述错误），需要基于真实源码建立可信的硬件解读基准，为后续NPU优化提供准确的事实基础。
- **Target Users**: 硬件架构研究员、NPU编译器开发者、文档维护者

## Goals
- 系统性识别vta-hw解读文档中的事实错误、描述偏差和内容遗漏
- 按模块分类统计偏差严重程度（Critical/Major/Minor）
- 结合git历史分析偏差产生的根因（基于错误版本/AI生成幻觉/理解偏差）
- 产出偏差审计报告，包含每处偏差的文档位置、源码证据、正确描述
- 识别高风险模块（偏差率>30%的模块需标记重写）

## Non-Goals (Out of Scope)
- 不自动修正文档内容（本次仅审计和报告）
- 不分析global/、apps-deploy/、configs/等非chisel-core核心模块（聚焦chisel-core/chisel-shell-dpi/includes）
- 不进行VTA架构本身的优化设计（仅做事实校验）
- 不覆盖FlowXM/plugins下的副本源码（以xmtools/下为主版本）

## Background & Context
- 文档生成时间：2026-08-23，约500篇概念文档
- 文档状态：`verified: false`，`status: draft`
- 真实源码位置：`d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\`
- 源码副本：`d:\AI\.chaos\FlowXM\plugins\npu_tvm\vta\vta_hw\`（与主版本一致，仅作交叉验证）
- 初步发现的偏差样本：Core模块后同步信号链描述为"Load→Compute→Store三级链"，实际为双向环形同步（Compute(0)↔Load, Compute(1)↔Store）
- .meta/目录下有facts-vta-hw.md等事实采集文件，需验证这些事实是否准确

## Functional Requirements
- **FR-1**: 建立文档-源码映射关系（每篇VH文档对应一个或多个scala源文件）
- **FR-2**: 逐模块（core/shell/dpi/interface/util）进行事实对比
- **FR-3**: 识别四类偏差：
  - 事实错误（描述与源码直接矛盾）
  - 描述不准确（信号方向/连接关系/时序描述有误）
  - 内容遗漏（关键信号/模块未在文档中提及）
  - 过度推断（添加了源码中不存在的功能/设计意图）
- **FR-4**: 检查git历史，确认源码版本与文档参考版本是否一致
- **FR-5**: 统计各模块偏差率（错误描述数/总描述数）
- **FR-6**: 按严重程度分级：Critical（影响架构理解）、Major（模块级错误）、Minor（细节描述问题）

## Non-Functional Requirements
- **NFR-1**: 审计覆盖率100%覆盖chisel-core下所有VH-001~VH-150文档
- **NFR-2**: 每处偏差必须提供源码行号作为证据（可点击链接）
- **NFR-3**: 报告结构清晰，支持按模块/严重程度/偏差类型筛选
- **NFR-4**: 偏差识别准确率≥95%（关键模块Core/Compute/TensorGemm需100%准确）

## Constraints
- **Technical**: 源码为Scala Chisel代码，需理解Chisel硬件描述语义；文档为Markdown格式带YAML frontmatter
- **Business**: 本次任务仅做审计报告，不执行文档修正
- **Dependencies**: 依赖文件系统访问，无外部API依赖

## Assumptions
- `d:\AI\.chaos\xmtools\npu_tvm\` 下的源码为权威真实版本
- 文档中引用的F-VH-Sxxx事实编号可作为初步事实清单，但需独立验证
- git历史可在xmtools/npu_tvm仓库中访问
- 约500篇文档中，chisel-core有150篇为核心审计对象

## Acceptance Criteria

### AC-1: 文档-源码映射完整
- **Given**: vta-hw文档目录和源码目录都存在
- **When**: 执行审计
- **Then**: 每篇VH-xxx.md文档都能映射到对应的scala源文件，映射关系记录在报告中
- **Verification**: `programmatic`
- **Notes**: 映射基于文档frontmatter或index.md中的路径

### AC-2: 关键模块偏差点完整识别
- **Given**: Core.scala、Compute.scala、TensorGemm.scala、Decode.scala、ISA.scala核心源码
- **When**: 对比对应文档
- **Then**: 所有信号连接、模块实例化、参数定义的事实错误都被识别，每个偏差有源码行号证据
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 核心模块零遗漏

### AC-3: 偏差分类与分级准确
- **Given**: 识别出的偏差点列表
- **When**: 分类分级
- **Then**: 每个偏差被正确分类为事实错误/描述不准确/内容遗漏/过度推断，并标记Critical/Major/Minor级别
- **Verification**: `human-judgment`

### AC-4: git历史溯源完成
- **Given**: npu_tvm git仓库可用
- **When**: 检查关键文件的git log
- **Then**: 确认文档参考的源码版本，识别是否因版本演进导致偏差
- **Verification**: `programmatic`

### AC-5: 偏差率统计完成
- **Given**: 各模块偏差点和总描述点
- **When**: 统计
- **Then**: 产出各模块偏差率（错误描述数/总描述数），标记高风险模块（>30%）
- **Verification**: `programmatic`

### AC-6: 审计报告结构完整
- **Given**: 所有审计数据
- **When**: 生成报告
- **Then**: 报告包含概述、方法论、偏差汇总表、分模块详细偏差、根因分析、修正建议、高风险模块清单
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要审计chisel-tests/、configs/、cross-cutting/、includes/目录下的文档？（默认chisel-core+chisel-shell-dpi为优先）
- [ ] .meta/下的facts-vta-hw.md等文件是否需要作为审计输入（验证其事实准确性）？
- [ ] 报告输出位置：默认放在 `.chaos/docs/xmnn/.meta/` 下还是docs/retrospective/reports/下？
