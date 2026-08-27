---
type: Concept
title: "视角174：Pass 基础设施"
description: "分析 TVM Pass 基础设施如何借助 FFI 对象模型定义 PassContext/PassInfo/Pass/Sequential，实现 IR 变换的可组合与可反射调度。"
tags:
  - pass
  - ir
  - ffi
  - pass-context
  - transform
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-357
  - code:
    - include/tvm/ir/transform.h
    - include/tvm/ir/module.h
    - include/tvm/ir/instrument.h
---

# 视角174：Pass 基础设施

## 概述

Pass 是编译器 IR 变换的最小组织单元。TVM 的 Pass 基础设施（`include/tvm/ir/transform.h`）将 Pass 与 `IRModule` 一起建在 FFI 对象模型之上，使 Pass 既能被 C++ 直接调用，也能作为 `ffi::Function` 暴露给 Python 编排，还能被 Instrument 回调检视。

## 核心源码引用

`include/tvm/ir/transform.h` 定义核心类型（均已通过类型声明验证）：

- `PassContextNode : public ffi::Object`（transform.h:80）、`PassContext : public ffi::ObjectRef`（:151）；
- `PassInfoNode : public ffi::Object`（:336）、`PassInfo : public ffi::ObjectRef`（:367）；
- `PassNode : public ffi::Object`（:387）、`Pass : public ffi::ObjectRef`（:417）；
- `SequentialNode : public PassNode`（:461）、`Sequential : public Pass`（:508）。

`include/tvm/ir/module.h` 提供变换的对象：`IRModuleNode : public ffi::Object`（module.h:58）、`IRModule : public ffi::ObjectRef`（:255）。`include/tvm/ir/instrument.h` 的 `PassInstrumentNode : public ffi::Object`（:102）与 `PassInstrument : public ffi::ObjectRef`（:150）用于在 Pass 运行前后插桩。

## 设计分析

### Pass 即 FFI 对象

`Pass`、`PassInfo`、`PassContext` 全是 `ffi::ObjectRef` 子类，因此可被放入 `ffi::Array<Pass>`、作为 `ffi::Function` 参数传递，且能在 `PassContext` 的 instruments 列表中灵活插拔（对应视角 185 的 PassInstrument）。

### PassContext 的 with-语义

`PassContext`（transform.h:80）作为跨越多个 Pass 的共享上下文，通过 FFI 的反射字段承载配置（如编译目标、优化级别），并在进入/退出时触发 instruments 的 `EnterPassContext`/`ExitPassContext`（instrument.h:110-112）。

### 组合即 Sequential

`Sequential` 把多个 Pass 串联为单个 Pass 对象（transform.h:461-508），复用了 `ffi::ObjectRef` 的值语义，使其可安全共享、拷贝与序列化，从而支撑从单 Pass 到整条编译流水线的统一抽象。

### 编译期字段反射

`PassContext` 等对象通过 `refl::ObjectDef` 注册字段（对应 facts F-357 中 `TypeNode::RegisterReflection` 的 `def_ro` 模式），使编译配置对 Python 完全可见。这意味着用户可以构造一个 `ffi::Array<Pass>`，再将其整体交付给 `Sequential` 或 `PassContext` 编排，字段注册的运行时可见性正是这一编排能力的前提。

## 扩展讨论

### Pass 的三种身份

同一个 `Pass` 对象在 FFI 语境下可以扮演三种角色：作为编译器 C++ 侧的变换单元被直接调用；作为 `ffi::Function` 暴露给 Python 侧 `transform` 模块按名调用；作为被检视对象供 `Instrument` 在进入/退出时观察。三种身份共享同一个 `ffi::ObjectRef` 底层，无需复制状态，这也说明为何 Pass 体系没有为不同语言各自维护一套镜像对象。

### 错误与异常穿过 Pass 边界

Pass 执行过程中抛出的异常（例如 IR 校验失败、目标特性不匹配）会沿着 `ffi::Function` 的 `safe_call` 路径被包装、跨 FFI 边界传播（对应视角 045/046 的异常与 TLS 错误机制）。`PassContext` 除了承载优化配置，还承担了错误聚合职责——多个 Pass 的失败信息可以在上下文层面被 `PassInstrument` 收集，而非仅由单个 Pass 抛出后直接终止。

### 与编译流水线的组合视角

`Sequential` 把线性依赖的多 Pass 折叠为单个对象，但真实流水线往往呈现分叉与复用（如同一简化 Pass 应用于不同 IR 域）。由于 `Sequential`/`Pass` 都是值语义的 `ffi::ObjectRef`，同一 Pass 可以被安全地放进多个 `ffi::Array` 而不产生所有权问题，这正是「从单 Pass 到整条流水线统一抽象」得以成立的结构性保证。

### 面向 IR 演进与 NPU 的扩展

当 IR 或硬件后端演进时（例如新增设备指令的 lowering Pass），只需在调用链中添加新的 `Pass` 对象并登记进 `GlobalDef`，即可复用现有的容器、反射与插桩设施。NPU 流水线可把「设备命令生成」「内存分配」等阶段实现为独立 Pass，并通过 `PassInstrument` 监控其耗时与输入输出 IR 规模，得到可观测的端到端编译链路。

## 相关概念

- [185 Instrument 性能分析](185-instrument-performance-analysis.md)：`PassInstrument` 对 Pass 的插桩
- [173 Relax IR 与 FFI](173-relax-ir-ffi.md)：IR 对象底层
- [180 目标代码生成注册](180-target-codegen-registration.md)：Pass 流水线末端的注册表