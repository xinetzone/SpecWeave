---
type: Concept
title: "视角013：内存所有权模型"
description: "分析 TVM FFI 的内存所有权模型：组合引用计数（强/弱引用打包）、对象生命周期管理、deleter 机制、移动语义优化、小字符串内联，以及跨语言内存安全保证。"
tags:
  - architecture
  - memory
  - ownership
  - reference-counting
  - raii
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-015, F-016, F-017, F-018, F-077, F-080
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
    - include/tvm/ffi/memory.h
    - include/tvm/ffi/any.h
---

# 视角013：内存所有权模型

## 概述

TVM FFI 的内存所有权模型建立在组合引用计数（combined reference counting）之上，通过 `TVMFFIObject` 头部的 64 位原子变量同时管理强引用和弱引用。C++ 层通过 RAII 类型（`ObjectPtr`、`Any`、`ObjectRef`）自动管理引用计数，C ABI 层通过显式的 `IncRef`/`DecRef` 函数提供手动控制。本视角分析引用计数的位打包设计、对象生命周期、删除器机制和内存安全保证。

## 组合引用计数

### 位打包设计

`TVMFFIObject` 的 `combined_ref_count` 字段（`c_api.h:247`）是一个 `uint64_t` 原子变量，将强引用计数和弱引用计数打包：

```
 63                    32 31                     0
+-----------------------+------------------------+
|   弱引用计数 (32位)    |   强引用计数 (32位)     |
+-----------------------+------------------------+
```

- **低 32 位**：强引用计数（strong count）。当强引用计数归零时，对象被销毁（调用 deleter）。
- **高 32 位**：弱引用计数（weak count）。当弱引用计数也归零时，内存被释放。

### 原子操作

引用计数的增减通过原子操作实现：

- **强引用 +1**：`combined_ref_count.fetch_add(1, memory_order_relaxed)`
- **强引用 -1**：`combined_ref_count.fetch_sub(1, memory_order_acq_rel)`，然后检查低 32 位是否归零。
- **弱引用 +1**：`combined_ref_count.fetch_add(1ULL << 32, memory_order_relaxed)`
- **弱引用 -1**：`combined_ref_count.fetch_sub(1ULL << 32, memory_order_acq_rel)`，然后检查整个 64 位是否归零。

### 设计优势

1. **单原子变量**：强引用和弱引用共享一个原子变量，强引用操作（最常见路径）只需一次原子加/减，无需两次独立操作。
2. **缓存友好**：引用计数和类型索引位于同一缓存行（前 16 字节），对象访问时缓存命中率高。
3. **无单独控制块**：与 `std::shared_ptr` 不同，引用计数直接嵌入对象头部，避免了额外的控制块分配和两次指针解引用。

## 对象生命周期

### 创建

对象通过 `make_object<T>(args...)`（`memory.h:279`）创建：

1. 分配 `sizeof(T)` 字节内存（包含 `TVMFFIObject` 头部）。
2. 在头部位置构造 `TVMFFIObject`，初始化 `combined_ref_count = 1`（一个强引用）。
3. 设置 `type_index` 为 `T` 的类型索引。
4. 设置 `deleter` 为 `T` 的删除函数。
5. 在用户数据区构造 `T` 对象。
6. 返回 `ObjectPtr<T>`。

### 共享

当对象被复制到新的 `ObjectPtr` 或 `Any` 时：

- 调用 `TVMFFIObjectIncRef`（`c_api.h:557`）增加强引用计数。
- 多个 `ObjectPtr` 共享同一对象，修改通过任一引用可见。

### 销毁

当最后一个强引用释放时：

1. `DecRef` 检测到强引用计数归零。
2. 调用对象的 `deleter` 函数。
3. deleter 调用对象的析构函数（C++ 层）。
4. 如果弱引用计数也为零，直接释放内存；否则保留对象头部（已析构但内存未释放），直到弱引用也释放。

### 弱引用的生命周期

弱引用通过 `WeakObjectPtr<T>` 持有：

