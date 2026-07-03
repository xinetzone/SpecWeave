---
version: 2.0
id: retrospective-mdi-phase1-insights
title: "MDI项目复盘 - 阶段一：洞察与行动项"
category: retrospective
type: project-reports
source: "execution-retrospective.md#4-洞察提炼"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/03-phase1-insights.toml"
date: 2026-07-03
---
# MDI项目复盘 - 阶段一：洞察与行动项

> 完整洞察列表（含阶段二）见 [insight-extraction.md](insight-extraction.md)，本文件仅列阶段一产生的核心洞察、模式和行动项。

## 1. 阶段一核心洞察

**洞察1："文档即接口"在AI时代有独特价值**

MDI的核心洞察是：在AI协作开发场景下，Markdown是LLM最容易理解和生成的格式。相比YAML/JSON格式的IDL（OpenAPI/AsyncAPI），Markdown的"人类可读性"不是nice-to-have而是核心需求——AI Agent需要直接读写接口文档，Markdown格式的上下文成本最低。这解释了为什么AI Skill文档天然适合MDI格式（14个已有SKILL.md可以零成本迁移）。

**洞察2：示例代码块是测试数据的金矿**

API文档中的example代码块（JSON响应示例、curl请求示例、Python调用示例）天然包含可执行的测试数据。从文档中提取这些示例作为测试用例，比纯Mock数据更真实，且与文档保持同步——文档更新时测试自动更新，解决了"文档漂移"问题。

**洞察3：三层架构+Profile是IDL工具的通用模式**

Parser→Validator→Generator三层+Profile变体的架构模式不仅适用于MDI，也适用于其他IDL工具的设计。分层的好处是每一层可以独立演进：Parser关注格式解析、Validator关注语义规则、Generator关注目标代码生成，Profile作为横切关注点在各层插入特定逻辑。

**洞察4：结构化diff+语义化版本建议解决文档变更的沟通成本**

代码有git diff和SemVer，但文档变更缺少类似工具。MDI的versioning模块证明：结构化diff（知道哪个接口的哪个参数变了）+影响分析（哪些下游产物需要重新生成）+版本建议（MAJOR/MINOR/PATCH）可以大幅降低接口变更的沟通成本。

**洞察5：检查清单是连接"人类验收标准"和"机器测试断言"的桥梁**

文档中的`- [ ]`复选框是人类可读的验收标准，checklist_converter证明这些复选框可以通过关键词分类（前置条件/断言/后置清理/注释）自动转换为测试步骤。这是"文档即测试"理念的关键实现路径。

## 2. 阶段一可复用模式

| 模式名称 | 适用场景 | 核心思想 |
|---------|---------|---------|
| 三层+Profile架构 | 解析器/编译器/代码生成器工具 | Parser→Validator→Generator分层，Profile做变体 |
| Directive参数状态机解析 | Markdown扩展语法解析 | 首行提取method/path，后续行按前缀状态机解析 |
| 示例驱动测试生成 | 从文档生成测试 | 代码块示例→测试数据，比Mock更真实 |
| 检查清单→断言转换 | 验收标准自动化 | 关键词分类→测试步骤，连接人与机器 |
| 结构化diff+SemVer | 文档/配置版本管理 | 字段级对比→严重性分级→版本建议 |
| Profile自动检测 | 多格式/多Schema工具 | 特征匹配自动选择Profile，降低使用门槛 |

## 3. 阶段一行动项

| 优先级 | 行动项 | 验收标准 |
|-------|--------|---------|
| 高 | Jest生成器补齐示例提取和检查清单转换功能 | Jest测试用例包含example数据和checklist断言步骤 |
| 高 | CLI专用测试生成器（subprocess风格） | file-cli.md能生成可执行的CLI测试骨架 |
| 中 | MCP Server PoC与MDI Generator深度集成验证 | 从MDI文档一键启动可运行的MCP Server |
| 中 | OpenAPI→MDI反向转换 | 能从现有OpenAPI JSON生成MDI文档初稿 |
| 低 | Markdown→MDI自动迁移工具 | 将自由格式API文档转换为MDI规范格式 |
| 低 | MDI Studio可视化编辑器 | Web UI拖拽式编辑MDI文档 |

## 导航

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [02-phase1-analysis.md](02-phase1-analysis.md) | [README.md](README.md) | [04-phase2-atomization.md](04-phase2-atomization.md) |

## Changelog

<!-- changelog -->
- 2026-07-03 | docs | v2.0：原子化拆分，从01-phase1-development.md独立为阶段一洞察与行动项文件
