---
type: Wiki Tutorial

id: cpython-devguide-02
title: "02 - 深度开发流程"
date: 2026-08-19
tags: [cpython, workflow, git, testing, release, backport, lifecycle]
source:
  - devguide.python.org
  - github.com/python/cpython
  - external/libs/python/devguide
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/cpython-devguide-wiki/02-development-workflow.toml"
maturity: L1-draft
---
# 02 - 深度开发流程

本章深入讲解CPython的Git工作流、PR生命周期、版本管理和测试体系，帮助你理解从代码修改到版本发布的完整流程。

## Git工作流详解

### 远程仓库配置

CPython开发使用经典的"Fork + Pull Request"模型：

| 远程名 | 指向 | 权限 | 用途 |
|--------|------|------|------|
| `origin` | `github.com/YOUR_USERNAME/cpython` | 读写 | 你的个人Fork，push你的分支 |
| `upstream` | `github.com/python/cpython` | 只读 | 官方仓库，pull最新代码 |

```bash
# 设置远程（首次克隆后）
git clone https://github.com/YOUR_USERNAME/cpython.git
cd cpython
git remote add upstream https://github.com/python/cpython.git

# 验证
git remote -v
```

### 日常工作流命令

```bash
# ===== 开始新工作前：同步main分支 =====
git switch main
git pull upstream main

# ===== 创建特性分支 =====
git switch -c gh-12345-fix-description upstream/main

# ===== 工作、提交 =====
# ... 编辑代码 ...
git add -p              # 逐块审查暂存
git commit -m "gh-12345: Fix description"

# ===== 推送并创建PR =====
git push origin gh-12345-fix-description
# 然后到GitHub创建PR

# ===== PR review期间：响应修改 =====
# ... 按review意见修改代码 ...
git add -p
git commit -m "Address review comments"
git push origin gh-12345-fix-description
# ⚠️ 不要 force-push！不要 rebase！不要 squash！

# ===== PR合并后：清理 =====
git switch main
git pull upstream main
git branch -d gh-12345-fix-description
git push origin --delete gh-12345-fix-description
```

### 实用Git命令参考

| 命令 | 用途 |
|------|------|
| `git status` | 查看当前分支状态、修改文件 |
| `git diff` | 查看未暂存的修改 |
| `git diff --staged` | 查看已暂存的修改 |
| `git add -p` | 交互式逐块暂存（强烈推荐） |
| `git checkout -- <file>` | 丢弃文件的未暂存修改 |
| `git reset HEAD <file>` | 取消暂存文件 |
| `git stash` | 暂存当前修改（临时切换分支时用） |
| `git stash pop` | 恢复stash的修改 |
| `git log --oneline -10` | 查看最近10条commit |
| `git log --oneline --graph` | 查看分支图 |

### 检出他人的PR进行测试

有时你需要在本地测试或审阅他人的PR：

```bash
# 方法1：使用GitHub CLI（推荐）
gh pr checkout PR_NUMBER

# 方法2：手动添加git别名
git config --global alias.pr '!f() { git fetch upstream pull/$1/head:pr/$1 && git switch pr/$1; }; f'
# 之后使用：
git pr PR_NUMBER

# 方法3：手动fetch
git fetch upstream pull/PR_NUMBER/head:pr-12345
git switch pr-12345
```

### Git Worktree：多分支并行工作

当你同时在多个PR上工作时，`git worktree` 可以避免反复切换分支需要重新编译的问题：

```bash
# 创建worktree目录
git worktree add ../cpython-pr-12345 gh-12345-fix-bug
# 这会在 ../cpython-pr-12345 创建一个新的工作目录
# 检出 gh-12345-fix-bug 分支，共享.git目录

# 在新目录中独立工作
cd ../cpython-pr-12345
# 独立编译、修改、提交，不影响主工作目录

# 清理worktree
cd ../cpython
git worktree remove ../cpython-pr-12345
```

### ⚠️ PR Review期间禁止Force-Push

这是CPython开发中**最重要**的Git规则：

**为什么禁止force-push？**
1. **审阅者需要增量diff** — Core Dev审阅你的修改时，需要看到你在上一轮review后具体改了什么。Force-push会重写历史，导致之前的review评论失效（显示"outdated"但无法看到上下文）。
2. **Squash merge会处理历史** — PR被merge时，GitHub会自动将你的所有commit压缩成一个干净的commit，你不需要自己清理历史。
3. **审查效率** — 审阅者可以快速浏览新push的commit，而不是重新审查整个diff。

