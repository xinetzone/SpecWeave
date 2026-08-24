---
type: Concept
title: "视角100：存根生成 stubgen"
description: "解析 tvm-ffi-stubgen 工具：从 C++ 反射元数据生成 Python 类型存根（.pyi 风格内联块）、内联指令标记、Generator 可插拔架构、CMake 与 CLI 两种集成方式、类型映射与导入收集。"
tags:
  - reflection
  - stubgen
  - codegen
  - python-tooling
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-036, F-254, F-329, F-330, F-338, F-339, F-340, F-341
  - code:
    - docs/packaging/stubgen.rst
    - python/tvm_ffi/stub/generator.py
    - python/tvm_ffi/stub/cli.py
    - python/tvm_ffi/stub/python_generator/generator.py
---

# 视角100：存根生成 stubgen

## 概述

`tvm-ffi-stubgen` 是 TVM FFI 提供的类型存根生成工具，它在构建时加载已编译的共享库，读取运行时反射注册表中的全局函数与对象类型信息，自动生成带类型注解的 Python 源代码。生成的存根使 IDE 能提供自动补全，并使 mypy/pyright 等静态类型检查器能对跨 FFI 边界的调用进行类型校验。工具采用"语言无关管线 + 可插拔语言生成器"的架构，目前内置 Python 生成器，并支持 CMake 与命令行两种集成方式。

## 工作原理

stubgen 的核心流程是"加载 DLL → 读取反射注册表 → 渲染代码"：

1. **加载共享库**：通过 `--dlls` 参数指定一个或多个已编译的 `.so`/`.dll`/`.dylib`。库加载时，其静态初始化块通过 `refl::GlobalDef` 与 `refl::ObjectDef<T>` 将全局函数和对象类型注册到 FFI 运行时。
2. **枚举反射元数据**：工具通过 `TVMFFIGetTypeInfo`、`Function::ListGlobalNames`（F-282）及 `tvm_ffi.registry.list_global_func_names()` 等 API 遍历所有已注册的类型与函数，提取字段名、字段类型、方法签名、参数 schema、文档字符串等信息，构造语言无关的 `ObjectInfo`/`FuncInfo` 中间表示（`stub/utils.py`）。
3. **渲染目标代码**：将中间表示交给 `Generator`（`stub/generator.py:52`）渲染为具体的 Python 类型注解文本，包括字段声明、`__init__`、`__ffi_init__`、方法签名等。
4. **写回文件**：在"指令模式"下，仅替换文件中 `# tvm-ffi-stubgen(begin)` 与 `# tvm-ffi-stubgen(end)` 标记之间的内容，保留用户手写代码；在"初始化模式"下，生成全新的 `_ffi_api.py` 与 `__init__.py` 脚手架。

## 内联指令系统

stubgen 的一大设计特色是内联指令（inline directives）。指令以注释标记界定生成区域，工具只修改标记内的内容，标记外的代码完全保留。这使得用户可以在生成文件中添加自定义方法、文档、导入，而不被重新生成覆盖。

支持的指令类型包括（`docs/packaging/stubgen.rst:292-400`）：

| 指令 | 用途 |
|------|------|
| `global/<prefix>` | 全局函数存根块 |
| `object/<type_key>` | 对象类型的字段与方法存根 |
| `import-section` | 自动导入区 |
| `export/<module>` | 子模块再导出 |
| `__all__` | 公共导出列表 |
| `ty-map` | C++ 类型键到 Python 类型路径的映射 |
| `import-object` | 注入自定义导入 |
| `skip-file` | 跳过整个文件 |

典型对象块生成结果形如：

```python
@tvm_ffi.register_object("my_ffi_extension.IntPair")
class IntPair(tvm_ffi.Object):
    # tvm-ffi-stubgen(begin): object/my_ffi_extension.IntPair
    a: int
    b: int
    if TYPE_CHECKING:
        def __init__(self, a: int, b: int) -> None: ...
        def __ffi_init__(self, a: int, b: int) -> None: ...
        def sum(self, /) -> int: ...
    # tvm-ffi-stubgen(end)
```

注意 `__init__` 与方法签名被包裹在 `if TYPE_CHECKING:` 中——这使得类型注解在静态检查时可见，但在运行时不实际定义方法（方法在运行时由 FFI 动态分派），避免了签名与实际 C++ 实现不一致的运行时风险。

## 可插拔 Generator 架构

`stub/generator.py` 将代码生成抽象为 `Generator` Protocol（`generator.py:52-177`），明确分离两个关注点：

1. **语言无关基础设施**：读取 FFI 反射注册表（`lib_state`）、解析/写回标记块（`file_utils`）、构造 `ObjectInfo`/`FuncInfo` 元数据。这一层完全不感知目标语言。
2. **语言特定渲染**：将 `TypeSchema` 渲染为目标语言类型表达式、管理该语言的导入语法、发射类定义与函数签名。

