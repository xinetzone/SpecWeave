# ai-dev 变体 Dockerfile 规范

## 基础信息

- **基础镜像**: `devcontainer-base:torch-dev-${BASE_TAG}`
- **继承链**: devcontainer-base → conda-llvm → onnx-dev → onnx-quantized → torch-dev → **ai-dev**（6层）
- **双环境架构**:
  - **base 环境**（`/opt/conda`，标准 Python，GIL **启用**）：承载 47 个 AI/ML/NLP 生态包，默认 `python` 指向此环境
  - **main 环境**（`/opt/conda/envs/main`，Python 3.14.6 cp314t **free-threading**，GIL **禁用**）：PyTorch CUDA + ONNX量化栈 + G-M1 torch依赖包（onnx2torch/open_clip_torch/sentence-transformers，继承自 torch-dev）
- **PATH 优先级**: `/opt/conda/bin:${PATH}`（base 环境在前，刻意覆盖 torch-dev 的 main 在前设置）
- **默认 Python**: `/opt/conda/bin/python`（base 环境，GIL 启用）
- **PyTorch Python**: `/opt/conda/envs/main/bin/python`（main 环境，free-threading，CUDA 可用）
- **/opt/venv**: 已在 onnx-dev 变体链中移除，不存在
- **Jupyter 服务**: `/opt/conda/envs/main/bin/jupyter`（supervisord 以绝对路径启动，运行于 main 环境）

## 核心组件

### base 环境安装的包（GIL 启用，47 包，G1-G14分组）

| 分组 | 包 | 说明 |
|------|-----|------|
| G1: Build Tools | scikit-build-core, nuitka, invoke, build | Python 包构建与编译 |
| G2: Core Utilities | decorator, attrs, cloudpickle, typing_extensions, pytest, psutil | 基础工具库 |
| G3: Jupyter Ecosystem | ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3 | Jupyter 生态（装于 base 供内核使用；服务运行于 main） |
| G4: Data Processing | pyarrow, pandas, scikit-learn, natsort | 数据分析栈 |
| G5: NLP/Transformers | datasets, transformers, sentencepiece, evaluate, tiktoken | HuggingFace 生态（**sentence-transformers 依赖 torch，移至 main G-M1**） |
| G6: Visualization/CLI | matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich | 图表与终端美化 |
| G7: AI/ML Utilities | einops, numba | 张量操作/编译加速（**open_clip_torch 依赖 torch，移至 main G-M1**） |
| G8: Audio Processing | librosa | 音频分析（soundfile/audioread/resampy 作为依赖自动安装） |
| G9: Chinese NLP | jieba, nltk, pypinyin | 中文分词/拼音/NLTK数据 |
| G10: Document Processing | PyMuPDF(fitz), EbookLib, beautifulsoup4, openpyxl | PDF/EPUB/HTML/Excel 文档解析 |
| G11: Web/API Stack | pydantic, fastapi, uvicorn, httpx>=0.28 | 异步 Web 框架 |
| G12: Serialization/Config | toml, typer, xmltodict, pyyaml | 配置文件/CLI框架 |
| G13: Database Clients | psycopg2-binary, pymongo, elasticsearch, minio | PostgreSQL/MongoDB/ES/MinIO 客户端 |
| G14: Developer Tools | icecream | 调试打印工具 |

### main 环境继承的包（来自 torch-dev，free-threading cp314t）

| 分类 | 包 | 说明 |
|------|-----|------|
| PyTorch 核心（继承自torch-dev） | torch, torchvision | cp314t free-threading，CUDA cu130/cu128/cpu |
| ONNX 生态（继承自torch-dev） | onnx, onnxruntime | 模型格式与推理引擎 |
| ONNX 工具（继承自torch-dev） | onnx-simplifier, onnxscript | 模型简化与脚本化 |
| 量化工具（继承自torch-dev） | onnxruntime.quantization, onnxconverter-common | INT8/FP16 量化 |
| **G-M1: PyTorch 生态（本层新增）** | **onnx2torch, open_clip_torch, sentence-transformers** | **依赖 torch 的包（install_requires 含 torch），安装于 main 环境与 torch 同处** |
| 编译工具链（继承自conda-llvm） | LLVM 22.1.8, clang, cmake, ninja | 继承自 conda-llvm |

### 显式排除

