---
type: Concept
title: "视角043：参数传递约定"
description: "解析 TVM FFI 的参数传递机制：TVMFFIAny 联合体的内存布局、AnyView 非持有视图、PackedArgs 的栈上数组填充，以及基础类型与对象类型的不同传递策略。"
tags:
  - function
  - argument-passing
  - any-view
  - packed-args
  - memory-layout
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-022, F-144, F-145, F-146, F-147
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - include/tvm/ffi/any.h
---

# 视角043：参数传递约定

## 概述

TVM FFI 的函数调用通过类型擦除的参数数组传递所有参数。每个参数被序列化为一个 16 字节的 `TVMFFIAny` 值，调用方在栈上填充数组，被调用方通过 `AnyView` 或 `PackedArgs` 读取。这种约定消除了为不同函数签名生成桥接代码的需要，但也要求精确理解值类型与对象类型的不同传递策略、参数生命周期约束和栈上分配规则。

## TVMFFIAny：类型擦除的基础单元

### 联合体布局

`TVMFFIAny` 定义在 `c_api.h`，是一个 16 字节的联合体。其内存布局为：

```
偏移 0-3:   v_type_index (int32_t)   类型标签
偏移 4-7:   padding (int32_t)        对齐填充
偏移 8-15:  数据负载 (8 字节联合体)
```

数据负载可以是：

| 字段 | 类型 | 适用类型 |
|------|------|----------|
| `v_int64` | `int64_t` | 整数类型 |
| `v_uint64` | `uint64_t` | 无符号整数 |
| `v_float64` | `double` | 浮点类型 |
| `v_handle` | `void*` | 对象指针、句柄 |
| `v_dtype` | `TVMFFIDataType` | 数据类型描述符 |
| `v_device` | `TVMFFIDevice` | 设备描述符 |

### 小值优化（Small Value Optimization）

基础类型（int、float、bool、null）直接存储在 8 字节负载内，无需堆分配。对象类型（String、Array、Tensor、Function 等）则通过 `v_handle` 存储对象指针，对象的生命周期由引用计数管理。这意味着：

- 传递整数/浮点数是纯值拷贝，零堆分配。
- 传递对象仅拷贝指针，引用计数相应增减。
- `TVMFFIAny` 自身不管理对象生命周期——它是非持有视图。

## AnyView：非持有参数视图

`AnyView` 类（`any.h`）包装 `TVMFFIAny`，提供类型检查和转换方法：

```cpp
class AnyView {
 protected:
  TVMFFIAny value_;

 public:
  TVMFFITypeIndex type_index() const;
  bool IsNone() const;
  bool IsInt() const;
  bool IsFloat() const;
  bool IsObject() const;
  bool IsFunction() const;
  // ...

  template <typename T>
  T cast() const;

  template <typename T>
  std::optional<T> try_cast() const;
};
```

关键特性：

1. **非持有**：`AnyView` 不增加对象引用计数，其生命周期取决于底层数据的存活时间。
2. **类型查询**：通过 `type_index()` 和 `IsXxx()` 方法在运行时检查类型。
3. **显式转换**：`cast<T>()` 在类型不匹配时抛出异常，`try_cast<T>()` 返回 `std::optional<T>`。
4. **隐式转换运算符**：支持 `operator int()`、`operator double()`、`operator bool()`、`operator std::string()` 等。

## PackedArgs：参数集合封装

`PackedArgs`（`function.h:261-314`）是函数参数在 C++ 侧的主要表示：

```cpp
class PackedArgs {
 public:
  PackedArgs(const AnyView* data, int32_t size);

  int size() const;
  const AnyView* data() const;
  AnyView operator[](int i) const;

  PackedArgs Slice(int begin, int end = -1) const;

  template <typename... Args>
  static void Fill(AnyView* data, Args&&... args);

 private:
  const AnyView* data_;
  int32_t size_;
};
```

### 索引访问

`operator[]`（`function.h:294`）直接返回指定位置的 `AnyView`：

```cpp
AnyView operator[](int i) const { return data_[i]; }
```

这是零成本的——仅返回数组元素的副本（`AnyView` 本身 16 字节，按值返回）。被调用方通过链式调用 `args[i].cast<T>()` 获取类型化值。

### 参数切片

`Slice` 方法（`function.h:282-287`）支持参数子集传递，常用于方法绑定中跳过 `self` 参数：

```cpp
PackedArgs Slice(int begin, int end = -1) const {
  if (end == -1) end = size_;
  return PackedArgs(data_ + begin, end - begin);
}
```

### 栈上填充

