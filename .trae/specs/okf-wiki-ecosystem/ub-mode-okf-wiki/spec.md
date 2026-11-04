---
okf_version: "0.2"
type: spec
title: "ub-mode 博文→OKF 知识包转化规划"
description: "将微信公众号「开源日记」博文《只有一个 Skill 的仓库，竟然斩获 2900 Star！》转化为 OKF v0.2 知识包——覆盖 ub-mode 的项目事实、三步编码纪律机制、可打分检查工具（Crapper/Dryer/Mutator/uml-viewer）、安装触发与边界勘误"
tags: [okf-bundle, blog-article, ub-mode, agent-skill, clean-code, tdd, code-quality, unclebob]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-11-04T10:00:00+08:00" }
---

# ub-mode 博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA |
| 公众号 / 作者 | 开源日记 / 熊叔 | 公开原创文章，2026-10-28 08:53 发布 |
| 访问控制 | 无（公开可访问） | `/s/<id>` 公开文章格式，无 `share?code=` / `token=` / 邀请码参数（URL 仅带 `from=industrynews` 传播来源参数） |
| 敏感度级别 | **公开内容** | 开源项目推介 + 工程方法论解读，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **第三方综述（开源项目推介号）**，非厂商自宣 | 作者为第三方公众号，非项目作者本人；无提效倍数/成本下降类营销数字；核验主锚为 GitHub 官方 API 与仓库原文 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是（但仅概要）** | 博文给出「上手三步」：`mkdir -p ~/.claude/skills/ub-mode` + `cp SKILL.md`、重启后输入 `/ub-mode`、装三个检查工具并执行 `./crapper --threshold 10` / `./dryer --threshold 0.8 src` / `./mutator --changed` |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | ① 无版本信息（仓库无语言、无 Release、无 tag）；② 三个检查工具「需要单独安装」但**博文未给出任何安装方式**，照做链路在第三步断裂；③ 博文未声明作者实测，`.metrics` 输出（`crap.edn`/`dry.edn`/`mutate`）同样未经核验；④ 命令参数与官方仓库无可对拍文档（官方 README 只给安装，不给 CLI 用法） |

**判定：Q1 是 / Q2 否 → 任一为否，采用概念骨架，不设 `examples/`**（空 examples/ 或伪示例制造的伪结构比没有更糟）。

**骨架**：

```
jishu/ai/practice/ub-mode-coding-discipline/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-overview-and-philosophy.md      # 项目定位、作者与仓库事实、"规则越写越不听话"的提出
│   ├── 01-three-step-mechanism.md         # 三步机制：把 Bug 修好 → 修好还要检验 → 说明修改了什么
│   ├── 02-scoreable-checks.md             # 可打分检查：Crapper / Dryer / Mutator / uml-viewer 与阈值
│   ├── 03-install-and-usage.md            # 官方安装三路径（grok/claude/cursor）+ 博文上手三步
│   └── 04-boundaries-and-gotchas.md       # 局限性、博文与官方口径差异（勘误 E-1/E-2）
└── references/
    ├── index.md
    ├── article-source.md                  # 博文 + 官方源事实清单（F 编号双份登记之一）
    └── verification.md                    # P0 核验报告（含勘误四张清单）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/practice/`（选定） | ✅ | ① 主线实体 ub-mode 是「AI 编码工程纪律」规则集，属**工程实践与方法论**，与该组定位「AI 工程方法论、上下文工程、行业趋势研究及博文核验转化束」直接吻合；② 组内非源码类先例充分且同型：`docx-report-skill`（Skill 设计）、`answer-me-with-html`（Agent Skill 博文转化）、`ai-engineering-methodology`、`planning-with-files`（Agent 上下文工程方法论）、`standardized-agent-exams`（官方 Skill 规则边界） |
