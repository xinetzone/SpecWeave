---
id: "docs-knowledge-learning-llm-token-optimization-references"
title: "LLM Token 优化参考文献"
category: "knowledge"
date: "2026-08-01"
---
# LLM Token 优化参考文献

## 基础论文

| 标题 | 链接 | 说明 |
|------|------|------|
| Attention Is All You Need | [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) | Transformer架构奠基论文，提出自注意力机制 |
| LoRA: Low-Rank Adaptation of Large Language Models | [arXiv:2106.09685](https://arxiv.org/abs/2106.09685) | 参数高效微调经典方法，大幅降低微调成本 |
| QLoRA: Efficient Finetuning of Quantized LLMs | [arXiv:2305.14314](https://arxiv.org/abs/2305.14314) | 4bit量化+LoRA，单卡即可微调大模型 |
| Fast Inference from Transformers via Speculative Decoding | [arXiv:2302.01318](https://arxiv.org/abs/2302.01318) | 投机解码原始论文，用小模型草稿加速大模型生成 |
| FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness | [arXiv:2205.14135](https://arxiv.org/abs/2205.14135) | IO感知注意力算法，显著减少GPU内存访问 |
| GQA: Training Generalized Multi-Query Transformer Models | [arXiv:2305.13245](https://arxiv.org/abs/2305.13245) | 分组查询注意力，平衡推理速度与模型质量 |
| Mistral 7B | [arXiv:2310.06825](https://arxiv.org/abs/2310.06825) | 引入滑动窗口注意力(SWA)，高效处理长上下文 |
| BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding | [arXiv:1810.04805](https://arxiv.org/abs/1810.04805) | WordPiece分词的代表性应用，双向Transformer架构 |
| SentencePiece: A simple and language independent subword tokenizer | [arXiv:1808.06226](https://arxiv.org/abs/1808.06226) | 语言无关子词分词工具，无需预分词 |
| Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | [arXiv:2005.11401](https://arxiv.org/abs/2005.11401) | RAG原始论文，检索增强生成范式 |
| Distilling the Knowledge in a Neural Network | [arXiv:1503.02531](https://arxiv.org/abs/1503.02531) | 知识蒸馏奠基论文，教师-学生模型训练范式 |
| Chain-of-Thought Prompting Elicits Reasoning in Large Language Models | [arXiv:2201.11903](https://arxiv.org/abs/2201.11903) | CoT思维链提示技术，显著提升推理能力 |

## 官方文档

| 标题 | 链接 | 说明 |
|------|------|------|
| OpenAI API Documentation | [platform.openai.com/docs](https://platform.openai.com/docs) | OpenAI GPT系列官方文档，含Token计费与最佳实践 |
| Anthropic Claude Documentation | [docs.anthropic.com](https://docs.anthropic.com) | Claude模型官方文档，Prompt Caching等特性说明 |
| vLLM Documentation | [docs.vllm.ai](https://docs.vllm.ai) | PagedAttention官方文档，高吞吐LLM推理引擎 |
| Hugging Face Transformers Documentation | [huggingface.co/docs/transformers](https://huggingface.co/docs/transformers) | Transformers库官方文档，含量化、Flash Attention等配置 |
| LangChain Documentation | [python.langchain.com](https://python.langchain.com) | RAG与Chain编排框架文档，含分块、检索最佳实践 |
| LlamaIndex Documentation | [docs.llamaindex.ai](https://docs.llamaindex.ai) | 数据框架文档，RAG与上下文优化指南 |

## 工程博客

| 标题 | 链接 | 说明 |
|------|------|------|
| GitHub Copilot: Optimizing latency for AI code suggestions | [github.blog](https://github.blog/2023-06-20-how-github-copilot-is-getting-better-at-understanding-your-code/) | GitHub Copilot工程实践，延迟优化与Token策略 |
| How Kapden built a low-cost LLM chatbot | [kapden.com/blog](https://www.kapden.com/blog) | 生产环境LLM成本优化实战经验 |
| Cursor: Building a fast AI code editor | [cursor.sh/blog](https://cursor.sh/blog) | Cursor编辑器技术博客，上下文管理与缓存策略 |
| Semantic Cache: 10x cheaper LLM API calls | [medium.com/semantic-cache](https://medium.com) | 语义缓存技术实践，大幅降低重复查询成本 |
| vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention | [blog.vllm.ai](https://blog.vllm.ai) | vLLM团队官方博客，PagedAttention技术详解 |
| The Illustrated Transformer | [jalammar.github.io](https://jalammar.github.io/illustrated-transformer/) | Transformer架构可视化经典教程 |

## 开源项目

| 标题 | 链接 | 说明 |
|------|------|------|
| vLLM | [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm) | 高吞吐LLM推理引擎，实现PagedAttention |
| LangChain | [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) | LLM应用开发框架，提供完整RAG工具链 |
| LlamaIndex | [github.com/run-llama/llama_index](https://github.com/run-llama/llama_index) | 数据框架，专注于RAG与上下文注入 |
| Flash Attention | [github.com/Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention) | Flash Attention官方实现，快速精确注意力 |
| PEFT | [github.com/huggingface/peft](https://github.com/huggingface/peft) | Hugging Face参数高效微调库，支持LoRA/QLoRA |
| bitsandbytes | [github.com/TimDettmers/bitsandbytes](https://github.com/TimDettmers/bitsandbytes) | 量化库，支持8bit/4bit量化推理与训练 |
| GPTCache | [github.com/zilliztech/GPTCache](https://github.com/zilliztech/GPTCache) | LLM语义缓存库，支持相似度匹配缓存 |
| LangChain Text Splitters | [python.langchain.com/docs/modules/data_connection/document_transformers/](https://python.langchain.com/docs/modules/data_connection/document_transformers/) | 多种分块策略官方实现 |
| Cohere Rerank | [cohere.com/rerank](https://cohere.com/rerank) | 商用Reranker服务，提升检索结果质量 |
| Sentence-Transformers | [github.com/UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers) | 句向量模型库，语义检索与语义缓存基础 |

---
<!-- created on 2026-08-01 -->
