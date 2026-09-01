---
type: Retrospective
title: invocations 知识包对账更新里程碑复盘（2026-08-24）
description: 基于 seven-concepts 编排（R→I→E→C），对 invocations bundle 22 文件对抗性对账、3 处漂移修复、invoke 任务化项目优化、2 个模式沉淀的完整复盘与更新报告
tags: [retrospective, invocations, adversarial-review, okf, seven-concepts, invoke, milestone]
generated: { by: "process:seven-concepts", at: "2026-08-24" }
verified: { by: "process:seven-concepts", at: "2026-08-24" }
status: stable
---

# invocations 知识包对账更新里程碑复盘

> 场景：里程碑复盘。链路：R（事实）→ I（洞察）→ E（萃取）→ C（原子提交）。
> 产物物关联：[facts.md](facts.md) / [review-report.md](review-report.md)（已归档至本目录）、bundle 更新、2 个已入库模式、本报告。

## 1. R 事实采集（G1 通过：无因果词、可溯源）

| # | 事实 | 来源 |
|---|------|------|
| R-1 | vendor invocations 版本 4.1.0；真实模块清单 11 顶层 + 4 packaging；`packaging/version.py` 经 Glob 确认不存在 | facts.md |
| R-2 | 22 文件对账：确定性漂移 2（D1 路径缺 `tools/`、D2 伪造键 `packaging.find_opts`）、疑似漂移 1（`ci.sudo.group`）；无虚构 API；19 文件准确 | review-report.md |
| R-3 | 引用 `packaging/version.py` 的文档仅 log.md 08-21 历史记录 | Grep |
| R-4 | D1 路径经 py314 `invocations.__file__` 实测确认为 `external/libs/tools/pyinvoke/invocations/invocations/` | 实测 |
| R-5 | `from __future__ import annotations` 已在 py314 移除（`str\|None` 运行时合法）；`import os/sys` 保留（clean 用 os、build 用 sys.platform） | tasks.py |
| R-6 | `ns.configure` 注入 `sphinx.source=doc`、`sphinx.target=_build/html`；`docs.build` 硬编码 `pty=True`，本项目以 `run.pty` 可配置、Windows 默认 False | tasks.py |
| R-7 | pyproject doc 依赖新增 `invoke` + `invocations==4.1.0`；CI pages.yml 由裸 sphinx-build 改为 `invoke build` | pyproject.toml / pages.yml |
| R-8 | `invoke build` 本地实测产出 `_build/html/index.html`；`invoke clean` 生效 | 本地验证 |
| R-9 | `git diff/status` 核对：6 文件修改 + 新 tasks.py 全部落盘（05/06/log/invocations-source/pyproject/pages.yml） | git |
| R-10 | 本轮修复：3 文档漂移 + verified 更新（references/05/06）+ log 追加 | git diff |

## 2. I 洞察（G2 通过：四元组完整）

| # | 现象 | 根因 | 影响 | 建议 |
|---|------|------|------|------|
| I-1 | bundle 声称源码路径少 `tools/` 层 | 生成时凭印象，未实测 `__file__` | 读者/工具按路径找不到源码 | 源码路径运行时实测，不照抄文档 |
| I-2 | `find_opts` 归错 `packaging` 配置块 | 只验证"键存在"未验证归属模块 | 读者照配置不生效，误导 | 对配置键核对所属 `ns.configure` 块，用同 bundle 正确文档反证 |
| I-3 | 22 文件对账仅 3 处漂移、无虚构 API | R/I/E 事实基线扎实 + V 阶段 Grep 级验证 | 核心内容可复用，无需重写 | "复基线→对账→定向修复"优于全量重写 |
| I-4 | 复用 vendor 任务在 Windows 因 `pty=True` 中止 | vendor 硬编码 POSIX pty | Windows 本地不可用 | 平台默认值可配置，按 `sys.platform` 分派 |
| I-5 | CI 裸 sphinx-build 改 `invoke build` | 命令散落、参数漂移 | CI 与本地命令不一致易漂移 | 默认值集中在 tasks.py `opts`，统一入口 |

## 3. E 萃取（G3 通过：模式可迁移，已入库）

| 模式 | 路径 | 反模式数 |
|------|------|:--:|
| 源码→OKF 对抗性更新工作流 | `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-code-to-okf-adversarial-update.md` | 6 |
| invocations Collection 封装 Sphinx 构建 | `.agents/docs/retrospective/patterns/code-patterns/invocations-collection-sphinx-build-wrapping.md` | 6 |

两模式均含触发场景/核心步骤/反模式（≥5）/迁移验证，成熟度 L1，validation_count=1，已在对应 README 索引登记。

## 4. C 原子提交（G4 通过：单一职责、可独立验证、已落盘）

变更已真实落盘（R-9），拟按单一职责拆分为 2 个原子提交：

1. `docs(invocations): 修复 bundle 三处漂移并按 vendor 4.1.0 对齐 verified/log`
   - 文件：references/invocations-source.md、concepts/05-packaging-release.md、concepts/06-ci-automation.md、log.md
2. `feat(build): 引入 invoke/invocations 任务化构建入口（build/clean）`
   - 文件：tasks.py、pyproject.toml、.github/workflows/pages.yml

## 5. 更新报告摘要

- **漂移清零**：D1/D2/S1 3 处修复完成，bundle 22 文件与 vendor 4.1.0 对齐。
- **项目优化落地**：`invoke build` = `sphinx-build -E -b html doc _build/html`；CI 统一任务入口；py314 editable 引入 vendor invocations。
- **方法论沉淀**：2 个 L1 模式入库并登记索引。
- **验证闭环**：git diff 核对 6 改 + 1 新文件真实落盘；checklist 阶段 1-5 全打勾。

## 6. 下一步

- 执行上述 2 个原子提交（原子提交用 atomic-commit-cmd 规范：三查暂存法）。
- 待项目根 repo 同步 submodule 引用。

<!-- changelog -->
- 2026-08-24 | retro | 里程碑复盘创建