---
id: baidu-unlimited-ocr-wiki-03-quick-start
title: "百度 Unlimited-OCR 快速上手指南"
source: "https://mp.weixin.qq.com/s/rO2yAeDZYbAoEXc7LqX-dg?from=industrynews&color_scheme=light#rd"
date: "2026-08-03"
category: "learning"
tags: ["OCR","快速上手","Transformers","SGLang","部署","PyMuPDF"]
---

# 百度 Unlimited-OCR 快速上手指南

> 本章提供两种上手方式：Transformers方式适合快速体验和开发调试，SGLang方式适合生产环境高并发部署。PDF需先用PyMuPDF转图片（DPI=300），两种方式覆盖从个人学习到大规模应用的全场景需求。

---

## 1. 通用前置处理

Unlimited-OCR当前不支持直接输入PDF文件，无论使用哪种推理方式，都需要先将PDF转换为图片。

### 1.1 转换流程

```
PDF 文件 → PyMuPDF 转图片（DPI=300） → 图片列表 → 模型解析 → 输出结果
```

### 1.2 为什么需要转图片

- 模型视觉编码器DeepEncoder接收的输入是图像格式，而非原生PDF
- DPI=300是平衡识别精度和处理速度的推荐值
- 单页图片建议分辨率1024×1024，与DeepEncoder训练时的输入规格匹配

---

## 2. Transformers方式（快速上手）

Transformers方式是最简单的上手路径，适合快速体验模型效果、开发调试和小批量文档处理。

### 2.1 适用场景

| 场景 | 说明 |
|------|------|
| **快速体验** | 第一次接触Unlimited-OCR，想马上看到效果 |
| **小批量处理** | 处理几份到几十份文档，不需要高并发 |
| **开发调试** | 集成到Python项目中，进行功能开发和调试 |
| **个人学习** | 学习研究模型原理，修改代码做实验 |

### 2.2 依赖安装

```bash
pip install torch transformers pymupdf
```

### 2.3 使用方式

从Hugging Face加载`baidu/Unlimited-OCR`模型，直接通过Python脚本调用：

1. 先用PyMuPDF将PDF逐页转换为图片（DPI=300）
2. 使用Transformers加载模型和处理器
3. 将图片列表输入模型进行解析
4. 获取结构化OCR输出结果

> 项目GitHub README中提供了完整的可运行示例代码，复制即可运行。

---

## 3. SGLang方式（高性能推理）

SGLang方式提供高性能推理服务，适合生产环境部署和高并发场景。

### 3.1 适用场景

| 场景 | 说明 |
|------|------|
| **大批量文档处理** | 处理成百上千份文档，需要高吞吐量 |
| **生产环境部署** | 作为后端服务提供OCR能力 |
| **高并发服务** | 同时响应多个用户的OCR请求 |
| **流式输出需求** | 需要实时展示识别进度的场景 |

### 3.2 服务启动命令

```bash
python -m sglang.launch_server --model-path baidu/Unlimited-OCR --port 30000
```

### 3.3 核心特性

- **OpenAI-compatible API**：提供与OpenAI API兼容的HTTP接口，便于集成
- **流式输出**：原生支持streaming模式，可实时返回识别结果
- **高并发支持**：服务端优化支持多请求并发处理
- **高性能推理**：基于SGLang推理引擎优化，吞吐量更高

---

## 4. 两种方式对比表

| 对比维度 | Transformers方式 | SGLang方式 |
|---------|----------------|-----------|
| **定位** | 快速上手 | 高性能推理 |
| **部署复杂度** | 低，直接Python脚本运行 | 中，需启动服务端 |
| **依赖安装** | torch, transformers, pymupdf | sglang（需额外安装） |
| **API接口** | 原生Python函数调用 | OpenAI-compatible HTTP API |
| **流式输出** | 需自行实现 | 原生支持 |
| **并发处理** | 单线程/单批次 | 服务端支持高并发 |
| **吞吐量** | 较低，适合小批量 | 高，适合大批量 |
| **适用阶段** | 开发调试、快速体验 | 生产部署、大规模应用 |

---

## 5. 方式选择建议

根据你的具体需求选择合适的方式：

### 🟢 选Transformers方式如果你：
- 是第一次使用Unlimited-OCR，想快速体验效果
- 只需要处理少量文档（几份到几十份）
- 在开发调试阶段，需要频繁修改代码
- 做个人学习研究或原型验证
- 不想额外安装和配置服务端组件

### 🔵 选SGLang方式如果你：
- 需要部署为线上服务供多人使用
- 有大批量文档处理需求（上百份以上）
- 需要支持高并发请求
- 需要流式输出实时展示结果
- 追求最高的推理吞吐量和性能

### 💡 混合使用建议
开发阶段用Transformers快速迭代验证，功能稳定后切换到SGLang部署生产环境，这是最常见的使用路径。

---

## 章节导航

← 上一章：[性能数据与基准测试](02-performance-data.md)

[下一章：局限性与风险提示](04-limitations-risks.md) →
