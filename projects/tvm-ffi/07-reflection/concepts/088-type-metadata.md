---
type: Concept
title: "视角088：TypeMetadata"
description: "解析 TVMFFITypeMetadata 结构体：doc、creator 工厂、total_size 与 structural_eq_hash_kind 四要素，以及其在反射创建与结构化相等/哈希中的枢纽作用。"
tags:
  - reflection
  - type-metadata
  - creator
  - seq-hash
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-037, F-249, F-254
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/reflection/creator.h
---

# 视角088：TypeMetadata

## 概述

`TVMFFITypeMetadata` 是 TVM FFI 反射系统中描述类型级可选元数据的 C 结构体，定义在 `include/tvm/ffi/c_api.h:1274`。与 `TVMFFIFieldInfo`/`TVMFFIMethodInfo` 描述成员不同，`TVMFFITypeMetadata` 挂载于 `TVMFFITypeInfo::metadata` 指针，承载类型整体的创建能力、内存尺寸与结构化比较/哈希语义。它是反射创建（reflection-based creation）与结构化相等/哈希的关键枢纽。

## 数据结构

`TVMFFITypeMetadata`（`c_api.h:1274-1299`）包含四个字段：

- **`doc`**（`TVMFFIByteArray`）：类型级文档字符串。
- **`creator`**（`TVMFFIObjectCreator`）：可选的零参数工厂函数，签名为 `int (*)(TVMFFIObjectHandle* result)`（`c_api.h:954`），用于分配一个零初始化的空实例。
- **`total_size`**（`int32_t`）：对象结构体的总字节数；未注册时为 0。
- **`structural_eq_hash_kind`**（`TVMFFISEqHashKind`）：结构化相等/哈希种类，决定对象在结构比较中作为树节点、DAG 节点、自由变量还是单例处理。

源码注释强调，`creator` 产生的对象需要调用者随后通过 setter 逐字段初始化才能进入有效状态（`c_api.h:1283-1286`）。换言之，`creator` 只负责"分配壳"，字段填充由反射层完成。

## 注册流程

C++ 层在 `ObjectDef<T>::RegisterExtraInfo`（`registry.h:976-991`）中构造并注册 metadata：

1. 设置 `total_size = sizeof(Class)`。
2. 设置 `structural_eq_hash_kind = Class::_type_s_eq_hash_kind`，默认基类 `Object` 为 `kTVMFFISEqHashKindUnsupported`（`object.h:223`）。
3. 根据类型的可构造性选择 creator：
   - 若 `std::is_default_constructible_v<Class>`，使用 `ObjectCreatorDefault<Class>`，内部调用 `make_object<Class>()`（`registry.h:417-422`）。
   - 否则若可通过 `UnsafeInit` 构造，使用 `ObjectCreatorUnsafeInit<Class>`（`registry.h:425-430`）。
   - 两者皆不可时 `creator = nullptr`，表示该类型不支持反射创建。
4. 调用 `TVMFFITypeRegisterMetadata`（`c_api.h:1420`）写入运行时类型表。

## 在反射创建中的作用

`CreateEmptyObject`（`creator.h:43-67`）优先使用 `metadata->creator` 生成本地空对象；若为 NULL，则回退到 `__ffi_new__` 类型属性（Python `@py_class` 类型使用）。`HasCreator`（`creator.h:77-91`）据此判断类型是否可反射创建。`ObjectCreator::operator()`（`creator.h:146-187`）在创建空对象后，遍历字段信息调用 setter 填充字段值或默认值，完成完整对象构造。

## 结构化相等/哈希语义

`structural_eq_hash_kind` 字段为结构比较器提供类型级提示。`TVMFFISEqHashKind` 枚举（`c_api.h:1084-1123`）定义了六种取值：

- `kTVMFFISEqHashKindUnsupported`（0）：不支持结构比较。
- `kTVMFFISEqHashKindTreeNode`（1）：作为树节点，按值递归比较。
- `kTVMFFISEqHashKindFreeVar`（2）：作为可映射的自由变量。
- `kTVMFFISEqHashKindDAGNode`（3）：作为 DAG 节点，识别共享结构。
- `kTVMFFISEqHashKindConstTreeNode`（4）：常量树节点，不含自由变量，可用指针相等。
- `kTVMFFISEqHashKindUniqueInstance`（5）：单例值，可直接指针相等。

这使得 IR 中的变量节点、常量节点与复合表达式节点能够采用不同的比较策略，在保证语义正确的同时利用指针相等快速路径。

## 设计分析

`TVMFFITypeMetadata` 是"可选能力"设计的典范：所有字段均可为空或取默认值，类型无需实现全部反射特性即可被注册。creator 与字段 setter 的分离将"内存分配"与"语义初始化"解耦，使得同一分配机制可服务于反序列化、Python 构造、拷贝等多种场景。`structural_eq_hash_kind` 以枚举而非虚函数表达比较策略，避免了在对象头中增加虚表指针，保持 C ABI 的 POD 特性。metadata 整体通过独立的 `TVMFFITypeRegisterMetadata` 注册，与字段/方法注册正交，支持分阶段填充类型信息。

## 相关概念

- [089 TypeInfo 运行时类型](089-type-info.md)：metadata 的宿主结构
- [095 SEqHash 种类](095-seq-hash-kind.md)：六种结构比较种类的语义
- [099 Creator 创建函数](099-creator.md)：creator 字段的消费方
- [090 ObjectDef 构建器](090-object-def-builder.md)：metadata 的注册入口
