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

P3-C阶段完成11层Backward验证后，剩余需要实现Backward的训练层共**6层**。本清单按优先级排序，目标是实现所有训练必需层的Backward，支持端到端CNN训练。

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

### ACT-14：Dropout层Backward实现 🔴 P0

| 项目 | 详情 |
|------|------|
| **优先级** | P0（最简单，无参数，identity pass-through） |
| **状态** | 📋 待实现 |
| **预估工作量** | 实现15分钟 + 测试30分钟 = 45分钟 |
| **C++文件** | `include/caffe_ffi/layers/dropout_layer.hpp`、`src/caffe_ffi/layers/dropout_layer.cpp` |
| **测试文件** | `tests/python/test_dropout_backward.py`（新建） |

**Backward公式**：
- 当前实现仅支持inference模式（Forward是identity copy）
- inference模式下：`dX = dy`（梯度直通pass-through）
- 无learnable参数，无`param_propagate_down_`需要初始化

**实现步骤**：
1. hpp: protected区域添加`Backward_cpu`声明
2. cpp: Forward_cpu之后添加`Backward_cpu`实现：
   - `propagate_down[0]`检查
   - `count = bottom[0]->count()`
   - inplace或memcpy：`bottom_diff[i] = top_diff[i]`（identity）
   - perf日志：count、diff值域、耗时
3. 测试文件：6个用例（见06-p3d-backward-plan.md）

**验收标准**：6个测试用例全部PASSED，数值梯度rtol≤1e-3。

---

### ACT-15：Bias层Backward实现 🔴 P0

| 项目 | 详情 |
|------|------|
| **优先级** | P0（加法层，梯度简单） |
| **状态** | 📋 待实现 |
| **预估工作量** | 实现30分钟 + 测试45分钟 = 75分钟 |
| **C++文件** | `include/caffe_ffi/layers/bias_layer.hpp`、`src/caffe_ffi/layers/bias_layer.cpp` |
| **测试文件** | `tests/python/test_bias_backward.py`（新建） |
| **前置检查** | `param_propagate_down_`已在Line 52初始化 ✅ |

**Backward公式**：
- Forward: `y = x + bias`（广播加法，bias沿outer_dim×inner_dim广播）
- `dX = dy`（bias是加法，梯度直接传过）
- `d_bias = sum(dy, axis=外维+内维)`（对非bias维度求和）
- 1个learnable参数：blobs_[0]（bias）

**实现步骤**：
1. hpp: 添加`Backward_cpu`声明
2. cpp: 实现Backward：
   - `propagate_down[0]`→计算dX（copy或memcpy dy）
   - `param_propagate_down_[0]`→计算d_bias（按axis和num_axes_求和）
   - 参考InnerProduct的db计算逻辑
   - perf日志
3. 测试文件：8个用例（解析dX/dbias + 数值dX/dbias + per-channel + positional + 零梯度 + 形状）

**验收标准**：8个测试用例全部PASSED，数值梯度rtol≤1e-3。

---

### ACT-16：Scale层Backward实现 🟡 P1

| 项目 | 详情 |
|------|------|
| **优先级** | P1（乘法层，梯度稍复杂） |
| **状态** | 📋 待实现 |
| **预估工作量** | 实现45分钟 + 测试60分钟 = 105分钟 |
| **C++文件** | `include/caffe_ffi/layers/scale_layer.hpp`、`src/caffe_ffi/layers/scale_layer.cpp` |
| **测试文件** | `tests/python/test_scale_backward.py`（新建） |

**Backward公式**：
- Forward: `y = alpha * x + beta`（alpha必选，beta可选bias_term）
- `dX = dy * alpha`
- `d_alpha = sum(dy * x)` over broadcast dimensions
- `d_beta = sum(dy)` over broadcast dimensions（如果bias_term=true）
- 最多2个learnable参数：blobs_[0]（alpha）、blobs_[1]（beta，可选）

**实现步骤**：
1. hpp: 添加`Backward_cpu`声明
2. cpp: 实现Backward：
   - dX: 逐元素 `dx = dy * alpha[c]`
   - d_alpha: 按广播维度求和 `sum(dy * x)`
   - d_bias（如果有bias_term）: 按广播维度求和 `sum(dy)`
   - 需要处理axis和num_axes广播维度
   - perf日志
3. 测试文件：9个用例（dX/dscale/dbias解析+数值 + no-bias + 零梯度 + 形状）

**验收标准**：9个测试用例全部PASSED，数值梯度rtol≤1e-3。

---

### ACT-17：Eltwise层Backward实现 🟡 P1

| 项目 | 详情 |
|------|------|
| **优先级** | P1（三种操作：SUM/PROD/MAX，MAX需要winner mask） |
| **状态** | 📋 待实现 |
| **预估工作量** | 实现60分钟 + 测试60分钟 = 120分钟 |
| **C++文件** | `include/caffe_ffi/layers/eltwise_layer.hpp`、`src/caffe_ffi/layers/eltwise_layer.cpp` |
| **测试文件** | `tests/python/test_eltwise_backward.py`（新建） |
| **无learnable参数** | 无需param_propagate_down_初始化 |

**Backward公式**：
- **SUM**: `dX[i] = dy * coeff[i]`（每个bottom获得等分或coeff加权的梯度）
- **PROD**: `dX[i] = dy * prod(X[j] for j≠i)`（乘积的导数是其他输入之积）
- **MAX**: 需要在Forward时记录max_idx_（类似Max Pooling），Backward时winner-take-all路由梯度

**实现注意**：
- MAX操作需要在Forward时保存winner索引（类似Pooling的max_idx_）
- PROD操作需要缓存输入或在Backward时重新计算乘积
- coeff支持加权SUM

**实现步骤**：
1. hpp: 添加`Backward_cpu`声明，可能需要添加`max_idx_`成员变量
2. cpp: 实现Backward：
   - SUM: 按coeff分配梯度
   - PROD: 计算其他输入的乘积
   - MAX: 根据max_idx_路由梯度
   - perf日志
3. 测试文件：8个用例（SUM/PROD/MAX解析+数值 + coeff + 多输入形状）

**验收标准**：8个测试用例全部PASSED，三种操作数值梯度rtol≤1e-3。

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

| 类别 | 实现时间 | 测试时间 | 合计 |
|------|---------|---------|------|
| P0（Dropout+Bias） | 45min | 75min | **2h** |
| P1（Scale+Eltwise+Concat） | 135min | 165min | **5h** |
| P2（Softmax+Split+Slice+LRN） | 105min | 150min | **4h15min** |
| P3（Crop测试） | 0min | 30min | **30min** |
| **合计** | **4h45min** | **7h** | **~11h45min** |

## 端到端训练目标

P0+P1层Backward完成后，可构建端到端训练验证网络：

```
Data → Conv → BN → ReLU → Pool → IP → ReLU → Dropout → IP → SoftmaxWithLoss → Loss
       ✅    ✅   ✅    ✅     ✅    ✅     ✅      ✅(P0)    ✅         ✅
```

验证目标：
1. Forward完整运行无崩溃
2. Backward完整运行无崩溃
3. Loss随训练步下降（梯度有效性）
4. 权重梯度范数非零且稳定（非NaN/Inf）

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
