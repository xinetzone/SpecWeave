---
spec: opencode-source-wiki
title: "OpenCode 2.0.32 源码 Wiki 增量扩展"
created: 2026-10-20
status: draft
methodology: "seven-concepts-cmd（知识沉淀 R→I→E；source-code-to-okf-wiki：0→R→I→E→V→C）"
content-sensitivity: public
source_skills: [seven-concepts-cmd, source-code-to-okf-wiki]
source_dir: external/dao/anomalyco/opencode
source_commit: "6ec56821d63100fe5bda45b759364f561c56b359"
target_dir: projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode
---

# OpenCode 2.0.32 源码 Wiki 增量扩展 Spec

## Overview

- **Summary**：基于 OpenCode 固定源码快照，对已有 OKF bundle 做可溯源的增量扩展。
- **Purpose**：把现有以 2026-08-23 旧快照为基线的知识，扩展为能解释当前 OpenCode monorepo 主要组件、关键运行路径和组件边界的中文学习教程。
- **Target Users**：AI Agent 架构学习者、OpenCode 使用者及希望沿源码验证技术结论的开发者。

## Goals

- 以 `anomalyco/opencode` commit `6ec56821d63100fe5bda45b759364f561c56b359` 为本轮唯一源码事实基线；包版本记录为 `2.0.32`，并在实施时对照该 commit 再核验。
- 在现有 `jishu/ai/frameworks/ai-agent/opencode/` bundle 中增量扩展，不另建同主题 bundle。
- 对 OpenCode monorepo 做分层全面学习：清点工作区包和主要子系统，深读关键架构、接口和端到端数据流；按源码规模采用分层采样，不以逐文件通读作为覆盖标准。
- 产出明确区分旧快照与新快照的事实、洞察、信源和学习路径；新事实可回溯到固定 commit 中的具体源码位置。

## Non-Goals

- 不修改 `external/dao/anomalyco/opencode` 的任何源码、配置或 Git 状态。
- 不新建重复 OpenCode bundle，不将本轮事实混入旧版事实而抹去版本边界。
- 不重写旧版已验证章节；仅在核实版本漂移后，为避免读者混淆而做有证据、可追溯的最小修订。
- 不修改与该 bundle 导航无直接关系的全局索引或其他知识包。
- 不执行新的 git commit 或 push；本任务交付包含验证结果，提交需用户另行明确授权。用户已明确接受既有并行聚合提交 `7a219626fdeb0f9b9cb2f12e47666074ee550323` 及其父仓库指针提交 `baedea3361db75749a34cfcd812f362d92546bf2` 作为本任务的例外；该接受仅确认现存历史，不授权新增提交、推送、回滚、重置或改写历史。
- 不因本次学习顺手新增 SpecWeave 主权区的方法论资产；C 阶段只评估是否产生值得另行提案的可复用模式。

## Background & Context

