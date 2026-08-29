---
type: Example
title: tiktoken 模型映射与 token 计数示例
description: 使用 encoding_for_model / encoding_name_for_model 实现模型到编码的映射，并结合 Encoding 展示 token 计数与计费相关实践，全部基于 tiktoken v0.14.0 model.py 真实映射
tags: [tiktoken, example, model, token-counting, encoding_for_model, encoding_name_for_model, pricing]
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

# tiktoken 模型映射与 token 计数示例

本示例演示 OpenAI 模型名如何映射到具体分词编码，以及如何据此进行 **token 计数与计费估算**。核心 API 为 `tiktoken.encoding_for_model` 与 `tiktoken.encoding_name_for_model`，均定义于 `tiktoken/model.py`（F-052~F-055）的真实映射表中。

## 环境要求

- 安装 tiktoken 0.14.0。模型映射数据内置在源码的 `MODEL_TO_ENCODING` / `MODEL_PREFIX_TO_ENCODING` 字典中，无需网络。

## 模型 → 编码映射

公开 API 由 `tiktoken/__init__.py` re-export（F-001）：

```python
from tiktoken import encoding_for_model, encoding_name_for_model, get_encoding

# 直接查编码名
print(encoding_name_for_model("gpt-4o"))          # o200k_base
print(encoding_name_for_model("gpt-4"))           # cl100k_base
print(encoding_name_for_model("gpt-3.5-turbo"))   # cl100k_base

# 获取编码实例
enc = encoding_for_model("gpt-4o")
print(enc.name)                                   # o200k_base
```

- `encoding_name_for_model(model_name)` 先查精确表 `MODEL_TO_ENCODING`，命中即返回；否则按 `MODEL_PREFIX_TO_ENCODING` 做前缀匹配；均未命中抛 `KeyError`（F-054）。
- `encoding_for_model(model_name)` 返回 `get_encoding(encoding_name_for_model(model_name))`（F-055）。
- `gpt-4o → o200k_base` 与 `gpt-4 → cl100k_base` 来自 `MODEL_TO_ENCODING`（F-053），**同一模型家族可能跨越不同词汇表**。

### 前缀匹配（版本化模型名）

`MODEL_PREFIX_TO_ENCODING` 允许未逐一列出的新版本模型通过前缀命中（F-052）。例如带日期的 `gpt-4o-2024-05-13`：

```python
name = encoding_name_for_model("gpt-4o-2024-05-13")
print(name)                  # o200k_base（命中 "gpt-4o-" 前缀）
assert name == encoding_name_for_model("gpt-4o")
```

前缀表部分条目（F-052）：

| 前缀 | 编码 |
|------|------|
| `o1-` / `o3-` / `o4-mini-` / `gpt-5` / `gpt-4.5-` / `gpt-4.1-` / `chatgpt-4o-` / `gpt-4o-` / `ft:gpt-4o` | `o200k_base` |
| `gpt-4-` / `gpt-3.5-turbo-` / `gpt-35-turbo-` / `ft:gpt-4` / `ft:gpt-3.5-turbo` | `cl100k_base` |
| `gpt-oss-` | `o200k_harmony` |
| `ft:davinci-002` / `ft:babbage-002` | `cl100k_base` |

> 注意：前缀匹配可能命中并不存在的模型名（源码注释明确说明，F-054），仅作为避免更新库即可兼容新模型的便捷机制。

### 未知模型的 KeyError

```python
try:
    encoding_name_for_model("unknown-model-xyz")
except KeyError as e:
    print(e)   # 提示改用 tiktoken.get_encoding
```

`KeyError` 消息提示改用 `tiktoken.get_encoding` 显式指定编码（F-054、F-049）。

## token 计数

得到 `Encoding` 后即可对文本计算 token 数。计费视角下，OpenAI 按「输入 + 输出」token 总量计费，因此常用 `len(tokens)` 估算。

```python
def count_tokens(text: str, model: str) -> tuple[int, list[int]]:
    enc = encoding_for_model(model)
    tokens = enc.encode(text)
    return len(tokens), tokens

text = "Hello, how are you? 你好，今天天气不错。"
n, tokens = count_tokens(text, "gpt-4o")
print(f"token 数: {n}")
print(tokens)
```

