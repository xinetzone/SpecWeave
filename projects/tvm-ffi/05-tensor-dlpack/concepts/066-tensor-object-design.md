---
type: Concept
title: "视角066：Tensor 对象设计"
description: "深入剖析 TensorObj/Tensor 的双重继承设计、内联 shape/stride 存储、NDAllocator 数据所有权模型，以及 TensorView 非拥有视图的实现机制。"
tags:
  - tensor
  - dlpack
  - object-design
  - multiple-inheritance
  - ndallocator
  - tensor-view
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-010, F-053, F-175, F-176, F-177, F-178, F-179, F-180, F-181, F-182, F-183, F-184, F-185, F-284, F-285, F-286, F-287
  - code:
    - include/tvm/ffi/container/tensor.h
    - src/ffi/tensor.cc
    - 3rdparty/dlpack/include/dlpack/dlpack.h
    - include/tvm/ffi/c_api.h
---

# 视角066：Tensor 对象设计

## 概述

`Tensor` 是 TVM FFI 中承载多维数组的核心容器类型，其底层对象 `TensorObj` 采用**双重继承**设计——同时继承自 `Object`（引用计数与运行时类型系统）和 `DLTensor`（DLPack 标准的张量元数据结构）。这种设计使得 `TensorObj` 本身就是一个合法的 `DLTensor`，无需额外的成员转发即可直接参与 DLPack 零拷贝交换。数据缓冲区的生命周期通过可定制的 `NDAllocator` 策略管理，shape 和 stride 则通过对象尾部的内联存储避免额外堆分配。此外，`TensorView` 提供了非拥有的轻量视图，适用于不需要持有引用的只读访问场景。

## TensorObj 的双重继承

`TensorObj` 定义在 `include/tvm/ffi/container/tensor.h:126`：

```cpp
class TensorObj : public Object, public DLTensor {
 public:
  static constexpr const uint32_t _type_index = TypeIndex::kTVMFFITensor;
  TVM_FFI_DECLARE_OBJECT_INFO_STATIC(StaticTypeKey::kTVMFFITensor, TensorObj, Object);
  // ...
};
```

关键点在于 `public DLTensor`——`TensorObj` 对象的内存布局中，`Object` 头之后直接紧跟 `DLTensor` 的各字段（`data`、`device`、`ndim`、`dtype`、`shape`、`strides`、`byte_offset`）。C ABI 辅助函数 `TVMFFITensorGetDLTensorPtr`（`c_api.h:1621`）正是利用这一布局，通过偏移 `sizeof(TVMFFIObject)` 直接获取 `DLTensor*`：

```cpp
inline DLTensor* TVMFFITensorGetDLTensorPtr(TVMFFIObjectHandle obj) {
  return reinterpret_cast<DLTensor*>(reinterpret_cast<char*>(obj) + sizeof(TVMFFIObject));
}
```

类型索引为 `kTVMFFITensor = 70`（`c_api.h:165`），类型键为 `"ffi.TensorObj"`。这使得 `Tensor` 可以通过 FFI 边界以类型索引 70 传递，并在 Any 中识别为 Tensor 对象。

## 内联 shape 与 stride 存储

`TensorObj` 本身不直接声明 shape/stride 数组，而是通过 `make_inplace_array_object` 在对象尾部**内联分配** shape 和 stride 存储空间。这一模式体现在两个辅助类中。

`TensorObjFromNDAlloc<TNDAlloc>`（`tensor.h:185`）在构造函数中计算尾部空间并设置 shape/stride 指针：

```cpp
this->shape = reinterpret_cast<int64_t*>(reinterpret_cast<char*>(this) + sizeof(Self));
this->strides = this->shape + shape.size();
std::copy(shape.begin(), shape.end(), this->shape);
details::FillStridesFromShape(shape, this->strides);
```

静态工厂 `Tensor::FromNDAlloc`（`tensor.h:470`）分配 `shape.size() * 2` 个 `int64_t` 的尾部空间：

```cpp
size_t num_extra_i64_at_tail = shape.size() * 2;
return Tensor(make_inplace_array_object<details::TensorObjFromNDAlloc<TNDAlloc>, int64_t>(
    num_extra_i64_at_tail, alloc, shape, dtype, device, ...));
```

当从 DLPack 导入时，若外部张量的 `strides` 为 `nullptr`（表示紧凑连续），`TensorObjFromDLPack`（`tensor.h:227`）同样会在尾部内联计算并填充 strides（`extra_strides_at_tail=true` 路径，`tensor.h:234-238`），避免后续访问空指针。

