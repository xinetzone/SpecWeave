---
type: Concept
title: "视角110：Unsafe 操作"
description: "解析 TVM FFI 中的 Unsafe 操作体系：TVM_FFI_UNSAFE_ASSUME 编译器假设宏、ObjectUnsafe 引用计数与指针操作、AnyUnsafe 类型擦除数据移动、ExpectedUnsafe 原始值访问，以及 Unsafe 操作的安全前置条件与使用纪律。"
tags:
  - cpp-impl
  - unsafe
  - assume
  - undefined-behavior
  - performance
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-019, F-060, F-095, F-122, F-123
  - code:
    - include/tvm/ffi/base_details.h
    - include/tvm/ffi/any.h
    - include/tvm/ffi/object.h
    - include/tvm/ffi/expected.h
    - include/tvm/ffi/device.h
    - include/tvm/ffi/error.h
---

# 视角110：Unsafe 操作

## 概述

TVM FFI 在类型安全的公开 API 之下，提供了一组以 "Unsafe" 命名的操作接口和编译器提示宏。这些接口绕过常规的类型检查、引用计数安全或边界验证，直接操作底层数据，以换取热路径上的极致性能。Unsafe 操作并非鼓励随意使用——相反，每一个 Unsafe 接口都有明确的前置条件，调用者必须确保这些条件成立，否则将导致未定义行为。FFI 通过命名约定（`Unsafe` 后缀、`TVM_FFI_UNSAFE_` 前缀）和 `details` 命名空间隔离，使这些危险操作在代码审查中清晰可辨。

## TVM_FFI_UNSAFE_ASSUME 编译器假设

`TVM_FFI_UNSAFE_ASSUME(cond)` 定义在 `base_details.h:126-139`，是最基础的 Unsafe 操作：

```cpp
#if defined(__clang__)
#define TVM_FFI_UNSAFE_ASSUME(cond) __builtin_assume(cond)
#elif defined(__GNUC__)
#define TVM_FFI_UNSAFE_ASSUME(cond)       \
  do {                                    \
    if (!(cond)) __builtin_unreachable(); \
  } while (0)
#elif defined(_MSC_VER)
#define TVM_FFI_UNSAFE_ASSUME(cond) __assume(cond)
#else
#define TVM_FFI_UNSAFE_ASSUME(cond) static_cast<void>(0)
#endif
```

源码注释明确警告（`base_details.h:118-124`）："Use ONLY when the external invariant guarantees cond. The compiler will remove all paths inconsistent with cond. This is not an assertion or check -- using on a wrong cond will result in undefined behavior."

与 `TVM_FFI_PREDICT_TRUE`（仅提示分支概率，条件仍被检查）不同，`UNSAFE_ASSUME` 告知编译器条件**必然为真**，编译器可以据此消除分支、传播常量、删除不可达路径。如果条件实际为假，程序行为未定义。

### 典型使用场景

`device.h:115` 中，`CopyFromAnyViewAfterCheck` 使用 ASSUME 告知编译器类型索引已验证：

```cpp
TVM_FFI_INLINE static DLDevice CopyFromAnyViewAfterCheck(const TVMFFIAny* src) {
  TVM_FFI_UNSAFE_ASSUME(src->type_index == TypeIndex::kTVMFFIDevice);
  return src->v_device;
}
```

方法名中的 `AfterCheck` 表明调用者已通过 `CheckAnyStrict`（`device.h:110`）验证了类型。此时 ASSUME 允许编译器消除类型检查分支，直接返回联合体中的设备字段。

`any.h:883` 和 `any.h:913` 中，`ObjectRef::as_or_throw()` 使用 ASSUME 优化对象类型检查：

```cpp
TVM_FFI_UNSAFE_ASSUME(any_data.type_index >= TypeIndex::kTVMFFIStaticObjectBegin);
```

这告知编译器该值必然是对象类型，可以安全地走对象指针路径。

## ObjectUnsafe 底层对象操作

`details::ObjectUnsafe`（`object.h:1365-1397`）提供绕过类型安全的引用计数和指针操作：

### IncRefObjectHandle / DecRefObjectHandle

```cpp
TVM_FFI_INLINE static void DecRefObjectHandle(TVMFFIObjectHandle handle) {
  if (handle) reinterpret_cast<Object*>(handle)->DecRef();
}
TVM_FFI_INLINE static void IncRefObjectHandle(TVMFFIObjectHandle handle) {
  reinterpret_cast<Object*>(handle)->IncRef();
}
```

这两个方法直接将 `TVMFFIObjectHandle`（即 `void*`）reinterpret_cast 为 `Object*` 并操作引用计数，不检查类型索引是否确实指向一个有效的 `Object`。调用者必须保证句柄有效。它们被 C ABI 函数 `TVMFFIObjectIncRef`/`TVMFFIObjectDecRef`（`object.cc:523-533`）、`String` 的引用管理（`string.h:125,145`）、`TensorObj` 的 self-referencing（`tensor.h:143,171`）等使用。

### 指针移动与裸访问

- **`MoveObjectPtrToTVMFFIObjectPtr`**（`object.h:1387`）：将 `ObjectPtr<T>` 的所有权移动到原始 `TVMFFIObject*`，不修改引用计数。调用者接管所有权。
- **`MoveObjectRefToTVMFFIObjectPtr`**（`object.h:1393`）：类似地从 `ObjectRef` 移动。
- **`RawObjectPtrFromObjectRef`**（`object.h:1373`）：直接返回 `ObjectRef` 内部的裸指针，不增加引用计数。
- **`TVMFFIObjectPtrFromObjectRef`**（`object.h:1377`）：返回 C ABI 对象头指针。
- **`ObjectPtrFromUnowned`**（`object.h:1356`）：从裸指针构造 `ObjectPtr`，不增加引用计数——调用者必须已持有引用。

