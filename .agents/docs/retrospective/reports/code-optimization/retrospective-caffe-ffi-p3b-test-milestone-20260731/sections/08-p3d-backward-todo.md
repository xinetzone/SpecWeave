---
title: P3-D Backward实现待办清单
date: 2026-08-03
category: code-optimization
task_type: planning
tags: [caffe-ffi, backward, p3d, todo, implementation-plan]
status: in-progress
source: "retrospective-caffe-ffi-p3b-test-milestone-20260731/README.md#p3-d-backward"
---

# P3-D Backward实现待办清单

## 概述

P3-C阶段完成11层Backward验证后，剩余需要实现Backward的训练层共**5层**（Dropout已完成）。本清单按优先级排序，目标是实现所有训练必需层的Backward，支持端到端CNN训练。

### 完成定义（DoD）

每个层的Backward实现完成需满足：
1. ✅ C++头文件声明`Backward_cpu`
2. ✅ C++实现文件添加`Backward_cpu`函数体
3. ✅ 实现遵循现有代码风格（perf日志、值域统计、propagate_down检查）
4. ✅ 有blobs_的层在LayerSetUp末尾正确初始化`param_propagate_down_`
5. ✅ 测试文件覆盖：已知值验证 + numpy解析梯度对比 + 中心有限差分数值梯度 + 零梯度 + 形状 + 确定性 + Forward保持
6. ✅ 编译0错误0警告
7. ✅ 所有测试PASSED
8. ✅ 无回归（现有Forward/Backward测试不受影响）

---

## 待办事项

### ACT-14：Dropout层Backward实现 ✅ 已完成

| 项目 | 详情 |
|------|------|
| **优先级** | P0（最简单，无参数，identity pass-through） |
| **状态** | ✅ 已完成（2026-08-03） |
| **实际工作量** | ~30分钟（实现10min + 编译5min + 测试10min + 文档5min） |
| **C++文件** | [dropout_layer.hpp](../../../../../../projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/layers/dropout_layer.hpp)、[dropout_layer.cpp](../../../../../../projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/dropout_layer.cpp) |
| **测试文件** | [test_dropout_backward.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_dropout_backward.py)（20个用例） |

**Backward公式**：
- 当前实现仅支持inference模式（Forward是identity copy）
- inference模式下：`dX = dy`（梯度直通pass-through）
- 无learnable参数，无`param_propagate_down_`需要初始化

**实现记录**：
1. ✅ hpp: protected区域添加`Backward_cpu`声明
2. ✅ cpp: 实现Backward_cpu：propagate_down检查 + memcpy（非inplace时）+ perf日志
3. ✅ 测试：20个用例全部通过（identity验证 + 4种ratio + 2D/3D/4D形状 + 数值梯度 + inplace测试）
4. ✅ 无回归

**测试结果**：20 passed in 0.19s，详见[06-p3d-backward-plan.md](06-p3d-backward-plan.md)。

---

### ACT-15：Bias层Backward实现 ✅ 已完成

| 项目 | 详情 |
|------|------|
| **优先级** | P0（加法层，梯度简单） |
| **状态** | ✅ 已完成（2026-08-03） |
| **实际工作量** | ~45分钟（实现15min + 测试20min + 文档10min） |
| **C++文件** | [bias_layer.hpp](../../../../../../projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/layers/bias_layer.hpp)、[bias_layer.cpp](../../../../../../projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/bias_layer.cpp) |
| **测试文件** | [test_bias_backward.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_bias_backward.py)（19个用例） |
| **前置检查** | `param_propagate_down_`已在Line 53初始化 ✅ |

**Backward公式**：
- Forward: `y = x + bias`（广播加法，bias沿outer_dim×inner_dim广播）
- `dX = dy`（bias是加法，梯度直接传过）
- `d_bias = sum(dy, axis=外维+内维)`（对非bias维度求和）
- 支持多轴bias（num_axes > 1，如Transformer位置编码bias shape (T,D)）
- 1个learnable参数：blobs_[0]（bias）

