---
type: Concept
title: "视角182：TE 张量表达式"
description: "分析 TE 张量表达式体系：Tensor/TensorNode 继承 ffi::Object 的 DataProducer 层级，ComputeOp/PlaceholderOp 以 IR 表达式描述算子，最终统一为可被 FFI 操控的对象。"
tags:
  - te
  - tensor-expression
  - ffi
  - data-producer
  - compute-op
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-355, F-373
  - code:
    - include/tvm/te/tensor.h
    - include/tvm/te/operation.h
    - include/tvm/ir/base_expr.h
---

# 视角182：TE 张量表达式

## 概述

TE（Tensor Expression）是 TVM 的算子表达 DSL，以「数据生产者（data producer）+ 计算操作（operation）」描述算子如何从一个张量推导出另一个张量。TE 的对象模型同样整体落在 FFI 类型系统上：`Tensor`、`Operation` 及其节点类型均以 `ffi::Object`/`ffi::ObjectRef` 为底盘，从而能与上文 TOPI 算子库（视角 181）无缝对接。

## 核心源码引用

`include/tvm/te/tensor.h`（已验证）：

- `class TensorNode : public DataProducerNode`（tensor.h:70）、`class Tensor : public DataProducer`（tensor.h:100）。

`include/tvm/te/operation.h`（已验证）：

- `class PlaceholderOpNode : public OperationNode`（operation.h:101）；同族还应有 `ComputeOpNode`、`TensorComputeOpNode` 等，它们统一表达「输入数据有向无环图」的节点。

底层 IR 表达式复用 `include/tvm/ir/base_expr.h` 的 `TypeNode : public ffi::Object`（:52）/`Type : public ffi::ObjectRef`（:77），使 TE 的类型标注与 TIR 共用一套 FFI 对象。

## 设计分析

### 数据生产者抽象

`TensorNode : public DataProducerNode`（tensor.h:70）把「张量」抽成数据生产者的一个特化：一个 `Tensor` 可由 `PlaceholderOp`（占位输入）或 `ComputeOp`（计算结果）产生，而消费者只需面向 FFI 对象做类型分发，不关心具体哪个操作产出它。

### 算子=IR 表达式的对象化

`ComputeOp` 等用 IR 表达式描述循环与访存，这些表达式节点本身是 `ffi::Object` 子类。因此算子的「结构相等、序列化、反射」全部继承自 FFI 基建，编译器可以在不丢失对象身份的前提下对算子图做 Pass 变换与自动调度。

### 与 TOPI 的桥接

TE 提供算子语义，TOPI 用 `refl::GlobalDef().def_packed("topi.nn.dense", ...)`（视角 181）把它发布为全局函数。二者以 FFI 对象/函数为共同语言，构成「TE 定义算子 → TOPI 登记 → 后端起调」的完整链路。

## 扩展讨论

### 为何 DataProducer 是一层独立抽象

把 `Tensor` 抽为 `DataProducer`（tensor.h:70）的特化，是为了让「一个张量由哪个操作产生、被哪些操作消费」形成统一的可查询契约。编译器沿 `DataProducer` 遍历可得到算子图的拓扑序，而无需针对 `PlaceholderOp`/`ComputeOp` 分别编写遍历逻辑。这一层抽象让调度、阶段划分与代码生成共享同一份图遍历语义。

### 占位符与计算操作的对照

`PlaceholderOpNode`（operation.h:101）走私一个没有计算体的「输入占位符」，`ComputeOp` 则携带真实的 lambda 与循环结构。二者通过 `DataProducer` 收敛为同一种对象后，TE 图即成为「输入节点 + 计算节点」的统一有向无环图——对后续 Pass 而言只剩「供数」与「算数」的差异，属性访问（shape、dtype）保持一致。TVM 在 Typical 的消融/合成阶段能据此统一处理输入与中间结果。

### 结构相等与缓存

`Tensor`/`Operation` 继承 FFI 的结构相等语义（`StructuralEqual`），这使编译器可以对完全相同的计算子图做公共子表达式消去，并对缓存命中判定做出可靠依据。两次计算若生成 `StructuralEqual` 的 `TensorNode`，调度层即可复用先前方案，是 TVM 自动调度可增量复用结果的前提。

### 对 NPU 算子的延伸

TE 描述「如何算」，但不限定「在哪算」。NPU 算子只要同样产出 `Tensor`/`Operation` 对象，并以其 `DataProducer` 结构加入图，调度层便能识别其访存与依赖关系，进而生成设备命令。这让自定义设备算子（见视角 193）与通用算子在同一张 TE 图上被统一编排。

## 相关概念

- [181 TOPI 算子库](181-topi-op-library.md)：TE 算子的对外发布
- [172 TIR 表达式与 FFI](172-tir-expression-ffi.md)：底层 IR 表达式对象
- [183 Arith 简化器](183-arith-simplifier.md)：调度推导的算术化简