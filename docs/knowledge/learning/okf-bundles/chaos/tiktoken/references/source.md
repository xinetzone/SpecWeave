---
type: Source
title: tiktoken v0.14.0 源码根目录登记
description: tiktoken v0.14.0 源码仓库的信源登记，涵盖项目标识、目录结构、子模块文件与 facts 覆盖映射、Python 与 Rust/PyO3 构建依赖
tags: [tiktoken, bpe, tokenizer, source, reference, osq]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
source_id: tiktoken-source
---

# tiktoken v0.14.0 源码信源登记

本文件登记了 tiktoken 源码学习 Bundle（`bundles/chaos/tiktoken/`）所依据的信源——OpenAI 开源 tiktoken 仓库 v0.14.0 版本的实际源码目录，作为 `references/` 事实清单与 `examples/` 示例文档的真实性基座。**所有 API 与行为均来自真实源码，禁止虚构。**

## 项目标识

| 项 | 值 |
|---|---|
| 项目名称 | tiktoken |
| 上游仓库 | [OpenAI/tiktoken](https://github.com/openai/tiktoken)（GitHub） |
| 版本 | `v0.14.0`（`tiktoken/__init__.py` 第 8 行 `__version__ = "0.14.0"`，F-002） |
| 原生扩展版本 | `Cargo.toml` `[package] version = "0.14.0"`（F-053） |
| 语言 | Python 门面层 + Rust 原生内核（PyO3 绑定） |
| 源码根路径 | `d:\AI\.chaos\ai\libs\tiktoken` |
| 构思简述 | fast BPE tokeniser for OpenAI's models（`pyproject.toml` `description`） |
| 作者 | Shantanu Jain（`pyproject.toml` `authors`） |

## 目录结构清单

以下结构经实际 `LS` 确认（`d:\AI\.chaos\ai\libs\tiktoken`）：

```
tiktoken/
├── tiktoken/                  # Python 包 (门面层)
│   ├── __init__.py            # 公开 API re-export 与 __version__
│   ├── core.py                # Encoding 类（Python 封装）
│   ├── registry.py            # ENCODINGS 注册表 / get_encoding / list_encoding_names
│   ├── model.py               # 模型→编码映射 / encoding_for_model / encoding_name_for_model
│   ├── load.py                # 远程/缓存读取与 BPE 文件解析
│   ├── _educational.py        # 教学用 SimpleBytePairEncoding（非公开 API，F-003）
│   └── py.typed               # PEP 561 类型标记
├── tiktoken_ext/              # 插件扩展包（命名空间包）
│   └── openai_public.py       # 各公开 encoding 构造函数与 ENCODING_CONSTRUCTORS 注册表
├── src/                       # Rust 源（原生内核）
│   ├── lib.rs                 # CoreBPE / BPE 合并算法 / 错误类型 / 单元测试
│   └── py.rs                  # PyO3 绑定（_tiktoken 模块 / TiktokenBuffer）
├── tests/                     # 测试
│   ├── __init__.py
│   ├── test_encoding.py       # 编解码 roundtrip / special token / batch 行为约束
│   ├── test_helpers.py
│   ├── test_misc.py           # encoding_for_model 模型映射约束 / blobfile 惰性加载
│   ├── test_offsets.py        # decode_with_offsets 偏移断言
│   ├── test_pickle.py         # Encoding pickle 往返
│   └── test_simple_public.py  # 顶层 API 公开行为
├── scripts/                   # 工具脚本
│   ├── benchmark.py           # 吞吐基准（benchmark_batch）
│   ├── redact.py              # 发布前敏感信息清理
│   └── wheel_download.py      # wheels 构件下载
├── .github/workflows/build_wheels.yml   # CI 构建矩阵
├── pyproject.toml             # Python 构建元数据 / 依赖 / 版本
├── setup.py                   # 传统构建入口
├── Cargo.toml                 # Rust 包 / 依赖 / feature
├── MANIFEST.in                # sdist 文件清单
├── .gitignore / LICENSE / README.md / CHANGELOG.md / perf.svg
└── .git/                      # 本地 git 元数据（分支 main）
```

## 子模块文件与 facts 覆盖映射

| 源码文件 | 相对路径 | 覆盖事实文档 |
|---|---|---|
| `tiktoken/__init__.py` | `tiktoken/__init__.py` | `references/facts-python.md`（F-001~F-003） |
| `tiktoken/core.py` | `tiktoken/core.py` | `references/facts-python.md`（F-004~F-042） |
| `tiktoken/registry.py` | `tiktoken/registry.py` | `references/facts-python.md`（F-043~F-051） |
| `tiktoken/model.py` | `tiktoken/model.py` | `references/facts-python.md`（F-052~F-055） |
| `tiktoken/load.py` | `tiktoken/load.py` | `references/facts-python.md`（F-056~F-069） |
| `tiktoken/_educational.py` | `tiktoken/_educational.py` | `references/facts-python.md`（F-070~F-082） |
| `tiktoken_ext/openai_public.py` | `tiktoken_ext/openai_public.py` | `references/facts-python.md`（F-083~F-096） |
| `src/lib.rs` | `src/lib.rs` | `references/facts-rust.md`（F-001~F-034） |
| `src/py.rs` | `src/py.rs` | `references/facts-rust.md`（F-035~F-052） |
| `Cargo.toml` | `Cargo.toml` | `references/facts-rust.md`（F-053~F-056） |
| `tests/test_*.py` | `tests/` | `references/facts-rust.md`（F-057~F-068，行为约束） |
| `scripts/*.py` | `scripts/` | `references/facts-rust.md`（F-069~F-071，工具类事实） |

## 构建与依赖

### Python 侧（`pyproject.toml`）

- **Python 版本门槛**：`requires-python = ">=3.9"`
- **运行依赖**：`regex`、`requests`
- **可选依赖**：`blobfile >=3`（extra `blobfile`，用于远端/云存储读取）
- **构建后端**：`setuptools.build_meta`，`requires = ["setuptools>=62.4", "wheel", "setuptools-rust>=1.5.2"]`——通过 `setuptools-rust` 将 Rust 扩展编译为 Python 扩展模块（即 `_tiktoken`）
- **CI**：`tool.cibuildwheel` 定义多平台 wheels 构建矩阵

### Rust 侧（`Cargo.toml`）

- **包**：`edition = "2024"`；`crate-type = ["cdylib", "rlib"]`——同时编译为 Python 动态扩展库与 Rust 库（F-054）
- **Feature**：`default = []`；`python = ["pyo3"]`（F-055）——`src/py.rs` 仅在启用 `python` feature 时经 `#[cfg(feature = "python")] mod py;` 编译
- **依赖**：
  - `pyo3 0.29.2`（optional，features `extension-module` + `macros`）
  - `fancy-regex 0.19.0`（Unicode 级正则回看，`special_token_regex` 等使用）
  - `regex 1.13.1`（普通分词正则）
  - `rustc-hash 2`（`FxHashMap` 快速哈希）
  - `bstr 1.13.1`（字节字符串处理）

### 命名空间 / 模块名要点

- Python 公开门面：`tiktoken.core.Encoding`、`tiktoken.model.encoding_for_model/encoding_name_for_model`、`tiktoken.registry.get_encoding/list_encoding_names`（F-001）
- Rust 原生扩展：Python 侧以 `tiktoken._tiktoken` 导入（`core.py` 第 7 行），对应 Rust `#[pymodule] fn _tiktoken`（F-035 / F-011）；**不存在 `tiktoken._core` 模块**（F-035，facts-rust）
- 插件机制：`tiktoken_ext.openai_public` 通过 `ENCODING_CONSTRUCTORS` 提供各 encoding 构造函数，由 `registry._find_constructors` 动态发现（F-047、F-093）

## 相关信源文档

- [Python 门面层事实清单](facts-python.md)：96 条，覆盖 `tiktoken/` 包与 `tiktoken_ext/`
- [Rust 核心事实清单](facts-rust.md)：71 条，覆盖 `src/`、`Cargo.toml`、`tests/`、`scripts/`
- [背景调研](background-research.md) 与 [洞察](insights.md)：分析侧产出