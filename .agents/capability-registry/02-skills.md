---
id: "capability-registry-skills"
title: "Skill索引"
source: "capability-registry.md#02-skills"
x-toml-ref: "../../.meta/toml/.agents/capability-registry/02-skills.toml"
---
# Skill索引


### 完整Skill（2个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| forum-posting | "发帖"、"编辑帖子"、"回复帖子"、"跟帖"、"清理草稿"、"读取帖子"、"操作forum.trae.cn"、"Discourse论坛" | 2（forum-bot.py脚本 + integrated_browser MCP） | v1.1.0 | [skills/forum-posting/SKILL.md](../skills/forum-posting/SKILL.md) |
| home-assistant | "智能家居"、"控制设备"、"查询状态"、"home assistant"、"ha_api" | 1（REST API） | v1.0.0 | [skills/home-assistant/SKILL.md](../skills/home-assistant/SKILL.md) |

### 命令集门面（7个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| retrospective-cmd | "复盘"、"retrospective"、"回顾"、"总结经验"、"项目总结"、"阶段回顾" | 3（标准/轻量/故障复盘） | v1.2.1 | [skills/retrospective-cmd/SKILL.md](../skills/retrospective-cmd/SKILL.md) |
| insight-cmd | "洞察"、"insight"、"分析问题"、"萃取洞察"、"根因分析"、"问题诊断"、"为什么" | 3（数据驱动/根因诊断/萃取洞察） | v1.2.1 | [skills/insight-cmd/SKILL.md](../skills/insight-cmd/SKILL.md) |
| pattern-extraction-cmd | "模式沉淀"、"萃取模式"、"模式入库"、"沉淀为模式"、"可复用模式"、"pattern extraction"、"更新模式库"、"生成模式文档" | 3（全新创建/模式更新/合并重构） | v1.0.0 | [skills/pattern-extraction-cmd/SKILL.md](../skills/pattern-extraction-cmd/SKILL.md) |
| export-report-cmd | "导出报告"、"export"、"生成报告"、"导出文档"、"归档" | 2（Markdown/JSON） | v1.2.1 | [skills/export-report-cmd/SKILL.md](../skills/export-report-cmd/SKILL.md) |
| atomization-cmd | "原子化"、"拆分文件"、"atomize"、"拆分大文档"、"文档拆分" | 3（文档原子化/一键收尾/预检） | v1.2.1 | [skills/atomization-cmd/SKILL.md](../skills/atomization-cmd/SKILL.md) |
| atomic-commit-cmd | "提交"、"commit"、"原子提交"、"代码提交"、"git commit" | 3（标准/快速/CI检查） | v1.2.1 | [skills/atomic-commit-cmd/SKILL.md](../skills/atomic-commit-cmd/SKILL.md) |
| mermaid-cmd | "mermaid"、"流程图"、"时序图"、"状态图"、"画个图"、"图表"、"架构图"、"思维导图"、"画流程图" | 3（快速生成/检查修复/复杂协作） | v1.1.0 | [skills/mermaid-cmd/SKILL.md](../skills/mermaid-cmd/SKILL.md) |

### 脚本命令门面（5个）

| Skill名 | 触发词 | 对应脚本 | 版本 | 路径 |
|---------|--------|---------|------|------|
| link-check-cmd | "链接检查"、"检查链接"、"断链"、"链接修复"、"fix links"、"check links"、"验证链接"、"死链" | check-links.py + lib/link_fixer.py | v1.0.0 | [skills/link-check-cmd/SKILL.md](../skills/link-check-cmd/SKILL.md) |
| atomization-finalize-cmd | "原子化收尾"、"finalize atomization"、"文档拆分完成"、"文件移动后处理"、"断链修复导航更新"、"一键收尾" | finalize-atomization.py | v1.0.0 | [skills/atomization-finalize-cmd/SKILL.md](../skills/atomization-finalize-cmd/SKILL.md) |
| docgen-cmd | "生成导航"、"更新导航"、"docgen"、"更新README"、"刷新看板"、"生成文档索引"、"应用清单" | docgen.py | v1.0.0 | [skills/docgen-cmd/SKILL.md](../skills/docgen-cmd/SKILL.md) |
| ci-check-cmd | "CI检查"、"提交前检查"、"综合检查"、"ci-check"、"流水线检查"、"提交门禁"、"全量检查"、"跑一下CI"、"pre-commit"、"预检" | ci-check.ps1 + ci-check.sh | v1.0.0 | [skills/ci-check-cmd/SKILL.md](../skills/ci-check-cmd/SKILL.md) |
| check-duplication-cmd | "重复代码"、"重复检查"、"代码重复"、"check-duplication"、"重复检测"、"提取共享库"、"DRY检查"、"脚本重复" | check-duplication.py + lib/ | v1.0.0 | [skills/check-duplication-cmd/SKILL.md](../skills/check-duplication-cmd/SKILL.md) |

> **Skill类型说明**：
> - **完整Skill**：包含完整双方案实现、工具函数、详细步骤，可独立完成复杂任务
> - **命令集门面**：对 `.agents/commands/` 命令集的轻量封装，提供触发词、决策树、快速开始和安全检查
> - **脚本命令门面**：对 `.agents/scripts/` 高频自动化脚本的封装，提供参数说明、dry-run/预览机制、幂等性说明和错误处理

---


---

## 相关模式


← 上一章: [脚本索引](01-scripts.md) | **[返回索引](../capability-registry.md)** | 下一章 → [命令集、工作流、协议、规则索引](03-commands-workflows-protocols-rules.md)
