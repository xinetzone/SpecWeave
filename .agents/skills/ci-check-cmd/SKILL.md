---
name: ci-check-cmd
version: 1.2.0
description: "当用户提到'CI检查'、'提交前检查'、'综合检查'、'ci-check'、'流水线检查'、'提交门禁'、'全量检查'、'跑一下CI'、'pre-commit'、'预检'、'检查所有'时，必须使用此技能。提供项目CI/CD综合检查能力，按标准流水线顺序执行10项核心检查：仓库合规→链接检查→Spec一致性→模式成熟度→文档生成→重复代码检测→阶段守卫日志→SG仪表盘→文件放置校验→.temp生命周期检查。提交前必跑，确保代码符合项目规范。不要手动逐个执行检查脚本——本Skill已按正确顺序编排，并处理了跨平台兼容（Windows用.ps1，Linux/Mac用.sh）。"
argument-hint: "[--quick] [--skip <step1,step2>]"
user-invocable: true
paths:
  - ".agents/scripts/ci-check.ps1"
  - ".agents/scripts/ci-check.sh"
  - ".agents/scripts/repo-check.py"
  - ".agents/scripts/check-links.py"
  - ".agents/scripts/docgen.py"
  - ".agents/scripts/check-duplication.py"
  - ".agents/scripts/check-stage-guardrails.py"
  - ".agents/scripts/generate-sg-dashboard.py"
  - ".agents/scripts/check-file-placement.py"
  - ".agents/scripts/check-temp-lifecycle.py"
  - ".agents/scripts/lib/checks/file_placement.py"
  - ".agents/scripts/lib/checks/temp_lifecycle.py"
title: "CI 综合检查命令 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/ci-check-cmd/SKILL.toml"
---
# CI 综合检查命令 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+核心步骤+安全清单）
> - L2：各检查脚本源码（`--help` 输出详细参数）

## 1. Skill ID
`ci-check-cmd`

## 2. 功能描述

项目CI/CD流水线综合检查工具，按标准顺序执行10项核心检查，模拟CI流水线完整流程：

| 步骤 | 检查项 | 阻断级别 | 底层脚本 |
|------|--------|---------|---------|
| 1/10 | 仓库合规（gitignore+vendor+mermaid+filename+roles） | 🔴 FAIL阻断 | repo-check.py all |
| 2/10 | Markdown链接有效性 | 🔴 FAIL阻断 | check-links.py |
| 3/10 | Spec一致性检查 | 🟡 WARN不阻断 | spec-tool.py check |
| 4/10 | 模式成熟度检查 | 🔴 FAIL阻断 | pattern-maturity.py check |
| 5/10 | 文档生成（导航+看板+应用清单） | 🔴 FAIL阻断 | docgen.py all |
| 6/10 | 跨文件重复代码检测 | 🟡 WARN不阻断 | check-duplication.py |
| 7/10 | 阶段守卫日志合规（strict模式） | 🔴 FAIL阻断 | check-stage-guardrails.py --strict |
| 8/10 | SG可视化仪表盘生成 | 🟡 WARN不阻断 | generate-sg-dashboard.py |
| 9/10 | 关键配置文件放置校验 | 🔴 FAIL阻断 | lib/checks/file_placement.py（封装 check-file-placement.py） |
| 10/10 | .temp/ 生命周期检查（>14d WARN / >30d ERROR） | 🟡🟰 分级 | lib/checks/temp_lifecycle.py（封装 check-temp-lifecycle.py，只读） |

> **步骤 9-10 分级策略**：步骤 9（文件放置）错误放置即 🔴 阻断；步骤 10（.temp 生命周期）采用 CI 统一年龄阈值——超 14 天 🟡 警告（不阻塞）、超 30 天 🔴 错误（阻塞），与底层脚本的"用途保留期"策略（backup 3天/experiments·exports·screenshots 14天/未分类 7天）独立。

**幂等性与安全性**：
- 所有检查步骤（1-4、6-10）均为只读操作，不修改任何文件
- 步骤5（文档生成）是写操作，但仅覆盖标记区域（幂等，多次运行结果相同），标记外人工内容不受影响
- 步骤7、8在无日志文件时自动SKIP，不会报错
- 步骤10为只读检查，不自动清理（清理需手动执行 `check-temp-lifecycle.py --clean`）
- 整体可安全重复执行

> **为什么用本Skill而非手动逐个跑检查？** 手动跑检查有三个风险：一是顺序错误（应先生成文档再检查链接，但反过来先检查链接再生成文档会产生误报）；二是遗漏检查项（8个步骤容易忘跑某几个）；三是跨平台差异（Windows用PowerShell、Linux/Mac用Bash，参数编码处理不同）。本Skill按CI验证过的正确顺序编排，自动处理平台差异，一次执行全量覆盖。

