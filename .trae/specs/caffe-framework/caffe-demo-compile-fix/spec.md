# Caffe Demo 模型编译修复 - Product Requirement Document

## Overview
- **Summary**: 修复 `external/chaos/models/debug/caffe_demo` 模型在 NPU 工具链下编译失败的问题。根因是 `config.toml` 中输入 shape `[1,3,120,120]` 与 `fgvsirfeature_ssd.prototxt` 定义的 `input_dim: 32` 不匹配，导致 VTA 硬件在静态运行时生成阶段无法对 29×29 特征图进行有效 tile split。
- **Purpose**: 使 caffe_demo 模型能在 SIM_VTA2.0 目标平台上完成完整编译流程（量化→构建→导出→自动调优→静态运行时生成），产出 `vta_config.bin` 等部署文件。
- **Target Users**: 使用 NPU 工具链编译和部署 Caffe SSD 模型的开发者。

## Goals
- caffe_demo 模型编译 6 个步骤全部通过，无 split error
- `vta_config.bin`、`network.xmnn`、`param.bin` 等产物正常生成
- config.toml 的 shape 与 prototxt 的 input_dim 保持一致

## Non-Goals (Out of Scope)
- 不修改模型网络结构（prototxt/caffemodel 保持不变）
- 不修改 VTA 工具链源代码
- 不调整量化策略或其他编译选项
- 不进行板端部署（仅仿真平台编译验证）

## Background & Context
- caffe_demo 的 config.toml 疑似从 caffe_demo_old 复制而来。旧模型 `fgvsirfeature.prototxt` 设计为 120×120 输入，而新 SSD 模型 `fgvsirfeature_ssd.prototxt` 设计为 32×32 输入。复制 config 时未更新 shape。
- VTA 硬件模型 `xmfpga_v2_1x16_i8w8a32_11_13_15_15` 对特征图空间维度有 tile 约束。120×120 输入经 conv1(k=3,s=2)+pool(k=3,s=2) 后产生 29×29 特征图，超出 tile 可切分范围，触发 `VTA_TOPI_conv2d split error`。
- 32×32 输入经相同层后产生 7×7 特征图，在硬件约束范围内，编译通过。

## Functional Requirements
- **FR-1**: config.toml 中 `[input].shape` 必须与 prototxt 中 `input_dim` 定义的输入尺寸一致
- **FR-2**: 执行 `compile.py -n debug/caffe_demo` 完成全部 6 步编译流程
- **FR-3**: 编译产物目录包含 `vta_config.bin`、`vta_data.bin`、`network.xmnn`、`param.bin`、`caffe_demo.bin`

## Non-Functional Requirements
- **NFR-1**: 编译总耗时不超过 30 秒（仿真平台）
- **NFR-2**: 运行时日志中无 error/fail/split 关键词
- **NFR-3**: 修复仅修改 1 行配置，不引入副作用

## Constraints
- **Technical**: VTA2.0 硬件 tile 约束（BLOCK=16，空间维度需可切分）；Caffe SSD 模型固定输入 32×32
- **Business**: 不修改模型权重和网络结构
- **Dependencies**: npu_tvm、npuusertools 工具链、Docker 开发环境

## Assumptions
- prototxt 的 input_dim 是模型设计的正确输入尺寸（32×32）
- demo.png（256×256）会在预处理阶段自动 resize/crop 到 32×32
- caffe_demo 仅用于调试/演示，不要求与 caffe_demo_old 保持相同输入尺寸

## Acceptance Criteria

### AC-1: 编译流程完整通过
- **Given**: config.toml 的 shape 为 [1,3,32,32]，Docker 容器运行中
- **When**: 执行 `compile.py -n debug/caffe_demo`
- **Then**: 6 个编译步骤全部完成，日志输出"模型编译全部完成"
- **Verification**: `programmatic`

### AC-2: 编译产物完整
- **Given**: 编译成功完成
- **When**: 检查 `temp/debug/caffe_demo/compile/` 目录
- **Then**: vta_config.bin、vta_data.bin、vta_data_rtos.bin、network.xmnn、param.bin、caffe_demo.bin 均存在且非空
- **Verification**: `programmatic`

### AC-3: 运行时无 split error
- **Given**: 静态运行时生成步骤完成
- **When**: 检查 runtime_bandwidth_first.log
- **Then**: 日志中不包含 "split error"、"error"、"failed" 等关键词
- **Verification**: `programmatic`

### AC-4: 配置一致性
- **Given**: config.toml 和 fgvsirfeature_ssd.prototxt
- **When**: 对比两者的输入尺寸定义
- **Then**: config.toml 的 shape 与 prototxt 的 input_dim 均为 32×32
- **Verification**: `programmatic`

## Open Questions
- 无（根因明确，修复方案唯一）
