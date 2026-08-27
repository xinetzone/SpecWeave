---
type: Concept
title: "视角014：错误处理与异常安全"
description: "分析 TVM FFI 的错误处理模型：C ABI 错误码约定、TLS 错误对象传播、C++ 异常捕获与转换、跨语言异常映射，以及 SafeCall 包装器的异常安全保证。"
tags:
  - architecture
  - error-handling
  - exception-safety
  - tls
  - cross-language
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-101, F-102, F-103, F-104, F-341, F-342
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/error.h
    - include/tvm/ffi/function.h
---

# 视角014：错误处理与异常安全

## 概述

TVM FFI 需要在多种错误处理机制之间架起桥梁：C++ 使用异常、C 使用错误码、Python 使用异常、Rust 使用 `Result`。FFI 通过"错误码 + TLS 错误对象"的统一模型，在 C ABI 边界阻止异常传播，同时保留丰富的错误信息。本视角分析错误捕获、存储、传播和转换的完整流程。

## C ABI 错误模型

### 错误码约定

所有 C ABI 函数遵循统一的错误码约定：

- **返回 0**：成功。
- **返回非零（通常为 -1）**：发生错误。

错误码本身仅表示"有错误发生"，不携带错误详情。详细错误信息通过 TLS（线程局部存储）机制单独传递。

### 为什么不通过参数返回错误

TVM FFI 选择 TLS 输出错误信息而非输出参数，原因包括：

1. **签名简洁**：函数签名不需要额外的错误输出参数。
2. **链式调用**：中间层不需要在每个调用点检查和传递错误对象。
3. **与函数指针兼容**：`TVMFFISafeCallType` 的固定签名不需要为错误信息预留参数。

## TLS 错误对象机制

### 错误存储

线程局部存储维护一个当前错误对象：

- **`TVMFFIErrorMoveFromRaised`**（`c_api.h:754`）：从 TLS 中取出错误对象，将 TLS 清空。返回 `TVMFFIObjectHandle`（Error 对象的句柄），调用者获得所有权。
  ```c
  int TVMFFIErrorMoveFromRaised(TVMFFIObjectHandle* out_error);
  ```

- **`TVMFFIErrorSetRaised`**（`c_api.h:760`）：将错误对象放回 TLS，用于中间层捕获后继续向上传播。

- **`TVMFFIErrorSetRaisedFromCStr`**（`c_api.h:768`）：从 C 字符串设置错误（kind + message），用于纯 C 环境的简单错误报告。
- **`TVMFFIErrorSetRaisedFromCStrParts`**（`c_api.h:793`）：从多个字符串片段组装错误消息。
- **`TVMFFIErrorCreate`**（`c_api.h:809`）：创建错误对象，包含 kind、message 和可选的 cause/extra_context。

### Error 对象类型

错误对象的类型索引为 `kTVMFFIError = 67`，是标准的 FFI 对象：

- 继承自 `Object`，通过引用计数管理。
- 包含错误消息字符串、错误类型标识、可选的堆栈跟踪。
- C++ 层对应 `Error` 类（`error.h`），继承自 `ObjectRef` 和 `std::exception`。

### 错误类型层次

C++ 层定义了异常类层次：

- `Error`：所有 FFI 异常的基类。
- `InternalError`：内部断言失败。
- `ValueError`：参数值错误。
- `TypeError`：类型不匹配。
- `NotFoundError`：查找的资源不存在。
- `OSError`：操作系统相关错误。

这些异常类型通过不同的类型索引或错误类型字段区分，跨语言传播时映射为目标语言的对应异常类型。

## SafeCall 异常包装

### SafeCall 包装器

`TVMFFISafeCallType` 是跨语言调用的安全边界。每个通过 C++ 模板机制（如 `Function::FromPacked`）创建的函数，其 `safe_call` 指针指向一个自动生成的包装器：

