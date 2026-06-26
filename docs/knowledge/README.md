# 项目知识库

## 统计摘要

- **总条目数**：6

| 分类 | 数量 |
|------|------|
| decisions | 1 |
| operations | 1 |
| troubleshooting | 2 |
| unknown | 2 |

## 按类别浏览

### decisions

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由 | 2026-06-23 | architecture、naming、directory、vendor、convention |

### operations

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案 | 2026-06-23 | windows、powershell、shell、heredoc、git |

### troubleshooting

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 记录 AI 智能体因未读取 AGENTS.md 启动协议而导致输出格式、文件路径、文档结构三项错误的完整故障链与修复方案 | 2026-06-24 | agents、protocol、startup、output-format、path、skill-conflict |
| [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md) | 记录 PowerShell Move-Item 重命名目录时 Access Denied 错误的排查与解决方案 | 2026-06-23 | windows、powershell、rename、directory、access-denied |

### unknown

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md) |  |  | - |
| [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md) |  |  | - |

## 标签索引

### access-denied

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### agents

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### architecture

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### convention

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### directory

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### git

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### heredoc

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### naming

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### output-format

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### path

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### powershell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### protocol

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### rename

- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### shell

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)

### skill-conflict

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### startup

- [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md)

### vendor

- [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md)

### windows

- [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md)
- [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md)

### 未分类

- [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md)
- [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md)

## 最近更新

| 标题 | 日期 | 分类 |
|------|------|------|
| [跳过 AGENTS.md 启动协议导致三重连锁输出错误](troubleshooting/agents-md-startup-protocol-skipped.md) | 2026-06-24 | troubleshooting |
| [ADR: libs/ 目录重命名为 vendor/](decisions/libs-rename-to-vendor.md) | 2026-06-23 | decisions |
| [Windows PowerShell 不支持 heredoc 语法](operations/windows-powershell-heredoc.md) | 2026-06-23 | operations |
| [Move-Item 目录重命名报 Access Denied 错误](troubleshooting/move-item-access-denied.md) | 2026-06-23 | troubleshooting |
| [ian-xiaohei-illustrations](learning/ian-xiaohei-illustrations.md) |  | unknown |
| [wechat-mp-content-extraction](operations/wechat-mp-content-extraction.md) |  | unknown |

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

*索引自动生成于 2026-06-26 13:37:31*
