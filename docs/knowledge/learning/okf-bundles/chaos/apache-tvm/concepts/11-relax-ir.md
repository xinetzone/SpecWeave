---
type: Concept
title: Relax 图级 IR
description: TVM Relax 图级中间表示，涵盖动态形状支持、数据流变量、绑定块、函数结构、类型系统及与 TIR 的桥接机制
tags: [tvm, relax, ir, graph, dataflow, tensor, dynamic-shape]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# Relax 图级 IR

Relax 是 TVM 的图级中间表示（Graph-level IR），位于 TIR 张量 IR 之上，负责描述整个神经网络模型的计算图结构。与传统的静态图 IR 不同，Relax 从设计之初就将**动态形状**（dynamic shape）作为一等公民支持，采用数据流语义与一阶函数式编程风格，使编译器能够同时处理符号形状、控制流和数据流计算。Relax 的核心设计目标包括：

1. **动态形状原生支持**：形状可以是符号表达式，支持运行时确定的维度。
2. **数据流与命令式混合**：通过 DataflowBlock 表达纯数据流区域，通过 BindingBlock 支持副作用和控制流。
3. **一阶函数式**：函数是一等值，支持高阶组合、闭包和 Lambda 提升。
4. **跨抽象层桥接**：通过 `call_tir` 直接调用 TIR PrimFunc，实现图级到张量级的无缝衔接。

Relax 的所有表达式节点定义于 `include/tvm/relax/expr.h`，类型系统定义于 `include/tvm/relax/type.h`。

## 表达式节点层次

Relax 的表达式体系以 `ExprNode` 为基类，派生为多种具体节点类型，覆盖变量、常量、控制流、函数和数据结构等语义范畴。

### 变量体系

Relax 区分两类变量，体现可见性和优化范围的差异：

- **`VarNode`**：普通函数局部变量，包含 `name_hint` 字段作为名称提示。变量通过对象地址唯一标识，`name_hint` 在结构相等和哈希计算中被忽略，仅用于调试打印 [F-5]。Var 的相等性采用 `kTVMFFISEqHashKindFreeVar` 模式，即按引用相等 [F-6]。
- **`DataflowVarNode`**：继承自 `VarNode`，专门标记数据流块内部的中间变量 [F-8]。DataflowVar 的作用域仅限于所在 DataflowBlock，不能被块外部引用。编译器可据此安全地对数据流变量进行重排、融合和消除。

两类变量的构造函数签名一致，均接受 `name_hint`、`ty_annotation` 和 `span` 三个参数 [F-7][F-9]。在 Python 层，`tvm.relax.Var` 和 `tvm.relax.DataflowVar` 分别对应这两个类。

### 常量与字面量

- **`ConstantNode`**：包含 `runtime::Tensor data` 字段，持有一个具体的 NDArray 张量数据 [F-10]。提供 `tensor_type()` 方法返回对应的张量类型，`is_scalar()` 判断是否为 0 维标量。Constant 构造时若未指定类型注解，则从 data 自动推断 [F-11]。
- **`StringImmNode`**：包含 `ffi::String value` 字段，表示字符串字面量常量 [F-12]。
- **`DataTypeImmNode`**：包含 `DLDataType value` 字段，表示数据类型常量（如 float32、int8）[F-13]。

### 元组与形状表达式

- **`TupleNode`**：包含 `ffi::Array<Expr> fields` 字段，表示固定长度的异构值集合 [F-1]。Tuple 支持从派生类数组到基类数组的模板转换构造，方便构造元素为特定子类型的元组 [F-2]。
- **`TupleGetItemNode`**：包含 `Expr tuple` 和 `int index` 两个字段，从元组中提取指定索引的字段 [F-3]。
- **`ShapeExprNode`**：包含 `ffi::Array<PrimExpr> values` 字段，将 TIR 层面的 PrimExpr 数组包装为 Relax 层面的形状值 [F-4]。这是连接 Relax 符号形状与 TIR 算术表达式的关键节点。

### 控制流

- **`IfNode`**：包含 `Expr cond`、`SeqExpr true_branch` 和 `SeqExpr false_branch` 三个字段 [F-23]。条件表达式求值为所取分支的结果。If 构造函数自动将非 SeqExpr 的分支包装为 SeqExpr [F-24]，确保控制流边界的统一表示。

### 函数

- **`FunctionNode`**：继承自 `BaseFuncNode`，是 Relax 的核心函数节点，包含四个核心字段 [F-25]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `params` | Array<Var> | 函数参数列表 |
| `body` | SeqExpr | 函数体（绑定块序列 + 最终表达式） |
| `ret_ty` | Type | 返回类型注解 |
| `is_pure` | bool | 是否为纯函数（无副作用），默认 true |

