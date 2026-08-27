---
type: Concept
title: "视角038：safe_call 与 cpp_call 双路径"
description: "深入分析 TVM FFI 函数对象的两条调用路径：safe_call 的异常捕获机制与 cpp_call 的直接异常传播，以及 CallPacked 如何在两者间无分支选择。"
tags:
  - function
  - safe-call
  - cpp-call
  - exception-handling
  - dual-path
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-016, F-139
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - src/ffi/function.cc
---

# 视角038：safe_call 与 cpp_call 双路径

## 概述

TVM FFI 的每个函数对象都携带两个函数指针：`safe_call` 和 `cpp_call`。这两个指针代表了两种不同的异常传播策略，构成了函数调用的双路径架构。`safe_call` 在 C ABI 边界捕获所有异常并转换为错误码，`cpp_call` 则允许异常直接传播以获得最佳性能。`FunctionObj::CallPacked` 通过一个条件表达式在两条路径间选择，实现了安全性与性能的统一。

## safe_call：异常安全路径

### 签名与契约

`safe_call` 的类型为 `TVMFFISafeCallType`（`c_api.h:501-502`）：

```c
typedef int (*TVMFFISafeCallType)(void* handle,
                                  const TVMFFIAny* args,
                                  int32_t num_args,
                                  TVMFFIAny* result);
```

契约要点（`c_api.h:479-487`）：

- 调用方必须将 `result->type_index` 初始化为 `kTVMFFINone` 或更小的值。
- 返回 0 表示成功，返回 -1 表示发生异常。
- 异常详情通过 `TVMFFIErrorMoveFromRaised` 从 TLS 中获取。

### 异常捕获实现

在 `FunctionObjImpl<TCallable>::SafeCall`（`function.h:189-196`）中，safe_call 的实现使用宏包裹实际调用：

```cpp
static int SafeCall(void* func, const TVMFFIAny* args,
                    int32_t num_args, TVMFFIAny* result) {
  TVM_FFI_SAFE_CALL_BEGIN();
  TVM_FFI_ICHECK_LT(result->type_index,
                    TypeIndex::kTVMFFIStaticObjectBegin);
  FunctionObj* self = static_cast<FunctionObj*>(func);
  reinterpret_cast<FCall>(self->cpp_call)(
      self, reinterpret_cast<const AnyView*>(args),
      num_args, reinterpret_cast<Any*>(result));
  TVM_FFI_SAFE_CALL_END();
}
```

`TVM_FFI_SAFE_CALL_BEGIN` 和 `TVM_FFI_SAFE_CALL_END` 宏（`function.h:72-89`）展开为 try-catch 块：

```cpp
#define TVM_FFI_SAFE_CALL_BEGIN() try { (void)0

#define TVM_FFI_SAFE_CALL_END()                                  \
  return 0;                                                      \
  }                                                              \
  catch (const ::tvm::ffi::Error& err) {                         \
    ::tvm::ffi::details::SetSafeCallRaised(err);                 \
    return -1;                                                   \
  }                                                              \
  catch (const std::exception& ex) {                             \
    ::tvm::ffi::details::SetSafeCallRaised(                      \
        ::tvm::ffi::Error("InternalError", ex.what(), ""));      \
    return -1;                                                   \
  }
```

捕获逻辑分两层：
1. **`tvm::ffi::Error`**：FFI 原生异常，直接存入 TLS。
2. **`std::exception`**：标准库异常，包装为 `InternalError` 类型后存入 TLS。

### C ABI 入口

`TVMFFIFunctionCall`（`function.cc:191-204`）是 C ABI 层的调用入口，它直接委托给 `safe_call`：

```cpp
int TVMFFIFunctionCall(TVMFFIObjectHandle func, TVMFFIAny* args,
                       int32_t num_args, TVMFFIAny* result) {
#ifdef _MSC_VER
  volatile int ret = reinterpret_cast<FunctionObj*>(func)
      ->safe_call(func, args, num_args, result);
  return ret;
#else
  return reinterpret_cast<FunctionObj*>(func)
      ->safe_call(func, args, num_args, result);
#endif
}
```

MSVC 版本使用 `volatile int` 防止尾调用优化，确保调用栈中保留该函数帧以可靠检测 FFI 边界（`function.cc:194-197`）。

## cpp_call：C++ 快速路径

### 签名与优势

