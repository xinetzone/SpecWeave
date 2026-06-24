+++
id = "retrospective-report-fact-statement-correction-overview"
date = "2026-06-23"
type = "project-overview"
source = "docs/retrospective/reports/retrospective-report-fact-statement-correction.md#一、项目概述"
+++

# 项目概述

## 1.1 项目背景

项目根目录的 `README.md` 第 31 行存在事实性偏差的描述：

> 本体系已被 OpenAI Codex、Cursor、GitHub Copilot 等 30+ AI 编码工具识别与遵循，通过单一入口路由与按需加载机制，让多智能体协作具备一致的上下文与质量基线。

该描述存在三重问题：

- **概念混淆**：将"基于 AGENTS.md 开放标准构建"等同于"被工具识别与遵循"。被工具识别与遵循的是 `AGENTS.md` 标准本身，而非本项目自己的规范体系。
- **数字无据**："30+ AI 编码工具"这一数字无明确出处，属于营销式夸大，不符合技术文档的客观性要求。
- **措辞自夸**："识别与遵循"语气过于绝对，与项目作为"规范体系"而非"行业事实标准"的实际定位不符。

## 1.2 项目目标

修正面向读者的现行文档中所有不恰当的事实表述，统一为客观准确的"基于 AGENTS.md 开放标准构建"的表述，同时保留对标准被工具支持的事实描述。

## 1.3 交付物清单

| 类别 | 文件 | 修改内容 |
|------|------|---------|
| 入口文档 | `README.md:31` | "被...30+ 工具识别与遵循" → "基于 AGENTS.md 开放标准构建" |
| 入口文档 | `README.md:81` | "被...30+ 工具识别遵循" → "基于 AGENTS.md 开放标准，可被支持该标准的工具加载" |
| 核心文档 | `docs/project-overview.md:12` | "被...30+ 工具识别与遵循" → "基于 AGENTS.md 开放标准构建" |
| 关联文档 | `docs/related-links.md:7` | 删除"30+"无依据数字，保留工具列举（属事实描述） |
| 复盘报告 | `docs/retrospective/reports/retrospective-report-fact-statement-correction.md` | 本报告 |
| **合计** | **5 个文件** | 4 处修正 + 1 份复盘 |