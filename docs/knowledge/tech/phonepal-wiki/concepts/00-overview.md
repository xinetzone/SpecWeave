---
type: Concept
title: "PhonePal 全景：一个「框架 + 技能」的手机助手"
description: "用一分钟心智模型理解 PhonePal：聊天模型负责理解、操作模型负责点屏幕、Sentinel 在模型之外把关、技能与记忆都是可读文件；附关键数字、能力边界与阅读路径"
tags: [phonepal, overview, android, agent, accessibility]
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

# PhonePal 全景：一个「框架 + 技能」的手机助手

PhonePal 是一个跑在 Android 手机上的开源私人助手。用户在它自己的聊天界面里说「帮我打车回家」，它去其他 App 里完成；说「记住我家在某某路」，它写进一个 Markdown 笔记；说「把 Wi-Fi 打开」，它直接操作系统设置。新场景不用改 APK——加一个带 `SKILL.md` 的小文件夹即可。

这一页给你一个能在五分钟内建立起来的心智模型，以及「它到底不是什么」的边界。

## 1. 一分钟心智模型

一次「帮我打车回家」实际发生了四件事：

```mermaid
flowchart LR
    U[用户：帮我打车回家] --> C[聊天模型 CHAT]
    C -->|memory_search| M[(记忆 Markdown)]
    C -->|list_skills / 技能索引| S[(技能文件夹)]
    C -->|phone_task(goal, skill)| O[操作循环 OPERATOR]
    O -->|截屏 + 节点列表| O
    O -->|一步动作| G{Sentinel}
    G -->|allow| D[无障碍服务执行]
    G -->|ask| A[用户确认卡]
    G -->|deny| O
    D --> O
    O -->|结果摘要| C
    C -->|回复| U
    O -->|成功后写 howto| M
```

1. **聊天模型**（`ModelRole.CHAT`）读懂目标，查记忆、挑技能，然后调用 `phone_task` 工具 [F-014/F-030]。
2. **操作模型**（`ModelRole.OPERATOR`）看不到聊天历史，只看到「目标 + 技能说明 + 相关记忆 + 最近几步 + 当前屏幕截图和节点列表」，每一步输出一个 JSON 动作 [F-025/F-029]。
3. **Sentinel** 在模型之外做 allow/ask/deny 判定；技能只能追加确认词，删不掉内置词 [F-039/F-042]。
4. **结果**回到聊天模型，由它用自然语言总结；任务成功时把操作路径写成 `howto/<技能或包名>` 笔记，下次同类任务会作为参考 [F-024]。

## 2. 四个角色，各管一段

| 角色 | 输入 | 输出 | 代码位置 |
|---|---|---|---|
| 聊天模型 | 用户消息、技能索引、记忆命中、历史 20 条 | 文字回复或工具调用 | `PhonePalAgent.handle` [F-021] |
| 工具层 | 6 个工具调用 | JSON 结果（错误也转成 JSON） | `AgentTools` / `ChatTools` [F-030/F-031] |
| 操作循环 | 屏幕 + 提示词分节 | 一个 `Action`，经 Sentinel 后执行 | `OperatorLoop.run` [F-025] |
| 安全闸门 | 动作 + 屏幕 + 技能 | `Allow` / `Ask` / `Deny` + 审计记录 | `PolicySentinel` [F-039/F-041] |

技能和记忆不是「模型的一部分」，而是**文件系统里的数据**：技能是 `SKILL.md`（+ 可选 `flow.yaml`），记忆是 Basic Memory 格式的 Markdown [F-019/F-045]。

## 3. 关键数字（全部可在源码中复核）

