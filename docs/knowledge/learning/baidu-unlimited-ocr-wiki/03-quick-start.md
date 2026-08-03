---
id: baidu-unlimited-ocr-wiki-03-quick-start
title: "百度 Unlimited-OCR 快速上手指南"
source: "https://github.com/baidu/Unlimited-OCR"
date: "2026-08-03"
category: "learning"
tags: ["OCR","快速上手","Transformers","SGLang","vLLM","部署","PyMuPDF","批量推理"]
---

# 百度 Unlimited-OCR 快速上手指南

> 本章基于官方源码README和infer.py脚本整理，提供三种部署方式：Transformers适合快速体验，SGLang适合高性能服务部署，vLLM适合成熟生产环境。PDF需先用PyMuPDF转图片（DPI=300），内置infer.py脚本支持一键批量推理。

---

## 1. 环境要求

| 项目 | 要求 |
|------|------|
| **Python** | 3.12.3（官方测试版本） |
| **CUDA** | 12.9 |
| **GPU** | 必须NVIDIA GPU（bfloat16支持） |
| **操作系统** | Linux推荐（vLLM/SGLang生产环境） |

---

## 2. 图像模式说明

Unlimited-OCR支持两种图像推理模式，针对不同场景优化：

| 模式 | base_size | image_size | crop_mode | ngram_window | 适用场景 |
|------|-----------|------------|-----------|--------------|---------|
| **gundam** | 1024 | 640 | ✅ 开启（裁剪） | 128 | 单张图片高精度识别 |
| **base** | 1024 | 1024 | ❌ 关闭 | 1024 | 多页PDF/长文档解析 |

> **选择原则**：单张图片用gundam（裁剪后聚焦核心区域，精度更高）；多页PDF或批量处理必须用base（不裁剪保证整页信息完整，长ngram_window保证跨页连贯性）。

---

## 3. 通用前置处理

Unlimited-OCR当前不支持直接输入PDF文件，无论使用哪种推理方式，都需要先将PDF转换为图片。

### 3.1 PDF转图片标准代码

```python
import os
import tempfile
import fitz  # PyMuPDF

def pdf_to_images(pdf_path, dpi=300):
    """将PDF逐页转换为PNG图片，返回图片路径列表"""
    doc = fitz.open(pdf_path)
    tmp_dir = tempfile.mkdtemp(prefix='pdf_ocr_')
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    paths = []
    for i, page in enumerate(doc):
        out = os.path.join(tmp_dir, f'page_{i+1:04d}.png')
        page.get_pixmap(matrix=mat).save(out)
        paths.append(out)
    doc.close()
    return paths
```

### 3.2 为什么需要转图片

- 模型视觉编码器DeepEncoder接收的输入是图像格式，而非原生PDF
- DPI=300是平衡识别精度和处理速度的推荐值（源码默认值）
- base模式下1024×1024分辨率与DeepEncoder训练时的输入规格匹配

---

## 4. Transformers方式（快速上手）

Transformers方式是最简单的上手路径，适合快速体验模型效果、开发调试和小批量文档处理。

### 4.1 适用场景

| 场景 | 说明 |
|------|------|
| **快速体验** | 第一次接触Unlimited-OCR，想马上看到效果 |
| **小批量处理** | 处理几份到几十份文档，不需要高并发 |
| **开发调试** | 集成到Python项目中，进行功能开发和调试 |
| **个人学习** | 学习研究模型原理，修改代码做实验 |

### 4.2 依赖安装

官方测试精确版本：

```bash
pip install torch==2.10.0 torchvision==0.25.0
pip install transformers==4.57.1
pip install Pillow==12.1.1 matplotlib==3.10.8
pip install einops==0.8.2 addict==2.4.0 easydict==1.13
pip install pymupdf==1.27.2.2 psutil==7.2.2
```

### 4.3 单图推理（gundam模式）

```python
import torch
from transformers import AutoModel, AutoTokenizer

model_name = 'baidu/Unlimited-OCR'

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    use_safetensors=True,
    torch_dtype=torch.bfloat16,
)
model = model.eval().cuda()

# 单图：gundam模式（image_size=640, crop_mode=True）
model.infer(
    tokenizer,
    prompt='<image>document parsing.',
    image_file='your_image.jpg',
    output_path='your/output/dir',
    base_size=1024, image_size=640, crop_mode=True,
    max_length=32768,
    no_repeat_ngram_size=35, ngram_window=128,
    save_results=True,
)
```

### 4.4 多页PDF推理（base模式）

```python
# 多页/PDF：base模式（image_size=1024, crop_mode=False, ngram_window=1024）
image_paths = pdf_to_images('your_doc.pdf', dpi=300)

model.infer_multi(
    tokenizer,
    prompt='<image>Multi page parsing.',
    image_files=image_paths,
    output_path='your/output/dir',
    image_size=1024,
    max_length=32768,
    no_repeat_ngram_size=35, ngram_window=1024,
    save_results=True,
)
```

---

## 5. SGLang方式（高性能服务部署）

SGLang方式提供高性能推理服务，适合需要高吞吐、流式输出的服务化部署场景。

