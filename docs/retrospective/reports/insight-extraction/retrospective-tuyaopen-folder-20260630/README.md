---
id: "retrospective-tuyaopen-folder-20260630-readme"
title: "TuyaOpen 目录全链路复盘（复盘+洞察+萃取+学习+导出）"
source: "external/TuyaOpen"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-tuyaopen-folder-20260630/README.toml"
---
# TuyaOpen 目录全链路复盘（复盘+洞察+萃取+学习+导出）

> **分析对象**：`external/TuyaOpen`（TuyaOpen 仓库工作区）
> **复盘日期**：2026-06-30
> **报告类型**：代码与工程体系洞察复盘（含学习路径与导出建议）

## 项目概览

### 关键事实（可追溯）

| 项目项 | 结论 | 证据 |
|---|---|---|
| 项目定位 | 面向 AI 智能体硬件的跨平台 IoT SDK（C/C++）+ 云侧低延迟多模态 AI | [README_zh.md](../../../../../external/TuyaOpen/README_zh.md#L44-L59) |
| 目标平台 | Ubuntu、Tuya T2/T3/T5、ESP32、BK7231N、LN882H 等 | [README_zh.md](../../../../../external/TuyaOpen/README_zh.md#L75-L85) |
| 顶层结构 | apps/ boards/ docs/ examples/ platform/ src/ tests/ tools/ | [README_zh.md](../../../../../external/TuyaOpen/README_zh.md#L44-L66) |
| 工具链入口 | `tos.py`（click 聚合命令：prepare/check/config/build/flash/monitor/...） | [tos.py](../../../../../external/TuyaOpen/tos.py#L33-L47) |
| 环境初始化 | `export.sh` / `export.ps1` + `uv sync` + `tos.py prepare` | [AGENTS.md](../../../../../AGENTS.md#L15-L30) |

## 子报告导航

| 文档 | 说明 |
|---|---|
| [execution-retrospective.md](execution-retrospective.md) | 执行过程复盘：事实与时间线、工程结构解读、关键节点与风险点 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取：系统性洞察、可复用模式、关键差异与机会点 |
| [export-suggestions.md](export-suggestions.md) | 学习与导出：学习路径、验证清单、资产沉淀与对外输出建议 |

## 关联资产

- [TuyaOpen 全面学习报告](../../../../knowledge/learning/tuya-open-learning-report.md)
- [复盘-洞察-导出闭环模式](../../../patterns/methodology-patterns/retrospective-knowledge/review-insight-export-loop.md)
