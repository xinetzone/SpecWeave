# 《高性价比人生指南》（HowToLiveBetter）多信源 → OKF Wiki 精读教程 - 产品需求文档

## Overview

- **Summary**：全面学习 4 个公开信源（mushroom 博文 + 3 个 GitHub Pages 站点）并上溯至其共同原始仓库 eternity4719/HowToLiveBetter，按七概念「知识沉淀」链路（R→I→E + V 审查）转化为一个 OKF v0.2 知识包（bundle），系统讲透「循证 + 性价比 + 四资源」人生决策方法论、33 章导览与 15–25 条标杆条目，并接入 awesome-okf-xs 三级索引。
- **Purpose**：原作是持续快速更新的 600+ 条网页/电子书，读者难以把握其方法论骨架与证据纪律；本包做"教程式蒸馏"——让读者理解其分级/算账框架、会用检索页与离线版/AI skill、能带着批判边界读条目，并能把框架迁移到评估任何一条生活建议；不复制全书。
- **Target Users**：① 想系统了解该开源指南的中文读者；② 希望用循证方式做健康/法律/理财/职场决策的普通人；③ 对"证据分级 + 成本收益"决策方法论本身感兴趣的人。

## Goals

- G1：产出一个结构完整、事实可溯源的 OKF v0.2 bundle，落位于 `sheke/personal-growth` 分组。
- G2：方法论讲透——证据等级 A/B/C、争议/TODO 机制、四种资源不跨口径、三项成本、收益量级阈值、性价比档、受益者四档、只引原始文献原则。
- G3：全书导航——33 章导览（四大板块、每章主题+口径）、5 篇 docs 长文导引。
- G4：标杆条目精读 15–25 条（跨章选取，完整保留成本/收益数字/证据级/争议/禁忌/原始出处），全部事实有 F 编号支撑。
- G5：多信源版本关系厘清——博文快照（498 条/31 章/2026-09-17）→ dlgrv 翻译快照（608 条）→ cdyforever（33 节）→ 原仓现行（615 条/33 章/2026-09-28），数字差异按"版本演进"处理而非勘误。
- G6：关键 P0 数字完成权威交叉核验（NEJM/Cochrane/China CDC/WHO/NHTSA/GitHub API 等）。
- G7：三级索引接入并计数同步；机械门禁逐项留痕。

## Non-Goals

- N1：**不复制/搬运全部 615 条**——本包是精读教程，全量内容以在线版/离线版为准（原作 Unlicense 允许复制，但镜像不是 wiki 的职责且会快速过期）。
- N2：不设 `examples/` 目录（操作可复现性两问判定见下）。
- N3：不执行任何 git commit / push（用户明确选择"仅落盘"）；C 阶段仅在 log.md 记录交付清单。
- N4：不做医学/法律建议——所有健康/法律条目均为原作内容转述，附边界声明，重大决策指引读者咨询专业人士与官方渠道。
- N5：不核验 615 条的全部引文（不现实）；P0 核验范围限定为博文与 README 的核心统计数字、精选条目直接引用的研究、以及项目元数据。
- N6：不修改原作仓库，不向其提 PR/Issue。

## Background & Context

### 内容敏感度预检（步骤 2.3）

- 4 个用户给入 URL 均为**公开内容**（公开博客 + 公开 GitHub Pages，无 token/邀请码/内网域名）；共同原始仓库为公开 GitHub 仓库 → **公开内容，标准工作流**。
- spec 落 `.trae/specs/okf-wiki-ecosystem/how-to-live-better-okf-wiki/`；产出落 `projects/awesome-okf-xs/doc/bundles/`；不涉及私域分流。

### 信源全景（R 阶段勘察结论）

