---
id: github-cli-wiki-05-advanced-usage
title: "高级用法指南"
source: "https://cli.github.com/manual/gh_api"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "advanced", "api", "alias", "extension", "search", "label", "ruleset", "attestation", "json", "jq", "graphql", "copilot"]
---

# 高级用法指南

本章涵盖 GitHub CLI（`gh`）的高级功能，包括 API 调用、别名系统、扩展管理、搜索语法、标签管理、规则集、工件签名验证、`--json` 输出与 `jq` 组合等。掌握这些能力后，你将能够将 `gh` 深度集成到自动化脚本和 CI/CD 流水线中。

> **前置条件**：请确保已完成 [安装与配置指南](01-installation.md) 中的认证流程，并熟悉 [基础命令指南](02-basic-commands.md) 中的核心命令。

---

## 1. gh api：直接调用 GitHub API

`gh api` 是 GitHub CLI 最强大的命令之一，它允许你直接调用 GitHub REST API 和 GraphQL API，无需手动处理认证、分页和响应格式化。所有 `gh api` 调用自动使用当前登录的认证凭据。

### 1.1 基本 REST API 调用

最简单的用法是直接指定 API 端点（以 `/` 开头为 REST API）：

```bash
# 获取当前用户信息
gh api /user

# 获取仓库信息
gh api /repos/cli/cli

# 获取仓库的 Issue 列表
gh api /repos/cli/cli/issues

# 获取指定 Issue
gh api /repos/cli/cli/issues/1
```

**端点路径规则**：

| 端点格式 | 说明 |
|----------|------|
| `/endpoint` | 以 `/` 开头，自动补全为 `https://api.github.com/endpoint` |
| `graphql` | 不带 `/` 前缀，以 `graphql` 开头则发起 GraphQL 请求 |
| `https://...` | 完整 URL，直接调用（可用于 GitHub Enterprise Server） |
| `host/endpoint` | `host` 部分指定目标主机（如 `my-ghe.com/api/v3/...`） |

```bash
# 调用 GitHub Enterprise Server 的 API
gh api my-ghe.com/api/v3/repos/my-org/my-repo

# 使用完整 URL
gh api https://api.github.com/repos/cli/cli/releases/latest
```

### 1.2 指定 HTTP 方法：`--method`

`gh api` 默认使用 `GET` 方法。通过 `--method`（或 `-X`）指定其他 HTTP 动词：

```bash
# POST 请求：创建 Issue
gh api /repos/cli/cli/issues --method POST \
  --field title="Bug Report" \
  --field body="This is a bug report."

# PATCH 请求：更新 Issue
gh api /repos/cli/cli/issues/1 --method PATCH \
  --field title="Updated Title" \
  --field state="closed"

# PUT 请求：更新仓库设置
gh api /repos/cli/cli --method PATCH \
  --field description="Updated description" \
  --field has_issues=false

# DELETE 请求：删除 Issue 评论
gh api /repos/cli/cli/issues/comments/123 --method DELETE
```

**支持的 HTTP 方法**：

| 方法 | 典型用途 |
|------|----------|
| `GET` | 读取资源（默认） |
| `POST` | 创建资源 |
| `PATCH` | 部分更新资源 |
| `PUT` | 完整替换资源 |
| `DELETE` | 删除资源 |

### 1.3 传递参数：`--field`、`--raw-field` 和 `--input`

`gh api` 提供三种向 API 传递数据的方式：

#### `--field` / `-F`：自动类型转换

`--field` 会自动将值转换为合适的 JSON 类型。字符串值按原样传递，数字和布尔值会尝试自动解析：

```bash
# 创建 Issue，自动序列化为 JSON
gh api /repos/cli/cli/issues --method POST \
  --field title="Bug Report" \
  --field body="Description here" \
  --field labels='["bug","high-priority"]'
```

#### `--raw-field` / `-f`：字符串原样传递

`--raw-field` 将所有值作为字符串传递，不进行类型转换：

```bash
# 数字和布尔值作为字符串传递
gh api /repos/cli/cli/issues --method POST \
  --raw-field title="Bug Report" \
  --raw-field body="true"  # 作为字符串 "true"，不是布尔值
```

