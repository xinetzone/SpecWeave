# C++ IIFE+AssertHelper 流式断言宏封装最佳实践

> **Pattern ID**: cpp-iife-assertion-macro
> **Category**: code-patterns / C++ 宏封装
> **Status**: ✅ Production-ready
> **Source**: caffe-ffi 测试框架流式断言改造（2026-08-01）
> **验证**: MSVC 2022 / C++17 零警告编译，14 项独立单元测试全通过，196 项集成测试全通过

---

## 1. 问题背景

在 C++ 项目中编写自定义断言/检查宏时，经典的 `do { } while(0)` 模式存在一个根本缺陷：**无法支持 `<< "message"` 流式消息追加**。

```cpp
// ❌ 经典 do-while 模式：无法支持 << 流式消息
#define EXPECT_EQ(a, b) \
  do { \
    if ((a) != (b)) { \
      std::cerr << "Expected equality failed\n"; \
    } \
  } while(0)

// 用法：无法做到 EXPECT_EQ(x, 0) << "x should be zero, got " << x;
// 因为 do-while 是语句，不是表达式，不能返回临时对象
```

而在测试框架和生产代码的 CHECK 宏中，流式追加上下文消息是刚需（类似 gtest 的 `EXPECT_EQ(a,b) << "context"`）。

---

## 2. 核心模式：IIFE + AssertHelper

### 2.1 模式结构

```
宏展开为立即调用的 lambda 表达式（IIFE）
  → lambda 返回 AssertHelper 临时对象
    → AssertHelper 在析构时（失败状态下）抛出异常
      → operator<< 可以链式追加消息到 AssertHelper 的 ostringstream
```

### 2.2 为什么 IIFE 能解决问题

| 特性 | `do { } while(0)` | IIFE `[&]() -> T { ... }()` |
|------|-------------------|------------------------------|
| 语法类别 | 语句（statement） | 表达式（expression） |
| 返回值 | ❌ 无法返回对象 | ✅ 返回 AssertHelper 临时对象 |
| `<<` 链式调用 | ❌ 不支持 | ✅ 天然支持 |
| dangling-else | ✅ 通过 do-while 避免 | ✅ 表达式天然避免 |
| 变量作用域 | ✅ 块级隔离 | ✅ lambda 作用域隔离 |
| C++ 版本要求 | 无 | C++11+（lambda 支持） |

---

## 3. 完整实现模板

### 3.1 AssertHelper 类

```cpp
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>

class AssertHelper {
 public:
  explicit AssertHelper(bool failed) : failed_(failed) {}
  AssertHelper(bool failed, std::string msg) : failed_(failed), msg_(std::move(msg)) {}

  ~AssertHelper() noexcept(false) {
    if (failed_) {
      throw std::runtime_error(msg_ + oss_.str());
    }
  }

  // 禁止拷贝，允许移动（MSVC 下 ostringstream 不可拷贝，必须提供移动构造）
  AssertHelper(const AssertHelper&) = delete;
  AssertHelper& operator=(const AssertHelper&) = delete;
  AssertHelper& operator=(AssertHelper&&) = delete;
  AssertHelper(AssertHelper&& other) noexcept
      : failed_(other.failed_),
        msg_(std::move(other.msg_)),
        oss_(std::move(other.oss_)) {
    other.failed_ = false;  // 源对象标记为不抛异常
  }

  // 流式追加任意类型
  template <typename T>
  AssertHelper& operator<<(const T& val) {
    if (failed_) oss_ << val;
    return *this;
  }

  // 支持流式操作符（如 std::endl, std::hex）
  AssertHelper& operator<<(std::ostream& (*manip)(std::ostream&)) {
    if (failed_) oss_ << manip;
    return *this;
  }

 private:
  bool failed_;
  std::string msg_;
  std::ostringstream oss_;
};
```

### 3.2 基础检查宏（CHECK）

