---
type: Concept
title: "视角169：跨平台测试"
description: "分析 TVM FFI 在 x86_64、aarch64、ARM64 macOS、Windows AMD64 四个平台的测试策略，包括构建差异、平台特定代码路径、以及自由线程 Python 的支持。"
tags:
  - testing
  - cross-platform
  - ci-cd
  - windows
  - arm
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-295, F-376
  - code:
    - .github/workflows/ci_test.yml
    - src/ffi/backtrace_win.cc
    - src/ffi/backtrace.cc
    - tests/cpp/test_abi_object.cc
---

# 视角169：跨平台测试

## 概述

TVM FFI 的测试覆盖四个主要平台组合：Linux x86_64、Linux aarch64、macOS ARM64、Windows AMD64。每个平台的构建工具链、运行时环境和平台特定代码路径不同，测试策略需要确保功能一致性。

## 平台矩阵

CI 测试矩阵定义在 `ci_test.yml`：

| 平台 | OS | 架构 | Python 版本 | Shell |
|------|-----|------|----------|-------|
| 1 | ubuntu-latest | x86_64 | 3.14t（自由线程） | bash |
| 2 | ubuntu-24.04-arm | aarch64 | 3.14 | bash |
| 3 | windows-latest | AMD64 | 3.9 | cmd/pwsh |
| 4 | macos-14 | arm64 | 3.13 | bash |

### Python 版本差异

- **Linux x86_64**：使用 Python 3.14t（自由线程模式），验证 `--disable-gil` 下的 FFI 行为。
- **Linux aarch64**：使用标准 Python 3.14。
- **Windows**：使用 Python 3.9（MSVC 兼容要求）。
- **macOS**：使用 Python 3.13。

版本差异主要受限于各平台的 toolchain 兼容性和 CI 代理的 Python 可用性。

## 构建差异

### C++ 测试构建

**Linux/macOS**：
```bash
cmake . -B build_test -DTVM_FFI_BUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build_test --clean-first --config Debug --target tvm_ffi_tests
ctest -V -C Debug --test-dir build_test --output-on-failure
```

**Windows**：
```cmd
cmake . -B build_test -DTVM_FFI_BUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build_test --clean-first --config Debug --target tvm_ffi_tests
ctest -V -C Debug --test-dir build_test --output-on-failure
```

Windows 需要先通过 `locate_vsdevcmd_bat.py` 定位 Visual Studio 的 `VsDevCmd.bat`，设置编译器环境变量后执行 CMake 配置。

### 地址 Sanitizer

C++ 测试在构建时启用地址 Sanitizer（`add_sanitizer_address(tvm_ffi_tests)`）。ASan 在 Linux 和 macOS 上原生支持，Windows 上通过 MSVC 的 `/GS` 和 `/RTC1` 提供类似的运行时检查。

## 平台特定代码路径

### 回溯捕获

```cpp
// src/ffi/backtrace.cc（POSIX）
#include <execinfo.h>
const TVMFFIByteArray* TVMFFIBacktrace(const char* filename, int lineno, const char* func, int32_t num_skip) {
  void* buffer[100];
  int nptrs = backtrace(buffer, 100);
  char** symbols = backtrace_symbols(buffer, nptrs);
  // ...
}

// src/ffi/backtrace_win.cc（Windows）
#include <windows.h>
#include <dbghelp.h>
const TVMFFIByteArray* TVMFFIBacktrace(const char* filename, int lineno, const char* func, int32_t num_skip) {
  PVOID buffer[100];
  USHORT nptrs = CaptureStackBackTrace(0, 100, buffer, NULL);
  // ...
}
```

测试通过 `test_error.cc` 中的 `Error/Backtrace` 用例验证两种实现的行为一致性：回溯字符串中包含函数名和行号信息。

### DLL 导出宏

```cpp
// include/tvm/runtime/base.h
#ifdef _WIN32
  #define TVM_DLL __declspec(dllexport)
  #define TVM_RUNTIME_DLL __declspec(dllexport)
#else
  #define TVM_DLL __attribute__((visibility("default")))
  #define TVM_RUNTIME_DLL __attribute__((visibility("default")))
#endif
```

Windows 使用 `__declspec(dllexport/import)`，POSIX 使用 `-fvisibility=hidden` + `__attribute__`。测试通过 `test_abi_object.cc` 验证 DLL 导出对象的正确性。

## Python 测试差异

### Windows 特殊处理

```yaml
- name: Run python tests [windows]
  if: ${{ matrix.os == 'windows-latest' }}
  shell: cmd
  run: |
    call "%VS_DEV_CMD_PATH%"
    pytest -vvs tests/python
```

