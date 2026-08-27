---
type: Concept
title: "视角053：SeqBaseObj 序列基类与 TVMFFISeqCell"
description: "深入剖析 SeqBaseObj 序列容器基类的设计，包括 TVMFFISeqCell C ABI 结构体、元素生命周期管理、插入删除的内存移动语义以及 SeqTypeTraitsBase 类型特征基类。"
tags:
  - containers
  - sequence
  - base-class
  - c-abi
  - memory-management
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-157, F-158
  - code:
    - include/tvm/ffi/container/seq_base.h
    - include/tvm/ffi/c_api.h
---

# 视角053：SeqBaseObj 序列基类与 TVMFFISeqCell

## 概述

`SeqBaseObj` 是 `ArrayObj` 和 `ListObj` 的共同抽象基类，封装了序列容器的核心操作：元素访问、插入、删除、扩容和缩容。它以 `protected` 方式继承 C ABI 结构体 `TVMFFISeqCell`，使子类能够直接操作底层数据指针、大小和容量字段，同时对外提供类型安全的 `const Any&` 访问接口。`SeqBaseObj` 本身对 FFI 类型系统透明（没有类型索引），遵循与 `BytesObjBase` 相同的透明基类模式。

## TVMFFISeqCell C ABI 结构体

`TVMFFISeqCell` 定义在 `include/tvm/ffi/c_api.h:382-407`，是序列容器的 C 兼容数据布局：

```c
struct TVMFFISeqCell {
  void* data;           // 元素数据指针
  int64_t size;         // 已使用元素数量
  int64_t capacity;     // 已分配容量
  void (*data_deleter)(void*);  // 数据释放函数
};
```

四个字段的语义体现了对不同存储策略的统一抽象：

- **data**：指向第一个 `Any` 元素的指针。对于 `ArrayObj`，它指向对象头之后的内联区域；对于 `ListObj`，它指向独立堆分配的缓冲区。
- **size**：当前元素数量，类型为 `int64_t` 以匹配 C ABI 的跨语言一致性。
- **capacity**：已分配的元素容量，决定何时需要扩容。
- **data_deleter**：数据缓冲区的释放函数。当为 `nullptr` 时，表示数据内联在对象分配中（如 `ArrayObj`），随对象一起释放；当非空时，表示数据独立分配（如 `ListObj`），析构时调用该函数释放。

`data_deleter` 的注释（`c_api.h:393-401`）明确说明了这一约定，使得 C ABI 层可以统一处理两种存储布局而无需知道具体子类。

## 元素生命周期管理

`SeqBaseObj` 的构造函数（`seq_base.h:46`）将所有字段初始化为安全默认值：`data = nullptr`、`size = 0`、`capacity = 0`、`data_deleter = nullptr`。

析构函数（`seq_base.h:53`）负责元素的正确销毁：

```cpp
~SeqBaseObj() {
  Any* begin = MutableBegin();
  for (int64_t i = 0; i < TVMFFISeqCell::size; ++i) {
    (begin + i)->Any::~Any();
  }
  if (data_deleter != nullptr) {
    data_deleter(data);
  }
}
```

析构分两步：首先逐元素显式调用 `Any::~Any()` 析构函数（确保持有对象引用的元素正确减少引用计数），然后如果 `data_deleter` 非空则释放数据缓冲区。这种设计确保了无论元素是 POD 类型还是堆对象引用，都能被正确清理。

`clear` 方法（`seq_base.h:114`）从尾部向前析构元素并递减 size，但不释放缓冲区容量：

```cpp
void clear() {
  Any* itr = MutableEnd();
  while (TVMFFISeqCell::size > 0) {
    (--itr)->Any::~Any();
    --TVMFFISeqCell::size;
  }
}
```

## 元素访问

只读访问通过 `at` 和 `operator[]` 提供（`seq_base.h:77,84`），两者都进行边界检查：

```cpp
const Any& operator[](int64_t i) const {
  if (i < 0 || i >= TVMFFISeqCell::size) {
    TVM_FFI_THROW(IndexError) << "Index " << i << " out of bounds " << TVMFFISeqCell::size;
  }
  return static_cast<Any*>(data)[i];
}
```

索引使用 `int64_t` 而非 `size_t`，与 C ABI 保持一致。负索引被拒绝（不支持 Python 风格的负索引），越界访问抛出 `IndexError`。

`front`（`seq_base.h:92`）和 `back`（`seq_base.h:100`）分别返回首尾元素，在空序列上抛出异常。`begin`/`end`（`seq_base.h:108,111`）返回 `const Any*` 指针，支持范围 for 循环遍历。

`SetItem`（`seq_base.h:127`）提供原地元素替换，使用移动语义：

```cpp
void SetItem(int64_t i, Any item) {
  if (i < 0 || i >= TVMFFISeqCell::size) {
    TVM_FFI_THROW(IndexError) << "Index " << i << " out of bounds " << TVMFFISeqCell::size;
  }
  static_cast<Any*>(data)[i] = std::move(item);
}
```

