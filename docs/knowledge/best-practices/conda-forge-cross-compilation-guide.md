---
id: "conda-forge-cross-compilation-guide"
title: "conda-forge 交叉编译配置完整指南"
category: "best-practices"
tags: ["conda-forge", "cross-compilation", "conda-build", "CMake", "scikit-build-core", "Docker", "Wine", "macOS", "Windows", "toolchain", "RPATH"]
date: "2026-07-30"
status: "stable"
author: "SpecWeave"
summary: "conda-forge 交叉编译配置完整调研报告，覆盖从 linux-64 构建 osx-64/osx-arm64/win-64 平台包的完整方案：平台三元组、工具链包名清单、conda_build_config.yaml模板、meta.yaml依赖分离、build.sh交叉编译检测、CMAKE_ARGS变量传递、scikit-build-core适配、Wine运行时测试、常见陷阱与解决方案。"
source: ".trae/specs/docker-cross-platform-test/research-report.md"
---

# conda-forge 交叉编译配置完整指南

> **调研日期**：2026-07-30
> **目标**：从 linux-64 构建 osx-64/osx-arm64/win-64 平台包的完整配置方案
> **来源**：Docker跨平台构建测试任务调研产出（[spec.md](../../../../.trae/specs/docker-cross-platform-test/spec.md)）

---

## 目录

