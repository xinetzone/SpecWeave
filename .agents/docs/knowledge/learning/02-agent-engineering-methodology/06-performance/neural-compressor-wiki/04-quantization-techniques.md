---
id: "neural-compressor-wiki-quantization-techniques"
title: "主流量化技术详解"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html"
summary: "Intel Neural Compressor 支持的主要量化技术：静态量化、动态量化、仅权重量化、FP8 量化、SmoothQuant 的原理、适用场景与使用方法。"
tags: ["neural-compressor", "quantization", "static-quantization", "dynamic-quantization", "fp8"]
---

# 主流量化技术详解

本章将详细介绍 Intel Neural Compressor 支持的五种主流量化技术，包括每种技术的基本原理、适用场景、代码示例和关键注意事项。

## 1. Static Quantization（静态量化）

### 基本原理

静态量化（Post-Training Static Quantization, PTQ-S）是最常用的训练后量化方法之一。它的核心思想是：

- **权重**在转换阶段就确定量化参数（scale 和 zero_point）
- **激活值**的量化参数通过在校准数据集上运行前向传播来收集统计信息后确定
- 量化后的模型在推理时直接使用预计算的缩放因子，无需动态计算

静态量化将权重和激活值都量化为 INT8 精度（W8A8），因此能获得最大的推理性能提升和内存节省。

Neural Compressor 支持两种静态量化后端：
- **IPEX 后端**：使用 Intel Extension for PyTorch，针对 Intel CPU 进行了 JIT 编译优化
- **PT2E 后端**：使用 PyTorch 2 Export Quantization，通过 `torch.dynamo` 捕获 FX 图，再通过 `torch.compile` 进行算子融合

### 适用场景

- **计算机视觉模型**：CNN（ResNet、MobileNet 等）图像分类、目标检测模型
- **需要高推理性能**：对延迟和吞吐量要求高的生产环境部署
- **有代表性校准数据集**：能够提供与实际推理数据分布一致的校准数据
- **Intel CPU 部署**：配合 IPEX 可获得最佳 INT8 性能
- **Intel Gaudi HPU FP8 量化**：在 Gaudi 硬件上使用 FP8 静态量化

### 代码示例

#### IPEX 后端 INT8 静态量化

```python
import torch
import torchvision.models as models
import intel_extension_for_pytorch as ipex
from neural_compressor.torch.quantization import StaticQuantConfig, prepare, convert

model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.eval()

example_inputs = torch.randn(1, 3, 224, 224)
quant_config = StaticQuantConfig(act_sym=True, act_algo="minmax")

prepared_model = prepare(model, quant_config=quant_config, example_inputs=example_inputs)

def run_fn(model):
    for _ in range(10):
        model(torch.randn(1, 3, 224, 224))

run_fn(prepared_model)
q_model = convert(prepared_model)
```

#### PT2E 后端静态量化

```python
import torch
from neural_compressor.torch.export import export
from neural_compressor.torch.quantization import StaticQuantConfig, prepare, convert

model = YourFloatModel()
example_inputs = torch.randn(1, 3, 224, 224)

exported_model = export(model=model, example_inputs=example_inputs)
quant_config = StaticQuantConfig()
prepared_model = prepare(exported_model, quant_config=quant_config)

run_fn(prepared_model)
q_model = convert(prepared_model)

from torch._inductor import config
config.freezing = True
opt_model = torch.compile(q_model)
```

### 关键注意事项

> **IMPORTANT**
> - 使用 IPEX 后端时，必须在程序开头显式 `import intel_extension_for_pytorch as ipex`
> - IPEX 需要 `example_inputs` 参数用于 JIT 追踪计算图
> - 校准数据应具有代表性，建议使用 100-1000 个样本，覆盖实际推理数据分布
> - 模型必须设置为 `eval()` 模式，关闭 Dropout 和 BatchNorm 的训练行为
> - PT2E 后端的 `set_local` 算子级配置需要 PyTorch 2.4 及以上版本支持
> - 静态量化对激活值分布敏感，如果模型中存在离群点（outliers），精度可能下降明显，此时可考虑 SmoothQuant

