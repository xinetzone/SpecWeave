---
id: github-cli-wiki-07-cheatsheet
title: "命令速查表与最佳实践"
source: "https://cli.github.com/manual/"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "cheatsheet", "best-practices", "quick-reference", "automation", "specweave", "workflow"]
---

# 命令速查表与最佳实践

本章是 GitHub CLI 的完整命令速查表，按功能分类组织，并集成了 SpecWeave 工作流的最佳实践和常用自动化模式。

> **使用方式**：按 `Ctrl+F` 搜索命令名或场景关键词，快速定位所需命令。本节也是前几章所有命令的浓缩索引，适合日常开发中随时查阅。

---

## 1. 命令速查表

### 1.1 Auth & Config（认证与配置）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh auth login` | 交互式登录 | `gh auth login` — 浏览器 OAuth 认证 |
| `gh auth login --with-token` | 非交互式登录（CI/CD） | `echo "$GH_TOKEN" \| gh auth login --with-token` |
| `gh auth login -p ssh` | 使用 SSH 协议登录 | `gh auth login -p ssh` |
| `gh auth login --hostname <host>` | 登录到 GHES | `gh auth login --hostname github.example.com` |
| `gh auth logout` | 登出 | `gh auth logout` — 交互式选择要登出的账号 |
| `gh auth status` | 查看认证状态 | `gh auth status` — 显示所有主机的登录状态 |
| `gh auth status --hostname <host>` | 查看指定主机认证状态 | `gh auth status --hostname github.com` |
| `gh auth token` | 查看当前 Token | `gh auth token` — 输出 Token 值 |
| `gh auth refresh` | 刷新认证凭证 | `gh auth refresh -s repo,workflow` — 刷新并扩展权限范围 |
| `gh config list` | 列出所有配置 | `gh config list` — 显示当前全部配置项 |
| `gh config set <key> <value>` | 设置配置项 | `gh config set git_protocol ssh` |
| `gh config get <key>` | 获取配置项 | `gh config get editor` |

### 1.2 Repo（仓库管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh repo clone <repo>` | 克隆仓库 | `gh repo clone cli/cli` |
| `gh repo clone <repo> -- --depth=1` | 浅克隆 | `gh repo clone cli/cli -- --depth=1` |
| `gh repo create` | 交互式创建仓库 | `gh repo create` — 向导式创建 |
| `gh repo create <name> --public --clone` | 创建公开仓库并克隆 | `gh repo create my-project --public --clone` |
| `gh repo create <name> --private --add-readme` | 创建私有仓库 | `gh repo create my-private --private --add-readme` |
| `gh repo create <name> --template <repo>` | 从模板创建 | `gh repo create my-service --template owner/template-repo` |
| `gh repo fork` | Fork 当前仓库 | `gh repo fork` |
| `gh repo fork <repo> --clone` | Fork 并克隆 | `gh repo fork cli/cli --clone` |
| `gh repo fork <repo> --org <org>` | Fork 到组织 | `gh repo fork cli/cli --org my-org` |
| `gh repo view` | 终端查看仓库信息 | `gh repo view` |
| `gh repo view --web` | 浏览器打开仓库 | `gh repo view --web` |
| `gh repo view --json name,description` | JSON 格式输出 | `gh repo view --json name,stargazerCount` |
| `gh repo list` | 列出自己的仓库 | `gh repo list --limit 20` |
| `gh repo list <owner>` | 列出指定用户的仓库 | `gh repo list cli` |
| `gh repo list --language <lang>` | 按语言筛选 | `gh repo list --language python` |
| `gh repo list --topic <topic>` | 按话题筛选 | `gh repo list --topic machine-learning` |
| `gh repo list --source` | 仅非 Fork 仓库 | `gh repo list --source --visibility public` |
| `gh repo sync` | 同步 Fork 仓库 | `gh repo sync` — 拉取上游更新 |
| `gh repo sync <repo>` | 同步指定仓库 | `gh repo sync owner/repo --source upstream` |
| `gh repo rename <new-name>` | 重命名仓库 | `gh repo rename new-name` |
| `gh repo delete <repo>` | 删除仓库 | `gh repo delete owner/repo --yes` |
| `gh repo archive <repo>` | 归档仓库 | `gh repo archive owner/repo` |

