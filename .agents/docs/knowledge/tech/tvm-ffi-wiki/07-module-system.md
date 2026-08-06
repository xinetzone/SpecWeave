---
id: "tvm-ffi-module-system"
title: "Module 模块系统"
tags: ["tvm-ffi", "module", "dynamic-loading", "dll"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# Module 模块系统

## 概述

Module系统是TVM-FFI实现插件化扩展的核心机制，它提供了动态加载编译好的动态库（.so/.dll/.dylib）的能力。通过Module系统，你可以在运行时动态加载C++函数库、即时编译源码，并将扩展打包进Python wheel。

核心API定义在 `module.h`（源项目归档路径） 和 `tvm_ffi.module` 模块。

## Module概念

Module是**包含一组全局函数的容器**，提供命名空间隔离和动态加载能力。有三种形式：

1. **共享库模块**：通过 `dlopen`/`LoadLibraryW` 动态加载的 `.so`/`.dll`/`.dylib`
2. **系统库模块**：静态链接到可执行文件中的符号
3. **内联模块**：运行时JIT编译C++/CUDA源码生成

### 符号约定

动态库导出函数遵循 `__tvm_ffi_<function_name>` 命名约定。`TVM_FFI_DLL_EXPORT_TYPED_FUNC(add_two, AddTwo)` 宏会导出 `__tvm_ffi_add_two` 符号。

### 自动初始化

动态库加载时，`TVM_FFI_STATIC_INIT_BLOCK()` 定义的静态初始化块自动执行，用于注册全局函数和对象类型。

## C++端创建模块

### 静态初始化块

```cpp
#include <tvm/ffi/tvm_ffi.h>

static int AddOne(int x) { return x + 1; }

TVM_FFI_STATIC_INIT_BLOCK() {
  namespace refl = tvm::ffi::reflection;
  refl::GlobalDef().def("my_ext.add_one", AddOne, "Add one to input");
}
```

### 直接导出C符号

```cpp
static int AddTwo(int x) { return x + 2; }
TVM_FFI_DLL_EXPORT_TYPED_FUNC(add_two, AddTwo);
```

导出的函数可通过 `mod.add_two(40)` 直接访问。

### math模块示例

```cpp
#include <tvm/ffi/tvm_ffi.h>
#include <cstdint>

namespace math_module {

static int64_t Add(int64_t a, int64_t b) { return a + b; }
static int64_t Sub(int64_t a, int64_t b) { return a - b; }
static int64_t Mul(int64_t a, int64_t b) { return a * b; }

TVM_FFI_DLL_EXPORT_TYPED_FUNC(add, Add)
TVM_FFI_DLL_EXPORT_TYPED_FUNC(sub, Sub)

TVM_FFI_STATIC_INIT_BLOCK() {
  namespace refl = tvm::ffi::reflection;
  refl::GlobalDef().def("math.mul", Mul, "Multiply two integers");
}

}  // namespace math_module
```

### CMake编译

```cmake
cmake_minimum_required(VERSION 3.18)
project(math_module)
find_package(tvm_ffi CONFIG REQUIRED)

add_library(math_module SHARED math.cc)
tvm_ffi_configure_target(math_module)
install(TARGETS math_module DESTINATION .)
```

## Python端加载模块

### 加载动态库

```python
import tvm_ffi

mod = tvm_ffi.load_module("./build/libmath_module.so")
```

`load_module()` 会：加载库→执行静态初始化→查找 `__tvm_ffi_*` 符号→包装为Function对象。默认 `keep_module_alive=True` 保持模块全局存活。

### 调用函数

```python
# 属性访问
result = mod.add(3, 4)  # -> 7
result = mod.sub(10, 3)  # -> 7

# 显式获取
add_func = mod.get_function("add")
result = add_func(3, 4)

# 字典访问
result = mod["add"](3, 4)

# 全局注册表函数
mul = tvm_ffi.get_global_func("math.mul")
result = mul(3, 4)  # -> 12
```

### 查询元数据

```python
metadata = mod.get_function_metadata("add")
if metadata:
    print(metadata["type_schema"])

doc = mod.get_function_doc("add")
```

### 生命周期注意事项

Module卸载后，由其创建的对象析构函数可能指向无效内存导致崩溃：

```python
# ❌ 危险：mod可能在tensor前析构
def bad_pattern(x):
    mod = tvm_ffi.load_module("lib.so")
    return mod.create_tensor(x)

# ✅ 安全：嵌套作用域或保持模块存活
def good_pattern(x):
    mod = tvm_ffi.load_module("lib.so")
    def run():
        tensor = mod.create_tensor(x)
    run()
```

## 动态加载流程

```mermaid
flowchart LR
    A[load_module(path)] --> B[ModuleLoadFromFile]
    B --> C{平台}
    C -->|Linux/macOS| D[dlopen]
    C -->|Windows| E[LoadLibraryW]
    D --> F[查找__tvm_ffi_符号]
    E --> F
    F --> G[执行静态初始化块]
    G --> H[注册全局函数/对象]
    H --> I[包装为Function]
    I --> J[返回Module]
```

流程：加载库→符号查找→静态初始化→函数包装→返回Module。Module持有库句柄，保证生命周期内不被卸载。

## inline_module：即时编译

使用 `tvm_ffi.cpp.load_inline()` 在Python中内嵌C++代码即时编译：

```python
import tvm_ffi.cpp
import torch

mod = tvm_ffi.cpp.load_inline(
    name="hello",
    cpp_sources=r"""
        void add_one_cpu(tvm::ffi::TensorView x, tvm::ffi::TensorView y) {
          for (int i = 0; i < x.size(0); ++i) {
            static_cast<float*>(y.data_ptr())[i] =
              static_cast<float*>(x.data_ptr())[i] + 1;
          }
        }
    """,
    functions=["add_one_cpu"],
)

x = torch.tensor([1, 2, 3], dtype=torch.float32)
y = torch.empty_like(x)
mod.add_one_cpu(x, y)
```

支持CUDA源码（`cuda_sources` 参数），也可从文件编译：

```python
mod = tvm_ffi.cpp.load(name="my_ops", cpp_files=["my_ops.cpp"])
```

## 模块依赖和命名空间

### 模块导入

```python
mod1 = tvm_ffi.load_module("lib1.so")
mod2 = tvm_ffi.load_module("lib2.so")
mod2.import_module(mod1)
func = mod2.get_function("func_from_mod1", query_imports=True)
```

### 命名约定

为避免符号冲突：
- 全局函数：`<module_name>.<function_name>`，如 `my_ext.add_one`
- 类型键名：`<module_name>.<TypeName>`，如 `my_ext.IntPair`
- 避免手动定义 `__tvm_ffi_` 前缀的符号

```cpp
// ✅ 好
refl::GlobalDef().def("myproject.math.add", Add);
// ❌ 避免
refl::GlobalDef().def("add", Add);
```

## 与Python wheel打包集成

### 项目结构

```
python_packaging/
├── CMakeLists.txt
├── pyproject.toml
├── src/extension.cc
└── python/my_ffi_extension/
    ├── __init__.py
    └── _ffi_api.py
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.18)
project(my_ffi_extension)
find_package(tvm_ffi CONFIG REQUIRED)

add_library(my_ffi_extension SHARED src/extension.cc)
tvm_ffi_configure_target(my_ffi_extension STUB_DIR "./python" STUB_INIT ON)
install(TARGETS my_ffi_extension DESTINATION .)
```

### pyproject.toml

```toml
[project]
name = "my-ffi-extension"
dependencies = ["apache-tvm-ffi"]

[build-system]
requires = ["scikit-build-core>=0.10.0", "apache-tvm-ffi"]
build-backend = "scikit_build_core.build"

[tool.scikit-build]
wheel.py-api = "py3"
wheel.packages = ["python/my_ffi_extension"]
```

### 使用

```python
import my_ffi_extension

print(my_ffi_extension.LIB.add_two(1))  # C符号导出
print(my_ffi_extension.add_one(3))      # 全局函数
```

## 跨平台注意事项

| 平台 | 后缀 | 加载API |
|------|-----|---------|
| Linux | `.so` | `dlopen`/`dlsym` |
| Windows | `.dll` | `LoadLibraryW`/`GetProcAddress` |
| macOS | `.dylib` | `dlopen`/`dlsym` |

`tvm_ffi_configure_target` 自动处理符号可见性（GCC/Clang `-fvisibility=hidden`，Windows `__declspec`）。

ABI稳定性保证：
1. 统一C ABI（`TVMFFISafeCallType`）
2. C++类型不跨边界
3. 版本检查机制

## 常见问题

**动态库找不到**：检查路径、Windows PATH、Linux `ldd` 依赖

**符号未导出**：确认使用了正确的宏，用 `nm -D`（Linux）或Dependency Walker（Windows）检查

**静态初始化顺序问题**：避免静态初始化间依赖，使用 `TVM_FFI_STATIC_INIT_BLOCK`

**卸载后崩溃**：保持Module存活，使用默认 `keep_module_alive=True`，避免Module对象提前析构

## 参考

- `C++ Module API`（源项目归档路径）
- `Python Module API`（源项目归档路径）
- `func_module.rst`（源项目归档路径）
- `inline_module示例`（源项目归档路径）
- `python_packaging示例`（源项目归档路径）

---

← 上一页：[Reflection 反射系统](06-reflection.md) | 下一页 → [C++ 开发指南](08-cpp-guide.md)
