---
type: Concept
title: "视角113：OrderedMap/OrderedSet 保序容器"
description: "解析 tvm::support::OrderedMap 和 OrderedSet 的实现：vector 存储元素保持插入顺序、unordered_map 建立键到索引的 O(1) 查找、显式拷贝构造重建索引、不支持 erase 的设计权衡，以及在 TVM 编译流程中的应用场景。"
tags:
  - cpp-impl
  - ordered-map
  - ordered-set
  - data-structure
  - insertion-order
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-295, F-296
  - code:
    - tvm/src/support/ordered_map.h
    - tvm/src/support/ordered_set.h
---

# 视角113：OrderedMap/OrderedSet 保序容器

## 概述

`tv::support::OrderedMap<K,V>` 和 `tv::support::OrderedSet<T>` 是两个保持插入顺序的关联容器，定义于 `tvm/src/support/ordered_map.h` 和 `tvm/src/support/ordered_set.h`。它们通过组合 `std::vector`（有序存储元素）和 `std::unordered_map`（键到向量索引的哈希映射）实现了"O(1) 查找 + 插入顺序遍历"的双重特性。这两个容器填补了 `std::map`（按 key 排序但 O(log n) 查找）和 `std::unordered_map`（O(1) 查找但无序）之间的空白，在 TVM 编译器中用于需要确定性遍历顺序的场景。

## OrderedMap 实现

### 双存储结构

`OrderedMap`（`ordered_map.h:44-144`）的核心数据成员：

```cpp
std::vector<std::pair<K, V>> elements_;
std::unordered_map<K, size_t, Hash, KeyEqual> elem_to_index_;
```

- **`elements_`**：按插入顺序存储键值对的向量。迭代器直接来自此向量，因此遍历顺序就是插入顺序。
- **`elem_to_index_`**：哈希表，将键映射到 `elements_` 中的位置索引。提供 O(1) 平均时间的查找。

### 插入与访问

`operator[]`（`ordered_map.h:94-102`）实现了类似 `std::map` 的语义：

```cpp
V& operator[](const K& k) {
  auto it = elem_to_index_.find(k);
  if (it != elem_to_index_.end()) {
    return elements_[it->second].second;
  }
  elements_.emplace_back(k, V());
  elem_to_index_[k] = elements_.size() - 1;
  return elements_.back().second;
}
```

键已存在时返回已有值的引用；键不存在时在向量末尾追加新元素并在哈希表中登记索引。

`insert(k, v)`（`ordered_map.h:104-112`）类似但显式传入值，键已存在时更新值而非保留默认值：

```cpp
void insert(const K& k, V v) {
  auto it = elem_to_index_.find(k);
  if (it != elem_to_index_.end()) {
    elements_[it->second].second = std::move(v);
  } else {
    elements_.emplace_back(k, v);
    elem_to_index_[k] = elements_.size() - 1;
  }
}
```

### 查找

`find(k)` 有 const 和非 const 两个重载（`ordered_map.h:78-92`），返回向量迭代器：

```cpp
auto find(const K& k) {
  auto it = elem_to_index_.find(k);
  if (it != elem_to_index_.end()) {
    return elements_.begin() + it->second;
  }
  return elements_.end();
}
```

通过哈希表 O(1) 定位索引，再通过向量随机访问返回迭代器。

### 显式拷贝构造

拷贝构造函数（`ordered_map.h:57-59`）是显式定义的，因为默认拷贝构造会导致问题：

```cpp
OrderedMap(const OrderedMap<K, V, Hash, KeyEqual>& other) : elements_(other.elements_) {
  InitElementToIter();
}
```

注释（`ordered_map.h:50-56`）解释了原因：默认拷贝构造会同时复制 `elements_` 和 `elem_to_index_`，但 `elem_to_index_` 中存储的索引值虽然在副本中仍然正确（因为向量元素位置相同），实际上这里使用的是索引（size_t）而非迭代器，所以默认拷贝其实也是正确的。不过，显式定义确保了语义清晰，并通过 `InitElementToIter()` 重建哈希表。

`InitElementToIter()`（`ordered_map.h:136-140`）遍历向量重建哈希映射：

```cpp
void InitElementToIter() {
  for (size_t i = 0; i < elements_.size(); i++) {
    elem_to_index_[elements_[i].first] = i;
  }
}
```

拷贝赋值运算符（`ordered_map.h:66-68`）使用 copy-and-swap 惯用法：

```cpp
OrderedMap& operator=(const OrderedMap<K, V, Hash, KeyEqual>& other) {
  return *this = OrderedMap(other);
}
```

移动构造和移动赋值使用默认实现。

### 其他操作

- **`clear()`**（`ordered_map.h:114-117`）：同时清空向量和哈希表。
- **`count(k)`**（`ordered_map.h:119`）：返回键是否存在（0 或 1）。
- **`reserve(n)`**（`ordered_map.h:131`）：预分配哈希表桶数，注意只 reserve 了 `elem_to_index_` 而未 reserve `elements_`。
- **`begin()`/`end()`**（`ordered_map.h:122-128`）：直接委托给向量的迭代器。
- **`size()`/`empty()`**：委托给向量。

