---
type: Concept
title: "视角193：NPU 自定义算子注册"
description: "讲解 NPU 自定义算子如何注册为可被调度的 FFI 全局函数与可被自省的自定义类型，覆盖全局函数注册、类型/字段/方法注册与运行时类型索引的分配。"
tags:
  - npu
  - custom-op
  - registration
  - reflection
  - global-function
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-141, F-142, F-261, F-343
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/function.h
---

# 视角193：NPU 自定义算子注册

## 概述

NPU 算子要参与编译与运行时调度，必须完成两类注册：一是把算子实现注册为可调用的全局函数，二是把算子相关的自定义数据结构注册为可自省的类型，供反射与语言绑定分析。TVM FFI 的反射体系（`reflection/registry.h`）与 `c_api.h` 的类型注册入口共同支撑这两类需求。本视角拆解自定义算子注册的完整路径。

## 全局函数注册：算子的可调用入口

算子实现首先以"名字→函数"的形式进入全局注册表，本 fork 统一采用 `refl::GlobalDef().def(name, func)`，例如 `target_kind.cc` 用其注册目标属性查询、`module.cc:169` 用其注册 `ffi.ModuleLoadFromFile`。注册后算子可由

```cpp
Function::GetGlobalRequired("npu.op.<opname>")   // function.h:456
```

按名取回。`ListGlobalNames()`（`function.h:511`）支持枚举，用于算子清单的审查与导出。Python 绑定侧由 `register_global_func`（视角120）提供等价的声明式入口。

## 类型注册：算子的数据结构自省

若算子附带自定义参数对象（如内核句柄、维序配置），需要注册其类型信息。`c_api.h` 提供一组运行时类型注册入口：

- `TVMFFITypeRegisterField(:1408)`：注册字段。
- `TVMFFITypeRegisterMethod(:1414)`：注册方法。
- `TVMFFITypeRegisterMetadata(:1420)`：注册元数据。
- `TVMFFITypeRegisterAttr(:1426)`：注册属性。

配合 `TVMFFITypeGetOrAllocIndex(:1487)` 在首次使用时分配运行时类型索引、`TVMFFIGetTypeInfo(:1498)` 查询已注册类型的完整描述，构成与 C++ 侧 `ObjectDef` 构建器（视角090）对应的运行时等价物。C++ 侧可直接用 `refl::GlobalDef`/`ObjectDef` 的宏在编译期完成等量注册。

## 两套注册的分工

- **函数注册**决定"算子能不能被调用"——进全局注册表，可被任意语言按名取用。
- **类型注册**决定"算子的参数能不能被理解"——进类型索引，可被反射、存根生成（视角100）、语言绑定正确序列化。

NPU 算子规范地同时完成两者，才能以一等公民身份参与推理/训练调度。

## 设计分析

1. **函数与类型两条注册线正交**：函数注册管调用，类型注册管理解，缺一不可。
2. **运行时类型索引按需分配**：`GetOrAllocIndex` 惰性登记，降低冷启动成本，也让"只被偶尔使用的算子类型"不占用额外索引。
3. **编译期与运行时注册可互为补充**：C++ 侧编译期 `ObjectDef` 最高效，跨语言或动态生成的类型则走运行时注册。

## NPU建议

1. 为每个 NPU 算子在全局注册表中登记，命名空间统一为 `npu.op.<opname>`，并声明签名元数据，保证 `GetGlobalRequired` 与 `ListGlobalNames` 可用。

2. 算子附带的参数对象通过 `TVMFFITypeRegisterField`/`TVMFFITypeRegisterMethod` 注册字段与方法，使用 `TVMFFITypeGetOrAllocIndex` 惰性分配索引，不热抢资源。

3. 若绑定类型在编译期已知，优先用 C++ 侧 `ObjectDef` 构建器注册，保证效率；对跨语言/动态生成的算子参数类型走运行时注册入口。

4. 用元数据入口（`TVMFFITypeRegisterMetadata`）登记算子参数的结构化说明（维度、数据类型、对齐要求），供前端校验与文档生成消费。

5. 为算子提供全局函数清单自检：装载后调用 `ListGlobalNames` 比对预期集合，防止内核缺失导致调度期才发现错误。

6. 以 Python 装饰器形式（对齐 `register_global_func` 视角120使用习惯）提供 NPU 算子的声明式注册包装，降低插件作者接入成本。

## 相关概念

- [040 全局函数注册表](/03-functions/concepts/040-global-function-registry.md)
- [090 ObjectDef 构建器](/07-reflection/concepts/090-object-def-builder.md)
- [089 TypeInfo 运行时类型](/07-reflection/concepts/089-type-info.md)
- [188 NPU 内核库发布](188-npu-kernel-library-publishing.md)