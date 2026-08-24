---
type: Concept
title: "视角015：版本演进与兼容性"
description: "分析 TVM FFI 的版本管理策略：语义化版本号、ABI 版本检查、编译时与运行时版本协商、废弃策略、结构体演进规则，以及 TVM 运行时对 FFI 版本的依赖管理。"
tags:
  - architecture
  - versioning
  - compatibility
  - deprecation
  - evolution
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-099, F-100, F-101, F-102, F-103, F-104
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/tvm_ffi.h
    - include/tvm/runtime/base.h
---

# 视角015：版本演进与兼容性

## 概述

作为跨语言基础设施库，TVM FFI 需要在持续演进的同时保持向后兼容性。本视角分析 TVM FFI 的版本管理策略，包括语义化版本号的构成、ABI 版本检查机制、编译时与运行时版本协商、API 废弃流程、结构体演进规则，以及 TVM 运行时对 FFI 版本的依赖约束。

## 版本号体系

### TVMFFIVersion 结构

`TVMFFIVersion` 结构体定义在 `c_api.h:83-90`：

```c
typedef struct {
  uint32_t major;
  uint32_t minor;
  uint32_t patch;
} TVMFFIVersion;
```

三个字段分别承担不同的兼容性语义：

| 字段 | 递增条件 | 兼容性含义 |
|------|---------|-----------|
| `major` | 不兼容的 API 变更 | 可能包含 ABI 或源码不兼容变更 |
| `minor` | 向后兼容的功能新增 | 旧代码可以直接使用新版本 |
| `patch` | 向后兼容的问题修复 | 仅修复缺陷，不新增功能 |

### 编译时版本宏

头文件定义了对应的编译时常量（`c_api.h:69-73`）：

- `TVM_FFI_VERSION_MAJOR`：编译时主版本号（当前为 0）。
- `TVM_FFI_VERSION_MINOR`：编译时次版本号（当前为 1）。
- `TVM_FFI_VERSION_PATCH`：编译时补丁版本号（当前为 14）。

绑定层在编译时可以通过预处理指令检查这些宏，条件编译依赖特定版本的代码。

### 运行时版本查询

`TVMFFIGetVersion`（`c_api.h:546`）是版本查询的唯一入口：

```c
void TVMFFIGetVersion(TVMFFIVersion* out_version);
```

动态加载 FFI 共享库后（如通过 `dlopen`），调用者应首先调用此函数获取运行时版本，与编译时版本比对，确认 major 版本兼容后再使用其他 API。

## ABI 兼容性策略

### ABI 稳定的内容

以下内容构成 ABI 契约，在同一 `abi_version` 内保持稳定：

1. **C 函数签名**：公共函数的名称、参数类型、返回类型、调用约定。
2. **结构体布局**：`TVMFFIAny`、`TVMFFIObject`、`TVMFFIFunctionCell`、`TVMFFIVersion` 的字段顺序、类型、大小和对齐。
3. **枚举值**：`TVMFFITypeIndex` 中已分配的类型索引值不变。
4. **函数指针签名**：`TVMFFISafeCallType`、`TVMFFIFunctionCell::cpp_call`、`TVMFFIObject::deleter` 的签名。
5. **错误码语义**：0 表示成功，非零表示错误。

### ABI 允许的变更

在不递增 `abi_version` 的前提下，允许以下变更：

1. **新增函数**：在 C ABI 中添加新的公共函数。
2. **新增类型索引**：在静态区 [0, 128) 的未分配位置添加新类型，或在动态区注册新类型。
3. **新增枚举值**：在现有枚举的末尾添加新值（不改变已有值）。
4. **函数行为增强**：函数可以接受新的输入组合（如新的标志位），但已有输入的行为不变。
5. **性能优化**：内部实现优化，不改变可观察行为。

### ABI 破坏性变更

以下变更必须递增 `abi_version`：

1. **删除或重命名公共函数**。
2. **修改函数签名**（参数类型、参数数量、返回类型）。
3. **修改结构体布局**（字段顺序、类型、大小）。
4. **改变已有枚举值的数值**。
5. **改变错误码的语义**。

## 结构体演进规则

### 尾部扩展原则

当需要向现有结构体添加字段时，遵循"仅尾部扩展"原则：

- 新字段添加在结构体末尾。
- 旧代码读取前 N 个字段，忽略新增字段。
- 新代码检查结构体大小（如果有 size 字段）或版本号，决定是否访问新字段。

例如，如果未来需要扩展 `TVMFFIVersion`，新字段将添加在 `minor` 之后：

```c
// 演进后（假设）
typedef struct {
  int32_t abi_version;
  int32_t major;
  int32_t minor;
  int32_t patch;       // 新增
  const char* git_hash; // 新增
} TVMFFIVersion;
```

旧代码传入的 `sizeof(TVMFFIVersion)` 较小，新代码应能处理部分填充的情况。

### 不透明句柄的自由度

使用不透明句柄（`void*`）的类型（如 `TVMFFIObjectHandle`、`TVMFFIModuleHandle`、`TVMFFIStreamHandle`）在 ABI 层面完全隐藏内部结构，因此可以自由演进：

- 添加、删除或重排内部字段。
- 改变内部数据结构。
- 使用不同的内存分配策略。

