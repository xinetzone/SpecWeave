---
type: Concept
title: OpenAI 公开词汇体系
description: 归纳 tiktoken_ext/openai_public.py 七个公开编码构造函数，对比 gpt2/r50k_base/p50k_base/cl100k_base/o200k_base 四代词表的规模、特殊 token、正则分化
tags: [tiktoken, bpe, openai, vocabularies, r50k, p50k, cl100k, o200k, encoding]
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
  - id: tiktoken-background
    resource: "/references/background-research.md"
    title: BPE 分词技术与外部背景
---

# OpenAI 公开词汇体系

tiktoken 的价值不仅在于一个高性能 BPE 实现，更在于它随包一并封装了 OpenAI 各代模型所用的**精确词表**。这些词表的定义全部集中在插件包 `tiktoken_ext/openai_public.py`，由七个构造函数对外声明，并经 `ENCODING_CONSTRUCTORS` 注册表纳入 `registry`（/concepts/05-registry-model.md）的惰性加载机制。读懂这一文件，就摸清了 tiktoken 覆盖的 OpenAI 词汇体系全貌。

## 七个构造函数与特殊 token 常量

文件首行 `from tiktoken.load import data_gym_to_mergeable_bpe_ranks, load_tiktoken_bpe`（facts-python F-083），复用加载层（/concepts/06-encoder-loading.md）的两种解析器。

### 特殊 token 常量

文件顶部定义五个共享常量（facts-python F-084）：

| 常量 | 字符串值 |
|---|---|
| `ENDOFTEXT` | `<|endoftext|>` |
| `FIM_PREFIX` | `<|fim_prefix|>` |
| `FIM_MIDDLE` | `<|fim_middle|>` |
| `FIM_SUFFIX` | `<|fim_suffix|>` |
| `ENDOFPROMPT` | `<|endofprompt|>` |

其中 FIM 前缀指 fill-in-the-middle（代码补全上下文拼接）语义；这些 token 的 id 都分配在 mergeable token 之上。

### 七个构造函数

| 构造函数 | `pat_str` | special_tokens | 备注 |
|---|---|---|---|
| `gpt2()` | `r50k_pat_str` | `{ENDOFTEXT: 50256}` | data-gym 双文件；`explicit_n_vocab=50257` |
| `r50k_base()` | `r50k_pat_str` | `{ENDOFTEXT: 50256}` | `.tiktoken`；`explicit_n_vocab=50257` |
| `p50k_base()` | `r50k_pat_str` | `{ENDOFTEXT: 50256}` | `.tiktoken`；`explicit_n_vocab=50281` |
| `p50k_edit()` | `r50k_pat_str` | `{ENDOFTEXT: 50256, FIM_PREFIX: 50281, FIM_MIDDLE: 50282, FIM_SUFFIX: 50283}` | 复用 p50k 词表与哈希 |
| `cl100k_base()` | 独立单行正则 | `{ENDOFTEXT: 100257, FIM_PREFIX: 100258, FIM_MIDDLE: 100259, FIM_SUFFIX: 100260, ENDOFPROMPT: 100276}` | `.tiktoken` |
| `o200k_base()` | 7 子正则 `\|` 拼接 | `{ENDOFTEXT: 199999, ENDOFPROMPT: 200018}` | `.tiktoken` |
| `o200k_harmony()` | 复用 o200k_base | o200k 基础上追加 `<|startoftext|>:199998`、`<|call|>:200012`、`<|reserved_200000|>`…`<|reserved_200011|>`、`<|reserved_{i}|>:i`（i∈200013..201088） | 以 `o200k_base()` 结果为基础 |

（构造详情 facts-python F-084~F-092；每一代 `.tiktoken` 文件均携带写死的 SHA-256 `expected_hash`，F-087~F-091。）

## 四代词表演进

按规模与策略，七个编码可归为四代演进（facts-python F-086~F-092，外部背景见背景调研演进表）：

