---
type: Concept
title: Object/Node/ObjectRef 对象系统
description: TVM 基于 TVM-FFI 的 intrusive 引用计数对象系统，涵盖 Object 基类、ObjectRef 智能指针、TypeIndex 类型系统、Node/Ref 双命名约定、COW 变换与结构相等哈希
tags: [tvm, object, node, objectref, intrusive-refcount, cow, type-index, structural-equal, container]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: ir-tir-source
    resource: "/references/ir-tir-source.md"
    title: IR 核心与 TIRx 源码
  - id: tvm-ffi-source
    resource: "/references/tvm-ffi-source.md"
    title: TVM-FFI 跨语言基础源码
---

# Object/Node/ObjectRef 对象系统

TVM 的对象系统建立在 TVM-FFI 提供的 `Object` 基类和 `ObjectRef` 智能指针之上，是整个编译器栈统一的数据模型。从 IR 节点（AddNode/VarNode/PrimFuncNode）到 Pass 基础设施（PassInfoNode/PassContextObj）再到 Runtime 组件（ModuleObj/NDArray），所有跨语言共享的数据类型均遵循同一套对象约定。理解这套系统是阅读和扩展 TVM 源码的基础。

## Object 基类与 intrusive 引用计数

`Object` 是所有堆分配对象的基类，在 C++ 中定义于 `include/tvm/ffi/object.h`，其 C 语言对应结构体为 `TVMFFIObject`（24 字节对象头）[F-020]。每个 Object 实例的前 24 字节布局固定：

| 偏移 | 字段 | 大小 | 说明 |
|------|------|------|------|
| 0 | `combined_ref_count` | 8 字节 | 强/弱引用计数打包（低 32 位强，高 32 位弱） |
| 8 | `type_index` | 4 字节 | 运行时类型索引 |
| 12 | `__padding` | 4 字节 | 对齐填充 |
| 16 | `deleter` | 8 字节 | 析构函数指针 |

这是一种 **intrusive 引用计数**（侵入式引用计数）设计：引用计数字段嵌入对象自身，而非由独立的控制块管理。相比 `std::shared_ptr` 的非侵入式设计，它有以下优势：

- **内存开销小**：无需额外的控制块分配，对象头仅 24 字节。
- **跨语言可观测**：引用计数字段在 C ABI 层可见，任何语言绑定均可直接操作。
- **原子操作高效**：强弱引用计数打包为单个 u64，增减可通过一次原子 fetch_add/fetch_sub 完成 [F-022]。
- **弱引用原生支持**：弱引用归零时才释放内存，强引用归零时先调用析构函数 [F-054]。

强引用（StrongRef）保持对象存活且成员有效；弱引用（WeakRef）保持内存块存活但不保证成员有效。当强引用计数归零时，deleter 以 kDeleterStrong 模式调用析构函数；当弱引用计数也归零时，以 kDeleterWeak 模式释放内存。kDeleterBoth（值 3）表示析构和释放同时进行 [F-054]。

`make_object<T>(args...)` 是创建对象的标准工厂函数，它分配内存、构造对象、返回 `ObjectPtr<T>`。对应 C ABI 为 `TVMFFIObjectNew` [F-030]。

## ObjectRef 智能指针

`ObjectRef` 是所有引用类的基类，内部持有一个 `ObjectPtr<Object>` 数据成员（8 字节指针）。它在构造、拷贝、赋值、析构时自动管理强引用计数，提供 RAII 语义。

TVM 中每个数据类型均由一对类表示，遵循 **Node/Ref 双命名约定**：

| Node 类（数据持有者） | Ref 类（智能指针） | 说明 |
|----------------------|-------------------|------|
| `XxxNode` | `Xxx` | Node 继承 Object，持有数据字段；Ref 继承 ObjectRef，提供类型安全的访问接口 |
| `XxxObj` | `Xxx` | Runtime/FFI 层使用 Obj 后缀，语义与 Node 相同 |

例如：`ExprNode`/`Expr`、`PrimFuncNode`/`PrimFunc`、`IRModuleNode`/`IRModule`、`FunctionObj`/`Function`、`ModuleObj`/`Module`。Ref 类通过 `operator->()` 返回 Node 指针以访问字段，通过 `get()` 获取原始指针，通过 `defined()` 判断是否非空。

`ObjectPtr<T>` 是底层的模板智能指针，直接操作引用计数。`ObjectRef` 内部封装 `ObjectPtr<Object>`，子类 Ref 通过构造时传入具体 Node 类型来保证类型安全。`Downcast<T>(ref)` 和 `ref.as<T>()` 提供运行时向下转型，内部通过 `IsInstance` 检查类型。

## TypeIndex 类型系统

TVM 不依赖 C++ RTTI，而是实现了自定义的运行时类型识别（RTTI）系统。核心机制是 `TypeTable`——一个全局的类型注册表，每个类型在其中占据一个条目，分配一个 `type_index` 整数 [F-035]。

### 类型索引分配

