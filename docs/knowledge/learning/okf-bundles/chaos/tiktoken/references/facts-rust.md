---
type: Facts
title: tiktoken Rust 核心事实清单
description: 从 tiktoken v0.14.0 源码采集的 Rust 核心实现事实，每条标注文件路径
tags: [tiktoken, bpe, tokenizer, facts, rust, reference]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-25T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-25T00:00:00Z }
status: verified
stale_after: 2027-08-25
source_id: tiktoken-rust
---

# 采集范围

本文件是 tiktoken v0.14.0 的 Rust 源码事实清单，属于 R 阶段（事实采集）产出。采集对象：

- `src/lib.rs`：核心 BPE 分词逻辑（结构体、函数、错误类型、性能注释、单元测试），共 702 行，已逐行精读
- `src/py.rs`：PyO3 绑定（`CoreBPE` 的 `#[pymethods]`、`TiktokenBuffer`、`#[pymodule]`），共 255 行，已逐行精读
- `Cargo.toml`：包元数据与依赖
- 辅助事实：`tests/test_*.py`、`scripts/*.py`（作为行为约束与工具类事实）

采集原则：每条事实只记录"代码里有什么"，不含"用于/目的是/设计为"等推断词。标注文件相对路径与行号/函数名/类型名。

> 提示：父任务示例中提及的 `insert_sorted`、`core_bpe` 两个符号在本仓库 v0.14.0 源码中**不存在**（见 F-034）；Python 侧 Rust 模块名为 `_tiktoken` 而非 `_core`（见 F-035）。下文均以实际源码为准。

## 1. lib.rs — BPE 核心分词逻辑

### 1.1 类型别名与内部数据结构

- F-001: `pub type Rank = u32;` 定义在 `src/lib.rs:13`。`Rank` 是 BPE rank（token 索引）的公开类型别名。
- F-002: 顶层导入包括 `std::collections::HashSet`（L1）、`std::num::NonZeroU64`（L2）、`std::thread`（L3）、`fancy_regex::Regex`（L5）、`rustc_hash::FxHashMap as HashMap`（L8）、`std::collections::BinaryHeap`（L15）。`pyo3` 仅在 `#[cfg(feature = "python")]` 下导入（L6-7）。
- F-003: `#[cfg(feature = "python")] mod py;` 在 `src/lib.rs:10-11`，即 `py.rs` 仅在启用 `python` feature 时编译。`CoreBPE` 的结构体声明上有 `#[cfg_attr(feature = "python", pyclass(frozen))]`（`src/lib.rs:318`）。
- F-004: `struct Merge { start: usize, rank: Rank }` 定义于 `src/lib.rs:17-21`，派生 `Eq/PartialEq/Clone/Copy`。
- F-005: `Merge` 的 `Ord::cmp` 实现于 `src/lib.rs:23-31`：先按 `other.rank.cmp(&self.rank)`，再按 `other.start.cmp(&self.start)`。`PartialOrd` 委托给 `cmp`（L33-37）。结合 `BinaryHeap`（最大堆）使用，实现依据 rank 从小到大、平局按 start 从小到大的弹出顺序。
- F-006: `struct State { prev: usize, end: usize, next_end: usize, next_rank: Rank, cur_rank: Rank }` 定义于 `src/lib.rs:39-45`，用于大输入的分词状态。

### 1.2 BPE 合并算法

