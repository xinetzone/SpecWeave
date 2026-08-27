---
type: Concept
title: "视角150：版本查询 API"
description: "分析 TVM FFI 的版本信息体系，包括编译期宏、运行时查询结构体与函数，以及它们如何支撑动态加载场景下的版本协商。"
tags:
  - version
  - versioning
  - abi
  - compatibility
  - deprecation
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-018, F-379
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/runtime/base.h
---

# 视角150：版本查询 API

## 概述

版本信息是二进制兼容的"协商凭证"：库头文件携带编译期版本，共享库运行时通报实际版本，绑定层据此判断是否可安全互操作。TVM FFI 同时提供编译时宏与运行时查询两套机制，二者互为补充。

## 编译期版本宏

`include/tvm/ffi/c_api.h:67-74` 定义三个版本宏：

- `TVM_FFI_VERSION_MAJOR`（当前 0）：不兼容变更时递增；
- `TVM_FFI_VERSION_MINOR`（当前 1）：向后兼容的功能新增时递增；
- `TVM_FFI_VERSION_PATCH`（当前 14）：问题修复时递增。

这些宏供预处理器在编译期检查——头文件与共享库来自同一版本时可直接信任其 API 形态。头文件采用"注释 + 宏"而非硬编码常量字符串，避免格式化迁移时改动版本号。

## 运行时版本结构

`TVMFFIVersion`（`c_api.h:83-90`）在 C ABI 层定义版本三元组：

```c
typedef struct {
  uint32_t major;
  uint32_t minor;
  uint32_t patch;
} TVMFFIVersion;
```

三个字段均用定宽 `uint32_t`，与 [143 32/64 位兼容性](143-32-64-bit-compatibility.md) 的定宽原则一致，保证结构体在跨位宽、跨端平台可被稳定解读。

## 运行时查询函数

`TVMFFIGetVersion`（`c_api.h:546`）是运行时版本入口，函数注释明确指出"该函数在所有版本的 C ABI 中始终保持稳定"：

```c
TVM_FFI_DLL void TVMFFIGetVersion(TVMFFIVersion* out_version);
```

**"恒稳定"是其核心承诺**——无论库演进到哪个版本，绑定层总能先调用 `TVMFFIGetVersion` 拿到实际版本，再决定启用哪些特性。这使 `dlopen`/`LoadLibrary` 动态加载场景可以在使用任何 API 之前先完成版本校验，避免因头文件与库版本错配而崩溃。

## 编译期与运行时的配合

- **编译期**：通过 `TVM_FFI_VERSION_*` 宏静态判断"头文件声称的版本"，用于特性分派与编译告警。
- **运行时**：通过 `TVMFFIGetVersion`/`TVMFFIVersion` 判断"库实际版本"，用于动态加载时的安全协商。

二者结合，覆盖"头文件与库同源"（信任宏）与"头文件与库异步分发"（运行时校验）两种分发形态。TVM 自带的版本宏 `TVM_VERSION`（`include/tvm/runtime/base.h:34-35`，默认 `"0.26.dev0"`，可被 `-DTVM_VERSION` 覆盖）则提供额外的字符串版本，供上层工具展示。

## 设计分析

版本查询 API 的设计重点是"演进可协商、协商可验证"。编译期宏 + 运行时查询构成双保险：前者零开销但只能反映编译时快照，后者准确反映实际加载的库但需一次函数调用。`TVMFFIGetVersion` 恒定稳定，保证任何版本都具备协商入口，这使其成为 [141 C ABI 稳定性保证](141-c-abi-stability-guarantee.md) 中"版本审计"的关键一环——稳定的 ABI 需要一套稳定的"我是什么版本"的问答机制。

## 扩展讨论

### "恒稳定"为何能成立

`TVMFFIGetVersion` 的托管版本契约是：它自第一版起就存在、签名固定（`void(TVMFFIVersion*)`）、永不改动。正因其「接口绝不变更」，绑定层在任何库版本下都能安全先调用它做协商——否则「用于查版本的函数本身也可能变」就会让协商入口失效。这与 dlopen 惯用的「先 dlsym 查入口再调用」形成互补：dlsym 管定位，`TVMFFIGetVersion` 管校验。

### 编译期快照与运行时事实的落差

`TVM_FFI_VERSION_*` 反映「头文件构建时声称的版本」，只对同源分发可信；一旦头文件与库异步更新（常见于系统包、源码混装），宏就可能已过时。运行时查询则反映「实际加载的库」的真实版本。因此双机制分场景取用：编译期宏用于特性分派与告警（零开销快照），运行时查询用于动态加载的安全协商（准确）。两层互补正对治「声称 vs 事实」的版本漂移。

### uint32_t 定宽与跨端可读

`TVMFFIVersion` 三期均用定宽 `uint32_t`，避免 `int`/`long` 在位宽差异平台上大小漂移；三字段的填充对齐也符合编译器默认布局，使同个结构体在 32/64 位、大端/小端间都能被稳定解读（呼应视角 143/144）。这让「版本协商」信号本身也做到跨平台可移植，端侧只需以固定宽度逐字段读出即可比较。

## 相关概念

- [141 C ABI 稳定性保证](141-c-abi-stability-guarantee.md)：版本审计是稳定性的配套
- [005 ABI 稳定性策略](/01-architecture/concepts/005-abi-stability-strategy.md)：版本协商策略
- [015 版本演进与兼容性](/01-architecture/concepts/015-version-evolution-compatibility.md)：演进规则
- [143 32/64 位兼容性](143-32-64-bit-compatibility.md)：定宽版本字段