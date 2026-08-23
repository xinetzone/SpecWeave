---
type: Example
title: TVM 快速入门
description: 通过矩阵乘法示例演示 TVM 的 TE 张量表达式定义、TVMScript TIR 编写、编译构建和运行时执行完整流程
tags: [tvm, example, quickstart, te, tvmscript, compile, runtime, matrix-multiplication]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-ir-tir
    resource: "/references/facts-ir-tir.md"
    title: IR/TIR 事实清单
  - id: facts-relax-te-topi
    resource: "/references/facts-relax-te-topi.md"
    title: Relax/TE/TOPI 事实清单
  - id: facts-runtime-target-arith
    resource: "/references/facts-runtime-target-arith.md"
    title: Runtime/Target/Arith 事实清单
---

# TVM 快速入门

本示例通过矩阵乘法（Matrix Multiplication）演示 TVM 的核心使用流程：使用 TE（Tensor Expression）定义计算、通过 TVMScript 直接编写 TIR PrimFunc、编译构建以及在 Runtime 上执行。所有 API 均来自事实文件中确认的接口。

## 环境要求

- TVM 0.26.dev0 或兼容版本（版本号定义于 `include/tvm/runtime/base.h`）。
- Python 3.x。
- NumPy（用于结果验证）。

## 方式一：使用 TE 定义矩阵乘法

TE 是 TVM 的声明式张量计算 DSL。用户描述输出张量每个元素如何计算，TVM 自动生成循环嵌套和 TIR PrimFunc。

### 步骤 1：导入模块

```python
import tvm
from tvm import te
import numpy as np
```

`te` 命名空间导出 `placeholder`、`compute`、`reduce_axis`、`create_prim_func` 等组件及所有 TIR 内建函数 [F-193]。

### 步骤 2：定义符号形状和占位符

```python
M, K, N = 1024, 1024, 1024

A = te.placeholder((M, K), name="A", dtype="float32")
B = te.placeholder((K, N), name="B", dtype="float32")
```

`te.placeholder()` 默认 dtype 为 `"float32"`，内部调用 `_ffi_api.Placeholder` 创建占位张量 [F-190]。PlaceholderOp 是计算图的输入节点，没有输入 [F-177]。

### 步骤 3：声明归约轴和计算

```python
k = te.reduce_axis((0, K), name="k")

C = te.compute(
    (M, N),
    lambda i, j: te.sum(A[i, k] * B[k, j], axis=k),
    name="C",
)
```

`te.compute()` 接受 `shape`、`fcompute`、`name` 等参数，通过 Python 反射解析 fcompute 的参数列表，自动为每个维度创建 IterVar [F-191]。`te.reduce_axis` 创建归约迭代变量 [F-193]，`te.sum` 是 TIR 内建归约函数。ComputeOp 的 body 字段存储每个输出元素的计算公式 [F-180]。

### 步骤 4：创建 TIR PrimFunc

```python
prim_func = te.create_prim_func([A, B, C])
```

`create_prim_func` 是 TE→TIR 降级的入口，将 Tensor/Operation 图转换为包含参数列表、Buffer 映射和循环嵌套函数体的 TIR PrimFunc [F-193]。降级过程通过 `ProducerToBufferTransformer` 将 ProducerLoad 转换为 BufferLoad [F-186]。

### 步骤 5：调度优化（可选）

TE 生成的 PrimFunc 使用默认调度。可通过调度原语优化性能：

```python
s = te.create_schedule(C.op)

i, j = s[C].op.axis
io, ii = s[C].split(i, factor=32)
jo, ji = s[C].split(j, factor=32)
s[C].reorder(io, jo, ii, ji)
s[C].parallel(io)
s[C].vectorize(ji)

prim_func = te.create_prim_func([A, B, C])
```

（注：`create_schedule` 是 TE 的标准调度创建接口，与 `create_prim_func` 协同工作。）

## 方式二：使用 TVMScript 直接编写 TIR

TVMScript 允许以 Python 语法直接编写 TIR PrimFunc，适用于需要精确控制循环结构和内存访问的场景。

```python
@tvm.script.tirx.prim_func
def matmul(
    A: tirx.Buffer((1024, 1024), "float32"),
    B: tirx.Buffer((1024, 1024), "float32"),
    C: tirx.Buffer((1024, 1024), "float32"),
):
    for i in range(1024):
        for j in range(1024):
            for k in range(1024):
                with tirx.sblock("C"):
                    vi = tirx.axis.spatial(1024, i)
                    vj = tirx.axis.spatial(1024, j)
                    vk = tirx.axis.reduce(1024, k)
                    with tirx.init():
                        C[vi, vj] = tirx.float32(0)
                    C[vi, vj] = C[vi, vj] + A[vi, vk] * B[vk, vj]
```

`@tvm.script.tirx.prim_func` 装饰器将 Python 函数解析为 TIR PrimFunc。函数体中的 `for` 循环被转换为 For 节点，`tirx.sblock` 创建声明式 SBlock，`tirx.axis.spatial`/`tirx.axis.reduce` 声明迭代变量类型，`tirx.init` 标记归约初始化块。

## 编译构建

### 方式 A：使用 `tvm.compile`（推荐）

`tvm.compile` 是统一的编译入口函数 [F-340]，自动检测模块类型：若包含 Relax 函数则路由到 `tvm.relax.build`，否则调用 `tvm.tirx.build` [F-342]。

```python
target = "llvm"

lib = tvm.compile(prim_func, target=target)
```

