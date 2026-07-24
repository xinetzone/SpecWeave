---
id: github-cli-wiki-04-actions-cicd
title: "Actions 与 CI/CD 集成指南"
source: "https://cli.github.com/manual/gh_run"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "actions", "ci-cd", "workflow", "run", "secret", "variable", "cache", "automation"]
---

# Actions 与 CI/CD 集成指南

本章介绍使用 `gh` 命令行工具管理 GitHub Actions 的完整生命周期：从工作流（Workflow）的启停管理、运行（Run）的追踪与重试，到缓存（Cache）清理、密钥（Secret）和变量（Variable）的安全配置。

GitHub CLI 的 Actions 相关命令以 `gh workflow`、`gh run`、`gh cache`、`gh secret`、`gh variable` 五个子命令组为入口，覆盖 CI/CD 流水线的全部操作。在开始之前，请确保已完成 [安装与配置](01-installation.md) 中的认证步骤。

## 1. 快速参考

下表汇总了各命令组的核心用途：

| 命令组 | 用途 | 典型场景 |
|--------|------|----------|
| `gh workflow` | 工作流管理 | 查看/启停工作流，手动触发运行 |
| `gh run` | 运行追踪 | 查看运行状态、日志、重试、下载产物 |
| `gh cache` | 缓存管理 | 查看/清理 Actions 缓存 |
| `gh secret` | 密钥管理 | 配置仓库/环境/组织级密钥 |
| `gh variable` | 变量管理 | 配置仓库/环境/组织级变量 |

## 2. gh workflow：工作流管理

`gh workflow` 用于管理仓库中定义的 GitHub Actions 工作流，支持查看、启用、禁用和手动触发运行。

### 2.1 gh workflow list

列出仓库中所有可用的工作流。

**基本语法**：

```bash
gh workflow list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--limit <int>` 或 `-L` | 最大返回数量（默认 50） |
| `--all` 或 `-a` | 包含已禁用的工作流 |

**示例**：

```bash
# 列出当前仓库的所有工作流
gh workflow list

# 限制返回数量
gh workflow list --limit 10

# 包含已禁用的工作流
gh workflow list --all
```

输出示例：

```
CI                             active  12345678  .github/workflows/ci.yml
Deploy                         active  23456789  .github/workflows/deploy.yml
Nightly Build                  disabled 34567890 .github/workflows/nightly.yml
```

### 2.2 gh workflow view

查看工作流的详细信息，包括其定义文件和最近运行记录。

**基本语法**：

```bash
gh workflow view [<workflow-id> | <workflow-name> | <filename>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--web` 或 `-w` | 在浏览器中打开工作流页面 |
| `--ref <string>` 或 `-r` | 查看指定分支/标签上的工作流 |
| `--json <fields>` | 以 JSON 格式输出 |
| `--yaml` 或 `-y` | 以 YAML 格式输出工作流定义文件内容 |

**示例**：

```bash
# 查看名为 "CI" 的工作流
gh workflow view CI

# 按文件名查看
gh workflow view ".github/workflows/ci.yml"

# 在浏览器中打开
gh workflow view CI --web

# 查看指定分支上的工作流定义
gh workflow view CI --ref main

# 以 YAML 格式输出工作流定义
gh workflow view CI --yaml

# JSON 格式输出
gh workflow view CI --json name,state,id,path
```

### 2.3 gh workflow enable

启用一个已禁用的工作流。

**基本语法**：

```bash
gh workflow enable [<workflow-id> | <workflow-name> | <filename>]
```

**示例**：

```bash
# 按名称启用
gh workflow enable CI

# 按文件名启用
gh workflow enable ".github/workflows/deploy.yml"

# 按 ID 启用
gh workflow enable 12345678
```

### 2.4 gh workflow disable

禁用一个工作流。禁用后，该工作流不会响应任何触发事件（包括 push、pull_request、schedule 等），但手动触发（`gh workflow run`）仍然有效。

**基本语法**：

```bash
gh workflow disable [<workflow-id> | <workflow-name> | <filename>]
```

**示例**：

```bash
# 按名称禁用
gh workflow disable "Nightly Build"

# 按文件名禁用
gh workflow disable ".github/workflows/nightly.yml"
```

> **提示**：禁用工作流是临时性的，不会删除工作流定义文件。如需恢复，使用 `gh workflow enable`。

