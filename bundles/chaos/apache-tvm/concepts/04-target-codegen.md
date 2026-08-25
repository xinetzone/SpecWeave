---
type: Concept
title: Target 与代码生成
description: TVM Target 多后端描述系统与代码生成框架，涵盖 TargetKind 注册、TargetTag 预设配置、CodeGenLLVM/CodeGenC 后端层次、GPU 后端适配、Module 导入树及 driver.build_module 编译入口
tags: [tvm, target, codegen, llvm, cuda, metal, vulkan, module, driver]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
---

# Target 与代码生成

Target 系统是 TVM 连接编译优化与硬件执行的桥梁。它描述目标设备的架构特性（指令集、线程模型、内存层次、向量化宽度等），指导 Pass 选择优化策略，并驱动代码生成器将 TIR PrimFunc 翻译为可在目标设备上执行的机器码或源码。TVM 的代码生成框架以 LLVM 和 C 源码为两大基础后端，在此之上派生 x86/AArch64 CPU 后端和 CUDA/Metal/OpenCL/Vulkan/ROCm 等 GPU 后端。

## Target / TargetKind / TargetTag

### TargetNode：目标设备描述

`TargetNode` 定义于 `include/tvm/target/target.h`，是描述一个编译目标的不可变对象，包含以下核心字段 [F-117]：

| 字段 | 类型 | 说明 |
|------|------|------|
| `kind` | TargetKind | 目标种类（llvm/cuda/metal/opencl/vulkan/c 等） |
| `host` | Target | 主机端目标（用于设备代码的主机侧包装） |
| `tag` | String | 预设标签（如 "nvidia/nvidia-a100"） |
| `keys` | Array<String> | 目标特性键列表（如 ["cuda", "gpu"]） |
| `attrs` | Map<String, ObjectRef> | 目标属性（max_num_threads、thread_warp_size 等） |

Target 提供线程局部上下文栈，Pass 在执行期间可通过 `Target::Current()` 获取当前目标，据此决定优化策略（如循环展开阈值、向量化宽度、共享内存大小）[F-119]。Python 端支持上下文管理器：

```python
with tvm.target.Target("cuda -arch=sm_80"):
    lib = tvm.build(mod, target="cuda")
```

Target 可从三种形式构造：
1. **字符串**：如 `"llvm -mtriple=aarch64-linux-gnu -mattr=+neon"`，解析 kind 和属性。
2. **字典**：如 `{"kind": "cuda", "arch": "sm_80", "max_threads_per_block": 1024}`。
3. **Tag**：如 `"nvidia/gtx-1080"`，查找预定义配置。

### TargetKind：后端种类注册表

`TargetKindNode` 定义于 `include/tvm/target/target_kind.h`，描述一类目标设备的通用信息 [F-120]：

| 字段 | 说明 |
|------|------|
| `name` | 种类名称（"llvm"、"cuda"、"c" 等） |
| `default_device_type` | 默认 DLDeviceType（kDLCPU/kDLCUDA/kDLMetal 等） |
| `default_keys` | 默认特性键 |
| `schema_` | 该 kind 支持的属性 schema（JSON Schema） |

每个 TargetKind 通过 `TVM_REGISTER_TARGET_KIND(name, device_type)` 宏在静态初始化阶段注册 [F-121]。注册时可通过 `.set_attr_parser()` 设置属性解析器，通过 `.add_attr_option<T>()` 声明支持的属性选项。框架内置注册的 kind 包括：

- **LLVM 系**：llvm（统一入口，根据 mtriple 自动选择 CPU 架构）
- **C 源码系**：c（C 源码，主机侧）、cuda、metal、opencl、vulkan、rocm
- **特殊**：composite（复合目标，用于 BYOC 外部代码生成）、stackvm、ext_dev

TargetKind 的注册表是一个全局 `Map<String, TargetKind>`，通过 `TargetKind::Get(name)` 查找。这种注册机制使新后端只需注册一个 TargetKind 和对应的 `"target.build.<kind>"` 全局函数即可接入编译流水线。

### TargetTag：预设配置

TargetTag 系统为常见硬件设备提供命名预设配置。`AddTag(name, config)` 注册一个标签到目标配置的映射，`GetConfig(name)` 查找配置，`ListTags()` 列出所有可用标签 [F-124]。标签命名通常采用 `<厂商>/<设备名>` 格式，如 `"nvidia/nvidia-a100"`、"`arm/cortex-a76`"。

使用 tag 构造 Target 时，框架自动填充该设备的已知属性（计算能力、核心数、缓存大小等），用户只需覆盖特定选项。这避免了每次编译都手动指定大量硬件参数。