```
用户函数（C++ lambda，可能抛异常）
    ↓ 调用
SafeCall 包装器
    ├── try { 调用用户函数 }
    ├── catch (const std::exception& e) {
    │     创建 Error 对象，存入 TLS
    │     return -1;
    │ }
    └── catch (...) {
          创建未知 Error 对象，存入 TLS
          return -1;
        }
```

### 异常安全保证

SafeCall 包装器提供以下保证：

1. **不泄漏异常**：所有 C++ 异常在 SafeCall 边界被捕获，不会传播到 C 调用栈。
2. **不泄漏资源**：用户函数中的 `Any`、`ObjectPtr` 等 RAII 类型在栈展开时正确析构。
3. **错误信息保留**：异常的 `what()` 消息被存入 Error 对象，跨语言可读。
4. **TLS 清理**：成功调用时 TLS 错误状态为空，避免上次错误的残留。

### CppCall 快速路径

对于 C++ 到 C++ 的内部调用，`cpp_call` 路径不捕获异常：

- 异常直接沿 C++ 调用栈传播。
- 避免了 try-catch 的代码体积和性能开销。
- 仅在 C++ 内部使用，不跨越语言边界。

`TVMFFIFunctionCall`（`c_api.h:746`）始终使用 `safe_call` 路径，确保 C ABI 安全。

## 跨语言错误传播流程

### C++ → Python

1. C++ 函数抛出异常（如 `ValueError`）。
2. SafeCall 捕获异常，创建 `Error` 对象存入 TLS，返回 -1。
3. Python 绑定的 ctypes/Cython 层检测到返回值 -1。
4. 调用 `TVMFFIErrorMoveFromRaised` 获取 `Error` 对象。
5. 将 Error 对象的消息和类型转换为 Python 异常（如 `TVMValueError`）。
6. 在 Python 中抛出异常。

### Python → C++

1. Python 函数抛出 Python 异常。
2. Python 绑定的函数包装器捕获 Python 异常。
3. 创建 FFI `Error` 对象，消息包含 Python 异常的 traceback。
4. SafeCall 将错误存入 TLS，返回 -1。
5. C++ 调用方检测到错误码，获取 Error 对象。
6. 抛出 C++ `Error` 异常（如果 C++ 调用方使用 `cpp_call` 路径）或返回错误码。

### Rust 错误处理

Rust 绑定将错误码 + TLS Error 转换为 `Result<T, Error>`：

- 调用 C ABI 函数后检查返回值。
- 非零时调用 `TVMFFIErrorMoveFromRaised`，将 Error 转换为 Rust `Error` 类型。
- 返回 `Err(Error)`，利用 Rust 的 `?` 运算符自然传播。

## 错误清理与资源安全

### RAII 与异常安全

C++ 层的 RAII 类型确保异常发生时资源正确释放：

- `ObjectPtr`：栈展开时析构，减少引用计数。
- `Any`：析构时释放持有的对象引用。
- `Optional<T>`： disengaged 状态不持有资源。

### 错误路径的内存管理

当 SafeCall 捕获异常时：

1. 用户函数的局部变量通过栈展开析构。
2. 参数 `PackedArgs` 中的 `AnyView` 是非持有视图，不需要清理。
3. 返回值 `TVMFFIAny* result` 在错误路径上不被写入（调用方不应读取）。
4. Error 对象通过 `make_object<ErrorObj>` 创建，由调用方（通过 `MoveFromRaised`）获得所有权。

## 错误信息丰富化

### 堆栈跟踪

C++ 层可以在异常中捕获堆栈跟踪（通过 `<stacktrace>` 或平台特定 API），存入 Error 对象。跨语言传播后，开发者可以看到完整的 C++ 调用栈，即使错误最终在 Python 中处理。

### 错误链

Error 对象可以包含"原因"（cause）字段，形成错误链。当一个错误由另一个错误引起时，保留原始错误信息，便于诊断。

### 结构化错误

除了消息字符串，错误可以携带结构化数据（通过 `Any` 字段），如错误码、文件名、行号、相关对象引用等。语言绑定可以根据结构化信息生成更友好的错误报告。

## NPU建议

