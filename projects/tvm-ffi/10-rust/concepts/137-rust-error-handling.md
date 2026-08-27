---
type: Concept
title: "视角137：Rust 错误处理"
description: "分析 TVM FFI Rust 绑定的错误类型体系，包括 Error/ ErrorKind 类型、TLS raised error 机制、回溯追加策略，以及 check_safe_call! / bail! 宏的错误传播。"
tags:
  - rust
  - error-handling
  - exception
  - traceback
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-317, F-318
  - code:
    - rust/tvm-ffi/src/error.rs
    - rust/tvm-ffi/src/macros.rs
    - rust/tvm-ffi-sys/src/c_api.rs
---

# 视角137：Rust 错误处理

## 概述

TVM FFI 的 Rust 绑定采用 C++ 风格的错误传播机制，通过 `Error` 对象和 TLS（线程局部存储）raised error 配合工作。Rust 侧定义 `Error`、`ErrorKind`、`Result<T>` 类型，并提供 `check_safe_call!`、`bail!`、`ensure!` 等宏简化错误传播。

## Error 类型体系

### ErrorKind

`error.rs:29-49`：

```rust
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ErrorKind<'a>(&'a str);

pub const VALUE_ERROR: ErrorKind = ErrorKind("ValueError");
pub const TYPE_ERROR: ErrorKind = ErrorKind("TypeError");
pub const RUNTIME_ERROR: ErrorKind = ErrorKind("RuntimeError");
pub const ATTRIBUTE_ERROR: ErrorKind = ErrorKind("AttributeError");
pub const KEY_ERROR: ErrorKind = ErrorKind("KeyError");
pub const INDEX_ERROR: ErrorKind = ErrorKind("IndexError");
```

`ErrorKind` 是 `&'a str` 的 wrapper，通过常量定义六种预置错误类型，与 C++ 侧的异常类型对应。

### ErrorObj 与 Error

`error.rs:52-65`：

```rust
#[repr(C)]
#[derive(Object)]
#[type_key = "ffi.Error"]
#[type_index(TVMFFITypeIndex::kTVMFFIError)]
pub struct ErrorObj {
    object: Object,
    cell: TVMFFIErrorCell,
}

#[derive(Clone, ObjectRef)]
pub struct Error {
    data: ObjectArc<ErrorObj>,
}
```

`Error` 包装 `ObjectArc<ErrorObj>`，通过引用计数管理错误对象的共享。`ErrorObj` 包含 `TVMFFIErrorCell`，其中有 `kind`、`message`、`backtrace` 三个 `TVMFFIByteArray` 字段和一个 `update_backtrace` 回调函数指针。

### Result 类型别名

`error.rs:68`：

```rust
pub type Result<T, E = Error> = std::result::Result<T, E>;
```

与 Rust 标准 `Result` 一致，默认错误类型为 `Error`。

## Error 构造方法

### Error::new（直接构造）

`error.rs:71-87`（F-317）：

```rust
pub fn new(kind: ErrorKind<'_>, message: &str, traceback: &str) -> Self {
    unsafe {
        let kind_data = TVMFFIByteArray::from_str(kind.as_str());
        let message_data = TVMFFIByteArray::from_str(message);
        let traceback_data = TVMFFIByteArray::from_str(traceback);
        let mut error_handle: TVMFFIObjectHandle = std::ptr::null_mut();
        let ret = TVMFFIErrorCreate(&kind_data, &message_data, &traceback_data, &mut error_handle);
        assert_eq!(ret, 0, "Failed to create error object");
        let error_obj = ObjectArc::from_raw(error_handle as *const ErrorObj);
        Self { data: error_obj }
    }
}
```

直接调用 C API `TVMFFIErrorCreate` 创建错误对象。这是构造错误的主要方式。

### Error::from_raised（从 TLS 转移）

`error.rs:93-104`（F-318）：

