# caffex vs caffe-ffi 技术差距分析 - 产品需求文档

## Overview
- **Summary**: 对 BVLC Caffe（caffex）与 caffe-ffi 两个深度学习推理框架进行全面系统性技术对比分析，识别 caffe-ffi 在算子覆盖、功能完整性、代码架构、接口设计等方面的差距，产出包含缺失算子清单和结构优化建议的技术分析报告。
- **Purpose**: 为 caffe-ffi 后续演进提供明确的补全路线图，量化当前算子覆盖缺口，识别架构层面的设计偏差和优化机会。
- **Target Users**: caffe-ffi 核心开发者、架构评审人员、模型部署工程师

## Goals
- 系统性统计 caffex 的完整算子清单与功能模块
- 系统性统计 caffe-ffi 的已实现算子与功能模块
- 在算子种类、算子功能、代码结构、模块划分、接口设计五个维度进行对比
- 输出详细的缺失算子分类清单（按优先级P0/P1/P2）
- 识别 caffe-ffi 架构层面的结构性缺失（如Solver、GPU、训练支持等）
- 给出接口兼容性差异分析与改进建议
- 形成可审计、可追溯的技术分析报告

## Non-Goals (Out of Scope)
- 不修改 caffex 或 caffe-ffi 的任何源代码
- 不实现任何缺失算子或功能（仅分析和建议）
- 不做性能基准测试对比
- 不提供具体代码实现方案
- 不分析 caffe-slim（中间过渡版本）

## Background & Context
- **caffex** (`projects/xuanspace/vendor/caffe/caffex`): 原版 BVLC Caffe 深度学习框架，完整支持训练+推理，包含约75+算子、GPU/CUDA加速、Solver优化器、数据层、Python Layer等完整功能
- **caffe-ffi** (`projects/xuanspace/libs/caffe-ffi`): 基于 TVM FFI 的 Caffe 推理引擎重构版，主打零拷贝(Zero-Copy)、写时复制(COW)、DLPack互操作，当前为纯推理模式（CPU only），实现了约21个算子
- 项目记忆表明 caffe-ffi 定位为推理引擎，框架当前为纯推理模式，Layer基类尚未声明Backward_cpu方法（实际已有默认实现但打警告返回）
- caffe-ffi 的 Blob 采用 TVM FFI Object 系统+侵入式引用计数+COW语义，这是相比 caffex 的核心架构创新

## Functional Requirements
- **FR-1**: 完整列出 caffex 所有算子（头文件+实现文件+CUDA文件），按功能分类
- **FR-2**: 完整列出 caffe-ffi 所有已实现算子，按功能分类
- **FR-3**: 计算算子覆盖率（按数量和按分类）
- **FR-4**: 对比核心类接口（Blob/Layer/Net）的差异
- **FR-5**: 对比代码目录结构的差异
- **FR-6**: 对比 Python API 暴露范围的差异
- **FR-7**: 识别功能模块级别的缺失（Solver/GPU/数据层/Python Layer等）
- **FR-8**: 输出缺失算子清单，按P0(推理必需)/P1(常用)/P2(冷门)分级
- **FR-9**: 给出代码组织结构优化建议
- **FR-10**: 给出接口兼容性改进建议

## Non-Functional Requirements
- **NFR-1**: 分析报告必须基于事实数据，每个差距点必须有具体文件/代码引用支撑
- **NFR-2**: 算子清单必须精确可审计（文件名+数量+分类）
- **NFR-3**: 报告使用中文撰写，格式为Markdown
- **NFR-4**: 缺失算子分级必须有明确依据（使用频率/推理场景必要性）

## Constraints
- **Technical**: 不修改任何源代码文件，只读分析；caffex 为第三方依赖禁止修改
- **Business**: 分析报告产出路径为 `.trae/specs/caffex-vs-caffe-ffi-gap-analysis/`
- **Dependencies**: 依赖已收集的文件目录清单和头文件内容

## Assumptions
- caffex 代表完整的 BVLC Caffe 功能基线（约75个算子）
- caffe-ffi 的算子实现均在 `include/caffe_ffi/layers/` 和 `src/caffe_ffi/layers/` 下
- caffe-ffi 中已注册到 layer_factory 的算子才算"已实现"
- 推理场景以 CNN 经典模型（AlexNet/VGG/ResNet/MobileNet等）的算子需求为优先级依据

## Acceptance Criteria

### AC-1: caffex 算子清单完整性
- **Given**: caffex 目录结构已完整枚举
- **When**: 统计算子头文件和源文件
- **Then**: caffex 算子清单包含所有75+个头文件、75+个.cpp文件、56+个.cu文件，按类别分组
- **Verification**: `programmatic`
- **Notes**: 包含base类（base_conv_layer.hpp等）和cuDNN加速层

### AC-2: caffe-ffi 算子清单准确性
- **Given**: caffe-ffi 目录结构已完整枚举
- **When**: 统计已实现算子
- **Then**: caffe-ffi 算子清单精确包含21个算子的头文件和实现文件
- **Verification**: `programmatic`

### AC-3: 算子覆盖率计算正确
- **Given**: 两份算子清单已整理
- **When**: 进行diff对比
- **Then**: 明确列出已实现的21个算子，以及缺失的算子清单（按分类）
- **Verification**: `programmatic`

### AC-4: 核心接口差异分析完整
- **Given**: Blob/Layer/Net 头文件已读取
- **When**: 进行API级对比
- **Then**: 识别caffex有但caffe-ffi缺失的方法、模板化差异（Dtype模板 vs float固定）、智能指针差异（shared_ptr vs ObjectPtr）等
- **Verification**: `programmatic` + `human-judgment`

### AC-5: 功能模块缺失清单完整
- **Given**: 两个项目的顶层目录和头文件已分析
- **When**: 进行模块级对比
- **Then**: 明确列出Solver/GPU/CUDA/数据层/Python Layer/RNN/LSTM等模块级缺失
- **Verification**: `human-judgment`

### AC-6: 报告格式规范
- **Given**: 所有分析数据已收集
- **When**: 生成最终报告
- **Then**: 报告包含概述、对比分析、缺失算子清单、结构建议、接口建议、总结六个章节，使用Markdown格式
- **Verification**: `human-judgment`

## Open Questions
- [ ] caffe-ffi 是否已规划 Solver/训练支持，还是定位为纯推理框架？（项目记忆显示为纯推理模式）
- [ ] GPU支持是否在路线图中？（当前GPU方法为占位桩）
- [ ] Python Layer 自定义层支持是否有需求？
