---
type: source-code
source_id: runtime-target-arith
title: Runtime/Target/Arith/Support 源码
description: TVM Runtime 执行引擎、Target 多后端系统、Arith 编译期证明引擎与 Support 工具库源码登记
tags: [tvm, runtime, target, arith, support, source, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: blackbox-validator/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: facts-runtime-target-arith
    resource: "/references/facts-runtime-target-arith.md"
    title: Runtime/Target/Arith 事实清单
---

# Runtime/Target/Arith/Support 源码登记

- **source_id**: runtime-target-arith
- **type**: source-code
- **path**: `d:\AI\.chaos\libs\ffi\tvm\`
- **language**: C++/Python
- **file_count**: 332
- **fact_file**: /references/facts-runtime-target-arith.md
- **registered**: 2026-08-23

## 目录结构

| 目录 | 文件数 | 职责 |
|------|--------|------|
| `src/runtime/` | 159 | Runtime C++ 实现：DeviceAPI、NDArray、Module、线程池、VM 虚拟机、RPC |
| `src/target/` | 40 | Target 与代码生成 C++ 实现：Target/TargetKind、CodeGenLLVM/CodeGenC、各后端 |
| `src/arith/` | 33 | Arith 编译期证明引擎：Analyzer、ConstIntBound、ModularSet、RewriteSimplify、Z3Prover |
| `src/support/` | 15 | 基础工具库 |
| `src/script/` | 16 | TVMScript 前端 |
| `include/tvm/runtime/` | 16 | Runtime 公共头文件 |
| `include/tvm/target/` | 5 | Target 公共头文件 |
| `include/tvm/arith/` | 6 | Arith 公共头文件 |
| `include/tvm/support/` | 3 | Support 公共头文件 |
| `python/tvm/runtime/` | 15 | Runtime Python 绑定 |
| `python/tvm/target/` | 13 | Target Python 绑定 |
| `python/tvm/arith/` | 8 | Arith Python 绑定 |
| `python/tvm/driver/` | 3 | Driver 编译入口（compile/build_module） |

## 关键文件

### Runtime 核心

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/runtime/base.h` | 版本号（0.26.dev0）、DLDataType/DLDevice、TVM_DLL 导出宏 |
| `include/tvm/runtime/device_api.h` | DeviceAPI 抽象基类：SetDevice/GetAttr/AllocDataSpace/FreeDataSpace/CopyDataFromTo |
| `include/tvm/runtime/tensor.h` | Tensor 类：DLTensor 托管封装、CopyFrom/CopyTo/CreateView/Empty |
| `src/runtime/device_api.cc` | DeviceAPIManager 单例、设备注册 |
| `src/runtime/cpu_device_api.cc` | CPU 设备 API（malloc/free） |
| `src/runtime/tensor.cc` | NDArray 引用计数与跨设备拷贝 |
| `src/runtime/thread_pool.cc` | 多线程线程池 |
| `src/runtime/workspace_pool.cc` | 设备工作区池化复用 |
| `src/runtime/module.cc` | RuntimeEnabled、模块加载 |
| `include/tvm/runtime/logging.h` | TVM_FFI_ICHECK/TVM_FFI_THROW 断言与异常宏 |
| `include/tvm/runtime/timer.h` | 高精度定时器 |

### VM 虚拟机

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/runtime/vm/vm.h` | VirtualMachine 核心：Init/LoadExecutable/RunLoop/InvokeBytecode |
| `include/tvm/runtime/vm/bytecode.h` | Opcode 枚举（Call/Ret/Goto/If）、Instruction 结构体 |
| `include/tvm/runtime/vm/executable.h` | Executable：字节码/常量池/函数表序列化、jit() |
| `src/runtime/vm/vm.cc` | VM 指令调度主循环 |
| `src/runtime/vm/executable.cc` | Executable 序列化实现 |
| `src/runtime/vm/builtin.cc` | VM 内建函数 |
| `src/runtime/vm/paged_kv_cache.cc` | 分页式 KV 缓存（LLM 推理） |
| `src/runtime/vm/attn_backend.cc` | 注意力计算后端抽象 |
| `python/tvm/runtime/vm.py` | Python VirtualMachine（NAIVE/POOLED 分配器） |

### RPC 远程调用

| 文件路径 | 职责 |
|---------|------|
| `src/runtime/rpc/rpc_session.h` | RPCSession：远程函数调用与对象生命周期 |
| `src/runtime/rpc/rpc_endpoint.h` | RPCEndpoint：消息收发 |
| `src/runtime/rpc/rpc_channel.h` | RPCChannel：底层通信通道抽象 |
| `src/runtime/rpc/rpc_module.cc` | RPCModule：远程设备 Module 统一接口 |

### Target 与代码生成

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/target/target.h` | TargetNode（kind/host/tag/keys/attrs）、Target 引用类、Current() 上下文 |
| `include/tvm/target/target_kind.h` | TargetKindNode（name/default_device_type/default_keys/schema_） |
| `src/target/target.cc` | Target 创建（String/Map/Tag）、线程局部上下文栈、ToConfig |
| `src/target/target_kind.cc` | TargetKind 注册表、TVM_REGISTER_TARGET_KIND 宏、LLVM/C/CUDA/composite 注册 |
| `src/target/codegen.cc` | codegen::Build 分派、ModuleSerializer、PackImportsToC/LLVM/Bytes |
| `src/target/llvm/codegen_cpu.h` | CodeGenCPU：LLVM CPU 后端 |
| `src/target/llvm/codegen_llvm.h` | CodeGenLLVM 基类（ExprFunctor + StmtFunctor） |
| `src/target/source/codegen_c.h` | CodeGenC：C 源码后端基类（CUDA/OpenCL/Metal/Vulkan 共用） |
| `src/target/source/codegen_c_host.h` | CodeGenCHost：主机 C 后端 |

### TargetTag 与 VirtualDevice

| 文件路径 | 职责 |
|---------|------|
| TargetTag 系统 | 命名预设配置（AddTag/ListTags/GetConfig），如 "nvidia/nvidia-a100" |
| VirtualDevice | device_type/device_id/target/memory_scope 四元组 |

### Arith 编译期证明引擎

| 文件路径 | 职责 |
|---------|------|
| `include/tvm/arith/analyzer.h` | AnalyzerObj：七个子分析器组合、Bind/CanProve/Simplify |
| `src/arith/const_int_bound.cc` | ConstIntBoundAnalyzer：min_value/max_value、kPosInf/kNegInf |
| `src/arith/modular_set.cc` | ModularSetAnalyzer：{coeff*x+base} 模集合分析 |
| `src/arith/rewrite_simplify.cc` | RewriteSimplifier：基于重写规则的化简 |
| `src/arith/canonical_simplify.cc` | CanonicalSimplifier：规范形式化简 |
| `src/arith/int_set.cc` | IntSetAnalyzer：整数集合分析 |
| `src/arith/transitive_comparison.cc` | TransitiveComparisonAnalyzer：8 种比较结果传递 |
| `src/arith/z3_prover.cc` | Z3Prover：可选 SMT 后端（USE_Z3=ON） |
| `src/arith/iter_affine_map.cc` | IterAffineMap：Fuse/Split 准仿射映射 |
| `ConstraintContext` | RAII 临时约束作用域，EnterConstraint/ExitConstraint |

### Support 工具库

| 文件路径 | 职责 |
|---------|------|
| `src/support/` | 基础工具：arena.h（内存池）、base64.h、env.h、limits.h、pipe.h、socket.h、ssize.h、utils.h |

### Driver 编译入口

| 文件路径 | 职责 |
|---------|------|
| `python/tvm/driver/build_module.py` | build()：TIR 编译入口 |
| `python/tvm/driver/driver_api.py` | compile()：自动检测模块类型，含 Relax 函数路由到 relax.build，否则 tirx.build |
