# 金融经济通识 OKF 知识包 - Product Requirements Document

## Overview

- **Summary**：以七概念方法论 R→I→E→V→C 全链路，对「金融经济」做系统性调研与知识化，在 `projects/awesome-okf-xs/doc/bundles/sheke/finance/` 下新增 OKF v0.2 知识束 `financial-economics/`。束内包含 11 篇概念文档、4 篇可复算例、1 份事实清单（104 条 F 编号、43 个 S 编号信源）、1 份核验报告、1 份洞察文档、根索引与更新日志，并完成分组、域、总索引三级注册。
- **Purpose**：把「金融是什么、货币如何创造、利率如何定价、银行与市场如何运转、宏观政策如何传导、风险与危机如何形成、中国金融体系如何监管、数字金融改变了什么」整理为一条可顺序阅读、可交叉检索、可事实核查的中文学习路径，补齐 `sheke/finance` 分组仅有个人理财与防骗、缺少金融经济总体框架的空白。
- **Target Users**：零基础但希望系统理解金融经济的自学者；需要宏观与金融框架的职场人、产品与运营从业者；准备阅读财经新闻、政策文件与公司财报的读者；已完成 `personal-investing` 并希望理解其宏观背景的投资者。

## Goals

- 用 11 篇概念文档构成「总论 → 货币 → 利率 → 机构 → 市场 → 宏观 → 货币政策 → 国际金融 → 风险危机 → 中国体系 → 数字金融 → 金融素养」的完整认知链。
- 用 4 篇示例提供可复算的教学算例：货币乘数、现值与债券定价、组合风险与 CAPM、杠杆与挤兑推演；全部标注教学假设，不构成投资建议。
- 建立 104 条 F 编号事实与 43 个 S 编号信源的双层溯源：理论事实挂教科书与经典论文，制度事实挂中国官方文件与国际组织标准。
- 对时效敏感内容（监管架构、统计口径、政策工具、加密资产监管）显式标注时点与边界，不写死易变数字，不以单年数据冒充长期规律。
- 与既有 `sheke/finance/personal-investing` 形成分工：本束讲「系统如何运转」，该束讲「个人如何决策」，两束互链。
- 通过 `scripts/check-bundles-index.py`、`scripts/check-toctrees.py` 与 UTF-8 手动核验；索引计数以目录树地面真值为准。

## Non-Goals

- 不提供投资建议、不推荐任何股票/基金/债券/加密资产/金融机构产品，不预测利率、汇率、股价或经济增速。
- 不复制实时行情、实时统计数据库或付费报告正文；不承诺任何数据的实时性。
- 不新增静态图片资产，保持纯文本知识包。
- 不修改 `.agents/`、`doc/conf.py`、既有 bundle 正文；只新增本束并最小化修改三处索引。
- 不执行 git commit / push；提交待用户显式指令。
- 不对中国金融政策作规范性评价；涉及争议议题时并列主要观点与证据边界。

## Background & Context

- 用户指令：`/七概念 全面调研和学习"金融经济"，生成 okf wiki 教程到 D:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles 恰当位置`。
- 内容敏感度预检：公开知识（教科书、官方统计与监管文件、国际组织标准）→ 标准工作流；规划区 `.trae/specs/financial-economics-okf-wiki/`，产出物入 `projects/awesome-okf-xs/doc/bundles/sheke/finance/financial-economics/`。
- 归属判定：`sheke/finance` 分组已有 `personal-investing`（个人理财）、`pipeline-story`（收入管道）、`ponzi-scheme`（庞氏骗局），均属「金融」主题但缺少金融经济总体框架；本束作为该分组的通识底座，不新建分组（避免单束新建分组的碎片化）。
- 结构样板：`sheke/finance/personal-investing/`（8 concepts + 3 examples + references + facts/insights/log/index，46 条事实、S1–S18 信源、stable、stale_after、根 toctree 直引 references 文件）。本束沿用其文档气质，但补上 `references/index.md` 并采用 11+4 的更完整结构。
- 信源距离：教科书与经典论文属「学术一手/权威综述」，官方统计与监管文件属「机构一手」，国际组织标准属「标准一手」；三者均非厂商自宣，无需按营销数据降权，但仍须区分「定义/恒等式」与「经验估计/争议观点」。

## Functional Requirements

