# Tasks

> **最近更新**: 2026-08-04
> **状态**: ✅ Phase 1（纯 Python 前向推理）已完成
> **范围**: 仅前向推理，不含 Backward/C++。用户确认"分阶段（先 Python 后 C++）"且"仅前向推理"。

## [x] Task 1: 迁移并提升 numpy 参考实现为内部模块
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 `tests/python/_numpy_rnn_reference.py` 复制为 `python/caffe_ffi/sequence/_numpy_rnn_reference.py`（保持函数签名与行为不变）
  - 验证 `rnn_forward`/`lstm_forward`/`pack_lstm_weights_caffe`/`unpack_lstm_weights_caffe`/`init_rnn_weights`/`init_lstm_weights` 等函数完整
  - 迁移后运行 8 个自测试确认通过
- **Acceptance Criteria Addressed**: 复用既有 numpy 参考实现，8 个自测试通过

## [x] Task 2: 新增 `caffe_ffi.sequence` 子模块（RNN/LSTM 前向 API）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新建 `python/caffe_ffi/sequence/__init__.py`，封装：
    - `RNN` 类：`input_dim`/`hidden_dim`/`activation`（tanh/relu），`load_weights(dict)`/`load_weights(W,b,fmt="caffe")`，`forward(x, batch_first=False, h0=None)` 返回 `(output, h_n)`
    - `LSTM` 类：`input_dim`/`hidden_dim`/`bidirectional`，`load_weights(dict)`/`load_weights(W,b,fmt="caffe")`，`forward(x, batch_first=False, h0=None, c0=None)` 返回 `(output, (h_n, c_n))`
    - 内部复用 `_numpy_rnn_reference` 函数
  - 在 `python/caffe_ffi/__init__.py` 导出 `sequence` 子模块
- **Acceptance Criteria Addressed**: RNN/LSTM 前向 API、Caffe 风格权重加载、双向支持

## [x] Task 3: 新增 RNN/LSTM 前向测试 `test_sequence_forward.py`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 已知值测试（复用手算值，如 tanh 单步、零权重 LSTM）
  - 布局测试：`T×N×D` 与 `N×T×D`（batch_first）互相一致
  - 形状测试：RNN `(T,N,H)`/`(N,H)`，LSTM `(T,N,H)`/`(N,H)`，双向 `2*H`/`(2,N,H)`
  - Caffe 风格打包权重加载与前向一致性
  - 末态正确性（`h_n`/`c_n`）
  - numpy 自洽性（与参考实现一致）
- **Acceptance Criteria Addressed**: 全量测试通过

## [x] Task 4: 新增 `examples/rnn_forward.py` 示例
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 展示 RNN/LSTM 前向推理、权重初始化、batch_first 用法
  - 可独立运行（`python examples/rnn_forward.py`）
- **Acceptance Criteria Addressed**: 可运行示例

## [x] Task 5: 更新 `caffe-ffi-tvm-integration` 规范文档
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 更新 `tasks.md` Task 30 状态：标注 Phase 1（纯 Python 前向）已完成，Phase 2（C++）待启动
  - 更新 `spec.md`/`checklist.md` 的 RNN/LSTM 相关进度
- **Acceptance Criteria Addressed**: 文档与实现状态一致

# Task Dependencies

- Task 1 → Task 2 → Task 3
- Task 2 → Task 4
- Task 3 → Task 5
- Task 1/2/3/4 可并行安排的：Task 1 独立；Task 2/4 依赖 Task 1；Task 3 依赖 Task 2；Task 5 依赖 Task 3