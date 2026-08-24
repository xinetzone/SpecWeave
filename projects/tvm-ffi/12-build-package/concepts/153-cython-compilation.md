---
type: Concept
title: "视角153：Cython 编译流程"
description: "分析 tvm-ffi 的 Cython 扩展编译流程，包括 core.pyx 的定义、pxi 头文件拆分、cython --cplus 转译、python_add_library 构建与学习安装路径。"
tags:
  - build
  - cython
  - python
  - c-plus-plus
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-335, F-336, F-337
  - code:
    - python/tvm_ffi/cython/core.pyx
    - CMakeLists.txt
    - pyproject.toml
---

# 视角153：Cython 编译流程

## 概述

tvm-ffi 的 Python 绑定采用 Cython（而非 ctypes/cffi）封装底层 C ABI。Cython 构建流程在 CMake 侧由 `TVM_FFI_BUILD_PYTHON_MODULE` 选项触发，其核心是将 `core.pyx` 转译为 C++ 源，再编译为 Python 扩展模块。该流程是视角124 存根生成、视角118 Python 对象注册等运行时能力的构建前提。

## core.pyx 模块

`python/tvm_ffi/cython/core.pyx` 是 Cython 扩展入口。它在 `core.pyx:30` 定义扩展类 `PyAny`，包装底层 `TVMFFIAny`，并在 `core.pyx:50` 实现 `__int__`、`__float__`、`__bool__`、`__str__` 等 Python 协议方法（事实 F-335、F-336）。`core.pyx:140` 定义 `PyFunction`，包装 `TVMFFIFunctionHandle` 并实现 `__call__`（事实 F-337），从而把 C 层的函数句柄暴露为可调用的 Python 对象。

为控制规模，Cython 源码按领域拆分为多个 `.pxi` 包含文件：`base.pxi`、`type_info.pxi`、`device.pxi`、`dtype.pxi`、`error.pxi`、`function.pxi`、`pycallback.pxi`、`pyclass_type_converter.pxi`、`tensor.pxi`、`object.pxi`、`string.pxi`（`CMakeLists.txt:270-283`）。这些 `.pxi` 被 `add_custom_command` 列为 `DEPENDS`，任一文件变更即触发重新转译。

## 转译与编译

### 调用 cython 命令

CMake 通过 `add_custom_command`（`CMakeLists.txt:284-292`）执行：

```
python -m cython --cplus core.pyx -o core.cpp --module-name tvm_ffi.core
```

`--cplus` 指示 Cython 生成 C++ 版本代码，输出 `core.cpp` 到构建目录。命令依赖全部 `_cython_sources`。

### 构建扩展模块

随后 `python_add_library(tvm_ffi_cython MODULE "${_core_cpp}" WITH_SOABI)`（`CMakeLists.txt:297`）把转译出的 C++ 最终编译为 Python 扩展库，输出名为 `core`（`target_set_properties OUTPUT_NAME core`，`CMakeLists.txt:298`）。源码注释（`CMakeLists.txt:294-296`）说明：PyObject 绑定实现在 `tvm_ffi_python_object.h` 中使用了完整 Python C API（`Py_IncRef`、`PyObject_GC_Del` 等），因此必须针对**逐版本 ABI** 构建，而不能用 limited/abi3 ABI——这与 `WITH_SOABI` 参数和 pyproject 中逐版本 Wheel 标签（cp312-cp312 而非 cp312-abi3）互相印证。

## 链接与运行时定位

扩展模块 `tvm_ffi_cython` 链接 `tvm_ffi_header`（头文件）、`tvm_ffi_shared`（动态库）、`tvm_ffi_testing`（确保卸载顺序 cython 先于测试库）（`CMakeLists.txt:303-307`）。为让运行时能找到动态库，Apple 与 Unix 分别设置 `@loader_path/lib` 与 `$ORIGIN/lib` 的 RPATH（`CMakeLists.txt:309-315`），Windows 则在加载层用 `os.add_dll_directory` 解决。

`python_add_library` 之前，CMake 会以 `Python ${_tvm_ffi_python_version} EXACT` 方式查找精确版本的解释器与开发模块（`CMakeLists.txt:262-267`），保证构建针对的目标 Python 版本与解释器一致。

## 与构建后端的衔接

当通过 `scikit-build-core` 构建时，pyproject 的 `cmake.args` 声明 `-DTVM_FFI_BUILD_PYTHON_MODULE=ON`（`pyproject.toml:139`），从而激活上述整个 Cython 路径；同时 `build-system.requires` 中的 `cython>=3.2.8` 保证生成 `core.cpp` 的 Cython 版本符合自由线程 Python 的 dealloc 修复要求（见视角152）。

## 设计分析

tvm-ffi 把 Cython 转译纳入 CMake `add_custom_command`，使转译成为构建图中的一个可被 `DEPENDS` 追踪的节点，从而获得增量构建与并行构建能力；`.pxi` 拆分让源码按领域解耦、降低单文件复杂度。逐版本 ABI（而非 abi3）的取舍牺牲了跨版本复用，却换取了对接自由线程等新特性的灵活性与完整 Python C API 访问能力，是为性能与特性优先于 wheel 体积比例的明确权衡。

## 扩展讨论

### Cython 一键同时满足速度与开发体验

相比纯 ctypes/cffi 的"运行期动态加载、运行时解析签名"，Cython 在**编译期**就把 `core.pyx` 转译为 C++，使 Python 协议方法（`__int__`、`__call__`）与 C 层 `TVMFFIAny`/句柄形成静态、类型已知的映射。收益是调用路径跳过 ctypes 的类型装箱/拆箱开销，接近原生 C++ 函数调用的性能；代价是需要维护一条"pyx→cpp→so"的转译链（由 CMake `add_custom_command` 承载），比 ctypes 的纯声明方式更重。tvm-ffi 在"每个调用都可能是紧循环内热路径"的 FFI 场景选择前者，是性能优先的必然。

### `.pxi` 按领域拆分是一种"编译期模块化"

`base/type_info/device/dtype/error/function/pycallback/tensor/object/string` 等 `.pxi` 把庞大的绑定按语义域切分，既有文档上的可读性收益（每段聚焦一类对象），又有工程收益：`add_custom_command` 把它们全部列为 `DEPENDS`，**改任一 `.pxi` 即触发重新转译**，避免了"大泥球 pyx 改动一处就要全量重转"的低效。这与源码侧 `include/` 的头文件拆分思想一致——把"转译单元"作为增量构建的最小粒度。

### 专项目标链保证卸载顺序

`tvm_ffi_cython` 显式链接 `tvm_ffi_testing`（`CMakeLists.txt:303-307`）服务于卸载顺序：测试库须在 Cython 模块之后释放，防止共享库先于使用方被卸载导致悬空符号。这类"链接目标即资源生命周期声明"的做法，把在多数语言里靠静态析构顺序/引用计数才能表达的约束，提前到构建期用目标依赖固定下来，减少了运行期资源释放的竞争窗口。

## 相关概念

- [007 Python 打包 wheel](155-wheel-distribution.md)：逐版本 ABI 与 Wheel 标签
- [006 One Wheel 策略](156-one-wheel-strategy.md)：Cython 模块随 Wheel 分发
- [存根生成 stubgen](/07-reflection/concepts/100-stubgen.md)：core.pyx 的类型存根联动
- [实现细节 内联优化](/08-cpp-impl/concepts/105-inline-optimization.md)：Cython 产物与内联的衔接