---
type: Concept
title: Relax 算子体系
description: Relax 算子分类体系、Attrs 属性系统、FNormalize/FLegalize/FPrimalGradient 算子属性函数、OpPatternKind 融合模式及 PatternRegistry
tags: [tvm, relax, operator, nn, tensor, attrs, legalize, pattern, fusion]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# Relax 算子体系

Relax 提供了一套完整的算子（Operator）体系，覆盖神经网络计算、张量操作、视觉处理、分布式通信等领域。每个算子不仅是一个函数调用，还携带丰富的属性信息，包括类型推导规则、归一化规则、合法化规则和融合模式，使编译器能够对算子进行深入分析和优化。Relax 算子体系定义于 `include/tvm/relax/op_attr_types.h` 和 `src/relax/op/` 目录。

## 算子分类

Relax 算子源码按子目录组织，每个子目录对应一个算子域 [F-79]：

| 子目录 | 职责 |
|--------|------|
| `nn/` | 神经网络算子：卷积、池化、注意力等 |
| `tensor/` | 张量操作：二元/一元/创建/索引/线性代数/变换/统计/搜索/排序等 |
| `vision/` | 视觉算子：NMS、ROI Align、ROI Pool 等 |
| `image/` | 图像处理算子 |
| `memory/` | 内存视图算子 |
| `ccl/` | 集合通信算子 |
| `distributed/` | 分布式版本算子 |

### 神经网络算子（nn）

`nn/` 子目录包含 `attention.cc`、`convolution.cc`、`nn.cc`、`pooling.cc` 四个实现文件 [F-80]。核心算子属性类型定义于 `include/tvm/relax/attrs/nn.h`：

- **Conv1DAttrs / Conv2DAttrs / Conv3DAttrs**：卷积属性，包含 `strides`、`padding`、`dilation`、`groups`、`data_layout`、`kernel_layout`、`out_layout`、`out_dtype` 字段 [F-75][F-76][F-77]。Conv2D 的 padding 支持一个整数（全边相同）、两个整数（上下/左右）或四个整数（上左下右）。
- **Conv1DTransposeAttrs**：转置卷积属性，在 Conv1D 基础上增加 `output_padding` 字段用于消除输出形状歧义 [F-78]。

除卷积外，nn 模块还包括 pooling、attention、batch_norm、layer_norm、dropout 等深度学习常用算子。

### 张量算子（tensor）

`tensor/` 子目录包含 16 个实现文件 [F-81]，是 Relax 算子数量最多的类别。Python 层将其细分为以下子类：

**基础算子（base）**[F-85]：`call_tir`、`call_tir_inplace`、`call_pure_packed`、`call_dps_packed`、`call_tir_with_grad`、`call_py_func`、`shape_of`、`tensor_to_shape`、`shape_to_tensor`、`make_closure`、`invoke_closure`、`print`、`assert_op`、`to_vdevice`、`hint_on_device`、`null_value`、`register_gradient`。

**二元算子（binary）**[F-86]：`add`、`subtract`、`multiply`、`divide`、`floor_divide`、`floor_mod`、`mod`、`power`、`log_add_exp`、`equal`、`not_equal`、`greater`、`greater_equal`、`less`、`less_equal`、`logical_and`、`logical_or`、`logical_xor`、`bitwise_and`、`bitwise_or`、`bitwise_xor`、`left_shift`、`right_shift`、`maximum`、`minimum`、`atan2`，共 26 个。

**创建算子（create）**[F-87]：`arange`、`full`、`full_like`、`ones`、`ones_like`、`zeros`、`zeros_like`、`eye`、`eye_like`、`tril`、`triu`、`hamming_window`。