- F-007: 函数 `fn _byte_pair_merge_large(ranks: &HashMap<Vec<u8>, Rank>, piece: &[u8]) -> Vec<Rank>` 定义于 `src/lib.rs:47-138`。返回值为 `Vec<Rank>`。该函数使用 `Vec<State>` 与 `BinaryHeap<Merge>`，循环内闭包 `potential_merge` 定义于 L79-95。
- F-008: 在 `_byte_pair_merge_large` 中，初始状态压入 `state`，通过 `while let Some(left) = heap.pop()` 循环（L97-125）；当 `left.rank == Rank::MAX` 时 `break`（L98-100）；当 `left.rank != state[left.start].next_rank` 时 `continue`（即该 merge 已失效，L101-103）。合并并更新相邻 merge 后，将 `state[right_start].next_rank = Rank::MAX` 使起始于 `right_start` 的旧 merge 失效（L124）。
- F-009: 函数 `fn _byte_pair_merge(ranks: &HashMap<Vec<u8>, Rank>, piece: &[u8]) -> Vec<(usize, Rank)>` 定义于 `src/lib.rs:140-196`。注释 L145-147 说明按字节切片（`piece[i..i+2]`）而非 token pair 索引 `ranks`。该方法为简单实现，注释 L174-177 记为 O(mn) work，`n` 通常很小。
- F-010: `_byte_pair_merge` 的循环逻辑（L178-194）：`while min_rank.0 != Rank::MAX` 时取 `i = min_rank.1`，先更新 `parts[i-1]` 与 `parts[i]` 的 rank（L182-185），再 `parts.remove(i + 1)`（L186），随后重扫 `parts[..parts.len()-1]` 找新的 `min_rank`（L188-193）。闭包 `get_rank` 定义于 L159-172。
- F-011: `pub fn byte_pair_encode(piece: &[u8], ranks: &HashMap<Vec<u8>, Rank>) -> Vec<Rank>` 定义于 `src/lib.rs:198-211`。分派逻辑：`piece_len == 1` 时返回 `vec![ranks[piece]]`（L201-203）；`piece_len < 100` 时调用 `_byte_pair_merge` 并用 `.windows(2)` 映射为 `ranks[&piece[..]]`（L204-208）；否则调用 `_byte_pair_merge_large`（L210）。
- F-012: `pub fn byte_pair_split<'a>(piece: &'a [u8], ranks: &HashMap<Vec<u8>, Rank>) -> Vec<&'a [u8]>` 定义于 `src/lib.rs:213-219`，首行 `assert!(piece.len() > 1)`，使用 `_byte_pair_merge(...).windows(2)` 把 `piece` 切分为字节切片。

### 1.3 性能注释（源码内嵌）

- F-013: `src/lib.rs:221-260` 存在注释块「Various performance notes」，含四类注释：`Regex`（L222-238，提到 `fancy_regex` 与 `regex.find_at` 的线程竞争问题）、`Threading`（L240-243，提到试用 rayon 未比 Python 线程 + 释放 GIL 更快）、`Caching`（L245-254，说明去掉 lru cache，把 token 集当作 cache）、`Hashing`（L256-260，说明使用 FxHashMap）。

### 1.4 线程哈希

- F-014: `struct FakeThreadId(NonZeroU64);` 定义于 `src/lib.rs:262`。
- F-015: `fn hash_current_thread() -> usize` 定义于 `src/lib.rs:264-275`，通过 `std::mem::transmute::<std::thread::ThreadId, FakeThreadId>(thread::current().id()).0` 取线程 ID（`unsafe`，L271-274），返回 `u64::from(x) as usize`。注释 L266-268 提到 Rust 内部线程 id 计数器是私有的，故用 transmute。

### 1.5 错误类型

- F-016: `pub struct DecodeKeyError { pub token: Rank }` 定义于 `src/lib.rs:277-280`，派生 `Debug/Clone`。
- F-017: `DecodeKeyError` 的 `Display` 实现（L282-286）输出 `"Invalid token for decoding: {}"` + token；并实现 `std::error::Error`（L288）。
- F-018: `pub struct DecodeError { pub message: String }` 定义于 `src/lib.rs:290-293`，`Display`（L295-299）输出 `"Could not decode tokens: {}"` + message，实现 `Error`（L301）。
- F-019: `pub struct EncodeError { pub message: String }` 定义于 `src/lib.rs:303-306`，`Display`（L308-312）输出 `"Could not encode string: {}"` + message，实现 `Error`（L314）。

### 1.6 CoreBPE 结构体与字段

