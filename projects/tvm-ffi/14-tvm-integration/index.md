# TVM编译器集成

> 分类编号：14-tvm-integration | 视角数量：15 篇

## 概述

本分类展示 TVM 编译器中的 FFI 集成实践，包括 TVM 运行时 FFI 应用、TIR 表达式系统、Relax IR、Pass 基础设施、Module 系统、RPC 服务、虚拟机、字节码执行、KV State、目标代码生成注册、TOPI/TE 等。

## 概念文档

> 按视角编号排序，共 15 篇。

| 编号 | 概念文档 | 简述 |
|------|----------|------|
| 171 | [TVM 运行时 FFI 应用](concepts/171-tvm-runtime-ffi-application.md) | pack_args.h 将 ffi::PackedArgs 适配为多种设备调用约定 |
| 172 | [TIR 表达式与 FFI](concepts/172-tir-expression-ffi.md) | TypeNode/PrimType 继承 ffi::Object 与反射注册 |
| 173 | [Relax IR 与 FFI](concepts/173-relax-ir-ffi.md) | Relax 三类节点统一落在 FFI 对象模型 |
| 174 | [Pass 基础设施](concepts/174-pass-infrastructure.md) | PassContext/Pass/Sequential 的 FFI 对象化 |
| 175 | [Module 系统集成](concepts/175-module-system-integration.md) | ffi::Module 承载 IRModule/VMExecutable/RPC 模块 |
| 176 | [RPC 服务端/客户端](concepts/176-rpc-server-client.md) | RPCSession/RPCChannel/RPCEndpoint 与远程句柄管理（含 NPU 建议） |
| 177 | [虚拟机 VM](concepts/177-virtual-machine-vm.md) | VirtualMachine 继承 ffi::ModuleObj 与 VMExtension（含 NPU 建议） |
| 178 | [字节码执行](concepts/178-bytecode-execution.md) | Opcode/Instruction 与 VMExecutable 序列化（含 NPU 建议） |
| 179 | [KV State 管理](concepts/179-kv-state-management.md) | AttentionKVCache/RNNState 的 FFI 状态对象（含 NPU 建议） |
| 180 | [目标代码生成注册](concepts/180-target-codegen-registration.md) | TargetKindRegistry/TagRegistry 与 refl::GlobalDef（含 NPU 建议） |
| 181 | [TOPI 算子库](concepts/181-topi-op-library.md) | 算子经 refl::GlobalDef 集中登记 |
| 182 | [TE 张量表达式](concepts/182-te-tensor-expression.md) | Tensor/Operation 的 DataProducer 层级 |
| 183 | [Arith 简化器](concepts/183-arith-simplifier.md) | Analyzer/IntSetAnalyzer/ConstraintContext |
| 184 | [Source Map](concepts/184-source-map.md) | SourceMap/SourceName/Span 的源码定位 |
| 185 | [Instrument 性能分析](concepts/185-instrument-performance-analysis.md) | PassInstrument/Timer/VMInstrument 探针（含 NPU 建议） |

## 参考资源

- [信源清单](references/sources.md) - 本分类相关源码路径与API清单
- [变更日志](log.md) - 文档变更历史记录
