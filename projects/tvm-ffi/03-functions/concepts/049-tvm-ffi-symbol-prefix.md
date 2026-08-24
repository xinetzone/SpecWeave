---
type: Concept
title: "视角049：__tvm_ffi_ 符号前缀"
description: "分析 TVM FFI 的符号命名约定：__tvm_ffi_ 前缀用于导出函数、__tvm_ffi__ 双下划线前缀用于内部元数据、TVM_FFI_DLL_EXPORT_TYPED_FUNC 宏自动生成符号，以及该约定如何避免命名空间冲突。"
tags:
  - function
  - symbol-prefix
  - c-abi
  - dll-export
  - naming-convention
  - dynamic-loading
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-001, F-016, F-018, F-019, F-020, F-022
  - code:
    - include/tvm/ffi/function.h
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/extra/module.h
    - examples/stable_c_abi/src/add_one_cpu.c
---

# 视角049：__tvm_ffi_ 符号前缀

## 概述

TVM FFI 使用统一的 `__tvm_ffi_` 前缀命名所有跨 FFI 边界导出的符号。这一约定涵盖用户函数（`__tvm_ffi_<name>`）、模块入口点（`__tvm_ffi_main`）、类型元数据（`__tvm_ffi__metadata_<name>`）、文档字符串（`__tvm_ffi__doc_<name>`）以及库上下文字段。前缀设计基于 C 语言的名称修饰规则和动态链接器的符号查找机制，确保 FFI 符号在全局符号空间中不与其他库冲突，并允许运行时通过约定的命名模式自动发现和加载函数。

## 符号常量定义

所有前缀相关的符号常量集中定义在 `extra/module.h:281-297`：

```cpp
namespace symbol {
constexpr const char* tvm_ffi_symbol_prefix = "__tvm_ffi_";
constexpr const char* tvm_ffi_main = "__tvm_ffi_main";
constexpr const char* tvm_ffi_library_ctx = "__tvm_ffi__library_ctx";
constexpr const char* tvm_ffi_library_bin = "__tvm_ffi__library_bin";
constexpr const char* tvm_ffi_metadata_prefix = "__tvm_ffi__metadata_";
constexpr const char* tvm_ffi_doc_prefix = "__tvm_ffi__doc_";
}  // namespace symbol
```

## 前缀层次结构

符号前缀采用**单层下划线 vs 双下划线**的层次区分：

| 模式 | 用途 | 示例 |
|------|------|------|
| `__tvm_ffi_<name>` | 用户可见的导出函数 | `__tvm_ffi_add`、`__tvm_ffi_matmul` |
| `__tvm_ffi_main` | 模块标准入口点 | `__tvm_ffi_main` |
| `__tvm_ffi__metadata_<name>` | 函数类型元数据（JSON schema） | `__tvm_ffi__metadata_add` |
| `__tvm_ffi__doc_<name>` | 函数文档字符串 | `__tvm_ffi__doc_add` |
| `__tvm_ffi__library_ctx` | 库上下文指针（JIT 场景） | — |
| `__tvm_ffi__library_bin` | 嵌入的库二进制数据 | — |

设计规则：
- **单下划线 + 用户名称**：公开函数符号，模块的 `GetFunction` 通过拼接 `__tvm_ffi_` + 函数名查找。
- **双下划线 + 内部类别**：框架内部使用的元数据和辅助符号，不直接作为用户函数调用。双下划线在 C/C++ 标准中保留给实现使用，进一步降低冲突风险。

## C ABI 函数签名约定

所有 `__tvm_ffi_<name>` 导出函数必须遵循 `TVMFFISafeCallType` 签名。从源码中的 C 示例（`examples/stable_c_abi/src/add_one_cpu.c:27`）可以看到：

```c
TVM_FFI_DLL_EXPORT int __tvm_ffi_add_one_cpu(void* handle,
                                            const TVMFFIAny* args,
                                            int32_t num_args,
                                            TVMFFIAny* result);
```

函数签名要素：

