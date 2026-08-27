---
type: Concept
title: "视角109：友元类模式"
description: "解析 TVM FFI 中 friend class/struct 的系统性使用：Node 与 Ref 的友元关系（ArrayNode/Array、MapNode/Map、ListNode/List）、Unsafe 访问器模式（AnyUnsafe、ObjectUnsafe、ExpectedUnsafe）、TypeTraits 特化的友元声明，以及封装与性能的平衡。"
tags:
  - cpp-impl
  - friend
  - encapsulation
  - access-control
  - node-ref-pattern
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-153, F-158, F-166, F-168, F-173
  - code:
    - include/tvm/ffi/any.h
    - include/tvm/ffi/object.h
    - include/tvm/ffi/container/array.h
    - include/tvm/ffi/container/list.h
    - include/tvm/ffi/container/map.h
    - include/tvm/ffi/container/dict.h
    - include/tvm/ffi/container/map_base.h
    - include/tvm/ffi/expected.h
---

# 视角109：友元类模式

## 概述

TVM FFI 在 C++ 封装设计中系统性地使用 `friend` 声明，在保持数据成员私有性的同时，允许特定的协作类高效访问内部状态。友元关系主要出现在三种场景：**Node-Ref 双层模式**中容器节点与引用句柄的互访、**Unsafe 访问器**对类型擦除内部的受控暴露、以及 **TypeTraits 特化**对存储细节的访问。这种设计在封装性和性能之间取得了精确平衡——内部数据不对外公开，但经过仔细选择的协作类可以绕过访问控制直接操作，避免了公共 getter/setter 的开销和语义泄漏。

## Node-Ref 友元模式

TVM FFI 的容器系统采用 Node-Ref 双层架构：Node（如 `ArrayNode`、`MapNode`）是继承自 `Object` 的内部实现节点，管理实际数据存储；Ref（如 `Array<T>`、`Map<K,V>`）是继承自 `ObjectRef` 的用户侧句柄，提供类型安全的 API。两者通过友元关系建立信任通道。

### ArrayNode 与 Array

`array.h:156-162` 中 `ArrayNode` 声明了多个友元：

```cpp
friend class Array;
friend class Tuple;
friend struct TypeTraits;
```

`Array` 作为用户侧数组类，需要直接访问 `ArrayNode` 的内联存储、`size_`、`capacity_` 等私有成员来实现 `push_back`、`operator[]`、COW（写时复制）等操作。`Tuple` 复用 `ArrayNode` 作为底层存储。`TypeTraits<Array<T>>` 特化需要访问内部布局以实现 `CopyToAnyView`。

对应的，`Array<T>` 在 `array.h:852` 声明 `friend class Array;`（用于不同模板参数间的协变访问），其内部的 `CopyOnWrite` 逻辑直接操作 `ArrayNode` 数据。

### ListNode 与 List

`list.h:120-123`：

```cpp
friend class List;
friend struct TypeTraits;
```

模式与 Array 相同，`List` 直接访问 `ListNode` 的存储和大小信息。

### MapNode 与 Map

`map.h:59` 声明 `friend class Map;`，`map.h:338` 和 `map.h:349` 在内部迭代器和 Map 类中也有友元声明。`Map<K,V>` 需要直接访问 `MapNode` 的开放寻址哈希表桶数组、`Find` 和 `Set` 等底层操作。

### DictNode 与 Dict

`dict.h:61` 声明 `friend class Dict;`，`dict.h:332` 和 `dict.h:350` 在迭代器和 Dict 类中也有声明。`Dict` 是键值均为 `Any` 的特殊 Map，复用 `MapNode`/`MapBaseObj` 基础设施。

### MapBase 层次

`map_base.h` 中的友元关系更为复杂：

- `DenseMapBaseObj`（`map_base.h:189-190`）声明 `friend class DenseMapBaseObj;` 和 `friend class SmallMapBaseObj;`
- `SmallMapBaseObj`（`map_base.h:267-274`）声明 `friend class SmallMapBaseObj;`、`friend class DenseMapBaseObj;`、`friend class Dict;`、`friend struct TypeTraits;`
- `MapBaseObj`（`map_base.h:1082-1083`）声明友元给 `SmallMapBaseObj` 和 `DenseMapBaseObj`
- `SmallMapBaseObj` 的迭代器（`map_base.h:1402-1403`）声明友元给 `MapBaseObj` 和 `DenseMapBaseObj`

这种密集的友元网络使得小映射优化（SmallMap，内联存储少量元素）和稠密映射（DenseMap，堆分配桶数组）之间可以互相访问内部状态，实现平滑的容量升级转换，同时对用户隐藏所有存储细节。

## Unsafe 访问器友元

