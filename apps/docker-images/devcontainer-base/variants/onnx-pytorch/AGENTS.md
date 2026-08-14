# onnx-pytorch 变体 - PyTorch+ONNX 深度学习运行时镜像 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本目录是 devcontainer-base 变体系列的一个变体，
>         规则继承自 ../AGENTS.md（变体系列入口），后者继承自 ../../AGENTS.md（项目入口）
> 步骤 3：按上下文路由表加载变体特有规范（.agents/rules/dockerfile.md）
> 步骤 3.5：自检 — 确认已理解父级规则与本变体特有约束（尤其 base 环境架构、PyTorch CPU 强制与 GIL 启用约束）
> 步骤 4：在规范指导下执行任务
> ```

本文件是 onnx-pytorch 变体（PyTorch CPU + ONNX 深度学习运行时镜像）的 AI 协作者入口。
进入本目录的任务优先读取本文件；本文件未覆盖的规则回退到父级 [../AGENTS.md](../AGENTS.md)。

## 变体概述

| 属性 | 值 |
|------|-----|
| 变体名称 | `onnx-pytorch` |
| 镜像标签 | `devcontainer-base:onnx-pytorch-<TAG>`（默认 latest） |
| 基础镜像 | `devcontainer-base:conda-llvm-${BASE_TAG}` |
| 依赖链 | base → conda-llvm → **onnx-pytorch** |
| 核心定位 | PyTorch 训练/导出 + ONNX 生态全工具链（**torch 一等公民**，含 onnxoptimizer） |
| Python 环境 | conda **base 环境**（`/opt/conda/bin`，Python 标准构建，**GIL 启用**） |
| 本层安装 | torch（CPU）、torchvision、onnx、onnxruntime、onnx-simplifier、onnxoptimizer、onnxscript |
| 与 onnx-quantized 的关系 | 架构**正交对偶**：本变体 base 环境 + GIL 启用 + torch 预装；quantized 变体 main 环境 + free-threading + torch 排除 |

## 三条核心约束（改动本变体前必读）

### 1. base 环境架构（GIL 启用，与 onnx-dev/onnx-quantized 的 main free-threading 相反）

- 所有工具位于 conda **base 环境**（`/opt/conda/bin`），`ENV PATH=/opt/conda/bin:${PATH}` 置于最前
- Python **标准构建**（GIL 启用）——`sys._is_gil_enabled() is True` 必须恒成立（架构守卫，防止基础镜像演进时 base 环境被静默替换为 free-threading 构建导致 PyTorch 生态不稳）
- 验证命令使用 `/opt/conda/bin/python`（注意区别于 onnx-quantized 的 `/opt/conda/envs/main/bin/python`）

### 2. PyTorch CPU 强制（正向验证）

- **必须**通过 CPU 专用索引（`TORCH_INDEX_URL`，默认 `https://download.pytorch.org/whl/cpu`）安装 torch/torchvision，禁止误装 CUDA 版
- 构建期与测试期断言 `torch.cuda.is_available() is False`，确认 CPU 构建
- PyTorch 版本升级时只改 Stage 2/4，不动其他阶段

### 3. torch.onnx.export 是模型导出主 API

- 本变体定位训练/导出环境：模型构建用 `torch.nn.Module` + `torch.onnx.export` 导出（与 onnx-quantized 的 `onnx.helper` 纯构建形成对偶）
- **onnxoptimizer 本变体保留**（base 环境 GIL 启用，无 free-threading 兼容问题；onnx-dev/onnx-quantized 排除它是因 cp314t 不兼容 CPython #111506——两变体架构正交的直接体现）
- 导出的 `.onnx` 需要量化时，移交 onnx-quantized 变体处理（跨变体工作流）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则）
  └─ apps/AGENTS.md（应用区入口）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            └─ variants/AGENTS.md（变体系列入口）
                 └─ onnx-pytorch/AGENTS.md ← 本文件（变体级入口）
                      ├─ .agents/rules/dockerfile.md   ← 本变体特有 Dockerfile 规范
                      ├─ Dockerfile                    ← 4 追加阶段构建定义
                      ├─ .env.example                 ← 构建参数模板
                      ├─ README.md                    ← 使用说明
                      └─ RELEASE.md                   ← v1.1.0 发布清单（镜像标识/版本矩阵/验证记录）
```

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 修改本变体 Dockerfile | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 基础信息、PATH 优先级、PyTorch CPU 安装、ONNX 生态、4 阶段结构 |
| 量化操作（INT8/FP16） | [../onnx-quantized/AGENTS.md](../onnx-quantized/AGENTS.md) | torch 导出的模型在 quantized 变体中量化（跨变体工作流） |
| 对比纯 ONNX 变体（无 PyTorch） | [../onnx-dev/AGENTS.md](../onnx-dev/AGENTS.md) | main 环境 + free-threading + torch 一等排除的架构来源 |
| 变体共享约定（FROM/SHELL/缓存挂载/验证检查点） | [../.agents/rules/variant-conventions.md](../.agents/rules/variant-conventions.md) | 所有变体必须遵循的 Dockerfile 共享约定 |
| 构建本变体 | [../build.sh](../build.sh) + [../.agents/rules/build-orchestration.md](../.agents/rules/build-orchestration.md) | `--variant onnx-pytorch`（拓扑排序自动补齐 conda-llvm 依赖） |
| 测试本变体 | [../scripts/test-onnx-pytorch.sh](../scripts/test-onnx-pytorch.sh) | 23 项测试（GIL 启用/版本/冒烟/导出推理/服务/环境） |
| 测试规范（分层策略） | [../.agents/rules/testing.md](../.agents/rules/testing.md) | 测试脚本编写规范 |
| 父级回退（变体系列通用规则） | [../AGENTS.md](../AGENTS.md) | 本文件未覆盖时回退 |

## 构建与验证速查

```bash
# 构建（WSL2/Linux，国内镜像源；拓扑排序自动先建 conda-llvm）
bash variants/build.sh --variant onnx-pytorch --cn

# 测试已有镜像（23 项：GIL启用/版本/torch张量/导出推理/服务/环境纯净）
bash variants/scripts/test-onnx-pytorch.sh --tag latest

# 快速验证（torch + ONNX 导出 + ORT 推理一条龙）
docker run --rm devcontainer-base:onnx-pytorch-latest \
  /opt/conda/bin/python -c "import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)"
```

## 已知设计决策记录

| 决策 | 原因 | 日期 |
|------|------|------|
| base 环境而非 main free-threading | PyTorch CPU wheel 对 cp314t free-threading 构建支持不稳，标准构建最稳；本变体优先可用性而非并行性能 | 2026-08-14 记录 |
| onnxoptimizer 保留预装 | base 环境 GIL 启用无兼容问题（对比：onnx-dev/onnx-quantized 因 cp314t 排除并以 onnxsim 替代） | 2026-08-14 记录 |
| onnx-pytorch-init.sh 保留 | base 环境 PATH 已通过 ENV 生效，init 脚本为 login shell 后备兼容 | 2026-08-14 记录 |

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-14 | 新增本 AGENTS.md（补齐变体系列三层路由空洞）；测试增强至 23 项（GIL 正向守卫/ONNX 生态完整导入/OpenMP）；规则文件修正过时引用 |
