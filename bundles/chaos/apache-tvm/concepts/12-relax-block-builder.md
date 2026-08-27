---
type: Concept
title: BlockBuilder 与 Dataflow 构建
description: Relax BlockBuilder 核心机制，涵盖 Emit/Normalize、作用域管理、DataflowBlock 构建、FunctionScope 上下文管理及 DataflowPattern 模式匹配
tags: [tvm, relax, block-builder, dataflow, ir-builder, normalize, pattern]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# BlockBuilder 与 Dataflow 构建

BlockBuilder 是 Relax 构建 IR 的核心接口，定义于 `include/tvm/relax/block_builder.h`。它提供了一套命令式 API，让前端（Python 脚本、TVMScript、模型导入器）能够逐步构建 Relax 函数，同时自动执行归一化、类型推导和形状推导。BlockBuilder 的设计融合了命令式构建的便利性与声明式数据流的语义安全，是 Relax 区别于传统图 IR 构建器的关键组件。

BlockBuilderNode 是虚接口类，提供三大类功能：**全局上下文管理**、**作用域管理**和**归一化**[F-43]。

## 全局上下文管理

BlockBuilder 在构建过程中维护一个上下文 IRModule，用于收集函数、管理名称唯一性和解析全局符号。

### 名称供应与模块访问

- **`name_supply()`**：返回名称供应器，确保生成的变量名在模块内唯一。名称供应器基于已有名称进行去重，自动添加数字后缀。
- **`GetContextIRModule()`**：获取当前构建所基于的上下文模块。BlockBuilder 可以在已有模块的基础上增量添加新函数，此时已有的 GlobalVar 和函数名会被纳入名称管理 [F-44]。

### 函数管理与终结

- **`AddFunction()`**：向上下模块添加一个 Relax 函数。
- **`UpdateFunction()`**：更新模块中已有的函数。
- **`Finalize()`**：终结构建过程，可能重命名 IRModule 中的 GlobalVar 以确保名称唯一性，并保证每个公开函数名与其 `global_symbol` 属性一致 [F-45]。Finalize 返回最终的 IRModule。

`BlockBuilder::Create()` 静态工厂方法创建 BlockBuilder 实例，可传入可选的 `ctx_mod` 作为重写前的上下文模块 [F-52]。若不提供，则创建空模块。

## 作用域管理

Relax 的作用域系统支持嵌套，允许在函数内部构建多层绑定块。BlockBuilder 维护作用域栈，每个作用域持有自己的绑定集合。

### 函数作用域

- **`BeginScope()`**：开启一个新作用域，父作用域的符号变量不可用 [F-47]。这通常用于开始一个新的函数体。
- **`BeginInnerScope()`**：开启内部作用域，继承父作用域的可见参数 [F-47]。用于在函数内部创建嵌套块（如 If 分支内部）。
- **`EndScope()`**：结束当前作用域，返回该作用域收集的 BindingBlock。
- **`AddDefinitionToScope()`**：向当前作用域添加符号变量定义（如 MatchCast 引入的形状变量）。

### 绑定块作用域

- **`BeginDataflowBlock()`**：开始一个新的数据流块。此后发射的绑定变量将被创建为 DataflowVar，直到调用 EndBlock。
- **`BeginBindingBlock()`**：开始一个普通绑定块。
- **`EndBlock()`**：结束当前块，返回构建好的 BindingBlock 或 DataflowBlock [F-46]。

### 绑定查找

- **`LookupBinding()`**：在当前已发射的序列中查找变量绑定值 [F-48]。对函数参数返回 `std::nullopt`，因为参数不是由绑定产生的。该方法用于归一化过程中追踪变量定义，支持常量折叠和复制传播。

## Emit：发射绑定

Emit 系列方法是 BlockBuilder 最常用的接口，负责将表达式加入当前块并返回绑定变量。

### Emit

`Emit()` 接受一个 Expr 并返回绑定变量 [F-49]。其内部流程为：

1. 调用 `Normalize()` 将表达式转换为范式，推导类型和形状。
2. 创建一个新的 Var（或在数据流块中创建 DataflowVar）。
3. 构造 VarBinding 并加入当前块。
4. 返回绑定变量。

在 Python 层，`bb.emit(expr)` 对应此方法。Emit 是构建计算图最基本的操作，每个中间计算结果都通过 Emit 绑定到变量。

### EmitMatchCast

`EmitMatchCast()` 发射一个 MatchCast 绑定 [F-50]，用于在已知值具有特定类型和形状时建立类型断言。它接受 value 和 ty 参数，创建 MatchCast 节点。MatchCast 在动态形状处理中尤为重要：当从外部传入一个形状未知的张量时，通过 MatchCast 可以在运行时验证形状并将符号变量绑定到实际维度。

