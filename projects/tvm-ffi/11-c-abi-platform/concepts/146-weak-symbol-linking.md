---
type: Concept
title: "视角146：弱链接"
description: "分析 TVM FFI 借用编译器的弱符号机制实现可覆盖的全局声明，涵盖 MSVC 的 selectany 与 GCC/Clang 的 weak 属性两条路径。"
tags:
  - weak-symbol
  - overridable
  - linking
  - selectany
  - weak-attribute
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-025
  - code:
    - include/tvm/ffi/c_api.h
---

# 视角146：弱链接

## 概述

弱链接（Weak Linking）允许同一个符号存在"弱定义"与"强定义"，链接器在既有较强的定义时舍弃弱定义，从而实现"默认实现 + 可被覆盖"的扩展点。TVM FFI 在头文件中用条件编译封装了跨编译器的弱符号声明宏，为可选特性与重写点提供统一的书写方式。

## TVM_FFI_WEAK 宏

`include/tvm/ffi/c_api.h:30-35` 定义了弱链接宏，注释明确"Macros to do weak linking"：

- **MSVC**（`c_api.h:31-32`）：`#define TVM_FFI_WEAK __declspec(selectany)`。`selectany` 指示编译器在多个编译单元定义同一符号时只保留其一，常用于头文件中定义的全局对象，行为上类似弱符号去重。
- **Emscripten/GCC/Clang 等**（`c_api.h:33-34`）：`#define TVM_FFI_WEAK __attribute__((weak))`。

这一分支让上层代码以 `TVM_FFI_WEAK` 一处书写，即可同时适配 MSVC 与 GNU 系编译器。

## 应用语义

弱声明的典型用途包括：

- **全局注册符号**：全局函数注册表、运行时特性开关等 head-object，允许库本端定义默认值，下游通过强定义覆盖或追加。
- **可裁剪特性**：将某特性以弱符号提供，平台无能力时由弱定义兜底，有能力时由强实现覆盖。
- **头文件内全局对象去重**：配合 `selectany`/`weak`，头部定义的静态全局对象在多重包含下不会产生重复定义错误。

TVM FFI 将这类符号的覆盖点集中管理，与 [145 DLL 导出/导入](145-dll-export-import.md) 的显式符号面互相配合：导出面保证符号可达，弱符号保证可在链接期改写。

## 设计分析

弱链接为"库提供默认、宿主可覆盖"的扩展模式提供了链接期常量成本解决方案——无需动态分派或回调注册，直接以符号重定位达成覆盖。其代价是弱符号行为部分依赖编译器扩展，因此 TVM FFI 用宏统一封装并附带清晰注释，以在一个可预测的抽象下使用该能力，避免把平台细节泄漏到业务代码。

## 扩展讨论

### selectany 与 weak 的语义差异为何被统一

MSVC 的 `selectany` 与 GNU 系的 `weak` 并不完全等价：`selectany` 更接近「多定义去重」（头文件内全局对象重名时只保留一个），而 `weak` 强调「弱/强定义共存时的取舍」。TVM FFI 用 `TVM_FFI_WEAK` 把两者收敛成同一书写接口，是因为上层关心的语义是「可被覆盖的默认符号」这一共同点，平台差异只呈现为宏扩展的不同——业务代码无需感知是走 selectany 还是 weak。

### 弱符号与 DLL 导出的分工

弱符号解决「链接期可否改写」：（145）的 DLL 宏解决「跨模块是否可见」。二者正交：导出面把符号暴露给外部，弱定位让同一符号在目标文件合并时能被宿主更强的定义顶替。合并看，注册表头对象以 `TVM_FFI_WEAK` 定义默认实现，宿主若提供强定义则自动接管，形成「零运行时开销」的覆盖机制，常用于运行时特性开关与平台裁剪。

### 易踩的坑：弱符号的链接期不确定性

弱符号若被多个强定义争抢，行为依赖链接器输入顺序且难以诊断；因此覆盖点必须唯一、集中，避免分散定义造成「谁生效靠运气」。这正是把覆盖点收敛到单一头文件、配合注释明确「默认/可改写」语义的意义所在——用可预测的抽象降低弱链接这种「编译器扩展带来的不确定」的维护成本。

## 相关概念

- [145 DLL 导出/导入](145-dll-export-import.md)：符号可见性
- [148 MSVC vs GCC/Clang](148-msvc-vs-gcc-clang.md)：selectany 与 weak 的平台差异
- [040 全局函数注册表](/03-functions/concepts/040-global-function-registry.md)：注册符号的宿主