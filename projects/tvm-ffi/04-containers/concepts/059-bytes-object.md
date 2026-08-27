---
type: Concept
title: "视角059：Bytes 字节数组对象"
description: "深入剖析 BytesObj/Bytes 字节数组容器的设计，包括与 String 共享的 SSO 机制、原始字节语义、内存比较工具函数以及 String/Bytes 类型区分的设计意图。"
tags:
  - containers
  - bytes
  - sso
  - raw-data
  - binary
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-169, F-170
  - code:
    - include/tvm/ffi/string.h
    - include/tvm/ffi/c_api.h
---

# 视角059：Bytes 字节数组对象

## 概述

`Bytes` 是 TVM FFI 中的字节数组容器，底层对象为 `BytesObj`。它与 `String` 共享完全相同的存储机制——`BytesBaseCell` 的小字节优化（≤7 字节内联，超过则堆分配），但语义不同：`Bytes` 表示原始二进制数据，不保证 `\0` 终止，不赋予内容文本含义。这种类型区分遵循 Python 的 `bytes`/`str` 分离约定，防止文本与二进制数据的意外混淆。`Bytes` 提供内存比较工具函数，支持与 `std::string` 的互操作。

## BytesObj 与类型标识

`BytesObj` 定义在 `include/tvm/ffi/string.h:74`：

```cpp
class BytesObj : public BytesObjBase {
 public:
  static constexpr const uint32_t _type_index = TypeIndex::kTVMFFIBytes;
  static const constexpr bool _type_final = true;
  TVM_FFI_DECLARE_OBJECT_INFO_STATIC(StaticTypeKey::kTVMFFIBytes, BytesObj, Object);
};
```

与 `StringObj`（`string.h:82`）结构完全相同，仅类型索引不同：
- `BytesObj`：`kTVMFFIBytes`（值 66），小模式为 `kTVMFFISmallBytes`（值 12）。
- `StringObj`：`kTVMFFIStr`（值 65），小模式为 `kTVMFFISmallStr`（值 11）。

两者共享基类 `BytesObjBase`（`string.h:66`），后者继承自 `Object` 和 `TVMFFIByteArray`，不添加任何字段。这种设计使得大字符串和大字节数组的内存布局完全一致，仅通过 `type_index` 区分。

## Bytes 类

`Bytes` 定义在 `string.h:267`，持有一个 `BytesBaseCell data_` 成员（`string.h:382`）。其 API 与 `String` 有显著差异：

- **data**（`string.h:327`）：返回 `const char*` 数据指针。
- **size**（`string.h:321`）：返回字节长度。
- **operator std::string**（`string.h:333`）：显式转换为 `std::string`，拷贝字节内容。
- 不提供 `c_str()`、`find()`、`substr()`、`starts_with()` 等文本操作方法。

默认构造函数将类型初始化为 `kTVMFFISmallBytes`（`string.h:270`），表示空字节数组。构造函数接受 `const char*` + size、`TVMFFIByteArray`、`const std::string&` 和 `std::string&&`（移动）。

`InitData`（`string.h:389`）在分配空间后使用 `std::memcpy` 复制字节数据，并在末尾写入 `\0`（`string.h:395`）。尽管 `Bytes` 不保证 `\0` 终止，但为了与 `String` 的 C 兼容性，仍保留终止符。

## 内存比较工具

`Bytes` 提供两个静态比较工具函数：

### memncmp

`memncmp`（`string.h:347`）执行两个字节序列的字典序比较：

```cpp
static int memncmp(const char* lhs, const char* rhs,
                   size_t lhs_count, size_t rhs_count) {
  if (lhs == rhs && lhs_count == rhs_count) return 0;
  for (size_t i = 0; i < lhs_count && i < rhs_count; ++i) {
    if (lhs[i] < rhs[i]) return -1;
    if (lhs[i] > rhs[i]) return 1;
  }
  if (lhs_count < rhs_count) return -1;
  else if (lhs_count > rhs_count) return 1;
  else return 0;
}
```

