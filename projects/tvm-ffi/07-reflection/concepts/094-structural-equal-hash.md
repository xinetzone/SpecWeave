---
type: Concept
title: "视角094：结构化相等与哈希"
description: "解析 StructuralEqual 与 StructuralHash 的设计：静态 API、反射驱动的递归比较/哈希、自由变量映射、张量内容跳过选项，以及通过类型属性注册自定义 kSEqual/kSHash 钩子。"
tags:
  - reflection
  - structural-equal
  - structural-hash
  - seq-hash
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-024, F-034, F-263, F-264, F-265, F-266, F-267, F-268
  - code:
    - include/tvm/ffi/extra/structural_equal.h
    - include/tvm/ffi/extra/structural_hash.h
    - include/tvm/ffi/reflection/accessor.h
    - include/tvm/ffi/c_api.h
---

# 视角094：结构化相等与哈希

## 概述

结构化相等（`StructuralEqual`）与结构化哈希（`StructuralHash`）是 TVM FFI 提供的运行时值比较与散列机制，定义在 `include/tvm/ffi/extra/structural_equal.h:36` 与 `include/tvm/ffi/extra/structural_hash.h:35`。与 C++ 默认的指针相等/`std::hash` 不同，它们递归遍历对象的反射字段，实现深度结构比较，并支持自由变量映射、DAG 共享识别与自定义钩子。这一机制是 IR 节点 α 等价判定、常量折叠、容器键比较等编译器核心功能的基础。

## 公开 API

两个类均为轻量包装器，核心逻辑委托给静态方法：

```cpp
// structural_equal.h:47
static bool Equal(const Any& lhs, const Any& rhs,
                  bool map_free_vars = false,
                  bool skip_tensor_content = false);

// structural_hash.h:45
static uint64_t Hash(const Any& value,
                     bool map_free_vars = false,
                     bool skip_tensor_content = false);
```

- **`map_free_vars`**：是否启用自由变量映射。启用后，标记为 `kTVMFFISEqHashKindFreeVar` 的对象在首次遇到时建立左右映射，后续按映射判定相等。这是 λ 演算风格 α 等价的关键。
- **`skip_tensor_content`**：是否跳过张量数据内容比较。仅比较张量元数据（形状、dtype、device），适用于不关心参数具体数值的编译阶段。

`operator()` 被内联为调用对应静态方法的便捷运算符（`structural_equal.h:71`、`structural_hash.h:52`），使这两个类可直接作为 `std::unordered_map` 的哈希器与键比较器。`StructuralEqual` 还提供 `GetFirstMismatch`（`structural_equal.h:62`）返回首个不匹配的 `AccessPathPair`，用于诊断差异位置。

## 反射驱动的递归

结构化比较/哈希通过反射系统遍历对象：

1. 对基础类型（int、float、bool、string 等）直接比较/哈希值。
2. 对 `Array`/`List` 逐元素递归，长度不同则不等。
3. 对 `Map`/`Dict` 按键值对递归比较，键使用结构哈希定位。
4. 对 `Object` 子类，查询 `TVMFFITypeInfo`：
   - 若类型键不同则不等。
   - 遍历 `ForEachFieldInfo` 反射字段，跳过标记 `SEqHashIgnore` 的字段。
   - 根据字段的 `SEqHashDefRecursive`/`DefNonRecursive` 标志管理 def 区域。
   - 应用 `structural_eq_hash_kind` 决定树/DAG/自由变量/单例策略。
5. 维护已访问节点映射以支持 DAG 共享检测，避免重复递归与无限循环。

## 类型级 SEqHash 种类

`TVMFFITypeMetadata::structural_eq_hash_kind`（`c_api.h:1298`）声明类型在结构比较中的行为类别，由 `TVMFFISEqHashKind` 枚举（`c_api.h:1084`）定义。C++ 类型通过静态常量 `_type_s_eq_hash_kind`（`object.h:223`）设定，默认基类 `Object` 为 `Unsupported`。这一枚举将在[视角095](095-seq-hash-kind.md)中详细分析。

## 自定义钩子

类型可通过类型属性注册自定义比较/哈希钩子，覆盖默认的逐字段逻辑：

- **`kSEqual`**（`"__s_equal__"`，`accessor.h:478`）：自定义结构相等钩子，签名 `(TSelf lhs, TSelf rhs, Function eq_cb) -> bool`。钩子接收递归比较回调 `eq_cb`，可比较部分字段后委托回调处理子值。
- **`kSHash`**（`"__s_hash__"`，`accessor.h:462`）：自定义结构哈希钩子，签名 `(TSelf self, int64 init_hash, Function hash_cb) -> int64`，接收累积哈希与递归哈希回调。
- **`kAnyHash`**（`"__any_hash__"`，`accessor.h:433`）与 **`kAnyEqual`**（`"__any_equal__"`，`accessor.h:446`）：在 `Any` 层级操作的钩子，用于容器键比较，可为原始 C 函数指针（快速路径）或 `Function` 对象。

这些钩子通过 `ObjectDef::def_type_attr(kSEqual, ...)` 或 `TypeAttrDef<T>::def(kSHash, ...)` 注册，与 Python 层的 `__eq__`/`__hash__` 形成分层：`kEq`/`kHash` 服务于 Python 递归协议，`kSEqual`/`kSHash` 服务于支持 def/use 语义的编译器结构比较。

## 设计分析

`StructuralEqual`/`StructuralHash` 的设计将"比较算法"与"类型结构"解耦：类型通过反射声明字段与种类标志，比较器通用地遍历这些声明，无需为每种类型编写 visitor。`map_free_vars` 参数使同一比较器同时支持语法相等（不映射）与 α 等价（映射自由变量）两种语义。自定义钩子在保持默认便利性的同时，为复杂类型（如带缓存的 IR 节点、需要规范化的类型）提供了优化出口。`skip_tensor_content` 选项承认了编译器中"同一算子不同权重"的常见场景，避免了大张量逐字节比较的性能开销。整体设计使 FFI 容器与 IR 节点共享同一套比较/哈希基础设施，减少了重复实现。

## 相关概念

- [095 SEqHash 种类](095-seq-hash-kind.md)：TreeNode/DAGNode/FreeVar 等种类语义
- [096 Def Region 语义](096-def-region.md)：字段标志控制的自由变量绑定作用域
- [098 自定义哈希/相等注册](098-custom-hash-eq.md)：kSEqual/kSHash 钩子的注册方式
- [097 TypeAttr 类型属性](097-type-attr.md)：钩子存储的稀疏列机制
