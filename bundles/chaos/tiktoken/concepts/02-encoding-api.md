---
type: Concept
title: Encoding 对象核心 API
description: Encoding 类的全部公开方法详解——encode 系列变体（ordinary/numpy/batch/with_unstable/single_token）、decode 系列（bytes/offsets/batch）与词表相关属性
tags: [tiktoken, encoding, api, bpe, tokenizer, 编码, 解码]
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
---

# Encoding 对象核心 API

`Encoding`（`core.py` 第 16 行定义，F-006）是 tiktoken 面向用户的唯一核心类，一个对象完整封装了一个 tokenizer 的预分词正则 `pat_str`、可合并的 BPE 字节 token 秩表 `mergeable_ranks` 与特殊 token 映射 `special_tokens`（F-007）。本文系统梳理其全部公开方法，作为后续文档的对象层基础。

## 对象构造与数据锚点

`Encoding.__init__` 签名（F-006）：

```python
Encoding(name: str, *, pat_str: str, mergeable_ranks: dict[bytes, int],
         special_tokens: dict[str, int], explicit_n_vocab: int | None = None)
```

构造时发生的关键计算：

- `max_token_value`：`max(max(mergeable_ranks.values()), max(special_tokens.values(), default=0))`，即进类 token 与特殊 token 两个秩集合最大值中的较大者（F-008）。
- 当 `explicit_n_vocab` 非零时执行两个一致性断言：`len(mergeable_ranks) + len(special_tokens) == explicit_n_vocab` 且 `self.max_token_value == explicit_n_vocab - 1`（F-009）。
- 立即构造原生核心 `self._core_bpe = _tiktoken.CoreBPE(...)`（F-011），把真实计算交给 Rust。

> 词表一致性锚点：`n_vocab` 属性返回 `self.max_token_value + 1`，docstring 注明仅供向后兼容并建议改用 `enc.max_token_value + 1`（F-034）。"词表大小"实际由"最大 token id + 1"决定，并非 mergeable 与 special 的计数之和。

## 属性与谓词

| 成员 | 类型 | 说明 |
|---|---|---|
| `name` | 属性 | 编码名（F-007） |
| `eot_token` | `@property` | `self._special_tokens["<|endoftext|>"]`，键缺失抛 `KeyError`（F-031） |
| `special_tokens_set` | `cached_property` | `set(self._special_tokens.keys())`，特殊 token 名集合（F-032） |
| `is_special_token(token)` | 方法 | `token in self._special_token_values`，先断言 `token` 为 int（F-033） |
| `n_vocab` | `@property` | `max_token_value + 1`（F-034） |
| `max_token_value` | 属性 | 字典中最大 token id（F-008） |
| `token_byte_values()` | 方法 | 返回 `self._core_bpe.token_byte_values()`：排序后的 token 字节值列表（F-030） |

## encode 系列方法

`Encoding` 提供五个公开的编码方法（外加 `encode_ordinary`），覆盖从单 token 到批次的各类诉求。

### encode（标准编码，含特殊 token 处理）

```python
def encode(self, text, *, allowed_special: Literal["all"] | AbstractSet[str] = set(),
           disallowed_special: Literal["all"] | Collection[str] = "all") -> list[int]
```

（F-014）核心逻辑（F-015、F-016）：

1. `allowed_special == "all"` 时展开为 `self.special_tokens_set`；`disallowed_special == "all"` 时展开为 `special_tokens_set - allowed_special`。
2. 若 `disallowed_special` 非空，用 `_special_token_regex`（F-004）在文本中搜索命中，命中则调用 `raise_disallowed_special_token` 抛 `ValueError`（F-005）。
3. 调用 `self._core_bpe.encode(text, allowed_special)`；捕获 `UnicodeEncodeError` 时执行 surrogate-pair 修复重试（`utf-16 surrogatepass` 往返）后再试一次。

### encode_ordinary（普通编码，不处理特殊 token）

```python
def encode_ordinary(self, text: str) -> list[int]
```

（F-013）直接调 `self._core_bpe.encode_ordinary(text)`，不进行任何特殊 token 分支，遇 `UnicodeEncodeError` 同样做 surrogate 修复重试。

### encode_to_numpy（numpy 数组输出）

```python
def encode_to_numpy(self, text, *, allowed_special=set(), disallowed_special="all")
    -> npt.NDArray[np.uint32]
```

