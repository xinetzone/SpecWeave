# Examples 索引

本目录包含 Apache TVM 的实践示例，帮助开发者快速上手 TVM 的核心功能。

## 示例列表

| 示例 | 说明 | 涵盖主题 |
|------|------|---------|
| [TVM 快速入门](tvm-quickstart.md) | 通过矩阵乘法示例演示完整的 TVM 工作流 | TE 张量表达式、TVMScript、编译构建、Runtime 执行 |

## 按主题分类

### 入门与基础

- [TVM 快速入门](tvm-quickstart.md)：从定义计算到编译运行的端到端示例，适合第一次接触 TVM 的开发者。

### 核心工作流

快速入门示例涵盖以下 TVM 核心工作流：

1. **计算定义**：使用 `te.placeholder` 和 `te.compute` 声明张量计算。
2. **IR 生成**：通过 `te.create_prim_func` 将 TE 计算降级为 TIR PrimFunc。
3. **TVMScript**：使用 `@tvm.script.tirx.prim_func` 装饰器以 Python 语法直接编写 TIR。
4. **编译**：使用 `tvm.compile` 针对目标后端（LLVM/CUDA 等）编译。
5. **执行**：通过 Runtime Module 的 `ffi::Function` 接口在设备上运行。
6. **验证**：将 TVM NDArray 转换为 NumPy 数组进行结果比对。

## 前置知识

阅读示例前建议先了解以下概念文档：

- [架构总览](/concepts/00-overview.md)：TVM 四层栈架构。
- [TE 张量表达式](/concepts/15-te-tensor-expression.md)：TE DSL 的设计与用法。
- [TIRx 中间表示](/concepts/05-tirx-ir.md)：TIR 的节点体系。
- [Runtime Module 系统](/concepts/17-runtime-module.md)：Module 与 `ffi::Function` 调用约定。

## 运行环境

示例代码基于 TVM 0.26.dev0 版本，需要：

- Python 3.x
- NumPy
- TVM Python 包（`import tvm`）

GPU 示例需要对应的硬件和驱动（CUDA/Metal/OpenCL/Vulkan），快速入门默认使用 CPU（LLVM 后端）。

```{toctree}
:maxdepth: 2

tvm-quickstart
```