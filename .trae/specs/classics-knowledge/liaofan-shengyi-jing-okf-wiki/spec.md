---
status: "draft"
name: liaofan-shengyi-jing-okf-wiki
version: 1.0.0
created: 2026-09-08
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（《了凡四训》原文为公共领域古籍；智然《了凡生意经》解读为公开课程实录）
---

# 《了凡生意经》原文+解读 → OKF Wiki 知识包 Spec

## Why

用户希望将《了凡生意经》（智然，2013年企业家研修班课堂实录）的原文层（袁了凡《了凡四训》逐篇原文）与阐释层（智然逐讲解读）系统化整理为 OKF v0.2 规范知识包，沉淀到最高可信度知识库 `projects/awesome-okf-xs/doc/bundles` 的国学分组下，方便后续引用、导航与学术查阅。

## What Changes

- 新增分组：`bundles/guoxue/liaofan/`（了凡体系分组，包含两个子 bundle：原文 + 解读）
  - `bundles/guoxue/liaofan/yuan-liaofan-sijun/`（袁了凡《了凡四训》原文 bundle，收录四篇原文全文 + 分段精读）
  - `bundles/guoxue/liaofan/liaofan-shengyi-jing/`（智然《了凡生意经》解读 bundle，五讲内容全量结构化）
- 更新导航索引：`guoxue/index.md`（新增分组行 + toctree）、`bundles/guoxue/index.md`（新增束导航行 + toctree）
- 遵循 source-code-to-okf-wiki 技能五阶段流程：R（原文信源采集与事实登记）→ I（架构洞察）→ E（批量生成 OKF 文档）→ V（独立验证）→ C（模式沉淀）
- 三层文本分层明确标注：古典层（《了凡四训》原文）/ 经典层（《周易》《尚书》等更早出处）/ 阐释层（智然现代解读）

**关键决策（落位）**：按《guoxue/yangming/》分组逻辑，新建 `liaofan/` 束（人名→经典束），下设两个子 bundle：
- `yuan-liaofan-sijun/`：收录《了凡四训》四篇原文（立命之学、改过之法、积善之方、谦德之效）全文
- `liaofan-shengyi-jing/`：收录智然《了凡生意经》五讲解读全文结构化文本

**关键决策（三层分层）**：
- 古典层（原文）：从维基文库/ctext.org 等权威古籍库逐字获取，双信源核对
- 经典层（引用）：原文中引用的《周易》《尚书》等更早经典原文另立 references 条目
- 阐释层（解读）：显式标注"智然老师阐释"，不伪装为古文原意

## Impact

- Affected specs: `boshu-laozi-wiki`、`yangsheng-bundle-visuals`（仅通过 references/cross-ref.md 交叉引用，不修改其产物）
- Affected code: `projects/awesome-okf-xs`（git submodule，第一方子项目，允许子模块内开发）内 `doc/bundles/guoxue/liaofan/` 新增文件与两处索引更新；提交发生在子模块仓库内
- 不修改任何既有 bundle 内容；不修改 SpecWeave 主仓文件

## ADDED Requirements

### Requirement: 原文忠实性与双源核对

《了凡四训》原文 bundle SHALL 收录四篇（立命之学、改过之法、积善之方、谦德之效）全文，每篇原文 SHALL 经至少两个独立权威信源（维基文库、ctext.org、中华书库等）逐字核对；每处关键异文在 facts.md 登记编号事实与信源 URL，异文登记不改字。

#### Scenario: 原文核对

- **WHEN** 读者对照任一权威底本核查 bundle 中的《了凡四训》原文
- **THEN** 逐字一致（异文处显式标注"某本作某"并给出信源出处）

#### Scenario: 三层文本分层

- **WHEN** 读者阅读任一概念文档
- **THEN** 古典层/经典层/阐释层明确区分，不再被误读为单一文本层

### Requirement: 解读结构化与信源标注

《了凡生意经》解读 bundle SHALL 按五讲（信心·正气·能量 / 谦德之效 / 连根养根 / 立命之学 / 改过之法）分层组织内容，每讲下收录全部小节标题与核心观点摘要；每个观点 SHALL 标注其对应的《了凡四训》原文出处（篇名+段落）。

#### Scenario: 观点溯源

- **WHEN** 读者阅读"立命九法"解读条目
- **THEN** 条目末尾标明出自《了凡四训·立命之学》对应段落，读者可回查原文

#### Scenario: 案例完整性

- **WHEN** 读者阅读"谦德之效的五个案例"解读条目
- **THEN** 五个案例（丁敬宇、杨荣、冯琦父、应大猷等）各有完整叙述与出处标注

### Requirement: OKF 格式与导航完整性

所有新增文档 SHALL 遵循 awesome-okf-xs 规范：OKF v0.2 YAML frontmatter（`type: OKF`、`source`、`generated`/`verified`、`status`、`stale_after`，规范见 `.agents/rules/frontmatter.md`）、bundle 根 index 以 `{toctree}` 引用全部内容文档、Markdown 相对路径交叉引用无断链、正文中文/文件名 kebab-case 纯英文，并通过 `invoke gates.all`（UTF-8 + toctree 完整性）。

#### Scenario: 质量门通过

- **WHEN** 在 `projects/awesome-okf-xs` 运行 `invoke gates.all`
- **THEN** toctrees 与 utf8 检查全部通过，无孤立文档、无断链

### Requirement: 方法论闭环（G1–G3 + V）

教程 SHALL 记录 seven-concepts 场景4 方法论痕迹：facts.md ≥50 条编号事实且无因果推断词（G1）、insights.md ≥3 条带四元组洞察（G2）、≥2 个可复用阅读模式含触发场景/核心步骤/反模式/迁移示例（G3），并在提交前经对抗审查（V）完成原文与事实抽查。

#### Scenario: 事实抽查

- **WHEN** 对抗审查随机抽取 10 条 facts.md 事实核对信源
- **THEN** 全部与登记信源一致，无虚构引证

## MODIFIED Requirements

无（本任务为全新增量；`guoxue/index.md` 与 `bundles/guoxue/index.md` 仅追加统计与导航行，属索引维护而非既有需求变更）。

## REMOVED Requirements

无。

## 开放问题

- 无（三层分层与落位决策已在 spec 中给出；若实现阶段发现原文版本存在无法调和的异文冲突，在 facts.md 登记并列呈现，不作裁决）
