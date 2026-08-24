---
type: Concept
title: "视角010：函数注册表"
description: "分析 TVM FFI 的全局函数注册表设计：Function 对象的生命周期、全局名称空间管理、函数注册/查找/枚举 API、跨语言函数互调，以及注册表在模块系统中的作用。"
tags:
  - architecture
  - function-registry
  - global-functions
  - cross-language
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-305, F-306, F-307, F-308, F-309, F-310
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - include/tvm/ffi/registry.h
---

# 视角010：函数注册表

## 概述

全局函数注册表是 TVM FFI 的中枢神经系统，提供了一个统一的、跨语言的函数名称空间。所有语言（C++、Python、Rust 等）注册的函数都进入同一个全局表，可以通过名称被任意语言查找和调用。本视角分析注册表的数据结构、API 设计、线程安全策略以及在模块系统中的作用。

## Function 对象

### 函数作为一等对象

在 TVM FFI 中，函数是一等公民。`Function` 类（`function.h:320`）继承自 `ObjectRef`，类型索引为 `kTVMFFIFunction = 68`。这意味着函数可以：

- 存储在 `Any` 中作为参数传递
- 存储在 `Array`/`Map`/`List`/`Dict` 容器中
- 作为另一个函数的返回值
- 通过引用计数管理生命周期
- 被任意语言绑定调用

### TVMFFIFunctionCell

函数对象的核心是 `TVMFFIFunctionCell`（`c_api.h:509`），包含两个函数指针：

- `safe_call`：C ABI 安全路径，捕获 C++ 异常并返回错误码。
- `cpp_call`：C++ 快速路径，异常直接传播。

函数对象在 `TVMFFIObject` 头部之后嵌入 `TVMFFIFunctionCell`，额外的资源句柄（如 lambda 捕获的上下文）存储在单元之后。

### 函数创建

- **`TVMFFIFunctionCreate`**（`c_api.h:719`）：从资源句柄和 `TVMFFISafeCallType` 函数指针创建函数对象。
- **`Function::FromPacked`**（`function.h:341`）：从 C++ 可调用对象（lambda、std::function）创建函数，自动管理捕获上下文的生命周期。
- **`Function::FromExternC`**（`function.h:392`）：从 C 函数指针和资源句柄创建函数。
- C++ 层的 `Function::FromPacked` 提供类型安全的工厂方法。

## 注册表 C API

### 核心注册接口

```c
int TVMFFIFunctionSetGlobal(const TVMFFIByteArray* name,
                            TVMFFIObjectHandle f,
                            int32_t override);
```

- `name`：函数名称（字节数组形式），通常使用点分隔的命名空间（如 `"tvm.ir.module"`）。
- `f`：函数对象句柄，通过 `TVMFFIFunctionCreate` 创建。
- `override`：是否覆盖已存在的同名函数。非零时覆盖，为零时若已存在则返回错误。

### 查找接口

```c
int TVMFFIFunctionGetGlobal(const TVMFFIByteArray* name,
                            TVMFFIObjectHandle* out);
```

按名称查找函数。找到时返回函数句柄（增加引用计数），未找到时返回非零错误码，`out` 设为 NULL。

### 枚举接口

C++ 层提供 `Function::ListGlobalNames()`（`function.h:511`），内部调用注册为 `"ffi.FunctionListGlobalNamesFunctor"` 的全局函数，返回 `std::vector<String>`。C ABI 层没有直接的枚举函数，枚举能力通过全局函数机制实现，保持核心 ABI 精简。

### 移除接口

函数可以通过注册 NULL 或调用专门的移除接口从全局表中删除。模块卸载时自动清理其注册的函数。

## C++ 注册表 API

### Function 类静态方法

`Function` 类提供了注册表的 C++ 封装：

- `static std::optional<Function> GetGlobal(std::string_view name)`（`function.h:409`）：查找全局函数，不存在时返回 `std::nullopt`。
- `static Function GetGlobalRequired(std::string_view name)`（`function.h:456`）：查找全局函数，不存在时抛出异常。
- `static void SetGlobal(std::string_view name, Function f, bool override = false)`（`function.h:499`）：注册函数。
- `static std::vector<String> ListGlobalNames()`（`function.h:511`）：枚举名称。

### 注册宏

C++ 提供便捷的注册宏：

- 通过 `TVM_FFI_STATIC_INIT_BLOCK()`（base_details.h:164）+ `refl::GlobalDef().def_packed(name, func)` 在静态初始化阶段注册函数。
- 静态初始化块在 `main()` 之前执行，将可调用对象写入全局表。

### TypedFunction

`TypedFunction<R(Args...)>`（`function.h:769`）为 `Function` 提供编译期类型检查：

- 自动将 `PackedArgs` 中的 `AnyView` 转换为具体参数类型。
- 自动将返回值包装为 `Any`。
- 支持 lambda 捕获和类型推导。