### 2.5 gh workflow run

手动触发一个工作流运行。这是 CI/CD 自动化中最常用的命令之一，支持向工作流传递输入参数。

**基本语法**：

```bash
gh workflow run [<workflow-id> | <workflow-name> | <filename>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--ref <string>` 或 `-r` | 指定运行工作流的分支或标签（默认当前分支） |
| `--field <key=value>` 或 `-F` | 传递工作流输入参数（`workflow_dispatch` 的 `inputs`） |
| `--field-file <key=path>` | 从文件读取输入参数的值 |
| `--json` | 从 stdin 读取 JSON 格式的输入参数 |

**示例**：

```bash
# 手动触发 CI 工作流（当前分支）
gh workflow run CI

# 在指定分支上触发
gh workflow run CI --ref main

# 传递输入参数（需工作流定义中声明了 workflow_dispatch inputs）
gh workflow run CI \
  --field environment=staging \
  --field debug=true

# 传递多个参数
gh workflow run "Deploy" \
  --ref main \
  --field environment=production \
  --field region=us-east-1 \
  --field version=2.1.0

# 从文件读取参数值
gh workflow run CI --field-file config=.github/deploy-config.json

# 触发带标签的工作流
gh workflow run CI --ref v2.0.0
```

#### 2.5.1 工作流输入参数详解

`gh workflow run` 的 `--field` / `-F` 参数对应工作流定义文件中 `workflow_dispatch` 事件的 `inputs` 字段。以下是一个典型的工作流定义示例：

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  workflow_dispatch:
    inputs:
      environment:
        description: '部署目标环境'
        required: true
        type: choice
        options:
          - staging
          - production
      region:
        description: '部署区域'
        required: false
        type: string
        default: 'us-east-1'
      version:
        description: '版本号'
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "Deploying version ${{ inputs.version }} to ${{ inputs.environment }} (${{ inputs.region }})"
```

对应的触发命令：

```bash
gh workflow run Deploy \
  --ref main \
  --field environment=production \
  --field region=ap-southeast-1 \
  --field version=2.3.0
```

#### 2.5.2 通过 JSON 传递复杂参数

对于复杂的输入参数结构，可以使用 `--json` 从 stdin 读取：

```bash
echo '{"environment":"production","region":"us-east-1","version":"2.3.0"}' | gh workflow run Deploy --json
```

## 3. gh run：运行追踪与管理

`gh run` 是 CI/CD 日常操作中最频繁使用的命令组，用于追踪工作流运行状态、查看日志、重试失败运行、下载产物等。

### 3.1 gh run list

列出仓库中最近的工作流运行记录，支持丰富的筛选条件。

**基本语法**：

```bash
gh run list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--limit <int>` 或 `-L` | 最大返回数量（默认 20） |
| `--status <string>` 或 `-s` | 按状态筛选：`queued`/`in_progress`/`completed`/`waiting`/`requested`/`cancelled`/`failure` |
| `--branch <string>` 或 `-b` | 按分支筛选 |
| `--event <string>` | 按触发事件筛选（`push`/`pull_request`/`schedule`/`workflow_dispatch` 等） |
| `--workflow <string>` 或 `-w` | 按工作流名称或 ID 筛选 |
| `--user <string>` 或 `-u` | 按触发用户筛选 |
| `--commit <sha>` 或 `-c` | 按提交 SHA 筛选 |
| `--created <date>` | 按创建日期筛选（支持 `>=YYYY-MM-DD` 格式） |
| `--json <fields>` | 以 JSON 格式输出 |
| `--jq <expression>` | 对 JSON 输出应用 jq 过滤器 |

**示例**：

```bash
# 列出最近的运行记录
gh run list

# 限制数量
gh run list --limit 10

# 查看失败的所有运行
gh run list --status failure

# 查看正在运行的
gh run list --status in_progress

# 按分支筛选
gh run list --branch main

# 按触发事件筛选
gh run list --event push
gh run list --event pull_request
gh run list --event workflow_dispatch

# 按工作流筛选
gh run list --workflow CI

# 按触发用户筛选
gh run list --user "@me"

# 组合筛选：main 分支上 CI 工作流最近 5 次失败的运行
gh run list --workflow CI --branch main --status failure --limit 5

