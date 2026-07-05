---
title: "07 - Python 绑定机制"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm-ffi, ffi, python, cuda, jit, dlpack]
---

# Python 绑定机制

TVM FFI 通过 Cython 实现 Python 与 C++ 的高效互操作。Python 包名为 `tvm_ffi`，提供了与 C++ API 一一对应的函数接口，支持自动类型转换、函数注册与回调、对象反射等核心能力。

## Python 包结构

```
python/tvm_ffi/
├── __init__.py          # 包入口，导出核心 API
├── _ffi_api.py          # 核心 FFI API 实现
├── _cython/             # Cython 扩展模块
│   ├── base.pyx
│   ├── _typing.pyx
│   └── ...
└── ...
```

主要入口文件：
- `python/tvm_ffi/__init__.py` - 导出所有公开 API
- `python/tvm_ffi/_ffi_api.py` - 核心 FFI 功能实现

## 核心 API

### register_func - 函数注册

`register_func` 支持两种使用方式：装饰器模式和函数调用模式。

**Python 示例：**
```python
from tvm_ffi import register_func, get_global_func

# 方式1：装饰器模式
@register_func("my_module.add")
def add(a, b):
    return a + b

# 方式2：函数调用模式
def multiply(a, b):
    return a * b

register_func("my_module.multiply", multiply)
```

**C++ 示例（注册函数供 Python 调用）：**
```cpp
#include <tvm/ffi/ffi.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("my_module.cpp_add")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        int a = args[0].cast<int>();
        int b = args[1].cast<int>();
        rv = a + b;
    });

TVM_FFI_REGISTER_GLOBAL("my_module.cpp_greet")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        std::string name = args[0].cast<std::string>();
        rv = std::string("Hello, ") + name;
    });
```

### get_global_func - 获取全局函数

通过函数名获取已注册的全局函数句柄，支持透明调用。

**Python 示例：**
```python
from tvm_ffi import get_global_func

# 获取 C++ 注册的函数
cpp_add = get_global_func("my_module.cpp_add")
result = cpp_add(3, 5)
print(result)  # 输出: 8

cpp_greet = get_global_func("my_module.cpp_greet")
print(cpp_greet("World"))  # 输出: Hello, World
```

### convert - 类型转换

`convert` 函数实现 Python 类型与 FFI 类型的双向自动转换。

**Python 示例：**
```python
from tvm_ffi import convert

# Python -> FFI 类型
ffi_int = convert(42)          # Int
ffi_float = convert(3.14)      # Float
ffi_str = convert("hello")     # String
ffi_list = convert([1, 2, 3])  # Array
ffi_dict = convert({"a": 1})   # Dict
ffi_none = convert(None)       # None

# FFI 类型 -> Python（隐式转换，无需手动调用）
```

## 类型映射表

| Python 类型 | FFI 类型 | C++ 类型 | 说明 |
|------------|---------|---------|------|
| `int` | `Int` | `int64_t` | 整数类型 |
| `float` | `Float` | `double` | 浮点数类型 |
| `str` | `String` | `std::string` | 字符串类型 |
| `list` | `Array` | `Array<T>` | 动态数组 |
| `dict` | `Dict` | `Map<K,V>` | 键值对映射 |
| `None` | `None` | `nullptr_t` | 空值 |
| `numpy.ndarray` | `Tensor` | `Tensor` | 张量（零拷贝） |
| `callable` | `Function` | `PackedFunc` | 可调用对象 |

## C++ 与 Python 互调用

### Python 调用 C++ 函数

参数和返回值会自动进行类型转换，无需手动处理。

**C++ 端注册函数：**
```cpp
#include <tvm/ffi/ffi.h>
#include <tvm/ffi/container/array.h>
#include <tvm/ffi/container/map.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("demo.process_data")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        // 自动类型转换：args 中的 Python 值转为 C++ 类型
        Array<int> numbers = args[0].cast<Array<int>>();
        Map<std::string, int> config = args[1].cast<Map<std::string, int>>();
        
        int sum = 0;
        for (int x : numbers) {
            sum += x;
        }
        
        int multiplier = config["multiplier"];
        rv = sum * multiplier;
    });
```

**Python 端调用：**
```python
from tvm_ffi import get_global_func

process_data = get_global_func("demo.process_data")
data = [1, 2, 3, 4, 5]
config = {"multiplier": 10}
result = process_data(data, config)
print(result)  # 输出: 150 (15 * 10)
```

