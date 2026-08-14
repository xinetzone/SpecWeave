# DevContainer Base - 标准化开发容器基础镜像 (SSH + Docker + Podman + Jupyter)

> 基于 Ubuntu 26.04 的企业级全功能开发容器基础镜像，集成 OpenSSH Server、Docker DinD/DooD、Podman rootless 和 Jupyter Notebook/Lab 四大核心服务，通过 supervisord 统一进程管理，支持环境变量动态服务启停。

## ✨ 特性

- **基础环境**：Ubuntu 26.04 固定标签、中文 locale zh_CN.UTF-8、Asia/Shanghai 时区、Miniforge3 (conda-forge) + Python 3.14.6 free-threading (cp314t，GIL默认禁用，libmamba求解器)
- **四大服务**：SSH(22) + Docker DinD(2375) + Podman(rootless) + JupyterLab(8888)，可独立启停
- **GIL可选**：默认cp314t无GIL构建支持真正多线程并行；`PYTHON_GIL=1`可启用GIL兼容模式；构建时`--python-build cp314`可选标准GIL构建
- **进程管理**：Supervisord 统一管理，服务自动重启、优先级调度
- **双容器运行时**：
  - Docker DinD 模式（--privileged，完全隔离）
  - Docker DooD 模式（挂载宿主 docker.sock，无需特权）
  - Podman rootless 模式（按需启动，无守护进程）
- **安全增强**：非 root 用户 devuser(UID 1000)、可选 NOPASSWD sudo、SSH ED25519 密钥、Jupyter Token/密码认证
- **灵活配置**：环境变量驱动、支持国内镜像源、运行时动态配置
- **多阶段构建**：7阶段单镜像构建、BuildKit缓存挂载（apt/pip/conda/libmamba）、激进清理策略、最小化镜像
- **健康检查**：内置 HEALTHCHECK，按启用服务条件化检查
- **可组合性**：每个服务可独立启用/禁用，适合作为各类开发容器的 base image

## 🏗️ 项目结构

