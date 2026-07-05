---
title: "编译构建与项目集成"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm-ffi, ffi, build, examples, best-practices, faq, resources]
---

# 第11章：编译构建与项目集成

本章详细介绍 TVM FFI 的构建系统、依赖管理，以及如何将 TVM FFI 集成到你自己的项目中。

## 前置条件

在开始构建 TVM FFI 之前，请确保你的系统已安装以下工具：

| 工具 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.9+ | 用于 Python 绑定和开发流程 |
| C++ 编译器 | 支持 C++17 | GCC 7+, Clang 5+, MSVC 2019+ |
| CMake | 3.18+ | C++ 构建系统 |
| Ninja | 推荐 | 快速构建后端 |
| uv | 最新 | Python 包管理器（替代 pip） |

### 安装 uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 获取源码

```bash
# 克隆主仓库
git clone https://github.com/tlc-pack/tvm-ffi.git
cd tvm-ffi

# 初始化子模块（包含 DLPack 等依赖）
git submodule update --init --recursive
```

## Python 可编辑安装（推荐工作流）

对于大多数开发者，Python 可编辑安装是最便捷的方式，它会同时编译 C++ 核心和 Cython 绑定：

```bash
# 在仓库根目录执行
uv pip install --force-reinstall --verbose -e .
```

### 这个命令做了什么？

1. **解析依赖**：通过 `pyproject.toml` 解析 Python 和构建依赖
2. **CMake 配置**：自动配置 C++ 构建（使用 Ninja 后端）
3. **编译 C++**：编译 `tvm_ffi_shared` 共享库
4. **编译 Cython**：编译 Python Cython 扩展
5. **可编辑安装**：将包链接到当前目录，修改 Python 文件后无需重新安装

### 何时需要重新构建？

| 修改内容 | 是否需要重新构建 | 命令 |
|----------|------------------|------|
| Python 源文件 | 否 | 立即生效 |
| C++ 头文件（`.h`） | 是 | `uv pip install --force-reinstall -e .` |
| C++ 实现（`.cc`） | 是 | `uv pip install --force-reinstall -e .` |
| Cython 文件（`.pyx`） | 是 | `uv pip install --force-reinstall -e .` |
| CMake 配置 | 是 | 删除 build 目录后重新安装 |

## 纯 C++ 构建

如果你只需要 C++ 库而不需要 Python 绑定，可以使用纯 CMake 构建：

```bash
# 配置构建目录
cmake . -B build_cpp -DCMAKE_BUILD_TYPE=RelWithDebInfo -G Ninja

# 编译共享库目标
cmake --build build_cpp --target tvm_ffi_shared
```

### CMake 构建选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `CMAKE_BUILD_TYPE` | `Release` | 构建类型：Debug/Release/RelWithDebInfo |
| `TVM_FFI_BUILD_TESTS` | `ON` | 是否构建 C++ 测试 |
| `TVM_FFI_BUILD_PYTHON` | `ON` | 是否构建 Python 绑定 |
| `TVM_FFI_BUILD_RUST` | `OFF` | 是否构建 Rust  crate |
| `BUILD_SHARED_LIBS` | `ON` | 构建共享库还是静态库 |

## CMake 项目集成

有两种方式将 TVM FFI 集成到你的 CMake 项目中：

### 方式一：find_package（已安装）

如果 TVM FFI 已经安装到系统中：

```cmake
cmake_minimum_required(VERSION 3.18)
project(my_project)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(tvm_ffi REQUIRED)

add_executable(my_app main.cc)
target_link_libraries(my_app PRIVATE tvm::ffi)
```

### 方式二：add_subdirectory（源码集成）

将 TVM FFI 作为子模块包含在你的项目中：

```cmake
cmake_minimum_required(VERSION 3.18)
project(my_project)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 禁用 TVM FFI 的测试和 Python 绑定
set(TVM_FFI_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(TVM_FFI_BUILD_PYTHON OFF CACHE BOOL "" FORCE)

add_subdirectory(3rdparty/tvm-ffi)

add_executable(my_app main.cc)
target_link_libraries(my_app PRIVATE tvm::ffi)
```

## Stub 生成

TVM FFI 提供了 stub 生成工具，为 Python 代码生成类型提示文件（`.pyi`）：

```bash
# 为已安装的 tvm_ffi 包生成 stubs
uv run tvm-ffi-stubgen python
```

生成的 `.pyi` 文件将提供完整的类型提示，支持 IDE 补全和类型检查。

## 运行测试

TVM FFI 支持三个语言生态的测试套件：

### C++ 测试

