---
type: Concept
title: 调度原语
description: S-TIR 40+ 调度原语分类详解，涵盖循环变换、ComputeAt 计算位置、缓存、绑定、归约、注解、张量化和布局变换，每个原语的前置条件与语义
tags: [tvm, s-tir, schedule, primitive, split, fuse, compute-at, tensorize, 调度原语]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: ir-tir-source
    resource: "/references/ir-tir-source.md"
    title: IR 核心与 TIRx 源码
---

# 调度原语

调度原语（Schedule Primitives）是 S-TIR 调度系统提供的原子变换操作。用户通过组合调用这些原语来描述内核的调度策略，MetaSchedule 则在搜索空间中自动选择和组合原语。S-TIR 提供 40+ 个调度原语，每个原语都有严格的前置条件检查，确保变换的正确性。原语操作 RV（LoopRV/SBlockRV/ExprRV）而非直接修改 IR 节点，使得调度序列可被 Trace 记录和重放。

## 原语分类概览

调度原语可分为以下七大类：

| 类别 | 代表原语 | 用途 |
|------|---------|------|
| 循环变换 | Split/Fuse/Reorder/Merge | 改变循环嵌套结构 |
| 计算位置 | ComputeAt/ComputeInline/ComputeRoot | 控制块的计算位置 |
| 缓存 | CacheRead/CacheWrite/CacheInplace | 插入缓存阶段 |
| ForKind 操作 | Parallel/Vectorize/Bind/Unroll | 设置循环执行方式 |
| 归约 | RFactor/DecomposeReduction | 归约优化 |
| 块注解 | Annotate/StorageAlign/SetScope | 附加元信息 |
| 张量化与布局 | Tensorize/TransformLayout | 硬件特定优化 |

## 循环变换原语

循环变换原语改变循环嵌套的结构，是调度优化的基础。

### Split 循环拆分

`Split()` 将循环拆分为连续循环列表 [F-212]。

**前置条件**：
- 循环无注解
- 循环无线程绑定
- 循环从 0 开始

**参数**：
- `loop`：待拆分的 LoopRV
- `factors`：拆分因子列表（可为 ExprRV 以支持采样）
- `preserve_unit_iters`：是否保留单位迭代
- `disable_predication`：是否禁用谓词保护

**语义**：将 extent 为 N 的循环拆分为多个嵌套循环，外层循环 extent 为 factors[i]，最内层为剩余部分。当 factors 包含 0（占位符）时，自动推导该位置的 extent。

**示例**：`split(loop, factors=[None, 32])` 将 N 拆分为 `outer=N/32` 和 `inner=32`。

### Fuse 循环融合

`Fuse()` 将连续循环列表融合为一个 [F-215]。

**前置条件**：
- 循环无注解/线程绑定
- 内层为外层唯一子节点
- 循环从 0 开始
- 域间无依赖

**语义**：将多个连续嵌套循环融合为一个循环，extent 为各循环 extent 的乘积。融合后的循环变量在 body 中通过整数除法和取模恢复各原始循环变量。

### Reorder 循环重排

`Reorder()` 重排循环列表（不要求连续）[F-216]。

**前置条件**：
- 循环在同一链上
- 外层循环域不依赖内层
- 块绑定为仿射
- 迭代变量为数据并行或归约类型

**语义**：改变循环嵌套顺序。Reorder 是数据布局优化的关键——通过调整循环顺序可以改变缓冲区访问模式，提高缓存局部性。

### ReorderBlockIterVar 块迭代变量重排

`ReorderBlockIterVar()` 重排块内部的迭代变量顺序 [F-217]。与 Reorder 不同，此原语操作 SBlock 内部声明的 iter_vars 顺序，影响块的迭代空间组织。

### Merge 循环合并

`Merge()` 合并多个循环为一个 [F-214]。

**前置条件**：
- 循环在同一作用域
- 无注解/线程绑定
- 从 0 开始且 extent 相同
- LCA 到目标循环间为单分支

### LoopPartition 循环分区

`LoopPartition()` 将循环分区为连续循环列表 [F-213]。要求循环无注解/线程绑定。分区通常用于将不规则循环（如带条件的循环）拆分为多个规则循环。

### AddUnitLoop 添加单位循环

`AddUnitLoop()` 在块或循环上方创建新的单位循环（extent=1）[F-218]。单位循环在调度中用作"锚点"，可用于后续的 ComputeAt 或线程绑定。

