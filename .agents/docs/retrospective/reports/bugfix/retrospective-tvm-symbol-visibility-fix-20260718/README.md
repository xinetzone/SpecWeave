---
title: TVM符号可见性控制修复--解决与PyTorch的LLVM符号冲突导致段错误
date: 2026-07-18
type: bug-fix
status: completed
tags: [TVM, LLVM, symbol-visibility, PyTorch, Segmentation-fault, CMake, linking, adaround]
source: d:\spaces\SpecWeave\external\xmhub\npu_tvm
chain: R->I->E->Export
depth: standard
---

# TVM符号可见性控制修复复盘

## 概览

| 属性 | 值 |
|------|-----|
| 任务类型 | Bug修复（C/C++链接器符号冲突） |
| 问题现象 | palmDet 模型编译时 adaround 启用后触发 Segmentation fault (core dumped) |
| 根本原因 | HIDE_PRIVATE_SYMBOLS=OFF 导致 TVM静态链接LLVM且符号全部导出，与PyTorch的libtorch.so中LLVM符号冲突，符号介入(Symbol Interposition)导致运行时绑定错误 |
| 修复方案 | 启用 HIDE_PRIVATE_SYMBOLS=ON，使用 -Wl,--exclude-libs,ALL 仅隐藏静态库符号，保留TVM自身符号可见 |
| 修复文件 | CMakeLists.txt、cmake/config.cmake、tasks.py、dev-env/rebuild_tvm_codegenc.sh、docker/local/nuitka/*、ci/jenkins/data.py、docs/install/from_source.rst |
| 验证结果 | TVM+PyTorch共存测试通过，无段错误 |
| 萃取模式 | 1个（精确符号可见性控制模式） |

## 快速导航

- [执行复盘](execution-retrospective.md) - 时间线、事实清单、变更摘要
- [洞察萃取](insight-extraction.md) - 根因分析、核心洞察
- [导出建议](export-suggestions.md) - 可复用模式、行动项

<!-- changelog -->
- 2026-07-18 | fix | 修复TVM符号可见性控制问题，解决与PyTorch的LLVM符号冲突导致的段错误

