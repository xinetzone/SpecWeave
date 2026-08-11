---
id: "neural-compressor-wiki-best-practices"
title: "最佳实践"
date: "2026-08-09"
category: "learning"
author: "SpecWeave"
status: "stable"
source: "https://intel.github.io/neural-compressor/latest/docs/source/Welcome.html"
summary: "Intel Neural Compressor 量化流程最佳实践：校准数据选择、精度验证、性能调优与常见陷阱。"
tags: ["neural-compressor", "best-practices", "performance", "calibration"]
---

# 最佳实践

本章总结了使用 Intel Neural Compressor 进行模型量化时的工程最佳实践，涵盖校准数据准备、量化策略选择、精度验证、性能调优以及常见陷阱规避等方面。这些经验来自大量实际项目验证，可帮助您首次量化即获得理想效果。

---

## 1. 校准最佳实践

**校准（Calibration）** 是静态量化和需要数据的仅权重量化算法（如 GPTQ、AutoRound）中的关键步骤。校准数据的质量直接决定了量化后模型的精度。

### 1.1 使用真实分布数据

- **必须使用与推理时相同分布的数据**：校准数据集应来自真实业务场景，覆盖各种典型输入情况，包括边缘案例（edge cases）
- **随机数据仅用于流程验证**：`torch.randn()` 生成的随机数据只能用来验证量化流程是否跑通，绝对不能用于最终量化——随机数据无法反映真实激活值分布，会导致 scale/zero_point 计算完全失真
- **数据预处理保持一致**：校准数据必须经过与推理时完全相同的预处理流程（归一化、缩放、tokenization 等）

### 1.2 校准数据量控制

| 模型类型 | 推荐样本量 | 说明 |
|---------|-----------|------|
| CNN 视觉模型 | 100~500 张图像 | ImageNet 等标准数据集取一个子集即可 |
| Transformer NLP 模型 | 128~512 条文本 | 序列长度分布应与实际推理一致 |
| 大语言模型（LLM） | 128~256 条样本 | GPTQ/AutoRound 建议使用 `nsamples=128` |
| 小模型（<10MB） | 50~100 条 | 模型本身表征能力有限，过多数据无额外收益 |

- **避免过少**：少于 50 个样本可能导致统计量不稳定，离群值影响过大
- **避免过多**：超过 1000 个样本通常带来的精度提升可忽略，但显著增加校准时间
- **批次大小适中**：使用与推理相同的 batch size，避免因 batch size 差异导致激活值分布变化

### 1.3 模型预处理规范

```python
model = YourModel()
model.eval()  # 必须！切换到评估模式，关闭 Dropout 和 BatchNorm 训练行为
```

- 务必在调用 `prepare()` 之前调用 `model.eval()`
- 如果模型包含 BatchNorm 层，确保已加载预训练权重且处于 eval 模式
- 对于 ONNX 模型，量化前务必执行：
  ```python
  import onnx
  from onnxsim import simplify
  from neural_compressor.onnxrt.quantization import quant_pre_process

  model = onnx.load("model.onnx")
  model = simplify(model)[0]  # 简化计算图
  model = quant_pre_process(model)  # 量化预处理（折叠 BN、处理残差连接等）
  onnx.save(model, "model_preprocessed.onnx")
  ```

---

## 2. 按模型类型选择量化策略

不同模型架构对量化的敏感度差异很大，选对量化策略是成功量化的第一步。

### 2.1 策略选择速查表

| 模型类型 | 架构特征 | 推荐量化策略 | 不推荐 | 原因 |
|---------|---------|------------|--------|------|
| **MLP/Linear 密集网络** | 大量 `nn.Linear` 层，如推荐系统、MLP-Mixer | **INT8 动态量化（DynamicQuantConfig）** | 静态量化 | 动态量化对 Linear 层权重缓存优化好，无需校准且精度损失小 |
| **CNN 卷积网络** | 大量 `nn.Conv2d` 层，如 ResNet、YOLO | **INT8 静态 QDQ 量化（StaticQuantConfig）** | 动态量化 | 动态量化不支持高效 Conv 算子加速，静态量化可利用 Intel VNNI 指令集 |
| **Transformer 模型** | Attention + FFN，如 BERT、GPT | **动态量化 或 Weight-only INT4** | 静态 QDQ | 静态量化对 Attention 中的 Softmax/LayerNorm 层敏感，容易造成精度灾难；动态量化推理时计算激活 scale，精度保持更好 |
| **大语言模型（LLM）** | 数十亿参数，如 LLaMA、Qwen | **Weight-only 量化（GPTQ/AWQ/AutoRound INT4）** | INT8 静态/动态 | 大模型激活值 outlier 严重，INT8 激活量化精度损失大；Weight-only 仅量化权重，精度保持极佳 |
| **小模型（<200KB）** | 参数极少，如简单分类头 | **FP16 或 保持 FP32** | INT8 | 量化反量化开销超过计算本身收益，反而导致性能下降 |
| **多模态/VLM 模型** | 视觉编码器 + LLM 解码器 | **分模块量化（set_local 混合精度）** | 一刀切量化 | 视觉编码器和语言解码器的量化敏感度不同，需分别配置 |

