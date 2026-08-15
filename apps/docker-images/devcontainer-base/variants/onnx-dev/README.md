# DevContainer Base - ONNX-Dev 变体 (纯 ONNX 生态工具链)

> 基于 devcontainer-base:conda-llvm 变体的**纯 ONNX 生态运行时**镜像，在保留所有基础功能（含 LLVM/Clang 工具链）的前提下，于 conda **main 环境**（Python 3.14.6 cp314t free-threading，默认用户环境）预装 ONNX 工具链（onnx, onnxruntime, onnx-simplifier, onnxscript），开箱即用。
>
> **核心定位：不含 PyTorch**。torch/torchvision 被显式排除并设有构建期负向验证防线（`find_spec('torch') is None` 断言），任何依赖意外拉入 torch 都会使构建失败。需要 PyTorch 时请运行期按需安装（`pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`）或使用 [onnx-pytorch 变体](../onnx-pytorch/README.md)。
>
> **onnxoptimizer 亦被排除**：其 sdist 声明 `py_limited_api='cp312'`，与 free-threading 构建（`Py_GIL_DISABLED`）根本不兼容（[CPython #111506](https://github.com/python/cpython/issues/111506)），无 cp314t wheel，源码构建必失败；onnxsim 0.5+ 已内置图优化功能基本覆盖其用途。

## ✨ 特性

- **基础镜像继承**：完全继承 conda-llvm 变体和 devcontainer-base 的所有功能
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户 (UID 1000)
  - Miniforge3 安装在 `/opt/conda`
  - LLVM/Clang 22.1.8 + CMake + Ninja + Make 编译工具链（conda main 环境）
- **main 环境安装**：ONNX 工具链安装于 conda **main 环境**（Python 3.14.6 cp314t free-threading，默认用户环境），与默认 Python/Jupyter 共享环境
- **ONNX 工具链**：
  - `onnx`（模型定义/checker/序列化）
  - `onnxruntime`（CPU 推理引擎）
  - `onnx-simplifier`（模型精简，`python -m onnxsim`，0.5+ 内置图优化）
  - `onnxscript`（新式 opset/算子编写）
- **PyTorch 一等排除约束**：torch/torchvision 不进镜像 + 构建期/测试期双重负向验证防线（镜像更小、依赖更干净）
- **onnxoptimizer 排除**：与 free-threading 根本不兼容（`Py_LIMITED_API` × `Py_GIL_DISABLED`，CPython #111506），设有 T4 负向验证防线防止依赖回拉
- **free-threading 防线**：安装后断言 python build 为 cp314t 且 `sys._is_gil_enabled() is False`，pip 依赖破坏 free-threading 会使构建立即失败
- **PATH 设计**：`/opt/conda/envs/main/bin` 在 PATH 最前面，onnx 工具与默认 Python 直接可用
- **服务稳定**：Jupyter 等服务由 supervisord 用 main 环境绝对路径启动，不受 PATH 变更影响
- **国内镜像支持**：conda 源支持 bfsu（默认）/tuna/aliyun/official，pip 源 aliyun（默认）/tuna/official

## 📦 包含组件

| 组件 | 版本 | 说明 |
|------|------|------|
| ONNX | latest | 开放神经网络交换格式（定义/checker） |
| ONNX Runtime | latest | 跨平台推理引擎（CPUExecutionProvider） |
| onnx-simplifier | latest | ONNX 模型精简工具（0.5+ 内置图优化） |
| onnxscript | latest | 新式 opset/算子编写框架 |
| onnxoptimizer | **不含** | 显式排除：free-threading 不兼容（CPython #111506） |
| torch / torchvision | **不含** | 显式排除（负向验证防线） |
| Python | 3.14.6 (cp314t) | main 环境，free-threading（GIL 禁用） |
| LLVM / Clang | 22.1.8 | 继承自 conda-llvm 变体 |
| CMake / Ninja / Make | latest | 继承自 conda-llvm 变体 |

> 组件实际版本以容器内 `/etc/devcontainer-variant-onnx-dev-build-info` 为准。

## 📁 目录结构

```
variants/onnx-dev/
├── Dockerfile              # ONNX-Dev 变体构建文件（4个追加阶段）
├── .env.example            # 构建参数配置模板
├── README.md               # 本文件
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

需要先构建基础镜像和 conda-llvm 变体（conda 中间变体已下线）：

```bash
# 在 devcontainer-base 根目录
cd /path/to/devcontainer-base

# 1. 构建基础镜像（V2 内置默认镜像源）
bash scripts/build.sh --cn

# 2. 构建 conda-llvm 变体
bash variants/build.sh --variant conda-llvm --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant onnx-dev

# 国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant onnx-dev --cn

# 构建后验证
bash variants/build.sh --variant onnx-dev --cn --verify
```

### 一键构建脚本（自动构建依赖 + 测试）

```bash
bash variants/scripts/build-onnx-dev.sh          # 国内源（默认）
bash variants/scripts/build-onnx-dev.sh --official
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建
docker build -f variants/onnx-dev/Dockerfile \
  -t devcontainer-base:onnx-dev-latest .

# 国内镜像源构建
docker build -f variants/onnx-dev/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=bfsu \
  --build-arg PIP_MIRROR=aliyun \
  -t devcontainer-base:onnx-dev-latest .
```

## 🐳 运行

### DinD 模式（推荐开发环境）

```bash
docker run -d \
  --name devcontainer-onnx-dev \
  --privileged \
  -p 2222:22 \
  -p 2375:2375 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  devcontainer-base:onnx-dev-latest
```

### 命令模式（调试/一次性推理任务）

```bash
# 进入容器交互模式
docker run -it --rm --privileged devcontainer-base:onnx-dev-latest bash

# 直接在容器内运行 ONNX 推理脚本
docker run --rm -v $(pwd):/workspace -w /workspace \
  devcontainer-base:onnx-dev-latest \
  python infer.py
```

## 🔧 工具使用说明

### PATH 优先级说明

**onnx-dev 变体中，`/opt/conda/envs/main/bin` 在 PATH 最前面**，因此：
- `python` 和 `pip` 默认指向 conda main 环境的 **Python 3.14.6（cp314t free-threading，GIL 默认禁用）**
- `onnx`, `onnxruntime`, `onnxsim`, `onnxscript` 可直接 import，无需激活环境
- LLVM 工具链（`llvm-config`, `clang`, `cmake`, `ninja`, `make`）直接可用（继承自 conda-llvm）
- **Jupyter 服务不受影响**：supervisord 使用 main 环境绝对路径启动

### 验证导入

```bash
# 一键验证 ONNX 生态（不含 torch）
python -c "import onnx,onnxruntime;print(onnx.__version__,onnxruntime.__version__)"

# 验证 free-threading Python（GIL 禁用）
python -c "import sys;print(sys._is_gil_enabled())"   # 期望输出: False

# 验证 torch 确实不存在（负向验证）
python -c "import torch"   # 期望: ModuleNotFoundError
```

### 纯 ONNX 工作流示例（无需 torch）

```bash
# onnx.helper 手工构图 + checker + onnxruntime 推理
python - << 'EOF'
import numpy as np
import onnx
from onnx import helper, TensorProto
import onnxruntime as ort

# 1) 手工构建 Add 模型
a = helper.make_tensor_value_info("a", TensorProto.FLOAT, [2])
b = helper.make_tensor_value_info("b", TensorProto.FLOAT, [2])
c = helper.make_tensor_value_info("c", TensorProto.FLOAT, [2])
node = helper.make_node("Add", ["a", "b"], ["c"])
graph = helper.make_graph([node], "add_graph", [a, b], [c])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
onnx.checker.check_model(model)
onnx.save(model, "/tmp/add.onnx")
print("model saved")

# 2) onnxruntime CPU 推理
sess = ort.InferenceSession("/tmp/add.onnx", providers=["CPUExecutionProvider"])
out = sess.run(None, {"a": np.array([1.,2.],np.float32), "b": np.array([3.,4.],np.float32)})
print("output:", out[0].tolist())   # [4.0, 6.0]
EOF
```

### 模型精简与优化

```bash
# 生成测试模型后，使用 onnx-simplifier 精简（0.5+ 内置图优化，
# 基本覆盖 onnxoptimizer 的用途——后者与 free-threading 不兼容，本变体不含）
python -m onnxsim /tmp/add.onnx /tmp/add-simplified.onnx
```

### 按需安装 PyTorch（可选）

```bash
# 运行期按需安装 CPU 版 PyTorch（不进镜像，装在容器层）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 国内网络可用清华镜像
pip install torch torchvision --index-url https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cpu
```

## ✅ 验证命令

```bash
# 验证 ONNX 版本
docker run --rm devcontainer-base:onnx-dev-latest \
  /opt/conda/envs/main/bin/python -c "import onnx;print(onnx.__version__)"

# 验证 ONNX Runtime 版本
docker run --rm devcontainer-base:onnx-dev-latest \
  /opt/conda/envs/main/bin/python -c "import onnxruntime;print(onnxruntime.__version__)"

# 验证 free-threading Python
docker run --rm devcontainer-base:onnx-dev-latest \
  /opt/conda/envs/main/bin/python -c "import sys;print(sys.version);print(sys._is_gil_enabled())"
# 期望: Python 3.14.6 ... / False

# 验证 torch 不存在（负向验证，期望失败退出码非0）
docker run --rm devcontainer-base:onnx-dev-latest \
  /opt/conda/envs/main/bin/python -c "import torch" || echo "torch absent (expected)"

# 验证 Jupyter 服务仍可用（main 环境绝对路径）
docker run --rm devcontainer-base:onnx-dev-latest /opt/conda/envs/main/bin/jupyter --version

# 验证 Docker 可用
docker run --rm --privileged devcontainer-base:onnx-dev-latest docker --version

# 验证 LLVM 工具链继承
docker run --rm devcontainer-base:onnx-dev-latest llvm-config --version
# 期望输出: 22.1.8

# 完整单元测试（21项）
bash variants/scripts/test-onnx-dev.sh

# 查看构建信息
docker run --rm devcontainer-base:onnx-dev-latest cat /etc/devcontainer-variant-onnx-dev-build-info
```

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | conda-llvm 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `bfsu` | Conda 源：bfsu（北外，默认）/tuna/aliyun/official |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun（阿里云）/tuna（清华）/official |

> 本变体无 `TORCH_INDEX_URL` 参数——torch/torchvision 不安装。

## 📋 关键路径

| 路径 | 说明 |
|------|------|
| `/opt/conda/envs/main/bin` | main 环境 bin 目录（PATH 最前：ONNX 工具 + Python 3.14t + Jupyter） |
| `/opt/conda` | Miniforge3 安装根目录 |
| `/opt/conda/envs/main` | main 环境（默认用户环境，ONNX 工具链所在） |
| `/etc/profile.d/conda-init.sh` | 基础镜像默认激活脚本（激活 main 环境） |
| `/etc/profile.d/onnx-dev-init.sh` | ONNX-Dev 备选激活脚本（激活 main 环境） |
| `/etc/devcontainer-variant-onnx-dev-build-info` | 构建元数据 |

## ⚠️ 注意事项

1. **PATH 优先级**：onnx-dev 变体中 `/opt/conda/envs/main/bin` 在 PATH 最前面。默认 `python` 是 main 环境的 Python 3.14.6（cp314t free-threading）。

2. **free-threading 运行时**：main 环境 Python 为 cp314t 构建，GIL 默认禁用（`sys._is_gil_enabled()` 返回 `False`）。构建期 GUARD 断言安装 ONNX 生态后 free-threading 状态未被破坏。

3. **PyTorch 不在镜像中（设计决策）**：torch/torchvision 被显式排除，构建期与测试期均有负向验证（`find_spec` 断言）。这使镜像更小、依赖更干净、避免 torch 与 free-threading python 的兼容性问题。如需 PyTorch：运行期 `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu`，或使用 onnx-pytorch 变体。

4. **cp314t wheel 兼容性**：onnxruntime 等含 C/C++ 扩展的包需要 cp314t（free-threading）wheel。若上游暂未发布兼容 wheel，构建会在 pip 安装阶段清晰失败（预期防线行为）。纯 Python 包（onnx/onnxscript 等）不受影响。

5. **服务不受影响**：Jupyter、SSH、Docker 等服务由 supervisord 使用 main 环境绝对路径启动，不受 PATH 顺序变更影响。

6. **下载缓存**：Dockerfile 使用 BuildKit cache 挂载 `/opt/conda/pkgs` 与 `/root/.cache/pip`，重复构建时可大幅加速。

7. **LLVM 工具链继承**：`llvm-config`/`clang`/`cmake`/`ninja` 来自 conda-llvm 基础镜像，可用于编译自定义算子/扩展。

## 🔗 相关镜像

- [devcontainer-base](../../README.md) - 基础镜像（SSH + Docker + Podman + Jupyter + Miniforge3）
- [conda-llvm variant](../conda-llvm/README.md) - LLVM/Clang 工具链变体（本变体的基础）
- [onnx-pytorch variant](../onnx-pytorch/README.md) - 含 PyTorch CPU 的 ONNX 变体（需要 torch 时选用）

## 📄 相关文档

- [Dockerfile 规范](./.agents/rules/dockerfile.md) - 本变体 Dockerfile 规范说明
- [构建编排规范](../.agents/rules/build-orchestration.md) - build.sh 统一构建
- [测试规范](../.agents/rules/testing.md) - 6 层测试策略
