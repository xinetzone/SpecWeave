---
type: Concept
title: "视角090：ObjectDef 构建器"
description: "解析 reflection::ObjectDef<T> 模板类：链式注册字段/方法/类型属性/构造函数的 DSL，析构时自动注册 __ffi_new__、__ffi_init__、__ffi_shallow_copy__ 的机制。"
tags:
  - reflection
  - object-def
  - builder
  - dsl
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-255, F-256, F-257, F-258
  - code:
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/reflection/accessor.h
    - include/tvm/ffi/c_api.h
---

# 视角090：ObjectDef 构建器

## 概述

`ObjectDef<T>` 是 TVM FFI 反射系统在 C++ 层提供的流式构建器，定义在 `include/tvm/ffi/reflection/registry.h:726`。它采用构造时获取类型索引、析构时提交特殊方法的 RAII 风格，通过链式调用 `def_ro`、`def_rw`、`def`、`def_static`、`def_type_attr`、`def_convert` 等方法，将类型的字段、方法、构造函数与类型属性注册到全局运行时类型表。它是 C++ 类型接入反射系统的主要入口。

## 构造与析构

`ObjectDef<T>` 构造函数（`registry.h:733-738`）执行：

1. 通过 `Class::_GetOrAllocRuntimeTypeIndex()` 获取类型索引。
2. 记录 `Class::_type_key`。
3. 调用 `MaybeSuppressAutoInit` 处理 `init(false)` 参数。
4. 调用 `RegisterExtraInfo` 填充 `TVMFFITypeMetadata` 并通过 `TVMFFITypeRegisterMetadata` 提交。

析构函数（`registry.h:750-784`）承担三项关键的延迟注册：

1. **`__ffi_shallow_copy__`**：若 `Class` 可拷贝构造，注册一个调用拷贝构造的 lambda 到 `kShallowCopy` 类型属性（`accessor.h:372`）。
2. **`__ffi_new__`**：若 metadata 中存在 native creator，将其包装为返回 `ObjectRef` 的 `Function` 并注册到 `kNew` 类型属性。
3. **`__ffi_init__`**：若用户未显式注册 `init`，通过全局函数 `ffi._RegisterFFIInit` 触发自动构造函数生成。

这种"析构时提交"的设计保证了用户在链式调用期间注册的字段、方法在特殊方法生成前已全部就位。

## 字段注册

- **`def_ro(name, field_ptr, extra...)`**（`registry.h:800`）：注册只读字段，内部 `writable=false`。
- **`def_rw(name, field_ptr, extra...)`**（`registry.h:819`）：注册可写字段，静态断言 `Class::_type_mutable` 为真，否则编译失败。

两者最终调用 `RegisterField`（`registry.h:993-1021`），计算字段偏移、绑定泛型 getter/setter、应用 `DefaultValue`、`AttachFieldFlag`、`repr(false)` 等 `InfoTrait`，并通过 `TVMFFITypeRegisterField` 提交。

## 方法注册

- **`def(name, func, extra...)`**（`registry.h:838`）：注册实例方法，`is_static=false`。
- **`def_static(name, func, extra...)`**（`registry.h:856`）：注册静态方法，置 `IsStaticMethod` 标志。

方法通过 `WrapFunction`（`registry.h:476-509`）将成员函数指针转换为首参为 self 的 lambda，再包装为带 schema 的 `Function`，最终由 `TVMFFITypeRegisterMethod` 提交。

## 构造函数注册

`def(init<Args...>(), extra...)`（`registry.h:942-960`）注册显式构造函数：

1. 标记 `has_explicit_init_ = true`，抑制自动生成。
2. 将 `init<Args...>::execute<Class>` 注册为静态方法 `__ffi_init__`，保留 type_schema 供存根生成。
3. 在已注册方法数组中找到该方法，同步注册到 `kInit` 类型属性列，供运行时分派。

`init<>` 零参数版本（`registry.h:668`）双重身份：作为 `def(init<>())` 时注册无参构造；作为 `InfoTrait` 时，`init(false)` 可在字段级或类级别抑制自动 init。

## 类型属性

- **`def_type_attr(name, value)`**（`registry.h:879/897`）：注册类型属性，值可直接转为 `AnyView` 或作为可调用对象包装为 `Function`，通过 `TVMFFITypeRegisterAttr` 写入稀疏列。
- **`def_convert<TSelf>()`**（`registry.h:912`）：注册标准 `__ffi_convert__` 转换钩子，将 `AnyView` 转为目标 `ObjectRef` 子类。

## 设计分析

`ObjectDef<T>` 体现了"RAII + 链式 DSL"的现代 C++ 注册范式。构造时建立类型上下文，链式调用期间累积元数据，析构时按正确顺序派发生命周期钩子（shallow copy → new → init），使用户无需关心注册顺序。模板化的成员指针推导自动计算字段偏移与类型 schema，消除了手工维护字段表的冗余。`InfoTrait` 机制（`DefaultValue`、`AttachFieldFlag`、`repr`、`compare`、`hash`、`kw_only` 等）以可组合的小对象扩展注册语义，避免了构造函数参数爆炸。不可拷贝/不可移动的约束确保注册器在栈上以临时对象方式安全使用，典型写法为 `refl::ObjectDef<MyType>().def_ro(...).def_rw(...);`。

## 相关概念

- [086 FieldInfo 设计](086-field-info.md)：ObjectDef 注册的字段结构
- [087 MethodInfo 设计](087-method-info.md)：ObjectDef 注册的方法结构
- [091 def_field/def_method](091-def-field-def-method.md)：注册方法的语义细节
- [097 TypeAttr 类型属性](097-type-attr.md)：def_type_attr 的底层机制
