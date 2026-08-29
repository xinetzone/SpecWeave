---
type: Concept
title: TVM-FFI 跨语言基础
description: TVM-FFI 0.1.13 跨语言互操作层的设计目标与核心架构，涵盖 C ABI 稳定性、Any 标签联合体、全局函数注册表、反射系统及 Cython/Rust 双绑定
tags: [tvm, ffi, c-abi, any, global-function-table, cython, rust, reflection]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: tvm-ffi-source
    resource: "/references/tvm-ffi-source.md"
    title: TVM-FFI 跨语言基础源码
---

# TVM-FFI 跨语言基础

TVM-FFI 是 Apache TVM 编译器栈的跨语言互操作基座，当前版本为 0.1.13 [F-001]。它独立于 TVM 编译器本体进行版本化，为 C++、Python、Rust 三种语言提供稳定、最小、机器学习原生的 ABI。TVM 编译器的所有层——从 TIRx 的 IR 节点到 Relax 的 Pass 系统，再到 Runtime 的 Module 加载——均构建在 FFI 提供的原语之上。理解 FFI 是理解 TVM 全栈架构的前提。

## 设计目标

TVM-FFI 的 ABI 设计遵循四大原则 [F-010]：

1. **最小高效**：核心类型（Any、Object、Function）均为栈上固定大小表示，避免不必要的堆分配。Any 仅 16 字节，Object 头仅 24 字节。
2. **跨编译器版本稳定**：所有 C ABI 函数使用 `extern "C"` 声明 [F-016]，不依赖 C++ 标准库类型在接口中出现，不依赖 C++ RTTI 或异常跨边界传播。
3. **ML 原生支持**：内建 tensor、shape、dtype 三种机器学习核心类型，无需在应用层重复定义。
4. **可扩展动态类型注册**：任何语言均可在运行时注册新的对象类型和全局函数，无需重新编译 FFI 库。

这四大原则解决了传统编译器跨语言绑定的常见痛点：ABI 不稳定导致升级困难、每种语言维护独立类型转换层导致样板代码冗余、错误处理不一致导致调试困难。

## C ABI 核心

### TVMFFIAny：16 字节标签联合体

`TVMFFIAny` 是 FFI 的核心动态类型，定义于 `include/tvm/ffi/c_api.h`，是一个 16 字节的栈上标签联合体 [F-112]。其内存布局为：

```text
┌─────────────────────────────────────────────────────┐
│ type_index (int32_t) │ padding/small_str_len (u32)  │
├─────────────────────────────────────────────────────┤
│ 8 字节值联合体（v_int64 / v_float64 / v_ptr /       │
│   v_obj / v_dtype / v_device / v_bytes[8] ...）     │
└─────────────────────────────────────────────────────┘
```

type_index 的值决定了 8 字节值联合体的解释方式：
- **type_index < 64（kTVMFFIStaticObjectBegin）**：栈上 POD 类型，无堆分配和引用计数。包括 None(0)、Int(1)、Bool(2)、Float(3)、OpaquePtr(4)、DataType(5)、Device(6)、DLTensorPtr(7)、RawStr(8)、SmallStr(11)、SmallBytes(12) 等 [F-042]。
- **type_index >= 64**：堆分配的引用计数对象，v_obj 字段持有 `TVMFFIObject*` 指针。内置对象类型从 64 开始：Object(64)、Str(65)、Bytes(66)、Error(67)、Function(68)、Shape(69)、Tensor(70)、Array(71)、Map(72)、Module(73)、List(75)、Dict(76) [F-043]。

小字符串优化（SmallStr）允许长度不超过 7 字节的字符串直接存储在 Any 的 8 字节值联合体中，长度存于 `small_str_len` 字段，无需堆分配 [F-115]。`zero_padding` 字段必须清零（小字符串除外），此不变量使 Any 值可直接进行字节比较和哈希 [F-114]。

C++ 端提供两种语义类型：`Any` 是拥有所有权的值类型（析构时释放引用），`AnyView` 是借用引用（不增减引用计数）。两者内存布局相同但所有权语义不同，借用 AnyView 转拥有 Any 需调用 `TVMFFIAnyViewToOwnedAny` [F-116][F-117]。

### TVMFFIObject：24 字节对象头

所有堆分配的 FFI 对象均以 `TVMFFIObject` 作为头部，这是一个 24 字节的 C 结构体 [F-020]：