- **onnxoptimizer**: free-threading 不兼容（CPython #111506），继承自 onnx-quantized 约束
- **torch/torchvision 不装在 base**: 只在 main 环境存在；**任何声明 `install_requires: torch` 的包都必须安装在 main 环境 G-M1 组**（已识别：onnx2torch, open_clip_torch, sentence-transformers）

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
| PATH | /opt/conda/bin:${PATH} | **base 环境 conda 工具优先**（刻意覆盖 torch-dev 的 main 在前） |
| OMP_NUM_THREADS | 4 | OpenMP 线程数 |
| OPENBLAS_NUM_THREADS | 1 | OpenBLAS 线程数 |
| OMP_WAIT_POLICY | PASSIVE | OpenMP 等待策略 |
| KMP_DUPLICATE_LIB_OK | TRUE | 允许 OpenMP 多副本共存 |
| PIP_USER | 1（运行时） | 构建期设为 0，运行时恢复为 1 支持用户级 pip 安装 |

## Stage 结构（3 层追加）

### Stage 1/3: 基础验证 + 双环境预检

- 计时器初始化 `variant_timer_start "ai-dev"`
- 验证 main 环境（free-threading）继承自 torch-dev：
  - torch + torchvision 可导入
  - onnxruntime.quantization 量化 API 可用
  - GIL 禁用（`sys._is_gil_enabled() is False`）
- 验证 base 环境（GIL）预检：
  - GIL 启用（`sys._is_gil_enabled() is True`）
  - `/opt/conda/bin/python` 可执行
- 注意：**Framework 已由上游 torch-dev 层 COPY 到 /usr/local/share/variant-framework/，不需要重复 COPY**

### Stage 2/3: 安装 AI/ML/NLP 生态系统（base 环境 G1-G14 + main 环境 G-M1）

- 设置 `variant_activate_base_env`（激活 base 环境 + `PIP_USER=0` 构建期写入全局）
- pip 升级：`pip install --no-cache-dir --upgrade pip setuptools wheel`
- 按 G1-G14 分组使用 `pip_install_group` 在 **base 环境**安装 47 个包（每组 3-8 个包，独立计时+冲突诊断）
- **切换到 main 环境**（`variant_activate_main_env`）前的 Rust/编译环境配置（G-M1源码编译必需）：
  1. 设置 Rust 镜像源（rsproxy.cn）加速 Rust toolchain 下载（maturin构建safetensors/tokenizers需要）
  2. 配置 clang/clang++ 作为 C/C++ 编译器（conda 环境中无 gcc，需用 conda 安装的 clang）
  3. 创建 cc→clang 和 c++→clang++ 符号链接（Rust cc-rs crate 默认查找 cc/c++）
  4. 设置 CC=clang, CXX=clang++ 环境变量
- **切换到 main 环境**（`variant_activate_main_env`），使用 `pip_install_group --verbose` 安装 G-M1 组（onnx2torch + open_clip_torch + sentence-transformers）：
  - **为什么用 `--verbose`？** safetensors/tokenizers 没有 cp314t prebuilt wheel，需要 Rust+maturin 源码编译，verbose 模式输出：
    - 安装前环境诊断（Python ABI/编译器/Rust版本）
    - pip -v 详细输出（wheel检测/编译进度/cargo build日志）
    - 安装后逐个包import验证+版本打印
  - 这三个包都声明 `install_requires: torch`，必须安装在 main 环境与 torch 同处，否则 pip 会自动拉取 GIL 版 torch 到 base 破坏双环境隔离
- 切回 base 环境（`variant_activate_base_env`）执行清理
- 使用 `--mount=type=cache,target=/root/.cache/pip,sharing=locked` 缓存 pip 下载
- 安装后执行：
  - `ensure_all_permissions`：修复 devuser 权限
  - `cleanup_binaries`：清理冗余二进制
  - `cleanup_pycache`：清理 Python 缓存
  - `cleanup_conda_pip_cache`：清理包缓存
  - `pip check`：依赖冲突检查（前5行输出）
- 版本汇总：分两段输出
  - base 环境版本：使用 importlib 输出核心包版本（注意模块名↔包名映射：sklearn→scikit-learn, fitz→PyMuPDF）
  - main 环境版本：输出 torch/torchvision/onnx2torch/open_clip/sentence-transformers 版本

### Stage 3/3: Jupyter 内核注册 + 元数据 + 双环境验证

