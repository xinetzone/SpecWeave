---
type: Concept
title: "视角133：tvm-ffi 安全包装"
description: "分析 tvm-ffi crate 的安全 API 层设计，包括 Object/ObjectArc 智能指针、Function 包装、Error 类型、集合类型及 derive 宏。"
tags:
  - rust
  - safety
  - smart-pointer
  - object-model
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-311, F-312, F-313, F-314, F-315, F-316, F-321, F-322, F-323, F-324, F-325, F-326, F-327, F-328
  - code:
    - rust/tvm-ffi/src/object.rs
    - rust/tvm-ffi/src/function.rs
    - rust/tvm-ffi/src/error.rs
    - rust/tvm-ffi/src/collections/tensor.rs
    - rust/tvm-ffi/src/collections/array.rs
    - rust/tvm-ffi/src/collections/map.rs
    - rust/tvm-ffi/src/string.rs
---

# 视角133：tvm-ffi 安全包装

## 概述

`tvm-ffi` crate 在 `tvm-ffi-sys` 原始绑定之上构建了完整的安全 API 层。通过 Rust 类型系统、智能指针和 derive 宏，将 C++ 风格的裸指针管理转化为内存安全的 Rust API。核心组件包括 `Object`/`ObjectArc` 对象系统、`Function` 调用包装、`Error` 错误类型、集合类型（Tensor/Array/Map/Shape/String/Bytes）等。

## Object 与 ObjectArc 对象系统

### Object 结构体

`object.rs:30-33`：

```rust
#[repr(C)]
pub struct Object {
    header: TVMFFIObject,
}
```

`Object` 是最基本的对象基类，直接包含 `TVMFFIObject` 头。所有 TVM FFI 对象都继承自 `Object`。

### ObjectCore trait

`object.rs:51-77` 定义了对象系统的核心 trait：

```rust
pub unsafe trait ObjectCore: Sized + 'static {
    const TYPE_KEY: &'static str;
    const TYPE_DEPTH: i32;
    const TYPE_FINAL: bool = false;
    fn type_index() -> i32;
    unsafe fn object_header_mut(this: &mut Self) -> &mut TVMFFIObject;
}
```

`ObjectCore` 是 unsafe trait，因为实现者需要保证 type_index 与运行时类型表一致。

### ObjectCoreWithExtraItems trait

`object.rs:82-103` 支持对象后附带额外数据（如数组数据、字符串内容）：

```rust
pub unsafe trait ObjectCoreWithExtraItems: ObjectCore {
    type ExtraItem;
    fn extra_items_count(this: &Self) -> usize;
    unsafe fn extra_items(this: &Self) -> &[Self::ExtraItem];
    unsafe fn extra_items_mut(this: &mut Self) -> &mut [Self::ExtraItem];
}
```

### ObjectArc<T> 智能指针

`object.rs:39-42` 是引用计数的核心抽象：

```rust
#[repr(C)]
pub struct ObjectArc<T: ObjectCore> {
    ptr: std::ptr::NonNull<T>,
    _phantom: std::marker::PhantomData<T>,
}
```

`ObjectArc` 等价于 C++ 的 `ObjectPtr<T>`，通过 `combined_ref_count` 管理生命周期：

- **Clone**（`object.rs:571-580`）：调用 `inc_ref` 递增强引用
- **Drop**（`object.rs:564-568`）：调用 `dec_ref` 递减弱引用
- **Deref/DerefMut**：透明访问底层对象

`ObjectArc::new()` 使用 Rust 全局分配器（`alloc::alloc`）分配对象，并通过 `ptr::write` 直接写入对象头和引用计数（`object.rs:396-421`）。

### ObjectRefCore trait

`object.rs:124-129`：

```rust
pub unsafe trait ObjectRefCore: Sized + Clone {
    type ContainerType: ObjectCore;
    fn data(this: &Self) -> &ObjectArc<Self::ContainerType>;
    fn into_data(this: Self) -> ObjectArc<Self::ContainerType>;
    fn from_data(data: ObjectArc<Self::ContainerType>) -> Self;
}
```

`ObjectRef`（`object.rs:224-227`）是所有用户可见对象包装的基类，通过 `#[derive(ObjectRef)]` 自动实现 `ObjectRefCore`。

