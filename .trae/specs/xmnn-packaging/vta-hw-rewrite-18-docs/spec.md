---
type: Spec
title: VTA-HW 18篇虚构文档重写 PRD
created: 2026-08-27
status: approved
---

# VTA-HW 18篇虚构文档重写 - Product Requirement Document

## Overview
- **Summary**: 基于真实源码重写ISA/Configs/package三个模块共18篇文档（VH-133~VH-150），这些文档在审计中被发现完全虚构（描述了不存在的LFSR64/PECounter/ShiftRegister模块），需要替换为基于真实源码的准确解读。
- **Purpose**: ISA定义软硬件接口（指令编码）、Configs定义硬件参数、package定义全局可见常量，这些是编译器和驱动开发的核心依据，错误文档会直接导致开发错误。
- **Target Users**: NPU编译器开发者、驱动开发者、硬件架构研究员

## Goals
- 基于ISA.scala真实源码重写6篇ISA模块文档（VH-133~VH-138）
- 基于core/Configs.scala和vta/Configs.scala真实源码重写6篇Configs模块文档（VH-139~VH-144）
- 基于core/package.scala真实源码重写6篇package模块文档（VH-145~VH-150）
- 保持与现有高质量文档一致的格式和风格
- 每篇文档标注verified: true，sources引用真实源文件
- 通过对抗审查验证重写内容与源码100%一致

## Non-Goals (Out of Scope)
- 不重写其他模块文档（Core/Load/Store等模块的非虚构偏差修正后续单独处理）
- 不修改chisel-shell-dpi等其他目录
- 不修改源码，仅修正文档
- 不进行VTA架构优化建议的实质性代码改动（仅提供文档层面的分析建议）

## Background & Context
- 审计报告显示VH-133~VH-150共18篇文档完全虚构，描述了源码中不存在的模块
- 真实源码位置：
  - ISA: `d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\core\ISA.scala`
  - Core配置: `d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\core\Configs.scala`
  - 顶层配置: `d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\vta\Configs.scala`
  - package对象: `d:\AI\.chaos\xmtools\npu_tvm\vta\vta_hw\hardware\chisel\src\main\scala\core\package.scala`
- 文档格式参考：以VH-019（Fetch模块）等高质量文档为模板，保持YAML frontmatter和章节结构一致
- 现有高质量文档格式：
  - YAML frontmatter: type/title/description/tags/generated/verified/status/sources/related
  - 章节：视角概述 → 源码事实证据 → 分析 → NPU优化建议 → 关联概念

## ISA模块真实内容摘要
- **ISAConstants trait**（第30-71行）：定义指令位宽常量
  - INST_BITS=128（指令总位宽），OP_BITS=3（操作码位宽）
  - 内存指令字段：M_DEP_BITS=4, M_ID_BITS=3, M_SRAM_OFFSET_BITS=16, M_DRAM_OFFSET_BITS=32, M_SIZE_BITS=16, M_STRIDE_BITS=16, M_PAD_BITS=4
  - 计算指令字段：C_UOP_BGN_BITS=13, C_UOP_END_BITS=14, C_ITER_BITS=14, C_AIDX_BITS=11, C_IIDX_BITS=11, C_WIDX_BITS=10, C_ALU_DEC_BITS=2, C_ALU_OP_BITS=3, C_ALU_IMM_BITS=16
  - 操作码：OP_L=0(load), OP_S=1(store), OP_G=2(gemm), OP_F=3(finish), OP_A=4(alu), OP_X=5(预留)
  - 内存ID：M_ID_U=0(uop), M_ID_W=1(wgt), M_ID_I=2(inp), M_ID_A=3(acc), M_ID_O=4(out)
  - ALU操作数：ALU_OP_NUM=5
- **ISA object**（第81-149行）：使用BitPat定义指令模式匹配
  - 内存加载指令：LUOP/LWGT/LINP/LACC（通过load(id)函数生成，在memId位置匹配不同目标）
  - 存储指令：SOUT
  - 计算指令：GEMM
  - ALU指令：VMIN(minpool)/VMAX(maxpool)/VADD(add)/VSHX(shift)
  - 结束指令：FNSH
  - 指令编码位置：taskId在最低3位，memId在depBits(4位)之后，aluId在第105-107位位置

