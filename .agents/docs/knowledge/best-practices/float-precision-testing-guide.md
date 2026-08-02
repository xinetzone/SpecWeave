---
title: 浮点数精度测试技术指南
date: 2026-08-02
category: best-practices
tags: [float32, precision, testing, ulp, numerical-gradient, c1-kink, sigmoid, elu, activation-functions]
status: stable
maturity: L2 (validated in caffe-ffi P3-C/D audit)
source: "retrospective-caffe-ffi-p3b-test-milestone-20260731.md#附录a浮点数精度测试技术指南"
---

# 浮点数精度测试技术指南

> 本文档整理自caffe-ffi P3-C阶段浮点数精度审计中发现的2个关键问题和系统化的精度测试经验，供团队编写数值计算相关测试时查阅参考。

## 1. float32 ULP与饱和区断言规则

### 1.1 背景

在IEEE 754 float32中，每个可表示值之间的间距（ULP, Unit in the Last Place）随数值大小变化：
- ULP(0.0) ≈ 1.4e-45（最小正浮点数）
- ULP(1.0) ≈ 1.2e-7
- ULP(16777216.0) = 2.0（2^24以上整数无法精确表示）

对于S型激活函数（sigmoid/tanh/softmax），输入超过一定阈值后输出将精确舍入到饱和值：

| 激活函数 | 饱和值 | 精确饱和输入阈值（float32） |
|----------|--------|---------------------------|
| sigmoid(x) | 1.0 | x > ~16.6（sigmoid(16.6)≈0.99999994，sigmoid(17)精确=1.0） |
| sigmoid(x) | 0.0 | x < ~-16.6 |
| tanh(x) | 1.0 | x > ~9.1（tanh(9.1)≈0.99999997，tanh(10)精确=1.0） |
| tanh(x) | -1.0 | x < ~-9.1 |
| softmax(x) | one-hot | max_logit - other_logit > ~16 |

### 1.2 规则

**🚫 禁止**使用违反ULP行为的断言：
```python
# ❌ 错误：float32中sigmoid(80)精确==1.0，不可能 > 1-1e-30（1e-30 < ULP(1.0)/2）
assert sigmoid(80) > 1.0 - 1e-30

# ❌ 错误：试图断言"非常接近但不等于"在饱和区无意义
assert sigmoid(80) != 1.0
```

**✅ 正确**的饱和区断言方式：
```python
# 方式1：精确相等（推荐，语义最清晰）
assert sigmoid(80) == 1.0
assert sigmoid(-80) == 0.0

# 方式2：宽松不等式（适用于"充分接近"语义）
assert sigmoid(10) > 0.9999  # 注意：0.9999 < 1.0 - ULP(1.0)/2，在安全区
assert sigmoid(-10) < 0.0001

# 方式3：精确equal用于零值
assert relu_dead_neuron_grad == 0.0  # 乘法截断精确为零，非近似
```

### 1.3 阈值选型参考表

| 场景 | 推荐rtol | 推荐atol | 说明 |
|------|---------|---------|------|
| numpy参考实现对比（无pow/exp/sum） | 1e-6 | 1e-8 | 纯算术运算，float32精度充裕 |
| 含GEMM/卷积（累加运算） | 1e-4 | 1e-5 | 乘加累加误差较大 |
| 含pow/exp/log（超越函数） | 1e-3 | 1e-4 | LRN/softmax/ELU等 |
| 数值梯度检查（中心差分h=1e-3） | 5e-3 | - | C¹拐点处截断误差O(h) |
| 反向传播梯度比较 | 1e-3~5e-3 | - | 逐层误差累积 |

---

## 2. C¹拐点处的数值梯度陷阱

### 2.1 问题描述

对于分段光滑激活函数，在分段点（C⁰或C¹拐点）处进行中心差分数值梯度计算时，截断误差会从O(h²)退化为O(h)：

以ELU为例：
```
f(x) = x,                    x > 0
f(x) = α(eˣ - 1),           x ≤ 0
```

