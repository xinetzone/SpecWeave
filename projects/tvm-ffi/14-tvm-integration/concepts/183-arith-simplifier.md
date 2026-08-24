---
type: Concept
title: "视角183：Arith 简化器"
description: "分析 Arith 分析器（Analyzer/IntSetAnalyzer/ConstraintContext）在 FFI 对象模型之上提供的边界与整数集合分析，支撑调度、边界检查与源代码生成。"
tags:
  - arith
  - analyzer
  - int-set
  - bound
  - constraint
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-355
  - code:
    - include/tvm/arith/analyzer.h
    - include/tvm/arith/bound.h
    - include/tvm/arith/int_set.h
---

# 视角183：Arith 简化器

## 概述

Arith 简化器（`tvm::arith`）为编译器提供算术分析能力，包括边界推断（bounds）、整数集合分析（int-set）与带约束的求值。`include/tvm/arith/analyzer.h` 的 `Analyzer` 本身是 `ffi::ObjectRef`（analyzer.h:927），其分析结果以 IR 表达式（`ffi::Object` 子类）表示，因此能直接嵌入 Pass 流水线并被 FFI 消费（facts F-355）。

## 核心源码引用

`include/tvm/arith/analyzer.h`（已验证）：

- `class Analyzer : public ffi::ObjectRef`（analyzer.h:927）：统一入口，封装数论/符号化/线性/仿射/整数集合等子分析器；
- `class IntSetAnalyzer`（analyzer.h:546）：整数集合分析；
- `class ConstraintContext`（analyzer.h:953）与 `class VarConstraintContext`（analyzer.h:...，经 friend 声明于 :181/261...）：以 RAII 方式在分析期间引入临时约束。

`include/tvm/arith/bound.h`、`include/tvm/arith/int_set.h` 分别承载 `Analyzer::ConstIntBound`、上/下界与 `IntSet` 的顶/底等表示。

## 设计分析

### 统一对象化入口

`Analyzer : public ffi::ObjectRef`（analyzer.h:927）把数论、符号、线性、仿射、整数集合、模等分析模块聚合为单一对象。每次分析构造时在内部建 `AnalyzerObj`，其生命周期受 `ffi::ObjectRef` 引用计数管理，可被放进 `PassContext` 或作为参数跨 FFI 传入。

### RAII 约束上下文

`ConstraintContext`（analyzer.h:953）在进入作用域时向分析器压入临时前提、退出时弹出，从而在受限范围内（如已断言 `0 <= i < 1024`）做精确化简，避免全局污染。这类上下文对象复用 C++ 作用域与 FFI 对象身份，精确而不泄漏。

### 服务场景

边界分析为「边界检查消除」与「源代码生成中的整型宽度推导」提供依据；整数集合分析用于循环展开与依赖分析。其结果作为普通 IR 表达式返回，天然融入视角 174 的 Pass 链。

## 扩展讨论

### 分析器是 ObjectRef：为什么"分析入口"也走对象模型

`Analyzer : public ffi::ObjectRef`（analyzer.h:927）是对传统"纯函数式/无状态分析器"的偏离——它选择把分析器本身做成一个可被引用计数管理的对象。收益是：一个 `Analyzer` 的多次调用之间可以共享累积的内部状态（如已建立的假设与约束），而不再是无状态的纯函数；同时它可被放进 `PassContext` 或作为参数跨 FFI 传入，使算术分析能力同样进入 FFI 的统一边界。代价是引入了对象生命周期管理，但正因如此它才成为"编译器能力被 FFI 化消费"的一环。

### RAII 约束上下文：临时前提的"作用域即生命周期"

`ConstraintContext`（analyzer.h:953）在进入作用域时压入临时前提、退出时弹出，这是 C++ RAII 原语与 FFI 对象身份的结合。它解决的核心问题是"约束污染的局部性"：若只在已断言 `0 <= i < 1024` 的范围内做精确化简，就必须保证这个前提随作用域结束自动撤销，否则一次分析建立的假设会悄悄污染后续无关分析。构造函数入前置、析构函数出前置，使约束的存在时间与代码块的生命周期严格对齐，精确而不泄漏。

### 分析结果作为普通 IR 表达式：平滑嵌入 Pass 链

`Analyzer` 的边界与整数集合分析结果都以 IR 表达式（`ffi::Object` 子类）返回，而非偏离 IR 的专有结构。这一选择的优势是分析产物与编译器主数据结构同构——可以直接作为已有 Pass 的输入再次变换，也可被 FFI 传递；下游（边界消除、循环展开、宽度推导）无需在"IR 世界"与"分析器世界"之间做翻译。循环依赖分析、依赖推导也就自然融入视角 174 的 Pass 基础设施，而非旁挂一条孤立工具链。

## 相关概念

- [174 Pass 基础设施](174-pass-infrastructure.md)：分析的调用上下文
- [182 TE 张量表达式](182-te-tensor-expression.md)：调度推导依赖的化简
- [172 TIR 表达式与 FFI](172-tir-expression-ffi.md)：分析结果的表达式表示