```rust
pub fn from_raised() -> Self {
    unsafe {
        let mut error_handle: TVMFFIObjectHandle = std::ptr::null_mut();
        TVMFFIErrorMoveFromRaised(&mut error_handle as *mut TVMFFIObjectHandle);
        assert!(!error_handle.is_null(), "Calling Error::from_raised but no error was raised");
        let error_obj = ObjectArc::from_raw(error_handle as *const ErrorObj);
        Self { data: error_obj }
    }
}
```

从 C++ 侧的 TLS raised error 移动构造。此方法**消耗** TLS 中的错误——调用后 TLS 中的错误被清空。如果 TLS 中没有 raised error，`error_handle` 为 null，`assert!` 触发 panic。

### Error::set_raised（设置 TLS）

`error.rs:110-114`：

```rust
pub fn set_raised(error: &Self) {
    unsafe {
        TVMFFIErrorSetRaised(ObjectArc::as_raw(&error.data) as TVMFFIObjectHandle);
    }
}
```

将错误设置为当前线程的 raised error，供 C++ 侧的 `from_raised` 或异常处理机制捕获。

## Error 访问方法

```rust
pub fn kind(&self) -> ErrorKind<'_> { ErrorKind(&self.data.cell.kind.as_str()) }
pub fn message(&self) -> &str { self.data.cell.message.as_str() }
pub fn backtrace(&self) -> &str { self.data.cell.backtrace.as_str() }
```

## 回溯追加策略

`Error::with_appended_backtrace`（`error.rs:163-184`）是关键方法，处理错误回溯的追加：

```rust
pub fn with_appended_backtrace(this: Self, backtrace: &str) -> Self {
    if ObjectArc::strong_count(&this.data) == 1 {
        // 单引用：原地 mutate
        unsafe {
            let backtrace_data = TVMFFIByteArray::from_str(backtrace);
            (this.data.cell.update_backtrace)(
                ObjectArc::as_raw(&this.data) as *mut ErrorObj as *mut c_void,
                &backtrace_data,
                kTVMFFIBacktraceUpdateModeAppend as i32,
            );
            this
        }
    } else {
        // 多引用：创建新 Error
        let mut new_backtrace = String::new();
        new_backtrace.push_str(this.backtrace());
        new_backtrace.push_str(backtrace);
        return Error::new(this.kind(), this.message(), &new_backtrace);
    }
}
```

**策略**：当 `Error` 只有单一引用时，原地修改回溯（避免拷贝）；有多个引用时，创建新 Error 以保持原有引用不变。这是典型的 copy-on-write 优化。

## 错误传播宏

### check_safe_call!

`macros.rs:73-83`：

```rust
#[macro_export]
macro_rules! check_safe_call {
    ($expr:expr) => {{
        let ret_code = $expr;
        if ret_code == 0 { Ok(()) } else {
            let error = $crate::error::Error::from_raised();
            Err(error)
        }
    }};
}
```

检查 C API 的返回码。返回 0 表示成功，非零表示 C++ 侧已通过 TLS 设置了 raised error，通过 `Error::from_raised()` 提取。

用法：`check_safe_call!(TVMFFIFunctionCall(func, args, n, &mut result))?;`

### bail!

`macros.rs:97-113`：

```rust
#[macro_export]
macro_rules! bail {
    ($error_kind:expr, $fmt:expr $(, $args:expr)* $(,)?) => {{
        let context = format!(
            "  File \"{}\", line {}, in {}\n",
            file!(), line!(), function_name!()
        );
        return Err($crate::error::Error::new(
            $error_kind,
            &format!($fmt $(, $args)*),
            &context,
        ));
    }};
}
```

立即返回错误，自动附加文件名、行号、函数名信息到回溯。

### ensure!

```rust
#[macro_export]
macro_rules! ensure {
    ($cond:expr, $error_kind:expr, $fmt:expr $(, $args:expr)*) => {
        if !$cond {
            bail!($error_kind, $fmt $(, $args)*);
        }
    };
}
```

