---
id: "tvm-ffi-build-packaging"
title: "构建与打包"
tags: ["tvm-ffi", "build", "cmake", "packaging", "wheel"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# 构建与打包

TVM FFI 使用 CMake 作为构建系统，支持 Linux/macOS/Windows 多平台编译，可通过 scikit-build-core 打包为 Python wheel，也可作为纯 C++ 库集成到其他项目中。

## CMake 构建选项总览

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `TVM_FFI_USE_LIBBACKTRACE` | `ON` | 启用 libbacktrace 栈追踪 |
| `TVM_FFI_USE_EXTRA_CXX_API` | `ON` | 共享库包含额外 C++ API（序列化、反射、模块加载等） |
| `TVM_FFI_USE_THREADS` | `ON` | 链接线程库（pthread） |
| `TVM_FFI_USE_DL_LIBS` | `ON` | 链接动态加载库（dl） |
| `TVM_FFI_BACKTRACE_ON_SEGFAULT` | `ON` | 段错误时打印栈回溯 |
| `TVM_FFI_ATTACH_DEBUG_SYMBOLS` | `OFF` | Release 模式附加调试符号（-g1） |
| `TVM_FFI_BUILD_TESTS` | `OFF` | 构建 C++ 测试目标（GoogleTest） |
| `TVM_FFI_BUILD_PYTHON_MODULE` | `OFF` | 构建 Python Cython 扩展 |

**注意**：TVM FFI 作为子项目（`add_subdirectory`）引入时，测试和 Python 模块选项自动跳过，仅构建核心库目标。

## 编译步骤

### 前置条件

- C++17 编译器（GCC/Clang/MSVC）、CMake ≥ 3.26、Ninja（推荐）
- Python ≥ 3.9、Cython ≥ 3.2.8（构建 Python 绑定时）
- Git submodules：`git submodule update --init --recursive`

### 命令行编译

**纯 C++ 构建**：

```bash
cmake . -B build_cpp -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build_cpp --parallel --config RelWithDebInfo --target tvm_ffi_shared
cmake --install build_cpp --config RelWithDebInfo --prefix ./dist
```

安装产物：头文件在 `dist/include/tvm/ffi/`，库文件在 `dist/lib/`。

**Python editable 安装**（推荐开发工作流）：

```bash
uv pip install --force-reinstall --verbose -e .
```

通过 scikit-build-core 驱动 CMake，自动编译 C++ 核心库和 Cython 扩展。C++/Cython 修改后需重新运行此命令；纯 Python 修改即时生效。

传递 CMake 选项：

```bash
uv pip install --force-reinstall --verbose -e . \
  --config-settings cmake.define.TVM_FFI_ATTACH_DEBUG_SYMBOLS=ON
```

### IDE 集成

**VSCode/Cursor**（CMake Tools）：

```json
{
    "cmake.buildDirectory": "${workspaceFolder}/build-vscode",
    "cmake.configureArgs": ["-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"],
    "cmake.configureSettings": {
        "tvm_ffi_ROOT": "${workspaceFolder}/.venv/lib/pythonX.Y/site-packages/tvm_ffi/share/cmake/tvm_ffi"
    }
}
```

**CLion/Visual Studio**：直接打开项目目录，设置 `TVM_FFI_BUILD_PYTHON_MODULE=ON` 构建 Python 模块。

### 编译目标

| CMake 目标 | 别名 | 类型 | 说明 |
|-----------|------|------|------|
| `tvm_ffi_header` | `tvm_ffi::header` | INTERFACE | 头文件目标，设置 C++17 和 include 路径 |
| `tvm_ffi_shared` | `tvm_ffi::shared` | SHARED | 核心动态库 |
| `tvm_ffi_static` | `tvm_ffi::static` | STATIC | 核心静态库 |
| `tvm_ffi_testing` | — | SHARED | 测试工具库 |
| `tvm_ffi_cython` | — | MODULE | Python Cython 扩展（需 `TVM_FFI_BUILD_PYTHON_MODULE=ON`） |

所有库输出到 `${CMAKE_BINARY_DIR}/lib/`。

## 运行测试

**C++ 测试**：

```bash
cmake . -B build_test -DTVM_FFI_BUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build_test --clean-first --config Debug --target tvm_ffi_tests
ctest -V -C Debug --test-dir build_test --output-on-failure
```

**Python 测试**：

```bash
uv pip install --force-reinstall --verbose --group test -e .
uv run pytest -vvs tests/python
```

**Rust 测试**：`cd rust && cargo test`（需先安装 Python 包）。

## Python Wheel 打包

使用 scikit-build-core 作为 PEP 517 构建后端，setuptools-scm 从 Git tag 自动推导版本号。

### 构建命令

```bash
pip wheel -w dist .           # 标准 wheel
uv build --wheel --out-dir dist .  # uv
pip install -e .              # editable 安装
```

### Wheel 标签

核心 Cython 扩展绑定到特定 Python 版本 C API（非 abi3），wheel 按版本标记：`cp39-cp39`、`cp310-cp310`、…、`cp314t-cp314t`（free-threaded）。下游扩展库可构建 ABI 无关 wheel（`py3-none`），因为通过稳定 C ABI 与 TVM FFI 交互。

### Wheel 审计修复

`libtvm_ffi` 由 `tvm_ffi` 包预加载，扩展 wheel 应排除此依赖：

```bash
auditwheel repair --exclude libtvm_ffi.so dist/*.whl        # Linux
delocate-wheel -w dist -v --exclude libtvm_ffi.dylib dist/*.whl  # macOS
delvewheel repair --exclude tvm_ffi.dll -w dist dist\\*.whl     # Windows
```

### 版本管理

使用 setuptools-scm，Git tag 格式 `v0.x.x`，版本自动写入 `python/tvm_ffi/_version.py`：

```toml
[tool.setuptools_scm]
version_file = "python/tvm_ffi/_version.py"
write_to = "python/tvm_ffi/_version.py"
```

### tvm-ffi-config CLI

```bash
tvm-ffi-config --includedir        # 头文件目录
tvm-ffi-config --dlpack-includedir # DLPack 头文件目录
tvm-ffi-config --libfiles          # 库文件路径
tvm-ffi-config --cmakedir          # CMake config 目录
tvm-ffi-config --cxxflags --ldflags --libs  # 原始编译链接标志
```

## 分发到 PyPI

```bash
cibuildwheel --output-dir dist     # 多平台构建
pip install twine && twine upload dist/*.whl dist/*.tar.gz
```

CI 多平台构建策略：

| 平台 | 架构 | 备注 |
|------|------|------|
| Linux | x86_64, aarch64 | manylinux_2_28 容器（旧 glibc 构建，新 glibc 运行） |
| macOS | x86_64, arm64 | `MACOSX_DEPLOYMENT_TARGET=10.14` |
| Windows | AMD64 | delvewheel 修复 |

## CMake 集成到其他项目

### 方式一：find_package（推荐，安装后）

```cmake
find_package(tvm_ffi CONFIG REQUIRED)
add_library(my_ext SHARED src/my_ext.cc)
tvm_ffi_configure_target(my_ext)
```

找不到包时显式指定：`cmake -Dtvm_ffi_ROOT="$(tvm-ffi-config --cmakedir)" ..`

### 方式二：add_subdirectory（源码嵌入）

```cmake
add_subdirectory(3rdparty/tvm-ffi)
target_link_libraries(my_ext PRIVATE tvm_ffi::shared)
```

### 方式三：FetchContent（CMake 3.14+）

```cmake
include(FetchContent)
FetchContent_Declare(tvm_ffi
    GIT_REPOSITORY https://github.com/apache/tvm-ffi.git
    GIT_TAG main)
FetchContent_MakeAvailable(tvm_ffi)
target_link_libraries(my_ext PRIVATE tvm_ffi::shared)
```

### 核心 CMake 函数

**tvm_ffi_configure_target**：一站式配置目标：

```cmake
tvm_ffi_configure_target(my_ext
    LINK_SHARED  ON       # 链接 tvm_ffi::shared（默认 ON）
    LINK_HEADER  ON       # 链接 tvm_ffi::header（默认 ON）
    DEBUG_SYMBOL ON       # dSYM 后处理（默认 ON）
    MSVC_FLAGS   ON       # MSVC 兼容标志（默认 ON）
    STUB_DIR     "python" # 生成 Python stubs 目录
    STUB_INIT    ON       # 初始化新包布局（默认 OFF）
)
```

**tvm_ffi_install**：安装平台产物（macOS dSYM）。

非 CMake 构建可直接用 `tvm-ffi-config` 输出的标志：

```bash
g++ -shared -fPIC my_ext.cc -o my_ext.so \
    $(tvm-ffi-config --cxxflags) $(tvm-ffi-config --ldflags) $(tvm-ffi-config --libs)
```

### Python 扩展示例

`CMakeLists.txt`：

```cmake
cmake_minimum_required(VERSION 3.18)
project(my_ffi_extension)
find_package(Python COMPONENTS Interpreter REQUIRED)
find_package(tvm_ffi CONFIG REQUIRED)
add_library(my_ffi_extension SHARED src/extension.cc)
tvm_ffi_configure_target(my_ffi_extension STUB_DIR "./python" STUB_INIT ON)
install(TARGETS my_ffi_extension DESTINATION .)
tvm_ffi_install(my_ffi_extension DESTINATION .)
```

`pyproject.toml`：

```toml
[build-system]
requires = ["scikit-build-core>=0.10.0", "apache-tvm-ffi"]
build-backend = "scikit_build_core.build"
[project]
name = "my-ffi-extension"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["apache-tvm-ffi"]
[tool.scikit-build]
wheel.py-api = "py3"
wheel.packages = ["python/my_ffi_extension"]
wheel.install-dir = "my_ffi_extension"
cmake.build-type = "Release"
```

加载扩展：

```python
from tvm_ffi.libinfo import load_lib_module
LIB = load_lib_module(package="my-ffi-extension", target_name="my_ffi_extension")
```

## 第三方依赖

| 依赖 | 位置 | 必选 | 说明 |
|------|------|------|------|
| DLPack | `3rdparty/dlpack/` | 是 | DLTensor 标准结构，Tensor 零拷贝互操作基础 |
| libbacktrace | `3rdparty/libbacktrace/` | 否 | 异常栈回溯，`TVM_FFI_USE_LIBBACKTRACE=ON` 启用 |
| Cython | pip 安装 | Python 绑定时 | ≥3.2.8，将 `.pyx` 编译为 C++ 扩展 |

## 跨平台编译注意事项

### 平台差异

| 特性 | Linux | macOS | Windows |
|------|-------|-------|---------|
| 共享库后缀 | `.so` | `.dylib` | `.dll` |
| RPATH | `$ORIGIN` | `@loader_path` | PATH 环境变量 |
| 栈回溯 | libbacktrace | libbacktrace | DbgHelp.lib |
| 符号隐藏 | `--exclude-libs,ALL` | hidden visibility | 自动处理 |
| 调试符号 | — | `.dSYM` bundle（dsymutil） | PDB（`/DEBUG`） |

### CUDA 编译

通过 `EmbedCubin.cmake` 模块：
- `add_tvm_ffi_cubin(<name> CUDA <src>)` — 编译为 CUBIN
- `add_tvm_ffi_fatbin(<name> CUDA <src>)` — 编译为 FATBIN
- `tvm_ffi_embed_bin_into(<tgt> SYMBOL <name> BIN <bin>)` — 嵌入二进制

默认 `CMAKE_CUDA_RUNTIME_LIBRARY=Shared`（动态链接 CUDA runtime），避免静态链接的驱动版本不匹配。仅用 Driver API 时设为 `None`。

### MSVC 特殊设置

`tvm_ffi_add_msvc_flags()` 自动应用：
- 预处理器：`WIN32_LEAN_AND_MEAN`、`_CRT_SECURE_NO_WARNINGS`、`NOMINMAX`
- 编译选项：`/Zi`（调试信息）、`/bigobj`（避免 C1128 大模板错误）
- 链接：`DbgHelp.lib`、`/DEBUG`（PDB）
- Release/Debug 均输出到 `build/lib/`，不附加配置子目录

## Config.cmake 与工具模块说明

**tvm_ffi-config.cmake**（安装到 `share/cmake/tvm_ffi/`）：`find_package` 时自动加载，调用 `tvm-ffi-config` CLI 查询路径，创建 `tvm_ffi::header`/`tvm_ffi::shared` 导入目标，包含工具模块。

**cmake/Utils/ 模块**：

| 文件 | 功能 |
|------|------|
| `Library.cmake` | `tvm_ffi_configure_target`、`tvm_ffi_install`、`tvm_ffi_add_msvc_flags` 等核心函数 |
| `EmbedCubin.cmake` | CUDA CUBIN/FATBIN 编译与嵌入 |
| `AddLibbacktrace.cmake` | libbacktrace 自动构建 |
| `AddGoogleTest.cmake` | GoogleTest 自动获取与测试注册 |
| `DetectTargetTriple.cmake` | 目标平台三元组检测 |

## 关键引用

- `CMakeLists.txt`（源项目归档路径）
- `cmake/Utils/Library.cmake`（源项目归档路径）
- `cmake/tvm_ffi-config.cmake`（源项目归档路径）
- `examples/python_packaging/`（源项目归档路径）
- `pyproject.toml`（源项目归档路径）

---

← 上一页：[Python 开发指南](09-python-guide.md) | 下一页 → [实战案例](11-examples.md)
