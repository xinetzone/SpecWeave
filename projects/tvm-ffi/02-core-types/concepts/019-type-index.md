---
type: Concept
title: "视角019：TypeIndex 类型索引"
description: "解析 TVMFFITypeIndex 枚举体系，包括基础 POD 类型索引（0-12）、静态对象类型索引（64-77）、动态对象起始边界（128），以及 TypeIndexToTypeKey/TypeKeyToTypeIndex 查询函数和类型信息注册机制。"
tags:
  - core-types
  - type-index
  - type-system
  - rtti
  - c-abi
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
---

# 视角019：TypeIndex 类型索引

## 概述

`TVMFFITypeIndex` 是 TVM FFI 类型系统的运行时标识，定义为 C 枚举（`include/tvm/ffi/c_api.h:94-200`）。每个 `TVMFFIAny` 值通过其 `type_index` 字段携带类型信息，所有类型分派、转换和检查都依赖这一整数标识。类型索引体系分为三个区段：基础 POD 类型、静态对象类型和动态对象类型，各区段之间留有保留间隙以支持未来扩展。

## 枚举定义

`TVMFFITypeIndex` 的完整定义位于 `c_api.h:94-200`，核心值如下：

### 基础类型（0-12）

| 枚举值 | 数值 | 含义 | 数据联合体字段 |
|---|---|---|---|
| `kTVMFFINone` | 0 | 空值/None | `v_int64 = 0` |
| `kTVMFFIInt` | 1 | 64位整数 | `v_int64` |
| `kTVMFFIBool` | 2 | 布尔值 | `v_int64` (0/1) |
| `kTVMFFIFloat` | 3 | 64位浮点 | `v_float64` |
| `kTVMFFIOpaquePtr` | 4 | 无类型指针 | `v_ptr` |
| `kTVMFFIDataType` | 5 | DLPack 数据类型 | `v_dtype` |
| `kTVMFFIDevice` | 6 | DLPack 设备 | `v_device` |
| `kTVMFFIDLTensorPtr` | 7 | DLTensor 指针 | `v_ptr` |
| `kTVMFFIRawStr` | 8 | 非拥有 C 字符串 | `v_c_str` |
| `kTVMFFIByteArrayPtr` | 9 | 非拥有字节数组指针 | `v_ptr` |
| `kTVMFFIObjectRValueRef` | 10 | 对象右值引用 | `v_ptr` |
| `kTVMFFISmallStr` | 11 | 内联小字符串 | `v_bytes[8]` |
| `kTVMFFISmallBytes` | 12 | 内联小字节数组 | `v_bytes[8]` |

此外还有 `kTVMFFIAny = -1`，用于通配类型匹配（如 `PackedFunc` 参数可接受任意类型）。

### 静态对象类型（64-77）

从 `kTVMFFIStaticObjectBegin = 64` 开始，这些类型对应堆分配的引用计数对象：

| 枚举值 | 数值 | C++ 类 |
|---|---|---|
| `kTVMFFIObject` | 64 | `Object` |
| `kTVMFFIStr` | 65 | `String`/`StringObj` |
| `kTVMFFIBytes` | 66 | `Bytes`/`BytesObj` |
| `kTVMFFIError` | 67 | 错误对象 |
| `kTVMFFIFunction` | 68 | `PackedFunc`/`FunctionObj` |
| `kTVMFFIShape` | 69 | 形状对象 |
| `kTVMFFITensor` | 70 | 张量对象 |
| `kTVMFFIArray` | 71 | `Array<T>` |
| `kTVMFFIMap` | 72 | `Map<K,V>` |
| `kTVMFFIModule` | 73 | `Module` |
| `kTVMFFIOpaquePyObject` | 74 | Python 不透明对象 |
| `kTVMFFIList` | 75 | Python 列表 |
| `kTVMFFIDict` | 76 | Python 字典 |
| `kTVMFFIVisitInterrupt` | 77 | 访问中断信号 |

静态对象类型在编译时固定，由 TVM FFI 核心库定义。

### 动态对象类型（>= 128）

`kTVMFFIDynObjectBegin = 128`（`c_api.h:193`）是用户自定义对象类型的起始索引。运行时通过 `TVMFFITypeGetOrAllocIndex`（`c_api.h:1487`）动态分配类型索引：

```c
TVM_FFI_DLL int32_t TVMFFITypeGetOrAllocIndex(
    const TVMFFIByteArray* type_key,
    int32_t static_type_index,
    int32_t type_depth,
    int32_t num_child_slots,
    int32_t child_slots_can_overflow,
    int32_t parent_type_index);
```

该函数在类型注册表中查找给定 `type_key`，若已存在则返回已有索引；否则分配新索引。参数含义如下：
- `static_type_index`：静态类型索引传具体值（如 `kTVMFFIStr`），动态类型传 -1。
- `type_depth`：继承链深度（根 Object 为 0）。
- `num_child_slots`：为子类型预留的连续槽位数。
- `child_slots_can_overflow`：子类型超出槽位时是否允许溢出分配。
- `parent_type_index`：父类型的运行时索引，根类型传 -1，查询模式传 -2。

## 区段边界的语义意义

三个区段的划分不仅是编号约定，更驱动着核心运行时逻辑：

### 堆对象判断阈值

`kTVMFFIStaticObjectBegin`（64）是判断值是否为堆对象的分界线。`Any::reset()`（`any.h:244`）和拷贝构造函数（`any.h:274`）均使用此阈值：

