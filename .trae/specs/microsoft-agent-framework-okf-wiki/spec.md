---
id: "microsoft-agent-framework-okf-wiki"
title: "Microsoft Agent Framework OKF 知识包"
theme: "knowledge-learning"
status: "in-progress"
created: "2026-11-10"
source: "https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/ + https://learn.microsoft.com/zh-cn/agent-framework/"
route: "summary-then-rewrite"
---

# Microsoft Agent Framework OKF 知识包 — 规格

## Overview

- **Summary**：把 Build 2026 官方公告博文与 Microsoft Learn `agent-framework` 中文文档中心系统学习后，转化为一个 OKF v0.2 知识包，落到 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/microsoft-agent-framework/`。
- **Purpose**：给中文读者一份可溯源、可操作的 MAF 学习路径：从 1.0 定位与快速开始，到代理管道、Harness、工具/技能、记忆/RAG/安全、工作流、托管运维、迁移与 Build 2026 新特性。
- **Target users**：已具备 Python 或 .NET 基础、准备把 Agent 从原型推进到生产的开发者；做框架选型的技术负责人；需要理解 MAF 与 AutoGen/Semantic Kernel 关系的学习者。

## Goals

1. 以官方文档为主信源，完整覆盖 MAF 的核心概念与操作路径，不以单篇博文替代文档。
2. 所有数字、日期、包名、API 名登记 F 编号并可回溯；厂商自述数据显式标注。
3. 设置 `examples/`，因为文档提供可复现的安装/代码/调用流程（操作可复现性两问皆“是”）。
4. 接入 `jishu/ai/frameworks` 分组索引与全库计数，保持 toctree 与链接可达。
5. 明确时效边界：MAF 迭代快（2026-04 GA，至 2026-10 已到 1.21），设 `stale_after` 并列出已知边界。

## Non-Goals

- 不做源码级逐行解读（信源是官方文档与 README，不是本地源码树；如需源码解读应改用 `source-code-to-okf-wiki`）。
- 不评测 MAF 与其他框架的优劣，不给出选型结论性排名。
- 不复制官方文档全文；概念文档为重构后的原创中文说明。
- 不覆盖 Go SDK 的完整教程（仅说明其预览状态与能力边界）。

## 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/frameworks/microsoft-agent-framework/` | **采用** | 主线实体是 Agent/LLM 应用框架；`frameworks` 已有 ai-agent、langchain-ai、pocketflow 等单束/多束项目目录，语义匹配 |
| `jishu/ai/ecosystems/microsoft/` | 否 | 新建厂商分组超出单束范围；MAF 是框架而非厂商生态全景 |
| `jishu/ai/practice/` | 否 | 内容是可操作框架教程，不是工程方法论/行业洞察 |

## 骨架判定（操作可复现性两问）

1. 文档是否包含读者可照做的安装/配置/代码/调用流程？→ **是**（pip/dotnet 安装、hello agent、工具、Harness、工作流、托管）。
2. 这些流程是否具备可复现性（版本、输入输出、步骤顺序）？→ **是**（文档给出包名、代码、运行命令与预期输出）。

结论：设 `examples/`，收录 5 篇可演练示例。

## 目录骨架

```
microsoft-agent-framework/
├── index.md
├── log.md
├── concepts/            # 10 篇
│   ├── 00-overview.md
│   ├── 01-quickstart.md
│   ├── 02-agent-architecture.md
│   ├── 03-harness.md
│   ├── 04-tools-skills-mcp.md
│   ├── 05-memory-rag.md
│   ├── 06-security-fides.md
│   ├── 07-workflows.md
│   ├── 08-hosting-operations.md
│   └── 09-build2026-migration.md
├── examples/            # 5 篇
│   ├── 00-hello-agent.md
│   ├── 01-tool-and-approval.md
│   ├── 02-harness-session.md
│   ├── 03-workflow-checkpoint.md
│   └── 04-hosted-and-handoff.md
└── references/
    ├── article-source.md
    └── verification.md
```

## 质量门

- G1：事实清单不含因果判断词；观点/厂商自述与事实分层。
- G2：每个概念文档的结论均有 F 编号支撑；关键差异（Go 预览、压缩启用条件、CodeAct 限制）在正文落实。
- G3：模式/结论可迁移到非 MAF 场景（如“框架收敛”“harness 化”“确定性信息流控制”）。
- G4：行动项与示例可独立执行，命令与包名可核对。
- 机械门禁：UTF-8 严格解码、双份 F 编号一致、toctree 条目文件存在、相对链接可达、计数同步、敏感路径零残留。
