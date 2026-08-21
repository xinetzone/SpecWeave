---
title: "Mini命令参考"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/reference/mini-commands"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/05-reference/05-mini-commands.toml"
date: "2026-07-07"
tags: ["minitest", "slack", "commands", "mini-commands", "聊天命令", "参考"]
summary: "Slack中@Mini支持的所有命令，包括运行命令、编写命令、应用命令及其替代措辞。"
---
> 来源：https://www.minitap.ai/docs/minitest/reference/mini-commands

# Mini命令参考

Mini在它加入的任何频道中响应`@mini`提及。没有斜杠命令。您可以用自然语言表达 — Mini使用LLM对意图进行分类，当未配置API密钥时使用关键字回退。

有关安装、频道路由和运行心跳，请参阅[Slack中的Mini](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack)。

## 运行命令

### 触发标记运行

```text
@mini run <app> <build or tag>
```

构建令牌必须包含数字（因此`v1.2.3`匹配但普通单词不匹配）。Mini模糊匹配应用名称，解析匹配标签的构建，然后发布一个短暂确认，带有10秒窗口：

- **Run now（立即运行）**立即触发。
- **Cancel（取消）**中止。
- 不点击？10秒后自动触发。

需要[链接的Slack账户](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#linking-your-account)。

替代措辞：`kick off <app> <tag>`、`trigger <app> build <tag>`、`start <app> on tag <tag>`。

### 运行所有测试（交互式选择器）

```text
@mini run all tests
```

在线程中打开多步选择器：

1. 选择应用（如果Mini可以从您的消息中猜出则跳过）。
2. 选择用户故事 — 全部或子集。
3. 选择iOS和/或Android构建。
4. 确认。

Mini会发布状态卡并随着运行的进行原地更新。

替代措辞：`run tests`、`test all`、`execute tests`。

### 检查最新判定结果

```text
@mini status
```

Mini回复应用的最新运行判定结果。如果工作区有多个应用且Mini猜不出您指的是哪个，它会首先显示一个下拉菜单。

替代措辞：`verdict`、`latest run`、`what's the latest`。

### 重试运行

```text
@mini retry run
```

即将推出。今天，使用`@mini run all tests`启动新运行。

## 编写命令

### 创建用户故事

```text
@mini create test
```

Mini按顺序引导您完成每个字段：

1. 选择应用（如果可猜出则跳过）。
2. 输入故事名称。
3. 输入验收标准（每行一个）。
4. 审查摘要，然后**Create（创建）**或**Cancel（取消）**。

故事在您确认后立即进入仪表板。

替代措辞：`new test`、`add test`。

### 编辑用户故事

```text
@mini edit test
```

形式与创建相同，但Mini会预填充当前名称和标准，因此您只需要更改需要修改的部分：

1. 选择应用。
2. 从下拉菜单中选择用户故事。
3. 编辑名称。
4. 编辑标准。

提交标准会立即保存（没有单独的确认步骤）。

替代措辞：`modify test`、`update test`、`change test`。

### 删除用户故事

```text
@mini delete test
```

1. 选择应用。
2. 选择用户故事。
3. 确认删除 — **Delete（删除）**或**Cancel（取消）**。

永久删除。故事及其验收标准被移除。

替代措辞：`remove test`。

## 应用命令

### 创建应用

```text
@mini create app
```

1. 输入应用名称。
2. 输入描述（可选）。
3. 选择要链接的GitHub仓库（来自您GitHub App安装的复选框列表），或跳过。
4. 如果链接了多个仓库，选择源（构建）仓库。
5. 审查摘要，然后**Create（创建）**或**Cancel（取消）**。

替代措辞：`new app`、`add app`。

## 当Mini不理解时

如果Mini无法对您的消息分类，它会回复一个列出可用命令的简短帮助卡片。卡片作为线程回复发布，而不是短暂消息，因此频道的其他成员也可以看到它。

---

> **下一章**：[GitHub Action参考 →](06-github-action.md)
