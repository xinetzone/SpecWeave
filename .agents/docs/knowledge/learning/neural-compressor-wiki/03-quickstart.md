---
id: "neural-compressor-wiki-quickstart"
title: "快速开始"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html"
summary: "Intel Neural Compressor 快速上手指南，包含完整的 PyTorch CPU 模型量化示例代码与详细注释。"
tags: ["neural-compressor", "quickstart", "code-example", "pytorch"]
---

# 快速开始

本章将通过两个完整的可运行示例，帮助您快速上手 Intel® Neural Compressor。第一个示例是在 **CPU（中央处理器）** 上运行的视觉模型量化，无需特殊硬件；第二个示例演示如何加载仅权重（Weight-Only）量化的大语言模型。

## 示例 1：PyTorch CPU 模型量化（ResNet18 静态量化）

本示例将展示如何使用 Neural Compressor 对 **ResNet18（残差网络 18 层）** 图像分类模型进行 **INT8 静态量化（Static Quantization）**，整个流程可在普通 CPU 上完成。

### 完整代码

```python
import torch
import torchvision.models as models
from neural_compressor.torch.quantization import (
    StaticQuantConfig,
    prepare,
    convert,
)

def main():
    # -------------------------------------------------------------------------
    # 步骤 1：加载预训练模型
    # -------------------------------------------------------------------------
    # 从 torchvision 加载预训练的 ResNet18 模型
    # 模型默认在 FP32（32位浮点数）精度下
    print("正在加载 ResNet18 模型...")
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.eval()  # 设置为评估模式，这对量化很重要
    
    # -------------------------------------------------------------------------
    # 步骤 2：配置量化参数
    # -------------------------------------------------------------------------
    # StaticQuantConfig：静态量化配置
    # - dtype: 指定量化后的数据类型，"int8" 表示使用 8位整数
    # - 量化后端会根据硬件自动选择：
    #   - Intel CPU: 使用 intel-extension-for-pytorch (IPEX) 后端（如果已安装）
    #   - 其他 CPU: 使用 TorchDynamo 后端
    print("配置量化参数...")
    quant_config = StaticQuantConfig(dtype="int8")
    
    # -------------------------------------------------------------------------
    # 步骤 3：准备模型（Prepare）
    # -------------------------------------------------------------------------
    # prepare 函数会在模型中插入观察者（Observer）模块
    # 观察者用于在校准过程中监控张量的数值范围（最小值/最大值）
    # 这些统计信息将用于计算量化缩放因子（scale）和零点（zero_point）
    print("准备模型（插入观察者）...")
    prepared_model = prepare(model, quant_config)
    
    # -------------------------------------------------------------------------
    # 步骤 4：校准（Calibration）
    # -------------------------------------------------------------------------
    # 静态量化需要校准步骤：在代表性数据上运行前向传播
    # 观察者会收集激活值的分布统计信息
    # 注意：校准数据应与实际推理数据分布相似
    # 这里使用随机数据作为演示，实际应用中请使用真实验证数据集的子集
    print("运行校准...")
    calibration_data = torch.randn(10, 3, 224, 224)  # 10 张 224x224 的 RGB 图像
    with torch.no_grad():  # 禁用梯度计算，节省内存和计算
        for i in range(10):
            input_tensor = calibration_data[i:i+1]  # 单张图像
            prepared_model(input_tensor)
            if (i + 1) % 5 == 0:
                print(f"  已完成 {i+1}/10 校准批次")
    
    # -------------------------------------------------------------------------
    # 步骤 5：转换模型（Convert）
    # -------------------------------------------------------------------------
    # convert 函数会：
    # 1. 根据收集到的统计信息计算量化参数
    # 2. 将观察者替换为实际的量化（Quantize）和反量化（Dequantize）算子
    # 3. 输出最终的 INT8 量化模型
    print("转换为量化模型...")
    quantized_model = convert(prepared_model)
    
    # -------------------------------------------------------------------------
    # 步骤 6：验证量化模型
    # -------------------------------------------------------------------------
    # 使用量化模型进行推理测试
    print("测试量化模型推理...")
    test_input = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        output = quantized_model(test_input)
    
    # 输出结果信息
    print(f"\n量化成功！")
    print(f"输出张量形状: {output.shape}")  # 应为 torch.Size([1, 1000]) - ImageNet 1000类
    print(f"输出数据类型: {output.dtype}")
    
    # -------------------------------------------------------------------------
    # 步骤 7（可选）：保存和加载量化模型
    # -------------------------------------------------------------------------
    # 保存量化模型到磁盘
    output_dir = "./quantized_resnet18"
    print(f"\n保存量化模型到: {output_dir}")
    quantized_model.save(output_dir)
    
    # 加载已保存的量化模型
    print("加载已保存的量化模型...")
    from neural_compressor.torch.quantization import load
    loaded_model = load(output_dir)
    
    # 验证加载的模型可以正常推理
    with torch.no_grad():
        loaded_output = loaded_model(test_input)
    print(f"加载的模型推理成功！输出差异: {torch.max(torch.abs(output - loaded_output)):.6f}")
    
    return quantized_model

if __name__ == "__main__":
    main()
```

