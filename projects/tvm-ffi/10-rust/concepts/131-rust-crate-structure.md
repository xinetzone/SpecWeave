---
type: Concept
title: "视角131：Rust Crate 结构"
description: "解析 tvm-ffi Rust 绑定的三层 Crate 架构——tvm-ffi-sys、tvm-ffi、tvm-ffi-macros，及其 lib.rs 模块划分与重导出策略。"
tags:
  - rust
  - crate-structure
  - architecture
  - ffi
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-305, F-306
  - code:
    - rust/tvm-ffi/src/lib.rs
    - rust/tvm-ffi/Cargo.toml
    - rust/tvm-ffi-sys/Cargo.toml
    - rust/Cargo.toml
---

# 视角131：Rust Crate 结构

## 概述

TVM FFI 的 Rust 绑定采用三层 Crate 架构，在 `rust/` 目录中以 Cargo workspace 形式组织。这种分层设计遵循 Rust 社区的最佳实践：底层原始 FFI 绑定、中层安全包装、顶层派生宏工具。三个 Crate 分别是 `tvm-ffi-sys`（原始绑定）、`tvm-ffi`（安全 API）和 `tvm-ffi-macros`（派生宏）。

## 三层 Crate 架构

### 第一层：tvm-ffi-sys（原始 FFI 绑定）

`rust/tvm-ffi-sys/Cargo.toml` 定义了最底层 Crate，纯 FFI 绑定，不依赖任何其他 crate：

```toml
[package]
name = "tvm-ffi-sys"
description = "Low-level sys crate for tvm-ffi"
version = "0.1.0-alpha.0"
edition = "2021"
license = "Apache-2.0"

[lib]
name = "tvm_ffi_sys"
crate-type = ["lib"]
```

此 Crate 直接声明 C ABI 结构体与函数，如 `TVMFFIAny`、`TVMFFIObject`、`TVMFFIFunctionCell`、`TVMFFIErrorCell` 等，以及所有 `extern "C"` 函数绑定。其 `src/c_api.rs` 文件包含所有原始类型定义（见 F-307、F-308）。

### 第二层：tvm-ffi（安全包装）

`rust/tvm-ffi/Cargo.toml` 定义了中层安全 Crate：

```toml
[package]
name = "tvm-ffi"
description = "tvm-ffi rust support"
version = "0.1.0-alpha.0"
edition = "2021"
license = "Apache-2.0"

[dependencies]
paste = "1.0"
tvm-ffi-sys = { version = "0.1.0-alpha.0", path = "../tvm-ffi-sys" }
tvm-ffi-macros = { version = "0.1.0-alpha.0", path = "../tvm-ffi-macros" }
```

`tvm-ffi` 依赖 `tvm-ffi-sys` 和 `tvm-ffi-macros`，提供 `Any`、`Object`、`Function`、`Error`、`Tensor`、`Array`、`Map` 等安全类型包装（见 F-311~F-328）。

### 第三层：tvm-ffi-macros（派生宏）

`rust/tvm-ffi-macros/` 提供 `#[derive(Object)]`、`#[derive(ObjectRef)]`、`#[dispatch]`、`#[match_any]` 等派生宏，用于生成类型反射代码和模式匹配代码。

## 模块划分

`lib.rs:19-34` 声明了 14 个公共子模块（F-305）：

```rust
pub mod any;
pub mod collections;
pub mod derive;
pub mod device;
pub mod dtype;
pub mod error;
pub mod extra;
pub mod function;
pub mod function_internal;
pub mod macros;
#[doc(hidden)]
pub mod match_any_internal;
pub mod object;
pub mod optional;
pub mod string;
pub mod type_traits;
pub use tvm_ffi_sys;
```

## 重导出策略

`lib.rs:37-69` 统一重导出公共 API（F-306），使下游用户无需知道内部模块路径：

