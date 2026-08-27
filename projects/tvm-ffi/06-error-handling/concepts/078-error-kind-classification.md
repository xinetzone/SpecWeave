---
type: Concept
title: "视角078：ErrorKind 错误类型分类"
description: "分析 TVM FFI 的错误类型分类体系：kind 字符串字段的设计、标准错误类型（RuntimeError/ValueError/TypeError 等）、Python/Rust 绑定的类型映射表，以及自定义错误类型的注册机制。"
tags:
  - error-handling
  - error-kind
  - error-classification
  - cross-language
  - type-mapping
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-210, F-211, F-212
  - code:
    - include/tvm/ffi/error.h
    - python/tvm_ffi/error.py
    - rust/tvm-ffi/src/error.rs
---

# 视角078：ErrorKind 错误类型分类

## 概述

TVM FFI 使用字符串类型的 `kind` 字段对错误进行分类，而非整数错误码或 C++ RTTI。这种设计使得错误类型可以在不修改 ABI 的情况下动态扩展，并且天然支持跨语言映射——每种语言绑定维护一张"kind 字符串 → 原生异常类型"的映射表。本视角分析错误类型的分类体系、标准错误类型、跨语言映射机制以及自定义错误类型的扩展方式。

## kind 字段的设计

### 字符串而非整数枚举

`TVMFFIErrorCell` 的第一个字段是 `TVMFFIByteArray kind`（`c_api.h:432`），存储错误类型的字符串名称，如 `"ValueError"`、`"TypeError"`、`"InternalError"`。选择字符串而非 C 枚举的原因包括：

1. **ABI 可扩展性**：新增错误类型不需要修改枚举定义或重新编译依赖头文件，字符串在运行时即可识别。
2. **跨语言自描述**：字符串在所有语言中都是原生类型，不需要生成枚举绑定代码。
3. **自定义类型支持**：库开发者可以定义自己的错误类型字符串（如 `"NPUInstructionError"`），无需向核心库申请编号。

C++ 层通过 `Error::kind()` 方法获取 kind 字符串（`error.h:180-183`）：

```cpp
std::string kind() const {
  ErrorObj* obj = static_cast<ErrorObj*>(data_.get());
  return std::string(obj->kind.data, obj->kind.size);
}
```

### kind 与 type_index 的关系

`ErrorObj` 的 `type_index` 固定为 `kTVMFFIError = 67`，所有错误对象共享同一个类型索引。这意味着 FFI 类型系统不通过 `type_index` 区分错误子类——错误分类完全由 `kind` 字段表达。这与 C++ 异常类层次（`Error` 作为基类，可派生子类）不同，后者通过 RTTI `catch` 块匹配类型。

在 FFI 的 C ABI 层面，所有错误都是同一种对象类型，通过 kind 字符串在语义上区分。C++ 层可以定义 `Error` 的子类，但跨语言传播时子类信息会丢失（因为只有 `kTVMFFIError` 一个类型索引），只有 kind 字符串被保留。

## 标准错误类型

### C++ 层的标准 kind 约定

虽然 C++ 层没有为每种错误类型定义独立的异常类，但 `TVM_FFI_THROW` 宏和检查宏约定了一组标准 kind 字符串：

| kind 字符串 | 用途 | 典型触发场景 |
|---|---|---|
| `InternalError` | 内部断言失败 | `TVM_FFI_ICHECK` 系列宏 |
| `RuntimeError` | 运行时通用错误 | `TVM_FFI_THROW(RuntimeError)` |
| `ValueError` | 参数值错误 | 无效参数值、越界 |
| `TypeError` | 类型不匹配 | 错误的 Any 类型转换 |
| `EnvErrorAlreadySet` | 宿主环境已有错误 | `TVMFFIEnvCheckSignals` 检测到信号 |

`TVM_FFI_ICHECK` 系列宏（`error.h:485-492`）固定使用 `InternalError`：

```cpp
#define TVM_FFI_ICHECK(x) TVM_FFI_CHECK(x, InternalError)
#define TVM_FFI_ICHECK_LT(x, y) TVM_FFI_CHECK_LT(x, y, InternalError)
// ...
```

