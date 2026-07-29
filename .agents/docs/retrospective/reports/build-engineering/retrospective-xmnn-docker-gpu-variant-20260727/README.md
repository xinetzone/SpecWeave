---
id: retrospective-xmnn-docker-gpu-variant-20260727
title: "XMNN Docker GPU变体构建实践复盘"
date: 2026-07-27
type: retrospective
category: build-engineering
source: "用户请求torch-gpu镜像提交 + xmtools Docker GPU变体创建实践"
tags: [docker, gpu, pytorch, cuda, xmnn, image-building, variant]
status: complete
chain: R→I→E
pattern_extracted: docker-gpu-variant-quick-creation
---

# XMNN Docker GPU变体构建实践复盘

## 概述

本次任务为 xmtools 项目创建 PyTorch GPU 版本的 Docker 构建环境，支持 CUDA GPU 加速。用户已在运行容器中手动安装好 PyTorch GPU 版本（torch 2.13.0 + CUDA 13.0.3），需要将环境固化为可用镜像并提供可复现的构建配置。

- **时间**：2026-07-27
- **场景**：知识沉淀（R→I→E + 导出）
- **产出物**：Docker GPU变体配置 + 可复用模式 + 复盘报告

---

## R：客观事实清单

| # | 事实 |
|---|------|
| F1 | 任务时间：2026-07-27，任务来源：用户请求"提交torch-gpu版本镜像" |
| F2 | 用户在容器 `root@11ab59c8235d` 内执行了 pip install，安装了 torch-2.13.0、cuda-toolkit-13.0.3、cuda-bindings-13.3.1、triton-3.7.1、nvidia-cuda-runtime-cu13、nvidia-cudnn-cu13、nvidia-cublas-cu13 等包 |
| F3 | 原 Docker 配置目录：[dev-llvm22/](../../../../../../external/chaos/xmtools/docker/dev-llvm22/)，Dockerfile 第114行安装 PyTorch 时使用 `--index-url https://download.pytorch.org/whl/cpu` 强制 CPU 版本 |
| F4 | 原 Docker 配置包含：Dockerfile(199行)、build-docker.sh、build-and-test.sh、run-build.sh、verify-wheel.sh、miniconda.sh |
| F5 | 新建目录：[dev-llvm22-torch-gpu/](../../../../../../external/chaos/xmtools/docker/dev-llvm22-torch-gpu/) |
| F6 | 新建文件：[Dockerfile](../../../../../../external/chaos/xmtools/docker/dev-llvm22-torch-gpu/Dockerfile)（215行） |
| F7 | 新建文件：[build-docker.sh](../../../../../../external/chaos/xmtools/docker/dev-llvm22-torch-gpu/build-docker.sh)（119行） |
| F8 | miniconda.sh 复制操作被 sandbox 拒绝，改为在 build-docker.sh 中自动创建软链接逻辑 |
| F9 | Dockerfile GPU 版本主要变更点：(1)移除torch安装的CPU index-url限制；(2)添加CUDA库路径LD_LIBRARY_PATH；(3)验证步骤增加torch.cuda检测 |
| F10 | 提供了两种镜像获取方案：方案一docker commit（快速提交）；方案二Dockerfile构建（可复现） |
| F11 | GPU容器运行要求：docker run需加`--gpus all`参数；宿主机需NVIDIA驱动+nvidia-container-toolkit |
| F12 | PyTorch pip GPU包自带nvidia-cuda-*系列依赖，不需要宿主机完整安装CUDA Toolkit |
| F13 | 项目硬约束：Docker基础镜像必须是ubuntu:26.04；Conda必须配置北外镜像；pip必须配置清华镜像；LLVM版本必须为22.1.8 |
| F14 | 未创建build-and-test.sh/run-build.sh/verify-wheel.sh（可复用dev-llvm22中的脚本） |

---

## I：核心洞察

### 洞察 I1：Docker 环境变体管理采用"目录复制+差异修改"模式存在维护成本

- **陈述**：Docker GPU变体通过复制整个dev-llvm22目录再修改关键行实现，存在文件重复
- **证据**：F3,F4,F5,F6,F7,F14——Dockerfile 90%内容与CPU版相同，仅三处差异
- **本质**：CPU和GPU版共享90%构建逻辑，差异仅在PyTorch安装源和少量环境变量。复制目录导致后续基础依赖更新需要同步修改两个Dockerfile，易产生漂移
- **建议**：可考虑使用Dockerfile多阶段构建或ARG参数控制CPU/GPU变体，或使用base镜像+ONBUILD触发器模式

### 洞察 I2：PyTorch GPU镜像的CUDA库路径配置需要显式处理

