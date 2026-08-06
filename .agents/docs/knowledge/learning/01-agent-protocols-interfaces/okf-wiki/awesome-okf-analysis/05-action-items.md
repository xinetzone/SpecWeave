---
id: awesome-okf-action-items
title: Awesome OKF 深度分析 - 原子行动项（A阶段）
type: ActionItems
version: 1.0
source: 基于02-insights.md的"下次行动"和V阶段审查反馈拆解为原子行动项
description: 从awesome-okf分析中提炼的4个原子行动项，可在SpecWeave中独立落地
tags: [okf, awesome-okf, 行动项, action-items, atomization]
category: case-study
date: 2026-08-06
---

# Awesome OKF 深度分析 - 原子行动项（A阶段）

> **方法论说明**：本阶段将I阶段洞察中的"下次行动"拆解为原子行动项，每项严格符合5项原子标准：**(1)单一职责 (2)可验证 (3)有Owner角色 (4)有时间盒 (5)可独立交付**。行动项不要求立即执行，作为知识沉淀的落地钩子。

---

## 行动项总览

| 行动项 | 对应洞察/模式 | Owner角色 | 预估时间盒 | 依赖 |
|---|---|---|---|---|
| A1 | P1（零依赖CLI聚合） | Developer | 2小时 | 无 |
| A2 | P2（规范留白扩展） | Architect | 4小时 | 无 |
| A3 | I4（Dogfooding自举） | Developer | 3小时 | 无 |
| A4 | I2（Producer/Skill分层） | Architect | 2小时 | A1、A3完成后参考 |

---

## A1：核心校验脚本依赖审计与零依赖改造优先级排序

- **对应洞察/模式**：模式P1零依赖CLI聚合模式 + V-YELLOW-01分层零依赖策略
- **单一职责**：完成`.agents/scripts/`下所有Python脚本的依赖审计，按"L0核心门禁（零依赖+降级）/L1常用工具（可选依赖+友好提示）/L2高级功能（明确依赖标注）"三层分类，输出零依赖改造优先级清单。
- **可验证完成标准**：
  1. 产出一份审计表格，列出`.agents/scripts/`下所有Python脚本（含子目录）
  2. 每个脚本标注：当前依赖列表、建议分层（L0/L1/L2）、零依赖改造难度评估（低/中/高）、是否需要降级策略
  3. 识别出3-5个L0核心门禁脚本作为首批零依赖改造候选
  4. 对已有依赖的核心脚本（如check-links.py若依赖requests），给出"优先用urllib"或"实现try-except降级"的具体建议
- **Owner角色**：Developer（开发者）
- **预估时间盒**：2小时
- **可独立交付**：是。审计完成后输出Markdown表格即可，无需等待其他行动项。
- **落地路径建议**：审计结果可存入`.agents/docs/knowledge/learning/.../scripts-dependency-audit.md`，作为后续零依赖改造的依据。

---

## A2：MDI规范扩展提案模板与流程建立

- **对应洞察/模式**：模式P2规范留白扩展打样模式 + V-YELLOW-02 L1/L2/L3扩展分级
- **单一职责**：为MDI（Markdown as Interface）v1.0规范建立"留白扩展→dogfooding打样→提案"的标准流程与模板，包含扩展分级（L1微调整/L2功能扩展/L3架构变更）和合法留白识别检查清单。
- **可验证完成标准**：
  1. 在`.agents/`合适位置创建《MDI规范演进指南》文档
  2. 文档包含：
     - "识别合法留白的3个信号"检查清单（对应V-BLUE-02补充）
     - L1/L2/L3三级扩展的判定标准与流程（对应V-YELLOW-02）
     - L2级扩展提案模板（含：留白位置引用、向后兼容性分析、Dogfooding计划、参考实现计划）
     - "语法兼容vs语义增强"边界说明（对应V-GREEN-02）
  3. 以x-toml-ref扩展作为试点案例，验证流程可执行
- **Owner角色**：Architect（架构师）
- **预估时间盒**：4小时
- **可独立交付**：是。仅需文档输出，不涉及代码改动。
- **落地路径建议**：文档存入`.agents/docs/standards/`或`.agents/rules/`，作为后续规范变更的指导文件。

