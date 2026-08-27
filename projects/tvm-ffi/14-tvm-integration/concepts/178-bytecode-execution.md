---
type: Concept
title: "视角178：字节码执行（NPU 建议）"
description: "分析 Relax VM 的字节码表示与执行器：Opcode/Instruction 标签联合体、VMExecutable 序列化、VMFuncInfo，以及 packed 函数表的索引驱动执行模型。"
tags:
  - bytecode
  - virtual-machine
  - opcode
  - executable
  - serialization
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-375
  - code:
    - include/tvm/runtime/vm/bytecode.h
    - include/tvm/runtime/vm/executable.h
    - src/runtime/vm/bytecode.cc
    - src/runtime/vm/executable.cc
---

# 视角178：字节码执行（NPU 建议）

## 概述

字节码是模型编译产物（`VMExecutable`）的中间表示：低阶指令序列仍以「索引 packed 函数」而非直接函数指针的方式运行，借此把真正算力（FX 算子、NPU 内核）留在 runtime 层按需绑定。本案剖析 `bytecode.h`/`executable.h` 的指令表示、函数表与序列化。

## 核心源码引用

`include/tvm/runtime/vm/bytecode.h`（已验证）：

```cpp
using ExecWord = int64_t;   // :40  主存储字
using RegName  = ExecWord;  // :43
using Index    = ExecWord;  // :48

enum class Opcode {         // :56-61
  Call = 1U, Ret = 2U, Goto = 3U, If = 4U,
};

struct Instruction {        // :72
  static constexpr ExecWord kKindBit = 8;                 // :74
  enum class ArgKind : int { kRegister, kImmediate, kConstIdx, kFuncIdx }; // :92
  Opcode op;
  union { struct{dst; func_idx; num_args; Arg* args;} /*Call*/;
          struct{result;} /*Ret*/; struct{pc_offset;} /*Goto*/;
          struct{cond; false_offset;} /*If*/; };
  static Instruction Call(Index, Index, Arg*, RegName);   // :220
  static Instruction Ret(RegName);                        // :226
  static Instruction Goto(RegName);                       // :232
  static Instruction If(RegName, Index);                  // :239
};
```

`include/tvm/runtime/vm/executable.h`（已验证）：`VMFuncInfo`（:53）含 `FuncKind{kPackedFunc,kVMFunc,kVMTIRFunc}`（:55-62）、`start_instr`、`end_instr`、`register_file_size`；`VMExecutable : public ffi::ModuleObj`（:89）含函数表 `func_table`、全局常量池 `constants`、指令字节 `instr_data` 与 `instr_offset`（:152-162），并提供 `Stats()`/`AsText()`/`SaveToBytes()`/`LoadFromBytes()` 等。

## 设计分析

### 标签联合的指令

`Instruction` 以 `Opcode` 为标签，`union` 承载各操作码字段，一个 `int64_t` 存储控制位 + 值（`kKindBit`/`kValueMask`，bytecode.h:74-80），紧凑且缓存友好。`Arg` 用高位存 kind、低位存 value 的位域编码（bytecode.h:177-180）压缩参数占用。

### 索引驱动的调用模型

`Call` 指令携带 `func_idx`（packed 函数表索引）而非函数指针。执行器据此到 `VMExecutable`（或运行时全局注册表）解析 `ffi::Function` 再调用。这一延迟绑定使字节码可无痛跨库序列化与迁移，且为 NPU 内核按 token 粒度替换留下挂载点。

### 函数表与序列化

`VMFuncInfo` 把函数名、指令区间、寄存器规模与 `FuncKind` 记入一张表；`VMExecutable` 的 `func_map`/`constants`/`instr_data` 一起构成可 `SaveToBytes`/`LoadFromBytes` 的完整可执行体，使编译产物能落盘并在异构设备间迁移执行（executable.h:127-149）。

### 指令区间执行

`start_instr`/`end_instr`（VMFuncInfo）界定每个函数的指令块，`instr_offset` 记录指令在 `instr_data` 中的字节偏移，执行器据此在寄存器文件上解释运行。

## 扩展讨论

### 单字存储与紧凑编码：字节码的"内存即带宽"取向

`ExecWord = int64_t` 让一条指令的每个主要字段都尽可能落进单个存储字；`Instruction` 用 `int64_t` 的 `kKindBit` 高位存标签、低位存值，`Arg` 更以高/低位分别编码 kind 与 value。这种"能塞进一个寄存器字就绝不扩到两条"的取向，是为了让指令解码逼近单次内存读取、保持缓存命中率——对需要逐条遍历 `instr_data` 的解释执行器而言，字节占用与取指成本几乎是线性挂钩的，紧凑布局直接转化为整体执行吞吐的优势。

### 索引调用而非指针调用：为序列化与后端替换留余地

`Call` 只携带 packed 函数表索引 `func_idx`，而不是函数指针，这是经过权衡的：指针无法跨进程/跨版本稳定，而索引作为一个逻辑位置可以在字节码落盘、迁移、加载到另一设备后重新解析到当地的 `ffi::Function`。更重要的是它把"调用谁"与"谁在那里"解耦——同一份字节码可被不同运行时以不同算子实现托底，NPU 内核只需在注册表里替身即可，前端字节码无需改动。

### VMFuncInfo + 指令区间：函数表就是字节码的"目录"

`VMFuncInfo` 的 `FuncKind`、`start_instr`/`end_instr`、`register_file_size` 三者合一，使执行器无需扫描字节码就能定位：某个函数从第几条指令开始、到第几条结束、需要多大寄存器文件。函数表因此承担"目录"职责——它把一串无差别的指令组织成可命名的函数单元，也让 `VMExecutable` 的 `SaveToBytes`/`LoadFromBytes` 得以把整张表与 `constants`/`instr_data` 一起序列化，使编译产物成为可携带、可版本迁移的完整执行体。

## NPU 建议

1. 把 NPU 算子包装为 packed 函数并登记入运行时函数表，让 VM 的 `Call(func_idx=...)` 零改造即可分派到 NPU 执行；懒加载 `kPackedFunc` 条目以延迟驱动初始化。
2. 用 `Instruction::ArgKind::kFuncIdx` 表达高频算子索引，在执行热路径上预解析为 NPU 内核句柄缓存，跳过每次调用的注册表查找。
3. 借用 `VMExecutable::SetInstructionData`/`AsPython`（executable.h:112-122）做 NPU 字节码可视化与逐指令单步调试，辅助算子对齐。
4. 对 NPU 特有指令，优先以 `VMFuncInfo::FuncKind` 扩展（如 `kVMTIRFunc`）承载，保持 VM 前端四个基础 Opcode 不变。

## 相关概念

- [177 虚拟机 VM](177-virtual-machine-vm.md)：字节码的执行载体
- [175 Module 系统集成](175-module-system-integration.md)：VMExecutable 的模块化
- [180 目标代码生成注册](180-target-codegen-registration.md)：packed 函数注册的来源