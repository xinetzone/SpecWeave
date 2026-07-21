---
id: "try-prepare-merge"
source: "caffe.py _try_prepare_rmsnorm_conversion merge function"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/try-prepare-merge.toml"
---
# TryPrepare判定准备合并模式

## 问题

代码中经常出现"判定+准备"分离的模式：先写一个 `should_X()` 函数判断是否可执行某操作（返回bool），在判断通过后又调用 `prepare_X()` 准备参数。这种分离导致：
1. **重复计算**：`should_X()` 内部已做了校验和部分计算，`prepare_X()` 又重复一遍
2. **调用方负担**：调用方必须记住在 `should_X()` 返回True后还要调用哪些准备函数
3. **不一致风险**：两个函数的校验逻辑可能不同步，导致判定通过但准备失败

典型症状：
```python
if should_convert(op_name, ...):  # 内部调用了normalize_params
    params = prepare_params(...)  # 又调用一次normalize_params
    plan = prepare_plan(...)      # 还要调用第三个函数
    result = do_op(params, plan)
```

## 解决方案

将判定逻辑和参数准备合并为一个 `try_prepare_X()` 函数，成功返回准备好的参数元组（或参数对象），失败返回 `(None, None, ...)`。调用方通过"返回值是否为None"判断是否适用，无需重复计算。

函数命名约定：`_try_prepare_<action>`，使用动词`try`表示"尝试"语义——尝试准备参数，准备好就返回，准备不好就返回None。

## 代码

### ❌ 反模式：判定与准备分离

```python
def _should_convert_normalize_to_rmsnorm(op_name, model_outputs, input_shape, axis, eps, scale_value):
    if op_name in model_outputs:
        return False
    if not isinstance(axis, (tuple, list)) or len(axis) != 1:
        return False
    rms_weight, rms_epsilon = _normalize_rmsnorm_params(input_shape, axis, eps, scale_value)
    return rms_weight is not None

# 调用处：判定+重复准备
if _should_convert_normalize_to_rmsnorm(op.name, self.model_outputs, input_shape, axis, eps, scale_value):
    rms_weight, rms_epsilon = _normalize_rmsnorm_params(input_shape, axis, eps, scale_value)  # 重复调用！
    rms_axis, transpose_axes, inverse_axes = _normalize_rmsnorm_plan(input_shape, axis)  # 还要记着调这个
    # ...使用参数
```

### ✅ 正确模式：TryPrepare合并

```python
def _try_prepare_rmsnorm_conversion(op_name, model_outputs, input_shape, axis, eps, scale_value):
    """Check if Normalize can be converted to RMSNorm and prepare parameters in one call.

    Returns (rms_weight, rms_epsilon, rms_axis) on success,
    or (None, None, None) if conversion is not applicable.
    """
    if op_name in model_outputs:
        return None, None, None
    if not isinstance(axis, (tuple, list)) or len(axis) != 1:
        return None, None, None
    norm_axis = int(axis[0])
    if norm_axis < 0:
        norm_axis += len(input_shape)
    rms_weight, rms_epsilon = _normalize_rmsnorm_params(input_shape, axis, eps, scale_value)
    if rms_weight is None:
        return None, None, None
    return rms_weight, rms_epsilon, norm_axis

# 调用处：一次调用，直接使用
rms_weight, rms_epsilon, rms_axis = _try_prepare_rmsnorm_conversion(
    op.name, self.model_outputs, input_shape, axis, eps, scale_value
)
if rms_weight is not None:
    scale_expr = self.exp_tab.new_const(rms_weight, dtype="float32")
    return _op.nn.rms_norm(in_expr, scale_expr, axis=rms_axis, epsilon=rms_epsilon)
```

## 关键设计原则

1. **单次遍历原则**：`try_prepare` 函数对输入只做一次遍历/校验，所有校验逻辑和参数计算在一次调用中完成
2. **None哨兵**：失败时返回与成功时相同元数的元组，元素全部为None，方便调用方解包
3. **文档即契约**：docstring明确说明"成功返回X，失败返回(None,...)"，让调用方无需查看实现即可理解语义
4. **零副作用**：try_prepare是纯函数，不修改全局状态、不修改输入参数，失败时返回None不抛异常（除非输入明确非法）
5. **判定入口唯一**：禁止保留独立的 `should_X()` 函数作为公开API，所有判定必须通过 `try_prepare` 进行

## 适用条件与边界

**适用场景**：
- 存在"判定是否适用"+"准备参数"的两步操作
- 判定过程本身需要做计算（非简单的bool标志检查）
- 参数准备依赖于判定过程中的中间结果

**不适用场景**：
- 判定是简单的属性检查（如 `x is None`、`len(x) > 0`），单独写if更清晰
- 准备过程代价极高（如需要IO、网络请求），此时应保留should+prepare分离以便提前终止
- 同一判定结果需要重复使用多次（缓存判定结果更合适）

## 反模式识别信号

| 信号 | 含义 |
|------|------|
| `should_X()` 返回True后，调用方立即调用 `prepare_X()` | 可以合并 |
| `should_X()` 内部调用了与 `prepare_X()` 相同的子函数 | 重复计算 |
| 判定函数返回bool，调用方还需手动组装参数 | 调用方负担 |
| 新增一个参数需要修改3个地方（should/prepare/call-site） | 维护成本高 |

## 推广场景

- **格式转换**：如尝试将某层/某操作转换为硬件加速版本
- **条件编译**：判断平台是否支持某特性并准备平台特定参数
- **可选优化**：判断是否可以应用优化pass并准备优化参数
- **类型转换**：尝试将某数据类型转换为更高效的表示形式
- **回退逻辑**：尝试快速路径→失败返回None→回退到通用路径

## 来源

- [caffe.py](../../../../../external/xmhub/npu_tvm/python/tvm/relay/frontend/caffe.py) — `_try_prepare_rmsnorm_conversion` 合并 `_should_convert_normalize_to_rmsnorm` + 参数准备逻辑

> **关联模式**：
> - [check-and-restore](check-and-restore.md) — CQS原则下的纯读检查
> - [defensive-attribute-access](defensive-attribute-access.md) — 防御性访问返回None而非抛异常
