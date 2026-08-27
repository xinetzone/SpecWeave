---
type: Concept
title: "视角112：Arena 分配器"
description: "解析 tvm::support::GenericArena 竞技场分配器：ArenaPageHeader 页链表、SimplePageAllocator 16KB 页分配、UpperAlign 对齐分配、FreeAll/RecycleAll 批量释放、placement new 构造，以及裸金属可移植性设计。"
tags:
  - cpp-impl
  - arena
  - memory-allocator
  - performance
  - bare-metal
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-298, F-299
  - code:
    - tvm/src/support/arena.h
    - src/ffi/custom_allocator.cc
---

# 视角112：Arena 分配器

## 概述

`tv::support::GenericArena`（定义于 `tvm/src/support/arena.h:72`）是一个竞技场（bump/arena）分配器，通过从连续内存页中顺序递增分配来避免逐对象的 `malloc`/`free` 开销。所有已分配对象在 Arena 销毁时一次性释放（或通过 `RecycleAll` 回收页以供重用）。该分配器采用模板策略模式，页分配策略由 `PageAllocator` 模板参数抽象，默认使用基于 `new`/`delete` 的 `SimplePageAllocator`。Arena 的核心部分被设计为可移植到裸金属嵌入式设备，不依赖 `operator new` 或 `malloc`。

## 整体架构

GenericArena 的架构由三个核心组件构成：

1. **ArenaPageHeader**（`arena.h:56-65`）：每页的头部，包含 `next` 指针（指向下一页）、`size`（页总大小）和 `offset`（当前分配偏移量）。
2. **GenericArena<PageAllocator>**（`arena.h:72`）：Arena 主体，维护三个链表指针：`head_`（当前活跃页）、`tail_`（活跃页链尾）、`free_list_`（已回收的空闲页链）。
3. **PageAllocator**（策略参数）：负责实际的页级内存分配与释放。默认 `SimplePageAllocator` 使用 `new`/`delete`。

## SimplePageAllocator 页分配器

`SimplePageAllocator`（`arena.h:188-216`）定义了默认的页分配策略：

```cpp
class SimplePageAllocator {
 public:
  ArenaPageHeader* allocate(size_t min_size) {
    size_t npages = ((min_size + kPageSize - 1) / kPageSize);
    ArenaPageHeader* header = reinterpret_cast<ArenaPageHeader*>(new Page[npages]);
    header->size = npages * kPageSize;
    header->offset = sizeof(ArenaPageHeader);
    return header;
  }
  void deallocate(ArenaPageHeader* page) {
    delete[] reinterpret_cast<Page*>(page);
  }
  static const constexpr int kPageSize = 16 << 10;      // 16 KB
  static const constexpr int kPageAlign = 1024;
 private:
  using Page = std::aligned_storage<kPageSize, kPageAlign>::type;
};
```

关键设计点：

- **默认页大小 16 KB**（`arena.h:209`）：在分配粒度和内存浪费之间取得平衡。
- **页对齐 1024 字节**（`arena.h:210`）：满足大多数对象的对齐需求。
- **按需多页分配**：当单次分配请求超过一页时，分配足够的连续页数。
- **aligned_storage**：使用 `std::aligned_storage<16KB, 1024>` 确保页内存在正确对齐的存储中。

类型别名 `using Arena = GenericArena<SimplePageAllocator>;`（`arena.h:218`）提供了默认 Arena 的便捷名称。

## 分配流程

### allocate_：对齐分配

`allocate_<T>(count)` 方法（`arena.h:106-110`）分配类型 `T` 的数组：

```cpp
template <typename T>
T* allocate_(int count = 1) {
  static_assert(PageAllocator::kPageAlign % alignof(T) == 0, "Too large alignment");
  return static_cast<T*>(Alloc(sizeof(T) * count, alignof(T)));
}
```

`static_assert` 确保页对齐度满足类型 `T` 的对齐要求。这是一个编译期检查，防止在对齐不足的页中分配过度对齐的类型。

### Alloc：核心分配逻辑

私有方法 `Alloc(size, align)`（`arena.h:151-170`）实现核心的 bump 分配：

1. 计算对齐后的偏移：`offset = UpperAlign(head_->offset, align)`
2. 检查当前页剩余空间是否足够：`if (offset + size <= head_->size)`
3. 如果足够，递增 `head_->offset` 并返回指针
4. 如果不足，尝试从 `free_list_` 获取空闲页
5. 如果空闲页也不够，通过 `alloc_.allocate(offset + size)` 分配新页
6. 将新页插入页链表头部

