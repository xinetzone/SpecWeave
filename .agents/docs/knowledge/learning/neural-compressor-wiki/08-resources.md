---
id: "neural-compressor-wiki-resources"
title: "术语表与资源"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html"
summary: "Intel Neural Compressor 相关术语表、官方文档链接、参考论文与学习资源。"
tags: ["neural-compressor", "glossary", "resources", "references"]
---

# 术语表与资源

本章汇总了使用 Intel Neural Compressor 和模型量化领域的核心术语，以及官方文档、相关项目、论文和博客等学习资源，方便读者查阅和深入学习。

---

## 一、术语表（Glossary）

### Quantization（量化）
将浮点精度（FP32/FP16/BF16）的模型权重和/或激活值映射到低比特整数（如 INT8/INT4）的过程。量化可以显著减小模型大小、降低内存带宽占用、利用硬件低精度计算指令加速推理，但会引入一定精度损失。核心公式：`q = round(x / scale) + zero_point`。

### PTQ（Post-Training Quantization，训练后量化）
在模型训练完成后进行的量化，不需要重新训练模型。包括静态量化、动态量化和仅权重量化等子类别。PTQ 的优点是流程简单、成本低，几分钟到几小时即可完成；缺点是精度可能不如 QAT。Neural Compressor 的主要功能即为 PTQ。

### QAT（Quantization-Aware Training，量化感知训练）
在训练（或微调）过程中模拟量化噪声，让模型适应低精度表示的量化方法。QAT 在训练前向传播中插入伪量化算子（fake quantize），使模型参数学习到量化误差的鲁棒性。QAT 精度通常优于 PTQ，但需要完整的训练流程和数据集，成本更高。

### Calibration（校准）
静态量化和部分仅权重量化算法中，使用一小部分代表性数据在准备好的模型上运行前向传播，收集各层激活值统计信息（min/max、直方图等）以计算最优量化参数（scale 和 zero_point）的过程。校准数据的质量直接决定量化模型精度，必须使用真实分布数据。

### Observer（观察者/观测器）
插入在模型各层之间，用于收集张量统计信息的模块。在 `prepare()` 阶段被插入模型，校准期间记录激活值的数值分布特征，`convert()` 时根据这些统计信息计算量化参数。常见算法包括 `minmax`（记录最大最小值）、`kl`（KL 散度最小化）、`percentile`（百分位数截断）等。

### Scale（缩放因子）
量化公式中的关键参数，将浮点数范围线性映射到整数范围的比例系数。例如 FP32 范围 `[α, β]` 映射到 INT8 范围 `[-128, 127]`，scale 计算公式为 `scale = (β - α) / 255`（非对称）或 `scale = max(|α|, |β|) / 127`（对称）。scale 的精度直接影响量化误差。

### Zero-point（零点）
非对称量化中的偏移参数，使量化后的整数零点对应浮点空间中的真实零点。公式为 `zero_point = round(-α / scale) - 128`（INT8）。对称量化的 zero_point 固定为 0，因此不需要额外存储，但对于分布不含 0 的张量（如 ReLU 输出），非对称量化精度更高。

### INT8（8-bit Integer，8 位整数）
最常用的量化数据类型，使用 8 个比特表示整数，范围 `-128~127`（有符号）或 `0~255`（无符号）。INT8 可将模型大小压缩至 FP32 的 25%，配合支持 VNNI/DP4A 等指令集的硬件可实现 2~4 倍推理加速，是生产部署的主流精度选择。

### FP8（8-bit Floating Point，8 位浮点数）
IEEE 最新标准化的低精度浮点格式，有两种变体：**E4M3**（4 位指数 + 3 位尾数，精度高但范围小，适合前向激活值）和 **E5M2**（5 位指数 + 2 位尾数，范围大但精度低，适合梯度和权重）。FP8 在保留浮点格式优势的同时实现接近 INT8 的加速比，主要用于训练和 Gaudi/H100 等新硬件。

### Weight-only Quantization（仅权重量化）
只将模型权重量化为低比特（如 INT4/INT8），激活值在推理时仍保持浮点精度（FP16/BF16）的量化方式。由于只压缩权重，仅权重量化对精度的影响远小于全量化（权重+激活），特别适合大语言模型——大模型的主要内存瓶颈是权重加载而非计算。代表算法包括 RTN、GPTQ、AWQ、AutoRound、HQQ 等。

### SmoothQuant
一种专为 Transformer 模型设计的量化技术，核心思想是通过数学等价变换将激活值中的异常点（outlier）难度"转移"到权重上，使得原本难以量化的 Transformer 模型可以使用 INT8 静态量化而不崩溃。变换公式：`Y = (X diag(s)^{-1}) · (diag(s) W)`，通过选择合适的平滑因子 s 平衡激活值和权重的量化难度。

