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

对于S型激活函数（sigmoid/tanh/softmax），输入超过一定阈值后输出将精确舍入到饱和值。

> **⚠️ 正负饱和不对称性**：sigmoid的正负饱和阈值**不对称**。
> 正向饱和→1.0是ULP舍入效应（1-sigmoid(x) < ULP(1)/2时发生），精确阈值在x≥**16.64**；
> 负向饱和→0.0需要exp(-x)溢出为inf（即sigmoid(x) = 1/(1+inf) = 0），精确阈值在x ≤ **-88.73**。
> 在-88.73 < x < 16.64区间，sigmoid(x)非精确饱和值；其中(-88.73, -85)为亚正规数区间。

| 激活函数 | 饱和值 | 精确饱和输入阈值（float32） |
|----------|--------|---------------------------|
| sigmoid(x) | 1.0 | x ≥ **16.64**（精确边界16.635532，ULP舍入：sigmoid(16.63553)≈0.9999999，sigmoid(16.635532)精确=1.0） |
| sigmoid(x) | 0.0（精确） | x ≤ **-88.73**（精确边界-88.72284，exp(88.72284) > FLT_MAX溢出为inf，1/inf=0） |
| sigmoid(x) | < 1e-37（近似零） | x ≤ -85（亚正规数区间，非精确零） |
| tanh(x) | ±1.0 | \|x\| ≥ **9.02**（精确边界9.010914，ULP舍入：tanh(9.010913)≈0.99999994，tanh(9.010914)精确=±1.0） |
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
# 方式1：精确相等（推荐，语义最清晰）——适用于x≥16.64或x≤-88.73的极端输入
assert sigmoid(80) == 1.0      # x=80≥16.64，正向ULP饱和
assert sigmoid(-100) == 0.0    # x=-100≤-88.73，exp溢出为inf，精确为0
assert tanh(100) == 1.0        # |x|=100≥9.02，tanh对称饱和
assert tanh(-100) == -1.0

# 方式2：宽松不等式（适用于"充分接近"语义，非极端输入）
assert sigmoid(10) > 0.9999    # 0.9999 < 1-ULP(1)/2，安全在可表示区间内
assert sigmoid(-10) < 0.0001   # -10在亚正规区间但非精确零，用<而非==0
assert tanh(5) > 0.999

# 方式3：精确equal用于乘法截断产生的精确零
assert relu_dead_neuron_grad == 0.0  # 0*dy精确为零，非近似
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

### 2.3 两类拐点：C¹连续 vs C¹不连续

分段激活函数的拐点分为两类，处理策略不同：

**类型A：C¹连续但C²不连续（如ELU α=1、Softplus）**
- 函数值连续 ✓，一阶导数连续 ✓，二阶导数跳变 ✗
- 中心差分截断误差退化为 **O(h)**（而非O(h²)），但有界
- 处理方式：**放宽rtol到5e-3**即可吸收O(h)误差
- 例：ELU在α=1时f'(0⁻)=f'(0⁺)=1，但f''(0⁻)=1≠f''(0⁺)=0

**类型B：C¹不连续（如ReLU、LeakyReLU、PReLU）**
- 函数值连续 ✓，一阶导数**跳变** ✗
- 中心差分跨越拐点时误差为 **O(1)**（导数跳变量级），而非O(h)
- 处理方式：**必须避开拐点区域**（将x推离0点至少2h距离），不能仅靠放宽rtol
- 例：ReLU f'(0⁻)=0, f'(0⁺)=1，跨0差分给出(1+0)/2=0.5，误差50%

### 2.4 规则

**🚫 禁止**在C¹不连续拐点附近进行中心差分（即使放宽阈值也不可靠）。

**✅ 正确**的应对策略：
```python
# 策略1（C¹连续拐点，如ELU α=1）：放宽rtol到5e-3
np.testing.assert_allclose(grad_num, grad_analytic, rtol=5e-3)

# 策略2（C¹不连续拐点，如ReLU/LeakyReLU/PReLU）：推离拐点
h = 1e-3  # 中心差分步长
x = rng.randn(...) * 2.0
# 将|x|<2h的点推到±2h，确保[x-h,x+h]不跨越拐点
x = np.where(x > 0, np.maximum(x, 2*h), np.minimum(x, -2*h))

# 策略3：采样偏移到单侧（标准ReLU数值梯度测试推荐）
x = rng.randn(...) * 2.0 + 1.0  # 全部>0，完全避开负半轴
```

