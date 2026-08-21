---
id: "zleap-agent-wiki-faq-glossary"
title: "FAQ 与术语表"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "faq", "glossary", "workspace", "context", "memory", "rrf", "mcp", "gateway", "turn-loop"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent FAQ 与术语表：常见问题解答（适合用户、是否需要本地模型、与单一大 prompt 区别、Workspace 协作、飞书/微信接入、Skill 导入等）+ 核心术语通俗解释。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 08 FAQ 与术语表

## FAQ

### Q1：Zleap-Agent 适合什么用户？

适合：本地模型/OpenAI-compatible 模型使用者、企业内网部署者、需要权限与数据边界的工作流、以及对 Agent 运行时架构感兴趣的研究者。当前处于早期预览（v0.3.3），适合源码阅读/本地开发/反馈，不建议直接用于生产再分发。

### Q2：一定要用本地模型吗？

不需要。Zleap-Agent 面向"本地模型与 OpenAI-compatible 模型"，通过 `ZLEAP_MODEL_BASE_URL` 指向任意 OpenAI 兼容端点即可（本地模型或云端 API 均可）。仓库还包含 Anthropic provider 代码。

### Q3：与"单一大 prompt"的 Agent 有什么本质区别？

单一大 prompt 把全部工具/记忆/规则/历史塞进一个不断增长的 prompt；Zleap-Agent 把运行时按 **Workspace 拆分**，每个空间只拿它需要的上下文。这降低了对本地小模型的上下文窗口压力，也更容易做权限与数据隔离。

### Q4：多个 Workspace 之间如何协作？

所有回复先进入常驻 `session`（main）空间，由会话模型经 `switchWorkspace(space, task)` 路由到某个子空间，执行完把结果带回对话。Main→Work 深度保持在 1，避免嵌套过深。

### Q5：支持飞书 / 微信吗？

支持。`packages/gateway` 提供飞书、微信、飞书 CLI 三种适配器，经 ChannelSupervisor 管理、dedup 去重后汇入 `ConversationService`。用 `pnpm dev:gateway` 启动网关 worker。

### Q6：如何导入 / 使用 Skill？

Skill 是可复用能力包，通常以 `SKILL.md` 为入口。Web UI 提供 `skills` 相关 API（`ZLEAP_WEB_SKILLS_ROOT` 可指定本地技能目录）。Skill 自带敏感性审计、token 预算、调用策略与信任状态，可控制其是否被调用。

### Q7：记忆存在哪里？可以回滚吗？

记忆存储于 **PostgreSQL**（含 pgvector 向量检索）。选择 PostgreSQL 是因为记忆参与 Agent 每一轮运行，需要检索、隔离、审计与回滚能力。记忆分 person / event / experience 三类。

### Q8：`request_approval` 和 `full_access` 有什么区别？

`request_approval`（默认）在写文件/命令/MCP 等高风险工具调用前需用户确认；`full_access` 让高风险工具自动执行（慎用）。可用 `--yes` 在一次性模式下启用全权。

## 术语表

| 术语 | 通俗解释 |
|------|---------|
| **Workspace** | Agent 可见上下文与可执行动作的隔离边界；`main` 为常驻主空间，`work` 为派发子空间 |
| **Context Layout** | 上下文运行时布局：`System Prompt + Workspace Prompt + Tools + Memory + History` |
| **Person Memory** | 对人记忆，用户偏好与稳定事实（A 线 impressions） |
| **Event Memory** | 对事记忆，与用户/任务/空间相关的状态（B 线 work records） |
| **Experience Memory** | 经验记忆，从已完成任务沉淀的可复用方法（B 线 experience） |
| **Skill** | 以 `SKILL.md` 为入口的可复用能力包（工作流 + 说明 + 资源） |
| **RRF** | Reciprocal Rank Fusion，多路径召回按秩融合排序的算法 |
| **MCP** | Model Context Protocol，让 Agent 接入外部工具/服务器的协议 |
| **Gateway** | IM 网关，把飞书/微信等外部渠道接入 Agent 的 worker |
| **Turn Loop** | 回合循环，单次模型调用 + 工具调用直到完成/超限的循环 |
| **Approval** | 审批模式，写文件/命令/MCP 等高风险操作需用户确认 |
| **Kernel** | 工作区入口调度核心，运行 `session` 主空间并携带身份/记忆/召回 |
| **Semantic cache breakpoint** | 缓存断点，让稳定上下文可被缓存以降低成本 |

## 本章小结

- FAQ 覆盖适合人群、模型选择、与单一大 prompt 的区别、多 Workspace 协作、飞书/微信接入、Skill 导入、记忆存储与权限模式。
- 术语表给出 13 个核心术语的通俗解释，与前七章内容一一对应。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [07 快速上手指南](./07-quickstart.md) | [README](./README.md) | → 这是教程最后一章 |