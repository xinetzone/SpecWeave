---
name: atomic-commit-cmd
version: 1.1.0
description: "当用户提到'提交'、'commit'、'原子提交'、'代码提交'、'提交代码'、'提交变更'、'git commit'、'保存更改'时，必须使用此技能。提供Git原子化提交规范执行能力：检查变更→预提交验证→构建提交信息→执行提交→验证结果。遵循Conventional Commits规范，确保单次提交单一职责。不要直接git commit——本Skill封装了预检查、提交信息格式和验证流程。"
argument-hint: "<提交类型：feat/fix/refactor/test/docs/chore/perf> [scope] <提交信息>"
user-invocable: true
paths:
  - ".agents/commands/atomic-commit.md"
  - ".agents/scripts/ci-check.ps1"
---

# Atomic-Commit 原子提交命令 Skill

> ⚠️ **本Skill是命令入口门面**，详细步骤见 [.agents/commands/atomic-commit.md](../../commands/atomic-commit.md)。
> 门面只做发现和路由，不重复完整流程定义。

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

**提交类型参考**（Conventional Commits）：

| 类型 | 用途 |
|------|------|
| feat | 新功能 |
| fix | Bug修复 |
| refactor | 重构（不改变功能） |
| test | 测试相关 |
| docs | 文档更新 |
| chore | 构建/工具/依赖更新 |
| perf | 性能优化 |

## 5. 快速开始

```
步骤1：读取 [.agents/commands/atomic-commit.md](../../commands/atomic-commit.md) 了解完整流程
步骤2：检查变更范围：
   - git status 查看当前变更
   - 确认变更符合单一职责（只做一件事）
   - 确保没有无关文件混入
步骤3：执行预提交验证：
   - 运行 check-links.py 验证链接（文档变更时）
   - 运行相关检查脚本（文件名/mermaid/vendor等，适用时）
   - 运行单元测试（代码变更时）
   - Windows: ci-check.ps1 做综合检查（重要提交）
步骤4：构建提交信息：
   - 格式：type(scope): subject
   - type: feat/fix/refactor/test/docs/chore/perf
   - scope: 模块或目录（可选）
   - subject: 中文描述"为什么"做这个变更，而非"做了什么"
步骤5：执行提交：
   - git add <相关文件>（不要git add .）
   - git commit -m "type(scope): subject"
步骤6：验证结果：
   - git log -1 确认提交信息正确
   - git status 确认没有遗漏文件
```

## 6. 安全检查清单（提交质量门）

- [ ] 变更范围符合单一职责（一次提交只做一件事）
- [ ] 没有无关文件混入提交
- [ ] 提交信息遵循Conventional Commits格式（type(scope): subject）
- [ ] 提交信息用中文描述"为什么"而非"做了什么"
- [ ] 预提交检查已执行（链接/格式/测试，适用时）
- [ ] 没有提交临时文件（.temp/、__pycache__/、node_modules/等）
- [ ] 没有提交敏感信息（密钥、密码、token等）
- [ ] vendor/目录变更符合子模块管理规范（不直接提交vendor内容）

> **为什么禁止git add .？** git add . 容易把无关文件（临时文件、日志、敏感配置、未完成的实验代码）混入提交，破坏原子性。应该明确指定要提交的文件。

## 7. 执行日志规范（CMD-LOG）

执行原子提交命令集时，必须在关键节点输出结构化日志：

```
[CMD-LOG] | level=<LEVEL> | cmd=atomic-commit | step=<STEP_ID> | event=<EVENT> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<CONTEXT_JSON>
```

**字段说明**：
- `level`：日志级别（INFO/WARN/ERROR/DEBUG）
- `cmd`：固定为 `atomic-commit`
- `step`：当前步骤（S0=启动/S1=检查范围/S2=预提交验证/S3=构建信息/S4=执行提交/S5=结果验证/S6=推送通知）
- `event`：事件类型
- `session`：会话ID（格式：`cmt-YYYYMMDD-<short-hash>`）
- `msg`：人类可读描述
- `ctx`：JSON格式上下文（不含换行）