### 5.1 适用场景

| 场景 | 说明 |
|------|------|
| **大批量文档处理** | 处理成百上千份文档，需要高吞吐量 |
| **服务化部署** | 作为后端HTTP服务提供OCR能力 |
| **高并发请求** | 同时响应多个用户的OCR请求 |
| **流式输出需求** | 需要实时展示识别进度的场景 |

### 5.2 环境准备

官方推荐使用uv管理虚拟环境，需要安装项目自带的定制SGLang wheel：

```bash
uv venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装项目附带的定制SGLang wheel
uv pip install wheel/sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl
uv pip install kernels==0.11.7
uv pip install pymupdf==1.27.2.2 requests
```

> wheel文件位于Unlimited-OCR项目的`wheel/`目录下。

### 5.3 启动SGLang服务（完整参数）

```bash
python -m sglang.launch_server \
    --model baidu/Unlimited-OCR \
    --served-model-name Unlimited-OCR \
    --attention-backend fa3 \
    --page-size 1 \
    --mem-fraction-static 0.8 \
    --context-length 32768 \
    --enable-custom-logit-processor \
    --disable-overlap-schedule \
    --skip-server-warmup \
    --host 0.0.0.0 \
    --port 10000
```

关键参数说明：
- `--attention-backend fa3`：使用FlashAttention-3后端
- `--page-size 1`：单页KV cache分配
- `--mem-fraction-static 0.8`：预分配80%显存
- `--context-length 32768`：最大上下文32768 token
- `--enable-custom-logit-processor`：启用去重logit处理器（必须）
- `--port 10000`：默认端口**10000**

服务启动后可通过 `http://127.0.0.1:10000/health` 检查健康状态。

### 5.4 客户端调用示例

```python
import base64
import json
import requests
from sglang.srt.sampling.custom_logit_processor import DeepseekOCRNoRepeatNGramLogitProcessor

server_url = "http://127.0.0.1:10000"

def encode_image(image_path):
    import os
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext.lstrip('.')}"
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}}

def build_content(prompt, image_paths):
    return [{"type": "text", "text": prompt}] + [encode_image(p) for p in image_paths]

def generate(prompt, image_paths, image_mode, ngram_window):
    payload = {
        "model": "Unlimited-OCR",
        "messages": [{"role": "user", "content": build_content(prompt, image_paths)}],
        "temperature": 0,
        "skip_special_tokens": False,
        "images_config": {"image_mode": image_mode},
        "custom_logit_processor": DeepseekOCRNoRepeatNGramLogitProcessor.to_str(),
        "custom_params": {"ngram_size": 35, "window_size": ngram_window},
        "stream": True,
    }
    response = requests.post(
        f"{server_url}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload), timeout=1200, stream=True,
    )
    for line in response.iter_lines(chunk_size=1, decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        data = line[len("data: "):]
        if data == "[DONE]":
            break
        event = json.loads(data)
        delta = event["choices"][0].get("delta", {}).get("content", "")
        if delta:
            print(delta, end="", flush=True)

# 单图（gundam模式，ngram_window=128）
generate("document parsing.", ["your_image.jpg"], image_mode="gundam", ngram_window=128)

# 多页PDF（base模式，ngram_window=1024）
generate("Multi page parsing.", pdf_to_images("your_doc.pdf", dpi=300), image_mode="base", ngram_window=1024)
```

---

## 6. vLLM方式（生产级部署）

vLLM是更成熟的推理引擎，官方已提供官方支持，适合大规模生产环境。

### 6.1 适用场景

| 场景 | 说明 |
|------|------|
| **大规模生产部署** | 已有vLLM基础设施的团队 |
| **Docker化部署** | 容器化部署、K8s编排 |
| **高并发服务** | 需要vLLM成熟的调度和批处理能力 |

### 6.2 Docker镜像

根据GPU平台选择对应镜像：

**默认（CUDA 13.0）：**
```bash
docker pull vllm/vllm-openai:unlimited-ocr
```

**Hopper架构GPU（H100等，CUDA 12.9）：**
```bash
docker pull vllm/vllm-openai:unlimited-ocr-cu129
```

### 6.3 官方Recipe

详细部署指南请参考官方vLLM recipe：
> **Recipe**: https://recipes.vllm.ai/baidu/Unlimited-OCR

---

## 7. infer.py批量推理脚本

项目内置`infer.py`脚本，可一键启动SGLang服务器并并发处理图片目录或PDF文件，无需手动管理服务生命周期。

### 7.1 功能特性

- ✅ 自动启动/停止SGLang服务器（复用已有服务）
- ✅ 支持图片目录批量处理（递归扫描）
- ✅ 支持PDF文件自动转图片逐页处理
- ✅ 多线程并发请求（默认8并发）
- ✅ 失败自动重试（最多5次，502错误指数退避）
- ✅ 大文件优先调度（按文件大小降序，优化GPU利用率）
- ✅ TPS统计和性能报告
- ✅ 结果保存为Markdown文件

### 7.2 使用方式

