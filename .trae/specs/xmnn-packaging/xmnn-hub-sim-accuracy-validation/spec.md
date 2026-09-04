---
version: "1.0"
source: "seven-concepts-cmd | sc-20260806-xmnn-hub-sim-accuracy"
change-id: "xmnn-hub-sim-accuracy-validation"
---

# xmnn 重新打包 + Docker 镜像构建 + hub 模型仿真精度验证 Spec

## Why

`external/chaos/xmtools` 的 TVM/VTA/XMNN 源码持续演进（含 `caffe_pb2.py` 更新、`CAFFE_FFI` 相关算子修复），需要重新打包 `xmnn` wheel 与运行时 Docker 镜像，将最新源码纳入产物。同时，`models/hub/`（caffe 30 个、onnx 24 个）模型尚未在 **仿真 target（sim_vta2.0）** 下做过系统性精度验证，需要补齐 hub 模型在仿真环境下的编译与精度基线，为后续板端验证与回归提供依据。

## What Changes

- 使用 `xmtools/docker/dev-llvm22/` 构建脚本在 WSL（Ubuntu-24.04）Docker 中重新打包 `xmnn` wheel（复用 `xmnn-dev:llvm22` 镜像，增量重建 Nuitka 模块以纳入最新源码）
- 使用 `xmtools/docker/runtime/build-runtime.sh` 基于新 wheel 构建运行时镜像（新标签，不覆盖既有基线 `xmnn:1.2.1-new`）
- 将 `models/hub/caffe`（30）与 `models/hub/onnx`（24）全部模型**临时**改为仿真 target（`compile.target = "sim_vta2.0"`、`compile.tune = false`），逐一执行编译与精度测试
- 编译无错误为硬性要求；精度测试产出 `result.csv`（余弦相似度/MSE/MAE），汇总为结构化对比表与报告
- 测试完成后恢复 hub 模型 config.toml 原始 target，保持仓库/子模块不被污染

## Impact

- Affected specs: xmnn/npu 打包、Docker 部署、hub 模型验证工作流
- Affected code:
  - `external/chaos/xmtools/docker/dev-llvm22/build-and-test.sh`、`run-build.sh`
  - `external/chaos/xmtools/docker/runtime/build-runtime.sh`、`Dockerfile`
  - `external/chaos/xmtools/sdk/tools/compile.py`、`accuracy.py`
  - `external/chaos/xmtools/models/hub/{caffe,onnx}`（临时仿真 target 补丁，测试后恢复）
  - 产出物：`external/chaos/xmtools/build/` 下编译日志、精度报告

## ADDED Requirements

### Requirement: 重新打包 xmnn wheel
系统 SHALL 使用 `xmtools/docker/dev-llvm22/build-and-test.sh --no-build` 在 WSL Docker 中增量重建 xmnn wheel，确保 wheel 内 `xmnn` Nuitka `.so` 包含最新源码。

#### Scenario: 成功生成 wheel
- **WHEN** 在 WSL 中执行 `bash build-and-test.sh --no-build`
- **THEN** `xmtools/dist/xmnn-*.whl` 生成，wheel 8 项验证全部通过，构建无错误退出

#### Scenario: 构建失败
- **WHEN** wheel 构建或验证失败
- **THEN** 收集错误，回退修复后重试，不进入下游任务

### Requirement: 基于新 wheel 构建运行时 Docker 镜像
系统 SHALL 使用 `xmtools/docker/runtime/build-runtime.sh -t <new-tag>` 基于新 wheel 构建运行时镜像，镜像内 `verify_xmnn.py` 全部通过。

#### Scenario: 成功构建镜像
- **WHEN** 执行 `bash build-runtime.sh -t xmnn:1.2.1-hub-sim`
- **THEN** 新镜像生成，镜像内 `verify_xmnn.py` 全部通过

### Requirement: 枚举 hub/caffe 与 hub/onnx 完整产物模型
系统 SHALL 枚举 `models/hub/caffe` 与 `models/hub/onnx` 下具备完整产物（config.toml + 引用的模型文件 + dataset）的模型。

#### Scenario: 枚举完成
- **WHEN** 运行枚举脚本
- **THEN** 输出完整产物模型清单（caffe 与 onnx 各若干），并列出缺失产物的模型

### Requirement: 仿真 target 下编译所有完整产物 hub 模型
系统 SHALL 将 hub 模型 config.toml 临时改为仿真 target（`sim_vta2.0` + `tune=false`），对每个完整产物模型执行 `compile.py -n hub.<frontend>.<路径>`，编译无错误。

#### Scenario: 编译成功
- **WHEN** 对每个完整产物模型执行编译
- **THEN** 生成 `network.xmnn` 与 `param.bin` 编译产物，无错误

#### Scenario: 编译失败
- **WHEN** 某模型编译失败
- **THEN** 记录编译日志到 `build/compile_logs/`，汇总失败清单与原因

### Requirement: 仿真 target 下精度测试并汇总报告
系统 SHALL 对编译成功的模型执行 `accuracy.py -n hub.<frontend>.<路径>`，记录 `result.csv`（余弦相似度/MSE/MAE），汇总为精度对比表与报告。

#### Scenario: 精度测试完成
- **WHEN** 对每个编译成功模型执行精度测试
- **THEN** 生成结构化指标，汇总为 `build/xmnn-hub-sim-accuracy-report.md`

### Requirement: 恢复 hub 模型原始 target
系统 SHALL 在测试完成后将 hub 模型 config.toml 恢复为原始 `compile.target`，确保仓库/子模块不被污染。

#### Scenario: 恢复完成
- **WHEN** 精度测试全部结束
- **THEN** hub/caffe 与 hub/onnx 所有 config.toml 的 target/tune 恢复为原始值，`git status` 无无关改动

## MODIFIED Requirements
无（本任务为全新流程，与既有 `xmnn-repackage-docker-model-validation`（debug/demo/tests）范围互补）。

## REMOVED Requirements
无。