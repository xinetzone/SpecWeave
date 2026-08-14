# ai-dev 变体 Dockerfile 规范

## 基础信息

- **基础镜像**: `devcontainer-base:onnx-quantized-${BASE_TAG}`
- **继承链**: devcontainer-base → conda → conda-llvm → onnx-pytorch → onnx-quantized → ai-dev
- **安装环境**: conda base 环境（`/opt/conda`）
- **PATH 优先级**: `/opt/conda/bin` 优先于系统 PATH（conda python 为默认 python）
- **默认 Python**: `/opt/conda/bin/python`（继承自 onnx-quantized）
- **系统 venv**: `/opt/venv/bin/python` 保留（Jupyter 服务使用）

## 核心组件

| 分类 | 包 | 说明 |
|------|-----|------|
| 构建工具 | scikit-build-core, nuitka, invoke, build | Python 包构建与编译 |
| 深度学习（继承） | torch, torchvision, onnx, onnxruntime | 来自 onnx-quantized |
| 量化（继承） | onnxruntime.quantization, onnxconverter-common, onnxsim | 来自 onnx-quantized |
| Jupyter | ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3 | 同时升级 /opt/venv 版本 |
| NLP/Transformers | transformers, datasets, sentencepiece, sentence-transformers, evaluate, tiktoken | HuggingFace 生态 |
| 模型转换 | onnx2torch | ONNX→PyTorch |
| 数据处理 | pandas, pyarrow, scikit-learn, natsort | 数据分析栈 |
| 可视化 | matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich | 图表与终端美化 |
| AI/ML 工具 | einops, open_clip_torch, numba | 张量操作/编译加速 |
| 音频处理 | librosa | 音频分析 |
| 中文 NLP | jieba, nltk, pypinyin | 中文分词/拼音 |
| 文档处理 | PyMuPDF, EbookLib, beautifulsoup4, openpyxl | PDF/EPUB/HTML/Excel |
| Web/API | fastapi, uvicorn, pydantic, httpx>=0.28 | 异步 Web 框架 |
| 序列化 | toml, typer, xmltodict, pyyaml | 配置/CLI |
| 数据库 | psycopg2-binary, pymongo, elasticsearch, minio | PostgreSQL/MongoDB/ES/MinIO |
| 开发工具 | pytest, psutil, decorator, attrs, cloudpickle, icecream | 测试/调试/工具 |

## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| BASE_TAG | latest | 基础镜像标签后缀 |
| APT_MIRROR | official | APT 镜像源 |
| CONDA_MIRROR | tuna (CN) / official | Conda 镜像源 |
| PIP_MIRROR | aliyun (CN) / official | Pip 镜像源 |

## 环境变量

| 变量 | 值 | 说明 |
|------|-----|------|
| CONDA_DIR | /opt/conda | Conda 安装路径 |
| PATH | /opt/conda/bin:${PATH} | conda 工具优先 |
| OMP_NUM_THREADS | 4 | OpenMP 线程数 |
| OPENBLAS_NUM_THREADS | 1 | OpenBLAS 线程数 |
| OMP_WAIT_POLICY | PASSIVE | OpenMP 等待策略 |
| KMP_DUPLICATE_LIB_OK | TRUE | 允许 OpenMP 多副本共存 |
| PIP_USER | 1（运行时） | 运行时支持用户级 pip 安装 |

## Stage 结构（3 层追加）

### Stage 1/3: 基础验证 + 计时器初始化
- 验证 torch/onnx/onnxruntime/quantization 可导入
- 确认 devuser 和基础服务（docker/supervisord）存在
- 验证 /opt/venv 保留
- 初始化 `/tmp/.ai-dev-variant-build-timer`

### Stage 2/3: 安装 AI/ML/NLP 生态系统
- 设置 `PIP_USER=0`（构建期写入 /opt/conda）
- 按分类批量 pip install（50+ 包）
- 升级 JupyterLab>=4.4 + notebook>=7.3（main 环境，继承自基础镜像）
- 使用 `--mount=type=cache` 缓存 conda/pkgs 和 pip cache
- 清理 conda/pip 缓存
- 安装后验证包版本

### Stage 3/3: Jupyter 内核 + 元数据 + 验证
- 注册 "Python 3 (AI Dev)" Jupyter 内核
  - 注册位置：`/opt/conda/envs/main/share/jupyter/kernels/ai-dev/`（main 环境 Jupyter 服务可见）
  - 内核 argv：`/opt/conda/bin/python -m ipykernel_launcher`
  - 内核 env：PATH 优先 conda，OpenMP 配置
- 写入 `/etc/devcontainer-variant-ai-dev-build-info`
- 8 项验证检查
- 输出 BUILD TIMING SUMMARY 表
- 恢复 `PIP_USER=1`

## Jupyter 内核说明

内核注册于 main 环境 kernels 目录（Jupyter 服务运行于 main 环境，supervisord 以绝对路径 `/opt/conda/envs/main/bin/jupyter` 启动）：

1. `/opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json` — main 环境 Jupyter 服务真实搜索路径（UI/CLI 一致）

内核配置：
- `display_name`: "Python 3 (AI Dev)"
- `argv`: `/opt/conda/bin/python -m ipykernel_launcher -f {connection_file}`
- `env.PATH`: `/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
- 不设置项目特定的 PYTHONPATH（通用内核）

## PIP_USER 构建/运行时分离

- **构建期（Stage 2）**: `PIP_USER=0`，pip 包写入 `/opt/conda`（root:root 属主，全局可读）
- **运行时（Stage 3 后）**: `PIP_USER=1`，支持 `pip install --user` 到 `~/.local`
- 此模式防止构建期包误写入 `/root/.local` 导致运行时 devuser 无法 import

## 服务继承

- SSH (sshd): 端口 22 ✓
- Docker DinD: `/var/run/docker.sock` ✓
- Podman: ✓
- Jupyter: `/opt/conda/envs/main/bin/jupyter`（supervisord 管理，main 环境）✓
- Supervisord: ✓

## build-info 路径

`/etc/devcontainer-variant-ai-dev-build-info`

包含字段：BUILD_DATE, VARIANT, BASE_IMAGE, PYTHON_VERSION, PYTORCH_VERSION, ONNX_VERSION, ONNXRUNTIME_VERSION, TRANSFORMERS_VERSION, DATASETS_VERSION, FASTAPI_VERSION, PANDAS_VERSION, JUPYTERLAB_VERSION, NOTEBOOK_VERSION, CONDA_DIR, PACKAGES_COUNT, JUPYTER_KERNEL, SERVICES_PRESERVED, OPENMP_CONFIG 等。

## 禁止事项

- 不覆盖 ENTRYPOINT/CMD/WORKDIR/USER/VOLUME/EXPOSE
- 不修改基础镜像的 supervisord/sshd/docker 配置
- 不重命名 devuser（保持基础镜像用户策略）
- 不设置项目特定的 PYTHONPATH
- 不安装 GPU 相关包（CPU-only 变体）
