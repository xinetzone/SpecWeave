---
type: Concept
title: "视角140：Rust 安全不变量"
description: "分析 tvm-ffi Rust 绑定中 unsafe 代码的安全契约、不变量保证，以及如何通过类型系统和设计模式将 unsafe 操作封装在安全抽象之后。"
tags:
  - rust
  - safety
  - unsafe
  - invariants
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-311, F-313
  - code:
    - rust/tvm-ffi/src/object.rs
    - rust/tvm-ffi/src/any.rs
    - rust/tvm-ffi/src/function.rs
    - rust/tvm-ffi/src/type_traits.rs
    - rust/tvm-ffi-sys/src/c_api.rs
---

# 视角140：Rust 安全不变量

## 概述

TVM FFI 的 Rust 绑定包含大量 `unsafe` 代码（FFI 调用、裸指针操作、unsafe trait 实现），但通过类型系统、结构不变量和设计模式，将这些 unsafe 操作封装在安全 API 之后。本视角分析关键安全不变量及其实现机制。

## unsafe trait 的安全契约

### ObjectCore trait

`object.rs:51-77`：

```rust
pub unsafe trait ObjectCore: Sized + 'static {
    const TYPE_KEY: &'static str;
    const TYPE_DEPTH: i32;
    const TYPE_FINAL: bool = false;
    fn type_index() -> i32;
    unsafe fn object_header_mut(this: &mut Self) -> &mut TVMFFIObject;
}
```

实现此 trait 的安全不变量：

1. **type_index 一致性**：`Self::type_index()` 返回的值必须在运行时类型表中存在，且与 `TYPE_KEY` 注册的类型一致。
2. **TYPE_DEPTH 正确性**：深度必须与类型继承树中的实际深度一致（根 `Object` 为 0）。
3. **object_header_mut 布局兼容**：`Self` 的首字段必须是 `TVMFFIObject`（或等价布局），确保 `as *mut TVMFFIObject` 转换正确。

`Object` 基类（`object.rs:378-389`）的实现满足这些不变量：

```rust
unsafe impl ObjectCore for Object {
    const TYPE_KEY: &'static str = "ffi.Object";
    const TYPE_DEPTH: i32 = 0;
    fn type_index() -> i32 { TypeIndex::kTVMFFIStaticObjectBegin as i32 }
    unsafe fn object_header_mut(this: &mut Self) -> &mut TVMFFIObject {
        &mut this.header
    }
}
```

### ObjectRefCore trait

`object.rs:124-129`，安全不变量（来自 doc comment）：

> `data`、`into_data`、`from_data` 必须保持相同的对象分配，形成所有权-preserving 的往返。分配必须以有效的 `TVMFFIObject` 头开始，其注册的 type index 正确描述布局和继承。

`ObjectRef` 通过 `#[derive(ObjectRef)]` 自动生成实现，确保这些不变量由宏保证而非手动编码。

### AnyCompatible trait

`type_traits.rs:27-71`，安全不变量：

1. **check_any_strict 与 type_index 一致**：`check_any_strict` 返回 true 当且仅当 `data.type_index` 是该类型接受的精确索引（或兼容索引）。
2. **copy/move 对称性**：`copy_to_any_view(src, data)` 后，`copy_from_any_view_after_check(data)` 必须返回与 `src` 等值的对象。
3. **move 后 Any 为空**：`move_to_any(src, data)` 后，调用者不再拥有 `src`（Rust 编译期通过 move 语义保证）。

## ObjectArc 的安全不变量

### 引用计数不变量

`ObjectArc<T>` 维护以下不变量：

1. **指针有效性**：`ptr: NonNull<T>` 始终指向有效分配的对象，其头部的 `combined_ref_count` ≥ 1（强引用）。
2. **deleter 正确性**：对象头部的 `deleter` 函数指针在对象存活期间有效，且在 Drop 时恰好被调用一次。
3. **type_index 一致性**：`ptr` 指向的对象的 `type_index` 字段等于 `T::type_index()`。

这些不变量通过以下方式保证：

- **构造时初始化**：`ObjectArc::new()` 使用 `std::alloc::alloc` + `std::ptr::write` 手动分配和初始化，确保 header 正确写入（`object.rs:396-421`）。
- **Drop 时清理**：`Drop::drop` 调用 `dec_ref`，后者在引用计数归零时调用 deleter 释放内存。
- **from_raw 的契约**：`from_raw(ptr)` 要求调用者保证 `ptr` 指向的对象已通过 `ObjectArc` 创建（即引用计数已初始化），且调用者在传入后不再通过 `ptr` 访问对象。

### Send/Sync 标注

`object.rs:44-45`：

```rust
unsafe impl<T: Send + Sync + ObjectCore> Send for ObjectArc<T> {}
unsafe impl<T: Send + Sync + ObjectCore> Sync for ObjectArc<T> {}
```