**正确做法**：
```bash
# review意见来了，修改代码后直接追加commit
git add -p
git commit -m "Address review feedback"
git push
# 追加多个commit也没关系，squash merge会清理一切
```

**唯一例外**：如果PR创建后很快（还没有人review）发现自己提交了敏感信息或明显的错误commit，可以amend+force-push。一旦有人开始review，就绝对不要force-push。

## PR生命周期全解

```
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────────┐
│  Issue  │───→│  Fork/   │───→│  Code +      │───→│  Local Verify│
│ 创建/发现│    │  Branch  │    │  Tests 编写  │    │  测试+patchchk│
└─────────┘    └──────────┘    └──────────────┘    └──────┬───────┘
                                                         │
                         ┌───────────────────────────────┘
                         ▼
┌──────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Squash      │←───│ Approve  │←───│ Re-review│←───│ Changes  │
│  Merge 合并  │    │ 批准合并 │    │ 再次审阅  │    │ + Push   │
└──────┬───────┘    └──────────┘    └──────────┘    └──────┬───┘
       │                                                  │
       │    ┌──────────┐    ┌──────────┐    ┌─────────────┘
       └───→│ Backport │←───│ Review   │←──→│ Push分支     │
            │ 版本回溯  │    │ Code审查 │    │ 创建PR       │
            └──────────┘    └────┬─────┘    └──────────────┘
                                 │
                          ┌──────▼──────┐
                          │ CI 自动测试  │
                          │ 多平台运行   │
                          └─────────────┘
```

### PR质量要求

提交PR前确保满足以下要求：

1. **目标分支正确**：bug fix和新功能先提交到 `main` 分支，需要backport时由RM处理
2. **代码风格**：Python代码遵循PEP 8，C代码遵循PEP 7，通过pre-commit检查
3. **向后兼容**：除非有意为之且经过讨论，不要破坏现有API
4. **包含测试**：bug fix添加回归测试，新功能添加功能测试
5. **测试通过**：至少相关测试全部通过，推荐运行全量测试
6. **原子性**：一个PR只解决一个问题，不混入无关改动
7. **文档更新**：如果修改了公共API或行为，更新相关文档
8. **NEWS条目**：用户可见的变更需要NEWS条目（见下文）

### NEWS条目详解

NEWS条目会被整合到每个版本的"What's New"文档中。

**分类目录**（`Misc/NEWS.d/next/`下）：
- `Library/` — 标准库变更
- `Core and Builtins/` — 解释器核心和内建
- `C API/` — C API变更
- `Security/` — 安全修复
- `Documentation/` — 文档改进（仅重大变更）
- `Tests/` — 测试相关（极少需要）
- `Build/` — 构建系统
- `Windows/` — Windows特定
- `macOS/` — macOS特定
- `Tools/` — 工具脚本
- `IDLE/` — IDLE相关

**NEWS条目写作风格**：
- 使用**过去式**描述（"Fixed ..."而非"Fix ..."——这是已合入的变更记录）
- 简洁明了，一句话说明问题和修复
- 包含Issue编号：`:gh-issue:`12345``
- 对于安全修复，包含CVE编号

**示例**：
```
Fixed a reference leak in :func:`os.scandir` when the iterator is
garbage-collected before being exhausted. Patch by Jane Doe.
```

```
:func:`datetime.fromisoformat` now correctly handles strings with
fractional seconds of more than 6 digits. Patch by John Smith.
```

**使用blurb工具创建**：
```bash
./python -m blurb add
# 交互式选择分类并输入描述
# 自动创建 Misc/NEWS.d/next/CATEGORY/YYYY-MM-DD-HH-MM-SSgh-ISSUE-NONCE.rst
```

> ⚠️ 不需要NEWS的情况：纯文档修改、纯测试补充/修复、typo修正、不影响用户的内部重构、注释/空白清理。

### Commit Message规范

**格式**：`gh-ISSUENUM: 描述`

规则：
- 使用**祈使句**（Fix, Add, Update, Remove），不用过去式
- 首字母大写
- 末尾不加句号
- 不超过72字符
- 描述清晰具体，不用"fix bug"这种笼统描述

