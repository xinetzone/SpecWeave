---
type: Concept
title: "视角157：多 Python 版本支持"
description: "分析 tvm-ffi 对多个 Python 版本的支持策略，包括 requires-python 范围、cibuildwheel 逐版本矩阵、自由线程 Python 3.14t、逐版本 ABI 构建与精确版本解释器查找。"
tags:
  - build
  - python
  - version
  - free-threaded
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-329, F-330, F-331, F-332
  - code:
    - pyproject.toml
    - CMakeLists.txt
---

# 视角157：多 Python 版本支持

## 概述

tvm-ffi 需要同时服务较宽范围的 Python 版本（≥3.9），并前瞻性地支持自由线程（free-threaded）Python 3.14t。其支持策略横跨 pyproject 的 `requires-python`、cibuildwheel 的逐版本构建矩阵，以及 CMake 构建时对 `Python EXACT` 版本的精确匹配，构成"声明范围 + 逐版本编译 + 逐版本标签"的三层配合。

## 声明层：requires-python

`pyproject.toml:34` 声明 `requires-python = ">=3.9"`，划定支持的 Python 下限。结合 cibuildwheel 构建矩阵 `cp39-* ~ cp314-*`、`cp314t-*`（`pyproject.toml:253`），下限声明与构建覆盖一致。`requires-python` 让 pip/uv 在用户环境 Python 过老时自动拒绝安装，避免 ABI 不符。

## 构建层：逐版本 ABI

源码多次强调不使用 abi3/limited API：

- CMake `python_add_library(..., WITH_SOABI)`（`CMakeLists.txt:297`），并按 `Python ${_tvm_ffi_python_version} EXACT`（`CMakeLists.txt:262-267`）精确匹配 Python 版本。
- PyObject 绑定用完整 Python C API（`Py_IncRef`、`PyObject_GC_Del`，`CMakeLists.txt:294-296`），因此只能逐版本编译。
- pyproject 注释明确 Wheel 标签为 `cp312-cp312` 而非 `cp312-abi3`（`pyproject.toml:118-121`）。

其结果是每个 CPython 小版本产出一个专属 Wheel，不能跨版本复用，但能充分访问 Python 内部与自由线程特性。

## 自由线程 Python 3.14t 支持

项目对 PEP 703 自由线程 Python（cp314t）有显式适配：

- CMake 构建期检测：`execute_process` 运行 Python 脚本检查 `Py_GIL_DISABLED == 1` 并打印 "Free-threaded Python detected."（`CMakeLists.txt:248-257`）。
- Cython 版本约束：`requires = [... "cython>=3.2.8"]`（`pyproject.toml:113`），因为 3.2.8 修复了自由线程下对象 keep-alive 问题（`pyproject.toml:108-113` 注释）。
- 构建矩阵包含 `cp314t-*`（`pyproject.toml:253`），且在依赖分组中 `torch; python_version < '3.14'`（`pyproject.toml:46`），说明对 3.14t 的依赖侧做了显式条件。

## 运行层：_ffi_api 签名声明

`python/tvm_ffi/_ffi_api.py` 在 Python 侧声明 C 函数签名（事实 F-332），如 `TVMFFIGetVersion`、`TVMFFIFunctionGetGlobal`、`TVMFFIFunctionCall`、`TVMFFIObjectIncRef/DecRef`（`_ffi_api.py:20-120`）。这些声明通过 `init_ffi_api("ffi", __name__)`（`_ffi_api.py:37`）绑定到已加载的 `libtvm_ffi` 符号，保证绑定层与当前解释器版本（含自由线程）的解耦——即使底层 ABI 逐版本，Python 层调用面保持一致。

## 设计分析与权衡

多版本支持的核心代价是"逐版本编译导致的构建矩阵膨胀"：cp39 到 cp314t 多达 7 个 Python 构建目标 × 多平台 NCS。项目以 cibuildwheel 的自动测试裁剪（`test-skip` 让 cp39-cp311 复用 cp312 测试，`pyproject.toml:256`）缓解测试负担。相比 abi3 单 Wheel 复用，逐版本策略放弃体积与矩阵精简，换取对自由线程与 Python 新特性的完整支持，这一取向在视角153 Cython、视角155 Wheel 中一脉相承。

## 扩展讨论

### 拒绝 abi3 的取舍

放弃 abi3/limited API 意味着每个 CPython 小版本必须产出专属 Wheel。收益是能完整访问 Python 内部结构与自由线程特性（如 `Py_GIL_DISABLED` 路径、对象 keep-alive），这恰是 FFI 高性能绑定需要的；代价是构建矩阵膨胀（cp39–cp314t × 多平台）与 wheel 体积增加。逐版本 CI coverage（cibuildwheel 用 `test-skip` 让 cp39–cp311 复用 cp312 测试）在不大幅加测的前提下压缩验证成本。

### EXACT 版本匹配与所谓 SOABI

CMake 用 `Python ${version} EXACT` 精确锁定解释器版本、`WITH_SOABI` 使扩展携带 ABI 后缀，这是「逐版本编译」的落地保证。SOABI 标签（如 `cpython-312-x86_64-linux-gnu`）正是让 pip 能分辨「这个 .so 属于哪个 Python」的机制——它把「只对本版本可用」的事实编码进文件名，从而避免误载不兼容扩展。

### 自由线程是本策略的压舱石

cp314t 并非额外附赠，而是策略成立的动因：abi3 通常无法表达 `Py_GIL_DISABLED` 的差异化编译，只有逐版本模型才能为自由线程单独出一个 `cp314t` 目标。项目在 build 期脚本检测 `Py_GIL_DISABLED == 1`、在依赖分组用 `torch; python_version < '3.14'` 做条件化，正是为了在统一构建框架里优雅容纳一个「可选但重要的」运行形态。

## 相关概念

- [002 Cython 编译流程](153-cython-compilation.md)：逐版本 Cython 产物
- [005 Wheel 分发包](155-wheel-distribution.md)：cp39-cp314t 构建矩阵
- [006 One Wheel 策略](156-one-wheel-strategy.md)：多版本下单一包入口
- [Python 自由线程](/09-python/concepts/123-freethreaded-python.md)：cp314t 的运行期语义