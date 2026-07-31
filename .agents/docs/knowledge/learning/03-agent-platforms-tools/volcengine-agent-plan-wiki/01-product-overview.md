---
id: "volcengine-agent-plan-wiki-01"
title: "产品详解：什么是Agent Plan"
source: "https://bytedance.larkoffice.com/wiki/W5eJwfn5biMffOkGP00coVAAnDe"
date: "2026-07-31"
category: "learning"
tags: ["volcengine", "agent-plan", "方舟", "订阅产品", "API Key"]
---
# 产品详解：什么是Agent Plan

## 一、产品定位

Agent Plan是火山引擎方舟面向Agent时代推出的**全新订阅产品**。它的核心理念是：

> **一个订阅套餐、一个API Key，覆盖主流编程模型、生图生视频模型、向量化模型、联网搜索，更多能力持续更新中。**

在Agent应用从单模态向跨模态演进的趋势下，开发者不再需要分别开通、管理、计费多个模型服务，通过Agent Plan即可一站式获取构建跨模态Agent所需的全部核心能力。

## 二、订阅模式特点

### 2.1 传统模式 vs Agent Plan模式

```mermaid
flowchart LR
    subgraph TRADITIONAL["传统接入模式"]
        direction TB
        K1["Key 1<br/>编程模型"]
        K2["Key 2<br/>语言模型"]
        K3["Key 3<br/>生图模型"]
        K4["Key 4<br/>生视频模型"]
        K5["Key 5<br/>向量化"]
        B1["分别计费<br/>5份账单"]
        K1 & K2 & K3 & K4 & K5 --> B1
    end
    subgraph AGENTPLAN["Agent Plan模式"]
        direction TB
        KEY["🔑 一个API Key"]
        SUB["📦 一个订阅套餐"]
        ALL["覆盖全部能力<br/>编程/语言/生图/生视频/向量化/搜索"]
        KEY --> SUB --> ALL
    end
    classDef traditional fill:#FF8787,stroke:#C92A2A,color:#fff
    classDef plan fill:#69DB7C,stroke:#2F9E44,color:#fff
    classDef key fill:#FFD43B,stroke:#F08C00,color:#000
    class K1,K2,K3,K4,K5,B1 traditional
    class SUB,ALL plan
    class KEY key
```

### 2.2 核心优势对比

| 对比维度 | 传统多服务接入 | Agent Plan订阅 |
|---------|--------------|---------------|
| **API Key数量** | 多个Key，需分别管理 | 1个Key，统一接入 |
| **开通流程** | 逐个服务申请开通 | 一次订阅，全部可用 |
| **计费方式** | 按服务分别计费，多份账单 | 订阅套餐制，简单清晰 |
| **能力更新** | 新服务需单独开通 | 能力持续更新，订阅即享 |
| **集成复杂度** | 多套SDK/API对接 | 统一接口规范 |
| **试用门槛** | 需分别申请试用资格 | 订阅即可开始使用 |

## 三、一个API Key覆盖的能力清单

Agent Plan通过单一API Key为开发者提供以下六大类核心能力：

### 3.1 能力全景表

| 能力类别 | 具体能力 | 典型应用场景 |
|---------|---------|-------------|
| **💻 编程模型** | 主流代码生成模型 | AI编程助手、代码审查、自动化脚本生成 |
| **💬 语言模型** | Doubao-Seed-Evolving等主力模型 | 推理、规划、对话、内容生成、任务分解 |
| **🖼️ 生图模型** | 图像生成模型 | 素材创作、设计稿生成、插画、配图 |
| **🎬 生视频模型** | 视频生成模型 | 短视频生成、动态素材、成片制作 |
| **📊 向量化模型** | Embedding模型 | 知识库检索、RAG、语义相似度计算 |
| **🔍 联网搜索** | Harness联网能力 | 实时信息获取、事实核查、资料检索 |

### 3.2 跨模态协同能力链路

```mermaid
flowchart LR
    subgraph INPUT["用户需求"]
        REQ["🎯 创作目标<br/>例如：制作产品宣传短视频"]
    end
    subgraph LANG["🧠 语言模型层"]
        PLAN["📋 任务规划<br/>脚本撰写"]
        SPLIT["🔀 步骤分解<br/>Prompt生成"]
    end
    subgraph VISION["🎨 视觉生成层"]
        IMG_GEN["🖼️ 生图模型<br/>分镜素材"]
        VID_GEN["🎬 生视频模型<br/>最终成片"]
    end
    subgraph ENGINEERING["⚙️ 工程支撑层"]
        VEC["📊 向量化<br/>知识库检索"]
        SEARCH["🔍 联网搜索<br/>资料补充"]
    end
    OUTPUT["✅ 最终交付物"]
    REQ --> LANG
    LANG --> VISION
    ENGINEERING -.->|"检索增强"| LANG
    ENGINEERING -.->|"参考素材"| VISION
    VISION --> OUTPUT
    classDef input fill:#5C7CFA,stroke:#364FC7,color:#fff
    classDef lang fill:#74C0FC,stroke:#1971C2,color:#fff
    classDef vision fill:#FFA94D,stroke:#E67700,color:#fff
    classDef engineering fill:#69DB7C,stroke:#2F9E44,color:#fff
    classDef output fill:#51CF66,stroke:#2B8A3E,color:#fff
    class REQ input
    class PLAN,SPLIT lang
    class IMG_GEN,VID_GEN vision
    class VEC,SEARCH engineering
    class OUTPUT output
```

**典型跨模态协同流程**（以短视频制作为例）：

1. **语言模型**接收用户需求 → 撰写脚本、生成分镜描述
2. **联网搜索/向量化**检索参考资料、风格案例
3. **生图模型**根据分镜描述生成关键帧素材
4. **生视频模型**基于素材生成最终视频片段
5. **语言模型**进行后期文案、字幕整理

## 四、持续更新承诺

Agent Plan采用"订阅即享更新"模式，官方承诺**更多能力持续更新中**，包括但不限于：

- 新发布的Doubao系列模型
- 升级后的多模态生成能力
- 增强的Harness工程能力
- 社区呼声高的第三方模型接入

订阅用户无需额外申请或付费，即可在能力上线后第一时间使用。

## 五、适合人群

Agent Plan特别适合以下类型的开发者和创作者：

| 用户类型 | 核心诉求 | Agent Plan价值 |
|---------|---------|---------------|
| **Agent开发者** | 快速构建多模态Agent | 一个Key搞定全部模型调用 |
| **全栈创作者** | 一人完成从内容到视觉到动效 | 语言+生图+生视频一站式 |
| **AI编程用户** | Claude Code/OpenCode/Codex等工具接入 | 覆盖主流编程模型 |
| **产品原型团队** | 快速验证跨模态产品想法 | 低门槛开通，开箱即用 |
| **研究者/评测者** | 对比不同模型表现 | 统一接口，方便横向测评 |

---

[🏠 返回总览](00-overview.md) | [➡️ 贡献方向详解](02-contribution-directions.md)
