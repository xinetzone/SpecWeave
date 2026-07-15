---
title: "05 - 反射与注册机制"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki/05-reflection.toml"
tags: [tvm-ffi, ffi, cpp, core-api]
---
# 反射与注册机制

反射是 TVM FFI 实现跨语言绑定的核心：C++ 中声明的类、字段、方法和枚举可以在运行时被查询、遍历、按名称调用，并且能自动生成 Python 端的 c_class，无需手写绑定代码。本章介绍反射注册表、`ObjectDef<T>` 构建器、访问器系统、对象创建器、重载解析以及枚举注册。

**头文件**位于 `include/tvm/ffi/reflection/`：
- `registry.h`：全局反射注册表入口（`ObjectDef<T>`、`EnumDef<T>`、`GlobalDef`）
- `accessor.h`：字段/方法访问器
- `access_path.h`：访问路径表示（嵌套字段）
- `creator.h`：按名称创建对象
- `overload.h`：方法重载解析
- `enum_def.h`：枚举注册构建器

---

## 1. 反射注册表概述

TVM FFI 的反射信息通过**类型属性列（Type Attribute Column）**机制存储。每个 Object 类型在运行时被分配一个 `type_index`，每个属性（字段列表、方法列表、枚举实例、构造函数等）占用一列，按 `type_index - begin_index` 偏移存取。

核心数据结构：
- `TVMFFITypeInfo`：每个类型一条记录，包含 `type_key`、`type_index`、`type_depth`、`type_ancestors[]`（继承链）、字段数、方法数等。
- `TVMFFIFieldInfo`：字段描述（名称、类型 schema、偏移、访问标志、metadata）。
- `TVMFFIMethodInfo`：方法描述（名称、参数类型 schema、返回类型、调用入口、metadata）。
- `TVMFFITypeAttrColumn`：某一属性的密集数组（按 type_index 索引）。

反射注册是**静态初始化 + 懒分配**的：C++ 中通过静态对象构造函数调用 `ObjectDef<T>`/`EnumDef<T>`，首次访问时分配运行时 type_index 并填入字段/方法表。

---

## 2. ObjectDef\<T\> 构建器模式

`reflection::ObjectDef<T>` 是注册自定义类反射信息的入口，采用链式调用（builder pattern）在 .cc 文件中一次性声明字段、方法、类型别名和 metadata。

### 2.1 最简示例：注册带字段的类

```cpp
// my_vec.h
#include <tvm/ffi/object.h>
using namespace tvm::ffi;

class MyVecObj : public Object {
public:
    double x, y, z;
    static constexpr const char* _type_key = "demo.MyVec";
    TVM_FFI_DECLARE_OBJECT_INFO_FINAL("demo.MyVec", MyVecObj, Object);
};

class MyVec : public ObjectRef {
public:
    TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE(MyVec, ObjectRef, MyVecObj);
};
```

```cpp
// my_vec.cc
#include "my_vec.h"
#include <tvm/ffi/reflection/registry.h>
using namespace tvm::ffi;

TVM_FFI_REGISTER_OBJECT(MyVecObj)
    .def_field<&MyVecObj::x>("x")
    .def_field<&MyVecObj::y>("y")
    .def_field<&MyVecObj::z>("z");
```

`TVM_FFI_REGISTER_OBJECT(MyVecObj)` 展开为一个静态注册对象，其构造函数链式完成：
1. 确保 `MyVecObj` 的运行时 type_index 被分配（`_GetOrAllocRuntimeTypeIndex`）。
2. 通过 `def_field<&MyVecObj::x>("x")` 记录字段偏移和类型信息（模板自动推导 `double`）。
3. 在程序启动时将字段/方法表填入全局注册表。

### 2.2 注册方法

```cpp
TVM_FFI_REGISTER_OBJECT(MyVecObj)
    .def_field<&MyVecObj::x>("x")
    .def_field<&MyVecObj::y>("y")
    .def_field<&MyVecObj::z>("z")
    .def_method("length", [](const MyVec& self) -> double {
        const MyVecObj* p = self.get();
        return std::sqrt(p->x*p->x + p->y*p->y + p->z*p->z);
    })
    .def_method("add", [](const MyVec& self, const MyVec& other) -> MyVec {
        MyVec result = make_object<MyVecObj>();
        result->x = self->x + other->x;
        result->y = self->y + other->y;
        result->z = self->z + other->z;
        return result;
    });
```

