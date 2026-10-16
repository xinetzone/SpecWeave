# 企业微信 5.0.12 发布页 → OKF Wiki 知识包 - 需求文档

## Overview

- **Summary**：按七概念知识沉淀链路（R→I→E→V）+ `blog-article-to-okf-wiki` 七阶段工作流，把企业微信官方公开页《5.0.12 版本新功能介绍》转化为一个 OKF v0.2 知识包（bundle），落位于 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/` 既有分组，与上一会话产出的 `wecom-5-0-10-release` 束并列并双向互链。
- **Purpose**：5.0.12 是 5.0.10（CLI/MCP 开放）之后的下一公开发布版本（2026-10-14 官宣），主线转为「企微 × WorkBuddy 深度互通」并新增频道、知识库、对外管理等协作/治理模块；需要一份可溯源、带时效管理、口径分层的版本快照，供后续读者区分官方事实、媒体转述与单源声明。
- **Target Users**：OKF 知识库读者——关注腾讯办公生态/AI Agent 开放能力的技术与产品人员、知识库机器审核（Sphinx toctree BFS + 机械门禁）。

## Goals

- 完整登记 5.0.12 发布页的全部功能声明（F-001～F-035），并对日期、版本号、规模数字、能力口径做 P0 权威核验（F-036～F-051）。
- 按「事实—机制/产品—治理」三层产出 4 篇 concepts：版本总览、WorkBuddy 互通与 AI 协作体系、频道/知识库/应用内协作、企业安全与对外管理。
- 不设 `examples/`（操作可复现性两问皆否：发布页无经实测的安装配置链路）。
- 接入 tencent 分组到 bundles 总索引的三级导航与计数，并与 `wecom-5-0-10-release` 束双向互链（5.0.10 束需回补「主题关联」指向 5.0.12 束）。
- 口径分层硬要求：①WorkBuddy 5.8.0/十大能力为通稿同源口径，官方 changelog 止于 5.7.7；②幻灯片 CLI/MCP 在发布页宣布但官方 AI 能力页仍为 11 模块；③AI 分析报告灰度标注跨版消失但官方未宣布 GA；④授权能力清单三处不一（网盘/日程微盘/邮件）。一律不得抹平。

## Non-Goals

- 不修改/提交 5.0.10 束正文事实（仅允许在其 index.md「主题关联/已知边界」处补一条指向 5.0.12 的互链；不重写其内容、不改其计数归属）。
- 不修复与本任务无关的并行在途工作（hwe-bench、kylin-wayland-compositor 等未跟踪束、iot/systems 索引改动、deepseek-harness 历史口径漂移）；只在本束 log.md 披露观测结果。
- 不做 git commit/push（用户未要求；提交待用户显式指令，顺序与工具按 `blog-article-to-okf-wiki` C 阶段执行）。
- 不抓取/转述隐私保护指引等 O10 三个规则页的细则正文，只登记链接与更新事实。
- 不新建分组、不新建顶级类目。

## Background & Context

- 上一会话已交付 `wecom-5-0-10-release` 束（9 文件，33 条事实，R1 pass，**至今未提交**），格式为本任务直接基准：OKF v0.2 frontmatter、无 examples、references 双件（article-source.md + verification.md）、根 index「内容性质/可信度状态/已知边界/主题关联/一句话结论」结构。
- 子模块 `projects/awesome-okf-xs` 当前工作树：5.0.10 束未跟踪 + 五个上游索引已改；另有并行会话的 hwe-bench、kylin-wayland-compositor 未跟踪束及 iot/systems 索引改动。计数必须以机械真值（目录树 + 门禁脚本）为准，只同步受本任务影响的面。
- R 阶段已完成（见同目录 `facts.md`，51 条事实）：发布页 WebFetch 成功；P0 核验经独立子代理 + 直接抓取完成，最硬独立信源为上证报操子怡稿（cnstock 802000，2026-10-14 13:23）；官方 AI 能力页 O6 核验时仍 11 模块；path/101906 路径可达但正文 JS 渲染未取得标题。

## Functional Requirements

- **FR-1**：新建 bundle `wecom-5-0-12-release/`，含根 index.md、log.md、concepts/（index + 4 篇）、references/（index + article-source.md + verification.md），共 10 个文件。
- **FR-2**：article-source.md 双份登记 F-001～F-051，编号集合与 spec `facts.md` 相等、连续无跳号；每条含声明摘要、来源代号、核验状态。
- **FR-3**：verification.md 给出 P0 核验总表（日期/版本、5.8.0 口径、幻灯片口径、灰度演进、规模数字、单源清单）、勘误四张清单落实、信源距离与厂商叙事评估、V 四视角对抗审查表、状态裁决（预期 stable，⚠️ 单源条目充分标注）。
- **FR-4**：4 篇 concepts 所有具体声明（数字、版本号、功能名、日期）均带 F 编号引用；单源/转述/灰度/前瞻四类措辞显式标注；含至少 1 张 Mermaid 图（版本线/协作架构）。
- **FR-5**：三级索引接入——tencent/index.md（导航表行 + toctree + 计数 12→13 束、概念 93→97、信源 52→54、事实 1555→1606）、ecosystems/index.md（腾讯行 12→13 及总计数）、jishu/ai/index.md、jishu/index.md、doc/bundles/index.md（total_bundles 632→633 等）；实际数字以实施时机械真值复算。
- **FR-6**：双向互链——新束 index「主题关联」链 5.0.10 束等 4 个同分组束；5.0.10 束 index.md 回补一条 5.0.12 链接。
- **FR-7**：log.md 记录七阶段执行、口径决策、并行在途观测、门禁运行方式（直接运行底层脚本，`invoke gates.*` 若不可用不谎报）。

## Non-Functional Requirements

- **NFR-1（规范一致）**：全部文件遵循 OKF v0.2 frontmatter（根文件带 `okf_version: "0.2"`，子文档 type=Concept/Reference；generated/verified 标识为 process:seven-concepts-*；status/stale_after/sources 齐备），中文正文，kebab-case 英文文件名。
- **NFR-2（机械质量）**：UTF-8 严格 roundtrip 无乱码；相对链接全部可达；零 `file:///`、零家目录绝对路径；每个 index.md 含 toctree 块且条目逐一存在；敏感信息零残留。
- **NFR-3（时效管理）**：stale_after 按版本资讯设为 2027-01-31（与 5.0.10 束对齐）；灰度/单源/前瞻项在「已知边界」集中声明。
- **NFR-4（可审计）**：核验信源全部为实际访问成功的 URL，禁止编造；无法核验项标「仅官方单源/未取得」，不升级可信度。