**实现记录**：
1. ✅ hpp: protected区域添加`Backward_cpu`声明
2. ✅ cpp: 实现Backward_cpu：单次遍历三层循环同时计算dX/d_bias
3. ✅ 支持bias_from_bottom（外部输入bias）和bias_from_blobs（learnable）两种模式
4. ✅ 多轴bias支持（num_axes=2时bias shape匹配input的连续维度）
5. ✅ 值域统计+PERF日志（[BIAS-PERF]前缀）
6. ✅ 测试：19个用例（L1手算2个+L2 numpy对比10个+L3数值梯度2个+属性测试5个）
7. ✅ param_propagate_down_在LayerSetUp第53行正确初始化

**测试结果**：19 passed in 0.22s

---

### ACT-16：Scale层Backward实现 ✅ 已完成

| 项目 | 详情 |
|------|------|
| **优先级** | P1（乘法层，梯度稍复杂） |
| **状态** | ✅ 已完成（2026-08-03） |
| **实际工作量** | ~75分钟（代码30min + 测试30min + 文档15min） |
| **C++文件** | [scale_layer.hpp](../../../../../../projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/layers/scale_layer.hpp)、[scale_layer.cpp](../../../../../../projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/scale_layer.cpp) |
| **测试文件** | [test_scale_backward.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_scale_backward.py)（25个用例） |

**Backward公式**：
- Forward: `y = alpha * x + beta`（alpha必选，beta可选bias_term）
- `dX = dy * alpha`
- `d_alpha = sum(dy * x)` over broadcast dimensions
- `d_beta = sum(dy)` over broadcast dimensions（如果bias_term=true）
- 最多2个learnable参数：blobs_[0]（alpha）、blobs_[1]（beta，可选）

**实现记录**：
1. ✅ hpp: 添加`Backward_cpu`声明（override）
2. ✅ cpp: 实现Backward_cpu：单次遍历三层循环同时计算dX/dα/dβ
3. ✅ 支持scale_from_bottom（外部输入scale）和scale_from_blobs（learnable）两种模式
4. ✅ bias_param_idx正确映射（scale从blobs_[0]时bias在[1]，scale从bottom[1]时bias在[0]）
5. ✅ 值域统计+PERF日志（[SCALE-PERF]前缀）
6. ✅ 测试：25个用例（L1手算6个+L2 numpy对比6个+L3数值梯度3个+属性测试10个）
7. ✅ param_propagate_down_在LayerSetUp第75行正确初始化
8. ✅ 代码审查通过，无未使用变量，索引与Forward完全一致

**测试结果**：25 passed in 0.25s

---

### ACT-17：Eltwise层Backward实现 ✅ 已完成

| 项目 | 详情 |
|------|------|
| **优先级** | P1（三种操作：SUM/PROD/MAX，MAX需要winner mask） |
| **状态** | ✅ 已完成（2026-08-03） |
| **实际工作量** | ~70分钟（代码25min + 测试35min + 文档10min） |
| **C++文件** | [eltwise_layer.hpp](../../../../../../projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/layers/eltwise_layer.hpp)、[eltwise_layer.cpp](../../../../../../projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/eltwise_layer.cpp) |
| **测试文件** | [test_eltwise_backward.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_eltwise_backward.py)（32个用例） |
| **无learnable参数** | 无需param_propagate_down_初始化 |

**Backward公式**：
- **SUM**: `dX_j[i] = dy[i] * coeffs[j]`（每个bottom获得coeff加权的梯度）
- **PROD**: `dX_j[i] = dy[i] * coeffs[j] * prod_{k≠j}(coeffs[k] * x_k[i])`（乘积的导数是其他输入之积×coeff，含除零保护）
- **MAX**: `dX_j[i] = dy[i] * coeffs[j]` if j is winner, else 0（winner-take-all，max_idx_缓存winner索引）

