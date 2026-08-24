---
type: Concept
title: "视角072：不安全张量视图"
description: "剖析 as_strided 与 TVMFFITensorCreateUnsafeView 实现的不安全张量视图机制，包括 ViewNDAlloc 源张量持有、prototype 元数据拷贝、byte_offset 折叠，以及使用约束与风险。"
tags:
  - tensor
  - dlpack
  - unsafe-view
  - as-strided
  - zero-copy
  - viewndalloc
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-054, F-182
  - code:
    - include/tvm/ffi/container/tensor.h
    - src/ffi/tensor.cc
    - include/tvm/ffi/c_api.h
---

# 视角072：不安全张量视图

## 概述

张量视图（view）是在不拷贝数据的前提下创建张量别名的机制——通过修改 shape、strides 和 byte_offset，同一块数据缓冲区可以呈现不同的逻辑形状。TVM FFI 提供 `Tensor::as_strided` 方法和 C ABI 函数 `TVMFFITensorCreateUnsafeView` 来创建不安全视图。之所以称为"不安全"，是因为视图共享源张量的数据缓冲区但不复制 shape/strides 元数据，调用者必须确保视图访问的内存范围在源张量的分配范围内，且源张量在视图存活期间不被释放。这一机制是切片、转置、expand 等操作的零拷贝基础。

## as_strided 方法

`Tensor::as_strided` 定义在 `include/tvm/ffi/container/tensor.h:384`：

```cpp
Tensor as_strided(ShapeView shape, ShapeView strides,
                  std::optional<int64_t> element_offset = std::nullopt) const {
  DLTensor prototype;
  prototype = *static_cast<const DLTensor*>(get());
  prototype.shape = const_cast<int64_t*>(shape.data());
  prototype.ndim = static_cast<int>(shape.size());
  prototype.strides = const_cast<int64_t*>(strides.data());
  int64_t elem_offset_as_i64 = element_offset.value_or(0);

  TVM_FFI_ICHECK_GE(elem_offset_as_i64, 0);
  prototype.byte_offset += GetDataSize(static_cast<size_t>(elem_offset_as_i64), prototype.dtype);

  if (prototype.byte_offset != 0 && IsDirectAddressDevice(prototype.device)) {
    prototype.data =
        reinterpret_cast<void*>(reinterpret_cast<char*>(prototype.data) + prototype.byte_offset);
    prototype.byte_offset = 0;
  }

  TVMFFIObjectHandle out;
  Object* obj_handle = const_cast<TensorObj*>(get());
  TVM_FFI_CHECK_SAFE_CALL(TVMFFITensorCreateUnsafeView(obj_handle, &prototype, &out));
  return Tensor(
      details::ObjectUnsafe::ObjectPtrFromOwned<TensorObj>(static_cast<TVMFFIObject*>(out)));
}
```

执行步骤：

1. **构造 prototype**：从当前 Tensor 拷贝一份 `DLTensor` 作为原型，然后替换 shape、ndim、strides 为调用者提供的新值。
2. **元素偏移转换**：`element_offset` 以 dtype 元素为单位，通过 `GetDataSize(elem_offset, dtype)` 转换为字节偏移，累加到 `prototype.byte_offset`。
3. **非负检查**：`TVM_FFI_ICHECK_GE(elem_offset_as_i64, 0)` 确保偏移不为负。
4. **直接地址折叠**：若设备支持直接地址且 byte_offset 非零，将偏移加到 data 指针并归零 byte_offset，简化后续地址计算。
5. **调用 C ABI**：通过 `TVMFFITensorCreateUnsafeView` 创建视图 Tensor，该函数内部持有源张量的引用。

## TVMFFITensorCreateUnsafeView 实现

C ABI 函数定义在 `src/ffi/tensor.cc:50`：

