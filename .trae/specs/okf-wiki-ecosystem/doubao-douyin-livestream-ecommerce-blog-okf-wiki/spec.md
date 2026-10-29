---
status: "in_progress"
version: "1.0"
---

# 豆包直播间嵌入抖音电商博文 → OKF Wiki 教程 Spec

## Why

微信公众号文章《抖音太猛了，又搞出一个新平台》（公众号"电商派Pro"，作者"李松月"，2026 年双 11 前夕）报道了豆包上线新功能：把抖音电商直播间嵌入豆包 AI 回答，用户问穿搭/好物时正在开播的直播间出现在回答里，可看播、领券、下单且全程不跳出豆包。文章同时梳理了豆包近一年的电商功能时间线（去年 10 月对话推荐商品、今年 3 月应用内下单测试、今年 4 月"帮你选"进导航栏）、双 11 价格补贴实例，以及阿里/美团/京东的 AI 电商对标布局。按 blog-article-to-okf-bundle 模式转化为 OKF 知识包，归入 `sheke/industry/` 分组。

## 内容敏感度预检

**结论：公开内容（Public）**。信源为公开发布的微信公众号行业资讯，无访问控制参数语义（URL 仅含常规追踪参数 `from=industrynews`），主题为公开商业新闻。→ 标准工作流，spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`。

## 归属判定

**结论：`sheke/industry/doubao-douyin-livestream-ecommerce/`**（🏭 AI 行业与商业趋势）

- 主线实体为豆包/抖音电商的 AI 电商布局，属行业趋势与商业分析，非技术实现教程。
- 该分组已有大量微信博文转化先例（`qianwen-go-my-apps`、`telecom-ai-pilot-base`、`ai-side-hustle-playbook`、`workbuddy-content-system` 等），且已有 `douyin-vibecoding`、`volcengine-ecosystem`（火山引擎生态，含抖音）等字节系条目。
- 单篇博文禁止新建分组 → 落既有 industry 分组。
- 排除落位：`jishu/ai/products/`（该处为面向终端任务的 AI 产品与工具教程，本文为平台级行业趋势分析，不落此类）。

### 候选位置对照表

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/industry/` | ✅ 采纳 | AI 行业与商业趋势分组，已有同类微信博文转化先例（qianwen-go-my-apps 等） |
| `jishu/ai/ecosystems/tencent/` 等生态分组 | ❌ 排除 | 该处为腾讯等单厂商生态源码/产品教程；本文非源码教程 |
| `jishu/ai/products/` | ❌ 排除 | 该处为终端 AI 产品与工具教程，本文为平台级行业趋势分析 |
| 新建分组 | ❌ 禁止 | 单篇博文不允许新建分组 |

### 同主题查重

全库检索 `豆包|doubao|抖音电商|直播间.*电商`：无同主题 bundle。字节系既有条目（`douyin-vibecoding` 抖音 Vibe Coding、`volcengine-ecosystem` 火山引擎生态）主题不同，无重复。→ **新建 bundle**。

## 骨架判定（操作可复现性两问）

1. 博文是否有读者可照做的安装/配置/代码/实测流程？→ **否**。全文为商业资讯报道与作者分析，无读者可照做的操作流程（价格对比属记者实测记录，非可复现教程）。
2. 这些流程是否经作者实测、具备可复现性？→ **不适用**。

两问皆非"是" → **不设 `examples/`**。骨架：`index.md + log.md + concepts/ + references/`。

## What Changes

- 新增 OKF bundle：`sheke/industry/doubao-douyin-livestream-ecommerce/`
  - `index.md` + `log.md` + `concepts/`（3 篇 + index）+ `references/`（2 篇 + index）
  - 不设 `examples/`（商业分析无可运行示例）
- 更新 `sheke/industry/index.md`：束数 35→36，导航表加行、toctree 追加条目、分组 description 更新
- 更新 `sheke/index.md`：AI 行业与商业趋势方向描述计数同步（35→36），社科域 83→84
- 更新 `bundles/index.md`：`total_bundles` 691→692、sheke 域 83→84、industry 分组 35→36

## 事实基础（博文 F-001 起）

共 43 条（F-001~F-043），详见 [facts.md](facts.md)。分组：文章元信息 / 豆包新功能 / 豆包电商时间线 / 用户与转化数据 / 大厂 AI 电商对标 / 作者观点。

## ADDED Requirements

### Requirement: Bundle 根索引
`index.md` frontmatter 含 `sources`（博文 URL + 公众号/作者/日期）与 `generated`/`verified`；description 显式标注"商业分析/战略资讯，非源码教程"。已知边界声明：价格实例受账号/时段/券包影响、推荐与排序机制未披露、双 11 转化数据未披露、资讯时效性。

### Requirement: 概念文档（concepts/，3 篇）
- `00-livestream-entry-timeline.md`：豆包电商功能时间线与直播嵌入新功能（去年 10 月→今年 3 月→4 月→双 11）
- `01-flow-to-orders-and-subsidy.md`：从流量到订单的转化逻辑与补贴机制（4.19 亿 MAU、价格实例、补贴归因疑点）
- `02-big-tech-ai-ecommerce-landscape.md`：大厂 AI 电商对标（阿里/美团/京东路径差异）

### Requirement: 信源登记簿（references/）
- `article-source.md`：F-001~F-043 博文事实登记（标注哪些为作者观点、哪些引自第三方/外媒）
- `verification.md`：P0 核验报告（QuestMobile 数据、130 万家商家、各平台产品时间线、价格口径）

### Requirement: 索引更新
`sheke/industry/index.md` 束数 35→36 与导航/toctree；`sheke/index.md` 与 `bundles/index.md` 计数同步。

## 约束
- 本文为第三方行业媒体商业分析，非技术教程；不设 `examples/`；不编造未在博文中出现的数据
- 第三方数据（QuestMobile 4.19 亿 MAU、130 万家商家）须在核验阶段尝试 WebSearch 验证，不可验证则标注"仅博文单源转述"
- 价格对比（17.43 元 vs 27.9 元）为账号/时段/券包相关的单次实测，须标注口径
- 交叉引用 industry 分组内其他 bundle 用相对路径

<!-- changelog -->
<!--
- 2026-10-29 | initial | 按 blog-article-to-okf-bundle 模式转化豆包直播间电商博文
-->
