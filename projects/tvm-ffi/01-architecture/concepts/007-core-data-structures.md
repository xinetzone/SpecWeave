---
type: Concept
title: "视角007：核心数据结构"
description: "分析 TVM FFI 的核心数据结构：TVMFFIAny（16字节类型擦除值）、TVMFFIObject（24字节对象头）、TVMFFIFunctionCell（16字节函数单元），以及它们之间的组合关系。"
tags:
  - architecture
  - data-structures
  - memory-layout
  - any
  - object
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-012, F-013, F-014, F-015, F-016, F-075
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/any.h
    - include/tvm/ffi/object.h
---

# 视角007：核心数据结构

## 概述

TVM FFI 的 C ABI 层定义了三个核心数据结构，它们构成了整个类型系统和对象系统的基石：`TVMFFIAny`（16字节类型擦除值）、`TVMFFIObject`（24字节对象头）、`TVMFFIFunctionCell`（16字节函数单元）。本视角详细分析这三个结构的内存布局、字段语义和组合关系。

## TVMFFIAny：类型擦除值

### 内存布局

`TVMFFIAny` 定义在 `c_api.h:297-342`，总大小 16 字节：

| 偏移 | 大小 | 字段 | 类型 | 说明 |
|------|------|------|------|------|
| 0 | 4 | `type_index` | `int32_t` | 类型标识，对应 `TVMFFITypeIndex` |
| 4 | 4 | `zero_padding` / `small_str_len` | `uint32_t` | 填充零或小字符串长度 |
| 8 | 8 | 数据联合体 | `union` | 实际数据存储 |

### 数据联合体

联合体（`c_api.h:309-333`）可容纳以下类型：

| 成员 | 类型 | 用途 |
|------|------|------|
| `v_int64` | `int64_t` | 整数、布尔值 |
| `v_float64` | `double` | 浮点数 |
| `v_uint64` | `uint64_t` | 无符号整数 |
| `v_ptr` | `void*` | 不透明指针 |
| `v_c_str` | `const char*` | C 字符串指针 |
| `v_obj` | `TVMFFIObject*` | 堆对象指针 |
| `v_dtype` | `DLDataType` | 张量数据类型（4字节，利用部分空间） |
| `v_device` | `DLDevice` | 设备标识（8字节） |
| `v_bytes` | `char[8]` | 小字符串/字节内联存储 |

### 特殊编码

1. **null 值**：`type_index = kTVMFFINone = 0`，数据字段为零。
2. **小字符串**：`type_index = kTVMFFISmallStr = 11`，字符串内容存在 `v_bytes[0..small_str_len-1]`，最多 7 字节（第8字节为终止符或长度限制）。
3. **右值引用标记**：`type_index = kTVMFFIObjectRValueRef = 10`，表示对象右值引用，用于移动语义优化。

## TVMFFIObject：堆对象头

### 内存布局

`TVMFFIObject` 定义在 `c_api.h:241-264`，总大小 24 字节：

| 偏移 | 大小 | 字段 | 类型 | 说明 |
|------|------|------|------|------|
| 0 | 8 | `combined_ref_count` | `uint64_t` | 组合引用计数（原子） |
| 8 | 4 | `type_index` | `int32_t` | 对象类型索引 |
| 12 | 4 | `__padding` | `uint32_t` | 对齐填充 |
| 16 | 8 | `deleter` / `__ensure_align` | 联合体 | 删除器函数指针或对齐保证 |

### 组合引用计数

`combined_ref_count` 将强引用计数和弱引用计数打包在一个 64 位原子变量中：

- 低 32 位：强引用计数（strong count），归零时对象被销毁。
- 高 32 位：弱引用计数（weak count），归零时内存被释放。

强引用 +1 等价于 `combined_ref_count += 1`；弱引用 +1 等价于 `combined_ref_count += (1ULL << 32)`。这种打包设计使得强引用操作是最常见的快速路径（单条原子加指令）。

### 删除器机制

`deleter` 字段（偏移 16）是一个函数指针，类型为 `void (*)(void* self, int flags)`。`flags` 参数由 `TVMFFIObjectDeleterFlagBitMask` 枚举定义，控制删除行为（强引用删除、弱引用删除或两者皆有）。当强引用计数归零时，调用 `deleter` 执行对象特定的清理逻辑。对于普通 C++ 对象，删除器调用析构函数并释放内存。

