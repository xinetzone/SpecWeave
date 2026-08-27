---
type: Concept
title: "视角187：VTA 类加速器设计"
description: "分析相似于 VTA 的通用可编程加速器如何以运行时模块形态融入 TVM FFI，以 CUDA 模块为模板拆解 kind 标识、属性掩码、函数分发与按设备索引管理实例等设计要点。"
tags:
  - npu
  - vta
  - accelerator
  - module-design
  - kind-key
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-301, F-304
  - code:
    - ../../tvm/src/backend/cuda/runtime/cuda_module.cc
    - include/tvm/ffi/extra/module.h
---

# 视角187：VTA 类加速器设计

## 概述

VTA（Versatile Tensor Accelerator）是一类可编程通用加速器：算子已编译为特定格式的机器码或配置流，运行时只需"加载 + 执行"。这类加速器的核心诉求是：让运行时把一个二进制/字节串解析为一个可调用的 `ffi::Function`。TVM FFI 的模块抽象（`ffi::Module`）正是为此设计，而 CUDA 模块（`CUDAModuleNode`）是离 VTA 最近的现成模板。本视角以模块为纲，拆解加速器接入的关键设计点。

## 模块的三要素设计

`module.h` 定义了一个加速器运行时模块必须实现的三个基本虚函数：

1. **`kind()`（`module.h:49`）**：返回模块类型的字符串键，如 CUDA 返回 `"cuda"`（`cuda_module.cc:90`）。该键被用于模块序列化分发，也是区分不同加速器运行时的身份标识。VTA 类加速器应返回自己唯一的 kind，如 `"vta"` 或 `"npu"`。
2. **`GetPropertyMask()`（`module.h:56`）**：返回模块能力位掩码。CUDA 返回 `kBinarySerializable | kRunnable`，即既能被保存为二进制又可直接获取可执行函数。
3. **`GetFunction(const String& name)`（`module.h:62`）**：按名字从模块取出可调用的 `ffi::Function`。

## 函数分发与按设备索引

正确性关键在 `GetFunction` 的分发逻辑。`cuda_module.cc:333` 的实现先从函数手册 `fmap_` 中按名查找签名信息，找不到则返回空函数：

```cpp
ffi::Optional<ffi::Function> CUDAModuleNode::GetFunction(const ffi::String& name) {
  auto opt_info = fmap_.Get(name);
  if (!opt_info.has_value()) return ffi::Function();
  // ... 绑定参数类型与启动参数，返回 PackFuncVoidAddr 包装的可调用函数
}
```

CUDA 模块内部维护一张**按设备 ID 索引**的 cuModule 表（`module_[device_id]`），`cuModuleGetFunction` 依据当前设备的句柄取内核。这一"per-device 实例表 + 惰性加载"的结构，是 VTA 类多实例加速器的直接参照。

## 惰性加载与 JIT 编译

CUDA 模块把"保存源码 + 事后 JIT"作为一等能力：当传入的格式是源码时，`CUDAModuleCreateImpl`（`cuda_module.cc:350-360`）先保存源码再通过 `JitCompileFromSource` 产出已编译字节。`SaveToBytes`（`cuda_module.cc:99`）仅序列化可反序列化的载荷，源码映射在往返中会被丢弃。这给加速器两点启示：一是把"对外界面"与"内部编译细节"分离；二是可追溯性（如 `InspectSource`）作为独立可选能力实现。

## 设计分析

1. **字符串 kind 是弱类型分发键**：模块工厂通过 kind 找到 `ffi.Module.create.<kind>` 全局注册函数，这要求 kind 全局唯一且稳定，一旦发布不可随意改动。
2. **属性掩码驱动序列化框架**：`kBinarySerializable` 决定是否注册 `ffi.Module.load_from_bytes.<kind>`；`kRunnable` 决定函数是否可直接执行。掩码是框架自动化的开关。
3. **per-device 表是多实例的自然结构**：加速器常有多张卡，把内核句柄按 device_id 分槽，天然支持多设备复用同一份模块对象。

## NPU建议

1. 为 NPU 运行时实现一个 `NPUModuleNode : public ffi::ModuleObj`，返回 `kind()` 为 `"npu"`，并实现 `GetFunction`/`GetPropertyMask`/`SaveToBytes`。

2. 用掩码精确声明能力，例如只声明 `kRunnable`（纯执行）或叠加 `kBinarySerializable`（需要序列化保留内核），避免声明未实现的能力导致框架误用。

3. 内部采用 `std::map<DeviceID, KernelHandle>` 按 device_id 分槽存储已加载内核，首次访问某设备时才加载（惰性加载），释放时按槽清理。

4. 若 NPU 内核需要源码态保留（如便于 `InspectSource` 审查），把源码与二进制分开存储，并在序列化时明确哪些数据会在往返中丢失，参考 CUDA 的注释约定。

5. 通过 `refl::GlobalDef().def("ffi.Module.create.npu", ...)` 注册创建工厂，并让创建函数接受统一的载荷参数（字节、格式、函数签名表），保持工厂界面与框架一致。

6. 若支持从磁盘加载预编译内核，务必实现 `ffi.Module.load_from_bytes.npu`，与创建键成对注册。

## 相关概念

- [194 NPU 运行时模块加载](194-npu-runtime-module-loading.md)：模块加载完整流程
- [186 NPU FFI 集成总览](186-npu-ffi-integration-overview.md)：集成四层地图
- [048 模块入口点约定](/03-functions/concepts/048-module-entry-point-convention.md)
- [036 Packed Function 约定](/03-functions/concepts/036-packed-function-convention.md)