### 1.3 Issue（议题管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh issue create` | 交互式创建议题 | `gh issue create` — 打开编辑器 |
| `gh issue create -t "<title>" -b "<body>"` | 快速创建议题 | `gh issue create -t "修复登录 Bug" -b "## 描述\n..."` |
| `gh issue create -a @me -l bug` | 指定负责人和标签 | `gh issue create -t "Bug" -a @me -l "bug,high-priority"` |
| `gh issue create -m "<milestone>"` | 关联里程碑 | `gh issue create -t "任务" -m "v2.0"` |
| `gh issue create --web` | 浏览器创建 | `gh issue create --web` |
| `gh issue create -F <file>` | 从文件读取正文 | `gh issue create -t "更新" -F ./docs/changes.md` |
| `gh issue list` | 列出开放议题 | `gh issue list` |
| `gh issue list -s all` | 列出所有议题 | `gh issue list --state all` |
| `gh issue list -l bug` | 按标签筛选 | `gh issue list --label bug` |
| `gh issue list -a @me` | 按负责人筛选 | `gh issue list --assignee @me` |
| `gh issue list -m "<milestone>"` | 按里程碑筛选 | `gh issue list --milestone "v2.0"` |
| `gh issue list -S "<query>"` | 全文搜索 | `gh issue list --search "性能优化 in:title"` |
| `gh issue list -L 50` | 限制返回数量 | `gh issue list --limit 50` |
| `gh issue list --json number,title,state` | JSON 输出 | `gh issue list --json number,title,state,labels` |
| `gh issue view <number>` | 查看议题详情 | `gh issue view 42` |
| `gh issue view <number> -c` | 查看含评论 | `gh issue view 42 --comments` |
| `gh issue view <number> -w` | 浏览器查看 | `gh issue view 42 --web` |
| `gh issue status` | 查看与自己相关的议题 | `gh issue status` — 按 assigned/mentioned/created 分组 |
| `gh issue close <number>` | 关闭议题 | `gh issue close 42` |
| `gh issue close <number> -r completed` | 关闭并注明原因 | `gh issue close 42 --reason completed` |
| `gh issue close <number> -c "<msg>"` | 关闭并评论 | `gh issue close 42 --comment "已在 PR #56 修复"` |
| `gh issue reopen <number>` | 重新打开议题 | `gh issue reopen 42` |
| `gh issue reopen <number> -c "<msg>"` | 重新打开并评论 | `gh issue reopen 42 --comment "问题复现，重新调查"` |
| `gh issue comment <number> -b "<msg>"` | 添加评论 | `gh issue comment 42 -b "正在调查此问题"` |
| `gh issue comment <number> -F <file>` | 从文件评论 | `gh issue comment 42 -F ./comment.md` |
| `gh issue edit <number> -t "<title>"` | 修改标题 | `gh issue edit 42 -t "新标题"` |
| `gh issue edit <number> --add-label <label>` | 添加标签 | `gh issue edit 42 --add-label "frontend"` |
| `gh issue edit <number> --remove-label <label>` | 移除标签 | `gh issue edit 42 --remove-label "backend"` |
| `gh issue edit <number> --add-assignee @me` | 添加负责人 | `gh issue edit 42 --add-assignee @me` |
| `gh issue edit <number> -m "<milestone>"` | 设置里程碑 | `gh issue edit 42 --milestone "v2.0"` |
| `gh issue lock <number>` | 锁定议题 | `gh issue lock 42` |
| `gh issue unlock <number>` | 解锁议题 | `gh issue unlock 42` |
| `gh issue transfer <number> <repo>` | 转移议题 | `gh issue transfer 42 owner/other-repo` |

### 1.4 PR（Pull Request 工作流）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh pr create` | 交互式创建 PR | `gh pr create` — 打开编辑器填写 |
| `gh pr create -t "<title>" -b "<body>"` | 快速创建 PR | `gh pr create -t "feat: 新功能" -b "## 变更说明\n..."` |
| `gh pr create --fill` | 自动填充（宽松模式） | `gh pr create --fill` — 使用首个提交信息 |
| `gh pr create --fill-verbose` | 自动填充（详细模式） | `gh pr create --fill-verbose` — 使用所有提交信息 |
| `gh pr create --draft` | 创建草稿 PR | `gh pr create -t "WIP: 重构" --draft` |
| `gh pr create --web` | 浏览器创建 | `gh pr create --web` |
| `gh pr create -B <base> -H <head>` | 指定源/目标分支 | `gh pr create -B main -H feature/my-branch` |
| `gh pr create -r <reviewer> -a <assignee>` | 指定审查者和负责人 | `gh pr create -r "alice,bob" -a "charlie"` |
| `gh pr create -l <label> -m <milestone>` | 指定标签和里程碑 | `gh pr create -l "feature,frontend" -m "v2.0"` |
| `gh pr create -F <file>` | 从文件读取描述 | `gh pr create -t "feat: 新功能" -F ./pr-body.md` |
| `gh pr create --recover` | 恢复中断的 PR 创建 | `gh pr create --recover` |
| `gh pr list` | 列出 PR | `gh pr list` |
| `gh pr list -s all` | 列出所有状态 | `gh pr list --state all` |
| `gh pr list -s merged` | 列出已合并 PR | `gh pr list --state merged` |
| `gh pr list -l bug` | 按标签筛选 | `gh pr list --label bug` |
| `gh pr list -a @me` | 按负责人筛选 | `gh pr list --assignee "@me"` |
| `gh pr list -A @me` | 按作者筛选 | `gh pr list --author "@me"` |
| `gh pr list -B main` | 按目标分支筛选 | `gh pr list --base main` |
| `gh pr list -S "<query>"` | 全文搜索 | `gh pr list --search "is:open label:bug"` |
| `gh pr list -L 10` | 限制数量 | `gh pr list --limit 10` |
| `gh pr list --json title,number,state` | JSON 输出 | `gh pr list --json title,number,state,author,createdAt` |
| `gh pr view <number>` | 查看 PR 详情 | `gh pr view 42` |
| `gh pr view <number> -c` | 查看含评论 | `gh pr view 42 --comments` |
| `gh pr view <number> -w` | 浏览器查看 | `gh pr view 42 --web` |
| `gh pr view <number> --json title,state,mergeable` | JSON 输出 | `gh pr view 42 --json title,state,mergeable,reviews` |
| `gh pr status` | 查看 PR 概览 | `gh pr status` — 当前分支/我创建的/待审查 |
| `gh pr checkout <number>` | 检出 PR 到本地 | `gh pr checkout 42` |
| `gh pr checkout <number> --repo <repo>` | 跨仓库检出 | `gh pr checkout 42 --repo owner/repo` |
| `gh pr checks <number>` | 查看 CI 检查 | `gh pr checks 42` |
| `gh pr checks <number> --watch` | 实时监控 CI | `gh pr checks 42 --watch` |
| `gh pr diff <number>` | 查看变更差异 | `gh pr diff 42` |
| `gh pr diff <number> --name-only` | 仅列文件名 | `gh pr diff 42 --name-only` |
| `gh pr diff <number> --color always` | 彩色输出 | `gh pr diff 42 --color always` |
| `gh pr merge <number>` | 合并 PR（默认策略） | `gh pr merge 42` |
| `gh pr merge <number> --squash` | 压缩合并 | `gh pr merge 42 --squash` |
| `gh pr merge <number> --rebase` | 变基合并 | `gh pr merge 42 --rebase` |
| `gh pr merge <number> --auto --squash` | 自动合并（CI 通过后） | `gh pr merge 42 --auto --squash` |
| `gh pr merge <number> --delete-branch` | 合并后删除分支 | `gh pr merge 42 --squash --delete-branch` |
| `gh pr review <number> --approve` | 批准 PR | `gh pr review 42 --approve` |
| `gh pr review <number> --approve -b "<msg>"` | 批准并评论 | `gh pr review 42 --approve -b "LGTM!"` |
| `gh pr review <number> --comment -b "<msg>"` | 仅评论 | `gh pr review 42 --comment -b "建议优化此处"` |
| `gh pr review <number> --request-changes -b "<msg>"` | 请求修改 | `gh pr review 42 --request-changes -b "需要修改:\n1. ..."` |
| `gh pr close <number>` | 关闭 PR | `gh pr close 42` |
| `gh pr close <number> -c "<msg>"` | 关闭并评论 | `gh pr close 42 -c "被 #56 替代"` |
| `gh pr reopen <number>` | 重新打开 PR | `gh pr reopen 42` |
| `gh pr reopen <number> -c "<msg>"` | 重新打开并评论 | `gh pr reopen 42 -c "已修复 CI 问题"` |
| `gh pr ready <number>` | 草稿→就绪 | `gh pr ready 42` |
| `gh pr comment <number> -b "<msg>"` | 添加评论 | `gh pr comment 42 -b "补充说明..."` |
| `gh pr comment <number> -F <file>` | 从文件评论 | `gh pr comment 42 -F ./review-notes.md` |

