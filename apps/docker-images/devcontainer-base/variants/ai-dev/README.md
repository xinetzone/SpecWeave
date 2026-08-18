# DevContainer Base - ai-dev 变体

> torch-dev + 47个 AI/ML/NLP 包（base GIL） + onnx2torch/open_clip/sentence-transformers（main ft）+ JupyterLab 4.x + 跨环境 AI 内核（双环境架构：base GIL 兼容 + main free-threading PyTorch）

## ✨ 特性

### 双环境架构（Dual-Env Architecture）

ai-dev 采用**双 Python 环境隔离**设计，平衡生态兼容性与性能前沿：

| 环境 | Python | GIL | ABI | 用途 | 默认路径 |
|------|--------|-----|-----|------|---------|
| **base** | 3.13.x 标准构建 | ✅ 启用 | cpython-313 | 47 AI/ML/NLP 兼容生态（日常开发默认） | `/opt/conda/bin/python` |
| **main** | 3.14.6 cp314t | ❌ 禁用 | cpython-314t | PyTorch CUDA + ONNX 量化栈 + G-M1 torch依赖包（多核无锁性能） | `/opt/conda/envs/main/bin/python` |

- 默认 `python` 命令指向 **base 环境**（Python 3.13 GIL 启用），保证 47 包最大兼容性
- PyTorch CUDA 训练/推理通过 `/opt/conda/envs/main/bin/python` 显式调用（Python 3.14 free-threading，无 GIL 锁）
- 两个环境 site-packages 完全隔离，不可跨环境 import 包
- PATH 刻意设置为 `/opt/conda/bin:${PATH}`（base 在前，覆盖 torch-dev 的 main 在前设置）

### 架构设计原则与关键约束

#### 1. Command Mode 日志分离（Unix 规范）

entrypoint.sh 在 command mode（非服务模式）下必须严格遵循 Unix 日志规范：
- **stdout**：仅输出用户命令的数据结果（纯净，可供脚本正则匹配）
- **stderr**：输出所有诊断日志（banner/INFO/WARN/密码提示/系统诊断等）

这是测试脚本（`test-ai-dev.sh`）通过 stdout 正则匹配验证功能的基础。如果诊断日志输出到 stdout，会污染命令输出导致测试失败。

#### 2. PyTorch / Triton Free-Threading 兼容性

**已知约束**：triton（PyTorch CUDA 依赖）等部分 C 扩展模块未声明 free-threading 兼容性（缺少 `Py_mod_gil` 多阶段初始化标志）。当这些模块被 import 时，CPython 3.14t 会**自动启用 GIL**（进程级一次性保险丝，启用后当前进程内无法关闭）。

**解决方案**：
- 在同一 Python 进程中需要保持 GIL 禁用状态时，设置环境变量 `PYTHON_GIL=0`（强制覆盖，at own risk）
- 构建验证阶段通过独立进程检查 GIL 状态（先 import torch 的进程不做 GIL 断言，GIL 断言在单独进程中执行）
- Jupyter 跨环境内核指向 base 环境（GIL 启用），不涉及此问题

```bash
# 正确：保持 main 环境 GIL 禁用（import torch 前设置 PYTHON_GIL=0）
docker run --rm devcontainer-base:ai-dev-latest \
  bash -c "PYTHON_GIL=0 /opt/conda/envs/main/bin/python -c 'import torch,sys;print(torch.__version__, not sys._is_gil_enabled())'"
```

#### 3. torch 依赖包隔离规则

**判定标准**：包的 `install_requires` 中显式声明 `torch` 或 `torchvision` 依赖。

**隔离规则**：所有 torch 依赖包必须安装在 main 环境（G-M1 组），禁止安装在 base 环境——否则会因为 base 环境无 torch 而导致安装失败，或意外将 torch 拉入 base 环境破坏双环境隔离。

**已识别的 torch 依赖包清单**：
| 包 | install_requires 中的 torch 声明 | 版本获取方式 |
|----|----------------------------------|-------------|
| onnx2torch | 显式依赖 torch | `importlib.metadata.version('onnx2torch')`（无 `__version__` 属性） |
| open_clip_torch | 显式依赖 torch | `open_clip.__version__` |
| sentence-transformers | `torch>=1.11.0` | `sentence_transformers.__version__` |

#### 4. 跨环境版本号获取机制

在 Dockerfile 构建阶段（S3阶段），获取 main 环境包版本号时必须：
1. 先执行 `variant_activate_main_env` 激活 main 环境（设置正确的 PATH/LD_LIBRARY_PATH/PYTHONPATH）
2. 调用 python 获取版本号并存入 shell 变量
3. 再执行 `variant_activate_base_env` 切回 base 环境
4. 将变量传入 `variant_write_build_info`