## OrderedSet 实现

`OrderedSet<T>`（`ordered_set.h:34-97`）是 `OrderedMap` 的简化版本：

```cpp
std::vector<T> elements_;
std::unordered_map<T, size_t, Hash, KeyEqual> elem_to_index_;
```

### 去重插入

`push_back(t)`（`ordered_set.h:67-72`）是核心操作，在追加前检查元素是否已存在：

```cpp
void push_back(const T& t) {
  if (!elem_to_index_.count(t)) {
    elements_.push_back(t);
    elem_to_index_[t] = elements_.size() - 1;
  }
}
```

`insert(t)`（`ordered_set.h:74`）是 `push_back` 的别名，提供与 STL 一致的命名。

### 其余接口

OrderedSet 的拷贝构造、拷贝赋值、`clear()`、`count()`、迭代器和大小方法与 OrderedMap 模式完全一致。它不提供 `operator[]`（集合无值类型）和 `find()`（仅通过 `count()` 判断存在性）。

## 设计约束：不支持 erase

源文件注释（`ordered_map.h:42`）明确说明：

> "we don't support erase since it is less needed and vector backing is more efficient."

不支持删除单个元素是一个有意的设计决策。从向量中间删除元素需要 O(n) 时间移动后续元素，并且需要更新哈希表中所有受影响元素的索引，实现复杂且容易出错。在 TVM 编译器的典型使用场景中（属性映射、参数列表、pass 依赖集合等），容器通常经历"构建→多次遍历→整体销毁"的生命周期，很少需要中途删除。省略 erase 简化了实现并保持了向量存储的缓存友好性。

如果确实需要删除，用户可以调用 `clear()` 清空整个容器，或通过重建容器来过滤元素。

## 模板参数定制

两个容器都接受四个模板参数：

```cpp
template <typename K, typename V, typename Hash = std::hash<K>,
          typename KeyEqual = std::equal_to<K>>
```

`Hash` 和 `KeyEqual` 允许自定义哈希和相等比较函数，与 `std::unordered_map` 的策略一致。这使得容器可以用于不可哈希类型（通过自定义 Hash）或需要特殊相等语义的场景。

## 在 TVM 中的应用场景

OrderedMap 和 OrderedSet 在 TVM 编译器中主要用于：

1. **IR 属性映射**：在 pass 中维护节点到属性的映射，需要确定性的遍历顺序以保证编译结果的可重现性。
2. **参数收集**：收集函数参数、算子属性等，保持声明顺序。
3. **去重序列**：OrderedSet 用于需要去重但保持首次出现顺序的场景，如拓扑排序中的节点收集、依赖分析。
4. **配置字典**：编译器配置选项通常需要保序输出（如生成代码时的参数顺序），OrderedMap 比 `std::map` 更直观（按插入顺序而非字典序）。

## 性能特征

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| `operator[]`/`insert` | O(1) 平均 | 哈希表查找 + 向量追加 |
| `find` | O(1) 平均 | 哈希表查找 + 向量随机访问 |
| `count` | O(1) 平均 | 哈希表查找 |
| 遍历 | O(n) | 向量顺序遍历，缓存友好 |
| `clear` | O(n) | 向量和哈希表各自清空 |
| 拷贝 | O(n) | 向量拷贝 + 哈希表重建 |
| 内存开销 | O(n) + 哈希表开销 | 额外存储一份键和索引 |

与 `std::unordered_map` 相比，OrderedMap 额外存储了一份键的副本（在向量中），内存开销略高，但换来的是保序遍历和更好的缓存局部性。

## 设计分析

OrderedMap/OrderedSet 的实现简洁而实用，是"组合优于继承"和"针对使用场景优化"的典范。它不追求成为一个功能完备的 STL 容器（没有 erase、没有 emplace、没有自定义 allocator），而是聚焦于 TVM 编译器的核心需求：快速查找和确定性顺序遍历。双存储设计的代价是双倍的键存储和更新时的双重维护，但在编译器场景中，容器构建后通常只读遍历，构建时的额外开销可以忽略。显式拷贝构造虽然在当前使用索引（而非迭代器）的实现中不是严格必需的，但体现了对正确性的谨慎态度——如果未来将索引改为迭代器，默认拷贝会导致悬空引用。不支持 erase 的决策体现了"YAGNI"（You Aren't Gonna Need It）原则，避免了复杂且易错的索引维护代码。

## 相关概念

- [054 Map 哈希容器](/04-containers/concepts/054-map-container.md)：FFI 层的对象哈希 Map
- [112 Arena 分配器](112-arena-allocator.md)：可用于 OrderedMap 的批量内存管理
- [051 Array 容器](/04-containers/concepts/051-array-container.md)：FFI 层的保序数组
