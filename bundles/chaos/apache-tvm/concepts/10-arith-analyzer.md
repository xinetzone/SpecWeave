---
type: Concept
title: Arith 整数分析器
description: Arith 子系统是 TVM 编译期的轻量级整数证明引擎，组合七子分析器进行边界分析、模分析、化简和集合运算，支撑调度合法性验证和内存优化
tags: [tvm, arith, analyzer, const-int-bound, modular-set, z3, 整数分析, 证明器]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
---

# Arith 整数分析器

Arith 子系统是 TVM 编译器内部的"轻量级定理证明器"。它不依赖外部 SMT 求解器（Z3 为可选后端），而是通过多个专用分析器的组合对整数表达式进行边界分析、模分析、化简和集合分析。这套证明引擎支撑了调度合法性验证（如 ComputeAt 的区域覆盖证明）、缓冲区压缩、循环展开因子推导、内存访问边界检查等关键编译期决策。Arith 位于 `include/tvm/arith/` 和 `src/arith/` 目录。

## Analyzer 复合分析器

### 核心架构

`AnalyzerObj` 是包含多个子分析器的复合分析器对象，定义在 `include/tvm/arith/analyzer.h` [F-197]。它包含七个子分析器：

| 子分析器 | 职责 |
|---------|------|
| `const_int_bound` | 常量整数边界分析 |
| `modular_set` | 模集合分析 |
| `rewrite_simplify` | 重写规则化简 |
| `canonical_simplify` | 规范形式化简 |
| `int_set` | 整数集合分析 |
| `transitive_comparisons` | 传递比较分析 |
| `z3_prover` | 可选 Z3 SMT 后端 |

`AnalyzerObj` 构造函数初始化所有子分析器并传入 `this` 指针，使各子分析器可以通过复合分析器协作 [F-199]。

`Analyzer` 是轻量级引用计数句柄，默认构造函数会创建新的 `AnalyzerObj` [F-208]。复制句柄共享同一 `AnalyzerObj` 状态 [F-209]。AnalyzerObj 标记为 `_type_mutable = true`，允许通过 const 引用调用非 const 方法 [F-210]。类型键为 `"arith.Analyzer"` [F-211]。

### 变量绑定

`AnalyzerObj::Bind(var, expr, allow_override)` 将变量绑定到表达式 [F-200]：

1. 先经 canonical_simplify 和 rewrite_simplify 化简绑定表达式
2. 更新所有子分析器的绑定信息

`AnalyzerObj::Bind(var, range, allow_override)` 绑定变量到范围 [F-201]：当 extent 为 1 时退化为表达式绑定。

`MarkGlobalNonNegValue` 将值标记为全局非负，通过分解为 `symbol*scale+offset` 并更新 const_int_bound [F-202]。

### 证明接口

Analyzer 提供三个核心证明方法：

- **CanProveGreaterEqual(expr, lower_bound)**：先经 rewrite_simplify 化简，再检查 const_int_bound 的 min_value [F-203]
- **CanProveLess(expr, upper_bound)**：类似地检查 const_int_bound 的 max_value [F-204]
- **CanProveEqual(lhs, rhs)**：先检查整数常量，再通过 `CanProve(lhs - rhs == 0)` 判定 [F-205]

### 化简接口

`AnalyzerObj::Simplify(expr, steps)` 默认执行 2 步化简 [F-206]：

1. rewrite_simplify（重写规则化简）
2. canonical_simplify（规范形式化简）

`Clone()` 深拷贝分析器，生成独立的副本 [F-207]。注释说明不应在约束作用域激活时调用 Clone()，否则约束会泄漏为全局事实。

## ConstIntBound 常量整数边界

ConstIntBound 是最快的分析器，以 O(1) 查表方式提供整数表达式的上下界。

### ConstIntBoundNode 结构

`ConstIntBoundNode` 包含两个 `int64_t` 字段 [F-216]：

- **min_value**：表达式的最小可能值
- **max_value**：表达式的最大可能值

两个特殊值表示无界 [F-217][F-218]：

- `kPosInf = std::numeric_limits<int64_t>::max()`：正无穷（无上界）
- `kNegInf = -kPosInf`：负无穷（无下界）

类型键为 `"arith.ConstIntBound"`，使用 `kTVMFFISEqHashKindTreeNode` 哈希 [F-219]。

### ConstIntBoundAnalyzer

