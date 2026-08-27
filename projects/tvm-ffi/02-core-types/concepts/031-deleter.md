---
type: Concept
title: "视角031：Deleter 析构机制"
description: "解析 TVMFFIObject 的 deleter 函数指针机制，包括两阶段删除协议（Strong/Weak/Both 标志）、SimpleObjAllocator 中的 placement new 与显式析构、TVMFFIObjectAllocHeader 自定义分配器回调，以及在 NPU 环境中的资源回收建议。"
tags:
  - core-types
  - deleter
  - destructor
  - memory-management
  - allocator
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-064, F-065, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
    - include/tvm/ffi/memory.h
---

# 视角031：Deleter 析构机制

## 概述

`TVMFFIObject` 通过函数指针 `deleter` 实现多态析构，而非 C++ 虚函数。每个堆对象在创建时绑定一个类型特定的删除器函数，引用计数归零时由 `DecRef` 调用该函数。Deleter 接收标志位参数，区分强删除（调用析构函数释放资源）和弱删除（释放内存块），支持两阶段销毁协议。这一设计避免了虚表指针开销，同时允许自定义分配器和语言绑定集成自己的资源回收逻辑。

## deleter 函数指针

### 声明

`deleter` 定义在 `TVMFFIObject` 中（`c_api.h:277-284`）：

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

### 函数签名

```c
void deleter(void* self, int flags);
```

- `self`：指向 `TVMFFIObject` 头部的指针（注意：是头部地址，不是对象数据起始地址）。
- `flags`：`TVMFFIObjectDeleterFlagBitMask` 枚举值，指示删除阶段。

### 删除标志

定义在 `c_api.h:211-234`：

```c
enum TVMFFIObjectDeleterFlagBitMask : int32_t {
  kTVMFFIObjectDeleterFlagBitMaskStrong = 1 << 0,  // 1 = 0x01
  kTVMFFIObjectDeleterFlagBitMaskWeak = 1 << 1,    // 2 = 0x02
  kTVMFFIObjectDeleterFlagBitMaskBoth =
      (kTVMFFIObjectDeleterFlagBitMaskStrong |
       kTVMFFIObjectDeleterFlagBitMaskWeak),       // 3 = 0x03
} TVMFFIObjectDeleterFlagBitMask;
```

三个标志分别对应：
- **Strong (1)**：调用 C++ 析构函数，释放对象持有的资源（其他对象引用、文件句柄、设备内存等），但不释放对象内存本身。
- **Weak (2)**：释放对象的内存块（`AlignedFree`）。此时对象的 C++ 生命周期已结束。
- **Both (3)**：同时执行析构和内存释放，快速路径。

## DecRef 中的 deleter 调用

`Object::DecRef()`（`object.h:300-363`）在三种情况下调用 deleter：

### Both 快速路径

当强引用和弱引用同时归零时（递减前计数为 `BothOne = 0x100000001`）：

```cpp
if (count_before_sub == kCombinedRefCountBothOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskBoth);
  }
}
```

deleter 被调用一次，传入 `Both` 标志，同时执行析构和内存释放。这是最常见的单所有者场景。

### Strong + Weak 两阶段路径

当强引用归零但仍有弱引用时：

```cpp
else if ((count_before_sub & kCombinedRefCountMaskUInt32) ==
         kCombinedRefCountStrongOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  // 阶段1：强删除——调用析构函数
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskStrong);
  }
  // 递减隐式弱引用
  if (__atomic_fetch_sub(&(header_.combined_ref_count),
                         kCombinedRefCountWeakOne, __ATOMIC_RELEASE) ==
      kCombinedRefCountWeakOne) {
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    // 阶段2：弱删除——释放内存
    if (header_.deleter != nullptr) {
      header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskWeak);
    }
  }
}
```

deleter 可能被调用两次：第一次释放资源，第二次释放内存。如果仍有外部弱引用（来自 `WeakObjectPtr`），第二次调用延迟到最后一个弱引用释放时。

### Weak-only 路径

`DecWeakRef()`（`object.h:366-381`）在弱引用归零时仅传入 `Weak` 标志：

```cpp
void DecWeakRef() {
  if (__atomic_fetch_sub(&(header_.combined_ref_count),
                         kCombinedRefCountWeakOne, __ATOMIC_RELEASE) ==
      kCombinedRefCountWeakOne) {
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    if (header_.deleter != nullptr) {
      header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskWeak);
    }
  }
}
```

## SimpleObjAllocator 的 Deleter 实现

标准分配器 `SimpleObjAllocator` 在 `memory.h:149` 定义，其 `Handler<T>::Deleter_`（`memory.h:199-212`）是默认的 deleter 实现：

