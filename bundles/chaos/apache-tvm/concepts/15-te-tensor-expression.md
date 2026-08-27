---
type: Concept
title: TE 张量表达式
description: TVM TE 张量表达式 DSL，涵盖 Placeholder/ComputeOp/TensorComputeOp/ScanOp/ExternOp、compute() 声明式计算、scan() 循环计算及 create_primfunc 降级
tags: [tvm, te, tensor-expression, dsl, compute, scan, primfunc, lowering]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# TE 张量表达式

TE（Tensor Expression）是 TVM 的张量计算声明式领域特定语言（DSL），定义于 `include/tvm/te/` 和 `python/tvm/te/`。它允许用户以类似数学公式的方式描述张量上的逐元素计算、归约和扫描操作，而无需手动编写循环嵌套。TE 描述的计算会被降级为 TIR PrimFunc，随后通过调度原语进行循环优化。TE 是连接高层算子定义与底层 TIR 优化的桥梁，也是 TOPI 算子库的构建基础。

## 核心概念：Tensor 与 Operation

TE 的数据模型建立在两个核心抽象之上：`Operation` 描述计算操作，`Tensor` 表示操作的输出张量。

### Tensor

`TensorNode` 继承自 `DataProducerNode`，包含四个字段 [F-165]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `shape` | Array\<PrimExpr\> | 张量形状 |
| `dtype` | PrimType | 元素数据类型，默认 Void |
| `op` | Operation | 产生该张量的操作 |
| `value_index` | int | 输出索引，默认 0（支持多输出操作） |

TensorNode 实现了 `GetShape()`、`GetDataType()`、`ToPrimExpr()`、`GetNameHint()` 方法，类型键为 `"te.Tensor"` [F-166]。

`Tensor` 类提供丰富的索引语法 [F-167][F-168]：
- `tensor(i, j)`：接受可变参数 PrimExpr 索引，返回表示张量读取的 PrimExpr。
- `tensor[Array<PrimExpr>]`：接受索引数组的重载。
- `tensor[Array<PrimVar>]`：接受变量数组的重载。
- `IndexWithNegativeIndices()`：支持负索引（从末尾偏移），提供三个对应重载 [F-169]。

`Tensor::Slice` 内部类支持 `Tensor[x][y][z]` 链式索引语法糖 [F-170][F-171]。Slice 固定前 k 个坐标，通过 `operator PrimExpr()` 隐式转换为完整索引表达式。Slice 还支持一元运算符（`!`、`-`）和二元运算符（`+`、`-`、`*`、`==`、`<=`、`>=`）的重载 [F-174]，使切片上的表达式计算更自然。

`Tensor::ndim()` 内联方法返回 `shape.size()` [F-172]。Tensor 的相等比较先比较指针，再比较 `op` 和 `value_index`；若两个 tensor 的 op 都未定义则返回 false [F-173]。

### Operation

`OperationNode` 是所有操作节点的抽象基类，定义于 `include/tvm/te/operation.h`，包含 `name`、`tag`、`attrs` 三个字段 [F-176]。纯虚方法包括：
- `num_outputs()`：输出数量。
- `output_dtype(i)`：第 i 个输出的数据类型。
- `output_shape(i)`：第 i 个输出的形状。
- `InputTensors()`：输入张量列表。

`Operation` 类提供 `output(size_t i)` 方法获取第 i 个输出张量 [F-164]。一个 Operation 可以产生多个输出 Tensor（如 scan 的状态和输出），通过 `value_index` 区分。

`TensorDom` 结构体存储张量各轴边界的并集，包含 `std::vector<std::vector<IntSet>> data` [F-175]，用于调度时的迭代域分析。

## Operation 层级

TE 定义了四种具体的 Operation 类型，构成操作层次结构：

### PlaceholderOp：输入占位符

`PlaceholderOpNode` 继承自 OperationNode，包含 `shape` 和 `dtype` 字段，表示计算图的输入张量 [F-177]。PlaceholderOp 没有输入，是计算图的源节点。

`PlaceholderOp` 构造函数接受 `name`、`shape`、`dtype` 三个参数 [F-178]。在 Python 中，`placeholder()` 函数默认 dtype 为 `"float32"`，调用 `_ffi_api.Placeholder` 创建占位张量 [F-190]：

```python
A = te.placeholder((M, K), name="A", dtype="float32")
B = te.placeholder((K, N), name="B")
```

### ComputeOp：逐标量计算

`ComputeOpNode` 继承自 `BaseComputeOpNode`（后者继承 OperationNode），是最常用的操作类型，表示在特定域上逐标量计算的张量操作 [F-180]。

