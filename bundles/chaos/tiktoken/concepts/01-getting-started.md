---
type: Concept
title: 安装与快速上手
description: tiktoken v0.14.0 的安装方式与最小使用套路——get_encoding / encoding_for_model 双入口、编解码 roundtrip 闭环与 list_encoding_names 清单
tags: [tiktoken, bpe, tokenizer, 安装, quickstart, 入门]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
sources:
  - id: tiktoken-source
    resource: /references/source.md
    title: tiktoken v0.14.0 源码根目录登记
  - id: tiktoken-python
    resource: /references/facts-python.md
    title: Python 门面层事实清单
  - id: tiktoken-rust
    resource: /references/facts-rust.md
    title: Rust 核心事实清单
---

# 安装与快速上手

本文演示如何安装 tiktoken 并跑通第一个"加载编码 → 编码 → 解码"的闭环。tiktoken 的公开门面极小，掌握 `get_encoding` 与 `encoding_for_model` 两个入口、一组 `encode`/`decode` 方法，即可完成绝大多数日常 token 计数需求。

## 安装

tiktoken 的 Python 侧要求 `requires-python = ">=3.9"`，运行时依赖仅有 `regex` 与 `requests`（可选地安装 `blobfile` 以支持云端词表读取）。它通过 `setuptools-rust` 构建后端把 Rust 原生扩展编译为 `_tiktoken` 模块，因此以常规方式安装即可：

```bash
pip install tiktoken
```

安装后在 Python 中使用：

```python
import tiktoken
print(tiktoken.__version__)  # 0.14.0（F-002）
```

> 行为约束：`import tiktoken` 不会触发加载 `blobfile`（facts-rust F-066），模块的公开导入路径很薄，只 re-export `Encoding`、`get_encoding`、`list_encoding_names`、`encoding_for_model`、`encoding_name_for_model`（F-001）。

## 双入口选择编码

加载一个编码对象有两种方式，对应两个不同的业务入口（详见 [05 注册表与模型映射](/concepts/05-registry-model.md)）：

1. **按编码名**：`tiktoken.get_encoding(name)`（F-048）。编码名是底层、更可控的权威入口，如 `cl100k_base`、`o200k_base`。
2. **按模型名**：`tiktoken.encoding_for_model(model)`（F-055）。返回 `get_encoding(encoding_name_for_model(model))`，根据模型名自动解析对应的编码名，如 `gpt-4o` 会解析到 `o200k_base`。

```python
import tiktoken

enc_by_name = tiktoken.get_encoding("cl100k_base")        # 按编码名
enc_by_model = tiktoken.encoding_for_model("gpt-4")       # 按模型名
```

典型的 `gpt2` 编码行为约束（facts-rust F-057）：

```python
enc = tiktoken.get_encoding("gpt2")
enc.encode("hello world")        # 结果 [31373, 995]
```

## 简单编解码 roundtrip

`Encoding` 对象最核心的两个方法是 `encode`（文本 → token id 列表）与 `decode`（token id 列表 → 文本），反向恢复原文的往返（roundtrip）是其最基本性质（facts-rust F-068）：

```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

tokens = enc.encode("请考试我的软件！12345")   # 文本 → token id
print(tokens)

text = enc.decode(tokens)                     # token id → 文本
print(text == "请考试我的软件！12345")          # True，roundtrip 成立
```

关于 `encode`/`decode` 的要点：

- `encode(text)` 返回 `list[int]`（F-014），可选的 `allowed_special`（默认空集 `set()`）与 `disallowed_special`（默认 `"all"`）控制特殊 token（special token）的处理策略。默认 `disallowed_special="all"` 意味着文本中出现未特意允许的特殊 token 时会抛出 `ValueError`（facts-rust F-061）。
- `decode(tokens)` 返回 `str`，`errors` 参数默认 `"replace"`（F-024），与 `encode` 互为逆操作。

```python
# special token 的显式允许
enc = tiktoken.get_encoding("gpt2")
enc.encode("hello <|endoftext|>", allowed_special="all")   # 结果 [31373, 220, 50256]（F-057）

# decode 逆过程
decoded = enc.decode([31373, 995])                          # "hello world"
```

对预算与上下文管理而言，统计 token 数只需 `len(enc.encode(text))`，这是 `encoding_for_model` 最典型的应用场景。

## 查看可用编码清单

`tiktoken.list_encoding_names()` 返回当前注册表中所有可用的编码名（F-051）：

```python
import tiktoken
print(tiktoken.list_encoding_names())
```

在默认安装下，它会列出 `tiktoken_ext` 插件包注册的七种公开编码：`gpt2`、`r50k_base`、`p50k_base`、`p50k_edit`、`cl100k_base`、`o200k_base`、`o200k_harmony`（facts-python F-093）。

## 相关概念

- [00 整体架构](/concepts/00-overview.md)：双层架构与公开 API 全貌
- [02 Encoding 对象核心 API](/concepts/02-encoding-api.md)：`encode`/`decode` 的全部变体与属性
- [05 注册表与模型映射](/concepts/05-registry-model.md)：`get_encoding`/`encoding_for_model` 背后的实现
- 事实来源：[Python 事实清单](/references/facts-python.md)、[Rust 事实清单](/references/facts-rust.md)
- 信源登记：[源码根目录](/references/source.md)