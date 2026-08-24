---
type: Concept
title: "视角085：Expected 无异常错误处理"
description: "分析 Expected<T> 模板类的设计：类 Result 的无异常错误处理、Any 存储的类型擦除、Unexpected 错误包装器、is_ok/is_err/value/error/value_or 接口、Expected<void> 特化，以及 TypeTraits 集成使其能作为 FFI 参数和返回值跨语言传递。"
tags:
  - error-handling
  - expected
  - result-type
  - exception-free
  - type-traits
  - any
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-202, F-212, F-213
  - code:
    - include/tvm/ffi/expected.h
    - include/tvm/ffi/error.h
    - include/tvm/ffi/any.h
---

# 视角085：Expected 无异常错误处理

## 概述

并非所有 C++ 环境都支持异常——某些嵌入式工具链、性能关键代码或编码规范禁用 C++ 异常。TVM FFI 提供 `Expected<T>` 模板类，类似 Rust 的 `Result<T, E>` 和 C++23 的 `std::expected`，以值语义返回成功值或错误对象，无需抛出异常。`Expected` 利用 FFI 的 `Any` 类型擦除机制存储成功值或 `Error`，并通过 `TypeTraits` 特化使其能作为 FFI 函数的参数和返回值跨语言传递。本视角分析 Expected 的类型设计、接口语义和 FFI 集成。

## Expected 模板类设计

### 类定义概述

`Expected<T>` 定义在 `include/tvm/ffi/expected.h:99-207`。其核心存储是一个 `Any data_` 成员：

```cpp
template <typename T>
class Expected {
 public:
  static_assert(!std::is_void_v<T>,
      "Expected with a cv-qualified void success type is not allowed. "
      "Use Expected<void>.");
  static_assert(!std::is_same_v<T, Error>,
      "Expected<Error> is not allowed. Use Error directly.");

  Expected(T value) : data_(Any(std::move(value))) {}
  Expected(Error error) : data_(Any(std::move(error))) {}

  template <typename E, typename = std::enable_if_t<
      std::is_base_of_v<Error, std::remove_cv_t<E>>>>
  Expected(Unexpected<E> unexpected)
      : data_(Any(std::move(unexpected).error())) {}

  int32_t type_index() const noexcept;
  bool is_ok() const noexcept;
  bool is_err() const noexcept;
  bool has_value() const noexcept;
  T value() const&;
  T value() &&;
  Error error() const&;
  Error error() &&;
  T value_or(U&& default_value) const&;
  T value_or(U&& default_value) &&;

 private:
  Expected() = default;
  friend struct details::ExpectedUnsafe;
  Any data_;
};
```

### 静态约束

两个 `static_assert` 强制了编译期约束：

1. **禁止 void**：`Expected<void>` 需要使用单独的特化版本，因为主模板假设 T 是具体值类型。
2. **禁止 Error**：`Expected<Error>` 没有意义——如果函数总是返回错误，直接返回 `Error` 即可。这避免了"成功值本身是错误"的语义歧义。

### Any 存储

`Expected<T>` 使用 `Any data_` 存储成功值或错误：

- 成功时，`data_` 持有类型为 T 的值，`type_index() != kTVMFFIError`。
- 失败时，`data_` 持有 `Error` 对象，`type_index() == kTVMFFIError`。

这种设计利用了 `Any` 的类型擦除能力——一个存储槽可以持有任意 FFI 兼容类型，无需 `Expected` 自己实现 tagged union。`kTVMFFIError = 67` 是错误对象的类型索引，作为区分成功和失败的标签。

## Unexpected 包装器

`Unexpected<E>` 定义在 `expected.h:40-65`：

```cpp
template <typename E = Error>
class Unexpected {
  static_assert(std::is_base_of_v<Error, std::remove_cv_t<E>>,
      "Unexpected<E> requires E to be Error or a subclass of Error.");

 public:
  explicit Unexpected(E error) : error_(std::move(error)) {}
  const E& error() const& noexcept { return error_; }
  E& error() & noexcept { return error_; }
  const E&& error() const&& noexcept { return std::move(error_); }
  E&& error() && noexcept { return std::move(error_); }

 private:
  E error_;
};
```

