---
title: "手动编写用户故事"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/suite/authoring"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/02-authoring-stories.toml"
date: "2026-07-07"
tags: ["minitest", "user-story", "authoring", "编写用户故事", "仪表板", "Slack", "IDE"]
summary: "介绍在仪表板、Slack、IDE（Cursor/Claude）三种界面中手动编写和编辑用户故事的方法。"
---
> 来源：https://www.minitap.ai/docs/minitest/suite/authoring

# 手动编写用户故事

您的测试套件是Mini针对每个构建运行的用户故事列表。[Mini大部分时间为您维护套件](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)，但当您想手动介入时，以下界面始终可用。

无论您使用哪种界面，[故事结构](https://www.minitap.ai/docs/minitest/suite/anatomy)都是相同的 — 名称、类型、描述、验收标准，以及可选的配置文件或文件。

## 在仪表板中编写

这是最容易开始的地方，也是您编辑时可以看到整个套件的唯一场所。

转到 **App（应用）→ Stories（故事）**，点击 **New story（新建故事）**。对话框涵盖所有内容：

- **名称（Name）**和**类型（Type）**（登录、结账等 — 或您为此应用定义的自定义类型）。
- **描述（Description）** — 一句话说明故事验证什么。
- **验收标准（Acceptance criteria）** — 每行一个断言。按Enter添加下一个。
- 可选地绑定[配置文件](https://www.minitap.ai/docs/minitest/suite/anatomy#profiles)或附加[文件](https://www.minitap.ai/docs/minitest/suite/anatomy#files)。
- 可选地声明依赖关系 — 如果故事需要另一个故事先通过（例如结账依赖登录）。

编辑现有故事的工作方式相同。删除标准会对更改进行版本控制，并自动解决与该标准关联的任何未解决问题 — 请参阅[用户故事解析](https://www.minitap.ai/docs/minitest/suite/anatomy)。

## 在Slack中编写

适合在不离开发现问题的频道的情况下进行快速编辑。

用简洁的中英文表达意图并@Mini：

```text
@mini create test
```

Mini会通过按钮和输入引导您完成：选择应用、命名故事、列出标准、确认。

![Mini creating a user story in a Slack thread](https://mintcdn.com/minitap-30239763/wLvqfpOkfUc7rcKB/minitest/images/slack-test-creation.png?w=2500&fit=max&auto=format&n=wLvqfpOkfUc7rcKB&q=85&s=6a24c7513a2e90a7f204a0fc1e20e5e7)

*Mini在Slack线程中创建用户故事*

编辑或删除的形式相同：

```text
@mini edit test
@mini delete test
```

当您正在阅读[问题分类](https://www.minitap.ai/docs/minitest/triage/issues)线程时，意识到套件缺少您刚刚确认的bug的故事，并想在忘记之前添加一个时，这非常方便。故事在您确认后立即进入仪表板。

有关完整的意图界面，请参阅[Slack中的Mini](https://www.minitap.ai/docs/minitest/integrations/mini-in-slack#talking-to-mini)。

## 在IDE中编写（Cursor或Claude）

您的编码代理已经知道您刚刚发布的功能，因此它可以为您编写故事。有两种方法连接到miniTest，它们可以做相同的事情：

### 选项1 — MCP服务器

在编辑器中安装miniTest MCP服务器。仪表板的引导流程为您提供一行命令：

```shellscript
npx add-mcp https://testing-service.app.minitap.ai/mcp/ -g -n minitest
```

您的代理在首次使用时会提示您进行身份验证。之后，用简洁的中英文要求它编写或编辑故事，它会在向您展示差异后通过`create_user_story` / `update_user_story`路由。

有关完整界面，请参阅[MCP工具参考](https://www.minitap.ai/docs/minitest/reference/mcp-tools)。

### 选项2 — 带有捆绑技能的CLI

安装CLI，进行身份验证，然后以相同的方式询问您的代理。CLI附带一个捆绑的技能，因此您编辑器的代理使用与您在shell中使用的相同的`minitest`命令。

有关安装步骤和完整CLI介绍，请参阅[Cursor和Claude集成](https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude)。

---

> **下一章**：[Mini自动维护套件 →](03-mini-maintains-suite.md)
