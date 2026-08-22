---
title: "快速开始"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/get-started/quickstart"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/01-getting-started/03-quickstart.toml"
date: "2026-07-07"
tags: ["minitest", "quickstart", "快速开始", "入门教程"]
summary: "从注册到运行第一个用户故事的完整快速开始教程，全程约15分钟。"
---
> 来源：https://www.minitap.ai/docs/minitest/get-started/quickstart

# 快速开始

在虚拟设备上运行您的第一个用户故事，全程约15分钟。

## 1. 创建工作区

在 [app.minitap.ai](https://app.minitap.ai/) 注册并按照引导流程操作：选择工作区名称，在拥有您移动端仓库的组织上安装 **MiniTest GitHub App**，然后连接一个应用（名称、图标、仓库、分支）。

![Onboarding — Create your app step with platforms, repo, and feature panel](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/onboarding-app.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=c5b663cb1ce719becd47c9bad62a1402)

*引导流程 — 创建应用步骤，包含平台、仓库和功能面板*

## 2. 编写您的第一个用户故事

在 **User stories（用户故事）** 标签页中，点击 **New story（新建故事）**。用简洁的中文或英文描述用户旅程，让miniTest起草验收标准。

```text
名称：邮箱登录
描述：回访用户登录后进入首页。
```

批准建议的验收标准。这些标准应该是人们仅通过查看屏幕就能验证的内容 — 请参阅[验收标准规则](https://www.minitap.ai/docs/minitest/suite/anatomy)了解运行时有效的标准要求。

![User Stories tab — story list grouped by type on the left, editable acceptance criteria on the right](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/user-story.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=7d1025c57ec9b72ba4f095fb99133d1c)

*用户故事标签页 — 左侧按类型分组的故事列表，右侧可编辑的验收标准*

## 3. 运行测试

打开应用的 **Runs（运行）** 标签页，点击 **New run（新建运行）**。选择最新构建（或通过[CLI](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)上传一个），选择故事，然后点击 **Start（开始）**。

几分钟后，您将看到绿色的标准列表和代理操作应用的视频。如果有失败的情况，运行页面会为您提供准备好用于Cursor或Claude的[修复提示](https://www.minitap.ai/docs/minitest/runs/run-report#fix-prompt)。

![Run report — per-story verdicts and per-criterion detail with video](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/run-report.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=8c8c21d5cb0448ee2d9b03370f2fa514)

*运行报告 — 每个故事的判定结果和带有视频的每个标准详情*

## 后续步骤

- [将miniTest接入GitHub Actions](https://www.minitap.ai/docs/minitest/runs/triggering-a-run)，让每个PR都运行测试套件
- [从IDE编写故事](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)，使用CLI或MCP服务器
- 为需要登录用户的用户故事[附加配置文件](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles)

---

> **返回章节**：[入门指南总览 →](00-overview.md)
>
> **下一章**：[测试套件管理 →](../02-suite-management/00-overview.md)