**一元算子（unary）**[F-98]：`abs`、`exp`、`sqrt`、`log`、`sin`、`cos`、`tan`、`sinh`、`cosh`、`tanh`、`sigmoid`、`erf`、`floor`、`ceil`、`round`、`trunc`、`negative`、`logical_not`、`bitwise_not`、`isnan`、`isfinite`、`isinf`、`acos`、`acosh`、`asin`、`asinh`、`atan`、`atanh`、`clip`、`rsqrt`、`sign`、`square`，共 32 个。

**其他张量子类**：
- 索引算子：`strided_slice`、`dynamic_strided_slice`、`take` [F-89]
- 线性代数：`einsum`、`matmul`、`linear`、`outer` [F-90]
- 操作/变换：`broadcast_to`、`concat`、`reshape`、`expand_dims`、`flatten`、`squeeze`、`permute_dims`、`split`、`stack`、`tile`、`repeat`、`gather_elements`、`gather_nd`、`scatter_elements`、`scatter_nd`、`one_hot`、`meshgrid`、`layout_transform`、`flip`、`reverse_sequence`、`slice_scatter`、`index_put`、`index_tensor`、`collapse_sum_like`、`collapse_sum_to` [F-91]
- 统计算子：`sum`、`mean`、`variance`、`std`、`max`、`min`、`prod`、`cumsum`、`cumprod`、`median` [F-96]
- 搜索：`argmax`、`argmin`、`where`、`bucketize` [F-93]
- 排序：`argsort`、`sort`、`topk` [F-95]
- 数据类型：`astype`、`wrap_param` [F-88]
- 量化反量化：`quantize`、`dequantize` [F-92]
- 集合：`nonzero`、`unique` [F-94]
- 三元：`ewise_fma`（逐元素融合乘加）[F-97]

### 视觉算子（vision）

`vision/` 子目录包含 `multibox_transform_loc.cc`、`nms.cc`、`roi_align.cc`、`roi_pool.cc` [F-82]。Python 层导出的视觉算子包括 `non_max_suppression`、`all_class_non_max_suppression`、`get_valid_counts`、`roi_align`、`roi_pool`、`multibox_transform_loc` [F-99]。这些算子主要用于目标检测和图像分割模型的后处理。

### 分布式算子（distributed）

`distributed/` 子目录包含 `binary.cc`、`ccl.cc`、`linear_algebra.cc`、`manipulate.cc`、`nn.cc`、`statistical.cc`、`unary.cc` 等分布式版本算子 [F-83]，支持多设备张量并行计算。

### Python 运算符重载

Python 层为 Relax 表达式注册了丰富的运算符重载 [F-100]，使张量计算可以用自然的数学语法表达：
- 算术：`__add__`/`__radd__`、`__sub__`、`__mul__`、`__div__`、`__floordiv__`、`__mod__`、`__pow__`、`__neg__`
- 比较：`__lt__`、`__le__`、`__gt__`、`__ge__`
- 索引：`__getitem__`
- 类型转换：`astype`
- 调用：`__call__`

特别地，`__add__` 对元组类型有特殊处理：若左操作数为 TupleType 且右操作数为 tuple，则执行元组拼接而非算子加法 [F-101]。

## Attrs 属性体系

每个算子调用通过 `Attrs` 对象携带参数。Attrs 是一个强类型的属性容器，在 C++ 中定义为继承自 `AttrsNode` 的结构体，在 Python 中通过 `tvm.relax.attrs` 访问。Attrs 具有以下特点：

1. **反射支持**：每个字段通过反射注册，可序列化为 JSON 或从 JSON 反序列化。
2. **结构相等**：两个 Attrs 对象按字段值比较，不依赖指针身份。
3. **Schema 定义**：每个算子的 Attrs 类定义了该算子接受的参数名、类型和默认值。

Attrs 在算子注册时与 Op 关联，在算子调用时作为 Call 节点的 `attrs` 字段传递。Pass 通过检查 Attrs 确定算子的具体参数（如卷积的 stride 和 padding）。

## 算子属性函数类型