#### 嵌套参数语法

`--field` 和 `--raw-field` 支持点号分隔的嵌套键名，自动构建嵌套 JSON 对象：

```bash
# 嵌套参数：自动构建 { "security_and_analysis": { "secret_scanning": { "status": "enabled" } } }
gh api /repos/my-org/my-repo --method PATCH \
  --field security_and_analysis.secret_scanning.status="enabled"
```

#### `--input` / `--input -`：从文件或标准输入读取请求体

```bash
# 从文件读取 JSON 请求体
gh api /repos/cli/cli/issues --method POST --input issue.json

# 从标准输入读取
echo '{"title":"From stdin","body":"Created via stdin"}' | gh api /repos/cli/cli/issues --method POST --input -
```

### 1.4 自定义请求头：`--header`

```bash
# 添加自定义请求头
gh api /repos/cli/cli --header "Accept: application/vnd.github.v3+json"

# 多个请求头
gh api /repos/cli/cli/issues \
  --header "Accept: application/vnd.github.v3+json" \
  --header "X-Custom-Header: value"
```

### 1.5 API 预览：`--preview`

某些 GitHub API 功能处于预览阶段，需要显式启用：

```bash
# 启用 API 预览功能
gh api /repos/cli/cli/code-scanning/alerts --preview "cloak"

# 多个预览功能
gh api /repos/cli/cli/code-scanning/alerts \
  --preview "cloak" \
  --preview "london"
```

### 1.6 分页处理：`--paginate` 和 `--slurp`

GitHub API 默认每页返回 30 条记录。`--paginate` 自动遍历所有分页，`--slurp` 将所有分页合并为单个 JSON 数组：

```bash
# 自动遍历所有分页，逐页输出
gh api /repos/cli/cli/issues --paginate

# 将所有分页合并为单个 JSON 数组
gh api /repos/cli/cli/issues --paginate --slurp

# 控制每页大小
gh api /repos/cli/cli/issues --paginate --jq '.[].title'
```

**`--paginate` 与 `--slurp` 的区别**：

| 选项 | 行为 | 输出格式 |
|------|------|----------|
| 无 | 仅返回第一页（默认 30 条） | 单个 JSON 数组 |
| `--paginate` | 遍历所有分页，逐页输出 | 多个 JSON 数组（每页一个） |
| `--paginate --slurp` | 遍历所有分页，合并后输出 | 单个 JSON 数组（所有结果合并） |

### 1.7 JSON 过滤：`--jq`

`--jq` 使用 jq 语法对 API 响应进行过滤和转换，是 `gh api` 最常用的输出处理选项：

```bash
# 提取单个字段
gh api /repos/cli/cli --jq '.stargazers_count'

# 提取多个字段，构造新对象
gh api /repos/cli/cli --jq '{name: .full_name, stars: .stargazers_count, forks: .forks_count}'

# 遍历数组，提取每个元素的指定字段
gh api /repos/cli/cli/issues --jq '.[] | {title: .title, state: .state, url: .html_url}'

# 过滤并提取
gh api /repos/cli/cli/issues --jq '.[] | select(.state == "open") | .title'

# 计算统计
gh api /repos/cli/cli/issues --jq '[.[] | .state] | group_by(.) | map({state: .[0], count: length})'
```

**常用 jq 表达式速查**：

| 需求 | jq 表达式 |
|------|-----------|
| 提取单个字段 | `.field_name` |
| 提取嵌套字段 | `.parent.child` |
| 数组第一个元素 | `.[0]` |
| 数组长度 | `length` |
| 过滤（条件选择） | `select(.field == "value")` |
| 映射（转换每个元素） | `map(.field)` |
| 构造新对象 | `{key1: .field1, key2: .field2}` |
| 管道组合 | `\|` |
| 分组 | `group_by(.field)` |
| 切片 | `.[0:5]` |

### 1.8 Go 模板输出：`--template`

`--template` 使用 Go 模板语法格式化输出，适合需要精确控制输出格式的场景：

