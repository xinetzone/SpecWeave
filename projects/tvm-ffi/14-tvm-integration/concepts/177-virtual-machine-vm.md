---
type: Concept
title: "视角177：虚拟机 VM（NPU 建议）"
description: "分析 Relax VM 如何以 ffi::ModuleObj 为基类承载执行状态，通过 ffi::Function/PackedArgs 调用 packed 函数，并用 VMExtension 支持目标后端扩展。"
tags:
  - virtual-machine
  - ffi
  - relax-vm
  - module-obj
  - extension
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-375
  - code:
    - include/tvm/runtime/vm/vm.h
    - include/tvm/runtime/vm/executable.h
    - include/tvm/ffi/extra/module.h
---

# 视角177：虚拟机 VM（NPU 建议）

## 概述

Relax VM 是执行编译后模型字节码的运行时虚拟机。`include/tvm/runtime/vm/vm.h` 直接 `#include <tvm/ffi/extra/module.h>`（vm.h:26），`VirtualMachine` 继承 `ffi::ModuleObj`（vm.h:126），说明 VM 本身就是一个 FFI 模块对象——既可被 Python 持有，也可作为 `ffi::Function` 分发入口。本案剖析其执行状态、调用约定与扩展机制。

## 核心源码引用

`include/tvm/runtime/vm/vm.h`（已验证）：

```cpp
// :126  -- VM 本身就是可加载的 FFI 模块
class VirtualMachine : public ffi::ModuleObj {
 public:
  virtual void Init(const std::vector<Device>& devices,
                    const std::vector<AllocatorType>& alloc_types) = 0;   // :133
  virtual void LoadExecutable(ffi::ObjectPtr<VMExecutable> exec) = 0;     // :139
  virtual VMClosure GetClosure(const ffi::String& func_name) = 0;         // :145
  virtual void InvokeClosurePacked(const ffi::ObjectRef& closure_or_packedfunc,
                                   ffi::PackedArgs args, ffi::Any* rv) = 0; // :152
  virtual void SetInstrument(ffi::Function instrument) = 0;               // :173
  template <typename T> T GetOrCreateExtension() { ... }                  // :182
  static ffi::ObjectPtr<VirtualMachine> Create();                          // :199
  static VirtualMachine* GetContextPtr(ffi::AnyView arg) { ... }          // :204
};
```

支撑类型还包括 `VMClosureObj : public ffi::Object`（:61）、`VMExtensionNode : public ffi::Object`（:104）。`.cc` 侧实现可见于 `src/runtime/vm/vm.cc`。

## 设计分析

### VM 即 FFI 模块

继承 `ffi::ModuleObj` 意味着 VM 的生命周期、GetFunction 契约与可序列化能力全部来自 FFI 模块层（视角 175）。用户以 `ffi::Function` 从 VM 取闭包并调用，无需感知 VM 内部如何执行字节码。

### 统一调用约定

`InvokeClosurePacked` 接受「VM 闭包或 packed 函数」二选一，统一以 `ffi::PackedArgs args` 为入口、`ffi::Any* rv` 为出口。因此对调用方而言，闭包与普通 `ffi::Function` 无差别——这正是 FFI 函数一等淡淡语义（facts F-135/137）在 VM 层的落地。

### 闭包捕获

`VMClosure::BindLastArgs(ffi::Function, last_args)`（vm.h:93）把「以最后参数绑定」的闭包捕获封装为一个新的 `ffi::Function`，支撑高阶函数与部分应用。

### 目标扩展点

`VMExtension`/`VMExtensionNode`（vm.h:104-113）允许为目标后端注入专用逻辑，`GetOrCreateExtension<T>()`（vm.h:182）按类型索引在 `extensions` 映射中懒创建并持引用，与 VM 同生命周期。

### 上下文指针传递

`GetContextPtr(ffi::AnyView arg)`（vm.h:204）把 VM 自身指针作为首个隐藏参数传给闭包，闭包在同一执行上下文内由此取得 VM 状态，避免全局查找。

## 扩展讨论

### VM 继承 ffi::ModuleObj：把"执行器"变成可寄居的可加载对象

`VirtualMachine : public ffi::ModuleObj` 这一继承关系是理解 VM 如何嵌入 FFI 生态的钥匙：VM 的生命周期、`GetFunction` 契约、可序列化能力全部复用模块层（视角 175）。对该者而言，VM 就是又一个可被 Python 持有、可被 `ffi::Function` 分发入口触碰的模块对象——内部如何解码字节码、如何管理寄存器栈都被封装在内。这把「Runtime 执行器」与「FFI 可调对象」统一为同一抽象，降低集成方的认知门槛。

### 闭包与 packed 函数一视同仁：FFI 函数一等公民在 VM 落地

`InvokeClosurePacked` 接受「VM 闭包或 packed 函数」二选一、统一以 `ffi::PackedArgs args` 为入口、`ffi::Any* rv` 为出口，呼应 FFI「函数是一等对象」的核心语义（facts F-135/137）。`VMClosure::BindLastArgs` 再把「按末参数绑定」的闭包捕获重封装为新的 `ffi::Function`，支撑高阶函数与部分应用。对调用方而言闭包与普通函数无差别，正是 FFI 函数抽象在 VM 执行层的自然延伸。

### VMExtension + GetContextPtr：为后端扩展留"旁路"而不污染主契约

`VMExtension`/`VMExtensionNode` 允许注入目标后端专用逻辑，`GetOrCreateExtension<T>()` 按类型懒创建并持引用；`GetContextPtr` 把 VM 自身作为闭包首个隐藏参数传递。这两者配合的意义在于：NPU 等后端的专属能力（设备/流/内存池）都收敛进扩展与上下文参数，而 `InvokeClosurePacked` 的通用 `ffi::PackedArgs` 契约保持纯净——新增后端无需改动 VM 主执行路径，只在扩展点上接线即可。

## NPU 建议

1. 为 NPU 定义 `VMExtension`（如 `NPUVMExecutor` 子类承载 NPU 设备/流/内存池），经 `GetOrCreateExtension<NPU...>()` 懒初始化，避免 VM 初始化时强制拉起 NPU 驱动。
2. 在 `Init` 阶段为 NPU 设备注册对应 `Allocator`（`AllocatorType`），让 VM 的 K/V 与临时张量分配直接落入 NPU 内存池。
3. 用 `SetInstrument` 挂 NPU 性能探针（before/after 每次 Call），量化 NPU 算子耗时与调度间隙（接视角 185）。
4. 把 NPU 特定逻辑收敛进 `VMExtension` 与闭包第一个上下文参数，保持 `InvokeClosurePacked` 的通用 `ffi::PackedArgs` 契约不被 NPU 细节污染。

## 相关概念

- [178 字节码执行](178-bytecode-execution.md)：VM 执行的具体指令
- [175 Module 系统集成](175-module-system-integration.md)：VM 的模块化底座
- [179 KV State 管理](179-kv-state-management.md)：VM 侧的记忆状态对象
- [185 Instrument 性能分析](185-instrument-performance-analysis.md)：VM 级插桩