```cpp
int TVMFFITensorCreateUnsafeView(TVMFFIObjectHandle source, const DLTensor* prototype,
                                 TVMFFIObjectHandle* out) {
  TVM_FFI_SAFE_CALL_BEGIN();
  tvm::ffi::ObjectPtr<tvm::ffi::TensorObj> source_tensor =
      tvm::ffi::details::ObjectUnsafe::ObjectPtrFromUnowned<tvm::ffi::TensorObj>(
          static_cast<tvm::ffi::Object*>(source));

  class ViewNDAlloc {
   public:
    explicit ViewNDAlloc(tvm::ffi::ObjectPtr<tvm::ffi::TensorObj> tensor)
        : tensor_(std::move(tensor)) {}
    void AllocData(DLTensor* tensor, void* data_ptr) { tensor->data = data_ptr; }
    void FreeData(DLTensor* tensor) {}

   private:
    tvm::ffi::ObjectPtr<tvm::ffi::TensorObj> tensor_;
  };

  void* source_data_ptr = prototype->data;
  size_t num_extra_i64_at_tail = static_cast<size_t>(prototype->ndim) * 2;
  ViewNDAlloc alloc(source_tensor);
  tvm::ffi::Tensor ret_tensor(
      tvm::ffi::make_inplace_array_object<tvm::ffi::details::TensorObjFromNDAlloc<ViewNDAlloc>,
                                          int64_t>(num_extra_i64_at_tail, alloc, *prototype,
                                                   source_data_ptr));
  *out = tvm::ffi::details::ObjectUnsafe::MoveObjectRefToTVMFFIObjectPtr(std::move(ret_tensor));
  TVM_FFI_SAFE_CALL_END();
}
```

关键设计：

1. **源张量持有**：`ViewNDAlloc` 类内部持有一个 `ObjectPtr<TensorObj>`（强引用），确保源 Tensor 在视图存活期间不被析构。这是通过 C++ RAII 实现的自动生命周期管理。
2. **复用 NDAlloc 框架**：视图复用了 `TensorObjFromNDAlloc<ViewNDAlloc>` 基础设施。`AllocData` 仅将 `data_ptr`（来自 prototype 的 data 指针）赋给 tensor->data，不实际分配内存；`FreeData` 为空，因为视图不拥有数据。
3. **内联 shape/stride**：分配 `ndim * 2` 个 int64_t 的尾部空间，`TensorObjFromNDAlloc` 构造函数会从 prototype 拷贝 shape 和 strides 到内联存储（`tensor.h:213-214`），确保视图的元数据自包含。
4. **ViewNDAlloc 析构**：当视图 Tensor 释放时，`TensorObjFromNDAlloc` 析构调用 `alloc_.FreeData()`（空操作），然后 `ViewNDAlloc` 析构释放源张量的强引用。若这是源张量的最后一个引用，源张量才真正析构并释放数据。

## TensorView 的 as_strided

`TensorView::as_strided`（`tensor.h:840`）是更轻量的版本，直接返回新的 `TensorView` 而不创建 TensorObj：

```cpp
TensorView as_strided(ShapeView shape, ShapeView strides,
                      std::optional<int64_t> element_offset = std::nullopt) const {
  DLTensor prototype = tensor_;
  prototype.shape = const_cast<int64_t*>(shape.data());
  prototype.ndim = static_cast<int>(shape.size());
  prototype.strides = const_cast<int64_t*>(strides.data());
  // ... offset 和 direct address 折叠逻辑 ...
  return TensorView(&prototype);
}
```

源码注释（`tensor.h:822-838`）给出了明确的警告：调用者必须确保 shape/strides 数组和 data 指针在返回的 TensorView 生命周期内有效。一个常见的反模式是传入临时 shape/strides 数组，在 as_strided 返回后立即释放，导致 TensorView 指向无效内存。

`TensorView` 的 as_strided 不持有源张量引用，因此适用于源张量生命周期明确长于视图的场景（如函数参数内的临时计算）。

## 不安全的语义边界

视图操作被称为"不安全"是因为：

1. **越界访问**：as_strided 不检查新 shape/strides 访问的内存是否在源张量的分配范围内。恶意或错误的 shape/strides 可导致越界读写。
2. **别名修改**：多个视图共享同一数据，通过一个视图修改会影响其他视图和源张量。
3. **生命周期依赖**：Tensor 视图通过 ViewNDAlloc 持有源引用来保证安全，但 TensorView 不持有，需调用者手动保证。
4. **shape/strides 生命周期**：TensorView 直接指向外部 shape/strides 数组，不拷贝。

## 设计分析

1. **复用 NDAlloc 框架的巧妙性**：视图通过实现一个"空分配器" ViewNDAlloc 来复用 `TensorObjFromNDAlloc` 的内联 shape/stride 存储和生命周期管理，无需为视图单独创建 TensorObj 子类。`AllocData` 设置 data 指针、`FreeData` 空操作，语义恰好匹配视图需求。