类型索引采用三级分配策略 [F-038]：

1. **静态 POD 区**（0-63）：Any 的栈上小类型，如 None、Int、Float、Bool、DataType、Device、DLTensorPtr、SmallStr 等。这些类型不需要堆分配 [F-042]。
2. **静态对象区**（64-127）：内置对象类型，如 Object、String、Bytes、Error、Function、Shape、Tensor、Array、Map、Module、List、Dict [F-043]。
3. **动态注册区**（≥128）：应用层注册的类型，包括 TVM IR 节点（ExprNode、StmtNode 等）、Pass 类型、TargetKind 等。

### 子类型 O(1) 判定

每个类型可通过 `_type_child_slots` 声明为子类预留的槽位数。子类分配 type_index 时优先使用父类预留槽位。这使得子类型判定只需一次范围比较：

```cpp
bool IsInstanceOf(int32_t self_index, int32_t target_index) {
    return target_index <= self_index &&
           self_index < target_index + type_table[target_index].num_slots;
}
```

无需遍历继承链，即可在 O(1) 时间内完成 `IsInstance<T>()` 检查 [F-024][F-031]。若父类槽位用尽，新子类从动态区分配，此时回退到祖先链遍历。

### 类型注册宏

C++ 端通过一组宏声明和注册类型：

- `TVM_FFI_DECLARE_OBJECT_INFO(TypeName, ParentType)`：声明静态 `_type_index`、`_type_key`、`_type_final`、`_type_child_slots` 等成员。
- `TVM_FFI_REGISTER_OBJECT_TYPE(TypeName)`：在静态初始化阶段调用 `TypeTable::RegisterType`，将类型加入全局注册表。
- `TVM_FFI_OBJECT_TYPE_CHECK`：生成 `IsInstance` 检查逻辑。

`type_key` 是类型的字符串标识（如 `"ir.Expr"`、`"tirx.PrimFunc"`、`"relax.Function"`），在跨语言场景中用于类型查找和错误诊断。Python 端 `register_object` 装饰器将 C++ type_key 映射到 Python 类，实现双向类型关联 [F-084]。

## COW（Copy-on-Write）不可变变换

TVM 的 IR 节点遵循不可变（immutable）设计：Node 对象的字段在构造后不应被直接修改。变换（Mutation）通过 **写时复制**（Copy-on-Write）实现：

1. 调用 `CopyOnWrite(ref)` 获取节点的可变指针。
2. 若引用计数为 1（独占所有权），直接返回原指针。
3. 若引用计数 > 1（共享中），创建原节点的深拷贝，返回拷贝的指针。
4. 通过返回的可变指针修改字段。
5. 修改完成后，Ref 指向（可能新创建的）节点。

这种模式的优势在于：未修改的子树在多个 IR 版本间共享，避免了全树深拷贝的开销；同时保证了 IR 的语义不可变性，使得 Pass 可以安全地缓存和共享中间结果。

`ExprMutator` 和 `StmtMutator` 是 TIR/Relax 层基于 COW 的标准变换基类，它们递归遍历 IR 树，对需要修改的节点调用 CopyOnWrite，对未修改的节点直接返回原引用。

## 结构相等与哈希

TVM 实现了独立于 C++ `operator==` 的结构相等（Structural Equal）和结构哈希（Structural Hash）系统，用于 IR 节点的语义比较和去重。

### SEqualReducer

`SEqualReducer` 是结构相等的归约器，定义于 `include/tvm/ffi/extra/structural_equal.h` [F-175]。它支持五种相等/哈希 kind [F-176]：

| Kind | 行为 |
|------|------|
| `Unsupported` | 不支持结构相等，回退到指针比较 |
| `UniqueInstance` | 每个实例唯一，按指针比较 |
| `ConstTreeNode` | 不可变叶子节点，按内容比较 |
| `DAGNode` | 有向无环图节点，按内容比较并检测循环 |
| `FreeVar` | 自由变量，按名称/标识比较 |

SEqualReducer 维护一个 `equal_map_`（双向 ObjectPtr 映射），在比较过程中记录已配对的对象，支持图结构（而非仅树结构）的相等判定。IRModule 的 SEqual 特别处理 GlobalVar：按名称重映射后比较函数体，确保两个模块中函数定义顺序不同也能判定相等 [F-051]。

### SHashReducer

`SHashReducer` 是结构哈希归约器，定义于 `include/tvm/ffi/extra/structural_hash.h` [F-177]。它维护 `hash_map_` 记录已哈希对象的结果，对 DAG 结构中重复出现的节点返回缓存哈希值。IRModule 的 SHash 先按名称排序函数再依次哈希，确保哈希与函数插入顺序无关 [F-052]。

类型可通过反射系统的 `kSEqual` 和 `kSHash` 类型属性注册自定义相等和哈希逻辑，或通过 `TVM_FFI_REGISTER_REFLECTION_VTABLE` 配置 `SEqualReduce`/`SHashReduce` 方法 [F-174]。