### 2.5 C¹拐点敏感函数清单

| 函数 | 拐点位置 | 左/右导数差异 |
|------|---------|-------------|
| ReLU/LeakyReLU/PReLU | x=0 | f'(0⁻)=0/α, f'(0⁺)=1 |
| ELU | x=0 | f'(0⁻)=α, f'(0⁺)=1（α=1时C¹连续） |
| Softplus | x≈0（软拐点） | f'(x)→0 for x→-∞, f'(x)→1 for x→+∞（实际上C^∞） |

### 2.6 共享Helper函数：`avoid_c1_discontinuity`

为统一C¹不连续拐点防护逻辑，项目提供了可复用的helper函数：

```python
from .caffe_test_helpers import avoid_c1_discontinuity
```

**函数签名：**

```python
def avoid_c1_discontinuity(
    x: np.ndarray,
    h: float = 1e-3,
    kink_points: float | tuple[float, ...] = 0.0,
    margin: float = 2.0,
) -> np.ndarray:
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `x` | `np.ndarray` | 必填 | 输入数组，返回其拷贝（不修改原数组） |
| `h` | `float` | `1e-3` | 中心差分步长 |
| `kink_points` | `float \| tuple[float, ...]` | `0.0` | C¹不连续拐点位置，多数激活函数为`0.0`；多拐点函数传入tuple |
| `margin` | `float` | `2.0` | 安全边距（以h为单位），默认2.0确保`x±h`均在拐点同侧 |

**使用示例：**

```python
from .caffe_test_helpers import avoid_c1_discontinuity

EPS = 1e-3  # 中心差分步长

# LeakyReLU/PReLU数值梯度测试——标准用法
x = rng.randn(1, 1, 3, 4).astype(np.float32) * 2.0
x = avoid_c1_discontinuity(x, h=EPS)  # 一行完成拐点推离

# 多拐点函数（如未来实现的分段函数有多个不可导点）
x = avoid_c1_discontinuity(x, h=EPS, kink_points=(-1.0, 0.0, 1.0))

# 自定义安全边距（默认margin=2.0已足够，一般不需要修改）
x = avoid_c1_discontinuity(x, h=EPS, margin=3.0)  # 3h安全边距
```

**函数特性：**
- ✅ **幂等安全**：多次调用结果一致
- ✅ **符号保留**：推离时点保持在拐点原侧
- ✅ **类型不变**：返回数组shape和dtype与输入一致
- ✅ **零依赖**：仅依赖numpy
- ✅ **多拐点支持**：可传入tuple处理多个不连续点

### 2.7 拐点防护策略选择决策树

新增分段激活函数数值梯度测试时，按此决策树选择正确策略：

```
测试的激活函数在数值梯度采样区间内是否有C¹不连续点（导数跳变）？
├─ 否（Sigmoid/TanH/Softplus/Exp/Log等C¹光滑函数）
│   └─ 无需特殊防护，按超越函数容差使用rtol=1e-3即可
│
└─ 是（存在导数跳变的分段点）
    ├─ C¹是否连续？（即f'(kink⁻) == f'(kink⁺)？）
    │   ├─ 是（如ELU α=1在x=0处，左右导数均为1）
    │   │   └─ 策略B：放宽rtol到5e-3，无需推离拐点
    │   │       （二阶导数跳变导致O(h)截断误差而非O(1)）
    │   │
    │   └─ 否（如ReLU/LeakyReLU/PReLU/Threshold）
    │       └─ 策略A：必须推离拐点
    │           ├─ 推荐：调用 avoid_c1_discontinuity(x, h=h)
    │           ├─ 替代（仅单侧测试）：偏移输入到全正/全负侧（如 x = randn*2 + 1.0）
    │           └─ 🚫 禁止：仅靠放宽rtol——导数跳变产生O(1)误差，无法通过任何rtol吸收
    │
    └─ 不确定？
        └─ 保守按C¹不连续处理，使用avoid_c1_discontinuity（安全无副作用）
