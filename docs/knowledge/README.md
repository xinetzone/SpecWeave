# 项目知识库

## 统计摘要

- **总条目数**：17

| 分类 | 数量 |
|------|------|
| architecture | 1 |
| best-practices | 1 |
| decisions | 1 |
| learning | 2 |
| operations | 3 |
| troubleshooting | 3 |
| unknown | 6 |

## 按类别浏览

### architecture

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | SpecWeave项目治理方法论体系的架构总览文档，定义了治理基建四层递进核心模型，以及围绕该模型形成的5个可复用元洞察模式，包含模式间关系、落地状态和自反性验证案例。 | 2026-06-30 | governance、architecture、methodology、stage-guardrails、patterns、four-layer-model、governance-loop、retrospective、meta-insights |

### best-practices

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | SpecWeave 项目中 Mermaid 图表的一站式操作手册，涵盖起步模板、安全编码六规则、自动化检查工具详解、渲染问题排查流程和不同图表类型注意事项。 | 2026-06-29 | mermaid、图表、可视化、check-mermaid、安全编码、六规则、模板、ci |

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |

### learning

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Claude Tag 文章知识捕获](learning/claude-tag-article.md) | 捕获量子位 2026-06-24 文章《刚刚，Claude Code大升级！卡帕西：LLM第三次变革》核心内容：Anthropic 发布企业协作工具 Claude Tag，定位为 Claude Code 进化，强调团队共享、主动介入（Ambient Mode）、异步执行，卡帕西称其为 LLM 用户界面第三次重大变革。 | 2026-06-29 | claude、tag、anthropic、agent、enterprise、slack、ambient-mode、opus、karpathy、llm、协作、知识沉淀 |
| [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md) | TuyaOpen 是涂鸦开源的跨平台、跨芯片、跨操作系统的 AI-IoT SDK，核心目标是用一套灵活的 C/C++ SDK，结合涂鸦云的低延迟多模态 AI 能力，简化开放式 AI-IoT 生态的搭建。 | 2026-06-30 | tuya、tuyaopen、iot、sdk、ai、embedded、c、cpp、mcu、esp32、mcp、cloud、tkl、tal、tdd、tdl |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、Ember框架感知操作方法、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。v2.1更新：精确化DOM选择器、新增diagnoseButtons诊断函数、补充MCP参数陷阱警告、补全误操作恢复方法、新增MCP vs Playwright操作区别对照表。 | 2026-06-30 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 当需要在 SpecWeave 中新增或使用 flexloop 相关功能时，基于三区域边界模型和四不原则的5种合规集成路径决策指南 | 2026-06-29 | vendor、flexloop、agentforge、submodule、集成方案、三区域模型、四不原则 |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |

### troubleshooting

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 记录 AI 智能体因未读取 AGENTS.md 启动协议而导致输出格式、文件路径、文档结构三项错误的完整故障链与修复方案 | 2026-06-24 | agents、protocol、startup、output-format、path、skill-conflict |
| [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md) | 记录 PowerShell Move-Item 重命名目录时 Access Denied 错误的排查与解决方案 | 2026-06-23 | windows、powershell、rename、directory、access-denied |
| [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md) | 记录在 submodule 目录内创建主项目文件导致 submodule 永久 dirty 的故障原因与解决方案，以及 submodule 元数据外置的最佳实践 | 2026-06-29 | git、submodule、vendor、dirty、modified-content |

### unknown

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [stage-guardrails-guide](stage-guardrails-guide.md) |  |  | - |
| [three-layer-routing](three-layer-routing.md) |  |  | - |
| [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md) |  |  | - |
| [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md) |  |  | - |
| [discourse-api-research](operations/discourse-api-research.md) |  |  | - |
| [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md) |  |  | - |

## 标签索引

### access-denied

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### agent

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### agentforge

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### agents

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### ai

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### ambient-mode

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### anthropic

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### architecture

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)
- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### browser

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### c

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### check-mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### ci

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### claude

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### cloud

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### convention

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### cpp

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### directory

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### dirty

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### discourse

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### embedded

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### enterprise

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### esp32

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### flexloop

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### four-layer-model

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### git

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### governance

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### governance-loop

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### heredoc

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### iot

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### karpathy

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### llm

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### mcp

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)
- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### mcu

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### meta-insights

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### methodology

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### modified-content

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### naming

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### opus

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### output-format

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### path

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### patterns

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### playwright

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### powershell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### protocol

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### rename

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### retrospective

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### sdk

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### shell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### skill-conflict

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### slack

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### stage-guardrails

- [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md)

### startup

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### submodule

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### tag

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### tal

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tdd

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tdl

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tkl

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tuya

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### tuyaopen

- [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md)

### vendor

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### windows

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### 三区域模型

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 六规则

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 协作

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### 发布

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 可视化

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 四不原则

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 图表

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 安全编码

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 未分类

- [stage-guardrails-guide](stage-guardrails-guide.md)
- [three-layer-routing](three-layer-routing.md)
- [VENDOR-INTEGRATION](VENDOR-INTEGRATION.md)
- [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md)
- [discourse-api-research](operations/discourse-api-research.md)
- [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md)

### 模板

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### 知识沉淀

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### 自动化

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 论坛

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### 集成方案

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [SpecWeave 治理方法论体系架构](governance-methodology-architecture.md) | 2026-06-30 | architecture |
| [TuyaOpen 全面学习报告](learning/tuya-open-learning-report.md) | 2026-06-30 | learning |
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 2026-06-30 | operations |
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | 2026-06-29 | best-practices |
| [Claude Tag 文章知识捕获](learning/claude-tag-article.md) | 2026-06-29 | learning |
| [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md) | 2026-06-29 | operations |
| [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md) | 2026-06-29 | troubleshooting |
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 2026-06-24 | troubleshooting |
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 2026-06-23 | decisions |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 2026-06-23 | operations |

## 相关资源

### 回溯报告

- [项目硬编码问题系统性复盘报告](../retrospective/hardcode-retrospective-report.md)
- [提示词工程 — 可迁移模式、模板与方法论萃取](../retrospective/prompt-extraction.md)
- [复盘文档体系](../retrospective/README.md)

### 任务总结

- [任务执行总结报告](../task-summaries/task-summary-readme-creation-20260623.md)

## 使用指南

### 如何添加知识条目

1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`platform/` 等）
2. 复制 `template.md` 作为模板，创建新的 `.md` 文件
3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）
4. 在正文中按照模板结构编写内容
5. 运行 `python scripts/generate_index.py` 重新生成索引

### 如何检索

- **按类别浏览**：使用上方的「按类别浏览」章节，按操作、平台、排错等分类查找
- **按标签检索**：使用上方的「标签索引」章节，按关键词标签快速定位
- **按时间排序**：查看「最近更新」章节，了解最新添加的知识条目
- **全文搜索**：在项目根目录使用 `grep -r "关键词" docs/knowledge/` 进行全文搜索

### 如何维护

- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息
- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）
- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目
- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成索引

---

*索引自动生成于 2026-06-30 13:20:40*