## Configs模块真实内容摘要
- **CoreParams case class**（core/Configs.scala第27-46行）：Core参数定义
  - batch=1, blockOut=16, blockOutFactor=1, blockIn=16
  - inpBits=8, wgtBits=8, uopBits=32, accBits=32, outBits=8
  - uopMemDepth=2048, inpMemDepth=2048, wgtMemDepth=1024, accMemDepth=2048, outMemDepth=2048
  - instQueueEntries=512
  - 约束：uopBits必须8位对齐（uopBits % 8 == 0）
- **CoreConfig类**（第30-48行）：Config子类，将CoreKey绑定到CoreParams默认值
- **顶层配置**（vta/Configs.scala第34-66行）：
  - DefaultPynqConfig = CoreConfig ++ PynqConfig（Xilinx Pynq平台）
  - DefaultF1Config = CoreConfig ++ F1Config（AWS F1平台）
  - DefaultDe10Config = CoreConfig ++ De10Config（Intel DE10平台）
  - 对应的App对象用于生成SystemVerilog

## package模块真实内容摘要
- **package object core**（core/package.scala第20-23行）：
  - 唯一作用：`package object core extends vta.core.ISAConstants`
  - 通过Scala包对象机制使ISAConstants中定义的常量在vta.core包内全局可见
  - 这是一个Scala语言技巧，避免每次使用ISA常量都需要混入ISAConstants trait

## Functional Requirements
- **FR-1**: ISA模块6篇文档准确覆盖ISAConstants和ISA object的全部内容
- **FR-2**: Configs模块6篇文档准确覆盖CoreParams、CoreConfig、三个DefaultConfig
- **FR-3**: package模块6篇文档准确解释package object的作用机制
- **FR-4**: 所有文档保持与现有高质量文档一致的格式
- **FR-5**: 每篇文档的sources字段引用真实源文件路径
- **FR-6**: verified字段设为true

## Non-Functional Requirements
- **NFR-1**: 每篇文档中的所有事实性描述必须能在源码中找到对应行
- **NFR-2**: 不添加源码中不存在的功能或设计意图描述
- **NFR-3**: 指令编码字段位宽和位置描述100%准确
- **NFR-4**: CoreParams参数值和默认值100%准确
- **NFR-5**: 中文描述，专业术语准确

## Constraints
- **Technical**: 文档为Markdown格式带YAML frontmatter
- **Business**: 仅重写18篇指定文档，不扩大范围
- **Dependencies**: 依赖已完成的审计结果和真实源码文件

## Assumptions
- VH-019.md等现有文档的格式是正确的模板
- tags字段沿用现有标签体系（chisel-core + 维度标签）
- related字段可暂时留空或引用同模块其他文档

## Acceptance Criteria

### AC-1: ISA模块文档准确
- **Given**: ISA.scala源码
- **When**: 重写VH-133~VH-138
- **Then**: INST_BITS=128, OP_BITS=3, 所有M_*/C_*位宽常量, 6个OP_*操作码, 5个M_ID_*内存ID, 9条指令（LUOP/LWGT/LINP/LACC/SOUT/GEMM/VMIN/VMAX/VADD/VSHX/FNSH）均被准确描述
- **Verification**: `programmatic` + `human-judgment`

### AC-2: Configs模块文档准确
- **Given**: core/Configs.scala和vta/Configs.scala源码
- **When**: 重写VH-139~VH-144
- **Then**: CoreParams全部16个参数及默认值、uopBits对齐约束、CoreConfig、三个DefaultConfig组合关系被准确描述
- **Verification**: `programmatic` + `human-judgment`

### AC-3: package模块文档准确
- **Given**: core/package.scala源码
- **When**: 重写VH-145~VH-150
- **Then**: package object继承ISAConstants使常量全局可见的机制被准确解释，不虚构任何不存在的模块或功能
- **Verification**: `programmatic` + `human-judgment`

### AC-4: 格式一致性
- **Given**: 现有高质量文档格式
- **When**: 重写所有18篇文档
- **Then**: YAML frontmatter字段完整、章节结构一致、语言风格一致
- **Verification**: `human-judgment`

### AC-5: 对抗审查通过
- **Given**: 重写后的18篇文档
- **When**: 执行V阶段对抗审查
- **Then**: 每篇文档的所有事实性描述都能在源码中找到对应，无虚构内容
- **Verification**: `programmatic`

## Open Questions
- 无（源码内容已充分理解，格式参考已确认）