### VirtualDevice

`VirtualDevice` 是对 Target 的补充，描述张量在编译期和运行期的放置位置，是一个四元组 [F-125]：

```text
(device_type, device_id, target, memory_scope)
```

其中 `memory_scope` 指定张量所在的内存层级（如 "global"、"shared"、"local"、"warp"）。VirtualDevice 在 Relax 的 StaticPlanBlockMemory Pass 和 TIR 的 Buffer 内存规划中使用，使编译器能够根据目标设备的内存层次进行优化。

## CodeGenTool 基类与 Build 流程

### 统一 Build 入口

`codegen::Build(IRModule mod, Target target)` 是所有后端的统一代码生成入口，定义于 `src/target/codegen.cc` [F-161]。其核心逻辑为：

1. 从 target 获取 kind 名称。
2. 在全局函数注册表中查找 `"target.build." + kind_name`。
3. 调用该全局函数，传入 IRModule 和 Target，返回 `runtime::Module`。

这种基于全局函数注册表的分派机制使得代码生成后端完全可插拔——新后端无需修改 `Build` 函数本身，只需注册对应的 build 函数 [F-162]。

### Build 的输入与输出

输入：经过 TIR lowering Pass 优化后的 IRModule，其中包含一个或多个 PrimFunc，每个函数标注了 `Target` 属性（指示应编译到哪个设备）。对于异构计算场景，同一模块中可能同时包含 CPU 函数和 GPU 函数。

输出：一个 `runtime::Module` 对象，它是编译产物的根模块。根模块通过 imports 树引用设备子模块（如 CUDA fatbin 模块、Metal 模块等）。

### Module 导入树

编译产物不是单个二进制文件，而是一棵 Module 导入树。根 Module（通常是 host 模块）持有 `imports_` 列表，每个子 Module 对应一个设备后端或外部库 [F-030]。`Module::GetFunction(name, query_imports=true)` 会递归搜索导入链，使得从根模块即可查找任意设备上的函数 [F-031]。

导入树支持三种序列化格式 [F-163]：

| 格式 | 函数 | 用途 |
|------|------|------|
| C 源码 | `PackImportsToC` | 生成可独立编译的 C 源文件（嵌入式部署） |
| LLVM IR | `PackImportsToLLVM` | 生成 LLVM bitcode 或目标文件 |
| 字节流 | `PackImportsToBytes` | 生成二进制 blob（运行时动态加载） |

序列化时使用 `ModuleSerializer`，它遍历导入树（CSR 格式的 indptr + child_indices），对每个模块调用其 `SaveToBinary` 方法。嵌入式库二进制格式为：`<nbytes:u64> <import_tree> <key0:str>[<val0:bytes>]...`，其中 `"_lib"` 键标识主库位置。

## LLVM 后端

LLVM 是 TVM CPU 代码生成的主要后端，也是 PTX（CUDA）和 AMDGPU（ROCm）代码生成的基础。

### CodeGenLLVM 基类

`CodeGenLLVM` 定义于 `src/target/llvm/codegen_llvm.h`，继承自 TIRx 的 `ExprFunctor` 和 `StmtFunctor`，将 TIR 表达式和语句翻译为 LLVM IR [F-164]。它维护：

- `llvm::LLVMContext`：LLVM 上下文
- `llvm::Module`：正在构建的 LLVM 模块
- `llvm::IRBuilder<>`：IR 构建器
- `builder_table_`：函数名→LLVM 内建函数的映射

核心方法包括 `VisitExpr_`（处理算术/比较/逻辑运算、Call、Cast）和 `VisitStmt_`（处理 For、IfThenElse、SeqStmt、Allocate、BufferStore、Evaluate）。每个 TIR 操作通过 `DoubleToLLVM`、`IntToLLVM`、`TypeToLLVM` 等转换函数映射到对应的 LLVM 指令。

### CodeGenCPU：CPU 代码生成

`CodeGenCPU`（`src/target/llvm/codegen_cpu.h`）继承自 CodeGenLLVM，是主机 CPU 代码生成的具体实现 [F-165]。它额外处理：

- **并行循环**：TIR 的 `parallel` ForKind 翻译为调用 TVM 运行时线程池的 `parallel_launch`。
- **向量指令**：根据 Target 属性中的向量宽度生成 LLVM vector 指令。
- **内建函数**：将 `tirx.call_pure_extern`、`tirx.call_extern` 翻译为 LLVM 外部函数调用。
- **函数属性**：设置 target-cpu、target-features 属性以启用指令集优化。

### 架构特化

LLVM 后端根据 Target 的 `mtriple` 自动选择目标架构：

