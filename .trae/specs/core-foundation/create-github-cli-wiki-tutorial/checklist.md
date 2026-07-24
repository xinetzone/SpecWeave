# Checklist: GitHub CLI Wiki 教程

## 七概念方法论质量门（G1-G4）

### G1：事实无因果词（R 阶段）

- [ ] 学习笔记中无主观因果推断词（"因为"、"所以"、"导致"、"错误"、"失误"），纯客观记录
- [ ] 三个来源（cli.githubdocs.cn、cli.github.com、github.com/cli/cli）的关键信息均已覆盖

### G2：洞察四元组完整（I 阶段）

- [ ] 教程结构设计包含：知识点识别（从三来源中提取出的共性主题）+ 组织结构（8 章划分的理由）+ 关联关系（章节间交叉引用）+ 应用场景（每章在 SpecWeave 工作流中的定位）

### G3：模式可迁移（E 阶段）

- [ ] 每个章节独立可读，不依赖其他章节的上下文
- [ ] 命令示例完整可复现，用户可直接复制执行
- [ ] 教程内容可迁移至其他技术栈的 CLI 工具教学场景

### G4：行动项原子化（C 阶段）

- [ ] 每次提交仅包含单一文档文件（单一职责）
- [ ] 提交信息遵循 Conventional Commits 规范（`docs(gh-cli-wiki): <subject>`）
- [ ] 提交历史清晰可追溯，每个提交对应一个独立的知识点

## 文档质量检查

### 00-overview.md

- [ ] 包含教程简介和目标读者说明
- [ ] 包含 8 章导航表
- [ ] 包含 Mermaid 架构图
- [ ] 包含阅读路径建议

### 01-installation.md

- [ ] 覆盖 Windows 安装（winget/scoop/msi 至少两种）
- [ ] 覆盖 macOS 安装（brew）
- [ ] 覆盖 Linux 安装（apt/yum/dnf/pacman 至少两种）
- [ ] 包含 `gh auth login` 认证流程（HTTPS 和 SSH 两种）
- [ ] 包含 `gh auth status` 验证方法
- [ ] 包含 Shell 补全配置（bash/zsh/fish/powershell 至少三种）
- [ ] 包含 `gh config` 配置管理

### 02-basic-commands.md

- [ ] 覆盖 `gh repo clone/create/fork/view/list`
- [ ] 覆盖 `gh issue create/list/view/status/comment`
- [ ] 覆盖 `gh gist create/list/view/edit/delete`
- [ ] 每个命令包含参数说明和使用示例

### 03-pr-workflow.md

- [ ] 覆盖 `gh pr create`（含 --web/--fill/--draft）
- [ ] 覆盖 `gh pr checkout`
- [ ] 覆盖 `gh pr review`（approve/comment/request-changes）
- [ ] 覆盖 `gh pr merge`（--squash/--rebase/--merge）
- [ ] 覆盖 `gh pr status/checks/diff/view`
- [ ] 包含完整 PR 工作流示例

### 04-actions-cicd.md

- [ ] 覆盖 `gh workflow list/view/enable/disable/run`
- [ ] 覆盖 `gh run list/view/watch/rerun/download`
- [ ] 覆盖 `gh secret list/set/remove`
- [ ] 覆盖 `gh variable list/set/remove`

### 05-advanced-usage.md

- [ ] 覆盖 `gh api`（REST + GraphQL），含 `--paginate`/`--jq`/`--template` 选项
- [ ] 覆盖 `gh alias`（set/list/delete）
- [ ] 覆盖 `gh extension`（install/list/search/remove/create）
- [ ] 覆盖 `gh search`（repos/issues/prs）
- [ ] 覆盖 `--json` + `jq` 组合使用示例

### 06-faq-troubleshooting.md

- [ ] 不少于 10 个常见问题
- [ ] 覆盖认证失败问题（token 过期/权限不足）
- [ ] 覆盖网络代理配置
- [ ] 覆盖版本升级（`gh upgrade`）
- [ ] 覆盖 SSH 密钥问题
- [ ] 覆盖 API 限流处理
- [ ] 每个问题包含现象描述和解决方案

### 07-cheatsheet.md

- [ ] 包含按功能分类的命令速查表
- [ ] 包含 SpecWeave 工作流集成最佳实践
- [ ] 包含原子化提交工作流集成示例

## 文件规范性检查

- [ ] 所有文件使用 YAML frontmatter（含 `source` 字段）
- [ ] 文档间交叉引用使用相对路径
- [ ] 无 `file:///` 绝对路径断链
- [ ] 文件命名使用 kebab-case
- [ ] 目录结构符合项目 wiki 规范（`docs/knowledge/learning/github-cli-wiki/`）