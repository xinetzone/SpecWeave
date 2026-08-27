---
type: Concept
title: "视角063：容器迭代器与 IterAdapter"
description: "深入剖析容器迭代器的设计，包括 IterAdapter 类型转换适配器、ReverseIterAdapter 逆向迭代器、Array 的随机访问迭代器、Map 的双向迭代器以及 DenseMap 的内省迭代器实现。"
tags:
  - containers
  - iterator
  - adapter
  - stl-compatible
  - type-erasure
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-177, F-178
  - code:
    - include/tvm/ffi/container/container_details.h
    - include/tvm/ffi/container/array.h
    - include/tvm/ffi/container/map.h
    - include/tvm/ffi/container/map_base.h
---

# 视角063：容器迭代器与 IterAdapter

## 概述

TVM FFI 容器的迭代器设计遵循 C++ 标准库规范，使得容器可以与 `<algorithm>` 中的算法无缝协作。核心适配器 `IterAdapter` 将底层的 `const Any*` 指针迭代器转换为返回类型化值 `T` 的迭代器；`ReverseIterAdapter` 则反转迭代方向。`Array` 基于这两个适配器提供随机访问迭代器，`Map`/`Dict` 提供双向迭代器，底层 `MapBaseObj::iterator` 是前向迭代器但通过内省链表支持 `--` 操作。所有类型化迭代器在解引用时执行 `Any` 到 `T` 的类型转换，对调用者透明。

## IterAdapter：类型转换适配器

`IterAdapter` 定义在 `include/tvm/ffi/container/container_details.h:46`：

```cpp
template <typename Converter, typename TIter>
class IterAdapter {
 public:
  using difference_type =
      typename std::iterator_traits<TIter>::difference_type;
  using value_type = typename Converter::ResultType;
  using pointer = const typename Converter::ResultType*;
  using reference = const typename Converter::ResultType;
  using iterator_category =
      typename std::iterator_traits<TIter>::iterator_category;

  explicit IterAdapter(TIter iter) : iter_(iter) {}
  IterAdapter& operator++() { ++iter_; return *this; }
  IterAdapter& operator--() { --iter_; return *this; }
  reference operator*() const { return Converter::convert(*iter_); }
  // ...
};
```

设计要点：

1. **双层类型参数**：`Converter` 定义如何从底层迭代器的值类型转换为目标类型；`TIter` 是底层迭代器类型。这种分离使得适配器可以复用不同的转换器和底层迭代器。

2. **迭代器类别透传**：`iterator_category` 直接从 `TIter` 继承。如果底层迭代器是随机访问迭代器（如 `const Any*`），`IterAdapter` 也是随机访问迭代器；如果底层是前向迭代器，适配器也是前向迭代器。

3. **值语义返回**：`reference` 类型为 `const ResultType`（值类型，非引用），`pointer` 为 `const ResultType*`。这是因为解引用时需要执行 `Any` 到 `T` 的转换，转换结果是临时值，不能返回引用。这也是 `Map::iterator::operator->` 被删除的原因。

4. **算术运算支持**：当底层迭代器支持随机访问时，`IterAdapter` 提供 `+`、`-`、`+=`、`-=` 和 `operator-(const IterAdapter&)` 等运算，通过 SFINAE 约束仅在 `random_access_iterator_tag` 时启用差值运算（`container_details.h:88-93`）。

## ReverseIterAdapter：逆向迭代器

`ReverseIterAdapter` 定义在 `container_details.h:109`，通过反转底层迭代器的递增/递减方向实现逆向遍历：

```cpp
ReverseIterAdapter& operator++() { --iter_; return *this; }
ReverseIterAdapter& operator--() { ++iter_; return *this; }
ReverseIterAdapter operator+(difference_type offset) const {
  return ReverseIterAdapter(iter_ - offset);
}
```

`++` 对应底层 `--`，`+offset` 对应底层 `-offset`。`rbegin()` 返回 `end() - 1`，`rend()` 返回 `begin() - 1`（`array.h:361-369`），这是因为逆向迭代器需要"越过"起始位置一个元素才能正确表示范围边界。

## Array 的迭代器

`Array<T>` 定义了两个迭代器类型别名（`array.h:350-352`）：

```cpp
using iterator = details::IterAdapter<ValueConverter, const Any*>;
using reverse_iterator =
    details::ReverseIterAdapter<ValueConverter, const Any*>;
```

`ValueConverter`（`array.h:338`）定义转换逻辑：

```cpp
struct ValueConverter {
  using ResultType = T;
  static T convert(const Any& val) {
    return details::AnyUnsafe::CopyFromAnyViewAfterCheck<T>(val);
  }
};
```

由于底层迭代器是 `const Any*`（随机访问迭代器），`Array::iterator` 自动获得随机访问能力，支持 `it + n`、`it - n`、`it[n]`、`it1 - it2` 等全部随机访问操作。这使得 `Array` 可以与 `std::sort`、`std::binary_search` 等需要随机访问迭代器的算法配合使用。

