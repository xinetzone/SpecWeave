---
type: Concept
title: "视角056：MapBaseObj 与稠密哈希表"
description: "深入剖析 MapBaseObj 哈希表内核的设计，包括 SmallMapBaseObj 小表内联存储、DenseMapBaseObj 开放寻址哈希、Fibonacci 哈希、1字节元数据隐式链表以及数据分块布局。"
tags:
  - containers
  - hash-map
  - open-addressing
  - dense-map
  - fibonacci-hash
  - inplace-storage
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-163, F-164
  - code:
    - include/tvm/ffi/container/map_base.h
---

# 视角056：MapBaseObj 与稠密哈希表

## 概述

`MapBaseObj` 是 `MapObj` 和 `DictObj` 的共同基类，定义了哈希映射容器的核心抽象。其真正的哈希引擎由两个内部实现类提供：`SmallMapBaseObj`（小规模内联哈希表，最多 4 个元素）和 `DenseMapBaseObj`（大规模开放寻址哈希表）。`DenseMapBaseObj` 采用了一系列高性能哈希表技术——Fibonacci 哈希、1 字节元数据隐式链表、数据分块和二次探测，在缓存局部性、内存占用和查找性能上显著优于传统的拉链法哈希表。本视角深入剖析这一双层设计。

## MapBaseObj 抽象层

`MapBaseObj` 定义在 `include/tvm/ffi/container/map_base.h:56`，声明了哈希映射的统一接口：

```cpp
class MapBaseObj : public Object {
 public:
  using key_type = Any;
  using mapped_type = Any;
  using KVType = std::pair<Any, Any>;
  // ...
  size_t size() const { return size_; }
  size_t count(const key_type& key) const;
  const mapped_type& at(const key_type& key) const;
  mapped_type& at(const key_type& key);
  iterator begin() const;
  iterator end() const;
  iterator find(const key_type& key) const;
  void erase(const iterator& position);
  void erase(const key_type& key) { erase(find(key)); }
  void clear();
};
```

键和值均为 `Any` 类型，`KVType` 即 `std::pair<Any, Any>`，大小为 32 字节（`map_base.h:75` 的静态断言保证）。受保护字段包括 `data_`（数据指针）、`size_`（条目数）、`slots_`（槽位数，最高位用作小表标记）和 `data_deleter_`。

`slots_` 的最高位通过 `kSmallTagMask`（`map_base.h:255`）区分当前存储是小表还是稠密表，`IsSmallMap()`（`map_base.h:260`）方法检测此标记。

## SmallMapBaseObj：内联小表

`SmallMapBaseObj` 定义在 `map_base.h:1097`，初始容量 `kInitSize = 2`，最大容量 `kMaxSize = 4`。它将键值对直接内联存储在对象之后：

