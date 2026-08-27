---
type: Concept
title: "视角139：Cargo workspace"
description: "分析 TVM FFI Rust 绑定的 Cargo workspace 配置，三个 crate 的依赖关系、resolver 版本、以及 workspace 级别的构建协调。"
tags:
  - rust
  - cargo
  - workspace
  - build-system
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-305
  - code:
    - rust/Cargo.toml
    - rust/tvm-ffi/Cargo.toml
    - rust/tvm-ffi-sys/Cargo.toml
    - rust/tvm-ffi-macros/Cargo.toml
---

# 视角139：Cargo workspace

## 概述

TVM FFI 的 Rust 绑定在 `rust/` 目录下以 Cargo workspace 形式组织，包含三个 crate：`tvm-ffi-sys`（底层 FFI 绑定）、`tvm-ffi`（安全 API）、`tvm-ffi-macros`（派生宏）。workspace 配置简洁，仅声明成员和 resolver 版本。

## Workspace 配置

`rust/Cargo.toml`：

```toml
[workspace]
members = ["tvm-ffi", "tvm-ffi-sys", "tvm-ffi-macros"]
resolver = "2"
```

### members

三个 crate 均为 workspace 成员：
- `tvm-ffi-sys`：最底层，无内部依赖
- `tvm-ffi-macros`：宏 crate，被 tvm-ffi 依赖
- `tvm-ffi`：主 crate，依赖 sys 和 macros

### resolver = "2"

Cargo resolver v2 是 2021 edition 的默认行为，关键特性：
- **依赖隔离**：每个 crate 的依赖图独立解析，避免 crate A 的额外依赖被传递给 crate B。
- **features 隔离**：可选 features 不再跨 crate 传递。
- **dev-dependencies 隔离**：测试依赖不影响其他 crate。

对于 TVM FFI，这意味着 `tvm-ffi` 的 `paste` 依赖不会出现在 `tvm-ffi-sys` 的依赖树中。

## Crate 依赖关系图

```
                    ┌─────────────────────┐
                    │   rust/Cargo.toml   │
                    │   (workspace root)  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
    ┌────────────────┐ ┌──────────────┐ ┌─────────────────┐
    │  tvm-ffi-sys   │ │ tvm-ffi-macros│ │    tvm-ffi      │
    │  (no deps)     │ │ (no deps)     │ │ dep: paste      │
    │                │ │               │ │ dep: tvm-ffi-sys│
    │  links:        │ │  provides:    │ │ dep: tvm-ffi-   │
    │  tvm_ffi       │ │  derive macros│ │   macros        │
    │  tvm_ffi_testing│ │  (Object,     │ │ build.rs:       │
    │                │ │   ObjectRef)  │ │  tvm-ffi-config │
    └────────────────┘ └──────────────┘ └─────────────────┘
```

## 各 Crate 的 Cargo.toml 详情

### tvm-ffi-sys

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

- 纯 `lib` crate 类型（无 `cdylib`/`dylib`）
- 无外部依赖
- `build.rs` 负责链接 `tvm_ffi` 和 `tvm_ffi_testing` 动态库

### tvm-ffi-macros

```toml
[package]
name = "tvm-ffi-macros"
description = "Procedural macros for tvm-ffi"
version = "0.1.0-alpha.0"
edition = "2021"
license = "Apache-2.0"

[lib]
name = "tvm_ffi_macros"
proc-macro = true
```

- `proc-macro = true`：编译为 proc-macro crate，输出为编译插件而非普通库
- 提供 `#[derive(Object)]`、`#[derive(ObjectRef)]`、`#[dispatch]`、`#[match_any]` 宏
- 无外部依赖

### tvm-ffi

```toml
[package]
name = "tvm-ffi"
description = "tvm-ffi rust support"
version = "0.1.0-alpha.0"
edition = "2021"
license = "Apache-2.0"

[lib]
name = "tvm_ffi"
crate-type = ["lib"]

[dependencies]
paste = "1.0"
tvm-ffi-sys = { version = "0.1.0-alpha.0", path = "../tvm-ffi-sys" }
tvm-ffi-macros = { version = "0.1.0-alpha.0", path = "../tvm-ffi-macros" }

[features]
example = []

[[example]]
name = "load_library"
path = "examples/load_library.rs"
required-features = ["example"]
```

