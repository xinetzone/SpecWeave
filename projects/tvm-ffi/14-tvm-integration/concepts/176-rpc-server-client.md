---
type: Concept
title: "视角176：RPC 服务端/客户端（NPU 建议）"
description: "分析 TVM RPC 子系统如何以 ffi::Function/PackedArgs 为传输约定，通过 RPCSession/RPCChannel/RPCEndpoint 实现跨进程远程调用、远端句柄管理与二进制序列化。"
tags:
  - rpc
  - ffi
  - packed-func
  - remote-session
  - device-api
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-135, F-137, F-141, F-142
  - code:
    - src/runtime/rpc/rpc_session.h
    - src/runtime/rpc/rpc_channel.h
    - src/runtime/rpc/rpc_endpoint.h
    - src/runtime/rpc/rpc_module.cc
---

# 视角176：RPC 服务端/客户端（NPU 建议）

## 概述

RPC 子系统让 TVM 可以在远程设备（如另一台机器或嵌入式 NPU）上执行算子编译与推理。其成败关键在于：把本地 `ffi::Function` 的调用语义完整搬到网络对端，同时透明管理远端资源句柄的生命周期。`src/runtime/rpc/` 下三层协作完成这一目标——`RPCChannel`（字节流传输）、`RPCEndpoint`（消息编解码与事件循环）、`RPCSession`（会话级抽象）。

## 核心源码引用

`src/runtime/rpc/rpc_session.h`（已验证）：

- `class RPCSession`（:59）：会话抽象，定义 `GetFunction(name)`（:100）、`CallFunc(PackedFuncHandle func, ffi::PackedArgs args, FEncodeReturn)`（:133）、`CopyToRemote`/`CopyFromRemote`（:142-149）、`FreeHandle(void*)`（:156）、`GetDeviceAPI(Device, bool)`（:173）；
- `RPCObjectRefObj : public ffi::Object`（:306）：把远端对象封装为 FFI 对象，析构时经 `sess_->FreeHandle` 释放远端引用（:319-328）；
- `CreateRPCSessionModule(std::shared_ptr<RPCSession> sess)`（:363）：生成一个 `ffi::Module` 指向该会话。

`src/runtime/rpc/rpc_channel.h`：`class RPCChannel`（:37）定义字节级数据通路；`rpc_endpoint.h`：`class RPCEndpoint`（:68）负责把 `ffi::PackedArgs` 编码进消息并驱动异步事件。

## 设计分析

### 调用即 ffi::PackedArgs

`CallFunc` 的入参就是 `ffi::PackedArgs`（rpc_session.h:133），返回值通过 `FEncodeReturn`（:82）编码。字符串/整型/浮点/字节按 `ffi::Function` 约定原样传输；函数与模块传 `void*` 句柄；张量传 `DLTensor*` 元数据加远端数据句柄。可见 RPC 复用 FFI 既有的类型擦除规格，没有为网络单独发明一套可调用格式。

### 远端句柄的引用语义

`RPCObjectRefObj`（:306）把「远端对象 + 所属会话」打包为一个 FFI 对象，析构时自动调用 `FreeHandle`（:319-327）。这使远端句柄生命周期与本地 `ffi::ObjectRef` 引用计数对齐——本地最后一个引用消亡即通知远端释放，规避资源泄漏。

### 同步与异步双通道

`RPCSession` 同时提供同步接口（`CallFunc`/`CopyToRemote`）与异步接口（`AsyncCallFunc`/`AsyncCopyToRemote`，:214-247）。异步路径用 `FAsyncCallback(status, ffi::PackedArgs)` 回传结果或异常，支撑事件驱动服务器在高并发远程推理下不阻塞线程。

### 重定向设备 API

`GetDeviceAPI` 返回代表「远端设备」的 `DeviceAPI`，分配远端内存后以 `RemoteSpace` 携带会话引用（rpc_session.h:288-301），数据指针即远端句柄。这让上层能以本地设备 API 的写法完成远程分配。

## 扩展讨论

### RPC 复用 FFI 类型擦除：网络不发明新协议

`CallFunc` 的入参直接是 `ffi::PackedArgs`、返回值经 `FEncodeReturn` 编码，正是把「本地 FFI 调用的类型擦除规格」延伸到网络对端。整型/浮点/字符串原样走线，函数与模块传 `void*` 句柄，张量传 `DLTensor*` 元数据加远端持有。其收益是**本地与远程调用共享同一套可调用语义**——上层无需区分对象在本地还是远端，绑定与编译器两侧也不用为 RPC 特造第二套参数格式。这是跨进程边界复用 FFI「最小通用契约」的典型示范。

### 远端句柄生命周期与本地引用计数对齐

`RPCObjectRefObj` 把「远端对象 + 所属会话」封装成 `ffi::Object`，析构时经 `sess_->FreeHandle` 释放远端引用。这一设计的关键是把**网络资源的回收时机**映射到本地对象引用计数：本地最后一次引用消亡即触发对远端的释放通知，无需用户手动 `Close`。若缺失这一层，远程张量/内核句柄会因无人负责释放而长期驻留对端内存，最终在远程推理长期运行时累积成泄漏。

### 同步/异步双通道：事件驱动不阻塞适配高并发

`RPCSession` 同时提供同步 `CallFunc` 与异步 `AsyncCallFunc`（经 `FAsyncCallback(status, PackedArgs)` 回传）。同步路径适合推理脚本的直白调用，异步路径则让单线程事件循环在等待远程结果时不阻塞——支撑 RPC 服务器在高并发远程推理下仍保持单线程非阻塞的经典模型。两条通道共用同一个 `PackedArgs` 编码，只是交付方式不同，从而不引入协议分歧。

## NPU 建议

1. NPU 远端推理应直接实现 `RPCSession` 接口，使 `CallFunc` 的 `ffi::PackedArgs` 直达 NPU 命令队列，同时复用 `ffi::Function` 约定，无需自造调用协议。
2. 为 NPU 张量定义专用 `RemoteSpace`（如携带 NPU 内存池与分页信息），并覆写 `GetDeviceAPI` 返回 NPU 的 `DeviceAPI`，让 `CopyToRemote` 走 NPU DMA/共享内存加速路径。
3. 复用 `RPCObjectRefObj`/`FreeHandle` 的引用语义管理 NPU 算子句柄与内核模块，确保远端 NPU 资源随本地引用消亡自动回收。
4. 暴露 `CreateRPCSessionModule` 产出的 `ffi::Module`，使 NPU 会话既能被 Python 直接调用，也能嵌入编译器流水线做交叉编译校验。

## 相关概念

- [175 Module 系统集成](175-module-system-integration.md)：RPC 会话以 `ffi::Module` 封装
- [171 TVM 运行时 FFI 应用](171-tvm-runtime-ffi-application.md)：FFI 类型擦除规格
- [185 Instrument 性能分析](185-instrument-performance-analysis.md)：远端调用耗时侧量