`FillStridesFromShape`（`shape.h:165`）按从后往前的顺序计算行优先紧凑步长：

```cpp
TVM_FFI_INLINE void FillStridesFromShape(ShapeView shape, int64_t* out_strides) {
  int64_t stride = 1;
  for (int64_t i = static_cast<int64_t>(shape.size()) - 1; i >= 0; --i) {
    out_strides[i] = stride;
    stride *= shape[i];
  }
}
```

## NDAllocator 数据所有权模型

`TensorObj` 本身不负责分配数据缓冲区，而是通过模板策略 `TNDAlloc` 将分配/释放委托给调用者。`TensorObjFromNDAlloc` 在构造时调用 `alloc_.AllocData(...)`，在析构时调用 `alloc_.FreeData(...)`（`tensor.h:219`）：

```cpp
~TensorObjFromNDAlloc() { alloc_.FreeData(static_cast<DLTensor*>(this)); }
```

`Tensor::FromNDAlloc`（`tensor.h:470`）接受任意满足 `AllocData`/`FreeData` 签名的分配器。源码注释（`tensor.h:421-457`）提供了 CPU、CUDA、NVSHMEM 三种示例分配器。这种策略模式使得同一套 Tensor 基础设施可以承载任意设备类型的内存——从 CPU 的 `malloc` 到 NPU 的设备内存分配，只需实现对应的分配器。

`FromNDAllocStrided`（`tensor.h:496`）是支持显式 strides 的变体，要求 shape 和 strides 等长。`FromEnvAlloc`（`tensor.h:532`）则通过函数指针 `TVMFFIEnvTensorAlloc` 从线程本地环境分配器创建 Tensor，适用于内核库需要从宿主框架获取中间张量内存的场景。

## Tensor 引用包装器

`Tensor` 类定义在 `tensor.h:260`，继承自 `ObjectRef`，提供值语义的句柄。拷贝仅增加引用计数，移动则转移所有权。其访问器方法直接转发到底层 `DLTensor` 字段：

- `data_ptr()`（`tensor.h:283`）返回 `void*`
- `device()`（`tensor.h:289`）返回 `DLDevice`
- `ndim()`（`tensor.h:295`）返回 `int32_t`
- `dtype()`（`tensor.h:301`）返回 `DLDataType`
- `shape()`（`tensor.h:307`）返回 `ShapeView`
- `strides()`（`tensor.h:316`）返回 `ShapeView`
- `numel()`（`tensor.h:358`）返回 shape 各维乘积
- `byte_offset()`（`tensor.h:363`）返回 `uint64_t`

`shape()` 和 `strides()` 返回 `ShapeView` 而非裸指针，提供边界安全的尺寸访问。`size(idx)` 和 `stride(idx)`（`tensor.h:328,344`）支持负索引（Python 风格），越界时抛出 `IndexError`。

`GetDLTensorPtr()`（`tensor.h:616`）返回 `const DLTensor*`，由于 `TensorObj` 本身就是 `DLTensor`，此操作仅为静态类型转换，零开销。

## TensorView 非拥有视图

`TensorView`（`tensor.h:667`）是一个纯值类型，内部存储一个 `DLTensor tensor_` 副本（`tensor.h:860`），不持有任何引用计数。它可以从 `Tensor` 或 `DLTensor*` 隐式构造：

```cpp
TensorView(const Tensor& tensor) {
  TVM_FFI_ICHECK(tensor.defined());
  tensor_ = *tensor.GetDLTensorPtr();
}
```

关键设计决策是**删除了从 `Tensor&&` 的移动构造**（`tensor.h:719`），防止将临时 Tensor 的数据悬挂到视图中。`TensorView` 同样提供 `data_ptr()`、`device()`、`shape()`、`strides()`、`IsContiguous()` 等访问器，但不提供 `ToDLPack()` 等所有权转移操作。

`TypeTraits<TensorView>`（`tensor.h:930`）将其映射到类型索引 `kTVMFFIDLTensorPtr = 7`，且 `storage_enabled = false`——这意味着 `TensorView` 不能存入 `Any`（不能跨边界持有所有权），只能通过 `CopyToAnyView` 传递其内部 `DLTensor*` 到 AnyView。`TypeTraits<DLTensor*>`（`tensor.h:886`）的 `MoveToAny` 直接抛出异常，明确提示使用 `Tensor` 代替。

## 设计分析

1. **双重继承的利弊**：`TensorObj` 同时继承 `Object` 和 `DLTensor` 消除了包装层开销，使得 ToDLPack 可以直接拷贝 `DLTensor` 字段。但 C++ 多重继承在某些 ABI 下可能引入调整 thunk，不过由于 `DLTensor` 是标准布局的 C 结构体，实际偏移在所有主流编译器上均可预测。

