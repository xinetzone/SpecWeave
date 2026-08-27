---
type: Concept
title: "视角052：List 可变序列容器"
description: "深入剖析 ListObj/List<T> 可变序列容器的设计，包括独立堆缓冲区分配、原地修改语义、容量预留机制以及与 Array 的 COW 语义对比。"
tags:
  - containers
  - list
  - mutable
  - sequence
  - heap-allocation
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-155, F-156
  - code:
    - include/tvm/ffi/container/list.h
    - include/tvm/ffi/container/seq_base.h
---

# 视角052：List 可变序列容器

## 概述

`List<T>` 是 TVM FFI 中的**可变**序列容器，与 `Array<T>` 的写时复制语义形成互补。`ListObj` 同样继承自 `SeqBaseObj`，但采用**独立堆缓冲区**存储元素数据——对象头与元素数据分离分配。所有修改操作直接在共享的 `ListObj` 上原地执行，所有持有同一 `ListObj` 的句柄都能立即看到变更。这种设计适用于需要频繁就地修改、且多句柄共享变更可见性的场景。

## ListObj 堆缓冲区布局

`ListObj` 定义在 `include/tvm/ffi/container/list.h:46`。其 `Empty` 工厂方法（`list.h:100`）展示了与 `ArrayObj` 的关键差异：

```cpp
static ObjectPtr<ListObj> Empty(int64_t n = kInitSize) {
  if (n < 0) {
    TVM_FFI_THROW(ValueError) << "cannot construct a List of negative size";
  }
  ObjectPtr<ListObj> p = make_object<ListObj>();
  p->TVMFFISeqCell::capacity = n;
  p->TVMFFISeqCell::size = 0;
  p->data = n == 0 ? nullptr : static_cast<void*>(::operator new(sizeof(Any) * n));
  p->data_deleter = RawDataDeleter;
  return p;
}
```

与 `ArrayObj::Empty` 的对比揭示了三个本质差异：

1. **对象分配方式**：`ListObj` 使用 `make_object<ListObj>()`（`list.h:104`），仅分配对象头本身；而 `ArrayObj` 使用 `make_inplace_array_object` 将对象头和元素连续分配。
2. **数据指针来源**：`ListObj` 的 `data` 通过 `::operator new` 独立分配（`list.h:107`），容量为 0 时为 `nullptr`。
3. **释放函数**：`data_deleter` 设置为 `RawDataDeleter`（`list.h:108`），该函数在 `list.h:112` 定义，调用 `::operator delete` 释放缓冲区。对于 `ArrayObj`，此字段为 `nullptr`，表示数据随对象一起释放。

初始容量同样为 `kInitSize = 4`（`list.h:115`），扩展因子 `kIncFactor = 2`（`list.h:117`）。

## 容量预留与原地扩容

`List` 的修改操作通过 `EnsureCapacity`（`list.h:476`）确保有足够空间：

```cpp
ListObj* EnsureCapacity(int64_t reserve_extra) {
  ListObj* p = EnsureListObj();
  if (p->TVMFFISeqCell::capacity >= p->TVMFFISeqCell::size + reserve_extra) {
    return p;
  }
  int64_t cap = p->TVMFFISeqCell::capacity * ListObj::kIncFactor;
  cap = std::max(cap, p->TVMFFISeqCell::size + reserve_extra);
  p->Reserve(cap);
  return p;
}
```

当容量不足时，调用 `ListObj::Reserve`（`list.h:78`）分配新缓冲区并迁移元素：

```cpp
void Reserve(int64_t n) {
  if (n <= TVMFFISeqCell::capacity) return;
  Any* old_data = MutableBegin();
  Any* new_data = static_cast<Any*>(::operator new(sizeof(Any) * static_cast<size_t>(n)));
  for (int64_t i = 0; i < TVMFFISeqCell::size; ++i) {
    new (new_data + i) Any(std::move(old_data[i]));
  }
  for (int64_t j = 0; j < TVMFFISeqCell::size; ++j) {
    (old_data + j)->Any::~Any();
  }
  data_deleter(data);
  data = new_data;
  TVMFFISeqCell::capacity = n;
}
```

