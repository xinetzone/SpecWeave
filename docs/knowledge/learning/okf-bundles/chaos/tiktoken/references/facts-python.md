---
type: Facts
title: tiktoken Python 门面层事实清单
description: 从 tiktoken v0.14.0 源码采集的 Python 门面层事实，每条标注文件路径
tags: [tiktoken, bpe, tokenizer, facts, python, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
source_id: tiktoken-python
---

# 采集范围

本清单从 tiktoken v0.14.0 的 Python 源码逐行采集，覆盖以下文件（相对路径）：

- `tiktoken/__init__.py`
- `tiktoken/core.py`
- `tiktoken/registry.py`
- `tiktoken/model.py`
- `tiktoken/load.py`
- `tiktoken/_educational.py`
- `tiktoken_ext/openai_public.py`

每条事实仅陈述源码中实际存在的内容，不含推断。部分任务提示中提到的名称（如 `_encode_ordinary_native`、`_encode_native`、`string_ordinal`）在 v0.14.0 源码中不存在，已在对应小节如实标注。

---

## tiktoken/__init__.py

- F-001: `__init__.py` 第 2-6 行从子模块 re-export 公开 API：`from .core import Encoding as Encoding`、`from .model import encoding_for_model as encoding_for_model`、`from .model import encoding_name_for_model as encoding_name_for_model`、`from .registry import get_encoding as get_encoding`、`from .registry import list_encoding_names as list_encoding_names`。
- F-002: `__init__.py` 第 8 行定义模块级常量 `__version__ = "0.14.0"`。
- F-003: `__init__.py` 未导入 `load.py` 与 `_educational.py` 的符号；这两者不作为公开门面层 API 暴露。

## tiktoken/core.py

### 模块层辅助函数

- F-004: `core.py` 第 431-438 行定义模块级函数 `_special_token_regex(tokens: frozenset[str]) -> re.Pattern[str]`，用 `@functools.lru_cache(maxsize=128)` 装饰；函数体内先 `import regex as re`，捕获 `ImportError` 后回退 `import re`，以 `"|".join(re.escape(token) for token in tokens)` 拼接编译为 `f"({inner})"` 捕获分组。
- F-005: `core.py` 第 441-449 行定义模块级函数 `raise_disallowed_special_token(token: str) -> NoReturn`，无条件抛出 `ValueError`，错误消息包含 `allowed_special`、`disallowed_special` 的修复提示文案。

### Encoding.__init__

- F-006: `core.py` 第 16 行定义类 `Encoding`。第 17-25 行 `__init__` 签名：`Encoding(self, name: str, *, pat_str: str, mergeable_ranks: dict[bytes, int], special_tokens: dict[str, int], explicit_n_vocab: int | None = None)`；`name` 为位置参数，其余为 keyword-only。
- F-007: `core.py` 第 41-45 行 `__init__` 将入参存入实例属性：`self.name = name`、`self._pat_str = pat_str`、`self._mergeable_ranks = mergeable_ranks`、`self._special_tokens = special_tokens`。
- F-008: `core.py` 第 47-49 行 `__init__` 计算 `self.max_token_value = max(max(mergeable_ranks.values()), max(special_tokens.values(), default=0))`，即 mergeable_ranks 最大值与 special_tokens 最大值中的较大者。
- F-009: `core.py` 第 50-52 行 `__init__` 在 `explicit_n_vocab` 非零时执行两个断言：`len(mergeable_ranks) + len(special_tokens) == explicit_n_vocab`，且 `self.max_token_value == explicit_n_vocab - 1`。
- F-010: `core.py` 第 55 行 `__init__` 计算 `self._special_token_values = set(self._special_tokens.values())`。
- F-011: `core.py` 第 57 行 `__init__` 构造原生核心对象 `self._core_bpe = _tiktoken.CoreBPE(mergeable_ranks, special_tokens, pat_str)`；`_tiktoken` 为 `tiktoken` 扩展模块（第 7 行 `from tiktoken import _tiktoken`）。
- F-012: `core.py` 第 59-60 行定义 `__repr__`，返回字符串 `f"<Encoding {self.name!r}>"`。

### Encoding 公开方法（Encoding）

- F-013: `core.py` 第 66-80 行定义 `encode_ordinary(self, text: str) -> list[int]`；先调用 `self._core_bpe.encode_ordinary(text)`，捕获 `UnicodeEncodeError` 后执行 `text = text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")` 再重试 `encode_ordinary`。
- F-014: `core.py` 第 82-88 行定义 `encode(self, text: str, *, allowed_special: Literal["all"] | AbstractSet[str] = set(), disallowed_special: Literal["all"] | Collection[str] = "all") -> list[int]`；`allowed_special` 与 `disallowed_special` 均为 keyword-only，默认值分别为空集 `set()` 与字符串 `"all"`。
- F-015: `core.py` 第 116-124 行 `encode` 的特殊 token 处理逻辑：若 `allowed_special == "all"` 则赋为 `self.special_tokens_set`；若 `disallowed_special == "all"` 则赋为 `self.special_tokens_set - allowed_special`；若 `disallowed_special` 非空，非 `frozenset` 时转为 `frozenset`，并用 `_special_token_regex(disallowed_special).search(text)` 检查，命中则调用 `raise_disallowed_special_token(match.group())`。
- F-016: `core.py` 第 126-136 行 `encode` 调用 `self._core_bpe.encode(text, allowed_special)`；捕获 `UnicodeEncodeError` 时同样执行 surrogate-pair 修复重试：`text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")` 后再次调用 `self._core_bpe.encode(text, allowed_special)`。
- F-017: `core.py` 第 138-144 行定义 `encode_to_numpy(self, text: str, *, allowed_special=set(), disallowed_special="all") -> npt.NDArray[np.uint32]`，参数默认值与 `encode` 相同；执行与 `encode` 一致的特殊 token 预检逻辑（第 149-157 行）。
- F-018: `core.py` 第 159-162 行 `encode_to_numpy` 函数体内执行 `import numpy as np`，取 `self._core_bpe.encode_to_tiktoken_buffer(text, allowed_special)` 返回的 buffer，用 `np.frombuffer(buffer, dtype=np.uint32)` 转 numpy 数组。
- F-019: `core.py` 第 164-176 行定义 `encode_ordinary_batch(self, text: list[str], *, num_threads: int = 8) -> list[list[int]]`；用 `functools.partial(self.encode_ordinary)` 构造 encoder，在 `ThreadPoolExecutor(num_threads)` 内 `list(e.map(encoder, text))`。
- F-020: `core.py` 第 178-185 行定义 `encode_batch(self, text: list[str], *, num_threads: int = 8, allowed_special=set(), disallowed_special="all") -> list[list[int]]`；第 195-200 行先处理 `allowed_special`/`disallowed_special`（`"all"` 展开、非空转 `frozenset`），再 `functools.partial(self.encode, ...)` 并用 `ThreadPoolExecutor` 并行映射。
- F-021: `core.py` 第 208-214 行定义 `encode_with_unstable(self, text: str, *, allowed_special=set(), disallowed_special="all") -> tuple[list[int], list[list[int]]]`；第 233-241 行执行与 `encode` 一致的特殊 token 预检，第 243 行返回 `self._core_bpe.encode_with_unstable(text, allowed_special)`。
- F-022: `core.py` 第 245-259 行定义 `encode_single_token(self, text_or_bytes: str | bytes) -> int`；若入参为 `str`，先 `text_or_bytes.encode("utf-8")` 转字节，再调用 `self._core_bpe.encode_single_token(text_or_bytes)` 返回 int；文档注明 token 不在词表时抛出 `KeyError`。

### Encoding 公开方法（Decoding）

- F-023: `core.py` 第 265-273 行定义 `decode_bytes(self, tokens: Sequence[int]) -> bytes`，直接返回 `self._core_bpe.decode_bytes(tokens)`。
- F-024: `core.py` 第 275-287 行定义 `decode(self, tokens: Sequence[int], errors: str = "replace") -> str`，返回 `self._core_bpe.decode_bytes(tokens).decode("utf-8", errors=errors)`；`errors` 默认 `"replace"`。
- F-025: `core.py` 第 289-301 行定义 `decode_single_token_bytes(self, token: int) -> bytes`，直接返回 `self._core_bpe.decode_single_token_bytes(token)`；文档注明 token 不在词表时抛出 `KeyError`。
- F-026: `core.py` 第 303-310 行定义 `decode_tokens_bytes(self, tokens: Sequence[int]) -> list[bytes]`，对每个 token 调用 `decode_single_token_bytes` 生成字节列表。
- F-027: `core.py` 第 312-335 行定义 `decode_with_offsets(self, tokens: Sequence[int]) -> tuple[str, list[int]]`；第 325 行先取 `token_bytes = self.decode_tokens_bytes(tokens)`；第 327-331 行计算 offsets，对每个 token 追加 `max(0, text_len - (0x80 <= token[0] < 0xC0))`，`text_len` 累加 `sum(1 for c in token if not 0x80 <= c < 0xC0)`；第 334 行以 `errors="strict"` 解码，返回 `(text, offsets)`。
- F-028: `core.py` 第 337-343 行定义 `decode_batch(self, batch, *, errors: str = "replace", num_threads: int = 8) -> list[str]`；`functools.partial(self.decode, errors=errors)` 后 `ThreadPoolExecutor` 并行映射。
- F-029: `core.py` 第 345-350 行定义 `decode_bytes_batch(self, batch, *, num_threads: int = 8) -> list[bytes]`；`ThreadPoolExecutor` 并行执行 `self.decode_bytes`。

### Encoding 公开/属性方法（Miscellaneous）

- F-030: `core.py` 第 356-358 行定义 `token_byte_values(self) -> list[bytes]`，返回 `self._core_bpe.token_byte_values()`。
- F-031: `core.py` 第 360-362 行定义属性 `eot_token`（`@property`），返回 `self._special_tokens["<|endoftext|>"]`；按键缺失会抛出 `KeyError`。
- F-032: `core.py` 第 364-366 行定义缓存属性 `special_tokens_set`（`@functools.cached_property`），返回 `set(self._special_tokens.keys())`。
- F-033: `core.py` 第 368-370 行定义 `is_special_token(self, token: int) -> bool`，先 `assert isinstance(token, int)`，返回 `token in self._special_token_values`。
- F-034: `core.py` 第 372-375 行定义属性 `n_vocab`（`@property`），返回 `self.max_token_value + 1`；docstring 标注为向后兼容并建议使用 `enc.max_token_value + 1`。

### Encoding 私有方法

- F-035: `core.py` 第 381-393 行定义 `_encode_single_piece(self, text_or_bytes: str | bytes) -> list[int]`；入参为 `str` 时先 `encode("utf-8")` 转字节，再调用 `self._core_bpe.encode_single_piece(text_or_bytes)`；dict 文档注明不编码任何 special token。
- F-036: `core.py` 第 395-404 行定义 `_encode_only_native_bpe(self, text: str) -> list[int]`；函数体内 `import regex`，`regex.compile(self._pat_str)` 编译，`for piece in regex.findall(_unused_pat, text)` 逐个 piece 调用 `self._core_bpe.encode_single_piece(piece.encode("utf-8"))` 并 extend 到列表；即在 Python 侧完成 regex 切分。
- F-037: `core.py` 第 406-407 行定义 `_encode_bytes(self, text: bytes) -> list[int]`，直接返回 `self._core_bpe._encode_bytes(text)`。
- F-038: `core.py` 第 409-420 行定义 `__getstate__`：函数体内 `import tiktoken.registry`；若 `self is tiktoken.registry.ENCODINGS.get(self.name)` 成立则返回字符串 `self.name`（按引用 pickle）；否则返回包含 `name`/`pat_str`/`mergeable_ranks`/`special_tokens` 的字典。
- F-039: `core.py` 第 422-428 行定义 `__setstate__`：函数体内 `import tiktoken.registry`；若 `value` 为 `str`，则将 `self.__dict__` 设为 `tiktoken.registry.get_encoding(value).__dict__`；否则执行 `self.__init__(**value)`。

### 版本差异说明（v0.14.0 不存在的方法）

- F-040: `core.py` 全文件中不存在 `_encode_ordinary_native` 方法——无该函数定义。
- F-041: `core.py` 全文件中不存在 `_encode_native` 方法——无该函数定义；实际提供的是 `_encode_only_native_bpe`（见 F-036）与 `_encode_bytes`（见 F-037）。
- F-042: `core.py` 全文件中不存在 `string_ordinal` 方法——无该函数定义。

## tiktoken/registry.py

- F-043: `registry.py` 第 14 行定义模块级常量 `_lock = threading.RLock()`。
- F-044: `registry.py` 第 15 行定义模块级注册表 `ENCODINGS: dict[str, Encoding] = {}`。
- F-045: `registry.py` 第 16 行定义模块级变量 `ENCODING_CONSTRUCTORS: dict[str, Callable[[], dict[str, Any]]] | None = None`，初始为 `None`。
- F-046: `registry.py` 第 19-30 行定义 `@functools.lru_cache` 装饰的 `_available_plugin_modules() -> Sequence[str]`；用 `pkgutil.iter_modules(tiktoken_ext.__path__, tiktoken_ext.__name__ + ".")` 遍历 `tiktoken_ext` 命名空间包下的子模块名并收集成列表。
- F-047: `registry.py` 第 33-58 行定义 `_find_constructors()`（`global ENCODING_CONSTRUCTORS`）；持锁状态下若 `ENCODING_CONSTRUCTORS is not None` 直接返回，否则置为空字典后遍历 `_available_plugin_modules()`，为每个模块执行 `importlib.import_module(mod_name)`，取模块属性 `mod.ENCODING_CONSTRUCTORS`；模块缺少该属性时抛 `ValueError`（"does not define ENCODING_CONSTRUCTORS"）；遇到重复 encoding name 时抛 `ValueError`（"Duplicate encoding name"）；异常时置 `ENCODING_CONSTRUCTORS = None` 并重新抛出。
- F-048: `registry.py` 第 63-88 行定义 `get_encoding(encoding_name: str) -> Encoding`；第 64-65 行对非 `str` 入参抛 `ValueError`（"Expected a string in get_encoding"）；第 67-72 行先查 `ENCODINGS` 缓存（含持锁二次检查），命中则直接返回。
- F-049: `registry.py` 第 74-83 行 `get_encoding` 在 `ENCODING_CONSTRUCTORS is None` 时调用 `_find_constructors()`；若 encoding_name 不在 `ENCODING_CONSTRUCTORS` 则抛 `ValueError`，错误消息含 `Plugins found` 与 `tiktoken version` 信息。
- F-050: `registry.py` 第 85-88 行 `get_encoding` 取 `constructor = ENCODING_CONSTRUCTORS[encoding_name]`，执行 `enc = Encoding(**constructor())`，写入 `ENCODINGS[encoding_name] = enc` 后返回；Lazy 构造并缓存。
- F-051: `registry.py` 第 91-96 行定义 `list_encoding_names() -> list[str]`；持锁状态下若 `ENCODING_CONSTRUCTORS is None` 调用 `_find_constructors()`，返回 `list(ENCODING_CONSTRUCTORS)`。

## tiktoken/model.py

- F-052: `model.py` 第 7-27 行定义模块级字典 `MODEL_PREFIX_TO_ENCODING: dict[str, str]`；条目含：`"o1-"→"o200k_base"`、`"o3-"→"o200k_base"`、`"o4-mini-"→"o200k_base"`、`"gpt-5"→"o200k_base"`、`"gpt-4.5-"→"o200k_base"`、`"gpt-4.1-"→"o200k_base"`、`"chatgpt-4o-"→"o200k_base"`、`"gpt-4o-"→"o200k_base"`、`"gpt-4-"→"cl100k_base"`、`"gpt-3.5-turbo-"→"cl100k_base"`、`"gpt-35-turbo-"→"cl100k_base"`、`"gpt-oss-"→"o200k_harmony"`、`"ft:gpt-4o"→"o200k_base"`、`"ft:gpt-4"→"cl100k_base"`、`"ft:gpt-3.5-turbo"→"cl100k_base"`、`"ft:davinci-002"→"cl100k_base"`、`"ft:babbage-002"→"cl100k_base"`。
- F-053: `model.py` 第 29-85 行定义模块级字典 `MODEL_TO_ENCODING: dict[str, str]`，按注释分组涵盖 reasoning（`o1`/`o3`/`o4-mini`→`o200k_base`）、chat（`gpt-5`/`gpt-4.1`/`gpt-4o`→`o200k_base`；`gpt-4`/`gpt-3.5-turbo`/`gpt-3.5`/`gpt-35-turbo`→`cl100k_base`）、base（`davinci-002`/`babbage-002`→`cl100k_base`）、embeddings（`text-embedding-ada-002`/`text-embedding-3-small`/`text-embedding-3-large`→`cl100k_base`），以及 DEPRECATED 模型映射（text/code/edit/old embeddings 系列→`p50k_base`/`r50k_base`/`p50k_edit`），开源模型 `gpt2`/`gpt-2`→`gpt2`。
- F-054: `model.py` 第 88-106 行定义 `encoding_name_for_model(model_name: str) -> str`；先查 `MODEL_TO_ENCODING` 命中返回（第 93-94 行）；否则遍历 `MODEL_PREFIX_TO_ENCODING.items()`，当 `model_name.startswith(model_prefix)` 时返回对应 encoding_name（第 99-101 行）；均未命中则抛 `KeyError`，消息提示改用 `tiktoken.get_encoding`（第 103-106 行）。
- F-055: `model.py` 第 109-114 行定义 `encoding_for_model(model_name: str) -> Encoding`，返回 `get_encoding(encoding_name_for_model(model_name))`。

## tiktoken/load.py

- F-056: `load.py` 第 8-27 行定义 `read_file(blobpath: str) -> bytes`；路径不含 `"://"` 时以 `open(blobpath, "rb", buffering=0)` 读取；以 `("http://", "https://")` 开头时 `import requests` 后 `requests.get(blobpath)`、`resp.raise_for_status()` 并返回 `resp.content`；其余路径尝试 `import blobfile`，未安装时抛 `ImportError`（提示 `pip install blobfile`），成功则返回 `blobfile.read_bytes(blobpath)`。
- F-057: `load.py` 第 30-32 行定义 `check_hash(data: bytes, expected_hash: str) -> bool`，返回 `hashlib.sha256(data).hexdigest() == expected_hash`。
- F-058: `load.py` 第 35-86 行定义 `read_file_cached(blobpath: str, expected_hash: str | None = None) -> bytes`；缓存目录解析顺序：`TIKTOKEN_CACHE_DIR` > `DATA_GYM_CACHE_DIR` > 默认 `tempfile.gettempdir()/data-gym-cache`；`cache_dir == ""` 时禁用缓存直接 `read_file`（第 47-49 行）。
- F-059: `load.py` 第 51-64 行 `read_file_cached` 以 `hashlib.sha1(blobpath.encode()).hexdigest()` 作为 `cache_key`，缓存路径为 `os.path.join(cache_dir, cache_key)`；命中且 `expected_hash is None or check_hash(data, expected_hash)` 时返回缓存数据；哈希不符则 `os.remove(cache_path)`（失败的 `OSError` 被忽略）。
- F-060: `load.py` 第 66-71 行 `read_file_cached` 重新 `read_file` 后，若 `expected_hash` 且 `check_hash` 失败则抛 `ValueError`（"Hash mismatch..."）。
- F-061: `load.py` 第 73-86 行 `read_file_cached` 写入缓存：先 `os.makedirs(cache_dir, exist_ok=True)`，写临时文件 `cache_path + "." + str(uuid.uuid4()) + ".tmp"`，再 `os.rename` 到 `cache_path`；`OSError` 时仅当 `user_specified_cache` 为 True 才重新抛出。
- F-062: `load.py` 第 89-144 行定义 `data_gym_to_mergeable_bpe_ranks(vocab_bpe_file: str, encoder_json_file: str, vocab_bpe_hash: str | None = None, encoder_json_hash: str | None = None, clobber_one_byte_tokens: bool = False) -> dict[bytes, int]`。
- F-063: `load.py` 第 97-99 行 `data_gym_to_mergeable_bpe_ranks` 构造 `rank_to_intbyte`（0-255 中可打印且非空格的单字节）与 `data_gym_byte_to_byte` 映射；第 100-105 行为不可打印字节补充偏移 `chr(2**8 + n)`；第 106 行断言 `len(rank_to_intbyte) == 2**8`。
- F-064: `load.py` 第 109-110 行 `data_gym_to_mergeable_bpe_ranks` 以 `read_file_cached(vocab_bpe_file, vocab_bpe_hash).decode()` 读取，按行第二个元素起解析 `bpe_merges`。
- F-065: `load.py` 第 117-124 行 `data_gym_to_mergeable_bpe_ranks` 先建单字节 token `{bytes([b]): i}`，再按 merge 顺序追加合并 token `bpe_ranks[decode(first)+decode(second)] = n`。
- F-066: `load.py` 第 131-142 行 `data_gym_to_mergeable_bpe_ranks` 读取 encoder.json 并断言与 merge 表一致；`encoder_json_loaded` 弹出 `b"<|endoftext|>"` 与 `b"<|startoftext|>"`（第 134-135 行）；`clobber_one_byte_tokens=True` 时用 encoder_json 覆盖单字节 rank（第 137-140 行）；最后 `assert bpe_ranks == encoder_json_loaded`。
- F-067: `load.py` 第 147-156 行定义 `dump_tiktoken_bpe(bpe_ranks: dict[bytes, int], tiktoken_bpe_file: str) -> None`；`import blobfile`（未安装抛 `ImportError`），用 `blobfile.BlobFile(tiktoken_bpe_file, "wb")` 按 rank 排序写入 `base64.b64encode(token) + b" " + str(rank).encode() + b"\n"`。
- F-068: `load.py` 第 159-171 行定义 `load_tiktoken_bpe(tiktoken_bpe_file: str, expected_hash: str | None = None) -> dict[bytes, int]`；用 `read_file_cached` 读取，逐行 `line.split()` 解析，`ret[base64.b64decode(token)] = int(rank)` 填充；解析异常时抛 `ValueError`（含该行内容与文件名）。
- F-069: `load.py` 未定义任何名为 `load_async` 的函数；该文件不包含协程/异步 I/O 函数。本清单采集范围内的全部 `tiktoken/` 目录 `.py` 文件均无 `load_async`。

## tiktoken/_educational.py

- F-070: `_educational.py` 第 12 行定义类 `SimpleBytePairEncoding`；第 13 行 `__init__(self, *, pat_str: str, mergeable_ranks: dict[bytes, int])`（keyword-only）。
- F-071: `_educational.py` 第 16-18 行 `SimpleBytePairEncoding.__init__` 保存 `self.pat_str`、`self.mergeable_ranks`；第 20 行构建 `self._decoder = {token: token_bytes for token_bytes, token in mergeable_ranks.items()}`；第 21 行 `self._pat = regex.compile(pat_str)`。
- F-072: `_educational.py` 第 23-37 行定义 `SimpleBytePairEncoding.encode(self, text: str, visualise: str | None = "colour") -> list[int]`；`self._pat.findall(text)` 切分单词，逐词 `word.encode("utf-8")` 后调用 `bpe_encode(self.mergeable_ranks, word_bytes, visualise=visualise)` 收集 token。
- F-073: `_educational.py` 第 39-45 行定义 `SimpleBytePairEncoding.decode_bytes(self, tokens: list[int]) -> bytes`，返回 `b"".join(self._decoder[token] for token in tokens)`。
- F-074: `_educational.py` 第 47-56 行定义 `SimpleBytePairEncoding.decode(self, tokens: list[int]) -> str`，返回 `decode_bytes(...).decode("utf-8", errors="replace")`。
- F-075: `_educational.py` 第 58-66 行定义 `SimpleBytePairEncoding.decode_tokens_bytes(self, tokens: list[int]) -> list[bytes]`，逐 token 返回 `self._decoder[token]`。
- F-076: `_educational.py` 第 68-72 行定义静态方法 `SimpleBytePairEncoding.train(training_data: str, vocab_size: int, pat_str: str)`，调用 `bpe_train(...)` 得 `mergeable_ranks` 后构造并返回 `SimpleBytePairEncoding`。
- F-077: `_educational.py` 第 74-80 行定义静态方法 `SimpleBytePairEncoding.from_tiktoken(encoding)`；入参为 `str` 时 `tiktoken.get_encoding(encoding)`，以 `encoding._pat_str` 与 `encoding._mergeable_ranks` 构造实例。
- F-078: `_educational.py` 第 83-116 行定义模块级函数 `bpe_encode(mergeable_ranks: dict[bytes, int], input: bytes, visualise: str | None = "colour") -> list[int]`；按字节拆分为 parts，循环寻找最低 rank 的相邻 pair 合并（`mergeable_ranks.get(pair[0]+pair[1])`），无合并对时结束；`visualise` 取值 `["colour","color"]` 时调用 `visualise_tokens(parts)`，取值 `"simple"` 时 `print(parts)`；最终返回 `[mergeable_ranks[part] for part in parts]`。
- F-079: `_educational.py` 第 119-185 行定义模块级函数 `bpe_train(data: str, vocab_size: int, pat_str: str, visualise: str | None = "colour") -> dict[bytes, int]`；第 123-124 行 `vocab_size < 2**8` 时抛 `ValueError`；先为 0-255 单字节建 rank（第 125-127 行），用 `regex.findall(pat_str, data)` 切词（第 135-137 行），循环 `while len(ranks) < vocab_size`：基于 `collections.Counter` 统计相邻 pair 频次，取 `max` 得到 `most_common_pair`，加为新 token 并合并所有 word 中的该 pair（第 140-170 行）。
- F-080: `_educational.py` 第 188-205 行定义模块级函数 `visualise_tokens(token_values: list[bytes]) -> None`；用 ANSI 背景色序列着色打印，token 边界处用 `errors="replace"` 解码，结尾输出 `"\u001b[0m"`。
- F-081: `_educational.py` 第 208-223 行定义模块级函数 `train_simple_encoding()`；内置 `gpt2_pattern` 正则，以 `with open(__file__)` 读取本文件为训练数据，`SimpleBytePairEncoding.train(data, vocab_size=600, pat_str=gpt2_pattern)` 训练，并断言 `enc.decode(tokens) == "hello world"` 等三条断言，返回 `enc`。
- F-082: `_educational.py` 通篇未出现名为 `SimpleBytePairDecoder` 的类；文件中定义的类仅为 `SimpleBytePairEncoding`（见 F-070）。

## tiktoken_ext/openai_public.py

- F-083: `openai_public.py` 第 1 行 `from tiktoken.load import data_gym_to_mergeable_bpe_ranks, load_tiktoken_bpe`。
- F-084: `openai_public.py` 第 3-7 行定义特殊 token 常量：`ENDOFTEXT = "<|endoftext|>"`、`FIM_PREFIX = "<|fim_prefix|>"`、`FIM_MIDDLE = "<|fim_middle|>"`、`FIM_SUFFIX = "<|fim_suffix|>"`、`ENDOFPROMPT = "<|endofprompt|>"`。
- F-085: `openai_public.py` 第 12-14 行定义模块级正则 `r50k_pat_str`，值为 `"'(?:[sdmt]|ll|ve|re)| ?\p{L}++| ?\p{N}++| ?[^\s\p{L}\p{N}]++|\s++$|\s+(?!\S)|\s"`；注释说明其为 GPT-2 原始 pattern 的等价快速变体。
- F-086: `openai_public.py` 第 17-30 行定义 `gpt2()`，调用 `data_gym_to_mergeable_bpe_ranks`，入参 `vocab_bpe_file`/`encoder_json_file` 为 gpt-2 远程 blob URL，`vocab_bpe_hash="1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5"`、`encoder_json_hash="196139668be63f3b5d6574427317ae82f612a97c5d1cdaf36ed2256dbf636783"`；返回 dict 含 `name="gpt2"`、`explicit_n_vocab=50257`、`pat_str=r50k_pat_str`、`special_tokens={ENDOFTEXT: 50256}`。
- F-087: `openai_public.py` 第 33-44 行定义 `r50k_base()`，`load_tiktoken_bpe(".../encodings/r50k_base.tiktoken", expected_hash="306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930")`；返回 dict 含 `name="r50k_base"`、`explicit_n_vocab=50257`、`pat_str=r50k_pat_str`、`special_tokens={ENDOFTEXT: 50256}`。
- F-088: `openai_public.py` 第 47-58 行定义 `p50k_base()`，`load_tiktoken_bpe(".../encodings/p50k_base.tiktoken", expected_hash="94b5ca7dff4d00767bc256fdd1b27e5b17361d7b8a5f968547f9f23eb70d2069")`；返回 dict 含 `name="p50k_base"`、`explicit_n_vocab=50281`、`pat_str=r50k_pat_str`、`special_tokens={ENDOFTEXT: 50256}`。
- F-089: `openai_public.py` 第 61-72 行定义 `p50k_edit()`，复用 p50k 的 BPE 文件与哈希（同 F-088），`special_tokens={ENDOFTEXT: 50256, FIM_PREFIX: 50281, FIM_MIDDLE: 50282, FIM_SUFFIX: 50283}`；返回 dict 含 `name="p50k_edit"`、`pat_str=r50k_pat_str`（未设 `explicit_n_vocab`）。
- F-090: `openai_public.py` 第 75-92 行定义 `cl100k_base()`，`load_tiktoken_bpe(".../encodings/cl100k_base.tiktoken", expected_hash="223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7")`；`special_tokens={ENDOFTEXT: 100257, FIM_PREFIX: 100258, FIM_MIDDLE: 100259, FIM_SUFFIX: 100260, ENDOFPROMPT: 100276}`；`pat_str` 为独立的一行正则 `"'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s"`；返回 dict 未含 `explicit_n_vocab`。
- F-091: `openai_public.py` 第 95-120 行定义 `o200k_base()`，`load_tiktoken_bpe(".../encodings/o200k_base.tiktoken", expected_hash="446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d")`；`special_tokens={ENDOFTEXT: 199999, ENDOFPROMPT: 200018}`；`pat_str` 由 7 个子正则 `"|".join([...])` 拼成，子项覆盖大小写字母/数字标点/换行/空白等分支（第 104-114 行）；返回 dict 未含 `explicit_n_vocab`。
- F-092: `openai_public.py` 第 123-151 行定义 `o200k_harmony()`；以 `o200k_base()` 结果为基础，`pat_str`/`mergeable_ranks` 复用 base，`special_tokens` 在 base 之上追加 `<|startoftext|>:199998`、`<|endoftext|>:199999`、`<|reserved_200000|>:200000` 至 `<|reserved_200011|>:200011`、`<|call|>:200012`，并追加 `{f"<|reserved_{i}|>": i for i in range(200013, 201088)}`；返回 dict 含 `name="o200k_harmony"`。
- F-093: `openai_public.py` 第 154-162 行定义模块级注册表 `ENCODING_CONSTRUCTORS`，映射 key→构造函数：`"gpt2"→gpt2`、`"r50k_base"→r50k_base`、`"p50k_base"→p50k_base`、`"p50k_edit"→p50k_edit`、`"cl100k_base"→cl100k_base`、`"o200k_base"→o200k_base`、`"o200k_harmony"→o200k_harmony`。

## 关键数据对照补充

- F-094: 各公开 encoding 的 `explicit_n_vocab` 字段仅在 `gpt2`（50257）、`r50k_base`（50257）、`p50k_base`（50281）三个构造函数 dict 中出现；`p50k_edit`、`cl100k_base`、`o200k_base`、`o200k_harmony` 四个构造 dict 不含该字段。
- F-095: 各公开 encoding 的 `pat_str` 来源：`gpt2`/`r50k_base`/`p50k_base`/`p50k_edit` 均使用共享常量 `r50k_pat_str`；`cl100k_base` 与 `o200k_base`/`o200k_harmony` 使用各自独立定义的正则字符串。
- F-096: registry 的 `get_encoding` 通过 `Encoding(**constructor())` 实例化 Encoding，因而各构造函数 dict 的键必须与 `Encoding.__init__` 的 keyword-only 参数（`pat_str`、`mergeable_ranks`、`special_tokens`、`explicit_n_vocab`）对齐；`name` 键作为位置参数 `name` 传入。