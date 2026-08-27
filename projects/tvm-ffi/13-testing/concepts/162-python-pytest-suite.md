---
type: Concept
title: "视角162：Python pytest 套件"
description: "TVM FFI 的 Python 测试套件基于 pytest 框架构建，覆盖容器转换、错误传播、DType 互操作、函数调用、数据类生成等模块，与 C++ GoogleTest 形成互补的测试层次。"
tags:
  - testing
  - python
  - pytest
  - ffi-binding
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-349, F-350
  - code:
    - tests/python/test_container.py
    - tests/python/test_dtype.py
    - tests/python/test_error.py
    - tests/python/test_function.py
    - tests/python/test_tensor.py
    - tests/python/test_string.py
    - tests/python/test_object.py
    - tests/python/test_serialization.py
---

# 视角162：Python pytest 套件

## 概述

TVM FFI 的 Python 测试套件位于 `tests/python/` 目录，使用 pytest 框架执行。与 C++ GoogleTest 形成互补——C++ 测试验证核心类型系统的底层行为，Python 测试验证语言绑定的正确性、Pythonic 交互以及跨语言边界的数据传递。

## 测试文件总览

`tests/python/` 目录下包含 40 个测试文件，主要模块覆盖如下：

| 测试文件 | 测试函数数 | 覆盖模块 |
|---------|----------|---------|
| `test_container.py` | 50+ | Array、List、Map、Dict 的 Python 交互 |
| `test_dtype.py` | 13 | DataType、Device 的 Python API |
| `test_error.py` | 5 | 错误传播、回溯解析、因果链 |
| `test_function.py` | 22 | 函数调用、Lambda、全局注册、不透明对象 |
| `test_tensor.py` | - | Tensor 的 Python API 与 DLPack 交换 |
| `test_string.py` | - | String/Bytes 的 Python 交互 |
| `test_object.py` | - | Object 生命周期与引用计数 |
| `test_serialization.py` | - | 序列化/反序列化的 Python 路径 |
| `test_dataclass_*.py` | - | 数据类生成的完整回归测试 |
| `test_structural*.py` | - | 结构比较与哈希的 Python 验证 |

## 容器测试（test_container.py）

`test_container.py` 是最丰富的 Python 测试文件，覆盖 Array、List、Map、Dict 的全部 Python API：

### Array 测试

```python
def test_array():
    a = tvm_ffi.convert([1, 2, 3])
    assert isinstance(a, tvm_ffi.Array)
    assert len(a) == 3
    assert a[-1] == 3
    a_slice = a[-3:-1]
    assert isinstance(a_slice, list)
    assert (a_slice[0], a_slice[1]) == (1, 2)
```

关键测试点：
- **自动转换**：`tvm_ffi.convert([1, 2, 3])` 将 Python list 转为 `Array[int]`。
- **切片行为**：Array 切片返回 Python list 而非 Array，这是有意设计。
- **负索引**：支持 Python 风格的负索引访问。
- **嵌套容器**：`convert([[1,2,3], {"A": 5}])` 递归转换嵌套结构。

### Map 测试

```python
def test_int_map():
    amap = tvm_ffi.convert({3: 2, 4: 3})
    assert 3 in amap
    assert len(amap) == 2
    dd = dict(amap.items())
    assert tuple(amap.items()) == ((3, 2), (4, 3))
```

### List 测试

```python
def test_list_basic():
    # ... 基本操作
def test_list_mutation_methods():
    # ... push/pop 操作
def test_list_slice_assignment_and_delete():
    # ... 切片赋值与删除
def test_list_pickle_roundtrip():
    # ... 序列化往返
```

### Dict 测试

覆盖 `setitem`、`delitem`、共享变更、`keys/values/items`、`get` 默认值、`pop`、`clear`、`update`、迭代等所有 Python dict 协议方法。

## DType 测试（test_dtype.py）

