# PyTorch Docker 基础镜像（Conda 版）- The Implementation Plan

## [ ] Task 1: 创建项目目录结构与 AGENTS.md
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `apps/pytorch-base/` 下创建完整目录结构
  - 创建 `AGENTS.md` 入口文件（遵循 docker-ssh-dind 项目模式）
  - 创建 `.dockerignore` 文件，排除不必要的文件
  - 创建 `wheels/` 目录（用于离线 wheel 包存放）
  - 创建 `conda-cache/` 目录（用于离线 conda 包缓存存放）
- **Acceptance Criteria Addressed**: [AC-1, AC-10]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构完整，AGENTS.md 包含"启动协议"关键词
  - `human-judgement` TR-1.2: AGENTS.md 正确引用父级 SpecWeave 规范和上下文路由表
- **Notes**: 参考 [docker-ssh-dind/AGENTS.md](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/AGENTS.md) 的结构

## [ ] Task 2: 创建 environment.yml Conda 环境定义
- **Priority**: high
- **Depends On**: [Task 1]
- **Description**:
  - 创建 `environment.yml`，定义名为 `pytorch` 的 conda 环境
  - 指定 Python 3.14、conda-forge 和 pytorch channels
  - 包含核心依赖：python=3.14、pip、pytorch、torchvision、torchaudio（CPU 版本通过 build-arg 控制）
  - 配置清华 TUNA 镜像源注释说明
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-2.1: environment.yml 语法正确，conda env create 可解析
  - `programmatic` TR-2.2: Python 版本指定为 3.14
  - `human-judgement` TR-2.3: channels 顺序合理（conda-forge 优先，pytorch 其次）
