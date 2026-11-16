---
title: "TRAE 2026-11-15 周报 → OKF Wiki 教程（Spec）"
source: "https://mp.weixin.qq.com/s/LxoUITnmaiH3CzI4AAz0iA"
date: "2026-11-16"
tags: ["okf-wiki", "trae", "blog-conversion", "deep-research"]
---

# Spec：TRAE 2026-11-15 周报 → OKF Wiki 教程

> 方法论编排：`seven-concepts-cmd`（场景 4 知识沉淀，链路 R→I→E→V→C，depth=deep）；领域工作流：`blog-article-to-okf-wiki`（七阶段）。
> CMD-LOG session：`sc-20261116-trae-weekly-update-okf-wiki`。

## 1. 内容敏感度预检（步骤 2.3）

| 检查项 | 判定 |
|--------|------|
| URL 含 `share?code=`／`token=`／邀请码？ | 否 |
| 企业内部域名？ | 否（`mp.weixin.qq.com` 为公开内容平台） |
| 需登录态访问？ | 否（WebFetch 直接返回完整正文） |
| 用户标注私域／内部／保密？ | 否 |
| 内容主题为内部会议／商业培训／个人笔记？ | 否（厂商公开发布的产品周报） |
| **结论** | **公开内容（Public）** → 标准工作流：spec 在 `.trae/specs/okf-wiki-ecosystem/`，不跳过规划区 |

**route 决策**：源材料为网页文本层（非扫描版、无文本层缺失），不属于「扫描版版权材料」附加条款适用范围；采用**深度摘要 + 原创改写**（`chaptered-summary` 语义），事实以 F 编号登记、观点标「官方表述」，不作逐字全文转录。

## 2. 落盘前三查

| 查项 | 结论 |
|------|------|
| 目标目录是否在根 `docs/` 下？ | **否**，落在 `projects/awesome-okf-xs/doc/bundles/…` |
| 同类产出物现有位置？ | 13 篇博文转化先例全部位于该子模块 `doc/bundles/`（如 `trae/bytedance-ai-consolidation`、`trae/threeui`、`trae/trae-one-click-deploy`、`agora-gemini-transcribe`）；分组 toctree 与全库计数体系均在子模块内 |
| 路径规则是否来自磁盘原文？ | 是——`AGENTS.md` 磁盘原文启动协议、`.agents/rules/content-sensitivity-precheck.md`、`.agents/skills/blog-article-to-okf-wiki/SKILL.md` 步骤 1 均明确「产出在 `projects/awesome-okf-xs/doc/bundles/`」 |

> **规范张力说明**：`AGENTS.md`「文档边界」条款声明根 `docs/` 为唯一文档中心，同时其「知识库与复盘」表把 `projects/awesome-okf-xs/doc/bundles/` 列为最高可信度 OKF 知识包库；`blog-article-to-okf-wiki` SKILL 与 13 篇先例一致把产出定为子模块。判定：根 `docs/` 条款约束**主仓库新增文档**，OKF bundle 属 **git submodule 自治文档中心**（有独立 Sphinx/toctree/计数体系），跨域写入会破坏导航与计数一致性。故按领域先例落子模块，spec 留主仓。此判定记录在此供审计。

## 3. 骨架判定（操作可复现性两问）

| 问 | 结论 | 依据 |
|----|------|------|
| ① 博文中是否有读者可照做的安装／配置／代码／调用／实测流程？ | **弱是** | 有「升级桌面端→插件市场」「私信后台报名」「11.10–11.23 提交作品」等入口指引，但均为活动／功能入口，非技术操作流程（F-033） |
| ② 是否经作者实测、具备可复现性（有版本／输入输出／步骤顺序）？ | **否** | 无客户端版本号、无输入输出示例、无实测数据、无构建日志（F-032、F-033） |
| **结论** | **不设 `examples/`** | 任一为否即不设；空 examples/ 制造伪结构。与同分组 `trae-one-click-deploy`、`threeui`、`a2a-mcp` 先例一致 |