### 2.2 数据类型选择建议

| 精度格式 | 精度表现 | 模型大小 | CPU 加速比 | 适用场景 |
|---------|---------|---------|-----------|---------|
| **FP32** | 基准（100%） | 基准（100%） | 1x | 精度敏感场景、小模型 |
| **FP16** | 接近 FP32（~99.9%） | 50% | **不稳定**（0.8x~1.5x） | 模型大小敏感、GPU 推理、精度要求高 |
| **BF16** | 接近 FP32（~99.9%） | 50% | 1x~1.2x（需 AMX 支持） | Intel Xeon CPU、Habana Gaudi |
| **INT8 静态** | 良好（~98~99.5%） | 25% | 2x~4x | CNN 模型、CPU 批量推理 |
| **INT8 动态** | 优秀（~99~99.9%） | 25%（权重） | 1.5x~3x | Transformer/MLP、CPU 推理 |
| **INT4 Weight-only** | 良好（~97~99%） | ~12.5% | 1.2x~2x（CPU）/ 2x~3x（GPU） | LLM 部署、内存受限场景 |

> **关键提醒**：FP16 的主要价值在于**减半模型大小和内存带宽占用**，CPU 上的加速并不稳定——某些 CPU 算子甚至可能因 FP16 需转换为 FP32 计算而变慢。如果主要目标是 CPU 推理加速，优先考虑 INT8 而非 FP16。

---

## 3. 精度验证技巧

量化后必须验证精度，"感觉没问题"不是验收标准。

### 3.1 建立基线对比

```python
import torch

def compare_models(fp32_model, quant_model, dataloader, num_batches=10):
    fp32_model.eval()
    quant_model.eval()

    all_fp32_outputs = []
    all_quant_outputs = []

    with torch.no_grad():
        for i, (inputs, _) in enumerate(dataloader):
            if i >= num_batches:
                break
            fp32_out = fp32_model(inputs)
            quant_out = quant_model(inputs)
            all_fp32_outputs.append(fp32_out)
            all_quant_outputs.append(quant_out)

    fp32_cat = torch.cat(all_fp32_outputs)
    quant_cat = torch.cat(all_quant_outputs)

    mae = torch.mean(torch.abs(fp32_cat - quant_cat)).item()
    max_diff = torch.max(torch.abs(fp32_cat - quant_cat)).item()
    cos_sim = torch.nn.functional.cosine_similarity(
        fp32_cat.flatten().unsqueeze(0),
        quant_cat.flatten().unsqueeze(0)
    ).item()

    print(f"平均绝对误差 (MAE): {mae:.6f}")
    print(f"最大绝对误差: {max_diff:.6f}")
    print(f"余弦相似度: {cos_sim:.6f}")
```

### 3.2 精度验收标准

| 指标 | 可接受 | 良好 | 优秀 |
|------|-------|------|------|
| 余弦相似度 | > 0.99 | > 0.999 | > 0.9999 |
| MAE（归一化后） | < 0.01 | < 0.001 | < 0.0001 |
| 任务精度下降 | < 2% | < 1% | < 0.5% |

### 3.3 精度问题排查路径

如果量化后精度下降超过预期，按以下顺序排查：

1. **检查 `model.eval()`**：确认模型在量化前已设为 eval 模式
2. **验证校准数据**：确认使用真实分布数据，预处理正确
3. **尝试非对称激活量化**：`StaticQuantConfig(act_sym=False)`（默认即为非对称）
4. **更换观测器算法**：激活值从 `minmax` 改为 `kl`（KL 散度）
   ```python
   config = StaticQuantConfig(act_algo="kl")
   ```
5. **敏感层回退**：使用 `set_local()` 将对量化敏感的层（通常是最后一层、输出头、LayerNorm）回退到 FP32
   ```python
   config.set_local("lm_head", StaticQuantConfig(w_dtype="fp32", act_dtype="fp32"))
   ```
6. **尝试 SmoothQuant**：对于 Transformer 模型，SmoothQuant 可平滑激活异常值
7. **考虑仅权重量化**：如果激活量化精度损失不可接受，退一步使用 Weight-only 量化
8. **使用 autotune**：让 Neural Compressor 自动搜索最优配置

---

## 4. 性能调优

### 4.1 CPU 推理线程配置

在 Intel CPU 上推理时，线程配置对延迟和吞吐量影响显著：

```bash
# 延迟敏感场景（单请求低延迟）
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=4
export KMP_AFFINITY=granularity=fine,compact,1,0

# 吞吐量敏感场景（批量处理）
export OMP_NUM_THREADS=<物理核心数>
export KMP_BLOCKTIME=1
```

