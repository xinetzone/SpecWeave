---
type: Concept
title: "视角194：NPU 运行时模块加载"
description: "梳理 NPU 运行时模块的加载执行链路，从 Module::LoadFromFile、注册键工厂、字节反序列化到 GetFunction 分发，给出以 CUDA 模块为模板的完整接入方案。"
tags:
  - npu
  - runtime
  - module-loading
  - dynamic-loading
  - registry-key
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-301, F-302, F-303, F-304
  - code:
    - include/tvm/ffi/extra/module.h
    - src/ffi/extra/module.cc
    - ../../tvm/src/backend/cuda/runtime/cuda_module.cc
---

# 视角194：NPU 运行时模块加载

## 概述

运行时模块加载是"把一个已编译的 NPU 二进制变成可调用内核集合"的枢纽。TVM FFI 的模块系统同时支持两类装载途径：从磁盘共享库装载（`Module::LoadFromFile`）与从字节载荷还原（`ffi.Module.load_from_bytes.<kind>`）。本视角把加载链路拆成文件装载、工厂分发、反序列化、函数取用四步，并以 CUDA 为全程模板。

## 文件装载：Module::LoadFromFile

`Module::LoadFromFile`（`module.h:264`，实现在 `module.cc:138`）按文件名装载共享库：装载后根据库内注册符号 `__tvm_ffi_main`（`module.h:288`）与库上下文 `__tvm_ffi_library_ctx` 建立函数注册关系，使库内全局函数可被 `GetGlobalRequired` 检索。文件形态适合离线安装、需保留源码/元数据的场景。

## 工厂分发：注册键的桥梁

字节形态走另一条路：`ffi.Module.create.<kind>` 与 `ffi.Module.load_from_bytes.<kind>` 是两把注册键（`module.h` 注释），`<kind>` 由 `ModuleObj::kind()`（`module.h:49`）返回。`cuda_module.cc:381-395` 在 `TVM_FFI_STATIC_INIT_BLOCK()` 内同时注册两把键：load 键直接把字节交给 `CUDAModuleLoadFromBytes`，create 键则接受"代码+格式+函数手册"构建新模块。这是 NPU 运行时必须对齐的双出口。

## 反序列化：从字节到模块

`CUDAModuleLoadFromBytes`（`cuda_module.cc:365`）演示解析模式：用流按顺序读出格式、函数手册、代码三部分，构造 `Module`。反序列化必须与 `SaveToBytes`（`cuda_module.cc:99`）的序列化顺序严格一致，且需处理"源码映射在往返中丢失"等不可逆信息——这要求加载器对缺失的可选字段容错。

## 函数取用：从模块到调用

模块装载后，框架通过 `mod->GetFunction(name)`（`module.h:62`）取用内核，`cuda_module.cc:333` 的实现从 `fmap_` 手册按名解析签名并返回 `PackFuncVoidAddr` 包装的可调用函数。配合 `GetPropertyMask`（`module.h:56`）声明能力、`InspectSource`（`module.h:131`）回查源码，框架得以判断"这个 NPU 模块能不能跑、能不能看源码"。

## 设计分析

1. **create 与 load 分置**：create 面向代码生成器（构建期），load 面向运行时（部署期），职责清晰、可分别演进，也让同一内核既可在编译流程中即时生成，又可在运行时从磁盘/字节恢复。
2. **kind 是注册键的命名空间**：不同 NPU 后端通过各自 kind 隔离注册项，互不冲突，一台宿主可同时挂载多种加速器模块而不互相干扰。
3. **序列化顺序即契约**：字节格式的任何演进都必须保持加载器向后兼容，否则已部署模块失配；这一契约一旦公开便不可随意破坏。

## NPU建议

1. 为 NPU 实现 `NPUModuleNode`，`kind()` 返回 `"npu"`，并成对注册 `ffi.Module.create.npu` 与 `ffi.Module.load_from_bytes.npu` 两把键。

2. 明确序列化格式的字段顺序（建议：格式 → 函数手册 → 内核字节），与 `SaveToBytes` 严格一致，新增字段一律追加到末尾以保持向后兼容。

3. 为 `load_from_bytes.npu` 实现容错：对可丢失的可选字段（如源码映射）给出降级行为而非直接失败。

4. 用 `GetPropertyMask` 精确声明能力：仅当实际支持 `SaveToBytes` 才声明 `kBinarySerializable`，仅当 `GetFunction` 直接返回可执行函数才声明 `kRunnable`。

5. 对磁盘装载形态提供 `__tvm_ffi_main` 入口与库上下文符号，使 `Module::LoadFromFile` 装载后内核即被注册。

6. 若 NPU 内核需要 JIT，参考 CUDA 的 `JitCompileFromSource` 分离"源码态"与"编译态"，并把源码存入独立可选项供 `InspectSource` 回看。

## 相关概念

- [187 VTA 类加速器设计](187-vta-style-accelerator-design.md)：模块三要素
- [008 模块系统与动态加载](/01-architecture/concepts/008-module-system-dynamic-loading.md)
- [188 NPU 内核库发布](188-npu-kernel-library-publishing.md)
- [048 模块入口点约定](/03-functions/concepts/048-module-entry-point-convention.md)