与 `std::memcmp` 不同，`memncmp` 处理长度不同的序列：先比较公共前缀，前缀相同时较短的序列排在前面。相同指针和长度时快速返回 0。

### memequal

`memequal`（`string.h:372`）判断两个字节序列是否完全相等：

```cpp
static bool memequal(const void* lhs, const void* rhs,
                     size_t lhs_count, size_t rhs_count) {
  return lhs_count == rhs_count &&
         (lhs == rhs || std::memcmp(lhs, rhs, lhs_count) == 0);
}
```

先比较长度（快速失败），再比较指针（相同指针直接返回 true），最后调用 `std::memcmp`。这两个函数被 `String::compare`（`string.h:541`）复用于文本比较。

## String 与 Bytes 的关系

`String` 和 `Bytes` 之间没有继承关系，也不提供隐式转换。这是有意的设计：

1. **语义隔离**：`String` 表示 UTF-8 文本（或至少是可打印字符序列），`Bytes` 表示任意二进制数据。隐式转换可能导致编码错误或安全漏洞。
2. **类型安全**：函数参数声明为 `String` 时，不能意外传入 `Bytes`，反之亦然。这在编译期就捕获了类型错误。
3. **存储共享**：尽管类型隔离，两者共享 `BytesBaseCell`、`BytesObjBase` 和 SSO 机制，代码复用通过组合和模板实现（`InitSpaceForSize<LargeObj>` 接受不同的大对象类型）。

当需要跨类型转换时，调用方必须显式构造：`String(bytes.data(), bytes.size())` 或 `Bytes(string.data(), string.size())`，明确表达转换意图。

## 小字节优化

`Bytes` 的小字节优化与 `String` 的 SSO 使用相同的机制，在 `BytesBaseCell::InitSpaceForSize` 中实现（`string.h:206`）。区别仅在于类型索引参数：

- `Bytes::InitSpaceForSize`（`string.h:385`）传入 `kTVMFFISmallBytes` 和 `kTVMFFIBytes`。
- `String` 对应的方法传入 `kTVMFFISmallStr` 和 `kTVMFFIStr`。

≤7 字节的数据存储在 `TVMFFIAny::v_bytes[8]` 中，长度在 `small_str_len` 字段；超过 7 字节则通过 `make_inplace_array_object<BytesObj, char>(size + 1)` 堆分配。

## 设计分析

1. **类型区分的工程价值**：在深度学习编译器中，`String` 常用于算子名称、属性键名等文本数据，而 `Bytes` 可用于序列化的模型权重、哈希摘要等二进制数据。类型区分防止了将二进制数据误当作文本处理（如查找子串、大小写转换）的潜在错误。

2. **代码复用策略**：`String` 和 `Bytes` 不通过继承复用代码，而是通过共享 `BytesBaseCell`（组合）和模板方法（`InitSpaceForSize<LargeObj>`）实现。这种组合优于继承的策略避免了切片问题，也使得两个类的公开 API 可以独立演化。

3. **std::string 互操作**：`Bytes` 提供 `operator std::string` 用于与标准库互操作，但这是显式转换（`explicit`），不会意外触发。从 `std::string&&` 移动构造使用 `BytesObjStdImpl`（`string.h:92`）零拷贝地接管 `std::string` 的内存。

4. **内存安全**：`memequal` 和 `memncmp` 都正确处理了相同指针（自比较）和长度为零的边界情况，避免了不必要的 `memcmp` 调用和潜在的空指针解引用。

## 相关概念

- [058 String 字符串对象](058-string-object.md)：共享 SSO 机制的文本容器
- [022 小字节优化](/02-core-types/concepts/022-small-bytes-optimization.md)：小字节内联存储机制
- [016 TVMFFIAny 16字节布局](/02-core-types/concepts/016-any-16-byte-layout.md)：Bytes 的底层载体
- [061 原地数组存储](061-inplace-array-storage.md)：大字节数组的内联堆分配
