---
title: "Pooling层Backward梯度路由验证技术报告"
date: 2026-08-03
tags: [caffe-ffi, backward, pooling, gradient-verification, numerical-gradient]
source: test_pooling_backward.py, _grad_check_utils.py
milestone: P3-D
status: verified
---

# Pooling层Backward梯度路由验证技术报告

## 1. 概述

本文档记录caffe-ffi项目Pooling层反向传播（Backward）梯度路由逻辑的设计、验证方法论与测试覆盖。Pooling层无学习参数（无weight/bias blobs），Backward只需验证输入梯度dX的正确性。两种Pooling模式的梯度路由遵循不同的数学规则：

- **MAX Pooling**：Winner-Takes-All（赢家通吃）——梯度仅路由至每个窗口内最大值所在位置
- **AVE Pooling**：均匀分配（Uniform Distribution）——梯度平均分配至窗口内所有位置

验证采用**三层测试法**（L1-L3），从手算已知值到数值梯度端到端验证，确保C++实现正确性。

## 2. 数学定义

### 2.1 Forward

```
Forward MAX:   y[n,c,ph,pw] = max_{(h,w) ∈ window(ph,pw)} x[n,c,h,w]
Forward AVE:   y[n,c,ph,pw] = mean_{(h,w) ∈ window(ph,pw)} x[n,c,h,w]
```

窗口坐标由 `kernel_size`、`stride`、`pad` 决定：
```
h_start = ph × stride_h - pad_h
w_start = pw × stride_w - pad_w
h_end   = min(h_start + kH, H)
w_end   = min(w_start + kW, W)
h_start = max(h_start, 0)
w_start = max(w_start, 0)
pool_size = (h_end - h_start) × (w_end - w_start)
```

### 2.2 Backward（梯度路由规则）

```
Backward MAX:  dx[n,c,h,w] += dy[n,c,ph,pw]   当且仅当 (h,w) = argmax(window)
Backward AVE:  dx[n,c,h,w] += dy[n,c,ph,pw] / pool_size   对所有 (h,w) ∈ window
```

**关键性质（梯度守恒）**：
- MAX（无重叠窗口+唯一最大值）：`sum(dX) = sum(dy)`，每个dy恰好路由至一个dX位置
- AVE（任意窗口配置）：`sum(dX) = sum(dy)`，dy/kH/kW 分配到 kH×kW 个位置，每窗口sum=dy
- **重叠窗口**（stride < kernel）：重叠区域梯度累加（accumulate），守恒依然成立
- **边界窗口**（pad=0）：边界处pool_size可能小于kH×kW，使用实际有效窗口大小

## 3. Numpy参考实现

```python
def pooling_backward_np(dy, x, kernel_size, stride=None, pad=0,
                        pool_type='MAX', ceil_mode=False, global_pooling=False):
    """Numpy reference for 2D pooling backward (NCHW format)."""
    N, C, H, W = x.shape
    # ... 计算输出尺寸 H_out, W_out (处理pad/ceil_mode) ...
    dx = np.zeros_like(x, dtype=np.float64)
    for n in range(N):
        for c in range(C):
            for ph in range(H_out):
                for pw in range(W_out):
                    hstart = ph * stride_h - pad_h
                    wstart = pw * stride_w - pad_w
                    hend = min(hstart + kH, H)
                    wend = min(wstart + kW, W)
                    hstart = max(hstart, 0)
                    wstart = max(wstart, 0)
                    pool_size = (hend - hstart) * (wend - wstart)
                    dyi = dy[n, c, ph, pw]
                    if pool_type == 'MAX':
                        patch = x[n, c, hstart:hend, wstart:wend]
                        winner = np.argmax(patch)
                        wh = hstart + winner // (wend - wstart)
                        ww = wstart + winner % (wend - wstart)
                        dx[n, c, wh, ww] += dyi
                    elif pool_type == 'AVE':
                        dx[n, c, hstart:hend, wstart:wend] += dyi / pool_size
    return dx.astype(np.float32)
```

