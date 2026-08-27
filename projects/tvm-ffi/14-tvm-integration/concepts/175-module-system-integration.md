---
type: Concept
title: "视角175：Module 系统集成"
description: "分析 FFI Module（ModuleObj/Module）如何作为运行时可加载对象的统一抽象，被 IRModule、VMExecutable、RPC 会话等复用，实现二进制可序列化模块的集成。"
tags:
  - module
  - ffi
  - ir-module
  - dynamic-loading
  - serialization
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-301, F-302, F-303, F-304, F-374
  - code:
    - include/tvm/ffi/extra/module.h
    - include/tvm/ir/module.h
    - include/tvm/runtime/vm/executable.h
    - src/runtime/rpc/rpc_session.h
---

# 视角175：Module 系统集成

## 概述

Module 是 TVM 把「编译产物 / 运行时可加载对象」统一为 FFI 对象的抽象。FFI 基础层在 `src/ffi/extra/module.cc` 中定义 `ModuleNode` 与 `Module`（facts F-301/302），并在 `include/tvm/ffi/extra/module.h` 中固化为 `ModuleObj` 与 `Module`。这一抽象被 IRModule（编译期模块）、VMExecutable（VM 字节码模块）、RPC 会话模块等广泛复用。

## 核心源码引用

`include/tvm/ffi/extra/module.h`（已验证）：

- `ModuleObj`：虚基，声明 `virtual Optional<Function> GetFunction(const String& name) = 0`（:62）与 `ImplementsFunction`（:73）等接口；
- `Module : public ObjectRef`（:218）：封装 `ModuleObj`，提供 `Optional<Function> GetFunction(name, query_imports)`（:147）、`Optional<String> GetFunctionDoc`（:163）等；
- `static Module LoadFromFile(const String& file_name)`（:264）：从共享库文件加载模块。

`include/tvm/runtime/vm/executable.h` 中 `VMExecutable : public ffi::ModuleObj`（:89）在同一文件展示 Module 如何支撑自定义加载器（`LoadFromBytes`/`SaveToBytes`，executable.h:127-149）。`include/tvm/ir/module.h` 的 `IRModule : public ffi::ObjectRef`（:255）则代表编译期模块。

## 设计分析

### 统一的 Find-Function 契约

`Module::GetFunction(name)` 是跨所有模块形态的统一入口。无论模块是 `.so`、VM 字节码还是 RPC 远端会话，调用方都以同一 `ffi::Function` 语义去取函数；运行时差异（加载、导入、远端代理）被 Module 内部封装。`FEncodeReturn`/`FAsyncCallback` 等 RPC 回调也回落到 `ffi::PackedArgs`（rpc_session.h:82-90），可见 Module 与函数约定深度耦合。

### 二进制可序列化

`ffi::Module::kBinarySerializable` 属性（executable.h:92）与 `SaveToBytes`/`LoadFromBytes` 使模块能在不同设备与进程间迁移。`VMExecutable` 通过覆写 `GetPropertyMask` 声明自身可序列化，再由 FFI 的 `Bytes`/`String` 与序列化器实现落盘。

### 单一对象世界

`ffi::Module`/`ModuleObj`、`IRModule`、`VMExecutable` 共享同一 FFI 对象底盘，使编译产物、运行产物、远端句柄能在不转换身份的前提下互操作。这正对应 facts F-374 所述 "ModuleNode 继承 ffi::Object，Module 继承 ffi::ObjectRef" 的同步设计。

## 扩展讨论

### 从编译期模块到运行期模块的身份转换

关键在于 `IRModule` 与 `Module` 是两个不同但同底座的类型：前者描述编译期 IR 对象图，后者描述运行时可加载产物。二者都继承 `ffi::ObjectRef`，因此可以在完成编译后，通过 `Module::LoadFromFile` 或 `SaveToBytes/LoadFromBytes` 把 IR 变换为可序列化的执行模块，而句柄语义（按名 `GetFunction`）在两端保持一致。用户从「编程 IR」到「运行模块」的切换不跨对象范式。

### GetFunction 的导入语义

`Module::GetFunction(name, query_imports)`（module.h:147）的第二个参数体现模块可携带依赖：一个模块可以导入若干被依赖模块，形成模块图。这在实际运行时（RPC 会话、多后端加载）尤为重要——同一名称可能落在某个被导入的依赖上，Module 负责按依赖关系解析，而非仅查自身导出表。

### 可序列化的判定与掩码

`kBinarySerializable` 与 `GetPropertyMask` 把「可序列化」提升为模块的能力声明，而非固定的类型属性（executable.h:92）。VMExecutable 通过覆写掩码表明自己可 `SaveToBytes/LoadFromBytes`，这意味着新增一种模块形态时，只需在掩码中声明其能力，FFI 的持久化/远端传输基建便可复用，无需为每种模块单独编写传输插件。

### 与现代加载链路的配合

Module 抽象天然契合 NPU 与异构后端：只需一个 `ModuleObj` 实现即可把「设备镜像或自研加载器的可调用入口」暴露为 `GetFunction` 返回的 `ffi::Function`。于是统一查询、统一序列化、统一错误传播都对跨硬件产物成立，运行时无需区分函数究竟来自宿主 `.so`、VM 字节码还是远端 NPU 服务。

## 相关概念

- [171 TVM 运行时 FFI 应用](171-tvm-runtime-ffi-application.md)：运行时对 FFI 的全面依赖
- [177 虚拟机 VM](177-virtual-machine-vm.md)：`VirtualMachine : public ffi::ModuleObj`
- [176 RPC 服务端/客户端](176-rpc-server-client.md)：远端会话的 Module 封装
- [180 目标代码生成注册](180-target-codegen-registration.md)：编译器产物注册