1. **返回 `int`**：0 表示成功，-1 表示错误（错误详情通过 TLS 传播）。
2. **`void* handle`**：函数上下文/self 指针，对应 `TVMFFIFunctionCell.resource_handle`。
3. **`const TVMFFIAny* args`**：参数数组指针。
4. **`int32_t num_args`**：参数数量。
5. **`TVMFFIAny* result`**：返回值写入位置。

这与 `TVMFFISafeCallType`（`c_api.h:501-502`）完全一致：

```c
typedef int (*TVMFFISafeCallType)(void* handle,
                                  const TVMFFIAny* args,
                                  int32_t num_args,
                                  TVMFFIAny* result);
```

## TVM_FFI_DLL_EXPORT_TYPED_FUNC 宏

`TVM_FFI_DLL_EXPORT_TYPED_FUNC` 宏（`function.h:1008-1027`）自动生成带前缀的 C ABI 包装函数：

```cpp
#define TVM_FFI_DLL_EXPORT_TYPED_FUNC_IMPL_(ExportName, Function)                      \
  extern "C" {                                                                         \
  TVM_FFI_DLL_EXPORT int __tvm_ffi_##ExportName(void* self, const TVMFFIAny* args,     \
                                                int32_t num_args, TVMFFIAny* result) { \
    TVM_FFI_SAFE_CALL_BEGIN();                                                         \
    using FuncInfo = ::tvm::ffi::details::FunctionInfo<decltype(Function)>;            \
    static std::string name = #ExportName;                                             \
    ::tvm::ffi::details::unpack_call<typename FuncInfo::RetType>(                      \
        std::make_index_sequence<FuncInfo::num_args>{}, &name, Function,               \
        reinterpret_cast<const ::tvm::ffi::AnyView*>(args), num_args,                  \
        reinterpret_cast<::tvm::ffi::Any*>(result));                                   \
    TVM_FFI_SAFE_CALL_END();                                                           \
  }                                                                                    \
  }
```

使用示例：

```cpp
int AddOne_(int x) { return x + 1; }
TVM_FFI_DLL_EXPORT_TYPED_FUNC(AddOne, AddOne_);

TVM_FFI_DLL_EXPORT_TYPED_FUNC(SubOne, [](int x) { return x - 1; });
```

展开后生成：

- `__tvm_ffi_AddOne`：C ABI 包装函数，内部解包 `TVMFFIAny` 参数并调用 `AddOne_`。
- `__tvm_ffi_SubOne`：包装 lambda 的 C ABI 函数。
- 当 `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA` 定义时，额外生成 `__tvm_ffi__metadata_AddOne`，返回 JSON 格式的类型 schema。

宏内部的关键机制：

1. **`extern "C"`**：禁用 C++ 名称修饰（name mangling），确保符号名在编译后保持为 `__tvm_ffi_AddOne` 而非 `_Z17__tvm_ffi_AddOnePvPK10TVMFFIAyiPS0_` 等修饰名。
2. **`TVM_FFI_DLL_EXPORT`**：平台相关的导出声明（Windows 上为 `__declspec(dllexport)`，类 Unix 上为 `__attribute__((visibility("default")))`）。
3. **`TVM_FFI_SAFE_CALL_BEGIN/END`**：包裹函数体，捕获所有 C++ 异常并通过 TLS 传播。
4. **`FunctionInfo`**：在编译期推导函数的返回类型、参数数量和参数类型。
5. **`unpack_call`**：根据编译期索引序列，将 `TVMFFIAny` 数组解包为类型化参数并调用原始函数。

## 元数据导出

当定义 `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA` 时，宏额外生成 `__tvm_ffi__metadata_<name>` 符号（`function.h:1010-1023`）：

```cpp
extern "C" {
TVM_FFI_DLL_EXPORT int __tvm_ffi__metadata_##ExportName(
    void* self, const TVMFFIAny* args, int32_t num_args, TVMFFIAny* result) {
  TVM_FFI_SAFE_CALL_BEGIN();
  using FuncInfo = ::tvm::ffi::details::FunctionInfo<decltype(Function)>;
  std::ostringstream os;
  os << R"({"type_schema":)"
     << ::tvm::ffi::EscapeStringJSON(
            ::tvm::ffi::String(FuncInfo::TypeSchema()))
     << R"(})";
  // ... 返回 JSON 字符串 ...
  TVM_FFI_SAFE_CALL_END();
}
}
```

