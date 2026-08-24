---
type: Concept
title: "视角152：pyproject.toml 构建配置"
description: "分析 tvm-ffi 基于 pyproject.toml 的标准构建配置，包括 scikit-build-core 后端、动态版本管理、Cython 依赖、Python 包声明与源码分发规则。"
tags:
  - build
  - python
  - pyproject
  - packaging
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-329, F-330
  - code:
    - pyproject.toml
---

# 视角152：pyproject.toml 构建配置

## 概述

tvm-ffi 的 Python 打包遵循 PEP 517/621，通过根目录 `pyproject.toml`（`d:\AI\.chaos\libs\ffi\tvm-ffi\pyproject.toml`）声明构建系统、项目元数据、依赖分组与质量工具配置。尤其值得一提的是它选用 **scikit-build-core** 作为构建后端，实现一套声明式配置即可驱动 CMake 原生编译与 Python Wheel 打包的联动。

## 项目元数据

`[project]` 段定义包名为 `apache-tvm-ffi`（`pyproject.toml:19`），版本号采用 `dynamic = ["version"]`（`pyproject.toml:20`），真实版本在构建期由 setuptools-scm 从 Git 推导并写入 `python/tvm_ffi/_version.py`（`pyproject.toml:310-312`）。Python 版本要求为 `>=3.9`（`pyproject.toml:34`），运行依赖仅有一个 `typing-extensions>=4.5`（`pyproject.toml:35`），体现了 FFI 核心库"轻依赖"的设计取向。

还声明了两个命令行入口脚本（`pyproject.toml:104-106`）：
- `tvm-ffi-config = "tvm_ffi.config:__main__"`：提供库路径查询，供 Rust 的 build.rs 调用。
- `tvm-ffi-stubgen = "tvm_ffi.stub.cli:__main__"`：存根生成命令行工具。

## 构建系统声明

```toml
[build-system]
requires = ["scikit-build-core>=0.10.0", "cython>=3.2.8", "setuptools-scm"]
build-backend = "scikit_build_core.build"
```

`pyproject.toml:108-114` 声明三条构建前置依赖，其中 `cython>=3.2.8` 的版本约束在注释中特别说明：3.2.8（2026-06-30 发布）修复了自由线程（free-threaded）Python 3.14t 下 `__dealloc__` 执行期间的对象 keep-alive 问题（`pyproject.toml:108-113`）。

## scikit-build-core 配置

`[tool.scikit-build]` 段是可裁剪的关键：

- **版本元数据**：版本由 `scikit_build_core.metadata.setuptools_scm` 提供（`pyproject.toml:117`）。
- **最小版本与 Ninja**：`ninja.version = ">=1.11"`，`ninja.make-fallback = false`（`pyproject.toml:122-123`）。
- **CMake 参数**：`cmake.build-type = "Release"`，并传入 `-DTVM_FFI_ATTACH_DEBUG_SYMBOLS=ON`、`-DTVM_FFI_BUILD_TESTS=OFF`、`-DTVM_FFI_BUILD_PYTHON_MODULE=ON`（`pyproject.toml:134-140`）。这三个开关使 Wheel 构建在生产 Release 动态库的同时启用 Cython 模块，而绕过测试目标。
- **Wheel 内容**：`wheel.packages = ["python/tvm_ffi"]` 声明随 wheel 打包的 Python 包目录，`wheel.install-dir = "tvm_ffi"`（`pyproject.toml:146-147`）。
- **sdist 内容**：`sdist.include`（`pyproject.toml:150-178`）显式罗列 CMakeLists、cmake/、src/*.cc、include/、python/tvm_ffi、3rdparty 第三方头、文档与 tests 等，`sdist.exclude` 排除 `.git` 与构建产物。

## 质量工具生态

pyproject.toml 同时声明了 Ruff（`[tool.ruff]`，`pyproject.toml:196-247`）、pytest（`[tool.pytest.ini_options]`，并行 `-n auto`，`pyproject.toml:189-194`）、ty（`[tool.ty]`，`pyproject.toml:272-301`)、cibuildwheel（`[tool.cibuildwheel]`，`pyproject.toml:249-270`) 等工具的配置。这些与构建共同构成 `[dependency-groups]` 中的 `dev`/`test`/`docs`/`cpp`/`torch` 依赖分组（`pyproject.toml:41-102`），实现"构建、测试、开发、文档"环境的按需隔离。

## 设计分析

pyproject.toml 作为 PEP 517 的标准入口，将 C/C++ 原生编译（经 scikit-build-core 桥接 CMake）与纯 Python 打包统一到一个声明文件。动态版本、运行期单依赖、类别覆盖等手段共同保证了 tvm-ffi 能作为独立库发布，又能被 TVM 复用。`[dependency-groups]` 把工具型依赖与运行期依赖解耦，使最终 Wheel 保持最小体积。脚本入口则打通了 Python/Rust 两个绑定生态对原生库路径的查询需求。

## 扩展讨论

### scikit-build-core 把 CMake 装进 PEP 517 管线

选用 scikit-build-core 作为后端，等于在「pip→wheel」的标准前端与「cmake→target」的原生编译之间架了一座桥：`[tool.scikit-build]` 的 `cmake.build-type=Release`、`-DTVM_FFI_BUILD_PYTHON_MODULE=ON` 等开关直接透传给 CMake configure，使一次 `python -m build --wheel` 就能同时产出动态库与 Cython 扩展。这避免了「先手工跑 cmake、再包 wheel」的两段式，也把编译选项收敛进可声明的配置文件而非 shell 脚本。

### 动态版本与运行期最少依赖的双约束

`version = dynamic` + setuptools-scm 让版本从 Git 推导并写入 `_version.py`，避免手工改号、防止 tag 与源码漂移；`requires-python = ">=3.9"` 与唯一运行依赖 `typing-extensions` 则把 FFI 核心做到最小。这两个约束一方保证「包版本可审计」（源头是 Git），另一方保证「运行依赖可收敛」。`[dependency-groups]` 再按 dev/test/docs/cpp/torch 切分，使工具链依赖不进入最终 Wheel。

### sdist 白名单是源码可复建的保证

`sdist.include` 显式列出 CMakeLists、src/*.cc、include/、python/tvm_ffi 与 3rdparty 等，`sdist.exclude` 剔除 `.git` 与产物。这份白名单决定了「从 sdist 能否重建 wheel」：遗漏任一被 include 的编译单元或第三方头，都会让分发的 sdist 无法自举编译。因此它实际上是发布物「最小但完备」的契约，与仓库根 CMake 对编译动线的描述互为印证。

## 相关概念

- [005 Wheel 分发包](155-wheel-distribution.md)：[tool.cibuildwheel] 的多平台矩阵联动
- [006 One Wheel 策略](156-one-wheel-strategy.md)：Wheel 产物取舍
- [002 Cython 编译流程](153-cython-compilation.md)：CMake 参数联动
- [009 多 Python 版本支持](157-multi-python-version.md)：requires-python 与依赖分组