`Reserve` 使用 `noexcept` 的 `Any` 移动构造函数迁移元素，注释明确指出这保证了异常安全——移动循环不会抛出异常而留下半构造状态（`list.h:74-76`）。这是独立堆分配相对于内联存储的一个优势：扩容只需分配新缓冲区并移动元素，无需复制整个对象头。

## 原地修改语义

`List` 的修改 API 直接操作底层对象，无 COW 检查：

- `push_back`（`list.h:324`）：调用 `EnsureCapacity(1)` 后在尾部构造元素。
- `Set`（`list.h:439`）：直接调用 `EnsureListObj()->SetItem(i, std::move(value))`，原地替换元素。
- `insert`（`list.h:346`）：调用 `EnsureCapacity(1)->insert(idx, Any(val))`，可能移动后续元素。
- `erase`（`list.h:385`）：直接调用 `GetListObj()->erase(idx)`，不创建副本。
- `pop_back`（`list.h:374`）：直接调用 `GetListObj()->pop_back()`。
- `clear`（`list.h:426`）：直接调用 `GetListObj()->clear()`。

这意味着如果两个 `List<T>` 句柄指向同一个 `ListObj`，一个句柄的修改对另一个立即可见。这与 `Array` 的 COW 行为根本不同。

## 默认构造与空列表

值得注意的是，`List` 的默认构造函数创建容量为 0 的空列表（`list.h:151`）：

```cpp
List() { data_ = ListObj::Empty(0); }
```

而 `Array` 的默认构造函数创建容量为 4 的数组（`array.h:227`）。这一差异反映了两者的使用模式：`Array` 作为不可变值，预分配容量以减少后续 COW 复制；`List` 作为可变容器，按需扩容以避免浪费。

## 引用循环警告

`List` 的头文件注释中明确警告了引用循环风险（`list.h:135-138`）：

> Because List elements are stored as `Any` (which may hold `ObjectRef` pointers), it is possible to create reference cycles (e.g. a List that contains itself). Such cycles will **not** be collected by the reference-counting mechanism alone; avoid them in long-lived data structures.

由于 `List` 是可变的且元素通过 `Any` 存储，一个 `List` 可以包含自身的引用，形成引用循环。引用计数机制无法回收循环引用，可能导致内存泄漏。`Array` 虽然也可能出现类似情况，但 COW 语义使得自引用更难意外形成。

## 设计分析

1. **可变性 vs 不可变性**：`List` 的原地修改语义使其适合作为构建器（builder）和累加器场景，而 `Array` 的 COW 语义适合作为不可变值在函数间安全传递。两者共享 `SeqBaseObj` 基类，但内存管理策略截然不同。

2. **独立堆分配的权衡**：独立缓冲区允许 `Reserve` 高效扩容（仅移动元素，不复制对象头），但引入了额外的堆分配和指针解引用。对于小型列表，`ArrayObj` 的内联存储更紧凑高效。

3. **线程安全**：`List` 不是线程安全的（`list.h:132-133`）。并发读写需要外部同步。这是原地可变性的直接后果——多个线程同时修改同一 `ListObj` 会导致数据竞争。

4. **API 对称性**：`List` 和 `Array` 提供了高度对称的 API（`push_back`、`insert`、`erase`、`Set`、`Map` 等），使得两者可以互换使用，但语义差异需要开发者明确选择。

## 相关概念

- [051 Array 容器与写时复制](051-array-container.md)：不可变 COW 序列容器的对比设计
- [053 SeqBaseObj 序列基类](053-seq-base.md)：Array 和 List 的共同基类
- [028 组合引用计数](/02-core-types/concepts/028-combined-refcount.md)：引用计数与循环引用问题
- [061 原地数组存储](061-inplace-array-storage.md)：内联存储与堆分配的对比分析
