---
type: Concept
title: "视角046：TLS 错误传播"
description: "分析 TVM FFI 基于线程局部存储（TLS）的错误传播机制：TVMFFIErrorSetRaised/MoveFromRaised 的移动语义、SetSafeCallRaised/MoveFromSafeCallRaised 的 C++ 封装，以及该设计对编译器代码生成的简化。"
tags:
  - function
  - tls
  - error-propagation
  - thread-local-storage
  - c-abi
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-026, F-061
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/error.h
    - include/tvm/ffi/function.h
    - src/ffi/function.cc
---

# 视角046：TLS 错误传播

## 概述

TVM FFI 选择 TLS（Thread-Local Storage，线程局部存储）作为跨 FFI 边界传播错误信息的机制，而非通过函数参数传递错误对象。C ABI 函数通过返回值 -1 表示错误，错误详情存储在发起调用的线程的 TLS 中，调用方通过 `TVMFFIErrorMoveFromRaised` 取回。这种设计简化了编译器代码生成中的错误传播链，避免了在每个函数签名中添加错误参数，同时保证了线程安全。

## 核心 C API

### TVMFFIErrorSetRaised

`TVMFFIErrorSetRaised` 定义在 `c_api.h:760`：

```c
TVM_FFI_DLL void TVMFFIErrorSetRaised(TVMFFIObjectHandle error);
```

该函数将一个错误对象句柄存入当前线程的 TLS。语义要点：

1. **所有权转移**：调用后，错误对象的所有权从调用方转移给 TLS。调用方不应再使用该句柄。
2. **覆盖语义**：如果 TLS 中已有未取出的错误，新错误会替换旧错误（旧错误被释放）。
3. **线程绑定**：错误仅对设置它的线程可见，其他线程调用 `MoveFromRaised` 不受影响。

### TVMFFIErrorMoveFromRaised

`TVMFFIErrorMoveFromRaised` 定义在 `c_api.h:754`：

```c
TVM_FFI_DLL void TVMFFIErrorMoveFromRaised(TVMFFIObjectHandle* result);
```

该函数从当前线程的 TLS 取出错误对象：

1. **移动语义**：函数名中的 "Move" 表示这是所有权移动操作——取出后 TLS 被清空。
2. **输出参数**：错误句柄通过 `result` 指针返回。如果 TLS 中无错误，`*result` 被设为 NULL。
3. **所有权转移**：取回的错误对象所有权转移给调用方，调用方负责最终释放。

### 字符串便捷函数

除了接收完整对象句柄的 API，还有两个直接从字符串创建错误的便捷函数：

```c
TVM_FFI_DLL void TVMFFIErrorSetRaisedFromCStr(
    const char* kind, const char* message);

TVM_FFI_DLL void TVMFFIErrorSetRaisedFromCStrParts(
    const char* kind, const char** message_parts, int32_t num_parts);
```

`FromCStrParts` 版本（`c_api.h:793-794`）接受多段消息片段，在内部拼接。源码注释说明了设计动机（`c_api.h:773-787`）：编译器可以将常见的错误消息部分（如函数签名）存储为全局字符串复用于多个错误报告，减少存储开销。

## C++ 层封装

### SetSafeCallRaised

`SetSafeCallRaised`（`error.h:335-337`）是 C++ 侧的设置函数：

```cpp
TVM_FFI_INLINE void SetSafeCallRaised(const Error& error) {
  TVMFFIErrorSetRaised(
      details::ObjectUnsafe::TVMFFIObjectPtrFromObjectRef(error));
}
```

它将 `Error` 对象引用转换为 C 句柄并调用 C API。由于 `Error` 是 `ObjectRef` 的子类，转换仅涉及指针提取，不增加引用计数——符合"所有权转移给 TLS"的语义。

### MoveFromSafeCallRaised

`MoveFromSafeCallRaised`（`error.h:324-329`）是 C++ 侧的取回函数：

```cpp
TVM_FFI_INLINE Error MoveFromSafeCallRaised() {
  TVMFFIObjectHandle handle;
  TVMFFIErrorMoveFromRaised(&handle);
  return details::ObjectUnsafe::ObjectRefFromObjectPtr<Error>(
      details::ObjectUnsafe::ObjectPtrFromOwned<Object>(
          static_cast<TVMFFIObject*>(handle)));
}
```

它从 TLS 取回句柄，构造一个持有所有权的 `Error` 对象返回。如果 TLS 中无错误（handle 为 NULL），返回的 `Error` 将为空引用。

## 在 SAFE_CALL 宏中的使用

### 异常捕获路径

`TVM_FFI_SAFE_CALL_END` 宏（`function.h:79-89`）在 catch 块中使用 TLS：

```cpp
catch (const ::tvm::ffi::Error& err) {
  ::tvm::ffi::details::SetSafeCallRaised(err);
  return -1;
}
catch (const std::exception& ex) {
  ::tvm::ffi::details::SetSafeCallRaised(
      ::tvm::ffi::Error("InternalError", ex.what(), ""));
  return -1;
}
```

