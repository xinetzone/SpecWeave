# torch-dev 变体 - Free-Threading PyTorch 开发环境 v1.0.0

> **发布日期**: 2026-08-15 | **状态**: ✅ 正式发布 | **Python**: 3.14.6 cp314t free-threading
>
> **可用标签**: `torch-dev-latest`（完整版 ~10GB）| **`torch-dev-slim`**（瘦身版 **8.15GB**，推荐）→ 详见 [SLIMMING-GUIDE.md](./SLIMMING-GUIDE.md)

Free-Threading PyTorch 开发环境变体，在 conda main 环境（cp314t，GIL 禁用）安装 PyTorch + torchvision，支持无 GIL 并发计算。是 ai-dev 变体（完整 AI/ML/NLP 全栈）的直接基础镜像。

**与 onnx-pytorch 的定位差异**：
- `onnx-pytorch`: PyTorch 安装在 conda **base** 环境（Python 3.13.x，**GIL 启用**）—— 传统 GIL 绑定工作负载
- `torch-dev`: PyTorch 安装在 conda **main** 环境（Python 3.14.6t，**free-threading，GIL 禁用**）—— 无 GIL 并发工作负载
- 两者为平行变体，互不依赖。

---

## 📦 版本信息

| 组件 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.14.6 (cp314t) | **free-threading 构建**（main 环境，GIL 禁用） |
| **PyTorch** | 2.13.0+cu130 | Free-threading 兼容构建（CUDA 13.0 索引） |
| **torchvision** | 0.28.0+cu130 | 与 torch 匹配的视觉库 |
| **ONNX** | 1.22.0 | 继承自 onnx-quantized |
| **ONNX Runtime** | 1.28.0 | 继承自 onnx-quantized（含 quantization 模块） |
| **ONNX Simplifier** | v0.7.3 | 继承自 onnx-quantized |
| **ONNX Converter Common** | 1.16.0 | 继承自 onnx-quantized |
| **LLVM/Clang** | 22.1.8 | 继承自 conda-llvm |
| ~~onnxoptimizer~~ | **排除** | free-threading 不兼容（CPython #111506），继承 onnx-quantized 排除策略 |

---

## ✅ 验证结果

本地 WSL2 Docker 环境部署验证结果（v1.0.0，构建后运行 `test-torch-dev.sh` 24 项测试）：

| 测试项 | 结果 | 详情 |
|--------|------|------|
| **free-threading 验证** | ✅ PASS | cp314t，GIL 禁用（`sys._is_gil_enabled() is False`） |
| **torch/torchvision 导入** | ✅ PASS | main 环境，cp314t manylinux wheel |
| **核心算子正确性** | ✅ PASS | matmul/conv2d/autograd/softmax/MLP forward 全部正确 |
| **ONNX 量化栈继承** | ✅ PASS | onnxruntime.quantization 正常可用 |
| **triton GIL 警告** | ⚠️ WARN | triton 加载时临时启用 GIL（预期行为，不影响纯 CPU 算子） |
| **基础服务继承** | ✅ PASS | SSH/Docker DinD/Podman/Jupyter/Supervisord |
| **devuser 权限** | ✅ PASS | devuser 可正常导入 torch |

**汇总**: 24 项测试（L1 free-threading/版本验证 + L2 PyTorch 导入 + L3 核心算子冒烟 + L4 服务继承 + L5 PATH 优先级 + L6 build-info + L7 ONNX 互操作）

---

## 🚀 部署步骤

### 方式一：本地一键构建（推荐用于开发）

```bash
cd apps/docker-images/devcontainer-base

# 使用本地一键构建脚本（自动处理WSL2路径映射）
bash scripts/local-build.sh --variant torch-dev

# 国内镜像加速（构建 slim 瘦身版，推荐）
bash scripts/local-build.sh --variant torch-dev --cn --tag slim
```

### 方式二：Docker 直接构建

```bash
cd apps/docker-images/devcontainer-base

# 按依赖链构建（需先构建 base→conda-llvm→onnx-dev→onnx-quantized）
bash variants/build.sh --variant torch-dev --tag latest

# 构建 slim 瘦身版（推荐，节省 2GB+）
bash variants/build.sh --variant torch-dev --tag slim

# 国内源（slim 版）
bash variants/build.sh --variant torch-dev --tag slim --cn
```

### 方式三：启动容器

#### 模式A：默认模式（本地workspace挂载，向后兼容）