```
devcontainer-base/
├── Dockerfile                      # 主构建文件（多阶段构建，Python 3.14 cp314t）
├── entrypoint.sh                   # 容器启动脚本（服务动态启停）
├── docker-compose.yml              # Compose 编排（3种profile）
├── docker-compose.ide.yml          # IDE Jupyter桥接模式专用Compose
├── .dockerignore                   # Docker 构建忽略文件
├── .env.example                    # 环境变量模板
├── .env.ide.example                # IDE桥接模式环境变量模板
├── CHANGELOG.md                    # 版本变更日志
├── AGENTS.md                       # AI 协作者规范（SpecWeave）
├── conda-lock/                     # Conda 环境精确版本锁定
│   ├── environment.yml             # Python 3.14.6 cp314t 锁定模板
│   └── generate-locks.sh           # 锁文件生成/验证/安装脚本
├── config/
│   ├── supervisord.conf            # Supervisord 主配置
│   ├── sshd_config                 # SSH 服务完整配置
│   ├── jupyter_notebook_config.py  # Jupyter 基础配置
│   └── supervisor/
│       └── conf.d/
│           ├── sshd.conf           # SSH 进程配置
│           ├── dockerd.conf        # Docker daemon 进程配置
│           └── jupyter.conf        # Jupyter 进程配置
├── scripts/
│   ├── build.sh                    # 一键构建脚本（支持--cn/--verify）
│   ├── start.sh                    # 一键启动脚本（健康验证+连接信息）
│   ├── run-jupyter-ide.sh          # IDE Jupyter桥接一键启动脚本
│   ├── local-build.sh              # 本地WSL2构建脚本（变体依赖链）
│   ├── healthcheck.sh              # 容器健康检查脚本（条件化检测）
│   ├── verify-deployment.py        # 部署验证脚本（多维度检查）
│   ├── verify-services.sh          # 服务验证脚本
│   ├── ci-requirements.txt         # CI环境Python依赖清单
│   ├── ci_quantization_gate.py     # CI量化门禁（精度阈值+基准测试）
│   ├── lib/
│   │   └── logging.sh              # 日志工具库
│   ├── onnx_quantize_kit/          # ONNX量化工具包（onnxruntime.quantization封装）
│   │   ├── __init__.py             # 公开API导出
│   │   ├── quantize.py             # 高层量化API（auto_quantize+各量化方法）
│   │   ├── accuracy.py             # 精度验证
│   │   ├── benchmark.py            # 性能基准测试
│   │   ├── calibration.py          # 校准数据读取器
│   │   ├── model_detect.py         # 模型类型自动检测
│   │   ├── cli.py                  # 命令行接口
│   │   └── reporting.py            # 报告生成
│   ├── test_quantize_kit.py        # onnx_quantize_kit单元测试
│   ├── test_onnxruntime_quantization.py  # ORT量化API单元测试
│   ├── test_ort_quantization_regression.py # ORT回归测试（G1-G11）
│   ├── test_neural_compressor.py   # Neural Compressor兼容性测试（可选）
│   ├── benchmark_quantization.py   # 量化性能基准对比
│   ├── batch_quantize.py           # 批量量化脚本
│   ├── onnx-quantize.py            # ONNX量化命令行工具
│   ├── compare_qdq_vs_qoperator.py # QDQ vs QOperator格式对比
│   ├── run_full_benchmark.py       # 完整基准测试套件
│   ├── analyze_benchmark.py        # 基准测试结果分析
│   ├── analyze-diagnostics.py      # 10维诊断解析器
│   ├── ci_alert.py                 # CI告警工具
│   ├── models/                     # 测试用ONNX模型（cnn/mlp/transformer）
│   ├── QUICKSTART.md               # 量化工具包快速入门
│   └── EXERCISES.md                # 量化练习材料
├── docs/                           # 文档目录
│   ├── best-practices.md           # Docker DinD/Compose/镜像源最佳实践
│   ├── IDE-JUPYTER-BRIDGE.md       # IDE Jupyter桥接模式使用指南（VSCode/Trae）
│   ├── examples/                   # 配置示例归档
│   │   └── ide-bridge/             # IDE桥接模式已验证配置归档（Compose+env+脚本）
│   ├── RELEASE-v2.md               # v2.2 详细发布说明
│   ├── v2.2-build-pipeline-optimization.md  # v2.2 构建流水线优化方案
│   ├── PY314T-C-EXTENSION-GUIDE.md # Python 3.14t C 扩展编译指南
│   ├── CONDA-PERF-INTEGRATION-GUIDE.md  # Conda 性能优化集成指南
│   └── TECH-ADVISORY-defaults-channel-abi-risk.md  # defaults channel ABI 风险公告
├── examples/                       # 示例代码
│   └── free_threading_demo.py      # Free-threading 多线程性能演示
├── templates/                      # 可复用模板
│   └── cmake-cext/                 # CMake C 扩展标准模板
└── variants/                       # 镜像变体系列（按依赖链排列）
    ├── AGENTS.md                   # 变体管理AI协作者入口
    ├── README.md                   # 变体索引和使用指南
    ├── build.sh                    # 变体统一构建脚本（拓扑排序+计时+验证）
    ├── _template/                  # 新变体模板
    ├── conda/                      # 镜像源配置+验证（Miniforge3/Python已在base中）
    ├── conda-llvm/                 # conda+LLVM/clang编译工具链变体
    ├── onnx-pytorch/               # PyTorch CPU+ONNX Runtime深度学习运行时
    ├── onnx-quantized/             # ONNX量化工具链（INT8/FP16）
    ├── ai-dev/                     # 全栈AI/ML/NLP生态+JupyterLab4.x
    ├── shared/                     # 变体间共享组件
    │   ├── lib/logging.sh          # 结构化日志库
    │   └── scripts/conda-mirror-setup.sh  # conda/pip镜像源配置
    └── scripts/                    # 单变体辅助脚本
        ├── build-conda-llvm.sh     # conda-llvm一键构建
        ├── build-onnx-pytorch.sh   # onnx-pytorch一键构建
        ├── test-conda-llvm.sh      # conda-llvm测试
        ├── test-onnx-pytorch.sh    # onnx-pytorch测试（20项）
        ├── test-onnx-quantized.sh  # onnx-quantized测试
        └── test-timer-parser.sh    # [TIMER]解析单元测试
```