```cpp
void* Alloc(size_t size, size_t align) {
  size_t offset = UpperAlign(head_->offset, align);
  if (offset + size <= head_->size) {
    head_->offset = offset + size;
    return reinterpret_cast<char*>(head_) + offset;
  } else {
    ArenaPageHeader* new_head;
    offset = UpperAlign(sizeof(ArenaPageHeader), align);
    if (free_list_ != nullptr && offset + size <= free_list_->size) {
      new_head = free_list_;
      free_list_ = free_list_->next;
    } else {
      new_head = alloc_.allocate(offset + size);
    }
    new_head->next = head_;
    new_head->offset = offset + size;
    head_ = new_head;
    return reinterpret_cast<char*>(head_) + offset;
  }
}
```

### UpperAlign：上界对齐

`UpperAlign(offset, align)`（`arena.h:143-145`）将偏移量向上对齐到指定边界：

```cpp
size_t UpperAlign(size_t offset, size_t align) {
  return offset + (align - (offset % align)) % align;
}
```

这是标准的上界对齐公式，确保返回的地址满足 `align` 对齐要求。

### make：对象构造

`make<T>(Args&&... args)`（`arena.h:122-127`）在 Arena 上构造对象：

```cpp
template <typename T, typename... Args>
T* make(Args&&... args) {
  T* ptr = allocate_<T>();
  new (ptr) T(forward<Args>(args)...);
  return ptr;
}
```

使用 placement new 在已分配的内存上调用构造函数。Arena 提供了自定义的 `forward` 辅助函数（`arena.h:47-50`）而非直接使用 `std::forward`，以保持裸金属可移植性。

**重要约束**：源码注释指出（`arena.h:118-120`）："The type T must be simple type, or only contain memory allocated from the same arena. Otherwise the destructor needs to be called explicitly." Arena 不自动调用析构函数——如果类型持有需要释放的外部资源（如堆内存、文件句柄），用户必须手动调用析构函数。

## 释放与回收

### FreeAll：全部释放

`FreeAll()`（`arena.h:85-88`）遍历活跃页链表和空闲页链表，逐页调用 `alloc_.deallocate`：

```cpp
void FreeAll() {
  FreePageList(&head_);
  FreePageList(&free_list_);
}
```

析构函数（`arena.h:81`）在 `TVM_ARENA_HAS_DESTRUCTOR` 启用时自动调用 `FreeAll`。

### RecycleAll：页回收

`RecycleAll()`（`arena.h:90-99`）将所有活跃页移到空闲链表，重置首页的偏移量以供重用：

```cpp
void RecycleAll() {
  tail_->next = free_list_;
  free_list_ = head_->next;
  head_->next = nullptr;
  head_->offset = sizeof(ArenaPageHeader);
  tail_ = head_;
}
```

与 `FreeAll` 不同，`RecycleAll` 不将内存还给系统，而是保留页以供后续分配使用。这适用于需要反复分配和清空大量短期对象的场景（如编译器 pass 中的临时节点），避免反复向操作系统申请/释放内存。

### FreePageList：链表释放

`FreePageList(ArenaPageHeader** ptr)`（`arena.h:175-182`）遍历页链表并逐页释放：

```cpp
void FreePageList(ArenaPageHeader** ptr) {
  while (ptr[0] != nullptr) {
    ArenaPageHeader* temp = ptr[0];
    ptr[0] = ptr[0]->next;
    alloc_.deallocate(temp);
  }
}
```

## LinkedList 辅助结构

arena.h 还提供了 `LinkNode<T>`（`arena.h:225-230`）和 `LinkedList<T>`（`arena.h:237-256`），是可与 Arena 配合使用的简单侵入式链表：

```cpp
template <typename T>
struct LinkNode {
  T value;
  LinkNode<T>* next{nullptr};
};

template <typename T>
struct LinkedList {
  LinkNode<T>* head{nullptr};
  LinkNode<T>* tail{nullptr};
  void Push(LinkNode<T>* node) { ... }
};
```

这些结构的节点可以通过 `arena->make<LinkNode<T>>()` 在 Arena 上分配，实现零额外分配开销的链表。

## 裸金属可移植性

文件注释（`arena.h:26-28`）明确说明了可移植性设计：