- F-020: `pub struct CoreBPE` 定义于 `src/lib.rs:318-328`，`#[cfg_attr(feature = "python", pyclass(frozen))]` 且 `#[derive(Clone)]`。共 7 个字段：
  - `encoder: HashMap<Vec<u8>, Rank>`
  - `special_tokens_encoder: HashMap<String, Rank>`
  - `decoder: HashMap<Rank, Vec<u8>>`
  - `special_tokens_decoder: HashMap<Rank, Vec<u8>>`
  - `regex_tls: Vec<Regex>`
  - `special_regex_tls: Vec<Regex>`
  - `sorted_token_bytes: Vec<Vec<u8>>`

### 1.7 CoreBPE 方法

- F-021: `fn _get_tl_regex(&self) -> &Regex`（`src/lib.rs:331-336`）返回 `&self.regex_tls[hash_current_thread() % MAX_NUM_THREADS]`。
- F-022: `fn _get_tl_special_regex(&self) -> &Regex`（`src/lib.rs:338-340`）返回 `&self.special_regex_tls[hash_current_thread() % MAX_NUM_THREADS]`。
- F-023: `fn decode_bytes(&self, tokens: &[Rank]) -> Result<Vec<u8>, DecodeKeyError>`（`src/lib.rs:345-358`）。对每个 token 先查 `self.decoder`，缺失则查 `self.special_tokens_decoder`，均缺失返回 `Err(DecodeKeyError { token })`；命中则 `ret.extend(token_bytes)`。注释 L343-344 说明返回字节不保证是合法 UTF-8。
- F-024: `pub fn encode_ordinary(&self, text: &str) -> Vec<Rank>`（`src/lib.rs:360-373`）。用 `regex.find_iter(text)` 遍历，对每个 `mat`，若 `self.encoder.get(piece)` 命中则直接 push token，否则 `ret.extend(&byte_pair_encode(piece, &self.encoder))`。
- F-025: `pub fn encode(&self, text: &str, allowed_special: &HashSet<&str>) -> Result<(Vec<Rank>, usize), EncodeError>`（`src/lib.rs:375-442`）。返回元组，第二元素 `last_piece_token_len`。逻辑含：外层循环用 `special_regex.find_from_pos` 找允许的 special token（L391-401），对普通片段用 `regex.find_iter` 分词（L405-424），命中 special 时 `self.special_tokens_encoder[piece]` push token（L426-434）。正则错误映射为 `EncodeError { message: "Regex error while tokenizing: {e}" }`（L408-412）。
- F-026: `fn _increase_last_piece_token_len(&self, tokens: Vec<Rank>, mut last_piece_token_len: usize) -> (Vec<Rank>, usize)`（`src/lib.rs:444-481`）。内部闭包 `token_is_all_space` 用 `self.decoder` 逆序检查 token 字节是否全部为 `[b' ', b'\n', b'\t']`（L457-467）；当 `last_piece_token_len > 0` 且该 token 全为空字符时，向前扩展计数（L468-476）。末尾 `debug_assert!(last_piece_token_len <= tokens.len())`（L478）。
- F-027: `pub fn _encode_unstable_native(&self, text: &str, allowed_special: &HashSet<&str>) -> (Vec<Rank>, HashSet<Vec<Rank>>)`（`src/lib.rs:483-599`）。调用 `self.encode(...).unwrap()`；`last_piece_token_len == 0` 时返回 `(tokens, HashSet::new())`（L489-493）；用 `self.sorted_token_bytes.partition_point` 找前/后缀起点（L514-516、L532-534），对每个可能 token 做黑白穷举尝试（L529-571），另含对 UTF-8 尾字符为空白的快速修复分支（L581-596）。
- F-028: `pub fn new<E, SE, NSE>(encoder: E, special_tokens_encoder: SE, pattern: &str) -> Result<Self, Box<dyn std::error::Error + Send + Sync>>`（`src/lib.rs:601-616`），其中 `E: IntoIterator<Item=(Vec<u8>, Rank)>`、`SE: IntoIterator<Item=(String, Rank)>`、`NSE: IntoIterator<Item=(String, (Rank, Rank))>`。委托给 `Self::new_internal(HashMap::from_iter(...), ...)`。
- F-029: `fn new_internal(encoder: HashMap<Vec<u8>, Rank>, special_tokens_encoder: HashMap<String, Rank>, pattern: &str) -> Result<Self, ...>`（`src/lib.rs:618-663`）。行为：`Regex::new(pattern)` 构建普通正则（L623）；`special_tokens_encoder.keys()` 逐个 `fancy_regex::escape` 后用 `"|"` join 构建 `special_regex`（L625-631）；`decoder` 由 `encoder` 映射 `(*v, k.clone())` 而来（L633-634）；`assert!(encoder.len() == decoder.len(), ...)` 校验无重复 token 索引（L636-641）；`special_tokens_decoder` 由 `special_tokens_encoder` 映射 `(*v, k.as_bytes().to_vec())`（L643-646）；`sorted_token_bytes` 为 `encoder.keys().cloned().collect()` 后 `sort()`（L649-650）；最后构造 `Self`，`regex_tls` 与 `special_regex_tls` 各 `(0..MAX_NUM_THREADS)` 克隆一份（L657-660）。
- F-030: `pub fn special_tokens(&self) -> HashSet<&str>`（`src/lib.rs:665-670`）返回 `special_tokens_encoder` 的所有 key。
- F-031: `pub fn encode_with_special_tokens(&self, text: &str) -> Vec<Rank>`（`src/lib.rs:672-675`）取 `self.special_tokens()` 作为 `allowed_special` 调用 `self.encode(...).unwrap().0`。
- F-032: `const MAX_NUM_THREADS: usize = 128;` 定义于 `src/lib.rs:316`，用于线程局部正则数组的取模。

