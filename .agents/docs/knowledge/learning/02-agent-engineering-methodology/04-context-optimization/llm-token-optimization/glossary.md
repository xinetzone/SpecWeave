---
id: "docs-knowledge-learning-llm-token-optimization-glossary"
title: "LLM Token 优化术语表"
category: "knowledge"
date: "2026-08-01"
---
# LLM Token 优化术语表

| 术语 | 英文 | 一句话解释 |
|------|------|-----------|
| Token | Token | LLM处理文本的基本单位，通常是子词或字符片段 |
| 字节对编码 | BPE (Byte Pair Encoding) | 一种数据压缩算法，在LLM中用于将文本拆分为子词单元的分词方法 |
| WordPiece | WordPiece | Google提出的分词算法，通过概率模型选择合并子词，用于BERT等模型 |
| SentencePiece | SentencePiece | 语言无关的分词工具，直接从原始文本训练子词单元，无需预分词 |
| Transformer | Transformer | 基于自注意力机制的深度学习架构，是现代大语言模型的基础 |
| 自注意力 | Self-Attention | Transformer中使序列内每个位置能够关注其他位置的机制，计算复杂度O(n²) |
| KV缓存 | KV Cache | 推理时缓存Key和Value矩阵以避免重复计算，显著加速自回归生成过程 |
| 分页注意力 | PagedAttention | vLLM提出的注意力机制，借鉴操作系统虚拟内存思想高效管理KV Cache |
| 检索增强生成 | RAG (Retrieval-Augmented Generation) | 通过检索外部知识库内容注入上下文，减少模型幻觉同时控制Token消耗 |
| 低秩适应 | LoRA (Low-Rank Adaptation) | 参数高效微调技术，仅训练低秩矩阵而非全模型，大幅降低微调成本 |
| 量化低秩适应 | QLoRA (Quantized LoRA) | LoRA的量化版本，在4/8bit量化模型上进行微调，进一步降低显存需求 |
| 投机解码 | Speculative Decoding | 使用小模型草稿、大模型验证的方式加速推理，不损失生成质量 |
| 提示词缓存 | Prompt Caching | 缓存系统提示词和前缀的KV Cache，避免重复计算相同前缀的注意力，也称自动前缀缓存(APC) |
| 首Token时间 | TTFT (Time To First Token) | 用户发送请求到收到第一个响应Token的时间延迟，衡量系统响应速度 |
| 每Token输出时间 | TPOT (Time Per Output Token) | 生成每个后续Token所需的平均时间，衡量生成吞吐量 |
| O(n²)复杂度 | O(n²) Complexity | 自注意力机制的时间/空间复杂度特性，序列长度翻倍计算量翻四倍 |
| 帕累托最优 | Pareto Optimal | 资源分配的理想状态，无法在不损害任一目标的前提下改善其他目标 |
| 语义缓存 | Semantic Cache | 基于语义相似度而非精确匹配的缓存机制，可命中相似问题的缓存结果 |
| 闪存注意力 | Flash Attention | IO感知的注意力算法，通过分块计算减少GPU内存访问，提升注意力计算速度 |
| 分组查询注意力 | GQA (Grouped-Query Attention) | Multi-Query Attention的泛化，将Query分组共享KV头，平衡速度与效果 |
| 滑动窗口注意力 | SWA (Sliding Window Attention) | 每个Token仅关注固定大小窗口内的历史Token，将长序列注意力复杂度降至O(n) |
| 上下文窗口 | Context Window | LLM单次推理能够处理的最大Token数量限制，决定了可输入文本长度 |
| 系统提示词 | System Prompt | 用于设定模型行为、角色、规则的特殊提示，在会话中持续生效 |
| 少样本学习 | Few-shot | 在提示中提供少量示例引导模型输出，无需微调即可完成特定任务 |
| 思维链 | CoT (Chain of Thought) | 提示技术，引导模型逐步展示推理过程，显著提升复杂推理任务准确率 |
| 知识蒸馏 | Distillation | 将大模型（教师模型）的知识迁移到小模型（学生模型）的模型压缩技术 |
| 量化 | Quantization | 将模型参数从高精度（FP32/FP16）转换为低精度（INT8/INT4）以减少内存和计算量 |
| 剪枝 | Pruning | 移除模型中不重要的参数或连接，在最小精度损失下减小模型体积 |
| Map-Reduce | Map-Reduce | 分布式处理范式，在长上下文处理中用于分块处理后聚合结果 |
| 分块 | Chunking | 将长文本拆分为固定或动态大小的块以适应上下文窗口限制的处理技术 |
| 重排序 | Reranker | 对检索结果进行二次排序的模型，提升检索相关性和最终生成质量 |
| 连续批处理 | Continuous Batching | vLLM等推理引擎采用的批处理技术，动态组合请求实现高GPU利用率（80-95%） |
| 自动前缀缓存 | APC (Automatic Prefix Caching) | 推理引擎自动识别并缓存相同前缀的KV缓存，无需应用层手动配置 |
| 黄金测试集 | Golden Test Set | 用于评估优化前后质量变化的标准测试数据集，覆盖典型场景和边缘case |
| 任务准确率保持率 | ARR (Accuracy Retention Rate) | 优化后任务准确率相对于基线的保留比例，是质量护栏核心指标 |
| 优化反弹 | Optimization Bounce | 优化上线后随着业务变化、提示词修改、模型更新，成本悄悄涨回优化前水平的现象 |
| 概念操作化三层递进 | Concept Operationalization | 将复杂概念分解为入门（识别问题）→深入（掌握方法）→精通（内化为直觉）三个学习层次 |
| 约束驱动设计 | Constraint-Driven Design | 通过"负面清单"划定不可逾越边界，在边界内给予最大自主空间的设计方法 |
| 前台-后台分离 | Frontend-Backend Separation | 文档撰写原则：后台文档完整冗余可执行，前台文档压缩提炼3分钟可感知 |
| ROI | ROI (Return on Investment) | 投资回报率，衡量优化投入的人力时间相对于成本节省的回收周期 |
| A/B测试 | A/B Testing | 将流量分组对照实验，科学衡量优化对质量/成本/延迟的影响 |

---
<!-- created on 2026-08-01 -->
