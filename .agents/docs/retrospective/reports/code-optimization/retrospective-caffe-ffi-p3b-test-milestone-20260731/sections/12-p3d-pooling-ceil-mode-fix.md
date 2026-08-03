---
title: P3-D Pooling层CEIL模式回归修复记录
date: 2026-08-03
category: code-optimization
task_type: bug-fix
tags: [caffe-ffi, pooling, backward, ceil-mode, regression, numpy-reference, root-cause-analysis]
status: completed
verification: docker-tested
tests_passed: 28
source: "P3-D Pooling Backward: CEIL mode round_mode mismatch regression"
---

# P3-D Pooling层CEIL模式回归修复记录

## 概述

在Scale/Bias Backward实现完成后运行全量回归测试时，发现Pooling层有1个测试失败：`test_ave_boundary_pool_size_correction`。经I→F→V→C链路分析，根因是C++ Caffe实现与numpy参考实现的默认`round_mode`不一致：C++默认使用CEIL模式，numpy参考默认使用FLOOR模式，导致输出shape不匹配。

**优先级**：🔴 P0（回归修复，阻塞验证）
**状态**：✅ 已修复（Docker测试28/28通过）
**实际耗时**：~20分钟（根因分析5min + 修复5min + 验证10min）
**测试结果**：28 passed in 0.32s

## 问题现象（R：事实采集）

### 测试失败日志

在Docker容器中运行回归测试时：
```
Scale: 25/25 PASSED
Bias: 19/19 PASSED
Dropout: 20/20 PASSED
Pooling: 27/28 FAILED

FAILED test_pooling_backward.py::TestPoolOverlapAccumulation::test_ave_boundary_pool_size_correction
  ValueError: cannot reshape array of size 4 into shape (1,1,1,2)
```

