---
id: "meta-audit-scale-economy"
title: "元洞察2：审计先行的\"规模效应\""
source: "../insight-extraction.md#洞察-2审计先行的规模效应"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/meta-02-audit-scale-economy.toml"
---
# 元洞察2：审计先行的"规模效应"

→ 关联模式：[large-scale-duplication-elimination.md](../../../../../patterns/methodology-patterns/document-architecture/large-scale-duplication-elimination.md)（五步法第一步：全量审计）

## 核心洞察

对 24 个脚本进行全量审计的成本（1 个 Agent，几分钟）远低于"边重构边发现新重复"的成本（多次返工、遗漏修复）。

审计规模越大，单位成本越低——因为审计的**边际成本递减**：已识别的模式可快速在其他文件中定位同类重复，第10个文件的审计成本远低于第1个文件。

## 对比

| 策略 | 首次成本 | 返工成本 | 总成本 | 遗漏率 |
|------|---------|---------|--------|-------|
| 边做边发现 | 低（直接开始） | 高（多次返工） | 高 | 高 |
| 审计先行 | 中（前期审计） | 低（一次性处理） | 低 | 低 |

## 适用边界

- 文件数 < 5：审计先行的规划成本可能高于收益
- 文件数 ≥ 10：**审计先行是必选项**，而非可选项
- 文件数 ≥ 20：审计先行的规模效应更加显著

## 实践意义

check-duplication.py 开发完成后立即运行扫描，一次性识别全部残留重复并分类修复——工具化审计的成本极低（几秒）、收益极高。这验证了审计先行原则在自动化工具加持下的边际成本趋近于零。

## 关联洞察

- [law-03-spec-driven-planning.md](law-03-spec-driven-planning.md) — 规划收益与审计先行同属"前期投入后期回报"模式
- [finding-07-tool-self-validation.md](finding-07-tool-self-validation.md) — 工具自生验证是审计先行的自动化体现

---
*来源：[脚本共享库提取复盘](../README.md)*
