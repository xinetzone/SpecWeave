# 数字经济与数字资产 OKF 教程束 - Product Requirements Document

## Overview

- **Summary**：以七概念方法论 R→I→E→V→C 全链路，对「数字经济」与「数字资产」两大主题做公开信源全面调研，在 `projects/awesome-okf-xs/doc/bundles/sheke/digital-economy/` 下新增 1 个分组、2 个 OKF v0.2 知识束：束 1 `digital-economy/`（数字经济：定义谱系·测度口径·数字产业化·产业数字化·数据要素·平台经济·规模数据·治理·争议），束 2 `digital-asset/`（数字资产：概念谱系·数据资产入表·数据确权·数据交易·加密资产·稳定币·数字人民币·NFT/数字藏品·RWA/DeFi·合规红线）。产出 41 个 Markdown 文件（含两份 facts.md、两份 insights.md、两份 references 信源台账），并完成三级索引注册与计数对账。
- **Purpose**：把「数字经济是什么、规模多大、怎么测度、政策怎么管」与「数字资产有哪些形态、哪些合法、边界在哪」从零散的政府文件、行业报告与新闻中沉淀为可审计、可溯源、可迭代的中文教程；对高时效、多口径、强监管的主题建立「官方口径优先 + 双源核对 + 口径冲突显式留痕」的知识组织范式。
- **Target Users**：关注数字经济政策与产业格局的读者、企业数字化/数据合规从业者、数据分析与政策研究者、需要辨析「数字资产≠加密货币」的普通读者。

## Goals

- 覆盖 `sheke`（社会科学）域既有 8 组未触及的空白主题：数字经济与数字资产（现仅有 `finance` 个人理财、`industry` AI 行业趋势）。
- 两束各 ≥50 条 F 编号事实、各 ≥15 个 S 编号信源，其中规模/政策/法规类事实标记【P0】并完成双源核对；信源以中国官方（国家数据局、国家统计局、中国信通院、国务院、发改委、财政部、人民银行、网信办）与国际权威（OECD、IMF、BIS、UNCTAD、World Bank）为主。
- 对测度口径冲突（信通院核算框架 vs 国家统计局《数字经济及其核心产业统计分类（2021）》vs OECD/IMF 国际口径）、监管分歧（中国境内全面禁止 vs 香港/欧盟/美国牌照化）在 facts.md 或正文显式留痕，不做静默调和。
- 结构与 frontmatter 与同域成熟束 `sheke/finance/personal-investing/` 对齐；通过 awesome-okf-xs 两大门禁（`check-bundles-index.py`、`check-toctrees.py`）、Sphinx dummy 构建与 UTF-8 门禁。
- 完成三级索引注册（分组 index → 域 index → bundles 总索引），总索引 5 面对账一致。**计数基线说明（2026-10-17 V 门澄清）**：立项时总索引为 `total_bundles: 641`、`groups: 61`、sheke 域节标题「69 束 · 8 组」；实施期间并行会话在 sheke/industry 组新增 1 束，使基线变为 642/61/「70 束 · 8 组」；本变更在其上 +2 束 +1 组，最终以目录树地面真值为准——`total_bundles: 644`、`groups: 62`、sheke 域节标题「72 束 · 9 组」、sheke 分组表新增 1 行束数 2、末尾 toctree 仍为 9 域。

## Non-Goals

- 不执行任何 git commit（awesome-okf-xs 为 git submodule，提交待用户显式指令）；不改动子项目 `.agents/` 规范、`tasks/`、`scripts/`、`doc/conf.py`。
- 不新增静态图片资产（`doc/_static/`）——本轮保持纯文本知识包，不引入 hero 图。
- 不做方法论模式库入库（`docs/retrospective/patterns/`）与 `.agents/` 主权区资产落盘；如需另行发起。
- 不做投资/理财建议，不推荐任何具体加密资产、交易平台、数据交易所或数据产品；不预测数字资产价格与市场走势。
- 不采集私域内容（付费报告全文、需登录访问的行业数据库），不逐字转录受版权保护的商业报告正文；只做公开口径的事实登记与原创改写。
- 不做数字经济测度的独立量化复现（不重算规模数据），不运行链上数据抓取。
- 不生成 DOCX/PDF/HTML 形态产出物。

## Background & Context