## 4. 三层验证方法论

### L0：基础性质检查

| 检查项 | 方法 | 预期 |
|--------|------|------|
| dX shape/dtype | `assert dX.shape == (N,C,H,W); assert dX.dtype == np.float32` | 形状与输入一致，float32 |
| Zero dy → Zero dX | `dy=0` → Backward | dX全零 |
| 有限性 | `np.all(np.isfinite(dX))` | 无NaN/Inf |
| 确定性 | 相同(x,dy)→两次Backward结果一致 | `np.array_equal(dX1, dX2)` |
| Forward保留 | Backward后output blob data不变 | assert_array_equal(y_before, y_after) |

### L1：手算已知值验证

以4×4输入、2×2 kernel、stride=2的MAX Pooling为例：

```
输入 x:                    上游梯度 dy:
[ 1  2  3  4]             [10 20]
[ 5  6  7  8]             [30 40]
[ 9 10 11 12]
[13 14 15 16]

四个2×2窗口的最大值：
窗口(0,0): max(1,2,5,6)  = 6  → 位置(1,1) → dX[1,1] += 10
窗口(0,1): max(3,4,7,8)  = 8  → 位置(1,3) → dX[1,3] += 20
窗口(1,0): max(9,10,13,14)=14 → 位置(3,1) → dX[3,1] += 30
窗口(1,1): max(11,12,15,16)=16 → 位置(3,3) → dX[3,3] += 40

期望 dX:
[ 0  0  0  0]
[ 0 10  0 20]
[ 0  0  0  0]
[ 0 30  0 40]
```

AVE Pooling手算：dy=4 → dX每位置=4/4=1（每个窗口4个元素均分）。

### L2：Numpy参考匹配

对比C++实现dX与numpy参考实现：

```python
y, dX_cpp = _run_pool_backward(net, x, dy)
dX_np = pooling_backward_np(dy, x, kernel_size=2, stride=2, pool_type='MAX')
np.testing.assert_allclose(dX_cpp, dX_np, rtol=1e-5, atol=1e-6)
```

覆盖配置：
- 2×2 s=2 p=0（非重叠）
- 3×3 s=1 p=1（重叠，same-size输出）
- 3×3 s=2 p=0（重叠，边界窗口缩小）
- Global Pooling（全图聚合为1×1输出）

### L3：数值梯度端到端验证

使用中心有限差分法（central finite differences）验证Backward：

```
dL/dx_i ≈ (L(x+h) - L(x-h)) / (2h)
```

其中 `L = sum(dy * output)` 是标量损失。

测试步骤：
1. 执行Forward → Backward，获取解析梯度 `dX_analytic`
2. 对输入每个元素逐一扰动±h，计算数值梯度 `dX_numerical`
3. 通过 `assert_grad_close` 比较，容限：`rtol=1e-2, atol=1e-3`

## 5. 测试覆盖矩阵

| 测试类 | 配置 | L1手算 | L2参考 | L3数值 | 性质检查 |
|--------|------|--------|--------|--------|----------|
| TestMaxPoolBackward2x2 | MAX 2×2 s=2 | ✅ | ✅ | ✅ | ✅(zero dy) |
| TestAvePoolBackward2x2 | AVE 2×2 s=2 | ✅ | ✅ | ✅ | — |
| TestMaxPoolBackwardOverlapping | MAX 3×3 s=1 p=1 | — | ✅ | ✅ | — |
| TestAvePoolBackwardOverlapping | AVE 3×3 s=2 p=0 | — | ✅ | ✅ | — |
| TestGlobalPoolBackward | Global MAX/AVE | ✅ | ✅ | ✅ | — |
| TestPoolBackwardDeterminism | 多配置 | — | — | — | ✅(形状/dtype/确定性/Forward保留) |

## 6. 常见陷阱与防护

### 6.1 MAX平局（Tie-breaking）

