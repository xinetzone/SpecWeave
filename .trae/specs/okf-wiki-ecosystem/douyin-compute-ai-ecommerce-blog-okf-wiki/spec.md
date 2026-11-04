---
status: "in_progress"
version: "1.0"
---

# 抖音算力扩张与 AI 电商博文 → OKF Wiki 教程 Spec

## Why

微信公众号文章《抖音突然成立大批公司，准备放手一搏》（公众号"电商派Pro"，作者"李响"，2026-10-30）报道了抖音集团 2026 年在多地密集新设科技公司并持续加码算力投入的动作：新设廊坊平舒数源科技（注册资本 1 亿元）、呼和浩特塞北云基科技（13 亿元）等一批公司；同时梳理了廊坊的算力禀赋（时延、数据中心、机柜、算力指数）、火山引擎在芜湖/无为/广灵/和林格尔的算力中心投资，以及抖音电商的 AI 落地（"经营 AI+"应用大赛、双 11 首日增幅、豆包领券与抖店"豆包运营"板块），并以阿里 3800 亿、腾讯 2026Q2 资本开支 528 亿作为同业对照。文章落脚于作者判断"AI 大战，前半场看投入，后半场看转化"。按 blog-article-to-okf-bundle 模式转化为 OKF 知识包，归入 `sheke/industry/` 分组。

## 内容敏感度预检

**结论：公开内容（Public）**。信源为公开发布的微信公众号行业资讯，无访问控制参数语义（URL 仅含常规追踪参数 `from=industrynews&color_scheme=light`），主题为公开商业新闻。→ 标准工作流，spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`。

## 归属判定

**结论：`sheke/industry/douyin-compute-ai-ecommerce/`**（🏭 AI 行业与商业趋势）

- 主线实体为字节跳动/抖音集团的算力扩张与 AI 电商落地，属行业趋势与商业分析，非技术实现教程。
- 该分组已有大量微信博文转化先例（`doubao-douyin-livestream-ecommerce`、`qianwen-go-my-apps`、`telecom-ai-pilot-base`、`ai-side-hustle-playbook`、`workbuddy-content-system` 等），且已有 `douyin-vibecoding`、`volcengine-ecosystem`（火山引擎生态）等字节系条目。
- 单篇博文禁止新建分组 → 落既有 industry 分组。

### 候选位置对照表

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/industry/` | ✅ 采纳 | AI 行业与商业趋势分组，已有字节系与微信博文转化先例（doubao-douyin-livestream-ecommerce、volcengine-ecosystem） |
| `jishu/ai/ecosystems/` 等生态分组 | ❌ 排除 | 该处为单厂商产品/源码教程；本文非源码教程，且不落单一厂商生态 |
| `jishu/ai/products/` | ❌ 排除 | 该处为终端 AI 产品与工具教程，本文为平台级行业趋势与资本动作分析 |
| 新建分组 | ❌ 禁止 | 单篇博文不允许新建分组 |

### 同主题查重

全库检索 `平舒数源|塞北云基|塞上鸣沙|Anew Labs|火山引擎长三角|太行算力` 与 `bytedance` 目录名：**零命中**，无同主题 bundle。

字节系既有条目主题不同，无重复：

- `doubao-douyin-livestream-ecommerce`——豆包直播间嵌入 AI 回答的**产品功能与转化**分析；本包为**公司注册与算力基建**分析，两者互补不重叠。
- `volcengine-ecosystem`——火山引擎 AI 产品生态（AgentKit/Ark/HiAgent 等）；本包仅涉及其算力中心项目投资金额。
- `douyin-vibecoding`——抖音 Vibe Coding 开发范式，无关。

→ **新建 bundle**。

## 骨架判定（操作可复现性两问）

1. 博文是否有读者可照做的安装/配置/代码/实测流程？→ **否**。全文为公司注册信息、算力投资金额、平台经营数据与作者分析，无读者可照做的操作流程。
2. 这些流程是否经作者实测、具备可复现性？→ **不适用**。

两问皆非"是" → **不设 `examples/`**。骨架：`index.md + log.md + concepts/ + references/`。

