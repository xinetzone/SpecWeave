---
title: "触发运行"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/runs/triggering-a-run"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/03-running-tests/02-triggering-runs.toml"
date: "2026-07-07"
tags: ["minitest", "trigger-run", "触发运行", "dashboard", "slack", "github-actions", "cli"]
summary: "介绍从仪表板、Slack、GitHub Actions、CLI四种方式触发测试运行的方法。"
---
> 来源：https://www.minitap.ai/docs/minitest/runs/triggering-a-run

# 触发运行

一次运行会获取您的套件（或其中一部分），并在虚拟设备上针对一个构建运行。有四种启动方式；选择适合您工作方式的即可。

## 从仪表板触发

在任何应用页面点击 **Run tests（运行测试）**。侧边面板引导您完成两个步骤：

1. **选择构建。** 使用配置分支的最新构建，选择特定提交或构建ID，上传新的`.apk` / `.ipa`，或粘贴PWA URL。
2. **选择故事。** 运行**全部**故事（默认），或从可搜索列表中缩小到子集。

点击 **Start run（开始运行）**，Mini会在下一个可用设备上将其排队。仪表板的Runs标签页实时更新。

最适合演示前的一次性检查、验证您刚刚推送的修复，或对来自第三方CI的构建进行健全性检查。

## 从Slack触发

有两种方式，都通过`@mini`实现。没有斜杠命令。

**内联输入运行命令。** 用应用和构建标签@Mini：

```text
@mini run acme-checkout v1.4.2
```

Mini会发布一个短暂的确认消息，带有10秒的取消窗口，然后启动。心跳消息会降落在您为该应用配置的频道中（请参阅[频道路由](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#channel-routing)）。

**或者打开选择器。** 对于引导式流程：

```text
@mini run all tests
```

Mini会发布一条交互式消息，引导您完成应用 → 构建 → 故事 → 确认。

从Slack触发需要您的Slack用户链接到Minitap账户。请参阅[链接您的账户](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#linking-your-account)。

## 从GitHub Actions触发（CI）

这是驱动[PR检查](https://www.minitap.ai/docs/minitest/integrations/github)的路径。设置一次，Mini会在每个PR上运行您的套件：它构建头部提交，运行故事，并将判定结果发布回PR。

设置是您仓库中的一个工作流文件，调用 **[`minitap-ai/minitest-trigger`](https://github.com/minitap-ai/minitest-trigger)** GitHub Action。该Action上传构建（或要求Mini构建一个）并启动运行，通过工作流的GitHub OIDC令牌进行身份验证 — 无需管理API密钥。

```yaml
name: miniTest

on:
  pull_request:
    branches: [main]

jobs:
  run-suite:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # OIDC认证必需
      contents: read
    steps:
      - uses: minitap-ai/minitest-trigger@v1
        with:
          app-slug: my-app
```

将该文件放在`.github/workflows/`中，推送到您的默认分支，就完成了。`MiniTest GitHub App`（请参阅[GitHub集成](https://www.minitap.ai/docs/minitest/integrations/github)）必须已安装在组织上 — 这是Mini能够将判定结果发布回PR的前提。

默认配置构建头部提交，运行每个故事，并在PR上发布检查和粘性评论。对于每个输入参数 — `run-ios`、`run-android`、`ios-build-path`、`android-build-path`、`user-story-types`、`tenant-id`、`cancel-previous-runs` — 请参阅[GitHub Action参考](https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action)。

### 必需检查与信息性检查

PR检查**默认是信息性的**。要使Mini成为合并的必需条件，请在工作区设置中启用`block_on_test_failures`，并将检查添加到 **GitHub → Settings → Branches → Branch protection rules → Require status checks**。有关GitHub App在PR上发布的所有内容 — 粘性评论、检查运行、复选框和斜杠命令触发器 — 请参阅[GitHub集成](https://www.minitap.ai/docs/minitest/integrations/github)。

### 重新运行

- 在粘性PR评论中切换 **Run tests** 复选框。
- 或者在PR评论中发布`/test`。
- 或者在仪表板运行报告上点击 **Re-run（重新运行）**。

## 从CLI触发

两个命令，取决于范围。

**单个故事：**

```shellscript
minitest run start <user-story-id> \
  --ios-build <build-id> \
  --android-build <build-id>
```

**整个套件：**

```shellscript
minitest run all \
  --ios-build <build-id> \
  --android-build <build-id>
```

两者都接受`--watch`将状态流式传输到您的终端，而不是打印运行ID并退出。使用`minitest auth login`登录一次。有关其他所有内容，请参阅[CLI参考](https://www.minitap.ai/docs/minitest/reference/cli-commands)。

有关如何处理结果，请参阅[阅读运行报告](https://www.minitap.ai/docs/minitest/runs/run-report)。

---

> **下一章**：[阅读运行报告 →](03-reading-run-report.md)
