---
type: Concept
title: "视角087：MethodInfo 设计"
description: "解析 TVM FFI 反射系统中方法元数据 TVMFFIMethodInfo 的结构设计：名称、文档、metadata JSON、flags 与包装为 Any 的 Function 对象，以及实例方法 self 约定与静态方法标记。"
tags:
  - reflection
  - method-info
  - metadata
  - function
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-035, F-251, F-252, F-253
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/reflection/accessor.h
---

# 视角087：MethodInfo 设计

## 概述

`TVMFFIMethodInfo` 是 TVM FFI 反射系统描述类型方法的元数据结构，定义在 `include/tvm/ffi/c_api.h:1249`。与 `TVMFFIFieldInfo` 类似，它是一个纯 C 结构体，但承载的是可调用实体而非数据成员。每个被反射暴露的方法——包括实例方法、静态方法、自动生成的 `__ffi_init__` 构造函数——都会在运行时类型表的 `methods` 数组中占据一条记录。

## 数据结构

`TVMFFIMethodInfo`（`c_api.h:1249-1266`）包含以下字段：

- **`name`**（`TVMFFIByteArray`）：方法名称。对于自动生成的构造函数，该名称为 `"__ffi_init__"`；对于浅拷贝工厂为 `"__ffi_shallow_copy__"`。
- **`doc`**（`TVMFFIByteArray`）：方法文档字符串。源码注释说明，doc 与 metadata 分离是因为文档可能是非结构化的大文本，而 metadata 聚焦于结构化信息（`c_api.h:1254-1256`）。
- **`metadata`**（`TVMFFIByteArray`）：JSON 字符串，包含 `type_schema` 等结构化类型信息，供存根生成与运行时分派使用。
- **`flags`**（`int64_t`）：方法标志位。当前核心标志为 `kTVMFFIFieldFlagBitMaskIsStaticMethod`（1<<2），标记静态方法。
- **`method`**（`TVMFFIAny`）：包装为 `AnyView` 的 `ffi::Function` 对象。源码注释强调：对于实例方法，函数的第一个参数始终是 `self`（`c_api.h:1263`）。

## self 约定

实例方法在反射层被统一为"第一个参数为 self"的普通函数。`ReflectionDefBase::WrapFunction`（`registry.h:476-509`）负责将 C++ 成员函数指针转换为接受目标对象作为首参的 lambda：

- 对继承自 `ObjectRef` 的类，生成 `[func](Class target, Args... params) { return (target.*func)(params...); }`。
- 对继承自 `Object` 的类，生成 `[func](const Class* target, Args... params) { return (target->*func)(params...); }`。

这一转换使得方法在 C ABI 层与自由函数具有相同的调用约定，跨语言绑定时无需区分成员函数与普通函数。

## 注册流程

`ObjectDef<T>::RegisterMethod`（`registry.h:1024-1044`）执行：

1. 通过 `GetMethod`（`registry.h:460`）将可调用对象包装为带类型 schema 的 `Function`，函数名形如 `"<type_key>.<method_name>"`。
2. 将 `Function` 移动为 `TVMFFIAny` 存入 `info.method`。
3. 若为静态方法，置 `kTVMFFIFieldFlagBitMaskIsStaticMethod`。
4. 注入 `type_schema` 元数据，应用文档等 `InfoTrait`。
5. 序列化为 JSON 后调用 `TVMFFITypeRegisterMethod`（`c_api.h:1414`）注册。

全局函数则通过 `GlobalDef::RegisterFunc`（`registry.h:585-597`）走类似流程，但最终调用 `TVMFFIFunctionSetGlobalFromMethodInfo`（`c_api.h:1401`）注入全局函数表，并附带 method info 元数据。

## 查询与调用

C++ 层提供 `GetMethodInfo`（`accessor.h:205`）按类型键与方法名线性查找 `TVMFFIMethodInfo*`，`GetMethod`（`accessor.h:227`）进一步将 `info.method` 转换为 `Function` 对象。Python 端在安装 `__init__` 时，会优先在 `methods` 数组中查找名为 `__ffi_init__` 的条目，回退到 `TypeAttrColumn` 中自动生成的版本（`registry.py:370-420`）。

## 设计分析

`TVMFFIMethodInfo` 的设计将"方法"统一为"具名 Function + 标志位"，避免了在 C ABI 层引入复杂的成员调用约定。`method` 字段以 `TVMFFIAny` 而非裸指针存储，使得方法本身可携带闭包状态（如 Python 绑定的回调），并参与引用计数管理。doc 与 metadata 的分离则兼顾了人类可读文档与机器可消费 schema 的不同演进速率。静态方法标志与 self 约定共同构成了跨语言方法分派的最小契约。

## 扩展讨论

### 把方法抹平为"具名 Function"：彻底绕开成员函数 ABI 差异

`TVMFFIMethodInfo` 的关键决策是把实例方法统一转写为"第一个参数为 `self`"的普通函数。C++ 成员函数指针的调用约定与自由函数不同，且 msvc/gcc/clang 之间对成员指针的表示并不统一；一旦方法以 `Function`（`TVMFFIAny`)形式落地，跨语言绑定就只需掌握一种"具名可调用对象 + 首参 self"的约定，无需为每个平台、每个类的成员调用方式分别适配。这让 Python、Rust 绑定在处理方法时与处理普通内置函数完全同构。

### `method` 用 `TVMFFIAny` 持有：方法也能带状态、能被引用计数

`method` 字段以 `TVMFFIAny` 而非裸 `void*` 存储，意味着被反射的方法自身即是一个 FFI 值——它可以是一个携带闭包捕获、在 Python 侧动态生成的 `ffi::Function`，其生命周期也纳入引用计数管理，而非一个随时可能悬空的指针。这保证了"反射出来的方法"与"传给调用方的对象"使用一致的资源语义，避免方法句柄在长期持有后因宿主对象被回收而失效。

### 静态标志 + self 约定：跨语言分派的统一钥匙

`flags` 中 `kTVMFFIFieldFlagBitMaskIsStaticMethod` 用于区分静态方法（无 self）与实例方法（有 self），配合 `name`、`metadata` 中的 `type_schema`，使绑定层能仅凭一条 `TVMFFIMethodInfo` 记录就完成 "如何调用、要不要传 self、参数类型为何" 的完整分派。`__ffi_init__`/`__ffi_shallow_copy__` 这类自动生成方法的命名约定，则进一步让 Python 端 `install __init__` 时能稳定地"按名查找"而非依赖位置假设，从而与 stubgen（视角 100）在元数据消费上保持一致。

## 相关概念

- [086 FieldInfo 设计](086-field-info.md)：字段元数据的姊妹结构
- [091 def_field/def_method](091-def-field-def-method.md)：注册方法的 DSL
- [097 TypeAttr 类型属性](097-type-attr.md)：方法与类型属性的互补关系
- [100 存根生成 stubgen](100-stubgen.md)：metadata 中 type_schema 的消费方
