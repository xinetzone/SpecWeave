---
version: 1.0
id: mdi-insight-extraction
title: "MDI项目洞察萃取文档"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.toml"
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

| 模式ID | 层级 | 路径 | 成熟度 |
|--------|------|------|--------|
| three-layer-parser-generator | architecture | docs/retrospective/patterns/architecture-patterns/ | L1 |
| example-driven-test-generation | code | docs/retrospective/patterns/code-patterns/ | L1 |
| structured-doc-diff-semver | code | docs/retrospective/patterns/code-patterns/ | L1 |