## 3. 何时使用本技能

### 必用场景
- **提交代码前**（pre-commit预检）：确保所有检查通过后再commit/push
- **PR/MR合并前**：作为合并门禁验证
- **重构/大范围修改后**：验证没有引入规范违规
- **发布前最终检查**：确保主干分支质量

### 触发词
- "CI检查"、"提交前检查"、"综合检查"、"ci-check"
- "流水线检查"、"提交门禁"、"全量检查"
- "跑一下CI"、"pre-commit"、"预检"、"检查所有"

## 4. 方案选择决策树

```
需要执行项目检查？
├─ 只想快速检查最关键的阻断项？ → --quick模式（仅1/2/4/7）
├─ 需要跳过某些已知问题步骤？ → --skip <steps>
└─ 完整CI流程（推荐提交前使用） → 全量10步
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `ci-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=ci-check | step=S0 | event=CMD_START | session=ci-... | msg=开始CI综合检查：<简述> | ctx={"target_path":"..."}
```

> **为什么决策前必须记录日志？** CI检查包含10项流水线，失败时需要知道具体检查范围，CMD_START记录目标路径便于回溯。

| 方案 | 适用场景 | 命令（Windows） | 命令（Linux/Mac） |
|------|---------|----------------|------------------|
| **全量检查** ⭐ | 提交前/合并前，完整CI流程 | `powershell -ExecutionPolicy Bypass -File .agents/scripts/ci-check.ps1` | `bash .agents/scripts/ci-check.sh` |
| **快速检查** | 开发中快速验证关键项 | 分步执行关键检查（见§5.2） | 同左 |
| **跳过特定步骤** | 已知某步骤暂时无法通过 | 手动分步执行并跳过对应步骤 | 同左 |

> **为什么用PowerShell/Bash直接调用而非python包装？** ci-check.py不存在——ci-check以.ps1和.sh双平台脚本形式提供，因为它需要协调Python脚本调用、处理退出码、输出彩色日志、设置UTF-8编码等Shell级操作，这些在纯Python中处理跨平台差异更复杂。

## 5. 核心执行步骤

### 5.1 全量检查（推荐）

**Windows（PowerShell）**：
```powershell
powershell -ExecutionPolicy Bypass -File .agents/scripts/ci-check.ps1
```

**Linux/Mac（Bash）**：
```bash
bash .agents/scripts/ci-check.sh
```

执行后观察输出：
- ✅ 所有步骤显示 `PASS` → 可安全提交
- ❌ 某步骤显示 `ERROR` 并退出 → 修复对应问题后重新运行
- ⚠️ 某步骤显示 `WARN` → 建议修复但不阻断提交

### 5.2 快速检查模式（开发中快速反馈）

如果开发中不想跑全量10步（尤其步骤5会生成文档可能产生diff干扰），可手动执行关键阻断项：

```bash
# 1. 仓库合规检查
python .agents/scripts/repo-check.py all
# 2. 链接检查
python .agents/scripts/check-links.py
# 4. 模式成熟度
python .agents/scripts/pattern-maturity.py check
# 6. 重复代码
python .agents/scripts/check-duplication.py
```

> 步骤5（文档生成）和步骤3（Spec一致性）、7、8可在提交前最后一次全量跑时再执行。

### 5.3 常见阻断问题快速定位

| 阻断步骤 | 常见问题 | 对应Skill/工具 |
|---------|---------|---------------|
| 1/10 mermaid检查 | Mermaid语法违规（空行/无引号文本） | mermaid-cmd（检查修复方案） |
| 2/10 链接检查 | 断链/路径错误 | link-check-cmd（--fix自动修复） |
| 4/10 模式成熟度 | 模式文档元数据缺失 | docs/retrospective/patterns/ |
| 5/10 文档生成 | 标记区域缺失/frontmatter格式错 | docgen-cmd（nav子命令） |
| 6/10 重复代码 | 跨文件重复逻辑≥10行 | 提取到.agents/scripts/lib/ |
| 7/10 阶段守卫日志 | SG-LOG/PDR-LOG违规 | check-stage-guardrails.py分析 |
| 9/10 文件放置校验 | 受管配置文件被错误放置到根目录 | `git mv` 到 .agents/scripts/（见 check-file-placement.py --fix-hint） |
| 10/10 .temp生命周期 | .temp/ 内容超30天 / 命名不合规 | `python check-temp-lifecycle.py --clean` 清理过期项 |

## 6. 安全检查清单（执行前确认）

- [ ] Git工作区已提交或有备份（步骤5会更新文档标记区域，虽然幂等但建议有回滚点）
- [ ] 没有正在编辑的未保存文件（避免生成文档时与手动编辑冲突）
- [ ] 理解快速模式和全量模式的区别，开发中用快速模式、提交前用全量模式
- [ ] 如果某个WARN项确认是误报或暂时无法修复，记录原因后再跳过
- [ ] 全量检查通过后再执行commit/push，不要跳过FAIL项强行提交
- [ ] 新脚本提交前额外确认步骤6（重复代码检查）无WARN，已有共享函数已复用

> **为什么区分FAIL阻断和WARN不阻断？** 并非所有问题都需要立即修复——断链、模式成熟度缺失是硬性质量问题，必须修复才能保证文档可用性；而重复代码是代码质量建议，新创建的模式可能暂时处于L1成熟度，这些可以记录后后续迭代。一刀切全部阻断会降低开发效率，全部不阻断又会导致质量滑坡，分级机制平衡了质量和效率。

## 7. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| PowerShell执行策略阻止 | Windows默认限制脚本执行 | 使用 `-ExecutionPolicy Bypass` 参数 |
| 步骤5生成文档后产生意外diff | 标记区域内有手动编辑内容 | 将手动内容移到标记区域外，再重新执行 |
| 步骤7找不到日志文件SKIP | 本次会话未产生阶段守卫日志 | 正常现象，不影响检查结果 |
| UTF-8编码乱码 | PowerShell 5默认编码非UTF-8 | 脚本已自动设置编码，如仍乱码改用PowerShell 7+ |
| 步骤6检测到重复代码 | 新脚本复制了其他脚本的逻辑 | 参考 `.agents/scripts/lib/README.md` 提取到共享库 |

## 8. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **Windows用.ps1/Linux用.sh**：跨平台脚本不通用，不要在Windows的Git Bash/WSL中运行 `.ps1` 脚本，也不要在PowerShell中运行 `.sh` 脚本——PowerShell用 `powershell -ExecutionPolicy Bypass -File .agents/scripts/ci-check.ps1`，Linux/Mac用 `bash .agents/scripts/ci-check.sh`。
- **步骤失败后必须检查$LASTEXITCODE**：PowerShell默认不会在命令失败时自动终止后续脚本执行——一个步骤失败后脚本仍会继续运行下一个步骤，可能导致"前面失败了但后面还在跑"的误导性输出，必须检查每个步骤的退出码。
- **--quick模式跳过文档生成和重复检测**：`--quick` 模式仅运行最关键的4个阻断项（仓库合规/链接/模式成熟度/阶段守卫），跳过文档生成（步骤5）和重复代码检测（步骤6）——开发中快速预检可用，但提交前必须跑全量检查。
- **docgen步骤会修改文件**：步骤5（文档生成）是写操作，会更新导航表、看板、应用清单等标记区域——这是预期行为，不属于"意外修改"，生成的diff需要正常提交，不要回滚这些变更。
- **check-skill-quality阈值70分**：模式成熟度检查的通过阈值是70分，不是0分才通过——低于70分的模式文档会阻断流水线，新创建的模式应至少达到L1成熟度（元数据完整+基本描述）。

## 9. 与其他Skill的协作

| 协作场景 | 配合Skill | 协作方式 |
|---------|----------|---------|
| 链接检查失败 | link-check-cmd | ci-check步骤2失败后，用link-check-cmd --fix自动修复 |
| Mermaid检查失败 | mermaid-cmd | ci-check步骤1中mermaid失败后，用mermaid-cmd检查修复方案 |
| 文档生成后需要更新导航 | docgen-cmd | ci-check步骤5已包含docgen all，单独更新时用docgen-cmd |
| 原子化操作收尾 | atomization-finalize-cmd | 原子化后先finalize再跑ci-check |
| 提交代码 | atomic-commit-cmd | ci-check全量通过后，用atomic-commit-cmd原子提交 |

## 10. Changelog

- **v1.2.0** (2026-07-18): 新增步骤 9（关键配置文件放置校验，🔴 FAIL阻断）与步骤 10（.temp/ 生命周期检查，>14天 WARN / >30天 ERROR 分级）；底层通过 `lib/checks/file_placement.py` 与 `lib/checks/temp_lifecycle.py` 模块封装 `check-file-placement.py` / `check-temp-lifecycle.py`；同步更新 frontmatter paths、检查项表格（8→10 项）、阻断问题定位表。来源：config-file-placement-governance spec Task 4。
- **v1.1.0** (2026-07-01): 在§4决策树后添加S0 CMD_START强制日志规范，记录触发时的输入参数（target_path）便于回溯检查范围；补充第3个Why解释（FAIL/WARN分级阻断的必要性）。
- **v1.0.0** (2026-06-30): 初始版本，基于ci-check.ps1/ci-check.sh双平台脚本封装为命令门面Skill，包含8项流水线检查。
