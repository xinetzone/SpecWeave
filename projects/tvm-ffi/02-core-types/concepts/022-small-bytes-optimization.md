---
type: Concept
title: "视角022：小字节数组优化"
description: "分析 TVM FFI 的小字节数组内联优化（SmallBytes, type_index=12），包括与小字符串的异同、7字节内联存储、二进制数据处理，以及在跨语言边界传递短二进制数据时的零拷贝优势。"
tags:
  - core-types
  - small-bytes
  - sso
  - binary-data
  - optimization
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-009, F-010, F-011
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/string.h
    - include/tvm/ffi/any.h
---

# 视角022：小字节数组优化

## 概述

小字节数组优化（Small Bytes Optimization）是 TVM FFI 针对短二进制数据的内联存储机制，类型索引为 `kTVMFFISmallBytes = 12`（`c_api.h:138`）。与小字符串优化类似，长度不超过 7 字节的字节数组直接存储在 `TVMFFIAny` 的 `v_bytes[8]` 联合体中，长度记录在 `small_str_len` 字段中。小字节数组不要求 `\0` 终止，可以包含任意二进制内容，包括嵌入的空字节。

## 与小字符串的异同

### 相同点

小字节数组与小字符串共享相同的底层存储机制：
- 都使用 `v_bytes[8]` 存储数据，最大容量 7 字节。
- 都使用 `small_str_len` 字段记录长度。
- 都通过 `type_index < kTVMFFIStaticObjectBegin`（64）判断为内联存储。
- 都使用相同的 `InitSpaceForSize` 模板方法分配空间（`string.h:206`）。
- 都支持透明切换到堆对象（`BytesObj`/`StringObj`）。

### 不同点

| 维度 | SmallStr (11) | SmallBytes (12) |
|---|---|---|
| 内容语义 | UTF-8 文本 | 任意二进制 |
| `\0` 终止 | 保证终止 | 不要求终止 |
| C++ 类 | `String` | `Bytes` |
| 堆对象类型 | `kTVMFFIStr` (65) | `kTVMFFIBytes` (66) |
| 比较语义 | 文本比较 | 二进制内存比较 |
| 哈希输入 | 字符串内容 | 原始字节 |

关键区别在于 `Bytes` 不保证 `\0` 终止。`InitSpaceForSize` 的注释明确说明 "always reserve one byte for \0 compactibility"（`string.h:202`），但这主要是为了与 C 字符串 API 兼容时的安全性——对于字节数组，第 8 字节可能包含有效数据，而 `small_str_len` 准确记录实际长度。

## Bytes 类设计

### 默认构造

`Bytes` 的默认构造函数（`string.h:269`）初始化为小字节数组类型：

```cpp
Bytes() { data_.InitTypeIndex(TypeIndex::kTVMFFISmallBytes); }
```

空字节数组表示为 `type_index = kTVMFFISmallBytes`、`small_str_len = 0`。

### 空间分配

`Bytes` 通过 `InitSpaceForSize<details::BytesObj>` 分配空间（`string.h:386`）：

```cpp
char* dest = data_.InitSpaceForSize<details::BytesObj>(
    size, TypeIndex::kTVMFFISmallBytes, TypeIndex::kTVMFFIBytes);
```

当 `size <= 7` 时，返回 `v_bytes` 内联指针；当 `size > 7` 时，在堆上分配 `BytesObj` 对象，设置 `type_index = kTVMFFIBytes`。

### 数据访问

`Bytes` 继承自 `BytesBaseCell`，使用相同的 `data()` 和 `size()` 方法（`string.h:168-184`）：

```cpp
const char* data() const noexcept {
  if (data_.type_index < TypeIndex::kTVMFFIStaticObjectBegin) {
    return data_.v_bytes;
  } else {
    return TVMFFIBytesGetByteArrayPtr(data_.v_obj)->data;
  }
}
```

`data()` 返回 `const char*`，但调用者应根据 `size()` 确定有效数据长度，不应假设 `\0` 终止。

## 类型特征

`TypeTraits<Bytes>` 在 `string.h` 中特化，提供 FFI 类型转换支持。`Bytes` 的 `field_static_type_index` 为 `kTVMFFIBytes`，但在 FFI 传输过程中，短字节数组自动使用 `kTVMFFISmallBytes` 类型索引。这意味着类型特征中声明的静态类型索引与实际运行时类型索引可能不同——`CheckAnyStrict` 会同时接受小字节数组和堆字节数组。