- 用户 `/spec` 指令：`Use Skill: seven-concepts-cmd` 全面调研数字资产、数字经济，生成 okf wiki 教程到 `doc/bundles` 的恰当位置。
- 内容敏感度预检：公开内容（政府公开文件、公开行业报告、开源知识）→ 标准工作流；规划区 `.trae/specs/digital-economy-okf-wiki/`，产出物入 `projects/awesome-okf-xs/doc/bundles/sheke/digital-economy/`。
- 定位决策（用户 2026-10-17 确认）：新增 `sheke/digital-economy` 分组（社会科学域，与 `finance`、`industry` 平级）；拆 2 束（`digital-economy` + `digital-asset`）；信源口径为「官方口径优先 + 双源核对」。
- 目录树既有布局：域（`sheke/index.md`）→ 组（`sheke/<group>/index.md`）→ 束（`<group>/<bundle>/`，含 `index.md`/`log.md`/`facts.md`/`insights.md`/`concepts/`/`examples/`/`references/`）。分组名与束名同名（`jishu/rust/rust/`、`jishu/build/cmake/cmake/`）在本仓库为既有惯例。
- 门禁机制：`scripts/check-bundles-index.py` 以目录树为地面真值，对总索引 7 项边对账（frontmatter 计数 / 正文计数行 / 域节标题 / 分组表束数列 / 表内链接可达 / 组注册覆盖 / 末尾 toctree）；`scripts/check-toctrees.py` 校验零断链、零孤立内容、bundle 根 `index.md` 完整。
- 样板束：`sheke/finance/personal-investing/`（8 concepts + 3 examples + 1 references + facts/insights/log/index，46 条事实、S1–S18 信源、`status: stable`、`stale_after`、`{toctree}` 直引 references 文件）。
- 子模块边界：`projects/awesome-okf-xs/` 为第一方 git submodule，本轮工作时直接在其工作树内写入 bundle 文件（与既往 okf-wiki 任务一致），但**不 commit**，遵循子项目流程。

## Functional Requirements

- **FR-1**：新增分组目录 `sheke/digital-economy/`，含分组 `index.md`（frontmatter `okf_version: "0.2"` + `type: group` + `title` + `description`；正文含收录原则、知识包导航表（含束数列）、阅读路径与 `{toctree}`）。
- **FR-2**：束 1 `sheke/digital-economy/digital-economy/` 含 20 个 Markdown 文件：`index.md`、`log.md`、`facts.md`、`insights.md`、`concepts/`（`index.md` + `00`–`09` 共 10 篇）、`examples/`（`index.md` + `01`–`03` 共 3 篇）、`references/01-sources-and-authorities.md`。
- **FR-3**：束 2 `sheke/digital-economy/digital-asset/` 同上结构 20 个文件，正文主题为数字资产谱系、数据资产入表与确权、加密资产/稳定币/数字人民币/NFT/RWA 与合规红线。
- **FR-4**：每束 `facts.md` 登记 `F-001` 起编号事实（≥50 条，分 6–7 个主题小节），每条含事实内容与 S 编号信源引用，规模/政策/法规类标记【P0】；文末含「信源登记表（S1–Sn，≥15 个）」与「放弃核验清单」；口径冲突在事实行内或独立勘误段留痕。
- **FR-5**：每束 `insights.md` 冻结 6 条四元组洞察（现象 / 根因 / 影响 / 建议），每条引用 ≥3 个 F 编号；正文（E 阶段）只消费洞察，不新造判断。
- **FR-6**：每束 `references/01-sources-and-authorities.md` 按「中国官方 / 国际权威 / 学术与行业」三层登记信源，含发布机构、文件号或报告名、日期与官方链接。
- **FR-7**：三级索引注册——分组 `sheke/digital-economy/index.md`、`sheke/index.md`（描述、方向条目、分组导航表、`{toctree}`）、`doc/bundles/index.md`（frontmatter 计数、正文计数行、sheke 域节标题、sheke 分组表行）；三处 toctree 链完整可解析。
- **FR-8**：每束根 `index.md` 含「快速导航（概念/示例/信源/工作文档）」「快速开始（分读者路径）」「知识包立场表」「推荐学习路径」与 `{toctree}`；每束 `log.md` 以 `YYYY-MM-DD` 倒序记录 R→V 全程。

## Non-Functional Requirements

