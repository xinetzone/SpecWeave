---
type: Concept
title: "视角084：ErrorBuilder 与抛出宏"
description: "分析 ErrorBuilder 的流式 API 设计：析构函数抛出异常的 RAII 模式、TVM_FFI_THROW/LOG_AND_THROW 宏的回溯自动捕获、TVM_FFI_ICHECK/DCHECK 系列断言宏、LogCheck 模板函数的比较格式化，以及 COLD_CODE 优化和 MSVC 警告处理。"
tags:
  - error-handling
  - error-builder
  - throw-macros
  - assertion
  - cold-code
  - raii
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-208, F-209, F-210, F-211
  - code:
    - include/tvm/ffi/error.h
    - include/tvm/ffi/base_details.h
---

# 视角084：ErrorBuilder 与抛出宏

## 概述

TVM FFI 提供了一套流式错误构建和抛出工具，使开发者能以简洁的语法抛出包含回溯、因果链和上下文的丰富错误。核心是 `ErrorBuilder` 类——它利用 C++ 析构函数在临时对象生命周期结束时抛出异常的 RAII 模式，配合 `TVM_FFI_THROW`、`TVM_FFI_ICHECK` 等宏，实现了类似 glog CHECK 宏的开发者体验。本视角分析 ErrorBuilder 的设计、流式 API 实现、断言宏体系和代码优化策略。

## ErrorBuilder 类设计

### 类定义

`ErrorBuilder` 定义在 `include/tvm/ffi/error.h:339-387`：

```cpp
class ErrorBuilder {
 public:
  TVM_FFI_COLD_CODE
  explicit ErrorBuilder(std::string kind, std::string backtrace,
                        bool log_before_throw)
      : kind_(std::move(kind)),
        backtrace_(std::move(backtrace)),
        log_before_throw_(log_before_throw) {}

  TVM_FFI_COLD_CODE
  explicit ErrorBuilder(std::string kind,
                        const TVMFFIByteArray* backtrace,
                        bool log_before_throw)
      : ErrorBuilder(std::move(kind),
                     std::string(backtrace->data, backtrace->size),
                     log_before_throw) {}

  TVM_FFI_COLD_CODE
  explicit ErrorBuilder(std::string kind,
                        const TVMFFIByteArray* backtrace,
                        bool log_before_throw,
                        std::optional<Error> cause_chain,
                        std::optional<ObjectRef> extra_context)
      : ErrorBuilder(std::move(kind), backtrace, log_before_throw) {
    cause_chain_ = std::move(cause_chain);
    extra_context_ = std::move(extra_context);
  }

  [[noreturn]] TVM_FFI_COLD_CODE
  ~ErrorBuilder() noexcept(false) {
    ::tvm::ffi::Error error(std::move(kind_), stream_.str(),
                            std::move(backtrace_),
                            std::move(cause_chain_),
                            std::move(extra_context_));
    if (log_before_throw_) {
      std::cerr << error.FullMessage();
    }
    throw error;
  }

  std::ostringstream& stream() { return stream_; }

 protected:
  std::string kind_;
  std::ostringstream stream_;
  std::string backtrace_;
  bool log_before_throw_;
  std::optional<Error> cause_chain_;
  std::optional<ObjectRef> extra_context_;
};
```

### 析构函数抛出异常的模式

ErrorBuilder 最核心的设计是**在析构函数中抛出异常**。当开发者写：

```cpp
TVM_FFI_THROW(ValueError) << "Invalid value: " << x;
```

宏展开后：

```cpp
::tvm::ffi::details::ErrorBuilder(
    "ValueError",
    TVMFFIBacktrace(__FILE__, __LINE__, TVM_FFI_FUNC_SIG, 0),
    TVM_FFI_ALWAYS_LOG_BEFORE_THROW)
    .stream()
<< "Invalid value: " << x;
```

执行流程：

1. 构造临时 `ErrorBuilder` 对象，传入 kind 和回溯。
2. 调用 `stream()` 获取 `std::ostringstream&`。
3. `<<` 操作符将消息内容追加到 ostringstream。
4. 完整表达式结束时，临时对象析构。
5. 析构函数从 ostringstream 取出消息，构造 `Error` 对象，抛出。

这种模式的优势：

- **流式语法**：支持任意数量的 `<<` 拼接，每个参数只需实现 `operator<<(std::ostream&)`。
- **回溯自动捕获**：回溯在构造时（即宏展开位置）捕获，包含准确的抛出点。
- **无额外括号**：不需要 `TVM_FFI_THROW(ValueError, "message")` 这样的函数调用语法。
- **冷路径优化**：构造函数和析构函数都标记 `TVM_FFI_COLD_CODE`，编译器将错误路径代码远离热路径。

### MSVC 警告处理