- `encode` 默认 `disallowed_special="all"`：文本中含未显式允许的特殊 token（如 `<|endoftext|>`）时会抛 `ValueError`（F-014、F-015、facts-rust F-061）。统计用户自由文本时应留意，或按需设置 `allowed_special`。
- 提示/模板文本常包含特殊 token，编写计费统计时建议显式声明：`enc.encode(text, allowed_special="all")` 将全部特殊 token 均视为允许（F-015）。

## 批处理计数（推荐）

对大语料按条统计，使用 `encode_batch` 并行提升吞吐（F-020；对应 facts-rust F-067 的批/逐条等价约束）：

```python
documents = [
    "Hello, how are you?",
    "你好，今天天气不错。",
    "tiktoken is a fast BPE tokeniser.",
]

enc = encoding_for_model("gpt-4o")
batch = enc.encode_batch(documents)          # list[list[int]]
counts = [len(t) for t in batch]

for doc, cnt in zip(documents, counts):
    print(f"{cnt:>4}  tokens | {doc}")
```

## 估算计费文本

以下工具函数综合了模型映射 + 特殊 token 允许 + 批量计数，用于估算一批请求的 token 用量：

```python
from tiktoken import encoding_for_model

def estimate_batch_tokens(messages: list[str], model: str = "gpt-4o") -> int:
    enc = encoding_for_model(model)
    # messages 允许含特殊 token，按 "all" 处理避免 ValueError
    encoded = enc.encode_batch(messages, allowed_special="all")
    return sum(len(tokens) for tokens in encoded)

messages = ["Hello", "请问 tiktoken 如何工作？", "<|endoftext|>"]
total = estimate_batch_tokens(messages)
print(f"总 token 数: {total}")
```

- `encode_batch(text, num_threads=8, allowed_special=set(), disallowed_special="all")`（F-020）：`allowed_special="all"` 展开为全部特殊 token 集合，等价写法为传入 `enc.special_tokens_set`（F-032）。

## 完整代码

```python
from tiktoken import encoding_for_model, encoding_name_for_model, get_encoding

# 1. 模型映射
assert encoding_name_for_model("gpt-4o") == "o200k_base"
assert encoding_name_for_model("gpt-4") == "cl100k_base"
assert encoding_for_model("gpt-4o").name == "o200k_base"

# 2. 前缀匹配版本化模型
assert encoding_name_for_model("gpt-4o-2024-05-13") == "o200k_base"

# 3. 计数
enc = encoding_for_model("gpt-4o")
tokens = enc.encode("Hello, how are you? 你好，今天天气不错。")
print("tokens:", tokens)
print("count:", len(tokens))

# 4. 批量计数
counts = [len(t) for t in enc.encode_batch(["Hello", "你好", "Hi there"])]
print("batch counts:", counts)
```

## 关键 API 索引

| API | 事实编号 | 说明 |
|-----|---------|------|
| `tiktoken.encoding_for_model(name)` | F-001 / F-055 | 按模型名获取 `Encoding` |
| `tiktoken.encoding_name_for_model(name)` | F-001 / F-054 | 模型名 → 编码名（精确表+前缀匹配） |
| `MODEL_TO_ENCODING` | F-053 | 精确模型名映射表 |
| `MODEL_PREFIX_TO_ENCODING` | F-052 | 前缀映射表（版本化模型） |
| `Encoding.encode_batch(text, ...)` | F-020 | 批编码 → `list[list[int]]` |
| `Encoding.special_tokens_set` | F-032 | 全部特殊 token 集合 |

## 延伸阅读

- [基础编解码示例](01-encoding-decoding.md)：`get_encoding`、`encode`/`decode` 的底层细节。
- [Registry 与 Model 映射](/concepts/05-registry-model.md)：`get_encoding` 惰性构造、`MODEL_PREFIX_TO_ENCODING` 前缀匹配设计。
- [OpenAI 词汇表](/concepts/07-openai-vocabularies.md)：`o200k_base` / `cl100k_base` 词汇表差异与 `pat_str` 正则。
- [背景调研](../references/background-research.md)：token 计数与计费背景。