禁止在 base 环境激活状态下直接用绝对路径 `/opt/conda/envs/main/bin/python -c ...` 获取版本——因环境变量未正确设置，可能导致 C 扩展 import 失败（错误被 `2>/dev/null` 吞掉后版本字段为空）。

#### 5. Rust 源码编译要求

G-M1 组（onnx2torch/open_clip_torch/sentence-transformers）及其依赖包中，部分包（如 safetensors）可能无预编译 cp314t wheel，需要 Rust 工具链 + maturin 从源码编译。构建时已预装 Rust，G-M1 组启用 `--verbose` 模式输出编译详情便于排查。

### 基础镜像继承链（6层）

devcontainer-base → conda-llvm → onnx-dev → onnx-quantized → torch-dev → **ai-dev**

继承自上游：
- Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
- SSH(22) + Docker DinD(2375) + Podman + Jupyter(8888)
- supervisord 进程管理，devuser 非 root 用户
- Miniforge3 + LLVM 22.1.8 + CMake + Ninja
- **main 环境（来自 torch-dev）**：PyTorch + TorchVision（CUDA cp314t free-threading）、ONNX Runtime + 量化工具链

### ai-dev 特有功能（base 环境，47 个包 + main 环境 G-M1 组）

- 47 个 Python 包覆盖 NLP、数据处理、可视化、文档处理、Web API、数据库客户端（base 环境 G1-G14）
- onnx2torch、open_clip_torch、sentence-transformers 安装在 main 环境（G-M1组，与 torch 同处），避免破坏双环境隔离
- HuggingFace Transformers 生态（transformers, datasets, evaluate 在 base；sentence-transformers 在 main G-M1）
- JupyterLab >=4.4 + notebook >=7.3（解决 httpx>=0.28 兼容性）
- 预注册 **"Python 3 (AI Dev)"** 跨环境 Jupyter 内核：Jupyter 服务运行于 main 环境（supervisord 启动），内核指向 base 环境 Python（47 个包可用）
- OpenMP 性能调优（OMP_NUM_THREADS=4, KMP_DUPLICATE_LIB_OK=TRUE）
- 下游 llm-agent 变体的直接基础

## 🚀 快速开始（3条命令）

```bash
# 1. base 环境验证（默认 python = Python 3.13 GIL 启用，47 包可用）
docker run --rm devcontainer-base:ai-dev-latest \
  python -c "import transformers,datasets,fastapi,pandas;print('base OK: GIL enabled, 47 packages ready')"

# 2. main 环境验证（PyTorch free-threading，无 GIL，CUDA 可用）
# 注意：import torch 后检查 GIL 需设置 PYTHON_GIL=0（triton 兼容问题）
docker run --rm devcontainer-base:ai-dev-latest \
  bash -c "PYTHON_GIL=0 /opt/conda/envs/main/bin/python -c \"import torch,sys;print(f'main OK: torch={torch.__version__}, GIL disabled={not sys._is_gil_enabled()}, CUDA={torch.cuda.is_available()}')\""

# 3. 交互式使用
docker run -it --rm -p 8888:8888 -e JUPYTER_TOKEN=mysecret devcontainer-base:ai-dev-latest
```

## 📦 包含的 Python 包

### base 环境安装的包（GIL 启用，本层新增 47 包，G1-G14分组）

| 分组 | 包 |
|------|-----|
| **G1: 构建工具** | scikit-build-core, nuitka, invoke, build |
| **G2: 核心工具** | decorator, attrs, cloudpickle, typing_extensions, pytest, psutil |
| **G3: Jupyter 生态** | ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3 |
| **G4: 数据处理** | pyarrow, pandas, scikit-learn, natsort |
| **G5: NLP/Transformers** | datasets, transformers, sentencepiece, evaluate, tiktoken（sentence-transformers 依赖 torch，在 main G-M1） |
| **G6: 可视化/CLI** | matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich |
| **G7: AI/ML 工具** | einops, numba（open_clip_torch 依赖 torch，在 main G-M1） |
| **G8: 音频处理** | librosa |
| **G9: 中文 NLP** | jieba, nltk, pypinyin |
| **G10: 文档处理** | PyMuPDF (fitz), EbookLib, beautifulsoup4, openpyxl |
| **G11: Web/API** | pydantic, fastapi, uvicorn, httpx>=0.28 |
| **G12: 序列化/配置** | toml, typer, xmltodict, pyyaml |
| **G13: 数据库客户端** | psycopg2-binary (PostgreSQL), pymongo (MongoDB), elasticsearch, minio |
| **G14: 开发工具** | icecream |

