---
type: Concept
title: "视角045：异常跨越 FFI 边界"
description: "分析 C++ 异常如何在 FFI 边界被捕获、转换为错误码和 TLS 错误对象，再在另一侧重建为异常的完整流程：SAFE_CALL 宏、ErrorCell 结构、ErrorMoveFromRaised 机制。"
tags:
  - function
  - exception
  - ffi-boundary
  - error-handling
  - tls
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-028, F-029, F-030, F-031, F-032, F-213
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - include/tvm/ffi/error.h
    - src/ffi/function.cc
---

# 视角045：异常跨越 FFI 边界

## 概述

C++ 异常无法直接跨越 C ABI 边界传播——C 语言没有异常概念，且不同编译器的异常 ABI 不兼容。TVM FFI 通过"捕获 → 序列化到 TLS → 错误码返回 → 反序列化 → 重新抛出"的流程，在保持 C ABI 稳定性的同时实现了异常信息的跨边界传递。这一机制由 `TVM_FFI_SAFE_CALL_BEGIN`/`END` 宏、`TVMFFIErrorCell` 结构、`TVMFFIErrorMoveFromRaised`/`TVMFFIErrorSetRaised` C API 和 `Error` C++ 类共同协作完成。

## C++ 侧：异常捕获

### SAFE_CALL 宏

在函数实现的 C++ 侧，`TVM_FFI_SAFE_CALL_BEGIN()` 和 `TVM_FFI_SAFE_CALL_END()` 宏（`function.h:72-89`）包裹可能抛出异常的代码：

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

两层 catch 块处理不同异常类型：

1. **`tvm::ffi::Error`**：FFI 原生异常类型，保留完整的 kind、message、traceback、cause chain 和 extra context。直接传递给 TLS。
2. **`std::exception`**：标准库异常，包装为 `InternalError` 类型，`what()` 作为 message。

`SetSafeCallRaised`（`error.h:335-337`）将异常存入 TLS：

```cpp
TVM_FFI_INLINE void SetSafeCallRaised(const Error& error) {
  TVMFFIErrorSetRaised(
      details::ObjectUnsafe::TVMFFIObjectPtrFromObjectRef(error));
}
```

### FunctionObjImpl::SafeCall 中的应用

`FunctionObjImpl<TCallable>::SafeCall`（`function.h:189-196`）是这一模式的典型应用：

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

注意它在 try 块内首先检查 `result->type_index` 的前置条件，然后委托给 `cpp_call` 执行实际逻辑。如果 `cpp_call` 抛出异常，宏的 catch 块负责捕获。

### TVM_FFI_CHECK_SAFE_CALL：调用侧检查

在调用 C ABI safe_call 的 C++ 代码中，`TVM_FFI_CHECK_SAFE_CALL` 宏（`function.h:101-107`）检查返回码：

```cpp
#define TVM_FFI_CHECK_SAFE_CALL(func)              \
  {                                                \
    int ret_code = (func);                         \
    if (TVM_FFI_PREDICT_FALSE(ret_code != 0)) {    \
      throw ::tvm::ffi::details::MoveFromSafeCallRaised(); \
    }                                              \
  }
```

`TVM_FFI_PREDICT_FALSE` 提示编译器错误路径是冷代码，优化正常路径的分支预测。当 `ret_code != 0` 时，`MoveFromSafeCallRaised()`（`error.h:324-329`）从 TLS 取回错误对象并抛出：

```cpp
TVM_FFI_INLINE Error MoveFromSafeCallRaised() {
  TVMFFIObjectHandle handle;
  TVMFFIErrorMoveFromRaised(&handle);
  return details::ObjectUnsafe::ObjectRefFromObjectPtr<Error>(
      details::ObjectUnsafe::ObjectPtrFromOwned<Object>(
          static_cast<TVMFFIObject*>(handle)));
}
```

## C ABI 层：错误存储与传递

### TVMFFIErrorCell 结构

错误对象在 C ABI 层的布局由 `TVMFFIErrorCell` 定义（`c_api.h:430-465`）：

```c
typedef struct {
  TVMFFIByteArray kind;
  TVMFFIByteArray message;
  TVMFFIByteArray backtrace;
  void (*update_backtrace)(TVMFFIObjectHandle self,
                           const TVMFFIByteArray* backtrace,
                           int32_t update_mode);
  TVMFFIObjectHandle cause_chain;
  TVMFFIObjectHandle extra_context;
} TVMFFIErrorCell;
```

