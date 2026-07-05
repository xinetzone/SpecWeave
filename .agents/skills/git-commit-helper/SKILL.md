---
name: git-commit-helper
version: 1.1.0
description: "当用户提到'提交'、'commit'、'原子提交'、'代码提交'、'提交变更'、'git commit'、'保存更改'时，必须使用此技能。提供Git原子化提交规范执行能力：检查变更（三查暂存法）→预提交验证→构建提交信息→执行提交→验证结果。遵循Conventional Commits规范，确保单次提交单一职责。不要直接git commit——本Skill封装了预检查、三查暂存验证、提交信息格式和验证流程。"
argument-hint: "[--dry-run] [--type <type>] [--scope <scope>]"
user-invocable: true
paths:
  - ".agents/skills/git-commit-helper/scripts/validate_commit.py"
  - ".agents/skills/git-commit-helper/references/conventional-commits.md"
title: "Git 原子提交助手 Skill"
---
# Git 原子提交助手 Skill

> 本Skill遵循**渐进式披露三层架构**：
> - **L0**：本文件（SKILL.md）——触发条件+核心流程+安全清单，<200行
> - **L1**：[references/conventional-commits.md](references/conventional-commits.md)——Conventional Commits规范详解（按需加载）
> - **L2**：[scripts/validate_commit.py](scripts/validate_commit.py)——提交信息验证脚本（可执行工具）

## 1. Skill ID
`git-commit-helper`

## 2. 功能描述

按照 Conventional Commits 规范生成原子化 Git 提交，确保每次提交遵循"单一职责"原则：

| 特性 | 说明 |
|------|------|
| **三查暂存法** | 查工作区状态 → 查暂存区差异 → 查最近提交记录，确保提交范围正确 |
| **类型自动推断** | 根据变更文件自动推断 commit type（feat/fix/docs/refactor/test/chore等） |
| **格式校验** | 验证提交信息符合 `<type>(<scope>): <subject>` 格式 |
| **中文描述** | subject 使用中文清晰描述变更目的（为什么改，不是改了什么） |
| **提交前预览** | 默认展示完整提交信息供用户确认后再执行 |
| **操作性质** | ✏️ 写操作，但所有破坏性操作前需用户确认 |

> **为什么要用原子提交而不是直接 git commit？** 直接 commit 容易犯三个错误：一是把不相关的改动混在一起提交（一个commit既有bugfix又有新功能），导致回滚时牵连无辜；二是提交信息模糊（"更新代码""fix bug"），三个月后看log完全不知道改了什么；三是忘记检查工作区状态，误把调试代码/临时文件提交上去。本Skill通过"三查暂存法"和格式校验，确保每个commit都是可回溯、可回滚、语义清晰的原子单元。

## 3. 何时使用本技能

### 必用场景
- 用户要求提交代码、保存更改、git commit
- 完成一个功能/修复后准备提交
- 重构完成后需要提交变更

### 触发词
- "提交"、"commit"、"原子提交"、"代码提交"
- "提交变更"、"git commit"、"保存更改"

## 4. 执行流程

严格按以下5步执行，**不要跳过任何步骤**：

```
步骤1: 三查暂存（必做，只读检查）
  ├─ 1a. git status --short  → 查看工作区和暂存区状态
  ├─ 1b. git diff --staged   → 查看已暂存的变更内容
  └─ 1c. git log --oneline -5 → 查看最近5条提交记录（了解提交风格）

步骤2: 变更分析
  ├─ 识别变更文件列表
  ├─ 根据文件路径推断 commit type（见§5类型映射表）
  ├─ 根据主要变更模块推断 scope
  └─ 提炼 subject：用一句话描述"为什么改"（中文，祈使句，不加句号）

步骤3: 构建提交信息
  ├─ 格式：<type>(<scope>): <subject>
  ├─ 如有破坏性变更，追加 ! 和 BREAKING CHANGE 脚注
  ├─ 运行验证脚本检查格式：python scripts/validate_commit.py "<message>"
  └─ 修复验证发现的问题

步骤4: 提交预览与确认
  ├─ 向用户展示：变更文件列表 + 提交信息 + 变更统计
  ├─ 等待用户明确确认（"提交"/"确认"/"yes"）
  └─ 用户要求修改则回到步骤2调整

步骤5: 执行提交并验证
  ├─ git add <相关文件>（精确add，不要git add -A）
  ├─ git commit -m "<message>"（使用HEREDOC传递含特殊字符的信息）
  └─ git log --oneline -1 → 验证提交结果
```

## 5. Commit Type 映射表

| Type | 适用场景 | 文件模式示例 |
|------|---------|-------------|
| **feat** | 新功能、新特性 | `*.ts`新增组件、`apps/`新增页面 |
| **fix** | Bug修复 | 修复逻辑错误、异常处理 |
| **docs** | 文档更新 | `*.md`、注释、README |
| **style** | 代码格式（不影响逻辑） | 空格、格式化、分号 |
| **refactor** | 重构（非feat非fix） | 重命名、提取函数、结构调整 |
| **perf** | 性能优化 | 缓存、懒加载、算法优化 |
| **test** | 测试相关 | `*test*`、`*spec*`、新增测试用例 |
| **chore** | 构建/工具/依赖 | `package.json`、CI配置、脚本 |
| **ci** | CI/CD变更 | `.github/workflows/`、流水线配置 |
| **revert** | 回滚提交 | `git revert` 操作 |