Relax 算子通过属性函数类型（Op Attribute Types）定义其在编译各阶段的行为。这些函数类型注册在 Op 上，供 Pass 回调。

### FInferType：类型推导

`FInferType` 的签名为 `Type(const Call&, const BlockBuilder&)` [F-56]。它根据算子参数和属性推导输出类型。类型推导在 BlockBuilder 的 Normalize 阶段自动调用，确保每个绑定变量都有类型注解。

### FNormalize：归一化

`FNormalize` 是归一化函数类型，作为 BlockBuilder 的一部分对每个表达式应用 [F-57]。它将多种等价语法形式归一化为单一表示。例如，某些算子可能接受多种参数写法，FNormalize 将它们统一为标准形式。归一化在 Emit 时自动执行，确保 IR 处于范式状态。

### FValidate：验证

`FValidate` 是验证函数类型，仅作为 well-formed 检查器的一部分运行 [F-58]。它定义算子的约束条件（如"卷积输入维度必须为 4"、"stride 必须为正数"），在 IR 验证阶段报告错误。

### FLegalize：合法化

`FLegalize` 是合法化函数类型，将 `relax::Call` 替换为更具体的实现（如 TIR 函数调用）[F-59]。合法化的结果表达式不得包含原始算子。FLegalize 是 Relax 高层算子降级到 TIR 的主要机制：

1. `LegalizeOps` Pass 遍历数据流块中的每个 Call。
2. 查找算子注册的 FLegalize 函数。
3. 调用 FLegalize，传入 Call 和 BlockBuilder。
4. FLegalize 生成 TIR PrimFunc 和 `call_tir` 表达式。
5. Pass 用返回的表达式替换原始 Call。

FLegalize 支持自定义映射 `cmap` 覆盖默认实现，`skip_ops` 指定跳过的算子 [F-118]。这允许用户为特定算子提供自定义降级逻辑。

### FLowerBuiltin：内置函数降级

`FLowerBuiltin` 是运行时内置函数降级函数类型，在 `LowerRuntimeBuiltin` Pass 中使用 [F-60]。它将 Relax 内置算子映射到 VM 内置函数调用。

### FPrimalGradient：梯度

`FPrimalGradient` 是算子梯度函数类型，签名为 `Array<Expr>(const Var&, const Call&, const Var&, const BlockBuilder&)` [F-61]。它定义算子的反向微分规则，被 `Gradient` Pass 用于自动微分。四个参数分别为：原始输入变量、原始前向调用、输出梯度变量、BlockBuilder。

### FCallPacked：运行时函数降级

`FCallPacked` 类型别名为 `ffi::String`，表示算子在代码生成时降级到的运行时函数名 [F-55]。当算子没有 TIR 实现但有对应的运行时函数时，通过 FCallPacked 指定运行时全局函数名。

## OpPatternKind：算子融合模式

`OpPatternKind` 枚举定义了 7 种算子模式，是算子融合算法的核心依据 [F-54]：

| 枚举值 | 数值 | 说明 |
|--------|------|------|
| `kElemWise` | 0 | 逐元素算子，一对一映射（如 add、relu） |
| `kBroadcast` | 1 | 广播算子，输出形状由广播规则决定（如 broadcast_to） |
| `kInjective` | 2 | 单射算子，每个输出元素对应一个输入元素但可能重排（如 transpose） |
| `kCommReduce` | 3 | 交换归约算子（如 sum、max） |
| `kOutEWiseFusable` | 4 | 输出逐元素可融合算子（如 conv2d 的输出） |
| `kTuple` | 7 | 元组算子 |
| `kOpaque` | 8 | 不透明算子，不可融合 |

融合规则遵循从"可融合"到"不透明"的层级：`kElemWise` 总是可以融合到其消费者；`kBroadcast` 和 `kInjective` 可以融合到 `kOutEWiseFusable` 之后；`kCommReduce` 通常作为融合边界；`kOpaque` 阻止融合。`FuseOps` Pass 根据每个算子注册的 `op_pattern` 属性决定融合分组 [F-128]。

