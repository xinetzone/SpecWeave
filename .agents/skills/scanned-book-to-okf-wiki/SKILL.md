---
name: scanned-book-to-okf-wiki
version: 2.0.0
description: "当用户提供扫描版（纯图像无文本层，或扫描图+内嵌噪声 OCR 层的混合型）版权书籍/内部培训材料/付费报告，要求转为教程、知识包、Wiki 类知识提炼产出，或用户提到'扫描版书籍转教程'、'书转Wiki'、'摘要替代转录'时，必须使用此技能。提供六工序工作流：route 决策前置→文本层可信度判定与逐章通读→深度摘要→原创改写→合规声明契约化→V 审查实证对账，聚合 rules/checklists/templates/模式四处既有资产。不要默认 OCR 逐字转录，也不要轻信内嵌 OCR 文本层——本Skill封装了版权合规与可审计决策门。"
argument-hint: "<扫描版书籍或材料路径，如：playground/<project>/source/xxx.pdf>"
user-invocable: true
paths:
  - ".agents/rules/content-sensitivity-precheck.md"
  - ".agents/checklists/"
  - ".agents/templates/"
  - "playground/"
title: "Scanned-Book-to-OKF-Wiki 扫描版书籍转教程工作流门面 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/scanned-book-to-okf-wiki/SKILL.toml"
---
# Scanned-Book-to-OKF-Wiki 扫描版书籍转教程工作流门面 Skill

> ⚠️ **本Skill是工作流门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（触发词+六工序+质量门+安全清单）
> - L2：实战案例见案例 1 `playground/pipeline-parable/retrospective/retrospective-2026-09-11-pipeline-parable-v1.md`（私域，财商寓言/纯图像 PDF）与案例 2 `playground/the-magic/`（私域，练习册/扫描图+噪声 OCR 混合型 PDF；复现报告与对账台账在 `playground/the-magic/retrospective/`）

## 1. Skill ID
`scanned-book-to-okf-wiki`（内部ID，对外名称：**扫描版书籍转 OKF Wiki 教程工作流**）

## 2. 功能描述

将扫描版（纯图像无文本层，或扫描图+内嵌噪声 OCR 层的混合型）版权材料经"摘要替代转录"路线转化为合规的教程/知识包/Wiki 产出，六工序：

| 工序 | 名称 | 关键动作 | 配套资产 |
|------|------|---------|---------|
| S0 | route 决策前置 | 显式二选一：逐字转录 / 深度摘要（默认摘要），写入 frontmatter `route` 字段与决策时间戳 | [content-sensitivity-precheck.md](../../rules/content-sensitivity-precheck.md) 附加条款 |
| S1 | 文本层判定 + 逐章多模态通读 | **混合型 PDF 先抽查内嵌文本层错字率判定可信度**：不可信则降格为章节定位工具（配合内嵌目录锚点），内容以渲染页图像为准，策略写入 frontmatter（如 `ocr_layer_policy: image-first-ocr-locate-only`）；按章/练习单元通读扫描页，捕捉论证链，建立 PDF 物理页↔印刷页映射规则 | — |
| S2 | 深度摘要 | 重构"论点→论据→结论"（练习册类重构"步骤→口令→边界"），非书摘集；frontmatter 含 `source` 溯源 | — |
| S3 | 原创改写重构 | 情节/数据/论证转述重组；通过"换个说法"测试（无连续 ≥30 字原文复现）；自助/灵性类材料另做"作者主张 vs 客观事实"分层 | — |
| S4 | 合规声明契约化 | index 三段式声明：可度量标准 + 溯源方式 + 使用边界；计数类条款必须带计数口径（标点是否计入、占位符句式/通用口令/专名的排除项清单） | [引用红线声明模板](../../templates/citation-redline-declaration-template.md) |
| S5 | V 审查实证对账 | 引用字数逐条实际统计（含中间摘要内嵌数字回渲染图核验），验证声明与实际一致 | [声明对账清单](../../checklists/declaration-reconciliation-checklist.md) |

> **为什么用本Skill而非默认 OCR？** 逐字转录物本身即高侵权风险衍生物，无法入 `docs/`；"深度摘要 + 原创改写"在合规性与信息保真度上同时占优。完整性是负债，可溯源的转述才是资产。

## 3. 何时使用本技能

当任务满足以下任一条件时触发：
- 源材料为扫描版的商业出版物、内部培训材料、付费报告，含两种形态：①纯图像、无文本层；②**扫描图 + 内嵌 OCR 文本层的混合型**（文本层常为低质量噪声 OCR，须先做可信度判定，不可直接信）
- 任务目标为教程、知识包、结构化摘要等知识提炼产出，非全文存档
- 用户提到"扫描版书籍转教程"、"书转Wiki"、"摘要替代转录"

