---
id: github-cli-wiki-02-basic-commands
title: "基础命令指南"
source: "https://cli.github.com/manual/gh"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "repo", "issue", "gist", "browse", "basic-commands"]
---

# 基础命令指南

本章介绍 GitHub CLI（`gh`）最常用的核心命令，涵盖仓库（repo）、议题（issue）、代码片段（gist）和浏览器（browse）四大模块。每个命令包含用途说明、基本语法、常用参数和实用示例。

> **前置条件**：请确保已完成 [安装与配置指南](01-installation.md) 中的认证流程，否则本节命令将无法正常工作。

## 1. gh repo：仓库管理

`gh repo` 是管理 GitHub 仓库的核心命令组，支持克隆、创建、复刻、查看和列出仓库等操作。

### 1.1 gh repo clone

克隆一个 GitHub 仓库到本地。

**基本语法**：

```bash
gh repo clone <repository> [<directory>] [-- <git-flags>...]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `repository` | 仓库标识，格式为 `owner/repo` |
| `directory` | 可选，指定本地目录名（不指定则使用仓库名） |
| `-- <git-flags>` | 传递给 `git clone` 的额外参数（如 `--depth=1`） |

**示例**：

```bash
# 克隆自己的仓库
gh repo clone myrepo

# 克隆指定组织的仓库
gh repo clone cli/cli

# 克隆到指定目录
gh repo clone cli/cli my-gh-cli

# 浅克隆（仅获取最近一次提交）
gh repo clone cli/cli -- --depth=1
```

#### 1.1.1 URL 格式详解

`gh repo clone` 支持多种仓库标识格式，`gh` 会自动解析为对应的 GitHub URL：

| 格式 | 示例 | 解析结果 |
|------|------|----------|
| `owner/repo` | `cli/cli` | `https://github.com/cli/cli.git` |
| `repo`（当前用户） | `myproject` | `https://github.com/<当前用户>/myproject.git` |
| 完整 URL（HTTPS） | `https://github.com/cli/cli` | 直接使用 |
| 完整 URL（SSH） | `git@github.com:cli/cli.git` | 直接使用 |

```bash
# 仅提供仓库名，自动使用当前登录用户作为 owner
gh repo clone myproject

# 等价于
gh repo clone <your-username>/myproject

# 直接使用完整 HTTPS URL
gh repo clone https://github.com/torvalds/linux.git

# 直接使用完整 SSH URL
gh repo clone git@github.com:cli/cli.git
```

> **提示**：默认使用 HTTPS 协议克隆。如需使用 SSH，可通过 `gh config set git_protocol ssh` 全局设置，或使用完整 SSH URL 格式。

### 1.2 gh repo create

在 GitHub 上创建新仓库，并可选择将其克隆到本地。

**基本语法**：

```bash
gh repo create [<name>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--public` | 创建公开仓库 |
| `--private` | 创建私有仓库 |
| `--internal` | 创建内部仓库（GitHub Enterprise 专属） |
| `--clone` | 创建后立即克隆到本地 |
| `--description <string>` | 仓库描述 |
| `--homepage <url>` | 仓库主页 URL |
| `--template <repo>` | 从模板仓库创建 |
| `--license <keyword>` | 指定开源许可证（如 `mit`、`gpl-3.0`） |
| `--add-readme` | 自动添加 README.md 文件 |
| `--gitignore <template>` | 添加 `.gitignore` 模板（如 `Python`、`Node`） |

**示例**：

```bash
# 交互式创建仓库（会引导填写名称、可见性等）
gh repo create

# 创建公开仓库并克隆到本地
gh repo create my-new-project --public --clone

# 创建私有仓库并添加 README
gh repo create my-private-repo --private --add-readme

# 从模板创建仓库
gh repo create my-service --template owner/template-repo --public

# 指定许可证和 .gitignore
gh repo create my-python-app --public --license mit --gitignore Python
```

### 1.3 gh repo fork

复刻（Fork）一个已有仓库到自己的账户下，并可选择克隆到本地。

**基本语法**：

```bash
gh repo fork [<repository>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--clone` | Fork 后立即克隆到本地 |
| `--remote` | 添加远程仓库时使用的名称（默认 `origin`） |
| `--remote-name <string>` | 自定义远程仓库名称 |
| `--org <string>` | Fork 到指定组织而非个人账户 |
| `--default-branch-only` | 仅克隆默认分支 |