- 弱引用不阻止对象析构。
- `lock()` 方法尝试增加强引用计数：若强引用计数 > 0，成功并返回 `ObjectPtr<T>`；若对象已析构（强引用计数为 0），返回空指针。
- 对象析构后、弱引用释放前，内存保持但对象处于"已销毁"状态，弱引用不能访问对象字段。

## Deleter 机制

### 删除器函数指针

`TVMFFIObject` 头部偏移 16 处存储 `deleter` 函数指针：

```c
void (*deleter)(void* self, int flags);
```

`flags` 参数由 `TVMFFIObjectDeleterFlagBitMask`（`c_api.h:211`）定义：`kTVMFFIObjectDeleterFlagBitMaskStrong = 1 << 0` 表示强引用归零，`kTVMFFIObjectDeleterFlagBitMaskWeak = 1 << 1` 表示弱引用归零。当强引用计数归零时，运行时调用 `deleter(obj, kTVMFFIObjectDeleterFlagBitMaskStrong)`。删除器负责：

1. 调用对象的 C++ 析构函数（通过 `static_cast<T*>(obj)->~T()`）。
2. 当弱引用也归零时（flags 包含 weak 标志），释放对象内存。
3. 如果对象仍有弱引用，仅析构不释放内存。

### 自定义删除器

对象可以指定自定义删除器，用于：
- 使用自定义内存池分配的对象。
- 需要在销毁时执行额外清理（如释放设备内存、关闭文件句柄）。
- 非 C++ 对象（如 Python 对象包装、Rust Box）。

### 小字符串优化

对于 `kTVMFFISmallStr = 11` 类型，对象头部的 `deleter` 字段被重用为字符串数据的一部分（`v_uint64`），不存储函数指针。这是因为小字符串完全内联在 `TVMFFIAny` 中，不需要堆分配和删除器。

## 移动语义

### 右值引用标记

`TVMFFIAny` 支持 `kTVMFFIObjectRValueRef = 10` 类型索引，标记对象的右值引用：

- 当 `Any` 被移动时，源值的 `type_index` 设为 `kTVMFFINone`，避免析构时减少引用计数。
- 函数可以通过检查 `kTVMFFIObjectRValueRef` 识别移动语义，执行高效的资源转移而非深拷贝。

### Any 的移动构造

`Any(Any&& other) noexcept`：
1. 位拷贝 `other.data_` 到新对象。
2. 将 `other.data_.type_index` 设为 `kTVMFFINone`。
3. 不涉及引用计数操作（零开销移动）。

### ObjectPtr 的移动构造

`ObjectPtr(ObjectPtr&& other) noexcept`：
1. 拷贝 `data_` 指针。
2. 将 `other.data_` 设为 `nullptr`。
3. 不涉及引用计数操作。

## C ABI 引用计数 API

### 公共 API

- **`TVMFFIObjectIncRef`**（`c_api.h:557`）：增加强引用计数。
  ```c
  int TVMFFIObjectIncRef(TVMFFIObjectHandle obj);
  ```

- **`TVMFFIObjectDecRef`**（`c_api.h:563`）：减少强引用计数，归零时销毁对象。
  ```c
  int TVMFFIObjectDecRef(TVMFFIObjectHandle obj);
  ```

- **`TVMFFIObjectUseCount`**：查询当前强引用计数（主要用于调试）。

### 多线程安全

引用计数操作使用原子指令，`IncRef` 和 `DecRef` 可以在任意线程调用。对象本身的线程安全由对象实现者保证（不可变对象天然线程安全，可变对象需要额外同步）。

## 跨语言内存安全

### 所有权传递规则

跨语言边界传递对象时遵循以下规则：

1. **参数传递**：调用者拥有对象，被调用方获得借用引用（不增加引用计数，通过 `AnyView`）。若被调用方需要保留对象，必须显式 `IncRef`。
2. **返回值传递**：被调用方转移一个引用给调用方（所有权转移），调用方负责最终 `DecRef`。
3. **全局注册表**：注册表持有函数对象的一个强引用，函数在注册期间不会被销毁。
4. **容器存储**：`Array`/`Map` 等容器持有元素对象的强引用。

