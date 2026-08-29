---
type: Concept
title: TVMScript DSL
description: TVMScript Python 嵌入式 DSL，涵盖 IRBuilder 分层架构、TIR/Relax 方言、Doc 打印体系、Python 装饰器及代码生成与解析机制
tags: [tvm, tvmscript, dsl, python, ir-builder, printer, tir, relax]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
  - id: ir-tir-source
    resource: "/references/ir-tir-source.md"
    title: IR/TIR 源码
  - id: relax-te-topi-source
    resource: "/references/relax-te-topi-source.md"
    title: Relax/TE/TOPI 源码
---

# TVMScript DSL

TVMScript 是 TVM 的 Python 嵌入式领域特定语言（Embedded DSL），允许开发者使用 Python 语法直接编写 TIR 和 Relax IR。它既是 IR 的**人类可读文本表示**（用于打印、调试和序列化），也是**IR 构建接口**（用于以编程方式构造 IR）。TVMScript 将编译器 IR 的表达能力与 Python 的生态和易用性结合，使开发者无需接触 C++ API 即可定义高性能张量程序和神经网络模型。

## 设计目标

TVMScript 的设计追求以下目标：

1. **Python 语法原生感**：TVMScript 程序是合法的 Python 代码，可使用 Python 工具链（编辑器、调试器、linter）编辑。
2. **双向转换**：IR 节点可打印为 TVMScript 文本，TVMScript 文本可解析回 IR 节点，实现无损往返。
3. **多方言支持**：同一套基础设施支持 TIR（张量级 IR）和 Relax（图级 IR）两种方言，并可扩展。
4. **增量构建**：通过 IRBuilder 以命令式方式逐步构建 IR，也可通过装饰器以声明式方式整体定义。

## IRBuilder 分层架构

IR Builder 头文件位于 `include/tvm/script/ir_builder/`，实现位于 `src/script/ir_builder/` [F-331][F-332]。IRBuilder 采用**分层架构**，为不同 IR 方言提供专用构建器 [F-333]：

### TIR IRBuilder

TIR 方言的 IRBuilder 提供构建 TIR 节点的 API，包括：

- **PrimFunc 构建**：函数参数、Buffer 声明、函数体。
- **语句构建**：For 循环、IfThenElse、Block、Allocate、AttrStmt 等。
- **表达式构建**：算术运算、BufferLoad/BufferStore、Call、Select 等。
- **SBlock 构建**：迭代变量声明、读写区域声明、块属性注解。
- **调度构建**：通过 `tirx.schedule` 命名空间执行调度原语。

TIR IRBuilder 内部维护帧栈（frame stack），每进入一个作用域（如函数、块、循环）压入新帧，退出时弹出并生成对应 IR 节点。

### Relax IRBuilder

Relax 方言的 IRBuilder 与 BlockBuilder 协作，提供构建 Relax IR 的 Pythonic API：

- **函数构建**：通过 `@R.function` 装饰器定义 Relax 函数。
- **数据流构建**：使用 `with R.dataflow()` 进入数据流块。
- **算子调用**：直接调用 `R.op.nn.conv2d`、`R.add` 等算子函数。
- **匹配铸造**：`R.match_cast()` 处理动态形状。
- **数据绑定**：`lv = R.emit(expr)` 发射绑定，`gv = R.emit_output(lv)` 声明输出。

Relax 方言注册通过 `tvm.script.register_dialect("relax", "tvm.relax.script")` 完成 [F-237]。

### 核心 IRBuilder 机制

IRBuilder 的核心机制包括：

1. **帧栈（Frame Stack）**：维护嵌套作用域的状态，每个 frame 对应一个 IR 作用域（函数、块、循环、数据流块等）。
2. **隐式上下文**：当前活跃的 Builder 存储在线程局部变量中，API 调用无需显式传递 Builder。
3. **值与表达式的自动转换**：Python 整数/浮点数自动转换为 IntImm/FloatImm，Python 列表/元组自动转换为 Array。
4. **作用域守卫**：`with` 语句确保作用域正确进入和退出，异常安全。

## Printer / Doc 体系

### Script 入口函数

`Script(node, config)` 自由函数声明在 `include/tvm/script/printer/printer.h`，是 TVMScript 打印的入口 [F-325]。对于未注册到 TVMScriptPrinter 的类型，回退到 `ffi::ReprPrint` [F-326]。

### TVMScriptPrinter