| 项 | 数值 | 说明 |
|---|---|---|
| Gradle 模块 | 8 | 5 个 `core-*` + `hands` + `app` + `cli`（CLI 不在 Gradle 内）[F-001] |
| 动作类型 | 11 | `tap`、`long_press`、`swipe`、`type`、`back`、`home`、`launch`、`deeplink`、`wait`、`ask_user`、`finish` [F-012] |
| 聊天工具 | 6 | 5 个记忆/技能工具 + `phone_task` [F-030] |
| 技能通道 | 6 | `api/cli/deeplink/gui/deeplink-then-gui/mixed` [F-019] |
| 技能 frontmatter 键 | 7 | 未知键会报错，防拼写错误静默丢字段 [F-054] |
| flow 步骤类型 | 8 | `launch/deeplink/ai/confirm/tap/type/wait/assert` [F-056] |
| 内置确认词 | 17 | 支付、转账、发送、删除、下单、确认呼叫…… [F-042] |
| 默认最大步数 | 30 | 可在设置里调到 1..200 [F-008/F-079] |
| 操作模型每步节点上限 | 120 | `AgentConfig.maxNodes` [F-008] |
| 无障碍压缩节点上限 | 200 | `NodeCompactor.DEFAULT_MAX_NODES` [F-064] |

> 关于「8 个模块」和「9 个目录」：README 的目录树里还有 `cli/`、`skills/examples/`、`docs/`、`scripts/`，但它们不是 Gradle 模块 [F-001/F-006]。讨论「模块」时以 8 为准，讨论「顶层目录」时以 README 为准。

## 4. 它不是什么（边界比功能更重要）

| 常见误解 | 实际情况 |
|---|---|
| 「一个全能模型直接看屏幕操作」 | 两个模型分工：CHAT 只谈话与调工具，OPERATOR 只做单步动作 [F-014] |
| 「安全靠 system prompt 约束」 | 安全是 `PolicySentinel` 的代码规则，模型无法关闭；技能只能追加确认词 [F-039/F-042] |
| 「技能是插件/脚本，能执行任意代码」 | 技能只是 `SKILL.md` + 声明式 `flow.yaml`，没有代码执行入口 [F-019/F-020] |
| 「记忆是向量数据库」 | 记忆是 Markdown 文件夹 + 内存 BM25 索引，可直接用 Obsidian 编辑 [F-045/F-048] |
| 「能操作 iOS」 | 不支持：iOS 不允许一个 App 读取或操作其他 App（README 明确写出）[F-080] |
| 「能操作任意 App 的任意界面」 | 依赖无障碍节点与截图；受保护页面（FLAG_SECURE）会被识别并转交用户 [F-063] |
| 「云端 Agent」 | 模型调用走网络，但设备观察、动作执行、记忆与安全判定都在手机本地 |

## 5. 版本与运行前提

- Android 11（API 30）及以上；`compileSdk = 35` [F-003/F-080]。
- 任意兼容 OpenAI `/chat/completions` 的服务：需要配置两个模型，聊天模型与能看图的屏幕操作模型。
- 记忆与技能目录在外部文件根（`/sdcard/Android/data/dev.phonepal.app/files/`）下：`memory/`、`skills/`、`traces/` [F-067]。
- 构建需要 JDK 17 与 Android SDK 35；CI 会跑单元测试、组装 debug APK、CLI 测试与示例技能 lint [F-003/F-076]。

## 6. 建议阅读路径

| 你的目标 | 读这几篇 |
|---|---|
| 先搞懂它怎么替我点手机 | 本篇 → [分层与依赖](01-architecture.md) → [操作循环](03-operator-loop.md) → [安全闸门](04-sentinel.md) |
| 我想写一个技能 | [技能与 flow](06-skills-and-flows.md) → [记忆](05-memory.md) → [示例：技能解剖](../examples/01-skill-anatomy.md) |
| 我想抄它的 Agent 架构 | [分层与依赖](01-architecture.md) → [一轮聊天](02-chat-and-tools.md) → [操作循环](03-operator-loop.md) → [工程模式](10-engineering-patterns.md) |
| 我想做中文记忆检索 | [记忆](05-memory.md) |
| 我想接新设备或换模型 | [无障碍手眼](07-hands-accessibility.md) → [模型客户端](08-llm-client.md) |

## 相关概念

- [分层与依赖：8 个模块如何拼起来](01-architecture.md)
- [一轮聊天：系统提示词与 6 个工具](02-chat-and-tools.md)
- [操作循环：观察 → 一步动作 → 反馈](03-operator-loop.md)
- [安全闸门：模型之外的 allow / ask / deny](04-sentinel.md)
- [信源登记](../references/00-source-inventory.md)