- **FR-1**：新增 `sheke/finance/financial-economics/`，含 `index.md`、`log.md`、`facts.md`、`insights.md`、`concepts/`（`index.md` + `00`–`10` 共 11 篇）、`examples/`（`index.md` + `01`–`04` 共 4 篇）、`references/`（`index.md` + `01-classics-and-authorities.md` + `02-verification.md`）。
- **FR-2**：每篇概念文档遵循「是什么 → 机制/框架 → 关键数字与算例 → 常见误读 → 与其他篇的关系 → 小结」的稳定骨架；正文 H2 起，H1 仅一处；事实引用使用 F 编号。
- **FR-3**：`facts.md` 按 12 个主题小节登记 F-001–F-104，每条含事实内容与 S 编号；日期、比率、制度安排、统计口径标【P0】；文末含 S1–S43 信源登记表、口径说明与放弃核验清单。
- **FR-4**：`references/02-verification.md` 记录 P0 核验结果、勘误/口径差异、单源项、时效边界与未核验项，禁止把未核验项写成已核验。
- **FR-5**：`insights.md` 固化 6 条四元组洞察（现象/根因/影响/建议），每条引用至少 3 个 F 编号；概念正文只消费洞察，不另造与事实冲突的判断。
- **FR-6**：4 篇示例均给出公式、假设、逐步算术、结果解释与边界提醒；不使用真实产品、真实个人或真实机构数据。
- **FR-7**：三级索引注册——`sheke/finance/index.md`（total_bundles 3→4、导航表、阅读路径、toctree）、`sheke/index.md`（域计数与 finance 组行）、`bundles/index.md`（total_bundles、sheke 域计数、finance 组行、Mermaid 概览）。
- **FR-8**：根 `index.md` 含快速导航、分读者快速开始、知识包立场表、推荐学习路径与 `{toctree}`；`concepts/index.md`、`examples/index.md`、`references/index.md` 均含 `{toctree}`。
- **FR-9**：`log.md` 以 `YYYY-MM-DD` 倒序记录 R→I→E→V 全程、核验结论、索引计数与已知边界。
- **FR-10**：与 `personal-investing`、`ponzi-scheme`、`digital-economy/digital-asset` 建立主题互链，说明分工而非重复。

## Non-Functional Requirements

- **NFR-1**：全中文（机构名、文件号、专有名词保留原文）；文件名 kebab-case 纯英文；无中文文件名。
- **NFR-2**：frontmatter 与样板束同构：根 `type: OKF` + `okf_version: "0.2"` + `version` + `sources` + `generated` + `verified` + `status` + `stale_after`；概念 `type: Concept`；示例 `type: Example`；事实 `type: Facts`；洞察 `type: Insights`。
- **NFR-3**：UTF-8 无 BOM、无乱码；相对链接全部可达；无 `file:///`、无本机绝对路径。
- **NFR-4**：时效边界——理论框架 `stale_after: 2027-12-31`；中国监管与数字金融细节在正文标注「以官方最新发布为准」。
- **NFR-5**：不写死易变统计值；必须引用规模/比率时，用「区间/量级/口径」表述并注明时点，避免制造过期硬数字。
- **NFR-6**：公式使用纯文本行内表达或独立公式块，不使用伪代码数学；变量名与单位在首次出现处解释。

## Acceptance Criteria

1. `financial-economics/` 目录文件数与 FR-1 一致，所有 index 的 toctree 条目均指向存在文件。
2. `facts.md` 的 F 编号连续无跳号（F-001–F-104），每条均有 S 编号；`references/02-verification.md` 覆盖全部 P0 主题。
3. 全部概念与示例引用的 F 编号都存在于 `facts.md`；无 F 编号之外的硬数字。
4. 三级索引计数与目录树一致：总束数 +1、sheke 束数 +1、finance 组束数 +1。
5. `python scripts/check-toctrees.py` 与 `python scripts/check-bundles-index.py` 通过；若不通过，修复至通过或在 log 中记录不可用原因与手动等效结果。
6. 全库新增/修改 Markdown 通过 UTF-8 严格解码；相对链接逐一可达。
7. 无投资建议、无产品推荐、无收益承诺、无市场预测；示例均标注教学假设。

## Risks & Mitigations

- **风险：主题过宽导致每篇变浅**。缓解：以「机制 + 一个可算例 + 一个常见误读」为每篇最低交付，宁可少写背景故事。
- **风险：中国监管细节快速过期**。缓解：只写架构与已生效的里程碑，不写具体窗口指导；stale_after + 官方最新口径提示。
- **风险：宏观争议被写成定论**。缓解：财政乘数、QE 效果、金融化、EMH 等标注「经验估计/学界争议」，事实与观点分层。
- **风险：与 personal-investing 重复**。缓解：本束不写产品选择与个人配置比例，只写系统机制；个人决策统一回链该束。
