---
id: p1-17-daoyan-mcp-skill-spec
title: MCP 技能开发与 REST API 集成规范——以道衍为例
source: d:\spaces\chaos\daoApps\dao-yan\.trae\skills\daoyan-wisdom\SKILL.md
source_type: file
category: tech
tags:
  - mcp
  - skill
  - api-integration
  - daoyan
  - model-context-protocol
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T12:35:00Z
updated_at: 2026-08-02T12:50:00Z
version: v0.1.0
reviewer: chaos-coordinator
review_notes: approved - MCP 技能开发规范完整，包含 API 集成和回答规范模板
summary: 以道衍（DaoYan）MCP Server 为例，说明 AI IDE 技能（Skill）定义、MCP 工具配置、REST API 调用与回答规范的完整模式
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p1-17-daoyan-mcp-skill-spec.md
archived_at: 2026-08-02T04:55:45Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T04:55:45Z archived from d:\spaces\chaos\.agents\knowledge\temp\tech\p1-17-daoyan-mcp-skill-spec.md to D:\spaces\SpecWeave\.agents\docs\knowledge\tech\p1-17-daoyan-mcp-skill-spec.md
---

# MCP 技能开发与 REST API 集成规范——以道衍为例

## 技能（Skill）定义结构

技能是 AI IDE 中自动触发的领域知识包，标准结构：

```markdown
---
name: skill-name
description: >
  技能描述，说明触发场景、核心能力、支持的调用方式。
  触发场景：列出用户会说的关键词/短语，如"问道衍"、"从道家角度看"
---

# 技能标题

## 描述
核心能力说明，关键特性列表。

## 使用场景
列出应触发本技能的具体场景。

## 指令
### 一、调用方式
（MCP 工具 / REST API 两种方式）
### 二、领域核心知识
（回答必须遵守的领域知识）
### 三、回答规范
（回答风格、引用规则、注意事项）
### 四、应用入口
（Web 应用链接）

## 示例
给出 2-4 个典型使用示例。
```

### Frontmatter 关键字段
| 字段 | 说明 |
|------|------|
| `name` | 技能唯一标识符 |
| `description` | 触发条件描述，必须明确列出触发词/场景 |

## MCP 工具定义模式

以道衍 MCP Server 为例，标准 3 工具组合：

| 工具名 | 功能 | 必填参数 |
|--------|------|----------|
| `ask_daoyan` | 向道衍提问 | `question` |
| `search_chapters` | 按关键词搜索章节 | `keyword` |
| `get_chapter` | 获取指定章节内容 | `chapter_number` |

### MCP 配置示例

**Trae IDE / Cursor**（`.trae/mcp.json` 或 `.cursor/mcp.json`）：
```json
{
  "mcpServers": {
    "daoyan": {
      "url": "https://your-supabase-url.supabase.co/functions/v1/daoyan-mcp",
      "headers": {
        "Authorization": "Bearer YOUR_ANON_KEY"
      }
    }
  }
}
```

**Claude Desktop**（`claude_desktop_config.json`）结构类似，使用 `command` + `args` 启动本地进程，或 `url` 连接远程服务。

> 注意：MCP 协议默认返回完整结果（非流式）。如需流式输出，使用 REST API 的 `stream: true`。

## REST API 集成模式

### 请求格式
```bash
curl -X POST "https://your-api-endpoint" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -d '{
    "question": "问题内容",
    "model": "provider/model-name",
    "conversation_history": [...],
    "enable_web_search": false,
    "stream": false,
    "locale": "zh-CN"
  }'
```

### 标准请求参数
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `question` | string | 是 | - | 问题内容 |
| `model` | string | 否 | 默认模型 | 模型 ID（provider/model 格式） |
| `conversation_history` | array | 否 | `[]` | 多轮对话历史 |
| `enable_web_search` | boolean | 否 | `false` | 是否联网搜索 |
| `stream` | boolean | 否 | `false` | 是否 SSE 流式输出 |
| `locale` | string | 否 | `zh-CN` | 响应语言 |

### 标准响应格式（非流式）
```json
{
  "answer": "回答内容...",
  "thinking": "（可选）模型思考过程",
  "sources": [{"title": "...", "url": "...", "snippet": "..."}]
}
```

### 多模型配置表
建议在技能文档中提供可选模型清单：

| 模型 ID | 名称 | 特点 |
|---------|------|------|
| `z-ai/glm-5` | GLM 5 | 默认推荐，支持深度思考 |
| `anthropic/claude-sonnet-4.5` | Claude Sonnet 4.5 | 复杂推理能力强 |
| `google/gemini-2.5-pro` | Gemini 2.5 Pro | 快速，多语言能力强 |
| `openai/gpt-4.1` | GPT-4.1 | 通用能力均衡 |
| `deepseek/deepseek-r1` | DeepSeek R1 | 开源，推理能力优秀 |

## 领域知识嵌入规范

技能文档中必须包含**回答必须遵守**的领域核心知识，例如道衍的帛书版规则：

### 章序规则示例
- 帛书版全书81章：德经（第1-44章）在前，道经（第45-81章）在后
- 帛书第1章 = 今本第38章（"上德不德"）
- 帛书第45章 = 今本第1章（"道可道也"）

### 关键差异对照表
| 帛书版（正确） | 传世版（常见但有误） | 差异原因 |
|----------------|---------------------|----------|
| 道可道也，非恒道也 | 道可道，非常道 | 汉讳改"恒"为"常" |
| 大器免成 | 大器晚成 | "免"=无需完成，义理不同 |

## 回答规范

制定明确的回答约束，避免 AI 产生领域错误：
1. **引文准确**：引用原文时逐字准确，不得混入其他版本文字
2. **版本标注**：引用时标注版本来源和章节号
3. **差异主动说明**：用户引用常见错误版本时，主动指出差异并解释原因
4. **精炼有力**：引用1-3段最相关原文即可
5. **语言一致**：与用户使用相同语言回答
6. **不拒绝回答**：对任何话题都能从领域角度给出启发

## 典型示例模板

```
**示例 N：[场景名称]**
- 用户："用户输入示例"
- 调用：`tool_name(param=value)`
- 期望：描述期望的输出行为和要点
```

## 部署技术栈参考

道衍后端采用 Supabase Edge Functions (Deno) + SSE 流式，可作为 Serverless AI API 参考架构：
- **前端**：React 19 + TypeScript + Vite
- **后端**：Supabase Edge Functions (Deno)
- **AI**：多模型路由（Claude/GPT/Gemini/GLM/DeepSeek）
- **搜索**：四层容错（DuckDuckGo HTML → Lite → Brave → Google）
- **协议**：MCP (JSON-RPC 2.0) + REST API + SSE 流式

---

**来源参考**：
- [daoyan-wisdom/SKILL.md](file:///d:/spaces/chaos/daoApps/dao-yan/.trae/skills/daoyan-wisdom/SKILL.md)
- 相关项目：[P1-10 DaoYan 项目概览](p1-10-daoyan-project-overview.md)
- 在线体验：https://167c2bc1450e4ea3a0dc4b07c5873069.prod.enter.pro
