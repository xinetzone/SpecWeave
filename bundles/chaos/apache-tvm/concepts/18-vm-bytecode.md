---
type: Concept
title: VM 字节码虚拟机
description: TVM VM 字节码执行引擎，涵盖 VirtualMachine 核心、Instruction/Opcode 指令集、Executable 常量池与函数表、ExecBuilder、PagedKVCache 及 AttentionBackend
tags: [tvm, runtime, vm, bytecode, executable, kvcache, attention, llm]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
---

# VM 字节码虚拟机

TVM 虚拟机（Virtual Machine，VM）是 Relax 图级 IR 的默认执行后端。与传统的图执行器（Graph Executor）相比，VM 支持动态形状、控制流、递归函数和动态内存分配，能够执行由 Relax 编译产生的任意复杂程序。VM 采用基于寄存器的字节码架构，将 Relax 函数编译为紧凑的指令序列，在运行时由 VM 解释执行。VM 还内置了对大语言模型（LLM）推理的关键支持，包括分页式 KV 缓存（PagedKVCache）和注意力后端抽象。

## VirtualMachine 核心

`VirtualMachine` 类定义在 `include/tvm/runtime/vm/vm.h`，是 VM 执行引擎的核心 [F-60]。

### 关键方法

- **`Init`**：初始化 VM 状态，包括寄存器堆、常量池加载和内置函数注册 [F-61]。
- **`LoadExecutable`**：加载 VM 可执行文件（Executable），准备执行环境 [F-62]。
- **`GetClosure`**：获取闭包对象，支持高阶函数和部分应用 [F-63]。

VM 实现在 `src/runtime/vm/vm.cc`，包含两个核心执行机制 [F-64]：
- **`RunLoop`**：指令调度主循环，逐条读取并执行字节码指令。
- **`InvokeBytecode`**：函数调用逻辑，处理参数传递、栈帧管理和返回值。

### Python 端

Python 端 `VirtualMachine` 类定义在 `python/tvm/runtime/vm.py` [F-65]，支持两种内存分配器 [F-66]：
- **`NAIVE_ALLOCATOR = 1`**：简单分配器，每次分配新内存。
- **`POOLED_ALLOCATOR = 2`**：池化分配器，复用已释放的内存块，适合推理服务场景。

VM 构造函数接收 `rt_mod`（运行时模块或 Executable）、`device`（设备或设备列表）和 `memory_cfg`（内存配置）[F-67]。构造时调用 `rt_mod["vm_load_executable"]()` 加载可执行文件 [F-68]，并缓存 `invoke_closure` 和 `save_function` 函数句柄 [F-69]。

`VMInstrumentReturnKind` 枚举定义了插桩返回类型，包含 `NO_OP=0` 和 `SKIP_RUN=1` [F-70]，用于 VM 调试和性能分析工具。

## 字节码与指令集

### Opcode

`Opcode` 枚举定义在 `include/tvm/runtime/vm/bytecode.h`，包含 VM 支持的所有指令操作码 [F-71]。指令集涵盖：

**控制流指令** [F-72]：
- `Call`：函数调用。
- `Ret`：函数返回。
- `Goto`：无条件跳转。
- `If`：条件分支。

**数据操作指令**：包括常量加载、张量分配、张量视图创建、元组构造/解构等。

**算子调用指令**：通过 `ffi::Function` 机制调用 TIR 编译函数或运行时内置函数。

### Instruction

`Instruction` 结构体定义在同一头文件，表示单条字节码指令 [F-73]，包含操作码和操作数。VM 采用基于寄存器的设计：指令操作数是寄存器编号，而非栈位置。这使得：

1. **指令更紧凑**：常见操作只需一条指令（如 `R0 = Call R1, R2, R3`）。
2. **执行更高效**：避免频繁的栈 push/pop 操作。
3. **优化更容易**：编译器可在编译期进行寄存器分配。

字节码实现在 `src/runtime/vm/bytecode.cc`，包含指令的解码和执行逻辑 [F-74]。

## Executable：可执行文件

`Executable` 类定义在 `include/tvm/runtime/vm/executable.h`，表示 VM 可执行文件 [F-75]。一个 Executable 包含执行一个 Relax 模型所需的全部信息：

### 组成部分

