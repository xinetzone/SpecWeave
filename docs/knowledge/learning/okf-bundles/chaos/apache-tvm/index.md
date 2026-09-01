# Apache TVM 深度学习编译器

Apache TVM 是一个开源的深度学习编译器栈，通过四层架构（FFI 基础设施 → TIR 张量 IR → Relax 图级 IR → Runtime 执行引擎）实现深度学习模型的跨硬件高性能编译与部署。本知识包基于 TVM 源码（版本 0.26.dev0）整理，包含 22 篇概念文档、实践示例和完整的事实参考。

## 概念文档

### 第一批：基础架构

- [00 架构总览](concepts/00-overview.md) — TVM 四层栈架构与编译流水线
- [01 FFI 基础设施](concepts/01-ffi-foundation.md) — 跨语言函数调用、C ABI 与类型系统
- [02 Object 对象系统](concepts/02-object-system.md) — 引用计数、容器系统与反射
- [03 Pass 基础设施](concepts/03-pass-infrastructure.md) — PassContext 与 IRModule 变换框架
- [04 Target 与代码生成](concepts/04-target-codegen.md) — 多后端描述与 LLVM/C 代码生成

### 第二批：TIR 与调度

- [05 TIRx 中间表示](concepts/05-tirx-ir.md) — 表达式/语句节点、SBlock、PrimFunc
- [06 Buffer/Var/IterVar 核心类型](concepts/06-buffer-var-itervar.md) — 内存布局、变量系统与迭代空间
- [07 SBlock 声明式调度](concepts/07-sblock-schedule.md) — Schedule 类、RV 体系与 Trace
- [08 调度原语](concepts/08-schedule-primitives.md) — 循环变换、computeAt、缓存、张量化
- [09 MetaSchedule 自动调度](concepts/09-meta-schedule.md) — 搜索策略、CostModel 与 dlight GPU 调度
- [10 Arith 整数分析器](concepts/10-arith-analyzer.md) — 七子分析器、Z3Prover 与编译期证明

### 第三批：Relax 与 TE

- [11 Relax 图级 IR](concepts/11-relax-ir.md) — 动态形状、数据流变量与类型系统
- [12 BlockBuilder 与 Dataflow](concepts/12-relax-block-builder.md) — Emit/Normalize 与模式匹配
- [13 Relax 算子体系](concepts/13-relax-ops.md) — 算子分类、Attrs 与融合模式
- [14 Relax 变换 Pass](concepts/14-relax-passes.md) — 40+ Pass、融合、自动微分与混合精度
- [15 TE 张量表达式](concepts/15-te-tensor-expression.md) — Compute DSL 与 TE→TIR 降级
- [16 TOPI 算子库](concepts/16-topi-operator-library.md) — 神经网络算子与多后端调度模板

### 第四批：Runtime 与生态

- [17 Runtime Module 系统](concepts/17-runtime-module.md) — Module 导入树、ffi::Function、DeviceAPI
- [18 VM 字节码虚拟机](concepts/18-vm-bytecode.md) — 指令集、Executable 与 PagedKVCache
- [19 RPC 与分布式](concepts/19-rpc-distributed.md) — RPC 三层架构、Tracker 与 Disco
- [20 TVMScript DSL](concepts/20-tvmscript.md) — Python 嵌入式 IR 构建与打印
- [21 LLM 推理支持](concepts/21-llm-inference.md) — PagedAttention、AttentionBackend

## 示例

- [TVM 快速入门](examples/tvm-quickstart.md) — 矩阵乘法的 TE 定义、编译与运行时执行完整流程
- [示例索引](examples/index.md) — 全部示例列表

## 参考资料

- [知识地图](references/insights.md) — 架构洞察与核心论点
- [References 索引](references/index.md) — 事实清单与信源登记列表

### 事实清单

- [facts-tvm-ffi.md](references/facts-tvm-ffi.md) — FFI 基础设施事实
- [facts-ir-tir.md](references/facts-ir-tir.md) — IR 与 TIRx 事实
- [facts-relax-te-topi.md](references/facts-relax-te-topi.md) — Relax/TE/TOPI 事实（244 条）
- [facts-runtime-target-arith.md](references/facts-runtime-target-arith.md) — Runtime/Target/Arith 事实

### 信源登记

- [tvm-ffi-source.md](references/tvm-ffi-source.md)
- [ir-tir-source.md](references/ir-tir-source.md)
- [relax-te-topi-source.md](references/relax-te-topi-source.md)
- [runtime-target-arith-source.md](references/runtime-target-arith-source.md)

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
verification-report
```