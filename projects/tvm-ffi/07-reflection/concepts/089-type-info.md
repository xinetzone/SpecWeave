---
type: Concept
title: "视角089：TypeInfo 运行时类型"
description: "解析 TVMFFITypeInfo 运行时类型信息结构：type_index、type_depth、type_key、type_ancestors、type_key_hash、fields/methods/metadata，以及类型表注册与查询 API。"
tags:
  - reflection
  - type-info
  - runtime-type
  - type-table
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-023, F-033, F-037, F-249, F-274, F-275
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
---

# 视角089：TypeInfo 运行时类型

## 概述

`TVMFFITypeInfo` 是 TVM FFI 运行时类型系统的核心记录，定义在 `include/tvm/ffi/c_api.h:1344`。每个已注册的对象类型在全局类型表中对应一条 `TVMFFITypeInfo`，集中存储类型索引、键名、继承链、字段、方法与元数据。它是 `IsInstance` 类型检查、反射字段访问、方法分派、结构化比较与跨语言类型发现的统一数据来源。

## 数据结构

`TVMFFITypeInfo`（`c_api.h:1344-1380`）包含以下字段：

- **`type_index`**（`int32_t`）：运行时类型索引。静态类型在编译期确定，动态类型通过 `TVMFFITypeGetOrAllocIndex` 在运行时分配。
- **`type_depth`**（`int32_t`）：类型在继承树中的深度，根 `Object` 深度为 0。
- **`type_key`**（`TVMFFIByteArray`）：唯一标识类型的字符串键，如 `"ffi.ArrayNode"`、`"ir.TypeNode"`。
- **`type_ancestors`**（`const TVMFFITypeInfo**`）：祖先类型信息指针数组，`type_ancestors[depth]` 为对应深度的祖先。源码注释明确说明系统不支持多重继承，继承层次保持为树（`c_api.h:1359-1360`）。
- **`type_key_hash`**（`uint64_t`）：类型键的缓存哈希值，用于结构化哈希的一致性。
- **`num_fields` / `num_methods`**（`int32_t`）：反射可访问字段与方法的数量。
- **`fields`**（`const TVMFFIFieldInfo*`）：字段信息数组。
- **`methods`**（`const TVMFFIMethodInfo*`）：方法信息数组。
- **`metadata`**（`const TVMFFITypeMetadata*`）：可选的类型级元数据。

## 类型表 API

C ABI 层提供以下接口管理类型表：

- **`TVMFFITypeGetOrAllocIndex`**（`c_api.h:1487`）：类型注册的核心入口。接受 `type_key`、`static_type_index`、`type_depth`、`num_child_slots`、`child_slots_can_overflow`、`parent_type_index`，返回已存在或新分配的类型索引。`parent_type_index` 为 -1 表示根类型，为 -2 表示仅查询模式（未注册返回 -2）。
- **`TVMFFIGetTypeInfo`**（`c_api.h:1498`）：按类型索引返回 `const TVMFFITypeInfo*`，标记为 `TVM_FFI_ATTRIBUTE_PURE`，表示无副作用可被公共子表达式优化。
- **`TVMFFITypeKeyToIndex`**（`c_api.h:705`）：按类型键查找索引。
- **`TVMFFITypeRegisterField` / `TVMFFITypeRegisterMethod` / `TVMFFITypeRegisterMetadata`**（`c_api.h:1408/1414/1420`）：分别向类型信息追加字段、方法与元数据。

C++ 层 `Object::GetTypeKey()`（`object.h:156`）与 `TypeIndex2Key()`（`object.h:176`）均通过 `TVMFFIGetTypeInfo` 获取类型键。

## 静态与动态类型索引

类型索引分为两段：内置类型占用静态索引（如 `kTVMFFITypeIndexObject = 16`），动态类型从 `kTVMFFITypeIndexDynamicBegin = 1000` 开始分配。C++ 子类通过 `TVM_FFI_DECLARE_OBJECT_INFO` 宏（`object.h:1059`）在首次使用时调用 `_GetOrAllocRuntimeTypeIndex()`，该方法将静态索引、子槽位数等信息传给 `TVMFFITypeGetOrAllocIndex`。`_type_child_slots` 允许为子类预留索引区间，使得 `IsInstance` 可通过范围比较快速判定；`_type_child_slots_can_overflow` 则在子类超出预留时回退到类型表查找。

## 继承与字段遍历

`ForEachFieldInfo`（`accessor.h:265`）按父类到子类的顺序遍历字段：从 `type_ancestors[1]`（跳过根 `Object`）开始遍历各父类字段，再遍历当前类型字段。这保证了反射创建时字段按继承顺序初始化，也使序列化结果在继承层次变化时保持稳定。`ForEachFieldInfoWithEarlyStop`（`accessor.h:293`）提供带提前终止的搜索变体。

## 设计分析

`TVMFFITypeInfo` 采用"一次分配、只读访问"的设计：类型注册在静态初始化或首次使用时完成字段、方法与元数据的填充，之后通过 `const` 指针在运行时高效读取，无需加锁。祖先数组以深度索引而非链表组织，使继承关系查询为 O(1)。类型键哈希的缓存避免了结构化哈希中重复计算字符串哈希。字段与方法数组的连续内存布局有利于缓存友好遍历，这在序列化、repr、结构比较等需要逐字段扫描的场景中尤为重要。整体设计在保持 C ABI 稳定性的同时，为 C++/Python/Rust 等多语言提供了一致的运行时类型视图。

## 相关概念

- [086 FieldInfo 设计](086-field-info.md)：TypeInfo 管理的字段数组元素
- [087 MethodInfo 设计](087-method-info.md)：TypeInfo 管理的方法数组元素
- [088 TypeMetadata](088-type-metadata.md)：TypeInfo 的可选元数据
- [090 ObjectDef 构建器](090-object-def-builder.md)：向 TypeInfo 注册字段的 C++ 接口
