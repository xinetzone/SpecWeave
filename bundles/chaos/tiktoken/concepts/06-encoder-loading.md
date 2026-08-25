---
type: Concept
title: BPE 词表加载与缓存
description: 解析 tiktoken load.py 的读文件多路径、SHA1 缓存键与 SHA256 校验、磁盘原子写，以及 data-gym 与 tiktoken 两种词表格式的解析流程
tags: [tiktoken, bpe, load, cache, sha1, sha256, data-gym, blobfile] 
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
sources:
  - id: tiktoken-source
    resource: "/references/source.md"
    title: tiktoken v0.14.0 源码信源登记
  - id: tiktoken-python
    resource: "/references/facts-python.md"
    title: Python 门面层事实清单
  - id: tiktoken-rust
    resource: "/references/facts-rust.md"
    title: Rust 核心事实清单
---

# BPE 词表加载与缓存

`Encoding` 的完整 token 空间由 `pat_str`（预分词正则）、`mergeable_ranks`（可合并 BPE 字节 token 的 rank 表）与 `special_tokens`（特殊 token 的 id 映射）三元组定义（facts-python F-006）。其中 `mergeable_ranks`——一张把原始字节序列映射为整数 rank 的词表——需要外部文件承载，因此 tiktoken 必须解决"词表文件从哪来、如何安全加载、如何缓存复用"的问题。这一整套机制全部集中在 `tiktoken/load.py`。

`load.py` 的核心职责有二：一是**读取**词表文件（支持本地路径、HTTP/HTTPS URL、云存储三种来源，并叠加磁盘缓存），二是**解析**词表格式（支持 `data-gym` 与 `tiktoken` 两种历史文件格式）。它位于 `registry`（/concepts/05-registry-model.md）与具体词汇实现（/concepts/07-openai-vocabularies.md）之间，是"编码构造函数 → 真实词表"的最后一公里。

## 读取：read_file 的多路径分发

`read_file(blobpath: str) -> bytes`（facts-python F-056）根据路径字符串形态走三条分支：

1. **本地文件**：路径不含 `"://"` 时，直接用 `open(blobpath, "rb", buffering=0)` 以无缓冲二进制方式读取，返回 `bytes`。
2. **HTTP/HTTPS**：以 `("http://", "https://")` 开头时，`import requests` 后调用 `requests.get(blobpath)`、`resp.raise_for_status()`，返回 `resp.content`。
3. **其余路径（云存储）**：尝试 `import blobfile`（`blobfile` 是用于云存储的类文件对象库），未安装时抛出 `ImportError`，错误消息提示 `pip install blobfile`；安装成功则返回 `blobfile.read_bytes(blobpath)`。

三个分支共享统一返回类型 `bytes`，为上层解析函数提供一致的输入。注意 `blobfile` 是**惰性**导入的——`import tiktoken` 并不会触发其加载（facts-rust F-066 断言 `"blobfile" not in sys.modules`），只有当真正走云存储分支时才导入，这是保持门面层启动轻量的刻意设计。

## 校验：check_hash 与 SHA256

`check_hash(data: bytes, expected_hash: str) -> bool`（facts-python F-057）是加载安全的守门员：它计算 `hashlib.sha256(data).hexdigest()`，与传入的 `expected_hash` 比较，返回布尔值。注意这里的摘要算法是 **SHA-256**，用于校验"读取到的字节内容是否正确"；而缓存**键**用的则是 SHA-1（见下文），两者目的不同，不可混淆。

## 缓存：read_file_cached

`read_file_cached(blobpath: str, expected_hash: str | None = None) -> bytes`（facts-python F-058~F-061）在 `read_file` 之上叠加了磁盘缓存，是加载流程的主入口。其行为可拆为四步：

### 缓存目录解析

缓存目录的解析优先级为（facts-python F-058）：

1. 环境变量 `TIKTOKEN_CACHE_DIR`；
2. 环境变量 `DATA_GYM_CACHE_DIR`；
3. 默认值 `tempfile.gettempdir()/data-gym-cache`（系统临时目录下的 `data-gym-cache` 子目录）。

若最终解析出的 `cache_dir == ""`（空字符串），则**禁用缓存**，直接调用 `read_file` 返回（facts-python F-058）。

### 缓存键与命中判定

缓存键由路径本身的 SHA-1 摘要生成：`hashlib.sha1(blobpath.encode()).hexdigest()`，缓存文件路径为 `os.path.join(cache_dir, cache_key)`（facts-python F-059）。即同一 URL/路径对应同一缓存文件，不区分词表内容。

命中判定规则（facts-python F-059）：
- 若缓存文件存在，且 `expected_hash is None` **或** `check_hash(data, expected_hash)` 通过，则直接返回缓存字节；
- 若哈希校验不通过（内容被污染/损坏），则 `os.remove(cache_path)` 删除损坏缓存（删除导致的 `OSError` 会被忽略），落到重新读取分支。

### 重新读取与最终校验

缓存未命中或哈希失配时重新调用 `read_file`。若 `expected_hash` 非空且 `check_hash` 失败，则抛出 `ValueError`（消息形如 `"Hash mismatch..."`），表明远程词表内容与预期的 SHA-256 不符（facts-python F-060）。

### 原子写入

写入缓存使用"临时文件 + rename"的原子写模式（facts-python F-061）：
1. `os.makedirs(cache_dir, exist_ok=True)` 确保目录存在；
2. 写临时文件 `cache_path + "." + str(uuid.uuid4()) + ".tmp"`，其中临时名以 UUID 保证唯一；
3. `os.rename` 将临时文件原子改名为 `cache_path`。

