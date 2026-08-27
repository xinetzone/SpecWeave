---
type: Concept
title: "视角062：Variant 类型安全变体"
description: "深入剖析 Variant<V...> 类型安全变体容器的设计，包括基于 Any 的单字存储、编译期类型集合检查、as/get 访问模式、ObjectPtrHash/Equal 支持以及与 std::variant 的差异。"
tags:
  - containers
  - variant
  - type-safe
  - any
  - sum-type
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-175, F-176
  - code:
    - include/tvm/ffi/container/variant.h
    - include/tvm/ffi/any.h
---

# 视角062：Variant 类型安全变体

## 概述

`Variant<V...>` 是 TVM FFI 中的类型安全变体（sum type）容器，代表"可以是 V... 中任意一种类型"的值。与 `std::variant` 不同，`Variant` 不继承自 `ObjectRef`，而是直接持有一个 `Any` 成员，其大小恰好等于 `sizeof(Any)`（16 字节）。这一设计使得 `Variant` 可以在 FFI 边界高效传递，同时在 C++ 层提供编译期类型安全。`Variant` 支持 `as<T>()` 安全尝试转换和 `get<T>()` 强制转换两种访问模式，并为所有备选类型均为 `ObjectRef` 子类的场景提供了 `ObjectPtrHash`/`ObjectPtrEqual` 支持。

## 基于 Any 的单字存储

`Variant` 定义在 `include/tvm/ffi/container/variant.h:46`：

```cpp
template <typename... V>
class Variant {
 public:
  static_assert(details::all_storage_enabled_v<V...>,
                "All types used in Variant<...> must be compatible with Any");
  static constexpr bool _type_container_is_exact = false;
  // ...
 private:
  Any data_;
};
```

类注释（`variant.h:38-43`）明确指出：

> Variant is always backed by a single Any (TVMFFIAny). Even when every alternative derives from ObjectRef, Variant is not ObjectRef-derived; this keeps the layout independent of the contained types (sizeof(Variant<...>) == sizeof(Any)).

关键设计点：

1. **单一 Any 存储**：无论备选类型有多少，`Variant` 仅持有一个 `Any`。实际存储的值由 `Any` 的 `type_index` 标识，变体的类型集合信息仅存在于 C++ 编译期。
2. **非 ObjectRef 派生**：即使所有备选类型都是 `ObjectRef` 子类，`Variant` 也不继承 `ObjectRef`。这避免了对象布局依赖于备选类型的数量和大小，保持了 16 字节的恒定布局。
3. **storage_enabled 约束**：所有备选类型必须满足 `storage_enabled_v`（即可存入 `Any`），由静态断言强制（`variant.h:49`）。

## 编译期类型集合

`Variant` 提供 `variant_contains_v`（`variant.h:58`）在编译期检查类型是否属于变体：

```cpp
template <typename T>
static constexpr bool variant_contains_v =
    (type_subsumes_v<V, T> || ...);
```

这是一个折叠表达式，对所有备选类型 `V` 检查 `type_subsumes_v<V, T>`。`enable_if_variant_contains_t`（`variant.h:61`）用于 SFINAE 约束构造函数和赋值运算符，确保只有变体可接受的类型才能存入。

从值构造（`variant.h:90`）：

```cpp
template <typename T, typename = enable_if_variant_contains_t<T>>
Variant(T other) : data_(std::move(other)) {}
```

这允许隐式转换，但仅限于类型集合中的类型。从 `std::string` 到 `Variant<String, int>` 的隐式转换会被拒绝（因为 `std::string` 不直接包容 `String`，需要显式构造）。

## as 与 get 访问模式

### as：安全尝试

`as<T>()`（`variant.h:108`）返回 `std::optional<T>`，不抛异常：

```cpp
template <typename T, typename = enable_if_variant_contains_t<T>>
TVM_FFI_INLINE std::optional<T> as() const {
  return ToAnyView().template as<T>();
}
```

它委托给 `AnyView::as<T>()`，在类型不匹配时返回 `std::nullopt`。适用于需要分支处理不同类型的场景。

当 `T` 是 `Object` 的子类时，`as<T>()` 有一个重载返回 `const T*`（`variant.h:119`）：

```cpp
template <typename T, typename = std::enable_if_t<std::is_base_of_v<Object, T>>>
TVM_FFI_INLINE const T* as() const {
  return ToAnyView().template as<const T*>().value_or(nullptr);
}
```

这提供了与 `ObjectRef::as<T>()` 一致的指针访问模式。

### get：强制获取

`get<T>()`（`variant.h:129`）返回 `T`，类型不匹配时抛出异常：

