---
id: "atomic-commit"
title: "原子提交指令集"
source: "AGENTS.md#原子提交指令"
x-toml-ref: "../../.meta/toml/.agents/commands/atomic-commit.toml"
---
# 原子提交指令集

## 触发条件

- 代码修改完成，需要提交
- 文档变更完成，需要提交
- 配置更新完成，需要提交
- 功能开发完成，需要提交
- 修复问题完成，需要提交

## 输入规范

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| commit_type | string | 是 | 提交类型：`feat`/`fix`/`refactor`/`test`/`docs`/`chore`/`perf` |
| scope | string | 否 | 提交范围：模块或文件路径 |
| message | string | 是 | 提交信息主体（中文描述"为什么"） |
| files | list | 是 | 要提交的文件列表 |
| verify | boolean | 否 | 是否执行预提交验证，默认 `true` |

## RACI责任分配矩阵

**RACI模型说明**：
- **R** = 负责执行（Responsible）：实际完成工作的角色
- **A** = 最终审批（Accountable）：对结果负最终责任，拥有最终决策权，每项活动有且仅有一个A
- **C** = 需咨询（Consulted）：决策前需征求意见、提供专业输入的角色，双向沟通
- **I** = 需知会（Informed）：决策后需告知进展与结果的角色，单向沟通

| 原子提交核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 触发提交与变更确认 | **R/A** | I | C | I | I | I |
| 变更范围检查（步骤1） | R | I | C | **A** | I | I |
| 预提交验证（步骤2：链接/格式/测试） | I | C | R | **A** | C | I |
| 提交信息构建（步骤3） | **R/A** | I | C | C | I | I |
| 执行提交（步骤4） | I | I | **R** | **A** | I | I |
| 提交验证（步骤5） | R | I | C | **A** | I | I |
| 推送与通知（步骤6） | **R/A** | I | I | I | I | I |
| 提交质量验收 | C | I | C | **R/A** | I | I |
| 强制跳过hooks/--no-verify审批 | I | I | I | C | I | **A**¹ |

> ¹ 禁止常规使用，仅紧急情况下经co-founder审批后方可执行，须记录原因

### 审批权限边界

- **常规原子提交**：developer执行提交，reviewer审查变更范围与质量
- **预提交验证失败时强制提交**：必须co-founder审批，且在提交信息中记录原因
- **提交信息格式**：orchestrator指导规范执行，reviewer验收格式合规性
- **是否推送远程**：orchestrator决策，developer执行推送操作
- **代码提交涉及架构变更**：architect需参与咨询（C），reviewer执行架构合规性审查

## 执行步骤

### 步骤 1：检查变更范围（三查暂存法）

- 查看当前工作区变更（`git status --short`）
- **三查验证**（必须逐项确认）：
  1. ✅ **查新增文件（A）**：确认所有新增文件都是本次需要提交的，排除 __pycache__/、*.pyc、.temp/ 等构建产物和临时文件
  2. ✅ **查修改文件（M）**：确认所有修改文件都属于本次单一职责范围，无无关变更混入
  3. ✅ **查删除文件（D）**：确认所有删除记录都已暂存——**注意**：`git add <新目录>` 不会自动暂存父目录中同名旧文件的删除记录，必须显式 `git add` 删除的旧文件
- 确认文件变更符合单一职责原则
- 评估变更影响范围
- 确保没有无关文件混入

### 步骤 2：执行预提交验证

- 运行文件名规范检查
- 运行链接有效性检查
- 运行代码格式检查（如适用）
- 运行单元测试（如适用）

### 步骤 3：构建提交信息

- 遵循 Conventional Commits 规范
- 格式：`<type>(scope): subject`
- subject 使用中文描述"为什么"而非"做了什么"
- 包含相关 Issue 或任务引用

### 步骤 4：执行提交

- 添加指定文件到暂存区
- 执行 git commit
- 记录提交哈希值
- 更新变更日志（如适用）

### 步骤 5：验证提交

- 确认提交成功
- 验证提交信息格式正确
- 检查提交文件列表符合预期
- 记录提交到变更历史

> ⚠️ **Windows 平台编码处理（commit message 含非 ASCII 字符时强制）**：
>
> **最佳方案（优先使用）**：使用项目内置的 `git-commit-utf8.py` 工具，自动检测编码并安全提交：
> ```powershell
> python .agents/scripts/git-commit-utf8.py -m "type(scope): 中文提交标题和正文" <file1> <file2>
> ```
> 该工具自动完成：非ASCII检测→bytes通道提交→暂存区一致性检查，无需手动处理编码问题。
>
> **手动方案（无Python环境时）**：将commit message写入UTF-8编码（无BOM）的临时文件，使用 `-F` 参数提交：
> ```powershell
> [System.IO.File]::WriteAllText("commit-msg.txt", $msg, (New-Object System.Text.UTF8Encoding $false))
> git commit -F commit-msg.txt
> Remove-Item commit-msg.txt
> ```
>
> **编码验证（必须执行）**：提交后**必须**用 `git cat-file -p HEAD` 验证存储字节，若发现乱码，改用 stdin-bytes 方式修复。
>
> 详见 [git-commit-utf8.py](../../scripts/git-commit-utf8.py) 和 [insight-windows-git-encoding-20260701.md](../../docs/retrospective/insights/insight-windows-git-encoding-20260701.md)。

### 步骤 6：推送（如需要）

- 如果配置了自动推送，则推送至远程
- 通知相关角色提交完成
- 更新任务状态
- 同步至自我复盘模块

## 输出规范

| 产出物 | 格式 | 说明 |
|--------|------|------|
| Git 提交 | commit | 包含变更的原子提交 |
| 提交信息 | string | Conventional Commits 格式 |
| 提交哈希 | string | 用于追溯的唯一标识 |
| 变更日志 | Markdown | 更新的 CHANGELOG.md |

## 质量验收

- 提交遵循 Conventional Commits 规范
- 提交信息主体使用中文描述"为什么"
- 单次提交只包含一个逻辑变更
- 预提交验证全部通过
- 提交文件与预期一致，无遗漏或多余

## 约束条件

- 单次提交必须符合单一职责原则
- 禁止将多个不相关变更合并到一个提交
- 提交信息必须清晰描述变更原因
- 必须通过预提交验证才能提交
- 禁止跳过 hooks（--no-verify）

## 提交类型规范

| 类型 | 用途 | 示例 |
|------|------|------|
| feat | 新功能 | `feat(auth): 添加 JWT 认证支持` |
| fix | 修复缺陷 | `fix(api): 修复用户列表分页错误` |
| refactor | 重构代码 | `refactor(utils): 优化字符串处理逻辑` |
| test | 添加测试 | `test(auth): 增加登录流程测试用例` |
| docs | 文档更新 | `docs(readme): 更新安装指南` |
| chore | 杂务工作 | `chore(deps): 更新依赖版本` |
| perf | 性能优化 | `perf(parser): 提升解析速度 30%` |

## 原子提交原则

- **单一职责**：每个提交只做一件事
- **可追溯**：提交信息清晰描述变更原因
- **可回滚**：单个提交可以安全回滚
- **可审查**：提交大小适中，便于代码审查
- **可复用**：便于 cherry-pick 到其他分支

## 关联资源

- [自我迭代模块](../modules/self-iteration.md)
- [自我验证模块](../modules/self-verification.md)
- [代码审查工作流](../workflows/code-review.md)