```cpp
if (data_.type_index >= TypeIndex::kTVMFFIStaticObjectBegin) {
  details::ObjectUnsafe::IncRefObjectHandle(data_.v_obj);
}
```

这意味着所有类型索引 >= 64 的值都通过 `v_obj` 字段持有 `TVMFFIObject*` 指针，需要引用计数管理。13-63 之间的保留区间确保未来添加基础 POD 类型时不会误触发引用计数逻辑。

### 动态类型注册边界

`kTVMFFIDynObjectBegin`（128）区分静态内置对象和动态注册对象。64-127 的空间预留给静态对象类型（当前使用 64-77），128 以上由运行时动态分配。这一设计允许核心库在未来版本中添加新的静态对象类型（78-127），而不会与用户自定义类型冲突。

## 类型键与索引的双向映射

### TypeKeyToIndex

`TVMFFITypeKeyToIndex`（`c_api.h:705`）将类型键字节数组转换为类型索引：

```c
TVM_FFI_DLL int TVMFFITypeKeyToIndex(const TVMFFIByteArray* type_key,
                                      int32_t* out_tindex);
```

该函数在类型注册表中查找键名，返回 0 表示成功，非零表示未找到。成功时通过 `out_tindex` 输出类型索引。

### TypeIndexToTypeKey（C++ 内联函数）

C++ 层通过 `TypeIndexToTypeKey`（`type_traits.h:115-118`）执行反向查询：

```cpp
inline std::string TypeIndexToTypeKey(int32_t type_index) {
  const TypeInfo* type_info = TVMFFIGetTypeInfo(type_index);
  return std::string(type_info->type_key.data, type_info->type_key.size);
}
```

该函数调用 `TVMFFIGetTypeInfo`（`c_api.h:1498`）获取类型信息结构，从中提取类型键字符串。C ABI 层没有单独的 `TypeIndexToTypeKey` 函数，反向查询统一通过 `TVMFFIGetTypeInfo` 完成。

这些函数在 C++ 层被 `ObjectRef::GetTypeKey()` 和 `AnyView::GetTypeKey()` 等方法调用，用于错误报告和调试。

## 类型信息结构

每个注册的类型对应一个 `TVMFFITypeInfo` 结构（`c_api.h:1344-1380`），包含：

```c
typedef struct TVMFFITypeInfo {
  int32_t type_index;
  int32_t type_depth;
  const char* type_key;
  const int32_t* type_ancestors;
  uint64_t type_key_hash;
  uint32_t num_fields;
  uint32_t num_methods;
  TVMFFIFieldInfo* fields;
  TVMFFIFuncInfo* methods;
  TVMFFIValue metadata;
} TVMFFITypeInfo;
```

- `type_depth`：继承链深度，用于 `IsInstance` 检查。
- `type_ancestors`：祖先类型索引数组，支持沿继承链向上查询。
- `type_key_hash`：类型键的预计算哈希值。
- `num_fields`/`fields`：反射字段信息（结构化类型）。
- `num_methods`/`methods`：反射方法信息。

`TVMFFIGetTypeInfo`（`c_api.h:1498`）通过类型索引获取完整的类型信息结构。

## C++ 层类型索引

在 C++ 层，`Object` 类通过静态成员管理类型索引（`object.h:287-386`）：

```cpp
static constexpr const char* _type_key = "runtime.Object";
static constexpr const bool _type_final = false;
static constexpr const bool _type_mutable = false;
static constexpr uint32_t _type_child_slots = 0;
static uint32_t _type_index;
static constexpr uint32_t _type_child_slots_can_overflow = true;
```

`_type_index` 是静态成员，在首次使用时通过 `RuntimeTypeIndex()`（`object.h:299-309`）延迟初始化：

```cpp
static uint32_t RuntimeTypeIndex() {
  if (TVM_FFI_PREDICT_FALSE(_type_index == 0)) {
    _GetOrAllocRuntimeTypeIndex();
  }
  return _type_index;
}
```

`TVM_FFI_DECLARE_OBJECT_INFO` 和相关宏（`object.h:928-981`）自动生成这些静态成员的声明和定义，子类通过覆盖 `_type_key` 和 `_type_child_slots` 注册自己的类型信息。

## 设计分析

类型索引体系体现了以下设计考量：

1. **整数标识 vs 字符串标识**：运行时分派使用整数索引（O(1) 比较），仅在调试和反射时查询字符串键。性能敏感路径完全避免字符串比较。
2. **区段保留**：三个区段之间的间隙（13-63、78-127）为未来扩展预留空间，ABI 兼容性好。
3. **C ABI 友好**：枚举使用 `int32_t` 底层类型，跨语言稳定；类型索引查询函数为纯 C 接口，可从任意 FFI 语言调用。
4. **延迟初始化**：C++ 静态类型索引在首次使用时分配，避免静态初始化顺序问题，同时支持动态库延迟加载。
5. **继承信息内联**：`type_depth` 和 `type_ancestors` 数组支持高效的 `IsInstance` 检查，无需 RTTI 或虚函数调用。

## 相关概念

- [020 静态与动态类型索引](020-static-dynamic-type-index.md)：静态/动态注册的详细对比
- [027 TVMFFIObject 对象头](027-object-header.md)：对象头中的 type_index 字段
- [029 对象继承模型](029-object-inheritance.md)：type_ancestors 与 IsInstance
- [032 不透明对象](032-opaque-object.md)：动态类型对象的特殊形态
