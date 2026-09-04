---
version: "1.0"
source: "seven-concepts-cmd | sc-20260806-xmtools-repackage-sim-test"
change-id: "xmtools-repackage-sim-accuracy-20260806"
---

# xmtools 重新打包 xmnn whl + Docker 镜像 + hub/caffe+onnx 仿真精度全量测试 PRD

## Overview
- **Summary**: 在 WSL Docker 环境中重新打包 xmnn wheel（含最新源码，包括已入库的 `compile_api.py` caffe 模型加载修复），基于新 wheel 构建运行时 Docker 镜像，对 `models/hub/caffe`（~30个）与 `models/hub/onnx`（~24个）全部完整产物模型在仿真 target（`sim_vta2.0`）下执行编译与精度测试，产出结构化精度报告，并在测试结束后恢复模型 config.toml 原始状态，不污染仓库。
- **Purpose**: (1) 确保 wheel/镜像包含最新代码修复；(2) 建立 hub/caffe 与 hub/onnx 模型在仿真环境下的精度基线，为板端验证和回归测试提供参照；(3) 完成上次会话遗留的精度测试与 config 恢复任务。
- **Target Users**: XMNN 工具链开发者、模型部署工程师、QA 验证人员。

## Goals
- G1: 使用最新源码（含 `compile_api.py` caffe `getattr` 修复）在 WSL Docker 中增量重建 xmnn wheel，wheel 9 项验证全部通过
- G2: 基于新 wheel 构建运行时 Docker 镜像（标签 `xmnn:1.2.1-sim-accuracy`），镜像内 `verify_xmnn.py` 全部通过
- G3: 枚举 hub/caffe 与 hub/onnx 下完整产物模型（config.toml + 模型文件 + dataset），生成模型清单
- G4: 对所有完整产物模型在仿真 target（`sim_vta2.0`, `tune=false`）下执行编译，记录编译成功/失败清单及失败原因
- G5: 对编译成功的模型执行精度测试（`accuracy.py`），收集 `result.csv`（余弦相似度/MSE/MAE），汇总为精度报告
- G6: 测试完成后恢复所有 hub/caffe 与 hub/onnx config.toml 的原始 target/tune 配置，确保 `git status` 无无关改动
- G7: 产出完整的编译报告 + 精度对比报告（Markdown 格式），存放于 `external/chaos/xmtools/build/`

## Non-Goals (Out of Scope)
- 不涉及 PyTorch 模型（`hub/pytorch/`）的测试，本任务仅覆盖 caffe 和 onnx
- 不涉及 ops/ 和 arch/ 目录（算子参考库、结构拓扑参考库），仅测试真实业务模型
- 不进行板端（FPGA/SOC）推理，仅仿真 target
- 不修复编译失败的模型（仅记录失败原因，修复为后续任务）
- 不修改 xmnn 核心库代码（除已入库的 compile_api.py 修复外）
- 不发布 wheel 到 PyPI 或镜像到 Docker Registry

