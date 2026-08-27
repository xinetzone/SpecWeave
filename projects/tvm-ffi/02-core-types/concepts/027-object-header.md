---
type: Concept
title: "视角027：TVMFFIObject 对象头"
description: "解析 TVMFFIObject 结构体的 24 字节布局，包括 combined_ref_count 组合引用计数、type_index 类型索引、__padding 填充，以及 deleter 析构函数指针的联合体设计。"
tags:
  - core-types
  - object
  - object-header
  - memory-layout
  - c-abi
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-012, F-013
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
---

# 视角027：TVMFFIObject 对象头

## 概述

`TVMFFIObject` 是所有堆分配 FFI 对象的公共头部，定义在 `include/tvm/ffi/c_api.h:241-287`。它恰好占据 24 字节，包含引用计数、类型索引和析构函数指针三个核心字段。所有 FFI 对象（`StringObj`、`ArrayObj`、`MapObj`、`FunctionObj` 等）在其内存布局的起始位置嵌入此头部，使得 C ABI 层可以通过统一的 `TVMFFIObject*` 指针管理任意类型的对象。

## 结构体定义

```c
typedef struct TVMFFIObject {
  uint64_t combined_ref_count;
  int32_t type_index;
  uint32_t __padding;
  union {
    void (*deleter)(void* self, int flags);
    int64_t __ensure_align;
  };
} TVMFFIObject;
```

### 内存布局

| 偏移 | 大小 | 字段 | 用途 |
|---|---|---|---|
| 0 | 8字节 | `combined_ref_count` | 强引用（低32位）+ 弱引用（高32位） |
| 8 | 4字节 | `type_index` | 运行时类型索引 |
| 12 | 4字节 | `__padding` | 填充，确保8字节对齐 |
| 16 | 8字节 | `deleter` / `__ensure_align` | 析构函数指针或对齐保证 |

总计 24 字节。这一布局在 64 位平台上经过精心设计，确保所有字段自然对齐。

## combined_ref_count 字段

`combined_ref_count`（`c_api.h:262`）是一个 64 位原子变量，将强引用计数和弱引用计数打包到单个机器字中：

- **低 32 位（bit 0-31）**：强引用计数。强引用保证对象存活（对象数据可访问）。
- **高 32 位（bit 32-63）**：弱引用计数。弱引用不保证对象存活，但可以通过 `TryPromoteWeakPtr` 尝试提升为强引用。

### 常量定义

在 `object.h:62-68` 中定义了操作组合计数的常量：

```cpp
constexpr uint64_t kCombinedRefCountWeakOne = static_cast<uint64_t>(1) << 32;
constexpr uint64_t kCombinedRefCountStrongOne = 1;
constexpr uint64_t kCombinedRefCountBothOne =
    kCombinedRefCountWeakOne | kCombinedRefCountStrongOne;
constexpr uint64_t kCombinedRefCountMaskUInt32 =
    (static_cast<uint64_t>(1) << 32) - 1;
```

- `kCombinedRefCountStrongOne = 1`：增加一个强引用。
- `kCombinedRefCountWeakOne = 0x100000000`：增加一个弱引用。
- `kCombinedRefCountBothOne = 0x100000001`：强引用和弱引用各为 1。
- `kCombinedRefCountMaskUInt32 = 0xFFFFFFFF`：用于提取低 32 位强引用计数。

### 初始值

新创建的对象通过 `make_object` 分配时，`combined_ref_count` 初始化为 `kCombinedRefCountBothOne`（强=1，弱=1）。弱引用始终从 1 开始，因为对象自身持有一个隐式弱引用，确保在强引用归零时对象头本身（包括 `combined_ref_count`）仍然有效，直到弱引用也归零。

## type_index 字段

`type_index`（`c_api.h:269`）是 `int32_t` 类型，存储对象的运行时类型索引。它与 `TVMFFIAny.type_index` 使用相同的枚举体系：

- 静态对象类型：64-77（如 `kTVMFFIStr=65`、`kTVMFFIArray=71`）。
- 动态对象类型：>=128。

此字段驱动运行时类型检查（`IsInstance`）、类型转换（`as`/`cast`）和反射（`GetTypeInfo`）。与 `TVMFFIAny` 不同，对象的 `type_index` 始终 >= 64，因为只有堆对象才有对象头。

## __padding 字段

`__padding`（`c_api.h:271`）是 4 字节填充，确保 `deleter` 联合体从 16 字节偏移开始（8 字节对齐）。虽然 C 编译器在大多数平台上会自动插入填充，但显式声明确保了跨编译器和平台的布局一致性，这对于 C ABI 稳定性至关重要。

## deleter 联合体

```c
union {
  void (*deleter)(void* self, int flags);
  int64_t __ensure_align;
};
```

### deleter 函数指针

`deleter`（`c_api.h:277-284`）是对象的析构函数指针，签名为：

```c
void deleter(void* self, int flags);
```

