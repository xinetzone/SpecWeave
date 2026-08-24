---
type: Concept
title: "视角135：Rust 所有权与 FFI"
description: "分析 Rust 所有权系统与 FFI 边界的交互，ObjectArc 引用计数、Any 的拷贝/移动语义、FFI 边界的所有权转移，以及在 NPU 异构环境中的适配建议。"
tags:
  - rust
  - ownership
  - ffi
  - reference-counting
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-311, F-312
  - code:
    - rust/tvm-ffi/src/object.rs
    - rust/tvm-ffi/src/any.rs
    - rust/tvm-ffi/src/function.rs
    - rust/tvm-ffi-sys/src/c_api.rs
---

# 视角135：Rust 所有权与 FFI

## 概述

Rust 的所有权系统与 FFI 边界之间存在天然的张力：Rust 的借用检查器要求在编译期确保内存安全，而 FFI 边界（C/C++）不存在这些约束。TVM FFI 通过 `ObjectArc<T>` 引用计数智能指针和 `Any`/`AnyView` 的所有权语义来解决这一矛盾，在保持 Rust 内存安全的同时与 C++ 侧的对象模型保持一致。

## ObjectArc：引用计数智能指针

### 结构

`object.rs:39-42`：

```rust
#[repr(C)]
pub struct ObjectArc<T: ObjectCore> {
    ptr: std::ptr::NonNull<T>,
    _phantom: std::marker::PhantomData<T>,
}
```

`ObjectArc` 持有一个 `NonNull<T>` 指针，通过组合引用计数（`combined_ref_count`）管理生命周期。它等价于 C++ 的 `ObjectPtr<T>`。

### Clone：IncRef

`object.rs:571-580`：

```rust
impl<T: ObjectCore> Clone for ObjectArc<T> {
    fn clone(&self) -> Self {
        unsafe { unsafe_::inc_ref(self.ptr.as_ref() as *mut TVMFFIObject) }
        Self { ptr: self.ptr, _phantom: std::marker::PhantomData }
    }
}
```

Clone 不拷贝数据，仅递增强引用计数。这使 `ObjectArc` 可以像 `std::shared_ptr` 一样共享所有权。

### Drop：DecRef + 两阶段删除

`object.rs:564-568` 和 `object.rs:264-302`：

```rust
impl<T: ObjectCore> Drop for ObjectArc<T> {
    fn drop(&mut self) {
        unsafe { unsafe_::dec_ref(self.ptr.as_mut() as *mut TVMFFIObject) }
    }
}
```

`dec_ref` 实现三路分支（见视角028）：

1. **BothOne 快速路径**（强=1、弱=1）：一次原子减后 deleter 同时执行析构和内存释放。
2. **两阶段删除**（强=1、弱>1）：先调用 deleter(Strong) 析构对象，再原子递减弱引用，弱引用归零时调用 deleter(Weak) 释放内存。
3. **普通递减**（强>1）：仅递减，不触发删除。

### 从 C++ 获取的原始指针

`ObjectArc::from_raw`（`object.rs:470-475`）允许从 C API 返回的 `TVMFFIObjectHandle` 构建 ObjectArc，将所有权转移给 Rust：

```rust
pub unsafe fn from_raw(ptr: *const T) -> Self {
    Self { ptr: std::ptr::NonNull::new_unchecked(ptr as *mut T), _phantom: PhantomData }
}
```

## Any 的所有权语义

### Clone 触发引用计数

`any.rs:239-247`：

```rust
impl Clone for Any {
    fn clone(&self) -> Self {
        if self.data.type_index >= TypeIndex::kTVMFFIStaticObjectBegin as i32 {
            unsafe { object::unsafe_::inc_ref(self.data.data_union.v_obj) }
        }
        Self { data: self.data }
    }
}
```

`Any` 的 Clone 判断 type_index：对象类型（≥64）触发 `inc_ref`，值类型（<64）直接按位拷贝（因为 TVMFFIAny 是 16 字节的 Copy 结构体）。

### Drop 触发引用释放

`any.rs:249-256` 对称地处理 Drop。

### AnyView → Any：所有权提升

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

从 `AnyView`（非拥有视图）构造 `Any`（拥有型容器），通过 `TVMFFIAnyViewToOwnedAny` C API 执行深拷贝。这是唯一需要从 C 侧发起所有权转移的场景。

## FFI 边界的所有权转移

### Function 闭包的生命周期

`function.rs:56-96` 中，`CallbackFunctionObjImpl<F>` 持有 Rust 闭包 `F: Fn(&[AnyView]) -> Result<Any> + 'static`。闭包通过 `ObjectArc` 包装后，其生命周期与 Function 对象绑定：

```rust
struct CallbackFunctionObjImpl<F: Fn(&[AnyView]) -> Result<Any> + 'static> {
    function: FunctionObj,
    callback: F,
}
```

当最后一个 `Function` 引用释放时，`CallbackFunctionObjImpl` 的 Drop 会自动调用闭包的 Drop，释放所有捕获的 Rust 资源。

### from_raw / into_raw：所有权的手动转移

```rust
// Rust → C++：交出所有权
pub unsafe fn into_raw(this: Self) -> *const T {
    let droped_this = std::mem::ManuallyDrop::new(this);
    droped_this.ptr.as_ptr() as *const T
}

// C++ → Rust：获取所有权
pub unsafe fn from_raw(ptr: *const T) -> Self {
    Self { ptr: NonNull::new_unchecked(ptr as *mut T), _phantom: PhantomData }
}
```