- **Notes**: 参考 XMNN 项目的 [environment.yml](file:///d:/spaces/SpecWeave/external/xmhub/xmnn/environment.yml)

## [ ] Task 3: 编写 Dockerfile（ubuntu:26.04 + Miniconda3 + PyTorch）
- **Priority**: high
- **Depends On**: [Task 2]
- **Description**:
  - Stage 1/7: 基础系统包+中文locale配置（ubuntu:26.04，apt阿里云源，tzdata，locales，tini，sudo，wget，bzip2等）
  - Stage 2/7: 安装 Miniconda3（支持本地安装包 MINICONDA_INSTALLER build-arg，默认在线下载，配置清华源）
  - Stage 3/7: 配置 conda 清华 TUNA 镜像源（.condarc）和 pip 阿里云镜像源（pip.conf）
  - Stage 4/7: 创建 pytorch conda 环境并安装 PyTorch（优先 conda 安装，支持离线 conda 包缓存 CONDA_PKGS_CACHE，支持 BuildKit cache mount 缓存 /opt/conda/pkgs）
  - Stage 5/7: 创建非root用户ai（UID 1000，sudo免密，配置.bashrc自动激活pytorch环境）
  - Stage 6/7: 安装entrypoint脚本并配置tini为init进程
  - Stage 7/7: 最终验证（conda环境检查、torch导入、版本检查、张量运算）+ 构建元信息写入 /etc/pytorch-base-build-info
  - GPU版本支持：通过USE_GPU build-arg控制，GPU版本从nvidia/cuda基础镜像开始构建
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-3.1: Dockerfile语法正确，`docker build` 无语法错误
  - `programmatic` TR-3.2: 每个Stage有明确的 `=== Stage X/7 ===` 标记和 `[BUILD]` 日志
  - `programmatic` TR-3.3: apt使用阿里云源，配置了 Acquire::Retries
  - `programmatic` TR-3.4: conda 配置了清华 TUNA 镜像源，pip 配置了阿里云镜像和 --retries 10 --timeout 120
  - `programmatic` TR-3.5: 验证步骤确保torch可导入，张量运算正常，conda 环境已激活
  - `programmatic` TR-3.6: Miniconda 安装到 /opt/conda，pytorch 环境在 /opt/conda/envs/pytorch
- **Notes**: 
  - 参考 docker-ssh-dind 的中文环境和用户配置规范
  - 参考 TVM 项目的 conda 安装方式
  - 使用 BuildKit `--mount=type=cache,target=/opt/conda/pkgs` 缓存 conda 下载
  - 使用 BuildKit `--mount=type=cache,target=/root/.cache/pip` 缓存 pip 下载

## [ ] Task 4: 编写 entrypoint.sh 启动脚本
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**:
  - 使用tini作为init进程（ENTRYPOINT中已指定，entrypoint负责逻辑）
  - 自动激活 pytorch conda 环境（source /opt/conda/etc/profile.d/conda.sh && conda activate pytorch）
  - 处理信号传递（SIGTERM/SIGINT正确转发给子进程）
  - 如果以root启动且没有指定--user，自动gosu/su切换到ai用户
  - 设置必要的环境变量（PATH、LD_LIBRARY_PATH等）
  - 如果没有传入CMD，默认启动login bash（自动激活环境）；否则exec执行传入的命令
  - 输出启动日志，显示 conda 环境名、Python版本、PyTorch版本等信息
- **Acceptance Criteria Addressed**: [AC-3, AC-5, AC-10]
- **Test Requirements**:
  - `programmatic` TR-4.1: entrypoint.sh可执行，正确处理命令传递
  - `programmatic` TR-4.2: 默认启动时切换到ai用户，conda环境已激活
  - `programmatic` TR-4.3: `docker run ... python` 直接使用pytorch环境的python
  - `human-judgement` TR-4.4: 启动日志清晰，显示版本信息
- **Notes**: 参考 [docker-ssh-dind/entrypoint.sh](file:///d:/spaces/SpecWeave/apps/docker-ssh-dind/entrypoint.sh) 和 [xmnn entrypoint-runtime.sh](file:///d:/spaces/SpecWeave/external/xmhub/xmnn/docker/entrypoint-runtime.sh)

## [ ] Task 5: 编写 build.sh 构建脚本
- **Priority**: high
- **Depends On**: [Task 3, Task 4]
- **Description**:
  - Bash脚本，自动启用 DOCKER_BUILDKIT=1
  - 支持命令行参数：
    - `--gpu`：构建GPU版本
    - `--offline`：离线构建模式（使用本地Miniconda安装包、conda包缓存、wheel）
    - `--torch-version X.Y.Z`：指定PyTorch版本
    - `--python-version X.Y`：指定Python版本（默认3.14）
    - `--tag <name>`：自定义镜像tag
    - `--no-cache`：禁用Docker缓存
    - `--help`：显示帮助
  - 自动传递对应build-arg参数
  - 构建完成后自动运行验证命令（AC-2、AC-3、AC-5、AC-9的验证命令）
  - 输出使用提示和后续运行命令
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-7, AC-8]
- **Test Requirements**:
  - `programmatic` TR-5.1: `./build.sh` 默认构建CPU版本，tag为pytorch-base:2.5.1-py314-cpu
  - `programmatic` TR-5.2: `./build.sh --help` 输出清晰的帮助信息
  - `programmatic` TR-5.3: 构建完成后自动运行验证命令，无报错
  - `human-judgement` TR-5.4: 脚本参数解析正确，错误提示清晰
- **Notes**: Windows 用户在 WSL2 Ubuntu 中运行此脚本

## [ ] Task 6: 离线安装逻辑完善与文档
- **Priority**: medium
- **Depends On**: [Task 3, Task 5]
- **Description**:
  - 完善 Dockerfile 中 MINICONDA_INSTALLER、CONDA_PKGS_CACHE、WHEEL_DIR 三个 build-arg 的逻辑
  - 编写 wheels/README.md 和 conda-cache/README.md 说明如何提前下载离线包：
    - Miniconda：wget 到本地
    - conda包：`conda create -n pytorch python=3.14 pytorch torchvision torchaudio --only-dl` 或 `conda download`
    - wheel：`pip download torch torchvision --index-url https://download.pytorch.org/whl/cpu -d ./wheels`
  - build.sh 的 --offline 模式自动配置三个离线路径
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-6.1: 提供本地Miniconda安装包时，不在线下载Miniconda
  - `programmatic` TR-6.2: 提供conda包缓存时，优先使用缓存
  - `programmatic` TR-6.3: WHEEL_DIR有wheel时，pip从本地安装
  - `human-judgement` TR-6.4: README说明清晰可操作
- **Notes**: 离线模式是应对网络极不稳定环境的最终保障

## [ ] Task 7: 编写 README.md 使用文档
- **Priority**: medium
- **Depends On**: [Task 5]
- **Description**:
  - 项目简介和定位（Python 3.14 + Miniconda3 + PyTorch 基础镜像，针对网络不稳定环境优化）
  - 快速开始：构建命令、运行验证命令
  - 构建参数说明（所有build-arg列表、默认值和说明）
  - build.sh 脚本参数说明
  - 使用方式：其他Dockerfile如何FROM引用此镜像，示例代码
  - 离线构建指南（如何预下载Miniconda、conda包、wheel）
  - GPU版本说明和nvidia-docker要求
  - 目录结构说明
  - 常见问题（网络问题重试、镜像体积、版本选择、conda环境激活问题）
- **Acceptance Criteria Addressed**: [AC-6, AC-7, AC-8]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 文档结构清晰，快速开始部分可直接复制命令执行
  - `human-judgement` TR-7.2: 其他镜像FROM引用示例明确可操作
  - `programmatic` TR-7.3: 文档中所有命令可执行（无明显拼写错误）
- **Notes**: 不创建多余文档，README.md作为唯一使用文档

## [ ] Task 8: 端到端构建与验证
- **Priority**: high
- **Depends On**: [Task 1, Task 3, Task 4, Task 5]
- **Description**:
  - 在 WSL2 Ubuntu 环境中执行 build.sh 构建 CPU 版本镜像
  - 运行 checklist.md 中的所有验证检查点
  - 构建一个简单的测试应用 Dockerfile FROM pytorch-base，验证可复用性
  - 验证 conda 环境在 login shell 和 non-login shell 中均正确激活
  - 记录构建过程中遇到的问题并修复
  - （可选，如果有 nvidia-docker 环境）测试 GPU 版本
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-9]
- **Test Requirements**:
  - `programmatic` TR-8.1: build.sh 执行成功，镜像构建完成
  - `programmatic` TR-8.2: checklist.md 中所有验证点通过
  - `programmatic` TR-8.3: 测试 FROM 引用的 Dockerfile 构建成功，torch 可导入，conda 命令可用
  - `human-judgement` TR-8.4: 构建过程重试机制生效（如遇网络波动）
- **Notes**: 用户环境为 Windows + WSL2，需要在 WSL 中执行构建