- **NFR-1**：全束中文（机构名、文件号、专有名词保留原文）；正文只用 `##` 起标题（H1 仅 frontmatter 后一处）；束内交叉引用**优先**使用 `/`-根路径（相对 bundle 根）；无 `file:///`、无 `.temp/`/`.spec/` 引用。**相对路径澄清（2026-10-17 C 门澄清）**：`concepts/index.md`、`examples/index.md`、`references/*` 等**同目录清单/台账类文件**允许使用同级相对路径（与样板束 `sheke/finance/personal-investing` 一致，该束相对同级 92 处、`../` 36 处）；概念与示例正文的束内导航仍强制 `/`-根路径。
- **NFR-2**：文件名 kebab-case 纯英文；目录名同上；无中文文件名。
- **NFR-3**：frontmatter 与 `sheke/finance/personal-investing/` 同构：束根 `index.md` 用 `type: OKF`、`okf_version: "0.2"`、`tags`、`version`、`sources`（`resource` 指向束内 `references/` 与 `facts.md`）、`generated`（`by`/`at` 嵌套时间戳）、`status`、`stale_after`；子目录 `concepts/index.md`、`examples/index.md` 不带 frontmatter；`facts.md` 用 `type: Facts`，`insights.md` 用 `type: Insights`。
- **NFR-4**：时效声明——数字经济规模数据与监管条款时效敏感，`stale_after` 设为 `2027-09-30`；束内显式提示「数据与法规以官方最新发布为准」。
- **NFR-5**：数字口径分层标注——「官方发布值」「机构估算值」「第三方测算值」三类不同来源的数字不得混同陈述，须在事实行标注口径来源。
- **NFR-6**：`.agents/` 未修改；除目标 bundle 目录与三处索引文件外，不触碰其他文件。

## Constraints

- **Technical**：Windows 环境；门禁脚本为 stdlib 单文件，须在 `projects/awesome-okf-xs` 工作目录下运行（`python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`）；Sphinx dummy 构建（`sphinx-build -b dummy -E doc _build/dummy`）用于验证 frontmatter 兼容与 toctree 完整性。
- **Business**：不 commit、不 push；不修改子模块内既有 bundle；数字资产部分必须包含合规与风险边界声明，明确区分中国境内监管口径与境外牌照化口径。
- **Dependencies**：`scripts/check-bundles-index.py`、`scripts/check-toctrees.py`、`scripts/check-utf8.py`；样板束 `sheke/finance/personal-investing/`；子模块边界规范 `projects/AGENTS.md`。

## Assumptions

- 分组名 `sheke/digital-economy`、束名 `digital-economy` / `digital-asset` 已经用户确认（2026-10-17）。
- 信源可得性：国家数据局、国家统计局、中国信通院、国务院、人民银行、财政部、网信办、OECD、IMF、BIS、UNCTAD 的公开文件与报告可通过公开检索获取；若个别文件官方页面不可达，则以「官方转载页 + 交叉报道」双源登记并标记为 ⚠️。
- R 阶段登记的原始事实由只读子代理机械采集，V 阶段用全新上下文的只读子代理做机械抽核（覆盖率 ≥10% 且每个概念页 ≥2 条）兜底。
- 「数字经济规模」类数字存在多套口径（信通院白皮书口径、国家统计局核心产业口径、国际比较口径），视为**已知口径冲突**而非待消除错误。
- 本轮不引入图片资产，束根 `index.md` 首屏用文字引言替代 hero 图。

## Acceptance Criteria

### AC-1: 事实可溯源（rule）

- **Type**: `rule`
- **Given**: 两束 `facts.md` 与全部概念/示例正文
- **When**: 检查每条事实性陈述的引用
- **Then**: 每个数字、法规文号、机构结论均可追到 S 编号信源或束内 F 编号；无裸断言
- **Pass Condition**: V 评审机械抽核覆盖率 ≥10%（每概念页 ≥2 条），命中率 ≥98%，P0 级虚构/错引 = 0
- **Evidence**: V 阶段 verification 记录 + `review.md` 对应检查点

### AC-2: 口径冲突显式留痕（rule）

