---
type: Concept
title: LLM 推理支持
description: TVM 大语言模型推理基础设施，涵盖 PagedAttention/KVCache、PagedKVCache 实现、AttentionBackend 抽象、RNN/KV State 及 Relax NN LLM 前端
tags: [tvm, llm, inference, paged-attention, kv-cache, attention-backend, flashinfer, cutlass]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# LLM 推理支持

随着大语言模型（Large Language Model，LLM）成为深度学习推理的重要工作负载，TVM 在 Runtime 和 Relax 层面构建了专门的 LLM 推理基础设施。这些设施解决了 LLM 推理的核心挑战：自回归生成的内存效率、注意力计算的高性能、动态序列长度的支持以及多后端的灵活适配。TVM 的 LLM 支持以 PagedKVCache 为核心内存管理机制，以 AttentionBackend 为注意力计算抽象层，并通过 Relax NN 模块提供 LLM 前端组件。

## LLM 推理的核心挑战

LLM 推理分为两个阶段：

1. **Prefill（预填充）**：一次性处理整个输入提示（prompt），计算所有 token 的键（Key）和值（Value）并填充 KV 缓存。此阶段计算密集，适合大批次并行。
2. **Decode（解码）**：逐个生成新 token，每步只需计算新 token 的 K/V，然后与缓存中所有历史 K/V 做注意力。此阶段内存带宽密集，批次小但序列长度不断增长。

传统实现面临以下问题：
- **KV 缓存内存浪费**：预分配连续大内存导致内部碎片。
- **注意力计算瓶颈**：长序列注意力的 O(n²) 复杂度需要专门优化。
- **动态形状**：序列长度在运行时变化，静态形状编译器难以处理。
- **后端多样性**：不同 GPU/加速器需要不同的注意力核函数。

## KVCache 基础

KV 缓存是 Transformer 推理的标准优化技术。在自注意力计算中，每个 token 的 Query 与所有之前 token 的 Key/Value 交互。由于已生成 token 的 Key/Value 不会改变，可以缓存起来避免重复计算。

KV 缓存的传统实现为每个序列预分配形状为 `[num_layers, num_heads, max_seq_len, head_dim]` 的连续张量，存在以下问题：

- **内部碎片**：实际序列长度远小于 `max_seq_len` 时浪费大量内存。
- **扩容困难**：序列超长时需要重新分配和拷贝。
- **共享困难**：Beam search 等多分支场景下，相同前缀的缓存无法高效共享。
- **批量管理复杂**：不同长度的序列难以批量处理。

## PagedAttention 与 PagedKVCache

### PagedAttention 原理

PagedAttention 借鉴操作系统虚拟内存分页机制，将 KV 缓存划分为固定大小的**页面（page）**。每个页面存储固定数量 token（如 16 个）的 K/V。逻辑上连续的 token 序列在物理上不需要连续存储，通过**页面表（page table）**映射逻辑位置到物理页面。

### PagedKVCache 实现

Paged KV Cache 实现在 `src/runtime/vm/paged_kv_cache.cc` [F-80]，是 TVM VM 运行时的一等组件。其核心数据结构和机制包括：

**页面管理**：
- 物理页面池预分配在 GPU/设备内存中。
- 每个序列维护独立的页面表，逻辑 token 位置通过页面表转换为 `(page_id, offset_within_page)`。
- 新 token 生成时按需分配新页面，无需预分配最大长度。

**注意力核函数集成**：
- PagedKVCache 不直接实现注意力计算，而是将页面表和页面数据传递给 AttentionBackend。
- 注意力核函数通过页面表间接访问 K/V，支持非连续内存布局。

**序列管理**：
- 支持多序列并行（continuous batching），不同序列的页面可交错分配。
- 支持序列 fork（beam search），fork 时复制页面表而非页面数据（写时复制）。
- 支持序列删除，页面归还到空闲池供其他序列使用。

**内存效率**：
- 内部碎片仅限于最后一个页面的未使用部分。
- 相同系统提示（system prompt）的多个序列可共享前缀页面。
- 页面大小可配置，平衡内存利用率和页表开销。

## AttentionBackend 抽象