```bash
# 使用 Go 模板格式化输出
gh api /repos/cli/cli --template '{{.full_name}} has {{.stargazers_count}} stars'

# 遍历数组
gh api /repos/cli/cli/issues --template \
  '{{range .}}{{.title}} ({{.state}})
{{end}}'

# 使用 printf 格式化
gh api /repos/cli/cli --template \
  '{{printf "%s: %d stars, %d forks" .full_name .stargazers_count .forks_count}}'
```

**`--jq` 与 `--template` 的选择**：

| 场景 | 推荐 |
|------|------|
| JSON 结构化输出 | `--jq` |
| 纯文本/Human-readable 输出 | `--template` |
| 复杂数据转换/过滤 | `--jq` |
| 简单字段提取 | 两者皆可 |

### 1.9 缓存：`--cache`

`--cache` 对 GET 请求的结果进行缓存，在缓存有效期内避免重复请求：

```bash
# 缓存 1 小时（默认 3600 秒）
gh api /repos/cli/cli --cache 1h

# 缓存 30 分钟
gh api /repos/cli/cli --cache 30m

# 缓存 10 分钟（秒为单位）
gh api /repos/cli/cli --cache 600s
```

### 1.10 占位符值

`gh api` 支持在 URL 路径中使用占位符，自动替换为当前仓库上下文：

| 占位符 | 替换为 |
|--------|--------|
| `{owner}` | 当前仓库的 owner |
| `{repo}` | 当前仓库名 |
| `{branch}` | 当前分支名 |

```bash
# 在仓库目录内执行，自动替换 {owner} 和 {repo}
cd ~/projects/my-project
gh api /repos/{owner}/{repo}/issues

# 等价于
gh api /repos/my-org/my-project/issues
```

### 1.11 从文件读取请求体：`@filename`

当请求体内容较大时，可以使用 `@` 前缀从文件读取：

```bash
# 将文件内容作为字段值
gh api /repos/cli/cli/issues --method POST \
  --field title="Large Issue" \
  --field body=@issue-body.md

# 也支持从标准输入
echo "Issue body from stdin" | gh api /repos/cli/cli/issues --method POST \
  --field title="Test" \
  --field body=@-
```

### 1.12 GraphQL API 调用

当端点参数不以 `/` 开头时，`gh api` 自动识别为 GraphQL 查询：

```bash
# 基本 GraphQL 查询
gh api graphql -f query='
  query {
    viewer {
      login
      name
      repositories(first: 5) {
        nodes {
          name
          stargazerCount
        }
      }
    }
  }
'

# 带变量的 GraphQL 查询
gh api graphql \
  --field query='
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        issues(first: 10, states: OPEN) {
          nodes {
            title
            url
          }
        }
      }
    }
  ' \
  --field owner="cli" \
  --field repo="cli"

# 使用 --jq 处理 GraphQL 响应
gh api graphql -f query='
  query { viewer { login } }
' --jq '.data.viewer.login'
```

**REST vs GraphQL 选择**：

| 场景 | 推荐 |
|------|------|
| 简单 CRUD 操作 | REST API |
| 需要关联多个资源的数据 | GraphQL |
| 需要精确控制返回字段 | GraphQL |
| 批量操作 | REST（配合 `--paginate`） |

### 1.13 完整工作流示例

```bash
# 创建一个带标签的 Issue，并获取其 URL
ISSUE_URL=$(gh api /repos/{owner}/{repo}/issues --method POST \
  --field title="自动化创建的 Issue" \
  --field body="由 CI 流水线自动创建" \
  --field labels='["automation","ci"]' \
  --jq '.html_url')

echo "Issue 已创建：$ISSUE_URL"

# 批量关闭所有标题包含 "过期" 的 Issue
gh api "/repos/{owner}/{repo}/issues?state=open&per_page=100" --paginate \
  --jq '.[] | select(.title | contains("过期")) | .number' | \
  while read -r num; do
    gh api "/repos/{owner}/{repo}/issues/$num" --method PATCH \
      --field state="closed"
    echo "已关闭 Issue #$num"
  done
```

---

## 2. gh alias：命令别名

`gh alias` 允许你为常用命令组合创建自定义别名，大幅提升操作效率。

### 2.1 设置别名：`gh alias set`

