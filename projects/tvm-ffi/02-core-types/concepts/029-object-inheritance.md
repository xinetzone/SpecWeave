---
type: Concept
title: "视角029：对象继承模型"
description: "解析 TVM FFI 对象继承体系，包括 Object 基类、_type_key/_type_depth/_type_child_slots 静态配置、type_ancestors 祖先链、子类型槽位范围检查，以及 IsObjectInstance 的三级快速分派机制。"
tags:
  - core-types
  - object
  - inheritance
  - rtti
  - type-system
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045
  - code:
    - include/tvm/ffi/object.h
    - include/tvm/ffi/c_api.h
---

# 视角029：对象继承模型

## 概述

TVM FFI 的对象继承模型是一种不依赖 C++ RTTI 的轻量运行时类型系统。所有堆对象继承自 `Object` 基类，通过静态配置成员（`_type_key`、`_type_depth`、`_type_child_slots`）和运行时类型信息（`type_ancestors` 数组）支持 `IsInstance` 类型检查。该模型结合了编译时常量折叠、槽位范围快速检查和运行时祖先链查询，在保证类型安全的同时实现了高效的向下转型。

## Object 基类

所有 FFI 对象的 C++ 基类是 `Object`（`object.h:127`），它嵌入 `TVMFFIObject header_` 作为受保护成员。`Object` 提供了类型系统的基础设施：

- `IsInstance<TargetType>()`（`object.h:144-147`）：检查对象是否为目标类型或其子类。
- `type_index()`（`object.h:150`）：返回运行时类型索引。
- `GetTypeKey()`（`object.h:156-160`）：返回类型键字符串。
- `GetTypeKeyHash()`（`object.h:165-169`）：返回类型键哈希。

### 根类型配置

`Object` 作为继承树根，配置如下（`object.h:207-221`）：

```cpp
static constexpr const char* _type_key = StaticTypeKey::kTVMFFIObject;
static constexpr const bool _type_final = false;
static constexpr const bool _type_mutable = false;
static constexpr uint32_t _type_child_slots = 0;
static constexpr int32_t _type_index = TypeIndex::kTVMFFIObject;  // 64
static constexpr int32_t _type_depth = 0;
```

根类型深度为 0，无子类型槽位（动态注册的子类型通过溢出机制分配）。

## 静态类型配置成员

每个 `Object` 子类通过宏声明以下静态配置：

### _type_key

类型的唯一字符串标识，如 `"ffi.String"`、`ffi.Array"`。类型键用于：
- 运行时类型注册和查找。
- 跨语言类型标识（Python、Rust 等通过字符串键识别类型）。
- 错误报告和调试。

### _type_final

布尔值，标记类是否为叶子类（不可继承）。`final` 类型的 `IsInstance` 检查只需一次整数比较（`object_type_index == target_type_index`），无需查询祖先链。

### _type_depth

类型在继承树中的深度。根 `Object` 深度为 0，每继承一层加 1。深度用于：
- 快速排除不可能匹配的类型（深度不足者不可能是子类）。
- 在 `type_ancestors` 数组中索引祖先类型。

### _type_child_slots

为直接和间接子类型预分配的连续类型索引槽位数。如果子类型的类型索引落在 `[parent_index, parent_index + child_slots + 1)` 范围内，可以通过一次范围比较确认继承关系，无需查询运行时类型信息。

### _type_child_slots_can_overflow

布尔值，控制子类型数量超过预分配槽位时是否允许溢出。如果为 `true`，超出的子类型通过全局类型注册表动态分配，`IsInstance` 回退到 `type_ancestors` 查询。如果为 `false`，溢出时报错。

## 类型注册宏

### TVM_FFI_DECLARE_OBJECT_INFO

`TVM_FFI_DECLARE_OBJECT_INFO(TypeName, ParentType)` 宏（`object.h:1052-1075`）为非最终类型生成静态成员：

```cpp
static constexpr int32_t _type_depth = ParentType::_type_depth + 1;
static int32_t _GetOrAllocRuntimeTypeIndex() {
  // 构建祖先链
  // 调用 TVMFFITypeGetOrAllocIndex
  // 缓存结果到 _type_index
}
static inline const int32_t _type_index = _GetOrAllocRuntimeTypeIndex();
```

子类的 `_type_depth` 比父类大 1，在编译期确定。

### TVM_FFI_DECLARE_OBJECT_INFO_FINAL

`TVM_FFI_DECLARE_OBJECT_INFO_FINAL(TypeName, ParentType)` 宏（`object.h:1078-1095`）为最终类型生成配置，设置 `_type_final = true`。

### TVM_FFI_DECLARE_OBJECT_INFO_STATIC

静态类型（如 `StringObj`、`ArrayObj`）使用 `TVM_FFI_DECLARE_OBJECT_INFO_STATIC` 宏，直接将 `_type_index` 设为编译时常量（如 `TypeIndex::kTVMFFIStr`），无需运行时注册。

## IsObjectInstance 实现

`details::IsObjectInstance<TargetType>`（`object.h:1172-1208`）是类型检查的核心，采用三级分派：

### 第一级：编译期常量折叠

```cpp
if constexpr (std::is_same_v<TargetType, Object>) {
  return true;  // 一切都是 Object
}
```

