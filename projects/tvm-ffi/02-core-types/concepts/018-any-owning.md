---
type: Concept
title: "视角018：Any 拥有语义"
description: "分析 Any 作为持有型类型擦除容器的设计，包括引用计数管理（IncRef/DecRef）、拷贝/移动构造与赋值、从具体类型构造、cast/try_cast/as 类型转换，以及 same_as 浅比较和 AnyHash 哈希机制。"
tags:
  - core-types
  - any
  - owning
  - reference-counting
  - raii
  - move-semantics
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-085, F-086, F-087, F-088, F-089, F-090, F-091, F-092, F-093, F-094, F-095, F-096, F-097, F-098
  - code:
    - include/tvm/ffi/any.h
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
---

# 视角018：Any 拥有语义

## 概述

`Any` 是 TVM FFI 的持有型类型擦除容器，定义在 `include/tvm/ffi/any.h:233`。与 `AnyView` 的非持有语义不同，`Any` 对堆对象持有强引用——拷贝时增加引用计数，析构时减少引用计数。`Any` 是 FFI 中值存储和返回的主要类型，确保被包装的值在 `Any` 存活期间不会被释放。

## 与 AnyView 的关系

值得注意的是，在当前版本（v0.1.14）中，`Any` **并非继承自 `AnyView`**，而是独立定义的类，同样包含一个 `TVMFFIAny data_` 成员（`any.h:236`）。两者通过静态断言保证内存布局一致：

```cpp
static_assert(sizeof(AnyView) == sizeof(TVMFFIAny));
static_assert(sizeof(Any) == sizeof(TVMFFIAny));
```

`Any` 提供到 `AnyView` 的隐式转换运算符（`any.h:322-324`）：

```cpp
operator AnyView() const {
  return AnyView::CopyFromTVMFFIAny(data_);
}
```

这一转换执行位拷贝，不改变引用计数。从 `AnyView` 构造 `Any` 时（`any.h:309-311`），则调用 `InplaceConvertAnyViewToAny` 获取所有权。

## RAII 生命周期管理

### 析构函数

`Any` 的析构函数（`any.h:268`）调用 `reset()`：

```cpp
~Any() { this->reset(); }
```

`reset()` 方法（`any.h:242-249`）检查是否持有堆对象，若是则减少引用计数：

```cpp
void reset() {
  if (data_.type_index >= TVMFFITypeIndex::kTVMFFIStaticObjectBegin) {
    details::ObjectUnsafe::DecRefObjectHandle(data_.v_obj);
  }
  data_.type_index = TVMFFITypeIndex::kTVMFFINone;
  data_.zero_padding = 0;
  data_.v_int64 = 0;
}
```

关键判断条件是 `type_index >= kTVMFFIStaticObjectBegin`（值为 64），所有堆对象类型的索引都在此阈值之上。POD 类型和小字符串/小字节数组无需引用计数管理。

### 拷贝构造

拷贝构造函数（`any.h:273-277`）复制 `data_` 后，对堆对象增加引用计数：

```cpp
Any(const Any& other) : data_(other.data_) {
  if (data_.type_index >= TypeIndex::kTVMFFIStaticObjectBegin) {
    details::ObjectUnsafe::IncRefObjectHandle(data_.v_obj);
  }
}
```

这是一个浅拷贝——多个 `Any` 可以共享同一个堆对象，通过引用计数确保对象在最后一个引用释放前存活。

### 移动构造

移动构造函数（`any.h:282-286`）执行零开销所有权转移：

```cpp
Any(Any&& other) noexcept : data_(other.data_) {
  other.data_.type_index = TypeIndex::kTVMFFINone;
  other.data_.zero_padding = 0;
  other.data_.v_int64 = 0;
}
```

源对象被置为 None，避免析构时减少引用计数。整个操作仅涉及 16 字节位拷贝和清零，无原子操作。

### 拷贝与移动赋值

赋值运算符使用 copy-and-swap 惯用法（`any.h:291-303`）：

```cpp
Any& operator=(const Any& other) {
  Any(other).swap(*this);
  return *this;
}
Any& operator=(Any&& other) noexcept {
  Any(std::move(other)).swap(*this);
  return *this;
}
```

这种写法天然保证自赋值安全和异常安全。

## 从 AnyView 构造

从 `AnyView` 构造 `Any`（`any.h:309-311`）需要获取所有权：

```cpp
Any(const AnyView& other) : data_(other.data_) {
  details::InplaceConvertAnyViewToAny(&data_);
}
```

`InplaceConvertAnyViewToAny`（`any.h:201-224`）处理三种特殊情况：

1. **RawStr → String 对象**：`kTVMFFIRawStr` 类型的 `const char*` 被转换为拥有的 `String` 堆对象，因为原始 C 字符串的生命周期不受 FFI 管理。
2. **ByteArrayPtr → Bytes 对象**：`kTVMFFIByteArrayPtr` 类型的 `TVMFFIByteArray*` 被转换为拥有的 `Bytes` 堆对象。
3. **ObjectRValueRef → ObjectRef**：`kTVMFFIObjectRValueRef` 类型的右值引用被解引用并移动所有权，源指针置空防止双重移动。

