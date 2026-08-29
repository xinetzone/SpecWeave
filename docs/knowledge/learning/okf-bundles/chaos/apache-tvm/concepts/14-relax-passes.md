---
type: Concept
title: Relax 变换 Pass
description: Relax 40+ 编译 Pass 体系，涵盖算子融合、合法化、自动微分、布局转换、混合精度、死代码消除及 VM lower 流水线
tags: [tvm, relax, pass, transform, fusion, legalize, gradient, mixed-precision, vm]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# Relax 变换 Pass

Pass 是 TVM 编译器中对 IR 进行分析和变换的基本单元。Relax 提供了 40 余个变换 Pass，定义于 `include/tvm/relax/transform.h`，实现于 `src/relax/transform/` 目录（60+ 个实现文件 [F-146]）。这些 Pass 覆盖了从图级优化到后端降级的完整编译流程，包括算子融合、合法化、常量折叠、自动微分、布局转换、混合精度、内存规划和代码生成等。

## Pass 基础设施

Relax 提供两种 Pass 创建函数 [F-102][F-103]：

- **`CreateFunctionPass(pass_func, opt_level, name, required, traceable)`**：创建函数级 Pass，对 IRModule 中的每个 Relax 函数独立执行变换。
- **`CreateDataflowBlockPass(pass_func, opt_level, name, required, traceable)`**：创建数据流块级 Pass，对函数内的每个 DataflowBlock 独立执行，作用域更小，便于编写局部优化。

Pass 通过 `required` 列表声明依赖的其他 Pass，PassContext 管理优化级别和调试信息。所有 Pass 遵循不可变语义：输入 IRModule 不被修改，变换返回新的 IRModule。

## 核心图级 Pass

### Normalize：归一化

`Normalize()` 将 Relax IR 转换为范式（A-normal form），填充表达式类型 [F-111]。它对所有绑定执行 BlockBuilder 的归一化逻辑，确保后续 Pass 看到的是统一格式的 IR。`CanonicalizeBindings()` 进一步折叠变量绑定和 match shape 节点及元组索引，简化模块 [F-113]；若数据流变量仅在输出绑定中使用，会移除该中间变量。

### ConvertToDataflow / ToNonDataflow

- **`ConvertToDataflow(min_size)`**：将 BindingBlock 中连续的数据流操作转换为 DataflowBlock [F-140]。`min_size` 参数指定创建新数据流块所需的最小连续绑定数。这使原本非数据流的 IR 能够享受数据流块的优化机会。
- **`ToNonDataflow()`**：将所有数据流结构转换为非数据流版本 [F-105]。它将 DataflowVar 提升为普通 Var，打破 DataflowBlock 的局部性约束。这通常在编译后期执行，因为某些降级 Pass（如 CallTIRRewrite）需要所有变量在函数作用域可见。

### DeadCodeElimination：死代码消除

`DeadCodeElimination()` 移除两类死代码 [F-141]：

1. **未使用的局部 VarBinding**：绑定变量未被使用且不使用非纯操作。
2. **未使用的 Relax 函数**：从入口函数检测调用链，不可达的函数被移除。

DCE 是编译流水线的常规清理 Pass，在多个阶段重复执行以保持 IR 精简。

### EliminateCommonSubexpr：公共子表达式消除

`EliminateCommonSubexpr(call_only)` 消除函数内的公共子表达式 [F-114]。当 `call_only` 为 true 时仅消除 Call 节点。CSE 通过结构相等识别等价表达式，将重复计算替换为对已有变量的引用。

### FoldConstant：常量折叠

`FoldConstant()` 在数据流块内折叠常量表达式 [F-117]。它对所有输入为 Constant 的算子调用进行求值，用结果常量替换。常量折叠可能需要先调用 ConvertToDataflow，因为折叠要求纯计算环境。

### LambdaLift：Lambda 提升

`LambdaLift()` 将嵌套函数提升为全局函数 [F-104]。Relax 支持嵌套函数定义（高阶函数），但后端执行引擎通常只支持全局函数。LambdaLift 将闭包捕获的变量转换为额外参数，把内部函数提升到 IRModule 的全局作用域。

## 算子融合

算子融合是深度学习编译器最关键的优化之一，通过合并多个算子减少内核启动开销和中间结果内存访问。

### FuseOps：按模式融合

