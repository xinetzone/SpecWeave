---
id: "deepseek-v4-self-hosting"
title: "06 开源自托管方案"
version: "1.0"
source: "HuggingFace deepseek-ai/DeepSeek-V4-Flash + github.com/deepseek-ai/DeepEP + github.com/deepseek-ai/DeepGEMM + MIT许可证"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/07-vendor-product-learning/deepseek/06-self-hosting.toml"
type: "Wiki Document"
description: "DeepSeek-V4-Flash开源模型自托管完整指南：MIT协议条款、硬件需求、部署步骤、成本估算"
tags: ["DeepSeek", "V4-Flash", "自托管", "MIT协议", "私有化部署", "vLLM", "SGLang"]
category: "learning/07-vendor-product-learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "V4-Flash以MIT协议完全开源，可从HuggingFace免费下载权重，支持vLLM/SGLang部署，最小配置2张H20/H100可跑FP8，4张RTX 4090可跑量化版，无调用限制、无token计费。"
last_verified: "2026-08-19"
---
# 06 开源自托管方案

> V4-Pro未开源，无法自托管。本章仅适用于DeepSeek-V4-Flash。

## 6.1 MIT协议要点

V4-Flash采用**MIT许可证**，这是最宽松的开源协议之一：

| 权限 | 说明 |
|------|------|
| ✅ 商业使用 | 可用于任何商业产品，无需付费 |
| ✅ 修改 | 可以修改模型权重和代码 |
| ✅ 分发 | 可以分发、再许可、出售 |
| ✅ 私有使用 | 可以内部使用不公开 |
| ✅ 无用户限制 | 不限制服务用户数量 |
| ✅ 无Token限制 | 不限制调用次数和token量 |
| ❗ 唯一要求 | 在产品中包含原始版权声明和许可声明 |

**与其他模型协议对比**：

| 模型 | 协议 | 商业使用 | 开源要求 |
|------|------|---------|---------|
| DeepSeek-V4-Flash | **MIT** | ✅ 自由 | ❌ 无需开源 |
| Llama系列 | Llama License | ⚠️ 需申请 | ❌ 无需开源 |
| Qwen系列 | Apache 2.0 | ✅ 自由 | ❌ 无需开源 |
| GLM系列 | Apache 2.0 | ✅ 自由 | ❌ 无需开源 |

## 6.2 模型权重获取

