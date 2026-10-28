---
okf_version: "0.2"
type: spec
title: "智谱清言 AgentMore × 清华 OpenMAIC「专属 AI 老师」博文→OKF 知识包转化规划"
description: "将智谱清言 AgentMore 官方公告《清言 × 清华 OpenMAIC，打造你的专属AI老师》转化为 OKF 知识包，覆盖 AgentMore 学习搭子两项新技能（费曼学习、习题带练）的三轮交互机制、8 个 OpenMAIC Skill 上新清单，以及清华 THU-MAIC 开源项目 OpenMAIC 的项目身份、版本/技术栈与官方能力事实，含官方仓库与 Live Demo 的 P0 核验"
tags: [okf-bundle, blog-article, openmaic, agentmore, zhipu, qingyan, feynman-learning, ai-education, 博文转化]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-10-28T14:10:00+08:00" }
---

# 智谱清言 AgentMore × 清华 OpenMAIC 博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。
> 类目：**产品能力上新公告解读**（厂商一手公告 + 第三方/官方仓库核验，非源码教程、非操作教程）。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 智谱清言 AgentMore 官方分享页（公开长图/图文公告） | https://agentmore.chatglm.cn/shareFile/m/6ad704d27f8c85cf468aac82 |
| 发布方 | **智谱清言（AgentMore）官方**（`chatglm.cn` 为智谱官方域名） | 厂商一手公告；内容为 AgentMore 学习搭子能力上新 |
| 访问控制 | 无（公开可访问分享链接） | `shareFile/m/<id>` 公开分享页；无 `token`/邀请码等访问控制参数 |
| 敏感度级别 | **公开内容** | 公开产品公告，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **厂商自述（智谱清言官方公告）+ 官方仓库/第三方交叉核验** | 公告主体为厂商自宣；被点名的 OpenMAIC 为清华 THU-MAIC 开源项目，可用 GitHub 仓库/Live Demo/第三方测评交叉核验 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否** | 公告为能力上新说明，仅给出**对话示例 prompt**（费曼学习/习题带练各 3 轮）与 Skill 名称清单，无安装、配置、代码、API 调用步骤 |
| Q2：这些流程是否经作者实测、具备可复现性？ | **否** | 公告未给出可复现的注册/开通/安装步骤序列；"Skill 广场搜索名称即可安装"为一句式指引，无逐步操作证据；OpenMAIC 自身虽开源可部署，但**公告正文**不含该流程 |

