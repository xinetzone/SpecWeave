---
type: Concept
title: "视角054：Map 不可变哈希映射"
description: "深入剖析 MapObj/Map<K,V> 哈希映射容器的设计，包括写时复制语义、基于 DenseMap 的开放寻址哈希表、类型化键值访问、双向迭代器以及与 Dict 的语义对比。"
tags:
  - containers
  - map
  - hash-map
  - copy-on-write
  - open-addressing
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-159, F-160
  - code:
    - include/tvm/ffi/container/map.h
    - include/tvm/ffi/container/map_base.h
---

# 视角054：Map 不可变哈希映射

## 概述

`Map<K, V>` 是 TVM FFI 中的不可变哈希映射容器，底层对象 `MapObj` 继承自 `MapBaseObj`。与 `Array` 类似，`Map` 实现了写时复制语义：修改操作在共享状态下透明地创建底层哈希表的浅拷贝。`Map` 的底层哈希引擎采用高性能的开放寻址设计——`DenseMapBaseObj`，结合 Fibonacci 哈希、1 字节元数据和数据分块技术，在缓存局部性和内存占用上显著优于传统的拉链法哈希表。

## MapObj 与 COW 语义

`MapObj` 定义在 `include/tvm/ffi/container/map.h:39`，是一个轻量级类，仅添加了 `ShallowCopy` 静态方法和类型索引声明：

```cpp
class MapObj : public MapBaseObj {
 public:
  static ObjectPtr<Object> ShallowCopy(const MapObj* src) {
    return MapBaseObj::CopyFrom<MapObj>(const_cast<MapObj*>(src));
  }
  static constexpr const int32_t _type_index = TypeIndex::kTVMFFIMap;
  // ...
};
```

`Map<K,V>` 的 COW 逻辑在 `CopyOnWrite` 方法中（`map.h:271`）：

```cpp
MapObj* CopyOnWrite() {
  if (data_.get() == nullptr) {
    data_ = MapObj::Empty<MapObj>();
  } else if (!data_.unique()) {
    data_ = MapObj::CopyFrom<MapObj>(GetMapObj());
  }
  return GetMapObj();
}
```

与 `Array::CopyOnWrite` 类似，当引用计数大于 1 时，调用 `MapObj::ShallowCopy` 创建底层哈希表的浅拷贝。`ShallowCopy` 复制哈希表结构和键值对的 `Any` 表示（浅拷贝 `Any`，对对象引用仅增加引用计数），保持迭代顺序不变。

## 键值访问

`Map` 提供类型安全的键值访问 API：

- **at**（`map.h:201`）：按键查找值，不存在时抛出异常。返回 `V` 的拷贝，通过 `CopyFromAnyViewAfterCheck<V>` 进行类型转换。
- **operator[]**（`map.h:209`）：等同于 `at`，仅提供 const 访问。
- **find**（`map.h:247`）：返回迭代器，未找到时返回 `end()`。
- **count**（`map.h:216`）：返回键的存在次数（0 或 1）。
- **Get**（`map.h:249`）：返回 `std::optional<V>`，未找到时返回 `std::nullopt`，避免异常开销。

`Set` 方法（`map.h:234`）执行写时复制后插入键值对：

```cpp
void Set(const K& key, const V& value) {
  CopyOnWrite();
  ObjectPtr<Object> new_data =
      MapObj::InsertMaybeReHash<MapObj>(MapObj::KVType(key, value), data_);
  if (new_data != nullptr) {
    data_ = std::move(new_data);
  }
}
```

`InsertMaybeReHash` 是 `MapBaseObj` 提供的静态方法，处理插入和可能的 rehash。当插入触发从小表到稠密表的升级或容量扩展时，返回新容器指针；否则返回 `nullptr` 表示原地插入成功。

`erase`（`map.h:261`）同样先执行 COW，再删除键。`clear`（`map.h:223`）通过替换为空 `MapObj` 实现，不直接清空底层数据。

## 双向迭代器

`Map::iterator`（`map.h:286`）是一个双向迭代器（`bidirectional_iterator_tag`），解引用返回 `const std::pair<K, V>`（值类型，非引用）：

```cpp
reference operator*() const {
  auto& kv = *itr;
  return std::make_pair(details::AnyUnsafe::CopyFromAnyViewAfterCheck<K>(kv.first),
                        details::AnyUnsafe::CopyFromAnyViewAfterCheck<V>(kv.second));
}
```

由于返回的是值对而非引用，`operator->` 被显式删除（`map.h:301`），防止用户通过指针修改元素。迭代器支持前缀/后缀的 `++` 和 `--`，底层委托给 `MapBaseObj::iterator`。

底层的 `MapBaseObj::iterator`（`map_base.h:127`）是前向迭代器，但通过内省链表结构也支持 `--` 操作。它包含 `index`（槽位索引）和 `self`（容器指针），在 debug 模式下还包含 `state_marker` 用于检测迭代器失效。

## Merge 函数

`Merge`（`map.h:360`）是一个自由函数，将两个 `Map` 合并：

```cpp
inline Map<K, V> Merge(Map<K, V> lhs, const Map<K, V>& rhs) {
  for (const auto& p : rhs) {
    lhs.Set(p.first, p.second);
  }
  return std::move(lhs);
}
```

注意 `lhs` 按值传递，函数内部的 `Set` 操作在必要时触发 COW，原始 Map 不受影响。

## 类型特征

`TypeTraits<Map<K, V>>`（`map.h:372`）继承自 `MapTypeTraitsBase`，声明：
- `kPrimaryTypeIndex = TypeIndex::kTVMFFIMap`
- `kOtherTypeIndex = TypeIndex::kTVMFFIDict`

这意味着 `Map<K,V>` 可以从 `Dict` 类型的 `Any` 值构造（在元素类型兼容时），但反之不成立。`type_subsumes_v` 特化（`map.h:390`）定义了 Map 之间的类型包容关系：`Map<K,V>` 包容 `Map<KU,VU>` 当且仅当 `K` 包容 `KU` 且 `V` 包容 `VU`。

## 设计分析

1. **不可变语义与 COW**：`Map` 的 COW 语义使其适合作为 DSL 图中的属性字典——在编译优化过程中频繁传递和浅拷贝，仅在实际修改时付出复制代价。这与 `Array` 的设计哲学一致。

2. **浅拷贝的效率**：`ShallowCopy` 复制哈希表元数据和槽位数组，但键值对以 `Any` 方式浅拷贝（对象引用仅增加引用计数）。这意味着即使 COW 触发，复制成本也主要是哈希表结构而非深拷贝元素。

3. **开放寻址 vs 拉链法**：底层 `DenseMapBaseObj` 采用开放寻址而非拉链法，消除了每个条目的链表指针开销（传统设计每个键值对需要额外 16 字节的 next/prev 指针），并通过数据分块提升缓存局部性。详细的哈希表设计见视角056。

4. **迭代顺序**：`Map` 保持插入顺序（通过内省隐式链表），这在需要确定性遍历的场景（如代码生成、序列化）中非常重要。

## 相关概念

- [055 Dict 可变字典容器](055-dict-container.md)：Map 的可变对应物
- [056 MapBaseObj 与稠密哈希表](056-map-base-dense-hash.md)：底层哈希引擎的深入分析
- [051 Array 容器与写时复制](051-array-container.md)：COW 语义的序列容器对应
- [063 容器迭代器与 IterAdapter](063-container-iterators.md)：迭代器适配机制