## What Changes

- 新增 OKF bundle：`sheke/industry/douyin-compute-ai-ecommerce/`
  - `index.md` + `log.md` + `concepts/`（3 篇 + index）+ `references/`（2 篇 + index）
  - 不设 `examples/`（商业分析无可运行示例）
- 更新 `sheke/industry/index.md`：束数 36→37，导航表加行、toctree 追加条目、分组 description 更新
- 更新 `sheke/index.md`：AI 行业与商业趋势方向描述计数同步（36→37），社科域 85→86
- 更新 `bundles/index.md`：`total_bundles` 694→695、sheke 域 85→86、industry 分组 36→37（五面一致）
- 更新 `doc/index.md` 与 `README.md`：库规模数字 694→695

## 事实基础（博文 F-001 起）

共 36 条（F-001~F-036，连续无跳号），详见 [facts.md](facts.md)。分组：文章元信息 / 公司注册与股权 / 廊坊算力禀赋 / 火山引擎算力投资 / 抖音电商 AI 落地 / 同业投入 / 作者观点。

口径类型：`page_fact`（源文明示、可逐字核对）28 条 / `author_claim`（作者价值与趋势判断）8 条（F-002、F-026、F-031~F-036，其中 F-035 为源文自陈边界）。无 `reporter_test`（本文无记者一手实测环节）。

## ADDED Requirements

### Requirement: Bundle 根索引
`index.md` frontmatter 含 `okf_version: "0.2"`、`type: bundle`、`sources`（博文 URL + 公众号/作者/日期 + facts + verification）与 `generated`/`verified`；description 显式标注"商业分析/战略资讯，非源码教程"。已知边界声明：源文含 1 项确定数据错误（数据中心 40 应为 36）、2 组官方口径冲突、双 11 首日数据部分单源、多条为作者推断。

### Requirement: 概念文档（concepts/，3 篇）
- `00-new-companies-and-timeline.md`：抖音集团 2026 年新设科技公司地图与股权结构（廊坊平舒数源 + 内蒙三家 + 中卫两家 + AI 制药 Anew Labs）
- `01-compute-base-and-investment.md`：廊坊算力禀赋（时延/数据中心/机柜/算力指数/腾讯廊坊）与火山引擎算力中心投资，附阿里/腾讯同业对照
- `02-ai-ecommerce-implementation-and-conversion.md`：抖音电商 AI 落地（大赛三赛道、双 11 首日增幅、豆包运营板块）与"投入 vs 转化"的作者判断

### Requirement: 信源登记簿（references/）
- `article-source.md`：F-001~F-036 博文事实登记（区分客观事实与作者观点、标注转述层级）
- `verification.md`：P0 核验报告（C1~C19 结论、E1~E5 口径差异与勘误、G1~G6 缺口、flagged 决策）

### Requirement: 索引更新
`sheke/industry/index.md` 束数 36→37 与导航/toctree；`sheke/index.md`、`bundles/index.md`（五面）、`doc/index.md`、`README.md` 计数同步。

### Requirement: 勘误落实
源文 1 项确定错误（廊坊数据中心"40 个"→官方口径 **36 个**）必须在 `verification.md` 单列勘误，正文呈现**正确值并标注源文口径**，禁止静默照搬。

## 约束
- 本文为第三方行业媒体商业分析，非技术教程；不设 `examples/`；不编造未在博文中出现的数据
- 公司注册与股权信息、算力投资金额、双 11 数据须在核验阶段尝试 WebSearch 验证，不可验证则标注"仅博文单源"
- 十万/百万级金额与日期一律保留源文数值，勘误以"源文口径 vs 官方口径"并列呈现，不擅自改写源文
- 作者观点（F-031~F-036）须在正文显式标注"作者观点"，不得呈现为官方结论
- 交叉引用 industry 分组内其他 bundle 用相对路径

<!-- changelog -->
<!--
- 2026-10-31 | initial | 按 blog-article-to-okf-bundle 模式转化抖音算力扩张与 AI 电商博文
-->
