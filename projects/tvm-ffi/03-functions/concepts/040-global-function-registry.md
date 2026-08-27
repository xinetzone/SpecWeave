---
type: Concept
title: "视角040：全局函数注册表"
description: "解析 TVM FFI 的全局函数注册机制：GlobalFunctionTable 单例、C API 注册入口、C++ 层 GetGlobal/SetGlobal/ListGlobalNames，以及基于 GlobalDef 的链式注册 API。"
tags:
  - function
  - global-registry
  - function-table
  - dynamic-linking
  - reflection
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-021, F-141, F-142, F-143, F-280, F-281, F-282, F-342
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/function.h
    - include/tvm/ffi/reflection/registry.h
    - src/ffi/function.cc
---

# 视角040：全局函数注册表

## 概述

全局函数注册表是 TVM FFI 的中央函数目录，允许系统中的任何模块——C++ 核心、动态加载的库、Python/Rust 绑定——按名称注册和查找函数。该注册表以名称为键、函数对象为值，支撑了动态分发、插件扩展和跨语言函数发现。注册表的实现位于 `function.cc` 中的 `GlobalFunctionTable` 单例，对外暴露 C ABI 和 C++ 两层接口。

## GlobalFunctionTable 实现

### 数据结构

`GlobalFunctionTable` 定义在 `function.cc:51-142`，是一个隐藏在 `.cc` 文件中的私有类：

```cpp
class GlobalFunctionTable {
 public:
  class Entry : public Object, public TVMFFIMethodInfo {
   public:
    String name_data;
    String doc_data;
    String metadata_data;
    ffi::Function func_data;
    // ...
  };

  void Update(const String& name, Function func, bool can_override);
  void Update(const TVMFFIMethodInfo* method_info, bool can_override);
  bool Remove(const String& name);
  const Entry* Get(const String& name);
  Array<String> ListNames() const;

  static GlobalFunctionTable* Global();

 private:
  Map<String, Any> table_;
};
```

内部使用 `Map<String, Any>` 存储名称到 `Entry` 对象的映射。每个 `Entry` 包含：

- `name_data`：函数名称（String 对象）
- `doc_data`：文档字符串
- `metadata_data`：JSON 格式的元数据（含类型 schema）
- `func_data`：实际的 `Function` 对象

### 单例生命周期

`Global()` 方法（`function.cc:130-138`）使用 `new` 创建裸指针单例，而非函数局部静态变量：

```cpp
static GlobalFunctionTable* Global() {
  static GlobalFunctionTable* inst = new GlobalFunctionTable();
  return inst;
}
```

源码注释解释了原因（`function.cc:132-135`）：

> We deliberately create a new instance via raw new. This is because GlobalFunctionTable can contain callbacks into the host language (Python) and the resource can become invalid in deterministic order of destruction and forking. The resources will only be recycled during program exit.

这避免了静态析构顺序问题——注册表可能持有 Python 回调，而 Python 解释器可能在注册表之前被销毁。

### 线程安全模型

注册表**不使用互斥锁保护更新操作**（`function.cc:43-49`）：

> We do not use mutex to guard updating of GlobalFunctionTable. The assumption is that updating of GlobalFunctionTable will be done in the main thread during initialization or loading, or explicitly locked from the caller.

读取操作（`Get`、`ListNames`）通过 `Map` 的隐式共享机制保证安全，而更新操作假设在初始化阶段单线程执行。这是一种为启动性能优化的有意设计。

### 重复注册检测

`Update` 方法（`function.cc:85-105`）在 `can_override == false` 时检测重复注册并抛出异常：

```cpp
void Update(const String& name, Function func, bool can_override) {
  if (TVM_FFI_PREDICT_FALSE(table_.count(name) != 0)) {
    if (!can_override) {
      TVM_FFI_THROW(RuntimeError)
          << "Global Function `" << name
          << "` is already registered";
    }
  }
  table_.Set(name, ObjectRef(make_object<Entry>(name, std::move(func))));
}
```

## C ABI 接口

### TVMFFIFunctionGetGlobal

按名称查找全局函数（`c_api.h:728`）：

```c
TVM_FFI_DLL int TVMFFIFunctionGetGlobal(
    const TVMFFIByteArray* name,
    TVMFFIObjectHandle* out);
```

实现位于 `function.cc:177-189`，从 `GlobalFunctionTable` 查找 Entry，若找到则将函数对象的所有权转移到输出句柄，否则输出 NULL。

### TVMFFIFunctionSetGlobal

注册全局函数（`c_api.h:1390-1391`）：

```c
TVM_FFI_DLL int TVMFFIFunctionSetGlobal(
    const TVMFFIByteArray* name,
    TVMFFIObjectHandle f,
    int allow_override);
```

实现位于 `function.cc:161-168`，委托给 `GlobalFunctionTable::Update`。

### TVMFFIFunctionSetGlobalFromMethodInfo

带元数据的注册入口（`c_api.h:1401-1402`）：

```c
TVM_FFI_DLL int TVMFFIFunctionSetGlobalFromMethodInfo(
    const TVMFFIMethodInfo* method_info,
    int allow_override);
