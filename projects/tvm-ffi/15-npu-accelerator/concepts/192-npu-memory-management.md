---
type: Concept
title: "视角192：NPU 内存管理"
description: "阐述 NPU 设备内存管理的分层模型：对象引用计数、宿主观测的生命周期、NDAllocator 设备无关分配，以及如何嵌入命令队列的异步释放优化。"
tags:
  - npu
  - memory-management
  - refcount
  - allocator
  - ownership
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-019, F-060, F-180, F-285, F-298, F-299
  - code:
    - include/tvm/ffi/object.h
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/container/tensor.h
---

# 视角192：NPU 内存管理

## 概述

NPU 内存（片上 SRAM、显存、主机 pinned 内存）是稀缺资源，其生命周期管理决定系统是否泄漏或悬垂。TVM FFI 提供三层治理：对象级引用计数（`IncRef`/`DecRef`）、宿主观测分配器（`NDAllocator`）、以及跨 FFI 边界的对象所有权协议（视角013）。NPU 内存管理应复用这三层，并在底层嵌入设备特有的分配/释放原语。

## 引用计数：对象生命周期之锚

FPI 对象（含张量、模块）通过引用计数管理生命周期。C ABI 暴露 `TVMFFIObjectIncRef(:557)` 与 `TVMFFIObjectDecRef(:564)`，任何持有多语言的引用都必须与之对应。对 NPU 内存而言，宿主持有对象的时段内引用计数必须为正，释放时归零才触发真正回收，这一契约由视角030的包装器与 deleter 协同保证。

## NDAllocator：设备无关的分配

NPU 的不确定性在于"如何分配归谁分配"。`tensor.h` 的 `TensorObjFromNDAlloc`（`tensor.h:184`）把分配完全委托给外界传入的分配器对象（类似视角112的 AOR 思想），其 `AllocData` 负责在构造时用设备 API 分配数据指针，模板参数 `ExtraArgs` 透传流等附加信息。核心张量不感知任何设备，新增设备类型只需实现分配器接口——这正是视角066阐述的设备无关分配。

## 异步释放与流绑定

NPU 内存的释放常与命令队列耦合：某内存可能仍被尚未执行完的命令引用，直接同步 `free` 会造成竞争。合理做法是把释放操作延迟到该内存最后使用的命令队列/流排空之后。分配器持有流的句柄，在 `FreeData` 中把释放追加为流上的回调而非立即执行，从而在正确性与性能间取得平衡。

## 多级内存池

根据 NPU 内存层次（设备内存 / 主机 pinned / 片上 scratchpad），建议为每种类型实现独立分配器，或在一个分配器内按类型分池。`Tensor::FromNDAlloc`（`tensor.h:470`）接收 `DLDevice` 参数，使分配器能依据目标设备与内存类型分发到正确的池。

## 设计分析

1. **引用计数解决"谁持有"，分配器解决"谁来分配"**：两者正交，便于映射到不同内存策略的开闭扩展（池化、缓存、统配均可插拔）。
2. **异步释放把正确性与性能统一**：延迟释放不是妥协而是利用队列顺序消除竞争的最佳实践。
3. **设备无关的核心得益于分配器抽象**：新增 NPU 内存类型不触碰张量核心，符合开闭原则。

## NPU建议

1. 为 NPU 内存实现分配器族，每种内存类型一个 `AllocData`/`FreeData` 实现：设备内存调 `npu_malloc`/`npu_free`，主机 pinned 内存调类似 `cudaMallocHost` 的 API，片上 scratchpad 从 SRAM 池分配。

2. 通过 `Tensor::FromNDAlloc` 创建张量时把目标 `DLDevice` 与设备特有的 `ExtraArgs`（如所属流）传入分配器，使 data 指针落在正确设备。

3. 实现流绑定的异步释放：分配器持有流句柄，`FreeData` 把 `npu_free` 作为回调追加到该流尾而非同步执行，消除与在飞命令的资源竞争。

4. 复用 `TVMFFIObjectIncRef`/`TVMFFIObjectDecRef` 治理张量/对象的跨语言持有；在跨 FFI 传参时显式配对增减引用，避免内存被提前回收或泄漏。

5. 对多级内存设立不同的分配策略开关（池化 vs 即时分配），通过构建配置或运行时选项暴露，供不同场景调优。

6. 把内存使用统计（总/空闲/峰值）实现为 `npu.memory_info` 全局函数，作为容量规划与泄漏定位的观测入口。

## 相关概念

- [013 内存所有权模型](/01-architecture/concepts/013-memory-ownership-model.md)
- [066 Tensor 对象设计](/05-tensor-dlpack/concepts/066-tensor-object-design.md)
- [031 Deleter 析构机制](/02-core-types/concepts/031-deleter.md)
- [191 NPU 命令队列](191-npu-command-queue.md)