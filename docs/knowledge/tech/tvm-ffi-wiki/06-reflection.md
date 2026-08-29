---
id: "tvm-ffi-reflection"
title: "Reflection 反射系统"
tags: ["tvm-ffi", "reflection", "dataclass", "stubgen"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# Reflection 反射系统

## 概述

在跨语言 FFI 开发中，最繁琐的工作莫过于编写重复的绑定代码：为每个 C++ 类手动编写构造函数包装、字段 getter/setter、方法转发，还要在 Python 端重新定义一遍类型签名。TVM FFI 的 **Reflection 反射系统**彻底解决了这个问题——通过**编译期静态注册** + **运行时元数据**，实现 C++/Python 双向互操作、自动类型转换，无需手动编写绑定代码。

反射系统核心价值：零样板绑定、类型安全、IDE 友好（stub 生成）、dataclass 语义、双向反射。

**关键头文件**：
- `reflection/registry.h`（源项目归档路径）
- `extra/dataclass.h`（源项目归档路径）

## 反射系统设计理念

### 静态注册 vs 动态反射

TVM FFI 采用**混合反射模型**：

| 阶段 | 机制 | 作用 |
|------|------|------|
| 编译期 | C++ 模板 + 宏 | 类型检查、字段偏移计算、函数签名推导 |
| 静态初始化 | `TVM_FFI_STATIC_INIT_BLOCK` | 程序启动时自动注册元数据到全局表 |
| 运行时 | `TVMFFITypeInfo` 元数据表 | 动态查询字段、方法、构造函数，驱动跨语言调用 |

### ObjectDef 构建器模式

反射注册采用链式调用的**构建器模式**，通过 `ObjectDef<T>` fluently 配置类型信息，析构时自动完成元数据注册：

```cpp
refl::ObjectDef<PointObj>()
    .def_rw("x", &PointObj::x)
    .def_rw("y", &PointObj::y)
    .def("distance_to", &PointObj::DistanceTo);
```

### 为什么需要反射？

传统手动 FFI 绑定存在重复劳动、不同步风险、无结构化操作、无 IDE 支持等痛点。反射系统将"类型结构"作为一等公民，一次注册，多处复用。

## C++ 端反射注册

### 基本步骤

#### 1. 声明类型信息

使用 `TVM_FFI_DECLARE_OBJECT_INFO` 宏在类内声明类型元数据，可读写类需设置 `_type_mutable = true`：

```cpp
class PointObj : public ffi::Object {
 public:
  double x, y;
  ffi::String label;

  static constexpr bool _type_mutable = true;

  PointObj(double x, double y, ffi::String label = "")
      : x(x), y(y), label(std::move(label)) {}

  double DistanceTo(const PointObj& other) const {
    return std::hypot(x - other.x, y - other.y);
  }

  TVM_FFI_DECLARE_OBJECT_INFO_FINAL(
    "demo.Point", PointObj, ffi::Object);
};
```

#### 2. 注册构造函数

字段 trait 控制自动生成构造函数的行为：

| Trait | 作用 |
|-------|------|
| `refl::default_(value)` | 设置字段默认值（字面量） |
| `refl::default_factory(fn)` | 设置工厂默认值（用于容器类型） |
| `refl::kw_only(true)` | 标记为仅限关键字参数 |
| `refl::init(false)` | 从构造函数中排除该字段 |

显式构造函数用 `refl::init<Args...>()` 注册；不注册则自动从字段生成 `__ffi_init__`。

#### 3. 注册字段与方法

| 方法 | 说明 |
|------|------|
| `.def_ro(name, ptr, ...)` | 注册只读字段 |
| `.def_rw(name, ptr, ...)` | 注册可写字段 |
| `.def(name, func, doc)` | 注册实例方法 |
| `.def_static(name, func, doc)` | 注册静态方法 |

#### 4. 静态初始化块注册

所有注册代码放在 `TVM_FFI_STATIC_INIT_BLOCK()` 中，程序启动时自动执行：

```cpp
TVM_FFI_STATIC_INIT_BLOCK() {
  namespace refl = tvm::ffi::reflection;
  refl::ObjectDef<PointObj>()
      .def_rw("x", &PointObj::x, "X coordinate")
      .def_rw("y", &PointObj::y, "Y coordinate")
      .def_rw("label", &PointObj::label, refl::default_(""))
      .def("distance_to", &PointObj::DistanceTo);
}
```

同时需要定义 `ObjectRef` 引用包装器：

```cpp
class Point : public ffi::ObjectRef {
 public:
  Point(double x = 0, double y = 0)
      : ObjectRef(ffi::make_object<PointObj>(x, y)) {}
  TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE(
      Point, ffi::ObjectRef, PointObj);
};
```

## Python 端 dataclass 集成

### @c_class：映射 C++ 反射对象

`@c_class(type_key)` 装饰器将 C++ 注册的反射类型包装为 Python dataclass 风格的类：

```python
import tvm_ffi
from tvm_ffi.dataclasses import c_class
from typing import TYPE_CHECKING

@c_class("demo.Point", repr=True, eq=True)
class Point(tvm_ffi.Object):
    # tvm-ffi-stubgen(begin): object/demo.Point
    x: float
    y: float
    label: str
    if TYPE_CHECKING:
        def __init__(self, x: float = 0, y: float = 0, label: str = "") -> None: ...
        def distance_to(self, other: "Point") -> float: ...
    # tvm-ffi-stubgen(end)
```

`@c_class` 主要参数：`frozen`（只读）、`init`（自动生成`__init__`）、`repr`、`eq`、`order`（比较运算符）、`unsafe_hash`。

### @py_class：定义 Python 端反射对象

`@py_class` 装饰器定义纯 Python 实现的反射对象，可被 C++ 通过 type_key 访问：

```python
from tvm_ffi.dataclasses import py_class, field

@py_class(type_key="demo.Config")
class Config:
    batch_size: int
    lr: float = 0.001
    device: str = field(default="cpu", kw_only=True)
    _cache: dict = field(init=False, default_factory=dict)
```

### 辅助函数

`dataclasses` 模块提供：`fields()`、`asdict()`、`astuple()`、`replace()`、`is_dataclass()`。

## 自动 stub 生成（tvm-ffi-stubgen）

`tvm-ffi-stubgen` 命令行工具从 C++ 编译后的反射元数据自动生成 Python 类型桩。

### 基本用法

```bash
tvm-ffi-stubgen python           # 生成到当前目录
tvm-ffi-stubgen python -o ./stubs/  # 指定输出目录
```

### 内联 stub 块标记

在 Python 类中使用特殊注释标记 stub 生成区域，`begin`/`end` 之间的内容会被自动更新：

```python
# tvm-ffi-stubgen(begin): object/demo.Point
# 此区域内容由 stubgen 自动维护
x: float
y: float
if TYPE_CHECKING:
    def __init__(self, x: float = 0, y: float = 0) -> None: ...
# tvm-ffi-stubgen(end)
```

生成的 stub 支持 IDE 自动补全、类型检查、参数提示，C++ 修改后重新运行 stubgen 即可同步。

## 反射与 Any/Object/Function 的关系

反射系统建立在 Object 系统之上：所有可反射类型继承自 `Object`，通过 `type_key`/`type_index` 查找元数据，字段访问通过偏移量直接操作内存。

反射注册的方法自动包装为 `Function` 对象，方法名成为全局函数名（如 `"demo.Point.distance_to"`），第一个参数隐式为 `self`，可通过 `Function::GetGlobal()` 获取。

`extra/dataclass.h` 中的通用操作完全通过反射元数据实现：

| 函数 | 功能 |
|------|------|
| `DeepCopy(any)` | 递归深拷贝 |
| `ReprPrint(any)` | 人类可读表示（处理循环引用） |
| `RecursiveHash(any)` | 递归哈希 |
| `RecursiveEq/Lt/Le/Gt/Ge` | 结构比较 |

所有操作使用迭代 DFS（显式栈）避免深层对象栈溢出。

## 完整示例

### C++ 端

```cpp
// user.h
#pragma once
#include <tvm/ffi/tvm_ffi.h>
#include <tvm/ffi/extra/dataclass.h>

namespace demo {
namespace ffi = tvm::ffi;
namespace refl = tvm::ffi::reflection;

class UserObj : public ffi::Object {
 public:
  int64_t id;
  ffi::String name;
  int32_t age;
  bool active;
  static constexpr bool _type_mutable = true;

  UserObj(int64_t id, ffi::String name, int32_t age = 18)
      : id(id), name(std::move(name)), age(age), active(true) {}
  void Deactivate() { active = false; }
  ffi::String Greet() const { return "Hello, " + name; }

  TVM_FFI_DECLARE_OBJECT_INFO_FINAL("demo.User", UserObj, ffi::Object);
};

class User : public ffi::ObjectRef {
 public:
  User(int64_t id, ffi::String name, int32_t age = 18)
      : ObjectRef(ffi::make_object<UserObj>(id, std::move(name), age)) {}
  TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE(User, ffi::ObjectRef, UserObj);
};
}  // namespace demo

// user.cc
#include "user.h"
TVM_FFI_STATIC_INIT_BLOCK() {
  using namespace demo;
  refl::ObjectDef<UserObj>()
      .def_rw("id", &UserObj::id)
      .def_rw("name", &UserObj::name)
      .def_rw("age", &UserObj::age, refl::default_(18))
      .def_rw("active", &UserObj::active, refl::default_(true))
      .def("greet", &UserObj::Greet)
      .def("deactivate", &UserObj::Deactivate);
}
```

### Python 端使用

```python
from tvm_ffi.dataclasses import c_class
from typing import TYPE_CHECKING

@c_class("demo.User", repr=True, eq=True)
class User(tvm_ffi.Object):
    # tvm-ffi-stubgen(begin): object/demo.User
    id: int
    name: str
    age: int
    active: bool
    if TYPE_CHECKING:
        def __init__(self, id: int, name: str, age: int = 18) -> None: ...
        def greet(self) -> str: ...
        def deactivate(self) -> None: ...
    # tvm-ffi-stubgen(end)

alice = User(1, "Alice", 25)
bob = User(2, "Bob")

print(alice.name)      # Alice
print(alice.greet())   # Hello, Alice
alice.deactivate()
print(alice.active)    # False
```

## 常见问题

**Q: 字段类型不支持怎么办？**
内置支持基本类型、`String`、`Array`/`List`/`Map`/`Dict`、`Optional`、`Variant` 及其他反射 Object。自定义类型需提供 `ffi::Any` 转换特化或注册遍历钩子。

**Q: 方法重载支持吗？**
C++ 端不支持同名方法重载，后注册会覆盖先注册。建议使用不同名称或 `Variant` 参数分发。

**Q: 反射注册顺序重要吗？**
基类必须在派生类之前注册；同一类型不可重复注册；类型引用通过 `type_key` 延迟解析，无需被引用类型已注册。

**Q: frozen=True 后真的不能修改吗？**
仅在 Python 端阻止常规赋值（`obj.x = 1` 抛异常），C++ 端仍可写，Python 可通过 `type(obj).x.set(obj, val)` 逃逸口修改。

**Q: 如何自定义 __repr__？**
C++ 端可注册 `__ffi_repr__` 类型属性钩子；Python 端在类体中自定义 `__repr__`，`@c_class(repr=True)` 不会覆盖用户定义。

---

← 上一页：[Container 容器类型](05-containers.md) | 下一页 → [Module 模块系统](07-module-system.md)
