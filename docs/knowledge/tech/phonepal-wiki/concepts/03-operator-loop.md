---
type: Concept
title: "操作循环：观察、一步动作、反馈"
description: "PhonePal 的核心循环：截屏与节点列表交给操作模型，每步只产出一个动作；宽容解析、Sentinel 拦截反馈、未知 nodeId 反馈、两级卡死检测与受保护屏幕接管共同保证循环不会失控"
tags: [phonepal, operator-loop, accessibility, llm, agent-loop]
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

# 操作循环：观察、一步动作、反馈

这是整个项目最值得读的一百多行。`OperatorLoop.run` 没有「规划一整条路径」的宏大逻辑，它只做一件事：**让模型每一步只决定一个动作，然后把动作的后果如实告诉它**。

## 1. 循环骨架

```kotlin
for (iteration in 0 until maxSteps) {
    if (task.stop.stopped) return LoopOutcome(false, Prompts.STOPPED)
    val screen = device.observe()                   // 截屏 + 节点列表 + 前台包名
    if (screen.secure) { /* 请用户接管，continue */ }

    // 卡死计数：动作执行后屏幕指纹连续不变
    if (acted) { sameAfterActing = if (fp == actedOn) sameAfterActing + 1 else 0 }

    val reply = completeWithRetry(operatorRequest(...))   // 一次调用，失败重试一次
    val action = OperatorReplyParser.parse(reply.text)    // 宽容解析

    // 单步约束（flow 的 tap/type 步骤）与 nodeId 存在性校验
    // 发 StepPlanned；finish / ask_user 在循环内处理
    execute(task, action, screen)                     // Sentinel → device.perform
}
```

源码位置：`OperatorLoop.run` [F-025]，执行与拦截在 `execute` [F-028]，提示词在 `operatorRequest` [F-029]。

默认上限：`maxSteps = 30`、`stuckRepeats = 3`、`historyWindow = 8`、`maxNodes = 120` [F-008]。设置页可把 `maxSteps` 调到 1..200 [F-079]。

## 2. 操作模型看到什么

提示词是固定分节的，顺序本身有讲究 [F-029]：

| 顺序 | 分节 | 内容 | 为什么放这里 |
|---|---|---|---|
| 1 | 目标 / 子目标 | 整任务目标；flow 的 `ai` 步骤会替换为子目标 | 模型每步都要知道「现在到底要做什么」 |
| 2 | 技能说明 | `SKILL.md` 的 Markdown 正文 | 只在这一层出现，不污染聊天模型 |
| 3 | 相关资料 | 技能 `memory` 引用的笔记 | 目的地、偏好等参数 |
| 4 | 以前成功的路径 | `howto` 笔记（最多 3 条，每条 800 字） | 给模型一个可复用的动作序列 |
| 5 | 最近的步骤 | 最近 `historyWindow = 8` 步的文字记录 | 防止重复点同一个按钮 |
| 6 | 上一步的反馈 | 解析失败、被拦截、执行失败、未知节点、卡死警告 | **纠错的主要通道** |
| 7 | 单步约束 | 「这一步只能 tap/type，对象是 X」 | flow 的精确步骤 |
| 8 | 当前屏幕 | 节点列表（≤ `maxNodes`）+ 截图 PNG | 唯一的视觉输入 |
| 9 | 下一步指令 | 「请给出下一步操作（一个 JSON 对象）」 | 固定收尾 |

模型必须只输出一个 JSON 对象：

```json
{"thought": "目的地输入框在顶部", "action": {"type": "tap", "nodeId": 12, "target": "目的地输入框", "reason": "先输入目的地"}}
```

`thought` 可选；`action.type` 是 11 种之一 [F-012]；坐标归一化到 0..1000 [F-010]。

## 3. 宽容解析：把「模型不听话」当常态

`OperatorReplyParser` 做四层兼容 [F-036]：

1. **剥围栏**：去掉 ```` ```json ```` / ```` ``` ```` 标记；
2. **取配平对象**：从第一个 `{` 开始，按字符串与转义规则找到配平的 `}`，忽略前后废话；
3. **同义词归一**：`click/press/touch/tap_node` → `tap`，`input/enter_text/set_text` → `type`，`done/complete/stop` → `finish`，约 50 个别名；
4. **形状兼容**：`nodeId` 可写成 `node_id`/`id`/`index`；点可写成 `[x,y]`、`{x,y}` 或 `"x,y"`，统一 clamp 到 0..1000。

解析失败不会立刻终止：错误信息进入 `feedback`，下一轮提示里出现「上一条回复无法解析：…… 请只输出一个 JSON 对象」；累计 `PARSE_FAILURE_LIMIT = 3` 次才失败 [F-026/F-037]。