`FuseOps(fuse_opt_level)` 将数据流块中的绑定按融合算法分组为新的 Relax 函数 [F-128]。其工作原理为：

1. 读取每个算子注册的 `OpPatternKind`（kElemWise/kBroadcast/kInjective/kCommReduce/kOutEWiseFusable/kOpaque）。
2. 从数据流块的输出开始反向遍历。
3. 按融合规则将兼容的算子分组：逐元素算子可以融合到其消费者，归约算子作为融合边界，不透明算子阻止融合。
4. 为每个分组创建一个子函数，包含分组内的所有绑定。
5. 后续 `FuseTIR` Pass 为每个分组函数生成融合的 TIR PrimFunc。

`fuse_opt_level` 为 -1 时从 PassContext 推断优化级别。

### FuseOpsByPattern：按自定义模式融合

`FuseOpsByPattern(patterns, annotate_codegen)` 按提供的 `FusionPattern` 列表进行模式匹配并融合 [F-132]。模式顺序决定优先级，先匹配的模式优先。每个 FusionPattern 包含 DFPattern、可选的 check 验证函数和 attrs_getter 属性获取函数 [F-129]。当 `annotate_codegen` 为 true 时，为匹配的子图标注外部代码生成属性，用于 BYOC。

### MergeCompositeFunctions

`MergeCompositeFunctions()` 将一个或多个 FuseOpsByPattern 创建的复合函数分组成新函数 [F-133]，标注 kCodegen 和 GlobalSymbol 属性，用于外部后端卸载。

### FuseTIR：TIR 层融合

`FuseTIR()` 将 Relax 子函数融合为更大的 TIR 函数 [F-134]。当 FuseOps 创建的子函数调用多个 TIR PrimFunc 时，FuseTIR 将这些 PrimFunc 合并为单个 PrimFunc，实现真正的内核融合。它与 FuseOps 协同：FuseOps 在图级决定哪些算子可以融合，FuseTIR 在 TIR 级执行实际的函数合并。

### AnnotateTIROpPattern

`AnnotateTIROpPattern()` 为 TIR 函数自动标注 Op Pattern Kind，供 FuseOps 使用 [F-127]。它分析 TIR PrimFunc 的循环结构和内存访问模式推断算子类型：无法检测时标注为 "opaque"。用户也可手动标注 `op_pattern` 属性覆盖自动检测。

### CombineParallelMatmul

`combine_parallel_matmul` Pass 检测多个共享相同输入的矩阵乘法，将它们合并为一个批量矩阵乘法，利用 GEMM 内核的批处理能力提高效率。实现文件为 `combine_parallel_matmul.cc` [F-146]。

## 合法化与降级

合法化（Legalization）将高层 Relax 算子转换为 `call_tir` 调用及对应的 TIR PrimFunc，是从图级 IR 到张量级 IR 的关键步骤。

### LegalizeOps

`LegalizeOps(cmap, skip_ops)` 遍历所有算子调用，调用每个算子注册的 `FLegalize` 函数 [F-118]：

- `cmap`：自定义映射，覆盖算子的默认合法化实现。
- `skip_ops`：指定跳过合法化的算子集合。

合法化后的 IR 中，高层算子（如 `relax.op.nn.conv2d`）被替换为 `call_tir(prim_func, args, out_sinfo)`，对应的 TIR PrimFunc 被添加到 IRModule。

### DecomposeOps

- **`DecomposeOpsForInference()`**：推理时分解复合算子 [F-136]，如 BatchNorm 三元组（mean/var/scale 融合）、Attention、Erf 等。
- **`DecomposeOpsForTraining()`**：训练时分解复合算子 [F-137]，保留训练所需的中间输出。

### AlterOpImpl

`AlterOpImpl(op_impl_map)` 根据提供的映射替换 PrimFunc 实现 [F-138]，可在调用点插入布局变换。这用于为特定后端选择优化的算子实现（如将默认卷积替换为 cuDNN 版本）。

### CallTIRRewrite

`CallTIRRewrite()` 为 `call_tir` 和 `call_dps_packed` 执行显式张量分配 [F-107]。合法化后的 call_tir 假设输出张量由被调用函数内部分配，此 Pass 在调用前插入显式的 `alloc_tensor`，使内存分配对后续 Pass 可见。

### RewriteDataflowReshape