### 1.8 lib.rs 单元测试

- F-033: `#[cfg(test)] mod tests` 于 `src/lib.rs:678-702`。`setup_ranks()` 构造 `HashMap::from_iter([(b"ab".to_vec(), 0), (b"cd".to_vec(), 1)])`（L685-687）；`test_simple_characters` 断言 `byte_pair_split(b"abcd", &ranks)` 为 `vec![b"ab", b"cd"]`（L689-694）；`test_repeated_characters` 断言 `byte_pair_split(b"abab", ...)` 为 `vec![b"ab", b"ab"]`（L696-701）。

### 1.9 源码中不存在的符号（防误导）

- F-034: 在 `src/lib.rs` 与 `src/py.rs` 全文中不存在 `insert_sorted` 与 `core_bpe` 两个标识符（已全文件精读核实）。Rust 侧分词入口函数实际命名为 `byte_pair_encode`、`byte_pair_split`（`src/lib.rs:198、213`）。

## 2. py.rs — PyO3 绑定

### 2.1 模块导入与全局

- F-035: `#[pymodule(gil_used = false)] fn _tiktoken(_py: Python, m: &Bound<PyModule>) -> PyResult<()>` 定义于 `src/py.rs:251-255`，函数体为 `m.add_class::<CoreBPE>()?; Ok(())`。即 Python 扩展模块名为 `_tiktoken`，且（经 `tiktoken/core.py:7` 的 `from tiktoken import _tiktoken` 核实）Python 侧以 `tiktoken._tiktoken` 导入，**本仓库不存在 `tiktoken._core` 模块**。
- F-036: py.rs 顶部 `use crate::{CoreBPE, Rank, byte_pair_encode};`（`src/py.rs:11`），并导入 `pyo3::{IntoPyObjectExt, PyResult, exceptions, prelude::*, pybacked::PyBackedStr, types::{PyBytes, PyList}}`（L3-8）、`std::collections::HashSet`（L1）、`rustc_hash::FxHashMap as HashMap`（L9）。

### 2.2 CoreBPE 的 Python 方法（#[pymethods]）

