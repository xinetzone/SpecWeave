---
type: Concept
title: "视角160：构建配置选项"
description: "分析 tvm-ffi 的构建配置选项体系，包括 CMake 特性开关、pyproject scikit-build 参数、TVM 版本宏覆盖与运行期降级开关的组合与联动。"
tags:
  - build
  - configuration
  - cmake
  - options
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-372, F-377
  - code:
    - CMakeLists.txt
    - pyproject.toml
    - include/tvm/runtime/base.h
    - python/tvm/base.py
---

# 视角160：构建配置选项

## 概述

tvm-ffi 的构建配置选项横跨 CMake、pyproject 与运行期三处，分别控制"编译什么、打包什么、运行期降级与否"。它们通过 `option`/`cmake.args`/环境变量共同构成一个可裁剪、可组合的构建矩阵。本视角梳理这些选项的分布、取值与组合对最终产物的影响。

## CMake 层配置选项

`CMakeLists.txt` 通过 `option` 暴露原生编译开关（沿用视角151 列表）：

| 选项 | 默认 | 决策作用 |
|------|------|---------|
| `TVM_FFI_USE_LIBBACKTRACE` | ON | 是否纳入栈回溯能力 |
| `TVM_FFI_USE_EXTRA_CXX_API` | ON | 是否纳入 src/ffi/extra 扩展 API |
| `TVM_FFI_USE_THREADS` | ON | 是否链接线程库 |
| `TVM_FFI_USE_DL_LIBS` | ON | 是否链接 dl 库 |
| `TVM_FFI_BACKTRACE_ON_SEGFAULT` | ON | 段错误 signal handler |
| `TVM_FFI_BUILD_TESTS` | OFF | 是否构建测试目标 |
| `TVM_FFI_ATTACH_DEBUG_SYMBOLS` | OFF | Release 下附加调试符号 |
| `TVM_FFI_BUILD_PYTHON_MODULE` | OFF | 是否构建 Cython Python 模块 |

`option` 全部集中在文件上部（`CMakeLists.txt:22-26` 与 `204-205`、`233`），下游可在 configure 期统一覆写。

## pyproject 层配置

`[tool.scikit-build]` 通过 `cmake.args` 固定三条构建时的 CMake 覆写（`pyproject.toml:136-140`）：

```
-DTVM_FFI_ATTACH_DEBUG_SYMBOLS=ON
-DTVM_FFI_BUILD_TESTS=OFF
-DTVM_FFI_BUILD_PYTHON_MODULE=ON
```

这组参数是"Wheel 构建的黄金配置"：开调试符号、关测试、开 Python 模块（触发 Cython 编译链）。配套 `cmake.build-type = "Release"`（`pyproject.toml:135`）、`build-dir = "build"`（`pyproject.toml:127`），形成声明式的构建矩阵入口。用户不改 CMake 也能一键构建，构建参数集中声明在 pyproject。

## 版本宏与运行期降级开关

### TVM 版本宏

`include/tvm/runtime/base.h:34-36`：`TVM_VERSION` 默认为 `"0.26.dev0"`，可通过 `-DTVM_VERSION` 覆盖（事实 F-377）。这是源码树/打包运行时识别版本、做兼容经验判断的编译期配置。

### 运行期降级开关

`python/tvm/base.py:33`：`_RUNTIME_ONLY = os.environ.get("TVM_USE_RUNTIME_LIB") == "1"`，通过环境变量注入"运行时仅用"模式；`base.py:58-61` 在 `_RUNTIME_ONLY` 下设置 `tvm_ffi.registry._SKIP_UNKNOWN_OBJECTS = True`（事实 F-372）。这构成一组运行期降级配置，与编译期 option 形成"编译期裁剪 + 运行期降级"两个维度的配置面。

## 配置组合与联动

三类配置形成闭环：

1. **CMake option** 决定是否编译某些源文件/链接某些库（如 `TVM_FFI_USE_EXTRA_CXX_API` 控制 extra 源）。
2. **pyproject cmake.args** 在打包时强制定向这些 option，屏蔽顶层项目时对测试/静态库的默认行为（`CMakeLists.txt:366-373`）。
3. **环境变量/运行时 flag** 在产物已固定后决定运行期是否降级（runtime-only）与是否跳过未知对象。

三者耦合实现"同一套 CMake 源码，经不同配置产出开发库、测试库、Wheel 包、runtime-only 姿态"的多种形态。

## 设计分析

tvm-ffi 的构建配置"分层收敛"：把最细粒度的编译决策留在 CMake `option`，把"给用户/CI 的一键入口"收敛到 pyproject `cmake.args`，把只能在运行期判定的切换（如设备能力、依赖缺失）交由环境变量与 registry flag。这种分层避免了"配置越多越混乱"——每层只暴露该层能决策的维度，上层要么忽略要么定向覆写下层。`TVM_VERSION` 覆盖与 `_SKIP_UNKNOWN_OBJECTS` 则分别保证"版本可控"与"能力降级可控"。

## 扩展讨论

### "三层开关"为何不可合并为一层

编译期 `option`、打包期 `cmake.args`、运行期环境变量三者**判定时机不同、决策主体不同**：前两者在产物生成前决定"是否编译某能力"（改动需重新构建），后者在产物已固定后决定"是否使用某能力"（零成本切换）。若强行合并为单一配置面，就会在一个开关里混淆"能不能编"与"要不要用"两个语义——例如 runtime-only 降级必须在 Wheel 已打包后依目标环境才能判定，编译期根本无从预知。分层因此不是冗余，而是各配置维度信息可用时刻的自然投影。

### 默认值即"最小可用基线"

`option` 默认值（`TVM_FFI_USE_THREADS=ON`、`TVM_FFI_BACKTRACE_ON_SEGFAULT=ON` 等）定义了"不加任何参数就能得到一个功能完整的 FFI"的基线；而 pyproject 的 `cmake.args` 在此基础上定向覆开调试符号与 Python 模块。这使"一键构建"与"深度裁剪"共用同一份 CMake，唯一区别是覆写配置的多少。默认值的选择决定了用户体验的下限，也是判断某能力是否"默认值得引入"的场所。

### 组合全矩阵 vs 每形态一配置

同一份 CMake 源码经不同配置可产出"开发库、测试库、Wheel 包、runtime-only 姿态"四种形态。刻意不做成"每种形态一个独立参数"，而是让它们共享同一组 `option`、仅以取值组合区分，换取维护单点——新增能力只需在一个 `option` 上扩展，而不必在 N 个形态配置里重复声明。代价是"某形态误配置了不该开的能力"的检查更难预设，故依赖声明式清单（如 pyproject 的定向参数）约束常见形态。

## 相关概念

- [001 CMake 构建系统](151-cmake-build-system.md)：option 的原生定义
- [002 pyproject.toml 构建](152-pyproject-toml-build.md)：[tool.scikit-build] 的定向参数
- [006 One Wheel 策略](156-one-wheel-strategy.md)：运行期降级开关
- [版本演进与兼容性](/01-architecture/concepts/015-version-evolution-compatibility.md)：TVM_VERSION 版本的兼容职责