`RewriteDataflowReshape()` 将 reshape 类 call_tir 转换为 `relax.reshape` 算子调用 [F-108]。reshape 在 VM 构建第一阶段处理，后续降级为运行时 CreateView（零拷贝视图），避免不必要的数据复制。

### LowerRuntimeBuiltin / VMShapeLower

- **`LowerRuntimeBuiltin()`**：执行内置函数降级，将大多数算子映射到 VM 内置函数 [F-150]。
- **`VMShapeLower()`**：将 Relax 中的形状表达式降级为 VM 形状堆和 TIR 函数 [F-151]。符号形状计算被编译为专用的 TIR 函数，在运行时执行以确定实际形状。

### RunCodegen

`RunCodegen(target_options, entry_functions)` 运行外部代码生成 [F-135]。它遍历标注了 kCodegen 属性的函数，调用对应后端的代码生成器（如 TensorRT、cuDNN、CUTLASS），生成外部模块并注册到 IRModule。

## 内存优化

### StaticPlanBlockMemory

`StaticPlanBlockMemory()` 是 BindingBlock 级静态内存规划 Pass [F-109]。它尽力复用已分配的内存：当两个张量的生命周期不重叠时，共享同一块内存。对于动态形状，支持通过 `tir_var_upper_bound`/`tir_var_lower_bound` 属性标注动态形状边界，使编译器能够估算内存大小并进行规划。

### KillAfterLastUse

`kill_after_last_use.cc` 实现在张量最后一次使用后立即释放其内存 [F-146]，缩短张量生命周期，提高内存复用率。这对 LLM 推理等内存密集型场景尤为重要。

### LowerAllocTensor

`lower_alloc_tensor.cc` 将高层 `alloc_tensor` 操作降级为运行时内存分配调用 [F-146]。

### AttachAttrLayoutFreeBuffers

`AttachAttrLayoutFreeBuffers()` 根据 Relax 函数中的使用情况为 tirx::PrimFunc 附加 layout free buffers 属性 [F-120]，主要标记模型权重和常量。Layout free buffer 表示其布局不被 PrimFunc 假设，可由外部自由重排（如为目标硬件预打包权重）。

### SplitLayoutRewritePreproc

`SplitLayoutRewritePreproc()` 将布局重写预处理块拆分为独立的 tirx::PrimFunc [F-121]，用于 MetaSchedule 调优后的预打包权重。

## 自动微分

### Gradient

`Gradient(func, require_grads)` 是反向自动微分 Pass [F-131]，为指定函数生成 `func_name + "_adjoint"` 函数。其约束包括：

- 输入函数必须只有一个数据流块。
- 梯度目标必须是标量（0 维张量）。
- 每个算子必须注册 `FPrimalGradient` 函数。

Gradient Pass 遍历数据流块的绑定（前向传播），为每个绑定生成对应的反向绑定（梯度计算），最终返回原始输出和参数梯度。`gradient_simplifier.cc` 对生成的梯度计算进行代数化简 [F-146]。

## 布局转换

### ConvertLayout

`ConvertLayout(desired_layouts, layout_cb)` 执行布局转换 Pass [F-139]：

- `desired_layouts`：算子名到期望布局的映射（如 `{"nn.conv2d": ["NHWC", "OHWI"]}`）。
- `layout_cb`：动态回调函数，可根据算子属性返回期望布局。

Pass 在算子调用点插入布局变换，确保数据按目标布局流动，同时消除冗余的布局转换。

### LiftTransformParams

`LiftTransformParams(shared_transform)` 提升函数参数的变换到独立的 `transform_params` 函数 [F-122]。当模型权重需要预处理（如布局转换、量化）时，这些变换被提取到独立函数，可在部署前离线执行一次，避免每次推理重复计算。`shared_transform` 控制是否为多个函数生成共享的变换函数。

### BindParams / BindSymbolicVars

- **`BindParams(params)`**：将函数参数绑定到常量张量 [F-115]，用于模型加载时将权重固化到 IR 中。
- **`BindSymbolicVars(symbol_map)`**：将符号变量绑定到常量形状值 [F-116]，支持 `tirx.Var` 或字符串名称作为键。用于固定输入形状（如将 batch size 绑定为 1）。

## 混合精度

### ToMixedPrecision