- **第一代 gpt2 / r50k_base（≈50k）**：`gpt2` 与 `r50k_base` 词表与正则一致，r50k 视作 gpt2 别名，均约 50,257，特殊 token 仅 `ENDOFTEXT`。区别在**加载来源**——`gpt2` 走 `data_gym_to_mergeable_bpe_ranks` 双文件构造（F-086），`r50k_base` 直接 `load_tiktoken_bpe` 单文件（F-087）。
- **第二代 p50k_base / p50k_edit（代码与 FIM 优化）**：`p50k_base` 约 50,281（`explicit_n_vocab=50281`），非代码场景下与 r50k 大多产出相同 token；`p50k_edit` 在 p50k 词表之上叠加三个 FIM 特殊 token（id 50281-50283），用于代码编辑模型，且不再设置 `explicit_n_vocab`（F-088、F-089、F-094）。
- **第三代 cl100k_base（≈100k）**：词表相对 r50k 翻倍至约 10 万，特殊 token 含 `ENDOFTEXT`/FIM 三件套/`ENDOFPROMPT`（id 100257-100276），`pat_str` 采用独立的一行新正则（F-090）。多语言与数值序列处理显著增强（背景调研：数值序列专用 token）。
- **第四代 o200k_base / o200k_harmony（≈200k）**：词表再翻倍至约 20 万，特殊 token 精简为 `{ENDOFTEXT: 199999, ENDOFPROMPT: 200018}`，`pat_str` 由 **7 个子正则**拼成以覆盖大小写字母/数字标点/换行/空白等分支（F-091）；`o200k_harmony` 复用 base 的 `pat_str` 与 `mergeable_ranks`，但大幅追加工具特殊 token（如 `<|call|>`、大量 `<|reserved_...|>`），总词汇覆盖到 201088（F-092）。

### `pat_str` 的来源分化

- 前三代（`gpt2`/`r50k_base`/`p50k_base`/`p50k_edit`）全部共享常量 `r50k_pat_str`，其值为 GPT-2 原始 pattern 的等价快速变体：`"'(?:[sdmt]|ll|ve|re)| ?\p{L}++| ?\p{N}++| ?[^\s\p{L}\p{N}]++|\s++$|\s+(?!\S)|\s"`（F-085、F-095）。这说明前三代预分词逻辑一致。
- `cl100k_base` 使用独立单行正则（F-095，详见 F-090），关键词如贪婪分支 `[^\r\n\p{L}\p{N}]?+\p{L}++`、`\p{N}{1,3}+`（限制数字连续长度）等。
- `o200k_base`/`o200k_harmony` 由 7 个子正则 `"|".join` 拼成（F-091/F-095），覆盖更大的字符类别分支，对 camelCase 与多语言更友好。

### `explicit_n_vocab` 的取舍

一个重要反直觉点：`explicit_n_vocab`（统一校验显式词表规模的字段）**仅出现在前三代**构造 dict——`gpt2`/`r50k_base` 为 50257、`p50k_base` 为 50281；从 `p50k_edit` 起彻底移除（facts-python F-094）。原因在于早期编码靠 merge 表构造、规模稳定，可安全断言（配合 `Encoding.__init__` 的两条一致性断言，见 /concepts/02-encoding-api.md 的 F-009）；而 cl100k/o200k 的 `.tiktoken` 词表口径以文件内容为准，硬编码 `explicit_n_vocab` 反而可能因 mergeable 与 special 计数方式不同造成误报。

### 词表总数口径提醒

各编码"精确词表总数"在外部存在口径差异：如 cl100k 常见口径 100,256 mergeable、含特殊 token 后约 100,277；o200k 常见口径约 200,000、逆向分析约 200,019（背景调研"研究空白"）。tiktoken 内部以 `max_token_value + 1`（`n_vocab`）为唯一权威锚点（F-008、F-034），引用具体词表数时务必注明口径。

## ENCODING_CONSTRUCTORS 注册表

文件末尾定义模块级注册表 `ENCODING_CONSTRUCTORS`（facts-python F-093），将七个 key 映射到对应构造函数：

```
"gpt2"→gpt2, "r50k_base"→r50k_base, "p50k_base"→p50k_base, "p50k_edit"→p50k_edit,
"cl100k_base"→cl100k_base, "o200k_base"→o200k_base, "o200k_harmony"→o200k_harmony
```

`registry` 通过 `_find_constructors` 扫描 `tiktoken_ext` 命名空间包，`importlib.import_module` 后取 `mod.ENCODING_CONSTRUCTORS`（F-046~F-047），再由 `get_encoding(name)` 执行 `Encoding(**constructor())` 惰性构造并缓存（F-050）。因此要新增一个公开编码，只需在此文件（或任意 `tiktoken_ext` 插件模块）的 `ENCODING_CONSTRUCTORS` 中注册即可同时被 `get_encoding` 与模型映射（/concepts/05-registry-model.md）复用。关键约束：各构造 dict 的键必须与 `Encoding.__init__` 的 keyword-only 参数（`pat_str`、`mergeable_ranks`、`special_tokens`、`explicit_n_vocab`）对齐，`name` 作位置参数传入（facts-python F-096）。

## 相关概念

- [/concepts/06-encoder-loading.md](/concepts/06-encoder-loading.md)：本词表文件的加载、缓存与哈希校验机制。
- [/concepts/05-registry-model.md](/concepts/05-registry-model.md)：`ENCODING_CONSTRUCTORS` 如何被注册表发现与惰性调用。
- [/concepts/02-encoding-api.md](/concepts/02-encoding-api.md)：构造 dict 最终喂入的 `Encoding` 对象初始化逻辑。