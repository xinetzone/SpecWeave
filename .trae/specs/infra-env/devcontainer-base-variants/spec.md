# devcontainer-base 镜像变体目录结构 - Product Requirement Document

## Overview
- **Summary**: 在 `apps/devcontainer-base/` 下新增 `variants/` 目录，用于放置基于基础 Dockerfile 的特殊功能镜像组（如 conda、conda+llvm 等），采用"基础镜像继承 + 变体配置化"模式，避免代码重复，支持多变体统一构建管理。
- **Purpose**: 解决 devcontainer-base 单一镜像无法满足多样化开发环境需求的问题，同时避免为每个变体复制整套 Dockerfile/脚本/配置导致的维护成本倍增。
- **Target Users**: 需要基于 devcontainer-base 构建定制化开发容器的开发者、CI/CD 系统。

## Goals
- 在 `devcontainer-base/variants/` 下建立标准化的变体目录结构
- 实现 2 个初始变体：`conda`（Miniconda3 基础环境）、`conda-llvm`（conda + LLVM/clang 编译工具链）
- 提供统一的变体构建脚本，支持单变体/多变体构建
- 共享脚本和配置模板，最小化重复代码
- 每个变体保持独立的 Dockerfile、配置和 .env.example
- 遵循现有 .agents/ 规范原子化结构

## Non-Goals (Out of Scope)
- 不修改 devcontainer-base 现有核心文件（Dockerfile/entrypoint.sh/config/等）
- 不实现变体镜像的自动 CI/CD 流水线（仅提供本地构建脚本）
- 不重构现有的 pytorch-base、caffe-ffi-jupyter 等独立 apps/ 项目
- 不提供离线构建资源下载（pytorch-base 的 offline/ 模式可作为后续参考）
- 不实现 Docker Compose 多变体编排

## Background & Context
- devcontainer-base 当前提供 Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter + Python venv 的基础环境
- 用户需要在基础镜像上叠加 conda、LLVM 等工具链，但这些工具不应放入基础镜像（会导致镜像膨胀、不适合所有用户）
- 现有派生项目（pytorch-base）采用独立 apps/ 目录模式，但变体与基础镜像关系紧密，适合放在同一项目下
- 参考 pytorch-base 的 Miniconda 安装模式和 caffe-ffi-jupyter 的 conda+LLVM 配置
- 项目已有成熟的多阶段构建、BuildKit缓存、国内镜像源切换、健康检查等模式可复用

## Functional Requirements
- **FR-1**: variants/ 目录结构标准化，包含共享脚本、模板和变体子目录
- **FR-2**: conda 变体：基于 devcontainer-base 安装 Miniconda3，配置清华镜像源，支持 conda 命令
- **FR-3**: conda-llvm 变体：基于 conda 变体叠加 LLVM 22.1.8 + clang 22.1.8 + cmake + ninja 编译工具链
- **FR-4**: 统一构建脚本 `variants/build.sh`，支持通过 `--variant` 参数指定构建单个或全部变体
- **FR-5**: 每个变体拥有独立的 Dockerfile、README.md、.env.example、docker-compose.yml（可选）
- **FR-6**: conda 环境激活机制：通过 /etc/profile.d/conda-init.sh 实现登录 shell 自动激活
- **FR-7**: conda 与系统 venv 共存：不覆盖 /opt/venv，用户可手动切换或通过环境变量选择
- **FR-8**: 每个变体遵循项目现有 Dockerfile 规范（BuildKit语法、7阶段构建、计时器、语法验证、国内镜像源支持）

## Non-Functional Requirements
- **NFR-1**: 构建性能：利用 Docker 层缓存，基础镜像层不重复构建
- **NFR-2**: 镜像体积：conda 变体 < 2GB，conda-llvm 变体 < 4GB（基于 devcontainer-base ~1.2GB）
- **NFR-3**: 可维护性：新增变体只需复制 `variants/_template/` 目录并修改配置，无需编写新的构建脚本
- **NFR-4**: 一致性：所有变体遵循相同的目录结构、构建流程、日志格式和验证标准
- **NFR-5**: 兼容性：变体镜像完全继承基础镜像的所有服务（SSH/Docker/Podman/Jupyter）和配置

## Constraints
- **Technical**: 
  - 必须使用 `FROM devcontainer-base:latest`（或指定版本标签）作为基础镜像
  - Dockerfile 必须遵循 `# syntax=docker/dockerfile:1.7-labs` 和现有 7 阶段构建模式
  - 必须支持 `APT_MIRROR` 和 `CONDA_MIRROR` 构建参数用于国内源切换
  - Miniconda 安装路径固定为 `/opt/conda`，环境目录 `/opt/conda/envs/`
  - LLVM 版本固定为 22.1.8（与项目 caffe-ffi 要求一致）
  - Python 版本默认 3.14，通过 `PYTHON_VERSION` ARG 可调