| `jishu/ai/products/` | ❌ | 该组定位为「面向终端任务的 AI 产品与工具」，其 Skill 束（oil-ui / image-blaster / huashu-art-motion / text-to-cad）均为**创作与任务型能力**；ub-mode 不产出终端交付物，而是约束 Agent 编码行为，语义错配 |
| `jishu/ai/learning/` | ⚠️ 次选 | 组内有 `qbs-book-to-skill`（书籍驱动技能构建）等同型方法论束，但该组定位为「体系化学习路径与上手教程」，本束是工程纪律解读而非学习路径 |
| `jishu/ai/frameworks/`、`ecosystems/`、`models/` | ❌ | 分别为「Agent/LLM 框架与代码库」「厂商与开源社区生态」「基础模型能力与多模态」，均不匹配 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/ub-mode-coding-discipline/`

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-10-28 08:53 |
| 官方核验时间 | 2026-11-04（GitHub API + `master` 分支 README.md / SKILL.md / LICENSE） |
| `stale_after` | **2027-01-31**（项目极年轻、Star 快速上涨，季度内复核） |
| 高时效字段 | Star 数（动态）、companion 工具清单、CLI 参数（`--threshold` / `--changed`）、`.metrics` 输出文件名 |
| 已知边界声明 | ① Star 为双时点快照（博文 2,900 / 核验 3,951）；② 三个检查工具的 CLI 用法**仅有博文单源**，官方仓库未提供用法文档；③ 默认分支为 `master` 而非 `main`；④ 未做真机复测 |

## 5. P0 必核验清单与结论摘要

| 核验对象（F 编号） | 类型 | 权威信源 | 结论 |
|--------------------|------|----------|------|
| 仓库存在 / owner / 创建时间（F-003~F-005） | 日期身份 | GitHub API `repos/unclebob/ub-mode` | ✅ `unclebob/ub-mode`，创建 2026-10-25T16:04:09Z |
| 默认分支（F-006） | 版本身份 | GitHub API `default_branch` | ✅ `master`（**非 main**）→ 决定 raw 路径口径 |
| 文件数量与体量「只有两个文件、约 6KB」（F-008） | 数字/口径 | GitHub Trees API | ⚠️ 实为 **3 个文件**（另含 LICENSE）；README+SKILL = 6,153 B ≈6KB，口径漏计 LICENSE |
| Star「2900」（F-010） | 动态数字 | GitHub API `stargazers_count` | ⚠️ 发文时点量级，核验时点 **3,951**（时效增长，非硬错） |
| 许可证 MIT / 著作权人（F-009） | 许可证 | 仓库 LICENSE 文件 | ✅ MIT License，Copyright (c) 2026 Robert C. Martin（API 的 `license` 字段为 null，以 LICENSE 文件为准） |
| 作者身份「Robert C. Martin 写过《Clean Code》」（F-036） | 身份 | LICENSE 署名 + GitHub owner | ✅ 署名一致；owner `unclebob` 即 Robert C. Martin（Uncle Bob）公开账号 |
| CRAP 阈值 < 10（F-024） | 阈值数字 | 官方 SKILL.md + README | ✅ 逐字一致（`CRAP < 10`） |
| 重复度阈值 0.8（F-025） | 阈值数字 | 官方 SKILL.md + README | ✅ 逐字一致（SKILL.md `rank 0.8 or above`；README `>= 0.8 similarity`） |
| 三步机制（F-016~F-018） | 机制声明 | 官方 SKILL.md 三大节 | ✅ 与官方 First Make it Work / Then Make it Right / Practice 结构一致 |
| 检查工具数量（F-027/F-028） | 清单 | 官方 README Companion Tool Repositories | ⚠️ 官方为 **4 个**（含 `uml-viewer`），博文只提 3 个 |
| 安装路径与触发（F-031/F-032） | 命令 | 官方 README Installation | ✅ 博文 Claude 路径与官方一致；官方另支持 `~/.grok/`、`~/.cursor/` |
| 检查工具 CLI 用法与 `.metrics` 输出（F-029/F-030） | 命令/输出 | 无权威源 | ⚠️ **仅博文单源**，官方仓库未提供 CLI 用法与产物文档 |
| 上游溯源 `@poteto` 的 poteto-mode / pstack（F-013） | 溯源声明 | 官方 README | ✅ 官方自述「loosely based on portions of @poteto's rules」；**博文未提及**，属补充事实 |

**汇总**：P0/P1 核验 13 组 —— ✅ 7、⚠️ 6、❌ 0。无核心声明失败 → `status: draft`（未实测），6 项 ⚠️ 在 verification.md 完整登记勘误/口径。

## 6. 三层知识拆分（知识地图）

| 博文内容层 | 映射篇目 | F 编号支撑 |
|-----------|---------|-----------|
| 定位层（项目是什么 / 谁做的 / 什么许可 / 仓库形态） | concepts/00-overview-and-philosophy.md | F-001~F-014、F-036 |
| 机制原理层（三步机制 = 修好 → 检验 → 说明） | concepts/01-three-step-mechanism.md | F-015~F-023 |
| 工具与度量层（Crapper / Dryer / Mutator / uml-viewer 与阈值） | concepts/02-scoreable-checks.md | F-024~F-030 |
| 安装与触发层（官方三路径 + 博文上手三步） | concepts/03-install-and-usage.md | F-031、F-032 |
| 边界与勘误层（作者不放心自动推送、工具需另装、口径差异） | concepts/04-boundaries-and-gotchas.md | F-033~F-035、F-008/F-010/F-027/F-028/F-029 |

**无 examples/ 的两问判定记录**：见本文第 2 节（Q1 是 / Q2 否）。

## 7. ADDED Requirements（验收标准）

- bundle 共 11 个文件齐备（index + log + concepts 6 + references 3），每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件
- 全部具体声明（数字 / 命令 / 阈值 / 路径 / 文件数量）携带 F 编号，无 facts.md 之外编造
- 6 项 ⚠️ 在正文呈现官方正确值并标注博文口径；`examples/` 明确不设且给出两问理由
- frontmatter 双信源（博文 URL + GitHub 仓库），`stale_after: 2027-01-31`，`status: draft`
- 双份 F 编号一致（spec `facts.md` ↔ bundle `references/article-source.md` 均为 F-001~F-037，连续无跳号）
- 分组 index 导航表 + toctree 接入（practice 27→28 束、25→26 目录）；`jishu/ai/index.md`（practice 27→28、总 279→280）、`jishu/index.md`（描述 279→280）、`bundles/index.md`（total 702→703、groups 64→65、jishu 512→513、ai 行 279→280）计数同步
- V 阶段执行四视角审查与机械门禁等效清单；`invoke gates.*` 不可用时在 log.md 注明「未声称 gates 通过」