`begin()` 和 `end()`（`array.h:355-358`）直接从 `ArrayObj` 获取 `const Any*` 指针并包装：

```cpp
iterator begin() const { return iterator(GetArrayObj()->begin()); }
iterator end() const { return iterator(GetArrayObj()->end()); }
```

`ArrayObj::begin()` 返回 `static_cast<Any*>(data)`（`seq_base.h:108`），即数据缓冲区的起始指针。

## Map 的双向迭代器

`Map<K,V>::iterator`（`map.h:286`）是一个双向迭代器：

```cpp
class iterator {
 public:
  using iterator_category = std::bidirectional_iterator_tag;
  using value_type = const std::pair<K, V>;
  // ...
  reference operator*() const {
    auto& kv = *itr;
    return std::make_pair(
        details::AnyUnsafe::CopyFromAnyViewAfterCheck<K>(kv.first),
        details::AnyUnsafe::CopyFromAnyViewAfterCheck<V>(kv.second));
  }
  iterator& operator++() { ++itr; return *this; }
  iterator& operator--() { --itr; return *this; }
};
```

它包装了 `MapObj::iterator`（即 `MapBaseObj::iterator`），在解引用时将 `Any` 键值对转换为类型化的 `std::pair<K, V>`。`operator->` 被删除（`map.h:301`），因为返回的是值类型而非引用，取地址无意义。

## MapBaseObj 的前向迭代器

底层 `MapBaseObj::iterator`（`map_base.h:127`）声明为 `forward_iterator_tag`，但实际支持 `--` 操作（`map_base.h:157`）：

```cpp
class iterator {
 public:
  using iterator_category = std::forward_iterator_tag;
  // ...
  iterator& operator++();
  iterator& operator--();
};
```

这种设计反映了实现的微妙之处：虽然迭代器在技术上可以双向移动（通过内省插入顺序的双向链表），但标记为前向迭代器是因为 `--` 的性能不如 `++`（可能需要反向遍历链表），且标准库算法通常不要求哈希表迭代器支持双向访问。`Map<K,V>::iterator` 将其提升为 `bidirectional_iterator_tag`，因为它确实支持双向操作。

迭代器内部包含 `index`（槽位索引）和 `self`（容器指针），在 debug 模式下还包含 `state_marker`（`map_base.h:175`）用于检测迭代器失效。`operator++` 根据当前存储类型（小表线性遍历或稠密表沿 next 指针遍历）前进到下一个有效条目。

## 迭代器失效

迭代器失效规则因容器而异：

- **Array COW**：`Array` 的修改操作可能触发 COW 复制，使旧迭代器指向旧容器。但由于 COW 后旧容器仍然存在（引用计数），旧迭代器在技术上仍可解引用，但遍历的是修改前的数据。
- **List**：原地修改，`erase` 使被删除元素的迭代器失效，`insert`/`push_back` 可能导致缓冲区重新分配，使所有迭代器失效。
- **Map COW**：与 Array 类似，COW 后旧迭代器指向旧容器。
- **Dict**：原地修改，`InsertMaybeReHash` 可能触发 rehash 或存储切换，使所有迭代器失效。

## 设计分析

1. **STL 兼容性**：迭代器完全遵循 C++ 迭代器规范（定义 `iterator_category`、`value_type`、`difference_type`、`pointer`、`reference`），使得容器可以直接用于 range-for 循环和标准算法。这是容器设计的基本要求。

2. **适配器模式的优雅性**：`IterAdapter` 将"遍历"和"类型转换"两个关注点分离。底层迭代器负责在 `Any` 数组中移动，适配器负责在解引用时转换类型。新增容器只需提供底层迭代器和转换器，无需重复实现迭代器算术。

3. **值返回的必然性**：由于元素以类型擦除的 `Any` 存储，类型化访问必须执行转换，转换结果是临时值。因此迭代器不能返回引用，这是类型擦除容器的固有约束。这也意味着通过迭代器修改元素需要通过容器的 `Set` 方法而非 `*it = value`。

4. **迭代器标签的诚实性**：`MapBaseObj::iterator` 标记为 `forward_iterator_tag` 而非 `bidirectional_iterator_tag`，即使它支持 `--`。这种诚实的标签反映了实际的性能特征，避免算法假设 O(1) 的双向移动。

## 相关概念

- [051 Array 容器与写时复制](051-array-container.md)：Array 的随机访问迭代器
- [054 Map 不可变哈希映射](054-map-container.md)：Map 的双向迭代器
- [056 MapBaseObj 与稠密哈希表](056-map-base-dense-hash.md)：底层迭代器的遍历机制
- [064 容器类型特征与类型包容](064-container-type-traits.md)：迭代器值类型的类型检查