`Unexpected` 的作用是**消除歧义**。没有它，`Expected<T>` 的两个构造函数 `Expected(T)` 和 `Expected(Error)` 在 T 本身可从 Error 构造时可能产生歧义。使用 `Unexpected` 需要显式包装：

```cpp
Expected<int> Divide(int a, int b) {
  if (b == 0) {
    return Unexpected(Error("ValueError", "Division by zero", ""));
  }
  return a / b;
}
```

C++17 推导指引（`expected.h:63-65`）允许省略模板参数：

```cpp
template <typename E>
Unexpected(E) -> Unexpected<E>;
```

`Unexpected` 的 static_assert 要求 E 必须是 Error 或其子类，确保错误类型的一致性。

## 核心接口

### 状态查询

```cpp
TVM_FFI_INLINE bool is_ok() const noexcept {
  return data_.type_index() != TypeIndex::kTVMFFIError;
}

TVM_FFI_INLINE bool is_err() const noexcept {
  return data_.type_index() == TypeIndex::kTVMFFIError;
}

TVM_FFI_INLINE bool has_value() const noexcept {
  return is_ok();
}
```

这三个方法都是 `noexcept` 且内联，仅检查类型索引，性能开销为单次整数比较。

### value()：获取成功值

```cpp
TVM_FFI_INLINE T value() const& {
  if (TVM_FFI_PREDICT_TRUE(is_ok())) {
    return details::AnyUnsafe::CopyFromAnyViewAfterCheck<T>(data_);
  }
  throw details::AnyUnsafe::CopyFromAnyViewAfterCheck<Error>(data_);
}

TVM_FFI_INLINE T value() && {
  if (TVM_FFI_PREDICT_TRUE(is_ok())) {
    return details::AnyUnsafe::MoveFromAnyAfterCheck<T>(std::move(data_));
  }
  throw details::AnyUnsafe::MoveFromAnyAfterCheck<Error>(std::move(data_));
}
```

关键设计：

- **成功时**：从 Any 中提取 T 值。左值重载复制，右值重载移动。
- **失败时**：从 Any 中提取 Error 并抛出。这意味着 `value()` 在错误路径上仍然使用异常——但这是调用者的选择，函数本身可以不使用异常返回 Expected。
- **PREDICT_TRUE**：提示编译器成功是大概率路径。

这种设计使得 `Expected<T>` 可以与异常代码互操作：无异常函数返回 Expected，调用者可以选择检查 `is_ok()` 或直接调用 `value()` 让错误抛出为异常。

### error()：获取错误

```cpp
TVM_FFI_INLINE Error error() const& {
  if (is_ok()) {
    TVM_FFI_THROW(RuntimeError)
        << "Bad expected access: contains value, not error";
  }
  return details::AnyUnsafe::CopyFromAnyViewAfterCheck<Error>(data_);
}
```

与 `value()` 对偶，在成功状态下调用 `error()` 会抛出 `RuntimeError`。注释说明了不使用分支预测提示的原因：`error()` 本身就是冷路径，调用者只在观察到 `!is_ok()` 后才调用，分支方向不重要。

### value_or()：带默认值

```cpp
template <typename U = std::remove_cv_t<T>>
TVM_FFI_INLINE T value_or(U&& default_value) const& {
  if (TVM_FFI_PREDICT_TRUE(is_ok())) {
    return details::AnyUnsafe::CopyFromAnyViewAfterCheck<T>(data_);
  }
  return T(std::forward<U>(default_value));
}
```

成功时返回实际值，失败时返回传入的默认值。支持完美转发，默认值可以是惰性构造的值或工厂函数的结果（如果 T 支持从可调用对象构造）。

## Expected<void> 特化

`Expected<void>` 特化定义在 `expected.h:216-284`，用于无返回值的操作：

```cpp
template <>
class Expected<void> {
 public:
  Expected() = default;
  Expected(Error error) : data_(Any(std::move(error))) {}

  bool is_ok() const noexcept;
  bool is_err() const noexcept;
  void value() const&;
  void value() &&;
  Error error() const&;
  Error error() &&;

 private:
  friend struct details::ExpectedUnsafe;
  Any data_;
};
```

关键区别：

