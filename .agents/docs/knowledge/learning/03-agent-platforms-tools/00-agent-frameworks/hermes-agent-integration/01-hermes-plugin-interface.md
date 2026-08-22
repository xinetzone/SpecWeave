---
id: "hermes-agent-integration-01-plugin-interface"
title: "01 Hermes Agent 插件接口规范"
source: "NousResearch/hermes-agent 插件文档 v2.5.0"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/01-hermes-plugin-interface.toml"
type: "Wiki Tutorial"
description: "Hermes Agent 插件接口规范：插件三类、发现路径、启用机制、plugin.yaml、register(ctx)、tool schema"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Hermes 插件是扩展 Agent 能力的核心机制，含通用/内存/上下文三类，通过 plugin.yaml 元数据与 register(ctx) 入口注册工具、技能、钩子与记忆"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 01 Hermes Agent 插件接口规范

> **⚠️ 版本提示**：Hermes 生态演进快，以下字段/API 基于插件文档 v2.5.0，落地前请以 [Hermes Agent 官方仓库](https://github.com/NousResearch/hermes-agent) 为准并验证。

## 1.1 插件是什么

**Plugin（插件）** 是 Hermes 的扩展模块，以独立目录形式存在，通过标准化配置与代码向 Agent 注入自定义能力，完全解耦于核心框架，升级/替换不影响主程序。

## 1.2 插件三类

| 类型 | 能力 | 实例限制 | 适合承载 |
|------|------|:---:|---------|
| **通用插件（General）** | 自定义工具、钩子、斜杠命令 | 可多实例 | SpecWeave 的 skills/commands/scripts |
| **内存插件（Memory Provider）** | 替换/增强内置记忆系统 | 仅单实例 | hermes-okf / 自定义记忆 |
| **上下文插件（Context Engine）** | 替换内置上下文压缩能力 | 仅单实例 | 自定义上下文压缩 |

> **为什么有单实例限制？** 内存与上下文是 Agent 运行时的全局单例状态，多个实现会互相覆盖导致状态混乱。SpecWeave 若只暴露工具能力，应走通用插件，避免占用单实例名额。

## 1.3 插件发现路径（按优先级，后加载覆盖先加载）

| 优先级 | 路径 | 说明 |
|:---:|------|------|
| 1 | 官方内置 `/plugins` | 框架自带，默认禁用 |
| 2 | 用户插件 `~/.hermes/plugins` | 个人专属，全局生效 |
| 3 | 项目插件 `./.hermes/plugins` | 项目目录，需手动开启权限 |
| 4 | Pip 插件 `hermes_agent.plugins` 入口点 | 通过 Python 入口点分发 |

插件目录根路径可通过 **`HERMES_HOME`** 环境变量重定向（默认 `~/.hermes`）。

## 1.4 启用机制

插件**默认禁用**，必须手动加入允许列表才会加载：

```yaml
plugins:
  enabled:            # 允许列表（启用的插件）
    - specweave
    - hermes-okf
  disabled:           # 拒绝列表（强制禁用）
    - noisy-plugin
```

## 1.5 插件目录结构

最小插件仅需 4 个文件：

```
~/.hermes/plugins/specweave/
├── plugin.yaml        # 插件元数据（必需）
├── __init__.py        # 注册入口 register(ctx)（必需）
├── schemas.py         # 工具模型（可选）
└── tools.py           # 工具逻辑（可选）
```

## 1.6 plugin.yaml 元数据

```yaml
name: specweave            # 用作安装目录名，必须安全（见权限章节）
version: "1.0.0"
description: 将 SpecWeave 能力暴露给 Hermes Agent
manifest_version: 1        # 插件清单 schema 版本（当前恒为 1）
```

> **manifest_version**：若插件声明的版本高于安装器支持，安装会被拒绝并提示 `hermes update`。

## 1.7 register(ctx) 注册入口

`__init__.py` 通过 `register(ctx)` 向 Agent 注入能力。核心方法（示例，需验证）：

```python
import json

def register(ctx):
    # 1. 注册工具
    tool_schema = {
        "name": "specweave_retrospective",
        "description": "执行 SpecWeave 复盘流程并生成报告",
        "parameters": {
            "type": "object",
            "properties": {
                "milestone": {"type": "string", "description": "复盘里程碑"}
            },
            "required": ["milestone"]
        }
    }

    def handle_retrospective(params, **kwargs):
        milestone = params.get("milestone", "")
        # 实际调用 SpecWeave 复盘逻辑/脚本
        return json.dumps({"success": True, "milestone": milestone})

    ctx.register_tool(
        name="specweave_retrospective",
        toolset="specweave",
        schema=tool_schema,
        handler=handle_retrospective,
        description="执行 SpecWeave 复盘流程"
    )
```

## 1.8 tool schema（JSON Schema）

工具 schema 遵循 JSON Schema 规范，声明模型的调用契约：

```json
{
  "name": "tool_name",
  "description": "工具用途说明，供模型理解何时调用",
  "parameters": {
    "type": "object",
    "properties": {
      "arg1": {"type": "string", "description": "参数说明"}
    },
    "required": ["arg1"]
  }
}
```

**要点**：
- `description` 要写清楚"何时用、何时不用"，帮助模型正确触发
- `parameters` 定义入参类型与必填项，模型按此生成调用
- schema 与实际 handler 逻辑必须匹配，否则模型调用失败

## 1.9 与 SpecWeave Skill 结构的对应

SpecWeave 的 `.agents/skills/*/SKILL.md` 采用"触发就绪 description + 决策树 + 渐进式披露 + Why + 安全检查"五要素模型。映射到 Hermes 插件时：

- **触发词 + description** → tool schema 的 `description`（如何触发）
- **决策树 / 步骤** → 工具 handler 内部逻辑
- **安全检查（dry-run/幂等）** → handler 内保留

> **反模式**：不要把 SpecWeave 的"角色（roles）"直接注册为工具——角色是系统提示/prompt 层面的东西，不是可调用的工具函数。

## 1.10 相关章节

- 下一章：[SpecWeave 能力盘点与映射矩阵](02-capability-mapping.md)
- 配置落地：[配置文件设置](03-configuration.md)
- 调用示例：[调用方式示例](06-usage-examples.md)
