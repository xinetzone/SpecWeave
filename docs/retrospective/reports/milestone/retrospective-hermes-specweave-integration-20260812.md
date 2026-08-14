---
id: "milestone-hermes-specweave-integration-20260812"
title: "Hermes-SpecWeave 工作区规范集成里程碑"
date: "2026-08-12"
type: "milestone-retrospective"
source: "seven-concepts-cmd 编排（R→I→E→C）· 场景1里程碑复盘"
methodology: "七概念 R→I→E→C"
status: "已完成"
---

# Hermes-SpecWeave 工作区规范集成里程碑复盘

## 任务概述

将 SpecWeave 工作区规范（AGENTS.md 启动协议 / 三层路由 / Skill 门面）接入 Hermes Agent，实现「目录感知的规范自动生效」。交付物包括：`specweave-bridge` 插件（已部署至 `~/.hermes/plugins/` 并启用）、使用者接入指南（ACCESS.md）、一键自动化脚本（install.py），全程 4 次原子提交，G1-G4 质量门通过。

## R — 事实采集（20 条，纯客观）

| # | 事实 |
|---|---|
| F-001 | 插件部署于 `C:\Users\admin\.hermes\plugins\specweave-bridge\` |
| F-002 | `config.yaml` 的 `plugins.enabled` 含 `specweave-bridge` |
| F-003 | `hermes plugins list` 显示 `specweave-bridge` 为 enabled / user |
| F-004 | 注册组件：`pre_llm_call` hook、`specweave_route`、`specweave_check`、`/specweave` 斜杠、`hermes specweave` CLI、`specweave:protocol` 技能 |
| F-005 | 集成测试断言：工作区内 hook 注入上下文、工作区外返回 None |
| F-006 | 路由映射实测：`复盘`→`retrospective-cmd.md`、`CI检查`→`ci-check-cmd.md`、`Mermaid`→`mermaid-cmd.md` |
| F-007 | 子区域检测实测：`vendor` 子路径→`vendor`，根目录→`None` |
| F-008 | CLI 实测 `hermes specweave status` / `route Mermaid` 正常输出 |
| F-009 | 规范源码入库 `specweave-bridge-skeleton/`（plugin.yaml/_constants.py/detector.py/__init__.py/skills） |
| F-010 | 启动协议注入位于用户消息层，系统提示词字节级不变 |
| F-011 | 共 4 次原子提交：源码、spec 规划、ACCESS 指南、install 脚本 |
| F-012 | `ACCESS.md` 使用者接入指南创建（三层接入：零配置/交互/Agent） |
| F-013 | `install.py` 一键脚本创建（install/verify/all/enable/deploy） |
| F-014 | `install.py` 零第三方依赖、幂等 |
| F-015 | `install.py verify` 输出 PASS，退出码 0 |
| F-016 | `install.py` 三种 enable 分支（无 plugins 块 / 无 enabled / 缺 item）均正确且重复执行为 already-enabled |
| F-017 | 首次 `verify` 失败（`No module named 'specweave_bridge'`），补 `sys.modules` 注册 + `__path__` 后通过 |
| F-018 | 真实 `HERMES_HOME` 为 `C:\Users\admin\.hermes`（网关脚本设置）；直跑 python 未设环境变量时回退 `AppData\Local\hermes` |
| F-019 | 集成测试执行 2 轮（组件注册 + 插件加载逻辑）均通过 |
| F-020 | `install.py` deploy 仅拷贝运行时文件（排除文档与脚本自身） |

**G1 检查**：≥20 条 ✅、无因果词 ✅、可验证可追溯 ✅ → 通过

## I — 洞察（3 条）

**洞察1｜接入的默认路径是「被动生效 + 目录感知」，而非用户主动安装**
- 陈述：Hermes 接入 SpecWeave 规范的核心机制是 cwd 探测，不是用户显式导入工具。
- 证据：F-005/F-006/F-007 —— hook 与工具均由工作区探测门控。
- 反常识：用户"什么都没装"就已接入——只要在 `SpecWeave/` 下开会话即生效。
- 行动：接入文档应以"目录即上下文"为第一原则，而非"安装教程"。

**洞察2｜自动化的正确建模是「面向结果」（install/verify 两命令），而非复刻手动步骤**
- 陈述：最有价值的设计决策是把 4 步手动操作抽象为「装好」与「确认装好」两个结果。
- 证据：F-013/F-015/F-016 —— install 幂等、verify 输出 JSON+退出码、全分支正确。
- 反常识：自动化价值不来自"少敲几条命令"，而来自「幂等 + 可回滚 + 可判定」的可靠性。
- 行动：任何流程自动化优先定义"成功/失败的可判定标准"（verify + 退出码）。

**洞察3｜复用插件自身逻辑做校验是正确选择，但包加载有反直觉坑**
- 陈述：verify 复用 `detector`/`_handle_specweave_route`，避免双份逻辑漂移。
- 证据：F-015/F-017 —— 复用成立，但首次因缺 `sys.modules` 注册 + `__path__` 而失败。
- 反常识：`spec_from_file_location` 加载包需**两处**补全（注册 + 路径），只设一处不够。
- 行动：跨代码库复用组件时，把"包级加载的初始化条件"写入模式反模式清单。

**G2 检查**：3 条 ✅、四元组完整 ✅、有反常识 ✅ → 通过

## E — 萃取（2 个可迁移模式）

| 模式ID | 模式名称 | 成熟度 | 说明 |
|--------|---------|--------|------|
| bp-plugin-bridge-standard-integration | [插件桥接规范集成法](../../patterns/methodology-patterns/plugin-bridge-standard-integration.md) | L1-draft | 把一套工作区规范接入已有 Agent 平台的五步法 |
| bp-automation-idempotent-four-elements | [自动化幂等四要素](../../patterns/methodology-patterns/automation-idempotent-four-elements.md) | L1-draft | 部署/启用/验证脚本的幂等设计 |

**G3 检查**：名称合规、触发+步骤+反模式+检验+迁移完整 ✅ → 通过

## C — 原子行动项

| # | 行动项 | Owner | 验收标准 |
|---|---|---|---|
| C-1 | 沉淀 2 模式到模式库并更新索引 | 团队 | 入库+索引更新+TOML 元数据 |
| C-2 | 为 install.py 补充单测（enable 分支回归） | 团队 | 覆盖率达标、无回归 |
| C-3 | 在 ACCESS.md 标注 HERMES_HOME 环境变量回退陷阱 | 团队 | ACCESS.md 含该说明 |
| C-4 | 本复盘报告落盘并原子提交 | 团队 | 报告入库、工作区干净 |

**G4 检查**：单一职责 ✅、可独立验证 ✅、有 Owner/验收 ✅ → 通过

---

**CHAIN_COMPLETED**：G1-G4 全通过；产出 = 20 事实 + 3 洞察 + 2 模式 + 4 原子行动项。