## 跨语言函数互调

注册表是跨语言互操作的关键桥梁：

### C++ 注册 → Python 调用

```
C++: TVM_FFI_REGISTER_GLOBAL_FUNC("my.add")([](int a, int b) { return a + b; });
Python: f = tvm.ffi.get_global_func("my.add"); result = f(1, 2)
```

### Python 注册 → C++ 调用

```
Python: @tvm.ffi.register_func("my.py_func")
        def my_func(x): return x * 2
C++: auto f = Function::GetGlobal("my.py_func"); int result = f(21).cast<int>();
```

### 函数作为参数传递

高阶函数（接受函数作为参数的函数）通过注册表实现解耦：

```c++
// C++ 注册一个接受回调的函数
TVM_FFI_STATIC_INIT_BLOCK() {
  refl::GlobalDef().def_packed("my.apply", [](Function fn, int x) {
    return fn(x);
  });
}
```

```python
# Python 传入 Python 函数作为回调
result = tvm.ffi.get_global_func("my.apply")(lambda x: x + 1, 41)
```

## 线程安全

全局注册表的实现需要考虑多线程并发访问：

- **注册操作**：使用互斥锁保护内部哈希表，支持运行时动态注册。
- **查找操作**：使用读写锁或原子指针，允许并发读取。
- **函数调用**：注册表本身不参与函数调用过程，一旦获取 `Function` 对象，调用是无锁的（线程安全由函数自身保证）。

## 命名空间约定

全局函数名称遵循点分隔的命名空间约定：

| 前缀 | 用途 |
|------|------|
| `tvm.ir.*` | 编译器 IR 构造和操作 |
| `tvm.target.*` | 目标设备相关 |
| `tvm.runtime.*` | 运行时功能 |
| `tvm.ffi.*` | FFI 核心功能 |
| `runtime.module.*` | 模块系统相关 |
| `<plugin>.*` | 插件自定义命名空间 |

## NPU建议

在 NPU 集成场景中，函数注册表的设计需要关注以下方面：

1. **NPU 算子函数命名规范**：建议为 NPU 算子使用统一命名前缀（如 `"npu.op.<op_name>"`），并在注册时附带算子的元数据（输入输出形状约束、支持的数据类型、目标 NPU 型号）。可通过函数属性机制（如 `Function::SetAttr`）将这些元数据附加到函数对象上，供编译器查询和算子融合决策使用。

2. **设备特定函数的条件注册**：NPU 插件加载时应检测可用的 NPU 设备型号和固件版本，仅注册当前设备支持的算子函数。避免注册设备不支持的函数导致运行时调用失败。可通过 NPU 插件注册的全局函数（如 `"npu.get_device_info"`）查询设备能力后再决定注册哪些函数。

3. **异步函数注册约定**：NPU 算子通常是异步执行的。建议异步函数统一接受 `TVMFFIStreamHandle` 作为最后一个参数，函数提交命令到流后立即返回，同步通过 NPU 插件提供的同步全局函数完成。注册表可通过属性标记函数为异步，供调度器优化。

4. **函数版本管理**：NPU 算子实现可能随固件版本更新而优化。建议在函数名中包含版本后缀（如 `"npu.op.conv2d.v2"`），或通过函数属性携带版本号，旧版本函数保留以支持向后兼容。全局注册表的 override 机制允许在运行时替换为优化版本。

5. **注册表性能**：NPU 编译流程可能在短时间内注册和查找大量算子函数。注册表的查找性能（哈希表 O(1)）足以满足需求，但应避免在热路径（如算子调用循环）中反复调用 `GetGlobal`。建议在编译阶段缓存 `Function` 对象，运行时直接调用。

6. **跨设备函数路由**：多 NPU 环境中，同一算子在不同设备上可能有不同实现。建议注册设备特定版本（如 `"npu.op.conv2d.device0"`、`".device1"`），并提供一个路由函数根据 `DLDevice` 参数分发到对应实现。

## 设计分析

全局函数注册表的设计简洁而强大。它将函数的"注册"和"发现"解耦：注册者不需要知道谁会调用，调用者不需要知道函数实现在哪种语言中。这种松耦合使得 TVM 的编译器 Pass、运行时算子、设备驱动可以各自独立开发和加载，通过统一的名称空间协作。

注册表的另一个重要作用是支持"运行时扩展"：新功能可以通过动态模块在运行时注入，无需重新编译主程序。这对于 NPU 驱动更新、自定义算子加载等场景至关重要。

## 相关概念

- [008 模块系统与动态加载](008-module-system-dynamic-loading.md)：模块自动注册函数
- [009 扩展点与插件机制](009-extension-points-plugin-mechanism.md)：注册表作为核心扩展点
- [011 跨语言边界设计](011-cross-language-boundary.md)：跨语言函数调用机制
- [014 错误处理与异常安全](014-error-handling-exception-safety.md)：函数调用中的错误传播
