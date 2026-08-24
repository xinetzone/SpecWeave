---
type: Concept
title: "视角154：共享库目标"
description: "分析 tvm-ffi 的共享库目标设计，包括 libtvm_ffi 的 CMake 产物、ctypes 探测机制、库路径搜索顺序与 RTLD_GLOBAL/RTLD_LOCAL 加载模式。"
tags:
  - build
  - shared-library
  - ctypes
  - dll
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-331, F-370, F-371
  - code:
    - python/tvm_ffi/libinfo.py
    - python/tvm_ffi/_ffi_api.py
    - python/tvm/base.py
    - CMakeLists.txt
---

# 视角154：共享库目标

## 概述

共享库目标是 tvm-ffi 在 C ABI 与各语言绑定之间的"桥梁物"。CMake 侧由对象库派生 `tvm_ffi_shared`（Linux 下生成 `libtvm_ffi.so`），Python 侧通过 ctypes 在运行期按平台规则探测并加载该动态库，最终以全局注册表暴露 C 函数。本节聚焦共享库目标如何被定义、定位与加载，这是跨语言复用 FFI 能力的基础设施。

## CMake 侧产物定义

`tvm_ffi_add_target_from_obj(tvm_ffi tvm_ffi_objs)`（`CMakeLists.txt:131`）由对象库派生命名目标 `tvm_ffi`，随后 `tvm_ffi_hide_static_linked_lib_symbols(tvm_ffi_shared)` 隐藏静态链接符号（`CMakeLists.txt:132`），分别形成共享库 `tvm_ffi_shared` 与静态库 `tvm_ffi_static`。共享库的可见符号由 `CXX_VISIBILITY_PRESET hidden` + 显式 `TVM_FFI_DLL_EXPORT` 宏（见视角代码）精确控制（`CMakeLists.txt:106-107`），保证导出面符合 C ABI 契约。

安装规则将 `tvm_ffi_shared` 安装到 `lib/`（`CMakeLists.txt:347`），选择让共享库成为分发主产物，而静态库仅在非 Python 模块构建时安装（`CMakeLists.txt:366-373`），这为后续 Wheel 分发把动态库打进包内做了铺垫。

## Python 侧加载

### 平台命名规则

`libinfo.py` 的 `_find_library_by_basename`（`python/tvm_ffi/libinfo.py:228`）按平台推导动态库名：

- Windows：`tvm_ffi.dll`
- macOS：优先 `libtvm_ffi.dylib`，回退 `.so`
- Linux/FreeBSD 等：`libtvm_ffi.so`

### 库路径搜索顺序

`load_lib_ctypes`（`python/tvm_ffi/libinfo.py:148`）通过 `_find_library_by_basename` 按如下顺序搜索：

1. **importlib.metadata 的 RECORD**（`libinfo.py:280-295`）：从已安装 distribution 的 `RECORD` 文件里精确匹配动态库路径，这是 Wheel 场景最可靠的方式。
2. **调用方提供的 extra_lib_paths**（`libinfo.py:304-305`）：外部调用方（如 `tvm` 包）可指向自身构建树。
3. **内置自锚定回退**：`build/lib`、`lib`（`libinfo.py:308-315`）。
4. **环境变量派生**：Windows 用 `PATH`，macOS 用 `DYLD_LIBRARY_PATH`+`PATH`，Linux/FreeBSD 用 `LD_LIBRARY_PATH`+`PATH`（`libinfo.py:318-325`）。

这一多层搜索确保了源码开发模式（CMake+Make 构建，产物在 `build/lib`）与 Wheel 安装模式（产物在包 RECORD 中）都能正确定位共享库。

### 加载与 DLL 目录

```python
def load_lib_ctypes(package, target_name, mode, extra_lib_paths=None):
    lib_path = _find_library_by_basename(package, target_name, extra_lib_paths)
    if sys.platform.startswith("win32"):
        os.add_dll_directory(str(lib_path.parent))
    return ctypes.CDLL(str(lib_path), getattr(ctypes, mode))
```