- 设置 `set +o pipefail`（防止某些验证命令的管道非零退出导致构建失败）
- 注册 "Python 3 (AI Dev)" Jupyter 内核：
  - 目标路径：`/opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json`
  - argv：`/opt/conda/bin/python -m ipykernel_launcher -f {connection_file}`（base 环境 python）
  - env.PATH：`/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
  - env.OMP_NUM_THREADS/KMP_DUPLICATE_LIB_OK：OpenMP 配置
  - 权限：chown devuser:devuser + chmod 644
- `variant_write_build_info` 写入构建元数据：
  - VARIANT_DESCRIPTION, ARCHITECTURE（dual-env）
  - PYTHON_BASE_VERSION/PYTHON_MAIN_VERSION（双环境版本）
  - PYTORCH_VERSION/TORCHVISION_VERSION（来自 main 环境）
  - ONNX2TORCH_VERSION/OPEN_CLIP_VERSION（来自 main 环境 G-M1）
  - TRANSFORMERS_VERSION/DATASETS_VERSION/FASTAPI_VERSION/PANDAS_VERSION 等（来自 base 环境）
  - JUPYTERLAB_VERSION（来自 main 环境）
  - JUPYTER_KERNEL 信息, PACKAGES_COUNT/GROUPS
  - PATH_PRIORITY, BASE_VARIANT, TORCH_IN_BASE=false
- `cleanup_all`：统一清理
- 双环境验证（9 项检查）：
  1. NLP 栈导入（transformers/datasets/evaluate；sentence-transformers 在 main 环境，不在 base）
  2. Web/API 栈导入（fastapi/uvicorn/pydantic/httpx）
  3. 数据栈导入（pandas/pyarrow/sklearn）
  4. 可视化/CLI栈导入（matplotlib/seaborn/rich/typer）
  5. 中文NLP导入（jieba/nltk/pypinyin）
  6. 文档处理导入（fitz/bs4/openpyxl）
  7. 数据库客户端导入（psycopg2/pymongo/elasticsearch/minio）
  8. 构建/开发工具导入（nuitka/pytest/psutil/icecream）
  9. 双环境 GIL 架构 + torch 隔离验证：
     - main 环境：torch+torchvision 导入、量化API、onnx2torch+open_clip+sentence-transformers导入、GIL禁用
     - base 环境：GIL启用、torch NOT present（双环境隔离守卫）
- `verify_base_services`：验证 SSH/Docker/Supervisord 基础服务未被破坏
- JupyterLab 版本检查（>=4.4）
- 内核文件存在检查 + devuser 双环境访问权限验证
- `variant_timer_summary` 输出构建阶段计时
- 最终恢复 `ENV PIP_USER=1`（运行时支持用户级安装）

## Jupyter 内核说明

内核注册于 **main 环境** kernels 目录（因为 Jupyter 服务运行于 main 环境，由 supervisord 以绝对路径 `/opt/conda/envs/main/bin/jupyter` 启动）：

```
/opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json
```

内核配置：
- `display_name`: "Python 3 (AI Dev)"
- `argv[0]`: `/opt/conda/bin/python`（指向 base 环境 Python，47个包可用）
- `env.PATH`: `/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`
- 不设置项目特定的 PYTHONPATH（通用开发内核）

**重要**：此内核在 Jupyter 中无法直接 import torch（torch 在 main 环境而非 base）。需要使用 PyTorch 时：
- 方案 A：用绝对路径 `/opt/conda/envs/main/bin/python` 启动脚本
- 方案 B：在 Notebook 中通过 `sys.path` 操作或 subprocess 调用 main 环境 python
- 方案 C：下游需要在 Jupyter 中直接使用 torch 时，可另行注册指向 main 环境的专属内核

## PIP_USER 构建/运行时分离

- **构建期（Stage 2）**: `variant_activate_base_env` 内部设置 `PIP_USER=0`，pip 包写入 `/opt/conda`（root:root 属主，全局可读）
- **运行时（Stage 3 结束）**: Dockerfile 末尾 `ENV PIP_USER=1`，支持 `pip install --user` 到 `~/.local`
- 此模式防止构建期包误写入 `/root/.local` 导致运行时 devuser 无法 import
- 新增 pip install 步骤必须在 `variant_activate_base_env` 之后执行

## 双环境 GIL 守卫与 torch 隔离（测试 T26-T29）

测试脚本必须包含双环境架构守卫，防止后续修改意外破坏架构：
- T26: base 环境 GIL 必须启用（`sys._is_gil_enabled() is True`）
- T27: main 环境 GIL 必须禁用（`sys._is_gil_enabled() is False`）
- T28: base 环境 torch 必须不存在（`importlib.util.find_spec('torch') is None`）—— **所有 torch 依赖包（onnx2torch/open_clip_torch/sentence-transformers）必须装在 main 环境**
- T29: main 环境 torch 生态（torch+torchvision+onnx2torch+open_clip+sentence-transformers）必须可导入且 GIL 禁用

### torch 依赖包识别规则

**判定标准**：包的 `install_requires` 中包含 `torch` 或 `torchvision` 声明。

**已识别的 torch 依赖包清单**（必须安装在 main 环境 G-M1 组）：
| 包 | install_requires 中的 torch 声明 | 备注 |
|----|----------------------------------|------|
| onnx2torch | 显式依赖 torch | ONNX→PyTorch 转换 |
| open_clip_torch | 显式依赖 torch | CLIP 模型实现 |
| sentence-transformers | `torch>=1.11.0` | 句向量模型（2026-08-16 修复时新发现） |

**新增包检查流程**：
1. 安装新包前先查 `pip show <pkg> | grep Requires` 是否包含 torch
2. 或在 base 环境试装：若 pip 自动下载 torch 则说明有隐式 torch 依赖
3. 确认依赖 torch 的包一律移至 main 环境 G-M1 组安装

## Rust 源码编译环境要求（cp314t free-threading）

由于 Python 3.14.6 cp314t（free-threading）生态尚不成熟，部分包（safetensors、tokenizers、huggingface-hub 等）没有预编译 wheel，需要 Rust+maturin 源码编译。构建 main 环境 G-M1 组前必须：

1. **Rust 镜像源配置**：`RUSTUP_DIST_SERVER=https://rsproxy.cn`、`RUSTUP_UPDATE_ROOT=https://rsproxy.cn/rustup`（国内加速 Rust toolchain 下载）
2. **C/C++ 编译器配置**：使用 conda 安装的 clang/clang++（无 gcc），设置 `CC=clang`、`CXX=clang++`
3. **符号链接**：创建 `cc→clang`、`c++→clang++`（Rust cc-rs crate 默认查找 cc/c++）
4. **日志详细度**：使用 `pip_install_group --verbose` 启用安装前环境诊断+编译详细输出+安装后逐个包验证，方便排查编译问题

