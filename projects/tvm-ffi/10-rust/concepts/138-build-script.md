---
type: Concept
title: "视角138：build.rs 构建脚本"
description: "分析 tvm-ffi 和 tvm-ffi-sys 的 build.rs 脚本，如何通过 tvm-ffi-config 定位运行时库路径，配置链接参数和运行时库搜索路径。"
tags:
  - rust
  - build-script
  - cargo
  - linking
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-305
  - code:
    - rust/tvm-ffi/build.rs
    - rust/tvm-ffi-sys/build.rs
---

# 视角138：build.rs 构建脚本

## 概述

TVM FFI 的 Rust 绑定使用 `build.rs` 构建脚本在编译时动态定位 C++ 库路径，而非在 `Cargo.toml` 中硬编码。这种设计使绑定可以适配不同安装位置的 TVM FFI 库，而无需重新编译绑定代码本身。

## tvm-ffi-sys/build.rs

`tvm-ffi-sys/build.rs` 是最底层的构建脚本，负责链接 `tvm_ffi` 和 `tvm_ffi_testing` 库。

### 库路径发现

```rust
fn main() {
    let is_rustdoc = env::var("RUSTDOC").is_ok() || env::var("CARGO_CFG_DOC").is_ok();
    let config_result = Command::new("tvm-ffi-config").arg("--libdir").output();
    let lib_dir = match config_result {
        Ok(output) if output.status.success() => String::from_utf8(output.stdout)
            .unwrap_or_default().trim().to_string(),
        _ if is_rustdoc => {
            eprintln!("Warning: tvm-ffi-config not available, skipping for documentation build");
            return;
        }
        _ => panic!("Failed to run tvm-ffi-config. Make sure tvm-ffi is installed."),
    };
```

脚本通过 `tvm-ffi-config --libdir` 命令获取库目录。此命令是 TVM FFI 安装时提供的配置工具，输出库所在的绝对路径。

### 链接配置

```rust
println!("cargo:rustc-link-search=native={}", lib_dir);
println!("cargo:rustc-link-lib=dylib=tvm_ffi");
println!("cargo:rustc-link-lib=dylib=tvm_ffi_testing");
```

- `rustc-link-search=native=` 添加库搜索路径
- `rustc-link-lib=dylib=` 声明动态链接 `libtvm_ffi.so` / `tvm_ffi.dll`
- `tvm_ffi_testing` 是测试辅助库，仅开发时使用

### 运行时库路径更新

```rust
fn update_ld_library_path(lib_dir: &str) {
    let os_env_var = match env::var("CARGO_CFG_TARGET_OS").as_deref() {
        Ok("windows") => "PATH",
        Ok("macos") => "DYLD_LIBRARY_PATH",
        Ok("linux") => "LD_LIBRARY_PATH",
        _ => "",
    };
    // ... 拼接当前路径与新路径
    println!("cargo:rustc-env={}={}", os_env_var, new_ld_path);
}
```

`update_ld_library_path` 将库目录追加到运行时库搜索路径环境变量，使 `cargo run`/`cargo test` 可以直接找到动态库，无需系统级配置（如 `/etc/ld.so.conf` 或 `DYLD_FALLBACK_LIBRARY_PATH`）。

**注意**：注释明确说明此环境变量"only used for cargo run/test"，下游依赖此 crate 的项目仍需自行配置运行时库路径。

## tvm-ffi/build.rs

`tvm-ffi/build.rs` 包含 tvm-ffi-sys 的所有功能，外加示例库生成：

```rust
fn main() {
    // 1. 库路径发现与运行时路径更新（同 tvm-ffi-sys）
    let config_output = Command::new("tvm-ffi-config").arg("--libdir").output()
        .expect("Failed to run tvm-ffi-config");
    let lib_dir = String::from_utf8(config_output.stdout).unwrap().trim().to_string();
    update_ld_library_path(&lib_dir);

    // 2. 条件生成示例库
    generate_example_lib();
}
```

### 示例库生成