**示例**：

```bash
# Fork 当前目录所在仓库
gh repo fork

# Fork 指定仓库并克隆到本地
gh repo fork cli/cli --clone

# Fork 到指定组织
gh repo fork cli/cli --org my-org

# Fork 并仅克隆默认分支
gh repo fork cli/cli --clone --default-branch-only
```

> **提示**：Fork 完成后，`gh` 会自动将上游仓库添加为 `upstream` 远程仓库，方便后续同步。

### 1.4 gh repo view

在浏览器中打开仓库页面，或在终端中查看仓库的详细信息。

**基本语法**：

```bash
gh repo view [<repository>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--web` 或 `-w` | 在浏览器中打开仓库页面 |
| `--branch <string>` 或 `-b` | 查看指定分支 |
| `--json <fields>` | 以 JSON 格式输出指定字段 |
| `--jq <expression>` | 对 JSON 输出应用 jq 过滤器 |

**示例**：

```bash
# 在终端中查看当前仓库的简介
gh repo view

# 在浏览器中打开当前仓库
gh repo view --web

# 查看指定仓库
gh repo view cli/cli

# 查看指定分支
gh repo view --branch main

# JSON 输出（提取仓库名称和描述）
gh repo view --json name,description

# 结合 jq 提取星标数
gh repo view --json stargazerCount --jq '.stargazerCount'
```

### 1.5 gh repo list

列出当前用户拥有的仓库，或搜索 GitHub 上的仓库。

**基本语法**：

```bash
gh repo list [<owner>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--limit <int>` 或 `-L` | 最大返回数量（默认 30） |
| `--language <string>` 或 `-l` | 按编程语言筛选 |
| `--topic <string>` | 按话题（Topic）筛选 |
| `--source` | 仅列出非 Fork 仓库 |
| `--fork` | 仅列出 Fork 仓库 |
| `--archived` | 仅列出已归档仓库 |
| `--no-archived` | 排除已归档仓库 |
| `--visibility <string>` | 按可见性筛选（`public`/`private`/`internal`） |
| `--json <fields>` | 以 JSON 格式输出 |
| `--jq <expression>` | 对 JSON 输出应用 jq 过滤器 |

**示例**：

```bash
# 列出自己的仓库（默认最多 30 条）
gh repo list

# 列出指定用户/组织的仓库
gh repo list cli

# 限制返回数量
gh repo list --limit 10

# 按编程语言筛选
gh repo list --language python

# 按话题筛选
gh repo list --topic machine-learning

# 仅列出公开的非 Fork 仓库
gh repo list --source --visibility public

# JSON 输出（提取仓库名、语言、星标数）
gh repo list --limit 5 --json name,language,stargazerCount

# 结合 jq 格式化输出
gh repo list --limit 5 --json name,language,stargazerCount \
  --jq '.[] | "\(.name) | \(.language) | ★ \(.stargazerCount)"'
```

## 2. gh issue：议题管理

`gh issue` 用于管理 GitHub Issues，支持创建、查看、筛选、更新和评论等操作。所有命令默认在 `gh issue` 下运行，也可通过 `-R` 参数指定远程仓库。

### 2.1 gh issue create

创建新议题。

**基本语法**：

```bash
gh issue create [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--title <string>` 或 `-t` | 议题标题 |
| `--body <string>` 或 `-b` | 议题正文（支持 Markdown） |
| `--body-file <file>` 或 `-F` | 从文件读取正文 |
| `--assignee <login>` 或 `-a` | 指定负责人（可用 `@me` 指代自己） |
| `--label <name>` 或 `-l` | 添加标签（可多次指定） |
| `--milestone <name>` 或 `-m` | 关联里程碑 |
| `--project <name>` 或 `-p` | 关联项目看板 |
| `--web` 或 `-w` | 在浏览器中打开创建页面 |

**示例**：

```bash
# 交互式创建（会打开编辑器填写标题和正文）
gh issue create

# 快速创建（标题 + 正文）
gh issue create --title "修复登录页面样式问题" --body "## 问题描述\n登录按钮在移动端显示异常。"

# 指定负责人和标签
gh issue create --title "更新依赖版本" --assignee @me --label "enhancement" --label "dependencies"

# 关联里程碑
gh issue create --title "v2.0 发布前检查" --milestone "v2.0" --label "release"

# 从文件读取正文
gh issue create --title "API 文档更新" --body-file ./docs/api-changes.md

# 在浏览器中创建
gh issue create --web
```