`def_method` 接受任意可调用对象（lambda/函数指针/Function），自动推导参数和返回类型的 schema，并将其包装为 `Function` 存入方法表。调用时通过 accessor 机制把 self 和参数按 Any 打包传递。

### 2.3 附加 metadata

使用 `Metadata` 和 `DefaultValue` 附加元信息（用于代码生成/序列化/文档）：

```cpp
TVM_FFI_REGISTER_OBJECT(MyVecObj)
    .def_field<&MyVecObj::x>("x", Metadata({
        {"doc", String("X coordinate")},
        {"range", String("(-inf, inf)")}
    }))
    .def_field<&MyVecObj::y>("y", DefaultValue(0.0))
    .def_field<&MyVecObj::z>("z", DefaultValue(0.0));
```

metadata 值只允许 int、bool、String，最终序列化为 JSON 存到 TVMFFIFieldInfo。

---

## 3. 访问器系统（accessor.h / access_path.h）

访问器（Accessor）是对字段和方法的统一封装，提供按名称读写字段、调用方法的能力，是 Python 端属性访问和方法分发的底层机制。

### 3.1 字段访问器

每个 `def_field` 会创建一个 FieldAccessor，内部存储：
- 字段在对象内的偏移量（通过成员指针 `&T::field` 计算）
- 字段的 TypeTraits（类型信息）
- 读/写/移动的函数指针

```cpp
// 概念模型
template <typename T, typename F>
struct FieldAccessor {
    F T::*member;
    Any (*get)(const T* self);
    void (*set)(T* self, AnyView val);
};
```

### 3.2 方法访问器

方法访问器封装一个已适配为 PackedFunc 形式的 `Function`：
- 第一个参数隐式为 self（或 self 的 mutable 指针）
- 其余参数为用户参数
- 返回值包装为 Any

### 3.3 AccessPath（access_path.h）

`AccessPath` 表示"嵌套字段"的路径，例如 `config.layers[0].name` 这样的链式访问。它由段（segment）组成，每段是字段名或数组下标，用于反射遍历、序列化路径定位和错误消息。

```cpp
// 概念表示
AccessPath p = AccessPath::Field("config")
    .Field("layers")
    .Index(0)
    .Field("name");
```

访问错误时（如类型不匹配），通过 `VisitErrorContext`（见 `extra/visit_error_context.h`）可以把当前 AccessPath 附加到错误消息上，极大提升调试效率。

---

## 4. Creator：按名称创建对象

`creator.h` 提供按类型 key 创建对象的能力。注册时若提供构造函数，creator 表会记录一个零参/多参工厂函数。

### 4.1 注册构造函数

```cpp
TVM_FFI_REGISTER_OBJECT(MyVecObj)
    .def_field<&MyVecObj::x>("x")
    .def_field<&MyVecObj::y>("y")
    .def_field<&MyVecObj::z>("z")
    .def_creator([](double x, double y, double z) -> MyVec {
        MyVec v = make_object<MyVecObj>();
        v->x = x; v->y = y; v->z = z;
        return v;
    });
```

也可以注册零参构造函数（用于反序列化和默认构造）：

```cpp
.def_creator([]() -> MyVec {
    return make_object<MyVecObj>();
})
```

### 4.2 按名称创建

```cpp
#include <tvm/ffi/reflection/creator.h>

ObjectRef obj = reflection::CreateObject(String("demo.MyVec"));
// 或者带参数
Any result = reflection::CreateObject(String("demo.MyVec"), {Any(1.0), Any(2.0), Any(3.0)});
MyVec v = result.cast<MyVec>();
```

Python 端的构造函数调用 `demo.MyVec(1,2,3)` 就走这个路径。

---

## 5. Overload：方法重载解析

