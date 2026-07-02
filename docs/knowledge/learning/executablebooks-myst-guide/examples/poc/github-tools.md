---
source: "MyST MCP指令PoC示例 - GitHub Tools"
version: "1.0.0"
description: "示例MyST文档：使用mcp:指令定义MCP Server"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/executablebooks-myst-guide/examples/poc/github-tools.toml"
id: "poc-github-tools"
title: "GitHub Tools MCP Server"
---
# GitHub Tools MCP Server

这是一个使用 MyST `{mcp:*}` 指令定义 MCP Server 的示例文档。
该文档既是人类可读的工具说明文档，也是可被 `myst_mcp_server.py` 直接
解析并运行为 MCP Server 的机器可执行规范。

本示例定义了一个模拟的 GitHub 工具集，提供 Issue 管理和代码仓库查询功能。

```{mcp:server} github-tools
:version: 1.0.0
:transport: stdio

GitHub MCP 工具集，提供代码仓库和 Issue 管理能力。
工具使用 mock 实现（PoC），用于演示"MyST文档即MCP Server"概念。

```{mcp:tool} list_repositories
:description: 列出当前用户可访问的GitHub仓库

获取当前认证用户有权限访问的所有仓库列表，支持按类型和排序筛选。

```{mcp:param} type
:type: string
:required: false
:default: owner
:enum: owner,all,public,private,member

仓库筛选类型：owner（拥有的）、all（所有）、public/private（公开/私有）、member（作为成员的）
```

```{mcp:param} per_page
:type: integer
:required: false
:default: 30

每页返回数量，最大100
```

```{mcp:param} sort
:type: string
:required: false
:default: updated
:enum: created,updated,pushed,full_name

排序方式
```
```

```{mcp:tool} create_issue
:description: 在指定仓库创建一个新的Issue

在指定的GitHub仓库中创建一个新的Issue，支持设置标题、正文、标签、负责人等。

```{mcp:param} repo
:type: string
:required: true

仓库全名，格式为 owner/repo（如 "octocat/Hello-World"）
```

```{mcp:param} title
:type: string
:required: true

Issue 标题，简洁明了描述问题
```

```{mcp:param} body
:type: string
:required: false

Issue 详细描述正文，支持 Markdown 格式
```

```{mcp:param} labels
:type: array
:required: false

要添加的标签列表，如 ["bug", "good first issue"]
```

```{mcp:param} assignees
:type: array
:required: false

负责人用户名列表
```
```

```{mcp:tool} get_issue
:description: 获取指定Issue的详细信息

根据仓库名和Issue编号获取Issue的完整信息，包括状态、评论数、标签等。

```{mcp:param} repo
:type: string
:required: true

仓库全名（owner/repo格式）
```

```{mcp:param} issue_number
:type: integer
:required: true

Issue编号
```
```

```{mcp:tool} search_code
:description: 在GitHub上搜索代码片段

使用关键词搜索GitHub上的公开代码，支持按语言、仓库、文件路径等过滤。

```{mcp:param} query
:type: string
:required: true

搜索查询字符串，支持GitHub搜索语法
```

```{mcp:param} language
:type: string
:required: false

编程语言过滤，如 "python"、"javascript"、"go"
```
```

```{mcp:resource} repo-readme
:uri: github://{repo}/readme
:mime-type: text/markdown
:description: 获取指定仓库的README内容
# {repo}

这是从 `{repo}` 仓库读取的 README 示例内容。

## 安装

使用包管理器安装：`pip install {repo}`

## 使用方法

请参阅官方文档获取更多信息。
```

```{mcp:resource} server-info
:uri: github://server-info
:mime-type: application/json
:description: 服务器版本和能力信息
{
  "server": "github-tools",
  "version": "1.0.0",
  "capabilities": {
    "tools": ["list_repositories", "create_issue", "get_issue", "search_code"],
    "resources": ["repo-readme", "server-info"],
    "prompts": ["create-bug-report"]
  }
}
```

```{mcp:prompt} create-bug-report
:description: 生成一个标准的Bug报告模板

帮助用户创建格式规范的Bug报告，包含复现步骤、期望行为、实际行为等结构。

```{mcp:arg} repo
:type: string
:required: true
:description: 发现Bug的仓库
```

```{mcp:arg} feature_name
:type: string
:required: false
:default: "该功能"
:description: 出现Bug的功能名称
```

请为仓库 {repo} 创建一个标准的Bug报告，针对功能：{feature_name}。

报告应包含以下部分：
1. Bug摘要
2. 复现步骤（详细，每步可操作）
3. 期望行为
4. 实际行为
5. 环境信息（OS、版本、依赖等）
6. 附加信息（截图、日志等）
```