## 🚀 快速开始

### 构建镜像

```bash
# 方式1：直接 docker build
docker build -t devcontainer-base:conda-libmamba-v2 .

# 方式2：使用构建脚本（推荐，含日志+预检+冒烟测试）
bash scripts/build.sh

# 使用国内镜像源（apt/pip/docker加速，conda使用official源保证稳定性）
bash scripts/build.sh --apt-mirror aliyun --pip-mirror aliyun --docker-mirror aliyun --conda-mirror official --network-host

# 构建并运行快速冒烟测试（自动验证Python 3.14+libmamba等核心功能）
bash scripts/build.sh --test

# 跳过缓存重新构建
bash scripts/build.sh --no-cache

# 自定义标签
bash scripts/build.sh -t my-tag
```

**构建脚本特性**：
- 📝 **详细日志**：`--progress=plain` 输出完整构建过程，日志自动保存至 `logs/builds/`
- ✅ **构建前预检**：6项检查（Docker运行状态/BuildKit/磁盘空间/缓存/配置摘要）
- 🌐 **多镜像源支持**：APT/PyPI/Docker CE/Conda 均可独立切换镜像源（aliyun/tuna/official）
- 🔧 **网络模式**：`--network-host` 使用host网络解决国内下载问题
- 🧪 **冒烟测试**：构建后自动启动容器验证Python版本、libmamba求解器、pip等7项核心功能
- 🚨 **错误捕获**：构建失败时自动输出最后50行日志和排查建议

### Docker Compose（推荐）

提供 3 种 profile 适应不同场景：

```bash
# DinD模式：Docker-in-Docker（推荐，完全隔离，需--privileged）
docker compose --profile dind up -d

# DooD模式：Docker-out-of-Docker（使用宿主Docker，无需特权）
docker compose --profile dood up -d

# 仅SSH模式：最小化，无Docker/Jupyter
docker compose --profile ssh-only up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

### IDE Jupyter 桥接模式（宿主机 VSCode/Trae 连接容器 Kernel）

将容器内 Jupyter Kernel 暴露给宿主机 IDE 使用，UI 在宿主机、执行在容器，轻量无需 Dev Containers 扩展：

```bash
# 一键启动（推荐，含健康检查+连接引导）
bash scripts/run-jupyter-ide.sh

# 或使用专用 Compose 文件
cp .env.ide.example .env
docker compose -f docker-compose.ide.yml up -d
```

启动后在 IDE 中连接：
1. `Ctrl+Shift+P` → **Jupyter: Specify Jupyter Server for Connections**
2. 选择 **Existing** → 输入 `http://localhost:8888/?token=devtoken123`
3. 打开 `.ipynb` → 选择 Python 3 kernel

⚠️ **关键配置**：必须设置 `JUPYTER_ALLOW_ORIGIN=*`（IDE WebView CORS 需要），docker-compose.ide.yml 和 run-jupyter-ide.sh 已默认配置。

> 详细使用指南见 [docs/IDE-JUPYTER-BRIDGE.md](docs/IDE-JUPYTER-BRIDGE.md)。

### 手动运行容器

#### DinD模式（Docker-in-Docker，推荐用于开发环境）

```bash
docker run -d \
  --name devcontainer \
  --privileged \
  -p 2222:22 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=your_password \
  -e JUPYTER_TOKEN=your_token \
  -e GRANT_SUDO=yes \
  devcontainer-base:conda-libmamba-v2
```

⚠️ **注意**: DinD模式必须使用 `--privileged`，否则Docker守护进程无法启动。

#### DooD模式（Docker-out-of-Docker，生产/CI环境）

```bash
docker run -d \
  --name devcontainer-dood \
  -p 2223:22 \
  -p 8889:8888 \
  -v $(pwd)/workspace:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e USER_PASSWORD=your_password \
  -e JUPYTER_TOKEN=your_token \
  devcontainer-base:conda-libmamba-v2
```