- **陈述**：PyTorch pip包自带的nvidia-cuda-*库存放于site-packages/nvidia/子目录，不在系统默认库搜索路径
- **证据**：F9,F12——Dockerfile中需要手动设置多个LD_LIBRARY_PATH路径
- **本质**："import torch能检测CUDA"但"原生代码链接CUDA失败"是常见坑——Python能找到包内库，但cmake/编译的C++代码依赖系统LD_LIBRARY_PATH
- **建议**：提供环境初始化脚本自动扫描site-packages/nvidia/*/lib添加到路径，而非手动枚举

### 洞察 I3："快速commit"与"可复现Dockerfile"是两种不同需求场景，需同时提供

- **陈述**：用户已在运行容器中手动安装好GPU环境，此时docker commit是最快路径；但Dockerfile是长期可复现的标准方式
- **证据**：F2,F10——同时提供了commit和Dockerfile两种方案
- **本质**：工程实践中"快速验证"和"可复现构建"是两个不同阶段的需求，不应强行二选一。commit适合即时使用，Dockerfile适合长期维护
- **建议**：建立"快速方案+标准方案"双轨交付模式

---

## E：萃取模式

本次实践沉淀了一个可复用模式：

**模式名称**：Docker GPU变体快速创建模式
**模式文件**：[docker-gpu-variant-quick-creation.md](../../../patterns/code-patterns/docker-gpu-variant-quick-creation.md)
**成熟度**：observed（观察级，已验证于xmtools项目）

### 模式核心要点

1. **双轨交付**：同时提供 docker commit（快速固化）和 Dockerfile（可复现构建）两种方案
2. **关键差异点**：GPU变体相对于CPU版只需修改三处：移除CPU索引、添加CUDA库路径、增加GPU验证
3. **大文件共享**：miniconda.sh等大文件使用软链接而非复制，避免重复存储
4. **构建时验证边界**：Dockerfile构建阶段不调用`torch.cuda.is_available()`（构建时无GPU设备），只验证CUDA版本和库文件
5. **运行时要求**：容器运行必须加`--gpus all`，宿主机需nvidia-container-toolkit

---

## 产出物清单

| 产出物 | 路径 | 说明 |
|--------|------|------|
| GPU版Dockerfile | [Dockerfile](../../../../../../external/chaos/xmtools/docker/dev-llvm22-torch-gpu/Dockerfile) | PyTorch GPU版本Dockerfile（215行） |
| GPU构建脚本 | [build-docker.sh](../../../../../../external/chaos/xmtools/docker/dev-llvm22-torch-gpu/build-docker.sh) | GPU镜像构建脚本（119行，含自动软链接逻辑） |
| 可复用模式 | [docker-gpu-variant-quick-creation.md](../../../patterns/code-patterns/docker-gpu-variant-quick-creation.md) | Docker GPU变体创建模式文档 |
| 复盘报告 | [README.md](README.md) | 本文档 |

---

## 快速使用指南

### 方式一：从当前容器快速提交（即时使用）

在宿主机执行（不是容器内）：

```bash
# 验证容器GPU环境
docker exec 11ab59c8235d python -c "
import torch
print(f'torch: {torch.__version__}')
print(f'CUDA: {torch.version.cuda}')
print(f'CUDA available: {torch.cuda.is_available()}')
"

# 提交镜像
docker commit \
    -m "XMNN dev with PyTorch GPU (CUDA 13)" \
    -a "XMNN Team" \
    11ab59c8235d \
    xmnn-dev:llvm22-torch-gpu

# 运行GPU容器
docker run --rm -it --gpus all \
    --user root --entrypoint '' \
    -v /path/to/chaos:/workspace \
    -w /workspace/xmtools \
    xmnn-dev:llvm22-torch-gpu bash -l
```

### 方式二：从Dockerfile构建（可复现）

```bash
cd external/chaos/xmtools/docker/dev-llvm22-torch-gpu
ln -sf ../dev-llvm22/miniconda.sh .  # 软链接共享大文件
bash build-docker.sh
```

---

## 质量门记录

| 质量门 | 阶段 | 结果 | 说明 |
|--------|------|------|------|
| G1 | R（事实） | ✅ PASS | 事实清单无因果推断词，纯客观描述（14条事实） |
| G2 | I（洞察） | ✅ PASS | 3条洞察均含完整四元组（陈述/证据/本质/建议） |
| G3 | E（萃取） | ✅ PASS | 模式可迁移到TensorFlow/ONNX Runtime/JAX等≥5个场景 |

[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S7 | event=CHAIN_COMPLETED | session=sc-20260727-docker-gpu-variant | msg=方法论编排完成：R→I→E链路执行完毕，报告已导出
