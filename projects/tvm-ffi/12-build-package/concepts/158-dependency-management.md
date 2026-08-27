---
type: Concept
title: "视角158：依赖管理"
description: "分析 tvm-ffi 的依赖管理策略，包括运行期最小依赖、依赖分组（dependency-groups）、原生库符号依赖、dl 库与 CPython 交互的边界设计。"
tags:
  - build
  - dependency
  - packaging
  - dlopen
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-354
  - code:
    - pyproject.toml
    - CMakeLists.txt
    - include/tvm/runtime/base.h
---

# 视角158：依赖管理

## 概述

依赖管理决定了 tvm-ffi 作为基础库的耦合边界。一方面它维持极小的运行期 Python 依赖（仅 `typing-extensions`），另一方面通过 `[dependency-groups]` 把构建/测试/开发/文档等多个环境的工具依赖隔离；在原生层则需处理 `dl` 库、线程库与符号全局可见性（F-354 揭示 TVM runtime 对 TVM FFI C ABI 的强依赖）。

## 运行期最小依赖

`pyproject.toml:35`：`dependencies = ["typing-extensions>=4.5"]`。运行期仅需这一纯类型支持库，这与 FFI 核心"框架无关、最小内核"的定位一致：原生能力全部封装在自编译的共享库中，Python 包不额外引入 numpy/torch 等重型运行依赖。重型能力以可选分组存在（如 `[dependency-groups] torch`，`pyproject.toml:44-51`）。

## dependency-groups 分组

`[dependency-groups]`（`pyproject.toml:41-102`）按用途隔离不同环境的依赖：

- `cpp`：`["ninja"]`
- `torch`：torch/setuptools/ninja/numpy/ml_dtypes，并含版本条件 `torch; python_version < '3.14'`
- `test`：引用 `torch` 分组 + pytest/pytest-xdist
- `dev`：引用 test 分组 + pre-commit/ruff/ty/clang-format/cython/scikit-build-core 等（`pyproject.toml:53-73`）
- `docs`：sphinx 生态（`pyproject.toml:74-102`）

这种分组使 CI 只需按需装 dev 或 test 组，避免污染运行期放车帽；`[tool.uv]` 还补充 `exclude-newer = "14 days"`（`pyproject.toml:304`）与 `requires-python` 约束。

## 原生层依赖管理

### dl / 线程 / 调试库

CMake 按 option 选择链接系统原生库：

- `TVM_FFI_USE_THREADS`：`find_package(Threads REQUIRED)` 并链 `Threads::Threads`（`CMakeLists.txt:134-138`）。
- `TVM_FFI_USE_EXTRA_CXX_API` + `TVM_FFI_USE_DL_LIBS`：链 `${CMAKE_DL_LIBS}`（`CMakeLists.txt:140-146`），为动态模块加载等扩展能力提供 `dlopen` 符号。
- MSVC：链 `DbgHelp.lib`（`CMakeLists.txt:154-157`）。

这些系统依赖随共享库打包装入，用户在 Wheel 场景无需手动处理。

### 符号可见性与全局符号

F-354（`include/tvm/runtime/base.h:27-29`）指出 "TVM runtime fully relies on TVM FFI C API" 并 `#include <tvm/ffi/c_api.h>`。这意味着 TVM 运行时对 tvm-ffi 符号有强运行期依赖。为满足这种跨库依赖，`base.py` 将 `tvm_runtime` 以 `RTLD_GLOBAL` 方式加载（见视角154），使 tvm_ffi 导出的符号对其他 DL 模块全局可见——依赖管理延伸到"符号查找空间"，而不只是包清单。

## 构建期依赖的版本钉住

dev 分组对编译链关键工具做了版本钉住：`cython>=3.2.8`（自由线程修复）、`scikit-build-core`、`ninja`、`setuptools-scm`，`dev`/`docs`/`test` 亦各自钉住 ruff/pre-commit/clang-format 等质量工具版本（`pyproject.toml:56-72`）。这保证 CI 前后端在不同运行者/不同时间构建结果可复现。

## 设计分析

tvm-ffi 的依赖管理体现了"运行期收敛、构建期放开、符号期协作"的分层观：Python 运行依赖压到最小，原生系统依赖用 option 显式开关，跨库符号依赖通过 RTLD_GLOBAL + 统一 C ABI 协调。`dependency-groups` 把环境复杂度从包内部搬到声明文件，让每个消费场景只需拉取所需的依赖子图。整体上，依赖是"声明式 + 平台感知"的产物，而非运行期"猜测"。

## 扩展讨论

### 依赖分组的本质：把环境切成可独立拉取的子图

`[dependency-groups]` 的 `cpp`/`torch`/`test`/`dev`/`docs` 五组，核心价值不是"多装几组依赖"，而是**让每种消费角色只拉自己需要的子图**：CI 测打包只需 dev（含 test 与 torch）、贡献者本地开发再叠加质量工具、纯运行只需最薄的 `typing-extensions`。配合 `[tool.uv] exclude-newer` 的发布时间约束，进一步把"可复现"从组粒度推进到"构件版本"粒度，避免日期过新、尚未经过验证的构件悄悄漂进依赖闭合集。

### 符号可见性是一种特殊的"运行期依赖"

`typing-extensions` 是 Python 层的显式依赖，而 `base.py` 用 `RTLD_GLOBAL` 加载 `tvm_runtime` 使 tvm_ffi 符号对其他 DL 模块全局可见，本质是在**符号查找空间**上「发布」一份依赖。它不能被 pip 清单表达，却决定"另一个 .so 里的代码能否在运行期 `dlsym` 到本库的符号"。tvm-ffi 选择把所有导出收敛到稳定 C ABI（F-354），使这种隐式符号依赖有明确边界，而不是靠命名巧合偶然可用。

### option 化系统依赖：让"平台差异"可重放

`Threads`、`dl`、`DbgHelp` 等系统库通过 `TVM_FFI_USE_*` 开关选择，把"某平台需要链什么原生库"变成**可在 configure 期重放的决定**。Windows 上无需 `dlopen` 语义也能关掉 dl 依赖、MSVC 才链 `DbgHelp.lib`——这些差异被显式键入构建系统而非散落在平台假设里，既满足可移植性，又让下游（如嵌入方）能按自己的运行时能力定向裁剪链接面。

## 相关概念

- [009 DLPack 供应商依赖](159-dlpack-vendor-dependency.md)：第三方头文件依赖管理
- [006 One Wheel 策略](156-one-wheel-strategy.md)：可拆分依赖与降级
- [004 共享库目标](154-shared-library-target.md)：RTLD_GLOBAL 符号依赖
- [006 最小核心设计哲学](/01-architecture/concepts/006-minimal-core-philosophy.md)：最小运行依赖的哲学基础