Attention 后端实现在 `src/runtime/vm/attn_backend.cc` [F-81]，提供注意力计算的可插拔抽象层。这一设计使 TVM 能够利用生态中各种高性能注意力实现，而无需为每个后端重写上层逻辑。

### 抽象接口

AttentionBackend 定义了注意力计算的统一接口，通常包括：

- **Prefill 注意力**：处理新提示序列，一次性计算所有位置的注意力。
- **Decode 注意力**：处理单个新 token，与分页 KV 缓存中的历史 K/V 交互。
- **页面表感知**：核函数接收 PagedKVCache 的页面表，正确访问非连续 K/V。
- **掩码支持**：因果掩码、滑动窗口、自定义注意力掩码。
- **头分组支持**：Grouped Query Attention（GQA）、Multi-Query Attention（MQA）。

### 后端集成

通过 AttentionBackend 抽象，TVM 可集成以下注意力实现：

- **FlashAttention**：IO 感知的精确注意力算法，通过分块计算减少 HBM 访问。
- **FlashInfer**：专为 LLM 推理优化的注意力内核库，支持分页 KV 缓存。
- **CUTLASS**：NVIDIA 的模板化 GEMM 和注意力库。
- **TVM 原生 TIR 实现**：通过 MetaSchedule 自动调优生成的注意力核函数。
- **vLLM 集成**：与 vLLM 的 PagedAttention 实现兼容。

后端选择在编译期或运行期配置，PagedKVCache 将注意力调用路由到当前活跃的后端。这种设计允许用户根据硬件和模型特性选择最优实现，也便于新硬件后端快速接入。

## RNN State 与 KV State

VM 为序列模型维护两类状态对象：

### RNNState

用于传统 RNN/LSTM/GRU 类模型，保存每轮推理之间的隐藏状态。RNNState 通常是固定形状的张量，在每次推理调用中被读取和更新。

### KVState

用于 Transformer 模型的键值缓存状态。在 TVM 的 LLM 运行时中，KVState 封装了 PagedKVCache 的引用，管理：
- 当前序列的页面表。
- 已缓存的 token 数量。
- K/V 张量的物理页面池。
- 序列间的共享关系。

这些状态通过 VM 的 `save_function` 和 `invoke_closure` 机制在多轮调用间保持。Python VM 缓存了 `invoke_closure` 和 `save_function` 函数句柄 [F-69]，支持高效的状态持久化。

## TensorCacheSupport

TensorCacheSupport 为 VM 提供张量缓存能力，在 LLM 推理中用于缓存不随 token 位置变化的常量张量，如：
- 位置编码（RoPE 的 cos/sin 表）。
- 因果掩码模板。
- ALiBi 斜率矩阵。

缓存这些张量避免了每轮推理的重复计算和内存分配。

## Relax NN LLM 前端

Relax 的 `nn` 模块提供构建 LLM 的高层组件，定义在 `python/tvm/relax/op/nn/` 中。

### 注意力组件

Relax NN 提供了灵活的注意力前端：

- **`attention`**：基础注意力算子，支持 Q/K/V 输入、注意力掩码和缩放因子。
- **`R.nn.attention`**：Relax 方言中的注意力 API。
- 注意力算子在编译期被 Legalize 为调用 TIR 注意力函数或外部后端函数。

### KV 缓存操作

Relax 提供与 PagedKVCache 交互的算子：
- **缓存读取**：从分页缓存中按位置读取 K/V。
- **缓存追加**：将新 token 的 K/V 写入新分配的页面。
- **缓存视图**：创建缓存的视图用于注意力计算。
- **注意力与缓存融合**：将 Q/K/V 计算、缓存写入和注意力计算融合为单个算子。

### Position Embedding

- **RoPE（Rotary Position Embedding）**：旋转位置编码，在 Q/K 上施加位置相关的旋转变换。
- **Alibi**：注意力线性偏置，为不同距离的注意力头添加固定斜率的偏置。
- **学习式位置编码**：传统的可学习位置嵌入。

### Tree Attention

在 Beam Search 或并行采样等多分支解码场景中，多个候选序列共享前缀。Tree Attention 允许：
- 构建树状的 KV 缓存结构，分支共享前缀页面。
- 注意力计算时遍历树结构，为每个分支聚合对应的 K/V。
- 配合 PagedKVCache 的页面共享机制，避免重复存储。

