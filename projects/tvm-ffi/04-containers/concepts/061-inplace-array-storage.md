---
type: Concept
title: "视角061：原地数组存储"
description: "深入剖析 make_inplace_array_object 原地数组存储机制，包括对象头与元素数据的连续分配、data_deleter 约定、ArrayObj/ShapeObj/SmallMapBaseObj 的内联布局以及与 ListObj 堆分配的对比。"
tags:
  - containers
  - inplace-storage
  - memory-layout
  - allocation
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-173, F-174
  - code:
    - include/tvm/ffi/memory.h
    - include/tvm/ffi/container/array.h
    - include/tvm/ffi/container/shape.h
    - include/tvm/ffi/container/map_base.h
---

# 视角061：原地数组存储

## 概述

原地数组存储（inplace array storage）是 TVM FFI 容器系统的核心内存优化模式。通过 `make_inplace_array_object` 工厂函数，对象头与其尾部的元素数组在**单次堆分配**中连续布局，消除了独立的数据指针和二次分配开销。这一模式被 `ArrayObj`、`ShapeObj`、`SmallMapBaseObj` 和大字符串/字节对象广泛采用。与之相对，`ListObj` 使用独立的堆缓冲区存储元素。本视角剖析原地存储的实现机制、布局约束和工程权衡。

## make_inplace_array_object

`make_inplace_array_object` 定义在 `include/tvm/ffi/memory.h:303`：

```cpp
template <typename ArrayType, typename ElemType, typename... Args>
inline ObjectPtr<ArrayType> make_inplace_array_object(size_t num_elems,
                                                       Args&&... args) {
  return details::SimpleObjAllocator().make_inplace_array<ArrayType, ElemType>(
      num_elems, std::forward<Args>(args)...);
}
```

该函数委托给 `SimpleObjAllocator::make_inplace_array`，后者分配 `sizeof(ArrayType) + num_elems * sizeof(ElemType)` 字节的连续内存，在起始处 placement-new 构造 `ArrayType` 对象（传入 `args`），尾部空间留作元素数组。返回的 `ObjectPtr<ArrayType>` 管理整块内存的生命周期，对象析构时整块内存一次性释放。

模板参数说明：
- **ArrayType**：对象头类型，必须继承自 `Object`。
- **ElemType**：尾部元素类型（如 `Any`、`int64_t`、`char`、`KVType`）。
- **Args**：传递给 `ArrayType` 构造函数的参数。

## ArrayObj 的内联布局

`ArrayObj::Empty`（`array.h:121`）是原地存储的典型应用：

```cpp
static ObjectPtr<ArrayObj> Empty(int64_t n = kInitSize) {
  ObjectPtr<ArrayObj> p = make_inplace_array_object<ArrayObj, Any>(n);
  p->TVMFFISeqCell::capacity = n;
  p->TVMFFISeqCell::size = 0;
  p->data = reinterpret_cast<char*>(p.get()) + sizeof(ArrayObj);
  p->data_deleter = nullptr;
  return p;
}
```

内存布局为：

```
+-------------------+  <-- p.get()
|   ArrayObj 头     |
| (Object + SeqCell)|
+-------------------+  <-- p->data
|   Any[0]          |
|   Any[1]          |
|   ...             |
|   Any[n-1]        |
+-------------------+
```

关键约定：`data` 指针设置为对象头之后的地址（`array.h:125`），`data_deleter` 设置为 `nullptr`（`array.h:126`）。`SeqBaseObj` 的析构函数（`seq_base.h:53`）检查 `data_deleter`：当为 `nullptr` 时，仅析构元素而不释放数据缓冲区，因为数据与对象头在同一块分配中，将随对象一起释放。

## ShapeObj 的内联布局

`ShapeObj` 通过 `MakeEmptyShape`（`shape.h:135`）使用原地存储：

```cpp
TVM_FFI_INLINE ObjectPtr<ShapeObj> MakeEmptyShape(size_t length,
                                                   int64_t** mutable_data) {
  ObjectPtr<ShapeObj> p = make_inplace_array_object<ShapeObj, int64_t>(length);
  static_assert(alignof(ShapeObj) % alignof(int64_t) == 0);
  static_assert(sizeof(ShapeObj) % alignof(int64_t) == 0);
  int64_t* data = reinterpret_cast<int64_t*>(
      reinterpret_cast<char*>(p.get()) + sizeof(ShapeObj));
  if (mutable_data) *mutable_data = data;
  p->data = data;
  p->size = length;
  return p;
}
```

