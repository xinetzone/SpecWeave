# Concepts 索引

Apache TVM 概念文档共 22 篇，按 TVM 四层栈架构分四批组织。

## 第一批：基础架构（00-04）

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [架构总览](00-overview.md) | TVM 四层栈架构（FFI/TIR/Relax/Runtime）与编译流水线 |
| 01 | [FFI 基础设施](01-ffi-foundation.md) | TVM-FFI 跨语言函数调用、C ABI 与类型系统 |
| 02 | [Object 对象系统](02-object-system.md) | Object/ObjectRef 引用计数、容器系统与反射 |
| 03 | [Pass 基础设施](03-pass-infrastructure.md) | PassContext、Pass 注册与 IRModule 变换框架 |
| 04 | [Target 与代码生成](04-target-codegen.md) | Target 多后端描述系统与 LLVM/C 代码生成框架 |

## 第二批：TIR 与调度（05-10）

| 编号 | 文档 | 说明 |
|------|------|------|
| 05 | [TIRx 中间表示](05-tirx-ir.md) | TIRx 命名空间、表达式/语句节点、SBlock、PrimFunc |
| 06 | [Buffer/Var/IterVar 核心类型](06-buffer-var-itervar.md) | Buffer 13 字段、Var/PrimVar、IterVar 9 种类型 |
| 07 | [SBlock 声明式调度](07-sblock-schedule.md) | Schedule 核心类、RV 体系、ScheduleState、Trace |
| 08 | [调度原语](08-schedule-primitives.md) | split/fuse/reorder、compute_at、cache_read/write、tensorize |
| 09 | [MetaSchedule 自动调度](09-meta-schedule.md) | TuneContext/SearchStrategy/CostModel/Database/dlight |
| 10 | [Arith 整数分析器](10-arith-analyzer.md) | Analyzer 七子分析器、ConstIntBound、Z3Prover、IntSet |

## 第三批：Relax 与 TE（11-16）

| 编号 | 文档 | 说明 |
|------|------|------|
| 11 | [Relax 图级 IR](11-relax-ir.md) | 动态形状、DataflowVar、BindingBlock、Function、类型系统 |
| 12 | [BlockBuilder 与 Dataflow](12-relax-block-builder.md) | Emit/Normalize、作用域管理、DFPattern 模式匹配 |
| 13 | [Relax 算子体系](13-relax-ops.md) | 算子分类、Attrs、FNormalize/FLegalize、OpPatternKind |
| 14 | [Relax 变换 Pass](14-relax-passes.md) | 40+ Pass、算子融合、合法化、自动微分、混合精度 |
| 15 | [TE 张量表达式](15-te-tensor-expression.md) | Placeholder/ComputeOp/ScanOp、compute()、create_primfunc |
| 16 | [TOPI 算子库](16-topi-operator-library.md) | broadcast/elemwise/reduction/nn/einsum、tags、多后端调度 |

## 第四批：Runtime 与生态（17-21）

| 编号 | 文档 | 说明 |
|------|------|------|
| 17 | [Runtime Module 系统](17-runtime-module.md) | Module 导入树、ffi::Function、DeviceAPI、NDArray、ThreadPool |
| 18 | [VM 字节码虚拟机](18-vm-bytecode.md) | VirtualMachine、Instruction/Opcode、Executable、PagedKVCache |
| 19 | [RPC 与分布式](19-rpc-distributed.md) | RPCSession/Endpoint/Channel、Tracker/Proxy、Disco |
| 20 | [TVMScript DSL](20-tvmscript.md) | IRBuilder 分层架构、TIR/Relax 方言、Doc 打印体系 |
| 21 | [LLM 推理支持](21-llm-inference.md) | PagedAttention、PagedKVCache、AttentionBackend、Relax NN |

```{toctree}
:maxdepth: 2

00-overview
01-ffi-foundation
02-object-system
03-pass-infrastructure
04-target-codegen
05-tirx-ir
06-buffer-var-itervar
07-sblock-schedule
08-schedule-primitives
09-meta-schedule
10-arith-analyzer
11-relax-ir
12-relax-block-builder
13-relax-ops
14-relax-passes
15-te-tensor-expression
16-topi-operator-library
17-runtime-module
18-vm-bytecode
19-rpc-distributed
20-tvmscript
21-llm-inference
```