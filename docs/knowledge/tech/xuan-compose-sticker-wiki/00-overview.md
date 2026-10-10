---
type: Reference
id: "xuan-compose-sticker-00-overview"
title: "教程总览：用 xuan-compose 编排手帐贴纸风格照片生成"
tags: ["xuan-compose", "podman", "compose", "容器编排", "seedream", "手帐贴纸"]
date: "2026-10-09"
last_verified: "2026-10-09"
status: "stable"
category: "tech"
author: "SpecWeave Agent"
source: "derived: projects/xuanspace/libs/xuan-compose 源码(v0.1.0 / 1.6.0+xuan.1)逐文件阅读；skills: travel-memory-card-duo、seedream-50；火山方舟 Seedream 5.0 pro 官方文档 docs.volcengine.com/82379/2582774"
summary: "以『一张照片→手帐记忆卡+透明底贴纸双产物』为实战案例，系统讲解 xuan-compose（podman-compose 翻译重构的 Compose 规范编排引擎）的安装、compose 文件、卷与 secret、服务生命周期、一次性任务与库 API。"
---

> 📚 **教程导航**：[总览](00-overview.md) | [流水线与架构](01-pipeline-architecture.md) | [安装与文件发现](02-install-discovery.md) | [compose.yaml 逐段精讲](03-compose-walkthrough.md) | [卷与密钥](04-volumes-secrets.md) | [生命周期与一次性任务](05-lifecycle-tasks.md) | [生图服务实战](06-generator-worker.md) | [色幕去底任务](07-chroma-key-task.md) | [库 API 与预演](08-library-api.md) | [避坑与 FAQ](09-pitfalls-faq.md) | [模式与验收清单](10-pattern-checklist.md)

# 教程总览

## 这篇教程教什么

把一条**AI 创意生产流水线**用 [xuan-compose](../../../../projects/xuanspace/libs/xuan-compose/README.md) 声明式地编排起来，并在这个过程中讲透 Compose 规范编排引擎的核心能力。案例产物来自「手帐贴纸风格照片生成」工作流：输入**一张**旅行/街景/生活照片，得到两份配套位图——

1. **一张 3:2 横版完整旅行记忆卡**（`card.png`）：左侧约 66% 是水粉/剪纸质感的无框插画与一行三个英文关键词，右侧约 32% 是六枚带暖白模切边的贴纸；
2. **一张 3:2 透明底贴纸 PNG**（`stickers.png`）：与记忆卡上**完全相同的六枚贴纸**，RGBA、四角全透明，可直接复用。

第二步的透明底不是模型直接"画"出来的，而是先生成一张**均匀色幕贴纸稿**（`stickers-chroma.png`），再由一个**确定性的本地去底任务**抠除色幕。这恰好构成容器编排里最经典的两类工作负载：**可复现的确定性任务**与**需要外部能力的服务**。

## 三个知识来源

| 来源 | 提供什么 |
|------|---------|
| [xuan-compose](../../../../projects/xuanspace/libs/xuan-compose/README.md)（本教程主角） | Compose 规范声明式容器编排引擎；由 containers/podman-compose v1.6.0 逐行翻译式分层重构，CLI/解析行为与上游对等 |
| 技能 `travel-memory-card-duo` | 双产物的**领域工作流规范**：六贴纸 motif 选择、三关键词、水粉/剪纸艺术方向、色幕策略（`#ff00ff` 用于绿植多场景、`#00ff00` 其他）、RGBA 校验 |
| 技能 `seedream-50` | Seedream 5.0 Pro 的**提示词组装方法论**（T2I/I2I 模板、构图决策、美学系统）；实际请求走火山方舟 OpenAI 兼容的 `images/generations` |

> xuan-compose 与"图像合成"无关——它是**容器编排引擎**（podman-compose 的重构版）。图像生成只是本教程选中的、足够具体的实战载体。上游概念可对照 OKF 知识包 [podman-compose：Docker Compose 规范的 Podman 实现](../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/index.md)。

## 目标读者与前置

- 会读基本 YAML、用过命令行；**不需要**事先懂 Compose 规范或 Podman。
- 本机装有 [Podman](https://podman.io/)（Linux/macOS，或 Windows 上的 WSL2 —— xuan-compose 的权威测试环境即 WSL + Python 3.14）。
- 想跟跑生图环节需要一个火山方舟 `ARK_API_KEY`；**只学编排**则可全程用 `config` / `--dry-run`，不产生任何调用费用。

## 你将学到的 xuan-compose 能力

| 能力点 | 对应章节 |
|--------|---------|
| 安装、console script 与 `python -m` 入口、compose 文件发现规则 | [02](02-install-discovery.md) |
| `services` / `build` / `environment` / 变量插值 / `.env` / `config` 校验 | [03](03-compose-walkthrough.md) |
| bind 挂载 vs 命名卷、文件 secret 与环境 secret、网络、profiles | [04](04-volumes-secrets.md) |
| `depends_on` 条件映射、健康检查、`up/down` 重建对账、`run --rm` 一次性任务 | [05](05-lifecycle-tasks.md) |
| 多阶段镜像、长驻 API 与一次性 CLI 双形态、供应商无关配置 | [06](06-generator-worker.md) |
| 色幕去底容器化、退出码透传、产物校验 | [07](07-chroma-key-task.md) |
| **库 API**：零副作用 import、`ComposeEngine`、纯解析、无 Podman 静态验证 | [08](08-library-api.md) |
| 上游保留怪癖、Windows/WSL 差异、GPL 许可、常见报错 | [09](09-pitfalls-faq.md) |
| 可迁移模式、反模式、端到端验收清单 | [10](10-pattern-checklist.md) |

## 全局流水线

```{mermaid}
flowchart LR
    A["输入照片<br/>photos/in.jpg"] --> B["generator 服务<br/>Seedream 5.0 Pro"]
    B --> C["card.png<br/>完整记忆卡"]
    C --> B
    B --> D["stickers-chroma.png<br/>均匀色幕贴纸稿"]
    D --> E["keychroma 一次性任务<br/>Pillow/numpy 去底"]
    E --> F["stickers.png<br/>RGBA 透明底"]
    C -. "只读挂载" .-> G["gallery 画廊<br/>profile=web"]
    F -. "只读挂载" .-> G
```

## 工作假设（先读这段，避免误解）

1. **编排是主角，API 客户端不是**：生图脚本只演示与编排相关的部分（密钥、挂载、双形态、退出码），请求字段以火山方舟官方文档为准，端点/模型/密钥全部走环境变量，不焊死供应商。
2. **确定性环节本地做**：去底、RGBA 校验是纯本地、可重复、零费用的，放进一次性容器；需要模型判断的生图环节才调用外部 API。
3. **示例面向 Podman**：xuan-compose 翻译出的是 `podman` 命令；它刻意保持与 podman-compose v1.6.0 的行为对等，包括若干"上游怪癖"（见 [09](09-pitfalls-faq.md)）。

配套的完整可运行工程在 [examples/](examples/README.md)，本教程所有代码片段都能在其中找到出处。
