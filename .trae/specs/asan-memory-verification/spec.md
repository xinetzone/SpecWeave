# ASan 内存验证 Spec

## Why

[Task 17b](file:///d:/spaces/SpecWeave/.trae/specs/caffe-ffi-tvm-integration/tasks.md#L297-L307)「ASan内存管理验证」处于待开始状态：内存计数器已实现，但 ASan 正式验证需在 Linux/GCC 环境执行。当前缺少可复现的 ASan 测试用例、可通过 CMake 开关集成的编译选项，以及 ASan 报告堆栈的解读能力。本 Spec 补齐这三块前置能力，为 Task 17b 的正式验证奠定基础。

## What Changes

- 新增一个独立的 C++ ASan 演示测试用例（含内存泄漏 + 堆越界访问两类运行时错误），可用 `-fsanitize=address` 编译运行并验证 ASan 捕获。
- 在 caffe-ffi 的 CMake 模块化体系中新增 `CAFFE_FFI_ENABLE_ASAN` 编译选项，并在 `CompilerConfig.cmake` 的 `caffe_ffi_configure_target()` 中统一接入 ASan 编译/链接标志（GCC/Clang 用 `-fsanitize=address`，MSVC 用 `/fsanitize=address`）。
- 新增一份 ASan 报告堆栈解读文档，说明如何从 ASan 输出定位具体越界写入位置。

## Impact

- Affected specs: [caffe-ffi-tvm-integration](file:///d:/spaces/SpecWeave/.trae/specs/caffe-ffi-tvm-integration/tasks.md#L297-L307)（推进 Task 17b 前置）
- Affected code: [caffe-ffi](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi) 的 `cmake/Options.cmake`、`cmake/CompilerConfig.cmake`、`examples/`、`docs/`、`tests/cpp/`

## ADDED Requirements

### Requirement: ASan 演示测试用例
系统 SHALL 提供一份自包含的 C++ 演示用例，包含且仅包含两类可被 ASan 捕获的运行时错误：内存泄漏（`new` 后未 `delete`）和堆越界写入（访问数组越界索引）。

#### Scenario: 成功捕获内存泄漏
- **WHEN** 使用 `-fsanitize=address` 编译并运行演示用例
- **THEN** ASan 报告 `LeakSanitizer` 段，指出泄漏的分配点（`new` 所在行）

#### Scenario: 成功捕获堆越界写入
- **WHEN** 使用 `-fsanitize=address` 编译并运行演示用例
- **THEN** ASan 报告 `heap-buffer-overflow`，并给出越界写入的栈轨迹（含函数名、行号、越界偏移）

#### Scenario: 无 ASan 标志时行为
- **WHEN** 不使用 `-fsanitize=address` 编译
- **THEN** 演示用例可正常运行或仅产生未定义行为，不强制触发 ASan 报错

### Requirement: CMake ASan 编译选项
系统 SHALL 在 caffe-ffi 的 CMake 中新增 `CAFFE_FFI_ENABLE_ASAN` 布尔选项（默认 OFF），并在 `caffe_ffi_configure_target()` 内统一为目标追加 ASan 编译与链接标志。

#### Scenario: 启用 ASan
- **WHEN** `-DCAFFE_FFI_ENABLE_ASAN=ON` 配置并构建
- **THEN** 目标编译/链接标志包含 `-fsanitize=address`（GCC/Clang）或 `/fsanitize=address`（MSVC），构建日志输出 ASan 启用状态

#### Scenario: 默认不启用
- **WHEN** 未显式传入 `-DCAFFE_FFI_ENABLE_ASAN`
- **THEN** 默认 OFF，不污染既有构建行为

### Requirement: ASan 报告解读文档
系统 SHALL 提供一份 Markdown 文档，解释 ASan 报告的堆栈信息结构，并演示如何定位具体的越界写入位置。

#### Scenario: 阅读标准堆栈
- **WHEN** 读者查看 ASan 报告的 `WRITE of size N` 与 `#0 ... #N` 栈帧
- **THEN** 文档说明各栈帧含义（`#0` 为现场、`#N` 为调用链上层）、`0x...` 地址偏移、红区（redzone）概念，以及如何用 `addr2line`/`-g` 符号定位到源码行

## MODIFIED Requirements

（无）

## REMOVED Requirements

（无）