`Generator` Protocol 要求实现者提供 `generate_global_funcs_block`、`generate_object_block`、`generate_import_section_block`、`generate_all_block` 等块级方法，以及 `generate_api_file`/`generate_init_file` 等整文件脚手架方法。导入收集器是不透明的——管线只通过 `new_imports`/`add_imported_object`/`generate_import_section_block` 与它交互，不窥探内部表示。目前注册了 `"python"` 生成器（`PythonGenerator`，`generator.py:181`），未来增加 Rust bindgen、C++ header 生成等目标语言只需"实现一个 Generator"，无需分叉管线。

## CMake 集成

推荐通过 CMake 函数 `tvm_ffi_configure_target` 自动集成（`stubgen.rst:44`）：

```cmake
tvm_ffi_configure_target(<target>
    STUB_DIR <dir>
    [STUB_INIT ON|OFF]
    [STUB_PKG <pkg>]
    [STUB_PREFIX <prefix>]
)
```

- `STUB_DIR`：Python 源码目录，必需。
- `STUB_INIT`：`OFF`（默认）时仅填充已有指令块，不创建新文件；`ON` 时从头生成 `_ffi_api.py` 与 `__init__.py`。
- `STUB_PKG`：Python 包名，决定目录结构与 `load_lib_module` 调用中的包名。
- `STUB_PREFIX`：注册名前缀过滤，仅包含匹配前缀的函数与类。

这使得每次构建后存根自动刷新，开发者无需手动运行命令。

## CLI 用法

独立使用时通过 `tvm-ffi-stubgen` 命令（`stubgen.rst:196`）：

```bash
tvm-ffi-stubgen python/my_ffi_extension \
  --dlls build/libmy_ffi_extension.so \
  --init-pypkg my-ffi-extension \
  --init-lib my_ffi_extension \
  --init-prefix "my_ffi_extension."
```

关键参数：
- `<directory>`：存根目录（位置参数）。
- `--dlls`：生成时加载的共享库，分号分隔多个。
- `--init-pypkg`/`--init-lib`/`--init-prefix`：三者同时提供时进入完整初始化模式；省略时进入仅指令模式。
- `--dry-run`：预览变更不写文件。
- `--verbose`：打印每个文件的统一 diff。
- `--imports`：生成前额外导入的 Python 模块。
- `--indent`：生成代码缩进宽度（默认 4）。

## 类型映射与导入

stubgen 需将 C++ 类型键解析为 Python 类型路径。默认映射由 `Generator.default_ty_map()` 提供，将 `ffi.Object`、`ffi.Tensor`、`ffi.Array` 等内置类型映射到 `tvm_ffi` 包路径。`ty-map` 指令允许用户覆盖默认映射（`stubgen.rst:383`）：

```python
# tvm-ffi-stubgen(ty-map): ffi.reflection.AccessStep -> ffi.access_path.AccessStep
```

`import-object` 指令注入自定义导入（`stubgen.rst:391`）：

```python
# tvm-ffi-stubgen(import-object): ffi.Object;False;_ffi_Object
```

格式为 `<full_name>;<type_checking_only>;<alias>`，其中第二字段控制导入是否包裹在 `if TYPE_CHECKING:` 中。导入收集器在渲染各块时累积所需类型，最终由 `generate_import_section_block` 统一发射，自动去重并避免遮蔽本地定义。

## 设计分析

stubgen 体现了"反射元数据即单一事实来源"的设计哲学——C++ 中通过 `ObjectDef<T>` 注册的字段、方法、类型 schema 不仅驱动运行时的 Python 绑定与序列化，还在构建时驱动静态类型存根的生成，消除了手写 Python 类型声明与 C++ 实际签名不同步的问题。内联指令机制在"全自动生成"与"完全手写"之间取得平衡：生成区域保持与 C++ 同步，手写区域保留用户定制，二者在同一文件中共存。可插拔 Generator 架构使工具不局限于 Python，其语言无关的元数据层未来可服务于任意目标语言的绑定生成。`if TYPE_CHECKING:` 包裹运行时方法的技巧则精确处理了"静态可见但运行时由 FFI 动态提供"的语义，避免了双重定义冲突。整体设计使跨语言 FFI 的类型安全从运行时前移到了编译期与编辑期。

## 相关概念

- [089 TypeInfo 运行时类型](089-type-info.md)：stubgen 读取的类型元数据
- [086 FieldInfo 设计](086-field-info.md)：字段名与类型的来源
- [087 MethodInfo 设计](087-method-info.md)：方法签名的来源
- [092 c_class Python 集成](092-c-class-python-integration.md)：运行时绑定，stubgen 为其提供静态类型
- [090 ObjectDef 构建器](090-object-def-builder.md)：C++ 侧注册的元数据被 stubgen 消费