现有 OpenCode bundle 位于 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/`，已有 5 篇概念文档、1 篇示例、源码参考和 F-001～F-080 事实记录。其日志标记的源码快照日期为 2026-08-23，旧事实中的包版本为 `1.18.21`；该内容是历史基线，不应默认代表当前源码。

本轮本地仓库位于 `external/dao/anomalyco/opencode`，工作树干净，当前 HEAD 为 `6ec56821d63100fe5bda45b759364f561c56b359`，根 `package.json` 声明版本 `2.0.32`。本地路径只作为本轮读取位置，不写入面向读者的绝对路径引用；知识文档使用带 commit 的上游源码链接，使引用不依赖本机路径或浮动分支。

项目规模属于大型 monorepo。学习范围以工作区包清单和子系统地图建立覆盖面，再选择核心源码路径进行深读。预期地图至少检查 CLI/运行时、会话与 Agent 执行、模型与 provider、工具与权限、MCP/插件、Server/API/Protocol/Client SDK、TUI/UI、桌面端与 Web、持久化、构建发布及测试边界；某领域若在该快照中不存在或不属于核心范围，须以事实说明，不得为凑齐清单而臆造。

## Functional Requirements

### Requirement: 在既有 bundle 内增量扩展

系统 SHALL 将本轮产物写入现有 OpenCode bundle，并保留旧快照知识作为可区分的历史基线。

#### Scenario: 目标 bundle 已存在

- **WHEN** 实施者开始 E 阶段
- **THEN** 新增的源码参考、版本化事实与洞察、概念文档和示例 SHALL 写入现有 bundle
- **AND** 新文档编号 SHALL 接续当前最大编号，不重排既有文档
- **AND** 已验证旧内容 SHALL 保持不变，除非源码对照证明确有误导且修订被记录在 `log.md`

### Requirement: 固定源码坐标并建立可审计事实

系统 SHALL 将所有新结论锚定到指定 commit，并把事实与旧快照分开记录。

#### Scenario: 采集当前快照事实

- **WHEN** R 阶段读取 OpenCode 源码
- **THEN** 事实清单 SHALL 续接 F-081 起的编号，保存为版本化事实文档
- **AND** 每条事实 SHALL 标注仓库相对文件路径及可复核的 commit 固定引用
- **AND** 数量类事实 SHALL 记录统计对象和口径，并由脚本或可重复的命令输出支持
- **AND** 概述、推断和设计意图 SHALL 不混入客观事实表述

### Requirement: 建立架构洞察与学习地图

系统 SHALL 从本轮事实提炼架构洞察，并据此确定教程组织和阅读路径。

#### Scenario: 形成知识地图

- **WHEN** R 阶段事实门通过
- **THEN** I 阶段 SHALL 产出 3～5 条互不重复的核心洞察
- **AND** 每条洞察 SHALL 包含陈述、F 编号证据、反常识点和对教程组织或读者行动的指导
- **AND** 知识地图 SHALL 标明新增文档清单、学习顺序、覆盖的 F 编号及包/子系统边界

### Requirement: 生成全面且有边界的 OKF 教程

系统 SHALL 以知识地图为依据增量生成面向读者的中文教程，而非按文件清单堆砌源码摘要。

#### Scenario: 学习当前 OpenCode 架构

- **WHEN** 读者从 bundle 入口进入本轮内容
- **THEN** 教程 SHALL 呈现包边界、主要组件职责、关键接口及至少一条端到端执行/数据流
- **AND** 教程 SHALL 覆盖工作区包清点结果，以及会话/Agent 执行、模型与工具、服务/API 与协议、交互界面、扩展机制、持久化和工程生命周期等适用领域
- **AND** 每个新增技术文档 SHALL 标注本轮源码快照及其 `sources`，并以 bundle-root 路径链接其他 bundle 文档
- **AND** 代码示例 SHALL 与该 commit 的符号、参数和调用路径一致；无法保证可运行时 SHALL 明确标为示意

### Requirement: 导航、版本边界与变更历史一致

系统 SHALL 使新增内容可从 bundle 导航到达，并清楚表达旧、新快照的范围。

#### Scenario: 浏览增量后的 bundle

- **WHEN** 读者通过根 index 或子目录 index 浏览 bundle
- **THEN** 根及受影响的 `concepts/`、`examples/`、`references/`、`spec/` 索引 SHALL 同时提供人类可读导航和完整 `{toctree}` 条目
- **AND** `log.md` SHALL 追加本轮日期、源码坐标、新增/修订文件和事实基线说明，不改写历史记录
- **AND** 根 index 的描述及版本元数据 SHALL 与实际覆盖范围和本轮来源相符

### Requirement: 对产物执行独立内容与结构验证

系统 SHALL 在交付前验证事实真实性、导航完整性、元数据和数量口径。

#### Scenario: 完成 V 阶段

- **WHEN** 本轮 bundle 内容定稿
- **THEN** 文档引用的关键类、函数、方法、命令和配置项 SHALL 对照固定 commit 的源码逐项验证
- **AND** 数量陈述 SHALL 由不同于首次采集的方法复核
- **AND** 所有新增文档的 frontmatter、sources、bundle 内链接、索引条目及 toctree SHALL 通过检查
- **AND** awesome-okf-xs 的相关质量门与文档构建 SHALL 运行并记录结果；既有无关失败 SHALL 单独归因，不得顺手修改其他资产

## Non-Functional Requirements

- **NFR-1 可追溯性**：新事实可定位到固定 commit 的仓库相对路径；禁止将本机绝对路径作为长期信源。
- **NFR-2 版本清晰度**：旧版 F-001～F-080 与本轮新增事实不得混淆；任何旧文档修订必须记录理由和证据。
- **NFR-3 OKF 合规**：遵循 awesome-okf-xs 当前 frontmatter 规则；根及子目录导航满足 Sphinx/toctree 门禁。
- **NFR-4 中文可读性**：正文中文，关键英文术语首次出现时解释；组织为从架构总览到机制深读的递进路径。
- **NFR-5 事实精度**：不得凭训练语料补全 OpenCode API 或行为；不确定内容必须回查源码或明确标为未确认。
- **NFR-6 增量安全**：变更限定在目标 bundle 内，不覆盖工作区已有的无关变更。

## Constraints

- **Technical**：源码仓库 `external/dao/anomalyco/opencode`；固定 commit `6ec56821d63100fe5bda45b759364f561c56b359`；根包版本 `2.0.32`（实施时复核）。
- **Destination**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/opencode/`。
- **Source links**：使用 `https://github.com/anomalyco/opencode/blob/6ec56821d63100fe5bda45b759364f561c56b359/...` 等固定 commit 链接，不引用 `dev`、`main`、本机 `file:///` 或环境相关绝对路径。
- **Workflow**：阶段 0 信源预检 → R 事实 → I 洞察/知识地图 → E 信源先行并分批生成（每批不超过 7 个文件，索引最后更新）→ V 独立复核 → C 模式适用性评估。
- **Repository boundary**：`awesome-okf-xs` 是自治 git submodule；本次只在授权目标 bundle 内工作，不触碰其余索引或文件，除非验证证明目标 bundle 的父级导航缺少入口。