Function 构造函数接受 params、body、ret_ty、is_pure、attrs 和 span，body 若非 SeqExpr 会被自动包装 [F-26]。`Function::CreateEmpty` 静态方法可创建无 body 的函数，此时 ret_ty 为必填项 [F-27]。

函数属性常量包括 [F-28]：
- `kPrimitive`（"Primitive"）：标记为原始算子函数
- `kCodegen`（"Codegen"）：指定外部代码生成后端
- `kComposite`（"Composite"）：标记为复合函数
- `kPartitionedFromPattern`：标记由模式匹配分区产生
- `kWorkspaceSize`：工作空间大小
- `kForcePure`：强制视为纯函数
- `kNumInput`：输入参数数量，最后 `params.size() - num_input` 个参数被视为跨调用固定的权重 [F-29]

- **`ExternFuncNode`**：包含 `ffi::String global_symbol` 字段，表示对外部运行时函数的引用 [F-30]。ExternFunc 可直接调用运行时注册的 `ffi::Function`，无需在编译期内联实现。

### SeqExpr：序列表达式

`SeqExprNode` 包含 `ffi::Array<BindingBlock> blocks` 和 `Expr body` 两个字段 [F-21]。块的顺序强制执行作用域和排序规则：每个绑定块中的变量对后续块可见，body 引用前面块中定义的变量作为最终结果。SeqExpr 提供从 Expr 的隐式转换，若表达式已是 SeqExpr 则复用同一节点不做拷贝 [F-22]。

## 绑定体系

Relax 采用 A-normal form（ANF）风格的绑定表示，每个中间计算结果都绑定到一个变量，这是许多优化 Pass（如公共子表达式消除、死代码消除）的基础。

### Binding 基类

`BindingNode` 继承自 `ffi::Object`，包含 `mutable Span span` 和 `Var var` 两个字段 [F-14]。它是所有变量绑定的基类，采用树节点式的结构相等定义（`kTVMFFISEqHashKindTreeNode`），`var` 字段使用递归式结构相等 [F-15]。

### VarBinding：值绑定

`VarBindingNode` 继承自 BindingNode，包含 `Expr value` 字段，将表达式的值绑定到变量 [F-18]。VarBinding 自定义了 SEqual 和 SHash 方法以提供更好的错误信息。这是最常见的绑定形式，例如 `lv = relax.op.add(x, y)`。

### MatchCast：类型匹配与形状填充

`MatchCastNode` 继承自 BindingNode，包含 `Expr value` 和 `Type ty` 字段 [F-16]。它执行运行时类型匹配，并在首次出现时填充未定义的符号形状变量。MatchCast 是动态形状处理的关键机制：当张量形状在编译期部分未知时，通过 MatchCast 在运行时确认形状并将符号变量绑定到具体值。

### BindingBlock 与 DataflowBlock

- **`BindingBlockNode`**：包含 `ffi::Array<Binding> bindings` 和 `mutable Span span` 字段，是绑定块的基类 [F-19]。普通 BindingBlock 中的绑定按顺序执行，可能包含副作用操作。
- **`DataflowBlockNode`**：继承自 BindingBlockNode，表示数据流块 [F-20]。DataflowBlock 中的所有中间变量必须是 DataflowVar，且块内计算必须是纯的（无副作用）。编译器可对数据流块进行激进优化，包括算子融合、并行调度和内存复用。块的输出通过 `EmitOutput` 显式声明，将 DataflowVar 转换为普通 Var 供块外使用。

这种双层块设计使 Relax 能够在同一函数中混合纯数据流计算和副作用操作：数据流区域享受图级优化，非数据流区域支持命令式控制流和内存操作。

## 类型系统

Relax 的类型系统定义于 `include/tvm/relax/type.h`，采用"假设语义"（assume-semantics）：编译器尽力推导和检查类型，但类型信息可被擦除为静态类型后程序仍可编译运行 [F-42]。这种设计平衡了静态类型安全与动态形状灵活性。

### TensorType：张量类型

`TensorTypeNode` 包含四个字段 [F-40]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `shape` | Optional<Expr> | 形状表达式（可为 ShapeExpr 或 RuntimeDepShape） |
| `vdevice` | Optional<VDevice> | 虚拟设备 |
| `dtype` | Optional<PrimType> | 元素数据类型 |
| `ndim` | int | 维数，默认 kUnknownNDim(-1) |

TensorType 提供 `IsUnknownNdim()`、`IsUnknownDtype()` 和 `GetShape()` 方法 [F-41]。`GetShape()` 从 shape 表达式中提取 PrimExpr 数组。当 ndim 为 `kUnknownNDim` 时，表示维数在编译期完全未知 [F-34]。