1. [官方文档核心概念](#1-官方文档核心概念)
2. [交叉编译配置模板](#2-交叉编译配置模板)
3. [工具链包名清单](#3-工具链包名清单)
4. [CONDA_BUILD_CROSS_COMPILATION 环境变量详解](#4-conda_build_cross_compilation-环境变量详解)
5. [CMake/scikit-build-core 交叉编译变量传递](#5-cmakescikit-build-core-交叉编译变量传递)
6. [Wine 运行 Windows conda/Python 可行性](#6-wine-运行-windows-condapython-可行性)
7. [Open Questions 解答](#7-open-questions-解答)
8. [关键注意事项](#8-关键注意事项)
9. [参考链接](#9-参考链接)

---

## 1. 官方文档核心概念

### 1.1 平台术语

| 术语 | 说明 |
|------|------|
| **Build 平台** | 运行构建过程的平台（如 linux-64） |
| **Host 平台** | 生成的二进制文件最终运行的平台（如 osx-64、win-64） |
| **Target 平台** | 仅在构建交叉编译器本身时使用，通常与 Host 相同 |

> **注意**：v0 recipes 使用 `target_platform` 指代 Host 平台；v1 recipes 使用 `host_platform`。

### 1.2 平台三元组 (Triplet)

| 平台 | 三元组 |
|------|--------|
| linux-64 | `x86_64-conda-linux-gnu` |
| linux-aarch64 | `aarch64-conda-linux-gnu` |
| osx-64 | `x86_64-apple-darwin20.0.0` |
| osx-arm64 | `arm64-apple-darwin20.0.0` |
| win-64 | `x86_64-w64-mingw32` |

### 1.3 两个前缀 (Prefix) 区分

- **`${BUILD_PREFIX}`**：构建工具所在目录（build 依赖安装位置）
- **`${PREFIX}`**：目标平台文件所在目录（host 依赖安装位置，也是最终包安装前缀）

**依赖放置规则**：
- Build 依赖：构建时需要运行的程序（编译器、cmake、make、ninja、pkg-config）
- Host 依赖：目标平台的库、头文件、Python 解释器等
- Build+Host：两者都需要的包（条件性放置）

---

## 2. 交叉编译配置模板

### 2.1 conda-forge.yml（启用交叉编译）

```yaml
# 从 linux-64 交叉编译 osx-64、osx-arm64、win-64
build_platform:
  linux_64: linux_64          # 原生构建
  osx_64: linux_64            # 从 linux-64 交叉编译 osx-64
  osx_arm64: linux_64         # 从 linux-64 交叉编译 osx-arm64
  win_64: linux_64            # 从 linux-64 交叉编译 win-64
  linux_aarch64: linux_64     # 可选：从 linux-64 交叉编译 linux-aarch64

# 测试配置：原生+模拟器运行测试；无模拟器时跳过
test: native_and_emulated

# 可选：跳过交叉编译时的测试（不推荐，优先用 native_and_emulated）
# test_on_native_only: true

conda_build:
  pkg_format: '2'

conda_forge_output_validation: true

github:
  branch_name: main
  tooling_branch_name: main
```

> **重要**：修改 `conda-forge.yml` 后必须执行 `conda-smithy rerender` 重新生成 CI 配置。

### 2.2 recipe/conda_build_config.yaml（编译器版本配置）

```yaml
# 使用 conda-forge 推荐的编译器版本
c_compiler:
  - gcc                        # [linux]
  - clang                      # [osx]
  - clang                      # [win]  # clang_win-64 (MSVC ABI)
  # - gcc                      # [win]  # 备选：gcc_win-64 (MinGW)

cxx_compiler:
  - gxx                        # [linux]
  - clangxx                    # [osx]
  - clangxx                    # [win]
  # - gxx                      # [win]

c_compiler_version:
  - 13                         # [linux]
  - 17                         # [osx]
  - 17                         # [win]

cxx_compiler_version:
  - 13                         # [linux]
  - 17                         # [osx]
  - 17                         # [win]

# macOS 部署目标版本
MACOSX_DEPLOYMENT_TARGET:
  - 10.15                      # [osx and x86_64]
  - 11.0                       # [osx and arm64]

# macOS SDK 路径（需要手动下载 SDK，因许可问题 conda-forge 不打包分发）
# 注意：本地构建时需要设置；conda-forge CI 已预装
CONDA_BUILD_SYSROOT:
  - /opt/MacOSX11.3.sdk        # [osx]

# 通道配置
channel_sources:
  - conda-forge
channel_targets:
  - conda-forge main
```

### 2.3 recipe/meta.yaml 示例（C/C++ 库，CMake 构建）

```yaml
{% set name = "example-package" %}
{% set version = "1.0.0" %}

package:
  name: {{ name|lower }}
  version: {{ version }}

source:
  url: https://github.com/example/{{ name }}/archive/v{{ version }}.tar.gz
  sha256: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

build:
  number: 0
  skip: true  # [win and vc&lt;14]

requirements:
  build:
    - {{ compiler('c') }}
    - {{ compiler('cxx') }}
    - {{ stdlib('c') }}
    - cmake
    - ninja
    - make  # [not win]
    - pkg-config
    # Python 交叉编译需要：build 平台的 Python + cross-python
    - cross-python_{{ target_platform }}  # [build_platform != target_platform]
    - python                               # [build_platform != target_platform]
    - cython                               # [build_platform != target_platform]
    - numpy                                # [build_platform != target_platform]
  host:
    - python
    - pip
    - cython
    - numpy
    - zlib
    - libboost-devel
  run:
    - python

test:
  commands:
    - test -f $PREFIX/lib/libexample.so  # [linux]
    - test -f $PREFIX/lib/libexample.dylib  # [osx]
    - if not exist %PREFIX%\\Library\\lib\\example.lib exit 1  # [win]
  imports:
    - example

about:
  home: https://github.com/example/example-package
  license: MIT
  summary: 'Example package for cross-compilation demo'
```

### 2.4 recipe/build.sh（Unix 构建脚本）

```bash
#!/bin/bash
set -e -x

# 复制更新的 config.sub/config.guess（autotools 项目需要）
if [ -f "$BUILD_PREFIX/share/gnuconfig/config.sub" ]; then
    cp $BUILD_PREFIX/share/gnuconfig/config.* .
fi

# ====== Python 扩展特殊处理（如使用 NumPy）======
if [[ "${CONDA_BUILD_CROSS_COMPILATION:-}" == "1" ]]; then
    Python_INCLUDE_DIR="$(python -c 'import sysconfig; print(sysconfig.get_path("include"))')"
    Python_NumPy_INCLUDE_DIR="$(python -c 'import numpy; print(numpy.get_include())')"
    CMAKE_ARGS+=" -DPython_EXECUTABLE:PATH=${PYTHON}"
    CMAKE_ARGS+=" -DPython_INCLUDE_DIR:PATH=${Python_INCLUDE_DIR}"
    CMAKE_ARGS+=" -DPython_NumPy_INCLUDE_DIR=${Python_NumPy_INCLUDE_DIR}"
    CMAKE_ARGS+=" -DPython3_EXECUTABLE:PATH=${PYTHON}"
    CMAKE_ARGS+=" -DPython3_INCLUDE_DIR:PATH=${Python_INCLUDE_DIR}"
    CMAKE_ARGS+=" -DPython3_NumPy_INCLUDE_DIR=${Python_NumPy_INCLUDE_DIR}"
fi

# ====== CMake 配置（必须传递 CMAKE_ARGS）======
cmake ${CMAKE_ARGS} -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_FIND_FRAMEWORK=NEVER \
    -DCMAKE_FIND_APPBUNDLE=NEVER \
    -S . -B build

cmake --build build -j${CPU_COUNT}
cmake --install build

# ====== 测试保护：仅在原生构建或有模拟器时运行 ======
if [[ "${CONDA_BUILD_CROSS_COMPILATION:-}" != "1" || "${CROSSCOMPILING_EMULATOR:-}" != "" ]]; then
    cd build &amp;&amp; ctest --output-on-failure -j${CPU_COUNT}
fi
```

### 2.5 recipe/bld.bat（Windows 构建脚本）

```batch
@echo on
setlocal EnableDelayedExpansion

if "%CONDA_BUILD_SKIP_TESTS%"=="1" (
    set CMAKE_ARGS=%CMAKE_ARGS% -DDISABLE_TESTS=ON
)

cmake %CMAKE_ARGS% -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% ^
    -DCMAKE_INSTALL_LIBDIR=lib ^
    -DBUILD_SHARED_LIBS=ON ^
    -S . -B build
if errorlevel 1 exit 1

cmake --build build -j%CPU_COUNT% --config Release
if errorlevel 1 exit 1

cmake --install build --config Release
if errorlevel 1 exit 1

if not "%CONDA_BUILD_SKIP_TESTS%"=="1" (
    cd build
    ctest --output-on-failure -j%CPU_COUNT% -C Release
    if errorlevel 1 exit 1
)
```

---

## 3. 工具链包名清单

### 3.1 macOS 目标（osx-64 / osx-arm64）

从 linux-64 或 osx-64 构建时可用：

| 包名 | 用途 | 支持的构建平台 |
|------|------|----------------|
| `clang_osx-64` | C 编译器（osx-64 目标） | linux-64, osx-64, osx-arm64 |
| `clangxx_osx-64` | C++ 编译器（osx-64 目标） | linux-64, osx-64, osx-arm64 |
| `gfortran_osx-64` | Fortran 编译器（osx-64 目标） | linux-64, osx-64 |
| `clang_osx-arm64` | C 编译器（osx-arm64 目标） | linux-64, osx-64, osx-arm64 |
| `clangxx_osx-arm64` | C++ 编译器（osx-arm64 目标） | linux-64, osx-64, osx-arm64 |
| `gfortran_osx-arm64` | Fortran 编译器（osx-arm64 目标） | linux-64, osx-64 |
| `cctools_osx-64` | 汇编器/归档器/ranlib/otool 等（osx-64 目标） | linux-64, osx-64, osx-arm64 |
| `cctools_osx-arm64` | 汇编器/归档器等（osx-arm64 目标） | linux-64, osx-64, osx-arm64 |
| `ld64_osx-64` | Mach-O 链接器（osx-64 目标） | linux-64, osx-64, osx-arm64 |
| `ld64_osx-arm64` | Mach-O 链接器（osx-arm64 目标） | linux-64, osx-64, osx-arm64 |
| `ldid` | macOS ad-hoc 代码签名工具（跨平台） | linux-64, osx-64 |
| `sdkroot_env_osx-64` | 设置 SDKROOT 环境变量（noarch 元包） | 所有平台 |
| `sdkroot_env_osx-arm64` | 设置 SDKROOT 环境变量（noarch 元包） | 所有平台 |

&gt; **重要**：`{{ compiler('c') }}` 和 `{{ compiler('cxx') }}` Jinja 宏会自动解析为正确的编译器包名，无需手动指定。

### 3.2 Windows 目标（win-64）

从 linux-64/osx-64/osx-arm64 构建时可用：

| 包名 | 用途 | ABI 兼容性 |
|------|------|------------|
| `clang_win-64` | C/C++ 编译器（LLVM/Clang，MSVC ABI 兼容） | MSVC（推荐，主流） |
| `clangxx_win-64` | C++ 编译器（随 clang_win-64 安装） | MSVC |
| `gcc_win-64` | C 编译器（GCC/MinGW-w64） | MinGW |
| `gxx_win-64` | C++ 编译器（GCC/MinGW-w64） | MinGW |
| `gfortran_win-64` | Fortran 编译器（MinGW） | MinGW |
| `binutils_win-64` | 二进制工具（MinGW） | - |
| `m2w64-sysroot_win-64` | Windows 系统根目录/头文件/库 | MinGW/UCRT |
| `gendef` | 从 DLL 生成 .def 文件工具 | - |
| `ucrt` | Universal C Runtime | UCRT（Windows 10+） |

&gt; **推荐**：优先使用 `clang_win-64`（MSVC ABI），这是 conda-forge Windows 包的默认编译器，与大多数现有二进制兼容。

### 3.3 macOS SDK 说明

**关键问题**：由于 Apple SDK 许可限制，conda-forge **不能分发** macOS SDK。

**获取途径**：
1. Apple Developer 网站下载 Xcode（需要 Apple ID）
2. 社区镜像：
   - https://github.com/phracker/MacOSX-SDKs
   - https://github.com/devernay/xcodelegacy

**本地配置**：
```bash
# 下载并解压 SDK 到 /opt 目录
# 然后在 conda_build_config.yaml 中设置：
CONDA_BUILD_SYSROOT:
  - /opt/MacOSX11.3.sdk  # [osx]
```

**conda-forge CI 环境**：Azure Pipelines 和 Travis-CI 的 macOS/ Linux 构建机已预装 SDK，无需手动配置。

**自动检测**：`sdkroot_env_osx-*` 包会通过以下逻辑设置 SDKROOT：
1. 如果 CONDA_BUILD_SYSROOT 已设置，使用该值
2. 如果在 macOS 上，通过 `xcrun --show-sdk-path` 自动检测
3. 如果以上都失败，报错

### 3.4 其他辅助包

| 包名 | 用途 |
|------|------|
| `cross-python_&lt;platform&gt;` | Python 交叉编译环境（如 cross-python_linux-64、cross-python_osx-64、cross-python_win-64） |
| `cross-r-base_&lt;platform&gt;` | R 交叉编译环境 |
| `gnuconfig` | 更新的 config.sub/config.guess（autotools 项目识别新平台需要） |
| `autotools_clang_conda` | Windows 上使用 autotools + clang 的辅助脚本 |
| `qemu-user-static` | Linux 用户态模拟器（用于运行跨架构测试） |

---

## 4. CONDA_BUILD_CROSS_COMPILATION 环境变量详解

### 4.1 核心环境变量列表

| 变量名 | 值 | 设置时机 | 用途 |
|--------|-----|----------|------|
| `CONDA_BUILD_CROSS_COMPILATION` | `"1"` | build_platform != host_platform 时 | **判断是否正在交叉编译的主要标志** |
| `CONDA_TOOLCHAIN_BUILD` | 如 `x86_64-conda-linux-gnu` | 总是 | 构建平台的 autoconf 三元组 |
| `CONDA_TOOLCHAIN_HOST` | 如 `arm64-apple-darwin20.0.0` | 总是 | 宿主平台的 autoconf 三元组 |
| `build_platform` | 如 `linux-64` | 总是 | 构建平台（v1 recipe 选择器用） |
| `host_platform` | 如 `osx-arm64` | 总是 | 宿主平台（v1 recipe 选择器用） |
| `target_platform` | 如 `osx-arm64` | 总是 | 宿主平台（v0 recipe 选择器用，兼容） |
| `CC` | 交叉编译器路径 | 编译器激活时 | C 编译器（如 `x86_64-apple-darwin20.0.0-clang`） |
| `CXX` | 交叉编译器路径 | 编译器激活时 | C++ 编译器 |
| `CC_FOR_BUILD` | 原生编译器路径 | 编译器激活时 | 构建平台的 C 编译器（编译构建时需要运行的工具） |
| `CXX_FOR_BUILD` | 原生编译器路径 | 编译器激活时 | 构建平台的 C++ 编译器 |
| `CMAKE_ARGS` | 预配置的 CMake 参数 | 编译器激活时 | **必须传递给 cmake**，包含交叉编译配置 |
| `MESON_ARGS` | 预配置的 Meson 参数 | 编译器激活时 | **必须传递给 meson**，包含交叉编译配置 |
| `CROSSCOMPILING_EMULATOR` | qemu 路径或空 | 有模拟器时 | 运行目标平台二进制的模拟器路径 |
| `CONDA_BUILD_SYSROOT` | SDK 路径 | macOS 构建时 | macOS SDK 根目录 |
| `MACOSX_DEPLOYMENT_TARGET` | 如 `10.15` | macOS 构建时 | 最低支持的 macOS 版本 |
| `PYTHON` | host 平台 Python 路径 | 总是 | Host 平台 Python 解释器路径 |
| `AR`/`RANLIB`/`LD` 等 | 交叉工具路径 | 编译器激活时 | 归档器/链接器等 |

### 4.2 build.sh 中检测交叉编译的标准模式

```bash
# 模式1：检查交叉编译标志（最可靠）
if [[ "${CONDA_BUILD_CROSS_COMPILATION:-}" == "1" ]]; then
    echo "Cross-compiling from ${build_platform} to ${target_platform}"
    # 交叉编译特有逻辑
fi

# 模式2：检查是否有模拟器可用（决定是否运行测试）
if [[ "${CONDA_BUILD_CROSS_COMPILATION:-}" != "1" || "${CROSSCOMPILING_EMULATOR:-}" != "" ]]; then
    # 可以运行测试
    make check
    # 或 ctest
fi

# 模式3：针对特定目标平台
if [[ "${target_platform}" == "osx-arm64" ]]; then
    echo "Building for Apple Silicon"
fi

if [[ "${target_platform}" == win-* ]]; then
    echo "Building for Windows (cross-compile from Unix)"
fi
```

### 4.3 meta.yaml 中使用选择器

```yaml
requirements:
  build:
    - {{ compiler('c') }}
    # 仅在交叉编译时需要的依赖
    - cross-python_{{ target_platform }}  # [build_platform != target_platform]
    - python                               # [build_platform != target_platform]
  host:
    - python

test:
  commands:
    # 仅在非交叉编译或有模拟器时运行的测试
    - ./run_tests.sh  # [build_platform == target_platform or CROSSCOMPILING_EMULATOR]
```

---

## 5. CMake/scikit-build-core 交叉编译变量传递

### 5.1 conda-forge 自动设置的 CMAKE_ARGS

编译器激活脚本会自动在 `CMAKE_ARGS` 中设置以下关键变量：

| CMake 变量 | 值（示例） | 说明 |
|------------|------------|------|
| `CMAKE_SYSTEM_NAME` | `Darwin`/`Windows`/`Linux` | 目标系统名称 |
| `CMAKE_SYSTEM_PROCESSOR` | `x86_64`/`arm64`/`aarch64` | 目标处理器架构 |
| `CMAKE_C_COMPILER` | 交叉 CC 路径 | C 编译器 |
| `CMAKE_CXX_COMPILER` | 交叉 CXX 路径 | C++ 编译器 |
| `CMAKE_FIND_ROOT_PATH` | `${PREFIX}` | 查找库/头文件的根路径 |
| `CMAKE_FIND_ROOT_PATH_MODE_PROGRAM` | `NEVER` | 不在 host 前缀查找程序 |
| `CMAKE_FIND_ROOT_PATH_MODE_LIBRARY` | `ONLY` | 仅在 host 前缀查找库 |
| `CMAKE_FIND_ROOT_PATH_MODE_INCLUDE` | `ONLY` | 仅在 host 前缀查找头文件 |
| `CMAKE_INSTALL_PREFIX` | `${PREFIX}` | 安装前缀 |
| `CMAKE_OSX_SYSROOT` | `${CONDA_BUILD_SYSROOT}` | macOS SDK 路径 |

**使用方式**：在 build.sh 中调用 cmake 时必须传递 `${CMAKE_ARGS}`：
```bash
cmake ${CMAKE_ARGS} ..
```

### 5.2 scikit-build-core 交叉编译支持

scikit-build-core **原生支持** conda 交叉编译环境，会自动识别以下配置：

| 环境变量 | 作用 | 平台 |
|----------|------|------|
| `CMAKE_ARGS` | 自动传递给 CMake | 所有平台 |
| `ARCHFLAGS` | macOS 架构标志（如 `-arch arm64`） | macOS |
| `MACOSX_DEPLOYMENT_TARGET` | macOS 部署目标 | macOS |
| `VSCMD_ARG_TGT_ARCH` | Visual Studio 目标架构（`x64`/`arm64`） | Windows |
| `SETUPTOOLS_EXT_SUFFIX` | 扩展模块后缀（跨平台编译时设置） | Windows/Linux |
| `DIST_EXTRA_CONFIG` | setuptools 风格配置文件路径 | Windows |
| `_PYTHON_HOST_PLATFORM` | Python 宿主平台标识（Pyodide 等） | 特殊平台 |

**scikit-build-core 配置建议（pyproject.toml）**：

```toml
[build-system]
requires = ["scikit-build-core>=0.9", "cmake>=3.26", "ninja"]
build-backend = "scikit_build_core.build"

[tool.scikit-build]
# 使用 conda-forge 的 CMAKE_ARGS，不手动覆盖
cmake.args = []
# 允许覆盖 wheel tags（如需要）
# wheel.tags = ["py3-none-any"]
# 交叉编译时可能需要禁用 Python 自动检测，使用工具链文件
# cmake.python-hints = false

[tool.scikit-build.overrides]
# 针对不同平台的覆盖配置
```

**CMakeLists.txt 最佳实践**：
```cmake
cmake_minimum_required(VERSION 3.26)
project(example LANGUAGES CXX)

# 使用 scikit-build-core 提供的 SOABI 变量
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

Python_add_library(_example MODULE src/bindings.cpp)
target_include_directories(_example PRIVATE ${Python_INCLUDE_DIRS})
# 使用 ${SKBUILD_SOABI} 作为扩展后缀（scikit-build-core 自动设置）
set_target_properties(_example PROPERTIES PREFIX "" SUFFIX ".${SKBUILD_SOABI}.so")
install(TARGETS _example DESTINATION .)
```

### 5.3 手动工具链文件（高级用法）

对于复杂项目，可能需要编写 CMake 工具链文件：

```cmake
# toolchain-osx-arm64.cmake
set(CMAKE_SYSTEM_NAME Darwin)
set(CMAKE_SYSTEM_PROCESSOR arm64)
set(triple arm64-apple-darwin20.0.0)

set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)
set(CMAKE_C_COMPILER_TARGET ${triple})
set(CMAKE_CXX_COMPILER_TARGET ${triple})

set(CMAKE_SYSROOT /opt/MacOSX11.3.sdk)
set(CMAKE_OSX__DEPLOYMENT_TARGET 11.0)

set(CMAKE_FIND_ROOT_PATH $ENV{PREFIX})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
```

使用方式：
```bash
export CMAKE_TOOLCHAIN_FILE=$RECIPE_DIR/toolchain-osx-arm64.cmake
cmake ${CMAKE_ARGS} ..
```

&gt; **注意**：conda-forge 的 `CMAKE_ARGS` 已包含大部分必要配置，通常不需要手动编写工具链文件。

---

## 6. Wine 运行 Windows conda/Python 可行性

### 6.1 官方支持状态

根据 conda-forge 官方文档（[Testing using wine](https://conda-forge.org/docs/how-to/advanced/windows/local-testing/#testing-using-wine)）：

&gt; **Miniforge 在 Wine 的 cmd shell 中可以正常工作**，可用于创建和运行 Conda 环境。有时 Wine 还能提供更有洞察力的错误信息。

### 6.2 可行性评估

| 场景 | 可行性 | 说明 |
|------|--------|------|
| 安装 Miniforge/Miniconda | ✅ 可行 | Wine 支持运行 Windows 安装程序 |
| 创建 conda 环境 | ✅ 可行 | conda 命令可在 Wine cmd 中运行 |
| 安装纯 Python 包 | ✅ 可行 | noarch 包可正常安装导入 |
| 运行纯 Python 代码 | ✅ 可行 | Python 解释器可正常工作 |
| 导入编译的 C 扩展 | ⚠️ 部分可行 | 简单扩展可运行，复杂的可能遇到 DLL 问题 |
| 运行 CTest 测试套件 | ⚠️ 部分可行 | 取决于 DLL 依赖完整性 |
| conda-build 构建包 | ❌ 不推荐 | 复杂，不用于 CI |

### 6.3 conda-forge CI 中的使用现状

- **conda-forge CI 不使用 Wine**：win-64 包通过 AppVeyor 或 Azure Windows runner 原生构建
- **Wine 用于本地调试**：官方文档推荐作为没有 Windows 机器时的本地调试工具
- **无大规模自动化测试案例**：目前没有 conda-forge feedstock 常规使用 Wine 运行 win-64 测试的公开案例

### 6.4 Wine 测试的调试工具

在 Wine 中调试 DLL 加载问题：

| 工具 | 用途 |
|------|------|
| `WINEDEBUG=+loaddll` | 查看 DLL 加载详细日志 |
| Dependencies (lucasg/Dependencies) | 现代 Dependency Walker，Wine 兼容良好 |
| `gendef`（conda 包） | Unix 上生成 DLL 导入库定义 |
| `WINEPATH` | 设置 Wine 路径 |

**基本使用示例**：
```bash
# 在 Wine 中安装 Miniforge（静默安装）
wine Miniforge3-Windows-x86_64.exe /S /D=C:\\miniforge3

# 使用 Wine cmd
wine cmd
# 在 cmd 中：
C:\&gt; C:\miniforge3\Scripts\activate.bat
C:\&gt; conda create -n test python=3.12 -y
C:\&gt; conda activate test
C:\&gt; python -c "import sys; print(sys.platform)"
```

---

## 7. Open Questions 解答

### Q1: osx-arm64 cross on linux-64 是否可行？

**结论：技术上可行，但需要手动准备 macOS SDK，conda-forge 官方 CI 不常规使用此配置。**

**详细说明**：

1. **技术可行性**：
   - ✅ `clang_osx-arm64`、`cctools_osx-arm64`、`ld64_osx-arm64` 包在 linux-64 上可用
   - ✅ Clang 原生支持跨架构编译（不像 GCC 需要构建单独的交叉编译器）
   - ✅ `ldid` 支持在 Linux 上进行 ad-hoc 代码签名（macOS Big Sur+ 要求）
   - ❌ 需要手动下载 macOS SDK（许可限制无法分发）

2. **conda-forge 实践**：
   - osx-arm64 包主要通过 **osx-64 runner 交叉编译**（Azure macOS x86_64 机器）
   - 或使用 **Apple Silicon 原生 runner**（Azure 已支持）
   - linux-64 → osx-arm64 是可行的，但不是官方默认路径

3. **本地构建步骤**：
   ```bash
   # 1. 下载 MacOSX11.3.sdk 或更高版本到 /opt/
   # 2. 在 conda_build_config.yaml 中设置 CONDA_BUILD_SYSROOT
   # 3. 配置 conda-forge.yml: osx_arm64: linux_64
   # 4. rerender 后即可尝试构建
   ```

4. **已知挑战**：
   - 部分 autotools 项目的 configure 脚本可能在跨 OS 时出问题
   - Fortran 编译器（gfortran_osx-arm64）在 Linux 上可能有更多限制
   - 无法运行测试（无 qemu/darling 可用）

### Q2: win-64 交叉编译选 MSVC ABI 还是 MinGW？

**结论：优先选择 MSVC ABI（clang_win-64），这是 conda-forge 的默认和推荐方案。**

| 对比项 | clang_win-64 (MSVC ABI) | gcc_win-64 (MinGW) |
|--------|-------------------------|---------------------|
| **conda-forge 默认** | ✅ 是 | ❌ 否（仅 R 等特殊生态使用） |
| **ABI 兼容性** | 与 MSVC 编译的二进制兼容 | MinGW ABI（与 MSVC 不兼容） |
| **C++ 标准库** | 使用 MSVC 的 STL（或 libc++） | 使用 libstdc++ |
| **运行时** | UCRT (Windows 10+) | msvcrt/ucrt |
| **导入库** | .lib 格式 | .a / .dll.a 格式 |
| **现有包兼容性** | ✅ 可与所有 conda-forge win-64 包链接 | ⚠️ 只能与其他 MinGW 包链接 |
| **异常处理** | SEH | SJLJ/DWARF |
| **推荐场景** | 绝大多数 conda 包、Python 扩展 | R 包、纯 MinGW 生态项目 |

**注意**：
- `clang_win-64` 不依赖 Visual Studio，可在 Linux/macOS 上纯交叉编译
- 它使用 LLVM/Clang，但生成的是 MSVC ABI 兼容的二进制
- Python 扩展在 Windows 上必须使用 MSVC ABI（因为官方 Python 用 MSVC 编译）

### Q3: Wine + conda 成熟度如何？能否用于 CI 测试？

**结论：Miniforge/Python 在 Wine 中可运行，但成熟度不足以作为 conda-forge 级别 CI 的常规测试手段。**

**成熟度评估**：

1. **已验证可行**：
   - Miniforge 安装和基本环境创建
   - 纯 Python 代码运行
   - noarch 包安装
   - 简单的 C 扩展导入
   - 基础 DLL 依赖问题调试

2. **存在的问题**：
   - Wine 对 Windows API 的实现不完整，某些库可能调用未实现的函数（会看到 `unimplemented function` 错误）
   - 复杂的 C++ 扩展可能因 C++ ABI 或异常处理差异崩溃
   - 多线程、异步 IO 等高级功能可能有问题
   - 不同 Wine 版本行为可能不一致
   - 性能比原生 Windows 慢

3. **CI 使用建议**：
   - ❌ **不推荐**作为主要测试手段：conda-forge 已提供 Windows CI runner
   - ✅ **可用于**：本地快速验证基本功能、DLL 依赖问题调试
   - ⚠️ **如果要用在 CI**：
     - 仅作为烟雾测试（smoke test）：验证包能安装、能导入、基本命令能运行
     - 不要期望完整测试套件通过
     - 固定 Wine 版本
     - 预期会有间歇性失败

### Q4: scikit-build-core 交叉编译时 platform/system 如何传递？

**结论：scikit-build-core 会自动读取 conda 环境变量，通过 CMAKE_ARGS 传递 CMAKE_SYSTEM_NAME 等变量，无需手动配置。**

**变量传递链路**：

```
conda 编译器激活脚本
    ↓ 设置
CMAKE_ARGS (包含 CMAKE_SYSTEM_NAME, CMAKE_SYSTEM_PROCESSOR, 编译器路径等)
    ↓ scikit-build-core 自动读取
传递给 CMake
    ↓
FindPython 模块使用正确的平台信息查找
    ↓
生成正确平台标签的 wheel
```

**关键点**：

1. **必须传递 `CMAKE_ARGS`**：scikit-build-core 会尊重这个环境变量，但要确保不手动覆盖它
2. **Python 头文件/库位置**：
   - 交叉编译时 FindPython 可能找不到正确的路径
   - 需要手动设置（如 conda-forge 文档中的 Python_INCLUDE_DIR 代码片段）
3. **Wheel 标签**：
   - scikit-build-core 读取环境变量自动确定正确的 wheel tags
   - macOS 使用 `ARCHFLAGS`，Windows 使用 `VSCMD_ARG_TGT_ARCH`
4. **SOABI/扩展后缀**：
   - cross-python 环境会通过 `_PYTHON_SYSCONFIGDATA_NAME` 让 Python 报告正确的 SOABI
   - scikit-build-core 使用 `SKBUILD_SOABI` 变量传递给 CMake

**常见问题排查**：
- 如果 FindPython 找到构建平台的 Python：设置 `-DPython_EXECUTABLE=${PYTHON}`
- 如果 wheel 标签错误：检查 `_PYTHON_HOST_PLATFORM` 是否正确设置
- 如果链接错误：确认 host 平台的库在 `${PREFIX}` 而不是 `${BUILD_PREFIX}`

---

## 8. 关键注意事项

### 8.1 交叉编译常见陷阱

| 陷阱 | 症状 | 解决方案 |
|------|------|----------|
| 忘记传递 `${CMAKE_ARGS}` | CMake 使用原生编译器，找到构建平台的库 | 总是写 `cmake ${CMAKE_ARGS} ..` |
| 测试未保护 | 交叉编译时尝试运行 host 二进制，报错 "Exec format error" | 用 `CONDA_BUILD_CROSS_COMPILATION` 保护测试命令 |
| build/host 依赖放错 | 构建时运行的工具（如 cython）从 host 安装，无法执行 | 构建时需要运行的放 build（条件性），链接用的库放 host |
| autotools 不识别平台 | configure 报错 "cannot guess build type" | 安装 `gnuconfig` 包，复制 config.sub/config.guess |
| macOS SDK 找不到 | 编译报错找不到头文件 | 设置 `CONDA_BUILD_SYSROOT` 环境变量 |
| Python 扩展构建失败 | distutils/setuptools 使用错误的编译器 | 添加 `cross-python_{{ target_platform }}` 到 build 依赖 |
| Windows 路径问题 | CMake 找不到库 | 使用 `${LIBRARY_PREFIX}`、`${LIBRARY_BIN}`、`${LIBRARY_LIB}`、`${LIBRARY_INC}` 变量 |

### 8.2 Windows 特殊路径变量

在 bld.bat 中使用这些 conda-build 预置变量：

| 变量 | 值 | 用途 |
|------|-----|------|
| `%LIBRARY_PREFIX%` | `%PREFIX%\Library` | 库安装前缀 |
| `%LIBRARY_BIN%` | `%PREFIX%\Library\bin` | DLL 和可执行文件 |
| `%LIBRARY_INC%` | `%PREFIX%\Library\include` | 头文件 |
| `%LIBRARY_LIB%` | `%PREFIX%\Library\lib` | .lib 导入库/静态库 |
| `%SCRIPTS%` | `%PREFIX%\Scripts` | Python 脚本 |
| `%PREFIX%` | 环境根目录 | 类似 Unix 的 $PREFIX |

### 8.3 本地测试交叉编译

```bash
# 安装必要工具
conda install -n base conda-build conda-smithy mamba

# 方法1：使用 build-locally.py（conda-smithy 生成）
# 设置目标平台环境变量
export CONFIG=linux_64_  # 或 osx_64_, win_64_, osx_arm64_
python build-locally.py

# 方法2：直接用 conda build
conda build recipe -m .ci_support/osx_64_.yaml
```

### 8.4 依赖拆分原则（速查）

| 类型 | 示例 | build 节 | host 节 |
|------|------|----------|---------|
| 编译器 | gcc, clang | ✅ | ❌ |
| 构建系统 | cmake, make, ninja, meson, pkg-config | ✅ | ❌ |
| 构建时工具 | bison, flex, gperf | ✅ | ❌ |
| Python（解释器，运行构建脚本） | python | ✅（交叉时） | ✅ |
| Python 构建工具 | cython, numpy, maturin | ✅（交叉时） | ✅ |
| cross-python | cross-python_* | ✅（仅交叉时） | ❌ |
| 要链接的库 | zlib, boost-devel | ❌ | ✅ |
| 要链接的库的工具 | *-config 脚本（某些情况） | ✅ | ✅ |
| Python 运行时 | python | ❌ | ✅（run 也要） |
| 纯 Python 依赖 | six, requests | ❌ | host + run |

---

## 9. 参考链接

### 官方文档
1. **conda-forge Cross-compilation How-to**：https://conda-forge.org/docs/how-to/advanced/cross-compilation/
2. **conda-forge Cross-compilation Concepts**：https://conda-forge.org/docs/maintainer/understanding_conda_forge/cross-compilation/
3. **conda-forge Knowledge Base**：https://conda-forge.org/docs/maintainer/knowledge_base/
4. **conda-forge.yml Configuration**：https://conda-forge.org/docs/maintainer/conda_forge_yml/
5. **Testing Windows builds with Wine**：https://conda-forge.org/docs/how-to/advanced/windows/local-testing/#testing-using-wine

### 关键 Feedstock
6. **clang-compiler-activation-feedstock**：https://github.com/conda-forge/clang-compiler-activation-feedstock
7. **ctng-compiler-activation-feedstock** (GCC/MinGW)：https://github.com/conda-forge/ctng-compiler-activation-feedstock
8. **cctools-and-ld64-feedstock**：https://github.com/conda-forge/cctools-and-ld64-feedstock
9. **osx-sysroot-feedstock**：https://github.com/conda-forge/osx-sysroot-feedstock
10. **autotools_clang_conda-feedstock**：https://github.com/conda-forge/autotools_clang_conda-feedstock

### 工具链/SDK
11. **cctools-port**（Linux 上的 Mach-O 工具）：https://github.com/tpoechtrager/cctools-port
12. **MacOSX-SDKs 社区镜像**：https://github.com/phracker/MacOSX-SDKs
13. **XcodeLegacy**：https://github.com/devernay/xcodelegacy

### scikit-build-core
14. **scikit-build-core Cross-compiling Documentation**：https://scikit-build-core.readthedocs.io/en/latest/guide/crosscompile.html

### 博客文章
15. **macOS ARM builds on conda-forge**（osx-arm64 交叉编译历史）：https://github.com/conda-forge/conda-forge.github.io/blob/main/blog/2020-10-29-macos-arm64.md
16. **gcc, g++ builds on macos**（2025 更新：Linux→macOS GCC 交叉编译）：https://conda-forge.org/blog/2025/11/21/gcc-macos/

### 查找更多示例
在 GitHub 中搜索 conda-forge 组织内的交叉编译 recipe：
- v0 recipes: `org:conda-forge path:meta.yaml "build_platform != target_platform"`
- v1 recipes: `org:conda-forge path:recipe.yaml "build_platform != host_platform"`
- CMake + Unix: `org:conda-forge cmake path:recipe/*.sh`
