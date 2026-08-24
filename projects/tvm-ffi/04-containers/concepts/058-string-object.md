---
type: Concept
title: "视角058：String 字符串对象"
description: "深入剖析 StringObj/String 字符串容器的设计，包括小字符串优化（SSO）、BytesBaseCell 内联存储、大字符串的堆对象分配、比较与查找操作以及与 Bytes 的类型区分。"
tags:
  - containers
  - string
  - sso
  - small-string-optimization
  - inplace-storage
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-167, F-168
  - code:
    - include/tvm/ffi/string.h
    - include/tvm/ffi/c_api.h
---

# 视角058：String 字符串对象

## 概述

`String` 是 TVM FFI 中的托管字符串容器，底层对象为 `StringObj`。它采用经典的**小字符串优化**（Small String Optimization, SSO）：长度不超过 7 字节的字符串直接内联存储在 `TVMFFIAny` 的 16 字节结构体中，零堆分配；超过 7 字节的字符串通过 `make_inplace_array_object` 在堆上分配 `StringObj`，字符数据紧邻对象头之后存储。`String` 不继承自 `ObjectRef`，而是直接持有一个 `BytesBaseCell`，其内存布局与 `Any` 完全一致，可以直接嵌入 `Any` 容器。

## BytesObjBase 与 StringObj

`StringObj` 定义在 `include/tvm/ffi/string.h:82`，继承链为 `StringObj → BytesObjBase → Object, TVMFFIByteArray`：

```cpp
class BytesObjBase : public Object, public TVMFFIByteArray {};

class StringObj : public BytesObjBase {
 public:
  static constexpr const uint32_t _type_index = TypeIndex::kTVMFFIStr;
  static const constexpr bool _type_final = true;
  TVM_FFI_DECLARE_OBJECT_INFO_STATIC(StaticTypeKey::kTVMFFIStr, StringObj, Object);
};
```

`TVMFFIByteArray`（`c_api.h:355-362`）包含 `data` 指针和 `size` 字段。`StringObj` 本身不添加任何额外字段，是一个 POD 类型（注释在 `string.h:81` 明确标注"This is a POD type"）。对于大字符串，字符数据通过 `make_inplace_array_object<StringObj, char>(size + 1)` 内联分配在对象头之后（`string.h:217`），并额外分配 1 字节用于 `\0` 终止符。

`BytesObjStdImpl`（`string.h:92`）是从 `std::string` 移动构造的辅助类，持有一个 `std::string` 成员，用于零拷贝地接收 `std::string` 的所有权。

## BytesBaseCell：SSO 核心

`BytesBaseCell` 定义在 `string.h:107`，是 `String` 和 `Bytes` 的内部存储单元，恰好包含一个 `TVMFFIAny data_` 字段（`string.h:260`）。它利用 `TVMFFIAny` 的 16 字节布局实现 SSO：

**小字符串模式**（`type_index < kTVMFFIStaticObjectBegin`，即 < 64）：
- `type_index` 设置为 `kTVMFFISmallStr`（值 11）。
- 字符串内容存储在 `v_bytes[8]` 中。
- 长度存储在 `small_str_len` 字段（即 `zero_padding` 联合体，偏移 4）。
- 最大容量为 7 字节（`kMaxSmallBytesLen = sizeof(int64_t) - 1 = 7`，`string.h:207`），第 8 字节为 `\0`。

**大字符串模式**（`type_index >= kTVMFFIStaticObjectBegin`）：
- `type_index` 设置为 `kTVMFFIStr`（值 65）。
- `v_obj` 指向堆上的 `StringObj`。
- 数据指针和长度从 `StringObj` 的 `TVMFFIByteArray` 字段获取。

`data()` 方法（`string.h:168`）根据类型索引选择内联数据或堆对象数据：

```cpp
const char* data() const noexcept {
  if (data_.type_index < TypeIndex::kTVMFFIStaticObjectBegin) {
    return data_.v_bytes;
  } else {
    return TVMFFIBytesGetByteArrayPtr(data_.v_obj)->data;
  }
}
```

## String 类

`String` 定义在 `string.h:402`，提供与 `std::string` 相似的 API：