```c
struct TVMFFIObject {
    uint64_t combined_ref_count;  // 低32位强引用，高32位弱引用
    int32_t  type_index;          // 运行时类型索引
    uint32_t __padding;
    union {
        void (*deleter)(TVMFFIObject*);
        uint64_t __ensure_align;
    };
};
```

强引用计数和弱引用计数打包在单个 `uint64_t` 中——低 32 位为强引用，高 32 位为弱引用 [F-021]。这种合并设计允许通过一次原子操作完成引用计数的增减，而非删除时分别读取强/弱计数，在多线程场景下减少缓存争用 [F-022]。删除器标志位控制析构和内存释放行为：强引用归零时调用析构函数但不释放内存（kDeleterStrong），弱引用归零时释放内存块（kDeleterWeak），两者都执行是最常见情况（kDeleterBoth）[F-054]。

### TVMFFIFunction：统一函数调用约定

`FunctionObj` 继承自 Object，类型索引为 68（kTVMFFIFunction）[F-063]。其核心是一个函数指针 `FCall`，签名为 [F-064]：

```cpp
void (*FCall)(const FunctionObj* self, const AnyView* args,
              int32_t nargs, Any* rv);
```

所有跨语言函数调用均遵循此约定：参数通过 `AnyView*` 数组传递，返回值写入 `Any*`。C++ 端同时支持异常路径（`cpp_call`）和安全调用路径（`safe_call`），`CallPacked` 优先使用 cpp_call，若为空则通过 `CppCallDedirectToSafeCall` 转发到 safe_call [F-065]。

所有 C ABI 函数返回 int，0 表示成功，-1 表示错误。错误信息不通过返回值传递，而是通过 thread-local 的 `SafeCallContext` 传递 [F-140]。`TVM_FFI_SAFE_CALL_BEGIN()`/`TVM_FFI_SAFE_CALL_END()` 宏包裹 C ABI 函数体，捕获 `tvm::ffi::Error` 和 `std::exception`，设置 raised error 并返回 -1 [F-066]。

## 全局函数注册表

`GlobalFunctionTable` 是 FFI 运行时可扩展性的核心，定义于 `src/ffi/function.cc`，内部使用 `Map<String, Any> table_` 存储命名函数 [F-068]。任何语言均可在运行时注册函数供其他语言调用：

- **C++ 端**：通过 `TVM_FFI_STATIC_INIT_BLOCK()` 宏和 `refl::GlobalDef()` 在静态初始化阶段注册 [F-056]。`.def(name, func)` 注册普通函数，`.def_packed(name, packed_func)` 注册 PackedArgs 风格函数，`.def_method(name, method)` 注册方法。
- **C ABI**：`TVMFFIFunctionSetGlobal` 注册命名全局函数，override 参数控制是否允许覆盖 [F-073]。`TVMFFIFunctionGetGlobal` 按名查找 [F-074]。
- **Python 端**：`@register_global_func` 装饰器可带函数名或直接使用函数名，`override` 参数控制覆盖行为 [F-083]。
- **Rust 端**：通过 `AsPackedCallable` trait 支持闭包自动转换为 Function。

全局函数注册默认不允许重名，`can_override=false` 时重复注册抛出 RuntimeError [F-070]。`GlobalFunctionTable::Global()` 使用 `new` 故意泄漏单例，原因是函数可能包含宿主语言（如 Python）回调，需避免析构顺序和 fork 问题 [F-071]。

注册表机制使 TVM 实现了真正的运行时可扩展性：新的 Target 后端通过注册 `"target.build."+kind` 全局函数接入编译流水线，新的 Pass 可动态注册，新的 DeviceAPI 可通过 `"device_api.xxx"` 注册。

## 类型系统与反射

### TypeTable：全局类型注册表

`TypeTable` 类管理所有 FFI 对象类型的运行时类型信息 [F-035]。每个类型条目（Entry）继承自 `TVMFFITypeInfo`，存储 type_key（类型字符串）、type_ancestors（祖先链）、type_fields（字段信息）、type_methods（方法信息）、metadata（元数据）等 [F-036]。

类型索引分配采用三级策略 [F-038]：
1. **静态索引**（≥64）：内置类型在编译时确定。
2. **父类槽位池**：若父类声明了 `_type_child_slots`，子类从预留槽位中分配。type_index 在 `[type_index, type_index+slots]` 范围内即可 O(1) 判定子类 [F-031]。
3. **动态溢出区**（≥128，kTVMFFIDynObjectBegin）：父类槽位用尽时从动态区分配。

