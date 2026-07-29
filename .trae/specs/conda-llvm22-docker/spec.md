---
version: 1.0
---

# Conda + LLVM 22.1 开发环境 Docker 镜像 - Product Requirement Document

## Overview
- **Summary**: 创建一个包含 Conda 包管理系统和 LLVM 22.1 版本工具链的 Docker 开发环境镜像，用于 NPU TVM 编译、Nuitka 打包等开发工作。镜像需正确配置 Conda 环境，安装指定版本 LLVM，并设置必要的环境变量确保工具链在系统路径中可用。
- **Purpose**: 为 XMNN wheel 打包项目提供一个可复现、隔离的构建环境，避免本地环境依赖冲突，确保在任何机器上都能获得一致的 LLVM 工具链和 Conda 环境。
- **Target Users**: XMNN/NPU TVM 项目开发者，需要使用 LLVM 22.1 和 Nuitka 进行 Python 编译打包的开发人员。

## Goals
- 选择合适的基础镜像（优先使用 Ubuntu 或官方 Conda 镜像）
- 正确安装并配置 Conda（Miniconda 或 Mambaforge）
- 通过 Conda 渠道或官方源安装 LLVM 22.1 版本
- 设置必要的环境变量（PATH、LD_LIBRARY_PATH、LLVM_CONFIG 等）确保 LLVM 工具链可用
- 优化镜像大小（清理缓存、多阶段构建如适用）
- 包含基础构建工具（cmake、ninja、gcc/g++、python3 等）
- 在镜像中包含验证命令来确认 LLVM 版本正确性
- 提供构建脚本便于一键构建

## Non-Goals (Out of Scope)
- 不包含 GPU/CUDA 支持
- 不包含完整的 TVM 编译（本镜像仅作为基础开发环境）
- 不推送到 Docker Hub（仅本地构建使用）
- 不包含 Nuitka、scikit-build-core 等 Python 包的预安装（由用户按需安装）
- 不支持多架构构建（仅 Linux x86_64）

## Background & Context
- **项目需求**: XMNN wheel 打包项目需要使用 Nuitka 编译 Python 模块，Nuitka 依赖 LLVM 工具链
- **LLVM 版本**: 用户明确要求 LLVM 22.1，这是一个较新的版本，需要确认 Conda 渠道或官方源是否提供
- **Conda 环境**: Conda 可以方便管理 Python 环境和二进制依赖，避免系统包版本冲突
- **参考**: 参考了 TVM 项目的 Dockerfile.conda_cpu 中的 Conda 安装方式
- **WSL2 环境**: 镜像将在 WSL2 Ubuntu 环境中构建和使用

## Functional Requirements
- **FR-1**: Dockerfile 使用合适的基础镜像（推荐 Ubuntu 24.04 或 continuumio/miniconda3）
- **FR-2**: 正确安装 Miniconda 或 Mambaforge 到 `/opt/conda`
- **FR-3**: Conda 可执行文件路径添加到系统 PATH 环境变量
- **FR-4**: 安装 LLVM 22.1 版本，包含 llvm-config、clang、opt、llc 等核心工具
- **FR-5**: 设置 LLVM_CONFIG 环境变量指向正确的 llvm-config 路径
- **FR-6**: 安装基础构建工具：cmake、ninja、build-essential、python3、git、wget 等
- **FR-7**: 清理 apt 和 Conda 缓存以减小镜像体积
- **FR-8**: 设置工作目录为 `/workspace`
- **FR-9**: Dockerfile 中包含 `llvm-config --version` 或类似验证命令作为 HEALTHCHECK 或构建步骤验证
- **FR-10**: 提供构建脚本 `build-docker.sh` 便于一键构建镜像

## Non-Functional Requirements
- **NFR-1**: 镜像大小应控制在 2GB 以内（基础系统 + Conda + LLVM + 构建工具）
- **NFR-2**: Dockerfile 结构清晰，每个步骤有适当注释
- **NFR-3**: 构建过程有明确的进度输出，失败时给出清晰错误信息
- **NFR-4**: 镜像启动后 LLVM 工具链立即可用，无需额外配置

