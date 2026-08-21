---
id: "llm-token-optimization-principles-facts"
title: "大语言模型Token节省机制底层原理事实清单"
date: "2026-08-01"
type: "knowledge"
tags: ["LLM", "Token", "Tokenization", "Transformer", "KV-Cache", "PagedAttention", "Pricing"]
maturity: "L1"
source: "deep-research"
validation_count: 1
reuse_count: 0
---

# 大语言模型Token节省机制底层原理事实清单

## 零、核心术语速查（新手必读）

> 💡 如果你第一次接触LLM优化，请先阅读本节：
>
> | 术语 | 一句话解释 |
> |------|----------|
> | **Token** | LLM处理文本的最小单位，类似"子词"——1个英文单词≈1-3个token，1个汉字≈1-2个token |
> | **分词器（Tokenizer）** | 将文本拆分成token的算法，模型训练时确定，不同模型分词结果不同 |
> | **Transformer** | 当前主流LLM使用的神经网络架构，核心是自注意力机制 |
> | **自注意力（Self-Attention）** | Transformer的核心计算，让每个token能"看到"序列中所有其他token |
> | **KV缓存（KV Cache）** | 生成时缓存历史token的Key/Value向量，避免重复计算——这是LLM能多轮对话的基础 |
> | **Prefill阶段** | 处理输入提示词的阶段，一次性计算所有输入token，速度快、计算密集 |
> | **Decoding阶段** | 逐token生成输出的阶段，每次生成1个新token，速度慢、内存密集 |
> | **TTFT** | Time To First Token，首token延迟——用户发送请求到收到第一个字的等待时间 |
> | **TPOT** | Time Per Output Token，每输出一个token的时间——决定生成速度 |
> | **Prompt Caching（前缀缓存）** | 缓存重复出现的提示词前缀（如系统提示），缓存命中时只需付10%左右费用 |
> | **PagedAttention** | vLLM推理引擎的核心技术，像操作系统虚拟内存一样管理KV缓存，大幅提升GPU利用率 |
> | **LoRA** | 一种高效微调技术，只需训练少量参数就能让模型适配特定任务，无需重新训练整个模型 |
> | **RAG** | Retrieval-Augmented Generation，检索增强生成——先从知识库检索相关内容再给LLM，避免把所有文档都塞进上下文 |
> | **Reranker** | 重排序器，对RAG初步检索出的文档做更精准的排序，选出最相关的少量内容传给LLM |
> | **量化（Quantization）** | 将模型参数从16位浮点压缩到4位/8位，减少内存占用、提升速度，精度损失很小 |
> | **推测解码（Speculative Decoding）** | 用小模型快速"猜"多个token，再用大模型并行验证，在不损失质量的情况下提升速度 |
> | **语义缓存（Semantic Cache）** | 缓存相似问题的答案，遇到语义相近的问题直接返回缓存结果，不调用LLM |
> | **vLLM** | 目前最流行的开源LLM推理引擎之一，内置PagedAttention、连续批处理、前缀缓存等优化 |

---

## 一、Tokenization算法

1. BPE（Byte Pair Encoding）最初于1994年作为数据压缩算法提出，2016年由Google引入NLP领域。
   - 来源：https://blog.csdn.net/sinat_20277079/article/details/153690408

2. BPE算法从所有单个字符开始，反复合并训练语料中出现频率最高的相邻字符对为子词，直到达到预设词汇表大小。
   - 来源：https://blog.csdn.net/polanpan/article/details/154489379

3. WordPiece算法选择合并token对的标准为最大化训练数据似然，而非单纯基于频率。
   - 来源：https://www.cnblogs.com/limingqi/p/18993211

4. SentencePiece是Google提出的通用分词工具包，支持BPE和Unigram LM两种算法，直接处理原始Unicode字符流，无需预分词。
   - 来源：https://adg.csdn.net/695331095b9f5f31781bbf2c.html

5. GPT系列（GPT-2/3/4）采用Byte-level BPE，词汇表大小为50257。
   - 来源：https://huggingface.co/transformers/v3.0.2/tokenizer_summary.html

6. BERT、DistilBERT、RoBERTa采用WordPiece算法，BERT词汇表大小为30522。
   - 来源：https://blog.truegeometry.com/api/exploreHTML/8e3464c2709d853c0a7ed8107039f3f3.exploreHTML

7. T5、PaLM、Mistral、Gemma、Phi-3采用SentencePiece框架，T5词汇表大小为32000。
   - 来源：https://rahatibnrafiq.github.io/llm_tokenizer/

8. LLaMA 3词汇表大小为128000，Gemini系列模型词汇表大小超过100000。
   - 来源：https://rahatibnrafiq.github.io/llm_tokenizer/

9. 英文文本平均1个token对应约4个字符或0.75个单词；中文文本平均1个汉字对应1-2个token。
   - 来源：https://aiwiki.ai/wiki/token