MSVC 对析构函数中抛出异常有警告 C4722（"destructor will never return"）。ErrorBuilder 使用 pragma 抑制（`error.h:361-376`）：

```cpp
#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable : 4722)
#endif
[[noreturn]] TVM_FFI_COLD_CODE
~ErrorBuilder() noexcept(false) {
  // ...
  throw error;
}
#ifdef _MSC_VER
#pragma warning(pop)
#endif
```

`[[noreturn]]` 属性告知编译器此函数不会返回，有助于优化调用点代码。`noexcept(false)` 显式标记析构函数可能抛出，覆盖 C++11 默认的 `noexcept(true)` 析构语义。

### log_before_throw 选项

`log_before_throw_` 控制抛出前是否将完整错误消息输出到 stderr：

- **TVM_FFI_THROW**：使用 `TVM_FFI_ALWAYS_LOG_BEFORE_THROW`（默认为 0），不记录日志，依赖上层 catch 处理。
- **TVM_FFI_LOG_AND_THROW**：固定传 `true`，在抛出前打印错误。

`TVM_FFI_LOG_AND_THROW`（`error.h:413-416`）适用于启动阶段等错误无法被捕获的场景：

```cpp
#define TVM_FFI_LOG_AND_THROW(ErrorKind)                          \
  ::tvm::ffi::details::ErrorBuilder(                              \
      #ErrorKind, TVMFFIBacktrace(__FILE__, __LINE__,            \
                                  TVM_FFI_FUNC_SIG, 0), true)    \
      .stream()
```

文档注释说明："This is only necessary on startup functions where we know error cannot be caught, and it is better to have a clear log message."

## TVM_FFI_THROW 宏

### 基本宏

```cpp
#define TVM_FFI_THROW(ErrorKind)                                              \
  ::tvm::ffi::details::ErrorBuilder(#ErrorKind,                               \
                                    TVMFFIBacktrace(__FILE__, __LINE__,       \
                                                    TVM_FFI_FUNC_SIG, 0),     \
                                    TVM_FFI_ALWAYS_LOG_BEFORE_THROW)          \
      .stream()
```

关键组成：

- `#ErrorKind`：将宏参数字符串化为 kind 字符串。
- `TVMFFIBacktrace(__FILE__, __LINE__, TVM_FFI_FUNC_SIG, 0)`：在抛出点捕获回溯，`cross_ffi_boundary=0` 表示在 FFI 边界停止。
- `TVM_FFI_FUNC_SIG`：编译器特定的函数签名宏（GCC/Clang 的 `__PRETTY_FUNCTION__`，MSVC 的 `__FUNCSIG__`）。
- `.stream()`：返回 ostringstream 引用以支持 `<<`。

### 使用示例

```cpp
if (shape.ndim() < 0) {
  TVM_FFI_THROW(ValueError)
      << "Tensor rank must be non-negative, got " << shape.ndim();
}

TVM_FFI_THROW(RuntimeError)
    << "Unsupported dtype: " << dtype;
```

## 断言检查宏体系

### TVM_FFI_CHECK 宏

`TVM_FFI_CHECK(cond, ErrorKind)`（`error.h:471-473`）是条件检查的基础宏：

```cpp
#define TVM_FFI_CHECK(cond, ErrorKind) \
  if (TVM_FFI_PREDICT_FALSE(!(cond)))  \
  TVM_FFI_THROW(ErrorKind) << "Check failed: (" #cond << ") is false: "
```

`TVM_FFI_PREDICT_FALSE` 是分支预测提示（GCC/Clang 的 `__builtin_expect`，MSVC 的空实现），告知编译器条件为假是冷路径。

使用示例：

```cpp
TVM_FFI_CHECK(ptr != nullptr, ValueError)
    << "Pointer must not be null";
```

展开后的逻辑：

```cpp
if (__builtin_expect(!(ptr != nullptr), 0))
  ErrorBuilder("ValueError", backtrace, 0).stream()
    << "Check failed: (" "ptr != nullptr" ") is false: "
    << "Pointer must not be null";
```

### 二元比较检查宏

`TVM_FFI_CHECK_BINARY_OP` 宏（`error.h:466-469`）处理比较操作：

```cpp
#define TVM_FFI_CHECK_BINARY_OP(name, op, x, y, ErrorKind)                \
  if (auto __tvm_ffi_log_err =                                             \
      ::tvm::ffi::details::LogCheck##name(x, y))                          \
  TVM_FFI_THROW(ErrorKind) << "Check failed: " << #x " " #op " " #y       \
                           << *__tvm_ffi_log_err << ": "
```

六个标准比较宏：

