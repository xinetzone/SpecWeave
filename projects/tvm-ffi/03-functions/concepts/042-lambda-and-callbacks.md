---
type: Concept
title: "视角042：Lambda 与回调"
description: "分析 TVM FFI 如何将 C++ lambda、函数对象和 std::function 转换为 Function：FromTyped/FromPacked 工厂方法、FunctionObjImpl 模板、类型推导与参数解包机制。"
tags:
  - function
  - lambda
  - callback
  - template-metaprogramming
  - type-deduction
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-140, F-150
  - code:
    - include/tvm/ffi/function.h
    - src/ffi/function.cc
---

# 视角042：Lambda 与回调

## 概述

TVM FFI 提供了从任意 C++ 可调用对象（lambda、函数指针、`std::function`、自定义函数对象）创建 `Function` 的能力。这一机制的核心是 `Function::FromTyped` 和 `Function::FromPacked` 两个工厂方法，它们通过模板元编程自动推导函数签名、生成参数解包代码，并将类型化的调用适配到类型擦除的 Packed Function 约定。这使得开发者可以用自然的 C++ 语法编写函数，零样板地注册到 FFI 系统。

## FromTyped：类型化函数的工厂

### 基本用法

`Function::FromTyped`（`function.h:536-545`）接受一个具有明确签名的可调用对象：

```cpp
template <typename TCallable>
static Function FromTyped(TCallable&& callable) {
  using FuncInfo = details::FunctionInfo<std::decay_t<TCallable>>;
  auto call_packed = [callable = std::forward<TCallable>(callable)](
                         const AnyView* args, int32_t num_args, Any* rv) mutable -> void {
    details::unpack_call<typename FuncInfo::RetType>(
        std::make_index_sequence<FuncInfo::num_args>{},
        nullptr, callable, args, num_args, rv);
  };
  return FromPackedInternal(std::move(call_packed));
}
```

执行流程：

1. **签名推导**：`FunctionInfo<TCallable>` 萃取返回类型 `RetType` 和参数数量 `num_args`。
2. **Packed 适配**：创建一个 lambda，将 `const AnyView*` 类型擦除参数转换为类型化参数。
3. **参数解包**：`unpack_call` 通过索引序列在编译期展开参数，逐个从 `AnyView` 转换为目标类型。
4. **对象构造**：`FromPackedInternal` 创建 `FunctionObjImpl` 存储适配后的 lambda。

### 带名称的重载

`FromTyped` 还有一个接受名称的重载（`function.h:553-562`），用于在错误信息中提供函数名：

```cpp
template <typename TCallable>
static Function FromTyped(TCallable&& callable, std::string name) {
  using FuncInfo = details::FunctionInfo<std::decay_t<TCallable>>;
  auto call_packed = [callable = ..., name = std::move(name)](
                         const AnyView* args, int32_t num_args, Any* rv) mutable {
    details::unpack_call<typename FuncInfo::RetType>(
        std::make_index_sequence<FuncInfo::num_args>{},
        &name, callable, args, num_args, rv);
  };
  return FromPackedInternal(std::move(call_packed));
}
```

当参数类型不匹配时，错误信息会包含函数名，便于调试。

## FromPacked：Packed 格式函数

`Function::FromPacked`（`function.h:341-356`）接受已经是 Packed 格式的函数：

```cpp
template <typename TCallable>
static Function FromPacked(TCallable&& packed_call) {
  static_assert(
      std::is_convertible_v<TCallable,
          std::function<void(const AnyView*, int32_t, Any*)>> ||
      std::is_convertible_v<TCallable,
          std::function<void(PackedArgs args, Any*)>>,
      "tvm::ffi::Function::FromPacked requires input function signature "
      "to match packed func format");
  // ...
}
```

它支持两种 Packed 签名：

1. `void(const AnyView* args, int32_t num_args, Any* result)`：原始格式
2. `void(PackedArgs args, Any* result)`：使用 `PackedArgs` 封装的格式

第二种更符合人体工程学，函数体可以通过 `args[i]` 访问参数。

## FunctionObjImpl：可调用对象的存储

### 模板类定义

`FunctionObjImpl<TCallable>`（`function.h:159-200`）是存储实际 C++ 可调用对象的函数对象类：

```cpp
template <typename TCallable>
class FunctionObjImpl : public FunctionObj {
 public:
  explicit FunctionObjImpl(Args&&... args)
      : callable_(std::forward<Args>(args)...) {
    this->safe_call = SafeCall;
    this->cpp_call = reinterpret_cast<void*>(CppCall);
  }

  TCallable* GetCallable() { return &callable_; }

 private:
  static void CppCall(const FunctionObj* func, const AnyView* args,
                      int32_t num_args, Any* result) {
    (static_cast<const TSelf*>(func))->callable_(args, num_args, result);
  }

  static int SafeCall(void* func, const TVMFFIAny* args,
                      int32_t num_args, TVMFFIAny* result) {
    TVM_FFI_SAFE_CALL_BEGIN();
    FunctionObj* self = static_cast<FunctionObj*>(func);
    reinterpret_cast<FCall>(self->cpp_call)(
        self, reinterpret_cast<const AnyView*>(args),
        num_args, reinterpret_cast<Any*>(result));
    TVM_FFI_SAFE_CALL_END();
  }

  mutable TCallable callable_;
};
```