- **data/c_str**（`string.h:516,523`）：返回字符数据指针，`c_str()` 保证 `\0` 终止。
- **size/length**（`string.h:530,596`）：返回字符串长度。
- **empty**（`string.h:603`）：判断是否为空。
- **at**（`string.h:611`）：带边界检查的字符访问。
- **compare**（`string.h:540,552,564,587`）：支持与 `String`、`std::string`、`const char*`、`TVMFFIByteArray` 比较。
- **find**（`string.h:628,636,645`）：子串查找，委托给 `std::string_view`。
- **substr**（`string.h:655`）：子串提取。
- **starts_with/ends_with**（`string.h:668,675`）：前后缀检查。

`String` 删除了 `nullptr` 构造函数（`string.h:407`），防止意外的空指针构造。比较操作使用 `Bytes::memncmp`（`string.h:347`），这是一个自定义的字节比较函数，避免了 `std::strncmp` 对 `\0` 的特殊处理。

## 大字符串分配

`InitSpaceForSize`（`string.h:206`）是分配字符串存储空间的核心方法：

```cpp
template <typename LargeObj>
char* InitSpaceForSize(size_t size, int32_t small_type_index,
                       int32_t large_type_index) {
  size_t kMaxSmallBytesLen = sizeof(int64_t) - 1;
  data_.type_index = small_type_index;
  data_.zero_padding = 0;
  if (size <= kMaxSmallBytesLen) {
    data_.small_str_len = static_cast<uint32_t>(size);
    return data_.v_bytes;
  } else {
    ObjectPtr<LargeObj> ptr =
        make_inplace_array_object<LargeObj, char>(size + 1);
    char* dest_data = reinterpret_cast<char*>(ptr.get()) + sizeof(LargeObj);
    ptr->data = dest_data;
    ptr->size = size;
    data_.v_obj = details::ObjectUnsafe::MoveObjectPtrToTVMFFIObjectPtr(
        std::move(ptr));
    data_.type_index = large_type_index;
    return dest_data;
  }
}
```

该方法先重置为小字符串类型（异常安全），然后根据大小选择内联或堆分配。大字符串分配 `size + 1` 字节以容纳 `\0` 终止符，数据指针设置为对象头之后的地址。

## 拷贝与移动语义

`BytesBaseCell` 的拷贝构造函数（`string.h:122`）在源为堆对象时增加引用计数；移动构造函数（`string.h:128`）将源重置为 None。析构函数（`string.h:142`）在堆对象模式下减少引用计数。这使得 `String` 的拷贝是浅拷贝（引用计数增减），移动是零开销的指针转移。

`String` 的拷贝/移动构造函数和赋值运算符均为 `= default`（`string.h:417-432`），编译器生成的代码正确地委托给 `BytesBaseCell` 的对应操作。

## 设计分析

1. **SSO 阈值选择**：7 字节的阈值来自 `TVMFFIAny` 的 8 字节 `v_bytes` 数组减去 1 字节 `\0`。这覆盖了常见的短字符串场景（键名、属性名、运算符名称等），在编译器 IR 中大量字符串不超过此长度。

2. **零开销嵌入 Any**：`String` 内部就是一个 `TVMFFIAny`，可以直接通过 `CopyToTVMFFIAny`/`MoveFromAny` 与 `Any` 互相转换，无需额外的适配层。小字符串完全在 Any 的 16 字节内表示。

3. **String vs Bytes 类型区分**：`StringObj`（`kTVMFFIStr`）和 `BytesObj`（`kTVMFFIBytes`）是不同的类型索引，尽管存储机制完全相同。这遵循 Python 约定——字符串是文本，字节是原始数据，两者不可隐式互换。小模式也对应 `kTVMFFISmallStr`（11）和 `kTVMFFISmallBytes`（12）。

4. **POD 对象设计**：`StringObj` 不添加虚函数或额外字段，确保 `make_inplace_array_object` 的内联布局简单可靠。类型分派通过 `Object` 基类的 `type_index` 而非虚函数表完成。

## 相关概念

- [059 Bytes 字节数组对象](059-bytes-object.md)：共享 SSO 机制的字节数组容器
- [021 小字符串优化](/02-core-types/concepts/021-small-string-optimization.md)：SSO 在 Any 布局中的基础
- [016 TVMFFIAny 16字节布局](/02-core-types/concepts/016-any-16-byte-layout.md)：String 的底层载体
- [061 原地数组存储](061-inplace-array-storage.md)：大字符串的内联堆分配
