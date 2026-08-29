---
type: Concept
title: TIRx 中间表示
description: TIRx 是 TVM 的张量级中间表示，定义了表达式节点、语句节点、SBlock 声明式块、PrimFunc 函数结构及 Functor 访问者模式，是调度和代码生成的基础
tags: [tvm, tir, tirx, ir, primfunc, sblock, 中间表示, 编译器]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: ir-tir-source
    resource: "/references/ir-tir-source.md"
    title: IR 核心与 TIRx 源码
---

# TIRx 中间表示

TIRx（Tensor Intermediate Representation extended）是 TVM 编译器栈中的张量级中间表示，位于命名空间 `tvm::tirx`。它在 FFI 跨语言基座之上构建标量/缓冲区级计算描述，是 S-TIR 调度系统和后端代码生成的直接操作对象。TIRx 替代了旧版 `tvm::tir` 命名空间，在保持向后兼容的同时引入了 SBlock（Symbolic Block）声明式调度机制，将"计算什么"与"如何调度"显式分离。

## 设计理念与命名空间

TIRx 的核心设计目标是提供一种既适合人类阅读书写、又适合编译器变换的低层 IR。其设计遵循以下原则：

1. **声明式计算描述**：通过 SBlock 显式声明迭代空间、读写区域和计算体，使调度原语可基于数据依赖进行正确性验证。
2. **静态单赋值（SSA）友好**：表达式节点不可变，变换通过 Copy-On-Write 产生新节点。
3. **多层级抽象**：从标量表达式到多维缓冲区访问再到函数级结构，层次清晰。
4. **类型分派访问者**：通过 ExprFunctor/StmtFunctor 实现可扩展的遍历和变换。

TIRx 复用了 IR 核心层的部分节点：通过 `using IntImmNode = tvm::IntImmNode` 和 `using FloatImmNode = tvm::FloatImmNode` 直接复用整数字面量和浮点字面量节点 [F-099]。其他 TIRx 特有的节点（如 StringImm、Cast、SBlock）则定义在 `include/tvm/tirx/` 目录下。

## 表达式节点体系

TIRx 表达式继承自 `PrimExpr`，表示具有基本类型（Primitive Type）的计算值。所有表达式节点均继承自 `ExprNode`，包含 `ty`（类型）和 `span`（源码位置）字段 [F-003]。

### 字面量节点

- **IntImmNode**：继承自 `ExprNode`，表示整数常量，包含 `int64_t value` 字段 [F-020]。`IntImm` 提供 `Bool()`、`Int32()`、`Int64()` 静态工厂方法分别创建布尔、32 位整数、64 位整数字面量 [F-021]。FFI 层为 `IntImm` 特化了 `TypeTraits`，从 `int64_t` 自动转换时根据值范围选择 int32 或 int64 类型 [F-033]。
- **FloatImmNode**：继承自 `ExprNode`，表示浮点常量，包含 `double value` 字段 [F-023]。支持 float16、float32、bfloat16、float8 变体（e3m4/e4m3/e5m2 等）、float6_e2m3fn、float4_e2m1fn 以及自定义类型 [F-024]。
- **StringImmNode**：继承自 `ExprNode`，表示字符串常量，仅用于断言中，类型键为 `"tirx.StringImm"` [F-100]。`StringImm` 继承自 `PrimExpr`，是 `StringImmNode` 的引用类 [F-101]。

### 变量节点