元数据函数返回 JSON 字符串，包含函数的类型 schema（参数类型、返回类型）。运行时或绑定生成器可以通过查找 `__tvm_ffi__metadata_<name>` 符号自动发现函数签名，无需手动维护类型信息。

## 文档导出

`TVM_FFI_DLL_EXPORT_TYPED_FUNC_DOC` 宏（`function.h:1070`）导出 `__tvm_ffi__doc_<name>` 符号，包含函数的文档字符串。文档字符串可被 stub 生成器和文档工具读取。

## 动态符号查找

在 ORC JIT 和动态库加载场景中，运行时通过前缀拼接直接调用 `dlsym`/`GetProcAddress` 查找符号：

```
函数名 "add" → 符号名 "__tvm_ffi_add" → dlsym(handle, "__tvm_ffi_add")
```

这一机制的优点：

1. **无需注册函数表**：动态库中的函数通过符号命名约定自动暴露，不需要在 `__tvm_ffi_main` 中手动注册每个函数。
2. **延迟解析**：`dlsym` 只在首次调用函数时执行，后续调用直接使用缓存的函数指针。
3. **ORC JIT 兼容**：LLVM ORC JIT 的 `ExecutionSession::lookup` 可以直接查找 `__tvm_ffi_<name>` 符号，实现 JIT 编译函数的无缝调用。

## C API 本身的命名前缀

除了用户导出的函数符号，TVM FFI 的 C API 函数本身也使用 `TVMFFI` 前缀（而非 `__tvm_ffi_`）：

- `TVMFFIFunctionCreate`、`TVMFFIFunctionCall`、`TVMFFIFunctionGetGlobal`
- `TVMFFIObjectIncRef`、`TVMFFIObjectDecRef`
- `TVMFFIGetVersion`、`TVMFFITypeKeyToIndex`

两套前缀的区分：
- **`TVMFFI`**（大驼峰）：C API 库函数，由 `libtvm_ffi` 导出，供外部调用方直接链接使用。
- **`__tvm_ffi_`**（小写下划线）：用户模块导出的 FFI 函数，由运行时通过动态符号查找发现，不直接链接。

这种区分使得 C API 函数和用户 FFI 函数在符号空间中互不干扰。

## 设计分析

`__tvm_ffi_` 前缀约定的设计考量：

1. **C 语言命名空间模拟**：C 语言没有 C++ 的 `namespace` 机制，前缀是唯一的符号隔离手段。双下划线前缀（`__tvm_ffi__`）利用 C/C++ 标准保留给实现的标识符空间，进一步降低冲突概率。

2. **自动发现能力**：运行时可以遍历动态库的导出符号表，筛选 `__tvm_ffi_` 前缀的符号自动注册函数，无需显式注册表。这在 JIT 编译场景中尤为重要——JIT 生成的机器码可以直接导出符合约定的符号，运行时立即发现并调用。

3. **零注册开销**：对比 `TVM_FFI_STATIC_INIT_BLOCK + refl::GlobalDef` 的静态初始化注册方式，符号导出方式不需要运行时初始化代码，函数在库加载后立即可用。静态初始化顺序问题也得以避免。

4. **工具链友好**：`extern "C"` + 明确前缀使得 `nm`、`objdump`、`depends.exe` 等工具可以直接识别 FFI 函数，便于调试和诊断。

5. **与 SafeCall ABI 的组合**：前缀仅解决符号命名问题，函数签名的 ABI 稳定性由 `TVMFFISafeCallType` 和 `TVMFFIAny` 保证。两者组合提供了完整的 C ABI 互操作方案。

## 相关概念

- [048 模块入口点约定](048-module-entry-point-convention.md)：__tvm_ffi_main 作为模块入口
- [039 C 回调创建](039-c-callback-creation.md)：FromExternC 创建的函数不使用前缀
- [036 Packed Function 约定](036-packed-function-convention.md)：SafeCall ABI 签名
- [040 全局函数注册表](040-global-function-registry.md)：静态注册 vs 符号导出的对比
