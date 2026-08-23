---
type: Facts
title: TVM-FFI 事实清单
description: 从 TVM-FFI 0.1.13 源码采集的跨语言互操作层事实，涵盖 C ABI、C++ 核心、Cython Python 绑定与 Rust 绑定
tags: [tvm, ffi, c-abi, cython, rust, facts, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
source_id: tvm-ffi
---

# TVM-FFI 事实清单

> 采集自 TVM-FFI 子项目源码，零推测，每条标注文件路径与行号。
> 项目路径：`d:\AI\.chaos\libs\ffi\tvm-ffi\`

## 1. 架构概览

1. TVM-FFI 当前版本号为 0.1.13，定义于 `include/tvm/ffi/c_api.h:61-65`（`TVM_FFI_VERSION_MAJOR=0`, `MINOR=1`, `PATCH=13`）。
2. 公共头文件根目录为 `include/tvm/ffi/`，而非 `include/ffi/`（见目录结构 `include/tvm/ffi/`）。
3. C++ 核心实现位于 `src/ffi/`，包含 object.cc、function.cc、container.cc、error.cc、dtype.cc、tensor.cc、init_once.cc、backtrace.cc 八个源文件。
4. C++ 扩展功能位于 `src/ffi/extra/`，包含 module.cc、library_module.cc、dataclass.cc、serialization.cc、json_parser.cc、json_writer.cc、structural_equal.cc、structural_hash.cc、reflection_extra.cc。
5. 公共头文件按功能分子目录：`container/`（容器）、`extra/`（扩展）、`reflection/`（反射），根目录含 any.h、object.h、function.h、c_api.h、error.h、string.h、dtype.h 等。
6. Python 绑定位于 `python/tvm_ffi/`，核心 Cython 扩展为 `core.pyx`，配套 `.pxi` 文件按功能拆分（base/object/function/error/string/tensor/dtype 等）。
7. Python 包还包含 `dataclasses/`（dataclass 支持）、`stub/`（类型存根生成）、`cython/`（Cython 绑定源码）、`cpp/`（C++ 工具子模块）、`testing/`（测试工具）、`utils/`（工具函数）。
8. Rust 绑定位于 `rust/tvm-ffi/`（高级绑定）和 `rust/tvm-ffi-sys/`（原始 FFI 绑定），Rust 模块包括 any、collections（array/map/shape/tensor）、derive、device、dtype、error、extra（module）、function、function_internal、macros、object、optional、string、type_traits。
9. 文档使用 Sphinx + reStructuredText，位于 `docs/`，分为 concepts/（概念）、guides/（指南）、get_started/（入门）、dev/（开发）、packaging/（打包）、reference/（API 参考）。
10. ABI 设计四大原则：最小高效、跨编译器版本稳定、ML 原生支持（tensor/shape/dtype）、可扩展动态类型注册，见 `docs/concepts/abi_overview.rst:28-33`。
11. TVM-FFI 不依赖 C++ RTTI 进行运行时类型识别，而是使用自定义 type_index 系统，见 `docs/concepts/abi_overview.rst:78-79`。
12. Python 包入口 `__init__.py` 在导入时会尝试先导入 torch 以避免符号冲突（Windows + Python 3.12 + torch 2.9.0 场景），见 `python/tvm_ffi/__init__.py:43-52`。
13. Python 包通过 `libinfo.load_lib_ctypes("apache-tvm-ffi", "tvm_ffi", "RTLD_GLOBAL")` 加载核心 C 动态库，见 `python/tvm_ffi/__init__.py:57`。
14. Rust 高级绑定 crate 名为 `tvm-ffi`，原始 sys crate 名为 `tvm-ffi-sys`，在 `rust/tvm-ffi/src/lib.rs:33` 通过 `pub use tvm_ffi_sys` 重新导出。
15. C++ 命名空间统一为 `tvm::ffi`，反射子命名空间为 `tvm::ffi::reflection`，见 `src/ffi/object.cc:46-47` 和 `src/ffi/extra/module.cc:165`。
16. 所有 C ABI 函数使用 `extern "C"` 声明，见 `include/tvm/ffi/c_api.h:68-70`。
17. DLL 导出/导入宏 `TVM_FFI_DLL` 和 `TVM_FFI_DLL_EXPORT` 支持 MSVC、GCC/Clang（visibility）和 Emscripten（EMSCRIPTEN_KEEPALIVE），见 `include/tvm/ffi/c_api.h:41-57`。

## 2. Object 系统

18. `Object` 基类定义于 `include/tvm/ffi/object.h:127`，所有 FFI 对象继承此类，包含 protected 成员 `TVMFFIObject header_`（object.h:130）。
19. `Object` 构造函数将 `combined_ref_count`、`type_index`、`__padding`、`__ensure_align` 全部初始化为 0，见 `include/tvm/ffi/object.h:133-138`。
20. `TVMFFIObject` 是 24 字节的 C 结构体头，定义于 `include/tvm/ffi/c_api.h:233-279`，包含 `combined_ref_count`（uint64_t）、`type_index`（int32_t）、`__padding`（uint32_t）、以及 `deleter`/`__ensure_align` 联合体。
21. 强引用计数打包在 `combined_ref_count` 的低 32 位，弱引用计数打包在高 32 位，见 `include/tvm/ffi/c_api.h:237-248`。
22. 使用合并引用计数的原因是可通过一次 u64 原子操作完成，而非删除时分别读取强/弱计数，见 `include/tvm/ffi/c_api.h:246-248`。
23. `kCombinedRefCountWeakOne = 1ULL << 32`，`kCombinedRefCountStrongOne = 1`，`kCombinedRefCountBothOne` 为两者按位或，定义于 `include/tvm/ffi/object.h:62-66`。
24. `Object::IsInstance<TargetType>()` 模板方法通过 `details::IsObjectInstance<TargetType>(header_.type_index)` 检查类型，不依赖 C++ RTTI，见 `include/tvm/ffi/object.h:144-147`。
25. `Object::type_index()` 返回运行时类型索引（int32_t），见 `include/tvm/ffi/object.h:150`。
26. `Object::GetTypeKey()` 通过 `TVMFFIGetTypeInfo` 查询类型表获取类型字符串，标注为昂贵操作仅用于错误报告，见 `include/tvm/ffi/object.h:156-160`。
27. `Object::GetTypeKeyHash()` 返回类型键的哈希值（uint64_t），见 `include/tvm/ffi/object.h:165-169`。
28. `Object::use_count()` 返回强引用计数，MSVC 使用 volatile 读取，其他平台使用 `__atomic_load_n` with `__ATOMIC_RELAXED`，见 `include/tvm/ffi/object.h:190-200`。
29. `Object::unique()` 当 `use_count() == 1` 时返回 true，见 `include/tvm/ffi/object.h:184`。
30. 子类需声明静态字段 `_type_index`、`_type_key`、`_type_final`、`_type_mutable`，以及可子类化时需声明 `_type_child_slots` 和 `_type_child_slots_can_overflow`，见 `include/tvm/ffi/object.h:88-118`。
31. `_type_child_slots` 为子类预留类型索引槽位数，用于 IsInstance 快速检查；若对象 type_index 在 `[type_index, type_index + _type_child_slots]` 范围内即可快速判定为子类，见 `include/tvm/ffi/object.h:107-113`。
32. `TVM_FFI_DECLARE_OBJECT_INFO` 宏用于可子类化的对象类型，`TVM_FFI_DECLARE_OBJECT_INFO_FINAL` 用于终态类型（不可子类化），见 `include/tvm/ffi/object.h:120-122`。
33. `make_object<T>(args...)` 函数创建对象并自动填充 type_index 和 deleter，见 `include/tvm/ffi/object.h:124-125`。
34. `UnsafeInit` 标签结构体允许 ObjectRef 字段在构造时先设为 nullptr 再赋值，用于无默认构造函数的对象，见 `include/tvm/ffi/object.h:54`。
35. `TypeTable` 类是全局类型注册表，定义于 `src/ffi/object.cc:60`，内部使用 `std::vector<std::unique_ptr<Entry>>` 存储类型条目。
36. `TypeTable::Entry` 继承自 `TVMFFITypeInfo`，额外存储 `type_key_data`（String）、`type_ancestors_data`（祖先信息向量）、`type_fields_data`（字段信息）、`type_methods_data`（方法信息）、`metadata_data`，见 `src/ffi/object.cc:63-73`。
37. `TypeTable` 不使用互斥锁保护更新，假设更新发生在主线程初始化/加载阶段或由调用方显式加锁，见 `src/ffi/object.cc:52-58`。
38. 类型索引分配策略：优先使用静态索引（`static_type_index >= 0`），其次从父类预留槽位池分配，最后从动态溢出区分配（`type_counter_` 起始于 `kTVMFFIDynObjectBegin=128`），见 `src/ffi/object.cc:143-173`。
39. 动态类型索引起始值为 `kTVMFFIDynObjectBegin = 128`，定义于 `include/tvm/ffi/c_api.h:188`。
40. 静态对象类型索引起始值为 `kTVMFFIStaticObjectBegin = 64`，定义于 `include/tvm/ffi/c_api.h:132`。
41. `TypeTable` 构造函数预留 `kTVMFFIDynObjectBegin` 个槽位，并注册 Object 及所有内置静态类型，见 `src/ffi/object.cc:387-431`。
42. 内置 POD 类型索引：kTVMFFINone=0、kTVMFFIInt=1、kTVMFFIBool=2、kTVMFFIFloat=3、kTVMFFIOpaquePtr=4、kTVMFFIDataType=5、kTVMFFIDevice=6、kTVMFFIDLTensorPtr=7、kTVMFFIRawStr=8、kTVMFFIByteArrayPtr=9、kTVMFFIObjectRValueRef=10、kTVMFFISmallStr=11、kTVMFFISmallBytes=12，见 `include/tvm/ffi/c_api.h:106-130`。
43. 内置对象类型索引：kTVMFFIObject=64、kTVMFFIStr=65、kTVMFFIBytes=66、kTVMFFIError=67、kTVMFFIFunction=68、kTVMFFIShape=69、kTVMFFITensor=70、kTVMFFIArray=71、kTVMFFIMap=72、kTVMFFIModule=73、kTVMFFIOpaquePyObject=74、kTVMFFIList=75、kTVMFFIDict=76、kTVMFFIVisitInterrupt=77，见 `include/tvm/ffi/c_api.h:137-181`。
44. `kTVMFFIAny = -1` 是根类型标记，不会出现在 `Any::type_index` 中，但可能出现在反射字段注解中，见 `include/tvm/ffi/c_api.h:97`。
45. `RegisterTypeField` 检查字段名在类型自身字段中不重复，但对祖先字段重名仅输出警告到 stderr，见 `src/ffi/object.cc:220-241`。
46. 当字段 setter 是 FunctionObj 时，通过 `any_pool_` 持有引用以确保其生命周期超过 Entry，见 `src/ffi/object.cc:243-251`。
47. `TypeTable` 支持类型属性列（TypeAttrColumn），按列存储稀疏属性值，通过 `RegisterTypeAttr` 和 `GetTypeAttrColumn` 访问，见 `src/ffi/object.cc:118-120` 和 `src/ffi/object.cc:295-340`。
48. `RegisterTypeMetadata` 不允许重复注册同一类型的元数据，重复时抛出 RuntimeError 并列出可能原因（两次 ObjectDef、忘记设置 _type_key、同 key 类型已注册），见 `src/ffi/object.cc:280-293`。
49. `OpaqueObjectImpl` 继承自 `Object` 和 `TVMFFIOpaqueObjectCell`，包装外部句柄和删除器，析构时调用 deleter，见 `src/ffi/object.cc:484-502`。
50. `TVMFFIObjectCreateOpaque` 当前仅支持 `kTVMFFIOpaquePyObject` 类型索引，见 `src/ffi/object.cc:535-549`。
51. `GetMissingObject()` 返回一个静态的空 Object 实例，用于表示 Map/Dict 中缺失的键，见 `src/ffi/object.cc:504-507`。
52. `GetKwargsObject()` 返回一个静态的空 Object 实例，用于标记关键字参数，见 `src/ffi/object.cc:509-512`。
53. C ABI 函数 `TVMFFIObjectIncRef`/`TVMFFIObjectDecRef` 分别调用 `ObjectUnsafe::IncRefObjectHandle`/`DecRefObjectHandle`，见 `src/ffi/object.cc:523-533`。
54. 删除器标志位：`kTVMFFIObjectDeleterFlagBitMaskStrong`（强引用归零时调用析构函数但不释放内存）、`kTVMFFIObjectDeleterFlagBitMaskWeak`（弱引用归零时释放内存块）、`kTVMFFIObjectDeleterFlagBitMaskBoth`（两者都执行，最常见），见 `include/tvm/ffi/c_api.h:203-227`。
55. `TypeTable::Global()` 使用 `new TypeTable()` 而非静态局部对象，故意泄漏以确保表在卸载场景下存活更久，内存由 OS 在程序退出时回收，见 `src/ffi/object.cc:377-384`。
56. 静态初始化块通过 `TVM_FFI_STATIC_INIT_BLOCK()` 宏注册内置类型的转换函数、EnumObj 字段和全局函数，见 `src/ffi/object.cc:624-669`。
57. Rust 端 `Object` 结构体为 `#[repr(C)]`，包含 `header: TVMFFIObject` 字段，见 `rust/tvm-ffi/src/object.rs:28-32`。
58. Rust 端 `ObjectArc<T: ObjectCore>` 是类似 Arc 的共享所有权智能指针，内部为 `std::ptr::NonNull<T>`，见 `rust/tvm-ffi/src/object.rs:38-41`。
59. Rust 端 `ObjectCore` 是 unsafe trait，要求关联常量 `TYPE_KEY`、函数 `type_index()` 和 `object_header_mut()`，见 `rust/tvm-ffi/src/object.rs:50-65`。
60. Rust 端 `ObjectCoreWithExtraItems` trait 支持对象后跟额外数组项（用于 Array/String 等类型），见 `rust/tvm-ffi/src/object.rs:70-91`。
61. Rust 端 `ObjectRefCore` trait 定义 ObjectRef 的核心操作：`data()`、`into_data()`、`from_data()`，关联类型 `ContainerType: ObjectCore`，见 `rust/tvm-ffi/src/object.rs:98-103`。
62. Rust 端原生实现引用计数增减（`inc_ref`/`dec_ref`），使用 `AtomicU64` 的 `fetch_add`/`fetch_sub`，等价于 C 端 `TVMFFIObjectIncRef`/`DecRef`，见 `rust/tvm-ffi/src/object.rs:136-149`。

## 3. Function 与注册表

63. `FunctionObj` 继承自 `Object` 和 `TVMFFIFunctionCell`，定义于 `include/tvm/ffi/function.h:113`，类型索引为 `kTVMFFIFunction=68`。
64. `FunctionObj::FCall` 是 C++ 风格异常传播的函数指针类型：`void (*)(const FunctionObj*, const AnyView*, int32_t, Any*)`，见 `include/tvm/ffi/function.h:116`。
65. `FunctionObj::CallPacked` 优先使用 `cpp_call`（C++ 异常路径），若为空则通过 `CppCallDedirectToSafeCall` 转发到 `safe_call`（C 错误码路径），见 `include/tvm/ffi/function.h:125-131`。
66. `TVM_FFI_SAFE_CALL_BEGIN()` / `TVM_FFI_SAFE_CALL_END()` 宏包裹 C ABI 函数体，捕获 `tvm::ffi::Error` 和 `std::exception`，设置 raised error 并返回 -1，成功返回 0，见 `include/tvm/ffi/function.h:72-90`。
67. `TVM_FFI_CHECK_SAFE_CALL(func)` 宏调用 safe_call 并在返回非零时抛出从 raised error 移动构造的 C++ 异常，见 `include/tvm/ffi/function.h:101-107`。
68. `GlobalFunctionTable` 是全局函数注册表，定义于 `src/ffi/function.cc:51`，内部使用 `Map<String, Any> table_` 存储。
69. `GlobalFunctionTable::Entry` 继承自 `Object` 和 `TVMFFIMethodInfo`，存储 `name_data`、`doc_data`、`metadata_data`、`func_data`（Function），见 `src/ffi/function.cc:55-60`。
70. 全局函数注册默认不允许重名，`can_override=false` 时重复注册抛出 RuntimeError，见 `src/ffi/function.cc:85-92`。
71. `GlobalFunctionTable::Global()` 同样使用 `new` 故意泄漏，原因是函数可能包含宿主语言（Python）回调，需避免析构顺序和 fork 问题，见 `src/ffi/function.cc:130-138`。
72. `TVMFFIFunctionCreate` 从 extern C 函数指针（self、safe_call、deleter）创建 Function 对象，见 `src/ffi/function.cc:146-152`。
73. `TVMFFIFunctionSetGlobal` 注册命名全局函数，`override` 参数控制是否允许覆盖，见 `src/ffi/function.cc:161-168`。
74. `TVMFFIFunctionGetGlobal` 按名查找全局函数，未找到时 `*out = nullptr`，见 `src/ffi/function.cc:177-189`。
75. `TVMFFIFunctionCall` 是核心调用函数，在 MSVC 上使用 `volatile int ret` 防止尾调用优化（需要此函数符号在调用帧中以可靠检测 FFI 边界），其他平台为尾调用，见 `src/ffi/function.cc:191-204`。
76. `TVMFFIAnyViewToOwnedAny` 将借用的 AnyView 转换为拥有所有权的 Any，见 `src/ffi/function.cc:154-159`。
77. 静态初始化注册的全局函数包括：`ffi.FunctionRemoveGlobal`、`ffi.FunctionListGlobalNamesFunctor`、`ffi.String`、`ffi.Bytes`、`ffi.GetGlobalFuncMetadata`、`ffi.FunctionFromExternC`，见 `src/ffi/function.cc:206-245`。
78. `ffi.FunctionListGlobalNamesFunctor` 返回一个闭包函数而非数组，以避免在 array FFI 函数可用前列表全局函数名的依赖问题，见 `src/ffi/function.cc:213-229`。
79. Rust 端 `FunctionObj` 使用 `#[repr(C)]` 和 derive 宏 `#[derive(Object)]`，标注 `#[type_key = "ffi.Function"]` 和 `#[type_index(TVMFFITypeIndex::kTVMFFIFunction)]`，见 `rust/tvm-ffi/src/function.rs:30-37`。
80. Rust 端 `CallbackFunctionObjImpl<F>` 在 FunctionObj 后跟泛型回调 F，通过 `invoke_callback` extern "C" 函数桥接，见 `rust/tvm-ffi/src/function.rs:53-94`。
81. Rust 端 `Function::call_packed` 调用 `safe_call` 函数指针，返回 `Result<Any>`，错误时调用 `Error::from_raised()`，见 `rust/tvm-ffi/src/function.rs:108-124`。
82. Rust 端 `Function::call_tuple` 使用小向量优化（STACK_LEN=4），参数数 ≤4 时使用栈数组，超过时堆分配，见 `rust/tvm-ffi/src/function.rs:126-150`。
83. Python 端 `register_global_func` 装饰器可带函数名或直接使用函数名，`override` 参数控制是否覆盖已有注册，见 `python/tvm_ffi/registry.py:110-150`。
84. Python 端 `register_object` 装饰器注册 Object 子类，要求 type_key 已在 C++ 端注册；默认安装 `__init__`（从 C++ `__ffi_init__` TypeAttrColumn 获取），见 `python/tvm_ffi/registry.py:37-107`。
85. Python 端 `_ffi_api.py` 通过 `_FFI_INIT_FUNC("ffi", __name__)` 自动绑定所有 `ffi.*` 全局函数为模块属性，见 `python/tvm_ffi/_ffi_api.py:37`。
86. `_ffi_api.py` 中自动生成的函数包含 Array、List、Map、Dict、Shape 等容器构造函数，以及 StructuralEqual/Hash、Module 操作、序列化等，共约 80 个 FFI 函数，见 `python/tvm_ffi/_ffi_api.py:39-124`。

## 4. 容器系统

87. 容器类型包括 Array（不可变序列）、List（可变序列）、Map（不可变有序映射）、Dict（可变映射）、String、Bytes、Shape、Tensor、Tuple、Variant，分别定义于 `include/tvm/ffi/container/` 子目录。
88. `TVMFFISeqCell` 是序列容器的公共 C 结构体，包含 `data`（void*）、`size`（int64_t）、`capacity`（int64_t）、`data_deleter`（可选的缓冲区删除器），见 `include/tvm/ffi/c_api.h:373-399`。
89. 当 `data_deleter` 为 nullptr 时，data 内联在对象分配中（如 ArrayObj 通过 `make_inplace_array_object`）；非 null 时 data 单独分配（如 ListObj 堆缓冲区），见 `include/tvm/ffi/c_api.h:386-393`。
90. `ArrayObj` 和 `ListObj` 均继承自 `SeqBaseObj`，见 `src/ffi/container.cc:53-54`。
91. `MapObj` 和 `DictObj` 均继承自 `MapBaseObj`，见 `src/ffi/container.cc:61-62`。
92. Array/Map 是不可变的（函数式风格），List/Dict 是可变的，通过 C++ 端的 `Set`、`push_back`、`erase` 等方法修改。
93. `ffi.Array` 全局工厂函数接受任意数量的 Any 参数构造 `Array<Any>`，见 `src/ffi/container.cc:107-110`。
94. `ffi.List` 全局工厂函数同理构造 `List<Any>`，见 `src/ffi/container.cc:120-123`。
95. `ffi.Map` 全局工厂函数接受偶数个参数（key-value 交替），检查 `args.size() % 2 == 0`，见 `src/ffi/container.cc:176-184`。
96. `ffi.Dict` 全局工厂函数同 Map 但构造可变 Dict，见 `src/ffi/container.cc:204-212`。
97. List 支持完整的可变操作：SetItem、Append、Insert、Pop（返回值并删除）、Erase、EraseRange、ReplaceSlice、Reverse、Clear，见 `src/ffi/container.cc:125-175`。
98. `ListReplaceSlice` 在源和替换目标别名同一对象时先快照替换内容，防止迭代器失效，见 `src/ffi/container.cc:153-167`。
99. Dict 支持 SetItem、Erase、Clear 等可变操作，见 `src/ffi/container.cc:216-223`。
100. Map/Dict 提供 `ForwardIterFunctor` 返回一个三命令迭代器函数（0=取当前 key，1=取当前 value，2=前进并返回是否成功），见 `src/ffi/container.cc:76-100` 和 `src/ffi/container.cc:192-195`。
101. `GetItemOrMissing` 方法在键不存在时返回 `GetMissingObject()` 而非抛出异常，见 `src/ffi/container.cc:196-203` 和 `src/ffi/container.cc:228-235`。
102. `ContainerFindFirstNonCPUDevice` 递归扫描 Any 元素中的第一个非 CPU tensor 设备，支持 Array/List/Map/Dict 嵌套，见 `src/ffi/container.cc:42-72` 和 `src/ffi/container.cc:236-240`。
103. Python 端 Array 类注册为 `"ffi.Array"`，继承 `CContainerBase`、`Object`、`Sequence[T]`，见 `python/tvm_ffi/container.py:140-141`。
104. Python 端 `getitem_helper` 支持整数索引和切片，切片返回 Python list，见 `python/tvm_ffi/container.py:91-124`。
105. Python 端 `normalize_index` 处理负索引和边界检查，行为与 Python list 一致，见 `python/tvm_ffi/container.py:127-137`。
106. Python 端序列相等性比较会将普通 Python 序列（非 str/bytes/Mapping）转换为同类 FFI 容器进行结构化比较，见 `python/tvm_ffi/container.py:54-63`。
107. String 和 Bytes 对象布局为 `{ TVMFFIObject, TVMFFIByteArray, ... }`，其中 `TVMFFIByteArray` 包含 `data`（const char*）和 `size`（size_t），见 `include/tvm/ffi/c_api.h:339-354`。
108. `MakeInplaceString` 创建内联字符串对象，字符串数据紧跟在 StringObj 之后，通过 `make_inplace_array_object<StringObj, char>(length+1)` 分配，见 `src/ffi/object.cc:442-453`。
109. Shape 对象布局为 `{ TVMFFIObject, { const int64_t*, size_t }, ... }`，见 `include/tvm/ffi/c_api.h:150-153`。
110. `ffi.Shape` 全局工厂函数接受 int64 参数列表，通过 `MakeEmptyShape` 分配并填充，见 `src/ffi/tensor.cc:33-44`。
111. Rust 端 collections 模块包含 array、map、shape、tensor 四个子模块，见 `rust/tvm-ffi/src/lib.rs:20` 和 `rust/tvm-ffi/src/collections/mod.rs`。

## 5. Any 动态类型

112. `TVMFFIAny` 是 16 字节的栈上标签联合体，定义于 `include/tvm/ffi/c_api.h:289-334`，包含 `type_index`（int32_t）、`zero_padding`/`small_str_len`（uint32_t 联合体）、以及 8 字节值联合体。
113. 8 字节值联合体支持：v_int64、v_float64、v_ptr、v_c_str、v_obj（TVMFFIObject*）、v_dtype（DLDataType）、v_device（DLDevice）、v_bytes[8]（小字符串）、v_uint64，见 `include/tvm/ffi/c_api.h:311-332`。
114. `zero_padding` 字段必须清零（小字符串除外），此不变量使 TVMFFIAny 值可直接进行字节比较和哈希，见 `docs/concepts/abi_overview.rst:94-97`。
115. 小字符串（kTVMFFISmallStr=11）最大长度为 7 字节，存储在 `v_bytes[8]` 中，长度存于 `small_str_len`，见 `include/tvm/ffi/c_api.h:300-306`。
116. C++ 端 `Any` 是拥有所有权的值类型，`AnyView` 是借用引用，两者内存布局相同但所有权语义不同，见 `docs/concepts/abi_overview.rst:60-66`。
117. Any 可表示拥有或借用引用；借用 AnyView 转拥有 Any 使用 `TVMFFIAnyViewToOwnedAny`，见 `docs/concepts/abi_overview.rst:68-69` 和 `src/ffi/function.cc:154-159`。
118. type_index < kTVMFFIStaticObjectBegin（64）为栈上 POD 类型，无堆分配和引用计数；type_index >= 64 为堆分配引用计数对象，见 `docs/concepts/abi_overview.rst:73-76`。
119. `kTVMFFIRawStr=8` 是 `\0` 结尾的 C 字符串，不由 Any 拥有；Any::type_index 永不为 kTVMFFIRawStr，但 AnyView::type_index 可以，见 `include/tvm/ffi/c_api.h:99-103`。
120. Rust 端 `AnyView<'a>` 是 `#[derive(Copy, Clone)]` 的非拥有引用，带生命周期参数 `'a`，见 `rust/tvm-ffi/src/any.rs:26-32`。
121. Rust 端 `Any` 是拥有所有权的类型，无生命周期参数，见 `rust/tvm-ffi/src/any.rs:35-38`。
122. Rust 端 `AnyView::try_as<T>()` 是严格类型检查（不尝试强制转换），通过 `T::check_any_strict` 和 `T::copy_from_any_view_after_check` 实现，见 `rust/tvm-ffi/src/any.rs:64-76`。
123. Rust 端 `AnyView::debug_strong_count()` 在 type_index >= kTVMFFIStaticObjectBegin 时返回底层对象的强引用计数，否则返回 None，见 `rust/tvm-ffi/src/any.rs:81-89`。
124. 从 Any/AnyView 提取 POD 值时可能发生隐式类型转换（如 int 转 float），见 `docs/concepts/abi_overview.rst:132-133`。

## 6. C ABI 稳定接口

125. 核心 C ABI 定义于 `include/tvm/ffi/c_api.h`，扩展 C ABI 定义于 `include/tvm/ffi/extra/c_env_api.h`，见 `docs/concepts/abi_overview.rst:23-26`。
126. C ABI 稳定性保证跨编译器版本稳定，独立于宿主语言或框架，见 `docs/concepts/abi_overview.rst:31`。
127. `TVMFFIVersion` 结构体包含 major/minor/patch 三个 uint32_t 字段，通过 `TVMFFIGetVersion` 获取，见 `include/tvm/ffi/c_api.h:75-82` 和 `src/ffi/object.cc:517-521`。
128. `TVMFFIObjectHandle` 是 `void*` 类型别名，作为 C API 中对象的不透明句柄，见 `include/tvm/ffi/c_api.h:197`。
129. 核心对象生命周期 C API：`TVMFFIObjectIncRef`、`TVMFFIObjectDecRef`、`TVMFFIObjectCreateOpaque`，见 `src/ffi/object.cc:523-549`。
130. 类型系统 C API：`TVMFFITypeKeyToIndex`、`TVMFFITypeGetOrAllocIndex`、`TVMFFIGetTypeInfo`、`TVMFFITypeRegisterField`、`TVMFFITypeRegisterMethod`、`TVMFFITypeRegisterMetadata`、`TVMFFITypeRegisterAttr`、`TVMFFIGetTypeAttrColumn`，见 `src/ffi/object.cc:551-603`。
131. 函数 C API：`TVMFFIFunctionCreate`、`TVMFFIFunctionSetGlobal`、`TVMFFIFunctionSetGlobalFromMethodInfo`、`TVMFFIFunctionGetGlobal`、`TVMFFIFunctionCall`，见 `src/ffi/function.cc:146-204`。
132. 错误 C API：`TVMFFIErrorSetRaised`、`TVMFFIErrorSetRaisedFromCStr`、`TVMFFIErrorSetRaisedFromCStrParts`、`TVMFFIErrorMoveFromRaised`、`TVMFFIErrorCreate`、`TVMFFIErrorCreateWithCauseAndExtraContext`，见 `src/ffi/error.cc:79-146`。
133. Tensor C API：`TVMFFITensorCreateUnsafeView`、`TVMFFITensorFromDLPack`、`TVMFFITensorFromDLPackVersioned`、`TVMFFITensorToDLPack`、`TVMFFITensorToDLPackVersioned`，见 `src/ffi/tensor.cc:50-111`。
134. DataType C API：`TVMFFIDataTypeFromString`、`TVMFFIDataTypeToString`，见 `src/ffi/dtype.cc:360-371`。
135. String/Bytes C API：`TVMFFIStringFromByteArray`、`TVMFFIBytesFromByteArray`，见 `src/ffi/object.cc:606-621`。
136. 初始化 C API：`TVMFFIHandleInitOnce`、`TVMFFIHandleDeinitOnce`，使用原子加载/存储和双检锁模式，见 `src/ffi/init_once.cc:59-94`。
137. Module C API：`TVMFFIEnvModLookupFromImports`、`TVMFFIEnvModRegisterContextSymbol`，见 `src/ffi/extra/module.cc:200-205` 和 `src/ffi/extra/library_module.cc:223-228`。
138. `TVMFFIHandleInitOnce` 使用 acquire 语义原子加载检查快速路径，加锁后二次检查，调用 init_func，最后用 release 语义原子存储结果，见 `src/ffi/init_once.cc:59-81`。
139. 弱符号宏 `TVM_FFI_WEAK` 在 MSVC 上为 `__declspec(selectany)`，在其他平台为 `__attribute__((weak))`，见 `include/tvm/ffi/c_api.h:31-35`。
140. 所有 C ABI 函数返回 int，0 表示成功，-1 表示错误（错误信息通过 thread-local SafeCallContext 传递）。

## 7. Module 系统

141. `ModuleObj` 是模块基类，继承自 Object，定义于 `include/tvm/ffi/extra/module.h`，类型索引为 `kTVMFFIModule=73`。
142. `ModuleObj::GetFunction(name, query_imports)` 支持查询导入链——先查自身，再递归遍历 imports_ 列表，见 `src/ffi/extra/module.cc:61-73`。
143. `ModuleObj::ImportModule` 使用 DFS 遍历检测循环依赖，检测到环时抛出 RuntimeError，见 `src/ffi/extra/module.cc:103-120`。
144. `Module::LoadFromFile` 根据文件扩展名选择加载器，扩展名映射规则：dll/dylib/dso 统一为 so，加载器函数名为 `ffi.Module.load_from_file.<format>`，见 `src/ffi/extra/module.cc:138-162`。
145. `ModuleGlobals` 单例管理运行时持有的模块（keep_alive=True），使用 `Map<Module, int>` 和 mutex 保护，见 `src/ffi/extra/module.cc:39-59`。
146. `LibraryModuleObj` 是动态库模块实现，继承自 ModuleObj，kind 返回 `"library"`，见 `src/ffi/extra/library_module.cc:36-40`。
147. `LibraryModuleObj` 的属性掩码为 `kBinarySerializable | kRunnable`，见 `src/ffi/extra/library_module.cc:43`。
148. `LibraryModuleObj::GetFunction` 通过 `lib_->GetSymbolWithSymbolPrefix(name)` 查找符号，返回的闭包含有 `self_strong_ref`（Module 的强引用）以确保动态库在函数调用期间不被卸载，见 `src/ffi/extra/library_module.cc:45-58`。
149. 函数元数据通过 `__tvm_ffi__metadata_<name>` 符号查找，函数文档通过 `__tvm_ffi__doc_<name>` 符号查找，见 `src/ffi/extra/library_module.cc:61-83`。
150. `ProcessLibraryBin` 解析嵌入式库二进制，格式为：`<nbytes:u64> <import_tree> <key0:str>[<val0:bytes>]...`，import_tree 使用 CSR 结构（indptr + child_indices），见 `src/ffi/extra/library_module.cc:109-163`。
151. 库二进制中 `"_lib"` 键表示 LibraryModuleObj 的位置，其他键为自定义模块类型的序列化字节，见 `src/ffi/extra/library_module.cc:138-152`。
152. `ContextSymbolRegistry` 全局注册上下文符号，库加载时通过 `InitContextSymbols` 将注册的符号地址写入库中对应符号位置，见 `src/ffi/extra/library_module.cc:166-193`。
153. `CreateLibraryModule` 检查库中是否存在 `tvm_ffi_library_bin` 和 `tvm_ffi_library_ctx` 符号，有嵌入二进制时反序列化，否则创建单一 LibraryModuleObj，见 `src/ffi/extra/library_module.cc:199-218`。
154. Python 端 Module 类注册为 `"ffi.Module"`，属性 `kind`、`imports_`、`entry_name="main"`，见 `python/tvm_ffi/module.py:50-117`。
155. Python 端 `ModulePropertyMask` 枚举：BINARY_SERIALIZABLE=0b001、RUNNABLE=0b010、COMPILATION_EXPORTABLE=0b100，见 `python/tvm_ffi/module.py:42-47`。
156. Python 文档警告：模块内函数返回的对象其析构函数属于库代码，必须在模块卸载前销毁所有返回对象，否则会调用无效地址，见 `python/tvm_ffi/module.py:80-107`。
157. Rust 端 Module 定义于 `rust/tvm-ffi/src/extra/module.rs`，通过 `pub mod extra` 导出，见 `rust/tvm-ffi/src/lib.rs:25,46`。

## 8. 反射与 Dataclass

158. 反射系统核心头文件位于 `include/tvm/ffi/reflection/`，包含 registry.h（注册表）、accessor.h（访问器）、creator.h（创建器）、access_path.h（访问路径）、enum_def.h（枚举定义）、overload.h（重载）。
159. `TVMFFITypeInfo` 结构体包含 type_index、type_depth、type_key（TVMFFIByteArray）、type_key_hash、type_ancestors、num_fields、fields、num_methods、methods、metadata 字段。
160. `TVMFFIFieldInfo` 描述反射字段：name、doc、、type_index、offset、getter、setter、flags、default_value_or_factory。
161. `TVMFFIMethodInfo` 描述反射方法：name、doc、metadata、method（TVMFFIAny）、flags。
162. `TVMFFITypeMetadata` 包含 total_size、structural_eq_hash_kind、creator、doc。
163. 字段标志位 `kTVMFFIFieldFlagBitSetterIsFunctionObj` 表示 setter 是 FunctionObj 而非普通函数指针，需通过 any_pool_ 保活，见 `src/ffi/object.cc:244-251`。
164. 字段标志位 `kTVMFFIFieldFlagBitMaskHasDefault` 表示字段有默认值，见 `src/ffi/object.cc:255-261`。
165. 字段标志位 `kTVMFFIFieldFlagBitMaskSEqHashIgnore` 标记字段在结构相等/哈希比较中忽略，见 `src/ffi/extra/structural_equal.cc:217`。
166. 字段标志位 `kTVMFFIFieldFlagBitMaskSEqHashDefRecursive` 和 `kTVMFFIFieldFlagBitMaskSEqHashDefNonRecursive` 标记字段进入 def region（用于 free var 绑定），见 `src/ffi/extra/structural_equal.cc:223-229`。
167. `refl::GlobalDef()` 返回全局函数注册构建器，`.def(name, func)` 注册普通函数，`.def_packed(name, packed_func)` 注册 PackedArgs 风格函数，`.def_method(name, method)` 注册方法。
168. `refl::ObjectDef<T>()` 注册对象类型的反射信息，`.def_field()`/`.def_ro()` 注册字段，`.def_method()` 注册方法。
169. `refl::TypeAttrDef<T>().def(attr_name, value)` 注册类型属性（如 kConvert、kSEqual、kSHash），见 `src/ffi/object.cc:627-654`。
170. `refl::EnsureTypeAttrColumn(name)` 确保类型属性列存在（即使为空），见 `src/ffi/container.cc:104-105`。
171. `dataclass.cc` 实现基于反射的数据类操作：深拷贝（DeepCopy）、表示打印（ReprPrint）、递归哈希（RecursiveHash）、递归比较（RecursiveEq/Lt/Gt/Le/Ge），见 `src/ffi/extra/dataclass.cc:20-23`。
172. `dataclass.cc` 定义最大遍历栈深度 `kMaxTraversalStackDepth = 1 << 20`（约 100 万），见 `src/ffi/extra/dataclass.cc:71`。
173. `dataclass.cc` 使用 CRTP（奇异递归模板模式）基类 `ObjectGraphDFS<Derived, FrameT, ResultT>` 实现迭代式 DFS 遍历，避免递归栈溢出，见 `src/ffi/extra/dataclass.cc:135-150`。
174. FrameBase 支持三种帧类型：kSequence（序列）、kMap（映射）、kObject（对象），见 `src/ffi/extra/dataclass.cc:116-126`。
175. EnumObj 注册了两个只读字段 `_value`（序号，标记为 SEqHashIgnore）和 `_name`（实例名），见 `src/ffi/object.cc:655-658`。
176. 枚举相关类型属性列：kEnumEntries、kEnumAttrs、kEnumValueEntries，见 `src/ffi/object.cc:659-661`。
177. Python 端 dataclass 支持位于 `python/tvm_ffi/dataclasses/`，包含 `c_class.py`（C++ 类装饰器）、`py_class.py`（Python 类装饰器）、`field.py`（字段定义）、`enum.py`（枚举支持）、`common.py`（公共工具）。
178. Python 端 `method` 装饰器从 `dataclasses.py_class` 导入，用于标记方法，见 `python/tvm_ffi/__init__.py:75`。
179. Rust 端使用 derive 宏 `#[derive(Object)]` 和 `#[derive(ObjectRef)]` 自动生成 ObjectCore/ObjectRefCore 实现，支持 `#[type_key]` 和 `#[type_index]` 属性，见 `rust/tvm-ffi/src/function.rs:31-33` 和 `rust/tvm-ffi/src/object.rs:109`。

## 9. 序列化与 JSON

180. 序列化核心函数为 `ToJSONGraph` 和 `FromJSONGraph`，声明于 `include/tvm/ffi/extra/serialization.h`，实现于 `src/ffi/extra/serialization.cc`。
181. `ObjectGraphSerializer::Serialize` 输出 JSON 对象，包含 `root_index`（根节点索引）、`nodes`（节点数组）、可选 `metadata`，见 `src/ffi/extra/serialization.cc:46-55`。
182. 序列化器使用 `node_index_map_`（unordered_map<Any, int64_t>）跟踪已序列化的值，支持共享引用（DAG），见 `src/ffi/extra/serialization.cc:60-65`。
183. 基本类型序列化为 `{"type": "<type_key>", "data": <value>}` 格式，见 `src/ffi/extra/serialization.cc:67-115`。
184. None 类型序列化为 `{"type": "ffi.None"}`（无 data 字段），见 `src/ffi/extra/serialization.cc:68-71`。
185. Bytes 类型使用 Base64 编码（`Base64Encode`），见 `src/ffi/extra/serialization.cc:109-114`。
186. DLDevice 序列化为 `[device_type, device_id]` 二元数组，见 `src/ffi/extra/serialization.cc:93-100`。
187. DataType 序列化为字符串形式（通过 `DLDataTypeToString`），见 `src/ffi/extra/serialization.cc:87-91`。
188. List 和 Dict 序列化时检测自引用循环，发现环时抛出 ValueError，见 `src/ffi/extra/serialization.cc:125-132` 和 `src/ffi/extra/serialization.cc:143-149`。
189. JSON 解析器和写入器分别实现于 `json_parser.cc` 和 `json_writer.cc`，提供 `json::Value`、`json::Object`、`json::Array` 等 DOM 类型。
190. `ToJSONGraphString` 和 `FromJSONGraphString` 提供字符串级别的序列化/反序列化便捷接口，见 `python/tvm_ffi/_ffi_api.py:121-122`。
191. Python 端 `serialization` 模块在 `__init__.py` 中直接导入，见 `python/tvm_ffi/__init__.py:90`。
192. `extra/base64.h` 提供 Base64 编解码功能，用于序列化中的二进制数据编码，见 `src/ffi/extra/serialization.cc:32`。

## 10. 结构相等与哈希

193. `StructuralEqual::Equal(lhs, rhs, map_free_vars, skip_tensor_content)` 是结构相等入口，见 `src/ffi/extra/structural_equal.cc:452-459`。
194. `StructuralEqual::GetFirstMismatch` 返回首个不匹配的访问路径对（`AccessPathPair`），用于错误诊断，见 `src/ffi/extra/structural_equal.cc:461-482`。
195. `StructuralHash::Hash(value, map_free_vars, skip_tensor_content)` 返回 uint64_t 哈希值，FFI 层通过 `FFIStructuralHash` 转为 int64_t 以避免 Any 转换溢出，见 `src/ffi/extra/structural_hash.cc:367-381`。
196. 结构相等/哈希支持五种 kind：`kTVMFFISEqHashKindUnsupported`（不支持）、`kTVMFFISEqHashKindUniqueInstance`（指针相等）、`kTVMFFISEqHashKindConstTreeNode`（常量树节点，指针相等可快速判定）、`kTVMFFISEqHashKindDAGNode`（有向无环图节点，记录映射）、`kTVMFFISEqHashKindFreeVar`（自由变量，支持绑定），见 `src/ffi/extra/structural_equal.cc:144-202`。
197. UniqueInstance 模式直接使用 `lhs.same_as(rhs)` 指针比较，见 `src/ffi/extra/structural_equal.cc:151-154`。
198. DAGNode 模式记录双向映射（equal_map_lhs_ 和 equal_map_rhs_），支持共享子节点的正确比较，见 `src/ffi/extra/structural_equal.cc:161-180`。
199. FreeVar 模式支持 def region 概念：kNone（不在 def 区域，free var 按指针比较）、kRecursive（递归 def 区域）、kNonRecursive（非递归 def 区域），见 `src/ffi/extra/structural_equal.cc:188-202` 和 `src/ffi/extra/structural_hash.cc:152-159`。
200. 结构相等比较中，float NaN 特判：两个 NaN 视为相等，见 `src/ffi/extra/structural_equal.cc:88-90`。
201. POD 类型比较通过直接比较 `zero_padding == zero_padding && v_int64 == v_int64` 实现（zero_padding 清零不变量使此操作正确），见 `src/ffi/extra/structural_equal.cc:92-93`。
202. 小字符串（kTVMFFISmallStr）与堆字符串（kTVMFFIStr）可跨表示比较，使用 `Bytes::memequal` 逐字节比较，见 `src/ffi/extra/structural_equal.cc:59-83`。
203. Map 比较时使用 `MapLhsToRhs`/`MapRhsToLhs` 进行键映射，支持 DAG/FreeVar 键的正确查找，见 `src/ffi/extra/structural_equal.cc:287-330` 和 `src/ffi/extra/structural_equal.cc:410-432`。
204. Tensor 内容比较要求 CPU 设备且连续（contiguous），使用 `std::memcmp` 逐字节比较；`skip_tensor_content=true` 时仅比较形状和 dtype，见 `src/ffi/extra/structural_equal.cc:390-408`。
205. 结构哈希中，NaN 被规范化为 `quiet_NaN` 后哈希，确保不同 NaN 表示映射到同一哈希值，见 `src/ffi/extra/structural_hash.cc:56-60`。
206. 小字符串哈希时使用 kTVMFFIStr 类型索引（而非 kTVMFFISmallStr），确保栈上和堆上字符串哈希一致，见 `src/ffi/extra/structural_hash.cc:61-66`。
207. Map 哈希是顺序无关的：通过 `FindOrderIndependentHash` 为键找顺序无关哈希，按键哈希排序后组合，处理哈希冲突（ties）时跳过值哈希以确保确定性，见 `src/ffi/extra/structural_hash.cc:248-318`。
208. DAG 节点哈希中注入 `graph_node_counter_` 以区分 DAG 与树结构，见 `src/ffi/extra/structural_hash.cc:163-165`。
209. FreeVar 哈希中注入 `free_var_counter_`（词法顺序），在 def region 内按发现顺序编号，见 `src/ffi/extra/structural_hash.cc:152-154`。
210. 哈希备忘录 `hash_memo_` 缓存已计算的对象哈希，避免重复计算并处理循环，见 `src/ffi/extra/structural_hash.cc:125-128` 和 `src/ffi/extra/structural_hash.cc:167`。
211. 自定义结构相等/哈希通过类型属性列 kSEqual/kSHash 注册，回调函数接收 def_region_kind 参数（int 类型以保持跨语言 FFI 签名稳定），见 `src/ffi/extra/structural_equal.cc:208-284` 和 `src/ffi/extra/structural_hash.cc:174-225`。
212. Python 端暴露 `structural_equal`、`structural_hash`、`get_first_structural_mismatch`、`StructuralKey`、`StructuralVisitor`、`structural_walk`、`DefRegionKind`、`WalkOrder`、`WalkResult`、`VisitInterrupt`，见 `python/tvm_ffi/__init__.py:78-89`。
213. 不匹配路径通过 `AccessStep` 表示，支持 Attr（属性访问）、ArrayItem（数组索引）、MapItem（映射键）、MapItemMissing（缺失键）、ArrayItemMissing（缺失元素），见 `src/ffi/extra/structural_equal.cc:239-242` 和 `src/ffi/extra/structural_equal.cc:299-309`。
214. 全局函数注册：`ffi.StructuralEqual`、`ffi.GetFirstStructuralMismatch`、`ffi.StructuralHash`，见 `src/ffi/extra/structural_equal.cc:486-488` 和 `src/ffi/extra/structural_hash.cc:385`。

## 11. Tensor 与 DLPack

215. Tensor 对象布局为 `{ TVMFFIObject, DLTensor, ... }`，类型索引为 kTVMFFITensor=70，见 `include/tvm/ffi/c_api.h:155-157`。
216. `TVMFFITensorCreateUnsafeView` 从源 tensor 和 DLTensor 原型创建不安全视图，使用 `ViewNDAlloc` 分配器（不释放数据），见 `src/ffi/tensor.cc:50-77`。
217. `TVMFFITensorFromDLPack` 从 `DLManagedTensor*` 创建 Tensor，接受 min_alignment 和 require_contiguous 参数，见 `src/ffi/tensor.cc:79-86`。
218. `TVMFFITensorFromDLPackVersioned` 从 `DLManagedTensorVersioned*` 创建 Tensor，见 `src/ffi/tensor.cc:88-95`。
219. `TVMFFITensorToDLPack` 将 Tensor 转换为 `DLManagedTensor*`，见 `src/ffi/tensor.cc:97-103`。
220. `TVMFFITensorToDLPackVersioned` 将 Tensor 转换为 `DLManagedTensorVersioned*`，见 `src/ffi/tensor.cc:105-111`。
221. Tensor 创建通过 `make_inplace_array_object<TensorObjFromNDAlloc<ViewNDAlloc>, int64_t>` 在对象后内联分配 shape/stride 数据，见 `src/ffi/tensor.cc:71-74`。
222. Rust 端 Tensor 定义于 `rust/tvm-ffi/src/collections/tensor.rs`，导出 `Tensor`、`NDAllocator`、`CPUNDAlloc`，见 `rust/tvm-ffi/src/lib.rs:39`。
223. Python 端 Tensor、Shape、Device、device、from_dlpack、DLDeviceType 从 `_tensor` 模块导入，见 `python/tvm_ffi/__init__.py:72-73`。
224. Python 端可选模块 `_optional_torch_c_dlpack` 用于加速 torch DLPack 转换，见 `python/tvm_ffi/__init__.py:97`。
225. DataType 支持丰富的浮点格式：float8_e3m4、float8_e4m3、float8_e4m3b11fnuz、float8_e4m3fn、float8_e4m3fnuz、float8_e5m2、float8_e5m2fnuz、float8_e8m0fnu、float6_e2m3fn、float6_e3m2fn、float4_e2m1fn，见 `src/ffi/dtype.cc:99-142`。
226. DataType 字符串解析支持 custom 类型（格式 `custom[<name>]`），通过全局函数 `dtype.get_custom_type_code`/`dtype.get_custom_type_name` 查找，见 `src/ffi/dtype.cc:41-69`。
227. DataType 支持可伸缩向量（scalable vectors），lanes 为负值表示 `xvscale<N>` 格式，见 `src/ffi/dtype.cc:185-187` 和 `src/ffi/dtype.cc:231-254`。
228. bool 类型特殊编码：code=kDLBool、bits=8、lanes=1，字符串表示为 "bool"，见 `src/ffi/dtype.cc:163-165`。
229. void/handle 类型：code=kDLOpaqueHandle、bits=0、lanes=0，字符串表示为空字符串，见 `src/ffi/dtype.cc:167-169`。
230. Rust 端 `DLDataTypeExt` trait 为 DLDataType 提供扩展方法，见 `rust/tvm-ffi/src/lib.rs:41`。

## 12. Python 绑定（Cython）

231. Python 核心 Cython 扩展为 `python/tvm_ffi/cython/core.pyx`，配套 `.pxi` 包含文件：base.pxi、object.pxi、function.pxi、error.pxi、string.pxi、tensor.pxi、dtype.pxi、device.pxi、type_info.pxi、pycallback.pxi、pyclass_type_converter.pxi。
232. C++/Python 桥接头文件为 `cython/tvm_ffi_python_helpers.h`，见 `python/tvm_ffi/cython/` 目录。
233. Python 端核心类从 `core` 模块导入：`Object`、`ObjectConvertible`、`Function`、`CAny`、`CContainerBase`，见 `python/tvm_ffi/__init__.py:69`。
234. Python 端类型转换通过 `convert` 和 `convert_func` 函数，从 `_convert` 模块导入，见 `python/tvm_ffi/__init__.py:70`。
235. Python 端错误注册通过 `register_error` 函数，从 `error` 模块导入，见 `python/tvm_ffi/__init__.py:71`。
236. Python 端 `_dunder.py` 实现双下方法（如 `__eq__`、`__hash__`、`__repr__` 等）的混入。
237. Python 端 `_dtype.py` 实现 dtype 字面量（bool/int8/int16/int32/int64/uint8/uint16/uint32/uint64/float64/float32/float16/bfloat16/float8_*/float4_*），见 `python/tvm_ffi/__init__.py:100-120`。
238. Python 端 `TracebackManager` 解析 C++ backtrace 字符串（格式 `File "<filename>", line <lineno>, in <func>`），通过 AST 编译和 code object 替换构造伪帧，见 `python/tvm_ffi/error.py:31-87`。
239. `TracebackManager` 缓存 code object 以避免重复创建，缓存键为 (filename, lineno, func)，见 `python/tvm_ffi/error.py:65-87`。
240. `_with_append_backtrace` 函数将 C++ backtrace 追加到 Python 异常的 `__traceback__`，使用嵌套函数避免帧对象引用循环（PR #327），见 `python/tvm_ffi/error.py:141-150`。
241. Python 端 `cpp/` 子模块包含 `dtype.py`、`extension.py`、`nvrtc.py`，提供 C++ 相关工具。
242. Python 端 stub 生成位于 `stub/`，包含 `cli.py`（命令行入口）、`generator.py`（生成器）、`python_generator/`（Python 存根生成器），支持 `# tvm-ffi-stubgen(begin/end)` 标记区域自动更新。
243. `_ffi_api.py` 使用 `# tvm-ffi-stubgen(begin): global/ffi@.registry` 和 `# tvm-ffi-stubgen(end)` 标记自动生成区域，见 `python/tvm_ffi/_ffi_api.py:35-36` 和 `python/tvm_ffi/_ffi_api.py:126`。
244. Python 端 `stream.py` 提供 `StreamContext`、`get_raw_stream`、`use_raw_stream`、`use_torch_stream`，支持 CUDA 流管理，见 `python/tvm_ffi/__init__.py:77`。
245. Python 端 `config.py` 提供 `tvm-ffi-config` CLI 入口，包导入时检测是否在配置模式（`sys.argv[0]` 以 `tvm-ffi-config` 结尾或 `-m tvm_ffi.config`），配置模式下跳过 eager import，见 `python/tvm_ffi/__init__.py:26-40`。
246. Python 端 `libinfo.py` 负责定位和加载动态库。
247. Python 端 `access_path.py` 实现 AccessPath 类，用于结构相等不匹配路径。
248. Python 端 Object 子类默认 `__slots__ = ()`（通过元类），阻止 per-instance `__dict__`；可通过显式声明 `__slots__ = ("__dict__",)` 退出，见 `python/tvm_ffi/registry.py:57-64`。

## 13. Rust 绑定

249. Rust 高级绑定 crate `tvm-ffi` 重新导出 `tvm_ffi_sys`（原始 FFI 绑定），见 `rust/tvm-ffi/src/lib.rs:33`。
250. Rust 端导出的核心类型：Any、AnyView、Array、Map、Shape、Tensor、CPUNDAlloc、NDAllocator、Function、Module、Object、ObjectArc、ObjectCore、ObjectCoreWithExtraItems、ObjectRefCore、Optional、String、Bytes、Error、ErrorKind、Result，见 `rust/tvm-ffi/src/lib.rs:35-51`。
251. Rust 端导出的错误常量：ATTRIBUTE_ERROR、INDEX_ERROR、KEY_ERROR、RUNTIME_ERROR、TYPE_ERROR、VALUE_ERROR，见 `rust/tvm-ffi/src/lib.rs:43-45`。
252. Rust 端重新导出 sys 层类型：TVMFFITypeIndex（as TypeIndex）、DLDataType、DLDataTypeCode、DLDevice、DLDeviceType、TVMFFIAny、TVMFFIObject、TVMFFIStreamHandle，见 `rust/tvm-ffi/src/lib.rs:53-56`。
253. Rust 端 `ObjectArc<T>` 实现 Send/Sync（当 T: Send + Sync 时），见 `rust/tvm-ffi/src/object.rs:43-44`。
254. Rust 端 `ObjectArc<T>` 使用 `#[repr(C)]`，内部为 `std::ptr::NonNull<T>` 和 `PhantomData<T>`，见 `rust/tvm-ffi/src/object.rs:38-41`。
255. Rust 端 `FunctionObj` 的 `cell` 字段类型为 `TVMFFIFunctionCell`，包含 `safe_call` 和 `cxx_call` 两个函数指针，见 `rust/tvm-ffi/src/function.rs:36`。
256. Rust 端回调函数签名为 `Fn(&[AnyView]) -> Result<Any>`，通过 `CallbackFunctionObjImpl<F>` 包装为 FFI 兼容的 extern "C" 函数，见 `rust/tvm-ffi/src/function.rs:54`。
257. Rust 端回调成功时通过 `Any::into_raw_ffi_any(value)` 写入结果并返回 0，失败时调用 `Error::set_raised(&error)` 并返回 -1，见 `rust/tvm-ffi/src/function.rs:83-92`。
258. Rust 端 `function_internal.rs` 提供 `AsPackedCallable` 和 `TupleAsPackedArgs` trait，支持将 Rust 闭包自动转换为 FFI 调用，见 `rust/tvm-ffi/src/function.rs:22`。
259. Rust 端 `derive.rs` 提供 `Object` 和 `ObjectRef` 过程宏，自动生成类型注册代码。
260. Rust 端 `macros.rs` 提供声明式宏。
261. Rust 端 `error.rs` 定义 Error、ErrorKind、Result 类型，以及六种标准错误类别常量。
262. Rust 端 `optional.rs` 实现 Optional 类型（映射到 FFI 的 Optional/None 语义）。
263. Rust 端 `string.rs` 实现 String 和 Bytes 类型。
264. Rust 端 `type_traits.rs` 定义 `AnyCompatible` trait，用于类型与 Any 之间的安全转换。
265. Rust 端 `device.rs` 提供 `current_stream` 和 `with_stream` 函数。
266. Rust 端 `dtype.rs` 提供 `DLDataTypeExt` 扩展 trait。
267. Rust 端 sys crate 的 C API 绑定位于 `rust/tvm-ffi-sys/src/c_api.rs`。

## 14. 错误处理

268. 错误对象类型索引为 kTVMFFIError=67，ErrorObj 继承自 Object，C++ 端 Error 类继承自 ObjectRef 和 std::exception。
269. `TVMFFIErrorCell` 定义于 `include/tvm/ffi/c_api.h:422-449`，包含 kind（TVMFFIByteArray）、message（TVMFFIByteArray）、backtrace（TVMFFIByteArray）、update_backtrace（函数指针）、cause_chain（可选的错误链）、extra_context（可选的附加上下文）。
270. backtrace 顺序为最近调用在前（栈顶到栈底），便于错误传播时追加；打印时鼓励反转以对齐 Python 风格，见 `include/tvm/ffi/c_api.h:430-435`。
271. `SafeCallContext` 是 thread-local 类，存储最后一个错误（`ObjectPtr<ErrorObj> last_error_`），见 `src/ffi/error.cc:32-74`。
272. `SafeCallContext::SetRaised` 从不透明句柄构造 ObjectPtr（不增加引用计数，接管所有权），见 `src/ffi/error.cc:34-37`。
273. `SafeCallContext::SetRaisedByCstr` 从 kind、message、backtrace C 字符串构造 Error 对象，见 `src/ffi/error.cc:39-42`。
274. `SafeCallContext::SetRaisedByCstrParts` 接受多段消息（message_parts 数组），拼接后构造 Error，见 `src/ffi/error.cc:44-61`。
275. `SafeCallContext::MoveFromRaised` 将最后一个错误移动到输出句柄（所有权转移），见 `src/ffi/error.cc:63-65`。
276. `TVMFFIErrorSetRaisedFromCStr` 在设置错误时调用 `TVMFFIBacktrace(nullptr, 0, nullptr, 0)` 收集回溯，见 `src/ffi/error.cc:79-83`。
277. `TVMFFIErrorCreate` 从 kind、message、backtrace 字节数组构造 Error 对象，捕获 std::bad_alloc 返回 -1，见 `src/ffi/error.cc:100-114`。
278. `TVMFFIErrorCreateWithCauseAndExtraContext` 支持错误原因链（cause_chain）和附加上下文（extra_context），见 `src/ffi/error.cc:116-146`。
279. backtrace 更新模式：`kTVMFFIBacktraceUpdateModeReplace=0`（替换）、`kTVMFFIBacktraceUpdateModeAppend=1`（追加），见 `include/tvm/ffi/c_api.h:406-416`。
280. 非 Windows 平台 backtrace 实现在 `backtrace.cc`，支持 libbacktrace（`TVM_FFI_USE_LIBBACKTRACE`）和简单回退两种模式，见 `src/ffi/backtrace.cc:24-190`。
281. libbacktrace 模式下使用 `backtrace_create_state` 创建状态，`backtrace_full` 获取栈帧，`abi::__cxa_demangle` 反混淆 C++ 符号名，见 `src/ffi/backtrace.cc:52-69` 和 `src/ffi/backtrace.cc:137-142`。
282. libbacktrace 在多线程同时运行时消耗内存，因此使用 static mutex 保护，见 `src/ffi/backtrace.cc:136-139`。
283. backtrace 支持 FFI 边界检测（`DetectFFIBoundary`），`cross_ffi_boundary` 参数控制是否在 FFI 边界停止，见 `src/ffi/backtrace.cc:101-103` 和 `src/ffi/backtrace.cc:127`。
284. backtrace 支持跳过额外帧（`skip_frame_count`）和排除特定帧（`ShouldExcludeFrame`），见 `src/ffi/backtrace.cc:104-111`。
285. 可选的 segfault 信号处理器（`TVM_FFI_BACKTRACE_ON_SEGFAULT`）在段错误时打印 backtrace 并重新抛出信号，见 `src/ffi/backtrace.cc:149-172`。
286. Windows 平台（_MSC_VER）不编译 backtrace.cc，backtrace 功能可能由其他平台特定实现提供。
287. Python 端 `register_error` 函数注册 Python 异常类型，使 C++ 错误能映射到对应 Python 异常类。
288. C++ 端异常层次：Error 为基类，派生类型包括 RuntimeError、ValueError、TypeError、InternalError 等，通过 `TVM_FFI_THROW(ErrorType)` 宏抛出。
289. `TVM_FFI_THROW`、`TVM_FFI_LOG_AND_THROW`、`TVM_FFI_ICHECK`、`TVM_FFI_ICHECK_NOTNULL`、`TVM_FFI_ICHECK_EQ`、`TVM_FFI_ICHECK_LT` 等宏提供断言和异常抛出功能。
290. `TVM_FFI_LOG_EXCEPTION_CALL_BEGIN/END` 宏用于记录异常但不设置 raised error 的 C API 函数（如 `TVMFFIGetTypeInfo`、`TVMFFIGetTypeAttrColumn`），见 `src/ffi/object.cc:582-603`。
291. Rust 端 Error 类型实现 `set_raised` 和 `from_raised` 方法，分别对应 C 端的 `TVMFFIErrorSetRaised` 和从 SafeCallContext 提取错误，见 `rust/tvm-ffi/src/function.rs:89` 和 `rust/tvm-ffi/src/function.rs:121`。
292. C++ safe_call 宏捕获两种异常：`tvm::ffi::Error`（通过 `SetSafeCallRaised(err)` 设置）和 `std::exception`（包装为 InternalError），见 `include/tvm/ffi/function.h:82-89`。
293. DataType 解析失败抛出 ValueError，包含未知 dtype 字符串和具体解析位置信息，见 `src/ffi/dtype.cc:338`。
294. Module 循环依赖检测在 ImportModule 时通过 DFS 遍历 imports 图实现，见 `src/ffi/extra/module.cc:104-118`。
295. 序列化中 List/Dict 自引用循环检测使用 `active_lists_` 集合跟踪正在序列化的可变容器指针，见 `src/ffi/extra/serialization.cc:125-132`。