| 字段 | 用途 |
|------|------|
| `kind` | 错误类别（如 "ValueError"、"TypeError"、"InternalError"） |
| `message` | 人类可读的错误描述 |
| `backtrace` | 栈回溯字符串 |
| `update_backtrace` | 更新回溯的函数指针（支持替换/追加模式） |
| `cause_chain` | 导致当前错误的链式原因（可为 NULL） |
| `extra_context` | 附加上下文对象（可为 NULL） |

`TVMFFIByteArray` 是 `{const char* data; size_t size}` 的简单结构，不拥有内存。实际的字符串数据由 `ErrorObjFromStd`（`error.h:88-123`）持有。

### 错误创建 C API

`TVMFFIErrorCreate`（`c_api.h:809-810`）创建基础错误对象：

```c
TVM_FFI_DLL int TVMFFIErrorCreate(
    const TVMFFIByteArray* kind,
    const TVMFFIByteArray* message,
    const TVMFFIByteArray* backtrace,
    TVMFFIObjectHandle* out);
```

`TVMFFIErrorCreateWithCauseAndExtraContext`（`c_api.h:822-824`）创建带因果链和附加上下文的完整错误对象。

### TLS 错误设置与获取

两个核心 C API 管理线程局部错误状态（`c_api.h:754-760`）：

```c
TVM_FFI_DLL void TVMFFIErrorMoveFromRaised(TVMFFIObjectHandle* result);
TVM_FFI_DLL void TVMFFIErrorSetRaised(TVMFFIObjectHandle error);
```

- `TVMFFIErrorSetRaised`：将错误对象存入当前线程的 TLS。调用后，错误对象的所有权转移给 TLS。
- `TVMFFIErrorMoveFromRaised`：从 TLS 取出错误对象并清空 TLS。返回的句柄所有权转移给调用方。函数名中的 "Move" 表示这是所有权移动操作，TLS 在取出后不再持有引用。

还有便捷函数 `TVMFFIErrorSetRaisedFromCStr`（`c_api.h:768`）和 `TVMFFIErrorSetRaisedFromCStrParts`（`c_api.h:793`），允许 C 代码直接从字符串设置错误，无需手动创建 Error 对象。

## C++ 侧：Error 类

### 类层次

`ErrorObj`（`error.h:65-85`）继承自 `Object` 和 `TVMFFIErrorCell`，是错误对象的 C++ 实现：

```cpp
class ErrorObj : public Object, public TVMFFIErrorCell {
 public:
  ErrorObj() {
    this->cause_chain = nullptr;
    this->extra_context = nullptr;
  }
  ~ErrorObj() {
    if (this->cause_chain != nullptr)
      details::ObjectUnsafe::DecRefObjectHandle(this->cause_chain);
    if (this->extra_context != nullptr)
      details::ObjectUnsafe::DecRefObjectHandle(this->extra_context);
  }
  static constexpr const int32_t _type_index = TypeIndex::kTVMFFIError;
  // ...
};
```

`Error` 类（`error.h:130`）是托管引用，同时继承 `std::exception`：

```cpp
class Error : public ObjectRef, public std::exception {
 public:
  Error(std::string kind, std::string message, std::string backtrace);
  const char* what() const noexcept override;
  const String& kind() const;
  const String& message() const;
  const String& traceback() const;
  ObjectRef cause() const;
  const String& extra_context() const;
  Error WithContext(const std::string& context) const;
};
```

继承 `std::exception` 使得 `Error` 可以被 `catch (const std::exception&)` 捕获，这也是 SAFE_CALL 宏第二层 catch 能处理它的原因。

### ErrorBuilder

`ErrorBuilder`（`error.h:339`）提供链式构建错误的 API：

```cpp
throw ErrorBuilder("ValueError", backtrace, log_before_throw)
    .kind("ValueError")
    .message("Invalid argument")
    .cause(original_error)
    .extra_context(context_obj)
    .Raise();
```

### EnvErrorAlreadySet

`EnvErrorAlreadySet`（`error.h:316`）是一种特殊错误，用于表示宿主环境（如 Python 解释器）中已有错误设置，FFI 层不应覆盖。这在 Python 回调中发生信号（如 Ctrl+C）时使用。

## 完整的异常跨越流程

以"Python 调用 C++ 函数，C++ 抛出异常"为例：

