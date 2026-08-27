---
type: Concept
title: "视角039：C 回调函数创建"
description: "分析如何从纯 C 回调函数创建 TVM FFI Function 对象：TVMFFIFunctionCreate C API、FromExternC C++ 封装，以及资源句柄与 deleter 的生命周期管理。"
tags:
  - function
  - c-callback
  - extern-c
  - lifetime-management
  - ffi
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-059, F-140
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - src/ffi/function.cc
---

# 视角039：C 回调函数创建

## 概述

TVM FFI 不仅支持从 C++ lambda 创建函数对象，还提供了从纯 C 回调函数创建 `Function` 的能力。这一机制通过 `TVMFFIFunctionCreate` C API 和 `Function::FromExternC` C++ 封装实现，使得用 C 编写的函数——甚至来自其他编译器或语言编译的原生代码——可以无缝接入 FFI 函数注册表。核心设计涉及资源句柄（`self`）和删除器（`deleter`）的生命周期管理。

## C API：TVMFFIFunctionCreate

### 函数签名

`TVMFFIFunctionCreate` 定义在 `c_api.h:719-720`：

```c
TVM_FFI_DLL int TVMFFIFunctionCreate(
    void* self,
    TVMFFISafeCallType safe_call,
    void (*deleter)(void* self),
    TVMFFIObjectHandle* out);
```

参数说明：

| 参数 | 类型 | 用途 |
|------|------|------|
| `self` | `void*` | 传递给回调的资源句柄，可为 NULL |
| `safe_call` | `TVMFFISafeCallType` | C 风格的安全回调函数指针 |
| `deleter` | `void (*)(void*)` | 释放 `self` 资源的函数，可为 NULL |
| `out` | `TVMFFIObjectHandle*` | 输出创建的函数对象句柄 |

### 实现细节

该函数的实现在 `function.cc:146-152`：

```cpp
int TVMFFIFunctionCreate(void* self, TVMFFISafeCallType safe_call,
                         void (*deleter)(void* self),
                         TVMFFIObjectHandle* out) {
  TVM_FFI_SAFE_CALL_BEGIN();
  tvm::ffi::Function func =
      tvm::ffi::Function::FromExternC(self, safe_call, deleter);
  *out = tvm::ffi::details::ObjectUnsafe::
      MoveObjectRefToTVMFFIObjectPtr(std::move(func));
  TVM_FFI_SAFE_CALL_END();
}
```

实现非常简洁：委托给 C++ 层的 `FromExternC` 方法，然后将 `Function` 对象的所有权转移到 C 句柄。整个函数体被 `TVM_FFI_SAFE_CALL_BEGIN` / `TVM_FFI_SAFE_CALL_END` 包裹，确保 C++ 异常不会逃逸到 C 调用方。

## C++ 封装：Function::FromExternC

### 方法签名

`Function::FromExternC` 定义在 `function.h:392-402`：

```cpp
static Function FromExternC(void* self,
                            TVMFFISafeCallType safe_call,
                            void (*deleter)(void* self)) {
  Function func;
  if (self == nullptr && deleter == nullptr) {
    func.data_ = make_object<
        details::ExternCFunctionObjNullHandleImpl>(safe_call);
  } else {
    func.data_ = make_object<
        details::ExternCFunctionObjImpl>(self, safe_call, deleter);
  }
  return func;
}
```

该方法根据 `self` 和 `deleter` 是否同时为空，选择两种不同的实现类，以优化无状态回调的内存开销。

### ExternCFunctionObjNullHandleImpl

当 `self == nullptr && deleter == nullptr` 时，使用轻量实现（`function.h:205-211`）：

```cpp
class ExternCFunctionObjNullHandleImpl : public FunctionObj {
 public:
  explicit ExternCFunctionObjNullHandleImpl(
      TVMFFISafeCallType safe_call) {
    this->safe_call = safe_call;
    this->cpp_call = nullptr;
  }
};
```

该类不存储任何额外数据，仅将传入的 `safe_call` 指针存入继承的 `TVMFFIFunctionCell`。`cpp_call` 设为 `nullptr`，标记此函数来源于 C，C++ 调用时需通过 safe_call 回退路径。

适用于无状态的纯函数指针，如：