### 1.5 Actions（CI/CD 管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh workflow list` | 列出工作流 | `gh workflow list` |
| `gh workflow list -a` | 列出所有（含禁用） | `gh workflow list --all` |
| `gh workflow list -L 20` | 限制数量 | `gh workflow list --limit 20` |
| `gh workflow view <workflow>` | 查看工作流 | `gh workflow view "CI"` — 按名称查看 |
| `gh workflow view <id>` | 按 ID 查看 | `gh workflow view 123456` |
| `gh workflow view <workflow> --web` | 浏览器查看 | `gh workflow view "CI" --web` |
| `gh workflow enable <workflow>` | 启用工作流 | `gh workflow enable "CI"` |
| `gh workflow disable <workflow>` | 禁用工作流 | `gh workflow disable "CI"` |
| `gh workflow run <workflow>` | 手动触发工作流 | `gh workflow run "CI"` |
| `gh workflow run <workflow> -f <key>=<value>` | 带参数触发 | `gh workflow run "Deploy" -f env=staging` |
| `gh workflow run <workflow> --ref <branch>` | 指定分支触发 | `gh workflow run "CI" --ref feature/test` |
| `gh run list` | 列出运行记录 | `gh run list` |
| `gh run list -w <workflow>` | 按工作流筛选 | `gh run list --workflow "CI"` |
| `gh run list -b <branch>` | 按分支筛选 | `gh run list --branch main` |
| `gh run list -s failure` | 仅失败运行 | `gh run list --status failure` |
| `gh run list -L 10` | 限制数量 | `gh run list --limit 10` |
| `gh run view <run-id>` | 查看运行详情 | `gh run view 1234567890` |
| `gh run view <run-id> --log` | 查看运行日志 | `gh run view 1234567890 --log` |
| `gh run view <run-id> --log-failed` | 仅查看失败日志 | `gh run view 1234567890 --log-failed` |
| `gh run view <run-id> --job <job-id>` | 查看指定 Job 日志 | `gh run view 1234567890 --job 987654321` |
| `gh run view <run-id> --web` | 浏览器查看 | `gh run view 1234567890 --web` |
| `gh run watch <run-id>` | 实时监控运行 | `gh run watch 1234567890` |
| `gh run rerun <run-id>` | 重新运行 | `gh run rerun 1234567890` |
| `gh run rerun <run-id> --failed` | 仅重跑失败 Job | `gh run rerun 1234567890 --failed` |
| `gh run download <run-id>` | 下载产物 | `gh run download 1234567890` |
| `gh run download <run-id> -n <name>` | 按名称下载产物 | `gh run download 1234567890 -n "build-output"` |
| `gh run download <run-id> -d <dir>` | 指定下载目录 | `gh run download 1234567890 -d ./artifacts` |
| `gh run cancel <run-id>` | 取消运行 | `gh run cancel 1234567890` |
| `gh run delete <run-id>` | 删除运行记录 | `gh run delete 1234567890` |

