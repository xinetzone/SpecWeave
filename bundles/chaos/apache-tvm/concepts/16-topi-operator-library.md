---
type: Concept
title: TOPI 算子库
description: TVM TOPI 算子库，涵盖 broadcast/elemwise/reduction/nn/transform/einsum/vision 算子、tags 标签体系及多后端调度模板
tags: [tvm, topi, operator, nn, conv2d, reduction, broadcast, schedule, cuda, x86]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# TOPI 算子库

TOPI（TVM Operator Inventory）是 TVM 的标准算子库，定义于 `include/tvm/topi/` 和 `python/tvm/topi/`。它基于 TE 张量表达式 DSL 提供深度学习中常用算子的计算定义和多后端调度模板，使开发者无需从零手写 TE 计算和调度即可构建神经网络。TOPI 类似于 NumPy 之于科学计算——提供一组覆盖全面的、经过优化的张量操作，并为不同硬件后端（CPU、CUDA、ROCm、Vulkan 等）提供专门的调度实现。

TOPI Python 包在初始化时先导入 C++ schedule（`.cpp`），再导入 Python 模块以允许 Python 覆盖 C++ 实现 [F-227]。导出模块包括 `math`、`tensor`、`index_put`、`reduction`、`transform`、`broadcast`、`sort`、`scatter`、`scatter_elements`、`slice_scatter`、`sparse_reshape`、`scan`、`einsum`、`unique`、`searchsorted`、`signal`，以及子包 `nn`、`utils`、`image`、`vision`、`gpu` [F-228]。TOPI 还导出 `InvalidShapeError` 异常类用于错误报告 [F-229]。

## Tags 标签体系

TOPI 定义了 14 个算子标签常量，用于标记算子的计算特性，指导调度选择和融合决策 [F-195]：

| 标签常量 | 字符串值 | 说明 |
|---------|---------|------|
| `kElementWise` | "elemwise" | 逐元素算子 |
| `kInjective` | "injective" | 单射算子 |
| `kCommReduce` | "comm_reduce" | 交换归约 |
| `kCommReduceIdx` | "comm_reduce_idx" | 带索引的交换归约（如 argmax） |
| `kBroadcast` | "broadcast" | 广播算子 |
| `kMatMul` | "matmul" | 矩阵乘法 |
| `kConv2dNCHW` | - | NCHW 布局 Conv2D |
| `kConv2dHWCN` | - | HWCN 布局 Conv2D |
| `kDepthwiseConv2dNCHW` | - | NCHW 深度可分离卷积 |
| `kDepthwiseConv2dNHWC` | - | NHWC 深度可分离卷积 |
| `kDepthwiseConv2dBackInputNHWC` | - | NHWC 深度可分离卷积输入梯度 |
| `kDepthwiseConv2dBackWeightNHWC` | - | NHWC 深度可分离卷积权重梯度 |
| `kEinsum` | "einsum" | Einstein 求和 |
| `kGroupConv2d` | - | 分组卷积 |

TOPI 提供两个辅助判断函数 [F-196]：
- `is_broadcast(tag)`：判断标签是否以 "elemwise" 或 "broadcast" 开头。
- `is_injective(tag)`：判断是否以 "elemwise"、"broadcast" 或 "injective" 开头。

这些标签在调度函数中用于确定优化策略：逐元素/广播算子通常可以内联或向量化，归约算子需要特殊的归约调度，卷积和矩阵乘需要分块（tiling）调度。

## Broadcast 广播算子

广播算子定义于 `include/tvm/topi/broadcast.h`，实现 NumPy 风格的广播语义。

### broadcast_to

`broadcast_to()` 将张量按 NumPy 规则广播到目标形状 [F-197]。它要求输出维度数不小于输入维度数，使用 `detail::BroadcastShape` 计算公共形状。广播规则从末尾维度开始向前比较：维度相等、其中一个为 1、或其中一个不存在则兼容。

### TOPI_DEFINE_BCAST_OP 宏

`TOPI_DEFINE_BCAST_OP` 宏为二元算子生成三个重载 [F-198]：
1. **Tensor-Tensor**：两个张量输入，自动广播，tag 为 kBroadcast。
2. **Tensor-PrimExpr**：张量与标量，tag 为 kElementWise（无需广播）。
3. **PrimExpr-Tensor**：标量与张量，tag 为 kElementWise。

这种三重重载设计使用户可以灵活地混合张量和标量操作，同时保持标签准确。

通过宏定义的广播逻辑算子包括 `logical_and`、`logical_or`、`logical_xor`、`bitwise_and`、`bitwise_or`、`bitwise_xor`，并为 `&&`、`||`、`&`、`|`、`^` 注册了运算符重载 [F-200]。算术算子如 `add` 通过 `TOPI_DEFINE_BCAST_OP(add, { return a + b; })` 定义，并为 `operator+` 注册重载 [F-201]。

