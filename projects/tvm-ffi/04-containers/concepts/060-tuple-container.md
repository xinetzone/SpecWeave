---
type: Concept
title: "视角060：Tuple 类型化元组"
description: "深入剖析 Tuple<Types...> 变长类型化元组的设计，包括基于 ArrayObj 的固定容量存储、编译期索引访问 get<I>、写时复制 Set<I>、std::tuple 互操作以及类型特征验证。"
tags:
  - containers
  - tuple
  - variadic
  - type-safe
  - copy-on-write
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-171, F-172
  - code:
    - include/tvm/ffi/container/tuple.h
    - include/tvm/ffi/container/array.h
---

# 视角060：Tuple 类型化元组

## 概述

`Tuple<Types...>` 是 TVM FFI 中的变长类型化元组容器，结合了 `std::tuple` 的编译期类型安全和 `ArrayObj` 的引用计数存储。与 `Array<T>` 存储同类型元素不同，`Tuple` 的每个位置可以有不同的类型，类型在编译期确定。其底层复用 `ArrayObj` 作为存储引擎，容量固定为 `sizeof...(Types)`，实现了写时复制语义。`Tuple` 与 `std::tuple` 互操作，特化了 `std::tuple_size` 和 `std::tuple_element`，支持结构化绑定和 ADL `get`。

## 基于 ArrayObj 的固定容量存储

`Tuple` 定义在 `include/tvm/ffi/container/tuple.h:46`，继承自 `ObjectRef`：

```cpp
template <typename... Types>
class Tuple : public ObjectRef {
  // ...
  using ContainerType = ArrayObj;
};
```

底层对象类型为 `ArrayObj`（`tuple.h:194`），与 `Array<T>` 共享相同的存储引擎。但关键区别在于：`Tuple` 的容量在构造时固定为 `sizeof...(Types)`，不支持动态增删元素。

默认构造通过 `MakeDefaultTupleNode`（`tuple.h:199`）实现：

```cpp
static ObjectPtr<ArrayObj> MakeDefaultTupleNode() {
  ObjectPtr<ArrayObj> p = ArrayObj::Empty(sizeof...(Types));
  Any* itr = p->MutableBegin();
  ((new (itr++) Any(Types()), p->TVMFFISeqCell::size++), ...);
  return p;
}
```

该方法创建容量恰好为元素个数的 `ArrayObj`，使用折叠表达式逐位置默认构造每个元素。size 在每个元素构造成功后递增，保证异常安全。

参数化构造通过 `MakeTupleNode`（`tuple.h:208`）实现，从传入参数构造每个位置的元素：

```cpp
template <typename... UTypes>
static ObjectPtr<ArrayObj> MakeTupleNode(UTypes&&... args) {
  ObjectPtr<ArrayObj> p = ArrayObj::Empty(sizeof...(Types));
  Any* itr = p->MutableBegin();
  ((new (itr++) Any(Types(std::forward<UTypes>(args))),
    p->TVMFFISeqCell::size++), ...);
  return p;
}
```

## 编译期索引访问

`Tuple` 提供模板方法 `get<I>()` 进行编译期索引访问（`tuple.h:146`）：

```cpp
template <size_t I>
auto get() const& {
  static_assert(I < sizeof...(Types), "Tuple index out of bounds");
  using ReturnType = std::tuple_element_t<I, std::tuple<Types...>>;
  const Any* ptr = GetArrayObj()->begin() + I;
  return details::AnyUnsafe::CopyFromAnyViewAfterCheck<ReturnType>(*ptr);
}
```

`static_assert` 在编译期检查索引越界。返回类型通过 `std::tuple_element_t` 推导，确保类型精确匹配。const 左值重载返回拷贝（通过 `CopyFromAnyViewAfterCheck`）。

右值重载（`tuple.h:161`）支持移动语义：

```cpp
template <size_t I>
auto get() && {
  if (!this->unique()) {
    return std::as_const(*this).template get<I>();
  }
  using ReturnType = std::tuple_element_t<I, std::tuple<Types...>>;
  Any* ptr = GetArrayObj()->MutableBegin() + I;
  return details::AnyUnsafe::MoveFromAnyAfterCheck<ReturnType>(
      std::move(*ptr));
}
```

当 `Tuple` 是底层 `ArrayObj` 的唯一所有者时，直接从存储中移动元素，避免拷贝；否则回退到 const 拷贝路径。

## 写时复制 Set

`Set<I>` 方法（`tuple.h:185`）修改指定位置的元素：