捕获到异常后，错误对象被存入 TLS，函数返回 -1。异常本身的栈展开在此终止，不会跨越 C ABI 边界。

### 异常重建路径

`TVM_FFI_CHECK_SAFE_CALL` 宏（`function.h:101-107`）在调用侧使用 TLS：

```cpp
#define TVM_FFI_CHECK_SAFE_CALL(func)              \
  {                                                \
    int ret_code = (func);                         \
    if (TVM_FFI_PREDICT_FALSE(ret_code != 0)) {    \
      throw ::tvm::ffi::details::MoveFromSafeCallRaised(); \
    }                                              \
  }
```

当 safe_call 返回非零值时，从 TLS 取回错误对象并作为 C++ 异常重新抛出。这完成了"C++ 异常 → C 错误码 + TLS → C++ 异常"的往返。

## 调用链中的错误传播

TLS 机制在链式调用中表现自然。考虑以下调用链：

```
C++ 函数 A → TVMFFIFunctionCall → safe_call(B) → C++ 函数 B
                                                         ↓
                                                    抛出异常
                                                         ↓
                                              B 的 SAFE_CALL 捕获
                                                         ↓
                                              SetSafeCallRaised(err)
                                              return -1
                                                         ↓
                                    TVMFFIFunctionCall 返回 -1
                                                         ↓
                              A 的 CHECK_SAFE_CALL 检测到 -1
                                                         ↓
                              MoveFromSafeCallRaised() → throw
```

每一层 safe_call 边界都独立地执行"捕获→存入TLS→返回-1"和"检测-1→取出TLS→抛出"的转换。如果中间有多层 FFI 边界，错误对象在 TLS 中被反复存取但保持完整信息。

源码注释明确说明了选择 TLS 的原因（`c_api.h:489-494`）：

> We decided to leverage TVMFFIErrorMoveFromRaised and TVMFFIErrorSetRaised for C function error propagation. This design choice, while introducing a dependency for TLS runtime, simplifies error propagation in chains of calls in compiler codegen. As we do not need to propagate error through argument but simply set them in the runtime environment.

## 线程安全考量

TLS 的核心优势是线程安全：

1. **无锁设计**：每个线程有独立的错误槽位，多线程同时设置/取回错误不需要互斥锁。
2. **无串扰**：线程 A 的错误不会被线程 B 看到，即使它们调用同一个函数。
3. **异常安全**：C++ 异常本身就是基于线程的，TLS 错误自然匹配异常的线程语义。

但也有约束：

1. **错误必须在同一线程取回**：如果线程 A 设置错误后线程 B 调用 `MoveFromRaised`，B 拿不到 A 的错误。
2. **不可重入嵌套**：在处理一个错误的过程中（catch 块内），如果再次调用可能设置错误的函数，新错误会覆盖尚未处理的旧错误。
3. **Fork 安全**：`GlobalFunctionTable` 使用裸 new 单例的部分原因就是 fork 后 TLS 状态可能不一致（`function.cc:132-135`）。

## 与 Errno 模式的对比

TLS 错误传播与 C 标准库的 `errno` 模式相似但有关键区别：

| 特性 | errno | TVM FFI TLS Error |
|------|-------|-------------------|
| 错误信息 | 整数错误码 | 完整对象（kind/message/traceback/cause） |
| 语义 | 粘性（需手动清零） | 移动语义（取出即清空） |
| 内存管理 | 无 | 引用计数对象 |
| 链式原因 | 不支持 | `cause_chain` 支持 |
| 栈回溯 | 不支持 | `backtrace` 字段 |

## 设计分析

TLS 错误传播是一种在 C ABI 约束下传递丰富错误信息的实用方案。相比通过输出参数传递错误对象（如 `int func(..., Error** err)`），TLS 方案：

- **简化代码生成**：编译器不需要为每个函数调用添加错误参数传递代码。
- **签名统一**：所有 C ABI 函数保持简洁签名，错误处理通过约定而非类型系统表达。
- **自然映射异常**：C++ 异常的线程语义与 TLS 完美匹配，转换机械且高效。

主要代价是：
- 引入 TLS 运行时依赖（所有现代平台都支持，包括 Windows 的 `__declspec(thread)` 和 POSIX 的 `__thread`）。
- 错误处理是隐式的，不如 Rust `Result` 类型那样在类型系统中强制处理。但在 C ABI 场景下，这是可接受的权衡。

## 相关概念

- [045 异常跨越 FFI 边界](045-exception-crossing-ffi.md)：TLS 机制在异常转换中的角色
- [038 safe_call 与 cpp_call 双路径](038-safe-call-and-cpp-call.md)：SAFE_CALL 宏如何使用 TLS
- [044 返回值约定](044-return-value-convention.md)：错误码 -1 与返回值的关系
- [040 全局函数注册表](040-global-function-registry.md)：注册表操作中的错误处理
