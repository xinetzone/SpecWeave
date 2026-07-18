---
version: "1.0"
id: "retro-idl-wiki-tutorial-20260704"
title: "IDL Wiki 教程创建复盘"
source: "spec:create-idl-wiki-tutorial"
category: retrospective
type: project-reports
tags: ["retrospective", "idl-wiki", "spec-driven", "parallel-subagent", "link-verification"]
date: "2026-07-04"
status: "stable"
author: "SpecWeave"
summary: "IDL Wiki 教程创建过程的四步复盘：事实收集→过程分析→洞察提炼→行动项，聚焦并行 sub-agent 协调与链接验证"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/reports/project-reports/idl-wiki-tutorial-retro-20260704.toml"
---
# IDL Wiki 教程创建复盘

> 本文档是 IDL（接口定义语言）Wiki 教程创建任务的复盘报告，遵循"事实→分析→洞察→行动"四步法，聚焦 spec-driven 开发模式下的并行 sub-agent 协调问题与链接验证机制。

## 任务背景

- **触发**：用户要求创建全面的 IDL 概念与应用 wiki 教程，覆盖定义、语法、规范、工具链、案例、与现代格式对比六大要点
- **执行日期**：2026-07-04 单日完成
- **执行模式**：Spec-driven development（先 spec 后实施）
- **协作方式**：1 个主 agent + 9 个并行 sub-agent
- **最终产出**：12 文件 / 1969 行（3 spec 文档 + 9 wiki 文件）
- **提交**：commit `02c34a4` `docs(learning): 新增IDL接口定义语言Wiki教程填补知识库空白`

## S1 事实收集

### 时间线

| 阶段 | 产出 | 耗时（估算） | 状态 |
|------|------|-------------|------|
| Spec 创建 | spec.md（232 行）+ tasks.md（128 行）+ checklist.md（92 行） | ~10 分钟 | ✅ 一次性通过用户审批 |
| 目录创建 | `docs/knowledge/learning/01-agent-protocols-interfaces/idl-wiki/` | <1 分钟 | ✅ |
| 并行 sub-agent 执行 | 9 个 wiki 文件（00-08） | ~3 分钟（并行） | ✅ 全部成功 |
| 链接验证 | check-links.py 检测 | <1 分钟 | ⚠️ 发现 10 个断链 |
| 断链修复 | 6 个文件名替换（00-overview.md） | ~2 分钟 | ✅ 修复后全部通过 |
| 原子提交 | git commit | <1 分钟 | ✅ commit 02c34a4 |

### 关键事件

1. **Spec 一次性通过**：用户对 spec.md、tasks.md、checklist.md 三份文档未提出修改意见，直接批准实施
2. **9 个 sub-agent 并行成功**：所有 sub-agent 在 ≤300 行约束下完成内容创作，无超长文件
3. **断链事件**：`00-overview.md` 的 sub-agent 自行推断文件名（如 `02-syntax-structure.md`），与实际创建的 `02-syntax-basics.md` 等 6 个文件名不一致，导致 10 个断链
4. **修复成本可控**：6 次 `Edit replace_all` 操作 + 1 次链接重检，约 2 分钟
5. **原子提交规范执行**：三查暂存法正确排除了无关的 `myst-unified-interface-ecosystem/` 目录

### 量化数据

| 指标 | 数值 |
|------|------|
| Spec 文档总行数 | 452 行（spec 232 + tasks 128 + checklist 92） |
| Wiki 文件总行数 | 1517 行（9 文件，平均 169 行） |
| 最大文件 | 02-syntax-basics.md（292 行，接近 300 行上限） |
| 最小文件 | 04-comparison.md（83 行） |
| 断链数量 | 10 个（全部集中在 00-overview.md） |
| 修复操作 | 6 次文件名替换 |
| 提交文件数 | 12 个 |
| 提交行数 | +1969 行 |

## S2 过程分析

### 成功因素

