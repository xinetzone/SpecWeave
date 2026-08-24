---
type: Concept
title: "视角008：模块系统与动态加载"
description: "分析 TVM FFI 的模块系统设计，包括动态库加载（.so/.dll/.dylib）、模块函数导出与注册、Module 对象的 ABI 接口，以及模块间符号解析和依赖管理机制。"
tags:
  - architecture
  - module-system
  - dynamic-loading
  - plugin
  - dlopen
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-329, F-330, F-331, F-332, F-333, F-334, F-335
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/module.h
---

# 视角008：模块系统与动态加载

## 概述

TVM FFI 提供了一套动态模块加载系统，允许在运行时加载共享库（`.so`/`.dll`/`.dylib`）并自动注册其中导出的函数。模块系统建立在函数注册机制之上，`Module` 本身是一个对象类型（`kTVMFFIModule = 73`），通过统一的 C ABI 接口实现跨平台动态加载。本视角分析模块系统的架构设计、加载流程和扩展机制。

## C++ 模块接口

### 模块加载方法

模块加载功能由 C++ `Module` 类（`extra/module.h:218`）的静态方法提供，建立在 C ABI 的对象和函数注册机制之上：

1. **`Module::LoadFromFile`**（`module.h:264`）：从文件路径加载模块。
   ```cpp
   static Module LoadFromFile(const String& file_name);
   ```
   根据文件扩展名自动推断模块格式（如 `.so`、`.dylib`、`.dll`），内部调用平台动态加载器。

2. **二进制加载**：支持序列化的模块类型通过全局注册表中以 `ffi.Module.load_from_bytes.<kind>` 命名的函数加载。`ModulePropertyMask::kBinarySerializable` 标志（`module.h:231`）标识支持序列化的模块类型。

3. **模块属性**：`ModulePropertyMask` 枚举定义了模块能力标志：
   - `kBinarySerializable`（0b001）：可序列化为字节数组。
   - `kRunnable`（0b010）：可直接返回可运行函数。
   - `kCompilationExportable`（0b100）：可导出为目标文件或源代码。

### 模块函数获取

`ModuleObj` 类（`module.h:186`，类型索引 `kTVMFFIModule`）提供：

- `GetFunction(const String& name, bool query_imports)`：按名称获取函数，返回 `Function`。
- `GetFunctionMetadata(const String& name, bool query_imports)`：获取函数元数据，返回 `Optional<String>`。
- `imports()`：获取模块依赖数组（`Array<Any>`）。

`query_imports` 参数控制是否查询导入的其他模块。当模块内部依赖其他模块的函数时，设置此标志可以触发跨模块符号解析。模块内部维护 `import_lookup_cache_`（`Map<String, Function>`，`module.h:202`）缓存导入查找结果。

### 模块生命周期

模块作为 FFI 对象（继承自 `Object`）通过引用计数管理：

- 使用 `TVMFFIObjectIncRef`/`TVMFFIObjectDecRef` 管理生命周期。
- 最后一个引用释放时，模块对象析构，动态库卸载。
- 模块注册的全局函数通过全局函数表管理生命周期。

## Module C++ 类

### Module 类设计

`Module` 类（`extra/module.h:218`）继承自 `ObjectRef`，封装了模块对象：

- `static Module LoadFromFile(const String& file_name)`：工厂方法，从文件加载。
- `ModuleObj* operator->()`：访问 `ModuleObj` 方法。
- 模块通过引用计数共享，拷贝 `Module` 仅增加引用计数。

### ModuleObj 基类

模块实现者继承 `ModuleObj`（`module.h:186`），重写以下方法：

- `virtual Function GetFunction(const String& name, bool query_imports) = 0`：函数查找。
- 通过 `TVM_FFI_DECLARE_OBJECT_INFO_STATIC` 宏注册类型信息。
- 可选重写：`SaveToBytes`、`WriteToFile`、导入管理等。

## 动态库加载流程

### 标准共享库模块

当加载 `.so`/`.dll`/`.dylib` 文件时，流程如下：

1. **平台动态加载**：调用 `dlopen`（Linux/macOS）或 `LoadLibrary`（Windows）加载共享库到进程地址空间。
2. **入口点查找**：查找预定义的初始化符号（如 `TVMFFIModuleInit` 或 `TVMFFIActivatelib`）。
3. **模块注册**：调用入口点函数，该函数通过 `TVMFFIFunctionSetGlobal`（C API）或 `Function::SetGlobal`（C++ API）注册模块提供的函数。
4. **函数获取**：通过 `ModuleObj::GetFunction` 或全局注册表（`Function::GetGlobal`）访问已注册的函数。

### 模块导入链

