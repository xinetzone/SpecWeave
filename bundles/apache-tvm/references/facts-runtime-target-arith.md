---
type: Facts
title: TVM Runtime/Target/Arith/Support 事实清单
description: 从 TVM 源码采集的 Runtime 执行引擎、Target 多后端、Arith 证明引擎、Support 工具库事实，每条标注文件路径与行号
tags: [tvm, runtime, target, arith, support, facts, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
source_id: runtime-target-arith
---

# TVM Runtime/Target/Arith/Support 事实清单

> R 阶段事实采集，零推测。每条标注文件路径与行号。
> 源码根目录：`d:\AI\.chaos\libs\ffi\tvm\`

---

## 1. Runtime 核心

### 1.1 基础类型与版本

1. TVM 版本号定义在 `include/tvm/runtime/base.h` 第 35 行，默认值为 `"0.26.dev0"`。
2. `TVM_DLL`、`TVM_RUNTIME_DLL` 等跨平台动态库导出宏定义在 `include/tvm/runtime/base.h` 中。
3. `DLDataType` 结构体（来自 DLPack）包含 `code`（类型代码）、`bits`（位宽）、`lanes`（向量通道数）三个字段，在 `include/tvm/runtime/base.h` 中通过 `#include <dlpack/dlpack.h>` 引入。
4. `DLDevice` 结构体包含 `device_type`（设备类型枚举）和 `device_id`（设备编号）两个字段。
5. 设备类型常量 `kDLCPU=1`、`kDLCUDA=2`、`kDLExtDev=12` 等来自 DLPack 头文件，在 Target 注册中被引用（`src/target/target_kind.cc` 第 116、165、173 行）。

### 1.2 DeviceAPI 抽象

6. `DeviceAPI` 抽象类定义在 `include/tvm/runtime/device_api.h` 中，是所有设备后端的统一接口。
7. `DeviceAPI` 声明了纯虚函数 `SetDevice(TVMContext ctx)`，用于设置当前线程的活动设备。
8. `DeviceAPI` 声明了纯虚函数 `GetAttr(TVMContext ctx, DeviceAttrKind kind, TVMPodValue* rv)`，用于查询设备属性（如最大线程数、warp size 等）。
9. `DeviceAPI` 声明了纯虚函数 `AllocDataSpace(TVMContext ctx, size_t nbytes, size_t alignment, DLDataType type_hint)`，用于在设备上分配数据内存。
10. `DeviceAPI` 声明了纯虚函数 `FreeDataSpace(TVMContext ctx, void* ptr)`，用于释放设备内存。
11. `DeviceAPI` 声明了纯虚函数 `CopyDataFromTo(const void* from, size_t from_offset, void* to, size_t to_offset, size_t num_bytes, TVMContext ctx_from, TVMContext ctx_to, DLDataType type_hint, TVMStreamHandle stream)`，用于跨设备数据拷贝。
12. `DeviceAPI` 声明了虚函数 `StreamSync(TVMContext ctx, TVMStreamHandle stream)`，用于流同步。
13. `DeviceAPIManager` 单例管理全局设备 API 注册表，定义在 `src/runtime/device_api.cc` 中。
14. 设备注册通过 `refl::GlobalDef().def_packed("device_api.xxx", ...)` 机制完成，每个设备类型对应一个全局函数返回其 `DeviceAPI` 实例。
15. `CPUThread` 设备 API 实现位于 `src/runtime/cpu_device_api.cc`，`kDLCPU` 设备类型使用标准 `malloc`/`free` 进行内存管理。
16. Python 端 `Device` 类定义在 `python/tvm/runtime/device.py` 第 29 行，继承自 `tvm_ffi.core.Device`。
17. Python `Device.exist` 属性通过 `_GetDeviceAttr` 查询属性 ID 0 判断设备是否存在（`python/tvm/runtime/device.py` 第 38-51 行）。
18. Python `Device.max_threads_per_block` 属性查询设备属性 ID 1（`python/tvm/runtime/device.py` 第 54-67 行）。
19. Python `Device.warp_size` 属性查询设备属性 ID 2，CUDA/ROCm/Vulkan 返回实际值，Metal/OpenCL 返回 1（`python/tvm/runtime/device.py` 第 70-84 行）。
20. Python `Device.max_shared_memory_per_block` 属性查询设备属性 ID 3（`python/tvm/runtime/device.py` 第 87-100 行）。
21. `RPC_SESS_MASK = 128` 定义在 `python/tvm/runtime/device.py` 第 26 行，RPC 远程设备的 device_type 通过此掩码标记。

### 1.3 NDArray / DLTensor

22. `Tensor` 类定义在 `include/tvm/runtime/tensor.h` 中，是对 `DLTensor` 的托管引用封装。
23. `Tensor` 提供 `CopyFrom(DLTensor* src)` 和 `CopyTo(DLTensor* dst)` 方法实现数据拷贝。
24. `Tensor` 提供 `CreateView` 方法创建共享底层数据的视图张量。
25. `Tensor::Empty` 静态方法用于创建指定形状、数据类型和设备的空张量。
26. NDArray 实现位于 `src/runtime/tensor.cc`，包含引用计数管理和跨设备拷贝逻辑。
27. Python 端 `Tensor`、`tensor`、`empty` 从 `python/tvm/runtime/_tensor.py` 导出（`python/tvm/runtime/__init__.py` 第 31 行）。
28. Python 端便捷设备构造函数 `cpu`、`cuda`、`opencl`、`vulkan`、`metal`、`rocm`、`ext_dev`、`vpi` 均从 `_tensor` 模块导出（`python/tvm/runtime/__init__.py` 第 36-37 行）。
29. `from_dlpack` 函数也从 `_tensor` 模块导出，支持 DLPack 协议互操作（`python/tvm/runtime/__init__.py` 第 37 行）。

### 1.4 Module 系统

30. `ffi::Module` 是 TVM 运行时模块系统的核心类，通过 `#include <tvm/ffi/extra/module.h>` 引入（`src/target/codegen.cc` 第 24 行）。
31. Module 支持 `imports()` 方法获取导入的子模块列表，返回 `ffi::Any` 类型的可迭代对象（`src/target/codegen.cc` 第 111 行）。
32. Module 具有属性掩码 `kCompilationExportable`（DSO 可导出）和 `kBinarySerializable`（二进制可序列化），用于模块序列化时的分类处理（`src/target/codegen.cc` 第 73、76、84 行）。
33. Module 的 `kind()` 方法返回模块类型键字符串（`src/target/codegen.cc` 第 78 行）。
34. Module 的 `SaveToBytes()` 方法将模块序列化为字节串（`src/target/codegen.cc` 第 80 行）。
35. `RuntimeEnabled` 函数在 `src/runtime/module.cc` 中实现，用于判断目标运行时是否在编译时启用。
36. 模块从字节加载通过全局函数 `"ffi.Module.load_from_bytes." + tkey` 完成，其中 `tkey` 是模块类型键（`src/target/codegen.cc` 第 248 行）。
37. `ModuleSerializer` 类定义在 `src/target/codegen.cc` 第 61-214 行，负责模块及其导入树的序列化。
38. `ModuleSerializer::CreateModuleIndex` 使用两阶段 DFS 遍历，将所有 DSO 可导出模块合并为单个组（`src/target/codegen.cc` 第 105-171 行）。
39. 模块导入树通过 `import_tree_row_ptr_`（CSR 格式行指针）和 `import_tree_child_indices_`（子节点索引）表示（`src/target/codegen.cc` 第 212-213 行）。
40. 序列化时根模块始终位于索引 0（`src/target/codegen.cc` 第 101 行注释，第 265 行）。
41. `"_lib"` 是 DSO 模块在导入树中的占位符类型键（`src/target/codegen.cc` 第 74 行，第 239-241 行）。
42. `PackImportsToC` 函数将模块导入树打包为 C 源码，包含十六进制字节数组和系统库注册代码（`src/target/codegen.cc` 第 282-324 行）。
43. `PackImportsToLLVM` 函数调用全局函数 `"codegen.codegen_blob"` 生成包含导入树的 LLVM 模块（`src/target/codegen.cc` 第 326-343 行）。
44. `PackImportsToBytes` 在序列化字节前添加 8 字节小端长度头（`src/target/codegen.cc` 第 271-280 行）。
45. Python 端 `Module` 类定义在 `python/tvm/runtime/module.py` 第 109 行，使用 `@_register_object("ffi.Module")` 装饰器注册。
46. Python `Module` 类提供 `_collect_from_import_tree` 辅助方法遍历导入树（`python/tvm/runtime/module.py` 第 112 行）。
47. Python `BenchmarkResult` 类定义在 `python/tvm/runtime/module.py` 第 48-104 行，封装基准测试结果，包含 min/mean/median/max/std 统计量。
48. `load_module`、`enabled`、`system_lib`、`load_static_library`、`num_threads` 从 `python/tvm/runtime/module.py` 导出（`python/tvm/runtime/__init__.py` 第 38 行）。
49. `save_param_dict`、`load_param_dict`、`save_param_dict_to_file`、`load_param_dict_from_file` 从 `params` 子模块导出（`python/tvm/runtime/__init__.py` 第 40-45 行）。
50. `disco` 模块是可选导入，当 `libtvm_runtime_extra` 不存在时静默设为 `None`（`python/tvm/runtime/__init__.py` 第 47-52 行）。

### 1.5 线程池与工作区

51. 线程池实现在 `src/runtime/thread_pool.cc`，提供多线程并行执行能力。
52. `WorkspacePool` 实现在 `src/runtime/workspace_pool.cc`，提供设备工作区内存的池化复用。
53. CPU 设备 API 实现在 `src/runtime/cpu_device_api.cc`，是默认设备后端。
54. `file_utils.cc` 提供文件读写工具函数，位于 `src/runtime/`。
55. `static_library.cc` 实现静态库模块，支持从静态链接的符号表中加载函数。

### 1.6 日志与定时器

56. 日志系统定义在 `include/tvm/runtime/logging.h`，提供 `TVM_FFI_ICHECK`、`TVM_FFI_THROW` 等断言和异常宏。
57. `TVM_FFI_ICHECK` 宏用于运行时检查，失败时抛出异常并附带文件名和行号信息。
58. `TVM_FFI_THROW(ErrorType)` 宏用于抛出指定类型的异常，如 `TypeError`、`ValueError`、`RuntimeError`。
59. 定时器定义在 `include/tvm/runtime/timer.h`，提供高精度计时功能。

---

## 2. VM 虚拟机

### 2.1 VirtualMachine 核心

60. `VirtualMachine` 类定义在 `include/tvm/runtime/vm/vm.h`，是 VM 执行引擎的核心。
61. `VirtualMachine` 声明了 `Init` 方法用于初始化 VM 状态。
62. `VirtualMachine` 声明了 `LoadExecutable` 方法用于加载可执行文件。
63. `VirtualMachine` 声明了 `GetClosure` 方法用于获取闭包对象。
64. VM 实现在 `src/runtime/vm/vm.cc`，包含 `RunLoop` 指令调度主循环和 `InvokeBytecode` 函数调用逻辑。
65. Python 端 `VirtualMachine` 类定义在 `python/tvm/runtime/vm.py` 第 41 行。
66. Python `VirtualMachine` 支持两种分配器：`NAIVE_ALLOCATOR = 1` 和 `POOLED_ALLOCATOR = 2`（`python/tvm/runtime/vm.py` 第 44-45 行）。
67. Python `VirtualMachine.__init__` 接收 `rt_mod`（运行时模块或 Executable）、`device`（设备或设备列表）、`memory_cfg`（内存配置）（`python/tvm/runtime/vm.py` 第 47-71 行）。
68. Python VM 构造时调用 `rt_mod["vm_load_executable"]()` 加载可执行文件（`python/tvm/runtime/vm.py` 第 78 行）。
69. Python VM 缓存 `invoke_closure` 和 `save_function` 函数句柄（`python/tvm/runtime/vm.py` 第 79-80 行）。
70. `VMInstrumentReturnKind` 枚举定义在 `python/tvm/runtime/vm.py` 第 35-38 行，包含 `NO_OP=0` 和 `SKIP_RUN=1`。

### 2.2 字节码与指令集

71. `Opcode` 枚举定义在 `include/tvm/runtime/vm/bytecode.h`，包含 VM 支持的所有指令操作码。
72. 指令集包含 `Call`（函数调用）、`Ret`（返回）、`Goto`（无条件跳转）、`If`（条件分支）等控制流指令。
73. `Instruction` 结构体定义在 `include/tvm/runtime/vm/bytecode.h`，表示单条字节码指令，包含操作码和操作数。
74. 字节码实现在 `src/runtime/vm/bytecode.cc`，包含指令的解码和执行逻辑。

### 2.3 Executable 序列化

75. `Executable` 类定义在 `include/tvm/runtime/vm/executable.h`，表示 VM 可执行文件。
76. Executable 实现在 `src/runtime/vm/executable.cc`，包含字节码、常量池、函数表的序列化与反序列化。
77. Python 端 `Executable` 类从 `python/tvm/runtime/executable.py` 导出（`python/tvm/runtime/__init__.py` 第 33 行）。
78. Executable 的 `jit()` 方法将可执行文件即时编译为运行时模块（`python/tvm/runtime/vm.py` 第 74 行）。

### 2.4 内建函数与 KV Cache

79. VM 内建函数实现在 `src/runtime/vm/builtin.cc`，提供 VM 执行时可用的基础操作。
80. Paged KV Cache 实现在 `src/runtime/vm/paged_kv_cache.cc`，为大语言模型推理提供分页式键值缓存。
81. Attention 后端实现在 `src/runtime/vm/attn_backend.cc`，提供注意力计算的后端抽象。

---

## 3. RPC 远程调用

### 3.1 架构概览

82. RPC 模块源码位于 `src/runtime/rpc/` 目录。
83. `rpc_session.h` 定义 `RPCSession` 类，管理远程函数调用和远程对象生命周期。
84. `rpc_endpoint.h` 定义 `RPCEndpoint` 类，处理通信端点的消息收发。
85. `rpc_channel.h` 定义 `RPCChannel` 抽象接口，提供底层通信通道抽象。
86. `rpc_module.cc` 实现 RPC 模块，使远程设备上的模块可通过统一 Module 接口访问。
87. RPC 架构支持 Session（会话）、Endpoint（端点）、Channel（通道）三层抽象。
88. RPC 远程对象通过 `RPCObjectRef` 引用机制管理，确保远程对象正确释放。
89. Python 端 RPC 会话掩码 `RPC_SESS_MASK = 128` 定义在 `python/tvm/runtime/device.py` 第 26 行。
90. Python VM 从 `..rpc.base` 导入 `RPC_SESS_MASK`（`python/tvm/runtime/vm.py` 第 32 行）。

---

## 4. Target 与代码生成

### 4.1 Target 数据结构

91. `TargetNode` 类定义在 `include/tvm/target/target.h` 第 45-128 行，继承自 `ffi::Object`。
92. `TargetNode` 包含 `kind`（`TargetKind` 类型）成员，表示目标设备种类（`include/tvm/target/target.h` 第 48 行）。
93. `TargetNode` 包含 `host`（`ffi::Optional<ffi::ObjectRef>` 类型）成员，表示主机目标（`include/tvm/target/target.h` 第 50 行）。
94. `TargetNode` 包含 `tag`（`ffi::String` 类型）成员，可为空（`include/tvm/target/target.h` 第 52 行）。
95. `TargetNode` 包含 `keys`（`ffi::Array<ffi::String>` 类型）成员，表示目标键列表（`include/tvm/target/target.h` 第 54 行）。
96. `TargetNode` 包含 `attrs`（`ffi::Map<ffi::String, Any>` 类型）成员，存储目标属性（`include/tvm/target/target.h` 第 56 行）。
97. `TargetNode` 的 `str()` 方法返回 JSON 字符串表示，通过 `ffi::json::Stringify(ToConfig())` 生成（`src/target/target.cc` 第 101-106 行）。
98. `TargetNode::ToConfig()` 将目标导出为 JSON 配置字典，包含 `kind`、`tag`、`keys`、`host` 和所有 attrs（`src/target/target.cc` 第 151-164 行）。
99. `TargetNode::GetTargetDeviceType()` 优先从 attrs 中读取 `target_device_type`，否则返回 kind 的 `default_device_type`（`src/target/target.cc` 第 178-183 行）。
100. `TargetNode::HasKey(query_key)` 使用 `std::any_of` 检查 keys 列表中是否包含指定键（`src/target/target.cc` 第 185-188 行）。
101. `TargetNode::GetAttr<T>(attr_key, default_value)` 模板方法从 attrs 中查找属性，支持可选默认值（`include/tvm/target/target.h` 第 97-118 行）。
102. `TargetNode` 的类型键为 `"target.Target"`，使用 `kTVMFFISEqHashKindTreeNode` 哈希方式（`include/tvm/target/target.h` 第 120-121 行）。
103. `TargetNode` 的反射注册通过 `RegisterReflection()` 完成，注册了 `kind`、`tag`、`keys`、`attrs`、`host` 五个只读属性（`include/tvm/target/target.h` 第 80-88 行）。

### 4.2 Target 引用类与上下文

104. `Target` 类定义在 `include/tvm/target/target.h` 第 134 行，继承自 `ffi::ObjectRef`。
105. `Target` 支持从 `ffi::String` 构造，解析标签名、JSON 配置或 kind 名称（`include/tvm/target/target.h` 第 142 行，`src/target/target.cc` 第 110-120 行）。
106. `Target` 支持从 `ffi::Map<ffi::String, ffi::Any>` 配置字典构造（`include/tvm/target/target.h` 第 147 行，`src/target/target.cc` 第 122-132 行）。
107. `Target(target, host)` 构造函数复制目标并设置 host（`src/target/target.cc` 第 134-138 行）。
108. `Target::Current(allow_not_defined)` 静态方法从线程本地存储获取当前目标上下文（`src/target/target.cc` 第 214-223 行）。
109. `Target::EnterWithScope()` 将目标压入线程本地上下文栈（`src/target/target.cc` 第 202-205 行）。
110. `Target::ExitWithScope()` 从线程本地上下文栈弹出目标（`src/target/target.cc` 第 207-212 行）。
111. 线程本地目标上下文存储在 `TVMTargetThreadLocalEntry` 结构体中，包含 `std::stack<Target> context_stack`（`src/target/target.cc` 第 191-194 行）。
112. `Target::WithoutHost()` 创建一个移除 host 的新 Target 副本（`src/target/target.cc` 第 168-176 行）。
113. `CheckAndUpdateHostConsistency` 函数确保 target 和 host 的一致性（`src/target/target.cc` 第 71-74 行）。

### 4.3 Target 创建流程

114. `TargetInternal::FromString` 首先尝试通过 `TargetTag::Get` 查找标签（`src/target/target.cc` 第 256 行）。
115. 若字符串以 `{` 开头，按 JSON 配置解析（`src/target/target.cc` 第 260-262 行）。
116. 不含空格的纯字符串被视为 kind 名称（如 `"llvm"`、`"cuda"`）（`src/target/target.cc` 第 263-271 行）。
117. 含空格的字符串会抛出 `ValueError`，提示 CLI 形式（如 `"llvm -mcpu=xxx"`）已不再支持（`src/target/target.cc` 第 265-269 行）。
118. `FromConfig` 中若存在 `tag` 但无 `kind`，先查找标签配置再合并用户覆盖项（`src/target/target.cc` 第 297-312 行）。
119. `FromConfig` 中 `host` 字段在 schema 验证前递归解析（`src/target/target.cc` 第 327-332 行）。
120. `FromConfig` 在 schema 验证前提取所有 `feature.*` 键并保留，以支持规范化器输出的元数据（`src/target/target.cc` 第 334-349 行）。
121. `TargetInternal::ConstructorDispatcher` 支持 1 个参数（String/Map/Target）或 2 个参数（Target+Target host）的构造分发（`src/target/target.cc` 第 227-252 行）。
122. `TargetInternal::WithHost` 通过复制 TargetNode 并设置 host 字段创建新 Target（`src/target/target.cc` 第 54-58 行）。

### 4.4 TargetKind 注册

123. `TargetKindNode` 类定义在 `include/tvm/target/target_kind.h` 第 57-97 行。
124. `TargetKindNode` 包含 `name`（`ffi::String`）字段，表示目标种类名称（`include/tvm/target/target_kind.h` 第 60 行）。
125. `TargetKindNode` 包含 `default_device_type`（`int`）字段，表示默认设备类型（`include/tvm/target/target_kind.h` 第 62 行）。
126. `TargetKindNode` 包含 `default_keys`（`ffi::Array<ffi::String>`）字段，表示默认键列表（`include/tvm/target/target_kind.h` 第 64 行）。
127. `TargetKindNode` 包含 `target_canonicalizer`（`FTargetCanonicalizer`）字段，是目标创建时的规范化函数（`include/tvm/target/target_kind.h` 第 66 行）。
128. `TargetKindNode` 内部包含 `schema_`（`ir::ConfigSchema`）用于验证和解析目标属性（`include/tvm/target/target_kind.h` 第 87 行）。
129. `TargetKindNode` 使用 `kTVMFFISEqHashKindUniqueInstance` 哈希方式，即同一 kind 名称对应唯一实例（`include/tvm/target/target_kind.h` 第 78 行）。
130. `FTargetCanonicalizer` 类型定义为 `ffi::TypedFunction<ffi::Map<ffi::String, ffi::Any>(ffi::Map<ffi::String, ffi::Any>)>`，接收并返回 JSON 配置（`include/tvm/target/target_kind.h` 第 48-49 行）。
131. `TargetKind::Get(name)` 静态方法从注册表查找 TargetKind，返回 `ffi::Optional<TargetKind>`（`src/target/target_kind.cc` 第 96-102 行）。
132. `TargetKindRegEntry::RegisterOrGet` 是注册或获取目标种类条目的入口（`src/target/target_kind.cc` 第 83-85 行）。
133. `TargetKindRegEntry::ListTargetKinds` 列出所有已注册的目标种类名称（`src/target/target_kind.cc` 第 70-72 行）。
134. `TargetKindRegEntry::ListTargetKindOptions` 列出目标种类的所有配置选项及其类型（`src/target/target_kind.cc` 第 74-81 行）。
135. `TargetKind` 注册表使用 `AttrRegistry<TargetKindRegEntry, TargetKind>` 实现（`src/target/target_kind.cc` 第 68 行）。
136. `TVM_REGISTER_TARGET_KIND("llvm", kDLCPU)` 注册 LLVM 目标种类，默认设备类型为 CPU（`src/target/target_kind.cc` 第 116 行）。
137. LLVM 目标种类支持的属性包括：`mattr`（字符串数组）、`mcpu`、`mtriple`、`mfloat-abi`、`mabi`、`num-cores`（`src/target/target_kind.cc` 第 117-122 行）。
138. LLVM 目标种类支持快速数学标志：`fast-math`（总开关）、`fast-math-nnan`、`fast-math-ninf`、`fast-math-nsz`、`fast-math-arcp`、`fast-math-contract`、`fast-math-reassoc`（`src/target/target_kind.cc` 第 124-130 行）。
139. LLVM 目标种类支持 `opt-level`、`cl-opt`（LLVM 命令行参数数组）、`jit`（mcjit/orcjit）、`vector-width` 属性（`src/target/target_kind.cc` 第 131-137 行）。
140. LLVM 目标种类的默认键为 `{"cpu"}`（`src/target/target_kind.cc` 第 138 行）。
141. LLVM 和 C 目标种类都设置了 `tvm::target::canonicalizer::llvm::Canonicalize` 作为规范化器（`src/target/target_kind.cc` 第 141、171 行）。
142. `TVM_REGISTER_TARGET_KIND("c", kDLCPU)` 注册 C 源码目标种类，支持 `mcpu`、`march`、`workspace-byte-alignment`、`constants-byte-alignment` 属性（`src/target/target_kind.cc` 第 165-171 行）。
143. `TVM_REGISTER_TARGET_KIND("ext_dev", kDLExtDev)` 注册外部设备目标种类（`src/target/target_kind.cc` 第 173 行）。
144. `TVM_REGISTER_TARGET_KIND("composite", kDLCPU)` 注册复合目标种类，支持 `devices` 属性为 Target 数组（`src/target/target_kind.cc` 第 175-198 行）。
145. `TVM_REGISTER_TARGET_KIND("test", kDLCPU)` 注册测试目标种类，使用 `TestTargetParser` 规范化器设置 `feature.is_test=true`（`src/target/target_kind.cc` 第 200-201 行，第 109-112 行）。
146. TargetKind 的 JSON 序列化直接保存为名称字符串，反序列化时通过 `TargetKind::Get(name)` 查找（`src/target/target_kind.cc` 第 47-56 行）。

### 4.5 Target Tags

147. `TargetTagNode` 类定义在 `include/tvm/target/tag.h` 第 36-64 行，包含 `name` 和 `config` 字段。
148. `TargetTag::Get(name)` 静态方法根据标签名查找对应的 Target（`include/tvm/target/tag.h` 第 77 行）。
149. `TargetTag::ListTags()` 返回所有已注册标签名到 Target 的映射（`include/tvm/target/tag.h` 第 82 行）。
150. `TargetTag::GetConfig(name)` 返回标签对应的原始配置字典（`include/tvm/target/tag.h` 第 88 行）。
151. `TargetTag::AddTag(name, config, override)` 添加新标签（`include/tvm/target/tag.h` 第 97 行）。
152. `TVM_REGISTER_TARGET_TAG(TagName)` 宏用于注册新的目标标签（`include/tvm/target/tag.h` 第 167-169 行）。
153. Python 端 `list_tags` 和 `register_tag` 从 `tag` 子模块导出（`python/tvm/target/__init__.py` 第 36 行）。
154. Python 端 `tag_registry` 模块在导入时自动注册标签（`python/tvm/target/__init__.py` 第 38 行）。

### 4.6 VirtualDevice

155. `VirtualDevice` 定义在 `include/tvm/target/virtual_device.h`，是编译时数据存放位置和代码编译方式的描述。
156. `MemoryScope` 是 `ffi::String` 的类型别名，表示内存区域标签（`include/tvm/target/virtual_device.h` 第 45 行）。
157. `kNullDeviceType = 0` 表示空设备类型，不对应任何 DLDeviceType 枚举（`include/tvm/target/virtual_device.h` 第 52 行）。
158. `kInvalidDeviceType = -1` 表示无效设备类型（`include/tvm/target/virtual_device.h` 第 55 行）。
159. VirtualDevice 是四元组：device_type、virtual_device_id、target、memory_scope（`include/tvm/target/virtual_device.h` 第 63-72 行）。
160. Python 端 `VirtualDevice` 从 `virtual_device` 子模块导出（`python/tvm/target/__init__.py` 第 35 行）。

### 4.7 CodeGen 抽象基类

161. `codegen::Build(mod, target)` 函数声明在 `include/tvm/target/codegen.h` 第 44 行，是代码生成的统一入口。
162. `Build` 实现在 `src/target/codegen.cc` 第 48-58 行，通过查找全局函数 `"target.build." + target->kind->name` 分派到具体后端。
163. `Build` 函数在构建前检查 `tirx.disable_assert` 配置，若为 true 则先应用 `SkipAssert` pass（`src/target/codegen.cc` 第 49-51 行）。
164. `Build` 函数使用 `TVM_FFI_ICHECK` 确保对应的 build 函数已启用（`src/target/codegen.cc` 第 56 行）。
165. `SerializeModuleToBytes` 函数声明在 `include/tvm/target/codegen.h` 第 52 行，序列化模块及其导入树。
166. `DeserializeModuleFromBytes` 函数声明在 `include/tvm/target/codegen.h` 第 59 行，从字节反序列化模块。
167. `PackImportsToC` 函数声明在 `include/tvm/target/codegen.h` 第 72-73 行，将导入设备库打包为 C 文件。
168. `PackImportsToLLVM` 函数声明在 `include/tvm/target/codegen.h` 第 88-90 行，将导入设备库打包为 LLVM 模块。
169. `target.Build` 全局函数在静态初始化块中注册（`src/target/codegen.cc` 第 345-348 行）。
170. `runtime.ModulePackImportsToC`、`runtime.ModulePackImportsToLLVM`、`runtime.ModulePackImportsToTensor` 等辅助函数在静态初始化块中注册到运行时命名空间（`src/target/codegen.cc` 第 351-373 行）。
171. Python 端 `codegen` 子模块从 `python/tvm/target/` 导出（`python/tvm/target/__init__.py` 第 37 行）。

### 4.8 LLVM 后端

172. `CodeGenLLVM` 类定义在 `src/target/llvm/codegen_llvm.h` 第 94-95 行，同时继承 `ExprFunctor<llvm::Value*(const Expr&)>` 和 `StmtFunctor<void(const Stmt&)>`。
173. `CodeGenLLVM` 是所有 LLVM IR 代码生成器的公共基类（`src/target/llvm/codegen_llvm.h` 第 92 行注释）。
174. `CodeGenLLVM::Create(LLVMTarget*)` 静态工厂方法根据目标机器创建对应的代码生成器（`src/target/llvm/codegen_llvm.h` 第 105 行）。
175. `CodeGenLLVM::Init` 方法接收模块名、LLVM 目标、系统库前缀、动态查找标志和 C 运行时标志（`src/target/llvm/codegen_llvm.h` 第 118-120 行）。
176. `CodeGenLLVM::SetFastMathFlags` 设置浮点运算的快速数学标志（`src/target/llvm/codegen_llvm.h` 第 126 行）。
177. `CodeGenLLVM::DeclareFunction` 声明函数而不定义，`AddFunction` 编译并添加函数（`src/target/llvm/codegen_llvm.h` 第 128、138 行）。
178. `CodeGenLLVM::Finish` 完成代码生成并返回 `std::unique_ptr<llvm::Module>`（`src/target/llvm/codegen_llvm.h` 第 148 行）。
179. 整个 LLVM 代码生成受 `#ifdef TVM_LLVM_VERSION` 保护，仅在编译时启用 LLVM 时可用（`src/target/llvm/codegen_llvm.h` 第 27 行）。
180. `CodeGenCPU` 类定义在 `src/target/llvm/codegen_cpu.h` 第 62 行，继承自 `CodeGenLLVM`，是 CPU 主机代码生成器。
181. `CodeGenCPU` 重写了 `Init`、`AddFunction`、`AddMainFunction`、`Finish`、`VisitStmt_(AssertStmtNode*)`、`VisitStmt_(AttrStmtNode*)`、`VisitStmt_(ForNode*)` 等方法（`src/target/llvm/codegen_cpu.h` 第 67-76 行）。
182. `CodeGenCPU` 重写了 `CreateIntrinsic` 和 `CreateCallExtern` 方法（`src/target/llvm/codegen_cpu.h` 第 76-78 行）。
183. `CodeGenCPU` 内部包含 `ParallelEnv` 结构体，跟踪并行任务环境（task_id、num_task、stride_pattern 等）（`src/target/llvm/codegen_cpu.h` 第 106-113 行）。
184. `CodeGenCPU` 管理多种 LLVM 类型：`t_tvm_shape_index_`、`t_tvm_func_handle_`、`t_tvm_device_`、`t_tvm_type_`、`t_tvm_array_`、`t_tvm_ffi_any_`（`src/target/llvm/codegen_cpu.h` 第 85-90 行）。
185. `CodeGenCPU` 声明了多种运行时函数类型：`ftype_tvm_ffi_c_func_`、`ftype_tvm_parallel_launch_`、`ftype_tvm_parallel_barrier_`、`ftype_tvm_register_system_symbol_`（`src/target/llvm/codegen_cpu.h` 第 92-102 行）。
186. `CodeGenCPU::CreateParallelLaunch` 创建并行启动代码（`src/target/llvm/codegen_cpu.h` 第 148 行）。
187. `CodeGenCPU` 维护导出系统符号列表 `export_system_symbols_` 和函数注册表 `registry_functions_`（`src/target/llvm/codegen_cpu.h` 第 186-188 行）。
188. `CreateLLVMCppMetadataModule` 函数声明在 `src/target/llvm/llvm_module.h` 第 37 行，创建 C++ 元数据模块。

### 4.9 C 源码后端

189. `CodeGenC` 类定义在 `src/target/source/codegen_c.h` 第 59-61 行，同时继承 `ExprFunctor`、`StmtFunctor` 和 `CodeGenSourceBase`。
190. `CodeGenC` 是生成 C 风格代码的基类，支持 SSA 形式和普通形式两种模式（`src/target/source/codegen_c.h` 第 52-57 行注释）。
191. `CodeGenC::Init(output_ssa)` 初始化代码生成器，参数控制是否输出 SSA 形式（`src/target/source/codegen_c.h` 第 67 行）。
192. `CodeGenC::DeclareFunction` 仅声明函数，`AddFunction` 添加完整的函数声明和定义（`src/target/source/codegen_c.h` 第 77、86 行）。
193. `CodeGenC::Finish` 完成编译并返回生成的代码字符串（`src/target/source/codegen_c.h` 第 99 行）。
194. `CodeGenC::PrintExpr` 将表达式打印到输出流，SSA 模式下使用 SSA ID（`src/target/source/codegen_c.h` 第 110-111 行）。
195. `CodeGenC` 注释明确说明其目标不是生成 MSVC/GCC 可消费的原生 C 代码，而是为 CUDA、OpenCL-C 等 C 变体提供基础设施（`src/target/source/codegen_c.h` 第 54-57 行）。
196. `CodeGenSourceBase` 是 C 风格源码生成的基类，`CodeGenC` 通过 `#include "codegen_source_base.h"` 引入（`src/target/source/codegen_c.h` 第 43 行）。

---

## 5. Arith 整数分析

### 5.1 Analyzer 核心架构

197. `AnalyzerObj` 类定义在 `include/tvm/arith/analyzer.h` 第 712-898 行，是包含多个子分析器的复合分析器对象。
198. `AnalyzerObj` 包含七个子分析器：`const_int_bound`、`modular_set`、`rewrite_simplify`、`canonical_simplify`、`int_set`、`transitive_comparisons`、`z3_prover`（`include/tvm/arith/analyzer.h` 第 715-727 行）。
199. `AnalyzerObj` 构造函数在 `src/arith/analyzer.cc` 第 37-43 行实现，初始化所有子分析器并传入 `this` 指针。
200. `AnalyzerObj::Bind(var, expr, allow_override)` 将变量绑定到表达式，先经 canonical_simplify 和 rewrite_simplify 化简，再更新所有子分析器（`src/arith/analyzer.cc` 第 45-57 行）。
201. `AnalyzerObj::Bind(var, range, allow_override)` 绑定变量到范围，当 extent 为 1 时退化为表达式绑定（`src/arith/analyzer.cc` 第 59-71 行）。
202. `AnalyzerObj::MarkGlobalNonNegValue` 将值标记为全局非负，通过分解为 symbol*scale+offset 并更新 const_int_bound（`src/arith/analyzer.cc` 第 73-122 行）。
203. `AnalyzerObj::CanProveGreaterEqual(expr, lower_bound)` 先经 rewrite_simplify 化简，再检查 const_int_bound 的 min_value（`src/arith/analyzer.cc` 第 151-158 行）。
204. `AnalyzerObj::CanProveLess(expr, upper_bound)` 类似地检查 const_int_bound 的 max_value（`src/arith/analyzer.cc` 第 160-167 行）。
205. `AnalyzerObj::CanProveEqual(lhs, rhs)` 先检查整数常量，再通过 `CanProve(lhs - rhs == 0)` 判定（`src/arith/analyzer.cc` 第 169-177 行）。
206. `AnalyzerObj::Simplify(expr, steps)` 默认执行 2 步化简：rewrite_simplify → canonical_simplify（`include/tvm/arith/analyzer.h` 第 853-865 行）。
207. `AnalyzerObj::Clone()` 深拷贝分析器，生成独立的副本（`include/tvm/arith/analyzer.h` 第 885 行）。
208. `Analyzer` 引用类定义在 `include/tvm/arith/analyzer.h` 第 913-921 行，默认构造函数会创建新的 `AnalyzerObj`。
209. `Analyzer` 是轻量级引用计数句柄，复制句柄共享同一 `AnalyzerObj` 状态（`include/tvm/arith/analyzer.h` 第 903-910 行注释）。
210. `AnalyzerObj` 标记为 `_type_mutable = true`，允许通过 const 引用调用非 const 方法（`include/tvm/arith/analyzer.h` 第 896 行）。
211. `AnalyzerObj` 的类型键为 `"arith.Analyzer"`（`include/tvm/arith/analyzer.h` 第 897 行）。

### 5.2 ConstraintContext 约束上下文

212. `ConstraintContext` 类定义在 `include/tvm/arith/analyzer.h` 第 939 行，配合 `With<ConstraintContext>` 使用。
213. `ConstraintContext::EnterWithScope` 依次调用六个子分析器的 `EnterConstraint` 方法（const_int_bound、modular_set、rewrite_simplify、int_set、transitive_comparisons、z3_prover）（`src/arith/analyzer.cc` 第 130-139 行）。
214. `ConstraintContext::ExitWithScope` 按逆序调用恢复函数清理约束（`src/arith/analyzer.cc` 第 141-149 行）。
215. 注释说明不应在约束作用域激活时调用 `Clone()`，否则约束会泄漏为全局事实（`include/tvm/arith/analyzer.h` 第 877-881 行）。

### 5.3 ConstIntBound 常量整数边界

216. `ConstIntBoundNode` 类定义在 `include/tvm/arith/analyzer.h` 第 90-112 行，包含 `min_value` 和 `max_value` 两个 `int64_t` 字段。
217. `ConstIntBoundNode::kPosInf` 定义为 `std::numeric_limits<int64_t>::max()`（第 103 行）。
218. `ConstIntBoundNode::kNegInf` 定义为 `-kPosInf`（第 108 行）。
219. `ConstIntBoundNode` 的类型键为 `"arith.ConstIntBound"`，使用 `kTVMFFISEqHashKindTreeNode` 哈希（第 111 行）。
220. `ConstIntBoundAnalyzer` 类定义在 `include/tvm/arith/analyzer.h` 第 135-196 行，使用 `BoundMapType`（`std::unordered_map<PrimExpr, ConstIntBound, ...>`）缓存中间结果。
221. `ConstIntBoundAnalyzer::operator()(expr)` 分析表达式的常量整数边界（第 144 行）。
222. `ConstIntBoundAnalyzer::Update(var, info, allow_override)` 更新变量的边界信息（第 161 行）。
223. `ConstIntBoundAnalyzer::Bind(var, range, allow_override)` 将变量绑定到范围（第 170 行）。
224. `ConstIntBoundAnalyzer::IsBound(var)` 检查变量是否已绑定范围（第 177 行）。

### 5.4 ModularSet 模集合

225. `ModularSetNode` 类定义在 `include/tvm/arith/analyzer.h` 第 210-226 行，包含 `coeff`（系数）和 `base`（基数）两个 `int64_t` 字段。
226. ModularSet 表示集合 `{coeff * x + base | x in Z}`，当 coeff≠0 时等价于 `{n | n % coeff == base}`（第 202-208 行注释）。
227. `ModularSetNode` 的类型键为 `"arith.ModularSet"`（第 225 行）。
228. `ModularSetAnalyzer::operator()(expr)` 分析表达式的模信息（第 249 行）。
229. Python 端 `ModularSet` 类定义在 `python/tvm/arith/analyzer.py` 第 67-72 行，通过 `_ffi_api.ModularSet` 构造。
230. Python 端 `ConstIntBound` 类定义在 `python/tvm/arith/analyzer.py` 第 75 行。

### 5.5 RewriteSimplifier 重写化简器

231. `RewriteSimplifier` 类定义在 `include/tvm/arith/analyzer.h` 第 281-423 行，基于重写规则的表达式化简器。
232. `RewriteSimplifier::operator()(expr)` 对表达式进行化简（第 288 行）。
233. `RewriteSimplifier::Extension` 枚举定义了四个可选扩展（第 319-379 行）：
    - `kTransitivelyProveInequalities = (1 << 0)`：传递性证明不等式
    - `kConvertBooleanToAndOfOrs = (1 << 1)`：布尔表达式转合取范式
    - `kApplyConstraintsToBooleanBranches = (1 << 2)`：对布尔分支应用约束
    - `kComparisonOfProductAndSum = (1 << 3)`：乘积与和比较的特殊处理
234. `SetEnabledExtensions(flags)` 启用可选扩展，`GetEnabledExtensions()` 返回当前启用的扩展（第 386-389 行）。
235. `SetMaximumRewriteSteps(maximum)` 设置最大重写步数限制，超限抛异常（第 411 行）。
236. `GetStatsCounters()` 和 `ResetStatsCounters()` 提供统计计数器功能（第 392-395 行）。
237. Python 端 `Extension` 枚举定义在 `python/tvm/arith/analyzer.py` 第 54-64 行，值与 C++ 端对应。

### 5.6 CanonicalSimplifier 规范化简器

238. `CanonicalSimplifier` 类定义在 `include/tvm/arith/analyzer.h` 第 428-455 行，基于规范形式的化简器。
239. `CanonicalSimplifier::operator()(expr)` 对表达式进行规范化化简（第 435 行）。
240. `CanonicalSimplifier::Update(var, new_expr, allow_override)` 更新变量绑定（第 444 行）。

### 5.7 IntSet 整数集合

241. `IntSetNode` 基类定义在 `include/tvm/arith/int_set.h` 第 58-61 行，类型键为 `"ir.IntSet"`。
242. `IntSet` 引用类定义在 `include/tvm/arith/int_set.h` 第 67 行，提供集合操作接口。
243. `IntSet::CoverRange(max_range)` 查找覆盖集合的范围（第 74 行）。
244. `IntSet::min()` 和 `IntSet::max()` 返回集合的下界和上界（第 76-78 行）。
245. `IntSet::GetSignType()` 返回集合中元素的符号类型（`kPositive`/`kNegative`/`kZero`/`kUnknown`）（第 80 行）。
246. `SignType` 枚举定义在 `include/tvm/arith/int_set.h` 第 51 行。
247. `IntSet::IsNothing()`、`IsEverything()`、`IsSinglePoint()` 判断集合的特殊形态（第 82-86 行）。
248. `IntSet::CanProveSinglePoint(ana)` 使用分析器进行更强的单点证明（第 100 行）。
249. `IntSet::CanProvePositive/Negative/NonPositive/NonNegative()` 进行符号证明（第 104-110 行）。
250. `IntSet::Nothing()`、`Everything()`、`SinglePoint(point)`、`Vector(vec)`、`FromMinExtent(min, extent)` 是静态工厂方法（第 129-150 行）。
251. `IntSetAnalyzer` 类定义在 `include/tvm/arith/analyzer.h` 第 546-596 行，提供符号整数集合分析。
252. `IntSetAnalyzer::operator()(expr, dom_map)` 根据变量域映射分析表达式的整数集合（第 556 行）。
253. `IntSetAnalyzer::operator()(expr)` 使用已绑定变量的域映射分析（第 566 行）。
254. Python 端导出 `IntSet`、`IntervalSet`、`PresburgerSet`（`python/tvm/arith/__init__.py` 第 20-23 行）。
255. Python 端导出 `estimate_region_lower_bound`、`estimate_region_strict_bound`、`estimate_region_upper_bound`（`python/tvm/arith/__init__.py` 第 24-26 行）。

### 5.8 TransitiveComparisonAnalyzer 传递比较分析器

256. `CompareResult` 枚举定义在 `include/tvm/arith/analyzer.h` 第 462-471 行，包含 8 个值：`kInconsistent=0`、`kEQ=1`、`kLT=2`、`kLE=3`、`kGT=4`、`kGE=5`、`kNE=6`、`kUnknown=7`。
257. `CompareResult` 支持位运算 `&` 和 `|`（第 473-478 行）。
258. `TransitiveComparisonAnalyzer::TryCompare(lhs, rhs, propagate_inequalities)` 尝试使用已知比较传递性推导结果（第 505-506 行）。
259. Python 端 `CompareResult` 枚举定义在 `python/tvm/arith/analyzer.py` 第 38-51 行，值与 C++ 端对应。

### 5.9 Z3 证明器

260. `Z3Prover` 类定义在 `include/tvm/arith/analyzer.h` 第 598-700 行，基于 Z3 SMT 求解器。
261. `Z3Prover::IsEnabled()` 检查 Z3 后端是否编译启用（`USE_Z3=ON`）（第 623 行）。
262. `Z3Prover::CanProve(expr)` 尝试证明表达式恒真（第 631 行）。
263. `Z3Prover::GetSMTLIB2(expr)` 获取当前上下文的 SMTLIB2 表示（第 647 行）。
264. `Z3Prover::SetTimeoutMs(timeout_ms)` 设置超时（毫秒）（第 661 行）。
265. `Z3Prover::SetRLimit(rlimit)` 设置资源限制（第 668 行）。
266. `Z3Prover::GetModel(expr)` 获取可满足时的模型字符串（第 676 行）。
267. `Z3Prover::CountSatisfyingValues(var, max_count, min_consecutive)` 计算满足约束的整数值数量（第 689-690 行）。

### 5.10 IterAffineMap 迭代仿射映射

268. `IterMapExprNode` 定义在 `include/tvm/arith/iter_affine_map.h` 第 67-71 行，是所有迭代映射表达式的基类，类型键 `"arith.IterMapExpr"`。
269. `IterMarkNode` 定义在第 89-110 行，包含 `source`（源表达式）和 `extent`（迭代范围）字段。
270. 文件头注释说明了 Fuse（融合）和 Split（分割）两种映射模式（第 28-46 行）：
    - Fuse: `y = x2 * 12 + x1 * 4 + x0`
    - Split: `[y0, y1, y2] = [x % 3, (x % 12) / 3, x / 12]`
271. 术语"准仿射"（quasi-affine）与多面体编译术语一致，split 对应 floorDiv/mod 操作（第 42-46 行）。
272. Python 端导出 `IterMapExpr`、`IterMark`、`IterSplitExpr`、`IterSumExpr`（`python/tvm/arith/__init__.py` 第 32 行）。
273. Python 端导出 `detect_iter_map`、`iter_map_simplify`、`normalize_iter_map_to_expr`、`normalize_to_iter_sum`、`subspace_divide`、`inverse_affine_iter_map`（`python/tvm/arith/__init__.py` 第 33-39 行）。

### 5.11 Pattern Matcher 与 IntSolver

274. `DetectLinearEquation(e, vars)` 函数声明在 `include/tvm/arith/pattern.h` 第 40 行，检测表达式是否可写为 `sum(var[i]*coeff[i]) + coeff[n]`。
275. `DetectClipBound(e, vars)` 函数声明在 `include/tvm/arith/pattern.h` 第 50 行，检测 clip 边界模式。
276. Python 端导出 `detect_linear_equation` 和 `detect_clip_bound`（`python/tvm/arith/__init__.py` 第 30 行）。
277. `IntGroupBoundsNode` 定义在 `include/tvm/arith/int_solver.h` 第 58-76 行，包含 `coef`、`lower`、`equal`、`upper` 四个字段。
278. `kSimplifyRewriteCanonicalRewrite = 3` 常量定义在 `include/tvm/arith/int_solver.h` 第 47 行，表示最佳化简顺序为 can→rw→can→rw。
279. Python 端导出 `solve_linear_equations` 和 `solve_linear_inequalities`（`python/tvm/arith/__init__.py` 第 31 行）。

### 5.12 Bound 推导

280. `DeduceBound(v, cond, hint_map, relax_map)` 函数声明在 `include/tvm/arith/bound.h` 第 56-57 行，推导目标变量在条件约束下的边界。
281. `DeduceBound` 有 `ffi::Map` 和 `std::unordered_map` 两个重载版本（第 56、68 行）。
282. `DomainTouched(body, buffer, consider_loads, consider_stores)` 推断语句中所有访问覆盖的区域（第 80-81 行）。
283. Python 端导出 `deduce_bound`（`python/tvm/arith/__init__.py` 第 29 行）。

### 5.13 ProofStrength 证明强度

284. `ProofStrength` 枚举定义在 `include/tvm/arith/analyzer.h` 第 75-82 行：`kDefault=0`、`kSymbolicBound=1`。
285. 注释说明强度越高越耗时，内部递归重写不应使用超过 kDefault 的强度（第 72-73 行）。
286. `DivMode` 枚举定义在第 61-66 行：`kTruncDiv`（截断除法）和 `kFloorDiv`（向下取整除法）。
287. Python 端 `ProofStrength` 枚举定义在 `python/tvm/arith/analyzer.py` 第 31-35 行。

---

## 6. Support 基础库

### 6.1 Arena 分配器

288. `ArenaPageHeader` 结构体定义在 `src/support/arena.h` 第 56-65 行，包含 `next`（指向下一页）、`size`（页总大小）、`offset`（页内分配偏移）。
289. `GenericArena<PageAllocator>` 模板类定义在 `src/support/arena.h` 第 72 行，是 Arena 分配器的通用实现。
290. `GenericArena` 构造时预分配第一页（`src/support/arena.h` 第 74-78 行）。
291. `FreeAll()` 释放所有页链表（第 85-88 行），`RecycleAll()` 回收所有页到空闲列表（第 90-99 行）。
292. `allocate_<T>(count)` 模板方法从 Arena 分配类型 T 的数组空间（第 107-110 行）。
293. `TVM_ARENA_HAS_DESTRUCTOR` 宏控制是否启用析构函数，默认为 1（第 33-35 行）。
294. 文件注释说明 `GenericArena/ArenaPageHeader` 部分可移植到裸机嵌入式设备，不使用 `operator new` 或 `malloc`（第 26-28 行）。

### 6.2 Base64 编解码

295. Base64 解码表 `DecodeTable` 定义在 `src/support/base64.h` 第 41-52 行，共 128 项。
296. Base64 编码表 `EncodeTable` 定义在第 54-55 行，为标准 Base64 字母表 `"ABC...XYZabc...xyz012...789+/"`。
297. `StreamBufferReader` 类定义在第 62 行，提供带缓冲的流读取，避免每次读取的虚函数调用开销。
298. `StreamBufferReader::GetChar()` 方法从缓冲区读取单个字符，缓冲区耗尽时从源流重新填充（第 76-80 行）。

### 6.3 OrderedMap / OrderedSet

299. `OrderedMap<K,V,Hash,KeyEqual>` 模板类定义在 `src/support/ordered_map.h` 第 44-46 行，是保持插入顺序的 STL 风格映射。
300. OrderedMap 内部使用 `std::vector<std::pair<K,V>>` 存储元素，`std::unordered_map<K, size_t>` 存储键到索引的映射（第 78-83 行 `find` 方法可见）。
301. OrderedMap 显式定义拷贝构造函数，重新初始化 `elem_to_iter_` 以避免引用原始元素（第 57-59 行）。
302. OrderedMap 不支持 erase 操作，因为 vector 后备设计更高效（第 42 行注释）。
303. `OrderedSet<T,Hash,KeyEqual>` 模板类定义在 `src/support/ordered_set.h` 第 34 行，是保持插入顺序的集合实现。
304. OrderedSet 同样显式定义拷贝构造函数和拷贝赋值运算符（`src/support/ordered_set.h` 第 46-57 行）。

### 6.4 RingBuffer 环形缓冲区

305. `RingBuffer` 类定义在 `src/support/ring_buffer.h` 第 39 行，用于 IO 数据缓冲。
306. `kInitCapacity = 4 << 10`（4096 字节）是初始容量（第 42 行）。
307. `bytes_available()` 返回缓冲区中可用字节数，`capacity()` 返回当前容量（第 46-48 行）。
308. `Reserve(n)` 方法在 n 大于当前容量时扩容（新大小为 n*1.2），并处理环形数据的重叠拷贝（第 58-70 行）。
309. Reserve 还会在缓冲区过大（大于 n*8 且大于初始容量）时收缩，避免嵌入式设备内存溢出（第 71-80 行）。

### 6.5 Utils 工具函数

310. `TVMPOpen(command, type)` 函数定义在 `src/support/utils.h` 第 55-61 行，是 `popen`/`_popen` 的跨平台封装。
311. `TVMPClose(stream)` 函数定义在第 70-76 行，是 `pclose`/`_pclose` 的跨平台封装。
312. 这些函数在 `__hexagon__` 平台上不可用（通过 `#ifndef __hexagon__` 保护）。

### 6.6 环境变量

313. `GetEnv<T>(key, default_value)` 模板函数定义在 `src/support/env.h` 第 43-58 行，提供类型化的环境变量访问。
314. 支持 `std::string`、`bool` 和算术类型：bool 类型将 `"0"`/`"false"`/`"False"`/`"FALSE"` 视为 false（第 46-52 行）。
315. 环境变量未设置或为空时返回默认值（第 45 行）。

### 6.7 IO 流与序列化

316. `Stream` 抽象类定义在 `include/tvm/support/io.h` 第 57 行，是二进制序列化的核心接口。
317. `Stream` 声明纯虚函数 `Read(void* ptr, size_t size)` 和 `Write(const void* ptr, size_t size)`（第 65、73 行）。
318. `Stream` 提供模板方法 `Write<T>(data)` 和 `Read<T>(out_data)`，委托给 `Serializer<T>` 特化（第 83-99 行）。
319. 注释提醒子类重写 Read/Write 时需添加 `using Stream::Read;` 和 `using Stream::Write;` 以避免 C++ 名称隐藏（第 53-55 行）。
320. `Serializer<T>` 主模板定义在 `include/tvm/support/serializer.h` 第 42-44 行，默认 `enabled = false`。
321. 算术类型的 `Serializer` 特化定义在第 56-76 行，支持端序感知（通过 `TVM_FFI_IO_NO_ENDIAN_SWAP` 控制）。
322. 枚举类型的 `Serializer` 特化定义在第 80-94 行，委托给底层算术类型。
323. `std::string` 的 `Serializer` 特化定义在第 98-118 行，先写入 uint64_t 长度再写入原始字节。
324. serializer.h 内置支持算术类型、枚举、`std::string`、`std::vector<T>`、`std::pair<A,B>`、`std::unordered_map<K,V>`、`DLDataType`、`DLDevice`（第 24-29 行注释）。

---

## 7. TVMScript

### 7.1 Printer 体系

325. `Script(node, config)` 自由函数声明在 `include/tvm/script/printer/printer.h` 第 40-41 行，是 TVMScript 打印的入口。
326. 对于未注册到 TVMScriptPrinter 的类型，回退到 `ffi::ReprPrint`（第 38 行注释）。
327. `TVMScriptPrinter` 类定义在第 47-51 行，使用 `NodeFunctor<std::string(const ffi::ObjectRef&, const PrinterConfig&)>` 作为分发表类型。
328. `TVMScriptPrinter::vtable()` 静态方法返回分发表引用，各方言打印机通过它注册对象类型打印函数（第 50 行）。
329. `TVM_REGISTER_SCRIPT_AS_REPR(ObjectType, Method)` 宏定义在第 60-68 行，同时注册 Script 为 ObjectType 的 kRepr 回调并安装分发表条目。
330. `PrinterConfig` 定义在 `config.h` 中，通过 `#include <tvm/script/printer/config.h>` 引入（第 32 行）。

### 7.2 IR Builder 架构

331. IR Builder 头文件位于 `include/tvm/script/ir_builder/` 目录。
332. IR Builder 实现位于 `src/script/ir_builder/` 目录。
333. IR Builder 采用分层架构，为 TIR、Relax 等不同 IR 方言提供构建器。
334. Python 端 `tvm.script` 包通过 `python/tvm/script/__init__.py` 导出。

### 7.3 Doc 体系

335. Doc 体系实现在 `src/script/printer/doc.cc`，是 TVMScript 打印的中间表示。
336. Doc 体系将 IR 节点转换为结构化文档对象，再渲染为最终的 TVMScript 文本。

---

## 8. Driver 编译入口

### 8.1 build 函数

337. `build` 函数定义在 `python/tvm/driver/build_module.py` 第 31-60 行，接收 `mod`（PrimFunc 或 IRModule）、`target`、`pipeline` 参数。
338. `build` 函数已标记为废弃，推荐使用 `tvm.compile` 或 `tvm.tirx.build`（第 40、56-59 行）。
339. `build` 函数内部直接委托给 `tvm.tirx.build(mod, target, pipeline)`（第 60 行）。

### 8.2 compile 函数

340. `compile` 函数定义在 `python/tvm/driver/build_module.py` 第 72-112 行，是统一的编译入口。
341. `compile` 接收 `mod`、`target`、`relax_pipeline`（默认 `"default"`）、`tir_pipeline`（默认 `"default"`）参数。
342. `compile` 自动检测模块类型：若包含 Relax 函数则路由到 `tvm.relax.build`，否则调用 `tvm.tirx.build`（第 104-111 行）。
343. TIR-only 模块的编译结果包装为 `Executable` 对象返回（第 111-112 行）。
344. `_contains_relax(mod)` 辅助函数检测模块是否包含 Relax 函数：PrimFunc 返回 False，IRModule 检查所有函数（第 63-69 行）。

---

## 9. Python 绑定

### 9.1 Runtime 包

345. Python runtime 包入口 `python/tvm/runtime/__init__.py` 使用 `# isort: skip_file` 跳过导入排序（第 1 行）。
346. runtime 包从 `tvm_ffi` 导入 `convert`、`Object`、`dtype as DataType`、`DataTypeCode`（第 20-21 行）。
347. runtime 包导入 `_ffi_node_api` 以安装 AsRepr 作为 `__object_repr__`（第 25 行注释）。
348. 导出的类包括：`Scriptable`、`ObjectConvertible`、`Device`、`Tensor`、`tensor`、`empty`、`Module`、`Executable`（第 28-33 行）。
349. `ShapeTuple` 直接从 `tvm_ffi.Shape` 别名导入（第 54 行）。
350. `const` 函数从 `object_generic` 模块导出（第 39 行）。

### 9.2 Target 包

351. Python target 包入口 `python/tvm/target/__init__.py` 的文档字符串说明了四种 Target 构造方式（第 20-26 行）：
    - 配置字典：`Target({"kind": "cuda", "arch": "sm_80"})`
    - 标签名：`Target("nvidia/nvidia-a100")`
    - 带覆盖的标签：`Target({"tag": "nvidia/nvidia-a100", "l2_cache_size_bytes": 12345})`
    - kind 名称：`Target("cuda")`
352. target 包导出 `Target`、`TargetKind`、`VirtualDevice`、`list_tags`、`register_tag`（第 34-36 行）。
353. `codegen` 和 `tag_registry` 子模块在 `__init__.py` 中导入，`tag_registry` 导入时自动注册标签（第 37-38 行）。

### 9.3 Arith 包

354. Python arith 包入口 `python/tvm/arith/__init__.py` 文档字符串为"Integer bound analysis, simplification and pattern detection."（第 18 行）。
355. arith 包导出 `IntSet`、`IntervalSet`、`PresburgerSet` 及区域边界估计函数（第 20-26 行）。
356. arith 包导出 `ModularSet`、`ConstIntBound`、`Analyzer`、`ProofStrength`、`Extension`、`CompareResult`（第 28 行）。
357. `Analyzer` 类在 `python/tvm/arith/analyzer.py` 中定义，是 C++ `arith::Analyzer` 的 Python 绑定。
358. Python `CompareResult` 枚举值：`INCONSISTENT=0`、`EQ=1`、`LT=2`、`LE=3`、`GT=4`、`GE=5`、`NE=6`、`UNKNOWN=7`（第 44-51 行），与 C++ 端一一对应。
359. Python `Extension` 标志值：`NoExtensions=0`、`TransitivelyProveInequalities=1<<0`、`ConvertBooleanToAndOfOrs=1<<1`、`ApplyConstraintsToBooleanBranches=1<<2`、`ComparisonOfProductAndSum=1<<3`（第 60-64 行）。

### 9.4 FFI 基础设施

360. TVM Python 绑定基于 `tvm_ffi` 包，使用 `@tvm_ffi.register_object("type.key")` 装饰器注册 C++ 对象类型（`python/tvm/runtime/module.py` 第 108 行）。
361. `_ffi_api` 模块提供 C++ FFI 函数的 Python 绑定，各子模块通过 `from . import _ffi_api` 引入。
362. Python `Module` 类通过 `@_register_object("ffi.Module")` 覆盖 ffi 包中的 Module 类（`python/tvm/runtime/module.py` 第 108 行）。
363. `tvm_ffi.libinfo` 提供库信息查询，runtime 模块从中导入 `libinfo as tvm_ffi_libinfo`（`python/tvm/runtime/module.py` 第 31 行）。

---

## 附录：文件索引

| 模块 | 头文件目录 | 源文件目录 | Python 目录 |
|---|---|---|---|
| Runtime | `include/tvm/runtime/` | `src/runtime/` | `python/tvm/runtime/` |
| VM | `include/tvm/runtime/vm/` | `src/runtime/vm/` | `python/tvm/runtime/vm.py` |
| RPC | `src/runtime/rpc/` | `src/runtime/rpc/` | `python/tvm/rpc/` |
| Target | `include/tvm/target/` | `src/target/` | `python/tvm/target/` |
| LLVM 后端 | - | `src/target/llvm/` | - |
| C 源码后端 | - | `src/target/source/` | - |
| Arith | `include/tvm/arith/` | `src/arith/` | `python/tvm/arith/` |
| Support | `include/tvm/support/` | `src/support/` | - |
| Script | `include/tvm/script/` | `src/script/` | `python/tvm/script/` |
| Driver | - | - | `python/tvm/driver/` |
