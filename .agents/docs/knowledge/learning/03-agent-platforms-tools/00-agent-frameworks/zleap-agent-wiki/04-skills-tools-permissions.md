---
id: "zleap-agent-wiki-skills-tools-permissions"
title: "Skill 与工具权限"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "skill", "skill-registry", "sensitivity-audit", "permission", "approval", "mcp", "tool-policy"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent Skill 机制与工具权限：SKILL.md 入口、SkillRegistry、敏感性审计、token 预算、调用策略、信任状态；request_approval/full_access 权限模式；MCP Runtime 与 MCP Secrets。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 04 Skill 与工具权限

本章讲 Zleap-Agent 的两大安全与能力维度：**Skill（可复用能力包）**与**工具权限（安全边界）**。

## 4.1 Skill 是什么

> **工具是 API，Skill 是工作流、说明、示例与配套资源。**

Skill 是一类可复用能力包，通常以 `SKILL.md` 为入口文件。它帮 Agent 完成"一类工作"而非"一次调用"。

## 4.2 Skill 的代码模型

`packages/core/src/skills.ts` 定义了 `SkillRegistry` 与 `SkillDefinition`：

- `SkillRegistry`：内存注册表，`register` / `get` / `list` / `search`。
- `skillDefinitionFromRecord`：把数据库记录投影为运行时 `SkillDefinition`。
- `searchSkillManifests`：按查询词对 Skill 做打分搜索（支持中英文分词）。

### 关键元数据

| 字段 | 含义 |
|------|------|
| `sections` | 指令中各章节的索引（`indexSkillSections` 解析 Markdown 标题） |
| `tokenBudget` | 该 Skill 的 token 预算（默认 450，上限 32000） |
| `sensitivity` | 敏感性审计结果（`clear` / `review`） |
| `invocationPolicy` | 调用策略（`implicit` / `explicit_only` / `disabled`） |
| `trustStatus` | 信任状态（`trusted` / `review_required` / `blocked`） |
| `source` | 来源类型（`db` / `project` / `user` / `admin` / `system` / `imported`） |

### 敏感性审计（`auditSkillSensitivity`）

自动扫描指令中的敏感信息：

| 检查 | 严重度 | 正则示例 |
|------|--------|---------|
| 私钥 | high | `-----BEGIN ... PRIVATE KEY-----` |
| 带凭据的 URL | high | `scheme://user:pass@host` |
| 疑似密钥 | medium | `api_key/token/secret/password = ...` |

命中任何一条 → `status: 'review'`，否则 `clear`。

### 架构洞察

> **洞察 7：Skill 自带"敏感性审计 + token 预算 + 信任状态"，把安全治理植入能力包本身。** 这比"所有 Skill 一视同仁"更稳——高风险 Skill 需要 `review_required`，可单独控制调用方式与预算（来源：`packages/core/src/skills.ts`）。

## 4.3 工具权限模型

`packages/agent/src/permissions.ts` 定义了两种权限模式：

| 模式 | 值 | 行为 | 高风险工具 |
|------|-----|------|-----------|
| **请求审批** | `request_approval`（默认） | 写文件/命令/MCP 等需确认 | 需用户审批 |
| **完全访问** | `full_access` | 高风险工具自动执行 | 自动执行（慎用） |

- `bypassesToolApproval(mode)`：`full_access` 时绕过工具审批。
- 默认 `request_approval`，符合"安全默认"原则。
- 工具级策略见 `packages/core/src/toolPolicy.ts` 的 `ToolPolicy`，用于统一工具访问控制。

## 4.4 MCP Runtime 与 MCP Secrets

- **MCP Runtime**（`packages/agent/src/mcpRuntime.ts`）：负责运行与管理外部工具（MCP），包含工具执行、配置与安全机制。
- **MCP Secrets**（`packages/agent/src/mcpSecrets.ts`）：管理 MCP 服务器的密钥，避免明文暴露。
- 相关执行器：`packages/agent/src/sdkMcpExecutor.ts`、`packages/runtime/src/sdkMcpExecutor.ts`。

### 架构洞察

> **洞察 8：MCP 作为一等工具源接入，密钥与运行时分离。** MCP 服务器可被动态发现、执行，且密钥集中管理，避免把密钥散落在各工具配置里（来源：`packages/agent/src/mcpRuntime.ts`、`mcpSecrets.ts`）。

## 本章小结

- Skill 是"工作流 + 说明 + 资源"的能力包，以 `SKILL.md` 为入口，自带敏感性审计、token 预算、调用策略与信任状态。
- 工具权限分 **request_approval（默认）/ full_access** 两档，默认安全。
- MCP 作为外部工具源接入，密钥与运行时分离管理。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [03 分区记忆系统](./03-memory-system.md) | [README](./README.md) | → [05 模型提供方与运行时入口](./05-model-providers-runtime.md) |