### RTN（Round-To-Nearest，最近邻舍入）
最简单的仅权重量化算法，将权重值直接四舍五入到最近的量化网格点。RTN 不需要校准数据，速度极快，但精度一般，适合作为量化基线或对精度要求不高的场景。Neural Compressor 的 `RTNConfig` 支持分组量化和双量化。

### GPTQ（GPT Quantization）
基于二阶 Hessian 信息的仅权重量化算法，通过逐层补偿量化误差来最小化输出扰动。GPTQ 需要校准数据来估计 Hessian 矩阵，精度显著优于 RTN，是当前最流行的 INT4 量化算法之一。`act_order=True`（按激活幅度重新排列通道）可进一步提升精度但降低推理速度。

### AutoRound
Intel 开发的先进权重量化算法，采用符号梯度下降优化量化值（而非固定使用最近邻舍入），在多种 LLM 和 VLM 上取得了业界领先的量化精度。AutoRound 同样需要少量校准数据，是 Neural Compressor 推荐的高质量量化方案。

### QDQ（Quantize-Dequantize，量化-反量化）
一种量化模型表示模式，在计算图中插入显式的 Quantize 和 Dequantize 算子。QDQ 模式保留了详细的量化信息，便于调试和跨框架部署，是 ONNX 和 PyTorch 2.0 导出推荐的量化格式。与之对应的是算子融合模式，将 QDQ 算子融合进计算算子内部以获得更好性能。

### Static Quantization（静态量化）
PTQ 的一种，在推理前（校准阶段）就确定所有张量的 scale 和 zero_point，推理时无需额外计算。静态量化性能最好，但需要校准数据集，且对激活值分布敏感。适合 CNN 等激活值分布稳定的模型。

### Dynamic Quantization（动态量化）
PTQ 的一种，权重离线量化，激活值在推理时根据实时数据范围动态计算 scale。动态量化无需校准数据，对激活值 outlier 更鲁棒，但推理时需额外计算 scale，延迟略高于静态量化。适合 Transformer、MLP 等 Linear 层密集的模型。

### Mixed Precision（混合精度）
在同一模型中为不同层/算子使用不同量化精度的策略。例如，对量化敏感的层保持 FP16/FP32，不敏感的层使用 INT8；或权重使用 INT4，激活值使用 BF16。Neural Compressor 通过 `set_local()` 和 `autotune()` 支持混合精度配置。

### VNNI（Vector Neural Network Instructions）
Intel AVX-512 指令集中的向量神经网络扩展，专门为低精度深度学习推理设计，支持 INT8/UINT8 乘加运算的硬件加速。支持 VNNI 的 CPU（如 Intel Xeon Cascade Lake 及以后）可在 INT8 推理时获得显著性能提升。

### AMX（Advanced Matrix Extensions）
Intel 最新的矩阵运算扩展指令集，首次出现在 Sapphire Rapids 至强处理器中，支持 BF16/INT8/FP16 的矩阵乘法硬件加速（TMUL 单元），可提供比 VNNI 高数倍的深度学习推理和训练吞吐量。

---

## 二、官方文档链接