### 2.2 gh issue list

列出仓库中的议题，支持丰富的筛选条件。

**基本语法**：

```bash
gh issue list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--assignee <login>` 或 `-a` | 按负责人筛选（`@me` 表示自己） |
| `--label <name>` 或 `-l` | 按标签筛选（可多次指定） |
| `--state <string>` 或 `-s` | 按状态筛选（`open`/`closed`/`all`，默认 `open`） |
| `--milestone <name>` 或 `-m` | 按里程碑筛选 |
| `--search <query>` 或 `-S` | 按搜索语法筛选（支持 GitHub 搜索语法） |
| `--limit <int>` 或 `-L` | 最大返回数量（默认 30） |
| `--author <login>` 或 `-A` | 按作者筛选 |
| `--json <fields>` | 以 JSON 格式输出 |
| `--jq <expression>` | 对 JSON 输出应用 jq 过滤器 |
| `--web` 或 `-w` | 在浏览器中打开议题列表 |

**示例**：

```bash
# 列出所有开放议题
gh issue list

# 列出所有议题（含已关闭）
gh issue list --state all

# 按标签筛选
gh issue list --label bug

# 多重标签筛选（AND 逻辑：同时拥有两个标签）
gh issue list --label "bug" --label "high-priority"

# 按负责人筛选
gh issue list --assignee @me

# 按里程碑筛选
gh issue list --milestone "v2.0"

# 组合筛选：自己负责的 bug 议题
gh issue list --label bug --assignee @me --state open

# 限制数量
gh issue list --limit 10

# 搜索（按关键词搜索标题和正文）
gh issue list --search "性能优化"

# 按作者筛选
gh issue list --author username

# 高级搜索（GitHub 搜索语法）
gh issue list --search "performance in:title created:>2026-01-01"

# JSON 输出
gh issue list --limit 5 --json number,title,state,labels

# 结合 jq 格式化
gh issue list --limit 5 --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title)"'
```

#### 2.2.1 筛选实战

以下是一些常见筛选场景的完整命令：

```bash
# 场景1：查看所有需要我处理的议题
gh issue list --assignee @me --state open

# 场景2：查找本周创建的 bug 报告
gh issue list --label bug --search "created:>=2026-07-20"

# 场景3：查看 v2.0 里程碑中所有未关闭的议题
gh issue list --milestone "v2.0" --state open

# 场景4：查找标题中包含"API"且无负责人的议题
gh issue list --search "API in:title no:assignee"

# 场景5：以 JSON 格式导出所有议题数据
gh issue list --limit 100 --state all --json number,title,state,assignees,labels,createdAt > issues.json
```

### 2.3 gh issue view

查看议题的详细信息，包括标题、正文、状态、标签、评论等。

**基本语法**：

```bash
gh issue view {<number> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--comments` 或 `-c` | 同时显示评论 |
| `--web` 或 `-w` | 在浏览器中打开议题页面 |
| `--json <fields>` | 以 JSON 格式输出 |
| `--jq <expression>` | 对 JSON 输出应用 jq 过滤器 |

**示例**：

```bash
# 查看第 42 号议题
gh issue view 42

# 查看议题并显示评论
gh issue view 42 --comments

# 通过 URL 查看
gh issue view https://github.com/cli/cli/issues/1234

# 在浏览器中打开
gh issue view 42 --web

# JSON 输出
gh issue view 42 --json number,title,state,body,assignees,labels
```

### 2.4 gh issue status

查看当前仓库中与自己相关的议题状态摘要，包括自己创建的、被分配的、被提及的议题。

**基本语法**：

```bash
gh issue status [flags]
```

**示例**：

```bash
# 查看与自己相关的议题摘要
gh issue status

# 结合 jq 获取结构化数据
gh issue status --json assigned,mentioned,created
```

> **提示**：`gh issue status` 是快速了解"有什么需要我关注"的最便捷方式，输出按 `assigned`（分配给我的）、`mentioned`（提到我的）、`created`（我创建的）分组展示。

### 2.5 gh issue close

关闭一个议题。

**基本语法**：

```bash
gh issue close {<number> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--reason <string>` 或 `-r` | 关闭原因（`completed`/`not planned`） |
| `--comment <string>` 或 `-c` | 关闭时添加评论 |

**示例**：

