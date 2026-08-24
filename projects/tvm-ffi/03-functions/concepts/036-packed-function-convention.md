---
type: Concept
title: "视角036：Packed Function 约定"
description: "分析 TVM FFI 中 Packed Function 的核心调用约定：统一的函数签名、类型擦除参数传递、返回值约定，以及该约定如何支撑跨语言互操作。"
tags:
  - function
  - packed-function
  - ffi
  - calling-convention
  - type-erasure
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-016, F-017, F-022, F-137, F-138, F-139, F-144
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - src/ffi/function.cc
---

# 视角036：Packed Function 约定

## 概述

Packed Function 是 TVM FFI 函数调用系统的基石约定。它定义了一种统一的函数签名模式：所有函数——无论其原始 C++ 签名如何——在 FFI 边界上都被抽象为接受类型擦除参数数组、返回类型擦除值的形式。这一约定使得 C++、Python、Rust 等不同语言能够以统一方式调用彼此的函数，而无需为每个函数签名生成特定的绑定代码。

## C ABI 层的 SafeCall 签名

在 C ABI 层，Packed Function 约定体现为 `TVMFFISafeCallType` 函数指针类型（`c_api.h:501`）：

```c
typedef int (*TVMFFISafeCallType)(void* handle,
                                  const TVMFFIAny* args,
                                  int32_t num_args,
                                  TVMFFIAny* result);
```

该签名包含四个要素：

1. **`handle`**：函数对象的不透明指针，用于访问闭包状态。对于无状态的纯 C 函数，此参数可为 `NULL`。
2. **`args`**：指向 `TVMFFIAny` 数组的指针，每个元素是一个 16 字节的类型擦除值，携带类型标签和数据负载。
3. **`num_args`**：参数数量，使被调用方能够进行参数数量校验。
4. **`result`**：输出参数，调用方预先分配 `TVMFFIAny` 并将其 `type_index` 初始化为 `kTVMFFINone`，被调用方写入返回值。

返回值为 `int` 错误码：0 表示成功，-1 表示发生异常，异常详情通过 TLS 机制获取（`c_api.h:486-487`）。

## C++ 层的 PackedArgs 封装

在 C++ 层，`PackedArgs` 类（`function.h:261`）对原始参数数组提供了更安全的封装：

```cpp
class PackedArgs {
 public:
  PackedArgs(const AnyView* data, int32_t size);
  int size() const;
  const AnyView* data() const;
  AnyView operator[](int i) const;
  PackedArgs Slice(int begin, int end = -1) const;

  template <typename... Args>
  static void Fill(AnyView* data, Args&&... args);
};
```

`PackedArgs` 的关键设计点：

- **非持有视图**：内部仅存储 `const AnyView* data_` 和 `int32_t size_`，不拥有参数内存，避免拷贝开销。
- **零成本索引**：`operator[]` 直接返回 `AnyView`，不进行类型转换，由被调用方决定如何解析每个参数。
- **静态填充**：`Fill` 方法利用模板变参和 `PackedArgsSetter` 在编译期展开参数，将任意 C++ 类型序列化为 `AnyView` 数组。

## Function::operator() 的统一调用

`Function` 类（`function.h:320`）的 `operator()` 是 Packed Function 约定在 C++ 侧的主要入口（`function.h:613-622`）：

```cpp
template <typename... Args>
TVM_FFI_INLINE Any operator()(Args&&... args) const {
  const int kNumArgs = sizeof...(Args);
  const int kArraySize = kNumArgs > 0 ? kNumArgs : 1;
  AnyView args_pack[kArraySize];
  PackedArgs::Fill(args_pack, std::forward<Args>(args)...);
  Any result;
  static_cast<FunctionObj*>(data_.get())->CallPacked(args_pack, kNumArgs, &result);
  return result;
}
```

该方法的执行流程为：

1. 在栈上分配 `AnyView` 数组（零参数时仍分配一个元素以避免零长数组）。
2. 通过 `PackedArgs::Fill` 将变参转发填充到数组中。
3. 调用 `FunctionObj::CallPacked` 执行实际调用。
4. 返回持有型 `Any` 对象，自动管理返回值的引用计数。

## CallPacked 内部路径

`FunctionObj::CallPacked`（`function.h:125-131`）实现了双路径调用逻辑：

```cpp
TVM_FFI_INLINE void CallPacked(const AnyView* args, int32_t num_args, Any* result) const {
  FCall call_ptr =
      this->cpp_call ? reinterpret_cast<FCall>(this->cpp_call) : CppCallDedirectToSafeCall;
  (*call_ptr)(this, args, num_args, result);
}
```

当 `cpp_call` 指针非空时，直接走 C++ 快速路径，异常直接传播；为空时回退到 `safe_call`，异常被捕获并转换为错误码。这种设计使得同一 `Function` 对象在跨 FFI 边界时使用安全路径，在 C++ 内部调用时使用快速路径。

## 设计分析

Packed Function 约定的核心价值在于**统一抽象**。传统 FFI 方案通常需要为每个函数签名生成桥接代码（如 SWIG 的类型映射），而 Packed Function 将所有签名归一化为同一形式，使得：

- **注册简单**：函数只需符合 `void(const AnyView*, int32_t, Any*)` 签名即可注册，无需代码生成。
- **动态分发**：函数名到函数对象的映射在运行时解析，支持动态加载和热插拔。
- **跨语言一致**：Python 端的 `__call__`、Rust 端的 `call`、C 端的 `TVMFFIFunctionCall` 都遵循同一参数传递约定。

代价是调用侧需要进行类型擦除和重建，引入少量运行时开销。但 `cpp_call` 快速路径和强制内联（`TVM_FFI_INLINE`）在 C++ 内部调用时将此开销降至最低。

## 相关概念

- [037 FunctionCell 函数单元](037-function-cell.md)：函数对象的内存布局
- [038 safe_call 与 cpp_call 双路径](038-safe-call-and-cpp-call.md)：异常安全与性能的权衡
- [043 参数传递约定](043-argument-passing-convention.md)：AnyView 数组的序列化细节
- [044 返回值约定](044-return-value-convention.md)：Any 返回值的语义