这样在并发或多个进程写入同一缓存键时，不会出现读到"写了一半的文件"的情况。写缓存过程中若抛出 `OSError`，仅当 `user_specified_cache` 为 `True` 时才重新抛出，否则静默容忍——因为缓存是优化而非必需，缓存写失败不应阻断加载主流程。"能不能写"取决于用户是否显式指定了 `TIKTOKEN_CACHE_DIR`/`DATA_GYM_CACHE_DIR`。

## 解析：两种词表格式

根据词表文件来源，`load.py` 提供两条对称但用途不同格式的解析路径。

### data-gym 格式：data_gym_to_mergeable_bpe_ranks

`data_gym_to_mergeable_bpe_ranks(vocab_bpe_file, encoder_json_file, vocab_bpe_hash=None, encoder_json_hash=None, clobber_one_byte_tokens=False) -> dict[bytes, int]`（facts-python F-062~F-066）面向 OpenAI 早期（GPT-2/Codex）的 `data-gym` 双文件格式——一份 `vocab.bpe`（merge 规则表）加一份 `encoder.json`。其流程：

1. **字节映射**：构造 `rank_to_intbyte`（0-255 中可打印且非空格的单字节）与 `data_gym_byte_to_byte`（facts-python F-063）；由于普通单字节只有约 95 个可打印字符，不足 256 个槽位，故为不可打印字节补充偏移 `chr(2**8 + n)`；最后断言 `len(rank_to_intbyte) == 2**8`（2620 个槽位须凑满 256 字节）。
2. **读 merge 表**：以 `read_file_cached(vocab_bpe_file, vocab_bpe_hash).decode()` 读取，按行第二个元素起解析 `bpe_merges`（facts-python F-064）。
3. **建单字节 token**：先建 `{bytes([b]): i}` 覆盖 256 个单字节，再按 merge 顺序追加合并 token `bpe_ranks[decode(first)+decode(second)] = n`（facts-python F-065）。
4. **与 encoder.json 对齐**：读取 `encoder.json`，弹出 `<|endoftext|>` 与 `<|startoftext|>`；当 `clobber_one_byte_tokens=True` 时用 encoder.json 覆盖单字节 rank；最后 `assert bpe_ranks == encoder_json_loaded` 强制 merge 表与 encoder 完全一致（facts-python F-066）。

可见 data-gym 格式是"从 merge 规则重建 + 与 encoder 交叉核对"的双源校验。

### tiktoken 格式：load_tiktoken_bpe 与 dump_tiktoken_bpe

`load_tiktoken_bpe(tiktoken_bpe_file: str, expected_hash: str | None = None) -> dict[bytes, int]`（facts-python F-068）面向现代的 `.tiktoken` 单文件格式（`cl100k_base`/`o200k_base` 等即用此格式，见 /concepts/07-openai-vocabularies.md）。该格式每行形如 `<base64> <rank>`：`<base64>` 是 token 字节的 base64 编码，`<rank>` 是十进制整数。解析时逐行 `line.split()`，以 `ret[base64.b64decode(token)] = int(rank)` 填充返回字典；某行解析异常时抛出 `ValueError`（错误消息含该行内容与文件名）。

对称地，`dump_tiktoken_bpe(bpe_ranks: dict[bytes, int], tiktoken_bpe_file: str) -> None`（facts-python F-067）执行反向序列化：`import blobfile`（未安装抛 `ImportError`），用 `blobfile.BlobFile(tiktoken_bpe_file, "wb")` 按 rank 排序写入 `base64.b64encode(token) + b" " + str(rank).encode() + b"\n"`。这为把 `data_gym_to_mergeable_bpe_ranks` 得到的 mergeable 词表转换为 `.tiktoken` 格式提供了双向工具（`openai_public.py` 的 `gpt2()` 正是先走 data-gym 再 dump，见 F-086/F-067）。

## 与上层如何衔接

- `read_file_cached` 是统一的"读 + 缓存 + 校验"入口，被两种格式解析器复用（F-064、F-068）。
- `openai_public.py` 的早期编码（`gpt2`）走 `data_gym_to_mergeable_bpe_ranks`，而 `r50k_base`/`p50k_base`/`cl100k_base`/`o200k_base` 均直接 `load_tiktoken_bpe(".../encodings/<name>.tiktoken", expected_hash=...)`（facts-python F-086~F-091），对比见 /concepts/07-openai-vocabularies.md。
- 每个编码的 `expected_hash` 是写死在构造 dict 里的 SHA-256，配合 `check_hash`（F-057）/`read_file_cached`（F-060）保证词表内容可复现、可防篡改。

> 异步说明：`load.py` 不存在任何 `load_async` 函数，本文件中不包含协程/异步 I/O 逻辑（facts-python F-069），全部为同步实现。

## 相关概念

- [/concepts/07-openai-vocabularies.md](/concepts/07-openai-vocabularies.md)：具体公开编码（`gpt2`/`r50k_base`/`cl100k_base`/`o200k_base` 等）如何调用本文件解析词表。
- [/concepts/05-registry-model.md](/concepts/05-registry-model.md)：`get_encoding` 触发构造函数、进而触发本文件加载的上游流程。
- [/concepts/02-encoding-api.md](/concepts/02-encoding-api.md)：加载产物 `mergeable_ranks`/`special_tokens` 如何进入 `Encoding` 对象。