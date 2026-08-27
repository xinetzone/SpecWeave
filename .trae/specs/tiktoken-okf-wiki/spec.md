# tiktoken 源码学习 OKF Wiki 教程生成 - Spec

## Why

`d:\AI\.chaos\ai\libs\tiktoken`（OpenAI 官方 BPE 分词器库，v0.14.0）以源码形式静态存在，缺乏结构化的中文知识文档。开发与学习任务难以快速定位其架构、核心 API 与设计模式，且 AI 在无事实来源时易虚构 API。本任务将对该库执行系统化源码阅读（source-code-to-okf-wiki 的 R→I→E→V→C 五阶段链路），在 `d:\AI\bundles` 生成符合 OKF v0.2 规范的可溯源中文 Wiki 教程 bundle。

## What Changes

- 在 `d:\AI\bundles\chaos\tiktoken\` 创建 OKF v0.2 bundle，包含：
  - `index.md`（根索引，含 `okf_version: "0.2"` frontmatter）
  - `log.md`（变更日志）
  - `concepts/`（概念文档，约 9 篇，编号 00-08，分入门/核心/进阶）
  - `examples/`（示例文档，含基础编解码、token 计数等）
  - `references/`（信源登记 `source.md`、编号事实清单 `facts-*.md`、洞察 `insights.md`）以及各级 `index.md`
- 调用 `source-code-to-okf-wiki`、`seven-concepts-cmd`（知识沉淀场景 R→I→E → C）、`deep-research` 三个 Skill 协同完成
- **BREAKING**: 不修改 `d:\AI\.chaos\ai\libs\tiktoken` 下任何源码（该路径为第三方依赖，禁止本地改动）

## Impact

- **Affected specs（相关知识基座）**: source-code-to-okf-wiki 工作流、seven-concepts-cmd 质量门（G1-G4）、OKF v0.2 bundle 规范
- **Affected bundles**: 新增 `bundles/chaos/tiktoken/`（独立新增，不影响现有 7 个 chaos bundle）
- **Affected code（参考对象，只读）**: `d:\AI\.chaos\ai\libs\tiktoken`（Python: `tiktoken/{__init__,core,registry,model,load,_educational}.py` 与 `tiktoken_ext/openai_public.py`；Rust: `src/{lib,py}.rs`；测试: `tests/test_*.py`；脚本: `scripts/*.py`）
- **输出 bundle 路径决策**: 现有 bundle 统一位于 `d:\AI\bundles\chaos\<name>\`，故 tiktoken 置于 `bundles/chaos/tiktoken/`，与既有组织保持一致

## ADDED Requirements

### Requirement: OKF v0.2 Bundle 结构生成
系统 SHALL 在 `d:\AI\bundles\chaos\tiktoken\` 生成完整 OKF v0.2 目录结构，包含 `index.md`（含 `okf_version: "0.2"` frontmatter）、`log.md`、`concepts/`、`examples/`、`references/` 及各子目录 `index.md`。

#### Scenario: 结构合规
- **WHEN** 检查 `bundles/chaos/tiktoken/` 目录
- **THEN** 根 `index.md` 含 `okf_version` frontmatter，子目录 `index.md` 不含 frontmatter，`references/` 先于 `concepts/` 生成，`index.md` 最后生成

### Requirement: 五阶段源码学习链路（R→I→E→V→C）
系统 SHALL 遵循 source-code-to-okf-wiki 五阶段执行源码学习：R 阶段零推测事实采集（facts-*.md）、I 阶段提炼 3-5 个架构洞察并设计知识地图（insights.md）、E 阶段分批生成文档（每批 ≤7 文件）、V 阶段独立验证、C 阶段模式沉淀。

#### Scenario: R 阶段事实零推测
- **WHEN** 生成编号事实清单 F-xxx
- **THEN** 每条事实无"用于/目的是/设计为"等推断词，指向具体源码文件路径，核心模块全覆盖（Python 门面、Rust 核心、公开 4 个 encoding、BPE 加载、教学模块）

#### Scenario: V 阶段零虚构 API
- **WHEN** 验证文档中引用的每个类名/方法名/函数名（如 `Encoding`、`encode`、`decode`、`get_encoding`、`encoding_for_model`、`load_tiktoken_bpe`、`SimpleBytePairEncoding`、Rust `py.rs` 导出函数）
- **THEN** 在源码目录 Grep 验证全部存在，无凭空虚构 API

### Requirement: deep-research 辅助边界
系统 SHALL 使用 deep-research 补充 BPE 算法原理、token 计数、OpenAI 分词器演进等外部背景知识，仅用于辅助理解 I 阶段洞察与文档背景叙述，**不得**将外部信息作为源码事实写入 facts-*.md，所有 API/事实以源码 Grep 验证为准。

#### Scenario: 外部背景与源码事实分离
- **WHEN** 引入 BPE/分词器背景知识
- **THEN** 背景知识标注为外部来源，facts-*.md 仅含源码可验证事实

### Requirement: 中文文档规范
系统 SHALL 使用规范现代汉语撰写全部文档，英文技术术语首次出现时括号注释，概念文档 500-5000 字、使用 `##` 二级标题分节、结尾含"## 相关概念"章节，交叉链接使用 `/` 开头的 bundle-relative 绝对路径。

#### Scenario: 格式一致性
- **WHEN** 审查任意概念文档
- **THEN** frontmatter 含 type/title/description/tags/generated/verified/status/stale_after/sources 全部字段，sources 指向 references/ 下已存在文件，交叉链接无 `../` 相对路径

### Requirement: 模式沉淀（C 阶段）
系统 SHALL 回顾本次工作流执行过程，将可复用经验沉淀至 `.agents/docs/retrospective/patterns/` 对应目录，并记录反模式与迁移验证。

#### Scenario: 模式可复用
- **WHEN** C 阶段完成模式萃取
- **THEN** 模式文档含触发场景、核心步骤、反模式（≥5）与迁移验证

## MODIFIED Requirements

无（本任务为全新 bundle 生成，不修改既有 spec 需求）。

## REMOVED Requirements

无。