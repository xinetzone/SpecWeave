---
type: Insights
title: TVM 架构洞察
description: 基于 1206 条源码事实综合分析的 TVM 四层栈架构成果，涵盖 FFI、TIR、Relax、Runtime 各层设计洞察
tags: [tvm, architecture, insights, analysis, reference]
generated: { by: source-code-to-okf-wiki/I, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-ir-tir
    resource: "/references/facts-ir-tir.md"
    title: IR 核心与 TIR 事实清单
  - id: facts-relax-te-topi
    resource: "/references/facts-relax-te-topi.md"
    title: Relax/TE/TOPI 事实清单
  - id: facts-runtime-target-arith
    resource: "/references/facts-runtime-target-arith.md"
    title: Runtime/Target/Arith 事实清单
  - id: facts-tvm-ffi
    resource: "/references/facts-tvm-ffi.md"
    title: TVM-FFI 事实清单
---

# TVM 架构洞察

> I 阶段产出。基于 1206 条 R 阶段事实综合分析。
> 生成日期：2026-08-23
> 信源：facts-ir-tir.md（304条）、facts-relax-te-topi.md（244条）、facts-runtime-target-arith.md（363条）、facts-tvm-ffi.md（295条）

---

## I-1: TVM 四层栈架构——FFI 基础设施 → TIR 张量 IR → Relax 图 IR → Runtime 执行

**核心论点**：TVM 采用严格分层的四层编译栈，自底向上依次为 TVM-FFI 跨语言基座、TIRx 张量级 IR、Relax 图级 IR、Runtime 执行引擎。四层之间通过明确定义的对象系统和 Pass 流水线解耦：FFI 层提供类型擦除的 Any/Object/Function 原语；TIRx 层在其上构建标量/缓冲区级计算描述；Relax 层在 TIRx 之上构建张量算子图与数据流模型；Runtime 层消费编译产物（VM Bytecode 或 DSO 模块）执行。这种分层使得高层图优化与低层内核优化可独立演进，同时通过 IRModule 容器实现跨层函数共存。

**支撑事实**：
- facts-tvm-ffi.md F-018: `Object` 基类定义于 `include/tvm/ffi/object.h:127`，所有 FFI 对象继承此类，包含 `TVMFFIObject header_`——FFI 层是全栈对象系统的根基
- facts-tvm-ffi.md F-112: `TVMFFIAny` 是 16 字节栈上标签联合体，type_index<64 为栈上 POD、≥64 为堆分配引用计数对象——FFI 的动态类型系统贯穿所有上层 IR
- facts-ir-tir.md F-153: `PrimFuncNode` 继承自 `BaseFuncNode`，包含 params/buffer_map/body，是 TIR 层的函数载体
- facts-relax-te-topi.md F-25: `FunctionNode` 继承自 `BaseFuncNode`，包含 params/body/ret_ty/is_pure——Relax 函数与 TIR PrimFunc 共享 BaseFunc 基类，共存于 IRModule
- facts-relax-te-topi.md F-118: `LegalizeOps()` Pass 将高层 Relax 算子调用合法化为 `call_tir` 及对应 TIR PrimFunc——这是 Relax→TIR 的核心桥接 Pass
- facts-runtime-target-arith.md F-075: `Executable` 类表示 VM 可执行文件，包含字节码、常量池、函数表——Runtime 层消费编译产物
- facts-runtime-target-arith.md F-340: `compile()` 函数自动检测模块类型，含 Relax 函数则路由到 `tvm.relax.build`，否则调用 `tvm.tirx.build`——Driver 层根据 IR 内容选择编译路径

**设计动机**：编译器栈的分层是关注点分离的必然结果。图级优化（算子融合、布局转换、内存规划）需要全局视角但不关心寄存器分配；张量级优化（循环变换、向量化、张量化）需要精细控制但不需要理解神经网络语义。四层架构使每一层都有最小化的语义内核，同时通过 BaseFunc/IRModule 实现跨层互操作。FFI 层独立为子项目（tvm-ffi），则解决了跨语言绑定和 ABI 稳定性这一横切关注点。

**跨模块影响**：
- IRModule 同时持有 Relax Function 和 TIR PrimFunc，是跨层函数的容器（F-049）
- Pass 系统在每一层都有实例（IR Pass、TIR Pass、Relax Pass），但共享 PassContext 基础设施（F-070~F-081）
- BlockBuilder.emit_te 桥接 Relax 与 TE/TIR（Relax 层 F-43~F-53）
- CodeGen 统一入口 `codegen::Build(mod, target)` 通过 target kind 分派到具体后端，消费 TIR PrimFunc（Runtime F-161~F-163）
- VM ExecBuilder 将 Relax 函数降级为字节码指令（Relax F-152~F-160）

---

## I-2: Object/ObjectRef 双层智能指针模式——Node 持有数据、Ref 管理生命周期，贯穿全栈

**核心论点**：TVM 的对象系统采用 intrusive reference counting 的双层设计：每个 IR 节点有一个 `Node`/`Object` 后缀类（如 `ExprNode`、`PrimFuncNode`）继承自 `ffi::Object`，持有实际数据和 vtable；对应的无后缀引用类（如 `Expr`、`PrimFunc`）继承自 `ffi::ObjectRef`，通过 `data_` 指针持有节点并管理强/弱引用计数。引用计数打包在单个 `uint64_t combined_ref_count` 中（低32位强引用、高32位弱引用），支持一次原子操作完成增减。类型系统不依赖 C++ RTTI，而是通过自定义 type_index 和 `_type_child_slots` 预留槽位实现 O(1) 子类检查。此模式从 FFI 层一直贯穿到 TIRx、Relax、Runtime 所有模块。

**支撑事实**：
- facts-ir-tir.md F-001: `Node` 后缀类继承自 `ffi::Object`，引用类继承自 `ffi::ObjectRef`，通过 `data_` 指针持有节点对象
- facts-ir-tir.md F-008~F-010: `TVM_FFI_DECLARE_OBJECT_INFO_FINAL` 宏声明终态类型信息，`TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE` 定义空值安全方法，`TVM_DEFINE_OBJECT_REF_COW_METHOD` 生成 Copy-On-Write 方法
- facts-tvm-ffi.md F-020: `TVMFFIObject` 是 24 字节 C 结构体头，包含 `combined_ref_count`（uint64_t）、`type_index`（int32_t）、deleter 联合体
- facts-tvm-ffi.md F-021: 强引用计数在低 32 位、弱引用计数在高 32 位，合并设计允许一次 u64 原子操作完成
- facts-tvm-ffi.md F-038: 类型索引分配策略——静态索引（≥64）优先，其次父类预留槽位池，最后动态溢出区（≥128）
- facts-tvm-ffi.md F-031: `_type_child_slots` 为子类预留类型索引槽位，type_index 在 `[type_index, type_index+slots]` 范围内即可 O(1) 判定子类
- facts-tvm-ffi.md F-024: `Object::IsInstance<TargetType>()` 不依赖 C++ RTTI，通过自定义 type_index 检查
- facts-ir-tir.md F-028: `RangeNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode`，`span` 字段在相等/哈希中被忽略——对象系统内建结构相等/哈希语义分类
- facts-tvm-ffi.md F-196: 结构相等/哈希支持五种 kind：Unsupported、UniqueInstance（指针相等）、ConstTreeNode、DAGNode（记录映射）、FreeVar（支持 def region 绑定）

**设计动机**： intrusive 引用计数相比 `shared_ptr` 的优势在于：(1) 对象头可被 C ABI 直接访问，支持跨语言边界传递而无需 C++ ABI 兼容；(2) 合并强弱引用计数为单次原子操作，在多线程场景下减少缓存争用；(3) 类型索引系统完全脱离 RTTI，使得 `-fno-rtti` 编译和嵌入式部署成为可能。Copy-On-Write 方法则支持函数式风格的不可变 IR 变换——Pass 通过 COW 修改节点而非原地修改，保证变换可追溯和可组合。结构相等/哈希的五种 kind 设计精确区分了指针相等、树节点、DAG 节点和自由变量四种语义，避免了全图遍历的性能开销。

**跨模块影响**：
- 所有 IR 节点（TIRx 的 Var/Buffer/SBlock/PrimFunc，Relax 的 Var/Function/Call）均遵循此模式
- Python 绑定通过 `@tvm_ffi.register_object("type.key")` 装饰器建立 Python 类到 C++ 类型键的映射（F-295）
- Rust 绑定通过 `ObjectArc<T>` 智能指针和 `#[derive(Object)]` 过程宏实现等价语义（FFI F-057~F-062, F-249~F-258）
- 容器系统（Array/Map/List/Dict）本身也是 Object 子类，可被 Any 持有和跨语言传递（FFI F-087~F-102）
- Pass 变换依赖 COW 语义实现不可变更新（F-046~F-048 的 with_attr 方法）

---

## I-3: TVM-FFI 作为统一跨语言基座——C ABI 稳定、Cython/Rust 双绑定、注册表机制

**核心论点**：TVM-FFI 是一个独立版本化（0.1.13）的跨语言互操作层，其设计目标是在 C++、Python、Rust 之间提供稳定、最小、ML 原生的 ABI。核心设计包括：(1) 所有跨语言函数签名统一为 `int(TVMFFIAnyView* args, int32_t nargs, TVMFFIAny* rv)`，返回 0 成功/-1 错误，错误通过 thread-local SafeCallContext 传递；(2) 全局函数注册表 `GlobalFunctionTable` 支持运行时按名注册和查找，使任意语言可注册函数供其他语言调用；(3) 类型反射系统支持字段/方法/元数据/属性列的运行时发现，支撑 dataclass 深拷贝、结构相等哈希、JSON 序列化等通用能力；(4) Cython（Python）和 proc-macro（Rust）双绑定自动生成样板代码。TVM 编译器本体完全构建在此 FFI 之上，Python 前端和 Rust 工具链共享同一 C ABI。

**支撑事实**：
- facts-tvm-ffi.md F-010: ABI 设计四大原则——最小高效、跨编译器版本稳定、ML 原生支持（tensor/shape/dtype）、可扩展动态类型注册
- facts-tvm-ffi.md F-016: 所有 C ABI 函数使用 `extern "C"` 声明
- facts-tvm-ffi.md F-140: 所有 C ABI 函数返回 int，0 成功/-1 错误，错误通过 thread-local SafeCallContext 传递
- facts-tvm-ffi.md F-068: `GlobalFunctionTable` 使用 `Map<String, Any> table_` 存储命名函数
- facts-tvm-ffi.md F-073: `TVMFFIFunctionSetGlobal` 注册命名全局函数，override 参数控制是否允许覆盖
- facts-tvm-ffi.md F-064: `FunctionObj::FCall` 签名为 `void (*)(const FunctionObj*, const AnyView*, int32_t, Any*)`——统一的 packed function 调用约定
- facts-tvm-ffi.md F-159~F-168: 反射系统包含 type_index/type_depth/type_key/fields/methods/metadata，字段有 getter/setter/flags，方法有 metadata
- facts-tvm-ffi.md F-171: dataclass.cc 实现 DeepCopy、ReprPrint、RecursiveHash、RecursiveEq 等基于反射的通用操作
- facts-tvm-ffi.md F-083~F-084: Python 端 `register_global_func` 装饰器和 `register_object` 装饰器
- facts-tvm-ffi.md F-249~F-258: Rust 端重新导出 sys 层类型，`ObjectArc<T>` 实现 Send/Sync，`AsPackedCallable` trait 支持闭包自动转换
- facts-ir-tir.md F-248: C++ 端使用 `TVM_FFI_STATIC_INIT_BLOCK()` 和 `refl::GlobalDef()` 注册 FFI 函数，方法注册用 `def_method`，全局函数用 `def`
- facts-tvm-ffi.md F-012: Python 包导入时尝试先导入 torch 以避免符号冲突（Windows + Python 3.12 + torch 2.9.0 场景）——体现 FFI 在真实复杂环境中的兼容性考量

**设计动机**：传统编译器（LLVM/MLIR）的跨语言绑定通常是事后追加的，导致 ABI 不稳定、样板代码冗余、错误处理不一致。TVM-FFI 将跨语言互操作作为第一性原理设计：统一的 Any 标签联合体避免了每种语言维护独立的类型转换层；全局函数注册表实现了真正的运行时可扩展性（新后端、新 Pass、新算子均可动态注册）；反射系统使得序列化、打印、相等比较等横切功能无需为每种类型手写代码。C ABI 稳定性保证则使得 TVM 编译器和运行时可独立升级，也使得嵌入式部署（无 libstdc++ 依赖）成为可能。

**跨模块影响**：
- Schedule 的所有方法通过 FFI 暴露给 Python（F-248~F-256），Python 层的 `_ffi_api` 自动绑定约 80 个 FFI 函数
- Relax BlockBuilder、ExecBuilder 等核心组件通过 `@tvm_ffi.register_object` 注册到 Python（Relax F-230~F-244）
- Runtime Module 系统构建在 FFI Module 之上（FFI F-141~F-156），支持动态库加载和嵌入式库二进制
- Target/CodeGen 通过全局函数 `"target.build." + kind_name` 分派（Runtime F-162），新后端只需注册此全局函数
- Arith Analyzer 通过 FFI 暴露给 Python（Runtime F-357），Python 端可直接调用 CanProve/Simplify
- 错误处理通过 FFI 的 SafeCallContext 跨 C++/Python/Rust 传播，C++ 异常自动转为 Python 异常（FFI F-271~F-292）

---

## I-4: TIRx 新一代调度设计——SBlock 声明式调度、随机变量 RV、Instruction/Trace 可追踪

**核心论点**：TIRx 引入的 S-TIR 调度系统代表了张量编译器调度范式的代际演进。其核心创新有三：(1) **SBlock（Schedule Block）** 作为声明式计算单元，显式声明 iter_vars/reads/writes，将"计算什么"与"如何调度"分离，使调度原语可基于块依赖关系进行正确性验证；(2) **随机变量（RV）系统**——LoopRV/SBlockRV/ExprRV 作为调度操作的符号句柄，而非直接操作 IR 节点，使得调度序列可被序列化、重放和搜索；(3) **Instruction/Trace 机制**记录每次调度原语调用及其决策（如 split 的因子），Trace 可 apply（应用到新 IR）、serialize（序列化）、simplify（简化）。这三者共同构成了 MetaSchedule 自动调优的基础设施——搜索算法在 RV 空间中采样决策，Trace 记录决策序列，最终可重放以生成最优内核。

**支撑事实**：
- facts-ir-tir.md F-146: `SBlockNode` 包含 iter_vars、reads、writes、name_hint、alloc_buffers、match_buffers、annotations、init、body——块显式声明其迭代空间和访问区域
- facts-ir-tir.md F-149~F-150: `SBlockRealizeNode` 将块绑定到具体迭代值，predicate 为 true 时块才执行——实现块的实例化
- facts-ir-tir.md F-180: `ScheduleNode` 持有 state（ScheduleState）、trace（Trace）、mod（IRModule）、func_working_on
- facts-ir-tir.md F-182: Schedule 有 Concrete（无追踪）和 Traced（有追踪）两种模式，Python 默认使用 TracedSchedule
- facts-ir-tir.md F-187: LoopRV/SBlockRV/ExprRV 是随机变量，ExprRV 类型别名为 Expr（整数值）
- facts-ir-tir.md F-190: `Schedule.get()` 评估随机变量：SBlockRV→SBlock、LoopRV→For、ExprRV→int
- facts-ir-tir.md F-200~F-201: `Instruction` 包含属性/输入/输出/应用函数，`Trace` 提供 apply/serialize/simplify
- facts-ir-tir.md F-203~F-208: 采样原语 SampleInt/SamplePerfectTile/SamplePartitionedTile/SampleComputeLocation 生成带决策记录的 ExprRV
- facts-ir-tir.md F-193: `ScheduleStateNode` 持有 sref 树、块信息（依赖/标志）、stmt2ref 映射——调度状态与 IR 分离
- facts-ir-tir.md F-212~F-247: 40+ 调度原语，每个都有严格的前置条件检查（如 Split 要求循环无注解/线程绑定，Fuse 要求域间无依赖）
- facts-ir-tir.md F-257~F-267: 分析接口自动检测块读写区域、LCA、FLOPs、GPU 代码正确性
- facts-ir-tir.md F-304: MetaSchedule 包含 builder/cost_model/database/feature_extractor/mutator/runner/search_strategy 等自动调优组件

**设计动机**：传统 TVM 的调度是命令式的——直接操作 IR 节点，无法回溯和重放。SBlock 的设计灵感来自 Halide 的调度思想但更进一步：块的读写区域声明显式化了数据依赖，使得调度原语可以在变换前验证正确性（如 ComputeAt 要求产生区域覆盖消费区域，F-230）。RV 和 Trace 的引入则是为自动调优服务的：搜索算法需要在巨大的调度空间中探索，每个决策（分块因子、并行/向量化选择、计算位置）必须可记录和重放。ConcreteSchedule 用于不需要追踪的场景（如手写调度），TracedSchedule 用于自动调优，两种模式共享同一套调度原语。

**跨模块影响**：
- Arith 子系统为调度正确性提供证明能力——ProducerCoversConsumer 逐维使用算术分析器证明包含关系（F-197）
- ScheduleState 的区域分析依赖 AnalyzeRegionUpperBound/LowerBound（F-195~F-196），后者调用 arith::IntSetAnalyzer
- TIRx 的 ForKind（serial/parallel/vectorized/unrolled/thread_binding，F-139）是调度原语 Parallel/Vectorize/Bind/Unroll 的操作目标
- Relax 的 FuseTIR Pass 将多个 Relax 子函数融合为更大的 TIR 函数后，可进入 S-TIR 调度（Relax F-134）
- MetaSchedule 的 Database/TuningRecord 持久化 Trace，实现跨编译会话的调优经验复用
- TVMScript 作为调度的人类可读/可写前端，Schedule.show() 同时显示 IRModule 和 Trace（F-289）

---

## I-5: Relax 块构建器与 Dataflow 模型——BlockBuilder/emit_te 桥接 TE、DataflowVar 区分计算/输入

**核心论点**：Relax 的 BlockBuilder 是图级 IR 的构建核心，它将"逐语句发射表达式"的命令式构建体验与"数据流图"的声明式语义统一起来。关键设计包括：(1) **作用域管理**——BeginScope/BeginInnerScope/EndScope 控制变量可见性，BeginDataflowBlock 开启数据流块；(2) **Emit/Normalize 管线**——每次 Emit 调用 Normalize 进行形状和类型推导，将表达式转为 A-norm 形式（每个中间结果绑定到变量）；(3) **DataflowVar 与 Var 的区分**——DataflowVar 仅在数据流块内部可见，表示纯计算中间结果，普通 Var 是函数级绑定；(4) **emit_te 桥接**——BlockBuilder 可直接发射 TE Compute 表达式，自动降级为 TIR PrimFunc 并生成 call_tir 调用。算子级别的 FNormalize/FLegalize/FInferType 注册属性使每个算子可自定义归一化、合法化和类型推导行为。

**支撑事实**：
- facts-relax-te-topi.md F-43: `BlockBuilderNode` 提供全局上下文管理、作用域管理、归一化三大类功能
- facts-relax-te-topi.md F-47: BeginScope 开启新作用域（父作用域符号不可用），BeginInnerScope 开启内部作用域（继承父作用域可见参数）
- facts-relax-te-topi.md F-49: Emit 发射 Expr 并返回绑定变量，会调用 Normalize 执行形状和类型推导
- facts-relax-te-topi.md F-51: Normalize 将表达式转换为范式并尽力推导类型和形状
- facts-relax-te-topi.md F-08: `DataflowVarNode` 继承自 `VarNode`，标记数据流变量，区别于普通函数局部可见绑定
- facts-relax-te-topi.md F-20: `DataflowBlockNode` 继承自 `BindingBlockNode`，类型键 `"relax.expr.DataflowBlock"`
- facts-relax-te-topi.md F-57: `FNormalize` 是归一化函数类型，作为 BlockBuilder 的一部分对每个表达式应用
- facts-relax-te-topi.md F-59: `FLegalize` 是合法化函数类型，将 relax::Call 替换为更具体的实现（如 TIR 函数调用）
- facts-relax-te-topi.md F-56: `FInferType` 签名为 `Type(const Call&, const BlockBuilder&)`——类型推导可访问 BlockBuilder 上下文
- facts-relax-te-topi.md F-105: `ToNonDataflow()` 将所有数据流结构转换为非数据流版本
- facts-relax-te-topi.md F-107: `CallTIRRewrite()` 为 call_tir 和 call_dps_packed 执行显式张量分配
- facts-relax-te-topi.md F-109: `StaticPlanBlockMemory()` BindingBlock 级静态内存规划，尽力复用已分配内存
- facts-relax-te-topi.md F-241~F-243: Python 层 FunctionScope/DataflowScope 上下文管理器，BlockBuilder 支持 function()/dataflow()/emit()/emit_output()

**设计动机**：Relax 面临的设计张力是：用户需要像写 NumPy/PyTorch 一样逐行构建计算图（命令式体验），但编译器需要数据流图的显式依赖信息来进行融合和内存优化。BlockBuilder 通过 Emit+Normalize 在构建时即完成 A-norm 转换，使得命令式写法自动产生 SSA 形式的数据流图。DataflowVar 的区分使得编译器可以识别哪些变量是纯计算中间值（可被融合、消除、重排），哪些是函数级绑定（可能被外部引用、不可随意消除）。emit_te 桥接则避免了用户在 Relax 和 TE 之间手动切换——TE 表达式在 BlockBuilder 中直接发射为 call_tir，后续 LegalizeOps/FuseOps/TIR 调度无缝衔接。

**跨模块影响**：
- TE 张量表达式通过 BlockBuilder.emit_te 进入 Relax 图，TE ComputeOp 自动生成 TIR PrimFunc（Relax F-49, TE F-180~F-181）
- LegalizeOps Pass 调用每个算子注册的 FLegalize，将高层算子替换为 call_tir（Relax F-118）
- FuseOps 在 DataflowBlock 内按 OpPatternKind（elemwise/broadcast/injective/reduce/out_ewise_fusable）融合算子（Relax F-54, F-128）
- FuseTIR 将融合后的 Relax 子函数编译为单个 TIR PrimFunc（Relax F-134）
- StaticPlanBlockMemory 在 BindingBlock 级别规划内存复用，需要 DataflowBlock 的依赖信息（Relax F-109）
- VMShapeLower 将形状表达式降级为 VM 形状堆和 TIR 函数（Relax F-151），BlockBuilder 产生的符号形状在此阶段具体化
- ToNonDataflow 在编译后期将 DataflowVar 提升为普通 Var，为 VM 字节码生成做准备（Relax F-105）

---

## I-6: Pass 系统与 PassContext——PassInfo/Sequential/Instrument、线程局部栈、可组合变换

**核心论点**：TVM 的 Pass 基础设施是一个分层、可组合、可观测的变换框架。核心设计包括：(1) **PassInfo 元数据**——每个 Pass 声明 opt_level、name、required 依赖列表、traceable 标志，PassContext 根据这些元数据决定是否启用；(2) **线程局部上下文栈**——PassContext 使用 thread_local 维护上下文栈，支持嵌套作用域和多线程并行编译；(3) **PassInstrument 接口**——在 Pass 执行前后插入回调，支持分析、验证和 profiling，且不侵入 Pass 本身；(4) **多层级 Pass**——Module 级、Function 级、DataflowBlock 级 Pass 通过统一的 Create*Pass 工厂函数创建，Sequential 组合器按序执行；(5) **配置选项注册**——TVM_REGISTER_PASS_CONFIG_OPTION 宏声明类型化的配置键，PassConfigManager 负责合法化。Relax 层在此基础上提供了 40+ 个具体 Pass 和预定义 Pipeline，TIR 层提供 30+ 个 PrimFunc 级 Pass。

**支撑事实**：
- facts-ir-tir.md F-070: `PassInfo` 包含 opt_level、name、required（依赖 Pass 列表）、traceable 元数据
- facts-ir-tir.md F-071: `PassContext` 包含 opt_level、required_pass、disabled_pass、instruments、config
- facts-ir-tir.md F-074: C++ 层 PassContext 使用 thread_local 维护上下文栈，每个线程有独立的默认上下文和上下文栈
- facts-ir-tir.md F-075~F-076: EnterWithScope 先调用 InstrumentEnterPassContext 再压栈，ExitWithScope 验证栈顶后弹栈再调用 InstrumentExitPassContext
- facts-ir-tir.md F-078: PassEnabled 判断逻辑——禁用列表优先，必需列表强制启用，否则比较优化级别
- facts-ir-tir.md F-079: PassConfigManager 管理配置选项注册和合法化，每个键关联类型字符串和合法化函数
- facts-ir-tir.md F-080: TVM_REGISTER_PASS_CONFIG_OPTION 宏注册配置选项
- facts-ir-tir.md F-089: PassInstrument 接口允许在 Pass 执行前后插入回调
- facts-relax-te-topi.md F-102~F-103: CreateFunctionPass 创建函数级 Pass，CreateDataflowBlockPass 创建数据流块级 Pass
- facts-relax-te-topi.md F-147: zero_pipeline 按序执行 LegalizeOps→AnnotateTIROpPattern→FoldConstant→FuseOps→FuseTIR
- facts-relax-te-topi.md F-148: default_build_pipeline 按序应用 13 个 Pass（LegalizeOps→RewriteDataflowReshape→ToNonDataflow→RemovePurityChecking→CallTIRRewrite→StaticPlanBlockMemory→RewriteCUDAGraph→LowerAllocTensor→KillAfterLastUse→LowerRuntimeBuiltin→ComputePrimValue→VMShapeLower→AttachGlobalSymbol）
- facts-ir-tir.md F-168~F-170: TIRx 变换 Pass 包括 VectorizeLoop、StorageRewrite、UnrollLoop、LowerTVMBuiltin、LowerTIRx
- facts-ir-tir.md F-269~F-272: S-TIR 变换 Pass 包括 CanonicalizeLoop、LowerCrossThreadReduction、InjectSoftwarePipeline、InjectDoubleBuffer 等 30+ 个

**设计动机**：编译器 Pass 框架的核心挑战是可组合性和可观测性。TVM 的设计选择体现了几个原则：(1) **显式依赖**——required 列表确保 Pass 间的顺序约束由框架而非隐式约定保证；(2) **线程隔离**——thread_local 上下文栈使得多线程并行编译不同模块时互不干扰，同时嵌套作用域支持条件性启用/禁用 Pass；(3) **Instrument 而非继承**——通过组合（PassInstrument 列表）而非继承来扩展 Pass 行为，符合开闭原则；(4) **配置类型安全**——注册时声明类型和合法化函数，避免运行时字符串键的类型错误。预定义 Pipeline（zero/default/static_shape_tuning）则将常见的 Pass 序列固化为命名流水线，用户也可注册自定义 Pipeline。

**跨模块影响**：
- Pass 基础设施在 IR 核心层定义，被 TIRx、S-TIR、Relax 三层共同复用
- Target 上下文同样使用 thread_local 栈（Runtime F-108~F-111），与 PassContext 模式一致，可在 Pass 中通过 Target::Current() 获取当前目标
- Relax 的 FuseOps→FuseTIR 序列跨越图级和张量级——FuseOps 在 Relax 层分组，FuseTIR 为每组生成 TIR PrimFunc 并可触发 TIR 调度
- S-TIR 的分析 Pass（VerifyGPUCode、VerifyVTCMLimit、OOBChecker）作为 PassInstrument 或验证 Pass 插入调度流水线
- MetaSchedule 在自动调优过程中动态应用调度原语（本质是 Trace 中的 Instruction），调度结果通过 RenewDefs 深拷贝后进入标准 TIR Pass 流水线
- TVMScript 打印可作为 PassInstrument 用于调试，在每个 Pass 后输出 IR 快照

---

## I-7: Arith 子系统作为编译期证明引擎——Analyzer/ConstIntBound/ModularSet/RewriteSimplify

**核心论点**：Arith 子系统是 TVM 编译器内部的"轻量级定理证明器"，它不依赖外部 SMT 求解器（Z3 为可选后端），而是通过多个专用分析器的组合对整数表达式进行边界分析、模分析、化简和集合分析。Analyzer 是复合分析器，包含七个子分析器：ConstIntBound（常量整数边界）、ModularSet（模集合）、RewriteSimplify（重写规则化简）、CanonicalSimplify（规范形式化简）、IntSet（整数集合）、TransitiveComparison（传递比较）、Z3Prover（可选 SMT）。关键设计是 ConstraintContext——在约束作用域内，子分析器可临时添加假设（如循环变量在范围内），退出时恢复。这套证明引擎支撑了调度合法性验证（如 ComputeAt 的区域覆盖证明）、缓冲区压缩、循环展开因子推导、内存访问边界检查等编译期决策。

**支撑事实**：
- facts-runtime-target-arith.md F-197~F-198: `AnalyzerObj` 包含七个子分析器：const_int_bound、modular_set、rewrite_simplify、canonical_simplify、int_set、transitive_comparisons、z3_prover
- facts-runtime-target-arith.md F-200: Bind 将变量绑定到表达式，先经 canonical_simplify 和 rewrite_simplify 化简，再更新所有子分析器
- facts-runtime-target-arith.md F-203~F-205: CanProveGreaterEqual 检查 const_int_bound 的 min_value，CanProveLess 检查 max_value，CanProveEqual 检查整数常量后 CanProve(lhs-rhs==0)
- facts-runtime-target-arith.md F-206: Simplify 默认执行 2 步：rewrite_simplify→canonical_simplify
- facts-runtime-target-arith.md F-216~F-224: ConstIntBoundNode 包含 min_value/max_value（int64_t），使用 kPosInf/kNegInf 表示无界；ConstIntBoundAnalyzer 使用 BoundMapType 缓存中间结果
- facts-runtime-target-arith.md F-225~F-228: ModularSet 表示集合 {coeff*x+base | x∈Z}，等价于 n%coeff==base
- facts-runtime-target-arith.md F-231~F-236: RewriteSimplifier 基于重写规则，支持四个可选扩展（传递性不等式证明、布尔转 CNF、约束应用于布尔分支、乘积与和比较），有最大步数限制和统计计数器
- facts-runtime-target-arith.md F-256~F-258: TransitiveComparisonAnalyzer 支持 8 种比较结果（kInconsistent/kEQ/kLT/kLE/kGT/kGE/kNE/kUnknown），TryCompare 使用已知比较传递性推导
- facts-runtime-target-arith.md F-260~F-266: Z3Prover 可选后端（USE_Z3=ON），CanProve/GetSMTLIB2/GetModel/CountSatisfyingValues
- facts-runtime-target-arith.md F-212~F-214: ConstraintContext 配合 With<> 使用，EnterWithScope 依次调用六个子分析器的 EnterConstraint，ExitWithScope 逆序恢复
- facts-runtime-target-arith.md F-268~F-272: IterAffineMap 支持 Fuse（y=x2*12+x1*4+x0）和 Split（floorDiv/mod）两种准仿射映射模式
- facts-runtime-target-arith.md F-280: DeduceBound 在条件约束下推导目标变量边界
- facts-ir-tir.md F-197: ProducerCoversConsumer 逐维使用算术分析器证明产生区域覆盖消费区域——这是 ComputeAt 合法性的核心检查

**设计动机**：张量编译器需要频繁回答"这个索引表达式是否在边界内""这两个区域是否重叠""这个循环的 trip count 是多少"等问题。这些问题在一般情况下不可判定，但在张量计算的受限域内（仿射表达式、有界循环、简单条件）通常可高效求解。TVM 的策略是分层证明：快速路径用 ConstIntBound/ModularSet（O(1) 查表），中等路径用 RewriteSimplify（规则重写），困难路径用 IntSet（集合运算）或 TransitiveComparison（传递链），最后可选 Z3（SMT 求解但有超时）。ProofStrength 枚举控制证明强度，内部递归重写不使用超过 kDefault 的强度以控制编译时间。ConstraintContext 的 RAII 设计使得循环边界等临时约束可安全地添加和移除，避免污染全局分析状态。

**跨模块影响**：
- S-TIR 调度的区域分析（AnalyzeRegionUpperBound/LowerBound）直接使用 IntSetAnalyzer（F-195~F-196）
- ComputeAt/ReverseComputeAt 的合法性依赖 ProducerCoversConsumer 的 arith 证明（F-197, F-230~F-231）
- CompactBufferAllocation 使用边界分析压缩缓冲区访问区域（F-270）
- StorageAlign 约束 `stride[axis] == k*factor+offset` 依赖 ModularSet 分析（F-237）
- TIRx 表达式运算符对索引类型执行立即常量折叠（F-032, F-159），这是 arith 化简的轻量前置
- Relax 的 CanProveShapeEqual 对符号形状进行尽力证明（Relax F-71），底层应依赖 arith
- TOPI 的 pad 算子输出形状通过算术分析器简化（Relax/TE F-216）
- IndexMap 的逆映射计算和 Layout 变换依赖 IterAffineMap 的仿射分析（F-171~F-172, Runtime F-268~F-273）

---

## I-8: Target/CodeGen 多后端统一——TargetKind/VirtualDevice、LLVM/C/SPIRV/PTX 分层

**核心论点**：TVM 的目标后端系统通过注册表机制实现了"一次描述、多后端生成"的可扩展架构。核心设计包括：(1) **Target 数据结构**——持有 kind（TargetKind）、host（主机目标）、tag（预设标签）、keys（目标键列表，用于匹配）、attrs（类型化属性字典）；(2) **TargetKind 注册表**——每种后端（llvm/cuda/c/opencl/vulkan/metal 等）注册一个 TargetKind，包含默认设备类型、默认键、配置 schema 和规范化函数；(3) **TargetTag 预设**——命名的目标配置（如 "nvidia/nvidia-a100"），支持用户覆盖部分属性；(4) **VirtualDevice 四元组**——device_type/device_id/target/memory_scope，在编译期描述数据放置位置；(5) **CodeGen 分派**——`codegen::Build(mod, target)` 通过全局函数 `"target.build."+kind_name` 分派到具体后端，CodeGenLLVM/CodeGenC 等基类提供共享基础设施。Module 序列化系统支持将设备库打包为 C 源码或 LLVM 模块，实现单文件部署。

**支撑事实**：
- facts-runtime-target-arith.md F-091~F-103: `TargetNode` 包含 kind/host/tag/keys/attrs，str() 返回 JSON，ToConfig() 导出配置字典
- facts-runtime-target-arith.md F-108~F-111: `Target::Current(allow_not_defined)` 从线程本地存储获取当前目标，EnterWithScope/ExitWithScope 管理上下文栈
- facts-runtime-target-arith.md F-123~F-135: `TargetKindNode` 包含 name/default_device_type/default_keys/target_canonicalizer/schema_，TargetKind::Get 按名查找
- facts-runtime-target-arith.md F-136: `TVM_REGISTER_TARGET_KIND("llvm", kDLCPU)` 注册 LLVM 目标，支持 mattr/mcpu/mtriple/fast-math/opt-level/jit 等属性
- facts-runtime-target-arith.md F-142: `TVM_REGISTER_TARGET_KIND("c", kDLCPU)` 注册 C 源码目标
- facts-runtime-target-arith.md F-144: `TVM_REGISTER_TARGET_KIND("composite", kDLCPU)` 注册复合目标，支持 devices 属性为 Target 数组
- facts-runtime-target-arith.md F-147~F-152: TargetTag 系统支持命名预设配置，AddTag/ListTags/GetConfig
- facts-runtime-target-arith.md F-155~F-159: VirtualDevice 是 device_type/virtual_device_id/target/memory_scope 四元组
- facts-runtime-target-arith.md F-161~F-162: `codegen::Build(mod, target)` 通过全局函数 `"target.build."+target->kind->name` 分派
- facts-runtime-target-arith.md F-172~F-187: CodeGenLLVM 同时继承 ExprFunctor 和 StmtFunctor，CodeGenCPU 重写并行启动/函数注册等
- facts-runtime-target-arith.md F-189~F-195: CodeGenC 为 CUDA/OpenCL-C 等 C 变体提供基础设施，注释明确说明目标不是生成 MSVC/GCC 可消费的原生 C
- facts-runtime-target-arith.md F-030~F-044: Module 系统支持 imports 树、属性掩码（DSO 可导出/二进制可序列化）、PackImportsToC/PackImportsToLLVM 打包
- facts-relax-te-topi.md F-161: Relax 外部后端目录包含 clml/codegen_c/codegen_json/cublas/cudnn/cutlass/dnnl/tensorrt 等 11 个子目录
- facts-relax-te-topi.md F-132~F-133: FuseOpsByPattern + MergeCompositeFunctions 为外部后端卸载包装代码生成属性

**设计动机**：深度学习编译器面临的后端碎片化问题极为严重——从 CPU（x86/ARM/RISC-V）到 GPU（NVIDIA/AMD/Intel/Apple）到专用加速器（TPU/NPU/FPGA），每种后端有不同的内存层次、线程模型和指令集。TVM 的策略不是为每种后端硬编码 if-else，而是通过 TargetKind 注册表将后端差异封装为配置+规范化函数+构建函数三元组。keys 列表实现了"模糊匹配"——一个 Target 可声明多个键（如 cuda 同时匹配 "cuda" 和 "gpu"），Pass 可根据键选择性启用。host 字段解决了交叉编译问题——设备代码在主机 CPU 上编译和编排。VirtualDevice 则将设备选择从 Target 中解耦，支持多设备联合编译（composite target）。

**跨模块影响**：
- Target 上下文通过 thread_local 栈在 Pass 执行期间可用，TIR Pass 可查询 Target 属性决定向量化宽度/并行策略
- VirtualDevice 信息在 Relax 层通过 RealizeVDevice Pass 传播（Relax F-119），在 TIR 层通过 SpecializePrimFuncBasedOnCallSite 更新（Relax F-145）
- CodeGenC 是 CUDA/OpenCL/Metal/Vulkan SPIR-V 等 C 变体后端的共同基类，CodeGenLLVM 是 CPU/PTX/AMDGPU 的共同基类
- Relax 的 RunCodegen Pass 触发外部代码生成（Relax F-135），FuseOpsByPattern 为 BYOC（Bring Your Own Codegen）后端创建复合函数
- Module 导入树的序列化（PackImportsToC/LLVM）使得编译产物可嵌入 C 程序或 LLVM 模块，支持无动态链接器部署
- DeviceAPI 抽象（Runtime F-006~F-021）与 TargetKind 的 default_device_type 对应，运行时按 device_type 查找 DeviceAPI 实例

---

## I-9: VM Bytecode 执行模型——Executable/Instruction/OpCode、PagedKVCache/AttentionBackend LLM 支持

**核心论点**：TVM Runtime 的 VM（Virtual Machine）是一个基于寄存器的字节码执行引擎，设计目标是在保持动态形状灵活性的同时实现接近原生的执行效率。核心组件包括：(1) **Executable**——包含字节码指令序列、常量池、函数表，支持 JIT 编译为运行时 Module；(2) **Instruction 集**——Call/Ret/Goto/If 等控制流指令构成图灵完备的指令集，支持动态形状和条件执行；(3) **ExecBuilder**——Relax 后端通过它逐指令构建 VM 可执行文件，内置常量去重和寄存器合法性检查；(4) **PagedKVCache/AttentionBackend**——VM 内置的大语言模型推理基础设施，提供分页式 KV 缓存管理和注意力计算后端抽象。VM 支持 NAIVE 和 POOLED 两种分配器，内存配置可在运行时指定。Module 系统使 VM Executable 可与 DSO 模块共存于同一导入树中。

**支撑事实**：
- facts-runtime-target-arith.md F-060: `VirtualMachine` 类定义于 `include/tvm/runtime/vm/vm.h`，是 VM 执行引擎核心
- facts-runtime-target-arith.md F-064: VM 实现包含 RunLoop 指令调度主循环和 InvokeBytecode 函数调用逻辑
- facts-runtime-target-arith.md F-066~F-067: Python VM 支持 NAIVE_ALLOCATOR=1 和 POOLED_ALLOCATOR=2，构造时接收 rt_mod/device/memory_cfg
- facts-runtime-target-arith.md F-071~F-073: Opcode 枚举包含 Call/Ret/Goto/If 等指令，Instruction 结构体表示单条字节码
- facts-runtime-target-arith.md F-075~F-078: Executable 类表示 VM 可执行文件，包含字节码/常量池/函数表的序列化，jit() 方法即时编译为运行时模块
- facts-runtime-target-arith.md F-079~F-081: VM 内建函数实现在 builtin.cc，PagedKVCache 在 paged_kv_cache.cc，AttentionBackend 在 attn_backend.cc
- facts-relax-te-topi.md F-152~F-160: ExecBuilderNode 提供 EmitCall/EmitRet/EmitGoto/EmitIf/EmitFunction/EndFunction 等 API，内部持有 VMExecutable 和 const_dedup_map_
- facts-relax-te-topi.md F-155: EmitCall 通过函数名或函数索引发射 packed function 调用
- facts-relax-te-topi.md F-158: SaveMemoryScope 为常量构建内存作用域，Get() 完成构建并 formalize
- facts-runtime-target-arith.md F-030~F-033: ffi::Module 支持 imports()、kind()、SaveToBytes()，属性掩码 kCompilationExportable/kBinarySerializable
- facts-runtime-target-arith.md F-036: 模块从字节加载通过全局函数 `"ffi.Module.load_from_bytes."+tkey`
- facts-runtime-target-arith.md F-082~F-090: RPC 模块支持远程设备上的模块通过统一 Module 接口访问，RPC_SESS_MASK=128 标记远程设备

**设计动机**：Relax 的设计目标是支持动态形状模型（如 LLM 的变长序列、目标检测的动态输出数量），这使得传统的图执行器（Graph Executor）无法胜任——图执行器要求形状在编译时固定且无控制流。VM 字节码方案在解释执行的灵活性和 AOT 编译的效率之间取得平衡：静态已知的算子调用被编译为 Call 指令（直接调用 `ffi::Function`，无解释开销），动态形状和控制流由 Goto/If 指令处理。ExecBuilder 的常量去重和寄存器检查在编译期完成，减少运行时开销。PagedKVCache 的内置则体现了 TVM 对 LLM 推理工作负载的一等支持——分页 KV 缓存是现代 LLM 推理系统的核心技术，将其放入 VM 内置函数使得所有 Relax 编译的 LLM 模型可直接受益，无需各自实现。

**跨模块影响**：
- Relax LowerRuntimeBuiltin Pass 将大多数算子映射到 VM 内置函数（Relax F-150）
- VMShapeLower Pass 将形状表达式降级为 VM 形状堆和 TIR 函数（Relax F-151），动态形状在 VM 中以形状堆上的 int64 数组表示
- StaticPlanBlockMemory Pass 规划的内存在 VM 中通过 POOLED_ALLOCATOR 池化复用（Relax F-109, Runtime F-066）
- KillAfterLastUse Pass 在张量最后一次使用后立即释放，减少 VM 的峰值内存（Relax F-148 中的 Pass 序列）
- CallTIRRewrite 插入的显式张量分配由 VM 的分配器执行（Relax F-107）
- VM Executable 可通过 Module 导入树与 TIR 编译的 DSO 模块组合，Executable.jit() 将字节码即时编译为原生 Module
- RPC 系统使 VM 可在远程设备上执行，本地通过 Module 接口透明调用远程函数（Runtime F-082~F-090）

---

## 知识地图

> 22 篇概念文档，分四批组织。每篇列出核心问题、信源文件和 Grep 验证清单（关键类/函数/宏）。

### 第一批：基础架构（5篇）

#### 00-overview.md
- **核心问题**：TVM 的整体架构分哪几层？编译流水线从前端到后端经历哪些阶段？IRModule 如何承载跨层函数？Driver 层如何路由编译请求？
- **信源**：facts-ir-tir.md, facts-relax-te-topi.md, facts-runtime-target-arith.md, facts-tvm-ffi.md
- **Grep 验证**：`tvm::IRModule`, `tvm::transform::Pass`, `tvm::Target`, `tvm::relax::Function`, `tvm::tirx::PrimFunc`, `tvm::compile`, `tvm::tirx::build`, `codegen::Build`, `BaseFuncNode`

#### 01-ffi-foundation.md
- **核心问题**：TVM-FFI 如何实现跨语言互操作？C ABI 的稳定性保证是什么？Any 标签联合体如何区分栈上 POD 和堆对象？全局函数注册表如何工作？Cython 和 Rust 绑定如何自动生成？
- **信源**：facts-tvm-ffi.md
- **Grep 验证**：`TVMFFIAny`, `TVMFFIObject`, `TVMFFIFunctionCall`, `GlobalFunctionTable`, `TVM_FFI_STATIC_INIT_BLOCK`, `refl::GlobalDef`, `ObjectArc`, `register_global_func`, `register_object`, `FunctionObj`, `AnyView`, `SafeCallContext`, `TVMFFI_VERSION`

#### 02-object-system.md
- **核心问题**：Object/ObjectRef 双层智能指针如何工作？intrusive 引用计数为何合并强弱计数为一个 u64？type_index 的三级分配策略（静态/槽位/动态）是什么？结构相等/哈希的五种 kind 各适用于什么场景？Copy-On-Write 如何支持不可变 IR 变换？
- **信源**：facts-tvm-ffi.md, facts-ir-tir.md
- **Grep 验证**：`ffi::Object`, `ffi::ObjectRef`, `TVMFFIObject`, `combined_ref_count`, `type_index`, `_type_child_slots`, `TVM_FFI_DECLARE_OBJECT_INFO_FINAL`, `TVM_DEFINE_OBJECT_REF_COW_METHOD`, `StructuralEqual`, `StructuralHash`, `kTVMFFISEqHashKindTreeNode`, `kTVMFFISEqHashKindFreeVar`, `make_object`

#### 03-pass-infrastructure.md
- **核心问题**：PassInfo 的元数据如何控制 Pass 启用/禁用？PassContext 的线程局部栈如何支持嵌套和多线程？PassInstrument 如何实现非侵入式观测？Module/Function/DataflowBlock 三级 Pass 如何创建和组合？预定义 Pipeline 有哪些？
- **信源**：facts-ir-tir.md, facts-relax-te-topi.md
- **Grep 验证**：`PassInfo`, `PassContext`, `PassInstrument`, `CreateFunctionPass`, `CreateDataflowBlockPass`, `Sequential`, `TVM_REGISTER_PASS_CONFIG_OPTION`, `EnterPassContext`, `ExitPassContext`, `PassEnabled`, `zero_pipeline`, `default_build_pipeline`

#### 04-target-codegen.md
- **核心问题**：Target/TargetKind/TargetTag 三者关系是什么？Target 如何从字符串/字典/标签构造？VirtualDevice 四元组解决什么问题？CodeGen 如何通过全局函数分派到后端？CodeGenLLVM 和 CodeGenC 的继承层次如何？Module 导入树如何序列化？
- **信源**：facts-runtime-target-arith.md, facts-relax-te-topi.md
- **Grep 验证**：`TargetNode`, `Target`, `TargetKind`, `TargetTag`, `VirtualDevice`, `TVM_REGISTER_TARGET_KIND`, `codegen::Build`, `CodeGenLLVM`, `CodeGenC`, `CodeGenCPU`, `PackImportsToC`, `PackImportsToLLVM`, `ModuleSerializer`, `target.build.`

### 第二批：TIR 与调度（6篇）

#### 05-tirx-ir.md
- **核心问题**：TIRx 的语句/表达式节点层次如何组织？SBlock/SBlockRealize 如何实现声明式计算？PrimFunc 的 buffer_map 如何处理参数解包？StmtFunctor/ExprFunctor 如何实现类型分派访问者？TIRx 与旧 TIR 的命名空间关系是什么？
- **信源**：facts-ir-tir.md
- **Grep 验证**：`tvm::tirx::StmtNode`, `tvm::tirx::SBlockNode`, `tvm::tirx::SBlockRealizeNode`, `tvm::tirx::PrimFuncNode`, `tvm::tirx::ForNode`, `tvm::tirx::BufferStoreNode`, `tvm::tirx::StmtFunctor`, `tvm::tirx::ExprFunctor`, `tvm::tirx::StmtMutator`, `TensorIntrinNode`, `ForKind`

#### 06-buffer-var-itervar.md
- **核心问题**：Var/PrimVar 的零开销检查视图如何实现？IterVar 的 9 种类型（DataPar/ThreadIndex/CommReduce 等）各允许什么操作？Buffer 的 13 个字段如何描述多维内存布局？ElemOffset 如何计算元素偏移？IndexMap 和 Layout 如何支持布局变换？
- **信源**：facts-ir-tir.md
- **Grep 验证**：`tvm::tirx::VarNode`, `tvm::tirx::PrimVar`, `tvm::tirx::IterVarNode`, `IterVarType`, `kDataPar`, `kCommReduce`, `tvm::tirx::BufferNode`, `BufferType`, `ElemOffset`, `tvm::tirx::Region`, `tvm::tirx::IndexMap`, `tvm::tirx::Layout`, `TileLayout`, `TVM_INDEX_DEFAULT_I64`

#### 07-sblock-schedule.md
- **核心问题**：SBlockNode 的 reads/writes/init 如何表达计算语义？SBlockRealize 的 predicate 如何实现条件执行？ScheduleState 的 sref 树如何组织 IR 节点？StmtSRef 如何在变换后保持引用有效性？AnalyzeRegionUpperBound/LowerBound 如何工作？
- **信源**：facts-ir-tir.md, facts-runtime-target-arith.md
- **Grep 验证**：`SBlockNode`, `SBlockRealizeNode`, `ScheduleNode`, `ScheduleStateNode`, `StmtSRef`, `stmt2ref`, `AnalyzeRegionUpperBound`, `AnalyzeRegionLowerBound`, `ProducerCoversConsumer`, `SBlockInfoCollector`, `GetSBlockAccessRegion`, `FindAnchorBlock`

#### 08-schedule-primitives.md
- **核心问题**：40+ 调度原语如何分类（循环变换/ForKind/缓存/计算位置/归约/布局）？每个原语的前置条件是什么？RV（LoopRV/SBlockRV/ExprRV）如何作为符号句柄？Trace/Instruction 如何记录和重放调度决策？采样原语如何支持自动搜索？
- **信源**：facts-ir-tir.md
- **Grep 验证**：`Schedule`, `LoopRV`, `SBlockRV`, `ExprRV`, `Trace`, `Instruction`, `Split`, `Fuse`, `Reorder`, `ComputeAt`, `CacheRead`, `CacheWrite`, `Tensorize`, `Parallel`, `Vectorize`, `Bind`, `SamplePerfectTile`, `SampleCategorical`, `ConcreteSchedule`, `TracedSchedule`

#### 09-meta-schedule.md
- **核心问题**：MetaSchedule 的自动调优流水线包含哪些组件（builder/runner/cost_model/database/search_strategy）？ScheduleRule/Mutator/Postproc 如何定义搜索空间？TuningRecord/Database 如何持久化调优经验？space_generator 如何生成调度草图？cost_model 如何预测性能而无需实际运行？
- **信源**：facts-ir-tir.md
- **Grep 验证**：`meta_schedule`, `Builder`, `Runner`, `CostModel`, `Database`, `SearchStrategy`, `ScheduleRule`, `Mutator`, `Postproc`, `SpaceGenerator`, `FeatureExtractor`, `MeasureCallback`, `TaskScheduler`, `TuningRecord`

#### 10-arith-analyzer.md
- **核心问题**：Analyzer 的七个子分析器如何协作？ConstIntBound 的 kPosInf/kNegInf 如何表示无界？ModularSet 的 coeff/base 语义是什么？RewriteSimplifier 的重写规则和扩展标志有哪些？ConstraintContext 如何管理临时约束？IntSet 的 Nothing/Everything/SinglePoint 如何使用？Z3Prover 何时参与证明？
- **信源**：facts-runtime-target-arith.md
- **Grep 验证**：`arith::Analyzer`, `AnalyzerObj`, `ConstIntBoundNode`, `ModularSetNode`, `RewriteSimplifier`, `CanonicalSimplifier`, `IntSetAnalyzer`, `TransitiveComparisonAnalyzer`, `Z3Prover`, `ConstraintContext`, `CanProve`, `Simplify`, `Bind`, `IntSet`, `IterMapExpr`, `DeduceBound`, `ProofStrength`, `DivMode`

### 第三批：Relax 与 TE（6篇）

#### 11-relax-ir.md
- **核心问题**：Relax 的表达式节点层次如何设计？Var 与 DataflowVar 的语义区别是什么？Binding/BindingBlock/DataflowBlock/SeqExpr 如何组织程序结构？FunctionNode 的 is_purity 标志影响什么？TensorType/ShapeType/AnyType 的"假设语义"是什么？MatchCast 如何实现运行时类型匹配？
- **信源**：facts-relax-te-topi.md
- **Grep 验证**：`relax::ExprNode`, `relax::VarNode`, `relax::DataflowVarNode`, `relax::BindingNode`, `relax::VarBindingNode`, `relax::MatchCastNode`, `relax::BindingBlockNode`, `relax::DataflowBlockNode`, `relax::SeqExprNode`, `relax::FunctionNode`, `relax::IfNode`, `relax::TupleNode`, `TensorTypeNode`, `ShapeTypeNode`, `kUnknownNDim`

#### 12-relax-block-builder.md
- **核心问题**：BlockBuilder 如何管理全局上下文和作用域？Emit/Normalize 管线如何将表达式转为 A-norm 形式？FNormalize/FInferType/FValidate/FLegalize 四类算子属性函数的职责边界是什么？DataflowBlockRewrite 如何支持使用点替换和死代码消除？Python 层的 FunctionScope/DataflowScope 如何工作？
- **信源**：facts-relax-te-topi.md
- **Grep 验证**：`relax::BlockBuilderNode`, `BlockBuilder::Create`, `Emit`, `EmitMatchCast`, `EmitOutput`, `Normalize`, `NormalizeArgument`, `BeginDataflowBlock`, `EndBlock`, `BeginScope`, `BeginInnerScope`, `FNormalize`, `FInferType`, `FLegalize`, `FValidate`, `DataflowBlockRewriteNode`, `ReplaceAllUses`, `RemoveUnused`

#### 13-relax-ops.md
- **核心问题**：Relax 算子如何按子目录组织（nn/tensor/vision/distributed/ccl）？OpPatternKind 的 7 种模式如何指导融合？算子属性类型（Conv2DAttrs 等）如何定义？Python 层的运算符重载如何分派到算子调用？call_tir/call_pure_packed/call_dps_packed 的区别是什么？
- **信源**：facts-relax-te-topi.md
- **Grep 验证**：`relax::Op`, `OpPatternKind`, `kElemWise`, `kBroadcast`, `kInjective`, `kCommReduce`, `kOutEWiseFusable`, `kOpaque`, `FCallPacked`, `FPrimalGradient`, `Conv2DAttrs`, `call_tir`, `call_tir_inplace`, `call_pure_packed`, `call_dps_packed`, `shape_of`, `register_gradient`

#### 14-relax-passes.md
- **核心问题**：40+ Relax Pass 如何分类（归一化/合法化/融合/内存/布局/微分/代码生成）？LegalizeOps 如何调用算子的 FLegalize？FuseOps 的融合算法如何使用 OpPatternKind？FuseTIR 如何将 Relax 子函数编译为 TIR？ToMixedPrecision 如何自动转换精度？Gradient 如何生成反向函数？DeadCodeElimination 如何追踪调用链？
- **信源**：facts-relax-te-topi.md
- **Grep 验证**：`LegalizeOps`, `FuseOps`, `FuseTIR`, `FuseOpsByPattern`, `MergeCompositeFunctions`, `Normalize`, `CanonicalizeBindings`, `EliminateCommonSubexpr`, `FoldConstant`, `DeadCodeElimination`, `ToNonDataflow`, `CallTIRRewrite`, `StaticPlanBlockMemory`, `ToMixedPrecision`, `Gradient`, `ConvertLayout`, `AlterOpImpl`, `LiftTransformParams`, `RewriteCUDAGraph`, `LambdaLift`

#### 15-te-tensor-expression.md
- **核心问题**：TE 的 Tensor/Operation 层次如何设计？ComputeOp 如何通过 axis+body 表达张量计算？PlaceholderOp/ComputeOp/ScanOp/ExternOp 各用于什么场景？Tensor::operator() 如何生成张量读取表达式？CreatePrimFunc 如何将 TE 降级为 TIR PrimFunc？Python 的 compute() 如何自动创建 IterVar？
- **信源**：facts-relax-te-topi.md, facts-ir-tir.md
- **Grep 验证**：`te::Tensor`, `te::TensorNode`, `te::Operation`, `te::OperationNode`, `te::PlaceholderOpNode`, `te::ComputeOpNode`, `te::ScanOpNode`, `te::ExternOpNode`, `te::BaseComputeOpNode`, `ProducerToBufferTransformer`, `CreateFuncInfo`, `te::placeholder`, `te::compute`, `te::scan`, `te::extern`, `create_prim_func`, `TensorSlice`, `DataProducerNode`

#### 16-topi-operator-library.md
- **核心问题**：TOPI 的标签体系（kElementWise/kBroadcast/kMatMul/kConv2dNCHW 等）如何指导调度？TOPI_DEFINE_BCAST_OP 宏如何生成广播算子重载？CommReduce 如何处理归约轴和 keepdims？softmax/dense/conv2d 等 NN 算子如何用 TE 表达？einsum 的方程字符串如何解析？
- **信源**：facts-relax-te-topi.md
- **Grep 验证**：`topi::kElementWise`, `topi::kBroadcast`, `topi::kCommReduce`, `topi::kMatMul`, `topi::kConv2dNCHW`, `topi::kEinsum`, `TOPI_DEFINE_BCAST_OP`, `TOPI_DECLARE_UNARY_OP`, `topi::broadcast_to`, `topi::relu`, `topi::softmax`, `topi::dense`, `topi::pad`, `topi::pool_grad_impl`, `topi::einsum`, `EinsumEquation`, `FReduce`, `CommReduce`

### 第四批：Runtime 与生态（5篇）

#### 17-runtime-module.md
- **核心问题**：ffi::Module 如何管理导入树和函数查找？LibraryModule 如何加载动态库并解析符号？Module 的属性掩码（Runnable/BinarySerializable/CompilationExportable）如何控制序列化？嵌入式库二进制格式（import_tree CSR + key-value）如何工作？ContextSymbolRegistry 如何支持静态链接？DeviceAPI 抽象如何统一 CPU/GPU 内存管理？
- **信源**：facts-runtime-target-arith.md, facts-tvm-ffi.md
- **Grep 验证**：`ffi::Module`, `ModuleObj`, `LibraryModuleObj`, `Module::LoadFromFile`, `ModuleGlobals`, `DeviceAPI`, `DeviceAPIManager`, `AllocDataSpace`, `FreeDataSpace`, `CopyDataFromTo`, `NDArray`, `Tensor`, `WorkspacePool`, `ThreadPool`, `save_param_dict`, `load_param_dict`, `runtime::Module`, `PackImportsToC`

#### 18-vm-bytecode.md
- **核心问题**：VM 的寄存器字节码指令集包含哪些操作码？Executable 如何组织字节码/常量池/函数表？ExecBuilder 如何发射指令并进行寄存器合法性检查？RunLoop 主循环如何调度指令？NAIVE 和 POOLED 分配器的区别是什么？VM 如何通过 JIT 将字节码编译为原生模块？
- **信源**：facts-runtime-target-arith.md, facts-relax-te-topi.md
- **Grep 验证**：`vm::VirtualMachine`, `vm::Executable`, `vm::Opcode`, `vm::Instruction`, `vm::ExecBuilderNode`, `EmitCall`, `EmitRet`, `EmitGoto`, `EmitIf`, `DeclareFunction`, `EmitFunction`, `EndFunction`, `NAIVE_ALLOCATOR`, `POOLED_ALLOCATOR`, `vm_load_executable`, `LowerRuntimeBuiltin`, `VMShapeLower`, `const_dedup_map_`

#### 19-rpc-distributed.md
- **核心问题**：RPC 的 Session/Endpoint/Channel 三层抽象如何工作？RPCObjectRef 如何管理远程对象生命周期？RPC_SESS_MASK 如何标记远程设备类型？RPCModule 如何使远程模块透明可调用？Disco 分布式运行时如何与 RPC 协同？
- **信源**：facts-runtime-target-arith.md
- **Grep 验证**：`RPCSession`, `RPCEndpoint`, `RPCChannel`, `RPCObjectRef`, `RPC_SESS_MASK`, `rpc_module`, `device_api.rpc`, `disco`, `kDLExtDev`, `RPCServer`

#### 20-tvmscript.md
- **核心问题**：TVMScript Printer 如何通过 NodeFunctor vtable 注册方言打印器？Doc 体系作为打印中间表示如何工作？IR Builder 如何分层支持 TIR/Relax 方言构建？TVM_REGISTER_SCRIPT_AS_REPR 宏如何将 Script 注册为对象的 repr？Python 端如何通过 @tvm.script 装饰器声明 IR？
- **信源**：facts-runtime-target-arith.md, facts-relax-te-topi.md
- **Grep 验证**：`Script`, `TVMScriptPrinter`, `NodeFunctor`, `vtable`, `TVM_REGISTER_SCRIPT_AS_REPR`, `PrinterConfig`, `Doc`, `IRBuilder`, `register_dialect`, `tvm.script`, `ir_builder`, `ReprPrint`

#### 21-llm-inference.md
- **核心问题**：PagedKVCache 如何实现分页式键值缓存管理？AttentionBackend 抽象如何支持不同注意力实现（FlashAttention/PagedAttention 等）？Relax 的哪些 Pass 为 LLM 推理服务（RewriteCUDAGraph/KillAfterLastUse/StaticPlanBlockMemory）？kNumInput 属性如何区分权重和激活？DecomposeOpsForInference 如何分解 Attention 等复合算子？
- **信源**：facts-runtime-target-arith.md, facts-relax-te-topi.md
- **Grep 验证**：`PagedKVCache`, `AttentionBackend`, `attn_backend`, `paged_kv_cache`, `RewriteCUDAGraph`, `KillAfterLastUse`, `kNumInput`, `kForcePure`, `DecomposeOpsForInference`, `StaticPlanBlockMemory`, `Attention`, `KVCache`, `vm.builtin`

---

## 附：跨模块依赖关系矩阵

| 概念文档 | FFI | Object | Pass | Target | TIRx | SBlock/Schedule | Arith | Relax IR | BlockBuilder | TE/TOPI | Runtime/VM |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 00-overview | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● | ● |
| 01-ffi-foundation | ● | ○ | | | | | | | | | |
| 02-object-system | ● | ● | | | | | | | | | |
| 03-pass-infrastructure | | | ● | | ○ | ○ | | ○ | | | |
| 04-target-codegen | | | | ● | ○ | | | | | | ● |
| 05-tirx-ir | | ● | | | ● | ○ | | | | | |
| 06-buffer-var-itervar | | ● | | | ● | | | | | | |
| 07-sblock-schedule | | | | | ● | ● | ● | | | | |
| 08-schedule-primitives | | | | | ● | ● | ○ | | | | |
| 09-meta-schedule | | | | ○ | ● | ● | ○ | | | | |
| 10-arith-analyzer | | | | | ○ | ○ | ● | | | | |
| 11-relax-ir | | ● | | | | | | ● | ○ | | |
| 12-relax-block-builder | | | ○ | | ○ | | | ● | ● | ○ | |
| 13-relax-ops | | | | | | | | ● | ○ | | |
| 14-relax-passes | | | ● | ○ | ● | ○ | | ● | ● | | ● |
| 15-te-tensor-expression | | ● | | | ● | | | ○ | ○ | ● | |
| 16-topi-operator-library | | | | | ○ | | ○ | | | ● | |
| 17-runtime-module | ● | ● | | | | | | | | | ● |
| 18-vm-bytecode | | | | | | | | ○ | | | ● |
| 19-rpc-distributed | ● | | | | | | | | | | ● |
| 20-tvmscript | | ● | | | ● | ○ | | ● | | | |
| 21-llm-inference | | | ● | ○ | | | | ● | ● | | ● |

> ● = 核心依赖；○ = 间接/次要依赖；空白 = 无直接依赖
