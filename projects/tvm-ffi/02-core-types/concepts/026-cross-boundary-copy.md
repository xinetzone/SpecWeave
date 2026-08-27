---
type: Concept
title: "视角026：跨边界复制语义"
description: "分析 TVMFFIAny 值在 C ABI 边界传递时的所有权规则，包括 AnyView 借用、Any 获取所有权、RawStr/ByteArrayPtr 自动复制、ObjectRValueRef 移动展开，以及 InplaceConvertAnyViewToAny 的完整转换逻辑。"
tags:
  - core-types
  - ffi
  - ownership
  - copy-semantics
  - boundary
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-085, F-086, F-099
  - code:
    - include/tvm/ffi/any.h
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
---

# 视角026：跨边界复制语义

## 概述

TVM FFI 的核心挑战之一是在 C ABI 边界正确管理值的所有权。`TVMFFIAny` 作为一个 16 字节 POD 结构体按值传递，但它可能持有指向堆对象的指针。跨边界复制语义定义了在 C++ 层与 C ABI 层之间转换时，何时增加引用计数、何时复制数据、何时转移所有权。这些规则由 `InplaceConvertAnyViewToAny` 函数集中实现，确保了 FFI 边界的内存安全。

## 所有权模型

### 三层所有权语义

TVM FFI 定义了三个层级的值容器：

| 容器 | 所有权 | 引用计数 | 生命周期保证 |
|---|---|---|---|
| `TVMFFIAny` (C 结构体) | 无管理 | 不自动操作 | 由调用约定保证 |
| `AnyView` (C++ 视图) | 借用 | 不增减 | 仅在调用期间有效 |
| `Any` (C++ 容器) | 拥有 | 自动增减 | RAII 管理 |

### C ABI 调用约定

C ABI 函数 `TVMFFIFunctionCall`（`c_api.h`）通过 `TVMFFIAny* args` 和 `TVMFFIAny* ret` 传递参数和返回值。约定如下：

- **参数**：调用者拥有参数值，被调用方在函数执行期间可以借用。如果被调用方需要保留参数，必须获取所有权。
- **返回值**：被调用方将返回值写入 `ret`，所有权转移给调用者。调用者负责释放返回值持有的资源。
- **异常**：通过 `TVMFFIError` 机制传递，不涉及值所有权。

## AnyView → Any 的所有权获取

当从 `AnyView`（借用）构造 `Any`（拥有）时，必须获取底层值的所有权。这一逻辑集中在 `details::InplaceConvertAnyViewToAny`（`any.h:201-224`）中。

### 函数签名

```cpp
TVM_FFI_INLINE void InplaceConvertAnyViewToAny(TVMFFIAny* data) {
  // 就地转换，将借用视图变为拥有值
}
```

函数接受指向 `TVMFFIAny` 的指针，就地修改其内容以获取所有权。这种就地设计避免了额外的内存拷贝。

### 特殊类型处理

函数处理四种需要特殊所有权转换的类型：

#### 1. RawStr（kTVMFFIRawStr = 8）

```cpp
if (data->type_index == TypeIndex::kTVMFFIRawStr) {
  const char* str = data->v_c_str;
  String new_str = String(str);
  data->v_obj = details::ObjectUnsafe::MoveObjectPtrToTVMFFIObjectPtr(
      details::ObjectUnsafe::ObjectPtrFromObjectRef<StringObj>(std::move(new_str)));
  data->type_index = TypeIndex::kTVMFFIStr;
  return;
}
```

`kTVMFFIRawStr` 存储 `const char*`，指向外部管理的 C 字符串。由于 `Any` 必须拥有其值，函数将 C 字符串复制到新的 `String` 堆对象中，然后将 `v_obj` 指向该对象。这确保了即使原始 C 字符串被释放，`Any` 持有的字符串仍然有效。

#### 2. ByteArrayPtr（kTVMFFIByteArrayPtr = 9）

```cpp
if (data->type_index == TypeIndex::kTVMFFIByteArrayPtr) {
  TVMFFIByteArray* arr = reinterpret_cast<TVMFFIByteArray*>(data->v_ptr);
  Bytes new_bytes = Bytes(arr->data, arr->size);
  data->v_obj = details::ObjectUnsafe::MoveObjectPtrToTVMFFIObjectPtr(
      details::ObjectUnsafe::ObjectPtrFromObjectRef<BytesObj>(std::move(new_bytes)));
  data->type_index = TypeIndex::kTVMFFIBytes;
  return;
}
```

类似地，`kTVMFFIByteArrayPtr` 存储指向外部 `TVMFFIByteArray` 的指针。函数复制字节内容到新的 `Bytes` 堆对象，获取独立所有权。

#### 3. ObjectRValueRef（kTVMFFIObjectRValueRef = 10）

```cpp
if (data->type_index == TypeIndex::kTVMFFIObjectRValueRef) {
  auto* rvalue_ref = reinterpret_cast<details::ObjectPtrBase*>(data->v_ptr);
  data->v_obj = reinterpret_cast<TVMFFIObject*>(rvalue_ref->get());
  rvalue_ref->release();
  data->type_index = data->v_obj->type_index;
  return;
}
```

