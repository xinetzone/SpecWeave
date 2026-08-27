---
type: Concept
title: Buffer/Var/IterVar 核心类型
description: TIRx 的变量系统、迭代变量九种类型、Buffer 十三字段多维内存布局描述、BufferRegion/Range 区域表示以及 Layout/IndexMap 布局变换机制
tags: [tvm, tir, buffer, var, itervar, layout, indexmap, 内存布局]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: ir-tir-source
    resource: "/references/ir-tir-source.md"
    title: IR 核心与 TIRx 源码
---

# Buffer/Var/IterVar 核心类型

TIRx 中的变量、迭代变量和缓冲区是构成张量计算描述的基础数据类型。Var/PrimVar 提供标量变量抽象，IterVar 定义迭代空间及其语义约束，Buffer 以 13 个字段完整描述多维内存布局。这些类型共同支撑了 SBlock 的声明式计算描述和调度原语的正确性验证。

## Var/PrimVar 变量系统

### VarNode 命名变量

`VarNode` 继承自 `ExprNode`，表示 TIR 中的命名变量，通过地址唯一标识，包含 `name_hint` 字段 [F-106]。变量的相等性和哈希基于对象指针而非名称，因此同名变量如果是不同对象则不相等。`VarNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindFreeVar`，`name_hint` 在结构相等/哈希中被忽略 [F-107]。

`Var` 类型键为 `"tirx.Var"`，有 1 个子类槽位（`_type_child_slots = 1`）[F-108]。Var 提供以下方法创建副本 [F-109]：

- **copy_with_name**：创建改名的副本
- **CopyWithSuffix**：添加名称后缀
- **copy_with_dtype**：创建改类型的副本

Var 特化了 `std::hash` 和 `std::equal_to`，使用指针相等/哈希，允许作为 STL 容器的键 [F-113]。

### PrimVar 零开销检查视图

`PrimVar` 继承自 `PrimExpr`，是 `VarNode` 的零开销检查视图，额外保证 `ExprNode::ty` 为 `PrimType` [F-110]。这种设计模式允许 VarNode 在不同上下文中以不同类型视图出现：当用于基本类型表达式时作为 PrimVar，当用于指针/句柄时作为 Var。

FFI 为 `PrimVar` 特化了 `TypeTraits`，在 Any 转换时动态检查底层 VarNode 的类型是否为 PrimType [F-111]。这种动态检查确保了跨语言边界的类型安全，同时不增加运行时开销（检查仅在 FFI 边界发生）。

### Region 多维区域

`Region` 类型别名定义为 `ffi::Array<Range>`，表示多维区域 [F-112]。每个 Range 描述一个维度的范围，Region 是 BufferRegion 的组成部分，用于声明 SBlock 的读写区域。

## IterVar 迭代变量

IterVar 是 TIRx 调度系统的核心概念，它不仅表示循环变量，还携带迭代语义类型，决定调度原语可对其执行的操作。

### IterVarType 九种类型

`IterVarType` 枚举定义了 9 种迭代变量类型 [F-114]：

| 枚举值 | 数值 | 语义 | 允许的操作 |
|--------|------|------|-----------|
| `kDataPar` | 0 | 数据并行 | 所有 IterVar 操作 [F-115] |
| `kThreadIndex` | 1 | 线程索引 | 禁止 split/fuse/vectorize/parallel [F-115] |
| `kCommReduce` | 2 | 通信归约 | 禁止 parallel/vectorize [F-115] |
| `kOrdered` | 3 | 有序迭代 | 禁止 reorder/parallel/vectorize [F-115] |
| `kRoot` | 4 | 根迭代 | - |
| `kOpaque` | 5 | 不透明 | 禁止所有操作和 compute_at [F-115] |
| `kUnrolled` | 6 | 展开迭代 | - |
| `kVectorized` | 7 | 向量化迭代 | - |
| `kParallelized` | 8 | 并行化迭代 | - |
| `kTensorized` | 9 | 张量化迭代 | - |

注：根据事实文件，枚举值 kDataPar=0 到 kTensorized=8 共 9 种，其中 kRoot 的具体操作限制在事实文件中未单独列出。

这些类型约束是调度正确性的基础。例如，归约迭代（kCommReduce）不能被并行化或向量化，因为这会导致数据竞争；不透明迭代（kOpaque）禁止所有变换，因为其迭代空间和依赖关系无法静态分析。

### IterVarNode 结构

`IterVarNode` 继承自 `PrimExprConvertibleNode`，包含以下字段 [F-116]：

- **dom**：`Range`，迭代变量的域（范围）
- **var**：`PrimVar`，内部循环变量
- **iter_type**：`IterVarType`，迭代类型
- **thread_tag**：线程标签（用于 GPU 线程绑定）
- **span**：源码位置