- **Type**: `rule`
- **Given**: R 阶段识别的口径分歧（数字经济测度三口径、数字经济规模占 GDP 比重的年际与口径差异、加密资产监管的中/港/欧/美四方分歧、稳定币储备与脱锚口径）
- **When**: 读者在 `facts.md` 或相关概念页查阅
- **Then**: 每类分歧有独立「口径备注 / 勘误」留痕，给出至少两个出处与采用口径说明
- **Pass Condition**: 四类分歧 4/4 覆盖，且每类 ≥2 个出处
- **Evidence**: `facts.md` 勘误段 + 相关概念页正文 + `review.md` 检查点

### AC-3: 结构与门禁全绿（rule）

- **Type**: `rule`
- **Given**: 41 个文件落盘（分组 1 + 束 2×20）并完成三级索引注册
- **When**: 在 `projects/awesome-okf-xs` 下运行 `python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`、`python scripts/check-utf8.py` 与 `sphinx-build -b dummy -E doc _build/dummy`
- **Then**: 三条门禁 rc=0；dummy 构建 rc=0 且无一条警告来自本分组
- **Pass Condition**: 四条命令输出符合预期并在 `verification` 记录中粘贴证据
- **Evidence**: 命令输出日志 + `review.md` 对应检查点

### AC-4: 教程教学质量（rubric）

- **Type**: `rubric`
- **Dimension**: 概念定义清晰度、知识地图连贯性、跨篇导航有效性、非专业读者可跟读至形成判断
- **Scale**: 1–5
- **Anchors**: 1 = 文件摘录堆砌无叙事；3 = 覆盖定义与制度但跨篇跳跃、概念不作辨析；5 = 每篇含「是什么 / 为什么重要 / 制度与数据现状 / 边界与争议」，概念谱系有辨析、示例可独立走读
- **Pass Threshold**: ≥4
- **Evidence**: C 阶段独立评审打分 + `review.md` 对应检查点

### AC-5: 合规与风险边界（rule）

- **Type**: `rule`
- **Given**: 束 2 `digital-asset/` 全部文件
- **When**: 扫描风险与监管相关表述
- **Then**: ①两束根 `index.md` 含「通识教育、不构成投资建议、不推荐任何产品/平台」声明；②中国境内虚拟货币监管红线逐条登记官方文号与日期；③数字人民币（e-CNY）与加密货币、稳定币的区别在正文明确辨析；④稳定币/NFT/RWA 境外牌照化口径与中国境内口径并列陈述、不混同
- **Pass Condition**: 4/4 满足，0 处推荐性表述
- **Evidence**: 束根 `index.md` + `concepts/05`–`09` 正文 + `review.md` 检查点

### AC-6: 工程纪律（rule）

- **Type**: `rule`
- **Given**: 全部产出 Markdown 文件
- **When**: 机械扫描
- **Then**: 0 处 `file:///`、0 处 `.temp/`/`.spec/` 引用、0 中文文件名、无重复 H1；每个概念/示例文件结尾有束内导航段；`concepts/index.md` 与 `examples/index.md` 均为纯 toctree 索引不带 frontmatter；束内引用一律 `/`-根路径。**跨束引用澄清（2026-10-17 V 门澄清）**：原措辞「0 处 `](../`」经 V 门实测与样板束比对（`sheke/finance/personal-investing` 亦有 36 处同类链接）确认不可行——跨束引用只能使用相对路径；判据修正为「允许 `../` 形式，但必须解析到 `doc/bundles/` 内的真实文件，禁止向上越出 `doc/bundles/` 根」；束内引用仍强制 `/`-根路径。
- **Pass Condition**: 扫描 0 违例
- **Evidence**: V 阶段机械扫描输出 + `review.md` 检查点

### AC-7: 双独立评审收口（rule）

- **Type**: `rule`
- **Given**: 实施完成、队列清空
- **When**: V 门（fresh-context 只读子代理）与 C 门（另一 fresh-context 只读子代理）分别执行
- **Then**: V 的 G1–G5 全过并回填各文件 `verified`；C 门独立评审（自跑门禁、自写枚举器）产出 `review.md`，`fail` 则建 pending issue → 修复 → 复审至 pass
- **Pass Condition**: `review.md` 终态 Result = pass
- **Evidence**: `.trae/specs/digital-economy-okf-wiki/review.md`

## Open Questions

- 无（分组位置、束粒度与信源口径已由用户 2026-10-17 确认）。R 阶段若发现某主题（如数据交易所定价机制）公开官方信源不足，按 Assumptions 的「⚠️ 双源登记」处理，不阻塞交付。