```bash
# CPU 模式（默认，使用 slim 瘦身版）
docker run -d --privileged \
  --name torch-dev \
  -p 2222:22 \
  -p 8888:8888 \
  -p 2375:2375 \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=devtoken \
  -e GRANT_SUDO=yes \
  -v $(pwd)/workspace:/workspace \
  -w /workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:torch-dev-slim

# GPU 模式（添加 --gpus all，详见下方「启用GPU支持」章节）
# docker run -d --privileged --gpus all \
#   --name torch-dev \
#   -p 2222:22 \
#   -p 8888:8888 \
#   -p 2375:2375 \
#   -e USER_PASSWORD=devpass \
#   -e JUPYTER_TOKEN=devtoken \
#   -e GRANT_SUDO=yes \
#   -v $(pwd)/workspace:/workspace \
#   -w /workspace \
#   -v docker-data:/var/lib/docker \
#   devcontainer-base:torch-dev-slim
```

#### 模式B：自定义数据目录模式（推荐用于数据集/模型挂载）

适用于数据集、预训练模型等大文件存储在宿主机独立分区的场景：

```bash
# 1. 定义数据挂载路径（根据实际环境修改）
# Linux 原生示例：
MOUNT=/media/pc/data/ai
# WSL2 示例（Windows D盘）：
# MOUNT=/mnt/d/ai-data
# macOS 示例：
# MOUNT=/Users/yourname/data/ai

# 2. 确保宿主机目录存在
mkdir -p "$MOUNT"

# 3. 启动容器（自动挂载数据目录并设置为工作目录）
# CPU 模式（默认，slim 版）
docker run -d -it --privileged \
  --name torch-dev \
  -p 2222:22 \
  -p 8888:8888 \
  -p 2375:2375 \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=devtoken \
  -e GRANT_SUDO=yes \
  -w "$MOUNT" \
  -v "$MOUNT:$MOUNT" \
  -v $(pwd)/workspace:/workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:torch-dev-slim

# GPU 模式（添加 --gpus all，详见下方「启用GPU支持」章节）
# docker run -d -it --privileged --gpus all \
#   --name torch-dev \
#   -p 2222:22 \
#   -p 8888:8888 \
#   -p 2375:2375 \
#   -e USER_PASSWORD=devpass \
#   -e JUPYTER_TOKEN=devtoken \
#   -e GRANT_SUDO=yes \
#   -w "$MOUNT" \
#   -v "$MOUNT:$MOUNT" \
#   -v $(pwd)/workspace:/workspace \
#   -v docker-data:/var/lib/docker \
#   devcontainer-base:torch-dev-slim
```

**关键参数说明**：
| 参数 | 作用 |
|------|------|
| `-w "$MOUNT"` | 设置容器启动后的默认工作目录，登录SSH直接进入；**Jupyter Notebook/Lab根目录会自动同步到此目录**（v2.2.1+） |
| `-v "$MOUNT:$MOUNT"` | 将宿主机数据目录映射到容器内相同路径，方便跨环境脚本复用 |
| `-v $(pwd)/workspace:/workspace` | 本地代码工作区（可选，建议同时挂载） |
| `--gpus all` | （GPU模式）启用所有NVIDIA GPU透传；多卡环境可指定`--gpus '"device=0,1"'`选择特定卡 |
| `-e JUPYTER_ROOT_DIR=/custom/path` | （可选）显式指定Jupyter根目录，优先级高于`-w`自动检测 |
| `-e JUPYTER_ROOT_CHOWN=auto` | （可选）Jupyter根目录权限策略：`auto`（默认，bind mount跳过chown保护宿主机）/`yes`（强制chown，会修改宿主机文件权限）/`no`（完全跳过）/`named-only`（仅Docker命名卷chown） |

> 💡 **跨平台提示**：WSL2/Windows Docker Desktop 环境下请使用 WSL2 路径格式（如 `/mnt/d/ai-data`），避免使用Windows盘符路径（如 `D:\ai-data`）。
>
> 💡 **Jupyter根目录同步机制**：容器启动时自动检测Docker `-w`设置的工作目录作为Jupyter根目录；如果`-w`设置为`/`（根目录）或目录不存在，自动回退到`/workspace`。也可通过`JUPYTER_ROOT_DIR`环境变量显式覆盖。

