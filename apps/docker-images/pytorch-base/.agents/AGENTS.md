---
id: "pytorch-base-agents"
title: "pytorch-base 镜像开发规范"
module_type: "docker-image"
version: "3.0"
last_updated: "2026-04-15"
source: "apps/docker-images/AGENTS.md#应用路由表"
---
# pytorch-base 镜像开发规范

<a id="模块定位"></a>
## 模块定位

PyTorch GPU/CPU 基础镜像，基于 Ubuntu 26.04 + Miniforge3（conda-forge native + libmamba solver）+ Python 3.14.6 + PyTorch 2.13.0，默认构建 **GPU 版本**（CUDA 12.6），包含 PyTorch 三件套（torch + torchvision + torchaudio）和 ONNX Runtime GPU 支持。可作为其他 AI 项目的基础镜像，也可直接用于训练和推理。

<a id="版本信息"></a>
## 版本信息（v3.0）

| 组件 | 版本 | 说明 |
|------|------|------|
| 基础镜像 | ubuntu:26.04 | 固定版本 |
| Conda 发行版 | Miniforge3 | conda-forge native + libmamba solver |
| Python | 3.14.6（GIL-enabled） | 精确 patch 版本 |
| PyTorch | 2.13.0（默认CUDA 12.6） | 支持 CUDA 12.6/12.8/13.0 |
| torchvision | 自动匹配 PyTorch 版本 | 官方三件套 |
| torchaudio | 自动匹配 PyTorch 版本 | 官方三件套 |
| ONNX Runtime | 1.27.0+gpu（GPU版）/ CPU版 | 含 CUDAExecutionProvider |
| CUDA toolkit | pip wheel 内置（nvidia-cuda-runtime-cu12等） | 无需完整 CUDA toolkit |

<a id="入口规范"></a>
## 入口规范

AI 智能体处理 pytorch-base 镜像相关任务时必须遵守：

1. **必读规范**：先阅读 [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) 了解Dockerfile多阶段构建规范
2. **必读规范**：再阅读 [.agents/rules/build.md](.agents/rules/build.md) 了解构建流程规范
3. **参考文档**：参考 [README.md](README.md) 了解使用方法
4. **镜像层逻辑**：构建7阶段按Runtime Logical Layering v1.3组织（系统包→Miniforge→镜像源→PyTorch三件套+ORT→非root用户→entrypoint→验证清理）
5. **默认GPU优先**：默认构建GPU版本，CPU版本需显式 `--cpu` 参数
6. **Miniforge3替代Miniconda3**：v3.0起使用Miniforge3（conda-forge native），不再使用Miniconda3
7. **完整三件套**：v3.0起默认安装torch+torchvision+torchaudio三件套和onnxruntime-gpu
8. **日志规范**：构建日志使用英文，遵循结构化前缀规范（[STAGE]/[ACTION]/[OK]/[WARN]/[ERROR]/[TIMER]/[VALIDATE]）
9. **国内镜像支持**：通过构建参数支持国内镜像源（conda: BFSU/TUNA/official，pip: aliyun/tuna/official）
10. **离线构建支持**：通过 `--prepare-offline` 和 `--offline` 参数支持离线构建

<a id="项目特有约束"></a>
## 项目特有约束

- 基础镜像固定为 ubuntu:26.04，不使用 cuda base镜像（通过pip wheel获取CUDA运行时库）
- Dockerfile必须严格遵循7阶段结构（详见dockerfile.md），不得随意合并或拆分阶段
- 使用 BuildKit `--mount=type=cache` 优化构建速度（apt/conda/pip缓存）
- 默认构建GPU版本，CPU版本通过构建参数切换
- 默认启用非root用户 `ai`（UID 1000），通过gosu在entrypoint中自动切换
- conda环境固定为 `pytorch`，安装路径 `/opt/conda/envs/pytorch/`
- 必须包含中文环境配置（UTF-8 locale + Asia/Shanghai时区）
- pip作为主要PyTorch安装方式，conda作为最终fallback
- PyTorch安装使用4级fallback：本地wheel→PyTorch官方索引→pip镜像→conda
- 必须包含完整的构建后验证（import检查、CUDA版本一致性、ORT providers、tensor运算等）
- Stage 7必须做激进清理（__pycache__、*.pyc、conda tar.bz2缓存、文档等）
- Stage 7必须输出构建耗时汇总表
- 所有离线资源存放在 `offline/` 目录（始终包含在构建上下文中）
- Miniforge3下载支持三镜像fallback：BFSU→TUNA→GitHub官方
- 必须支持无GPU环境下的构建（构建时不依赖GPU，torch.cuda.is_available()=False视为正常）

<a id="文件结构"></a>
## 文件结构

