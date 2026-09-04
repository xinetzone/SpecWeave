# Chaos AI XMNN Wheel 打包器 Spec

## Why
现有 `xmtools` 的 XMNN wheel 打包方案与 `chaos/ai` 的 devcontainer 是两套独立体系，且 xmtools 作为独立 git 仓库与其源码目录（npu_tvm/npuusertools）强耦合。用户希望在 `chaos/ai` 内创建子目录，**从零**构建一个新的、**自包含**的 wheel 打包 Dockerfile：直接复用已构建好的 `devcontainer-base:chaos-ai-npu` 镜像作为基础，将 NPU 源码编译打包为自包含 xmnn wheel，且**不依赖 xmtools 目录**、**不暴露源码**。

## What Changes
- 在 `external/chaos/ai/` 下新建子目录 `xmnn-whl-builder/`，作为自包含的 wheel 打包器
- 新增多阶段 `Dockerfile`：`FROM devcontainer-base:chaos-ai-npu`（build 阶段）+ 运行时最终层
- 自包含打包配置（复制 xmtools 打包经验，但**不引用 xmtools 路径**）：
  - `pyproject.toml`（scikit-build-core + Nuitka）
  - `CMakeLists.txt`（安装 `_libs/`、RPATH `$ORIGIN`、数据目录）
  - `_xmnn_bootstrap.py` + `xmnn_bootstrap.pth`（AST 兼容层 + TVM 环境引导）
- 构建脚本：`build-wheel.sh`（build 阶段 bind-mount 挂载 npu_tvm/npuusertools，产出自包含 wheel）
- 验证脚本：`verify-wheel.sh`（复用 8 项验证标准）
- 一键脚本：`build-and-test.sh`（构建镜像 → 挂载源码 → 打包 wheel → 验证）
- **BREAKING**：不依赖 `external/chaos/xmtools` 目录，也不依赖 `external/chaos/xmtools/docker/dev-llvm22` 的镜像

## Impact
- Affected specs: `chaos-ai-npu-devcontainer`（复用其基础镜像 `devcontainer-base:chaos-ai-npu`）
- Affected code: `external/chaos/ai/xmnn-whl-builder/`（新建目录）
- 不修改：`external/chaos/xmtools/`、`external/chaos/ai/Dockerfile`、`external/chaos/ai/build.sh`

## ADDED Requirements

### Requirement: 自包含打包器目录结构
系统 SHALL 在 `external/chaos/ai/xmnn-whl-builder/` 下提供完整自包含的文件集合，不引用 `external/chaos/xmtools` 的任何路径或文件。

#### Scenario: 目录完整性
- **WHEN** 检查 `xmnn-whl-builder/` 目录
- **THEN** 存在 `Dockerfile`、`pyproject.toml`、`CMakeLists.txt`、`_xmnn_bootstrap.py`、`xmnn_bootstrap.pth`、`build-wheel.sh`、`verify-wheel.sh`、`build-and-test.sh`

### Requirement: 多阶段构建与源码隔离
系统 SHALL 使用多阶段 Dockerfile：build 阶段 `FROM devcontainer-base:chaos-ai-npu` 通过 BuildKit `RUN --mount=type=bind` 挂载源码构建 wheel；最终层仅包含 wheel 与运行时依赖，**不含任何源码文件**。

#### Scenario: 最终镜像无源码
- **WHEN** 构建完成后检查最终镜像文件系统
- **THEN** 不存在 npu_tvm/npuusertools 的源码文件；Python 源码经 Nuitka 编译为 `.so` 二进制，无 `*.py` 可读源码

### Requirement: 自包含 wheel 产物
系统 SHALL 产出包含 `_libs/`（libtvm.so + libLLVM + 依赖库，RPATH `$ORIGIN`）、`tvm/relay/std/*.rly`、`vta_hw/config/*.py/*.json`、`xmnn/autolibs|tools_cpp|fonts` 数据目录、bootstrap 文件的 wheel。

#### Scenario: wheel 内容完整性
- **WHEN** 安装 wheel 后执行 8 项验证
- **THEN** 全部通过（import tvm/vta/xmnn、_libs 检查、tvm.build 计算、relay/std、.pth、数据目录）

### Requirement: 国内镜像与构建约束
系统 SHALL 继承 chaos-ai-npu 基础镜像的国内镜像配置（conda 北外 / pip 清华），构建时使用 `--no-isolation` 避免下载 Python 版 cmake/ninja，设置 `PIP_USER=0`。

#### Scenario: 构建约束
- **WHEN** 执行一键构建脚本
- **THEN** 使用 `python -m build --wheel --no-isolation`，环境变量 `PIP_USER=0`，`PATH=/opt/conda/bin:$PATH`

## MODIFIED Requirements
无（新建能力，不修改既有要求）。

## REMOVED Requirements
无。