- `self`：指向 `TVMFFIObject` 自身的指针（注意不是对象数据起始地址，而是头部地址）。
- `flags`：`TVMFFIObjectDeleterFlagBitMask` 枚举值，指示删除阶段。

### 删除标志

`TVMFFIObjectDeleterFlagBitMask`（`c_api.h:211-234`）定义了三个标志：

```c
typedef enum {
  kTVMFFIObjectDeleterFlagBitMaskStrong = 1 << 0,  // 1：强删除（调用析构函数）
  kTVMFFIObjectDeleterFlagBitMaskWeak = 1 << 1,    // 2：弱删除（释放内存）
  kTVMFFIObjectDeleterFlagBitMaskBoth = 3,         // 3：两者同时
} TVMFFIObjectDeleterFlagBitMask;
```

两阶段删除的设计允许：
- **强删除（Strong）**：当强引用归零时调用，执行 C++ 析构函数，释放对象持有的资源（如文件句柄、其他对象引用）。但对象内存本身不释放。
- **弱删除（Weak）**：当弱引用归零时调用，释放对象的内存块。
- **同时删除（Both）**：强引用和弱引用同时归零时的快速路径，一次调用完成析构和内存释放。

### __ensure_align

`__ensure_align` 是一个 `int64_t` 字段，确保联合体至少 8 字节对齐。在 64 位平台上函数指针本身就是 8 字节，此字段主要用于在 32 位平台或奇异平台上保证对齐一致性。它不存储有效数据。

## C++ Object 类的封装

C++ 层的 `Object` 类（`object.h:127`）以 `protected` 方式嵌入 `TVMFFIObject header_`：

```cpp
class Object {
 protected:
  TVMFFIObject header_;
  // ...
};
```

`Object` 提供类型安全的方法访问头部字段：

- `type_index()`（`object.h:150`）：返回 `header_.type_index`。
- `use_count()`（`object.h:190-201`）：通过原子加载读取 `combined_ref_count` 并掩码提取强引用计数。
- `unique()`（`object.h:184`）：`use_count() == 1`。
- `IncRef()`（`object.h:245-252`）：原子递增强引用计数。
- `DecRef()`（`object.h:300-363`）：原子递减强引用计数并触发删除。
- `IncWeakRef()`/`DecWeakRef()`：管理弱引用。
- `TryPromoteWeakPtr()`（`object.h:258-286`）：CAS 循环尝试将弱引用提升为强引用。

### 构造函数初始化

`Object` 的默认构造函数（`object.h:133-138`）将头部清零：

```cpp
Object() {
  header_.combined_ref_count = 0;
  header_.type_index = 0;
  header_.__padding = 0;
  header_.__ensure_align = 0;
}
```

实际的类型索引和引用计数由 `make_object` 在分配后设置，而非构造函数中。这是因为 `Object` 可能被直接嵌入栈对象或作为值成员，此时不需要引用计数管理。

## 对象创建流程

`make_object<T>`（`memory.h:279`）创建堆对象的流程：

1. 通过 `SimpleObjAllocator` 分配 `sizeof(T)` 字节的内存。
2. 使用 placement new 在分配的内存上构造 `T` 对象（`Object` 构造函数将头部清零）。
3. 设置 `header_.combined_ref_count = kCombinedRefCountBothOne`。
4. 设置 `header_.type_index = T::RuntimeTypeIndex()`。
5. 设置 `header_.deleter = ObjectDeleter<T>::Deleter_`。
6. 返回 `ObjectPtr<T>`。

`ObjectDeleter<T>` 是一个模板化的删除器，知道如何调用 `T` 的析构函数并释放内存。

## 设计分析

`TVMFFIObject` 对象头的设计体现了多个工程考量：

1. **C ABI 兼容**：纯 C 结构体，无虚函数表，无 C++ 名称修饰。任意语言都可以读取头部字段并管理对象生命周期。
2. **原子效率**：强/弱引用计数打包到单个 64 位原子变量中，`IncRef` 只需一次原子加法。分离的两个计数器将需要两次原子操作。
3. **两阶段删除**：强删除和弱删除的分离允许弱引用在对象析构后安全检测到对象已死亡，而不会访问已释放的内存。
4. **24字节开销**：每个堆对象有 24 字节固定开销。对于小对象（如短字符串已通过 SSO 避免堆分配），这是合理的代价。
5. **deleter 多态**：通过函数指针而非虚函数实现多态删除，避免了虚表指针（vptr）的 8 字节开销和 RTTI 依赖。删除器在对象创建时设置，运行时不可变。
6. **显式对齐**：`__padding` 和 `__ensure_align` 确保跨平台布局一致，这对于序列化为原始内存或跨 FFI 边界传递至关重要。

## 相关概念

- [028 组合引用计数](028-combined-refcount.md)：引用计数的详细机制
- [031 Deleter 析构机制](031-deleter.md)：两阶段删除的深入分析
- [029 对象继承模型](029-object-inheritance.md)：type_index 与 IsInstance
- [030 ObjectRef 包装器](030-object-ref-wrapper.md)：ObjectPtr 与对象头的交互
