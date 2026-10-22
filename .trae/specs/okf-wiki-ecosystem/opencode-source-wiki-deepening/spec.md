---
spec: opencode-source-wiki-deepening
title: "OpenCode 2.0.32 同快照源码深化与 Wiki 增量"
created: 2026-10-21
status: approved
methodology: "seven-concepts-cmd + source-code-to-okf-wiki：0→R→I→E→V→C"
content-sensitivity: public
source: "../opencode-source-wiki/spec.md"
source_skills: [seven-concepts-cmd, source-code-to-okf-wiki, TRAE-spec-mode]
source_commit: "6ec56821d63100fe5bda45b759364f561c56b359"
target_dir: projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode
---

# OpenCode 同快照源码深化

## Overview

- **Summary**: 在既有 OpenCode Wiki 内，补充上一轮仅清单级或入口级覆盖的实现机制。
- **Purpose**: 让读者从包图继续读到配置、执行环境、交互状态及工程验证，理解真实调用关系与限制。
- **Target Users**: OpenCode 架构学习者、扩展开发者及沿源码核验教程的读者。

## Background & Context

用户要求全面学习本地 `external/dao/anomalyco/opencode` 并更新 awesome-okf-xs 的 Wiki。
2026-10-21 只读调查确认源码 HEAD 与上一轮 Wiki 固定 commit 相同，根 manifest 版本为 `2.0.32`。
上一轮已完成规格见 [前轮任务](../opencode-source-wiki/tasks.md) 和 [前轮审查](../opencode-source-wiki/review.md)。
本轮不重开已完成任务，不把前轮批准或审查结论视为新增内容的批准与验证。

既有工作区地图清点 39 个 manifest，覆盖等级为深读 6、入口/接口读取 4、清单级 29；这些数字是前轮记录，不能改写成当时已深读全部包。
当前 bundle 已有 F-001～F-114、概念编号 00～09、示例编号 01～02。
新增事实默认从 F-115 续接，实施前以最新磁盘状态核实。

本轮调查时，子项目四个父级索引和 `vibeknow-cli/` 存在他方改动，目标 OpenCode bundle 无未提交变更。
两个 rebase 状态目录均不存在。主仓亦有他方 Skill 与看板变更，本轮不改这些文件。

## Goals

- 保留同一不可变源码坐标，深化既有 Wiki，避免重建重复 bundle。
- 覆盖下列六个主题的代表性实现链路，分别声明已读文件、证据与未读范围。
- 为主要机制配对实现与测试或调用方证据；缺少测试时如实说明。
- 以事实、洞察及渐进教程支持读者定位实现与验证理解。

## Non-Goals

- 不宣称逐文件穷尽阅读整个 monorepo，不为凑篇数或事实数拆分内容。
- 不修改 OpenCode checkout、源码、配置或 Git 状态，不安装其依赖，不运行付费模型或真实云部署。
- 不覆盖前轮事实、覆盖统计或审查历史；发现事实错误时只做有证据且写入日志的最小修订。
- 不修改其他知识包、共享父级索引、全局看板、子项目治理规则或构建配置。
- 不执行 git add、commit、push、fetch、reset、revert 或历史改写。
- 不自动新增主仓方法论资产；C 阶段仅作候选评估，入库与提交另获授权。

## Functional Requirements

- **FR-1 配置与上下文**: 解释当前配置合并/发现、skills、instructions 与会话压缩的代表性路径；与旧版配置/会话篇明确区分。
- **FR-2 Codemode**: 阅读 `packages/codemode` 与 Core 接线，解释执行环境、宿主工具调用、运行时复用及限制；不将解释器或测试通过等同于安全隔离证明。
- **FR-3 扩展契约**: 深化 Schema/Plugin 公共契约、插件加载与权限接线，明确内部服务与对外接口边界；不重复前轮 Provider/MCP 概述。
- **FR-4 产品状态流**: 深化 TUI、App 与 Desktop 的代表性状态同步、持久化或进程通信链路，明确各端差异与生命周期。
- **FR-5 验证与回放**: 阅读 simulation、http-recorder 及代表性测试/夹具，区分源码静态核验、测试已存在和本轮实际运行结果。
- **FR-6 云端与更新**: 阅读 console、stats、services 的代表性入口与接线，解释服务边界和更新链路；不把源码配置扩写为线上可用性或部署验证。
- **FR-7 增量知识组织**: 新增本轮信源登记、编号事实、3～5 条洞察及知识地图，续接概念/示例编号；每篇新教程有独立主题、证据与相关概念链接。
- **FR-8 导航与历史**: 内容定稿后再更新目标 bundle 根与四个子目录索引、版本和日志；保留旧信源及前轮记录。

## Non-Functional Requirements

