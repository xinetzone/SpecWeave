---
type: Concept
title: "视角037：FunctionCell 函数单元"
description: "解析 TVMFFIFunctionCell 结构体的内存布局与设计意图：safe_call 与 cpp_call 双函数指针如何共存于同一对象，以及 C++ 层 FunctionObj 如何继承该结构。"
tags:
  - function
  - function-cell
  - memory-layout
  - c-abi
  - cpp-inheritance
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-017, F-020
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - src/ffi/function.cc
---

# 视角037：FunctionCell 函数单元

## 概述

`TVMFFIFunctionCell` 是 TVM FFI 函数对象在 C ABI 层的内存单元定义。它紧跟在 `TVMFFIObject` 头部之后，构成函数对象的完整内存布局。该结构体仅包含两个函数指针——`safe_call` 和 `cpp_call`——却支撑了整个 FFI 的双路径调用机制。理解 FunctionCell 的设计是理解函数调用系统的关键。

## 结构体定义

`TVMFFIFunctionCell` 定义在 `c_api.h:509-525`：

```c
typedef struct {
  TVMFFISafeCallType safe_call;
  void* cpp_call;
} TVMFFIFunctionCell;
```

在 64 位系统上，该结构体占 16 字节：

| 偏移 | 字段 | 类型 | 大小 | 用途 |
|------|------|------|------|------|
| 0 | `safe_call` | `TVMFFISafeCallType` | 8 字节 | 异常安全的 C ABI 调用入口 |
| 8 | `cpp_call` | `void*` | 8 字节 | C++ 快速路径调用入口（可为 NULL） |

结合 `TVMFFIObject` 头部（含类型索引和引用计数），一个函数对象在内存中的完整布局为：

```
+-------------------+  ← 对象起始地址
|   TVMFFIObject    |  类型索引 + 引用计数 + deleter
+-------------------+  ← sizeof(TVMFFIObject)
| TVMFFIFunctionCell|  safe_call + cpp_call
+-------------------+
```

C ABI 提供了内联辅助函数 `TVMFFIFunctionGetCellPtr`（`c_api.h:1593-1594`）来获取 Cell 指针：

```c
inline TVMFFIFunctionCell* TVMFFIFunctionGetCellPtr(TVMFFIObjectHandle obj) {
  return reinterpret_cast<TVMFFIFunctionCell*>(
      reinterpret_cast<char*>(obj) + sizeof(TVMFFIObject));
}
```

## safe_call 字段

`safe_call` 是 `TVMFFISafeCallType` 类型的函数指针（`c_api.h:501`），签名为：

```c
int (*)(void* handle, const TVMFFIAny* args, int32_t num_args, TVMFFIAny* result);
```

该字段**始终非空**。它代表函数的异常安全入口：内部捕获所有 C++ 异常，将其转换为 TLS 错误对象，并通过返回值 -1 报告失败。跨语言边界（如 Python 调用 C++ 函数）时，必须通过 `safe_call` 进行调用。

## cpp_call 字段

`cpp_call` 是 `void*` 类型的指针，指向一个 C++ 函数。其实际签名为（`function.h:116`）：

```cpp
using FCall = void (*)(const FunctionObj*, const AnyView*, int32_t, Any*);
```

与 `safe_call` 的关键区别：

1. **返回类型为 `void`**：不返回错误码，异常直接抛出。
2. **参数为 C++ 类型**：使用 `const AnyView*` 和 `Any*` 而非 C 的 `TVMFFIAny*`。
3. **首参数为 `const FunctionObj*`**：类型更明确，避免 `void*` 转换。

该字段**可为 NULL**。当函数来源于纯 C 回调（通过 `TVMFFIFunctionCreate` 创建）时，`cpp_call` 为 NULL，此时所有调用都必须走 `safe_call` 路径。

源码注释明确说明（`c_api.h:519-522`）：

> This pointer should be set to NULL for functions that are not originally created in cpp.
> The caller must assume the same cpp exception catching abi when using this pointer.
> When used across FFI boundaries, always use safe_call.

## C++ 层的继承关系

在 C++ 层，`FunctionObj` 类（`function.h:113`）通过多重继承将 C 结构体内嵌到对象中：

```cpp
class FunctionObj : public Object, public TVMFFIFunctionCell {
 public:
  using FCall = void (*)(const FunctionObj*, const AnyView*, int32_t, Any*);
  using TVMFFIFunctionCell::cpp_call;
  using TVMFFIFunctionCell::safe_call;

  TVM_FFI_INLINE void CallPacked(const AnyView* args, int32_t num_args, Any* result) const {
    FCall call_ptr =
        this->cpp_call ? reinterpret_cast<FCall>(this->cpp_call)
                       : CppCallDedirectToSafeCall;
    (*call_ptr)(this, args, num_args, result);
  }
};
```

继承 `TVMFFIFunctionCell` 后，`FunctionObj` 的内存布局自动包含了 `safe_call` 和 `cpp_call` 字段，且位置与 C ABI 期望的偏移一致。`using` 声明将这两个字段提升为 `public` 可见性，供内部实现使用。

## FunctionObjImpl 的初始化

模板类 `FunctionObjImpl<TCallable>`（`function.h:159-200`）在构造时同时设置两个指针：

```cpp
explicit FunctionObjImpl(Args&&... args)
    : callable_(std::forward<Args>(args)...) {
  this->safe_call = SafeCall;
  this->cpp_call = reinterpret_cast<void*>(CppCall);
}
```

- `CppCall`（`function.h:184-186`）直接转发调用到存储的 `callable_`，不捕获异常。
- `SafeCall`（`function.h:189-196`）使用 `TVM_FFI_SAFE_CALL_BEGIN()` / `TVM_FFI_SAFE_CALL_END()` 宏包裹对 `cpp_call` 的调用，捕获异常并设置 TLS 错误。

而 `ExternCFunctionObjImpl`（`function.h:216-237`）仅设置 `safe_call`，将 `cpp_call` 置为 `nullptr`：

```cpp
ExternCFunctionObjImpl(void* self, TVMFFISafeCallType safe_call,
                       void (*deleter)(void* self))
    : self_(self), safe_call_(safe_call), deleter_(deleter) {
  this->safe_call = SafeCall;
  this->cpp_call = nullptr;
}
```

## 设计分析

FunctionCell 的双指针设计体现了**安全与性能的分层**原则：

- `safe_call` 保证了跨语言调用的异常安全性，是稳定的 ABI 契约。
- `cpp_call` 为同语言（C++ 到 C++）调用提供了零开销的快速路径，避免了异常捕获和 TLS 操作的开销。

使用 `void*` 存储 `cpp_call` 而非具体的 C++ 函数指针类型，是为了让 `c_api.h` 保持纯 C 兼容性——该头文件可以被 C 编译器包含，不需要知道 C++ 的 `FunctionObj` 类型。这种类型擦除是 C ABI 稳定性的必要妥协。

## 相关概念

- [036 Packed Function 约定](036-packed-function-convention.md)：函数调用的整体约定
- [038 safe_call 与 cpp_call 双路径](038-safe-call-and-cpp-call.md)：双路径的详细调用逻辑
- [047 cpp_call 快速路径](047-cpp-call-fast-path.md)：快速路径的性能优化细节
- [039 C 回调函数创建](039-c-callback-creation.md)：纯 C 函数的创建方式
