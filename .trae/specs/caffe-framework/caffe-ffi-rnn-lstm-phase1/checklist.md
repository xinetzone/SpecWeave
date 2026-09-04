# Caffe-FFI RNN/LSTM Phase 1 验证检查清单

> **更新日期**: 2026-08-04
> **验证状态**: ✅ Phase 1 实现完成，16 测试通过

## 代码实现检查
- [x] `python/caffe_ffi/sequence/_numpy_rnn_reference.py` 存在且函数签名与行为与原 `tests/python/_numpy_rnn_reference.py` 兼容（fc 校验无差异）
- [x] 迁移后 8 个 numpy 自测试全部通过
- [x] `python/caffe_ffi/sequence/__init__.py` 存在，封装 `RNN` 与 `LSTM` 类
- [x] `RNN.forward()` 返回 `(output, h_n)`，形状正确（`(T,N,H)`/`(N,H)`，batch_first 时 `(N,T,H)`）
- [x] `LSTM.forward()` 返回 `(output, (h_n, c_n))`，形状正确
- [x] `LSTM(bidirectional=True)` 输出隐藏维度 `2*H`，末态 `(2,N,H)`
- [x] `load_weights` 支持字典输入与 Caffe 风格打包权重（`fmt="caffe"`，位置/关键字双形式）
- [x] `python/caffe_ffi/__init__.py` 导出 `sequence` 子模块
- [x] `examples/rnn_forward.py` 可独立运行

## 测试验证
- [x] `tests/python/test_sequence_forward.py` 存在
- [x] 已知值测试通过（手算 tanh 单步、零权重 LSTM）
- [x] 布局测试通过（`T×N×D` 与 `N×T×D` 一致）
- [x] 形状测试通过（RNN/LSTM/双向）
- [x] Caffe 风格权重加载一致测试通过
- [x] 末态正确性测试通过
- [x] numpy 自洽测试通过
- [x] 全量测试通过（新增测试不影响既有 1646 passed）— 新文件 16 passed

## 文档一致性检查
- [x] `caffe-ffi-tvm-integration/tasks.md` Task 30 标注 Phase 1 完成、Phase 2 待启动
- [x] `caffe-ffi-tvm-integration/spec.md`/`checklist.md` RNN/LSTM 进度更新
- [x] 未引入 Backward/C++ RecurrentLayer 相关改动（Phase 2 范围外）