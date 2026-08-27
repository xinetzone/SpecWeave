---
type: Concept
title: "视角125：core.pyi类型存根"
description: "分析tvm_ffi.core模块的类型存根文件，包括Cython扩展类的类型注解、Protocol定义和类型映射。"
tags:
  - python
  - stub
  - typing
  - cython
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-335, F-336
  - code:
    - python/tvm_ffi/core.pyi
    - python/tvm_ffi/cython/core.pyx
---

# 视角125：core.pyi类型存根

## 概述

`core.pyi`是`tvm_ffi.core`模块的类型存根文件，为Cython扩展类提供完整的类型注解。这些存根由`tvm-ffi-stubgen`工具自动生成，确保IDE类型检查和静态分析工具的准确性。

## 存根文件结构

### 文件头部

```python
# python/tvm_ffi/core.pyi
"""Type stubs for tvm_ffi.core Cython extension."""
from __future__ import annotations
from typing import Any, Callable, Sequence, Mapping, overload
from ._tensor import Device, DLDeviceType, Tensor, Shape
```

### 导入声明

存根文件使用`TYPE_CHECKING`条件导入：
```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .core import Object, Function, CAny
```

## Cython类存根

### PyAny存根

```python
# python/tvm_ffi/core.pyi
class PyAny:
    """Type-erased FFI value wrapper."""

    def __init__(self, value: Any = ...) -> None: ...

    # 类型检查方法
    def is_none(self) -> bool: ...
    def is_int(self) -> bool: ...
    def is_float(self) -> bool: ...
    def is_bool(self) -> bool: ...
    def is_string(self) -> bool: ...
    def is_object(self) -> bool: ...
    def is_function(self) -> bool: ...

    # 转换方法
    def cast(self, type_: type) -> Any: ...
    def try_cast(self, type_: type) -> Any | None: ...

    # Python协议
    def __int__(self) -> int: ...
    def __float__(self) -> float: ...
    def __bool__(self) -> bool: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
```

### PyFunction存根

```python
class PyFunction:
    """FFI function wrapper."""

    def __init__(self, handle: int) -> None: ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

    def get_global(self, name: str) -> PyFunction: ...
    def set_global(self, name: str) -> None: ...
    def call_any(self, args: Sequence[Any]) -> Any: ...
```

### Object基类存根

```python
class Object:
    """Base class for all FFI objects."""

    def __init__(self) -> None: ...

    # 类型信息
    @property
    def type_key(self) -> str: ...
    @property
    def type_index(self) -> int: ...

    # 生命周期
    def inc_ref(self) -> None: ...
    def dec_ref(self) -> None: ...
    @property
    def use_count(self) -> int: ...
    @property
    def is_unique(self) -> bool: ...

    # 比较
    def same_as(self, other: Object) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
```

## Protocol定义

### Seqable协议

```python
class Seqable(Protocol):
    """Protocol for sequence-like objects."""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> Any: ...
    def __iter__(self) -> iter: ...
```

### Mapping协议

```python
class MappingProtocol(Protocol):
    """Protocol for mapping-like objects."""

    def __len__(self) -> int: ...
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    def __delitem__(self, key: Any) -> None: ...
    def __contains__(self, key: Any) -> bool: ...
    def keys(self) -> Sequence[Any]: ...
    def values(self) -> Sequence[Any]: ...
    def items(self) -> Sequence[tuple[Any, Any]]: ...
```

## 工厂函数存根

### Array工厂

```python
@overload
def Array(*args: Any) -> Array: ...
@overload
def Array(seq: Sequence[Any]) -> Array: ...
```

### Dict工厂

```python
@overload
def Dict() -> Dict: ...
@overload
def Dict(mapping: Mapping[Any, Any]) -> Dict: ...
@overload
def Dict(pairs: Sequence[tuple[Any, Any]]) -> Dict: ...
```

### List工厂

```python
@overload
def List() -> List: ...
@overload
def List(seq: Sequence[Any]) -> List: ...
```

### Map工厂

```python
@overload
def Map() -> Map: ...
@overload
def Map(mapping: Mapping[Any, Any]) -> Map: ...
```

## Tensor相关存根

### Tensor存根

```python
class Tensor:
    """FFI Tensor object wrapping DLTensor."""

    @property
    def data(self) -> Any: ...
    @property
    def device(self) -> Device: ...
    @property
    def dtype(self) -> DataType: ...
    @property
    def ndim(self) -> int: ...
    @property
    def shape(self) -> tuple[int, ...]: ...
    @property
    def strides(self) -> tuple[int, ...]: ...

    def to_dlpack(self) -> Any: ...
    def numpy(self) -> Any: ...
```

### Shape存根

```python
class Shape(tuple):
    """Shape tuple for tensor dimensions."""

    def __new__(cls, content: tuple[int, ...]) -> Shape: ...
```

## DataType存根

