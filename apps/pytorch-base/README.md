# PyTorch Docker 基础镜像

基于 **ubuntu:26.04 LTS** + **Miniconda3** + **Python 3.14** + **PyTorch 2.13.0** 的 Docker 基础镜像，严格遵循 [PyTorch 官方安装指南](https://pytorch.org/get-started/locally/)，专为网络不稳定环境优化。

## 特性

- **基础镜像**：ubuntu:26.04 LTS（glibc ≥ 2.28，官方支持）
- **Python**：3.14（通过 Miniconda3 安装，支持 3.10-3.14）
- **PyTorch**：默认 2.13.0（最新稳定版，per pytorch.org）
- **CUDA 支持**：默认 CPU 版本，GPU 版本支持 CUDA 12.6/13.0/13.2（默认 12.6）
- **安装方式**：pip 优先（官方推荐），conda 作为 fallback
- **国内镜像源**：apt 使用阿里云源，conda 使用清华 TUNA 源，pip 使用阿里云源
- **离线构建支持**：所有资源可提前下载到 `offline/` 目录，无网络环境也能构建
- **三阶段安装策略**：本地 wheel → 官方 PyTorch 索引 → 国内镜像 → conda fallback
- **BuildKit 缓存**：自动缓存 conda 和 pip 下载，加速重复构建
- **网络容错**：所有下载均配置重试机制（5-10次重试，30-120秒超时）
- **非 root 用户**：默认以 `ai` 用户（UID 1000）运行，配置 sudo 免密
- **中文环境**：默认 locale 为 `zh_CN.UTF-8`，时区 `Asia/Shanghai`
- **自动验证**：构建脚本自动运行官方验证测试（`torch.rand(5,3)` + `torch.cuda.is_available()`）
- **tini 初始化**：使用 tini 作为 PID 1，正确处理信号转发和僵尸进程

## 官方安装命令对照

根据 [pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)（Linux + Pip + Python）：

| 计算平台 | 官方命令 | 本镜像 build 命令 |
|---------|---------|------------------|
| CPU | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu` | `./build.sh` |
| CUDA 12.6 | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126` | `./build.sh --gpu` |
| CUDA 13.0 | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu130` | `./build.sh --gpu --cuda 13.0` |
| CUDA 13.2 | `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu132` | `./build.sh --gpu --cuda 13.2` |

## 快速开始

### 在线构建（推荐）

```bash
cd apps/pytorch-base

# 默认 CPU 版本（PyTorch 2.13.0 + Python 3.14）
./build.sh

# GPU 版本（CUDA 12.6，官方默认推荐）
./build.sh --gpu

# GPU 版本（CUDA 13.0）
./build.sh --gpu --cuda 13.0

# 指定版本
./build.sh --torch-version 2.13.0 --python-version 3.14

# 自定义标签
./build.sh --tag my-pytorch:latest

# 静默模式（不显示启动横幅）
./build.sh --quiet
```

### 离线构建

适用于无法联网的环境，需要两步：

```bash
# 第一步：在有网络的机器上下载离线资源
./build.sh --prepare-offline
# 如需准备 GPU 版本离线包
./build.sh --gpu --prepare-offline

# 第二步：将整个 pytorch-base 目录复制到离线机器后构建
./build.sh --offline
```

离线资源存放位置：
- `offline/miniconda/` - Miniconda 安装脚本
- `offline/wheels/` - pip wheel 包（torch、torchvision 等）
- `offline/conda-pkgs/` - conda 包缓存（可选）

### 验证镜像

```bash
# 官方推荐验证（per pytorch.org）
docker run --rm pytorch-base:2.13.0-py3.14-cpu \
    python -c "import torch; x = torch.rand(5, 3); print(x); print('PyTorch', torch.__version__)"

# CUDA 可用性检查
docker run --rm pytorch-base:2.13.0-py3.14-cpu \
    python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# 张量运算验证
docker run --rm pytorch-base:2.13.0-py3.14-cpu \
    python -c "import torch; x=torch.randn(3,3); y=x@x.T; print(f'Tensor OK: {y.shape}')"

# 交互式 shell
docker run -it --rm pytorch-base:2.13.0-py3.14-cpu

# GPU 版本验证（需要 nvidia-docker2）
docker run --rm --gpus all pytorch-base:2.13.0-py3.14-gpu-cu126 \
    python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

### 作为基础镜像使用

在其他 Dockerfile 中直接引用：

```dockerfile
FROM pytorch-base:2.13.0-py3.14-cpu

# conda 环境 'pytorch' 已自动激活，pip 使用阿里云镜像
RUN pip install --no-cache-dir pandas scikit-learn

# 复制项目代码
COPY . /workspace/myapp

# 默认用户为 ai（非 root），如需 root 操作请在前面加 USER root
WORKDIR /workspace/myapp

# 自定义启动命令
CMD ["python", "train.py"]
```

如需以 root 运行：
```dockerfile
FROM pytorch-base:2.13.0-py3.14-cpu
USER root
RUN apt-get update && apt-get install -y some-package
USER ai
```

## 构建脚本参数

```bash
./build.sh [OPTIONS]

选项：
  --gpu                 构建 GPU 版本（默认 CUDA 12.6）
  --cuda VER            CUDA 版本（默认：12.6，可选：12.6/13.0/13.2）
  --offline             使用 offline/ 目录中的本地包构建
  --prepare-offline     下载离线资源但不构建镜像
  --torch-version VER   PyTorch 版本（默认：2.13.0）
  --python-version VER  Python 版本（默认：3.14，支持：3.10-3.14）
  --tag NAME            自定义镜像标签
  --no-cache            禁用 Docker 构建缓存
  --no-verify           跳过构建后验证
  --quiet, -q           静默模式（容器启动时不显示横幅）
  --help, -h            显示帮助信息
```

## 目录结构

```
pytorch-base/
├── Dockerfile              # 主构建文件（7阶段构建）
├── build.sh                # 一键构建脚本
├── entrypoint.sh           # 容器入口点
├── environment.yml         # Conda 环境定义（本地开发参考）
├── .dockerignore           # Docker 忽略规则
├── AGENTS.md               # AI 协作者入口
├── README.md               # 本文档
└── offline/                # 离线资源目录（--prepare-offline 自动生成）
    ├── miniconda/          # Miniconda 安装脚本
    ├── wheels/             # pip wheel 包（torch, torchvision, numpy 等）
    └── conda-pkgs/         # conda 包缓存（可选）
```

## Dockerfile 构建阶段

| 阶段 | 内容 | 说明 |
|-----|------|------|
| Stage 1/7 | 系统包 + 中文环境 | 配置阿里云 apt 源（先 HTTP 安装 ca-certificates，再切 HTTPS）、安装系统依赖、中文 locale、时区、tini、gosu |
| Stage 2/7 | 安装 Miniconda3 | 优先使用 offline/ 中的本地安装包，否则从清华 TUNA 镜像下载，禁用 base 自动激活 |
| Stage 3/7 | 配置镜像源 | 配置清华 conda 源（含 pytorch/nvidia 通道）、阿里云 pip 源、重试参数 |
| Stage 4/7 | 创建 conda 环境 + 安装 PyTorch | 创建 pytorch 环境，**pip 优先**（本地 wheel → 官方 PyTorch 索引 → 阿里云镜像 → conda fallback） |
| Stage 5/7 | 创建非 root 用户 | 删除默认 ubuntu 用户，创建 ai 用户（UID 1000），配置 sudo 免密、conda 自动激活、bashrc/profile.d |
| Stage 6/7 | 安装 entrypoint | 复制并设置入口点脚本权限 |
| Stage 7/7 | 最终验证 + 元数据 | 官方验证（torch.rand + CUDA 检查）、写入构建信息到 /etc/pytorch-base-build-info |

## PyTorch 安装策略（Stage 4 详解）

镜像采用**四阶段 fallback 策略**确保在各种网络环境下都能安装成功：

1. **本地 wheel 优先**：检查 `offline/wheels/torch-*.whl`，存在则本地安装
2. **官方 PyTorch 索引**：`pip install torch==<ver> torchvision --index-url https://download.pytorch.org/whl/cuXXX`（或 `/cpu`），完全遵循官方指南
3. **国内镜像 fallback**：如果官方索引超时，使用配置好的阿里云 pip 镜像
4. **conda 最终 fallback**：pip 全部失败时使用 conda 安装（含 nvidia 通道的 GPU 支持）

## 运行时环境变量

| 变量 | 默认值 | 说明 |
|-----|-------|------|
| `CONDA_DIR` | `/opt/conda` | Miniconda 安装路径 |
| `ENV_NAME` | `pytorch` | conda 环境名称 |
| `ENV_PATH` | `/opt/conda/envs/pytorch` | conda 环境路径 |
| `PATH` | 以 `/opt/conda/envs/pytorch/bin` 开头 | conda 环境 bin 优先 |
| `DEBIAN_FRONTEND` | `noninteractive` | 禁用 apt 交互式提示 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `LANG` / `LC_ALL` | `zh_CN.UTF-8` | 中文 locale |
| `PIP_INDEX_URL` | 阿里云 PyPI 镜像 | pip 默认使用国内源 |
| `PYTHONUNBUFFERED` | `1` | Python 输出不缓冲 |
| `ENTRYPOINT_QUIET` | (空) | 设为 `1` 禁用启动横幅 |

运行时可覆盖：
```bash
# 覆盖环境变量
docker run --rm -e ENTRYPOINT_QUIET=1 pytorch-base:2.13.0-py3.14-cpu python -c "import torch; print(torch.__version__)"

# 指定以 root 运行
docker run --rm -e RUN_AS_USER=root pytorch-base:2.13.0-py3.14-cpu whoami
```

## 手动 docker build（不使用 build.sh）

```bash
# 启用 BuildKit（必需，用于缓存挂载）
export DOCKER_BUILDKIT=1

# 基础 CPU 版本
docker build -t pytorch-base:custom \
    --build-arg BASE_IMAGE=ubuntu:26.04 \
    --build-arg USE_GPU=0 \
    --build-arg PYTHON_VERSION=3.14 \
    --build-arg PYTORCH_VERSION=2.13.0 \
    -f Dockerfile .

# GPU 版本（CUDA 12.6）
docker build -t pytorch-base:gpu \
    --build-arg USE_GPU=1 \
    --build-arg CUDA_VERSION=12.6 \
    -f Dockerfile .

# 离线构建
docker build -t pytorch-base:offline \
    --build-arg USE_GPU=0 \
    -f Dockerfile .
```

## 常见问题

### Q: Python 3.14 与 PyTorch 兼容性如何？

A: 根据 PyTorch 官方文档，PyTorch 2.13.0（最新稳定版）支持 Python 3.10-3.14。本镜像默认使用 Python 3.14。如需使用更保守的版本，可指定 `--python-version 3.12` 或 `--python-version 3.11`。

### Q: 构建过程中网络超时怎么办？

A: 镜像已配置以下容错机制：
- apt：5次重试，30秒超时
- wget：5次重试，120秒超时，5秒重试间隔
- pip：10次重试，120秒超时
- 四阶段 fallback：本地 wheel → 官方索引 → 阿里云镜像 → conda
- BuildKit 缓存：重复构建时自动使用缓存的包

如果网络仍然不稳定，建议使用离线模式：先在网络良好的环境执行 `./build.sh --prepare-offline` 下载所有资源，再离线构建。

### Q: GPU 版本的基础镜像为什么不用 nvidia/cuda？

A: 用户要求统一使用 ubuntu:26.04 作为基础镜像。GPU 版本通过 pip 从 `download.pytorch.org/whl/cuXXX` 安装 CUDA 版 PyTorch（包含 CUDA runtime），宿主机只需安装 NVIDIA 驱动和 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) 即可。如果需要完整 CUDA toolkit，可在子镜像中安装或改用 nvidia/cuda 基础镜像。

