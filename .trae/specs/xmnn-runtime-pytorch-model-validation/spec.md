# XMNN Runtime PyTorch 模型支持验证 - Product Requirement Document

## Overview
- **Summary**: 验证 `xmnn-runtime-1.2.1-fix-cp314.tar.gz` 对指定 PyTorch 模型（resnet18、two_inputs）的支持情况，包括模型加载、编译、推理、精度验证等完整流程
- **Purpose**: 确保修复后的 XMNN Runtime 能够正确支持 PyTorch 框架的模型，特别是多输入模型场景
- **Target Users**: XMNN 开发者、模型部署工程师、QA 测试人员

## Goals
- 验证 xmnn-runtime wheel 包能够正确安装和导入
- 验证 PyTorch resnet18 模型能够成功编译和推理
- 验证双输入模型（two_inputs）能够正确处理多输入场景
- 验证推理结果精度符合预期（余弦相似度 ≥ 0.99）
- 生成详细的支持情况报告

## Non-Goals (Out of Scope)
- 不涉及 ONNX 和 Caffe 模型的验证（已在之前的任务中完成）
- 不涉及硬件部署验证（仅验证 SIM_VTA2.0_PRO 仿真环境）
- 不涉及性能优化或调优
- 不修改 xmnn-runtime 源码

## Background & Context
- 上一轮任务已完成 xmnn-runtime 的重新打包，修复了 RelayToTIR 属性注册问题
- ONNX YOLOv5s 和 Caffe ResNet50 模型的验证已通过，精度达到要求
- 本次需验证 PyTorch 模型支持，特别是新增的多输入模型场景
- 测试模型位于 `npuusertools/models/pytorch/resnet18` 和 `npuusertools/models/two_inputs`

## Functional Requirements
- **FR-1**: 验证 wheel 包安装与核心模块导入（tvm、vta、xmnn）
- **FR-2**: 验证 PyTorch resnet18 模型编译流程（compile_xmnn）
- **FR-3**: 验证 PyTorch resnet18 模型推理流程（infer_xmnn）
- **FR-4**: 验证双输入模型 two_inputs 编译流程
- **FR-5**: 验证双输入模型 two_inputs 推理流程
- **FR-6**: 验证推理精度（余弦相似度与原始模型对比）
- **FR-7**: 记录验证过程中的问题并生成报告

## Non-Functional Requirements
- **NFR-1**: 验证过程应自动化执行，减少人工干预
- **NFR-2**: 精度验证余弦相似度 ≥ 0.99
- **NFR-3**: 报告应包含完整的验证步骤、日志和结果
- **NFR-4**: 验证脚本应可复用，便于后续回归测试

## Constraints
- **Technical**: Python 3.14 环境、SIM_VTA2.0_PRO 仿真目标、Windows 操作系统
- **Dependencies**: xmnn-runtime-1.2.1-fix-cp314.tar.gz、PyTorch、NumPy、Pillow
- **Resources**: 模型文件位于 `npuusertools/models/` 目录

## Assumptions
- wheel 包已正确生成并位于 `external/xmhub/notebook/xmnn/dist/` 目录
- 验证环境已配置好必要的依赖（PyTorch、NumPy 等）
- 模型配置文件（config.toml）已正确配置

## Acceptance Criteria

### AC-1: Wheel 包安装与模块导入
- **Given**: xmnn-runtime wheel 包存在于指定路径
- **When**: 执行安装并导入 tvm、vta、xmnn 模块
- **Then**: 安装成功，模块导入无错误，核心 API（compile_xmnn、infer_xmnn）可用
- **Verification**: `programmatic`

### AC-2: PyTorch ResNet18 模型编译
- **Given**: ResNet18 模型文件和配置文件存在
- **When**: 调用 compile_xmnn 编译模型
- **Then**: 编译成功，生成中间表示文件
- **Verification**: `programmatic`

### AC-3: PyTorch ResNet18 模型推理
- **Given**: 已编译的 ResNet18 模型
- **When**: 调用 infer_xmnn 执行推理
- **Then**: 推理成功，生成输出文件
- **Verification**: `programmatic`

### AC-4: ResNet18 精度验证
- **Given**: 原始 PyTorch 模型和 NPU 推理结果
- **When**: 计算余弦相似度
- **Then**: 余弦相似度 ≥ 0.99
- **Verification**: `programmatic`

### AC-5: 双输入模型编译
- **Given**: two_inputs 模型文件和配置文件存在
- **When**: 调用 compile_xmnn 编译双输入模型
- **Then**: 编译成功，正确处理多输入配置
- **Verification**: `programmatic`

### AC-6: 双输入模型推理
- **Given**: 已编译的双输入模型
- **When**: 调用 infer_xmnn 执行推理
- **Then**: 推理成功，正确处理多输入数据
- **Verification**: `programmatic`

### AC-7: 双输入模型精度验证
- **Given**: 原始双输入模型和 NPU 推理结果
- **When**: 计算余弦相似度
- **Then**: 余弦相似度 ≥ 0.99
- **Verification**: `programmatic`

### AC-8: 支持情况报告生成
- **Given**: 所有验证步骤已完成
- **When**: 汇总验证结果
- **Then**: 生成详细的 Markdown 格式支持情况报告
- **Verification**: `human-judgment`

## Open Questions
- [ ] wheel 包安装后是否需要特殊的环境变量配置？
- [ ] 双输入模型的精度验证是否需要特殊处理？
