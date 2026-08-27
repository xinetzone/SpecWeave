---
type: Concept
title: "视角120：register_global_func"
description: "分析TVM FFI中全局函数注册的装饰器设计，包括双参数调用模式、命名解析、覆盖控制等机制。"
tags:
  - python
  - function
  - registration
  - decorator
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-342, F-343, F-344, F-345
  - code:
    - python/tvm_ffi/registry.py
    - python/tvm_ffi/_ffi_api.py
---

# 视角120：register_global_func

## 概述

`register_global_func`是TVM FFI中用于注册Python函数到C++全局函数注册表的装饰器。它支持两种调用模式：装饰器模式和直接调用模式，提供灵活的功能注册方式。

## 函数签名

```python
# python/tvm_ffi/registry.py:110-114
def register_global_func(
    func_name: str | Callable[..., Any],
    f: Callable[..., Any] | None = None,
    override: bool = False,
) -> Any:
    ...
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `func_name` | `str \| Callable` | - | 函数名或函数对象 |
| `f` | `Callable \| None` | `None` | 函数对象（装饰器模式时省略） |
| `override` | `bool` | `False` | 是否覆盖已存在的注册 |

## 双参数调用模式

### 装饰器模式

```python
# python/tvm_ffi/registry.py:161-174
if not isinstance(func_name, str):
    f = func_name
    func_name = f.__name__

if not isinstance(func_name, str):
    raise ValueError("expect string function name")

def register(myf: Callable[..., Any]) -> Any:
    return core._register_global_func(func_name, myf, override)

if f is not None:
    return register(f)
return register
```

当`func_name`是函数对象时，自动提取`__name__`作为注册名。

### 直接调用模式

```python
# 示例
tvm_ffi.register_global_func("my.add_one", lambda x: x + 1)
```

## 命名解析策略

### 从函数名提取

```python
# python/tvm_ffi/registry.py:162-163
if not isinstance(func_name, str):
    f = func_name
    func_name = f.__name__
```

如果传入函数对象，使用函数的`__name__`属性作为注册名。

### 全限定名支持

支持使用`.`分隔的命名空间：
```python
@tvm_ffi.register_global_func("tvm.ir.Op")
def my_op(...):
    ...
```

## override参数

### 默认行为（override=False）

如果目标名称已注册，会抛出异常：
```python
# core._register_global_func内部逻辑
if name in registry and not override:
    raise RuntimeError(f"Function '{name}' is already registered")
```

### 覆盖模式（override=True）

允许覆盖已注册的函数：
```python
@tvm_ffi.register_global_func("my.func", override=True)
def my_func():
    pass
```

## 与init_ffi_api的配合

### 自动导出机制

`init_ffi_api`会自动将所有注册的全局函数导出到Python模块：

```python
# python/tvm_ffi/_ffi_api.py
_FFI_INIT_FUNC("ffi", __name__)
```

这等价于：
```python
for name in list_global_func_names():
    if name.startswith("ffi."):
        fname = name[4:]
        f = get_global_func(name)
        setattr(sys.modules[__name__], fname, f)
```

### 命名空间映射

不同模块使用不同前缀：
- `tvm.ir._ffi_api`：导出所有`tvm.ir.*`函数
- `tvm.tir._ffi_api`：导出所有`tvm.tir.*`函数
- `tvm_ffi._ffi_api`：导出所有`ffi.*`函数

## get_global_func配套

### 获取已注册函数

```python
# python/tvm_ffi/registry.py:185-221
def get_global_func(name: str, allow_missing: bool = False) -> core.Function | None:
    return core._get_global_func(name, allow_missing)
```

### 元数据查询

```python
# python/tvm_ffi/registry.py:271-303
def get_global_func_metadata(name: str) -> dict[str, Any]:
    metadata_json = get_global_func("ffi.GetGlobalFuncMetadata")(name)
    return json.loads(metadata_json) if metadata_json else {}
```

## list_global_func_names

### 获取所有注册函数

```python
# python/tvm_ffi/registry.py:224-235
def list_global_func_names() -> list[str]:
    name_functor = get_global_func("ffi.FunctionListGlobalNamesFunctor")()
    num_names = name_functor(-1)
    return [name_functor(i) for i in range(num_names)]
```

使用`FunctionListGlobalNamesFunctor`获取函数列表，避免重复查询。

## remove_global_func

### 注销函数

```python
# python/tvm_ffi/registry.py:238-268
def remove_global_func(name: str) -> None:
    get_global_func("ffi.FunctionRemoveGlobal")(name)
```

## 使用示例

### 基本注册

```python
import tvm_ffi

@tvm_ffi.register_global_func("demo.echo")
def echo(x):
    return x

# 使用
f = tvm_ffi.get_global_func("demo.echo")
result = f(42)
assert result == 42
```

### Lambda注册

```python
tvm_ffi.register_global_func("demo.add_one", lambda x: x + 1)
```

### 命名空间注册

```python
@tvm_ffi.register_global_func("tvm.mytest.compute")
def compute(x, y):
    return x + y
```

## 设计分析

### 灵活性

双参数调用模式支持：
- 装饰器语法：`@register_global_func("name")`
- 直接调用：`register_global_func("name", func)`
- 自动命名：传入函数对象时自动使用`__name__`

### 安全性

- 默认禁止覆盖已注册函数
- 提供`override`参数显式控制覆盖行为
- 函数名必须是字符串，防止意外注册

### 集成性

与`init_ffi_api`无缝集成：
- 注册后立即可通过全局函数表访问
- 自动参与模块导出流程
- 支持命名空间隔离

## 扩展讨论

### 装饰器模式与直接调用模式的本质统一

双参数调用的关键是 Python 装饰器「`@f` 参数被隐式注入」的求值顺序：当 `register_global_func("name")` 返回 `register` 闭包，装饰器语法把它再套在函数上；而直接调用 `register_global_func("name", f)` 则立刻对该闭包求值。两种形式最终都走到 `core._register_global_func(func_name, myf, override)`，与 C++ 侧 `TVMFFIFunctionSetGlobal` 的语义对齐——后者同样以「名 + 可调用对象 + 覆盖标志」三元组写入全局注册表。

### override 的双刃属性

默认拒绝重复注册是安全红线：它保证同一 `name` 只被定义一次，避免跨模块的静默覆盖。但测试替身、后端切换等场景需要显式 `override=True` 重绑定。注意覆盖只影响运行时查找，已通过 `get_global_func` 捕获的 `Function` 句柄仍指向旧实现——因此覆盖通常须在程序早期、任何句柄被缓存之前完成。

### 与 Free-threaded 注册表的一致性

全局函数注册表本质是一个进程级键值表。在自由线程 Python（视角 123）下，`register_global_func` 若不加锁保护，多线程同时注册会破坏表结构；因此注册侧须保证写操作的互斥性，而读侧 `get_global_func` 依赖表在初始化完成后只读的固有时序。这也是扩展库把注册集中到 import 期而非懒执行的原因。

## 相关概念

- [117 _ffi_api模块模式](117-_ffi-api-module-pattern.md)：模块自动导出机制
- [118 Python对象注册](118-python-object-registration.md)：对象注册机制对比
- [121 Python错误转换](121-python-error-conversion.md)：错误处理机制