- `OPENBLAS_NUM_THREADS=1`：禁止 OpenBLAS 内部多线程，避免与 PyTorch 线程竞争
- `OMP_NUM_THREADS=4`：平衡延迟和吞吐量的经验值，可根据实际 CPU 调整
- `KMP_AFFINITY=compact`：将线程绑定到相邻物理核心，减少 NUMA 跨节点访问

### 4.2 后端选择

| 后端 | 安装方式 | 最佳场景 |
|------|---------|---------|
| **IPEX**（Intel Extension for PyTorch） | `pip install intel-extension-for-pytorch` | Intel CPU/GPU 最佳性能，推荐生产环境使用 |
| **PT2E**（TorchDynamo + Inductor） | 随 PyTorch 2.0+ 内置 | 开发调试、无需额外安装、支持 `torch.compile` 进一步优化 |

默认情况下 Neural Compressor 会自动检测可用后端，IPEX 优先。

### 4.3 输入批处理优化

- 动态量化对 batch size 不敏感，适合可变 batch size 在线服务
- 静态量化推荐固定 batch size 进行校准和推理
- 大模型 Weight-only 量化建议使用 `use_layer_wise=True` 降低峰值内存：
  ```python
  config = RTNConfig(bits=4, use_layer_wise=True)
  ```

---

## 5. 常见陷阱与避坑指南

### ❌ 陷阱 1：使用随机数据校准

**错误做法**：
```python
calib_data = torch.randn(100, 3, 224, 224)  # 错误！
```

**正确做法**：从验证集或训练集中采样真实数据，应用与推理一致的预处理。

### ❌ 陷阱 2：忘记 `model.eval()`

量化前忘记调用 `model.eval()` 会导致：
- Dropout 层随机丢弃神经元，校准统计量不稳定
- BatchNorm 使用 batch 统计量而非 running mean/var
- 结果：量化后精度随机下降

### ❌ 陷阱 3：对 CNN 使用动态量化

动态量化仅优化 Linear 层的权重缓存，Conv 层的激活值仍在推理时动态量化，无法利用 Intel VNNI 指令集加速。CNN 模型务必使用静态量化。

### ❌ 陷阱 4：对 Transformer 使用静态 QDQ 量化（无 SmoothQuant）

Transformer 的 Attention 机制中存在严重的激活值 outlier（某些 token 的激活值远大于其他 token），直接静态量化会导致这些 outlier 截断过多信息，精度可能从 90% 暴跌到 50% 以下。必须使用 SmoothQuant 预处理或直接选择动态/Weight-only 量化。

### ❌ 陷阱 5：对小模型强制 INT8 量化

模型参数量小于 200KB 时，INT8 量化带来的反量化计算开销可能超过矩阵乘法本身的节省，导致推理速度不升反降。此时 FP16 或保持 FP32 是更好的选择。

### ❌ 陷阱 6：校准后不验证精度

不要假设量化后精度一定可接受。某些模型（特别是含自定义算子或特殊结构的模型）可能出现严重精度问题。必须在验证集上对比量化前后的输出。

### ❌ 陷阱 7：过度追求低比特

INT4 不是万金油。4-bit 量化虽然模型最小，但：
- 精度下降比 INT8 更明显
- CPU 上的加速不如 INT8（需要额外的反量化和类型转换）
- 某些硬件没有 INT4 计算指令，需要模拟执行

**建议**：先尝试 INT8，精度不够再考虑 INT4；生产环境优先 INT8，大模型部署才考虑 INT4 Weight-only。

### ❌ 陷阱 8：ONNX 模型未做预处理直接量化

ONNX 模型可能包含：
- 未折叠的 BatchNorm 层
- 冗余的算子（如连续两个 Transpose）
- 不利于量化的残差连接结构

未做 `onnxsim.simplify()` 和 `quant_pre_process()` 直接量化，可能导致：
- 量化算子融合失败
- 某些层跳过量化
- 精度异常下降

---

## 6. 量化检查清单

每次执行量化前，对照以下清单逐项确认：

- [ ] 模型已调用 `model.eval()`
- [ ] 已加载正确的预训练权重
- [ ] 校准数据来自真实分布，预处理流程与推理一致
- [ ] 校准样本量在推荐范围内（100~500 条）
- [ ] 根据模型类型选择了正确的量化策略（参考 2.1 节速查表）
- [ ] ONNX 模型已执行 simplify 和 quant_pre_process
- [ ] 已设定精度验证方案（余弦相似度/任务指标）
- [ ] 对敏感层（输出头、LayerNorm）考虑了 set_local 回退
- [ ] 线程配置已针对部署场景优化
- [ ] 量化后在验证集上验证了精度和性能

---

[← 上一章：API 概览](05-api-overview.md) | [下一章：常见问题 →](07-faq.md)
