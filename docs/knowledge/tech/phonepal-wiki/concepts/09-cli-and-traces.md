---
type: Concept
title: "CLI 与轨迹：把手机上的运行变成可读证据"
description: "开发者 CLI 的 6 个命令、debug 广播桥、logcat 事件行与 trace.jsonl/audit.jsonl/step-png 的关系；如何用 lint/push/run/traces 在真机上迭代技能，以及为什么每个任务都必须以终止事件收尾"
tags: [phonepal, cli, adb, traces, logcat, debugging]
generated:
  by: specweave-agent
  at: "2026-11-12T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-12T00:00:00+08:00"
status: stable
stale_after: "2027-05-12"
sources:
  - id: S-01
    resource: ../references/00-source-inventory.md
    title: 信源登记：PhonePal 源码快照
---

# CLI 与轨迹：把手机上的运行变成可读证据

PhonePal 的调试不是「看界面猜」，而是三层可读证据：**logcat 一行一事件**、**trace.jsonl 一行一状态**、**audit.jsonl 一行一决策**，外加每步截图。CLI 负责把这三层串起来。

## 1. 6 个命令

| 命令 | 作用 | 关键参数 |
|---|---|---|
| `lint` | 按 App 同规则校验技能文件夹 | 一个或多个技能目录 |
| `push` | 先 lint，通过后 `adb push` 到手机并触发重载 | 技能目录 |
| `run` | 通过调试桥启动手机任务 | `goal`、`--skill`、`--run-id`、`--follow` |
| `stop` | 停止当前任务 | — |
| `logs` | 持续读取 PhonePal logcat 事件 | `--run-id` |
| `traces` | 拉取并查看轨迹 | `pull <run_id>` / `show <path-or-run-id>` |

顶层 6 个命令，`traces` 下 2 个子命令 [F-073]。run id 只允许字母、数字、`.`、`_`、`-`，默认格式 `cli-YYYYMMDD-HHMMSS-xxxx`。

## 2. 一次典型迭代

```bash
# 1) 本地校验：与 App 同规则、同行号
python3 cli/phonepal.py lint skills/examples/taxi-home

# 2) 推到手机（会先 lint，失败不推）并触发 reload
python3 cli/phonepal.py push skills/examples/taxi-home

# 3) 跑一个任务，持续输出事件直到终止事件
python3 cli/phonepal.py run "用高德打车回家" --skill taxi-home --follow

# 4) 拉轨迹并渲染成表格
python3 cli/phonepal.py traces show cli-20261112-101500-abcd --full
```

`run --follow` 会先启动 logcat 再发广播，避免漏掉前几个事件；退出码由终止事件决定：`PhoneTaskFinished.success = true` 返回 0，否则返回 1 [F-073]。

## 3. 调试桥：三条广播

debug 包导出 `DebugReceiver`，只接受三条 action [F-072]：

| action | extras | 效果 |
|---|---|---|
| `dev.phonepal.debug.RUN` | `goal`、`skill`、`run_id` | 交给会话执行 `runPhoneTask` |
| `dev.phonepal.debug.STOP` | 无 | 协作式停止（释放待答问题与审批） |
| `dev.phonepal.debug.RELOAD_SKILLS` | 无 | 重新加载技能并记录问题 |

CLI 的 `adb.broadcast` 用 `shlex.quote` 把参数拼成**一个**远端 shell 字符串，中文、空格、引号都能完整到达设备 [F-073]。`am broadcast` 即使没人接收也返回 0，所以 CLI 还检查输出里是否含 `Error`/`Exception`。

## 4. 三层证据

### 4.1 logcat

格式固定为：

```text
PhonePal: <run_id> <EventKind> <json>
```

`EventKind` 是 `AgentEvent` 的类名（10 种之一）；`json` 与 `trace.jsonl` 的行完全相同。CLI 的 `logcat.py` 同时兼容 `threadtime`、`brief` 与 `-v raw` 三种格式 [F-071/F-073]。

### 4.2 trace.jsonl

每行固定 8 个键 [F-071]：

```json
{"time":1761830000000,"run":"r1","kind":"StepExecuted","step":3,
 "action":{"type":"tap","nodeId":12},"text":"click node 12","ok":true,
 "decision":"allow: allowed"}
```

`kind` 与 `AgentEvent` 的 10 个子类型一一对应；`decision` 是同一任务最近一条审计记录的字符串形式。

### 4.3 audit.jsonl 与截图

- `audit.jsonl`：每条 Sentinel 决策一行，6 个字段（含 `approved`）；
- `step-<n>.png`：每次 `observe()` 得到的屏幕截图（`RecordingDevice` 包装设备后保存）[F-082]。

目录结构：

```text
traces/<run_id>/
├── trace.jsonl
├── audit.jsonl
└── step-0.png, step-1.png, ...
```

## 5. 为什么「每个任务必须有终止事件」

`AgentSession` 有一条硬约束：任务无论因为未配置、忙、崩溃还是取消而没跑完，都必须补发 `Failed` + `PhoneTaskFinished` [F-070]。

原因在 CLI 侧：`run --follow` 等的是 `PhoneTaskFinished` 或 `Failed`。如果某个路径悄悄结束而不发终止事件，CLI 会一直挂着，直到 logcat 断开才报「logcat ended before the run finished」。这条约束把「调试体验」和「运行时正确性」绑在了一起。

## 6. 解析事件时容易忽略的细节

| 细节 | 说明 |
|---|---|
| `step` 从 0 开始 | `PhoneTaskFinished.steps` 是总步数 |
| `StepPlanned` 与 `StepExecuted` 成对 | 被拦截时只有 `StepBlocked`，没有 `StepExecuted`，步数不增加 |
| `decision` 可能为 null | `StepPlanned`、`Reply` 等事件没有决策 |
| 密钥一定被掩码 | 长度 ≥ 4 的 API Key 在任何一行都会变成 `***` |
| run id 会清洗成目录名 | 非 `[A-Za-z0-9._-]` 字符替换为 `_`，防目录穿越 |

## 7. 用轨迹回答什么问题

| 问题 | 看哪里 |
|---|---|
| 模型想做什么？ | `StepPlanned.action` + `target`/`reason` |
| 为什么没执行？ | `StepBlocked.decision` 的原因 |
| 执行成功了吗？ | `StepExecuted.ok` + `text` |
| 卡在哪一步？ | 最后几条 `step` 与截图 |
| 用户被问了几次？ | `NeedsUser` 事件数量 |
| 安全层拦了什么？ | `audit.jsonl` 的 `decision` 列 |
| 任务成功学习了什么？ | `MemoryUpdated.permalink`（通常是 `howto/<key>`） |

## 8. CLI 的边界

- 只操作 **debug 包**：release 清单不导出 `DebugReceiver`；
- 不做设备管理：不装 APK、不启模拟器，只调 `adb`；
- 不解析截图内容：`traces show` 只渲染文本表格，截图要自己打开；
- 与 App 的规则可能漂移：Kotlin 与 Python 是两套实现，靠 CI 的「示例技能 lint」与测试兜底 [F-074/F-076]。

## 相关概念

- [技能与 flow：lint 检查什么](06-skills-and-flows.md)
- [操作循环：事件是在哪里发出的](03-operator-loop.md)
- [示例：CLI 实操剧本](../examples/02-cli-workflow.md)
- [信源登记](../references/00-source-inventory.md)