## Background & Context
- **项目位置**: `d:\spaces\SpecWeave\external\chaos\xmtools\`（独立 git 子模块）
- **依赖目录**: `../npu_tvm`（TVM 源码）、`../npuusertools`（XMNN Python 源码）
- **构建环境**: WSL2 (Ubuntu) + Docker，使用 `xmnn-dev:llvm22` 开发镜像（已配置 Conda + Python 3.14 + LLVM 22.1.8 + CMake 4.4 + Ninja 1.13 + Nuitka）
- **运行时镜像**: 基于 `ubuntu:26.04` + Miniconda + Python 3.14，预装 xmnn wheel 及其依赖
- **历史修复**: 上次会话中发现并修复了 `npuusertools/xmnn/compile_api.py` 第391行 caffe 模型加载 bug（原代码无条件访问 `model_file_path` 导致 caffe 模型加载失败），修复已入库（使用 `getattr` 兼容 `caffemodel_file_path`）
- **上次会话状态**: Tasks 1-4（wheel 构建、runtime 镜像构建、模型枚举、编译）已完成，PASS=49, FAIL=11；Tasks 5（精度测试）和 6（恢复 config）未完成。本次为全新端到端执行。
- **现有脚本**:
  - 构建: `docker/dev-llvm22/build-and-test.sh`（一键构建）、`run-build.sh`（容器内构建）
  - 运行时: `docker/runtime/build-runtime.sh`、`Dockerfile`、`verify_xmnn.py`
  - 模型枚举: `docker/runtime/enumerate_hub.py`
  - 仿真 target patch: `docker/runtime/patch_to_sim.py`（注意：当前仅覆盖 debug/demo/tests，需扩展支持 hub/caffe/onnx）
  - 备份恢复: `docker/runtime/backup_configs.sh`、`restore_configs.sh`
  - SDK 工具: `sdk/tools/compile.py`、`accuracy.py`

## Functional Requirements
- **FR-1**: 系统 SHALL 使用 `docker/dev-llvm22/build-and-test.sh --no-build` 在 WSL Docker 中增量重建 xmnn wheel（复用 `xmnn-dev:llvm22` 镜像）
- **FR-2**: 系统 SHALL 执行 wheel 9 项验证（import tvm/vta/xmnn、_libs 目录、libtvm.so 动态加载、tvm.build(llvm) 计算、relay/std 数据文件、xmnn_bootstrap.pth、xmnn 数据目录 autolibs/tools_cpp/fonts、bootstrap 加载、核心 API 导入）
- **FR-3**: 系统 SHALL 使用 `docker/runtime/build-runtime.sh -t xmnn:1.2.1-sim-accuracy` 基于新 wheel 构建运行时镜像
- **FR-4**: 系统 SHALL 运行镜像内 `verify_xmnn.py`，所有检查项通过
- **FR-5**: 系统 SHALL 枚举 `models/hub/caffe` 与 `models/hub/onnx` 下具备完整产物（config.toml + 模型文件 + dataset）的模型，输出模型名清单（`hub.caffe.<路径>` 和 `hub.onnx.<路径>`）
- **FR-6**: 系统 SHALL 备份所有 hub/caffe 与 hub/onnx config.toml 的原始内容到 `build/hub_config_backup/`
- **FR-7**: 系统 SHALL 将 hub/caffe 与 hub/onnx config.toml 批量 patch 为仿真 target：`compile.target = "sim_vta2.0"`、`compile.tune = false`（扩展现有 `patch_to_sim.py` 支持 hub 组或编写新脚本）
- **FR-8**: 系统 SHALL 在运行时容器中对每个完整产物模型执行 `python -m sdk.tools.compile -n hub.<frontend>.<路径>`，记录编译成功/失败状态
- **FR-9**: 编译失败时，系统 SHALL 记录错误日志到 `build/compile_logs/` 并汇总失败原因分类
- **FR-10**: 系统 SHALL 对每个编译成功的模型执行 `python -m sdk.tools.accuracy -n hub.<frontend>.<路径>`，收集输出的 `result.csv`
- **FR-11**: 系统 SHALL 从每个 `result.csv` 提取余弦相似度、MSE、MAE 指标，汇总为结构化精度对比表
- **FR-12**: 系统 SHALL 生成精度报告 `build/xmnn-hub-caffe-onnx-sim-accuracy-report.md`，包含：环境信息、模型总数/编译成功数/失败数、编译失败清单与原因、精度指标汇总表、结论
- **FR-13**: 系统 SHALL 在全部测试完成后，从备份恢复 hub/caffe 与 hub/onnx 全部 config.toml 的原始 target/tune 配置
- **FR-14**: 系统 SHALL 验证恢复后 `git status` 在 `external/chaos/xmtools/` 子模块中无 config.toml 相关改动（仅 build/ 产出物为新增）

## Non-Functional Requirements
- **NFR-1**: 构建脚本 SHALL 具备幂等性——重复执行不产生副作用（wheel 被覆盖为最新版本、镜像标签唯一）
- **NFR-2**: 编译和精度测试过程 SHALL 记录完整日志，包括 stdout/stderr、时间戳，便于失败排查
- **NFR-3**: 精度测试 SHALL 对每个模型使用 config.toml 中 `[accuracy]` 段指定的输入图片/数据
- **NFR-4**: 测试 SHALL 具备容错性——单个模型编译或精度测试失败不中断整体流程，继续下一个模型
- **NFR-5**: 备份与恢复机制 SHALL 确保原子性——patch 前全量备份，恢复时全量恢复，不遗漏任何 config.toml
- **NFR-6**: 整个流程（wheel 构建 + 镜像构建 + 编译 + 精度测试）SHALL 在 WSL2 Docker 环境中执行，不依赖 Windows 本地 Python 环境
- **NFR-7**: 精度报告 SHALL 为 Markdown 格式，包含可排序的表格，方便人工审阅

## Constraints
- **Technical**:
  - 必须使用 WSL2 + Docker 执行（Windows 本地无完整编译环境）
  - Python 版本必须 3.14+，LLVM/Clang 必须 22.1.8
  - 构建参数必须 `--no-isolation`，使用系统 cmake/ninja
  - 模型 config.toml 中部分模型已有 `target = "sim_vta2.0"`（如 palm、HAND），patch 脚本需兼容已正确配置的模型（不重复修改）
  - `npuusertools` 为独立 git 子模块，修改需在子模块内操作
- **Business**:
  - 不修改 hub 模型的原始配置（测试后必须恢复）
  - 不将 build/ 目录的临时产物提交到版本控制
- **Dependencies**:
  - `xmnn-dev:llvm22` 开发镜像必须存在（或可重新构建）
  - `/mnt/d/spaces/SpecWeave` 必须可挂载到 Docker 容器
  - `npu_tvm`、`npuusertools`、`xmtools` 三个兄弟目录必须完整存在于 `external/chaos/` 下

## Assumptions
- A1: `xmnn-dev:llvm22` 开发镜像已存在且可用（如不存在，`build-and-test.sh` 可自动构建但耗时较长）
- A2: `models/hub/` 子模块已初始化并拉取完整（模型文件存在）
- A3: 上次修复的 `compile_api.py` caffe `getattr` bug 已正确入库，新 wheel 将包含此修复
- A4: WSL2 Docker daemon 正在运行，当前用户有 docker 执行权限
- A5: 精度测试的输入数据（dataset.txt 引用的图片/数据）已存在于对应模型目录
- A6: 编译失败的 11 个模型中，部分可能因模型本身问题（OOM、不支持的算子、配置错误）而无法通过编译，本次任务仅记录不修复

## Acceptance Criteria

### AC-1: xmnn wheel 成功构建并通过验证
- **Given**: WSL2 Docker 环境可用，`xmnn-dev:llvm22` 镜像存在，源码挂载正常
- **When**: 执行 `bash docker/dev-llvm22/build-and-test.sh --no-build`
- **Then**: `dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` 生成，构建过程 exit 0，wheel 9 项验证全部通过，pyproject.toml 已恢复原始状态
- **Verification**: `programmatic`
- **Notes**: 验证项包括 import tvm/vta/xmnn、_libs 目录、libtvm.so CDLL 加载、tvm.build(llvm) 计算、relay/std 数据、.pth 引导、autolibs/tools_cpp/fonts 目录、核心 API 导入

### AC-2: 运行时 Docker 镜像构建成功
- **Given**: wheel 已构建成功且位于 `dist/` 目录
- **When**: 执行 `bash docker/runtime/build-runtime.sh -t xmnn:1.2.1-sim-accuracy`
- **Then**: 镜像 `xmnn:1.2.1-sim-accuracy` 构建成功，镜像内 `verify_xmnn.py` 全部检查通过（import、_libs、libtvm、tvm.build、核心 API、时区）
- **Verification**: `programmatic`

### AC-3: 完整产物模型枚举完成
- **Given**: 运行时镜像已就绪，hub 模型目录完整
- **When**: 在运行时容器中执行模型枚举脚本
- **Then**: 输出完整产物模型清单（caffe + onnx），每个模型格式为 `hub.<frontend>.<路径>`；同时列出不完整模型及缺失项
- **Verification**: `programmatic`

### AC-4: 模型 config.toml 备份并 patch 为仿真 target
- **Given**: 模型清单已生成
- **When**: 执行备份和 patch 操作
- **Then**: (1) 所有 hub/caffe 和 hub/onnx config.toml 备份到 `build/hub_config_backup/`；(2) patch 后所有模型的 `compile.target` 为 `"sim_vta2.0"`，`compile.tune` 为 `false`；(3) 原本已是 sim target 的模型不被错误修改
- **Verification**: `programmatic`

### AC-5: 所有完整产物模型编译执行完成
- **Given**: config.toml 已 patch 为仿真 target，运行时镜像就绪
- **When**: 对清单中每个模型执行编译
- **Then**: (1) 每个模型的编译结果（成功/失败）被记录；(2) 编译成功模型的 `network.xmnn` 和 `param.bin` 存在；(3) 编译失败模型的错误日志保存到 `build/compile_logs/`；(4) 编译过程不因单个模型失败而中断
- **Verification**: `programmatic`
- **Notes**: 预期部分模型可能因不支持的算子/OOM/配置错误而失败，需记录原因

### AC-6: 编译成功模型全部完成精度测试
- **Given**: 编译阶段完成，成功模型列表已知
- **When**: 对每个编译成功模型执行精度测试
- **Then**: (1) 每个模型执行 `accuracy.py` 不中断整体流程；(2) `result.csv` 被收集；(3) 余弦相似度、MSE、MAE 指标被提取汇总
- **Verification**: `programmatic`

### AC-7: 精度报告生成
- **Given**: 精度测试全部完成
- **When**: 汇总结果
- **Then**: 生成 `build/xmnn-hub-caffe-onnx-sim-accuracy-report.md`，包含环境信息、编译统计、失败清单、精度指标表、结论
- **Verification**: `human-judgment`
- **Notes**: 报告应清晰标注每个模型的 pass/fail 状态和数值指标，精度异常值应高亮

### AC-8: config.toml 恢复且仓库不被污染
- **Given**: 所有测试完成
- **When**: 从备份恢复 config.toml
- **Then**: (1) hub/caffe 和 hub/onnx 所有 config.toml 恢复为原始 target/tune；(2) 在 `external/chaos/xmtools/` 目录执行 `git status` 无 config.toml 修改（仅 build/ 目录新增文件）
- **Verification**: `programmatic`

## Open Questions
- [ ] 上次编译失败的 11 个模型具体是哪些？失败原因是否已有记录可供参考？是否需要在本次执行前尝试修复？
- [ ] 精度阈值是多少？余弦相似度达到多少算 PASS（如 >0.99）？是否有既有基线数据可供对比？
- [ ] 运行时容器挂载模型目录的方式：是将整个 external/chaos 挂载进容器，还是仅挂载 xmtools 目录？
- [ ] 精度测试的输入数据：使用 config.toml 中 `[accuracy] input` 指定的单张图片，还是使用 dataset.txt 中的全部数据？
