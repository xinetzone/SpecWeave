# torch-dev 变体 - Free-Threading PyTorch CUDA 开发镜像 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本目录是 devcontainer-base 变体系列的一个变体，
>         规则继承自 ../AGENTS.md（变体系列入口），后者继承自 ../../AGENTS.md（项目入口）
> 步骤 3：按上下文路由表加载变体特有规范（.agents/rules/dockerfile.md）
> 步骤 3.5：自检 — 确认已理解父级规则与本变体特有约束（尤其 main free-threading 环境、CUDA PyTorch、triton GIL 兼容问题）
> 步骤 4：在规范指导下执行任务
> ```

本文件是 torch-dev 变体（Free-Threading PyTorch CUDA 开发镜像）的 AI 协作者入口。
进入本目录的任务优先读取本文件；本文件未覆盖的规则回退到父级 [../AGENTS.md](../AGENTS.md)。

## 变体概述

| 属性 | 值 |
|------|-----|
| 变体名称 | `torch-dev` |
| 镜像标签 | `devcontainer-base:torch-dev-<TAG>`（默认 latest） |
| 基础镜像 | `devcontainer-base:onnx-quantized-${BASE_TAG}` |
| 依赖链 | base → conda-llvm → onnx-dev → onnx-quantized → **torch-dev** |
| 核心定位 | Free-Threading PyTorch CUDA 开发环境（torch 一等公民，cp314t 无 GIL，支持 CUDA 训练/推理） |
| Python 环境 | conda **main 环境**（`/opt/conda/envs/main/bin`，Python 3.14.6 cp314t **free-threading**，GIL 禁用） |
| 继承自带 | onnx、onnxruntime（含 quantization）、onnxconverter-common、onnxsim、onnxscript（来自 onnx-quantized 链） |
| 本层安装 | torch（CUDA cu130/cu128/cpu，cp314t free-threading wheel）、torchvision |
| 排除项 | onnxoptimizer（free-threading 不兼容，CPython #111506，继承自 onnx-quantized 约束） |
| Jupyter kernel | **不注册**（kernel 注册属于下游 ai-dev 变体职责） |
| 下游变体 | ai-dev（直接基础，torch 取代量化栈成为一等公民） |

## 三条核心约束（改动本变体前必读）

### 1. main 环境 free-threading 架构（继承 onnx-quantized，与 onnx-pytorch 的 base GIL 启用相反）

- 所有工具位于 conda **main 环境**（`/opt/conda/envs/main/bin`），`ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:...` 置于最前
- Python 3.14.6 **cp314t free-threading 构建**（GIL 禁用）——`sys._is_gil_enabled() is False` 必须恒成立
- 验证命令使用 `/opt/conda/envs/main/bin/python`（注意区别于 onnx-pytorch 的 `/opt/conda/bin/python`）
- 构建期双守卫：pip 安装后断言 python 构建串含 `cp314t` 且 GIL 仍禁用，否则 FATAL

### 2. CUDA PyTorch（与 onnx-pytorch 的 CPU-only 强制相反）

- **必须**通过 PyTorch CUDA 索引（`TORCH_CUDA_INDEX`，默认 `cu130`，可选 `cu128`/`cpu`）安装 torch/torchvision
- 从 `https://download.pytorch.org/whl/${TORCH_CUDA_INDEX}` 安装，cp314t free-threading wheel
- 容器运行时需 `--gpus all` 才能使用 CUDA（无 GPU 时自动 fallback 到 CPU，`torch.cuda.is_available()` 返回 False）
- triton 模块导入时会临时启用 GIL（警告信息无害），设置 `PYTHON_GIL=0` 可保持 GIL 禁用状态
- PyTorch 版本升级时只改 Stage 2，不动其他阶段

### 3. 开发容器三模式与端口自动管理

本变体提供三种启动模式，通过 [docker-compose.torch.yml](docker-compose.torch.yml) + [scripts/start-torch-dev.sh](scripts/start-torch-dev.sh) 统一管理：

