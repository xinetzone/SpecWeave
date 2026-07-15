---
id: "finding-tool-self-validation"
title: "发现7：\"工具自生验证\"模式"
source: "../insight-extraction.md#发现-7工具自生验证模式"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/finding-07-tool-self-validation.toml"
---
# 发现7："工具自生验证"模式

→ 正式模式：[tool-self-validation.md](../../../../../patterns/methodology-patterns/tools-automation/tool-self-validation.md)（L2 已验证，7项提交前检查清单）

## 事件发现

check-duplication.py 开发完成后首次运行就发现了7处"重复"，其中包括自身开发过程中需要消除的真实重复（check-links.py和check-source-traceability.py中的find_markdown_files）。这一过程同时验证了工具的正确性、发现了目标问题、暴露了可用性缺陷。

后续将误报过滤规则提取为通用规则文件（false-positive-rules.toml）后，重构check-duplication.py使用外部规则，再次通过自生验证7项检查确认无误。

## 规律

新开发的质量守护工具（linter/checker/静态分析器/scanner/validator）应在提交前**立即用它扫描自身代码库**。工具的首次运行即是自身的dry-run验证——同一把尺子先量自己。

这是 dry-run-first 模式在工具开发领域的具体应用。

## 自生验证可同时发现三类问题

1. **工具自身的bug**：误报/漏报/崩溃/编码错误/路径问题
2. **代码库中工具要检测的目标问题**：即工具存在的意义——检测真实问题
3. **工具的可用性缺陷**：输出不清晰、建议不可操作、exit code不正确

## 7项检查清单

| # | 检查项 | 核心验证 |
|---|--------|---------|
| 1 | 自扫描 | 工具能扫描自身目录并正常退出 |
| 2 | 真阳性修复 | 自扫描发现的真实问题全部修复 |
| 3 | 误报过滤 | 结构性样板自动排除（使用通用规则文件） |
| 4 | 信噪比≥30% | 真实问题占比不达标则不得提交 |
| 5 | 输出可用 | 每条报告含路径/行号/问题/建议/级别 |
| 6 | CI兼容 | ci-check全绿，参数/输出符合lib/cli.py约定 |
| 7 | 边界场景 | 空目录/二进制/特殊字符路径不崩溃 |

## 关联洞察

- [finding-05-fp-three-categories.md](finding-05-fp-three-categories.md) — 误报三分类是自生验证第3项的理论依据
- [meta-02-audit-scale-economy.md](meta-02-audit-scale-economy.md) — 工具化审计边际成本趋零
- [finding-06-powershell-encoding-trap.md](finding-06-powershell-encoding-trap.md) — CI集成验证（第6项）中发现的bug

---
*来源：[脚本共享库提取复盘](../README.md)*