## 服务继承

- SSH (sshd): 端口 22 ✓
- Docker DinD: `/var/run/docker.sock` ✓
- Podman: ✓
- Jupyter: `/opt/conda/envs/main/bin/jupyter`（supervisord 管理，main 环境）✓
- Supervisord: ✓

## build-info 路径

`/etc/devcontainer-variant-ai-dev-build-info`

包含字段：BUILD_DATE, VARIANT, BASE_IMAGE（=devcontainer-base:torch-dev-${BASE_TAG}）, ARCHITECTURE, PYTHON_BASE_VERSION, PYTHON_MAIN_VERSION, PYTORCH_VERSION, TORCHVISION_VERSION, TRANSFORMERS_VERSION, DATASETS_VERSION, FASTAPI_VERSION, PANDAS_VERSION, JUPYTERLAB_VERSION, JUPYTER_KERNEL, PACKAGES_COUNT, PACKAGES_GROUPS, PATH_PRIORITY, BASE_VARIANT 等。

## 禁止事项

- 不覆盖 ENTRYPOINT/CMD/WORKDIR/USER/VOLUME/EXPOSE
- 不修改基础镜像的 supervisord/sshd/docker 配置
- 不重命名 devuser（保持基础镜像用户策略）
- 不设置项目特定的 PYTHONPATH
- 不安装 GPU 相关包到 base 环境（CUDA 相关包只在 main 环境，由 torch-dev 管理）
- 不在 base 环境直接 pip install torch（torch 只存在于 main 环境）
- 不在 base 环境安装声明 `install_requires: torch` 的包（如 onnx2torch, open_clip_torch, sentence-transformers）——这类包必须在 main 环境安装，防止 pip 自动拉取 GIL 版 torch 到 base 破坏双环境隔离
- 不重复 COPY variant-framework（已由 torch-dev 层提供）
- 不删除或修改 main 环境的 torch/onnx 包
