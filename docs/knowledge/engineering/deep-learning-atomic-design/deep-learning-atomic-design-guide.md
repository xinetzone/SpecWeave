---
title: 深度学习原子化设计指南
date: 2026-07-04
author: Trae AI Engineering
version: 1.0
description: 系统化的深度学习原子化设计方法论、最佳实践与代码示例
---

# 深度学习原子化设计指南

## 目录

1. [原子化设计理念概述](#1-原子化设计理念概述)
2. [深度学习原子化组件分类](#2-深度学习原子化组件分类)
3. [主流框架原子化实现模式](#3-主流框架原子化实现模式)
4. [原子化设计最佳实践](#4-原子化设计最佳实践)
5. [代码示例](#5-代码示例)
6. [评估指标](#6-评估指标)

---

## 1. 原子化设计理念概述

### 1.1 定义

**深度学习原子化设计**是一种将复杂的深度学习系统拆解为最小可复用组件（原子），通过标准化接口和组合模式构建灵活、可维护、可扩展系统的方法论。

原子化设计的核心思想是：**将复杂系统分解为独立的、可测试的、可复用的原子组件，通过组合而非继承来构建上层功能**。

### 1.2 核心原则

| 原则 | 说明 | 深度学习场景示例 |
|------|------|-----------------|
| **单一职责** | 每个组件只负责一个特定功能 | `MultiHeadAttention` 只负责注意力计算 |
| **组合优于继承** | 通过嵌套组合构建复杂模型 | `TransformerEncoder` 由多个 `EncoderLayer` 组合而成 |
| **接口标准化** | 统一的组件接口规范 | `__init__` / `forward` / `from_pretrained` / `save_pretrained` |
| **配置与实现分离** | 超参数管理与模型实现解耦 | `Config` 类管理超参数，`Model` 类实现架构 |
| **关注点分离** | 不同阶段的逻辑独立封装 | Pipeline 将预处理、推理、后处理解耦 |
| **高内聚低耦合** | 组件内部紧密关联，组件间松耦合 | 数据加载、模型训练、推理部署相互独立 |

### 1.3 在深度学习中的应用

深度学习系统的原子化设计体现在以下层面：

```
深度学习系统
├── 数据层原子：数据加载、预处理、增强、采样
├── 模型层原子：Layer、Block、Module、Encoder/Decoder
├── 训练层原子：优化器、损失函数、调度器、训练循环
├── 推理层原子：Pipeline、预处理、后处理、服务封装
└── 监控层原子：指标计算、日志记录、漂移检测、告警
```

---

## 2. 深度学习原子化组件分类

### 2.1 数据层组件

数据层负责数据的获取、预处理和增强，是模型训练的基础。

| 组件类型 | 职责 | 实现示例 |
|----------|------|---------|
| **数据加载器** | 从存储读取数据，支持分批加载 | `torch.utils.data.DataLoader`、`tf.data.Dataset` |
| **预处理管道** | 数据清洗、格式转换、特征工程 | 自定义 `Preprocessor` 类 |
| **数据增强器** | 随机变换以增加数据多样性 | `torchvision.transforms`、`albumentations` |
| **采样策略** | 类别平衡、难例挖掘、负采样 | 自定义 `Sampler` 类 |

### 2.2 模型层组件

模型层是深度学习的核心，负责特征提取和预测。

| 组件类型 | 职责 | 实现示例 |
|----------|------|---------|
| **基础层（Layer）** | 最小计算单元 | `nn.Linear`、`nn.Conv2d`、`tf.keras.layers.Dense` |
| **功能块（Block）** | 一组相关层的封装 | `ResidualBlock`、`MultiHeadAttention` |
| **模块（Module）** | 多个 Block 的组合 | `TransformerEncoder`、`ResNetStage` |
| **完整模型（Model）** | 端到端的模型架构 | `BERT`、`ResNet50`、`GPT` |

### 2.3 训练层组件

训练层负责模型参数优化和训练流程管理。

| 组件类型 | 职责 | 实现示例 |
|----------|------|---------|
| **优化器** | 参数更新策略 | `torch.optim.Adam`、`tensorflow.keras.optimizers.Adam` |
| **损失函数** | 目标函数定义 | `nn.CrossEntropyLoss`、自定义损失 |
| **学习率调度器** | 学习率动态调整 | `torch.optim.lr_scheduler.CosineAnnealingLR` |
| **训练循环** | 训练流程编排 | `Trainer` 类、`tf.keras.Model.fit` |
| **评估器** | 验证和测试流程 | `Evaluator` 类 |

### 2.4 推理层组件

推理层负责模型部署和在线预测。

| 组件类型 | 职责 | 实现示例 |
|----------|------|---------|
| **预处理** | 输入数据标准化 | 自定义 `preprocess` 方法 |
| **推理引擎** | 模型推理执行 | `torch.inference_mode()`、`tensorrt` |
| **后处理** | 输出结果解析 | 自定义 `postprocess` 方法 |
| **Pipeline** | 端到端推理封装 | `transformers.pipeline` |
| **服务封装** | API 接口暴露 | FastAPI、TensorFlow Serving |

### 2.5 监控层组件

监控层负责模型质量和系统性能的持续追踪。

| 组件类型 | 职责 | 实现示例 |
|----------|------|---------|
| **指标计算** | 准确率、F1、AUC 等 | `sklearn.metrics`、自定义计算函数 |
| **日志记录** | 训练过程记录 | TensorBoard、Weights & Biases |
| **漂移检测** | 数据/模型漂移识别 | PSI、KS 检验、ADWIN |
| **性能监控** | 推理延迟、吞吐量 | Prometheus、Grafana |

---

## 3. 主流框架原子化实现模式

### 3.1 PyTorch nn.Module 组合模式

#### 模式概述

PyTorch 通过 `nn.Module` 基类构建层次化的组件体系。每个组件都是独立的 `nn.Module` 子类，可以嵌套组合形成复杂模型。

#### 核心特点

| 特点 | 说明 |
|------|------|
| **单一职责** | 每个 `nn.Module` 子类只负责一个特定功能 |
| **嵌套组合** | 通过在 `__init__` 中声明子模块实现层次化 |
| **自动管理** | `nn.Module` 自动追踪参数、梯度和设备 |
| **灵活扩展** | 通过继承 `nn.Module` 轻松创建自定义组件 |

#### 实现示例：Transformer Encoder

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
    
    def split_heads(self, x):
        batch_size, seq_len, d_model = x.size()
        return x.view(batch_size, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
    
    def forward(self, q, k, v, mask=None):
        q = self.split_heads(self.q_proj(q))
        k = self.split_heads(self.k_proj(k))
        v = self.split_heads(self.v_proj(v))
        
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.head_dim, dtype=torch.float32))
        
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))
        
        attn_weights = F.softmax(attn_scores, dim=-1)
        output = torch.matmul(attn_weights, v)
        
        output = output.transpose(1, 2).contiguous().view(-1, q.size(2), self.d_model)
        return self.out_proj(output)


class PositionWiseFFN(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        return self.fc2(self.dropout(F.gelu(self.fc1(x))))


class EncoderLayer(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, n_heads)
        self.ffn = PositionWiseFFN(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))
        
        ffn_output = self.ffn(x)
        x = self.norm2(x + self.dropout2(ffn_output))
        return x


class TransformerEncoder(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, num_layers, dropout=0.1):
        super().__init__()
        self.layers = nn.ModuleList([
            EncoderLayer(d_model, n_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
    
    def forward(self, x, mask=None):
        for layer in self.layers:
            x = layer(x, mask)
        return self.norm(x)
```

### 3.2 Hugging Face Config-Model-Pipeline 三层抽象

#### 模式概述

Hugging Face Transformers 采用**配置-模型-流水线**三层抽象架构，将模型定义、超参数管理和推理流程解耦。

#### 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    User API Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  pipeline() │  │  AutoModel   │  │   Trainer    │   │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼────────────────┼────────────────┼─────────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼─────────────┐
│                    Core Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ PreTrained  │  │PreTrained    │  │   Tokenizer  │   │
│  │   Config    │  │   Model      │  │   /Processor │   │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼────────────────┼────────────────┼─────────────┘
          │                │                │
┌─────────▼────────────────▼────────────────▼─────────────┐
│                 Infrastructure Layer                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │Weight       │  │Device        │  │Checkpoint    │   │
│  │ Converter   │  │ Management   │  │  Loading     │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### 实现示例：Config-Model-Pipeline

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import torch
import torch.nn as nn


@dataclass
class TransformerConfig:
    d_model: int = 512
    n_heads: int = 8
    d_ff: int = 2048
    num_layers: int = 6
    vocab_size: int = 30522
    max_seq_len: int = 512
    dropout: float = 0.1
    
    @classmethod
    def from_json(cls, json_path: str) -> "TransformerConfig":
        import json
        with open(json_path, "r") as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def to_json(self, json_path: str) -> None:
        import json
        with open(json_path, "w") as f:
            json.dump(self.__dict__, f, indent=2)


class TransformerModel(nn.Module):
    def __init__(self, config: TransformerConfig):
        super().__init__()
        self.config = config
        
        self.embedding = nn.Embedding(config.vocab_size, config.d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, config.max_seq_len, config.d_model))
        
        self.encoder = TransformerEncoder(
            d_model=config.d_model,
            n_heads=config.n_heads,
            d_ff=config.d_ff,
            num_layers=config.num_layers,
            dropout=config.dropout
        )
        
        self.classifier = nn.Linear(config.d_model, 2)
    
    def forward(self, input_ids: torch.Tensor, attention_mask: Optional[torch.Tensor] = None):
        x = self.embedding(input_ids) + self.pos_encoding[:, :input_ids.size(1), :]
        x = self.encoder(x, attention_mask)
        cls_output = x[:, 0, :]
        return self.classifier(cls_output)
    
    @classmethod
    def from_pretrained(cls, model_name_or_path: str) -> "TransformerModel":
        config = TransformerConfig.from_json(f"{model_name_or_path}/config.json")
        model = cls(config)
        model.load_state_dict(torch.load(f"{model_name_or_path}/pytorch_model.bin", weights_only=True))
        return model
    
    def save_pretrained(self, save_directory: str) -> None:
        import os
        os.makedirs(save_directory, exist_ok=True)
        self.config.to_json(f"{save_directory}/config.json")
        torch.save(self.state_dict(), f"{save_directory}/pytorch_model.bin")


class Pipeline(ABC):
    def __init__(self, model: nn.Module, tokenizer, device: str = "cpu"):
        self.model = model.to(device)
        self.tokenizer = tokenizer
        self.device = device
        self.model.eval()
    
    @abstractmethod
    def preprocess(self, inputs: Any) -> Dict[str, torch.Tensor]:
        pass
    
    @abstractmethod
    def _forward(self, model_inputs: Dict[str, torch.Tensor]) -> Any:
        pass
    
    @abstractmethod
    def postprocess(self, model_outputs: Any) -> Any:
        pass
    
    def __call__(self, inputs: Any) -> Any:
        model_inputs = self.preprocess(inputs)
        model_outputs = self._forward(model_inputs)
        return self.postprocess(model_outputs)


class TextClassificationPipeline(Pipeline):
    def preprocess(self, inputs: str) -> Dict[str, torch.Tensor]:
        encoding = self.tokenizer(inputs, return_tensors="pt", padding=True, truncation=True)
        return {k: v.to(self.device) for k, v in encoding.items()}
    
    def _forward(self, model_inputs: Dict[str, torch.Tensor]) -> torch.Tensor:
        with torch.no_grad():
            return self.model(**model_inputs)
    
    def postprocess(self, model_outputs: torch.Tensor) -> List[Dict[str, float]]:
        logits = model_outputs
        probabilities = torch.softmax(logits, dim=-1).cpu().numpy()
        return [
            {"label": "positive" if p[1] > p[0] else "negative", "score": float(max(p))}
            for p in probabilities
        ]
```

### 3.3 TensorFlow Keras Layer 封装模式

#### 模式概述

TensorFlow Keras 通过继承 `tf.keras.layers.Layer`，将一组相关层封装为可复用的组件，支持权重共享和动态形状。

#### 核心特点

| 特点 | 说明 |
|------|------|
| **权重共享** | 同一 Layer 实例可多次调用，共享权重 |
| **状态管理** | `build()` 方法延迟构建权重，支持动态形状 |
| **兼容性** | 自定义 Layer 可在 Sequential 和 Functional API 中使用 |
| **序列化** | 支持 `save()` / `load_model()` 完整保存和加载 |

#### 实现示例：CNN Residual Block

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class ResidualBlock(layers.Layer):
    def __init__(self, filters, kernel_size=3, strides=1, **kwargs):
        super().__init__(**kwargs)
        self.filters = filters
        self.kernel_size = kernel_size
        self.strides = strides
        
        self.conv1 = layers.Conv2D(filters, kernel_size, strides=strides, padding="same", use_bias=False)
        self.bn1 = layers.BatchNormalization()
        self.relu1 = layers.ReLU()
        
        self.conv2 = layers.Conv2D(filters, kernel_size, strides=1, padding="same", use_bias=False)
        self.bn2 = layers.BatchNormalization()
        self.relu2 = layers.ReLU()
        
        self.shortcut = None
    
    def build(self, input_shape):
        self.input_channels = input_shape[-1]
        if self.strides > 1 or self.filters != self.input_channels:
            self.shortcut = keras.Sequential([
                layers.Conv2D(self.filters, 1, strides=self.strides, use_bias=False),
                layers.BatchNormalization()
            ])
        super().build(input_shape)
    
    def call(self, inputs, training=False):
        x = self.conv1(inputs)
        x = self.bn1(x, training=training)
        x = self.relu1(x)
        
        x = self.conv2(x)
        x = self.bn2(x, training=training)
        
        shortcut = self.shortcut(inputs, training=training) if self.shortcut else inputs
        x = layers.add([x, shortcut])
        return self.relu2(x)
    
    def get_config(self):
        config = super().get_config()
        config.update({
            "filters": self.filters,
            "kernel_size": self.kernel_size,
            "strides": self.strides
        })
        return config
```

---

## 4. 原子化设计最佳实践

### 4.1 接口设计

#### 标准化接口规范

| 方法 | 功能 | 实现要求 |
|------|------|---------|
| `__init__(config)` | 初始化组件 | 接收配置对象，初始化子组件 |
| `forward(x)` | 前向传播 | 定义计算逻辑，返回输出张量 |
| `from_pretrained(path)` | 加载预训练模型 | 类方法，从路径加载配置和权重 |
| `save_pretrained(path)` | 保存模型 | 将配置和权重保存到路径 |
| `get_config()` | 获取配置 | 返回可序列化的配置字典 |

#### 输入输出契约

```python
from pydantic import BaseModel, Field


class ModelInput(BaseModel):
    input_ids: torch.Tensor = Field(description="Token IDs tensor")
    attention_mask: Optional[torch.Tensor] = Field(None, description="Attention mask tensor")
    
    class Config:
        arbitrary_types_allowed = True


class ModelOutput(BaseModel):
    logits: torch.Tensor = Field(description="Model logits")
    hidden_states: Optional[torch.Tensor] = Field(None, description="Hidden states")
    
    class Config:
        arbitrary_types_allowed = True
```

### 4.2 配置管理

#### Config 类设计

```python
from pydantic import BaseModel, Field, field_validator


class TransformerConfig(BaseModel):
    d_model: int = Field(gt=0, description="Model dimension")
    n_heads: int = Field(gt=0, description="Number of attention heads")
    d_ff: int = Field(gt=0, description="Feed-forward dimension")
    num_layers: int = Field(gt=0, description="Number of layers")
    dropout: float = Field(ge=0, le=1, description="Dropout rate")
    vocab_size: int = Field(gt=0, description="Vocabulary size")
    max_seq_len: int = Field(gt=0, description="Maximum sequence length")
    
    @field_validator('d_model')
    @classmethod
    def d_model_divisible_by_n_heads(cls, v, values):
        n_heads = values.data.get('n_heads')
        if n_heads and v % n_heads != 0:
            raise ValueError(f"d_model {v} must be divisible by n_heads {n_heads}")
        return v
    
    @property
    def head_dim(self) -> int:
        return self.d_model // self.n_heads
```

#### YAML/JSON 配置文件

```yaml
# config.yaml
model:
  type: "bert"
  config:
    d_model: 768
    n_heads: 12
    d_ff: 3072
    num_layers: 12
    dropout: 0.1
    vocab_size: 30522
    max_seq_len: 512

training:
  batch_size: 32
  learning_rate: 2e-5
  epochs: 3
  optimizer: "adamw"
  weight_decay: 0.01

data:
  train_path: "./data/train.csv"
  val_path: "./data/val.csv"
  test_path: "./data/test.csv"

logging:
  experiment_name: "bert-base-finetune"
  log_dir: "./logs"
  checkpoint_dir: "./checkpoints"
```

### 4.3 组件复用

#### 组件注册机制

```python
class ComponentRegistry:
    def __init__(self):
        self.components = {}
    
    def register(self, name, component_class):
        self.components[name] = component_class
    
    def get(self, name):
        return self.components.get(name)


registry = ComponentRegistry()
registry.register("transformer_encoder", TransformerEncoder)
registry.register("residual_block", ResidualBlock)
registry.register("multi_head_attention", MultiHeadAttention)


def build_component(name, **kwargs):
    component_class = registry.get(name)
    if not component_class:
        raise ValueError(f"Component {name} not found in registry")
    return component_class(**kwargs)
```

#### 可组合的构建模式

```python
def build_model(config: dict) -> nn.Module:
    components = []
    
    for layer_config in config.get("layers", []):
        layer_type = layer_config["type"]
        layer_kwargs = layer_config.get("kwargs", {})
        component = build_component(layer_type, **layer_kwargs)
        components.append(component)
    
    return nn.Sequential(*components)


model_config = {
    "layers": [
        {"type": "conv2d", "kwargs": {"in_channels": 3, "out_channels": 64, "kernel_size": 7}},
        {"type": "batch_norm", "kwargs": {}},
        {"type": "relu", "kwargs": {}},
        {"type": "max_pool2d", "kwargs": {"kernel_size": 3}}
    ]
}

model = build_model(model_config)
```

### 4.4 版本控制

#### 模型版本管理

```python
import hashlib
from datetime import datetime


def generate_model_version(config: dict) -> str:
    config_str = str(sorted(config.items()))
    config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"v{timestamp}-{config_hash}"


def save_model_with_version(model: nn.Module, config: dict, base_dir: str = "./models") -> str:
    version = generate_model_version(config)
    save_dir = f"{base_dir}/{version}"
    
    model.save_pretrained(save_dir)
    with open(f"{save_dir}/metadata.json", "w") as f:
        import json
        json.dump({
            "version": version,
            "config": config,
            "created_at": datetime.now().isoformat(),
            "git_commit": get_git_commit()
        }, f, indent=2)
    
    return save_dir


def get_git_commit() -> str:
    import subprocess
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except:
        return "unknown"
```

---

## 5. 代码示例

### 5.1 计算机视觉：图像分类

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride=stride, padding="same")
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = ConvBlock(in_channels, out_channels, stride=stride)
        self.conv2 = ConvBlock(out_channels, out_channels, stride=1)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        residual = self.shortcut(x)
        out = self.conv1(x)
        out = self.conv2(out)
        out += residual
        return F.relu(out)


class ImageClassifier(nn.Module):
    def __init__(self, num_classes=10, config=None):
        super().__init__()
        config = config or {
            "base_channels": 64,
            "num_blocks": [2, 2, 2, 2],
            "num_classes": num_classes
        }
        
        self.in_channels = config["base_channels"]
        
        self.stem = nn.Sequential(
            nn.Conv2d(3, self.in_channels, 7, stride=2, padding=3),
            nn.BatchNorm2d(self.in_channels),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(3, stride=2, padding=1)
        )
        
        self.layer1 = self._make_layer(config["base_channels"], config["num_blocks"][0])
        self.layer2 = self._make_layer(config["base_channels"] * 2, config["num_blocks"][1], stride=2)
        self.layer3 = self._make_layer(config["base_channels"] * 4, config["num_blocks"][2], stride=2)
        self.layer4 = self._make_layer(config["base_channels"] * 8, config["num_blocks"][3], stride=2)
        
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(config["base_channels"] * 8, config["num_classes"])
    
    def _make_layer(self, out_channels, num_blocks, stride=1):
        layers = []
        layers.append(ResidualBlock(self.in_channels, out_channels, stride))
        self.in_channels = out_channels
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock(self.in_channels, out_channels))
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = self.avg_pool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


if __name__ == "__main__":
    model = ImageClassifier(num_classes=10)
    input_tensor = torch.randn(32, 3, 224, 224)
    output = model(input_tensor)
    print(f"Input shape: {input_tensor.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters())}")
```

### 5.2 自然语言处理：文本分类

```python
import torch
import torch.nn as nn


class TextEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model, max_seq_len, dropout=0.1):
        super().__init__()
        self.word_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Parameter(torch.randn(1, max_seq_len, d_model))
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, input_ids):
        seq_len = input_ids.size(1)
        x = self.word_embedding(input_ids) + self.pos_embedding[:, :seq_len, :]
        return self.dropout(x)


class TextClassifier(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.embedding = TextEmbedding(
            vocab_size=config.vocab_size,
            d_model=config.d_model,
            max_seq_len=config.max_seq_len,
            dropout=config.dropout
        )
        
        self.encoder = TransformerEncoder(
            d_model=config.d_model,
            n_heads=config.n_heads,
            d_ff=config.d_ff,
            num_layers=config.num_layers,
            dropout=config.dropout
        )
        
        self.classifier = nn.Linear(config.d_model, config.num_classes)
    
    def forward(self, input_ids, attention_mask=None):
        x = self.embedding(input_ids)
        x = self.encoder(x, attention_mask)
        cls_output = x[:, 0, :]
        return self.classifier(cls_output)


if __name__ == "__main__":
    config = TransformerConfig(
        d_model=512,
        n_heads=8,
        d_ff=2048,
        num_layers=6,
        vocab_size=30522,
        max_seq_len=512,
        dropout=0.1
    )
    config.num_classes = 2
    
    model = TextClassifier(config)
    input_ids = torch.randint(0, 30522, (32, 128))
    attention_mask = torch.ones(32, 128)
    
    output = model(input_ids, attention_mask)
    print(f"Input shape: {input_ids.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters())}")
```

### 5.3 推荐系统：协同过滤

```python
import torch
import torch.nn as nn


class UserEmbedding(nn.Module):
    def __init__(self, num_users, embedding_dim):
        super().__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.init_weights()
    
    def init_weights(self):
        nn.init.normal_(self.user_embedding.weight, std=0.01)
    
    def forward(self, user_ids):
        return self.user_embedding(user_ids)


class ItemEmbedding(nn.Module):
    def __init__(self, num_items, embedding_dim):
        super().__init__()
        self.item_embedding = nn.Embedding(num_items, embedding_dim)
        self.init_weights()
    
    def init_weights(self):
        nn.init.normal_(self.item_embedding.weight, std=0.01)
    
    def forward(self, item_ids):
        return self.item_embedding(item_ids)


class MFRecommender(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=64):
        super().__init__()
        self.user_embedding = UserEmbedding(num_users, embedding_dim)
        self.item_embedding = ItemEmbedding(num_items, embedding_dim)
        self.user_bias = nn.Embedding(num_users, 1)
        self.item_bias = nn.Embedding(num_items, 1)
        self.global_bias = nn.Parameter(torch.tensor(0.0))
    
    def forward(self, user_ids, item_ids):
        user_embed = self.user_embedding(user_ids)
        item_embed = self.item_embedding(item_ids)
        
        user_bias = self.user_bias(user_ids).squeeze()
        item_bias = self.item_bias(item_ids).squeeze()
        
        dot_product = torch.sum(user_embed * item_embed, dim=1)
        prediction = dot_product + user_bias + item_bias + self.global_bias
        
        return prediction


class NeuralCFRecommender(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim=64, hidden_dim=128):
        super().__init__()
        self.user_embedding = UserEmbedding(num_users, embedding_dim)
        self.item_embedding = ItemEmbedding(num_items, embedding_dim)
        
        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, user_ids, item_ids):
        user_embed = self.user_embedding(user_ids)
        item_embed = self.item_embedding(item_ids)
        
        concat = torch.cat([user_embed, item_embed], dim=1)
        prediction = self.mlp(concat).squeeze()
        
        return prediction


if __name__ == "__main__":
    num_users = 10000
    num_items = 5000
    
    mf_model = MFRecommender(num_users, num_items, embedding_dim=64)
    nc_model = NeuralCFRecommender(num_users, num_items, embedding_dim=64)
    
    user_ids = torch.randint(0, num_users, (32,))
    item_ids = torch.randint(0, num_items, (32,))
    
    mf_output = mf_model(user_ids, item_ids)
    nc_output = nc_model(user_ids, item_ids)
    
    print(f"MF output shape: {mf_output.shape}")
    print(f"NC output shape: {nc_output.shape}")
    print(f"MF parameters: {sum(p.numel() for p in mf_model.parameters())}")
    print(f"NC parameters: {sum(p.numel() for p in nc_model.parameters())}")
```

---

## 6. 评估指标

### 6.1 可维护性评估

| 指标 | 定义 | 计算方法 | 合格标准 |
|------|------|---------|---------|
| **代码行数** | 单个组件的代码量 | 统计 `.py` 文件行数 | < 200 行 |
| **圈复杂度** | 代码逻辑复杂度 | 使用 `radon` 工具分析 | < 10 |
| **重复代码率** | 代码重复程度 | 使用 `jscpd` 或 `duplicate-code-detector` | < 5% |
| **文档覆盖率** | 组件文档完整度 | 统计有 docstring 的函数比例 | > 80% |
| **测试覆盖率** | 单元测试覆盖程度 | 使用 `coverage.py` | > 80% |

### 6.2 可扩展性评估

| 指标 | 定义 | 评估方法 | 合格标准 |
|------|------|---------|---------|
| **接口稳定性** | 公共 API 的变更频率 | 统计版本间 API 变更次数 | < 5% 变更率 |
| **组件复用率** | 组件被其他模块引用的次数 | 分析代码库中的 import 关系 | > 3 个引用 |
| **配置灵活性** | 通过配置调整行为的能力 | 评估可配置参数占比 | > 70% 参数可配置 |
| **框架兼容性** | 跨框架使用的难易程度 | 评估迁移到其他框架的工作量 | < 2 天迁移时间 |
| **组合能力** | 组件间组合的自由度 | 评估组件接口的标准化程度 | 任意组件可组合 |

### 6.3 性能影响评估

| 指标 | 定义 | 测量方法 | 参考标准 |
|------|------|---------|---------|
| **推理延迟** | 单次推理的平均耗时 | 使用 `timeit` 或 `py-spy` | 根据业务需求确定 |
| **吞吐量** | 单位时间处理的请求数 | 并发测试测量 | 根据业务需求确定 |
| **内存占用** | 模型加载后的内存使用 | 使用 `torch.cuda.memory_allocated()` | < GPU 显存的 80% |
| **参数数量** | 模型总参数量 | `sum(p.numel() for p in model.parameters())` | 根据部署环境确定 |
| **训练速度** | 每 epoch 的训练时间 | 记录训练日志 | 根据数据集大小确定 |

### 6.4 评估工具链

```python
import time
import torch
from collections import namedtuple

PerformanceMetrics = namedtuple('PerformanceMetrics', [
    'latency_ms',
    'throughput',
    'memory_mb',
    'params_count'
])


def evaluate_model_performance(model, input_shape, device='cuda', iterations=100):
    model.eval()
    model.to(device)
    
    dummy_input = torch.randn(*input_shape, device=device)
    
    with torch.no_grad():
        for _ in range(10):
            model(dummy_input)
    
    start_time = time.time()
    with torch.no_grad():
        for _ in range(iterations):
            model(dummy_input)
    end_time = time.time()
    
    latency_ms = ((end_time - start_time) / iterations) * 1000
    throughput = iterations / (end_time - start_time)
    
    if device == 'cuda':
        memory_mb = torch.cuda.memory_allocated(device) / (1024 ** 2)
    else:
        memory_mb = 0
    
    params_count = sum(p.numel() for p in model.parameters())
    
    return PerformanceMetrics(
        latency_ms=round(latency_ms, 2),
        throughput=round(throughput, 2),
        memory_mb=round(memory_mb, 2),
        params_count=params_count
    )


def evaluate_maintainability(component):
    import inspect
    import radon.complexity as radon
    
    source = inspect.getsource(component)
    lines = source.count('\n')
    
    try:
        complexity = radon.cc_visit(source)[0].complexity
    except:
        complexity = 0
    
    docstrings = sum(1 for name, obj in inspect.getmembers(component) 
                     if inspect.isfunction(obj) and obj.__doc__)
    total_methods = sum(1 for name, obj in inspect.getmembers(component) 
                        if inspect.isfunction(obj))
    doc_coverage = (docstrings / total_methods) * 100 if total_methods > 0 else 0
    
    return {
        'lines_of_code': lines,
        'cyclomatic_complexity': complexity,
        'documentation_coverage': round(doc_coverage, 2)
    }


if __name__ == "__main__":
    model = TransformerEncoder(d_model=512, n_heads=8, d_ff=2048, num_layers=6)
    
    perf_metrics = evaluate_model_performance(model, (32, 128, 512), device='cpu')
    print("Performance Metrics:")
    print(f"  Latency: {perf_metrics.latency_ms} ms")
    print(f"  Throughput: {perf_metrics.throughput} req/s")
    print(f"  Memory: {perf_metrics.memory_mb} MB")
    print(f"  Parameters: {perf_metrics.params_count:,}")
    
    maintainability = evaluate_maintainability(TransformerEncoder)
    print("\nMaintainability Metrics:")
    print(f"  Lines of Code: {maintainability['lines_of_code']}")
    print(f"  Cyclomatic Complexity: {maintainability['cyclomatic_complexity']}")
    print(f"  Documentation Coverage: {maintainability['documentation_coverage']}%")
```

---

## 附录：组件设计检查清单

### 模型层组件检查

- [ ] 组件是否遵循单一职责原则？
- [ ] 组件是否继承自正确的基类（`nn.Module` / `tf.keras.layers.Layer`）？
- [ ] `forward` 方法是否有清晰的输入输出契约？
- [ ] 是否支持 `from_pretrained` / `save_pretrained`？
- [ ] 是否有完整的配置类管理超参数？
- [ ] 是否使用 `nn.ModuleList` / `nn.Parameter` 正确注册子模块和参数？

### Pipeline 组件检查

- [ ] 是否实现了 `preprocess` / `_forward` / `postprocess` 三个核心方法？
- [ ] 是否处理了设备迁移（CPU/GPU）？
- [ ] 是否使用 `torch.no_grad()` 或 `tf.keras.backend.set_learning_phase(False)`？
- [ ] 是否支持批量输入和动态批大小？
- [ ] 后处理是否返回人类可读的结果？

### 配置管理检查

- [ ] 是否使用 `dataclasses` 或 `pydantic` 定义配置？
- [ ] 是否有参数验证和类型安全？
- [ ] 是否支持从 JSON/YAML 文件加载配置？
- [ ] 是否有默认值和合理的参数范围？
- [ ] 配置是否与模型解耦？

---

**文档版本**: v1.0  
**生成日期**: 2026-07-04  
**参考来源**: 
- `ai-agent-atomic-design-analysis.md`
- `deep-learning-atomic-components.md`