### 1.6 Release（发布管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh release create <tag>` | 创建 Release | `gh release create v1.0.0` |
| `gh release create <tag> --title "<title>" -n "<notes>"` | 指定标题和说明 | `gh release create v1.0.0 -t "v1.0.0 正式版" -n "## 更新内容\n..."` |
| `gh release create <tag> --generate-notes` | 自动生成 Release Notes | `gh release create v1.0.0 --generate-notes` |
| `gh release create <tag> --draft` | 创建为草稿 | `gh release create v1.0.0 --draft` |
| `gh release create <tag> --prerelease` | 标记为预发布 | `gh release create v1.0.0-beta --prerelease` |
| `gh release create <tag> --target <branch>` | 指定目标分支 | `gh release create v1.0.0 --target main` |
| `gh release create <tag> <file>...` | 上传资产文件 | `gh release create v1.0.0 ./dist/app.tar.gz ./dist/checksums.txt` |
| `gh release list` | 列出 Release | `gh release list` |
| `gh release list -L 10` | 限制数量 | `gh release list --limit 10` |
| `gh release list --exclude-drafts` | 排除草稿 | `gh release list --exclude-drafts` |
| `gh release list --exclude-pre-releases` | 排除预发布 | `gh release list --exclude-pre-releases` |
| `gh release view <tag>` | 查看 Release | `gh release view v1.0.0` |
| `gh release view <tag> --web` | 浏览器查看 | `gh release view v1.0.0 --web` |
| `gh release view <tag> --json name,tagName,body` | JSON 输出 | `gh release view v1.0.0 --json name,tagName,publishedAt` |
| `gh release download <tag>` | 下载 Release 资产 | `gh release download v1.0.0` |
| `gh release download <tag> -p "<pattern>"` | 按模式下载 | `gh release download v1.0.0 -p "*.tar.gz"` |
| `gh release download <tag> -d <dir>` | 指定下载目录 | `gh release download v1.0.0 -d ./releases` |
| `gh release upload <tag> <file>...` | 上传资产 | `gh release upload v1.0.0 ./dist/binary.tar.gz` |
| `gh release delete <tag>` | 删除 Release | `gh release delete v1.0.0 --yes` |
| `gh release edit <tag>` | 编辑 Release | `gh release edit v1.0.0 --draft=false` |

### 1.7 Gist（代码片段管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh gist create <file>` | 创建 Gist | `gh gist create my-script.sh` |
| `gh gist create <file> -d "<desc>"` | 创建含描述 | `gh gist create my-script.sh -d "实用脚本"` |
| `gh gist create <file> --public` | 创建公开 Gist | `gh gist create my-script.sh --public` |
| `gh gist create -` | 从管道创建 | `echo "Hello" \| gh gist create -` |
| `gh gist create -f <name>` | 指定文件名 | `echo "print('hi')" \| gh gist create -f hello.py` |
| `gh gist create <file1> <file2>` | 多文件 Gist | `gh gist create config.yml notes.md` |
| `gh gist list` | 列出 Gist | `gh gist list` |
| `gh gist list -L 20` | 限制数量 | `gh gist list --limit 20` |
| `gh gist list --public` | 仅公开 Gist | `gh gist list --public` |
| `gh gist list --secret` | 仅私密 Gist | `gh gist list --secret` |
| `gh gist view <id>` | 查看 Gist | `gh gist view abc123def456` |
| `gh gist view <id> -f <name>` | 查看指定文件 | `gh gist view abc123def456 -f notes.md` |
| `gh gist view <id> -r` | 原始格式输出 | `gh gist view abc123def456 --raw` |
| `gh gist view <id> -w` | 浏览器查看 | `gh gist view abc123def456 --web` |
| `gh gist edit <id>` | 编辑 Gist | `gh gist edit abc123def456 updated-script.sh` |
| `gh gist edit <id> -d "<desc>"` | 修改描述 | `gh gist edit abc123def456 -d "v2.0 更新"` |
| `gh gist edit <id> -a <file>` | 添加文件 | `gh gist edit abc123def456 -a new-file.md` |
| `gh gist delete <id>` | 删除 Gist | `gh gist delete abc123def456` |

### 1.8 API & Search（API 调用与搜索）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh api <endpoint>` | REST API 调用 | `gh api /user` — 获取当前用户信息 |
| `gh api <endpoint> --method POST` | 指定 HTTP 方法 | `gh api /repos/owner/repo/issues -F title="New Issue"` |
| `gh api <endpoint> -F <key>=<value>` | 发送表单字段 | `gh api /repos/owner/repo/issues -F title="Bug" -F body="..."` |
| `gh api <endpoint> -f <key>=<value>` | 发送原始字段 | `gh api /repos/owner/repo/issues -f title="Bug"` |
| `gh api <endpoint> -H "<header>"` | 自定义 Header | `gh api /user -H "Accept: application/vnd.github.v3+json"` |
| `gh api <endpoint> --paginate` | 自动翻页 | `gh api /orgs/cli/repos --paginate` |
| `gh api <endpoint> --jq "<expr>"` | jq 过滤 | `gh api /user --jq '.login'` |
| `gh api graphql -f query='<query>'` | GraphQL 查询 | `gh api graphql -f query='{ viewer { login } }'` |
| `gh api graphql -F <key>=<value>` | GraphQL 变量 | `gh api graphql -F owner="cli" -f query='query($owner:String!){...}'` |
| `gh search repos <query>` | 搜索仓库 | `gh search repos "machine learning language:python"` |
| `gh search repos <query> -L 50` | 限制结果数 | `gh search repos "topic:react" --limit 50` |
| `gh search repos <query> --sort stars` | 按星标排序 | `gh search repos "language:go" --sort stars --order desc` |
| `gh search issues <query>` | 搜索 Issue | `gh search issues "bug label:help-wanted"` |
| `gh search prs <query>` | 搜索 PR | `gh search prs "is:open review-requested:@me"` |
| `gh search code <query>` | 搜索代码 | `gh search code "function authenticate" --language python` |
| `gh search commits <query>` | 搜索提交 | `gh search commits "fix: login" --author @me` |