| 文档 | 链接 | 说明 |
|------|------|------|
| **官方欢迎页** | [Welcome Page](https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html) | 项目介绍、特性、安装入口 |
| **安装指南** | [Installation Guide](https://intel.github.io/neural-compressor/latest/docs/source/installation_guide.html) | 各平台详细安装说明 |
| **PyTorch API 概览** | [PyTorch Overview](https://intel.github.io/neural-compressor/latest/docs/source/PyTorch.html) | PyTorch 扩展 API 文档入口 |
| **静态量化** | [Static Quantization](https://intel.github.io/neural-compressor/latest/docs/source/PT_StaticQuant.html) | INT8 静态量化使用指南 |
| **动态量化** | [Dynamic Quantization](https://intel.github.io/neural-compressor/latest/docs/source/PT_DynamicQuant.html) | INT8 动态量化使用指南 |
| **SmoothQuant** | [SmoothQuant](https://intel.github.io/neural-compressor/latest/docs/source/PT_SmoothQuant.html) | Transformer 平滑量化 |
| **仅权重量化** | [Weight-Only Quantization](https://intel.github.io/neural-compressor/latest/docs/source/PT_WeightOnlyQuant.html) | RTN/GPTQ/AWQ/AutoRound |
| **AutoRound** | [AutoRound Guide](https://intel.github.io/neural-compressor/latest/docs/source/PT_AutoRound.html) | 先进权重量化算法 |
| **FP8 量化** | [FP8 Quantization](https://intel.github.io/neural-compressor/latest/docs/source/PT_FP8Quant.html) | FP8 E4M3/E5M2 量化 |
| **MX 量化** | [MX Quantization](https://intel.github.io/neural-compressor/latest/docs/source/PT_MXQuant.html) | 微缩放格式（实验性） |
| **NVFP4 量化** | [NVFP4 Quantization](https://intel.github.io/neural-compressor/latest/docs/source/PT_NVFP4Quant.html) | NVIDIA 4-bit 浮点（实验性） |
| **混合精度** | [Mixed Precision](https://intel.github.io/neural-compressor/latest/docs/source/PT_MixedPrecision.html) | 自动混合精度 |
| **Auto Tune** | [Auto Tune](https://intel.github.io/neural-compressor/latest/docs/source/autotune.html) | 自动调优功能 |
| **Transformers-like API** | [Transformers-like API](https://intel.github.io/neural-compressor/latest/docs/source/transformers_like_api.html) | VLM 模型易用 API |
| **TensorFlow API** | [TensorFlow Overview](https://intel.github.io/neural-compressor/latest/docs/source/TensorFlow.html) | TensorFlow 扩展 |
| **JAX API** | [JAX Overview](https://intel.github.io/neural-compressor/latest/docs/source/JAX.html) | JAX/Keras 扩展（实验性） |
| **架构设计** | [Architecture](https://intel.github.io/neural-compressor/latest/docs/source/design.html#architecture) | 系统架构与工作流 |
| **API 参考** | [API Reference](https://intel.github.io/neural-compressor/latest/docs/source/api-doc/apis.html) | 完整 API 文档 |
| **示例代码** | [Examples](https://github.com/intel/neural-compressor/blob/main/examples/README.md) | GitHub 示例仓库 |
| **官方 FAQ** | [FAQ](https://intel.github.io/neural-compressor/latest/docs/source/faq.html) | 官方常见问题列表 |
| **Gaudi 版本映射** | [Gaudi Version Map](https://intel.github.io/neural-compressor/latest/docs/source/gaudi_version_map.html) | Neural Compressor 与 Gaudi 软件栈版本对应表 |

---

## 三、相关项目

### Intel 生态项目

| 项目 | 链接 | 说明 |
|------|------|------|
| **AutoRound** | [github.com/intel/auto-round](https://github.com/intel/auto-round) | Intel 先进的低比特权重量化算法，基于符号梯度优化，Neural Compressor 已深度集成 |
| **Intel Extension for PyTorch (IPEX)** | [github.com/intel/intel-extension-for-pytorch](https://github.com/intel/intel-extension-for-pytorch) | Intel 官方 PyTorch 扩展，提供 CPU/GPU 算子优化和量化后端，是 Neural Compressor CPU 推理的推荐后端 |
| **Intel Extension for Transformers** | [github.com/intel/intel-extension-for-transformers](https://github.com/intel/intel-extension-for-transformers) | Transformer 模型工具包，包含量化、压缩、蒸馏等功能，构建在 Neural Compressor 之上 |
| **OpenVINO** | [github.com/openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | Intel 推理部署框架，支持 NNCF（Neural Network Compression Framework）量化 |

### 第三方量化项目

| 项目 | 链接 | 说明 |
|------|------|------|
| **GPTQ-for-LLaMa** | [github.com/qwopqwop200/GPTQ-for-LLaMa](https://github.com/qwopqwop200/GPTQ-for-LLaMa) | GPTQ 算法的最早开源实现 |
| **AutoGPTQ** | [github.com/AutoGPTQ/AutoGPTQ](https://github.com/AutoGPTQ/AutoGPTQ) | 易用的 GPTQ 实现，Neural Compressor 兼容其格式 |
| **AWQ** | [github.com/mit-han-lab/llm-awq](https://github.com/mit-han-lab/llm-awq) | Activation-aware Weight Quantization，基于激活感知的权重量化 |
| **bitsandbytes** | [github.com/bitsandbytes-foundation/bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes) | 轻量级 8-bit/4-bit 量化库，广泛用于 HuggingFace Transformers |
| **llama.cpp** | [github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) | LLaMA 模型的 C/C++ 推理实现，支持多种量化格式（GGUF） |

---

## 四、学习资源

### 经典论文

| 论文 | 年份 | 链接 | 核心贡献 |
|------|------|------|---------|
| **Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference** | 2017 | [arXiv:1712.05877](https://arxiv.org/abs/1712.05877) | Google 提出的 INT8 量化推理框架，现代量化技术的奠基之作 |
| **Quantizing deep convolutional networks for efficient inference: A whitepaper** | 2018 | [arXiv:1806.08342](https://arxiv.org/abs/1806.08342) | NVIDIA 量化白皮书，系统介绍对称/非对称量化、校准方法 |
| **Dynamic Quantization for Efficient Inference of Neural Networks** | 2019 | - | 动态量化技术基础（PyTorch 动态量化设计参考） |
| **SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models** | 2022 | [arXiv:2211.10438](https://arxiv.org/abs/2211.10438) | MIT/Intel 等提出，解决 LLM 激活 outlier 导致量化精度崩溃的问题 |
| **GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers** | 2022 | [arXiv:2210.17323](https://arxiv.org/abs/2210.17323) | 基于二阶信息的 LLM INT4 量化算法 |
| **AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration** | 2023 | [arXiv:2306.00978](https://arxiv.org/abs/2306.00978) | 通过保护显著权重通道提升 INT4 量化精度 |
| **AutoRound: Recovering LLM Quantization through Advanced Rounding** | 2024 | [arXiv:2309.05516](https://arxiv.org/abs/2309.05516) | Intel 提出的基于优化的权重量化方法，显著提升低比特精度 |
| **FP8 Formats for Deep Learning** | 2022 | [arXiv:2209.05433](https://arxiv.org/abs/2209.05433) | NVIDIA/ARM/Intel 联合提出 FP8 数据格式标准 |
| **LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale** | 2022 | [arXiv:2208.07339](https://arxiv.org/abs/2208.07339) | 混合精度分解方法，通过 outlier 分离实现 LLM INT8 推理 |
| **Faster Inference of LLMs using FP8 on the Intel Gaudi** | 2025 | [arXiv:2503.09975](https://arxiv.org/abs/2503.09975) | Intel Gaudi FP8 LLM 推理实践 |

### 推荐博客

| 博客 | 链接 | 说明 |
|------|------|------|
| **[Intel Gaudi] #4. FP8 Quantization** | [blog.squeezebits.com](https://blog.squeezebits.com/intel-gaudi-4-fp8-quantization--40269) | SqueezeBits 博客，系统介绍 Gaudi 上 FP8 量化实践 |
| **PyTorch Quantization Documentation** | [pytorch.org/docs/stable/quantization.html](https://pytorch.org/docs/stable/quantization.html) | PyTorch 官方面向开发者的量化文档 |
| **TensorFlow Model Optimization** | [tensorflow.org/model_optimization](https://www.tensorflow.org/model_optimization) | TensorFlow 量化与模型优化指南 |
| **ONNX Runtime Quantization** | [onnxruntime.ai/docs/performance/model-optimizations/quantization.html](https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html) | ONNX Runtime 量化文档 |

### 社区与沟通

| 渠道 | 链接 | 用途 |
|------|------|------|
| **GitHub Issues** | [github.com/intel/neural-compressor/issues](https://github.com/intel/neural-compressor/issues) | Bug 报告、功能请求、提问 |
| **邮件联系** | [inc.maintainers@intel.com](mailto:inc.maintainers@intel.com) | 研究合作、学术交流 |
| **PyTorch Landscape** | [landscape.pytorch.org](https://landscape.pytorch.org/) | PyTorch 生态项目索引 |

---

## 五、本教程章节索引

| 章节 | 文件 | 内容 |
|------|------|------|
| 00 | [00-overview.md](00-overview.md) | 教程总览：库介绍、特性、章节导航 |
| 01 | [01-core-concepts.md](01-core-concepts.md) | 核心概念与架构：量化基础、工作流 |
| 02 | [02-installation.md](02-installation.md) | 安装指南：各环境安装方法 |
| 03 | [03-quickstart.md](03-quickstart.md) | 快速开始：第一个量化程序 |
| 04 | [04-quantization-techniques.md](04-quantization-techniques.md) | 量化技术详解：各算法原理与适用场景 |
| 05 | [05-api-overview.md](05-api-overview.md) | API 概览：核心函数与配置类说明 |
| 06 | [06-best-practices.md](06-best-practices.md) | 最佳实践：校准、策略选择、调优、避坑 |
| 07 | [07-faq.md](07-faq.md) | 常见问题：20 个高频问题与解决方案 |
| 08 | 本章 | 术语表与资源：术语定义、文档、论文、项目 |

---

[← 上一章：常见问题](07-faq.md) | [🏠 返回教程首页](00-overview.md)