`IterVarNode::ToPrimExpr()` 返回内部的 `var`，实现了 `PrimExprConvertibleNode` 接口 [F-117]。`IterVar` 类型键为 `"tirx.IterVar"`，提供到 `PrimExpr` 的隐式转换运算符 [F-118]。`IterVarType2String()` 函数将 IterVarType 枚举值转换为可读字符串 [F-119]。

### SBlock 中的 iter_vars

在 SBlock 中，`iter_vars` 是 `IterVar` 数组，声明块的迭代空间。每个迭代变量有明确的类型（数据并行、归约等），调度系统根据这些类型决定哪些变换是合法的。SBlockRealize 的 `iter_values` 数组为每个 IterVar 提供具体的绑定值。

## Buffer 多维内存布局

Buffer 是 TIRx 中描述多维数组内存布局的核心结构。与 DLTensor 不同，Buffer 不仅包含数据指针和形状，还包含步幅、对齐、偏移因子、布局映射等完整信息，支持复杂的内存访问模式。

### BufferNode 字段

`BufferNode` 继承自 `ffi::Object`，包含以下字段 [F-122]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | Var | 数据指针变量，指向分配的内存 |
| `dtype` | PrimType | 元素数据类型（如 float32、int32） |
| `shape` | Array<PrimExpr> | 多维形状，每个维度的大小 |
| `strides` | Array<PrimExpr> | 多维步幅，相邻元素间的距离 |
| `elem_offset` | PrimExpr | 元素偏移量，缓冲区起始位置 |
| `name` | String | 缓冲区名称 |
| `data_alignment` | IntImm | 数据对齐要求（字节数） |
| `offset_factor` | IntImm | 偏移因子，elem_offset 必须是其倍数 |
| `buffer_type` | BufferType | 缓冲区类型（默认/自动广播） |
| `axis_separators` | Array<IntImm> | 轴分隔符，用于分层内存 |
| `layout` | Layout | 布局映射（可选） |
| `allocated_addr` | Var? | 预分配地址（可选） |
| `span` | Span | 源码位置 |

Buffer 的类型键为 `"tirx.Buffer"`，`_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode` [F-124]。构造函数接收 13 个参数 [F-125]。

### 内存布局参数详解

**strides（步幅）**：对于形状为 `(M, N)` 的二维行优先数组，strides 为 `(N, 1)`。strides 可以大于紧凑布局所需值，用于描述填充（padding）或切片视图。当 strides 为空时，表示紧凑行优先布局。

**elem_offset（元素偏移）**：缓冲区数据指针指向的内存起始位置与第一个元素之间的偏移（以元素为单位）。这在缓冲区视图和子数组场景中使用。

**data_alignment（数据对齐）**：数据指针的内存对齐要求（以字节为单位）。例如，alignment=8 表示数据指针按 8 字节对齐。代码生成器利用此信息选择对齐的加载/存储指令。

**offset_factor（偏移因子）**：elem_offset 必须是此值的倍数。这在某些硬件后端的地址计算中有用。

**axis_separators（轴分隔符）**：将维度分为多个组，每组对应不同的内存层次。例如，在 GPU 共享内存中，前两个维度可能对应共享内存布局，后两个维度对应寄存器布局。

### BufferType

`BufferType` 枚举定义了两种缓冲区类型 [F-121]：

- **kDefault=1**：标准缓冲区
- **kAutoBroadcast=2**：自动广播维度为 1 的轴，在访问时自动扩展

### ElemOffset 元素偏移计算

`BufferNode::ElemOffset(index, inner)` 计算给定多维索引的线性偏移量（以元素为单位）[F-123]。当 `inner=true` 时忽略 `elem_offset`，仅计算索引本身的偏移。偏移计算综合 shape、strides 和 elem_offset：

```text
offset = elem_offset + sum(index[i] * strides[i])
```

此方法在代码生成时被调用，将多维缓冲区访问降级为线性内存地址。

### 默认索引类型

默认索引类型由宏 `TVM_INDEX_DEFAULT_I64` 控制，默认为 1（int64），可通过编译选项改为 int32 [F-120]。int64 索引支持大张量，但在某些嵌入式设备上 int32 可减少寄存器压力。

## BufferRegion 与 Range

### Range 一维范围

