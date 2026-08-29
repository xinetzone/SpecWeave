---
type: Concept
title: 注册表与模型映射
description: tiktoken 双入口解析机制——registry.get_encoding 的 Lazy 构造与 tiktoken_ext 插件发现、model.encoding_for_model 的精确映射加前缀降级链
tags: [tiktoken, registry, model, 注册表, 映射, bpe]
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

# 注册表与模型映射

tiktoken 对外暴露两个独立但不并列的编码加载入口：`get_encoding`（按编码名）与 `encoding_for_model`（按模型名）。二者分别由 `registry.py` 与 `model.py` 实现，且 `encoding_for_model` 最终回落到 `get_encoding`（F-055）。理解这两套机制，就理解了"编码从哪来"。

## 注册表：get_encoding 与 Lazy 构造

`registry.py` 维护三层模块级状态（F-043~F-045）：

- `_lock = threading.RLock()`：保护注册表读写的重入锁；
- `ENCODINGS: dict[str, Encoding] = {}`：已构造的编码实例缓存；
- `ENCODING_CONSTRUCTORS: dict[str, Callable[[], dict[str, Any]]] | None = None`：编码名 → 构造函数，初始为 `None`。

### 插件发现机制（_find_constructors）

构造函数不是硬编码的，而是从 **`tiktoken_ext` 命名空间插件包**动态发现（F-046~F-047）：

- `_available_plugin_modules()`（`@functools.lru_cache` 装饰）用 `pkgutil.iter_modules(tiktoken_ext.__path__, ...)` 遍历 `tiktoken_ext` 下的子模块；
- `_find_constructors()` 持 `_lock` 状态下，若 `ENCODING_CONSTRUCTORS` 已非 `None` 直接返回；否则为每个插件模块执行 `importlib.import_module`，取模块属性 `mod.ENCODING_CONSTRUCTORS`；模块缺该属性或出现重复编码名时抛 `ValueError`。

默认安装下，`tiktoken_ext/openai_public.py` 提供 `ENCODING_CONSTRUCTORS`，注册七种公开编码 `gpt2`/`r50k_base`/`p50k_base`/`p50k_edit`/`cl100k_base`/`o200k_base`/`o200k_harmony`（F-093）。

### get_encoding 的执行链

```
get_encoding(name)                    # F-048~F-050
├─ 非 str 入参 → ValueError
├─ 命中 ENCODINGS 缓存（持锁二次检查）→ 直接返回
├─ ENCODING_CONSTRUCTORS is None → _find_constructors()
├─ name 不在构造器 → ValueError（含 Plugins found / version 信息）
└─ enc = Encoding(**constructor())；写入 ENCODINGS；返回
```

关键约束：构造函数返回的 dict 键必须与 `Encoding.__init__` 的 keyword-only 参数（`pat_str`、`mergeable_ranks`、`special_tokens`、`explicit_n_vocab`）对齐，`name` 作为位置参数传入（F-096）。

`list_encoding_names()` 返回 `list(ENCODING_CONSTRUCTORS)`，即所有可用编码名（F-051）。

## 模型映射：encoding_for_model 的三级降级链

`model.py` 维护两张映射表：

- `MODEL_TO_ENCODING: dict[str, str]`（F-053）：精确映射已知模型，覆盖 reasoning/chat/base/embeddings 分组，含 DEPRECATED 模型与开源 `gpt2`/`gpt-2`；
- `MODEL_PREFIX_TO_ENCODING: dict[str, str]`（F-052）：前缀映射模型族，如 `"o1-"→"o200k_base"`、`"gpt-4o-"→"o200k_base"`、`"gpt-4-"→"cl100k_base"`、`"gpt-oss-"→"o200k_harmony"` 等，同一编码被多个前缀共享。

`encoding_name_for_model(model)` 的解析顺序（F-054）：

```python
def encoding_name_for_model(model_name):
    if model_name in MODEL_TO_ENCODING:      # 1. 精确查表
        return MODEL_TO_ENCODING[model_name]
    for prefix, encoding in MODEL_PREFIX_TO_ENCODING.items():  # 2. 前缀匹配
        if model_name.startswith(prefix):
            return encoding
    raise KeyError(...)                      # 3. 均未命中 → 提示改用 get_encoding
```

`encoding_for_model(model)` 返回 `get_encoding(encoding_name_for_model(model))`（F-055），把 model.py 与 registry.py 串联起来。行为约束示例（facts-rust F-065）：`gpt-4o→o200k_base`、`gpt-3.5-turbo-0301→cl100k_base`、`gpt-oss-120b→o200k_harmony`。

> 设计要点：模型映射刻意采用"精确映射 + 前缀兜底"的宽容策略。前缀表甚至涵盖 `gpt-4.5-`、`gpt-4.1-` 等未来模型族（F-052），使其成为"命名空间路由"而非静态清单；而 `encoding_name_for_model` 对未知模型抛 `KeyError` 并建议改用 `get_encoding`，等于把"按编码名加载"定义为更底层、更可控的权威入口。

## 相关概念

- [01 安装与快速上手](/concepts/01-getting-started.md)：`get_encoding`/`encoding_for_model` 的最小用法
- [02 Encoding 对象核心 API](/concepts/02-encoding-api.md)：`Encoding(**constructor())` 的实例化协议
- [00 整体架构](/concepts/00-overview.md)：公开 API 全貌
- 编排总览：[架构洞察](/references/insights.md)
- 事实来源：[Python 事实清单](/references/facts-python.md)