```

### 2.8 CI门禁

项目CI流水线包含自动检查（`scripts/check_c1_kink_protection.py`），在lint阶段运行：
- 检测测试C¹不连续激活函数（LeakyReLU/PReLU）且包含数值梯度检查的文件
- 验证是否调用了`avoid_c1_discontinuity`或有`# c1-kink-ok`豁免注释
- 专项拐点测试文件（文件名匹配`*kink*stability*`）自动豁免
- 违规将导致CI失败，阻止PR合并

---

## 3. 精度测试检查清单

新增测试用例时，逐项检查：

- [ ] **饱和区断言**：是否存在对sigmoid/tanh/softmax极端输入值使用`< 1e-30`或`> 1-1e-30`等违反ULP的断言？正向饱和(x≥17)用`== 1.0`，负向精确零(x≤-89)用`== 0.0`，中等负值(-89<x<-17)用`< threshold`
- [ ] **sigmoid正负饱和不对称**：正向饱和阈值x≈17（ULP舍入），负向精确零阈值x≈-89（exp溢出），不可对称套用
- [ ] **精确相等断言**：`== 0.0`/`== 1.0`是否确实是精确值（乘法截断/ULP饱和/exp溢出），而非近似值？
- [ ] **C¹不连续拐点防护**：ReLU/LeakyReLU/PReLU数值梯度测试中，是否调用了`avoid_c1_discontinuity`或使用了等价偏移策略？不可仅靠放宽rtol
- [ ] **C¹连续拐点阈值**：ELU(α=1)等C¹连续拐点处的中心差分rtol是否≥5e-3？
- [ ] **共享helper使用**：新增C¹不连续激活函数数值梯度测试时，是否使用了`caffe_test_helpers.avoid_c1_discontinuity`而非手写推离逻辑？
- [ ] **CI门禁合规**：新增测试文件是否通过`python scripts/check_c1_kink_protection.py tests/python/`检查？
- [ ] **超越函数容差**：涉及exp/log/pow/sqrt的断言rtol是否≥1e-3？
- [ ] **GEMM容差**：矩阵乘法/卷积的断言rtol是否≥1e-4？
- [ ] **确定性种子**：随机输入是否使用固定seed以保证可复现？
- [ ] **边界条件**：是否覆盖了零输入、负值、极端大值等边界情况？

---

## 相关资源

- **原始复盘报告**：[retrospective-caffe-ffi-p3b-test-milestone-20260731](../../retrospective/reports/code-optimization/retrospective-caffe-ffi-p3b-test-milestone-20260731/README.md)
- **精度修复与ELU专项复盘**：[retrospective-float-precision-elu-kink-20260802](../../retrospective/reports/code-optimization/retrospective-float-precision-elu-kink-20260802/README.md)
- **批量加固总结报告**：[report-batch-hardening-float-precision-20260802](../../retrospective/reports/code-optimization/report-batch-hardening-float-precision-20260802/README.md)
- **C¹拐点防护推广覆盖率报告**：[report-c1-kink-protection-rollout-20260802](../../retrospective/reports/code-optimization/report-c1-kink-protection-rollout-20260802/README.md)
- **验证案例**：caffe-ffi P3-C/D阶段测试（test_p3c_activations_ip.py, test_activation_backward.py, test_p3d_slice_crop_deconv_lrn.py）
- **共享Helper函数**：[caffe_test_helpers.py: avoid_c1_discontinuity](../../../../projects/xuanspace/libs/caffe-ffi/tests/python/caffe_test_helpers.py#L284-L340)
- **CI检查脚本**：[check_c1_kink_protection.py](../../../../projects/xuanspace/libs/caffe-ffi/scripts/check_c1_kink_protection.py)
- **ELU C¹拐点专项测试**：test_elu_kink_stability.py（24个专项用例，覆盖C⁰/C¹连续性、O(h)误差缩放、阈值鲁棒性）
- **发现问题**：sigmoid(80)饱和断言矛盾（已修复）、tanh(±100)饱和断言同类问题（已修复）、ELU x≈0拐点中心差分截断误差（rtol已放宽至5e-3）、LeakyReLU/PReLU C¹不连续拐点flake风险（已统一使用avoid_c1_discontinuity防护）