### ShapeType：形状类型

`ShapeTypeNode` 包含 `ffi::Optional<ffi::Array<PrimExpr>> values` 和 `int ndim`（默认 kUnknownNDim）字段 [F-38]。ShapeType 表示形状值本身的类型，既可以是已知的符号形状数组，也可以是仅知维数的未知形状。ShapeType 提供两个构造函数：接受已知符号形状值数组，或仅接受 ndim [F-39]。

### 其他类型

- **`AnyTypeNode`**：表示任意 Relax 值，类型键为 `"relax.AnyType"` [F-36]。`ObjectTypeNode`/`ObjectType` 是其兼容性别名，新代码应使用 AnyType [F-37]。
- **`PackedFuncTypeNode`**：表示 PackedFunc 类型，类型键为 `"relax.PackedFuncType"` [F-35]。
- **TupleType / FuncType**：分别表示元组类型和函数类型，构成复合类型系统的基础。

### RuntimeDepShape：运行时依赖形状

当张量形状完全依赖运行时值（如 `unique` 操作的输出长度），无法用符号 PrimExpr 表达时，Relax 使用 `RuntimeDepShape` 表示。这种形状在编译期不透明，仅在运行时可知。

## 与 TIR 的桥接

Relax 作为图级 IR，不直接描述张量级循环计算，而是通过 `call_tir` 机制调用 TIR PrimFunc：

```python
lv = relax.call_tir(prim_func, args, out_sinfo)
```

`call_tir` 是 Relax 的基础算子之一 [F-85]，它接受一个 TIR PrimFunc（或其全局符号名）、输入张量列表和输出结构信息，在运行时分发到底层实现。这一桥接设计实现了关注点分离：

- **Relax 层**：负责算子间的数据流、形状推导、内存规划、算子融合决策。
- **TIR 层**：负责单个算子内部的循环嵌套、线程绑定、向量化和张量化。

在编译流水线中，`LegalizeOps` Pass 将高层 Relax 算子（如 `relax.op.nn.conv2d`）替换为 `call_tir` 调用及对应的 TIR PrimFunc [F-118]；`FuseTIR` Pass 再将多个融合的子函数合并为更大的 TIR PrimFunc [F-134]。`CallTIRRewrite` Pass 为 `call_tir` 插入显式的张量分配 [F-107]，完成从图级到张量级的降级。

## GetShapeOf：形状查询

`GetShapeOf` 函数返回表达式的形状 [F-32]。它要求表达式已归一化：若张量有编译时符号形状，直接返回该形状；若张量无编译时符号形状，则返回 `Call(relax.op.shape_of, [expr])`，在运行时通过 `shape_of` 算子查询。这一机制统一了静态形状和动态形状的处理路径。

## 设计要点总结

Relax IR 的设计体现了以下架构原则：

1. **显式绑定**：所有中间计算通过 Binding 绑定到变量，为优化提供清晰的中间表示。
2. **数据流与控制流分离**：DataflowBlock 标记纯计算区域，BindingBlock 支持顺序副作用，二者可在同一函数内共存。
3. **渐进式类型信息**：从完全动态（AnyType）到完全静态（已知形状和 dtype）的光谱式类型表示，适应不同编译阶段的信息丰度。
4. **符号形状一等公民**：ShapeExpr 将 TIR PrimExpr 嵌入图级 IR，使形状计算本身可被分析和优化。
5. **桥接而非替代**：Relax 不重新发明张量级 IR，而是通过 call_tir 复用成熟的 TIR 基础设施。

这些设计使 Relax 能够表达从传统静态 CNN 到动态序列模型（如 LLM 推理中的可变序列长度）的广泛深度学习程序，同时为编译器提供足够的语义信息进行跨算子优化。

## 相关概念

- [FFI 基础设施](/concepts/01-ffi-foundation.md) — Relax 表达式节点与对象系统基于 TVM-FFI 的引用计数和反射机制构建
- [TIRx 中间表示](/concepts/05-tirx-ir.md) — Relax 通过 `call_tir` 桥接 TIR PrimFunc，实现图级到张量级的衔接
- [BlockBuilder 与 Dataflow](/concepts/12-relax-block-builder.md) — 构建 Relax IR 的核心接口，负责 Emit、归一化和作用域管理
- [Relax 算子体系](/concepts/13-relax-ops.md) — Relax Call 节点调用的算子集合，携带类型推导与合法化属性
- [Relax 变换 Pass](/concepts/14-relax-passes.md) — 对 Relax IR 进行融合、合法化、内存规划等优化的编译 Pass 体系
