---
status: "draft"
id: "vista-visual-harness-blog-okf-wiki-spec"
title: "VISTA 视觉 Harness 博文 → OKF 知识包"
source: "微信公众号「量子位 QbitAI」《何恺明团队发布多模态Harness框架》(2026-10-09)；权威源 arXiv:2610.02200"
date: "2026-10-20"
methodology: "seven-concepts knowledge scenario: R-I-E-V-C"
content-sensitivity: "public"
tags: ["VISTA", "视觉Harness", "多模态", "ARC-AGI-3", "Agent记忆", "OKF Wiki"]
---

# VISTA 视觉 Harness 博文 → OKF 知识包

## 内容敏感度预检

- URL：`https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ`（量子位公众号公开文章，无 `code=`/`token=`/邀请码等访问控制参数）
- 判定：**公开内容（Public）** → 标准工作流
- Spec 目录：`.trae/specs/okf-wiki-ecosystem/vista-visual-harness-blog-okf-wiki/`
- 产出物：`projects/awesome-okf-xs/doc/bundles/jishu/ai/models/vista-visual-harness/`

## Overview

- **Summary**：将量子位《何恺明团队发布多模态Harness框架》转化为可溯源的 OKF v0.2 中文知识包，核心是 MIT 团队 VISTA 视觉原生 Harness 的设计机制、ARC-AGI-3/GameWorld/AI GameStore/BabyVision 四基准证据，以及博文相对论文的口径差异。
- **Purpose**：给需要理解"多模态 Agent 如何保存并复用视觉经验"、以及要评估"ARC-AGI-3 满分 100"这一结论的可信度的读者，提供一条从博文到论文原文再到官方基准的可复核路径。
- **Target Users**：AI Agent/多模态方向工程师与研究者、关注 Harness/上下文工程范式的读者、需要评估交互式基准成绩解读方式的读者。

## Goals

- 在 `jishu/ai/models/` 创建独立 bundle `vista-visual-harness`，与同组 `minit2i`（同为何恺明团队研究工作）、`agent-lightning`（同为 harness 范式 + 微信博文转化）互为同主题参照。
- 按 R→I→E→V 完成信源登记、F 编号事实采集、P0 权威核验、三层知识拆分、bundle 生成与独立核验。
- 保留 C 阶段交付核对；不在未获明确提交请求时创建 Git commit。
- 同步更新 `jishu/ai/models/index.md`、`jishu/ai/index.md`、`jishu/index.md` 与 `doc/bundles/index.md`，使新 bundle 可由文档根导航抵达。

## Non-Goals

- 不复现 ARC-AGI-3 私有/半私有游戏环境（不在任何公开仓库中，需 API key 授权）。
- 不训练、不微调任何模型；不实现 VISTA 的 Harness 代码（仅在开源事实范围内引用）。
- 不把 ARC-AGI-3 满分 100 表述为"通用多模态模型已达到人类水平"的普适结论——论文 §6 明确其泛化边界。
- 不新建顶级技术域或分组；不改动同组其他 bundle 的既有内容。
- 不创建 Git commit，除非用户另行明确要求。

## Background & Context

- **信源**：量子位（QbitAI，公众号别名 `QbitAI`）《何恺明团队发布多模态Harness框架》，作者 henry（发自 凹非寺），发布 2026-10-09 10:41（北京时间），页面 `var ct = "1791513671"`。
- **权威源**：arXiv:2610.02200《VISTA: A Visual Harness for Reasoning in an Interactive World》（2026-10-01 提交，MIT，CC BY 4.0）；项目页 `vista-research.github.io`（2026-08-05 blogpost 版本）；代码 `github.com/joshhhhhan/VISTA`（MIT License）；ARC Prize 官方方法学 `docs.arcprize.org/methodology`。
- **归属依据**：`jishu/ai/models/` 定位"基础模型能力与多模态"，已承载同源先例 `minit2i`（何恺明团队研究工作）与 `agent-lightning`（harness 范式、微信博文转化非操作教程）。VISTA 既是模型能力工作又是 harness 范式工作，落在该组最贴合读者查找路径。
- **执行约束**：awesome-okf-xs 是 git 子模块；工作树当前含 `doc/bundles/jishu/iac/sst/` 两处并行 WIP 修改，本任务不得触碰。共享索引 `doc/bundles/index.md` 与 `jishu/ai/index.md` 需重读最新内容后再做追加与计数更正。

## Functional Requirements

- **FR-1：信源登记**：建立 `references/` 记录博文账号、URL、发布时点、访问时点、可见性边界与停止规则，并登记论文/项目页/代码/ARC 官方方法学等权威源。
- **FR-2：事实与核验**：以连续 F 编号登记博文事实与核验补充事实；P0 声明逐项对照权威源，差异单列勘误而非静默照搬。
- **FR-3：三层知识拆分**：分离事实层（发布/机制/实验事实）、机制层（作者洞察，标注假设）、迁移层（中立可逆实践）。
- **FR-4：骨架判定**：以"操作可复现性两问"决定是否设 `examples/`；结论须在 spec 与 bundle 索引中留痕。
- **FR-5：OKF 结构与元数据**：按 OKF v0.2 创建 bundle 根索引、`log.md`、`concepts/`、`references/`；非保留 Markdown 含可解析 YAML frontmatter 与 `sources`；各级索引含隐藏 `{toctree}`。
- **FR-6：导航登记**：挂入 `jishu/ai/models/index.md` 及必要的上级导航与总索引；按官方 gate 口径更新计数，不凭记忆写数字。
- **FR-7：门禁与独立核验**：运行 `invoke gates.toctrees` / `gates.bundles` / `gates.utf8`；对 F 编号双份一致性、相对链接可达、勘误落实做机械检查。