```bash
# 创建基本别名
gh alias set bugs 'issue list --label="bugs"'

# 创建带参数的别名
gh alias set prc 'pr create'

# 使用别名
gh bugs        # 等价于 gh issue list --label="bugs"
gh prc         # 等价于 gh pr create
```

**别名中的 Shell 参数**：`$1`、`$2` 等表示位置参数，`$@` 表示所有参数：

```bash
# 带参数的别名
gh alias set co 'pr checkout $1'

# 使用：gh co 42  →  gh pr checkout 42

# 传递所有参数
gh alias set prv 'pr view $@'

# 使用：gh prv 42 --web  →  gh pr view 42 --web
```

**常用实用别名示例**：

```bash
# PR 相关
gh alias set prc 'pr create'
gh alias set prm 'pr merge'
gh alias set prv 'pr view'
gh alias set prco 'pr checkout'
gh alias set prd 'pr diff'
gh alias set prs 'pr status'

# Issue 相关
gh alias set bugs 'issue list --label="bugs"'
gh alias set myissues 'issue list --assignee @me'
gh alias set ic 'issue create'

# 仓库相关
gh alias set rv 'repo view'
gh alias set rc 'repo clone'

# 快速查看当前仓库的 CI 状态
gh alias set ci 'run list --limit 10'

# 查看所有未读通知
gh alias set inbox 'api /notifications --jq ".[] | .subject.title"'
```

### 2.2 列出别名：`gh alias list`

```bash
# 列出所有已定义的别名
gh alias list

# 输出示例：
# bugs: issue list --label="bugs"
# co: pr checkout $1
# prc: pr create
```

### 2.3 删除别名：`gh alias delete`

```bash
# 删除指定别名
gh alias delete bugs
```

### 2.4 导入别名：`gh alias import`

从 YAML 文件批量导入别名：

```yaml
# aliases.yaml
prc: pr create
prm: pr merge --auto
prv: pr view $1
bugs: issue list --label="bugs"
myissues: issue list --assignee @me
ci: run list --limit 10
```

```bash
# 导入别名文件
gh alias import aliases.yaml
```

---

## 3. gh extension：扩展管理

`gh extension` 允许你安装社区或自定义开发的扩展，扩展 `gh` 的功能边界。

### 3.1 安装扩展：`gh extension install`

```bash
# 从 GitHub 仓库安装
gh extension install owner/repo

# 安装指定版本
gh extension install owner/repo@v1.2.3

# 从本地路径安装
gh extension install /path/to/local/extension
```

**常用社区扩展推荐**：

| 扩展 | 仓库 | 用途 |
|------|------|------|
| `gh-poi` | `seachicken/gh-poi` | 交互式清理本地分支 |
| `gh-dash` | `dlvhdr/gh-dash` | 交互式仪表盘 |
| `gh-copilot` | `github/gh-copilot` | Copilot CLI 集成 |
| `gh-eco` | `coloradocolby/gh-eco` | 探索生态系统 |
| `gh-s` | `gennaro-tedesco/gh-s` | 交互式搜索 |

### 3.2 列出已安装扩展：`gh extension list`

```bash
gh extension list
```

### 3.3 搜索扩展：`gh extension search`

```bash
# 搜索扩展
gh extension search "topic"

# 搜索 PR 相关扩展
gh extension search "pr"
```

### 3.4 升级扩展：`gh extension upgrade`

```bash
# 升级单个扩展
gh extension upgrade owner/repo

# 升级所有扩展
gh extension upgrade --all
```

### 3.5 移除扩展：`gh extension remove`

```bash
gh extension remove owner/repo
```

### 3.6 浏览扩展仓库：`gh extension browse`

```bash
# 在浏览器中打开扩展的 GitHub 仓库
gh extension browse owner/repo
```

### 3.7 创建扩展：`gh extension create`

```bash
# 创建新的扩展项目
gh extension create my-extension
```

### 3.8 执行扩展：`gh extension exec`

```bash
# 直接执行已安装的扩展
gh extension exec owner/repo
```

---

## 4. gh search：搜索

`gh search` 提供对 GitHub 上仓库、Issue、PR、代码和提交的全文搜索能力。

### 4.1 搜索仓库：`gh search repos`

