---
title: "TVM FFI 200 视角深度解读"
type: "Wiki Bundle Index"
okf_version: "0.2"
generated: 2026-08-23
---

# TVM FFI 200 视角深度解读

> 基于 TVM FFI 源码的 200 个技术视角，系统性解读跨语言函数接口设计与实现。

## 项目概览

- **总视角数**: 200
- **分类数**: 15
- **源码路径**: `d:\AI\.chaos\libs\ffi`
- **方法论**: seven-concepts 知识沉淀链路 + source-code-to-okf-wiki 五阶段

## 分类导航

| 编号 | 分类 | 视角数 | 说明 |
|------|------|--------|------|
| 01 | [架构与设计哲学](01-architecture/index.md) | 15 | 分层设计、类型擦除、ABI稳定性、最小核心等 |
| 02 | [核心类型系统](02-core-types/index.md) | 20 | Any/Object/TypeIndex/DataType/Cast等 |
| 03 | [函数与调用系统](03-functions/index.md) | 15 | Packed Function/全局注册表/回调/错误传播 |
| 04 | [容器系统](04-containers/index.md) | 15 | Array/List/Map/Dict/String/Tuple/Variant等 |
| 05 | [Tensor与DLPack](05-tensor-dlpack/index.md) | 10 | Tensor对象/零拷贝/DLManagedTensor（含NPU建议） |
| 06 | [错误处理系统](06-error-handling/index.md) | 10 | Error对象/栈回溯/因果链/TLS错误状态 |
| 07 | [反射系统](07-reflection/index.md) | 15 | VTable/ObjectDef/字段注册/结构化相等哈希 |
| 08 | [C++实现细节](08-cpp-impl/index.md) | 15 | 模板元编程/内联优化/原子操作/分配器等 |
| 09 | [Python绑定](09-python/index.md) | 15 | Cython/_ffi_api/注册表/GIL/类型存根 |
| 10 | [Rust绑定](10-rust/index.md) | 10 | crate结构/sys绑定/安全包装/所有权/unsafe |
| 11 | [C ABI与平台](11-c-abi-platform/index.md) | 10 | ABI稳定性/对齐/兼容性/DLL/WASM（含NPU建议） |
| 12 | [构建与打包](12-build-package/index.md) | 10 | CMake/Cython/Wheel/多版本/依赖管理 |
| 13 | [测试策略](13-testing/index.md) | 10 | GoogleTest/pytest/覆盖分析/CI/CD |
| 14 | [TVM编译器集成](14-tvm-integration/index.md) | 15 | 运行时/TIR/Relax/Pass/VM/RPC（含NPU建议） |
| 15 | [NPU与加速器建议](15-npu-accelerator/index.md) | 15 | NPU集成全场景建议（全部含NPU建议） |

## 文档结构

每个分类目录为一个 OKF bundle，包含：

```
分类目录/
├── index.md          # 分类索引
├── log.md            # 变更日志
├── concepts/         # 概念文档（按视角编号）
└── references/       # 参考资源
    └── sources.md    # 信源清单（源码路径+API）
```

## 质量门

- **G1**: 事实零推测，每条事实有源码行号引用
- **G2**: 洞察四元组完整（陈述+证据+反常识+行动）
- **G3**: 信源先行，references 先于 concepts 创建
- **G4**: Grep 级 API 验证，0 个虚构 API

## 相关资源

- [实施计划](../../.trae/specs/tvm-ffi-200-perspectives/tasks.md)
- [事实清单](../../.trae/specs/tvm-ffi-200-perspectives/supporting-analysis/facts.md)