```python
def test_dtype():
    float32 = tvm_ffi.dtype("float32")
    assert float32.__repr__() == "dtype('float32')"
    x = np.array([1, 2, 3], dtype=float32)
    assert x.dtype == float32

@pytest.mark.parametrize("alias, expected", [
    ("i8", "int8"), ("i16", "int16"), ("f32", "float32"), ...
])
def test_dtype_aliases(alias, expected): ...
```

测试要点：
- **字符串构造**：`tvm_ffi.dtype("float32")` 通过字符串创建 DataType。
- **NumPy 互操作**：创建的 dtype 可直接用于 `np.array` 的 dtype 参数。
- **别名映射**：支持 `"i32"` → `"int32"`、`"f64"` → `"float64"` 等缩写。
- **参数化测试**：使用 `@pytest.mark.parametrize` 批量验证所有 DLPack 类型别名。

## 错误处理测试（test_error.py）

```python
def test_error_from_cxx():
    test_raise_error = tvm_ffi.get_global_func("testing.test_raise_error")
    try:
        test_raise_error("ValueError", "error XYZ")
    except ValueError as e:
        assert e.__tvm_ffi_error__.kind == "ValueError"
        assert e.__tvm_ffi_error__.message == "error XYZ"
        assert e.__tvm_ffi_error__.backtrace.find("TestRaiseError") != -1
```

关键设计：
- **C++ 异常 → Python 异常**：C++ 侧抛出的 `ffi::Error` 被转换为对应类型的 Python 异常。
- **`__tvm_ffi_error__` 属性**：Python 异常对象保留对原始 FFI Error 对象的引用，可通过该属性访问 kind、message、backtrace。
- **嵌套传播**：`test_error_from_nested_pyfunc` 验证 C++ → Python → C++ → Python 多层传播后的回溯完整性。

## 函数调用测试（test_function.py）

```python
def test_echo():
    echo = tvm_ffi.convert(lambda x: x)
    assert echo(42) == 42

def test_global_func():
    func = tvm_ffi.get_global_func("testing.echo")
    assert func(1, 2, 3) == [1, 2, 3]
```

测试覆盖：
- **Lambda 转换**：Python lambda 通过 `tvm_ffi.convert()` 包装为 FFI Function。
- **全局函数获取**：`get_global_func()` 从 C++ 全局注册表获取函数。
- **不透明对象传递**：`test_echo_with_opaque_object` 验证 Handle 类型参数的正确传递。
- **DLPack 协议**：`test_function_with_dlpack_data_type_protocol` 验证支持 DLPack 协议的对象传递。

## 执行方式

CI 中 Python 测试通过以下命令执行：

```bash
uv pip install --reinstall --verbose --group test -e .
pytest -vvs tests/python
```

- **依赖安装**：使用 `uv` 安装开发依赖，`-e .` 以 editable 模式安装当前包。
- **详细输出**：`-vvs` 标志启用最高详细级别，每个测试用例单独打印。
- **多 Python 版本**：CI 矩阵覆盖 Python 3.9、3.13、3.14（含自由线程版 `3.14t`）。

## 设计分析

Python 测试套件的设计体现了以下原则：

1. **Pythonic 交互**：测试验证 Python 侧 API 符合 Python 社区惯例（如 `len()`、`in`、切片、`__repr__` 等）。
2. **双向转换验证**：通过 `convert()` 验证 Python → FFI → Python 的往返正确性。
3. **异常传播完整性**：不仅验证异常类型正确，还验证 `__tvm_ffi_error__` 属性中的结构化信息完整。
4. **参数化覆盖**：使用 pytest 的参数化功能批量覆盖类型别名、边界条件等。

## 相关概念

- [161 C++ GoogleTest 套件](161-cpp-googletest-suite.md)：C++ 侧测试框架，与 Python pytest 互补
- [163 test_any 覆盖分析](163-test-any-coverage.md)：Any 类型在 Python 侧的转换测试
- [168 CI/CD 流水线](168-ci-cd-pipeline.md)：Python 测试在 CI 中的触发条件与执行顺序
