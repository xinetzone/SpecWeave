---
id: "export-summary-xmnn-wheel-20260726"
title: "XMNN Wheel 构建复盘导出摘要"
date: "2026-07-26"
source: "retrospective-xmnn-wheel-scikit-build-nuitka-20260726"
---

# 导出摘要

## 产出物清单

| 产出物 | 路径 | 说明 |
|--------|------|------|
| 复盘报告（主文档） | [README.md](README.md) | R→I→E 完整复盘报告（含13条事实、5条洞察、3个模式、6项决策、4个行动项） |
| 洞察萃取文档 | [insight-extraction.md](insight-extraction.md) | 洞察分析与模式萃取关系映射 |
| 本文件 | [export-summary.md](export-summary.md) | 导出摘要 |

## 模式更新

| 模式 | 更新类型 | 变更内容 |
|------|---------|---------|
| [python-native-extension-self-contained-wheel.md](../../../patterns/code-patterns/python-native-extension-self-contained-wheel.md) | 验证计数更新 | validation_count: 1→2, reuse_count: 0→1 |
| [python-ast-compatibility.md](../../../patterns/code-patterns/python-ast-compatibility.md) | 内容+计数更新 | 新增案例3（运行时Monkey-patch策略）、ExtSlice/Bytes兼容类、validation_count: 2→3, reuse_count: 1→2 |

## 原子行动项（推进状态更新）

| # | 优先级 | 行动项 | 验收标准 | 状态 | 备注 |
|---|--------|--------|---------|------|------|
| A1 | 高 | 固化构建环境Dockerfile | `docker build` 后 `docker run` 内执行 `inv build-all` 可产出wheel | ✅ 完成 | 添加了 Nuitka/invoke/build/scikit-build-core/auditwheel 依赖 |
| A2 | 中 | 添加manylinux合规性检查 | `auditwheel show` 输出仅依赖已打包的_libs库 | ✅ 完成 | 在 verify_wheel.py 中添加了 auditwheel_check() 函数 |
| A3 | 中 | 添加tvm.build(llvm)端到端计算验证 | verify_wheel.py包含计算图构建+执行测试 | ✅ 完成 | 已有 `tvm.build(llvm) compute test` 验证项 |
| A4 | 低 | 清理tasks.py中PREAMBLE重复代码 | AST patch代码只定义一次 | ✅ 完成 | 重构为 `_make_preamble()` 函数，消除重复 |

## 核心代码文件（xmtools项目）

| 文件 | 路径 |
|------|------|
| pyproject.toml | [pyproject.toml](../../../../../../external/chaos/xmtools/pyproject.toml) |
| CMakeLists.txt | [CMakeLists.txt](../../../../../../external/chaos/xmtools/CMakeLists.txt) |
| tasks.py | [tasks.py](../../../../../../external/chaos/xmtools/tasks.py) |
| _xmnn_bootstrap.py | [_xmnn_bootstrap.py](../../../../../../external/chaos/xmtools/_xmnn_bootstrap.py) |
| xmnn_bootstrap.pth | [xmnn_bootstrap.pth](../../../../../../external/chaos/xmtools/xmnn_bootstrap.pth) |
| verify_wheel.py | [verify_wheel.py](../../../../../../external/chaos/xmtools/scripts/verify_wheel.py) |
