---
type: Concept
title: "视角020：静态与动态类型索引"
description: "对比静态类型索引（编译时固定，64-127）与动态类型索引（运行时分配，>=128）的注册机制、生命周期和使用场景，分析类型注册表、子类型槽位和类型提示在跨库扩展中的作用。"
tags:
  - core-types
  - type-index
  - static-types
  - dynamic-types
  - type-registration
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-001, F-002, F-003, F-114
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
---

# 视角020：静态与动态类型索引

## 概述

TVM FFI 的类型索引体系将对象类型划分为静态类型和动态类型两大类。静态类型索引在编译时硬编码于 `TVMFFITypeIndex` 枚举中（64-127），由核心库预定义；动态类型索引在运行时通过类型注册表分配（>=128），支持用户自定义对象和跨库扩展。这种二分法在保证核心类型 ABI 稳定性的同时，提供了开放的类型扩展能力。

## 静态类型索引

### 范围与特征

静态类型索引从 `kTVMFFIStaticObjectBegin = 64`（`c_api.h:190`）开始，当前使用到 `kTVMFFIVisitInterrupt = 77`（`c_api.h:182`），保留范围为 78-127。静态类型具有以下特征：

- **编译时确定**：索引值直接写入枚举常量，无需运行时注册。
- **ABI 稳定**：核心库版本升级不会改变已有静态类型的索引值。
- **C++ 类直接映射**：每个静态对象类型对应一个固定的 C++ 类（如 `kTVMFFIStr` 对应 `StringObj`）。
- **全局唯一**：由 TVM FFI 核心库统一管理，不存在冲突风险。

### 静态类型的 C++ 注册

在 C++ 层，静态对象类型通过 `TVM_FFI_DECLARE_OBJECT_INFO_STATIC` 宏注册（`object.h:933-946`）：

```cpp
#define TVM_FFI_DECLARE_OBJECT_INFO_STATIC(TypeName, TypeKey, TypeIndex, ...) \
  static constexpr uint32_t _type_index = TypeIndex;                          \
  static uint32_t RuntimeTypeIndex() { return TypeIndex; }                    \
  ...
```

该宏将 `_type_index` 设置为编译时常量，`RuntimeTypeIndex()` 直接返回该常量，无需调用 `_GetOrAllocRuntimeTypeIndex()`。这避免了静态初始化开销，且类型索引在编译期即可用于 `constexpr` 上下文。

预定义的静态类型通过 `TVM_FFI_REGISTER_OBJECT_INFO_STATIC_PREDEFINED` 宏在全局注册，类型键和索引在编译时绑定。

### 静态类型列表

完整的静态对象类型列表见视角019，包括 `Object`(64)、`String`(65)、`Bytes`(66)、`Error`(67)、`PackedFunc`(68)、`Shape`(69)、`Tensor`(70)、`Array`(71)、`Map`(72)、`Module`(73)、`OpaquePyObject`(74)、`List`(75)、`Dict`(76)、`VisitInterrupt`(77)。

这些类型覆盖了 FFI 运行时所需的全部核心数据结构，从容器到函数再到模块。

## 动态类型索引

### 范围与特征

动态类型索引从 `kTVMFFIDynObjectBegin = 128`（`c_api.h:193`）开始，无上限。动态类型具有以下特征：

- **运行时分配**：首次使用时通过 `TVMFFITypeGetOrAllocIndex` 分配索引。
- **类型键驱动**：以字符串类型键（如 `"myapp.MyObject"`）为唯一标识，索引值可能因进程而异。
- **支持继承**：通过 `type_child_slots` 预留子类型槽位，支持运行时继承关系。
- **跨库扩展**：动态库可以在加载时注册新类型，无需重新编译核心库。

### 动态注册流程

C++ 层动态类型的注册通过 `TVM_FFI_DECLARE_OBJECT_INFO_PREDEFINED_TYPE_KEY` 宏（`object.h:1080-1095`）生成的 `_GetOrAllocRuntimeTypeIndex()` 方法完成。核心逻辑如下：

1. **构建类型键字节数组**：将 `_type_key` 字符串包装为 `TVMFFIByteArray`（包含指针和长度）。
2. **递归获取父类型索引**：调用 `ParentType::_GetOrAllocRuntimeTypeIndex()` 确保父类型已注册。
3. **调用 C API**：调用 `TVMFFITypeGetOrAllocIndex`（`c_api.h:1487`），传入类型键、静态索引（动态类型传 -1）、类型深度、子类型槽位数、溢出标志和父类型索引。
4. **缓存结果**：将返回的类型索引存入静态成员 `_type_index`，后续访问直接使用缓存值。