## Constraints

- **Technical**：产出在 git submodule `projects/awesome-okf-xs/`（只读引用区，但已有同分组先例，允许按子模块工作流落盘文档，不提交）；Windows + PowerShell 7 + Python py314；门禁脚本在子模块根目录直接 `python scripts/<name>.py` 运行。
- **Business**：遵循 AGENTS.md 启动协议与文档边界（公开内容标准工作流；spec 在主仓 `.trae/specs/okf-wiki-ecosystem/`）；用户沟通中文、动作导向。
- **Dependencies**：发布页可访问性（已验证 WebFetch 成功）；外部信源时效性（2026-10-14 核验快照）；门禁脚本 check-bundles-index.py / check-utf8.py / check-toctrees.py。

## Assumptions

- 归属 `jishu/ai/ecosystems/tencent/` 无争议：主线实体为企业微信（腾讯），同分组已有同型版本资讯束先例，不单新建分组。
- 5.0.12 发布页结构与 5.0.10 同型（官方活动页），骨架按「技术综述/版本发布资讯：index + concepts + references + log，无 examples」。
- 核验时点 2026-10-14 的页面状态即本束快照基准；10-15 直播后可能出现的新信息不在本束范围（stale_after 到期复核）。

## Acceptance Criteria

### AC-1: Bundle 结构与规范完整
- **Type**: `rule`
- **Given**: bundle 目录 `jishu/ai/ecosystems/tencent/wecom-5-0-12-release/`
- **When**: 实施完成
- **Then**: 10 个文件全部存在（index.md、log.md、concepts/index.md + 00～03 四篇、references/index.md + article-source.md + verification.md），无 examples/ 目录；每个 index.md 含 toctree 块且条目逐一 Test-Path 存在；根 index.md frontmatter 含 okf_version "0.2" 且 sources 含 W+O1～O10 中实际引用者
- **Pass Condition**: 文件清单、toctree 条目、frontmatter 必填字段逐项核对全部通过
- **Evidence**: 目录列表 + toctree/frontmatter 机械核对结果