## ComputeAt 计算位置系列

ComputeAt 系列原语控制生产者块和消费者块之间的相对位置，是数据局部性优化的核心。

### ComputeAt 计算位置

`ComputeAt()` 将生产者块移动到指定循环下，重新生成块诱导的循环，使产生区域覆盖消费区域 [F-230]。

**参数**：
- `block`：待移动的生产者 SBlockRV
- `loop`：目标循环 LoopRV
- `index`：插入位置（-1=最后、-2=最前）

**核心检查**：`ProducerCoversConsumer` 逐维使用算术分析器证明产生区域覆盖消费区域 [F-197]。如果不满足，说明移动生产者会导致消费者读取到未计算的数据。

**语义**：将生产者块的计算嵌套到消费者的某层循环内，使得生产者在该循环的每次迭代中只计算消费者需要的部分数据，减少中间缓冲区的大小。

### ReverseComputeAt 反向计算位置

`ReverseComputeAt()` 将消费者块移动到指定循环下，约束与 ComputeAt 对称 [F-231]。它将消费者移动到生产者附近，而非将生产者移动到消费者。

### ComputeInline 内联计算

`ComputeInline()` 将完整非根块内联到消费者 [F-232]。

**前置条件**：
- 块仅产生一个缓冲区
- 不是唯一叶子块
- body 为简单 BufferStore

**语义**：消除块的中间缓冲区，将计算直接嵌入消费者中。适用于逐元素操作等简单计算。

### ReverseComputeInline 反向内联

`ReverseComputeInline()` 将块内联到唯一生产者 [F-233]。

**前置条件**：
- 块为完整非根块
- 仅生产消费一个缓冲区

### ComputeRoot 计算根位置

将块提升到函数根层级（最外层），独立计算完整输出。这是默认的计算位置。

### FuseReductionEpilogue 归结语段融合

`FuseReductionEpilogue()` 将 epilogue 块融合到归约块 [F-234]。当归约后紧跟逐元素操作时，融合可以避免额外的全局内存往返。

### ReadAt/WriteAt 指定位置读写缓存

`ReadAt()` 在指定循环位置创建读取缓存；`WriteAt()` 在指定循环位置创建写入缓存 [F-229]。这是 CacheRead/CacheWrite 与 ComputeAt 的组合快捷方式。

## 缓存原语

缓存原语在生产者和消费者之间插入缓存阶段，改善数据局部性。

### CacheRead 读取缓存

`CacheRead()` 创建读取缓存块 [F-223]。

**前置条件**：
- 作用域内至多一个写入者
- 作用域块有 stage-pipeline 属性

**语义**：在消费者读取数据之前，将数据从原始缓冲区复制到缓存中。缓存通常位于更快的内存层次（如 GPU 共享内存）。

**参数**：
- `block`：消费者块
- `read_buffer_index`：要缓存的读取缓冲区索引
- `storage_scope`：缓存的存储范围（如 "shared"、"local"）

### CacheWrite 写入缓存

`CacheWrite()` 创建写入缓存块 [F-234]。要求仅有一个写入者。

**语义**：生产者先写入缓存，然后在适当位置将缓存刷新到原始缓冲区。

### CacheInplace 原地缓存

`CacheInplace()` 同时为读/写缓冲区创建缓存块（目标块同时读写该缓冲区）[F-226]。

### ReindexCacheRead/ReindexCacheWrite 重索引缓存

`ReindexCacheRead()`/`ReindexCacheWrite()` 使用用户自定义 IndexMap 创建重索引缓存 [F-225]。允许以非平凡的索引模式重排缓存数据。

### CacheIndex 索引缓存

`CacheIndex()` 缓存预计算的索引，`cse_thresh` 参数确定公共子表达式的重复阈值 [F-227]。当索引计算复杂时，缓存索引可以减少重复计算。

### ReIndex 重索引阶段

`ReIndex()` 创建重索引阶段块 [F-228]。

**前置条件**：
- 仅有一个读/写者
- 块中仅有一个 buffer load/store

## ForKind 操作原语

ForKind 原语设置循环的执行方式，对应 ForKind 枚举的五种类型。

### Parallel 并行化

`Parallel()` 并行化循环 [F-219]。