`Object::IsInstance<TargetType>()` 不依赖 C++ RTTI，而是通过 type_index 和 `_type_child_slots` 范围检查实现运行时类型识别 [F-024]。这使得 TVM 可在 `-fno-rtti` 模式下编译，对嵌入式部署友好。

### 反射系统

反射系统核心头文件位于 `include/tvm/ffi/reflection/`，包含 registry.h、accessor.h、creator.h 等 [F-158]。`TVMFFITypeInfo` 结构体包含 type_index、type_depth、type_key、fields、methods、metadata 等完整反射信息 [F-159]：

- **字段**（`TVMFFIFieldInfo`）：name、type_index、offset、getter、setter、flags、default_value。字段标志位支持"setter 是 FunctionObj"（需 any_pool_ 保活）、"有默认值"、"结构相等/哈希中忽略"、"进入 def region"等 [F-160][F-163~F-166]。
- **方法**（`TVMFFIMethodInfo`）：name、method（TVMFFIAny）、flags、metadata [F-161]。
- **元数据**（`TVMFFITypeMetadata`）：total_size、structural_eq_hash_kind、creator、doc [F-162]。

C++ 端通过 `refl::ObjectDef<T>()` 注册对象类型的反射信息，`.def_field()`/`.def_ro()` 注册字段，`.def_method()` 注册方法 [F-167]。`refl::TypeAttrDef<T>().def(attr_name, value)` 注册类型属性（如 kConvert、kSEqual、kSHash）[F-168]。

反射系统支撑了一系列通用能力：`dataclass.cc` 实现了基于反射的 DeepCopy（深拷贝）、ReprPrint（表示打印）、RecursiveHash（递归哈希）、RecursiveEq（递归比较）[F-171]。最大遍历栈深度为 `1<<20`（约 100 万），防止恶意构造的深层循环结构导致栈溢出 [F-172]。

## 容器系统

FFI 提供一套完整的容器类型，全部继承自 Object，可被 Any 持有和跨语言传递 [F-087]：

| 容器 | 可变性 | 类型索引 | 说明 |
|------|--------|---------|------|
| `Array<T>` | 不可变 | 71 | 函数式序列，COW 修改 |
| `List<T>` | 可变 | 75 | 支持 push_back/erase/ReplaceSlice |
| `Map<K,V>` | 不可变 | 72 | 有序映射 |
| `Dict` | 可变 | 76 | 可变映射 |
| `String` | 不可变 | 65 | 内联字符串优化（短字符串内联） |
| `Bytes` | 不可变 | 66 | 字节串 |
| `Shape` | 不可变 | 69 | int64 数组 |
| `Tensor` | — | 70 | DLPack 互操作 |

Array 和 List 共享 `SeqBaseObj` 基类，Map 和 Dict 共享 `MapBaseObj` [F-090][F-091]。序列容器的公共 C 结构体为 `TVMFFISeqCell`，包含 data 指针、size、capacity 和可选的 data_deleter。当 data_deleter 为 nullptr 时，data 内联在对象分配中（如 ArrayObj 通过 `make_inplace_array_object`）；非 null 时 data 单独分配（如 ListObj 堆缓冲区）[F-088][F-089]。

Map/Dict 提供 `ForwardIterFunctor` 返回三命令迭代器函数（0=取当前 key，1=取当前 value，2=前进），使迭代器可跨语言边界使用 [F-100]。`GetItemOrMissing` 方法在键不存在时返回静态的 `GetMissingObject()` 而非抛出异常，优化了查找性能 [F-101]。

## Cython Python 绑定

Python 绑定位于 `python/tvm_ffi/`，核心为 Cython 扩展 `core.pyx`，配套 `.pxi` 文件按功能拆分 [F-006]。包入口 `__init__.py` 在导入时会尝试先导入 torch 以避免 Windows + Python 3.12 + torch 2.9.0 场景下的符号冲突 [F-012]，随后通过 `libinfo.load_lib_ctypes("apache-tvm-ffi", "tvm_ffi", "RTLD_GLOBAL")` 加载核心 C 动态库 [F-013]。