**实现记录**：
1. ✅ hpp: 添加`Backward_cpu`声明 + `max_idx_`成员变量（`std::vector<int>`）
2. ✅ cpp: Reshape中分配max_idx_空间（仅MAX模式）
3. ✅ cpp: Forward MAX分支记录winner索引（`if (val > top_data[i])`更新，第一个最大值获胜）
4. ✅ cpp: Backward实现三种模式：
   - SUM：直接分配`dy * coeffs[j]`，单次遍历
   - PROD：逐元素计算总乘积，用除法快速路径（xj≠0时）+ 直接计算fallback（xj=0时避免除零）
   - MAX：根据max_idx_做winner-take-all路由
5. ✅ PERF日志（[ELTWISE-PERF]前缀）+ 值域统计
6. ✅ 测试：32个用例（L1手算4个+L2 numpy对比10个+L3数值梯度8个+L4属性10个）
7. ✅ 支持任意数量输入（2/3个bottom）和coeff加权

**Winner mask缓存逻辑**：
- Forward MAX模式：初始化max_idx_[i]=0，遍历j=1..num_bottoms，当`bj*cj > current_max`时更新max_idx_[i]=j
- Backward MAX模式：遍历每个位置i，将dy*coeffs[winner]路由到winner的bottom_diff，非winner保持0（已memset清零）
- 与std::max语义一致：相等时保留第一个遇到的最大值（第一个winner）

**测试结果**：32 passed in 0.29s，回归测试64/64通过（Scale+Bias+Dropout无回归）

---

### ACT-18：Concat层Backward实现 🟡 P1

| 项目 | 详情 |
|------|------|
| **优先级** | P1（通道拆分，Slice反向操作） |
| **状态** | 📋 待实现 |
| **预估工作量** | 实现30分钟 + 测试45分钟 = 75分钟 |
| **C++文件** | `include/caffe_ffi/layers/concat_layer.hpp`、`src/caffe_ffi/layers/concat_layer.cpp` |
| **测试文件** | `tests/python/test_concat_backward.py`（新建） |
| **无learnable参数** | 无需param_propagate_down_初始化 |

**Backward公式**：
- Forward: 沿concat_axis拼接多个bottom → 一个top
- Backward: 沿同一axis将top_diff拆分到各bottom_diff
- `dX[i] = slice(dy, concat_axis, offset_i, offset_i + channels_i)`

**实现注意**：
- 需要记录每个bottom在concat轴上的offset（Forward时已知）
- 类似于Slice的Forward，但方向相反

**实现步骤**：
1. hpp: 添加`Backward_cpu`声明
2. cpp: 实现Backward：
   - 遍历每个bottom
   - 计算在concat轴上的起止位置
   - 将对应slice复制到底部diff
   - 支持axis=0/1/2/3
   - perf日志
3. 测试文件：6个用例（拆分验证 + 数值梯度 + 零梯度 + 形状 + 往返还原 + 多输入）

**验收标准**：6个测试用例全部PASSED，数值梯度rtol≤1e-3。

---

### ACT-19：Softmax层Backward实现 🟡 P2

| 项目 | 详情 |
|------|------|
| **优先级** | P2（通常配合SoftmaxWithLoss使用，独立Softmax BW需求较低） |
| **状态** | 📋 待实现 |
| **预估工作量** | 实现45分钟 + 测试45分钟 = 90分钟 |
| **C++文件** | `include/caffe_ffi/layers/softmax_layer.hpp`、`src/caffe_ffi/layers/softmax_layer.cpp` |
| **测试文件** | `tests/python/test_softmax_backward.py`（新建） |
| **无learnable参数** | 无需param_propagate_down_初始化 |

**Backward公式**：
- Forward: `y_i = exp(x_i) / sum_j(exp(x_j))`（softmax概率）
- Backward（Jacobian向量积）: `dx_i = y_i * (dy_i - sum_j(dy_j * y_j))`
- 等价于: `dX = dy * y - y * sum(dy * y)`（先计算dot=sum(dy*y)，再逐元素计算）

**实现注意**：
- 需要在Forward时缓存softmax输出（top_data），或在Backward时重新计算
- 数值稳定性：使用与Forward相同的max subtraction技巧