| ✅ 好 | ❌ 差 |
|-------|-------|
| `gh-12345: Fix reference leak in os.scandir()` | `fix bug` |
| `gh-12346: Add tests for datetime edge cases` | `updates` |
| `gh-12347: Improve error message for invalid mode` | `Fixed a typo in docs.` |
| `gh-12348: Deprecate unused legacy API` | `gh-12345: various fixes` |

**无Issue的commit**：极少数情况下如果没有对应Issue，可以使用 `gh-0:` 前缀，但强烈建议先创建Issue。

### Backport（版本回溯）流程

Bug修复合入 `main` 后，如果影响维护版本，需要backport到维护分支：

1. **自动backport（miss-islington bot）**：
   - PR合并后，Core Dev添加 `needs backport to 3.Y` 标签
   - miss-islington bot自动创建backport PR
   - 如果没有冲突，Core Dev合并即可

2. **手动backport（cherry_picker）**：
   - 当自动backport有冲突时需要手动操作
   ```bash
   # 安装cherry_picker
   ./python -m pip install cherry_picker

   # backport到3.13分支
   ./python -m cherry_picker COMMIT_HASH 3.13

   # 解决冲突后
   ./python -m cherry_picker --continue
   # 自动push并创建PR
   ```

3. **backport规则**：
   - **Feature（新功能）**：不backport，只在main分支
   - **Bug fix**：backport到受影响的维护分支
   - **Security fix**：由PSRT决定backport范围
   - **Documentation fix**：backport到对应版本分支
   - **API change**：通常不backport（除非是bug导致的）

## 开发周期与版本管理

### 版本号方案

CPython使用语义化版本的变体：`MAJOR.MINOR.MICRO{LEVEL}{SERIAL}`

| 部分 | 说明 | 示例 |
|------|------|------|
| MAJOR | 大版本，不兼容的API变更 | 3 → 4（Python 4尚无计划） |
| MINOR | 特性版本，新功能、新API | 3.12, 3.13, 3.14 |
| MICRO | 补丁版本，bug修复、安全修复 | 3.13.1, 3.13.2 |
| LEVEL | 预发布阶段 | a(alpha), b(beta), rc(release candidate), final |
| SERIAL | 预发布序号 | a1, b2, rc1 |

**完整版本号示例**：
- `3.14.0a1` — 3.14的第一个alpha
- `3.13.0b2` — 3.13的第二个beta
- `3.12.7` — 3.12的第七个micro版本（final）

### 分支类型

| 分支类型 | 命名 | 说明 | 接受的PR |
|----------|------|------|----------|
| **开发分支** | `main` | 下一版本的开发分支 | 新功能、bug修复、一切 |
| **维护分支** | `3.13`, `3.14` | 已发布特性版本的维护 | bug修复（通过backport） |
| **安全分支** | `3.11`（进入安全模式后） | 仅接受安全修复 | 安全修复（由PSRT处理） |
| **EOL分支** | `3.10`及更早 | 不再支持 | 不接受任何PR |

### 发布阶段

```
pre-alpha → alpha → beta（feature freeze）→ RC → final
   │         │         │                      │      │
   │         │         │                      │      └─ 正式发布，进入维护
   │         │         │                      └─ 仅peer review修复，不加新功能
   │         │         └─ 特性冻结，只修bug，不加新功能
   │         └─ 可以试验新API，可能有破坏性变更
   └─ main分支，大量新功能开发中
```

| 阶段 | 特征 | 可接受的变更 |
|------|------|-------------|
| **Alpha** | 新功能开发期，PEP实现 | 几乎所有变更，包括破坏性变更 |
| **Beta（feature freeze）** | 功能冻结，进入测试期 | 仅bug修复，不增加新功能 |
| **RC（release candidate）** | 发布候选 | 仅阻塞性bug修复、文档修复 |
| **Final** | 正式发布 | 转入维护模式，仅bug/安全修复 |

### 支持生命周期

```
新MINOR版本发布
    │
    ├── Feature开发期（~18个月，在main分支）
    │   └─ alpha → beta → rc → final
    │
    ├── Bugfix模式（~18-24个月）
    │   └─ 每2个月发布一个micro版本
    │   └─ 接受bug fix backport
    │
    ├── Security模式（~5年总计）
    │   └─ 仅接受安全修复
    │   └─ 由PSRT管理
    │
    └── EOL（End of Life）
        └─ 不再接受任何修复
        └─ 用户应升级到支持版本
```

**当前支持版本**（以实际为准）：
- `main` — 3.14开发中
- `3.13` — bugfix模式
- `3.12` — bugfix模式
- `3.11` — security模式
- `3.10`及更早 — EOL