1. **Spec-driven 模式确保产出对齐**：spec.md 中 12 条验收标准（AC-1 ~ AC-12）+ tasks.md 中 10 个任务的详细步骤分解，使 9 个 sub-agent 各自独立工作却能在内容上互补、无重大重复
2. **并行 sub-agent 显著缩短创作时间**：9 个文件并行创建（~3 分钟）vs 串行创建（估算 ~27 分钟），效率提升约 9 倍
3. **质量约束前置有效**：spec 中明确的 frontmatter 规范、`<300 行`限制、相对路径要求、导航格式，使 sub-agent 在创建时即遵循，9 个文件的 frontmatter 字段顺序、source/category 值全部一致，无需事后统一
4. **链接检查工具作为质量门**：`check-links.py` 自动检测出 10 个断链，避免了带病提交
5. **三查暂存法排除无关文件**：原子提交时正确识别并排除了 `.trae/specs/standards-tools/myst-unified-interface-ecosystem/`（非本次任务产出）

### 问题与瓶颈

1. **sub-agent 间命名约定不一致**（核心问题）：
   - **现象**：`00-overview.md` 的 sub-agent 在导航表中使用了 `02-syntax-structure.md`、`03-major-specs.md`、`04-spec-comparison.md` 等 6 个错误文件名
   - **根因**：sub-agent 的 prompt 中提供了"9 章导航表"的章节号和标题，但**未明确锁定具体文件名清单**，sub-agent 根据章节标题自行推断文件名，而实际创建文件的 sub-agent 遵循了 spec 中的文件名约定
   - **影响**：10 个断链，需 2 分钟手动修复

2. **缺乏 sub-agent 间协调机制**：
   - 并行 sub-agent 各自独立工作，无法感知其他 agent 的实际产出文件名
   - 主 agent 在分派任务时未将"文件名清单"作为契约传递给每个 sub-agent

3. **02-syntax-basics.md 接近行数上限**：
   - 292 行（限制 300 行），余量仅 8 行
   - 原因：该章需覆盖 4 类语法要素（类型/接口/方法/注解）× 3 种 IDL 语法对照（Protobuf/CORBA/Thrift），代码示例较多
   - 风险：后续维护时若增加内容容易超限

## S3 洞察提炼

### 洞察 1：并行 sub-agent 任务必须在 prompt 中锁定文件名契约

- **类别**：工程/方法论洞察
- **内容**：当多个 sub-agent 并行创建相互引用的文件时，必须在每个 sub-agent 的 prompt 中**明确列出所有相关文件名清单**（包括它自己创建的和其他 agent 创建的），作为不可变更的命名契约
- **支撑证据**：`00-overview.md` 的 sub-agent 在 prompt 中收到了章节号和标题，但未收到文件名清单，导致它自行推断出 6 个错误文件名；而其他 8 个 sub-agent 的 prompt 中明确指定了"创建文件 `XX-xxx.md`"，因此文件名全部正确
- **可迁移性**：所有并行 sub-agent 创建相互引用文档的任务均适用——文件名是跨 agent 协作的"接口契约"，必须在 prompt 中显式声明

### 洞察 2：链接检查是并行 sub-agent 任务的必备质量门

- **类别**：工程/质量保障洞察
- **内容**：并行 sub-agent 各自独立工作，无法感知彼此产出的实际文件名与内容，链接检查工具（`check-links.py`）是验证跨文件引用一致性的**最后一道防线**，必须在提交前强制执行
- **支撑证据**：本次链接检查捕获了 10 个断链，全部集中在 `00-overview.md`（导航枢纽文件），如果不检查直接提交会导致教程的 9 章导航中 6 章无法跳转
- **可迁移性**：所有并行 sub-agent 创建的相互引用文档集，提交前必须运行 `check-links.py`，这是不可跳过的质量门

### 洞察 3：Spec 驱动开发的"格式契约前置"显著降低协调成本

- **类别**：方法论洞察
- **内容**：通过 spec.md 中的 frontmatter 规范、文件大小限制、链接规范等"硬约束"前置，sub-agent 在创建文件时即遵循统一格式，避免了事后统一调整的成本。这种"格式契约前置"模式使 9 个独立 agent 的产出在格式上天然一致
- **支撑证据**：9 个 sub-agent 各自独立创建的文件，frontmatter 字段顺序、`source`/`category` 值、导航格式、代码块语言标注全部一致，无需事后统一；唯一不一致的是文件名引用（因为文件名清单未在 prompt 中锁定）
- **可迁移性**：所有需要多 agent 协作的文档创建任务，都应在 spec 阶段明确"格式契约"（frontmatter 模板、文件大小、链接格式、导航格式），并在每个 sub-agent 的 prompt 中复用该契约