## Constraints
- **Technical**:
  - 仅支持 Linux x86_64 架构
  - LLVM 版本必须精确为 22.1
  - 使用 WSL2 (Ubuntu 26.04) + Docker 环境构建
  - 基础镜像为 Ubuntu 26.04
  - Conda 安装路径固定为 `/opt/conda`
- **Business**:
  - 交付物位于 `d:\spaces\SpecWeave\external\chaos\xmtools\docker\dev-llvm22\` 目录
- **Dependencies**:
  - WSL2 环境中已安装 Docker
  - 网络连接正常（可下载 apt 包、Conda 安装器、LLVM 包）

## Assumptions
- Conda 的 conda-forge 渠道提供 LLVM 22.1 版本，或者可通过 LLVM 官方 APT 源安装
- LLVM 22.1 存在对应的 conda 包或可通过官方预编译二进制安装
- WSL2 环境 Docker 运行正常
- 用户拥有足够的磁盘空间（至少 5GB 可用空间用于构建）

## Acceptance Criteria

### AC-1: Dockerfile 存在且语法正确
- **Given**: 在 `d:\spaces\SpecWeave\external\chaos\xmtools\docker\dev-llvm22\` 目录下
- **When**: 查看 Dockerfile 文件
- **Then**: Dockerfile 存在，语法正确可被 docker build 解析
- **Verification**: `programmatic`

### AC-2: Conda 正确安装且可用
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `conda --version`
- **Then**: 输出 Conda 版本信息，且 `which conda` 指向 `/opt/conda/bin/conda`
- **Verification**: `programmatic`

### AC-3: LLVM 版本为 22.1
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `llvm-config --version`
- **Then**: 输出显示 `22.1.x`（精确匹配 22.1 系列）
- **Verification**: `programmatic`

### AC-4: LLVM 核心工具可用
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `which clang && which opt && which llc && which llvm-dis`
- **Then**: 所有命令都返回正确路径，工具存在且可执行
- **Verification**: `programmatic`

### AC-5: LLVM_CONFIG 环境变量正确设置
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `echo $LLVM_CONFIG`
- **Then**: 输出指向 llvm-config 可执行文件的路径（如 `/opt/conda/bin/llvm-config` 或 `/usr/bin/llvm-config-22`）
- **Verification**: `programmatic`

### AC-6: 基础构建工具可用
- **Given**: Docker 镜像构建完成
- **When**: 在容器内执行 `cmake --version && ninja --version && gcc --version`
- **Then**: 所有命令都输出版本信息，工具正确安装
- **Verification**: `programmatic`

### AC-7: 工作目录和 PATH 设置正确
- **Given**: Docker 镜像构建完成
- **When**: 启动容器执行 `pwd && echo $PATH`
- **Then**: pwd 显示 `/workspace`，PATH 包含 Conda 的 bin 目录和 LLVM 的 bin 目录
- **Verification**: `programmatic`

### AC-8: 构建脚本可执行
- **Given**: 在 WSL2 环境中，进入 Dockerfile 目录
- **When**: 执行 `./build-docker.sh`
- **Then**: Docker 镜像成功构建，标签为 `xmnn-dev:llvm22`
- **Verification**: `programmatic`

### AC-9: 镜像大小合理
- **Given**: Docker 镜像构建完成
- **When**: 执行 `docker images xmnn-dev:llvm22`
- **Then**: 镜像大小不超过 2GB
- **Verification**: `programmatic`

### AC-10: 验证命令在构建过程中执行
- **Given**: Docker 构建过程
- **When**: Docker 执行到验证步骤
- **Then**: 构建日志中显示 LLVM 版本为 22.1
- **Verification**: `programmatic`

## Open Questions
- [ ] LLVM 22.1 是否在 conda-forge 上可用？如果不可用，应使用 LLVM 官方 APT 源还是从源码编译？
- [ ] 基础镜像选择 Ubuntu 24.04 还是官方 Miniconda 镜像？哪个更适合此场景？
- [ ] 是否需要在镜像中预安装特定版本的 Python（如 Python 3.14）？
- [ ] 是否需要包含 ccache 以加速后续编译？
