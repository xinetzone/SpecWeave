---
title: "术语表"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/reference/glossary"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/03-glossary.toml"
date: "2026-07-07"
tags: ["minitest", "glossary", "术语表", "terminology"]
summary: "miniTest在仪表板、CLI、MCP服务器和文档中使用的术语定义和规范命名。"
---
> 来源：https://www.minitap.ai/docs/minitest/reference/glossary

# 术语表

这些是miniTest在仪表板、CLI、MCP服务器和本文档中使用的术语。当文档和仪表板不一致时，以文档为准，直到仪表板跟进。

| 术语 | 含义 |
| --- | --- |
| **miniTest** | 产品名称。小写m，大写T。CLI二进制文件是`minitest`（全小写）。 |
| **Mini** | 驱动设备、编写用户故事和分类问题的AI代理。代词："it（它）"。 |
| **Workspace（工作区）** | 容纳应用、成员、集成和计费的顶级容器。 |
| **App（应用）** | 工作区内配置的移动应用。 |
| **User story（用户故事）** | 用通俗易懂的语言描述的应用中的一段旅程，带有验收标准。不是"test（测试）"、"flow（流程）"或"scenario（场景）"。 |
| **Acceptance criterion（验收标准，复数criteria）** | 用户故事中的单个可观察条件。不是"assertion（断言）"、"check（检查）"或"step（步骤）"。 |
| **Suite（套件）** | 一个应用的所有用户故事。 |
| **Run（运行）** | 一次执行事件。您点击**Run tests**，N个故事一起运行。不是"batch（批次）"。 |
| **Build（构建）** | 运行所针对的`.ipa`或`.apk`产物。 |
| **Verdict（判定结果）** | 运行或运行中故事的结果：Passed、Warning、Failed或Unprocessable。不是"result（结果）"或"status（状态）"。 |
| **Status（状态）** | 问题的生命周期状态（open、acknowledged、resolved）。与判定结果不同。 |
| **Criticality（严重性）** | 问题上的重要性标签：Critical、Warning或Pass。Mini在运行时推断它。当推断不符合您的业务实际时，您可以按问题覆盖它。 |
| **Issue（问题）** | 需要分类的失败标准。存在于Issues标签页。不是"failure（失败）"或"bug（缺陷）"。 |
| **Suggestion（建议）** | Mini在运行故事时标记的UX观察 — 验收标准之外看起来不对的东西。不是"finding（发现）"或"recommendation（推荐）"。 |
| **Fix prompt（修复提示）** | Mini为每个失败标准生成的可粘贴到剪贴板的文本块。包含根本原因、复现步骤和建议修复。 |
| **Profile（配置文件）** | 附加到用户故事的命名凭据集（用户名、密码、备注）。Mini在运行期间使用它登录。 |
| **Mini's memory（Mini的记忆）** | Mini在每次运行前读取的关于应用的额外上下文。通过MCP服务器或CLI设置。 |
| **Test Configuration（测试配置）** | 仪表板中每个应用的设置屏幕（配置文件、环境变量、Mini的记忆）。指代屏幕时作为专有名词大写；在散文中使用小写。 |
| **Dashboard（仪表板）** | 位于[app.minitap.ai](https://app.minitap.ai/)的Web应用。 |
| **Agent（代理）** | 驱动设备的AI。在技术上下文中是Mini的同义词。 |
| **CLI** | `minitest`命令行工具。请参阅[Cursor和Claude](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)。 |
| **MCP server（MCP服务器）** | Cursor、Claude Code和其他MCP客户端连接到的Model Context Protocol界面。 |
| **MCP tools（MCP工具）** | MCP服务器暴露的各个调用。请参阅[MCP工具](https://www.minitap.ai/docs/minitest/reference/mcp-tools)。 |
| **PR check（PR检查）** | MiniTest GitHub App在Pull Request上发布的GitHub状态检查。 |
| **MiniTest GitHub App** | 字面GitHub App名称（Pascal大小写，无空格）。仅在指代您在GitHub上安装的App时使用。 |

---

> **下一章**：[MCP工具参考 →](04-mcp-tools.md)
