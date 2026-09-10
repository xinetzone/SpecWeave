---
title: "网易有道开源生态 OKF Wiki 教程 - 产品需求文档"
status: "draft"
id: netease-youdao-okf-wiki
---

# 网易有道开源生态 OKF Wiki 教程 Spec

## Why

迁移前，6 个网易有道开源项目（BCEmbedding、Confucius4-TTS、EmotiVoice、LobsterAI、QAnything、ScholarClaw）以临时克隆形式存放于工作区旧临时克隆目录，覆盖 Embedding/RAG、语音合成、AI Agent 桌面应用、学术搜索四个技术方向。这些源码缺乏结构化中文知识文档，且临时信源存在引用断裂风险。需按 source-code-to-okf-wiki 工作流（阶段0 信源稳定性门 + R→I→E→V→C 五阶段）生成可溯源、零虚构 API 的 OKF v0.2 中文 Wiki 教程。

## What Changes

- **阶段0（G0 信源稳定性门）**：将 6 个临时克隆迁移为 `vendor/netease-youdao/<repo>` git 子模块，固定到 release tag 或 commit hash（禁止 main/master 浮动分支），更新 vendor 区域元数据（AGENTS.md 路由表、README.md 依赖清单、VERSION.md 版本记录），GATE-SPS 零引用扫描通过后清理旧临时克隆目录。参照先例 [okf-libs-vendor-migration](../../migration-archival/okf-libs-vendor-migration/spec.md)。
- **R 阶段**：对 6 个仓库逐模块源码阅读，提取编号事实清单（F-xxx），零推测，每条事实指向 vendor 稳定路径。
- **I 阶段**：基于事实清单提炼核心架构洞察（陈述+证据+反常识+行动四元组），设计知识地图与学习路径。
- **E 阶段**：在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/netease-youdao/` 生成生态分组索引 + 6 个知识束（每仓库一束，参照 [tencent-okf-wiki](../tencent-okf-wiki/spec.md) 先例）。信源先行（references/ 先生成）、分批生成（每批 ≤7 文件）、index 最后写。
- **V 阶段**：独立验证——Grep 级 API 真实性验证、计数断言比对、链接检查、frontmatter 完整性、toctree 导航完整性（`scripts/check-toctrees.py`）。
- **C 阶段**：模式沉淀——回顾工作流，将有价值的新反模式/改进点回写 source-code-to-okf-wiki 模式文档，原子提交收尾。
- **无 BREAKING 变更**（不修改任何源码，不改动既有 bundle）。

## Impact

- Affected specs: `.trae/specs/okf-wiki-ecosystem/`（本 spec 新增）；source-code-to-okf-wiki 模式文档（C 阶段可能更新）
- Affected code: `vendor/`（新增 6 个 third_party 子模块 + 元数据）；旧临时克隆目录（迁移后已清理）；`projects/awesome-okf-xs/doc/bundles/jishu/ai/netease-youdao/`（新增分组 + 6 个 bundle）
- 受影响 Skill：source-code-to-okf-wiki（方法论）、seven-concepts-cmd（场景4 知识沉淀链路编排）

## ADDED Requirements

### Requirement: 信源稳定性门（G0，R 阶段前强制）

系统 SHALL 在事实采集开工前完成 6 个仓库的 vendor 子模块迁移，且满足：

| 仓库 | 上游 | 固定方式 | 当前基线 |
|---|---|---|---|
| BCEmbedding | git@github.com:netease-youdao/BCEmbedding.git | commit hash（无 tag） | 1aa07ea |
| Confucius4-TTS | git@github.com:netease-youdao/Confucius4-TTS.git | commit hash（无 tag） | 4fb32c4 |
| EmotiVoice | git@github.com:netease-youdao/EmotiVoice.git | release tag + hash | v0.3 @ 59f0f36 |
| LobsterAI | git@github.com:netease-youdao/LobsterAI.git | release tag + hash | 2026.9.4 @ 7592cd0 |
| QAnything | git@github.com:netease-youdao/QAnything.git | release tag + hash | v2.0.0 @ 615417a |
| ScholarClaw | git@github.com:netease-youdao/ScholarClaw.git | commit hash（无 tag） | 97bdb5e |

- **WHEN** 检查 `.gitmodules` 与 `git submodule status`
- **THEN** 6 个子模块均为 gitlink（mode 160000），以固定 tag/commit 检出（无前缀 `-`/`+`）；VERSION.md 记录完整 hash + 远程 URL + 许可证；旧临时克隆目录已清理且 GATE-SPS 扫描 rc=0
- **THEN** facts.md 与文档中的信源路径只指向 `vendor/netease-youdao/`，禁止 `file:///` 指向临时目录

