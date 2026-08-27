---
type: Concept
title: "视角093：字段标志位系统"
description: "解析 TVMFFIFieldFlagBitMask 枚举的十三位标志：可写、有默认值、静态方法、SEqHash 忽略/Def 区域、默认工厂、repr/compare/hash/init 控制、kw_only、setter 为函数对象等。"
tags:
  - reflection
  - field-flags
  - bitmask
  - seq-hash
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-259
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/reflection/accessor.h
---

# 视角093：字段标志位系统

## 概述

`TVMFFIFieldFlagBitMask` 是 TVM FFI 反射系统中字段与方法的位标志枚举，定义在 `include/tvm/ffi/c_api.h:960-1057`。它以 `int32_t` 位掩码的形式存储在 `TVMFFIFieldInfo::flags` 与 `TVMFFIMethodInfo::flags` 中，以极低的空间开销表达字段的可访问性、默认值策略、结构化比较行为、Python 集成语义等多维属性。C++ 层通过 `AttachFieldFlag`、`repr`、`compare`、`hash`、`kw_only`、`init` 等 `InfoTrait` 以类型安全的方式设置这些标志。

## 标志位清单

| 位 | 常量 | 值 | 语义 |
|----|------|----|------|
| 0 | `kTVMFFIFieldFlagBitMaskWritable` | 1<<0 | 字段可写 |
| 1 | `kTVMFFIFieldFlagBitMaskHasDefault` | 1<<1 | 字段具有默认值或默认工厂 |
| 2 | `kTVMFFIFieldFlagBitMaskIsStaticMethod` | 1<<2 | 该条目为静态方法 |
| 3 | `kTVMFFIFieldFlagBitMaskSEqHashIgnore` | 1<<3 | 结构化相等/哈希时忽略此字段 |
| 4 | `kTVMFFIFieldFlagBitMaskSEqHashDefRecursive` | 1<<4 | 进入递归 def 区域 |
| 5 | `kTVMFFIFieldFlagBitMaskDefaultFromFactory` | 1<<5 | 默认值是 `() -> Any` 工厂函数 |
| 6 | `kTVMFFIFieldFlagBitMaskReprOff` | 1<<6 | 从 repr 输出中排除 |
| 7 | `kTVMFFIFieldFlagBitMaskCompareOff` | 1<<7 | 从递归比较中排除 |
| 8 | `kTVMFFIFieldFlagBitMaskHashOff` | 1<<8 | 从递归哈希中排除 |
| 9 | `kTVMFFIFieldFlagBitMaskInitOff` | 1<<9 | 从自动生成的 `__ffi_init__` 中排除 |
| 10 | `kTVMFFIFieldFlagBitMaskKwOnly` | 1<<10 | 在自动构造函数中仅限关键字参数 |
| 11 | `kTVMFFIFieldFlagBitMaskSetterIsFunctionObj` | 1<<11 | setter 是 FunctionObj 而非函数指针 |
| 12 | `kTVMFFIFieldFlagBitMaskSEqHashDefNonRecursive` | 1<<12 | 进入非递归 def 区域 |

## 可访问性与默认值

**Writable**（位 0）决定字段是否暴露写接口。`def_rw` 注册的字段置位，`def_ro` 不置位。即使只读字段也设置 setter 函数指针，因为序列化反序列化需要通过 setter 填充字段，只是 Python 属性的 setter 会拒绝外部写入。

**HasDefault**（位 1）与 **DefaultFromFactory**（位 5）共同控制默认值行为：
- 仅置 `HasDefault`：`default_value_or_factory` 直接持有静态默认值。
- 同时置 `DefaultFromFactory`：`default_value_or_factory` 持有一个 `Function`，`SetFieldToDefault`（`accessor.h:243`）调用它产生新值。后者对 `Array`、`Map` 等可变默认值至关重要，避免多个实例共享同一默认容器导致别名 bug。

C++ 层分别由 `DefaultValue`（`registry.h:154`）和 `DefaultFactory`（`registry.h:187`）两个 InfoTrait 设置，并提供小写别名 `default_value`、`default_factory` 以镜像 Python 的 `dataclasses.field` 命名。

## 结构化比较控制

三个标志控制字段在结构化相等/哈希中的参与方式：

- **SEqHashIgnore**（位 3）：字段完全不参与结构比较，适用于缓存、派生值等不影响语义相等性的字段。
- **SEqHashDefRecursive**（位 4）：字段进入递归 def 区域，字段值及其子字段中发现的自由变量均在同一绑定点引入，适用于函数式绑定（如函数参数列表及其形状参数）。
- **SEqHashDefNonRecursive**（位 12）：字段进入非递归 def 区域，仅字段值本身绑定为新变量，其子字段中的自由变量必须已由外层 def 区域绑定，适用于 let 风格绑定。

位 12 的注释说明它被安排在 1<<12 而非紧邻位 4，是因为位 1<<5 到 1<<11 已被其他标志占用（`c_api.h:1050-1052`）。

## Python 集成控制

- **ReprOff**（位 6）：由 `repr(false)` 设置，字段不出现在反射生成的 `__repr__` 中，适用于大字段或敏感字段。
- **CompareOff**（位 7）/ **HashOff**（位 8）：分别由 `compare(false)` 和 `hash(false)` 设置，控制字段是否参与 `RecursiveEq`/`RecursiveHash`。这三个标志相互独立，可单独控制 repr、比较、哈希。
- **InitOff**（位 9）：由 `init(false)` 设置，字段不作为自动 `__ffi_init__` 的参数。置位的字段必须有默认值或由 creator 初始化，否则反射创建会失败。
- **KwOnly**（位 10）：由 `kw_only(true)` 设置，字段在自动构造函数中只能通过关键字传入，不能作为位置参数。仅当 `InitOff` 未置位时有意义。
- **IsStaticMethod**（位 2）：标记方法为静态，Python 绑定据此不为方法注入 self 参数。

## Setter 分派模式

**SetterIsFunctionObj**（位 11）改变 setter 的解释方式。默认情况下 `TVMFFIFieldInfo::setter` 是 `TVMFFIFieldSetter` 函数指针；置位后它是指向 `FunctionObj` 的 `TVMFFIObjectHandle`。`CallFieldSetter`（`accessor.h:67-82`）据此分派：未置位时直接函数调用，置位时构造 `(field_addr, value)` 两个参数通过 `TVMFFIFunctionCall` 调用。这为 Python 定义的属性（setter 是 Python 回调）提供了统一路径。

## 设计分析

标志位系统是"用整数编码多维布尔属性"的经典工程实践。13 个标志共享一个 `int64_t`，相比为每个属性设置独立布尔字段节省了约 96 字节/字段的元数据空间，在类型拥有大量字段时收益显著。位运算的检查与设置都是单条指令，反射遍历字段时可批量判断。InfoTrait 层将原始位操作封装为具名、可组合的 C++ 类型，保留了类型安全与可读性。`SEqHashDefRecursive`/`NonRecursive` 等高级标志为编译器 IR 的 α 等价比较提供了精细化的绑定作用域控制，是通用反射框架中罕见但对编译器正确性至关重要的能力。

## 相关概念

- [086 FieldInfo 设计](086-field-info.md)：flags 字段的宿主结构
- [091 def_field/def_method](091-def-field-def-method.md)：通过 InfoTrait 设置标志
- [095 SEqHash 种类](095-seq-hash-kind.md)：Def 区域标志作用的比较框架
- [096 Def Region 语义](096-def-region.md)：DefRecursive/NonRecursive 的形式语义
