# tiktoken 源码学习 OKF Wiki 教程生成 - 实施计划

> **执行原则**：本 bundle 规模适中（Python 门面 + Rust 核心），按 R→I→E→V→C 五阶段闭环。E 阶段信源先行、分批生成（每批 ≤7）、index 最后写。所有实现任务通过子代理委派执行。

---

## [x] Task 0: deep-research 辅助研究（BPE 背景知识）

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 使用 deep-research 研究 tiktoken/BPE 分词器外部背景：BPE 算法原理、OpenAI 公开 encoding（o200k_base/cl100k_base/p50k_base/r50k_base）演进与适用模型、token 计数实践
  - 产出：背景笔记（供 I 阶段洞察与文档背景叙述参考），标注外部来源
- **Notes**: 外部背景仅辅助理解，**不写入** facts-*.md；源码事实以 R 阶段 Grep 验证为准

## [x] Task 1: R 阶段事实采集（Python 门面层）

- **Priority**: high
- **Depends On**: None（可与 Task 2 并行）
- **Description**:
  - 精读 `tiktoken/__init__.py`、`core.py`、`registry.py`、`model.py`、`load.py`、`_educational.py`、`tiktoken_ext/openai_public.py`
  - 提取编号事实 F-xxx：公开 API（`get_encoding`/`list_encoding_names`/`encoding_for_model`/`encoding_name_for_model`）、`Encoding` 类全部方法（encode/decode/decode_with_offsets/encode_with_unstable/encode_ordinary/get_rank/encode_single_token/decode_single_token_bytes/string_ordinal 等）、注册表与模型映射、BPE 文件加载（`load_tiktoken_bpe`、`read_file` 等）、`SimpleBytePairEncoding` 教学实现、4 个公开 encoding 定义
  - 事实写入 `bundles/chaos/tiktoken/references/facts-python.md`
- **Acceptance Criteria Addressed**: R 事实零推测（AC-6）、模块全覆盖（AC-9）
- **Test Requirements**:
  - `programmatic` TR-1.1: facts-python.md 存在，每条事实含源码文件路径
  - `human-judgement` TR-1.2: 无"用于/目的是/设计为"推断词；`Encoding` 方法签名与 core.py 一致

## [x] Task 2: R 阶段事实采集（Rust 核心 + 测试/脚本）

- **Priority**: high
- **Depends On**: None（可与 Task 1 并行）
- **Description**:
  - 精读 `src/lib.rs`、`src/py.rs`（Rust 核心实现与 PyO3 绑定）
  - 浏览 `tests/test_*.py` 与 `scripts/*.py` 提取辅助事实（测试用法、benchmark/redact/wheel_download 工具）
  - 提取事实：Rust 分词器核心逻辑、PyO3 导出的 Python 接口、`_core` 模块对应关系
  - 事实写入 `bundles/chaos/tiktoken/references/facts-rust.md`
- **Acceptance Criteria Addressed**: R 事实零推测（AC-6）、模块全覆盖（AC-9）
- **Test Requirements**:
  - `programmatic` TR-2.1: facts-rust.md 存在，覆盖 lib.rs 与 py.rs
  - `human-judgement` TR-2.2: Rust→Python 绑定接口与 py.rs 导出一致

## [x] Task 3: I 阶段架构洞察 + 知识地图

- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 基于 facts-python.md + facts-rust.md 提炼 3-5 个核心架构洞察（陈述+证据 F-xxx + 反常识 + 行动四元组），可选洞察：Python 门面 + Rust 高性能核心双层架构、Encoding 对象封装 BPE 状态、公开 API 的注册表/模型双入口、4 种 encoding 词汇体系演进、教学模块。
  - 设计概念文档知识地图（分入门/核心/进阶，学习路径递进），确定每篇覆盖的 F-xxx 事实
  - 洞察写入 `bundles/chaos/tiktoken/references/insights.md`
- **Acceptance Criteria Addressed**: 洞察四元组（AC-7）、学习路径（AC-4/NFR-4）
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每条洞察含陈述/证据(F-xxx)/反常识/行动

## [x] Task 4: E 阶段 references 信源文件 + examples

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 步骤 1：生成 `references/source.md`（源码信源登记：仓库地址、版本 v0.14.0、源码目录结构）
  - 步骤 2：生成 `examples/` 示例文档（基础编解码示例、token 计数/模型映射示例）