DooD模式无需 `--privileged`，容器内 docker 命令直接操作宿主Docker。entrypoint 会自动检测宿主 socket 并禁用内部 dockerd。

#### 命令模式（调试/一次性任务）

```bash
docker run -it --rm devcontainer-base:conda-libmamba-v2 bash
```

### 构建镜像变体

基础镜像之上提供了一系列功能变体，按依赖链构建：

```
base (Ubuntu 26.04 + SSH + Docker + Podman + Jupyter + Miniforge3 + Python 3.14.6 cp314t free-threading)
  ↓
conda (镜像源配置 + 验证，Miniforge3已在base中)
  ↓
conda-llvm (LLVM/Clang 22.1.8 + CMake + Ninja via conda-forge)
  ↓
onnx-pytorch (PyTorch CPU + ONNX Runtime 1.28.0)
  ↓
onnx-quantized (onnxruntime.quantization 量化工具链: INT8/FP16)
  ↓
ai-dev (全栈AI/ML/NLP生态50+包 + JupyterLab4.x + AI内核)
```

```bash
# 构建所有变体（按依赖顺序，国内源加速）
bash variants/build.sh --all --cn

# 构建单个变体
bash variants/build.sh --variant onnx-quantized --cn

# 列出可用变体
bash variants/build.sh --list
```

| 变体 | 说明 | 核心组件 |
|------|------|---------|
| conda | 镜像源配置 + 基础验证（Miniforge3已在base中） | conda, libmamba, conda/pip镜像源配置 |
| conda-llvm | 编译工具链 | LLVM 22.1.8, Clang, CMake, Ninja |
| onnx-pytorch | 深度学习运行时 | PyTorch CPU, ONNX Runtime, onnxsim |
| onnx-quantized | 模型量化工具链 | onnxruntime.quantization, FP16/INT8, onnx_quantize_kit, Neural Compressor |
| ai-dev | 全栈AI/ML/NLP开发环境 | transformers, datasets, fastapi, pandas, JupyterLab4.x, AI内核 |

> 详细变体文档见 [variants/README.md](variants/README.md) 和 [variants/AGENTS.md](variants/AGENTS.md)。

### ONNX 量化工具包（onnx_quantize_kit）

`scripts/onnx_quantize_kit/` 提供基于 `onnxruntime.quantization` 的高层量化API：

```python
from onnx_quantize_kit import auto_quantize, quantize_dynamic_simple, quantize_fp16

# 自动选择最优量化策略（根据模型类型MLP/CNN/Transformer）
result = auto_quantize("model.onnx", "model_quantized.onnx", calib_reader=...)
print(f"Strategy: {result.strategy_used}, Accuracy: {result.accuracy.cosine_sim:.4f}")

# 一行动态量化
quantize_dynamic_simple("model.onnx", "model_int8.onnx")

# FP16转换
quantize_fp16("model.onnx", "model_fp16.onnx")
```

支持：动态INT8量化、静态QDQ/QOperator量化、FP16半精度转换、自动策略选择、精度验证、性能基准。详细文档见 [scripts/QUICKSTART.md](scripts/QUICKSTART.md)。

## 🔌 连接方式

> **注意**：以下端口为 `docker run` DinD示例。使用不同模式时请根据实际映射调整端口。

### SSH连接

```bash
ssh devuser@localhost -p 2222
```

### Jupyter Notebook

浏览器访问 http://localhost:8888/，使用 `JUPYTER_TOKEN` 或密码登录。

### IDE Jupyter 连接（VSCode / Trae）

容器内 Jupyter 可直接暴露给宿主机 IDE 的 Jupyter 插件使用：

```bash
# 启动IDE桥接模式（已配置CORS+端口映射+volume挂载）
bash scripts/run-jupyter-ide.sh
```

IDE 中连接步骤：
1. `Ctrl+Shift+P` → **Jupyter: Specify Jupyter Server for Connections**
2. 选择 **Existing** → 输入 `http://localhost:8888/?token=<JUPYTER_TOKEN>`
3. 打开 `.ipynb` 文件，Kernel 选择容器内 Python 3 环境

