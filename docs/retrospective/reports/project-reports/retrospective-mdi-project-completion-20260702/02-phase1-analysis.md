---
version: 2.0
id: retrospective-mdi-phase1-analysis
title: "MDI项目复盘 - 阶段一：过程分析"
category: retrospective
type: project-reports
source: "execution-retrospective.md#3-过程分析"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/02-phase1-analysis.toml"
date: 2026-07-03
---
# MDI项目复盘 - 阶段一：过程分析

## 1. 成功因素

**1. 三层架构设计（Parser→Validator→Generator）验证了可扩展性**

从一开始就采用分层架构：解析层负责Markdown→结构化模型，验证层负责Profile+规则，生成层负责输出。这个设计在后续扩展中得到了验证：
- 新增CLI Profile时，只需在Parser增加`{command}` directive支持、在Validator增加CLI规则、在Generator增加cli_gen.py，各层独立变更不互相影响
- 新增versioning模块时，直接复用Parser输出的MDIDocument模型，不需要修改核心流程
- 新增示例提取器和检查清单转换器时，作为独立工具模块接入pytest_gen/jest_gen

**2. Profile自动检测机制降低了使用门槛**

通过frontmatter字段和内容特征自动判断文档类型（webapi/skill/clitool），用户不需要显式指定`--profile`参数。三个验证案例的检测全部正确。

**3. 测试先行+调试日志策略有效**

每个模块都先写单元测试再实现，遇到转换问题时通过添加DEBUG级日志快速定位。关键转换点（参数分类、示例匹配、响应断言生成）的日志在排查Bug#4、#5、#6时非常有效。

**4. 原子提交保证了提交历史清晰**

遵循Conventional Commits规范，每次提交单一职责，本次会话4个原子提交（feat/fix/docs×2）清晰区分了功能、修复、文档变更。

## 2. 遇到的困难与瓶颈

**1. MyST Directive解析的复杂度超预期**

最初以为`{endpoint}` directive只是简单的fence扩展，但实际遇到了：
- directive参数元信息（`:query name: type - desc`格式）的状态机解析
- directive后续内容块（子章节、代码块、列表）与directive本身的归属关系
- 多个directive之间的section树构建
- 解决Block tokenizer的递归终止条件问题（Bug#10）花费了较多时间

**2. Windows/PowerShell环境下的编码和引号问题**

- Git commit message中文乱码：PowerShell默认GBK编码，需要用Python写UTF-8文件再用`-F`参数传递
- Python命令行参数中嵌套引号在PowerShell中频繁出错，不得不写临时脚本文件执行
- 终端显示UTF-8内容乱码但Git存储正确，验证时需要用Python decode确认

**3. 参数location推断的歧义问题**

表格中参数的位置（path/query/body/header）在Markdown中没有明确标记时，仅靠参数名和HTTP方法推断存在歧义：
- GET请求的参数默认query但可能有path参数
- POST请求的参数可能在body也可能在query
- 最终通过":query/:path/:body/:header"前缀显式标记+智能推断fallback解决

**4. 测试生成器的"有用性"vs"正确性"平衡**

生成的pytest/Jest测试骨架如果只是空函数没有价值，但生成过于具体的断言又可能不正确。最终采用的策略是：
- 提取example代码块作为测试数据
- 将checklist复选框转换为断言步骤注释
- 生成语义化Mock数据填充参数
- 保留TODO注释提示人工补充业务逻辑

## 3. 做得不够好的地方

1. **MCP Server PoC未与MDI Generator深度集成**：mcp_domain.py和mcp_server.py实现了基础框架但未在验证案例中端到端测试
2. **CLI专用测试生成器缺失**：file-cli.md案例只能生成通用pytest，缺少CLI风格的测试骨架（subprocess调用）
3. **Jest生成器相对简陋**：相比pytest生成器的完整示例提取+检查清单转换，Jest生成器功能较少
4. **双向转换（MDI↔OpenAPI）未实现**：只能MDI→OpenAPI导出，不能从已有OpenAPI反向生成MDI

> 💡 阶段一产生的核心洞察、可复用模式及行动项已合并至全项目洞察汇总文档：[insight-extraction.md](insight-extraction.md)（洞察1-5为阶段一洞察，洞察6-11为阶段二洞察）。

## 导航

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [01-phase1-facts.md](01-phase1-facts.md) | [README.md](README.md) | [04-phase2-atomization.md](04-phase2-atomization.md) |

## Changelog

<!-- changelog -->
- 2026-07-03 | docs | v2.1：导航跳过已合并的03-phase1-insights.md，添加洞察文档引用指引
- 2026-07-03 | docs | v2.0：原子化拆分，从01-phase1-development.md独立为阶段一过程分析文件
