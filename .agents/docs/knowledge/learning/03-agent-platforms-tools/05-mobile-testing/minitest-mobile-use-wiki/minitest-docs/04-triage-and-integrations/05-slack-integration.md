---
title: "Slack集成"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/integrations/mini-in-slack"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/05-slack-integration.toml"
date: "2026-07-07"
tags: ["minitest", "slack", "integration", "chatops", "通知", "运行心跳"]
summary: "详细介绍Slack集成配置，包括安装、频道路由、运行心跳消息、线程内分类操作和账户链接。"
---
> 来源：https://www.minitap.ai/docs/minitest/integrations/mini-in-slack

# Slack集成

Mini作为Slack工作区中的真实参与者工作。安装一次后，您通常在仪表板中执行的操作就会直接在您团队已经工作的频道中发生：启动运行、分类失败标准、起草新故事。

Slack中的Mini是单个集成，但它触及产品的每个部分。本页介绍安装、它添加的界面，以及仅在聊天中有意义的部分（频道路由、账户链接、运行心跳）。

## 安装

在仪表板中，转到 **Workspace settings（工作区设置）→ Integrations（集成）→ Slack** 并点击 **Connect（连接）**。Slack会引导您完成标准的OAuth同意屏幕。批准后，Mini会自动加入工作区中的每个公共频道 — 在几分钟内分批进行以保持在Slack的速率限制内。如果您稍后创建新的公共频道，Mini也会加入该频道。

您不必邀请Mini进入私有频道。如果您希望它在一个私有频道中，从频道内部运行`/invite @mini`。

### 断开连接

在同一位置：**Workspace settings → Integrations → Slack → Disconnect（断开连接）**。Mini会离开所有频道，每个应用的路由规则消失，心跳停止发布。稍后重新连接会恢复OAuth授权；您需要重新选择每个应用的频道。

## 频道路由

每个应用将其运行通知路由到一个Slack频道。从仪表板中的 **App Settings → Slack** 设置：选择频道，保存。机器人会在保存前验证频道存在并且它可以在那里发布。

当您第一次设置频道时，Mini会在那里发布欢迎消息。当您稍后更改它时，Mini会在旧频道发布"moving to #new-channel（移动到#新频道）"提示，并开始使用新频道。当您清除它时，Mini会发布"going quiet（静音）"提示并完全停止为该应用发布。

Mini仍然会在它加入的每个频道中监听`@mini`提及 — 频道路由仅控制**出站**通知降落在何处，而不是您可以在哪里与它交谈。

## 与Mini交谈

Mini在它加入的任何频道中响应`@mini`提及。没有斜杠命令。有关Mini理解的短语完整列表，请参阅[Mini命令参考](https://www.minitap.ai/docs/minitest/reference/mini-commands)。

### 触发运行

两种形式：

```text
@mini run <app name> <build tag or version>
```

构建令牌必须包含数字（因此`v1.2.3`匹配但普通单词不匹配）。Mini模糊匹配应用名称，解析匹配标签的构建，然后发布一个**短暂确认**，带有10秒的`[Cancel] [Run now]`窗口然后启动。如果您不点击，它会在10秒后自动启动。

需要[链接的Slack账户](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#linking-your-account)。

替代措辞：`kick off <app> <tag>`、`trigger <app> build <tag>`、`start <app> on tag <tag>`。

```text
@mini run all tests
```

打开线程中的多步选择器：

1. 选择应用（如果Mini可以从您的消息中猜出则跳过）。
2. 选择用户故事 — 全部或子集。
3. 选择iOS和/或Android构建。
4. 确认。

Mini会发布状态卡并随着运行的进行原地更新。

替代措辞：`run tests`、`test all`、`execute tests`。

有关跨界面的完整情况，请参阅[触发运行](https://www.minitap.ai/docs/minitest/runs/triggering-a-run)。

### 编写用户故事

```text
@mini create test
@mini edit test
@mini delete test
```

每个都会打开多步流程：选择应用，选择用户故事（用于编辑/删除），然后输入名称、描述、验收标准。在分类线程中当有人发现缺失场景时非常有用 — 您可以在不离开对话的情况下捕获它。有关完整心智模型，请参阅[手动编写用户故事](https://www.minitap.ai/docs/minitest/suite/authoring)。

### 状态

```text
@mini status
```

Mini回复应用的最新运行判定结果。如果您的工作区有多个应用，它会首先显示一个选择器。

替代措辞：`verdict`、`latest run`、`what's the latest`。

## 运行心跳

每次运行都会在应用配置的频道中发布一条**心跳消息**。Mini随着运行的进行原地编辑那条单条消息 — 故事完成、发现问题、基础设施暂停、重试开始 — 因此频道不会被填满。编辑每十秒去抖动一次以保持礼貌。

当运行完成时，Mini最后一次重写心跳消息，带有最终判定结果。如果每个故事都通过了，您会得到绿色完成。如果有失败，您会得到带有每个问题跳转链接的细分。

### 问题线程

当运行发现问题时，Mini在心跳上在线程中回复详细信息：失败的标准、严重性、运行报告链接，以及失败时刻的**嵌入视频片段**。三个按钮让您无需离开Slack即可进行分类：

- **Acknowledge（确认）** — 将问题标记为已看到。
- **Not a bug（非bug）** — 打开模态框捕获原因。反馈流回Mini的学习循环。
- **Resolved（已解决）** — 打开模态框捕获如何修复的。

分类后，Mini将操作行替换为状态页脚。如果您改变主意，那里有一个 **Back to review（返回审核）** 按钮。

### 跨频道触发器

如果您从应用配置频道以外的频道触发了运行，Mini会在配置频道发布心跳，并在您触发它的频道中删除一个小的永久链接回复。这样您就可以从对话开始的地方跟踪运行。

## 链接您的账户

您第一次从Slack触发运行或分类问题时，Mini会要求您将Slack身份链接到Minitap账户。点击短暂消息中的链接；它会打开仪表板并在一次点击中完成链接。从那时起，Slack操作归因于您的Minitap用户并尊重您的角色。

Mini还在安装时通过电子邮件将Slack用户与现有Minitap用户匹配 — 如果您的Slack电子邮件和Minitap电子邮件匹配，您会自动链接。

## 功能对照表

| 在Slack中 | 在仪表板中 |
| --- | --- |
| 用`@mini run …`触发运行 | 用**Run tests**按钮触发运行 |
| 查看每次运行的心跳 | 查看带有完整时间线+视频的运行报告 |
| 在线程中用三个按钮分类问题 | 用完整历史+严重性覆盖分类问题 |
| 通过`@mini`编写/编辑/删除用户故事 | 用完整编辑器编写/编辑用户故事 |
| `@mini status`查看最新判定 | 跨每个应用的舰队视图 |

将Slack用于快速、即时的操作，当您需要深入细节时使用仪表板。

---

> **返回章节**：[问题分类与集成总览 →](00-overview.md)
>
> **下一章**：[参考文档 →](../05-reference/00-overview.md)