```rust
fn generate_example_lib() {
    let is_example_build = env::var("CARGO_FEATURE_EXAMPLE").is_ok();
    if !is_example_build { return; }
    let output_dir = env::var("OUT_DIR").unwrap();
    let _ = Command::new("python")
        .arg("scripts/generate_example_lib.py")
        .arg(output_dir)
        .output()
        .expect("Failed to generate example library");
    println!("cargo:rerun-if-changed=scripts/generate_example_lib.py");
}
```

示例库仅在启用 `example` feature 时生成。Python 脚本 `scripts/generate_example_lib.py` 根据 TVM FFI 的类型注册信息生成 Rust 示例代码，用于演示 API 使用。

## 设计分析

### 为什么使用 tvm-ffi-config 而非 PKG_CONFIG

1. **跨平台一致性**：`tvm-ffi-config` 是 TVM FFI 统一的配置工具，在 Windows/macOS/Linux 上行为一致，而 `pkg-config` 在 Windows 上支持不佳。
2. **与 CMake 构建系统集成**：TVM FFI 的 CMake 构建也使用类似的 config 工具，保持了一致性。
3. **rustdoc 兼容**：脚本检测 `RUSTDOC`/`CARGO_CFG_DOC` 环境变量，在生成文档时跳过库查找，避免文档构建因缺少运行时库而失败。

### 为什么需要 update_ld_library_path

动态链接库在编译后可被找到（通过 `rustc-link-search`），但**运行时**需要动态链接器能够定位 `.so`/`.dll`。通过 `cargo:rustc-env=` 生成的环境变量只在 cargo 子进程中生效，使 `cargo run` 和 `cargo test` 可以直接运行，而不需要用户在系统层面配置库路径。

### build.rs 的依赖顺序

由于 `tvm-ffi` 依赖 `tvm-ffi-sys`，而两者都有 `build.rs`，构建顺序为：
1. `tvm-ffi-sys/build.rs` 执行 → 链接 `tvm_ffi` 库
2. `tvm-ffi/build.rs` 执行 → 同样链接 `tvm_ffi`，并可能生成示例代码

两者都调用 `tvm-ffi-config`，结果一致。

## 扩展讨论

### 编译期与运行期的库解析分属两个时机

`rustc-link-search`/`rustc-link-lib` 解决「编译+链接期如何找到库」，`cargo:rustc-env=LD_LIBRARY_PATH=...` 解决「cargo run/test 运行动态链接器如何定位库」——两者缺一不可。但 `cargo:rustc-env` 只在 cargo 子进程的运行时环境生效，下游项目将 `tvm-ffi` 作为依赖时不会继承该变量，仍需自行配置库路径。这正是 FFI 绑定维护中"自用方便、分发需重配"的典型取舍。

### 用 tvm-ffi-config 替代 pkg-config 的原因

`pkg-config` 在 Windows 上支持不完整，且难以表达「TVM FFI 自己排布的安装路径」；`tvm-ffi-config --libdir` 是随安装一同生成的配置工具，跨平台行为统一、与 CMake 侧的 config 工具同构。它把「库装在哪」抽象为一个可执行的查询命令，使 build.rs 只依赖命令而非文件系统假设，从而适配 conda、pip、源码树等多种安装布局。

### rustdoc 专门豁免库查找

build.rs 检测 `RUSTDOC`/`CARGO_CFG_DOC` 后跳过库查找，是为了让仅生成文档的路径不因缺少运行时库而失败——文档构建不链接也不运行，不应被环境强约束。而示例库生成由 `CARGO_FEATURE_EXAMPLE` 门控，只在显式启用 `example` 时调用 Python 脚本，结合 `cargo:rerun-if-changed=scripts/generate_example_lib.py` 让脚本变更自动触发重建，保持增量构建正确性。

## 相关概念

- [视角131 Rust crate 结构](131-rust-crate-structure.md)：三层 crate 架构
- [视角139 Cargo workspace](139-cargo-workspace.md)：workspace 构建流程
- [视角151 CMake 构建系统](/12-build-package/concepts/151-cmake-build-system.md)：CMake 侧的等价机制