## 非拥有字节数组指针

除了拥有的 `Bytes` 类型，TVM FFI 还定义了 `kTVMFFIByteArrayPtr = 9`（`c_api.h:125`），用于非拥有地引用外部字节数组。其 `v_ptr` 字段指向 `TVMFFIByteArray` 结构：

```c
typedef struct {
  const char* data;
  size_t size;
} TVMFFIByteArray;
```

当从 `AnyView` 构造 `Any` 时，`InplaceConvertAnyViewToAny`（`any.h:201-224`）会将 `kTVMFFIByteArrayPtr` 转换为拥有的 `Bytes` 堆对象，复制数据内容。这确保了 `Any` 的值语义——即使原始数据由外部管理，`Any` 也持有独立副本。

## C API 支持

`TVMFFISmallBytesGetContentByteArray`（`c_api.h:1566-1567`）提供小字节数组的直接访问：

```c
inline TVMFFIByteArray TVMFFISmallBytesGetContentByteArray(const TVMFFIAny* value) {
  return TVMFFIByteArray{value->v_bytes, static_cast<size_t>(value->small_str_len)};
}
```

返回的 `TVMFFIByteArray` 包含指向内联数据的指针和长度。调用者不应释放该指针——它指向 `TVMFFIAny` 内部。

C API 还提供 `TVMFFIBytesGetByteArrayPtr`（`c_api.h`）用于获取堆字节数组对象的数据指针，以及 `TVMFFIBytesAllocFromBytes`（`c_api.h:912`）用于从现有数据创建新的 `Bytes` 值。

## 哈希与比较

### 哈希

小字节数组使用与小字符串相同的 `StableHashSmallStrBytes` 函数（`base_details.h:350`）计算哈希，因为两者的内存布局相同。堆字节数组通过 `BytesObjBase` 接口访问数据并计算内容哈希。哈希一致性保证了 `Bytes` 键在 `Map` 中的正确查找。

### 比较

`AnyEqual`（`any.h:804-813`）处理小字节数组与堆字节数组之间的跨表示比较：

```cpp
if (lhs.data_.type_index == kTVMFFIBytes && rhs.data_.type_index == kTVMFFISmallBytes) {
  return Bytes::memequal(lhs_bytes->data, rhs.data_.v_bytes,
                         lhs_bytes->size, rhs.data_.small_str_len);
}
```

比较使用 `memcmp` 语义，基于原始字节内容，不涉及文本编码。

## 典型应用场景

小字节数组优化在以下场景中特别有价值：

1. **短哈希值/摘要**：MD5（16字节）虽超出内联限制，但 CRC32（4字节）、短 token 等可内联。
2. **小型枚举标签**：二进制协议中的短标签字段。
3. **序列化小对象**：紧凑二进制格式中的小整数值、标志位组合。
4. **跨语言数据传递**：在 Python 和 C++ 之间传递短 `bytes` 对象时避免拷贝。
5. **NPU/加速器元数据**：设备句柄、内核标识符等短二进制标识符。

## 设计分析

小字节数组优化与小字符串优化共享基础设施但语义独立，体现了以下考量：

1. **代码复用**：通过 `BytesBaseCell` 模板基类和 `InitSpaceForSize` 泛型方法，字符串和字节数组共享分配逻辑，减少代码重复。
2. **类型区分**：使用不同的 `type_index`（11 vs 12, 65 vs 66）区分文本和二进制，允许类型系统在跨语言边界时选择正确的转换策略（如 Python 中 `str` vs `bytes`）。
3. **无终止符假设**：字节数组不依赖 `\0` 终止，通过显式长度字段管理数据，这对于包含空字节的二进制数据至关重要。
4. **非拥有到拥有的转换**：`ByteArrayPtr` 到 `Bytes` 的自动转换确保了 FFI 边界处的值语义安全，防止悬垂指针。
5. **与 DLPack 的协同**：字节数组可用于包装原始张量数据的短元数据，而大张量数据通过 `DLTensorPtr` 零拷贝传递。

## 相关概念

- [021 小字符串优化](021-small-string-optimization.md)：共享底层机制的字符串优化
- [016 TVMFFIAny 16字节布局](016-any-16-byte-layout.md)：v_bytes 和 small_str_len 字段
- [018 Any 拥有语义](018-any-owning.md)：ByteArrayPtr 到 Bytes 的所有权转换
- [027 TVMFFIObject 对象头](027-object-header.md)：堆字节数组对象 BytesObj