当同名方法注册多个签名时，`overload.h` 提供基于参数类型的静态/动态分发：

```cpp
TVM_FFI_REGISTER_OBJECT(MyVecObj)
    .def_overload("scale", [](const MyVec& self, double s) -> MyVec {
        MyVec r = make_object<MyVecObj>();
        r->x = self->x * s; r->y = self->y * s; r->z = self->z * s;
        return r;
    })
    .def_overload("scale", [](const MyVec& self, const MyVec& other) -> MyVec {
        MyVec r = make_object<MyVecObj>();
        r->x = self->x * other.x; r->y = self->y * other.y; r->z = self->z * other.z;
        return r;
    });
```

调用时重载解析器按以下顺序匹配：
1. 完全匹配（参数类型数量和 Any 中实际类型严格对应）
2. 兼容转换（通过 `try_cast`）
3. 若仍然歧义，抛 TypeError 并列出候选项

对 Object 子类方法，推荐使用 `OverloadObjectDef<T>`（`overload.h` 中）或直接在 `def_method` 中使用 `Overload` 辅助函数。

---

## 6. EnumDef：枚举类型注册

枚举使用 `EnumDef<T>` 注册（在 enum_def.h），与 ObjectDef 类似但面向 EnumObj 子类：

```cpp
// op_kind.h
class OpKindObj : public EnumObj {
public:
    static constexpr const char* _type_key = "demo.OpKind";
    TVM_FFI_DECLARE_OBJECT_INFO_FINAL("demo.OpKind", OpKindObj, EnumObj);
};

class OpKind : public Enum {
public:
    TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE(OpKind, Enum, OpKindObj);
};
```

```cpp
// op_kind.cc
#include <tvm/ffi/reflection/enum_def.h>

TVM_FFI_REGISTER_ENUM(OpKindObj)
    .add("Add")
    .add("Sub")
    .add("Mul")
    .add("Div")
    .add_attr<String>("commute", String("Add,Mul"));  // 附加扩展属性
```

- `.add("Name")`：创建名为 "Name" 的单例 EnumObj，分配从 0 开始的密集序号 `_value`。
- `.add_attr<K,V>(key, value)`：为整个枚举类附加不修改 C++ 类定义的扩展属性（存入类型属性列）。
- 每个枚举实例本身也是 Object，可以为单个实例附加字段（通过 `.add(name, fields_dict)` 重载）。

---

## 7. 反射如何驱动 Python 绑定

### 7.1 自动 c_class 生成

Python 端 `tvm_ffi` 启动时遍历所有注册类型，为每个 Object 类型动态生成一个 `c_class`：

```python
import tvm_ffi

MyVec = tvm_ffi.CClass("demo.MyVec")
v = MyVec(x=1.0, y=2.0, z=3.0)   # 走 Creator + 字段 setter
print(v.x)                       # 走字段 getter
print(v.length())                # 走方法调用
```

字段访问转为 Any 中的 getter/setter 调用，方法调用转为 PackedFunc 调用。

### 7.2 类型 Schema

每个字段/方法在注册时都会生成 JSON Schema（通过 `TypeSchema()`），Python 端和 stub 生成器据此产生类型提示：

```jsonc
// MyVec 的隐式 schema
{
  "kind": "object",
  "name": "demo.MyVec",
  "fields": [
    {"name": "x", "type": {"type": "float64"}},
    {"name": "y", "type": {"type": "float64"}},
    {"name": "z", "type": {"type": "float64"}}
  ],
  "methods": [
    {"name": "length", "args": [], "ret": {"type": "float64"}},
    {"name": "add", "args": [{"name": "other", "type": {"type": "object", "name": "demo.MyVec"}}], "ret": {"type": "object", "name": "demo.MyVec"}}
  ]
}
```

`python/tvm_ffi/stub/` 下的 stub 生成器读取这些 schema，为 IDE 自动补全输出 `.pyi` 文件。

### 7.3 方法分发路径

当 Python 调用 `v.add(u)` 时，调用链为：

