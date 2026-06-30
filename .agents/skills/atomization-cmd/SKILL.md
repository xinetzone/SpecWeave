---
name: atomization-cmd
version: 1.2.0
description: "当用户提到'原子化'、'拆分文件'、'atomize'、'拆分大文档'、'文件拆分'、'拆分成多个文件'、'单一职责'、'文档重构'、'拆分文档'时，必须使用此技能。提供文档与代码的原子化拆分能力：分析源文件→制定拆分方案→执行拆分→修复链接→收尾验证。不要手动拆分文件——本Skill封装了链接修复、索引更新、一致性检查等必要步骤。"
argument-hint: "<目标类型：document/code/config> <源文件路径>"
user-invocable: true
paths:
  - ".agents/commands/atomization.md"
  - ".agents/scripts/finalize-atomization.py"
  - ".agents/scripts/check-atomization-coverage.py"
  - "docs/standards/cmd-log-specification.md"
---

# Atomization 原子化命令 Skill

> ⚠️ **本Skill是命令入口门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<500行，触发词+决策树+核心步骤+安全清单）
> - L2：[commands/atomization.md](../../commands/atomization.md)（完整流程）+ [cmd-log-specification.md](../../../docs/standards/cmd-log-specification.md)（日志规范）

## 1. Skill ID
`atomization-cmd`

## 2. 功能描述

提供文档与代码的原子化拆分能力，确保拆分后的文件遵循单一职责原则：

| 方案 | 推荐场景 | 优势 |
|------|---------|------|
| **文档原子化** | ⭐ 大文档拆分（如复盘报告、长规范） | 单一主题、易维护、可独立引用 |
| **原子化+收尾** | ⭐ 拆分完成后的一键收尾 | 自动修复断链+更新导航+刷新看板 |
| **原子化预检** | 创建新模式前的覆盖度检查 | 避免重复创建已有模式 |

核心功能：分析源文件结构→制定拆分策略→创建原子文件→迁移内容→更新交叉引用→一键收尾。

> **为什么用本Skill而非手动拆分？** 手动拆分最大的陷阱是链接断裂——文件移动后相对路径错误导致大量断链，修复成本非线性增长（跳过5分钟的规范可能导致30分钟返工）。本Skill配合finalize-atomization.py自动处理链接修复、导航更新、看板刷新。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "原子化"、"拆分"、"atomize"、"拆分文件"
- "拆分大文档"、"拆分大文件"、"文件拆分"、"拆分成多个文件"
- "单一职责"、"文档重构"、"文档拆分"
- "把这个文件拆一下"、"内容太多拆分一下"
- 文档内容超过500行、职责不单一、多个主题混在一起
- 复盘报告需要拆分insights/actions等子模块

> **关于触发**：原子化是高风险操作（涉及文件创建/移动/链接修改），必须使用本Skill确保流程规范。拆分前先用check-atomization-coverage.py预检，拆分后必须用finalize-atomization.py收尾。

## 4. 方案选择决策树

```
需要进行原子化拆分？
├─ 拆分前预检（检查是否已有模式覆盖）？ → 先运行 check-atomization-coverage.py
├─ 拆分文档（Markdown报告/规范等）？ → 文档原子化流程
├─ 拆分完成需要收尾？ → finalize-atomization.py 一键执行
├─ 原子化后需要检查一致性？ → check-atomization-duplication.py 检查残留内容
└─ Git提交原子化结果？ → 拆分完成后使用 atomic-commit-cmd
```

## 5. 快速开始

```
步骤1：读取 [.agents/commands/atomization.md](../../commands/atomization.md) 了解完整流程
步骤2：预检阶段：
   - 运行 check-atomization-coverage.py 确认新内容未被已有模式覆盖
   - 分析源文件的核心主题和结构
   - 确定拆分策略（按主题/功能/模块/组件）
步骤3：制定拆分方案：
   - 规划新文件的命名和目录结构
   - 设计文件间的引用关系
   - 将源文件转为索引页
步骤4：执行拆分：
   - 创建新的原子文件（每个文件单一主题）
   - 添加正确的frontmatter（含source溯源字段）
   - 迁移内容到对应文件
步骤5：收尾阶段（关键！）：
   - 运行 finalize-atomization.py 自动修复断链+更新导航+刷新看板
   - 运行 check-links.py 验证所有链接有效
   - 运行 check-atomization-duplication.py 检查源文件无残留深度内容
```