- **VarNode**：继承自 `ExprNode`，表示 TIR 中的命名变量，通过地址唯一标识，包含 `name_hint` 字段 [F-106]。其 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindFreeVar`，`name_hint` 在结构相等/哈希中被忽略 [F-107]。
- **PrimVar**：继承自 `PrimExpr`，是 `VarNode` 的零开销检查视图，额外保证 `ExprNode::ty` 为 `PrimType` [F-110]。FFI 为 `PrimVar` 特化了 `TypeTraits`，在 Any 转换时动态检查底层 VarNode 的类型是否为 PrimType [F-111]。

### 算术与逻辑节点

TIRx 定义了模板基类 `BinaryOpNode<T>`，包含 `a`（左操作数）和 `b`（右操作数），子类通过 `_type_key` 静态成员指定类型键 [F-103]。具体的二元运算节点包括：

| 节点类 | 类型键 | 语义 |
|--------|--------|------|
| `AddNode` | `"tirx.Add"` | 加法 [F-104] |
| `SubNode` | `"tirx.Sub"` | 减法 [F-104] |
| `MulNode` | `"tirx.Mul"` | 乘法 [F-104] |
| `DivNode` | `"tirx.Div"` | 截断除法（C 标准 trunc div）[F-105] |
| `ModNode` | `"tirx.Mod"` | 取模 |
| `MinNode` | `"tirx.Min"` | 最小值 |
| `MaxNode` | `"tirx.Max"` | 最大值 |

`DivNode` 的语义遵循 C 标准的截断除法（trunc div），区别于 Python 的地板除法 [F-105]。所有算术和比较运算符均对索引类型（int32/int64）执行立即常量折叠（eager constant folding）[F-032]。

### 其他表达式节点

- **CastNode**：继承自 `ExprNode`，表示类型转换，包含 `PrimExpr value` 字段，类型键为 `"tirx.Cast"` [F-102]。
- **SelectNode**：三元选择表达式（条件 ? a : b）。
- **CallNode**：函数调用，包含 `op`（被调用者）、`args`（参数数组）、`attrs`（属性）、`ty_args`（类型参数）[F-017]。
- **LetNode**：let 绑定表达式。
- **ReduceNode**：归约表达式。
- **ShuffleNode**：向量重排。
- **BroadcastNode**：标量广播为向量。

IR 表达式层重载了全套算术运算符（`+`、`-`、`*`、`/`、`<<`、`>>`）、比较运算符（`>`、`>=`、`<`、`<=`、`==`、`!=`）、逻辑运算符（`&&`、`||`、`!`）和位运算符（`&`、`|`、`^`、`~`）[F-029][F-030][F-031]。

## 语句节点体系

`StmtNode` 是所有 TIR 语句的基类，继承自 `ffi::Object`，包含 `mutable Span span` 字段，预留 15 个子类槽位 [F-126]。类型键为 `"tirx.Stmt"`，`_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode` [F-127]。

### 核心语句节点

| 节点类 | 类型键 | 职责 |
|--------|--------|------|
| `EvaluateNode` | `"tirx.Evaluate"` | 表达式求值语句（主要用于有副作用的 Call）[F-137] |
| `BufferStoreNode` | `"tirx.BufferStore"` | 多维缓冲区写入，含 buffer/value/indices/predicate [F-131] |
| `BufferRealizeNode` | - | 缓冲区区域实现 |
| `AllocateNode` | - | 原始内存分配 |
| `DeclBufferNode` | `"tirx.DeclBuffer"` | 声明缓冲区可在 body 中使用 [F-132] |
| `AllocBufferNode` | `"tirx.AllocBuffer"` | 分配并声明缓冲区，含 annotations [F-133] |
| `ForNode` | - | 循环语句 |
| `WhileNode` | `"tirx.While"` | while 循环 [F-142] |
| `IfThenElseNode` | `"tirx.IfThenElse"` | 条件分支 [F-138] |
| `SeqStmtNode` | `"tirx.SeqStmt"` | 语句序列 [F-135] |
| `AssertStmtNode` | `"tirx.AssertStmt"` | 断言语句 [F-130] |
| `AttrStmtNode` | `"tirx.AttrStmt"` | 属性语句 [F-129] |
| `SBlockNode` | `"tirx.SBlock"` | 声明式调度块 [F-148] |
| `SBlockRealizeNode` | `"tirx.SBlockRealize"` | 块实例化 [F-150] |
| `LaunchThreadNode` | - | 线程启动 |
| `BindNode` | - | 变量绑定 [F-128] |
| `BreakNode` | `"tirx.Break"` | break 控制流 [F-143] |
| `ContinueNode` | `"tirx.Continue"` | continue 控制流 [F-143] |

### SeqStmt 语句序列

`SeqStmtNode` 包含 `ffi::Array<Stmt> seq`，提供 `size()` 和 `operator[]` 方法 [F-135]。`SeqStmt::Flatten()` 静态模板方法递归展平参数中的数组和 SeqStmt，忽略空指针和 `Evaluate(0)`（no-op），单元素时直接返回该元素 [F-136]。

### BufferStore 缓冲区写入

`BufferStoreNode` 表示多维缓冲区写入，包含 `buffer`（目标缓冲区）、`value`（写入值）、`indices`（多维索引）、`predicate`（可选谓词掩码）[F-131]。谓词支持掩码写入，在 GPU 向量化和边界处理中使用。

### AllocBuffer 缓冲区分配

`AllocBufferNode` 分配并声明缓冲区，包含 `buffer`（Buffer 对象）和 `annotations`（注解映射）[F-133]。`AllocBuffer::ConstantAllocationSize()` 在所有形状维度为常量时返回总元素数，否则返回 `std::nullopt` [F-134]。

## ForKind 循环类型

`ForKind` 枚举定义了 5 种循环类型 [F-139]：

| 枚举值 | 数值 | 语义 |
|--------|------|------|
| `kSerial` | 0 | 串行循环 |
| `kParallel` | 1 | CPU 多线程并行 |
| `kVectorized` | 2 | SIMD 向量化 |
| `kUnrolled` | 3 | 循环展开 |
| `kThreadBinding` | 4 | GPU 线程绑定 |

`ForNode` 包含 `loop_var`（PrimVar）、`min`、`extent`、`kind`（ForKind）、`body`、`thread_binding`（可选 IterVar）、`annotations`、`step`（可选步长，默认为 1）[F-140]。`HasTrivialStep()` 检查循环是否没有非平凡步长 [F-141]。这五种 ForKind 是调度原语 Parallel/Vectorize/Bind/Unroll 的操作目标。

## SBlock 声明式块

SBlock（Symbolic Block）是 TIRx 的核心创新，继承自 `StmtNode`，是 TensorIR 调度系统的基本计算单元 [F-146]。

### SBlockNode 结构

`SBlockNode` 包含以下字段 [F-146]：

- **iter_vars**：`IterVar` 数组，声明块的迭代空间
- **reads**：`BufferRegion` 数组，声明块读取的缓冲区区域
- **writes**：`BufferRegion` 数组，声明块写入的缓冲区区域
- **name_hint**：块名称提示
- **alloc_buffers**：块内分配的缓冲区
- **match_buffers**：缓冲区匹配声明
- **annotations**：注解映射
- **init**：可选初始化语句，在归约块的第一次迭代时执行 [F-147]
- **body**：块计算体

`init` 字段区分了归约块的初始化阶段和更新阶段：在归约块的第一次迭代时执行 init 逻辑，后续迭代执行 body [F-147]。非归约块的 init 为 `nullopt`。

### SBlockRealize 块实例化

`SBlockRealizeNode` 表示块在特定绑定值下的执行，包含 [F-149]：

- **iter_values**：迭代变量绑定值数组
- **predicate**：谓词条件，为 true 时块才执行 [F-150]
- **block**：被实现的 SBlock

SBlockRealize 实现了块的参数化实例化——同一个 SBlock 可在不同的迭代值绑定下多次执行，predicate 支持条件执行（如边界检查）。

### BufferRegion 缓冲区区域

`BufferRegionNode` 表示多维缓冲区访问区域，包含 `buffer` 和 `region`（Range 数组）[F-144]。`BufferRegion::FullRegion(buffer)` 创建覆盖整个缓冲区的区域，`FromPoint(buffer, indices)` 创建单点访问区域 [F-145]。SBlock 的 reads/writes 声明使得调度系统可以在不分析块体的情况下推导数据依赖。

## PrimFunc 函数结构

`PrimFuncNode` 继承自 `BaseFuncNode`，是包含 TIR 语句的基本函数 [F-153]。

### 字段结构

`PrimFuncNode` 包含 [F-153]：

- **params**：`Var` 数组，函数参数列表
- **ret_type**：返回类型，默认为 Missing
- **buffer_map**：`Var→Buffer` 映射，参数到缓冲区的绑定
- **body**：`Stmt`，函数体
- **attrs**：函数属性（继承自 BaseFuncNode）
- **span**：源码位置

### buffer_map 参数解包

`buffer_map` 提供参数解包和约束检查功能：首次出现的变量定义 Buffer 字段，重复出现转换为运行时断言 [F-154]。这种设计使得 PrimFunc 可以同时接收数据指针（Var）和对应的缓冲区描述（Buffer），在函数入口处自动验证参数形状和类型约束。

### 结构相等与哈希

`PrimFuncNode::SEqual` 依次比较 attrs、params（递归）、ret_type、buffer_map、body；`SHash` 按相同顺序计算哈希 [F-155]。`func_type_annotation()` 从参数 Vars 直接派生函数类型注解，无需类型推断 [F-156]。

`PrimFunc` 类型键为 `"tirx.PrimFunc"`，构造函数参数依次为 params、body、ret_type、buffer_map、attrs、span [F-157]。

### TensorIntrin 张量化内建函数

`TensorIntrinNode` 表示张量化内建函数，包含 `desc`（描述计算的 PrimFunc）和 `impl`（实现执行的 PrimFunc），类型键为 `"tirx.TensorIntrin"` [F-158]。这种描述与实现分离的设计使得调度原语 `Tensorize` 可以将计算块替换为特定硬件的张量指令。

## Buffer 多维内存布局

`BufferNode` 继承自 `ffi::Object`，是 TIRx 描述多维内存布局的核心数据结构 [F-122]。

### 13 个字段

Buffer 构造函数接收 13 个参数 [F-125]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | Var | 数据指针变量 |
| `dtype` | PrimType | 元素数据类型 |
| `shape` | Array<PrimExpr> | 形状数组 |
| `strides` | Array<PrimExpr> | 步幅数组 |
| `elem_offset` | PrimExpr | 元素偏移 |
| `name` | String | 名称 |
| `data_alignment` | int | 数据对齐（字节） |
| `offset_factor` | int | 偏移因子 |
| `buffer_type` | BufferType | 缓冲区类型 |
| `axis_separators` | Array<IntImm> | 轴分隔符 |
| `span` | Span | 源码位置 |
| `layout` | Layout | 布局映射 |
| `allocated_addr` | Var? | 分配地址 |

### BufferType

`BufferType` 枚举定义了 `kDefault=1` 和 `kAutoBroadcast=2`（自动广播维度为 1 的轴）两种缓冲区类型 [F-121]。

### ElemOffset 元素偏移计算

`BufferNode::ElemOffset(index, inner)` 计算给定索引的缓冲区偏移量（以元素为单位），`inner=true` 时忽略 `elem_offset` [F-123]。偏移计算综合 shape、strides 和 elem_offset，支持复杂的多维内存布局。

默认索引类型由宏 `TVM_INDEX_DEFAULT_I64` 控制，默认为 1（int64），可通过编译选项改为 int32 [F-120]。

## Functor 访问者模式

TIRx 提供了完整的类型分派访问者体系，支持 IR 的遍历和变换。

### ExprFunctor 表达式访问者

`ExprFunctor` 是 TIR 表达式的类型分派访问者基类，支持根据表达式运行时类型调用不同的 `VisitExpr` 重载 [F-162]。它有两个主要子类：

- **ExprVisitor**：继承自 `ExprFunctor`，提供表达式的只读遍历，默认递归访问子表达式 [F-163]。
- **ExprMutator**：继承自 `ExprFunctor`，提供表达式的可变遍历，默认递归访问并返回变换后的子表达式 [F-164]。

### StmtFunctor 语句访问者

`StmtFunctor` 是 TIR 语句的类型分派访问者基类，类似于 ExprFunctor 但针对语句节点 [F-165]。它有两个主要子类：

- **StmtVisitor**：继承自 `StmtFunctor`，提供语句的只读遍历 [F-166]。
- **StmtMutator**：继承自 `StmtFunctor`，提供语句的可变遍历 [F-167]。

Functor 模式是 TIRx 所有 Pass 和分析的基础——每个 Pass 通过继承 Visitor 或 Mutator 并重写感兴趣的节点方法来实现特定的变换逻辑。

## TIRx Op 与内建函数

TIRx 提供 `add()`、`sub()`、`mul()`、`div()` 等算术 Op 函数，对索引类型执行立即常量折叠 [F-159]。同时提供 `logical_and()`、`logical_or()`、`if_then_else()` 等逻辑 Op 函数 [F-160]。

内建函数（builtin）以 `Op` 形式定义，包括 `ret()`、`thread_return()`、`continue_loop()`、`break_loop()`、位运算函数、`address_of()` 等内存访问函数 [F-161]。这些内建函数在 LowerTVMBuiltin Pass 中被降级为具体的后端实现。

## Attr 键常量

TIRx 在 `tirx::attr` 命名空间定义了属性键常量，包括 `buffer_bound`（缓冲区边界标记）、`compute_scope`（计算范围标记）、`device_id`（设备 ID）、`device_scope`（设备范围标记）、`device_type`（设备类型）等 [F-152]。这些属性键在 AttrStmt 中使用，传递设备和调度相关的元信息。

## 相关概念

- [Buffer/Var/IterVar 核心类型](/concepts/06-buffer-var-itervar.md)
- [SBlock 声明式调度](/concepts/07-sblock-schedule.md)
- [调度原语](/concepts/08-schedule-primitives.md)
- [Pass 基础设施](/concepts/03-pass-infrastructure.md)