# 按日期筛选（查看今天创建的运行）
gh run list --created ">=2026-07-24"

# JSON 输出
gh run list --limit 5 --json name,status,conclusion,headBranch,createdAt

# 结合 jq 提取关键信息
gh run list --limit 5 --json name,status,conclusion,headBranch \
  --jq '.[] | "\(.name) | \(.status) | \(.conclusion) | \(.headBranch)"'
```

### 3.2 gh run view

查看某个运行（Run）的详细信息，包括状态、触发者、关联提交、各 Job 的执行状态等。

**基本语法**：

```bash
gh run view [<run-id>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--web` 或 `-w` | 在浏览器中打开运行页面 |
| `--job <string>` 或 `-j` | 查看指定 Job 的详细信息 |
| `--log` | 查看运行的全部日志 |
| `--log-failed` | 仅查看失败的 Job 日志 |
| `--exit-status` | 运行结束后以运行结果作为退出码 |
| `--json <fields>` | 以 JSON 格式输出 |
| `--jq <expression>` | 对 JSON 输出应用 jq 过滤器 |

**示例**：

```bash
# 查看最近一次运行的详情（交互式选择）
gh run view

# 查看指定 Run ID 的详情
gh run view 1234567890

# 在浏览器中打开
gh run view 1234567890 --web

# 查看全部日志
gh run view 1234567890 --log

# 仅查看失败的 Job 日志
gh run view 1234567890 --log-failed

# 查看指定 Job 的详情
gh run view 1234567890 --job build

# 以退出码反映运行结果（适合 CI 脚本中做条件判断）
gh run view 1234567890 --exit-status && echo "运行成功" || echo "运行失败"

# JSON 输出
gh run view 1234567890 --json name,status,conclusion,jobs
```

### 3.3 gh run watch

实时监控运行状态，持续刷新输出直到运行完成。这是 CI/CD 工作流中最实用的交互式命令之一。

**基本语法**：

```bash
gh run watch <run-id> [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--exit-status` | 运行结束后以运行结果作为退出码 |
| `--interval <int>` 或 `-i` | 刷新间隔秒数（默认 3） |

**示例**：

```bash
# 监控指定运行
gh run watch 1234567890

# 监控并返回退出码
gh run watch 1234567890 --exit-status

# 自定义刷新间隔
gh run watch 1234567890 --interval 5
```

#### 3.3.1 交互模式说明

`gh run watch` 进入交互模式后，终端会持续刷新显示以下信息：

```
Refreshing run status every 3 seconds. Press Ctrl+C to quit.

✓ trunk  CI · main  CI #42
Triggered via push about 1 minute ago

JOBS
✓ build (20s)        https://github.com/owner/repo/actions/runs/1234567890/job/build
✓ test (35s)         https://github.com/owner/repo/actions/runs/1234567890/job/test
● deploy (in_progress)  https://github.com/owner/repo/actions/runs/1234567890/job/deploy

✓ Run CI (1234567890) completed with 'success'
```

交互模式下的状态图标含义：

| 图标 | 状态 | 含义 |
|------|------|------|
| ✓ | completed + success | Job 成功完成 |
| × | completed + failure | Job 执行失败 |
| ○ | completed + cancelled | Job 被取消 |
| ⊘ | completed + skipped | Job 被跳过 |
| ● | in_progress | Job 正在执行 |
| ◷ | queued | Job 排队等待 |
| ◌ | waiting | Job 等待依赖 |

按下 `Ctrl+C` 可随时退出交互模式，但不会取消运行本身。

### 3.4 gh run rerun

重新运行一个已完成或失败的运行。

**基本语法**：

```bash
gh run rerun [<run-id>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--failed` | 仅重新运行失败的 Job |
| `--debug` | 启用调试日志重新运行 |
| `--job <string>` 或 `-j` | 仅重新运行指定 Job |

**示例**：

```bash
# 重新运行整个 Workflow
gh run rerun 1234567890

# 仅重新运行失败的 Job
gh run rerun 1234567890 --failed

# 启用调试日志重新运行
gh run rerun 1234567890 --debug

# 仅重新运行指定 Job
gh run rerun 1234567890 --job test
```

> **提示**：`--failed` 是日常开发中最常用的选项——CI 中的某个 Job 因偶发性问题（如网络超时、测试不稳定）失败时，无需重新运行全部 Job。

### 3.5 gh run download

下载工作流运行产生的产物（Artifacts）。产物是工作流中通过 `actions/upload-artifact` 上传的文件。

**基本语法**：

```bash
gh run download [<run-id>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--name <string>` 或 `-n` | 下载指定名称的产物（不指定则下载全部） |
| `--dir <string>` 或 `-D` | 指定下载目录（默认当前目录） |
| `--pattern <glob>` 或 `-p` | 按 glob 模式匹配产物名称 |

**示例**：

```bash
# 下载最近一次运行的全部产物
gh run download

# 下载指定运行的全部产物
gh run download 1234567890

# 下载指定名称的产物到指定目录
gh run download 1234567890 --name "build-output" --dir ./artifacts

# 按模式匹配下载（如只下载名称包含 "coverage" 的产物）
gh run download 1234567890 --pattern "*coverage*"

# 下载到指定目录
gh run download 1234567890 --dir ./downloads

# 典型使用场景：下载构建产物用于本地验证
gh run download 1234567890 --name "dist" --dir ./local-build
```

#### 3.5.1 产物下载典型场景

```bash
# 场景1：CI 构建失败，下载构建产物排查问题
BUILD_RUN=$(gh run list --workflow CI --branch main --status failure --limit 1 --json databaseId --jq '.[0].databaseId')
gh run download "$BUILD_RUN" --name "build-logs" --dir ./debug

# 场景2：下载最新的 Release 构建产物
LATEST_RUN=$(gh run list --workflow Release --status success --limit 1 --json databaseId --jq '.[0].databaseId')
gh run download "$LATEST_RUN" --dir ./release-artifacts
```

### 3.6 gh run cancel

取消一个正在运行的 Workflow。

**基本语法**：

```bash
gh run cancel [<run-id>] [flags]
```

**示例**：

```bash
# 取消指定运行
gh run cancel 1234567890

# 取消最近一次运行（交互式选择）
gh run cancel
```

### 3.7 gh run delete

删除一个运行记录。

**基本语法**：

```bash
gh run delete [<run-id>] [flags]
```

**示例**：

```bash
# 删除指定运行记录
gh run delete 1234567890

# 删除最近一次运行记录（交互式选择）
gh run delete
```

> **警告**：删除运行记录是不可逆操作。删除后，运行的日志、产物和状态将永久丢失。建议在确认不再需要后执行。

## 4. gh cache：Actions 缓存管理

`gh cache` 用于管理 GitHub Actions 的缓存存储。缓存用于在工作流运行之间共享依赖项和构建输出，加速后续运行。

### 4.1 gh cache list

列出仓库的 Actions 缓存。

**基本语法**：

```bash
gh cache list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--limit <int>` 或 `-L` | 最大返回数量（默认 30） |
| `--sort <string>` | 排序方式：`created_at`/`last_accessed_at`/`size_in_bytes` |
| `--order <string>` | 排序方向：`asc`/`desc`（默认 `desc`） |
| `--key <string>` | 按缓存 key 筛选 |
| `--ref <string>` | 按 Git ref 筛选 |
| `--json <fields>` | 以 JSON 格式输出 |

**示例**：

```bash
# 列出所有缓存
gh cache list

# 限制数量
gh cache list --limit 10

# 按大小降序排列
gh cache list --sort size_in_bytes --order desc

# 按最近访问时间排序
gh cache list --sort last_accessed_at --order desc

# 按分支筛选
gh cache list --ref refs/heads/main

# JSON 输出
gh cache list --limit 5 --json key,sizeInBytes,lastAccessedAt
```

输出示例：

```
Showing 3 of 3 caches in owner/repo

Linux-node-modules-a1b2c3d4...  150 MB  refs/heads/main  2 days ago
Linux-pip-cache-e5f6g7h8...     80 MB   refs/heads/main  1 day ago
macOS-homebrew-i9j0k1l2...      200 MB  refs/heads/main  3 days ago
```

### 4.2 gh cache delete

删除指定的 Actions 缓存。

**基本语法**：

```bash
gh cache delete [<cache-id> | <cache-key>] [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--all` 或 `-a` | 删除所有缓存 |

**示例**：

```bash
# 按缓存 ID 删除
gh cache delete 123

# 按缓存 key 删除
gh cache delete Linux-node-modules-a1b2c3d4...

# 删除所有缓存（会弹出确认提示）
gh cache delete --all
```

> **提示**：GitHub Actions 缓存总量有 10 GB 上限（按仓库计），超出后旧缓存会被自动淘汰。定期清理不用的缓存可以释放存储空间，确保关键缓存不被提前淘汰。

## 5. gh secret：密钥管理

`gh secret` 用于管理 GitHub Actions 中使用的加密密钥（Secrets）。密钥在日志中自动遮蔽，适合存储 API Token、部署密钥、数据库密码等敏感信息。支持三个层级：仓库级、环境级、组织级。

### 5.1 gh secret list

列出指定层级的密钥。

**基本语法**：

```bash
gh secret list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--org <string>` 或 `-o` | 列出组织级密钥 |
| `--env <string>` 或 `-e` | 列出环境级密钥 |
| `--repo <string>` 或 `-R` | 指定仓库（默认当前目录仓库） |

**示例**：

```bash
# 列出当前仓库的密钥（仅显示名称，不显示值）
gh secret list

# 列出指定仓库的密钥
gh secret list --repo owner/repo

# 列出组织级密钥（需有组织管理员权限）
gh secret list --org my-org

# 列出指定环境的密钥
gh secret list --env production
```

### 5.2 gh secret set

设置或更新一个密钥。

**基本语法**：

```bash
gh secret set <secret-name> [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--body <string>` 或 `-b` | 密钥值（直接从命令行传入） |
| `--org <string>` 或 `-o` | 设置为组织级密钥 |
| `--env <string>` 或 `-e` | 设置为环境级密钥 |
| `--repo <string>` 或 `-R` | 指定仓库（默认当前目录仓库） |
| `--visibility <string>` 或 `-v` | 组织级密钥可见性：`all`/`private`/`selected` |
| `--repos <repos>` 或 `-r` | 当可见性为 `selected` 时，指定可访问的仓库列表（逗号分隔） |

**示例**：

```bash
# 设置仓库级密钥（从命令行传入值）
gh secret set NPM_TOKEN --body "npm_xxxxxxxxxxxxxxxx"

# 从 stdin 读取密钥值（推荐方式，避免密钥值出现在 shell 历史中）
echo "npm_xxxxxxxxxxxxxxxx" | gh secret set NPM_TOKEN

# 从文件读取密钥值
gh secret set DEPLOY_KEY < ./keys/deploy-key.pem

# 设置环境级密钥
gh secret set DATABASE_URL --env production --body "postgresql://user:pass@host:5432/db"

# 设置组织级密钥（对所有仓库可见）
gh secret set DOCKER_HUB_TOKEN --org my-org --visibility all --body "dckr_pat_xxxx"

# 设置组织级密钥（仅对指定仓库可见）
gh secret set AWS_ACCESS_KEY --org my-org --visibility selected \
  --repos "repo-a,repo-b,repo-c" \
  --body "AKIAIOSFODNN7EXAMPLE"

# 更新已有密钥
gh secret set NPM_TOKEN --body "npm_new_token_value"
```

> **安全提示**：强烈建议通过 stdin 或文件方式传入密钥值，避免在命令行中直接暴露敏感信息。`--body` 参数接受的值会出现在 shell 历史记录中，不建议在生产环境中使用。

### 5.3 gh secret remove

删除一个密钥。

**基本语法**：

```bash
gh secret remove <secret-name> [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--org <string>` 或 `-o` | 删除组织级密钥 |
| `--env <string>` 或 `-e` | 删除环境级密钥 |
| `--repo <string>` 或 `-R` | 指定仓库（默认当前目录仓库） |

**示例**：

```bash
# 删除仓库级密钥
gh secret remove NPM_TOKEN

# 删除环境级密钥
gh secret remove DATABASE_URL --env staging

# 删除组织级密钥
gh secret remove OLD_DEPLOY_KEY --org my-org

# 删除指定仓库的密钥
gh secret remove NPM_TOKEN --repo owner/repo
```

## 6. gh variable：变量管理

`gh variable` 用于管理 GitHub Actions 中使用的非敏感配置变量（Variables）。与 Secrets 不同，变量的值在日志中不会被遮蔽，适合存储非敏感配置如环境名称、功能开关、版本号等。同样支持仓库级、环境级、组织级三个层级。

### 6.1 gh variable list

列出指定层级的变量。

**基本语法**：

```bash
gh variable list [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--org <string>` 或 `-o` | 列出组织级变量 |
| `--env <string>` 或 `-e` | 列出环境级变量 |
| `--repo <string>` 或 `-R` | 指定仓库（默认当前目录仓库） |

**示例**：

```bash
# 列出当前仓库的变量
gh variable list

# 列出指定仓库的变量
gh variable list --repo owner/repo

# 列出组织级变量
gh variable list --org my-org

# 列出指定环境的变量
gh variable list --env production
```

### 6.2 gh variable set

设置或更新一个变量。

**基本语法**：

```bash
gh variable set <variable-name> [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--body <string>` 或 `-b` | 变量值 |
| `--org <string>` 或 `-o` | 设置为组织级变量 |
| `--env <string>` 或 `-e` | 设置为环境级变量 |
| `--repo <string>` 或 `-R` | 指定仓库（默认当前目录仓库） |
| `--visibility <string>` 或 `-v` | 组织级变量可见性：`all`/`private`/`selected` |
| `--repos <repos>` 或 `-r` | 当可见性为 `selected` 时，指定可访问的仓库列表（逗号分隔） |

**示例**：

```bash
# 设置仓库级变量
gh variable set DEPLOY_ENV --body "staging"

# 设置环境级变量
gh variable set API_BASE_URL --env production --body "https://api.example.com"

# 设置组织级变量（对所有仓库可见）
gh variable set NODE_VERSION --org my-org --visibility all --body "20"

# 设置组织级变量（仅对指定仓库可见）
gh variable set REGISTRY_URL --org my-org --visibility selected \
  --repos "frontend,backend" \
  --body "registry.example.com"

# 更新已有变量
gh variable set DEPLOY_ENV --body "production"
```

### 6.3 gh variable remove

删除一个变量。

**基本语法**：

```bash
gh variable remove <variable-name> [flags]
```

**常用参数**：

| 参数 | 说明 |
|------|------|
| `--org <string>` 或 `-o` | 删除组织级变量 |
| `--env <string>` 或 `-e` | 删除环境级变量 |
| `--repo <string>` 或 `-R` | 指定仓库（默认当前目录仓库） |

**示例**：

```bash
# 删除仓库级变量
gh variable remove DEPLOY_ENV

# 删除环境级变量
gh variable remove API_BASE_URL --env staging

# 删除组织级变量
gh variable remove OLD_CONFIG --org my-org

# 删除指定仓库的变量
gh variable remove DEPLOY_ENV --repo owner/repo
```

## 7. Secret 与 Variable 的对比

| 特性 | Secret（密钥） | Variable（变量） |
|------|---------------|-----------------|
| 日志遮蔽 | ✅ 自动遮蔽 | ❌ 不遮蔽 |
| 适用场景 | API Token、密码、私钥、证书 | 环境名称、版本号、功能开关、URL |
| 访问级别 | 仓库/环境/组织 | 仓库/环境/组织 |
| 值可见性 | 设置后不可查看（仅可更新/删除） | 设置后可在 Web UI 查看 |
| 在 Workflow 中的引用 | `${{ secrets.NAME }}` | `${{ vars.NAME }}` |

## 8. CI/CD 工作流集成模式

以下介绍几种常见的 CI/CD 工作流集成模式，展示 `gh` 命令在实际自动化场景中的组合使用方式。

### 8.1 模式一：手动触发部署

适用于需要人工确认的部署流程，通过 `gh workflow run` 触发部署工作流，再通过 `gh run watch` 追踪执行状态。

```bash
#!/bin/bash
# deploy.sh — 手动触发并监控部署

ENVIRONMENT="${1:-staging}"
VERSION="${2:-latest}"

echo "🚀 触发部署到 ${ENVIRONMENT}..."

# 触发部署工作流
gh workflow run Deploy \
  --ref main \
  --field environment="${ENVIRONMENT}" \
  --field version="${VERSION}"

# 等待工作流启动（给 GitHub 一些时间创建 Run）
sleep 5

# 获取最新运行的 ID
RUN_ID=$(gh run list --workflow Deploy --limit 1 --json databaseId --jq '.[0].databaseId')

echo "📡 监控运行 #${RUN_ID}..."
gh run watch "${RUN_ID}" --exit-status

if [ $? -eq 0 ]; then
  echo "✅ 部署成功"
else
  echo "❌ 部署失败，请查看日志"
  gh run view "${RUN_ID}" --log-failed
  exit 1
fi
```

### 8.2 模式二：CI 失败自动重试

当 CI 运行因偶发性问题失败时，自动重试失败的 Job。

```bash
#!/bin/bash
# retry-failed-ci.sh — 自动重试失败的 CI Job

WORKFLOW_NAME="CI"
BRANCH="main"

# 获取最近一次失败的运行
FAILED_RUN=$(gh run list \
  --workflow "${WORKFLOW_NAME}" \
  --branch "${BRANCH}" \
  --status failure \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')

if [ -z "${FAILED_RUN}" ]; then
  echo "✅ 没有失败的运行记录"
  exit 0
fi

echo "🔄 发现失败的运行 #${FAILED_RUN}，正在重试失败的 Job..."

# 仅重试失败的 Job
gh run rerun "${FAILED_RUN}" --failed

# 等待新运行启动
sleep 5

# 获取新运行的 ID
NEW_RUN=$(gh run list --workflow "${WORKFLOW_NAME}" --branch "${BRANCH}" --status in_progress --limit 1 --json databaseId --jq '.[0].databaseId')

echo "📡 监控重试运行 #${NEW_RUN}..."
gh run watch "${NEW_RUN}" --exit-status
```

### 8.3 模式三：PR 合并前健康检查

在合并 PR 之前，确保所有 CI 检查通过。结合 [PR 工作流指南](03-pr-workflow.md) 中的 `gh pr checks` 命令。

```bash
#!/bin/bash
# pre-merge-check.sh — PR 合并前健康检查

PR_NUMBER=$1

if [ -z "${PR_NUMBER}" ]; then
  echo "用法: $0 <PR_NUMBER>"
  exit 1
fi

echo "🔍 检查 PR #${PR_NUMBER} 的 CI 状态..."

# 查看 CI 检查状态
gh pr checks "${PR_NUMBER}"

# 等待所有检查完成（如果还在运行中）
gh pr checks "${PR_NUMBER}" --watch

# 检查是否全部通过
if gh pr checks "${PR_NUMBER}" --json state --jq '.[].state' | grep -q "FAILURE"; then
  echo "❌ CI 检查失败，无法合并"
  
  # 获取失败 Job 的日志
  echo "📋 失败日志："
  gh run list --workflow CI --branch "$(gh pr view "${PR_NUMBER}" --json headRefName --jq '.headRefName')" --status failure --limit 1 --json databaseId --jq '.[0].databaseId' | xargs -I {} gh run view {} --log-failed
  
  exit 1
fi

echo "✅ 所有 CI 检查通过，可以合并"
```

### 8.4 模式四：多环境密钥同步

在多个环境之间同步密钥配置，确保各环境配置一致性。

```bash
#!/bin/bash
# sync-secrets.sh — 多环境密钥同步

SECRET_NAME=$1
SECRET_VALUE=$2

if [ -z "${SECRET_NAME}" ] || [ -z "${SECRET_VALUE}" ]; then
  echo "用法: $0 <SECRET_NAME> <SECRET_VALUE>"
  echo "密钥值从 stdin 或文件读取更安全"
  exit 1
fi

# 同步到多个环境
for ENV in development staging production; do
  echo "🔐 设置 ${SECRET_NAME} 到 ${ENV} 环境..."
  echo "${SECRET_VALUE}" | gh secret set "${SECRET_NAME}" --env "${ENV}"
done

echo "✅ 密钥 ${SECRET_NAME} 已同步到所有环境"
```

### 8.5 模式五：构建产物下载与本地验证

下载 CI 构建产物，在本地进行验证或测试。

```bash
#!/bin/bash
# verify-build.sh — 下载并验证构建产物

WORKFLOW_NAME="Build"
BRANCH="main"

# 获取最近一次成功的构建运行
BUILD_RUN=$(gh run list \
  --workflow "${WORKFLOW_NAME}" \
  --branch "${BRANCH}" \
  --status success \
  --limit 1 \
  --json databaseId \
  --jq '.[0].databaseId')

if [ -z "${BUILD_RUN}" ]; then
  echo "❌ 没有找到成功的构建运行"
  exit 1
fi

echo "📥 下载构建产物 #${BUILD_RUN}..."

# 下载产物
mkdir -p ./verify-build
gh run download "${BUILD_RUN}" --dir ./verify-build

echo "📦 产物列表："
ls -la ./verify-build/

# 运行本地验证
echo "🔍 运行本地验证..."
# 此处添加你的验证逻辑，例如：
# tar -xzf ./verify-build/dist.tar.gz -C ./verify-build/extracted
# npm test -- --verify-build ./verify-build/extracted

echo "✅ 验证完成"
```

### 8.6 模式六：缓存清理自动化

定期清理 Actions 缓存，避免超出存储上限。

```bash
#!/bin/bash
# clean-cache.sh — 清理过期缓存

# 设置缓存的保留天数
RETENTION_DAYS=7
CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d)

echo "🧹 清理 ${CUTOFF_DATE} 之前的 Actions 缓存..."

# 获取过期缓存列表
OLD_CACHES=$(gh cache list \
  --limit 100 \
  --sort last_accessed_at \
  --order asc \
  --json id,key,lastAccessedAt \
  --jq ".[] | select(.lastAccessedAt < \"${CUTOFF_DATE}\") | .id")

if [ -z "${OLD_CACHES}" ]; then
  echo "✅ 没有需要清理的过期缓存"
  exit 0
fi

for CACHE_ID in ${OLD_CACHES}; do
  echo "🗑️ 删除缓存 #${CACHE_ID}..."
  gh cache delete "${CACHE_ID}"
done

echo "✅ 缓存清理完成"
```

### 8.7 模式七：跨仓库 CI 状态聚合

聚合多个仓库的 CI 状态，生成统一的健康报告。

```bash
#!/bin/bash
# ci-status-report.sh — 多仓库 CI 状态聚合报告

REPOS=("owner/repo-a" "owner/repo-b" "owner/repo-c")
BRANCH="main"

echo "📊 CI 状态聚合报告"
echo "========================="
printf "%-20s %-15s %-15s\n" "仓库" "状态" "最近运行"
echo "----------------------------------------------------"

for REPO in "${REPOS[@]}"; do
  STATUS=$(gh run list \
    --repo "${REPO}" \
    --branch "${BRANCH}" \
    --limit 1 \
    --json conclusion,createdAt \
    --jq '.[0] | "\(.conclusion) \(.createdAt)"')

  CONCLUSION=$(echo "${STATUS}" | awk '{print $1}')
  CREATED=$(echo "${STATUS}" | awk '{print $2}')

  case "${CONCLUSION}" in
    success)  ICON="✅";;
    failure)  ICON="❌";;
    null)     ICON="🔄";;
    *)        ICON="❓";;
  esac

  printf "%-20s %-15s %-15s\n" "${REPO}" "${ICON} ${CONCLUSION}" "${CREATED}"
done
```

## 9. 相关资源

- [安装与配置指南](01-installation.md) — 安装 `gh` 并完成认证
- [基础命令](02-basic-commands.md) — 仓库和 Issue 的日常操作
- [PR 工作流指南](03-pr-workflow.md) — Pull Request 的完整生命周期管理
- [GitHub CLI 官方文档 - gh workflow](https://cli.github.com/manual/gh_workflow) — 工作流管理完整命令参考
- [GitHub CLI 官方文档 - gh run](https://cli.github.com/manual/gh_run) — 运行追踪完整命令参考
- [GitHub CLI 官方文档 - gh cache](https://cli.github.com/manual/gh_cache) — 缓存管理完整命令参考
- [GitHub CLI 官方文档 - gh secret](https://cli.github.com/manual/gh_secret) — 密钥管理完整命令参考
- [GitHub CLI 官方文档 - gh variable](https://cli.github.com/manual/gh_variable) — 变量管理完整命令参考
- [GitHub Actions 官方文档](https://docs.github.com/en/actions) — Actions 概念、语法与最佳实践
- [GitHub Actions - 加密密钥](https://docs.github.com/en/actions/security-guides/encrypted-secrets) — Secrets 安全指南
- [GitHub Actions - 变量](https://docs.github.com/en/actions/learn-github-actions/variables) — Variables 使用指南
- [GitHub Actions - 缓存依赖项](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows) — 缓存最佳实践