```cpp
static void Deleter_(void* objptr, int flags) {
  T* tptr = details::ObjectUnsafe::RawObjectPtrFromUnowned<T>(
      static_cast<TVMFFIObject*>(objptr));
  if (flags & kTVMFFIObjectDeleterFlagBitMaskStrong) {
    tptr->T::~T();
  }
  if (flags & kTVMFFIObjectDeleterFlagBitMaskWeak) {
    AlignedFree(static_cast<void*>(tptr));
  }
}
```

### 显式析构调用

关键细节：使用 `tptr->T::~T()` 而非 `tptr->~T()`。注释解释了原因（`memory.h:203-207`）：

> It is important to do `tptr->T::~T()`, so that we explicitly call the specific destructor instead of `tptr->~T()`, which could mean the intention to call a virtual destructor (which may not be available and is not required).

显式调用 `T` 的析构函数确保：
1. 不依赖虚析构函数（`Object` 没有虚函数）。
2. 编译器在编译期确定要调用的析构函数，无运行时分派。
3. 即使 `T` 继承自非虚析构的基类，也能正确调用完整的析构链。

### placement new 构造

对应的构造使用 placement new（`memory.h:189-191`）：

```cpp
void* data = AlignedAlloc(sizeof(T), alignof(T));
AllocGuard alloc_guard(data);
new (data) T(std::forward<Args>(args)...);
alloc_guard.Release();
```

`AlignedAlloc` 分配对齐内存，placement new 在预分配内存上构造对象。`AllocGuard` 是 RAII 守卫，确保构造函数抛异常时释放内存。这种分离分配和构造的方式是两阶段删除的前提——析构和释放必须独立可控。

### 数组对象的 Deleter

`ArrayHandler`（`memory.h:216-267`）用于内联数组对象（如 `StringObj` 附带字符数据），其 deleter 类似，但调用 `ArrayType::~ArrayType()` 并释放对齐后的完整内存块。

## TVMFFIObjectAllocHeader

### 用途

`TVMFFIObjectAllocHeader`（`c_api.h:606-623`）是位于每个对象体之前的强制头部，允许前端自定义分配器协调存储回收：

```c
typedef struct {
  void (*delete_space)(void* ptr);
} TVMFFIObjectAllocHeader;
```

### 内存布局

当使用自定义分配器时，对象内存布局为：

```
+---------------------------+
|  分配器私有元数据（可选）   |
+---------------------------+
|  TVMFFIObjectAllocHeader   |  <- delete_space 回调
+---------------------------+
|  TVMFFIObject (对象头)     |  <- self 指针指向这里
+---------------------------+
|  对象数据 (T 的成员)       |
+---------------------------+
```

### delete_space 回调

`delete_space` 回调负责回收完整的分配器拥有内存（包括私有前缀），并清理关联的前端状态（如缓存在包装对象中的 PyObject）。回调在对象的弱生命周期结束时调用：

- `ptr` 指向对象体（`TVMFFIObject`），而非前面的 `TVMFFIObjectAllocHeader`。
- 回调**不能**访问对象字段，因为 C++ 析构函数可能已经执行。
- 回调可以为 NULL，表示 deleter 直接释放存储。

### 头部恢复

C++ 层通过 `GetObjectAllocHeaderFromPtr`（`object.h:1274-1276`）从对象指针恢复分配头：

```cpp
TVM_FFI_INLINE static TVMFFIObjectAllocHeader*
GetObjectAllocHeaderFromPtr(void* ptr) {
  return reinterpret_cast<TVMFFIObjectAllocHeader*>(
      static_cast<char*>(ptr) - sizeof(TVMFFIObjectAllocHeader));
}
```

## 自定义分配器

### TVMFFICustomAllocator

`TVMFFICustomAllocator`（`c_api.h:641-672`）允许前端控制对象存储分配：

```c
typedef struct {
  void* (*allocate)(size_t size, size_t alignment, void* context);
  void* context;
} TVMFFICustomAllocator;
```

通过 `TVMFFISetCustomAllocator`（`c_api.h:675`）注册全局分配器。分配器返回的内存必须在对象体前包含初始化的 `TVMFFIObjectAllocHeader`。

### 不透明对象的 deleter

`TVMFFIObjectCreateOpaque`（`c_api.h:590-591`）接受一个简单的 deleter：

```c
TVM_FFI_DLL int TVMFFIObjectCreateOpaque(
    void* handle, int32_t type_index,
    void (*deleter)(void* handle), TVMFFIObjectHandle* out);
```

此 deleter 签名为 `void(void* handle)`，不接收 flags 参数。它在对象的强引用和弱引用都归零时调用一次，负责释放 `handle` 指向的资源。这为语言绑定（如 Python）包装外部对象提供了简化接口。

## NPU建议

在 NPU 异构计算环境中，deleter 机制需要特别关注设备资源的异步回收：

### 1. 设备内存的延迟释放

