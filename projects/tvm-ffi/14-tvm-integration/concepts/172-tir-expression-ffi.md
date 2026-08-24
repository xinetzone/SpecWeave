---
type: Concept
title: "视角172：TIR 表达式与 FFI"
description: "分析 TIR 表达式体系的类型节点如何继承 ffi::Object、通过 refl::ObjectDef 注册反射字段，展示 IR 编译期对象在 FFI 类型系统下的落地方式。"
tags:
  - tir
  - ir
  - ffi
  - reflection
  - type-node
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-355, F-373
  - code:
    - include/tvm/ir/base_expr.h
    - include/tvm/ir/expr.h
    - src/ir/expr.cc
---

# 视角172：TIR 表达式与 FFI

## 概述

TIR（Tensor Intermediate Representation）是 TVM 编译器中间层表达式体系。`include/tvm/ir/base_expr.h` 是本体系与 FFI 交汇的最直观窗口：头文件直接 `#include <tvm/ffi/cast.h>`、`<tvm/ffi/dtype.h>`、`<tvm/ffi/reflection/registry.h>`、`<tvm/ffi/string.h>`（base_expr.h:27-30），说明 IR 对象类型直接以 FFI 基础类型为底盘。

## 核心源码引用

类型节点构成一个继承链：

```cpp
// include/tvm/ir/base_expr.h
class TypeNode : public ffi::Object { ... };        // :52
class Type : public ffi::ObjectRef { ... };         // :77
class PrimTypeNode final : public TypeNode { ... }; // :95，含 DLDataType dtype 字段
class PrimType final : public Type { ... };         // :113
```

`TypeNode::RegisterReflection`（base_expr.h:60-65）使用 `refl::ObjectDef<TypeNode>().def_ro("span", &TypeNode::span, ...)` 注册只读字段，把 C++ 字段暴露给反射与 Python 侧。`TypeNode` 的 `_type_index` 使用 `kTVMFFITypeIndexDynamicBegin`（动态分配），因为 IR 类型节点数量在编译期无法静态枚举，需运行时向 `TypeTable` 登记索引（对应 facts F-356）。

`PrimTypeNode` 在 `TypeNode` 之上仅增加一个 `DLDataType dtype` 字段，`PrimType` 则提供工厂方法 `Int(bits, lanes)`、`UInt`、`Float`、`BFloat`、`Bool`、`Void()`（base_expr.h:113-148），沿用 `ffi::DataType` 的命名习惯。

## 设计分析

### IR 对象 == FFI 对象

把 `TypeNode` 直接继承 `ffi::Object`、`Type` 继承 `ffi::ObjectRef` 意味着：每个 IR 类型节点天然拥有 FFI 的引用计数、类型索引、反射表与结构相等语义。编译器无需为 IR 单独保留一套对象基建，IR 对象可以直接穿越 FFI 边界进出 Python/Rust。

### 动态类型索引

静态类型做静态索引（`_type_index` 编译期常量），IR 用户类型做动态索引（`kTVMFFITypeIndexDynamicBegin` 起），两者在同一个全局 `TypeTable` 中共存。这是 FFI「静态优先、动态兜底」策略在编译器层的体现：内建类型零开销，扩展类型可插拔。

### 反射登记

借助 `refl::ObjectDef` 链式 API（base_expr.h:60-65）声明字段，编译器只在头文件中用几行代码便让 `span`、`dtype` 等字段对 Python 可见，无需手写 getter/setter 胶水。

## 扩展讨论

### 编译期类型与 IR 类型的边界如何划分

`TypeNode` 家族的 `PrimType`、`FuncType` 等是 IR 层面表达「类型」的对象，而 `ffi::TypeIndex` 枚举是 C++ 层面表达「对象运行时类型标识」的标签。前者描述程序数据的类型，后者描述 FFI 对象自身的类型。本案强调 `TypeNode._type_index` 用动态索引（`kTVMFFITypeIndexDynamicBegin`），正是因为 IR 类型实例在编译期不作为 C++ 模板参数展开——它们需要在运行时创建、枚举与反射，故归入动态段而与 `ffi::DataType`（`kTVMFFIDataType`）静态索引区分。

### 工厂方法背后的类型安全

`PrimType::Int(bits, lanes)`（base_expr.h:113-148）等工厂方法之所以必需，是因为 FFI 边界上传入的是不含编译期信息的 `DLDataType` 或`DataType`。Int/UInt/Float/BFloat 工厂把「bit 位宽 × lanes」组合约束为合法类型，避免在 IR 中构造非法位宽的 `PrimType`，从源头保证类型合法性。

### 与 TIR 表达式、Pass 的串接

有了 `TypeNode` 对 span/dtype 的反射字段，Pass 在改写 TIR 时既能读取节点类型信息，也能保留或更新其 source range，从而在不破坏诊断链条（视角 184）的前提下做合法类型变换。反射字段与动态类型索引共同支撑了编译器「对象即数据」的编辑体验。

### 多语言一致性的内核

C++ 定义 `TypeNode`、Python 经反射读其字段、Rust 经 `ffi::Object` 包装参与变换，三端看到的都是同一对象模型。这正是把"编译器 IR 也建在 FFI 上"的价值：语言边界不再是对象边界，IR 节点可无痛穿梭于前端脚本与后端镜像加载之间。

## 相关概念

- [172 TIR 表达式与 FFI](172-tir-expression-ffi.md)：类型节点基建
- [173 Relax IR 与 FFI](173-relax-ir-ffi.md)：高阶 IR 对同一模式的复用
- [174 Pass 基础设施](174-pass-infrastructure.md)：IRModule 上的 Pass 遍历
- [184 Source Map](184-source-map.md)：`Span` 字段的来源定位