> 完整RACI矩阵、拆分策略选择指南、frontmatter规范、断链修复规则见L2文档 [commands/atomization.md](../../commands/atomization.md)。

## 6. 安全检查清单（原子化质量门）

- [ ] 拆分前已做coverage预检，确认没有重复创建已有模式
- [ ] 每个新文件遵循单一职责原则（一个文件一个主题）
- [ ] 新文件frontmatter包含source字段（溯源到原始文档）
- [ ] 源文件转为索引页，包含子模块导航链接
- [ ] 文件命名符合规范（英文小写、连字符分隔）
- [ ] **已运行 finalize-atomization.py 收尾**（⚠️ 强制步骤——手动修复链接遗漏率高达40%，自动收尾避免非线性返工）
- [ ] 链接验证通过（check-links.py无断链）
- [ ] 无内容残留（源文件不保留已拆分到子文件的深度内容）
- [ ] 相关README/索引已更新（新增文件出现在目录列表中）

## 7. 执行日志（CMD-LOG）

执行原子化命令集时，必须按 [CMD-LOG规范](../../../docs/standards/cmd-log-specification.md) 输出结构化日志：
- `cmd=atomization`，session前缀 `atom-YYYYMMDD-<filename>`
- 步骤编号 S0-S6（启动→源文件分析→制定方案→执行拆分→更新引用→收尾验证→索引更新）
- 关键特有事件：`PRECHECK_RESULT`、`DUPLICATE_FOUND`、`SPLIT_PLAN`、`OVER_SPLIT_WARN`、`FILE_CREATED`、`LINK_FIXED`、`FINALIZE_RUN`、`BROKEN_LINKS_FOUND`、`RESIDUAL_FOUND`

> 完整字段说明、21个事件表格、日志示例见L2文档 [cmd-log-specification.md §7.4](../../../docs/standards/cmd-log-specification.md)。

## 8. 关键脚本速查

| 脚本 | 层级 | 用途 | 何时使用 |
|------|------|------|---------|
| [check-atomization-coverage.py](../../scripts/check-atomization-coverage.py) | L1工具 | 预检：检查模式库是否已有覆盖 | 拆分前必运行 |
| [finalize-atomization.py](../../scripts/finalize-atomization.py) | L1工具 | 一键收尾：修链接+更新导航+刷看板 | 拆分完成后必运行 |
| [check-atomization-duplication.py](../../scripts/check-atomization-duplication.py) | L1工具 | 检查：源文件残留内容 | 收尾后验证 |
| [check-links.py](../../scripts/check-links.py) | L1工具 | 链接有效性验证 | 收尾后验证 |

## 9. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 完整命令文档（RACI/参数/模板） | L2 | [commands/atomization.md](../../commands/atomization.md) | 每次使用必读 |
| CMD-LOG日志规范 | L2 | [cmd-log-specification.md](../../../docs/standards/cmd-log-specification.md) | 日志格式、事件定义、解析方法 |
| 原子化三标准测试 | L2 | [atomization-three-criteria-test.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/atomization-three-criteria-test.md) | 判断是否需要拆分 |
| 原子化三层分类 | L2 | [atomization-three-tier-classification.md](../../../docs/retrospective/patterns/methodology-patterns/document-architecture/atomization-three-tier-classification.md) | 确定拆分粒度 |

## 10. Changelog

- **v1.2.0** (2026-06-30): 按渐进式披露三层架构重构，将CMD-LOG详细事件表（57行）迁移至L2规范文档，finalize强制提示内联到checklist，关键参考表增加层级列。
- **v1.1.0** (2026-06-29): 添加CMD-LOG结构化日志规范，定义21个关键日志事件。
- **v1.0.0** (2026-06-29): 初始版本（Skill门面），基于atomization命令集封装。