- **NFR-1**: 中文 Markdown，遵循子项目 OKF v0.2 YAML frontmatter，派生产物有 `sources`，子目录 index 不加 frontmatter。
- **NFR-2**: 新断言引用编号事实；事实含仓库相对路径、固定 commit 链接和可定位证据，推断留在洞察/解释层。
- **NFR-3**: 数量断言记录统计对象与口径，采集时工具计数，V 阶段用独立手段复核。
- **NFR-4**: 面向读者的信源使用固定 commit URL，不依赖本机路径、临时目录或浮动分支。
- **NFR-5**: 每批新增文件不超过 7；信源先于引用它的教程，索引最后更新。
- **NFR-6**: 单次逻辑 LLM 调用称 step，不称 provider turn；前轮疑似措辞问题须对源码核验后再决定最小修订。

## Constraints

- **Source**: `anomalyco/opencode@6ec56821d63100fe5bda45b759364f561c56b359`。
- **Destination**: `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/`，按子项目自治规则落盘，不迁往主仓 `docs/`。
- **Workflow**: 本规格与任务队列获显式批准后开始实施；知识文件只在目标 bundle 内写入；`review.md` 仅在实施队列清空后创建。
- **Validation**: 使用 py314 的子项目质量门及文档构建；无关在途失败分开归因，不代修。

## Assumptions

- 源码 commit 可从本地对象库读取；远端 URL 是长期引用坐标，本轮不预设实时网络可达性。
- 六个主题采用关键链路分层采样。内部章节可以合并，但不能静默移除主题；实质变更回到批准门。
- 示例可以是源码导读或明确标注的示意；只有实际运行过的片段才能宣称本轮运行验证通过。

## Acceptance Criteria

### AC-1: 修改与历史边界
- **Type**: `rule`
- **Pass Condition**: 本轮写入仅限本规格目录和目标 bundle，源码未改变；无暂存、提交、推送或历史改写；前轮历史未覆盖，他方变更未修改。
- **Evidence**: 两仓状态、显式变更清单、前后 diff、编号与历史条目比对。

### AC-2: 源码事实与信源真实性
- **Type**: `rule`
- **Pass Condition**: 新事实编号唯一且续接基线；每条可回到指定 commit 的文件与代码；主要机制有实现和测试/调用方证据或明确缺口说明；所有新 API 与数量断言完成独立核验。
- **Evidence**: 新事实、信源登记、符号/签名检索、计数记录及 Review。

### AC-3: 六主题实现覆盖
- **Type**: `rubric`
- **Dimension**: 实现深度与边界诚实度
- **Scale**: 0-3
- **Anchors**: 0 = 重复旧篇或臆造；1 = 六主题有清单但缺实现链路；2 = 每个主题至少一条代表性实现链路及已读/未读边界；3 = 达到 2，且关键机制有测试或调用方对照、跨包关系与失败边界。
- **Pass Threshold**: >= 2
- **Evidence**: 本轮覆盖矩阵、新事实、教程与源码引用。

### AC-4: 洞察与学习可用性
- **Type**: `rubric`
- **Dimension**: 增量教程连贯性
- **Scale**: 0-3
- **Anchors**: 0 = 零散摘要；1 = 有章节但重复旧知识或前置关系不清；2 = 3～5 条完整证据四元组洞察，新篇主题独立且能沿学习路径查源；3 = 达到 2，且导读示例、限制与反常识说明帮助读者自行核验。
- **Pass Threshold**: >= 2
- **Evidence**: 新洞察与知识地图、教程交叉引用、独立 Review。

### AC-5: OKF 与导航完整性
- **Type**: `rule`
- **Pass Condition**: 新文档元数据及来源合规，内部链接可达，编号续接；受影响索引的人类导航与 toctree 收录集合等于实际内容集合；日志追加本轮坐标、变化及修订原因。
- **Evidence**: 元数据/链接/集合比对、toctree 门禁、bundle diff。

### AC-6: 验证与交付
- **Type**: `rule`
- **Pass Condition**: 子项目质量门和文档构建实际运行并记录退出状态；目标 bundle 无新增诊断；无关失败有归属说明；独立 Review 覆盖全部 AC/TR、结果为 pass，无遗留可行动发现；C 候选评估有结论。
- **Evidence**: 命令结果、构建日志、tasks Completion Evidence、review.md。

## Approval

2026-10-21 已通过 NotifyUser 获得本文件与 [tasks.md](tasks.md) 的显式批准（返回：User has approved the given files, continue working）。批准不包含 Git 提交、源码修改、真实模型调用或云部署。

## Open Questions

无必须先澄清的内容问题。默认按六主题深化；具体篇名与事实数量由 R/I 的证据决定，不设数量凑齐指标。