`ToMixedPrecision(out_dtype)` 执行自动混合精度转换 [F-143]。它假设输入模块为 fp32，自动将特定算子（如 conv2d、matmul）转换为 fp16 计算，同时保留某些敏感算子（如 softmax、loss）在 fp32。`out_dtype` 指定 gemm/conv 的累加器类型。混合精度可显著减少内存占用和计算延迟，尤其在支持 Tensor Core 的 GPU 上。

## 数据相关优化

### DataflowUseInplaceCalls

`DataflowUseInplaceCalls()` 将数据流块中可原地执行的算子（主要是逐元素操作）替换为 `call_tir_inplace` 调用 [F-142]。原地操作直接修改输入张量而非分配输出，减少内存分配。Pass 通过分析缓冲区活性确保原地操作安全（输入在操作后不再被使用）。

### RewriteCUDAGraph

`RewriteCUDAGraph()` 重写 Relax 模块以使用 CUDA graph 执行 [F-144]。它识别可使用 CUDA graph 的区域（无动态形状、无 CPU-GPU 同步的连续内核序列）并提升为新函数，供运行时进行图捕获和重放，减少内核启动开销。

## 预定义 Pipeline

Relax 提供了三个预定义编译流水线 [F-147][F-148][F-149]：

### zero_pipeline

轻量流水线，按顺序应用 [F-147]：
1. LegalizeOps
2. AnnotateTIROpPattern
3. FoldConstant
4. FuseOps
5. FuseTIR
6. 若存在 MetaSchedule Database，追加 MetaScheduleApplyDatabase

适用于已调优模型的快速编译。

### default_build_pipeline

`tvm.compile` 使用的默认编译流水线，按顺序应用 13 个 Pass [F-148]：

1. DispatchSampling
2. DispatchSortScan
3. LegalizeOps
4. RewriteDataflowReshape
5. ToNonDataflow
6. RemovePurityChecking
7. CallTIRRewrite
8. StaticPlanBlockMemory
9. RewriteCUDAGraph
10. LowerAllocTensor
11. KillAfterLastUse
12. LowerRuntimeBuiltin
13. ComputePrimValue
14. VMShapeLower
15. AttachGlobalSymbol

### static_shape_tuning_pipeline

用于静态形状模型调优 [F-149]，接受 `total_trials`、`target`、`work_dir`、`cpu_weight_prepack`、`max_trials_per_task` 参数，集成 MetaSchedule 自动调度。

## MetaSchedule 集成

`meta_schedule.cc` 实现了 Relax 与 MetaSchedule 的集成 [F-146]。它提取 Relax 函数中的 TIR PrimFunc 作为调优任务，调用 MetaSchedule 进行自动调度，将最优调度结果存回 Database，并在编译时应用 Database 中的调度。

## 设计总结

Relax Pass 体系体现了以下设计哲学：

1. **分层降级**：从高层算子到 TIR PrimFunc 再到 VM 字节码，每一层 Pass 只关注当前抽象级别的优化，降级 Pass 清晰地标记层级边界。
2. **可组合流水线**：Pass 是独立的变换单元，通过 Pipeline 组合使用，用户可自定义编译流程。
3. **属性驱动**：算子的优化行为（融合模式、合法化、梯度）通过属性注册，Pass 通用逻辑与算子特定知识分离。
4. **多目标支持**：布局转换、混合精度、外部代码生成等 Pass 使同一 IR 能适配不同硬件和精度需求。
5. **渐进式降低**：编译过程中形状信息从符号逐渐具体化，内存规划从静态到动态，优化机会在每个阶段被充分挖掘。

## 相关概念

- [Pass 基础设施](/concepts/03-pass-infrastructure.md) — Relax Pass 基于 TVM 通用 Pass 框架，使用 PassContext 管理优化级别和依赖
- [Relax 图级 IR](/concepts/11-relax-ir.md) — Pass 变换的目标 IR，涵盖 BindingBlock、DataflowBlock、Function 等节点
- [BlockBuilder 与 Dataflow](/concepts/12-relax-block-builder.md) — Pass 实现中使用 BlockBuilder 进行归一化和增量重写
- [Relax 算子体系](/concepts/13-relax-ops.md) — 算子融合和合法化依赖 OpPatternKind 和 FLegalize 等算子属性
- [VM 字节码虚拟机](/concepts/18-vm-bytecode.md) — LowerRuntimeBuiltin/VMShapeLower 等 Pass 将 Relax 降级为 VM 字节码