- F-037: `#[pymethods] impl CoreBPE` 块为 `src/py.rs:13-184`。构造方法 `#[new] fn py_new(encoder: HashMap<Vec<u8>, Rank>, special_tokens_encoder: HashMap<String, Rank>, pattern: &str) -> PyResult<Self>`（L15-23），调用 `Self::new_internal(...)`，错误经 `.map_err` 转为 `PyValueError`。
- F-038: `#[pyo3(name = "encode_ordinary")] fn py_encode_ordinary(&self, py: Python, text: &str) -> Vec<Rank>`（`src/py.rs:29-32`），函数体 `py.detach(|| self.encode_ordinary(text))`，Python 名 `encode_ordinary`。
- F-039: `#[pyo3(name = "encode")] fn py_encode(&self, py: Python, text: &str, allowed_special: HashSet<PyBackedStr>) -> PyResult<Vec<Rank>>`（`src/py.rs:34-49`）。用 `py.detach` 释放 GIL 后调用 `self.encode(...)`，错误映射为 `PyValueError(e.message)`；Python 名 `encode`。
- F-040: `fn encode_to_tiktoken_buffer(&self, py: Python, text: &str, allowed_special: HashSet<PyBackedStr>) -> PyResult<Py<PyAny>>`（`src/py.rs:51-70`），无显式 `#[pyo3(name)]`（Python 名即 `encode_to_tiktoken_buffer`）。内部构建 `TiktokenBuffer { tokens }` 并 `buffer.into_py_any(py)`。
- F-041: `fn _encode_bytes(&self, py: Python, bytes: &[u8]) -> Vec<Rank>`（`src/py.rs:72-115`）。用 `std::str::from_utf8` 判断：合法 UTF-8 则 `self.encode_ordinary`；否则用 `from_utf8_unchecked(&bytes[..e.valid_up_to()])` 走 `self.encode(..., &HashSet::new())` + `_increase_last_piece_token_len`，最后对 `unstable_bytes` 走 `self.encoder.get` 或 `byte_pair_encode`（L103-110）。
- F-042: `#[pyo3(name = "encode_with_unstable")] fn py_encode_with_unstable(&self, py: Python, text: &str, allowed_special: HashSet<PyBackedStr>) -> PyResult<(Vec<Rank>, Py<PyList>)>`（`src/py.rs:117-131`），`py.detach` 内调用 `self._encode_unstable_native`，completions 转为 `PyList`；Python 名 `encode_with_unstable`。
- F-043: `fn encode_single_token(&self, piece: &[u8]) -> PyResult<Rank>`（`src/py.rs:133-143`），先查 `self.encoder`，再查 `self.special_tokens_encoder`（需 UTF-8 可转），全缺则返回 `PyKeyError`。
- F-044: `fn encode_single_piece(&self, piece: &[u8]) -> Vec<Rank>`（`src/py.rs:145-150`），命中 encoder 返回 `vec![*token]`，否则 `byte_pair_encode(piece, &self.encoder)`。
- F-045: `#[pyo3(name = "decode_bytes")] fn py_decode_bytes(&self, py: Python, tokens: Vec<Rank>) -> Result<Py<PyBytes>, PyErr>`（`src/py.rs:156-162`），`py.detach` 内 `self.decode_bytes`，成功转 `PyBytes`，失败转 `PyKeyError`；Python 名 `decode_bytes`。
- F-046: `fn decode_single_token_bytes(&self, py: Python, token: Rank) -> PyResult<Py<PyBytes>>`（`src/py.rs:164-172`），先查 `self.decoder` 再查 `self.special_tokens_decoder`，全缺返回 `PyKeyError(token.to_string())`。
- F-047: `fn token_byte_values(&self, py: Python) -> Vec<Py<PyBytes>>`（`src/py.rs:178-183`），遍历 `self.sorted_token_bytes` 逐个转 `PyBytes`（Python 名 `token_byte_values`；对应 `tests/test_simple_public.py` 与 `tiktoken/core.py:358` 的 `token_byte_values` 断言循环用例）。

### 2.3 TiktokenBuffer（buffer protocol）

