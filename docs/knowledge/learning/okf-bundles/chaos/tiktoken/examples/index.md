# Examples 索引

本目录包含 tiktoken v0.14.0 的实践示例，帮助开发者快速上手 OpenAI 分词库的核心功能：编解码往返与模型映射。

## 示例列表

| 示例 | 说明 | 涵盖主题 |
|------|------|---------|
| [基础编解码](01-encoding-decoding.md) | 演示 `get_encoding` 与 `Encoding` 类的 encode/decode 往返 | `encode`/`decode`/`decode_bytes`、`encode_single_token`、`decode_single_token_bytes`、`n_vocab`/`max_token_value`/`eot_token` |
| [模型映射与 token 计数](02-model-token-counting.md) | 演示模型名到编码的映射及 token 计数/计费估算 | `encoding_for_model`、`encoding_name_for_model`、前缀匹配、`encode_batch`、批处理计数 |

## 按主题分类

### 入门与基础

- [基础编解码](01-encoding-decoding.md)：通过 `get_encoding("o200k_base")` 演示文本 ↔ token 的双向转换与 roundtrip 断言，适合第一次接触 tiktoken 的开发者。

### 模型映射与计数

- [模型映射与 token 计数](02-model-token-counting.md)：演示 `encoding_for_model`/`encoding_name_for_model` 的精确表与前缀匹配映射，以及据此估算 token 用量与计费的实践。

## 前置知识

阅读示例前建议先了解以下概念文档：

- [Registry 与 Model 映射](/concepts/05-registry-model.md)：`get_encoding` 惰性构造与模型映射机制。
- [OpenAI 词汇表](/concepts/07-openai-vocabularies.md)：`o200k_base`/`cl100k_base` 等词汇表的构造。

## 运行环境

示例代码基于 tiktoken 0.14.0 版本，需要：

- Python 3.9+（`pyproject.toml` 的 `requires-python = ">=3.9"`）
- tiktoken Python 包（`pip install tiktoken==0.14.0`）

示例无需网络（内置词汇表文件）；如需按 OpenAI API 计费相关实践，网络访问由上层应用自行处理。

```{toctree}
:maxdepth: 2

01-encoding-decoding
02-model-token-counting
```