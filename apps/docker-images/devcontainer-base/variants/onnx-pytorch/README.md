# DevContainer Base - ONNX-PyTorch 变体 (深度学习运行时)

> 基于 devcontainer-base:conda-llvm 变体的 ONNX + PyTorch CPU 深度学习运行时镜像，在保留所有基础功能（含 LLVM/Clang 工具链）的前提下，于 conda base 环境预装 PyTorch CPU 版、torchvision 以及完整 ONNX 生态（onnx, onnxruntime, onnx-simplifier, onnxoptimizer），开箱即用。

## ✨ 特性

- **基础镜像继承**：完全继承 conda-llvm 变体和 devcontainer-base 的所有功能
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户 (UID 1000)
  - Miniconda3 安装在 `/opt/conda`
  - LLVM/Clang 22.1.8 + CMake + Ninja + Make 编译工具链
- **PyTorch CPU**：CPU 版 PyTorch（通过 CPU 专用 wheel 索引安装，不含 CUDA，体积小）
- **torchvision**：图像处理与预训练模型库
- **ONNX 生态**：onnx（模型互操作格式）、onnxruntime（推理引擎）、onnx-simplifier（模型精简）、onnxoptimizer（图优化）
- **PATH 设计**：`/opt/conda/bin` 在 PATH 最前面，python/pip/torch/onnx 直接可用
- **开箱即用**：无需手动激活 conda，所有深度学习组件直接在 PATH 中
- **服务稳定**：Jupyter 等服务由 supervisord 用绝对路径启动，不受 PATH 变更影响
- **国内镜像支持**：支持清华 TUNA conda 镜像、阿里云/清华 pip 镜像、清华 PyTorch wheels 镜像

## 📦 包含组件

| 组件 | 版本 | 说明 |
|------|------|------|
| PyTorch | CPU latest | CPU 版深度学习框架（不含 CUDA） |
| torchvision | 与 torch 匹配 | 图像处理 + 预训练模型 |
| ONNX | latest | 开放神经网络交换格式 |
| ONNX Runtime | latest | 跨平台推理引擎（CPU provider） |
| onnx-simplifier | latest | ONNX 模型精简工具 |
| onnxoptimizer | latest | ONNX 图优化工具 |
| onnxscript | latest | ONNX Script（用 Python 编写 ONNX 算子） |
| LLVM | 22.1.8 | 继承自 conda-llvm 变体 |
| Clang | 22.1.8 | 继承自 conda-llvm 变体 |
| CMake / Ninja / Make | latest | 继承自 conda-llvm 变体 |

## 📁 目录结构

```
variants/onnx-pytorch/
├── Dockerfile              # ONNX-PyTorch 变体构建文件（4个追加阶段）
├── .env.example            # 构建参数配置模板
├── README.md               # 本文件
├── AGENTS.md               # AI 协作者入口（变体级路由）
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

需要先构建基础镜像、conda 变体和 conda-llvm 变体：

```bash
# 在 devcontainer-base 根目录
cd /path/to/devcontainer-base

# 1. 构建基础镜像
bash scripts/build.sh --cn

# 2. 构建 conda 变体
bash variants/build.sh --variant conda --cn

# 3. 构建 conda-llvm 变体
bash variants/build.sh --variant conda-llvm --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant onnx-pytorch

# 使用国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant onnx-pytorch --cn

# 构建后验证
bash variants/build.sh --variant onnx-pytorch --cn --verify
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建
docker build -f variants/onnx-pytorch/Dockerfile \
  -t devcontainer-base:onnx-pytorch-latest .

# 国内镜像源构建
docker build -f variants/onnx-pytorch/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=aliyun \
  -t devcontainer-base:onnx-pytorch-latest .
```

## 🐳 运行

### DinD 模式（推荐开发环境）

```bash
docker run -d \
  --name devcontainer-onnx-pytorch \
  --privileged \
  -p 2222:22 \
  -p 2375:2375 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  devcontainer-base:onnx-pytorch-latest
```

### 命令模式（调试/一次性推理任务）

```bash
# 进入容器交互模式
docker run -it --rm --privileged devcontainer-base:onnx-pytorch-latest bash

# 直接在容器内运行 Python 深度学习脚本
docker run --rm -v $(pwd):/workspace -w /workspace \
  devcontainer-base:onnx-pytorch-latest \
  python train.py
```

## 🔧 工具使用说明

### PATH 优先级说明

**onnx-pytorch 变体中，`/opt/conda/bin` 在 PATH 最前面**，因此：
- `python` 和 `pip` 默认指向 conda base 环境的 Python（PyTorch/ONNX 所在环境）
- `torch`, `onnx`, `onnxruntime` 可直接 import，无需激活环境
- **Jupyter 服务不受影响**：由 supervisord 使用 main 环境 `/opt/conda/envs/main/bin/jupyter` 独立启动，与 base torch 环境解耦（`/opt/venv` 已在基础镜像中移除）

### 验证导入

```bash
# 一键验证所有深度学习组件
python -c "import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)"

