---
title: 执行复盘
source: caffe.py RMSNorm transpose removal
---
# 执行复盘

## 时间线

| 阶段 | 事件 |
|------|------|
| 初始请求 | 用户请求对caffe.py L549-560进行代码优化（性能、可读性、错误处理、注释、测试） |
| 第一轮优化 | 创建`_try_prepare_rmsnorm_conversion`合并判定+参数准备，提取命名变量，添加数学原理注释，保留transpose逻辑（基于"rms_norm只支持最后一维"的假设） |
| 用户指正 | 用户指出transpose算子可移除，参考test_rms_norm.py L60-68的rmsnorm_tensor实现 |
| API验证 | 查阅TVM rms_norm参考实现(topi/testing/rms_norm_python.py)和API签名(nn.py)，确认axis参数支持任意整数 |
| 第二轮优化 | 移除所有transpose逻辑，代码从15行简化为6行，删除transpose_axes/inverse_axes返回值 |
| 测试验证 | 更新单元测试适配新接口，扩展数值验证测试，1250个用例全部通过 |
| 知识沉淀 | 复盘→洞察→萃取，沉淀两个代码模式 |

## 事实清单

### 修改文件

1. **[caffe.py](../../../../../../external/xmhub/npu_tvm/python/tvm/relay/frontend/caffe.py)**
   - `_try_prepare_rmsnorm_conversion`函数：返回值从五元组(rms_weight, rms_epsilon, rms_axis, transpose_axes, inverse_axes)简化为三元组(rms_weight, rms_epsilon, rms_axis)
   - `convert_normalize`方法中RMSNorm分支：从约15行（含重复函数调用、条件transpose、逆transpose）简化为6行（直接调用rms_norm）
   - `_normalize_rmsnorm_plan`函数保留未删除（向后兼容，可能被其他地方引用）
   - 添加注释说明数学原理（L2→RMSNorm重参数化公式）

2. **[test_caffe_normalize_rmsnorm.py](../../../../../../external/xmhub/npu_tvm/tests/python/ci/test_caffe_normalize_rmsnorm.py)**
   - 更新5个现有测试函数适配三元组返回值接口
   - 新增`test_try_prepare_rmsnorm_conversion_negative_axis`测试负axis场景

3. **[test_rms_norm_numerical.py](../../../../../../apps/tests/test_rms_norm_numerical.py)**
   - 移除`transpose_to_last_axis`函数和`verify_transpose_roundtrip`测试（transpose不再需要）
   - 新增`verify_channel_axis`测试验证在channel axis(C=1)上直接归一化的等价性
   - 保留1250个参数化测试用例（5形状×5epsilon×50组×2scale配置变体）

### 代码变更量化

| 指标 | 优化前 | 优化后 | 变化 |
|------|--------|--------|------|
| RMSNorm分支代码行数 | ~15行 | 6行 | -60% |
| transpose操作数 | 2个（条件性） | 0个 | -100% |
| 辅助函数依赖 | 3个(params+plan+should) | 1个(params) | -67% |
| _try_prepare返回元组大小 | 5元组 | 3元组 | -40% |
| 数值测试用例 | ~1000+ | 1250 | +25% |
| 测试最大绝对误差 | ~5e-7 | ~4.8e-7 | 持平(float32精度) |

### 关键参考证据

1. TVM rms_norm参考实现（topi/testing/rms_norm_python.py）核心逻辑：
   ```python
   return data / np.sqrt(np.mean(np.square(data), axis=axis, keepdims=True) + epsilon) * weight
   ```
   — `np.mean(..., axis=axis)` 支持任意axis，不限于最后一维。

2. TVM rms_norm API签名（relay/op/nn/nn.py L2236）：
   ```python
   def rms_norm(data, weight, axis=-1, epsilon=1e-5):
   ```
   — axis参数默认值为-1（最后一维），但接受任意整数。

3. 用户参考实现（test_rms_norm.py L60-68 rmsnorm_tensor）：
   ```python
   variance = np.mean(np.square(x), axis=axis, keepdims=True)
   return x / np.sqrt(variance + eps) * gamma
   ```
   — 直接在目标axis上计算mean，无transpose操作。

## 变更前后代码对比

### 优化前（含冗余transpose）
```python
if _should_convert_normalize_to_rmsnorm(
    op.name, self.model_outputs, input_shape, axis, eps, scale_value
):
    rms_weight, rms_epsilon = _normalize_rmsnorm_params(input_shape, axis, eps, scale_value)
    rms_axis, transpose_axes, inverse_axes = _normalize_rmsnorm_plan(input_shape, axis)
    scale_expr = self.exp_tab.new_const(rms_weight, dtype="float32")
    rms_input = in_expr if transpose_axes is None else _op.transpose(in_expr, axes=transpose_axes)
    rms_out = _op.nn.rms_norm(rms_input, scale_expr, axis=rms_axis, epsilon=rms_epsilon)
    return rms_out if inverse_axes is None else _op.transpose(rms_out, axes=inverse_axes)
```

### 优化后（零transpose）
```python
rms_weight, rms_epsilon, rms_axis = _try_prepare_rmsnorm_conversion(
    op.name, self.model_outputs, input_shape, axis, eps, scale_value
)
if rms_weight is not None:
    scale_expr = self.exp_tab.new_const(rms_weight, dtype="float32")
    return _op.nn.rms_norm(in_expr, scale_expr, axis=rms_axis, epsilon=rms_epsilon)
```