Windows 使用 `cmd` shell 而非 bash，需要先调用 Visual Studio 编译器环境脚本。

### 自由线程 Python

Linux x86_64 使用 Python 3.14t（自由线程/无 GIL 版本）：
```yaml
- {os: ubuntu-latest, arch: x86_64, python_version: '3.14t'}
```

验证 FFI 在 `--disable-gil` 模式下的行为，确保线程安全设计（引用计数的原子操作、TLS 错误状态等）在无 GIL 环境下正确工作。

## ABI 稳定性测试

`test_abi_object.cc` 验证 C ABI 层面的对象布局稳定性：

```cpp
TEST(ABITest, ObjectHeaderSize) {
  // 验证 TVMFFIObject 头部的固定大小
  EXPECT_EQ(sizeof(TVMFFIObject), EXPECTED_SIZE);
}

TEST(ABITest, AnyLayout) {
  // 验证 TVMFFIAny 联合体的大小和对齐
  EXPECT_EQ(sizeof(TVMFFIAny), 16u);
  static_assert(std::is_standard_layout_v<TVMFFIAny>);
}
```

这些测试确保 C ABI 在不同平台和编译器下保持一致，是跨平台互操作的基础。

## 覆盖缺口

| 场景 | 当前覆盖 | 建议改进 |
|------|---------|---------|
| Python 3.14 自由线程 | ✅ Linux x86_64 | 扩展到其他平台 |
| aarch64 Python 测试 | ✅ | 已有 |
| Windows ASan | ⚠️ 使用 /RTC1 替代 | 考虑启用 moreca 或 /fsanitize=address |
| macOS x86_64 | ❌ 仅有 arm64 | 可考虑添加 |
| Python 3.12 覆盖 | ❌ | CI 矩阵缺少 3.12 |

## 设计分析

跨平台测试策略的核心原则是"差异化配置、统一验证"：

1. **构建差异最小化**：通过 CMake 条件编译和平台特定的 action 处理构建差异，测试代码本身尽量平台无关。
2. **Python 版本矩阵**：覆盖从 3.9 到 3.14t 的版本跨度，确保向前兼容性和对新特性的支持。
3. **自由线程验证**：3.14t 的加入标志着对 Python 未来无 GIL 版本的预适配，这是 TVM FFI 作为高性能 FFI 库的必要能力。
4. **ABI 稳定性**：跨平台的一致性通过静态断言和运行时大小检查双重保障。

## 扩展讨论

### 四个平台覆盖的本质：每对「架构×工具链」至少验一遍

矩阵刻意挑选 Linux x86_64、Linux aarch64、macOS ARM64、Windows AMD64 四个组合，使每一种主流「CPU 架构 × 工具链」至少覆盖一次：x86 与 ARM 两个指令集、GCC/Clang 与 MSVC 两类编译器。测试策略因此不是"越多越好"，而是**用最少平台交换出最大的组合多样性**——每一对差异都能暴露一类可能的移植缺陷（如字节序、后端 ABI、`__declspec` 与 `__attribute__` 分支），从而以一当多地支撑跨平台可移植性声明。

### 自由线程 Python 的定点适配：3.14t 只放在一个平台

Linux x86_64 单独使用 Python 3.14t（自由线程、无 GIL），其余平台各用标准版本。这是一种**代价可控的预适配**：自由线程是 FFI 正确性的"高压区"——引用计数需原子化、线程局部（TLS）错误状态、共享状态加锁等，在 `--disable-gil` 下任何一个非线程安全假设都可能变成竞态崩溃。因为这类问题与平台强相关且难以全矩阵放大，先用一个代表性平台钉住形态、验证 FFI 的线程安全设计，是为未来全版本推广建立可信起点的务实选择。

### ABI 稳定性测试：跨平台互操作的地基

`test_abi_object.cc` 用 `static_assert` 与运行时 `EXPECT_EQ(sizeof(...))` 双重手段校验 `TVMFFIObject` 头部大小与 `TVMFFIAny` 的对齐（固定 16 字节、标准布局）。这类测试不验证"功能"，而验证"二进制契约在跨平台/跨编译器下不漂移"——正是多个平台各自编出的分支库能与统一头部结构互操作的根因。没有这一类地基性断言，其余功能测试即便全绿，也会在真正的跨库二进制互操作时因布局差异而崩溃。

## 相关概念

- [168 CI/CD 流水线](168-ci-cd-pipeline.md)
- [170 代码检查与格式化](170-code-check-formatting.md)
- [005 ABI 稳定性策略](/01-architecture/concepts/005-abi-stability-strategy.md)
