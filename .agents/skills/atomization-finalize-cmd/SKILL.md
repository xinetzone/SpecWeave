---
name: atomization-finalize-cmd
version: 1.1.0
description: "当用户提到'原子化收尾'、'finalize atomization'、'文档拆分完成'、'文件移动后处理'、'断链修复导航更新'、'一键收尾'、'重构完成后整理'时，必须使用此技能。原子化/文件移动/目录重构后的一键收尾工具：自动断链修复→导航表更新→Spec看板刷新→验证摘要。不要手动逐个执行后处理步骤——本Skill封装了正确的执行顺序和dry-run预览机制，是文档原子化工作流的标准最后一步。"
argument-hint: "[--dry-run] [--no-links] [--no-nav] [--no-dashboard] [--target <dir>]"
user-invocable: true
paths:
  - ".agents/scripts/finalize-atomization.py"
  - ".agents/commands/atomization.md"
title: "Atomization Finalize 原子化一键收尾 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/atomization-finalize-cmd/SKILL.toml"
---
# Atomization Finalize 原子化一键收尾 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心命令+安全清单）
> - L2：脚本源码 [finalize-atomization.py](../../scripts/finalize-atomization.py) + [commands/atomization.md](../../commands/atomization.md)（完整规范）

## 1. Skill ID
`atomization-finalize-cmd`

## 2. 功能描述

原子化拆分、文件移动、目录重构后的**标准一键收尾工具**，按正确顺序自动执行三个后处理步骤：

| 步骤 | 功能 | 底层脚本 |
|------|------|---------|
| **步骤1：断链修复** | 自动检测并修复相对路径错误、绝对路径转换 | check-links.py --fix |
| **步骤2：导航更新** | 重新生成 README.md / docs/README.md 文档导航表 | docgen.py nav |
| **步骤3：看板刷新** | 更新 .trae/specs/ 执行进度看板和根README状态 | docgen.py dashboard |

提供两种执行模式：

| 模式 | 推荐场景 | 优势 |
|------|---------|------|
| **预览模式（--dry-run）** | ⭐ 首次执行、验证收尾范围 | 零风险，展示将要执行的所有操作 |
| **实际执行** | ⭐ 预览确认后正式收尾 | 一键完成，输出验证摘要 |

> **为什么用本Skill而非手动执行三个脚本？** 文档原子化后有三个高频遗留问题：断链、导航过时、看板不准。手动逐个执行容易遗漏步骤或顺序错误（比如先更新导航再修复链接，导致导航表引用了断链）；本Skill封装了经过验证的执行顺序（链接→导航→看板），且每步都有错误捕获和状态报告，确保收尾质量可预测。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "原子化收尾"、"finalize atomization"、"一键收尾"、"收尾工作"
- "文档拆分完成"、"文件移动后处理"、"目录重构后整理"
- "断链修复导航更新"、"更新链接和导航"、"刷新看板"
- 使用 atomization-cmd 完成原子化拆分后
- 提到 `finalize-atomization.py` 脚本

> **关于触发**：原子化拆分是高频操作，但"拆分完就完了"是最常见的遗漏——忘记收尾会导致断链、过时导航、看板状态错误，这些问题会在后续使用中陆续暴露且难以追溯来源。只要完成了文件移动/拆分/重构，就应该使用本Skill收尾，不要等到出问题才补救。

## 4. 方案选择决策树

```
完成了文件移动/原子化/目录重构？
├─ 首次执行，不确定影响范围？ → 预览模式（--dry-run，第5.1节）
├─ 预览确认无误？ → 实际执行（第5.2节）
├─ 只做了小范围文件重命名，导航/看板不受影响？ → 加 --no-nav --no-dashboard 只修链接
├─ 链接已经用 link-check-cmd 单独修过了？ → 加 --no-links 跳过链接修复
└─ 只是单个Spec目录的变更，不需要全项目扫描？ → --target <目录> 指定目标
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `fin-YYYYMMDD-<topic>`）：
```
[CMD-LOG] | level=INFO | cmd=atomization-finalize | step=S0 | event=CMD_START | session=fin-... | msg=开始原子化收尾：<简述> | ctx={"target_dir":"..."}
```

> **为什么决策前必须记录日志？** 收尾操作涉及断链修复和索引更新，影响范围广，CMD_START记录目标目录便于回溯变更范围。

**执行原则**：必须先用 `--dry-run` 预览，确认修复范围符合预期再实际执行。

> **为什么顺序是「链接→导航→看板」不能乱？** 导航表和看板都包含文件链接，如果先生成导航再修链接，导航表中会写入断链路径；反过来，先修复链接确保所有路径正确，再生成导航和看板才能保证引用一致性。这就像装修——先修好水电（链接是基础设施），再刷墙铺地（导航/看板是表层展示）。

## 5. 核心命令（快速开始）

脚本路径：[finalize-atomization.py](../../scripts/finalize-atomization.py)

### 5.1 预览模式（推荐首次执行）

```bash
cd d:\spaces\SpecWeave

# 全项目预览（不修改任何文件，强烈推荐先执行）
python .agents/scripts/finalize-atomization.py --dry-run

# 指定目录预览（只扫描目标目录及其相关引用）
python .agents/scripts/finalize-atomization.py --dry-run --target docs/retrospective/
```

### 5.2 实际执行（预览确认后）

```bash
# 完整收尾（链接修复 + 导航更新 + 看板刷新）
python .agents/scripts/finalize-atomization.py

# 指定目录收尾
python .agents/scripts/finalize-atomization.py --target .agents/skills/
```

### 5.3 跳过部分步骤

```bash
# 只修复链接，跳过导航和看板（小范围重命名场景）
python .agents/scripts/finalize-atomization.py --no-nav --no-dashboard

