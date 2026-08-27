---
type: Concept
title: "视角048：模块入口点约定"
description: "分析 TVM FFI 动态模块的入口点约定：ModuleObj 虚函数接口、Module::LoadFromFile 的加载器分发机制、__tvm_ffi_main 符号约定，以及模块的属性掩码和导入机制。"
tags:
  - function
  - module
  - entry-point
  - dynamic-loading
  - plugin
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-301, F-303
  - code:
    - include/tvm/ffi/extra/module.h
    - src/ffi/extra/module.cc
---

# 视角048：模块入口点约定

## 概述

TVM FFI 的模块系统提供了动态加载和管理函数集合的能力。`ModuleObj` 定义了模块的抽象接口，`Module` 是其托管引用。模块可以从动态库文件（.so/.dll/.dylib）加载，也可以由 JIT 编译器在内存中创建。模块通过虚函数 `GetFunction` 暴露其包含的函数，支持模块间导入和函数查找。入口点约定包括标准化的 `__tvm_ffi_main` 符号、文件扩展名到加载器的映射，以及属性掩码描述模块能力。

## ModuleObj：模块抽象基类

`ModuleObj` 定义在 `extra/module.h:43-203`，继承自 `Object`。核心虚函数包括：

1. **`kind()`**：返回模块类型标识字符串（如 "so"、"c"），用于序列化和反序列化。
2. **`GetFunction(name)`**：按名称查找模块中的函数，返回 `Optional<Function>`。这是模块的核心入口点。
3. **`GetPropertyMask()`**：返回模块能力位掩码，默认返回 0。

`Module::ModulePropertyMask`（`module.h:223-250`）定义了三种能力标志：

| 标志 | 值 | 含义 |
|------|----|------|
| `kBinarySerializable` | 0b001 | 模块可序列化为字节，系统注册 `ffi.Module.load_from_bytes.<kind>` |
| `kRunnable` | 0b010 | 模块的 `GetFunction` 返回可直接运行的函数 |
| `kCompilationExportable` | 0b100 | 模块可导出为目标文件（.o/.cc/.cu），编译后可重新加载 |

其他虚函数提供文档查询（`GetFunctionDoc`）、元数据查询（`GetFunctionMetadata`）、源码检查（`InspectSource`）、文件写入（`WriteToFile`）和序列化（`SaveToBytes`）能力，均有默认实现返回空值或抛出"不支持"异常。

## Module：托管引用

`Module` 类（`module.h:218-276`）继承自 `ObjectRef`，是 `ModuleObj` 的托管引用：

```cpp
class Module : public ObjectRef {
 public:
  enum ModulePropertyMask : int { ... };
  explicit Module(const ObjectPtr<ModuleObj>& ptr) : ObjectRef(ptr) {}
  TVM_FFI_EXTRA_CXX_API static Module LoadFromFile(const String& file_name);
  TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE(Module, ObjectRef, ModuleObj);
};
```

通过 `operator->`，调用方可以直接访问 `ModuleObj` 的方法。模块类型索引为 `kTVMFFIModule`，标记为可变（`_type_mutable = true`）且终态（`_type_final = true`）。

## LoadFromFile：文件加载机制

`Module::LoadFromFile`（`module.cc:137-161`）实现了基于文件扩展名的加载器分发：

```cpp
Module Module::LoadFromFile(const String& file_name) {
  // 提取文件扩展名作为 format
  String format = /* ... 从 file_name 解析扩展名 ... */;

  // .dll/.dylib/.dso 统一映射为 so
  if (format == "dll" || format == "dylib" || format == "dso") {
    format = "so";
  }
  // 在全局注册表中查找加载器函数
  String loader_name = "ffi.Module.load_from_file." + format;
  const auto floader = tvm::ffi::Function::GetGlobal(loader_name);
  if (!floader.has_value()) {
    TVM_FFI_THROW(RuntimeError)
        << "Loader for `." << format << "` files is not registered";
  }
  return (*floader)(file_name, format).cast<Module>();
}
```

加载流程为：提取扩展名 → 标准化动态库格式 → 查找 `ffi.Module.load_from_file.<format>` 全局函数 → 调用加载器返回 Module。新的模块格式可以通过注册新的全局函数来扩展，无需修改 `LoadFromFile` 本身。

## 符号约定

在 `extra/module.h:281-297` 中定义了标准符号常量：

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

`__tvm_ffi_main` 是动态库模块的标准入口函数。动态库加载器查找此符号并调用它，获取模块对象。库还可以导出 `__tvm_ffi_<name>` 前缀的函数符号，这些函数遵循 `TVMFFISafeCallType` 签名，可被模块加载器直接查找。元数据和文档分别通过 `__tvm_ffi__metadata_<name>` 和 `__tvm_ffi__doc_<name>` 符号提供。

## 模块导入

