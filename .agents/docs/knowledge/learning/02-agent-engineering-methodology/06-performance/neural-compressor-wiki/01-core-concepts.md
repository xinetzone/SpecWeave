---
id: "neural-compressor-wiki-core-concepts"
title: "核心概念与架构"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html"
summary: "Intel Neural Compressor 的核心概念、模型压缩技术分类、架构设计与工作流程详解。"
tags: ["neural-compressor", "architecture", "core-concepts", "workflow"]
---

# 核心概念与架构

## 模型压缩基本概念

模型压缩（Model Compression）是一系列技术的统称，旨在减少深度学习模型的计算和存储需求，同时尽可能保持模型精度。在实际部署中，模型压缩可以带来以下好处：

- **减小模型体积**：降低存储空间和内存带宽需求
- **提升推理速度**：减少计算量，实现更低延迟
- **降低功耗**：在边缘设备和数据中心中减少能源消耗
- **支持部署在资源受限环境**：使大模型能够在消费级硬件上运行

量化（Quantization）是最常用的模型压缩技术之一，它通过将模型权重和/或激活值从高精度数据类型（如 FP32）转换为低精度数据类型（如 INT8、FP8、INT4）来实现压缩。

## 量化技术分类

Intel Neural Compressor 支持多种量化技术，适用于不同场景：

### 1. 静态量化（Static Quantization）

静态量化又称训练后静态量化（Post-Training Static Quantization, PTQ-S），是最常用的量化方式之一。

**工作原理**：
- 权重在量化前就确定了缩放因子
- 激活值的缩放因子通过在校准数据集上运行前向传播来收集统计信息后确定
- 量化后的模型在推理时直接使用预计算的缩放因子

**适用场景**：
- CNN 等计算机视觉模型
- 需要高推理性能的场景
- 有代表性校准数据集可用的情况

**支持后端**：intel-extension-for-pytorch (INT8)、TorchDynamo (INT8)、Intel Gaudi AI accelerator (FP8)

### 2. 动态量化（Dynamic Quantization）

动态量化又称训练后动态量化（Post-Training Dynamic Quantization, PTQ-D）。

**工作原理**：
- 权重在量化前确定缩放因子
- 激活值的缩放因子在推理时动态计算
- 无需预先准备校准数据集

**适用场景**：
- RNN、Transformer 等 NLP 模型
- 快速原型验证
- 没有校准数据集的情况

**支持后端**：TorchDynamo

### 3. 仅权重量化（Weight-Only Quantization）

仅权重量化只压缩模型的权重部分，激活值在推理时仍然保持高精度（如 FP16/BF16）。

**支持算法**：

| 算法 | 全称 | 特点 |
|------|------|------|
| **RTN** | Round to Nearest | 最简单的舍入量化，无需额外数据 |
| **GPTQ** | - | 基于二阶信息的后训练量化方法，精度较高 |
| **AWQ** | Activation-aware Weight Quantization | 考虑激活值分布的权重量化 |
| **AutoRound** | - | Intel 提出的先进量化算法，支持多种低精度格式 |
| **TEQ** | Trainable Equivalent Transformation | 可训练等价变换量化 |
| **HQQ** | Half-Quadratic Quantization | 基于半二次优化的快速量化方法 |

**适用场景**：
- 大语言模型（LLM）部署
- 显存/内存受限场景
- 追求快速量化流程

### 4. FP8 量化（FP8 Quantization）

FP8 是一种 8 位浮点数据格式，包括 E4M3（4 位指数，3 位尾数）和 E5M2（5 位指数，2 位尾数）两种变体。相比 INT8，FP8 能更好地表示长尾分布，特别适合大模型和 Transformer 架构。

**工作模式**：
- 静态量化：使用校准数据集确定缩放因子
- 动态量化：推理时动态计算，支持 Linear、FusedMoE 等算子
- KV Cache/Attention 静态量化（实验性，通过 AutoRound）

**支持硬件**：Intel Gaudi AI 加速器、Intel GPU（部分支持）

### 5. SmoothQuant

SmoothQuant 是一种专门针对大语言模型设计的量化技术，通过数学变换将激活值的难度转移到权重上，从而可以直接使用 INT8 量化而不显著损失精度。

**核心思想**：
- 大模型激活值中存在离群点（outliers），导致直接量化困难
- 通过逐通道缩放因子，在数学上等价地将难度从激活值转移到权重
- 变换后可以直接应用标准的 INT8 权重量化和激活量化

**支持后端**：intel-extension-for-pytorch

### 其他量化技术

- **MX 量化（Microscaling）**：实验性支持 MXFP8/MXFP4 微缩放数据格式
- **NVFP4 量化**：实验性支持 NVFP4 低精度格式
- **混合精度（Mixed Precision）**：自动为不同层选择最优精度配置
- **量化感知训练（QAT）**：在训练过程中插入伪量化节点，模拟量化误差，通常能获得比 PTQ 更高的精度