### C++ 调用 Python 回调函数

Python 函数可以作为参数传递给 C++ 函数，C++ 端通过 `Function` 类型调用。

**C++ 端接受回调：**
```cpp
#include <tvm/ffi/ffi.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("demo.apply_transform")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        Array<int> data = args[0].cast<Array<int>>();
        Function transform = args[1].cast<Function>();
        
        Array<int> result;
        for (int x : data) {
            // 调用 Python 回调函数
            int transformed = transform(x).cast<int>();
            result.push_back(transformed);
        }
        rv = result;
    });
```

**Python 端传递回调：**
```python
from tvm_ffi import get_global_func

apply_transform = get_global_func("demo.apply_transform")

# 传递 Python lambda 作为回调
result = apply_transform([1, 2, 3, 4], lambda x: x * x)
print(result)  # 输出: [1, 4, 9, 16]

# 传递具名函数
def add_one(x):
    return x + 1

result2 = apply_transform([1, 2, 3], add_one)
print(result2)  # 输出: [2, 3, 4]
```

## 对象反射与自动类生成

TVM FFI 支持从 C++ `ObjectDef` 自动生成 Python 类，使用 `dataclasses.c_class` 装饰器。

**C++ 定义对象：**
```cpp
#include <tvm/ffi/ffi.h>
#include <tvm/ffi/object.h>

using namespace tvm::ffi;

struct MyPoint : public Object {
    double x;
    double y;
    
    TVM_FFI_DECLARE_OBJECT_INFO(MyPoint, Object)
    TVM_FFI_DEFINE_OBJECT_INFO("demo.MyPoint");
    
    // 对象方法
    double norm() const {
        return std::sqrt(x * x + y * y);
    }
};

TVM_FFI_REGISTER_OBJECT(MyPoint)
    .add_field("x", &MyPoint::x)
    .add_field("y", &MyPoint::y)
    .add_method("norm", &MyPoint::norm);
```

**Python 中使用反射类：**
```python
from tvm_ffi import dataclasses
from tvm_ffi.dataclasses import c_class

# 自动从 C++ 反射生成类
@c_class("demo.MyPoint")
class MyPoint:
    x: float
    y: float
    
    def norm(self) -> float:
        ...

# 创建实例
p = MyPoint(3.0, 4.0)
print(p.x, p.y)  # 输出: 3.0 4.0
print(p.norm())  # 输出: 5.0

# 访问 C++ 方法
print(p.norm())
```

## 类型存根生成（tvm-ffi-stubgen）

`tvm-ffi-stubgen` 工具从 C++ 反射注册表生成 Python 类型存根（`.pyi` 文件），提供 IDE 类型提示支持。

**使用方式：**
```bash
# 为编译出的模块生成存根
tvm-ffi-stubgen --module my_module --output ./stubs/

# 或指定库路径
tvm-ffi-stubgen --lib ./build/libmy_module.so --output ./stubs/
```

生成的存根示例：
```python
# stubs/my_module/__init__.pyi
from typing import Callable, Any

def cpp_add(a: int, b: int) -> int: ...
def cpp_greet(name: str) -> str: ...
def process_data(numbers: list[int], config: dict[str, int]) -> int: ...
def apply_transform(data: list[int], transform: Callable[[int], int]) -> list[int]: ...
```

## NumPy 数组互操作

TVM FFI Tensor 与 NumPy ndarray 实现零拷贝互操作。

**Python 示例：**
```python
import numpy as np
from tvm_ffi import get_global_func

# C++ 函数接收 Tensor
process_tensor = get_global_func("demo.double_tensor")

arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)
result = process_tensor(arr)
print(result)  # NumPy 数组: [2.0, 4.0, 6.0]
```

**C++ 端：**
```cpp
#include <tvm/ffi/container/tensor.h>

TVM_FFI_REGISTER_GLOBAL("demo.double_tensor")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        Tensor t = args[0].cast<Tensor>();
        // 直接操作数据，零拷贝
        float* data = static_cast<float*>(t->data);
        for (int i = 0; i < t->shape[0]; i++) {
            data[i] *= 2;
        }
        rv = t;
    });
```

## 源码引用

- `python/tvm_ffi/__init__.py` - 包入口
- `python/tvm_ffi/_ffi_api.py` - 核心 FFI API

---

**导航：**
- [上一章：06 - 序列化](06-serialization.md)
- [返回目录](README.md)
- [下一章：08 - CUDA 支持](08-cuda-support.md)