条件不满足时 bail。

### attach_context!

```rust
#[macro_export]
macro_rules! attach_context {
    ($expr:expr) => {{
        let ret = $expr;
        match ret {
            Ok(v) => v,
            Err(e) => {
                let context = format!("  File \"{}\", line {}, in {}\n", file!(), line!(), function_name!());
                return Err(Error::with_appended_backtrace(e, &context));
            }
        }
    }};
}
```

执行表达式，失败时附加当前函数的上下文信息。

## Display 与 Debug

`error.rs:187-203`：

```rust
impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Traceback (most recent call last):\n{}{}: {}",
            self.traceback_most_recent_call_last(),
            self.kind().as_str(),
            self.message()
        )
    }
}
impl std::fmt::Debug for Error { std::fmt::Display::fmt(self, f) }
impl std::error::Error for Error {}
```

`Error` 实现了 Rust 标准 `std::error::Error` trait，可以与 `?` 运算符配合使用。

## 设计分析

1. **C++ TLS 机制的 Rust 封装**：`from_raised`/`set_raised` 封装了 C++ 侧的 TLS raised error，使 Rust 代码可以参与 C++ 的错误传播链。
2. **Copy-on-Write 回溯**：`with_appended_backtrace` 在单引用时原地修改，减少不必要的 Error 对象拷贝。
3. **宏驱动的错误传播**：`bail!`/`ensure!`/`check_safe_call!` 等宏提供了一致的错误上下文注入，使每个错误都携带文件/行号信息。
4. **std::error::Error 实现**：使 Rust 错误系统（? 运算符、anyhow、thiserror 等）可以与 TVM FFI 错误类型互操作。

## 扩展讨论

### Error 作为 Object：错误也要走引用计数

`ErrorObj` 被 `#[derive(Object)]` 标记且 `type_index = kTVMFFIError`，意味着错误本身是堆上引用计数对象，其 `kind/message/backtrace` 的 `TVMFFIByteArray` 剖面随对象生命周期共享。`Error`（`ObjectRef` 风格）克隆只加引用不拷贝数据，这使得大错误结构（长回溯）在多处传播时零拷贝；配合 `ObjectArc<ErrorObj>` 才能在 `with_appended_backtrace` 里检查 `strong_count` 决定原地改写还是新建。

### Copy-on-Write 的引用计数条件

`with_appended_backtrace` 若 `strong_count == 1` 会原地调用 `update_backtrace`（以 `kTVMFFIBacktraceUpdateModeAppend` 追加），否则构造新 `Error`。其正确性依赖一个前提：单引用时可以安全改写共享内存。这是把 Rust 所有权与 C++ COW 语义对齐的典型用法——Rust 通过强计数判断「我是不是唯一持有者」，从而复用共享 buffer 或分裂。

### TLS raised error 的"所有权转移"语义

`Error::from_raised` 调用 `TVMFFIErrorMoveFromRaised` 把 TLS 中的错误**搬走**（转移所有权而非拷贝），`set_raised` 则把错误放回 TLS。二者的存在使 Rust 与 C++ 能在同一条错误传播链上并置：C++ 抛出→Rust 取回→Rust 改/附加→再 set 给 C++，全程只有一次错误对象的移动。`check_safe_call!`/`bail!`/`attach_context!` 在每层自动注入 `file!()/line!()` 帧，构成跨语言的完整回溯栈，呼应视角 080 的追溯链。

## 相关概念

- [视角045 异常跨越 FFI 边界](/03-functions/concepts/045-exception-crossing-ffi.md)：C++ 侧的异常处理机制
- [视角046 TLS 错误传播](/03-functions/concepts/046-tls-error-propagation.md)：TLS raised error 的 C++ 实现
- [视角133 tvm-ffi 安全包装](133-tvm-ffi-safe-wrapper.md)：ErrorObj 的 Object 基类