1. **常量池（Constant Pool）**：存储模型权重和常量张量。常量被去重和索引，指令通过常量索引引用。
2. **指令序列**：每个函数对应一段 Instruction 数组。
3. **函数表**：函数名到指令起始位置和参数数量的映射。
4. **符号形状表达式**：编译后的形状计算函数。
5. **设备分配信息**：张量到设备的映射。

Executable 实现在 `src/runtime/vm/executable.cc`，包含字节码、常量池、函数表的序列化与反序列化 [F-76]。Python 端 `Executable` 类从 `python/tvm/runtime/executable.py` 导出 [F-77]。

Executable 的 `jit()` 方法将可执行文件即时编译为运行时模块 [F-78]，允许 VM 函数被直接调用而无需通过字节码解释。

## ExecBuilder：可执行文件构建器

Relax 编译流程通过 `ExecBuilderNode`（定义在 `include/tvm/relax/exec_builder.h`）构建 VM 可执行文件。ExecBuilder 提供了一套生成 VM 字节码的 API：

| 方法 | 功能 |
|------|------|
| `DeclareFunction(name)` | 声明函数（可多次声明） |
| `EmitFunction(name, num_inputs, param_names, kind, init_register_size)` | 标注 VM 函数开始 [F-153] |
| `EndFunction()` | 标注 VM 函数结束 [F-154] |
| `EmitCall(func_name/func_idx, args, dst)` | 发射函数调用指令 [F-155] |
| `EmitRet(result)` | 发射返回指令 [F-156] |
| `EmitGoto(pc)` | 发射跳转指令 |
| `EmitIf(cond, tgt, false_tgt)` | 发射条件分支指令 |
| `GetFunction(name)` | 获取函数索引 |
| `ConvertConstant(value)` | 转换常量并更新常量池 [F-157] |
| `SaveMemoryScope()` | 为常量构建内存作用域 [F-158] |

ExecBuilder 内部持有 `vm::VMExecutable` 和常量去重映射 `const_dedup_map_` [F-152]。`exec()` 返回底层可执行文件的原始指针，`Get()` 完成构建、运行 formalize 并返回最终结果 [F-158]。`ExecBuilder::Create()` 静态工厂方法创建实例 [F-159]。内部有 `CheckExecutable()` 检查寄存器使用是否合法，`Formalize()` 完成可执行文件的形式化 [F-160]。

## 内建函数

VM 内建函数实现在 `src/runtime/vm/builtin.cc` [F-79]，提供 VM 执行时可用的基础操作。这些函数通过 FFI 全局函数注册表注册，包括：

- **形状操作**：查询张量形状、形状表达式求值。
- **内存管理**：张量分配、视图创建、内存复制。
- **设备操作**：设备同步、跨设备拷贝。
- **张量操作**：reshape（CreateView，零拷贝视图）、concatenate 等。
- **调试操作**：打印张量值、断言。

Relax 的 `LowerRuntimeBuiltin` Pass 将高层内置算子降级为对这些 VM 内置函数的调用，`VMShapeLower` Pass 将形状表达式降级为 VM 形状堆和 TIR 函数。

## PagedKVCache：分页式 KV 缓存

Paged KV Cache 实现在 `src/runtime/vm/paged_kv_cache.cc` [F-80]，是 TVM 为大语言模型推理提供的核心优化。传统 KV 缓存为每个序列预分配连续的大内存块，导致：

- **内部碎片**：序列实际长度可能远小于预分配长度。
- **外部碎片**：不同长度序列的内存块难以复用。
- **扩容困难**：序列增长时需要重新分配和拷贝。

PagedKVCache 借鉴操作系统的虚拟内存分页机制：

1. **固定大小页面**：KV 缓存被划分为固定大小的页面（page），每个页面存储固定数量 token 的键和值。
2. **页面表**：每个序列维护一个页面表，逻辑 token 位置通过页面表映射到物理页面。
3. **按需分配**：新 token 到达时分配新页面，无需预分配大块连续内存。
4. **页面共享**：不同序列（如 beam search 的多个分支）可共享相同前缀的页面。

PagedKVCache 支持注意力后端（AttentionBackend）的插拔，可将注意力计算委托给 FlashInfer、CUTLASS 等高性能库。它管理 K/V 张量的页面分配、释放和查询，为 LLM 推理提供高效的内存管理。