对于普通堆对象（`type_index >= kTVMFFIStaticObjectBegin`），函数调用 `IncRefObjectHandle` 增加引用计数。

## 从具体类型构造

`Any` 提供模板构造函数（`any.h:329-332`）接受任何启用 FFI 转换的类型：

```cpp
template <typename T, typename = std::enable_if_t<TypeTraits<T>::convert_enabled>>
Any(T other) {
  TypeTraits<T>::MoveToAny(std::move(other), &data_);
}
```

注意参数按值传递并使用 `MoveToAny`，这意味着：
- 对于 POD 类型（int、double、bool），值直接写入联合体。
- 对于 `std::string`，字符串内容被移动到新创建的 `String` 堆对象中。
- 对于 `ObjectRef` 子类，对象指针的所有权被转移到 `Any`，不增加引用计数。

## 类型转换接口

`Any` 提供与 `AnyView` 类似但更丰富的类型转换接口，区分左值和右值重载：

### as<T>()：严格重解释

`Any` 提供 `as<T>() &&`（`any.h:353-363`）和 `as<T>() const&`（`any.h:397-407`）两个版本。右值版本在严格匹配时使用 `MoveFromAnyAfterCheck` 移动值，避免不必要的拷贝；左值版本使用 `CopyFromAnyViewAfterCheck`。

当 `T` 为 `Any` 本身时，右值版本移动整个 `Any`，左值版本拷贝。

### as_or_throw<T>()：严格重解释或抛出

`as_or_throw<T>()`（`any.h:374-386` 和 `418-430`）在 `as<T>()` 失败时抛出 `TypeError`，不执行语义转换。

### cast<T>()：语义转换

`cast<T>() const&`（`any.h:449-457`）委托给 `TryCastFromAnyView`，支持类型提升和转换：

```cpp
template <typename T>
T cast() const& {
  std::optional<T> opt = TypeTraits<T>::TryCastFromAnyView(&data_);
  if (TVM_FFI_PREDICT_FALSE(!opt.has_value())) {
    TVM_FFI_THROW(TypeError) << "Cannot convert from type `"
                             << TypeTraits<T>::GetMismatchTypeInfo(&data_)
                             << "` to `" << TypeTraits<T>::TypeStr() << "`";
  }
  return *std::move(opt);
}
```

右值版本 `cast<T>() &&`（`any.h:465-477`）在严格匹配时走快速路径直接移动，否则回退到 `TryCastFromAnyView`。

### try_cast<T>()：非抛出转换

`try_cast<T>()`（`any.h:488-494`）返回 `std::optional<T>`，支持 `T = Any` 的特化。

## 浅比较与哈希

### same_as

`same_as` 方法（`any.h:500-503`）执行浅比较，逐字段比较 `type_index`、`zero_padding` 和 `v_int64`：

```cpp
bool same_as(const Any& other) const noexcept {
  return data_.type_index == other.data_.type_index &&
         data_.zero_padding == other.data_.zero_padding &&
         data_.v_int64 == other.data_.v_int64;
}
```

对于对象类型，这比较的是指针地址而非对象内容，因此两个内容相同但地址不同的对象 `same_as` 返回 false。还有一个接受 `ObjectRef` 的重载（`any.h:510-517`）。

### AnyHash

`AnyHash` 仿函数（`any.h:648-687`）根据类型选择哈希策略：
- 小字符串/小字节数组：使用稳定的内容哈希，确保栈上和堆上的相同字符串哈希一致。
- 堆字符串/字节数组：通过 `BytesObjBase` 访问数据并计算内容哈希。
- 其他堆对象：查找自定义哈希类型属性列，若注册了自定义哈希函数则调用之；否则组合 `type_index` 和 `v_uint64`（指针值）。
- POD 类型：组合 `type_index` 和 `v_uint64`。

## 设计分析

`Any` 的设计在安全性和性能之间取得了平衡：

1. **RAII 自动化**：析构函数自动释放引用，异常安全，无需手动管理。
2. **移动优先**：模板构造函数按值接收并 `MoveToAny`，鼓励移动语义；右值转换方法优先移动。
3. **copy-and-swap**：赋值运算符使用这一惯用法，代码简洁且天然异常安全。
4. **阈值快速判断**：`type_index >= kTVMFFIStaticObjectBegin` 一次比较即可判断是否需要引用计数操作，热路径高效。
5. **AnyView 转换的所有权获取**：从非持有视图构造持有的 `Any` 时，`InplaceConvertAnyViewToAny` 正确处理 RawStr/ByteArrayPtr/RValueRef 等需要所有权转换的特殊类型，避免悬垂指针。

## 相关概念

- [016 TVMFFIAny 16字节布局](016-any-16-byte-layout.md)：底层数据结构
- [017 AnyView 非拥有语义](017-anyview-non-owning.md)：非持有视图的对比
- [025 FFI 移动语义](025-ffi-move-semantics.md)：移动构造与右值引用
- [028 组合引用计数](028-combined-refcount.md)：引用计数底层机制
- [035 类型转换流水线](035-type-conversion-pipeline.md)：cast/try_cast 转换流程