```
Python 代码
    ↓
PyFunction.__call__ (Cython)
    ↓
TVMFFIFunctionCall (C ABI, function.cc:191)
    ↓
FunctionObj::safe_call (function.h:189)
    ↓
TVM_FFI_SAFE_CALL_BEGIN() → try {
    ↓
FunctionObj::cpp_call → 实际 C++ 逻辑
    ↓
抛出 tvm::ffi::Error
    ↓
} catch (const Error& err) {
    SetSafeCallRaised(err) → TVMFFIErrorSetRaised(handle)
    return -1;
}
    ↓
TVMFFIFunctionCall 返回 -1
    ↓
Python 绑定检查返回码 -1
    ↓
TVMFFIErrorMoveFromRaised(&handle)
    ↓
从 handle 构造 Python 异常
    ↓
Python 层收到异常
```

关键特性：

1. **异常类型保留**：`kind` 字段映射到 Python 异常类型（ValueError→ValueError，TypeError→TypeError 等）。
2. **回溯完整**：C++ 栈回溯被捕获并传递到 Python，可以与 Python 回溯拼接。
3. **因果链**：`cause_chain` 允许嵌套错误，保留根本原因。
4. **线程安全**：TLS 确保多线程环境下错误不串扰。

## NPU 建议

在 NPU 加速场景中，异常跨越 FFI 边界的机制需特别注意：

1. **NPU 驱动回调中的异常安全**：NPU 驱动通常通过 C 回调通知完成事件。如果在回调中需要报告错误，**禁止直接抛出 C++ 异常**——驱动栈帧可能不是 C++ 编译的，异常会导致未定义行为。应使用 `TVMFFIErrorSetRaisedFromCStr` 将错误存入 TLS，然后通过返回值 -1 通知调用方。

2. **异步错误的延迟传递**：NPU 异步执行的错误可能在提交命令后的任意时刻发生。建议在命令队列中维护错误状态，在 `Function::safe_call` 入口处检查前序异步错误，通过 `TVMFFIErrorSetRaised` 设置后返回 -1。不要尝试从 NPU 中断处理程序中调用 FFI 错误 API——TLS 在中断上下文中不可用。

3. **NPU 错误码到 FFI Error 的映射**：建立 NPU 驱动错误码到 FFI `ErrorKind` 的映射表。设备硬件错误建议映射为 `RuntimeError`，参数校验错误映射为 `ValueError`，内存不足映射为 `InternalError`。使用 `TVMFFIErrorCreateWithCauseAndExtraContext` 在 `extra_context` 中携带 NPU 特定的诊断信息（如寄存器快照、命令序列号）。

4. **命令队列中的异常隔离**：当 NPU 命令队列中的某个内核失败时，应通过 `cause_chain` 保留原始 NPU 错误，并在上层包装为更高级别的错误（如"模型推理失败"）。避免直接在 NPU 工作线程中抛出跨线程异常——通过 `std::promise<Error>` 或无锁错误队列将错误传递回调用线程，再由 FFI 边界抛出。

5. **注意事项**：
   - `TVMFFIErrorSetRaised` 会转移对象所有权，不要在调用后继续使用错误对象。
   - `TVMFFIErrorMoveFromRaised` 会清空 TLS，重复调用将返回空句柄。
   - 在 NPU 性能关键路径上，异常路径应保持冷代码（使用 `TVM_FFI_PREDICT_FALSE`），正常命令提交路径不应有 try-catch 开销。
   - 如果 NPU 运行时编译为 `-fno-exceptions`，使用 `CallExpected` API 而非异常路径。

## 设计分析

异常跨越 FFI 边界的设计核心是**错误信息的序列化与重建**。C++ 异常是语言内建的、基于栈展开的机制，无法直接表示为 C 数据结构。TVM FFI 将异常的关键信息（kind、message、backtrace、cause、context）提取为 C 结构体，通过 TLS 传递，在另一侧重建为对应语言的异常对象。

选择 TLS 而非通过函数参数传递错误，有两个原因（`c_api.h:489-494`）：
1. 简化编译器代码生成中的错误传播链——不需要在每个函数签名中添加错误参数。
2. 错误信息在运行时环境中自然流动，调用方只需在 FFI 边界检查一次。

这种设计的代价是引入了 TLS 运行时依赖，但在现代系统中 TLS 的性能开销极低（通常通过编译器内联的线程指针访问），且错误路径本身是冷路径。

## 相关概念

- [038 safe_call 与 cpp_call 双路径](038-safe-call-and-cpp-call.md)：异常在两条路径上的不同处理
- [046 TLS 错误传播](046-tls-error-propagation.md)：TLS 错误存储的详细机制
- [044 返回值约定](044-return-value-convention.md)：错误码与返回值的关系
- [040 全局函数注册表](040-global-function-registry.md)：函数注册中的异常处理
