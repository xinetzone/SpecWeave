---
id: "deepseek-v4-glossary"
title: "10 术语表"
version: "1.0"
source: "API文档 + 官方技术博客 + AI/大模型通用术语"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/07-vendor-product-learning/deepseek/10-glossary.toml"
type: "Wiki Document"
description: "DeepSeek-V4免费方案相关的专业术语解释，帮助初学者理解文档中的技术概念"
tags: ["DeepSeek", "术语表", "Token", "MoE", "API", "上下文", "KV Cache", "峰谷定价"]
category: "learning/07-vendor-product-learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "整理文档中15+个专业术语的中英文对照和通俗解释，包括Token、MoE、上下文窗口、KV Cache、缓存命中、Tool Calls、FIM、MTP、SFT、RLHF等。"
last_verified: "2026-08-19"
---
# 10 术语表

## A

### API（Application Programming Interface，应用程序编程接口）
应用程序之间相互调用的接口。DeepSeek API允许开发者通过编程方式（而非网页界面）调用DeepSeek模型，将AI能力集成到自己的应用中。

### Agent（智能体）
能够自主感知环境、规划任务、调用工具、执行操作并完成目标的AI系统。V4-Pro的核心升级就是原生Agent能力，可以自主完成跨文件代码编辑、多步搜索推理等复杂任务链。

## C

### Cache Hit（缓存命中）
当API请求的前缀部分（如system prompt、RAG上下文）与之前请求相同时，系统直接使用之前缓存的KV Cache计算结果，无需重新计算，成本降低97-98%。参见"KV Cache"。

### Chat Completions API
DeepSeek提供的对话式API接口，兼容OpenAI格式，是最常用的API调用方式。通过传入messages数组（包含system/user/assistant角色的消息）获取模型回复。

### Concurrency（并发限制）
同一时间允许的最大API请求数量。V4-Pro默认500并发，V4-Flash默认2500并发。超出并发限制会返回HTTP 429错误。

### Context Window / Context Length（上下文窗口/上下文长度）
模型在一次交互中能够处理的最大token数量，包括输入和输出。V4系列支持100万tokens的超长上下文。

## F

### Fair-Use（公平使用策略）
服务提供商为保障整体服务稳定性而对过度使用行为进行软限制的策略。DeepSeek网页端的"重新生成"次数限制就是一种fair-use措施，区别于硬性配额限制。

### FIM（Fill-in-the-Middle，中间填充）
代码补全的一种模式，给定前缀和后缀，让模型填充中间的代码。常用于IDE实时代码补全场景。

### Fine-tuning（微调）
在预训练模型基础上，使用特定领域数据进一步训练，使模型适应特定任务的过程。V4-Flash开源后用户可以自行微调。

### FP8 / BF16（浮点精度格式）
模型权重和计算使用的数值精度。BF16（16位脑浮点）精度高但显存占用大；FP8（8位浮点）显存占用减半，精度损失极小，是推理部署推荐的格式。

### Function Calling / Tool Calls（函数调用/工具调用）
模型在对话中识别需要调用外部工具的时机，生成结构化的工具调用指令，由执行端调用工具后将结果返回给模型继续推理。V4系列原生支持此能力。

## K

### KV Cache（Key-Value Cache，键值缓存）
Transformer模型推理时缓存之前计算过的Key和Value矩阵，避免每次生成新token时重新计算全部前文的注意力机制，是长上下文推理的核心优化技术。V4的CSA+HCA技术大幅压缩了KV Cache的显存占用。

## M

### MTP（Multi-Token Prediction，多Token预测）
DeepSeek V4引入的推理加速技术，模型在一次前向传播中同时预测多个后续token，可提升推理速度约30-80%。

### MoE（Mixture of Experts，混合专家模型）
一种模型架构，将模型分为多个"专家"子网络，每次推理只激活部分专家。V4-Pro总参数1.6T但仅激活49B，V4-Flash总参数284B但仅激活13B，用较少的计算成本获得大模型的能力。

### MIT License（MIT许可证）
最宽松的开源软件许可证之一，允许用户自由使用、修改、分发、商用，唯一要求是保留原版权声明。V4-Flash采用MIT协议。

## P

### Peak-Valley Pricing（峰谷定价）
按时间段差异化定价的机制。DeepSeek API在高峰时段（工作日9:00-12:00、14:00-18:00）收取较高价格，空闲时段价格减半。类似电力系统的峰谷电价。

### Prefix Caching（前缀缓存）
参见"Cache Hit"。当多个请求共享相同前缀时自动缓存KV Cache的机制，是降低API成本最重要的优化手段。

### Prompt（提示词）
用户输入给模型的指令或问题。好的prompt设计可以显著提升输出质量并减少token消耗。

## R

### RAG（Retrieval-Augmented Generation，检索增强生成）
一种AI应用架构，先从知识库中检索相关文档片段，再将其作为上下文传给模型生成回答。RAG场景中system prompt通常包含大量检索到的固定内容，缓存命中率很高。

## S

### SLA（Service Level Agreement，服务等级协议）
服务提供商对服务可用性、响应时间等的承诺。DeepSeek免费API层和网页端不提供SLA保障，企业级服务可洽谈SLA。

### Streaming / SSE（流式响应/Server-Sent Events）
API返回方式之一，模型生成内容时逐字/逐句实时推送给客户端，而非等待全部生成完毕后一次性返回。类似ChatGPT网页端的打字机效果。

### SWE-bench
软件工程基准测试，要求模型自主解决真实GitHub仓库中的Issue。SWE-bench Pro是其更难的版本，V4-Pro以80.6%排名第一。

### System Prompt（系统提示词）
在对话开始前设置的全局指令，定义模型的角色、行为规则、输出格式等。System prompt在多轮对话中保持不变，是缓存命中的最佳实践场景。

## T

### Tensor Parallelism（张量并行）
将模型的权重矩阵拆分到多张GPU上进行并行计算的技术，用于部署超过单卡显存容量的大模型。

### Thinking Mode / Reasoning Mode（思考模式/推理模式）
V4系列支持三档思考模式：Non-Think（快速响应，无思维链）、Think High（中等深度推理，显示思维链）、Think Max（最深度推理，思维链最长）。思考模式会额外消耗reasoning tokens。

### Token
模型处理文本的基本单位。1个token约等于0.75个中文字或0.3个英文单词。例如"DeepSeek-V4正式版"大约是5-6个tokens。API计费以token为单位。

| 文本 | 约token数 |
|------|----------|
| 1个汉字 | ~1.3 tokens |
| 1个英文单词 | ~1.3 tokens |
| 1000字中文文章 | ~1300 tokens |
| 一页A4纸（500字） | ~650 tokens |
| 一本《三体》（约90万字） | ~120万tokens |

### Tool Calls
见"Function Calling"。

### TPM / RPM（Tokens Per Minute / Requests Per Minute）
每分钟token数/每分钟请求数，是API速率限制的计量单位。

## V

### vLLM
一个高性能的大模型推理服务框架，支持PagedAttention等优化技术，是部署V4-Flash自托管的推荐方案之一。

## 数字

### 1M Context（100万上下文）
V4系列支持的最大输入长度为100万tokens（约75万汉字），相当于一整本长篇小说或中型代码仓库的完整代码。

### 384K Output（38.4万输出）
V4系列支持单次最大输出384,000 tokens（约29万汉字），可以生成超长文档、完整代码模块、详细分析报告。