如果目标类型是 `Object` 本身，编译期直接返回 `true`，无运行时开销。

### 第二级：final 类型快速路径

```cpp
else if constexpr (TargetType::_type_final) {
  return object_type_index == TargetType::RuntimeTypeIndex();
}
```

如果目标类型标记为 `final`，只需一次整数比较。这是最快的路径，适用于叶子类型。

### 第三级：槽位范围 + 祖先链查询

对于非 final 类型：

```cpp
int32_t target_type_index = TargetType::RuntimeTypeIndex();
int32_t begin = target_type_index;

if constexpr (TargetType::_type_child_slots != 0) {
  int32_t end = begin + TargetType::_type_child_slots + 1;
  if (object_type_index >= begin && object_type_index < end) return true;
} else {
  if (object_type_index == begin) return true;
}

if constexpr (TargetType::_type_child_slots_can_overflow) {
  if (object_type_index < target_type_index) return false;
  const TypeInfo* type_info = TVMFFIGetTypeInfo(object_type_index);
  return (type_info->type_depth > TargetType::_type_depth &&
          type_info->type_ancestors[TargetType::_type_depth]->type_index
              == target_type_index);
}
```

**槽位范围检查**：如果子类型索引落在预分配槽位范围内，O(1) 返回 true。

**祖先链查询**：对于溢出的子类型，查询运行时 `TypeInfo`：
1. 父类型索引始终小于子类型索引（注册顺序保证），因此 `object_type_index < target_type_index` 时直接返回 false。
2. 获取对象的类型信息，检查 `type_depth` 是否大于目标类型深度。
3. 在 `type_ancestors` 数组的 `TargetType::_type_depth` 位置检查是否为目标类型。

`type_ancestors` 是一个按深度索引的数组，`type_ancestors[d]` 返回深度 `d` 处的祖先类型信息。这种设计使得祖先查询为 O(1)，无需遍历链表。

## RuntimeTypeIndexMatch 非模板版本

`RuntimeTypeIndexMatch`（`object.h:1217-1251`）是 `IsObjectInstance` 的非模板版本，接受两个类型索引参数。它增加了对特殊类型的处理：

- `kTVMFFIAny`(-1) 匹配所有类型。
- `kTVMFFIStr`(65) 同时匹配 `kTVMFFISmallStr`(11)。
- `kTVMFFIBytes`(66) 同时匹配 `kTVMFFISmallBytes`(12)。
- `kTVMFFIObject`(64) 匹配所有 `type_index >= 64` 的堆对象。

此函数用于运行时类型检查，当目标类型在编译期未知时使用。

## 类型信息结构

`TVMFFITypeInfo`（`c_api.h:1344-1380`）存储完整的运行时类型信息：

```c
typedef struct TVMFFITypeInfo {
  int32_t type_index;
  int32_t type_depth;
  const char* type_key;
  const int32_t* type_ancestors;  // 祖先类型索引数组
  uint64_t type_key_hash;
  uint32_t num_fields;
  uint32_t num_methods;
  TVMFFIFieldInfo* fields;
  TVMFFIFuncInfo* methods;
  TVMFFIValue metadata;
} TVMFFITypeInfo;
```

C++ 层通过 `TVMFFIGetTypeInfo(type_index)` 获取此结构的指针（`c_api.h:1498`）。

## _GetOrAllocRuntimeTypeIndex

动态类型在首次使用时通过 `_GetOrAllocRuntimeTypeIndex()`（`object.h:234`）注册。该函数：

1. 收集从当前类型到根的所有祖先类型索引。
2. 调用 `TVMFFITypeGetOrAllocIndex`（`c_api.h:1487`）注册类型键和祖先链。
3. 类型注册表分配类型索引，优先使用父类型的子类型槽位。
4. 缓存结果到静态成员 `_type_index`。

`TVM_FFI_COLD_CODE` 标记此函数为冷代码，提示编译器将其移出热路径。

## 设计分析

对象继承模型的设计体现了以下技术选择：

1. **无 RTTI 依赖**：不使用 C++ 的 `typeid` 和 `dynamic_cast`，避免 RTTI 带来的二进制膨胀和跨模块比较问题。类型信息由 FFI 自行管理。
2. **编译期优化**：`if constexpr` 和 `static constexpr` 使编译器在编译期消除不可能的分支，final 类型的检查退化为单次整数比较。
3. **槽位预分配**：通过 `_type_child_slots` 预分配连续索引范围，常见继承关系通过 O(1) 范围比较确认，避免运行时查找。
4. **深度索引祖先**：`type_ancestors[depth]` 数组将祖先查询从 O(深度) 优化为 O(1) 数组访问。
5. **类型索引单调性**：父类型索引始终小于子类型索引，允许通过一次比较快速排除不匹配情况。
6. **开放继承**：`_type_child_slots_can_overflow` 允许类型层次在运行时扩展，动态库可以添加新的子类型而无需重新编译父类型。

## 相关概念

- [019 TypeIndex 类型索引](019-type-index.md)：类型索引体系
- [020 静态与动态类型索引](020-static-dynamic-type-index.md)：类型注册机制
- [027 TVMFFIObject 对象头](027-object-header.md)：type_index 字段
- [030 ObjectRef 包装器](030-object-ref-wrapper.md)：IsInstance 在类型转换中的应用
