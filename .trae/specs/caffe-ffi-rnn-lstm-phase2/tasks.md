# Tasks

> **最近更新**: 2026-08-04
> **状态**: 🔄 实现中（Tasks 1-4 已完成并编译通过；Task 5 测试待运行）
> **范围**: 含 Backward/BPTT。梯度验证遵循 L0-L1-L2-L3 三层法（见 spec.md 梯度验证标准）。
> **前置**: Phase 1（`caffe-ffi-rnn-lstm-phase1`）纯 Python 前向已完成，作为 Forward 数值基准。

## [x] Task 1: 扩展 `caffe.proto` 新增 `RecurrentParameter`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `proto/caffe/proto/caffe.proto` 新增 `RecurrentParameter`（`num_steps`、`expose_hidden`、`recurrent_param` 等）
  - 重新生成并提交 `caffe_pb2.py`（protobuf 预生成 pb2.py 提交仓库，开箱即用）
- **Acceptance Criteria Addressed**: proto 定义可用，网络可解析

## [x] Task 2: 新增 numpy backward 参考实现（`_numpy_rnn_reference` 扩展）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `_numpy_rnn_reference.py` 新增 `rnn_backward`/`lstm_backward`（基于 BPTT 公式独立编写，非 C++ 翻译）
  - 覆盖 `dW_ih/dW_hh/db_ih/db_hh`（LSTM 含 4 门）、`dX`、`dh0/dc0`
  - 前向函数签名/行为保持兼容（Phase 1 的 16 测试与 8 自测试继续通过）
- **Acceptance Criteria Addressed**: L2 验证真值可用

## [x] Task 3: 实现 `RecurrentLayer`/`RNNLayer`（前向 + Backward）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `RecurrentLayer` 基类：时间步展开、中间 `h_t` 存储、`param_propagate_down_` 初始化
  - `RNNLayer`：vanilla RNN 前向 + BPTT Backward（`relu` 激活需 C¹ 拐点防护）
  - 前向数值与 Phase 1 对齐（`rtol ≤ 1e-5`）
- **Acceptance Criteria Addressed**: RNN 前向 + Backward 实现

## [x] Task 4: 实现 `LSTMUnit`/`LSTMLayer`（前向 + Backward）
- **Priority**: high
- **Depends On**: Task 3, Task 1
- **Description**:
  - `LSTMUnit`：单步 LSTM 单元（i/f/o/g 四门），可独立实现
  - `LSTMLayer`：LSTM 序列层，**复用 `RecurrentLayer` 基类的时间步展开**，前向 + BPTT Backward
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

- Task 1 → Task 3
- Task 3 → Task 4（`LSTMLayer` 复用 `RecurrentLayer` 基类的时间步展开，故 Task 4 须在 Task 3 之后）
- Task 2 → Task 5（独立，可与 Task 1 并行）
- Task 3/4 → Task 5
- Task 5 → Task 6
- Task 2 独立（可与 Task 1 并行）；但**建议 Task 2 排在 Task 3/4 之前**，确保 numpy backward 参考基于数学公式独立编写（非 C++ 翻译），避免被 C++ 实现污染
- Task 3 与 Task 4 **不并行**：Task 4 依赖 Task 3 的 `RecurrentLayer` 基类（LSTMUnit 单元本身可独立，但 LSTMLayer 序列层复用基类）

# Task 4-6 依赖检查结论

- **Task 4 依赖调整**：原 `Depends On: Task 1` → 改为 `Task 3, Task 1`。因 `LSTMLayer` 继承/复用 `RecurrentLayer` 基类（spec 明确定位为"通用 RNN 基类"承担时间步展开），必须先实现基类。
- **Task 5 依赖正确**：依赖 Task 3/4（C++ 层）+ Task 2（numpy backward 参考），三者齐备才能做 L0-L3 验证。
- **Task 6 依赖正确**：文档更新须在测试通过（Task 5）之后，避免文档与实现状态不一致。
- **实现顺序**：Task 1 → Task 3 → Task 4 → Task 5 → Task 6，Task 2 与 Task 1 并行（且建议先于 Task 3/4 完成）。