1. **默认构造表示成功**：`Expected<void>` 成功时不持有值，默认构造即为成功状态。
2. **value() 返回 void**：成功时不返回值，仅验证状态；失败时抛出错误。
3. **底层存储 None**：成功时 `data_` 持有 FFI None（`std::nullptr_t`），失败时持有 Error。

`value()` 的实现：

```cpp
TVM_FFI_INLINE void value() const& {
  if (TVM_FFI_PREDICT_FALSE(is_err())) {
    throw details::AnyUnsafe::CopyFromAnyViewAfterCheck<Error>(data_);
  }
}
```

使用场景：

```cpp
Expected<void> Validate(const Tensor& t) {
  if (t->shape.ndim() < 0) {
    return Unexpected(Error("ValueError", "Invalid shape", ""));
  }
  return {};  // 成功
}
```

## ExpectedUnsafe：ABI 边界辅助

`ExpectedUnsafe`（`expected.h:294-354`）提供 FFI ABI 边界的原始存储操作：

```cpp
struct ExpectedUnsafe {
  template <typename T>
  TVM_FFI_INLINE static Expected<T> MoveFromTVMFFIAny(TVMFFIAny raw);

  template <typename T>
  TVM_FFI_INLINE static TVMFFIAny MoveToTVMFFIAny(Expected<T>&& result);

  template <typename T>
  TVM_FFI_INLINE static const Any& GetData(const Expected<T>& result) noexcept;

  template <typename T, typename U>
  TVM_FFI_INLINE static T ValueAs(const Expected<U>& result);
};
```

这些方法绕过正常的值检查，用于 ABI 边界代码——这些代码已经知道底层 Any 存储持有有效的 T 或 Error，不需要重复检查。`MoveToTVMFFIAny` 和 `MoveFromTVMFFIAny` 实现 Expected 与原始 FFI Any 表示之间的零拷贝转换。

`ValueAs` 是一个模板辅助，在 T 为 void 时验证成功状态不返回值，否则提取成功值或抛出错误。

## TypeTraits 集成

### Expected<T> 的 TypeTraits 特化

`TypeTraits<Expected<T>>`（`expected.h:363-416`）使 Expected 能作为 FFI 函数参数和返回值：

```cpp
template <typename T>
struct TypeTraits<Expected<T>> : public TypeTraitsBase {
  TVM_FFI_INLINE static void CopyToAnyView(
      const Expected<T>& src, TVMFFIAny* result) {
    if (src.is_err()) {
      TypeTraits<Error>::CopyToAnyView(src.error(), result);
    } else {
      TypeTraits<T>::CopyToAnyView(src.value(), result);
    }
  }

  TVM_FFI_INLINE static void MoveToAny(
      Expected<T> src, TVMFFIAny* result) {
    if (src.is_err()) {
      TypeTraits<Error>::MoveToAny(std::move(src).error(), result);
    } else {
      TypeTraits<T>::MoveToAny(std::move(src).value(), result);
    }
  }

  TVM_FFI_INLINE static bool CheckAnyStrict(const TVMFFIAny* src) {
    return TypeTraits<T>::CheckAnyStrict(src) ||
           TypeTraits<Error>::CheckAnyStrict(src);
  }

  TVM_FFI_INLINE static Expected<T> CopyFromAnyViewAfterCheck(
      const TVMFFIAny* src) {
    if (TypeTraits<T>::CheckAnyStrict(src)) {
      return TypeTraits<T>::CopyFromAnyViewAfterCheck(src);
    }
    return TypeTraits<Error>::CopyFromAnyViewAfterCheck(src);
  }

  // ... TryCastFromAnyView, TypeStr, TypeSchema ...
};
```

关键设计：

1. **CopyToAnyView/MoveToAny**：根据 is_err() 状态，将底层值或错误写入 Any 视图。这意味着 Expected 在 FFI 边界被"展平"为普通 Any——接收方看到的是 T 值或 Error 对象，不需要知道 Expected 的存在。
2. **CheckAnyStrict**：接受 T 类型或 Error 类型的 Any，两种都能构造为 Expected。
3. **CopyFromAnyViewAfterCheck**：从 Any 构造 Expected，如果 Any 持有 T 则成功，持有 Error 则失败。
4. **TypeStr/TypeSchema**：报告类型为 `"Expected<T>"` 和 JSON schema `{"type":"Expected","args":[T_schema, {"type":"ffi.Error"}]}`，用于反射和文档生成。

