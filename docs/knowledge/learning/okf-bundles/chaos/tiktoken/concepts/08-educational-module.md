---
type: Concept
title: 教学模块 SimpleBytePairEncoding
description: 拆解 _educational.py 的 SimpleBytePairEncoding 类与 bpe_encode/bpe_train/train_simple_encoding 纯 Python 复现，并与 Rust 生产 byte_pair_encode 对照，体会可读性优先 vs 性能优先
tags: [tiktoken, bpe, educational, train, encode, visualise, rust, comparison]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
sources:
  - id: tiktoken-source
    resource: "/references/source.md"
    title: tiktoken v0.14.0 源码信源登记
  - id: tiktoken-python
    resource: "/references/facts-python.md"
    title: Python 门面层事实清单
  - id: tiktoken-rust
    resource: "/references/facts-rust.md"
    title: Rust 核心事实清单
---

# 教学模块 SimpleBytePairEncoding

`tiktoken/_educational.py` 是一个**刻意不对外暴露**的独立教学模块——`__init__.py` 并未导入它的任何符号（facts-python F-003）。它用纯 Python，以最直白的方式复现 BPE 的**编码**与**训练**两个流程，并与 Rust 生产实现形成"可读性优先 vs 性能优先"的对照。学 BPE 的最佳路径，就是先读懂这个模块（facts 覆盖见 F-070~F-082），再对照 `/concepts/04-rust-core.md` 理解性能优化。

## SimpleBytePairEncoding 类

`SimpleBytePairEncoding`（facts-python F-070）只接受两个参数：`__init__(self, *, pat_str: str, mergeable_ranks: dict[bytes, int])`（F-070，keyword-only）。初始化时（F-071）：
- 保存 `self.pat_str` 与 `self.mergeable_ranks`；
- 构建反向解码器 `self._decoder = {token: token_bytes for token_bytes, token in mergeable_ranks.items()}`；
- 用 `regex.compile(pat_str)` 预编译 `self._pat`。

其方法面与生产 `Encoding` 一一对应，但签名与逻辑高度简化：

- **`encode(self, text, visualise="colour")`**（F-072）：用 `self._pat.findall(text)` 做正则预分词，对每个 word 执行 `word.encode("utf-8")` 后交给 `bpe_encode(self.mergeable_ranks, word_bytes, visualise=visualise)` 收集 token——预分词与 BPE 合并的职责划分，与生产实现（`_encode_only_native_bpe`，facts-python F-036）一致。
- **`decode_bytes(tokens)`**（F-073）：`b"".join(self._decoder[token] for token in tokens)`，逐 token 查表拼接为 `bytes`。
- **`decode(tokens)`**（F-074）：对 `decode_bytes` 结果执行 `.decode("utf-8", errors="replace")`。
- **`decode_tokens_bytes(tokens)`**（F-075）：逐 token 返回 `self._decoder[token]`，得到字节列表。
- **静态方法 `train(training_data, vocab_size, pat_str)`**（F-076）：调用模块级 `bpe_train(...)` 得到 `mergeable_ranks`，据此构造并返回一个 `SimpleBytePairEncoding`。
- **静态方法 `from_tiktoken(encoding)`**（F-077）：入参为 `str`（编码名）时先 `tiktoken.get_encoding(encoding)`，然后以生产 `Encoding` 的私有属性 `encoding._pat_str` 与 `encoding._mergeable_ranks` 构造教学实例——这是连接"真实词表"（/concepts/07-openai-vocabularies.md）与教学类的桥。

> 注意：通篇不存在 `SimpleBytePairDecoder` 类，本文件定义的类仅 `SimpleBytePairEncoding`（facts-python F-082）。

## 模块级函数：编码与训练

除去类方法，模块还有四个核心模块级函数，构成教学 BPE 的完整工具链。

### bpe_encode：贪心合并

`bpe_encode(mergeable_ranks, input, visualise="colour") -> list[int]`（facts-python F-078）复现推理期 BPE：
1. 把输入 `bytes` 按字节拆分为 `parts`；
2. 循环寻找**最低 rank** 的相邻 pair 合并（`mergeable_ranks.get(pair[0]+pair[1])`），无合并对时结束；
3. 当 `visualise` 取 `["colour","color"]` 时调用 `visualise_tokens(parts)` 可视化，取 `"simple"` 时 `print(parts)`；
4. 最终返回 `[mergeable_ranks[part] for part in parts]`。

