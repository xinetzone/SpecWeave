---
type: Concept
title: "视角200：NPU 内核 DSL 集成"
description: "讲解如何把 NPU 内核 DSL（领域特定语言）接入 TVM 的代码生成流程：目标注册、模块创建工厂、JIT 编译与源码回看，最终实现 DSL 内核被运行时调用的闭环。"
tags:
  - npu
  - dsl
  - codegen
  - jit
  - target-kind
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-355, F-373
  - code:
    - ../../tvm/src/backend/trn/codegen/target_kind.cc
    - ../../tvm/src/backend/cuda/runtime/cuda_module.cc
    - include/tvm/ffi/extra/module.h
---

# 视角200：NPU 内核 DSL 集成

## 概述

NPU 厂商常自带一套内核 DSL（如类似 CUDA C 的扩展语言或专用中间表达），编写的高层内核需要被降级为设备可执行代码并被运行时调用。DSL 集成的本质，是把"DSL 源码 → 编译 → 可执行内核"的链路挂到 TVM 模块系统上（对应 `kind=codegen` 的 `codegen_*` 模块）。本视角以 Trainium 与 CUDA 为参照，梳理 DSL 落地的目标注册、创建工厂、JIT 与源码回看四步。

## 目标注册：让 DSL 目标可声明

DSL 必须绑定一个编译目标。仿照 Trainium 在 `target_kind.cc:35-41` 用 `TVM_REGISTER_TARGET_KIND("trn", kDLTrn)` 注册，NPU DSL 应注册自己的目标并声明属性（内核风格、支持的向量宽度、片上 SRAM 容量等）：

```cpp
TVM_REGISTER_TARGET_KIND("npu_kernel", kNpuDevice)
    .add_attr_option<int64_t>("vector_width", 512)
    .add_attr_option<int64_t>("num_cores");
```

注册置于 `TVM_FFI_STATIC_INIT_BLOCK()`（`target_kind.cc:57`），装载即生效。

## 模块创建工厂：DSL 源码进、模块出

DSL 编译完成由 `ffi.Module.create.<kind>` 工厂承载。CUDA 的 create 键（`cuda_module.cc:389`）接受"代码+格式+函数手册+源码"构建 `Module`。NPU 的 create 工厂应接受 DSL 源码（或预编译字节）+ 内核清单，返回一个含可执行函数的 `NPUModuleNode`。格式参数（如 `"npu_dsl"` / `"npu_bin"`）驱动创建路径选择"源码 JIT"或"字节直载"。

## JIT 编译与源码态分离

若 DSL 需要运行时编译，把"源码态"与"编译态"分离：进厂时若传入源码（`fmt == "npu_dsl"`），先保存源码用于当时的源码审查，再 JIT 产出字节。`cuda_module.cc:350-360` 的 `CUDAModuleCreateImpl` 示范了"存源码→JIT→替换 fmt"的流程。`SaveToBytes`（`cuda_module.cc:99`）仅序列化可逆载荷，源码作为可选项。

## 源码回看与自省

编译产物是否可追溯，取决于 `ModuleObj::InspectSource`（`module.h:131`）与 `GetFunctionMetadata`/`GetFunctionDoc`（`module.h:101`、`module.h:81`）是否被实现。DSL 集成应保留源码态（至少保留到编译完成），使调试与性能分析（视角197）能回看"这段可执行内核最初的 DSL 长什么样"。

## 设计分析

1. **目标、工厂、格式三位一体**：目标声明"能编什么"，工厂声明"怎么造模块"，格式声明"造哪种"——三者需一次性对齐。
2. **JIT 与源码态分离提升可观测性**：编译是非确定性的，保留源码才能在失败与调优时还原现场。
3. **DSL 编译产物统一收敛为 Module**：无论 DSL 多复杂，对外最终只需交付一个 `ffi::Module`，既隔离复杂度又复用模块系统的加载/调用能力。

## NPU建议

1. 为 NPU DSL 在 `target_kind.cc` 中注册目标并绑定设备枚举，声明 DSL 关键属性，静态注册于 `TVM_FFI_STATIC_INIT_BLOCK()`。

2. 实现 `ffi.Module.create.npu` 工厂，接受"DSL 源码/字节 + 格式 + 函数手册"，返回 `NPUModuleNode`；按格式区分源码 JIT 与字节直载路径。

3. 进厂处理遵循 CUDA 的"存源码 → JIT → 更新格式"次序，源码态与编译态分离存储。

4. 实现 `InspectSource("npu_dsl")` 回看 DSL 源码，并填充 `GetFunctionMetadata`/`GetFunctionDoc` 提供内核签名与说明。

5. 通过格式标记（`"npu_dsl"` / `"npu_bin"`）承载"是否需要编译"的元信息，使 `load_from_bytes` 与 `create` 路径都能正确决策。

6. 保留失败诊断入口：DSL 编译失败时输出带行号的错误（配合视角195的错误因果链），把编译器诊断折叠进 FFI 错误对象一并上报。

## 相关概念

- [186 NPU FFI 集成总览](186-npu-ffi-integration-overview.md)：集成四层地图
- [187 VTA 类加速器设计](187-vta-style-accelerator-design.md)：模块三要素
- [194 NPU 运行时模块加载](194-npu-runtime-module-loading.md)：工厂与加载链路
- [197 NPU 性能分析追踪](197-npu-profiling-tracing.md)：源码回看与自省