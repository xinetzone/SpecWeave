---
type: Concept
title: BPE 分词与预切分
description: BPE 字节对编码算法的两个阶段（预分词与合并）在 tiktoken 中的落点——pat_str 正则切分、mergeable_ranks 合并与特殊 token 的双轨处理
tags: [tiktoken, bpe, tokenizer, 预切分, 正则, special-token]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
sources:
  - id: tiktoken-python
    resource: /references/facts-python.md
    title: Python 门面层事实清单
  - id: tiktoken-rust
    resource: /references/facts-rust.md
    title: Rust 核心事实清单
  - id: tiktoken-background
    resource: /references/background-research.md
    title: BPE 分词技术与外部背景
---

# BPE 分词与预切分

BPE（Byte Pair Encoding，字节对编码）分词由两个阶段组成：**正则预分词**把文本切成一连串"词/piece"，**字节级 BPE 合并**再在每个 piece 内部把相邻字节/子 token 合并成词表中的 token。在 tiktoken 中，这两个阶段分处于 Python 与 Rust 两层，特殊 token（special token）则由另一套独立的双轨逻辑处理。

## BPE 算法原理

BPE 是一种贪心子词算法，反复执行一个操作：找到当前序列中**秩（rank）最低的相邻 token 对**，将其合并为一个 token，直到不能再合并（[背景调研](/references/background-research.md)）。tiktoken 采用字节级 BPE（byte-level BPE），基础 token 是 256 个字节，因此对任意 Unicode 输入都不会出现未登录词。

任何一个 `Encoding` 的 token 空间由三元组刻画（[02 Encoding 对象核心 API](/concepts/02-encoding-api.md)）：

- `pat_str`：正则，定义预分词规则；
- `mergeable_ranks: dict[bytes, int]`：可合并的 BPE 字节 token 到秩（rank）的映射；
- `special_tokens: dict[str, int]`：特殊 token 字符串到 token id 的映射。

## 阶段一：正则预分词（pat_str 切分）

预分词用给定模式 `pat_str` 把一段文本切成多个 piece。tiktoken 预分词发生在**两层**：

- **Python 侧**：私有方法 `_encode_only_native_bpe(text)`（F-036）函数体内 `import regex`、`regex.compile(self._pat_str)` 编译正则，再 `for piece in regex.findall(...)` 逐个 piece 调用 `self._core_bpe.encode_single_piece(piece.encode("utf-8"))`——即切分本身在 Python 侧完成。
- **Rust 侧**：`CoreBPE.encode_ordinary`/`encode` 内部用 `regex.find_iter` 遍历做同样的预分词（facts-rust F-024/F-025）。

各编码的 `pat_str` 来源不一：`gpt2`/`r50k_base`/`p50k_base`/`p50k_edit` 共享常量 `r50k_pat_str`（F-085），例如：

```
'(?:[sdmt]|ll|ve|re)| ?\p{L}++| ?\p{N}++| ?[^\s\p{L}\p{N}]++|\s++$|\s+(?!\S)|\s
```

而 `cl100k_base` 使用独立定义的一行正则，`o200k_base`/`o200k_harmony` 则由 7 个子正则 `"|".join` 拼成，覆盖大写字母/数字/标点/换行/空白等分支（F-090/F-091，详见 [05 Registry 对应的词表演进](/concepts/05-registry-model.md)）。

## 阶段二：字节级 BPE 合并

预分词产出的每个 piece 交给 BPE 合并逻辑，在 piece 内部按秩贪心合并得到最终 token 序列。Rust 侧合并算法的入口为 `byte_pair_encode(piece, ranks)`（facts-rust F-011），它依据 piece 长度做大小输入分派：

- `piece_len == 1`：直接返回 `vec![ranks[piece]]`；
- `piece_len < 100`：调用简单 O(mn) 实现 `_byte_pair_merge`（facts-rust F-009，注释记为 O(mn) work，n 通常很小）——按字节切片、循环寻找最低秩相邻对合并；
- 否则：调用用 `BinaryHeap`（最大堆）优化的 `_byte_pair_merge_large`（facts-rust F-007），适用于长 piece 的高效合并。

合并的贪心准则体现在 `Merge` 结构的 `Ord` 实现：先按 rank 升序、平局再按 start 升序弹出（facts-rust F-005），直至遇到 `Rank::MAX` 哨兵（facts-rust F-008）。字节级看法：`_byte_pair_merge` 按 `piece[i..i+2]` 的字节切片查表（facts-rust F-009），而非 token 序号对。

> 教学对照：`_educational.py` 的 `SimpleBytePairEncoding`（非公开 API，F-003）用纯 Python 复现了这一贪心合并（`bpe_encode`，F-078），并支持逐步可视化，是理解 BPE 算法本体的最佳入门（[00 整体架构](/concepts/00-overview.md)）。

## 特殊 token 双轨处理

特殊 token（如 `<|endoftext|>`）是词表中独立于 mergeable 的一类 token id。tiktoken 对它们的处理采用"Python 预检 + Rust 匹配"的双轨机制：

- **Python 预检层**：`encode` 的参数 `allowed_special`（默认空集）与 `disallowed_special`（默认 `"all"`）决定策略（F-015）。`disallowed_special == "all"` 时展开为 `special_tokens_set - allowed_special`；非空时用 `_special_token_regex(disallowed_special).search(text)`（F-004，基于 `re.escape` + `|` 拼接编译）检查文本，命中则调用 `raise_disallowed_special_token` 抛 `ValueError`（F-005）。
- **Rust 匹配层**：`CoreBPE.encode` 内部先构建 `special_regex`（在 `new_internal` 中用 `fancy_regex::escape` 对每个特殊 token key 转义后 `|` join，facts-rust F-029），再用 `special_regex.find_from_pos` 定位允许的特殊 token，普通片段走 `regex.find_iter` 分词（facts-rust F-025）。

行为约束（facts-rust F-061）：

```python
enc = tiktoken.get_encoding("gpt2")
enc.encode("<|endoftext|>")                    # disallowed_special 默认 "all" → ValueError
enc.encode("<|endoftext|>", allowed_special="all")   # [50256]，特殊 token 进入结果
enc.encode("<|endoftext|>", disallowed_special=())   # 特殊 token 不进入结果
```

## 相关概念

- [02 Encoding 对象核心 API](/concepts/02-encoding-api.md)：`encode` 与特殊 token 参数的接口签名
- [04 Rust 核心 CoreBPE 与性能](/concepts/04-rust-core.md)：`byte_pair_encode`/`_byte_pair_merge` 的底层实现
- [05 注册表与模型映射](/concepts/05-registry-model.md)：各编码 `pat_str` 的定义来源
- 外部背景：[BPE 技术背景](/references/background-research.md)
- 事实来源：[Python 事实清单](/references/facts-python.md)、[Rust 事实清单](/references/facts-rust.md)