```cpp
template <typename T, typename = enable_if_variant_contains_t<T>>
TVM_FFI_INLINE T get() const& {
  return ToAnyView().template cast<T>();
}
```

右值重载（`variant.h:139`）支持移动语义，从内部 `Any` 中移动出值：

```cpp
template <typename T, typename = enable_if_variant_contains_t<T>>
TVM_FFI_INLINE T get() && {
  return std::move(*this).MoveToAny().template cast<T>();
}
```

`get` 适用于确定当前持有类型的场景，其异常提供详细的类型不匹配信息。

## 类型特征

`TypeTraits<Variant<V...>>`（`variant.h:186`）继承自 `TypeTraitsBase`，实现了：

- **CheckAnyStrict**（`variant.h:199`）：检查 `Any` 的类型是否匹配任一备选类型，使用折叠表达式的逻辑或。
- **TryCastFromAnyView**（`variant.h:211`）：先尝试快速路径（严格匹配），失败后按声明顺序逐一尝试备选类型的 `TryCastFromAnyView`（`variant.h:221`）。
- **TypeSchema**（`variant.h:232`）：生成 JSON Schema，如 `{"type":"Variant","args":[...]}`。
- **TypeStr**（`variant.h:231`）：生成可读类型名，如 `Variant<String, Int>`。

`type_subsumes_v` 的特化（`variant.h:256`）定义了变体的类型包容：`Variant<V...>` 包容类型 `T` 当且仅当任一备选类型包容 `T`。

## ObjectPtrHash 与 ObjectPtrEqual

当所有备选类型均为 `ObjectRef` 子类时，`Variant` 支持 `ObjectPtrHash` 和 `ObjectPtrEqual`（`variant.h:243-251`）：

```cpp
template <typename... V>
TVM_FFI_INLINE size_t ObjectPtrHash::operator()(
    const Variant<V...>& a) const {
  return std::hash<Object*>()(a.GetObjectPtrForHashEqual());
}
```

`GetObjectPtrForHashEqual`（`variant.h:169`）通过 `static_assert` 确保所有备选类型都是 `ObjectRef` 子类，然后从内部 `Any` 提取裸 `Object*` 指针。这使得 `Variant` 可以直接用作 `std::unordered_map` 的键类型，基于对象身份（指针值）进行哈希和比较，与 `ObjectRef` 的哈希语义一致。

## 与 std::variant 的差异

| 特性 | Variant<V...> | std::variant<V...> |
|------|---------------|-------------------|
| 存储 | 单个 Any（16 字节） | 最大备选类型的大小 + 标签 |
| FFI 兼容 | 是（直接映射到 Any） | 否（标准库布局不稳定） |
| 类型检查 | 运行时 type_index | 编译期 + 运行时索引 |
| 对象引用 | 原生支持引用计数 | 不感知引用计数 |
| 跨语言 | 可通过 Any 跨 FFI | C++ 专用 |

## 设计分析

1. **16 字节恒定布局**：`Variant` 的大小不随备选类型数量或大小变化，始终等于 `sizeof(Any)`。这对于 FFI 至关重要——变体值可以直接通过 `TVMFFIAny` 在 C ABI 边界传递，无需额外的序列化或堆分配。

2. **编译期安全与运行时灵活性**：`Variant` 在 C++ 层通过模板和 SFINAE 提供编译期类型安全（不能存入不在集合中的类型），在运行时通过 `Any` 的 `type_index` 实现灵活的类型检查和转换。编译期检查防止编程错误，运行时检查支持跨语言动态类型。

3. **类型转换顺序**：`TryCastFromAnyView` 按备选类型的声明顺序尝试转换。这意味着如果多个备选类型都可以从某个 `Any` 值转换，第一个匹配的类型胜出。声明顺序应从最具体到最一般，以避免意外的转换结果。

4. **非虚多态**：`Variant` 不使用虚函数，类型分派完全由 `type_index` 和模板完成。这与 TVM FFI 的整体设计一致——避免虚表指针开销和 ABI 不稳定。

5. **same_as 身份比较**：`same_as` 方法（`variant.h:154`）比较两个变体是否持有相同的底层对象身份（对于对象类型比较指针，对于 POD 比较值），这在图遍历和去重场景中很有用。

## 相关概念

- [016 TVMFFIAny 16字节布局](/02-core-types/concepts/016-any-16-byte-layout.md)：Variant 的底层存储
- [024 cast/try_cast/as](/02-core-types/concepts/024-cast-try-cast-as.md)：Any 的类型转换接口
- [060 Tuple 类型化元组](060-tuple-container.md)：另一种类型安全的复合容器
- [064 容器类型特征与类型包容](064-container-type-traits.md)：type_subsumes 体系