### 洞察 4：导航枢纽文件是并行任务的高风险点

- **类别**：架构/风险洞察
- **内容**：在多文件教程中，导航枢纽文件（如 `00-overview.md`）需要引用所有其他文件，是并行任务中**链接错误集中爆发**的高风险点。导航文件的 sub-agent 必须接收最完整的"文件名清单"作为输入
- **支撑证据**：本次 10 个断链全部集中在 `00-overview.md`，其他 8 个分章文件（01-08）的链接全部正确——因为分章文件只引用相邻章节（上一章/下一章），而 00-overview.md 需要引用全部 9 章
- **可迁移性**：所有并行创建的多文件教程/文档集，导航枢纽文件应作为重点关注对象，其 sub-agent prompt 必须包含完整的文件名清单

## S4 行动项

| # | 改进项 | 优先级 | 对应洞察 | 验收标准 | 状态 |
|---|-------|--------|---------|---------|------|
| 1 | 在并行 sub-agent 任务模板中加入"文件名清单"必填项 | 🔴 高 | 洞察 1 | 后续并行 sub-agent 任务的主 agent prompt 中，每个 sub-agent 都收到完整的文件名清单 | 🗓️ 待执行 |
| 2 | 将链接检查纳入并行 sub-agent 任务的强制流程 | 🔴 高 | 洞察 2 | 后续并行 sub-agent 创建文档后，提交前必须运行 `check-links.py` 并通过 | 🗓️ 待执行 |
| 3 | 总结"格式契约前置"模式为可复用方法论 | 🟡 中 | 洞察 3 | 沉淀为 `navigation-hub-filename-contract` 模式文档，入库 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/` | ✅ 已完成（[模式文件](../../patterns/methodology-patterns/ai-collaboration/navigation-hub-filename-contract.md)） |
| 4 | 为 02-syntax-basics.md 建立行数监控 | 🟢 低 | S2 问题 3 | 该文件若后续增加内容，需评估是否拆分为 02-syntax-types.md + 02-syntax-interface.md | ℹ️ 观察中 |

## 5-Whys 根因分析

| 问题 | 根因 | 最终状态 |
|------|------|---------|
| 00-overview.md 出现 10 个断链 | sub-agent prompt 未锁定文件名清单，agent 自行推断文件名与实际不一致 | ✅ 已修复，并提炼为"文件名契约锁定"洞察 |
| 其他 8 个分章文件链接全部正确 | 这些 sub-agent 的 prompt 中明确指定了"创建文件 `XX-xxx.md`"，文件名作为输入而非推断 | ✅ 验证了"文件名清单前置"的有效性 |
| 02-syntax-basics.md 接近 300 行上限 | 该章需覆盖 4 类语法 × 3 种 IDL 对照，代码示例密度高 | ℹ️ 观察中，未来可考虑按语法要素拆分 |

## 复盘结论

本次 IDL Wiki 教程创建任务**整体成功**：12 文件 1969 行单日完成，链接检查通过，原子提交规范执行。核心教训是**并行 sub-agent 任务的文件名契约必须在 prompt 中显式锁定**——这是一个可复用的工程模式，值得沉淀为方法论。spec-driven 开发模式的"格式契约前置"特性显著降低了多 agent 协作的协调成本，验证了该模式在文档创建场景下的高效性。

## 导航

| 上一份报告 | 报告目录 | 相关文档 |
|-----------|---------|---------|
| [dockerfile-optimization-retro-20260703.md](dockerfile-optimization-retro-20260703.md) | [README.md](README.md) | [IDL Wiki 教程](../../../knowledge/learning/01-agent-protocols-interfaces/idl-wiki/00-overview.md) |

## Changelog

<!-- changelog -->
- 2026-07-04 | docs | v1.1：洞察萃取完成，行动项 3 已落地为 `navigation-hub-filename-contract` 模式文档，入库 ai-collaboration 分类
- 2026-07-04 | docs | v1.0：IDL Wiki 教程创建任务复盘，提炼 4 个洞察（文件名契约锁定/链接检查必备/格式契约前置/导航枢纽高风险），4 项行动项
