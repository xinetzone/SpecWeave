---
version: 1.2
id: mdi-insight-extraction
title: "MDI项目洞察萃取文档"
category: retrospective
type: project-reports
source: "MDI项目核心洞察萃取"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.toml"
date: 2026-07-02
---
# MDI项目洞察萃取文档

## 核心洞察

### 洞察1："文档即接口"在AI时代有独特价值
- **类别**：产品/方法论洞察
- **内容**：Markdown是LLM最容易理解和生成的格式，AI Agent场景下Markdown IDL的上下文成本远低于YAML/JSON格式的OpenAPI
- **支撑证据**：14个已有SKILL.md可以零成本迁移到MDI格式；LLM生成MDI格式的准确率高于生成OpenAPI YAML
- **可迁移性**：AI Agent工具定义、AI辅助编程场景下的接口设计均可应用

### 洞察2：示例代码块是测试数据的金矿
- **类别**：技术/工程洞察
- **内容**：API文档中的example代码块天然包含可执行测试数据，提取作为测试用例比纯Mock数据更真实且与文档同步
- **支撑证据**：MDI example_extractor.py能从JSON/Python/curl/HTTP格式代码块提取参数和响应数据
- **可迁移性**：所有从文档生成测试的工具都应优先提取文档示例而非纯Mock

### 洞察3：三层架构+Profile是IDL工具的通用模式
- **类别**：架构洞察
- **支撑证据**：Parser→Validator→Generator三层+Profile变体在MDI中验证了可扩展性，新增CLI Profile和versioning模块均不需要修改核心架构
- **沉淀为模式**：three-layer-parser-generator（架构层模式）

### 洞察4：结构化diff+SemVer解决文档变更沟通成本
- **类别**：工程洞察
- **内容**：代码有git diff和SemVer，但文档变更缺少类似工具。结构化diff+影响分析+版本建议可以大幅降低接口变更沟通成本
- **沉淀为模式**：structured-doc-diff-semver（代码层模式）

### 洞察5：检查清单是连接人类验收和机器测试的桥梁
- **类别**：方法论洞察
- **内容**：文档中的`- [ ]`复选框是人类可读的验收标准，通过关键词分类可自动转换为测试步骤
- **支撑证据**：MDI checklist_converter.py实现了前置/断言/后置/注释四分类

## 沉淀的模式

> ✅ 状态确认：以下3个模式均已成功沉淀至模式库，来源追溯正确

| 模式ID | 层级 | 路径 | 成熟度 | 入库状态 |
|--------|------|------|--------|---------|
| three-layer-parser-generator | architecture | ../../patterns/architecture-patterns/three-layer-parser-generator.md | L1 | ✅ 已入库 |
| example-driven-test-generation | code | ../../patterns/code-patterns/example-driven-test-generation.md | L1 | ✅ 已入库 |
| structured-doc-diff-semver | code | ../../patterns/code-patterns/structured-doc-diff-semver.md | L1 | ✅ 已入库 |

## 待沉淀模式（候选）

| 模式名称 | 层级 | 路径 | 状态 | 成熟度 |
|---------|------|------|------|--------|
| directive-state-machine-parsing | code | ../../patterns/code-patterns/directive-state-machine-parsing.md | ✅ 初稿已生成 | L1 |
| checklist-to-assertion-conversion | code | ../../patterns/code-patterns/checklist-to-assertion-conversion.md | ✅ 初稿已生成 | L1 |
| profile-auto-detection | code | ../../patterns/code-patterns/profile-auto-detection.md | ✅ 初稿已生成 | L1 |

## Changelog

<!-- changelog -->
- 2026-07-02 | docs | v1.2：3个候选模式已生成初稿并入库code-patterns/，更新状态标记
- 2026-07-02 | docs | v1.1：补全frontmatter（category/type/source/date），确认3个模式入库状态，添加待沉淀模式候选列表
- 2026-07-02 | docs | v1.0：初始版本，包含5个核心洞察和3个已沉淀模式