## Elemwise 逐元素算子

逐元素算子定义于 `include/tvm/topi/elemwise.h`，每个输出元素仅依赖对应位置的输入元素。

### TOPI_DECLARE_UNARY_OP 宏

`TOPI_DECLARE_UNARY_OP` 宏为一元内建算子生成 Tensor 版本 [F-202]。它使用 `te.compute` 在输入形状上逐元素应用 `::tvm::OpName`，tag 默认为 `kElementWise`。通过宏声明的一元算子共 27 个 [F-203]：

`exp`、`erf`、`sigmoid`、`sqrt`、`log`、`log2`、`log10`、`floor`、`ceil`、`round`、`trunc`、`abs`、`cos`、`cosh`、`tan`、`sin`、`sinh`、`acos`、`acosh`、`asin`、`asinh`、`atan`、`atanh`、`isnan`、`tanh`、`isfinite`、`isinf`。

### 特殊逐元素算子

- **`fast_tanh_float()`**：使用 Eigen 的 Padé 近似实现快速 tanh [F-204]。将输入裁剪到 [-9, 9] 范围，使用分子（奇次多项式）和分母（偶次多项式）系数计算，避免昂贵的数学库调用。`fast_tanh()` 对 float32 输入使用此快速实现，其他类型回退到默认的 `::tvm::tanh` [F-205]。
- **`identity()`**：返回输入张量的恒等映射。
- **`negative()`**：逐元素取负。
- **`logical_not()`**：逐元素逻辑非。
- **`bitwise_not()`**：逐元素按位取反 [F-206]。

## Reduction 归约算子

归约算子定义于 `include/tvm/topi/reduction.h`，将张量沿指定轴聚合为更小的张量。

### 核心类型与函数

- **`FReduce`**：归约函数类型别名，签名为 `PrimExpr(PrimExpr source, const Array<IterVar>& axis, Array<PrimExpr> init, Span span)` [F-207]。
- **`GetRealAxis()`**：将可能为空或含负数的归约轴转换为有效维度索引数组 [F-208]。空轴表示所有维度，负索引从最后一维偏移，结果排序并去重。
- **`MakeReduceAxes()`**：为每个真实归约轴创建名为 "k{i}" 的 `reduce_axis`，范围为 `[0, data->shape[i])` [F-209]。
- **`MakeReduceTargetShape()`**：计算归约输出形状 [F-210]。`keepdims` 为 true 时归约轴保留为 size 1，否则移除；`atleast1d` 为空结果追加维度 1。
- **`DoCommReduce()`**：执行实际的交换归约计算 [F-211]。通过索引映射将输出索引和归约索引组合为输入索引，tag 为 `kCommReduce`。
- **`CommReduce()`**：归约的高层封装 [F-212]。对 0 维输入特殊处理（identity + 可选 expand_dims），否则依次调用 GetRealAxis、MakeReduceTargetShape、DoCommReduce。

Python 层导出的归约算子包括 `sum`、`max`、`min`、`prod`、`argmax`、`argmin`、`cumsum`、`cumprod` 等，其中 argmax/argmin 使用 `kCommReduceIdx` 标签（同时返回值和索引）。

## NN 神经网络算子

神经网络算子定义于 `include/tvm/topi/nn.h` 和 `include/tvm/topi/nn/` 子目录，是 TOPI 最核心的部分。

### 激活函数

- **`relu(threshold=0)`**：实现 `max(x, threshold)`，支持模板参数类型 [F-213]。
- **`leaky_relu(alpha=0.1)`**：实现 `Select(x > 0, x, x * alpha)` [F-214]。负值部分以 alpha 系数线性泄漏。
- **`prelu(slope, axis)`**：参数化 ReLU，slope 按通道应用 [F-215]。axis 参数指定通道维度，要求 slope 的第一个维度与输入通道数匹配。与 leaky_relu 不同，prelu 的斜率是可学习的输入张量。

### Padding

`pad()` 支持三种填充模式 [F-216]：
- **"constant"**：常量填充（默认填充 0）。
- **"edge"**：边缘值填充（复制边界值）。
- **"reflect"**：反射填充（以边缘为轴镜像，不重复边缘值）。

`pad_after` 为空时使用对称填充（前后填充相同数量）。输出形状通过算术分析器简化，确保符号维度的正确推导。

### Pooling 池化

`PoolType` 枚举定义 `kAvgPool` 和 `kMaxPool` 两种池化类型 [F-217]。`pool_grad_impl()` 实现池化梯度 [F-218]，要求 kernel_size 和 stride_size 各有 2 个元素，padding_size 有 4 个元素（上左下右）；ceil_mode 为 true 时追加 stride-1 的额外填充。

