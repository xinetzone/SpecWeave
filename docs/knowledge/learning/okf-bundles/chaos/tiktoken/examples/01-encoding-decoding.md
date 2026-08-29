---
type: Example
title: tiktoken 基础编解码示例
description: 使用 get_encoding("o200k_base") 与 Encoding 类的 encode/decode/roundtrip，演示 token 编解码、单 token 操作与字节级往返，全部基于 tiktoken v0.14.0 真实 API
tags: [tiktoken, example, encoding, decoding, roundtrip, o200k_base]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
sources:
  - id: tiktoken-source
    resource: "/references/source.md"
    title: tiktoken v0.14.0 源码根目录登记
  - id: tiktoken-python
    resource: "/references/facts-python.md"
    title: tiktoken Python 门面层事实清单
  - id: tiktoken-rust
    resource: "/references/facts-rust.md"
    title: tiktoken Rust 核心事实清单
---

# tiktoken 基础编解码示例

本示例演示 tiktoken v0.14.0 最基础且最常用的能力：**文本 ↔ token 的双向转换**。通过 `get_encoding("o200k_base")` 获取 OpenAI 最新的 `o200k_base` 编码，并验证 `Encoding.encode` / `Encoding.decode` 的往返（roundtrip）一致性。所有 API 均来自真实源码，行为与事实清单一致。

## 环境要求

- 安装 tiktoken 0.14.0（`pip install tiktoken==0.14.0`）。运行时会惰性加载 `o200k_base.tiktoken` 文件，内置在 wheel 中，无需网络（F-091 的 `load_tiktoken_bpe`）。

## 导入与获取编码

公开门面层在 `tiktoken/__init__.py` 中 re-export `Encoding` 与 `get_encoding`（F-001）。

```python
from tiktoken import get_encoding, encoding_for_model, Encoding

# 获取 o200k_base 编码
enc = get_encoding("o200k_base")
print(type(enc))       # <class 'tiktoken.core.Encoding'>
print(enc.name)        # o200k_base
```

`get_encoding` 通过 `Encoding(**constructor())` 惰性构造并缓存 `Encoding` 实例（F-050），已构造的编码缓存在 `tiktoken.registry.ENCODINGS` 字典中（F-044）。`o200k_base` 的构造函数定义于 `tiktoken_ext/openai_public.py`（F-091），其 `pat_str` 由 7 个子正则经 `"|"` 拼成（F-091）。

## 基础 encode / decode

对字符串编码返回 token 索引列表，`decode` 将其还原为文本。

```python
tokens = enc.encode("hello world")
print(tokens)          # [15339, 1917]

text = enc.decode(tokens)
print(text)            # hello world
```

- `enc.encode(text)` 返回 `list[int]`，`allowed_special` 与 `disallowed_special` 为 keyword-only 参数，默认值分别为空集 `set()` 与字符串 `"all"`（F-014）。
- `enc.decode(tokens)` 返回 `str`，`errors` 默认 `"replace"`（F-024）。

## 往返（roundtrip）断言

tiktoken 的核心保证是 `decode(encode(x)) == x`。测试约束同样验证了这一性质（facts-rust F-068、F-060）。

```python
samples = [
    "hello",
    "hello world",
    "  ",
    "请考试我的软件！12345",
    "Unicode 文本 tiktoken 🎉",
]

for text in samples:
    assert enc.decode(enc.encode(text)) == text
    assert enc.decode_bytes(enc.encode(text)).decode("utf-8") == text

print("roundtrip 全部通过")
```

- `enc.decode_bytes(tokens)` 返回原始 `bytes`（F-023），再经 UTF-8 解码得到文本。
- 对合法输入的 roundtrip 保证来自 `tests/test_encoding.py` 的 `decode(encode(x)) == x` 约束（F-068）。

## 字节级：`encode_single_token` 与 `decode_single_token_bytes`

单 token 的字节↔索引互转。此二方法在词表缺失时会抛出 `KeyError`（F-022、F-025）。