`PackedArgs::Fill`（`function.h:305-307`）是调用侧的核心方法：

```cpp
template <typename... Args>
TVM_FFI_INLINE static void Fill(AnyView* data, Args&&... args) {
  details::for_each(details::PackedArgsSetter(data),
                    std::forward<Args>(args)...);
}
```

`PackedArgsSetter`（`function.h:240-254`）将每个参数赋值到数组的对应位置：

```cpp
class PackedArgsSetter {
 public:
  explicit PackedArgsSetter(AnyView* args) : args_(args) {}

  template <typename T>
  TVM_FFI_INLINE void operator()(size_t i, T&& value) const {
    args_[i].operator=(std::forward<T>(value));
  }

 private:
  AnyView* args_;
};
```

`AnyView::operator=` 通过 `TypeTraits<T>::CopyToAnyView` 将 C++ 类型序列化到 `TVMFFIAny`。对于对象类型，此操作会增加引用计数。

## 调用侧的参数数组分配

在 `Function::operator()`（`function.h:613-622`）中，参数数组在栈上分配：

```cpp
template <typename... Args>
TVM_FFI_INLINE Any operator()(Args&&... args) const {
  const int kNumArgs = sizeof...(Args);
  const int kArraySize = kNumArgs > 0 ? kNumArgs : 1;
  AnyView args_pack[kArraySize];
  PackedArgs::Fill(args_pack, std::forward<Args>(args)...);
  Any result;
  static_cast<FunctionObj*>(data_.get())
      ->CallPacked(args_pack, kNumArgs, &result);
  return result;
}
```

设计要点：

1. **栈上数组**：`AnyView args_pack[N]` 在调用栈上分配，无堆开销。
2. **零参数保护**：当 `sizeof...(Args) == 0` 时仍分配 1 个元素，避免 ISO C++ 禁止的零长数组。
3. **固定上限**：栈上数组大小在编译期确定，不支持运行时可变参数数量（但可通过 `CallPacked(const AnyView*, int32_t, Any*)` 手动传递动态数组）。
4. **结果也是栈上**：`Any result` 在栈上构造，调用完成后作为返回值移动。

## 参数生命周期约束

源码注释明确警告（`function.h:301-303`）：

> Caller must ensure all args are alive during lifetime of data. A common pitfall is to pass in local variables that are immediately destroyed after calling Fill.

具体约束：

1. **`PackedArgs::Fill` 后立即调用**：填充的 `AnyView` 数组引用了传入对象的数据，必须在所有被引用对象存活期间完成函数调用。
2. **字符串字面量安全**：`const char*` 字面量具有静态存储期，可安全使用。
3. **临时对象危险**：传入临时 `std::string` 时，`AnyView` 可能持有其内部指针，临时对象在完整表达式结束时销毁。但在 `operator()` 的同一完整表达式中，临时对象的生命周期持续到调用结束，因此通常是安全的。

## 基础类型与对象类型的传递差异

| 特性 | 基础类型（int/float/bool） | 对象类型（String/Array/Function） |
|------|---------------------------|----------------------------------|
| 存储方式 | 直接存入 `TVMFFIAny` 的 8 字节负载 | 通过 `v_handle` 存储对象指针 |
| 拷贝成本 | 8 字节值拷贝 | 8 字节指针拷贝 + 引用计数增减 |
| 生命周期 | 值语义，无需管理 | 引用计数自动管理 |
| 空值表示 | `kTVMFFITypeIndexNull` | 指针为 NULL |
| 类型检查 | `IsInt()`/`IsFloat()`/`IsBool()` | `IsObject()` + 类型索引检查 |

## 设计分析

参数传递约定的核心权衡是**统一表示与性能的平衡**。所有参数归一化为 16 字节的 `TVMFFIAny`，使得函数签名可以在运行时动态构建，无需编译期代码生成。栈上数组分配和小值优化确保了常见调用场景（少量基础类型参数）的零堆分配性能。

`AnyView` 的非持有设计是关键的性能决策——它避免了在参数传递路径上频繁增减引用计数，但要求严格的生命周期约束。`PackedArgs` 在 `AnyView` 之上提供了最小的便利封装，同时保持零开销。

## 相关概念

- [036 Packed Function 约定](036-packed-function-convention.md)：参数传递的总体约定
- [038 safe_call 与 cpp_call 双路径](038-safe-call-and-cpp-call.md)：参数在两条路径上的传递
- [044 返回值约定](044-return-value-convention.md)：返回值的处理方式
- [042 Lambda 与回调](042-lambda-and-callbacks.md)：lambda 参数的解包机制