第二类友元是 `*Unsafe` 结构体，它们作为受控的"逃生舱"，允许 FFI 内部基础设施绕过类型安全检查直接操作底层数据。

### AnyUnsafe

`any.h:532-534` 中 `Any` 类声明：

```cpp
friend struct details::AnyUnsafe;
friend struct AnyHash;
friend struct AnyEqual;
```

`AnyUnsafe` 提供 `MoveTVMFFIAnyToAny`、`MoveFromAnyAfterCheck`、`ObjectPtrFromAnyAfterCheck`、`TVMFFIAnyPtrFromAny` 等静态方法。这些方法直接访问 `Any` 的 `data_` 成员，在类型检查已通过的前提下执行零开销的值提取。`AnyHash` 和 `AnyEqual` 作为哈希和相等比较的自定义函数对象，也需要访问内部数据。

`AnyView` 在 `any.h:53` 声明 `friend class Any;`，允许持有型 `Any` 直接构造非持有视图。

### ObjectUnsafe

`ObjectUnsafe`（`object.h:1365-1397`）虽然不通过友元声明访问（因为它操作的是 `Object` 的 protected 成员和 C ABI 句柄），但它是 Unsafe 模式的典型代表，提供 `IncRefObjectHandle`、`DecRefObjectHandle`、`RawObjectPtrFromObjectRef`、`TVMFFIObjectPtrFromObjectRef`、`MoveObjectPtrToTVMFFIObjectPtr` 等底层操作。

### ExpectedUnsafe

`expected.h:204` 和 `expected.h:281` 中 `Expected<T>` 声明 `friend struct details::ExpectedUnsafe;`。`ExpectedUnsafe`（`expected.h:294` 起）提供 `MoveFromTVMFFIAny` 和 `MoveToTVMFFIAny` 方法，允许 FFI 内部将原始 `TVMFFIAny` 直接移入/移出 `Expected` 存储，跳过成功/错误状态检查。

### FunctionNode 与 Function

`function.h:140` 中 `FunctionNode` 声明 `friend class Function;`，允许 `Function` 引用类直接访问函数节点的 `safe_call` 指针等内部状态。

## TypeTraits 友元

多个容器和值类型声明 `friend struct TypeTraits;`，允许 `TypeTraits<T>` 特化访问私有成员来实现 `CopyToAnyView`/`MoveToAny`/`CopyFromAnyViewAfterCheck` 等序列化方法。这包括：

- `ArrayNode`（`array.h:162`）
- `ListNode`（`list.h:123`）
- `SmallMapBaseObj`（`map_base.h:274`）

TypeTraits 特化是 FFI 类型系统的"序列化网关"，需要访问内部布局才能高效地将对象移入/移出 `TVMFFIAny` 联合体。

## 友元与封装的平衡

TVM FFI 的友元使用遵循以下原则：

1. **最小化友元集**：每个类只将确实需要访问内部的协作类声明为友元，而非公开所有私有成员。
2. **友元不继承**：C++ 友元关系不传递、不继承。`ArrayNode` 友元 `Array` 不意味着 `Array` 的子类也自动获得访问权。
3. **details 命名空间隔离**：Unsafe 访问器全部位于 `details` 命名空间，明确标记为内部实现，用户不应直接使用。
4. **性能优先于教条封装**：在引用计数、类型转换等热路径上，直接访问私有数据比通过虚函数或虚 getter 更高效。友元提供了受控的性能逃逸通道。
5. **Node-Ref 分层清晰**：Node 是内部实现，Ref 是公开接口，友元关系是两层之间的桥梁而非对所有人开放。

## 设计分析

友元类模式是 TVM FFI 实现"零开销封装"的关键手段。在传统的面向对象设计中，私有数据通过公共 getter/setter 访问，但在 FFI 的高频操作场景中，即使是非虚函数的 getter 也可能阻止某些编译器优化（如常量传播、死代码消除）。通过友元，`Array<T>::push_back` 可以直接修改 `ArrayNode` 的 `size_` 和内联存储，编译后与直接操作 C 结构体无异。同时，友元关系是显式且有限的——编译器强制检查只有被声明的类才能访问私有成员，比将数据设为 public 安全得多。Unsafe 访问器模式则进一步将危险操作集中在命名明确的类中，便于代码审计。这种设计体现了"信任边界明确、性能关键路径特权访问"的工程实用主义。

## 相关概念

- [051 Array 容器](/04-containers/concepts/051-array-container.md)：Node-Ref 模式的具体实现
- [053 SeqBase 基类](/04-containers/concepts/053-seq-base.md)：序列容器的共享基类
- [013 内存所有权模型](/01-architecture/concepts/013-memory-ownership-model.md)：Node-Ref 与引用计数
- [110 Unsafe 操作](110-unsafe-operations.md)：Unsafe 访问器的详细语义