### 1.9 Extensions（扩展管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh extension install <repo>` | 安装扩展 | `gh extension install cli/gh-dash` |
| `gh extension list` | 列出已安装扩展 | `gh extension list` |
| `gh extension search <query>` | 搜索扩展 | `gh extension search dash` |
| `gh extension remove <name>` | 移除扩展 | `gh extension remove gh-dash` |
| `gh extension upgrade <name>` | 升级扩展 | `gh extension upgrade gh-dash` |
| `gh extension upgrade --all` | 升级全部扩展 | `gh extension upgrade --all` |
| `gh extension browse` | 浏览器浏览扩展 | `gh extension browse` |
| `gh extension create <name>` | 创建新扩展 | `gh extension create my-gh-extension` |

### 1.10 Secret & Variable（密钥与变量管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh secret list` | 列出仓库 Secrets | `gh secret list` |
| `gh secret list -e <env>` | 列出环境 Secrets | `gh secret list --env production` |
| `gh secret list -o <org>` | 列出组织 Secrets | `gh secret list --org my-org` |
| `gh secret set <name>` | 设置 Secret | `gh secret set DEPLOY_KEY < ./key.pem` |
| `gh secret set <name> -b "<value>"` | 直接设置值 | `gh secret set API_KEY -b "sk-xxxxxxxx"` |
| `gh secret set <name> -e <env>` | 设置环境 Secret | `gh secret set DB_PASSWORD -e production -b "secret"` |
| `gh secret set <name> -o <org>` | 设置组织 Secret | `gh secret set NPM_TOKEN -o my-org -b "token"` |
| `gh secret remove <name>` | 删除 Secret | `gh secret remove DEPLOY_KEY` |
| `gh variable list` | 列出变量 | `gh variable list` |
| `gh variable set <name> -b "<value>"` | 设置变量 | `gh variable set ENVIRONMENT -b "staging"` |
| `gh variable remove <name>` | 删除变量 | `gh variable remove ENVIRONMENT` |

### 1.11 Alias（别名管理）

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh alias set <name> "<command>"` | 创建别名 | `gh alias set co "pr checkout"` |
| `gh alias set <name> --shell` | 创建 Shell 别名 | `gh alias set ci-check --shell 'gh pr checks $(gh pr view --json number --jq .number) --watch'` |
| `gh alias list` | 列出别名 | `gh alias list` |
| `gh alias delete <name>` | 删除别名 | `gh alias delete co` |

### 1.12 其他命令

| 命令 | 用途 | 常用示例 |
|------|------|----------|
| `gh browse` | 浏览器打开仓库主页 | `gh browse` |
| `gh browse 42` | 打开指定 Issue/PR | `gh browse 42` |
| `gh browse <file>` | 打开指定文件 | `gh browse README.md` |
| `gh browse <file>:<L>-<L>` | 打开指定行范围 | `gh browse src/app.ts:42-56` |
| `gh browse -b <branch>` | 打开指定分支 | `gh browse --branch develop` |
| `gh browse -c` | 打开最后一次提交 | `gh browse --commit` |
| `gh browse -s` | 打开仓库设置 | `gh browse --settings` |
| `gh browse -w` | 打开 Wiki | `gh browse --wiki` |
| `gh browse -n` | 仅打印 URL | `gh browse --no-browser` |
| `gh label list` | 列出标签 | `gh label list` |
| `gh label create <name>` | 创建标签 | `gh label create "high-priority" --color "FF0000"` |
| `gh label edit <name>` | 编辑标签 | `gh label edit "bug" --color "FF4444"` |
| `gh label delete <name>` | 删除标签 | `gh label delete "deprecated"` |
| `gh codespace list` | 列出 Codespaces | `gh codespace list` |
| `gh codespace create` | 创建 Codespace | `gh codespace create` |
| `gh codespace ssh` | SSH 连接 Codespace | `gh codespace ssh` |
| `gh codespace delete` | 删除 Codespace | `gh codespace delete` |
| `gh copilot suggest "<prompt>"` | Copilot 建议 | `gh copilot suggest "如何优化这段代码"` |
| `gh copilot explain "<command>"` | Copilot 解释 | `gh copilot explain "git rebase -i HEAD~3"` |
| `gh attestation verify <file>` | 验证产物签名 | `gh attestation verify ./dist/binary.tar.gz --repo owner/repo` |
| `gh completion -s <shell>` | 生成补全脚本 | `gh completion -s bash \| sudo tee /etc/bash_completion.d/gh` |

---

## 2. SpecWeave 工作流集成最佳实践

在 SpecWeave 的 AI 辅助开发范式中，`gh` 是 AI 智能体与 GitHub 之间的核心桥梁。以下最佳实践覆盖了 `gh` 在 SpecWeave 工作流中的典型应用场景。

### 2.1 Spec 驱动的开发（Spec → Issue → PR）

SpecWeave 的核心理念是"先规范、后编码"。`gh` 在此过程中的角色是将 Spec 文档映射为 GitHub 上的 Issue 和 PR：

```bash
# 1. 从 Spec 创建 Issue（将 spec.md 中的任务拆解为 Issue）
gh issue create \
  -t "feat: 实现用户认证模块（Spec S-001）" \
  -F ./specs/feature-auth/spec.md \
  -a @me -l "feature,spec" -m "v2.0"

# 2. 开始开发后，基于 Issue 创建关联 PR
git checkout -b feature/auth-module
# ... 编写代码 ...
git add . && git commit -m "feat: 实现 JWT 认证流程

实现 S-001 规范中的认证模块核心功能：
- Token 签发与验证
- 中间件集成
- 单元测试覆盖

Closes #42"
git push -u origin feature/auth-module

