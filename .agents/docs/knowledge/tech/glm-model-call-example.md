---
id: glm-model-call-example
title: GLM 大模型调用可复用示例（本地加载 + API 调用）
category: tech
tags: ["glm", "llm", "transformers", "zai", "huggingface", "python"]
date: "2026-08-07"
last_updated: "2026-08-07"
status: active
author: flexloop 沉淀
summary: 从 chaos/flexloop/models 沉淀的 GLM 大模型调用可复用示例：本地模型加载（transformers + torch）与 Z.AI 云端 API 调用（zai-sdk）两种方式，含脱敏代码与环境变量配置说明。
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: "0"
integrity: "unchecked"
---

# GLM 大模型调用可复用示例

> 一句话摘要：沉淀自 `chaos/flexloop/models`，提供 GLM 大模型两种调用方式的可复用示例——本地模型加载与 Z.AI 云端 API 调用，全部代码已脱敏。

---

## 1. 概述

本条目沉淀自 `d:\spaces\chaos\flexloop\models\`（`main.py` 与 `main.ipynb`），涵盖 GLM 系列大模型的两类调用方式：

1. **本地模型加载**：使用 `transformers` + `torch` 加载本地 GLM 权重，支持单轮/多轮/流式对话。
2. **云端 API 调用**：使用 `zai-sdk`（Z.AI）通过 OpenAI 兼容接口调用 `glm-5.1`。

两种方式均通过 `python-dotenv` 加载环境变量，密钥从 `.env` 读取，**示例中不含任何真实密钥或个人路径**。

### 依赖安装

```python
# 本地模型方式
# !pip install transformers torch python-dotenv

# API 调用方式
# !pip install zai-sdk
```

---

## 2. 环境变量加载（两种方式共用）

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Hugging Face Token（本地模型联网/鉴权用）
HF_TOKEN = os.getenv('HF_TOKEN')
if HF_TOKEN:
    print("Using Hugging Face token for authenticated requests")
    os.environ['HF_TOKEN'] = HF_TOKEN
```

> 环境变量的字段结构与脱敏模板详见《model-env-template》。

---

## 3. 本地模型加载方式

### 3.1 加载模型与分词器

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 模型路径（脱敏：使用占位符）
model_path = "<MODEL_PATH>"

print("正在加载模型和分词器...")
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="auto"
)
print("模型加载完成！")
```

关键参数说明：

| 参数 | 说明 |
|------|------|
| `trust_remote_code=True` | 允许加载模型自定义代码（GLM 等国产模型常见） |
| `torch_dtype=torch.float16` | 以半精度加载，节省显存 |
| `device_map="auto"` | 自动分派到可用设备（CPU/GPU） |

### 3.2 基本对话函数（支持多轮）

```python
def chat_with_model(prompt, history=None):
    if history is None:
        history = []

    # 构建对话历史
    messages = []
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    messages.append({"role": "user", "content": prompt})

    # 生成响应
    input_ids = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True
    ).to(model.device)

    # 生成输出
    output_ids = model.generate(
        input_ids,
        max_new_tokens=1024,
        temperature=0.7,
        top_p=0.95,
        repetition_penalty=1.1
    )

    # 解码输出
    response = tokenizer.decode(
        output_ids[0][input_ids.shape[1]:],
        skip_special_tokens=True
    )
    return response
```

**多轮对话用法**：

```python
history = []
response = chat_with_model("第一轮问题", history)
history.append(("第一轮问题", response))

response = chat_with_model("第二轮问题", history)
history.append(("第二轮问题", response))
```

### 3.3 流式对话示例

```python
def stream_chat_with_model(prompt):
    messages = [{"role": "user", "content": prompt}]

    input_ids = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True
    ).to(model.device)

    print("AI: ", end="")
    for output in model.stream_generate(
        input_ids,
        max_new_tokens=1024,
        temperature=0.7,
        top_p=0.95,
        repetition_penalty=1.1
    ):
        token = tokenizer.decode(output[-1:], skip_special_tokens=True)
        print(token, end="", flush=True)
    print()

stream_chat_with_model("Tell a short story about AI.")
```

---

## 4. 云端 API 调用方式（Z.AI）

使用 `zai-sdk`，通过 OpenAI 兼容的 `/v1/chat/completions` 接口调用云端 GLM 模型。

```python
from zai import ZaiClient
import os

# 初始化客户端（从环境变量读取 API Key）
client = ZaiClient(api_key=os.getenv("ZAI_API_KEY"))

# 创建对话补全请求
response = client.chat.completions.create(
    model="glm-5.1",
    messages=[
        {"role": "user", "content": "Hello, please introduce yourself, Z.ai!"}
    ]
)
print(response.choices[0].message.content)
```

要点：

- API Key 通过 `os.getenv("ZAI_API_KEY")` 读取，**不要硬编码在源码中**。
- `model` 参数指定云端模型名（如 `glm-5.1`）。
- 响应结构遵循 OpenAI 兼容格式（`choices[0].message.content`）。

---

## 5. 环境变量配置说明

| 变量名 | 用途 | 说明 |
|--------|------|------|
| `HF_TOKEN` | Hugging Face 访问令牌 | 本地模型联网下载或鉴权时使用，可选 |
| `ZAI_API_KEY` | Z.AI 云端 API 密钥 | API 调用方式必需 |

> 所有密钥值一律使用占位符，严禁在文档/仓库中写入真实密钥。详细脱敏模板见《model-env-template》。

---

## 6. 复用要点

- 两种方式（本地 / API）可按资源与场景选择：本地适合离线与隐私场景，API 适合快速接入与云端弹性。
- 多轮对话通过维护 `history` 元组列表实现，注意每次追加 `(user_msg, assistant_msg)`。
- 生成参数（`max_new_tokens`、`temperature`、`top_p`、`repetition_penalty`）可按需调整。

---

## 7. 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-08-07 | 初始沉淀：从 chaos/flexloop/models 萃取本地加载 + API 调用两种 GLM 调用示例，全部密钥与路径脱敏 |