两个静态断言（`shape.h:137-138`）确保 `ShapeObj` 的对齐和大小是 `alignof(int64_t)`（8 字节）的倍数。这是原地存储的关键约束——对象头的尾部对齐必须满足元素类型的对齐要求，否则尾部数据可能未对齐，导致某些架构上的性能惩罚或崩溃。

## SmallMapBaseObj 的内联布局

`SmallMapBaseObj::Empty`（`map_base.h:1305`）将原地存储推向更复杂的场景：

```cpp
template <typename MapObjType>
static ObjectPtr<Object> Empty(uint64_t n = kInitSize) {
  static_assert(alignof(SmallMapBaseObj) % alignof(KVType) == 0);
  static_assert(sizeof(SmallMapBaseObj) + kInitSize * sizeof(KVType) >=
                sizeof(DenseMapBaseObj));
  n = std::max(n, static_cast<uint64_t>(kInitSize));
  ObjectPtr<SmallMapBaseObj> p =
      ffi::make_inplace_array_object<SmallMapBaseObj, KVType>(n);
  p->data_ = reinterpret_cast<char*>(p.get()) + sizeof(SmallMapBaseObj);
  p->size_ = 0;
  p->SetSlotsAndSmallLayoutTag(n);
  p->header_.type_index = MapObjType::RuntimeTypeIndex();
  return p;
}
```

这里最精妙的设计是第二个静态断言（`map_base.h:1308`）：初始分配的空间必须足够大，以容纳未来原地升级后的 `DenseMapBaseObj` 头部。这意味着即使小表只有 2 个键值对，分配的内存也预留了稠密表头部的空间。当元素数量超出小表容量时，`Dict` 通过 `InplaceSwitchTo` 在同一块内存中将 `SmallMapBaseObj` 原地"改造"为 `DenseMapBaseObj`，对象地址不变。

## 大字符串的内联布局

`BytesBaseCell::InitSpaceForSize`（`string.h:206`）对超过 7 字节的字符串使用原地存储：

```cpp
ObjectPtr<LargeObj> ptr =
    make_inplace_array_object<LargeObj, char>(size + 1);
char* dest_data = reinterpret_cast<char*>(ptr.get()) + sizeof(LargeObj);
ptr->data = dest_data;
ptr->size = size;
```

字符数据（含 `\0` 终止符）紧邻 `StringObj`/`BytesObj` 头部之后分配。这使得字符串数据与对象元数据在同一缓存行或相邻缓存行中，提升了访问局部性。

## 与 ListObj 堆分配的对比

`ListObj::Empty`（`list.h:100`）采用了相反的策略：

```cpp
static ObjectPtr<ListObj> Empty(int64_t n = kInitSize) {
  ObjectPtr<ListObj> p = make_object<ListObj>();
  p->TVMFFISeqCell::capacity = n;
  p->TVMFFISeqCell::size = 0;
  p->data = n == 0 ? nullptr
                   : static_cast<void*>(::operator new(sizeof(Any) * n));
  p->data_deleter = RawDataDeleter;
  return p;
}
```

`ListObj` 使用 `make_object` 仅分配对象头，元素缓冲区通过 `::operator new` 独立分配。`data_deleter` 设置为 `RawDataDeleter`（`list.h:112`），在析构时调用 `::operator delete` 释放缓冲区。

两种策略的对比：

| 维度 | 原地存储（ArrayObj） | 堆分配（ListObj） |
|------|---------------------|-------------------|
| 分配次数 | 1 次（对象头+元素） | 2 次（对象头+缓冲区） |
| 扩容方式 | 整体复制到新分配 | 仅移动元素到新缓冲区 |
| data_deleter | nullptr | RawDataDeleter |
| 缓存局部性 | 更好（连续内存） | 略差（两次分配可能不相邻） |
| 适用场景 | 不可变/COW 容器 | 可变容器 |

`ListObj::Reserve`（`list.h:78`）扩容时只需移动元素到新缓冲区，对象头地址不变；而 `ArrayObj` 扩容需要重新分配整块内存并复制对象头和元素。但 `ArrayObj` 的 COW 语义意味着扩容只在唯一所有者时发生，整体复制的代价被修改频率所摊销。

## 对齐约束