```cpp
template <size_t I, typename U>
void Set(U&& item) {
  static_assert(I < sizeof...(Types), "Tuple index out of bounds");
  using T = std::tuple_element_t<I, std::tuple<Types...>>;
  this->CopyIfNotUnique();
  Any* ptr = GetArrayObj()->MutableBegin() + I;
  *ptr = T(std::forward<U>(item));
}
```

`CopyIfNotUnique`（`tuple.h:217`）实现 COW 逻辑：

```cpp
void CopyIfNotUnique() {
  if (!data_.unique()) {
    ObjectPtr<ArrayObj> p = ArrayObj::Empty(sizeof...(Types));
    Any* itr = p->MutableBegin();
    const Any* read = GetArrayObj()->begin();
    for (size_t i = 0; i < sizeof...(Types); ++i) {
      new (itr++) Any(*read++);
      p->TVMFFISeqCell::size++;
    }
    data_ = std::move(p);
  }
}
```

当引用计数大于 1 时，创建固定容量的新 `ArrayObj` 并逐元素浅拷贝（拷贝 `Any`，对对象引用仅增减引用计数），然后替换 `data_`。这保证了修改不会影响其他共享同一元组的句柄。

## std::tuple 互操作

`Tuple` 通过特化标准库模板实现与 `std::tuple` 的互操作：

- **ADL get**（`tuple.h:362`）：提供 `get<I>(tuple)` 自由函数，委托给成员方法。
- **std::tuple_size**（`tuple.h` 中特化）：`std::tuple_size<Tuple<Types...>>::value` 等于 `sizeof...(Types)`。
- **std::tuple_element**（`tuple.h` 中特化）：`std::tuple_element<I, Tuple<Types...>>::type` 等于第 I 个类型。

这些特化使得 `Tuple` 支持 C++17 结构化绑定：

```cpp
auto [a, b, c] = Tuple<int, String, float>(1, "hello", 3.14f);
```

## 类型特征

`TypeTraits<Tuple<Types...>>`（`tuple.h:242`）继承自 `ObjectRefTypeTraitsBase`，实现了严格的类型检查：

- **CheckAnyStrict**（`tuple.h:273`）：验证 `type_index` 为 `kTVMFFIArray`，数组大小等于 `sizeof...(Types)`，且每个位置的元素类型严格匹配。
- **TryCastFromAnyView**（`tuple.h:294`）：先尝试快速路径（严格匹配），失败后逐位置尝试类型转换。
- **GetMismatchTypeInfo**（`tuple.h:245`）：在类型不匹配时生成精确的诊断信息，指出哪个位置的元素类型不正确。

`type_subsumes_v` 对 `Tuple` 的特化（`tuple.h:345`）定义了元组之间的包容关系：`Tuple<Types...>` 包容 `Tuple<UTypes...>` 当且仅当每个位置的类型都包容对应位置的源类型。

## 设计分析

1. **复用 ArrayObj 的智慧**：`Tuple` 不引入新的对象类型，而是复用 `ArrayObj` 的内联存储、引用计数和 COW 机制。这减少了代码重复，并使得 `Tuple` 可以无缝参与序列容器的 C ABI 接口（底层就是一个 `ArrayObj`）。

2. **固定容量与动态容量的统一**：`Array<T>` 和 `Tuple<Types...>` 底层都是 `ArrayObj`，但前者容量动态变化，后者容量固定。类型系统在编译期区分两者——`Array<T>` 的元素类型统一，`Tuple<Types...>` 的元素类型各异。这种统一使得跨容器转换（如 `Shape` 从 `Array<int64_t>` 构造）自然实现。

3. **COW 的最小化复制**：`CopyIfNotUnique` 复制整个 `ArrayObj`（包括所有位置的 `Any`），但 `Any` 的拷贝是浅拷贝（对象引用仅增减计数），成本可控。由于元组通常很短（2-5 个元素），复制开销可忽略。

4. **移动语义优化**：右值 `get<I>()` 在唯一所有权时移动元素，这对于持有大型对象（如 `String`、`Array`）的元组特别重要，避免了不必要的引用计数原子操作。

## 相关概念

- [051 Array 容器与写时复制](051-array-container.md)：Tuple 的底层存储引擎
- [057 Shape 形状对象](057-shape-object.md)：从 Array<int64_t> 转换的专用容器
- [062 Variant 类型安全变体](062-variant-container.md)：另一种类型安全的联合体容器
- [023 类型特征](/02-core-types/concepts/023-type-traits.md)：TypeTraits 体系详解
