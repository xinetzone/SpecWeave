# References 索引

本目录包含 tiktoken v0.14.0 知识包的参考资料，包括知识地图、事实清单和信源登记。

## 知识地图

| 文件 | 说明 |
|------|------|
| [insights.md](insights.md) | tiktoken 架构洞察与核心论点知识地图 |

## 事实清单

事实清单基于源码采集，每条事实标注文件路径与行号，零推测。

| 文件 | 涵盖范围 | 事实数量 |
|------|---------|---------|
| [facts-python.md](facts-python.md) | Python 门面层：`Encoding` API、registry 注册表、model 模型映射、load 词表加载与缓存、`_educational` 教学模块 | 详见文件 |
| [facts-rust.md](facts-rust.md) | Rust 核心层：`CoreBPE`、`byte_pair_encode` 算法、PyO3 绑定与 GIL 管理 | 详见文件 |

## 信源登记

信源登记记录源码树的结构、文件统计和关键文件清单。

| 文件 | 源路径 | 文件数 | 涵盖范围 |
|------|--------|--------|---------|
| [source.md](source.md) | tiktoken v0.14.0 源码树 | 详见文件 | Python 包结构与 Rust crate 结构、关键文件清单 |
| [background-research.md](background-research.md) | 领域背景与研究过程 | — | BPE 分词背景、tiktoken 定位、研究思路与信源引用 |

```{toctree}
:maxdepth: 2

background-research
facts-python
facts-rust
insights
source
```