- **DinD 模式**（默认）：容器内独立 Docker daemon（`--privileged`），适合隔离开发
- **DooD 模式**：共享宿主机 Docker Socket（`-v /var/run/docker.sock`），无需 privileged
- **SSH-only 模式**：仅启动 SSH，最小资源占用
- **端口冲突自动处理**：启动脚本自动检测默认端口（2226/8891）占用，+1递增寻找空闲端口，通过环境变量注入 compose（**不修改 compose 文件**，避免配置漂移）
- **验证机制**：启动后自动运行 [examples/test_torch.py](examples/test_torch.py) 综合验证（支持 `--quick` 快速模式）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则）
  └─ apps/AGENTS.md（应用区入口）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            └─ variants/AGENTS.md（变体系列入口）
                 └─ torch-dev/AGENTS.md ← 本文件（变体级入口）
                      ├─ .agents/rules/dockerfile.md   ← 本变体特有 Dockerfile 规范
                      ├─ Dockerfile                    ← 3 追加阶段构建定义
                      ├─ .env.example                 ← 构建参数模板（含 TORCH_CUDA_INDEX）
                      ├─ README.md                    ← 使用说明
                      ├─ docker-compose.torch.yml     ← Docker Compose 配置（DinD/DooD/SSH-only 三模式）
                      ├─ examples/test_torch.py       ← PyTorch + CUDA 综合验证脚本
                      └─ scripts/start-torch-dev.sh   ← 一键启动脚本（自动端口冲突检测+健康等待+验证）
```

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 修改本变体 Dockerfile | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 基础信息、PATH 优先级、CUDA PyTorch 安装、3 阶段结构、冒烟测试 |
| 启动/停止开发容器 | [scripts/start-torch-dev.sh](scripts/start-torch-dev.sh) | 一键启动脚本（`--dood`/`--ssh-only`/`--test`/`--bash`/`--stop`/`--logs`） |
| PyTorch/CUDA 验证 | [examples/test_torch.py](examples/test_torch.py) | 综合验证脚本（Python环境/free-threading/PyTorch版本/CUDA检测/算子/ONNX互操作/健康检查） |
| Docker Compose 配置 | [docker-compose.torch.yml](docker-compose.torch.yml) | 三模式服务定义、环境变量端口管理、命名卷持久化 |
| 量化操作（INT8/FP16） | [../onnx-quantized/AGENTS.md](../onnx-quantized/AGENTS.md) | 继承量化工具链，onnxruntime.quantization API 直接可用 |
| 对比 CPU-only PyTorch 变体 | [../onnx-pytorch/AGENTS.md](../onnx-pytorch/AGENTS.md) | base 环境 + GIL 启用 + CPU-only 的架构对偶 |
| 对比纯 ONNX 变体 | [../onnx-dev/AGENTS.md](../onnx-dev/AGENTS.md) | main 环境 + free-threading + torch 一等排除的架构来源 |
| 变体共享约定（FROM/SHELL/缓存挂载/验证检查点） | [../.agents/rules/variant-conventions.md](../.agents/rules/variant-conventions.md) | 所有变体必须遵循的 Dockerfile 共享约定 |
| 构建本变体 | [../build.sh](../build.sh) + [../.agents/rules/build-orchestration.md](../.agents/rules/build-orchestration.md) | `--variant torch-dev`（拓扑排序自动补齐 onnx-quantized/onnx-dev/conda-llvm 依赖） |
| 测试本变体 | [../scripts/test-torch-dev.sh](../scripts/test-torch-dev.sh) | 镜像构建冒烟测试 |
| 测试规范（分层策略） | [../.agents/rules/testing.md](../.agents/rules/testing.md) | 测试脚本编写规范 |
| 父级回退（变体系列通用规则） | [../AGENTS.md](../AGENTS.md) | 本文件未覆盖时回退 |

## 构建与验证速查

```bash
# 构建（WSL2/Linux，国内镜像源；拓扑排序自动先建 onnx-quantized 依赖链）
bash variants/build.sh --variant torch-dev --cn

# 构建（CUDA 12.8 版本）
TORCH_CUDA_INDEX=cu128 bash variants/build.sh --variant torch-dev --cn

# 构建（CPU only 版本）
TORCH_CUDA_INDEX=cpu bash variants/build.sh --variant torch-dev --cn

