---
id: "review-insight-export-loop"
source: "external: 已删除的knowledge-extraction.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/review-insight-export-loop.toml"
---
> **来源**：从 `external: 已删除的knowledge-extraction.md` 三、可复用方法论 拆分

# 复盘→洞察→导出 知识闭环

## 来源
两轮复盘分析实践

## 流程图
```
复盘（回顾事实）→ 洞察（提炼规律）→ 导出（行动计划）
                                       ↓
                                  驱动下一轮改进
                                       ↓
                                  新一轮复盘（验证效果）
```

## 报告结构模板
```markdown
# {项目名称} — 项目复盘分析报告

## 一、项目概述
### 1.1 项目背景
### 1.2 项目目标
### 1.3 交付物清单

## 二、复盘环节
### 2.1 实施过程回顾（时间线 + 迭代演进 + Mermaid 流程图）
### 2.2 关键节点分析（每个关键决策的决策依据、技术挑战、解决方案）
### 2.3 执行情况与结果数据（量化统计表）
### 2.4 成功经验（每条经验有支撑事实）
### 2.5 存在问题（每个问题有根因分析和影响评估）

## 三、洞察环节
### 3.1 关键发现（每条发现有支撑事实和深层含义）
### 3.2 规律认知（提炼通用方法论，配 Mermaid 流程图）
### 3.3 潜在机会（改进空间、可复用资产、未来方向）

## 四、导出环节
### 4.1 改进建议（针对问题 + 流程优化 + 工具链完善）
### 4.2 行动计划（优先级 + 具体措施 + 责任方 + 时间节点）
### 4.3 后续优化方向（路线图 + 整合方向）
```

## 复用场景
任何项目的结项复盘。

> **关联模块**：
> - `templates/retrospective-report-template.md`
> - `patterns/architecture-patterns/incremental-regression-verification.md`