### EmitOutput

`EmitOutput()` 为当前数据流块生成输出 [F-50]。在 DataflowBlock 中，中间变量都是 DataflowVar，作用域仅限于块内。当需要将某些值暴露给块外时，通过 EmitOutput 声明输出，BlockBuilder 自动将 DataflowVar 转换为普通 Var。

### EmitNormalized

`EmitNormalized()` 发射已归一化的绑定 [F-50]。当调用方已经手动完成归一化（或从已归一化的 IR 复制）时使用，跳过 Normalize 步骤以提高效率。

## Normalize：归一化与类型推导

`Normalize()` 是 BlockBuilder 的核心智能所在，它将任意表达式转换为范式并尽力推导类型和形状 [F-51]。归一化过程包括：

1. **常量折叠**：对常量表达式进行求值。
2. **算子归一化**：调用算子注册的 `FNormalize` 函数，将多种等价语法形式归一化为单一表示。
3. **形状推导**：根据输入形状和算子语义推导输出形状。
4. **类型推导**：调用算子的 `FInferType` 函数推导输出类型。
5. **子表达式绑定**：对 Call 等复合表达式，通过 `NormalizeArgument()` 为非叶子参数创建绑定变量 [F-51]，确保 ANF 形式。

### FNormalize 算子归一化

`FNormalize` 是注册在算子上的归一化函数类型 [F-57]，作为 BlockBuilder 的一部分对每个表达式应用。它允许算子将多种等价写法归一化为统一表示。例如，某些算子可能接受位置参数或关键字参数，FNormalize 将它们统一为标准参数顺序。

`DisableOperatorSpecificNormalizationForTVMScript` 标记结构体用于禁用 FNormalize，仅供 TVMScript 解析使用 [F-53]。这是因为 TVMScript 作为源码表示，需要精确保留用户编写的形式，不应在解析时被归一化改写。

## Python 层作用域上下文

Python 绑定提供了三个上下文管理器，简化作用域管理 [F-241][F-242][F-243]：

### FunctionScope

`FunctionScope` 是函数构建的辅助上下文管理器。在 `__enter__` 中进入函数作用域，在 `__exit__` 中退出，内部维护 `_blocks` 列表和 `_is_emit_func_output_called` 标志 [F-241]。典型用法：

```python
bb = relax.BlockBuilder()
with bb.function("main", [x, y]):
    with bb.dataflow():
        lv = bb.emit(relax.op.add(x, y))
        gv = bb.emit_output(lv)
    bb.emit_func_output(gv)
mod = bb.finalize()
```

FunctionScope 确保函数体的所有绑定被正确收集，并在退出时自动处理作用域关闭。

### DataflowScope

`DataflowScope` 是数据流块构建的辅助上下文管理器。进入时结束当前块并开始 DataflowBlock，退出时结束 DataflowBlock 并开始新的 BindingBlock [F-242]。在 DataflowScope 内，`bb.emit()` 自动创建 DataflowVar，`bb.emit_output()` 声明块输出。

### TestingScope

`TestingScope` 用于单元测试，接受 `tirx.Var` 列表作为 def_vars [F-243]。内部创建 dummy ShapeType 参数使形状变量进入作用域，方便在隔离环境中测试需要符号形状的表达式。

## emit_te：桥接 TE

BlockBuilder 提供 `emit_te` 方法，允许在 Relax 数据流块中直接使用 TE（Tensor Expression）定义计算。`emit_te` 接受一个 TE 计算函数和输入张量，内部执行以下步骤：

1. 调用 TE 函数生成 Tensor 和 Operation。
2. 通过 `create_prim_func` 将 TE 计算降级为 TIR PrimFunc。
3. 将 PrimFunc 添加到 IRModule。
4. 生成 `call_tir` 表达式并发射到当前数据流块。

这一桥接使用户可以在 Relax 图中无缝嵌入 TE 张量表达式，既享受图级优化，又能利用 TE 的灵活计算描述能力。`emit_te` 是 Relax 与 TE/TOPI 生态集成的主要入口。

## DataflowPattern：数据流模式匹配

除了构建 IR，Relax 还提供了 `DFPattern` 数据流模式系统，定义于 `include/tvm/relax/dataflow_pattern.h`，用于描述算子子图模式，支持算子融合和 BYOC（Bring Your Own Codegen）。

### 模式节点与组合

