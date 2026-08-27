---
type: Concept
title: "视角044：返回值约定"
description: "分析 TVM FFI 的返回值处理机制：Any 持有型返回值、TVMFFIAny 输出参数、void 返回的编码方式，以及 CallExpected 的无异常返回路径。"
tags:
  - function
  - return-value
  - any
  - error-handling
  - expected
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-148
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - include/tvm/ffi/any.h
---

# 视角044：返回值约定

## 概述

TVM FFI 的函数返回值遵循与参数传递对称的类型擦除约定：所有函数在 C ABI 层通过输出参数 `TVMFFIAny* result` 返回结果，在 C++ 层返回持有型 `Any` 对象。void 返回通过 `kTVMFFITypeIndexNull` 类型标签编码。此外，`CallExpected` 方法提供了无异常的返回路径，将错误包装为 `Expected<T>` 类型。理解返回值约定对于正确实现跨语言函数和处理调用结果至关重要。

## C ABI 层的输出参数

### SafeCall 签名中的 result

在 C ABI 层，`TVMFFISafeCallType`（`c_api.h:501`）通过输出参数返回结果：

```c
typedef int (*TVMFFISafeCallType)(void* handle,
                                  const TVMFFIAny* args,
                                  int32_t num_args,
                                  TVMFFIAny* result);
```

`result` 是调用方预先分配的 `TVMFFIAny` 指针。被调用方负责：

1. **初始化检查**：调用方必须将 `result->type_index` 初始化为 `kTVMFFINone`（或更小的值）。被调用方通过 `TVM_FFI_ICHECK_LT` 验证此条件（`function.h:191`）。
2. **写入结果**：将返回值写入 `result` 指向的内存。
3. **所有权转移**：如果返回对象类型，被调用方将对象的所有权转移给调用方（通过指针传递，不额外增加引用计数）。

### 成功与失败

- 返回 0：`result` 包含有效返回值（或 `kTVMFFINone` 表示 void）。
- 返回 -1：`result` 保持 `kTVMFFINone`，错误信息通过 TLS 获取。

这种设计避免了在函数签名中同时返回值和错误，简化了 ABI。

## C++ 层的 Any 返回值

### Function::operator() 的返回

在 C++ 层，`Function::operator()`（`function.h:613-622`）返回 `Any`：

```cpp
template <typename... Args>
TVM_FFI_INLINE Any operator()(Args&&... args) const {
  AnyView args_pack[kArraySize];
  PackedArgs::Fill(args_pack, std::forward<Args>(args)...);
  Any result;
  static_cast<FunctionObj*>(data_.get())
      ->CallPacked(args_pack, kNumArgs, &result);
  return result;
}
```

`Any result` 是持有型容器（`any.h:560`），与非持有的 `AnyView` 不同：

- **构造时**：从 `AnyView` 构造时，对对象类型执行 `IncRef`。
- **析构时**：对对象类型执行 `DecRef`。
- **移动语义**：移动构造将源置为 null，避免引用计数操作。
- **拷贝语义**：自赋值安全，先增加新引用再减少旧引用。

### CallPacked 的结果写入

`FunctionObj::CallPacked`（`function.h:125-131`）接收 `Any* result` 指针：

```cpp
TVM_FFI_INLINE void CallPacked(const AnyView* args,
                               int32_t num_args,
                               Any* result) const {
  FCall call_ptr = this->cpp_call
      ? reinterpret_cast<FCall>(this->cpp_call)
      : CppCallDedirectToSafeCall;
  (*call_ptr)(this, args, num_args, result);
}
```

在 `cpp_call` 快速路径上，`Any*` 直接传递给 C++ 可调用对象。可调用对象通过 `rv->operator=(value)` 写入返回值。

## void 返回值的编码

C ABI 层没有专门的 void 表示——所有函数都必须写入 `result`。void 返回通过将 `result->type_index` 保持为 `kTVMFFINone` 来编码。

在 `TypedFunction<R(Args...)>` 的调用操作符中（`function.h:864-875`），void 返回类型有专门处理：

```cpp
TVM_FFI_INLINE R operator()(Args... args) const {
  if constexpr (std::is_same_v<R, void>) {
    packed_(std::forward<Args>(args)...);
  } else {
    Any res = packed_(std::forward<Args>(args)...);
    if constexpr (std::is_same_v<R, Any>) {
      return res;
    } else {
      return std::move(res).cast<R>();
    }
  }
}
```

- `R = void`：调用底层函数但不读取返回值。
- `R = Any`：直接返回 `Any`。
- 其他类型：从 `Any` 转换为目标类型。

在 `CallExpected<void>` 路径中（`function.h:676-686`），void 返回通过检查 `result.type_index() == kTVMFFINone` 判断：

