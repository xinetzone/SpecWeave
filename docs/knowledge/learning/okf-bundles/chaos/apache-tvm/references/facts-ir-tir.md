---
type: Facts
title: TVM IR 核心与 TIR 事实清单
description: 从 TVM 源码采集的 IR 核心层、TIRx、S-TIR 调度系统事实，每条标注文件路径与行号
tags: [tvm, ir, tir, s-tir, facts, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
source_id: ir-tir
---

# TVM IR 核心与 TIR 事实清单

> 源码路径：d:\AI\.chaos\libs\ffi\tvm\
> 采集日期：2026-08-23
> 采集范围：IR 核心层（include/tvm/ir/ + src/ir/）、TIRx（include/tvm/tirx/）、S-TIR 调度（include/tvm/s_tir/ + src/s_tir/）、Python 绑定（python/tvm/ir/ + python/tvm/s_tir/）

---

## 1. IR 核心层

### 1.1 Object/Node 基础体系

- F-001: TVM 的 IR 节点体系采用 `Node`/`ObjectRef` 双层设计：`Node` 后缀类（如 `ExprNode`）继承自 `ffi::Object`，对应引用类（如 `Expr`）继承自 `ffi::ObjectRef`，通过 `data_` 指针持有节点对象 — 源码：`include/tvm/ir/base_expr.h:52-71`
- F-002: `TypeNode` 是所有类型节点的基类，继承自 `Object`；对应的 `Type` 引用类继承自 `ObjectRef` — 源码：`include/tvm/ir/base_expr.h:52-71`
- F-003: `ExprNode` 继承自 `Object`，是所有表达式节点的基类，包含 `ty`（类型）和 `span`（源码位置）字段 — 源码：`include/tvm/ir/expr.h`（ExprNode 定义）
- F-004: `Expr` 是 `ExprNode` 的托管引用类，继承自 `ObjectRef`，提供 COW（Copy-On-Write）方法 — 源码：`include/tvm/ir/expr.h`
- F-005: `PrimExpr` 是 `Expr` 的子类，表示具有基本类型（Primitive Type）的表达式，可从 `int32_t`、`float`、`Call` 隐式构造 — 源码：`src/ir/expr.cc:49-55`
- F-006: `PrimExpr` 支持从 `ffi::String` 回退构造为 `tirx::StringImm` — 源码：`src/ir/expr.cc:55`
- F-007: FFI 层为 `PrimExpr` 特化了 `TypeTraits`，支持从 `StrictBool`、`int64_t`、`double` 自动转换为 `IntImm`/`FloatImm` — 源码：`src/ir/expr.cc:57-71`
- F-008: TVM 使用 `TVM_FFI_DECLARE_OBJECT_INFO_FINAL` 宏声明最终类型信息，参数为类型键字符串、节点类、父节点类 — 源码：`include/tvm/ir/expr.h:296`
- F-009: TVM 使用 `TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE` 宏为引用类定义空值安全的方法 — 源码：`include/tvm/ir/expr.h:307`
- F-010: `TVM_DEFINE_OBJECT_REF_COW_METHOD` 宏为引用类生成 Copy-On-Write 方法，支持不可变数据结构的可变修改 — 源码：`include/tvm/ir/expr.h:308`

### 1.2 表达式系统

- F-011: `GlobalVarNode` 继承自 `ExprNode`，表示顶层模块中的全局变量，仅引用函数定义，用于启用函数间递归调用 — 源码：`include/tvm/ir/expr.h:271-297`
- F-012: `GlobalVarNode` 包含 `name_hint` 字段（`ffi::String` 类型），名称仅作提示，全局变量按地址唯一标识 — 源码：`include/tvm/ir/expr.h:274`
- F-013: `GlobalVarNode` 的结构相等性（SEqual）仅比较 `name_hint`，结构哈希（SHash）也仅基于 `name_hint` — 源码：`include/tvm/ir/expr.h:286-293`
- F-014: `GlobalVarNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindFreeVar`，表示自由变量的相等/哈希语义 — 源码：`include/tvm/ir/expr.h:295`
- F-015: `GlobalVar` 的类型键为 `"ir.GlobalVar"` — 源码：`include/tvm/ir/expr.h:296`
- F-016: `GlobalVar` 特化了 `std::hash` 和 `std::equal_to`，允许其作为 STL 容器的键，使用指针相等/哈希 — 源码：`include/tvm/ir/expr.h:557-567`
- F-017: `CallNode` 继承自 `ExprNode`，表示可调用对象调用，包含 `op`（被调用者）、`args`（参数数组）、`attrs`（属性）、`ty_args`（类型参数）四个字段 — 源码：`include/tvm/ir/expr.h:314-343`
- F-018: `CallNode` 的 `op` 字段类型为 `Expr`，可以是 `Op`、`GlobalVar`、局部函数值或其他可调用表达式 — 源码：`include/tvm/ir/expr.h:322`
- F-019: `Call` 的类型键为 `"ir.Call"`，构造函数接收返回类型、op、参数、属性、类型参数和 span — 源码：`include/tvm/ir/expr.h:342,350-351`
- F-020: `IntImmNode` 继承自 `ExprNode`，表示整数常量，包含 `int64_t value` 字段 — 源码：`include/tvm/ir/expr.h:361-371`
- F-021: `IntImm` 提供静态工厂方法 `Bool()`、`Int32()`、`Int64()` 分别创建布尔、32位整数、64位整数字面量 — 源码：`include/tvm/ir/expr.h:393-413`
- F-022: `IntImm` 构造函数验证类型必须为标量（非向量），且类型代码必须为 int/uint/bool，对无符号类型检查非负和范围 — 源码：`src/ir/expr.cc:73-105`
- F-023: `FloatImmNode` 继承自 `ExprNode`，表示浮点常量，包含 `double value` 字段 — 源码：`include/tvm/ir/expr.h:424-434`
- F-024: `FloatImm` 支持多种浮点类型：float16、float32、bfloat16、float8 变体（e3m4/e4m3/e5m2 等）、float6_e2m3fn、float4_e2m1fn 以及自定义类型 — 源码：`src/ir/expr.cc:121-132`
- F-025: `FloatImm` 对 float32 和 float16/bfloat16 进行范围检查，对 infinity 和 NaN 跳过范围验证 — 源码：`src/ir/expr.cc:135-150`
- F-026: `RangeNode` 继承自 `ffi::Object`（非 ExprNode），表示一维范围，包含 `min`、`extent`、`span` 字段 — 源码：`include/tvm/ir/expr.h:457-481`
- F-027: `Range` 引用类提供 `FromMinExtent()` 静态方法和 `(begin, end)` 构造函数，自动计算 extent = end - begin — 源码：`include/tvm/ir/expr.h:484-506`
- F-028: `RangeNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode`，表示树节点语义，`span` 字段在相等/哈希中被忽略 — 源码：`include/tvm/ir/expr.h:475,478`
- F-029: IR 表达式层重载了全套算术运算符：`+`、`-`（二元和一元）、`*`、`/`、`<<`、`>>` — 源码：`include/tvm/ir/expr.h:57-122`
- F-030: IR 表达式层重载了全套比较运算符：`>`、`>=`、`<`、`<=`、`==`、`!=` — 源码：`include/tvm/ir/expr.h:133-188`
- F-031: IR 表达式层重载了逻辑运算符：`&&`、`||`、`!`，以及位运算符：`&`、`|`、`^`、`~` — 源码：`include/tvm/ir/expr.h:198-260`
- F-032: 所有算术和比较运算符均对索引类型（int32/int64）执行立即常量折叠（eager constant folding） — 源码：`include/tvm/ir/expr.h:54-55`
- F-033: FFI 为 `IntImm` 特化了 `TypeTraits`，从 `int64_t` 自动转换时根据值范围选择 int32 或 int64 类型 — 源码：`include/tvm/ir/expr.h:521-529`
- F-034: FFI 为 `FloatImm` 特化了 `TypeTraits`，从 `double` 自动转换时默认使用 float32 类型 — 源码：`include/tvm/ir/expr.h:535-539`

### 1.3 类型系统

- F-035: `Type` 类提供静态方法 `missing()`/`Missing()` 返回缺失类型的哨兵值，`is_missing()` 检查是否为缺失类型 — 源码：`python/tvm/ir/type.py:31-43`
- F-036: `PrimType` 继承自 `Type`，表示低级 IR 中的基本数据类型，通过 dtype 字符串构造，如 `"float32"`、`"int32"` — 源码：`python/tvm/ir/type.py:57-68`
- F-037: `PrimType` 的哈希基于 dtype 的 `type_code`、`bits`、`lanes` 三元组 — 源码：`python/tvm/ir/type.py:78-80`
- F-038: `PrimType` 提供 `matches_code()` 方法检查类型代码是否匹配给定的 DLPack 代码列表，`matches_element_type()` 检查代码和位数，`is_scalar()` 检查 lanes 是否为 1 — 源码：`python/tvm/ir/type.py:85-97`
- F-039: `PointerType` 继承自 `Type`，包含 `element_type` 和 `storage_scope`（存储范围，默认为空字符串）两个参数 — 源码：`python/tvm/ir/type.py:100-114`
- F-040: `TupleType` 继承自 `Type`，由 `fields`（类型列表）组成 — 源码：`python/tvm/ir/type.py:117-128`
- F-041: `FuncType` 继承自 `Type`，表示函数类型，包含参数类型列表 `arg_types` 和返回类型 `ret_type` — 源码：`python/tvm/ir/type.py:131-150`
- F-042: Python 层使用 `@tvm_ffi.register_object("ir.Type")` 装饰器将 Python 类注册到 C++ 类型键 — 源码：`python/tvm/ir/type.py:27`

### 1.4 函数系统

- F-043: `CallingConv` 枚举定义了三种调用约定：`DEFAULT=0`、`C_PACKED_FUNC=1`、`DEVICE_KERNEL_LAUNCH=2` — 源码：`include/tvm/ir/function.h:44-81`；Python 层同名枚举见 `python/tvm/ir/function.py:32-37`
- F-044: `LinkageType` 枚举定义了函数的链接类型（在 function.h 中声明） — 源码：`include/tvm/ir/function.h`
- F-045: `BaseFuncNode` 继承自 `ExprNode`，是所有函数节点的基类；`BaseFunc` 继承自 `Expr` — 源码：`include/tvm/ir/function.h`
- F-046: Python 层 `BaseFunc` 提供 `attrs` 属性获取函数属性，`with_attr()`/`with_attrs()`/`without_attr()` 方法进行不可变属性更新 — 源码：`python/tvm/ir/function.py:40-100`
- F-047: `with_attr()` 方法先复制函数（copy-on-write），再通过 `BaseFuncWithAttr` FFI 调用设置属性，支持单键值和字典批量设置 — 源码：`python/tvm/ir/function.py:49-76`
- F-048: `BaseFunc` 的类型键为 `"ir.BaseFunc"` — 源码：`python/tvm/ir/function.py:40`

### 1.5 IRModule

- F-049: `IRModuleNode` 持有 `functions`（GlobalVar→BaseFunc 映射）、`source_map`、`attrs`、`global_infos` 等成员 — 源码：`include/tvm/ir/module.h:58-67`
- F-050: `IRModule` 构造时会构建 `global_var_map_`（名称→GlobalVar 的反向映射），并检查重复的全局函数名 — 源码：`src/ir/module.cc:44-61`
- F-051: `IRModuleNode::SEqual` 对 `attrs` 和 `global_infos` 进行正常比较，对 `functions` 按 GlobalVar 名称重映射后比较 — 源码：`src/ir/module.cc:63-85`
- F-052: `IRModuleNode::SHash` 先按名称排序函数，再依次哈希名称、GlobalVar 和函数内容，确保哈希与函数顺序无关 — 源码：`src/ir/module.cc:87-114`
- F-053: `IRModuleNode::ContainGlobalVar()` 通过 `global_var_map_` 查找名称是否存在 — 源码：`src/ir/module.cc:116-118`
- F-054: `IRModuleNode::GetGlobalVar()` 在找不到名称时抛出 `ValueError` 并列出所有候选名称 — 源码：`src/ir/module.cc:120-137`
- F-055: `IRModuleNode::GetGlobalVars()` 返回按名称字母顺序排序的所有 GlobalVar — 源码：`src/ir/module.cc:139-148`
- F-056: Python 层 `IRModule` 构造函数接收 `functions`（dict）、`attrs`、`global_infos`，字符串键自动转换为 `GlobalVar` — 源码：`python/tvm/ir/module.py:43-67`
- F-057: Python 层 `IRModule` 支持字典式接口：`__setitem__`、`__getitem__`、`__delitem__`、`__contains__` — 源码：`python/tvm/ir/module.py:84-128`
- F-058: Python 层 `IRModule.__getitem__` 支持字符串键（通过 `Module_Lookup_str`）和 GlobalVar 键（通过 `Module_Lookup`）两种查找方式 — 源码：`python/tvm/ir/module.py:106-122`
- F-059: Python 层 `IRModule.functions_items()` 返回按函数名称母排序的函数列表 — 源码：`python/tvm/ir/module.py:72-82`
- F-060: Python 层 `IRModule.update()` 支持合并另一个 IRModule 或字典到当前模块 — 源码：`python/tvm/ir/module.py:130-141`
- F-061: `IRModule` 的类型键为 `"ir.IRModule"` — 源码：`python/tvm/ir/module.py:31`

### 1.6 Op/OpRegistry

- F-062: `OpNode` 继承自 `ExprNode`，表示原始算子，通过 `index_` 字段在注册表中索引 — 源码：`src/ir/op.cc:55-58`
- F-063: `Op::Get(name)` 通过全局 `OpRegistry` 按名称查找算子，找不到时抛出 `AttributeError` — 源码：`src/ir/op.cc:49-53`
- F-064: `OpRegEntry::RegisterOrGet(name)` 返回算子的注册条目，支持链式调用设置属性 — 源码：`src/ir/op.cc:63-65`
- F-065: `OpRegEntry` 支持设置 `describe`、`add_argument`、`set_support_level`、`set_num_inputs`、`set_attrs_type_key` 等属性 — 源码：`src/ir/op.cc:113-140`
- F-066: 算子属性通过 `AttrRegistry` 管理，支持 `GetAttrMap`、`HasAttrMap`、`UpdateAttr`、`ResetAttr` 操作 — 源码：`src/ir/op.cc:68-84`
- F-067: FFI 暴露了 `ir.ListOpNames`、`ir.GetOp`、`ir.OpGetAttr`、`ir.OpHasAttr`、`ir.OpSetAttr`、`ir.OpResetAttr`、`ir.RegisterOp`、`ir.OpAddArgument` 等函数 — 源码：`src/ir/op.cc:87-150`
- F-068: Python 层 `Op` 类不能直接构造（`__init__` 抛出 RuntimeError），必须通过 `Op.get(name)` 静态方法获取 — 源码：`python/tvm/ir/op.py:30-47`
- F-069: Python 层 `Op` 提供 `get_attr()`、`has_attr()`、`set_attr()`、`reset_attr()` 方法操作算子属性 — 源码：`python/tvm/ir/op.py:49-100`

### 1.7 Pass 系统

- F-070: `PassInfo` 包含 `opt_level`（优化级别）、`name`（Pass 名称）、`required`（依赖的 Pass 列表）、`traceable`（是否可追踪）元数据 — 源码：`python/tvm/ir/transform.py:30-52`
- F-071: `PassContext` 是优化/分析 Pass 运行的基础环境，包含 `opt_level`、`required_pass`、`disabled_pass`、`instruments`、`config` 等配置 — 源码：`python/tvm/ir/transform.py:55-106`
- F-072: `PassContext` 支持 Python 上下文管理器协议（`__enter__`/`__exit__`），进入时调用 `EnterPassContext`，退出时调用 `ExitPassContext` — 源码：`python/tvm/ir/transform.py:108-113`
- F-073: `PassContext.current()` 静态方法返回当前线程的 Pass 上下文 — 源码：`python/tvm/ir/transform.py:126-129`
- F-074: C++ 层 `PassContext` 使用线程局部存储（`thread_local`）维护上下文栈，每个线程有独立的默认上下文和上下文栈 — 源码：`src/ir/transform.cc:47-63`
- F-075: `PassContext::EnterWithScope()` 先调用 `InstrumentEnterPassContext()`，再将当前上下文压入线程局部栈 — 源码：`src/ir/transform.cc:65-70`
- F-076: `PassContext::ExitWithScope()` 验证栈顶上下文与当前一致后弹出，再调用 `InstrumentExitPassContext()` — 源码：`src/ir/transform.cc:72-79`
- F-077: `PassContext::Current()` 在上下文栈非空时返回栈顶，否则返回默认上下文 — 源码：`src/ir/transform.cc:81-88`
- F-078: `PassContext::PassEnabled()` 判断 Pass 是否启用：禁用列表中的 Pass 被禁用，必需列表中的 Pass 被启用，否则比较优化级别 — 源码：`src/ir/transform.cc:98-108`
- F-079: `PassConfigManager` 管理 Pass 配置选项的注册和合法化，每个配置键关联类型字符串和合法化函数 — 源码：`src/ir/transform.cc:110-150`
- F-080: TVM 使用 `TVM_REGISTER_PASS_CONFIG_OPTION` 宏注册 Pass 配置选项，如 `"testing.immutable_module"`（bool 类型） — 源码：`src/ir/transform.cc:45`
- F-081: Python 层 `Pass` 类是所有 Pass 的基类，继承自 `tvm.runtime.Object` — 源码：`python/tvm/ir/transform.py:143-150`

### 1.8 Attrs 系统

- F-082: `Attrs` 是属性容器基类，`DictAttrs` 是其具体实现，持有键值对映射 — 源码：`include/tvm/ir/attrs.h`；Python 层见 `python/tvm/ir/__init__.py:22`
- F-083: Python 层通过 `make_node` 函数创建属性节点 — 源码：`python/tvm/ir/__init__.py:22`

### 1.9 NodeFunctor 模式

- F-084: `NodeFunctor` 是基于类型分派的访问者模式基类，支持根据节点的运行时类型调用不同的处理函数 — 源码：`include/tvm/ir/node_functor.h`
- F-085: `ExprVisitor` 继承自 `NodeFunctor`，提供表达式的只读遍历，默认递归访问子节点 — 源码：`include/tvm/ir/node_functor.h`
- F-086: `ExprMutator` 继承自 `NodeFunctor`，提供表达式的可变遍历，返回变换后的新表达式 — 源码：`include/tvm/ir/node_functor.h`

### 1.10 其他 IR 核心组件

- F-087: `EnvFunc` 是环境函数，允许在 IR 中引用外部注册的函数 — 源码：`include/tvm/ir/env_func.h`；Python 导出见 `python/tvm/ir/__init__.py:24`
- F-088: `GlobalInfo` 是全局信息基类，`DummyGlobalInfo` 和 `VDevice`（虚拟设备）是其具体实现 — 源码：`include/tvm/ir/global_info.h`；Python 导出见 `python/tvm/ir/__init__.py:35`
- F-089: `PassInstrument` 是 Pass 仪器接口，允许在 Pass 执行前后插入回调，用于分析、验证和 profiling — 源码：`include/tvm/ir/instrument.h`；Python 模块见 `python/tvm/ir/instrument.py`
- F-090: `SourceMap` 和 `Span` 用于源码位置追踪，`SequentialSpan` 表示连续的源码范围 — 源码：`include/tvm/ir/source_map.h`；Python 导出见 `python/tvm/ir/__init__.py:26-28`
- F-091: `UniqueNameSupply` 提供唯一名称生成功能，确保 IR 转换中名称不冲突 — 源码：`include/tvm/ir/unique_name_supply.h`；实现见 `src/ir/unique_name_supply.cc`
- F-092: Python 层 `ir.__init__` 导出了 `Node`、`EnvFunc`、`SourceName`、`Span`、`SequentialSpan`、`assert_structural_equal`、`load_json`、`save_json` 等基础组件 — 源码：`python/tvm/ir/__init__.py:23-32`
- F-093: Python 层 `ir.__init__` 导出了 `Call`、`Expr`、`GlobalVar`、`Range`、`is_prim_expr` 等表达式类 — 源码：`python/tvm/ir/__init__.py:33`
- F-094: Python 层 `ir.__init__` 导出了 `FuncType`、`PointerType`、`PrimType`、`TupleType`、`Type` 等类型类 — 源码：`python/tvm/ir/__init__.py:38`
- F-095: Python 层 `is_prim_expr(value)` 函数判断值是否为具有基本类型的表达式（`isinstance(value, Expr) and isinstance(value.ty, PrimType)`） — 源码：`python/tvm/ir/expr.py:38-40`
- F-096: Python 层 `GlobalVar.__call__` 在所有参数均为 TIR 基本类型时调用 `tvm.tirx.call_tir`，否则在所有参数为 Expr 时创建 `Call` 节点 — 源码：`python/tvm/ir/expr.py:61-90`
- F-097: Python 层 `Call` 构造函数支持字符串 op（自动通过 `Op.get` 转换）、字典 attrs（自动转换为 `DictAttrs`）、字符串 ret_ty（如 `"handle"` 转换为 `PointerType(PrimType("void"))`） — 源码：`python/tvm/ir/expr.py:105-131`
- F-098: Python 层 `Call` 重载了算术运算符，根据是否为基本表达式分派到 `_overload_prim_expr` 或 `_tensor_expr_overload` — 源码：`python/tvm/ir/expr.py:139-150`

---

## 2. TIRx（新 TIR）

### 2.1 TIRx 表达式系统

- F-099: TIRx 命名空间为 `tvm::tirx`，通过 `using IntImmNode = tvm::IntImmNode` 和 `using FloatImmNode = tvm::FloatImmNode` 复用 IR 核心层的整数字面量和浮点字面量节点 — 源码：`include/tvm/tirx/expr.h:50-51`
- F-100: `StringImmNode` 继承自 `ExprNode`，表示字符串常量，仅用于断言中，类型键为 `"tirx.StringImm"` — 源码：`include/tvm/tirx/expr.h:53-63`
- F-101: `StringImm` 继承自 `PrimExpr`，是 `StringImmNode` 的引用类 — 源码：`include/tvm/tirx/expr.h:69-75`
- F-102: `CastNode` 继承自 `ExprNode`，表示类型转换，包含 `PrimExpr value` 字段，类型键为 `"tirx.Cast"` — 源码：`include/tvm/tirx/expr.h:81-90`
- F-103: `BinaryOpNode<T>` 是二元运算节点的模板基类，包含 `a`（左操作数）和 `b`（右操作数），子类通过 `_type_key` 静态成员指定类型键 — 源码：`include/tvm/tirx/expr.h:108-122`
- F-104: `AddNode`/`SubNode`/`MulNode`/`DivNode` 均继承自 `BinaryOpNode<T>`，类型键分别为 `"tirx.Add"`、`"tirx.Sub"`、`"tirx.Mul"`、`"tirx.Div"` — 源码：`include/tvm/tirx/expr.h:125-198`
- F-105: `DivNode` 的语义遵循 C 标准的截断除法（trunc div），区别于 Python 的地板除法 — 源码：`include/tvm/tirx/expr.h:180-181`

### 2.2 变量系统

- F-106: `VarNode` 继承自 `ExprNode`，表示 TIR 中的命名变量，通过地址唯一标识，包含 `name_hint` 字段 — 源码：`include/tvm/tirx/var.h:49-65`
- F-107: `VarNode` 的 `_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindFreeVar`，`name_hint` 在结构相等/哈希中被忽略 — 源码：`include/tvm/tirx/var.h:58-62`
- F-108: `Var` 类型键为 `"tirx.Var"`，有 1 个子类槽位（`_type_child_slots = 1`） — 源码：`include/tvm/tirx/var.h:63-64`
- F-109: `Var` 提供 `copy_with_name()`、`CopyWithSuffix()`、`copy_with_dtype()` 方法创建改名/改类型的副本 — 源码：`include/tvm/tirx/var.h:92-104`
- F-110: `PrimVar` 继承自 `PrimExpr`，是 `VarNode` 的零开销检查视图，额外保证 `ExprNode::ty` 为 `PrimType` — 源码：`include/tvm/tirx/var.h:127-151`
- F-111: FFI 为 `PrimVar` 特化了 `TypeTraits`，在 Any 转换时动态检查底层 VarNode 的类型是否为 PrimType — 源码：`include/tvm/tirx/var.h:319-356`
- F-112: `Region` 类型别名定义为 `ffi::Array<Range>`，表示多维区域 — 源码：`include/tvm/tirx/var.h:153`
- F-113: `tirx::Var` 特化了 `std::hash` 和 `std::equal_to`，使用指针相等/哈希，允许作为 STL 容器的键 — 源码：`include/tvm/tirx/var.h:374-384`

### 2.3 IterVar 枚举与类

- F-114: `IterVarType` 枚举定义了 9 种迭代变量类型：`kDataPar=0`（数据并行）、`kThreadIndex=1`（线程索引）、`kCommReduce=2`（归约）、`kOrdered=3`（有序）、`kOpaque=4`（不透明）、`kUnrolled=5`（展开）、`kVectorized=6`（向量化）、`kParallelized=7`（并行化）、`kTensorized=8`（张量化） — 源码：`include/tvm/tirx/var.h:162-223`
- F-115: `kDataPar` 类型允许所有 IterVar 操作；`kThreadIndex` 禁止 split/fuse/vectorize/parallel；`kCommReduce` 禁止 parallel/vectorize；`kOrdered` 禁止 reorder/parallel/vectorize；`kOpaque` 禁止所有操作和 compute_at — 源码：`include/tvm/tirx/var.h:163-204`
- F-116: `IterVarNode` 继承自 `PrimExprConvertibleNode`，包含 `dom`（Range 域）、`var`（PrimVar 循环变量）、`iter_type`（IterVarType）、`thread_tag`（线程标签）、`span` 字段 — 源码：`include/tvm/tirx/var.h:231-266`
- F-117: `IterVarNode::ToPrimExpr()` 返回内部的 `var`，实现了 `PrimExprConvertibleNode` 接口 — 源码：`include/tvm/tirx/var.h:253`
- F-118: `IterVar` 类型键为 `"tirx.IterVar"`，提供到 `PrimExpr` 的隐式转换运算符 — 源码：`include/tvm/tirx/var.h:274-288`
- F-119: `IterVarType2String()` 函数将 IterVarType 枚举值转换为可读字符串 — 源码：`include/tvm/tirx/var.h:290-312`

### 2.4 Buffer 系统

- F-120: 默认索引类型由宏 `TVM_INDEX_DEFAULT_I64` 控制，默认为 1（int64），可通过编译选项改为 int32 — 源码：`include/tvm/tirx/buffer.h:39-58`
- F-121: `BufferType` 枚举定义了 `kDefault=1` 和 `kAutoBroadcast=2`（自动广播维度为 1 的轴）两种缓冲区类型 — 源码：`include/tvm/tirx/buffer.h:64-68`
- F-122: `BufferNode` 继承自 `ffi::Object`，包含 `data`（Var 数据指针）、`dtype`（PrimType）、`shape`（形状数组）、`strides`（步幅数组）、`elem_offset`（元素偏移）、`name`、`data_alignment`、`offset_factor`、`buffer_type`、`axis_separators`、`layout`、`allocated_addr` 等字段 — 源码：`include/tvm/tirx/buffer.h:71-180`
- F-123: `BufferNode::ElemOffset(index, inner)` 计算给定索引的缓冲区偏移量（以元素为单位），`inner=true` 时忽略 `elem_offset` — 源码：`include/tvm/tirx/buffer.h:166-175`
- F-124: `BufferNode` 的类型键为 `"tirx.Buffer"`，`_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode` — 源码：`include/tvm/tirx/buffer.h:177-179`
- F-125: `Buffer` 构造函数接收 13 个参数：data、dtype、shape、strides、elem_offset、name、data_alignment、offset_factor、buffer_type、axis_separators、span、layout、allocated_addr — 源码：`include/tvm/tirx/buffer.h:191-195`

### 2.5 TIR 语句系统

- F-126: `StmtNode` 是所有 TIR 语句的基类，继承自 `ffi::Object`，包含 `mutable Span span` 字段，预留 15 个子类槽位 — 源码：`include/tvm/tirx/stmt.h:41-61`
- F-127: `StmtNode` 的类型键为 `"tirx.Stmt"`，`_type_s_eq_hash_kind` 为 `kTVMFFISEqHashKindTreeNode` — 源码：`include/tvm/tirx/stmt.h:57-60`
- F-128: `BindNode` 继承自 `StmtNode`，表示变量绑定，包含 `Var var` 和 `Expr value`，无 body 字段，绑定的变量在同一封闭作用域的后续语句中可见 — 源码：`include/tvm/tirx/stmt.h:76-91`
- F-129: `AttrStmtNode` 继承自 `StmtNode`，包含 `node`（属性目标）、`attr_key`（属性键）、`value`（属性值）、`body`（语句体），类型键为 `"tirx.AttrStmt"` — 源码：`include/tvm/tirx/stmt.h:115-135`
- F-130: `AssertStmtNode` 包含 `condition`、`error_kind`（StringImm）、`message_parts`（StringImm 数组，运行时拼接），类型键为 `"tirx.AssertStmt"` — 源码：`include/tvm/tirx/stmt.h:159-176`
- F-131: `BufferStoreNode` 表示多维缓冲区写入，包含 `buffer`、`value`、`indices`、`predicate`（可选谓词掩码），类型键为 `"tirx.BufferStore"` — 源码：`include/tvm/tirx/stmt.h:201-221`
- F-132: `DeclBufferNode` 声明缓冲区可在 body 中使用，包含 `Buffer buffer` 字段，类型键为 `"tirx.DeclBuffer"` — 源码：`include/tvm/tirx/stmt.h:238-248`
- F-133: `AllocBufferNode` 分配并声明缓冲区，包含 `buffer` 和 `annotations`（注解映射），类型键为 `"tirx.AllocBuffer"` — 源码：`include/tvm/tirx/stmt.h:259-279`
- F-134: `AllocBuffer::ConstantAllocationSize()` 在所有形状维度为常量时返回总元素数，否则返回 `std::nullopt` — 源码：`include/tvm/tirx/stmt.h:292-302`
- F-135: `SeqStmtNode` 表示语句序列，包含 `ffi::Array<Stmt> seq`，提供 `size()` 和 `operator[]` 方法，类型键为 `"tirx.SeqStmt"` — 源码：`include/tvm/tirx/stmt.h:312-329`
- F-136: `SeqStmt::Flatten()` 静态模板方法递归展平参数中的数组和 SeqStmt，忽略空指针和 `Evaluate(0)`（no-op），单元素时直接返回该元素 — 源码：`include/tvm/tirx/stmt.h:399-435`
- F-137: `EvaluateNode` 表示表达式求值语句（主要用于将有副作用的 Call 放入 Stmt），包含 `Expr value`，类型键为 `"tirx.Evaluate"` — 源码：`include/tvm/tirx/stmt.h:337-347`
- F-138: `IfThenElseNode` 包含 `condition`、`then_case`、`else_case`（可选），类型键为 `"tirx.IfThenElse"` — 源码：`include/tvm/tirx/stmt.h:517-534`
- F-139: `ForKind` 枚举定义了 5 种循环类型：`kSerial=0`（串行）、`kParallel=1`（CPU 并行）、`kVectorized=2`（SIMD 向量化）、`kUnrolled=3`（展开）、`kThreadBinding=4`（线程绑定） — 源码：`include/tvm/tirx/stmt.h:556-575`
- F-140: `ForNode` 包含 `loop_var`（PrimVar）、`min`、`extent`、`kind`（ForKind）、`body`、`thread_binding`（可选 IterVar）、`annotations`、`step`（可选步长，默认为 1） — 源码：`include/tvm/tirx/stmt.h:587-635`
- F-141: `ForNode::HasTrivialStep()` 检查循环是否没有非平凡步长 — 源码：`include/tvm/tirx/stmt.h:632`
- F-142: `WhileNode` 包含 `condition` 和 `body`，类型键为 `"tirx.While"` — 源码：`include/tvm/tirx/stmt.h:662-676`
- F-143: `BreakNode` 和 `ContinueNode` 分别表示 break 和 continue 控制流语句，类型键为 `"tirx.Break"` 和 `"tirx.Continue"` — 源码：`include/tvm/tirx/stmt.h:693-738`
- F-144: `BufferRegionNode` 表示多维缓冲区访问区域，包含 `buffer` 和 `region`（Range 数组），类型键为 `"tirx.BufferRegion"` — 源码：`include/tvm/tirx/stmt.h:743-761`
- F-145: `BufferRegion::FullRegion(buffer)` 静态方法创建覆盖整个缓冲区的 BufferRegion；`FromPoint(buffer, indices)` 创建单点访问区域 — 源码：`include/tvm/tirx/stmt.h:776-784`

### 2.6 SBlock（调度块）

- F-146: `SBlockNode` 继承自 `StmtNode`，是 TensorIR 的核心调度块，包含 `iter_vars`（IterVar 数组）、`reads`（读区域）、`writes`（写区域）、`name_hint`、`alloc_buffers`、`match_buffers`、`annotations`、`init`（可选初始化语句）、`body` — 源码：`include/tvm/tirx/stmt.h:851-892`
- F-147: `SBlockNode` 的 `init` 字段在归约块的第一次迭代时执行，表示初始化逻辑，在非归约块中为 `nullopt` — 源码：`include/tvm/tirx/stmt.h:867-874`
- F-148: `SBlock` 类型键为 `"tirx.SBlock"`，提供两个构造函数：完整参数版本和简化版本（仅 name_hint + body + alloc_buffers） — 源码：`include/tvm/tirx/stmt.h:898-915`
- F-149: `SBlockRealizeNode` 表示块在特定绑定值下的执行，包含 `iter_values`（迭代变量绑定值）、`predicate`（谓词条件）、`block`（被实现的块） — 源码：`include/tvm/tirx/stmt.h:920-940`
- F-150: `SBlockRealizeNode` 的 `predicate` 为 true 时块才执行，类型键为 `"tirx.SBlockRealize"` — 源码：`include/tvm/tirx/stmt.h:925-929,939`
- F-151: `ScopeIdDefStmtNode` 声明作用域 ID 绑定（如 cta_id、warp_id、lane_id），包含 `ScopeIdDef def` 字段，类型键为 `"tirx.ScopeIdDefStmt"` — 源码：`include/tvm/tirx/stmt.h:963-973`

### 2.7 Attr 键常量

- F-152: TIRx 在 `tirx::attr` 命名空间定义了属性键常量，包括 `buffer_bound`（缓冲区边界标记）、`compute_scope`（计算范围标记）、`device_id`（设备 ID）、`device_scope`（设备范围标记）、`device_type`（设备类型）等 — 源码：`include/tvm/tirx/stmt.h:985-999`

### 2.8 PrimFunc

- F-153: `PrimFuncNode` 继承自 `BaseFuncNode`，是包含 TIR 语句的基本函数，包含 `params`（Var 数组）、`ret_type`（返回类型，默认为 Missing）、`buffer_map`（Var→Buffer 映射）、`body`（Stmt） — 源码：`include/tvm/tirx/function.h:49-148`
- F-154: `PrimFuncNode::buffer_map` 提供参数解包和约束检查功能：首次出现的变量定义 Buffer 字段，重复出现转换为运行时断言 — 源码：`include/tvm/tirx/function.h:56-99`
- F-155: `PrimFuncNode::SEqual` 依次比较 attrs、params（递归）、ret_type、buffer_map、body；`SHash` 按相同顺序计算哈希 — 源码：`include/tvm/tirx/function.h:116-136`
- F-156: `PrimFuncNode::func_type_annotation()` 从参数 Vars 直接派生函数类型注解，无需类型推断 — 源码：`include/tvm/tirx/function.h:138-145`
- F-157: `PrimFunc` 类型键为 `"tirx.PrimFunc"`，构造函数参数依次为 params、body、ret_type、buffer_map、attrs、span — 源码：`include/tvm/tirx/function.h:147,174-176`
- F-158: `TensorIntrinNode` 表示张量化内建函数，包含 `desc`（描述计算的 PrimFunc）和 `impl`（实现执行的 PrimFunc），类型键为 `"tirx.TensorIntrin"` — 源码：`include/tvm/tirx/function.h:185-199`

### 2.9 TIRx Op 与内建函数

- F-159: TIRx 提供 `add()`、`sub()`、`mul()`、`div()` 等算术 Op 函数，对索引类型执行立即常量折叠 — 源码：`include/tvm/tirx/op.h`
- F-160: TIRx 提供 `logical_and()`、`logical_or()`、`if_then_else()` 等逻辑 Op 函数 — 源码：`include/tvm/tirx/op.h`
- F-161: TIRx 内建函数（builtin）以 `Op` 形式定义，包括 `ret()`、`thread_return()`、`continue_loop()`、`break_loop()`、位运算函数、`address_of()` 等内存访问函数 — 源码：`include/tvm/tirx/builtin.h`

### 2.10 TIRx Functor 模式

- F-162: `ExprFunctor` 是 TIR 表达式的类型分派访问者基类，支持根据表达式运行时类型调用不同的 VisitExpr 重载 — 源码：`include/tvm/tirx/expr_functor.h:36-287`
- F-163: `ExprVisitor` 继承自 `ExprFunctor`，提供表达式的只读遍历，默认递归访问子表达式 — 源码：`include/tvm/tirx/expr_functor.h`
- F-164: `ExprMutator` 继承自 `ExprFunctor`，提供表达式的可变遍历，默认递归访问并返回变换后的子表达式 — 源码：`include/tvm/tirx/expr_functor.h`
- F-165: `StmtFunctor` 是 TIR 语句的类型分派访问者基类，类似于 ExprFunctor 但针对语句节点 — 源码：`include/tvm/tirx/stmt_functor.h`
- F-166: `StmtVisitor` 继承自 `StmtFunctor`，提供语句的只读遍历 — 源码：`include/tvm/tirx/stmt_functor.h`
- F-167: `StmtMutator` 继承自 `StmtFunctor`，提供语句的可变遍历 — 源码：`include/tvm/tirx/stmt_functor.h`

### 2.11 TIRx 变换 Pass

- F-168: `VectorizeLoop()` Pass 将循环向量化；`StorageRewrite()` Pass 重写存储；`UnrollLoop()` Pass 展开循环 — 源码：`include/tvm/tirx/transform.h`
- F-169: `LowerTVMBuiltin()` Pass 将 TVM 内建函数降级；`LowerTIRx()` Pass 执行 TIRx 整体降级 — 源码：`include/tvm/tirx/transform.h`
- F-170: `CreatePrimFuncPass` 是创建 PrimFunc 级别 Pass 的工具函数（在 s_tir/transform.h 中通过 using 引入） — 源码：`include/tvm/s_tir/transform.h:48`

### 2.12 Layout 与 IndexMap

- F-171: `Layout` 类层次包括基类 `Layout` 及其子类 `TileLayout`、`SwizzleLayout`、`ComposeLayout`，支持 apply、tile、slice 等布局变换操作 — 源码：`include/tvm/tirx/layout.h`
- F-172: `IndexMap` 表示缓冲区索引的重映射，支持 `map_indices`、`map_ranges`、`map_shape` 以及逆映射计算 — 源码：`include/tvm/tirx/index_map.h`

### 2.13 执行上下文与作用域

- F-173: `ScopeKind` 枚举定义了执行作用域层次：`kCluster`、`kCta`、`kWarpgroup`、`kWarp`、`kThread` 等 — 源码：`include/tvm/tirx/exec_scope.h`
- F-174: `ScopeBinding` 表示父子作用域关系，用于管理线程和内存层次 — 源码：`include/tvm/tirx/exec_scope.h`
- F-175: `ActiveSet` 表示活动线程集合，由 `TileLayout` 定义，包含 shard、replica 和 offset 信息 — 源码：`include/tvm/tirx/exec_context.h`
- F-176: `ExecContext` 表示执行上下文，包含活动线程集（ActiveSet）、作用域类型（ScopeKind）和 split 信息，用于调度中追踪线程活动 — 源码：`include/tvm/tirx/exec_context.h`

### 2.14 其他 TIRx 组件

- F-177: `Predicate` 类提供谓词构造和操作功能，用于条件执行 — 源码：`include/tvm/tirx/predicate.h`
- F-178: `async_structs.h` 定义异步 DMA 和同步相关的 TIR 结构 — 源码：`include/tvm/tirx/async_structs.h`
- F-179: `analysis.h` 提供 TIR 分析接口，如缓冲区访问区域检测、依赖分析等 — 源码：`include/tvm/tirx/analysis.h`

---

## 3. S-TIR 调度系统

### 3.1 Schedule 核心类

- F-180: `ScheduleNode` 是调度系统的核心，持有 `state`（ScheduleState）、`trace`（Trace）、`mod`（IRModule）、`func_working_on`（当前工作的 GlobalVar）等成员 — 源码：`include/tvm/s_tir/schedule/schedule.h`
- F-181: `Schedule` 类是用户面向的调度接口，提供循环变换、缓存插入、计算位置管理、张量化等方法 — 源码：`include/tvm/s_tir/schedule/schedule.h`
- F-182: `Schedule` 有两种构造模式：`Concrete()`（无追踪）和 `Traced()`（有追踪），通过 FFI 暴露为 `s_tir.schedule.ConcreteSchedule` 和 `s_tir.schedule.TracedSchedule` — 源码：`src/s_tir/schedule/schedule.cc:72-85`
- F-183: Python 层 `Schedule` 默认使用 `TracedSchedule` 构造（带追踪），`_create_non_traced()` 静态方法使用 `ConcreteSchedule` — 源码：`python/tvm/s_tir/schedule/schedule.py:177-202`
- F-184: Python 层 `Schedule` 构造函数接收 `mod`（PrimFunc 或 IRModule）、`seed`、`debug_mask`、`error_render_level`、`enable_check` 参数 — 源码：`python/tvm/s_tir/schedule/schedule.py:128-184`
- F-185: `error_render_level` 支持三个级别：`"detail"`（0，详细错误）、`"fast"`（1，快速错误）、`"none"`（2，无错误信息） — 源码：`python/tvm/s_tir/schedule/schedule.py:72-85`
- F-186: `ScheduleNode::GetSRef(stmt)` 通过 `stmt2ref` 映射查找语句对应的 StmtSRef，找不到时抛出 IndexError — 源码：`src/s_tir/schedule/schedule.cc:41-48`

### 3.2 随机变量（RV）系统

- F-187: `LoopRV` 是表示循环的随机变量，`SBlockRV` 是表示块的随机变量，`ExprRV` 是表示整数值的随机变量（类型别名为 `Expr`） — 源码：`include/tvm/s_tir/schedule/schedule.h`；Python 层见 `python/tvm/s_tir/schedule/schedule.py:42-68`
- F-188: Python 层 `LoopRV` 和 `SBlockRV` 分别注册为 `"s_tir.LoopRV"` 和 `"s_tir.SBlockRV"` — 源码：`python/tvm/s_tir/schedule/schedule.py:42,53`
- F-189: `RAND_VAR_TYPE` 定义为 `ExprRV | SBlockRV | LoopRV` 的联合类型 — 源码：`python/tvm/s_tir/schedule/schedule.py:70`
- F-190: `Schedule.get()` 方法评估随机变量：SBlockRV→SBlock、LoopRV→For、ExprRV→int（IntImm 自动解包）、StmtSRef→stmt — 源码：`python/tvm/s_tir/schedule/schedule.py:300-325`
- F-191: `Schedule.get_sref()` 方法返回随机变量或语句对应的 StmtSRef — 源码：`python/tvm/s_tir/schedule/schedule.py:327-347`
- F-192: `Schedule.remove_rv()` 从符号表中移除随机变量 — 源码：`python/tvm/s_tir/schedule/schedule.py:349-358`

### 3.3 ScheduleState

- F-193: `ScheduleStateNode` 是调度的核心数据结构，持有 IR module、sref 树、块信息（依赖、标志）、`stmt2ref` 映射和调试设置 — 源码：`include/tvm/s_tir/schedule/state.h`
- F-194: C++ 层 `SMap` 类型别名为使用 `ffi::ObjectPtrHash` 和 `ffi::ObjectPtrEqual` 的 `std::unordered_map` — 源码：`src/s_tir/schedule/state.cc:30-31`
- F-195: `AnalyzeRegionUpperBound()` 在 sref 树路径上分析缓冲区区域的上界，使用 `LoopDomainOfSRefTreePath` 和 `EstimateRegionUpperBound` — 源码：`src/s_tir/schedule/state.cc:44-58`
- F-196: `AnalyzeRegionLowerBound()` 分析缓冲区区域下界，失败时返回全 `IntSet::Nothing()` 的数组 — 源码：`src/s_tir/schedule/state.cc:70-87`
- F-197: `ProducerCoversConsumer()` 检查产生区域是否覆盖消费区域，逐维使用算术分析器证明包含关系 — 源码：`src/s_tir/schedule/state.cc:97-132`
- F-198: `UpdateSRef()` 更新 sref 指向的语句：更新 `stmt2ref` 映射（删除旧条目、添加新条目）并更新 `sref->stmt`，仅允许 SBlockNode 和 ForNode — 源码：`src/s_tir/schedule/state.cc:143-150`
- F-199: `SBlockInfoCollector` 是私有继承自 `StmtVisitor` 的辅助类，用于收集 SBlockInfo，包括 scope、affine_binding、region_cover、stage_pipeline 等标志 — 源码：`src/s_tir/schedule/state.cc:154-200`

### 3.4 Instruction 与 Trace

- F-200: `InstructionKind` 枚举表示调度原语种类（如 Split、Reorder 等），`Instruction` 包含属性、输入、输出和应用函数 — 源码：`include/tvm/s_tir/schedule/instruction.h`
- F-201: `Trace` 记录调度指令和决策序列，提供 apply（应用）、serialize（序列化）、simplify（简化）方法 — 源码：`include/tvm/s_tir/schedule/trace.h`
- F-202: Python 层 `Schedule.trace` 属性返回内部维护的调度追踪 — 源码：`python/tvm/s_tir/schedule/schedule.py:217-219`

### 3.5 调度原语（Sampling）

- F-203: `SampleInt()` 在给定范围内采样随机整数；`SampleWithoutReplacement()` 从 0 到 n-1 中无放回采样 k 个 — 源码：`src/s_tir/schedule/primitive.h:39-49`
- F-204: `SampleCategorical()` 根据候选列表和概率权重进行分类采样，支持决策记录 — 源码：`src/s_tir/schedule/primitive.h:58-61`
- F-205: `MakeMultinomialSampler()` 创建多项式采样函数 — 源码：`src/s_tir/schedule/primitive.h:68-69`
- F-206: `SamplePerfectTile()` 采样完美分块因子，有三个重载版本：接受 extent+n_splits、增加 max_innermost_factor、接受 loop_sref+decision — 源码：`src/s_tir/schedule/primitive.h:77-102`
- F-207: `SamplePartitionedTile()` 采样分区分块因子，第二部分保证 extent 乘积有 `innerpart_factor` 因子 — 源码：`src/s_tir/schedule/primitive.h:118-140`
- F-208: `SampleComputeLocation()` 采样给定块的 compute-at 位置 — 源码：`src/s_tir/schedule/primitive.h:149-152`

### 3.6 调度原语（查询块与循环）

- F-209: `GetSBlocks()` 按名称和函数获取块；`GetLoops()` 获取块的外层循环（从外到内） — 源码：`src/s_tir/schedule/primitive.h:162-170`
- F-210: `GetChildBlocks()` 获取块/循环的叶子块；`GetProducers()` 获取生产者块；`GetConsumers()` 获取消费者块 — 源码：`src/s_tir/schedule/primitive.h:177-191`
- F-211: `GetOutputBlocks()` 获取写入未在 PrimFunc 内分配的输出缓冲区的块 — 源码：`src/s_tir/schedule/primitive.h:200`

### 3.7 调度原语（循环变换）

- F-212: `Split()` 将循环拆分为连续循环列表，要求循环无注解/线程绑定且从 0 开始，支持 `preserve_unit_iters` 和 `disable_predication` 参数 — 源码：`src/s_tir/schedule/primitive.h:216-218`
- F-213: `LoopPartition()` 将循环分区为连续循环列表，要求循环无注解/线程绑定 — 源码：`src/s_tir/schedule/primitive.h:229-231`
- F-214: `Merge()` 合并多个循环为一个，要求循环在同一作用域、无注解/线程绑定、从 0 开始且 extent 相同、LCA 到目标循环间为单分支 — 源码：`src/s_tir/schedule/primitive.h:243`
- F-215: `Fuse()` 将连续循环列表融合为一个，要求循环无注解/线程绑定、内层为外层唯一子节点、从 0 开始、域间无依赖 — 源码：`src/s_tir/schedule/primitive.h:256-257`
- F-216: `Reorder()` 重排循环列表（不要求连续），要求循环在同一链上、外层循环域不依赖内层、块绑定为仿射且迭代变量为数据并行或归约 — 源码：`src/s_tir/schedule/primitive.h:271`
- F-217: `ReorderBlockIterVar()` 重排块内部的迭代变量顺序 — 源码：`src/s_tir/schedule/primitive.h:279-280`
- F-218: `AddUnitLoop()` 在块或循环上方创建新的单位循环（extent=1） — 源码：`src/s_tir/schedule/primitive.h:290`

### 3.8 调度原语（ForKind 操作）

- F-219: `Parallel()` 并行化循环，要求作用域块有 stage-pipeline 属性、块为完整/归约块且仿射绑定、循环仅在数据并行迭代绑定中 — 源码：`src/s_tir/schedule/primitive.h:303`
- F-220: `Vectorize()` 向量化循环，约束与 Parallel 类似 — 源码：`src/s_tir/schedule/primitive.h:314`
- F-221: `Bind()` 将循环绑定到线程轴，threadIdx 轴可绑定数据并行和归约迭代，其他轴仅可绑定数据并行迭代 — 源码：`src/s_tir/schedule/primitive.h:327`
- F-222: `Unroll()` 展开循环，无特殊约束 — 源码：`src/s_tir/schedule/primitive.h:333`

### 3.9 调度原语（缓存阶段）

- F-223: `CacheRead()` 创建读取缓存块，要求作用域内至多一个写入者、作用域块有 stage-pipeline 属性 — 源码：`src/s_tir/schedule/primitive.h:346-348`
- F-224: `CacheWrite()` 创建写入缓存块，要求仅有一个写入者 — 源码：`src/s_tir/schedule/primitive.h:360-362`
- F-225: `ReindexCacheRead()`/`ReindexCacheWrite()` 使用用户自定义 IndexMap 创建重索引缓存 — 源码：`src/s_tir/schedule/primitive.h:376-394`
- F-226: `CacheInplace()` 同时为读/写缓冲区创建缓存块（目标块同时读写该缓冲区） — 源码：`src/s_tir/schedule/primitive.h:406-407`
- F-227: `CacheIndex()` 缓存预计算的索引，cse_thresh 参数确定公共子表达式的重复阈值 — 源码：`src/s_tir/schedule/primitive.h:416-417`
- F-228: `ReIndex()` 创建重索引阶段块，要求仅有一个读/写者且块中仅有一个 buffer load/store — 源码：`src/s_tir/schedule/primitive.h:431-432`

### 3.10 调度原语（数据移动与计算位置）

- F-229: `ReadAt()` 在指定循环位置创建读取缓存；`WriteAt()` 在指定循环位置创建写入缓存 — 源码：`src/s_tir/schedule/primitive.h:436-440`
- F-230: `ComputeAt()` 将生产者块移动到指定循环下，重新生成块诱导的循环，使产生区域覆盖消费区域；支持 index 参数控制插入位置（-1=最后、-2=最前） — 源码：`src/s_tir/schedule/primitive.h:464-465`
- F-231: `ReverseComputeAt()` 将消费者块移动到指定循环下，约束与 ComputeAt 对称 — 源码：`src/s_tir/schedule/primitive.h:486-487`
- F-232: `ComputeInline()` 将完整非根块内联到消费者，要求块仅产生一个缓冲区、不是唯一叶子、body 为简单 BufferStore — 源码：`src/s_tir/schedule/primitive.h:499`
- F-233: `ReverseComputeInline()` 将块内联到唯一生产者，要求块为完整非根块、仅生产消费一个缓冲区 — 源码：`src/s_tir/schedule/primitive.h:512`
- F-234: `FuseReductionEpilogue()` 将 epilogue 块融合到归约块 — 源码：`src/s_tir/schedule/primitive.h:519-520`

### 3.11 调度原语（归约）

- F-235: `DecomposeReduction()` 将归约块分解为 init 块（插入到指定循环前）和 update 块（原块去 init），要求输入为归约块且循环为块的祖先 — 源码：`src/s_tir/schedule/primitive.h:537-538`
- F-236: `RFactor()` 通过指定循环对归约块进行因式分解，`factor_axis` 指定新维度在 rfactor 缓冲区中的位置 — 源码：`src/s_tir/schedule/primitive.h:550`

### 3.12 调度原语（块注解与布局变换）

- F-237: `StorageAlign()` 设置缓冲区特定维度的对齐要求：`stride[axis] == k * factor + offset` — 源码：`src/s_tir/schedule/primitive.h:566-567`
- F-238: `SetScope()` 设置缓冲区的存储范围；`UnsafeSetDType()` 不安全地设置缓冲区数据类型（可能改变正确性） — 源码：`src/s_tir/schedule/primitive.h:576-589`
- F-239: `SetAxisSeparator()` 设置缓冲区的轴分隔符 — 源码：`src/s_tir/schedule/primitive.h:598-600`
- F-240: `Blockize()` 有两个重载：将以循环为根的子树转为块，或将多个块组合为嵌套块 — 源码：`src/s_tir/schedule/primitive.h:611,620-621`
- F-241: `Tensorize()` 使用张量化内建函数替换循环/块的计算，支持块和循环两种目标 — 源码：`src/s_tir/schedule/primitive.h:630-631`
- F-242: `Annotate()`/`Unannotate()` 为块/循环添加/移除键值对注解 — 源码：`src/s_tir/schedule/primitive.h:641-649`
- F-243: `TransformLayout()` 通过 IndexMap 变换缓冲区布局，支持 pad_value 和 `assume_injective_transform`（跳过重叠检查） — 源码：`src/s_tir/schedule/primitive.h:670-673`
- F-244: `TransformBlockLayout()` 通过双射仿射 IndexMap 变换块迭代器和块体，需要逆映射 — 源码：`src/s_tir/schedule/primitive.h:684-685`
- F-245: `DecomposePadding()` 将填充块分解为常量填充块和边界内写入块；`PadEinsum()` 对 Einsum 计算进行填充 — 源码：`src/s_tir/schedule/primitive.h:695-705`
- F-246: `RollingBuffer()` 通过滚动缓冲计算目标缓冲区，选择最外层可滚动轴进行折叠和循环化 — 源码：`src/s_tir/schedule/primitive.h:721`
- F-247: `UnsafeHideBufferAccess()` 隐藏块中的缓冲区访问；`AnnotateBufferAccess()` 通过 IndexMap 注解缓冲区的读写区域 — 源码：`src/s_tir/schedule/primitive.h:731-744`

### 3.13 S-TIR FFI 注册

- F-248: Schedule 的 FFI 方法以 `s_tir.schedule.Schedule*` 命名，通过 `TVM_FFI_STATIC_INIT_BLOCK` 和 `refl::GlobalDef()` 注册 — 源码：`src/s_tir/schedule/schedule.cc:52-63`
- F-249: 调度工具方法 FFI 包括 `ScheduleGetMod`、`ScheduleGetState`、`ScheduleGetTrace`、`ScheduleGetFuncWorkingOn`、`ScheduleCopy`、`ScheduleSeed`、`ScheduleForkSeed`、`ScheduleWorkOn` — 源码：`src/s_tir/schedule/schedule.cc:54-62`
- F-250: 查找类 FFI 方法 `ScheduleGet` 通过 `as<LoopRV>`/`as<SBlockRV>`/`as<ExprRV>` 运行时类型分派到对应重载 — 源码：`src/s_tir/schedule/schedule.cc:93-108`
- F-251: 循环变换 FFI 方法包括 `ScheduleMerge`、`ScheduleFuse`、`ScheduleSplit`、`ScheduleLoopPartition`、`ScheduleReorder`、`ScheduleReorderBlockIterVar`、`ScheduleAddUnitLoop` — 源码：`src/s_tir/schedule/schedule.cc:176-193`
- F-252: ForKind 操作 FFI 方法包括 `ScheduleParallel`、`ScheduleVectorize`、`ScheduleBind`、`ScheduleUnroll` — 源码：`src/s_tir/schedule/schedule.cc:199-202`
- F-253: 缓存阶段 FFI 方法包括 `ScheduleCacheRead`、`ScheduleCacheWrite`、`ScheduleReindexCacheRead`、`ScheduleReindexCacheWrite`、`ScheduleCacheInplace`、`ScheduleCacheIndex`、`ScheduleReIndex` — 源码：`src/s_tir/schedule/schedule.cc:208-218`
- F-254: 计算位置 FFI 方法包括 `ScheduleComputeAt`、`ScheduleReverseComputeAt`、`ScheduleComputeInline`、`ScheduleReverseComputeInline`、`ScheduleFuseReductionEpilogue` — 源码：`src/s_tir/schedule/schedule.cc:231-237`
- F-255: 张量化 FFI `ScheduleTensorize` 通过运行时类型检查支持 SBlockRV 和 LoopRV 两种目标 — 源码：`src/s_tir/schedule/schedule.cc:267-278`
- F-256: 布局变换 FFI 方法接收 `buffer_index_type` 为 int，内部通过 `static_cast<BufferIndexType>` 转换 — 源码：`src/s_tir/schedule/schedule.cc:318-323`

### 3.14 S-TIR 分析与变换

- F-257: `GetSBlockAccessRegion()` 自动检测块的读区域、写区域和不透明区域（三个 BufferRegion 数组） — 源码：`include/tvm/s_tir/analysis.h:50-51`
- F-258: `GetSBlockReadWriteRegion()` 检测块的读写区域，不透明访问同时计为读和写 — 源码：`include/tvm/s_tir/analysis.h:61-62`
- F-259: `DetectBufferAccessLCA()` 检测缓冲区访问的最低公共祖先（LCA），同时处理高级访问（BufferLoad/Store）和低级访问（Load/Store/opaque） — 源码：`include/tvm/s_tir/analysis.h:72`
- F-260: `FindAnchorBlock()` 查找模块的"锚点块"：有 init 语句且 flops 最大的块（如 conv2d） — 源码：`include/tvm/s_tir/analysis.h:88`
- F-261: `EstimateTIRFlops()` 估计 TIR 片段或整个 IRModule 的 FLOPs — 源码：`include/tvm/s_tir/analysis.h:106,113`
- F-262: `IsPureFunction()` 检查函数纯度，`assert_on_error=true` 时对不纯函数抛出错误 — 源码：`include/tvm/s_tir/analysis.h:121`
- F-263: `VerifyGPUCode()` 根据约束字典验证 GPU 代码正确性 — 源码：`include/tvm/s_tir/analysis.h:129`
- F-264: `IdentifyMemCpy()` 识别 For 循环是否语义等价于 MemCpy，返回源和目标 BufferRegion — 源码：`include/tvm/s_tir/analysis.h:142-143`
- F-265: `CalculateAllocatedBytes()` 计算 PrimFunc 或 IRModule 中每个存储范围的分配字节数 — 源码：`include/tvm/s_tir/analysis.h:150-159`
- F-266: `VerifyVTCMLimit()` 验证 VTCM 使用是否在限制内，支持 PrimFunc 和 IRModule 两个重载 — 源码：`include/tvm/s_tir/analysis.h:173,181`
- F-267: S-TIR transform 命名空间提供 `VerifyGPUCode()`、`VerifyVTCMLimit()`、`OOBChecker()` 等 Pass — 源码：`include/tvm/s_tir/analysis.h:193-206`
- F-268: `RenewDefs()` 为 TIR 重新生成定义节点（Var、Buffer、IterVar），相当于深拷贝但行为相同 — 源码：`include/tvm/s_tir/transform.h:44`
- F-269: S-TIR 变换 Pass 包括 `CanonicalizeLoop()`、`LowerCrossThreadReduction()`、`LowerInitBlock()`、`PlanAndUpdateBufferAllocationLocation()`、`ConvertBlocksToOpaque()`、`LiftThreadBinding()` 等 — 源码：`include/tvm/s_tir/transform.h:56-91`
- F-270: `CompactBufferAllocation(is_strict)` Pass 压缩缓冲区访问区域，移除未访问部分，`is_strict=true` 时保证压缩后形状不大于原始形状 — 源码：`include/tvm/s_tir/transform.h:131`
- F-271: `InjectSoftwarePipeline()` Pass 将注解循环转换为流水线循环，使用 `software_pipeline_stage` 和 `software_pipeline_order` 注解，生成 prologue/body/epilogue 三块 — 源码：`include/tvm/s_tir/transform.h:205`
- F-272: 其他 S-TIR Pass 包括 `InjectVirtualThread()`、`InjectDoubleBuffer()`、`HoistIfThenElse()`、`HoistExpression()`、`RenormalizeSplitPattern()`、`RewriteUnsafeSelect()`、`InstrumentBoundCheckers()`、`InjectPTXLDG32()`、`ThreadSync()`、`InferFragment()`、`LowerThreadAllreduce()`、`LowerAsyncDMA()`、`InjectPTXAsyncCopy()`、`MergeSharedMemoryAllocations()`、`DefaultGPUSchedule()`、`DecorateDeviceScope()` 等 — 源码：`include/tvm/s_tir/transform.h:234-368`

---

## 4. Python 绑定层

### 4.1 tvm.ir 模块

- F-273: `python/tvm/ir/__init__.py` 导出 `instrument` 和 `transform` 子模块，以及 `Attrs`、`DictAttrs`、`make_node` 等属性类 — 源码：`python/tvm/ir/__init__.py:21-22`
- F-274: `python/tvm/ir/__init__.py` 从 `.base` 导出 `EnvFunc`、`Node`、`SourceName`、`Span`、`SequentialSpan`、`assert_structural_equal`、`load_json`、`save_json` — 源码：`python/tvm/ir/__init__.py:23-32`
- F-275: Python 层使用 `tvm_ffi.register_object` 装饰器注册对象类型，使用 `__init_handle_by_constructor__` 调用 C++ 构造函数 — 源码：`python/tvm/ir/expr.py:30,59`
- F-276: Python 层 FFI 调用通过 `_ffi_api` 模块进行，如 `_ffi_api.GlobalVar`、`_ffi_api.Call`、`_ffi_api.IRModule` — 源码：`python/tvm/ir/expr.py:59,131`；`python/tvm/ir/module.py:62`
- F-277: Python 层 `PassInfo` 构造函数通过 `_ffi_transform_api.PassInfo` 调用 C++ 实现 — 源码：`python/tvm/ir/transform.py:50-51`
- F-278: Python 层 `PassContext` 通过 `_ffi_transform_api.EnterPassContext`/`ExitPassContext` 管理上下文生命周期 — 源码：`python/tvm/ir/transform.py:109-113`
- F-279: Python 层 `PassContext.list_configs()` 静态方法通过 `_ffi_transform_api.ListConfigs` 列出所有注册的配置选项 — 源码：`python/tvm/ir/transform.py:132-140`

### 4.2 tvm.s_tir 模块

- F-280: `python/tvm/s_tir/__init__.py` 从 `tvm.tirx.function` 导入 `TensorIntrin`，表明 TIRx Python 模块作为 C++ 扩展存在 — 源码：`python/tvm/s_tir/__init__.py:21`
- F-281: `python/tvm/s_tir/__init__.py` 导出 `StmtSRef`、`SBlockScope`、`ScheduleState`、`Schedule`、`ScheduleError`、`Trace` 等核心类 — 源码：`python/tvm/s_tir/__init__.py:32`
- F-282: `python/tvm/s_tir/__init__.py` 导出 `SBlockDependenceInfo`、`SLayout`、`SBijectiveLayout`、`sbijective_layout`、`slayout` — 源码：`python/tvm/s_tir/__init__.py:33-34`
- F-283: `python/tvm/s_tir/__init__.py` 在非 runtime-only 构建中导入 `analysis`、`meta_schedule`、`dlight` 子模块 — 源码：`python/tvm/s_tir/__init__.py:36-39`
- F-284: `renew_defs(func)` 函数通过 `_ffi_api.RenewDefs` 重新生成 TIR 定义节点 — 源码：`python/tvm/s_tir/__init__.py:42-57`
- F-285: Python 层 `Schedule` 使用 `@type_checked` 装饰器进行参数类型检查 — 源码：`python/tvm/s_tir/schedule/schedule.py:128`
- F-286: Python 层 `Schedule.work_on(func_name)` 切换当前调度工作的函数 — 源码：`python/tvm/s_tir/schedule/schedule.py:226-241`
- F-287: Python 层 `Schedule.copy()` 返回调度的深拷贝，保证 SRef 树完全重建、IRModule 不变、所有随机变量在拷贝中有效 — 源码：`python/tvm/s_tir/schedule/schedule.py:243-256`
- F-288: Python 层 `Schedule.seed(seed)` 设置随机种子，`fork_seed()` 返回分叉的随机种子 — 源码：`python/tvm/s_tir/schedule/schedule.py:258-277`
- F-289: Python 层 `Schedule.show()` 同时显示 IRModule 和 Trace 的 TVM 脚本 — 源码：`python/tvm/s_tir/schedule/schedule.py:279-296`
- F-290: Python 层 `Schedule.sample_categorical()`、`sample_perfect_tile()`、`sample_partitioned_tile()`、`sample_compute_location()` 提供采样 API，均通过 `_ffi_api` 调用 C++ 实现 — 源码：`python/tvm/s_tir/schedule/schedule.py:362-478`
- F-291: Python 层 `Schedule.get_sblock(name, func_name)` 按名称获取块，默认在当前工作的函数中搜索 — 源码：`python/tvm/s_tir/schedule/schedule.py:482-499`
- F-292: Python 层 `ScheduleError` 通过 `@register_error` 注册为 TVM 错误类型 — 源码：`python/tvm/s_tir/schedule/schedule.py:37-39`
- F-293: `_parse_seed(seed)` 验证种子范围为 [1, 2147483647]，None 转换为 -1（使用设备随机） — 源码：`python/tvm/s_tir/schedule/schedule.py:94-101`
- F-294: `_get_sblock_default_dtype(block)` 获取块的默认数据类型：优先从 iter_var 获取，其次从 buffer_region 获取，默认为 int64 — 源码：`python/tvm/s_tir/schedule/schedule.py:104-110`

### 4.3 Python 绑定模式总结

- F-295: TVM Python 绑定统一使用 `tvm_ffi` 包（而非旧的 `_ffi`），通过 `register_object` 装饰器建立 Python 类到 C++ 类型键的映射 — 源码：`python/tvm/ir/expr.py:21,30`
- F-296: Python 类通过 `__init_handle_by_constructor__` 特殊方法调用 C++ 构造函数，参数自动通过 FFI 转换 — 源码：`python/tvm/ir/expr.py:59`
- F-297: C++ 端使用 `TVM_FFI_STATIC_INIT_BLOCK()` 宏在静态初始化阶段注册 FFI 函数，通过 `refl::GlobalDef().def()` 或 `.def_method()` 链注册 — 源码：`src/ir/expr.cc:107-112`；`src/s_tir/schedule/schedule.cc:52-63`
- F-298: C++ 端方法注册使用 `def_method("ffi.name", &Class::Method)` 语法，全局函数使用 `def("ffi.name", lambda)` 语法 — 源码：`src/s_tir/schedule/schedule.cc:54-62`
- F-299: Python 层的 `_ffi_api` 模块是自动生成的 FFI 绑定模块，提供类型安全的 Python 到 C++ 调用接口 — 源码：`python/tvm/ir/__init__.py`（`from . import _ffi_api`）
- F-300: Python 层 `tvm.tirx` 模块作为 C++ 编译扩展存在（非纯 Python 包），通过 `from tvm.tirx import Buffer, FloatImm, For, IntImm, PrimFunc, SBlock` 等方式导入 — 源码：`python/tvm/s_tir/schedule/schedule.py:28`
- F-301: Python 层 `tvm.tirx.function` 模块导出 `TensorIntrin` 和 `IndexMap`（通过 `from tvm.tirx.function import IndexMap`） — 源码：`python/tvm/s_tir/schedule/schedule.py:29`
- F-302: S-TIR Python 包结构包含 `schedule/`（调度核心）、`analysis/`、`backend/`、`dlight/`（自动调度）、`meta_schedule/`（元调度）等子模块 — 源码：`python/tvm/s_tir/` 目录结构
- F-303: Python 层 `s_tir.schedule` 子模块包含 `schedule.py`、`state.py`、`trace.py`、`instruction.py`、`analysis.py`、`_type_checker.py`、`_ffi_api.py` 等文件 — 源码：`python/tvm/s_tir/schedule/` 目录结构
- F-304: Python 层 `s_tir.meta_schedule` 子模块包含 builder、cost_model、database、feature_extractor、measure_callback、mutator、post_optimization、postproc、runner、schedule_rule、search_strategy、space_generator、task_scheduler 等组件 — 源码：`python/tvm/s_tir/meta_schedule/` 目录结构