模块可以声明对其他模块的依赖。`query_imports = true` 时，`GetFunction` 会沿着导入链查找：

```
Module A → Module B → Module C
```

如果 A 中未找到函数，依次查询 B、C。这种机制支持模块组合和分层扩展。

## 全局函数注册表

模块系统与全局函数注册表紧密协作：

- **`TVMFFIFunctionSetGlobal`**（`c_api.h:1390`）：将函数注册到全局命名空间，可被任意模块通过 `TVMFFIFunctionGetGlobal`（`c_api.h:728`）获取。
- **`Function::ListGlobalNames`**（`function.h:511`）：C++ 方法，枚举所有已注册的全局函数名，内部调用注册为 `"ffi.FunctionListGlobalNamesFunctor"` 的全局函数。
- 模块加载时注册的函数带有模块来源标记，模块卸载时自动注销。

## 模块格式扩展

除了原生共享库，TVM FFI 的模块系统支持自定义模块格式：

1. **DSO 模块**：标准动态共享库。
2. **二进制模块**：通过注册为 `ffi.Module.load_from_bytes.<kind>` 的全局函数从内存加载，支持自定义序列化格式。
3. **可导出模块**：标记为 `kCompilationExportable` 的模块可导出为目标文件或源代码，编译后加载。
4. **用户自定义模块**：继承 `ModuleObj`，实现自定义的函数查找和加载逻辑。

新模块格式通过 `ModuleObj` 继承和类型注册机制接入，无需修改核心 ABI。

## NPU建议

在 NPU 运行时环境中，模块系统需要特别考虑以下场景：

1. **NPU 内核模块加载**：NPU 计算内核通常以预编译二进制形式（如 NPU 指令序列、ELF 目标文件）存在。建议通过自定义 `ModuleObj` 子类加载 NPU 内核二进制，在 `GetFunction` 中将内核封装为 `Function` 对象返回。内核二进制的元数据（输入/输出张量描述、内存需求、目标 NPU 型号）应通过模块属性或函数属性暴露。

2. **设备端代码与主机端代码分离**：NPU 模块可能同时包含主机端调度代码（运行在 CPU 上）和设备端执行代码（运行在 NPU 上）。建议在 `ModuleObj` 中区分两类函数：主机端函数通过标准 `safe_call` 路径调用，设备端函数通过 `TVMFFIStreamHandle`（定义于 `extra/c_env_api.h`）异步提交。模块加载时应根据当前 NPU 设备能力进行内核校验和版本匹配。

3. **模块依赖与 NPU 固件版本**：NPU 模块可能依赖特定版本的 NPU 固件或驱动。建议在模块二进制元数据中嵌入最低固件版本要求，加载时通过注册的 NPU 能力查询全局函数获取设备固件版本，不兼容时通过 TLS 错误机制返回明确错误而非运行时崩溃。

4. **多 NPU 设备的模块隔离**：在多卡 NPU 环境中，同一模块可能需要在不同设备上实例化。建议模块函数通过第一个参数（`DLDevice` 或设备句柄）区分目标设备，模块本身保持无状态，设备上下文由调用者传入。避免在模块全局状态中缓存特定设备的句柄。

5. **安全加载**：NPU 内核二进制在加载到设备前应进行完整性校验（签名验证）。建议在模块加载流程中增加校验钩子，校验失败时拒绝加载并通过 TLS 错误机制报告安全违规。

6. **热更新与 AOT 编译**：NPU 内核可能需要在不重启进程的情况下更新。模块的引用计数机制天然支持热更新：新模块加载并注册新版本函数，旧模块在所有引用释放后自动卸载。建议全局注册表支持函数版本号，调用者可选择使用最新版本或固定版本。

## 设计分析

模块系统是 TVM FFI 扩展性的核心载体。其设计体现了两个原则：

1. **统一抽象**：无论是原生共享库还是自定义二进制格式，都通过 `Module` 对象和 `GetFunction` 接口统一访问，调用者无需关心模块的物理来源。
2. **去中心化注册**：模块不主动导出函数表，而是在初始化时通过全局注册表注册函数。这使得模块函数可以被全局发现，也支持模块间通过导入链相互引用。

对于 NPU 等异构计算场景，模块系统提供了将设备内核封装为标准 FFI 函数的自然路径，使得上层代码可以像调用普通函数一样调用 NPU 计算。

## 相关概念

- [006 最小核心设计哲学](006-minimal-core-philosophy.md)：模块作为核心之外的扩展
- [009 扩展点与插件机制](009-extension-points-plugin-mechanism.md)：注册和扩展系统
- [010 函数注册表](010-function-registry.md)：全局函数注册机制
- [012 异步流与设备管理](012-async-stream-device-management.md)：NPU 异步执行