```bash
# 纯 C++ 构建后
cd build_cpp
ctest --output-on-failure

# 或通过 Python 构建
cd build
ctest --output-on-failure
```

### Python 测试

```bash
# 运行所有 Python 测试
uv run pytest tests/python/ -v

# 运行特定测试文件
uv run pytest tests/python/test_function.py -v

# 带覆盖率
uv run pytest tests/python/ --cov=tvm_ffi
```

### Rust 测试

```bash
cd rust
cargo test
```

## 代码检查与格式化

TVM FFI 使用 pre-commit 管理代码质量工具：

```bash
# 安装 pre-commit hooks
uv run pre-commit install

# 运行所有检查
uv run pre-commit run --all-files
```

### 包含的检查工具

| 工具 | 适用语言 | 功能 |
|------|----------|------|
| ruff | Python | Linting + 格式化 |
| clang-format | C/C++ | 代码格式化（Google 风格，100 列） |
| cython-lint | Cython | Cython 代码检查 |
| cmake-format | CMake | CMake 脚本格式化 |
| trailing-whitespace | 所有 | 去除行尾空格 |
| end-of-file-fixer | 所有 | 确保文件以换行结尾 |

### 手动运行单个检查

```bash
# 只运行 ruff
uv run ruff check python/

# 自动修复 ruff 问题
uv run ruff check --fix python/

# 格式化 C++ 文件
clang-format -i include/tvm/ffi/*.h src/ffi/*.cc
```

## 跨平台注意事项

### Linux (x86_64 / aarch64)

- 推荐 GCC 9+ 或 Clang 10+
- 默认生成 `.so` 共享库
- CI 覆盖 x86_64 和 aarch64

```bash
# Ubuntu/Debian 依赖安装
sudo apt-get update && sudo apt-get install -y \
    build-essential cmake ninja-build python3-dev
```

### macOS (arm64)

- 推荐 Xcode Command Line Tools 或 Homebrew Clang
- 生成 `.dylib` 共享库
- CI 覆盖 Apple Silicon (arm64)

```bash
# Homebrew 依赖安装
brew install cmake ninja python
```

### Windows (AMD64)

- 需要 Visual Studio 2019+ 或 Build Tools
- 生成 `.dll` 共享库
- 注意符号导出：使用 `TVM_FFI_DLL_EXPORT` 宏
- 路径使用反斜杠或正斜杠均可

```powershell
# 使用 Visual Studio Developer Command Prompt
cmake . -B build_cpp -G "Visual Studio 17 2022" -A x64
cmake --build build_cpp --config Release --target tvm_ffi_shared
```

## 项目集成示例

### 最小 C++ 项目集成

**目录结构：**
```
my_project/
├── 3rdparty/
│   └── tvm-ffi/          # git submodule
├── CMakeLists.txt
└── main.cc
```

**main.cc：**
```cpp
#include <tvm/ffi/function.h>
#include <tvm/ffi/container/array.h>
#include <iostream>

int main() {
    using namespace tvm::ffi;

    // 注册一个简单函数
    register_global_func("my_project.add", [](int a, int b) {
        return a + b;
    });

    // 调用注册的函数
    auto add = get_global_func("my_project.add");
    int result = add(3, 4).cast<int>();
    std::cout << "3 + 4 = " << result << std::endl;

    return 0;
}
```

### 最小 Python 项目

**目录结构：**
```
my_python_project/
├── pyproject.toml
└── my_module.py
```

**pyproject.toml：**
```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = ["tvm-ffi"]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

**my_module.py：**
```python
from __future__ import annotations

import tvm_ffi
from tvm_ffi import register_func, get_global_func


@register_func("my_module.greet")
def greet(name: str) -> str:
    return f"Hello, {name} from TVM FFI!"


if __name__ == "__main__":
    greet_fn = get_global_func("my_module.greet")
    print(greet_fn("World"))
```

## CI/CD 参考

TVM FFI 官方 CI 覆盖以下平台：

| 平台 | 架构 | 编译器 | Python 版本 |
|------|------|--------|-------------|
| Ubuntu 22.04 | x86_64 | GCC 11 | 3.9, 3.10, 3.11, 3.12 |
| Ubuntu 22.04 | aarch64 | GCC 11 | 3.11 |
| macOS 13 | arm64 | Apple Clang 14 | 3.11 |
| Windows 2022 | AMD64 | MSVC 2022 | 3.11 |

---

**本章导航：**
- 上一章：[10-DLPack 集成](10-dlpack-integration.md)
- 下一章：[12-完整实战示例](12-examples.md)
- [返回目录](README.md)
