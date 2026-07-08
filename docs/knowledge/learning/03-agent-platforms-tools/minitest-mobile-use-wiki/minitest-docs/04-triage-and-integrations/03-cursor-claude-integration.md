---
title: "Cursor和Claude集成"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/03-cursor-claude-integration.toml"
date: "2026-07-07"
tags: ["minitest", "cursor", "claude", "ide", "mcp", "cli", "集成"]
summary: "介绍如何通过CLI和MCP服务器将miniTest与Cursor、Claude Code等AI编码助手集成，从IDE编写测试故事和触发运行。"
---
> 来源：https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude

# Cursor和Claude集成

您的编码代理已经知道您刚刚发布的功能。接入miniTest，它也会为您编写测试。

有两种接入方式，它们可以做相同的事情。选择适合您设置的方式，或两者都使用。

## CLI（命令行工具）

CLI附带一个捆绑的代理技能。安装后，您编辑器的代理使用与您在shell中使用的相同的`minitest`命令，对[故事结构](https://www.minitap.ai/docs/minitest/suite/anatomy)、标准规则和依赖关系有相同的理解。

### 安装CLI后可做的更多事情

CLI也是脚本、本地开发和上传手动构建的合适界面：

```shellscript
# 列出您可以看到的应用
minitest apps list

# 上传构建
minitest --app myapp build upload ./path/to/build.ipa

# 为一个用户故事启动运行（等待直到完成）
minitest --app myapp run start "Sign up" --android-build 8f9c... --watch

# 启动覆盖所有用户故事的运行
minitest --app myapp run all --ios-build 4e2b... --android-build 8f9c...
```

所有命令都接受`--json`用于脚本编写。使用`--app <id-or-name>`定位应用，或在每个shell中设置一次`export MINITEST_APP_ID=...`。

有关每个命令和标志，请参阅[CLI命令参考](https://www.minitap.ai/docs/minitest/reference/cli-commands)。

开源地址：[github.com/minitap-ai/minitest-cli](https://github.com/minitap-ai/minitest-cli)。

## MCP服务器

MCP服务器为您的代理提供对miniTest后端的直接访问。它适用于**任何MCP兼容客户端**：Cursor、Claude Code、Windsurf、Cline、Continue，或任何其他支持Model Context Protocol的工具。

### MCP服务器安装

在编辑器中安装miniTest MCP服务器。仪表板的引导流程为您提供一行命令：

```shellscript
npx add-mcp https://testing-service.app.minitap.ai/mcp/ -g -n minitest
```

您的代理在首次使用时会提示您进行身份验证。

### 您的代理可以做什么

#### 用户故事

列出、创建、更新和删除用户故事。连接依赖关系。附加配置文件和文件。

#### 运行

为单个故事或整个套件创建运行。轮询状态，读取每个标准的结果。

#### 配置

为每个应用设置配置文件，更新Mini的记忆，读取当前应用配置。

#### 文档

在不离开编辑器的情况下搜索和阅读miniTest文档。

有关每个工具及其payload，请参阅[MCP工具参考](https://www.minitap.ai/docs/minitest/reference/mcp-tools)。

---

> **下一章**：[GitHub集成 →](04-github-integration.md)