```python
# 给定文本片段编码为单个 token（若它是一个完整词表 token）
tok = enc.encode_single_token("hello")
print(tok)                       # 15339

# 反查 token 对应的原始字节
token_bytes = enc.decode_single_token_bytes(tok)
print(token_bytes)               # b"hello"
assert token_bytes == b"hello"

# roundtrip：encode_single_token(decode_single_token_bytes(t)) == t
for t in range(enc.n_vocab):
    try:
        b = enc.decode_single_token_bytes(t)
    except KeyError:
        continue                    # 特殊 token 或未覆盖 token 跳过
    assert enc.encode_single_token(b) == t

print("token 字节级 roundtrip 通过")
```

- `enc.encode_single_token(text_or_bytes)`：`str` 入参先 `utf-8` 编码，再交原生 `CoreBPE.encode_single_token`（F-022；Rust `py.rs` 的 `encode_single_token` F-043）。
- `enc.decode_single_token_bytes(token)` 直接返回原生字节（F-025；Rust F-046）。
- 遍历 `range(enc.n_vocab)` 做单 token 往返，对应测试 `test_single_token_roundtrip` 的性质（F-060）。`enc.n_vocab` 属性返回 `max_token_value + 1`（F-034）。由于并非 `range(n_vocab)` 内每个整数都有对应字节（部分为特殊 token，部分「空洞」），需 `try/except KeyError` 跳过不可解码 token。

## 编解码相关的元信息属性

`Encoding` 还暴露若干只读元信息（F-008、F-031、F-032）：

```python
print("name:", enc.name)
print("max_token_value:", enc.max_token_value)
print("n_vocab:", enc.n_vocab)
print("eot_token:", enc.eot_token)                     # <|endoftext|> 的 token id
print("special_tokens_set:", enc.special_tokens_set)
```

- `max_token_value` 为 mergeable、special token 两方 rank 最大值中的较大者（F-008）。
- `eot_token` 返回特殊 token `<|endoftext|>` 的 id（F-031）。
- `special_tokens_set` 是 `set(self._special_tokens.keys())` 的缓存属性（F-032）。

## 完整代码

```python
from tiktoken import get_encoding

enc = get_encoding("o200k_base")

# 基础编解码
tokens = enc.encode("hello world")
assert enc.decode(tokens) == "hello world"

# 文本往返
for text in ["hello", "hello world", "  ", "请考试我的软件！12345", "Unicode 文本 🎉"]:
    assert enc.decode(enc.encode(text)) == text

# 单 token 字节往返
tok = enc.encode_single_token("hello")
assert enc.decode_single_token_bytes(tok) == b"hello"

print("全部断言通过")
```

## 关键 API 索引

| API | 事实编号 | 说明 |
|-----|---------|------|
| `tiktoken.get_encoding(name)` | F-001 / F-048~F-050 | 按名获取（惰性构造+缓存）编码 |
| `Encoding.encode(text)` | F-014 | 文本 → token 列表 |
| `Encoding.decode(tokens)` | F-024 | token 列表 → 文本 |
| `Encoding.decode_bytes(tokens)` | F-023 | token 列表 → 原始字节 |
| `Encoding.encode_single_token(piece)` | F-022 / F-043 | 单 token → 索引 |
| `Encoding.decode_single_token_bytes(token)` | F-025 / F-046 | 索引 → 单 token 字节 |
| `Encoding.n_vocab` | F-034 | 词表大小（向后兼容） |
| `Encoding.max_token_value` | F-008 | 最大 token rank |
| `Encoding.eot_token` | F-031 | `<\|endoftext\|>` 的 token id |
| `encoding_for_model(name)` | F-001 / F-055 | 按模型名获取编码（见 `02` 示例） |

## 延伸阅读

- [模型映射与 token 计数示例](02-model-token-counting.md)：`encoding_for_model` / `encoding_name_for_model` 与 token 计数实践。
- [Registry 与 Model 映射](/concepts/05-registry-model.md)：`get_encoding` 惰性构造、`MODEL_TO_ENCODING` 前缀匹配机制。
- [OpenAI 词汇表](/concepts/07-openai-vocabularies.md)：`o200k_base`、`cl100k_base` 等词汇表的构造与 `pat_str` 正则。