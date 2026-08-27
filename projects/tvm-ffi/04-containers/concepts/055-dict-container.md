---
type: Concept
title: "视角055：Dict 可变字典容器"
description: "深入剖析 DictObj/Dict<K,V> 可变字典容器的设计，包括原地修改语义、InplaceSwitchTo 存储切换机制、与 Map 的内存布局等价性保证以及共享引用的变更可见性。"
tags:
  - containers
  - dict
  - mutable
  - hash-map
  - inplace-switch
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-161, F-162
  - code:
    - include/tvm/ffi/container/dict.h
    - include/tvm/ffi/container/map_base.h
---

# 视角055：Dict 可变字典容器

## 概述

`Dict<K, V>` 是 TVM FFI 中的**可变**哈希映射容器，与 `Map<K, V>` 的写时复制语义形成互补。其底层对象 `DictObj` 同样继承自 `MapBaseObj`，共享相同的高性能哈希引擎。但 `Dict` 的所有修改操作直接在共享的 `DictObj` 上原地执行——当多个句柄引用同一字典时，一个句柄的修改对其他句柄立即可见。`Dict` 特别引入了 `InplaceSwitchTo` 机制，使得从小表到稠密表的存储升级可以在不改变对象地址的情况下原地完成，这是可变语义下的关键设计。

## DictObj 与布局等价保证

`DictObj` 定义在 `include/tvm/ffi/container/dict.h:41`，与 `MapObj` 一样是轻量级类：

```cpp
class DictObj : public MapBaseObj {
 public:
  static ObjectPtr<Object> ShallowCopy(const DictObj* src) {
    return MapBaseObj::CopyFrom<DictObj>(const_cast<DictObj*>(src));
  }
  static constexpr const int32_t _type_index = TypeIndex::kTVMFFIDict;
  // ...
};
```

紧接着是一个关键的静态断言（`dict.h:63`）：

```cpp
static_assert(sizeof(DictObj) == sizeof(MapBaseObj),
              "DictObj must match MapBaseObj layout");
```

这一断言确保 `DictObj` 不引入任何额外字段，其内存布局与 `MapBaseObj` 完全一致。这不是巧合——`Dict` 在修改时需要原地切换底层存储（从小表升级到稠密表，或 rehash 到更大容量），而原地切换要求新存储可以覆盖旧存储的内存位置。只有当 `DictObj` 的大小等于基类 `MapBaseObj` 时，`SmallMapBaseObj` 预分配的内联空间才能容纳 `DenseMapBaseObj` 的头部。

`MapObj` 同样满足这一约束，但 `Map` 的 COW 语义使其在修改时创建新对象而非原地切换。

## InplaceSwitchTo 存储切换

`Dict::Set` 方法（`dict.h:240`）展示了可变语义下的存储切换：

```cpp
void Set(const K& key, const V& value) {
  EnsureDictObj();
  ObjectPtr<Object> new_container =
      MapBaseObj::InsertMaybeReHash<DictObj>(DictObj::KVType(key, value), data_);
  if (new_container != nullptr) {
    static_cast<MapBaseObj*>(data_.get())->InplaceSwitchTo(std::move(new_container));
  }
}
```

当 `InsertMaybeReHash` 返回非空指针时，表示插入操作触发了存储变更（从小表升级为稠密表，或 rehash 到新容量）。此时调用 `InplaceSwitchTo`（`map_base.h:205`）将新存储的内容**原地搬移**到当前对象的内存位置：

- 当前 `DictObj` 的内存空间在初始分配时已预留足够大小（`SmallMapBaseObj::Empty` 中通过 `make_inplace_array_object` 分配了足以容纳 `DenseMapBaseObj` 的空间）。
- `InplaceSwitchTo` 将新容器的数据复制到当前对象的地址，并重置新容器（使其变为空壳），最终当前对象的类型标记从小表变为稠密表。
- 所有指向该 `DictObj` 的指针/引用仍然有效，因为对象地址未改变。