### 语言绑定的 RAII

- **C++**：`ObjectPtr`、`Any`、`ObjectRef` 在析构函数中自动 `DecRef`。
- **Python**：Cython 扩展类的 `__dealloc__` 方法调用 `DecRef`。
- **Rust**：包装类型实现 `Drop` trait，在 `drop` 中调用 `DecRef`。

## NPU建议

在 NPU 运行时中，内存所有权模型需要特别关注：

1. **NPU 设备内存对象**：NPU 分配的设备内存（片上 SRAM、板载 DDR）应包装为 FFI 对象，通过自定义 deleter 在引用计数归零时调用 NPU 的内存释放 API。建议定义 `NPUMemoryObj` 对象类型，头部为标准 `TVMFFIObject`，附加字段包含设备指针、大小、内存类型（SRAM/DDR）、所属设备。deleter 调用 `npu_free_memory(device, ptr)`。

2. **张量对象的内存共享**：`Tensor` 对象（`kTVMFFITensor = 70`）包装 `DLTensor`，其 `data` 字段可能指向 NPU 设备内存。张量拷贝时仅增加引用计数（浅拷贝），不复制设备内存。需要确保 NPU 内存在所有引用释放前不被回收。对于跨多函数传递的中间张量，引用计数机制天然保证了生命周期安全。

3. **异步执行与生命周期**：NPU 异步执行时，算子函数返回后 NPU 可能仍在访问张量内存。必须确保流同步完成前张量不被释放。建议：
   - 异步算子函数在提交命令时增加输入/输出张量的强引用。
   - 在流完成回调中减少引用。
   - 或要求调用者在同步前保持张量存活（在文档中明确约定）。
   推荐第一种方式（自动引用管理），避免调用者错误导致的 use-after-free。

4. **内存池集成**：NPU 运行时通常使用内存池管理设备内存以减少分配开销。自定义 deleter 可以将内存归还内存池而非真正释放，配合引用计数实现高效的对象回收。内存池本身可以是 FFI 对象，其生命周期长于从中分配的张量。

5. **主机-设备共享内存**：对于零拷贝共享内存（mapped/pinned memory），对象可能同时被 CPU 和 NPU 访问。引用计数只能管理主机端的生命周期，设备端的访问需要通过流同步保证。建议在内存对象中记录"最后使用的流"，在 deleter 中先同步该流再释放内存。

6. **内存分配钩子**：建议通过设备属性或全局配置注册 NPU 自定义的主机内存分配器（用于 FFI 对象和主机端数据结构），确保所有内存分配走统一的追踪和统计机制，便于调试内存泄漏和优化内存使用。

7. **弱引用缓存**：NPU 编译结果（如内核二进制）可以使用弱引用缓存：编译完成后注册弱引用，下次请求相同内核时若缓存未失效则直接复用，否则重新编译。这避免了缓存阻止不再使用的内核被释放。

## 设计分析

TVM FFI 的组合引用计数设计在性能和功能之间取得了良好平衡。与传统的双计数方案（强/弱各一个原子变量）相比，单变量打包方案将强引用操作（热路径）的开销减半，代价是弱引用操作需要移位。由于强引用操作远比弱引用频繁，这种偏向热路径的设计是合理的。

嵌入头部的引用计数（而非独立控制块）减少了一次缓存行访问和一次内存分配，对于包含大量小对象的编译器 IR 场景尤其有利。deleter 函数指针提供了灵活的内存管理策略，使得 FFI 可以与各种自定义分配器和内存池集成。

## 相关概念

- [004 值语义与引用语义](004-value-vs-reference-semantics.md)：值/引用语义与所有权
- [007 核心数据结构](007-core-data-structures.md)：Object 头部布局
- [012 异步流与设备管理](012-async-stream-device-management.md)：异步生命周期
- [028 组合引用计数](/02-core-types/concepts/028-combined-refcount.md)：引用计数深入分析
