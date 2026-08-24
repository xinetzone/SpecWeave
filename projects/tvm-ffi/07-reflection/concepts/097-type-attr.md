---
type: Concept
title: "视角097：TypeAttr 类型属性"
description: "解析 TVMFFITypeAttrColumn 稀疏列结构与 TypeAttr 机制：开放类型属性集合、kNew/kInit/kConvert/kShallowCopy/kSEqual/kSHash 等标准属性、TypeAttrDef 构建器与 EnsureTypeAttrColumn。"
tags:
  - reflection
  - type-attr
  - sparse-column
  - hooks
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-034, F-250, F-251, F-252, F-253
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/accessor.h
    - include/tvm/ffi/reflection/registry.h
---

# 视角097：TypeAttr 类型属性

## 概述

TypeAttr（类型属性）是 TVM FFI 反射系统提供的一种开放扩展机制，允许在运行时为类型索引挂载额外的、按列存储的属性值。其 C ABI 结构为 `TVMFFITypeAttrColumn`（`include/tvm/ffi/c_api.h:1322`），C++ 层通过 `TypeAttrColumn`（`accessor.h:167`）与 `TypeAttrDef<T>`（`registry.h:1063`）提供查询与注册接口。与固定字段的 `TVMFFITypeInfo` 不同，TypeAttr 支持任意数量的命名属性列，框架与下游用户均可定义新属性，无需修改核心 ABI。

## 数据结构：稀疏列

`TVMFFITypeAttrColumn`（`c_api.h:1322-1338`）包含三个字段：

- **`data`**（`const TVMFFIAny*`）：属性值数组，按 `type_index - begin_index` 索引。
- **`size`**（`int32_t`）：数组元素数量，覆盖类型索引区间 `[begin_index, begin_index + size)`。
- **`begin_index`**（`int32_t`）：列数据的起始类型索引。

源码注释（`c_api.h:1301-1320`）将 TypeAttr 概念化为"C++/Rust 中 TypeTraits 的动态变体"。它像 C++ type_traits 一样行为，但以运行时稀疏列实现：`column[T]` 不包含基类的属性值，每列只存储该类型自身注册的值。这一设计使得属性查询为 O(1) 数组访问，同时未注册属性的类型不占用空间。

## C API

- **`TVMFFITypeRegisterAttr`**（`c_api.h:1426`）：为指定类型索引注册命名属性值，接受 `type_index`、`attr_name`（字节数组）、`attr_value`（`TVMFFIAny*`）。
- **`TVMFFIGetTypeAttrColumn`**（`c_api.h:1434`）：按属性名返回 `const TVMFFITypeAttrColumn*`，未注册时返回 NULL。

`type_index = kTVMFFINone`（0）时用于注册列本身（声明该属性名存在），`EnsureTypeAttrColumn`（`registry.h:1159`）封装了这一引导逻辑。

## C++ 接口

**查询**：`TypeAttrColumn`（`accessor.h:167-196`）构造时按名查找列，`operator[](type_index)` 返回对应位置的 `AnyView`，越界返回空 `AnyView`。

**注册**：`TypeAttrDef<T>`（`registry.h:1063-1152`）是类型属性的流式构建器，提供：

- `def(name, value)`：值可直接转为 `AnyView` 时原样存储；否则作为可调用对象包装为 `Function`。通过 SFINAE 在两个重载间分派（`registry.h:1088-1115`）。
- `def_convert<TSelf>()`：注册标准 `__ffi_convert__` 转换钩子。
- `attr(name, value)`：注册常量值属性。

`ObjectDef<T>::def_type_attr`（`registry.h:879/897`）提供相同能力，可在字段/方法注册链中混合使用。

## 标准属性名

`type_attr` 命名空间（`accessor.h:319-567`）定义了框架使用的标准属性常量：

| 属性名 | 常量 | 用途 |
|--------|------|------|
| `"__ffi_new__"` | `kNew` | 零参数分配器 |
| `"__ffi_init__"` | `kInit` | 打包构造函数 |
| `"__ffi_convert__"` | `kConvert` | AnyView 到 TSelf 转换 |
| `"__ffi_convert_type_schema__"` | `kConvertTypeSchema` | 转换接受的类型 schema |
| `"__ffi_shallow_copy__"` | `kShallowCopy` | 浅拷贝工厂 |
| `"__ffi_repr__"` | `kRepr` | 自定义递归 repr |
| `"__ffi_hash__"` | `kHash` | 自定义递归哈希 |
| `"__ffi_eq__"` | `kEq` | 自定义递归相等 |
| `"__ffi_compare__"` | `kCompare` | 自定义三路比较 |
| `"__any_hash__"` | `kAnyHash` | Any 级哈希（容器键） |
| `"__any_equal__"` | `kAnyEqual` | Any 级相等（容器键） |
| `"__s_hash__"` | `kSHash` | 结构哈希钩子 |
| `"__s_equal__"` | `kSEqual` | 结构相等钩子 |
| `"__s_visit__"` | `kStructuralVisit` | 结构遍历钩子 |
| `"__s_mutate__"` | `kStructuralMutate` | 结构变更钩子 |
| `"__s_maybe_inplace_mutate__"` | `kStructuralMaybeInplaceMutate` | 可选就地变更钩子 |
| `"__data_to_json__"` | `kDataToJson` | 自定义 JSON 序列化 |
| `"__data_from_json__"` | `kDataFromJson` | 自定义 JSON 反序列化 |
| `"__ffi_enum__"` | `kEnumState` | 枚举状态 |

每个属性的签名与语义在 `accessor.h` 中有详细文档注释。

## 设计分析

TypeAttr 的稀疏列设计在三个维度上取得平衡：开放性（任意方可定义新属性）、查询效率（O(1) 数组索引）、空间效率（未注册类型零开销）。相比在 `TVMFFITypeInfo` 中为每种可能的钩子预留函数指针，稀疏列避免了核心结构随特性增长而膨胀，保持了 C ABI 的前向兼容性——新版本增加的属性列不影响旧版本解析。属性值统一为 `TVMFFIAny`，既可存储函数钩子也可存储标量元数据，使该机制同时服务于行为定制（eq/hash/repr）与数据标注（编译器 Pass 元数据）。`column[T]` 不继承基类属性的语义与 C++ type_traits 一致，避免了属性意外继承导致的行为偏差；需要继承的逻辑由查询方沿 `type_ancestors` 链自行实现。这一机制是反射系统从"固定字段描述"迈向"可扩展特性系统"的关键。

## 相关概念

- [089 TypeInfo 运行时类型](089-type-info.md)：TypeAttr 与 TypeInfo 互补
- [092 c_class Python 集成](092-c-class-python-integration.md)：消费 kNew/kInit/kConvert
- [094 结构化相等与哈希](094-structural-equal-hash.md)：消费 kSEqual/kSHash
- [098 自定义哈希/相等注册](098-custom-hash-eq.md)：TypeAttr 的典型应用
