---
id: "full-lifecycle-retrospective-dedup-reorg-tasks"
title: "实施计划：复盘报告内容去重与重组整合"
version: "1.0"
---

# 实施计划：复盘报告内容去重与重组整合

## 前置决策

在开始执行前需确认：
- **SSOT分配原则**：最详细、最完整描述所在文件即为该内容的单一数据源
- **统计数据口径**：以README.md frontmatter中commit `5d4642c`为最终统计时间点，统一使用800次提交、2800+文件、~155脚本、237+模式
- **final-execution-summary.md处理原则**：保留完成总览表、自举验证独特内容、闭环声明；IA-01~IA-08详细交付内容精简为"完成状态+一句话成果+链接到insight-action-backlog.md"

---

## 文件职责边界（重组后）

| 文件 | 重组后单一职责 | SSOT内容 | 非SSOT处理 |
|------|--------------|---------|-----------|
| README.md | 入口导航+执行摘要（精简）| 核心数据简表、Top3经验/建议、阅读路径导航 | 删除重复的"按演化阶段查找"详细表，改为链接到execution-retrospective.md时间线 |
| execution-retrospective.md | 执行过程概览 | 七阶段Mermaid时间线、16项关键决策总表、目标达成度评估、成就亮点（精简）| 核心数据表改为引用README（或作为SSOT保留）；ha_api重构仅一句话提及+链接到l3报告 |
| execution-phases-s1-s3.md | S1-S3阶段详录 | **SSOT**：阶段一~三完整详录 | 无变化（已原子化，无外部重复） |
| execution-phases-s4-s7.md | S4-S7阶段详录 | **SSOT**：阶段四~七完整详录 | 无变化（已原子化，无外部重复） |
| insight-extraction.md | 洞察萃取主文档 | **SSOT**：十大维度分析、16条成功要素、5-Whys根因、元方法论模式、认知升级 | 与6/26对比表保留（最详细）；四层防御体系保留模式5详细描述；ha_api仅作为证据一句话提及 |
| export-suggestions.md | 改进建议与路线图 | **SSOT**：A-01~A-15改进建议清单、风险预警、路线图 | 删除已完成IA项的详细重复描述，改为状态标记+链接到final-execution-summary；L3模式升级表精简为链接到l3报告 |
| insight-action-backlog.md | IA行动项详情（历史归档）| **SSOT**：IA-01~IA-08的洞察来源、具体操作、DoD清单（作为历史归档记录保留）| 无变化（本身就是行动项详情，DoD标记完成是历史状态记录） |
| final-execution-summary.md | 执行闭环总结+自举验证 | **SSOT**：闭环声明、资产沉淀统计、自举验证三实践（独特内容）、待验证项 | IA-01~IA-08详细交付详情大幅精简：每个IA保留"完成状态+一句话成果+一句话交付物+链接到insight-action-backlog.md对应章节"；删除与l3报告重复的ha_api重构细节，改为链接 |
| l3-pattern-application-report.md | L3模式应用验证报告 | **SSOT**：5个L3模式描述、模板升级量化分析、四层防御体系（此处最系统）、推广建议 | 已原子化，l3-template-upgrade-details.md保留详情，主报告无冗余需要删除 |
| l3-template-upgrade-details.md | 6个模板升级明细 | **SSOT**：模板升级前后代码对比 | 无变化（已原子化，无外部重复） |

---

## [ ] Task 1: 核实Git统计数据并确定统一口径

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 运行git log确认commit 5d4642c时的准确提交数
  - 统计核心区文件数（不含vendor/.meta）的准确数字
  - 确认所有核心指标的最终统一值
  - 在README.md的核心数据表中增加"统计口径说明"脚注
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: git log --oneline输出确认提交数
  - `programmatic` TR-1.2: 核心区文件数统计命令输出确认
  - `human-judgement` TR-1.3: 统一后的数字在各文件中一致

---

## [ ] Task 2: 精简README.md——保持纯入口导航性质

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 核心数据表保留（作为SSOT或execution-retrospective的镜像）
  - "按演化阶段查找"表（README §按演化阶段查找）简化为一句话指引+链接到execution-retrospective.md §二时间线
  - Top3经验/建议保留（摘要性质）
  - 关键发现保留（摘要性质）
  - 检查README行数控制在≤120行
  - 与6/26复盘关系保留末尾链接
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: README.md行数≤120行
  - `human-judgement` TR-2.2: 阅读路径清晰，导航完整无遗漏
  - `human-judgement` TR-2.3: 无大段重复内容，所有深度内容通过链接访问

---

## [ ] Task 3: 精简execution-retrospective.md——保持概览性质

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 核心数据一览表保留（作为SSOT或与README统一），增加统计口径说明
  - 成就亮点中与L3模式/四层防御/ha_api相关的条目（#8/#9/#10）精简为一句话+链接到l3-pattern-application-report.md
  - 删除成就亮点中对四层防御体系的展开描述（保留一句话提及）
  - 七阶段Mermaid时间线保留（作为SSOT）
  - 目标达成度评估中超预期成果部分精简：ha_api重构、四层防御改为一句话+链接
  - 16项关键决策总表保留（SSOT）
  - 检查整体文件保持概览性质，不重复细节
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `human-judgement` TR-3.1: 概览性质明确，细节内容通过链接访问
  - `human-judgement` TR-3.2: 成就亮点和超预期成果中无大段重复L3报告内容
  - `programmatic` TR-3.3: 统计数据与README一致

---

