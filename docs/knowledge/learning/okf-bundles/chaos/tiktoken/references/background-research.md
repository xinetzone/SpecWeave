---
type: Background
title: BPE 分词技术与 tiktoken 外部背景
description: tiktoken/BPE 分词技术的外部背景研究：算法原理、词汇体系演进、token 计数实践（辅助理解用，非源码事实）
tags: [tiktoken, bpe, tokenizer, background, research]
generated: { by: deep-research, at: 2026-08-25T00:00:00Z }
verified: { by: deep-research, at: 2026-08-25T00:00:00Z }
status: draft
stale_after: 2027-08-25
source_id: tiktoken-background
---

# BPE 分词技术与 tiktoken 外部背景

> 本文是 **外部背景知识**，用于辅助理解 OpenAI `tiktoken` 库所处的生态与技术语境，**不涉及 tiktoken 内部具体 API 的虚构实现**。文中提及的公开接口名（如 `get_encoding`、`encoding_for_model`、`Encoding.encode`/`decode`）均为开源公开文档中真实存在者。所有关键信息来源均已标注。

## 执行摘要

- BPE 是现代 LLM（GPT、Llama、Mistral、Gemma、Claude 等）最主流的子词分词算法，由数据压缩算法改编而来，GPT-2 将其确立为标准。
- OpenAI 通过 tiktoken 发布多套分词编码体系：`gpt2`/`r50k_base`（约 5 万词表）→ `p50k_base`（代码优化）→ `cl100k_base`（10 万词表，ChatGPT/GPT-4）→ `o200k_base`（20 万词表，GPT-4o/o1/GPT-5 系列），词表持续扩张以提升多语言与数字处理能力。
- token 计数直接决定 API 计费与上下文窗口可用性；英文平均约 1 token ≈ 4 字符 ≈ 0.75 词，不同语言差异显著。
- 性能上 tiktoken 通常显著快于 HuggingFace `tokenizers`（2–6 倍量级），并催生了 GPU/SIMD 加速的进一步优化方向。

## BPE（Byte Pair Encoding）算法原理

### 起源与沿革

