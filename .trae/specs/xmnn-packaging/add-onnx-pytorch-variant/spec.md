# 新增 onnx-pytorch 镜像变体 Spec

## Why
当前 devcontainer-base 变体体系仅提供 conda / conda-llvm 两个基础工具链变体，缺少面向深度学习推理与模型转换的运行时变体。用户需要基于 conda-llvm（已含 LLVM/Clang/CMake/Ninja 工具链）创建新的 `onnx-pytorch` 变体，预装 ONNX 生态（onnx / onnxruntime）与 PyTorch CPU（torch / torchvision），实现开箱即用的 Python 深度学习开发与 ONNX 模型转换/推理环境。

## What Changes
- 基于 `variants/conda-llvm` 创建新变体 `variants/onnx-pytorch/`，完整替换模板/来源中的占位符。
- 变体在 conda base 环境安装 CPU 版 PyTorch（torch + torchvision）与 ONNX 生态（onnx, onnxruntime, onnx-simplifier, onnxoptimizer）。
- 遵循既有 4 追加阶段分层结构（config+init → install → symlink/init-script+verify → build-info+cleanup+final verify），并保留 `[TIMER]` 计时、`[VALIDATION CHECKPOINT]` 验证、build-info 写入、`--mount=type=cache` 缓存等既有约定。
- 在 `variants/build.sh` 的 `VARIANTS` 数组中注册 `onnx-pytorch`（依赖 `conda-llvm`）。
- 新增 `variants/scripts/test-onnx-pytorch.sh`（L1-L6 六层测试）与可选 `variants/scripts/build-onnx-pytorch.sh`。
- 在 `variants/README.md` 变体表格中注册新变体。
- 创建 `variants/onnx-pytorch/.agents/rules/dockerfile.md` 变体规范文件。

## Impact
- Affected specs: `devcontainer-base-variants`（变体目录体系）、`conda-llvm22-docker`
- Affected code:
  - `apps/devcontainer-base/variants/build.sh`（注册新变体）
  - `apps/devcontainer-base/variants/onnx-pytorch/`（新增目录，含 Dockerfile/.env.example/README.md/.agents/rules/dockerfile.md）
  - `apps/devcontainer-base/variants/README.md`（变体表格）
  - `apps/devcontainer-base/variants/scripts/test-onnx-pytorch.sh`（新增）
  - `apps/devcontainer-base/variants/scripts/build-onnx-pytorch.sh`（新增，可选）

## ADDED Requirements

### Requirement: onnx-pytorch 变体目录
系统 SHALL 提供 `variants/onnx-pytorch/` 目录，包含 `Dockerfile`、`.env.example`、`README.md`、`.agents/rules/dockerfile.md`。

#### Scenario: 目录结构完整
- **WHEN** 查看 `variants/onnx-pytorch/` 目录
- **THEN** 存在 Dockerfile、.env.example、README.md、.agents/rules/dockerfile.md 四个文件

### Requirement: Dockerfile 基于 conda-llvm
系统 SHALL 使新变体 Dockerfile 以 `FROM devcontainer-base:conda-llvm-${BASE_TAG}` 为起点，并遵循 `# syntax=docker/dockerfile:1.7-labs`、FROM 后重新声明 ARG、SHELL 指令、不覆盖 ENTRYPOINT/CMD/WORKDIR/USER 等变体约定。

#### Scenario: FROM 与 ARG 正确
- **WHEN** 检查 Dockerfile
- **THEN** 首行含 syntax 声明，FROM 使用 `devcontainer-base:conda-llvm-${BASE_TAG}`，FROM 后重新声明 `ARG BASE_TAG` 等，且未覆盖基础服务入口

### Requirement: PyTorch CPU 安装
系统 SHALL 在 conda base 环境安装 CPU 版 PyTorch（torch + torchvision），通过 pip 使用 CPU 专用索引或 conda-forge 的 pytorch-cpu 包，并记录实际版本到 build-info。

#### Scenario: 安装 CPU 版 PyTorch
- **WHEN** 构建 onnx-pytorch 变体
- **THEN** `python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"` 可用，且 `torch.cuda.is_available()` 为 False（CPU 版）

### Requirement: ONNX 生态安装
系统 SHALL 在 conda base 环境安装 ONNX 生态核心包：onnx、onnxruntime（CPU）、onnx-simplifier、onnxoptimizer。

#### Scenario: ONNX 包可用
- **WHEN** 构建完成后
- **THEN** `python -c "import onnx, onnxruntime; print(onnx.__version__, onnxruntime.__version__)"` 可用

### Requirement: build.sh 注册与验证
系统 SHALL 在 `variants/build.sh` 的 `VARIANTS` 数组中注册 `onnx-pytorch` 变体，依赖 `conda-llvm`，并定义验证命令。

#### Scenario: 注册成功且可构建
- **WHEN** 执行 `bash variants/build.sh --list`
- **THEN** 输出包含 `onnx-pytorch` 变体
- **WHEN** 执行 `bash variants/build.sh --variant onnx-pytorch --cn`
- **THEN** 构建成功，验证命令通过（torch/onnx/onnxruntime 导入成功）

### Requirement: 六层测试脚本
系统 SHALL 提供 `variants/scripts/test-onnx-pytorch.sh`，覆盖 L1-L6 六层测试（工具链版本、Hello World、深度组件、基础服务继承、PATH 优先级、配置文件）。

#### Scenario: 全部测试 PASS
- **WHEN** 执行 `bash variants/scripts/test-onnx-pytorch.sh`
- **THEN** 所有测试用例 PASS

## MODIFIED Requirements

### Requirement: variants/README.md 变体表格
更新 `variants/README.md` 的可用变体表格，新增 `onnx-pytorch` 条目（描述/基础镜像/包含组件）。

## REMOVED Requirements

无。
