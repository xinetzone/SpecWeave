---
id: github-cli-wiki-03-pr-workflow
title: "Pull Request 工作流指南"
source: "https://cli.github.com/manual/gh_pr"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "pull-request", "pr", "code-review", "workflow", "collaboration"]
---

# Pull Request 工作流指南

本章介绍使用 `gh` 命令行工具完成 Pull Request（PR）的完整生命周期管理：从创建、审查、合并到关闭，以及 Fork 工作流等进阶场景。

GitHub CLI 的 PR 相关命令均以 `gh pr` 为入口，支持所有主流 PR 操作。在开始之前，请确保已完成 [安装与配置](01-installation.md) 中的认证步骤。

## 1. 快速参考

下表汇总了 `gh pr` 各子命令的核心用途：

| 子命令 | 用途 | 常用场景 |
|--------|------|----------|
| `gh pr create` | 创建 Pull Request | 推送分支后创建 PR |
| `gh pr checkout` | 检出 PR 到本地 | 审查他人代码 |
| `gh pr review` | 提交审查意见 | 批准/评论/请求修改 |
| `gh pr merge` | 合并 PR | 审查通过后合入目标分支 |
| `gh pr status` | 查看当前 PR 状态 | 了解审查进度 |
| `gh pr checks` | 查看 CI 检查状态 | 确认所有检查通过 |
| `gh pr diff` | 查看 PR 变更差异 | 代码审查 |
| `gh pr view` | 查看 PR 详细信息 | 快速了解 PR 内容 |
| `gh pr list` | 列出 PR 列表 | 批量查看/筛选 PR |
| `gh pr close` | 关闭 PR（不合并） | 放弃或替代 PR |
| `gh pr reopen` | 重新打开已关闭的 PR | 恢复被关闭的 PR |
| `gh pr comment` | 在 PR 上添加评论 | 讨论/反馈 |
| `gh pr ready` | 将草稿 PR 标记为就绪 | 取消 Draft 状态 |

## 2. 创建 Pull Request

`gh pr create` 是 PR 工作流的起点，提供丰富的参数来定制 PR 的元数据。

### 2.1 基本创建

最简单的用法——在已推送的分支上执行，`gh` 自动使用当前分支的提交信息填充 PR 标题和描述：

```bash
git checkout -b feature/my-awesome-change
git push -u origin feature/my-awesome-change
gh pr create
```

### 2.2 指定标题和描述

使用 `--title` 和 `--body` 参数直接指定 PR 标题和描述：

```bash
gh pr create --title "feat: 添加用户认证模块" --body "## 变更说明

- 实现 JWT Token 认证流程
- 新增登录/登出 API
- 添加中间件鉴权拦截器

Closes #42"
```

### 2.3 在 Web 浏览器中创建

`--web` 参数在浏览器中打开 GitHub 的 PR 创建页面，适合需要复杂操作（如拖拽添加 Reviewer）的场景：

```bash
gh pr create --web
```

### 2.4 自动填充 PR 描述

`--fill` 和 `--fill-verbose` 让 `gh` 根据提交信息自动填充 PR 标题和描述：

```bash
# 使用宽松模式，优先使用单个提交的标题/描述
gh pr create --fill

# 使用详细模式，引入所有提交信息
gh pr create --fill-verbose
```

| 参数 | 行为 |
|------|------|
| `--fill` | 使用第一个提交的标题和描述，不添加额外注释 |
| `--fill-verbose` | 使用所有提交的标题和描述，并添加脚注标明来自命令行 |

### 2.5 创建草稿 PR

`--draft` 将 PR 创建为草稿（Draft）状态，适合"先占坑、后完善"的协作方式：

```bash
gh pr create --title "WIP: 重构数据访问层" --body "仍在开发中，欢迎提前反馈架构设计" --draft
```