## Non-Functional Requirements

- **NFR-1**：事实、作者观点、执行者洞察三层分离；作者观点不固化为研究结论。
- **NFR-2**：具体声明（数字/模型名/组件名/工具名）全部挂 F 编号，无 F 之外的新增断言。
- **NFR-3**：中文撰写，英文术语首次出现时解释；文件名 kebab-case。
- **NFR-4**：bundle 内链接使用 bundle-relative `/` 路径；父级链接遵循项目现有导航格式。
- **NFR-5**：时效性显式声明——`stale_after` 前复核基准排名、模型版本与代码仓库状态。
- **NFR-6**：敏感信息零残留；不写入本机绝对路径或临时目录路径。

## Constraints

- **Technical**：以 arXiv 论文（2026-10-01 v1）为一手事实基准；项目页 2026-08 数字仅作差异对照，不混入正文结论。
- **Repository**：子模块工作树含 `jishu/iac/sst` 并行 WIP，本任务只写 `jishu/ai/models/vista-visual-harness/` 及其索引行。
- **Documentation**：遵循 `projects/awesome-okf-xs/.agents/rules/frontmatter.md` 与该子项目 toctree/bundle gates。
- **Workflow**：spec 三件套（spec.md + tasks.md + review.md）在批准后创建；未批准前只写 spec 文件。

## Acceptance Criteria

### AC-1：Bundle 归属与结构
- **Type**：`rule`
- **Given**：实施范围已获批准
- **When**：检查目标文档目录
- **Then**：独立 bundle 位于 `jishu/ai/models/vista-visual-harness/`，含根 `index.md`、`log.md`、`concepts/`、`references/`；不改动同组其他 bundle 内容。
- **Pass Condition**：目录结构存在且各级索引遵守项目规范。
- **Evidence**：文件清单、`git diff --stat`。

### AC-2：信源与事实可追溯
- **Type**：`rule`
- **Given**：Bundle 文档引用博文或论文
- **When**：核验 references 与 frontmatter
- **Then**：博文账号、URL、发布时点、访问时点可复核；论文/项目页/代码/ARC 方法学各自标注角色；无浮动来源作为唯一依据。
- **Pass Condition**：所有内容文档 `sources` 指向已存在 references。
- **Evidence**：references 文件、frontmatter 扫描。

### AC-3：机制与实验事实覆盖
- **Type**：`rule`
- **Given**：论文全文可读
- **When**：审查 facts 与 concepts
- **Then**：三组件、无损视觉记忆、inspect/read_pixels 工具、GUIDE.md/WORKING.md 双笔记、上下文交接、四个基准结果、消融阶梯、多次运行方差、局限与未来方向均有证据驱动的说明。
- **Pass Condition**：每个覆盖项至少关联一条编号事实。
- **Evidence**：facts 清单、知识地图、逐项核验记录。

### AC-4：口径差异如实呈现
- **Type**：`rule`
- **Given**：博文与论文存在差异
- **When**：审查正文与勘误章节
- **Then**：E-1~E-8 全部在正文与 `references/verification.md` 中落实：术语按论文原词、Anthropic 脉络归因加边界、论文 §6 局限置于显著位置、方差与基线补入、39 题范围精确化、开源资产补入、项目页差异标注来源。
- **Pass Condition**：勘误无静默照搬，正文呈现的是正确值与限定条件。
- **Evidence**：勘误章节、verification 报告、正文对应段落。

### AC-5：OKF 元数据与导航合规
- **Type**：`rule`
- **Given**：所有 bundle 内容文档已生成
- **When**：运行项目质量门
- **Then**：frontmatter、sources、目录索引、bundle-relative 链接、父级导航与总索引均符合 OKF v0.2 与子项目规范。
- **Pass Condition**：`invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8` 对本次变更通过。
- **Evidence**：质量门命令输出。

### AC-6：知识分层与可学习性
- **Type**：`rubric`
- **Dimension**：全面性、准确性、可学习性与口径表达
- **Scale**：1-5
- **Anchors**：1 = 主题零散且关键机制/信源缺失；3 = 核心机制有覆盖但口径边界仍有明显空缺；5 = 机制/实验/局限/边界均有事实支撑，学习顺序连贯，差异表述清楚
- **Pass Threshold**：>= 4
- **Evidence**：独立 Review 对照 FR-1~FR-7 与事实映射评分。

## Open Questions

- 无阻断性待决问题。若批准时要调整"全面学习"范围或目标分类，实施前更新本规格与任务队列。