```cpp
#define TVM_FFI_CHECK_LT(x, y, ErrorKind) TVM_FFI_CHECK_BINARY_OP(_LT, <, x, y, ErrorKind)
#define TVM_FFI_CHECK_GT(x, y, ErrorKind) TVM_FFI_CHECK_BINARY_OP(_GT, >, x, y, ErrorKind)
#define TVM_FFI_CHECK_LE(x, y, ErrorKind) TVM_FFI_CHECK_BINARY_OP(_LE, <=, x, y, ErrorKind)
#define TVM_FFI_CHECK_GE(x, y, ErrorKind) TVM_FFI_CHECK_BINARY_OP(_GE, >=, x, y, ErrorKind)
#define TVM_FFI_CHECK_EQ(x, y, ErrorKind) TVM_FFI_CHECK_BINARY_OP(_EQ, ==, x, y, ErrorKind)
#define TVM_FFI_CHECK_NE(x, y, ErrorKind) TVM_FFI_CHECK_BINARY_OP(_NE, !=, x, y, ErrorKind)
```

### LogCheck 模板函数

`LogCheck##name` 模板函数（`error.h:431-439`）执行比较并返回格式化消息：

```cpp
#define TVM_FFI_CHECK_FUNC(name, op)                                       \
  template <typename X, typename Y>                                        \
  TVM_FFI_INLINE std::unique_ptr<std::string> LogCheck##name(              \
      const X& x, const Y& y) {                                           \
    if (x op y) return nullptr;                                            \
    return LogCheckFormat(x, y);                                          \
  }                                                                        \
  TVM_FFI_INLINE std::unique_ptr<std::string> LogCheck##name(              \
      int x, int y) {                                                      \
    return LogCheck##name<int, int>(x, y);                                \
  }
```

当条件满足时返回 `nullptr`（检查通过，宏中的 `if` 不进入错误路径）；失败时返回格式化的 `" (x vs. y) "` 字符串。使用 `std::unique_ptr<std::string>` 而非 `bool` 的原因是：需要在失败时携带比较值的格式化字符串，而 `nullptr` 隐式转换为 false 使 `if` 条件成立。

`LogCheckFormat`（`error.h:424-429`）格式化两个操作数：

```cpp
template <typename X, typename Y>
TVM_FFI_INLINE std::unique_ptr<std::string> LogCheckFormat(
    const X& x, const Y& y) {
  std::ostringstream os;
  os << " (" << x << " vs. " << y << ") ";
  return std::make_unique<std::string>(os.str());
}
```

### NOTNULL 检查

`TVM_FFI_CHECK_NOTNULL`（`error.h:481-483`）检查指针非空并返回指针本身：

```cpp
#define TVM_FFI_CHECK_NOTNULL(x, ErrorKind)                                \
  ((x) == nullptr ? TVM_FFI_THROW(ErrorKind) << "Check not null: " #x << ' ', \
   (x) : (x))
```

这是一个表达式（非语句），可以在赋值中使用：

```cpp
auto* ptr = TVM_FFI_CHECK_NOTNULL(GetPointer(), ValueError);
```

使用逗号表达式确保即使抛出路径也能正确返回值（虽然抛出路径不会真正返回）。

### ICHECK 系列：内部断言

`TVM_FFI_ICHECK` 系列（`error.h:485-492`）固定使用 `InternalError`：

```cpp
#define TVM_FFI_ICHECK(x) TVM_FFI_CHECK(x, InternalError)
#define TVM_FFI_ICHECK_LT(x, y) TVM_FFI_CHECK_LT(x, y, InternalError)
#define TVM_FFI_ICHECK_GT(x, y) TVM_FFI_CHECK_GT(x, y, InternalError)
#define TVM_FFI_ICHECK_LE(x, y) TVM_FFI_CHECK_LE(x, y, InternalError)
#define TVM_FFI_ICHECK_GE(x, y) TVM_FFI_CHECK_GE(x, y, InternalError)
#define TVM_FFI_ICHECK_EQ(x, y) TVM_FFI_CHECK_EQ(x, y, InternalError)
#define TVM_FFI_ICHECK_NE(x, y) TVM_FFI_CHECK_NE(x, y, InternalError)
#define TVM_FFI_ICHECK_NOTNULL(x) TVM_FFI_CHECK_NOTNULL(x, InternalError)
```

ICHECK 用于内部不变量检查——失败表示程序 bug，而非用户输入错误。

### DCHECK 系列：调试断言

`TVM_FFI_DCHECK` 系列（`error.h:495-520`）在 Debug 构建中与 ICHECK 相同，在 Release 构建（`NDEBUG` 定义）中被消除：

```cpp
#ifndef NDEBUG
#define TVM_FFI_DCHECK(x) TVM_FFI_ICHECK(x)
// ...
#else
#define TVM_FFI_DCHECK(x) \
  while (false) TVM_FFI_ICHECK(x)
// ...
#define TVM_FFI_DCHECK_NOTNULL(x) (x)
#endif
```