- BPE 最初由 Philip Gage 于 **1994 年** 提出，是一项**无损数据压缩**算法：扫描数据中最频繁出现的相邻字节对，用一个未占用的字节值替换，并记录替换表（来源：[aiwiki Byte-Pair Encoding](https://aiwiki.ai/wiki/byte_pair_encoding)；[github.com/maraja/llm-concepts byte-pair-encoding.md](https://github.com/maraja/llm-concepts/blob/main/02-input-representation/byte-pair-encoding.md)）。
- **2015/2016 年** Sennrich、Haddow、Birch 在论文《Neural Machine Translation of Rare Words with Subword Units》（arXiv:1508.07909）中将其引入神经机器翻译，用于解决**开放词表（open-vocabulary）** 与生词/OOV 问题（来源：[aiwiki Byte-Pair Encoding](https://aiwiki.ai/wiki/byte_pair_encoding)；[hugging-face.cn LLM 课程 BPE 分词](https://hugging-face.cn/learn/llm-course/chapter6/5)）。
- **GPT-2（2019）** 引入 **字节级 BPE（byte-level BPE）**，使基础词表固定为 256 个字节，从而对任意 Unicode 字符都不会出现未知标记（来源：[hugging-face.cn LLM 课程](https://hugging-face.cn/learn/llm-course/chapter6/5)；[blogcode.vn BPE 分词](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)）。此后 BPE 成为前沿模型的主流选择（来源：[web.stanford.edu CS224N 分词课程](https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-guest-julie-tokenization-multilinguality.pdf)）。

### 核心思想与训练过程

BPE 是一种**贪心（greedy）** 子词分词算法，只重复一个操作：反复寻找语料中**出现频率最高的相邻 token 对**，将其合并为一个新 token，直到词表达到目标大小。每一个 merge 步骤恰好新增一个 token（来源：[blogcode.vn BPE 分词](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)；[github.com/lamdaz LLMs-from-scratch bpe-from-scratch.ipynb](https://github.com/lamdaz/LLMs-from-scratch/blob/main/ch02/05_bpe-from-scratch/bpe-from-scratch.ipynb)）。

训练流程（来源：[hugging-face.cn LLM 课程 BPE](https://hugging-face.cn/learn/llm-course/chapter6/5)；[github.com/maraja byte-pair-encoding.md](https://github.com/maraja/llm-concepts/blob/main/02-input-representation/byte-pair-encoding.md)）：

1. 归一化（normalization）；
2. 预分词（pre-tokenization，通常用正则按空白/标点切分）；
3. 将每个词拆成单个字符（或字节）；基础词表为 256 个字节（字节级 BPE）；
4. 统计语料中所有相邻对的出现频次，将最高频对合并为新 token，记录合并规则 `(a, b) -> ab`；
5. 重复直至达到目标词表大小（如 5 万/10 万/20 万）。

编码（inference）时按训练顺序应用已学到的 merge 规则即可（来源：[github.com/maraja byte-pair-encoding.md](https://github.com/maraja/llm-concepts/blob/main/02-input-representation/byte-pair-encoding.md)；[blogcode.vn BPE 分词](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)）。示例：GPT-2 把 `"This is some text"` 17 个字符分词为 `1212, 318, 617, 2420` 共 4 个 token（来源：[github.com/willseu LLMs-from-scratch](https://github.com/willseu/LLMs-from-scratch/blob/main/ch02/05_bpe-from-scratch/bpe-from-scratch.ipynb)）。

### 与其他方案对比

- **字符级分词**：序列极长，自注意力成本随序列长度**二次方**增长；**词级分词**：词表爆炸且无法处理未见词（OOV）。BPE 以可变的子词粒度在二者间取平衡：高频词成为单一 token，稀有/陌生串分解为已知子词，任何输入都不会真正越界（来源：[aiwiki Byte-Pair Encoding](https://aiwiki.ai/wiki/byte_pair_encoding)；[crazyrouter.com Tokens vs Bytes](https://crazyrouter.com/en/blog/tokens-vs-bytes-what-llms-actually-see)）。
- 词表大小 `|V|` 是控制分词粒度的关键超参数，直接影响序列长度与输入嵌入矩阵规模（来源：[web.stanford.edu CS224N](https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-guest-julie-tokenization-multilinguality.pdf)；[github.com/maraja byte-pair-encoding.md](https://github.com/maraja/llm-concepts/blob/main/02-input-representation/byte-pair-encoding.md)）。
- 其他子词算法包括 UnigramLM（来源：[arXiv:2508.04796 Parity-Aware BPE](https://arxiv.org/pdf/2508.04796)）、WordPiece、SentencePiece（来源：[blogcode.vn BPE 分词](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)）。
- 跨语言公平性方面，标准 BPE 的频率目标倾向于语料中的高资源语言，导致低资源语言 token 数更多、成本更高；研究提出 Parity-Aware BPE 等变体进行缓解（来源：[arXiv:2508.04796](https://arxiv.org/pdf/2508.04796)）。

## OpenAI tokenizer 词汇体系（tiktoken 编码）

tiktoken 是 OpenAI 于 **2022 年 12 月** 开源的 BPE 分词库，用 Rust（PyO3 绑定）编写，打包了各模型的精确 merge 表，README 定位为"a fast BPE tokeniser for use with OpenAI's models"（来源：[aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)）。

tiktoken 公开分发的编码体系（词汇表数据见 tiktoken 源码 `tiktoken_ext/openai_public.py`，来源：[github.com/openai/tiktoken openai_public.py](https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py)）：

| 编码名称 | 词表大小 | 发布时间/背景 | 适用模型 |
| --- | --- | --- | --- |
| `gpt2` | 50,257 | 2019，GPT-2 | GPT-2 |
| `r50k_base`（别名 gpt2） | 50,257 | GPT-3 早期 | GPT-3 系列（davinci/curie/babbage/ada） |
| `p50k_base` | 50,281 | ~2021，Codex | text-davinci-002/003、code-davinci-002 等 |
| `p50k_edit` | 50,284 | 编辑模型 | text/code-davinci-edit-001，支持 FIM |
| `cl100k_base` | 100,256（含特殊 token 后总计约 100,277） | 2022 | GPT-3.5/GPT-4、text-embedding-ada-002 等 |
| `o200k_base` | 约 200,000 | 2024 | GPT-4o、GPT-4.1、o1、o3、GPT-5 等 |
| `o200k_harmony` | 201,088 | 2024 | GPT-5 with tools（额外工具特殊 token） |

主要来源交叉核对：[aiwiki tiktoken 编码表](https://www.aiwiki.ai/wiki/tiktoken)、[CSDN tiktoken 编码格式全解析](https://blog.csdn.net/gitblog_00111/article/details/151169854)、[github.com/openai/tiktoken openai_public.py](https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py)、[metehan.ai GPT-5 Tokenizer 逆向](https://metehan.ai/blog/reverse-engineering-the-gpt-5-tokenizer-aeo-geo/)、[Z. Cheng《Every Token of cl100k_base in tiktoken》](https://raw.githubusercontent.com/chengmarc/every-token/main/paper/every_token.pdf)。

演进关系简述：

- `gpt2` 与 `r50k_base` 关系紧密：tiktoken 称 r50k_base 为 gpt2 的别名，二者词表与正则模式一致（来源：[aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)；[开发文档 OpenAI Cookbook 计数 token](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)）。
- `p50k_base` 与 `r50k_base` 显著重叠，非代码场景下通常产出相同 token（来源：[开发文档 OpenAI Cookbook](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)）。
- `cl100k_base` 相对 r50k 词表翻倍，对多语言与数字序列着墨更多，社区初次见到即注意到数值序列专用 token（来源：[aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)）。
- `o200k_base` 词表再翻倍，采用对 camelCase 更友好的正则，并优化非英语语言与 URL/brand 单 token 化（来源：[metehan.ai GPT-5 Tokenizer 逆向](https://metehan.ai/blog/reverse-engineering-the-gpt-5-tokenizer-aeo-geo/)；[blogcode.vn BPE 分词](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)）。

特殊 token 示例（真实存在，来源：[github.com/openai/tiktoken openai_public.py](https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py)）：`<|endoftext|>`、`<|fim_prefix|>`、`<|fim_middle|>`、`<|fim_suffix|>`、`<|endofprompt|>`。这些 ID 分配在 mergeable token 之上。

## GPT 系列分词器演进

| 阶段 | 模型 | 编码 | 关键变化 | 来源 |
| --- | --- | --- | --- | --- |
| GPT-2（2019） | GPT-2 | `gpt2`（字节级 BPE） | 以 256 字节为基础词表，消除 Unicode OOV | [blogcode.vn](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)；[hugging-face.cn](https://hugging-face.cn/learn/llm-course/chapter6/5) |
| GPT-3（2020） | GPT-3 | `r50k_base`（约 50k） | 沿用 GPT-2 算法思路，词表 50,257 | [aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)；[blogcode.vn](https://blogcode.vn/series/ai-llm-genai/bpe-encoding) |
| Codex（~2021） | Codex | `p50k_base`/`p50k_edit` | 代码优化，p50k_edit 支持 FIM | [aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)；[CSDN](https://blog.csdn.net/gitblog_00111/article/details/151169854) |
| ChatGPT/GPT-4（2022–2023） | GPT-3.5/GPT-4 | `cl100k_base`（约 100k） | 词表翻倍，多语言与数字处理更强 | [aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)；[开发文档 OpenAI Cookbook](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/) |
| o1/GPT-4o/GPT-5（2024+） | GPT-4o/o1/GPT-4.1/GPT-5 | `o200k_base`（约 200k） | 词表翻倍，camelCase 正则，非英语优化 | [metehan.ai 逆向](https://metehan.ai/blog/reverse-engineering-the-gpt-5-tokenizer-aeo-geo/)；[aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken) |

补充说明：

- 一份 AI 逆向分析认为 o200k_base 具体词表数为 **200,019**，且 200k token 中把 Google、Amazon、Reddit 等品牌名做成单一 token（来源：[metehan.ai GPT-5 Tokenizer 逆向](https://metehan.ai/blog/reverse-engineering-the-gpt-5-tokenizer-aeo-geo/)）。
- BPE 不仅是 OpenAI 的选择，也是 Llama 3 等所用 tokenizer 的基础；多位作者指出 Llama 3 训练即采用（GPT-4 风格的）tiktoken tokenizer（来源：[github.com/willseu LLMs-from-scratch](https://github.com/willseu/LLMs-from-scratch/blob/main/ch02/05_bpe-from-scratch/bpe-from-scratch.ipynb)；[github.com/maraja llm-concepts](https://github.com/maraja/llm-concepts/blob/main/02-input-representation/byte-pair-encoding.md)）。

## token 计数的实践

### 为什么按 token 计费、与字符/字节的关系

- LLM 不直接读字符或词，而是读取来自固定词表的**整数 token 序列**；因此 token 数是衡量上下文占用与 API 成本的核心单位。tiktoken 是 OpenAI 官方 cookbook 推荐的计数工具（来源：[aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)；[开发文档 OpenAI Cookbook 计数 token](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)）。
- OpenAI 官方经验值（英文）：**1 token ≈ 4 字符 ≈ ¾ 词**；100 tokens ≈ 75 词；约 1500 词 ≈ 2048 tokens（来源：[help.openai.com What are tokens and how to count them](https://help.openai.com/en/articles/4936856-what-are-rate-limits)）。
- 字节层面通常平均 1 token ≈ 4 字节量级，但按语言差异显著（来源：[crazyrouter.com Tokens vs Bytes](https://crazyrouter.com/en/blog/tokens-vs-bytes-what-llms-actually-see)）：

| 语言 | 示例 | Tokens | Bytes | Bytes/Token |
| --- | --- | --- | --- | --- |
| English | "Hello, how are you today?" | 7 | 25 | ~3.6 |
| Chinese | "你好，今天怎么样？" | 5 | 27 | ~5.4 |
| Japanese | "こんにちは" | 1 | 15 | ~15.0 |

- 4 字符规则适用于干净英文；对**代码/JSON**（约 3.3 字符/token）、**CJK/阿拉伯/印地/泰文**（UTF-8 下多为每字 3 字节，常约 1 token 对应 2–3 字符）、**长数字**（在异常边界切分）时偏差明显（来源：[calculatormatics.com Token Counter](https://calculatormatics.com/tech/token-counter/)）。

### 计费与上下文

- API 按 token 计费，区分输入（input）、输出（output）、缓存（cached）、推理（reasoning）token；输出 token 通常比输入贵得多（来源：[help.openai.com](https://help.openai.com/en/articles/4936856-what-are-rate-limits)；[github.com/LDLoeb LLM_COST_GUIDE.md](https://github.com/LDLoeb/AgenticAI_foundry/blob/main/docs/LLM_COST_GUIDE.md)）。
- 每套模型有最大上下文（input+output）token 上限，超出则需截断/分块或精简 prompt（来源：[help.openai.com](https://help.openai.com/en/articles/4936856-what-are-rate-limits)）。
- token 在不同模型/厂商间不通用：同一文本在不同 tokenizer 下 token 数不同，因此宣称的价格不能只按 100 万 token 单价比较，还要看总 token 数与"每个成功结果"的成本（来源：[help.openai.com](https://help.openai.com/en/articles/4936856-what-are-rate-limits)；[calculatormatics.com](https://calculatormatics.com/tech/token-counter/)）。

### tiktoken 公开接口（仅列举公开且真实存在者）

- `tiktoken.get_encoding(name)`：按编码名加载，如 `cl100k_base`（来源：[开发文档 OpenAI Cookbook](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)；[CSDN](https://blog.csdn.net/gitblog_00111/article/details/151169854)）。
- `tiktoken.encoding_for_model(model)`：按模型名取编码，如 `encoding_for_model('gpt-4o-mini')`（来源：[开发文档 OpenAI Cookbook](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)；[help.openai.com](https://help.openai.com/en/articles/4936856-what-are-rate-limits)）。
- 编码对象上的 `encode`/`decode` 方法分别把文本转 token ID、把 ID 序列转回文本（来源：[开发文档 OpenAI Cookbook](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)）。
- 交互式工具：[platform.openai.com/tokenizer](https://platform.openai.com/tokenizer)、[tiktokenizer.vercel.app](https://tiktokenizer.vercel.app/)（来源：[metehan.ai 逆向](https://metehan.ai/blog/reverse-engineering-the-gpt-5-tokenizer-aeo-geo/)；[github.com/lamdaz LLMs-from-scratch](https://github.com/lamdaz/LLMs-from-scratch/blob/main/ch02/05_bpe-from-scratch/bpe-from-scratch.ipynb)）。

## tiktoken 与 HuggingFace tokenizers 等替代方案的性能背景

- **tiktoken README**：宣称对 1 GB 文本分词时，比同类开源 tokenizer（如 HuggingFace GPT2TokenizerFast）快 **3–6 倍**（来源：[aiwiki tiktoken 引用 tiktoken README](https://www.aiwiki.ai/wiki/tiktoken)）。
- **独立基准**（machinelearningplus）：tiktoken 相对 HuggingFace tokenizers 稳定快约 **2–3 倍**。原因在于 tiktoken 只跑 BPE 就停止，而 HuggingFace 执行完整链条"normalize → pre-split → BPE"（来源：[machinelearningplus.com tiktoken vs HuggingFace Tokenizers Benchmark](https://machinelearningplus.com/gen-ai/tiktoken-vs-huggingface-tokenizers/)）。需注意这是一个热门的网络基准，非官方权威数据。
- **GPU/SIMD 加速方向**：
  - GPUTOK（GPU 字节级 BPE）：在最长输入（13 万 token）下优化 GPU kernel 比 tiktoken 快约 **1.7×**、比 HuggingFace GPT-2 tokenizer 快约 **7.6×**（来源：[arXiv:2603.02597 GPUTOK](https://arxiv.org/pdf/2603.02597)）。
  - GigaToken（SIMD 预分词替代正则）：宣称最高约 1000×，其测试表中 tiktoken 约 36 MB/s、HuggingFace 约 25 MB/s 量级（来源：[dev.to Every Word I Say Gets Tokenized](https://dev.to/hermestomagent/every-word-i-say-gets-tokenized-this-library-does-it-1000x-faster-1kch)）。该数为厂商宣传，需谨慎对待。
  - tokie（chonkie-inc）：对 cl100k/o200k 若干用例比 tiktoken 快数倍（如 o200k 45KB 文本快约 7.9×）（来源：[github.com/chonkie-inc/tokie](https://github.com/chonkie-inc/tokie)）。
- 其他语言生态：o200k/cl100k/p50k 有 C#（SharpToken/TiktokenSharp）、Java（jtokkit）、Go（tiktoken-go）、Rust（tiktoken-rs）等移植；r50k(gpt2) 另有 JS（gpt-3-encoder）等多语言实现（来源：[开发文档 OpenAI Cookbook 各类库](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)）。
- 使用面：LangChain、LlamaIndex 默认以 `cl100k_base` 作为 token 计数器，tiktoken 已成为衡量 OpenAI token 数的事实标准（来源：[aiwiki tiktoken](https://www.aiwiki.ai/wiki/tiktoken)）。

## 综合来源清单

1. [tiktoken 官方源码 openai_public.py（编码/词表/特殊 token）](https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py)
2. [开发文档 OpenAI Cookbook：How to count tokens with Tiktoken（编码-模型映射与接口）](https://developers.openai.com/cookbook/examples/how_to_count_tokens_with_tiktoken/)
3. [help.openai.com：What are tokens and how to count them（4 字符规则、计费）](https://help.openai.com/en/articles/4936856-what-are-rate-limits)
4. [aiwiki：tiktoken（发布、编码表、性能、生态）](https://www.aiwiki.ai/wiki/tiktoken)
5. [HuggingFace LLM 课程（中文）：字节对编码 BPE 分词（训练/编码算法）](https://hugging-face.cn/learn/llm-course/chapter6/5)
6. [aiwiki：Byte-Pair Encoding（历史沿革）](https://aiwiki.ai/wiki/byte_pair_encoding)
7. [maraja/llm-concepts：Byte-Pair Encoding（BPE 步骤与词表作用）](https://github.com/maraja/llm-concepts/blob/main/02-input-representation/byte-pair-encoding.md)
8. [Stanford CS224N 分词课程（BPE 成为主流、模型词表对比）](https://web.stanford.edu/class/cs224n/slides_w26/cs224n-2026-guest-julie-tokenization-multilinguality.pdf)
9. [blogcode.vn：BPE(token hóa của GPT)（历史、vocab 表、o200k）](https://blogcode.vn/series/ai-llm-genai/bpe-encoding)
10. [metehan.ai：Reverse-Engineering the GPT-5 Tokenizer（o200k 逆向、词表数 200,019）](https://metehan.ai/blog/reverse-engineering-the-gpt-5-tokenizer-aeo-geo/)
11. [Z. Cheng：Every Token of cl100k_base in tiktoken（cl100k 约 100,277 token）](https://raw.githubusercontent.com/chengmarc/every-token/main/paper/every_token.pdf)
12. [crazyrouter.com：Tokens vs Bytes（按语言 bytes/token）](https://crazyrouter.com/en/blog/tokens-vs-bytes-what-llms-actually-see)
13. [calculatormatics.com：Token Counter（4 字符规则的适用与失效场景）](https://calculatormatics.com/tech/token-counter/)
14. [machinelearningplus.com：tiktoken vs HuggingFace Tokenizers（2–3× 基准）](https://machinelearningplus.com/gen-ai/tiktoken-vs-huggingface-tokenizers/)
15. [arXiv:2603.02597 GPUTOK（GPU 加速，对比 tiktoken/HF）](https://arxiv.org/pdf/2603.02597)
16. [arXiv:2508.04796 Parity-Aware BPE（跨语言公平性）](https://arxiv.org/pdf/2508.04796)
17. [CSDN：tiktoken 编码格式全解析（编码表与应用模型）](https://blog.csdn.net/gitblog_00111/article/details/151169854)
18. [github.com/chonkie-inc/tokie（比 tiktoken 更快）](https://github.com/chonkie-inc/tokie)
19. [dev.to：GigaToken（SIMD 加速与对比数据）](https://dev.to/hermestomagent/every-word-i-say-gets-tokenized-this-library-does-it-1000x-faster-1kch)
20. [rasbt/willseu LLMs-from-scratch bpe-from-scratch（GPT-2 示例、tiktoken 性能优势、Llama 3 用 GPT-4 tokenizer）](https://github.com/willseu/LLMs-from-scratch/blob/main/ch02/05_bpe-from-scratch/bpe-from-scratch.ipynb)

## 研究空白与注意点

- tiktoken 各编码的**精确词表总数存在口径差异**（如 cl100k 常见口径 100,256 mergeable、含特殊 token 后约 100,277；o200k 常见口径 200,000、逆向约 200,019），引用时需注明口径。
- 性能对比数据来源分散（README 3–6×、第三方 2–3×、GPU/SIMD 方案 1.7×~1000×），且部分为厂商宣传，应视为量级参考而非权威标准。
- BPE 按 token 计费的实践对低资源语言的经济代价、以及 tokenizer 设计对模型行为的间接影响（如 glitch tokens、数字切分）仍属活跃研究领域。