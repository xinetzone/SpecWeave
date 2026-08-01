---
id: "llm-token-optimization-tool-survey"
title: "LLM Token优化工具与框架调研报告"
source: "deep-research调研结果"
created_at: "2026-08-01"
updated_at: "2026-08-01"
category: "knowledge"
subcategory: "llm-token-optimization"
tags: ["LLM", "Token优化", "推理引擎", "Prompt缓存", "Token压缩"]
authors: ["AI Research Assistant"]
version: "1.0.0"
---

# LLM Token优化工具与框架调研报告

## 概述

本报告系统调研了主流的大语言模型（LLM）Token优化相关工具与框架，覆盖应用框架、推理引擎、专门优化工具以及云厂商缓存特性四大类别，共计20个工具。报告从Token优化的三大核心路径——减少（Reduction）、复用（Reuse/Caching）、压缩（Compression）——出发，对每个工具的核心功能、优化机制、开源状态、适用场景及优缺点进行客观分析。

**Token优化三大路径说明：**
- **减少（Reduction）**：通过算法优化、量化、架构改进等方式减少每轮推理的Token计算量或存储开销
- **复用（Reuse/Caching）**：通过缓存机制复用已计算的KV Cache或Prompt前缀，避免重复计算
- **压缩（Compression）**：对输入Prompt或上下文进行Token级或语义级压缩，在保持语义的前提下减少Token数量

---

## 工具对比矩阵