## AttentionBackend：注意力后端抽象

Attention 后端实现在 `src/runtime/vm/attn_backend.cc` [F-81]，提供注意力计算的后端抽象层。这一抽象使 TVM 能够：

1. **统一接口**：PagedKVCache 和 Relax 注意力算子通过统一接口调用不同的注意力实现。
2. **后端插拔**：支持 FlashInfer、CUTLASS、vLLM 等第三方注意力库作为后端。
3. **回退机制**：无外部后端时使用 TVM 自身的 TIR 实现。
4. **硬件适配**：不同后端可针对特定硬件（NVIDIA GPU、AMD GPU 等）优化。

注意力后端通常提供以下功能：
- Prefill 阶段注意力计算（处理整个提示序列）。
- Decode 阶段注意力计算（逐 token 生成）。
- Paged KV Cache 感知的注意力核函数。
- 因果掩码（causal mask）和滑动窗口支持。

## RNN State 与 KV State

VM 为序列模型维护状态对象：
- **RNNState**：RNN 类模型的隐藏状态。
- **KVState**：Transformer 模型的键值缓存状态。

这些状态在多轮推理调用间保持，避免每次调用重新分配。状态可以被保存（`save_function`）和恢复，支持推理检查点和连续生成。

## TensorCacheSupport

TensorCacheSupport 为 VM 提供张量缓存能力，缓存常用的中间结果（如位置编码、注意力掩码），避免重复计算。

## VM 执行流程

一个完整的 Relax → VM 执行流程如下：

1. **编译期**：
   - Relax IR 经过 Pass 流水线优化（融合、合法化、布局转换等）。
   - `VMShapeLower` 将形状表达式编译为 TIR 函数。
   - `LowerRuntimeBuiltin` 将内置算子映射到 VM 内置函数。
   - ExecBuilder 将 Relax 函数翻译为 VM 字节码指令。
   - TIR PrimFunc 通过代码生成编译为设备机器码（DSOModule）。
   - 所有组件打包为 VM Executable。

2. **运行期**：
   - VirtualMachine 加载 Executable。
   - 初始化设备、内存分配器和常量池。
   - 调用入口函数，VM 进入 RunLoop。
   - 逐条执行指令：控制流指令由 VM 直接处理，算子调用通过 `ffi::Function` 分发到编译后的设备函数。
   - PagedKVCache 管理 LLM 的 KV 内存。
   - 注意力计算通过 AttentionBackend 委托给优化后端。
   - 函数返回时，Ret 指令恢复调用者栈帧。

## 设计要点

VM 字节码架构的设计体现了以下考量：

1. **动态性优先**：相比静态图执行器，VM 天然支持动态形状、控制流和递归，适应现代深度学习模型（尤其 LLM）的需求。
2. **寄存器架构**：基于寄存器的字节码比栈式架构更紧凑、更高效，减少指令分发开销。
3. **可序列化部署**：Executable 可序列化为文件，在无编译器环境的部署端加载运行。
4. **LLM 原生支持**：PagedKVCache 和 AttentionBackend 不是事后附加的补丁，而是 VM 执行模型的一等组件，反映了 TVM 对 LLM 推理场景的深度适配。
5. **分层降级**：Relax → VM 字节码 → `ffi::Function` → 设备代码，每层职责清晰，便于调试和优化。

## 相关概念

- [Relax 图级 IR](/concepts/11-relax-ir.md) — VM 是 Relax 图级 IR 的默认执行后端，支持动态形状和控制流
- [Relax 变换 Pass](/concepts/14-relax-passes.md) — VMShapeLower、LowerRuntimeBuiltin 等 Pass 将 Relax 降级为 VM 可执行格式
- [Runtime Module 系统](/concepts/17-runtime-module.md) — VMExecutable 作为 Module 实现被加载，通过 `ffi::Function` 调用设备代码
- [LLM 推理支持](/concepts/21-llm-inference.md) — VM 内置 PagedKVCache 和 AttentionBackend，为 LLM 推理提供核心运行时支持
- [FFI 基础设施](/concepts/01-ffi-foundation.md) — VM 字节码中的算子调用通过 `ffi::Function` 打包调用约定分发到 TIR 编译函数
