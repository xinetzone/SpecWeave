---
okf_version: "0.2"
type: spec-facts
title: "ub-mode 博文转化事实清单（F 编号）"
description: "微信公众号「开源日记」《只有一个 Skill 的仓库，竟然斩获 2900 Star！》博文事实 + GitHub 官方源核验事实的编号登记（F-001~F-037）；bundle references/article-source.md 为同集双份登记"
generated: { by: "seven-concepts-cmd+R", at: "2026-11-04T10:00:00+08:00" }
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: github
    url: https://github.com/unclebob/ub-mode
---

# ub-mode 博文转化事实清单

图例：**[博文]** 博文单源 · **[官方]** GitHub 官方源核验 · **[观点]** 作者观点（不得转述为事实）。

## A. 元信息（博文与仓库身份）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-001 | 博文标题《只有一个 Skill 的仓库，竟然斩获 2900 Star！》，公众号「开源日记」，署名作者「熊叔」 | [博文] |
| F-002 | 博文发布日期 2026-10-28 08:53 | [博文] |
| F-003 | 开源仓库地址 `https://github.com/unclebob/ub-mode` | [博文][官方] |
| F-004 | 仓库全名 `unclebob/ub-mode`，owner 登录名 `unclebob`（GitHub user id 36901） | [官方] |
| F-005 | 仓库创建时间 `2026-10-25T16:04:09Z`；最后代码推送 `2026-10-25T16:07:59Z`；元数据更新 `2026-10-29T05:19:47Z` | [官方] |
| F-006 | 默认分支为 `master`（非 `main`）；博文未提及 | [官方] |
| F-007 | GitHub API `language` 字段为 `null`，无语言统计（仓库内无可执行代码） | [官方] |
| F-008 | 仓库文件树共 **3 个文件**：`LICENSE`（1,073 B）、`README.md`（2,195 B）、`SKILL.md`（3,958 B），合计 7,226 B | [官方] |
| F-009 | 许可证 `MIT License`，著作权署名 `Copyright (c) 2026 Robert C. Martin`（GitHub API `license` 字段为 `null`，以 LICENSE 文件为准） | [官方] |
| F-010 | Star 数：博文标题口径 **2,900**（2026-10-28）；核验时点（2026-11-04）GitHub API `stargazers_count` = **3,951** | [博文][官方] |
| F-011 | 核验时点（2026-11-04）`forks_count` = 214、`open_issues_count` = 5、`subscribers_count` = 24 | [官方] |

## B. 项目定位与官方自述

| 编号 | 事实 | 来源 |
|------|------|------|
| F-012 | README 自述：ub-mode 是一个 **agent skill**，在编写或修改代码时强制执行有纪律的软件工程原则 | [官方] |
| F-013 | README 自述：ub-mode "loosely based on portions of @poteto's rules (`poteto-mode` / `pstack`)"（**博文未提及此溯源**） | [官方] |
| F-014 | `SKILL.md` frontmatter：`name: ub-mode`；description 声明「每次改动遵循 First Make it Work → Then Make it Right → Follow Practice」，触发时机为用户执行 `/ub-mode` 或要求 "the reduced principles" | [官方] |

## C. 博文主张的三步机制

| 编号 | 事实 | 来源 |
|------|------|------|
| F-015 | 博文核心议题：AI 编程助手「写规则越写越不听话」 | [观点] |
| F-016 | 博文第一步「把 Bug 修好」：先写测试，再做最小改动 | [博文] |
| F-017 | 博文第二步「修好还要检验」：用 Crapper 查复杂度、Dryer 查重复度、Mutator 做变异测试 | [博文] |
| F-018 | 博文第三步「说明修改了什么」：报告改了哪些文件、加了哪些测试、检查结果 | [博文] |
| F-019 | 博文列举的规则之一：登录参数入口检查一次 | [博文] |
| F-020 | 博文列举的规则之一：重复逻辑集中维护 | [博文] |

## D. 官方 SKILL.md 三大节原则清单

