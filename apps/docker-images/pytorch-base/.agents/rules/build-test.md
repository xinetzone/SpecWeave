---
id: "pytorch-build-test-rules"
title: "构建与测试流程"
source: "AGENTS.md#构建命令速查"
---
# 构建与测试流程（pytorch-base v3.0）

## 构建命令速查

```bash
# 默认构建GPU版本（CUDA 12.6，国内镜像源，Miniforge3 + Python 3.14.6）
./build.sh

# 构建CPU版本
./build.sh --cpu

# 指定CUDA版本（支持12.6/12.8/13.0）
./build.sh --cuda 13.0

# 指定PyTorch版本和Python版本
./build.sh --torch-version 2.13.0 --python-version 3.14.6

# 自定义镜像标签
./build.sh --tag my-pytorch:latest

# 无缓存构建（用于调试）
./build.sh --no-cache

# 安静模式（减少日志输出）
./build.sh --quiet

# 第一步：准备离线资源（在有网络的机器上执行，含Miniforge3 + 三件套 + ORT-GPU）
./build.sh --prepare-offline

# 第二步：离线构建（offline/中有缓存后，可无网络构建）
./build.sh --offline

# 列出离线资源状态
./build.sh --list-offline

# 跳过验证（不推荐）
./build.sh --no-verify
```

## 运行与验证

```bash
# 验证PyTorch三件套导入
docker run --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu \
  python -c "import torch; import torchvision; import torchaudio; print(f'PyTorch {torch.__version__}, CUDA {torch.cuda.is_available()}')"

# 验证ONNX Runtime GPU
docker run --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu \
  python -c "import onnxruntime as ort; print(ort.get_available_providers())"

# 交互式shell（自动显示GPU信息banner）
docker run -it --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu

# CPU版本运行（无需--gpus）
docker run -it --rm xinetzone/pytorch:2.13.0-cpu-py3.14.6

# 快速GPU tensor运算测试
docker run --rm --gpus all xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu \
  python -c "import torch; x=torch.randn(1000,1000,device='cuda'); print((x@x.T).sum())"

# 作为基础镜像被其他Dockerfile引用
FROM xinetzone/pytorch:2.13.0-cuda12.6-py3.14.6-gpu
```

## 构建脚本（build.sh）功能

- **彩色结构化输出**：INFO/OK/WARN/ERROR分级日志，[STAGE]/[ACTION]/[TIMER]/[VALIDATE]前缀
- **构建计时**：总耗时+各阶段耗时，最终输出汇总表
- **自动标签生成**：`xinetzone/pytorch:<version>-cuda<cuda>-py<py>-<gpu|cpu>`
- **默认GPU版本**：CUDA 12.6为默认构建目标，CPU需显式`--cpu`
- **Miniforge3下载**：三镜像fallback（BFSU→TUNA→GitHub官方）
- **国内镜像源**：conda默认BFSU，pip默认阿里云，均支持fallback切换
- **离线资源管理**：`--prepare-offline`自动下载Miniforge3、torch三件套、onnxruntime-gpu wheels
- **自动验证**：构建完成后自动运行综合验证
- **BuildKit支持**：自动检测并启用BuildKit缓存挂载
- **多CUDA版本**：通过`--cuda`切换12.6/12.8/13.0
- **PowerShell兼容**：`build.ps1`提供同等功能（Windows环境）

## 离线资源管理

`offline/` 目录结构（始终包含在构建上下文中，空目录仅含.gitkeep不影响构建速度）：

```
offline/
├── miniforge/      ← Miniforge3-Linux-x86_64.sh（v3.0起替代miniconda/）
├── wheels/         ← pip wheel包（torch/torchvision/torchaudio/onnxruntime-gpu等）
└── conda-pkgs/     ← conda包缓存tar.bz2文件
```

离线构建逻辑：Dockerfile通过COPY+shell条件检测，offline/中有文件时使用本地安装，否则从网络下载。
四级fallback安装链：本地wheel → PyTorch官方索引 → pip国内镜像 → conda。

