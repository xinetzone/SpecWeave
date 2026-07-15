---
title: 元原子化批量推广复盘 - 洞察行动项 Backlog
version: "1.0"
date: 2026-07-05
type: insight-action-backlog
source: "external: 模板引用-comprehensive-retrospective-template/insight-action-backlog.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-meta-atomization-batch-p0-p2-20260705/insight-action-backlog.toml"
project: retrospective-meta-atomization-batch-p0-p2-20260705
ssot:
  suggestions_source: export-suggestions.md
  insight_source: insight-extraction.md
---
# 洞察行动项 Backlog

> 本文件记录从本次复盘洞察和改进建议转化的可执行行动项。行动项执行完成后将结果记录在本文件中。

## 行动项总览

| ID | 来源 | 标题 | 优先级 | 状态 | DoD（完成定义） |
|---|---|---|---|---|---|
| IA-01 | S-01 | comprehensive-retrospective-template添加场景适配指南 | P1 | ⏳ 待执行 | README中新增"场景适配"章节，说明不同项目类型应选择哪些文件，含至少3种场景示例 |
| IA-02 | S-02/S-03 | 原子化操作添加相对路径校验和README计数检查 | P1 | ⏳ 待执行 | atomization-cmd或文档治理检查清单中新增2个检查项：相对路径层级校验、README文档计数一致性 |
| IA-03 | S-06/S-07 | 元原子化方法论补充批量推广检查清单和分类决策树 | P1 | ⏳ 待执行 | 元原子化相关文档中补充"批量推广前置检查清单"（7项）和"分类处置决策树"（4类判断标准） |
| IA-04 | S-05 | 编写可靠的行数统计Python脚本 | P2 | ⏳ 待执行 | .agents/scripts/中新增count-lines.py，支持多文件统计，结果与实际Read行数一致，添加到工具库README |
| IA-05 | S-08 | comprehensive-retrospective-template添加批量操作项目适配示例 | P2 | ⏳ 待执行 | 模板中添加execution-phases按批次组织的示例片段，说明与时间阶段组织的区别 |
| IA-06 | 模式升级 | 将两个L2验证模式写入模式库 | P1 | ⏳ 待执行 | docs/retrospective/patterns/中新增"方法论推广渐进式验证模式"和"文档原子化分类处置模式"两个模式文档，含问题场景/解决方案/验证案例 |

## 行动项详情

### IA-01: comprehensive-retrospective-template添加场景适配指南

- **优先级**: P1
- **来源建议**: S-01
- **问题描述**: 模板README列出了所有文件，但未说明什么场景下可以省略哪些文件，依赖使用者经验判断
- **执行方案**:
  1. 在comprehensive-retrospective-template/README.md中新增"场景适配指南"章节
  2. 定义3种典型场景：
     - 全生命周期大型复盘（使用所有7个文件）
     - 单日/单任务中型复盘（使用5-6个文件，省略final-execution-summary直到行动项闭环）
     - 小型任务快速复盘（使用3-4个核心文件）
  3. 每种场景给出文件选择矩阵
- **DoD**: README新增适配指南章节，包含场景判断条件和文件选择矩阵，至少覆盖3种场景
- **预计工作量**: 低（~30分钟）

---

### IA-02: 原子化操作添加相对路径校验和README计数检查

- **优先级**: P1
- **来源建议**: S-02, S-03
- **问题描述**: P0批次3次出现相对路径层级错误，1次出现README文档计数未更新
- **执行方案**:
  1. 在document-governance-checklist-template.md中添加：
     - [ ] 子目录文件创建后，验证所有`../`相对路径层级与实际目录深度一致
     - [ ] 原子化完成后，README中的文档计数/描述与实际文件数量一致
  2. 或在check-links.py中增强功能，自动检测常见相对路径错误
- **DoD**: 文档治理检查清单新增2项检查项，或check-links.py新增相对路径层级检测功能
- **预计工作量**: 中（~1小时）

---

### IA-03: 元原子化方法论补充批量推广检查清单和分类决策树

- **优先级**: P1
- **来源建议**: S-06, S-07 + 洞察萃取§3模式1/模式2
- **问题描述**: 本次批量推广前没有显式的检查清单和分类标准，依赖执行时的即时判断
- **执行方案**:
  1. 整理本次执行中的批量推广前置检查清单（7项，见export-suggestions.md §四）
  2. 整理分类处置决策树（4类判断标准，见export-suggestions.md §四）
  3. 将这些内容添加到元原子化相关的方法论文档或SOP中
- **DoD**: 元原子化方法论文档中包含批量推广检查清单和分类决策树，可被后续批量操作直接使用
- **预计工作量**: 中（~1小时）

---

### IA-04: 编写可靠的行数统计Python脚本

- **优先级**: P2
- **来源建议**: S-05
- **问题描述**: PowerShell的`Measure-Object -Line`统计行数不准确
- **执行方案**:
  1. 在.agents/scripts/中创建count-lines.py
  2. 支持单文件/多文件/目录统计
  3. 准确统计实际行数（与Read工具读取结果一致）
  4. 在.agents/scripts/lib/README.md中注册该工具
- **DoD**: 脚本存在，测试验证统计结果准确，工具库README已更新
- **预计工作量**: 低（~30分钟）

---

### IA-05: comprehensive-retrospective-template添加批量操作项目适配示例

- **优先级**: P2
- **来源建议**: S-08
- **问题描述**: 模板中execution-phases默认按时间阶段组织，但批量操作类项目更适合按批次组织，缺乏示例参考
- **执行方案**:
  1. 在comprehensive-retrospective-template/execution-phases.md中添加注释说明，或在README的适配指南中添加示例
  2. 提供批次组织的模板片段：按P0/P1/P2批次划分，每批包含处理对象、策略、结果、问题
- **DoD**: 模板中包含批次组织方式的说明和示例片段
- **预计工作量**: 低（~20分钟）

---

### IA-06: 将两个L2验证模式写入模式库

- **优先级**: P1
- **来源**: export-suggestions.md §2.1 L1→L2升级模式
- **问题描述**: "方法论推广渐进式验证模式"和"文档原子化分类处置模式"已通过本次验证达到L2，但尚未正式写入模式库
- **执行方案**:
  1. 在docs/retrospective/patterns/中创建两个模式文档
  2. 每个模式文档包含：问题场景、解决方案、模式结构、验证案例（本次复盘作为首个验证案例）、适用边界
  3. 更新模式库索引
- **DoD**: 两个模式文档存在，frontmatter标记maturity: L2，模式库索引已更新
- **预计工作量**: 中（~1.5小时）

## 执行记录

> 行动项执行完成后，在此章节记录执行结果、提交哈希、完成日期。

| IA-ID | 完成日期 | 提交/变更 | 执行结果 |
|---|---|---|---|
| — | — | — | 暂无已完成项 |