```bash
# 基本搜索
gh search repos "topic:cli"

# 按语言和星标数搜索
gh search repos "language:go stars:>1000"

# 按更新时间搜索
gh search repos "pushed:>2024-01-01"

# 搜索组织下的仓库
gh search repos "org:github"

# 组合搜索
gh search repos "topic:cli language:go stars:>500"
```

### 4.2 搜索 Issue：`gh search issues`

```bash
# 搜索标题包含关键词的 Issue
gh search issues "bug"

# 按标签和状态搜索
gh search issues "label:bug state:open"

# 按仓库搜索
gh search issues "repo:cli/cli"

# 按作者搜索
gh search issues "author:username"

# 按里程碑搜索
gh search issues "milestone:v1.0"
```

### 4.3 搜索 PR：`gh search prs`

```bash
# 搜索 PR
gh search prs "fix"

# 搜索草稿 PR
gh search prs "draft:true"

# 按审查状态搜索
gh search prs "review:required"

# 按合并状态搜索
gh search prs "is:merged"
```

### 4.4 搜索代码：`gh search code`

```bash
# 搜索代码内容
gh search code "TODO"

# 按语言和仓库搜索
gh search code "import React" --language javascript

# 按路径搜索
gh search code "main" --path "cmd/"

# 按文件扩展名搜索
gh search code "class" --extension py
```

### 4.5 搜索提交：`gh search commits`

```bash
# 搜索提交信息
gh search commits "fix:"

# 按作者搜索
gh search commits "author:username"

# 按仓库搜索
gh search commits "repo:cli/cli fix:"
```

### 4.6 搜索语法速查

| 限定符 | 用途 | 示例 |
|--------|------|------|
| `repo:` | 限定仓库 | `repo:cli/cli` |
| `org:` | 限定组织 | `org:github` |
| `user:` | 限定用户 | `user:username` |
| `language:` | 限定语言 | `language:python` |
| `label:` | 限定标签 | `label:bug` |
| `state:` | 限定状态 | `state:open` |
| `author:` | 限定作者 | `author:username` |
| `assignee:` | 限定指派人 | `assignee:@me` |
| `milestone:` | 限定里程碑 | `milestone:"v1.0"` |
| `stars:` | 按星标数过滤 | `stars:>100` |
| `pushed:` | 按推送时间过滤 | `pushed:>2024-01-01` |
| `is:` | 限定类型/状态 | `is:merged` `is:public` |
| `draft:` | 是否为草稿 | `draft:true` |
| `review:` | 审查状态 | `review:required` |

### 4.7 排除语法

搜索时可以使用 `NOT` 排除特定条件：

```bash
# Unix/Linux/Mac：使用反斜杠转义
gh search repos "language:go NOT stars:\>1000"

# Windows PowerShell：使用反引号转义
gh search repos "language:go NOT stars:`>1000"

# Windows CMD：使用 ^ 转义
gh search repos "language:go NOT stars:^>1000"

# 排除多个条件
gh search issues "repo:cli/cli NOT label:wontfix NOT label:duplicate"
```

---

## 5. gh label：标签管理

`gh label` 提供对仓库 Issue/PR 标签的完整管理能力。

### 5.1 列出标签：`gh label list`

```bash
# 列出所有标签
gh label list

# 限制数量
gh label list --limit 50

# 按名称搜索
gh label list --search "bug"

# 排序
gh label list --sort created --order desc

# JSON 输出
gh label list --json name,color,description
```

### 5.2 创建标签：`gh label create`

```bash
# 创建标签
gh label create "high-priority" --color "FF0000" --description "最高优先级"

# 创建标签（交互式）
gh label create "feature"
```

### 5.3 编辑标签：`gh label edit`

```bash
# 修改标签颜色
gh label edit "high-priority" --color "FF4444"

# 修改标签描述
gh label edit "high-priority" --description "更新后的描述"
```

### 5.4 删除标签：`gh label delete`

```bash
# 删除标签（需确认）
gh label delete "high-priority"
```

### 5.5 克隆标签：`gh label clone`

将一个仓库的标签批量复制到另一个仓库：

```bash
# 从源仓库克隆标签到当前仓库
gh label clone source-owner/source-repo

