---
id: "tvm-ffi-python-guide"
title: "Python 开发指南"
tags: ["tvm-ffi", "python", "guide", "cython"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# Python 开发指南

本指南介绍如何在 Python 中使用 TVM-FFI，包括环境配置、核心 API、容器类型、反射类、模块加载和最佳实践。

## 环境准备

### 版本要求

- **Python ≥ 3.8**（标准 ABI）
- **Python ≥ 3.13**（free-threading 无 GIL 模式支持）
- **Cython ≥ 3.0**（源码编译时需要）

### 安装方式

**pip 安装（推荐）**：`pip install apache-tvm-ffi`

**源码编译**：
```bash
git clone https://github.com/apache/tvm-ffi.git && cd tvm-ffi && pip install -e .
```

**验证安装**：
```python
import tvm_ffi
```

## 核心 API 快速入门

### 获取全局函数

`get_global_func(name)` 获取已注册的全局函数（C++/Python 注册的均可）：

```python
import tvm_ffi

fecho = tvm_ffi.get_global_func("testing.echo")
assert fecho(1) == 1
assert fecho("hello") == "hello"
```

### 注册 Python 函数到全局

`register_global_func` 将 Python 函数注册到 FFI 注册表，可被 C++ 调用：

```python
import tvm_ffi

@tvm_ffi.register_global_func("myexample.add_one")
def add_one(a):
    return a + 1

tvm_ffi.register_global_func("myexample.mul", lambda x, y: x * y)

f_add = tvm_ffi.get_global_func("myexample.add_one")
assert f_add(1) == 2
assert tvm_ffi.get_global_func("myexample.mul")(3, 4) == 12
```

## 容器类型使用

TVM FFI 提供四种容器：

| 类型 | 可变性 | Python ABC | 语义 |
|------|--------|------------|------|
| `Array` | 不可变 | `Sequence[T]` | 同构序列（写时复制） |
| `List` | 可变 | `MutableSequence[T]` | 同构序列（共享引用） |
| `Map` | 不可变 | `Mapping[K, V]` | 同构映射（写时复制） |
| `Dict` | 可变 | `MutableMapping[K, V]` | 同构映射（共享引用） |

### Array/List 使用

```python
import tvm_ffi

# Array（不可变，类似 tuple）
arr = tvm_ffi.convert([1, 2, 3, 4])
assert isinstance(arr, tvm_ffi.Array)
assert arr[0] == 1
# arr[0] = 10  # TypeError

# List（可变）
lst = tvm_ffi.List([1, 2, 3])
lst.append(4)
lst[0] = 10
assert lst[0] == 10
```

### Map/Dict 使用

```python
import tvm_ffi

# Map（不可变）
m = tvm_ffi.convert({"a": 1, "b": 2})
assert isinstance(m, tvm_ffi.Map)
assert m["a"] == 1
# m["c"] = 3  # TypeError

# Dict（可变）
d = tvm_ffi.Dict({"a": 1, "b": 2})
d["c"] = 3
del d["a"]
assert "a" not in d
```

Python `str` 与 FFI `String` 自动双向转换。

### Tensor 与 numpy/PyTorch 零拷贝互操作

Tensor 遵循 [DLPack](https://dmlc.github.io/dlpack/latest/) 标准：

```python
import tvm_ffi
import numpy as np

# numpy → tvm_ffi.Tensor（零拷贝）
np_data = np.array([1, 2, 3, 4], dtype=np.float32)
tvm_tensor = tvm_ffi.from_dlpack(np_data)

# tvm_ffi.Tensor → numpy（零拷贝）
np_result = np.from_dlpack(tvm_tensor)
assert np.allclose(np_data, np_result)

# 支持 torch.Tensor（零拷贝）
try:
    import torch
    t = torch.tensor([1, 2, 3], dtype=torch.float32)
    t2 = torch.from_dlpack(tvm_ffi.from_dlpack(t))
except ImportError:
    pass
```

**关键特性**：自动类型转换、零拷贝、CUDA stream 透传。

## 定义 Python 反射类（@py_class）

使用 `@py_class` 装饰器定义 Python 端反射类，可被 C++ 调用：

```python
import tvm_ffi
from tvm_ffi.dataclasses import py_class, field
from tvm_ffi.dataclasses.py_class import method

@py_class("myexample.Point")
class Point(tvm_ffi.Object):
    x: float
    y: float
    label: str = field(default="point", kw_only=True)

    @method
    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

p1 = Point(1.0, 2.0, label="A")
p2 = Point(4.0, 6.0)
assert p1.distance_to(p2) == 5.0
```

常用参数：`type_key`、`frozen`（只读）、`init`、`repr`、`structural_eq`。

## 使用 C++ 反射对象（@c_class）

使用 `@c_class` 映射 C++ 端定义的反射对象：

```python
import tvm_ffi
from tvm_ffi.dataclasses import c_class

@c_class("testing.TestIntPair")
class TestIntPair(tvm_ffi.Object):
    a: int
    b: int

obj = TestIntPair(10, 20)
assert obj.a == 10
assert obj.b == 20
```

**自动 stub 生成**：使用 `tvm-ffi-stubgen --module my_module --output stubs/` 生成类型提示，获得 IDE 支持。

## 加载 C++ 模块

### load_module 加载预编译动态库

```python
import tvm_ffi

mod = tvm_ffi.load_module("path/to/mylib.so")
result = mod.my_function(arg1, arg2)
metadata = mod.get_function_metadata("my_function")
doc = mod.get_function_doc("my_function")
```

**注意生命周期**：模块返回对象（如 Tensor）的析构函数在动态库中，确保 Module 在所有对象销毁后才卸载。

### system_lib 静态链接库

```python
import tvm_ffi
mod = tvm_ffi.system_lib("testing.")
assert mod["add_one"](10) == 11
```

## 函数回调

将 Python 函数作为回调传给 C++：

```python
import tvm_ffi

fapply = tvm_ffi.get_global_func("testing.apply")  # C++: (f, val) => f(val)

assert fapply(lambda x: x * 2 + 1, 5) == 11

# 闭包捕获
factor = 10
assert fapply(lambda x: x * factor, 3) == 30
```

## inline_module 即时编译

通过 `tvm_ffi.cpp.load_inline()` 在 Python 中嵌入 C++ 代码即时编译：

```python
import tvm_ffi
import tvm_ffi.cpp
import numpy as np

cpp_source = r"""
void add_one_cpu(tvm::ffi::TensorView x, tvm::ffi::TensorView y) {
    TVM_FFI_ICHECK(x.ndim() == 1);
    DLDataType f32{kDLFloat, 32, 1};
    TVM_FFI_ICHECK(x.dtype() == f32);
    TVM_FFI_ICHECK(y.ndim() == 1);
    TVM_FFI_ICHECK(y.dtype() == f32);
    TVM_FFI_ICHECK(x.size(0) == y.size(0));
    for (int i = 0; i < x.size(0); ++i) {
        static_cast<float*>(y.data_ptr())[i] =
            static_cast<float*>(x.data_ptr())[i] + 1;
    }
}
"""

mod = tvm_ffi.cpp.load_inline(
    name="add_one_demo",
    cpp_sources=cpp_source,
    functions=["add_one_cpu"]
)

x = np.array([1, 2, 3, 4, 5], dtype=np.float32)
y = np.empty_like(x)
mod.add_one_cpu(x, y)
np.testing.assert_equal(x + 1, y)
```

常用参数：`name`、`cpp_sources`、`cuda_sources`、`functions`、`build_directory`。

## 测试工具：tvm_ffi.testing

```python
from tvm_ffi.testing import (
    add_one,           # add_one(x) => x+1
    TestIntPair,       # 测试对象
    run_with_gpu_lock, # GPU 测试锁
)
assert add_one(41) == 42
```

## 最佳实践

1. **使用 @c_class 获得类型提示**：为 C++ 反射对象定义包装类并加类型注解，获得 IDE 补全和类型检查。

2. **注意 Tensor 生命周期**：推荐嵌套函数模式确保对象先于 Module 销毁：
   ```python
   def process():
       mod = tvm_ffi.load_module("kernel.so")
       def run():
           out = mod.compute(x, y)
       run()
   ```

3. **用 dataclass 代替 dict**：`@py_class`/`@c_class` 提供类型安全、更快访问、支持结构相等。

## 常见问题

**Q: 找不到全局函数？**
- 检查函数名拼写和命名空间前缀
- 确认模块已加载
- 用 `tvm_ffi.list_global_func_names()` 列出所有已注册函数

**Q: 类型转换错误？**
- 检查容器元素类型一致性
- 检查 Tensor dtype/device
- 自定义类型实现 `__tvm_ffi_value__` 协议
- 用 `tvm_ffi.convert()` 显式转换

**Q: GIL 和多线程？**
- FFI 调用期间自动释放 GIL
- Python 回调重新获取 GIL
- Python 3.13+ free-threading 无 GIL
- GPU kernel 异步启动，注意 stream 同步

## 关键引用

- `python/tvm_ffi/`（源项目归档路径） - Python 包源码
- `docs/guides/python_lang_guide.md`（源项目归档路径） - 官方 Python 指南

---

← 上一页：[C++ 开发指南](08-cpp-guide.md) | 下一页 → [构建与打包](10-build-packaging.md)