## 二、Transformer注意力机制

10. 标准自注意力机制时间复杂度为O(n²d)，其中n为序列长度，d为特征维度。
    - 来源：https://ask.csdn.net/questions/8923837

11. QK^T点积计算生成n×n注意力分数矩阵，共n²个元素，每个元素为两个d维向量的点积。
    - 来源：https://ask.csdn.net/questions/8923837

12. 序列长度为8000时，注意力计算涉及6400万次操作；序列长度为100万时，注意力计算涉及1万亿次操作。
    - 来源：https://podcasts.apple.com/hr/podcast/scaling-transformer-context-the-o-n-bottleneck/id1852646161?i=1000736525168

13. 序列长度4096时需计算超过1600万注意力分数；序列长度16384时需计算超过2.68亿注意力分数。
    - 来源：https://www.artificial-intelligence-wiki.com/ai-research/foundation-models-and-architectures/efficient-transformer-architectures/

14. n=32768时，存储n×n注意力矩阵（单精度浮点）占用约4GB显存。
    - 来源：https://ask.csdn.net/questions/8923837

## 三、上下文窗口与KV缓存

15. KV缓存在自回归生成阶段存储历史token的Key和Value向量，内存占用随序列长度线性增长，空间复杂度为O(n)。
    - 来源：https://arxiv.org/pdf/2509.00202v1

16. Llama 3.1-70B（FP16精度）单token KV缓存约2.5MB；8K上下文单请求KV缓存约20GB；batch size为32时总KV缓存约640GB。
    - 来源：https://introl.com/uk/blog/kv-cache-optimization-memory-efficiency-production-llms-guide

17. PagedAttention由UC Berkeley团队于2023年在SOSP会议提出，是vLLM推理引擎的核心技术。
    - 来源：https://arxiv.org/pdf/2309.06180

18. 传统KV缓存管理系统内存利用率为20.4%-38.2%；PagedAttention将KV缓存内存利用率提升至96%以上。
    - 来源：https://arxiv.org/pdf/2309.06180

19. PagedAttention借鉴操作系统虚拟内存分页思想，将KV缓存分割为固定大小的物理块（默认每块存储16个token），通过块表管理逻辑地址与物理地址映射。
    - 来源：https://www.jiangnengli.com/post/llm-infra-pagedattention/

20. PagedAttention实现Copy-on-Write（写时复制）机制，支持同源序列（共享前缀、并行采样、束搜索）间KV缓存块的共享。
    - 来源：https://arxiv.org/pdf/2309.06180

21. 输入处理阶段（Prefill）为计算密集型负载，可并行处理所有输入token；输出生成阶段（Decoding）为内存密集型负载，逐token顺序生成。
    - 来源：https://www.jiangnengli.com/post/llm-infra-pagedattention/

22. KV缓存内存计算公式：Memory = batch_size × seq_length × num_layers × 2 × hidden_dim × precision_bytes。
    - 来源：https://introl.com/uk/blog/kv-cache-optimization-memory-efficiency-production-llms-guide

## 四、Token计费模型

23. OpenAI GPT-5.6 Sol模型定价：输入$5.00/百万token，缓存输入$0.50/百万token，输出$30.00/百万token。
    - 来源：https://openai.com/api/pricing/

24. Anthropic Claude Opus 4.8模型定价：输入$5.00/百万token，缓存读取$0.50/百万token，输出$25.00/百万token；缓存写入收取溢价（5分钟缓存为1.25x输入价，1小时缓存为2x输入价）。
    - 来源：https://axiomstudio.ai/blog/ai-tokenomics-llm-token-costs-compared

25. Google Gemini 2.5 Pro模型定价（≤200K tokens）：输入$1.25/百万token，缓存读取约$0.13/百万token，输出$10.00/百万token；上下文缓存按小时收取存储费用。
    - 来源：https://axiomstudio.ai/blog/ai-tokenomics-llm-token-costs-compared

26. DeepSeek V4-Flash原厂直供定价：输入1元/百万token，输出2元/百万token，缓存命中0.02元/百万token。
    - 来源：https://cloud.tencent.com/document/product/1823/130055

27. 主流厂商输出token单价为输入token的3-8倍。
    - 来源：https://axiomstudio.ai/blog/ai-tokenomics-llm-token-costs-compared

28. OpenAI自动缓存机制无单独写入费用，缓存输入按输入价格的约10%计费。
    - 来源：https://axiomstudio.ai/blog/ai-tokenomics-llm-token-costs-compared

29. Batch API模式通常提供50%折扣，响应方式为24小时内异步处理。
    - 来源：https://openai.com/api/pricing/

30. Qwen3.5-Flash（0-128k）定价：输入0.2元/百万token，输出2元/百万token，缓存命中0.02元/百万token。
    - 来源：https://cloud.tencent.com/document/product/1823/130055