关键代码片段（`object.h:1087-1092`）：

```cpp
TVMFFIByteArray type_key{TypeName::_type_key,
                         std::char_traits<char>::length(TypeName::_type_key)};
static int32_t tindex = TVMFFITypeGetOrAllocIndex(
    &type_key, -1, TypeName::_type_depth, TypeName::_type_child_slots,
    TypeName::_type_child_slots_can_overflow,
    ParentType::_GetOrAllocRuntimeTypeIndex());
return tindex;
```

### static_type_index 参数

`TVMFFITypeGetOrAllocIndex` 的 `static_type_index` 参数区分静态和动态注册：
- 传 -1：动态分配类型索引（>= 128）。
- 传非负值：使用指定的静态类型索引（64-127），由核心库预定义。

当多个动态库使用相同的类型键注册时，注册表返回相同的索引值，确保跨库类型一致性。

### 子类型槽位机制

动态类型系统支持通过槽位预留实现高效的继承检查。当一个非最终类型（`_type_final == false`）注册时，它请求 `_type_child_slots` 个连续的子类型槽位。子类型注册时优先使用父类型预留的槽位，这样父类型的 `IsInstance` 检查只需验证目标类型索引是否落在其槽位范围内，无需遍历祖先链。

如果子类型数量超过预留槽位（`_type_child_slots_can_overflow == true`），系统从全局池追加分配；若不允许溢出，则报错。

## 静态与动态的对比

| 维度 | 静态类型 | 动态类型 |
|---|---|---|
| 索引范围 | 64-127 | >=128 |
| 分配时机 | 编译时 | 运行时首次使用 |
| 标识方式 | 枚举常量 | 字符串键 + 运行时索引 |
| ABI 稳定性 | 稳定 | 索引值可能变化 |
| 继承支持 | 固定 C++ 继承 | 运行时槽位 + 祖先链 |
| 注册开销 | 零 | 一次哈希 + C API 调用 |
| 适用场景 | 核心内置类型 | 用户扩展、跨库类型 |
| `RuntimeTypeIndex()` | 返回常量 | 延迟初始化 + 缓存 |

## 类型注册表

类型注册表是一个全局的运行时数据结构，通过以下 C API 操作：

- `TVMFFITypeGetOrAllocIndex`（`c_api.h:1487`）：查找或分配类型索引，支持静态和动态注册。
- `TVMFFIGetTypeInfo`（`c_api.h:1498`）：根据索引获取 `TVMFFITypeInfo`。
- `TVMFFITypeKeyToIndex`（`c_api.h:705`）：类型键字节数组→索引查询。
- `TVMFFISetCustomAllocator`（`c_api.h:697`）：注册自定义对象分配器。

C++ 层通过 `TypeIndexToTypeKey`（`type_traits.h:115`）内联函数执行索引→键查询，内部调用 `TVMFFIGetTypeInfo` 获取类型键。

注册表在内部维护类型键到索引的哈希映射，以及索引到 `TVMFFITypeInfo` 的数组。动态类型的 `TVMFFITypeInfo` 在注册时填充，包含字段和方法的反射信息。

## 设计分析

静态/动态二分法体现了以下架构智慧：

1. **核心稳定与开放扩展**：核心类型使用静态索引保证 ABI 稳定和零开销；用户类型通过动态注册获得无限扩展能力，两者互不干扰。
2. **延迟初始化**：动态类型索引在首次使用时才分配，避免了静态初始化顺序灾难，也支持动态库按需加载。
3. **槽位继承优化**：子类型槽位机制将继承检查从 O(深度) 优化为 O(1) 范围检查，在频繁的 `IsInstance` 调用中性能显著。
4. **类型键作为唯一标识**：虽然动态索引值可能变化，但类型键字符串是跨进程、跨语言的稳定标识，序列化和跨语言通信使用类型键而非索引。
5. **保留区间**：78-127 的保留区为未来核心类型扩展预留空间，无需破坏动态类型的起始边界。

## 相关概念

- [019 TypeIndex 类型索引](019-type-index.md)：类型索引体系全貌
- [029 对象继承模型](029-object-inheritance.md)：type_ancestors 与槽位继承
- [027 TVMFFIObject 对象头](027-object-header.md)：对象头中的 type_index
- [032 不透明对象](032-opaque-object.md)：动态类型的特殊用法