`RangeNode` 继承自 `ffi::Object`（非 ExprNode），表示一维范围，包含 `min`、`extent`、`span` 字段 [F-026]。`Range` 引用类提供 `FromMinExtent()` 静态方法和 `(begin, end)` 构造函数，自动计算 extent = end - begin [F-027]。RangeNode 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode`，span 字段在相等/哈希中被忽略 [F-028]。

### BufferRegion 缓冲区区域

`BufferRegionNode` 表示多维缓冲区访问区域，包含 `buffer` 和 `region`（Range 数组）[F-144]。它是 SBlock 读写声明的基本单位。BufferRegion 提供两个静态工厂方法 [F-145]：

- **FullRegion(buffer)**：创建覆盖整个缓冲区的 BufferRegion，每个维度的范围为 `[0, shape[i])`
- **FromPoint(buffer, indices)**：创建单点访问区域，每个维度的范围为 `[indices[i], indices[i]+1)`

在调度过程中，系统通过分析 BufferRegion 来确定数据依赖关系。例如，ProducerCoversConsumer 检查逐维比较生产者和消费者的 BufferRegion，验证生产者的写入区域是否覆盖消费者的读取区域。

## Layout 布局变换

Layout 系统描述张量逻辑形状与物理内存布局之间的映射关系，是张量化和硬件特定优化的基础。

### Layout 类层次

`Layout` 类层次包括基类 `Layout` 及其子类 [F-171]：

- **TileLayout**：分块布局，将维度拆分为固定大小的块
- **SwizzleLayout**：交错布局，支持硬件特定的地址交错模式
- **ComposeLayout**：组合布局，将多个 Layout 组合

Layout 支持以下操作：

- **apply**：将布局应用于形状或索引
- **tile**：对维度进行分块
- **slice**：对布局进行切片

### IndexMap 索引重映射

`IndexMap` 表示缓冲区索引的重映射，支持 [F-172]：

- **map_indices**：映射索引
- **map_ranges**：映射范围
- **map_shape**：映射形状
- **逆映射计算**：自动推导反向索引变换

IndexMap 在调度原语 `TransformLayout` 和 `TransformBlockLayout` 中使用，允许用户定义自定义的内存布局变换。`TransformBlockLayout` 要求 IndexMap 是双射仿射变换，需要提供逆映射 [F-244]。

### Layout 与 Buffer 的关系

Buffer 的 `layout` 字段可选地关联一个 Layout 对象，描述缓冲区的物理布局。当 layout 存在时，代码生成器使用 layout 映射逻辑索引到物理地址。axis_separators 与 layout 协同工作，将多维索引空间分层到不同的内存层次。

## 执行作用域

虽然不是核心类型，但执行作用域与 IterVar 和 Buffer 密切相关。

### ScopeKind 作用域层次

`ScopeKind` 枚举定义了 GPU 等并行设备的执行作用域层次 [F-173]：

- `kCluster`：集群级
- `kCta`：线程块级（CUDA Thread Block）
- `kWarpgroup`：线程束组级
- `kWarp`：线程束级
- `kThread`：线程级

`ScopeBinding` 表示父子作用域关系，用于管理线程和内存层次 [F-174]。这些作用域通过 AttrStmt 和 thread_binding 与 IterVar 关联。

### ActiveSet 与 ExecContext

`ActiveSet` 表示活动线程集合，由 `TileLayout` 定义，包含 shard、replica 和 offset 信息 [F-175]。`ExecContext` 表示执行上下文，包含活动线程集（ActiveSet）、作用域类型（ScopeKind）和 split 信息，用于调度中追踪线程活动 [F-176]。这些结构主要在 GPU 自动调度（如 dlight）中使用。

## 类型间协作关系

Var、IterVar 和 Buffer 在 TIRx 中形成紧密的协作关系：

1. **Buffer 持有 Var**：Buffer 的 `data` 字段是 Var 类型，表示数据指针。`allocated_addr` 也可以是 Var，表示预分配的地址。
2. **IterVar 持有 PrimVar**：IterVar 内部的 `var` 字段是 PrimVar，在循环体中作为循环变量使用。
3. **SBlock 声明显式依赖**：SBlock 的 iter_vars 是 IterVar 数组，reads/writes 是 BufferRegion 数组，显式声明块对缓冲区的访问模式。
4. **PrimFunc 的 buffer_map 绑定**：PrimFunc 的参数（Var）通过 buffer_map 绑定到 Buffer，建立函数参数与内存描述的关联。

这种显式声明设计是 TIRx 与传统命令式 IR 的关键区别——编译器不需要分析函数体就能确定数据依赖和内存访问模式，从而使调度原语可以在变换前进行严格的正确性验证。

## 相关概念

- [TIRx 中间表示](/concepts/05-tirx-ir.md)
- [SBlock 声明式调度](/concepts/07-sblock-schedule.md)
- [调度原语](/concepts/08-schedule-primitives.md)
- [Arith 整数分析器](/concepts/10-arith-analyzer.md)
