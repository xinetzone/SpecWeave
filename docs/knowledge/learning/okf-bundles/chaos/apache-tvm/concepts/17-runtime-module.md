---
type: Concept
title: Runtime Module 系统
description: TVM Runtime Module 系统，涵盖 Module 导入树、DSOModule、StaticLibraryModule、LoadFromFile、ffi::Function 调用约定、DeviceAPI 设备抽象及 NDArray 张量管理
tags: [tvm, runtime, module, ffi-function, device-api, ndarray, dso, threadpool]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: runtime-target-arith-source
    resource: "/references/runtime-target-arith-source.md"
    title: Runtime/Target/Arith 源码
  - id: tvm-ffi-source
    resource: "/references/tvm-ffi-source.md"
    title: TVM-FFI 源码
---

# Runtime Module 系统

TVM Runtime 是编译后模型的执行环境，负责设备管理、内存分配、函数调用和模块加载。Runtime Module 系统是 TVM 部署能力的核心——它定义了编译产物的组织方式、动态加载机制和跨设备函数调用约定，使同一份编译模型能在 CPU、GPU、移动端甚至嵌入式设备上运行。Runtime 设计遵循最小依赖原则，核心运行时库（`libtvm_runtime`）不依赖 LLVM 或任何编译器组件，可独立部署。

## Module：模块基类与导入树

`ffi::Module` 是 TVM 运行时模块系统的核心类 [F-30]。一个 Module 代表一组可调用函数的集合，可以是动态链接库、静态库、VM 字节码或外部代码生成模块。Module 之间通过**导入树**（import tree）组织：根 Module 可以导入若干子 Module，子 Module 又可以继续导入，形成树形依赖结构。

### Module 核心方法

| 方法 | 说明 |
|------|------|
| `kind()` | 返回模块类型键字符串 [F-33] |
| `GetFunction(name)` | 按名称查找模块中的函数 |
| `imports()` | 获取导入的子模块列表，返回可迭代对象 [F-31] |
| `SaveToBytes()` | 将模块序列化为字节串 [F-34] |

Module 具有两个属性掩码用于序列化分类 [F-32]：
- **`kCompilationExportable`**：DSO 可导出，可被打包为动态库。
- **`kBinarySerializable`**：二进制可序列化，可保存为字节流。

### 模块类型

TVM 内置多种 Module 实现：

- **DSOModule**：动态共享库模块，通过 `dlopen`/`LoadLibrary` 加载编译生成的 `.so`/`.dll`/`.dylib`。这是最常见的模块类型，每个设备代码生成后都产生一个 DSOModule。
- **StaticLibraryModule**：静态库模块，支持从静态链接的符号表中加载函数 [F-55]。适用于不支持动态加载的嵌入式环境。
- **VMExecutable**：Relax VM 字节码模块，包含序列化的 VM 指令和常量池。
- **RPCModule**：远程过程调用模块，将函数调用转发到远程设备。

### 模块加载

模块加载通过全局函数 `"ffi.Module.load_from_bytes." + tkey` 完成，其中 `tkey` 是模块类型键 [F-36]。`LoadFromFile` 根据文件扩展名或显式指定的 format 参数分派到对应的加载器。`RuntimeEnabled` 函数用于判断目标运行时是否在编译时启用 [F-35]。

Python 端 `Module` 类通过 `@_register_object("ffi.Module")` 注册 [F-45]，提供 `_collect_from_import_tree` 辅助方法遍历导入树 [F-46]。`load_module`、`enabled`、`system_lib`、`load_static_library`、`num_threads` 等函数从 Python runtime 包导出 [F-48]。

### 模块序列化

`ModuleSerializer` 类负责模块及其导入树的序列化 [F-37]。其关键机制包括：

- **两阶段 DFS 索引**：`CreateModuleIndex` 使用深度优先搜索遍历导入树，将所有 DSO 可导出模块合并为单个组 [F-38]。
- **CSR 格式存储**：导入树通过 `import_tree_row_ptr_`（行指针）和 `import_tree_child_indices_`（子节点索引）以 CSR（Compressed Sparse Row）格式表示 [F-39]。
- **根模块固定**：序列化时根模块始终位于索引 0 [F-40]。
- **DSO 占位符**：`"_lib"` 是 DSO 模块在导入树中的占位符类型键 [F-41]。

序列化提供三种打包方式：
- **`PackImportsToC`**：将模块导入树打包为 C 源码，包含十六进制字节数组和系统库注册代码 [F-42]。
- **`PackImportsToLLVM`**：调用 `"codegen.codegen_blob"` 生成包含导入树的 LLVM 模块 [F-43]。
- **`PackImportsToBytes`**：在序列化字节前添加 8 字节小端长度头 [F-44]。

## ffi::Function 调用约定

`ffi::Function` 是 TVM Runtime 的统一函数调用抽象（由 TVM-FFI 提供）。所有可调用对象——无论是 C++ 函数、Python 函数、设备内核还是远程函数——都通过 `ffi::Function` 接口暴露。其底层打包调用签名为：