这与 `Map::Set` 形成对比——`Map` 在 rehash 时直接替换 `data_` 指针为新对象，旧对象在引用计数归零时释放。

## 原地修改 API

`Dict` 的修改 API 均直接操作底层对象，无 COW 检查：

- **Set**（`dict.h:240`）：原地插入或更新键值对，必要时触发存储切换。
- **erase**（`dict.h:267`）：直接调用 `n->erase(key)`，原地删除。
- **clear**（`dict.h:229`）：直接调用 `n->clear()`，原地清空所有条目。

读取 API 与 `Map` 对称：`at`（`dict.h:207`）、`operator[]`（`dict.h:215`）、`find`（`dict.h:253`）、`count`（`dict.h:222`）、`Get`（`dict.h:255`）提供类型安全的键值访问。

`Dict::iterator`（`dict.h:281`）也是双向迭代器，与 `Map::iterator` 结构相同，解引用返回 `const std::pair<K, V>` 值类型，`operator->` 被删除。

## EnsureDictObj 惰性初始化

与 `List` 类似，`Dict` 的默认构造函数创建空字典，但修改操作通过 `EnsureDictObj` 确保底层对象存在：

```cpp
void Set(const K& key, const V& value) {
  EnsureDictObj();
  // ...
}
```

这确保了即使 `Dict` 处于空状态（`data_ == nullptr`），首次修改也能正确初始化底层存储。`Map` 的默认构造函数则直接分配空的 `MapObj`（`map.h:88`），因为 `Map` 的不可变语义要求对象始终存在。

## 类型特征

`TypeTraits<Dict<K, V>>`（`dict.h:358`）继承自 `MapTypeTraitsBase`，声明：
- `kPrimaryTypeIndex = TypeIndex::kTVMFFIDict`
- `kOtherTypeIndex = TypeIndex::kTVMFFIMap`

注意方向与 `Map` 相反：`Dict` 接受 `Map` 作为备选类型，但 `Map` 不接受 `Dict`。这是因为 `Dict` 的可变性强于 `Map`——从不可变 `Map` 转为可变 `Dict` 是安全的（获得更多能力），而从 `Dict` 转为 `Map` 可能导致意外的共享可变性。

`type_subsumes_v` 对 `Dict` 同样适用，支持元素类型兼容的字典之间的转换。

## 设计分析

1. **原地切换的精妙设计**：`InplaceSwitchTo` 是 `Dict` 可变语义的核心技术。它要求初始分配时预留足够空间（`SmallMapBaseObj::Empty` 中 `sizeof(SmallMapBaseObj) + kInitSize * sizeof(KVType) >= sizeof(DenseMapBaseObj)` 的静态断言保证了这一点），使得后续存储升级不需要移动对象地址。这对于持有 `DictObj*` 裸指针的场景（如 C ABI 遍历）至关重要。

2. **可变 vs 不可变的选择**：`Dict` 适合作为需要频繁增删的构建期数据结构，而 `Map` 适合作为构建完成后的不可变快照。两者共享哈希引擎，但修改策略不同。开发者应根据是否需要共享变更可见性来选择。

3. **布局等价的工程意义**：`sizeof(DictObj) == sizeof(MapBaseObj)` 的断言不仅是为了原地切换，也意味着 `MapObj` 和 `DictObj` 在二进制层面可以互换解释（仅类型索引不同）。这为跨语言运行时的类型转换提供了基础。

4. **共享可变性风险**：与 `List` 一样，`Dict` 不是线程安全的，且可能产生引用循环（字典的值包含自身引用）。在多线程环境中使用需要外部同步。

## 相关概念

- [054 Map 不可变哈希映射](054-map-container.md)：Dict 的不可变对应物
- [056 MapBaseObj 与稠密哈希表](056-map-base-dense-hash.md)：共享的哈希引擎设计
- [052 List 可变序列容器](052-list-container.md)：可变容器的语义类比
- [062 Variant 类型安全变体](062-variant-container.md)：类型安全的联合体