| 编号 | 事实 | 来源 |
|------|------|------|
| F-021 | **First Make it Work** 节含 8 组原则：Laziness Protocol、Foundational Thinking、TDD、Redesign From First Principles、Attack the Premise、Subtract Before You Add、Outcome-Oriented Execution、Build the Lever；另有 Architecture 子节 5 条（Model the Domain、Boundary Discipline、Type System Discipline、Make Operations Idempotent、Separate Before Serializing Shared State） | [官方] |
| F-022 | **Then Make it Right** 节含 7 条：Fix Root Causes、Sequence work into verifiable units、Test Behavior Not Implementation、Crapper、Dryer、Mutator、Refactoring | [官方] |
| F-023 | **Practice** 节含 4 条：Keep a Log、Guard the Context Window、Worktree Cleanup、Commit and Push | [官方] |

## E. 可打分检查工具与阈值

| 编号 | 事实 | 来源 |
|------|------|------|
| F-024 | Crapper 阈值：每个函数 CRAP 分数须低于 **10**（官方 SKILL.md「Reduce each function under CRAP 10」；README「CRAP < 10」） | [官方] |
| F-025 | Dryer 阈值：消除相似度 **≥ 0.8** 的重复代码（官方 SKILL.md「rank 0.8 or above」；README「>= 0.8 similarity」） | [官方] |
| F-026 | Mutator 用法：覆盖未覆盖代码、杀掉存活的变异体、删除死代码 | [官方] |
| F-027 | Companion 工具仓库共 **4 个**：`crapper`、`dryer`、`mutator`、`uml-viewer`（均属 `unclebob/` 命名空间）；**博文只提 3 个** | [官方] |
| F-028 | `uml-viewer` 用于可视化组件、覆盖率、CRAP 分数、变异分数与依赖方向；**博文未提及** | [官方] |
| F-029 | 博文所述检查命令：`./crapper --threshold 10`、`./dryer --threshold 0.8 src`、`./mutator --changed`；官方仓库**未提供 CLI 用法文档**，无从对拍 | [博文] |
| F-030 | 博文所述输出：检查结果写入 `.metrics` 目录，产物为 `crap.edn`、`dry.edn`、`mutate` 快照；**仅博文单源** | [博文] |

## F. 安装与触发

| 编号 | 事实 | 来源 |
|------|------|------|
| F-031 | 官方安装方式：把 `SKILL.md` 复制为 agent 技能目录下的 `ub-mode/SKILL.md`，示例路径 `~/.grok/skills/ub-mode/SKILL.md`、`~/.claude/skills/ub-mode/SKILL.md`、`~/.cursor/skills/ub-mode/SKILL.md`，随后调用 `/ub-mode` | [官方] |
| F-032 | 博文「上手三步」：① `mkdir -p ~/.claude/skills/ub-mode` + `cp SKILL.md ~/.claude/skills/ub-mode/SKILL.md`；② 重启助手并输入 `/ub-mode`；③ 安装三个检查工具（博文仅给 Claude 一条路径） | [博文] |

## G. 博文自陈的局限与口径差异

| 编号 | 事实 | 来源 |
|------|------|------|
| F-033 | 博文局限①：规则要求 AI 自动提交并推送代码，作者对此「不放心」（对应官方 Practice > Commit and Push「Push to the main line at the end」） | [观点] |
| F-034 | 博文局限②：三个检查工具需**单独安装**，ub-mode 本身只提供规则（与官方「companion tool repositories」自述一致） | [博文][官方] |
| F-035 | 博文称仓库「只有两个文件，加起来 6KB」；实际为 3 个文件、合计 7,226 B（README+SKILL = 6,153 B ≈6KB，口径漏计 LICENSE） | [博文] vs [官方] |
| F-036 | 博文称作者 Robert C. Martin 写过《Clean Code》；LICENSE 署名 `Copyright (c) 2026 Robert C. Martin`，GitHub owner 为 `unclebob` | [博文][官方] |
| F-037 | 仓库自 2026-10-25 创建至核验时点（2026-11-04）**无 Release、无 tag**，README/SKILL 自初始推送后未再改动（`pushed_at` 仍为创建当日） | [官方] |

## 核验记录摘要

- 核验时点：2026-11-04
- 核验信源：GitHub REST API（`/repos/unclebob/ub-mode`、`/git/trees/master?recursive=1`）+ `raw.githubusercontent.com/unclebob/ub-mode/master/{README.md,SKILL.md,LICENSE}`
- 结论：13 组 P0/P1 核验 —— ✅ 7、⚠️ 6、❌ 0；详见 `references/verification.md`（bundle 侧）与本 spec 第 5 节
- 关键提示：`default_branch = master`（首次按 `main` 取 raw 会失败）
