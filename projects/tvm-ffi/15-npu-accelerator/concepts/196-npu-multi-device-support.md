---
type: Concept
title: "视角196：NPU 多设备支持"
description: "探讨 NPU 多设备（多卡）支持的设计，以 DLDevice.device_id 为键、per-device 实例表为结构，覆盖设备解析、拓扑亲和与跨设备拷贝策略。"
tags:
  - npu
  - multi-device
  - device-id
  - topology
  - device-affinity
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-005, F-230, F-231
  - code:
    - include/tvm/ffi/device.h
    - include/tvm/ffi/c_api.h
    - ../../tvm/src/backend/cuda/runtime/cuda_module.cc
---

# 视角196：NPU 多设备支持

## 概述

现代 NPU 通常以多卡形态部署，"多设备支持"指运行时能正确区分、调度并迁移多块 NPU 上的数据与内核。TVM FFI 以 `DLDevice.device_id` 作为设备唯一键，TVM 的多卡实现提供了 per-device 实例表的范式。本视角聚焦设备标识、实例管理、拓扑亲和与跨设备拷贝。

## 设备标识的解析与规范

`DLDevice` 含 `device_type` 与 `device_id` 两个字段（`dlpack.h:128`）。`device.h` 提供 `TryParseDLDeviceType`（`device.h:41`）与 `TryParseDLDeviceIndex`（`device.h:57`）分别解析类型与编号，`TryStringViewToDLDevice`（`device.h:68`）合成完整解析。设计上应保证 `device("npu:2")` 的编号 2 与底层驱动第二块设备的句柄一一对应，且同设备多次解析结果稳定相等。

## per-device 实例管理

多设备支持在实现层通常表现为"按 device_id 分槽的实例表"。CUDA 模块维护 `module_[device_id]` 的 cuModule 表，`GetFunction` 时以当前设备 ID 取对应内核句柄（`cuda_module.cc:333`）。该结构保证：

- 每张卡的上下文独立，互不串扰；
- 惰性创建：首次用到某卡才初始化其句柄；
- 释放时按槽清理，避免资源残留。

## 拓扑与亲和性

多 NPU 的互联拓扑（NVLink 类高速互连 / 普通 PCIe / 是否存在 P2P）决定数据交换成本。`device_id` 是查询拓扑矩阵的键。框架在张量分配与算子调度时应考虑设备亲和性：P2P 可用的设备对可零拷贝共享 data 指针，否则需经主机内存中转。

## 跨设备拷贝

跨设备张量迁移通过 `enum`/修改设备信息的拷贝原语完成。参考视角190的交换机制，跨设备时分配目标设备张量并提交 DMA 拷贝，同设备内直接返回以免无谓复制；拷贝结果应按 DLPack 标志标记，避免接收方误判数据仍在源设备。

## 设计分析

1. **device_id 是会话级键**：为每次分配/调度提供一个既稳定又可映射到驱动句柄的标识，是全部多设备逻辑的基础设施。
2. **分槽表天然并行友好**：per-device 上下文让多卡可并行调度，共享一份模块对象而不互相加锁竞争。
3. **拓扑决定搬运策略**：硬件能力（P2P 与否）直接决定"零拷贝与否"，软件层需把该信息显式化。

## NPU建议

1. 为每张 NPU 卡建立一个独立运行时上下文对象，以 `DLDevice.device_id` 为键存入 per-device 表，惰性创建、按槽释放。

2. 保证 `device("npu:N")` 中的 N 与驱动句柄严格一一对应，并在 `device.h` 解析函数中登记，随枚举稳定发布。

3. 维护设备拓扑矩阵（P2P/高速互联/总线带宽），供调度器按亲和性放置张量；对 P2P 可达的设备对允许 DLPack 零拷贝共享指针。

4. 实现 `npu.tensor_copy` 一类的跨设备迁移原语：同设备直接返回引用，跨设备分配目标张量并启 DMA，完成后按 DLPack 拷贝标志标记结果。

5. 提供多设备查询全局函数（`npu.get_device_count`/`npu.device_properties`），使宿主在启动时发现全部设备并制定调度策略。

6. 对跨设备错误统一归并到当前调用设备的错误上下文（配合视角195），使多卡调试时能精确定位到出错设备。

## 相关概念

- [189 NPU 设备 API 设计](189-npu-device-api-design.md)：设备枚举与字符串解析
- [190 NPU 张量交换](190-npu-tensor-exchange.md)：跨设备拷贝机制
- [187 VTA 类加速器设计](187-vta-style-accelerator-design.md)：per-device 实例表
- [075 张量设备管理](/05-tensor-dlpack/concepts/075-tensor-device-management.md)