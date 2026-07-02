---
source: "MyST MCP指令演示示例"
name: "github-tools"
version: "1.0.0"
description: "GitHub代码仓库和Issue管理MCP工具集"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/executablebooks-myst-guide/examples/mcp-server-demo.toml"
title: "GitHub Tools MCP Server"
---
# GitHub Tools MCP Server

:::{mcp:server} github-tools
:version: 1.0.0
:transport: stdio

GitHub MCP工具集，提供代码仓库和Issue管理能力。
支持创建Issue、查询PR、列出仓库等常用操作。

::::{mcp:tool} create_issue
:description: 在指定仓库创建Issue

在GitHub仓库中创建一个新的Issue，可以指定标题、内容、标签和指派人。

:::::{mcp:param} repo
:type: string
:required: true
仓库全名，格式为 owner/repo（如 "octocat/Hello-World"）
:::::

:::::{mcp:param} title
:type: string
:required: true
Issue标题，简短描述问题
:::::

:::::{mcp:param} body
:type: string
:required: false
Issue详细描述内容，支持Markdown格式
:::::

:::::{mcp:param} labels
:type: array[string]
:required: false
标签列表，如 ["bug", "enhancement"]
:::::

:::::{mcp:param} assignee
:type: string
:required: false
指派人的GitHub用户名
:::::
::::

::::{mcp:tool} list_repositories
:description: 列出用户可访问的仓库

获取当前认证用户有权访问的所有仓库列表，支持分页和过滤。

:::::{mcp:param} per_page
:type: integer
:required: false
:default: 30
每页返回数量，最大100
:::::

:::::{mcp:param} page
:type: integer
:required: false
:default: 1
页码，从1开始
:::::

:::::{mcp:param} visibility
:type: string
:required: false
:enum: all, public, private
仓库可见性过滤
:::::
::::

::::{mcp:tool} get_pull_request
:description: 获取Pull Request详情

根据PR编号获取指定仓库的Pull Request详细信息，包括状态、审查者和CI结果。

:::::{mcp:param} repo
:type: string
:required: true
仓库全名（owner/repo格式）
:::::

:::::{mcp:param} pr_number
:type: integer
:required: true
Pull Request编号
:::::
::::

::::{mcp:resource} repo://{owner}/{repo}/readme
:name: 仓库README
:mime-type: text/markdown
获取指定仓库的README文件内容
::::

::::{mcp:resource} repo://{owner}/{repo}/issues/{number}
:name: Issue详情
:mime-type: application/json
获取指定Issue的完整信息和评论
::::

::::{mcp:prompt} code-review
:description: 生成代码审查提示词

创建用于审查Pull Request的结构化提示词。

:::::{mcp:param} pr_url
:type: string
:required: true
待审查的Pull Request URL
:::::

:::::{mcp:param} focus
:type: string
:required: false
:enum: security, performance, style, all
:default: all
审查重点方向
:::::
::::
:::