```cpp
void (*)(ffi::PackedArgs args, ffi::Any* rv)
```

`ffi::PackedArgs` 封装可变参数列表（支持整数、浮点数、字符串、NDArray、Module、其他 Function 等类型），`ffi::Any*` 是通用返回值容器。这种设计使得：

1. **跨语言调用透明**：Python 调用 C++ 函数、C++ 调用 Python 函数使用相同接口。
2. **模块间解耦**：模块只需通过名称导出 Function，无需链接时依赖。
3. **远程调用统一**：RPC 模块将 Function 调用序列化后发送到远程设备执行。

编译生成的 TIR PrimFunc 在运行时通过模块的 `GetFunction` 获取，以 `ffi::Function` 形式调用。函数名通常是 PrimFunc 的 `global_symbol` 属性值。

## DeviceAPI：设备抽象层

`DeviceAPI` 抽象类定义在 `include/tvm/runtime/device_api.h`，是所有设备后端的统一接口 [F-6]。它屏蔽了 CPU、CUDA、Metal、OpenCL、Vulkan、ROCm 等不同设备的 API 差异，使 Runtime 核心逻辑与具体设备无关。

### 核心接口

DeviceAPI 声明了以下纯虚函数 [F-7][F-8][F-9][F-10][F-11][F-12]：

| 方法 | 功能 |
|------|------|
| `SetDevice(ctx)` | 设置当前线程的活动设备 |
| `GetAttr(ctx, kind, rv)` | 查询设备属性（最大线程数、warp size 等） |
| `AllocDataSpace(ctx, nbytes, alignment, type_hint)` | 在设备上分配数据内存 |
| `FreeDataSpace(ctx, ptr)` | 释放设备内存 |
| `CopyDataFromTo(from, from_offset, to, to_offset, num_bytes, ctx_from, ctx_to, type_hint, stream)` | 跨设备数据拷贝 |
| `StreamSync(ctx, stream)` | 流同步（虚函数，有默认实现） |

### 设备注册与管理

`DeviceAPIManager` 单例管理全局设备 API 注册表 [F-13]。设备注册通过 `refl::GlobalDef().def_packed("device_api.xxx", ...)` 机制完成，每个设备类型对应一个返回其 DeviceAPI 实例的全局函数 [F-14]。

已注册的设备后端包括：
- **CPU**：`CPUThread` 设备 API 位于 `src/runtime/cpu_device_api.cc`，使用标准 `malloc`/`free` 进行内存管理 [F-15]。
- **CUDA**：通过 CUDA Driver API 管理 GPU 设备和显存。
- **Metal**：Apple Metal 设备。
- **OpenCL**：跨平台 OpenCL 设备。
- **Vulkan**：Vulkan 计算设备。
- **ROCm**：AMD GPU 设备。

### Python 端 Device

Python 端 `Device` 类定义在 `python/tvm/runtime/device.py`，继承自 `tvm_ffi.core.Device` [F-16]。提供以下属性：

- `exist`：通过查询属性 ID 0 判断设备是否存在 [F-17]。
- `max_threads_per_block`：查询属性 ID 1 [F-18]。
- `warp_size`：查询属性 ID 2，CUDA/ROCm/Vulkan 返回实际值，Metal/OpenCL 返回 1 [F-19]。
- `max_shared_memory_per_block`：查询属性 ID 3 [F-20]。

`RPC_SESS_MASK = 128` 用于标记 RPC 远程设备的 device_type [F-21]。Python 端便捷设备构造函数 `cpu`、`cuda`、`opencl`、`vulkan`、`metal`、`rocm`、`ext_dev`、`vpi` 从 `_tensor` 模块导出 [F-28]。

## NDArray / DLTensor

NDArray 是 TVM Runtime 的张量数据结构，基于 DLPack 标准的 `DLTensor` 格式。

### DLTensor 结构

DLTensor 包含：
- `data`：指向数据内存的指针。
- `device`：DLDevice（device_type + device_id）。
- `ndim`：维数。
- `dtype`：DLDataType（code + bits + lanes）[F-3]。
- `shape`：形状数组。
- `strides`：步幅数组（可为 NULL 表示紧凑布局）。
- `byte_offset`：字节偏移。

DLDevice 包含 `device_type` 和 `device_id` 两个字段 [F-4]。设备类型常量（kDLCPU=1、kDLCUDA=2、kDLExtDev=12 等）来自 DLPack 头文件 [F-5]。

### Tensor 托管封装

`Tensor` 类定义在 `include/tvm/runtime/tensor.h`，是对 DLTensor 的托管引用封装 [F-22]，提供引用计数自动管理。核心方法包括：

- `CopyFrom(DLTensor* src)` / `CopyTo(DLTensor* dst)`：数据拷贝 [F-23]。
- `CreateView`：创建共享底层数据的视图张量 [F-24]。
- `Tensor::Empty`：创建指定形状、数据类型和设备的空张量 [F-25]。