（F-017）特殊 token 预检与 `encode` 一致（F-018）；取 `self._core_bpe.encode_to_tiktoken_buffer(text, allowed_special)` 返回的内存 buffer，用 `np.frombuffer(buffer, dtype=np.uint32)` 转 numpy 数组。底层的 `TiktokenBuffer` 实现 buffer protocol（facts-rust F-048~F-050）。

### encode_batch / encode_ordinary_batch（并行批处理）

```python
def encode_batch(self, text, *, num_threads: int = 8, allowed_special=set(),
                 disallowed_special="all") -> list[list[int]]
def encode_ordinary_batch(self, text, *, num_threads: int = 8) -> list[list[int]]
```

（F-020、F-019）先用 `functools.partial` 构造绑定参数的 encoder，再用 `ThreadPoolExecutor(num_threads)` 并行 `map`。`encode_batch` 与逐条 `encode` 结果等价（facts-rust F-067）。

### encode_with_unstable（不稳定 token 探测）

```python
def encode_with_unstable(self, text, *, allowed_special=set(), disallowed_special="all")
    -> tuple[list[int], list[list[int]]]
```

（F-021）返回 `(tokens, completions)` 二元组，`completions` 是 last-piece 的候选 token 集；内部调 `self._core_bpe.encode_with_unstable(text, allowed_special)`（facts-rust F-042）。

### encode_single_token（单 token 编码）

```python
def encode_single_token(self, text_or_bytes: str | bytes) -> int
```

（F-022）`str` 先 `utf-8` 转字节，再调 `_core_bpe.encode_single_token`；token 不在词表时抛 `KeyError`。

## decode 系列方法

| 方法 | 签名 | 说明 |
|---|---|---|
| `decode_bytes` | `(tokens) -> bytes` | 直接返回 `_core_bpe.decode_bytes(tokens)`（F-023） |
| `decode` | `(tokens, errors="replace") -> str` | `decode_bytes(...).decode("utf-8", errors=errors)`（F-024） |
| `decode_single_token_bytes` | `(token) -> bytes` | 单 token 对应的字节，不在词表抛 `KeyError`（F-025） |
| `decode_tokens_bytes` | `(tokens) -> list[bytes]` | 逐 token 调 `decode_single_token_bytes`（F-026） |
| `decode_with_offsets` | `(tokens) -> tuple[str, list[int]]` | 返回 `(text, offsets)`，offsets 为各 token 的字节级起始位置（F-027），`errors="strict"` 解码 |
| `decode_batch` | `(batch, errors="replace", num_threads=8) -> list[str]` | `ThreadPoolExecutor` 并行（F-028） |
| `decode_bytes_batch` | `(batch, num_threads=8) -> list[bytes]` | 并行执行 `decode_bytes`（F-029） |

`decode_with_offsets` 的偏移计算沿用了 UTF-8 尾字节（`0x80 <= c < 0xC0`）不计入开头的规则，偏移值以字节位置计（facts-rust F-062、F-063）。

## 私有方法与 pickle 协议

- `_encode_single_piece(text_or_bytes)`：`str` 先 utf-8 转字节，再调 `_core_bpe.encode_single_piece`，不编码任何特殊 token（F-035）。
- `_encode_only_native_bpe(text)`：在 Python 侧用 `regex.compile(self._pat_str)` 做正则切分，逐 piece 调 `_core_bpe.encode_single_piece`（F-036）。
- `_encode_bytes(text)`：直接调 `_core_bpe._encode_bytes(text)`（F-037）。
- `__getstate__`/`__setstate__`：支持 pickle。当对象是注册表中已登记实例时按引用存字符串；否则存构造参数字典；反序列化时对应按键查找或 `__init__(**value)` 重建（F-038、F-039）。

> v0.14.0 源码中不存在 `_encode_ordinary_native`、`_encode_native`、`string_ordinal` 这些方法（F-040~F-042），实际提供的是 `_encode_only_native_bpe` 与 `_encode_bytes`。

## 相关概念

- [01 安装与快速上手](/concepts/01-getting-started.md)：`encode`/`decode` 的最小用法
- [03 BPE 分词与预切分](/concepts/03-bpe-tokenizer.md)：`_encode_only_native_bpe` 依赖的 `pat_str` 正则切分
- [04 Rust 核心 CoreBPE 与性能](/concepts/04-rust-core.md)：`self._core_bpe.*` 对应的 Rust 实现
- [05 注册表与模型映射](/concepts/05-registry-model.md)：Encoding 由注册表/模型映射构造
- 事实来源：[Python 事实清单](/references/facts-python.md)