> ⚠️ **权限安全重要提示（v2.2.1+安全默认）**：
> - **默认行为**：自定义挂载的数据目录（非`/workspace`）**默认跳过chown**，避免修改宿主机文件权限导致无法访问
> - `/workspace`目录保持原有行为（默认chown给devuser），保证开发工作区可用性
> - 敏感系统目录（`/`、`/home`、`/etc`等）会强制跳过chown，防止误挂载损坏宿主机系统
> - 遇到`Permission denied`时，容器启动日志会打印友好的解决方案提示框

---

## 🚀 启用GPU支持（CUDA）

PyTorch 已预编译为 `cu130`（CUDA 13.0）版本，但容器默认以CPU模式启动。启用GPU只需添加`--gpus all`参数，并确保宿主机满足前置条件。

### 前置条件

| 环境 | 要求 |
|------|------|
| **Linux 原生** | ① NVIDIA显卡驱动已安装（宿主机执行`nvidia-smi`可正常输出）<br>② 已安装 [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)<br>③ Docker daemon已配置nvidia runtime（安装toolkit后执行`sudo systemctl restart docker`）<br>④ 推荐驱动版本 ≥ 550.x（支持CUDA 13.0） |
| **WSL2 + Docker Desktop** | ① Windows宿主机已安装最新NVIDIA Game Ready/Studio驱动（WSL2自动继承，**无需在WSL内单独安装驱动**）<br>② Docker Desktop已启用WSL2后端（Settings → General → Use the WSL 2 based engine）<br>③ Docker Desktop 4.18+ 内置GPU支持，无需额外安装nvidia-container-toolkit |
| **macOS** | ❌ 不支持NVIDIA GPU透传（Apple Silicon使用MPS，本镜像暂未优化） |

### 完整GPU启动示例（自定义数据目录模式）

```bash
# 1. 定义数据挂载路径
MOUNT=/media/pc/data/ai   # Linux原生
# MOUNT=/mnt/d/ai-data    # WSL2/Windows

mkdir -p "$MOUNT"

# 2. GPU模式启动（仅增加 --gpus all 参数）
docker run -d -it --privileged --gpus all \
  --name torch-dev \
  -p 2222:22 \
  -p 8888:8888 \
  -p 2375:2375 \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=devtoken \
  -e GRANT_SUDO=yes \
  -w "$MOUNT" \
  -v "$MOUNT:$MOUNT" \
  -v $(pwd)/workspace:/workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:torch-dev-slim
```

### 多卡场景：指定GPU设备

不需要使用所有GPU时，可精确指定透传的设备：

```bash
# 仅使用第0号和第1号GPU
--gpus '"device=0,1"'

# 仅使用第0号GPU
--gpus '"device=0"'
```

> 💡 **注意引号格式**：`device=`参数需要双层引号（外层单引号、内层双引号），避免shell解析错误。

### 验证GPU是否可用

容器启动后，执行以下命令完整验证GPU状态：

```bash
docker exec -it torch-dev /opt/conda/envs/main/bin/python -c "
import sys, torch
print(f'torch {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA device count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        print(f'  GPU {i}: {torch.cuda.get_device_name(i)}')
        props = torch.cuda.get_device_properties(i)
        print(f'    VRAM: {props.total_memory / 1024**3:.1f} GB')
        print(f'    Compute Capability: {props.major}.{props.minor}')
print(f'Free-threading: GIL disabled = {not sys._is_gil_enabled()}')
"
```

**预期正常输出（GPU可用时）**：
```
torch 2.13.0+cu130
CUDA available: True
CUDA device count: <N>
  GPU 0: NVIDIA GeForce RTX 4090
    VRAM: 23.6 GB
    Compute Capability: 8.9
Free-threading: GIL disabled = True
```

> 💡 **一键快速验证命令**：见下方「🔍 快速验证」章节中的「🟢 选项2：GPU模式验证」。

### 只读数据集挂载（推荐）

对于只读的训练数据集/预训练模型，推荐使用只读挂载（`:ro`），从根本上避免权限问题和误修改：

```bash
docker run -d -it --privileged --gpus all \
  ... \
  -v /media/pc/datasets:/media/pc/datasets:ro \
  -v /media/pc/models:/media/pc/models:ro \
  ...
```

### GPU常见问题排查

