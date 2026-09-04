# xmnn 重新打包 + Docker 镜像构建 + 模型编译与精度验证 Spec

## Why
`d:\spaces\SpecWeave\external\chaos\npuusertools\xmnn\caffe_pb2.py` 已更新到最新版本，需要将该更新纳入 xmnn wheel 打包，并基于新 wheel 构建 Docker 运行时镜像，进而在新镜像中对 models/debug、models/demo、models/tests 三个目录下的模型进行全面编译与精度测试，验证模型性能并对比基准值。

## What Changes
- 使用 `xmtools/docker/dev-llvm22/` 构建脚本在 WSL（Ubuntu-24.04）Docker 环境中重新打包 `xmnn` wheel（复用已构建的 `xmnn-dev:llvm22` 镜像，增量重建 xmnn Nuitka 模块以纳入更新的 `caffe_pb2.py`）
- 使用 `xmtools/docker/runtime/` 的 `build-runtime.sh` 基于新 wheel 构建运行时镜像（新镜像标签，避免覆盖旧镜像以保留基线）
- 基于新运行时镜像，对三个模型目录下**具备完整产物**（config.toml + 引用的模型文件 + dataset 数据）的模型执行编译；编译无错误为硬性要求
- 对已编译模型执行精度测试，记录 `result.csv`（余弦相似度/MSE/MAE）等指标，并与**基线镜像（`xmnn:1.2.1-alpha`）** 或既有基线数据对比
- 产出编译报告 + 精度对比报告

## Impact
- Affected specs: xmnn/npu 打包、Docker 部署、模型验证工作流
- Affected code:
  - `external/chaos/npuusertools/xmnn/caffe_pb2.py`（已更新）
  - `external/chaos/xmtools/docker/dev-llvm22/build-and-test.sh`、`run-build.sh`
  - `external/chaos/xmtools/docker/runtime/build-runtime.sh`
  - `external/chaos/xmtools/sdk/tools/compile.py`、`accuracy.py`
  - `external/chaos/xmtools/models/{debug,demo,tests}` 模型目录

## ADDED Requirements

### Requirement: 重新打包 xmnn wheel 并纳入更新后的 caffe_pb2
系统 SHALL 使用 `xmtools/docker/dev-llvm22/build-and-test.sh --no-build` 增量重建 xmnn wheel，确保 wheel 内 `xmnn` Nuitka `.so` 包含更新后的 `caffe_pb2` 定义。

#### Scenario: 成功生成 wheel
- **WHEN** WSL Docker 环境中执行 `build-and-test.sh --no-build`
- **THEN** `xmtools/dist/xmnn-*.whl` 生成，wheel 8 项验证全部通过，构建过程无错误退出

#### Scenario: 构建失败
- **WHEN** wheel 构建或验证失败
- **THEN** 收集错误，回退修复后重试，不进入下游任务

### Requirement: 基于新 wheel 构建运行时 Docker 镜像
系统 SHALL 使用 `xmtools/docker/runtime/build-runtime.sh` 基于新 wheel 构建运行时镜像，镜像包含所有必要依赖，且 `verify_xmnn.py` 全部通过。

#### Scenario: 成功构建镜像
- **WHEN** 执行 `build-runtime.sh -t xmnn:1.2.1-new`
- **THEN** 新镜像生成，镜像内 `verify_xmnn.py` 全部通过，Caffe 前端 `caffe_pb2` 可正常解析

### Requirement: 编译三目录下所有完整产物模型
系统 SHALL 对 `models/{debug,demo,tests}` 下具备完整产物（config.toml + 模型文件 + dataset）的模型执行 `compile.py -n <model>`，编译无错误。

#### Scenario: 编译成功
- **WHEN** 对每个完整产物模型执行编译
- **THEN** 生成 `network.xmnn` 与 `param.bin` 编译产物，无错误

### Requirement: 精度测试与基准对比
系统 SHALL 对编译成功的模型执行 `accuracy.py -n <model>`，记录 `result.csv`（余弦相似度/MSE/MAE），并与基线镜像或既有基线数据对比，产出精度对比表与报告。

#### Scenario: 精度测试完成
- **WHEN** 对每个编译成功模型执行精度测试
- **THEN** 生成结构化指标，并判断 `caffe_pb2.py` 更新是否引入精度回归

## MODIFIED Requirements
无（本任务为全新流程）。

## REMOVED Requirements
无。