**实现步骤**：
1. hpp: 添加`Backward_cpu`声明
2. cpp: 实现Backward：
   - 获取top_data（softmax概率）
   - 计算`dot = sum(top_diff * top_data)` per sample
   - `bottom_diff = top_diff * top_data - top_data * dot`
   - perf日志
3. 测试文件：6个用例（解析梯度 + 数值梯度 + one-hot + uniform + 形状 + 零梯度）

**验收标准**：6个测试用例全部PASSED，数值梯度rtol≤1e-3。

---

## P3遗留：测试补齐（无需C++实现）

以下层Backward_cpu已存在，仅缺测试覆盖：

| 行动项 | 优先级 | 层 | 预估 | 说明 |
|--------|:------:|-----|------|------|
| ACT-20 | 🟡 P2 | Split | 30分钟 | 梯度累加验证（多个top梯度求和到底部）+ 数值梯度 |
| ACT-21 | 🟡 P2 | Slice | 30分钟 | 梯度路由验证（按slice_point分发）+ 数值梯度 |
| ACT-22 | 🟡 P2 | LRN | 45分钟 | 局部响应归一化梯度 + 数值梯度（公式较复杂） |
| ACT-23 | 🟢 P3 | Crop | 30分钟 | 梯度复制+zero-pad验证（裁剪区域复制梯度，其余为0） |

---

## 工作量汇总

| 类别 | 实现时间 | 测试时间 | 合计 | 状态 |
|------|---------|---------|------|:----:|
| ~~P0（Dropout）~~ | ~~15min~~ | ~~30min~~ | ~~45min~~ | ✅ 完成 |
| ~~P0（Bias）~~ | ~~15min~~ | ~~30min~~ | ~~45min~~ | ✅ 完成 |
| ~~P1（Scale）~~ | ~~30min~~ | ~~45min~~ | ~~75min~~ | ✅ 完成 |
| ~~P1（Eltwise）~~ | ~~25min~~ | ~~35min~~ | ~~60min~~ | ✅ 完成 |
| P1（Concat） | 30min | 45min | **75min** | 📋 |
| P2（Softmax+Split+Slice+LRN） | 105min | 150min | **4h15min** | 📋 |
| P3（Crop测试） | 0min | 30min | **30min** | 📋 |
| **剩余合计** | **2h15min** | **3h45min** | **~6h** | |

## 端到端训练目标

端到端梯度流验证脚本已就绪：[test_e2e_gradient_flow.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_e2e_gradient_flow.py)

```
Data → Conv → BN → ReLU → Pool → IP → ReLU → Dropout → Scale → Bias → IP → SoftmaxWithLoss → Loss
       ✅    ✅   ✅    ✅     ✅    ✅     ✅       ✅      ✅     ✅     ✅         ✅
```

> Dropout✅、Scale✅、Bias✅完成，端到端Backward路径中除Softmax本身外均已实现。Conv/IP/BN/Pool/ReLU已验证，Dropout/Scale/Bias测试全部通过。

验证目标（e2e脚本6个测试用例）：
1. Forward完整运行无崩溃
2. Backward完整运行无崩溃
3. 所有参数梯度有限且非零（Conv/IP权重+bias）
4. Dropout梯度直通验证（drop1 diff == relu2 diff）
5. 多步SGD：Loss随训练步下降（梯度有效性）
6. 梯度范数稳定（非NaN/Inf/爆炸/消失）

## 关键约束与检查清单

新增Backward实现时必查：
- [ ] 头文件声明`Backward_cpu`（override）
- [ ] cpp实现包含`propagate_down`检查
- [ ] 有blobs_的层：LayerSetUp末尾`param_propagate_down_.resize(blobs_.size(), true)`
- [ ] perf日志格式与现有层一致（`[LAYER-PERF]`前缀+值域统计+耗时）
- [ ] 测试文件：numpy参考实现先行
- [ ] 测试覆盖三层验证：已知值→解析梯度→数值梯度
- [ ] 数值梯度rtol≤1e-3，使用`avoid_c1_discontinuity`防护（如适用）
- [ ] 编译0错误0警告
- [ ] 所有测试PASSED，现有测试无回归
