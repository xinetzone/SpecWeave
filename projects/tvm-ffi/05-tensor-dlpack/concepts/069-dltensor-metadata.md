---
type: Concept
title: "视角069：DLTensor 元数据"
description: "详解 DLTensor 结构体的七大字段语义：data 指针、device 设备标识、ndim 维度数、dtype 数据类型、shape 形状、strides 步长、byte_offset 字节偏移，以及它们在 TVM FFI 中的映射。"
tags:
  - tensor
  - dlpack
  - dltensor
  - metadata
  - dtype
  - shape
  - strides
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-177, F-182, F-183, F-184
  - code:
    - include/tvm/ffi/container/tensor.h
    - 3rdparty/dlpack/include/dlpack/dlpack.h
    - include/tvm/ffi/c_api.h
---

# 视角069：DLTensor 元数据

## 概述

`DLTensor` 是 DLPack 标准的核心 C 结构体，以极简的七个字段完整描述一个多维数组的内存布局和数据属性。TVM FFI 的 `TensorObj` 直接继承自 `DLTensor`（`tensor.h:126`），使得所有 Tensor 元数据在内存中与 DLPack 标准完全一致，无需转换即可参与跨框架交换。本视角逐一解析 `data`、`device`、`ndim`、`dtype`、`shape`、`strides`、`byte_offset` 七个字段的语义、约束和在 TVM FFI 中的访问方式。

## DLTensor 结构定义

`DLTensor` 定义在 `3rdparty/dlpack/include/dlpack/dlpack.h:220`：

```c
typedef struct {
  void* data;
  DLDevice device;
  int32_t ndim;
  DLDataType dtype;
  int64_t* shape;
  int64_t* strides;
  uint64_t byte_offset;
} DLTensor;
```

该结构为标准 C 布局，所有编译器生成相同的字段偏移，这是跨语言 ABI 稳定性的基础。

## data：数据指针

`data`（`dlpack.h:250`）是 `void*` 类型，指向张量数据的起始位置。其语义因 `device.device_type` 而异：

- 对于 CPU/CUDA Host/ROCm Host 等**直接地址设备**，`data` 是可直接解引用的虚拟地址。
- 对于 OpenCL，`data` 是 `cl_mem` 句柄；对于 Vulkan，是缓冲区句柄；对于某些设备类型可能是不透明句柄。
- DLPack 规范建议 `data` 对齐到 256 字节（如 CUDA 惯例），但注释明确指出多个库未遵守此建议，不应依赖（`dlpack.h:227-231`）。

DLPack 规定零尺寸张量的 `data` 应为 `NULL`（`dlpack.h:247-248`）。

TVM FFI 中通过 `Tensor::data_ptr()`（`tensor.h:283`）访问：

```cpp
void* data_ptr() const { return get()->data; }
```

## device：设备标识

`device`（`dlpack.h:252`）是 `DLDevice` 类型（`dlpack.h:128`），包含两个字段：

```c
typedef struct {
  DLDeviceType device_type;
  int32_t device_id;
} DLDevice;
```

`device_type` 是 `DLDeviceType` 枚举（`dlpack.h:72`），预定义了 16 种设备类型，包括 `kDLCPU=1`、`kDLCUDA=2`、`kDLCUDAHost=3`、`kDLOpenCL=4`、`kDLVulkan=7`、`kDLMetal=8`、`kDLROCM=10`、`kDLCUDAManaged=13`、`kDLHexagon=16`、`kDLMAIA=17`、`kDLTrn=18` 等。128 以上的值保留给扩展设备类型。

`device_id` 是设备编号，用于多卡环境。对于 CPU、pinned memory、managed memory，通常设为 0。

TVM FFI 通过 `Tensor::device()`（`tensor.h:289`）返回 `DLDevice`，并在 `device.h` 中提供字符串解析（如 `"cuda:0"` → `{kDLCUDA, 0}`）。

## ndim：维度数

`ndim`（`dlpack.h:254`）是 `int32_t`，指定张量的维度数。当 `ndim == 0` 时表示标量（0 维张量），此时 `shape` 和 `strides` 可以为 NULL。

TVM FFI 通过 `Tensor::ndim()`（`tensor.h:295`）访问：

```cpp
int32_t ndim() const { return get()->ndim; }
```

`Tensor::dim()`（`tensor.h:627`）是 ATen 风格的别名，转发到 `ndim()`。

## dtype：数据类型

`dtype`（`dlpack.h:256`）是 `DLDataType` 结构（`dlpack.h:202`）：

```c
typedef struct {
  uint8_t code;
  uint8_t bits;
  uint16_t lanes;
} DLDataType;
```