注意其合并语义"每次先取 rank 最小的相邻 pair"——rank 小的 token 在训练中**更早**被合并，优先级更高，这是 BPE 解码应用 merge 规则的正确顺序。

### bpe_train：从语料学到词表

`bpe_train(data: str, vocab_size: int, pat_str: str, visualise="colour") -> dict[bytes, int]`（facts-python F-079）实现训练期 BPE：
1. **入口校验**：`vocab_size < 2**8` 时抛 `ValueError`——因为字节级 BPE 的基础词表固定为 256 个单字节；
2. **初始化 rank**：为 0-255 单字节建 rank（F-079，与"字节级 BPE 基础词表为 256 字节"的外部原理一致）；
3. **预分词**：用 `regex.findall(pat_str, data)` 把语料切词（F-079）；
4. **循环合并**：`while len(ranks) < vocab_size`，基于 `collections.Counter` 统计所有相邻 pair 的频次，取 `max` 得到 `most_common_pair`，作为新 token 加入，并合并所有 word 中的该 pair（F-079）。每轮恰好新增一个 token，直到达到 `vocab_size`。

这一"统计最高频相邻对 → 合并 → 重统计"的循环，正是 /concepts/03-bpe-tokenizer.md 所述 BPE 训练的标准贪心流程，但用最朴素的 `Counter` 与显式循环实现，便于逐行理解。

### visualise_tokens：ANSI 着色可视化

`visualise_tokens(token_values: list[bytes]) -> None`（facts-python F-080）用 ANSI 背景色序列为不同 token 着色打印，token 边界处用 `errors="replace"` 解码，结尾输出 `"\u001b[0m"` 复位颜色。它让学习者直观看到一句话被切成了哪些 token、每个 token 对应哪个字节片段。

### train_simple_encoding：自包含演示

`train_simple_encoding()`（facts-python F-081）内置一个 `gpt2_pattern` 正则，以 `with open(__file__)` 读取**本文件自身**作为训练语料，执行 `SimpleBytePairEncoding.train(data, vocab_size=600, pat_str=gpt2_pattern)` 训练一个 600 词素的编码，并用三条 assertion（含 `enc.decode(tokens) == "hello world"` 等）验证 roundtrip，最后返回该编码。这是一个零外部依赖、开箱即用的"从零学 BPE"演示入口。

## 与 Rust 生产实现对照

教学版的 `bpe_encode`（facts-python F-078）在语义上等价于 Rust 的 `byte_pair_encode`（facts-rust F-011）与 `_byte_pair_merge`（facts-rust F-009），而后者的注释明确记为 O(mn) work、`n` 通常很小。两者的关键差异在**工程取舍**：

| 维度 | 教学模块（纯 Python） | Rust 生产实现 |
|---|---|---|
| 合并查找 | `bpe_encode` 逐个 pair 探测最低 rank（F-078） | `_byte_pair_merge` 也朴素扫描（F-009），但对**长输入** `piece_len >= 100` 改走 `_byte_pair_merge_large` 的 `BinaryHeap<Merge>` 优化（facts-rust F-007） |
| 长度分派 | 无 | `byte_pair_encode` 按 `piece_len` 分派：`< 100` 走简单实现、否则走大输入实现（facts-rust F-011） |
| 解码器结构 | `self._decoder` 朴素 dict（F-071） | `CoreBPE` 分 `decoder`/`special_tokens_decoder` 双表（facts-rust F-020、F-029） |
| 线程/GIL | 无 | `py.detach` 释放 GIL（facts-rust F-038~F-039）、TLS 正则缓冲（facts-rust F-021~F-022） |

对比要点：**教学版只求"算法正确、可读、可可视化"**，甚至刻意不用任何生产期的 Rust 加速与线程机制；**生产版在正确性之外补齐性能机制**——大小输入分派、`BinaryHeap` 优先队列、TLS 正则缓冲、GIL 释放，全部详见 /concepts/04-rust-core.md。两者是同一算法在不同目标驱动下的两种实现，学习时"先读 `_educational.py` 理解算法本体，对照 `/concepts/04-rust-core.md` 理解性能优化"是最佳路径。

## 相关概念

- [/concepts/03-bpe-tokenizer.md](/concepts/03-bpe-tokenizer.md)：本模块复现的 BPE 算法与预分词原理。
- [/concepts/04-rust-core.md](/concepts/04-rust-core.md)：与教学实现对照的 Rust 生产实现与性能机制。
- [/concepts/07-openai-vocabularies.md](/concepts/07-openai-vocabularies.md)：`from_tiktoken` 所桥接的真实词表来源。