- F-048: `#[pyclass(frozen)] struct TiktokenBuffer { tokens: Vec<Rank> }` 定义于 `src/py.rs:186-189`。
- F-049: `unsafe fn __getbuffer__(slf: Bound<'_, Self>, view: *mut pyo3::ffi::Py_buffer, flags: c_int) -> PyResult<()>` 于 `src/py.rs:194-238`。行为：view 为空返回 `PyBufferError`（L199-201）；`flags & PyBUF_WRITABLE` 时返回 `PyBufferError("Object is not writable")`（L202-206）；否则填充 `view_ref.buf/len/readonly/itemsize/format/ndim/shape/strides/suboffsets/internal`（L209-234）。`format` 为 `"I"` 的 `CString`（L216-221），`ndim = 1`，`readonly = 1`。
- F-050: `unsafe fn __releasebuffer__(&self, view: *mut pyo3::ffi::Py_buffer)` 于 `src/py.rs:240-248`，若 `view_ref.format` 非空则 drop 对应 `CString`。开始处注释引用 PyO3 v0.22.2 的 buffer 协议测试（L193）。

### 2.4 Rust 导出接口速查（Python 侧名称）

- F-051: 通过 `#[pyclass]` 导出的 Python 类：`CoreBPE`（`src/lib.rs:318`，`src/py.rs:253`）；另有内部 `#[pyclass(frozen)]` 类 `TiktokenBuffer`（`src/py.rs:186`）。
- F-052: 通过 `#[pymethods]` 导出的 `CoreBPE` 方法（Python 名称 → 源行）：`__init__`(py_new, L15)、`encode_ordinary`(L29)、`encode`(L34)、`encode_to_tiktoken_buffer`(L51)、`_encode_bytes`(L72)、`encode_with_unstable`(L117)、`encode_single_token`(L133)、`encode_single_piece`(L145)、`decode_bytes`(L156)、`decode_single_token_bytes`(L164)、`token_byte_values`(L178)。

## 3. Cargo.toml — 包与依赖

- F-053: `[package] name = "tiktoken"`、`version = "0.14.0"`、`edition = "2024"`（`Cargo.toml:1-4`）。
- F-054: `[lib] name = "tiktoken"`，`crate-type = ["cdylib", "rlib"]`（`Cargo.toml:6-8`），即编译为动态库（Python 扩展）+ Rust 库两种类型。
- F-055: `[features] default = []`，`python = ["pyo3"]`（`Cargo.toml:10-14`）。
- F-056: 依赖（`Cargo.toml:16-26`）：`pyo3 = 0.29.2`（可选，features 含 `extension-module`、`macros`）、`fancy-regex = 0.19.0`、`regex = 1.13.1`、`rustc-hash = 2`、`bstr = 1.13.1`。

## 4. 辅助事实（tests / scripts）

### 4.1 测试行为约束

