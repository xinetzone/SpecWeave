---
type: Concept
title: "视角086：FieldInfo 设计"
description: "解析 TVM FFI 反射系统中字段元数据 TVMFFIFieldInfo 的结构设计：名称、文档、偏移、getter/setter、默认值、静态类型索引及标志位，以及 C++ 层 FieldInfoBuilder 的构建方式。"
tags:
  - reflection
  - field-info
  - metadata
  - accessor
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-035, F-036, F-254
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/reflection/accessor.h
---

# 视角086：FieldInfo 设计

## 概述

`TVMFFIFieldInfo` 是 TVM FFI 反射系统描述对象字段的核心元数据结构，定义在 `include/tvm/ffi/c_api.h:1179`。它以纯 C 结构体的形式存在，确保跨编译器、跨语言的 ABI 稳定性。每个通过反射注册的字段（无论是 C++ 类成员还是 Python `@c_class` 属性）都会在运行时类型表中对应一条 `TVMFFIFieldInfo` 记录，供序列化、结构化比较、Python 属性访问、自动构造等机制统一消费。

## 数据结构

`TVMFFIFieldInfo`（`c_api.h:1179-1244`）包含以下关键字段：

- **`name`**（`TVMFFIByteArray`）：字段名称，作为反射访问的键。
- **`doc`**（`TVMFFIByteArray`）：字段文档字符串，可用于生成帮助信息与存根。
- **`metadata`**（`TVMFFIByteArray`）：JSON 格式的结构化元数据，例如 `type_schema` 等编译期类型信息。
- **`flags`**（`int64_t`）：位标志集合，标记可写、有默认值、参与结构化相等/哈希等属性。
- **`size` / `alignment` / `offset`**（`int64_t`）：字段在对象内存布局中的字节大小、对齐与相对对象基址的偏移。
- **`getter`**（`TVMFFIFieldGetter`）：读取字段值的函数指针，签名为 `int (*)(void* field, TVMFFIAny* result)`（`c_api.h:939`）。
- **`setter`**（`void*`）：写入字段值的入口。默认情况下是 `TVMFFIFieldSetter` 函数指针（`c_api.h:947`）；当 `kTVMFFIFieldFlagBitSetterIsFunctionObj` 置位时，它是一个指向 `FunctionObj` 的对象句柄，通过 `TVMFFIFunctionCall` 调用。
- **`default_value_or_factory`**（`TVMFFIAny`）：默认值或默认工厂函数。
- **`field_static_type_index`**（`int32_t`）：编译期静态类型索引，是一种提示而非运行时真值判定依据。

## 标志位语义

标志位由枚举 `TVMFFIFieldFlagBitMask`（`c_api.h:960-1057`）定义，关键位包括：

- `kTVMFFIFieldFlagBitMaskWritable`（1<<0）：字段可写。
- `kTVMFFIFieldFlagBitMaskHasDefault`（1<<1）：字段具有默认值。
- `kTVMFFIFieldFlagBitMaskIsStaticMethod`（1<<2）：该条目实际为静态方法。
- `kTVMFFIFieldFlagBitMaskSEqHashIgnore`（1<<3）：结构化相等/哈希时忽略。
- `kTVMFFIFieldFlagBitMaskDefaultFromFactory`（1<<5）：默认值是一个 `() -> Any` 工厂函数。
- `kTVMFFIFieldFlagBitMaskReprOff`（1<<6）：从 repr 输出中排除。
- `kTVMFFIFieldFlagBitMaskCompareOff` / `kTVMFFIFieldFlagBitMaskHashOff`（1<<7/8）：从递归比较/哈希中排除。
- `kTVMFFIFieldFlagBitMaskInitOff`（1<<9）：从自动生成的 `__ffi_init__` 中排除。
- `kTVMFFIFieldFlagBitMaskKwOnly`（1<<10）：在自动构造函数中为仅限关键字参数。
- `kTVMFFIFieldFlagBitMaskSEqHashDefRecursive` / `...DefNonRecursive`（1<<4/12）：进入 def 区域的方式。

## C++ 构建流程

C++ 层通过 `FieldInfoBuilder`（`registry.h:69`）构建字段信息，它继承自 `TVMFFIFieldInfo` 并额外持有临时的 `_MetadataType`（`std::vector<std::pair<String, Any>>`）。`ObjectDef<T>::RegisterField`（`registry.h:993-1021`）执行以下步骤：

1. 通过 `GetFieldByteOffsetToObject`（`registry.h:387`）计算字段相对 `Object` 基址的字节偏移。
2. 设置 `size`、`alignment`、`flags`（可写字段置 `Writable`）。
3. 绑定泛型 `FieldGetter<T>` / `FieldSetter<T>`（`registry.h:399-414`）。getter 将字段值移动为 `Any`；setter 从 `TVMFFIAny` 读取并 `cast<T>()` 后写入。
4. 初始化默认值为 null，并将 `type_schema` 写入临时 metadata。
5. 应用 `InfoTrait` 参数（如 `DefaultValue`、`AttachFieldFlag`、`repr(false)` 等）。
6. 将 metadata 序列化为 JSON，调用 `TVMFFITypeRegisterField`（`c_api.h:1408`）注册到运行时类型表。

## 访问器

C++ 层提供 `FieldGetter` 与 `FieldSetter` 两个辅助类（`accessor.h:87-162`），封装按偏移调用函数指针的细节。`CallFieldSetter`（`accessor.h:67`）会根据 `SetterIsFunctionObj` 标志在直接函数调用与 `TVMFFIFunctionCall` 之间分派。`SetFieldToDefault`（`accessor.h:243`）则根据 `DefaultFromFactory` 标志决定是直接使用默认值还是调用工厂函数产生新值。

`field_static_type_index` 虽可用于序列化器对 POD 字段内联编码，但源码注释明确警告：它仅反映编译期声明类型，不能用于运行时真值判定；`Any` 字段即使持有 `int` 仍会报告 `kTVMFFIAny`。

## 设计分析

`TVMFFIFieldInfo` 的设计体现了"稳定 C ABI + 可扩展元数据"的平衡。固定布局的函数字段保证任意语言均可通过偏移直接访问，而 `metadata` JSON 字段允许在不破坏 ABI 的前提下演进附加信息。getter/setter 的双模式（函数指针 vs `FunctionObj`）既为 C++ 原生字段保留零开销路径，也为 Python 定义的属性提供动态分派能力。偏移与大小信息使得反射创建（`ObjectCreator`）能够在不了解 C++ 类型的情况下逐字段填充对象，是跨语言对象构造的基础。

## 相关概念

- [087 MethodInfo 设计](087-method-info.md)：方法元数据与字段共用注册框架
- [090 ObjectDef 构建器](090-object-def-builder.md)：字段注册的 C++ DSL
- [093 字段标志位系统](093-field-flags.md)：标志位的完整语义
- [099 Creator 创建函数](099-creator.md)：基于字段偏移的反射构造
