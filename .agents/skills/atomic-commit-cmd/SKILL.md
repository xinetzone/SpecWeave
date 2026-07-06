---
name: atomic-commit-cmd
version: 1.6.0
description: "当用户提到'提交'、'commit'、'原子提交'、'代码提交'、'提交代码'、'提交变更'、'git commit'、'保存更改'时，必须使用此技能。提供Git原子化提交规范执行能力：检查变更（三查暂存法）→预提交验证→构建提交信息→执行提交→验证结果。遵循Conventional Commits规范，确保单次提交单一职责。不要直接git commit——本Skill封装了预检查、三查暂存验证、提交信息格式和验证流程。"
argument-hint: "<提交类型：feat/fix/refactor/test/docs/chore/perf> [scope] <提交信息>"
user-invocable: true
paths:
  - ".agents/commands/atomic-commit.md"
  - ".agents/scripts/ci-check.ps1"
  - "rules/cmd-log-specification.md"
title: "Atomic-Commit 原子提交命令 Skill"
---
# Atomic-Commit 原子提交命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/atomic-commit.md](../../commands/atomic-commit.md)（完整流程）+ [cmd-log-specification.md](../../rules/cmd-log-specification.md)（日志规范）

## 1. Skill ID
`atomic-commit-cmd`

## 2. 功能描述

提供Git原子化提交执行能力，确保单次提交遵循单一职责原则：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **标准原子提交** | ⭐ 日常代码/文档提交 | 完整预检查+规范信息格式 |
| **快速提交** | ⭐ 小改动/紧急修复 | 跳过非必要检查（仍需基本验证） |
| **提交前CI检查** | ⭐ 重要功能/重构提交 | 运行完整CI检查套件 |

核心功能：检查变更范围→执行预提交验证→构建规范提交信息→执行提交→验证结果。

> **为什么用本Skill而非直接git commit？** 直接commit容易混入无关文件、提交信息不规范、跳过必要检查；原子提交确保每次提交只做一件事、提交信息说明"为什么"而非"做了什么"、预提交检查通过后才能提交，保持提交历史清晰可追溯。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "提交"、"commit"、"git commit"、"原子提交"
- "提交代码"、"提交变更"、"代码提交"
- "保存更改"、"保存一下"、"提交一下"
- 功能开发完成、Bug修复完成、文档更新完成后

> **关于触发**：任何Git提交操作都应使用本Skill，以确保符合Conventional Commits规范和原子提交原则。如果是原子化拆分后的提交，应配合atomization-cmd完成内容拆分后再提交。

## 4. 方案选择决策树

