---
id: "caffe-ffi-rnn-lstm-phase2"
title: "Caffe-FFI: RNN/LSTM 层 C++ 实现与 Backward 梯度验证（Phase 2）"
status: "complete"
progress: "100% - 全部完成（Tasks 1-6；全量回归 1692 passed / 1 skipped）"
last_updated: "2026-08-04"
source: "caffe-ffi-tvm-integration/tasks.md#Task 30 (Phase 2)"
---

# Caffe-FFI: RNN/LSTM 层 C++ 实现与 Backward 梯度验证（Phase 2）Spec

## Current Status（2026-08-04）

Phase 2 已全部完成并通过验收：

- **Tasks 1-6 全部完成**：proto 扩展（`RecurrentParameter`）、numpy backward 参考（`rnn_backward`/`lstm_backward`）、`RecurrentLayer`/`RNNLayer`/`LSTMUnit`/`LSTMLayer` C++ 前向 + BPTT Backward、`test_recurrent_backward.py`（29 用例 L0-L3 验证）、规范文档同步。
- **梯度验证达标**：L0 烟雾测试、L1 手算已知值（`assert_array_equal`）、L2 numpy 参考匹配（`rtol ≤ 1e-5`）、L3 数值梯度端到端（`cos_sim > 0.99`、`norm_ratio ∈ [0.9, 1.1]`）全部通过。
- **关键修复**：LSTM Backward 的 `c_prev` batch 索引步长（`i*H_` → `i*6H_+kCacheC*H_`）；权重梯度延迟到 `BackwardEnd()` 一次性 scatter（避免 T 倍重复累加）。
- **全量回归**：1692 passed / 1 skipped（含既有 P3 全部用例，无回归）。

## Why

`caffe-ffi-tvm-integration` 的 Task 30 Phase 2 需要实现 C++ `RecurrentLayer`（含 `LSTMUnit/LSTMLayer`、`RNNLayer`）并提供 Backward 梯度支持。Phase 1（`caffe-ffi-rnn-lstm-phase1`）已交付纯 Python 前向推理 API（`caffe_ffi.sequence`，16 测试通过），可作为 Phase 2 前向的**数值基准**。

Phase 2 的**核心难点是 Backward 梯度正确性**（尤其 BPTT 时间展开）。当前主规范的 Task 30 Phase 2 规划**未定义任何梯度验证标准**，而项目已沉淀一套成熟的 L0-L1-L2-L3 三层验证工作流（见 [caffe-layer-backward-validation-workflow.md](../../../.agents/docs/knowledge/best-practices/caffe-layer-backward-validation-workflow.md)）。本 Spec 将这套标准**完整显式化**，作为 Phase 2 实现与验收的硬性门槛。

## What Changes

- 新建 C++ Recurrent 系列层：`RecurrentLayer`（通用 RNN 基类）、`RNNLayer`（vanilla RNN）、`LSTMUnit`（LSTM 单元）、`LSTMLayer`（LSTM 序列层）
- 扩展 `caffe.proto`：新增 `RecurrentParameter`（含 `num_steps`、`expose_hidden`、`recurrent_param` 等）
- 实现 Backward：RNN/LSTM 的 BPTT（按时间步反向传播），对权重 `W_ih/W_hh/b_ih/b_hh`（LSTM 含 4 门）与输入 `x`、初始状态 `h0/c0` 计算梯度
- 新增 numpy Backward 参考实现（`_numpy_rnn_reference.py` 由仅前向扩展为含 backward），作为 L2 验证真值
- 新增测试 `test_recurrent_backward.py`：按 L0-L1-L2-L3 标准覆盖
- 前向数值与 Phase 1 的 `caffe_ffi.sequence` 结果对齐（作为 Forward 基准）
- **不涉及**：GPU/CUDA 支持、双向 C++ 实现（若 Phase 2 范围外则留待后续）、分布式训练

## Impact

- **Affected specs**: `caffe-ffi-tvm-integration`（Task 30 Phase 2 状态更新）
- **依赖的既有方法论**（本 Spec 的核心依据）:
  - [caffe-layer-backward-validation-workflow.md](L1-L2-L3 三层验证法)
  - [hand-computed-gradient-verification.md](手算梯度方法论)
  - [numerical-gradient-diagnostic-logging.md](数值梯度诊断日志)
  - [caffe-pooling-max-gradient-routing.md](Winner-takes-all 路由参考)
