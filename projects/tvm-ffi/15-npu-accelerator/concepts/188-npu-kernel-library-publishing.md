---
type: Concept
title: "视角188：NPU 内核库发布"
description: "讲解如何把 NPU 内核库以动态库形式发布到 FFI 生态系统，覆盖符号前缀约定、模块入口点、全局注册表接入与清单维护，确保库可被运行时加载并检索其函数。"
tags:
  - npu
  - kernel-library
  - publishing
  - symbol-prefix
  - dynamic-loading
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-141, F-142, F-151
  - code:
    - include/tvm/ffi/extra/module.h
    - include/tvm/ffi/function.h
    - include/tvm/ffi/c_api.h
---

# 视角188：NPU 内核库发布

## 概述

NPU 内核编译完成后的产物可以是一个共享库（`.so`/`.dll`）或一段可序列化字节。发布"内核库"要解决两个问题：**库内函数如何被外部按名查找**、**库的加载与函数清单如何对运行时可见**。TVM FFI 给出了两套互补机制——共享库通过既定的符号前缀与模块入口点约定被 `Module::LoadFromFile` 加载；字节形态通过模块注册键按 kind 分发。本视角聚焦将 NPU 内核打包为可发布库的规范。

## 符号前缀约定

`module.h:283` 定义了库内符号的统一前缀 `__tvm_ffi_`，并派生出一组保留符号：

- `__tvm_ffi_main`：库的默认入口函数（`module.h:288`）。
- `__tvm_ffi_library_ctx`：库级全局上下指针（`module.h:290`）。
- `__tvm_ffi_library_bin`：随库附带的内核二进制数据（`module.h:292`）。

使用统一前缀能把"本库导出的 FFI 符号"与其他编译产物符号隔离开，避免同名冲突，也是加载器识别库入口与上下文的依据（视角049 详细阐述该前缀的设计动机）。

## 装载时的函数注册

共享库被 `Module::LoadFromFile`（`module.cc:138`）装载后，库内定义的全局函数会以"库上下文（library context）"的方式注册到运行时。用户侧通过 `Function::GetGlobalRequired(name)`（`function.h:456`）按名取回某个内核函数：

```cpp
static Function GetGlobalRequired(std::string_view name);
```

当需要枚举库内已注册的全部函数时，使用 `Function::ListGlobalNames()`（`function.h:511`），它内部通过 `GetGlobalRequired("ffi.FunctionListGlobalNamesFunctor")` 获取枚举器。这为"库发布了哪些内核"提供了可审查的清单接口。

## 二进制载荷发布

对于不以共享库形式发布、而以字节串分发的内核（如 JIT 产物），应走模块注册键 `ffi.Module.load_from_bytes.<kind>`，由 kind 指定的加载器还原为模块。CUDA 的 `CUDAModuleLoadFromBytes`（`cuda_module.cc:365`）展示了从 `ffi::Bytes` 流中依次读出格式、函数手册、代码的解析模式。这种形态更适合需要跨网络分发、无文件系统依赖的场景。

## 设计分析

1. **符号前缀是 ABI 层面的命名空间**：它不具备运行期隔离，但通过约定避免了不同库的 FFI 符号互相污染，是低成本、高价值的发布纪律。
2. **函数清单是发布文档的一部分**：`ListGlobalNames` 让运行时能自省库内容，是调试与工具链依赖的基础。
3. **共享库与字节形态是两种可组合的发布通道**：前者适合离线安装，后者适合在线传输，kind 注册键让两者统一为"模块"这一抽象。

## NPU建议

1. 发布的 NPU 内核库统一使用 `__tvm_ffi_` 前缀导出符号，不导出裸符号，防止与宿主程序或其他库的符号冲突。

2. 提供 `__tvm_ffi_main` 入口，在入口内通过 `TVM_FFI_STATIC_INIT_BLOCK` 完成所有内核全局函数的静态注册，使库一经装载其函数即可被 `GetGlobalRequired` 检出。

3. 维护一份内核函数清单，并在发布时通过 `ListGlobalNames()` 自检，确认所有预期内核均已注册。

4. 若内核以字节串分发，注册 `ffi.Module.load_from_bytes.npu` 并按 `cuda_module.cc:365` 的声明顺序（格式→手册→代码）做好序列化，保证前后向兼容（新增字段追加在末尾）。

5. 为每个内核补全签名元数据与文档字符串（对应模块的 `GetFunctionMetadata`/`GetFunctionDoc`），使发布库具备可被工具链消费的结构化信息。

6. 提供库版本号导出符号（可复用 `c_api.h` 的版本查询思路，见视角198），作为下游兼容性判断的依据。

## 相关概念

- [198 NPU ABI 稳定性建议](198-npu-abi-stability.md)：符号与版本稳定策略
- [194 NPU 运行时模块加载](194-npu-runtime-module-loading.md)：库装载与字节加载
- [049 __tvm_ffi_ 符号前缀](/03-functions/concepts/049-tvm-ffi-symbol-prefix.md)
- [048 模块入口点约定](/03-functions/concepts/048-module-entry-point-convention.md)
- [040 全局函数注册表](/03-functions/concepts/040-global-function-registry.md)