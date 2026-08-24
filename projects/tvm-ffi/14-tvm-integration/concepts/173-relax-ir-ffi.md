---
type: Concept
title: "视角173：Relax IR 与 FFI"
description: "分析 Relax 高阶 IR 的三类节点（Expr/Binding/Var）如何统一继承 FFI 对象模型，借助 ObjectRef 与反射实现从前端到 VM 字节码的无缝落地。"
tags:
  - relax
  - ir
  - ffi
  - object-ref
  - object-model
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-355, F-358, F-373
  - code:
    - include/tvm/ir/base_expr.h
    - include/tvm/relax/expr.h
    - include/tvm/relax/analysis.h
---

# 视角173：Relax IR 与 FFI

## 概述

Relax 是 TVM 面向高性能端到端模型的高阶 IR，承载数据流图、绑定与函数抽象。它复用了与 TIR 相同的 FFI 对象模型：所有节点最终继承 `ffi::Object`，所有引用类型继承 `ffi::ObjectRef`。本案考察 Relax 如何在 FFI 类型系统之上组织其三大类结构——表达式、绑定与变量。

## 核心源码引用

`include/tvm/relax/expr.h` 定义核心节点（已验证存在）：

- `relax::Expr` / 具体子类 `Constant`、`Var`、`VarBinding`（继承 `BindingNode` → `Binding`）；
- `relax::Function : public BaseFunc`（expr.h:540）；
- `ConstantNode : public ExprNode`（expr.h:162）、`Constant : public Expr`（expr.h:180）。

`include/tvm/ir/base_expr.h` 提供 `TypeNode : public ffi::Object`（:52）与 `Type : public ffi::ObjectRef`（:77，对应 facts F-358），构成 Relax 表达式类型标注的基类。

## 设计分析

### 三类结构的统一底座

Relax 的表达式树、绑定关系、函数头都以 FFI ObjectRef 为句柄。这意味着它们共享同一套生命周期管理（引用计数 `IncRef`/`DecRef`）、同一套结构相等（`StructuralEqual`）与同一套反射（`refl::ObjectDef`）。前端的 `relax::Var` 经编译后能直接映射到 VM 的寄存器符号，这依赖 FFI 的 `ffi::String`、`ffi::Function` 等类型在编译期与运行期之间稳定传输。

### 类型擦除贯穿全链路

Relax 的 `Constant`、`VarBinding` 等对象常被封装进 `ffi::Array<Binding>` 或作为 `ffi::Function` 的参数传入 Pass。FFI 的容器（`ffi::Array`、`ffi::Map`）与 `Any` 类型擦除机制，使 Relax IR 在进入编译管线时无需逐对象具形就能被主机语言操控。

### 从 IR 到 VM 的连续对象世界

Relax 的高阶 IR 最终被编译为 `runtime::vm` 的字节码，而 VM 的 `VirtualMachine`、`VMExecutable` 同样继承 `ffi::ModuleObj`、`ffi::Object`（见视角 177/178）。这构成「前端 IR 对象 → 后端运行时对象」的连续 FFI 对象世界，减少两端的转换鸿沟。

## 扩展讨论

### 为何 Binding 与 Expr 分开建模

Relax 把绑定（`VarBinding` 等）与表达式（`Expr`）分开，是为了让数据流图可被显式地作为一等成员处理：绑定节点描述「变量 ← 表达式」的指派关系，表达式描述纯值计算。区分二者后，编译器可对绑定做具体化、内联与死代码消除，而不必在表达式树上反向推导数据依赖。二者同为 `ffi::ObjectRef`，可无差异地装入 `ffi::Array<Binding>` 或作为 Pass 参数传递。

### 变量作用域即对象作用域

`relax::Var` 从创建到被引用都持有 FFI 句柄，作用域信息天然随对象保存。Pass 需要做自由变量收集（`relax::analysis.h` 的 `FreeVars` 等）时，可借助对象身份与结构相等语义精确识别同一变量，避免以字符串名或地址等脆弱键做比对。这使高层 IR 的别名与作用域分析既可靠又跨语言一致。

### 数据结构借用 FFI 容器

Relax 的函数体常以一个 `ffi::Array<VarBinding>` 表达，函数参数为 `ffi::Array<Var>`。FFI 容器（视角 051-064）在此承担着色器、序列化与反射三重职责：同一数据结构既能为编译期 Pass 提供遍历，又能被 Python 侧读取，还能随模块序列化落盘。

### 面向 VM 寄存器分配的一致性

Relax 的 `Var` 与 VM 的寄存器符号一一对应，这种对应之所以平滑，正是因为两边都基于 FFI `String`/`Object` 的稳定标识。编译后 `VarBinding` 被翻译为设值指令、函数调用被翻译为调用指令，对象世界的一致性让 lowering 各阶段能保留精确的调试与错误映射信息。

## 相关概念

- [172 TIR 表达式与 FFI](172-tir-expression-ffi.md)：低阶类型节点基建
- [174 Pass 基础设施](174-pass-infrastructure.md)：对 IRModule 的变换支撑
- [177 虚拟机 VM](177-virtual-machine-vm.md)：Relax 的运行时载体
- [178 字节码执行](178-bytecode-execution.md)：IR 最终落地的指令序列