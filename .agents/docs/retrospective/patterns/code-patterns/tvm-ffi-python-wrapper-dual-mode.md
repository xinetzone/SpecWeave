---
id: "tvm-ffi-python-wrapper-dual-mode"
source: "caffe-ffi 日志框架与Python Wrapper修复实践 (2026-07-28)"
status: "candidate"
maturity: "L1"
validation_count: 1
reuse_count: 0
---
# TVM-FFI Python Wrapper 双模式包装模式

> ⚠️ **候选模式状态**：本模式基于单一案例（caffe-ffi）萃取，等待第二个支撑案例验证后升级为正式模式。单案例可能是特定环境的产物，请勿在关键路径盲目套用。

## 模式概述

使用 TVM-FFI（或类似 Cython 扩展类型的 FFI 框架）将 C++ 对象暴露给 Python 时，C++ 返回的对象通过 C API 直接设置 `_handle` 并绕过 Python 层的 `__init__`，导致 `__init__` 中初始化的 Python 属性不存在。必须同时满足**五要素**（继承 Object、声明 _type_key、__slots__、__new__ 初始化、双模式分发）才能保证两种来源（Python 创建/C++ 返回）的对象行为一致。

## 触发场景

- 使用 TVM-FFI 或类似 Cython/Pybind11 FFI 框架包装 C++ 对象到 Python
- Python 包装类出现 `AttributeError: 'Xxx' object has no attribute '_handle'`
- Python 包装类出现 `AttributeError: 'Xxx' object has no attribute '_py_xxx'`
- C++ 返回的对象在 Python 端调用方法时属性缺失
- FFI 框架创建的 Cython 扩展类型不支持动态属性赋值（无 `__dict__`）

## 核心步骤

### 五要素模板

```python
import tvm_ffi
from typing import List, Optional, Any
import numpy as np

class WrapperClass(tvm_ffi.Object):
    # 要素1：声明与 C++ TVM_FFI_REGISTER_OBJECT 一致的 _type_key
    _type_key = "namespace.ClassName"
    
    # 要素2：__slots__ 显式声明所有 Python 端属性（Cython扩展类型无__dict__）
    __slots__ = ['_py_attr1', '_py_attr2', '_py_mode']
    
    # 要素3：使用 __new__ 而非 __init__ 初始化 Python 属性
    # C++ 返回对象时绕过 __init__，但 __new__ 总是被调用
    def __new__(cls, arg1=None, handle=None):
        inst = super().__new__(cls)
        inst._py_attr1 = default_value1
        inst._py_attr2 = default_value2
        inst._py_mode = "python"  # 或通过handle判断
        return inst
    
    # 要素4：_is_native 属性区分 C++ 后端 vs 纯 Python 后备
    @property
    def _is_native(self) -> bool:
        return bool(getattr(self, '_handle', None))
    
    # 要素5：方法分发——根据 _is_native 调用 C++ FFI 或 Python 实现
    def method(self, *args, **kwargs):
        if self._is_native:
            # 调用 C++ 实现：通过 tvm_ffi.core.Object 分发
            return tvm_ffi.core.Object.method(self, *args, **kwargs)
        else:
            # 纯 Python 后备实现
            return self._py_method_impl(*args, **kwargs)
```

### 关键要点

1. **`_type_key` 必须精确匹配** C++ 端 `TVM_FFI_REGISTER_OBJECT("namespace.ClassName")` 的字符串，差一个字符就会导致 FFI 类型查找失败
2. **`__slots__` 必须列出所有** Python 端自定义属性，Cython 扩展类型不支持 `__dict__`，动态赋值会抛 `AttributeError`
3. **`__new__` 而非 `__init__`**：`__init__` 只在 Python 端 `WrapperClass(args)` 时调用，C++ 返回对象时走 `__new__` → C API 直接填 `_handle`，不经过 `__init__`
4. **双模式 `_is_native`**：通过 `_handle` 是否存在判断对象是 C++ 后端（有 `_handle`）还是纯 Python 后备模式（无 `_handle`）
5. **方法分发显式调用**：C++ 方法必须通过 `tvm_ffi.core.Object.method(self, ...)` 显式分发，不能用 `super().method()`，因为 MRO 会走到 Python 自身

## 反模式

### ❌ 反模式1：只实现 __init__ 不用 __new__
```python
class Blob:  # 错误：未继承 tvm_ffi.Object
    def __init__(self, shape=None):
        self._py_shape = []  # C++返回对象时__init__不执行，_py_shape不存在
```
结果：C++ 通过 FFI 返回的 Blob 对象调用 `self._py_shape` 时抛 `AttributeError`。

### ❌ 反模式2：继承 tvm_ffi.Object 但不用 __slots__
```python
class Blob(tvm_ffi.Object):
    def __init__(self, shape=None):
        self._py_shape = []  # Cython扩展类型无__dict__，动态赋值失败
```
结果：`AttributeError: 'Blob' object has no attribute '_py_shape'`——即使在 `__init__` 里赋值也不行，因为 `_py_shape` 未在 `__slots__` 中声明。

### ❌ 反模式3：用 super().method() 分发
```python
def Reshape(self, shape):
    if self._is_native:
        super().Reshape(shape)  # 错误：MRO可能走到Python自身的Reshape而非C++实现
```
结果：无限递归或调用到 Python 后备实现而非 C++ 原生方法。

### ❌ 反模式4：假设对象总是有 _handle
```python
def Reshape(self, shape):
    self._check_handle()  # 错误：纯Python后备模式下_handle不存在
    tvm_ffi.core.Object.Reshape(self, shape)
```
结果：纯 Python 模式创建的对象（如测试桩）调用 Reshape 时崩溃。

## 迁移验证

- ✅ caffe-ffi 项目：Blob/Layer/Net 三个核心类按五要素实现，Python创建对象和C++返回对象（如 `net.blob_by_name("data")`）均正常工作
- ⏳ 等待第二案例：demo_ffi 或其他 tvm-ffi 子项目中验证

## 适用条件

- FFI 框架：TVM-FFI（Pybind11/pybind11 的 `py::return_value_policy::take_ownership` 场景类似但机制不同）
- 对象来源混合：既有 Python 端直接构造的对象，又有 C++ 方法返回的对象
- 双模式需求：需要纯 Python 后备模式（如测试桩、CPU fallthrough）
- 不适用场景：纯 Python 类（无需 FFI）、Pybind11 绑定（使用 `py::class_` 机制，不需要五要素）

## 升级标准（candidate → 正式）

当满足以下任一条件时升级为正式 L2 模式：
1. 在第二个独立项目（如 demo_ffi、xmnn、或其他 tvm-ffi 绑定）中验证五要素全部必要
2. 发现 _type_key 与 C++ 不一致导致的错误至少2次，形成反模式验证
3. 验证 pybind11 等其他 FFI 框架是否需要类似模式，明确适用边界