在x=0处：
- f'(0⁺) = 1（右导数）
- f'(0⁻) = α（左导数，通常α=1所以左右导数相等——C¹连续）
- f''(0⁺) = 0（右二阶导数）
- f''(0⁻) = α ≠ 0（左二阶导数——C²不连续）

中心差分公式：f'(x) ≈ [f(x+h) - f(x-h)] / (2h)

当采样点落在x≈0附近时，x-h < 0（左侧用ELU表达式），x+h > 0（右侧用线性表达式），泰勒展开的二阶项不再抵消：

**截断误差 ≈ (h/2)·f''(ξ) ≈ O(h)** 而非 O(h²)

### 2.2 实测数据

| 采样点x | h | rtol阈值 | 实际rel_err | 是否超界 |
|---------|---|---------|------------|---------|
| 0.34 | 1e-3 | 1e-3 | 0.04% | ✅ |
| 0.001 | 1e-3 | 1e-3 | **0.26%** | ❌ 超界 |
| -0.15 | 1e-3 | 1e-3 | 0.12% | ✅ |

当x接近0且h=1e-3时，中心差分窗口[x-h, x+h]跨越拐点，截断误差显著增大。

### 2.3 规则

**🚫 禁止**在分段激活函数的C¹拐点附近使用紧阈值（rtol < 5e-3）进行数值梯度检查。

**✅ 正确**的应对策略：
```python
# 方式1：放宽rtol到5e-3（推荐，最简单）
np.testing.assert_allclose(grad_num, grad_analytic, rtol=5e-3)

# 方式2：采样时避开拐点附近（rng范围偏移）
x = rng.randn(...) * 0.5 + 0.5  # 偏移到正半轴为主

# 方式3：使用单侧差分在拐点处
# f'(x) ≈ [f(x+h) - f(x)] / h  （前向差分，O(h)但不跨拐点）
```

### 2.4 C¹拐点敏感函数清单

| 函数 | 拐点位置 | 左/右导数差异 |
|------|---------|-------------|
| ReLU/LeakyReLU/PReLU | x=0 | f'(0⁻)=0/α, f'(0⁺)=1 |
| ELU | x=0 | f'(0⁻)=α, f'(0⁺)=1（α=1时C¹连续） |
| Softplus | x≈0（软拐点） | f'(x)→0 for x→-∞, f'(x)→1 for x→+∞（实际上C^∞） |

---

## 3. 精度测试检查清单

新增测试用例时，逐项检查：

- [ ] **饱和区断言**：是否存在对sigmoid/tanh/softmax极端输入值使用`< 1e-30`或`> 1-1e-30`等违反ULP的断言？应使用`== 1.0`/`== 0.0`或宽松不等式（`> 0.9999`）
- [ ] **精确相等断言**：`== 0.0`/`== 1.0`是否确实是精确值（乘法截断/饱和），而非近似值？
- [ ] **数值梯度阈值**：C¹拐点附近的中心差分rtol是否≥5e-3？
- [ ] **超越函数容差**：涉及exp/log/pow/sqrt的断言rtol是否≥1e-3？
- [ ] **GEMM容差**：矩阵乘法/卷积的断言rtol是否≥1e-4？
- [ ] **确定性种子**：随机输入是否使用固定seed以保证可复现？
- [ ] **边界条件**：是否覆盖了零输入、负值、极端大值等边界情况？

---

## 相关资源

- **原始复盘报告**：[retrospective-caffe-ffi-p3b-test-milestone-20260731](../../retrospective/reports/code-optimization/retrospective-caffe-ffi-p3b-test-milestone-20260731/README.md)
- **验证案例**：caffe-ffi P3-C/D阶段测试（test_p3c_activations_ip.py, test_activation_backward.py, test_p3d_slice_crop_deconv_lrn.py）
- **发现问题**：sigmoid(80)饱和断言矛盾（已修复）、ELU x≈0拐点中心差分截断误差（已修复）