```cpp
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

关键设计点：

1. **内联分配**：通过 `make_inplace_array_object` 将对象头和 `KVType` 数组连续分配，`data_` 指向对象头之后（`map_base.h:1314`）。
2. **预留升级空间**：静态断言确保分配大小足以容纳 `DenseMapBaseObj` 头部（`map_base.h:1308`），为后续原地升级到稠密表预留空间。
3. **线性查找**：小表使用简单的线性扫描（`find` 遍历前 `size_` 个元素），对于 ≤4 个元素，线性扫描的常数因子小于哈希计算，且数据在缓存中连续。
4. **类型标记**：`SetSlotsAndSmallLayoutTag` 设置 `kSmallTagMask` 位，标识当前为小表布局。

## DenseMapBaseObj：开放寻址稠密哈希

当元素数量超过小表容量时，存储升级为 `DenseMapBaseObj`（`map_base.h:335`）。其设计文档注释（`map_base.h:277-334`）详细描述了三大创新：

### A1. 隐式链表

不同于传统拉链法为每个桶维护显式链表指针，`DenseMapBaseObj` 将所有数据存储在单个数组中，通过元数据中的 7 位"跳转偏移"隐式链接同义词。这消除了每个条目 16 字节的 next/prev 指针开销。

### A2. 1 字节元数据

每个槽位仅 1 字节元数据（`map_base.h:290-301`），分为三部分：
- **保留码**：`0b11111111`（255）表示空槽（`kEmptySlot`），`0b11111110`（254）表示保护槽（`kProtectedSlot`，空但不可写入）。
- **链表头标记**：最高位为 0 表示该槽是链表头。
- **跳转偏移**：低 7 位存储到下一个同义词的偏移索引（126 个预定义候选值之一）。低 7 位全 0 表示链表末尾。

### A3. 数据分块

每 16 个元素组成一个 Block（`map_base.h:361`），16 字节元数据在前，后跟 16 个 `ItemType`（键值对加 prev/next 索引）：

```cpp
struct Block {
  uint8_t bytes[kBlockCap + kBlockCap * sizeof(ItemType)];
};
```

`ItemType`（`map_base.h:352`）包含 `KVType data` 和 `uint64_t prev/next`，用于维护插入顺序的双向链表。`kBlockCap = 16`（`map_base.h:338`）使得元数据和数据在缓存行中良好对齐。

### B1. Fibonacci 哈希

表大小为 2 的幂，使用 Fibonacci 哈希将哈希值映射到槽位（`map_base.h:940`）：

```cpp
static uint64_t FibHash(uint64_t hash_value, uint32_t fib_shift) {
  constexpr uint64_t coeff = 11400714819323198485ull;
  return (coeff * hash_value) >> fib_shift;
}
```

黄金比例乘数 `11400714819323198485`（即 2^64 / φ）确保哈希值在 2 的幂大小的表中均匀分布，避免了取模运算。

### B2. 链表遍历

查找时，先通过 Fibonacci 哈希定位链表头槽位，若该槽位的元数据指示它是链表头（最高位为 0），则沿跳转偏移遍历同义词链；否则该桶为空。跳转偏移使用三角形数探测序列（`map_base.h:326-329`），数学上可证明能遍历整个 2 的幂大小的表。

### B4. 最大负载因子

`kMaxLoadFactor = 0.99`（`map_base.h:340`），远高于传统哈希表的 0.7。这得益于开放寻址和高效的探测策略，允许表几乎填满而性能不显著下降，大幅提升了内存利用率。

## 存储升级流程

当 `InsertMaybeReHash` 检测到小表容量不足时：
1. 分配新的 `DenseMapBaseObj`（利用小表预留的空间原地构造）。
2. 将小表中的键值对重新哈希到稠密表中。
3. 对 `Dict`，通过 `InplaceSwitchTo` 原地切换；对 `Map`，通过 COW 创建新对象。

`CalcTableSize`（`map_base.h:917`）计算 2 的幂表大小和 Fibonacci 移位量，确保槽位数严格大于所需容量。

## 设计分析

1. **双层策略的工程智慧**：小表（≤4 元素）使用线性扫描，避免了哈希计算和元数据开销；大表自动升级到稠密哈希。这种渐进式策略使得常见的小规模映射（如属性字典）零开销，而大规模映射仍有 O(1) 性能。

2. **缓存局部性优化**：数据分块将元数据和键值对组织在连续内存中，一次缓存行加载可获取多个条目的元数据。隐式链表避免了指针追踪，同义词在数组中物理邻近。

3. **内存效率**：1 字节元数据 + 32 字节键值对 + 16 字节 prev/next = 每条约 49 字节，而拉链法通常需要额外 16 字节链表指针。0.99 的负载因子进一步减少了空间浪费。

4. **迭代顺序**：通过 `ItemType` 中的 prev/next 维护插入顺序的双向链表，使得遍历顺序确定。这对于序列化、代码生成和调试输出非常重要。

## 相关概念

- [054 Map 不可变哈希映射](054-map-container.md)：基于 MapBaseObj 的 COW 容器
- [055 Dict 可变字典容器](055-dict-container.md)：基于 MapBaseObj 的可变容器
- [061 原地数组存储](061-inplace-array-storage.md)：SmallMapBaseObj 的内联分配机制
- [063 容器迭代器与 IterAdapter](063-container-iterators.md)：哈希表迭代器实现