`ObjectArc<T>` 的 `Send`/`Sync` 依赖于 `T` 的 `Send`/`Sync`。这是合理的，因为：
- 引用计数操作（`fetch_add`/`fetch_sub`）是原子的，多线程安全。
- 对象的实际数据 `T` 必须也是线程安全的，否则共享引用会导致数据竞争。

## Any 的安全不变量

### type_index 阈值不变量

`any.rs:242` 和 `any.rs:252`：

```rust
if self.data.type_index >= TypeIndex::kTVMFFIStaticObjectBegin as i32 {
    unsafe { object::unsafe_::inc_ref(self.data.data_union.v_obj) }
}
```

不变量：type_index ≥ 64 的值必然是指向 `TVMFFIObject` 的指针（存储在 `data_union.v_obj` 中）；type_index < 64 的值是 POD 数据（存储在 `data_union.v_int64` 等字段中）。此不变量由 `TVMFFITypeIndex` 枚举保证，Rust 类型系统确保只有合法的 type_index 被写入。

### From<AnyView> 的不变量

`any.rs:295-304`：

```rust
impl From<AnyView<'_>> for Any {
    fn from(value: AnyView<'_>) -> Self {
        unsafe {
            let mut data = TVMFFIAny::new();
            crate::check_safe_call!(TVMFFIAnyViewToOwnedAny(&value.data, &mut data)).unwrap();
            Self { data }
        }
    }
}
```

`TVMFFIAnyViewToOwnedAny` 将视图深拷贝为拥有型 Any。不变量：无论 `AnyView` 的源数据是什么类型，`TVMFFIAnyViewToOwnedAny` 都会创建一个新的 `TVMFFIAny`，对于对象类型会 `inc_ref`，对于值类型会按位拷贝。

## Function 的安全不变量

### CallbackFunctionObjImpl 的生命周期

`function.rs:56-96`：

```rust
struct CallbackFunctionObjImpl<F: Fn(&[AnyView]) -> Result<Any> + 'static> {
    function: FunctionObj,
    callback: F,
}
```

不变量：
1. **`'static` 约束**：闭包 `F` 不能捕获任何非 `'static` 的引用。这确保闭包可以安全地存储在堆对象中，不受栈帧生命周期的约束。
2. **safe_call 函数指针**：`invoke_callback` 作为 `TVMFFIFunctionCell.safe_call` 存储，通过 `ObjectArc` 的生命周期管理，确保在函数调用时回调对象仍然存活。
3. **错误传播**：回调返回 `Err(Error)` 时，通过 `Error::set_raised` 设置 TLS raised error，返回 -1 给 C 侧。C 侧通过 `from_raised` 获取错误。此链路的不变量是：在任何 safe_call 调用中，要么返回 0 并填写 result，要么返回非零并设置 raised error，二者必居其一。

## unsafe_ 模块的安全边界

`object.rs:231-364` 的 `unsafe_` 模块提供了对象系统的底层原语，所有 unsafe 操作被限制在此模块内：

| 函数 | 安全假设 |
|------|---------|
| `inc_ref(handle)` | `handle` 指向有效的 `TVMFFIObject`，`combined_ref_count` 已初始化 |
| `dec_ref(handle)` | 同上，且调用者在引用计数归零后不再访问该对象 |
| `strong_count(handle)` | 同上，仅用于调试 |
| `object_deleter_for_new<T>` | `ptr` 指向通过 `ObjectArc::new` 分配的 `T` 对象 |
| `object_deleter_for_new_with_extra_items<T,U>` | `ptr` 指向通过 `ObjectArc::new_with_extra_items` 分配的对象 |

这些函数均为 `pub(crate)`，不出现在 crate 的公共 API 中。

## 设计模式：将 unsafe 封装在 safe 抽象之后

TVM FFI Rust 绑定的安全策略可以概括为三层：

1. **类型系统层**：通过 `ObjectArc<T>`、`Any`、`AnyView<'a>` 等类型，利用 Rust 的所有权系统自动管理生命周期，使大多数用户代码完全安全。
2. **unsafe 模块层**：所有 unsafe 操作集中在 `unsafe_`、`function_internal`、`match_any_internal` 等内部模块，对外暴露安全 API。
3. **unsafe trait 契约层**：`ObjectCore`、`ObjectRefCore`、`AnyCompatible` 等 unsafe trait 通过文档和 derive 宏保证不变量，实现者需遵守契约。

## 相关概念

- [视角135 Rust 所有权与 FFI](135-rust-ownership-and-ffi.md)：ObjectArc 的引用计数机制
- [视角133 tvm-ffi 安全包装](133-tvm-ffi-safe-wrapper.md)：derive 宏的不变量保证
- [视角136 Rust 中的 Any](136-rust-any.md)：Any 的类型不变量
- [视角028 组合引用计数](/02-core-types/concepts/028-combined-refcount.md)：底层引用计数不变量