### Scope 推断规则
- 单体项目：使用主要变更的模块/目录名（如 `auth`、`utils`、`docs`）
- 多包项目：使用包名（如 `core`、`cli`、`web`）
- 跨模块小改动：可以省略scope，格式为 `<type>: <subject>`

## 6. Subject 编写规范

| 规则 | ✅ 好的示例 | ❌ 坏的示例 |
|------|-----------|-----------|
| 使用中文，祈使句 | "修复登录态过期跳转问题" | "fixed login bug"、"修复了一个问题" |
| 描述"为什么改"而非"改了什么" | "为列表页添加分页支持" | "修改了list.tsx文件" |
| 不加句号结尾 | "重构用户服务依赖注入" | "重构用户服务。" |
| 长度≤50字 | "优化首屏加载时间减少300ms" | "做了一些优化和调整还有bug修复" |
| 一个commit只说一件事 | "修复日期选择器跨年选择异常" | "修复日期选择器bug并优化表格样式" |

> **为什么subject要写"为什么改"？** 因为`git diff`已经告诉你"改了什么"（具体代码变更），commit message的价值在于解释**变更背后的意图**。三个月后你看到一行被修改的代码，通过diff能看到改了什么，但你需要commit message告诉你当时为什么做这个改变。

## 7. 安全检查清单（提交前逐项确认）

- [ ] **三查已执行**：已查看status/diff/log，了解当前变更全貌
- [ ] **暂存精确**：使用 `git add <file>` 精确添加，未使用 `git add -A` 或 `git add .`（避免误提交临时文件）
- [ ] **单一职责**：本次提交只包含一件事，没有混入无关变更
- [ ] **格式正确**：type/scope/subject 格式符合规范（可运行验证脚本确认）
- [ ] **无敏感信息**：提交内容不含密码、密钥、.env文件、本地配置
- [ ] **fix类型提交专项检查**（type=fix时必须执行）：
  - [ ] 若本次提交包含Bug修复，是否包含预防措施（检查脚本/测试用例/规则更新/反模式清单）？遵循[fix-prevent-close-loop](../../rules/fix-prevent-close-loop.md)三阶段SOP
  - [ ] 如属于平凡修复（拼写/格式/注释/清理），确认符合豁免条件
  - [ ] commit message中注明预防措施类型（如`[prevent: test-case]`、`[prevent: check-script]`、`[prevent: rule-update]`、`[prevent: trivial-exempt]`）或引用跟踪Issue
- [ ] **用户已确认**：提交信息和文件列表已向用户展示并获得明确确认
- [ ] **提交后验证**：commit 后运行 `git log -1` 确认提交成功

## 8. 常见错误处理

| 问题 | 原因 | 处理方式 |
|------|------|---------|
| 提交信息格式验证失败 | type/scope/subject不符合规范 | 根据验证脚本提示修正，参考§5类型表和§6编写规范 |
| 工作区有未暂存变更 | git add 不完整 | 检查 `git status`，确认是否需要 add 或者 stash |
| 变更范围太大 | 一次改了太多东西 | 建议拆分提交：先提交A功能，再提交B修复 |
| 误提交了敏感文件 | add了不该提交的文件 | `git reset HEAD <file>` 取消暂存，检查 `.gitignore` |

## 9. Gotchas（陷阱与注意事项）

- **Windows中文编码**：PowerShell下commit message含中文时，避免在命令行直接用 `-m "中文"`（可能GBK乱码），使用HEREDOC方式传递：`git commit -m "$(cat <<'EOF'<message>EOF)"`
- **不要用 `git add .`**：这个命令会把所有修改（包括调试打印、临时文件、.env）都加入暂存，必须精确指定要提交的文件
- **amend不是常规操作**：`git commit --amend` 只用于修改**最近一次且未push**的提交，不要习惯性amend，已push的commit禁止amend（会破坏其他人的历史）
- **--no-verify不是逃生舱**：不要为了绕过pre-commit hook而加 `--no-verify`，hook报错说明代码有问题，应该修复问题而非跳过检查

## 10. 快速参考

### 最简提交流程（用户确认后执行）

```bash
# 1. 三查
git status --short
git diff --staged
git log --oneline -5

# 2. 精确暂存
git add <file1> <file2>

# 3. 验证提交信息格式
python .agents/skills/git-commit-helper/scripts/validate_commit.py "feat(auth): 添加JWT令牌刷新机制"

# 4. 提交（使用HEREDOC避免编码问题）
git commit -m "$(cat <<'EOF'
feat(auth): 添加JWT令牌刷新机制
EOF
)"

# 5. 验证
git log --oneline -1
```

### 验证脚本使用

```bash
# 验证提交信息格式
python .agents/skills/git-commit-helper/scripts/validate_commit.py "fix(login): 修复登录态过期跳转问题"

# 干跑模式（只分析当前变更，不提交）
python .agents/skills/git-commit-helper/scripts/validate_commit.py --dry-run
```

## 11. Changelog

- **v1.1.0** (2026-07-06): 新增"fix类型提交专项检查"安全清单项和validate_commit.py预防标记自动检测，强制执行"修复即闭环"三阶段SOP（修复→预防→闭环），禁止纯点修复提交。平凡修复（拼写/格式/注释/清理）可使用[prevent: trivial-exempt]标记豁免。
- **v1.0.0** (2026-07-05): 初始版本。三查暂存法、Conventional Commits规范、提交信息验证脚本。
