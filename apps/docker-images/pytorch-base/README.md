# PyTorch GPU Docker 基础镜像

基于 **ubuntu:26.04** + **Miniforge3** + **Python 3.14.6** + **PyTorch 2.13.0** 的 GPU 优先 Docker 基础镜像，默认构建 **CUDA 12.6 GPU 版本**，包含完整 PyTorch 三件套（torch + torchvision + torchaudio）和 ONNX Runtime GPU 支持，严格遵循 [PyTorch 官方安装指南](https://pytorch.org/get-started/locally/)，专为国内网络环境优化。

## 特性

- **默认 GPU 版本**：CUDA 12.6（开箱即用 GPU 加速），CPU 版本需显式 `--cpu`
- **基础镜像**：ubuntu:26.04（glibc ≥ 2.28，官方支持）
- **Conda 发行版**：Miniforge3（conda-forge native + libmamba solver，比 Miniconda3 更快更稳）
- **Python**：3.14.6（GIL-enabled，精确 patch 版本）
- **PyTorch 三件套**：torch 2.13.0 + torchvision + torchaudio（官方完整三件套）
- **ONNX Runtime**：onnxruntime-gpu（含 CUDAExecutionProvider，GPU 推理加速）
- **CUDA 运行时**：通过 pip wheel 内置（nvidia-cuda-runtime-cu12 等），无需宿主机装完整 CUDA toolkit
- **CUDA 多版本**：支持 12.6 / 12.8 / 13.0（通过 `--cuda` 参数切换）
- **四级安装 fallback**：本地 wheel → PyTorch 官方索引 → 国内镜像 → conda fallback
- **国内镜像源**：apt 阿里云源，conda BFSU 源（默认）/ TUNA，pip 阿里云源（默认）
- **Miniforge 三源 fallback**：BFSU → TUNA → GitHub 官方
- **离线构建支持**：所有资源可提前下载到 `offline/` 目录，无网络环境也能构建
- **BuildKit 缓存**：自动缓存 apt/conda/pip 下载，加速重复构建
- **网络容错**：所有下载配置重试机制（5-10次重试，30-120秒超时）
- **非 root 用户**：默认以 `ai` 用户（UID 1000）运行，配置 sudo 免密
- **中文环境**：默认 locale 为 `zh_CN.UTF-8`，时区 `Asia/Shanghai`
- **构建后综合验证**：19项自动验证（含 CUDA 版本一致性、ORT providers、GPU tensor 运算）
- **交互式 GPU Banner**：启动时自动显示 GPU 设备列表、显存大小、ORT 状态
- **tini 初始化**：使用 tini 作为 PID 1，正确处理信号转发和僵尸进程

## 宿主机前置要求（GPU 版本）

| 组件 | 最低版本 |
|------|---------|
| NVIDIA 驱动 | ≥ 525.60.13（CUDA 12.x）；≥ 570（CUDA 13.0） |
| Docker Engine | ≥ 20.10 |
| NVIDIA Container Toolkit | ≥ 1.13 |
| BuildKit | 启用（Docker 23.0+ 默认启用） |

验证 GPU 可用：
```bash
nvidia-smi  # 显示 GPU 列表和驱动版本
```

## 快速开始

### 在线构建（推荐）

```bash
cd apps/docker-images/pytorch-base

# 默认 GPU 版本（PyTorch 2.13.0 + CUDA 12.6 + Python 3.14.6，国内镜像源）
./build.sh

# CPU 版本
./build.sh --cpu

# GPU 版本（CUDA 13.0，实验性）
./build.sh --cuda 13.0

# 指定版本
./build.sh --torch-version 2.13.0 --python-version 3.14.6

# 自定义标签
./build.sh --tag my-pytorch:latest

# 静默模式
./build.sh --quiet
```

### 离线构建

**第一步**：在有网络的机器上准备离线资源（约 3-5 GB）：

```bash
./build.sh --prepare-offline
```

这会下载：
- `offline/miniforge/Miniforge3-Linux-x86_64.sh`（~120 MB）
- `offline/wheels/` 下的 torch、torchvision、torchaudio、onnxruntime-gpu、nvidia-* 等 wheel 包

**第二步**：将整个目录拷贝到离线机器，执行离线构建：

```bash
./build.sh --offline
```

查看离线资源状态：
```bash
./build.sh --list-offline
```

## 运行容器

### GPU 版本

```bash
# 交互式 shell（自动显示 GPU 信息 banner）
docker run --gpus all -it --rm xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu

# 验证 GPU 可用
docker run --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu \
  python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Devices: {torch.cuda.device_count()}')"

# GPU tensor 运算测试
docker run --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu \
  python -c "import torch; x=torch.randn(2000,2000,device='cuda'); print('GPU matmul OK:', (x@x.T).shape)"

# ONNX Runtime GPU 验证
docker run --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu \
  python -c "import onnxruntime as ort; print('ORT providers:', ort.get_available_providers())"

# 挂载数据目录
docker run --gpus all -it --rm -v $(pwd)/data:/workspace/data xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu
```

### CPU 版本

```bash
docker run -it --rm xinetzone/pytorch:2.13.0-cpu-py3.14.6
```

### 作为基础镜像

```dockerfile
FROM xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu

# conda 环境 pytorch 已自动激活
RUN pip install transformers datasets accelerate

WORKDIR /workspace
COPY train.py .
CMD ["python", "train.py"]
```

## 镜像标签格式

```
xinetzone/pytorch:<pytorch_version>-cuda<cuda_version>-py<python_version>-gpu
xinetzone/pytorch:<pytorch_version>-cpu-py<python_version>
```

示例：
- `xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu`（默认 GPU 版本）
- `xinetzone/pytorch:2.13.0-cuda13.0-py3.14.6-gpu`（CUDA 13.0）
- `xinetzone/pytorch:2.13.0-cpu-py3.14.6`（CPU 版本）

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NVIDIA_VISIBLE_DEVICES` | `all` | GPU 可见设备 |
| `NVIDIA_DRIVER_CAPABILITIES` | `compute,utility` | NVIDIA 驱动能力 |
| `LD_LIBRARY_PATH` | torch.lib + nvidia lib | CUDA 库路径 |
| `ENTRYPOINT_DEBUG` | `0` | 设为 `1` 启用 entrypoint 调试日志 |
| `ENTRYPOINT_QUIET` | `0` | 设为 `1` 抑制启动 banner |
| `RUN_AS_USER` | `ai` | 非 root 用户切换目标 |

## 构建参数（Dockerfile ARG / build.sh 参数）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--cpu` | off | 构建 CPU-only 版本 |
| `--cuda <ver>` | `12.6` | CUDA 版本（12.6/12.8/13.0） |
| `--torch-version <ver>` | `2.13.0` | PyTorch 版本 |
| `--python-version <ver>` | `3.14.6` | Python 版本 |
| `--tag <name>` | 自动生成 | 自定义镜像标签 |
| `--no-cache` | off | 禁用 Docker 构建缓存 |
| `--quiet` | off | 减少日志输出 |
| `--offline` | off | 使用离线资源构建 |
| `--prepare-offline` | off | 准备离线资源 |
| `--list-offline` | off | 列出离线资源状态 |
| `--no-verify` | off | 跳过构建后验证 |
| `--conda-mirror <src>` | `bfsu` | conda 镜像源（bfsu/tuna/official） |
| `--pip-mirror <src>` | `aliyun` | pip 镜像源（aliyun/tuna/official） |

## 交互式启动 Banner 示例

```
============================================================
  PyTorch GPU Base Image (Miniforge3 + Python + PyTorch CUDA)
============================================================

  Conda env : pytorch (/opt/conda/envs/pytorch)
  Python    : Python 3.14.6
  PyTorch   : 2.13.0+cu126
  CUDA ver  : 12.6 (torch builtin)
  GPUs      : 1 device(s)
    [0]     : NVIDIA GeForce RTX 4090 23.6 GB
  torchvis  : 0.20.0+cu126
  torchaudio: 2.13.0+cu126
  ONNX RT   : 1.27.0
    GPU     : CUDAExecutionProvider enabled
  User      : ai
  Workdir   : /workspace

  Quick test: python -c 'import torch; x=torch.rand(5,3); print(x)'
  Tip: conda env 'pytorch' is already activated on PATH
  Tip: Set ENTRYPOINT_DEBUG=1 for verbose logging
============================================================
```

## 目录结构

```
pytorch-base/
├── Dockerfile              # 7阶段多阶段构建
├── build.sh                # 构建脚本（GPU默认+离线+验证）
├── build.ps1               # PowerShell 版本（Windows）
├── entrypoint.sh           # 入口脚本（conda激活+用户切换+GPU banner）
├── profile.d/
│   └── conda-init.sh       # Shell conda 自动激活
├── offline/                # 离线构建资源（gitkeep占位）
│   ├── miniforge/          # Miniforge3 安装包
│   ├── wheels/             # pip wheel 缓存
│   └── conda-pkgs/         # conda 包缓存
└── .agents/                # AI 智能体开发规范
    ├── AGENTS.md
    └── rules/
        ├── dockerfile.md
        ├── build-test.md
        └── entrypoint.md
```

## 常见问题

**Q: 构建时提示 `torch.cuda.is_available()=False` 但我明明有 GPU？**
A: 这是正常的！构建阶段容器没有挂载 GPU。`--gpus all` 是运行时参数。构建只验证 CUDA 库存在性和版本一致性，运行时才能检测到 GPU。

**Q: 运行时 `torch.cuda.is_available()` 为 False？**
A: 检查：
1. 宿主机 `nvidia-smi` 是否正常
2. 是否安装了 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
3. docker run 是否加了 `--gpus all` 参数

**Q: 网络不好导致构建失败？**
A: 使用 `--prepare-offline` 在有网络时下载所有资源，然后 `--offline` 构建。

**Q: 想在 WSL2 中使用 GPU？**
A: WSL2 支持 GPU 直通，确保 Windows 侧安装 NVIDIA Game Ready/Studio 驱动 ≥ 525，WSL2 内无需额外装驱动，安装 nvidia-container-toolkit 即可。

**Q: Miniforge3 和 Miniconda3 的区别？**
A: Miniforge3 是 conda-forge 社区维护的发行版：
- 默认使用 conda-forge 通道（包更全更新更快）
- 内置 libmamba solver（依赖解析速度提升 5-10 倍）
- 无 Anaconda 商业授权风险

**Q: CUDA 13.0 稳定吗？**
A: CUDA 13.0 于 2025 年底发布，需 PyTorch 2.13+ 正式版支持。生产环境建议使用 CUDA 12.6（PyTorch 官方默认推荐）。

## 变更历史

### v3.0（2026-04-15）
- 默认构建 GPU 版本（CUDA 12.6）
- Miniconda3 → Miniforge3（conda-forge + libmamba solver）
- Python 3.14.6（精确 patch）
- PyTorch 2.13.0
- 新增 torchvision + torchaudio 三件套
- 新增 onnxruntime-gpu（CUDAExecutionProvider）
- CUDA 运行时库 pip wheel 内置
- 支持 CUDA 12.6/12.8/13.0
- GPU 设备列表+显存 banner
- 19项综合构建后验证