`BaseComputeOpNode` 包含两个字段 [F-179]：
- `axis`：Array\<IterVar\>，空间迭代变量。
- `reduce_axis`：Array\<IterVar\>，归约迭代变量。

`ComputeOpNode` 额外包含 `body`（Array\<PrimExpr\>）字段，表示每个输出元素的计算公式 [F-180]。ComputeOp 构造函数接受 `name`、`tag`、`attrs`、`axis`、`body` [F-181]。

Python 的 `compute()` 函数是创建 ComputeOp 的主要接口 [F-191]：

```python
C = te.compute(
    (M, N),
    lambda i, j: te.sum(A[i, k] * B[k, j], axis=k),
    name="C"
)
```

`compute()` 接受 `shape`、`fcompute`、`name`、`tag`、`attrs`、`varargs_names` 参数。它通过 `inspect.getfullargspec` 解析 fcompute 的参数列表，自动为每个维度创建 IterVar。若 fcompute 返回单个 PrimExpr，生成单输出 Tensor；若返回 PrimExpr 列表/元组，生成多输出 Tensor 元组。

### ScanOp：扫描/循环计算

`ScanOpNode` 继承自 OperationNode，表示符号扫描操作，用于实现 RNN、cumsum 等具有时序依赖的计算 [F-182]。它包含以下字段：

| 字段 | 说明 |
|------|------|
| `scan_axis` | 扫描轴（时间维） |
| `init` | 初始状态张量 |
| `update` | 更新函数（描述时间步 t 的状态更新） |
| `state_placeholder` | 状态占位符 |
| `inputs` | 外部输入张量 |
| `spatial_axis_` | 空间轴 |

ScanOp 的语义为：沿 scan_axis 迭代，每个时间步使用上一步的状态和当前输入计算新状态。`ScanOp` 构造函数接受 `name`、`tag`、`attrs`、`axis`、`init`、`update`、`state_placeholder`、`input` [F-183]。

Python 的 `scan()` 函数创建扫描操作 [F-192]，接受 `init`、`update`、`state_placeholder`、`inputs`、`name`、`tag`、`attrs`。init/update/state_placeholder/inputs 可为单个 Tensor 或列表，内部自动转换为列表。

### ExternOp：外部算子

`ExternOpNode` 继承自 OperationNode，表示不可分割的外部计算 [F-184]。它包含：
- `inputs`：输入张量。
- `input_placeholders`：输入占位符。
- `output_placeholders`：输出占位符（描述输出形状和类型）。
- `body`：Stmt，TIR 语句体，描述具体实现。

ExternOp 用于包装无法用 TE compute 表达的计算（如调用外部库、手写汇编等）。构造函数接受 `name`、`tag`、`attrs`、`inputs`、`input_placeholders`、`output_placeholders`、`body` [F-185]。

## TE→TIR Lowering

TE 描述的是"计算什么"，需要降级为 TIR PrimFunc 才能进行调度和代码生成。降级逻辑实现于 `src/te/operation/create_primfunc.cc`。

### ProducerToBufferTransformer

`ProducerToBufferTransformer` 继承自 `StmtExprMutator`，将 TE 层面的 `ProducerLoad`/`ProducerStore` 转换为 TIR 层面的 `BufferLoad`/`BufferStore` [F-186]。它通过 `tensor2buffers_` 映射查找每个 Tensor 对应的 Buffer，完成从生产者-消费者抽象到具体内存访问的转换。

### BufferSubstituter

`BufferSubstituter` 继承自 `StmtExprMutator`，根据 `var_map_` 和 `buffer_map_` 重写 buffer 和 buffer 变量访问 [F-187]。这在调度过程中用于替换缓冲区声明（如缓存读写时创建的新缓冲区）。

### CreateFuncInfo

`CreateFuncInfo` 结构体存储降级过程中的共享信息 [F-188]：
- `arg_list`：Tensor 数组，函数参数列表。
- `tensor2buffers`：Tensor 到 Buffer 的映射。
- `transformer`：ProducerToBufferTransformer 实例。
- `root_alloc`：根分配 Buffer 数组。
- `name_supply`：名称供应器。

### LayoutFreePlaceholdersNormalizer

`LayoutFreePlaceholdersNormalizer` 继承自 `StmtMutator`，处理 layout free placeholder [F-189]。它为函数附加 `layout_free_buffers` 属性（索引列表），标记哪些参数的布局不被函数假设，允许外部进行布局重排。

### create_prim_func

`create_prim_func` 是 TE→TIR 降级的入口函数，接受 TE Tensor 列表（输出张量），遍历其依赖的 Operation 图，生成完整的 TIR PrimFunc。生成的 PrimFunc 包含：
- 参数列表（所有 PlaceholderOp 和输出 Tensor）。
- Buffer 映射（参数到 Buffer）。
- 函数体（嵌套循环，由 ComputeOp/ScanOp 转换而来）。