## 4. 三类反馈

循环里所有「不对劲」都会被翻译成模型能理解的一句话，而不是直接抛错：

| 情况 | 反馈给模型 | 结果 |
|---|---|---|
| JSON 解析失败 | 「上一条回复无法解析：<原因>」 | 继续，最多 3 次 |
| 引用了不存在的 nodeId | 「节点 12 不在当前屏幕的节点列表中，请从列表中选择或改用 point」 | 继续，不计入解析失败 |
| 动作被 Sentinel 拦截 | 「上一步操作被安全模块拦截（<原因>），没有执行。请换一种做法，或用 ask_user 询问用户，或用 finish 结束」 | 继续，步数不增加 |
| 动作执行失败 | 「上一步执行失败：<消息>」 | 继续 |
| 屏幕连续不变 | 先警告「你可能卡住了，请换一种做法」；再次触发则失败 | 两级处理 |
| 单步约束不匹配 | 「这一步只能执行 tap 操作，请重新给出」 | 继续 |

这些文本都在 `Prompts` 里集中管理 [F-037]。

## 5. 单步约束：flow 如何借用同一个循环

`flow.yaml` 的 `tap:` 和 `type:` 不想让模型自由发挥，于是调用 `loop.run(task, constraint = StepConstraint("tap", target), maxSteps = 3)` [F-027/F-033]：

- 只接受对应类型的动作；
- `type` 步骤可以用 `constraint.text` 强制覆盖模型给的内容；
- 命中一次就返回，最多试 `SINGLE_STEP_TRIES = 3` 次。

这让「固定步骤」和「自由探索」共用同一套 Sentinel、审计、卡死检测，而不是两套执行器。

## 6. 受保护屏幕：模型看不见，就请人接管

`ScreenState.secure` 由两层判定 [F-063]：

1. 系统返回 `ERROR_TAKE_SCREENSHOT_SECURE_WINDOW`；
2. Android 11–13 把受保护窗口截成纯黑帧，`ScreenshotScaling.looksAllBlack` 用 16×16 采样判黑。

一旦 `secure = true`，循环不发任何设备动作，而是发 `NeedsUser(..., takeover = true)` 请用户手动完成，用户回复后继续 [F-025]。这条路径与 Sentinel 的 deny 规则互为兜底：即使循环漏判，Sentinel 也会拒绝受保护屏幕上的动作 [F-039]。

## 7. 卡死检测为什么是两段式

只看「屏幕没变」很容易误伤：加载慢、动画、系统弹窗都可能让指纹短暂不变。PhonePal 的处理是 [F-026]：

- 第一次连续 `stuckRepeats = 3` 次不变：清空计数，给模型一条警告，允许它换策略；
- 警告后再次连续不变：返回失败 `STUCK_FAILED`。

这比「一次不变就失败」稳健，也比「永远重试」安全——后者会白白消耗模型调用与用户耐心。

## 8. 一次任务在轨迹里长什么样

每一步都会写 `trace.jsonl`（8 个固定键）[F-071]：

```json
{"time":1761830000000,"run":"r1","kind":"StepPlanned","step":3,"action":{"type":"tap","nodeId":12},"text":null,"ok":null,"decision":null}
{"time":1761830000400,"run":"r1","kind":"StepExecuted","step":3,"action":{"type":"tap","nodeId":12},"text":"click node 12","ok":true,"decision":"allow: allowed"}
```

`decision` 来自同一任务的审计记录，格式 `allow|ask|deny: <原因>`；截图在同目录 `step-<n>.png` [F-071]。用 CLI 的 `traces show <run_id>` 可以把它渲染成表格 [F-073]。

## 9. 这一段代码的边界

- **不做全局规划**：没有「先生成 5 步计划再执行」的逻辑，只有逐步决策；
- **不做视觉定位模型**：节点列表来自无障碍树，截图只是补充；节点里有目标时优先用 `nodeId`；
- **不做动作回滚**：执行失败只反馈，不撤销；
- **不做多任务并行**：`AgentSession` 保证同一时刻只有一个任务 [F-069]。

理解这四条边界，就不会期待它完成「跨 20 步、强依赖前序状态」的复杂任务——那是 `flow.yaml` + `ai` 子目标存在的理由。

## 相关概念

- [一轮聊天：`phone_task` 之前发生什么](02-chat-and-tools.md)
- [安全闸门：每一步都要过的门](04-sentinel.md)
- [无障碍手眼：截图与节点怎么来](07-hands-accessibility.md)
- [技能与 flow：把固定步骤写进 YAML](06-skills-and-flows.md)