> "The GenericArena/ArenaPageHeader portion of this file is portable to bare-metal embedded devices. Don't use operator new (without placement parameters) or malloc in that section. The SimplePageAllocator below uses operator new / delete and is NOT bare-metal portable."

`GenericArena` 模板本身只使用 placement new 和 `PageAllocator` 接口，不直接调用 `new`/`malloc`。用户可以为裸金属环境提供自定义的 `PageAllocator`（例如从静态内存池中分配页），而 Arena 的核心逻辑完全不变。`TVM_ARENA_HAS_DESTRUCTOR` 宏（`arena.h:33-35`，默认为1）允许在不支持析构函数的环境中禁用析构函数。

## NPU建议

在 NPU 环境中使用 Arena 分配器时，建议考虑以下事项：

1. **设备端页分配器**：为 NPU 实现自定义 `PageAllocator`，从设备内存池（如 NPU 的 SRAM 或 HBM）中分配页。Arena 的模板设计使得替换页分配器无需修改核心分配逻辑。建议页大小根据 NPU 的内存管理单元（MMU）页大小设置，通常为 4KB 或 64KB。

2. **对齐与 NPU 向量访问**：NPU 的向量加载/存储指令通常要求严格的数据对齐（如 64 字节或 128 字节缓存行对齐）。建议将 `kPageAlign` 设置为 NPU 的最大向量对齐要求，并在 `allocate_<T>` 的 `static_assert` 中验证。对于张量数据等特殊需求，可以提供显式对齐参数的分配方法。

3. **主机-设备共享内存**：如果 Arena 分配的内存需要主机和 NPU 共同访问，应使用统一内存（unified memory）或已映射的共享内存。自定义 PageAllocator 应调用相应的驱动 API（如 `cuMemAllocManaged` 或 NPU SDK 的共享内存分配接口）。

4. **析构函数与设备资源**：NPU 上的对象可能持有设备端资源（如算子句柄、命令缓冲区）。由于 Arena 不自动调用析构函数，建议在 `FreeAll`/`RecycleAll` 之前手动遍历并销毁持有设备资源的对象，或使用 `LinkedList` 维护需要析构的对象列表。

5. **RecycleAll 与 NPU 内存复用**：在 NPU 推理场景中，多次推理请求可以复用同一块 Arena 内存。`RecycleAll()` 比 `FreeAll()` 更适合——它保留已分配的页，避免反复向 NPU 驱动申请设备内存，显著降低延迟。建议在推理引擎的请求级别使用 Arena，每个请求结束时 `RecycleAll()`。

6. **多 NPU 核的 Arena 隔离**：如果多个 NPU 核并发执行，建议为每个核分配独立的 Arena 实例。GenericArena 本身不是线程安全的（bump 指针的更新没有原子保护），每个核一个 Arena 可以避免锁竞争。如果需要多核共享，应在外层加锁或使用线程本地 Arena。

7. **内存池预分配**：在 NPU 初始化阶段，可以通过自定义 PageAllocator 预分配足够的物理页并建立空闲页池。运行时 Arena 分配将从池中取页，避免在推理关键路径中触发驱动级内存分配。

## 设计分析

Arena 分配器的设计目标是消除频繁小对象分配的开销。通过 bump 指针分配，每次分配只需一次指针加法和比较，比 `malloc` 快数十倍；批量释放只需遍历页链表，比逐对象 `free` 快数个数量级。模板策略模式使得核心分配逻辑与底层页管理解耦，兼顾了默认场景的便利性（SimplePageAllocator）和特殊场景的灵活性（自定义 PageAllocator）。裸金属可移植性设计使得 Arena 可用于 TVM 在嵌入式和边缘设备上的部署。`RecycleAll` 的页复用机制特别适合编译器和推理引擎中的阶段性内存分配模式。需要注意的是，Arena 不适合管理生命周期差异大的对象——如果少数对象长期存活而大多数短期对象需要回收，Arena 无法单独释放它们，可能导致内存浪费。这种情况下应考虑结合引用计数或分代 Arena。

## 相关概念

- [111 原子内存序](111-atomic-memory-ordering.md)：Arena 非线程安全，多线程需配合原子或锁
- [114 RingBuffer 环形缓冲](114-ring-buffer.md)：IO 缓冲的另一种内存管理策略
- [013 内存所有权模型](/01-architecture/concepts/013-memory-ownership-model.md)：Arena 与引用计数的互补关系
- [018 Any 持有型](/02-core-types/concepts/018-any-owning.md)：Any 对象的引用计数管理
