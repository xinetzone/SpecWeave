---
id: "task4-usage"
title: "使用方式与代码示例整理"
source: "article-content.md"
date: "2026-07-09"
task: "Task 4"
project: "Baidu Unlimited-OCR"
spec: "spec.md"
---

# 百度 Unlimited-OCR 使用方式与代码示例整理

本文档基于 article-content.md 内容，整理 Unlimited-OCR 的两种推理方式：Transformers快速上手方式和SGLang高性能推理方式，并提供对比表格。

---

## 一、Transformers方式（快速上手）

Transformers方式是最低门槛的使用方式，适合快速体验和小批量处理场景。

### 1. 依赖安装

安装PyTorch、Transformers和PyMuPDF三个依赖包：

```bash
pip install torch transformers pymupdf
```

**原文引用：**
> 用 Transformers，安装好 torch、transformers、PyMuPDF 这几个依赖之后，就可以直接从 Hugging Face 加载模型来运行了。
>
> 先安装依赖：
> pip install torch、transformers、pymupdf

### 2. 单页文档解析流程

从Hugging Face加载baidu/Unlimited-OCR模型，然后对单页文档（图片格式）进行解析。

**原文引用：**
> 加载模型并解析单页文档：
> （代码示例图见原文）
>
> 第一种方法是使用 transformers 快速上手

### 3. PDF多页处理流程

PDF文件不能直接输入模型，需要先用PyMuPDF将PDF的每一页转换为图片，然后再进行批量解析。DPI默认设置为300。

**原文引用：**
> PDF 处理比较麻烦一些：要先用 PyMuPDF 把 PDF 页面转换为图片，然后再进行批量解析。
>
> README 中有完整的示例代码，dpi 默认为 300，已经很清晰了。
>
> PDF 多页处理示例：
> （代码示例图见原文）

处理步骤：
1. 使用PyMuPDF（fitz）打开PDF文件
2. 遍历每一页，将页面渲染为图片（DPI=300）
3. 收集所有页面图片
4. 批量送入模型进行解析

### 4. 模型加载

模型托管在Hugging Face上，模型ID为 `baidu/Unlimited-OCR`，可通过Transformers库直接加载。

**原文引用：**
> 就可以直接从 Hugging Face 加载模型来运行了。

### 5. 适用场景

- 快速体验模型效果
- 小批量文档处理
- 开发调试阶段
- 个人学习和研究

---

## 二、SGLang方式（高性能推理）

SGLang方式适用于大批量处理、生产环境和高并发场景，提供更高的推理效率。

### 1. 服务器启动命令

使用SGLang启动推理服务，指定模型路径和端口：

```bash
python -m sglang.launch_server --model-path baidu/Unlimited-OCR --port 30000
```

**原文引用：**
> 第二种方法是使用SGLang进行高效率的推理
>
> 启动服务器：
> python -m sglang.launch_server --model-path baidu/Unlimited-OCR --port 30000

### 2. OpenAI-compatible API支持

服务器启动后，提供与OpenAI API兼容的接口，可以使用类似OpenAI客户端的方式发送请求，降低集成成本。

**原文引用：**
> 启动服务器之后可以使用OpenAI-compatible API来发送请求
>
> 使用API调用的方式为：
> （代码示例图见原文）

### 3. 流式输出支持

支持流式输出（streaming），可以边生成边返回结果，提升用户体验，适合长文档解析的实时反馈场景。

**原文引用：**
> 并且支持流式输出。

### 4. 适用场景

- 大批量文档处理
- 生产环境部署
- 高并发服务场景
- 需要API接口对外提供服务
- 对推理延迟和吞吐量有较高要求的场景

**原文引用：**
> SGLang方式适用于大批量处理以及高效率推理。

---

## 三、两种方式对比表格

| 对比维度 | Transformers方式 | SGLang方式 |
|---|---|---|
| **定位** | 快速上手 | 高性能推理 |
| **部署复杂度** | 低，直接Python脚本运行 | 中，需启动服务端 |
| **依赖安装** | torch, transformers, pymupdf | sglang（需额外安装） |
| **启动命令** | 直接运行Python脚本 | `python -m sglang.launch_server ...` |
| **API接口** | 原生Python函数调用 | OpenAI-compatible HTTP API |
| **流式输出** | 需自行实现 | 原生支持 |
| **并发处理** | 单线程/单批次 | 服务端支持高并发 |
| **吞吐量** | 较低，适合小批量 | 高，适合大批量 |
| **适用阶段** | 开发调试、快速体验 | 生产部署、大规模应用 |
| **典型用户** | 研究者、个人开发者 | 企业用户、生产环境 |
| **PDF处理** | 需PyMuPDF转图片 | 同样需先转图片（前置处理相同） |

---

## 四、使用流程总结

### 通用前置处理（两种方式都需要）

无论使用哪种推理方式，处理PDF文档都需要遵循相同的前置步骤：

```
PDF文件 → PyMuPDF转图片（DPI=300） → 图片列表 → 模型解析 → 输出结果
```

### 方式选择决策树

1. 如果是第一次尝试、学习或处理少量文档 → 选择 **Transformers方式**
2. 如果是部署服务、处理大量文档或需要对外提供API → 选择 **SGLang方式**

**原文引用：**
> Unlimited-OCR 有两种推理方式：Transformers、SGLang。
>
> 看完这些功能，相信各位已经迫不及待了。
>
> 最低门槛的打开方式其实很简单。