`compile` 函数接收 `mod`（PrimFunc 或 IRModule）、`target`、`relax_pipeline`（默认 `"default"`）和 `tir_pipeline`（默认 `"default"`）参数 [F-341]。对于 TIR-only 模块，编译结果包装为 Executable 对象返回 [F-343]。

Target 可从字符串构造，纯字符串（如 `"llvm"`、`"cuda"`）被视为 kind 名称 [F-116]。

### 方式 B：使用 `tvm.tirx.build`

```python
lib = tvm.tirx.build(prim_func, target="llvm")
```

`tvm.build` 函数已标记为废弃，内部直接委托给 `tvm.tirx.build` [F-338][F-339]。新代码应使用 `tvm.compile` 或 `tvm.tirx.build`。

### 构建流程

`codegen::Build(mod, target)` 是代码生成的统一入口 [F-161]，通过查找全局函数 `"target.build." + target->kind->name` 分派到具体后端 [F-162]。LLVM 目标种类默认设备类型为 kDLCPU [F-136]，生成的代码通过 CodeGenCPU（继承自 CodeGenLLVM）编译为机器码 [F-180]。

## 运行时执行

### 步骤 1：创建设备上的输入张量

```python
device = tvm.cpu()

a_np = np.random.randn(M, K).astype(np.float32)
b_np = np.random.randn(K, N).astype(np.float32)

a_tvm = tvm.nd.array(a_np, device=device)
b_tvm = tvm.nd.array(b_np, device=device)
c_tvm = tvm.nd.empty((M, N), dtype="float32", device=device)
```

`tvm.cpu()` 是便捷设备构造函数之一 [F-28]。`tvm.nd.array` 从 NumPy 数组创建 NDArray，`tvm.nd.empty` 创建指定形状和类型的空张量 [F-27]。NDArray 内部通过 DeviceAPI 的 `AllocDataSpace` 分配设备内存 [F-9]。

### 步骤 2：获取并调用函数

```python
func = lib["main"]
func(a_tvm, b_tvm, c_tvm)
```

Module 通过 `GetFunction(name)` 按名称查找函数，返回 `ffi::Function`。调用时参数通过 `ffi::PackedArgs` 传递，TVM 运行时自动处理 NDArray 参数 [F-31]。函数名通常是 PrimFunc 的 `global_symbol` 属性值，默认为 `"main"`。

CPU 后端生成的代码通过线程池并行执行 TIR 中的 `parallel` 循环 [F-51]。

### 步骤 3：验证结果

```python
c_np = a_np @ b_np
np.testing.assert_allclose(c_tvm.numpy(), c_np, rtol=1e-5, atol=1e-5)
print("矩阵乘法结果验证通过！")
```

`c_tvm.numpy()` 将设备张量拷贝回主机并转换为 NumPy 数组，底层调用 DeviceAPI 的 `CopyDataFromTo` 完成跨设备数据传输 [F-11]。

## 完整代码：TE + 编译 + 运行

```python
import tvm
from tvm import te
import numpy as np

# 1. 定义计算
M, K, N = 512, 512, 512
A = te.placeholder((M, K), name="A", dtype="float32")
B = te.placeholder((K, N), name="B", dtype="float32")
k = te.reduce_axis((0, K), name="k")
C = te.compute(
    (M, N),
    lambda i, j: te.sum(A[i, k] * B[k, j], axis=k),
    name="C",
)

# 2. 创建 PrimFunc 并编译
prim_func = te.create_prim_func([A, B, C])
lib = tvm.compile(prim_func, target="llvm")

# 3. 准备数据
device = tvm.cpu()
a_np = np.random.randn(M, K).astype("float32")
b_np = np.random.randn(K, N).astype("float32")
a_tvm = tvm.nd.array(a_np, device=device)
b_tvm = tvm.nd.array(b_np, device=device)
c_tvm = tvm.nd.empty((M, N), dtype="float32", device=device)

# 4. 执行
lib["main"](a_tvm, b_tvm, c_tvm)

# 5. 验证
c_np = a_np @ b_np
np.testing.assert_allclose(c_tvm.numpy(), c_np, rtol=1e-5)
print("验证通过")
```

## 关键 API 索引

| API | 事实编号 | 说明 |
|-----|---------|------|
| `te.placeholder()` | F-190 | 创建输入占位张量 |
| `te.compute()` | F-191 | 声明式张量计算 |
| `te.reduce_axis()` | F-193 | 创建归约迭代轴 |
| `te.create_prim_func()` | F-193 | TE→TIR 降级 |
| `tvm.compile()` | F-340 | 统一编译入口 |
| `tvm.tirx.build()` | F-339 | TIR 编译入口 |
| `tvm.cpu()` | F-28 | CPU 设备构造 |
| `tvm.nd.array()` | F-27 | 创建 NDArray |
| `tvm.nd.empty()` | F-27 | 创建空张量 |
| `lib["main"]` | F-31 | Module 获取 ffi::Function |
| `@tvm.script.tirx.prim_func` | F-331 | TIR TVMScript 装饰器 |

## 延伸阅读

- [TE 张量表达式](/concepts/15-te-tensor-expression.md)：TE 计算 DSL 的完整概念文档。
- [TIRx 中间表示](/concepts/05-tirx-ir.md)：TIR 表达式与语句节点体系。
- [调度原语](/concepts/08-schedule-primitives.md)：循环变换和缓存原语详解。
- [Runtime Module 系统](/concepts/17-runtime-module.md)：Module、ffi::Function 和 DeviceAPI。
- [Target 与代码生成](/concepts/04-target-codegen.md)：多后端编译机制。