---

## 2. Dynamic Quantization（动态量化）

### 基本原理

动态量化（Post-Training Dynamic Quantization, PTQ-D）与静态量化的主要区别在于激活值量化参数的计算时机：

- **权重**在转换阶段离线量化，与静态量化相同
- **激活值**的缩放因子在**推理时动态计算**，根据当前批次数据的数值范围实时确定
- 无需预先准备校准数据集，也不需要单独的校准步骤

动态量化同样支持 W8A8（权重和激活值均为 8-bit），但由于激活值量化在运行时进行，会带来一定的计算开销。

Neural Compressor 的动态量化基于 PyTorch 的 `X86InductorQuantizer` 实现，使用 PT2E 流程。

### 适用场景

- **NLP 模型**：RNN、LSTM、Transformer 等文本处理模型
- **快速原型验证**：没有校准数据集，想快速验证量化效果
- **激活值分布变化大**：不同输入的激活值范围差异较大，静态量化难以覆盖
- **TorchDynamo 后端**：目前动态量化仅支持 PT2E 后端

### 代码示例

```python
import torch
from neural_compressor.torch.export import export
from neural_compressor.torch.quantization import DynamicQuantConfig, prepare, convert

model = YourFloatModel()
example_inputs = torch.randn(1, 10)

exported_model = export(model=model, example_inputs=example_inputs)
quant_config = DynamicQuantConfig()
prepared_model = prepare(exported_model, quant_config=quant_config)
q_model = convert(prepared_model)

from torch._inductor import config
config.freezing = True
opt_model = torch.compile(q_model)

with torch.no_grad():
    output = opt_model(torch.randn(1, 10))
```

### 关键注意事项

> **NOTE**
> - 动态量化不需要校准步骤，`prepare` 后可直接调用 `convert`
> - 由于激活值量化在推理时进行，速度提升通常不如静态量化
> - 动态量化目前仅支持 PT2E（TorchDynamo）后端
> - `set_local` 算子级配置需要 PyTorch 2.4 及以上版本支持
> - 如果对性能要求极高且有校准数据，优先选择静态量化
> - 对于大语言模型（LLM），通常仅权重量化（Weight-Only）是更好的选择

---

## 3. Weight-Only Quantization（仅权重量化）

### 基本原理

仅权重量化（Weight-Only Quantization）只压缩模型的权重部分，激活值在推理时仍然保持高精度（FP16/BF16/FP32）。这是部署大语言模型（LLM）的首选量化方案。

**为什么仅权重量化适合 LLM？**

大模型文本生成是自回归（auto-regressive）过程，每次只生成一个 token，计算量约等于参数量，但现代硬件的计算能力（FLOPS）与内存带宽（Bandwidth）的比例可达 **100:1**，使得**内存带宽成为瓶颈**。仅权重量化可以显著减少权重读取的数据量，而激活量化是导致精度下降的主要原因，因此保持激活值高精度可以在大幅降低显存占用的同时保持较好精度。

Neural Compressor 支持六种仅权重量化算法：

| 算法 | 全称 | 核心特点 |
|------|------|----------|
| **RTN** | Round to Nearest | 最简单的舍入量化，无需额外数据，速度极快 |
| **GPTQ** | - | 基于二阶信息（Hessian 矩阵逆）的后训练量化，精度较高 |
| **AWQ** | Activation-aware Weight Quantization | 通过观察激活值分布保护显著权重通道 |
| **AutoRound** | - | Intel 提出的先进算法，通过签名梯度下降优化舍入方向，精度最佳 |
| **TEQ** | Trainable Equivalent Transformation | 可训练等价变换，在权重和激活之间搜索最优逐通道缩放因子 |
| **HQQ** | Half-Quadratic Quantization | 基于半二次优化，使用超拉普拉斯分布建模离群点误差 |

### 适用场景

- **大语言模型（LLM）部署**：LLaMA、Qwen、DeepSeek、Mistral 等
- **显存/内存受限场景**：4-bit/8-bit 量化可将 7B 模型从 14GB（FP16）压缩到 3.5GB（4-bit）
- **追求快速量化流程**：RTN 算法无需校准数据，秒级完成量化
- **消费级硬件运行大模型**：在普通 GPU 甚至 CPU 上运行大模型