## Function 包装

`function.rs:36-45`：

```rust
#[repr(C)]
#[derive(Object)]
#[type_key = "ffi.Function"]
#[type_index(TVMFFITypeIndex::kTVMFFIFunction)]
pub struct FunctionObj {
    object: Object,
    cell: TVMFFIFunctionCell,
}

#[derive(Clone, ObjectRef)]
pub struct Function {
    data: ObjectArc<FunctionObj>,
}
```

`Function` 通过 `CallbackFunctionObjImpl<F>`（`function.rs:56-96`）包装 Rust 闭包：

```rust
struct CallbackFunctionObjImpl<F: Fn(&[AnyView]) -> Result<Any> + 'static> {
    function: FunctionObj,
    callback: F,
}
```

关键 API（F-313~F-316）：

| API | 说明 |
|-----|------|
| `Function::get_global(name)` | 调用 `TVMFFIFunctionGetGlobal` 获取全局函数 |
| `Function::register_global(name, func)` | 调用 `TVMFFIFunctionSetGlobal` 注册全局函数 |
| `Function::from_packed(callback)` | 从 Rust 闭包创建 Function |
| `Function::from_typed(method_name)` | 从类型方法创建 Function |
| `Function::call_packed(args)` | 调用函数，返回 `Result<Any>` |

## Error 包装

`error.rs:52-65`：

```rust
#[repr(C)]
#[derive(Object)]
#[type_key = "ffi.Error"]
#[type_index(TVMFFITypeIndex::kTVMFFIError)]
pub struct ErrorObj {
    object: Object,
    cell: TVMFFIErrorCell,
}

#[derive(Clone, ObjectRef)]
pub struct Error {
    data: ObjectArc<ErrorObj>,
}
```

错误类型包含六种预定义 kind（F-317）：`VALUE_ERROR`、`TYPE_ERROR`、`RUNTIME_ERROR`、`ATTRIBUTE_ERROR`、`KEY_ERROR`、`INDEX_ERROR`。

核心 API：

| API | 说明 |
|-----|------|
| `Error::new(kind, message, traceback)` | 直接创建错误对象，调用 `TVMFFIErrorCreate` |
| `Error::from_raised()` | 从 TLS 中的 raised error 移动构造，调用 `TVMFFIErrorMoveFromRaised` |
| `Error::set_raised(&self)` | 将错误设置为当前 raised error，调用 `TVMFFIErrorSetRaised` |
| `Error::with_appended_backtrace(this, bt)` | 追加回溯，单引用时原地 mutate，多引用时创建新 Error |

## 集合类型

### Tensor（F-321）

`collections/tensor.rs:30`：

```rust
pub struct TensorObj {
    object: Object,
    dltensor: DLTensor,
}
pub struct Tensor {
    data: ObjectArc<TensorObj>,
}
```

提供 `shape()`、`dtype()`、`device()`、`data()` 方法，支持 DLPack 互转（`TVMFFITensorFromDLPack`/`TVMFFITensorToDLPack`）。

### Array<T>（F-322）

`collections/array.rs:30`：

```rust
pub struct ArrayObj {
    object: Object,
    data: *mut c_void,
    size: usize,
    capacity: usize,
    data_deleter: Option<TVMFFIObjectDeleter>,
}
pub struct Array<T> {
    data: ObjectArc<ArrayObj>,
    _phantom: std::marker::PhantomData<T>,
}
```

### Map<K,V>（F-323）

`collections/map.rs:30`：

```rust
pub struct MapObj {
    object: Object,
    data: *mut c_void,
    size: u64,
    slots: u64,
}
pub struct Map<K,V> {
    data: ObjectArc<MapObj>,
    _phantom: std::marker::PhantomData<(K,V)>,
}
```

### Shape（集合类型之一）

`collections/shape.rs`：

```rust
pub struct ShapeObj {
    object: Object,
    data: TVMFFIShapeCell,
}
pub struct Shape {
    data: ObjectArc<ShapeObj>,
}
```

实现 `Deref<Target=[i64]>`，可直接索引访问维度。

## String 与 Bytes（F-326~F-328）

