---
title: P3-D 遗留测试补齐技术报告（Split/Slice/LRN/Crop Backward）
date: 2026-08-03
category: code-optimization
task_type: testing
tags: [caffe-ffi, backward, p3d, split, slice, lrn, crop, numerical-gradient]
status: completed
verification: passed
source: "retrospective-caffe-ffi-p3b-test-milestone-20260731/README.md#p3-d待实现backward层"
coverage: "4层Backward测试补齐，P3-D全套219测试通过"
---

# P3-D 遗留测试补齐技术报告（Split/Slice/LRN/Crop Backward）

## 概述

P3-D 计划的 6 个核心训练层（Dropout/Scale/Bias/Eltwise/Concat/Softmax）Backward 已实现并验证后，本阶段补齐了 4 个 **Backward_cpu 已存在、仅缺测试覆盖** 的层：Split、Slice、LRN、Crop。四层 Backward 实现均无需改动 C++，本次交付纯为测试补齐。

## 测试环境

| 项 | 值 |
|----|----|
| 运行环境 | `<USER_HOME>\anaconda3\envs\py314`（Python 3.14.3） |
| 测试框架 | pytest 9.1.1 |
| C++ 扩展 | `_ffi_api.is_available() == True`（原生模式，非 stub） |
| 验证方法 | 三层验证法：已知值(L1) → numpy解析对比(L2) → 中心有限差分数值梯度(L3) + 属性测试(L4) |

## 测试结果摘要

**P3-D 全套 219 个用例全部通过，0 失败。**

| 测试文件 | 用例数 | 关键验证点 |
|---------|:------:|-----------|
| [test_split_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_split_backward.py) | 17 | 梯度累加（N=2/3 求和到底部）、N=1 直通、数值梯度 |
| [test_slice_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_slice_backward.py) | 20 | 梯度路由（按 slice_point 分发）、显式/隐式分割、数值梯度 |
| [test_lrn_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_lrn_backward.py) | 13 | 局部响应归一化梯度（scale 项+链式法则）、数值梯度 |
| [test_crop_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_crop_backward.py) | 19 | 梯度复制+zero-pad（裁剪区复制，其余为 0）、数值梯度 |
| [test_concat_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_concat_backward.py) | 24 | Concat 梯度拆分（多轴/多输入） |
| [test_eltwise_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_eltwise_backward.py) | 32 | Eltwise SUM/PROD/MAX 梯度路由 |
| [test_scale_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_scale_backward.py) | 25 | Scale 参数/输入梯度 |
| [test_bias_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_bias_backward.py) | 19 | Bias 参数/输入梯度 |
| [test_dropout_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_dropout_backward.py) | 20 | Dropout 梯度直通（ratio=0 identity） |
| [test_softmax_backward.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_softmax_backward.py) | 22 | Softmax 预测层梯度 |
| [test_p3d_all_layers_e2e.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_p3d_all_layers_e2e.py) | 8 | 端到端：Loss 随 SGD 下降（梯度有效性金标准） |
| **合计** | **219** | **全部通过** |

## 各层 Backward 语义

### Split（梯度累加）
多个 top 共享 bottom 内存，Backward 时 `d_bottom = Σ_i d_top_i`（fan-out 分支求和）。

### Slice（梯度路由）
按 `slice_point` 将 bottom 切分为多个 top，Backward 时把各 top 的梯度沿 axis 拼回原 bottom 形状（Concat 的逆操作）。

### LRN（局部响应归一化）
涉及 scale 项与链式法则，核心公式：

```
dx[c] = dy[c] * scale[c]^(-beta) - cache_ratio * x[c] * Σ_window(dy * y / scale)
cache_ratio = 2 * alpha * beta / size
```

### Crop（梯度复制 + zero-pad）
两个 bottom：`data`（待裁剪）与 `crop_ref`（定义输出尺寸）。Backward 时 `d_data = 0`，仅把 `dy` 复制到裁剪区域，其余位置为 0。

## 本次修复的关键问题

### 问题 1：protobuf 文本格式无法解析 `offset: 0 0 1 1`
- **现象**：`NetInitialization` 报 `Error parsing text-format caffe.NetParameter: Expected identifier, got: 0`
- **根因**：protobuf 文本格式要求重复 `offset` 字段逐行书写，单行多值非法
- **修复**：改为每行一个 `offset: N`
- **测试影响**：Crop 层所有含 offset 用例

### 问题 2：Crop 的 offset 是轴相对，且长度受 LayerSetUp 强校验
- **现象**：`start_axis + param.offset_size() == input_dim` 校验失败（如 6 vs 4）
- **根因**：offset 长度须等于 `input_dim - axis`（axis 之后维度数），如 4D axis=2 时 offset 应为 `[1,1]`（H,W），而非全维度 `[0,0,1,1]`
- **修复**：按层约定传 offset，numpy 参考同步修正为轴相对语义

### 问题 3：Crop 的 top 形状截断规则
- **现象**：`dy` shape 与期望不符（reshape 失败）
- **根因**：axis 之后维度取 `crop_ref` 尺寸，axis 之前取 `data` 尺寸，故 `dy` 形状须匹配完整输出形状
- **修复**：正确构造 `crop_shape` 与 `dy`

## 回归验证

- 完整套件：`1615 passed, 31 failed`（31 个失败集中在无关的既有问题文件：`test_layer_template_three_layer_validation.py`、`test_phase3_set_shape_only.py`、`test_split_concat_bench.py`，属 `Blob` 对象算术/惰性分配既有缺陷，非本阶段引入）
- P3-D 相关套件：**219 passed, 0 failed**（Split/Slice/LRN/Crop/Concat/Eltwise/Scale/Bias/Dropout/Softmax + e2e）

## 结论

P3-D Backward 测试覆盖全部补齐。Split（梯度累加）、Slice（梯度路由）、LRN（归一化梯度）、Crop（裁剪复制+zero-pad）四层 Backward 均通过已知值、numpy 解析对比、中心有限差分数值梯度、零梯度、形状、确定性、Forward 保持、往返一致性验证。P3-D 阶段累计 Backward 验证层数齐全，端到端 SGD 训练 Loss 下降验证通过，可进一步推进端到端 CNN 训练。