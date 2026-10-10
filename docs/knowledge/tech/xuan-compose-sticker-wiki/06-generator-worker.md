---
type: Reference
id: "xuan-compose-sticker-06-generator-worker"
title: "生图服务实战：把 Seedream 5.0 Pro 装进容器"
tags: ["xuan-compose", "seedream", "dockerfile", "fastapi", "i2i", "提示词"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: examples/generator/*；火山方舟 Seedream 5.0 pro 官方文档(docs.volcengine.com/82379/2582774)；skills: seedream-50、travel-memory-card-duo"
summary: "构建 generator 镜像：用环境变量外置端点/模型/密钥，用经官方文档核实的 images/generations 请求完成记忆卡与色幕贴纸稿两次 I2I 生成；提示词按 seedream-50 方法论与 travel-memory-card-duo 规范落地为模板文件；同一镜像兼顾长驻 API 与一次性 CLI。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 生图服务实战：把 Seedream 5.0 Pro 装进容器

## 接口事实（已按官方文档核实）

火山方舟提供 OpenAI 兼容的图像生成接口，本教程只依赖以下核实过的字段：

- 请求：`POST {ARK_BASE_URL}/images/generations`，默认基址 `https://ark.cn-beijing.volces.com/api/v3`，头 `Authorization: Bearer $ARK_API_KEY`；
- 模型 ID：`doubao-seedream-5-0-pro-260628`（5.0 Pro）；
- 请求体：`model`、`prompt`、`size`、`output_format`（`png`/`jpeg`）、`response_format`（`url`/`b64_json`）、图生图参考图 `image`（URL 或 URL 数组）、`watermark`；
- 3:2 尺寸：1K 档 `1248x832`、2K 档 `1872x1248`；`size` 也接受 `1K/1.5K/2K/auto` 档位；
- 响应：`data[0].url` 或 `data[0].b64_json`。

API Key 在火山方舟控制台「API Key 管理」创建（`https://ark.volcengine.com/region:cn-beijing/apikey`），模型 ID 以控制台「开通管理/模型广场」实际可用版本为准（版本会迭代）。

> Seedream 5.0 Pro 还支持 `background: "transparent"` 直出透明图。本教程**刻意不使用**它：`travel-memory-card-duo` 规范要求六枚贴纸与记忆卡严格同版（同形状、同色、同模切边），先出**色幕稿**再本地去底，能把"视觉一致性"和"透明通道正确性"分成两个各自可校验的步骤。直出透明可作为你日后省步骤的备选，但要自行承担贴纸与卡面不一致的风险。

## 镜像：一个镜像，两种形态

[examples/generator/Dockerfile](examples/generator/Dockerfile) 基于 `python:3.12-slim`，先 `COPY requirements.txt` 再装依赖（利用层缓存），业务代码只有一个 [generate.py](examples/generator/generate.py)：

- 默认 `CMD` 是 `uvicorn generate:app` —— 长驻 API（`up` 形态）；
- `xuan-compose run --rm --entrypoint python generator generate.py ...` —— 一次性 CLI 形态。

**端点、模型、密钥全部来自环境变量/secret**（见 [04 章](04-volumes-secrets.md)），镜像本身与供应商解耦，换区域、换账号、换模型版本都不用重新构建。

## 两次 I2I：先卡后贴纸，卡是视觉母版

技能规范要求贴纸稿以**完成的记忆卡为视觉母版**，所以流水线顺序固定（`generate.py::pipeline`）：

1. **照片 → 记忆卡**：以输入照片为参考图，用 [prompts/card.txt](examples/prompts/card.txt) 生成 `card.png`；
2. **记忆卡 → 色幕贴纸稿**：以刚生成的 `card.png` 为参考图，用 [prompts/stickers.txt](examples/prompts/stickers.txt)（内含 `{CHROMA_KEY}` 占位）生成 `stickers-chroma.png`；
3. 色幕稿交给 [07 章](07-chroma-key-task.md)的 `keychroma` 任务抠成 `stickers.png`。

## 提示词方法论如何落进模板

`seedream-50` 技能的 I2I 方法要求按"编辑目标 + 保留项 + 编辑项 + 空间线性描述"组织，并显式写清风格、材质、光影、构图层级。两个模板文件就是该方法的成品：

- [card.txt](examples/prompts/card.txt) 固化了 `travel-memory-card-duo` 的硬约束：3:2 暖纸张、连续 4–5% 外边距、左侧 66–68% 无框水粉插画、其下**恰好**三个英文关键词（`{KW1} · {KW2} · {KW3}`，居中点号分隔）、右侧 30–32% **恰好六枚**模切贴纸（主体局部/成组变体/环境形态/结构局部/功能物件/氛围尺度各一）、粗砺不规则暖白切边、平涂阴影无渐变、无标题水印；
- [stickers.txt](examples/prompts/stickers.txt) 要求**同六枚贴纸**（不得重设计/增删/合并）、两行松散排布、完全可见不裁切，并以最严格措辞要求背景为**绝对均匀的 `{CHROMA_KEY}` 纯色幕**（无渐变/纹理/阴影/反光，贴纸内部也不得出现幕布色）——这是去底成败的前提。

关键词要像 `Crater Smoke / Blue Summit / Quiet Ridge` 这样**具体、场景派生**，不要用 `Travel / Beautiful` 这类泛词；色幕普通场景用 `#00ff00`，绿植丰盛场景换 `#ff00ff`（避免幕布色与图案色重合）。

> 在豆包助手环境里，Seedream 5.0 Pro 的标准路径是经 `seedream-50 → doubao-creative-design` 技能调用生图工具，`model_version=seedream_5.0_pro` 是**工具参数**而非提示词的一部分；本教程容器走的是你自己的方舟 API，对应的是模型 ID 字符串。两者方法论相同、接入面不同，不要把工具参数写进 HTTP 请求体。

## 调用方式

一次性批处理（最贴合本案例）：

```bash
xuan-compose run --rm --entrypoint python generator \
  generate.py pipeline photos/in.jpg "Crater Smoke" "Blue Summit" "Quiet Ridge"
# → /work/out/card.png 与 /work/out/stickers-chroma.png（即宿主 ./out）
```

长驻 API 形态：

```bash
xuan-compose up -d generator
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/generate -H 'Content-Type: application/json' \
  -d '{"mode":"pipeline","photo_path":"/work/photos/in.jpg",
       "keywords":["Crater Smoke","Blue Summit","Quiet Ridge"]}'
```

唯一需要按供应商适配的点：官方示例的 `image` 传可访问 URL；脚本对容器内本地文件改用 **data URI** 上传（见 `generate.py::to_image_ref`）。若你的端点只接受 URL，就把输入图先放到对象存储或 `gallery` 能访问到的位置，改传 `image_url`。