- **Affected code**:
  - `projects/xuanspace/libs/caffe-ffi/src/layers/`：新增 `recurrent_layer.*`、`rnn_layer.*`、`lstm_unit.*`、`lstm_layer.*`
  - `projects/xuanspace/libs/caffe-ffi/proto/caffe/proto/caffe.proto`：`RecurrentParameter` 扩展
  - `projects/xuanspace/libs/caffe-ffi/tests/python/_numpy_rnn_reference.py`：扩展 backward 参考
  - `projects/xuanspace/libs/caffe-ffi/tests/python/test_recurrent_backward.py`：新增
  - `projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/sequence/`：Phase 1 前向（作为基准，不改）

## ADDED Requirements

### Requirement: Recurrent 层 C++ 实现与 proto 扩展
系统 SHALL 提供 C++ `RecurrentLayer`/`RNNLayer`/`LSTMUnit`/`LSTMLayer`，并在 `caffe.proto` 扩展 `RecurrentParameter`，支持前向与反向（Backward/BPTT）。

#### Scenario: 前向数值对齐 Phase 1 基准
- **WHEN** C++ 层以 Phase 1 相同的权重/输入执行前向
- **THEN** 输出与 `caffe_ffi.sequence`（Phase 1 纯 Python 参考）数值一致（`rtol ≤ 1e-5`，视为 Forward 基准）

#### Scenario: 反向梯度正确
- **WHEN** 对随机配置执行 `backward()`
- **THEN** 输入梯度 `dX`、参数梯度 `dW/db`、初始状态梯度 `dh0/dc0` 均通过 L0-L3 验证标准（见 Requirement: 梯度验证标准）

### Requirement: 梯度验证标准（L0-L1-L2-L3 三层法）
系统 SHALL 对每个 Recurrent 层的 Backward 执行 L0-L1-L2-L3 三层递进验证，每层通过后才进入下一层。该标准是 Phase 2 的**硬性验收门槛**，完整定义如下。

#### Scenario: L0 烟雾测试（不崩溃）
- **WHEN** 以最小配置（`1×1×1×1` 输入、最简参数）执行 `Forward()` + `backward()`
- **THEN** `backward()` 不抛出异常（Access Violation/Segfault），输出 diff 不含 NaN/Inf
- **通过标准**：`net.backward()` 无异常；无 NaN/Inf
- **常见失败**：`param_propagate_down_` 未初始化、bottom/top 向量不匹配、空指针/未初始化 Blob

#### Scenario: L1 手算已知值精确验证
- **WHEN** 以小输入（可手算尺寸）与简单权重（如单位向量/全零）执行 backward
- **THEN** 梯度与手算结果**精确相等**（`assert_array_equal`，非 `allclose`），覆盖核心路由/缩放逻辑
- **通过标准**：至少 1 个非平凡配置用 `assert_array_equal` 通过；覆盖核心梯度路由（BPTT 时间路由、门结构、系数缩放）
- **RNN/LSTM 特例**：单步 LSTM 手算（零权重→全门 `sigmoid(0)=0.5`、`g=tanh(0)=0`）；多步 RNN 手算验证时间路由（`dh_{t-1}` 沿 `W_hh` 回传）
- **常见失败**：门索引错、时间步反向顺序错、系数/符号错、`=` 而非 `+=` 累加

#### Scenario: L2 numpy 参考匹配验证
- **WHEN** 对随机数据（多种参数组合、N>1/C>1）执行 backward，并与 numpy 参考对比
- **THEN** 梯度与 numpy 参考一致（`rtol ≤ 1e-5`，L2 是精确匹配层，不应有数值误差）
- **通过标准**：numpy 参考**基于数学公式独立编写**（非 C++ 翻译）；覆盖 ≥3 种参数组合（`num_steps`/`hidden_dim`/`input_dim` 变化）；覆盖多 batch；每次测试 ≥3 个随机种子；`rtol ≤ 1e-5`
- **关键约束**：Phase 1 的 `_numpy_rnn_reference.py` 仅前向，**numpy backward 参考须新建**（基于 BPTT 公式），覆盖 `dW_ih/dW_hh/db_ih/db_hh`（LSTM 含 4 门）与 `dX`、`dh0/dc0`
- **常见失败**：numpy 与 C++ 的 winner/门选择规则不一致、时间步边界处理不一致、float32 vs float64 精度