## [ ] Task 4: 精简insight-extraction.md——去除行动项和验证报告重复

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 十大维度分析保留完整（SSOT）
  - 1.10"自举验证与模式落地"中关于ha_api重构的细节描述精简为一句话证据+链接到final-execution-summary或l3报告
  - 1.10中四层防御体系保留模式层面的描述，但删除与l3报告重复的"检查项+46%"等执行细节
  - 元方法论模式保留完整（SSOT：规范自举性、治理三阶段、知识库三阶段、元文档杠杆、四层防御模式5）
  - 与6/26对比完整保留（SSOT：最详细对比）
  - 16条成功要素保留完整（SSOT）
  - 5-Whys根因保留完整（SSOT）
  - 8条认知升级保留完整（SSOT）
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `human-judgement` TR-4.1: 洞察层面分析完整，无洞察丢失
  - `human-judgement` TR-4.2: ha_api重构和四层防御的执行细节已替换为链接引用
  - `human-judgement` TR-4.3: 元方法论模式描述保持完整性（作为模式SSOT）

---

## [ ] Task 5: 精简export-suggestions.md——去除已完成项重复描述

- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 15条改进建议A-01~A-15保留完整（SSOT）
  - "✅ 已完成（闭环后自举验证期落地）"部分（IA-01~IA-08的L3升级/模板嵌入/零依赖验证详细描述）大幅精简：改为3-4行总结+链接到final-execution-summary.md
  - §四"模式成熟度更新"中：
    - 4.1 L3模式已升级表格保留，但删除与l3报告重复的"3次提交完成升级+46%检查项增加+四层防御建立"大段描述，改为一句话+链接
    - 4.2/4.3/4.4保留（待升级候选、新模式入库建议是独特内容）
  - 风险预警和路线图保留完整（SSOT）
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-5.1: 改进建议清单A-01~A-15完整保留
  - `human-judgement` TR-5.2: 已完成项不再大段重复IA执行细节，改为链接
  - `human-judgement` TR-5.3: 风险预警和路线图无删减

---

## [ ] Task 6: 重构final-execution-summary.md——保留闭环+自举验证独特内容

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 执行摘要保留（总览性质）
  - 完成总览表保留（8项IA的状态一览）
  - **大幅精简§"各行动项交付详情"**：
    - IA-01~IA-05和IA-08：每个从当前15-30行精简为3-4行（完成状态+一句话核心成果+关键交付物名称+链接到insight-action-backlog.md对应章节）
    - IA-06：保留模式升级表格（5个L3模式列表是有价值的汇总），删除大段描述改为一句话总结+链接到l3-pattern-application-report.md
    - IA-07：精简为3行说明
  - §"资产沉淀统计"保留（独特汇总）
  - §"方法论资产增量"保留（独特总结）
  - §"未完成项与后续观察"保留（独特内容）
  - §"闭环声明"保留（核心结论）
  - §"闭环后立即验证：L3模式实践应用"完整保留（**SSOT**：自举验证三实践是本文件独特价值内容）
    - 验证实践1（模板嵌入）保留但不过度展开模板细节（链接到l3报告）
    - 验证实践2（ha_api重构）保留核心证据（11个测试通过），删除代码层面细节（链接到l3报告）
    - 验证实践3（报告生成）保留一句话
  - 验证结论表保留
  - 关联文档表更新
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `human-judgement` TR-6.1: IA交付详情大幅精简（从当前~120行减至~40行）
  - `human-judgement` TR-6.2: 自举验证三实践作为独特内容保留完整
  - `human-judgement` TR-6.3: 闭环声明和资产统计完整保留
  - `programmatic` TR-6.4: 所有IA详情位置有正确链接到insight-action-backlog.md

---

## [ ] Task 7: 更新execution-phases-s4-s7.md中阶段七的交叉引用

- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 阶段七（3.7）事实还原中关于L3模式升级、模板嵌入、ha_api重构的描述保留（作为阶段记录的一部分，是历史事实）
  - 检查是否有与l3报告过度重复的细节需要精简（但阶段记录本身是SSOT，应保持完整）
  - 确认阶段七中引用的模式描述链接正确
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-7.1: 阶段七作为历史事实记录保持完整
  - `human-judgement` TR-7.2: 无多余的跨文件重复展开

---

## [ ] Task 8: 更新所有内部链接和交叉引用

- **Priority**: high
- **Depends On**: Tasks 2-7
- **Description**:
  - 检查所有文件中的相对路径链接是否正确
  - 新增的链接引用需使用正确的相对路径和锚点
  - 更新README.md中的快速索引表，反映重组后的文档结构
  - 更新各文件末尾的"关联文档"章节（如有）
  - 特别注意final-execution-summary.md中新增的链接指向insight-action-backlog.md的正确锚点
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-8.1: `python .agents/scripts/check-links.py --path docs/retrospective/reports/project-governance/comprehensive-reviews/retrospective-specweave-full-lifecycle-20260705/` 零断链
  - `human-judgement` TR-8.2: 抽查10个链接可正确跳转

---

## [ ] Task 9: 最终验证——一致性检查和信息完整性核查

- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 搜索关键统计数字（800、2800、155、237、5个L3、140+、59、15）在所有文件中出现时口径一致
  - 人工评审：对照冗余映射表，确认每类重复信息只有一个SSOT位置有完整描述
  - 人工评审：信息完整性检查——确认原始文档中的所有事实数据、关键结论、核心证据均可在重组后找到
  - 检查各文件frontmatter版本号是否需要更新（建议：有内容变更的文件patch版本号+0.1）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-9.1: grep检查关键数字在所有文件中一致
  - `human-judgement` TR-9.2: 冗余类别逐一核对，每类仅一个完整SSOT
  - `human-judgement` TR-9.3: 无关键信息丢失（对照原始文档核心要点）
  - `programmatic` TR-9.4: README.md行数≤120行验证