### 对象继承模式

所有 FFI 堆对象以 `TVMFFIObject` 作为第一个成员：

```
+-------------------+
|  TVMFFIObject     |  24字节（头部）
|  (ref_count, ...) |
+-------------------+
|  派生类型数据      |  N字节（用户字段）
+-------------------+
```

C ABI 通过 `void*` 句柄引用对象，调用 `TVMFFIObjectGetTypeIndex`（内联函数，直接读取头部字段）确定实际类型，C++ 层通过 `TVMFFIGetTypeInfo` 获取类型继承关系并进行安全的向下转型。

## TVMFFIFunctionCell：函数单元

### 内存布局

`TVMFFIFunctionCell` 定义在 `c_api.h:509-514`，总大小 16 字节：

| 偏移 | 大小 | 字段 | 类型 | 说明 |
|------|------|------|------|------|
| 0 | 8 | `safe_call` | `TVMFFISafeCallType` | C 安全调用路径 |
| 8 | 8 | `cpp_call` | `void*` | C++ 快速路径函数指针（实际签名同 safe_call 但返回 void） |

### 函数单元与对象的关系

`TVMFFIFunctionCell` 嵌入在函数对象内部。函数对象的完整布局为：

```
+-------------------+
|  TVMFFIObject     |  24字节（type_index = kTVMFFIFunction）
+-------------------+
|  TVMFFIFunctionCell|  16字节（safe_call + cpp_call）
+-------------------+
|  资源句柄等        |  可变
+-------------------+
```

`TVMFFIFunctionCreate`（`c_api.h:719`）创建函数对象时分配包含 `TVMFFIObject` 头部和 `TVMFFIFunctionCell` 的内存块，并设置 `safe_call` 和 `cpp_call` 函数指针。

### 调用路径选择

- **跨语言调用**：使用 `safe_call`，C++ 异常在函数内部被捕获并转换为错误码，通过 TLS 传递错误对象。
- **C++ 内部调用**：可使用 `cpp_call`，异常直接传播，避免 try-catch 开销。
- `TVMFFIFunctionCall`（`c_api.h:746`）始终使用 `safe_call` 路径，确保 C ABI 边界不传播异常。

## 结构间的组合关系

### Any 引用 Object

`TVMFFIAny` 通过 `v_obj` 成员持有 `TVMFFIObject*` 指针。当 `type_index` 属于对象类型范围（>= 64）时，`v_obj` 指向堆对象。`Any` 的拷贝构造检查 `IsObject()`，对对象类型增加引用计数。

### Object 包含 FunctionCell

函数对象是 `TVMFFIObject` 的特化，在头部之后包含 `TVMFFIFunctionCell`。这种组合而非继承的关系（C 层面）使得函数单元可以被嵌入到任意对象中，不限于特定的继承层级。

### 函数调用中的 Any

`TVMFFISafeCallType` 的签名以 `TVMFFIAny*` 作为参数和返回值载体：

```c
int (*safe_call)(void* resource_handle,
                 const TVMFFIAny* args,
                 int32_t num_args,
                 TVMFFIAny* result);
```

函数调用时，参数以 `TVMFFIAny` 数组形式连续传递，返回值写入 `result` 指向的 `TVMFFIAny`。这形成了"Any 传值 → Object 引用 → Function 调度"的完整数据通路。

## 设计分析

三个核心结构的设计体现了紧凑性和正交性：

1. **紧凑性**：总核心结构大小仅 56 字节（16 + 24 + 16），且全部为 POD 类型，内存布局可预测、可跨语言映射。
2. **正交性**：`Any` 负责值表示，`Object` 负责生命周期，`FunctionCell` 负责可调用性。三者通过指针组合而非继承耦合，可以独立演进。
3. **缓存友好**：16 字节的 `Any` 可以在两个寄存器中传递；24 字节的 `Object` 头部在单次缓存行读取中即可获取引用计数和类型信息。

## 相关概念

- [003 类型擦除模式](003-type-erasure-pattern.md)：Any 的类型擦除语义
- [006 最小核心设计哲学](006-minimal-core-philosophy.md)：三原语设计
- [013 内存所有权模型](013-memory-ownership-model.md)：Object 引用计数
- [016 TVMFFIAny 16字节布局](/02-core-types/concepts/016-any-16-byte-layout.md)：Any 布局详解