# 快速验证镜像（导入+版本+free-threading）
docker run --rm devcontainer-base:torch-dev-latest \
  /opt/conda/envs/main/bin/python -c "import sys,torch;print(f'Python {sys.version}');print(f'GIL disabled: {not sys._is_gil_enabled()}');print(f'torch {torch.__version__}, CUDA available: {torch.cuda.is_available()}')"

# 一键启动（默认 DinD 模式，自动端口冲突检测+健康等待+自动验证）
bash variants/torch-dev/scripts/start-torch-dev.sh

# 一键启动（自定义端口）
bash variants/torch-dev/scripts/start-torch-dev.sh -p 2300 -P 8900

# 一次性 GPU 验证（--rm 自动删除）
bash variants/torch-dev/scripts/start-torch-dev.sh --test

# 停止容器
bash variants/torch-dev/scripts/start-torch-dev.sh --stop

# 容器内手动运行完整验证
docker exec -it torch-dev /opt/conda/envs/main/bin/python /workspace/examples/test_torch.py
```

## 已知设计决策记录

| 决策 | 理由 | 日期 |
|------|------|------|
| 基于 onnx-quantized 而非 onnx-pytorch | 继承 free-threading main 环境（cp314t）与 ONNX 量化工具链；torch-dev 需要无 GIL 的 PyTorch 以支持多核并行推理，onnx-pytorch 的 base 环境 GIL 启用不符合目标 | 2026-08-15 记录 |
| CUDA 索引默认 cu130 | PyTorch 最新稳定 CUDA 版本；cu128/cpu 通过 TORCH_CUDA_INDEX 构建参数可选 | 2026-08-15 记录 |
| Jupyter kernel 不注册 | kernel 注册属于下游 ai-dev 变体职责（多内核管理），torch-dev 仅启动 JupyterLab 服务不注册自定义 kernel | 2026-08-15 记录 |
| onnxoptimizer 继续排除 | 继承 onnx-quantized 的 free-threading 约束（CPython #111506），torch 不依赖 onnxoptimizer，无回拉风险 | 2026-08-15 记录 |
| 端口通过环境变量管理而非修改 compose | docker-compose.torch.yml 中使用 `${SSH_PORT:-2226}` 动态端口，启动脚本自动检测冲突并注入环境变量，避免修改配置文件导致的配置漂移 | 2026-08-16 记录 |
| triton GIL 警告视为无害 | triton 模块导入时临时启用 GIL 是已知行为（triton 未声明 free-threading 兼容），设置 `PYTHON_GIL=0` 可强制保持 GIL 禁用，不影响功能 | 2026-08-16 验证 |
| 命名卷持久化 Docker 存储和 Conda 缓存 | DinD 模式下 `/var/lib/docker` 和 `/opt/conda/pkgs` 使用命名卷，避免容器重建后镜像和包缓存丢失 | 2026-08-16 记录 |
| start-torch-dev.sh 支持三模式 | DinD（隔离开发）、DooD（共享宿主机Docker）、SSH-only（最小化）覆盖不同使用场景，单一脚本统一管理 | 2026-08-16 记录 |

## triton GIL 警告说明

导入 PyTorch 时可能出现以下警告：

```
<frozen importlib._bootstrap>:491: RuntimeWarning: The global interpreter lock (GIL) has been enabled to load module 'triton._C.libtriton'
```

这是**预期行为**，不影响使用：
- triton（PyTorch 的 GPU kernel 编译器）尚未声明 free-threading 兼容
- Python 导入该模块时临时启用 GIL，导入完成后恢复
- 如需强制保持 GIL 禁用状态，设置环境变量 `PYTHON_GIL=0`
- 该警告不影响 PyTorch 功能正确性和 free-threading 的并行计算能力

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-16 | 新增本 AGENTS.md；添加 docker-compose.torch.yml（三模式+环境变量端口）、examples/test_torch.py（综合验证脚本）、scripts/start-torch-dev.sh（一键启动+自动端口冲突处理） |
| 2026-08-15 | 新增 torch-dev 变体 Dockerfile（3 追加阶段：基础验证→PyTorch安装→冒烟测试），注册到 build.sh VARIANTS 数组 |