**处理图片目录：**
```bash
python infer.py \
    --image_dir ./examples/images \
    --output_dir ./outputs \
    --concurrency 8 \
    --image_mode gundam
```

**处理PDF文件：**
```bash
python infer.py \
    --pdf ./examples/document.pdf \
    --output_dir ./outputs \
    --concurrency 8 \
    --image_mode base
```

### 7.3 完整参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--image_dir` | "" | 图片目录路径（与--pdf二选一） |
| `--pdf` | "" | PDF文件路径（与--image_dir二选一） |
| `--output_dir` | ./outputs | 输出目录（结果保存为.md文件） |
| `--concurrency` | 8 | 并发请求数 |
| `--gpu` | 0 | CUDA_VISIBLE_DEVICES GPU编号 |
| `--model_dir` | baidu/Unlimited-OCR | 模型路径或HuggingFace ID |
| `--image_mode` | gundam | 图像模式：gundam/base |
| `--server_log` | ./log/sglang_server.log | SGLang服务日志路径 |

### 7.4 输出示例

```
Mode: pdf_pages, requests=15, concurrency=8, image_mode=base
Server ready (42s)
  [1] page_0001.png: 2847 tokens, 3.2s
  [2] page_0002.png: 3156 tokens, 3.5s
  ...
============================================================
Concurrent Results:
  Requests: 15/15
  Total tokens: 45230
  Wall time: 18.52s
  System TPS: 2442.18 tokens/s
  Avg tokens/request: 3015
  Avg decode_time/request: 3.38s
============================================================
```

---

## 8. OmniDocBench评估后处理

在OmniDocBench基准上评估时，需要对模型输出进行后处理，移除`<|det|>`检测标记：

```python
import re

DET_RE = re.compile(r'<\|det\|>([^<\s]+)(?:\s*\[[^\]]*\])?\s*<\|/det\|>(.*)', re.DOTALL)

def remove_det(raw: str) -> str:
    """移除<|det|>标记，同一块内的行用\\n连接，不同块之间用\\n\\n分隔"""
    blocks = []
    cur = None
    for line in raw.splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = DET_RE.match(line)
        if m:
            category, content = m.group(1).strip(), m.group(2).strip()
            if category == 'image':
                continue
            if cur is not None:
                blocks.append(cur)
            cur = [content] if content else []
            continue
        if cur is None:
            cur = []
        cur.append(line)
    if cur is not None:
        blocks.append(cur)
    return '\n\n'.join('\n'.join(b) for b in blocks).strip()
```

---

## 9. 三种方式对比表

| 对比维度 | Transformers方式 | SGLang方式 | vLLM方式 |
|---------|----------------|-----------|---------|
| **定位** | 快速上手/开发调试 | 高性能服务部署 | 成熟生产级部署 |
| **部署复杂度** | 低，pip install后直接运行 | 中，需安装定制wheel+启动服务 | 中，Docker一键部署 |
| **依赖安装** | torch+transformers+10个精确版本包 | 定制SGLang wheel+kernels+pymupdf | Docker镜像（含全部依赖） |
| **API接口** | 原生Python函数调用 | OpenAI-compatible HTTP API | OpenAI-compatible HTTP API |
| **流式输出** | 需自行实现 | 原生支持 | 原生支持 |
| **并发处理** | 单线程/单批次 | 服务端支持高并发 | 成熟批处理调度 |
| **批量推理** | 需自行循环调用 | 客户端需自行实现 | 服务端批处理 |
| **一键批量脚本** | ❌ 无 | ✅ infer.py内置 | ❌ 需自行实现 |
| **生产就绪度** | ⭐ 仅开发调试 | ⭐⭐⭐ 中小规模服务 | ⭐⭐⭐⭐⭐ 大规模生产 |
| **部署成本** | 最低 | 中等 | 最低（Docker） |

---

## 10. 方式选择建议

### 🟢 选Transformers方式如果你：
- 是第一次使用Unlimited-OCR，想快速体验效果
- 只需要处理少量文档（几份到几十份）
- 在开发调试阶段，需要频繁修改代码
- 做个人学习研究或原型验证
- 不想额外安装和配置服务端组件

### 🔵 选SGLang方式如果你：
- 需要部署为HTTP服务供内部系统调用
- 有中等规模批量处理需求（上百份文档）
- 需要使用内置infer.py一键批量推理
- 需要流式输出实时展示结果
- 团队对SGLang栈比较熟悉

### 🟣 选vLLM方式如果你：
- 大规模生产环境部署（K8s/Docker）
- 已有vLLM基础设施和运维经验
- 需要最高并发和最成熟的调度能力
- 追求稳定可靠的生产级服务

### 💡 推荐路径
1. **学习验证阶段**：Transformers方式快速跑通单图示例
2. **批量处理阶段**：使用infer.py（SGLang后端）一键处理目录/PDF
3. **生产上线阶段**：切换到vLLM Docker镜像部署

---

## 章节导航

← 上一章：[性能数据与基准测试](02-performance-data.md)

[下一章：局限性与风险提示](04-limitations-risks.md) →