这些宏用于内部不变量检查，失败表示程序逻辑存在 bug，而非用户输入错误。

### Python 层的标准映射

Python 绑定在 `python/tvm_ffi/error.py:259-266` 注册了标准错误类型映射：

```python
register_error("RuntimeError", RuntimeError)
register_error("ValueError", ValueError)
register_error("TypeError", TypeError)
register_error("AttributeError", AttributeError)
register_error("KeyError", KeyError)
register_error("IndexError", IndexError)
register_error("AssertionError", AssertionError)
register_error("MemoryError", MemoryError)
```

`register_error` 函数（`error.py:205-256`）维护两张双向映射表：

```python
def register(mycls: type) -> type:
    err_name = name_or_cls if isinstance(name_or_cls, str) else mycls.__name__
    core.ERROR_NAME_TO_TYPE[err_name] = mycls
    core.ERROR_TYPE_TO_NAME[mycls] = err_name
    return mycls
```

- `ERROR_NAME_TO_TYPE`：kind 字符串 → Python 异常类，用于从 FFI Error 重建 Python 异常。
- `ERROR_TYPE_TO_NAME`：Python 异常类 → kind 字符串，用于将 Python 异常转换为 FFI Error。

当 C++ 错误传播到 Python 时，绑定层根据 kind 查找对应的 Python 异常类并实例化；未注册的 kind 会映射为通用的 `tvm_ffi.Error`。

### Rust 层的标准常量

Rust 绑定在 `rust/tvm-ffi/src/error.rs:44-49` 定义了错误类型常量：

```rust
pub const VALUE_ERROR: ErrorKind = ErrorKind("ValueError");
pub const TYPE_ERROR: ErrorKind = ErrorKind("TypeError");
pub const RUNTIME_ERROR: ErrorKind = ErrorKind("RuntimeError");
pub const ATTRIBUTE_ERROR: ErrorKind = ErrorKind("AttributeError");
pub const KEY_ERROR: ErrorKind = ErrorKind("KeyError");
pub const INDEX_ERROR: ErrorKind = ErrorKind("IndexError");
```

`ErrorKind` 是一个新类型结构体（`error.rs:29-36`），包装 `&'a str`，提供类型安全的错误 kind 传递：

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ErrorKind<'a>(&'a str);

impl<'a> ErrorKind<'a> {
    pub fn as_str(&self) -> &str { self.0 }
}
```

Rust 的 `Result<T, Error>` 类型别名（`error.rs:68`）将 `Error` 作为默认错误类型，与 Rust 生态的错误处理惯例一致。

## 跨语言错误类型映射

### C++ → Python 映射流程

当 C++ 抛出 `Error` 并通过 FFI 传播到 Python 时：

1. C++ SafeCall 捕获 `Error`，将其存入 TLS。
2. Python 绑定检测到返回码 -1，调用 `TVMFFIErrorMoveFromRaised` 获取 Error 对象。
3. 读取 `kind` 字段（如 `"ValueError"`）。
4. 在 `ERROR_NAME_TO_TYPE` 中查找对应的 Python 异常类。
5. 实例化该异常类，消息来自 Error 的 message 字段。
6. 通过 `_with_append_backtrace` 将 C++ 回溯追加到 Python 异常的 traceback。

如果 kind 未在映射表中注册，Python 侧会使用基类 `tvm_ffi.Error` 异常，保留原始 kind 字符串。

### Python → C++ 映射流程

当 Python 回调抛出异常并传播到 C++ 时：

1. Python 绑定的函数包装器捕获 Python 异常。
2. 在 `ERROR_TYPE_TO_NAME` 中查找异常类对应的 kind 字符串。
3. 创建 FFI `Error` 对象，kind 为映射结果，message 包含 Python 异常的字符串表示。
4. 将 Python traceback 转换为 FFI backtrace 字符串（通过 `_traceback_to_backtrace_str`）。
5. 将 Error 存入 TLS，返回 -1。
6. C++ 调用侧从 TLS 取回 Error 并抛出。

未注册的 Python 异常类型映射为通用 kind（如 `"RuntimeError"`）。

### C++ → Rust 映射

Rust 绑定直接从 `TVMFFIErrorCell` 读取 kind 字符串：

```rust
pub fn kind(&self) -> ErrorKind<'_> {
    ErrorKind(&self.data.cell.kind.as_str())
}
```

Rust 侧不自动将 kind 映射为不同的 Rust 错误类型——所有 FFI 错误都是 `Error` 类型。调用者可以通过 `kind().as_str()` 匹配字符串来区分错误类型，或在自己的代码中将 `Error` 转换为自定义枚举错误类型。

## 自定义错误类型

### Python 自定义错误注册

Python 开发者可以通过装饰器注册自定义异常类：

```python
@tvm_ffi.error.register_error
class MyError(RuntimeError):
    pass