# 强制覆盖已存在的标签
gh label clone source-owner/source-repo --force
```

---

## 6. gh attestation：工件签名验证

`gh attestation` 用于管理、下载和验证 Sigstore 签名的工件（artifact），确保软件供应链安全。

### 6.1 基本用法

```bash
# 下载仓库的认证工件
gh attestation download owner/repo

# 查看认证工件详情
gh attestation trusted-root

# 验证命令
gh attestation verify
```

### 6.2 验证工件完整性：`gh attestation verify`

```bash
# 验证本地文件
gh attestation verify ./binary-file

# 验证指定仓库的发布文件
gh attestation verify --repo cli/cli ./gh_2.0.0_linux_amd64.tar.gz

# 验证指定所有者
gh attestation verify --owner github ./binary-file

# 指定摘要算法
gh attestation verify --digest-alg sha256 ./binary-file

# 限制证书颁发者
gh attestation verify --cert-identity "https://github.com/cli/cli/.github/workflows/release.yml@refs/tags/v2.0.0" \
  --cert-oidc-issuer "https://token.actions.githubusercontent.com" ./binary-file

# 使用自定义信任根
gh attestation verify --custom-trusted-root ./trusted_root.json ./binary-file

# 跳过在线验证（仅离线验证）
gh attestation verify --denylist ./binary-file

# 详细输出格式
gh attestation verify --format json ./binary-file
```

**验证参数一览**：

| 参数 | 说明 |
|------|------|
| `--repo` | 限制为指定仓库的认证 |
| `--owner` | 限制为指定所有者的认证 |
| `--cert-identity` | 期望的证书身份 |
| `--cert-oidc-issuer` | 期望的 OIDC 颁发者 |
| `--digest-alg` | 摘要算法（sha256/sha512） |
| `--format` | 输出格式（json） |
| `--custom-trusted-root` | 自定义信任根文件 |
| `--denylist` | 仅在离线/拒绝列表模式下验证 |
| `--no-public-good` | 不使用公共透明日志 |
| `--signer-repo` | 签名者仓库 |
| `--signer-workflow` | 签名者工作流 |

---

## 7. gh ruleset：仓库规则集管理

`gh ruleset` 用于管理仓库的规则集（Rulesets），控制分支保护、标签要求、必需状态检查等策略。

### 7.1 列出规则集：`gh ruleset list`

```bash
# 列出当前仓库的规则集
gh ruleset list

# 列出组织的规则集
gh ruleset list --org my-org

# JSON 输出
gh ruleset list --json name,enforcement,status
```

### 7.2 查看规则集：`gh ruleset view`

```bash
# 查看指定规则集详情
gh ruleset view 12345

# 在浏览器中查看
gh ruleset view 12345 --web

# 查看组织规则集
gh ruleset view 12345 --org my-org
```

### 7.3 检查规则集：`gh ruleset check`

```bash
# 检查当前分支是否满足规则集要求
gh ruleset check

# 检查指定分支
gh ruleset check --branch main
```

---

## 8. gh org：组织管理

`gh org` 用于查看和管理 GitHub 组织信息。

```bash
# 查看组织成员列表
gh org list

# 查看指定组织成员
gh org members my-org

# 查看组织成员（含角色）
gh org members my-org --role admin
```

---

## 9. gh project：项目管理

`gh project` 用于管理 GitHub Projects（项目看板）。

```bash
# 列出项目
gh project list

# 查看项目详情
gh project view 123

# 列出项目中的条目
gh project item-list 123
```

---

## 10. gh copilot：Copilot 集成

`gh copilot` 提供对 GitHub Copilot 的命令行访问。

```bash
# 查看 Copilot 使用情况
gh copilot usage

# 查看 Copilot 配置
gh copilot config

# 查看 Copilot 扩展
gh copilot extension
```

---

## 11. `--json` 输出与 `jq` 组合

几乎所有 `gh` 命令都支持 `--json` 参数，输出结构化的 JSON 数据。搭配 `jq` 可以实现强大的数据提取和自动化。

### 11.1 基本 `--json` 用法

```bash
# 指定需要输出的字段
gh pr list --json number,title,state,author,createdAt

