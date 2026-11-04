---
status: "completed"
version: "1.0"
---

# 秒悟 Meoo「豆掌柜」副业案例博文 → OKF Wiki 教程 Spec

## Why

微信公众号「秒悟Meoo」（发布账号即 Meoo 官方公众号）2026-10-29 01:00 发布公开文章《纳尼?！真有人靠 Meoo 做副业月入过万！》。文章讲述一名 02 年出生的女生王玉丹用秒悟 Meoo 为上海一家拼豆店做出门店管理应用「豆掌柜」，跑 5 家店、免费试用一个月、驻店一周、累计迭代数百次，最终于 2026 年 8 月底被店主以 1 万元购买，并梳理了需求发现、工具层降摩擦、客户开发与试用、成交边界四段经历。按 `seven-concepts-cmd`（R→I→E→V→C）知识沉淀链路转化为 OKF v0.2 知识包，归入 `jishu/ai/ecosystems/miaowu/` 分组。

## 内容敏感度预检

**结论：公开内容（Public）**。信源为公开发布的微信公众号文章，URL 不含 `share?code=`/`token=` 等访问控制参数，无登录墙或验证码；WebFetch 单通道取到完整正文。→ 标准工作流，spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`。

## 归属判定

**结论：`jishu/ai/ecosystems/miaowu/miaowu-douzhanggui-case/`**（⚙️ 技术域 / AI 与大模型应用生态 / 秒悟 Meoo）

- 文章主线是「秒悟 Meoo 被真实用于接单成交」的单案例拆解，属 Meoo 平台生态的实践叙事，与同分组既有束（实训案例、增长 Skill、赏金广场、大使指南、产品功能全景）互补。
- 单篇博文禁止新建分组 → 落既有 `miaowu` 组。

### 候选位置对照表

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/ecosystems/miaowu/miaowu-douzhanggui-case/` | ✅ 采纳 | 与同分组既有五束同属 Meoo 平台生态，本束补齐「一个已走完全程的真实案例」 |
| `sheke/industry/` | ❌ 排除 | 该处为 AI 行业与商业趋势分析；本文是单案例实践拆解，非行业趋势报道 |
| `jishu/ai/products/` | ❌ 排除 | 该处为面向终端任务的 AI 产品与工具教程；本文非产品教程 |
| 新建分组 | ❌ 禁止 | 单篇博文不允许新建分组 |

### 同主题查重

全库检索 `miaowu|秒悟|Meoo|豆掌柜|拼豆`：既有五束主题分别为「怎么搭」「按阶段选 Skill」「平台共创计划」「创作者激励」「平台能力面」，无「单案例成交拆解」。→ **新建 bundle**。

## 骨架判定（操作可复现性两问）

1. 博文是否有读者可照做的安装/配置/代码/实测流程？→ **否**。全文为单案例叙事，无读者可照做的操作步骤。
2. 这些流程是否经作者实测、具备可复现性？→ **不适用**。

两问皆非「是」 → **不设 `examples/`**。骨架：`index.md + log.md + concepts/ + references/`。

## What Changes

- 新增 OKF bundle：`jishu/ai/ecosystems/miaowu/miaowu-douzhanggui-case/`
  - `index.md` + `log.md` + `concepts/`（4 篇 + index）+ `references/`（2 篇 + index）
  - 不设 `examples/`（叙事型案例无可运行示例）
- 更新 `jishu/ai/ecosystems/miaowu/index.md`：束数 6→7，bullet 与 toctree 追加条目、description 更新
- 更新 `jishu/ai/ecosystems/index.md`：ecosystems 束数 103→104，miaowu 表行 6→7
- 更新 `jishu/ai/index.md`：ai 域 277→278
- 更新 `jishu/index.md`：技术域 510→511
- 更新 `doc/bundles/index.md`：`total_bundles` 692→693、mermaid 节点、域节标题、ai 表行
- 更新 `doc/index.md` 与 `README.md`：三处规模数字 692→693

## 事实基础（文章 F-001 起）

共 60 条（F-001–F-060），详见 [facts.md](facts.md)。分组：文章身份与人物背景 / 需求发现 / 工具层与开发起点 / 客户开发与三类失败 / 试用与迭代 / 成交与后续 / 通用建议 / 结尾互动。**全部来自单一信源 S1**，无第三方凭证。

## ADDED Requirements

### Requirement: Bundle 根索引
`index.md` frontmatter 含 `sources`（文章 URL + 账号/标题/日期；同分组既有束相对路径；Meoo 官方入口）与 `generated`/`verified`；description 显式标注「单案例拆解、不设 examples」；设「阅读前必知的三件事」与「已知边界」段，声明单源、可迁移的是方法而非结果、成交含隐性维护成本。

### Requirement: 概念文档（concepts/，4 篇）
- `00-case-overview.md`：案例全景（人物与背景、时间线、产品与交易要素、与同分组既有束的关系）
- `01-need-discovery-and-tooling.md`：需求发现（观察店员忙乱）与工具层降摩擦（Meoo 处理服务器/数据库/部署）+ 现场观察问题清单
- `02-customer-development-and-trial.md`：客户开发与试用迭代（跑 5 家店三类失败、话术导图、免费试用条件、驻店一周与数百次迭代）
- `03-deal-boundaries-and-insights.md`：成交条款与边界（1 万元 / 一年免费维护 / 第二家未验证）、五条四元组洞察、两个可迁移模式

### Requirement: 信源登记与核验（references/）
- `source-ledger.md`：S1–S5 信源台账 + F-001–F-060 编号事实 + 单源声明 + 放弃核验清单 + 口径提醒
- `verification.md`：P0 核验报告（19 项；9✅ / 9⚠️ / 1❌）

### Requirement: 索引更新
`miaowu/index.md` 束数 6→7 与 bullet/toctree/description；`ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`、`doc/index.md`、`README.md` 计数同步。

## 约束
- 本文为**平台方自述单源案例**（发布账号即案例中工具提供方，存在利益相关）；不设 `examples/`；不编造未在博文中出现的数据
- 金额、数量、人物经历均无第三方凭证，须在核验阶段标注单源边界；标题「月入过万」与单笔 1 万元口径须区分
- 交叉引用 miaowu 分组内其他 bundle 用相对路径；bundle 内引用同组束需从 `concepts/` 上溯两级（`../../`）
- 产出物入 `projects/awesome-okf-xs/doc/bundles/`；源文缓存与截图不落库

<!-- changelog -->
<!--
- 2026-10-29 | initial | 按 seven-concepts-cmd（R→I→E→V→C）转化秒悟 Meoo「豆掌柜」副业案例博文
-->
