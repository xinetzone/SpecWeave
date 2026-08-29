---
type: source-code
source_id: relax-te-topi
title: Relax/TE/TOPI 源码
description: TVM Relax 图级 IR、TE 张量表达式与 TOPI 算子库源码登记，包含目录结构、文件统计与关键文件清单
tags: [tvm, relax, te, topi, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-relax-te-topi
    resource: "/references/facts-relax-te-topi.md"
    title: Relax/TE/TOPI 事实清单
---

# Relax/TE/TOPI 源码登记

- **source_id**: relax-te-topi
- **type**: source-code
- **path**: `d:\AI\.chaos\libs\ffi\tvm\`
- **language**: C++/Python
- **file_count**: 664
- **fact_file**: /references/facts-relax-te-topi.md
- **registered**: 2026-08-23

## 目录结构

| 目录 | 文件数 | 职责 |
|------|--------|------|
| `src/relax/` | 217 | Relax 图级 IR C++ 实现：表达式、类型、BlockBuilder、算子、Pass、VM 后端、外部代码生成 |
| `src/te/` | 9 | TE 张量表达式 C++ 实现：Operation 层级、CreatePrimFunc 降级 |
| `src/topi/` | 8 | TOPI 算子库 C++ 实现 |
| `include/tvm/relax/` | 40 | Relax 公共头文件 |
| `include/tvm/te/` | 2 | TE 公共头文件 |
| `include/tvm/topi/` | 32 | TOPI 公共头文件 |
| `python/tvm/relax/` | 212 | Relax Python 绑定与前端 |
| `python/tvm/te/` | 6 | TE Python 绑定 |
| `python/tvm/topi/` | 138 | TOPI Python 算子实现 |

## 关键文件

### Relax 核心 IR

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/relax/expr.h` | Relax 表达式节点：Var/DataflowVar/Constant/Binding/Function/If/Tuple/ShapeExpr |
| `include/tvm/relax/type.h` | TensorType/ShapeType/AnyType/PackedFuncType，"假设语义"类型系统 |
| `include/tvm/relax/block_builder.h` | BlockBuilderNode：Emit/Normalize、作用域管理、DataflowBlock 构建 |
| `include/tvm/relax/op_attr_types.h` | FNormalize/FInferType/FValidate/FLegalize/FPrimalGradient 算子属性函数类型 |
| `include/tvm/relax/dataflow_pattern.h` | DFPattern 数据流模式匹配（用于融合和 BYOC） |
| `include/tvm/relax/binding_rewrite.h` | DataflowBlockRewriteNode：ReplaceAllUses/RemoveUnused |
| `include/tvm/relax/analysis.h` | CanProveShapeEqual/EraseToWellDefined 分析接口 |
| `include/tvm/relax/attrs/nn.h` | Conv1DAttrs/Conv2DAttrs/Conv3DAttrs 神经网络算子属性 |
| `include/tvm/relax/transform.h` | 40+ Relax Pass 声明与 CreateFunctionPass/CreateDataflowBlockPass |
| `include/tvm/relax/backend.h` | LowerRuntimeBuiltin/VMShapeLower 后端 Pass |
| `include/tvm/relax/exec_builder.h` | ExecBuilderNode：VM 字节码指令构建 API |

### Relax Pass 实现（src/relax/transform/）

该目录包含 60+ 个实现文件，核心 Pass 包括：

| 文件 | 职责 |
|------|------|
| `legalize_ops.cc` | LegalizeOps：调用算子 FLegalize 将高层算子替换为 call_tir |
| `fuse_ops.cc` | FuseOps：按 OpPatternKind 融合数据流块中的绑定 |
| `fuse_tir.cc` | FuseTIR：将 Relax 子函数融合为 TIR PrimFunc |
| `fold_constant.cc` | FoldConstant：常量折叠 |
| `dead_code_elimination.cc` | DeadCodeElimination：死代码消除 |
| `to_non_dataflow.cc` | ToNonDataflow：DataflowVar 提升为普通 Var |
| `call_tir_rewrite.cc` | CallTIRRewrite：为 call_tir 插入显式张量分配 |
| `static_plan_block_memory.cc` | StaticPlanBlockMemory：BindingBlock 级内存规划 |
| `to_mixed_precision.cc` | ToMixedPrecision：自动混合精度转换 |
| `gradient.cc` | Gradient：反向自动微分 |
| `convert_layout.cc` | ConvertLayout：布局转换 |
| `run_codegen.cc` | RunCodegen：外部代码生成触发 |
| `vmshape_lower.cc` | VMShapeLower：形状表达式降级 |
| `lower_runtime_builtin.cc` | LowerRuntimeBuiltin：内置函数降级 |

### Relax 外部后端（src/relax/backend/contrib/）

包含 11 个外部代码生成后端子目录：`clml/`、`codegen_c/`、`codegen_json/`、`cublas/`、`cudnn/`、`cutlass/`、`dnnl/`、`example_npu/`、`hipblas/`、`nnapi/`、`tensorrt/`。

### Relax 算子（src/relax/op/）

| 子目录 | 职责 |
|--------|------|
| `nn/` | 神经网络算子：attention、convolution、pooling |
| `tensor/` | 张量操作：binary、unary、create、linear_algebra、manipulate、statistical 等 16 个文件 |
| `vision/` | 视觉算子：nms、roi_align、roi_pool、multibox_transform_loc |
| `distributed/` | 分布式版本算子 |
| `ccl/` | 集合通信算子 |
| `image/` | 图像处理算子 |
| `memory/` | 内存视图算子 |

### TE 张量表达式

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/te/tensor.h` | Tensor/TensorNode、Tensor::Slice、operator() 索引 |
| `include/tvm/te/operation.h` | OperationNode 层次：PlaceholderOp/ComputeOp/ScanOp/ExternOp |
| `src/te/operation/create_primfunc.cc` | ProducerToBufferTransformer、CreateFuncInfo、TE→TIR 降级 |
| `python/tvm/te/operation.py` | Python 端 placeholder()/compute()/scan()/extern() |
| `python/tvm/te/__init__.py` | TE 命名空间导出 |

### TOPI 算子库

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/topi/tags.h` | 算子标签体系：kElementWise/kBroadcast/kCommReduce/kMatMul/kConv2dNCHW/kEinsum |
| `include/tvm/topi/broadcast.h` | TOPI_DEFINE_BCAST_OP 宏与广播算子 |
| `include/tvm/topi/nn/` | 神经网络算子头文件（softmax/dense/conv2d/pooling） |
| `python/tvm/topi/` | 138 个 Python 文件，涵盖各后端算子实现 |