### Dense 全连接

`dense()` 计算 `data * weight^T + bias` [F-219]：
- data 形状 [batch, in_dim]
- weight 形状 [out_dim, in_dim]
- bias 形状 [out_dim]（可选）

内部使用归约轴 k 执行矩阵乘，tag 为 "dense"。这是全连接层和矩阵乘法的基础。

### Softmax

`softmax()` 通过四步数值稳定算法计算 [F-220]：
1. **max 归约**：沿 axis 求最大值（数值稳定性，防止 exp 溢出）。
2. **exp(x - max)**：减去最大值后取指数。
3. **sum 归约**：沿 axis 求指数和。
4. **归一化**：指数除以指数和。

axis 默认为 -1（最后一维），tag 为 "softmax_output"。

`log_softmax()` 要求 2-D 输入，计算 `x - max - log(sum(exp(x-max)))`，tag 为 "log_softmax_output" [F-221]。直接计算 log(softmax(x)) 可获得更好的数值稳定性。

### 卷积

TOPI 的卷积算子（conv2d、depthwise_conv2d、group_conv2d 等）通过 TE compute 描述 im2col 或直接卷积计算，并提供针对不同后端的高度优化的调度模板。卷积调度通常涉及：
- 空间分块（output tiling）
- 归约轴分块（reduction tiling）
- 共享内存/寄存器复用
- 张量核心利用（NVIDIA GPU）
- Winograd 快速卷积算法

### 其他 NN 算子

TOPI nn 子包还包括：
- 归一化：batch_norm、layer_norm、rms_norm、group_norm、instance_norm
- 注意力：attention、multi_head_attention
- 损失函数：cross_entropy、nll_loss
- 卷积变体：conv1d、conv2d_transpose、conv3d
- 池化变体：adaptive_pool、global_pool

## Transform 变换算子

变换算子定义于 `include/tvm/topi/transform.h`，改变张量的形状或布局但不改变数据值。

### sliding_window

`sliding_window()` 在输入张量上滑动窗口 [F-222]，是池化和卷积的基础原语。axis 决定窗口起始维度，窗口形状和步长长度均为 `data.ndim - axis`。输出形状由三部分组成：
1. 前置维度（axis 之前的维度）
2. 窗口数量维度（每个轴一个）
3. 窗口内容维度（每个轴一个）

其他变换算子包括 reshape、transpose、concatenate、split、strided_slice、flip、crop 等，分别处理形状变换、维度重排、张量拼接、分割、切片和翻转等操作。

## Einsum 爱因斯坦求和

Einsum 定义于 `include/tvm/topi/einsum.h`，是表达张量 contractions 的统一接口。

### 核心组件

- **`InferEinsumShape()`**：根据 einsum 下标字符串和操作数形状推断输出形状 [F-223]。
- **`einsum()`**：实现爱因斯坦求和约定，接受下标字符串和输入张量数组，tag 默认为 `kEinsum` [F-224]。
- **`EinsumEquation`** 结构体：包含 `inputs`（每个操作数的下标向量）和 `output`（输出下标），`kEllipsis` 标签值为 '\0' [F-225]。`FromString()` 静态方法从字符串解析方程并转换为显式模式。
- 常量：`LABELRANGE`(128)、`NPY_MAXDIMS`(16)、`NPY_MAXARGS`(16) [F-226]。

Einsum 可以表达矩阵乘（`"ij,jk->ik"`）、批量矩阵乘（`"bij,bjk->bik"`）、张量缩并、转置、求和等多种操作，是最通用的张量计算原语之一。

## Vision 视觉算子

视觉算子位于 `python/tvm/topi/vision/` 和 `src/relax/op/vision/`，主要用于目标检测和图像分割后处理：

- **non_max_suppression (NMS)**：非极大值抑制，去除重叠的检测框。
- **roi_align / roi_pool**：区域特征聚合，将不同大小的 ROI 池化为固定尺寸特征图。
- **multibox_transform_loc**：多框定位变换。
- **get_valid_counts / all_class_non_max_suppression**：有效计数和全类 NMS。

这些算子通常是控制流密集型操作，调度时更多依赖 CPU 或专用后端而非 GPU 并行。

## 多后端调度体系

TOPI 的核心价值不仅在于计算定义，更在于为不同硬件提供专门的调度模板。调度文件按后端组织：

### 通用调度（generic）

`python/tvm/topi/generic/` 提供默认调度实现，作为所有后端的 fallback。包括 `schedule_conv2d.py`、`schedule_dense.py`、`schedule_pool.py` 等。