# 只更新导航和看板，链接已人工确认
python .agents/scripts/finalize-atomization.py --no-links

# 只刷新看板（Spec状态变更但无文件移动）
python .agents/scripts/finalize-atomization.py --no-links --no-nav
```

### 5.4 收尾后验证

实际执行成功后，脚本会提示进一步验证命令：

```bash
# 完整链接检查（确认零断链）
python .agents/scripts/check-links.py

# 全量CI检查（所有质量门禁）
python .agents/scripts/ci-check.ps1
```

> 完整参数说明见脚本源码 `--help` 输出。

## 6. 各步骤详情

| 步骤 | 做什么 | 不做什么 | 失败处理 | 幂等性 |
|------|--------|---------|---------|--------|
| 断链修复 | 修复相对路径层级、file:///转相对、斜杠补全 | 不删除不存在的文件引用（标注为需人工处理） | 输出"需人工处理"清单，不阻断后续步骤 | 已修复路径不再重复修改 |
| 导航更新 | 扫描docs/和根目录.md，更新README.md导航表 | 不修改导航表以外的内容 | 报告错误，继续执行看板步骤 | 基于当前文件状态重新生成，幂等 |
| 看板刷新 | 扫描.trae/specs/，更新根README.md中的看板区域 | 不修改Spec文件本身 | 报告错误 | 基于当前Spec状态重新生成，幂等 |

> 链接修复的详细能力说明见 [link-check-cmd](../link-check-cmd/SKILL.md) 第6节。

## 7. 安全检查清单（执行前逐项确认）

- [ ] Git工作区已提交或有备份（防止意外修改可回滚）
- [ ] **已执行 `--dry-run` 预览**，确认修复范围和变更文件列表符合预期
- [ ] 预览中"需人工处理"的断链数量在预期内（文件删除导致的断链是正常的）
- [ ] 指定了正确的 `--target`（如适用），避免全项目扫描
- [ ] 明确知道哪些步骤被跳过（如使用了 --no-* 参数）
- [ ] 执行后重新运行检查模式确认无遗留问题
- [ ] 如有重大变更，考虑运行完整CI检查

> **为什么执行前必须要求Git工作区有备份？** 虽然finalize脚本是幂等的且只修改标记区域，但断链自动修复涉及多个文件的路径替换——在复杂场景（如跨目录移动、符号链接、特殊字符文件名）下，自动修复有极低概率产生非预期修改。有Git备份意味着可以用`git checkout .`一键回滚，把"可能出问题"的风险降到零成本回滚。

## 8. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| 大量"无法自动修复"的断链 | 目标文件确实已被删除 | 人工确认：删除的文件需要移除引用，移动的文件需要检查路径 |
| 导航表更新后格式错乱 | 手动修改过导航表区域标记 | 检查导航表是否被 `<!-- nav-start -->`/`<!-- nav-end -->` 标记包裹 |
| 看板更新不反映最新状态 | Spec文件frontmatter缺失status字段 | 检查对应spec.md的TOML frontmatter |
| 跨盘符引用无法修复 | Windows环境限制 | 人工处理，考虑统一盘符或使用绝对路径白名单 |
| 子进程调用失败 | Python环境或依赖问题 | 单独执行底层脚本（check-links.py/docgen.py）定位具体错误 |

> 脚本输出采用彩色编码：绿色✓是成功，黄色⚠是警告（需关注但不阻断），红色✗是失败。

## 9. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **必须在atomization-cmd完成后立即运行**：不要在原子化拆分和收尾之间插入其他文件编辑操作，否则会导致文件状态不一致，断链修复可能基于过时的文件树进行。原子化完成后应第一时间执行收尾。
- **dry-run预览不会修改任何文件**：首次运行务必先加`--dry-run`参数，脚本只会输出将要执行的操作和变更文件列表，不会实际写入磁盘。确认变更范围符合预期后再去掉dry-run正式执行。
- **断链修复会自动调整相对路径层级**：自动修复`../`层级和斜杠方向时，可能因复杂目录结构产生非预期路径。修复完成后必须人工抽查几个关键链接，确认路径跳转正确。
- **docgen会更新所有导航表**：导航更新会扫描docs/和根目录并重新生成所有标记区域内的导航表，这属于预期变更，需要一并提交。不要因为"怎么改了这么多文件"而惊讶——这是设计行为。
- **收尾验证失败时需回滚到原子化前状态**：如果最终验证发现大面积断链或导航错乱，不要在错误状态上继续尝试修复。使用`git checkout .`回滚所有变更，分析问题原因后重新原子化和收尾。

## 10. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 脚本源码（完整参数） | L2 | [finalize-atomization.py](../../scripts/finalize-atomization.py) | 需要高级参数或排障时 |
| 原子化命令规范 | L2 | [commands/atomization.md](../../commands/atomization.md) | 理解原子化完整工作流 |
| 链接检查Skill | L1 | [link-check-cmd](../link-check-cmd/SKILL.md) | 单独执行链接检查/修复时 |
| 文档生成Skill | L1 | [docgen-cmd](../docgen-cmd/SKILL.md) | 单独更新导航/看板时 |
| 共享工具库 | L2 | [scripts/lib/](../../scripts/lib/) | 理解底层实现 |

## 11. Changelog

- **v1.1.0** (2026-07-01): 在§4决策树后添加S0 CMD_START强制日志规范，记录触发时的输入参数（target_dir）便于回溯变更范围；补充第3个Why解释（Git工作区备份的必要性）。
- **v1.0.0** (2026-06-30): 初始版本，基于finalize-atomization.py脚本封装为命令门面Skill，遵循五要素模型和渐进式披露三层架构。