```bash
# 关闭第 42 号议题
gh issue close 42

# 关闭并注明原因
gh issue close 42 --reason completed

# 关闭并添加评论
gh issue close 42 --comment "已在 PR #56 中修复，关闭此议题。"
```

### 2.6 gh issue reopen

重新打开一个已关闭的议题。

**基本语法**：

```bash
gh issue reopen {<number> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--comment <string>` 或 `-c` | 重新打开时添加评论 |

**示例**：

```bash
# 重新打开第 42 号议题
gh issue reopen 42

# 重新打开并添加评论说明原因
gh issue reopen 42 --comment "问题在 v2.1 中复现，需要重新调查。"
```

### 2.7 gh issue comment

为议题添加评论。

**基本语法**：

```bash
gh issue comment {<number> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--body <string>` 或 `-b` | 评论正文 |
| `--body-file <file>` 或 `-F` | 从文件读取评论内容 |
| `--editor` 或 `-e` | 在编辑器中编写评论 |
| `--web` 或 `-w` | 在浏览器中打开评论页面 |

**示例**：

```bash
# 添加评论
gh issue comment 42 --body "我已经开始调查这个问题，预计明天提交修复 PR。"

# 从文件读取评论内容
gh issue comment 42 --body-file ./comment.md

# 在编辑器中编写评论
gh issue comment 42 --editor

# 在浏览器中添加评论
gh issue comment 42 --web
```

### 2.8 gh issue edit

编辑议题的标题、正文、标签、负责人、里程碑等属性。

**基本语法**：

```bash
gh issue edit {<number> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--title <string>` 或 `-t` | 修改标题 |
| `--body <string>` 或 `-b` | 修改正文 |
| `--body-file <file>` 或 `-F` | 从文件读取新正文 |
| `--add-assignee <login>` | 添加负责人 |
| `--remove-assignee <login>` | 移除负责人 |
| `--add-label <name>` | 添加标签 |
| `--remove-label <name>` | 移除标签 |
| `--milestone <name>` 或 `-m` | 设置里程碑 |
| `--add-project <name>` | 添加到项目看板 |
| `--remove-project <name>` | 从项目看板移除 |

**示例**：

```bash
# 修改标题
gh issue edit 42 --title "修复登录页面在 Safari 上的样式问题"

# 添加标签
gh issue edit 42 --add-label "bug" --add-label "frontend"

# 移除标签
gh issue edit 42 --remove-label "enhancement"

# 分配负责人
gh issue edit 42 --add-assignee @me

# 移除负责人
gh issue edit 42 --remove-assignee old-user

# 设置里程碑
gh issue edit 42 --milestone "v2.0"

# 同时修改多个属性
gh issue edit 42 --title "新标题" --add-label "high-priority" --add-assignee @me --milestone "v2.0"
```

## 3. gh gist：代码片段管理

`gh gist` 用于管理 GitHub Gist（代码片段），支持创建、查看、编辑和删除公开或私密的 Gist。

### 3.1 gh gist create

创建新的 Gist。

**基本语法**：

```bash
gh gist create [<filename>... | -] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--desc <string>` 或 `-d` | Gist 描述 |
| `--filename <string>` 或 `-f` | 指定文件名（可多次指定，用于多文件 Gist） |
| `--public` 或 `-p` | 创建公开 Gist |
| `--secret` | 创建私密 Gist（默认行为） |
| `--web` 或 `-w` | 创建后在浏览器中打开 |

**示例**：

```bash
# 从文件创建私密 Gist
gh gist create my-script.sh

# 创建公开 Gist 并添加描述
gh gist create my-script.sh --public --desc "一个实用的 Shell 脚本"

# 从管道创建 Gist（- 表示从 stdin 读取）
echo "Hello, World!" | gh gist create -

# 创建多文件 Gist
gh gist create config.yml notes.md --desc "项目配置和笔记"

# 指定文件名（适用于管道输入）
echo "print('Hello')" | gh gist create -f hello.py --desc "Python Hello World"

# 创建后在浏览器中打开
gh gist create my-script.sh --public --web
```

### 3.2 gh gist list

列出自己的 Gist。

**基本语法**：

```bash
gh gist list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--limit <int>` 或 `-L` | 最大返回数量（默认 10） |
| `--public` | 仅列出公开 Gist |
| `--secret` | 仅列出私密 Gist |

**示例**：

```bash
# 列出所有 Gist
gh gist list

# 限制数量
gh gist list --limit 20

# 仅列出公开 Gist
gh gist list --public

# 仅列出私密 Gist
gh gist list --secret
```

