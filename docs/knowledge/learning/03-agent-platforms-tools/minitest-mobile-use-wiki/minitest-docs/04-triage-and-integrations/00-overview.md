---
title: "问题分类与集成总览"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/triage"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/00-overview.toml"
date: "2026-07-07"
tags: ["minitest", "triage", "integration", "问题分类", "集成"]
summary: "问题分类与集成章节导航，包含问题分类流程、Mini改进建议、Cursor/Claude集成、GitHub集成和Slack集成。"
---
# 问题分类与集成

本章介绍如何对测试失败进行分类处理，以及miniTest与各种开发工具的集成方式。当测试发现问题时，您可以在仪表板或Slack中进行分类；同时miniTest可以与您日常使用的IDE、GitHub、Slack等工具无缝集成。

## 章节导航

| 序号 | 标题 | 内容概要 | 文件 |
|---|---|---|---|
| 1 | 问题分类 | 问题的结构、分类操作（确认/非bug/已解决）、严重性覆盖 | [01-triaging-issues.md](01-triaging-issues.md) |
| 2 | Mini改进建议 | Mini在测试过程中主动发现的UX问题和边缘情况，与问题的区别 | [02-mini-suggestions.md](02-mini-suggestions.md) |
| 3 | Cursor和Claude集成 | 通过CLI和MCP服务器从IDE编写故事、触发运行和查看结果 | [03-cursor-claude-integration.md](03-cursor-claude-integration.md) |
| 4 | GitHub集成 | GitHub App安装、PR检查、自动构建、触发运行 | [04-github-integration.md](04-github-integration.md) |
| 5 | Slack集成 | Slack安装、频道路由、运行心跳、线程内分类 | [05-slack-integration.md](05-slack-integration.md) |

## 问题分类工作流

```
测试失败 → 创建Issue → 分类处理 → （确认/非bug/已解决）→ Mini学习反馈
```

### 三种分类操作

1. **Acknowledge（确认）**：您已看到问题，暂无其他操作
2. **Not a bug（非bug）**：有意更改、不稳定标准或误报
3. **Resolved（已解决）**：底层问题已修复，下一次干净运行将关闭问题

### 集成生态

- **IDE集成**：Cursor、Claude Code等MCP兼容客户端
- **代码托管**：GitHub PR检查、自动构建、GitHub Actions
- **团队沟通**：Slack实时通知、线程内操作

---

> **开始阅读**：[第1章 — 问题分类 →](01-triaging-issues.md)
