---
title: "GitHub集成"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/integrations/github"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/04-triage-and-integrations/04-github-integration.toml"
date: "2026-07-07"
tags: ["minitest", "github", "integration", "github-app", "pr-check", "ci"]
summary: "详细介绍GitHub集成配置，包括GitHub App安装、PR检查、自动构建、触发运行和分支保护设置。"
---
> 来源：https://www.minitap.ai/docs/minitest/integrations/github

# GitHub集成

miniTest通过单个GitHub App与GitHub通信。每个组织安装一次，它就覆盖该组织中每个连接的应用。

## 连接GitHub是必需的吗？

严格来说，不是 — 您可以通过CLI手动上传构建来测试任何应用。但跳过GitHub连接意味着放弃miniTest许多有用的功能：

- 从代码库[自动生成和维护套件](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)。
- CI触发运行时的自动构建（请参阅[提供应用构建](https://www.minitap.ai/docs/minitest/runs/builds)）。
- Mini出现在您的PR上告诉您是否可以发布。

如果您正在评估miniTest，可以今天跳过GitHub，稍后再添加。如果您日常使用miniTest，请连接它。

## 安装

**Workspace settings（工作区设置）→ Integrations（集成）→ GitHub → Install（安装）**。该流程打开GitHub的App安装屏幕 — 选择组织，然后授予**All repositories（所有仓库）**或**Only selected repositories（仅选定仓库）**。

![Workspace integrations settings showing a connected GitHub org](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/integrations-settings.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=f1502b6a2d8149112a28f229f7d8acc2)

*显示已连接GitHub组织的工作区集成设置*

## 您在PR上看到什么

Mini仅在针对您应用默认分支（通常是`main`）或匹配您配置的[发布分支模式](#mini何时出现)的PR上发布。Monorepo应用还要求PR中至少有一个文件在应用的源文件夹下被更改。

### 粘性评论

Mini在每个PR上发布一条评论。它进行自我介绍，列出每个受影响的应用并带有 **Run tests（运行测试）** 复选框，然后等待您操作 — 它永远不会自己启动运行。

勾选复选框（或在PR评论中发布`@mini test <slug>`）会触发运行。评论随着运行的进行原地编辑，完成后变成完整报告：每个平台的判定结果、严重和警告存储桶带有可展开的故事卡片，以及返回仪表板查看完整时间线和视频的链接。

如果您在评论发布后更改PR — 推送新提交、添加应用 — Mini会编辑评论以匹配。不会有线程垃圾邮件，不会有第二条评论。

### 检查运行

每个CI触发的运行也会在PR上发布GitHub检查：

**检查名称：** `Minitest (AppName)` — 在项目树中不可见，但这是您在分支保护列表中会看到的名称。

- **状态：** queued（排队）→ in progress（进行中）→ completed（完成，success / failure / neutral）。
- 运行期间和终端故障时可用**Cancel（取消）**和**Bypass（绕过）**按钮。

检查结论**默认为neutral（中立）** — 在您开启阻塞之前，Mini不会阻止合并。要要求它通过，请在工作区设置中启用`block_on_test_failures`，然后将检查添加到 **GitHub → Settings → Branches → Branch protection rules → Require status checks**。

## 从PR触发运行

三种路径，都产生相同的运行报告：

### 1. CI Action（推荐）

**为什么选择这条路径。** 您可以精确控制运行何时触发 — 在每次推送时、仅在PR上、在`release-*`标签上，或您想要的任何组合。您拥有工作流文件，因此您决定触发条件。

将`minitap-ai/minitest-trigger@v1`添加到您的`.github/workflows/*.yml`：

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - uses: minitap-ai/minitest-trigger@v1
        with:
          app-slug: my-app
```

该Action通过GitHub OIDC进行身份验证 — 无需API密钥。MiniTest GitHub App必须在第一次运行之前安装在组织上。有关每个输入和构建路径示例，请参阅[GitHub Action参考](https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action)。

### 2. PR评论复选框

勾选Mini粘性评论中的 **Run tests** 复选框会为该应用触发运行。无需工作流文件，无需设置 — GitHub App处理调度。当您正在审查并希望在不等待CI的情况下确认修复时使用此方法。

### 3. /test斜杠命令

在PR上发布`@mini test <app-slug>`，Mini会执行与复选框相同的操作。在同一评论或任何顶级PR评论中都有效。

## Mini何时出现

Mini使用两个规则决定是否在PR上发布粘性评论 — 两者都可以按应用配置：

### 默认分支

针对您应用**默认分支**（通常是`main`）的PR总是会为该应用获得评论。这是您将应用连接到仓库时设置的**源分支**。

### 发布分支模式

您可以在 **App Settings → CI** 下的`release_branch_patterns`中定义**gitignore风格的模式**。针对匹配任何模式的分支（例如`release/*`）的PR即使默认分支不同也会获得评论。

如果PR两者都不匹配（例如它针对功能分支），Mini会保持安静。通过CI Action的检查运行路径无论分支如何都有效。

Monorepo应用有一条额外规则：PR中至少有一个文件必须在应用配置的源文件夹下。仅触及不相关目录的PR会被跳过。

## 从标签触发

如果您推送与应用配置的标签模式匹配的git标签（在 **App Settings → CI** 下的`ci_tag_pattern`中设置），Mini会通过GitHub webhook拾取它并启动运行。无需工作流文件，无需评论 — 纯粹用于发布风格的触发器，如`release-1.2.0`。

## 将应用连接到仓库

在每个应用的 **Settings → Source** 中，指向：

- **Repo（仓库）** (`owner/name`) — 从App可以看到的仓库中自动完成。
- **Branch（分支）** — 默认分支。确定哪些PR获得粘性评论（请参阅[Mini何时出现](#mini何时出现)）以及标签触发运行的基础。
- **Source folder（源文件夹）**（可选）— monorepos的子文件夹。请参阅[提供应用构建](https://www.minitap.ai/docs/minitest/runs/builds)。

## 移除App

`GitHub → Settings → Applications → MiniTest → Configure → Uninstall`。miniTest会保留运行历史和配置，但构建和PR检查会停止。重新安装会恢复一切。

---

> **下一章**：[Slack集成 →](05-slack-integration.md)