```cpp
#define LOC_MSG __FILE__ ":" + std::to_string(__LINE__)

#define MY_CHECK(cond) \
  [&]() -> AssertHelper { \
    if (cond) return AssertHelper(false); \
    return AssertHelper(true, \
        std::string("CHECK failed: ") + #cond + " at " + LOC_MSG); \
  }()
```

### 3.3 二元比较宏（CHECK_EQ/CHECK_NE/CHECK_LT 等）

```cpp
namespace detail {

template <typename A, typename B>
AssertHelper CmpEq(bool failed, const A& a, const B& b, const char* expr) {
  if (!failed) return AssertHelper(false);
  std::ostringstream oss;
  oss << "Expected equality: " << expr << "\n"
      << "  Left:  " << a << "\n"
      << "  Right: " << b;
  return AssertHelper(true, oss.str());
}

}  // namespace detail

#define MY_CHECK_EQ(a, b) \
  [&]() -> AssertHelper { \
    return ::detail::CmpEq((a) == (b), (a), (b), #a " == " #b); \
  }()
```

### 3.4 自定义消息宏

```cpp
#define MY_CHECK_MSG(cond, msg) \
  [&]() -> AssertHelper { \
    if (cond) return AssertHelper(false); \
    return AssertHelper(true, \
        std::string("CHECK failed: ") + #cond + " (" + msg + ") at " + LOC_MSG); \
  }()
```

---

## 4. 使用方式

```cpp
void ProcessTensor(const Tensor& t, int expected_channels) {
  MY_CHECK(t.data() != nullptr) << "Tensor data is null for shape " << t.shape();

  MY_CHECK_EQ(t.channels(), expected_channels)
      << " for tensor name=" << t.name();

  MY_CHECK(t.shape().size() >= 2) << " expected at least 2D tensor";

  // ... 业务逻辑
}
```

输出示例（断言失败时）：

```
terminate called after throwing an instance of 'std::runtime_error'
  what():  Expected equality: t.channels() == expected_channels
  Left:  3
  Right: 64
 for tensor name=conv1_weight
```

---

## 5. 关键设计要点

### 5.1 必须提供移动构造函数（GOTCHA #1）

**陷阱**：lambda 中 `return AssertHelper(true, msg)` 会触发移动/拷贝构造。MSVC 下 `std::ostringstream` 不可拷贝，如果类不提供移动构造函数，编译报错：

```
error C2280: AssertHelper::AssertHelper(const AssertHelper&): attempting to reference a deleted function
```

**解决方案**：显式提供移动构造函数，移动 `oss_` 和 `msg_`，并将源对象的 `failed_` 设为 `false`（防止源对象析构时也抛异常——双重异常会导致 `std::terminate`）。

### 5.2 析构函数必须标记 `noexcept(false)`（GOTCHA #2）

**陷阱**：C++11 起，析构函数默认 `noexcept(true)`。在析构函数中抛出异常会直接调用 `std::terminate()`。

**解决方案**：析构函数必须显式标记 `noexcept(false)`。

### 5.3 lambda 使用 `[&]` 按引用捕获（GOTCHA #3）

**陷阱**：使用 `[=]` 按值捕获可能导致大对象拷贝开销，且在某些编译器下可能引入悬垂引用。使用 `[]` 不捕获则无法访问局部变量。

**解决方案**：统一使用 `[&]` 按引用捕获。宏在语句结束时立即执行 lambda，不存在引用悬垂问题。

### 5.4 宏参数必须加括号（GOTCHA #4）

**陷阱**：宏中直接使用 `(a) == (b)` 而非 `a == b`，避免运算符优先级问题。例如 `CHECK_EQ(x & mask, 0)` 如果不加括号会被解析为 `x & (mask == 0)`。

**解决方案**：宏体内所有参数引用处必须用括号包裹：`(a) == (b)`、`(a) < (b)` 等。

### 5.5 内部辅助宏避免重定义（GOTCHA #5）

