---
title: "AReaL 2.0 官方实战教程：从安装到在线RL微服务部署"
source: "AReaL官网(https://areal-ai.io/)、官方文档(https://areal-ai.io/docs/en/intro.html)、本地代码仓库(d:\\AI\\external\\tools\\AReaL)"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/areal-official-practical-wiki.toml"
date: "2026-08-04"
tags: ["areal", "rl-training", "agentic-rl", "online-rl", "llm-alignment", "distributed-training", "pytorch", "sglang", "vllm", "fsdp", "megatron"]
---

# AReaL 2.0 官方实战教程：从安装到在线RL微服务部署

> 📚 **相关文档**：本文为实战教程篇，概念原理篇请参考 [AReaL Agent RL Wiki：异步强化学习系统概念与原理](./areal-agent-rl-wiki.md)

## 目录

- [一、概述与前置准备](#一概述与前置准备)
- [二、环境安装](#二环境安装)
- [三、快速开始](#三快速开始)
- [四、核心概念与架构](#四核心概念与架构)
- [五、算法、训练引擎与推理后端](#五算法训练引擎与推理后端)
- [六、v2.0微服务架构详解](#六v20微服务架构详解)
- [七、Online RL在线训练实战](#七online-rl在线训练实战)
- [八、CLI命令参考与配置指南](#八cli命令参考与配置指南)
- [九、代码仓库结构与示例解析](#九代码仓库结构与示例解析)
- [十、最佳实践、FAQ、术语表、资源链接](#十最佳实践faq术语表资源链接)

---

## 一、概述与前置准备

**AReaL**（Asynchronous Reinforcement Learning，异步强化学习）是一个专为大规模语言模型推理和Agent应用设计的强化学习基础设施，由清华大学IIIS与蚂蚁集团AReaL团队开发。

> 💡 **概念篇交叉引用**：关于AReaL的异步RL范式、解耦PPO损失、参数重分配等核心原理，请阅读 [AReaL Agent RL Wiki：异步强化学习系统概念与原理](./areal-agent-rl-wiki.md)。

### 1.1 AReaL 2.0亮点

- **⚡ 灵活性**：通过替换`base_url`即可为任意黑盒Agent应用提供Agentic RL和Online RL训练支持
- **📈 可扩展性**：稳定的全异步RL训练，业界领先速度（相比同步系统2.77×加速）
- **✨ 前沿性能**：数学、代码、搜索、客服等领域达到SOTA

### 1.2 前置硬件要求

| 组件 | 单节点推荐配置 | 分布式推荐配置 |
|------|---------------|---------------|
| GPU | 8× H800/A100 | 每节点8× H800 |
| CPU | 64核 | 每节点64核 |
| 内存 | 1TB | 每节点1TB |
| 网络 | NVSwitch | NVSwitch + RoCE 3.2 Tbps |
| 存储 | 1TB本地SSD | 10TB共享存储（NFS/NAS） |

### 1.3 前置软件要求

| 组件 | 版本要求 |
|------|---------|
| 操作系统 | CentOS 7 / Ubuntu 22.04 |
| NVIDIA驱动 | 550.127.08+ |
| CUDA | 12.8 |
| Git LFS | 最新版 |
| Docker（推荐） | 27.5.1 |
| NVIDIA Container Toolkit | 最新版 |

---

## 二、环境安装

### 2.1 方式一：Docker安装（推荐）

官方提供预构建镜像，包含所有运行时依赖和Ray组件：

```bash
# 拉取默认SGLang镜像
docker pull ghcr.io/areal-project/areal-runtime:v2.0.0-sglang

# 启动容器
docker run -it --name areal-node1 \
   --privileged --gpus all --network host \
   --shm-size 700g -v /path/to/shared:/path/to/shared \
   ghcr.io/areal-project/areal-runtime:v2.0.0-sglang \
   /bin/bash

# 容器内安装AReaL
git clone https://github.com/areal-project/AReaL /path/to/shared/AReaL
cd /path/to/shared/AReaL
uv pip install -e . --no-deps
```

如需使用vLLM作为推理后端，替换镜像标签为`v2.0.0-vllm`。

### 2.2 方式二：源码安装

#### 步骤1：安装uv包管理器

```bash
pip install uv
```

#### 步骤2：克隆仓库

```bash
git clone https://github.com/areal-project/AReaL
cd AReaL
```

#### 步骤3：（可选）配置国内镜像源

在`pyproject.toml`中添加：

```toml
[[tool.uv.index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

#### 步骤4：安装Flash Attention预编译wheel（推荐）

PyPI只提供源码分发，从源码编译需约30分钟，推荐安装预编译wheel：

```bash
# SGLang版本（torch 2.9，Python 3.12）
uv pip install "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.8.3+cu128torch2.9-cp312-cp312-linux_x86_64.whl"
```

其他Python版本请访问：https://github.com/mjun0812/flash-attention-prebuild-wheels/releases

#### 步骤5：安装依赖

```bash
# Linux CUDA环境（默认SGLang推理后端）
uv sync --extra cuda

# macOS/无CUDA环境（仅开发测试用）
uv sync
```

### 2.3 SGLang与vLLM后端切换

SGLang和vLLM对torch/torchao/transformers版本有互斥约束，需通过替换配置文件切换：

```bash
# ====== 切换到vLLM ======
cp pyproject.vllm.toml pyproject.toml
cp uv.vllm.lock uv.lock
# 安装vLLM版本的flash-attn（torch 2.10）
uv pip install "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.8.3+cu128torch2.10-cp312-cp312-linux_x86_64.whl"
uv sync --extra cuda

# ====== 切回SGLang ======
git checkout pyproject.toml uv.lock
uv sync --extra cuda
```

Docker构建时指定VARIANT参数：
```bash
docker build --build-arg VARIANT=vllm -t areal-runtime:dev-vllm .
```

### 2.4 额外CUDA包（可选，手动安装）

自定义环境如需FP8训练、融合Adam等优化，需额外安装（需`--no-build-isolation`）：

| 包 | 用途 | 安装命令 |
|----|------|---------|
| grouped_gemm | Megatron MoE支持 | `uv pip install --no-build-isolation git+https://github.com/fanshiqing/grouped_gemm@v1.1.4` |
| NVIDIA apex | 融合Adam等 | `NVCC_APPEND_FLAGS="--threads 4" APEX_PARALLEL_BUILD=8 uv pip install --no-build-isolation git+https://github.com/NVIDIA/apex.git` |
| TransformerEngine | FP8训练 | `uv pip install --no-build-isolation git+https://github.com/NVIDIA/TransformerEngine.git@stable` |

### 2.5 安装验证

运行验证脚本确认安装正确：

```bash
uv run python3 areal/tools/validate_installation.py
```

### 2.6 昇腾NPU支持

NPU支持在`ascend-v1.0.4`分支维护：

```bash
git checkout ascend-v1.0.4
# 使用官方NPU镜像
docker pull ghcr.io/hwvanici/areal_npu:v1.0.4-a3  # Atlas A3
# 或 ghcr.io/hwvanici/areal_npu:v1.0.4-a2  # Atlas A2
```

**注意**：NPU上推理仅支持vLLM（vLLM-Ascend插件），SGLang不可用；训练支持FSDP和Megatron（通过MindSpeed）。

### 2.7 （可选）Ray集群启动

多节点分布式训练前启动Ray集群：

```bash
# 第一个节点（Head）
ray start --head

# 其他节点（Worker）
RAY_HEAD_IP=<head-node-ip>
ray start --address $RAY_HEAD_IP

# 验证
ray status
```

---

## 三、快速开始

### 3.1 单节点GSM8K GRPO训练

训练脚本会自动下载数据集（openai/gsm8k）和模型（Qwen/Qwen2-1.5B-Instruct）：

```bash
python3 examples/math/gsm8k_rl.py \
  --config examples/math/gsm8k_grpo.yaml \
  scheduler.type=local \
  experiment_name=my_first_exp \
  trial_name=trial_1
```

也可以使用新的`areal train` CLI：
```bash
areal train run \
  --config examples/math/gsm8k_grpo.yaml \
  --driver examples.math.gsm8k_rl:main \
  experiment_name=my_first_exp trial_name=trial_1
```

Qwen2.5-1.5B-Instruct经过调优可达到约79.6%的GSM8K准确率。

### 3.2 配置修改方法

所有配置选项定义在`areal/api/cli_args.py`。自定义配置有两种方式：

**方式1：直接编辑YAML文件**

编辑`examples/math/gsm8k_grpo.yaml`。

**方式2：命令行覆盖（Hydra风格）**

| 语法 | 说明 | 示例 |
|------|------|------|
| `key=value` | 覆盖已有配置项 | `actor.path=Qwen/Qwen3-1.7B` |
| `+key=value` | 新增配置项（YAML中不存在的） | `+sglang.attention_backend=triton` |

**自定义配置示例**：

```bash
python3 examples/math/gsm8k_rl.py \
    --config examples/math/gsm8k_grpo.yaml \
    scheduler.type=local \
    experiment_name=custom_exp \
    trial_name=t1 \
    rollout.backend=sglang:d2t2 \
    actor.backend=fsdp:d2t2 \
    cluster.n_nodes=1 \
    cluster.n_gpus_per_node=4 \
    gconfig.max_new_tokens=2048 \
    train_dataset.batch_size=1024 \
    +sglang.attention_backend=triton
```

**配置优先级**：CLI参数 > `--config`传入的YAML > `~/.areal/`默认配置 > 内置默认值。

### 3.3 分布式训练（Ray/Slurm）

确保总GPU数匹配：`#GPU == cluster.n_nodes * cluster.n_gpus_per_node`。

**Ray分布式（4节点×4GPU）**：
```bash
python3 examples/math/gsm8k_rl.py \
    --config examples/math/gsm8k_grpo.yaml \
    scheduler.type=ray \
    experiment_name=ray_exp \
    trial_name=t1 \
    rollout.backend=sglang:d12t1 \
    actor.backend=fsdp:d4t1 \
    cluster.n_nodes=4 \
    cluster.n_gpus_per_node=4 \
    cluster.fileroot=/path/to/nfs
```

**Slurm分布式（16节点×8GPU）**：
```bash
python3 examples/math/gsm8k_rl.py \
    --config examples/math/gsm8k_grpo.yaml \
    scheduler.type=slurm \
    experiment_name=slurm_exp \
    trial_name=t1 \
    rollout.backend=sglang:d96t1 \
    actor.backend=fsdp:d32t1 \
    cluster.n_nodes=16 \
    cluster.n_gpus_per_node=8 \
    cluster.fileroot=/path/to/nfs
```

> **注意**：Ray/Slurm调度器仅在多节点（`n_nodes > 1`）时工作，以节点为粒度分配GPU，因此rollout和training的GPU数必须是`n_gpus_per_node`的整数倍。

### 3.4 SkyPilot云部署

SkyPilot支持在GCP、AWS、Kubernetes等17+云平台一键部署：

```bash
# 安装SkyPilot
pip install -U "skypilot[gcp,kubernetes]"

# GCP配置
gcloud init
gcloud auth application-default login

# 验证
sky check

# 启动集群（2节点8xA100）
sky launch -c areal-test examples/skypilot/ray_cluster.sky.yaml --infra gcp
```

### 3.5 backend并行配置语法

训练引擎和推理后端均使用统一的并行配置语法：

```
backend:engine[:parallel-config]
```

其中并行配置字母含义：
- `d`：数据并行（DP, Data Parallelism）
- `t`：张量并行（TP, Tensor Parallelism）
- `p`：流水线并行（PP, Pipeline Parallelism）
- `c`：上下文并行（CP, Context Parallelism）
- `e`：专家并行（EP, Expert Parallelism，不增加world size）

**常用配置示例**：

| 配置 | 说明 | 总GPU数 |
|------|------|---------|
| `sglang:d4` | 4个SGLang数据并行实例 | 4 |
| `sglang:d2t2` | 2个SGLang实例，每个2卡TP | 4 |
| `vllm:d2t4` | vLLM，2节点×4张量并行 | 8 |
| `fsdp:d8` | 8卡FSDP数据并行 | 8 |
| `fsdp:d4t2` | 4卡DP，2卡TP | 8 |
| `fsdp:d2c2` | 2卡DP，2卡Ulysses上下文并行 | 4 |
| `megatron:d2p2t4` | 2 DP × 2 PP × 4 TP | 16 |
| `archon:d2p2e2` | 2 DP × 2 PP，2专家并行 | 4（EP不增加world size） |

MoE混合并行语法：`megatron:(attn:d1p4t2c2|ffn:d1p4t1e4)`

---

## 四、核心概念与架构

> 💡 **概念篇交叉引用**：关于异步RL、解耦PPO损失、staleness控制等深入原理，请参考 [AReaL Agent RL Wiki：异步强化学习系统概念与原理](./areal-agent-rl-wiki.md)。

### 4.1 核心组件

| 组件 | 中文解释 | 职责 |
|------|---------|------|
| **Trainer** | 训练器 | 管理训练循环的核心组件（PPOTrainer、SFTTrainer、DPOTrainer等） |
| **Engine** | 引擎 | 封装推理或训练后端（FSDPEngine、MegatronEngine、SGLang、vLLM） |
| **Workflow** | 工作流 | 定义rollout如何生成、奖励如何计算（RolloutWorkflow、AgentWorkflow） |
| **Rollout** | 轨迹采样/推演 | 使用策略生成轨迹（序列）的过程 |
| **Actor** | Actor/策略网络 | RL中生成动作（文本）的策略网络 |
| **Critic** | Critic/价值网络 | PPO中估计状态价值的网络（GRPO无需Critic） |
| **Scheduler** | 调度器 | 管理集群资源分配（LocalScheduler、RayScheduler、SlurmScheduler） |

### 4.2 单控制器架构（Single-Controller Mode）

AReaL 2.0推荐使用**单控制器模式**（vs 传统SPMD模式）：

- 一个驱动脚本管理所有组件
- 通过scheduler（local/ray/slurm）分配资源
- 直接运行Python脚本即可启动，无需`torchrun`或专用launcher
- 支持训练和推理完全解耦的异步执行

**单控制器模式 vs SPMD模式**：

| 特性 | 单控制器模式（推荐） | SPMD模式（legacy） |
|------|---------------------|-------------------|
| 启动方式 | 直接运行脚本+scheduler.type | 通过`areal.infra.launcher.*`启动 |
| 进程模型 | 一个控制器+多个worker | 每个GPU运行相同程序 |
| 灵活性 | 高，支持微服务架构 | 低，传统分布式训练模式 |
| Online RL支持 | ✅ | ❌ |

### 4.3 Weight Versioning（权重版本控制）

异步RL训练中，rollout策略可能落后于当前训练策略若干版本，这个版本差称为**staleness（陈旧度）**：

- `max_head_offpolicyness`：允许的最大staleness（默认4，即允许落后4个训练版本）
- 通过**解耦PPO损失**（Decoupled PPO Loss）分离三种策略：
  - `π_behave`（行为策略）：生成样本的rollout策略
  - `π_proximal`（近端策略）：比当前策略落后一个训练步的策略
  - `π_θ`（当前策略）：正在优化的当前策略
- 通过**拒绝采样**（Rejection Sampling）掩码策略偏移过大的token（IcePop/KPop算法）

### 4.4 AReaL v2.0 vs v1.0区别

| 特性 | v1.0 | v2.0 |
|------|------|------|
| 架构 | 单体+SPMD | 微服务架构（四大独立服务） |
| CLI | Python脚本直接运行 | `areal` CLI统一管理服务 |
| Agent支持 | Workflow嵌入Python代码 | 独立Agent Service，HTTP API交互 |
| Online RL | 有限支持 | 一等公民，OpenAI兼容API |
| 服务管理 | 脚本手动管理 | `areal inf/agent`自动管理生命周期 |
| Hermes Agent | 实验性 | 端到端自进化示例 |
| SWE训练 | 不支持 | 完整端到端支持 |

---

## 五、算法、训练引擎与推理后端

### 5.1 16种算法完整列表

所有RL算法均支持异步和同步两种模式（设置`max_head_offpolicyness=0`切换为同步）。

| 算法名 | 简要说明 | 典型应用场景 |
|--------|---------|-------------|
| **GRPO** | Group Relative Policy Optimization，组相对策略优化，组内归一化优势，无需critic | 数学推理、代码生成 |
| **GSPO** | Group Sequence Policy Optimization，组序列策略优化，序列级几何平均重要性比率 | 大规模LLM后训练 |
| **PPO** | Proximal Policy Optimization，近端策略优化，GAE估计优势，需critic | RLHF对齐、通用RL |
| **DAPO** | Decoupled Alignment Policy Optimization，非对称裁剪+动态采样，过滤全对/全错样本 | 推理模型、长响应 |
| **LitePPO** | 轻量级PPO，组级均值归一化 | 快速原型、资源受限 |
| **Dr.GRPO** | 组级均值归一化、无std缩放，消除长度偏差 | 数学推理 |
| **REINFORCE++** | REINFORCE改进版 | 基线对比实验 |
| **RLOO** | REINFORCE Leave-One-Out，留一法估计基线 | 减少方差的策略梯度 |
| **SAPO** | Soft Adaptive Policy Optimization，soft sigmoid门控替代硬裁剪 | 需要稳定训练的场景 |
| **IcePop** | 重要性比率token掩码，掩码比率超出[α,β]的token，可组合使用 | 异步RL、离策略校正 |
| **KPop** | 双向二元KL散度token掩码，掩码KL超阈值的token | 异步RL、策略偏移控制 |
| **M2PO** | Second-Moment Trust Policy Optimization，约束重要性权重二阶矩，支持256版陈旧数据 | 大规模异步RL |
| **DPO** | Direct Preference Optimization，直接偏好优化，无需奖励模型或在线rollout | RLHF对齐、偏好学习 |
| **RW** | Reward Modeling，Bradley-Terry奖励模型训练 | RLHF奖励模型 |
| **SFT** | Supervised Fine-Tuning，监督微调 | 预训练后微调、指令跟随 |
| **Distillation** | On-Policy Distillation，在线策略蒸馏，支持纯KD和KDRL | 模型压缩、知识迁移 |

### 5.2 算法核心参数配置矩阵

| 算法 | `adv_norm.mean_level` | `adv_norm.std_level` | `mean_leave1out` | `importance_sampling_level` | 特殊配置 |
|------|-----------------------|----------------------|-------------------|-----------------------------|---------|
| PPO | `batch` | `batch` | `false` | `token` | 需要critic模型 |
| GRPO | `batch` | `batch` | `false` | `token` | - |
| Dr.GRPO | `group` | `null` | `false` | `token` | - |
| LitePPO | `group` | `batch` | `false` | `token` | - |
| RLOO | `group` | `null` | `true` | `token` | - |
| GSPO | `batch` | `batch` | `false` | `sequence` | - |
| DAPO | `batch` | `batch` | `false` | `token` | 非对称裁剪、动态采样 |
| SAPO | `batch` | `batch` | `false` | `token` | `use_sapo_loss=true`，`use_decoupled_loss=false` |
| IcePop | `batch` | `batch` | `false` | `token` | `rejection_sampling.metric=ratio`，`use_decoupled_loss=true` |
| KPop | `batch` | `batch` | `false` | `token` | `rejection_sampling.metric=binary_kl`，`use_decoupled_loss=true` |

### 5.3 三种训练引擎对比

| 特性 | **FSDP2 (FSDPEngine)** | **Megatron (MegatronEngine)** | **Archon (ArchonEngine)** |
|------|------------------------|-------------------------------|---------------------------|
| 后端基础 | HuggingFace + FSDP2 | Megatron-Core | PyTorch-native (DTensor, DeviceMesh) |
| 模型来源 | 任意HuggingFace模型 | Megatron模型（mbridge） | 内置模型+用户自定义 |
| 生产状态 | ✅ Production | ✅ Production | ⚠️ Experimental |
| 数据并行(DP) | ✅ FSDP2 | ✅ ZeRO-1 | ✅ FSDP2 |
| 张量并行(TP) | ✅ PyTorch DTensor | ✅ Megatron TP | ✅ PyTorch DTensor |
| 序列并行(SP) | ✅ Ulysses SP | ✅ | ✅ Ulysses SP |
| 上下文并行(CP) | ✅ | ✅ Megatron CP | ✅ Ulysses SP |
| 流水线并行(PP) | ❌ | ✅ (VPP) | ✅ (1F1B/I1F1B/IZB/ZBV) |
| 专家并行(EP) | ❌ | ✅ Full EP/ETP | ✅ Full EP/ETP |
| LoRA支持 | ✅ | ✅（需vLLM） | ❌ |
| torch.compile | Limited | ❌ | ✅（默认启用） |
| 依赖复杂度 | 纯Python，简单 | 需C++编译（transformer_engine等） | 纯Python，无复杂构建 |

**引擎适用场景**：
- **FSDP2**：快速原型、任意HF模型、中小规模训练
- **Megatron**：大规模训练、MoE模型、极致性能（生产验证）
- **Archon**：RL研究、自定义优化、需要原生PyTorch调试

**引擎切换方法**：
```yaml
# FSDP2
actor:
  backend: "fsdp:d4t2"

# Megatron
actor:
  backend: "megatron:d4p2t2"
  # MoE混合并行：
  # backend: "megatron:(attn:d1p4t2c2|ffn:d1p4t1e4)"

# Archon
actor:
  backend: "archon:d4p2t2"
  archon:
    pp_schedule: Interleaved1F1B
    enable_compile: true
    ac_mode: selective
```

### 5.4 两种推理后端对比

| 特性 | **SGLang（默认）** | **vLLM** |
|------|-------------------|---------|
| 版本 | `sglang[tracing]==0.5.10.post1` | `vllm==0.19.1` |
| Torch版本 | `torch>=2.9.1,<2.11` | `torch>=2.10.0,<2.11` |
| 张量并行(TP) | ✅ | ✅ |
| 流水线并行(PP) | ❌ | ✅ |
| DP Attention | ✅ | ❓ |
| 专家并行(EP) | ✅ | ❓ |
| 视觉语言模型(VLM) | ✅（依赖nvidia-cudnn-cu12） | 需验证 |

**版本依赖冲突**：SGLang和vLLM不能同时安装，切换方法见[2.3节](#23-sglang与vllm后端切换)。

**推理后端配置**：
```yaml
# SGLang
rollout:
  backend: "sglang:d4t2"

# vLLM
rollout:
  backend: "vllm:d4t2"
```

### 5.5 模型支持矩阵

| 模型系列 | Megatron | FSDP2 | Archon | 说明 |
|---------|----------|-------|--------|------|
| Qwen2/3 (Dense) | ✅ | ✅ | ✅ | Qwen稠密模型 |
| Qwen3-MoE | ✅ | ✅ | ✅ | Qwen3混合专家 |
| Qwen2.5-VL | ✅ | ✅ | ❌ | 视觉语言模型 |
| Qwen3-VL | ✅ | ✅ | ❌ | 视觉语言模型 |
| Gemma 3 | ❌ | ✅ | ❌ | VLM |
| 其他HuggingFace LLM | ❌ | ✅ | ❌ | 兼容性取决于transformers版本 |

Archon内置支持`qwen2`、`qwen3`、`qwen3_moe`三类模型，不支持的需使用FSDP2或Megatron。

---

## 六、v2.0微服务架构详解

### 6.1 四大微服务总览

AReaL 2.0重构为独立微服务架构：

| 微服务 | 模块路径 | 职责 |
|--------|---------|------|
| **Training Service** | `areal/v2/training_service/` | 执行RL训练循环，管理actor/critic权重更新 |
| **Inference Service** | `areal/v2/inference_service/` | 提供LLM推理，管理SGLang/vLLM实例，记录token级数据 |
| **Agent Service** | `areal/v2/agent_service/` | 运行Agent代码，管理多轮会话和工具调用 |
| **Weight Update** | `areal/v2/weight_update/` | 通过NCCL或磁盘将新权重同步到推理后端 |

### 6.2 Agent Service四组件详解

Agent Service由四个独立HTTP服务组成，通过REST通信：

```
Client (HTTP/WS)
    │
    ▼
┌──────────┐  POST /route   ┌──────────┐
│ Gateway  │ ──────────────▶ │ Router   │
│          │ ◀────────────── │          │
└──────────┘  DataProxy addr └──────────┘
    │
    │ POST /session/{key}/turn
    ▼
┌──────────┐
│ DataProxy│  POST /run   ┌──────────┐
│ (history)│ ────────────▶│ Worker   │
└──────────┘              │ (agent)  │
                          └──────────┘
```

| 组件 | 职责 | 状态 |
|------|------|------|
| **Gateway** | 公共入口，接受WebSocket和HTTP请求（OpenResponses桥、OpenAI chat-completions桥），通过Router路由到DataProxy | 无状态 |
| **Router** | 会话亲和性路由，DataProxy启动时注册，新会话round-robin分配，维护session→DataProxy亲和性 | 无状态 |
| **DataProxy** | 有状态会话代理，与Worker 1:1配对，管理每会话对话历史，每轮读取history→构造AgentRequest→转发Worker→追加消息→返回响应 | 有状态（会话历史） |
| **Worker** | 无状态Agent执行服务器，启动时加载`AgentRunnable`实现，每个`POST /run`是一个turn，Worker无会话状态 | 无状态 |

### 6.3 AgentRunnable协议

任何满足以下协议的Python类都可在Worker上运行：

```python
from typing import Protocol, runtime_checkable
from areal.v2.agent_service.types import AgentRequest, AgentResponse, EventEmitter

@runtime_checkable
class AgentRunnable(Protocol):
    async def run(
        self,
        request: AgentRequest,
        *,
        emitter: EventEmitter,
    ) -> AgentResponse: ...
```

**AgentRequest结构**：
```python
@dataclass
class AgentRequest:
    message: str                              # 当前用户消息
    session_key: str                          # 会话标识符
    run_id: str                               # 唯一run ID
    history: list[dict[str, str]]             # 之前的对话轮次
    queue_mode: QueueMode = QueueMode.COLLECT
    metadata: dict[str, Any] = field(default_factory=dict)
```

**AgentResponse结构**：
```python
@dataclass
class AgentResponse:
    summary: str = ""                         # Agent回复文本
    metadata: dict[str, Any] = field(default_factory=dict)
```

**EventEmitter接口**（流式输出和工具调用事件）：
```python
class EventEmitter(Protocol):
    async def emit_delta(self, text: str) -> None: ...
    async def emit_tool_call(self, name: str, args: str) -> None: ...
    async def emit_tool_result(self, name: str, result: str) -> None: ...
```

### 6.4 HTTP API端点列表

**Agent Service - Gateway**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/ws` | WS | Gateway WebSocket协议（流式delta/tool_call事件） |
| `/v1/responses` | POST | OpenResponses HTTP桥接 |
| `/v1/chat/completions` | POST | OpenAI chat-completions桥接 |

**Agent Service - Router**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/register` | POST | 注册DataProxy |
| `/unregister` | POST | 注销DataProxy |
| `/route` | POST | 获取会话对应的DataProxy |
| `/remove_session` | POST | 移除会话亲和性 |

**Agent Service - DataProxy**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/session/{key}/turn` | POST | 发送消息（一轮对话） |
| `/session/{key}/close` | POST | 关闭会话 |
| `/session/{key}/history` | GET | 获取对话历史 |

**Agent Service - Worker**：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/run` | POST | 执行一个Agent turn |

**Inference Service - Online RL端点**（详见第七章）：

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/health` | GET | 无 | 健康检查 |
| `/rl/start_session` | POST | Admin key | 创建/刷新会话 |
| `/chat/completions` | POST | Session key | OpenAI兼容chat补全 |
| `/v1/chat/completions` | POST | Session key | v1别名 |
| `/rl/set_reward` | POST | Session key | 设置奖励 |
| `/export_trajectories` | POST | Admin key | 导出训练轨迹 |

---

## 七、Online RL在线训练实战

Online模式是AReaL 2.0的核心特性：Agent代码运行在AReaL**外部**，AReaL暴露OpenAI兼容HTTP API，任何支持chat completions协议的应用程序都可连接，实现人类反馈或外部运行时的在线RL训练。

### 7.1 三种Agent执行模式对比

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| `inline` | Agent在rollout worker进程内运行 | 大多数Agent框架 |
| `subproc` | Agent在子进程池中运行 | 非异步或需要隔离的代码 |
| **`online`** | 外部用户通过HTTP API驱动交互 | 人类反馈、外部运行时、黑盒Agent |

### 7.2 Online RL架构

```
                          External Application
                         (ZeroClaw, scripts, etc.)
                                  |
                      POST /chat/completions
                      POST /rl/set_reward
                                  |
                                  v
                      +-------------------+
                      |  Proxy Gateway    |  (FastAPI, stateless router)
                      |  - Session mgmt   |
                      |  - Key auth       |
                      |  - Load balancing |
                      +-------------------+
                         /        |        \
                        v         v         v
                  +---------+ +---------+ +---------+
                  | Proxy   | | Proxy   | | Proxy   |
                  | Worker  | | Worker  | | Worker  |  (one per rollout worker)
                  +---------+ +---------+ +---------+
                      |           |           |
                      v           v           v
                  +---------+ +---------+ +---------+
                  | SGLang/ | | SGLang/ | | SGLang/ |
                  | vLLM    | | vLLM    | | vLLM    |  (inference servers)
                  +---------+ +---------+ +---------+
                                  |
                      Token-level data collected
                                  |
                                  v
                      +-------------------+
                      |   RL Trainer      |
                      |   (PPOTrainer)    |
                      +-------------------+
```

**核心组件**：
- **Proxy Gateway**：轻量FastAPI服务器，路由外部请求到后端proxy worker，管理会话、认证、负载均衡
- **Proxy Workers**：与rollout worker共置，管理会话，记录token级数据（token IDs, log probabilities），导出训练轨迹
- **Inference Servers**：SGLang或vLLM，执行实际LLM推理

### 7.3 6步快速开始

#### Step 1：配置Online模式

在YAML配置中设置`rollout.agent.mode: online`：

```yaml
rollout:
  agent:
    mode: online
    admin_api_key: "my-secret-admin-key"
    session_timeout_seconds: 3600
    turn_discount: 1.0
    export_style: "individual"
    drop_retry_orphans: false
```

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `mode` | `inline` | 必须设为`online`启用外部访问 |
| `admin_api_key` | `areal-admin-key` | 管理API密钥（生产环境请修改） |
| `session_timeout_seconds` | `3600` | 会话超时时间（秒） |
| `turn_discount` | `1.0` | 多轮对话奖励几何折扣因子 |
| `export_style` | `individual` | 交互导出方式：`individual`或`concat` |
| `drop_retry_orphans` | `false` | 导出前删除重试孤儿completion |

#### Step 2：启动RL服务

```bash
python3 examples/openclaw/train.py --config examples/openclaw/config.yaml \
    experiment_name=my-exp trial_name=trial-0 \
    rollout.backend=sglang:d1 actor.backend=fsdp:d1 \
    actor.path=Qwen/Qwen3-0.6B \
    scheduler.type=local \
    rollout.agent.admin_api_key=my-secret-admin-key
```

初始化成功后打印网关地址：
```
(AReaL) RLTrainer INFO: Proxy gateway available at http://x.x.x.x:8090
```

#### Step 3：创建Session

使用admin API key创建会话，获取session API key：

```bash
curl -X POST http://localhost:8090/rl/start_session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-secret-admin-key" \
  -d '{"task_id": "demo-task-0", "group_size": 1}'
```

**v2响应格式**：
```json
{
  "group_id": "grp-<uuid>",
  "sessions": [
    {
      "session_id": "demo-task-0-0",
      "session_api_key": "sk-sess-xxxxxxxxxxxx"
    }
  ]
}
```

- 传入`api_key`可复用已有key（刷新机制）：旧session自动结束（未设奖励则默认0），轨迹导出，新session使用同一key启动
- `group_size > 1`可原子性批量创建多个会话

#### Step 4：与模型交互

使用任何OpenAI兼容客户端。

**curl方式**：
```bash
curl http://localhost:8090/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-sess-xxxxxxxxxxxx" \
  -d '{
    "model": "default",
    "messages": [{"role": "user", "content": "What is 12 * 15 + 3?"}],
    "temperature": 0.7
  }'
```

**OpenAI Python SDK方式**：
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8090",
    api_key="sk-sess-xxxxxxxxxxxx",
)

response = client.chat.completions.create(
    model="default",
    messages=[{"role": "user", "content": "What is 12 * 15 + 3?"}],
)
print(response.choices[0].message.content)
```

#### Step 5：设置奖励并结束会话

```bash
curl -X POST http://localhost:8090/rl/set_reward \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-sess-xxxxxxxxxxxx" \
  -d '{"reward": 1.0}'
```

刷新session自动结束旧会话并开始新会话（无需单独调用end_session）：
```bash
curl -X POST http://localhost:8090/rl/start_session \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer my-secret-admin-key" \
  -d '{"task_id": "demo-task-0", "api_key": "sk-sess-xxxxxxxxxxxx"}'
```

#### Step 6：批量采样

将Steps 3-5整合为脚本，使用`sbatch`等并发运行。每个agent session必须重新调用`/rl/start_session`获取新API key（或使用刷新机制复用同一key）。缓冲区积累足够数据后AReaL自动执行训练步，更新后的权重透明服务于后续会话。

### 7.4 认证机制

Online模式使用双层认证系统：

| 认证类型 | Token来源 | 可访问端点 |
|----------|----------|-----------|
| **Admin API key** | YAML配置`rollout.agent.admin_api_key` | `start_session`、`export_trajectories` |
| **Session API key** | `/rl/start_session`签发 | `chat/completions`、`set_reward` |

认证头格式：`Authorization: Bearer <token>`

为什么每个session需要唯一API key？因为多个并发Agent应用可能调用同一URL端点，API key与session一一对应，用于区分不同Agent的轨迹，追踪同一session内的交互并设置奖励。

### 7.5 训练工作原理

训练在底层**异步**运行：
1. 外部应用通过gateway与模型交互
2. 每个session的交互与token级数据（logprobs等）一同记录
3. Session结束时（通过refresh或显式结束），轨迹被导出
4. 收集足够轨迹（由`train_dataset.batch_size`控制），AReaL执行一次训练步骤
5. 更新后的模型权重透明地服务于后续session，Agent无需重启

### 7.6 错误处理

| HTTP Code | 含义 | 处理建议 |
|-----------|------|----------|
| 400 | 请求参数错误 | 检查JSON格式和必填参数 |
| 401 | 认证缺失/无效 | 检查API key和Authorization头格式 |
| 403 | Admin API key无效 | 检查admin key是否正确 |
| 409 | API key已绑定到活跃session | 先结束已有session，或使用refresh机制 |
| 429 | 无可用容量（staleness control） | 短暂延迟后重试（默认超时120秒） |
| 500 | 服务器内部错误 | 检查服务日志 |
| 502 | 后端worker不可达 | 检查RL服务是否运行 |

标准错误响应格式：
```json
{"detail": "Missing or malformed Authorization header. Expected 'Bearer <token>'."}
```

### 7.7 完整Python示例（单key刷新机制）

```python
import requests

gateway_url = "http://localhost:8090"
admin_key = "my-secret-admin-key"
task_id = "demo-task"
num_episodes = 2

session_api_key = None

for episode_num in range(1, num_episodes + 1):
    # Step 1: Start/Refresh Session
    start_body = {"task_id": task_id}
    if session_api_key is not None:
        start_body["api_key"] = session_api_key

    resp = requests.post(
        f"{gateway_url}/rl/start_session",
        headers={"Authorization": f"Bearer {admin_key}"},
        json=start_body,
        timeout=130 if session_api_key else 10,
    )
    data = resp.json()
    # v1格式: data["api_key"], data["session_id"]
    # v2格式: data["sessions"][0]["session_api_key"]
    session_api_key = data.get("api_key") or data["sessions"][0]["session_api_key"]

    # Step 2: Chat Completion
    resp = requests.post(
        f"{gateway_url}/chat/completions",
        headers={"Authorization": f"Bearer {session_api_key}"},
        json={
            "model": "default",
            "messages": [{"role": "user", "content": "Solve step by step: What is 12 * 15 + 3?"}],
            "temperature": 0.7,
        },
        timeout=30,
    )
    answer = resp.json()["choices"][0]["message"]["content"]
    print(f"Episode {episode_num} answer: {answer[:80]}...")

    # Step 3: Set Reward
    requests.post(
        f"{gateway_url}/rl/set_reward",
        headers={"Authorization": f"Bearer {session_api_key}"},
        json={"reward": 1.0},
        timeout=10,
    )
```

### 7.8 限制与注意事项

- Online模式兼容`local`、`slurm`、`ray`调度器，但ray下gateway端到端验证尚未完成
- Online模式仅支持**单控制器模式**（不支持SPMD模式）
- 有内置速率限制（staleness control），并发过多返回429
- 设置`drop_retry_orphans: true`可丢弃超时重试导致的孤儿completion

---

## 八、CLI命令参考与配置指南

### 8.1 areal CLI顶层命令

```
areal
├── agent      # 管理Agent服务
├── inf        # 管理推理服务（inference）
├── train      # 运行训练实验
└── logs       # 查看服务日志（agent/inf的子命令）
```

服务类命令（`agent`/`inf`）支持通用子命令：`run`、`ps`、`status`、`logs`、`stop`。

### 8.2 areal agent命令

#### agent run - 启动Agent服务

```bash
areal agent run [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--service` | string | `default` | 服务名称 |
| `--agent` | string | 必填 | Agent导入路径（如`examples.hermes.hermes.HermesAgent`） |
| `--num-pairs` | int | `1` | worker/data-proxy对数 |
| `--admin-api-key` | string | `areal-agent-admin` | 管理API密钥 |
| `--setup-timeout` | float | `120.0` | 启动超时（秒） |
| `--log-level` | choice | `info` | 日志级别：debug/info/warning/error |
| `--force` | flag | false | 强制替换残留服务状态 |

**示例**：
```bash
areal agent run \
  --service default \
  --agent examples.hermes.hermes.HermesAgent \
  --num-pairs 1 \
  --admin-api-key sk-123456 \
  --force
```

#### agent ps - 列出Agent服务

```bash
areal agent ps [--json] [--all]
```
输出列：`SERVICE / STATUS / GATEWAY / AGENT`

#### agent status - 查看服务健康状态

```bash
areal agent status [--service default] [--watch] [--interval 2] [--json]
```

#### agent logs - 查看日志

```bash
areal agent logs --service default --component <component> -f -n 200
```
组件名：`gateway`、`router`、`worker-0`、`proxy-0`、`worker-1`、`proxy-1`...

#### agent stop - 停止服务

```bash
areal agent stop --service default [--grace-period 10] [--force] [--keep-state]
```

### 8.3 areal inf命令

#### inf run - 启动推理服务

```bash
areal inf run [OPTIONS]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--service` | string | `default` | 服务名称 |
| `--port` | int | `8080` | Gateway端口 |
| `--host` | string | `127.0.0.1` | Gateway绑定地址 |
| `--admin-api-key` | string | `areal-admin-key` | 管理API密钥 |
| `--routing-strategy` | choice | `round_robin` | 路由策略：round_robin/least_busy |
| `-d, --detach` | flag | false | 后台守护模式 |
| `--model` | string | None | 启动时直接注册的模型名 |
| `--backend` | string | None | 后端规格，如`sglang:d4`、`vllm:d2t4` |
| `--model-path` | string | None | 模型路径 |
| `--engine-args` | string | `""` | 转发给sglang/vllm的参数 |
| `--proxy-args` | string | `""` | Data-proxy参数 |
| `--force` | flag | false | 强制替换服务状态 |

**示例**：启动时直接注册模型
```bash
areal inf run \
  --service default \
  --port 8080 \
  --admin-api-key areal-admin-key \
  --model qwen-local \
  --backend sglang:d1 \
  --model-path Qwen/Qwen2.5-7B-Instruct \
  --engine-args "--mem-fraction-static 0.8" \
  --detach
```

#### inf ps - 列出推理服务

```bash
areal inf ps [--json] [--all]
```
输出列：`SERVICE / STATUS / BACKEND / MODELS / GATEWAY / PID`

#### inf logs - 查看推理服务日志

```bash
areal inf logs --service default --component <component> -f
```
组件名：`gateway`、`router`、`<model>-worker-<rank>`、`<model>-data-proxy-<rank>`

#### inf stop - 停止推理服务

```bash
areal inf stop --service default [--grace 10] [--force]
```

### 8.4 areal train命令

#### train run - 运行训练实验

```bash
areal train run --config <yaml> --driver <module:func> [OVERRIDES...]
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--config` | Path | 是 | 实验YAML配置文件 |
| `--driver` | string | 是 | Driver入口，格式`module.path:func` |
| `OVERRIDES` | args | 否 | Hydra风格覆盖参数 |

**示例**：
```bash
areal train run \
  --config examples/math/gsm8k_grpo.yaml \
  --driver examples.math.gsm8k_rl:main \
  experiment_name=gsm8k_test trial_name=t1 \
  actor.path=Qwen/Qwen3-1.7B
```

### 8.5 配置覆盖语法

使用Hydra风格覆盖：

| 语法 | 说明 | 示例 |
|------|------|------|
| `key=value` | 覆盖已有配置项 | `actor.optimizer.lr=5e-6` |
| `+key=value` | 新增配置项 | `+sglang.attention_backend=triton` |

**常见覆盖项**：
```bash
# 实验命名
experiment_name=my_run trial_name=t1

# 集群规模
cluster.n_nodes=4 cluster.n_gpus_per_node=8

# 训练超参
actor.optimizer.lr=5e-6
total_train_epochs=20

# 后端配置
rollout.backend=sglang:d2t2
actor.backend=fsdp:d2t2

# 数据集
train_dataset.batch_size=256
```

### 8.6 状态存储位置

- 状态根目录：`~/.areal/`（可通过`AREAL_HOME`环境变量覆盖）
- Agent状态：`~/.areal/agent/`
- 推理服务状态：`~/.areal/inf/`
- 日志目录：`~/.areal/<service-type>/<service-name>/logs/`

---

## 九、代码仓库结构与示例解析

### 9.1 areal/子模块结构

```
areal/
├── api/              # API接口定义（CLI参数、引擎API、奖励API等）
├── dataset/          # 数据集加载器（GSM8K、Geometry3K、HHRLHF等）
├── engine/           # 训练与推理引擎（FSDP、Megatron、SGLang、vLLM）
├── experimental/     # 实验性功能（Archon FP8、OpenAI客户端缓存）
├── infra/            # 基础设施（控制器、启动器、调度器、RPC、沙箱）
├── models/           # 模型实现（FSDP Ulysses、Megatron-Core适配、VLM、Tree Attention）
├── reward/           # 内置奖励函数（GSM8K、Geometry3K、CLEVR Count）
├── tools/            # 开发工具（性能分析、安装验证、许可证检查）
├── trainer/          # 训练器实现（SFT、PPO、DPO、RW）
├── utils/            # 通用工具函数
├── v2/               # v2微服务架构（四大服务）
└── workflow/         # 工作流定义（多轮对话、RLVR、Agent集成）
```

### 9.2 v2/微服务子结构

```
areal/v2/
├── agent_service/       # Agent微服务
│   ├── gateway/         # 公共入口（HTTP/WS）
│   ├── router/          # 会话亲和性路由
│   ├── data_proxy/      # 有状态会话代理（历史管理）
│   ├── worker/          # 无状态Agent执行
│   └── guard/           # 守护进程
├── inference_service/   # 推理微服务
│   ├── gateway/         # Inference Gateway（Online RL端点）
│   ├── router/          # 推理路由
│   ├── data_proxy/      # 推理数据代理（记录token/logprob）
│   ├── guard/           # 守护进程
│   └── backend.py       # SGLang/vLLM后端管理
├── training_service/    # 训练微服务
│   ├── gateway/
│   ├── router/
│   ├── worker/
│   ├── guard/
│   └── awex.py          # 异步权重交换
├── weight_update/       # 权重更新服务
│   ├── gateway/
│   ├── auth.py
│   ├── awex/
│   └── nccl_group.py    # NCCL权重同步组
└── cli/                 # areal CLI实现
    ├── agent/
    ├── inference/
    ├── training/
    └── commands/
```

### 9.3 关键示例解析

#### examples/math/ - 数学推理（入门示例）

GSM8K数学推理，提供15+种RL算法配置：

| 文件 | 用途 |
|------|------|
| `gsm8k_rl.py` | GRPO/PPO等RL训练入口 |
| `gsm8k_sft.py` | SFT训练入口 |
| `gsm8k_grpo.yaml` | GRPO默认配置（最高准确率~79.6%） |
| `gsm8k_*.yaml` | 各种算法配置（PPO/DPO/Dr.GRPO/GSPO/M2PO等） |

**运行命令**：
```bash
areal train run \
  --config examples/math/gsm8k_grpo.yaml \
  --driver examples.math.gsm8k_rl:main \
  experiment_name=gsm8k_test trial_name=t1 \
  scheduler.type=local
```

**推荐超参数**（Qwen2.5-1.5B，8×H800）：lr=1.7e-5，weight decay=0.017，group size=4。

#### examples/hermes/ - Hermes在线RL自进化Agent

基于Nous Research Hermes Agent实现端到端在线RL自进化：

| 文件 | 用途 |
|------|------|
| `hermes.py` | `HermesAgent` - 进程内每会话Hermes AIAgent |
| `hermes_loop.py` | 交互式对话脚本 |
| `start_session.py` | 创建会话密钥 |
| `set_reward.py` | 分配奖励 |
| `train.py` | RL训练入口（嵌入推理gateway） |
| `config.yaml` | 2-GPU默认配置 |

**运行步骤**：
1. 启动训练服务：`uv run python3 examples/hermes/train.py --config ...`
2. 启动Agent服务：`areal agent run --agent examples.hermes.hermes.HermesAgent ...`
3. 创建session：`python examples/hermes/start_session.py ...`
4. 交互产生轨迹：`python examples/hermes/hermes_loop.py ...`
5. 评分：`python examples/hermes/set_reward.py --reward 1.0`

**核心特性**：每个会话一个独立AIAgent实例，DataProxy管理跨轮次上下文，Agent LLM调用流经推理gateway捕获token数据用于RL训练。需至少2张GPU。

#### examples/swe/ - SWE-bench编程Agent

端到端编程Agent RL训练：
- Agent循环、沙箱、奖励计算在独立仓库[AReaL-SWEAgent](https://github.com/areal-project/AReaL-SWEAgent)
- 支持内置`swe`工具Agent和Claude Code (`cc`) Agent
- 需要[AEnvironment](https://github.com/inclusionAI/AEnvironment)沙箱平台（K8s + Helm）

**运行命令**：
```bash
python -m examples.swe.train_swe_rl --config examples/swe/qwen3_30b_a3b_grpo.yaml
```

#### examples/openclaw/ - ZeroClaw黑盒Agent

演示黑盒Agent（ZeroClaw）RL训练，任何OpenAI兼容Agent都可接入：

| 文件 | 用途 |
|------|------|
| `train.py` | RL训练入口 |
| `demo_lifecycle.py` | 一体化生命周期演示 |
| `start_session.py` | 创建/刷新会话 |
| `set_reward.py` | 设置奖励 |

**核心特性**：
- 黑盒Agent无需修改代码，只需替换`base_url`和`api_key`
- 异步训练，收集足够轨迹后自动更新权重，Agent无需重启
- 会话刷新机制：同一API key调用start_session自动结束旧会话导出轨迹

#### examples/tau2/ - Tau2客服Agent

$\tau^2$-Bench客服Agent训练，支持airline/retail/telecom三个领域：
- 提供1.7B到235B MoE的多种规模配置
- 默认启用Tree Training优化前缀计算共享
- 开源模型：[inclusionAI/AReaL-SEA-235B-A22B](https://huggingface.co/inclusionAI/AReaL-SEA-235B-A22B)
- 开源数据集：[inclusionAI/AReaL-tau2-data](https://huggingface.co/datasets/inclusionAI/AReaL-tau2-data)

#### examples/tir/ - 工具集成推理（TIR）

Tool-Integrated Reasoning Agent，数学推理中通过多轮工具调用解决问题：
- 支持Python代码执行（本地/Daytona云沙箱）和数学计算器
- 流式生成时检测工具调用标记，执行后整合结果继续生成
- 基于Qwen2.5-Math-1.5B训练，准确率提升约15%

**工具调用格式**：
- Python：` ```python ... ``` `
- 计算器：`<calculator>表达式</calculator>`

### 9.4 其他示例简表

| 示例目录 | 分类 | 用途 |
|----------|------|------|
| `alignment/` | 对齐 | HHRLHF上的Reward Model和DPO训练 |
| `multi_turn_math/` | Math | 多轮GSM8K数学Agent，concat模式+折扣奖励 |
| `vlm/` | VLM | CLEVR Count/Geometry3K视觉推理GRPO/SFT |
| `vlm_npu/` | VLM | 昇腾NPU上的VLM训练 |
| `countdown/` | 任务 | Countdown数字游戏RL训练 |
| `scaffolding/` | Agent | NVIDIA Scaffoldings框架集成 |
| `terminal_bench/` | Agent | Terminal-Bench终端Agent |
| `camel/` | Agent | CAMEL-AI框架集成 |
| `openai_agents/` | Agent | OpenAI Agents SDK集成 |
| `sandbox_daytona/` | 沙箱 | Daytona云沙箱使用 |
| `skypilot/` | 部署 | SkyPilot云部署配置 |
| `search_agent/` | Agent | 通义千问DeepResearch搜索Agent |
| `distillation/` | 蒸馏 | 在线策略蒸馏示例 |

---

## 十、最佳实践、FAQ、术语表、资源链接

### 10.1 最佳实践

#### 算法性能诊断

**同步vs异步RL**：调试新Agent应用时可切换同步模式（性能降低~2倍但更易调试）：
```yaml
rollout:
  max_head_offpolicyness: 0
actor:
  recompute_logprob: false
  use_decoupled_loss: false
```

**训练奖励不上升诊断步骤**：
1. 训练前先在测试集跑评估建立基线
2. 在测试集而非训练集上跑RL，验证奖励是否上升
3. 测试集不上升→调大batch size/lr，换模型，先SFT
4. 测试集上升训练集不上升→检查数据质量，启用动态过滤`should_accept_fn`

**关键监控指标**：
- `eval-rollout/reward`：测试集奖励（泛化能力主要指标）
- `rollout/reward`：训练集奖励（跟踪进度）
- `ppo/actor/task_reward`：实际用于训练的奖励（动态过滤时与rollout/reward不同）
- `ppo_actor/update/importance_weight`：应接近1.0，偏离则减小`ppo_n_minibatches`
- `ppo_actor/update/behave_imp_weight`：应接近1.0，偏离则配置`rejection_sampling`或减小`max_head_offpolicyness`
- `ppo_actor/no_eos_ratio`：超过0.05时增大`max_new_tokens`

#### Agent工作流编写

- **全程使用Async/Await**：所有workflow方法应为async，禁止阻塞调用（`engine.generate()`、同步OpenAI客户端）
- **封装昂贵奖励函数**：用`AsyncRewardWrapper`将CPU密集/外部API奖励分派到进程池
- **避免重初始化**：昂贵设置放在`__init__`而非`arun_episode`中
- **复用HTTP客户端**：通过`workflow_context.get_aiohttp_session()`获取共享客户端

#### 调试指南

**使用持久化推理服务器调试**：
1. 先启动独立SGLang/vLLM服务器
2. 用OpenAI兼容客户端连接，单样本调试Agent
3. 高并发测试验证Agent能处理并发
4. 再与AReaL集成，确保`max_head_offpolicyness`和`max_concurrent_rollouts`足够大

**训练挂起/死锁调试**：
1. `nvidia-smi`查看GPU利用率，`ps aux`查看进程
2. 用py-spy dump所有rank调用栈：
   ```bash
   pip install py-spy
   for pid in $(ps aux | grep 'python.*areal' | grep -v grep | awk '{print $2}'); do
     echo "===== PID $pid ====="; py-spy dump --pid $pid
   done
   ```
3. 设置调试环境变量：
   ```bash
   export NCCL_DEBUG=INFO
   export TORCH_DISTRIBUTED_DEBUG=DETAIL
   export NCCL_TIMEOUT=300
   ```

#### OOM问题处理

**关键内存参数**（`batch_size`不影响峰值内存）：
- `actor.backend`/`rollout.backend`：并行策略
- `train_dataset.max_length`：最大prompt长度
- `gconfig.max_new_tokens`：生成token数
- `actor.mb_spec.max_tokens_per_mb`：每微批次token数（控制训练内存）
- `max_concurrent_rollouts`：并行生成请求数

**生成阶段OOM**：
1. 减少`max_concurrent_rollouts`（最有效）
2. 增加张量并行度：`sglang:d2t2`
3. 降低SGLang`mem_fraction_static`到0.8

**训练阶段OOM**：
1. 减小`max_tokens_per_mb`
2. 启用`gradient_checkpointing: true`
3. 启用5D并行（Ulysses SP：`fsdp:d2c2`，TP：`fsdp:d2t2`，PP/EP：Megatron/Archon）
4. 启用逐层优化器步骤：`actor.fsdp.per_layer_optim_step: true`
5. 切换到bf16优化器：`optimizer.type: adam_bf16`（不要用原生adam配bf16）
6. 内存高效加载：`actor.fsdp.memory_efficient_load: true`

#### 性能Profiling

AReaL提供`perf_tracer`输出Chrome Trace格式，可在Perfetto（https://ui.perfetto.dev/）可视化：

```yaml
perf_tracer:
  enabled: true
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  fileroot: ${cluster.fileroot}
  save_interval: 1
```

转换并查看：
```bash
python -m areal.tools.perf_trace_converter logs/**/perf_tracer/traces-*.jsonl merged.json
```

### 10.2 常见问题FAQ（精选）

**安装类**：
- **flash-attn编译太慢**：安装预编译wheel（见2.4节）
- **SGLang和vLLM能同时安装吗？**：不能，版本互斥，切换时替换pyproject文件
- **如何验证安装？**：运行`uv run python3 areal/tools/validate_installation.py`

**训练类**：
- **奖励一直不上升？**：按诊断步骤：先建基线→测试集验证→调参/换模型→检查数据质量
- **importance_weight偏离1？**：减小`ppo_n_minibatches`（设为1理论上精确等于1）
- **SAPO不生效？**：SAPO需要`use_decoupled_loss: false`
- **IcePop/KPop不生效？**：需要`use_decoupled_loss: true`

**分布式类**：
- **训练挂起无输出？**：用py-spy dump所有rank栈，看是否在集合操作上等待；设置`NCCL_TIMEOUT=300`
- **GPU数量不匹配？**：确保rollout+actor总GPU数等于`n_nodes * n_gpus_per_node`
- **多节点checkpoint保存失败？**：确保所有节点挂载相同共享存储，`cluster.fileroot`指向共享目录

**Online RL类**：
- **401未授权？**：管理端点用admin key，chat用session key（start_session签发）
- **409 key已绑定？**：使用refresh机制（传入旧api_key）而非创建新key
- **429无容量？**：等待几秒重试，训练pipeline循环需要时间
- **更新模型何时生效？**：每个训练步后自动加载，始终使用最新模型

**v2.0类**：
- **~/.areal/目录作用？**：存储inf/agent服务本地状态
- **Worker和DataProxy关系？**：1:1配对，DataProxy有状态管理会话历史，Worker无状态执行Agent
- **AgentRunnable协议是什么？**：实现`async def run(self, request, *, emitter) -> AgentResponse`即可

### 10.3 核心术语表（精选）

| 术语 | 中文解释 |
|------|---------|
| RL（Reinforcement Learning） | 强化学习，通过交互奖励学习最优策略 |
| GRPO（Group Relative Policy Optimization） | 组相对策略优化，组内归一化优势，无需critic |
| PPO（Proximal Policy Optimization） | 近端策略优化，经典RL算法，需critic通过GAE估计优势 |
| DPO（Direct Preference Optimization） | 直接偏好优化，无需奖励模型或在线rollout |
| GSPO（Group Sequence Policy Optimization） | 组序列策略优化，序列级几何平均重要性比率 |
| DAPO（Decoupled Alignment Policy Optimization） | 解耦对齐策略优化，非对称裁剪+动态采样 |
| SFT（Supervised Fine-Tuning） | 监督微调，在标注数据上微调 |
| DP/TP/PP/EP | 数据/张量/流水线/专家并行，分布式训练并行策略 |
| FSDP（Fully Sharded Data Parallelism） | 完全分片数据并行，分片参数/梯度/优化器状态 |
| On-policy/Off-policy | 在策略/离策略，训练数据由当前/旧策略生成 |
| Staleness | 陈旧度，异步RL中rollout策略落后训练策略的版本数 |
| Importance Weight | 重要性权重，当前/行为策略概率比，用于离策略校正 |
| Rollout | 轨迹采样，使用策略生成序列的过程 |
| Actor/Critic | Actor/策略网络生成文本，Critic/价值网络估计价值 |
| Workflow | 工作流，定义rollout生成和奖励计算 |
| Gateway/Router/Worker | 网关（API入口）/路由器（负载均衡）/工作节点（执行） |
| Data Proxy | 数据代理，会话管理、记录交互、导出轨迹 |
| Scheduler | 调度器，管理集群资源分配（local/ray/slurm） |
| Weight Update | 权重更新，训练后新权重同步到推理后端 |
| LoRA（Low-Rank Adaptation） | 低秩适配，参数高效微调技术 |
| MoE（Mixture of Experts） | 混合专家模型，多专家子网络+门控网络 |
| VLM（Vision-Language Model） | 视觉语言模型，多模态模型 |
| Session/Task | 会话（一次完整交互周期）/任务（单个数据点） |
| AgentRunnable | v2 Worker上运行的Agent协议类 |
| Async/Await | Python异步编程模式，并发I/O不阻塞 |

### 10.4 资源链接

#### 官方资源

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/areal-project/AReaL |
| 中文文档 | https://areal-project.github.io/AReaL/zh/ |
| arXiv论文（AReaL系统） | https://arxiv.org/abs/2505.24298 |
| arXiv论文（AReaL 2.0微服务） | https://arxiv.org/abs/2607.01120 |
| Hugging Face模型与数据 | https://huggingface.co/collections/inclusionAI/ |
| Docker镜像 | `ghcr.io/areal-project/areal-runtime:v2.0.0-sglang` / `v2.0.0-vllm` |
| Ask DeepWiki | https://deepwiki.com/areal-project/AReaL |

#### 核心算法论文

| 算法 | 链接 |
|------|------|
| GRPO | https://arxiv.org/pdf/2402.03300 |
| PPO | https://arxiv.org/pdf/2203.02155 |
| DPO | https://arxiv.org/abs/2305.18290 |
| GSPO | https://arxiv.org/abs/2507.18071 |
| DAPO | https://arxiv.org/abs/2503.14476 |
| M2PO | https://arxiv.org/abs/2510.01161 |
| AReaL-SEA客服Agent | https://arxiv.org/abs/2601.22607 |

#### 依赖项目文档

| 项目 | 链接 |
|------|------|
| SGLang | https://docs.sglang.io/ |
| vLLM | https://docs.vllm.ai/ |
| PyTorch FSDP | https://pytorch.org/docs/stable/fsdp.html |
| Megatron-LM | https://github.com/NVIDIA/Megatron-LM |
| Ray/SkyPilot | https://www.ray.io/ / https://docs.skypilot.co/ |
| Perfetto/py-spy/uv | https://ui.perfetto.dev/ / https://github.com/benfred/py-spy / https://docs.astral.sh/uv/ |

#### 社区资源

| 资源 | 链接 |
|------|------|
| GitHub Discussions | https://github.com/areal-project/AReaL/discussions |
| 社区仓库 | https://github.com/areal-project/community |
| 贡献指南 | https://github.com/areal-project/community/blob/main/CONTRIBUTING.md |
| 路线图 | https://github.com/areal-project/AReaL/blob/main/ROADMAP.md |

#### 同步/异步RL快速配置参考

```yaml
# 异步RL（默认，推荐，高吞吐量）
rollout:
  max_head_offpolicyness: 4
actor:
  use_decoupled_loss: true
  recompute_logprobs: true

# 同步RL（调试用，慢~2倍）
rollout:
  max_head_offpolicyness: 0
actor:
  use_decoupled_loss: false
  recompute_logprob: false
```

---

> 📚 **继续学习**：本文为实战教程篇，异步RL核心原理、解耦PPO数学推导、参数重分配机制等深入内容，请阅读 [AReaL Agent RL Wiki：异步强化学习系统概念与原理](./areal-agent-rl-wiki.md)。
