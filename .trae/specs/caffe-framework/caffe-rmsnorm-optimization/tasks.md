# Caffe Normalize→RMSNorm 代码优化 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 重构辅助函数，合并判定与参数计算逻辑
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 优化 `_should_convert_normalize_to_rmsnorm` 函数，使其在判定可转换的同时直接返回计算好的 rms_weight、rms_epsilon、rms_axis、transpose_axes、inverse_axes，避免后续重复调用
  - 或创建新的合并函数 `_try_prepare_rmsnorm_conversion`，一次性完成条件检查和参数准备
  - 保持原有三个辅助函数的向后兼容性（现有 CI 测试依赖它们）
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: 重构后 `_normalize_rmsnorm_params` 和 `_normalize_rmsnorm_plan` 在 convert_normalize 主路径中各只被调用一次（或通过合并函数只调用一次）
  - `programmatic` TR-1.2: 现有的 test_caffe_normalize_rmsnorm.py 中所有单元测试继续通过
  - `programmatic` TR-1.3: 当 op 在 model_outputs 中时返回 False/None，不执行转换
  - `programmatic` TR-1.4: 当 axis 为多轴（across_spatial=True）时返回 None，安全回退
- **Notes**: 可以选择创建新的合并函数而非修改原有函数签名，以确保完全向后兼容

## [x] Task 2: 优化 convert_normalize 中的 RMSNorm 转换分支代码
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 Task 1 的合并函数重构第 549-560 行代码
  - 提取长表达式为命名中间变量（如 `needs_transpose`、`rms_input_expr`）
  - 为关键步骤添加注释说明：重参数化公式、axis 转置策略
  - 添加防御性校验：确保参数不为 None 才执行 RMSNorm 路径
  - 理顺逻辑流，使代码结构清晰
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 代码审查确认无重复辅助函数调用
  - `human-judgement` TR-2.2: 代码有清晰注释，关键步骤有数学原理说明
  - `programmatic` TR-2.3: 转换失败时安全回退到 L2 normalize 路径，不抛出异常

## [x] Task 3: 为优化后的转换逻辑添加端到端数值等价性测试
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 参照 test_rms_norm.py 的测试标准，在 `tests/python/ci/` 目录下扩展测试（或创建新测试文件）
  - 使用 Relay 表达式构建实际计算图，验证 RMSNorm 转换路径与 L2 normalize 路径的数值等价性
  - 测试覆盖：
    - 不同 shape: (N,C), (N,C,H), (N,C,H,W), (N,C,D,H,W) 等
    - axis=1（标准 channel 轴）的情况
    - across_spatial=False（单轴归一化，可转 RMSNorm）
    - across_spatial=True（多轴归一化，不可转 RMSNorm）
    - channel_shared=True/False
    - 不同 eps 值（1e-10, 1e-5, 1e-3 等）
    - 负 axis 索引
  - 数值精度要求：max_abs_diff ≤ 1e-6（float32）
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 测试覆盖至少 20 种 shape/axis/eps 组合
  - `programmatic` TR-3.2: 所有测试用例的 max_abs_diff ≤ 1e-6
  - `programmatic` TR-3.3: across_spatial=True 时不使用 RMSNorm 路径
  - `programmatic` TR-3.4: 测试无需 NPU 硬件，纯 CPU/NumPy 即可运行

## [x] Task 4: 验证现有测试无回归
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 运行 TVM caffe frontend 现有测试，确保优化不引入回归
  - 运行 test_forward.py 中的 Normalize 相关测试
  - 运行 test_caffe_normalize_rmsnorm.py 确保原有辅助函数测试继续通过
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: test_caffe_normalize_rmsnorm.py 全部通过
  - `programmatic` TR-4.2: caffe frontend 其他相关测试无失败

## [x] Task 5: 代码风格与最终审查
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 检查代码风格与 caffe.py 现有风格一致（缩进、命名、空行等）
  - 检查注释准确性，不添加冗余注释
  - 验证无多余的 import 或未使用变量
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-5.1: 代码风格与文件现有风格一致
  - `human-judgement` TR-5.2: 注释简洁准确，解释"为什么"而非"是什么"