## PatternRegistry：模式注册

除了基于 OpPatternKind 的自动融合，Relax 还支持通过 `FusionPattern` 注册自定义融合模式 [F-129]：

```cpp
class FusionPatternNode : public ffi::Object {
 public:
  ffi::String name;
  DFPattern pattern;
  ffi::Map<ffi::String, DFPattern> annotation_patterns;
  ffi::Optional<ffi::Function> check;
  ffi::Optional<ffi::Function> attrs_getter;
};
```

- `name`：模式名称。
- `pattern`：DFPattern 描述的子图结构。
- `annotation_patterns`：需要注解的内部模式。
- `check`：可选验证函数，接收 `PatternCheckContext`（包含 matched_expr、annotated_expr、matched_bindings、var_usages、value_to_bound_var 五个字段 [F-130]），返回布尔值。
- `attrs_getter`：可选属性获取函数，从匹配的子图中提取属性传递给融合后的函数。

`FuseOpsByPattern` Pass 按提供的模式列表进行模式匹配并融合，模式顺序决定优先级 [F-132]。当 `annotate_codegen` 为 true 时，为外部后端卸载包装代码生成属性。`MergeCompositeFunctions` 进一步将一个或多个 FuseOpsByPattern 创建的复合函数分组，标注 kCodegen 和 GlobalSymbol 属性 [F-133]。

## 算子注册流程

一个 Relax 算子的完整注册流程包括：

1. **定义 Attrs**：若算子有参数，定义 AttrsNode 结构体并注册反射。
2. **注册 Op**：通过 `RELAY_REGISTER_OP` 或 Relax 对应宏注册算子名称和参数数量。
3. **设置属性函数**：注册 FInferType、FNormalize、FValidate、FLegalize 等。
4. **设置 OpPatternKind**：注册 `op_pattern` 属性指定融合模式。
5. **注册梯度**：若支持训练，注册 FPrimalGradient。
6. **Python 绑定**：在 `python/tvm/relax/op/` 中添加 Python 函数。
7. **添加运算符重载**（可选）：在 `__init__.py` 中注册运算符重载。

## 设计要点

Relax 算子体系的设计体现了以下原则：

1. **属性驱动编译**：算子的编译行为（类型推导、归一化、合法化、融合）通过属性函数声明式定义，而非硬编码在 Pass 中，便于扩展。
2. **分层降级**：从高层 Relax 算子到 TIR PrimFunc 的降级通过 FLegalize 可定制，支持不同后端选择不同实现。
3. **双轨融合**：OpPatternKind 提供基于规则的自动融合，FusionPattern 提供基于模式的自定义融合，兼顾自动化和灵活性。
4. **完整的数学覆盖**：32 个一元算子、26 个二元算子及完整的统计/线性代数/搜索/排序算子，覆盖主流深度学习模型需求。
5. **Python 优先体验**：运算符重载和 NumPy 风格的 API 使模型定义简洁直观。

## 相关概念

- [Relax 图级 IR](/concepts/11-relax-ir.md) — 算子以 Call 节点形式存在于 Relax 函数中，是图级 IR 的核心组成部分
- [BlockBuilder 与 Dataflow](/concepts/12-relax-block-builder.md) — BlockBuilder 的 Normalize 阶段调用算子的 FInferType/FNormalize 进行类型推导与归一化
- [Relax 变换 Pass](/concepts/14-relax-passes.md) — LegalizeOps/FuseOps 等 Pass 根据算子属性执行合法化和融合
- [TE 张量表达式](/concepts/15-te-tensor-expression.md) — FLegalize 将高层 Relax 算子降级为基于 TE 描述的 TIR PrimFunc
- [TOPI 算子库](/concepts/16-topi-operator-library.md) — Relax 算子合法化时调用 TOPI 获取计算定义和调度模板