> **不适用**：源材料自带**可信**文本层且为公开/开源内容（直接走标准工作流）；全文存档需求（转录路线须附理由并经用户显式确认，默认不批准）。注意："有文本层"不等于"文本层可信"——错字密集的内嵌 OCR 仍按扫描版路线处理。

## 4. 核心步骤

1. **敏感度预检**：按 [content-sensitivity-precheck](../../rules/content-sensitivity-precheck.md) 判定级别；扫描版版权材料默认私域工作流（产出入 `playground/` 或用户指定目录，跳过 `.trae/specs/`）
2. **S0 route 决策**：任务 frontmatter 写入 `route: chaptered-summary`（默认）或 `route: verbatim-transcription`（须附选择理由 + 用户确认）及决策时间戳；禁止隐式执行
3. **S1 文本层判定**：抽取若干页检查内嵌文本层质量（错字率、缺字、串行）；可信才解析文本层，不可信一律图像为准、OCR 仅定位，策略字段（如 `ocr_layer_policy`）写入 frontmatter；随后逐章/逐练习单元多模态通读，建立页码映射规则
4. **S2–S3 执行**：深度摘要 → 原创改写；摘要 frontmatter 含 `source` 溯源；涉及主观功效/玄学主张时正文做主张分层并保留健康/财务边界声明
5. **S4 声明**：产出物 index 复制引用红线声明模板三段式，数字全部来自实际统计（非写作印象），并写明计数口径与排除项
6. **S5 对账**：按声明对账清单核验声明与事实一致（字数 / 条数 / 页码逐条实证）；**中间摘要里的字数等数字标注同样必须回渲染图核验后才能进最终声明**
7. **闭环**：产出物相对链接核验（check-links.py）；独立复现案例按 [L2 案例复现检查清单](../../checklists/scanned-book-to-okf-wiki-reproduction-checklist.md)（门面层）+ [A-005](../../checklists/summary-over-transcription-reproduction-checklist.md)/[A-006](../../checklists/compliance-contracting-reproduction-checklist.md) 复现清单（模式层）留证，双清单全过后按主权区治理门申请成熟度升级

## 5. 质量门

- **G1**：route 决策在 R 阶段第一步完成且 frontmatter 可审计（禁止事后补记）；混合型 PDF 另须有文本层策略字段
- **G2**：摘要为重构论证链/操作规程的独立分析物，非金句摘抄集
- **G3**：产出无连续 ≥30 字原文复现；直接引用均 ≤30 字且逐条标注 PDF 物理页页码；计数口径与排除项在契约中点名
- **G4**：index 声明数字与全文实际统计一致（含中间摘要数字回图核验；声明对账通过后才算定稿）

## 6. Gotchas（陷阱与反直觉行为）

- **默认 OCR 是最大陷阱**："转录越完整越好"对版权材料不成立——逐字转录物即高侵权风险衍生物，完整性是负债
- **内嵌噪声 OCR 层是第二陷阱（v2.0.0 新增，案例 2）**：混合型 PDF"有文本层"会诱导跳过图像通读直接信文本；噪声 OCR（如"被"识别成"㻛"）把错字当原文进入摘要即事实污染。必须先抽查错字率判定可信度，不可信则图像为准、OCR 与内嵌目录仅用于章节定位
- **声明数字禁凭印象填写**：写作时作者并不掌握全文实际统计状态，S4 数字必须 S5 实测回填；先写声明后产出是反模式
- **中间摘要的数字同样不可信（v2.0.0 新增，案例 2）**：摘要写作时随手标的引语字数误差率实测 9/19；不回渲染图核验就搬进最终声明，S5 必然返工
- **摘要勿退化为书摘集**：金句摘抄汇编仍是衍生复制，原创性不成立则合规红线失守
- **route 禁隐式执行**：不记录决策即开工 = 流程违规，任务看似完成但决策不可审计，下个同类任务会滑回 OCR 路线
- **混合路线不可声明**：部分章节转录、部分章节摘要导致引用红线声明无法全覆盖，契约名存实亡
- **练习册体裁先定计数口径（v2.0.0 新增，案例 2）**：28 天同构练习含大量操作口令（"谢谢"反复出现）与占位符句式模板，"≤30 字、共 N 条"不定义口径就无法复核；须在契约中点名排除项（占位模板/通用口令/专名）
- **主张分层是版权之外的第二红线（v2.0.0 新增，案例 2）**：自助/灵性类材料的吸引力法则因果承诺、科学类比、健康功效不能转述成客观事实，一律标注"作者主张"，并保留"配合正规医疗/营养"限定与非理财建议边界
- **页码体系可能双轨（v2.0.0 新增，案例 2）**：正文用 PDF 物理页、书末速查表用纸质印刷页码且偏移递增；引用页码规则必须在 S1 显式统一并在契约溯源段写明

