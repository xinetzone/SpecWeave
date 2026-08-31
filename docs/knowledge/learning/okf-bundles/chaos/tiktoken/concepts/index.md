# Concepts 索引

tiktoken v0.14.0 概念文档共 9 篇，按学习路径分入门 / 核心 / 进阶三组组织。

## 入门（00-01）

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [整体架构](00-overview.md) | tiktoken 双层架构（薄 Python 门面 + 重型 Rust 核心 / PyO3）与 BPE 分词原理总览，以及从入门到进阶的学习路径导览 |
| 01 | [安装与快速上手](01-getting-started.md) | 安装方式与最小使用套路——`get_encoding` / `encoding_for_model` 双入口、编解码 roundtrip 闭环与 `list_encoding_names` 清单 |

## 核心（02-06）

| 编号 | 文档 | 说明 |
|------|------|------|
| 02 | [Encoding 对象核心 API](02-encoding-api.md) | `Encoding` 类全部公开方法：encode 系列变体（ordinary/numpy/batch/with_unstable/single_token）与 decode 系列（bytes/offsets/batch）及词表相关属性 |
| 03 | [BPE 分词与预切分](03-bpe-tokenizer.md) | BPE 字节对编码的两个阶段（预分词与合并）在 tiktoken 中的落点——`pat_str` 正则切分、`mergeable_ranks` 合并与特殊 token 的双轨处理 |
| 04 | [Rust 核心 CoreBPE 与性能](04-rust-core.md) | Rust 原生内核剖析——`CoreBPE` 七个字段、`byte_pair_encode` 大小输入分派、BinaryHeap 大输入优化、线程局部正则缓冲与 GIL 释放 |
| 05 | [注册表与模型映射](05-registry-model.md) | 双入口解析机制——`registry.get_encoding` 的 Lazy 构造与 `tiktoken_ext` 插件发现、`encoding_for_model` 的精确映射与前缀降级链 |
| 06 | [BPE 词表加载与缓存](06-encoder-loading.md) | 解析 load.py——读文件多路径、SHA1 缓存键与 SHA256 校验、磁盘原子写，以及 data-gym 与 tiktoken 两种词表格式的解析流程 |

## 进阶（07-08）

| 编号 | 文档 | 说明 |
|------|------|------|
| 07 | [OpenAI 公开词汇体系](07-openai-vocabularies.md) | 归纳 `tiktoken_ext/openai_public.py` 七个公开编码构造函数，对比 gpt2/字节级 /r50k/p50k/cl100k/o200k 各代词表的规模、特殊 token 与正则分化 |
| 08 | [教学模块 SimpleBytePairEncoding](08-educational-module.md) | 拆解 `_educational.py` 的 `SimpleBytePairEncoding` 类与 bpe_encode/bpe_train 纯 Python 复现，并与 Rust 生产 `byte_pair_encode` 对照，体会可读性优先 vs 性能优先 |

```{toctree}
:maxdepth: 2

00-overview
01-getting-started
02-encoding-api
03-bpe-tokenizer
04-rust-core
05-registry-model
06-encoder-loading
07-openai-vocabularies
08-educational-module
```