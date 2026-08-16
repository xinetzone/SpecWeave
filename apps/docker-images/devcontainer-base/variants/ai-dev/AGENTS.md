# ai-dev 变体 - 全栈 AI/ML/NLP 开发镜像 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本目录是 devcontainer-base 变体系列的一个变体，
>         规则继承自 ../AGENTS.md（变体系列入口），后者继承自 ../../AGENTS.md（项目入口）
> 步骤 3：按上下文路由表加载变体特有规范（.agents/rules/dockerfile.md）
> 步骤 3.5：自检 — 确认已理解父级规则与本变体特有约束（尤其双环境架构、PATH优先级、Jupyter跨环境内核）
> 步骤 4：在规范指导下执行任务
> ```

本文件是 ai-dev 变体（全栈 AI/ML/NLP 开发镜像，双环境架构）的 AI 协作者入口。
进入本目录的任务优先读取本文件；本文件未覆盖的规则回退到父级 [../AGENTS.md](../AGENTS.md)。

## 变体概述

| 属性 | 值 |
|------|-----|
| 变体名称 | `ai-dev` |
| 镜像标签 | `devcontainer-base:ai-dev-<TAG>`（默认 latest） |
| 基础镜像 | `devcontainer-base:torch-dev-${BASE_TAG}` |
| 依赖链 | base → conda-llvm → onnx-dev → onnx-quantized → torch-dev → **ai-dev**（6层） |
| 核心定位 | 全栈 AI/ML/NLP 开发环境（双环境架构：base GIL兼容 + main free-threading PyTorch） |
| Python 环境架构 | **双环境（Dual-Env）**：base(GIL) + main(free-threading cp314t) |
| 默认 Python | `/opt/conda/bin/python`（base 环境，GIL 启用，承载 50+ AI/ML/NLP 包） |
| PyTorch 环境 | `/opt/conda/envs/main/bin/python`（main 环境，cp314t free-threading，无 GIL，继承自 torch-dev） |
| 本层安装（base环境） | transformers/datasets/fastapi/pandas/matplotlib/jieba/PyMuPDF/数据库客户端/einops/numba 等 48 个包（不含 torch 依赖包） |
| 本层安装（main环境） | onnx2torch, open_clip_torch（torch 依赖包，与 torch 同处 main 环境，G-M1组） |
| 继承自带（main环境） | torch/torchvision（CUDA cp314t）、onnx/onnxruntime（含量化）、onnxsim/onnxscript（来自 torch-dev） |
| 继承自带（base环境） | LLVM/clang/cmake/ninja（来自 conda-llvm 链）、Python 3.14.6 标准构建 |
| 排除项 | onnxoptimizer（free-threading 不兼容，继承自 onnx-quantized 约束） |
| Jupyter kernel | "Python 3 (AI Dev)" — 注册于 main 环境 jupyter，指向 base 环境 python |
| 下游变体 | llm-agent（直接基础，在 base 环境加装 LangChain/LangGraph/LLM SDK/向量库） |

## 三条核心约束（改动本变体前必读）

### 1. 双环境架构不可破坏（Dual-Env Architecture）

ai-dev 的核心设计是**双Python环境隔离**：

- **base 环境（`/opt/conda`，GIL 启用，PATH 最前）**：
  - 默认 `python` 命令指向此环境
  - 承载 48 个 AI/ML/NLP 生态包（transformers、datasets、fastapi、pandas、数据库客户端等）
  - 使用标准 CPython（GIL 启用）保证最大包兼容性
  - **不得在此环境安装 torch/torchvision 或声明 torch 依赖的包**（如 onnx2torch、open_clip_torch）——它们只在 main 环境存在
  - 如果必须安装新包且其 `install_requires` 包含 torch，该包必须装在 main 环境，防止 pip 自动拉取 GIL 版 torch 到 base

- **main 环境（`/opt/conda/envs/main`，free-threading cp314t，无 GIL）**：
  - PyTorch CUDA、ONNX 量化栈、onnx2torch、open_clip_torch 所在（继承自 torch-dev + 本层 G-M1 组）
  - 通过绝对路径 `/opt/conda/envs/main/bin/python` 访问
  - 放已验证可在 free-threading 下工作的包（torch/onnx/onnxruntime/onnxsim/onnxscript/onnx2torch/open_clip）
  - Jupyter 服务运行于此环境（supervisord 启动）

- **环境隔离铁则**：两个环境的 site-packages 完全隔离，**不可跨环境 import 包**。
  - base 环境中无法 import torch（除非 pip 自动安装了 GIL 版，那是 Bug）
  - main 环境中无法 import transformers/fastapi/pandas（它们只装在 base）

- **PATH 优先级（刻意覆盖 torch-dev 设置）**：
  - torch-dev: `/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}`（main 在前）
  - ai-dev: `/opt/conda/bin:${PATH}`（base 在前，覆盖 torch-dev 的 PATH）
  - 理由：ai-dev 的日常开发重心在 base 环境（50+包），main 环境 PyTorch 为需要时显式调用

### 2. Jupyter 跨环境内核机制

Jupyter 服务由 supervisord 以绝对路径 `/opt/conda/envs/main/bin/jupyter` 启动（运行于 main 环境），但用户日常使用的 AI 包在 base 环境。解决方案是**跨环境内核注册**：

- 内核注册位置：`/opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json`
- 内核 argv：`/opt/conda/bin/python -m ipykernel_launcher`（指向 base 环境 python）
- 内核 env.PATH：必须显式设置为 `/opt/conda/bin:/usr/local/sbin:...`（确保内核进程中 base 工具优先）
- Jupyter UI 中显示名为 "Python 3 (AI Dev)"
- 下游 llm-agent 变体会复用此内核，不需要重新注册

### 3. PIP_USER 构建/运行时分离

- **构建期（Stage 2）**：`PIP_USER=0`，所有 pip 包写入 `/opt/conda`（全局可读，root:root 属主）
- **运行时（Stage 3 结束后）**：`PIP_USER=1`，支持用户 `pip install --user` 安装到 `~/.local`
- 此模式防止构建期包误写入 `/root/.local` 导致 devuser 无法 import
- 新增 pip install 步骤必须在 `variant_activate_base_env` 之后执行（该函数设置 PIP_USER=0）

## 环境选择决策树（用户/开发者参考）

```
我要做什么？
├─ 数据处理（pandas/pyarrow）、NLP（transformers/datasets）、Web API（fastapi）、
│  文档处理（PyMuPDF/bs4）、数据库（psycopg2/pymongo）、可视化（matplotlib/seaborn）
│  → 用 base 环境：直接 python 命令，或 Jupyter 中 "Python 3 (AI Dev)" 内核
│
├─ PyTorch 模型训练/推理、CUDA 计算、无 GIL 多核并行、ONNX Runtime 量化
│  → 用 main 环境：/opt/conda/envs/main/bin/python 显式调用
│
└─ 不确定？
   → 先用 base 环境（默认），遇到 import torch 错误时再切到 main 环境
