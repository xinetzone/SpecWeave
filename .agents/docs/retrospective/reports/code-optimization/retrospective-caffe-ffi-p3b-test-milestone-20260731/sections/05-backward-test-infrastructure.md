---
title: Backward梯度验证基础设施
date: 2026-08-03
category: code-optimization
task_type: infrastructure
tags: [caffe-ffi, testing, gradient, numerical-gradient, c1-kink, infrastructure]
status: completed
source: "retrospective-caffe-ffi-p3b-test-milestone-20260731/README.md#梯度验证基础设施"
---

# Backward梯度验证基础设施

## _grad_check_utils.py 工具库

为统一Backward梯度验证，提取了通用梯度检查工具库。

**文件**：[_grad_check_utils.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/_grad_check_utils.py)

### 核心函数

| 函数 | 功能 |
|------|------|
| `numerical_grad_for_input(net, blob_name, h=1e-3, loss_layer=None)` | 中心有限差分计算输入梯度dX |
| `numerical_grad_for_param(net, param_idx, h=1e-3, loss_layer=None)` | 中心有限差分计算参数梯度dW/db |
| `compare_gradients(analytical, numerical, rtol=1e-3, atol=1e-6)` | 解析梯度vs数值梯度对比，输出详细误差统计 |
| `assert_grad_close(analytical, numerical, rtol=1e-3, atol=1e-6, name="")` | 梯度断言，自动报告最大误差位置和分布 |

### 特性

- **自动检测**：自动识别Net的输入blob和可学习参数（支持多输入多参数）
- **参数数组复用**：避免每次扰动重新分配内存（性能优化）
- **GC优化**：循环中禁用GC，减少测量噪声
- **详细误差诊断**：最大误差位置（索引坐标）、误差分布直方图、相对误差统计
- **多参数批量检查**：一次调用检查dX/dW/db所有梯度
- **中心有限差分**：使用`(f(x+h) - f(x-h))/(2h)`，O(h²)截断误差

### 自测文件

[test_grad_check_utils_selftest.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_grad_check_utils_selftest.py)

## C¹拐点数值稳定性防护

### 问题背景

分段激活函数（ELU/PReLU/LeakyReLU）在C¹/C²不连续拐点处，中心有限差分截断误差从O(h²)降阶为O(h)，常规rtol=1e-3阈值下容易假阳性失败。

### 防护机制

**共享helper函数**：`avoid_c1_discontinuity(x, kink_points, margin=2.0, h=1e-3)`

核心逻辑：
1. 识别输入x中的拐点位置（|x - kink| < margin*h）
2. 将这些点推离拐点至少margin*h距离
3. 幂等安全：多次调用不重复推离
4. 支持多拐点（PReLU在x=0，ELU在x=0）

### CI静态检查门禁

- 正则扫描测试文件，检测LeakyReLU(negative_slope>0)、PReLU、ELU(α≠1)三类C¹不连续激活
- 要求数值梯度测试调用`avoid_c1_discontinuity`函数或添加`# c1-kink-ok`豁免注释
- 检测正则：使用`(?<![a-zA-Z0-9])`替代`\b`处理下划线前缀函数名

### 专项测试

[test_elu_kink_stability.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_elu_kink_stability.py)

### 相关文档

[float-precision-testing-guide.md](../../../../../knowledge/best-practices/float-precision-testing-guide.md) §2 C¹拐点处的数值梯度陷阱

## numpy参考实现库

| 参考文件 | 覆盖层 | 功能 |
|---------|--------|------|
| [_numpy_bn_reference.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/_numpy_bn_reference.py) | BatchNorm | Forward/Backward/inv_std计算（12个自测试） |
| [_numpy_conv_reference.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/_numpy_conv_reference.py) | Conv/Deconv | im2col/col2im/GEMM前向反向（含groups支持） |
| [_numpy_rnn_reference.py](../../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/_numpy_rnn_reference.py) | RNN/LSTM | 纯Python前向参考（8个自测试） |
| 测试文件内置 | Pooling | `pooling_backward_np()` MAX/AVE/ceil/global |
| 测试文件内置 | SoftmaxWithLoss | `softmax_loss_backward_np()`含ignore_label |
| 测试文件内置 | InnerProduct | `ip_backward_np()`支持transpose/no-bias |
| 测试文件内置 | 激活层 | ReLU/Sigmoid/TanH/ELU/PReLU backward公式 |

## 浮点数精度规范

详见独立指南：[float-precision-testing-guide.md](../../../../../knowledge/best-practices/float-precision-testing-guide.md)

### 关键规则

1. **ULP饱和**：float32中ULP(1.0)≈1.2e-7，x>~17(sigmoid)或|x|>~9(tanh)结果精确舍入为1.0
2. **饱和区断言**：使用`== 1.0`/`== 0.0`或宽松不等式（`>0.9999999`），禁止`> 1-ε`（ε<ULP/2）
3. **C¹拐点差分误差**：跨拐点时截断误差O(h)，rtol应放宽至5e-3或使用`avoid_c1_discontinuity`
4. **数值梯度阈值**：常规rtol=1e-3（h=1e-3），C¹拐点处rtol=5e-3