草稿 PR 创建后，使用 `gh pr ready` 将其标记为正式 PR（见 [第 12 节](#12-将草稿标记为就绪)）。

### 2.6 指定源分支和目标分支

```bash
# --head 指定源分支（当前分支为默认值）
# --base 指定目标分支（仓库默认分支为默认值）
gh pr create --title "hotfix: 修复登录超时" --base main --head hotfix/login-timeout
```

### 2.7 指定 Reviewer 和 Assignee

```bash
gh pr create \
  --title "feat: 新增导出报表功能" \
  --body "支持导出 CSV 和 PDF 格式" \
  --reviewer "alice,bob" \
  --assignee "charlie"
```

> **注意**：`--reviewer` 和 `--assignee` 接受 GitHub 用户名（`@` 前缀可省略），多个用户用逗号分隔。

### 2.8 添加 Label 和 Milestone

```bash
gh pr create \
  --title "fix: 修复分页查询边界条件" \
  --label "bug,high-priority" \
  --milestone "v2.1.0"
```

### 2.9 关联 Project

`--project` 将 PR 关联到 GitHub Projects 看板：

```bash
gh pr create --title "feat: 暗黑模式支持" --project "Q3 功能迭代"
```

### 2.10 使用 PR 模板

`--template` 指定仓库中已有的 PR 模板：

```bash
gh pr create --title "docs: 更新 API 文档" --template "docs_change.md"
```

PR 模板文件需存放在仓库的 `.github/PULL_REQUEST_TEMPLATE/` 目录下，或使用单一模板文件 `.github/pull_request_template.md`。

### 2.11 从文件读取描述

`--body-file` 从文件读取 PR 描述内容：

```bash
# 将描述内容写入文件
cat > pr-body.md << 'EOF'
## 变更摘要
- 重构用户服务层
- 新增单元测试覆盖

## 测试说明
1. 运行 `npm test`
2. 验证所有 128 个测试通过
EOF

# 创建 PR
gh pr create --title "refactor: 重构用户服务层" --body-file pr-body.md
```

### 2.12 使用编辑器编写描述

`--editor` 打开配置的默认编辑器（通过 `gh config set editor` 设置）来编写 PR 描述：

```bash
gh pr create --title "feat: 多语言国际化支持" --editor
```

### 2.13 禁止维护者编辑

`--no-maintainer-edit` 禁止目标仓库的维护者修改你的 PR 分支：

```bash
gh pr create --title "feat: 新增自定义主题" --no-maintainer-edit
```

对于 Fork 仓库的 PR，此选项特别有用——当你不希望上游维护者向你的分支推送额外提交时。

### 2.14 恢复草稿 PR

`--recover` 恢复之前中断的 PR 创建流程。如果创建 PR 时编辑器崩溃或终端意外关闭，可以使用此参数恢复：

```bash
gh pr create --recover
```

`gh` 将读取上次保存的 PR 草稿数据，重新打开编辑器让你继续编辑。

## 3. 检出 Pull Request

`gh pr checkout` 将远程 PR 检出到本地，方便你在本地环境中审查和测试代码。

### 3.1 按 PR 编号检出

```bash
# 检出 PR #42
gh pr checkout 42
```

执行后，`gh` 自动执行以下操作：
1. 从远程仓库获取 PR 对应的分支
2. 创建本地跟踪分支
3. 切换到该分支

```bash
# 如果当前不在 PR 所在的仓库目录中，需要指定仓库
gh pr checkout 42 --repo owner/repo
```

### 3.2 按分支名检出

如果知道 PR 对应的源分支名称，可以直接检出：

```bash
gh pr checkout feature/my-awesome-change
```

当分支名在多个 PR 中冲突时，`gh` 会提示你选择具体的 PR。

## 4. 审查 Pull Request

`gh pr review` 用于提交代码审查意见，支持三种审查结论和附带评论。

### 4.1 批准 PR

```bash
gh pr review 42 --approve
```

或附带评论一并批准：

```bash
gh pr review 42 --approve --body "代码结构清晰，测试覆盖完整，LGTM!"
```

### 4.2 仅评论

```bash
gh pr review 42 --comment --body "建议在 `UserService` 中增加空值检查，避免 NPE。"
```

### 4.3 请求修改

```bash
gh pr review 42 --request-changes --body "## 需要修改的问题

1. `auth.ts` 第 42 行：Token 过期时间应设为配置项而非硬编码
2. 缺少错误处理中间件的集成测试
3. 补充 API 文档中对新增错误码的说明"
```

### 4.4 审查结论对照

| 参数 | 含义 | 对 PR 的影响 |
|------|------|-------------|
| `--approve` | 批准合并 | PR 满足合并条件 |
| `--comment` | 仅评论（不做结论） | 不改变 PR 状态 |
| `--request-changes` | 请求修改 | 阻止 PR 合并，直到作者解决 |

> **注意**：`--comment`、`--approve`、`--request-changes` 三者互斥，每次审查只能选择一种结论。

## 5. 合并 Pull Request

`gh pr merge` 将 PR 合并到目标分支，支持三种合并策略。

### 5.1 合并策略

```bash
# 创建合并提交（默认策略）
gh pr merge 42 --merge

# 压缩合并（将所有提交合并为一个）
gh pr merge 42 --squash

# 变基合并（将提交变基到目标分支顶端）
gh pr merge 42 --rebase
```

| 策略 | 参数 | 效果 | 适用场景 |
|------|------|------|----------|
| 合并提交 | `--merge` | 保留所有提交历史，生成一个合并提交 | 多人协作的特性分支，需要保留完整历史 |
| 压缩合并 | `--squash` | 所有提交压缩为一个，保留清晰的线性历史 | 单人或小特性分支，提交粒度较细 |
| 变基合并 | `--rebase` | 将提交变基到目标分支顶端，不产生合并提交 | 追求完全线性历史的项目 |

### 5.2 自动合并

`--auto` 启用自动合并——当所有必需的 CI 检查通过后自动合并：

```bash
gh pr merge 42 --auto --squash
```

输出示例：

```
✓ Automatically merging when all checks pass
```

当所有分支保护规则要求的检查通过后，PR 会自动合并。如果任何检查失败，自动合并将被取消。

### 5.3 删除源分支

`--delete-branch` 在合并后自动删除源分支（本地和远程）：

```bash
gh pr merge 42 --squash --delete-branch
```

此操作等同于：
1. 执行合并
2. 删除远程分支 `git push origin --delete feature/my-branch`
3. 删除本地分支 `git branch -d feature/my-branch`

## 6. 查看 PR 状态

`gh pr status` 提供当前工作区 PR 的概览信息。

### 6.1 基本用法

```bash
gh pr status
```

输出示例：

```
Current branch
  There is no pull request associated with [feature/new-dashboard]

Created by you
  #51  feat: 新增用户仪表盘面板 [feature/user-dashboard]
  #48  fix: 修复侧边栏折叠动画抖动 [fix/sidebar-animation]

Requesting a code review from you
  #53  refactor: 重构数据查询引擎 [refactor/query-engine] (alice)
  #52  docs: 更新贡献指南 [docs/contributing] (bob)
```

### 6.2 输出解读

| 区块 | 含义 |
|------|------|
| `Current branch` | 当前分支关联的 PR（如果有）。若无关联，显示提示信息 |
| `Created by you` | 你创建的所有打开状态的 PR |
| `Requesting a code review from you` | 等待你审查的 PR（Reviewer 包含你） |

最后一个区块尤其重要——它帮助你快速定位需要你投入审查时间的 PR。

## 7. 查看 CI 检查状态

`gh pr checks` 显示 PR 的 CI 检查运行状态。

### 7.1 基本用法

```bash
gh pr checks 42
```

输出示例：

```
All checks were successful
  1/1 checks passed

  ✓  build-and-test (3m 24s)  https://github.com/owner/repo/actions/runs/123456
```

失败时的输出：

```
Some checks were not successful
  0/1 checks passed

  ×  build-and-test (2m 11s)  https://github.com/owner/repo/actions/runs/123456
  
  ANNOTATIONS
  -----------
  build-and-test
  src/services/auth.ts#L42: Type 'null' is not assignable to type 'string'
```

### 7.2 实时等待检查完成

`--watch` 参数持续监控检查状态，直到所有检查完成：

```bash
gh pr checks 42 --watch
```

此命令会持续刷新输出，直到所有检查通过或失败。适合在 `gh pr merge --auto` 之前确认所有检查是否就绪。

```bash
# 典型工作流：先确认检查通过，再启用自动合并
gh pr checks 42 --watch && gh pr merge 42 --auto --squash
```

## 8. 查看 PR 变更差异

`gh pr diff` 显示 PR 的代码变更差异，支持多种输出格式。

### 8.1 基本用法

```bash
gh pr diff 42
```

输出与 `git diff` 类似的 unified diff 格式。

### 8.2 彩色输出

`--color` 启用彩色差异输出（默认行为取决于终端支持）：

```bash
gh pr diff 42 --color always
```

可选值：`always`、`never`、`auto`。

### 8.3 补丁格式

`--patch` 强制显示补丁格式的差异（默认行为，可与其他参数组合）：

```bash
gh pr diff 42 --patch
```

### 8.4 仅显示文件名

`--name-only` 仅列出变更的文件名，不显示具体差异内容：

```bash
gh pr diff 42 --name-only
```

输出示例：

```
src/components/Dashboard.tsx
src/services/auth.ts
tests/unit/auth.test.ts
docs/CHANGELOG.md
```

此模式适合快速了解 PR 的变更范围，再决定是否深入审查具体差异。

## 9. 查看 PR 详情

`gh pr view` 显示 PR 的详细信息，支持多种输出格式。

### 9.1 基本用法

```bash
gh pr view 42
```

输出示例：

```
feat: 添加用户认证模块
nobody closed this in 2 minutes
label: feature, backend

## 变更说明

- 实现 JWT Token 认证流程
- 新增登录/登出 API
- 添加中间件鉴权拦截器

View this PR on GitHub: https://github.com/owner/repo/pull/42
```

### 9.2 在浏览器中查看

```bash
gh pr view 42 --web
```

直接在浏览器中打开 PR 页面。

### 9.3 查看评论

`--comments` 在输出中显示 PR 的所有评论（审查意见和普通评论）：

```bash
gh pr view 42 --comments
```

### 9.4 JSON 格式输出

`--json` 以 JSON 格式输出 PR 数据，适合脚本处理和自动化：

```bash
# 查看基本信息
gh pr view 42 --json title,state,author,createdAt,url

# 查看所有可用字段
gh pr view 42 --json title,number,state,author,labels,assignees,reviews,mergeable,createdAt,updatedAt,closedAt,mergedAt,body,url
```

输出示例：

```json
{
  "title": "feat: 添加用户认证模块",
  "number": 42,
  "state": "OPEN",
  "author": {
    "login": "octocat"
  },
  "url": "https://github.com/owner/repo/pull/42"
}
```

## 10. 列出 PR 列表

`gh pr list` 列出仓库中的 PR，支持丰富的筛选和格式化选项。

### 10.1 基本用法

```bash
gh pr list
```

输出示例：

```
#42  feat: 添加用户认证模块     feature/user-auth     about 2 hours ago
#41  fix: 修复分页边界条件       fix/pagination        about 1 day ago
#40  docs: 更新 API 文档         docs/api-update       about 3 days ago
```

### 10.2 按状态筛选

`--state` 按 PR 状态筛选：

```bash
# 查看所有打开的 PR（默认）
gh pr list --state open

# 查看已关闭的 PR（含已合并和未合并关闭）
gh pr list --state closed

# 查看已合并的 PR
gh pr list --state merged

# 查看所有状态的 PR
gh pr list --state all
```

### 10.3 按 Label 筛选

```bash
# 查看标记为 bug 的 PR
gh pr list --label bug

# 多个标签（AND 逻辑，PR 必须同时具有所有指定标签）
gh pr list --label "bug,high-priority"
```

### 10.4 按 Assignee 筛选

```bash
gh pr list --assignee alice

# 查看分配给自己的 PR（使用 @me 快捷方式）
gh pr list --assignee "@me"
```

### 10.5 按作者筛选

```bash
# 查看自己创建的 PR
gh pr list --author "@me"

# 查看指定用户创建的 PR
gh pr list --author alice
```

### 10.6 按分支筛选

```bash
# 查看指定目标分支的 PR
gh pr list --base main

# 查看指定源分支的 PR
gh pr list --head feature/new-dashboard
```

### 10.7 全文搜索

`--search` 支持 GitHub 的 PR 搜索语法，按标题、描述、标签等进行全文匹配：

```bash
# 搜索标题或描述中包含 "authentication" 的 PR
gh pr list --search "authentication"

# 搜索特定标签的 PR
gh pr list --search "label:bug"

# 组合搜索（搜索特定状态和标签）
gh pr list --search "is:open label:bug"
```

### 10.8 限制返回数量

`--limit` 限制返回的 PR 数量：

```bash
# 只显示最近 5 个 PR
gh pr list --limit 5
```

### 10.9 JSON 格式输出

`--json` 以 JSON 格式导出 PR 列表，适合脚本处理和自动化分析：

```bash
# 导出基本字段
gh pr list --json title,number,state,author,createdAt

# 导出所有可用字段
gh pr list --json title,number,state,author,labels,assignees,createdAt,updatedAt,url
```

输出示例：

```json
[
  {
    "title": "feat: 添加用户认证模块",
    "number": 42,
    "state": "OPEN",
    "author": {"login": "octocat"},
    "createdAt": "2026-07-23T10:30:00Z"
  },
  {
    "title": "fix: 修复分页边界条件",
    "number": 41,
    "state": "OPEN",
    "author": {"login": "alice"},
    "createdAt": "2026-07-22T15:20:00Z"
  }
]
```

## 11. 关闭与重新打开 PR

### 11.1 关闭 PR

`gh pr close` 关闭 PR 而不合并。适用于以下场景：
- 方向调整，需要用新 PR 替代
- 不再需要该变更
- 发现严重问题，需要重新设计

```bash
gh pr close 42
```

关闭时附上说明：

```bash
gh pr close 42 --comment "此 PR 被 #56 替代，新 PR 采用了更简洁的实现方案。"
```

> **注意**：关闭 PR 不等同于拒绝。关闭的 PR 可以随时用 `gh pr reopen` 重新打开。

### 11.2 重新打开 PR

```bash
gh pr reopen 42
```

重新打开时附上说明：

```bash
gh pr reopen 42 --comment "已修复 CI 失败问题，请重新审查。"
```

## 12. 将草稿标记为就绪

`gh pr ready` 将草稿（Draft）PR 转换为正式 PR，通知 Reviewer 可以开始审查：

```bash
gh pr ready 42
```

草稿 PR 创建于 `gh pr create --draft`（见 [第 2.5 节](#25-创建草稿-pr)）。标记为就绪后：
- Reviewer 在 `gh pr status` 的审查列表中可以看到该 PR
- 仓库的自动通知机制会提醒 Reviewer
- 分支保护规则开始生效

## 13. 添加 PR 评论

`gh pr comment` 在 PR 上添加普通评论（区别于审查意见）。

### 13.1 基本用法

```bash
gh pr comment 42 --body "这个实现思路不错，但建议把 `TokenManager` 单例改为依赖注入，方便单元测试。"
```

### 13.2 从文件读取评论

```bash
gh pr comment 42 --body-file review-notes.md
```

### 13.3 使用编辑器编写

```bash
gh pr comment 42 --editor
```

## 14. 完整 PR 工作流示例

以下是一个从创建到合并的完整 PR 工作流，展示 `gh pr` 各子命令在实际协作中的使用方式。

### 14.1 场景设定

- **仓库**：`owner/myapp`
- **目标分支**：`main`
- **功能**：新增用户仪表盘面板
- **协作者**：开发者 `charlie`，审查者 `alice`

### 14.2 步骤 1：创建特性分支并推送

```bash
git checkout -b feature/user-dashboard
# 编写代码...
git add .
git commit -m "feat: 新增用户仪表盘面板

- 实现仪表盘布局组件
- 添加数据统计卡片
- 集成图表可视化
- 编写单元测试"
git push -u origin feature/user-dashboard
```

### 14.3 步骤 2：创建 PR

```bash
gh pr create \
  --title "feat: 新增用户仪表盘面板" \
  --body "## 变更说明

- 实现仪表盘布局组件 `DashboardLayout`
- 添加数据统计卡片组件 `StatsCard`
- 集成 ECharts 图表可视化
- 单元测试覆盖核心组件

## 截图

![仪表盘预览](https://example.com/dashboard-preview.png)

Closes #38" \
  --base main \
  --reviewer "alice" \
  --assignee "charlie" \
  --label "feature,frontend" \
  --milestone "v2.2.0"
```

输出示例：

```
https://github.com/owner/myapp/pull/42
```

### 14.4 步骤 3：查看 CI 检查状态

```bash
gh pr checks 42 --watch
```

### 14.5 步骤 4（审查者 `alice`）：检出 PR 到本地审查

```bash
# Alice 检出 PR 到本地进行测试
gh pr checkout 42

# 查看变更差异
gh pr diff 42 --name-only

# 在本地运行测试
npm test
```

### 14.6 步骤 5（审查者 `alice`）：提交审查意见

审查通过，附带评论：

```bash
gh pr review 42 --approve --body "代码质量很高，测试覆盖完整。建议在 `StatsCard` 中添加 loading 状态处理，但可以在后续 PR 中优化。"
```

如果有需要修改的问题：

```bash
gh pr review 42 --request-changes --body "## 需要修改

1. `DashboardLayout.tsx` 缺少响应式断点处理
2. 图表组件的数据加载缺少错误边界
3. 补充 `StatsCard` 的空数据状态展示"
```

### 14.7 步骤 6（开发者 `charlie`）：响应审查意见

```bash
# 在 PR 上添加评论回复
gh pr comment 42 --body "已修复所有问题，新增了响应式布局和错误边界处理，请重新审查。"

# 推送修复提交
git add .
git commit -m "fix: 添加响应式布局和错误边界"
git push
```

### 14.8 步骤 7：确认审查通过后合并

```bash
# 确认所有检查通过
gh pr checks 42

# 压缩合并并删除源分支
gh pr merge 42 --squash --delete-branch
```

输出示例：

```
✓ Squashed and merged PR #42
✓ Deleted branch feature/user-dashboard
```

### 14.9 步骤 8：清理本地环境

```bash
# 切回主分支
git checkout main

# 拉取最新代码
git pull

# 删除本地分支
git branch -d feature/user-dashboard
```

## 15. Fork 工作流

Fork 工作流是开源项目贡献的常见模式。贡献者先从目标仓库 Fork 一份到自己的账号下，在 Fork 仓库完成开发后，再向上游提交 PR。

### 15.1 Fork 仓库并克隆

```bash
# 通过 gh 命令 Fork 上游仓库
gh repo fork owner/upstream-repo --clone

# 等效于先 Fork 再克隆
gh repo fork owner/upstream-repo
cd upstream-repo
```

### 15.2 创建特性分支

```bash
git checkout -b feature/my-contribution
# 编写代码...
git add .
git commit -m "feat: 添加新功能"
git push -u origin feature/my-contribution
```

### 15.3 向上游提交 PR

使用 `--head` 指定 Fork 仓库的分支，格式为 `username:branch`：

```bash
gh pr create \
  --title "feat: 添加新功能" \
  --body "## 变更说明

详细描述你的变更内容。" \
  --base main \
  --head "your-username:feature/my-contribution" \
  --reviewer "upstream-maintainer"
```

> **关键参数**：`--head "your-username:feature/my-contribution"` 告诉 GitHub 这个 PR 的源分支来自你的 Fork 仓库。如果省略 `--head`，`gh` 默认使用当前仓库的当前分支，这在 Fork 场景下通常不是你想要的行为。

### 15.4 同步上游更新

当上游仓库有新的提交时，需要同步到你的 Fork：

```bash
# 添加上游仓库为远程
git remote add upstream https://github.com/owner/upstream-repo.git

# 拉取上游更新
git fetch upstream

# 将上游 main 合并到本地 main
git checkout main
git merge upstream/main

# 推送到你的 Fork
git push origin main
```

### 15.5 Fork 工作流完整示例

```bash
# 1. Fork 并克隆
gh repo fork owner/awesome-project --clone

# 2. 创建特性分支
cd awesome-project
git checkout -b feature/add-dark-mode

# 3. 编码与提交
# ... 编写代码 ...
git add .
git commit -m "feat: 添加暗黑模式支持"
git push -u origin feature/add-dark-mode

# 4. 向上游提交 PR
gh pr create \
  --title "feat: 添加暗黑模式支持" \
  --body "## 实现说明

- 使用 CSS 变量实现主题切换
- 支持系统偏好自动检测
- 新增 ThemeProvider 组件
- 覆盖所有现有页面

Closes upstream-repo#28" \
  --base main \
  --head "your-username:feature/add-dark-mode" \
  --reviewer "upstream-maintainer"

# 5. 等待审查和 CI 检查
gh pr checks --watch

# 6. 根据审查意见修改（如有需要）
# ... 修改代码 ...
git add .
git commit -m "fix: 根据审查意见优化主题切换性能"
git push
```

## 16. 常见问题

### 16.1 创建 PR 时提示"当前分支没有新的提交"

**原因**：当前分支与目标分支的提交历史一致，没有可合并的差异。

**解决**：

```bash
# 确认有新的提交
git log main..HEAD --oneline

# 如果输出为空，说明没有新提交，需要先提交代码
git add .
git commit -m "feat: 你的变更"
git push
```

### 16.2 使用 `gh pr checkout` 时提示"无法找到 PR"

**原因**：PR 编号不存在或当前目录不在正确的仓库中。

**解决**：

```bash
# 显式指定仓库
gh pr checkout 42 --repo owner/repo

# 或先切换到正确的仓库目录
cd /path/to/repo
gh pr checkout 42
```

### 16.3 合并时被阻止

**原因**：分支保护规则要求特定条件（如审查通过、CI 通过、签名验证等）。

**解决**：

```bash
# 查看当前检查状态
gh pr checks 42

# 查看审查状态
gh pr view 42 --json reviews

# 满足所有条件后再合并
gh pr merge 42 --squash
```

### 16.4 草稿 PR 无法合并

**原因**：草稿 PR 在大部分仓库中无法合并。

**解决**：先转为正式 PR。

```bash
gh pr ready 42
gh pr merge 42 --squash
```

## 17. 相关资源

- [安装与配置指南](01-installation.md) — 安装 `gh` 并完成认证
- [GitHub CLI 官方文档 - gh pr](https://cli.github.com/manual/gh_pr) — 完整命令参考
- [GitHub 官方文档 - Pull Request](https://docs.github.com/en/pull-requests) — PR 概念与最佳实践
- [GitHub 官方文档 - Fork 工作流](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks) — Fork 协作模式详解