`DFPatternNode` 是所有数据流模式的基类，预留 21 个子类槽位 [F-62]。`DFPattern` 提供运算符重载来组合模式 [F-63]：

- `operator()`：创建 CallPattern，匹配算子调用。
- `operator|`：创建 OrPattern，表示"或"关系。
- `operator&`：创建 AndPattern，表示"与"关系。
- `operator~`：创建 NotPattern，表示"非"关系。

### 约束方法

DFPattern 提供多种约束方法来精化匹配 [F-64]：

- `HasAttr()`：要求匹配节点具有特定属性。
- `HasType()`：要求匹配值具有特定类型。
- `HasDtype()`：要求匹配张量具有特定数据类型。
- `HasShape()`：要求匹配张量具有特定形状。
- `HasSameShapeAs()`：要求与另一个模式匹配的张量形状相同。
- `dup()`：创建模式的副本，用于多次引用同一模式。

### 图级边约束

模式不仅描述单个节点，还描述节点间的数据流关系：

- **`UsedBy()`**：在 `lhs[-1]` 和 `rhs[0]` 之间创建 used-by 关系，`operator^` 是其语法糖 [F-65]。表示 lhs 的输出被 rhs 使用。
- **`OnlyUsedBy()`**：创建 only-used-by 关系，`operator>>` 是其语法糖 [F-65]。表示 lhs 的输出**仅**被 rhs 使用，不能被其他节点消费——这是算子融合的关键约束，因为融合要求中间结果不被其他消费者共享。

`PairCons` 结构体定义图级匹配中的边约束，包含 `kUsedBy` 和 `kOnlyUsedBy` 两种类型及 `index` 参数 [F-66]。

### DFConstraint：自定义约束

`DFConstraintNode` 是图上额外约束的基类 [F-67]，提供：
- `GetDependentPatterns()`：返回约束依赖的模式集合。
- `AsCondition()`：返回 PrimExpr 条件及是否为充要条件的布尔值。

这允许用户编写复杂的自定义匹配逻辑（如"两个卷积的权重形状相同"），超越纯结构模式匹配的能力。

## DataflowBlockRewrite：块重写

`DataflowBlockRewriteNode` 提供对已构建数据流块的增量修改能力，定义于 `include/tvm/relax/binding_rewrite.h`。它维护三个内部状态 [F-69]：
- `to_users_`：变量到使用者的映射。
- `fn_outputs_`：函数输出所需变量集合。
- `name_supply_`：名称供应器。

主要方法包括 [F-68]：
- `ReplaceAllUses()`：替换变量的所有使用点。
- `Add(Binding)` / `Add(var_name, expr)` / `Add(expr)`：向块添加新绑定。
- `RemoveUnused()`：移除未使用的绑定。
- `RemoveAllUnused()`：移除所有未使用绑定。

DataflowBlockRewrite 构造函数接受 DataflowBlock 和 root_fn [F-70]，在 Pass 实现中广泛用于增量变换。

## 设计意义

BlockBuilder 的设计体现了 Relax 的核心理念：

1. **构建即归一化**：每次 Emit 都触发归一化和类型推导，确保构建出的 IR 始终处于范式状态，减少后续 Pass 的负担。
2. **作用域安全**：通过显式的作用域栈管理变量可见性，DataflowVar 的局部性由类型系统强制保证。
3. **多层级抽象桥接**：emit_te 将 TE 计算无缝嵌入 Relax 图，DFPattern 将图模式匹配标准化为可组合的代数对象。
4. **增量友好**：DataflowBlockRewrite 支持对已有 IR 进行局部修改，避免全量重写的开销。

BlockBuilder 不仅是 IR 构建工具，更是 Relax 语义模型的具体实现——它强制执行的 ANF 形式、数据流边界和类型推导规则，定义了什么是"良构"的 Relax 程序。

## 相关概念

- [Relax 图级 IR](/concepts/11-relax-ir.md) — BlockBuilder 所构建的目标 IR，包含 Var/Binding/Function 等节点体系
- [Relax 算子体系](/concepts/13-relax-ops.md) — Emit 时调用算子的 FNormalize 进行归一化，算子属性驱动构建过程
- [Relax 变换 Pass](/concepts/14-relax-passes.md) — Pass 实现中广泛使用 BlockBuilder 和 DataflowBlockRewrite 增量重写 IR
- [TE 张量表达式](/concepts/15-te-tensor-expression.md) — `emit_te` 方法将 TE 计算桥接为 Relax 中的 `call_tir` 表达式
- [TVMScript DSL](/concepts/20-tvmscript.md) — TVMScript 的 Relax 方言底层通过 BlockBuilder 构建 IR 节点