### 公共参数说明

所有仅权重量化配置类共享以下参数：

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| `dtype` | 权重量化数据类型 | `'int'`, `'nf4'`, `'fp4'` | `'int'` |
| `bits` | 量化位宽 | 1~8 | 4 |
| `group_size` | 分组大小，`-1` 表示逐输出通道 | -1, 1~输入通道数 | -1 |
| `use_sym` | 是否使用对称量化 | `True`, `False` | `True` |
| `quant_lm_head` | 是否量化语言模型头层 | `True`, `False` | `False` |
| `use_double_quant` | 是否启用双量化（RTN/GPTQ 支持） | `True`, `False` | `False` |

> **说明**：
> - `group_size=-1` 表示逐输出通道量化，例如 Linear 层（输入通道 $C_{in}$，输出通道 $C_{out}$）会计算 $C_{out}$ 个量化参数
> - `group_size=gs` 表示沿输入通道每 `gs` 个元素共享一组量化参数，共 $C_{out} \times (C_{in}/gs)$ 个参数
> - NF4（NormalFloat 4-bit）是 QLoRA 论文提出的非均匀数据类型
> - 默认不量化 `lm_head`/`output_layer`/`embed_out` 等最后一层，以保证输出精度

### 代码示例

#### RTN（Round to Nearest）- 最快

```python
import torch
from neural_compressor.torch.quantization import RTNConfig, prepare, convert

quant_config = RTNConfig(bits=4, group_size=128)
model = prepare(model, quant_config)
model = convert(model)
```

#### GPTQ - 高精度

```python
import torch
from neural_compressor.torch.quantization import GPTQConfig, prepare, convert

quant_config = GPTQConfig(bits=4, group_size=128, act_order=True, percdamp=0.01)
model = prepare(model, quant_config)
run_fn(model)
model = convert(model)
```

#### AutoRound - Intel 推荐最佳精度

```python
import torch
from neural_compressor.torch.quantization import AutoRoundConfig, prepare, convert

quant_config = AutoRoundConfig(
    bits=4,
    group_size=128,
    iters=200,
    n_samples=512,
    seqlen=2048,
    low_gpu_mem_usage=True,
)
model = prepare(model, quant_config)
run_fn(model)
model = convert(model)
```

#### AWQ - 激活感知权重量化

```python
import torch
from neural_compressor.torch.quantization import AWQConfig, prepare, convert

quant_config = AWQConfig(bits=4, group_size=128, use_auto_scale=True, use_auto_clip=True)
model = prepare(model, quant_config, example_inputs=example_inputs)
run_fn(model)
model = convert(model)
```

#### 算子级配置（set_local）

```python
from neural_compressor.torch.quantization import RTNConfig

quant_config = RTNConfig(bits=4)
quant_config.set_local("lm_head", RTNConfig(dtype="fp32"))
quant_config.set_local(".*mlp.*", RTNConfig(bits=8))
```

#### 分层量化（Layer-wise Quantization）

对于超大模型无法一次性加载到内存的情况，可以使用分层量化逐层处理：

```python
from neural_compressor.torch.quantization import RTNConfig, convert, prepare
from neural_compressor.torch import load_empty_model

model_state_dict_path = "/path/to/model/state/dict"
float_model = load_empty_model(model_state_dict_path)
quant_config = RTNConfig(use_layer_wise=True)
prepared_model = prepare(float_model, quant_config)
quantized_model = convert(prepared_model)
```

### 关键注意事项

