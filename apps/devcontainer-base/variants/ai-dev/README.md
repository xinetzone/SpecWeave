# DevContainer Base - ai-dev 变体

> onnx-quantized + 完整 AI/ML/NLP 全栈 Python 生态系统（50+ 包）+ JupyterLab 4.x + 通用 AI 内核

## ✨ 特性

- **基础镜像继承链**：devcontainer-base → conda → conda-llvm → onnx-pytorch → onnx-quantized → **ai-dev**
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户
  - Miniconda3 + LLVM 22.1.8 + CMake + Ninja
  - PyTorch CPU + ONNX + ONNX Runtime + 量化工具链
- **ai-dev 特有功能**：
  - 50+ Python 包覆盖 NLP、数据处理、可视化、文档处理、Web API、数据库客户端
  - HuggingFace Transformers 生态（transformers, datasets, sentence-transformers, evaluate）
  - JupyterLab >=4.4 + notebook >=7.3（解决 httpx>=0.28 兼容性）
  - 预注册 "Python 3 (AI Dev)" Jupyter 内核（conda base 环境）
  - OpenMP 性能调优（OMP_NUM_THREADS=4, KMP_DUPLICATE_LIB_OK=TRUE）

## 📦 包含的 Python 包

### 构建工具
scikit-build-core, nuitka, invoke, build

### Jupyter 生态
ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3

### NLP / Transformers
transformers, datasets, sentencepiece, sentence-transformers, evaluate, tiktoken, onnx2torch

### 数据处理
pandas, pyarrow, scikit-learn, natsort

### 可视化
matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich

### AI/ML 工具
einops, open_clip_torch, numba

### 音频处理
librosa

### 中文 NLP
jieba, nltk, pypinyin

### 文档处理
PyMuPDF (fitz), EbookLib, beautifulsoup4, openpyxl

### Web / API
fastapi, uvicorn, pydantic, httpx>=0.28

### 序列化 / 配置
toml, typer, xmltodict, pyyaml

### 数据库客户端
psycopg2-binary (PostgreSQL), pymongo (MongoDB), elasticsearch, minio

### 开发工具
pytest, psutil, decorator, attrs, cloudpickle, typing_extensions, icecream

### 继承自 onnx-quantized
torch, torchvision, onnx, onnxruntime, onnxconverter-common, onnxsim

## 📁 目录结构

```
variants/ai-dev/
├── Dockerfile              # ai-dev 变体构建文件（3 层追加阶段）
├── .env.example            # 构建参数配置模板
├── README.md               # 本文档
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

需要先构建完整的依赖链：

```bash
# 在 devcontainer-base 根目录构建所有依赖
bash variants/build.sh --all --cn

# 或仅构建 ai-dev 及其依赖
bash variants/build.sh --variant ai-dev --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant ai-dev

# 使用国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant ai-dev --cn

# 构建后自动验证
bash variants/build.sh --variant ai-dev --cn
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建
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
docker run -it --rm devcontainer-base:ai-dev-latest bash
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
# 核心包导入验证
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/conda/bin/python -c "import transformers, datasets, fastapi, pandas; print('ai-dev OK')"

# 验证系统 venv 仍然存在
docker run --rm devcontainer-base:ai-dev-latest /opt/venv/bin/python --version

# 验证 JupyterLab 版本
docker run --rm devcontainer-base:ai-dev-latest /opt/venv/bin/jupyter lab --version

# 验证 Jupyter 内核注册
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/venv/bin/jupyter kernelspec list

# 验证量化工具链继承
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/conda/bin/python -c "from onnxruntime.quantization import quantize_dynamic; print('quantization OK')"

# 验证基础服务
docker run --rm devcontainer-base:ai-dev-latest which sshd
docker run --rm devcontainer-base:ai-dev-latest docker --version

# 查看构建信息
docker run --rm devcontainer-base:ai-dev-latest \
  cat /etc/devcontainer-variant-ai-dev-build-info
```

## 🔧 Jupyter 内核

ai-dev 变体内核名为 **"Python 3 (AI Dev)"**，使用 conda base 环境的 Python：

- 内核路径：`/opt/conda/bin/python`
- 已预装所有 AI/ML/NLP 包，无需额外 pip install
- UI 和 CLI 均可见（双路径注册）

在 JupyterLab 中选择 "Python 3 (AI Dev)" 内核即可使用全部包。

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna/official |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun/tuna/official |

## 📊 继承的镜像变体

| 层级 | 变体 | 新增内容 |
|------|------|---------|
| L0 | devcontainer-base | Ubuntu 26.04 + SSH + Docker + Jupyter + supervisord |
| L1 | conda | Miniconda3 + Python 3.14 |
| L2 | conda-llvm | LLVM 22.1.8 + clang + cmake + ninja |
| L3 | onnx-pytorch | PyTorch CPU + ONNX + ONNX Runtime |
| L4 | onnx-quantized | onnxruntime.quantization + FP16/INT8 量化 |
| L5 | **ai-dev** | **50+ AI/ML/NLP 包 + JupyterLab 4.x + AI 内核** |

## 🔗 相关镜像

- [devcontainer-base](../../README.md) — 基础镜像（SSH + Docker + Podman + Jupyter）
- [conda](../conda/README.md) — Miniconda3 基础环境
- [conda-llvm](../conda-llvm/README.md) — LLVM 编译工具链
- [onnx-pytorch](../onnx-pytorch/README.md) — PyTorch + ONNX 运行时
- [onnx-quantized](../onnx-quantized/README.md) — ONNX 量化工具链