## 插入与删除的内存移动

`insert`（`seq_base.h:175`）在指定位置插入元素，需要将后续元素向右移动：

```cpp
void insert(int64_t idx, Any item) {
  int64_t sz = TVMFFISeqCell::size;
  if (idx < 0 || idx > sz) {
    TVM_FFI_THROW(IndexError) << "Index " << idx << " out of bounds [0, " << sz << "]";
  }
  EnlargeBy(1);
  MoveElementsRight(idx + 1, idx, sz);
  MutableBegin()[idx] = std::move(item);
}
```

`MoveElementsRight`（`seq_base.h:262`）使用 `std::move_backward` 将元素从 `[src_begin, src_end)` 移动到 `dst` 开始的位置，确保重叠区域的正确移动。`erase`（`seq_base.h:146`）则使用 `MoveElementsLeft`（`seq_base.h:257`）调用 `std::move` 将后续元素左移。

范围插入（`seq_base.h:194`）支持从任意迭代器范围批量插入元素，通过 `std::distance` 计算元素数量后一次性扩容和移动。

## 扩容与缩容原语

`SeqBaseObj` 提供了三个受保护的容量管理原语：

- **EmplaceInit**（`seq_base.h:236`）：在指定索引处使用 placement new 构造元素。
- **EnlargeBy**（`seq_base.h:241`）：从尾部开始构造 `delta` 个默认值元素并递增 size。
- **ShrinkBy**（`seq_base.h:249`）：从尾部开始析构 `delta` 个元素并递减 size。

这些原语由子类（`ArrayObj`、`ListObj`）在确保足够容量后调用。子类负责实现具体的容量策略（`ArrayObj` 的 `SwitchContainer` 和 `ListObj` 的 `Reserve`），而 `SeqBaseObj` 专注于元素构造/析构的正确性。

`resize`（`seq_base.h:217`）组合使用这些原语实现大小调整，`Reverse`（`seq_base.h:210`）使用 `std::reverse` 原地反转元素。

## SeqTypeTraitsBase 类型特征

`SeqTypeTraitsBase`（`seq_base.h:278`）是 `Array<T>` 和 `List<T>` 的 `TypeTraits` 特化的 CRTP 基类，提供了序列容器的通用类型检查逻辑：

```cpp
TVM_FFI_INLINE static bool CheckAnyStrict(const TVMFFIAny* src) {
  if (src->type_index != Derived::kPrimaryTypeIndex) return false;
  if constexpr (std::is_same_v<T, Any>) {
    return true;
  } else {
    const SeqBaseObj* n = reinterpret_cast<const SeqBaseObj*>(src->v_obj);
    for (const Any& any_v : *n) {
      if (!details::AnyUnsafe::CheckAnyStrict<T>(any_v)) return false;
    }
    return true;
  }
}
```

该方法首先检查 `type_index` 是否匹配主类型索引（`kTVMFFIArray` 或 `kTVMFFIList`），然后遍历所有元素验证类型一致性。`Derived` 类需提供 `kPrimaryTypeIndex`、`kOtherTypeIndex` 和 `kTypeName` 三个静态常量，支持 Array/List 之间的跨类型转换。

## 设计分析

1. **模板方法模式**：`SeqBaseObj` 定义了序列操作的骨架（元素访问、插入、删除），将容量策略延迟到子类实现。`ArrayObj` 通过 `SwitchContainer` 实现 COW 扩容，`ListObj` 通过 `Reserve` 实现原地扩容，两者复用相同的元素移动逻辑。

2. **C ABI 透明性**：`SeqBaseObj` 以 `protected` 继承 `TVMFFISeqCell`，既暴露了底层字段给子类，又对外部隐藏了 C 结构体细节。`TVMFFISeqCell` 的四字段设计统一了内联存储和堆分配两种布局。

3. **异常安全**：所有批量构造操作都遵循"先构造、后递增 size"的模式（如 `EnlargeBy` 中 `new (itr++) Any(val)` 在 `++size` 之前），确保构造失败时 size 不会反映未初始化的元素。

4. **Any 析构的显式调用**：代码中多处显式调用 `Any::~Any()` 而非 `delete`，因为元素是通过 placement new 在预分配内存中构造的，不能使用 `delete`。这是 C++ 低层容器实现的标准做法。

## 相关概念

- [051 Array 容器与写时复制](051-array-container.md)：SeqBaseObj 的 COW 子类实现
- [052 List 可变序列容器](052-list-container.md)：SeqBaseObj 的可变子类实现
- [016 TVMFFIAny 16字节布局](/02-core-types/concepts/016-any-16-byte-layout.md)：序列元素的底层存储类型
- [061 原地数组存储](061-inplace-array-storage.md)：data_deleter 为 nullptr 的内联存储模式