### AC-2: 双份 F 编号一致且核验真实
- **Type**: `rule`
- **Given**: spec `facts.md` 与 bundle `references/article-source.md`
- **When**: V 阶段用正则提取两文件 `F-\d{3}` 编号集合
- **Then**: 两集合相等 = {F-001…F-051}，连续无跳号；每条外部 URL 来自 R 阶段实际访问记录；四类口径（5.8.0 vs 5.7.7、幻灯片前瞻、灰度标注消失、三处能力清单）在 verification.md 与 concepts 正文中均有呈现
- **Pass Condition**: 集合比对零差异；口径项 4/4 在正文落地
- **Evidence**: 正则集合比对输出 + verification.md 勘误节

### AC-3: 三级索引与计数同步
- **Type**: `rule`
- **Given**: tencent/index.md、ecosystems/index.md、jishu/ai/index.md、jishu/index.md、bundles/index.md
- **When**: 运行 `python scripts/check-bundles-index.py`
- **Then**: 门禁通过（五面计数一致）；新束在 tencent 分组导航表与 toctree 均出现；与本束相关的 toctree 断链过滤复检零命中
- **Pass Condition**: 门禁脚本退出码 0 且输出含本束的计数面一致；check-toctrees 过滤 `wecom-5-0-12` 零命中
- **Evidence**: 脚本输出（在无并行写入窗口复跑锁定）

### AC-4: 链接与编码机械门禁
- **Type**: `rule`
- **Given**: 全部新增/修改的 .md 文件
- **When**: V 阶段执行
- **Then**: check-utf8.py 通过；全部 Markdown 相对链接可达；零 `file:///`、零 `C:\Users` 等家目录路径；双向互链成立（新束→5.0.10 与 5.0.10 index→新束各至少 1 条）
- **Pass Condition**: 各项检查零命中违规
- **Evidence**: 门禁脚本输出 + Grep/Test-Path 核对记录

### AC-5: 内容可信度与读者可用性
- **Type**: `rubric`
- **Dimension**: 口径分层与读者决策可用性
- **Scale**: 1-5
- **Anchors**: 1 = 单源/通稿/前瞻/灰度信息与已证事实混写，读者无法判断可信度；3 = 主要声明有出处但口径分层不统一、个别数字无 F 编号；5 = 每条数字/版本/功能声明可回溯 F 编号，单源/媒体转述/通稿同源/官方前瞻/灰度五类标签全文一致，「已知边界」可直接支持读者的使用与等待决策
- **Pass Threshold**: >= 4
- **Evidence**: 四篇 concepts + index「已知边界」；独立评审逐篇抽查

### AC-6: 知识三层结构质量
- **Type**: `rubric`
- **Dimension**: 三层拆分（事实→机制/产品→治理）与导航体验
- **Scale**: 1-5
- **Anchors**: 1 = 按发布页顺序平铺翻译，无分层与互链；3 = 有分层但层间重复或跨层跳转不清；5 = 总览回答「何时/什么/时效位置」，机制篇回答「怎么打通/边界」，产品篇回答「能用什么」，治理篇回答「企业怎么管」，篇间阅读路径明确、Mermaid 图有 F 依据
- **Pass Threshold**: >= 4
- **Evidence**: 4 篇 concepts 结构与独立评审评分

## Open Questions

- 无阻断性开放问题。以下为实施时按既有裁决执行、无需用户确认的事项：①不提交 git；②计数以机械真值为准、并行漂移只披露不修复；③stale_after=2027-01-31；④status 目标 stable（若 V 阶段发现核心声明证伪则转 flagged）。