## INC 架构概览

Intel Neural Compressor 采用分层架构设计，为不同框架提供统一的 API 抽象。以 PyTorch 后端为例，核心设计理念是复用 PyTorch 原生的 `prepare`/`convert` API 风格，同时通过 `Quantizer` 基类提供灵活的自定义扩展能力。

### 核心工作流：Prepare → Convert → Autotune

Intel Neural Compressor 提供三种主要使用场景，对应三类核心 API：

#### 1. 一次性量化：Prepare & Convert

这是最基础的量化工作流，分为两个阶段：

**Prepare 阶段**：
- 在模型中插入观察者（Observer）
- 观察者用于监控校准过程中输入和输出张量的分布
- 准备好的模型可以在校准数据集上运行以收集统计信息

```python
def prepare(model, quant_config, inplace=True, example_inputs=None):
    """准备模型进行校准，插入观察者"""
```

**Convert 阶段**：
- 根据收集到的统计信息计算量化参数
- 将观察者替换为实际的量化/反量化算子
- 输出最终的量化模型

```python
def convert(model, quant_config=None, inplace=True):
    """将准备好的模型转换为量化模型"""
```

#### 2. 自动调优：Autotune

当不确定哪种量化配置能获得最佳精度-性能权衡时，可以使用 Autotune 自动搜索最优配置：

```python
def autotune(model, tune_config, eval_fn, eval_args=None,
             run_fn=None, run_args=None, example_inputs=None):
    """自动调优主入口，搜索最优量化配置"""
```

**工作原理**：
- 用户定义搜索空间（量化位宽、算法、算子配置等）和评估函数
- Autotune 自动尝试不同配置组合
- 根据评估结果选择满足精度要求的最快模型

#### 3. 模型保存与加载

量化后的模型可以保存到磁盘，也可以直接加载已量化的模型（包括 HuggingFace 格式的预量化模型）：

```python
def save(self, output_dir="./saved_results"):
    """保存量化模型"""

def load(output_dir="./saved_results", model=None):
    """加载量化模型，支持 HuggingFace 格式自动转换"""
```

> **注意**：首次加载 HuggingFace 格式（如 GPTQ）的模型时，Neural Compressor 会自动将其转换为对应后端格式并缓存，因此首次加载可能较慢。

## 典型使用工作流

以 PyTorch 后端的 FP8 量化为例，完整的量化流程如下：

### 步骤 1：导入必要模块

```python
from neural_compressor.torch.quantization import FP8Config, prepare, convert
import torch
import torchvision.models as models
```

### 步骤 2：加载模型并配置量化参数

```python
model = models.resnet18()
qconfig = FP8Config(fp8_config="E4M3")  # 使用 E4M3 FP8 格式
```

### 步骤 3：准备模型（插入观察者）

```python
model = prepare(model, qconfig)
```

### 步骤 4：校准（运行前向传播收集统计信息）

```python
# 使用代表性数据进行校准
model(torch.randn(1, 3, 224, 224).to("hpu"))
```

### 步骤 5：转换为量化模型

```python
model = convert(model)
```

### 步骤 6：使用量化模型进行推理

```python
output = model(torch.randn(1, 3, 224, 224).to("hpu")).to("cpu")
```

### 步骤 7（可选）：保存模型

```python
model.save("./quantized_resnet18")
```

### 步骤 8（可选）：加载已保存模型

```python
from neural_compressor.torch.quantization import load
model = load("./quantized_resnet18")
```

## 架构设计特点

1. **Torch-like API 设计**：对于 PyTorch 用户，API 风格与 PyTorch 原生量化保持一致，降低学习成本
2. **细粒度算子支持**：量化方法可以细粒度应用到 `torch.nn.Module` 级别
3. **可扩展性**：通过 `Quantizer` 基类，便于自定义新的量化算法
4. **自动后端检测**：自动检测可用后端（intel-extension-for-pytorch、TorchDynamo、Gaudi 等）
5. **算子级配置**：支持通过 `set_local` 方法为特定算子或层设置不同的量化配置

```python
# 示例：为不同层设置不同配置
quant_config = RTNConfig()  # 全局默认 4-bit
quant_config.set_local(".*mlp.*", RTNConfig(bits=8))  # MLP 层使用 8-bit
quant_config.set_local("Conv1d", RTNConfig(dtype="fp32"))  # Conv1d 不量化
```

> **未来规划**：Neural Compressor 计划提供通用的设备无关 Q-DQ（量化-反量化）模型表示，实现"一次量化，任意部署"的目标。

---

[← 上一章：教程总览](00-overview.md) | [下一章：安装指南 →](02-installation.md)
