---
type: Concept
title: tiktoken 整体架构
description: tiktoken v0.14.0 的双层架构总览——薄 Python 门面加重型 Rust 核心（PyO3），BPE 分词原理、公开 API 全貌与从入门到进阶的学习路径导览
tags: [tiktoken, bpe, tokenizer, 架构, pyo3, 笔记, 入门]
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
  - id: tiktoken-background
    resource: /references/background-research.md
    title: BPE 分词技术与外部背景
---

# tiktoken 整体架构

tiktoken 是 OpenAI 开源的高性能 BPE（字节对编码，Byte Pair Encoding）分词库，为 OpenAI 系列模型提供快速的分词与 token 计数能力。tiktoken v0.14.0 采用清晰的**"薄 Python 门面 + 重型 Rust 核心"双层架构**：Python 侧的 `Encoding` 类负责面向用户的逻辑编排，而真正的 BPE 合并压缩全部下沉到用 PyO3 编写的 Rust 原生扩展模块 `_tiktoken` 中完成。理解这一分层是学习整个库的前提。

## BPE 分词简介

BPE 是一种贪心（greedy）子词分词算法，起源于 1994 年的数据压缩算法，后被 OpenAI 的 GPT-2（2019）以**字节级 BPE（byte-level BPE）**形式引入自然语言处理，使基础词表固定为 256 个字节，从而对任意 Unicode 输入都不会产生未登录词（OOV）。其核心思路是：反复寻找语料中出现频率最高的相邻 token 对并合并，直到词表达到目标大小；编码（inference）时按训练学习到的合并规则贪心应用即可（见 [背景调研](/references/background-research.md)）。

tiktoken 封装了 OpenAI 的四代词汇体系：`gpt2`/`r50k_base`（约 5 万）、`p50k_base`/`p50k_edit`、`cl100k_base`（约 10 万）、`o200k_base`/`o200k_harmony`（约 20 万），词表规模随模型演进持续翻倍。

## 双层架构：Python 门面 + Rust 核心

tiktoken 的分词重担几乎全部下沉到原生扩展模块中。体现在两个层面：

- **Python 门面**：`tiktoken/` 包由 `core.py`（`Encoding` 类）、`registry.py`（编码注册表）、`model.py`（模型映射）、`load.py`（词表加载）、`_educational.py`（教学模块）组成。
- **Rust 核心**：`src/lib.rs` 定义 `CoreBPE` 结构与 BPE 合并算法，`src/py.rs` 通过 PyO3 绑定把 `CoreBPE` 导出为 Python 扩展模块 `_tiktoken`。

两者的结合点在于：`Encoding.__init__` 构造时即新建原生核心对象 `self._core_bpe = _tiktoken.CoreBPE(mergeable_ranks, special_tokens, pat_str)`（F-011），而 `_tiktoken` 是 Rust 侧 `#[pymodule(gil_used = false)] fn _tiktoken` 导出的扩展模块（facts-rust F-035）。所有真正耗时的入口都直接调用 `self._core_bpe.*`——例如 `encode` 调 `_core_bpe.encode`（F-016）、`encode_ordinary` 调 `_core_bpe.encode_ordinary`（F-013）。

Rust 侧的编译由 `Cargo.toml` 配置：`crate-type = ["cdylib", "rlib"]`（同时编译为 Python 动态扩展库与 Rust 库，facts-rust F-054），`python = ["pyo3"]` feature 控制 `src/py.rs` 的编译（facts-rust F-055）。Python 侧通过 `setuptools-rust` 构建后端将 Rust 扩展编译为 `_tiktoken` 模块。

> 反常识：Python 门面并非"完全甩锅"给 Rust。预分词（pre-tokenization）的 regex 切分在某些路径上由 Python 侧的 `_encode_only_native_bpe` 用 `regex.compile(self._pat_str)` 完成（F-036），再逐个 piece 交给 `_core_bpe.encode_single_piece` 做 BPE。也就是说"正则预分词"与"BPE 合并"分属于 Python 与 Rust 两层。

## 公开 API 全貌

tiktoken 以极少的顶层函数对外暴露，全部在 `__init__.py` 中 re-export（F-001）：

| 公开符号 | 来源模块 | 说明 |
|---|---|---|
| `tiktoken.Encoding` | `core.py` | 分词编码对象，提供 `encode`/`decode` 全套方法 |
| `tiktoken.get_encoding(name)` | `registry.py` | 按编码名加载编码，如 `get_encoding("cl100k_base")` |
| `tiktoken.list_encoding_names()` | `registry.py` | 列出所有可用编码名 |
| `tiktoken.encoding_for_model(model)` | `model.py` | 按模型名加载编码，如 `encoding_for_model("gpt-4o")` |
| `tiktoken.encoding_name_for_model(model)` | `model.py` | 按模型名解析编码名 |
| `tiktoken.__version__` | `__init__.py` | 版本号 `0.14.0`（F-002） |

值得注意的是，`load.py` 与 `_educational.py` 的符号**不会被导入**公开门面（F-003）——教学模块 `SimpleBytePairEncoding` 是刻意与生产实现解耦的非公开产物。

## 学习路径导览

本 bundle 的 `concepts/` 按"入门 → 核心"分批组织，推荐顺序如下：

- **00 整体架构**（本文）→ 建立双层心智模型
- [01 安装与快速上手](/concepts/01-getting-started.md) → 跑通第一个编解码闭环
- [02 Encoding 对象核心 API](/concepts/02-encoding-api.md) → 掌握公开方法全集（可与 03 并行）
- [03 BPE 分词与预切分](/concepts/03-bpe-tokenizer.md) → 理解预分词 + BPE 合并两个阶段
- [04 Rust 核心 CoreBPE 与性能](/concepts/04-rust-core.md) → 深入 Rust 底层实现（依赖 03）
- [05 注册表与模型映射](/concepts/05-registry-model.md) → 双入口与插件机制（依赖 02）

若目标仅是**用库**，掌握 00/01/02/05 即可；若目标是**自定义 tokenizer 或深入学习**，建议完整走 03 → 04，并结合词表文件加载机制理解编码的来源。

## 相关概念

- [01 安装与快速上手](/concepts/01-getting-started.md)：双入口与最小 roundtrip
- [02 Encoding 对象核心 API](/concepts/02-encoding-api.md)：`Encoding` 公开方法全集
- [03 BPE 分词与预切分](/concepts/03-bpe-tokenizer.md)：预分词与 BPE 合并
- [04 Rust 核心 CoreBPE 与性能](/concepts/04-rust-core.md)：Rust 底层实现
- [05 注册表与模型映射](/concepts/05-registry-model.md)：编码与模型解析
- 事实来源：[Python 事实清单](/references/facts-python.md)、[Rust 事实清单](/references/facts-rust.md)
- 架构剖析：[架构洞察](/references/insights.md)