## Assumptions

- 指定本地 checkout 的 remote 对应 `https://github.com/anomalyco/opencode`，且固定 commit 在该仓库可访问。
- 当前事实清单最大编号仍为 F-080；实施前必须重新核实，若工作区事实已变化，则从实际最大编号之后续接。
- `2.0.32` 是根 `package.json` 对该 commit 声明的包版本；标签与 commit 的对应关系不预设，统一以 commit hash 为权威坐标。
- 教程覆盖以当前 monorepo 的实际工作区和主要子系统为准；分层采样不等于逐文件逐行穷尽。

## Acceptance Criteria

### AC-1: 目标与增量边界
- **Type**: `rule`
- **Given**: OpenCode bundle 已存在
- **When**: 本轮交付完成
- **Then**: 所有本轮知识均位于既有 `jishu/ai/frameworks/ai-agent/opencode/` 中，未创建重复 bundle、未改变源码仓库；除用户已接受的既有并行聚合提交及其父仓库指针提交外，本任务不执行新的 Git 提交或推送
- **Pass Condition**: Git 状态、变更文件清单和 bundle 目录能证明增量边界；已存在的两个例外提交仅作为既成事实记录，且未发生新增提交、推送或历史改写
- **Evidence**: 两个仓库的 `git status`、本轮 diff、bundle 文件清单、例外提交 SHA 与用户明确接受记录

### AC-2: 固定信源与事实分层
- **Type**: `rule`
- **Given**: 新增的参考、事实和概念文档
- **When**: 对照指定源码快照检查
- **Then**: 每条新增事实带 F-081 或更高且不冲突的编号、路径和固定 commit 来源；旧事实及历史记录未被静默重排或覆盖
- **Pass Condition**: 事实编号无重复，API/路径可在目标 commit 核验，数量断言有统计口径及独立复核证据
- **Evidence**: 版本化 facts、reference 文档、源码检索记录及 V 阶段计数复核

### AC-3: monorepo 覆盖度
- **Type**: `rubric`
- **Dimension**: 工作区与核心架构覆盖度
- **Scale**: 0-3
- **Anchors**: 0 = 只描述单一包或旧版内容；1 = 有包清单但无关键调用路径；2 = 包清单、核心子系统职责和至少一条端到端路径齐全；3 = 达到 2，且对重要接口边界、版本差异和未覆盖区域均有证据化说明
- **Pass Threshold**: >= 2
- **Evidence**: facts、insights、知识地图和新增教程与源码树的覆盖矩阵

### AC-4: OKF 文档与导航完整
- **Type**: `rule`
- **Given**: bundle 中本轮新增或修改的文档
- **When**: 执行元数据、链接和 Sphinx/toctree 检查
- **Then**: 新增概念、示例和参考文档均有合规 frontmatter 与固定来源；受影响索引包含全部文档且有 `{toctree}`；内部链接全部可达
- **Pass Condition**: 新增文档和受影响索引的结构检查零遗漏、零断链
- **Evidence**: 元数据/链接/toctree 检查结果及定向文档构建

### AC-5: 学习路径与事实表达质量
- **Type**: `rubric`
- **Dimension**: 教程连贯性与读者可用性
- **Scale**: 0-3
- **Anchors**: 0 = 零散摘要且无法循路径学习；1 = 有章节但边界或前后依赖不清；2 = 从全景到机制有明确顺序，每篇有独立主题并能回链到事实；3 = 达到 2，且示例、反常识洞察和局限说明能帮助读者验证并迁移理解
- **Pass Threshold**: >= 2
- **Evidence**: bundle 导航、概念文档交叉引用及独立 Review 记录

### AC-6: 验证闭环
- **Type**: `rule`
- **Given**: 新增 bundle 内容完成
- **When**: 执行 V 阶段与 Spec Mode 独立 Review
- **Then**: 关键 API 与数量陈述完成核验，受影响质量门及构建结果有记录，所有可行动发现已修复或明确阻塞，最终独立 Review 为 `pass`
- **Pass Condition**: `review.md` 覆盖全部 AC，所有规则项有证据，两项 rubric 均达到阈值，且无未解决可行动发现
- **Evidence**: V 阶段验证记录、质量门输出和 `review.md`

## Open Questions

- [ ] 本轮知识地图应如何划分新增概念篇数？默认由 R/I 阶段覆盖矩阵决定，不预设固定篇数，以每篇单一职责、每批不超过 7 个文件为约束。
- [ ] C 阶段是否产生值得进入 SpecWeave 方法论库的新模式？默认仅记录评估结论；如需新增主权区资产，另走提案与批准流程。
