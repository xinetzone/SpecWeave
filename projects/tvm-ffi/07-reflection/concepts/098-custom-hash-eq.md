---
type: Concept
title: "视角098：自定义哈希/相等注册"
description: "解析通过 TypeAttr 注册 kSEqual/kSHash/kEq/kHash/kAnyEqual/kAnyHash 自定义比较与哈希钩子的机制，区分结构层与 Python 递归层，以及钩子接收的递归回调签名。"
tags:
  - reflection
  - custom-hash
  - custom-equal
  - hooks
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-034, F-251, F-263
  - code:
    - include/tvm/ffi/reflection/accessor.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/extra/structural_equal.h
    - include/tvm/ffi/extra/structural_hash.h
---

# 视角098：自定义哈希/相等注册

## 概述

TVM FFI 反射系统允许类型通过 TypeAttr 机制注册自定义的相等与哈希钩子，覆盖默认的逐字段反射比较。系统区分两个层级：**结构层**（`kSEqual`/`kSHash`）服务于支持 def/use 语义的编译器结构比较，**递归层**（`kEq`/`kHash`/`kCompare`）服务于 Python `==`/`hash()` 协议，另有 **Any 层**（`kAnyEqual`/`kAnyHash`）服务于容器键比较。本视角解析各钩子的签名、注册方式与协作关系。

## 结构层钩子

结构层钩子被 `StructuralEqual`/`StructuralHash`（视角094）消费，支持自由变量映射与 def 区域语义。

### kSEqual（__s_equal__）

定义在 `accessor.h:478`，签名为：

```
(TSelf lhs, TSelf rhs, Function eq_cb) -> bool
```

其中 `eq_cb` 是递归比较回调，签名 `(AnyView lhs, AnyView rhs, bool def_region, AnyView field_name) -> bool`，用于比较子值。钩子可比较部分字段后委托 `eq_cb` 处理嵌套值，`def_region` 参数控制自由变量绑定，`field_name` 用于不匹配路径报告。若类型未注册 `kSEqual`，比较器回退到逐字段反射比较。

### kSHash（__s_hash__）

定义在 `accessor.h:462`，签名为：

```
(TSelf self, int64 init_hash, Function hash_cb) -> int64
```

`hash_cb` 签名 `(AnyView val, int64 init_hash, bool def_region) -> int64`，递归哈希子值。钩子接收累积初始哈希，可混入自定义盐值后委托回调。这一设计使哈希组合顺序可控，避免了不同字段顺序产生相同哈希的碰撞风险。

## 递归层钩子

递归层钩子服务于 Python 数据模型与通用 `RecursiveEq`/`RecursiveHash`，不涉及自由变量映射。

- **`kEq`**（`"__ffi_eq__"`，`accessor.h:406`）：签名 `(TSelf lhs, TSelf rhs, FnEq fn_eq) -> bool`，自定义 `==`。若未注册，回退到 `kCompare`。
- **`kHash`**（`"__ffi_hash__"`，`accessor.h:394`）：签名 `(TSelf self, FnHash fn_hash) -> int64`，自定义 `hash()`。
- **`kCompare`**（`"__ffi_compare__"`，`accessor.h:418`）：签名 `(TSelf lhs, TSelf rhs, FnCmp fn_cmp) -> int32`，三路比较，服务于 `<`/`<=`/`>`/`>=`，同时作为 `kEq` 的回退。
- **`kRepr`**（`"__ffi_repr__"`，`accessor.h:383`）：签名 `(TSelf self, FnRepr fn_repr) -> String`，自定义 `__repr__`。

每个钩子都接收一个递归回调（`fn_eq`/`fn_hash`/`fn_cmp`/`fn_repr`），使钩子能复用框架的递归遍历与循环检测，只需处理类型特有的逻辑。

## Any 层钩子

Any 层钩子在 `Any` 而非 `ObjectRef` 层级操作，被容器键比较消费：

- **`kAnyHash`**（`"__any_hash__"`，`accessor.h:433`）：可为原始 C 函数指针 `int64_t (*)(const Any& src)`（快速路径，无装箱开销）或 `Function` 对象 `(Any src) -> int64`。
- **`kAnyEqual`**（`"__any_equal__"`，`accessor.h:446`）：可为原始 C 函数指针 `bool (*)(const Any& lhs, const Any& rhs)` 或 `Function` 对象。

源码注释说明，与 `kHash`（操作 `ObjectRef` 且递归）不同，Any 层钩子在 `AnyHash`/`AnyEqual` 遇到持有该类型对象的 `Any` 作为容器键时调用。原始函数指针形式避免了创建 `Function` 对象的开销，适用于高频容器操作。

## 注册方式

所有钩子通过 `ObjectDef<T>::def_type_attr` 或 `TypeAttrDef<T>::def` 注册：

```cpp
refl::ObjectDef<MyType>()
    .def_ro("field", &MyType::field)
    .def_type_attr(refl::type_attr::kSEqual, &MyEqualHook)
    .def_type_attr(refl::type_attr::kSHash, &MyHashHook);
```

`def_type_attr`（`registry.h:879/897`）通过 SFINAE 分派：可直接转为 `AnyView` 的值原样存储，否则作为可调用对象经 `GetMethod` 包装为 `Function` 后通过 `TVMFFITypeRegisterAttr`（`c_api.h:1426`）注册。函数指针钩子会被包装为带类型 schema 的 `Function`，名称形如 `"<type_key>.__s_equal__"`。

## 结构变更钩子

除比较与哈希外，类型属性还支持结构遍历与变更钩子：

- **`kStructuralVisit`**（`"__s_visit__"`，`accessor.h:499`）：自定义结构遍历，返回 `Optional<VisitInterrupt>` 控制中断。
- **`kStructuralMutate`**（`"__s_mutate__"`，`accessor.h:520`）：非就地变更钩子，递归变更子节点并返回新对象。
- **`kStructuralMaybeInplaceMutate`**（`accessor.h:542`）：可选就地变更钩子，仅在输入可安全修改时使用，缺席时回退到非就地变更。

这些钩子与 `kSEqual`/`kSHash` 协同，构成完整的结构操作定制体系，使复杂 IR 节点能在反射遍历中正确处理非平凡内部状态。

## 设计分析

三层钩子设计反映了 TVM FFI 对不同比较场景的精确区分：结构层面向编译器 α 等价，需要自由变量与 def 区域；递归层面向 Python 协议，需要 repr 与三路比较；Any 层面向容器键，追求零开销。每层都提供"默认反射实现 + 自定义钩子覆盖"的模式，钩子通过接收递归回调而非直接递归，保证了循环检测、def 区域管理等横切关注点由框架统一处理。原始函数指针与 `Function` 对象的双模式支持兼顾了性能热点与动态语言扩展。所有钩子通过开放的 TypeAttr 列注册而非硬编码到 `TVMFFITypeInfo`，使得新增钩子类型无需演进核心 ABI，下游项目可自定义扩展属性。

## 相关概念

- [094 结构化相等与哈希](094-structural-equal-hash.md)：消费 kSEqual/kSHash 的框架
- [097 TypeAttr 类型属性](097-type-attr.md)：钩子的存储机制
- [095 SEqHash 种类](095-seq-hash-kind.md)：类型级比较策略
- [092 c_class Python 集成](092-c-class-python-integration.md)：消费 kEq/kHash
