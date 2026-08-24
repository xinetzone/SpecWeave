---
type: Concept
title: "视角145：DLL 导出/导入"
description: "分析 TVM FFI 与 TVM 运行时如何通过 DLL 宏体系控制系统符号的导出与导入，包括 TVM_FFI_DLL 各平台分支与编译器/运行时的符号分离。"
tags:
  - dll
  - symbol
  - export
  - import
  - visibility
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-376
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/runtime/base.h
---

# 视角145：DLL 导出/导入

## 概述

共享库（Windows 上为 DLL）的符号默认不可见，跨模块调用必须显式标注符号的导出/导入。TVM FFI 用一组条件编译宏统辖这一机制，并在 TVM 编译器中进一步区分编译器库与运行时库两套符号体系，实现模块间的清晰边界。

## TVM_FFI_DLL 宏体系

`include/tvm/ffi/c_api.h:30-57` 完整定义了 `TVM_FFI_DLL` 与 `TVM_FFI_DLL_EXPORT`：

- **Emscripten/WASM**（`c_api.h:41-45`）：当定义了 `__EMSCRIPTEN__` 时，两者均定为 `EMSCRIPTEN_KEEPALIVE`，防止 WebAssembly 导出符号被优化器移除。
- **MSVC**（`c_api.h:46-53`）：若定义 `TVM_FFI_EXPORTS`（构建共享库本端），`TVM_FFI_DLL` 为 `__declspec(dllexport)`；否则为 `__declspec(dllimport)`。`TVM_FFI_DLL_EXPORT` 恒为 `__declspec(dllexport)`。
- **GCC/Clang 等**（`c_api.h:54-57`）：默认回退为 `__attribute__((visibility("default")))`。

这套宏的关键价值在于"一份声明多处复用"：库内头文件既被共享库本端看到（定义 `TVM_FFI_EXPORTS`），也被下游用户看到（定义 `TVM_FFI_DLL` 导入），从而自动切换语义，避免为每个函数重复书写平台专属标注。

## 编译器库与运行时库分离

`include/tvm/runtime/base.h:43-93` 定义了**两套独立**的 DLL 宏：

- `TVM_DLL`/`TVM_DLL_EXPORT` 属于 `libtvm_compiler`（`base.h:43-46`），`TVM_DLL` 在编译本端时为 `dllexport`、下游为 `dllimport`；
- `TVM_RUNTIME_DLL`/`TVM_RUNTIME_DLL_EXPORT` 属于 `libtvm_runtime`（`base.h:48-51`），由 `TVM_RUNTIME_EXPORTS` 控制方向；
- 两套宏同样为 Emscripten 提供 `EMSCRIPTEN_KEEPALIVE` 分支（`base.h:61-62`、`base.h:79-80`）。

注释清晰指出"`TVM_DLL_EXPORT` 恒为 dllexport"（`base.h:47`），确保库导出源始终以导出语义声明符号。这种编译器库与运行时库符号分离，使调用方可按需仅链接运行时，减小二进制面。

## 设计分析

DLL 宏体系把平台相关的符号可见性差异收敛到一处头文件，通过 `TVM_FFI_EXPORTS`/`TVM_RUNTIME_EXPORTS` 构建开关自动区分导出与导入。在此之上，TVM 将编译器与运行时分隔成两套符号域，配合 [141 版本查询](141-c-abi-stability-guarantee.md) 的版本审计，形成"符号可见 + 版本可控"的双重稳定保障。对于跨平台分发，符号导出面越收敛，动态加载（`dlopen`/`LoadLibrary`）时代理与依赖解析越简单。

## 扩展讨论

### 一份声明为何能自动切换导入/导出

`TVM_FFI_DLL` 的取值方向由 `TVM_FFI_EXPORTS` 决定：构建共享库本端时定义该宏，符号标为 `dllexport`；下游消费端未定义，符号标为 `dllimport`。由于同一个头文件在两端都被包含，宏只需在构建配置层面翻转即可，函数声明处不用写两遍。这解释了「头文件自给自足」的边界设计——它不仅描述 API，还携带了平台符号可见性这道编译期决策。

### 导出面即契约面

DLL 宏把符号可见性收敛到一处，等价于声明「这是对外 ABI」。符号越少且越稳定，动态加载（`dlopen`/`LoadLibrary`）时符号解析越简单，版本错配的报错面也越小。配合 [141 版本查询](141-c-abi-stability-guarantee.md) 的版本审计，「显式导出 + 版本约束」双保险共同维系跨语言、跨版本的稳定调用面，避免隐式导出的符号漂移破坏下游。

### 编译器/运行时两套域的设计动机

`libtvm_compiler` 与 `libtvm_runtime` 分开导出的价值在于控制磁盘与装载代价：需要编译优化时链编译器库，仅部署/推理时可只链运行时库。两套宏不共用 `TVM_FFI_EXPORTS`，而是各自持有 `TVM_RUNTIME_EXPORTS`，从而允许两个库在同一构建中独立标记方向，互不干扰。

## 相关概念

- [141 C ABI 稳定性保证](141-c-abi-stability-guarantee.md)：稳定导出面
- [148 MSVC vs GCC/Clang](148-msvc-vs-gcc-clang.md)：各平台导出语法差异
- [147 Emscripten/WASM](147-emscripten-wasm-support.md)：EMSCRIPTEN_KEEPALIVE 导出
- [146 弱链接](146-weak-symbol-linking.md)：符号覆盖机制