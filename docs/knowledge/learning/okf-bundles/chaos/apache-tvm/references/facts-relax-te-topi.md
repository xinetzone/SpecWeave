---
type: Facts
title: TVM Relax/TE/TOPI 事实清单
description: 从 TVM 源码采集的 Relax 图级 IR、TE 张量表达式、TOPI 算子库事实，每条标注文件路径与行号
tags: [tvm, relax, te, topi, facts, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
source_id: relax-te-topi
---

# TVM Relax/TE/TOPI 事实清单

> 源树根目录：`d:\AI\.chaos\libs\ffi\tvm\`
> 采集阶段：R 阶段事实采集
> 原则：零推测，每条事实标注文件路径与行号

---

## 1. Relax 核心 IR

### 1.1 表达式节点（expr.h）

1. `TupleNode` 继承自 `ExprNode`，包含 `tvm::ffi::Array<Expr> fields` 字段，类型键为 `"relax.expr.Tuple"`。include/tvm/relax/expr.h:39-50
2. `Tuple` 提供从 `ffi::Array<ExprType>` 到 `ffi::Array<Expr>` 的模板转换构造函数，支持派生类数组向基类数组的转换。include/tvm/relax/expr.h:52-81
3. `TupleGetItemNode` 包含 `Expr tuple` 和 `int index` 两个字段，用于从元组中提取指定索引的字段。include/tvm/relax/expr.h:83-98
4. `ShapeExprNode` 继承自 `ExprNode`，包含 `ffi::Array<PrimExpr> values` 字段，用于构造包含 PrimExpr 的形状表达式。include/tvm/relax/expr.h:114-126
5. `VarNode` 继承自 `ExprNode`，包含 `ffi::String name_hint` 字段；变量通过地址唯一标识，`name_hint` 仅作名称提示且在结构相等/哈希中被忽略。include/tvm/relax/expr.h:135-153
6. `VarNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindFreeVar`，`_type_child_slots` 为 1，预留一个子类槽位。include/tvm/relax/expr.h:150-151
7. `Var` 构造函数接受 `name_hint`、`ty_annotation` 和 `span` 三个参数。include/tvm/relax/expr.h:155-160
8. `DataflowVarNode` 继承自 `VarNode`，用于标记数据流变量，区别于普通的函数局部可见绑定。include/tvm/relax/expr.h:162-174
9. `DataflowVar` 继承自 `Var`，构造函数签名与 `Var` 一致。include/tvm/relax/expr.h:176-182
10. `ConstantNode` 包含 `runtime::Tensor data` 字段，提供 `tensor_type()` 方法返回对应张量类型，`is_scalar()` 方法判断是否为 0 维标量张量。include/tvm/relax/expr.h:189-205
11. `Constant` 构造函数接受 `data`、可选的 `ty_annotation` 和 `span`，若未指定类型注解则从 data 推断。include/tvm/relax/expr.h:207-221
12. `StringImmNode` 包含 `ffi::String value` 字段，表示字符串字面量常量。include/tvm/relax/expr.h:226-236
13. `DataTypeImmNode` 包含 `DLDataType value` 字段，表示数据类型常量。include/tvm/relax/expr.h:258-268
14. `BindingNode` 继承自 `ffi::Object`，包含 `mutable Span span` 和 `Var var` 字段，是所有变量绑定的基类。include/tvm/relax/expr.h:287-305
15. `BindingNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode`，`var` 字段使用递归式结构相等定义。include/tvm/relax/expr.h:298-302
16. `MatchCastNode` 继承自 `BindingNode`，包含 `Expr value` 和 `Type ty` 字段，执行运行时类型匹配并在首次出现时填充未定义的符号形状变量。include/tvm/relax/expr.h:323-345
17. `MatchCast` 构造函数接受 `var`、`value`、`ty` 和 `span` 参数。include/tvm/relax/expr.h:351-357
18. `VarBindingNode` 继承自 `BindingNode`，包含 `Expr value` 字段，并自定义了 `SEqual` 和 `SHash` 方法以提供更好的错误信息。include/tvm/relax/expr.h:359-377
19. `BindingBlockNode` 包含 `ffi::Array<Binding> bindings` 和 `mutable Span span` 字段，是绑定块的基类。include/tvm/relax/expr.h:386-401
20. `DataflowBlockNode` 继承自 `BindingBlockNode`，类型键为 `"relax.expr.DataflowBlock"`，表示数据流块。include/tvm/relax/expr.h:411-419
21. `SeqExprNode` 包含 `ffi::Array<BindingBlock> blocks` 和 `Expr body` 字段，块的顺序强制执行作用域和排序。include/tvm/relax/expr.h:428-463
22. `SeqExpr` 提供从 `Expr` 的隐式转换构造函数，若表达式已是 `SeqExpr` 则复用同一节点不做拷贝。include/tvm/relax/expr.h:465-483
23. `IfNode` 包含 `Expr cond`、`SeqExpr true_branch` 和 `SeqExpr false_branch` 三个字段，条件表达式求值为所取分支的结果。include/tvm/relax/expr.h:496-515
24. `If` 构造函数接受 `cond`、`true_branch`、`false_branch` 和 `span`，若分支不是 `SeqExpr` 则自动包装为 `SeqExpr`。include/tvm/relax/expr.h:517-540
25. `FunctionNode` 继承自 `BaseFuncNode`，包含 `params`、`body`、`ret_ty`、`is_pure` 四个核心字段。include/tvm/relax/expr.h:542-565
26. `Function` 构造函数接受 `params`、`body`、`ret_ty`、`is_pure`（默认 true）、`attrs` 和 `span`，body 若非 SeqExpr 会被自动包装。include/tvm/relax/expr.h:567-602
27. `Function::CreateEmpty` 静态方法用于创建无 body 的函数，此时 `ret_ty` 为必填项。include/tvm/relax/expr.h:597-598
28. 函数属性常量包括 `kPrimitive`（"Primitive"）、`kCodegen`（"Codegen"）、`kComposite`（"Composite"）、`kPartitionedFromPattern`、`kWorkspaceSize`、`kForcePure`、`kNumInput`。include/tvm/relax/expr.h:606-633
29. `kNumInput` 属性表示函数输入数量，最后 `params.size() - num_input` 个参数被视为跨调用固定的权重。include/tvm/relax/expr.h:628-632
30. `ExternFuncNode` 继承自 `BaseFuncNode`，包含 `ffi::String global_symbol` 字段，可表示 packed function。include/tvm/relax/expr.h:635-646
31. `ExternFunc` 提供两个构造函数：仅接受 `global_symbol`，或同时接受 `global_symbol` 和 `Type ty`。include/tvm/relax/expr.h:648-655
32. `GetShapeOf` 函数返回表达式的形状；要求表达式已归一化，若张量无编译时符号形状则返回 `Call(relax.op.shape_of, [expr])`。include/tvm/relax/expr.h:657-668
33. `tvm::relax::Var` 特化了 `std::hash` 和 `std::equal_to`，使用 `ObjectPtrHash`/`ObjectPtrEqual` 按引用相等，使其可作为 STL 容器的键。include/tvm/relax/expr.h:687-699

### 1.2 类型系统（type.h）

34. `kUnknownNDim` 常量值为 -1，表示张量维数在编译时未知。include/tvm/relax/type.h:47
35. `PackedFuncTypeNode` 继承自 `TypeNode`，类型键为 `"relax.PackedFuncType"`，表示 PackedFunc 类型。include/tvm/relax/type.h:52-59
36. `AnyTypeNode` 继承自 `TypeNode`，类型键为 `"relax.AnyType"`，表示任意 Relax 值。include/tvm/relax/type.h:95-102
37. `ObjectTypeNode` 和 `ObjectType` 是 `AnyTypeNode`/`AnyType` 的兼容性别名，新代码应使用 `AnyType`。include/tvm/relax/type.h:115-117
38. `ShapeTypeNode` 包含 `ffi::Optional<ffi::Array<PrimExpr>> values` 和 `int ndim`（默认 `kUnknownNDim`）字段，提供 `IsUnknownNdim()` 方法。include/tvm/relax/type.h:122-142
39. `ShapeType` 提供两个构造函数：接受已知符号形状值数组，或接受 ndim（可为 `kUnknownNDim`）。include/tvm/relax/type.h:148-164
40. `TensorTypeNode` 包含 `shape`（Optional<Expr>）、`vdevice`（Optional<VDevice>）、`dtype`（Optional<PrimType>）、`ndim`（默认 kUnknownNDim）四个字段。include/tvm/relax/type.h:169-187
41. `TensorTypeNode` 提供 `IsUnknownNdim()`、`IsUnknownDtype()` 和 `GetShape()` 方法；`GetShape()` 从 shape 表达式中提取 PrimExpr 数组。include/tvm/relax/type.h:188-200
42. 类型系统遵循"假设语义"（assume-semantics）：编译器尽力推导和检查，类型可被擦除为静态类型后仍可编译。include/tvm/relax/type.h:68-91

### 1.3 BlockBuilder（block_builder.h）

43. `BlockBuilderNode` 是虚接口类，提供三大类功能：全局上下文管理、作用域管理、归一化。include/tvm/relax/block_builder.h:36-64
44. 全局上下文管理方法包括 `name_supply()`、`GetContextIRModule()`、`Finalize()`、`AddFunction()`、`UpdateFunction()`。include/tvm/relax/block_builder.h:70-113
45. `Finalize()` 可能重命名 IRModule 中的 GlobalVar 以确保名称唯一性，并保证每个公开函数名与其 `global_symbol` 属性一致。include/tvm/relax/block_builder.h:86-96
46. 作用域管理方法包括 `BeginScope()`、`BeginInnerScope()`、`AddDefinitionToScope()`、`EndScope()`、`BeginDataflowBlock()`、`BeginBindingBlock()`、`EndBlock()`。include/tvm/relax/block_builder.h:126-183
47. `BeginScope()` 开启新作用域，父作用域的符号变量不可用；`BeginInnerScope()` 开启内部作用域，继承父作用域的可见参数。include/tvm/relax/block_builder.h:127-155
48. `LookupBinding()` 在当前已发射的序列中查找变量绑定值，对函数参数返回 `std::nullopt`。include/tvm/relax/block_builder.h:118-124
49. `Emit()` 发射一个 Expr 并返回绑定变量，会调用 `Normalize` 执行形状和类型推导。include/tvm/relax/block_builder.h:191-200
50. `EmitMatchCast()` 发射 MatchCast 绑定，`EmitOutput()` 为当前数据流块生成输出，`EmitNormalized()` 发射已归一化的绑定。include/tvm/relax/block_builder.h:202-226
51. `Normalize()` 将表达式转换为范式并尽力推导类型和形状；`NormalizeArgument()` 为 Call 等非叶子表达式创建绑定变量。include/tvm/relax/block_builder.h:228-245
52. `BlockBuilder::Create()` 静态方法创建 BlockBuilder，可传入可选的 `ctx_mod` 作为重写前的上下文模块。include/tvm/relax/block_builder.h:257-270
53. `DisableOperatorSpecificNormalizationForTVMScript` 标记结构体用于禁用 FNormalize，仅供 TVMScript 解析使用。include/tvm/relax/block_builder.h:295-297

### 1.4 算子属性类型（op_attr_types.h）

54. `OpPatternKind` 枚举定义了 7 种算子模式：`kElemWise`(0)、`kBroadcast`(1)、`kInjective`(2)、`kCommReduce`(3)、`kOutEWiseFusable`(4)、`kTuple`(7)、`kOpaque`(8)。include/tvm/relax/op_attr_types.h:35-55
55. `FCallPacked` 类型别名为 `ffi::String`，表示算子在代码生成时降级到的 packed function 实现。include/tvm/relax/op_attr_types.h:61
56. `FInferType` 是类型推导函数类型，签名为 `Type(const Call&, const BlockBuilder&)`。include/tvm/relax/op_attr_types.h:69
57. `FNormalize` 是归一化函数类型，作为 BlockBuilder 的一部分对每个表达式应用，用于将多种等价语法形式归一化为单一表示。include/tvm/relax/op_attr_types.h:91
58. `FValidate` 是验证函数类型，仅作为 well-formed 检查器的一部分运行，用于定义算子约束。include/tvm/relax/op_attr_types.h:110
59. `FLegalize` 是合法化函数类型，将 `relax::Call` 替换为更具体的实现（如 TIR 函数调用），结果表达式不得包含原始算子。include/tvm/relax/op_attr_types.h:126
60. `FLowerBuiltin` 是运行时内置函数降级函数类型，在 `LowerRuntimeBuiltin` pass 中使用。include/tvm/relax/op_attr_types.h:135
61. `FPrimalGradient` 是算子梯度函数类型，签名为 `Array<Expr>(const Var&, const Call&, const Var&, const BlockBuilder&)`。include/tvm/relax/op_attr_types.h:146-147

### 1.5 Dataflow Pattern（dataflow_pattern.h）

62. `DFPatternNode` 是所有数据流模式的基类，`_type_child_slots` 为 21，类型键为 `"relax.dpl.DFPattern"`。include/tvm/relax/dataflow_pattern.h:92-96
63. `DFPattern` 提供 `operator()` 创建 CallPattern、`operator|` 创建 OrPattern、`operator&` 创建 AndPattern、`operator~` 创建 NotPattern。include/tvm/relax/dataflow_pattern.h:104-114
64. `DFPattern` 提供 `HasAttr()`、`HasType()`、`HasDtype()`、`HasShape()`、`HasSameShapeAs()`、`dup()` 等约束方法。include/tvm/relax/dataflow_pattern.h:115-128
65. `UsedBy()` 函数在 lhs[-1] 和 rhs[0] 之间创建 used-by 关系，`operator^` 是其语法糖；`OnlyUsedBy()` 创建 only-used-by 关系，`operator>>` 是其语法糖。include/tvm/relax/dataflow_pattern.h:72-86
66. `PairCons` 结构体定义图级匹配中的边约束，包含 `kUsedBy` 和 `kOnlyUsedBy` 两种类型及 `index` 参数。include/tvm/relax/dataflow_pattern.h:136-156
67. `DFConstraintNode` 是图上额外约束的基类，提供 `GetDependentPatterns()` 和 `AsCondition()` 虚方法，返回 PrimExpr 条件及是否为充要条件的布尔值。include/tvm/relax/dataflow_pattern.h:165-200

### 1.6 Binding Rewrite（binding_rewrite.h）

68. `DataflowBlockRewriteNode` 提供 `ReplaceAllUses()`、`Add(Binding)`、`Add(var_name, expr)`、`Add(expr)`、`RemoveUnused()`、`RemoveAllUnused()` 等方法。include/tvm/relax/binding_rewrite.h:44-61
69. `DataflowBlockRewriteNode` 内部维护 `to_users_`（变量到使用者映射）、`fn_outputs_`（函数输出所需变量）和 `name_supply_`。include/tvm/relax/binding_rewrite.h:83-90
70. `DataflowBlockRewrite` 构造函数接受 `DataflowBlock dfb` 和 `Function root_fn`。include/tvm/relax/binding_rewrite.h:97-99

### 1.7 分析接口（analysis.h）

71. `CanProveShapeEqual()` 对两个符号形状数组或表达式进行尽力证明，返回 false 不代表运行时一定不等。include/tvm/relax/analysis.h:56-70
72. `GetStaticType()` 从给定类型获取对应静态类型；`TypeFromStaticType()` 从静态类型获取对应类型。include/tvm/relax/analysis.h:80-87
73. `DeriveCallRetType()` 从函数类型和调用表达式推导返回值类型，忽略 `call->op` 字段，仅依赖 `func_ty` 信息。include/tvm/relax/analysis.h:98-108
74. `EraseToWellDefined()` 将类型擦除为仅包含目标作用域中已定义变量的良定义类型，支持回调函数和 Map 两种参数形式。include/tvm/relax/analysis.h:165-198

---

## 2. Relax 算子

### 2.1 神经网络算子属性（attrs/nn.h）

75. `Conv1DAttrs` 包含 `strides`、`padding`、`dilation`、`groups`、`data_layout`、`kernel_layout`、`out_layout`、`out_dtype` 字段。include/tvm/relax/attrs/nn.h:33-74
76. `Conv2DAttrs` 字段与 Conv1D 相同，padding 支持一个整数（全边相同）、两个整数（上下/左右）或四个整数（上左下右）。include/tvm/relax/attrs/nn.h:77-120
77. `Conv3DAttrs` 字段与 Conv2D 相同，data_layout 支持 'NCDHW'、'NDHWC' 等，padding 为六个值。include/tvm/relax/attrs/nn.h:123-168
78. `Conv1DTransposeAttrs` 在 Conv1D 基础上增加 `output_padding` 字段，用于消除输出形状歧义。include/tvm/relax/attrs/nn.h:171-200

### 2.2 算子注册目录结构（src/relax/op/）

79. Relax 算子源码按子目录组织：`ccl/`（集合通信）、`distributed/`（分布式）、`image/`（图像处理）、`memory/`（内存视图）、`nn/`（神经网络）、`tensor/`（张量操作）、`vision/`（视觉算子）。src/relax/op/
80. `nn/` 子目录包含 `attention.cc`、`convolution.cc`、`nn.cc`、`pooling.cc` 四个实现文件及对应头文件。src/relax/op/nn/
81. `tensor/` 子目录包含 `binary.cc`、`create.cc`、`datatype.cc`、`grad.cc`、`index.cc`、`inspect.cc`、`linear_algebra.cc`、`manipulate.cc`、`qdq.cc`、`sampling.cc`、`search.cc`、`set.cc`、`sorting.cc`、`statistical.cc`、`ternary.cc`、`unary.cc` 等。src/relax/op/tensor/
82. `vision/` 子目录包含 `multibox_transform_loc.cc`、`nms.cc`、`roi_align.cc`、`roi_pool.cc`。src/relax/op/vision/
83. `distributed/` 子目录包含 `binary.cc`、`ccl.cc`、`linear_algebra.cc`、`manipulate.cc`、`nn.cc`、`statistical.cc`、`unary.cc` 等分布式版本算子。src/relax/op/distributed/
84. 算子公共注册入口为 `op.cc` 和 `op_common.cc`/`op_common.h`。src/relax/op/op.cc

### 2.3 Python 算子分类（python/tvm/relax/op/__init__.py）

85. 基础算子（base）包括 `call_tir`、`call_tir_inplace`、`call_pure_packed`、`call_dps_packed`、`call_tir_with_grad`、`call_py_func`、`shape_of`、`tensor_to_shape`、`shape_to_tensor`、`make_closure`、`invoke_closure`、`print`、`assert_op`、`to_vdevice`、`hint_on_device`、`null_value`、`register_gradient` 等。python/tvm/relax/op/__init__.py:25-47
86. 二元算子（binary）包括 `add`、`subtract`、`multiply`、`divide`、`floor_divide`、`floor_mod`、`mod`、`power`、`log_add_exp`、`equal`、`not_equal`、`greater`、`greater_equal`、`less`、`less_equal`、`logical_and`、`logical_or`、`logical_xor`、`bitwise_and`、`bitwise_or`、`bitwise_xor`、`left_shift`、`right_shift`、`maximum`、`minimum`、`atan2`。python/tvm/relax/op/__init__.py:48-75
87. 创建算子（create）包括 `arange`、`full`、`full_like`、`ones`、`ones_like`、`zeros`、`zeros_like`、`eye`、`eye_like`、`tril`、`triu`、`hamming_window`。python/tvm/relax/op/__init__.py:76-89
88. 数据类型算子包括 `astype`、`wrap_param`。python/tvm/relax/op/__init__.py:90
89. 索引算子包括 `strided_slice`、`dynamic_strided_slice`、`take`。python/tvm/relax/op/__init__.py:91
90. 线性代数算子包括 `einsum`、`matmul`、`linear`、`outer`。python/tvm/relax/op/__init__.py:92
91. 操作算子（manipulate）包括 `broadcast_to`、`concat`、`reshape`、`expand_dims`、`flatten`、`squeeze`、`permute_dims`、`split`、`stack`、`tile`、`repeat`、`gather_elements`、`gather_nd`、`scatter_elements`、`scatter_nd`、`one_hot`、`meshgrid`、`layout_transform`、`flip`、`reverse_sequence`、`slice_scatter`、`index_put`、`index_tensor`、`collapse_sum_like`、`collapse_sum_to`。python/tvm/relax/op/__init__.py:93-119
92. 量化反量化算子包括 `quantize`、`dequantize`。python/tvm/relax/op/__init__.py:121
93. 搜索算子包括 `argmax`、`argmin`、`where`、`bucketize`。python/tvm/relax/op/__init__.py:123
94. 集合算子包括 `nonzero`、`unique`。python/tvm/relax/op/__init__.py:124
95. 排序算子包括 `argsort`、`sort`、`topk`。python/tvm/relax/op/__init__.py:125
96. 统计算子包括 `sum`、`mean`、`variance`、`std`、`max`、`min`、`prod`、`cumsum`、`cumprod`、`median`。python/tvm/relax/op/__init__.py:126
97. 三元算子包括 `ewise_fma`（逐元素融合乘加）。python/tvm/relax/op/__init__.py:127
98. 一元算子包括 `abs`、`exp`、`sqrt`、`log`、`sin`、`cos`、`tan`、`sinh`、`cosh`、`tanh`、`sigmoid`、`erf`、`floor`、`ceil`、`round`、`trunc`、`negative`、`logical_not`、`bitwise_not`、`isnan`、`isfinite`、`isinf`、`acos`、`acosh`、`asin`、`asinh`、`atan`、`atanh`、`clip`、`rsqrt`、`sign`、`square`。python/tvm/relax/op/__init__.py:128-161
99. 视觉算子包括 `non_max_suppression`、`all_class_non_max_suppression`、`get_valid_counts`、`roi_align`、`roi_pool`、`multibox_transform_loc`。python/tvm/relax/op/__init__.py:162-169
100. Python 层为 Relax 表达式注册了运算符重载：`__add__`/`__radd__`、`__sub__`、`__mul__`、`__div__`、`__floordiv__`、`__mod__`、`__pow__`、`__neg__`、`__lt__`、`__le__`、`__gt__`、`__ge__`、`__getitem__`、`astype`、`__call__`。python/tvm/relax/op/__init__.py:196-237
101. `__add__` 特殊处理：若左操作数类型为 TupleType 且右操作数为 tuple，则执行元组拼接而非算子加法。python/tvm/relax/op/__init__.py:180-183

---

## 3. Relax 变换 Pass

### 3.1 Pass 基础设施（transform.h）

102. `CreateFunctionPass()` 创建函数级 Pass，接受 `pass_func`、`opt_level`、`name`、`required` 依赖列表和 `traceable` 标志。include/tvm/relax/transform.h:57-59
103. `CreateDataflowBlockPass()` 创建数据流块级 Pass，签名与 FunctionPass 类似但作用于 DataflowBlock。include/tvm/relax/transform.h:72-74

### 3.2 核心 Pass 清单（transform.h 声明）

104. `LambdaLift()`：将嵌套函数提升为全局函数。include/tvm/relax/transform.h:81
105. `ToNonDataflow()`：将所有数据流结构转换为非数据流版本。include/tvm/relax/transform.h:88
106. `RemovePurityChecking()`：激活所有纯函数的 force_pure 并解包 pure override ops，应在 ToNonDataflow 之后使用。include/tvm/relax/transform.h:101
107. `CallTIRRewrite()`：为 call_tir 和 call_dps_packed 执行显式张量分配。include/tvm/relax/transform.h:108
108. `RewriteDataflowReshape()`：将 reshape 类 call_tir 转换为 relax.reshape 算子调用，后续降级为运行时 CreateView，在 VM 构建第一阶段应用。include/tvm/relax/transform.h:122
109. `StaticPlanBlockMemory()`：BindingBlock 级静态内存规划 Pass，尽力复用已分配内存；支持通过 `tir_var_upper_bound`/`tir_var_lower_bound` 属性标注动态形状边界。include/tvm/relax/transform.h:145
110. `AttachGlobalSymbol()`：为 Relax 函数和 TIR PrimFunc 附加 global_symbol 以供代码生成。include/tvm/relax/transform.h:152
111. `Normalize()`：将 Relax IR 转换为范式，转为 A-norm 形式并填充表达式类型。include/tvm/relax/transform.h:160
112. `NormalizeGlobalVar()`：重命名 GlobalVar 以确保公开函数名与 global_symbol 属性一致，且所有 GlobalVar 名称在模块中唯一。include/tvm/relax/transform.h:169
113. `CanonicalizeBindings()`：折叠变量绑定和 match shape 节点及元组索引，简化 Relax 模块；若数据流变量仅在输出绑定中使用，会移除该中间变量。include/tvm/relax/transform.h:182
114. `EliminateCommonSubexpr()`：消除函数内公共子表达式，`call_only` 参数为 true 时仅消除 Call 节点。include/tvm/relax/transform.h:191
115. `BindParams()`：将函数参数绑定到常量张量。include/tvm/relax/transform.h:201
116. `BindSymbolicVars()`：将符号变量绑定到常量形状值，支持 `tirx.Var` 或字符串名称作为键。include/tvm/relax/transform.h:218
117. `FoldConstant()`：在数据流块内折叠常量表达式，可能需要先调用 ConvertToDataflow。include/tvm/relax/transform.h:228
118. `LegalizeOps()`：将高层算子调用合法化为 call_tir 及对应低层 TIR PrimFunc；每个算子的合法化函数注册为 `FLegalize` 属性；支持自定义映射 `cmap` 覆盖默认实现，`skip_ops` 指定跳过的算子。include/tvm/relax/transform.h:254-256
119. `RealizeVDevice()`：传播虚拟设备信息。include/tvm/relax/transform.h:262
120. `AttachAttrLayoutFreeBuffers()`：根据 Relax 函数中的使用情况为 tirx::PrimFunc 附加 layout free buffers（主要是模型权重和常量）。include/tvm/relax/transform.h:274
121. `SplitLayoutRewritePreproc()`：将布局重写预处理块拆分为独立的 tirx::PrimFunc，用于 meta_schedule 调优后的预打包权重。include/tvm/relax/transform.h:283
122. `LiftTransformParams()`：提升函数参数的变换到独立的 `transform_params` 函数；`shared_transform` 参数控制是否为多个函数生成共享的变换函数。include/tvm/relax/transform.h:311-312
123. `UpdateVDevice()`：更新虚拟设备，接受新 VDevice 和设备索引。include/tvm/relax/transform.h:320
124. `ExpandTupleArguments()`：展开内部函数的元组参数。include/tvm/relax/transform.h:326
125. `RemoveUnusedParameters()`：移除内部函数的未使用参数。include/tvm/relax/transform.h:332
126. `RemoveUnusedOutputs()`：移除内部函数的未使用输出。include/tvm/relax/transform.h:338
127. `AnnotateTIROpPattern()`：为 TIR 函数自动标注 Op Pattern Kind，供 FuseOps 使用；无法检测时标注为 "opaque"，用户也可手动标注 `op_pattern` 属性。include/tvm/relax/transform.h:347
128. `FuseOps()`：将数据流块中的绑定按融合算法分组为新的 Relax 函数，后续 FuseTIR Pass 为每个分组函数生成 TIR PrimFunc；`fuse_opt_level` 为 -1 时从 PassContext 推断。include/tvm/relax/transform.h:360
129. `FusionPatternNode` 包含 `name`、`pattern`（DFPattern）、`annotation_patterns`、`check`（可选验证函数）、`attrs_getter`（可选属性获取函数）。include/tvm/relax/transform.h:367-415
130. `PatternCheckContextNode` 包含 `matched_expr`、`annotated_expr`、`matched_bindings`、`var_usages`、`value_to_bound_var` 五个字段，作为 FusionPattern check 函数的输入。include/tvm/relax/transform.h:432-474
131. `Gradient()`：反向自动微分 Pass，为指定函数生成 `func_name + "_adjoint"` 函数；输入函数必须只有一个数据流块，目标必须是标量（0 维张量）。include/tvm/relax/transform.h:512-514
132. `FuseOpsByPattern()`：按提供的模式列表进行模式匹配并融合，模式顺序决定优先级；`annotate_codegen` 为 true 时为外部后端卸载包装代码生成属性。include/tvm/relax/transform.h:536-538
133. `MergeCompositeFunctions()`：将一个或多个 FuseOpsByPattern 创建的复合函数分组成新函数，标注 kCodegen 和 GlobalSymbol 属性，用于外部后端卸载。include/tvm/relax/transform.h:547
134. `FuseTIR()`：将 Relax 子函数融合为更大的 TIR 函数，与 FuseOps 协同执行算子融合。include/tvm/relax/transform.h:555
135. `RunCodegen()`：运行代码生成，接受 `target_options`（目标名到编译选项的映射）和 `entry_functions`。include/tvm/relax/transform.h:563-565
136. `DecomposeOpsForInference()`：推理时分解复合算子（如 BatchNorm 三元组、Attention、Erf 等）。include/tvm/relax/transform.h:575
137. `DecomposeOpsForTraining()`：训练时分解复合算子。include/tvm/relax/transform.h:585
138. `AlterOpImpl()`：根据 `op_impl_map` 替换 PrimFunc 实现，可在调用点插入布局变换。include/tvm/relax/transform.h:601-606
139. `ConvertLayout()`：布局转换 Pass，接受 `desired_layouts` 映射和 `layout_cb` 动态回调。include/tvm/relax/transform.h:615-616
140. `ConvertToDataflow()`：将 BindingBlock 中连续的数据流操作转换为 DataflowBlock，`min_size` 参数指定创建新数据流块所需的最小连续绑定数。include/tvm/relax/transform.h:625
141. `DeadCodeElimination()`：移除未使用的局部 VarBinding（绑定变量未使用且不使用非纯操作）和未使用的 Relax 函数（从入口函数检测调用链）。include/tvm/relax/transform.h:643
142. `DataflowUseInplaceCalls()`：将数据流块中可原地执行的算子（主要是逐元素操作）替换为 `call_tir_inplace` 调用。include/tvm/relax/transform.h:654
143. `ToMixedPrecision()`：自动混合精度 Pass，假设输入模块为 fp32，自动将特定算子转换为 fp16；`out_dtype` 指定 gemm/conv 的累加器类型。include/tvm/relax/transform.h:666-667
144. `RewriteCUDAGraph()`：重写 Relax 模块以使用 CUDA graph 执行，识别可使用 CUDA graph 的区域并提升为新函数供运行时图捕获。include/tvm/relax/transform.h:674
145. `SpecializePrimFuncBasedOnCallSite()`：根据 call_tir 信息更新 PrimFunc 的 var_buffer 映射，主要用于更新 VDevice 信息。include/tvm/relax/transform.h:681

### 3.3 Transform 实现文件清单（src/relax/transform/）

146. Transform 目录包含 60+ 个实现文件，涵盖：`adjust_matmul_order.cc`、`allocate_workspace.cc`、`alter_op_impl.cc`、`annotate_tir_op_pattern.cc`、`attach_attr_layout_free_buffers.cc`、`attach_global_symbol.cc`、`bind_params.cc`、`bind_symbolic_vars.cc`、`bundle_model_params.cc`、`call_tir_rewrite.cc`、`canonicalize_bindings.cc`、`combine_parallel_matmul.cc`、`compute_prim_value.cc`、`convert_dataflow.cc`、`convert_layout.cc`、`dataflow_inplace.cc`、`dead_code_elimination.cc`、`decompose_ops.cc`、`eliminate_common_subexpr.cc`、`expand_matmul_of_sum.cc`、`expand_tuple_arguments.cc`、`fold_constant.cc`、`fuse_ops.cc`、`fuse_tir.cc`、`gradient.cc`、`gradient_simplifier.cc`、`inline_functions.cc`、`kill_after_last_use.cc`、`lambda_lift.cc`、`lazy_transform_params.cc`、`legalize_ops.cc`、`lift_transform_params.cc`、`lower_alloc_tensor.cc`、`merge_composite_functions.cc`、`meta_schedule.cc`、`normalize.cc`、`realize_vdevice.cc`、`remove_purity_checking.cc`、`remove_unused_outputs.cc`、`remove_unused_parameters.cc`、`reorder_permute_dims_after_concat.cc`、`reorder_take_after_matmul.cc`、`rewrite_cuda_graph.cc`、`rewrite_dataflow_reshape.cc`、`run_codegen.cc`、`specialize_primfunc_based_on_callsite.cc`、`split_call_tir_by_pattern.cc`、`split_layout_rewrite_preproc.cc`、`static_plan_block_memory.cc`、`to_mixed_precision.cc`、`to_non_dataflow.cc`、`topological_sort.cc`、`update_param_type.cc`、`update_vdevice.cc`、`utils.cc`。src/relax/transform/

### 3.4 预定义 Pipeline（python/tvm/relax/pipeline.py）

147. `zero_pipeline()` 按顺序应用：`LegalizeOps` → `AnnotateTIROpPattern` → `FoldConstant` → `FuseOps` → `FuseTIR`；若存在 MetaSchedule Database 则追加 `MetaScheduleApplyDatabase`。python/tvm/relax/pipeline.py:63-75
148. `default_build_pipeline()` 是 `tvm.compile` 使用的默认编译流水线，按顺序应用 13 个 Pass：DispatchSampling、DispatchSortScan、LegalizeOps、RewriteDataflowReshape、ToNonDataflow、RemovePurityChecking、CallTIRRewrite、StaticPlanBlockMemory、RewriteCUDAGraph、LowerAllocTensor、KillAfterLastUse、LowerRuntimeBuiltin、ComputePrimValue、VMShapeLower、AttachGlobalSymbol。python/tvm/relax/pipeline.py:85-103
149. `static_shape_tuning_pipeline()` 用于静态形状模型调优，接受 `total_trials`、`target`、`work_dir`、`cpu_weight_prepack`、`max_trials_per_task` 参数。python/tvm/relax/pipeline.py:110-150

---

## 4. Relax 后端与代码生成

### 4.1 后端 Pass（backend.h）

150. `LowerRuntimeBuiltin()`：执行内置函数降级，将大多数算子映射到 VM 内置函数。include/tvm/relax/backend.h:38
151. `VMShapeLower()`：将 Relax 中的形状表达式降级为 VM 形状堆和 TIR 函数。include/tvm/relax/backend.h:45

### 4.2 VM ExecBuilder（exec_builder.h）

152. `ExecBuilderNode` 提供构建 VM 可执行指令的 API，内部持有 `vm::VMExecutable` 和常量去重映射 `const_dedup_map_`。include/tvm/relax/exec_builder.h:49-184
153. `DeclareFunction()` 声明一个函数，允许多次声明；`EmitFunction()` 标注 VM 函数开始，接受函数名、输入数、参数名、函数种类（默认 kVMFunc）和初始寄存器大小。include/tvm/relax/exec_builder.h:56-68
154. `EndFunction()` 标注 VM 函数结束。include/tvm/relax/exec_builder.h:73
155. `EmitCall()` 有两个重载：通过函数名或函数索引发射 packed function 调用指令，接受参数列表和返回寄存器。include/tvm/relax/exec_builder.h:80-87
156. `EmitRet()` 发射返回指令，结果必须是寄存器；`EmitGoto()` 发射跳转指令；`EmitIf()` 发射条件分支指令。include/tvm/relax/exec_builder.h:93-105
157. `GetFunction()` 通过名称获取函数索引参数；`ConvertConstant()` 模板方法将常量值转换为 ExecBuilder 可理解的参数，可能更新常量池。include/tvm/relax/exec_builder.h:111-125
158. `SaveMemoryScope()` 为常量构建内存作用域；`exec()` 返回底层可执行文件的原始指针；`Get()` 完成构建、运行 formalize 并返回最终结果。include/tvm/relax/exec_builder.h:134-143
159. `ExecBuilder::Create()` 静态工厂方法创建 ExecBuilder 实例。include/tvm/relax/exec_builder.h:148
160. ExecBuilder 内部有 `CheckExecutable()` 检查寄存器使用是否合法，`Formalize()` 完成可执行文件的形式化。include/tvm/relax/exec_builder.h:173-177

### 4.3 外部代码生成后端（src/relax/backend/contrib/）

161. Relax 外部后端目录包含以下子目录：`clml/`、`codegen_c/`、`codegen_json/`、`cublas/`、`cudnn/`、`cutlass/`、`dnnl/`、`example_npu/`、`hipblas/`、`nnapi/`、`tensorrt/`。src/relax/backend/contrib/
162. 每个后端子目录包含一个 `codegen.cc` 文件实现代码生成逻辑；公共工具位于 `utils.cc`/`utils.h`。src/relax/backend/contrib/
163. `codegen_c/` 子目录包含 `codegen_c.h` 头文件；`codegen_json/` 子目录包含 `codegen_json.h` 头文件。src/relax/backend/contrib/codegen_c/

---

## 5. TE 张量表达式

### 5.1 Tensor 与 Operation（tensor.h）

164. `Operation` 类继承自 `ffi::ObjectRef`，提供 `output(size_t i)` 方法获取第 i 个输出张量。include/tvm/te/tensor.h:48-67
165. `TensorNode` 继承自 `DataProducerNode`，包含 `shape`（Array<PrimExpr>）、`dtype`（PrimType，默认 Void）、`op`（Operation）、`value_index`（int，默认 0）四个字段。include/tvm/te/tensor.h:69-94
166. `TensorNode` 实现 `GetShape()`、`GetDataType()`、`ToPrimExpr()`、`GetNameHint()` 方法，类型键为 `"te.Tensor"`。include/tvm/te/tensor.h:83-93
167. `Tensor` 类提供 `operator()` 模板方法，接受可变参数索引返回 `PrimExpr` 表示张量读取。include/tvm/te/tensor.h:131-135
168. `Tensor` 提供两个 `operator()` 重载，分别接受 `Array<PrimExpr>` 和 `Array<PrimVar>` 索引。include/tvm/te/tensor.h:141-147
169. `IndexWithNegativeIndices()` 方法支持负索引，提供与 `operator()` 对应的三个重载。include/tvm/te/tensor.h:153-169
170. `Tensor::Slice` 内部类表示固定前 k 个坐标的切片，支持 `Tensor[x][y][z]` 语法糖，通过 `operator PrimExpr()` 转换为表达式。include/tvm/te/tensor.h:175-200
171. `Tensor::operator[]` 返回 Slice 对象，支持链式索引。include/tvm/te/tensor.h:206
172. `Tensor::ndim()` 内联方法返回 `shape.size()`。include/tvm/te/tensor.h:212
173. `Tensor::operator==` 先比较指针，再比较 `op` 和 `value_index`；若两个 tensor 的 op 都未定义则返回 false。include/tvm/te/tensor.h:214-224
174. Slice 支持一元运算符 `!`、`-` 和二元运算符 `+`、`-`、`*`、`==`、`<=`、`>=` 的重载，通过 `DEFINE_OVERLOAD_SLICE_UNARY_OP`/`DEFINE_OVERLOAD_SLICE_BINARY_OP` 宏定义。include/tvm/te/tensor.h:227-250

### 5.2 Operation 层级（operation.h）

175. `TensorDom` 结构体存储张量各轴边界的并集，包含 `std::vector<std::vector<IntSet>> data`。include/tvm/te/operation.h:48-53
176. `OperationNode` 是所有操作节点的抽象基类，包含 `name`、`tag`、`attrs` 字段，纯虚方法包括 `num_outputs()`、`output_dtype()`、`output_shape()`、`InputTensors()`。include/tvm/te/operation.h:58-96
177. `PlaceholderOpNode` 继承自 `OperationNode`，包含 `shape` 和 `dtype` 字段，表示输入占位符。include/tvm/te/operation.h:101-120
178. `PlaceholderOp` 构造函数接受 `name`、`shape`、`dtype` 三个参数。include/tvm/te/operation.h:126-131
179. `BaseComputeOpNode` 继承自 `OperationNode`，包含 `axis`（Array<IterVar>）和 `reduce_axis`（Array<IterVar>）字段，是 ComputeOp 的基类。include/tvm/te/operation.h:137-153
180. `ComputeOpNode` 继承自 `BaseComputeOpNode`，包含 `body`（Array<PrimExpr>）字段，表示在特定域上逐标量计算的张量操作。include/tvm/te/operation.h:158-174
181. `ComputeOp` 构造函数接受 `name`、`tag`、`attrs`、`axis`、`body` 参数。include/tvm/te/operation.h:180-187
182. `ScanOpNode` 继承自 `OperationNode`，包含 `scan_axis`、`init`、`update`、`state_placeholder`、`inputs`、`spatial_axis_` 字段，表示符号扫描操作。include/tvm/te/operation.h:192-236
183. `ScanOp` 构造函数接受 `name`、`tag`、`attrs`、`axis`、`init`、`update`、`state_placeholder`、`input` 参数。include/tvm/te/operation.h:242-250
184. `ExternOpNode` 继承自 `OperationNode`，包含 `inputs`、`input_placeholders`、`output_placeholders`、`body`（Stmt）字段，表示不可分割的外部计算。include/tvm/te/operation.h:255-283
185. `ExternOp` 构造函数接受 `name`、`tag`、`attrs`、`inputs`、`input_placeholders`、`output_placeholders`、`body` 参数。include/tvm/te/operation.h:289-296

### 5.3 TE→TIR Lowering（create_primfunc.cc）

186. `ProducerToBufferTransformer` 继承自 `StmtExprMutator`，将 `ProducerLoad` 转换为 `BufferLoad`，通过 `tensor2buffers_` 映射查找对应 Buffer。src/te/operation/create_primfunc.cc:48-65
187. `BufferSubstituter` 继承自 `StmtExprMutator`，根据 `var_map_` 和 `buffer_map_` 重写 buffer 和 buffer 变量访问。src/te/operation/create_primfunc.cc:68-103
188. `CreateFuncInfo` 结构体存储 `arg_list`（Tensor 数组）、`tensor2buffers`（Tensor 到 Buffer 映射）、`transformer`、`root_alloc`（根分配 Buffer 数组）、`name_supply`。src/te/operation/create_primfunc.cc:106-127
189. `LayoutFreePlaceholdersNormalizer` 继承自 `StmtMutator`，处理 layout free placeholder，为函数附加 `layout_free_buffers` 属性（索引列表）。src/te/operation/create_primfunc.cc:129-150

### 5.4 Python TE 绑定（python/tvm/te/）

190. Python `placeholder()` 函数默认 dtype 为 "float32"，调用 `_ffi_api.Placeholder` 创建占位张量。python/tvm/te/operation.py:37-57
191. Python `compute()` 函数接受 `shape`、`fcompute`、`name`、`tag`、`attrs`、`varargs_names`；通过 `inspect.getfullargspec` 解析 fcompute 参数，自动为每个维度创建 IterVar，单输出返回 Tensor，多输出返回 Tensor 元组。python/tvm/te/operation.py:60-140
192. Python `scan()` 函数接受 `init`、`update`、`state_placeholder`、`inputs`、`name`、`tag`、`attrs`；init/update/state_placeholder/inputs 可为单个 Tensor 或列表，内部自动转换为列表。python/tvm/te/operation.py:143-200
193. `te` 命名空间导出 `placeholder`、`compute`、`scan`、`extern`、`var`、`const`、`thread_axis`、`reduce_axis`、`AXIS_SEPARATOR`、`create_prim_func`、`extern_primfunc`、`Tensor`、`TensorSlice`、`PlaceholderOp`、`ComputeOp`、`ScanOp`、`ExternOp` 及所有 TIR 内建函数。python/tvm/te/__init__.py:22-37
194. `te` 命名空间从 `tvm.tirx` 重新导出数学函数（exp、erf、tanh、sigmoid、log、sqrt 等）、归约器（min、max、sum、comm_reducer）和条件表达式（if_then_else）。python/tvm/te/__init__.py:22-29

---

## 6. TOPI 算子库

### 6.1 标签体系（tags.h）

195. TOPI 定义了 14 个算子标签常量：`kElementWise`("elemwise")、`kInjective`("injective")、`kCommReduce`("comm_reduce")、`kCommReduceIdx`("comm_reduce_idx")、`kBroadcast`("broadcast")、`kMatMul`("matmul")、`kConv2dNCHW`、`kConv2dHWCN`、`kDepthwiseConv2dNCHW`、`kDepthwiseConv2dNHWC`、`kDepthwiseConv2dBackInputNHWC`、`kDepthwiseConv2dBackWeightNHWC`、`kEinsum`("einsum")、`kGroupConv2d`。include/tvm/topi/tags.h:32-45
196. `is_broadcast()` 判断标签是否以 "elemwise" 或 "broadcast" 开头；`is_injective()` 判断是否以 "elemwise"、"broadcast" 或 "injective" 开头。include/tvm/topi/tags.h:47-54

### 6.2 广播算子（broadcast.h）

197. `broadcast_to()` 将张量按 numpy 规则广播到目标形状，要求输出维度数不小于输入维度数，使用 `detail::BroadcastShape` 计算公共形状。include/tvm/topi/broadcast.h:48-70
198. `TOPI_DEFINE_BCAST_OP` 宏为二元算子生成三个重载：Tensor-Tensor（自动广播，tag=kBroadcast）、Tensor-PrimExpr（tag=kElementWise）、PrimExpr-Tensor（tag=kElementWise）。include/tvm/topi/broadcast.h:72-92
199. `TOPI_DEFINE_OP_OVERLOAD` 宏为 C++ 运算符生成重载，委托给对应的 topi 函数。include/tvm/topi/broadcast.h:94-103
200. 通过宏定义的广播逻辑算子包括 `logical_and`、`logical_or`、`logical_xor`、`bitwise_and`、`bitwise_or`、`bitwise_xor`，并为 `&&`、`||`、`&`、`|`、`^` 注册了运算符重载。include/tvm/topi/broadcast.h:116-186
201. `add` 算子通过 `TOPI_DEFINE_BCAST_OP(add, { return a + b; })` 定义，并为 `operator+` 注册重载。include/tvm/topi/broadcast.h:199-200

### 6.3 逐元素算子（elemwise.h）

202. `TOPI_DECLARE_UNARY_OP` 宏为一元内建算子生成 Tensor 版本，使用 `compute` 在输入形状上逐元素应用 `::tvm::OpName`，tag 默认为 `kElementWise`。include/tvm/topi/elemwise.h:43-48
203. 通过宏声明的一元算子包括 27 个：`exp`、`erf`、`sigmoid`、`sqrt`、`log`、`log2`、`log10`、`floor`、`ceil`、`round`、`trunc`、`abs`、`cos`、`cosh`、`tan`、`sin`、`sinh`、`acos`、`acosh`、`asin`、`asinh`、`atan`、`atanh`、`isnan`、`tanh`、`isfinite`、`isinf`。include/tvm/topi/elemwise.h:50-76
204. `fast_tanh_float()` 使用 Eigen 的 Padé 近似实现快速 tanh，将输入裁剪到 [-9, 9] 范围，使用分子（奇次多项式）和分母（偶次多项式）系数计算。include/tvm/topi/elemwise.h:82-121
205. `fast_tanh()` 对 float32 输入使用 `fast_tanh_float` 实现，其他类型回退到默认的 `::tvm::tanh`。include/tvm/topi/elemwise.h:132-142
206. `identity()` 返回输入张量的恒等映射；`negative()` 返回逐元素取负；`logical_not()` 返回逐元素逻辑非；`bitwise_not()` 返回逐元素按位取反。include/tvm/topi/elemwise.h:153-198

### 6.4 归约算子（reduction.h）

207. `FReduce` 类型别名表示归约函数类型：`PrimExpr(PrimExpr source, const Array<IterVar>& axis, Array<PrimExpr> init, Span span)`。include/tvm/topi/reduction.h:46-47
208. `GetRealAxis()` 将可能为空或含负数的归约轴转换为有效维度索引数组：空轴表示所有维度，负索引从最后一维偏移，结果排序并去重。include/tvm/topi/reduction.h:65-86
209. `MakeReduceAxes()` 为每个真实归约轴创建名为 "k{i}" 的 `reduce_axis`，范围为 `[0, data->shape[i])`。include/tvm/topi/reduction.h:89-96
210. `MakeReduceTargetShape()` 计算归约输出形状：keepdims 时归约轴保留为 size 1，否则移除归约轴；atleast1d 时空结果追加维度 1。include/tvm/topi/reduction.h:99-125
211. `DoCommReduce()` 执行实际的交换归约计算，通过索引映射将输出索引和归约索引组合为输入索引，tag 为 `kCommReduce`。include/tvm/topi/reduction.h:140-169
212. `CommReduce()` 是归约的高层封装，对 0 维输入特殊处理（identity + 可选 expand_dims），否则调用 GetRealAxis、MakeReduceTargetShape、DoCommReduce。include/tvm/topi/reduction.h:184-195

### 6.5 神经网络算子（nn.h, nn/）

213. `relu()` 实现 `max(t(i), threshold)`，threshold 默认为 0，支持模板参数类型。include/tvm/topi/nn.h:54-64
214. `leaky_relu()` 实现 `Select(value > 0, value, value * alpha)`，alpha 默认为 0.1。include/tvm/topi/nn.h:76-87
215. `prelu()` 实现参数化 ReLU，slope 按通道应用，axis 参数指定通道维度，要求 slope 的第一个维度与输入通道数匹配。include/tvm/topi/nn.h:100-115
216. `pad()` 支持三种填充模式："constant"（常量填充）、"edge"（边缘值填充）、"reflect"（反射填充）；pad_after 为空时使用对称填充；输出形状通过算术分析器简化。include/tvm/topi/nn.h:156-200
217. `PoolType` 枚举定义 `kAvgPool` 和 `kMaxPool` 两种池化类型。include/tvm/topi/nn/pooling.h:44-47
218. `pool_grad_impl()` 实现池化梯度，要求 kernel_size 和 stride_size 各有 2 个元素，padding_size 有 4 个元素（上左下右）；ceil_mode 时追加 stride-1 的额外填充。include/tvm/topi/nn/pooling.h:49-149
219. `dense()` 计算 `data * weight^T + bias`，data 形状 [batch, in_dim]，weight 形状 [out_dim, in_dim]，bias 形状 [out_dim]（可选）；使用归约轴 k 执行矩阵乘，tag 为 "dense"。include/tvm/topi/nn/dense.h:48-76
220. `softmax()` 通过四步计算：max 归约（数值稳定性）→ exp(x-max) → sum 归约 → 归一化，axis 默认为 -1（最后一维），tag 为 "softmax_output"。include/tvm/topi/nn/softmax.h:50-120
221. `log_softmax()` 要求 2-D 输入，计算 `x - max - log(sum(exp(x-max)))`，tag 为 "log_softmax_output"。include/tvm/topi/nn/softmax.h:131-149

### 6.6 变换算子（transform.h）

222. `sliding_window()` 在输入张量上滑动窗口，axis 决定窗口起始维度，窗口形状和步长长度均为 `data.ndim - axis`；输出形状由前置维度 + 窗口数量维度 + 窗口内容维度组成。include/tvm/topi/transform.h:76-142

### 6.7 Einsum（einsum.h）

223. `InferEinsumShape()` 根据 einsum 下标字符串和操作数形状推断输出形状。include/tvm/topi/einsum.h:58-59
224. `einsum()` 实现爱因斯坦求和约定，接受下标字符串和输入张量数组，tag 默认为 `kEinsum`。include/tvm/topi/einsum.h:72-73
225. `EinsumEquation` 结构体包含 `inputs`（每个操作数的下标向量）和 `output`（输出下标），`kEllipsis` 标签值为 '\0'；`FromString()` 静态方法从字符串解析方程并转换为显式模式。include/tvm/topi/einsum.h:75-91
226. Einsum 定义了 `LABELRANGE`(128)、`NPY_MAXDIMS`(16)、`NPY_MAXARGS`(16) 三个常量。include/tvm/topi/einsum.h:27-29

### 6.8 Python TOPI 绑定（python/tvm/topi/__init__.py）

227. TOPI Python 包先导入 C++ schedule（`.cpp`），再导入 Python 模块以允许 Python 覆盖 C++ 实现。python/tvm/topi/__init__.py:31-33
228. TOPI 导出模块包括 `math`、`tensor`、`index_put`、`reduction`、`transform`、`broadcast`、`sort`、`scatter`、`scatter_elements`、`slice_scatter`、`sparse_reshape`、`scan`、`einsum`、`unique`、`searchsorted`、`signal`，以及子包 `nn`、`utils`、`image`、`vision`、`gpu`。python/tvm/topi/__init__.py:35-56
229. TOPI 导出 `InvalidShapeError` 异常类用于错误报告。python/tvm/topi/__init__.py:59

---

## 7. Python 绑定

### 7.1 Relax 顶层命名空间（python/tvm/relax/__init__.py）

230. Relax Python 命名空间导出表达式类：`Expr`、`Span`、`GlobalVar`、`Var`、`DataflowVar`、`Binding`、`MatchCast`、`VarBinding`、`BindingBlock`、`DataflowBlock`、`SeqExpr`、`ShapeExpr`、`Tuple`、`TupleGetItem`、`Function`、`ExternFunc`、`If`、`Constant`、`DataTypeImm`、`StringImm`、`prim_value`。python/tvm/relax/__init__.py:26-48
231. 导出辅助函数 `const`、`extern`、`get_shape_of`。python/tvm/relax/__init__.py:50
232. 导出类型类：`Type`、`AnyType`、`ObjectType`、`ShapeType`、`TensorType`、`TupleType`、`FuncType`、`PackedFuncType`。python/tvm/relax/__init__.py:53-62
233. 导出 `ExecBuilder`、`BlockBuilder`、`ExprFunctor`、`PyExprVisitor`、`PyExprMutator`、`DataflowBlockRewrite`、`BasePyModule`。python/tvm/relax/__init__.py:65-111
234. 导出 pipeline 函数：`get_default_pipeline`、`get_pipeline`、`register_pipeline`。python/tvm/relax/__init__.py:83-85
235. 导出 VM 构建函数 `build` 和 `VMExecutable` 类。python/tvm/relax/__init__.py:109
236. 导入子模块：`exec_builder`、`expr`、`ty`、`type`、`analysis`、`transform`、`block_builder`、`op`、`backend`、`training`、`distributed`、`frontend`、`utils`。python/tvm/relax/__init__.py:94-106
237. 通过 `tvm.script.register_dialect("relax", "tvm.relax.script")` 注册 Relax 为 TVMScript 方言。python/tvm/relax/__init__.py:113-115

### 7.2 Relax 表达式 Python 层（python/tvm/relax/expr.py）

238. `prim_value()` 函数将 Python 标量或原始表达式转换为 `Expr`：bool 转为 IntImm("bool")，整数转为 IntImm("int64")，浮点数转为 FloatImm("float64")，已有 Expr 原样返回。python/tvm/relax/expr.py:46-74
239. `Type.is_base_of` 方法通过 monkey-patching 添加，委托给 `_ffi_api.TypeIsBaseOf`。python/tvm/relax/expr.py:77-83
240. `_binary_op_helper()` 要求左操作数为 Expr，右操作数若为 Number 则提示先用 `const` 转换，不支持其他类型。python/tvm/relax/expr.py:90-99

### 7.3 Relax BlockBuilder Python 层（python/tvm/relax/block_builder.py）

241. `FunctionScope` 是函数构建的辅助上下文管理器，在 `__enter__` 中进入函数作用域，`__exit__` 中退出，内部维护 `_blocks` 列表和 `_is_emit_func_output_called` 标志。python/tvm/relax/block_builder.py:39-61
242. `DataflowScope` 是数据流块构建的辅助上下文管理器，进入时结束当前块并开始 DataflowBlock，退出时结束 DataflowBlock 并开始新的 BindingBlock。python/tvm/relax/block_builder.py:64-80
243. `TestingScope` 用于测试，接受 tirx.Var 列表作为 def_vars，内部创建 dummy ShapeType 参数使形状变量进入作用域。python/tvm/relax/block_builder.py:83-104
244. Python `BlockBuilder` 类注册为 `"relax.BlockBuilder"`，支持 `function()`、`dataflow()`、`emit()`、`emit_output()`、`emit_func_output()` 等方法，可用于构建 Relax IR 和神经网络。python/tvm/relax/block_builder.py:107-150

---

## 附录：事实统计

| 章节 | 事实数量 |
|------|----------|
| 1. Relax 核心 IR | 74 |
| 2. Relax 算子 | 27 |
| 3. Relax 变换 Pass | 48 |
| 4. Relax 后端与代码生成 | 14 |
| 5. TE 张量表达式 | 31 |
| 6. TOPI 算子库 | 35 |
| 7. Python 绑定 | 15 |
| **合计** | **244** |