# 查看可用字段
gh pr list --json help

# 查看所有字段
gh pr list --json help --include-fields
```

### 11.2 `--json` 与 `jq` 组合实战

```bash
# 查找所有需要我审查的 PR
gh pr list --json number,title,author,reviewRequests \
  --search "review-requested:@me" \
  --jq '.[] | "\(.number): \(.title) by \(.author.login)"'

# 统计每个作者的 PR 数量
gh pr list --json author --jq 'group_by(.author.login) | map({author: .[0].author.login, count: length})'

# 查找所有超过 7 天未更新的 PR 并输出为表格
gh pr list --json number,title,updatedAt,author \
  --jq '.[] | select((.updatedAt | fromdate) < (now - 7*24*3600)) | "\(.number)\t\(.title)\t\(.author.login)"'

# 列出所有包含 "bug" 标签的 Issue，按创建时间排序
gh issue list --json number,title,labels,createdAt \
  --search "label:bug" \
  --jq 'sort_by(.createdAt) | .[] | "\(.number): \(.title)"'

# 导出仓库所有 Issue 到 CSV
gh issue list --limit 1000 --json number,title,state,labels,author,createdAt \
  --jq '["number","title","state","labels","author","createdAt"], (.[] | [.number, .title, .state, (.labels | map(.name) | join(";")), .author.login, .createdAt]) | @csv'

# 查找所有带有 "help wanted" 标签且无指派的 Issue
gh issue list --json number,title,labels,assignees \
  --search "label:\"help wanted\" no:assignee" \
  --jq '.[] | "\(.number): \(.title)"'
```

### 11.3 高级数据管道

```bash
# 获取所有已合并 PR 的作者统计
gh pr list --state merged --limit 1000 --json author \
  --jq 'group_by(.author.login) | map({author: .[0].author.login, prs: length}) | sort_by(-.prs)'

# 查找重复标签（名称相似）
gh label list --json name --jq '[.[].name]' | jq 'group_by(.[0:1]) | map(select(length > 1))'

# 批量检查所有仓库的 CI 状态
gh repo list --json name --jq '.[].name' | while read -r repo; do
  echo "=== $repo ==="
  gh run list --repo "{owner}/$repo" --limit 3
done

# 导出所有 PR 审查时间统计
gh pr list --state merged --limit 500 --json number,title,createdAt,mergedAt \
  --jq '.[] | {number, title, hours: (((.mergedAt | fromdate) - (.createdAt | fromdate)) / 3600 | floor)} | select(.hours > 0)'
```

### 11.4 `--jq` 与 `--template` 的选择

| 特性 | `--jq` | `--template` |
|------|--------|-------------|
| 输出格式 | JSON | 任意文本 |
| 学习曲线 | 中等（需学 jq 语法） | 低（Go 模板语法） |
| 数据过滤 | 强（select/map/group_by） | 弱（仅 range） |
| 类型转换 | 自动 | 需手动 |
| 适用场景 | 数据管道、JSON 输出 | 人类可读的文本输出 |

---

## 12. 真实世界高级工作流

### 12.1 自动化 Release 流水线

```bash
#!/bin/bash
# 自动化发布流程：创建 tag → 生成 Release Notes → 发布 Release

VERSION=$1
RELEASE_NOTES=$(gh api "/repos/{owner}/{repo}/releases/generate-notes" \
  --method POST \
  --field tag_name="$VERSION" \
  --jq '.body')

git tag -a "$VERSION" -m "Release $VERSION"
git push origin "$VERSION"

gh release create "$VERSION" \
  --title "Release $VERSION" \
  --notes "$RELEASE_NOTES" \
  --generate-notes
```

### 12.2 批量 Issue 清理

```bash
#!/bin/bash
# 关闭所有超过 90 天未更新的 Issue 并添加 "stale" 标签

CUTOFF=$(date -d "90 days ago" +%Y-%m-%d)

gh issue list --state open --limit 1000 \
  --json number,updatedAt \
  --jq ".[] | select(.updatedAt < \"$CUTOFF\") | .number" | \
  while read -r num; do
    gh issue edit "$num" --add-label "stale"
    gh issue comment "$num" --body "此 Issue 已超过 90 天未更新，自动标记为 stale。"
    gh issue close "$num" --reason "not planned"
    echo "已关闭 Issue #$num"
  done