# 3. 创建 PR，关联 Issue 和 Spec
gh pr create \
  -t "feat: 实现用户认证模块（Spec S-001）" \
  -F ./specs/feature-auth/pr-body.md \
  -r "tech-lead" -a @me \
  -l "feature,spec" -m "v2.0"
```

### 2.2 原子化提交工作流

SpecWeave 要求每次提交遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范，且单一职责——一个 PR 对应一个 Spec 中的一个清晰变更单元。

```bash
# 原子化提交流程：每个功能点一个 PR
# 1. 先创建 Issue 作为任务追踪
gh issue create -t "feat: 添加报表导出功能" -a @me -l "feature,atomized"

# 2. 从 Issue 创建特性分支
ISSUE_NUM=$(gh issue view --json number --jq '.number' 2>/dev/null || echo "42")
git checkout -b "feature/issue-${ISSUE_NUM}"

# 3. 原子化提交：每个 commit 只做一件事
git commit -m "feat: 添加 CSV 导出接口"
git commit -m "feat: 添加 PDF 导出接口"
git commit -m "test: 添加导出功能单元测试"
git push -u origin "feature/issue-${ISSUE_NUM}"

# 4. 创建 PR，关联 Issue
gh pr create -t "feat: 添加报表导出功能" -F ./pr-body.md \
  -r "reviewer" -a @me -l "feature" --body "Closes #${ISSUE_NUM}"

# 5. CI 验证通过后，压缩合并
gh pr checks --watch && gh pr merge --squash --delete-branch
```

### 2.3 CI/CD 流水线管理

SpecWeave 的 CI 综合检查流水线通过 `gh` 命令进行管理：

```bash
# 查看所有工作流
gh workflow list

# 查看 CI 综合检查工作流的最新运行
gh run list -w "CI 综合检查" -L 5

# 手动触发 CI 综合检查
gh workflow run "CI 综合检查" --ref main