```python
class DataType:
    """Data type descriptor."""

    @classmethod
    def Int(cls, bits: int, lanes: int = 1) -> DataType: ...
    @classmethod
    def UInt(cls, bits: int, lanes: int = 1) -> DataType: ...
    @classmethod
    def Float(cls, bits: int, lanes: int = 1) -> DataType: ...
    @classmethod
    def BFloat(cls, bits: int, lanes: int = 1) -> DataType: ...
    @classmethod
    def Bool(cls, lanes: int = 1) -> DataType: ...
    @classmethod
    def Void(cls) -> DataType: ...

    @property
    def code(self) -> int: ...
    @property
    def bits(self) -> int: ...
    @property
    def lanes(self) -> int: ...

    def is_int(self) -> bool: ...
    def is_uint(self) -> bool: ...
    def is_float(self) -> bool: ...
    def is_bool(self) -> bool: ...
    def is_void(self) -> bool: ...
```

## Device存根

```python
class Device:
    """Device descriptor."""

    def __init__(self, device_type: int, device_id: int = 0) -> None: ...

    @property
    def device_type(self) -> int: ...
    @property
    def device_id(self) -> int: ...

    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
```

## 类型映射

### FFI类型到Python类型

| FFI类型 | Python类型 | 说明 |
|---------|-----------|------|
| `kTVMFFITypeIndexInt64` | `int` | 64位整数 |
| `kTVMFFITypeIndexFloat64` | `float` | 64位浮点 |
| `kTVMFFITypeIndexBool` | `bool` | 布尔值 |
| `kTVMFFITypeIndexString` | `str` | 字符串 |
| `kTVMFFITypeIndexBytes` | `bytes` | 字节序列 |
| `kTVMFFITypeIndexObject` | `Object` | 对象句柄 |
| `kTVMFFITypeIndexFunction` | `Function` | 函数句柄 |
| `kTVMFFITypeIndexTensor` | `Tensor` | 张量对象 |
| `kTVMFFITypeIndexArray` | `Array` | 数组容器 |
| `kTVMFFITypeIndexDict` | `Dict` | 字典容器 |

### 容器类型映射

| C++类型 | Python类型 | 可变性 |
|---------|-----------|--------|
| `ffi::Array<T>` | `Array` | 不可变 |
| `ffi::List<T>` | `List` | 可变 |
| `ffi::Map<K,V>` | `Map` | 不可变 |
| `ffi::Dict` | `Dict` | 可变 |

## 设计分析

### 存根生成策略

1. **从C++反射推断**：根据类型注册表的字段和方法定义生成
2. **Protocol优先**：使用Protocol定义接口，而非具体类
3. **Overload支持**：对多态函数使用`@overload`注解

### 类型安全保证

1. **编译时检查**：IDE可以检查类型使用
2. **运行时验证**：Cython层执行类型检查
3. **双向映射**：C++和Python类型保持一致

### 向后兼容

- 存根文件与实现分离
- 实现变更只需重新生成存根
- 用户代码不受存根变更影响

## 扩展讨论

### 存根与运行时反射的"镜像"关系

`core.pyi` 里 `PyAny`、`PyFunction`、`Object`、`Tensor` 等类的存根并非凭空杜撰，而是 C++ 反射表（`refl::ObjectDef` 注册的字段与方法）在 Python 侧的投影。存根中 `Object.inc_ref/dec_ref` 对应视角 136 的引用计数语义，`Object.type_key` 对应对象经反射登记的类型名。正因为存根源自反射而非手写，实现变更时只需重新运行 `tvm-ffi-stubgen`，就能保持两者一致，避免「存根声明存在但运行时不存在」的漂移。

### Protocol 抽象的价值

`Seqable`、`MappingProtocol` 用 `Protocol`（PEP 544 结构子类型）而非具体类声明接口，使得同一种几何语义可以被 `Array/List/Map/Dict` 多个容器实现共用。调用方只需依赖协议，就能在类型检查层面同时支持 FFI 容器与原生 `list`/`dict`，不必强耦合具体容器类——这对跨语言边界传递数据的上层框架尤为友好。

### 类型映射表与运行时转换的一致性

存根内的「FFI 类型到 Python 类型」映射表（`int64→int`、`object→Object` 等）必须与 `code.pxi` 中转换器实际执行的分派一致。若存根声明某 FFI 符号可映射为某 Python 类型而在转换器中未登记，静态检查与运行时行为就会背离。因此存根生成流水线（视角 124）以转换器分派为唯一输入源，从机制上保证二者同步，而 `DataType/Device` 的只读属性与工厂方法同样复用了 DDLC 的 `code/bits/lanes` 字段约定。

### 存根不只是给 IDE：它也是 FFI 公共 API 的"契约清单"

`core.pyi` 在类型检查层面之外，还承担着一份"FFI 公开接口目录"的职责——`PyAny`/`PyFunction`/`Object`/`Tensor`/`DataType`/`Device` 的可调用成员及其签名，都被存根显式固化。因此它既约束实现（实现必须满足存根声明的成员），又指导使用（调用方按存根书写代码即可被静态校验）。对于跨语言 FFI 这类"边界即接口"的库，存根往往比运行时文档更能精确表达"哪些能力是稳定可依赖的"。

## 相关概念

- [124 存根生成流水线](124-stub-generation-pipeline.md)：存根生成工具设计
- [116 Cython绑定架构](116-cython-binding-architecture.md)：Cython层实现
- [126 dataclass集成](126-dataclass-integration.md)：dataclass存根生成