### Expected<void> 的 TypeTraits 特化

`TypeTraits<Expected<void>>`（`expected.h:420-472`）类似，成功时使用 `TypeTraits<std::nullptr_t>`（即 None），失败时使用 `TypeTraits<Error>`。

### use_default_type_traits_v 禁用

```cpp
template <typename T>
inline constexpr bool use_default_type_traits_v<Expected<T>> = false;
```

此特化禁用默认 TypeTraits，强制编译器使用专门的 Expected TypeTraits，确保 FFI 边界的正确转换。

## 与 VISIT 宏的协作

`TVM_FFI_VISIT_END_RETURN_EXPECTED`（`visit_error_context.h:169-174`）支持 Expected 返回路径：

```cpp
#define TVM_FFI_VISIT_END_RETURN_EXPECTED(node)                \
  }                                                            \
  catch (::tvm::ffi::Error & _tvm_ffi_visit_err_) {            \
    ::tvm::ffi::details::UpdateVisitErrorContext(              \
        _tvm_ffi_visit_err_, (node));                          \
    return ::tvm::ffi::Unexpected(_tvm_ffi_visit_err_);        \
  }
```

在无异常代码中，访问器函数可以使用 Expected 返回值，VISIT 宏在捕获错误后返回 `Unexpected(error)` 而非重新抛出。这使得递归访问逻辑可以在 `-fno-exceptions` 环境中工作。

## 设计分析

`Expected<T>` 的设计核心是**利用 Any 类型擦除实现 tagged union**，而非自定义的 `union { T value; Error error; }`。这种选择有几个优势：

1. **复用 FFI 基础设施**：Any 已经处理了类型安全、对象引用计数、跨语言序列化等问题，Expected 不需要重新实现。
2. **简化 TypeTraits**：Expected 的 FFI 集成只需委托给 T 和 Error 的 TypeTraits，不需要额外的 ABI 代码。
3. **统一的错误表示**：Expected 中的 Error 与抛出的 Error 是同一类型，异常路径和无异常路径可以无缝互操作。

`value()` 在错误路径抛出 Error 的设计体现了"渐进式错误处理"哲学：函数作者可以选择不使用异常（返回 Expected），调用者可以根据场景选择：

- 性能关键代码：检查 `is_ok()`，手动处理错误，零异常开销。
- 业务逻辑代码：调用 `value()`，让错误自动抛出为异常，代码更简洁。
- 跨 FFI 边界：TypeTraits 自动展平，接收方语言看到的是值或 Error。

`Unexpected` 包装器虽然增加了语法开销（`return Unexpected(err)` 而非 `return err`），但消除了构造函数歧义，是值得的权衡。推导指引减少了模板参数的冗余。

`Expected<void>` 的特化展示了 C++ 模板特化在处理"无值成功"场景时的必要性。默认构造为成功、Error 构造为失败的设计，使得 `return {};` 成为自然的成功返回语法。

TypeTraits 集成是 Expected 能在 FFI 生态中工作的关键。没有它，Expected 只能在 C++ 内部使用；有了它，Expected 函数可以通过 FFI 被 Python/Rust 调用，错误自动转换为对应语言的异常。这种"零成本抽象"在 FFI 场景中尤为重要——在 C++ 内部使用 Expected 没有额外开销，跨边界时自动转换为语言原生错误机制。

## 相关概念

- [077 Error 类与 std::exception 集成](077-error-class-exception-integration.md)：Expected 中存储和抛出的 Error 类型
- [082 额外错误上下文 extra_context](082-error-extra-context.md)：VISIT_END_RETURN_EXPECTED 与 VisitErrorContext
- [017 Any 16字节布局](/02-core-types/concepts/017-anyview-non-owning.md)：Expected 底层使用的 Any 存储
- [023 类型特征 TypeTraits](/02-core-types/concepts/023-type-traits.md)：Expected 的 TypeTraits 集成机制
- [038 safe_call 与 cpp_call 双路径](/03-functions/concepts/038-safe-call-and-cpp-call.md)：异常与无异常路径的双轨设计