NDArray 实现位于 `src/runtime/tensor.cc`，包含引用计数管理和跨设备拷贝逻辑 [F-26]。跨设备拷贝通过 DeviceAPI 的 `CopyDataFromTo` 实现，自动处理主机到设备、设备到主机、设备到设备的传输。

Python 端 `Tensor`、`tensor`、`empty` 从 `python/tvm/runtime/_tensor.py` 导出 [F-27]。`from_dlpack` 函数支持 DLPack 协议互操作 [F-29]，使 TVM NDArray 可与 NumPy、PyTorch、CuPy 等框架零拷贝共享数据。

## WorkspacePool 与 MemoryManager

`WorkspacePool` 实现在 `src/runtime/workspace_pool.cc` [F-52]，提供设备工作区内存的池化复用。在深度学习推理中，中间临时缓冲区（workspace）的分配和释放可能成为性能瓶颈。WorkspacePool 维护一个空闲内存块池：

1. 分配时先查找池中是否有足够大的空闲块。
2. 若有，直接复用；若无，向 DeviceAPI 分配新内存。
3. 释放时将块归还池中而非立即归还设备。
4. 池按大小组织，支持不同大小的请求。

这显著减少了频繁分配/释放设备内存的开销，尤其在 GPU 上（cudaMalloc/cudaFree 相对昂贵）。

## ThreadPool 线程池

线程池实现在 `src/runtime/thread_pool.cc` [F-51]，提供多线程并行执行能力。TVM 生成的 CPU 代码通过 `tvm_parallel_launch` 运行时函数将并行循环分发给线程池：

1. 编译时，TIR 的 `parallel` for 循环被降级为 `tvm_parallel_launch` 调用。
2. 运行时，线程池将任务按 stride 模式分配给工作线程。
3. 工作线程数可通过环境变量或 `num_threads` 函数配置。
4. 线程池在首次使用时懒初始化，在程序退出时销毁。

CodeGenCPU 内部包含 `ParallelEnv` 结构体跟踪并行任务环境（task_id、num_task、stride_pattern 等），声明了 `ftype_tvm_parallel_launch_` 和 `ftype_tvm_parallel_barrier_` 运行时函数类型。

## 日志与错误处理

日志系统定义在 `include/tvm/runtime/logging.h` [F-56]，提供：
- **`TVM_FFI_ICHECK`**：运行时检查宏，失败时抛出异常并附带文件名和行号 [F-57]。
- **`TVM_FFI_THROW(ErrorType)`**：抛出指定类型异常（TypeError、ValueError、RuntimeError 等）[F-58]。

定时器定义在 `include/tvm/runtime/timer.h`，提供高精度计时功能 [F-59]，用于基准测试和性能分析。

## BenchmarkResult

Python 端 `BenchmarkResult` 类封装基准测试结果 [F-47]，包含 min/mean/median/max/std 统计量，提供结构化的性能报告。

## 参数字典

`save_param_dict`、`load_param_dict`、`save_param_dict_to_file`、`load_param_dict_from_file` 从 params 子模块导出 [F-49]，提供模型权重的序列化/反序列化功能。参数字典将参数名映射到 NDArray，支持保存为文件供部署时加载。

## Disco 分布式

`disco` 模块是可选导入，当 `libtvm_runtime_extra` 不存在时静默设为 None [F-50]。Disco 是 TVM 的分布式执行引擎，用于多设备张量并行。

## 架构设计原则

Runtime Module 系统体现了以下设计原则：

1. **最小运行时**：核心运行时不依赖编译器组件，可独立部署到资源受限环境。
2. **统一抽象**：DeviceAPI 屏蔽设备差异，ffi::Function 统一函数调用，Module 统一代码组织。
3. **树形组合**：Module 导入树支持将多个设备代码、外部库和 VM 字节码组合为单一可部署单元。
4. **DLPack 互操作**：NDArray 遵循 DLPack 标准，与整个 Python 科学计算生态零拷贝互通。
5. **池化优化**：WorkspacePool 和线程池减少运行时开销，适合推理服务的低延迟需求。
6. **序列化灵活**：支持 C 源码、LLVM IR 和原始字节三种序列化格式，适应不同部署场景。

## 相关概念

- [FFI 基础设施](/concepts/01-ffi-foundation.md) — Runtime 通过 `ffi::Function` 统一函数调用约定，Module/NDArray 基于 FFI 对象系统
- [Object 对象系统](/concepts/02-object-system.md) — Module、NDArray、DeviceAPI 等运行时对象均继承自 Object 引用计数体系
- [VM 字节码虚拟机](/concepts/18-vm-bytecode.md) — VMExecutable 是 Module 的一种实现，包含 Relax 编译后的字节码和常量池
- [RPC 与分布式](/concepts/19-rpc-distributed.md) — RPCModule 作为 Module 的远程代理，透明转发函数调用到远程设备
- [Target 与代码生成](/concepts/04-target-codegen.md) — 各后端代码生成器产出 DSOModule（.so/.dll），由 Runtime 动态加载执行