1. Python 端通过 FFI 传递方法名 `"add"` 和参数 `(u,)`。
2. C++ 端按 `v.type_index()` 在方法表中查找 `"add"` 的访问器。
3. 若存在重载，用 overload 解析器选择最佳签名。
4. 将 `v` 作为 self、`u` 转换为 Any，执行 PackedFunc。
5. 返回 Any 结果，按 schema 转换回 Python 对象。

---

## 8. 完整示例：注册一个带字段和方法的自定义类

```cpp
// point.h
#pragma once
#include <tvm/ffi/object.h>
#include <tvm/ffi/string.h>
namespace demo {
using namespace tvm::ffi;

class PointObj : public Object {
public:
    double x{0}, y{0};
    String label;

    static constexpr const char* _type_key = "demo.Point";
    TVM_FFI_DECLARE_OBJECT_INFO_FINAL("demo.Point", PointObj, Object);
};

class Point : public ObjectRef {
public:
    TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE(Point, ObjectRef, PointObj);

    double x() const { return get()->x; }
    double y() const { return get()->y; }
    const String& label() const { return get()->label; }
};
}  // namespace demo
```

```cpp
// point.cc
#include "point.h"
#include <tvm/ffi/reflection/registry.h>
#include <cmath>

namespace demo {
using namespace tvm::ffi;

TVM_FFI_REGISTER_OBJECT(PointObj)
    .def_field<&PointObj::x>("x", DefaultValue(0.0),
        Metadata({{"doc", String("X coordinate")}}))
    .def_field<&PointObj::y>("y", DefaultValue(0.0),
        Metadata({{"doc", String("Y coordinate")}}))
    .def_field<&PointObj::label>("label", DefaultValue(String("")),
        Metadata({{"doc", String("Optional label")}}))
    .def_creator([](double x, double y, String label) -> Point {
        Point p = make_object<PointObj>();
        p->x = x; p->y = y; p->label = std::move(label);
        return p;
    })
    .def_creator([]() -> Point {
        return make_object<PointObj>();
    })
    .def_method("distance_to", [](const Point& self, const Point& other) -> double {
        double dx = self->x - other->x;
        double dy = self->y - other->y;
        return std::sqrt(dx*dx + dy*dy);
    })
    .def_method("is_origin", [](const Point& self) -> bool {
        return self->x == 0.0 && self->y == 0.0;
    });

}  // namespace demo
```

Python 端使用：

```python
import tvm_ffi
Point = tvm_ffi.CClass("demo.Point")

p1 = Point(3.0, 4.0, "A")
p2 = Point(0.0, 0.0, "origin")

print(p1.x, p1.y, p1.label)   # 3.0 4.0 'A'
print(p1.distance_to(p2))      # 5.0
print(p2.is_origin())          # True
```

---

## 9. 反射 API 速查

| 组件 | 头文件 | 作用 |
|------|--------|------|
| `reflection::ObjectDef<T>` | `reflection/registry.h` | 注册类字段、方法、构造函数、metadata |
| `reflection::EnumDef<T>` | `reflection/enum_def.h` | 注册枚举实例与属性 |
| `FieldAccessor` | `reflection/accessor.h` | 字段读写访问器 |
| `MethodAccessor` | `reflection/accessor.h` | 方法调用访问器 |
| `AccessPath` | `reflection/access_path.h` | 嵌套访问路径表示 |
| `CreateObject(name, args...)` | `reflection/creator.h` | 按类型名创建实例 |
| `Overload` / `def_overload` | `reflection/overload.h` | 重载方法注册与解析 |
| `TVMFFI*Info` 结构 | `c_api.h` | C ABI 层的反射元数据结构 |
| `TVM_FFI_REGISTER_OBJECT(T)` | 宏 | 展开为静态 ObjectDef 注册器 |
| `TVM_FFI_REGISTER_ENUM(T)` | 宏 | 展开为静态 EnumDef 注册器 |

---

反射是 TVM FFI "一次注册、处处可用"特性的基础：它串联起对象系统、容器、函数、序列化和 Python/Rust 绑定。下一章将在反射之上介绍 JSON 序列化和结构相等/哈希。

---

[上一章](04-containers.md) | [下一章 →](06-serialization.md)