```cpp
if constexpr (std::is_same_v<T, void>) {
  if (result.type_index() == TypeIndex::kTVMFFINone) {
    return Expected<void>();
  }
  if (auto err = result.template try_cast<Error>()) {
    return Unexpected(std::move(*err));
  }
  return Unexpected(Error("TypeError",
      "CallExpected: result type mismatch, expected void, but got "
      + result.GetTypeKey(), ""));
}
```

## 返回值类型转换

### Any::cast<T>

调用方通过 `Any::cast<T>()`（`any.h:780`）将类型擦除的返回值转换为具体类型。该方法委托给 `Cast<T>`（`cast.h:50`），执行：

- 基础类型：检查 `IsInt()`/`IsFloat()`/`IsBool()` 后直接转换。
- 字符串：检查 `IsString()` 或 `IsBytes()` 后构造 `std::string`。
- 对象类型：检查 `IsObject()` 后执行 `Downcast`。
- `Optional<T>`：允许 null 值。

转换失败时抛出 `TypeError`。

### Any::try_cast<T>

`try_cast<T>()`（`any.h:792`）返回 `std::optional<T>`，转换失败时返回 `std::nullopt` 而非抛出异常，适用于条件分支场景。

## CallExpected：无异常返回路径

`Function::CallExpected<T>`（`function.h:661-703`）提供了一种不使用 C++ 异常的调用方式：

```cpp
template <typename T = Any, typename... Args>
TVM_FFI_INLINE Expected<T> CallExpected(Args&&... args) const {
  AnyView args_pack[kArraySize];
  PackedArgs::Fill(args_pack, std::forward<Args>(args)...);

  Any result;
  FunctionObj* func_obj = static_cast<FunctionObj*>(data_.get());

  int ret_code = func_obj->safe_call(
      func_obj,
      reinterpret_cast<const TVMFFIAny*>(args_pack),
      kNumArgs,
      reinterpret_cast<TVMFFIAny*>(&result));

  if (ret_code == 0) {
    if constexpr (std::is_same_v<T, Any>) {
      return result;
    } else {
      // 尝试转换为 T，失败则检查是否为 Error
      if (auto val = result.template try_cast<T>()) {
        return *std::move(val);
      }
      if (auto err = result.template try_cast<Error>()) {
        return Unexpected(std::move(*err));
      }
      return Unexpected(Error("TypeError", ...));
    }
  } else {
    return Unexpected(details::MoveFromSafeCallRaised());
  }
}
```

关键设计：

1. **始终走 safe_call**：即使函数有 `cpp_call`，也通过 `safe_call` 调用以确保异常被捕获。
2. **双重错误检查**：`ret_code != 0` 表示 safe_call 捕获了异常；`ret_code == 0` 但结果是 `Error` 类型表示函数主动返回了错误对象。
3. **返回 `Expected<T>`**：包含成功值或 `Error`，类似 Rust 的 `Result<T, E>`。

## 返回值中的对象所有权

当返回值是对象类型时，所有权规则为：

1. **C ABI 层**：被调用方将对象指针写入 `result->v_handle`，不增加引用计数。所有权从被调用方转移到调用方。
2. **C++ Any 构造**：`Any` 从 `TVMFFIAny` 构造时接管对象指针，不增加引用计数（移动语义）。
3. **Any 析构**：`Any` 析构时减少引用计数，如果计数归零则释放对象。
4. **Any 拷贝**：拷贝 `Any` 时增加引用计数，两个 `Any` 共同拥有对象。

这确保了零额外引用计数操作的返回路径——从被调用方到调用方的转移是一次指针移动。

## 设计分析

返回值约定与参数传递约定形成对称设计：

- 参数通过 `const TVMFFIAny*` 输入（只读，非持有视图）。
- 返回值通过 `TVMFFIAny*` 输出（可写，所有权转移）。
- 两者都使用 16 字节的 `TVMFFIAny` 作为统一载体。

`Any` 与 `AnyView` 的区分是关键设计：参数使用非持有视图以避免调用路径上的引用计数开销，返回值使用持有容器以确保对象生命周期安全。这种"输入借用、输出拥有"的模式在 Rust 的所有权系统中也有对应，但在 C++ 中通过值语义和 RAII 实现。

`CallExpected` 路径为禁用异常的编译环境（如某些嵌入式系统或游戏引擎）提供了替代方案，同时不影响默认路径的性能。

## 相关概念

- [043 参数传递约定](043-argument-passing-convention.md)：对称的输入参数机制
- [038 safe_call 与 cpp_call 双路径](038-safe-call-and-cpp-call.md)：返回路径中的异常处理
- [045 异常跨越 FFI 边界](045-exception-crossing-ffi.md)：错误返回值的完整流程
- [046 TLS 错误传播](046-tls-error-propagation.md)：safe_call 错误的 TLS 存储
