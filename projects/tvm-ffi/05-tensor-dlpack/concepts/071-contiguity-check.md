---
type: Concept
title: "视角071：连续性检查"
description: "剖析 IsContiguous 函数的算法实现，包括从后往前遍历的步长验证、size=1 维度的跳过逻辑、空张量的特殊处理，以及连续性在内存访问优化中的意义。"
tags:
  - tensor
  - dlpack
  - contiguity
  - is-contiguous
  - strides
  - memory-layout
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-177
  - code:
    - include/tvm/ffi/container/tensor.h
    - 3rdparty/dlpack/include/dlpack/dlpack.h
---

# 视角071：连续性检查

## 概述

张量的"连续性"（contiguity）是指其数据在内存中是否以紧凑的行优先（C order）方式布局，即相邻逻辑元素在物理内存中也相邻。连续张量可以通过简单的指针递增线性遍历，无需步长乘法，这对向量化加载、DMA 块传输和缓存预取至关重要。TVM FFI 提供 `IsContiguous` 函数检查 `DLTensor` 的连续性，正确处理空张量、size=1 维度和 strides 为空等边界情况。`Tensor` 和 `TensorView` 均提供 `IsContiguous()` 方法，`FromDLPack` 支持 `require_contiguous` 参数在导入时强制校验。

## IsContiguous 函数实现

`IsContiguous` 定义在 `include/tvm/ffi/container/tensor.h:58`：

```cpp
inline bool IsContiguous(const DLTensor& arr) {
  if (arr.strides == nullptr) return true;
  // An empty tensor (numel == 0) is trivially contiguous regardless of strides,
  // matching NumPy/PyTorch semantics.
  for (int32_t i = 0; i < arr.ndim; ++i) {
    if (arr.shape[i] == 0) return true;
  }
  int64_t expected_stride = 1;
  for (int32_t i = arr.ndim; i != 0; --i) {
    int32_t k = i - 1;
    if (arr.shape[k] == 1) {
      // Skip stride check if shape[k] is 1, where the dimension is contiguous
      // regardless of the value of stride.
      continue;
    }
    if (arr.strides[k] != expected_stride) return false;
    expected_stride *= arr.shape[k];
  }
  return true;
}
```

算法分三个阶段：

### 阶段一：strides 为空

DLPack v1.2 之前，`strides == nullptr` 表示紧凑连续布局。函数直接返回 `true`。这保持了对旧版生产者的向后兼容。在 TVM FFI 内部，导入 strides 为空的旧版 DLPack 时会内联计算 strides，因此内部创建的 Tensor 通常 strides 非空，但此检查仍保留用于直接检查外部 DLTensor。

### 阶段二：空张量快速路径

遍历所有维度，若任一维度 size 为 0，则张量元素数为 0（numel == 0）。空张量没有实际数据，其连续性是平凡的（trivially contiguous），无论 strides 取何值都返回 `true`。注释明确指出这匹配 NumPy/PyTorch 语义。

### 阶段三：从后往前验证步长

从最后一维开始向前遍历，维护 `expected_stride` 变量：
- 初始 `expected_stride = 1`（最后一维的步长应为 1）。
- 对每个维度 k（从 ndim-1 到 0）：
  - 若 `shape[k] == 1`，跳过该维度的步长检查。size=1 的维度无论 stride 取何值都不影响连续性（因为该维度只有一个元素，不涉及跨步访问）。
  - 否则检查 `strides[k] == expected_stride`，不等则返回 false。
  - 更新 `expected_stride *= shape[k]`，为前一维计算期望步长。

这一算法验证的是**行优先（C order）连续布局**。对于 shape `(d0, d1, ..., dn-1)`，连续 strides 应为 `(d1*d2*...*dn-1, d2*...*dn-1, ..., dn-1, 1)`。

## size=1 维度跳过的设计依据

PyTorch 在导出 DLPack 时会将 size=1 维度的 stride 归一化为 1（见源码注释引用的 PyTorch PR #83158，`tensor.h:72-74`）。但不同框架可能对 size=1 维度设置任意 stride 值（如广播产生的 stride=0）。由于 size=1 的维度在物理内存中只对应一个元素，其 stride 值不影响数据访问的连续性，因此跳过检查是正确且宽容的。

例如，shape `(3, 1, 4)` 且 strides `(4, 0, 1)` 的张量：维度 1 的 stride=0（广播语义），但该维只有一个元素，整体数据仍以 stride 4 和 1 紧凑访问，是连续的。

## 面向对象的 API

`Tensor::IsContiguous()`（`tensor.h:368`）和 `TensorView::IsContiguous()`（`tensor.h:803`）均转发到自由函数：

```cpp
bool IsContiguous() const { return tvm::ffi::IsContiguous(*get()); }
```

`Tensor::is_contiguous()`（`tensor.h:637`）是 ATen 风格的小写别名，转发到 `IsContiguous()`。

## 导入时的连续性校验

`Tensor::FromDLPack`（`tensor.h:552`）接受 `require_contiguous` 参数：

```cpp
if (require_contiguous && !ffi::IsContiguous(tensor->dl_tensor)) {
  TVM_FFI_THROW(RuntimeError) << "FromDLPack: Tensor is not contiguous.";
}
```