### CUDA 调度（cuda）

`python/tvm/topi/cuda/` 提供 NVIDIA GPU 优化调度：
- 分块矩阵乘（利用共享内存和寄存器分块）
- 卷积（im2col + GEMM、Winograd）
- 归约（warp shuffle、树状归约）
- 深度可分离卷积
- Tensor Core 调度（通过张量核心加速 fp16/int8 计算）

### x86 调度（x86）

`python/tvm/topi/x86/` 提供 CPU 优化调度：
- AVX-512/AVX2/SSE 向量化
- 多线程并行（通过 TIR parallel）
- 卷积的 NCHWc 和 Winograd 布局
- GEMM 的分块打包调度

### 其他后端

TOPI 还为 ARM CPU（`arm_cpu/`）、Mali GPU（`mali/`）、AMD GPU（`rocm/`）、Intel GPU（`intel_graphics/`）、Raspberry Pi（`raspberry_pi/`）等硬件提供调度。每个后端目录包含该硬件特有的调度文件，覆盖主要算子。

### 调度调度分发机制

TOPI 使用 TVM 的 Target 系统进行调度分发。用户调用 `topi.nn.conv2d` 定义计算后，调用对应后端的 `schedule_conv2d` 获取调度。Python 层通过 `@target_generic` 装饰器实现根据当前 Target 自动选择调度函数：

```python
with tvm.target.Target("cuda"):
    A = te.placeholder(...)
    W = te.placeholder(...)
    C = topi.cuda.conv2d_nchw(A, W, ...)
    s = topi.cuda.schedule_conv2d_nchw([C])
```

## Tags 与调度关联

TOPI 的 tags 标签体系在调度选择中起关键作用：

- **kElementWise/kBroadcast/kInjective**：这些算子的调度通常是简单的内联或向量化，调度函数会检查标签并应用通用的逐元素调度（如 `schedule_injective`）。
- **kCommReduce**：归约算子需要特殊的归约调度，如 rfactor、跨线程归约、warp 级归约。
- **kMatMul/kConv2dNCHW**：计算密集型算子使用专门的分块调度，标签帮助调度函数识别计算类型并选择正确的分块参数。

## TOPI 与 Relax/TE 的关系

在 TVM 编译流程中，TOPI 的角色如下：

1. **Relax 算子合法化**：当 `LegalizeOps` Pass 将 `relax.op.nn.conv2d` 降级时，调用 TOPI 的 `topi.nn.conv2d` 生成 TE 计算和 TIR PrimFunc。
2. **MetaSchedule 调优**：MetaSchedule 对 TOPI 生成的 PrimFunc 进行自动调度搜索，TOPI 的默认调度作为搜索起点或 fallback。
3. **TVMScript 桥接**：用户可通过 `emit_te` 在 Relax 中直接调用 TOPI 函数。
4. **独立使用**：TE + TOPI 也可独立于 Relax 使用，直接构建和编译 TIR 函数（传统 TVM 工作流）。

## 设计要点

TOPI 的设计体现了以下原则：

1. **计算/调度分离**：算子定义（C++ 头文件中的 TE compute）与调度实现（各后端目录中的 schedule 函数）完全分离，同一计算定义可对应多个后端调度。
2. **标签驱动优化**：通过 tags 标记算子特性，使通用调度逻辑能处理一类算子而非逐个编写。
3. **渐进式特化**：generic 提供正确但可能非最优的默认调度，各后端逐步特化优化，新硬件可先复用 generic 再逐步优化。
4. **宏驱动代码生成**：通过 `TOPI_DEFINE_BCAST_OP`、`TOPI_DECLARE_UNARY_OP` 等宏批量生成算子，减少重复代码并确保 API 一致性。
5. **NumPy 对齐**：API 设计和语义（广播规则、轴处理、keepdims 等）与 NumPy 保持一致，降低学习成本。

## 相关概念

- [TE 张量表达式](/concepts/15-te-tensor-expression.md) — TOPI 算子内部使用 `te.compute` 和 `te.placeholder` 描述张量计算
- [调度原语](/concepts/08-schedule-primitives.md) — TOPI 为各硬件后端提供调度模板，应用 split/fuse/cache_read 等原语优化循环
- [Target 与代码生成](/concepts/04-target-codegen.md) — TOPI 通过 Target 系统分发到 CUDA/x86/ARM 等后端的专用调度实现
- [Relax 算子体系](/concepts/13-relax-ops.md) — Relax 算子合法化时调用 TOPI 获取计算定义和 TIR PrimFunc
- [MetaSchedule 自动调度](/concepts/09-meta-schedule.md) — TOPI 默认调度作为 MetaSchedule 自动搜索的起点和 fallback