**必须记录的事件**：

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 命令开始 | INFO | CMD_START | 开始原子提交，类型：<type>，范围：<scope>，文件数：<N> | commit_type, scope, files_staged, verify |
| 进入步骤1 | INFO | STEP_ENTER | 进入步骤1：检查变更范围 | |
| 变更范围检查 | INFO | SCOPE_CHECK | 变更范围检查：<N>个文件，类型：<add/modify/delete> | changed_files, file_types, single_concern（是否单一职责） |
| 发现无关文件 | WARN | UNRELATED_FILES | 发现无关文件混入变更：<文件列表>，需排除 | unrelated_files, action |
| 敏感文件检测 | ERROR | SENSITIVE_FILE | 检测到敏感文件：<文件>，禁止提交！ | sensitive_file, risk_level |
| 临时文件检测 | WARN | TEMP_FILE_FOUND | 检测到临时文件：<文件>，应加入.gitignore | temp_file, recommendation |
| vendor目录变更 | WARN | VENDOR_CHANGE | 检测到vendor/目录变更，需确认是否为子模块更新 | vendor_files, is_submodule_update |
| 步骤1完成 | INFO | STEP_COMPLETE | 步骤1完成：变更范围确认，<N>个文件待提交 | staged_count, scope_status |
| 进入步骤2 | INFO | STEP_ENTER | 进入步骤2：预提交验证 | checks_to_run |
| 验证项通过 | DEBUG | CHECK_PASS | 验证通过：<检查项名称> | check_name, duration |
| 验证项失败 | WARN | CHECK_FAIL | 验证失败：<检查项名称>，错误：<原因> | check_name, error_detail, blocking（是否阻塞） |
| 验证失败阻塞提交 | ERROR | VERIFICATION_BLOCKED | 预提交验证阻塞：<失败项>，需要修复后继续 | failed_checks, fix_required |
| 步骤2完成 | INFO | STEP_COMPLETE | 步骤2完成：<N>项检查通过，<M>项警告 | passed_count, warning_count |
| 进入步骤3 | INFO | STEP_ENTER | 进入步骤3：构建提交信息 | |
| 提交信息构建 | INFO | COMMIT_MSG_BUILT | 提交信息构建完成：<type>(<scope>): <subject> | full_message, commit_type, scope, subject_length |
| 提交信息不合规 | WARN | MSG_NONCOMPLIANT | 提交信息不合规：<问题描述>，建议修正 | issue, suggested_fix |
| 步骤3完成 | INFO | STEP_COMPLETE | 步骤3完成：提交信息已构建 | commit_message |
| 进入步骤4 | INFO | STEP_ENTER | 进入步骤4：执行提交 | |
| 执行提交 | INFO | COMMIT_EXECUTED | 提交执行成功：commit <hash>，<N>个文件变更 | commit_hash, files_committed, insertions, deletions |
| 提交失败 | ERROR | COMMIT_FAILED | 提交执行失败：<错误信息> | error, retry_hint |
| 进入步骤5 | INFO | STEP_ENTER | 进入步骤5：提交结果验证 | |
| 提交验证通过 | INFO | COMMIT_VERIFIED | 提交验证通过：<hash>信息正确，无遗漏文件 | commit_hash, log_verified, status_clean |
| 步骤5完成 | INFO | STEP_COMPLETE | 步骤5完成：提交验证通过 | |
| 命令完成 | INFO | CMD_COMPLETE | 原子提交完成：<type>(<scope>): <subject>，<hash>，总耗时：<duration> | commit_hash, full_message, duration |
| 提交错误 | ERROR | CMD_ERROR | 原子提交错误：<错误描述> | error_type, error_detail, failed_step, recovery_hint |

**日志示例**：

```
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S0 | event=CMD_START | session=cmt-20260629-a3f2b1 | msg=开始原子提交，类型：feat，范围：skills，文件数：6 | ctx={"commit_type":"feat","scope":"skills","files_staged":6,"verify":true}
[CMD-LOG] | level=WARN | cmd=atomic-commit | step=S1 | event=UNRELATED_FILES | session=cmt-20260629-a3f2b1 | msg=发现无关文件混入变更：.temp/debug.log，需排除 | ctx={"unrelated_files":[".temp/debug.log"],"action":"exclude"}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S2 | event=CHECK_PASS | session=cmt-20260629-a3f2b1 | msg=验证通过：check-links.py（0个断链） | ctx={"check_name":"check-links","duration":"5s"}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S3 | event=COMMIT_MSG_BUILT | session=cmt-20260629-a3f2b1 | msg=提交信息构建完成：feat(skills): 新增5个命令集Skill门面增强能力发现 | ctx={"full_message":"feat(skills): 新增5个命令集Skill门面增强能力发现","commit_type":"feat","scope":"skills","subject_length":22}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S4 | event=COMMIT_EXECUTED | session=cmt-20260629-a3f2b1 | msg=提交执行成功：commit a3f2b1c，6个文件变更 | ctx={"commit_hash":"a3f2b1c","files_committed":6,"insertions":280,"deletions":12}
[CMD-LOG] | level=INFO | cmd=atomic-commit | step=S6 | event=CMD_COMPLETE | session=cmt-20260629-a3f2b1 | msg=原子提交完成：feat(skills): 新增5个命令集Skill门面增强能力发现，a3f2b1c，总耗时：约3分钟 | ctx={"commit_hash":"a3f2b1c","full_message":"feat(skills): 新增5个命令集Skill门面增强能力发现","duration":"~3min"}
```

> **为什么需要日志？** 提交是最容易"出错但事后难查"的操作——为什么这个文件被提交了？为什么提交信息不规范？预提交检查过了吗？日志记录了从变更检查到提交验证的完整链路，可以精确回答"当时发生了什么"。

## 8. 提交信息示例

✅ 好的提交信息：
```
feat(skills): 新增5个命令集Skill门面增强能力发现
fix(links): 修复原子化后相对路径错误导致的断链
docs(sop): 沉淀三角验证法为可复用SOP文档
```

❌ 不好的提交信息：
```
update
fix
提交代码
更新了一些东西
```

## 9. 关键参考

| 参考 | 路径 | 何时查阅 |
|------|------|---------|
| 完整命令文档 | [.agents/commands/atomic-commit.md](../../commands/atomic-commit.md) | 每次使用必读 |
| CMD-LOG日志规范 | [cmd-log-specification.md](../../../docs/standards/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 开发规范（提交规范章节） | [docs/development-standards.md](../../../docs/development-standards.md) | 确认提交规范 |
| CI检查脚本 | [ci-check.ps1](../../scripts/ci-check.ps1) | 重要提交前验证 |
| Git忽略验证 | [check-gitignore.py](../../scripts/check-gitignore.py) | 怀疑有不该提交的文件时 |

## 10. Changelog

- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义20个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于atomic-commit命令集封装。