`ConstIntBoundAnalyzer` 使用 `BoundMapType`（`std::unordered_map<PrimExpr, ConstIntBound>`）缓存中间结果 [F-220]。

核心方法：

- **operator()(expr)**：分析表达式的常量整数边界 [F-221]
- **Update(var, info, allow_override)**：更新变量的边界信息 [F-222]
- **Bind(var, range, allow_override)**：将变量绑定到范围 [F-223]
- **IsBound(var)**：检查变量是否已绑定范围 [F-224]

### 边界传播规则

ConstIntBoundAnalyzer 对每种算术运算实现了边界传播规则，例如：

- 加法：`[a_min+b_min, a_max+b_max]`
- 乘法：考虑符号组合的四种情况
- 除法：处理除数正负和除零保护
- min/max：取对应边界的 min/max

## ModularSet 模集合

ModularSet 分析表达式的模性质，用于对齐分析和存储优化。

### ModularSetNode 结构

`ModularSetNode` 包含两个 `int64_t` 字段 [F-225]：

- **coeff**：系数
- **base**：基数

ModularSet 表示集合 `{coeff * x + base | x in Z}`，当 coeff≠0 时等价于 `{n | n % coeff == base}` [F-226]。例如：

- `coeff=2, base=0` 表示偶数集合
- `coeff=16, base=0` 表示 16 字节对齐的地址
- `coeff=1, base=0` 表示所有整数（无约束）

类型键为 `"arith.ModularSet"` [F-227]。

### ModularSetAnalyzer

`ModularSetAnalyzer::operator()(expr)` 分析表达式的模信息 [F-228]。它对每种运算推导模性质：

- 加法：`(coeff1*x+base1) + (coeff2*y+base2)` 的 coeff 为 gcd(coeff1, coeff2)
- 乘法：`(c1*x+b1)*(c2*y+b2)` 的 coeff 为 c1*c2
- 常量：coeff=0, base=常量值

ModularSet 在调度原语 `StorageAlign` 中用于验证和利用缓冲区步幅对齐约束：`stride[axis] == k*factor+offset` [F-237]。

## RewriteSimplify 重写化简器

RewriteSimplifier 基于声明式重写规则对表达式进行化简。

### 核心机制

`RewriteSimplifier::operator()(expr)` 对表达式进行递归化简 [F-232]。它维护一组重写规则，每个规则匹配特定的表达式模式并替换为更简单的形式。例如：

- `x + 0 → x`
- `x * 1 → x`
- `x * 0 → 0`
- `min(x, max_value) → x`（当已知 x ≤ max_value）
- `if_then_else(true, a, b) → a`

### 可选扩展

`RewriteSimplifier::Extension` 枚举定义了四个可选扩展 [F-233]：

| 扩展标志 | 语义 |
|---------|------|
| `kTransitivelyProveInequalities` | 使用已知不等式的传递性进行证明 |
| `kConvertBooleanToAndOfOrs` | 将布尔表达式转换为合取范式（CNF） |
| `kApplyConstraintsToBooleanBranches` | 对 if 分支应用条件约束 |
| `kComparisonOfProductAndSum` | 乘积与和比较的特殊处理 |

`SetEnabledExtensions(flags)` 启用可选扩展，`GetEnabledExtensions()` 返回当前启用的扩展 [F-234]。

### 步数限制与统计

`SetMaximumRewriteSteps(maximum)` 设置最大重写步数限制，超限抛异常 [F-235]。这防止了非终止的重写循环。`GetStatsCounters()` 和 `ResetStatsCounters()` 提供统计计数器功能，用于监控化简过程 [F-236]。

## CanonicalSimplify 规范化简器

CanonicalSimplifier 将表达式转换为规范形式，使得语义等价的表达式具有相同的表示。

### 核心机制

`CanonicalSimplifier::operator()(expr)` 对表达式进行规范化化简 [F-239]。规范形式的特点：

- 加法和乘法的操作数按确定性顺序排列
- 常量合并到固定位置
- 嵌套表达式扁平化

例如，`(b + a) + 3` 和 `3 + (a + b)` 都规范化为 `a + b + 3`。

### 变量更新

`CanonicalSimplifier::Update(var, new_expr, allow_override)` 更新变量绑定 [F-240]，在变量替换后重新规范化相关表达式。

CanonicalSimplify 通常在 RewriteSimplify 之后运行，作为化简管线的第二步 [F-206]。

## IntSet 整数集合