### main 环境的包（来自 torch-dev + 本层 G-M1 组，free-threading cp314t）

| 分类 | 包 |
|------|-----|
| **PyTorch 核心** | torch, torchvision（CUDA cu130/cu128/cpu，cp314t free-threading） |
| **ONNX 生态** | onnx, onnxruntime |
| **ONNX 工具** | onnx-simplifier, onnxscript |
| **量化工具** | onnxruntime.quantization, onnxconverter-common |
| **G-M1: PyTorch 生态（本层新增）** | onnx2torch, open_clip_torch, sentence-transformers（依赖 torch，装在 main 环境） |
| **编译工具链** | LLVM 22.1.8, clang, cmake, ninja（来自 conda-llvm 链） |

### 显式排除

- **onnxoptimizer**: free-threading 不兼容（CPython #111506），继承自 onnx-quantized 约束
- **torch/torchvision 不装在 base**: 只在 main 环境存在；所有声明 `install_requires: torch` 的包（onnx2torch, open_clip_torch, sentence-transformers）也必须装在 main 环境（G-M1组）

## 📁 目录结构

```
variants/ai-dev/
├── AGENTS.md               # AI 协作者入口（本变体规范路由）
├── Dockerfile              # ai-dev 变体构建文件（3 层追加阶段）
├── .env.example            # 构建参数配置模板
├── README.md               # 本文档
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 详细规范
```

## 🚀 构建

### 前置条件

需要先构建完整的依赖链（拓扑排序自动处理，无需手动逐层构建）：

```bash
# 在 devcontainer-base 根目录构建所有依赖
bash variants/build.sh --all --cn

# 或仅构建 ai-dev 及其依赖链（torch-dev → onnx-quantized → onnx-dev → conda-llvm → base）
bash variants/build.sh --variant ai-dev --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant ai-dev

# 使用国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant ai-dev --cn
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建（需先有 devcontainer-base:torch-dev-latest 镜像）
docker build -f variants/ai-dev/Dockerfile \
  -t devcontainer-base:ai-dev-latest .

# 国内镜像源构建
docker build -f variants/ai-dev/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=aliyun \
  -t devcontainer-base:ai-dev-latest .
```

## 🐳 运行

### DinD 模式（推荐开发环境）

```bash
docker run -d \
  --name devcontainer-ai-dev \
  --privileged \
  -p 2222:22 \
  -p 2375:2375 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  devcontainer-base:ai-dev-latest
```

### 命令模式（调试/一次性任务）

```bash
# 默认进入 bash，使用 base 环境（GIL）
docker run -it --rm devcontainer-base:ai-dev-latest bash

# 显式使用 main 环境（PyTorch free-threading）
docker run -it --rm devcontainer-base:ai-dev-latest /opt/conda/envs/main/bin/python
```

### DooD 模式（生产/CI 环境，无需 --privileged）

```bash
docker run -d \
  --name devcontainer-ai-dev-dood \
  -p 2223:22 \
  -p 8889:8888 \
  -v $(pwd)/workspace:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:ai-dev-latest
```

## ✅ 验证

```bash
# === 双环境架构验证 ===
echo "=== base 环境（默认 python，GIL 启用）==="
docker run --rm devcontainer-base:ai-dev-latest \
  python -c "import sys;print(f'GIL enabled: {sys._is_gil_enabled()}')"

echo "=== main 环境（PyTorch ft，GIL 禁用）==="
# 注意：先 import torch 再检查 GIL 时需设置 PYTHON_GIL=0（triton 未声明 ft 兼容会自动启用 GIL）
docker run --rm devcontainer-base:ai-dev-latest \
  bash -c "PYTHON_GIL=0 /opt/conda/envs/main/bin/python -c \"import sys;print(f'GIL enabled: {sys._is_gil_enabled()}')\""

# === base 环境核心包导入验证（47 包）===
docker run --rm devcontainer-base:ai-dev-latest \
  python -c "import transformers, datasets, fastapi, pandas; print('ai-dev base OK')"

# === main 环境 PyTorch + ONNX 量化验证（含onnx2torch/open_clip/sentence-transformers）===
docker run --rm devcontainer-base:ai-dev-latest \
  bash -c "PYTHON_GIL=0 /opt/conda/envs/main/bin/python -c \"import torch, torchvision, onnx2torch, open_clip, sentence_transformers; from onnxruntime.quantization import quantize_dynamic; print(f'torch={torch.__version__}, torchvision={torchvision.__version__}, CUDA={torch.cuda.is_available()}')\""

# === base 环境 torch 隔离验证（base 不应有 torch）===
docker run --rm devcontainer-base:ai-dev-latest \
  python -c "import importlib.util; print('torch NOT in base:', importlib.util.find_spec('torch') is None)"

# === Jupyter 验证 ===
# JupyterLab 版本（服务由 main 环境 jupyter 启动）
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/conda/envs/main/bin/jupyter lab --version

# Jupyter 内核注册（main 环境 jupyter 服务可见 ai-dev 内核）
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/conda/envs/main/bin/jupyter kernelspec list

# === 基础服务验证 ===
docker run --rm devcontainer-base:ai-dev-latest which sshd
docker run --rm devcontainer-base:ai-dev-latest docker --version

# === 查看构建元数据 ===
docker run --rm devcontainer-base:ai-dev-latest \
  cat /etc/devcontainer-variant-ai-dev-build-info

# === 完整测试套件（29 项，含双环境GIL守卫+torch隔离）===
bash variants/scripts/test-ai-dev.sh
```