> **NOTE**
> - RTN 不需要校准数据，`prepare` 后直接 `convert`；GPTQ/AWQ/AutoRound/TEQ/HQQ 需要校准步骤（调用 `run_fn`）
> - GPTQ 的 `act_order=True`（按 Hessian 对角线重排通道）可提升精度但会增加计算量
> - AutoRound 的量化速度较慢（默认 200 次迭代），但通常能获得最佳精度
> - 双量化（Double Quant）对缩放因子本身进行二次量化，可进一步减少内存占用，目前仅 RTN 和 GPTQ 支持
> - 量化后模型使用 `WeightOnlyLinear` 模块存储，将低比特数据打包到 int8/int32 中节省内存，推理时反量化为 FP32 计算
> - 加载仅权重量化模型时，如果使用了 `use_layer_wise=True`，需要传入原始模型（`original_model` 参数）
> - 算法选择建议：快速测试用 RTN，追求精度用 AutoRound 或 GPTQ

---

## 4. FP8 Quantization（FP8 量化）

### 基本原理

FP8（Float Point 8）是一种 8 位浮点数据格式，与 INT8 整数格式相比，FP8 能更好地表示深度学习中常见的长尾分布（离群点），特别适合 Transformer 和大语言模型。

FP8 有两种标准格式：
- **E4M3**：4 位指数 + 3 位尾数，动态范围较小但精度较高，适合权重和激活值
- **E5M2**：5 位指数 + 2 位尾数，动态范围较大但精度较低，适合梯度等需要更大范围的场景

Neural Compressor 支持两种 FP8 运行模式：
- **FP8 模式**：张量直接以 FP8 格式表示，算子替换为原生 FP8 版本（需要硬件支持）
- **FP8 QDQ 模式**：插入量化/反量化（Quantize/Dequantize）算子对，激活值仍以高精度计算，框架可根据能力自动融合算子（支持 CPU 模拟）

运行时自动检测硬件，优先级：HPU > CPU。

### 适用场景

- **Intel Gaudi AI 加速器（HPU）**：Gaudi2/Gaudi3 原生支持 FP8 硬件加速
- **大语言模型推理**：Llama、Mistral、Mixtral、Qwen、Phi 等
- **FP8 KV Cache 量化**：减少 KV Cache 显存占用，支持更长上下文
- **需要比 INT8 更高精度的 8-bit 量化**：FP8 的浮点特性对离群点更鲁棒
- **VLLM/Optimum-Habana 推理服务**：与 vLLM、Optimum 集成部署

### 代码示例

#### 基础 FP8 量化（HPU）

```python
import torch
from neural_compressor.torch.quantization import FP8Config, prepare, convert

model = YourModel()
model.eval()

qconfig = FP8Config(fp8_config="E4M3")
model = prepare(model, qconfig)

with torch.no_grad():
    for batch in calibration_dataloader:
        model(batch)

model = convert(model)

with torch.no_grad():
    output = model(test_input.to("hpu"))
```

#### FP8 配置参数说明

```python
from neural_compressor.torch.quantization import FP8Config

qconfig = FP8Config(
    fp8_config="E4M3",
    hp_dtype="bf16",
    observer="maxabs",
    scale_method="maxabs_hw",
    mode="AUTO",
    dump_stats_path="./hqt_output/measure",
    measure_exclude="OUTPUT",
)
```

关键参数说明：

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `fp8_config` | FP8 数据格式 | `E4M3`（默认）, `E5M2` |
| `hp_dtype` | 非 FP8 算子的高精度类型 | `bf16`（默认）, `fp16`, `fp32` |
| `observer` | 统计信息观测器 | `maxabs`（默认） |
| `scale_method` | 缩放因子计算方法 | `maxabs_hw`（默认）, `unit_scale`, `maxabs_pow2` 等 |
| `mode` | 运行模式 | `AUTO`（默认）, `MEASURE`, `QUANTIZE` |

### 关键注意事项

> **NOTE**
> - FP8 原生模式仅在 Intel Gaudi HPU 上支持，CPU 仅支持 FP8 QDQ 模拟模式
> - E4M3 是权重和激活值量化的默认推荐格式，动态范围和精度平衡较好
> - FP8 量化支持白名单（`allowlist`）和黑名单（`blocklist`）控制哪些层量化
> - 默认不量化输出层（`measure_exclude="OUTPUT"`）以加快测量速度
> - 在 Gaudi 上使用时，注意 Neural Compressor 与 Habana 软件栈的版本映射关系
> - FP8 KV Cache 是实验性功能，通过 AutoRound 支持，可显著减少长文本生成的显存占用
> - Optimum-Habana 和 vLLM-HPU 已集成 Neural Compressor 的 FP8 量化能力