**前置条件**：
- 作用域块有 stage-pipeline 属性
- 块为完整/归约块且仿射绑定
- 循环仅在数据并行迭代绑定中

**语义**：将 ForKind 设置为 kParallel，使用多线程并行执行循环迭代。在 CPU 后端，代码生成器创建并行启动代码；在 GPU 后端不适用（使用 Bind 代替）。

### Vectorize 向量化

`Vectorize()` 向量化循环，约束与 Parallel 类似 [F-220]。

**语义**：将 ForKind 设置为 kVectorized，代码生成器将循环体中的标量操作替换为 SIMD 向量指令。要求循环内无数据依赖。

### Bind 线程绑定

`Bind()` 将循环绑定到线程轴 [F-221]。

**约束**：
- threadIdx 轴可绑定数据并行和归约迭代
- 其他轴（blockIdx 等）仅可绑定数据并行迭代

**语义**：将 ForKind 设置为 kThreadBinding，并关联一个 IterVar 作为线程轴。这是 GPU 编程模型的核心——将循环迭代映射到 CUDA thread/block 层次。

### Unroll 循环展开

`Unroll()` 展开循环，无特殊约束 [F-222]。

**语义**：将 ForKind 设置为 kUnrolled，编译器将循环体完全展开或按因子展开。展开可以消除循环开销但增加代码大小。

## 归约原语

归约原语优化归约计算（如 sum、max），是高性能计算的关键模式。

### RFactor 归约因式分解

`RFactor()` 通过指定循环对归约块进行因式分解 [F-236]。

**参数**：
- `loop`：用于因式分解的归约循环
- `factor_axis`：新维度在 rfactor 缓冲区中的位置

**语义**：将归约计算拆分为两阶段：第一阶段在每个线程/块中部分归约，第二阶段合并部分结果。这是 GPU 并行归约的标准模式——将全局归约分解为线程块内归约和块间归约。

### DecomposeReduction 归约分解

`DecomposeReduction()` 将归约块分解为 init 块和 update 块 [F-235]。

**参数**：
- `block`：归约块
- `loop`：作为 init/update 分界的循环（必须是块的祖先）

**语义**：init 块插入到指定循环前（执行初始化），update 块是原块去掉 init。这种分解使得初始化可以在不同的作用域执行，例如在 GPU 上 init 在全局内存执行一次，update 在每个线程中执行。

### SetThreadScope 设置线程范围

设置归约变量的线程范围，控制跨线程归约的语义。

## 注解与属性原语

### Annotate/Unannotate 注解

`Annotate()`/`Unannotate()` 为块/循环添加/移除键值对注解 [F-242]。注解用于传递提示信息给后续 Pass，如软件流水线参数、双缓冲配置等。

### Pragma 编译指示

与 Annotate 类似，Pragma 设置编译器特定的提示。

### StorageAlign 存储对齐

`StorageAlign()` 设置缓冲区特定维度的对齐要求 [F-237]：

```text
stride[axis] == k * factor + offset
```

**语义**：约束缓冲区某维度的步幅满足对齐条件。这依赖 Arith 子系统的 ModularSet 分析来验证和利用对齐信息。

### SetScope 设置存储范围

`SetScope()` 设置缓冲区的存储范围 [F-238]。例如将缓冲区标记为 "shared"（GPU 共享内存）或 "local"（寄存器）。

### UnsafeSetDType 不安全设置类型

`UnsafeSetDType()` 不安全地设置缓冲区数据类型（可能改变正确性）[F-238]。用于混合精度等需要手动管理类型转换的场景。

### SetAxisSeparator 设置轴分隔符

`SetAxisSeparator()` 设置缓冲区的轴分隔符 [F-239]，控制维度在内存层次中的分组。

## 张量化原语

### Tensorize 张量化

`Tensorize()` 使用张量化内建函数替换循环/块的计算 [F-241]。

**参数**：
- `loop_or_block`：目标 LoopRV 或 SBlockRV
- `intrin`：TensorIntrin 对象

**语义**：TensorIntrin 包含 `desc`（描述计算的 PrimFunc）和 `impl`（实现执行的 PrimFunc）[F-158]。调度器将目标块的计算模式与 desc 匹配，匹配成功后用 impl 替换。这是利用硬件张量指令（如 Tensor Core、DMA 引擎）的机制。

FFI 层 `ScheduleTensorize` 通过运行时类型检查支持 SBlockRV 和 LoopRV 两种目标 [F-255]。