#### Scenario: tag 选型冲突

- **WHEN** 某仓库 HEAD 超前于所选 tag 且文档引用的 API 落在版本变更集合中
- **THEN** 按"文档引用集合 ∩ 版本变更集合 = ∅"判据改选更新 tag，仍无合规 tag 则固定 commit hash 并记录获取方式

### Requirement: 事实采集（G1）

系统 SHALL 对每个仓库逐模块阅读源码，产出编号事实清单（F-xxx），每条事实指向具体 vendor 源码路径。

- **WHEN** 审查事实表述
- **THEN** 不出现"用于"/"目的是"/"设计为"等推断性表述（推断移至 I 阶段）；核心模块（按各仓库 README/AGENTS.md/目录结构定义）全覆盖

### Requirement: 架构洞察（G2）

系统 SHALL 基于事实清单为每个仓库提炼 3-5 个核心洞察，并设计知识地图（概念文档分组、依赖关系、编号学习路径）。

- **WHEN** 审查洞察质量
- **THEN** 每条洞察包含陈述、证据（引用 F-xxx 编号）、反常识、行动四元组；concepts/ 文档按 00-NN 编号形成入门→高级递进路径

### Requirement: OKF 文档批量生成（G3）

系统 SHALL 按 OKF v0.2 规范生成 1 个生态分组索引 + 6 个知识束，每束含 `references/`（信源登记 + facts/insights）、`concepts/`、`examples/`、`index.md`（含 okf_version frontmatter）、`log.md`。

- **WHEN** 检查生成顺序
- **THEN** references/ 先于 concepts/examples 生成；每批 ≤7 文件；各级 index.md 最后写且含 `{toctree}` 块；子目录 index.md 无 frontmatter
- **WHEN** 检查 frontmatter
- **THEN** 每个非保留 .md 文件含 type/title/description/tags/generated/verified/status/stale_after/sources 全部字段，sources 指向已存在的 references/ 信源文件

### Requirement: 独立验证（G4）

系统 SHALL 对每个 bundle 执行独立验证并输出验证报告，修复全部问题后交付。

- **WHEN** 对文档中引用的每个类名/方法名/函数签名在 vendor 源码中执行 Grep
- **THEN** 零虚构 API；所有"X个/Y份/Z处"数量陈述经 Glob/Grep 独立计数比对一致；交叉链接全部 `/` 开头 bundle-relative 路径且无断裂；`python scripts/check-toctrees.py` 导航链完整

### Requirement: 模式沉淀（G5）

系统 SHALL 在交付后回顾工作流顺利点与问题点，萃取可复用模式并原子提交。

- **WHEN** 发现新的反模式或改进点
- **THEN** 回写 source-code-to-okf-wiki 相关模式文档；变更按 Conventional Commits 原子提交（单一职责）

## Non-Goals (Out of Scope)

- 不修改任何源码仓库内的文件（third_party 只读）
- 不编译/运行源码（静态阅读为主）
- 不生成英文文档；不构建可独立运行的代码示例
- 不更新 awesome-okf-xs 根 `bundles/index.md` 分组索引（由 docgen 流程统一更新）
- 不执行 awesome-okf-xs 子模块的 commit/push（由用户确认后另行处理）
- 不覆盖旧临时克隆目录之外的 `.chaos/libs/` 内容

## Constraints

- **Technical**: Windows + PowerShell 环境；Grep 路径分隔符需正确处理；vendor 子模块使用 SSH 远程 URL（与现有 `.gitmodules` 多数条目一致）
- **Business**: 遵循 vendor 区域治理规范（check-vendor.py 合规）；projects/awesome-okf-xs 为 git submodule，写入前须阅读其 `AGENTS.md`（子项目路由）
- **Dependencies**: source-code-to-okf-wiki Skill 五阶段工作流与 Prompt 模板；seven-concepts 方法论编排质量门；先例 `bundles/jishu/ai/tencent/` 作为分组格式参考

## Open Questions

- [ ] BCEmbedding/Confucius4-TTS/ScholarClaw 无 release tag，固定 commit hash 之外是否需要向 vendor VERSION.md 标注"无 tag 版本基线"？（建议：标注 tag 字段为 `N/A@<hash>`）
- [ ] 6 个知识束的规模差异大（LobsterAI 为完整 Electron 应用、ScholarClaw 仅 3 个 TS 源文件），concepts/ 文档数量下限是否统一按"核心模块全覆盖"判据而非固定数量？（建议：是，按 NFR 覆盖度判据）
- [x] 旧临时克隆目录清理前，是否需要保留一份 HEAD commit 对照表在 spec 目录备查？（建议：是，作为迁移基线记录）→ 已落实：migration-baseline.md