- F-057: `tests/test_encoding.py:16-18`：`get_encoding("gpt2")` 下 `encode("hello world") == [31373, 995]`，`encode("hello <|endoftext|>", allowed_special="all") == [31373, 220, 50256]`。
- F-058: `tests/test_encoding.py:86-99`：`enc._encode_bytes(b" \xec\x8b\xa4\xed") == [62085]`；对 `b"\x80" * i`（i in 0..10）满足 `decode_bytes(_encode_bytes(bytestring)) == bytestring`。属性测试 `test_hyp_encode_bytes` 对任意字节串断言同一性质。
- F-059: `tests/test_encoding.py:102-110`：`encode("👍") == [9468, 239, 235]`，surrogate pair `"\ud83d\udc4d"` 被转换为 `👍` 的 codepoint，lone surrogate `"\ud83d"` 编码等于 `encode("")`。
- F-060: `tests/test_encoding.py:25-28`（`test_simple`）与 `test_single_token_roundtrip`（L159-167）：对 `range(enc.max_token_value - 1)` / `range(enc.n_vocab)` 内的 token，`encode_single_token(decode_single_token_bytes(token)) == token`（`decode_single_token_bytes` 抛 `KeyError` 的 token 跳过）。
- F-061: `tests/test_encoding.py:175-224`：`encode(text)` 在默认 `disallowed_special="all"` 语义下遇到未允许的 special token 抛 `ValueError`；`disallowed_special=()` 时 special token 不进入结果；`allowed_special="all", disallowed_special=()` 时 special token 进入结果。
- F-062: `tests/test_offsets.py:49-79`：`decode_with_offsets` 的偏移断言，如 `"hello world"` 偏移 `[0, 5]`；含 special token 文本偏移 `[0, 5, 11, 24, 30]`；中文与泰米尔文、`" Ġ除"`（含 `\xa0\xe9...` 多字节字符）等用例。偏移值以字节位置计。
- F-063: `tests/test_offsets.py:19-25`：`_token_offsets_reference` 用 `decode(tokens[:i], errors="ignore")` 的公共前缀长度构造参考偏移。
- F-064: `tests/test_pickle.py:4-23`：`Encoding` 对象（含内置与自定义）可 pickle 往返，往返后 `encode` 结果一致；自定义 `special_tokens={"<|pickle|>": 100_000}` 往返后 `encode("<|pickle|>", allowed_special="all") == [100_000]`。
- F-065: `tests/test_misc.py:7-21`：`encoding_for_model` 的模型→编码名映射，如 `gpt2→gpt2`、`text-davinci-003→p50k_base`、`text-davinci-edit-001→p50k_edit`、`gpt-3.5-turbo-0301→cl100k_base`、`gpt-4→cl100k_base`、`gpt-4o→o200k_base`、`gpt-oss-120b→o200k_harmony`。
- F-066: `tests/test_misc.py:24-31` 与 `tests/test_simple_public.py:36-42`：`import tiktoken` 不触发加载 `blobfile`（`assert "blobfile" not in sys.modules`）。
- F-067: `tests/test_encoding.py:240-252`：`encode_batch` 与 `encode_ordinary_batch` 的批编码等价于逐条 `encode` / `encode_ordinary`；`decode_batch(encoded) == batch`（L258-264 属性测试）。
- F-068: `tests/test_encoding.py:132-146`：对 `"hello"`、`"  "`、中文 `"请考试我的软件！12345"` 等，`decode(encode(x)) == x` 且 `decode(encode_ordinary(x)) == x`（roundtrip 约束）。

### 4.2 scripts 工具类事实

- F-069: `scripts/redact.py`：`redact_file`（L7-39）按文件首行是否含 `"redact"` 决定删除（L15-20），否则按 `"# ===== redact-beg ====="` / `"# ===== redact-end ====="` / `"<!--- redact-beg -->"` / `"<!--- redact-end -->"` 四类标记做 `re.split(pattern, text)[::2]` 取未标记片段改写文件（L22-37）。`redact` 函数（L42-54）基于 `tiktoken_root = Path(__file__).parent.parent` 且断言目录名为 `tiktoken` 并含 `pyproject.toml`，用 `git ls-files`（失败回退 `glob("**/*")`）枚举文件。`--dry-run` 默认 `True`（L59）。
- F-070: `scripts/benchmark.py`：`benchmark_batch`（L15-37）从环境变量 `RAYON_NUM_THREADS` 取线程数（L16），统计 `num_bytes`（L17），用 `tiktoken.get_encoding("gpt2")` 预热后调用 `enc.encode_ordinary_batch(documents, num_threads=num_threads)`（L20-25），再与 HuggingFace `GPT2TokenizerFast` 对比吞吐（L28-37）。
- F-071: `scripts/wheel_download.py`：`download_artifacts`（L8-41）用 GitHub Actions Artifacts REST API（`/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts`）列出并下载 artifact，先写临时 zip 再 `zipfile` 解压到 `output_dir`，最后删除临时 zip。`main`（L44-57）定义 `--token`、`--owner`、`--repo`、`--run-id`、`--output-dir`（默认 `artifacts`）等必需/可选参数。

## 相关概念

- 本文件是 R 阶段事实基座，供 tiktoken Bundle 的 `concepts/` 与 `references/` 其他文档引用。
- 关键交叉点：`CoreBPE`（F-020）↔ `tiktoken/core.py` 中的 Python `Encoding` 封装；BPE 算法入口 `byte_pair_encode`（F-011）↔ 大/小输入分派（F-007、F-009）。