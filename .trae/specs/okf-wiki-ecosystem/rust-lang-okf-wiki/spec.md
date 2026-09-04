---
title: "rust-lang 全量子项目 OKF Wiki 教程生成"
status: "draft"
---

# rust-lang 全量子项目 OKF Wiki 教程生成 Spec

> 方法论：seven-concepts-cmd（场景 4：知识沉淀，链路 R→I→E→V→C）+ source-code-to-okf-wiki 五阶段工作流（G1-G5 质量门）。

## Why

`external/libs/rust-lang/` 下三个 Rust 官方核心仓库（rust 编译器 62,286 文件、cargo 3,072 文件、rfcs 665 文件）目前以原始源码形式存在，缺乏结构化中文知识文档。将其转化为可溯源、AI 可读的 OKF v0.2 知识包并纳入 awesome-okf-xs 知识库（当前 11 域 30 组 263 束），可填补 Rust 语言核心域空白，为后续 Rust 相关开发任务提供冲突裁决级可信知识源。

## What Changes

- 新增 `projects/awesome-okf-xs/doc/bundles/rust/` 技术域（第 12 域），含 3 个 OKF v0.2 知识包：
  - `rust/rust/` — rustc 编译器与标准库（锚点束，镜像 python/cpython 定位）
  - `rust/cargo/` — Cargo 包管理与构建系统
  - `rust/rfcs/` — Rust RFC 语言设计决策与演进流程
- 更新 `bundles/index.md` 总索引：域数 11→12、分组 30→31、束数 263→266，新增 mermaid 节点、导航表行与 toctree 条目
- 不修改 `external/libs/rust-lang/` 下任何源码（只读学习，外部依赖区）

## Impact

- Affected specs: awesome-okf-xs OKF v0.2 frontmatter 规范（遵循，不修改）
- Affected code: 仅新增 `doc/bundles/rust/` 目录树与修改 `doc/bundles/index.md`（awesome-okf-xs 子模块工作树内，用户指定的目标位置）
- 信源基线（只读锚定）：
  - `external/libs/rust-lang/rust` @ `e457a7b0d326d67b4322ef0d11bd715cfaeda48f`（main, 2026-08-27）
  - `external/libs/rust-lang/cargo` @ `75d17360928f57ff2a7d2f2da1c753f5fe1926d1`（master, 2026-08-26）
  - `external/libs/rust-lang/rfcs` @ `354518a8c9025f40be6f730452c1bfe71a12dc22`（master, 2026-08-15）

## Scale Strategy（规模决策）

rust 仓库 62,286 文件命中 source-code-to-okf-wiki 适用性决策树的「超大规模源码」分支 → 采用**分层采样策略**（架构文档 → 核心接口 → 按需深入），覆盖方式为：

- 编译器：按**流水线阶段**横向组织（driver→parse→expand→HIR→typeck→borrowck→MIR→codegen），不逐一精读 90+ 个 rustc_* crate，但每个阶段对应的核心 crate 必须阅读
- 标准库：按 **core/alloc/std 三层分层**组织，重点读 library/ 目录布局与 std 关键模块
- bootstrap 构建系统：读 src/bootstrap 与 x.py 的阶段化构建流程
- tests/、llvm-project、gcc 等子模块与测试集不逐文件精读，在概念文档中登记其角色

cargo（3,072 文件）与 rfcs（665 文件）按常规全量核心模块阅读。

## ADDED Requirements

### Requirement: rust 域三知识包生成

系统 SHALL 在 `projects/awesome-okf-xs/doc/bundles/rust/` 下生成 3 个符合 OKF v0.2 规范的中文知识包，每个包含 concepts/、examples/（有可提取示例时）、references/、根 index.md（含 `okf_version: "0.2"`）与 log.md。

#### Scenario: Bundle 结构合规
- **WHEN** 检查任一知识包目录
- **THEN** 根 index.md 含 `okf_version: "0.2"` frontmatter 与 `{toctree}`；子目录 index.md 无 frontmatter；每个内容文档含完整 frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）

#### Scenario: 信源先行与分批生成
- **WHEN** E 阶段生成文档
- **THEN** references/ 先于 concepts/ 生成，index.md 最后写，每批 concepts/ ≤7 文件

#### Scenario: 零虚构 API
- **WHEN** 文档引用 rustc/cargo 的 crate 名、struct、方法、配置键
- **THEN** 每个引用在源码中 Grep 验证存在，V 阶段输出验证记录

#### Scenario: 根索引更新
- **WHEN** 三个 bundle 定稿
- **THEN** `bundles/index.md` 的 mermaid 生态图、推荐入门路径、十二域分组导航表、frontmatter 计数（total_bundles: 266、groups: 31、domains: 12）与 toctree 均包含 rust 域

#### Scenario: 质量门通过
- **WHEN** V 阶段完成
- **THEN** 在 awesome-okf-xs 内 `invoke gates.toctrees` 与 `invoke gates.utf8` 通过；所有 `/` 开头 bundle-relative 交叉链接指向存在的文件

## MODIFIED Requirements

### Requirement: 知识包总索引
`bundles/index.md` 从「11 域 30 组 263 束」更新为「12 域 31 组 266 束」，新增「🦀 Rust 语言核心」域导航行，说明列涵盖 rustc 编译器流水线、Cargo 构建系统、RFC 设计演进。

## REMOVED Requirements

无。