## 🔧 Jupyter 内核

ai-dev 变体内核名为 **"Python 3 (AI Dev)"**，采用跨环境内核机制：

- **Jupyter 服务**：`/opt/conda/envs/main/bin/jupyter`（supervisord 以绝对路径启动，运行于 main 环境）
- **内核注册位置**：`/opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json`（main 环境 kernels 目录，对服务可见）
- **内核 Python**：`/opt/conda/bin/python`（指向 base 环境，50+ AI/ML/NLP 包全部可用）
- **内核 env.PATH**：显式设置为 `/opt/conda/bin:...` 确保内核进程中 base 工具优先

在 JupyterLab 中选择 "Python 3 (AI Dev)" 内核即可使用全部 50+ 包。

> ⚠️ **注意**：此内核中无法直接 `import torch`（torch 在 main 环境而非 base）。需要 PyTorch 时请使用绝对路径 `/opt/conda/envs/main/bin/python` 启动脚本，或在 Notebook 中通过 subprocess 调用。

## 🌍 哪个环境用哪个？（环境选择决策树）

```
我要做什么？
├─ 数据处理（pandas/pyarrow）、NLP（transformers/datasets）、Web API（fastapi）、
│  文档处理（PyMuPDF/bs4）、数据库（psycopg2/pymongo）、可视化（matplotlib/seaborn）
│  → ✅ 用 base 环境：直接 python 命令 / Jupyter "Python 3 (AI Dev)" 内核
│
├─ PyTorch 模型训练/推理、CUDA 计算、无 GIL 多核并行、ONNX Runtime 量化
│  → ✅ 用 main 环境：/opt/conda/envs/main/bin/python 显式调用
│
└─ 不确定？
   → ✅ 先用 base 环境（默认），遇到 import torch 错误时再切 main
```

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像标签（torch-dev 变体标签） |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna (CN)` | Conda 源：tuna/official |
| `PIP_MIRROR` | `aliyun (CN)` | PyPI 源：aliyun/tuna/official |

## 📊 继承的镜像变体（6层依赖链）

| 层级 | 变体 | 新增内容 |
|------|------|---------|
| L0 | devcontainer-base | Ubuntu 26.04 + SSH + Docker + Jupyter + supervisord + devuser |
| L1 | conda-llvm | Miniforge3 + LLVM 22.1.8 + clang + cmake + ninja |
| L2 | onnx-dev | ONNX 生态（onnx/onnxruntime/onnx-simplifier/onnxscript，base 环境纯 ONNX） |
| L3 | onnx-quantized | onnxruntime.quantization + FP16/INT8 量化 + main free-threading 环境 |
| L4 | torch-dev | PyTorch + TorchVision（CUDA cp314t free-threading，main 环境）+ JupyterLab 4.x |
| L5 | **ai-dev** | **47个AI/ML/NLP包（base env）+ onnx2torch/open_clip/sentence-transformers（main env G-M1）+ 跨环境Jupyter内核 + 双环境架构守卫** |

## 🔗 相关镜像

- [devcontainer-base](../../README.md) — 基础镜像（SSH + Docker + Podman + Jupyter）
- [conda-llvm](../conda-llvm/README.md) — LLVM 编译工具链
- [onnx-dev](../onnx-dev/README.md) — 纯 ONNX 生态
- [onnx-quantized](../onnx-quantized/README.md) — ONNX 量化工具链 + free-threading 环境
- [torch-dev](../torch-dev/README.md) — PyTorch CUDA free-threading（ai-dev 直接基础）
- [llm-agent](../llm-agent/README.md) — LLM Agent 开发（基于 ai-dev，加装 LangChain 生态）
