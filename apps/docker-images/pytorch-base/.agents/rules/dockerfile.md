---
id: "pytorch-dockerfile-rules"
title: "Dockerfile 多阶段构建规范"
source: "AGENTS.md#项目特有约束"
---
# Dockerfile 多阶段构建规范（pytorch-base v3.0）

<a id="基础约定"></a>
## 基础约定

- 文件名为 `Dockerfile`，首行声明 BuildKit 语法：`# syntax=docker/dockerfile:1.7-labs`
- 基础镜像：`ubuntu:26.04`（固定版本，通过 `BASE_IMAGE` ARG 可覆盖）
- 默认构建 **GPU 版本**（CUDA 12.6），CPU 版本通过 `--cpu` 参数构建
- Conda 发行版：**Miniforge3**（conda-forge native + libmamba solver），不再使用 Miniconda3
- Python 版本：**3.14.6**（GIL-enabled 标准构建，精确 patch 版本）
- PyTorch 三件套：torch + torchvision + torchaudio（官方完整三件套）
- GPU 附加组件：onnxruntime-gpu（含 CUDAExecutionProvider）
- 构建注释/日志使用**英文**（避免 PowerShell/Shell 编码问题）
- 启用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`，管道中任何命令失败立即终止
- 结构化日志前缀：`[STAGE]`/`[ACTION]`/`[OK]`/`[WARN]`/`[ERROR]`/`[TIMER]`/`[VALIDATE]`
- 每个Stage输出 `[TIMER]` 耗时统计，最终Stage输出汇总表

## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| BASE_IMAGE | ubuntu:26.04 | 基础镜像 |
| USE_GPU | 1 | 1=CUDA版（默认）, 0=CPU版 |
| PYTHON_VERSION | 3.14.6 | Python版本（精确patch版本） |
| PYTORCH_VERSION | 2.13.0 | PyTorch版本 |
| CUDA_VERSION | 12.6 | CUDA版本（GPU模式，支持12.6/12.8/13.0） |
| CONDA_MIRROR | bfsu | conda镜像：bfsu/tuna/official |
| PIP_MIRROR | aliyun | pip镜像：aliyun/tuna/official |
| QUIET | 0 | 安静模式 |

## 7阶段结构（Runtime Logical Layering v1.3）

按变化频率从低到高排列，最大化缓存命中率：

1. **Stage 1/7**：系统包 + locale/timezone + APT镜像源配置（变化频率：最低）
   - 安装：ca-certificates, tzdata, locales, tini, sudo, wget, curl, bzip2, gzip, tar, xz-utils, git, build-essential, gosu, patchelf
   - 先HTTP安装ca-certificates，再切HTTPS apt源
2. **Stage 2/7**：Miniforge3 安装到 `/opt/conda`（变化频率：低）
   - 支持离线/在线下载，多镜像fallback（BFSU→TUNA→GitHub官方）
   - 启用 libmamba solver（加速依赖解析）
   - 禁用 base 环境自动激活
3. **Stage 3/7**：conda + pip 镜像源配置（国内源切换）（变化频率：低）
   - conda源：BFSU（默认）/ TUNA / 官方，含 conda-forge/pytorch/nvidia 通道
   - pip源：阿里云（默认）/ 清华TUNA / 官方，配置10次重试120秒超时
4. **Stage 4/7**：conda环境创建（pytorch环境）+ PyTorch三件套 + onnxruntime-gpu（变化频率：中，主要耗时阶段）
   - Python 3.14.6 精确版本
   - 4级fallback：本地wheel → PyTorch官方索引 → pip镜像 → conda fallback
   - GPU模式安装 onnxruntime-gpu，CPU模式安装 onnxruntime
   - 构建后立即验证Python导入
5. **Stage 5/7**：非root用户 `ai`(UID 1000) 创建 + sudo配置 + 权限设置（变化频率：中）
   - chmod -R a+rX /opt/conda（确保所有用户可读conda）
6. **Stage 6/7**：entrypoint安装 + profile.d脚本COPY + 语法验证（变化频率：高）
7. **Stage 7/7**：build-info写入 + GPU/CPU综合验证 + 激进清理 + 耗时汇总表（变化频率：最低）
   - 验证项：Python路径、torch/vision/audio导入、CUDA版本一致性、CUDA库存在性、ORT providers、tensor运算、numpy、tini、gosu
   - 无GPU时 `torch.cuda.is_available()=False` 是正常行为，不报错
   - 修复PyTorch .so文件的executable stack标志
   - 激进清理：__pycache__、*.pyc/pyo、conda包缓存tar.bz2、文档/man页

## 层缓存优化

- 使用 BuildKit `--mount=type=cache` 缓存 apt/conda/pip：
  ```dockerfile
  RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
      --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
      apt-get update -qq && apt-get install -y --no-install-recommends -qq ...
  ```
- conda缓存：`--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- pip缓存：`--mount=type=cache,target=/root/.cache/pip,sharing=locked`
- 多个RUN指令合并为一个（用 `&& \` 连接），减少镜像层数
- apt-get update 和 install 在同一个RUN中，避免缓存过期
- COPY指令放在靠后阶段

## 中文环境配置

```dockerfile
ENV TZ=Asia/Shanghai
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8
```

与其他项目一致，使用sed修改locale.gen后生成locale。

## Conda环境规范

- Miniforge安装路径：`/opt/conda`
- 环境名：`pytorch`
- 环境路径：`/opt/conda/envs/pytorch/`
- Python版本：3.14.6（通过PYTHON_VERSION ARG控制，默认精确patch版本）
- 自动激活：通过 `/etc/profile.d/conda.sh` 和 `.bashrc` 实现
- pip作为主要PyTorch安装方式（官方推荐），conda作为最终fallback
- libmamba solver默认启用

## GPU运行时环境变量

```dockerfile
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV LD_LIBRARY_PATH=/opt/conda/envs/pytorch/lib/python3.14/site-packages/torch/lib:/usr/local/nvidia/lib64:${LD_LIBRARY_PATH}
```

运行GPU容器需要：
- 宿主机安装 NVIDIA 驱动（CUDA 12.6 需要驱动 ≥ 525.60.13）
- 安装 NVIDIA Container Toolkit
- docker run 时加 `--gpus all` 参数

## 离线资源支持

所有离线资源统一存放在 `offline/` 目录（始终包含在构建上下文中）：

| 子目录 | 内容 | 对应安装阶段 |
|--------|------|-------------|
| `offline/miniforge/` | Miniforge安装脚本(.sh) | Stage 2 |
| `offline/wheels/` | pip wheel包（torch/torchvision/torchaudio/onnxruntime-gpu等） | Stage 4 |
| `offline/conda-pkgs/` | conda包缓存 | Stage 4 |

Dockerfile中通过检测文件是否存在实现条件离线安装（COPY + shell条件判断）。
准备离线资源：`./build.sh --prepare-offline`。

<a id="安全规范"></a>
## 安全规范

- 禁止在Dockerfile中硬编码密码、密钥、token
- 默认以非root用户 `ai` 运行（通过USER指令或entrypoint gosu切换）
- sudo权限通过NOPASSWD配置（可通过环境变量控制）
- APT配置5次重试，wget配置5次重试/120秒超时
- 镜像内无SSH服务，仅保留必要运行时工具

<a id="非-root-用户规范"></a>
## 非root用户规范

- 固定用户名 `ai`，UID 1000
- 默认配置 NOPASSWD sudo
- HOME 目录为 `/home/ai`
- WORKDIR 设置为 `/workspace`
- 支持作为其他项目的基础镜像（FROM pytorch-base）

<a id="网络容错"></a>
## 网络容错

- APT：`Acquire::Retries "5"` 配置5次重试，30秒超时
- wget：`--tries=5 --timeout=120 --waitretry=5` 5次重试/120秒超时/5秒间隔
- Miniforge下载：三镜像fallback（BFSU→TUNA→GitHub官方）
- PyTorch安装：四级fallback（本地wheel→PyTorch官方索引→pip镜像→conda）
- pip：`retries=10 timeout=120` 10次重试120秒超时
- 支持国内镜像源切换（通过build-arg CONDA_MIRROR/PIP_MIRROR控制）

## 镜像源切换

通过构建参数支持国内镜像：
- APT源：阿里云（固定）
- conda源：BFSU（默认）/ 清华TUNA / 官方
- pip源：阿里云（默认）/ 清华TUNA / 官方

## 验证清单

- [ ] `bash build.sh` 无错误，构建日志有清晰的Stage标记和[TIMER]耗时
- [ ] `bash build.sh --prepare-offline` 可下载离线资源（含Miniforge3、torch三件套、onnxruntime-gpu）
- [ ] `bash build.sh --offline` 可离线构建
- [ ] `bash build.sh --cpu` 可构建CPU-only版本
- [ ] 镜像中 `locale -a` 显示 zh_CN.UTF-8
- [ ] 镜像中 `date` 显示 Asia/Shanghai 时区
- [ ] `id ai` 显示 uid=1000，groups包含sudo
- [ ] `source /opt/conda/etc/profile.d/conda.sh && conda activate pytorch && python -c "import torch; print(torch.__version__)"` 正常
- [ ] `python -c "import torch; import torchvision; import torchaudio"` 三件套均导入成功
- [ ] `python -c "import onnxruntime as ort; print(ort.get_available_providers())"` 显示CUDAExecutionProvider（GPU版本）
- [ ] conda环境pytorch在 `/opt/conda/envs/pytorch/`
- [ ] GPU模式下`docker run --gpus all`后torch.cuda.is_available()为True
- [ ] entrypoint.sh语法正确（bash -n检查通过）
- [ ] Python来自 `/opt/conda/envs/pytorch/bin/python`
