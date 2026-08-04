---
id: "caffe-ffi-rnn-lstm-phase1"
title: "Caffe-FFI: RNN/LSTM 层 Python 前向推理（Phase 1）"
status: "complete"
progress: "100% - Phase 1 完成（纯 Python 前向推理，16 测试通过）"
last_updated: "2026-08-04"
source: "caffe-ffi-tvm-integration/tasks.md#Task 30"
---

# Caffe-FFI: RNN/LSTM 纯 Python 前向推理（Phase 1）Spec

## Why

`caffe-ffi-tvm-integration` 的 Task 30（RNN/LSTM 层实现）是当前最大的遗留任务，完整 C++ `RecurrentLayer` 预估 15-20 工作日。任务备注明确建议：**若仅需前向推理，短期可用 numpy 纯 Python 方案**。当前 `_numpy_rnn_reference.py`（RNN/LSTM numpy 前向参考，8 个自测试通过）已就绪，但仅存在于测试目录，未暴露为 caffe_ffi 用户的正式 API。

本 Spec 交付 **Phase 1（纯 Python 前向推理）**，将已就绪的 numpy 参考实现提升为正式、可测试、可复用的 caffe_ffi 用户 API，为后续 C++ Phase 2 提供数值基准与原型验证，同时满足仅需前向推理的短期用户需求。

## What Changes

- 新增 `caffe_ffi.sequence` 子模块（纯 Python 前向推理 API），封装：
  - `RNN` 类：vanilla RNN 前向（tanh/relu 激活），支持 `T×N×D` 与 `N×T×D`（batch_first）两种布局
  - `LSTM` 类：LSTM 前向（4 门），支持单方向与双向（bidirectional），初始状态 h0/c0
  - 权重加载：字典（`W_ih/W_hh/b_ih/b_hh`）与 Caffe 风格打包权重（`(4*H, D+H)` + `(4*H,)`）双入口
  - `forward(x)` 返回所有时间步输出 `(T,N,H)` 与末态 `(h_n, c_n)`
- 复用并提升 `tests/python/_numpy_rnn_reference.py` 为内部实现（`caffe_ffi/sequence/_numpy_rnn_reference.py`），保持函数签名兼容
- 新增 `examples/rnn_forward.py` 示例：展示 RNN/LSTM 前向推理、权重加载、batch_first
- 新增测试 `tests/python/test_sequence_forward.py`：已知值、布局、形状、双向、Caffe 权重打包、末态、numpy 自洽
- 更新 `caffe-ffi-tvm-integration` 的 `tasks.md`/`spec.md`/`checklist.md` 记录 Task 30 Phase 1 进展
- **不涉及**：C++ `RecurrentLayer`/`LSTMUnit`/`LSTMLayer`/`RNNLayer`、proto `RecurrentParameter` 扩展、Backward 梯度（均留待 Phase 2）

## Impact

- **Affected specs**: `caffe-ffi-tvm-integration`（Task 30 状态更新）
- **Affected code**:
  - `projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/sequence/__init__.py`（新增）
  - `projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/sequence/_numpy_rnn_reference.py`（由 tests 迁移+保持兼容）
  - `projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/__init__.py`（导出 `sequence`）
  - `projects/xuanspace/libs/caffe-ffi/examples/rnn_forward.py`（新增）
  - `projects/xuanspace/libs/caffe-ffi/tests/python/test_sequence_forward.py`（新增）
  - `projects/xuanspace/libs/caffe-ffi/tests/python/_numpy_rnn_reference.py`（保留为兼容代理或删除）

## ADDED Requirements

### Requirement: RNN 前向推理 API
系统 SHALL 提供 `caffe_ffi.sequence.RNN` 类，支持 vanilla RNN 前向计算（`h_t = act(W_ih·x_t + b_ih + W_hh·h_{t-1} + b_hh)`）。

#### Scenario: 成功前向
- **WHEN** 用户构造 `RNN(input_dim, hidden_dim, activation="tanh")` 并 `load_weights(...)` 后调用 `forward(x)`
- **THEN** 返回 `(output, h_n)`，其中 `output` 形状 `(T,N,H)`（或 batch_first 时 `(N,T,H)`），`h_n` 形状 `(N,H)`，数值与 numpy 参考一致

### Requirement: LSTM 前向推理 API
系统 SHALL 提供 `caffe_ffi.sequence.LSTM` 类，支持 LSTM 前向计算（i/f/o/g 四门）、初始状态，以及选项双向（bidirectional）。

#### Scenario: 双向 LSTM
- **WHEN** 用户构造 `LSTM(input_dim, hidden_dim, bidirectional=True)` 并前向
- **THEN** 输出隐藏维度为 `2*H`，末态 `(h_n, c_n)` 形状为 `(2, N, H)`（forward/backward 两层）

### Requirement: Caffe 风格权重加载
系统 SHALL 支持从 Caffe 风格打包权重 `(4*H, D+H)` + `(4*H,)`（`pack_lstm_weights_caffe` 产物）加载 LSTM 权重。

#### Scenario: 打包权重加载
- **WHEN** 用户 `load_weights(packed_W, packed_b, fmt="caffe")`
- **THEN** 内部正确拆分 i/f/o/g 四门权重与偏置，前向数值与 `unpack_lstm_weights_caffe` 后逐门计算一致

## MODIFIED Requirements

### Requirement: 现有 numpy 参考实现复用
`tests/python/_numpy_rnn_reference.py` 从测试目录提升为内部实现模块，保持 `rnn_forward`/`lstm_forward`/`pack_lstm_weights_caffe`/`unpack_lstm_weights_caffe` 等函数签名与行为不变，确保既有 8 个自测试继续通过（迁移到 `caffe_ffi.sequence._numpy_rnn_reference` 后仍可运行）。

## REMOVED Requirements

### Requirement: 无
**Reason**: Phase 1 仅新增，不删除既有功能。
**Migration**: 不适用。