Python 端通过 `te.create_prim_func` 调用此功能。

## Python TE 命名空间

Python `te` 命名空间导出以下组件 [F-193]：

**计算函数**：`placeholder`、`compute`、`scan`、`extern`。

**变量与轴**：`var`、`const`、`thread_axis`、`reduce_axis`、`AXIS_SEPARATOR`。

**降级入口**：`create_prim_func`、`extern_primfunc`。

**类**：`Tensor`、`TensorSlice`、`PlaceholderOp`、`ComputeOp`、`ScanOp`、`ExternOp`。

**TIR 内建函数**：所有 TIR 内建函数（如 `te.sum`、`te.max` 等归约操作）直接在 te 命名空间可用。

## TE + TOPI 协同

TE 本身只提供计算描述原语，不提供具体的神经网络算子。TOPI（TVM Operator Inventory）基于 TE 构建，提供预定义的算子计算和调度模板：

1. **TOPI 使用 TE 描述计算**：TOPI 算子（如 `topi.nn.conv2d`）内部调用 `te.compute` 和 `te.placeholder` 定义计算。
2. **TOPI 提供调度**：TOPI 为不同硬件提供 `schedule_conv2d` 等调度函数，对 TE 生成的 PrimFunc 应用循环变换。
3. **Relax 通过 emit_te 桥接**：在 Relax BlockBuilder 中，`emit_te` 调用 TOPI/TE 函数生成 TIR PrimFunc，并包装为 `call_tir` 嵌入 Relax 图。

这种分层设计使 TE 保持精简（仅计算描述），TOPI 承担算子库职责，Relax 负责图级编排。

## 设计特点

### 声明式编程

TE 采用声明式风格：用户描述"输出张量的每个元素如何计算"，而非"如何循环遍历"。例如矩阵乘法：

```python
k = te.reduce_axis((0, K), "k")
C = te.compute((M, N), lambda i, j: te.sum(A[i, k] * B[k, j], axis=k))
```

用户不需要编写 for 循环、归约初始化等样板代码，TE 自动生成正确的循环嵌套。

### 调度与计算分离

TE 描述的计算独立于调度。同一个 ComputeOp 可以应用不同的调度（split、reorder、parallel、vectorize 等），生成不同性能的 TIR。这种分离是 TVM 性能可移植性的基础。

### 归约作为一等公民

TE 通过 `reduce_axis` 和归约函数（`te.sum`、`te.max`、`te.min` 等）原生支持归约计算。归约轴与空间轴区分管理，使调度器能够对归约进行 rfactor、并行化等优化。

### 多输出支持

ComputeOp 和 ScanOp 都支持多输出，通过 `body` 数组或 init/update 列表表达。这使得需要同时计算多个结果的操作（如 BatchNorm 的 mean 和 var）可以在一个 Operation 中描述，共享中间计算。

### 可扩展性

ExternOp 提供了逃生舱，允许在 TE 中嵌入任意 TIR 语句或外部函数调用，确保 TE 不会因表达能力不足而限制用户。

## 在 TVM 栈中的位置

TE 在 TVM 四层栈中位于 TIR 之上、Relax 之下：

- **向上**：被 Relax 的 `emit_te` 和 TOPI 算子库使用，作为计算描述的标准方式。
- **向下**：通过 `create_prim_func` 降级为 TIR PrimFunc，进入 TIR 调度和代码生成流程。
- **平行**：TVMScript 的 TIR 方言是另一种直接编写 TIR 的方式，TE 更适合从高层算子自动生成的场景。

理解 TE 是理解 TVM 算子定义和自动调优的基础——MetaSchedule 调优的对象正是由 TE/TOPI 生成的 TIR PrimFunc。

## 相关概念

- [TIRx 中间表示](/concepts/05-tirx-ir.md) — TE 通过 `create_prim_func` 降级为 TIR PrimFunc，进入张量级 IR 层
- [调度原语](/concepts/08-schedule-primitives.md) — TE 描述的计算与调度分离，可通过 split/fuse/reorder 等原语优化循环
- [BlockBuilder 与 Dataflow](/concepts/12-relax-block-builder.md) — Relax BlockBuilder 的 `emit_te` 方法将 TE 计算嵌入图级 IR
- [TOPI 算子库](/concepts/16-topi-operator-library.md) — TOPI 基于 TE 构建，提供神经网络常用算子的计算定义和调度模板
- [MetaSchedule 自动调度](/concepts/09-meta-schedule.md) — TE/TOPI 生成的 PrimFunc 是 MetaSchedule 自动调优的目标对象
