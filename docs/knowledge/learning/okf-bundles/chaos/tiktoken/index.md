# tiktoken 源码学习知识包

tiktoken 是 OpenAI 官方的 BPE 分词库，采用「薄 Python 门面 + 重型 Rust 核心」的双层架构（基于 PyO3 绑定）。本知识包基于 tiktoken v0.14.0 源码整理，收入 9 篇概念文档，系统覆盖从安装快速上手、BPE 分词原理、Encoding 核心 API、Rust 原生内核、注册表与模型映射、词表加载缓存，到 OpenAI 公开词汇体系与教学模块的完整学习路径，并附实践示例与事实参考。

## 概念文档

### 入门

- [00 整体架构](concepts/00-overview.md) — tiktoken 双层架构总览、BPE 分词原理与学习路径导览
- [01 安装与快速上手](concepts/01-getting-started.md) — 安装方式与 `get_encoding` / `encoding_for_model` 双入口最小使用套路

### 核心

- [02 Encoding 对象核心 API](concepts/02-encoding-api.md) — `Encoding` 类全部公开方法：encode 系列与 decode 系列变体及词表相关属性
- [03 BPE 分词与预切分](concepts/03-bpe-tokenizer.md) — BPE 两阶段（预分词与合并）在 tiktoken 中的落点，`pat_str` 正则与 `mergeable_ranks` 合并
- [04 Rust 核心 CoreBPE 与性能](concepts/04-rust-core.md) — Rust 原生内核：`CoreBPE` 字段、`byte_pair_encode` 大小输入分派与 GIL 释放
- [05 注册表与模型映射](concepts/05-registry-model.md) — `registry.get_encoding` Lazy 构造与 `encoding_for_model` 精确映射加前缀降级链
- [06 BPE 词表加载与缓存](concepts/06-encoder-loading.md) — 读文件多路径、SHA1 缓存键与 SHA256 校验、磁盘原子写及两种词表格式解析

### 进阶

- [07 OpenAI 公开词汇体系](concepts/07-openai-vocabularies.md) — 七个公开编码构造函数与四代词表规模、特殊 token、正则分化对比
- [08 教学模块 SimpleBytePairEncoding](concepts/08-educational-module.md) — 纯 Python 复现 BPE 训练/编码，与 Rust 生产实现对照体会可读性 vs 性能

## 示例

- [基础编解码](examples/01-encoding-decoding.md) — `get_encoding` 与 `Encoding` 类的 encode/decode 往返
- [模型映射与 token 计数](examples/02-model-token-counting.md) — `encoding_for_model` 映射及 token 计数/计费估算
- [示例索引](examples/index.md) — 全部示例列表

## 参考资料

- [知识地图](references/insights.md) — 架构洞察与核心论点
- [事实清单：Python](references/facts-python.md) — tiktoken Python 门面事实登记
- [事实清单：Rust](references/facts-rust.md) — tiktoken Rust 核心事实登记
- [信源登记](references/source.md) — 源码树结构与关键文件清单
- [背景调研](references/background-research.md) — 领域背景与研究过程
- [References 索引](references/index.md) — 参考资料汇总列表

```{toctree}
:maxdepth: 2

concepts/index
examples/index
references/index
log
verification-report
```