## 7. 关键参考

| 参考 | 路径 | 用途 |
|------|------|------|
| 内容敏感度预检 + route 附加条款 | [../../rules/content-sensitivity-precheck.md](../../rules/content-sensitivity-precheck.md) | S0 级别判定与决策 |
| **Skill L2 案例复现清单** | [../../checklists/scanned-book-to-okf-wiki-reproduction-checklist.md](../../checklists/scanned-book-to-okf-wiki-reproduction-checklist.md) | 第 2 案例门面层留证与升 L2 判定 |
| 复现检查清单（A-005） | [../../checklists/summary-over-transcription-reproduction-checklist.md](../../checklists/summary-over-transcription-reproduction-checklist.md) | 第 2 案例模式层留证 |
| 声明对账清单（A-001） | [../../checklists/declaration-reconciliation-checklist.md](../../checklists/declaration-reconciliation-checklist.md) | S5 核验 |
| 引用红线声明模板（A-002） | [../../templates/citation-redline-declaration-template.md](../../templates/citation-redline-declaration-template.md) | S4 声明 |
| 模式：摘要替代转录（L2） | [../../../docs/retrospective/patterns/methodology-patterns/summary-over-transcription.md](../../../docs/retrospective/patterns/methodology-patterns/summary-over-transcription.md) | 六工序依据（已入库，案例 1+2 验证） |
| 模式：合规契约化（L2） | [../../../docs/retrospective/patterns/methodology-patterns/compliance-contracting.md](../../../docs/retrospective/patterns/methodology-patterns/compliance-contracting.md) | S4 依据（已入库，案例 1+2 验证） |
| 模式：声明对账（L2） | [../../../docs/retrospective/patterns/documentation-patterns/declaration-reconciliation.md](../../../docs/retrospective/patterns/documentation-patterns/declaration-reconciliation.md) | S5 依据 |
| 实战复盘（案例 1 全记录） | [../../../playground/pipeline-parable/retrospective/retrospective-2026-09-11-pipeline-parable-v1.md](../../../playground/pipeline-parable/retrospective/retrospective-2026-09-11-pipeline-parable-v1.md) | 案例 1（财商寓言/纯图像 PDF） |
| 案例 2 复现报告与台账 | [reproduction-report-summary-over-transcription.md](../../../playground/the-magic/retrospective/reproduction-report-summary-over-transcription.md)（同目录另含 A-006 复现报告与 s5-reconciliation-ledger.md） | 案例 2（练习册/混合型 PDF）：双复现报告 + S5 对账台账 |

## 8. 执行日志（CMD-LOG）

按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=scanned-book-to-okf-wiki`，session 前缀 `sc-YYYYMMDD-<book>`
- 核心事件：`ROUTE_DECIDED`、`CHAPTER_READ`、`SUMMARY_DRAFTED`、`REWRITE_COMPLETED`、`CONTRACT_DECLARED`、`RECONCILIATION_PASSED`、`WIKI_COMPLETED`

## 9. Changelog

- **v2.0.0** (2026-09-11): 第 2 独立案例《魔力》（sc-20260911-the-magic，170 页练习册，扫描图+噪声 OCR 混合型）复现通过后重大升级：①启用条件与 S1 工序覆盖"混合型 PDF"，新增文本层可信度判定（`ocr_layer_policy` 留证）；②S4 增加计数口径与排除项要求，S3 增加主张分层；③G3/G4 增强（PDF 物理页、中间摘要数字回图核验）；④Gotchas 新增 5 条（噪声 OCR 层、中间数字不可信、练习册计数口径、主张分层第二红线、双轨页码）；⑤两配套模式升 L2 入库 docs 模式库，§7 链接改指入库版本；⑥参考表登记案例 2 复现报告。
- **v1.0.1** (2026-09-11): 配套 [L2 案例复现检查清单](../../checklists/scanned-book-to-okf-wiki-reproduction-checklist.md) 落盘，§4 第 6 步与 §7 参考表同步登记（门面层与模式层双清单机制）。
- **v1.0.0** (2026-09-11): 初始版本。萃取自扫描版《管道的故事》→ OKF Wiki 教程任务链里程碑复盘（sc-20260911，场景4 R→I→E），聚合 A-001~A-006 六项行动项固化的 6 处资产（规则附加条款、2 清单、3 模板、2 L1 模式、1 L2 模式）。
