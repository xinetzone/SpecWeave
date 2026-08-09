---
id: "neural-compressor-wiki-installation"
title: "安装指南"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/installation_guide.html"
summary: "Intel Neural Compressor PyTorch 后端的安装步骤、依赖说明与不同硬件环境的配置要点。"
tags: ["neural-compressor", "installation", "pytorch", "setup"]
---

# 安装指南

本章将详细介绍 Intel® Neural Compressor 的安装流程，包括前置条件检查、不同硬件平台的框架依赖安装、以及安装验证方法。

## 前置条件（Prerequisites）

在安装 Neural Compressor 之前，请确保您的环境满足以下要求：

### 1. Python 版本要求

**Python（蟒蛇编程语言）**：推荐 **Python 3.11 或更高版本**（支持 3.10、3.11、3.12、3.13）。

您可以通过以下命令检查当前 Python 版本：

```shell
python --version
```

如果您的 Python 版本低于 3.10，建议使用 conda 或 pyenv 等工具创建新版本的虚拟环境。

### 2. 操作系统支持

经过官方验证的操作系统环境包括：

| 操作系统 | 版本 |
|---------|------|
| Ubuntu | 24.04 |
| macOS | Ventura 13.5 及以上 |
| Windows | 11 |

> **注意**：如果在安装过程中遇到编译问题，请先查阅官方 [FAQ（常见问题解答）](https://intel.github.io/neural-compressor/latest/docs/source/faq.html)。

## 框架依赖安装（Framework Dependencies）

Intel Neural Compressor 支持 PyTorch 框架在 **CPU（中央处理器）**、**GPU（图形处理器）** 和 **HPU（Habana 处理单元，即 Intel Gaudi AI 加速器）** 三种硬件平台上运行。请根据您的目标硬件环境安装对应的 PyTorch 版本和扩展。

### 选项 1：CPU 平台安装

对于通用 CPU 环境，首先安装 CPU 版本的 PyTorch：

```shell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

为了在 Intel CPU 上获得最佳性能，推荐安装 **Intel Extension for PyTorch（IPEX，英特尔 PyTorch 扩展）**：

- 安装指南：[intel-extension-for-pytorch for CPU](https://intel.github.io/intel-extension-for-pytorch/cpu/latest/)

IPEX 提供了针对 Intel 硬件的深度优化，包括 INT8 量化算子支持和 CPU 特定性能调优。

### 选项 2：Intel GPU 平台安装

对于 Intel 数据中心 GPU（Flex 系列/Max 系列）或 Intel Arc 显卡，需要安装 GPU 版本的 PyTorch 和对应的 IPEX 扩展：

- 安装指南：[intel-extension-for-pytorch for Intel GPU](https://intel.github.io/intel-extension-for-pytorch/xpu/latest/)

请按照官方文档配置好 GPU 驱动和 oneAPI 基础工具包后，再安装 IPEX。

### 选项 3：Intel Gaudi AI 加速器（HPU）平台

Intel Gaudi 系列 AI 加速器（Gaudi2、Gaudi3）推荐使用官方预配置的 **Docker（容器化技术）** 镜像，镜像中已预装了适配的 PyTorch 版本和 Habana 软件栈。

- Docker 镜像获取：[Habana Labs 安装指南](https://docs.habana.ai/en/latest/Installation_Guide/Bare_Metal_Fresh_OS.html#bare-metal-fresh-os-single-click)

启动 Gaudi Docker 容器示例命令：

```shell
docker run -it --runtime=habana \
  -e HABANA_VISIBLE_DEVICES=all \
  -e OMPI_MCA_btl_vader_single_copy_mechanism=none \
  --cap-add=sys_nice \
  --net=host --ipc=host \
  vault.habana.ai/gaudi-docker/1.24.0/ubuntu24.04/habanalabs/pytorch-installer-2.10.0:latest
```

> **重要提示 - Gaudi 版本兼容性**：
>
> Intel Neural Compressor 与 Gaudi Software Stack（Habana 软件栈）之间存在严格的版本对应关系。安装前请务必查阅官方 [版本映射表](https://intel.github.io/neural-compressor/latest/docs/source/gaudi_version_map.html)，确保使用匹配的版本组合，否则可能出现兼容性问题。
>
> 此外，自 Habana 软件栈 1.21.0 版本起，`PT_HPU_LAZY_MODE=0` 成为默认设置，但大多数低精度函数（如 `convert_from_uint4`）不支持此模式，建议设置 `PT_HPU_LAZY_MODE=1` 以保持兼容性。

### 选项 4：其他平台（AMD CPU、ARM CPU、NVIDIA GPU）

对于非 Intel 硬件平台，可以直接从 PyTorch 官方获取对应版本：

- 安装指南：[PyTorch 官方安装页面](https://pytorch.org/get-started/locally)

> **注意**：Neural Compressor 在这些平台上仅经过有限测试，部分量化功能（如 Intel 特定硬件优化）可能不可用。

## 安装 Neural Compressor

### 通过 PyPI 安装（推荐）

**PyPI（Python Package Index，Python 包索引）** 是最简便的安装方式。根据您使用的深度学习框架，选择对应的安装包：

```shell
# PyTorch 框架扩展 API + PyTorch 依赖（推荐）
pip install neural-compressor-pt

# TensorFlow 框架扩展 API + TensorFlow 依赖
pip install neural-compressor-tf

# JAX 框架扩展 API + JAX 依赖（v3.9 及以上版本支持）
pip install neural-compressor-jax
```

您也可以先安装基础包，再自行安装框架依赖：

```shell
# 仅安装框架扩展 API，不包含框架依赖
pip install neural-compressor

# 或使用 extras 语法按需安装对应框架
pip install "neural-compressor[pt]"   # PyTorch
pip install "neural-compressor[tf]"   # TensorFlow
pip install "neural-compressor[jax]"  # JAX
```

### 从源码安装（高级用户）

如果您需要使用最新开发版本或参与贡献，可以从 GitHub 源码安装：

```shell
# 克隆仓库
git clone https://github.com/intel/neural-compressor.git
cd neural-compressor

# 切换到最新稳定版本标签（main 分支可能不稳定）
git fetch --tags && git checkout "$(git tag -l 'v*' --sort=-v:refname | head -n 1)"

# 仅安装 PyTorch 版本
INC_PT_ONLY=1 pip install .

# 仅安装 TensorFlow 版本
# INC_TF_ONLY=1 pip install .

# 仅安装 JAX 版本（v3.8 及以上支持）
# INC_JAX_ONLY=1 pip install .
```

## 安装验证（Verification）

安装完成后，通过以下步骤验证 Neural Compressor 是否安装成功：

### 步骤 1：验证包导入

打开 Python 解释器，尝试导入核心模块：

```python
import neural_compressor
print(f"Neural Compressor 版本: {neural_compressor.__version__}")
```

如果没有报错并输出版本号，说明基础包安装成功。

### 步骤 2：验证 PyTorch 扩展

对于 PyTorch 用户，进一步验证量化模块：

```python
from neural_compressor.torch.quantization import (
    RTNConfig,
    prepare,
    convert,
    load
)
print("PyTorch 量化模块导入成功！")
```

### 步骤 3：运行简单功能测试

执行一个简单的权重量化测试，确认完整流程可以运行：

```python
import torch
import torch.nn as nn
from neural_compressor.torch.quantization import RTNConfig, prepare, convert

# 定义一个简单模型
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 5)
    
    def forward(self, x):
        return self.fc(x)

# 创建模型并量化
model = SimpleModel()
qconfig = RTNConfig(bits=4)  # 4-bit 仅权重量化
model = prepare(model, qconfig)
model = convert(model)

# 测试推理
x = torch.randn(1, 10)
output = model(x)
print(f"量化模型推理成功！输出形状: {output.shape}")
```

如果上述代码正常运行并输出结果，说明 Neural Compressor 已成功安装并可以正常使用。

---

[← 上一章：核心概念与架构](01-core-concepts.md) | [下一章：快速开始 →](03-quickstart.md)

