# torch-dev 变体 - Free-Threading PyTorch 开发环境 v1.0.0

> **发布日期**: 2026-08-15 | **状态**: ✅ 正式发布 | **Python**: 3.14.6 cp314t free-threading

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

# 国内镜像加速
bash scripts/local-build.sh --variant torch-dev --cn
```

### 方式二：Docker 直接构建

```bash
cd apps/docker-images/devcontainer-base

# 按依赖链构建（需先构建 base→conda-llvm→onnx-dev→onnx-quantized）
bash variants/build.sh --variant torch-dev --tag latest

# 国内源
bash variants/build.sh --variant torch-dev --tag latest --cn
```

### 方式三：启动容器

```bash
# 开发模式（推荐）
docker run -d --privileged \
  --name torch-dev \
  -p 2222:22 \
  -p 8888:8888 \
  -p 2375:2375 \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=devtoken \
  -e GRANT_SUDO=yes \
  -v $(pwd)/workspace:/workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:torch-dev-latest

# 快速验证（一次性运行）
docker run --rm devcontainer-base:torch-dev-latest \
  /opt/conda/envs/main/bin/python -c "
import torch
print(f'torch {torch.__version__} ready!')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'Free-threading: GIL disabled = {not torch._is_gil_enabled()}')
"
```

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

## ⚠️ 已知问题与注意事项

1. **triton 加载时 GIL 临时启用**

   症状：首次使用某些 CUDA 算子或 triton 相关功能时看到 GIL 启用警告。
   
   原因：triton 库暂不支持 free-threading。
   
   影响：纯 CPU 算子、基础线性代数、conv2d、autograd 等不受影响；仅 triton JIT 编译路径临时启用 GIL。
   
   规避：纯 CPU 工作流可忽略此警告；如遇问题可回退到 onnx-pytorch 变体（GIL 模式）。

2. **CUDA 可用性**

   torch 安装的是 `cu130` 索引包，但容器默认无 NVIDIA runtime。需要 CUDA 时请使用 `--gpus all` 启动并确保宿主机已安装 NVIDIA Container Toolkit：
   ```bash
   docker run --gpus all --rm devcontainer-base:torch-dev-latest \
     /opt/conda/envs/main/bin/python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **依赖链构建顺序**
   - torch-dev 依赖链：base → conda-llvm → onnx-dev → onnx-quantized → torch-dev
   - 下游 ai-dev 直接基于 torch-dev 构建
   - 本地构建建议使用 `local-build.sh` 自动处理依赖链

4. **与 onnx-pytorch 的选择**

   | 场景 | 推荐变体 | Python 环境 | GIL 状态 |
   |------|---------|------------|---------|
   | 需要 no-GIL 并发、PyTorch + ONNX 量化 | **torch-dev** | main (cp314t) | 禁用 |
   | 传统 PyTorch 工作流、兼容旧代码、onnxoptimizer | onnx-pytorch | base (3.13.x) | 启用 |
   | 完整 AI/ML/NLP 全栈（50+包） | ai-dev | base + main 双环境 | base启用/main禁用 |

5. **Python 路径**

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
