# VTA-HW 文档与源码偏差审计 - The Implementation Plan

## [ ] Task 1: 建立审计基础设施和事实采集框架
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 确认源码仓库git状态和版本
  - 读取.meta/facts-vta-hw.md等前期事实文件，建立基准
  - 制定偏差分类标准和证据标注规范
  - 列出chisel-core下所有VH-001~VH-150文档与对应scala文件的映射表
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 映射表覆盖150篇chisel-core文档，每篇文档有对应scala文件路径
  - `programmatic` TR-1.2: 能成功执行git log查看关键文件历史
  - `human-judgement` TR-1.3: 偏差分类标准明确（4类偏差×3级严重度）
- **Notes**: 优先使用xmtools/npu_tvm下的源码作为权威版本

## [ ] Task 2: 核心模块（Core/Compute/Decode/Fetch）深度审计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 审计Core.scala对应文档（VH-001~VH-006）
  - 审计Compute.scala对应文档（VH-007~VH-012）
  - 审计Decode.scala对应文档（VH-013~VH-018）
  - 审计Fetch.scala及其变体（FetchVME64/FetchWideVME）对应文档
  - 逐行对比信号连接、模块实例化、参数定义、控制流
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: 每个模块的io信号连接100%核对（名称、方向、连接目标）
  - `programmatic` TR-2.2: 每个子模块实例化记录与源码一致
  - `human-judgement` TR-2.3: 微架构描述和数据流描述与代码逻辑一致
  - `programmatic` TR-2.4: 所有偏差点标注源码行号（可点击链接）
- **Notes**: Core为顶层模块，需特别关注i_post/o_post同步链的真实连接关系

## [ ] Task 3: 内存访问模块（Load/Store/TensorLoad/TensorStore）审计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 审计Load.scala/LoadUop.scala/LoadUopSimple.scala对应文档
  - 审计Store.scala对应文档
  - 审计TensorLoad及其变体（NarrowVME/Simple/WideVME）对应文档
  - 审计TensorStore及其变体（NarrowVME/WideVME）对应文档
  - 重点核对：VME通道分配、地址生成、数据位宽、SRAM接口、握手机制
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: VME读/写通道分配与源码一致
  - `programmatic` TR-3.2: 基地址寄存器(ptrs)映射正确
  - `human-judgement` TR-3.3:  Load/Store状态机和流水线描述准确
- **Notes**: 内存访问是VTA性能关键，地址和通道描述错误会导致严重误解

## [ ] Task 4: 计算模块（TensorGemm/TensorAlu/TensorUtil/ISA/Configs）审计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 审计TensorGemm.scala对应文档（矩阵乘核心）
  - 审计TensorAlu.scala对应文档（ALU单元）
  - 审计TensorUtil.scala对应文档
  - 审计ISA.scala对应文档（指令集架构）
  - 审计Configs.scala/package.scala对应文档
  - 重点核对：数据类型精度、MAC阵列结构、微操作(uop)编码、参数字段
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: ISA指令字段编码与源码一致
  - `programmatic` TR-4.2: Configs参数定义（batch/blockIn/blockOut等）描述正确
  - `human-judgement` TR-4.3: TensorGemm/TensorAlu数据通路描述准确
- **Notes**: ISA是软硬件接口，描述错误影响编译器开发

## [ ] Task 5: 其他模块（Semaphore/EventCounters）和Shell/DPI层审计
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 审计Semaphore.scala/EventCounters.scala对应文档
  - 审计chisel-shell-dpi/下VTAShell/VCR/VME/DPI相关文档
  - 核对Shell层接口信号和时钟复位
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-5.1: VCR/VMEMaster接口Bundle定义与文档一致
  - `human-judgement` TR-5.2: DPI仿真接口用途描述正确

## [ ] Task 6: Git历史溯源和版本对比
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 在xmtools/npu_tvm仓库中执行git log查看关键文件历史
  - 对比apache/tvm上游vta代码与当前npu_tvm版本的差异
  - 识别哪些偏差是因为基于上游旧版本分析，哪些是AI生成幻觉
  - 检查FlowXM/plugins下副本与xmtools下版本是否一致
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-6.1: 获取至少5个关键文件（Core/Compute/TensorGemm/ISA/Configs）的git log
  - `human-judgement` TR-6.2: 分析每个Critical/Major偏差的可能来源（版本差异/理解错误/生成幻觉）

## [ ] Task 7: 偏差统计和高风险模块识别
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**:
  - 统计每个模块的总描述点数和偏差点数
  - 计算偏差率（偏差点数/总描述点数）
  - 按严重程度汇总：Critical/Major/Minor数量
  - 按偏差类型汇总：事实错误/描述不准确/内容遗漏/过度推断
  - 标记偏差率>30%的高风险模块
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-7.1: 偏差统计表包含所有审计模块
  - `programmatic` TR-7.2: 高风险模块清单明确列出
  - `human-judgement` TR-7.3: 偏差率计算合理（如何定义"描述点"有明确定义）

## [ ] Task 8: 生成偏差审计报告
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**:
  - 整合所有审计结果生成完整报告
  - 报告结构：概述→方法论→偏差汇总表→分模块详细偏差→根因分析→修正建议→高风险模块清单
  - 每个偏差条目包含：文档ID、文档位置、源码位置、偏差描述、正确描述、严重程度、偏差类型、可能根因
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 报告结构清晰，易于导航
  - `programmatic` TR-8.2: 所有源码引用使用file:///可点击链接
  - `human-judgement` TR-8.3: 修正建议具体可执行（针对高风险模块给出重写建议）
- **Notes**: 报告输出到 `.chaos/docs/xmnn/.meta/vta-hw-doc-audit-report.md`