## 验证清单（构建后自动执行）

build.sh构建成功后自动执行综合验证：

### 基础验证（CPU/GPU通用）
1. Python版本正确（与PYTHON_VERSION一致）
2. Python来自conda环境路径（`/opt/conda/envs/pytorch/bin/python`）
3. PyTorch三件套均可导入（torch + torchvision + torchaudio）
4. PyTorch版本正确（与PYTORCH_VERSION一致）
5. torchvision/torchaudio版本与torch匹配
6. numpy可导入
7. conda命令可用，环境pytorch存在
8. conda环境自动激活（bash -l后python路径正确）
9. locale为zh_CN.UTF-8
10. 时区为Asia/Shanghai
11. ai用户存在（uid=1000），可sudo
12. tini和gosu可用
13. tensor基本运算正常

### GPU附加验证（构建USE_GPU=1时）
14. CUDA版本一致性（torch.version.cuda与CUDA_VERSION匹配）
15. CUDA运行时库存在（libcudart/libcublas/libcudnn等）
16. ONNX Runtime可导入，版本匹配
17. **注意**：无GPU时`torch.cuda.is_available()=False`视为正常（仅警告），有GPU时强制验证为True

### Entrypoint验证
18. entrypoint.sh bash语法正确（bash -n）
19. entrypoint banner正常显示

## Dockerfile语法检查

```bash
# 本地bash语法检查（无需Docker）
bash -n Dockerfile
bash -n build.sh
bash -n entrypoint.sh
bash -n profile.d/conda-init.sh
```

## 宿主机前置要求（GPU版本）

| 组件 | 最低版本 | 安装命令参考 |
|------|---------|-------------|
| NVIDIA驱动 | ≥ 525.60.13（CUDA 12.x）；≥ 570（CUDA 13.0） | Ubuntu: `sudo ubuntu-drivers autoinstall` |
| Docker Engine | ≥ 20.10 | 官方Docker CE |
| NVIDIA Container Toolkit | ≥ 1.13 | `nvidia-ctk --version`验证 |
| BuildKit | 启用（默认DOCKER_BUILDKIT=1） | Docker 23.0+默认启用 |

验证宿主机GPU支持：
```bash
nvidia-smi  # 应显示GPU列表和驱动版本
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi  # 容器内也能看到GPU
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| Miniforge安装超时 | 查看Stage 2日志 | 网络不稳定，使用`--prepare-offline`提前下载 |
| PyTorch安装失败 | 查看Stage 4日志 | 镜像源问题，尝试`--torch-version`指定或`--cuda`切换 |
| ONNX Runtime导入失败 | `docker run --rm <img> python -c "import onnxruntime"` | CUDA版本不匹配，检查ORT与CUDA版本兼容性 |
| CUDA不可用（运行时） | `docker run --rm --gpus all <img> nvidia-smi` | 未安装nvidia-container-toolkit或未加`--gpus all`参数 |
| Python不是conda环境的 | `docker run --rm <img> which python` | PATH设置错误，检查entrypoint.sh和Dockerfile ENV |
| 离线构建找不到包 | `ls -la offline/miniforge/ offline/wheels/` | 未执行`--prepare-offline`或文件不完整 |
| ai用户无法sudo | `docker run --rm <img> gosu ai sudo -n whoami` | sudoers配置未生效 |
| LD_LIBRARY_PATH错误 | `docker run --rm <img> echo $LD_LIBRARY_PATH` | torch/lib路径未正确设置，检查Dockerfile ENV |
| CUDA 13.0找不到镜像 | 检查是否使用pip wheel方式 | 需使用PyTorch nightly或2.13+正式版，通过pip安装CUDA库 |

## .dockerignore

排除非构建文件：`.git/`、`.trae/`、`.agents/`、`specs/`、`__pycache__/`、`*.pyc`等。
注意：`offline/`目录**必须**包含在构建上下文中（不加入.dockerignore）。