| 信源 | 性质 | 关键口径 | 时效 |
|---|---|---|---|
| github.com/eternity4719/HowToLiveBetter（**原仓/一级信源**，用户未直接给出但博文明确指向，按信源先行原则上溯） | 开源组织仓库（Unlicense）；数据= README.md + book/ 33 章 Markdown；纯静态检索页；docs/ 含 5 篇长文 + `引用对照.md`（110KB）+ `核实记录/` 目录；附 life-decision-guide AI skill | **现行 615 条/33 章；A 415 / B 151 / C 49；争议 57；TODO 35；极高 104（17%）/高 279（45%）/一般 232（38%）** | 创建 2026-09-07（API）；最近 push 2026-09-25；2026-09-28 stars **19,238**/forks 1,355（GitHub API） |
| eternity4719.github.io/HowToLiveBetter/（用户 URL②） | 原仓官方在线检索页（JS 渲染，WebFetch 仅得标题） | 数据随 book/ 实时更新；支持关键词/章节/证据级/三项成本/口径组合筛选、术语悬浮、条目互引 | 现行 |
| blog.mushroom.cv 博文（用户 URL①，CC BY 4.0，作者 Mycelium Protocol，2026-09-17） | 第三方介绍文（项目盘点性质） | **快照口径：498 条/31 章；A 323/B 126/C 49；争议 45；TODO 39；极高 88（18%）/高 248（50%）/一般 162（33%）；三周 stars 2,366/forks 195**；低钠盐等示例；四篇长文介绍 | 2026-09-17，自述上线日 2026-09-07 |
| dlgrv.github.io/HowToLiveBetter/zh/（用户 URL③） | Fork 的**非官方翻译快照**（页首自述"非官方翻译……原文仍在更新"） | 快照口径 **608 条**；sec=1 含 36 条；条目结构（成本/收益/备注/来源 DOI）完整 | 快照，已滞后 |
| cdyforever.github.io/how-to-live-better/（用户 URL④） | 另一个 Fork 渲染（单页锚点 `#s1-30`） | **33 节**全章名；条目渲染同构 | 接近现行 |

**版本链结论**：498（9/17 博文）→ 608（dlgrv 快照）→ 615（9/28 现行）；章数 31 → 33（新增第 32 出国留学、第 33 残疾之后；现行章名与博客盘点的 31 章在中段也有拆分/增补，如"不要浪费精力/时间""反面清单""怎么放松""看病""人走了以后""出国旅行""外形""重大打击""上学以后"）。博文数字与现行数字的差异是**作品高速演进的版本差**，非源文错误；但须在正文与 verification.md 双向标注时点。

### 归属位置分析（步骤 3 决策树）

| 候选位置 | 判定 | 理由 |
|---|---|---|
| **sheke/personal-growth（选定）** | ✅ | 主线实体是"循证人生决策/自我提升指南"，跨健康/法律/理财/职场/婚育，"个人成长与自我提升"是唯一能容纳跨域人生决策主线的既有分组；组内现有 2 束（female/male-charm-eq）均为综合生活能力教程，形态可容纳 |
| sheke/workplace | ❌ | 仅覆盖第 19/23/31 章职场切片 |
| sheke/finance | ❌ | 仅覆盖金钱口径（第 5/7/15 章等） |
| yixue 医学与养生 | ❌ | 该域为中医经典/养生元典，本书是现代循证科普 + 大量非医学内容，语义不符 |
| 新建 life-skills 分组 | ❌ | 技能铁律：单主题禁止新建分组（过度工程） |

- bundle 目录名：`how-to-live-better`（kebab-case，与原仓同名）。
- 组内互链：与 female-charm-eq / male-charm-eq 互链（同属"用证据优化个人生活"主题簇，分工：本书是决策框架与条目库，两束是魅力/情商专项能力）。

### 骨架判定（步骤 2：操作可复现性两问）

