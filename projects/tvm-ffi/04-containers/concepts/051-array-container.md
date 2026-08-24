---
type: Concept
title: "视角051：Array 容器与写时复制"
description: "深入剖析 ArrayObj/Array<T> 容器的设计与实现，包括内联存储布局、写时复制（COW）语义、容量扩展策略以及类型化元素访问机制。"
tags:
  - containers
  - array
  - copy-on-write
  - inplace-storage
  - sequence
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-153, F-154
  - code:
    - include/tvm/ffi/container/array.h
    - include/tvm/ffi/container/seq_base.h
    - include/tvm/ffi/memory.h
---

# 视角051：Array 容器与写时复制

## 概述

`Array<T>` 是 TVM FFI 中最核心的序列容器，代表一段连续存储的类型化元素序列。其底层对象 `ArrayObj` 继承自 `SeqBaseObj`，采用**内联存储**（inplace storage）布局——元素数据直接紧邻对象头之后分配，无需额外的堆指针。`Array` 实现了**写时复制**（Copy-on-Write, COW）语义：当容器被多个引用共享时，修改操作会透明地创建底层副本；当引用计数为 1 时，则直接原地修改。这一设计在不可变值语义和可变操作效率之间取得了平衡。

## ArrayObj 内联存储布局

`ArrayObj` 定义在 `include/tvm/ffi/container/array.h:46`，继承自 `SeqBaseObj`。其静态工厂方法 `Empty`（`array.h:121`）通过 `make_inplace_array_object` 分配内存：

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

关键设计点在于 `p->data` 被设置为对象头之后的地址（`array.h:125`），且 `data_deleter` 为 `nullptr`（`array.h:126`），表示数据缓冲区与对象本身在同一块分配中，析构时无需单独释放。这与 `ListObj` 的独立堆分配形成鲜明对比（详见视角052）。

初始容量 `kInitSize` 为 4（`array.h:149`），扩展因子 `kIncFactor` 为 2（`array.h:152`）。这意味着空数组仅占用 `sizeof(ArrayObj) + 4 * sizeof(Any)` 的内存，对于小型集合非常高效。

## 写时复制机制

`Array` 的 COW 逻辑集中在 `CopyOnWrite` 方法中（`array.h:663`）：

```cpp
ArrayObj* CopyOnWrite() {
  if (data_ == nullptr) {
    return SwitchContainer(ArrayObj::kInitSize);
  }
  if (!data_.unique()) {
    return SwitchContainer(capacity());
  }
  return static_cast<ArrayObj*>(data_.get());
}
```

该方法的逻辑分三步：

1. **空句柄**：若 `data_` 为 null，创建初始容量为 4 的新容器。
2. **共享状态**：若 `data_.unique()` 返回 false（即存在多个引用），调用 `SwitchContainer` 创建当前容量的完整副本。
3. **唯一所有者**：直接返回底层指针，原地修改。

所有修改操作——`push_back`（`array.h:426`）、`emplace_back`（`array.h:437`）、`Set`（`array.h:587`）、`insert`（`array.h:448`）、`erase`（`array.h:487`）、`resize`（`array.h:514`）、`clear`（`array.h:541`）——都首先调用 `CopyOnWrite()` 获取唯一所有权的 `ArrayObj*`，然后在其上执行变更。这确保了 COW 语义对调用者完全透明。

`SwitchContainer`（`array.h:716`）负责分配新容器并迁移数据。它根据是否需要扩容选择 `CopyFrom`（`array.h:54`）或 `MoveFrom`（`array.h:75`），这两个工厂方法逐元素构造 `Any`，保证异常安全——size 仅在元素构造成功后递增。

## 类型化访问与 Any 转换

`Array<T>` 通过模板参数提供类型安全的元素访问。`operator[]`（`array.h:379`）返回 `T` 而非引用：

```cpp
const T operator[](int64_t i) const {
  ArrayObj* p = GetArrayObj();
  if (p == nullptr) {
    TVM_FFI_THROW(IndexError) << "cannot index a null array";
  }
  return details::AnyUnsafe::CopyFromAnyViewAfterCheck<T>(p->at(i));
}
```

底层存储统一为 `Any` 类型，每次访问通过 `CopyFromAnyViewAfterCheck<T>` 进行类型检查和转换。`Set` 方法（`array.h:587`）则执行反向操作，将 `T` 转换为 `Any` 后存入。

类型参数 `T` 必须满足 `storage_enabled_v<T>`（`array.h:214`），即要么是 `Any` 本身，要么其 `TypeTraits<T>::storage_enabled` 为 true。这一约束在 `container_details.h:162` 定义，确保类型可以安全地存入 `Any` 容器。

## 函数式变换

`Array` 提供了 `Map` 方法（`array.h:612`），支持函数式变换：

```cpp
template <typename F, typename U = std::invoke_result_t<F, T>>
Array<U> Map(F fmap) const {
  return Array<U>(MapHelper(data_, fmap));
}
```

`Map` 同样利用 COW 优化：如果变换函数返回的元素与原元素相同（相同身份），则返回的数组可以共享底层数据，避免不必要的引用计数增减。`MutateByApply`（`array.h:623`）则用于原地修改场景。

## 迭代器

`Array` 的迭代器类型为 `details::IterAdapter<ValueConverter, const Any*>`（`array.h:350`），是一个随机访问迭代器。`ValueConverter`（`array.h:338`）在解引用时将 `const Any&` 转换为 `T`。逆向迭代使用 `ReverseIterAdapter`（`array.h:352`），通过反转底层指针的递增/递减方向实现。

## 设计分析

1. **内联存储 vs 分离存储**：`ArrayObj` 选择内联存储，消除了一次指针解引用和单独的堆分配，提升了缓存局部性。代价是扩容时必须整体复制（无法像 `std::vector` 那样 realloc），但 COW 语义使得扩容只在唯一所有者时发生，共享数组的修改本就需要复制。

2. **COW 的正确性基础**：COW 依赖引用计数的准确性。当 `data_.unique()` 为 true 时，当前句柄是底层对象的唯一所有者，可以安全地原地修改。这一前提由 `ObjectPtr` 的引用计数机制严格保证。

3. **值语义与性能**：`Array` 对外表现为值语义——拷贝是浅拷贝（仅增加引用计数），修改时自动复制。这使得在函数间传递 `Array` 的成本极低，同时避免了意外的别名修改。

4. **初始容量选择**：初始容量 4 是空间与性能的折中。太小会导致频繁扩容，太大则浪费内存。对于 IR 图中的属性列表等常见场景，4 个元素通常足够。

## 相关概念

- [052 List 可变序列容器](052-list-container.md)：对比可变序列容器的不同设计
- [053 SeqBaseObj 序列基类](053-seq-base.md)：Array 和 List 的共同基类
- [060 Tuple 类型化元组](060-tuple-container.md)：基于 ArrayObj 的定长类型化元组
- [061 原地数组存储](061-inplace-array-storage.md)：内联存储机制的深入分析
- [016 TVMFFIAny 16字节布局](/02-core-types/concepts/016-any-16-byte-layout.md)：元素存储的底层载体