```
pytorch-base/
├── Dockerfile              # 7阶段多阶段构建Dockerfile（v3.0: Miniforge3+Python3.14.6+GPU默认+三件套+ORT-GPU）
├── build.sh                # 智能构建脚本（含日志、计时、多架构检测、镜像源切换、离线构建）
├── entrypoint.sh           # 容器入口脚本（conda环境激活+非root用户切换+GPU信息banner）
├── profile.d/              # Shell初始化脚本
│   └── conda-init.sh       # conda自动激活脚本
├── offline/                # 离线构建资源（始终包含在构建上下文中）
│   ├── miniforge/          # Miniforge安装脚本（gitkeep占位）
│   ├── wheels/             # pip wheel包缓存（gitkeep占位）
│   └── conda-pkgs/         # conda包缓存（gitkeep占位）
├── .agents/                # AI智能体规范
│   ├── AGENTS.md           # 本文件
│   └── rules/              # 开发规则
│       ├── dockerfile.md   # Dockerfile多阶段构建规范
│       └── build.md        # 构建流程规范
└── README.md               # 使用说明文档
```

<a id="快速开始"></a>
## 快速开始

```bash
# 默认构建GPU版本（CUDA 12.6，国内镜像源）
cd apps/docker-images/pytorch-base
bash build.sh

# 构建CPU版本
bash build.sh --cpu

# 准备离线资源（含Miniforge3、torch三件套、onnxruntime-gpu）
bash build.sh --prepare-offline

# 离线构建
bash build.sh --offline

# 指定CUDA版本（支持12.6/12.8/13.0）
bash build.sh --cuda 13.0

# 构建完成后运行
docker run --gpus all -it --rm xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu
```

<a id="相关文档索引"></a>
## 相关文档索引

| 文档 | 路径 | 说明 |
|------|------|------|
| Dockerfile构建规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 7阶段构建规范、缓存优化、离线支持、安全规范 |
| 构建流程规范 | [.agents/rules/build.md](.agents/rules/build.md) | build.sh参数、离线构建、多架构支持、验证流程 |
| 使用说明 | [README.md](README.md) | 用户指南、常见问题、命令参考 |
| 全局应用规范 | [../../AGENTS.md](../../AGENTS.md) | apps区域入口路由 |
| 全局开发规范 | [.agents/docs/development-standards.md](.agents/docs/development-standards.md) | 代码风格、提交规范、文档规范 |

<a id="变更历史"></a>
## 变更历史

### v3.0（2026-04-15）

- **重大变更**：默认构建GPU版本（CUDA 12.6），从CPU-only变为GPU优先
- **重大变更**：从 Miniconda3 切换到 Miniforge3（conda-forge native + libmamba solver）
- Python 版本升级到 3.14.6（精确 patch 版本，GIL-enabled）
- PyTorch 版本升级到 2.13.0
- **新增**：默认安装完整三件套（torch+torchvision+torchaudio）
- **新增**：默认安装 onnxruntime-gpu（GPU 版，含 CUDAExecutionProvider）
- **新增**：CUDA 运行时库通过 pip wheel 安装（nvidia-cuda-runtime-cu12 等），无需完整 CUDA toolkit
- **新增**：支持 CUDA 12.6/12.8/13.0 三版本切换
- **新增**：Stage 7 GPU 综合验证（CUDA版本一致性、CUDA库存在性、ORT providers、tensor运算）
- **增强**：banner 显示 GPU 设备列表、显存大小、ONNX Runtime 信息
- **优化**：Miniforge3 下载三镜像 fallback（BFSU→TUNA→GitHub官方）
- **优化**：PyTorch 安装四级 fallback（本地wheel→PyTorch官方→pip镜像→conda）
- **修复**：LD_LIBRARY_PATH 加入 torch.lib 路径（防止 libnvToolsExt 找不到）

### v2.6（2026-04-15）

- 修复 execstack 缺失问题（stage 7增加conditional install）
- 增强 conda 清理（增加 tar.bz2 缓存清理）
- Python 3.13.5 精确版本
- 增加 --list-offline 命令
- 修复 /etc/profile.d/conda.sh 路径问题

### v2.5（2026-04-15）

- PyTorch 升级到 2.5.1，支持 Python 3.13
- Python 版本升级到 3.13.3
- CUDA 12.4/12.6/12.8 支持
- 安装 torchvision（匹配 PyTorch 版本）
- CUDA 库通过本地wheel安装（nvidia-cuda-runtime-cu124等）
- conda libmamba solver默认启用（提升构建速度）
- 镜像标签增加cuda版本后缀（如2.5.1-cpu-py3.13, 2.5.1-cuda12.6-py3.13）
- Python路径验证增强（严格匹配路径）