#### Scenario: L3 数值梯度端到端验证
- **WHEN** 用中心有限差分计算数值梯度，与 C++ 解析梯度对比
- **THEN** 满足阈值表（见下），覆盖输入梯度 `dX` 与所有参数梯度 `dW/db`
- **通过标准**：`dX` 验证通过；每个参数梯度 `dW/db` 验证通过；分段/路由层使用 `avoid_c1_discontinuity`；诊断日志无未解释 WARNING；`cosine similarity > 0.99`；`norm ratio ∈ [0.9, 1.1]`
- **工具**：`_grad_check_utils`（`numerical_grad_for_input`/`numerical_grad_for_blob`/`assert_grad_close`/`avoid_c1_discontinuity`）
- **L3 阈值表**（依据既有方法论）：

| 层类型 | rtol | atol | 注意事项 |
|--------|------|------|---------|
| 线性组合（RNN 线性投影、LSTM 门线性层） | 1e-3 | 1e-4 | 直接通过 |
| 平滑激活（tanh/sigmoid 门） | 1e-3 | 1e-4 | 直接通过（LSTM 门为平滑函数） |
| 分段激活（RNN `relu` 激活） | 5e-3 | 1e-4 | 必须用 `avoid_c1_discontinuity`（x=0 拐点） |
| 路由/时间步（BPTT 回传） | 5e-3 | 1e-4 | 注意 `W_hh` 回传的时间路由 |

- **常见失败**：BPTT 时间步梯度未正确累加、`W_hh` 回传方向错、初始状态 `h0/c0` 梯度遗漏、浮点精度（长序列 `num_steps` 大时误差累积）

### Requirement: 检查清单（验收门槛）
系统 SHALL 在每个 Recurrent 层 Backward 完成后逐项确认以下清单，全部通过方视为完成。

#### Scenario: 分层检查
- **L0**：最简配置 Backward 不崩溃；输出 diff 无 NaN/Inf
- **L1**：至少 1 个手算配置 `assert_array_equal` 通过；覆盖核心路由/缩放逻辑；手算过程有注释
- **L2**：numpy 参考基于数学公式（非 C++ 翻译）；≥3 种参数组合；覆盖 N>1/C>1；`rtol ≤ 1e-5`
- **L3**：`dX` 验证通过；`dW/db` 每个参数验证通过；分段层用 `avoid_c1_discontinuity`；`cos_sim > 0.99`、`norm_ratio ∈ [0.9, 1.1]`；诊断日志无未解释 WARNING

#### Scenario: 代码质量
- **`param_propagate_down_`** 已在 LayerSetUp 末尾 `resize`（有参数层）
- **Blob reshape** 逻辑正确（`num_steps` 展开的中间 `h_t/c_t` 存储）
- **梯度 `+=` 累加**（非 `=`，避免重叠/多路径/多时间步）
- **测试文件命名**：`test_recurrent_backward.py`；测试类带 `@require_cpp_extension` 装饰器

## MODIFIED Requirements

### Requirement: 现有 numpy 参考实现扩展（前向 + 反向）
`caffe_ffi.sequence._numpy_rnn_reference` 由 Phase 1 的**仅前向**扩展为**含 backward 参考**。前向函数签名/行为保持兼容（Phase 1 的 16 测试与 8 自测试继续通过），新增 backward 函数（如 `rnn_backward`/`lstm_backward`）基于 BPTT 公式独立编写，作为 L2 验证真值。

## REMOVED Requirements

### Requirement: 无
**Reason**: Phase 2 仅新增，不删除既有功能。
**Migration**: 不适用。

## 附：Phase 2 与 Phase 1 的衔接

- Phase 1 交付的 `caffe_ffi.sequence`（纯 Python 前向）作为 Phase 2 **Forward 数值基准**，不修改。
- Phase 2 的 numpy backward 参考可与 Phase 1 的前向参考**共用同一套权重/输入约定**（`T×N×D`、Caffe 风格打包权重 `(4*H, D+H)`）。
- 梯度验证标准（本 Spec 的 L0-L3）为 Phase 2 的**硬性验收门槛**，与项目既有 19 类层 Backward 验证方法论保持一致。