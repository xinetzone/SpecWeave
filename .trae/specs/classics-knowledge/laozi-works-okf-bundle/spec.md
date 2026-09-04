---
status: "draft"
name: laozi-works-okf-bundle
version: 1.0.0
created: 2026-08-30
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（老子著作属先秦古典文献，公共领域）
source: 出土文献整理本（郭店楚简/马王堆帛书/北大汉简）+ 历代注本 + 现代学术注本
---

# 老子著作 OKF 知识包（出土文献原文 + 权威解读）

## Why

用户希望全面调研老子本人相关的著作，获取「最权威、最真实」的原文与解读，并以 OKF wiki 教程形式发布到 awesome-okf-xs 知识库的恰当位置。经澄清确认三点范围决策：

1. **著作范围**：《道德经》为核心，并延伸覆盖托名老子/与老子直接相关的道家著作（《文子》《关尹子》《阴符经》等）。
2. **原文基准**：以出土文献为主（郭店楚简本 1993、马王堆帛书甲/乙本 1973、北大汉简本 2009 入藏），更接近老子原貌。
3. **解读来源**：出土文献校注 + 历代注本 + 现代学者注本三线并收。

现有 bundle 均非此主题：`boshu-laozi-wiki`（帛书阅读教程）、`laozi-lineage-okf-bundle`（传本源流谱系）、`laozi-zhudu-mystx-wiki`（单一注家 MyST 转换）。本任务新建一个独立 bundle，聚焦「老子著作的原文与解读本体」，与既有 `boshu-reading`（怎么读）互补。

## What Changes

- 新增 OKF bundle 目录 `projects/awesome-okf-xs/doc/bundles/think/laozi/laozi-works/`
- 按 OKF v0.2 规范建立三层结构：`concepts/`（核心概念）、`text/`（出土文献原文）、`commentaries/`（权威解读）、`references/`（信源登记簿）
- 新增方法论文档：`facts.md`（R 阶段事实清单）、`insights.md`（I 阶段洞察）、`patterns.md`（E 阶段可复用模式）
- 更新 `think/laozi/index.md`，将新 bundle 纳入其 toctree 与知识包列表
- 每条事实性论断以脚注 `[^source-id]` 溯源至 `references/` 权威信源，逐声明归因

## Impact

- 新增目录：`think/laozi/laozi-works/`（约 20+ 个 Markdown 文档）
- 修改文件：`think/laozi/index.md`（追加知识包列表行 + toctree 条目）
- 不修改任何既有 bundle 内容；不破坏现有功能
- 需通过 `invoke gates.toctrees`（导航完整性）与 `invoke gates.utf8`（编码）质量门

## ADDED Requirements

### Requirement: 老子著作知识包结构

系统 SHALL 在 `think/laozi/laozi-works/` 下建立一个符合 OKF v0.2 的知识包，根 `index.md` 含 `okf_version: "0.2"`，并含 `log.md`。

#### Scenario: bundle 结构合规

- **WHEN** 检查 `laozi-works/` 目录
- **THEN** 存在根 `index.md`、`log.md`，及 `concepts/`、`text/`、`commentaries/`、`references/` 四个子目录，每个子目录含 `index.md`

#### Scenario: OKF 一致性

- **WHEN** 逐个解析 bundle 内非保留 `.md` 文件的 frontmatter
- **THEN** 每个文件含可解析 YAML frontmatter 与非空 `type` 字段；`index.md`/`log.md` 遵循保留文件约定

### Requirement: 著作范围覆盖

系统 SHALL 覆盖「《道德经》+ 相关道家著作」：

- 《道德经》全书（出土文献版本体系为基准）为核心内容
- 延伸覆盖托名老子/直接相关的道家著作概览（《文子》《关尹子》《阴符经》等），各含成书、真伪、主题与老子思想关系

#### Scenario: 著作覆盖

- **WHEN** 浏览 `concepts/` 与 `text/`
- **THEN** 能找到《道德经》核心概念与原文，并能找到相关道家著作的概览概念

### Requirement: 出土文献原文（text/）

系统 SHALL 以出土文献为主提供《老子》原文，并逐声明溯源：

- 帛书甲本、帛书乙本、郭店楚简本、北大汉简本，各自独立概念文档
- 原文以权威整理本为准（如高明《帛书老子校注》、荆门市博物馆《郭店楚墓竹简》、《北京大学藏西汉竹书（贰）》），不得凭空编造释文
- 关键异文标注版本差异（如「大器晚成／大器免成」），并链接到相应解读

#### Scenario: 原文权威性

- **WHEN** 阅读 `text/` 任一原文文档
- **THEN** 释文可溯源至正式出版的整理本（frontmatter `sources` 含可核查文献），无匿名来源

### Requirement: 权威解读（commentaries/）

系统 SHALL 三线并收权威解读，每条解读标注注家立场与出处：

- 出土文献校注：高明、裘锡圭、北大简整理组等
- 历代注本：王弼、河上公、严遵、苏辙等
- 现代学者注本：陈鼓应、楼宇烈、李零等

#### Scenario: 解读权威性

- **WHEN** 阅读 `commentaries/` 文档
- **THEN** 能找到对应学者姓名、著作名与立场，重要分歧点（如「无」与「道」的哲学诠释）显式呈现为「争议与不确定性」小节，不做单一确定性断言

### Requirement: 可复用模式萃取（G3）

系统 SHALL 在 `patterns.md` 中沉淀至少 2 个可复用方法模式（如「出土文献层级校读法」「多注本立场对照法」），每个含触发场景、核心步骤、反模式、迁移验证。

### Requirement: 方法论文档闭环

系统 SHALL 记录 seven-concepts 场景4（R→I→E→V→C）应用痕迹：

- `facts.md`：R 阶段零推测事实清单（G1）
- `insights.md`：I 阶段洞察，至少 3 条含四元组（现象+根因+影响+建议）（G2）
- `patterns.md`：E 阶段模式（G3）
- V 阶段对抗审查结果显式记录于有争议概念的「争议与不确定性」小节

## MODIFIED Requirements

无（本任务为全新增量，不修改既有需求）。

## REMOVED Requirements

无。

## 开放问题

- 郭店楚简本存世仅为残简（约对应今本 31 章内容），`text/guodian-laozi.md` 只覆盖现存部分，需在文档中显式说明残损范围。
- 帛书甲本文有多处残毁，原文呈现以帛书乙本为较完整底本、甲本补充对照，此策略在解读中说明。
- 是否逐字转录帛书/北大简 81 章全文（体量较大），抑或「关键篇目全文 + 全部篇目逐章题解」？当前方案倾向「帛书乙本全文为主线、郭店/北大简现存差异对照」，实施阶段可据此调整颗粒度。