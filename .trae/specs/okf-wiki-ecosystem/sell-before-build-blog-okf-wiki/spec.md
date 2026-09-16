---
status: "draft"
version: "1.0"
---

# 「先卖后做」需求验证博文 → OKF Wiki 教程 Spec

## Why

微信公众号文章《自动赚钱系统，仅用一天时间，就能搭建好》（公众号"黄唯起"，页面署名"财富解密"，2026-09-10 12:33 发布于广西，标注原创，页面显示"标题已修改"）以"赚钱顺序"为切入点，主张"卖→验证→再做"的逆向创业顺序，援引芒格/雅各比逆向思维、哈佛商学院 Lou Shipley 观点、Dropbox 演示视频、亚马逊逆向工作法四个证据，并给出普通人的"一周需求验证法"。按 blog-article-to-okf-bundle 模式（R→I→E→V→C）转化为 OKF 知识包。

## 内容敏感度预检（阶段 0）

- URL：`https://mp.weixin.qq.com/s/f6xHxUiHVgpIbifKSOQ3FQ`，无 `share?code=`/`token=`/邀请码等访问控制参数 → **公开内容（Public）**
- 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 信源距离预判

- 信源性质：**个人自媒体观点文 + 引流钩子**（文末"评论区留'顺序'领可打印清单"为私域引流动作），非官方发布、非一手实测报告
- 作者自称"12 年野路子投资"（F-002），无法独立核验，按"作者自述"处理
- 博文无厂商赞助身份、无客户成效数字（提效倍数/收入截图），营销叙事浓度主要体现在**标题党**（标题"一天"vs 正文"一周"，F-029）而非伪造成效数据
- 四个二手转述证据（名人/名企案例）全部列为 P0 必核验

## 骨架判定（操作可复现性两问）

| 判据 | 结论 |
|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用/实测流程？ | 有"一周 7 天行动方案"（找品→测试内容→PDF 最小产品→挂单定价→搜索型内容→看数据→迭代），属泛化商业行动建议 |
| ② 是否经作者实测、有版本/输入输出/步骤顺序可复现？ | **否**——作者未提供本人按此流程实操的成交数据或输入输出样例；平台规则（小红书/闲鱼/抖音）强时效；属方法论主张而非经实测的 SOP |

**两问任一为"否" → 不设 examples/**。判定为**商业方法论/自媒体观点类**（商业分析骨架的社科对应物）：index + concepts/（3 篇）+ references/（2 篇）+ log，index 顶部声明"个人自媒体方法论观点，非经实测的操作 SOP"。

## 归属判定

**结论：`sheke/marketing/sell-before-build-validation/`**

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `sheke/marketing/`（选定） | ✅ | 主线方法"先卖后做（sell before you build）"本质是需求验证/营销顺序方法论；一周方案全部动作（选品、测试内容、挂单、搜索流量）属内容电商营销范畴；分组导语明确收录"内容私域"，现有 marketing-fundamentals 为系统通识，本文为单观点深描+案例核验，互补不重复 |
| `sheke/finance/` | ❌ | 分组定位为投资通识/资产配置/财富观念（含《管道的故事》），本文非投资理财内容，作者投资身份仅为叙述人设 |
| `sheke/personal-growth/` | ❌ | 分组收魅力/情商综合教程，主题不符 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程 |

## What Changes

- 新增 spec：`.trae/specs/okf-wiki-ecosystem/sell-before-build-blog-okf-wiki/`（spec.md + facts.md）
- 新增 OKF bundle：`sheke/marketing/sell-before-build-validation/`（9 文件，无 examples/）
- 更新 `sheke/marketing/index.md`：total_bundles 1→2、导航表加行、toctree 追加
- 更新 `sheke/index.md`：导航表 marketing 行束数 1→2
- 更新 `bundles/index.md`：total_bundles 538→539、正文计数、mermaid sheke 37→38、社科域节 37→38、marketing 行 1→2

## ADDED Requirements

### Requirement: 概念文档（concepts/，3 篇）

| 博文内容层 | 映射篇目 |
|-----------|---------|
| 论点层（What）：顺序倒置、需求发现论、逆向思维 | `00-sell-before-build-thesis.md` |
| 证据层（Why/核验）：芒格/雅各比、Lou Shipley、Dropbox、亚马逊四证据及勘误 | `01-evidence-and-case-studies.md` |
| 落地与边界层（How）：一周验证法 7 天表、精益创业谱系定位、批判边界 | `02-one-week-validation-playbook.md` |

### Requirement: 信源登记簿（references/，2 篇）

- `article-source.md`：F-001~F-029 博文事实（客观陈述/作者观点/元信息三类）+ F-030~F-036 核验补充
- `verification.md`：6 项 P0 核验逐项结论（✅/⚠️/❌）、勘误四清单落点、权威 URL 汇总

### Requirement: 状态与时效

- `status: stable`——核心论点（先验证需求再投入生产）经多源成立；博文瑕疵均为非核心的细节夸张/装饰引语/无出处数字，勘误完整登记，不触发 flagged
- `stale_after: 2027-06-30`——方法论骨架跨周期有效；平台动作与 9.9/19.9 定价部分强时效，正文声明规则时点 2026-09

## 约束

- 所有具体声明引用 F 编号；作者观点保留"作者观点"标注
- 博文中的夸张/失实细节（"没写一行代码"、"18 个月"、歌德句、头衔）正文呈现核验后正确值并标注博文口径，不静默照搬
- 不替作者宣称方案有效性（无成交证据）；平台合规只做一般性风险提示，具体规则以平台当期条款为准
- 交叉引用使用相对路径，禁止 `file:///`

<!-- changelog -->
<!--
- 2026-09-16 | initial | 按 blog-article-to-okf-bundle 模式转化「先卖后做」需求验证博文
-->
