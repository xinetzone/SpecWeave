---
type: Concept
title: "视角004：值语义与引用语义"
description: "分析 TVM FFI 中值语义与引用语义的并存设计：AnyView 的非持有引用、Any 的持有值语义、ObjectPtr 的共享引用语义，以及容器的写时复制（COW）机制。"
tags:
  - architecture
  - semantics
  - value-semantics
  - reference-semantics
  - cow
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-075, F-085, F-086, F-111, F-124, F-160, F-172
  - code:
    - include/tvm/ffi/any.h
    - include/tvm/ffi/object.h
    - include/tvm/ffi/container/array.h
    - include/tvm/ffi/container/map.h
---

# 视角004：值语义与引用语义

## 概述

TVM FFI 在类型系统中同时支持值语义和引用语义，通过不同类型明确区分。POD 类型在 `TVMFFIAny` 中按值存储；对象类型通过引用计数指针共享；`AnyView` 提供非持有引用视图；`Any` 提供持有值容器；容器类型通过写时复制（COW）在值语义外观下实现高效共享。

## 值语义类型

### POD 类型的内联值存储

在 `TVMFFIAny` 联合体中，POD 类型直接存储值本身：

- 整数 `kTVMFFIInt = 1` 存储在 `v_int64` 字段
- 浮点数 `kTVMFFIFloat = 3` 存储在 `v_float64` 字段
- 布尔值 `kTVMFFIBool = 2` 存储在 `v_int64` 字段
- DataType `kTVMFFIDataType = 5` 存储在 `v_dtype` 字段
- Device `kTVMFFIDevice = 6` 存储在 `v_device` 字段

这些类型的赋值、传参和返回均执行位拷贝，无额外开销。

### Any 的持有值语义

`Any`（`any.h:233`）对外表现为值语义：拷贝 `Any` 创建逻辑独立副本（POD 位拷贝，对象增加引用计数）；移动 `Any` 转移所有权；析构自动释放资源。

## 引用语义类型

### ObjectPtr：共享引用指针

`ObjectPtr<T>`（`object.h:401`）管理 `T* data_`，语义类似 `std::shared_ptr<T>`：

- 拷贝构造调用 `IncRef()` 增加引用计数
- 析构调用 `DecRef()`，归零时释放对象
- `operator->()` 允许直接修改共享对象
- `use_count()` 返回强引用计数，`unique()` 检查是否为唯一所有者

### ObjectRef：对象引用基类

`ObjectRef`（`object.h:791`）持有 `ObjectPtr<Object> data_`，是 `Function`、`Array<T>`、`Map<K,V>`、`Tensor` 等的基类。提供 `defined()`、`same_as()`、`use_count()` 等方法。

### WeakObjectPtr：弱引用

弱引用不增加强引用计数，通过 `lock()` 尝试获取 `ObjectPtr<T>`，适用于缓存和观察者场景。

## 非持有引用：AnyView

`AnyView`（`any.h:48`）不管理生命周期，内部持有 `TVMFFIAny data_` 的 16 字节位拷贝，对对象类型不增加引用计数。适用于函数参数传递：`PackedArgs`（`function.h:261`）使用 `const AnyView*` 避免调用时的引用计数开销。

安全性依赖使用约定：`AnyView` 不得逃逸出引用值的生命周期。

## 写时复制（COW）容器

### Array 的 COW 机制

`Array<T>` 继承自 `ObjectRef`，对外为不可变数组：

- `operator[]` 返回元素拷贝，不修改底层数组
- `push_back` 触发 COW：若 `use_count() > 1`，先复制 `ArrayNode` 再追加

COW 基于 `Object::unique()` 检查，单所有者时直接修改，共享时复制后修改。

### Map 的 COW 机制

`Map<K,V>` 同样采用 COW，`Set()` 方法在写入前检查引用计数。底层 `MapNode` 使用开放寻址哈希表。

### 可变容器 List 和 Dict

与 `Array`/`Map` 不同，`List` 和 `Dict` 支持原地修改，所有引用共享变更，不采用 COW。

## 语义选择矩阵

| 类型 | 语义 | 生命周期管理 | 典型场景 |
|------|------|-------------|---------|
| `AnyView` | 非持有引用 | 不管理 | 函数参数、临时视图 |
| `Any` | 持有值 | RAII 自动 | 返回值、变量存储 |
| `ObjectPtr<T>` | 共享引用 | 引用计数 | 对象内部持有、可变访问 |
| `ObjectRef` 子类 | 共享引用 | 引用计数 | 公共 API 对象传递 |
| `Array<T>`/`Map<K,V>` | 值语义（COW） | 引用计数+COW | 不可变集合 |
| `List`/`Dict` | 引用语义（可变） | 引用计数 | 原地修改 |
| `WeakObjectPtr<T>` | 弱引用 | 不影响生命周期 | 缓存、观察者 |

## 设计分析

TVM FFI 遵循"显式优于隐式"原则：每种语义对应明确类型。`AnyView` 与 `Any` 的分离避免意外的生命周期延长；`Array`/`Map` 与 `List`/`Dict` 的分离使可变性成为类型级别保证。COW 机制在值语义外观与性能间取得折中，在编译器 IR 等大量传递不可变数据的场景中显著减少深拷贝。

## 相关概念

- [003 类型擦除模式](003-type-erasure-pattern.md)
- [013 内存所有权模型](013-memory-ownership-model.md)
- [018 Any 拥有语义](/02-core-types/concepts/018-any-owning.md)
- [028 组合引用计数](/02-core-types/concepts/028-combined-refcount.md)