`_ffi_api.py` 通过 `_FFI_INIT_FUNC("ffi", __name__)` 自动绑定所有 `ffi.*` 全局函数为模块属性，包括 Array/List/Map/Dict/Shape 构造函数、StructuralEqual/Hash、Module 操作、序列化等约 80 个 FFI 函数 [F-085][F-086]。

`register_object` 装饰器将 Python 类注册到 C++ 类型键，要求 type_key 已在 C++ 端注册。它默认从 C++ `__ffi_init__` TypeAttrColumn 获取并安装 `__init__` 方法 [F-084]。Python 端 Array 类注册为 `"ffi.Array"`，继承 CContainerBase、Object、Sequence[T]，支持整数索引和切片（切片返回 Python list），序列相等性比较会将普通 Python 序列转换为同类 FFI 容器进行结构化比较 [F-103~F-106]。

## Rust 绑定

Rust 绑定包含两个 crate [F-008][F-014]：
- **tvm-ffi-sys**：原始 FFI 绑定（unsafe extern "C" 声明）。
- **tvm-ffi**：高级安全绑定，在 `rust/tvm-ffi/src/lib.rs` 通过 `pub use tvm_ffi_sys` 重新导出 sys 层类型。

Rust 端的关键类型包括 [F-057~F-062][F-079~F-082]：
- `Object`：`#[repr(C)]` 结构体，包含 `header: TVMFFIObject` 字段。
- `ObjectArc<T: ObjectCore>`：类似 Arc 的共享所有权智能指针，内部为 `std::ptr::NonNull<T>`，实现 Send/Sync，原生实现引用计数增减（使用 AtomicU64 的 fetch_add/fetch_sub）。
- `ObjectCore`：unsafe trait，要求关联常量 `TYPE_KEY`、函数 `type_index()` 和 `object_header_mut()`。
- `AnyView<'a>`：`#[derive(Copy, Clone)]` 的非拥有引用，带生命周期参数。
- `Any`：拥有所有权的类型，无生命周期参数。
- `Function`：`call_packed` 调用 safe_call 函数指针，返回 `Result<Any>`；`call_tuple` 使用小向量优化（STACK_LEN=4），参数数不超过 4 时使用栈数组。

Rust 端通过 `#[derive(Object)]` 过程宏自动生成对象样板代码，`CallbackFunctionObjImpl<F>` 在 FunctionObj 后跟泛型回调 F，通过 `invoke_callback` extern "C" 函数桥接 [F-080]。collections 模块包含 array、map、shape、tensor 四个子模块 [F-110]。

## Module 动态加载

FFI 的 Module 系统（`include/tvm/ffi/extra/module.h`）支持动态库加载和嵌入式库二进制 [F-141]。`ModuleObj::GetFunction(name, query_imports)` 支持查询导入链——先查自身，再递归遍历 imports_ 列表 [F-142]。`ImportModule` 使用 DFS 遍历检测循环依赖 [F-143]。

`Module::LoadFromFile` 根据文件扩展名选择加载器（dll/dylib/dso 统一为 so），加载器函数名为 `ffi.Module.load_from_file.<format>` [F-144]。`LibraryModuleObj` 是动态库模块实现，通过 `lib_->GetSymbolWithSymbolPrefix(name)` 查找符号，返回的闭包含有 `self_strong_ref`（Module 的强引用）以确保动态库在函数调用期间不被卸载 [F-148]。

嵌入式库二进制格式为：`<nbytes:u64> <import_tree> <key0:str>[<val0:bytes>]...`，其中 import_tree 使用 CSR 结构（indptr + child_indices）。`"_lib"` 键表示 LibraryModuleObj 的位置 [F-150][F-151]。`ContextSymbolRegistry` 全局注册上下文符号，库加载时通过 `InitContextSymbols` 将注册的符号地址写入库中对应符号位置，支持静态链接场景 [F-152]。

Module 属性掩码控制序列化行为：BINARY_SERIALIZABLE（0b001）、RUNNABLE（0b010）、COMPILATION_EXPORTABLE（0b100）[F-155]。Python 文档明确警告：模块内函数返回的对象其析构函数属于库代码，必须在模块卸载前销毁所有返回对象，否则会调用无效地址 [F-156]。

## 相关概念

- [Object/Node/ObjectRef 对象系统](/concepts/02-object-system.md)
- [TVM 整体架构与编译流水线](/concepts/00-overview.md)