| 问题现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `could not select device driver "" with capabilities: [[gpu]]` | 宿主机未正确配置nvidia-container-toolkit | **Linux**: 安装nvidia-container-toolkit后重启docker；**WSL2/Docker Desktop**: 更新Docker Desktop到最新版，确认WSL2引擎已启用 |
| 加了`--gpus all`但`torch.cuda.is_available()`仍返回`False` | ① nvidia-smi在容器内也失败<br>② 驱动版本过旧不支持CUDA 13.0 | 先执行`docker exec torch-dev nvidia-smi`验证设备透传；宿主机驱动升级到≥550.x |
| WSL2下看不到GPU | Docker Desktop WSL2集成未正确启用 | Docker Desktop → Settings → Resources → WSL Integration，确认对应发行版已启用 |
| `nvidia-smi`正常但PyTorch找不到CUDA | LD_LIBRARY_PATH环境变量问题 | 容器内执行`source /opt/conda/etc/profile.d/conda.sh && conda activate main`后再试 |

---

#### 🔍 快速验证（一次性运行，不启动服务）

容器启动后，选择对应模式验证镜像是否正常：

---

##### 🔵 选项1：CPU模式验证（默认，无需GPU）

适用于：快速检查镜像是否正常导入、PyTorch基础功能是否可用

```bash
docker run --rm devcontainer-base:torch-dev-slim \
  /opt/conda/envs/main/bin/python -c "
import sys, torch
print(f'torch {torch.__version__} ready!')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'Free-threading: GIL disabled = {not sys._is_gil_enabled()}')
"
```

**✅ 预期正常输出（CPU模式）**：
```
torch 2.13.0+cu130 ready!
CUDA available: False          ← CPU模式下这是正常的！不是错误
Free-threading: GIL disabled = True
```

> ⚠️ **重要提示**：CPU模式下 `CUDA available: False` 是**预期的正确行为**，不要误认为是配置错误！Docker默认不透传GPU，需要添加 `--gpus all` 参数（见下方GPU模式）。

---

##### 🟢 选项2：GPU模式验证（需要NVIDIA显卡 + 前置条件）