### DecomposePadding 填充分解

`DecomposePadding()` 将填充块分解为常量填充块和边界内写入块 [F-245]。这使得张量化可以在非填充区域使用张量指令，边界区域使用标量代码。

### PadEinsum Einsum 填充

`PadEinsum()` 对 Einsum 计算进行填充 [F-245]，使其维度满足张量化的对齐要求。

## 布局变换原语

### TransformLayout 变换布局

`TransformLayout()` 通过 IndexMap 变换缓冲区布局 [F-243]。

**参数**：
- `buffer`：目标缓冲区
- `index_map`：IndexMap 变换函数
- `pad_value`：填充值
- `assume_injective_transform`：跳过重叠检查

**语义**：改变缓冲区的物理内存布局而不改变逻辑计算。常用于将 NCHW 转换为 NCHWc（分块通道）等硬件友好布局。

### TransformBlockLayout 变换块布局

`TransformBlockLayout()` 通过双射仿射 IndexMap 变换块迭代器和块体 [F-244]。需要逆映射。与 TransformLayout 不同，此原语同时变换块的迭代空间和访问模式。

### RollingBuffer 滚动缓冲

`RollingBuffer()` 通过滚动缓冲计算目标缓冲区，选择最外层可滚动轴进行折叠和循环化 [F-246]。滚动缓冲是一种重用寄存器/共享内存的技术，通过循环化缓冲区地址来减少内存分配。

### UnsafeHideBufferAccess/AnnotateBufferAccess

- `UnsafeHideBufferAccess()` 隐藏块中的缓冲区访问 [F-247]
- `AnnotateBufferAccess()` 通过 IndexMap 注解缓冲区的读写区域 [F-247]

## Blockize 块化

`Blockize()` 有两个重载 [F-240]：
1. 将以循环为根的子树转为块
2. 将多个块组合为嵌套块

Blockize 是将命令式循环结构转换为 SBlock 声明式结构的桥梁。在 TVMScript 解析或 TE lowering 后，可能需要 Blockize 来生成规范的 SBlock 形式。

## FFI 注册

Schedule 的 FFI 方法以 `s_tir.schedule.Schedule*` 命名，通过 `TVM_FFI_STATIC_INIT_BLOCK` 和 `refl::GlobalDef()` 注册 [F-248]。C++ 端方法注册使用 `def_method`，全局函数使用 `def` [F-298]。

主要 FFI 方法分组 [F-249~F-256]：

| 分组 | FFI 方法 |
|------|---------|
| 工具方法 | GetMod/GetState/GetTrace/Copy/Seed/WorkOn |
| 查找 | Get（通过 as<> 运行时类型分派） |
| 循环变换 | Merge/Fuse/Split/LoopPartition/Reorder |
| ForKind | Parallel/Vectorize/Bind/Unroll |
| 缓存 | CacheRead/CacheWrite/ReindexCacheRead/CacheInplace |
| 计算位置 | ComputeAt/ReverseComputeAt/ComputeInline |
| 张量化 | Tensorize（支持 SBlockRV 和 LoopRV） |
| 布局变换 | TransformLayout/TransformBlockLayout |

Python 层约 80 个 FFI 函数通过 `_ffi_api` 模块自动绑定 [F-249~F-256]。

## 前置条件检查机制

每个调度原语在执行前进行严格的前置条件检查。检查失败时抛出 `ScheduleError` [F-292]，包含：

- 错误类型和描述
- 涉及的块/循环名称
- IR 上下文（根据 error_render_level 决定详细程度）

前置条件检查依赖 Arith 子系统进行证明：
- ComputeAt 使用 `ProducerCoversConsumer` 证明区域覆盖 [F-197]
- StorageAlign 使用 ModularSet 分析步幅约束 [F-237]
- 区域分析使用 IntSetAnalyzer [F-195][F-196]

这种"先验证后变换"的设计确保了调度原语的正确性——非法的调度组合在编译期即被拒绝，而非生成错误的代码。

## 相关概念

- [SBlock 声明式调度](/concepts/07-sblock-schedule.md)
- [TIRx 中间表示](/concepts/05-tirx-ir.md)
- [MetaSchedule 自动调度](/concepts/09-meta-schedule.md)
- [Arith 整数分析器](/concepts/10-arith-analyzer.md)