- `code`：类型代码，取自 `DLDataTypeCode` 枚举（`dlpack.h:141`）：`kDLInt=0`、`kDLUInt=1`、`kDLFloat=2`、`kDLBfloat=4`、`kDLComplex=5`、`kDLBool=6`，以及 fp8/fp6/fp4 等子字节类型代码（7-17）。
- `bits`：元素位数，常见值 8、16、32、64。子字节类型如 fp4 设为 4，fp6 设为 6，fp8 设为 8。
- `lanes`：向量通道数，1 表示标量类型，>1 表示向量化类型（如 float4 对应 `code=2, bits=32, lanes=4`）。

子字节类型（fp4/fp6）在内存中是**打包存储**的。DLPack 规定数据采用小端位序：第 i 个元素存储在 `(D >> (i * bits)) & bit_mask`（`dlpack.h:199-200`）。`GetDataSize`（`tensor.h:105`）正确计算打包类型的字节数：

```cpp
inline size_t GetDataSize(size_t numel, DLDataType dtype) {
  return static_cast<size_t>(
      (static_cast<uint64_t>(numel) * dtype.bits * dtype.lanes + 7) / 8);
}
```

TVM FFI 通过 `Tensor::dtype()`（`tensor.h:301`）返回 `DLDataType`。

## shape：形状数组

`shape`（`dlpack.h:262`）是 `int64_t*`，指向长度为 `ndim` 的数组，每个元素指定对应维度的大小。当 `ndim == 0` 时可为 NULL。

在 TVM FFI 中，shape 存储在 `TensorObj` 对象尾部的内联空间中（由 `make_inplace_array_object` 分配），通过 `Tensor::shape()`（`tensor.h:307`）返回 `ShapeView`：

```cpp
ShapeView shape() const {
  const TensorObj* obj = get();
  return tvm::ffi::ShapeView(obj->shape, obj->ndim);
}
```

`ShapeView` 是一个非拥有的轻量视图，提供 `size()`、`operator[]`、`Product()`（计算元素总数）等方法。`Tensor::size(idx)`（`tensor.h:328`）支持负索引访问单个维度大小。

`Tensor::numel()`（`tensor.h:358`）通过 `shape().Product()` 计算元素总数。

## strides：步长数组

`strides`（`dlpack.h:275`）是 `int64_t*`，指向长度为 `ndim` 的数组，指定每个维度上相邻元素的**元素数**偏移（非字节偏移）。

关键语义变化：
- **DLPack v1.2 之前**：`strides` 可以为 NULL，表示紧凑连续（C 顺序/行优先）布局。
- **DLPack v1.2 及以后**：`strides` 不允许为 NULL（ndim != 0 时），消费者可始终安全访问 `strides[dim]`（`dlpack.h:270-273`）。

对于紧凑行优先布局，strides 满足：`strides[i] = product(shape[i+1..ndim-1])`。例如 shape `(2,3,4)` 的紧凑 strides 为 `(12,4,1)`。

TVM FFI 中，`Tensor::strides()`（`tensor.h:316`）返回 `ShapeView`，并内部检查 strides 非空（ndim > 0 时）：

```cpp
ShapeView strides() const {
  const TensorObj* obj = get();
  TVM_FFI_ICHECK(obj->strides != nullptr || obj->ndim == 0);
  return ShapeView(obj->strides, obj->ndim);
}
```

当从 strides 为 NULL 的旧版 DLPack 导入时，`TensorObjFromDLPack` 会在对象尾部内联计算并填充 strides（`tensor.h:234-238`），确保内部 strides 始终有效。`FillStridesFromShape`（`shape.h:165`）执行计算。

`Tensor::stride(idx)`（`tensor.h:344`）支持负索引访问单个维度步长。

## byte_offset：字节偏移

`byte_offset`（`dlpack.h:277`）是 `uint64_t`，指定从 `data` 指针到张量第一个元素的字节偏移。这支持张量视图共享同一数据缓冲区但起始位置不同。

在 `Tensor::as_strided`（`tensor.h:384`）中，`element_offset`（以元素为单位）被转换为字节偏移：

```cpp
prototype.byte_offset += GetDataSize(static_cast<size_t>(elem_offset_as_i64), prototype.dtype);
```

对于**直接地址设备**（CPU、CUDA、ROCm 等），`as_strided` 会将 byte_offset 直接加到 data 指针上并将 byte_offset 归零（`tensor.h:396-401`），简化后续访问：

```cpp
if (prototype.byte_offset != 0 && IsDirectAddressDevice(prototype.device)) {
  prototype.data =
      reinterpret_cast<void*>(reinterpret_cast<char*>(prototype.data) + prototype.byte_offset);
  prototype.byte_offset = 0;
}
```