| 架构 | mtriple 前缀 | 说明 |
|------|-------------|------|
| x86_64 | `x86_64-*` | SSE/AVX/AVX2/AVX-512 向量化 |
| AArch64 | `aarch64-*` | NEON/SVE 向量化 |
| ARM | `armv7-*` | 32 位 ARM，NEON |
| RISC-V | `riscv64-*` | RVV 向量扩展 |
| Hexagon | `hexagon-*` | Qualcomm Hexagon DSP |

x86 后端通过 `codegen_x86` 相关文件处理 AVX-512 等特化指令选择；AArch64 后端（`codegen_aarch64`）处理 SVE 可变长度向量；ARM 后端（`codegen_arm`）处理 32 位 NEON。

### LLVM 优化与目标代码生成

CodeGenLLVM 生成 LLVM IR 后，通过 LLVM 的 PassManager 运行标准优化（O2/O3 级别），然后调用 LLVM TargetMachine 生成目标文件（.o）或汇编。最终通过 `LLVMModuleSerializer` 将编译后的机器码包装为 TVM runtime::Module。

对于 CUDA（PTX）和 ROCm（AMDGPU），CodeGenLLVM 使用对应的 LLVM 后端生成 PTX/AMDGCN 二进制，包装为 GPU 子模块。

## C 源码后端

C 源码后端为不使用 LLVM 的目标提供代码生成路径，也是 GPU 类 C 语言（CUDA/OpenCL/Metal/Vulkan）的基础设施。

### CodeGenC 基类

`CodeGenC`（`src/target/source/codegen_c.h`）将 TIR 翻译为 C 语言源码，继承自 `ExprFunctor` 和 `StmtFunctor` [F-166]。它将 TIR 结构映射为 C 语法：

| TIR 结构 | C 输出 |
|---------|--------|
| For (serial) | `for (...) { ... }` |
| For (parallel/thread_binding) | 后端特化（CUDA `__global__` 等） |
| For (vectorized) | `#pragma clang loop vectorize(enable)` 或目标特有语法 |
| BufferStore | `buffer[index] = value;` |
| Allocate | `float* buffer = (float*)alloca(...);`（常量大小栈分配）或设备内存分配 API |
| IfThenElse | `if (...) { ... } else { ... }` |
| Call (extern) | `func_name(args...)` |

CodeGenC 维护类型映射表（`PrintType` 将 DLDataType 转为 C 类型字符串）、函数名映射表、以及缩进/行号追踪。它生成的 C 源码可由目标平台的 C 编译器（nvcc、gcc、clang 等）进一步编译。

### CodeGenCHost：主机 C 后端

`CodeGenCHost`（`src/target/source/codegen_c_host.h`）继承自 CodeGenC，生成主机侧 C 代码 [F-167]。它额外处理：

- TVM-FFI C API 调用（`TVMFFIFunctionCall`、`TVMFFIAny`、`TVMFFIEnvModLookupFromImports`）
- FFI 函数包装与入口生成（`tvm_ffi_main`）
- 模块上下文字符串（`tvm_ffi_library_ctx`）
- 设备函数的主机侧入口

CodeGenCHost 的输出是一个 C 源文件，编译后生成的动态库可被 TVM Runtime 直接加载。这种方式在交叉编译和嵌入式部署中特别有用——不需要在目标设备上安装 LLVM。

## GPU 后端

GPU 后端均基于 CodeGenC 派生，将 TIR 翻译为各 GPU 平台的 kernel 语言，再通过平台工具链编译为二进制。

### CUDA 后端

- **Target kind**：`cuda`，默认 device_type 为 kDLCUDA
- **代码生成**：CodeGenCUDA 继承 CodeGenC，生成 `.cu` 源码
- **特殊处理**：
  - `thread_binding` For 映射为 `threadIdx.x/y/z`、`blockIdx.x/y/z`
  - `shared` memory scope 映射为 `__shared__`
  - `warp` scope 映射为 warp 级内建函数
  - `__syncthreads()` 屏障生成
- **编译**：调用 nvcc 将 `.cu` 编译为 fatbin，包装为 CUDAModule
- **属性**：`max_num_threads`（通常 1024）、`thread_warp_size`（32）、`arch`（sm_75/sm_80/sm_90 等）

### Metal 后端

- **Target kind**：`metal`，device_type 为 kDLMetal
- **代码生成**：CodeGenMetal 生成 Metal Shading Language（MSL，基于 C++14）
- **特殊处理**：`[[kernel]]`、`[[buffer]]`、`[[thread_position_in_grid]]` 等 Metal 属性语法
- **编译**：运行时通过 Metal 编译器编译着色器（macOS/iOS）