### Q: 为什么不强制安装 torchaudio？

A: 根据 PyTorch 官方安装指南，`torchaudio` 是可选组件，官方默认安装命令仅包含 `torch` 和 `torchvision`。本镜像遵循官方最小化安装原则，torchaudio 可按需安装：
```bash
pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Q: 镜像体积多大？

A: CPU 版本约 3-4GB（包含 Miniconda + Python 3.14 + PyTorch 2.13.0 + 系统工具）。GPU 版本略大。可通过多阶段构建在子镜像中进一步精简。

### Q: 如何安装额外的 Python 包？

A: 有几种方式：
1. 在子 Dockerfile 中：`RUN pip install <package>`（默认使用阿里云源）
2. 运行时安装：`docker run --rm pytorch-base pip install <package>`（临时）
3. 离线 wheel 包：将 .whl 文件放入 `offline/wheels/` 后重新构建（额外 wheel 会在 Stage 4 自动安装）

### Q: 为什么用 Miniconda3 而不是系统 Python 或 Anaconda3？

A: 
- Miniconda3 轻量（相比完整 Anaconda3 节省数 GB），同时保留 conda 环境管理能力
- 支持灵活切换 Python 版本（3.10-3.14）
- conda-forge 提供丰富的科学计算包，解决编译依赖问题
- pip 作为主要 PyTorch 安装方式（官方推荐），conda 作为 fallback

## 构建元数据

构建成功后，镜像内 `/etc/pytorch-base-build-info` 文件记录完整构建信息：
```
PYTORCH_BASE_IMAGE=ubuntu:26.04
USE_GPU=0
PYTHON_VERSION=3.14
PYTORCH_VERSION=2.13.0
CUDA_VERSION=12.6
CONDA_DIR=/opt/conda
ENV_NAME=pytorch
BUILD_DATE=2026-01-XXTXX:XX:XXZ
ENTRYPOINT_QUIET=0
```

查看方式：
```bash
docker run --rm pytorch-base:2.13.0-py3.14-cpu cat /etc/pytorch-base-build-info
```