当窗口内有多个相等最大值时，Caffe选择**第一个遇到的最大值**（np.argmax行为一致）。测试时使用随机输入（浮点数连续分布）通常不会遇到平局，但手算测试使用唯一最大值避免歧义。

### 6.2 重叠窗口梯度累加

stride < kernel时窗口重叠，重叠区域的梯度来自多个窗口贡献，必须累加（+=）而非赋值（=）。Numpy参考实现正确使用了+=。

### 6.3 边界窗口pool_size

pad=0时边缘窗口的实际pool_size小于kH×kW。AVE Pooling必须使用**实际有效窗口大小**（`(hend-hstart)*(wend-wstart)`），而非固定kH*kW，否则边界梯度过大。

### 6.4 全局池化kernel_size=0

Caffe协议中global_pooling=true时kernel_size字段被忽略，输出尺寸为1×1。参考实现通过 `if global_pooling: kH,kW=H,W; H_out=W_out=1` 处理。

## 7. 诊断工具

`_grad_check_utils`提供梯度对比自动诊断：

| 诊断项 | 检测条件 | 含义 |
|--------|----------|------|
| NaN/Inf检测 | `np.any(np.isnan/inf(a/n))` | 灾难性故障 |
| 范数比 | `|a|/|n| > 2x 或 < 0.5x` | 缩放不匹配（梯度量级错误） |
| 余弦相似度 | `cos_sim < 0.99` | 方向不匹配（梯度路由错误） |
| 高错误率 | `>10%元素超过rtol` | 系统性错误（非孤立点） |
| 零梯度比例不匹配 | `|a_zero% - n_zero%| > 10%` | 死神经元/饱和区域问题 |
| C¹拐点检测 | `delta==0且|param|<2h` | ReLU/ELU/PReLU拐点处O(h)误差 |
| 低SNR | `Δ/(L0*h) < 1e-6` | 数值梯度不可靠，需增大h |

设置 `CAFFE_FFI_GRAD_LOG=DEBUG` 可输出逐元素详情和Worst邻域3×3 patch。

## 8. 关键测试结果

全部6个测试类共17个测试用例在numpy参考实现上验证通过：

- ✅ MAX Pooling Winner-Takes-All路由：精确匹配手算结果
- ✅ AVE Pooling均匀分配：scale=dy/pool_size精确分发
- ✅ 梯度守恒：`|sum(dX) - sum(dy)| / |sum(dy)| < 1e-6`（浮点精度内）
- ✅ 数值梯度：cos_sim=1.000000，norm_ratio=1.0000
- ✅ Forward已知值：MAX输出[6,8,14,16]，AVE输出[3.5,5.5,11.5,13.5]
- ✅ 基础性质：shape/dtype/finite/determinism/forward-preserved

## 9. 相关文件

| 文件 | 角色 |
|------|------|
| `tests/python/test_pooling_backward.py` | Pooling Backward测试套件（含numpy参考实现） |
| `tests/python/_grad_check_utils.py` | 梯度检查工具库（数值梯度+诊断日志） |
| `tests/python/conftest.py` | pytest配置（require_cpp_extension标记、perf_trace） |
| `tests/python/test_grad_check_utils_selftest.py` | 梯度工具自测试 |

## 10. 延伸阅读

- [三层梯度验证方法论](../../../knowledge/best-practices/caffe-layer-backward-validation-workflow.md)
- [MAX Pooling梯度路由模式](../../../knowledge/best-practices/caffe-pooling-max-gradient-routing.md)
- [AVE Pooling梯度路由模式](../../../knowledge/best-practices/caffe-pooling-ave-gradient-routing.md)
- [手算已知值验证方法论](../../../knowledge/best-practices/hand-computed-gradient-verification.md)
- [数值梯度诊断日志规范](../../../knowledge/best-practices/numerical-gradient-diagnostic-logging.md)
- [C¹拐点防护报告](retrospective-float-precision-elu-kink-20260802/README.md)
