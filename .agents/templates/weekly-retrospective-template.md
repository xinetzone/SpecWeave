---
title: "周迭代复盘模板"
id: "weekly-retrospective-template"
source: "retrospective:retrospective-specweave-full-project-20260719"
x-toml-ref: "../../.meta/toml/.agents/templates/weekly-retrospective-template.toml"
type: "checklist-template"
maturity_level: "L1"
created_date: "2026-07-19"
tags: [weekly, retrospective, iteration, checklist]
trigger_conditions:
  - 每周日晚进行本周迭代复盘
  - docgen weekly 子命令执行后填写
validation_count: 0
reuse_count: 0
related_patterns:
  - meta-retrospective-closed-loop
  - automated-stats-three-defense-lines
---
# SpecWeave 周迭代复盘模板

> **来源**：从[SpecWeave全项目复盘报告](../docs/retrospective/reports/project-reports/retrospective-specweave-full-project-20260719/README.md)ACT-04 萃取。使用流程：先运行 `python .agents/scripts/docgen.py weekly` 获取本周数据快照，复制本模板到对应周目录，基于数据撰写复盘。

---

## 基本信息

- **复盘周期**：YYYY-MM-DD（周一） 至 YYYY-MM-DD（周日）
- **复盘生成时间**：YYYY-MM-DD
- **参与者**：[orchestrator, developer, reviewer]
- **Session ID**：retro-YYYYMMDD-weekly

## 一、本周数据快照

> 运行 `cd .agents/scripts && python docgen.py weekly` 后复制输出到下方：

```
<粘贴 docgen weekly 输出>
```

### 关键指标

| 指标 | 本周值 | 上周值 | 变化 |
|------|--------|--------|------|
| 提交数 | | | |
| test 提交数（占比） | | | |
| 新增模式数 | | | |
| 新增脚本数 | | | |
| CI 通过率 | | | |

## 二、本周关键事件

| 日期 | 事件/Spec/里程碑 | 类型(feat/fix/refactor/docs/test) | 影响范围 |
|------|-----------------|--------------------------------|---------|
| MM-DD | | | |
| MM-DD | | | |
| MM-DD | | | |

## 三、本周成就（What went well）

- 

## 四、本周问题（What didn't go well）

- 

## 五、根因分析（对每个问题执行5-Whys）

对"四"中每个问题：

**问题 N：**
1. 为什么发生？
2. 为什么会出现这个原因？
3. 为什么没有更早发现？
4. 为什么没有预防机制？
5. 根本原因：
6. 预防措施：

## 六、模式沉淀检查

- [ ] 本周是否有值得萃取为模式的实践？→ 如有，记录：
- [ ] 本周是否有反模式需要记录？→ 如有，记录：
- [ ] 是否有现有模式需要成熟度升级？→ 如有，记录：

## 七、下周行动项

| # | 行动项 | 优先级 | 责任角色 | DoD（验收标准） |
|---|--------|--------|---------|----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## 八、复盘元数据

- **复盘耗时**：__ 分钟
- **数据来源**：`docgen weekly` + `git log --oneline --since=<monday>`
- **链接校验**：`python .agents/scripts/check-links.py --path <本周复盘目录>` 结果：__ 个链接全部通过
