---
type: Concept
title: "视角092：c_class Python 集成"
description: "解析 TVM FFI 中 @c_class 装饰器如何将 C++ 反射类型暴露为 Python 类：__ffi_new__/__ffi_init__ 分派、__init_handle_by_constructor__、字段属性访问与类型转换注册。"
tags:
  - reflection
  - python
  - c-class
  - binding
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-338, F-339, F-340, F-341
  - code:
    - include/tvm/ffi/reflection/accessor.h
    - include/tvm/ffi/reflection/registry.h
    - python/tvm_ffi/registry.py
    - python/tvm_ffi/cython/object.pxi
---

# 视角092：c_class Python 集成

## 概述

`c_class` 是 TVM FFI Python 绑定层的核心装饰器，用于将已通过 C++ 反射系统注册的类型暴露为符合 Python 习惯的类。它与 C++ 层的 `ObjectDef<T>` 协同工作：C++ 侧注册字段、方法与 `__ffi_new__`/`__ffi_init__` 钩子，Python 侧的 `c_class` 读取这些反射元数据，自动生成 `__init__`、属性访问器、`__copy__`、`__repr__` 等协议方法。本视角分析两侧协作的机制。

## 核心类型属性约定

C++ 反射系统在 `type_attr` 命名空间（`accessor.h:319-567`）定义了一组以双下划线包围的类型属性名，作为 Python 集成的契约：

- **`__ffi_new__`**（`accessor.h:329`）：零参数分配器，签名 `() -> TSelf`，分配零初始化对象。C++ 类型包装 `metadata->creator`；Python `@py_class` 类型则提供基于 `calloc` 的分配器。
- **`__ffi_init__`**（`accessor.h:344`）：打包构造函数，签名 `(*args, **kwargs) -> TSelf`，创建并初始化完整对象。关键字参数打包为 `[KWARGS, key0, val0, ...]`。
- **`__ffi_convert__`**（`accessor.h:354`）：将 `AnyView` 转换为特定 `TSelf` 子类，供 Python 类型转换器使用。
- **`__ffi_shallow_copy__`**（`accessor.h:372`）：浅拷贝工厂，服务于 Python `copy.copy()` 与 `copy.replace()`。

`ObjectDef<T>` 析构函数（`registry.h:750-784`）自动注册前三个钩子：可拷贝类型注册 `__ffi_shallow_copy__`；有 creator 的类型注册 `__ffi_new__`；未显式定义 init 时调用 `ffi._RegisterFFIInit` 生成默认 `__ffi_init__`。

## Python 端 __init__ 安装

`python/tvm_ffi/registry.py` 中的 `_install_init`（约 357 行起）负责将 C++ 的 `__ffi_init__` 安装为 Python 类的 `__init__`：

1. 优先在类型的 `methods` 数组中查找名为 `__ffi_init__` 的方法（用户通过 `def(init<Args...>())` 显式注册的版本）。
2. 若未找到，回退到通过 `core._lookup_type_attr(type_info.type_index, "__ffi_init__")` 查询类型属性列（自动生成版本）。
3. 将找到的构造函数包装为调用 `self.__init_handle_by_constructor__(ffi_init, *args, **kwargs)` 的方法。该方法在 Cython 层（`cython/object.pxi`）实现，负责调用 C++ 函数并将返回的对象句柄绑定到 Python 实例。

源码注释强调，`c_class` 必须是完整的构造函数安装器，维护"自定义 `__init__` 调用 `self.__ffi_init__(*args, **kwargs)`"的不变量（`registry.py:361-364, 446`）。子类通过重写 `__init__` 可在调用父类构造前后插入 Python 侧逻辑。

## 字段属性访问

C++ 注册的字段通过 `TVMFFIFieldInfo` 暴露给 Python。Cython 层在类创建时遍历 `fields` 数组，为每个字段生成 Python property：getter 调用 `TVMFFIFieldGetter` 读取值并转换为 Python 对象，setter 检查 `kTVMFFIFieldFlagBitMaskWritable` 后调用 `TVMFFIFieldSetter`。`kTVMFFIFieldFlagBitMaskReprOff` 控制字段是否出现在自动生成的 `__repr__` 中，`kTVMFFIFieldFlagBitMaskInitOff` 控制字段是否作为 `__init__` 参数。

## @py_class 互补机制

与 `c_class`（包装 C++ 类型）相对，`@py_class` 允许在 Python 中定义全新的对象类型。Cython 层的 `_register_py_class`（`cython/object.pxi:697`）在 C++ 类型表中分配新类型索引，注册基于 Python 回调的 `__ffi_new__` 分配器与 `__ffi_init__`，并在验证失败时通过 `_rollback_py_class`（`object.pxi:765`）回滚注册。这使得 Python 定义的类型与 C++ 类型在反射系统中地位对等，可被 C++ 代码通过 `TVMFFIGetTypeInfo` 发现和操作。

## 类型转换

`def_convert<TSelf>()`（`registry.h:912`）注册的 `__ffi_convert__` 钩子被 Python 类型转换器消费。当 C++ 函数期望参数类型为特定 `ObjectRef` 子类时，转换层调用该钩子将传入的 `AnyView` 转换为目标类型，支持 Python 子类实例透明传递给 C++ 接口。`__ffi_convert_type_schema__`（`accessor.h:362`）存储接受的输入类型 schema，存根生成据此渲染放宽的输入注解。

## 设计分析

`c_class` 集成体现了"元数据驱动的绑定生成"设计：C++ 侧通过 `ObjectDef` 以声明方式注册字段、方法与生命周期钩子，Python 侧在类创建时读取这些元数据并合成符合 Python 数据模型的方法。两侧通过稳定的类型属性名（`__ffi_new__`、`__ffi_init__` 等）解耦，C++ 无需了解 Python 对象模型，Python 也无需了解 C++ 内存布局。`__init_handle_by_constructor__` 这一中间层使得 Python 子类可自定义 `__init__` 而不破坏句柄绑定不变量。`@py_class` 的存在则打通了反向通道，使 Python 类型成为反射系统的一等公民，为跨语言对象互操作提供了对称能力。

## 相关概念

- [087 MethodInfo 设计](087-method-info.md)：__ffi_init__ 方法的承载结构
- [090 ObjectDef 构建器](090-object-def-builder.md)：C++ 侧注册生命周期钩子
- [097 TypeAttr 类型属性](097-type-attr.md)：__ffi_new__ 等钩子的存储机制
- [099 Creator 创建函数](099-creator.md)：__ffi_new__ 的底层 creator