`cpp_call` 的实际类型为 `FunctionObj::FCall`（`function.h:116`）：

```cpp
using FCall = void (*)(const FunctionObj*, const AnyView*, int32_t, Any*);
```

与 safe_call 相比，cpp_call 路径具有以下优势：

1. **无异常捕获开销**：不设置 try-catch 块，异常直接沿调用栈传播。
2. **无 TLS 操作**：不涉及 `TVMFFIErrorSetRaised` / `TVMFFIErrorMoveFromRaised`。
3. **类型更明确**：首参数为 `const FunctionObj*`，无需 `void*` 转换。
4. **返回值为 void**：不返回错误码，减少一次分支判断。

### 直接调用实现

`FunctionObjImpl<TCallable>::CppCall`（`function.h:184-186`）是最简单的转发：

```cpp
static void CppCall(const FunctionObj* func, const AnyView* args,
                    int32_t num_args, Any* result) {
  (static_cast<const TSelf*>(func))->callable_(args, num_args, result);
}
```

该函数仅将调用转发给存储的 `callable_` 对象，不做任何异常处理。

## CallPacked 的路径选择

`FunctionObj::CallPacked`（`function.h:125-131`）是两条路径的汇合点：

```cpp
TVM_FFI_INLINE void CallPacked(const AnyView* args,
                               int32_t num_args,
                               Any* result) const {
  FCall call_ptr =
      this->cpp_call
          ? reinterpret_cast<FCall>(this->cpp_call)
          : CppCallDedirectToSafeCall;
  (*call_ptr)(this, args, num_args, result);
}
```

这里使用三元条件表达式而非 if-else，源码注释说明这是为了让编译器生成**无分支（branchless）**的选择代码（`function.h:127`）。选择逻辑为：

- `cpp_call != NULL`：函数由 C++ 创建，直接走快速路径。
- `cpp_call == NULL`：函数来源于纯 C 回调，走 `CppCallDedirectToSafeCall` 回退路径。

### CppCallDedirectToSafeCall 回退

当 `cpp_call` 为空时，`CppCallDedirectToSafeCall`（`function.h:143-148`）将调用重定向到 `safe_call`：

```cpp
static void CppCallDedirectToSafeCall(const FunctionObj* func,
                                      const AnyView* args,
                                      int32_t num_args,
                                      Any* rv) {
  FunctionObj* self = const_cast<FunctionObj*>(func);
  TVM_FFI_CHECK_SAFE_CALL(
      self->safe_call(self,
                      reinterpret_cast<const TVMFFIAny*>(args),
                      num_args,
                      reinterpret_cast<TVMFFIAny*>(rv)));
}
```

`TVM_FFI_CHECK_SAFE_CALL` 宏（`function.h:101-107`）检查 safe_call 返回值，非零时抛出从 TLS 恢复的异常：

```cpp
#define TVM_FFI_CHECK_SAFE_CALL(func)              \
  {                                                \
    int ret_code = (func);                         \
    if (TVM_FFI_PREDICT_FALSE(ret_code != 0)) {    \
      throw ::tvm::ffi::details::MoveFromSafeCallRaised(); \
    }                                              \
  }
```

这样，即使函数来源于纯 C，从 C++ 侧调用时异常也能以 C++ 异常的形式正常传播。

## 设计分析

双路径设计的精妙之处在于**同一函数对象支持两种调用语义**：

- 跨 FFI 边界（Python/Rust/C 调用 C++）时，通过 `TVMFFIFunctionCall` 走 safe_call，异常被转换为错误码和 TLS 状态。
- C++ 内部调用时，通过 `Function::operator()` → `CallPacked` 走 cpp_call，异常直接传播，零额外开销。

这种设计避免了传统 FFI 方案中"所有调用都必须付出异常捕获代价"的性能问题，同时保持了 ABI 的安全性。`cpp_call` 为 NULL 时的回退机制确保了纯 C 函数也能无缝融入 C++ 异常体系。

## 相关概念

- [037 FunctionCell 函数单元](037-function-cell.md)：双指针的内存布局
- [045 异常跨越 FFI 边界](045-exception-crossing-ffi.md)：异常转换的完整流程
- [047 cpp_call 快速路径](047-cpp-call-fast-path.md)：快速路径的性能分析
- [046 TLS 错误传播](046-tls-error-propagation.md)：TLS 错误存储机制