原地存储要求对象头大小满足元素类型的对齐要求。`ShapeObj` 和 `SmallMapBaseObj` 都通过静态断言强制了这一点。对于 `ArrayObj`，元素类型为 `Any`（16 字节，8 字节对齐），而 `Object` 基类已确保足够的对齐。

如果对象头大小不是元素对齐的整数倍，尾部元素数组的起始地址将未对齐。`make_inplace_array_object` 的分配器通常返回最大对齐（如 16 字节）的内存，但对象头之后的偏移 `sizeof(ArrayType)` 也必须是 `alignof(ElemType)` 的倍数。

## NPU建议

在 NPU 环境中，原地数组存储模式具有特殊意义和优化空间：

1. **连续内存与 DMA 友好**：原地存储的对象头和数据在单次分配中连续布局，这对于 NPU 的 DMA 传输非常友好。建议在 NPU 运行时中，对张量形状（`ShapeObj`）和小型常量数组使用原地存储，使得 DMA 描述符可以直接引用连续物理内存，无需散列-聚集（scatter-gather）列表。

2. **对齐增强**：NPU 硬件通常要求比 CPU 更严格的内存对齐（如 64 字节或 128 字节缓存行对齐）。建议为 NPU 环境定制 `make_inplace_array_object` 的分配器，使其返回满足 NPU 对齐要求的内存。同时在静态断言中增加对 NPU 对齐的检查，例如 `static_assert(sizeof(ArrayObj) % 64 == 0)` 或使用 `alignas(64)` 标注关键容器对象。

3. **避免原地扩容**：NPU 计算图在执行阶段应避免内存分配和扩容。建议在编译期确定容器容量，使用 `ArrayObj::Empty(n)` 预分配足够空间，避免运行时触发 `SwitchContainer` 的整体复制。对于动态形状场景，考虑使用预分配的内存池。

4. **NPU 感知的数据布局**：原地存储的 `Any` 元素在 NPU 场景中可能不是最优的数据表示——`Any` 的 16 字节布局包含类型标签，而 NPU 更倾向于同类型、连续对齐的原始数据缓冲区。建议为 NPU 提供专用的"类型化原地数组"模板，绕过 `Any` 的类型擦除开销，直接存储 `float`/`int8_t` 等 NPU 原生类型。

5. **内存池集成**：NPU 的片上内存（SRAM）容量有限但带宽极高。建议将原地存储对象分配在 NPU 管理的内存池中，利用其连续布局特性减少 TLB miss 和页表遍历。对象头和数据在同一内存区域，避免了对象头在主机内存而数据在设备内存的分离情况。

6. **SmallMap 预留空间利用**：`SmallMapBaseObj` 预留给 `DenseMapBaseObj` 的空间在 NPU 场景中可以被进一步利用——例如在预留区域嵌入 NPU 特定的元数据（如硬件缓存行填充、预取提示），在不改变对象大小的前提下提升 NPU 访问效率。

## 设计分析

1. **单次分配的性能收益**：原地存储将两次堆分配合并为一次，减少了分配器开销和内存碎片。对于生命周期短、创建频繁的容器（如 IR 中的属性数组），这一优化累积效果显著。

2. **data_deleter 作为策略标记**：`TVMFFISeqCell::data_deleter` 字段巧妙地统一了两种存储策略——`nullptr` 表示内联（数据随对象释放），非空表示独立分配（需要单独释放）。C ABI 层无需知道具体子类即可正确管理内存。

3. **原地升级的设计创新**：`SmallMapBaseObj` 预留 `DenseMapBaseObj` 空间并原地切换，是可变容器在不改变对象地址的前提下实现存储升级的创新方案。这要求精确的内存布局计算和静态断言保障。

4. **COW 与原地存储的协同**：`ArrayObj` 的 COW 语义使得原地存储的扩容劣势（整体复制）被最小化——只有唯一所有者时才扩容，而唯一所有者的修改不需要复制。共享时的修改本就需要复制，原地存储的整体复制与分离存储的元素复制在 COW 场景下成本相近。

## 相关概念

- [051 Array 容器与写时复制](051-array-container.md)：ArrayObj 的原地存储与 COW
- [052 List 可变序列容器](052-list-container.md)：ListObj 的堆分配对比
- [056 MapBaseObj 与稠密哈希表](056-map-base-dense-hash.md)：SmallMapBaseObj 的原地升级
- [057 Shape 形状对象](057-shape-object.md)：ShapeObj 的内联布局
- [058 String 字符串对象](058-string-object.md)：大字符串的内联字符数据
