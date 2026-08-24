---
type: Concept
title: "视角095：SEqHash 种类"
description: "解析 TVMFFISEqHashKind 枚举的六种取值：Unsupported、TreeNode、FreeVar、DAGNode、ConstTreeNode、UniqueInstance，以及它们在结构比较与哈希中的语义差异和指针相等快速路径。"
tags:
  - reflection
  - seq-hash
  - dag
  - free-var
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-273
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
    - include/tvm/ffi/reflection/registry.h
---

# 视角095：SEqHash 种类

## 概述

`TVMFFISEqHashKind` 是 TVM FFI 反射系统中声明类型在结构化相等/哈希中行为类别的枚举，定义在 `include/tvm/ffi/c_api.h:1084-1123`。每个类型通过 `TVMFFITypeMetadata::structural_eq_hash_kind` 字段（`c_api.h:1298`）声明自己的种类，C++ 类型通过静态常量 `_type_s_eq_hash_kind`（`object.h:223`）设定。这一枚举让结构比较器能够区分树节点、DAG 节点、自由变量、常量节点与单例，从而在保证语义正确的前提下应用指针相等快速路径。

## 六种取值

### Unsupported（0）

`kTVMFFISEqHashKindUnsupported = 0` 表示类型不支持结构化相等/哈希。基类 `Object` 默认取此值（`object.h:223`）。对该类型调用 `StructuralEqual`/`StructuralHash` 会回退到指针身份比较或抛出错误，具体行为由比较器实现决定。这是安全默认值——类型必须显式 opt-in 才参与结构比较。

### TreeNode（1）

`kTVMFFISEqHashKindTreeNode = 1` 表示对象作为树节点比较：按值递归比较所有子字段，不识别共享。每次遇到子节点都递归展开，即使同一子节点被多次引用也逐份比较。适用于纯函数式数据构造器（如 `AddNode(a, b)`），其语义相等性完全由子节点值决定。

### FreeVar（2）

`kTVMFFISEqHashKindFreeVar = 2` 表示对象是可映射的自由变量。在 `map_free_vars=true` 的比较中，首次遇到自由变量时在左右两侧建立映射（"这两个变量视为等价"），后续遇到同一变量时按映射判定。这是编译器 IR 中 α 等价比较的核心：`λx.λy.x` 与 `λa.λb.a` 因变量名不同但绑定结构相同而等价。

### DAGNode（3）

`kTVMFFISEqHashKindDAGNode = 3` 表示对象作为有向无环图（DAG）节点比较。比较器维护已访问节点映射，识别共享子结构。源码注释（`c_api.h:1069-1082`）给出了经典示例：

```
x = VarNode()
v0 = AddNode(x, 1)
v1 = AddNode(x, 1)
v2 = AddNode(v0, v0)   # v0 被引用两次
v3 = AddNode(v1, v0)   # v1 和 v0 各引用一次
```

若 `AddNode` 为 TreeNode，则 `v2` 与 `v3` 结构相等（展开后均为 `AddNode(AddNode(x,1), AddNode(x,1))`）；若为 DAGNode，则二者不等，因为共享拓扑不同。DAG 模式对编译器中的公共子表达式消除（CSE）正确性至关重要。

### ConstTreeNode（4）

`kTVMFFISEqHashKindConstTreeNode = 4` 表示常量树节点：与 TreeNode 语义相同，但对象不包含任何自由变量作为嵌套子节点。由于无自由变量，比较器可安全使用指针相等作为快速路径——同一常量节点的多次出现若为同一指针则必然相等，无需递归。这一优化适用于编译器中已完全求值的常量。

### UniqueInstance（5）

`kTVMFFISEqHashKindUniqueInstance = 5` 表示单例实例：可直接使用指针相等判定相等性。适用于每个值只存在唯一副本的类型（如 interned 字符串、枚举单例、全局唯一标记对象）。比较器遇到此种类时完全跳过递归，哈希可直接使用指针地址，性能最优。

## 与字段 Def 标志的协作

类型级种类与字段级 `SEqHashDefRecursive`/`SEqHashDefNonRecursive` 标志（视角096）共同决定比较行为：

- 种类决定对象整体被视为树、DAG 还是自由变量。
- 字段标志决定该字段引入的绑定作用域（递归/非递归 def 区域）。
- 二者配合使得比较器能精确表达编译器 IR 中复杂的绑定结构，如函数参数与其形状参数的共同引入。

## C++ 注册方式

类型通过覆盖静态常量声明种类：

```cpp
class MyExprNode : public Object {
 public:
  static constexpr TVMFFISEqHashKind _type_s_eq_hash_kind =
      kTVMFFISEqHashKindTreeNode;
};
```

`ObjectDef<T>::RegisterExtraInfo`（`registry.h:980`）在注册 metadata 时读取该常量并写入 `TVMFFITypeMetadata::structural_eq_hash_kind`，运行时由 `StructuralEqual`/`StructuralHash` 通过 `TVMFFIGetTypeInfo` 查询。

## 性能层级

六种种类形成递增的性能优化层级：

| 种类 | 比较策略 | 相对开销 |
|------|----------|----------|
| UniqueInstance | 指针相等 | O(1) |
| ConstTreeNode | 指针相等快速路径 + 树递归回退 | 接近 O(1) |
| DAGNode | 节点映射 + 递归 | O(n)，含哈希表 |
| TreeNode | 纯递归 | O(n)，无映射开销 |
| FreeVar | 变量映射 + 递归 | O(n)，含绑定表 |
| Unsupported | 指针身份或失败 | O(1) |

类型设计者应根据语义选择最具体的种类：单例数据选 UniqueInstance，无自由变量的纯值选 ConstTreeNode，有共享的表达式选 DAGNode，纯树构造器选 TreeNode，需要 α 等价的变量选 FreeVar。错误地将 DAG 声明为 TreeNode 会导致 CSE 错误合并，错误地将 TreeNode 声明为 DAGNode 则会丢失合法等价。

## 设计分析

`TVMFFISEqHashKind` 以一个枚举字段表达了结构比较的六种核心语义，避免了为每种类型实现虚函数或 visitor。它将编译器领域的专业知识（自由变量、α 等价、DAG 共享）编码为通用反射框架可理解的元数据，使得任意语言绑定都能复用同一套比较逻辑。ConstTreeNode 与 UniqueInstance 的存在体现了"语义正确前提下的性能优化"设计哲学——它们不改变比较结果，仅允许比较器跳过不必要的递归。种类与字段 Def 标志的正交组合则提供了足够的表达力来描述真实编译器 IR 的复杂绑定结构，而无需将比较逻辑硬编码到框架中。

## 相关概念

- [094 结构化相等与哈希](094-structural-equal-hash.md)：消费种类的比较器
- [096 Def Region 语义](096-def-region.md)：字段级绑定作用域
- [088 TypeMetadata](088-type-metadata.md)：种类字段的宿主
- [093 字段标志位系统](093-field-flags.md)：SEqHash 相关字段标志
