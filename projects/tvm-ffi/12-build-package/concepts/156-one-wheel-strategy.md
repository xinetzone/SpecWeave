---
type: Concept
title: "视角156：One Wheel 策略"
description: "分析 tvm-ffi 的 One Wheel 分发策略，包括单一基础 Wheel、运行时库（RTLD_GLOBAL）与编译器库（RTLD_LOCAL）的拆分、runtime-only 模式与未知对象跳过机制。"
tags:
  - build
  - wheel
  - runtime-only
  - strategy
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-372
  - code:
    - python/tvm/base.py
    - python/tvm_ffi/registry.py
    - pyproject.toml
---

# 视角156：One Wheel 策略

## 概述

"One Wheel 策略"指的是 tvm-ffi 以**单一基础 Wheel** 交付运行时能力的打包思路：不按功能拆分成多个并行安装的 wheel，而是通过编译期 flag 与运行期模式开关，在同一 Wheel 内区分"完整版"与"runtime-only（运行时仅用）"两种装载路径。其核心机制由 `python/tvm/base.py` 中的库加载逻辑与 `tvm_ffi.registry._SKIP_UNKNOWN_OBJECTS` 标志位共同实现（事实 F-372）。

## 运行时库与编译器库拆分解读

```python
_LOADED_LIBS["tvm_runtime"] = load_lib_ctypes("tvm", "tvm_runtime", "RTLD_GLOBAL", ...)  # base.py:44-46
if not _RUNTIME_ONLY:
    try:
        _LOADED_LIBS["tvm_compiler"] = load_lib_ctypes("tvm", "tvm_compiler", "RTLD_LOCAL", ...)  # base.py:50-52
    except (RuntimeError, OSError):
        _RUNTIME_ONLY = True
if _RUNTIME_ONLY:
    from tvm_ffi import registry as _tvm_ffi_registry
    _tvm_ffi_registry._SKIP_UNKNOWN_OBJECTS = True  # base.py:58-61
```

`base.py:58-61`（事实 F-372）的关键在于：当 `_RUNTIME_ONLY=True`（由 `TVM_USE_RUNTIME_LIB=1` 环境变量触发，`base.py:33`）或编译器库加载失败导致回退时，会设置 `tvm_ffi.registry._SKIP_UNKNOWN_OBJECTS = True`。这表明 "One Wheel" 并非"一刀切少装模块"，而是**单包内动态降级**：同一 wheel 装上后，根据运行期条件自动进入"仅运行时"模式，并跳过对未知对象类型的严格校验。

`_LOADED_LIBS`（`base.py:39`）以 basename 为键记录实际加载的库，供 downstream/autoload 扩展检测以避免重复加载。

## 动态加载失败的回退

`base.py:48-56` 展示了 graceful degradation：`tvm_compiler` 加载失败（缺 LLVM 依赖、链接器问题）时捕获 `RuntimeError/OSError` 并置 `_RUNTIME_ONLY=True`。这意味着即便用户安装了完整 Wheel，也会在缺少特定依赖的运行时下自动退化为 runtime-only，不会因编译器库不可用而整体崩溃。这是 One Wheel 策略"一份产物覆盖多种运行期状态"的核心体现。

## _SKIP_UNKNOWN_OBJECTS 机制

`registry.py` 的 `_SKIP_UNKNOWN_OBJECTS` 标志（`python/tvm_ffi/registry.py`）用于控制对象注册与反序列化时的未知对象处理：为 True 时，遇到 FFI 在运行库中未注册的对象类型将跳过校验而非报错，从而容忍"运行库只内置了部分对象类型"的情况。这使 runtime-only 包（无编译器、对象种类较少）也能正常解析不涉及编译器 IR 的数据流。

## 与构建配置的关联

`pyproject.toml` 的 Wheel 只声明单一包 `python/tvm_ffi`（`pyproject.toml:146`），并不为 runtime-only 单独产出第二个包；模式差异完全由安装后的运行期环境（`TVM_USE_RUNTIME_LIB`、库是否存在）驱动。CMake 侧"非 Python 模块时不装静态库、共享库作为主产物"（`CMakeLists.txt:366-373`）也与"单 Wheel 内一物多用"的取向一致。

## 设计分析

One Wheel 策略在"安装复杂度"与"功能完整性"间取得平衡：用户永远只 `pip install` 一个包，功能差异通过运行期自适应实现。相对"拆分为多个可选 wheel（base full-npu 等）"的粒度方案，它牺牲了"按需最小安装"，却换取了统一的依赖图与安装入口，避免了包间版本冲突与元数据组合爆炸。其代价是需要 `_SKIP_UNKNOWN_OBJECTS` 这类降级语义来保证部分功能缺失时的可用性。

## NPU建议

针对 NPU 运行时复用 One Wheel 策略，建议：

1. **NPU 降级语义设计**：借鉴 `_SKIP_UNKNOWN_OBJECTS`，为 NPU 场景定义 `_SKIP_UNKNOWN_NPU_OBJECTS`；当 NPU 设备库缺失或驱动不可用时，让 FFI 结构数据（如 tensor/dict）正常解析但不执行 NPU 算子，实现"模型加载可用、算子运行降级"的优雅降级。

2. **设备探测作为降级开关**：建议把 NPU 能力探测（如存在 `npu_runtime.so`、是否检测到设备）纳入 `base.py` 的 `_RUNTIME_ONLY` 判定，形成"runtime-only / runtime+npu"多级回退，进一步收敛单 Wheel 内的运行期分支。

3. **符号加载顺序治理**：NPU 扩展若采用 RTLD_GLOBAL 以减少重复加载，应沿用 `_LOADED_LIBS` 按 basename 去重管理模式，防止多个 NPU 中间件重复加载 `tvm_ffi` 导致符号表膨胀或重复静态区。

4. **打包与回退标记联动**：将"NPU 模块是否存在"与 `[dependency-groups]` 的可分离（如 `pip install apache-tvm-ffi[npu]` 提供可选 NPU 依赖）结合，使单 Wheel 核心保持纯净、NPU 能力按需 add，同时用 `_SKIP_UNKNOWN_*` 保证缺少该可选能力时回退可用。

5. **测试兼容性矩阵**：在 CI 中分别覆盖"完整模式"与"runtime-only 模式"（`TVM_USE_RUNTIME_LIB=1`）两类测试，确保 One Wheel 的降级路径在 NPU 生态不被破坏。

## 相关概念

- [005 Wheel 分发包](155-wheel-distribution.md)：单 Wheel 的打包实现
- [004 共享库目标](154-shared-library-target.md)：_LOADED_LIBS 加载管理
- [008 依赖管理](158-dependency-management.md)：可选 NPU 依赖分组
- [003 Python 对象注册](/09-python/concepts/118-python-object-registration.md)：_SKIP_UNKNOWN_OBJECTS 的注册联动