## 反射系统与 VisitAttrs

反射系统使运行时能够遍历和操作对象的字段，无需在每处编写类型特定的序列化/打印/比较代码。核心机制包括：

### 字段注册

每个 Node 类通过 `VisitAttrs(AttrVisitor* v)` 或反射注册表声明其字段。`TVMFFIFieldInfo` 记录每个字段的名称、类型索引、偏移量、getter/setter、标志位和默认值 [F-159]。字段标志位包括：

- `kFieldSetterIsFunctionObj`：setter 是 Function 对象（需 any_pool_ 保活）[F-163]
- `kFieldHasDefault`：字段有默认值（构造时可省略）[F-164]
- `kFieldNotInStructuralHashEqual`：结构相等/哈希中忽略此字段 [F-165]
- `kFieldInDefRegion`：字段进入 def region [F-166]

### AttrVisitor 与 AttrDocGetter

`AttrVisitor` 是经典的访问者模式基类，通过 `v->Visit("field_name", &field)` 逐个访问字段。它被用于：
- 节点的序列化/反序列化
- ReprPrint（类似 `__repr__` 的调试打印）
- DeepCopy（深拷贝）
- 旧版结构相等/哈希

反射系统的 `metadata.creator` 支持通用对象工厂：给定类型索引和字段名→值映射，运行时构造对象实例 [F-162]。这使得 JSON/Protobuf 等跨语言序列化无需为每个类型编写手写代码。

### Dataclass 支持

`dataclass.cc` 基于反射系统为所有注册类型提供通用的 DeepCopy、ReprPrint、RecursiveHash、RecursiveEq [F-171]。递归遍历有最大栈深度限制 `kMaxTraversalStackDepth = 1<<20`（约 100 万），防止恶意构造的深层嵌套对象导致栈溢出 [F-172]。

Python 端 `python/tvm_ffi/dataclasses/` 提供了与 Python dataclass 的互操作，允许用 `@dataclass` 装饰的 Python 类与 C++ 反射字段自动映射。

## 容器类型

FFI 提供的容器类型全部继承自 Object，可被 Any 和 ObjectRef 持有。TVM IR 层在此基础上构建了特定领域的容器：

### 基础容器

| 容器 | 类型 | 说明 |
|------|------|------|
| `Array<T>` | 不可变序列 | 函数式数据结构，COW 修改，下标 O(1) |
| `Map<K,V>` | 不可变有序映射 | 键有序，结构相等按内容比较 |
| `String` | 不可变字符串 | 短字符串内联优化 |
| `Shape` | 不可变 int64 数组 | 用于张量形状 |
| `Bytes` | 不可变字节串 | 二进制数据 |

### IR 特定容器

- **Attrs**：算子属性基类，`DictAttrs` 是 `Map<String, ObjectRef>` 的封装，所有 Relax 算子属性（如 `Conv2DAttrs`）均继承自 Attrs。
- **Type 层次**：`PrimType`、`PointerType`、`TupleType`、`FuncType`、`TensorType` 等，均继承自 `TypeNode`。
- **GlobalVar**：函数的全局符号引用，在 IRModule 中作为函数表的键。

### 容器的 C ABI 表示

序列容器的 C 结构体为 `TVMFFISeqCell`，包含 data 指针、size、capacity 和可选的 data_deleter [F-088]。当 deleter 为 nullptr 时，data 内联在对象内存中（Array 的典型布局）；非 null 时 data 为独立堆分配（List 的可变缓冲区）[F-089]。映射容器的 C 表示使用有序数组 + ForwardIterFunctor 三命令迭代器（取 key、取 value、前进），使迭代器可安全跨越 C ABI 边界 [F-100]。

## Node 命名空间与层次

TVM 的对象类型按模块划分命名空间，通过 type_key 前缀区分：

| type_key 前缀 | 模块 | 示例 |
|---------------|------|------|
| `ir.` | IR 核心 | `ir.Expr`、`ir.Type`、`ir.IRModule`、`ir.PrimFunc` |
| `tirx.` | TIRx | `tirx.For`、`tirx.BufferStore`、`tirx.SBlock` |
| `s_tir.` | S-TIR | `s_tir.Schedule`、`s_tir.Trace` |
| `relax.` | Relax | `relax.Function`、`relax.Var`、`relax.DataflowVar` |
| `runtime.` | Runtime | `runtime.Module`、`runtime.NDArray` |
| `target.` | Target | `target.Target`、`target.TargetKind` |
| `ffi.` | FFI | `ffi.Array`、`ffi.Map`、`ffi.String` |

这种命名空间约定使类型注册表成为可浏览的类型目录，也便于在错误信息和调试输出中快速定位类型所属模块。

## 相关概念

- [TVM-FFI 跨语言基础](/concepts/01-ffi-foundation.md)
- [Pass 基础设施](/concepts/03-pass-infrastructure.md)
- [TVM 整体架构与编译流水线](/concepts/00-overview.md)