> 完整指南见 [docs/IDE-JUPYTER-BRIDGE.md](docs/IDE-JUPYTER-BRIDGE.md)。

### Docker使用

容器内SSH登录后，devuser已在docker组，直接使用docker命令：

```bash
docker ps
docker run hello-world
docker build -t myapp .
```

### Podman使用（rootless，需ENABLE_PODMAN=yes）

```bash
podman ps
podman run --rm hello-world
```

## ⚙️ 环境变量配置

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `ENABLE_SSH` | `yes` | 启用SSH服务 |
| `ENABLE_DOCKER` | `yes` | 启用Docker（DinD模式；若检测到宿主socket则自动切换DooD） |
| `ENABLE_PODMAN` | `no` | 启用Podman rootless（与Docker同开时cgroupv2可能冲突） |
| `ENABLE_JUPYTER` | `yes` | 启用Jupyter Notebook/Lab |
| `USER_PASSWORD` | *(随机生成)* | devuser用户密码 |
| `ROOT_PASSWORD` | *(不设置)* | root密码，需 `ALLOW_ROOT_SSH=yes` |
| `JUPYTER_TOKEN` | *(随机生成)* | Jupyter访问令牌 |
| `JUPYTER_PASSWORD` | *(空)* | Jupyter密码（与Token二选一） |
| `JUPYTER_ALLOW_ORIGIN` | *(空)* | Jupyter CORS允许Origin（IDE连接需设为`*`） |
| `GRANT_SUDO` | `no` | devuser免密sudo |
| `ALLOW_ROOT_SSH` | `no` | 允许root SSH登录 |
| `SSH_PUBLIC_KEY` | *(空)* | SSH公钥注入 |
| `JUPYTER_PORT` | `8888` | Jupyter端口 |
| `SSH_PORT` | `22` | SSH端口 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `APT_MIRROR` | `official` | APT源（official/aliyun/tuna）- build-arg |
| `PIP_MIRROR` | `official` | PyPI源（official/aliyun/tuna）- build-arg |
| `DEBUG` | `0` | 调试模式 |

## 🔒 安全说明

1. **非root默认用户**：devuser（UID 1000），Jupyter以非root运行
2. **SSH安全配置**：
   - ED25519密钥优先
   - 禁用root登录（默认）
   - 禁用空密码
   - 严格模式
3. **Docker socket权限控制**：DooD模式挂载为 `ro` 只读
4. **Podman rootless模式**：无守护进程、用户命名空间隔离
5. **Jupyter认证**：Token/Password认证机制
6. **运行时SSH host keys生成**：容器启动时生成，避免密钥复用
7. ⚠️ **DinD模式--privileged安全警告**：特权模式赋予容器几乎所有宿主权限，仅用于可信开发环境；生产/CI环境推荐DooD模式或Podman

## 📋 服务管理 (supervisorctl)

```bash
# 查看所有服务状态
supervisorctl status

# 重启单个服务
supervisorctl restart sshd
supervisorctl restart dockerd
supervisorctl restart jupyter

# 查看服务日志
supervisorctl tail -f dockerd
supervisorctl tail -f jupyter
```

**Note**: Podman不通过supervisord管理，为rootless按需启动，无需守护进程。

## 🏗️ 作为基础镜像使用

```dockerfile
FROM devcontainer-base:conda-libmamba-v2

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    your-package \
    && rm -rf /var/lib/apt/lists/*

# conda环境安装包（默认已激活base环境，使用libmamba solver）
RUN conda install -y your-conda-package && conda clean -yafq
# 或使用pip
RUN pip install your-pip-package && pip cache purge

USER devuser
# ENTRYPOINT保持不变，服务按环境变量自动启动
```

## 🔧 DinD vs DooD vs Podman 对比