```

该版本接受 `TVMFFIMethodInfo` 结构体，包含名称、文档、类型 schema 等完整元数据，是反射系统注册函数的主要入口。

## C++ 层接口

### Function::GetGlobal

`Function::GetGlobal`（`function.h:409-419`）按名称查找函数，返回 `std::optional<Function>`：

```cpp
static std::optional<Function> GetGlobal(std::string_view name) {
  TVMFFIObjectHandle handle;
  TVMFFIByteArray name_arr{name.data(), name.size()};
  TVM_FFI_CHECK_SAFE_CALL(
      TVMFFIFunctionGetGlobal(&name_arr, &handle));
  if (handle != nullptr) {
    return Function(
        details::ObjectUnsafe::ObjectPtrFromOwned<FunctionObj>(
            static_cast<Object*>(handle)));
  } else {
    return std::nullopt;
  }
}
```

该方法有四个重载，分别接受 `std::string_view`、`const std::string&`、`const String&` 和 `const char*`。

`GetGlobalRequired`（`function.h:456-462`）是变体版本，在函数不存在时抛出 `ValueError`：

```cpp
static Function GetGlobalRequired(std::string_view name) {
  std::optional<Function> res = GetGlobal(name);
  if (!res.has_value()) {
    TVM_FFI_THROW(ValueError) << "Function " << name << " not found";
  }
  return *res;
}
```

### Function::SetGlobal

`Function::SetGlobal`（`function.h:499-505`）注册函数：

```cpp
static void SetGlobal(std::string_view name, Function func,
                      bool override = false) {
  TVMFFIByteArray name_arr{name.data(), name.size()};
  TVM_FFI_CHECK_SAFE_CALL(
      TVMFFIFunctionSetGlobal(
          &name_arr,
          details::ObjectUnsafe::GetHeader(func.get()),
          override));
}
```

### Function::ListGlobalNames

列出所有已注册函数名称（`function.h:511-521`）：

```cpp
static std::vector<String> ListGlobalNames() {
  Function fname_functor =
      GetGlobalRequired("ffi.FunctionListGlobalNamesFunctor")()
          .cast<Function>();
  std::vector<String> names;
  int len = fname_functor(-1).cast<int>();
  names.reserve(len);
  for (int i = 0; i < len; ++i) {
    names.push_back(fname_functor(i).cast<String>());
  }
  return names;
}
```

该方法的实现采用了**函子（functor）模式**而非直接返回数组。源码注释说明原因（`function.cc:215-218`）：

> NOTE: we return functor instead of array so list global function names do not need to depend on array. This is because list global function names usually is a core API that happens before array ffi functions are available.

这是一种依赖解耦设计：列出全局名称是核心 API，可能在 Array 容器 FFI 函数注册之前就需要被调用。

### Function::RemoveGlobal

按名称移除全局函数（`function.h:526-529`）：

```cpp
static void RemoveGlobal(const String& name) {
  static Function fremove = GetGlobalRequired("ffi.FunctionRemoveGlobal");
  fremove(name);
}
```

该方法通过调用预注册的 `ffi.FunctionRemoveGlobal` 全局函数实现，该函数在静态初始化块中注册（`function.cc:208-212`）。

## GlobalDef 链式注册 API

`reflection::GlobalDef` 类（`reflection/registry.h:521-598`）提供了流式的函数注册接口：

```cpp
namespace refl = tvm::ffi::reflection;
refl::GlobalDef()
    .def("my_func", [](int x) { return x + 1; })
    .def("another_func", MyFunction, "docstring");
```

`def` 方法模板（`registry.h:536-541`）自动完成以下工作：

1. 通过 `FunctionInfo` 推导函数签名和类型 schema。
2. 使用 `Function::FromTyped` 将任意可调用对象转换为 `Function`。
3. 构建 `TVMFFIMethodInfo` 结构体（包含名称、文档、元数据）。
4. 调用 `TVMFFIFunctionSetGlobalFromMethodInfo` 完成注册。

此外还有 `def_packed`（注册 PackedArgs 格式函数）和 `def_method`（暴露类方法为全局函数）两个变体。

## 内置全局函数

在 `TVM_FFI_STATIC_INIT_BLOCK`（`function.cc:206-245`）中，系统预注册了以下核心函数：

| 函数名 | 用途 |
|--------|------|
| `ffi.FunctionRemoveGlobal` | 移除全局函数 |
| `ffi.FunctionListGlobalNamesFunctor` | 名称列表函子 |
| `ffi.String` | String 类型标识函数 |
| `ffi.Bytes` | Bytes 类型标识函数 |
| `ffi.GetGlobalFuncMetadata` | 获取函数元数据 |
| `ffi.FunctionFromExternC` | 从 C 回调创建函数 |

## 设计分析

全局函数注册表的设计体现了多个工程考量：

1. **名称解耦**：调用方通过字符串名称查找函数，不需要编译期链接，支持运行时动态发现。
2. **元数据丰富**：每个 Entry 不仅存储函数，还包含文档和类型 schema，支撑反射系统和 IDE 工具。
3. **生命周期安全**：裸 new 单例避免静态析构顺序问题，特别考虑了宿主语言（Python）回调的生命周期。
4. **核心依赖最小化**：ListGlobalNames 使用函子模式避免对 Array 的依赖，确保核心 API 在容器系统初始化前可用。
5. **C++ 与 C API 对称**：`SetGlobal`/`GetGlobal` 与 `TVMFFIFunctionSetGlobal`/`TVMFFIFunctionGetGlobal` 一一对应，C++ 层仅是薄封装。

## 相关概念

- [036 Packed Function 约定](036-packed-function-convention.md)：注册的函数遵循的调用约定
- [041 函数一等公民](041-function-as-first-class-citizen.md)：Function 对象可作为参数传递
- [048 模块入口点约定](048-module-entry-point-convention.md)：动态模块如何注册函数
- [049 __tvm_ffi_ 符号前缀](049-tvm-ffi-symbol-prefix.md)：导出符号的命名约定
