# PyTorch Docker 基础镜像（Conda 版）- Product Requirement Document

## Overview
- **Summary**: 在 `d:\spaces\SpecWeave\apps\pytorch-base\` 目录构建一个基于 **Python 3.14 + Miniconda3** 的 PyTorch 深度学习框架 Docker 基础镜像，专门应对网络不稳定环境。采用国内 conda/pip 镜像源配置、分层缓存策略、重试机制，支持离线安装包和版本灵活配置，可直接被其他应用 Dockerfile 通过 `FROM` 指令引用。
- **Purpose**: 解决网络不稳定环境下 PyTorch + Conda 环境反复构建失败的痛点，提供一个预配置好国内源、基于 Miniconda + Python 3.14、经过验证的标准基础镜像，作为后续深度学习应用镜像的可靠依赖底座。
- **Target Users**: SpecWeave 项目开发者、需要在国内网络环境构建基于 Conda 的深度学习应用 Docker 镜像的用户、需要稳定可复用 PyTorch + Conda 基础镜像的团队。

## Goals
- 提供网络不稳定环境下高成功率的 PyTorch + Miniconda3 基础镜像构建方案
- 镜像基于 Miniconda3 + Python 3.14（用户要求的 Python 3.14 + Anaconda 环境，使用 Miniconda 更轻量）
- 镜像可直接被其他 Dockerfile 通过 `FROM pytorch-base:latest` 引用
- 支持通过 `--build-arg` 灵活指定 PyTorch 版本、Python 版本（默认 3.14）、CPU/GPU 变体
- 内置 conda 国内镜像源（清华 TUNA）和 pip 阿里云镜像源配置
- 支持离线安装：本地 Miniconda 安装包、本地 conda 包缓存、本地 wheel 包
- 包含完整的安装后验证步骤，构建失败能尽早暴露
- 遵循 docker-ssh-dind 项目的最佳实践（中文环境、非 root 用户 ai、tini init、详细构建日志）
- 镜像体积优化：conda clean、pip --no-cache-dir、--no-install-recommends

## Non-Goals (Out of Scope)
- 不安装完整 Anaconda 发行版（Miniconda 足够，体积小一个数量级，需要的包可后续安装）
- 不包含 GPU 驱动（GPU 镜像仅预装 CUDA runtime，依赖宿主机 nvidia-docker）
- 不包含项目特定代码（仅通用 PyTorch + Conda 环境）
- 不提供 Jupyter Notebook 等额外服务（保持基础镜像纯净）
- 不支持 Windows 容器（仅 Linux x86_64）
- 不处理 arm64/aarch64 架构（首个版本仅支持 amd64）

## Background & Context
- 用户明确要求 Python 3.14 + Anaconda3 环境
- 现有参考：[docker-ssh-dind/Containerfile](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/Containerfile) 提供了成熟的 Docker 镜像构建规范
- XMNN 项目已有 Python 3.14 + Conda 的实践：[environment.yml](file:///d:/spaces/SpecWeave/external/xmhub/xmnn/environment.yml) 验证了 Python 3.14 + conda-forge 的可行性
- TVM 项目的 conda 安装脚本：[ubuntu_install_conda.sh](file:///d:/spaces/SpecWeave/external/xmhub/npu_tvm/docker/install/ubuntu_install_conda.sh) 提供了 Miniconda 安装的参考
- 国内网络环境特点：访问官方 Anaconda repo、PyPI、Ubuntu 源速度慢且不稳定，大文件下载容易中断
- Docker 构建特性：分层缓存机制，RUN 指令失败会导致该层重建，合理分层可大幅提升重试成功率
- Conda 优势：预编译二进制包、科学计算库兼容性好、环境隔离清晰，适合深度学习场景

## Functional Requirements
- **FR-1**: 使用 Ubuntu 26.04 LTS 作为基础镜像，配置 zh_CN.UTF-8 locale 和 Asia/Shanghai 时区
- **FR-2**: 配置 apt 国内镜像源（阿里云），设置 `Acquire::Retries "5"` 重试机制
- **FR-3**: 安装 Miniconda3（到 /opt/conda），配置 conda 清华 TUNA 镜像源，设置包缓存和环境目录
- **FR-4**: 创建名为 `pytorch` 的 conda 环境，默认 Python 3.14，通过 build-arg `PYTHON_VERSION` 可调整
- **FR-5**: conda 环境默认激活（所有用户 .bashrc、ENTRYPOINT 中均激活），PATH 优先指向 conda 环境
- **FR-6**: 支持通过 build-arg `PYTORCH_VERSION` 指定 PyTorch 版本（默认 2.5.1），`TORCHVISION_VERSION` 指定 torchvision 版本
- **FR-7**: 支持通过 build-arg `USE_GPU=1` 切换为 GPU 版本（基于 nvidia/cuda 基础镜像 + CUDA 版 PyTorch），默认 CPU 版本
- **FR-8**: 支持离线安装模式：
  - build-arg `MINICONDA_INSTALLER`：本地 Miniconda 安装包路径（避免在线下载）
  - build-arg `CONDA_PKGS_CACHE`：本地 conda 包缓存目录（提前下载好的包）
  - build-arg `WHEEL_DIR=./wheels`：本地 wheel 包目录
- **FR-9**: 网络配置：
  - conda 配置清华 TUNA 镜像源（pkgs/main、pkgs/r、conda-forge、pytorch）
  - pip 配置阿里云镜像源和可信主机，设置 `--retries 10 --timeout 120`
  - wget/curl 配置重试次数
- **FR-10**: 创建非 root 用户 `ai`（UID 1000），加入 sudo 组，配置 NOPASSWD sudo，默认激活 pytorch conda 环境
- **FR-11**: 使用 tini 作为 init 进程，提供 entrypoint.sh 处理信号传递、conda 环境激活和用户切换
- **FR-12**: 镜像构建最后一步执行验证：`import torch`、检查版本、验证基本张量运算、验证 conda 环境正确性
- **FR-13**: 提供 `build.sh` 构建脚本，支持一键构建、参数传递（--gpu、--offline、--torch-version、--python-version）、构建后自动验证
- **FR-14**: 提供 `environment.yml` 作为 conda 环境配置文件（可被 docker build 或用户单独使用）
- **FR-15**: 提供 README.md 说明文档，包含使用示例、构建参数说明、其他镜像引用方式、离线构建指南

## Non-Functional Requirements
- **NFR-1**: 构建成功率：在国内普通网络环境下（非VPN），构建成功率≥90%（首次构建，缓存为空）
- **NFR-2**: 构建速度：利用 Docker 分层缓存和 conda/pip 缓存，系统包+Miniconda层缓存命中后，重复构建时间<10分钟
- **NFR-3**: 镜像体积：CPU 版本解压后≤5GB（Miniconda+PyTorch+Python 3.14 约 3-4GB），GPU 版本解压后≤10GB
- **NFR-4**: 可复用性：其他 Dockerfile 只需 `FROM pytorch-base:2.5.1-py314-cpu` 即可使用，conda 环境已默认激活
- **NFR-5**: 可维护性：Dockerfile 结构清晰，关键步骤有 `[BUILD]` 日志输出，每层职责单一
- **NFR-6**: 安全性：非 root 用户默认运行，不包含硬编码密码，apt 安全更新在构建时执行
- **NFR-7**: 环境兼容性：`conda activate pytorch` 在 login shell 和 non-login shell 中均可正常工作，与上层镜像兼容

## Constraints
- **Technical**: 
  - 基础镜像：CPU版使用 ubuntu:26.04，GPU版使用 nvidia/cuda 对应的 ubuntu26.04 runtime 镜像（如可用）
  - Conda 发行版：Miniconda3（非完整 Anaconda），安装到 /opt/conda
  - Python 版本：默认 3.14（用户要求），可通过 build-arg 调整
  - Conda channels：默认 conda-forge + pytorch（国内通过清华 TUNA 镜像访问）
  - PyTorch 安装：优先使用 conda 安装（二进制兼容性好），如 conda 无对应版本则回退到 pip
  - Python 3.14 注意事项：部分科学计算包可能尚未支持 Python 3.14，需验证 numpy/scipy 等核心依赖可用性
- **Business**:
  - 镜像放置在 `apps/pytorch-base/` 目录，作为 SpecWeave apps 下的基础组件
  - 遵循项目现有 Docker 镜像规范（参考 docker-ssh-dind）
- **Dependencies**:
  - Docker BuildKit 推荐启用（提升构建性能和缓存挂载支持）
  - GPU 版本运行需要宿主机安装 nvidia-docker2
  - conda 清华镜像源需可用（mirrors.tuna.tsinghua.edu.cn）

## Assumptions
- 假设构建机器已安装 Docker（版本≥24.0，支持 BuildKit cache mount）
- 假设国内网络访问清华 TUNA 镜像源稳定（mirrors.tuna.tsinghua.edu.cn）
- 假设 Python 3.14 + conda-forge + PyTorch 的组合在构建时可用（根据 XMNN 项目经验可行）
- 假设 conda 环境 `pytorch` 是默认环境，用户进入容器后直接可用
- 假设用户需要通用 PyTorch 环境，而非特定领域（如 transformers、mmcv 等额外库由上层镜像安装）
- 假设 CPU 版本是最常用的基础版本，作为默认配置
- 假设用户会基于此基础镜像构建自己的应用镜像，而非直接运行此镜像（此镜像默认 CMD 为 bash）

## Acceptance Criteria

### AC-1: 基础镜像构建成功
- **Given**: 网络环境为国内普通家庭宽带（无VPN），Docker 缓存为空
- **When**: 执行 `./build.sh`（或标准 docker build 命令）
- **Then**: 镜像构建成功完成，所有验证步骤通过，tag 为 `pytorch-base:2.5.1-py314-cpu`
- **Verification**: `programmatic`
- **Notes**: 构建过程中出现网络重试是正常的，只要最终成功即可

### AC-2: Conda 环境和 PyTorch 可正常使用
- **Given**: 镜像构建成功
- **When**: 执行 `docker run --rm pytorch-base:2.5.1-py314-cpu python -c "import torch; import sys; print('Python:', sys.version); print('PyTorch:', torch.__version__); x = torch.randn(3,3); print('Tensor op:', (x @ x.T).shape)"`
- **Then**: 输出正确的 Python 3.14 版本、PyTorch 版本号，张量乘法运算成功无报错
- **Verification**: `programmatic`

### AC-3: Conda 环境默认激活
- **Given**: 镜像构建成功
- **When**: 执行 `docker run --rm pytorch-base:2.5.1-py314-cpu which python` 和 `docker run --rm pytorch-base:2.5.1-py314-cpu conda info --envs`
- **Then**: python 路径指向 /opt/conda/envs/pytorch/bin/python，pytorch 环境有 * 标记（激活状态）
- **Verification**: `programmatic`

### AC-4: 国内源配置生效
- **Given**: 镜像构建成功，进入容器
- **When**: 执行 `conda config --show-sources` 和 `pip config get global.index-url`
- **Then**: conda channels 包含清华 TUNA 镜像地址，pip 使用阿里云镜像
- **Verification**: `programmatic` + `human-judgment`

### AC-5: 非 root 用户 ai 正常工作
- **Given**: 镜像构建成功
- **When**: 执行 `docker run --rm pytorch-base:2.5.1-py314-cpu whoami` 和 `docker run --rm pytorch-base:2.5.1-py314-cpu sudo -n whoami` 和 `docker run --rm pytorch-base:2.5.1-py314-cpu bash -lc "which python"`
- **Then**: 默认用户是 ai，sudo 免密正常工作，ai 用户也能正确使用 conda 环境中的 python
- **Verification**: `programmatic`

### AC-6: 可被其他 Dockerfile 引用
- **Given**: 已有 pytorch-base:2.5.1-py314-cpu 镜像
- **When**: 创建一个临时 Dockerfile 使用 `FROM pytorch-base:2.5.1-py314-cpu` 并 `RUN python -c "import torch; import conda"` 构建
- **Then**: 引用成功，无需重新安装 Conda 和 PyTorch，可直接 import torch 和使用 conda 命令
- **Verification**: `programmatic`

### AC-7: 离线安装模式可用
- **Given**: 提前下载好 Miniconda 安装包和 PyTorch 相关包到本地
- **When**: 执行 `./build.sh --offline` 或 `docker build --build-arg MINICONDA_INSTALLER=... --build-arg WHEEL_DIR=./wheels ...`
- **Then**: 构建过程不访问外部网络安装 Miniconda 和 PyTorch（可断网测试），从本地文件安装成功
- **Verification**: `programmatic`

### AC-8: GPU 版本构建可选
- **Given**: 网络正常
- **When**: 执行 `./build.sh --gpu`
- **Then**: 构建出 `pytorch-base:2.5.1-py314-gpu-cu124` 镜像，基于 nvidia/cuda 基础镜像，`torch.cuda.is_available()` 在有 GPU 的环境下返回 True
- **Verification**: `programmatic`（需 nvidia-docker 环境）

### AC-9: 中文环境和时区配置正确
- **Given**: 镜像构建成功
- **When**: 执行 `docker run --rm pytorch-base:2.5.1-py314-cpu locale` 和 `date`
- **Then**: LANG=zh_CN.UTF-8，时区为 Asia/Shanghai
- **Verification**: `programmatic`

### AC-10: 构建日志清晰可追溯
- **Given**: 正在执行构建
- **When**: 观察 docker build 输出
- **Then**: 每个关键阶段有 `=== Stage X/Y: ... ===` 标题和 `[BUILD]` 日志，可清晰看到当前进度（系统包、Miniconda、Conda环境、PyTorch、用户配置、验证）
- **Verification**: `human-judgment`

## Open Questions
- [x] 使用 Miniconda 还是完整 Anaconda？→ Miniconda（体积小，需要的包可后续 conda install）
- [x] conda 环境名是什么？→ pytorch（简洁明了）
- [x] PyTorch 安装用 conda 还是 pip？→ 优先 conda（二进制兼容性好），不支持的包回退 pip
- [ ] 是否需要预装常用的科学计算库（numpy、scipy、pandas、matplotlib）？→ numpy 是 PyTorch 依赖会自动安装，其他不预装（保持基础镜像轻量，上层镜像按需安装）
- [x] 是否支持 BuildKit cache mount 缓存 conda/pip 下载？→ 是，这是应对网络不稳定的重要手段
- [ ] 是否提供 PowerShell 版本构建脚本？→ 主要提供 bash 脚本（WSL/Linux 使用），README 说明 Windows 用户在 WSL 中运行