`string.rs` 实现了小字符串优化（SOO）：

```rust
// Bytes
pub struct Bytes { data: Any }
// String
pub struct String { data: Any }
```

对于 ≤7 字节的内容，直接内联存储在 `TVMFFIAny.data_union.v_bytes` 中（type_index 分别为 `kTVMFFISmallBytes=12`、`kTVMFFISmallStr=11`）。对于更长的内容，使用 `ObjectArc` + extra items 分配堆内存（type_index 分别为 `kTVMFFIBytes=66`、`kTVMFFIStr=65`）。

`String::from_str` 调用 `TVMFFIStringFromByteArray`（F-327），`String::as_bytes` 调用 `TVMFFIStringGetData`（F-328）。

## 设计分析

tvm-ffi 安全包装层的核心设计哲学：

1. **所有对象通过 ObjectArc 管理**：无论 Tensor、Array、Map 还是 Function，底层都是 `ObjectArc<T>`，统一引用计数生命周期。
2. **derive 宏自动生成反射代码**：`#[derive(Object)]` 自动生成 `ObjectCore` 实现，`#[derive(ObjectRef)]` 自动生成 `ObjectRefCore` 实现。
3. **AnyCompatible trait 统一类型转换**：集合类型通过 `AnyCompatible` trait 实现与 `Any`/`AnyView` 的双向转换。
4. **SOO 优化减少内存分配**：String/Bytes 对短内容避免堆分配，与 C++ 侧 `SmallStr`/`SmallBytes` 类型索引对齐。

## 扩展讨论

### ObjectArc：把 C++ 引用计数藏进 Rust 智能指针

`ObjectArc<T>` 等价于 C++ 的 `ObjectPtr<T>`，其 `Clone` 调用 `inc_ref` 递增强引用、`Drop` 调用 `dec_ref` 递减，Deref/DerefMut 透明访问底对象。如此，C++ 手动引用计数的每一点开销都由 Rust 编译器在作用域边界自动插入，上层 `ObjectRef` 派生即可获得与 `Arc<T>` 相似的体验；`ObjectArc::new` 用 `alloc::alloc` 直接落位并 `ptr::write` 头部，规避了「先构造后改布局」的对齐问题。

### Unsafe trait 前置条件是安全层的契约地基

`ObjectCore`/`ObjectRefCore` 被标记为 unsafe trait，因为实现者必须保证 `type_index` 与运行时类型表一致、布局与 `#[repr(C)]` 约定吻合。derive 宏在编译期生成这些实现，因而绝大多数用户不会触碰到 unsafe 细节；只有在手工 impl 时才需要自行维持不变量（视角 140）。这把「安全 API 与安全契约」分离，让默认路径无 unsafe、进阶路径显式 unsafe。

### Function 包装让闭包也能成为 FFI 对象

`Function = ObjectArc<FunctionObj>`，而 `CallbackFunctionObjImpl<F>` 把 Rust 闭包 `F` 作为尾随字段与 `TVMFFIFunctionCell` 一并存进同一对象，由 `Function::from_packed`（对应 C++ `Function::FromPacked` 语义）构造。这意味着任意符合 `Fn(&[AnyView])->Result<Any>` 的 Rust 闭包都能被注册为全局函数、跨 FFI 边界调用，成为面向回调式互操作（如 NPU 图调度）的通用载体。

### 集合类型的 Phantom 泛型

`Array<T>` 与 `Map<K,V>` 都用 `PhantomData` 携带元素类型，但底层 `ObjectArc<ArrayObj>`/`ObjectArc<MapObj>` 并不含类型信息——Rust 以此把「类型安全」限定在编译期，运行时类型由元素自身的 `type_index` 判定。这让同一容器对象可以在不同泛型签名间复用布局，同时编译期仍能捕获元素类型错配。

## 相关概念

- [视角135 Rust 所有权与 FFI](135-rust-ownership-and-ffi.md)：ObjectArc 的引用计数机制
- [视角136 Rust 中的 Any](136-rust-any.md)：AnyCompatible trait 体系
- [视角140 Rust 安全不变量](140-rust-safety-invariants.md)：unsafe 代码的安全契约