**判定：两问任一为"否" → 产品公告/能力解读类骨架，不设 examples/**

**骨架**：
```
jishu/ai/products/agentmore-openmaic/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-what-is-openmaic-agentmore.md      # 项目/产品身份：OpenMAIC 是什么、AgentMore 学习搭子是什么、公告事实（What·Who·When）
│   ├── 01-two-new-study-modes.md             # 机制层：费曼学习三轮（先讲/再讲/换情境）+ 习题带练三轮（卡点/依据/总结）
│   └── 02-eight-openmaic-skills.md           # 清单层：8 个上新 Skill 名称/用途 + 与官方仓库目录名映射
└── references/
    ├── index.md
    ├── article-source.md                     # 博文事实清单（F 编号双份登记之一）
    └── verification.md                       # P0 核验报告（含勘误四张清单）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/products/agentmore-openmaic/`（选定） | ✅ | ① 主线是**智谱清言 AgentMore 的产品能力上新公告**，归 ai 产品组；② 该组 35 束全为"单篇公开文章 + P0 核验 + 七阶段转化"范式，且已有 `aitokenbus`（明确标注"产品自述资讯，非操作教程"）等**厂商自述类先例**；③ 名称 `agentmore-openmaic` 独特无同名冲突 |
| `jishu/ai/ecosystems/<新建智谱/清言目录>/` | ❌ | 该组 18 个目录为"厂商/项目生态全景"（如某平台全家桶）；本篇主线是**单一能力上新公告**，非智谱生态全景，新建目录属过度工程 |
| `jishu/ai/frameworks/<新建 openmaic 目录>/` | ❌ | 该组定位为**开源项目源码/操作教程**；本篇公告正文无可复现操作流程（两问皆否），且无源码解读内容，归此会与组内"教程"范式不符 |
| `sheke/` 或顶层新建分组 | ❌ | 主体为技术域 AI 产品/项目，跨域归置错误；单篇公告新建分组属过度工程 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/products/agentmore-openmaic/`

**与既有同类 spec 的关系（重要）**：`.trae/specs/okf-wiki-ecosystem/openmaic-wiki-20260909/`（已跟踪 `facts.md`）针对的是**另一篇文章**（GitHubDaily《短短 5 个月，暴涨 3.3 万 Star，清华开源的这个 AI 教育神器火了！》，2026-09-09），主体同为 OpenMAIC 项目但**信源、文章、采集时点均不同**。本次以**智谱清言 AgentMore 公告**为信源新建独立 spec 与 bundle，命名以 `agentmore-` 前缀区分；两束主题相邻，bundle 层以"主题关联"互链，不合并、不互相改写。

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-10（采集时点 2026-10-28，分享页未显示具体日期） |
| 官方核验时间 | 2026-10-28（GitHub 仓库 README/API、`skills/` 目录树、LICENSE 原文、Live Demo 在线页、第三方测评） |
| `stale_after` | **2026-12-31**（AgentMore 学习搭子处于快速迭代期，公告自述"后续将持续升级课程生成与修改能力"，年末复核能力集/Skill 清单/版本） |
| 高时效字段 | Star 数、License 口径、AgentMore Skill 上新清单、OpenMAIC 版本号、学习搭子能力集 |
| 已知边界声明 | ① 公告为**厂商自述**，"携手清华 OpenMAIC""8 个 Skill 已上新"等以官方公告为准，官方仓库/智谱文档未见对应逐字声明处标"仅公告单源"；② OpenMAIC **Star 数与 License 均为多源互斥口径**，本束不采信单一权威值，按"带时点观测"分层登记；③ 8 个 Skill 名称与官方 `skills/agent-runtime/` 目录名**仅部分可一一对应**，未命中项不推断；④ 公告未给出 OpenMAIC 具体 Star 数（"Github万星项目"为模糊表述） |

## 5. P0 必核验清单与结论摘要

| 核验对象（F 编号） | 类型 | 权威信源 | 结论 |
|--------------------|------|----------|------|
| OpenMAIC 项目真实存在、归属清华 THU-MAIC（F-002/F-025/F-026） | 项目身份 | GitHub 仓库 + README + 第三方站点 | ✅ 仓库 `THU-MAIC/OpenMAIC` 真实存在，全员口径一致 |
| Live Demo 与访问码机制（F-027） | 能力事实 | 官方 README（open.maic.chat） | ✅ README 确认 Demo 与访问码获取路径 |
| 版本与时间线（F-028） | 产品/项目事实 | README News + Release | ✅ v0.2.1（2026-04-26）为最新；v0.1.0（2026-03-26）与"2026-03 开源"口径一致 |
| 技术栈（F-029） | 技术事实 | README 徽章 | ✅ Next.js 16 / React 19 / TypeScript 5 / LangGraph 1.1 / Tailwind CSS 4 |
| Star 数（F-030） | 成效数字 | GitHub API 18,538（2026-10-28）vs 33,000+（GitHubDaily 2026-08-28）vs 41.5k（站点自宣）vs 16.3k（过期 HTML） | ⚠️ **多口径互斥**，按"带时点观测"分层登记，不单一断言 |
| License（F-031） | 合规事实 | LICENSE 文件正文 **MIT** vs README 徽章 **AGPL-3.0** vs GitHub API license 字段 **AGPL-3.0** | ⚠️ **三源互斥**，本束并列登记，不采信单一结论 |
| 8 个上新 Skill 与官方目录名映射（F-013~F-020/F-034~F-036） | 能力事实 | `skills/agent-runtime/` 目录树（24 项，`truncated: false`） | ⚠️ 6 项一一对应 ✅；"逆向教学设计"疑对应 `understanding-by-design`（UbD）、"习题带练"未见逐字同义项 |
| 官方 openmaic Skill 引导式 SOP（F-037） | 能力事实 | `skills/openmaic/SKILL.md` 全文 | ✅ 0 选择模式→克隆→启动→配置 Key→`GET {url}/api/health` 验活→生成课堂（`requirement`/`materialIds`） |
| ACCESS_CODE 站点级口令（F-038） | 能力事实 | README（v0.1.1 起） | ✅ |
| 课程生成能力存在（F-043） | 能力事实 | README two-stage pipeline（Outline→Scenes） | ✅ |
| AgentMore 学习搭子 + 8 Skill 上新（F-002/F-012/F-044/F-045） | 厂商自述 | 智谱清言 AgentMore 官方公告 | ⚠️ 公告单源；官方仓库与智谱公开文档未见逐字对应（"Skill 广场"机制亦无公开文档） |
| 智谱清言存在"学习搭子"与 AgentMore 模式（F-041/F-042） | 产品事实 | 第三方测评（36氪）+ App Store 开发者信息 | ✅ 第三方确认存在，作为公告可采信的旁证 |

**汇总**：P0/P1 核验 13 项 —— ✅ 7、⚠️ 6、❌ 0（F 编号行级口径 ✅ 14 / ⚠️ 6 / ❌ 0）。无核心声明失败（项目存在、归属、版本、Demo、SOP 均可核）→ 争议集中于 **Star 数、License 口径与厂商自述的 Skill 上新**；6 项 ⚠️ 在 verification.md 完整勘误并在正文标注口径。

## 6. 三层知识拆分（知识地图）

| 博文内容层 | 映射篇目 | F 编号支撑 |
|-----------|---------|-----------|
| 身份事实层（OpenMAIC 是什么/归属清华/AgentMore 学习搭子是什么/公告元信息/版本技术栈） | concepts/00-what-is-openmaic-agentmore.md | F-001~F-003、F-021~F-029、F-041~F-043 |
| 机制层（费曼学习三轮 / 习题带练三轮 / 学习闭环设计） | concepts/01-two-new-study-modes.md | F-004~F-011、F-022~F-024 |
| 清单层（8 个 OpenMAIC Skill 名称/用途/与官方目录映射/安装入口） | concepts/02-eight-openmaic-skills.md | F-012~F-020、F-032~F-040、F-044~F-045 |

## 7. ADDED Requirements（验收标准）

- bundle 9 个文件齐备（3 concepts + 2 references + 2 目录 index + 根 index + log，**无 examples/**），每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件
- 全部具体声明（项目名/版本/技术栈/Star/License/Skill 名/域名）携带 F 编号，无 facts.md 之外编造；厂商自述显式标"公告单源"
- 6 项 ⚠️ 勘误在正文呈现正确口径并标注：**Star 多口径**、**License 三源互斥（MIT vs AGPL-3.0）**、Skill 名映射 6✅/2⚠️、"Skill 广场/学习搭子上新"为公告单源
- frontmatter 多信源（公告 URL + GitHub 仓库 + Live Demo + README）标注，`stale_after=2026-12-31`
- 双份 F 编号一致（spec `facts.md` ↔ bundle `references/article-source.md` 连续无跳号、集合相等）
- products 组 index 导航表 + toctree 接入本束；计数 sync：products 35→36、ai 域 276→277、jishu 509→510、总 690→691（三处规模数字一致）
- V 阶段执行四视角审查与机械门禁（`check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` / `check-asset-baseline.py`）；invoke gates 不可用时执行手动等效清单并在 log.md 注明
