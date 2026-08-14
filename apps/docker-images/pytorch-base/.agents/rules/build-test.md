---
id: "pytorch-build-test-rules"
title: "构建与测试流程"
source: "AGENTS.md#构建命令速查"
---
# 构建与测试流程（pytorch-base）

## 构建命令速查

```bash
# 在线构建（默认，从国内镜像源下载包）
./build.sh

# 指定PyTorch版本和Python版本
./build.sh --torch-version 2.5.1 --python-version 3.14

# GPU版本（CUDA 12.6，需要nvidia-docker2）
./build.sh --gpu

# 自定义镜像标签
./build.sh --tag my-pytorch:latest

# 无缓存构建（用于调试）
./build.sh --no-cache

# 离线构建（使用offline/目录中的本地包）
./build.sh --offline

# 第一步：准备离线资源（在有网络的机器上执行）
./build.sh --prepare-offline
# 第二步：离线构建（offline/中有缓存后，可无网络构建）
./build.sh --offline

# 跳过验证（不推荐）
./build.sh --no-verify
```

## 运行与验证

```bash
# 验证PyTorch导入
docker run --rm pytorch-base:2.13.0-py3.14-cpu python -c "import torch; print(torch.__version__)"

# 交互式shell
docker run -it --rm pytorch-base:2.13.0-py3.14-cpu

# GPU模式运行（需要nvidia-docker2和--gpus参数）
docker run --rm --gpus all pytorch-base:2.13.0-py3.14-cuda12.6 python -c "import torch; print(torch.cuda.is_available())"

# 作为基础镜像被其他Dockerfile引用
FROM pytorch-base:2.13.0-py3.14-cpu
```

## 构建脚本（build.sh）功能

- **彩色输出**：INFO/OK/WARN/ERROR分级日志
- **构建计时**：总耗时+各阶段耗时
- **自动标签**：`pytorch-base:<torch_version>-py<python_version>-<cpu|cuda>`
- **国内镜像源**：自动检测网络环境，配置apt/conda/pip国内源
- **离线资源管理**：`--prepare-offline`自动下载Miniconda安装包、pip wheels、conda包缓存
- **13项自动验证**：构建完成后自动运行验证脚本（Python版本、PyTorch导入、CUDA可用性、conda环境等）
- **BuildKit支持**：自动检测并启用BuildKit缓存挂载
- **PowerShell兼容**：`build.ps1`提供同等功能

## 离线资源管理

`offline/` 目录结构（始终包含在构建上下文中，空目录仅含.gitkeep不影响构建速度）：

```
offline/
├── miniconda/      ← Miniconda3-latest-Linux-x86_64.sh
├── wheels/         ← pip wheel包（torch/torchvision等）
└── conda-pkgs/     ← conda包缓存tar.bz2文件
```

离线构建逻辑：Dockerfile通过COPY+shell条件检测，offline/中有文件时使用本地安装，否则从网络下载。

## 验证清单（13项）

build.sh构建成功后自动执行：

1. Python版本正确（与PYTHON_VERSION一致）
2. Python来自conda环境路径（`/opt/conda/envs/pytorch/bin/python`）
3. PyTorch可导入
4. PyTorch版本正确（与PYTORCH_VERSION一致）
5. CPU模式：torch.cuda.is_available()为False
6. GPU模式：torch.cuda.is_available()为True，设备数>0
7. conda命令可用
8. conda环境pytorch存在
9. conda环境自动激活（bash -l后python路径正确）
10. locale为zh_CN.UTF-8
11. 时区为Asia/Shanghai
12. ai用户存在（uid=1000）
13. ai用户可sudo

## Dockerfile语法检查

```powershell
# 使用项目根目录的自动化测试脚本
powershell -ExecutionPolicy Bypass -File ../../.agents/scripts/test-dockerfiles.ps1 -File Dockerfile
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| conda安装超时 | 查看构建日志Stage 2 | 网络不稳定，使用--prepare-offline准备离线包 |
| PyTorch安装失败 | 查看Stage 4日志 | 镜像源问题，尝试--gpu或指定版本 |
| CUDA不可用 | `docker run --rm --gpus all <img> nvidia-smi` | 未安装nvidia-docker2或未加--gpus参数 |
| Python不是conda环境的 | `docker run --rm <img> which python` | PATH设置错误，检查entrypoint.sh |
| 离线构建找不到包 | `ls -la offline/miniconda/ offline/wheels/` | 未执行--prepare-offline或文件不完整 |
| ai用户无法sudo | `docker run --rm <img> su - ai -c "sudo -n whoami"` | sudoers配置未生效 |

## .dockerignore

排除非构建文件：`.git/`、`.trae/`、`.agents/`、`specs/`、`__pycache__/`、`*.pyc`等。
注意：`offline/`目录**必须**包含在构建上下文中（不加入.dockerignore）。