```

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            └─ variants/AGENTS.md（变体系列入口）
                 └─ ai-dev/AGENTS.md ← 本文件（变体级入口）
                      ├─ .agents/rules/dockerfile.md   ← 本变体特有 Dockerfile 规范
                      ├─ Dockerfile                    ← 3 追加阶段构建定义
                      ├─ .env.example                 ← 构建参数模板
                      └─ README.md                    ← 使用说明
```

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 修改本变体 Dockerfile | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 基础信息、双环境架构、PATH优先级、3阶段结构、内核注册、PIP_USER分离 |
| PyTorch CUDA 相关问题 | [../torch-dev/AGENTS.md](../torch-dev/AGENTS.md) | torch 来自 torch-dev 变体，free-threading cp314t、triton GIL警告、CUDA索引等问题参考上游 |
| ONNX 量化相关问题 | [../onnx-quantized/AGENTS.md](../onnx-quantized/AGENTS.md) | 量化工具链继承自 onnx-quantized |
| 变体共享约定（FROM/SHELL/缓存挂载/验证检查点） | [../.agents/rules/variant-conventions.md](../.agents/rules/variant-conventions.md) | 所有变体必须遵循的 Dockerfile 共享约定 |
| 构建本变体 | [../build.sh](../build.sh) + [../.agents/rules/build-orchestration.md](../.agents/rules/build-orchestration.md) | `--variant ai-dev`（拓扑排序自动补齐 torch-dev/onnx-quantized/... 依赖链） |
| 测试本变体 | [../scripts/test-ai-dev.sh](../scripts/test-ai-dev.sh) | 29 项单元测试（L1-L7分层，含双环境GIL守卫+torch隔离T28/T29） |
| 下游 LLM Agent 变体 | [../llm-agent/AGENTS.md](../llm-agent/AGENTS.md) | llm-agent 直接基于 ai-dev，在 base 环境加装 LangChain 生态 |
| 测试规范（分层策略） | [../.agents/rules/testing.md](../.agents/rules/testing.md) | 测试脚本编写规范 |
| 父级回退（变体系列通用规则） | [../AGENTS.md](../AGENTS.md) | 本文件未覆盖时回退 |

## 构建与验证速查

