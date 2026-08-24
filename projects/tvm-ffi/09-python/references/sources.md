# Python绑定 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. 包入口与导出

### 源码路径

- `python/tvm_ffi/__init__.py`

### 关键 API/类型清单

- `__init__.py 模块导入`
- `Object`
- `Function`
- `Tensor`
- `Array`
- `Dict`
- `List`
- `Map`
- `String`
- `Bytes`
- `Shape`
- `Scalar`
- `Error`
- `DataType`
- `Device`

### 相关事实编号

`F-329`, `F-330`

---

## 2. C FFI 接口

### 源码路径

- `python/tvm_ffi/_ffi_api.py`

### 关键 API/类型清单

- `_ffi_api`
- `ctypes`
- `libtvm_ffi`
- `TVMFFIGetVersion`
- `TVMFFIFunctionGetGlobal`
- `TVMFFIFunctionCall`
- `TVMFFIObjectIncRef`
- `TVMFFIObjectDecRef`
- `TVMFFITypeKeyToIndex`
- `TypeIndex2Key`（C++ 侧）
- `TVMFFIStructuralEqual`
- `TVMFFIStructuralHash`
- `TVMFFIGetLastError`
- `TVMFFISetLastError`

### 相关事实编号

`F-331`, `F-332`, `F-333`, `F-334`

---

## 3. Cython 核心

### 源码路径

- `python/tvm_ffi/cython/core.pyx`

### 关键 API/类型清单

- `PyAny`
- `PyFunction`
- `__int__`
- `__float__`
- `__bool__`
- `__str__`
- `__call__`

### 相关事实编号

`F-335`, `F-336`, `F-337`

---

## 4. 容器类型

### 源码路径

- `python/tvm_ffi/container.py`

### 关键 API/类型清单

- `PyArray`
- `PyDict`
- `PyList`
- `PyMap`
- `__len__`
- `__getitem__`
- `__setitem__`
- `append`
- `pop`
- `__contains__`
- `keys`
- `values`
- `items`

### 相关事实编号

`F-338`, `F-339`, `F-340`, `F-341`

---

## 5. 函数注册表

### 源码路径

- `python/tvm_ffi/registry.py`

### 关键 API/类型清单

- `_REGISTRY`
- `register_func`
- `get_global_func`
- `list_global_func_names`

### 相关事实编号

`F-342`, `F-343`, `F-344`, `F-345`

---

## 6. 错误处理

### 源码路径

- `python/tvm_ffi/error.py`

### 关键 API/类型清单

- `TVMFFIError`
- `TVMFFIInternalError`
- `TVMFFIValueError`
- `TVMFFITypeError`
- `TVMFFIIndexError`
- `TVMFFIKeyError`
- `_extract_error`

### 相关事实编号

`F-346`, `F-347`, `F-348`

---

## 7. 类型转换与Tensor

### 源码路径

- `python/tvm_ffi/_convert.py`
- `python/tvm_ffi/_tensor.py`

### 关键 API/类型清单

- `to_tvm_ffi_any`
- `from_tvm_ffi_any`
- `Tensor`
- `tensor_from_numpy`
- `tensor_from_dlpack`
- `numpy`

### 相关事实编号

`F-349`, `F-350`, `F-351`, `F-352`, `F-353`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
