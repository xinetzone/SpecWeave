---
type: Concept
title: "视角091：def_field/def_method"
description: "解析 ObjectDef 的字段与方法注册原语 def_ro/def_rw/def/def_static 的语义差异、InfoTrait 组合机制，以及 init 构造函数注册与 type_schema 元数据生成。"
tags:
  - reflection
  - def-field
  - def-method
  - registration
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-256, F-257, F-258, F-261
  - code:
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/c_api.h
---

# 视角091：def_field/def_method

## 概述

`def_field` 与 `def_method` 是 `ObjectDef<T>` 暴露的两类基础注册原语，分别用于向运行时类型表登记字段与方法。C++ 层以 `def_ro`/`def_rw` 表达字段的只读/可写属性，以 `def`/`def_static` 表达实例方法/静态方法。这些原语均返回 `ObjectDef&` 以支持链式调用，并接受可变数量的 `InfoTrait` 参数来附加默认值、标志位、文档与元数据。

## 字段注册：def_ro 与 def_rw

`def_ro(name, field_ptr, extra...)`（`registry.h:800`）注册只读字段，`def_rw(name, field_ptr, extra...)`（`registry.h:819`）注册可写字段。二者共同委托私有方法 `RegisterField`（`registry.h:993-1021`），区别仅在于 `writable` 参数：

- `def_rw` 在调用前执行 `static_assert(Class::_type_mutable, ...)`，只有声明 `_type_mutable = true` 的可变类型才允许注册可写字段。这是编译期安全约束，防止对不可变 IR 节点意外暴露写接口。
- 可写字段会置位 `kTVMFFIFieldFlagBitMaskWritable`，并在 `TVMFFIFieldInfo` 中提供 setter；只读字段同样设置 setter（源码注释说明 setter 存在是为了序列化需要，`c_api.h:1206`），但运行时可通过标志位拒绝外部写入。

`field_ptr` 是 C++ 成员指针（如 `&MyNode::name`），`GetFieldByteOffsetToObject`（`registry.h:387`）通过在 `nullptr` 上取成员地址再减去子类到 `Object` 的偏移，计算出字段相对对象基址的字节偏移。这一技巧使得反射层无需了解具体类型即可按偏移访问字段。

## 方法注册：def 与 def_static

`def(name, func, extra...)`（`registry.h:838`）注册实例方法，`def_static(name, func, extra...)`（`registry.h:856`）注册静态方法。二者委托 `RegisterMethod`（`registry.h:1024-1044`）：

1. 通过 `FunctionInfo::TypeSchema()` 推导函数的类型 schema。
2. 调用 `GetMethod`（`registry.h:460`）将可调用对象包装为 `Function`，名称为 `"<type_key>.<method_name>"`。
3. 静态方法置位 `kTVMFFIFieldFlagBitMaskIsStaticMethod`。
4. 将 schema 写入 metadata，应用 InfoTrait，序列化为 JSON。
5. 调用 `TVMFFITypeRegisterMethod` 提交。

成员函数指针由 `WrapFunction`（`registry.h:476-509`）转换为首参为 self 的 lambda，使得实例方法在 ABI 层与自由函数一致。`def` 还接受 `init<Args...>` 这一特殊参数形式来注册构造函数（`registry.h:942`）。

## InfoTrait 组合

所有注册原语的 `extra...` 参数包均可接受 `InfoTrait` 子类，由 `ApplyFieldInfoTrait`/`ApplyMethodInfoTrait`（`registry.h:433-450`）通过 `if constexpr` 判断并应用：

- `DefaultValue(value)`：设置静态默认值，置位 `HasDefault`。
- `DefaultFactory(factory)`：设置工厂函数，置位 `HasDefault | DefaultFromFactory`。
- `AttachFieldFlag::SEqHashIgnore()` 等：附加结构化比较标志。
- `repr(false)`、`compare(false)`、`hash(false)`：控制字段在 repr/比较/哈希中的可见性。
- `kw_only(true)`：标记字段在自动构造函数中仅限关键字。
- `init(false)`：从自动 `__ffi_init__` 中排除字段。
- 字符串字面量：作为 doc 文档字符串。

多个 InfoTrait 可组合传入，顺序无关，各自通过位或修改 `flags`。

## init 构造函数注册

`def(init<Args...>(), extra...)`（`registry.h:942-960`）是 `def` 的重载，专门注册构造函数：

1. 置 `has_explicit_init_ = true`，抑制析构时的自动 init 生成。
2. 将 `init<Args...>::execute<Class>` 注册为静态方法 `__ffi_init__`，该函数内部调用 `make_object<Class>(std::forward<Args>(args)...)`（`registry.h:653`）。
3. 在已注册方法中查找 `__ffi_init__`，将其函数指针同步注册到 `kInit` 类型属性列，供运行时快速分派。
4. 构造函数的 type_schema 被保留，Python 存根生成据此渲染参数类型。

## 设计分析

`def_field`/`def_method` 原语的设计将"声明什么"与"如何注册"分离：用户以接近 C++ 原生语法的成员指针和函数指针声明反射信息，框架负责偏移计算、schema 推导、标志位管理与 ABI 提交。只读/可写与实例/静态的二分法覆盖了常见场景，而 InfoTrait 的开放组合避免了为每种配置组合提供重载。`init` 的双重身份（无参版本作为构造注册，`init(false)` 作为抑制标志）展示了在不增加 API 表面积的前提下复用类型的技巧。整体机制使得一个典型类型的反射注册可在十余行链式调用内完成，且全部在编译期校验类型安全。

## 相关概念

- [086 FieldInfo 设计](086-field-info.md)：def_field 产出的结构
- [087 MethodInfo 设计](087-method-info.md)：def_method 产出的结构
- [090 ObjectDef 构建器](090-object-def-builder.md)：注册原语的宿主类
- [093 字段标志位系统](093-field-flags.md)：InfoTrait 操作的标志位
