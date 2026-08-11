---
id: onnx-wiki-readme
title: ONNX Wiki - 入口导航
date: 2026-08-09
tags:
  - onnx
  - wiki
  - navigation
  - index
source:
  - https://onnx.ai
category: knowledge/learning/06-ai-ml-inference
maturity: L1-draft
---

# ONNX Wiki

> 面向工程师的ONNX实用知识库——讲清心智模型，指出生产反模式，提供可运行代码。

## 📋 前置知识要求

阅读本Wiki前你需要：
- ✅ 基础Python编程能力
- ✅ NumPy数组操作基础（理解shape、dtype、矩阵运算）
- ✅ 基本的机器学习/深度学习概念（知道什么是模型、权重、推理）
- ❌ 不需要事先了解ONNX或Protobuf

## 📖 术语快速入门（第一次看先扫一眼）

| 术语 | 一句话解释 |
|------|-----------|
| **ONNX** | 开放神经网络交换格式——机器学习模型的"通用语言"，让不同框架的模型可以互相转换部署 |
| **IR** | Intermediate Representation（中间表示）——ONNX模型本身就是一个计算图IR |
| **opset** | Operator Set Version（算子集版本）——算子行为的"契约版本号"，类似API版本 |
| **Protobuf** | Google的二进制序列化格式——ONNX用它来把模型存成文件，类比class文件之于Java |
| **Initializer** | 初始化器——模型里存的常量数据（如训练好的权重W和偏置b） |
| **算子（Operator）** | ONNX里的基本计算单元（如MatMul矩阵乘、Add加法、Conv卷积） |

**基于**：ONNX 1.23.0 / opset 28 / IR v13

---

## 📚 文档列表

| 编号 | 文档 | 内容 | 阅读时间 |
|------|------|------|----------|
| 00 | [00-overview.md](./00-overview.md) | **总览**：TL;DR快速结论、阅读路径、一页纸速查表、可迁移模式 | 10分钟 |
| 01 | [01-core-concepts.md](./01-core-concepts.md) | **核心概念详解**：11个主题（计算图本质、5大组件、类型系统、opset、控制流等），线性回归贯穿案例 | 30分钟 |
| 02 | [02-python-api.md](./02-python-api.md) | **Python API实战**：4大Helper函数、完整线性回归示例、序列化/校验、Reference Runtime、Initializer可选参数模式 | 40分钟（含动手） |
| 03 | [03-quickstart.md](./03-quickstart.md) | **快速上手**：安装、5分钟Hello World、Netron可视化、PyTorch/TF导出概览 | 15分钟 |
| 04 | [04-best-practices.md](./04-best-practices.md) | **最佳实践与反模式**（🔥**重点**）：6个反模式（每个含问题/后果/正确做法）、opset选择策略、检查清单 | 25分钟 |
| 05 | [05-faq-and-resources.md](./05-faq-and-resources.md) | **FAQ与资源**：12个常见问题、官方/工具/框架资源链接、25个关键术语表 | 15分钟（查阅） |

---

## 🚀 快速开始指引

### 30分钟快速部署路径
> 我只想把PyTorch模型转ONNX部署，不想搞懂底层概念

1. 读 [00-overview.md](./00-overview.md) 的TL;DR部分（2分钟）
2. 读 [03-quickstart.md](./03-quickstart.md)（15分钟）
3. 重点看 [04-best-practices.md](./04-best-practices.md) 的反模式部分（10分钟）
4. 遇到问题查 [05-faq-and-resources.md](./05-faq-and-resources.md)

### 2小时深度理解路径
> 我要手写/修改ONNX图，需要理解API和底层机制

1. 完整读 [00-overview.md](./00-overview.md)
2. [01-core-concepts.md](./01-core-concepts.md) 建立正确心智模型
3. [02-python-api.md](./02-python-api.md) 跟着手敲线性回归示例
4. [04-best-practices.md](./04-best-practices.md) 通读所有反模式
5. [03-quickstart.md](./03-quickstart.md) 看框架导出部分
6. 遇到问题查 [05-faq-and-resources.md](./05-faq-and-resources.md)

---

## ⚠️ 最关键的7条结论（来自I阶段核心洞察）

1. **ONNX是张量计算DSL，不是模型保存格式**——你在写程序，不是存权重
2. **onnx.reference仅用于语义验证/单元测试/教学，禁止用于生产流量**——CI测试可以用，生产用onnxruntime
3. **强类型零隐式转换**——混合类型必须显式Cast，否则直接报错
4. **opset是算子行为契约版本，不是功能开关**——选部署目标支持的版本
5. **Python API是函数式组装+字符串接线**——没有OO的graph.add_node()
6. **控制流分支输出签名必须完全一致**——数量/类型/形状都要相同
7. **Initializer与Input同名时成为可选输入默认值**——原生支持可选参数

---

## 🔗 相关Wiki链接

- **[protobuf-wiki](../../01-agent-protocols-interfaces/protobuf-wiki/README.md)**：ONNX使用Protobuf作为序列化编码，两者都是"IDL/DSL + 二进制编码"范式
- 向上导航：[../../README.md](../../README.md)（学习知识库目录）

---

## 📁 文件结构

```
onnx-wiki/
├── README.md               ← 你在这里：入口导航
├── 00-overview.md          ← 总览
├── 01-core-concepts.md     ← 核心概念详解
├── 02-python-api.md        ← Python API实战
├── 03-quickstart.md        ← 快速上手
├── 04-best-practices.md    ← 最佳实践与反模式（重点）
└── 05-faq-and-resources.md ← FAQ与资源
```

---

## 版本信息

- ONNX版本：1.23.0
- opset版本：28
- IR版本：v13
- 文档版本：L1-draft
- 最后更新：2026-08-09

---

**开始阅读**：[00-overview.md - 总览](./00-overview.md)