### 失败位置
- 文件：[test_pooling_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_pooling_backward.py#L638-L668)
- 函数：`test_ave_boundary_pool_size_correction`
- 错误：dy shape (1,1,2,2) 无法reshape为测试中硬编码的(1,1,1,2)

## 根因分析（I：洞察）

### 现象四元组

| 项 | 内容 |
|----|------|
| **现象** | AVE pooling边界测试失败，shape不匹配错误 |
| **根因** | C++ Pooling层默认使用CEIL round_mode，numpy参考实现默认使用FLOOR模式，导致输出尺寸计算不一致 |
| **影响** | Pooling层Backward测试1/28失败；但C++实现本身正确，只是测试参考与实现不一致 |
| **建议** | 将numpy参考默认ceil_mode改为True与C++对齐，修正测试用例dy shape和断言 |

### 详细技术分析

Caffe Pooling层输出尺寸计算公式：
```cpp
// C++默认（无round_mode显式指定时）
pooled_height_ = ceil((H + 2*pad_h - kernel_h) / stride_h) + 1;  // CEIL模式
pooled_width_  = ceil((W + 2*pad_w - kernel_w) / stride_w) + 1;
```

numpy参考实现（修复前）：
```python
# 修复前默认ceil_mode=False → 使用floor计算
H_out = int(np.floor(float(H + 2*pad_h - kH) / stride_h)) + 1;  # FLOOR模式
W_out = int(np.floor(float(W + 2*pad_w - kW) / stride_w)) + 1;
```

**具体案例**（4x5输入，3x3 kernel，stride=2，pad=0）：
- CEIL模式（C++默认）：H_out=ceil((4-3)/2)+1=2, W_out=ceil((5-3)/2)+1=2 → 输出2x2
- FLOOR模式（numpy旧默认）：H_out=floor((4-3)/2)+1=1, W_out=floor((5-3)/2)+1=2 → 输出1x2

这解释了为什么测试中硬编码dy=(1,1,1,2)会失败——C++实际输出是2x2而非1x2。

### 为什么P3-C阶段没发现？

Pooling Backward在P3-C阶段实现并通过了27个测试，但`test_ave_boundary_pool_size_correction`是P3-D阶段新增的边界专项测试，专门验证边界窗口pool_size归一化。该测试用例编写时错误假设了FLOOR模式，与C++实际行为不一致。

## 第一性原理验证（F）

### Caffe round_mode规范核查

查阅Caffe官方proto定义：
```protobuf
// caffe.proto
enum RoundMode {
  CEIL = 0;  // 默认值：向上取整
  FLOOR = 1;
}
```
默认值为0=CEIL，与C++实现一致。

### 输出尺寸计算验证

| 输入H | kernel | stride | pad | CEIL输出 | FLOOR输出 | C++实际 |
|-------|--------|--------|-----|----------|-----------|---------|
| 4 | 3 | 2 | 0 | ceil((4-3)/2)+1=2 | floor((4-3)/2)+1=1 | **2** |
| 5 | 3 | 2 | 0 | ceil((5-3)/2)+1=2 | floor((5-3)/2)+1=2 | **2** |
| 7 | 3 | 2 | 0 | ceil((7-3)/2)+1=3 | floor((7-3)/2)+1=3 | **3** |

确认C++行为符合CEIL默认规范。

## 修复方案（C：原子修复）

### 变更1：numpy参考默认参数对齐

**文件**：[test_pooling_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_pooling_backward.py#L48)

```python
# 修复前
def pooling_backward_np(dy, x, kernel_size, stride=None, pad=0,
                        pool_type='MAX', ceil_mode=False, global_pooling=False):

# 修复后：默认ceil_mode=True与C++ Caffe默认行为对齐
def pooling_backward_np(dy, x, kernel_size, stride=None, pad=0,
                        pool_type='MAX', ceil_mode=True, global_pooling=False):
```

### 变更2：修正测试用例dy shape和断言

**文件**：[test_pooling_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_pooling_backward.py#L638-L668)

修复后的测试用例：
```python
def test_ave_boundary_pool_size_correction(self):
    """AVE pooling边界窗口pool_size小于kernel²时必须用实际大小归一化（CEIL模式）。"""
    # C++默认使用CEIL round_mode（Caffe原生默认行为）
    # 4x5输入,3x3 kernel,stride=2,pad=0 → CEIL输出2x2:
    #   ph=0,pw=0: h[0:3],w[0:3] → pool_size=9 (完整窗口)
    #   ph=0,pw=1: h[0:3],w[2:5] → pool_size=9 (完整窗口)
    #   ph=1,pw=0: h[2:4],w[0:3] → pool_size=6 (边界裁剪: 2行×3列)
    #   ph=1,pw=1: h[2:4],w[2:5] → pool_size=6 (边界裁剪: 2行×3列)
    N, C, H, W = 1, 1, 4, 5
    net = _make_pool_net(N, C, H, W, kernel_size=3, stride=2, pad=0, pool='AVE')
    x = np.zeros((N, C, H, W), dtype=np.float32)
    # CEIL模式输出: H_out=ceil((4-3)/2)+1=2, W_out=ceil((5-3)/2)+1=2
    dy = np.array([[[[9.0, 9.0], [9.0, 9.0]]]], dtype=np.float32)  # 修复前: (1,1,1,2)

    _, dX = _run_pool_backward(net, x, dy)
    expected_dx = pooling_backward_np(dy, x, kernel_size=3, stride=2, pad=0, pool_type='AVE', ceil_mode=True)
    np.testing.assert_allclose(dX, expected_dx, rtol=1e-5, atol=1e-6)

    # 边界窗口(ph=1)pool_size=6: dy=9 → 每个元素=9/6=1.5
    # 完整窗口(ph=0)pool_size=9: dy=9 → 每个元素=9/9=1.0
    # 非边界区域(0:2,0:2)只属于(0,0)窗口 → =1.0
    np.testing.assert_allclose(dX[0, 0, 0:2, 0:2], 1.0, rtol=1e-5)
    # 非边界区域(0:2,3:5)只属于(0,1)窗口 → =1.0
    np.testing.assert_allclose(dX[0, 0, 0:2, 3:5], 1.0, rtol=1e-5)
    # 边界区域(3:4,0:2)只属于(1,0)窗口 → =1.5
    np.testing.assert_allclose(dX[0, 0, 3:4, 0:2], 1.5, rtol=1e-5)
    # 边界区域(3:4,3:5)只属于(1,1)窗口 → =1.5
    np.testing.assert_allclose(dX[0, 0, 3:4, 3:5], 1.5, rtol=1e-5)
    # 重叠区域(2:3,2:3)属于所有4个窗口 → 1.0+1.0+1.5+1.5=5.0
    assert abs(dX[0, 0, 2, 2] - 5.0) < 1e-5, \
        f"Overlap pixel (2,2) should accumulate 5.0 from 4 windows, got {dX[0,0,2,2]}"
```

**关键改进**：
1. dy shape从(1,1,1,2)修正为(1,1,2,2)（CEIL输出）
2. 新增4个区域断言：完整窗口(1.0)、边界窗口(1.5)、4窗口重叠中心(5.0)
3. 详细注释说明每个窗口的pool_size计算和期望梯度值

### 变更3：其他测试显式传递ceil_mode（可选加固）

对于已有通过的测试（7x7输入输出3x3，CEIL/FLOOR结果一致），numpy参考会自动适配，但为代码清晰性，所有调用点保持默认即可——因为默认值已与C++对齐。

## 对抗审查（V）

### 审查视角1：是否会引入新回归？

- 已有27个Pooling测试在修复前通过
- 检查这些测试的输入尺寸，确认CEIL/FLOOR输出一致（如4x4→2x2，5x5→2x2/3x3，7x7→3x3等），默认值变更不影响这些测试的expected_dx计算
- 结论：无新回归风险

### 审查视角2：边界窗口归一化是否正确？

CEIL模式下4x5输入的2x2输出窗口划分：
```
ph=0行: hstart=0, hend=3 (行0,1,2) → pool_size=3行
ph=1行: hstart=2, hend=4 (行2,3) → pool_size=2行（边界裁剪）

pw=0列: wstart=0, wend=3 (列0,1,2) → pool_size=3列
pw=1列: wstart=2, wend=5 (列2,3,4) → pool_size=3列
```
验证：
- (ph=0,pw=0): 3×3=9，dy=9→每个元素=1.0 ✅
- (ph=1,pw=0): 2×3=6，dy=9→每个元素=1.5 ✅
- 中心(2,2)属于4个窗口：1.0+1.0+1.5+1.5=5.0 ✅

计算正确。

### 审查视角3：为什么其他测试没暴露这个问题？

- 2x2 s2（4x4→2x2）：(4-2)/2=1，CEIL/FLOOR都是1→结果一致
- 3x3 s1 pad=1（5x5→5x5）：pad=1使CEIL/FLOOR一致→结果一致
- 3x3 s2（7x7→3x3）：(7-3)/2=2，CEIL/FLOOR都是2→结果一致
- global pooling（HxW→1x1）：特殊处理→结果一致

只有当(H-kernel)不能被stride整除且pad=0时，CEIL/FLOOR差异才会暴露。`test_ave_boundary_pool_size_correction`恰好选择了(H=4,kernel=3,stride=2)这一触发条件。

## 验证结果（V→闭环）

### Docker内测试执行

```bash
cd /workspace/projects/xuanspace/libs/caffe-ffi
python -m pytest tests/python/test_pooling_backward.py -v
```

**结果**：
```
============================= test session starts ==============================
platform linux -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 28 items

tests/python/test_pooling_backward.py::TestMaxPoolBackward2x2::test_maxpool_2x2_known_values PASSED
tests/python/test_pooling_backward.py::TestMaxPoolBackward2x2::test_maxpool_2x2_analytical_dx PASSED
tests/python/test_pooling_backward.py::TestMaxPoolBackward2x2::test_maxpool_2x2_numerical_dx PASSED
tests/python/test_pooling_backward.py::TestMaxPoolBackward2x2::test_maxpool_zero_dy_zero_dx PASSED
tests/python/test_pooling_backward.py::TestAvePoolBackward2x2::test_avepool_2x2_known_values PASSED
tests/python/test_pooling_backward.py::TestAvePoolBackward2x2::test_avepool_2x2_analytical_dx PASSED
tests/python/test_pooling_backward.py::TestAvePoolBackward2x2::test_avepool_2x2_numerical_dx PASSED
tests/python/test_pooling_backward.py::TestMaxPoolBackwardOverlapping::test_maxpool_3x3_pad1_analytical_dx PASSED
tests/python/test_pooling_backward.py::TestMaxPoolBackwardOverlapping::test_maxpool_3x3_pad1_numerical_dx PASSED
tests/python/test_pooling_backward.py::TestAvePoolBackwardOverlapping::test_avepool_3x3_s2_analytical_dx PASSED
tests/python/test_pooling_backward.py::TestAvePoolBackwardOverlapping::test_avepool_3x3_s2_numerical_dx PASSED
tests/python/test_pooling_backward.py::TestGlobalPoolBackward::test_global_maxpool_analytical_dx PASSED
tests/python/test_pooling_backward.py::TestGlobalPoolBackward::test_global_avepool_analytical_dx PASSED
tests/python/test_pooling_backward.py::TestGlobalPoolBackward::test_global_maxpool_numerical_dx PASSED
tests/python/test_pooling_backward.py::TestPoolBackwardDeterminism::test_deterministic PASSED
tests/python/test_pooling_backward.py::TestPoolBackwardDeterminism::test_dx_shape_dtype PASSED
tests/python/test_pooling_backward.py::TestPoolBackwardDeterminism::test_forward_preserved_after_backward PASSED
tests/python/test_pooling_backward.py::TestMaxPoolTieBreaking::test_tie_2x2_s2_all_equal PASSED
tests/python/test_pooling_backward.py::TestMaxPoolTieBreaking::test_tie_2x2_s2_partial_equal PASSED
tests/python/test_pooling_backward.py::TestMaxPoolTieBreaking::test_tie_vs_numpy_reference_random_ties PASSED
tests/python/test_pooling_backward.py::TestMaxPoolTieBreaking::test_tie_deterministic_across_runs PASSED
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_ave_3x3_s1_overlap_accumulation_known_values PASSED
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_ave_3x3_s1_pad1_overlap_center_accumulates_more PASSED
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_ave_boundary_pool_size_correction PASSED  # 修复前FAIL
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_max_overlap_same_pixel_wins_multiple_windows PASSED
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_ave_stride1_full_overlap_random_vs_numpy PASSED
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_max_stride1_overlap_random_vs_numpy PASSED
tests/python/test_pooling_backward.py::TestPoolOverlapAccumulation::test_gradient_sum_conservation_ave PASSED

============================== 28 passed in 0.32s ==============================
```

### 全量回归测试

```bash
python -m pytest tests/python/test_scale_backward.py tests/python/test_bias_backward.py tests/python/test_dropout_backward.py tests/python/test_pooling_backward.py -v
```

**结果**：
```
Scale:   25/25 PASSED
Bias:    19/19 PASSED
Dropout: 20/20 PASSED
Pooling: 28/28 PASSED
============================== 92 passed in 1.23s ==============================
```

无新回归引入，修复闭环。

## 经验萃取（E：模式沉淀）

### 反模式：numpy参考默认值与框架实现不一致

**触发条件**：编写numpy参考实现时，未核查框架默认参数，仅凭"常见约定"假设默认值。

**核心错误**：
1. 假设pooling默认FLOOR（PyTorch等框架默认），但Caffe默认是CEIL
2. 编写测试时按FLOOR假设硬编码shape，未先验证C++实际输出shape
3. 选择了恰好暴露CEIL/FLOOR差异的测试输入(H=4,ks=3,s=2,pad=0)，但未察觉这是边界情况

**预防措施**（添加到测试编写Checklist）：
- [ ] 编写numpy参考前，必须核查proto定义中的默认枚举值
- [ ] 对于有枚举参数的层（round_mode、pool等），测试中应显式传递参数而非依赖默认值
- [ ] 编写边界测试前，先用C++跑一遍Forward获取实际输出shape，再写dy
- [ ] 对所有可能的round_mode（CEIL/FLOOR）都应有至少一个测试用例覆盖

### 可复用模式：框架默认值对齐原则

当Python/numpy参考实现与C++框架实现并存时：
1. **默认值必须对齐**：参考实现的默认参数必须与C++ proto/cpp中的默认行为一致
2. **显式优于隐式**：关键测试用例应显式传递参数（如`ceil_mode=True`），避免默认值变更导致的隐性break
3. **反向验证**：先跑C++ Forward获取y.shape，再构造dy，而非手动计算shape

## 覆盖矩阵更新

修复后Pooling层测试覆盖情况：

| 测试类 | 用例数 | 覆盖内容 |
|--------|--------|---------|
| TestMaxPoolBackward2x2 | 4 | 非重叠MAX known/analytical/numerical/zero |
| TestAvePoolBackward2x2 | 3 | 非重叠AVE known/analytical/numerical |
| TestMaxPoolBackwardOverlapping | 2 | 重叠MAX s1pad1 analytical/numerical |
| TestAvePoolBackwardOverlapping | 2 | 重叠AVE s2 analytical/numerical |
| TestGlobalPoolBackward | 3 | Global MAX/AVE analytical/numerical |
| TestPoolBackwardDeterminism | 3 | determinism/shape/forward-preserved |
| TestMaxPoolTieBreaking | 4 | 平局路由专项（全相等/部分相等/随机/确定性） |
| TestPoolOverlapAccumulation | 7 | 重叠累加专项（AVE/MAX边界/守恒/CEIL模式） |
| **合计** | **28** | |

P3-D阶段四层总测试：
- Dropout: 20
- Scale: 25
- Bias: 19
- Pooling: 28
- **P3-D合计**：92个测试
- **P3-C+P3-D总计**：98+92=190个Backward测试用例

## 相关文档

- [06-p3d-backward-plan.md](06-p3d-backward-plan.md) - P3-D主计划
- [08-p3d-backward-todo.md](08-p3d-backward-todo.md) - P3-D待办清单
- [10-p3d-scale-backward.md](10-p3d-scale-backward.md) - Scale层Backward记录
- [11-p3d-bias-backward.md](11-p3d-bias-backward.md) - Bias层Backward记录