```
需要执行Git提交？
├─ 提交前需要完整CI验证？ → 提交前CI检查（运行ci-check.ps1）
├─ 日常小改动/文档更新？ → 标准原子提交
├─ 紧急Hotfix修复？ → 快速提交（仍需基本链接/格式检查）
└─ 原子化拆分完成后的提交？ → 先确认原子化收尾已完成，再标准提交
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `cmt-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S0 | event=CMD_START | session=cmt-... | msg=开始原子提交：<简述> | ctx={"files":"...","type":"feat/fix/docs/refactor/test/chore/ci","dry_run":true/false}
```

> **为什么决策前必须记录日志？** 原子提交涉及文件暂存和提交信息生成，选错提交类型或scope会导致提交历史混乱，CMD_START记录原始输入便于回溯提交决策。

**提交类型速查**（Conventional Commits）：

| 类型 | 用途 | 类型 | 用途 |
|------|------|------|------|
| feat | 新功能 | fix | Bug修复 |
| refactor | 重构（不改功能） | test | 测试相关 |
| docs | 文档更新 | chore | 构建/工具/依赖 |
| perf | 性能优化 | | |

## 5. 快速开始

```
步骤1：读取 [.agents/commands/atomic-commit.md](../../commands/atomic-commit.md) 了解完整流程
步骤2：三查暂存验证（git status --short）：
   - 查新增(A)：排除__pycache__/*.pyc等构建产物，确认都是本次需要的
   - 查修改(M)：确认所有修改属于单一职责范围
   - 查删除(D)：确认所有删除记录都已add（注意：git add新目录不会自动暂存旧文件删除！）
步骤3：执行预提交验证（check-links.py、相关检查脚本、单元测试，重要提交运行ci-check.ps1）
步骤4：构建提交信息（格式：type(scope): subject，中文描述"为什么"）
步骤5：执行提交（显式git add <每个文件> — 禁止git add .）
   - **Windows平台含中文**：优先使用 `python .agents/scripts/git-commit-utf8.py -m "msg" <files>` 自动处理编码
步骤6：验证结果（git log -1确认信息正确无乱码，git status确认无遗漏）
   - **批量提交场景**：全部提交完成后必须重新执行 `git status --short`，若仍有残留变更，回到步骤1分析是否需要追加提交（禁止假设残留是已处理的）
```

> 完整RACI矩阵、CI检查清单、提交信息规范详情见L2文档 [commands/atomic-commit.md](../../commands/atomic-commit.md)。

> **为什么禁止 `git add .`？** `git add .` 会把工作目录中所有变更（包括临时文件、调试日志、敏感配置、无关修改）一股脑加入暂存区，是原子提交原则的最大敌人——它使"一次提交只做一件事"变成不可能。原子提交要求**显式指定每个要提交的文件**，迫使你在add阶段审查每个变更，从源头防止无关文件混入。

## 6. 安全检查清单（提交质量门）

- [ ] 变更范围符合单一职责（一次提交只做一件事）
- [ ] **三查暂存验证完成**：
  - [ ] 查新增(A)：无__pycache__/、*.pyc、临时文件等构建产物
  - [ ] 查修改(M)：所有修改文件都属于本次提交范围
  - [ ] 查删除(D)：所有删除记录都已显式git add（注意：git add新目录不会自动暂存旧文件删除）
- [ ] 没有无关文件混入提交（明确指定文件，禁止 `git add .`）
- [ ] 提交信息遵循Conventional Commits格式（type(scope): subject）
- [ ] 提交信息用中文描述"为什么"而非"做了什么"
- [ ] 预提交检查已执行（链接/格式/测试，适用时）
- [ ] 没有提交敏感信息（密钥、密码、token等）
- [ ] vendor/目录变更符合子模块管理规范（不直接提交vendor内容）
- [ ] **fix类型提交专项检查**：
  - [ ] 若本次提交包含Bug修复（type=fix），是否包含预防措施（检查脚本/测试用例/规则更新/反模式清单）？
  - [ ] 如属于平凡修复（拼写/格式/注释/清理），确认符合豁免条件
  - [ ] commit message中注明预防措施类型（如`[prevent: test-case]`）或引用跟踪Issue
- [ ] **Windows 平台**：
  - [ ] commit message含中文/非ASCII时，优先使用UTF-8临时文件法（commit-msg.txt）
  - [ ] 提交后用 `git cat-file -p HEAD` 验证存储字节未乱码
- [ ] **批量提交场景**：全部提交完成后重新扫描工作区（git status --short），确认无残留变更或已识别后续处理方式

## 7. 执行日志（CMD-LOG）

执行原子提交命令集时，必须按 [CMD-LOG规范](../../rules/cmd-log-specification.md) 输出结构化日志：
- `cmd=atomic-commit`，session前缀 `cmt-YYYYMMDD-<short-hash>`
- 步骤编号 S0-S6（启动→检查范围→预提交验证→构建信息→执行提交→结果验证→推送通知）
- 关键特有事件：`SCOPE_CHECK`、`UNRELATED_FILES`、`SENSITIVE_FILE`、`TEMP_FILE_FOUND`、`VENDOR_CHANGE`、`CHECK_FAIL`、`VERIFICATION_BLOCKED`、`COMMIT_MSG_BUILT`、`COMMIT_EXECUTED`、`COMMIT_FAILED`

> 完整字段说明、20个事件表格、日志示例见L2文档 [cmd-log-specification.md §7.5](../../rules/cmd-log-specification.md)。

## 8. 提交信息速查

✅ 正确示例：
- `feat(skills): 新增5个命令集Skill门面增强能力发现`
- `fix(links): 修复原子化后相对路径错误导致的断链`
- `docs(sop): 沉淀三角验证法为可复用SOP文档`

❌ 错误示例：`update` / `fix` / `提交代码` / `更新了一些东西`

> **为什么提交信息要写"为什么"而非"做了什么"？** "做了什么"从git diff就能看出来（如"修改了auth.ts"），但"为什么做"（如"修复JWT过期时间配置错误导致的凌晨登出问题"）是三个月后回滚或排查问题时唯一能理解变更意图的线索。提交历史是项目的集体记忆，写清楚"为什么"才能让后来人（包括未来的自己）理解当时的决策上下文。

> 完整提交类型表见§4决策树，详细规范见L2 [commands/atomic-commit.md](../../commands/atomic-commit.md)。

## 9. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **Windows中文commit message编码**：PowerShell 5默认使用GBK编码，直接在命令行传递中文commit message会导致Git存储时乱码。**最佳方案**是使用项目已有的 [git-commit-utf8.py](../../scripts/git-commit-utf8.py) 工具：`python .agents/scripts/git-commit-utf8.py -m "type(scope): 中文描述" <files>`，它会自动检测非ASCII字符并通过stdin bytes通道安全提交，还会自动检查暂存区一致性。手动方案是将提交信息写入UTF-8编码（无BOM）的临时文件 `commit-msg.txt`，使用 `-F` 参数提交，或升级到PowerShell 7+。
- **`git add <新目录>`不会自动暂存旧文件删除**：这是git最容易踩的反直觉陷阱之一——当你将一个大文件拆分为包目录时，执行 `git add new_package/` 只会添加新目录下的文件，**不会**自动暂存父目录中原大文件的删除记录。必须显式执行 `git add deleted_old_file.py` 来暂存删除，否则提交后旧文件仍然存在，需要amend修复。
- **git add前检查diff**：原子提交要求"一次提交只做一件事"，在 `git add` 之前务必用 `git diff` 和 `git status --short` 执行三查验证（新增/修改/删除），避免临时调试文件、__pycache__、意外修改的配置文件被混入提交——禁止直接使用 `git add .`。
- **amend只会修改最后一次提交**：`git commit --amend` 只能修改最近一次提交，无法amend更早的commit。如果需要修改更早的提交，必须使用交互式rebase（`git rebase -i`），操作复杂度显著增加，因此提交前务必通过三查验证确认信息正确。
- **Conventional Commits type必须小写**：提交类型必须使用小写（`feat`/`fix`/`docs`/`refactor`/`test`/`chore`/`perf`），大写开头（`Feat`/`Fix`/`Docs`）不符合规范，会被CI检查拦截。
- **空提交需要--allow-empty**：触发CI流水线但无代码变更时（如重新运行失败的CI），需要创建空提交，此时必须添加 `--allow-empty` 参数（`git commit --allow-empty -m "ci: 触发流水线重跑"`），否则Git会拒绝提交。

## 10. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/CI清单） | L2 | [commands/atomic-commit.md](../../commands/atomic-commit.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../rules/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| Windows中文提交工具 | L1工具 | [git-commit-utf8.py](../../scripts/git-commit-utf8.py) | **Windows平台提交中文必用**，自动处理编码，支持-m/-F/--auto |
| 开发规范（提交规范章节） | L2 | [docs/development-standards.md](../../../docs/development-standards.md) | 确认提交规范 |
| CI检查脚本 | L1工具 | [ci-check.ps1](../../scripts/ci-check.ps1) | 重要提交前验证 |
| Git忽略验证 | L1工具 | [check-gitignore.py](../../scripts/check-gitignore.py) | 怀疑有不该提交的文件时 |

## 11. Changelog

- **v1.6.0** (2026-07-06): 新增"批量提交场景重扫描"检查项，解决批量原子提交后工作区残留变更被误判为已处理的隐患。三处同步增强：§5步骤6新增重扫描提示、§6安全检查清单新增批量提交项、L2文档atomic-commit.md步骤5新增第5项验证。基于5次批量原子提交复盘中"4个文件未显示在初始扫描"问题萃取。
- **v1.5.0** (2026-07-05): 新增"fix类型提交专项检查"清单，强制执行"修复即闭环"三阶段SOP（修复→预防→闭环），禁止纯点修复提交。平凡修复（拼写/格式/注释/清理）可豁免但须自查确认。基于SpecWeave 13天全生命周期复盘洞察萃取。
- **v1.4.0** (2026-07-03): 新增"三查暂存法"验证流程（查新增/修改/删除），明确git add新目录不会自动暂存旧文件删除的反直觉陷阱；强化Windows中文提交最佳实践（优先使用UTF-8临时文件法），安全检查清单细化为三查子项和Windows平台双项检查；基于14个大文件批量拆分复盘的经验萃取。
- **v1.3.0** (2026-07-01): 在§4决策树后添加S0 CMD_START强制日志规范，记录触发时的输入参数（files/type/dry_run）便于回溯提交决策；补充第3个Why解释（提交信息写"为什么"而非"做了什么"的原因）。
- **v1.2.2** (2026-07-01): 新增 Windows 编码验证清单项（commit message 含非 ASCII 时必须用 git cat-file 验证存储字节），对应 L2 步骤5 新增 Windows 平台编码陷阱说明与 stdin-bytes 修复方案。
- **v1.2.1** (2026-06-30): 补充Why设计意图解释（禁止git add .的原因），通过质量检查why.explanations≥2要求。
- **v1.2.0** (2026-06-30): 按渐进式披露三层架构重构，将CMD-LOG详细事件表（59行）迁移至L2规范文档，提交类型表压缩为双列，提交示例精简，禁止git add.提示内联到checklist，关键参考表增加层级列。
- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义20个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于atomic-commit命令集封装。