- **Business**: 无特殊业务约束
- **Dependencies**:
  - 依赖 devcontainer-base 镜像已构建并可在本地 Docker 中使用
  - 复用 devcontainer-base 的 scripts/lib/logging.sh 日志库
  - 复用 pytorch-base 的 Miniconda 安装和镜像源配置逻辑

## Assumptions
- devcontainer-base 镜像已通过 `bash scripts/build.sh` 构建完成，镜像标签为 `devcontainer-base:latest`
- 构建环境支持 Docker BuildKit（Docker 18.09+）
- 网络环境可访问 Docker Hub、Anaconda 仓库或国内镜像源
- 用户熟悉 Docker 构建和容器基本操作
- conda 环境默认不自动激活（避免干扰系统 venv），但提供 `/etc/profile.d/conda-init.sh` 供手动激活或配置自动激活

## Acceptance Criteria

### AC-1: variants/ 目录结构创建
- **Given**: devcontainer-base 项目根目录
- **When**: 创建 variants/ 目录结构
- **Then**: 目录结构包含 README.md、build.sh、_template/ 模板目录，以及 conda/ 和 conda-llvm/ 两个初始变体目录
- **Verification**: `programmatic` (目录结构检查)
- **Notes**: 目录结构遵循：variants/{shared,_template,conda,conda-llvm}/

### AC-2: conda 变体 Dockerfile 可构建
- **Given**: devcontainer-base:latest 镜像存在
- **When**: 执行 `bash variants/build.sh --variant conda`
- **Then**: 成功构建 `devcontainer-base:conda` 镜像，镜像内 `/opt/conda/bin/conda` 可执行，Python 版本正确
- **Verification**: `programmatic` (docker build + docker run 验证)
- **Notes**: 支持国内镜像源 `--build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna`

### AC-3: conda-llvm 变体 Dockerfile 可构建
- **Given**: devcontainer-base:conda 镜像存在（或自动先构建 conda）
- **When**: 执行 `bash variants/build.sh --variant conda-llvm`
- **Then**: 成功构建 `devcontainer-base:conda-llvm` 镜像，llvm-config、clang、cmake、ninja 可执行且版本正确
- **Verification**: `programmatic` (docker build + docker run 验证)
- **Notes**: LLVM 22.1.8、clang 22.1.8、cmake、ninja 在 conda 环境中可用

### AC-4: 变体继承基础镜像全部服务
- **Given**: conda 或 conda-llvm 镜像已构建
- **When**: 启动容器并检查服务
- **Then**: SSH(22)、Docker DinD、Jupyter(8888) 服务正常运行，与基础镜像行为一致
- **Verification**: `programmatic` (容器启动 + healthcheck + 端口检查)

### AC-5: 统一构建脚本支持全部变体构建
- **Given**: variants/ 目录结构完整
- **When**: 执行 `bash variants/build.sh --all`
- **Then**: 按依赖顺序（先 conda，再 conda-llvm）构建所有变体，输出构建日志和计时器汇总
- **Verification**: `programmatic` (脚本执行 + 镜像存在检查)

### AC-6: 变体 .agents/ 规范目录存在
- **Given**: 每个变体目录
- **When**: 检查目录结构
- **Then**: 每个变体包含 `.agents/rules/` 目录，至少有 dockerfile.md 规则文件说明该变体特有的构建规范
- **Verification**: `human-judgment` (文件存在性和内容审查)

### AC-7: conda 与系统 venv 共存无冲突
- **Given**: conda 变体容器
- **When**: 分别检查 /opt/venv 和 /opt/conda
- **Then**: /opt/venv（Jupyter 等基础工具）和 /opt/conda 都存在且互不干扰，`python` 命令默认使用 venv，`conda activate` 可切换到 conda 环境
- **Verification**: `programmatic` (路径检查 + Python 版本验证)

### AC-8: variants/README.md 提供清晰使用文档
- **Given**: variants/ 目录
- **When**: 查看 README.md
- **Then**: 包含变体列表、快速开始命令、构建参数说明、如何新增变体指南
- **Verification**: `human-judgment` (文档内容审查)

## Open Questions
- [ ] conda 环境是否需要默认自动激活？（目前假设不自动激活，通过 profile.d 脚本提供手动激活）
- [ ] 是否需要为每个变体提供 docker-compose.yml？（目前假设可选，初始版本可能不提供）
- [ ] 基础镜像标签是固定用 latest 还是支持通过参数指定版本？（目前假设用 latest，后续可扩展）