**内容性质**：资讯速报／资讯盘点（厂商周报，四板块并列，单板块仅数句，无方法论、无源码、无可演练决策工具）。
**目录骨架**：`index + concepts/(4 篇) + references/(2 篇) + log`，**无 examples/**；`description` 标注「非操作教程」；`stale_after` 缩短至 1.5 个月（2026-12-31，赛事 12-06 结束）。

## 4. 归属判定决策树

1. **主线实体优先**：文章四项更新全部围绕 TRAE 产品与 TRAE 创作者生态 → 锚点为 `trae`。
2. **查先例**：目标分组 `jishu/ai/ecosystems/trae/` 已存在，且已有 4 个非源码类 bundle（`bytedance-ai-consolidation`、`threeui`、`tushare-ai-office`、`trae-one-click-deploy`），证明可容纳博文转化产物；其中 `trae-one-click-deploy` 与本篇板块一直接同主题，可交叉引用。
3. **单篇博文禁止新建分组** → 不新建顶级分组。
4. **板块**：归入「📰 战略资讯」（该分组既有分类，语义匹配厂商公告／资讯解读）。

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/ecosystems/trae/trae-weekly-update-20261115/`（选定） | ✅ | 主线实体 TRAE；分组已有 4 个资讯类先例；有同主题 bundle 可互链；不新建分组 |
| 并入既有 `trae-one-click-deploy/` | ❌ | 该束是 11-12 单篇公告解读，其 F 编号体系、核验结论、status 均已固化；本篇为 11-15 周报且含另外三个板块，合并会污染单篇信源边界 |
| `jishu/ai/products/` | ❌ | 该分类为产品工具源码／能力教程，非厂商周报资讯 |
| 新建 `trae-weekly/` 分组 | ❌ | 单篇博文新建分组属过度工程 |

## 5. 三层知识拆分（I 阶段知识地图）

| 层 | 篇目 | 回答的问题 |
|----|------|-----------|
| 事件时间线层（What／When／Who） | `concepts/00-weekly-overview.md` | 本周发了什么、四项各处于什么时间线、信源距离与时效边界 |
| 机制原理层（Why／How） | `concepts/01-product-capabilities.md` | 一键部署与画中画各自解决什么问题、官方日志如何精确化、与既有 bundle 的关系 |
| 生态／格局层 | `concepts/02-creator-ecosystem.md` | 大赏赛与创作者计划的完整规则、两个官方渠道口径差异、作品硬要求 |
| 方法论层（可迁移，E 阶段萃取） | `concepts/03-verification-tutorial.md` | 如何把一份厂商周报转成可溯源知识：信源距离→P0→勘误四清单→时效边界→门禁 |
| 信源层 | `references/article-source.md`、`references/verification.md` | F-001~F-051 双份登记、15 项 P0 核验与勘误四张清单 |

**教程定位**：用户要求「生成 okf wiki 教程」。OKF bundle 即系统化中文教程形态；其中 `03-verification-tutorial.md` 是可独立 follow 的实操教程（五步核验法），使本包不止于资讯存档，而具备方法论复用价值。

## 6. ADDED Requirements（验收口径）

- **R1**：所有具体声明带 F 编号；不得出现 facts.md 之外的数字、日期、金额。
- **R2**：信源先行——references/ 先于 concepts/，各级 index.md 最后写。
- **R3**：frontmatter 遵循 OKF v0.2（本项目既有先例的 `generated`／`verified` 为标量写法，按格式证据优先于模板记忆执行）；`sources` 同时含博文 URL 与核验权威 URL。
- **R4**：`status: draft`（单源密集 + 3 处渠道口径差异 + 活动时效）；`stale_after: 2026-12-31`。
- **R5**：不设 `examples/`，index 顶部显著声明「非操作教程」。
- **R6**：同主题多 bundle 互链——index 增加「主题关联」段，与 `trae-one-click-deploy` 等两两互链并说明分工。
- **R7**：三级 toctree + 全库计数同步（先读现值再 +1，不凭记忆写数字）。
- **R8**：双份 F 编号集合一致且连续；相对链接逐一可达；UTF-8 strict roundtrip。
- **R9**：勘误落实——verification.md 的 ⚠️ 项在正文呈现的是精确化后的值（非源文模糊口径）。
- **R10**：C 阶段原子提交（子模块→主仓库），显式文件列表，不 push；主仓存在他方 WIP，须隔离暂存，不代改。
- **R11**（V 阶段审查追加）：显式声明**信源独立性边界**——同厂商多渠道不等于独立验证；P0 的 ✅ 语义限定为「官方渠道间口径一致」，并在核验报告前置判据、根 index、教程三处同步。
- **R12**（V 阶段审查追加）：渠道差异集中登记为 `CD-xxx` **单一真源台账**（状态／工作口径／复核触发条件），概念文档只引用编号；状态「未澄清」的项不得写成「已判定」，并须在 `stale_after` 前回查。
- **R11**（V 阶段审查追加）：显式声明**信源独立性边界**——同厂商多渠道不等于独立验证；P0 的 ✅ 语义限定为「官方渠道间口径一致」，并在核验报告前置判据、根 index、教程三处同步。
- **R12**（V 阶段审查追加）：渠道差异集中登记为 `CD-xxx` **单一真源台账**（状态／工作口径／复核触发条件），概念文档只引用编号；状态「未澄清」的项不得写成「已判定」，并须在 `stale_after` 前回查。

## 7. 已知边界

1. 无客户端版本号，能力可能随版本变化（F-036）。
2. 一键部署限免起止时间、结束后计费规则未给出。
3. 报名起始日两个官方渠道差 1 天（11.9 / 11.10），未见官方澄清 → 登记为 CD-001（状态「未澄清」），暂取 11.10 为工作口径，待官方澄清后复核。
4. 创作者计划「100 位」是否仍开放、首批截止时间未给出。
5. 画中画 Windows 版开放进度未给出。
6. 赛事奖项金额图片 OCR 顺序存在歧义（F-045）。
7. 本包不改写既有 `trae-one-click-deploy` 的核验结论，仅登记「须复核」。