---

## A3：.agents/目录Dogfooding合规自检机制建立

- **对应洞察/模式**：洞察I4 Dogfooding作为活的符合性证明
- **单一职责**：建立`.agents/`目录的MDI v1.0合规自检脚本（或扩展现有validate脚本），确保.agents/下所有.md文件自身符合MDI规范，SKILL.md文件满足双frontmatter要求（Skill门面+OKF Concept），实现"规范即范例"的自举验证。
- **可验证完成标准**：
  1. 自检脚本（可基于现有okf-validate思路扩展）检查项包括：
     - 所有非保留.md文件有正确YAML frontmatter
     - frontmatter包含必要字段（id/title/type等MDI要求字段）
     - skills/目录下SKILL.md同时包含Skill所需字段（name/description）和MDI所需字段（type: Skill）
     - 文档内相对路径链接有效（可复用现有check-links.py）
  2. 在`.githooks/pre-commit`中集成此自检（可选，或作为独立命令）
  3. 运行自检脚本，输出当前.agents/目录合规报告，列出不合规项（如缺少frontmatter的文件）
- **Owner角色**：Developer（开发者）
- **预估时间盒**：3小时
- **可独立交付**：是。脚本可独立运行，产出合规报告即可，不要求一次性修复所有不合规项。
- **落地路径建议**：脚本存入`.agents/scripts/`，可考虑作为`sagents check-mdi`子命令（A1完成后）。

---

## A4：.agents/skills/与scripts/边界审查指南文档

- **对应洞察/模式**：洞察I2 Producer/Skill双层解耦 + V-RED-03确定性/判断性分层修正
- **单一职责**：创建一份边界审查指南，明确`.agents/skills/`（Skill门面，方法论指导）与`.agents/scripts/`（确定性脚本，自动化执行）的职责边界，给出越界识别检查清单与典型反模式。
- **可验证完成标准**：
  1. 指南文档包含：
     - 两层职责定义："脚本做确定性执行（可自动化验证）、Skill做方法论指导（判断性内容）"（替换"笨/聪明"表述，对应V-RED-03）
     - 越界识别检查清单（如"脚本中是否包含大段指导性文字？""Skill中是否包含可自动化的格式校验逻辑？"）
     - 3-5个现有文件的正面示例（正确分层）
     - 反模式列表（如"在脚本中硬编码业务规则""在Skill中描述可自动化的格式步骤"）
  2. 抽查现有2-3个skill和script，用检查清单做一次边界审查，记录发现（不需要立即重构，仅记录）
- **Owner角色**：Architect（架构师）
- **预估时间盒**：2小时
- **可独立交付**：是。仅需文档输出+审查记录，不涉及大规模重构。
- **前置参考**：建议在A1（脚本审计）和A3（dogfooding自检）完成后执行，有更完整的现状数据。但不阻塞，可独立执行。
- **落地路径建议**：文档存入`.agents/docs/knowledge/learning/`或`.agents/skills/`目录下作为README补充。

---

## 行动项依赖关系图

```
A1（脚本依赖审计）──┐
                   ├──> A4（边界审查指南）
A3（Dogfooding自检）┘

A2（MDI扩展流程）：独立
```

---

## G4质量门自检

- ✅ 原子行动项数量4个（在3-5个目标范围内）
- ✅ 每个行动项符合5项原子标准：
  - **单一职责**：A1审计、A2流程文档、A3自检脚本、A4边界指南，各做一件事
  - **可验证**：每个行动项都有明确的完成标准（可检查的产出物）
  - **有Owner**：明确Developer/Architect角色
  - **有时间盒**：每项预估2-4小时，时间盒明确
  - **可独立交付**：A1/A2/A3可完全独立执行；A4建议参考A1/A3结果但不阻塞
- ✅ 行动项与洞察有明确对应关系：
  - A1 ← P1零依赖CLI聚合
  - A2 ← P2规范留白扩展
  - A3 ← I4 Dogfooding自举
  - A4 ← I2 Producer/Skill分层
- ✅ 回应了V-YELLOW-03 CTO视角的关切：每个行动项明确时间盒和Owner，不是空泛的"评估一下"