2. **分配器策略的开放性**：通过模板化的 `NDAllocator`，Tensor 核心不需要链接任何设备 SDK。设备内存的分配逻辑完全由调用者注入，符合"机制与策略分离"原则。这也是 NPU 集成的关键扩展点。

3. **内联存储的取舍**：shape/stride 内联在对象尾部避免了两次堆分配（对象+元数据），提升了缓存局部性。但这也意味着无法在对象创建后改变维度数（ndim），strided view 必须通过创建新对象实现。

4. **所有权层级**：`TensorObj` 的引用计数管理对象本身（含 shape/stride 内联存储），而数据缓冲区的生命周期由 `NDAllocator::FreeData` 或 DLPack 的 `deleter` 管理。两层生命周期通过析构函数链正确衔接。

## NPU建议

1. **实现 NPU 专用 NDAllocator**：建议 NPU 运行时实现 `NPUNDAlloc` 结构体，在 `AllocData` 中调用 NPU 驱动的设备内存分配 API（如 `npu_malloc`/`npu_alloc_device_memory`），在 `FreeData` 中调用对应释放函数。分配大小应使用 `ffi::GetDataSize(*tensor)` 计算，确保正确处理 sub-byte 类型（fp4/fp6）的打包存储。

2. **NPU 内存对齐分配**：NPU DMA 引擎通常要求数据缓冲区按特定边界对齐（如 64 字节、128 字节或 4KB 页对齐）。建议在 `AllocData` 中使用对齐分配（如 `aligned_alloc(NPU_ALIGNMENT, size)` 或 NPU 驱动的对齐分配 API），并通过 `Tensor::IsAligned(NPU_ALIGNMENT)` 在导入外部张量时验证对齐。建议默认对齐到 64 字节以覆盖大多数 NPU DMA 描述符要求。

3. **使用 FromEnvAlloc 集成内核库**：当 NPU 内核库作为动态模块加载到宿主框架时，建议使用 `Tensor::FromEnvAlloc(TVMFFIEnvTensorAlloc, ...)` 从宿主环境分配中间张量，而非自行分配。这样可确保内存在宿主框架的内存池统一管理，避免模块卸载后悬空指针。注意模块必须在返回的 Tensor 释放前保持加载状态。

4. **零拷贝 DMA 描述符准备**：NPU 算子启动时需要从 Tensor 提取 DMA 描述符信息。建议通过 `Tensor::GetDLTensorPtr()` 获取 `DLTensor*`，直接读取 `data`（NPU 设备虚拟地址）、`shape`、`strides`、`dtype`、`byte_offset` 字段填充 DMA 命令链，避免额外的元数据拷贝。对于 strided Tensor，strides 以元素为单位（非字节），构造 DMA 描述符时需乘以 `dtype.bits * dtype.lanes / 8`。

5. **TensorView 用于算子参数**：建议 NPU 算子函数签名使用 `ffi::TensorView` 而非 `ffi::Tensor` 作为输入参数类型。`TensorView` 仅 72 字节左右（DLTensor 大小），按值传递开销极低，且不会增加引用计数。但需注意：调用者必须保证输入 Tensor 在算子执行期间存活——对于异步 NPU 算子，应在流同步前持有 Tensor 强引用。

6. **NPU 片上内存管理**：对于 NPU 片上 SRAM/ scratchpad memory，可实现自定义 `NPUScratchpadAlloc`，在 `AllocData` 中从预分配的片上内存池分配，`FreeData` 中归还。结合 `FromNDAllocStrided` 支持 double-buffer 等复杂访问模式。

## 相关概念

- [067 DLPack 零拷贝互操作](067-dlpack-zero-copy-interop.md)：ToDLPack/FromDLPack 的零拷贝机制
- [068 DLManagedTensor 生命周期](068-dlmanaged-tensor-lifecycle.md)：DLPack deleter 与引用计数的衔接
- [069 DLTensor 元数据](069-dltensor-metadata.md)：DLTensor 各字段的语义
- [072 不安全张量视图](072-unsafe-tensor-view.md)：as_strided 与 TVMFFITensorCreateUnsafeView
- [013 内存所有权模型](/01-architecture/concepts/013-memory-ownership-model.md)：Object 引用计数与数据缓冲区的两层所有权
- [061 原地数组存储](/04-containers/concepts/061-inplace-array-storage.md)：make_inplace_array_object 内联分配模式