### 弱引用操作

C ABI 层的 `TVMFFIPointerIsAlive`、`TVMFFIPointerDecWeakRef`、`TVMFFIPointerLock`（`c_api.h:890-903`，事实 F-060）对应 `WeakObjectPtr<T>`（`object.h:559`）的实现。`WeakObjectPtr::lock()`（`object.h:597`）尝试将弱引用提升为强引用，底层调用 `TryPromoteWeakPtr`（`object.h:258`），该方法使用 CAS 循环原子地增加强引用计数。

## AnyUnsafe 类型擦除数据移动

`details::AnyUnsafe`（`any.h:532` 声明为友元）提供以下关键操作：

- **`MoveTVMFFIAnyToAny`**（`any.h:600`）：从原始 `TVMFFIAny*` 移动构造 `Any`，接管对象引用所有权。
- **`MoveAnyToTVMFFIAny`**（`any.h:592`）：将 `Any` 移动到原始 `TVMFFIAny`，使源 `Any` 置空。
- **`MoveFromAnyAfterCheck`**（`any.h:624`）：在类型检查通过后，从 `Any` 移动出目标类型的值。
- **`CopyFromAnyViewAfterCheck`**（`any.h:615`）：在类型检查通过后，从 `AnyView` 复制出值。
- **`ObjectPtrFromAnyAfterCheck`**（`any.h:632`）：在确认是对象类型后，直接取出对象指针。
- **`TVMFFIAnyPtrFromAny`**（`any.h:636`）：返回指向内部 `TVMFFIAny` 的常量指针。
- **`CheckAnyStrict`**（`any.h:610`）：严格类型检查，是 `AfterCheck` 系列函数的前置条件。
- **`GetMismatchTypeInfo`**（`any.h:641`）：生成类型不匹配的错误信息。

所有 `AfterCheck` 方法的命名约定明确表明：调用者**必须**先调用对应的检查函数。这是一种"检查与使用分离"的模式——检查在一处完成，后续多次使用无需重复检查，但使用处通过 ASSUME 和命名提醒维护者前置条件。

## ExpectedUnsafe 原始值访问

`details::ExpectedUnsafe`（`expected.h:294`，`Expected<T>` 在 `expected.h:204` 声明为友元）提供：

- **`MoveFromTVMFFIAny<T>`**（`expected.h:302`）：将原始 `TVMFFIAny` 移入 `Expected<T>` 存储，不检查是否为错误。
- **`MoveToTVMFFIAny`**：将 `Expected` 的内部存储移动到原始 `TVMFFIAny`。

这些方法用于 FFI 边界处，当从 C ABI 接收到 `TVMFFIAny` 且已知其语义（成功值或错误）时，直接构造 `Expected`，跳过类型检查。

## Unsafe 操作的使用纪律

TVM FFI 通过多层机制确保 Unsafe 操作不被滥用：

1. **命名约定**：所有 Unsafe 结构体以 `Unsafe` 后缀命名；所有 Unsafe 函数名包含 `AfterCheck`、`FromUnowned`、`Unsafe` 等关键词；宏以 `TVM_FFI_UNSAFE_` 前缀标识。
2. **details 命名空间**：`ObjectUnsafe`、`AnyUnsafe`、`ExpectedUnsafe` 均位于 `tvm::ffi::details`，头文件注释明确"internal use only"。
3. **前置条件文档**：每个 Unsafe 方法的注释或命名（如 `AfterCheck`）说明调用者必须满足的条件。
4. **TVM_FFI_ICHECK 守卫**：在调试构建中，部分 Unsafe 路径仍通过 `TVM_FFI_ICHECK`（`error.h:485`）进行内部检查，这些检查在发布构建中保留但抛出异常而非 UB。
5. **友元限制**：Unsafe 结构体通过友元声明获得访问权，编译器强制只有这些特定结构体可以访问私有数据。

## 设计分析

Unsafe 操作体现了"安全默认、性能逃逸"的设计哲学。FFI 的公开 API（`Any::Cast<T>`、`ObjectPtr<T>`、`Expected<T>::value`）在类型安全的前提下提供合理性能，而 Unsafe 接口为编译器和 FFI 内部基础设施提供了消除所有冗余检查的能力。关键的设计决策是将安全检查与值访问分离为 `Check` 和 `AfterCheck` 两个步骤——这允许在函数入口处检查一次，然后在内部多次高效访问，而不是每次访问都重复检查。`TVM_FFI_UNSAFE_ASSUME` 则是更激进的优化，它利用编译器的假设机制消除所有防御性代码，但要求调用者有外部不变量保证。这种分层设计使得 FFI 在 Rust 等安全语言绑定中可以选择只使用安全 API，而在 C++ 热路径中可以使用 Unsafe API 达到原生性能。

## 相关概念

- [107 分支预测提示](107-branch-prediction-hints.md)：PREDICT 与 UNSAFE_ASSUME 的区别
- [109 友元类模式](109-friend-class-pattern.md)：Unsafe 访问器通过友元获得访问权
- [045 异常跨 FFI 边界](/03-functions/concepts/045-exception-crossing-ffi.md)：Safe Call 与异常安全
- [085 Expected 异常免除](/06-error-handling/concepts/085-expected-exception-free.md)：Expected 的安全错误处理
