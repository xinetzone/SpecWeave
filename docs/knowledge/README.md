# 项目知识库

## 统计摘要

- **总条目数**：15

| 分类 | 数量 |
|------|------|
| best-practices | 1 |
| decisions | 1 |
| learning | 1 |
| operations | 5 |
| troubleshooting | 3 |
| unknown | 4 |

## 按类别浏览

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

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md) | 阶段守卫运行时强制执行层（GuardrailRuntime）的完整使用指南，涵盖8阶段权限速查、必读文档清单、典型日志示例、常见拦截原因与解决方案、CLI工具手册，以及运行时+离线双层验证闭环。 | 2026-06-29 | stage-guardrails、阶段守卫、运行时拦截、SG-LOG、guard-operation、强制执行、工作流 |
| [三层路由流程图与异常处理说明](three-layer-routing.md) | SpecWeave 三层路由（SpecWeave → vendor → flexloop）的完整跳转逻辑可视化，含主流程与 8 类异常处理分支说明，便于团队成员理解路由机制与排查异常。 | 2026-06-29 | vendor、routing、flexloop、mermaid、三层路由、异常处理、AGENTS |
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 基于Trae IDE集成浏览器（integrated_browser MCP）和Playwright Python脚本操作forum.trae.cn论坛的完整指南，包含DOM选择器参考、操作序列模板、JavaScript代码片段、独立Python脚本使用、故障排查和长期方案（@discourse/mcp）接入指南。 | 2026-06-29 | discourse、论坛、自动化、browser、mcp、playwright、发布 |
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

### AGENTS

- [三层路由流程图与异常处理说明](three-layer-routing.md)

### agents

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### ambient-mode

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### anthropic

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### architecture

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### browser

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### check-mermaid

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### ci

- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

### claude

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### convention

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### directory

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### dirty

- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### discourse

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### enterprise

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### flexloop

- [三层路由流程图与异常处理说明](three-layer-routing.md)
- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### git

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### guard-operation

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### heredoc

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### karpathy

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### llm

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### mcp

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### mermaid

- [三层路由流程图与异常处理说明](three-layer-routing.md)
- [Mermaid 图表操作指南](best-practices/mermaid-guide.md)

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

### playwright

- [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md)

### powershell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### protocol

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### rename

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### routing

- [三层路由流程图与异常处理说明](three-layer-routing.md)

### SG-LOG

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### shell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### skill-conflict

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### slack

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### stage-guardrails

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### startup

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### submodule

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### tag

- [Claude Tag 文章知识捕获](learning/claude-tag-article.md)

### vendor

- [三层路由流程图与异常处理说明](three-layer-routing.md)
- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)
- [Git Submodule 显示 modified content 或 dirty 状态](troubleshooting/submodule-modified-content.md)

### windows

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### 三区域模型

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

### 三层路由

- [三层路由流程图与异常处理说明](three-layer-routing.md)

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

### 工作流

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### 异常处理

- [三层路由流程图与异常处理说明](three-layer-routing.md)

### 强制执行

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### 未分类

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

### 运行时拦截

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### 阶段守卫

- [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md)

### 集成方案

- [vendor/flexloop 功能集成方案决策指南](operations/vendor-flexloop-integration-guide.md)

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [阶段守卫运行时强制执行层使用指南](stage-guardrails-guide.md) | 2026-06-29 | operations |
| [三层路由流程图与异常处理说明](three-layer-routing.md) | 2026-06-29 | operations |
| [Mermaid 图表操作指南](best-practices/mermaid-guide.md) | 2026-06-29 | best-practices |
| [Claude Tag 文章知识捕获](learning/claude-tag-article.md) | 2026-06-29 | learning |
| [Discourse论坛（forum.trae.cn）自动化操作指南](operations/forum-automation.md) | 2026-06-29 | operations |
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

*索引自动生成于 2026-06-29 13:29:10*
