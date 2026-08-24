---
type: Concept
title: "视角096：Def Region 语义"
description: "解析 TVMFFIDefRegionKind 枚举与字段标志 SEqHashDefRecursive/NonRecursive 的形式语义：自由变量的绑定作用域、递归与非递归 def 区域的区别，以及在编译器 IR α 等价比较中的应用。"
tags:
  - reflection
  - def-region
  - free-var
  - alpha-equivalence
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-255, F-261
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/registry.h
---

# 视角096：Def Region 语义

## 概述

Def Region（定义区域）是 TVM FFI 结构化相等/哈希系统中用于表达自由变量绑定作用域的机制。它通过 `TVMFFIDefRegionKind` 枚举（`include/tvm/ffi/c_api.h:1130`）与字段级标志 `kTVMFFIFieldFlagBitMaskSEqHashDefRecursive`（1<<4）、`kTVMFFIFieldFlagBitMaskSEqHashDefNonRecursive`（1<<12）共同控制比较器在遍历对象字段时如何引入和解析自由变量。这一机制借鉴了 λ 演算与逻辑证明论中的"绑定位点"概念，是编译器 IR 实现正确 α 等价比较的关键。

## TVMFFIDefRegionKind 枚举

`TVMFFIDefRegionKind`（`c_api.h:1130-1174`）定义比较器当前所处的绑定上下文：

- **`kTVMFFIDefRegionKindNone = 0`**：不在 def 区域中。通过该字段可达的自由变量被视为"使用"（use），必须已由外层 def 区域绑定；若未绑定，相等性回退到指针身份比较。
- **`kTVMFFIDefRegionKindRecursive = 1`**：处于递归 def 区域。首次见到的自由变量被定义（define），且该变量的子字段（如其类型注解、形状参数中的自由变量）仍处于同一 def 区域，内部发现的自由变量也在同一位点绑定为新变量。
- **`kTVMFFIDefRegionKindNonRecursive = 2`**：处于非递归 def 区域。首次见到的自由变量被定义，但其子字段不在 def 区域——子字段中的自由变量被视为使用，必须解析到外层绑定。

## 递归与非递归的区别

源码注释（`c_api.h:1142-1168`）给出了明确语义与典型用例：

**递归 def（Recursive）**：适用于"函数式"绑定。注释举例：函数参数列表中，值变量及其类型中出现的形状参数在同一绑定位点共同引入。例如函数参数 `x: Tensor[(n, m), float32]`，比较时 `x`、`n`、`m` 同时被绑定为新变量，右侧对应位置的变量无论名称是否相同都视为等价。

**非递归 def（NonRecursive）**：适用于"let 风格"绑定。注释举例：一个普通绑定的值类型包含形状参数时，值变量本身被引入为新变量，但其形状参数引用的是外层作用域已定义的变量，不应被重新绑定。若子字段中出现未绑定的自由变量，相等性判定失败。

## 字段标志

两个字段标志控制进入字段时切换到何种 def 区域：

- `kTVMFFIFieldFlagBitMaskSEqHashDefRecursive`（`c_api.h:983`）：该字段进入递归 def 区域。C++ 层通过 `AttachFieldFlag::SEqHashDefRecursive()`（`registry.h:232`）设置。
- `kTVMFFIFieldFlagBitMaskSEqHashDefNonRecursive`（`c_api.h:1053`）：该字段进入非递归 def 区域。C++ 层通过 `AttachFieldFlag::SEqHashDefNonRecursive()`（`registry.h:243`）设置。

注释说明位 12 的选择是因为位 1<<5 到 1<<11 已被其他字段标志占用（`c_api.h:1050-1052`）。若两个标志均未设置，字段继承当前 def 区域状态（`kTVMFFIDefRegionKindNone` 或外层传入的状态）。

## 与 SEqHashKind 的协作

Def Region 语义与类型级 `TVMFFISEqHashKind`（视角095）正交但协作：

- 类型被标记为 `kTVMFFISEqHashKindFreeVar` 的对象在 def 区域内首次出现时被绑定。
- 字段标志决定绑定的作用域深度（递归 vs 非递归）。
- `kTVMFFISEqHashKindDAGNode` 类型的对象即使在 def 区域内也保持 DAG 共享识别。
- 比较器维护一个从左侧自由变量到右侧自由变量的映射表，在 def 区域内建立映射，在 use 位置查询映射。

## 比较流程

在启用 `map_free_vars=true` 的结构比较中，遍历字段时：

1. 检查字段是否携带 `SEqHashDefRecursive` 或 `SEqHashDefNonRecursive` 标志，决定进入该字段时的 def 区域种类。
2. 若字段值为 `FreeVar` 类型且当前在 def 区域中：首次遇到时在映射表中建立左右变量的绑定；后续遇到时查询映射表判定等价。
3. 递归区域中，变量的子字段继续在同一区域处理；非递归区域中，子字段以 `None` 区域处理。
4. 若 use 位置的自由变量未在映射表中绑定，回退到指针身份比较。
5. 退出字段时恢复外层 def 区域状态。

## 设计分析

Def Region 机制将编程语言理论中的绑定结构概念编码为反射元数据，使通用结构比较器无需理解具体 IR 语法即可正确处理 α 等价。递归与非递归的区分精确捕捉了"函数参数（绑定及其类型注解共引入）"与"let 绑定（仅值引入，类型引用外层）"两种根本不同的作用域规则。这一设计避免了为每种 IR 节点编写自定义比较器的需要，同时通过标志位保持了极低的运行时开销。对于不涉及变量绑定的类型，标志位为零，比较器行为退化为普通树比较，不引入额外复杂度。这体现了 TVM FFI "为编译器领域量身定制但以通用机制表达"的设计哲学。

## 相关概念

- [094 结构化相等与哈希](094-structural-equal-hash.md)：Def Region 的消费框架
- [095 SEqHash 种类](095-seq-hash-kind.md)：FreeVar 类型与 Def Region 协作
- [093 字段标志位系统](093-field-flags.md)：DefRecursive/NonRecursive 标志
- [098 自定义哈希/相等注册](098-custom-hash-eq.md)：自定义钩子可覆盖默认 Def 行为