```

注册后，当 C++ 侧抛出 kind 为 `"MyError"` 的错误时，Python 绑定会自动创建 `MyError` 实例。反之，Python 代码抛出 `MyError` 时，跨 FFI 边界传播会使用 kind `"MyError"`。

### C++ 自定义 kind

C++ 代码可以直接使用任意 kind 字符串抛出错误：

```cpp
throw Error("NPUInstructionError", "Invalid opcode", backtrace);
// 或
TVM_FFI_THROW(RuntimeError) << "NPU execution failed";
```

`TVM_FFI_THROW(ErrorKind)` 宏（`error.h:400-404`）将参数字符串化作为 kind：

```cpp
#define TVM_FFI_THROW(ErrorKind)                                              \
  ::tvm::ffi::details::ErrorBuilder(#ErrorKind,                               \
                                    TVMFFIBacktrace(__FILE__, __LINE__,       \
                                                    TVM_FFI_FUNC_SIG, 0),     \
                                    TVM_FFI_ALWAYS_LOG_BEFORE_THROW)          \
      .stream()
```

`#ErrorKind` 将宏参数字符串化，因此 `TVM_FFI_THROW(MyCustomError)` 的 kind 就是 `"MyCustomError"`。

### 设计约束

虽然自定义错误类型不受限制，但有以下约定：

1. **命名风格**：使用 CamelCase，与 Python 异常类命名一致。
2. **语义明确**：kind 名称应能自解释，避免缩写。
3. **层次关系**：kind 字符串不编码继承关系。如果需要"这是一种 RuntimeError"的语义，Python 侧可以让自定义异常继承 `RuntimeError`，但 C++/Rust 侧仅看到 kind 字符串。
4. **注册可选**：C++/Rust 抛出的自定义 kind 不需要注册即可跨语言传播，只是 Python 侧会映射为基类异常。

## 设计分析

使用字符串 kind 而非枚举或异常类层次进行错误分类，是 FFI 场景下的务实选择。核心洞察是：**错误类型需要跨越的边界越多，字符串的自描述优势越明显**。C++ RTTI 类名依赖编译器的名称改编（name mangling），C 枚举需要在所有绑定中同步定义，而字符串在所有语言中都是通用的。

这种设计的代价是类型安全的丧失——C++ 编译器无法在编译期检查 kind 字符串的拼写错误。但这一代价通过宏封装（`TVM_FFI_THROW(ErrorKind)` 将标识符字符串化）和命名约定得到缓解。Rust 的 `ErrorKind` 新类型也提供了一定程度的编译期检查。

双向映射表的设计（kind ↔ 异常类）使得错误类型转换是数据驱动的，不需要硬编码的 switch/if-else 链。新增错误类型只需注册一行代码，符合开闭原则。

## 相关概念

- [076 ErrorObj 对象设计](076-error-obj-design.md)：kind 字段在 ErrorCell 中的位置
- [084 ErrorBuilder 与抛出宏](084-error-builder-throw-macros.md)：TVM_FFI_THROW 宏的 kind 字符串化机制
- [045 异常跨越 FFI 边界](/03-functions/concepts/045-exception-crossing-ffi.md)：错误类型跨边界的转换流程
- [085 Expected 无异常错误处理](085-expected-exception-free.md)：无异常路径中的错误 kind 传递