### 代码逐段解析

让我们详细解释每个关键步骤的作用：

#### 1. 模型与配置

| 组件 | 说明 |
|------|------|
| `model.eval()` | 将模型设置为评估模式。量化过程中必须关闭 Dropout 和 BatchNorm 的训练行为，否则会影响量化精度 |
| `StaticQuantConfig(dtype="int8")` | 静态量化配置，指定使用 INT8 精度。Neural Compressor 会自动检测可用后端 |
| `prepare(model, quant_config)` | 模型准备阶段：在网络的适当位置插入 Observer，用于监控张量数值范围 |

#### 2. 校准阶段

校准是静态量化的关键步骤：

- **为什么需要校准**：INT8 量化需要知道每个激活张量的数值范围，才能确定合适的缩放因子将 FP32 映射到 INT8
- **校准数据要求**：应使用约 100-1000 个样本，覆盖实际推理场景的数据分布
- **批次大小**：可以使用单张图像或小批次，Observer 会自动统计所有批次的全局范围

> **提示**：在实际项目中，建议使用验证集的一个子集作为校准数据，而不是随机噪声。随机噪声数据可能无法代表真实数据分布，导致量化精度下降。

#### 3. 转换阶段

`convert` 函数完成从准备模型到量化模型的转换：

1. 读取每个 Observer 收集的统计信息（min/max 或直方图）
2. 计算每个张量的 scale 和 zero_point
3. 替换 Observer 为 Quantize/Dequantize 算子
4. 对权重进行离线量化（权重在转换时就确定了量化参数）

#### 4. 模型保存与加载

量化后的模型支持两种序列化方式：

- `model.save(output_dir)`：保存为 Neural Compressor 格式目录
- 也可以使用 `torch.save()` 保存为 state_dict，但推荐使用 Neural Compressor 的 save 方法以保证完整的元数据保存

---

## 示例 2：仅权重（Weight-Only）量化大语言模型加载

**Weight-Only Quantization（仅权重量化）** 是部署大语言模型（LLM）最常用的技术：只将模型权重量化为低精度（如 4-bit/8-bit），而激活值在推理时仍保持 FP16/BF16 精度。这种方法可以大幅减少显存占用，同时保持较好的模型精度。

Neural Compressor 提供了便捷的 `load` 函数，可以直接加载 HuggingFace Hub 上预量化的模型。

### 完整代码

```python
import torch
from neural_compressor.torch.quantization import load

def load_llm_example():
    # -------------------------------------------------------------------------
    # 模型名称：使用 HuggingFace Hub 上的 GPTQ 量化模型
    # -------------------------------------------------------------------------
    # TheBloke/Llama-2-7B-GPTQ 是 Llama-2-7B 模型的 GPTQ 4-bit 量化版本
    # 注意：运行此示例需要：
    # 1. 网络连接访问 HuggingFace Hub
    # 2. 约 4-5GB 磁盘空间用于缓存模型
    # 3. 足够的 RAM/显存（CPU 加载需要约 8GB+ 内存）
    model_name = "TheBloke/Llama-2-7B-GPTQ"
    
    print(f"正在加载模型: {model_name}")
    print("=" * 60)
    print("注意：首次加载会进行格式转换，可能需要较长时间（5-30分钟）")
    print("转换后的模型将缓存到本地，后续加载会快很多")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # 使用 load 函数加载量化模型
    # -------------------------------------------------------------------------
    # 参数说明：
    # - model_name_or_path: HuggingFace 模型名称或本地路径
    # - format: 模型格式，"huggingface" 表示从 HuggingFace Hub 加载
    # - device: 目标设备
    #   - "cpu": 加载到 CPU（支持 weight-only 推理）
    #   - "cuda": 加载到 NVIDIA GPU（需要 CUDA 环境）
    #   - "hpu": 加载到 Intel Gaudi 加速器
    # - torch_dtype: 激活值计算精度
    #   - torch.float32: FP32 精度，兼容性最好
    #   - torch.bfloat16: BF16 精度（推荐在支持的 CPU/GPU 上使用）
    #   - torch.float16: FP16 精度
    model = load(
        model_name_or_path=model_name,
        format="huggingface",
        device="cpu",  # 使用 CPU，无需特殊硬件
        torch_dtype=torch.bfloat16,
    )
    
    print("模型加载完成！")
    
    # -------------------------------------------------------------------------
    # 验证模型
    # -------------------------------------------------------------------------
    # 简单的文本生成测试
    from transformers import AutoTokenizer
    
    print("\n加载分词器...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # 准备输入
    prompt = "Hello, I am a language model and"
    inputs = tokenizer(prompt, return_tensors="pt")
    
    print(f"输入提示: {prompt}")
    print("正在生成文本...")
    
    # 推理
    model.eval()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            top_p=0.9,
        )
    
    # 解码输出
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\n生成结果: {generated_text}")
    
    return model

if __name__ == "__main__":
    load_llm_example()
```

