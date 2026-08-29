---
type: Concept
title: "安装与配置"
description: "Jira 集成插件安装与配置完整指南，涵盖六种安装方式、凭证文件配置、Server/DC 与 Cloud 的认证差异、环境校验命令。"
tags: ["jira", "installation", "configuration", "credentials", "authentication", "uv"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T00:00:00Z" }
status: stable
stale_after: "2027-08-29T00:00:00Z"
sources:
  - resource: "/references/source-code.md"
    type: "source-code"
    trust: high
  - resource: "/references/official-docs.md"
    type: "official-docs"
    trust: high
---
# 第 2 章：安装与配置

本章介绍 jira-skill 的六种安装方式与凭证配置方法，帮助读者完成从安装到可用的完整准备。

## 2.1 安装方式

### 2.1.1 Marketplace（推荐）

先添加 Netresearch 市场，再浏览安装技能：

```bash
# Claude Code
/plugin marketplace add netresearch/claude-code-marketplace
```

### 2.1.2 npx（skills.sh）

适用于任何兼容 Agent Skills 标准的智能体：

```bash
npx skills add https://github.com/netresearch/jira-skill --skill jira-communication
npx skills add https://github.com/netresearch/jira-skill --skill jira-syntax
```

### 2.1.3 下载 Release

下载[最新发布版本](https://github.com/netresearch/jira-skill/releases/latest)并解压到智能体的技能目录。

### 2.1.4 Git Clone

```bash
git clone https://github.com/netresearch/jira-skill.git
```

### 2.1.5 Composer（PHP 项目）

```bash
composer require netresearch/jira-skill
```

依赖 [netresearch/composer-agent-skill-plugin](https://github.com/netresearch/composer-agent-skill-plugin)。

### 2.1.6 npm（Node 项目）

```bash
npm install --save-dev \
  @netresearch/agent-skill-coordinator \
  github:netresearch/jira-skill
```

依赖 [@netresearch/agent-skill-coordinator](https://github.com/netresearch/node-agent-skill-coordinator)，它会在 `node_modules` 中发现技能并通过 `postinstall` 钩子注册到 `AGENTS.md`。若使用 pnpm，需额外允许该协调器的 postinstall：

```json
{
  "pnpm": {
    "onlyBuiltDependencies": ["@netresearch/agent-skill-coordinator"]
  }
}
```

## 2.2 运行环境准备

脚本依赖 **Python 3.10+** 与 **uv**。若尚未安装 uv：

```bash
pip install uv
```

## 2.3 凭证配置

脚本通过环境变量读取 Jira 凭证，支持两种配置载体。

### 2.3.1 环境文件 `~/.env.jira`

最常用的方式，在用户主目录创建 `~/.env.jira`：

**Jira Cloud**（用户名是邮箱）：

```bash
JIRA_URL=https://your-org.atlassian.net
JIRA_USERNAME=you@example.com
JIRA_API_TOKEN=your-api-token
```

**Jira Server/Data Center**：

```bash
JIRA_URL=https://jira.example.com
JIRA_PERSONAL_TOKEN=your-personal-token
```

### 2.3.2 多配置文件 `~/.jira/profiles.json`

需要连接多个 Jira 实例时，使用配置文件并按 `--profile` 切换：

```json
{
  "profiles": {
    "myinstance": {
      "url": "https://jira.example.com",
      "token": "..."
    }
  }
}
```

## 2.4 认证方式对比

| 维度 | Jira Cloud | Jira Server/DC |
|------|-----------|----------------|
| 环境变量 | `JIRA_URL` + `JIRA_USERNAME` + `JIRA_API_TOKEN` | `JIRA_URL` + `JIRA_PERSONAL_TOKEN` |
| 用户标识 | `accountId`（如 `5b10ac8d82e05b22cc7d4ef5`） | `username`（如 `john.doe`） |
| 认证机制 | Bearer Token / Basic Auth | Personal Access Token |

## 2.5 环境校验

安装并配置完成后，先进行环境设置校验与连接校验：

```bash
# 交互式凭证配置引导（可选）
uv run scripts/core/jira-setup.py

# 校验环境配置是否完整、能否连通 Jira
uv run scripts/core/jira-validate.py
```

`jira-validate.py` 会检查凭证是否存在、Jira 实例是否可达。若校验失败，参考第 8 章故障排查。

## 相关概念

- [架构设计](/concepts/01-architecture.md)：理解插件架构
- [快速开始](/concepts/03-quickstart.md)：安装后快速上手
- [故障排查](/concepts/08-troubleshooting.md)：安装问题排查
- [官方文档信源](/references/official-docs.md)：外部参考资源