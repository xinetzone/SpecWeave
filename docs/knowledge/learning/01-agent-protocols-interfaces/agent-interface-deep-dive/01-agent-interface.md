---
id: "agent-interface-chapter"
title: "Agent Interface：能力契约层"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-interface-deep-dive/01-agent-interface.toml"
source: "spec:agent-interface-deep-dive"
category: "learning"
tags: ["agent", "interface", "mcp", "tool", "json-schema", "skill"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "Agent视角的Interface：能力契约，JSON Schema驱动的Tool/Skill/Agent声明模式"
---
# Agent Interface：能力契约层

## 什么是Agent Interface？

在Agent生态中，**Interface不是OOP语言级的`interface`关键字，而是声明式的能力契约**——它回答"这个Tool/Skill/Agent能做什么、需要什么参数、返回什么结果"。

通用编程中的Interface（如TypeScript的`interface`、Java的`interface`）是编译期类型约束；而Agent Interface是**运行时可发现、可解析、语言无关的能力声明**，核心载体是JSON Schema。

> 💡 **基础概念回顾**：如果你对通用Interface（OOP接口、鸭子类型、面向接口编程）不熟悉，请先阅读[通用Wiki - Interface章节](../interface-api-abi-protocol-wiki/01-interface.md)。

## Agent Interface的核心特征

| 特征 | 说明 |
|------|------|
| **声明式** | 只定义"是什么"，不定义"怎么实现"——Tool Interface只描述参数Schema，不暴露实现代码 |
| **Schema驱动** | 以JSON Schema为核心标准，输入输出都有结构化Schema定义 |
| **语言无关** | Interface用JSON/JSON Schema表达，不绑定任何特定编程语言 |
| **可发现性** | Agent可以在运行时通过API动态获取Interface定义（如MCP的`tools/list`） |
| **组合性** | 多个Tool Interface可以组合成一个Agent的能力集，Skill可以引用多个Tool |

## Agent Interface的三种主要形态

### 1. MCP Tool定义

MCP（Model Context Protocol）中每个Tool都是一个Interface，通过`inputSchema`声明参数契约：

```typescript
// 案例1：TypeScript中定义MCP Tool Interface
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({ name: "calculator", version: "1.0.0" });

// Tool Interface定义：名称 + 描述 + Zod Schema（自动转JSON Schema）
server.tool(
  "calculate",
  "执行数学计算，支持加减乘除和基本函数",
  {
    expression: z.string().describe("数学表达式，如 '2 + 3 * 4'"),
    precision: z.number().int().min(0).max(10).optional()
      .describe("结果精度，默认2位小数")
  },
  async ({ expression, precision = 2 }) => {
    // 实现逻辑...
    return { content: [{ type: "text", text: String(result) }] };
  }
);
```

对应的纯JSON Schema Interface：

```json
{
  "name": "calculate",
  "description": "执行数学计算，支持加减乘除和基本函数",
  "inputSchema": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "数学表达式，如 '2 + 3 * 4'"
      },
      "precision": {
        "type": "integer",
        "minimum": 0,
        "maximum": 10,
        "default": 2,
        "description": "结果精度，默认2位小数"
      }
    },
    "required": ["expression"]
  }
}
```

### 2. Skill描述文件

本系统中的Skill通过`SKILL.md`文件声明能力Interface，包含name、description、triggers等元数据：

```yaml
# Skill Interface示例（SKILL.md frontmatter）
---
name: mcp-builder
description: 构建高质量MCP Server的指南，适用于集成外部API或开发Agent工具
triggers:
  -   - "创建MCP Server"
  -   - "开发MCP工具"
  -   - "集成外部API到MCP"
---
```

### 3. A2A Agent Card

A2A（Agent-to-Agent）协议中，Agent通过Agent Card声明自身能力Interface，支持跨Agent发现与协作。

## Python中的隐式Tool Interface

Python生态中常用类型注解+docstring作为隐式Interface，由框架自动转换为JSON Schema：

```python
# 案例2：Python中用类型注解定义Tool Interface
from typing import Optional
from pydantic import Field

def calculate(
    expression: str = Field(description="数学表达式，如 '2 + 3 * 4'"),
    precision: int = Field(default=2, ge=0, le=10, description="结果精度，0-10")
) -> str:
    """执行数学计算，支持加减乘除和基本函数。"""
    # 实现逻辑...
    return str(result)

# 框架（如LangChain、AutoGen）会自动从函数签名+Field+docstring
# 提取出JSON Schema格式的Tool Interface
```

## Agent Interface vs 通用OOP Interface

| 维度 | OOP Interface | Agent Interface |
|------|--------------|-----------------|
| 检查时机 | 编译期 | 运行时 |
| 表达格式 | 语言语法（`interface`关键字） | JSON Schema / 声明式元数据 |
| 语言绑定 | 绑定特定语言 | 语言无关 |
| 发现方式 | 源码import | 运行时API调用（如tools/list） |
| 消费者 | 同语言编译器/IDE | LLM / 跨语言Agent Runtime |

## 章节导航

| 章节 | 链接 |
|------|------|
| 总览 | [00 - 总览](00-overview.md) |
| 上一章 | [00 - 总览](00-overview.md) |
| 下一章 | [02 - Agent API](02-agent-api.md) |
| 对比分析 | [05 - 对比分析](05-agent-comparison.md) |

---

**上一章**：[00 - 总览](00-overview.md) | **下一章**：[02 - Agent API：可调用方法层](02-agent-api.md)