### OpenCL 后端

- **Target kind**：`opencl`，device_type 为 kDLOpenCL
- **代码生成**：CodeGenOpenCL 生成 OpenCL C kernel
- **特殊处理**：`__kernel`、`__global`/`__local`/`__private` 地址空间限定符、`get_global_id()`/`get_local_id()` 内建函数
- **优势**：跨厂商（Intel/AMD/NVIDIA/ARM），适用于非 NVIDIA GPU

### Vulkan 后端

- **Target kind**：`vulkan`，device_type 为 kDLVulkan
- **代码生成**：CodeGenVulkan 生成 GLSL（Vulkan 的着色器语言），然后通过 glslang 编译为 SPIR-V 二进制
- **特殊处理**：descriptor set 映射、push constants、计算着色器管线
- **优势**：跨平台（Windows/Linux/Android），显式 API 开销低

### ROCm 后端

- **Target kind**：`rocm`，device_type 为 kDLROCM
- **代码生成**：两种路径——CodeGenC 生成 HIP 源码，或通过 LLVM AMDGPU 后端直接生成机器码
- **特殊处理**：`__global__`、`__shared__`（与 CUDA 类似的 HIP 语法）、wavefront 大小 64
- **属性**：`arch`（gfx906/gfx908/gfx942 等）

### GPU 后端的共同模式

所有 GPU 后端共享以下编译模式：

1. TIR 中的 `thread_binding` 循环映射为 GPU 线程/块索引。
2. 不同 memory scope（global/shared/local/warp）映射为 GPU 内存层级。
3. 生成的 kernel 源码通过平台编译器编译为二进制。
4. 二进制包装为设备 Module，作为根 Module 的 import。
5. 主机侧 Module 负责内存拷贝和 kernel 启动。

## driver.build_module 编译入口

Python 端的 `tvm.driver.build_module.build()` 是 TIR 编译的高层入口，封装了完整的 lowering 和 codegen 流程 [F-341]：

```python
def build(input, target=None, target_host=None):
    # 1. 输入规范化：IRModule / PrimFunc / dict
    # 2. Target 解析与配置
    # 3. TIR lowering Pass 序列
    # 4. 设备函数分组（按 Target 分桶）
    # 5. 对每个 Target 调用 codegen::Build
    # 6. 主机侧代码生成与 Module 组装
    # 7. 返回 runtime.Module
```

更上层的 `tvm.driver.driver_api.compile()` 是统一的编译入口，自动检测 IRModule 内容 [F-340]：

- 若模块包含 Relax 函数，路由到 `tvm.relax.build`，后者执行 Relax 优化流水线后调用 TIR build 处理生成的 PrimFunc。
- 若模块仅包含 TIR PrimFunc，直接调用 `tvm.tirx.build`（即 build_module.build）。

`relax.build` 的流程为：
1. 执行 `default_build_pipeline()` 中的 Relax Pass（包括 LegalizeOps 将高层算子降级为 call_tir）。
2. 收集所有 TIR PrimFunc，按 Target 分组。
3. 对每组调用 `tvm.tirx.build` 生成设备 Module。
4. Relax 函数通过 `VMShapeLower` 和 `LowerRuntimeBuiltin` 降级为 VM 字节码。
5. VM 字节码和设备 Module 组装为最终的 Executable Module。

## 外部代码生成（BYOC）

除内置后端外，TVM 支持 Bring Your Own Codegen（BYOC）框架，允许外部编译器（如 TensorRT、cuDNN、DNNL、Cutlass）接管子图编译 [F-216]：

1. `RunCodegen` Pass 遍历 IRModule，找到标注了外部编译器的函数（通过 `kCodegen` 属性）。
2. 对每个外部编译器，调用 `"relay.ext.<compiler>"` 或 `"relax.ext.<compiler>"` 全局函数。
3. 外部编译器编译子图，返回序列化的 runtime::Module。
4. 外部 Module 作为 import 加入最终 Module 树。

`src/relax/backend/contrib/` 目录包含 11 个外部后端参考实现：clml、codegen_c、codegen_json、cublas、cudnn、cutlass、dnnl、example_npu、hipblas、nnapi、tensorrt。其中 `codegen_json` 是一个通用的 JSON 序列化框架，外部编译器只需实现对应的 JSON 消费端即可。

## 相关概念

- [TVM 整体架构与编译流水线](/concepts/00-overview.md)
- [Pass 基础设施](/concepts/03-pass-infrastructure.md)
- [TVM-FFI 跨语言基础](/concepts/01-ffi-foundation.md)