### 关键说明

#### 首次加载速度问题

首次加载 HuggingFace 格式的预量化模型（如 GPTQ、AWQ 等）时，Neural Compressor 会自动执行以下操作：

1. 从 HuggingFace Hub 下载原始模型文件
2. 将模型格式从第三方格式（auto-gptq/autoawq）转换为 Neural Compressor 优化的后端格式
3. 保存转换后的模型文件（`hpu_model.safetensors` 或对应后端格式）到本地缓存目录
4. 加载转换后的模型

这个转换过程是一次性的，可能需要 5-30 分钟（取决于模型大小和硬件性能）。**后续加载将直接使用缓存文件，速度会快很多。**

> **缓存位置**：转换后的模型通常缓存在 HuggingFace 的缓存目录（默认 `~/.cache/huggingface/hub/`）下模型仓库的子目录中。

#### Weight-Only 量化算法选择

如果需要自己对 LLM 进行仅权重量化，可以使用 Neural Compressor 提供的多种算法：

```python
from neural_compressor.torch.quantization import (
    RTNConfig,      # Round to Nearest - 最简单，速度最快
    GPTQConfig,     # GPTQ - 精度较高
    AWQConfig,      # AWQ - 激活感知权重量化
    AutoRoundConfig # AutoRound - Intel 提出的先进算法，精度最好
)

# 示例：使用 4-bit RTN 量化
qconfig = RTNConfig(bits=4, group_size=128)
```

不同算法的对比：

| 算法 | 量化速度 | 精度 | 适用场景 |
|------|---------|------|---------|
| **RTN** | ⚡ 极快 | ⭐⭐ | 快速原型、基线对比 |
| **GPTQ** | 🐢 慢 | ⭐⭐⭐⭐ | 高精度需求、开源预量化模型常用 |
| **AWQ** | 🚶 中 | ⭐⭐⭐⭐ | 兼顾速度和精度 |
| **AutoRound** | 🐢 慢 | ⭐⭐⭐⭐⭐ | 追求最高精度（Intel 推荐） |

---

## 常见问题排查

### 问题 1：`ImportError: No module named 'neural_compressor'`

**原因**：Neural Compressor 未正确安装或不在 Python 路径中。

**解决方案**：
```shell
# 确认已安装
pip show neural-compressor-pt
# 如果未安装，重新安装
pip install neural-compressor-pt
```

### 问题 2：量化后模型精度下降明显

**可能原因和解决方案**：
1. 校准数据不具代表性：使用与推理数据分布一致的校准数据集
2. 校准样本太少：增加校准样本数量（建议 100+）
3. 尝试其他量化算法：如 SmoothQuant 或仅权重量化
4. 排除敏感层不量化：使用 `set_local` 配置为特定层设置更高精度

### 问题 3：CPU 上量化模型速度没有提升

**可能原因**：
1. 未安装 Intel Extension for PyTorch（IPEX）：IPEX 提供了优化的 INT8 算子实现
2. 模型太小：小模型的量化开销可能抵消收益
3. 硬件不支持：较老的 CPU 可能没有 AVX2/AVX-512/VNNI 指令集支持

> **建议**：在 Intel Xeon 可扩展处理器或 Intel Core Ultra 处理器上，配合 IPEX 使用可获得最佳性能提升。

---

## 下一步

恭喜您完成了第一个 Neural Compressor 量化程序！接下来您可以：

- 阅读 [量化技术详解](04-quantization-techniques.md) 深入了解各种量化算法原理
- 查看 [API 概览](05-api-overview.md) 了解 prepare/convert/autotune 等核心 API 的详细用法
- 访问 [官方示例库](https://github.com/intel/neural-compressor/tree/main/examples) 获取更多场景的示例代码

---

[← 上一章：安装指南](02-installation.md) | [下一章：量化技术详解 →](04-quantization-techniques.md)

