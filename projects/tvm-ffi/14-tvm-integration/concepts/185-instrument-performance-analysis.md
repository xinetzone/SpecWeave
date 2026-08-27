---
type: Concept
title: "视角185：Instrument 性能分析（NPU 建议）"
description: "分析 TVM 的性能分析与插桩体系：PassInstrument 在 Pass 前后插桩、Timer/WrapTimeEvaluator 做设备计时、VMInstrument 对 VM 执行探针，展示 FFI 如何承载跨编译期/运行期的可观测性。"
tags:
  - instrument
  - performance
  - profiling
  - timer
  - pass-instrument
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-063, F-295, F-296
  - code:
    - include/tvm/runtime/timer.h
    - include/tvm/ir/instrument.h
    - src/ir/instrument.cc
    - include/tvm/runtime/vm/vm.h
---

# 视角185：Instrument 性能分析（NPU 建议）

## 概述

性能分析贯穿 TVM 的编译期与运行期：编译侧用 `PassInstrument` 对 IR 变换插桩，运行侧用 `Timer`/`WrapTimeEvaluator` 做设备级计时，VM 侧用 `SetInstrument` 对每次 packed 调用设探针。三者都以 FFI 对象/函数为载体，构成可组合、可对 Python 暴露的可观测性体系。

## 核心源码引用

`include/tvm/runtime/timer.h`（已验证）：

- `class TimerNode : public ffi::Object`（timer.h:41）：`Start()`/`Stop()`/`SyncAndGetElapsedNanos()`（:47-63）；
- `class Timer : public ffi::ObjectRef`（:77）：`static Timer Start(Device dev)`（:134）；
- `ffi::Function WrapTimeEvaluator(ffi::Function f, Device dev, int number, int repeat, ...)`（:186-189）：包装一次性计时为多次采样平均；
- 注释示例展示 CPU 计时器经 `TVM_FFI_STATIC_INIT_BLOCK(){ refl::GlobalDef().def("runtime.timer.cpu", ...) }`（timer.h:126-131）登记。

`include/tvm/ir/instrument.h`（已验证）：`PassInstrumentNode : public ffi::Object`（:102）定义 `EnterPassContext`/`ExitPassContext`/`ShouldRun`/`RunBeforePass`/`RunAfterPass`（:110-137）。

`src/ir/instrument.cc`（已验证）：`TVM_FFI_STATIC_INIT_BLOCK(){ refl::GlobalDef().def("instrument.RenderTimePassProfiles", ...).def("instrument.MakePassTimingInstrument", ...) }`（instrument.cc:317-321）把经典计时探针登记为全局函数。

`include/tvm/runtime/vm/vm.h`：`VirtualMachine::SetInstrument(ffi::Function)`（vm.h:173）与 `VMInstrumentReturnKind{kNoOp,kSkipRun}`（:51-56）支撑 VM 执行探针。

## 设计分析

### 编译期：PassInstrument

`PassInstrumentNode`（instrument.h:102）在 `PassContext` 生命周期内被有序触发——进入/退出上下文各一次，每个 Pass 前后各一次；多个 instrument 按声明顺序串联（instrument.h:72-97）。`ShouldRun` 返回 false 即可跳过某个 Pass，实现按需计时。

### 运行期：Timer + WrapTimeEvaluator

`TimerNode`（timer.h:41）抽象「开始→停止→同步取纳秒」，`Start`/`Stop` 尽力廉价、同步开销集中在 `SyncAndGetElapsedNanos`（:63），避免计时本身拖慢测量对象。`WrapTimeEvaluator`（:186）在其上叠加预热、多次采样、冷启动与温度控制，产出稳定均值。

### VM 探针与插入原语

`SetInstrument`（vm.h:173）在每个 `Call` 前后回调解剖 `(closure, func_symbol, before_run, args...)`；`VMInstrumentReturnKind::kSkipRun`（vm.h:54）允许在 before 阶段跳过执行，用于"只统计不发运行"类采样。回溯（facts F-295/296）为 profiling 补充调用栈上下文。

### 全局函数化可观测性

计时器、探针工厂都以 `refl::GlobalDef` 登记（instrument.cc:317-321；timer.h:126-131），使 Python 能以普通 `ffi::Function` 调用"instrument.*"与"runtime.timer.*"，跨语言共享同一套 profiling 基建。

## 扩展讨论

### 插桩的"三处观察点"：编译期、运行期、VM 执行穿梭一致

性能分析刻意在三个时段各设观察点：编译期用 `PassInstrument` 对每个 IR 变换前后打点，配置 `ShouldRun=false` 即可跳过某个 Pass；运行期用 `Timer`/`WrapTimeEvaluator` 做设备级计时；VM 侧用 `SetInstrument` 对每次 packed 调用设探针。三者都建立在 FFI 对象/函数之上，因此既能各自独立使用，也能被同一壳层聚合。这使得"编译慢在哪、运行慢在哪、单次调用慢在哪"让一套体系统一回答，而不是散落多个工具各自为政。

### Timer 的"低干扰"设计：测量动作不应拖慢被测对象

`TimerNode` 把「开始→停止→同步取纳秒」拆开，并强调 `Start`/`Stop` 尽力廉价、同步开销集中在 `SyncAndGetElapsedNanos`（:63）。这是刻意的低干扰取向——真实的耗时必须发生在被测量的区间内，计时本身的计数动作不能成为主要噪声。`WrapTimeEvaluator` 再叠加预热、多次采样、冷启动控制与均值输出，把"单次计时"升级为"可复现的统计测量"，避免冷启动与系统噪点污染采样结论。

### 全局函数化：Python 与 C++ 共用同一套 profiling

计时器工厂（`runtime.timer.cpu`）与探针工厂（`instrument.MakePassTimingInstrument`）都以 `refl::GlobalDef` 登记进全局函数表，意味着 **Python 侧无需重新实现计时**，直接以 `ffi::Function` 调用同一套 C++ 实现。这避免了"按语言各写一套 profiling"造成的功能不对齐与结果可比性问题，使编译期与运行期的可观测性在跨语言边界上保持同一语义——这也是 FFI 作为"基础设施复用与贯通"价值在 profiler 领域的具体体现。

## NPU 建议

1. 为 NPU 注册专用 `refl::GlobalDef().def("runtime.timer.npu", [](Device dev){ return Timer(...); })`，让 `Timer::Start(device)` 在 NPU 上启用设备时钟而非退化为 CPU 同步计时。
2. 用 `instrument.MakePassTimingInstrument` 精准统计"NPU 内核生成/编译"各 Pass 耗时，定位调度与代码生成瓶颈；按算子标签过滤 `ShouldRun`。
3. 在 `VirtualMachine::SetInstrument` 回调里对 `func_symbol` 命中 NPU 算子时采样其 `SyncAndGetElapsedNanos`，输出 NPU 内核级延迟与调用间隙，配合 `kSkipRun` 做无执行预热。
4. 把 NPU 探针统一登记进 `refl::GlobalDef`（如 "npu.profile.*"），与 `instrument.RenderTimePassProfiles` 的输出合并，形成编译+运行时一体化的 NPU 性能报告。

## 相关概念

- [174 Pass 基础设施](174-pass-infrastructure.md)：PassInstrument 的宿主
- [177 虚拟机 VM](177-virtual-machine-vm.md)：VM 探针的载体
- [180 目标代码生成注册](180-target-codegen-registration.md)：`runtime.timer.*` 的登记模式
- [184 Source Map](184-source-map.md)：性能归因的位置信息