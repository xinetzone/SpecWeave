---
id: "templates-readme"
title: "templates 目录说明"
source: "extract-agent-workspace-template"
module: "templates"
---

# templates 目录说明

本目录存放可复用的通用脚手架与模板，供新项目引导使用。

## 模板清单

| 模板 | 说明 | 适用场景 |
|------|------|---------|
| [agent-workspace-hub/](agent-workspace-hub/README.md) | 通用智能体工作区脚手架（模板 AGENTS.md + 精简 .agents/ 骨架） | 新项目需要引导结构一致的智能体规范工作区 |

## 使用方式

1. 按需定位模板（如 `agent-workspace-hub/`）
2. 复制对应目录到新项目
3. 按模板内 README 替换占位符（`{{PROJECT_NAME}}` 等）
4. 验证 AGENTS.md 生效后开始开发

## 关联资源

- 模式文档：[agent-workspace-template.md](../.agents/docs/retrospective/patterns/architecture-patterns/agent-workspace-template.md)（可复用模式的完整说明）
- 根契约：[../AGENTS.md](../AGENTS.md)