```rust
pub use crate::any::{Any, AnyView};
pub use crate::collections::array::Array;
pub use crate::collections::map::Map;
pub use crate::collections::shape::Shape;
pub use crate::collections::tensor::{CPUNDAlloc, NDAllocator, Tensor};
pub use crate::device::{current_stream, with_stream};
pub use crate::dtype::DLDataTypeExt;
pub use crate::error::{Error, ErrorKind, Result};
pub use crate::error::{ATTRIBUTE_ERROR, INDEX_ERROR, KEY_ERROR, RUNTIME_ERROR, TYPE_ERROR, VALUE_ERROR};
pub use crate::extra::module::Module;
pub use crate::extra::structural_mutate::{structural_map, structural_mutate, ...};
pub use crate::extra::structural_visit::{structural_visit, structural_walk, ...};
pub use crate::function::Function;
pub use crate::object::ObjectRefCast;
pub use crate::object::{Object, ObjectArc, ObjectCore, ObjectCoreWithExtraItems, ObjectRefCore};
pub use crate::optional::{Optional, OptionalCompatible};
pub use crate::string::{Bytes, String};
pub use crate::type_traits::AnyCompatible;
pub use tvm_ffi_macros::{dispatch, match_any};
pub use tvm_ffi_sys::TVMFFITypeIndex as TypeIndex;
pub use tvm_ffi_sys::{DLDataType, DLDataTypeCode, DLDevice, DLDeviceType, TVMFFIAny, TVMFFIObject, TVMFFIStreamHandle};
```

这种重导出策略使 `tvm_ffi::Any` 和 `tvm_ffi::object::Any` 等价，降低了 API 使用门槛。

## Cargo Workspace

`rust/Cargo.toml` 将三个 crate 组织为单一 workspace：

```toml
[workspace]
members = ["tvm-ffi", "tvm-ffi-sys", "tvm-ffi-macros"]
resolver = "2"
```

Workspace resolver 2 确保依赖解析在 crate 级别正确隔离，同时共享 lock 文件。

## 设计分析

三层 Crate 架构体现了以下设计考量：

1. **分离原始 FFI 与安全 API**：`tvm-ffi-sys` 保持最小化，仅包含 `#[repr(C)]` 结构体和 `extern "C"` 绑定，不引入任何安全封装逻辑。这确保了 C ABI 变更时只需更新 sys crate，安全层可保持稳定。

2. **build.rs 依赖**：`tvm-ffi` 和 `tvm-ffi-sys` 各自有独立的 `build.rs`，通过 `tvm-ffi-config --libdir` 命令定位运行时库路径（见视角138）。

3. **派生宏解耦**：将 `#[derive(Object)]` 等宏放在独立 crate，避免编译膨胀——不生成代码的 crate 不需要编译宏 crate。

4. **重导出层级**：`pub use tvm_ffi_sys` 将 sys crate 的所有 public 项直接暴露到 tvm-ffi 命名空间，使 `tvm_ffi::TVMFFIAny` 可用，同时保留 `tvm_ffi::any::Any` 等安全包装类型。

## 扩展讨论

### 三层分包是"安全边界"的 Rust 化表达

`tvm-ffi-sys` 刻意保持最小、无安全封装，只放 `#[repr(C)]` 结构体与 `extern "C"` 绑定，把「不安全的 C 接口」关进最小的 crate；`tvm-ffi` 在其上提供 `unsafe` 封装收敛到 `unsafe{...}` 的 API，把内存安全交给 Rust 类型系统；`tvm-ffi-macros` 则通过过程宏在编译期为 `#[derive(Object)]` 生成反射与引用计数代码。这个分层让「激进的安全承诺」只出现在中层，sys 层永不承诺安全，符合 Rust Rx/C API 的惯用工程实践。

### 重导出把命名空间压平为"用起来简单"

`lib.rs:37-69` 的 `pub use` 把 `object::Object`、`any::Any`、`error::Error` 等顶到 crate 根部，使 `tvm_ffi::Any` 与 `tvm_ffi::any::Any` 等价。这降低了用户心智负担，同时保留按模块组织的内部结构；`pub use tvm_ffi_sys` 更进一步把 sys 层的 `TVMFFIAny` 等直接暴露，让高级用户能在不额外 import sys 的前提下触及原始类型。

### 派生宏独立成 crate 的编译权衡

把 `#[derive(Object)]` 等宏放在独立 crate，避免安全层编译时强制编译宏 crate——不产生代码的 crate（如下游只 import tvm-ffi）无需构建 macros。这是把「编译期代码生成」与「运行时包装」解耦的经典做法：只有需要推导类型时才拉入 macros 依赖，从而缩短常见路径的构建时间。workspace resolver 2 让三个 crate 在同一次 cargo build 内统一解析依赖并共享锁文件。

## 相关概念

- [视角132 tvm-ffi-sys 原始绑定](132-tvm-ffi-sys-raw-bindings.md)：sys crate 的 FFI 类型详情
- [视角133 tvm-ffi 安全包装](133-tvm-ffi-safe-wrapper.md)：安全层的模块组织
- [视角139 Cargo workspace](139-cargo-workspace.md)：workspace 配置与构建
- [视角138 build.rs 构建脚本](138-build-script.md)：库路径发现机制