IntSet 表示符号整数集合，用于区域分析和缓冲区边界计算。

### IntSetNode 基类

`IntSetNode` 基类类型键为 `"ir.IntSet"` [F-241]。`IntSet` 引用类提供集合操作接口 [F-242]：

- **CoverRange(max_range)**：查找覆盖集合的范围 [F-243]
- **min()/max()**：返回集合的下界和上界 [F-244]
- **GetSignType()**：返回集合中元素的符号类型（kPositive/kNegative/kZero/kUnknown）[F-245]
- **IsNothing()/IsEverything()/IsSinglePoint()**：判断集合的特殊形态 [F-247]
- **CanProveSinglePoint(ana)**：使用分析器进行更强的单点证明 [F-248]
- **CanProvePositive/Negative/NonPositive/NonNegative()**：符号证明 [F-249]

### 静态工厂方法

IntSet 提供多个静态工厂方法 [F-250]：

- **Nothing()**：空集
- **Everything()**：全集（无约束）
- **SinglePoint(point)**：单点集合
- **Vector(vec)**：离散点集合
- **FromMinExtent(min, extent)**：连续区间 [min, min+extent)

### IntSetAnalyzer

`IntSetAnalyzer::operator()(expr, dom_map)` 根据变量域映射分析表达式的整数集合 [F-252]。重载版本 `operator()(expr)` 使用已绑定变量的域映射分析 [F-253]。

IntSetAnalyzer 是 S-TIR 区域分析的底层引擎：`AnalyzeRegionUpperBound` 和 `AnalyzeRegionLowerBound` 使用 IntSetAnalyzer 计算缓冲区访问区域的精确范围。

### Python 接口

Python 端导出 `IntSet`、`IntervalSet`、`PresburgerSet` [F-254]，以及 `estimate_region_lower_bound`、`estimate_region_strict_bound`、`estimate_region_upper_bound` 函数 [F-255]。

## TransitiveComparisonAnalyzer 传递比较分析器

TransitiveComparisonAnalyzer 维护已知的变量比较关系，通过传递性推导新的比较结果。

### CompareResult 比较结果

`CompareResult` 枚举包含 8 个值 [F-256]：

| 枚举值 | 数值 | 语义 |
|--------|------|------|
| `kInconsistent` | 0 | 矛盾（已知同时 < 和 ≥） |
| `kEQ` | 1 | 等于 |
| `kLT` | 2 | 小于 |
| `kLE` | 3 | 小于等于 |
| `kGT` | 4 | 大于 |
| `kGE` | 5 | 大于等于 |
| `kNE` | 6 | 不等于 |
| `kUnknown` | 7 | 未知 |

CompareResult 支持位运算 `&` 和 `|`，用于组合多个比较结果 [F-257]。

### TryCompare 推导

`TransitiveComparisonAnalyzer::TryCompare(lhs, rhs, propagate_inequalities)` 尝试使用已知比较的传递性推导结果 [F-258]。例如，已知 `a < b` 和 `b ≤ c`，可推导出 `a < c`。

## Z3Prover SMT 证明器

Z3Prover 是可选的 SMT（Satisfiability Modulo Theories）后端，在编译时启用 `USE_Z3=ON` 时可用。

### 核心接口

`Z3Prover` 类提供以下方法 [F-260~F-267]：

- **IsEnabled()**：检查 Z3 后端是否编译启用 [F-261]
- **CanProve(expr)**：尝试证明表达式恒真 [F-262]
- **GetSMTLIB2(expr)**：获取当前上下文的 SMTLIB2 表示 [F-263]
- **SetTimeoutMs(timeout_ms)**：设置超时（毫秒）[F-264]
- **SetRLimit(rlimit)**：设置资源限制 [F-265]
- **GetModel(expr)**：获取可满足时的模型字符串 [F-266]
- **CountSatisfyingValues(var, max_count, min_consecutive)**：计算满足约束的整数值数量 [F-267]

### 使用策略

Z3 是最后手段的证明器，仅在快速分析器无法证明时调用。这是因为：

1. SMT 求解可能非常耗时（需要超时保护）
2. 大多数编译器内部的证明问题可通过专用分析器快速解决
3. Z3 作为可选依赖，不强制安装

## ConstraintContext 约束上下文

ConstraintContext 提供 RAII 风格的临时约束管理。

### 工作机制

`ConstraintContext` 配合 `With<ConstraintContext>` 使用 [F-212]：