关键设计：

1. **值捕获**：`callable_` 按值存储可调用对象，lambda 的捕获数据在函数对象生命周期内有效。
2. **双指针设置**：构造时同时设置 `cpp_call`（直接调用）和 `safe_call`（异常安全包装）。
3. **静态函数指针**：`CppCall` 和 `SafeCall` 是静态方法，其地址可以作为 C ABI 函数指针使用。
4. **`mutable` 修饰**：`callable_` 被声明为 `mutable`，允许在 `const` 方法中修改 lambda 的状态（如 `mutable` lambda）。

### FromPackedInplace：原地构造

`FromPackedInplace`（`function.h:369-379`）提供了更高效的构造方式，直接在函数对象内存中原地构造可调用对象：

```cpp
template <typename TCallable, typename... Args>
static auto FromPackedInplace(Args&&... args) {
  using ObjType = details::FunctionObjImpl<TCallable>;
  Function func;
  auto obj_ptr = make_object<ObjType>(std::forward<Args>(args)...);
  auto* call_ptr = obj_ptr->GetCallable();
  func.data_ = std::move(obj_ptr);
  return std::make_tuple(std::move(func), call_ptr);
}
```

返回 `(Function, TCallable*)` 元组，允许调用方在函数注册后仍能访问内部的可调用对象。这在需要设置回调状态或建立反向引用时非常有用。

## TypedFunction：类型安全包装

`TypedFunction<R(Args...)>`（`function.h:769`）提供了比 `Function` 更强的类型安全保证：

```cpp
TypedFunction<int(int)> addone = [](int x) -> int { return x + 1; };
int y = addone(1);  // 编译期类型检查
ffi::Function packed = addone;  // 隐式转换为类型擦除函数
```

它内部持有一个 `Function`，但在调用时自动进行类型转换。`TypeTraits` 特化确保 `TypedFunction` 也能存入 `Any`，运行时表现为普通 `Function`。

## GlobalDef：注册 Lambda 为全局函数

`reflection::GlobalDef::def`（`reflection/registry.h:536-541`）是注册 lambda 最便捷的方式：

```cpp
refl::GlobalDef()
    .def("my_module.add", [](int a, int b) { return a + b; })
    .def("my_module.greet", [](const String& name) -> String {
      return "Hello, " + name;
    });
```

`def` 方法内部调用 `Function::FromTyped`，自动推导函数签名并生成类型 schema 元数据。

## NPU 建议

在 NPU（神经网络处理单元）加速场景中，Lambda 与回调机制可用于以下场景：

1. **算子注册**：NPU 厂商可通过 lambda 将自定义算子实现注册为全局函数，例如 `refl::GlobalDef().def("npu.matmul", [](Tensor a, Tensor b, Tensor out) { ... })`。lambda 可以捕获 NPU 设备句柄、命令队列等资源，但需注意捕获对象的线程安全性——`GlobalFunctionTable` 的更新假设在初始化阶段单线程完成。

2. **异步回调**：NPU 异步执行完成后的通知回调可通过 `Function::FromPacked` 创建并传递给 NPU 运行时。建议使用 `FromPackedInplace` 在函数对象中存储 `std::promise` 或事件句柄，避免额外的堆分配。回调中应避免抛出 C++ 异常——如果回调从 NPU 驱动线程被调用，异常可能无法正确跨越 C ABI 边界。

3. **内核选择策略**：可将内核选择逻辑实现为 lambda 并注册为全局函数，接收张量形状和数据类型参数，返回最优内核配置。由于 `FunctionObjImpl` 按值捕获 lambda，选择策略中使用的查找表会随函数对象一起生命周期管理。

4. **注意事项**：
   - NPU 回调中避免执行耗时操作，应尽快返回以避免阻塞 NPU 命令队列。
   - 如果 lambda 捕获了 NPU 设备上下文指针，确保设备上下文的生命周期长于函数对象（可通过 `FromPackedInplace` 返回的指针设置反向引用）。
   - 跨线程调用时，`Function::operator()` 通过 `CallPacked` 走 `cpp_call` 快速路径，异常直接传播；从 NPU 驱动线程回调时应确保异常被 `safe_call` 捕获。

## 设计分析

Lambda 到 `Function` 的转换是模板元编程与类型擦除的经典结合。`FunctionInfo` 在编译期萃取签名，`unpack_call` 通过 `index_sequence` 展开参数，整个适配过程的开销被编译器内联优化消除。运行时，所有 lambda——无论捕获了多少状态——都归一化为同一组函数指针，体现了"编译期多态 → 运行时单态"的设计哲学。

`mutable TCallable callable_` 的设计允许有状态 lambda（如计数器、缓存）在多次调用间保持状态，但也要求开发者注意线程安全。`FromPackedInplace` 返回内部指针的设计为需要后初始化的场景提供了逃生舱，同时保持了默认路径的简洁性。

## 相关概念

- [036 Packed Function 约定](036-packed-function-convention.md)：lambda 转换的目标约定
- [041 函数一等公民](041-function-as-first-class-citizen.md)：Function 在对象系统中的地位
- [050 函数重载解析](050-function-overload-resolution.md)：FunctionInfo 的类型推导细节
- [040 全局函数注册表](040-global-function-registry.md)：GlobalDef 注册 API