```c
extern "C" int my_add(void* self, const TVMFFIAny* args,
                      int32_t n, TVMFFIAny* result) {
  // 不使用 self，直接从 args 读取参数
  return 0;
}
```

### ExternCFunctionObjImpl

当需要闭包状态时，使用完整实现（`function.h:216-237`）：

```cpp
class ExternCFunctionObjImpl : public FunctionObj {
 public:
  ExternCFunctionObjImpl(void* self, TVMFFISafeCallType safe_call,
                         void (*deleter)(void* self))
      : self_(self), safe_call_(safe_call), deleter_(deleter) {
    this->safe_call = SafeCall;
    this->cpp_call = nullptr;
  }

  ~ExternCFunctionObjImpl() {
    if (deleter_) deleter_(self_);
  }

 private:
  static int32_t SafeCall(void* func, const TVMFFIAny* args,
                          int32_t num_args, TVMFFIAny* rv) {
    ExternCFunctionObjImpl* self =
        reinterpret_cast<ExternCFunctionObjImpl*>(func);
    return self->safe_call_(self->self_, args, num_args, rv);
  }

  void* self_;
  TVMFFISafeCallType safe_call_;
  void (*deleter_)(void* self);
};
```

关键设计点：

1. **间接调用**：对象自身的 `safe_call` 被设为静态方法 `SafeCall`，该方法从对象中取出原始的 `self_` 和 `safe_call_`，再转发调用。这是因为 C ABI 的 `safe_call` 接收 `void* handle` 作为第一参数，而该 handle 需要指向函数对象本身以访问闭包状态。

2. **RAII 资源管理**：析构函数调用 `deleter_(self_)` 释放外部资源。`deleter_` 为 NULL 时不调用，允许 `self_` 指向不需要释放的资源（如静态数据）。

3. **cpp_call 为 NULL**：与无状态版本一致，标记为 C 来源函数。

## 资源生命周期模式

### 无状态模式

```
self = NULL, deleter = NULL
```

函数对象不持有外部资源，析构时无额外清理。适用于纯函数指针。

### 所有权转移模式

```
self = malloc(...), deleter = free
```

调用方将资源所有权转移给 FFI 函数对象。函数对象析构时通过 `deleter` 释放资源。这是最常见的闭包模式。

### 借用模式

```
self = &global_data, deleter = NULL
```

`self` 指向比函数对象生命周期更长的资源（如全局变量、静态数据），不需要在析构时释放。

## 与 C++ Lambda 创建的对比

| 特性 | C 回调（FromExternC） | C++ Lambda（FromTyped/FromPacked） |
|------|----------------------|-----------------------------------|
| `cpp_call` | NULL（始终走 safe_call） | 非 NULL（支持快速路径） |
| 异常处理 | C 回调内部必须自行处理 | C++ lambda 可直接抛出异常 |
| 资源管理 | 通过 `self` + `deleter` 手动管理 | 通过 lambda 捕获自动管理 |
| 类型安全 | 手动解析 `TVMFFIAny` | 编译期类型检查 |
| 跨编译器 | 支持（纯 C ABI） | 需相同 C++ ABI |

## 设计分析

C 回调创建机制的核心价值在于**语言互操作性**。通过纯 C ABI，任何能编译为原生代码并遵循 C 调用约定的语言——C、Rust、Fortran、Zig 等——都可以创建可被 FFI 系统调用的函数对象。`self` + `deleter` 的设计是 C 语言中实现闭包的经典模式，与 `pthread_create` 的参数传递方式一脉相承。

两种实现类的分离（`NullHandleImpl` vs 完整 `Impl`）体现了对常见情况的优化：大多数 C 回调可能是无状态的函数指针，避免为每个函数分配额外的 `self_`、`safe_call_`、`deleter_` 字段（24 字节）是有意义的内存优化。

## 相关概念

- [037 FunctionCell 函数单元](037-function-cell.md)：函数对象的内存布局
- [042 Lambda 与回调](042-lambda-and-callbacks.md)：C++ lambda 的创建方式
- [036 Packed Function 约定](036-packed-function-convention.md)：统一的函数签名约定
- [040 全局函数注册表](040-global-function-registry.md)：函数注册与查找机制