---

## 5. SmoothQuant（平滑量化）

### 基本原理

SmoothQuant 是专门针对大语言模型设计的量化技术，解决 LLM 激活值中存在大量离群点导致直接 INT8 量化精度严重下降的问题。

**核心思想**：通过数学上的等价变换，将量化难度从激活值转移到权重上。

- 大模型的激活值分布通常具有**显著的离群点**（某些通道的值远大于其他通道），直接量化会导致大的误差
- 权重的分布通常更加平滑，更容易量化
- SmoothQuant 引入逐通道缩放因子 $s$，在数学上等价地变换：$Y = (X \cdot \text{diag}(s)^{-1}) \cdot (\text{diag}(s) \cdot W)$
- 变换后，激活值的离群点被平滑，权重虽然变得不太平滑但仍然在可量化范围内
- 经过平滑处理后，可以直接应用标准的 W8A8 INT8 量化而不显著损失精度

SmoothQuant 目前基于 IPEX 后端实现。

### 适用场景

- **大语言模型 INT8 量化**：Llama、OPT、BLOOM 等 Transformer 架构 LLM
- **激活值存在明显离群点**：直接静态量化精度下降严重的模型
- **Intel CPU 部署**：需要在 CPU 上使用 INT8 加速 LLM 推理
- **希望获得比仅权重量化更好的计算性能**：W8A8 比 W4A16 的计算强度更高

### 代码示例

```python
import torch
from neural_compressor.torch.quantization import SmoothQuantConfig, prepare, convert
import intel_extension_for_pytorch as ipex

model = YourLLMModel()
model.eval()

example_inputs = tokenizer("Hello, world!", return_tensors="pt")
quant_config = SmoothQuantConfig(alpha=0.5)

prepared_model = prepare(
    model,
    quant_config=quant_config,
    example_inputs=example_inputs,
)

def run_fn(model):
    for batch in calibration_dataloader:
        with torch.no_grad():
            model(**batch)

run_fn(prepared_model)
q_model = convert(prepared_model)
```

### 关键注意事项

> **NOTE**
> - SmoothQuant 需要 IPEX 后端支持，程序开头必须导入 `intel_extension_for_pytorch`
> - `alpha` 参数控制平滑强度：`alpha=0` 表示不平滑（等价于普通静态量化），`alpha=1` 表示将难度完全转移到权重，默认 `0.5` 是一个较好的平衡点
> - 需要提供 `example_inputs` 用于 JIT 追踪
> - 校准数据的质量和数量对 SmoothQuant 效果有重要影响
> - 如果 SmoothQuant 后精度仍不理想，可以考虑仅权重量化（Weight-Only）或 FP8 量化
> - 与 `set_local` 配合使用，可以为某些对量化敏感的层（如输出层）设置回退到 FP32

---

## 技术选择指南

面对多种量化技术，如何选择最适合的方案？

| 场景 | 推荐技术 | 精度 | 速度 | 模型大小 |
|------|---------|------|------|---------|
| CNN 视觉模型，Intel CPU，追求极致性能 | 静态量化（INT8） | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | 1/4 |
| LLM，显存受限，快速部署 | RTN 4-bit 仅权重 | ⭐⭐⭐ | ⚡⚡⚡ | 1/4（权重） |
| LLM，追求高精度低比特 | AutoRound/GPTQ 4-bit | ⭐⭐⭐⭐⭐ | ⚡⚡ | 1/4（权重） |
| LLM，Intel Gaudi HPU | FP8 E4M3 | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | 1/2 |
| LLM，Intel CPU，INT8 加速 | SmoothQuant + INT8 | ⭐⭐⭐⭐ | ⚡⚡⚡ | 1/4 |
| 快速验证，无校准数据 | 动态量化 / RTN | ⭐⭐⭐ | ⚡⚡ | 1/4 |

---

[← 上一章：快速开始](03-quickstart.md) | [下一章：API 概览 →](05-api-overview.md)
