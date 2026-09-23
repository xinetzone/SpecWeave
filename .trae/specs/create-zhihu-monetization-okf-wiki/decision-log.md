---
source: .trae/specs/create-zhihu-monetization-okf-wiki/tasks.md（Task 4）+ 三级索引实测读数
created_at: 2026-09-23
task: Task 4（I-a · 骨架判定与归属决策）
status: decided
---

# Decision Log — 骨架判定与归属决策（Task 4）

## 1. 操作可复现性两问（examples/ 取舍）

- **问 1：信源是否为操作可复现内容？**——部分。S2 含明确的日常操作（发布 ≥100 字回答 / ≥30 字想法 / 互动五选三），S3 含报名与入圈动作；但信源本体是**活动规则宣告页**（规则声明），非分步教程。
- **问 2：操作步骤是否值得独立 examples/ 目录？**——否。bundle 定位为「事实 + 机制 + 路径」三层分析型 bundle（同簇先例：`monetization-essence` 无 examples/，`workbuddy-content-system` 标注「商业分析，非操作教程」亦无 examples/）。变现路径的行动清单属「建议路径」而非「信源复现」，并入 concepts 路径层（concepts/monetization-path-matrix.md、concepts/ai-creator-main-path.md 承载）。
- **判定：无 examples/**。理由留痕：信源为规则宣告页；行动清单为设计产物（Task 7 path-design.md → concepts），复现对象是平台规则本身而非本教程步骤。若后续 Task 8 审查认为路径文档需附"第一周 checklist"样例，以 concepts 内嵌小节承载，不单开 examples/。

## 2. 归属候选对照表

| 候选位置 | 判定 | 理由 |
|---|---|---|
| **sheke/industry** | ✅ 落此 | 内容为单一平台（知乎）的变现机制解析与个人路径设计——行业/商业趋势分析型；同簇 `ai-monetization`/`monetization-essence`/`overseas-freelance-night-work`/`ai-one-person-micro-product` 均在此；WorkBuddy 先例证明「博文转化 + 路径型」可入 industry |
| sheke/personal-growth | ❌ | 定位魅力/情商方法论教程，非平台经济机制 |
| sheke/marketing | ❌ | 营销理论通识（STP/4P/定位），非单一平台激励规则解析 |
| sheke/finance | ❌ | 个人理财投资通识，非创作变现 |
| jishu/ai | ❌ | 技术实现教程域；本 bundle 无技术实现内容 |
| 新建顶级分组 | ❌ | 规范：单篇不新建顶级分组 |

**结论**：`projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/`

## 3. 现值计数（Task 6 更新基准，2026-09-23 实测读取）

| 位置 | 现值 | 待更新处 |
|---|---|---|
| 总 index frontmatter | `total_bundles: 564`、`groups: 59`、`domains: 9` | total_bundles → 565；groups/domains 不变 |
| 总 index 概览图 + 域导航表 | sheke「社会科学（41 束）」两处 | → 42 束（两处同步） |
| sheke/index.md 方向列表 | 「…等 16 束行业分析」 | → 17 束 |
| sheke/index.md 分组导航表 | 「…数字自由职业（18 束）」 | → 19 束 |
| industry/index.md frontmatter description | 「…等 18 束行业分析」 | → 19 束 |
| industry/index.md 导航表 | 18 行（ai-monetization … workbuddy-content-system） | +1 行 = 19 行 |
| industry/index.md toctree | 18 条 | +1 条 = 19 条 |

三处计数一致（导航表/toctree/description 均为 18），Task 6 更新后四处须一致为 19（navigation+toctree+description+sheke 域表）。