适用于：验证CUDA/GPU加速是否正常工作（需先满足[GPU前置条件](#前置条件)）

```bash
docker run --gpus all --rm devcontainer-base:torch-dev-slim \
  /opt/conda/envs/main/bin/python -c "
import sys, torch
print(f'torch {torch.__version__} ready!')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU detected: {torch.cuda.get_device_name(0)}')
    print(f'GPU VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
print(f'Free-threading: GIL disabled = {not sys._is_gil_enabled()}')
"
```

**✅ 预期正常输出（GPU模式）**：
```
torch 2.13.0+cu130 ready!
CUDA available: True           ← GPU模式下应为True
GPU detected: NVIDIA GeForce RTX XXXX
GPU VRAM: X.X GB
Free-threading: GIL disabled = True
```

---

> 🔑 **CPU/GPU命令唯一区别**：GPU模式多了 **`--gpus all`** 参数，其他完全相同。
>
> ❓ 如果GPU模式下仍显示 `CUDA available: False`，请参考上方[GPU常见问题排查](#gpu常见问题排查)。

### 访问服务

| 服务 | 地址 | 凭证 |
|------|------|------|
| **Jupyter Notebook** | http://localhost:8888 | Token: `devtoken`（或通过环境变量设置）|
| **SSH** | `ssh devuser@localhost -p 2222` | 密码: `devpass` |
| **Docker API** | tcp://localhost:2375 | - |

### CI/CD 自动构建

推送代码到 `main` 分支或创建 PR 时，GitHub Actions 会自动触发完整依赖链构建：
```
Lint → base → conda-llvm → onnx-dev → onnx-quantized → torch-dev → ai-dev
```

手动触发：
```bash
gh workflow run devcontainer-variants.yml --ref main -f variant=torch-dev
```

---

## ⚡ PyTorch free-threading 使用注意事项

### 1. GIL 状态检测

```python
import sys
import torch

print(f"GIL enabled: {sys._is_gil_enabled()}")  # 预期: False
print(f"torch version: {torch.__version__}")
```

### 2. triton 库的 GIL 临时启用

首次导入 triton 相关模块时可能看到警告：
```
The global interpreter lock (GIL) has been enabled to load module 'triton._C.libtriton'
```

这是**预期行为**：triton 暂不支持 free-threading，加载时临时启用 GIL。纯 CPU 算子不受影响，仍可享受 free-threading 并发收益。

### 3. 线程配置建议

```bash
# 容器启动时设置 OpenMP 环境变量
export OMP_NUM_THREADS=4
export OMP_WAIT_POLICY=PASSIVE
export OPENBLAS_NUM_THREADS=1
export KMP_AFFINITY=granularity=fine,compact,1,0
export KMP_BLOCKTIME=1
```

### 4. 基础算子冒烟验证

```python
import torch
import torch.nn.functional as F

torch.manual_seed(42)

# matmul
a = torch.randn(64, 128)
b = torch.randn(128, 32)
c = torch.matmul(a, b)
assert c.shape == (64, 32)

# conv2d
x = torch.randn(1, 3, 32, 32)
w = torch.randn(16, 3, 3, 3)
conv_out = F.conv2d(x, w, padding=1)
assert conv_out.shape == (1, 16, 32, 32)

# autograd
x = torch.randn(4, 8, requires_grad=True)
w = torch.randn(8, 4, requires_grad=True)
y = x @ w
loss = y.sum()
loss.backward()
assert x.grad is not None and w.grad is not None

print("All PyTorch smoke tests passed!")
```

---

## 📝 使用示例

### 示例1: 简单 MLP 训练循环

```python
import torch
import torch.nn as nn
import torch.optim as optim

model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10)
)

optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

# Free-threading 下可用多线程数据加载
for epoch in range(5):
    for _ in range(100):
        x = torch.randn(32, 784)
        y = torch.randint(0, 10, (32,))
        
        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
    
    print(f"Epoch {epoch+1}, loss: {loss.item():.4f}")
```

### 示例2: 与 ONNX 量化栈互操作

```python
import torch
import onnx
import onnxruntime as ort
from onnxruntime.quantization import quantize_dynamic, QuantType

# 1. PyTorch 导出 ONNX
model = nn.Sequential(nn.Linear(64, 10))
model.eval()
dummy = torch.randn(1, 64)
torch.onnx.export(model, dummy, "/tmp/model.onnx",
                  input_names=["input"], output_names=["output"],
                  opset_version=18)

# 2. ONNX 量化（继承自 onnx-quantized）
quantize_dynamic("/tmp/model.onnx", "/tmp/model_int8.onnx",
                 weight_type=QuantType.QInt8)

# 3. ONNX Runtime 推理
sess = ort.InferenceSession("/tmp/model_int8.onnx",
                            providers=["CPUExecutionProvider"])
out = sess.run(None, {"input": dummy.numpy()})[0]
print(f"Inference output shape: {out.shape}")
```

---

## 🔒 挂载目录权限最佳实践

Docker bind mount（`-v /host/path:/container/path`）会直接共享宿主机文件系统，容器内的`chown`操作会**穿透修改宿主机文件权限**。本镜像v2.2.1+采用安全默认策略避免此问题：

### 默认安全策略

| 目录类型 | 默认chown行为 | 说明 |
|---------|-------------|------|
| `/workspace` | 执行chown给devuser | 这是容器专用工作目录，预期由容器管理 |
| 自定义数据目录（如`/media/pc/data/ai`） | **跳过chown** | 保护宿主机共享数据集/模型目录权限 |
| 系统目录（`/`、`/home`、`/etc`等） | **强制跳过chown** | 防止误挂载损坏宿主机系统 |
| Docker命名卷（`-v volume-name:/path`） | 执行chown | Docker管理的私有存储，安全 |

### 遇到 Permission denied 怎么办？

容器启动时如果检测到bind mount且跳过chown，会在日志中打印友好的解决方案提示框。你可以选择以下任一方案：

**方案1（推荐，宿主机一次性配置）**：
```bash
# 在宿主机执行一次，将目录权限设置为与容器devuser一致的UID/GID（默认都是1000）
sudo chown -R 1000:1000 /path/to/your/data
```

**方案2（容器内临时使用sudo）**：
```bash
# 登录容器后，仅在需要写入时临时提权修改
sudo chown -R devuser:devuser /media/pc/data/ai
```

**方案3（显式允许chown，不推荐用于共享目录）**：
```bash
# 仅在确定目录是容器专用时才添加此环境变量
docker run ... -e JUPYTER_ROOT_CHOWN=yes ...
```

### 只读挂载（推荐用于数据集）

对于只读的数据集/模型目录，推荐使用只读挂载，从根本上避免权限问题和误修改：
```bash
-v /media/pc/datasets:/media/pc/datasets:ro
```

---

## ⚠️ 已知问题与注意事项

1. **triton 加载时 GIL 临时启用**

   症状：首次使用某些 CUDA 算子或 triton 相关功能时看到 GIL 启用警告。
   
   原因：triton 库暂不支持 free-threading。
   
   影响：纯 CPU 算子、基础线性代数、conv2d、autograd 等不受影响；仅 triton JIT 编译路径临时启用 GIL。
   
   规避：纯 CPU 工作流不会触发此警告；GPU训练场景如遇问题可回退到 onnx-pytorch 变体（GIL 模式）。

2. **CUDA/GPU 使用**

   PyTorch 预编译为 `cu130`（CUDA 13.0）版本，但容器默认以CPU模式启动。
   
   ✅ **启用GPU完整指南**：详见上方「🚀 启用GPU支持（CUDA）」章节，包含前置条件、启动命令、多卡配置、验证方法和常见问题排查。
   
   快速记忆：只需在`docker run`中添加`--gpus all`参数，并确保宿主机满足NVIDIA驱动和容器工具链要求。

3. **slim 版本功能边界**

   `torch-dev-slim` 版本删除了部分专业工具以节省 2GB+ 空间：
   - ✅ 保留：单GPU/多GPU训练、推理、ONNX导出/量化、核心CUDA算子
   - ❌ 删除：多GPU分布式线性代数（cusolverMg）、cuDNN JIT引擎、NVSHMEM InfiniBand插件、protoc
   - 📖 完整说明见 [SLIMMING-GUIDE.md](./SLIMMING-GUIDE.md)「已知限制与陷阱」章节

4. **依赖链构建顺序**
   - torch-dev 依赖链：base → conda-llvm → onnx-dev → onnx-quantized → torch-dev
   - 下游 ai-dev 直接基于 torch-dev 构建
   - 本地构建建议使用 `local-build.sh` 自动处理依赖链

5. **与 onnx-pytorch 的选择**

   | 场景 | 推荐变体 | Python 环境 | GIL 状态 |
   |------|---------|------------|---------|
   | 需要 no-GIL 并发、PyTorch + ONNX 量化 | **torch-dev** | main (cp314t) | 禁用 |
   | 传统 PyTorch 工作流、兼容旧代码、onnxoptimizer | onnx-pytorch | base (3.13.x) | 启用 |
   | 完整 AI/ML/NLP 全栈（50+包） | ai-dev | base + main 双环境 | base启用/main禁用 |

6. **Python 路径**

   所有命令必须使用 main 环境 Python：
   ```bash
   /opt/conda/envs/main/bin/python your_script.py
   ```
   或先激活环境：
   ```bash
   source /opt/conda/etc/profile.d/conda.sh && conda activate main
   ```

---

## 🔗 相关链接

- [**镜像瘦身指南 SLIMMING-GUIDE.md**](./SLIMMING-GUIDE.md) - slim 标签瘦身策略、验证方法、已知限制
- [上游变体 onnx-quantized](../onnx-quantized/README.md)
- [下游变体 ai-dev](../ai-dev/README.md)
- [平行变体 onnx-pytorch](../onnx-pytorch/README.md)（GIL 模式 PyTorch）
- [本地构建脚本](../../scripts/local-build.sh)
- [测试脚本](../scripts/test-torch-dev.sh)
- [部署验证脚本](../../scripts/verify-deployment.py)
- [PyTorch free-threading 官方文档](https://docs.python.org/3.14/whatsnew/3.14.html#free-threaded-cpython)
- [PyTorch 安装指南](https://pytorch.org/get-started/locally/)

---

## 📋 依赖链

```
base (Ubuntu 26.04 + SSH + Docker DinD + Jupyter)
  ↓
conda-llvm (LLVM/Clang 22.1.8 + 编译工具链)
  ↓
onnx-dev (纯 ONNX 生态 + main 环境 free-threading cp314t，无 PyTorch)
  ↓
onnx-quantized (量化工具链 + onnxruntime.quantization)
  ↓
torch-dev (free-threading PyTorch ← 当前变体)
  - torch (2.13.0+cu130, cp314t, main 环境)
  - torchvision (0.28.0+cu130, 匹配 torch)
  - 继承: onnx, onnxruntime, onnxsim, onnxconverter-common
  - 排除: onnxoptimizer (free-threading 不兼容)
  ↓
ai-dev (完整 AI/ML/NLP 全栈生态)
```