| 资源 | 链接 | 说明 |
|------|------|------|
| HuggingFace权重 | [huggingface.co/deepseek-ai/DeepSeek-V4-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) | 主下载渠道 |
| HuggingFace Pro-Flash | 暂未完全开放 | Pro的预览版权重 |
| ModelScope魔搭 | modelscope.cn搜索DeepSeek-V4-Flash | 国内镜像，速度更快 |
| GitHub | [github.com/deepseek-ai](https://github.com/deepseek-ai) | 官方代码仓库 |

### 模型文件结构

- `config.json`：模型配置（MoE路由、隐藏层维度等）
- `model*.safetensors`：模型权重文件（分片存储）
- `tokenizer.json`/`tokenizer_config.json`：分词器
- `generation_config.json`：生成默认参数
- 总大小：BF16约568GB，FP8约284GB

## 6.3 硬件需求详细方案

### 6.3.1 方案对比

| 方案 | 显卡配置 | 显存需求 | 显存/卡 | 量化方式 | 适用场景 | 预估成本（二手/租赁） |
|------|---------|---------|--------|---------|---------|-------------------|
| **最低配置** | 2×H20/H100 | 192GB | 96GB | FP8 | 开发测试、低并发 | 云服务约15-30元/小时 |
| **推荐生产** | 4×H20 141GB | 564GB | 141GB | BF16 | 生产环境、高质量 | 云服务约40-80元/小时 |
| **消费级方案** | 4×RTX 4090 | 96GB | 24GB | GPTQ-Int4 | 个人/小团队实验 | 自购约6-8万元 |
| **性价比方案** | 2×A100 80GB | 160GB | 80GB | AWQ-Int4 | 中等质量服务 | 云服务约20-40元/小时 |
| **大规模部署** | 8×H100 80GB | 640GB | 80GB | BF16+TP8 | 高并发服务 | 云服务约100-200元/小时 |

### 6.3.2 显存估算

| 组件 | BF16 | FP8 | Int4 |
|------|------|-----|------|
| 模型权重 | ~568GB | ~284GB | ~142GB |
| KV Cache（1M上下文×并发1） | ~120GB | ~60GB | ~30GB |
| 推理框架开销 | ~20GB | ~20GB | ~20GB |
| **总显存（并发1）** | **~708GB** | **~364GB** | **~192GB** |
| **并发能力** | 高并发（>50） | 中高并发（20-50） | 低中并发（5-20） |

> 实际部署时可通过PagedAttention等技术优化KV Cache显存占用。

### 6.3.3 推理速度参考

| 配置 | 并发数 | 首Token延迟 | 生成速度（tokens/s） |
|------|-------|-----------|-------------------|
| 8×H100 BF16 | 64 | ~0.3s | ~2000+ total |
| 4×H20 FP8 | 32 | ~0.5s | ~800+ total |
| 2×A100 Int4 | 8 | ~1s | ~200+ total |
| 4×4090 Int4 | 4 | ~2s | ~100+ total |

## 6.4 部署步骤（vLLM推荐）

### 6.4.1 环境准备

```bash
# 推荐使用CUDA 12.1+，Python 3.10+
pip install vllm
# 或从源码安装（获得最新优化）
pip install "vllm @ git+https://github.com/vllm-project/vllm.git"
```

### 6.4.2 基础启动命令

```bash
# FP8精度，4卡张量并行，1M上下文
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 4 \
  --trust-remote-code \
  --max-model-len 1048576 \
  --dtype fp8 \
  --kv-cache-dtype fp8 \
  --enable-prefix-caching \
  --port 8000

# Int4量化，2卡部署（小显存方案）
vllm serve deepseek-ai/DeepSeek-V4-Flash \
  --tensor-parallel-size 2 \
  --trust-remote-code \
  --max-model-len 131072 \
  --dtype half \
  --quantization awq \
  --port 8000
```

### 6.4.3 SGLang部署（性能更好，推荐生产环境）

```bash
pip install sglang[slim]

python -m sglang.launch_server \
  --model deepseek-ai/DeepSeek-V4-Flash \
  --tp 4 \
  --dtype fp8 \
  --mem-fraction-static 0.85 \
  --enable-mtp \
  --enable-dp-attention \
  --context-length 1048576 \
  --port 8000
```

### 6.4.4 验证部署

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # 本地部署不需要key
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-V4-Flash",
    messages=[{"role": "user", "content": "你好，请介绍一下自己"}],
    max_tokens=1024
)
print(response.choices[0].message.content)
```

## 6.5 自托管 vs API调用 成本对比

### API调用成本

| 日调用量（tokens） | V4-Flash高峰 | V4-Flash空闲 | 月成本（30天） |
|------------------|-------------|-------------|--------------|
| 100万 | ~6元/天 | ~3元/天 | 90-180元 |
| 1000万 | ~60元/天 | ~30元/天 | 900-1800元 |
| 1亿 | ~600元/天 | ~300元/天 | 9000-18000元 |

### 自托管成本估算（云GPU租赁）

| 配置 | 日租金（约） | 月租金（约） | 适合日调用量 |
|------|-----------|-----------|-----------|
| 2×H20 FP8 | ~500-700元 | ~15000-21000元 | 5000万+tokens |
| 4×H20 BF16 | ~1000-1500元 | ~30000-45000元 | 2亿+tokens |

### 自托管盈亏平衡点

- 日调用量**低于3000万tokens**：API调用更划算
- 日调用量**高于5000万tokens**：自托管开始省钱
- 有数据合规需求或定制化需求：无论规模大小都应自托管

## 6.6 自托管注意事项

1. **首次加载较慢**：模型加载到显存需要5-15分钟（视配置）
2. **网络下载**：模型权重284GB（FP8），建议使用ModelScope国内镜像
3. **KV Cache优化**：使用`--enable-prefix-caching`（vLLM）或`--enable-radix-cache`（SGLang）可大幅提升重复前缀场景的效率
4. **MTP加速**：V4-Flash支持2-token前瞻预测（MTP），开启后推理速度提升约30-50%
5. **思考模式**：自托管也支持思考模式，需在API调用中传入`thinking: "high"`或`"max"`
6. **无官方技术支持**：自部署问题需通过GitHub Issues或社区解决
7. **更新滞后**：官方可能推送模型更新/修复，自托管需手动更新权重
