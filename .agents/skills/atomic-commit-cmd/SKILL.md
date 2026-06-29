---
name: atomic-commit-cmd
version: 1.0.0
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

## 7. 提交信息示例

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

## 8. 关键参考

| 参考 | 路径 | 何时查阅 |
|------|------|---------|
| 完整命令文档 | [.agents/commands/atomic-commit.md](../../commands/atomic-commit.md) | 每次使用必读 |
| 开发规范（提交规范章节） | [docs/development-standards.md](../../../docs/development-standards.md) | 确认提交规范 |
| CI检查脚本 | [ci-check.ps1](../../scripts/ci-check.ps1) | 重要提交前验证 |
| Git忽略验证 | [check-gitignore.py](../../scripts/check-gitignore.py) | 怀疑有不该提交的文件时 |

## 9. Changelog

- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于atomic-commit命令集封装。
