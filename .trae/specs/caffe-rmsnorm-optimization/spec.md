# Caffe Normalize→RMSNorm 代码优化 - Product Requirement Document

## Overview
- **Summary**: 对 [caffe.py](file:///d:/spaces/SpecWeave/external/xmhub/npu_tvm/python/tvm/relay/frontend/caffe.py#L549-L560) 中 Normalize 层转 RMSNorm 的代码段进行优化，消除重复计算、提升可读性、完善错误处理，并参照 [test_rms_norm.py](file:///d:/spaces/SpecWeave/apps/tests/test_rms_norm.py) 的标准补充单元测试。
- **Purpose**: 当前代码存在辅助函数重复调用、缺少参数校验、可读性不足等问题，优化后可提升代码质量、减少冗余计算、降低维护成本，同时通过测试确保数学等价性不被破坏。
- **Target Users**: TVM NPU 编译器开发者、维护 caffe frontend 的工程师。

## Goals
- 消除 `_should_convert_normalize_to_rmsnorm` 与后续 `_normalize_rmsnorm_params`/`_normalize_rmsnorm_plan` 的重复调用
- 提升代码可读性：添加必要注释、提取中间变量、理顺逻辑流
- 完善错误处理：对辅助函数返回 None 的场景增加防御性校验
- 保持 L2 Normalize 与 RMSNorm 重参数化的数学等价性（参照 test_rms_norm.py 的验证标准）
- 补充单元测试，覆盖各种 shape、axis、eps 组合场景

## Non-Goals (Out of Scope)
- 不改变 L2 Normalize 层的原有功能语义
- 不修改 `_op.nn.rms_norm` 算子本身的实现
- 不重构 caffe.py 中其他层的转换逻辑（如 BatchNorm、Convolution 等）
- 不进行跨文件的大规模架构重构

## Background & Context
- Caffe 的 Normalize 层执行 L2 归一化后逐通道缩放：`output = x / sqrt(sum(x^2) + eps) * scale`
- 经过数学重参数化，可以等价转换为 TVM 的 `rms_norm` 算子，利用 NPU 硬件加速
- 转换公式：`gamma_rms = gamma / sqrt(d)`, `eps_rms = eps / d`，其中 d 为归一化轴的维度
- 当前实现中存在的问题：
  1. `_should_convert_normalize_to_rmsnorm` 内部调用了 `_normalize_rmsnorm_params`，但判断为 True 后又在第 552 行重复调用，造成不必要的计算
  2. `_normalize_rmsnorm_plan` 在第 553 行才调用，但其返回值与 `_should_convert` 的判定条件可以合并
  3. 缺少对辅助函数返回 None 的二次校验（理论上 `_should_convert` 返回 True 时不会返回 None，但防御性编程更安全）
  4. 第 555 行的三元表达式过长，可读性不佳
  5. 没有对应的单元测试验证转换的数值正确性

## Functional Requirements
- **FR-1**: 重构 RMSNorm 转换分支逻辑，消除辅助函数重复调用，将参数计算和规划在一次判定中完成
- **FR-2**: 为关键转换步骤添加清晰注释，解释重参数化数学原理与 axis 转置策略
- **FR-3**: 增加防御性校验，确保辅助函数返回有效参数后才执行 RMSNorm 转换
- **FR-4**: 提取长表达式为命名中间变量，提升代码可读性
- **FR-5**: 参照 test_rms_norm.py 的测试标准，为 Normalize→RMSNorm 转换添加单元测试，覆盖：
  - 不同输入 shape（1D/2D/3D/4D/5D）
  - 不同 axis（正/负索引，channel 轴与非 channel 轴）
  - 不同 eps 值范围
  - across_spatial=True/False 两种模式
  - channel_shared=True/False 两种缩放模式
  - 数值等价性验证（L2 normalize 结果与 RMSNorm 转换结果的最大绝对误差）

## Non-Functional Requirements
- **NFR-1**: 优化后代码性能不低于原实现（消除重复调用应带来微小性能提升）
- **NFR-2**: 数值精度保持一致，L2 normalize 与 RMSNorm 转换结果的最大绝对误差 ≤ 1e-6（float32 精度下）
- **NFR-3**: 代码风格与 caffe.py 现有风格保持一致
- **NFR-4**: 单元测试可独立运行，无需 NPU 硬件环境

## Constraints
- **Technical**: Python 3.x、TVM Relay API、NumPy；必须兼容 TVM 现有的 expr 构建方式
- **Business**: 不破坏现有 caffe 模型转换功能，所有已有测试必须通过
- **Dependencies**: tvm.relay.op.nn、numpy、现有 caffe.py 辅助函数

## Assumptions
- 现有 `_normalize_rmsnorm_params` 和 `_normalize_rmsnorm_plan` 函数逻辑正确（已由 test_rms_norm.py 的 NumPy 参考实现验证数学等价性）
- `_op.nn.rms_norm` 算子在 TVM 中可用且行为正确
- Caffe Normalize 层的 `across_spatial` 模式（多轴归一化）不适合转换为 RMSNorm（RMSNorm 仅支持单轴归一化），此场景下保持原有 L2 normalize 路径

## Acceptance Criteria

### AC-1: 重复计算消除
- **Given**: caffe.py 中 convert_normalize 方法
- **When**: 执行 RMSNorm 转换分支
- **Then**: `_normalize_rmsnorm_params` 和 `_normalize_rmsnorm_plan` 各只被调用一次，不在判定函数内外重复调用
- **Verification**: `programmatic`（代码审查 + 调用计数验证）

### AC-2: 代码可读性提升
- **Given**: 优化后的代码
- **When**: 开发者阅读 RMSNorm 转换分支
- **Then**: 关键步骤有注释说明，长表达式被拆分为命名变量，逻辑流清晰可跟踪
- **Verification**: `human-judgment`（代码审查）

### AC-3: 防御性错误处理
- **Given**: 辅助函数可能返回 None 的边界情况
- **When**: 转换条件满足但参数计算失败
- **Then**: 代码能够安全回退到原有 L2 normalize 路径，不抛出未处理的异常
- **Verification**: `programmatic`（单元测试覆盖边界情况）

### AC-4: 功能等价性
- **Given**: 相同的输入张量、scale 参数、eps 值
- **When**: 分别走原有 L2 normalize 路径和优化后的 RMSNorm 转换路径
- **Then**: 输出结果的最大绝对误差 ≤ 1e-6（float32 精度）
- **Verification**: `programmatic`（单元测试数值比较）

### AC-5: 单元测试覆盖
- **Given**: 新增的单元测试文件
- **When**: 运行测试
- **Then**: 覆盖 shape/axis/eps/across_spatial/channel_shared 等多种组合场景，全部测试通过
- **Verification**: `programmatic`（运行测试命令）

### AC-6: 向后兼容性
- **Given**: 现有 TVM caffe frontend 测试用例
- **When**: 运行现有测试
- **Then**: 所有已有测试全部通过，无回归
- **Verification**: `programmatic`（运行现有测试）

## Open Questions
- [ ] 单元测试文件应放置在哪个目录？（建议放在 `external/xmhub/npu_tvm/tests/python/frontend/caffe/` 下，参照 TVM 测试目录结构）
- [ ] 是否需要为不适合转换的场景（如 across_spatial=True）添加明确的注释说明原因？
