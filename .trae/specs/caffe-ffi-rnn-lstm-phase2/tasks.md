# Tasks

> **最近更新**: 2026-08-04
> **状态**: ⬜ 待实现（Phase 2：C++ Recurrent 层 + Backward 梯度验证）
> **范围**: 含 Backward/BPTT。梯度验证遵循 L0-L1-L2-L3 三层法（见 spec.md 梯度验证标准）。
> **前置**: Phase 1（`caffe-ffi-rnn-lstm-phase1`）纯 Python 前向已完成，作为 Forward 数值基准。

## [ ] Task 1: 扩展 `caffe.proto` 新增 `RecurrentParameter`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `proto/caffe/proto/caffe.proto` 新增 `RecurrentParameter`（`num_steps`、`expose_hidden`、`recurrent_param` 等）
  - 重新生成并提交 `caffe_pb2.py`（protobuf 预生成 pb2.py 提交仓库，开箱即用）
- **Acceptance Criteria Addressed**: proto 定义可用，网络可解析

## [ ] Task 2: 新增 numpy backward 参考实现（`_numpy_rnn_reference` 扩展）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `_numpy_rnn_reference.py` 新增 `rnn_backward`/`lstm_backward`（基于 BPTT 公式独立编写，非 C++ 翻译）
  - 覆盖 `dW_ih/dW_hh/db_ih/db_hh`（LSTM 含 4 门）、`dX`、`dh0/dc0`
  - 前向函数签名/行为保持兼容（Phase 1 的 16 测试与 8 自测试继续通过）
- **Acceptance Criteria Addressed**: L2 验证真值可用

## [ ] Task 3: 实现 `RecurrentLayer`/`RNNLayer`（前向 + Backward）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `RecurrentLayer` 基类：时间步展开、中间 `h_t` 存储、`param_propagate_down_` 初始化
  - `RNNLayer`：vanilla RNN 前向 + BPTT Backward（`relu` 激活需 C¹ 拐点防护）
  - 前向数值与 Phase 1 对齐（`rtol ≤ 1e-5`）
- **Acceptance Criteria Addressed**: RNN 前向 + Backward 实现

## [ ] Task 4: 实现 `LSTMUnit`/`LSTMLayer`（前向 + Backward）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `LSTMUnit`：单步 LSTM 单元（i/f/o/g 四门）
  - `LSTMLayer`：LSTM 序列层，时间步展开，前向 + BPTT Backward
  - 前向数值与 Phase 1 对齐（`rtol ≤ 1e-5`）
- **Acceptance Criteria Addressed**: LSTM 前向 + Backward 实现

## [ ] Task 5: 新增 `test_recurrent_backward.py`（L0-L1-L2-L3 验证）
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 2
- **Description**:
  - L0：最小配置 Backward 不崩溃、无 NaN/Inf
  - L1：手算已知值精确验证（`assert_array_equal`；单步 LSTM 零权重、多步 RNN 时间路由）
  - L2：numpy 参考匹配（≥3 种参数组合、N>1、≥3 随机种子、`rtol ≤ 1e-5`）
  - L3：数值梯度端到端（`dX` + 每个 `dW/db` + `dh0/dc0`；`_grad_check_utils`；分段层 `avoid_c1_discontinuity`；`cos_sim > 0.99`、`norm_ratio ∈ [0.9, 1.1]`）
- **Acceptance Criteria Addressed**: 全量测试通过（新增不影响既有 1646 passed）

## [ ] Task 6: 更新 `caffe-ffi-tvm-integration` 规范文档
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 更新 `tasks.md` Task 30 状态：Phase 2 完成
  - 更新 `spec.md`/`checklist.md` 的 RNN/LSTM 进度
- **Acceptance Criteria Addressed**: 文档与实现状态一致

# Task Dependencies

- Task 1 → Task 3/4
- Task 2 → Task 5
- Task 3/4 → Task 5
- Task 5 → Task 6
- Task 2 独立（可与 Task 1 并行）；Task 3/4 可并行（依赖 Task 1）