# 双镜像模型精度测试 Spec（xmnn-whl-builder / xmnn-runtime）

## Why

`external/chaos/ai/` 镜像矩阵中 `xmnn-whl-builder:latest` 与 `xmnn-runtime:latest` 均已构建可用（WSL Ubuntu-26.04）。`external/chaos/models/debug/caffe_demo`（Caffe 前端，`fgvsirfeature_ssd`）与 `external/chaos/models/debug/palmDet`（ONNX 前端，`palm_det_agatha`）是两套不同前端、不同输入规格的典型部署模型，但尚未在这两个镜像上系统性验证编译与量化精度。

本任务在 WSL 下，分别在 `xmnn-whl-builder:latest` 与 `xmnn-runtime:latest` 两个镜像中，对这两个模型执行**编译 + 精度测试**（`compile_xmnn` + `accuracy_xmnn`，产出余弦相似度/MSE/MAE），并交叉对比两镜像的精度结果，确认两个镜像对同一模型的量化精度一致、无回归，为镜像交付与后续板端部署提供精度基线。

## What Changes

- 在 WSL（Ubuntu-26.04）Docker 中，将 `external/chaos/models` 挂载进容器，分别用 `xmnn-whl-builder:latest` 与 `xmnn-runtime:latest` 对 `caffe_demo`、`palmDet` 执行编译与精度测试。
- 精度测试使用 `xmnn.accuracy_api.accuracy_xmnn`（浮点 relay-vm 推理 vs XMNN 量化推理，指标：余弦相似度/MSE/MAE），产出 `result.csv`。
- 汇总 2 模型 × 2 镜像的精度指标对比表与报告，判断两镜像精度一致性。
- **不修改** 模型 config.toml / prototxt / onnx / 镜像 / xmnn 源码；编译与精度产物落在各模型 `temp/` 目录，报告落在 `.trae/specs/<change-id>/`。
- 遵循七概念方法论编排（场景：问题解决/验证 → 链路 I→F→V→C，必要时对抗审查精度数据可信性）。

## Impact

- Affected specs: 复用/衔接 `xmnn-hub-sim-accuracy-validation`、`xmnn-repackage-docker-model-validation`、`caffe-demo-compile-fix`（已完成）的精度测试工作流。
- Affected code（只读引用，不修改）:
  - `external/chaos/ai/xmnn-whl-builder`（whl 打包镜像）
  - `external/chaos/ai/xmnn-runtime`（客户运行时镜像）
  - `external/chaos/models/debug/caffe_demo`（Caffe 前端模型 + temp 编译产物）
  - `external/chaos/models/debug/palmDet`（ONNX 前端模型）
  - `external/chaos/npuusertools/xmnn/{compile_api,infer_api,accuracy_api}.py`（编译/精度 API，只读）
- 产出物（新增）: 本 change-id 下 `spec.md`/`tasks.md`/`checklist.md` + 精度对比报告。

## 环境约束（关键前提）

| 镜像 | 特点 | 是否含构建工具链 |
|---|---|---|
| `xmnn-whl-builder:latest` | 含 Nuitka/scikit-build-core/编译器，tvm/vta/xmnn 已装 | ✅ 有 |
| `xmnn-runtime:latest` | 精简运行时，tvm/vta/xmnn 已装，无 LLVM/编译器 | ❌ 无（libLLVM 内置于 `_libs/`，`tvm.build(llvm)` 可运行） |

- 两镜像均已通过各自内置验证（verify-wheel.sh 11 项 / verify-runtime.sh 10 项）。
- 模型源码挂载：容器内 `/workspace/models` ↔ 宿主 `external/chaos/models`（双向挂载，精度产物可回写宿主）。
- 精度 API 需 `tvm.relay.frontend.caffe`（依赖 pytest，已入 wheel 核心依赖）——两镜像均应可导入。
- WSL 会话保活：`wsl -d Ubuntu-26.04` 每次独立调用后若无保活线程，dockerd/容器会被回收；需在同一会话内完成运行，必要时用后台进程保活。

## ADDED Requirements

### Requirement: 在 whl-builder 镜像编译并精度测试 caffe_demo 与 palmDet（FR-1）
系统 SHALL 在 `xmnn-whl-builder:latest` 镜像中对 `caffe_demo` 与 `palmDet` 分别执行 `compile_xmnn` 与 `accuracy_xmnn`，编译无错误并产出 `result.csv`。

#### Scenario: 编译与精度测试完成
- **WHEN** 在 whl-builder 镜像中分别对两模型执行编译 + 精度测试
- **THEN** 两模型均生成 `network.xmnn`/`param.bin` 编译产物，且 `temp/<model>/accuracy/result.csv` 含余弦相似度/MSE/MAE 指标

### Requirement: 在 runtime 镜像编译并精度测试 caffe_demo 与 palmDet（FR-2）
系统 SHALL 在 `xmnn-runtime:latest` 镜像中对 `caffe_demo` 与 `palmDet` 分别执行编译 + 精度测试，编译无错误并产出 `result.csv`。

#### Scenario: 编译与精度测试完成
- **WHEN** 在 runtime 镜像中分别对两模型执行编译 + 精度测试
- **THEN** 两模型均产出 `result.csv`，且 compile/infer/accuracy 阶段无致命错误（runtime 无 LLVM 工具链场景下 `tvm.build(llvm)` 可运行）

### Requirement: 双镜像精度交叉对比（FR-3）
系统 SHALL 汇总 2 模型 × 2 镜像的精度指标（各输出节点的余弦相似度/MSE/MAE），生成对比表，判断两镜像对同一模型量化精度的一致性。

#### Scenario: 对比表与结论
- **WHEN** 两镜像精度数据均收集完成
- **THEN** 产出 `xmnn-dual-image-accuracy-report.md`，包含逐模型/逐镜像的指标对比、一致性判定（是否在容差范围内）与差异说明

### Requirement: 环境与产物不被污染（FR-4）
系统 SHALL 保证任务不修改模型 config.toml、prototxt、onnx、镜像与 xmnn 源码；编译/精度产物仅落在模型 `temp/` 目录与 spec 目录内。

#### Scenario: 无污染
- **WHEN** 全部测试完成后检查
- **THEN** 模型 config.toml 未被改动，仅 `temp/` 下新增编译/精度产物，spec 目录新增报告

## MODIFIED Requirements
无（本任务为全新验证流程，与既有 spec 互补，不修改既有需求）。

## REMOVED Requirements
无。

## Open Questions
- [ ] palmDet config.toml 中 `adaround = { enable = true }`、`tune = true` 可能导致编译/精度耗时较长——执行时按需评估是否临时关闭加速（关闭前须备份 config，测试后恢复），或直接以原始配置执行并记录耗时。
- [ ] `caffe_demo` 前端为 caffe，`accuracy_xmnn` 的浮点参考模型经 `tvm.relay.frontend.caffe` 加载——确认两镜像该前端可正常解析 `fgvsirfeature_ssd.prototxt`。