- **EnterWithScope**：依次调用六个子分析器的 `EnterConstraint` 方法（const_int_bound、modular_set、rewrite_simplify、int_set、transitive_comparisons、z3_prover）[F-213]
- **ExitWithScope**：按逆序调用恢复函数清理约束 [F-214]

### 使用场景

ConstraintContext 用于在分析特定代码区域时添加临时假设。例如，在分析循环体时，可以假设循环变量在 `[min, min+extent)` 范围内：

```cpp
{
    With<ConstraintContext> ctx(&analyzer);
    analyzer.Bind(loop_var, Range::FromMinExtent(min, extent));
    // 在这个作用域内，analyzer 知道 loop_var 的范围
    analyzer.CanProveLess(index, buffer_size);
}
// 退出作用域后，临时约束被移除
```

这种机制在 S-TIR 的区域分析中广泛使用——分析循环嵌套中的缓冲区访问时，逐层添加循环变量的范围约束。

## IterAffineMap 迭代仿射映射

IterAffineMap 分析准仿射迭代映射，用于布局变换和索引分析。

### 两种映射模式

文件头注释说明了两种映射模式 [F-270]：

**Fuse（融合）**：
```text
y = x2 * 12 + x1 * 4 + x0
```
将多个迭代变量融合为一个线性索引。

**Split（分割）**：
使用 floorDiv 和 mod 将一个迭代变量拆分为多个：
```text
x0 = y % 4
x1 = (y / 4) % 3
x2 = y / 12
```

### IterMapExpr 节点体系

- **IterMapExprNode**：所有迭代映射表达式的基类，类型键 `"arith.IterMapExpr"` [F-268]
- **IterMarkNode**：包含 `source`（源表达式）和 `extent`（迭代范围）[F-269]

IterAffineMap 支持逆映射计算，在 IndexMap 的布局变换中使用 [F-172]。

### DeduceBound 边界推导

`DeduceBound` 在条件约束下推导目标变量的边界。它结合 ConstIntBound 和 IntSet 分析，在给定迭代变量范围的情况下推导索引表达式的精确范围。

## 分层证明策略

Arith 子系统采用分层证明策略，在精度和速度之间取得平衡：

```mermaid
graph TB
    A[待证明表达式] --> B[ConstIntBound O(1) 查表]
    B -->|无法证明| C[ModularSet 模分析]
    C -->|无法证明| D[RewriteSimplify 规则重写]
    D -->|无法证明| E[CanonicalSimplify 规范化]
    E -->|无法证明| F[IntSet 集合分析]
    F -->|无法证明| G[TransitiveComparison 传递链]
    G -->|无法证明| H{Z3 启用?}
    H -->|是| I[Z3 SMT 求解]
    H -->|否| J[返回 false/unknown]
    I --> J
```

**ProofStrength** 枚举控制证明强度。内部递归重写不使用超过 `kDefault` 的强度以控制编译时间。这种分层设计确保了常见情况的快速响应，同时保留了对复杂问题的求解能力。

## 在 TVM 编译中的应用

Arith 子系统在 TVM 编译器中有广泛应用：

1. **调度合法性验证**：`ProducerCoversConsumer` 逐维使用算术分析器证明产生区域覆盖消费区域 [F-197]
2. **缓冲区压缩**：`CompactBufferAllocation` 使用边界分析确定精确访问区域，移除未访问部分 [F-270]
3. **存储对齐**：`StorageAlign` 依赖 ModularSet 分析验证步幅约束 [F-237]
4. **常量折叠**：TIRx 表达式运算符对索引类型执行立即常量折叠 [F-032]，是 Arith 化简的轻量前置
5. **布局变换**：IndexMap 的逆映射计算依赖 IterAffineMap 的仿射分析 [F-172]
6. **形状证明**：Relax 的形状等价证明底层依赖 Arith
7. **越界检查**：`OOBChecker` Pass 使用边界分析验证内存访问安全性
8. **循环展开**：UnrollLoop 根据常量边界推导展开因子

## 相关概念

- [SBlock 声明式调度](/concepts/07-sblock-schedule.md)
- [调度原语](/concepts/08-schedule-primitives.md)
- [Buffer/Var/IterVar 核心类型](/concepts/06-buffer-var-itervar.md)
- [TIRx 中间表示](/concepts/05-tirx-ir.md)
- [MetaSchedule 自动调度](/concepts/09-meta-schedule.md)