`FromDLPackVersioned`（`tensor.h:578`）同样支持。C ABI 层 `TVMFFITensorFromDLPack`（`tensor.cc:79`）通过 `int32_t require_contiguous` 参数暴露，Python `from_dlpack`（`tensor.pxi:191`）通过关键字参数传递。

## 连续性与 GetDataSize

`GetDataSize(const DLTensor&)`（`tensor.h:117`）计算张量数据所需字节数时，使用 shape 各维乘积而非 strides：

```cpp
inline size_t GetDataSize(const DLTensor& arr) {
  size_t size = 1;
  for (int i = 0; i < arr.ndim; ++i) {
    size *= static_cast<size_t>(arr.shape[i]);
  }
  return GetDataSize(size, arr.dtype);
}
```

对于连续张量，此值等于实际占用的字节数。对于非连续张量（如切片、转置），实际缓冲区可能更大，`GetDataSize` 仅计算逻辑元素数对应的紧凑数据量，不反映物理缓冲区大小。这一区别在 DMA 传输时需要特别注意。

## 设计分析

1. **算法效率**：IsContiguous 是 O(ndim) 的线性扫描，通常 ndim ≤ 4（深度学习常见张量维度），开销可忽略。从后往前遍历只需维护一个 `expected_stride` 变量，无需额外数组。

2. **语义兼容性**：对 strides=nullptr、空张量、size=1 维度的处理均参考了 NumPy/PyTorch 的既有语义，降低了框架互操作时的意外行为。

3. **连续性的相对性**：IsContiguous 检查的是行优先连续。某些框架（如 Fortran/NumPy 的 F order）使用列优先连续，strides 从前往后递增，此函数会判定为非连续。这是 DLPack 生态的约定——行优先是标准交换格式。

4. **可选强制校验**：与对齐检查一样，连续性检查默认关闭（`require_contiguous=false`），因为某些场景（如切片视图、广播）合法地产生非连续张量，强制连续会降低灵活性。

## NPU建议

1. **NPU DMA 对连续性的要求**：大多数 NPU DMA 引擎支持二维/三维 strided 传输，但高阶或复杂步长模式可能需要多次 DMA 描述符。建议在 NPU 算子入口调用 `Tensor::IsContiguous()`，对于连续张量使用最高效的块传输模式（单个 DMA 描述符传输 `numel * element_size` 字节），对于非连续张量降级到 strided DMA 或临时缓冲区。

2. **导入时强制连续**：对于不支持 strided 访问的 NPU 算子，建议在 `FromDLPack` 时传入 `require_contiguous = true`，在数据入口处拒绝非连续张量并抛出明确错误。这比在算子内部产生错误结果更安全。若需要支持非连续输入，应在算子调度层显式处理。

3. **连续内存的 DMA 优化**：连续张量可利用 NPU 的突发传输（burst transfer）能力，最大化 DMA 带宽利用率。建议 NPU 内存分配器默认分配连续缓冲区，并在算子图优化阶段优先传播连续性（如将 transpose+conv 模式融合为 weight 预转置）。

4. **非连续张量的 NPU 处理策略**：
   - (a) **Strided DMA**：若 NPU DMA 支持步长传输，直接使用 shape/strides 构造 DMA 描述符链，无需拷贝。
   - (b) **临时缓冲区**：调用 `Tensor::FromNDAlloc` 分配连续临时缓冲区，提交 DMA 将非连续数据打包到临时区，计算后按需解包回写。
   - (c) **算子重塑**：对于简单的切片/视图操作，调整 NPU 算子的起始偏移和循环边界，避免物理拷贝。

5. **size=1 维度的 NPU 处理**：NPU 编译器在生成 DMA 描述符时应跳过 size=1 的维度（与 IsContiguous 逻辑一致），避免为单元素维度生成冗余的 DMA 命令。对于 stride=0 的广播维度，NPU 应支持广播填充模式（读取一个元素并在输出维度上重复）。

6. **空张量的 NPU 快速返回**：NPU 算子入口应检查 `numel() == 0`（等价于 IsContiguous 中的空张量检查），直接返回成功而不提交任何 DMA 命令。提交零长度 DMA 到 NPU 可能导致硬件异常或未定义行为。

7. **连续性传播的运行时追踪**：建议 NPU 运行时维护张量连续性标志，在 `as_strided`、slice、transpose 等视图操作后更新标志。对于已知连续的张量跳过运行时 IsContiguous 调用，减少 CPU 端开销。可在 TensorObj 中扩展一个 `is_contiguous_cached` 位，但需注意此扩展不影响 DLPack ABI。

## 相关概念

- [069 DLTensor 元数据](069-dltensor-metadata.md)：strides 与 shape 字段语义
- [070 张量对齐检查](070-tensor-alignment-check.md)：IsAligned 互补校验
- [072 不安全张量视图](072-unsafe-tensor-view.md)：as_strided 创建非连续视图
- [067 DLPack 零拷贝互操作](067-dlpack-zero-copy-interop.md)：导入时的连续性参数
- [066 Tensor 对象设计](066-tensor-object-design.md)：FillStridesFromShape 生成连续 strides