### 3.3 gh gist view

查看 Gist 的详细内容。

**基本语法**：

```bash
gh gist view {<gist-id> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--filename <string>` 或 `-f` | 仅显示指定文件的内容 |
| `--raw` 或 `-r` | 以原始格式输出（无语法高亮） |
| `--web` 或 `-w` | 在浏览器中打开 |

**示例**：

```bash
# 查看 Gist 内容
gh gist view abc123def456

# 通过 URL 查看
gh gist view https://gist.github.com/username/abc123def456

# 仅查看指定文件
gh gist view abc123def456 --filename notes.md

# 以原始格式输出
gh gist view abc123def456 --raw

# 在浏览器中打开
gh gist view abc123def456 --web
```

### 3.4 gh gist edit

编辑已有的 Gist。与 `create` 类似，但会覆盖现有 Gist 的内容。

**基本语法**：

```bash
gh gist edit {<gist-id> | <url>} [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--desc <string>` 或 `-d` | 修改描述 |
| `--filename <string>` 或 `-f` | 指定文件名（用于更新或添加文件） |
| `--add <filename>` 或 `-a` | 添加新文件到 Gist |

**示例**：

```bash
# 编辑 Gist 内容（更新已有文件）
gh gist edit abc123def456 updated-script.sh

# 修改描述
gh gist edit abc123def456 --desc "更新后的脚本（v2.0）"

# 添加新文件到现有 Gist
gh gist edit abc123def456 --add new-file.md

# 在浏览器中编辑
gh gist edit abc123def456 --web
```

### 3.5 gh gist delete

删除 Gist。

**基本语法**：

```bash
gh gist delete {<gist-id> | <url>}
```

**示例**：

```bash
# 删除 Gist（会弹出确认提示）
gh gist delete abc123def456

# 通过 URL 删除
gh gist delete https://gist.github.com/username/abc123def456
```

> **警告**：删除操作不可撤销。删除后，通过该 Gist 链接访问的所有用户都将无法查看内容。

## 4. gh browse：浏览器集成

`gh browse` 在浏览器中打开与当前仓库相关的 GitHub 页面。这是一个便捷命令，无需手动在浏览器中输入 URL。

**基本语法**：

```bash
gh browse [<number> | <path> | <commit-sha>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--branch <string>` 或 `-b` | 打开指定分支的页面 |
| `--commit` 或 `-c` | 打开最后一次提交的页面 |
| `--projects` 或 `-p` | 打开仓库的项目看板页面 |
| `--settings` 或 `-s` | 打开仓库的设置页面 |
| `--wiki` 或 `-w` | 打开仓库的 Wiki 页面 |
| `--no-browser` 或 `-n` | 仅打印 URL 而不在浏览器中打开 |

**示例**：

```bash
# 在当前目录的仓库根页面打开
gh browse

# 打开仓库的 Issues 页面
gh browse -- issues

# 打开指定分支
gh browse --branch develop

# 打开最后一次提交
gh browse --commit

# 打开指定文件
gh browse README.md

# 打开指定行范围
gh browse README.md:10-20

# 打开指定议题
gh browse 42

# 打开仓库设置页面
gh browse --settings

# 打开 Wiki 页面
gh browse --wiki

# 仅打印 URL 不打开浏览器
gh browse --no-browser

# 打开指定分支的特定文件
gh browse --branch main src/app.js
```

> **提示**：`gh browse` 的打开目标取决于当前工作目录和参数。如果当前在仓库目录中且未提供参数，默认打开仓库主页；如果提供了数字，则打开对应编号的 Issue/PR；如果提供了文件路径，则打开对应文件。

## 5. 小结

本章覆盖了 GitHub CLI 最常用的四个命令模块：

| 命令 | 核心操作 | 典型场景 |
|------|----------|----------|
| `gh repo` | clone / create / fork / view / list | 仓库生命周期管理 |
| `gh issue` | create / list / view / status / close / reopen / comment / edit | 议题跟踪与协作 |
| `gh gist` | create / list / view / edit / delete | 代码片段分享 |
| `gh browse` | 在浏览器中打开 | 快速跳转到 GitHub 页面 |

> **下一步**：继续阅读 [PR 工作流](03-pr-workflow.md) 了解如何使用 `gh pr` 命令管理完整的 Pull Request 工作流。