右值引用的处理最为关键：
1. 从 `v_ptr` 获取 `ObjectPtrBase` 的地址。
2. 获取对象指针并存入 `v_obj`。
3. 调用 `release()` 将源 `ObjectPtr` 置空（不减少引用计数），所有权直接转移。
4. 将 `type_index` 从 `kTVMFFIObjectRValueRef` 更新为对象的实际类型索引。

这一过程实现了真正的零拷贝移动——没有原子操作，没有内存分配。

#### 4. 普通堆对象（type_index >= 64）

```cpp
if (data->type_index >= TypeIndex::kTVMFFIStaticObjectBegin) {
  details::ObjectUnsafe::IncRefObjectHandle(data->v_obj);
}
```

对于普通堆对象（String、Array、Map 等），函数增加引用计数。这是因为 `AnyView` 借用了对象指针，`Any` 需要获取自己的强引用。

### POD 类型无需处理

对于 `kTVMFFINone`、`kTVMFFIInt`、`kTVMFFIBool`、`kTVMFFIFloat`、`kTVMFFIDataType`、`kTVMFFIDevice`、`kTVMFFISmallStr`、`kTVMFFISmallBytes` 等类型，值直接内联在 `TVMFFIAny` 的 8 字节联合体中，位拷贝即拥有完整副本，无需任何额外操作。

## Any → AnyView 的借用转换

从 `Any` 到 `AnyView` 的转换是零开销的（`any.h:322-324`）：

```cpp
operator AnyView() const {
  return AnyView::CopyFromTVMFFIAny(data_);
}
```

这只是位拷贝 `TVMFFIAny`，不改变引用计数。`AnyView` 借用 `Any` 持有的引用，只要 `Any` 存活，`AnyView` 就有效。

## PackedArgs 中的参数传递

`PackedArgs` 类（`function.h`）是 C ABI 参数数组的 C++ 封装：

```cpp
class PackedArgs {
  const TVMFFIAny* values_;
  size_t size_;
 public:
  AnyView operator[](size_t i) const {
    return AnyView::CopyFromTVMFFIAny(values_[i]);
  }
};
```

参数以 `AnyView`（借用）形式访问。如果打包函数的 lambda 参数声明为具体类型（如 `int`、`String`、`Array<int>`），`Function::FromTyped` 生成的适配代码会调用 `cast<T>()` 或 `try_cast<T>()` 进行转换。对于对象类型，`cast` 内部的 `CopyFromAnyViewAfterCheck` 会增加引用计数，使函数参数成为拥有的副本。

如果函数参数声明为 `AnyView`，则直接借用，不增加引用计数——这适用于只需在函数调用期间读取参数且不需要保留的场景。

## 返回值的所有权转移

C ABI 层的返回值约定：被调用方写入 `TVMFFIAny* ret`，所有权转移给调用者。在 C++ 层：

- 如果函数返回 `Any`，`Any` 的 `MoveToAny` 将值写入 `ret`，源 `Any` 被置空。
- 如果函数返回具体 `ObjectRef` 类型，适配代码通过 `MoveToAny` 移动对象指针，不增加引用计数。
- 如果函数返回 POD 类型，直接写入联合体。

调用方通过 `Any::MoveFromAny` 或直接读取 `TVMFFIAny` 获取返回值所有权。

## CopyToAnyView vs MoveToAny

`TypeTraits` 提供两个序列化方法，体现了借用与拥有的区别：

- **CopyToAnyView**：用于构造 `AnyView`。对于堆对象，存储指针但不增加引用计数。适用于值在当前作用域内保证存活的场景。
- **MoveToAny**：用于构造 `Any`。对于堆对象，移动 `ObjectPtr` 所有权，不增加引用计数；对于 `std::string`，创建新的 `String` 堆对象并移动内容。

这两个方法的区分使得 FFI 可以在不同场景下选择最优的所有权策略。

## 设计分析

跨边界复制语义的设计体现了以下原则：

1. **集中式所有权转换**：所有借用→拥有的转换逻辑集中在 `InplaceConvertAnyViewToAny`，新增特殊类型时只需修改一处。
2. **最小化原子操作**：移动路径（RValueRef）完全避免原子操作；普通对象仅需一次 IncRef；POD 类型零操作。
3. **防御性复制**：RawStr 和 ByteArrayPtr 的自动复制防止了悬垂指针，即使调用者管理的内存在函数返回后被释放。
4. **就地修改**：`InplaceConvertAnyViewToAny` 就地修改 `TVMFFIAny`，避免创建临时对象和额外拷贝。
5. **约定优于强制**：所有权规则通过 API 约定和命名（Copy vs Move）表达，而非编译器强制。这要求开发者理解 `AnyView` 和 `Any` 的语义差异。

## 相关概念

- [017 AnyView 非拥有语义](017-anyview-non-owning.md)：借用视图
- [018 Any 拥有语义](018-any-owning.md)：拥有容器
- [025 FFI 移动语义](025-ffi-move-semantics.md)：RValueRef 跨边界移动
- [034 FFI 右值引用](034-ffi-rvalue-ref.md)：RValueRef 深入
