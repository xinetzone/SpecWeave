---
id: "templates"
title: "模板使用说明"
source: "AGENTS.md#模板"
x-toml-ref: "../../.meta/toml/.agents/templates/README.toml"
---
# 模板使用说明

本目录提供多智能体协作过程中使用的标准模板，用于规范任务定义与交接流程。

## 模板清单

| 模板 | 用途 | 使用场景 |
|---|---|---|
| [task-template.md](task-template.md) | 通用任务定义 | 创建新任务时（通用模板） |
| [handoff-template.md](handoff-template.md) | 任务交接 | 智能体间任务转移时 |
| [insight-extraction-template.md](insight-extraction-template.md) | 洞察萃取 | 复盘中萃取洞察、根因分析、改进建议时 |
| [spec-release-checklist-template.md](spec-release-checklist-template.md) | 规范发布检查 | 新规范发布时遵循三同步原则的检查清单 |
| [document-governance-checklist-template.md](document-governance-checklist-template.md) | 文档治理检查 | 新建文档/原子化拆分/批量迁移时的质量门禁（frontmatter合规+工具清单+原则速查） |
| [theme-templates/](theme-templates/) | 主题任务模板 | 创建不同主题 spec 时的专用 tasks.md 模板（7 个主题） |
| [mermaid-templates/](mermaid-templates/) | Mermaid 图表模板 | 编写 Mermaid 流程图/时序图时的安全格式模板（5 种常用图表） |

## 主题任务模板

[theme-templates/](theme-templates/) 目录提供了按主题分类的 spec 任务模板，创建新 spec 时根据归类选择对应模板：

| 主题 | 模板文件 | 适用场景 |
|---|---|---|
| core-foundation | [core-foundation-task-template.md](theme-templates/core-foundation-task-template.md) | 从零创建核心系统/目录/基础设施 |
| roles-governance | [roles-governance-task-template.md](theme-templates/roles-governance-task-template.md) | 新增角色、添加治理规则、同步索引 |
| standards-tools | [standards-tools-task-template.md](theme-templates/standards-tools-task-template.md) | 编写规范文档、开发检查脚本、IDE 适配 |
| readme-branding | [readme-branding-task-template.md](theme-templates/readme-branding-task-template.md) | 修改 README、品牌定位、对外展示 |
| docs-restructure | [docs-restructure-task-template.md](theme-templates/docs-restructure-task-template.md) | 文档拆分/合并/重命名/目录重组 |
| retrospectives-insights | [retrospectives-insights-task-template.md](theme-templates/retrospectives-insights-task-template.md) | 任务复盘、问题诊断、经验萃取 |
| migration-archival | [migration-archival-task-template.md](theme-templates/migration-archival-task-template.md) | 外部内容迁移、沙箱治理、归档清理 |

## 使用方法

1. **复制模板**：根据任务类型，复制对应的模板文件。
2. **填写字段**：将模板中以 `{占位符}` 形式标注的字段替换为实际内容。
3. **遵循协议**：填写完成后，依据相关协议提交任务或执行交接。

### 任务模板使用示例

```
任务名称: 实现用户登录接口
任务类型: feature
优先级: high
负责人: developer-01
```

### 交接模板使用示例

```
交接方: architect
接收方: developer
任务名称: 实现用户登录接口
任务 ID: TASK-2026-001
交接时间: 2026-06-23T10:00:00+08:00
```

## 与协议的关系

- **交接协议**：使用 `handoff-template.md` 时，须遵循 `protocols/handoff.md` 中定义的交接协议，确保上下文、已完成工作与待办事项完整传递。
- **消息协议**：任务创建与交接的通知消息，须遵循 `protocols/messaging.md` 中定义的消息格式与通信规范。
