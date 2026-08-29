---
type: source-code
source_id: tvm-ffi
title: TVM-FFI 跨语言基础源码
description: TVM-FFI 0.1.13 跨语言互操作层源码登记，涵盖 C ABI、C++ 核心、Cython Python 绑定与 Rust 绑定
tags: [tvm, ffi, c-abi, cython, rust, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-tvm-ffi
    resource: "/references/facts-tvm-ffi.md"
    title: TVM-FFI 事实清单
---

# TVM-FFI 源码登记

- **source_id**: tvm-ffi
- **type**: source-code
- **path**: `d:\AI\.chaos\libs\ffi\tvm-ffi\`
- **language**: C++/Python(Cython)/Rust
- **version**: 0.1.13
- **file_count**: 195
- **fact_file**: /references/facts-tvm-ffi.md
- **registered**: 2026-08-23

## 目录结构

| 目录 | 文件数 | 职责 |
|------|--------|------|
| `src/ffi/` | 29 | C++ 核心实现：object、function、container、error、dtype、tensor、module、dataclass、反射 |
| `include/tvm/ffi/` | 53 | C++ 公共头文件：c_api、any、object、function、container、reflection、extra |
| `python/tvm_ffi/` | 65 | Python 绑定：Cython 核心扩展（core.pyx）、注册表、容器、Module、dataclass 支持 |
| `rust/` | 48 | Rust 绑定：tvm-ffi（高级绑定）与 tvm-ffi-sys（原始 FFI） |

## 关键文件

### C ABI 核心

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/ffi/c_api.h` | 核心 C ABI 定义：TVMFFIAny（16字节标签联合体）、TVMFFIObject（24字节对象头）、版本号、类型索引常量、所有 extern "C" 函数声明 |
| `include/tvm/ffi/any.h` | C++ Any（拥有所有权）与 AnyView（借用引用）值类型 |
| `include/tvm/ffi/object.h` | Object 基类、ObjectRef 智能指针、make_object、类型声明宏 |
| `include/tvm/ffi/function.h` | FunctionObj、TVM_FFI_SAFE_CALL_BEGIN/END 宏、Function 引用类 |
| `include/tvm/ffi/error.h` | Error 类型与 SafeCallContext thread-local 错误传递 |
| `include/tvm/ffi/string.h` | ffi::String 不可变字符串 |
| `include/tvm/ffi/dtype.h` | DLDataType 支持 |
| `include/tvm/ffi/tensor.h` | Tensor/DLPack 互操作 |

### C++ 核心实现

| 文件路径 | 职责 |
|---------|------|
| `src/ffi/object.cc` | TypeTable 全局类型注册表、类型索引三级分配（静态/槽位/动态≥128）、对象生命周期、反射字段/方法/元数据注册 |
| `src/ffi/function.cc` | GlobalFunctionTable（Map<String,Any>）、TVMFFIFunctionCreate/SetGlobal/GetGlobal/Call、SafeCallContext |
| `src/ffi/container.cc` | Array/List/Map/Dict 容器实现、SeqBaseObj/MapBaseObj、ffi.Array/List/Map/Dict 工厂函数 |
| `src/ffi/error.cc` | TVMFFIErrorSetRaised/MoveFromRaised/Create 错误 C API |
| `src/ffi/dtype.cc` | TVMFFIDataTypeFromString/ToString |
| `src/ffi/tensor.cc` | TVMFFITensorCreateUnsafeView/FromDLPack/ToDLPack、ffi.Shape 工厂 |
| `src/ffi/init_once.cc` | TVMFFIHandleInitOnce/DeinitOnce（双检锁单例） |
| `src/ffi/backtrace.cc` | 堆栈回溯支持 |

### C++ 扩展功能（src/ffi/extra/）

| 文件路径 | 职责 |
|---------|------|
| `module.cc` | ModuleObj 基类：GetFunction（查询导入链）、ImportModule（DFS 环检测）、LoadFromFile |
| `library_module.cc` | LibraryModuleObj：动态库加载、符号解析、嵌入式库二进制（import_tree CSR + key-value）、ContextSymbolRegistry |
| `dataclass.cc` | 基于反射的 DeepCopy/ReprPrint/RecursiveHash/RecursiveEq（kMaxTraversalStackDepth=1<<20） |
| `serialization.cc` | 序列化支持 |
| `json_parser.cc` | JSON 解析器 |
| `json_writer.cc` | JSON 写入器 |
| `structural_equal.cc` | SEqualReducer：五种相等/哈希 kind（Unsupported/UniqueInstance/ConstTreeNode/DAGNode/FreeVar） |
| `structural_hash.cc` | SHashReducer |
| `reflection_extra.cc` | 反射扩展 |

### 容器头文件（include/tvm/ffi/container/）

| 文件 | 职责 |
|------|------|
| `array.h` | Array<T> 不可变序列 |
| `list.h` | List<T> 可变序列 |
| `map.h` | Map<K,V> 不可变有序映射 |
| `dict.h` | Dict 可变映射 |
| `shape.h` | Shape（int64 数组） |
| `string.h` | String/Bytes |
| `tensor.h` | Tensor 容器 |

### 反射系统（include/tvm/ffi/reflection/）

| 文件 | 职责 |
|------|------|
| `registry.h` | refl::GlobalDef()/ObjectDef<T>()/TypeAttrDef<T>() 注册构建器 |
| `accessor.h` | 字段访问器 |
| `creator.h` | 对象创建器 |
| `access_path.h` | 访问路径 |
| `enum_def.h` | 枚举定义 |
| `overload.h` | 重载支持 |

### Python 绑定（python/tvm_ffi/）

| 文件路径 | 职责 |
|---------|------|
| `core.pyx` | Cython 核心扩展：Any/Object/Function/容器的 Python 绑定 |
| `_ffi_api.py` | _FFI_INIT_FUNC 自动绑定约 80 个 ffi.* 全局函数 |
| `registry.py` | register_global_func 装饰器、register_object 装饰器（type_key→Python 类映射） |
| `container.py` | Array/List/Map/Dict Python 类、getitem_helper、normalize_index |
| `module.py` | Module Python 类（kind/imports_/entry_name）、ModulePropertyMask |
| `__init__.py` | 包入口：加载动态库（libinfo.load_lib_ctypes）、torch 符号冲突规避 |
| `dataclasses/` | dataclass 支持 |
| `stub/` | 类型存根生成 |
| `cython/` | Cython 绑定源码 |
| `cpp/` | C++ 工具子模块 |
| `testing/` | 测试工具 |

### Rust 绑定（rust/）

| 目录/文件 | 职责 |
|-----------|------|
| `tvm-ffi-sys/` | 原始 FFI 绑定（unsafe extern "C" 声明） |
| `tvm-ffi/src/lib.rs` | 高级绑定 crate 入口，重新导出 tvm_ffi_sys |
| `tvm-ffi/src/any.rs` | Any（拥有所有权）与 AnyView（借用引用，Copy+Clone） |
| `tvm-ffi/src/object.rs` | Object（#[repr(C)]）、ObjectArc<T>（Arc 式共享所有权）、ObjectCore/ObjectRefCore trait |
| `tvm-ffi/src/function.rs` | FunctionObj、CallbackFunctionObjImpl<F>、call_packed/call_tuple（小向量优化 STACK_LEN=4） |
| `tvm-ffi/src/collections/` | array/map/shape/tensor 集合模块 |
| `tvm-ffi/src/derive/` | #[derive(Object)] 过程宏 |
| `tvm-ffi/src/error.rs` | Error 类型、from_raised() |
| `tvm-ffi/src/extra/module.rs` | Module Rust 绑定 |
| `tvm-ffi/src/dtype.rs` | DataType |
| `tvm-ffi/src/device.rs` | Device |

## 设计要点

- **ABI 四大原则**：最小高效、跨编译器版本稳定、ML 原生支持（tensor/shape/dtype）、可扩展动态类型注册
- **不依赖 C++ RTTI**：使用自定义 type_index 系统，支持 `-fno-rtti` 编译
- **合并引用计数**：强引用低 32 位、弱引用高 32 位，单次 u64 原子操作完成
- **Any 标签联合体**：16 字节，type_index<64 为栈上 POD（无堆分配），≥64 为堆分配引用计数对象
- **所有 C ABI 函数返回 int**：0 成功/-1 错误，错误通过 thread-local SafeCallContext 传递