在 NPU 运行时中，错误处理需要考虑以下特殊场景：

1. **NPU 硬件错误分类**：NPU 执行可能产生多种硬件错误：指令错误、内存越界、总线错误、超时、功耗异常、固件崩溃。建议为每种错误定义明确的 FFI 错误类型（如 `NPUInstructionError`、`NPUMemoryError`、`NPUTimeoutError`），继承自 FFI `Error`，携带 NPU 特定的错误码和寄存器状态。这些错误类型通过动态类型索引注册，不占用核心 ABI 的错误码空间。

2. **异步错误延迟报告**：NPU 异步执行时，硬件错误在算子函数返回后才可能发生（在流同步时检测）。建议：
   - 在 Stream 对象中维护"挂起的错误"状态。
   - 算子提交时不检测错误（命令仅写入缓冲区）。
   - 流同步时（通过 NPU 插件提供的同步全局函数）查询 NPU 错误状态寄存器，若有错误则通过 TLS 机制报告。
   - 同步后的第一个 FFI 调用应检查流的错误状态，避免错误被静默吞没。

3. **错误恢复策略**：NPU 硬件错误有些是可恢复的（如超时可重试），有些是不可恢复的（如固件崩溃需要重置设备）。建议 Error 对象携带"可恢复性"标记：
   - 可恢复错误：调用者可选择重试或降级执行。
   - 不可恢复错误：需要重置 NPU 设备或重新加载固件。建议提供 `npu.device_reset` 全局函数触发设备重置流程。

4. **固件崩溃诊断**：NPU 固件崩溃时可能产生 core dump 或崩溃日志。建议错误对象包含崩溃日志的路径或二进制数据（包装为 `Bytes` 对象），供上层诊断工具分析。在开发环境中，错误消息应包含 NPU 程序计数器（PC）、出错指令地址等调试信息。

5. **多流错误隔离**：多流并发执行时，一个流的错误不应影响其他流。建议每个 Stream 独立维护错误状态。`StreamSync` 仅报告该流的错误。设备级致命错误（如固件崩溃）影响所有流，应标记为设备级错误，所有流的同步都会返回该错误。

6. **错误与资源清理**：NPU 算子执行失败时，可能已部分修改输出缓冲区。错误处理流程应明确：
   - 失败算子的输出缓冲区内容未定义，调用者不应读取。
   - 已提交到流的后续命令应被清空（通过 NPU 的命令队列重置功能）。
   - StreamSync 失败后，流应处于"错误状态"，后续提交应被拒绝直到流被重置或销毁。

7. **主机端错误的 NPU 上下文**：当主机端检测到参数错误（如无效张量形状、不支持的数据类型）时，应在提交到 NPU 之前抛出 `ValueError`/`TypeError`，避免向 NPU 提交无效命令。建议在算子函数的参数校验阶段使用 FFI 标准异常类型，仅在 NPU 执行阶段产生的错误使用 NPU 特定错误类型。

## 设计分析

TVM FFI 的错误处理模型是"异常与错误码桥接"的经典设计。核心洞察是：C ABI 边界必须是异常安全的（不传播 C++ 异常），但完全丢弃异常信息会严重影响可调试性。TLS 错误对象机制在两者之间取得平衡：C ABI 接口保持简洁的整数返回值，同时通过线程局部存储传递完整的错误对象。

SafeCall 和 CppCall 的双路径设计也值得注意：它不强迫所有调用都承担异常处理开销，而是在安全边界处才付出代价。这种"快速路径+安全路径"的思想与内核态/用户态分离类似，在保证安全的前提下最大化了内部调用的性能。

## 相关概念

- [005 ABI 稳定性策略](005-abi-stability-strategy.md)：错误码作为 ABI 契约
- [011 跨语言边界设计](011-cross-language-boundary.md)：跨语言错误传播
- [012 异步流与设备管理](012-async-stream-device-management.md)：异步错误处理
- [007 核心数据结构](007-core-data-structures.md)：Error 作为对象类型