- **Acceptance Criteria Addressed**: 信源先行（AC-8）、frontmatter 完整（AC-3）
- **Test Requirements**:
  - `programmatic` TR-4.1: references/ 先于 concepts/ 创建（检查时间戳）
  - `human-judgement` TR-4.2: 示例代码与 core.py API 一致

## [x] Task 5: E 阶段 concepts 第一批（入门 + 核心组，00-05，6 篇）

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 生成 00-overview（整体架构）、01-getting-started（安装与公开 API）、02-encoding-api（Encoding 核心方法）、03-bpe-tokenizer（BPE 分词器算法）、04-rust-core（Rust 实现与 PyO3 绑定）、05-registry-model（注册表 + 模型映射）
  - 文档 frontmatter 含 type/title/description/tags/generated/verified/status/stale_after/sources 全字段，sources 指向 references/source.md 与相关 facts-*.md
- **Acceptance Criteria Addressed**: AC-2/3, 分批纪律（AC-8）
- **Test Requirements**:
  - `programmatic` TR-5.1: 每篇 frontmatter 完整，sources 指向已存在文件
  - `human-judgement` TR-5.2: 500-5000 字，构成从入门到核心的递进路径

## [x] Task 6: E 阶段 concepts 第二批（进阶 + 扩展，06-08，3 篇）

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 生成 06-encoder-loading（BPE 文件加载 load.py）、07-openai-vocabularies（tiktoken_ext 的 4 种公开 encoding）、08-educational-module（_educational.py 教学 SimpleBytePairEncoding）
- **Acceptance Criteria Addressed**: AC-3, AC-9
- **Test Requirements**:
  - `programmatic` TR-6.1: 每篇 frontmatter 完整
  - `human-judgement` TR-6.2: 进阶文档准确覆盖 load/ext/educational 模块

## [x] Task 7: E 阶段 index 与 log 收尾

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 最后生成根 `index.md`（含 okf_version: "0.2"）、`concepts/index.md`、`examples/index.md`、`references/index.md`、`log.md`
  - index 完整列出本 bundle 全部内容文档，参照 bundles/chaos/apache-tvm/ 的 index 格式
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-7.1: 根 index 含 okf_version，子目录 index 不含 frontmatter
  - `programmatic` TR-7.2: index 列出所有 concept/example，无遗漏

## [x] Task 8: V 阶段独立验证与修复

- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 结构检查 + frontmatter 检查 + 链接检查（`/` 开头 bundle-relative 路径无断裂）
  - Grep 验证：文档中每个 Python 类名/方法名/函数名（Encoding/encode/decode/get_encoding/encoding_for_model/load_tiktoken_bpe/SimpleBytePairEncoding 等）在 tiktoken/ 源码存在；Rust 导出在 py.rs 存在
  - 代码示例检查：encode("hello world") 等与 core.py 签名一致
  - 修复所有问题后输出验证记录
- **Acceptance Criteria Addressed**: 零虚构 API（AC-4）、链接无断裂（AC-5）
- **Test Requirements**:
  - `programmatic` TR-8.1: 零虚构 API（Grep 验证每个 API 名）
  - `programmatic` TR-8.2: 零断裂链接，frontmatter 全字段完整

## [x] Task 9: C 阶段模式沉淀

- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 回顾 Python+Rust 双层小中型库的五阶段学习过程
  - 记录经验教训、反模式（≥5，新增至模式文档或复用 source-code-to-okf-wiki 既有反模式），沉淀至 `.agents/docs/retrospective/patterns/` 对应目录
- **Acceptance Criteria Addressed**: 模式可复用（AC-C）
- **Test Requirements**:
  - `human-judgement` TR-9.1: 至少记录 3 个本次实践经验教训，反模式总数 ≥5

---

# Task Dependencies

- Task 1、Task 2 可并行执行
- Task 4 依赖 Task 3；Task 5 依赖 Task 4；Task 6 依赖 Task 5；Task 7 依赖 Task 6（串行，保证信源先行与分批纪律）
- Task 8 依赖 Task 7；Task 9 依赖 Task 8
- Task 0 独立执行，输出供 Task 3（I 阶段）参考