`IsDirectAddressDevice`（`tensor.h:48`）判断设备类型是否支持直接地址运算。对于非直接地址设备（如 OpenCL），byte_offset 保持不变，由设备运行时解释。

TVM FFI 通过 `Tensor::byte_offset()`（`tensor.h:363`）访问。

## 元数据组合语义

七个字段共同确定张量中任意元素的地址。对于直接地址设备，元素 `(i0, i1, ..., in-1)` 的地址为：

```
(char*)data + byte_offset + sum(ik * strides[k]) * (dtype.bits * dtype.lanes / 8)
```

数据总字节数由 `GetDataSize(const DLTensor&)`（`tensor.h:117`）计算：先求 shape 各维乘积得到元素数，再乘以每元素字节数。

## 设计分析

1. **极简元数据**：DLTensor 仅七个字段即可描述任意步长、任意设备、任意数据类型的多维数组，包括 sub-byte 打包类型和向量类型。这种极简性是其成为跨框架交换标准的关键。

2. **strides 单位选择**：strides 以元素数而非字节为单位，简化了不同 dtype 下的步长计算，但要求消费者结合 dtype 计算实际地址。这也意味着 sub-byte 类型的位偏移需要额外处理。

3. **byte_offset 的设备差异**：对于不透明句柄设备，byte_offset 无法直接加到指针上，必须由设备运行时解释。TVM FFI 的 `IsDirectAddressDevice` 分支处理了这一差异。

4. **向后兼容**：TVM FFI 对 strides=NULL 的旧版 DLPack 进行内联补全，对版本化结构体检查 flags，体现了对协议演进的兼容处理。

## NPU建议

1. **NPU 自定义设备类型注册**：NPU 设备应使用 128 以上的扩展设备类型值（如 `kDLNPU = 128` 或通过 DLPack 扩展注册），避免与官方枚举冲突。在 `DLDevice.device_type` 中使用该值，使框架能识别张量位于 NPU 上。建议同时在 `device.h` 的 `TryParseDLDeviceType` 中注册 `"npu"` 字符串映射。

2. **NPU dtype 支持矩阵**：NPU 通常支持有限的数据类型集合（如 int8/int16/fp16/bf16/int32），不支持 fp64 或复杂类型。建议在 NPU 算子入口检查 `dtype.code/bits/lanes`，对不支持的类型返回明确错误。对于 NPU 原生支持的 fp8/int4 等子字节类型，确保 DMA 引擎正确处理打包存储——`data` 指针和 `byte_offset` 应满足 NPU 的位对齐要求。

3. **shape/stride 内联存储的 DMA 友好性**：TVM FFI 将 shape/stride 内联在 TensorObj 尾部，物理上与对象头连续。NPU 驱动在构造 DMA 描述符时可一次性读取对象头后的连续内存获取所有维度信息，减少主机侧内存访问次数。建议 NPU 命令链构建函数直接遍历 `shape`/`strides` 数组填充描述符，避免二次拷贝。

4. **NPU 对非连续张量的支持**：NPU DMA 引擎可能仅支持连续张量的块传输。建议在 NPU 算子调度前调用 `Tensor::IsContiguous()` 检查（详见视角071），若非连续则回退到：(a) NPU 支持 strided DMA 时直接使用 strides 构造描述符；(b) 否则分配临时连续缓冲区并插入 pack/unpack 操作。

5. **byte_offset 与 NPU 地址转换**：若 NPU 使用 IO 地址空间而非 CPU 虚拟地址，`data` 可能存储 NPU IO 地址或句柄。`byte_offset` 的加法必须在 NPU 地址空间中进行。建议 NPU 运行时实现 `npu_resolve_address(data, byte_offset)` 函数，在构造 DMA 描述符时统一处理地址转换，而非依赖 CPU 指针运算。

6. **零尺寸张量处理**：NPU 算子可能收到空张量（shape 含 0 维度）。DLTensor 规范要求此时 `data = NULL`。建议 NPU 算子入口检查 `numel() == 0`，直接返回不提交 DMA 命令，避免 NPU 对 NULL 指针的非法访问。

## 相关概念

- [066 Tensor 对象设计](066-tensor-object-design.md)：TensorObj 继承 DLTensor
- [067 DLPack 零拷贝互操作](067-dlpack-zero-copy-interop.md)：元数据在交换中的作用
- [071 连续性检查](071-contiguity-check.md)：IsContiguous 基于 strides 的判定
- [070 张量对齐检查](070-tensor-alignment-check.md)：IsAligned 基于 data 和 byte_offset
- [057 Shape 形状对象](/04-containers/concepts/057-shape-object.md)：ShapeView 与 ShapeObj
- [075 张量设备管理](075-tensor-device-management.md)：DLDevice 与设备抽象