`TVMScriptPrinter` 类使用 `NodeFunctor<std::string(const ffi::ObjectRef&, const PrinterConfig&)>` 作为分发表类型 [F-327]。`TVMScriptPrinter::vtable()` 静态方法返回分发表引用，各方言打印机通过它注册对象类型打印函数 [F-328]。

`TVM_REGISTER_SCRIPT_AS_REPR(ObjectType, Method)` 宏同时注册 Script 为 ObjectType 的 kRepr 回调并安装分发表条目 [F-329]。这使得在 Python 中直接输出 IR 对象时自动以 TVMScript 格式显示。

### Doc 中间表示

Doc 体系实现在 `src/script/printer/doc.cc`，是 TVMScript 打印的中间表示 [F-335]。打印过程分为两个阶段：

1. **IR → Doc**：IR 节点被转换为结构化的 Doc 对象树（如 ExprDoc、StmtDoc、FunctionDoc）。Doc 抽象掉了具体的 Python 语法细节，只保留程序结构。
2. **Doc → 文本**：Doc 树被渲染为最终的 TVMScript 文本，处理缩进、换行和运算符优先级。

Doc 体系的设计带来以下优势：
- **方言无关**：不同方言的 IR 可生成不同 Doc，但共享同一渲染器。
- **可转换性**：Doc 树可在渲染前被变换（如变量重命名、注释附加）。
- **一致性**：统一处理引号、转义和格式化规则。

### PrinterConfig

`PrinterConfig` 定义在 `config.h` 中 [F-330]，控制打印行为，包括：
- 缩进宽度。
- 是否打印行号和 span 信息。
- 变量命名策略（保留名称或自动生成）。
- 是否使用简洁语法糖。
- 方言特定选项。

## Python 装饰器

TVMScript 使用 Python 装饰器标记函数为 IR 定义：

### TIR 装饰器

```python
@tvm.script.tirx.prim_func
def func(A: T.Buffer((128, 128), "float32"), B: T.Buffer((128, 128), "float32")):
    for i in range(128):
        for j in range(128):
            B[i, j] = A[i, j] * 2.0
```

- `@tvm.script.tirx.prim_func`（或 `@T.prim_func`）：将 Python 函数解析为 TIR PrimFunc。
- 类型注解（`T.Buffer(...)`）声明 Buffer 的形状和 dtype。
- 函数体使用 TIR 方言的 Python 语法子集编写。

### Relax 装饰器

```python
@tvm.script.ir_module
class MyModule:
    @R.function
    def main(x: R.Tensor((1, 3, 224, 224), "float32")):
        with R.dataflow():
            lv = R.op.nn.relu(x)
            gv = R.emit_output(lv)
        return gv
```

- `@tvm.script.ir_module`：将 Python 类解析为 IRModule，类方法为模块中的函数。
- `@R.function`：标记方法为 Relax 函数。
- `R.Tensor(shape, dtype)`：类型注解声明张量类型。
- `with R.dataflow()`：进入数据流块。

## 代码生成与解析

### 解析流程（Python → IR）

TVMScript 程序的解析发生在 Python 解释器执行装饰器函数时：

1. **装饰器拦截**：`@tvm.script.tirx.prim_func` 装饰器拦截函数定义，不立即执行函数体。
2. **IRBuilder 激活**：创建对应方言的 IRBuilder 并设为当前上下文。
3. **函数体执行**：执行原始 Python 函数体，但函数内的操作（循环、索引、赋值）被 IRBuilder 的魔术方法拦截。
   - `for i in range(n)` 被转换为 For 节点。
   - `B[i, j] = expr` 被转换为 BufferStore。
   - `if cond` 被转换为 IfThenElse。
4. **帧栈弹出**：函数体执行完毕，IRBuilder 从帧栈生成完整 IR 节点。
5. **类型处理**：函数注解和返回类型被解析为 IR 类型节点。
6. **返回 IR**：装饰器返回构造好的 IR 对象（PrimFunc 或 IRModule）。

### 打印流程（IR → Python 文本）

1. **调度**：`Script()` 函数根据对象类型查找 TVMScriptPrinter vtable 中的打印函数。
2. **Doc 生成**：打印函数遍历 IR 节点树，生成对应的 Doc 对象。
3. **规范化**：变量名去重、类型注解简化、公共子表达式命名。
4. **渲染**：Doc 树渲染为带缩进的 Python 语法文本。
5. **方言前缀**：TIR 方言使用 `T.` 前缀，Relax 方言使用 `R.` 前缀。

### 往返一致性

TVMScript 保证打印出的代码可被重新解析为语义相同的 IR。这一性质对于以下场景至关重要：