1. 有无读者可照做的安装/配置/代码/实测流程？——仅有"打开检索页勾选筛选""下载离线文件""git clone + python -m http.server""装 AI skill"等简单使用动作；作品主体是生活建议。
2. 是否经作者实测、有版本/输入输出/步骤顺序？——使用动作来自上游 README 文档而非本转化作者实测；不构成两问意义上的可复现操作 SOP。
- **结论：任一问不满足 → 不设 examples/**；使用方法写成 `concepts/05-how-to-use.md`（同 sell-before-build-validation 先例：硬核技术内容亦可正确无 examples/）。

### 内容骨架（I 阶段三层拆分）

```
how-to-live-better/
├── index.md                        # 根索引：性质声明/版本时点/勘误与版本差提示/知识结构/信任与边界
├── log.md                          # 生成日志（R→I→E→V 链路记录）
├── concepts/
│   ├── index.md                    # 学习路径 + toctree
│   ├── 00-project-landscape.md     # 事实层：项目是什么、版本演进时间线、33章/5长文/引用对照/AI skill 生态、增长数据
│   ├── 01-evidence-grading.md      # 机制层：A/B/C 分级、争议/TODO、只引原始文献；统计数字素养（HR/RR/OR/CI/RCT/荟萃/队列/混杂/反向因果 精选）
│   ├── 02-cost-benefit-model.md    # 机制层：四资源不跨口径、三成本、收益量级阈值表、性价比档（档位属作者判断=C级）、受益者四档、排序与互引
│   ├── 03-chapter-map.md           # 导航层：33 章四大板块导览（Mermaid 板块图 + 每章一行：主题/口径/代表问题）+ 5 篇 docs 长文导引
│   ├── 04-high-value-entries.md    # 应用层：15–25 条标杆条目精读（跨章；每条含成本/说人话/收益数字/证据级/争议与禁忌/F 出处）
│   ├── 05-how-to-use.md            # 使用层：检索页组合筛选/互引/术语悬浮、离线 HTML·PDF·EPUB、life-decision-guide skill、自托管、三镜像怎么选
│   └── 06-boundaries-and-method.md # 迁移层：时效与适用边界（法规价格中国 2026-09 时点/C级/TODO/非医疗法律建议）+ 用本书框架评估任意生活建议的方法
└── references/
    ├── index.md                    # toctree
    ├── article-source.md           # F 编号事实双份登记（四信源 + 原仓，分类：元信息/版本数据/机制规则/条目事实/长文与工具）
    └── verification.md             # P0 核验报告 + 版本演进对照表（勘误四清单落点 + 信源距离评估）
```

## Functional Requirements

- **FR-1（R 事实）**：spec `facts.md` 完成 F-001 起连续编号登记，覆盖四信源 + 原仓的元信息、全部计数声明、机制规则、精选条目数字与出处；作者观点/价值判断显式标注；镜像快照口径标注时点。
- **FR-2（R 核验）**：P0 清单逐项 WebSearch/官方 API 核验并记录 ✅/⚠️/❌：① 项目元数据（创建日、license、stars/forks 两时点）；② 版本计数（498/31/323·126·49/45/39/88·248·162 vs 615/33/415·151·49/57/35/104·279·232）；③ 低钠盐 SSaSS（NEJM 2021, DOI, n=20,995, RR 0.88/0.86/0.87, 4.74 年）；④ 头盔 Cochrane 2008（OR 0.58/0.31）；⑤ 烟雾报警器 JAMA 1998 + 中国 CO 中毒 11,523（China CDC Weekly 2020）；⑥ 安全带 NHTSA 45%/60% + WHO 中国 2021 道路死亡 248,099；⑦ 院外心脏骤停 79.2% 家中/38,227 例中国研究；⑧ 2025 蘑菇中毒 828 起/2,165 人/13 死（中国疾控）；⑨ 博文自述的上线日期与 stars 增速。
- **FR-3（E 信源先行）**：先写 references/ 两篇，再写 concepts/，各级 index 最后写；具体数字/研究名/法规名必须可回溯到 F 编号，禁止 facts 集外生造。
- **FR-4（E 精读）**：04-high-value-entries.md 精选 15–25 条，覆盖四大板块且优先"极高性价比 × A 级"交集；每条保留原作的争议与禁忌（如低钠盐对肾功能不全/保钾药人群、头盔数据外推电动自行车、观察性研究反向因果）。
- **FR-5（V 门禁）**：执行技能§7 手动等效验证清单（UTF-8 strict、双份 F 编号集合比对、三级 toctree 逐一 Test-Path、相对链接全可达、三级计数同步、敏感路径零残留、frontmatter 齐备、版本差在正文落实），结果写入 log.md；invoke gates 若环境可用则跑并记录，不可用不得谎报。
- **FR-6（索引）**：personal-growth/index.md（束数 2→3、导航表+阅读路径+toctree）、sheke/index.md（域计数）、bundles/index.md（total_bundles 574→575、sheke 45→46/组计数、mermaid 图与导航表、toctree 不涉及域级新增）五面对账。
- **FR-7（边界）**：bundle index 顶部含性质声明（开源项目导读/非原创医学法律建议/数字时点 2026-09）、版本差提示块；status 与 stale_after 按核验结果设定（建议 stable / 2027-03-31：方法论跨周期有效，计数与法规强时效）。
- **FR-8（语言与格式）**：正文中文、文件名 kebab-case 英文；Mermaid 遵守安全编码（节点文本不写裸特殊字符）；不使用 `file:///`；frontmatter 日期用裸格式（conf.py 钩子兼容）。

## Non-Functional Requirements

- **NFR-1 可审计性**：每个具体声明可在 2 跳内到达信源（正文 → article-source F 行 → 外部 URL/原仓文件）。
- **NFR-2 忠实度**：数字逐字与信源一致（RR/OR/CI/百分比/日期），转述不改变量口径；"说人话"式改写须可识别为改写而非新数字。
- **NFR-3 防过期设计**：所有易变数字（条目数/stars/补贴金额/处罚档次）在句中或表注带"截至 2026-09-XX"时点；提供"回到原仓核对"的明确链接。
- **NFR-4 教程可读性**：concepts 按"事实→机制→导航→应用→使用→迁移"递进，单篇可独立阅读；篇长控制在可教程化范围，03/04 两篇可用表格压缩信息。
- **NFR-5 最小变更**：除新 bundle 与三处索引计数外不改动既有文件内容；不动任何 .agents/ 规范。

## Constraints

- **Technical**：产出在 git submodule `projects/awesome-okf-xs/` 内，遵循 OKF v0.2 与该子项目 frontmatter/toctree 规范；Python 门禁脚本与 invoke 依赖可能未安装（手动等效清单兜底）；JS 渲染站点不可用 WebFetch 深取时回退 browser_use（本次原仓 README/API/raw 文件可取，预计无需）。
- **Business / 合规**：原作 Unlicense（PD 等效，允许引用）、博文 CC BY 4.0（须署名+链接）；引用时标注作者/许可；健康与法律内容加免责声明；不得去除上游署名。
- **Dependencies**：WebSearch/WebFetch/GitHub API 可用；子模块已初始化（已验证可读）。
- **流程**：Spec Mode 五阶段（Specify→Plan→Approve→Implement→Review）；七概念场景 4（R→I→E）+ 强制 V；review.md 仅 Review 阶段创建。

## Assumptions

- A1：原仓 main 分支代表现行权威版本（README 徽章与正文自证 615 条口径一致）。
- A2：博文 mushroom.cv 为善意第三方盘点（其 498 口径与上线三周时间线自洽，stars 2,366 为 9/17 时点，与 9/28 API 的 19,238 构成增长曲线而非矛盾）。
- A3：P0 核验中若个别中文统计（如 2025 蘑菇中毒数据）仅能在原仓引述与疾控通报间建立单链，按"原仓已附官方出处+我们核对到出处存在"标 ✅ 或 ⚠️，不硬编。
- A4：用户已确认四项决策（personal-growth 落位 / 精读+15–25 条 / 无 examples / 仅落盘不提交）。

## Acceptance Criteria

### AC-1：Bundle 结构与 OKF 规范完整（rule）

- **Given**：bundle 落位于 `projects/awesome-okf-xs/doc/bundles/sheke/personal-growth/how-to-live-better/`
- **When**：列目录并读取每个 index.md
- **Then**：存在 index.md、log.md、concepts/index.md + 7 篇概念文档（00–06）、references/index.md + article-source.md + verification.md；不存在 examples/；根 index 与两个子目录 index 均含 toctree 块且条目逐一对应实际文件
- **Pass Condition**：目录树与骨架清单逐文件一致；每个 toctree 条目（排除 `:` 指令行）Test-Path 全部为真
- **Evidence**：目录清单 + toctree 核对记录（写入 log.md 与 review.md）

### AC-2：F 编号双份一致且覆盖关键事实（rule）

- **Given**：spec facts.md 与 bundle references/article-source.md
- **When**：用正则 `^\|\s*F-(\d{3})\s*\|` 分别提取两份编号集合
- **Then**：两集合相等、从 F-001 连续无跳号（跳号须有显式注记）；FR-2 的 P0 九类声明在 facts.md 中均有对应 F 行
- **Pass Condition**：集合比对零差异；P0 清单逐项可在 facts.md 定位
- **Evidence**：比对输出（编号计数+差集）附入 verification.md/log.md

### AC-3：P0 核验闭环（rule）

- **Given**：FR-2 的 P0 清单
- **When**：逐项检索权威源（NEJM/Cochrane/JAMA/China CDC Weekly/WHO/NHTSA/GitHub API/原仓文件）
- **Then**：verification.md 给出每项 ✅/⚠️/❌ 结论、权威 URL、与博文/原仓口径的差异；版本演进类差异（498→615 等）单列"版本演进对照"而非混作勘误；❌/⚠️ 项在 bundle 正文呈现核验后口径
- **Pass Condition**：P0 清单每项有结论与外部信源（无法外部核验项明确标"仅原仓/博文单源"，数量与原因可见），无硬编 URL
- **Evidence**：verification.md P0 总表 + 正文落点抽查

### AC-4：三级索引接入与计数同步（rule）

- **Given**：新增 1 个 bundle
- **When**：读取 personal-growth/index.md、sheke/index.md、bundles/index.md
- **Then**：personal-growth total_bundles=3 且 toctree 含 how-to-live-better/index；sheke 域束数 45→46（含其 index frontmatter/正文/图）；bundles/index.md total_bundles=575、sheke 计数与 mermaid/导航表一致
- **Pass Condition**：五面（frontmatter total_bundles / 计数行 / 域节标题束数 / 分组表束数列 / toctree）三角对账无差异
- **Evidence**：计数前后对照（ gates.bundles 输出或手工对账记录）

### AC-5：链接、编码与卫生门禁（rule）

- **Given**：全部新增/修改 .md
- **When**：执行手动等效验证
- **Then**：UTF-8 strict 无乱码；Markdown 相对链接逐一可达；零 `file:///`；零家目录绝对路径；无 `.temp/` 引用
- **Pass Condition**：清单逐项打勾并在 log.md 留痕（gates 不可用时显式注明"手动等效验证"）
- **Evidence**：log.md 门禁段

### AC-6：边界与时效声明落实（rule）

- **Given**：bundle 根 index 与 06-boundaries-and-method.md
- **When**：检查声明内容
- **Then**：含"非医学/法律建议、重大决策咨询专业人士"声明；易变数字带 2026-09 时点；C 级/TODO/争议条目机制有说明；三镜像与原仓的关系及滞后性有交代；frontmatter 含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources（sources 同时列四个用户 URL + 原仓 + 权威核验源）
- **Pass Condition**：声明要素逐项可指认
- **Evidence**：index.md/06 篇/frontmatter 片段

### AC-7：精选条目的忠实与克制（rule）

- **Given**：04-high-value-entries.md
- **When**：逐条核对
- **Then**：精选条目数量在 15–25 条；每条含原作六要素（成本/说人话/收益/证据级/来源/备注中的争议或限制）；数字与原仓/镜像一致且挂 F 编号；不出现"全书 615 条皆然"式的超出处范围断言；明确指向在线版阅读全文
- **Pass Condition**：数量在区间内；抽查 5 条数字与信源逐字一致；无全书搬运
- **Evidence**：条目计数表 + 抽查记录

### AC-U1：教程教学质量（rubric）

- **Type**：rubric
- **Dimension**：教程链路（是否能让一个未读过原作的人理解框架→会查会用→能迁移）
- **Scale**：1–5
- **Anchors**：1 = 资料堆砌/读不懂框架；3 = 信息完整但需自行串联；5 = 七篇形成"事实→机制→导航→应用→使用→迁移"清晰学习路径，示例真正教会方法
- **Pass Threshold**：≥ 4
- **Evidence**：独立评审通读意见

### AC-U2：事实与观点分层质量（rubric）

- **Type**：rubric
- **Dimension**：可信度表达（事实/作者观点/核验事实分层，数字时点与口径标注）
- **Scale**：1–5
- **Anchors**：1 = 观点混入事实、数字无时点；3 = 主要分层正确但偶有混淆；5 = 全文每条断言层级清晰，版本时点/口径限定/争议反方齐备
- **Pass Threshold**：≥ 4
- **Evidence**：独立评审抽查 + verification.md 对照

## Open Questions

- 无阻塞性开放问题（四项关键决策已由用户确认）。实施中若 P0 出现"核心声明❌"（如低钠盐 RCT 数字对不上），按技能 flagged 管理：frontmatter `status: flagged` + 顶部明示，并在通知用户后继续；非核心失败保持 stable。