`libinfo.py:148-183`：Windows 下先 `os.add_dll_directory` 显式登记 DLL 目录，再 `ctypes.CDLL(lib_path, mode)` 加载，`mode` 取 `RTLD_GLOBAL` 或 `RTLD_LOCAL`。

## RTLD_GLOBAL 与 RTLD_LOCAL 的运用

`python/tvm/base.py` 展示了两种模式的使用场景（事实 F-370、F-371）：

```python
_LOADED_LIBS["tvm_runtime"] = load_lib_ctypes("tvm", "tvm_runtime", "RTLD_GLOBAL", ...)  # base.py:44-46
_LOADED_LIBS["tvm_compiler"] = load_lib_ctypes("tvm", "tvm_compiler", "RTLD_LOCAL", ...)  # base.py:50-52
```

- **RTLD_GLOBAL**：用于将被后续加载的其他库依赖的符号暴露到全局符号表，保证跨库符号解析。
- **RTLD_LOCAL**：用于不向后传播符号的库，隔离符号冲突、减小污染。

`tvm_runtime`（含 `tvm_ffi`）以 GLOBAL 加载，使其符号可被后续 `tvm_compiler` 等扩展使用；扩展库以 LOCAL 加载，避免污染全局符号空间。

## 设计分析

共享库目标的设计核心是"一次编译、多方定位、按需符号可见"。CMake 的 PIC 与符号隐藏保证产物可被 `dlopen`/`LoadLibrary` 安全加载；Python 的多层路径探测兼顾开发态与安装态；RTLD 模式的选择在"符号共享"（GLOBAL）与"隔离最优"（LOCAL）之间做出按库粒度的权衡。这种设计让同一动态库既能服务当前进程内绑定，也能被 Rust 经 build.rs 定位复用。

## NPU建议

针对 NPU（神经网络处理单元）运行时集成 tvm-ffi 共享库目标，建议：

1. **NPU 运行时符号全局化**：NPU 设备驱动或专有运行时扩展若依赖 `tvm_ffi` 符号，应以 `RTLD_GLOBAL` 加载；建议与 `tvm_runtime` 同级，确保后续加载的 NPU 模块在全局符号表中解析到 FFI 入口。但需评估 GLOBAL 导致的符号覆盖风险，必要时为 NPU 扩展单独建立命名空间前缀。

2. **跨框架互操作路径优先**：NPU 前端常作为 `tvm` 的 downstream，应利用 `libinfo.load_lib_ctypes` 的 `extra_lib_paths` 参数把 NPU 构建产物目录前置，避免依赖 NPU 实现自带的路径猜测；建议在 NPU 打包流程中复用 `RECORD` 探测机制以提高定位确定性。

3. **Windows DLL 目录管理**：在 Windows 上部署 NPU 端（如设备动态库 + tvm_ffi.dll）时，应统一调用 `os.add_dll_directory` 登记 NPU 库目录；建议在 NPU 的 autoload 入口集中管理 DLL 目录集合，避免与 `libtvm_ffi.dll` 的加载目录冲突。

4. **加载顺序与符号隐藏**：NPU 自定义算子扩展应以 `RTLD_LOCAL` 加载，与 `tvm_compiler` 对齐，保证设备厂商符号不泄漏进全局命名空间；同时对 NPU 扩展同样启用符号隐藏（hidden），仅暴露注册入口，符合 C ABI 最小导出面原则。

5. **版本与能力协商**：在共享库加载完成（`_LOADED_LIBS` 就绪）后，建议 NPU 集成层显式调用 `find_libtvm_ffi()` 并校验版本（可经 `TVMFFIGetVersion`），以运行时位点避免与固件/驱动版本不匹配导致的 ABI 偏移。

## 相关概念

- [001 CMake 构建系统](151-cmake-build-system.md)：共享库目标的上游定义
- [006 One Wheel 策略](156-one-wheel-strategy.md)：共享库随 Wheel 分发到 `python/tvm_ffi`
- [004 版本查询 API](/11-c-abi-platform/concepts/150-version-query-api.md)：运行期版本协商
- [003 ABI 稳定性保证](/11-c-abi-platform/concepts/141-c-abi-stability-guarantee.md)：共享库符号契约