```bash
# 构建（WSL2/Linux，国内镜像源；拓扑排序自动先建 torch-dev 依赖链）
bash variants/build.sh --variant ai-dev --cn

# 快速验证镜像（base 环境 47 个包导入）
docker run --rm devcontainer-base:ai-dev-latest \
  python -c "import transformers,datasets,fastapi,pandas;print('ai-dev base OK')"

# 验证 main 环境 PyTorch 生态（free-threading cp314t，含onnx2torch/open_clip/sentence-transformers）
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/conda/envs/main/bin/python -c "import torch,sys,onnx2torch,open_clip,sentence_transformers;print(f'torch {torch.__version__}, GIL disabled: {not sys._is_gil_enabled()}, CUDA: {torch.cuda.is_available()}')"

# 验证 base 环境无 torch（双环境隔离）
docker run --rm devcontainer-base:ai-dev-latest \
  python -c "import importlib.util;print('torch NOT in base:', importlib.util.find_spec('torch') is None)"

# 验证 Jupyter 内核注册
docker run --rm devcontainer-base:ai-dev-latest \
  /opt/conda/envs/main/bin/jupyter kernelspec list

# 验证双环境 GIL 架构 + torch 隔离
docker run --rm devcontainer-base:ai-dev-latest bash -c '
  echo "=== base env (default python, GIL enabled, NO torch) ===";
  python -c "import sys;print(f\"GIL enabled: {sys._is_gil_enabled()}\")";
  python -c "import importlib.util;print(f\"torch present: {importlib.util.find_spec(\"torch\") is not None}\")";
  python -c "import transformers,datasets;print(f\"transformers OK: base env\")";
  echo "=== main env (PyTorch ft + onnx2torch/open_clip/sentence-transformers, GIL disabled) ===";
  /opt/conda/envs/main/bin/python -c "import sys,torch,onnx2torch,open_clip,sentence_transformers;print(f\"GIL enabled: {sys._is_gil_enabled()}, torch: {torch.__version__}, sentence-transformers OK\")"
'

# 运行完整测试（29项，含双环境GIL守卫+torch隔离T28/T29）
bash variants/scripts/test-ai-dev.sh
```

## 已知设计决策记录

| 决策 | 理由 | 日期 |
|------|------|------|
| 基于 torch-dev 而非 onnx-quantized | torch-dev 提供 free-threading PyTorch CUDA（cp314t），ai-dev 需要 torch 作为一等公民支持下游 LLM Agent | 2026-08-16 记录（之前文档错误声称基于 onnx-quantized） |
| PATH 设置为 `/opt/conda/bin:${PATH}`（base 在前） | 刻意覆盖 torch-dev 的 `/opt/conda/envs/main/bin` 在前设置；ai-dev 日常开发重心在 base 环境（47个兼容包），PyTorch ft 通过绝对路径显式调用 | 2026-08-16 记录 |
| Jupyter 内核注册在 main 环境但指向 base python | Jupyter 服务运行于 main 环境（supervisord 绝对路径启动），但用户需要使用 base 环境的 47 个 AI 包；ipykernel 跨环境内核机制支持此架构 | 2026-08-16 记录 |
| 47 个包装在 base 环境而非 main 环境 | free-threading 生态尚未成熟，大量包（pandas/matplotlib/数据库客户端等）没有 cp314t wheel 或未经验证；base 环境用标准 Python（GIL启用）保证最大兼容性 | 2026-08-16 第一性原理推导 |
| onnx2torch、open_clip_torch、sentence-transformers 装在 main 环境（G-M1组） | 这些包 `install_requires` 包含 torch；装在 base 会导致 pip 自动拉取 GIL 版 torch 到 base，破坏双环境隔离。**所有 torch 依赖包必须与 torch 同处 main 环境** | 2026-08-16 V阶段审查发现问题，构建验证时发现sentence-transformers遗漏，C阶段修复 |
| PIP_USER 构建期0/运行期1分离 | 防止构建期以 root 身份运行 pip install 时，包被写入 `/root/.local` 而非 `/opt/conda`，导致 devuser 运行时无法 import | 2026-08-16 记录 |
| 不提供自己的 AGENTS_EXTRA 激活脚本 | 基础镜像和 onnx-dev 已有激活脚本；ai-dev 不新增额外 profile.d 脚本以避免复杂度 | 2026-08-16 记录 |

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-16 | 新增本 AGENTS.md；修正文档继承链（onnx-quantized→torch-dev→ai-dev）；明确双环境架构三条核心约束；修复 onnx2torch/open_clip_torch/sentence-transformers 安装位置（从 base 移到 main G-M1组，构建验证时发现sentence-transformers遗漏）；添加 T28（base 无 torch 守卫）和 T29（main torch 生态含sentence-transformers）测试；解决V阶段发现的架构风险 |
| 2026-08-15 | ai-dev 变体首次创建（但文档/规范未同步更新，遗留不一致问题） |