# 实时监控 CI 流水线状态
RUN_ID=$(gh run list -w "CI 综合检查" -L 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID"

# 查看失败的检查日志
gh run view "$RUN_ID" --log-failed

# 重跑失败的工作流
gh run rerun "$RUN_ID" --failed
```

### 2.4 Secret 与变量管理

在 CI/CD 自动化中，通过 `gh` 管理密钥和变量，避免手动操作 Web UI：

```bash
# 设置仓库级 Secret
gh secret set DEPLOY_SSH_KEY < ~/.ssh/deploy_key

# 设置环境级 Secret（适用于生产环境）
gh secret set DB_PASSWORD -e production -b "$(vault read -field=password secret/db)"

# 设置组织级 Secret（多仓库共享）
gh secret set NPM_PUBLISH_TOKEN -o my-org -b "$NPM_TOKEN"

# 设置 CI 变量
gh variable set DEPLOY_ENV -b "production"
gh variable set NOTIFY_SLACK_CHANNEL -b "#deployments"

# 批量导出 Secrets（审计用）
gh secret list --json name,updatedAt,visibility > secrets-audit.json
```

### 2.5 `gh copilot` — AI 辅助开发集成

`gh copilot` 是 GitHub CLI 的 Copilot 扩展，将 AI 辅助能力直接集成到命令行中，与 SpecWeave 的 AI 辅助开发理念高度契合：

```bash
# 解释复杂命令
gh copilot explain "git rebase -i HEAD~5"

# 生成 Shell 命令
gh copilot suggest "找出最近 7 天修改过的所有 TypeScript 文件"

# 解释代码逻辑
gh copilot explain "gh api /repos/owner/repo/actions/runs --jq '.workflow_runs[] | select(.conclusion==\"failure\")'"

# 将 Copilot 与 gh 命令结合使用
# 例如：生成一个分析 PR 合并趋势的脚本
gh copilot suggest "使用 gh api 和 jq 统计最近 30 天合并的 PR 数量"
```

### 2.6 跨仓库协作模式

在 SpecWeave 的多仓库架构中，`gh` 支持跨仓库的 Issue 转移和 PR 管理：

```bash
# 将 Issue 转移到其他仓库
gh issue transfer 42 owner/other-repo

# 列出跨仓库的待审查 PR
gh search prs --review-requested=@me --state=open --owner=my-org

# 跨仓库搜索代码引用
gh search code "import.*SpecWeave" --owner=my-org --language=typescript

# 批量克隆组织下的所有仓库
gh repo list my-org --limit 100 --json nameWithOwner --jq '.[].nameWithOwner' | \
  while read repo; do gh repo clone "$repo" "repos/$repo"; done
```

---

## 3. 常用工作流模式

### 3.1 日常开发一行命令

以下 Shell 一行命令覆盖了日常开发中最常见的场景：

```bash
# 快速创建 PR：推送当前分支后自动创建 PR
git push -u origin HEAD && gh pr create --fill

# 快速查看需要我审查的 PR
gh search prs --review-requested=@me --state=open

# 快速查看我被分配的 Issue
gh issue list --assignee @me --state open

# 快速查看我创建的 PR 的 CI 状态
gh pr checks $(gh pr list --author @me --limit 1 --json number --jq '.[0].number')

# 快速检出最近一个需要审查的 PR
gh pr checkout $(gh search prs --review-requested=@me --state=open --limit 1 --json number --jq '.[0].number')

# 快速合并当前分支对应的 PR（需确认 CI 通过）
gh pr checks --watch && gh pr merge --squash --delete-branch

# 快速同步 Fork 仓库
gh repo sync && git pull

# 快速查看今天的 GitHub 动态
gh api "users/$(gh api user --jq .login)/events" --jq '.[] | select(.created_at > "'$(date -u -Iseconds --date="24 hours ago")'") | "\(.type) \(.repo.name)"'
```

### 3.2 批量操作模式

```bash
# 批量关闭满足条件的 Issue
gh issue list -l "stale" -s open --limit 100 --json number --jq '.[].number' | \
  while read num; do
    gh issue close "$num" -c "自动关闭：超过 30 天无活动"
  done

# 批量标记 PR 的审查状态
gh pr list --label "needs-review" --limit 50 --json number --jq '.[].number' | \
  while read num; do
    gh pr review "$num" --comment -b "批量审查：请检查 CI 是否通过"
  done

# 批量下载 Release 资产
gh release list -L 10 --json tagName --jq '.[].tagName' | \
  while read tag; do
    gh release download "$tag" -p "*.tar.gz" -d "./releases/$tag"
  done

# 批量删除已合并的本地分支
git branch --merged | grep -v "main\|master\|develop" | xargs -r git branch -d
```

### 3.3 脚本自动化模板

以下是一个完整的 PR 自动化脚本模板，可在 SpecWeave 项目中使用：

```bash
#!/bin/bash
# auto-pr.sh — 自动化 PR 创建与合并脚本
# 用法：./auto-pr.sh "feat: 添加新功能" "feature/my-branch"

set -euo pipefail

TITLE="${1:?请提供 PR 标题}"
BRANCH="${2:?请提供特性分支名}"
BASE_BRANCH="${3:-main}"
REVIEWER="${4:-tech-lead}"

echo "=== 1. 创建特性分支 ==="
git checkout -b "$BRANCH"

echo "=== 2. 提交变更 ==="
git add .
git commit -m "$TITLE" || { echo "无变更可提交"; exit 1; }

echo "=== 3. 推送分支 ==="
git push -u origin "$BRANCH"

echo "=== 4. 创建 PR ==="
PR_URL=$(gh pr create \
  --title "$TITLE" \
  --base "$BASE_BRANCH" \
  --head "$BRANCH" \
  --fill \
  --reviewer "$REVIEWER" \
  --assignee "@me")

echo "=== 5. PR 已创建 ==="
echo "$PR_URL"

echo "=== 6. 等待 CI 检查 ==="
PR_NUM=$(echo "$PR_URL" | grep -oP '\d+$')
gh pr checks "$PR_NUM" --watch

echo "=== 7. CI 检查通过，是否立即合并？(y/n) ==="
read -r answer
if [ "$answer" = "y" ]; then
  gh pr merge "$PR_NUM" --squash --delete-branch
  echo "=== PR #$PR_NUM 已合并 ==="
  git checkout "$BASE_BRANCH"
  git pull
  git branch -d "$BRANCH"
else
  echo "=== PR #$PR_NUM 等待审查 ==="
fi
```

### 3.4 GitHub Actions 中的 `gh` 集成模板

```yaml
# .github/workflows/pr-automation.yml
name: PR Automation

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  auto-label:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - name: 自动添加标签
        run: |
          # 根据 PR 标题自动添加标签
          if echo "${{ github.event.pull_request.title }}" | grep -qi "^feat"; then
            gh pr edit ${{ github.event.pull_request.number }} --add-label "feature"
          elif echo "${{ github.event.pull_request.title }}" | grep -qi "^fix"; then
            gh pr edit ${{ github.event.pull_request.number }} --add-label "bug"
          elif echo "${{ github.event.pull_request.title }}" | grep -qi "^docs"; then
            gh pr edit ${{ github.event.pull_request.number }} --add-label "documentation"
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  ci-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 运行 CI 检查
        run: |
          # 运行项目 CI 检查
          npm ci
          npm run lint
          npm run test
      - name: 报告 CI 结果到 PR
        if: success() || failure()
        run: |
          STATUS="${{ job.status }}"
          if [ "$STATUS" = "success" ]; then
            gh pr comment ${{ github.event.pull_request.number }} \
              -b "✅ CI 检查全部通过"
          else
            gh pr comment ${{ github.event.pull_request.number }} \
              -b "❌ CI 检查失败，请查看 [Actions 日志](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})"
          fi
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3.5 常用别名推荐

将以下别名添加到 Shell 配置文件中，大幅提升日常开发效率：

```bash
# 将以下内容添加到 ~/.bashrc 或 ~/.zshrc

# GitHub CLI 快捷别名
alias ghpr='gh pr create --fill'                          # 快速创建 PR
alias ghprw='gh pr create --web'                          # 浏览器创建 PR
alias ghprs='gh pr status'                                # 查看 PR 状态
alias ghprl='gh pr list'                                  # 列出 PR
alias ghprv='gh pr view'                                  # 查看 PR 详情
alias ghprc='gh pr checkout'                              # 检出 PR
alias ghprd='gh pr diff'                                  # 查看 PR 差异
alias ghprm='gh pr merge --squash --delete-branch'        # 压缩合并 PR
alias ghprr='gh pr review --approve'                      # 批准 PR

alias ghisl='gh issue list --assignee @me'                # 列出我的 Issue
alias ghisc='gh issue create'                             # 创建 Issue
alias ghiss='gh issue status'                             # 查看 Issue 状态

alias ghrc='gh repo clone'                                # 克隆仓库
alias ghrv='gh repo view --web'                           # 浏览器查看仓库
alias ghrl='gh repo list'                                 # 列出仓库

alias ghci='gh run watch'                                 # 监控 CI 运行
alias ghcil='gh run list -L 5'                            # 列出最近 CI 运行

alias ghb='gh browse'                                     # 快速打开 GitHub
alias ghbs='gh browse --settings'                         # 打开仓库设置
```

### 3.6 `gh` 别名管理

除了 Shell 别名，`gh` 本身也支持内置别名，可在所有环境中使用：

```bash
# 创建 gh 内置别名
gh alias set co "pr checkout"
gh alias set prs "pr status"
gh alias set prm "pr merge --squash --delete-branch"
gh alias set prr "pr review --approve"
gh alias set issues "issue list --assignee @me"
gh alias set ci "run watch"

# 创建带 Shell 扩展的别名
gh alias set ci-status --shell 'gh run list -L 5 -w "CI"'

# 查看所有别名
gh alias list

# 删除别名
gh alias delete ci
```

---

## 4. 环境变量快速参考

| 环境变量 | 用途 | 示例 |
|---------|------|------|
| `GH_TOKEN` | 认证 Token（优先于 `GITHUB_TOKEN`） | `export GH_TOKEN=ghp_xxx` |
| `GITHUB_TOKEN` | 认证 Token（GitHub Actions 兼容） | 在 Actions 中自动注入 |
| `GH_HOST` | 默认 GitHub 主机名 | `export GH_HOST=github.example.com` |
| `GH_ENTERPRISE_TOKEN` | GHES 专用 Token | `export GH_ENTERPRISE_TOKEN=ghp_xxx` |
| `GH_REPO` | 默认仓库（`owner/repo`） | `export GH_REPO=octocat/Hello-World` |
| `GH_EDITOR` | 覆盖编辑器设置 | `export GH_EDITOR="code --wait"` |
| `GH_PAGER` | 覆盖分页器设置 | `export GH_PAGER="less -R"` |
| `GH_DEBUG` | 开启调试日志 | `export GH_DEBUG=api` |
| `GH_NO_UPDATE_NOTIFIER` | 禁用更新通知 | `export GH_NO_UPDATE_NOTIFIER=true` |
| `GH_PROMPT_DISABLED` | 禁用交互式提示 | `export GH_PROMPT_DISABLED=true` |
| `GH_CONFIG_DIR` | 自定义配置目录 | `export GH_CONFIG_DIR=/path/to/gh/config` |

---

## 5. 常用筛选参数汇总

### 5.1 Issue 搜索语法速查

| 搜索语法 | 说明 | 示例 |
|---------|------|------|
| `is:open` / `is:closed` | 按状态筛选 | `gh issue list -S "is:open"` |
| `label:<name>` | 按标签筛选 | `gh issue list -S "label:bug"` |
| `assignee:<user>` | 按负责人筛选 | `gh issue list -S "assignee:@me"` |
| `author:<user>` | 按作者筛选 | `gh issue list -S "author:octocat"` |
| `milestone:<name>` | 按里程碑筛选 | `gh issue list -S "milestone:v2.0"` |
| `<keyword> in:title` | 在标题中搜索 | `gh issue list -S "性能 in:title"` |
| `no:assignee` | 无负责人 | `gh issue list -S "no:assignee"` |
| `no:label` | 无标签 | `gh issue list -S "no:label"` |
| `created:>YYYY-MM-DD` | 按创建时间 | `gh issue list -S "created:>2026-01-01"` |
| `updated:<YYYY-MM-DD` | 按更新时间 | `gh issue list -S "updated:<2026-06-01"` |

### 5.2 PR 搜索语法速查

| 搜索语法 | 说明 | 示例 |
|---------|------|------|
| `is:open` / `is:closed` / `is:merged` | 按状态筛选 | `gh pr list -S "is:merged"` |
| `review-requested:@me` | 待我审查的 PR | `gh search prs --review-requested=@me` |
| `review:approved` | 已批准的 PR | `gh pr list -S "review:approved"` |
| `review:changes_requested` | 需要修改的 PR | `gh pr list -S "review:changes_requested"` |
| `draft:true` | 草稿 PR | `gh pr list -S "draft:true"` |
| `base:<branch>` | 按目标分支 | `gh pr list -S "base:main"` |
| `head:<branch>` | 按源分支 | `gh pr list -S "head:feature/*"` |
| `merged:>YYYY-MM-DD` | 按合并时间 | `gh pr list -S "merged:>2026-01-01"` |

---

## 6. 故障排查速查

| 问题 | 排查命令 | 解决方案 |
|------|---------|----------|
| 认证失败 | `gh auth status` | 重新登录：`gh auth login` |
| Token 权限不足 | `gh auth status` | 刷新 Token：`gh auth refresh -s repo,workflow` |
| 找不到仓库 | `gh repo view owner/repo` | 检查仓库名拼写，确认有访问权限 |
| PR 无法合并 | `gh pr checks <num>` / `gh pr view <num> --json reviews` | 确认 CI 通过且审查满足要求 |
| CI 运行失败 | `gh run view <id> --log-failed` | 查看失败日志定位原因 |
| 网络超时 | `gh config set http_proxy <url>` | 配置 HTTP 代理 |
| Fork 仓库过期 | `gh repo sync` | 同步上游更新 |
| 命令无响应 | `export GH_DEBUG=api` | 开启调试模式查看 API 请求 |

---

## 7. 相关资源

- [概述](00-overview.md) — 教程总览与架构图
- [安装与配置指南](01-installation.md) — 环境搭建与认证
- [基础命令指南](02-basic-commands.md) — 仓库/Issue/Gist 核心操作
- [Pull Request 工作流指南](03-pr-workflow.md) — PR 全生命周期管理
- [GitHub CLI 官方手册](https://cli.github.com/manual/) — 完整命令参考
- [GitHub CLI 仓库](https://github.com/cli/cli) — 源代码与 Issue 追踪