| 工具名称 | 类别 | 核心优化机制 | 开源地址 | Stars (2026.07) | 适用场景 | 学习难度 |
|---|---|---|---|---|---|---|
| LangChain | 应用框架 | 链式编排优化、RAG检索策略、记忆管理 | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | ~139k | 复杂Agent工作流、RAG应用 | 中等 |
| LlamaIndex | 应用框架 | 数据索引优化、检索策略、分层索引 | [run-llama/llama_index](https://github.com/run-llama/llama_index) | ~49k | 知识密集型RAG、文档问答 | 低-中等 |
| Semantic Kernel | 应用框架 | 插件式架构、函数契约、企业集成 | [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) | ~28k | .NET企业应用、Azure集成 | 中等 |
| LiteLLM | 应用框架 | 统一网关、预算控制、FallBack路由 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | ~48k | 多模型管理、成本控制网关 | 低 |
| Haystack | 应用框架 | Pipeline架构、检索优化、NLP流水线 | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | ~20k | 企业级搜索、文档处理 | 中等 |
| Dify | 应用框架 | LLMOps、可视化工作流、缓存集成 | [langgenius/dify](https://github.com/langgenius/dify) | ~140k | 低代码AI应用平台 | 低 |
| Flowise | 应用框架 | 可视化LangChain编排、拖拽式流程 | [FlowiseAI/Flowise](https://github.com/FlowiseAI/Flowise) | ~53k | 快速原型、无代码构建 | 低 |
| vLLM | 推理引擎 | PagedAttention、Continuous Batching、前缀缓存 | [vllm-project/vllm](https://github.com/vllm-project/vllm) | ~77k | 高并发生产推理服务 | 中等-高 |
| Text Generation Inference | 推理引擎 | 连续批处理、FlashAttention、张量并行 | [huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) | ~17k | Hugging Face生态部署 | 中等 |
| TensorRT-LLM | 推理引擎 | 内核优化、量化、In-Flight Batching | [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | ~15k | NVIDIA GPU极致性能 | 高 |
| llama.cpp | 推理引擎 | GGUF量化、CPU/GPU混合推理、低比特量化 | [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | ~88k | 本地部署、边缘设备、CPU推理 | 中等 |
| Ollama | 推理引擎 | llama.cpp封装、一键部署、模型管理 | [ollama/ollama](https://github.com/ollama/ollama) | ~155k | 本地开发、快速原型 | 低 |
| SGLang | 推理引擎 | RadixAttention、结构化生成、推测解码 | [sgl-project/sglang](https://github.com/sgl-project/sglang) | ~28k | 共享前缀工作负载、低延迟 | 中等-高 |
| LLMLingua/LongLLMLingua | 专门优化 | Token级压缩、问题感知压缩、小模型评分 | [microsoft/LLMLingua](https://github.com/microsoft/LLMLingua) | ~6.3k | Prompt压缩、长上下文RAG | 中等 |
| Selective Context | 专门优化 | 自信息过滤、无参数压缩、句法保留 | [liyucheng09/Selective_Context](https://github.com/liyucheng09/Selective_Context) | ~423 | 轻量上下文裁剪 | 低 |
| GPTCache | 专门优化 | 语义缓存、相似度匹配、多层缓存 | [zilliztech/GPTCache](https://github.com/zilliztech/GPTCache) | ~8k | 重复查询缓存、API成本削减 | 低-中等 |
| Cohere Rerank | 专门优化 | 交叉编码器重排序、检索精度提升 | [cohere-ai/cohere-python](https://github.com/cohere-ai/cohere-python) | N/A | RAG检索精度优化 | 低 |
| MemGPT (Mem0) | 专门优化 | 分层记忆管理、虚拟上下文、内存换入换出 | [cpacker/MemGPT](https://github.com/cpacker/MemGPT) | ~20k | 长对话记忆、无限上下文 | 中等 |
| OpenAI Prompt Caching | 云厂商缓存 | 自动前缀缓存、50%折扣、零代码 | [官方文档](https://platform.openai.com/docs/guides/prompt-caching) | 闭源 | GPT系列API成本优化 | 低 |
| Anthropic Prompt Caching | 云厂商缓存 | 显式缓存断点、90%折扣、TTL控制 | [官方文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) | 闭源 | Claude系列API成本优化 | 低-中等 |
| Google Context Caching | 云厂商缓存 | 显式上下文缓存、多模态缓存、小时级存储 | [官方文档](https://cloud.google.com/vertex-ai/generative-ai/docs/context-cache/context-cache-overview) | 闭源 | Gemini系列API、多模态 | 中等 |
| 阿里云百炼上下文缓存 | 云厂商缓存 | 显式/隐式双模式、10%-20%折扣 | [官方文档](https://help.aliyun.com/zh/model-studio/context-cache) | 闭源 | 国内模型服务（通义千问等） | 低 |
| Kimi (月之暗面) 缓存 | 云厂商缓存 | Mooncake架构、自动前缀缓存、90%+命中率 | [官方文档](https://platform.moonshot.cn/) | 闭源 | Kimi长上下文API | 低 |
| 智谱GLM缓存 | 云厂商缓存 | 前缀缓存、分层计费 | [官方文档](https://open.bigmodel.cn/) | 闭源 | GLM系列模型API | 低 |

---

## 一、应用框架类

### 1. LangChain

**官方链接**：
- GitHub: https://github.com/langchain-ai/langchain
- 文档: https://python.langchain.com/

**核心功能概述**：
LangChain是目前生态最完整的LLM应用开发框架，提供链式调用、Agent编排、记忆管理、工具集成、RAG流水线等核心能力，支持500+第三方集成。

**Token优化具体机制**：
- **减少**：LCEL（LangChain Expression Language）管道优化减少冗余Prompt构造；提供多种文本分割器（RecursiveCharacterTextSplitter等）进行智能分块
- **复用**：内置ConversationBufferWindowMemory、ConversationSummaryMemory等记忆管理策略，支持对话历史的摘要复用；支持与缓存系统（如GPTCache）集成
- **压缩**：提供ContextualCompressionRetriever进行检索后上下文压缩；集成LLMLingua等压缩工具

**开源状态与Stars**：开源（MIT License），~139k Stars（2026.07）

**适用场景**：
- 复杂多步骤Agent工作流
- 多工具调用编排
- 需要丰富生态集成的生产级应用
- RAG与对话系统混合场景

**优缺点简评**：
- ✅ 优点：生态最完整、集成最丰富、社区活跃、LangSmith可观测性强
- ❌ 缺点：抽象层次高、学习曲线陡峭、版本迭代快导致API不稳定、Token开销相对较大（基准测试约2.4k tokens/query）

**版本信息**：v0.3.x（2026年稳定版）

---

### 2. LlamaIndex

**官方链接**：
- GitHub: https://github.com/run-llama/llama_index
- 文档: https://www.llamaindex.ai/

**核心功能概述**：
LlamaIndex（原GPT Index）是专注于数据索引和检索增强的框架，以数据为中心设计，提供丰富的数据连接器、索引结构和查询引擎，是RAG场景的首选框架。

**Token优化具体机制**：
- **减少**：内置多种索引结构（VectorStoreIndex、SummaryIndex、TreeIndex、KeywordTableIndex等），根据场景选择最优索引减少检索Token；分层索引策略支持海量文档
- **复用**：提供ComposableGraph支持多索引组合查询；ChatMemoryBuffer支持对话记忆管理
- **压缩**：原生支持SentenceWindowNodeParser、MetadataReplacementPostProcessor等高级RAG技术；LongLLMLingua集成优化长上下文

**开源状态与Stars**：开源（MIT License），~49k Stars（2026.07）

**适用场景**：
- 知识密集型RAG应用
- 文档问答系统
- 语义搜索与知识库
- 需要精细检索策略控制的场景

**优缺点简评**：
- ✅ 优点：RAG能力最强、检索策略丰富、API相对简洁、Token效率高（基准测试约1.6k tokens/query，比LangChain少33%）、内存占用低40%
- ❌ 缺点：多Agent能力较弱、生态比LangChain小、更专注于RAG而非通用Agent

**版本信息**：v0.11.x（2026年稳定版）

---

### 3. Semantic Kernel (SK)

**官方链接**：
- GitHub: https://github.com/microsoft/semantic-kernel
- 文档: https://learn.microsoft.com/en-us/semantic-kernel/

**核心功能概述**：
微软出品的企业级AI集成SDK，采用Plugin-Function契约模型，支持C#、Python、Java多语言，深度集成Azure和Microsoft生态，提供Process Framework用于长时间运行的工作流。

**Token优化具体机制**：
- **减少**：插件式松散耦合架构，按需加载函数定义；Function Calling自动生成精简Prompt
- **复用**：Memory Connector支持向量存储记忆复用；Kernel Memory提供持久化记忆
- **压缩**：支持文本摘要插件进行上下文压缩；Handlebars模板引擎优化Prompt构造

**开源状态与Stars**：开源（MIT License），~28k Stars（2026.07）

**适用场景**：
- .NET/Java企业级应用
- Microsoft Azure生态部署
- 需要严格安全合规的场景
- 长时间运行的业务流程自动化

**优缺点简评**：
- ✅ 优点：企业级特性完善、多语言支持、Azure集成度高、安全合规性好
- ❌ 缺点：Python生态相对较小、社区规模不及LangChain/LlamaIndex、与Microsoft栈耦合较紧

**版本信息**：v1.5.x（2026年稳定版）

---

### 4. LiteLLM

**官方链接**：
- GitHub: https://github.com/BerriAI/litellm
- 文档: https://docs.litellm.ai/

**核心功能概述**：
LiteLLM是一个统一的LLM网关，提供OpenAI兼容的接口调用100+模型提供商，内置预算管理、费用追踪、速率限制、FallBack路由等成本控制功能，是多模型管理的事实标准中间件。

**Token优化具体机制**：
- **减少**：智能路由将简单查询导向便宜模型（配合RouteLLM可节省85%成本）；自动重试与FallBack避免无效调用
- **复用**：作为代理层可与后端缓存集成；内置虚拟API Key的预算限额
- **压缩**：支持在代理层配置Prompt压缩策略

**开源状态与Stars**：开源（MIT License），~48k Stars（2026.07）

**适用场景**：
- 多LLM提供商统一管理
- API成本控制与预算执行
- 企业级LLM网关
- 模型路由与A/B测试

**优缺点简评**：
- ✅ 优点：支持100+提供商、统一OpenAI接口、实时预算追踪、Y Combinator背书
- ❌ 缺点：Python GIL在极高并发（1000+ RPS）下可能成为瓶颈

**版本信息**：持续更新（2026年活跃维护）

---

### 5. Haystack

**官方链接**：
- GitHub: https://github.com/deepset-ai/haystack
- 文档: https://docs.haystack.deepset.ai/

**核心功能概述**：
由deepset.ai开发的端到端NLP/LLM框架，采用Pipeline架构，从传统NLP演进而来，在搜索和问答领域生产就绪度高，支持多种检索器、阅读器和生成器的灵活组合。

**Token优化具体机制**：
- **减少**：Pipeline架构最小化组件间数据传递；优化的文档处理流水线
- **复用**：支持文档存储缓存；InMemoryDocumentStore等内置缓存
- **压缩**：Token效率在RAG框架中表现最佳（基准测试约1.57k tokens/query，为测试框架中最低）

**开源状态与Stars**：开源（Apache License 2.0），~20k Stars（2026.07）

**适用场景**：
- 企业级搜索系统
- 大规模文档处理
- 传统NLP与LLM混合场景
- 需要生产级稳定性的问答系统

**优缺点简评**：
- ✅ 优点：生产就绪度高、搜索能力强、Pipeline架构清晰、Token效率最高、由deepset.ai商业支持
- ❌ 缺点：对话Agent能力相对较弱、LLM社区比LangChain小、更偏传统NLP

**版本信息**：2.x系列（2026年稳定版）

---

### 6. Dify（补充）

**官方链接**：
- GitHub: https://github.com/langgenius/dify
- 文档: https://docs.dify.ai/

**核心功能概述**：
开源LLM应用开发平台，提供可视化工作流编排、RAG Pipeline、Agent构建、Prompt IDE、LLMOps监控等全生命周期能力，是Star数增长最快的LLMOps平台。

**Token优化具体机制**：
- **减少**：可视化工作流优化节点执行；内置Prompt IDE支持Prompt优化
- **复用**：RAG Pipeline内置缓存；支持数据集与知识库复用
- **压缩**：集成Rerank与上下文压缩

**开源状态与Stars**：开源（Apache License 2.0），~140k Stars（2026.07）

**适用场景**：
- 低代码/无代码AI应用构建
- 企业LLMOps平台
- 快速原型到生产部署
- 非技术用户参与的AI开发

**优缺点简评**：
- ✅ 优点：可视化界面友好、全栈能力、RAG/Agent/Workflow一体、开箱即用
- ❌ 缺点：深度定制需要二次开发、自托管资源需求较高

**版本信息**：持续更新（2026年活跃维护）

---

### 7. Flowise（补充）

**官方链接**：
- GitHub: https://github.com/FlowiseAI/Flowise
- 文档: https://docs.flowiseai.com/

**核心功能概述**：
基于LangChain的可视化拖拽式LLM流程构建工具，将LangChain的组件封装为可视化节点，用户通过连线方式构建Chatflow/Agent/RAG，无需编写代码。

**Token优化具体机制**：
- **减少**：可视化调试帮助识别冗余节点；LangChain底层优化继承
- **复用**：支持会话记忆与缓存组件
- **压缩**：集成LangChain的ContextualCompression

**开源状态与Stars**：开源（Apache License 2.0），~53k Stars（2026.07）

**适用场景**：
- 快速原型验证
- 无代码AI工作流构建
- 演示与教学
- 非工程师构建AI应用

**优缺点简评**：
- ✅ 优点：拖拽式操作、零代码启动、LangChain生态兼容、部署简单
- ❌ 缺点：复杂逻辑表达受限、生产级定制需要嵌入模式、性能开销相对纯代码高

**版本信息**：持续更新（2026年活跃维护）

---

## 二、推理引擎类

### 1. vLLM

**官方链接**：
- GitHub: https://github.com/vllm-project/vllm
- 文档: https://docs.vllm.ai/

**核心功能概述**：
由UC Berkeley Sky Computing Lab发起的开源高性能LLM推理引擎，以PagedAttention技术为核心，是目前生产环境部署的事实标准之一，提供OpenAI兼容API，支持200+模型架构。

**Token优化具体机制**：
- **减少（核心）**：PagedAttention将KV Cache组织为固定大小的页（类似OS虚拟内存），显存利用率从<40%提升至95%+；Continuous Batching在batch运行中动态插入/移除请求，消除GPU空转；Chunked Prefill优化长Prompt预填充
- **复用（核心）**：Automatic Prefix Caching（APC）自动缓存共享前缀的KV Cache（如System Prompt），相同前缀无需重复计算；支持多LoRA共享基础模型权重
- **压缩**：支持GPTQ、AWQ、AutoRound、INT4、INT8、FP8等多种量化格式；与FlashAttention/FlashInfer集成优化注意力计算

**开源状态与Stars**：开源（Apache License 2.0），~77k Stars（2026.07）

**适用场景**：
- 高并发生产API服务
- 通用LLM部署
- 需要OpenAI兼容接口的场景
- 研究与生产兼顾

**优缺点简评**：
- ✅ 优点：吞吐量高（H100上Llama 3.3-70B达2400 tok/s @100并发）、PagedAttention革命性优化、模型支持广、社区活跃、OpenAI API开箱即用
- ❌ 缺点：对新模型架构支持需要等待、极高负载下调优有一定门槛

**版本信息**：v0.19.x（2026年4月发布）

---

### 2. Text Generation Inference (TGI)

**官方链接**：
- GitHub: https://github.com/huggingface/text-generation-inference
- 文档: https://huggingface.co/docs/text-generation-inference

**核心功能概述**：
Hugging Face官方推出的推理服务器，与HF生态深度集成，提供生产级日志、指标和监控，支持连续批处理和张量并行。**注意**：根据2026年3月公告，TGI已进入维护模式，官方推荐新用户迁移至vLLM、SGLang、llama.cpp或MLX。

**Token优化具体机制**：
- **减少**：Continuous Batching支持动态批处理；FlashAttention v2集成；张量并行支持多GPU
- **复用**：支持Prefix Caching；与HF Hub模型版本管理深度集成
- **压缩**：支持GPTQ、AWQ、bitsandbytes量化

**开源状态与Stars**：开源（Apache License 2.0），~17k Stars（2026.07），维护模式

**适用场景**：
- 已有Hugging Face生态的部署
- 存量TGI系统维护
- 需要HF Hub零配置集成的场景（新用户不推荐）

**优缺点简评**：
- ✅ 优点：HF生态集成最佳、Docker一键部署、日志监控生产就绪
- ❌ 缺点：已进入维护模式（2026年3月）、吞吐量低于vLLM/SGLang、新功能不再积极开发

**版本信息**：最终维护版v2.4.x（2026年）

---

### 3. TensorRT-LLM

**官方链接**：
- GitHub: https://github.com/NVIDIA/TensorRT-LLM
- 文档: https://nvidia.github.io/TensorRT-LLM/

**核心功能概述**：
NVIDIA官方推出的LLM推理优化库，基于TensorRT深度优化，提供最高的原始推理性能，但需要为每个模型进行约28分钟的引擎编译，仅支持NVIDIA GPU。

**Token优化具体机制**：
- **减少**：高度优化的CUDA内核；In-Flight Batching（类似Continuous Batching）；FP8/INT4/INT8量化；Speculative Decoding；Paged KV Cache
- **复用**：KV Cache复用；多实例GPU（MIG）支持
- **压缩**：支持SmoothQuant、GPTQ、AWQ、FP8等多种量化方案；权重修剪

**开源状态与Stars**：开源（Apache License 2.0），~15k Stars（2026.07）

**适用场景**：
- NVIDIA GPU数据中心极致性能需求
- 固定模型高流量服务
- 对延迟/吞吐量有极致要求的场景
- 大规模云端部署

**优缺点简评**：
- ✅ 优点：原始性能最高（H100上Llama 3.3-70B达2780 tok/s）、NVIDIA官方支持、深度硬件优化
- ❌ 缺点：每个模型需28分钟编译、仅支持NVIDIA GPU、学习曲线陡峭、灵活性差

**版本信息**：v1.2.x（2026年4月）

---

### 4. llama.cpp

**官方链接**：
- GitHub: https://github.com/ggml-org/llama.cpp
- 文档: https://github.com/ggerganov/llama.cpp/tree/master/examples/main

**核心功能概述**：
纯C/C++实现的LLM推理引擎，无外部依赖，是本地LLM生态的基石。支持GGUF格式量化模型，可在几乎所有硬件上运行（NVIDIA CUDA、AMD ROCm、Apple Metal、CPU、树莓派等），是Ollama等工具的底层引擎。

**Token优化具体机制**：
- **减少**：支持1.5-bit到8-bit全系列整数量化（Q2_K到Q8_0）；CPU/GPU混合推理；ARM NEON/AVX/AVX2/AVX512/AMX指令集优化
- **复用**：KV Cache量化；支持Prompt缓存保存/加载
- **压缩**：GGUF格式本身即为量化压缩格式；支持K/V量化进一步减少KV Cache内存

**开源状态与Stars**：开源（MIT License），~88k Stars（2026.07）

**适用场景**：
- 本地开发与测试
- CPU/边缘设备部署
- 消费级GPU运行大模型
- 无网络环境/气隙部署
- 资源受限环境

**优缺点简评**：
- ✅ 优点：硬件支持最广、GGUF生态标准、内存占用极低（7B模型INT4仅需5.4GB VRAM）、无需GPU也可运行、MIT协议宽松
- ❌ 缺点：高并发吞吐量不及vLLM/SGLang、生产级服务需要额外封装、C/C++代码定制难度高

**版本信息**：b6838（2026年7月），持续活跃开发

---

### 5. Ollama（补充）

**官方链接**：
- GitHub: https://github.com/ollama/ollama
- 文档: https://github.com/ollama/ollama/tree/main/docs

**核心功能概述**：
基于llama.cpp封装的用户友好型本地LLM运行工具，提供一键模型拉取、运行、API服务，支持OpenAI兼容端点，是本地开发最便捷的选择。

**Token优化具体机制**：
- **减少**：底层继承llama.cpp所有量化优化；自动根据硬件选择最优量化等级
- **复用**：模型管理与本地缓存；Modelfile支持自定义系统提示复用
- **压缩**：默认使用Q4_K_M量化平衡质量与速度

**开源状态与Stars**：开源（MIT License），~155k Stars（2026.07）

**适用场景**：
- 本地开发快速原型
- 个人桌面使用
- 低并发内部工具
- 开发环境模型调试

**优缺点简评**：
- ✅ 优点：一键部署（`ollama run llama3`）、模型库丰富、OpenAI兼容API、跨平台支持
- ❌ 缺点：缺少PagedAttention、高并发支持弱、不适合生产环境对外服务、结构化输出支持有限

**版本信息**：v0.12.6（2026年）

---

### 6. SGLang（补充）

**官方链接**：
- GitHub: https://github.com/sgl-project/sglang
- 文档: https://sglang.io/

**核心功能概述**：
由LMSYS（Chatbot Arena团队）开发的高性能服务框架，核心创新是RadixAttention——基于基数树的KV Cache共享机制，在共享前缀工作负载（如RAG、多轮对话）中表现优异，同时支持结构化生成。

**Token优化具体机制**：
- **减少（核心）**：RadixAttention通过基数树自动复用跨请求的公共前缀KV Cache，共享前缀场景吞吐量比vLLM高29%；推测解码（Speculative Decoding）降低延迟
- **复用（核心）**：RadixAttention实现细粒度KV Cache自动复用，不仅限于前缀匹配；支持多轮对话历史自动复用
- **压缩**：支持FP8/INT8量化；与FlashInfer深度集成；约束解码加速JSON结构化生成

**开源状态与Stars**：开源（Apache License 2.0），~28k Stars（2026.07）

**适用场景**：
- RAG系统（大量共享系统提示）
- 多轮对话服务
- 需要结构化JSON输出
- 低延迟交互式应用

**优缺点简评**：
- ✅ 优点：共享前缀场景吞吐量领先、RadixAttention设计先进、结构化生成速度快、p95延迟低（280ms）
- ❌ 缺点：生态相对较新、模型兼容性略少于vLLM、社区规模较小

**版本信息**：v0.5.x（2026年）

---

## 三、专门优化工具类

### 1. LLMLingua / LongLLMLingua / LLMLingua-2

**官方链接**：
- GitHub: https://github.com/microsoft/LLMLingua
- 论文: https://arxiv.org/abs/2310.05736 (LLMLingua), https://arxiv.org/abs/2310.06839 (LongLLMLingua), https://arxiv.org/abs/2403.12968 (LLMLingua-2)

**核心功能概述**：
微软研究院开发的Prompt压缩系列工具，从EMNLP 2023到ACL 2024持续迭代。通过小语言模型评估Token重要性，移除低信息Token，实现最高20倍压缩且性能损失极小。

**Token优化具体机制**：
- **压缩（核心）**：
  - LLMLingua：使用小型LM（GPT-2-small/LLaMA-7B）通过困惑度（perplexity）评分Token，迭代式移除可预测Token，配合预算控制器动态分配压缩比
  - LongLLMLingua：增加问题感知能力，对问题相关的上下文块进行相关性评分并重新排序文档，对抗"Lost in the Middle"位置偏差，在NaturalQuestions上以1/4 Token量提升21.4%性能
  - LLMLingua-2：将压缩重构为Token级二分类任务，使用BERT大小的编码器通过GPT-4蒸馏训练，速度比初代快3-6倍，域外泛化更好，压缩比控制更精确

**开源状态与Stars**：开源（MIT License），~6.3k Stars（2026.07）

**适用场景**：
- 长Prompt压缩（>2000 tokens）
- RAG系统检索后上下文压缩
- API成本敏感场景
- 实时对话系统延迟优化

**优缺点简评**：
- ✅ 优点：压缩率高（最高20x）、质量损失小（GSM8K上仅1.5%退化）、LongLLMLingua针对RAG优化效果显著、LLMLingua-2速度快
- ❌ 缺点：压缩本身需要一次小模型调用，短Prompt场景可能得不偿失；压缩后文本人类不可读；需要与缓存策略配合（缓存稳定前缀，压缩动态部分）

**版本信息**：持续更新（2026年活跃维护），LLMLingua-2为最新版本

---

### 2. Selective Context

**官方链接**：
- GitHub: https://github.com/liyucheng09/Selective_Context
- 论文: https://arxiv.org/abs/2309.04837

**核心功能概述**：
无参数的轻量级上下文压缩方法，基于自信息（Self-Information）和句法分析进行Token过滤，不需要训练额外模型即可工作。

**Token优化具体机制**：
- **压缩（核心）**：使用基础LM计算Token的自信息 I(xi) = -log P(xi|x<i)，结合SpaCy句法分析保留名词短语等关键成分，在保持语法连贯性的前提下移除低信息Token。完全无训练，参数自由。

**开源状态与Stars**：开源（MIT License），~423 Stars（2026.07），自2024年初起更新不活跃

**适用场景**：
- 轻量级上下文裁剪
- 不想引入额外模型依赖的场景
- 快速实验与原型验证

**优缺点简评**：
- ✅ 优点：无参数无需训练、速度快、保留句法结构、实现简单
- ❌ 缺点：项目维护不活跃、压缩率和质量不如LLMLingua系列、无问题感知能力

**版本信息**：最后更新2024年初

---

### 3. GPTCache

**官方链接**：
- GitHub: https://github.com/zilliztech/GPTCache
- 文档: https://gptcache.readthedocs.io/

**核心功能概述**：
Zilliz（Milvus团队）开发的LLM语义缓存库，通过存储查询的Embedding和响应，对相似查询直接返回缓存结果，避免重复API调用，可将响应速度提升100倍，成本降低10倍。

**Token优化具体机制**：
- **复用（核心）**：语义缓存而非精确匹配缓存，通过Embedding相似度判断查询是否重复；支持多层缓存（内存、向量数据库、KV存储）；可配置相似度阈值平衡命中率与准确率
- **减少**：相似查询直接命中缓存，完全跳过LLM API调用
- **与框架集成**：原生集成LangChain和LlamaIndex

**开源状态与Stars**：开源（MIT License），~8k Stars（2026.07）

**适用场景**：
- 高频重复查询场景（客服、FAQ）
- RAG Pipeline中重复检索结果缓存
- API成本削减
- 降低P99延迟

**优缺点简评**：
- ✅ 优点：语义匹配而非字符串匹配、无缝集成LangChain/LlamaIndex、缓存存储后端灵活（支持Milvus/FAISS/Redis等）、速度提升显著
- ❌ 缺点：需要调优相似度阈值避免误命中、增加Embedding计算开销、对高度多样化/唯一性查询效果有限

**版本信息**：v0.1.x系列（2025年7月更新）

---

### 4. Cohere Rerank

**官方链接**：
- 文档: https://docs.cohere.com/reference/rerank
- Python SDK: https://github.com/cohere-ai/cohere-python

**核心功能概述**：
Cohere提供的托管式交叉编码器重排序API，作为RAG系统的第二阶段检索组件，在向量检索初筛后对候选文档进行精排，显著提升检索准确率，从而间接减少发送给LLM的无关上下文Token。

**Token优化具体机制**：
- **减少（间接）**：提高Top-K检索准确率，避免将无关文档送入LLM上下文；Rerank后可以只取Top-3而非Top-10，减少60-70%检索上下文Token
- **压缩（间接）**：通过提升检索精度实现有效上下文压缩，同样的回答质量下可使用更少的文档块

**开源状态**：托管API服务，Python SDK开源，核心模型闭源

**适用场景**：
- RAG系统检索精度优化
- 对回答准确性要求高的企业应用
- 向量检索结果噪音较大的场景

**优缺点简评**：
- ✅ 优点：无需自托管模型、API调用简单、效果稳定、定价低（$0.10/1000次搜索）、可显著提升RAG质量
- ❌ 缺点：托管服务有API调用成本、需要联网、相比本地Reranker（如FlashRank、bge-reranker）增加网络延迟

**版本信息**：持续更新（2026年），支持rerank-multilingual-v3.0等多语言模型

---

### 5. MemGPT / Mem0（补充）

**官方链接**：
- MemGPT GitHub: https://github.com/cpacker/MemGPT
- Mem0 GitHub: https://github.com/mem0ai/mem0

**核心功能概述**：
受操作系统虚拟内存启发的分层记忆管理系统（现发展为Mem0），通过在主上下文（类似RAM）和外部存储（类似磁盘）之间智能换入换出信息，实现"无限上下文"效果，是长对话和长时记忆Agent的关键技术。

**Token优化具体机制**：
- **减少**：记忆分层架构，仅将相关记忆加载到上下文窗口；自动总结与提取关键信息
- **复用**：外部向量数据库存储历史记忆，按需检索召回；对话历史摘要复用
- **压缩**：记忆自动提取为结构化事实，冗余对话被压缩为摘要

**开源状态与Stars**：开源（Apache License 2.0），MemGPT ~20k Stars（2026.07）

**适用场景**：
- 长对话/多轮会话
- 个性化AI助手（长期记忆用户偏好）
- 需要"无限上下文"的Agent系统
- 虚拟角色/陪伴类应用

**优缺点简评**：
- ✅ 优点：突破上下文窗口限制、记忆持久化、支持用户级/会话级/Agent级多层记忆、主动记忆召回
- ❌ 缺点：系统复杂度增加、记忆检索质量影响最终效果、额外的向量数据库依赖

**版本信息**：Mem0为MemGPT的演进版本，持续活跃开发（2026年）

---

## 四、云厂商缓存特性类

### 1. OpenAI Prompt Caching

**官方链接**：
- 文档: https://platform.openai.com/docs/guides/prompt-caching

**核心功能概述**：
OpenAI于2024年推出的自动前缀缓存功能，对GPT-4o及更新模型默认启用，无需任何代码修改，系统自动缓存长度≥1024 tokens的Prompt前缀，缓存命中的输入Token享受50%折扣。

**Token优化具体机制**：
- **复用（核心）**：自动前缀缓存，基于Prompt前1024+ tokens的哈希进行匹配；缓存TTL约5-10分钟，命中后重置；缓存写入免费
- **减少**：缓存命中时跳过预填充计算，TTFT（首Token时间）降低80%
- **缓存粒度**：1024 tokens起，按128 tokens增量递增

**折扣与定价**（2026年中）：
- 缓存写入：无额外费用
- 缓存读取：输入Token价格的50%
- GPT-5.4/GPT-5.5部分模型已支持90%缓存折扣（与Anthropic对齐）

**开源状态**：闭源API服务

**适用场景**：
- 所有使用OpenAI API的生产应用
- 长System Prompt场景
- 多轮对话（对话历史前缀稳定）
- 零成本接入（无需改代码）

**优缺点简评**：
- ✅ 优点：完全自动无需代码、零配置、写入免费、实施成本为零
- ❌ 缺点：折扣力度相对较小（50%）、开发者无法控制缓存行为、缓存命中率不透明、TTL不可控、无法显式创建/管理缓存

**版本/更新信息**：2024年8月发布，持续优化中（2026年）

---

### 2. Anthropic Prompt Caching

**官方链接**：
- 文档: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching

**核心功能概述**：
Anthropic推出的开发者可控式Prompt缓存，通过在Prompt中显式放置`cache_control`断点（最多4个）精确控制缓存内容，缓存命中享受90%折扣，是目前折扣力度最大的官方缓存方案。

**Token优化具体机制**：
- **复用（核心）**：显式缓存断点，每个断点前的内容作为独立缓存块；支持5分钟（默认，ephemeral）和1小时TTL选项；缓存命中时首Token延迟降低85%
- **减少**：精确控制哪些内容缓存（System Prompt、工具定义、Few-shot示例、长文档等）；可在响应元数据中查看各缓存块命中情况
- **缓存粒度**：Opus 4.x/Sonnet 4.x/Haiku 4.5需1024-4096 tokens起（不同模型阈值不同）

**折扣与定价**（2026年中）：
- 5分钟TTL缓存写入：输入价格的1.25倍
- 1小时TTL缓存写入：输入价格的2倍
- 缓存读取：输入价格的10%（即90%折扣）

**开源状态**：闭源API服务

**适用场景**：
- Claude API重度用户
- 超长System Prompt/工具定义场景
- RAG系统（长文档作为缓存前缀）
- 需要精确控制缓存行为的生产应用
- 成本敏感的高流量场景

**优缺点简评**：
- ✅ 优点：折扣最高（90%）、开发者可精确控制、缓存命中情况可观测、支持自定义TTL、长上下文效果显著
- ❌ 缺点：缓存写入有溢价（1.25x/2x）、需要修改代码添加断点、对Prompt组织有要求（稳定内容必须放前面）、字节级精确匹配（一个空格变化即失效）

**版本/更新信息**：2024年8月发布，2026年支持多断点、1小时TTL等增强

---

### 3. Google Context Caching

**官方链接**：
- 文档: https://cloud.google.com/vertex-ai/generative-ai/docs/context-cache/context-cache-overview

**核心功能概述**：
Google Vertex AI提供的显式上下文缓存，支持创建、引用、管理缓存对象，特色是支持多模态内容（视频、音频）缓存，采用存储时间计费模式，缓存有效期可手动控制（最长至删除）。

**Token优化具体机制**：
- **复用（核心）**：显式创建缓存对象，通过cache_name引用；支持文本、图像、视频、音频多模态缓存；缓存读取享受75%折扣；同时支持隐式自动缓存
- **减少**：缓存命中时TTFT显著降低
- **特色**：支持超长上下文缓存（Gemini 2.5 Pro支持200万token窗口），多模态缓存是独特优势

**折扣与定价**（2026年中）：
- 缓存创建：免费
- 缓存存储：$4.50/百万tokens/小时
- 缓存读取：输入价格的25%（即75%折扣）；Gemini 2.5+/3支持90%折扣
- 缓存有效期：手动控制，可至显式删除

**开源状态**：闭源云服务（Vertex AI）

**适用场景**：
- Gemini API用户
- 多模态应用（视频/音频理解）
- 需要超长缓存时间（>1小时）的场景
- 百万级token长文档反复查询

**优缺点简评**：
- ✅ 优点：支持多模态缓存、存储期灵活（可长期）、显式管理、Gemini 2.5+支持90%折扣
- ❌ 缺点：存储费模式对短生命周期缓存不友好、最小缓存块较大（32768 tokens）、Vertex AI集成相对复杂

**版本/更新信息**：2024年发布，2026年持续增强多模态支持

---

### 4. 国内厂商缓存特性（补充）

#### 阿里云百炼上下文缓存

**官方链接**：https://help.aliyun.com/zh/model-studio/context-cache

**核心特性**：
- **双模式**：同时支持显式缓存（cache_control标记，10%折扣）和隐式缓存（自动，20%折扣）
- **显式缓存**：创建费125%，命中10%，有效期5分钟（命中重置），最少1024 tokens
- **隐式缓存**：自动，无需配置，命中20%折扣，最少256 tokens
- **支持模型**：通义千问全系列（Qwen3.8/3.7/3.6/3.5等），以及第三方部署模型（Kimi、GLM、MiniMax等）
- **特色**：预置吞吐（PTU）部署同样支持缓存

**适用场景**：国内通义千问及阿里云生态用户

---

#### Kimi（月之暗面）缓存

**核心特性**：
- **架构基础**：Mooncake分离式推理架构，编程场景缓存命中率超过90%
- **自动前缀缓存**：命中即打折模式，对重复系统指令/工具定义自动缓存
- **显式缓存**：通过`extra_body`传递`cache_id`支持超长文档显式缓存
- **定价**：kimi-k3输入未命中缓存20元/百万tokens，命中缓存2元/百万tokens（即90%折扣），输出100元/百万tokens
- **上下文分层定价**：推出k3-256k版本（256k上下文），配额消耗约为1M版本的一半
- **特色**：D-Mail技术支持主动回滚到检查点，主动做减法优化上下文

**适用场景**：长上下文编程、长文档处理、代码助手等Kimi API用户

---

#### 智谱GLM缓存

**核心特性**：
- **前缀缓存**：支持自动前缀缓存
- **缓存定价**：编码场景中缓存命中部分约占90%-95%，实际成本大幅降低
- **API参考价**：输入未命中缓存约4元/百万tokens，命中缓存约0.7元/百万tokens（约82.5%折扣）
- **工具链**：Coding Plan套餐内置大量MCP工具，工具定义缓存效果好

**适用场景**：GLM系列模型用户、Coding Plan开发者

---

## 五、选型建议总结

### 按优化路径选型

| 优化路径 | 首选工具 | 适用场景 |
|---|---|---|
| **减少（Reduction）** | vLLM（PagedAttention）、llama.cpp（量化）、TensorRT-LLM（极致性能） | 推理服务性能优化、硬件成本控制 |
| **复用（Caching）** | Anthropic Prompt Caching（90%折扣）、vLLM APC、GPTCache、OpenAI自动缓存 | API成本削减、延迟降低、长System Prompt |
| **压缩（Compression）** | LLMLingua-2（快速压缩）、LongLLMLingua（RAG优化）、Cohere Rerank（检索精度） | 长上下文、RAG系统、Prompt精简 |

### 按技术栈选型

| 场景 | 推荐组合 |
|---|---|
| 快速原型/本地开发 | Ollama + LangChain/LlamaIndex |
| 生产RAG系统 | vLLM/SGLang + LlamaIndex + Anthropic/OpenAI缓存 + Cohere Rerank |
| 企业级.NET应用 | Semantic Kernel + Azure OpenAI缓存 |
| 多模型成本管控 | LiteLLM网关 + GPTCache语义缓存 |
| 边缘/CPU部署 | llama.cpp + 4-bit量化 |
| 极致性能NVIDIA | TensorRT-LLM + Triton Inference Server |
| 低代码平台 | Dify/Flowise + vLLM后端 |
| 长对话Agent | Mem0 + SGLang（RadixAttention）+ Anthropic缓存 |

### 最佳实践组合策略

生产环境中通常组合使用多种优化手段以达到最佳效果：

1. **稳定前缀优先缓存**：System Prompt、工具定义、Few-shot示例等不常变化的内容通过云厂商缓存（Anthropic 90%折扣或vLLM APC）复用
2. **动态检索内容压缩**：每次请求变化的RAG检索结果使用LongLLMLingua或Rerank进行压缩/精排，减少无关Token
3. **重复查询语义缓存**：高频重复查询通过GPTCache在应用层缓存，完全跳过LLM调用
4. **推理层硬件优化**：部署层使用vLLM/SGLang+量化，最大化GPU吞吐量
5. **框架层选择**：RAG优先选LlamaIndex，复杂Agent选LangChain，注意框架本身Token开销差异（Haystack≈1.57k < LlamaIndex≈1.6k < LangChain≈2.4k）

---

## 附录：数据来源与说明

本报告数据采集时间为2026年7-8月，主要来源包括：
- 各项目GitHub仓库Stars与README
- 官方文档与定价页面
- 第三方基准测试（AIMultiple RAG Benchmark 2026、Spheron H100 Benchmarks、MarkAI Code基准测试等）
- arXiv论文（LLMLingua系列、PagedAttention论文等）
- 行业分析文章与实践指南

注：Stars数为近似值，随时间变化；定价信息基于2026年中公开数据，实际以官方最新价格为准；TGI已进入维护模式，新部署不推荐使用。