| 特性 | DinD模式 | DooD模式 | Podman |
|------|---------|---------|--------|
| 需要--privileged | ✅ 是 | ❌ 否 | ❌ 否 |
| 容器隔离 | 完全隔离 | 共享宿主Docker | 用户命名空间隔离 |
| 性能 | 稍慢（嵌套） | 快（原生） | 快（无守护进程） |
| 安全性 | 较低（特权） | 中（共享socket） | 高（rootless） |
| 镜像持久化 | 需要volume | 宿主镜像共享 | 用户级存储 |
| docker-compose支持 | ✅ dind profile | ✅ dood profile | 手动启动 |

## 🩺 健康检查

内置 `healthcheck.sh`，条件化检查已启用服务：
- **SSH**: 端口监听检测
- **Docker**: dockerd进程 + docker.sock + docker info
- **Jupyter**: HTTP API检测（200/302/401/403为正常）

Docker HEALTHCHECK配置：
- `interval=30s`
- `timeout=10s`
- `start-period=60s`
- `retries=3`

## 🔄 CI/CD 持续集成

项目配置了两套 GitHub Actions CI 流水线：

### 1. 变体构建流水线（devcontainer-variants.yml）

- **触发条件**：PR（Lint快速检查）、main分支推送（完整构建）、Nightly定时、手动触发
- **构建矩阵**：按依赖拓扑 `base → conda → conda-llvm → onnx-pytorch → onnx-quantized → ai-dev` 顺序构建
- **验证**：每个变体构建后自动运行单元测试（20+项测试/变体），逐条PASS/FAIL报告

### 2. ONNX量化工具包CI（onnx-quantize-ci.yml）

- **触发条件**：onnx_quantize_kit代码/测试/Dockerfile/CI配置变更（push/main + PR）、每周日定时全量回归、手动触发
- **测试矩阵**：Python 3.10/3.11/3.12 多版本
- **测试阶段**：单元测试 → G1-G11回归测试 → CI量化门禁 → 性能基准（定时/手动）
- **自动门禁**：cosine_sim ≥ 0.90 精度阈值，失败阻断合并

手动触发：
```bash
# 触发变体构建
gh workflow run devcontainer-variants.yml --ref main -f variant=onnx-quantized

# 触发量化CI
gh workflow run onnx-quantize-ci.yml --ref main
```

## 📝 版本信息

- **版本**：conda-libmamba-ft (Miniforge3 + Python 3.14.6 cp314t)
- **基础镜像**：ubuntu:26.04
- **Python**：3.14.6（Miniforge3 / conda-forge, GCC 14.4.0, free-threading cp314t build, GIL默认禁用）
- **Conda发行版**：Miniforge3（conda-forge官方，无defaults channel，无Anaconda商业包）
- **Conda**：预装libmamba solver，频道: conda-forge only
- **libmambapy**：2.3.2（底层求解器库）
- **pip**：26.2.1
- **Jupyter**: JupyterLab（通过conda安装）
- **Docker CE**：官方仓库最新稳定版（支持Aliyun镜像加速）
- **Podman**：Ubuntu 26.04官方源（rootless模式）
- **OpenSSH**：Ubuntu 26.04官方包
- **Supervisor**：Ubuntu 26.04官方包
- **镜像大小**：~2.38GB
- **镜像变体**：conda, conda-llvm, onnx-pytorch, onnx-quantized, ai-dev（共5个功能变体）
- **ONNX量化工具包**：onnx_quantize_kit（基于onnxruntime.quantization原生API）

## 📄 许可证

遵循SpecWeave项目规范。

## 🤝 相关应用

- [jupyter-ssh-base](../jupyter-ssh-base/) - 基础镜像（SSH+Jupyter，无容器运行时）
- [docker-ssh-dind](../docker-ssh-dind/) - Docker DinD镜像（SSH+Docker，无Jupyter/Podman）
- [onnx-pytorch 变体](variants/onnx-pytorch/) - PyTorch CPU + ONNX Runtime 深度学习运行时
- [onnx-quantized 变体](variants/onnx-quantized/) - ONNX模型量化工具链（INT8/FP16）
- [ai-dev 变体](variants/ai-dev/) - 全栈AI/ML/NLP开发环境