2. **源引用的自动化管理**：ViewNDAlloc 持有 `ObjectPtr<TensorObj>` 是强引用，视图存活期间源张量不会释放。这一设计将生命周期安全内建到类型系统中，无需调用者手动管理。

3. **C ABI 桥接**：`TVMFFITensorCreateUnsafeView` 通过 `SAFE_CALL` 宏包装，将 C++ 异常转换为错误码。源句柄通过 `ObjectPtrFromUnowned` 转换为不拥有指针再构造 ObjectPtr，正确处理了 FFI 边界的引用计数。

4. **Tensor vs TensorView 视图的取舍**：Tensor 视图安全但有创建 TensorObj 的开销（堆分配+引用计数）；TensorView 视图零开销但需手动保证生命周期。两者服务于不同场景。

## NPU建议

1. **NPU 算子中的视图零拷贝**：NPU 算子常需处理切片（slice）、展开（expand）、转置（transpose）等操作。建议优先使用 `as_strided` 创建零拷贝视图，避免为中间结果分配 NPU 设备内存。视图 Tensor 通过 ViewNDAlloc 持有源张量引用，可安全传递给异步 NPU 算子——源张量在算子完成前不会释放。

2. **NPU DMA 描述符中的 strides 处理**：从视图构造 NPU DMA 描述符时，必须使用视图自身的 shape/strides（已内联拷贝到 TensorObj 尾部），而非源张量的。建议 NPU 命令链构建函数接收 `DLTensor*`，直接读取其 shape/strides 字段，确保视图的非连续布局正确反映在 DMA 步长中。

3. **越界保护**：虽然 as_strided 不检查边界，但 NPU 硬件有内存保护单元（MPU）。建议 NPU 运行时在提交 DMA 前进行软件边界检查：计算视图访问的地址范围 `[data + min_offset, data + max_offset + element_size)`，验证其落在源张量的分配范围内（可通过源张量的 `GetDataSize` 估算紧凑数据量，但非连续视图的实际范围可能更大，需用 max(stride * (shape-1)) 计算）。

4. **NPU 上的 strided 视图性能**：非连续视图在 NPU 上可能无法利用突发传输。建议 NPU 编译器/运行时对视图进行分类：
   - 连续视图（IsContiguous 返回 true）：使用块 DMA。
   - 规则 strided 视图（各维 stride 固定）：使用 NPU 的 2D/3D strided DMA。
   - 不规则视图：回退到临时连续缓冲区 + pack DMA。

5. **视图与 NPU 缓存一致性**：视图共享源数据缓冲区，通过视图写入数据后，源张量和其他视图在 CPU 端立即可见（同一块内存）。但 NPU 缓存可能独立，建议在视图写入后、其他设备读取前插入 NPU 缓存刷新操作。对于只读视图（如权重切片），可设置 NPU 缓存为只读模式避免一致性开销。

6. **element_offset 的 NPU 地址计算**：as_strided 的 element_offset 被转换为字节偏移并折叠到 data 指针。NPU DMA 描述符应直接使用视图的 `data` 指针（已包含偏移），不要再额外加 byte_offset。对于非直接地址设备（byte_offset 未折叠），NPU 驱动需在地址翻译时包含 byte_offset。

7. **避免 TensorView 在异步 NPU 操作中使用**：TensorView 不持有源张量引用。若 NPU 算子异步执行，TensorView 可能在 NPU 完成前被销毁（局部变量离开作用域），导致 shape/strides 悬空。建议跨异步边界传递 Tensor 强引用而非 TensorView，在算子函数内部如需轻量访问再从 Tensor 构造 TensorView。

## 相关概念

- [066 Tensor 对象设计](066-tensor-object-design.md)：TensorObjFromNDAlloc 与内联存储
- [069 DLTensor 元数据](069-dltensor-metadata.md)：shape/strides/byte_offset 语义
- [071 连续性检查](071-contiguity-check.md)：视图连续性判定
- [068 DLManagedTensor 生命周期](068-dlmanaged-tensor-lifecycle.md)：源引用持有机制
- [075 张量设备管理](075-tensor-device-management.md)：IsDirectAddressDevice 与偏移折叠