### CPython源码目录地图

| 目录 | 内容 | 语言 | 贡献频率 |
|------|------|------|----------|
| `Doc/` | 官方文档（.rst格式） | reStructuredText | ⭐⭐⭐⭐⭐ 非常高 |
| `Lib/` | Python标准库 | Python | ⭐⭐⭐⭐⭐ 非常高 |
| `Lib/test/` | 测试套件 | Python | ⭐⭐⭐⭐⭐ 非常高 |
| `Modules/` | C扩展模块（如_socket, _json） | C | ⭐⭐⭐ 中等 |
| `Objects/` | 核心对象类型实现（int, str, list, dict等） | C | ⭐⭐ 较低 |
| `Python/` | 解释器核心（字节码执行、编译器、GC） | C | ⭐⭐ 较低 |
| `Parser/` | Python语法解析器 | C | ⭐ 低 |
| `Include/` | 头文件（公共C API和内部API） | C | ⭐⭐ 较低 |
| `PC/` | Windows平台特定代码 | C | ⭐⭐ 较低 |
| `PCbuild/` | Windows构建系统 | batch/props | ⭐ 低 |
| `Mac/` | macOS平台特定代码 | C/Python | ⭐ 低 |
| `Programs/` | 可执行程序入口（python.c等） | C | ⭐ 低 |
| `Tools/` | 开发和维护工具 | Python | ⭐⭐ 较低 |
| `Misc/` | NEWS条目、其他杂项 | rst/text | ⭐⭐⭐⭐ 高 |

> 💡 **新贡献者最常接触的目录**：`Doc/`（文档）、`Lib/`（标准库）、`Lib/test/`（测试）。这三个目录占所有贡献的80%以上。

## 测试体系

### 测试命令大全

```bash
# ===== 基本测试 =====

# 全量测试（多核并行）
./python -m test -j0

# 单个测试文件
./python -m test test_os
./python -m test test_datetime test_json

# 单个测试用例（精确匹配）
./python -m test test_os -v -m test_scandir_basic

# 直接运行测试文件（不需要test runner）
./python -m unittest Lib/test/test_os.py
./python Lib/test/test_os.py

# ===== 严格模式 =====
# -bb: bytes/bytearray与str比较时抛异常
# -E: 忽略环境变量（PYTHONPATH等）
# -Wd: 默认显示DeprecationWarning
# -r: 随机种子执行（发现测试顺序依赖）
# -w: 失败时重试（识别flaky test）
# -uall: 启用所有"特殊资源"测试（网络、大文件等）
./python -bb -E -Wd -m test -r -w -uall -j0

# ===== 高级测试 =====

# C代码内存泄漏检测（运行3次，比较引用计数）
# 格式: -R RUNS:LOOPS
./python -m test -R 3:3 test_os

# 覆盖率测试
./python -m pip install coverage
./python -m coverage run -m test test_os
./python -m coverage report -m

# 详细输出
./python -m test -v test_os

# 列出所有测试用例
./python -m test -v test_os --list-tests
```

### 测试类型

| 测试类型 | 位置 | 说明 |
|----------|------|------|
| 回归测试 | `Lib/test/test_*.py` | 验证bug修复和功能正确性 |
| 单元测试 | `Lib/test/test_*.py` | 模块/类/函数的单元测试 |
| Doctest | 文档字符串中 | 文档中的示例代码测试 |
| C测试 | `Modules/_testcapi/` 等 | C API的测试 |
| 性能测试 | `pyperformance` | 外部基准测试套件 |

### Buildbot与CI

- **GitHub Actions (GHA)**：每个PR自动在Linux/macOS/Windows上运行测试套件
- **Buildbot**：[buildbot.python.org](https://buildbot.python.org) — 由社区维护的更多平台测试（AIX、ARM、BSD、旧版本OS等）
- **OSS-Fuzz**：Google的模糊测试服务，持续对CPython进行fuzzing测试，发现安全漏洞和crash bug
- **CI检查项**：
  - 多平台编译（Linux/macOS/Windows）
  - 全量测试（多配置：debug、release、free-threaded、ASAN等）
  - 文档构建检查
  - pre-commit/lint检查
  - ABI稳定性检查

---

## 下一步

👉 [03 - 治理与社区：沟通渠道、分类处理、核心团队与AI政策](03-governance-community.md)
