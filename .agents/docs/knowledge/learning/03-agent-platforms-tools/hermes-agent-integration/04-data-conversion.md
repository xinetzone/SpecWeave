---
id: "hermes-agent-integration-04-data-conversion"
title: "04 数据格式转换方法"
source: "hermes-agent 插件文档 v2.5.0 + hermes-okf v0.5.9 + OKF 规范 + SpecWeave 现状"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/04-data-conversion.toml"
type: "Wiki Tutorial"
description: "数据格式转换：AGENTS.md 契约→plugin.yaml+register(ctx)、知识库 markdown→OKF concept/bundle、tool schema 定义"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "把 SpecWeave 的 AGENTS.md 契约、知识库 markdown 转换为 Hermes 插件元数据与 OKF bundle 的具体方法"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 04 数据格式转换方法

## 4.1 转换总览

SpecWeave 的数据主要是 Markdown + YAML frontmatter（AGENTS.md 契约、SKILL.md、commands、知识库）。转换为 Hermes 可识别格式主要有三条路径：

| 来源 | 转换目标 | 目的 |
|------|---------|------|
| AGENTS.md 契约 | plugin.yaml + register(ctx) | 让 Hermes 加载插件并注入能力 |
| 知识库 markdown | OKF concept / bundle | 作为可检索记忆层挂接 |
| 命令/Skill 接口 | tool schema（JSON Schema） | 让模型可调用 |

## 4.2 AGENTS.md 契约 → plugin.yaml + register(ctx)

AGENTS.md 是 SpecWeave 的"能力契约"，转换为 Hermes 插件时：

### 4.2.1 元数据转换

```yaml
# AGENTS.md 顶层信息 → plugin.yaml
name: specweave            # 插件名
version: "1.0.0"           # 插件版本
description: 将 SpecWeave 能力暴露给 Hermes Agent
manifest_version: 1
```

### 4.2.2 能力契约 → register(ctx) 工具

AGENTS.md 中的"指令集/命令"映射为工具，核心是**把契约的步骤转化为 handler 逻辑**：

```python
# 把 AGENTS.md 中"复盘"指令集的执行流程封装为工具 handler
def handle_retrospective(params, **kwargs):
    # 1. 采集事实（对应复盘 R 阶段）
    # 2. 分析根因（对应 I 阶段）
    # 3. 提炼模式（对应 E 阶段）
    # 4. 生成报告
    ...
    return result_json

ctx.register_tool(
    name="specweave_retrospective",
    toolset="specweave",
    schema=retro_schema,
    handler=handle_retrospective,
    description="执行 SpecWeave 复盘流程"
)
```

### 4.2.3 转换对照

| AGENTS.md / .agents 元素 | 转换方式 |
|-------------------------|---------|
| 指令集（commands/） | 每个指令集 → 一个或多个工具 handler |
| 脚本（scripts/） | 高频脚本 → 工具（subprocess 调用） |
| Skill 触发词 | → 工具 schema 的 description |
| 角色（roles/） | → 系统提示，不转换 |
| 全局规则 | → 系统提示 / on_session_start hook |

## 4.3 知识库 markdown → OKF concept / bundle

OKF（Open Knowledge Format）以 Markdown + YAML frontmatter 表示知识。SpecWeave 的 `knowledge/` 恰好是 Markdown + YAML frontmatter 结构，转换成本低。

### 4.3.1 frontmatter 对齐

SpecWeave 知识库 frontmatter 含 `id/title/source/type/description/tags/category/date/status` 等字段，与 OKF concept 高度兼容。转换为 OKF concept 时：

```markdown
---
id: "my-concept"
title: "我的知识单元"
description: "一句话描述"
tags: [tag1, tag2]
date: "2026-08-09"
type: "decision"    # 或 observation / plan / tool
---
# 知识内容

正文 markdown...
```

### 4.3.2 通过 hermes-okf 导入

hermes-okf 提供 CLI 管理 OKF bundle（`init / validate / list / show / search / snapshot / restore` 等）。把 SpecWeave 知识库作为 bundle 挂接：

```bash
# 初始化 OKF bundle（示例）
hermes-okf init --path <specweave-knowledge-path>

# 校验 bundle 合法性
hermes-okf validate

# 在 Hermes 会话中检索
hermes okf search "SpecWeave 复盘"
hermes okf show config/agent
```

> **注意**：OKF concept 需要 frontmatter 有 `id` 等字段，SpecWeave 现有文档多数已具备；缺失字段的文档需补齐后再导入（详见 [OKF 指南](../../01-agent-protocols-interfaces/okf-wiki/README.md)）。

### 4.3.3 可选 RAG 增强

hermes-okf 支持可选 RAG（LangChain + ChromaDB），`pip install hermes-okf[rag]` 后可用 DirectoryLoader 加载知识库做向量检索。

## 4.4 tool schema（JSON Schema）定义

为每个工具定义 JSON Schema，作为模型调用契约：

```json
{
  "name": "specweave_insight",
  "description": "对给定数据/问题执行洞察（根因分析），返回现象/根因/影响/建议四元组",
  "parameters": {
    "type": "object",
    "properties": {
      "topic": {
        "type": "string",
        "description": "要分析的问题或数据主题"
      },
      "depth": {
        "type": "string",
        "enum": ["light", "standard", "deep"],
        "description": "分析深度"
      }
    },
    "required": ["topic"]
  }
}
```

**转换规则**：
- 命令的必填输入 → `required`
- 命令的可选参数 → `properties` 中可选字段
- 枚举选项（如深度）→ `enum`

## 4.5 相关章节

- 能力映射：[SpecWeave 能力盘点与映射矩阵](02-capability-mapping.md)
- 权限安全：[权限认证流程](05-auth-permission.md)
- 调用示例：[调用方式示例](06-usage-examples.md)