`ModuleObj::ImportModule`（`module.cc:102-119`）建立模块间依赖关系。在导入前通过 DFS 遍历被导入模块的传递导入链执行**循环依赖检测**，如果发现当前模块已在链中则抛出 RuntimeError。

带 `query_imports` 参数的 `GetFunction`（`module.cc:60-72`）在自身和导入模块中递归查找：

```cpp
Optional<Function> ModuleObj::GetFunction(const String& name,
                                          bool query_imports) {
  if (auto opt_func = this->GetFunction(name)) return opt_func;
  if (query_imports) {
    for (const Any& import : imports_) {
      if (auto opt_func = import.cast<Module>()
              ->GetFunction(name, query_imports))
        return *opt_func;
    }
  }
  return std::nullopt;
}
```

查找结果通过 `import_lookup_cache_`（`Map<String, Function>`）缓存以加速重复查找。同样的导入查询模式也应用于 `ImplementsFunction`、`GetFunctionDoc` 和 `GetFunctionMetadata`。

## 模块全局表

`ModuleGlobals`（`module.cc:38-58`）管理运行时保活的模块集合，使用 `std::mutex` 保护线程安全。当 `load_module` 以 `keep_alive=True` 调用时，模块被加入此集合防止意外卸载。与不使用锁的 `GlobalFunctionTable` 不同，`ModuleGlobals` 需要锁保护，因为模块可能在运行时动态添加。

在静态初始化块（`module.cc:163-195`）中，系统注册了一系列模块相关的全局函数，包括 `ffi.ModuleLoadFromFile`、`ffi.ModuleGetFunction`、`ffi.ModuleImportModule` 等，使得模块操作可以从 Python/Rust 等绑定语言调用。

## NPU 建议

在 NPU 加速场景中，模块入口点约定可用于以下场景：

1. **NPU 内核模块动态加载**：将 NPU 算子实现编译为独立的动态库（.so），通过 `Module::LoadFromFile` 在运行时加载。库中导出 `__tvm_ffi_main` 入口点，在入口函数中通过 `refl::GlobalDef().def()` 注册所有 NPU 算子函数。这样可以在不重新编译主程序的情况下更新 NPU 内核实现。

2. **NPU 驱动适配层**：为不同型号的 NPU 硬件实现不同的 `ModuleObj` 子类，通过 `GetPropertyMask` 报告能力（如是否支持异步执行、支持的数据精度）。`GetFunction` 返回设备管理函数。模块的 `kind()` 返回硬件标识，上层根据 kind 选择适配逻辑。

3. **内核库的导入链**：NPU 算子可能依赖底层的 NPU 运行时库。使用 `ImportModule` 建立依赖关系：基础运行时模块先加载，算子内核模块导入运行时模块。`query_imports=true` 的 `GetFunction` 自动在导入链中查找函数，实现分层依赖。

4. **注意事项**：
   - `__tvm_ffi_main` 在动态库加载时被调用，应避免在其中执行耗时的 NPU 初始化（如固件加载），改为延迟初始化。
   - NPU 模块的 `GetFunction` 应通过 `__tvm_ffi_<func_name>` 符号查找快速返回函数，避免每次调用都进行字符串匹配。
   - 如果 NPU 模块需要保持硬件上下文，将其加入 `ModuleGlobals` 保活。
   - 使用 `TVM_FFI_DLL_EXPORT_TYPED_FUNC` 宏导出 NPU 内核函数，自动生成符合 SafeCall 约定的符号和类型元数据。
   - 模块卸载时确保所有 NPU 命令队列已排空，避免设备访问已释放的主机内存。

## 设计分析

模块入口点约定的设计体现了**可扩展性**与**约定优于配置**的平衡：

1. **基于全局函数注册表的加载器分发**：新格式通过注册 `ffi.Module.load_from_file.<format>` 全局函数扩展，无需修改核心代码。
2. **符号命名约定**：`__tvm_ffi_` 前缀避免符号冲突，双下划线前缀用于内部元数据符号。
3. **虚函数接口最小化**：只有 `kind()` 和 `GetFunction()` 是纯虚函数，降低新模块类型的实现成本。
4. **属性掩码而非类型检测**：通过位掩码描述模块能力，比 `dynamic_cast` 更灵活，支持能力组合。
5. **循环依赖检测**：导入时的 DFS 检测在构建期阻止循环依赖，避免运行时无限递归。

## 相关概念

- [040 全局函数注册表](040-global-function-registry.md)：加载器通过全局注册表分发
- [049 __tvm_ffi_ 符号前缀](049-tvm-ffi-symbol-prefix.md)：模块导出符号的命名约定
- [041 函数一等公民](041-function-as-first-class-citizen.md)：模块通过 GetFunction 返回 Function
- [036 Packed Function 约定](036-packed-function-convention.md)：模块中函数遵循的调用约定