# 确认是 CPU 版
python -c "import torch;print(torch.cuda.is_available())"   # 期望输出: False
```

### PyTorch + ONNX 工作流示例

```bash
# 训练/推理 + 导出 ONNX + onnxruntime 推理
python - << 'EOF'
import torch, onnxruntime, numpy as np

# torch 张量运算
a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print("torch add:", (a + a).tolist())

# torch 导出 ONNX
class Net(torch.nn.Module):
    def forward(self, x):
        return x * 2 + 1
torch.onnx.export(Net(), torch.randn(1, 3), "/tmp/net.onnx", opset_version=13)

# onnxruntime 推理
sess = onnxruntime.InferenceSession("/tmp/net.onnx")
out = sess.run(None, {"input": np.random.randn(1, 3).astype("float32")})
print("onnxruntime out:", out[0].tolist())
EOF
```

### 模型精简与优化

```bash
# 使用 onnx-simplifier 精简模型
python -m onnxsim /tmp/net.onnx /tmp/net-simplified.onnx

# 使用 onnxoptimizer 优化图
python -c "import onnxoptimizer; print('onnxoptimizer ready')"
```

## ✅ 验证命令

```bash
# 验证 PyTorch 版本
docker run --rm devcontainer-base:onnx-pytorch-latest \
  /opt/conda/bin/python -c "import torch;print(torch.__version__)"

# 验证 ONNX Runtime 版本
docker run --rm devcontainer-base:onnx-pytorch-latest \
  /opt/conda/bin/python -c "import onnxruntime;print(onnxruntime.__version__)"

# 验证 CPU 版（CUDA 不可用）
docker run --rm devcontainer-base:onnx-pytorch-latest \
  /opt/conda/bin/python -c "import torch;print(torch.cuda.is_available())"
# 期望输出: False

# 验证 Jupyter 服务仍可用（main 环境）
docker run --rm devcontainer-base:onnx-pytorch-latest /opt/conda/envs/main/bin/jupyter --version

# 验证 Docker 可用
docker run --rm --privileged devcontainer-base:onnx-pytorch-latest docker --version

# 查看构建信息
docker run --rm devcontainer-base:onnx-pytorch-latest cat /etc/devcontainer-variant-onnx-pytorch-build-info
```

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | conda-llvm 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna（清华）/official（官方） |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun（阿里云）/tuna（清华）/official |
| `TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cpu` | PyTorch CPU 版 wheel 索引 |

## 📋 关键路径

| 路径 | 说明 |
|------|------|
| `/opt/conda/bin` | Conda base 环境 bin 目录（在 PATH 最前，torch/onnx 所在） |
| `/opt/conda` | Miniconda3 安装根目录 |
| `/etc/profile.d/conda-init.sh` | 原始 conda 激活脚本（不自动激活） |
| `/etc/profile.d/onnx-pytorch-init.sh` | ONNX-PyTorch 备选激活脚本 |
| `/etc/devcontainer-variant-onnx-pytorch-build-info` | 构建元数据 |

## ⚠️ 注意事项

1. **PATH 优先级**：onnx-pytorch 变体中 `/opt/conda/bin` 在 PATH 最前面，默认 `python` 是 conda base 环境的 Python（PyTorch/ONNX 所在环境）。

2. **服务不受影响**：Jupyter、SSH、Docker 等服务由 supervisord 启动，不受 PATH 顺序变更影响（Jupyter 由 supervisord 以 main 环境绝对路径启动）。

3. **CPU 版 PyTorch**：本变体安装的是 CPU 版 PyTorch（`torch.cuda.is_available() == False`），不含 CUDA 支持。如需 GPU 推理请另行构建 CUDA 变体。

4. **base 环境安装**：所有深度学习组件直接安装在 conda base 环境中，没有创建新环境。如需隔离环境，可以自行 `conda create -n myenv`。

5. **下载缓存**：Dockerfile 使用 BuildKit cache 挂载 `/opt/conda/pkgs`，重复构建时可大幅加速下载和安装。

6. **网络注意**：PyTorch CPU 版默认从 `https://download.pytorch.org/whl/cpu` 下载，若该源不可达，请在 `.env` 中设置 `TORCH_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cpu`。

## 🔗 相关镜像

- [devcontainer-base](../../README.md) - 基础镜像（SSH + Docker + Podman + Jupyter）
- [conda variant](../conda/README.md) - Conda 基础变体（Miniconda3，venv 优先）
- [conda-llvm variant](../conda-llvm/README.md) - LLVM/Clang 工具链变体（本变体的基础）
- [onnx-dev variant](../onnx-dev/README.md) - 纯 ONNX 生态变体（main 环境 free-threading，无 PyTorch，架构对偶）
- [onnx-quantized variant](../onnx-quantized/README.md) - ONNX 量化工具链变体（torch 导出模型的量化下游）

## 📄 相关文档

- [Dockerfile 规范](./.agents/rules/dockerfile.md) - 本变体 Dockerfile 规范说明