**陷阱**：如果直接 `#define CHECK_EQ(...) ...`，在同一个翻译单元中可能与其他头文件的同名宏冲突，产生 C4005 重定义警告。

**解决方案**：
- 公共宏名保持简洁（`CHECK_EQ`），内部实现宏用前缀（`AH_CHECK_EQ_`）
- 公共宏作为别名指向内部宏：`#define CHECK_EQ AH_CHECK_EQ_`
- 若要支持前缀定制（通用库场景），使用两阶段宏拼接：

```cpp
#define AH_CONCAT_(a, b) a##b
#define AH_CONCAT(a, b) AH_CONCAT_(a, b)

#ifndef ASSERT_MACRO_PREFIX
#define ASSERT_MACRO_PREFIX MY
#endif

// 这样最终宏名为 MY_CHECK, MY_CHECK_EQ 等
#define AH_CHECK_NAME(name) AH_CONCAT(ASSERT_MACRO_PREFIX, _##name)
```

---

## 6. 不适用场景

| 场景 | 原因 | 替代方案 |
|------|------|----------|
| 性能关键热路径（每次调用都构造 ostringstream） | ostringstream 有堆分配开销 | 使用 `if (!cond) __builtin_trap()` 或 `assert()` |
| 不可抛异常的环境（嵌入式、信号处理、noexcept 函数） | 析构抛异常会 terminate | 返回错误码或使用断言宏直接 abort |
| 需要在失败后继续执行（非致命检查） | AssertHelper 析构即抛，无法继续 | 使用 EXPECT 模式（返回 bool + 记录日志而非抛异常） |
| C++03 或更早版本 | 不支持 lambda | 退回 do-while 模式，放弃流式消息 |

---

## 7. 与 gtest ASSERT/EXPECT 的对比

| 特性 | gtest ASSERT_* | 本模式 CHECK_* |
|------|---------------|----------------|
| 流式消息 | ✅ `<< "msg"` | ✅ `<< "msg"` |
| 失败行为 | 返回（fatal）/继续（non-fatal） | 抛异常 |
| 依赖 | gtest 框架（~1MB+ 编译开销） | 仅标准库（header-only，~200行） |
| 适用范围 | 单元测试 | 生产代码 + 测试 |
| 异常安全 | 非异常机制（setjmp/longjmp 或 return） | C++ 异常 |
| 可移植性 | 高 | C++11+ |

---

## 8. 完整测试验证

以下 14 个测试场景必须全部通过，方可确认宏实现正确：

1. ✅ CHECK 真条件不抛异常
2. ✅ CHECK 假条件抛出异常，异常消息包含 `__FILE__:__LINE__`
3. ✅ CHECK << "message" 流式消息正确追加
4. ✅ CHECK_EQ 整数相等通过
5. ✅ CHECK_EQ 不等时抛出异常，异常消息包含左右值
6. ✅ CHECK_NE 不等通过，相等时抛异常
7. ✅ CHECK_LT / CHECK_LE / CHECK_GT / CHECK_GE 比较正确
8. ✅ CHECK_NEAR 浮点数近似比较（epsilon 控制）
9. ✅ CHECK_NOTNULL 非空指针通过，空指针抛异常
10. ✅ CHECK_THROW 正确捕获指定类型异常
11. ✅ CHECK_MSG 自定义消息正确显示
12. ✅ CHECK_EQ 浮点数比较
13. ✅ CHECK_NEAR epsilon 边界值正确
14. ✅ 失败异常消息包含文件名和行号

---

## 9. 参考实现

本模式的生产级通用实现位于：
- [assert_helper.hpp](../../../../scripts/include/assert_helper.hpp) — SpecWeave 通用版（可直接 copy 到其他项目）

使用示例：
```cpp
#include "assert_helper.hpp"

void Foo(int x) {
  CHECK(x > 0) << "x must be positive, got " << x;
  CHECK_EQ(x % 2, 0) << "x must be even";
  CHECK_NEAR(x * 0.1, 1.0, 1e-6);
}
```