```

### 12.3 PR 审查仪表盘

```bash
#!/bin/bash
# 生成个人审查仪表盘

echo "=== 需要我审查的 PR ==="
gh pr list --search "review-requested:@me" \
  --json number,title,author,createdAt \
  --jq '.[] | "  #\(.number): \(.title) (by @\(.author.login))"'

echo ""
echo "=== 我创建的待合并 PR ==="
gh pr list --search "author:@me is:open" \
  --json number,title,state,createdAt \
  --jq '.[] | "  #\(.number): \(.title) (\(.state))"'

echo ""
echo "=== 最近失败的 CI ==="
gh run list --limit 5 --status failure \
  --json displayTitle,conclusion,updatedAt,headBranch \
  --jq '.[] | "  \(.headBranch): \(.displayTitle) - \(.conclusion)"'
```

### 12.4 仓库健康度检查

```bash
#!/bin/bash
# 仓库健康度检查脚本

echo "=== 仓库健康度报告 ==="

# 基本信息
REPO=$(gh repo view --json name,stargazerCount,openIssues,openPullRequests,licenseInfo,defaultBranchRef \
  --jq '{name: .name, stars: .stargazerCount, issues: .openIssues, prs: .openPullRequests, license: .licenseInfo.name, defaultBranch: .defaultBranchRef.name}')

echo "$REPO" | jq '.'

# 无标签的 Issue
echo ""
echo "无标签的 Issue："
gh issue list --json number,title --jq '.[] | "  #\(.number): \(.title)"' | head -5

# 没有 CI 通过的 PR
echo ""
echo "CI 失败的 PR："
gh pr list --json number,title,statusCheckRollup \
  --jq '.[] | select(.statusCheckRollup | length > 0) | "  #\(.number): \(.title)"' | head -5

# 长期未更新的 PR
echo ""
echo "超过 30 天未更新的 PR："
gh pr list --json number,title,updatedAt \
  --jq '.[] | select((.updatedAt | fromdate) < (now - 30*24*3600)) | "  #\(.number): \(.title)"' | head -5
```

### 12.5 跨仓库同步标签

```bash
#!/bin/bash
# 将标准标签集同步到多个仓库

REPOS=("repo1" "repo2" "repo3")
OWNER="my-org"

for repo in "${REPOS[@]}"; do
  echo "同步标签到 $OWNER/$repo..."
  gh label clone "$OWNER/template-repo" --repo "$OWNER/$repo" --force
done
```

### 12.6 使用 GraphQL 进行高效数据查询

```bash
# 一次性获取仓库的 Issue、PR 和 Release 统计
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      issues(states: OPEN) { totalCount }
      pullRequests(states: OPEN) { totalCount }
      releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
        nodes { tagName publishedAt }
      }
      stargazers { totalCount }
      forks { totalCount }
    }
  }
' -f owner="{owner}" -f repo="{repo}" --jq '.data.repository'
```

---

## 13. 本章总结

本章涵盖了 `gh` 的高级用法，核心要点如下：

| 主题 | 关键能力 | 典型场景 |
|------|----------|----------|
| `gh api` | 直接调用 REST/GraphQL API | 自动化、数据管道、批量操作 |
| `gh alias` | 命令别名管理 | 简化常用命令组合 |
| `gh extension` | 扩展管理 | 安装社区/自定义扩展 |
| `gh search` | 全文搜索 | 发现代码、Issue、PR |
| `gh label` | 标签 CRUD | 标签管理、跨仓库同步 |
| `gh attestation` | 工件签名验证 | 供应链安全 |
| `gh ruleset` | 规则集管理 | 分支保护、合规策略 |
| `--json` + `jq` | 结构化输出与数据处理 | 数据管道、自动化脚本 |

> **下一步**：阅读 [CI/CD 集成指南](04-ci-cd-integration.md) 了解如何将 `gh` 深度集成到 GitHub Actions 工作流中。（注：如该章节尚未完成，可先阅读 [GitHub CLI 官方手册](https://cli.github.com/manual/) 了解更多）