Release 模式下，`while (false)` 确保宏后的 `<<` 消息不会被编译（不可达代码），但编译器仍会进行语法检查。`DCHECK_NOTNULL` 直接返回参数，不进行检查。

### 编译器警告处理

比较宏在不同编译器上可能产生有符号/无符号比较警告。代码使用 pragma 包装（`error.h:444-463`）：

```cpp
#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
#elif defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable : 4389)
#endif

TVM_FFI_CHECK_FUNC(_LT, <)
// ... 所有比较函数 ...

#if defined(__GNUC__) || defined(__clang__)
#pragma GCC diagnostic pop
#elif defined(_MSC_VER)
#pragma warning(pop)
#endif
```

`int` 重载版本（`error.h:437-439`）为常见的 int 比较提供非模板实例化，避免某些编译器在模板实例化时产生警告。

## TVM_FFI_VISIT_THROW 与 ErrorBuilder 的五参构造

`TVM_FFI_VISIT_THROW` 宏使用 ErrorBuilder 的五参构造函数，传入 `extra_context`：

```cpp
#define TVM_FFI_VISIT_THROW(ErrorKind, node)                                \
  ::tvm::ffi::details::ErrorBuilder(                                        \
      #ErrorKind, TVMFFIBacktrace(__FILE__, __LINE__, TVM_FFI_FUNC_SIG, 0), \
      TVM_FFI_ALWAYS_LOG_BEFORE_THROW, ::std::nullopt,                      \
      ::std::optional<::tvm::ffi::ObjectRef>(                               \
          ::tvm::ffi::details::MakeVisitErrorContext(node)))                \
      .stream()
```

`cause_chain` 参数传 `std::nullopt`，`extra_context` 传 `VisitErrorContext`。这展示了 ErrorBuilder 支持携带完整错误上下文的能力。

## 避免 GLOG 宏冲突

源码注释（`error.h:419-420`）说明了命名决策：

> NOTE: we explicitly avoid glog style generic macros (LOG/CHECK) in tvm ffi to avoid potential conflict of downstream users who might have their own GLOG style macros

所有宏都使用 `TVM_FFI_` 前缀（`TVM_FFI_CHECK`、`TVM_FFI_THROW`、`TVM_FFI_ICHECK`），避免与下游项目的 GLOG 或其他日志库的 `CHECK`/`LOG` 宏冲突。

## 设计分析

ErrorBuilder 的析构抛出模式是 C++ 中"作用域守卫"（Scope Guard）惯用法的变体。它利用了 C++ 标准保证的临时对象析构时机（完整表达式结束时），将"构造 → 流式拼接 → 析构抛出"映射为自然的 `THROW(Type) << "msg"` 语法。

这种设计相比函数调用式 API（如 `ThrowError("ValueError", "msg")`）的优势在于：

1. **类型安全的流式拼接**：`<<` 操作符自动处理任意可流输出类型，不需要模板变参函数。
2. **惰性求值**：消息格式化仅在错误发生时进行。`if (condition) THROW() << expensive_msg;` 中的 `expensive_msg` 只在条件为真时求值。
3. **代码位置准确**：宏在调用点展开，`__FILE__`/`__LINE__`/`__PRETTY_FUNCTION__` 精确指向抛出位置。

断言宏的 `PREDICT_FALSE` 提示和 `COLD_CODE` 标记体现了对性能的关注。正常路径（断言通过）仅包含一个条件分支，且被提示为很可能为真；错误路径的代码（ErrorBuilder 构造、回溯捕获、字符串拼接、异常抛出）被编译器放置在远离热路径的代码段。DCHECK 在 Release 中的完全消除进一步确保零开销。

比较检查宏返回 `unique_ptr<string>` 而非 `bool` 的设计，在类型安全和信息丰富性之间取得了平衡：通过 `nullptr` 表示成功避免了不必要的字符串分配，失败时提供格式化的操作数值用于错误消息。int 重载版本则展示了对实际使用模式的优化——大多数断言涉及整数比较。

## 相关概念

- [077 Error 类与 std::exception 集成](077-error-class-exception-integration.md)：ErrorBuilder 构造并抛出的 Error 对象
- [079 TVMFFIBacktrace 栈回溯捕获](079-backtrace-capture.md)：TVM_FFI_THROW 中回溯的捕获机制
- [082 额外错误上下文 extra_context](082-error-extra-context.md)：VISIT_THROW 中 extra_context 的使用
- [081 错误因果链 cause_chain](081-error-cause-chain.md)：ErrorBuilder 对 cause_chain 的支持
- [014 错误处理与异常安全](/01-architecture/concepts/014-error-handling-exception-safety.md)：断言宏在异常安全体系中的作用