- 依赖 `paste`（用于宏代码生成）和两个内部 crate
- `example` feature 控制示例库的生成
- `load_library` 示例需要 `example` feature

## 构建协调

### 构建顺序

Cargo workspace 保证依赖顺序：
1. `tvm-ffi-macros` 最先构建（无依赖）
2. `tvm-ffi-sys` 其次构建（无依赖，但 build.rs 需要 tvm-ffi 库已安装）
3. `tvm-ffi` 最后构建（依赖前两者）

### 版本一致性

三个 crate 版本均为 `0.1.0-alpha.0`，通过 `path = "../..."` 本地路径依赖绑定。这意味着：
- 任何 crate 的版本变更需要手动同步三个版本的 frontmatter
- 不适合独立发布——三个 crate 应作为一个整体版本发布

### workspace 级别的命令

在 `rust/` 目录下执行：

```bash
# 构建所有 crate
cargo build

# 构建特定 crate
cargo build -p tvm-ffi-sys
cargo build -p tvm-ffi
cargo build -p tvm-ffi-macros

# 运行测试
cargo test --workspace
cargo test -p tvm-ffi

# 生成文档
cargo doc --workspace --no-deps
```

`-p` 指定 crate 名（package name），workspace 中各 crate 的 lib name 与 package name 可能不同（如 `tvm-ffi-sys` package → `tvm_ffi_sys` lib）。

## 设计分析

1. **workspace 的必要性**：三个 crate 紧密耦合（共享版本号、路径依赖），workspace 提供了统一的构建、测试和文档生成入口。
2. **resolver v2**：确保 `tvm-ffi` 的 `paste` 依赖不会意外传递给 `tvm-ffi-sys`，保持 sys crate 的纯净性。
3. **proc-macro crate 隔离**：`tvm-ffi-macros` 作为独立的 proc-macro crate，编译时不进入 `tvm-ffi` 的依赖图（proc-macro crate 在编译期单独编译），减少了 `tvm-ffi` 的编译依赖。
4. **build.rs 的重复逻辑**：`tvm-ffi` 和 `tvm-ffi-sys` 的 build.rs 有重叠的库路径发现逻辑，但未提取为共享 crate——这是合理的，因为 build.rs 在编译期运行，不能依赖其他 workspace crate。

## 扩展讨论

### resolver v2 的 feature 隔离对 FFI 的影响

resolver v2（2021 edition 默认）让可选 features 不再跨 crate 传递。对 FFI 场景这意味着 `tvm-ffi` 的 `example` feature 不会意外开启 `tvm-ffi-macros` 或 `tvm-ffi-sys` 的任何 feature，依赖图更可预测；同时 dev-dependencies 隔离保证测试依赖（如 `paste` 的 dev 用法）不会污染发布依赖树，正是 `tvm-ffi` 依赖 `paste`、而 `tvm-ffi-sys` 保持零依赖的原因。

### proc-macro crate 吃掉了一整个编译阶段

`proc-macro = true` 的 crate 不是普通库，它被编译为加载进编译器的插件；因此 `tvm-ffi-macros` 一旦变更，会触发下游所有依赖它 derive 宏的 crate 重新编译。把它独立出来能让演绎宏的三层职责（sys 布局、安全封装、宏生成）各自独立演进，也让 tvm-ffi 的普通依赖图不包含编译期插件，压缩常见增量构建路径。

### path 依赖与版本一致性的代价

三个 crate 全部 `version = "0.1.0-alpha.0"`，通过 `path = "../..."` 绑定本地路径。好处是 workspace 内天然一致、可直接 `cargo build`；代价是无法独立发布（版本需手动三处同步）。这正是「整体发布一个 crate 家族」的取舍——把版本文档、变更日志、发布版本统一到一个节奏，把「版本漂移」风险集中在发布流程而非构建期。

## 相关概念

- [视角131 Rust crate 结构](131-rust-crate-structure.md)：三层 crate 架构
- [视角138 build.rs 构建脚本](138-build-script.md)：库路径发现机制
- [视角151 CMake 构建系统](/12-build-package/concepts/151-cmake-build-system.md)：CMake 侧的 workspace 等价概念
