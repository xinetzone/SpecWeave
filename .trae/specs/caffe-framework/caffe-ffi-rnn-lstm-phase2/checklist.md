# Caffe-FFI RNN/LSTM Phase 2 验证检查清单

> **更新日期**: 2026-08-04
> **验证状态**: ✅ 全部通过（全量回归 1692 passed / 1 skipped）

## proto 扩展检查
- [x] `caffe.proto` 含 `RecurrentParameter`（`num_steps`/`expose_hidden`/`recurrent_param`）
- [x] 预生成 `caffe_pb2.py` 已提交，网络可解析

## 代码实现检查
- [x] `_numpy_rnn_reference.py` 新增 `rnn_backward`/`lstm_backward`（基于 BPTT 公式，非 C++ 翻译）
- [x] numpy backward 覆盖 `dW_ih/dW_hh/db_ih/db_hh`（LSTM 含 4 门）、`dX`、`dh0/dc0`
- [x] 前向函数保持兼容（Phase 1 的 16 测试与 8 自测试继续通过）
- [x] `RecurrentLayer`/`RNNLayer` 前向 + BPTT Backward 实现
- [x] `LSTMUnit`/`LSTMLayer` 前向 + BPTT Backward 实现
- [x] `param_propagate_down_` 已在 LayerSetUp 末尾 `resize`（有参数层）
- [x] 梯度使用 `+=` 累加（多时间步/多路径）
- [x] 前向数值与 Phase 1 对齐（`rtol ≤ 1e-5`）

## L0 烟雾测试
- [x] 最小配置 Backward 不崩溃
- [x] 输出 diff 无 NaN/Inf

## L1 手算已知值验证
- [x] 至少 1 个手算配置 `assert_array_equal` 通过
- [x] 覆盖核心梯度路由（BPTT 时间路由、门结构、系数缩放）
- [x] 手算过程有注释（单步 LSTM 零权重、多步 RNN 时间路由）

## L2 numpy 参考匹配验证
- [x] numpy 参考基于数学公式（非 C++ 翻译）
- [x] ≥3 种参数组合（`num_steps`/`hidden_dim`/`input_dim` 变化）
- [x] 覆盖多 batch（N>1）
- [x] 每次测试 ≥3 个随机种子
- [x] `rtol ≤ 1e-5`

## L3 数值梯度端到端验证
- [x] 输入梯度 `dX` 验证通过
- [x] 每个参数梯度 `dW/db` 验证通过
- [x] 初始状态梯度 `dh0/dc0` 验证通过
- [x] 分段/路由层使用 `avoid_c1_discontinuity`
- [x] `cosine similarity > 0.99`
- [x] `norm ratio ∈ [0.9, 1.1]`
- [x] 诊断日志无未解释 WARNING

## 测试与文档
- [x] `tests/python/test_recurrent_backward.py` 存在，测试类带 `@require_cpp_extension`
- [x] 全量测试通过（新增不影响既有 1646 passed；实际 1692 passed / 1 skipped）
- [x] `caffe-ffi-tvm-integration/tasks.md` Task 30 标注 Phase 2 完成
- [x] `caffe-ffi-tvm-integration/spec.md`/`checklist.md` RNN/LSTM 进度更新