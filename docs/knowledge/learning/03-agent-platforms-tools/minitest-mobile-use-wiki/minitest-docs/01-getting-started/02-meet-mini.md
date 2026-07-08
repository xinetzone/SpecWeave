---
title: "认识Mini代理"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/get-started/meet-mini"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/01-getting-started/02-meet-mini.toml"
date: "2026-07-07"
tags: ["minitest", "mini", "ai-agent", "ai-qa", "代理介绍"]
summary: "Mini是miniTest背后的AI QA工程师代理，负责运行测试套件、维护用户故事、在虚拟设备上执行测试并提供可操作的反馈。"
---
> 来源：https://www.minitap.ai/docs/minitest/get-started/meet-mini

# 认识Mini代理

![Mini, the miniTest AI QA engineer](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/meet-mini.svg?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=170c3b77d0045e1dc15f33202759a644)

*Mini，miniTest的AI QA工程师*

## 这就是Mini，您的AI QA工程师

Mini是运行您测试套件的AI代理，从您编写第一个用户故事开始，在之后的每次发布中始终陪伴您。

## 负责维护测试套件

您不需要亲自维护测试套件的健康状态。Mini会读取您的代码库来起草值得测试的故事，并随着应用的成长[提出新的测试故事](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)。它还会从您的问题分类操作中学习：每次您将某事标记为"不是bug"或修复验收标准时，Mini都会在下一次运行中运用这些经验。

## 在虚拟设备上运行

每次运行都在虚拟iOS或Android设备上执行。Mini[直接从GitHub构建您的应用](https://www.minitap.ai/docs/minitest/runs/builds)，因此您无需管理构建产物，并且它会使用[您附加到每个故事的配置文件](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles)进行登录。对于Google登录，它使用Minitap为您维护的账户。

## 呈现关键信息

当出现问题时，Mini会为您提供足够的信息以便采取行动：失败故事的设备视频、失败的确切标准，以及您可以粘贴到Cursor或Claude中的[修复提示](https://www.minitap.ai/docs/minitest/runs/run-report#fix-prompt)。当设备日志有助于解释失败原因时，Mini也会提取这些日志。有了这些信息，您通常无需猜测即可复现bug。

Mini还会标记您没有要求它检查的内容：测试过程中遇到的UX小问题和损坏的边界情况。这些显示为[改进建议](https://www.minitap.ai/docs/minitest/triage/suggestions)，是否值得花时间处理由您决定。

## 您将在哪里看到Mini

### 在仪表板中

这是编写故事、查看运行和分类问题的主要界面。

### 在Slack中

Mini为每次运行发布实时心跳消息，并允许您直接从线程中进行问题分类。

### 在您的Pull Request上

每个PR上都有一个miniTest检查。绿色表示套件在该构建上通过了测试。

### 从您的IDE中

通过MCP服务器从Cursor或Claude编写和编辑用户故事。

---

> **下一章**：[快速开始 →](03-quickstart.md)
