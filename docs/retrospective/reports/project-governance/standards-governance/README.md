---
type: Report
id: "standards-governance-readme"
title: "标准规范治理报告索引"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-governance/standards-governance/README.toml"
---

# 标准规范治理报告索引

本目录收录项目标准规范建立与推广相关的里程碑复盘报告。

## 报告列表

| 报告 | 日期 | 类型 | 说明 |
|------|------|------|------|
| [pwsh7 Windows统一规范建立复盘](retrospective-pwsh7-windows-standard-20260729/README.md) | 2026-07-29 | 里程碑复盘 | 完成PowerShell 7.4+版本统一，28个脚本全部合规，萃取runtime-version-enforcement模式 |
| [Python 3.10+统一版本规范迁移完成报告](retrospective-python310-unification-20260730/README.md) | 2026-07-30 | 里程碑复盘 | 完成Python 3.10+版本统一，.agents/scripts/目录566个文件全部合规，验证runtime-version-enforcement模式跨语言可复用性 |
| [.temp 写入引导强化落盘执行报告](execution-report-temp-write-guidance-20260923.md) | 2026-09-23 | 落盘执行报告 | `.temp` 治理防复发（sovereign-rollout）：协议对齐用途前缀+日期命名、治理文档增补清理死锁/写入自检/引用纪律、AGENTS 与开发规范增补临时目录引用禁令 |

## 可复用模式

| 模式 | 萃取来源 | 适用性 |
|------|---------|--------|
| [runtime-version-enforcement](../../../patterns/code-patterns/runtime-version-enforcement.md) | pwsh7规范建立 | 通用：Python/Node.js/CMake/Go/Java/Docker/Git/Bash等任意需要统一版本的运行时/工具场景 |