只要通过句柄访问的公共函数签名不变，句柄指向的内部结构可以任意修改。

## API 废弃策略

### 废弃标记

当公共 API 需要被移除时，遵循以下流程：

1. **引入替代 API**：新增推荐使用的函数或方法。
2. **标记旧 API 为 deprecated**：使用编译器属性（如 C++17 `[[deprecated("message")]]`、GCC `__attribute__((deprecated))`）在头文件中标记。
3. **保留一个 major 版本周期**：旧 API 至少保留一个主版本，给使用者迁移时间。
4. **文档说明**：在 CHANGELOG 和文档中说明废弃原因、替代方案和移除时间表。
5. **在下一个 major 版本中移除**：递增 major 版本号，删除废弃 API。

### C ABI 的废弃

C ABI 函数一旦发布通常不删除（即使在 major 版本升级中也极为谨慎），因为删除会导致动态链接失败。更常见的做法是：

- 保留函数符号，但内部实现转发到新函数。
- 在函数被调用时输出废弃警告（通过日志或回调）。
- 仅在 `abi_version` 递增时才真正删除。

## 版本协商流程

### 动态加载场景

通过 `dlopen`/`LoadLibrary` 动态加载 FFI 时，建议执行以下版本协商：

1. 加载共享库。
2. 使用 `dlsym`/`GetProcAddress` 获取 `TVMFFIGetVersion` 函数指针。
3. 调用 `TVMFFIGetVersion` 获取运行时版本。
4. 检查 `runtime_version.abi_version == TVM_FFI_ABI_VERSION`。
5. 如果不匹配，卸载库并报告版本不兼容错误。
6. 如果匹配，继续获取其他函数指针。

### 直接链接场景

直接链接 FFI 共享库时，操作系统的动态链接器在加载时解析符号。如果共享库缺少引用的符号，加载失败。这种模式下：

- 编译时头文件版本决定了期望的 ABI 版本。
- 运行时共享库必须导出所有编译时引用的符号。
- 新版本共享库通过 SONAME 机制标识 ABI 版本（如 `libtvm_ffi.so.1`）。

### 语言绑定的版本检查

Python 绑定在 `import tvm_ffi` 时检查版本：

```python
# 伪代码
runtime_version = _ffi_api.TVMFFIGetVersion()
assert runtime_version.abi_version == _FFI_ABI_VERSION, \
    f"ABI version mismatch: expected {_FFI_ABI_VERSION}, got {runtime_version.abi_version}"
```

Rust 绑定在 `tvm-ffi-sys` 的 `build.rs` 中检查头文件版本，在运行时初始化时检查共享库版本。

## TVM 运行时的版本依赖

`include/tvm/runtime/base.h:27-29` 明确声明：

```cpp
// TVM runtime fully relies on TVM FFI C API
#include <tvm/ffi/c_api.h>
```

TVM 运行时直接依赖 FFI C ABI，不依赖 C++ 层。这种设计意味着：

1. TVM 运行时编译时使用的 FFI 头文件版本决定了期望的 ABI 版本。
2. 运行时加载的 FFI 共享库必须具有匹配的 `abi_version`。
3. FFI C++ 层的变更（模板、内联函数、类布局）不影响 TVM 运行时的 ABI 兼容性。

TVM 编译器中的 C++ 代码同时依赖 FFI C++ API，因此编译器对 FFI 版本的要求更严格（可能需要匹配 major.minor 版本）。

## 版本演进示例

### 假设的演进路径

| 版本 | 变更类型 | 说明 |
|------|---------|------|
| 1.0.0 | 初始发布 | 核心 ABI 稳定 |
| 1.1.0 | minor | 新增设备流管理 API（`TVMFFIEnvSetStream`/`TVMFFIEnvGetStream`） |
| 1.2.0 | minor | 新增 List/Dict 容器类型 |
| 2.0.0 | major | 废弃旧的错误 API，移除 deprecated 函数 |
| 3.0.0 | major + abi | 修改 `TVMFFIAny` 布局以支持更大的联合体 |

每个 minor 版本保持 ABI 向后兼容，已编译的二进制可以直接升级到新的 minor 版本共享库而无需重新编译。

## 设计分析

TVM FFI 的版本管理策略体现了"契约式演进"思想：ABI 是明确的契约，版本号是契约的版本，结构体布局和函数签名是契约的条款。通过语义化版本号，使用者可以准确判断版本间的兼容性风险。

三层版本号（abi/major/minor）的设计区分了三种兼容性维度：二进制兼容（abi）、源码兼容（major）、功能新增（minor）。这种精细划分比单一版本号更能传达兼容性信息，尤其对于需要长期维护的基础设施库。

不透明句柄和动态注册机制是保持 ABI 稳定的重要架构手段——它们将易变的实现细节隐藏在稳定的接口之后，使得核心 ABI 不需要因功能扩展而频繁变更。

## 相关概念

- [002 分层设计](002-layered-design.md)：C ABI 层的稳定性边界
- [005 ABI 稳定性策略](005-abi-stability-strategy.md)：ABI 保证机制详解
- [006 最小核心设计哲学](006-minimal-core-philosophy.md)：最小核心降低 ABI 变更风险
- [009 扩展点与插件机制](009-extension-points-plugin-mechanism.md)：通过扩展避免核心变更