NPU 显存（如 Ascend 的 Device Memory）不能在 deleter 中立即释放，因为可能有挂起的 NPU 内核仍在访问该内存。建议：
- **Strong 阶段**：调用 `rtStreamSynchronize` 或提交一个"释放命令"到 NPU 命令流，确保所有挂起的 DMA/内核操作完成后再释放显存。
- **使用引用计数包装**：将 NPU 内存句柄包装为 FFI 对象，在 deleter 中向 NPU runtime 注册延迟释放回调，而非直接调用 `rtFree`。
- **避免在 deleter 中阻塞**：如果同步等待 NPU 完成，会阻塞 Host 线程。推荐使用 NPU runtime 的事件回调机制，在设备端操作完成时异步触发内存释放。

### 2. 两阶段删除与 NPU 资源

- **Strong deleter**：释放 NPU 相关资源（如 kernel 句柄、stream、event），但保留对象的 Host 端元数据（如 shape、dtype），使弱引用仍可查询这些信息用于调试。
- **Weak deleter**：释放 Host 端内存。这确保了即使 NPU 资源已释放，调试工具仍可通过弱引用检查对象的最终状态。
- **注意顺序**：必须先释放 NPU 资源（Strong），再释放 Host 内存（Weak），因为 Strong 阶段可能需要访问 Host 端元数据来确定要释放哪些 NPU 资源。

### 3. 自定义分配器与 NPU 内存池

对于高频创建/销毁的 NPU 张量对象：
- 实现自定义 `TVMFFICustomAllocator`，从 NPU 内存池分配而非每次调用 `rtMalloc`/`rtFree`。
- 在 `TVMFFIObjectAllocHeader.delete_space` 中将内存归还池而非真正释放，减少 NPU 内存分配开销。
- 池化分配器的 deleter 仍需调用 C++ 析构函数（释放非池化资源），但 `delete_space` 回调执行池化回收。
- 确保池的线程安全性——NPU 推理可能从多个 Host 线程提交任务。

### 4. deleter 中的异常安全

NPU runtime API 可能返回错误码。deleter 是 `noexcept` 的 C 函数指针，不能抛出 C++ 异常：
- 在 deleter 内部捕获所有错误，记录日志但不抛出。
- 对于 NPU 资源泄漏（如 `rtFree` 失败），使用全局错误处理器或泄漏检测器，而非尝试在 deleter 中恢复。
- 考虑使用"僵尸对象"模式：释放失败的对象标记为僵尸，记录到泄漏列表，下次 GC 周期重试。

### 5. 跨 PE 的 deleter 执行

在多 NPU PE 环境中：
- deleter 应在创建对象的 PE 上执行，因为 NPU 资源通常与 PE 绑定。
- 如果最后一个引用在另一个 PE 上释放，通过消息将删除请求转发给归属 PE。
- 可以使用"归属 PE"标记（存储在对象的分配器私有元数据中），在 deleter 中检查当前 PE 是否为归属 PE，若不是则转发。

### 6. 实时性与后台删除

NPU 推理有严格延迟要求，deleter 的执行时间不确定（特别是涉及 NPU 同步时）：
- 将 deleter 操作卸载到后台回收线程。
- 在 Strong 阶段仅标记对象为"待回收"，将实际的 NPU 资源释放加入后台队列。
- 引用计数归零的快速路径仅执行原子操作和标志设置，不调用重量级 deleter。
- 但需注意：弱引用必须在内存实际释放后轮转失效，后台删除期间 `TryPromoteWeakPtr` 仍可成功提升（因为强引用计数虽归零但对象未被析构）。这需要在快速路径和后台回收之间仔细设计状态机。

## 设计分析

Deleter 机制体现了多个设计决策：

1. **函数指针 vs 虚函数**：使用函数指针而非虚析构函数，节省了每个对象的 vptr（8字节），且不依赖 C++ RTTI。删除器在创建时绑定，类型安全由模板保证。
2. **两阶段销毁**：Strong/Weak 分离支持弱引用在对象析构后安全检测过期状态，是 `WeakObjectPtr` 正确性的基础。
3. **显式析构调用**：`tptr->T::~T()` 语法精确控制析构目标，避免虚分派，编译器可内联析构调用。
4. **分配器抽象**：`TVMFFIObjectAllocHeader` 和 `TVMFFICustomAllocator` 提供了灵活的存储管理扩展点，支持对象池、垃圾回收、语言运行时集成等场景。
5. **C ABI 兼容**：deleter 是纯 C 函数指针，可从任意 FFI 语言设置和调用。
6. **空指针安全**：所有 deleter 调用前检查 `!= nullptr`，允许对象没有 deleter（如栈嵌入对象或特殊管理对象）。

## 相关概念

- [027 TVMFFIObject 对象头](027-object-header.md)：deleter 字段的存储位置
- [028 组合引用计数](028-combined-refcount.md)：DecRef 触发 deleter 的逻辑
- [032 不透明对象](032-opaque-object.md)：TVMFFIObjectCreateOpaque 的简化 deleter
- [033 Python 不透明对象](033-python-opaque-object.md)：OpaquePyObject 的资源管理