这两个 unsafe 方法允许在所有权和裸指针之间显式转换，类似于 C++ 的 `release()` 和 `reset(ptr)`。

## 与 C++ 移动语义的对比

| 特性 | C++ TVM FFI | Rust tvm-ffi |
|------|------------|-------------|
| 对象所有权 | `ObjectPtr<T>` 裸指针 + 引用计数 | `ObjectArc<T>` 智能指针 + 引用计数 |
| 拷贝 | 显式 IncRef | `Clone` 自动 inc_ref |
| 移动 | `std::move` + 置空 | Rust 所有权转移（Move语义） |
| 视图借用 | `ObjectPtr<T>&` 引用 | `AnyView<'a>` 带生命周期 |
| 右值引用 | `T&&` | Rust 无右值引用，用 `move_to_any` 模拟 |

Rust 版通过类型系统强制所有权的显式管理：从 `Any` 取回值必须经过 `move_from_any_after_check`，编译器确保不会重复使用已 move 的值。

## NPU建议

在 NPU（神经网络处理单元）等异构计算环境中使用 TVM FFI Rust 绑定时，需考虑以下适配建议：

### 1. ObjectArc 的跨设备生命周期管理

NPU 推理通常涉及 Host 端（Rust/CPU）和 Device 端（NPU）的数据交互。建议：

- **对象生命周期与设备流绑定**：在提交 NPU 任务前调用 `ObjectArc::clone()` 持有对象引用，在任务完成回调中 Drop。避免在 NPU DMA 传输期间对象被释放。
- **避免跨设备共享 ObjectArc**：NPU kernel 不应直接持有 `ObjectArc<T>` 的 Rust 智能指针。应通过整数句柄或 DLPack 描述符传递数据所有权信息，由 Host 端管理 ObjectArc。
- **Device 端对象使用裸指针**：如果 NPU kernel 需要直接访问对象数据，使用 `ObjectArc::as_raw()` 获取裸指针，但必须在 Host 端确保对象存活期覆盖 NPU 任务执行期。

### 2. Any 跨 FFI 边界的 NPU 场景

- **TVMFFIAnyViewToOwnedAny 的性能**：此函数执行深拷贝，在高频路径（如 batch inference 的每个样本）上可能成为瓶颈。建议：
  - 对 tensor 数据使用 DLPack 零拷贝传递（`TVMFFITensorFromDLPack`），避免 Any 的序列化/反序列化。
  - 对字符串/整型等小值类型，利用 SOO（小对象优化）避免堆分配。
- **回调闭包的 NPU 亲和性**：`CallbackFunctionObjImpl<F>` 中的闭包在 Host 端执行。如果回调需要触发 NPU 操作，确保闭包内不调用可能阻塞的 NPU 同步 API。

### 3. 引用计数的 NPU 原子操作

- **NPU 侧不操作引用计数**：`ObjectArc` 的 Clone/Drop 涉及 64 位原子操作。这些操作应始终在 Host 端执行，不在 NPU kernel 中调用。
- **批量 IncRef/DecRef**：在 NPU 任务提交阶段批量 clone 所需对象，在任务完成阶段统一 drop。减少原子操作的频率，降低缓存行竞争。
- **多 NPU PE 场景**：如果多个 NPU PE 需要共享对象引用，在 Host 端维护引用计数，通过消息传递将"增加引用"请求串行化到创建对象的 PE。

### 4. Error 对象的 NPU 错误传播

- **异步错误的处理**：NPU 错误通常通过 stream 回调传播。`Error::from_raised()` 依赖 TLS 中的 raised error，这在异步 NPU 回调中可能不可靠。建议：
  - 在 NPU 回调中显式构造 `Error::new(kind, message, traceback)`，不依赖 TLS。
  - 使用 `Error::with_appended_backtrace()` 追加 NPU 侧的调用栈信息。
- **错误对象的引用计数**：`Error::with_appended_backtrace` 在单引用时原地 mutate（避免拷贝），多引用时创建新 Error。在 NPU 并发场景中，如果多个回调同时修改同一 Error，应克隆后再修改。

### 5. String/Bytes 小对象优化的 NPU 意义

- **短字符串内联存储**：SOO 对 ≤7 字节的字符串/字节数组避免堆分配。在 NPU 推理中，常见的 dtype 字符串（如"float32"=7字节）、设备名（如"cuda"=4字节）恰好可内联存储，减少内存分配开销。
- **长字符串的 NPU 场景**：错误消息、堆叠算子名称等超长字符串走堆分配路径。建议在 NPU kernel 中避免构造过长的错误消息，或将错误消息预先缓存。

## 相关概念

- [视角028 组合引用计数](/02-core-types/concepts/028-combined-refcount.md)：combined_ref_count 的原子操作
- [视角133 tvm-ffi 安全包装](133-tvm-ffi-safe-wrapper.md)：ObjectArc 的 API 详情
- [视角136 Rust 中的 Any](136-rust-any.md)：Any 的所有权语义
- [视角025 FFI 移动语义](/02-core-types/concepts/025-ffi-move-semantics.md)：C++ 侧的移动语义对比