- **调试**：打印 IR 检查中间结果，修改文本后重新加载。
- **测试**：以 TVMScript 文本编写测试用例，易于版本控制和 review。
- **序列化**：TVMScript 可作为人类可读的序列化格式（二进制序列化另行处理）。
- **教学文档**：以可执行的代码示例展示 IR 结构。

## TVMScript 与 BlockBuilder/IRBuilder 的关系

TVMScript 是 IRBuilder 的 Python 前端：

- **TIR**：TVMScript 的 `@T.prim_func` 内部使用 TIR IRBuilder 构建 PrimFunc。
- **Relax**：TVMScript 的 `@R.function` 内部使用 Relax BlockBuilder 构建函数。BlockBuilder 的 `Emit`、`EmitMatchCast`、`BeginDataflowBlock` 等方法由 `R.emit()`、`R.match_cast()`、`with R.dataflow()` 等 TVMScript API 封装。

用户可以选择：
- **声明式**：使用装饰器整体定义 IR（适合手写和阅读）。
- **命令式**：直接调用 IRBuilder/BlockBuilder API 增量构建（适合代码生成和自动转换）。

## Python 端命名空间

Python 端 `tvm.script` 包通过 `python/tvm/script/__init__.py` 导出 [F-334]，主要组件包括：

- `tvm.script.tir` / `tvm.script.relax`：方言装饰器。
- `tvm.script.ir_module`：IRModule 类装饰器。
- `T`（tir）、`R`（relax）：方言命名空间，提供类型注解、算子和构建函数。
- `tvm.script.Script`：打印入口函数。

## 禁用算子特定归一化

在 BlockBuilder 中有一个特殊的标记结构体 `DisableOperatorSpecificNormalizationForTVMScript`，用于禁用 FNormalize [F-53]。这是因为 TVMScript 作为源码表示，需要精确保留用户编写的形式：当 TVMScript 解析器构建 IR 时，不应在构建过程中触发算子归一化（否则打印出的 IR 可能与用户编写的不同，破坏往返一致性）。该标记仅供 TVMScript 解析器使用。

## 在 TVM 生态中的角色

TVMScript 贯穿 TVM 的开发和使用流程：

1. **算子开发**：开发者使用 TVMScript 编写 TIR PrimFunc 和调度。
2. **Pass 开发**：Pass 的测试用例以 TVMScript 文本编写输入和期望输出。
3. **调试**：`mod.show()` 或 `print(mod)` 以 TVMScript 格式显示 IR。
4. **模型定义**：使用 Relax 方言直接定义神经网络模型。
5. **教学和文档**：TVMScript 代码示例是 TVM 文档的主要表达方式。
6. **自动调优**：MetaSchedule 生成的调度可序列化为 TVMScript 格式的 `tirx.Schedule` 规则。

## 设计要点

TVMScript 的设计体现了以下原则：

1. **嵌入式而非外部语言**：TVMScript 是合法 Python，无需自定义解析器，享受 Python 生态。但 IRBuilder 在执行时拦截语义，将 Python 控制流转换为 IR 节点。
2. **打印即解析**：Doc 体系和分发表机制确保打印和解析对称，支持可靠往返。
3. **多方言统一框架**：TIR 和 Relax 方言共享 IRBuilder 和 Printer 基础设施，新方言只需注册自己的帧和打印函数。
4. **渐进式类型**：类型注解既可作为 IR 的类型信息，也可被 Python 类型检查器利用。
5. **保真与归一化平衡**：TVMScript 解析时禁用算子特定归一化以保源码保真，编译期 Normalize Pass 再做归一化，职责分离。

## 相关概念

- [TIRx 中间表示](/concepts/05-tirx-ir.md) — TVMScript 的 TIR 方言用于直接编写 PrimFunc、Buffer、For 循环等张量级 IR
- [Relax 图级 IR](/concepts/11-relax-ir.md) — TVMScript 的 Relax 方言用于定义神经网络模型的图级函数和数据流块
- [BlockBuilder 与 Dataflow](/concepts/12-relax-block-builder.md) — TVMScript Relax 方言底层通过 BlockBuilder 的 Emit/DataflowScope 构建 IR
- [SBlock 声明式调度](/concepts/07-sblock-schedule.md) — TVMScript 可表达 TIR 调度规则，与 Schedule/Trace 机制协同
- [Pass 基础设施](/concepts/03-pass-infrastructure.md) — TVMScript 是 Pass 单元测试用例的标准输入输出格式，支持打印-解析往返验证
