---
name: specweave-dsh-bridge-access
description: "DeepSeek Harness 使用者接入指南：说明如何在工作区零配置生效、如何使用 /specweave 命令与四个模型侧工具，以及接入成功与失败的判别标准。"
source: "specweave-dsh-bridge/README.md + AGENTS.md#启动协议"
---

# DeepSeek Harness 使用者接入指南

`specweave-dsh-bridge` 让 DeepSeek Harness 会话把 SpecWeave 工作区的 `AGENTS.md` + `.agents/` 当作入口。
本文档说明使用者如何接入、如何验证，以及哪些做法属于反模式。

## 前提

- [ ] 已安装 DeepSeek Harness（桌面版或 CLI），且能打开 SpecWeave 工作区会话
- [ ] 已把本仓库的 `specweave-dsh-bridge/` 通过 `plugin_manager install_bundle` 装进当前 profile
- [ ] 安装返回值的 `application` 为 `applied`（不是 `failed` / `overridden` / `restart-required`）
- [ ] 已**新开**一个会话（安装前已存在的会话不会重放注入）

## 接入方式总览

| 层级 | 使用者 | 入口 | 适用诉求 |
|---|---|---|---|
| 零配置 | 任何人 | 在工作区内开会话即生效 | 自动获得启动协议提醒 |
| 交互式 | 人 | `/specweave status \| route <任务> \| help` | 想知道"现在在哪、该读什么" |
| Agent 自主 | 模型 | `specweave_route` / `specweave_status` / `specweave_check` / `specweave_protocol` | 任务路由、状态确认、提交前校验 |

**核心机制**：桥接层按会话工作目录逐级向上探测，命中「`AGENTS.md` 含签名关键词 **且** 存在
`.agents/context-routing.md`」的目录即认定为 SpecWeave 工作区根。因此**注入跟随目录，而不是跟随会话**——
换到非 SpecWeave 目录开会话时 **brief 不注入**；工具、命令与技能是宿主级注册仍然可见，
但工具会明确返回 `in_workspace: false`（`specweave_protocol` 则返回与工作区无关的协议要点）。

## 第 1 步：零配置接入（默认生效）

在 SpecWeave 工作区内直接开会话即可。桥接层会在第一步注入一段启动协议 brief（用户消息层，`<system-reminder>` 包裹）。

**检验标记**：会话历史中出现 `[SpecWeave 启动协议]` 字样，且其中包含工作区根路径与「按上下文路由表定位必读规范」的指令。

## 第 2 步：交互式接入（人用）

```text
/specweave status            # 工作区根、子区域、入口文件、产出物路径纪律
/specweave route 复盘         # 查询该任务对应的规范入口
/specweave skill 七概念       # 中文触发词 → 技能名，并把技能正文排入下一步
/specweave help              # 命令与工具清单
```

> ⚠️ **中文斜杠手势不可用**：DSH 的 `/name` 手势按技能名精确匹配，而技能名强制 ASCII kebab-case，
> 所以 `/七概念` 永远不通。中文入口请走 `/specweave skill 七概念`，或让智能体用 `specweave_route` 定位后加载。

## 第 5 步：Agent 自主接入（Agent 用）

| 工具 | 语义 | 门控 |
|---|---|---|
| `specweave_route(task)` | 关键词多命中 → 规范路径；路径不存在则标记 `stale` 并回退路由表 | 工作区外返回 `in_workspace: false` |
| `specweave_status()` | 工作区根 / 子区域 / 入口 / 公开与私域产出物根 / 废止路径 | 同上 |
| `specweave_check(kind)` | 返回该变更类型的校验命令（`links`/`mermaid`/`gitignore`/`atomization`/`duplication`/`traceability`/`pwsh`/`ci`） | **不执行**，执行请用 `pwsh` 工具 |
| `specweave_protocol()` | 协议要点文本（技能目录不可用时的兜底） | 同上 |

## 反模式（避免）

1. **换目录仍期待生效**——在非 SpecWeave 目录开会话，brief 不注入、工具返回 `in_workspace: false`，这是设计行为，不是故障。
2. **手动记忆规范路径**——规范路径会随仓库重构漂移；用 `specweave_route` / `specweave_check` 现查，而不是背路径。
5. **让桥接层替你执行脚本**——桥接层只回答"跑什么"，执行必须走会话的 `pwsh` 工具，以保留沙箱与审批边界。
4. **手工改写 profile 的 `package.json` / `cordis.patch.yml`**——装配一律走 `plugin_manager install_bundle`。
5. **把 brief 当成规范真源**——brief 只是提醒；规范真源是磁盘上的 `AGENTS.md` 与 `.agents/` 文件。

## 检验标准

```powershell
# 1) 仓库内自测（无需安装）
cd specweave-dsh-bridge
node tests/bridge.test.js    # 期望：48 项全通过

# 2) 装配层确认（不改 live profile）
dsh --profile "$env:DSH_PROFILE" --dump-config | Select-String "specweave-bridge"
```

**接入成功 = 以下三条同时成立**：

- 工作区会话第一步出现 `[SpecWeave 启动协议]` 注入文本；
- `/specweave status` 报出正确的工作区根与子区域；
- `specweave_route 复盘` 返回 `.agents/skills/retrospective-cmd/SKILL.md` 且 `exists: true`。

**接入失败 = 安装结果 `application` 非 `applied`，或注入文本缺失**；此时先看 `warnings`（模块解析、配置校验），
再确认 `signaturePaths` 与工作区实际结构是否一致（衍生工作区可覆盖 `signatureKeyword` / `signaturePaths`）。
