---
id: "editable-install-stale-so"
title: "Editable安装stale .so处理模式"
type: "code-pattern"
date: "2026-08-04"
maturity: "L1-draft"
source: "caffe-ffi CMake原子化重构里程碑复盘 (2026-08-04)"
related_patterns:
  - "python-editable-import-isolation"
  - "conda-package-clean-verification"
  - "compiled-wheel-runtime-image-build"
  - "preflight-checks-script"
tags: ["editable-install", "pep-660", "c-extension", ".so", "stale-artifact", "scikit-build-core", "recompile", "build-artifact"]
validation_count: 1
reuse_count: 0
documentation_level: "standard"
---

# Editable安装stale .so处理模式（Editable-Install-Stale-So）

## 背景与动机

C++/Cython 原生扩展项目使用 `pip install -e .`（PEP 660 editable install）进行开发时，开发者普遍假设"editable 安装会即时反映源码变更"。这个假设对 **Python 层成立**，但对**编译产物层（.so/.pyd）不成立**：

- editable install 只把 Python 源码目录接入 `sys.path`（或通过 editable finder 重定向），源码改动即时生效
- 但 `_caffe_ffi.so` 这类已编译扩展**不会在重编译后自动更新到 editable 指向的源码树路径**
- 结果是：重新构建（`pip install -e .` / scikit-build-core）后，测试仍加载源码树里**旧的 .so**，静默跑在"错误路径"上

本次复盘的直接证据（F-011/F-012）：editable 路径下 `python/caffe_ffi/_caffe_ffi.so` 为 stale（缺 `CAFFE_FFI_ENABLE_COW_PHASE3` 宏符号），将 `build/python/caffe_ffi/_caffe_ffi.so` 复制到源码树路径后，3 个 lazy allocation 测试才通过。回归结果 1646 passed 均依赖此修复。

> **反常识**：editable install 的"即时生效"承诺只覆盖 Python 层，编译产物是例外。多数开发者因信任该承诺而跳过".so 是否更新"的验证，导致测试静默跑错路径、且难以定位（测试"通过"了但执行的是旧代码）。

---

## 触发场景

- C++/Cython 原生扩展 + editable install 开发迭代
- 重新编译后预期行为变化（新增符号/宏/功能），但测试行为未跟随变化
- scikit-build-core / setuptools / pybind11 等把编译产物输出到 `build/` 的构建后端
- 编译产物路径与源码树 editable 路径不一致时

**不适用于**：
- 纯 Python 包（无编译产物，editable 即时生效）
- 正式 wheel 安装（`.so` 打进 wheel，随安装落位，无 stale 问题）
- 每次全量重新安装（非 editable）的场景

---

## 核心步骤

1. **触发构建**：执行 `pip install -e .`（或 scikit-build-core 构建），确认编译成功
2. **对比产物**：比较 `build/` 下新编译的 `.so` 与源码树 editable 路径（如 `python/caffe_ffi/_caffe_ffi.so`）的时间戳与符号
   - **符号检查**：用 `strings <so> | grep <期望符号>` 验证新宏/新符号确实编译进产物（F-010 用 `strings` 确认 `lazy_reshape=` 存在）
3. **若不一致**：将新编译的 `.so` 复制到源码树 editable 路径（覆盖 stale 版本）
   - 或使用 `pip install -e . --force-reinstall` 强制重新生成
4. **重跑测试验证**：确认依赖新特性/新符号的测试通过

---

## 反模式（不要这么做）

- ❌ **假设 editable install 自动更新编译产物**：它只更新 Python 层，.so 是例外
- ❌ **只重新构建不复制 .so**：构建产物在 `build/`，但测试加载的是源码树路径，两者不同步
- ❌ **用 `import x._x` 子模块诊断替代符号检查**：显式导入子模块可能触发 protobuf descriptor 重复注册崩溃（`File already exists in database`），且无法证明加载的是新 .so
- ❌ **只比对时间戳忽略符号**：某些构建会保留旧时间戳或二次构建不变，符号比对更可靠
- ❌ **在测试"通过"后不做确认**：测试通过不代表跑的是新代码，需证明加载的 .so 与 `build/` 一致

---

## 检验标准

- 测试加载的 `.so` 与 `build/` 最新编译产物一致（符号/时间戳匹配）
- `strings <so>` 能 grep 到测试所依赖的新宏/新符号
- 依赖新特性/新宏的测试全部通过
- 未使用 `import x._x` 显式子模块导入触发 descriptor 崩溃

---

## 迁移验证

- **同类 MLOps 场景**：共享库/模型文件在 editable 或 Jupyter 热加载环境下被缓存，需显式刷新而非信任自动重载
- **跨领域场景**：任何"源码与编译/生成产物分离"的开发模式（如 WASM 编译、TypeScript 编译产物、proto 生成代码），都存在"重建产物未刷新到消费路径"的同类风险，需显式比对+刷新

---

## 与其他模式的关系

| 模式 | 关系 |
|------|------|
| [python-editable-import-isolation](python-editable-import-isolation.md) | 互补：本模式解决"editable 加载 stale .so"，后者解决"测试隔离 editable finder/sys.path 干扰" |
| [conda-package-clean-verification](conda-package-clean-verification.md) | 场景配套：conda 环境验证前清理 editable 残留四件套，避免污染验证结果 |
| [compiled-wheel-runtime-image-build](compiled-wheel-runtime-image-build.md) | 互补：wheel 场景强调 .so 落位与 RPATH，本模式强调 editable 开发场景的 .so 刷新 |
| [preflight-checks-script](preflight-checks-script.md) | 可延伸：将 .so 符号验证纳入构建预检脚本 |

---

## 来源

- 复盘报告：[CMAKE_REFACTOR_RETROSPECTIVE_20260804.md](../../../../../projects/xuanspace/libs/caffe-ffi/docs/retrospectives/CMAKE_REFACTOR_RETROSPECTIVE_20260804.md)（洞察1、模式1）
- 相关事实：F-010/F-011/F-012