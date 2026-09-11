---
id: "scanned-book-to-okf-wiki-reproduction-checklist"
title: "扫描版书籍转OKF Wiki教程 Skill L2 案例复现检查清单"
source: "skill:scanned-book-to-okf-wiki (v1.0.0) / A-005"
date: "2026-09-11"
type: "checklist"
severity: "high"
tags: ["Skill复现", "L2晋升", "扫描版材料", "版权合规", "工作流门面"]
---

# 扫描版书籍转 OKF Wiki 教程 Skill L2 案例复现检查清单

> 配套 Skill：[scanned-book-to-okf-wiki](../skills/scanned-book-to-okf-wiki/SKILL.md)（v1.0.0，萃取自案例 1《管道的故事》任务链）。
> 与 [A-005 摘要替代转录复现清单](summary-over-transcription-reproduction-checklist.md) 的关系：A-005 管**底层模式步骤**逐步留证，本清单管 **Skill 门面被端到端复用**的证据与升 L2 判定。两清单配合使用，本清单不重复 A-005 的步骤细节。
> 核心原则：门面 Skill 的价值不在步骤罗列而在编排闭环——复现的证据链必须证明"经门面编排"这件事本身成立。

## 🚨 启用条件（全部成立才启用，缺一即为不适用）

- [ ] 源材料为扫描版（纯图像、无文本层）版权材料，且与案例 1（《管道的故事》）不同源、不同主题（独立性要求）
- [ ] 任务经 scanned-book-to-okf-wiki Skill 门面编排（触发词命中或用户显式调用）
- [ ] 任务目标为教程、知识包、Wiki 类知识提炼产出，非全文存档

## 🛡️ 复现步骤（对应 Skill 六工序，逐步留证）

### S0 route 决策前置
- [ ] CMD-LOG 输出 `ROUTE_DECIDED` 事件，任务 frontmatter 含 `route` 字段（非事后补记）
- [ ] 若选逐字转录路线：附选择理由并经用户显式确认（默认摘要路线，默认不批准转录）

### S1–S3 逐章通读 → 深度摘要 → 原创改写
- [ ] 每章摘要 frontmatter 含 `source` 溯源字段与页码映射规则
- [ ] 产出通过质量门 G2（重构论证链的独立分析物，非书摘集）与 G3（无连续 ≥30 字原文复现）
- [ ] 步骤级留证对照 A-005 步骤 2–4 逐项执行（本清单不重复其细节）

### S4 合规声明契约化
- [ ] 产出物 index 声明使用引用红线声明模板三段式（标准 + 溯源方式 + 使用边界）
- [ ] 声明数字标注来源：实测回填或"写作估计待 S5 实测回填"（禁凭印象定为最终值）

### S5 V 审查实证对账
- [ ] 声明对账通过（配合 [声明对账清单](declaration-reconciliation-checklist.md) 执行）
- [ ] CMD-LOG 留证 `RECONCILIATION_PASSED` 事件与对账记录

### S6 门面级复用证据（本清单特有，A-005 不覆盖）
- [ ] Skill §5 质量门 G1–G4 逐条判定记录（判定依据与结果）
- [ ] 会话 CMD-LOG 完整：cmd=scanned-book-to-okf-wiki，session 前缀 `sc-YYYYMMDD-<book>` 规范
- [ ] 发现的 Skill 缺陷逐条登记（Gotchas 未覆盖的场景、步骤歧义、引用失效），反哺 Skill Changelog 作为升版输入

## ✅ 复现后验收

- [ ] 六工序各留证点齐全：route 字段、溯源 frontmatter、声明文本、对账记录、CMD-LOG
- [ ] G1–G4 全过；任一项未过则 Skill 维持 L1，缺陷记入本次任务复盘并反哺反模式清单
- [ ] 反模式自查通过（对照 Skill §6：默认先 OCR、摘要退化为书摘集、声明数字凭印象、route 隐式执行、混合路线不可声明）

## 🏁 升 L2 判定与归档

**判定线：启用条件 3 项 + 复现步骤全过 + 验收 3 项，缺一不可。**

任一项未过：Skill 维持 L1（frontmatter `version` 保持 1.x），缺陷记入任务复盘。

全过后执行：
- [ ] Skill frontmatter `version` 升 2.0.0，Changelog 补记案例 2 来源与缺陷反哺条目
- [ ] 案例 2 证据包归档：CMD-LOG 全文、route frontmatter、index 声明文本、对账记录、G1–G4 判定记录
- [ ] A-005 同步执行完毕（底层模式随第 2 案例升 L2），「摘要替代转录」「合规契约化」两模式成熟度与本 Skill 一并更新
- [ ] 索引更新：`capability-registry/02-skills.md` 方案数与实战验证列、ONBOARDING.md 速查表、skills/README.md 门面表

## 📊 与其他机制的关系

- 步骤级留证复用 [A-005 复现清单](summary-over-transcription-reproduction-checklist.md)（模式层），本清单只管门面层证据与升 L2 判定，避免双清单内容漂移
- S5 复用 [声明对账清单](declaration-reconciliation-checklist.md)（A-001），不重复其 5 步核验细节
- 与 [自引用盲点防御清单](self-reference-blindspot-defense.md) 检查 3（引文溯源）衔接：原创改写后引用仍须逐条可溯