### Prefill/Decode 分离

Relax NN 模块允许模型定义区分 prefill 和 decode 路径：
- Prefill 路径可使用更大的批次和更激进的并行。
- Decode 路径针对单 token 生成优化，使用 PagedKVCache。
- 两条路径可编译为不同的 VM 函数，在运行时根据阶段选择调用。

## VM 内存分配器

Python VirtualMachine 支持两种分配器 [F-66]：

- **NAIVE_ALLOCATOR（1）**：每次内存分配向设备申请新内存，释放时归还。适合简单场景。
- **POOLED_ALLOCATOR（2）**：池化分配器，维护内存块池，分配时复用已释放的块。这是 LLM 推理的推荐配置，显著减少内存分配开销和碎片。

`memory_cfg` 参数允许配置不同设备和内存范围的池大小，根据模型规模和 KV 缓存需求调整。

## 编译流水线集成

LLM 推理支持贯穿 Relax 编译流水线：

1. **前端模型定义**：使用 Relax NN 组件定义 Transformer 模型，标注 KV 缓存和注意力。
2. **算子合法化**：`LegalizeOps` 将高层注意力算子降级为 call_tir，调用 TIR 注意力函数或外部后端。
3. **算子融合**：`FuseOps`/`FuseTIR` 融合 Q/K/V 投影、RoPE、注意力和输出投影。
4. **内存规划**：`StaticPlanBlockMemory` 和 `KillAfterLastUse` 优化中间张量内存。
5. **混合精度**：`ToMixedPrecision` 将计算转为 fp16/bf16 减少内存和计算量。
6. **VM 降级**：`VMShapeLower` 和 `LowerRuntimeBuiltin` 生成 VM 字节码，PagedKVCache 作为 VM 内置对象管理。
7. **代码生成**：注意力核函数通过 CUDA/Metal/Vulkan 后端编译为设备代码，或委托给 FlashInfer/CUTLASS 外部库。

## dlight GPU 自动调度

对于未使用外部注意力后端的场景，TVM 的 dlight GPU 自动调度规则可为注意力和其他 LLM 算子生成高性能 GPU kernel。dlight 提供针对 GEMV、reduction、matmul 等模式的规则，在 MetaSchedule 框架下自动搜索和应用调度。

## 设计要点

TVM LLM 推理支持的设计体现了以下原则：

1. **运行时与编译器协同**：PagedKVCache 是 VM 运行时对象而非编译期常量，使动态序列长度和多序列管理成为可能；编译器通过算子和 Pass 与运行时协同。
2. **注意力后端可插拔**：AttentionBackend 抽象使 TVM 不绑定于单一注意力实现，可利用社区最新的高性能 kernel。
3. **分页内存管理**：借鉴经典操作系统概念解决现代 AI 推理问题，显著提升内存利用率和批量处理能力。
4. **端到端优化**：从前端模型定义到运行时执行，KV 缓存、注意力、内存分配和调度形成完整优化链。
5. **开放生态**：不重新发明轮子，通过集成 FlashInfer、CUTLASS、vLLM 等外部库，与更广泛的 LLM 推理生态互通。

## 相关概念

- [Relax 图级 IR](/concepts/11-relax-ir.md) — LLM 模型通过 Relax NN 前端定义，动态形状和控制流由 Relax 原生支持
- [MetaSchedule 自动调度](/concepts/09-meta-schedule.md) — dlight GPU 自动调度规则为注意力和 GEMV 等 LLM 算子生成高性能 kernel
- [Runtime Module 系统](/concepts/17-runtime-module.md) — LLM 推理在 TVM Runtime 上执行，使用 NDArray/DeviceAPI/ThreadPool 等基础设施
- [VM 字节码虚拟机](/concepts/18-vm-bytecode.md) — PagedKVCache 和 AttentionBackend 是 VM 运行时的一等组件，支撑 LLM 执行
- [Relax 变换 Pass](/concepts/14-relax-passes.md) — 算子融合、混合精度、内存规划等 Pass 共同优化 LLM 推理性能
- [Relax 算子体系](/concepts/13-relax-ops.md) — attention、RoPE、KV cache 操作等 LLM 核心算子在 Relax 算子层定义并合法化
