---
type: source-code
source_id: ir-tir
title: IR 核心与 TIRx 源码
description: TVM IR 核心层、TIRx 张量级 IR 与 S-TIR 调度系统源码登记，包含目录结构、文件统计与关键文件清单
tags: [tvm, ir, tir, s-tir, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-ir-tir
    resource: "/references/facts-ir-tir.md"
    title: IR 核心与 TIR 事实清单
---

# IR 核心与 TIRx 源码登记

- **source_id**: ir-tir
- **type**: source-code
- **path**: `d:\AI\.chaos\libs\ffi\tvm\`
- **language**: C++/Python
- **file_count**: 620
- **fact_file**: /references/facts-ir-tir.md
- **registered**: 2026-08-23

## 目录结构

| 目录 | 文件数 | 职责 |
|------|--------|------|
| `src/ir/` | 13 | IR 核心层 C++ 实现：表达式、类型、函数、模块、Pass 基础设施、Op 注册表 |
| `src/tirx/` | 103 | TIRx 张量级 IR C++ 实现：语句/表达式节点、Buffer、PrimFunc、Functor、分析与变换 |
| `src/s_tir/` | 177 | S-TIR 调度系统 C++ 实现：Schedule、ScheduleState、40+ 调度原语、Trace/Instruction、MetaSchedule |
| `include/tvm/ir/` | 19 | IR 核心层公共头文件 |
| `include/tvm/tirx/` | 22 | TIRx 公共头文件 |
| `include/tvm/s_tir/` | 34 | S-TIR 调度系统公共头文件 |
| `python/tvm/ir/` | 20 | IR 核心层 Python 绑定 |
| `python/tvm/tirx/` | 55 | TIRx Python 绑定 |
| `python/tvm/s_tir/` | 177 | S-TIR 调度系统 Python 绑定 |

## 关键文件

### IR 核心层

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/ir/expr.h` | ExprNode/Expr、PrimExpr、IntImm、FloatImm、Range、Call、GlobalVar 等核心表达式定义 |
| `include/tvm/ir/base_expr.h` | TypeNode/Type、ExprNode/Expr 基类定义 |
| `include/tvm/ir/function.h` | BaseFuncNode/BaseFunc、CallingConv、LinkageType |
| `include/tvm/ir/module.h` | IRModuleNode/IRModule，跨层函数容器 |
| `include/tvm/ir/attrs.h` | Attrs/DictAttrs 属性容器 |
| `include/tvm/ir/op.h` | Op/OpRegistry/OpRegEntry 算子注册表 |
| `include/tvm/ir/transform.h` | Pass/PassInfo/PassContext/PassInstrument 基础设施 |
| `include/tvm/ir/node_functor.h` | NodeFunctor/ExprVisitor/ExprMutator 类型分派访问者 |
| `include/tvm/ir/instrument.h` | PassInstrument 观测接口 |
| `include/tvm/ir/source_map.h` | SourceMap/Span/SequentialSpan 源码位置追踪 |
| `src/ir/module.cc` | IRModule 实现：SEqual/SHash、GlobalVar 管理 |
| `src/ir/transform.cc` | PassContext 线程局部栈、PassConfigManager |
| `src/ir/op.cc` | OpRegistry、AttrRegistry 实现 |

### TIRx 张量级 IR

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/tirx/expr.h` | TIRx 表达式：Add/Sub/Mul/Div、Cast、StringImm、Var/PrimVar |
| `include/tvm/tirx/var.h` | VarNode、PrimVar、IterVar（9 种 IterVarType） |
| `include/tvm/tirx/buffer.h` | BufferNode（13 字段多维内存布局描述）、BufferType |
| `include/tvm/tirx/stmt.h` | StmtNode 层次：For/IfThenElse/SeqStmt/SBlock/SBlockRealize/BufferStore/AllocBuffer |
| `include/tvm/tirx/function.h` | PrimFuncNode/PrimFunc、TensorIntrinNode |
| `include/tvm/tirx/expr_functor.h` | ExprFunctor/ExprVisitor/ExprMutator |
| `include/tvm/tirx/stmt_functor.h` | StmtFunctor/StmtVisitor/StmtMutator |
| `include/tvm/tirx/transform.h` | TIRx 变换 Pass 声明：VectorizeLoop/StorageRewrite/UnrollLoop/LowerTVMBuiltin |
| `include/tvm/tirx/op.h` | 算术/逻辑 Op 函数，立即常量折叠 |
| `include/tvm/tirx/builtin.h` | TIRx 内建函数（ret/thread_return/address_of 等） |
| `include/tvm/tirx/layout.h` | Layout/TileLayout/SwizzleLayout/ComposeLayout |
| `include/tvm/tirx/index_map.h` | IndexMap 索引重映射与逆映射 |
| `include/tvm/tirx/analysis.h` | TIRx 分析接口：缓冲区访问区域、依赖分析 |
| `include/tvm/tirx/exec_scope.h` | ScopeKind（kCluster/kCta/kWarpgroup/kWarp/kThread） |
| `include/tvm/tirx/exec_context.h` | ActiveSet/ExecContext 执行上下文 |

### S-TIR 调度系统

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/s_tir/schedule/schedule.h` | ScheduleNode/Schedule：Concrete/Traced 两种模式、RV 系统、40+ 调度原语 |
| `include/tvm/s_tir/schedule/state.h` | ScheduleStateNode：sref 树、stmt2ref 映射、块信息 |
| `include/tvm/s_tir/schedule/instruction.h` | InstructionKind/Instruction：调度指令记录 |
| `include/tvm/s_tir/schedule/trace.h` | Trace：apply/serialize/simplify |
| `include/tvm/s_tir/analysis.h` | 分析接口：GetSBlockAccessRegion、DetectBufferAccessLCA、EstimateTIRFlops、VerifyGPUCode |
| `include/tvm/s_tir/transform.h` | S-TIR 变换 Pass：CanonicalizeLoop、InjectSoftwarePipeline、CompactBufferAllocation 等 30+ |
| `src/s_tir/schedule/schedule.cc` | Schedule FFI 注册（约 80 个 FFI 函数） |
| `src/s_tir/schedule/state.cc` | ScheduleState 实现、AnalyzeRegionUpperBound/LowerBound、ProducerCoversConsumer |
| `src/s_tir/schedule/primitive.h` | 40+ 调度原语实现声明 |

### Python 绑定

| 文件路径 | 职责 |
|---------|------|
| `python/tvm/ir/module.py` | IRModule Python 类，字典式接口 |
| `python/tvm/ir/transform.py` | Pass/PassContext Python 类，上下文管理器协议 |
| `python/tvm/ir/op.py` | Op Python 类，get_attr/set_attr |
| `python/tvm/ir/type.py` | PrimType/PointerType/TupleType/FuncType |
| `python/tvm/ir/function.py` | BaseFunc with_attr/with_attrs/without_attr |
| `python/tvm/s_tir/schedule/schedule.py` | Schedule Python 类，默认 TracedSchedule |
