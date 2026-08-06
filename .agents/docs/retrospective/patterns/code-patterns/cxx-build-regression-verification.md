---
id: "cxx-build-regression-verification"
title: "C++扩展构建回归验证模式"
type: "code-pattern"
date: "2026-08-04"
maturity: "L1-draft"
source: "caffe-ffi CMake原子化重构里程碑复盘 (2026-08-04)"
related_patterns:
  - "preflight-checks-script"
  - "conda-package-clean-verification"
  - "build-failure-layered-triage"
  - "editable-install-stale-so"
  - "python-editable-import-isolation"
tags: ["c-extension", "regression", "build-verification", "symbol-check", "macro", "cmake", "scikit-build-core", "test-archive", "wsl"]
validation_count: 1
reuse_count: 0
documentation_level: "standard"
---

# C++扩展构建回归验证模式（Cxx-Build-Regression-Verification）

## 背景与动机

跨平台 C++ 项目（CMake + scikit-build-core）在构建/重构后跑回归测试，最容易踩三类"静默假成功"陷阱：

1. **错误环境**：测试跑在错误的 Python/编译器/容器环境（如 py313 而非项目要求的 py314），或依赖的 .so 未加载
2. **宏/符号脱节**：测试期望某编译宏（如 `CAFFE_FFI_ENABLE_COW_PHASE3`）启用特性，但编译产物未含该宏，测试静默通过"错误路径"
3. **结果不归档**：回归次数/结果无日志、无追溯，后续无法佐证"某里程碑闭环"

本次复盘的直接证据（F-007~F-017）：在 WSL docker 镜像（caffe-ffi-jupyter，conda env caffe-ffi，Python 3.14.6）跑 `pytest tests/python -q` 得 1646 passed / 1 skipped / 0 failures，耗时 10.52s，覆盖 43 个测试文件；用 `strings` 检查 `lazy_reshape=` 符号确认宏已编译；输出详细日志并归档为 markdown 里程碑总结。

> **反常识**：回归通过 ≠ 验证正确。若编译产物未含测试所依赖的宏/符号，或跑在错误环境，测试会"看似通过"地执行错误路径，回归无法发现脱节。回归前必须验证"产物含预期特性"。

---

## 触发场景

- 跨平台 C++ 项目（CMake + scikit-build-core）构建/重构后的回归验证
- 编译产物含"可配置特性"（宏开关/特性标志）的测试
- 需要追溯"某里程碑/重构闭环"、为后续开发提供验证依据的场景
- 多环境（容器/conda/本地）切换时的回归一致性

**不适用于**：
- 无编译产物的纯脚本项目（无符号/宏验证需求）
- 单次快速烟雾测试（不需要完整回归+归档）

---

## 核心步骤

1. **环境确认**：明确容器/conda/Python/编译器版本（如 WSL docker、conda env、Python 3.14.6、cmake 4.4.1、ninja 1.13.2、gcc 14.3.0），确保与项目要求一致
2. **宏与符号验证**：回归前用 `strings <so> | grep <期望符号>` 确认测试所依赖的宏/符号确实编译进产物（而非仅信任配置）
3. **全量回归**：`pytest <测试目录> -q`，记录总用例数/通过/跳过/失败/耗时/覆盖文件数
4. **日志归档**：用 `-v` 逐用例输出转成 markdown 详细日志，并生成里程碑总结文档，链接到 spec/tasks/roadmap
5. **关联文档**：更新 spec.md 里程碑行、p4-roadmap 前置验证链接、tasks.md Post-optimization notes

---

## 反模式（不要这么做）

- ❌ **在错误环境跑测试**：低版本 Python/错误容器会导致 `_ffi_api` 加载失败、fallback 返回空值，测试无意义地 FAIL（或假通过）
- ❌ **跳过宏/符号验证**：仅信任配置，编译产物缺宏时测试静默跑错误路径且回归无法发现
- ❌ **回归结果不归档**：无日志、无追溯，无法佐证里程碑闭环，后续无法复用
- ❌ **只报告"通过"不记录耗时/覆盖**：缺少可量化的回归证据
- ❌ **用 `import x._x` 子模块诊断替代符号检查**：显式导入可能触发 protobuf descriptor 重复注册崩溃

---

## 检验标准

- 全量回归通过（记录通过/跳过/失败/耗时/覆盖文件数）
- 回归前已用 `strings` 验证编译产物含测试依赖的宏/符号
- 详细日志已归档（`-v` 逐用例转 markdown）
- 里程碑总结文档已生成并链接到 spec/tasks/roadmap
- 环境版本在文档中明确记录，可复现

---

## 迁移验证

- **同类 CI/CD 场景**：任何"编译产物可配置特性"的回归（如编译器特性开关、条件编译、feature flag）需先验证产物含预期特性再执行测试
- **跨领域场景**：科学计算/深度学习框架的构建验证，回归前需确认运行时加载的是目标构建产物（而非缓存/旧版本），并保留可复现的完整日志与版本记录

---

## 与其他模式的关系

| 模式 | 关系 |
|------|------|
| [preflight-checks-script](preflight-checks-script.md) | 互补：预检在构建前验证环境/依赖，本模式在构建后验证产物符号+全量回归 |
| [editable-install-stale-so](editable-install-stale-so.md) | 配套：回归前须确认加载的是新 .so（非 stale），符号验证是两者共同手段 |
| [conda-package-clean-verification](conda-package-clean-verification.md) | 场景配套：干净环境验证 + 符号/依赖检查，避免 editable 残留污染 |
| [build-failure-layered-triage](build-failure-layered-triage.md) | 互补：本模式覆盖"构建成功后的回归验证"，后者覆盖"构建失败的分层排查" |
| [python-editable-import-isolation](python-editable-import-isolation.md) | 配套：隔离测试环境时需清理 editable finder/sys.path/sys.modules |

---

## 来源

- 复盘报告：[CMAKE_REFACTOR_RETROSPECTIVE_20260804.md](../../../../../projects/xuanspace/libs/caffe-ffi/docs/retrospectives/CMAKE_REFACTOR_RETROSPECTIVE_20260804.md)（洞察2、模式2）
- 相关事实：F-007~F-017
- 详细回归日志：[CMake_REFACTOR_WSL_REGRESSION_LOG_20260804.md](../../../../../projects/xuanspace/libs/caffe-ffi/docs/setup/CMake_REFACTOR_WSL_REGRESSION_LOG_20260804.md)