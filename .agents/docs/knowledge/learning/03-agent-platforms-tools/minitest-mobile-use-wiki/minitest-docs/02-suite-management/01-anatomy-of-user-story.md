---
title: "用户故事解析"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/suite/anatomy"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/01-anatomy-of-user-story.toml"
date: "2026-07-07"
tags: ["minitest", "user-story", "acceptance-criteria", "用户故事", "验收标准"]
summary: "详细解析用户故事的组成结构，包括名称、类型、描述、验收标准、配置文件、附件和依赖关系。"
---
> 来源：https://www.minitap.ai/docs/minitest/suite/anatomy

# 用户故事解析

**用户故事（User Story）**是对应用中一段用户旅程的描述，为人类读者编写。Mini将其同时作为测试脚本和断言列表。

下面介绍的大部分工作**[由Mini自动为您处理](https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite)**：编写标准、拆分捆绑的断言、停用过时的故事、连接依赖关系。保持手动操作的只有两项：**配置文件（Profiles）**（Mini无法猜测您的凭据）和**文件（Files）**（Mini无法生成您的旅程需要上传的PDF和照片）。阅读本页了解结构即可，不要将其视为需要持续更新的检查清单。

## 用户故事的组成部分

### 名称（Name）

简短、以动作为导向。例如：`邮箱登录`、`添加商品到购物车`。

### 类型（Type）

旅程的类别 — 用于选择图标和颜色，并在列表中对故事进行分组。

#### 内置类型

内置类型涵盖大多数场景 — `Login（登录）`、`Registration（注册）`、`Checkout（结账）`、`Onboarding（引导）`、`Search（搜索）`、`Settings（设置）`、`Navigation（导航）`、`Form（表单）`、`Profile（个人资料）`、`Other（其他）`。

您还可以从类型选择器创建**自定义类型**。自定义类型包含名称、图标、颜色，以及一个可选的使用提示，当该类型的故事运行时，该提示会注入Mini的上下文中。团队通常会添加诸如`Payment（支付）`、`Reservation（预订）`或`Loyalty（会员）`等类型。

类型仅用于分类。它不会自动选择配置文件，也不会改变Mini对故事的评分严格程度。

### 描述（Description）

一句话描述用户的目标。

### 验收标准（Acceptance Criteria）

Mini在运行时评分的可观察条件。

每个标准是一个可观察的条件，用简洁的中英文句子写成。Mini端到端地执行旅程，并根据观察到的情况为每个标准判定通过（PASS）或失败（FAIL）。

```text
1. 首页已显示。
2. "购物车"按钮显示带有"1"的徽标。
3. 点击"结账"打开地址表单。
```

运行时有效的三条规则：

- **每行一个条件。** 如果一个步骤做了两件事，请拆分它。
- **像用户一样说话。** 按照用户的方式引用UI元素，而不是通过无障碍ID。
- **跳过输入步骤。** 当附加了配置文件时，编写关于登录后状态的标准（`已显示登录用户的首页`）— Mini已经拥有到达那里所需的凭据。

编辑标准会对其进行版本控制：现有问题保持与评分时的版本关联，因此当您修改措辞时，您的分类历史不会中断。删除标准会自动解决其未解决的问题。

## 可以附加的内容

除了四个字段之外，还有三个可选部分影响Mini运行故事的方式。

### 配置文件（Profiles）

**配置文件**是当故事需要登录时Mini使用的命名身份。将其附加到故事，Mini会在每次运行时使用它。

大多数应用需要少数几个配置文件 — 一个用于免费用户，一个用于专业用户，如果旅程不同则一个用于管理员。

**创建配置文件**

转到 **App settings（应用设置）→ Test Data（测试数据）→ Profiles（配置文件）→ New profile（新建配置文件）**。配置文件包含：

- **名称（Name）** — 您引用它的方式（`Free user`、`Pro user`、`Admin`）。
- **用户名（Username）** — 邮箱、电话或登录屏幕接受的任何内容。
- **密码（Password）** — 静态加密存储，不再显示，永远不会在运行报告或Slack中回显。
- **关于此用户（About this user）** — Mini作为上下文读取的自由格式备注（账户状态、权益、任何特殊信息）。

您还可以使用[MCP服务器](https://www.minitap.ai/docs/minitest/reference/mcp-tools)从IDE创建配置文件：

```text
Create a "Free user" profile: tester@example.com / ••••••
Attach the "Free user" profile to the "Sign in with email" story
```

**使用Google登录**

如果您的应用使用Google登录，您不需要配置自己的测试账户。Minitap管理一组共享的Google账户 — 它们在配置文件选择器中显示在**Shared by Minitap（Minitap共享）**下。附加一个，Mini会在每次运行时使用它登录。

**按角色配置，而非按人配置**

使用专用测试用户，而不是个人用户。失败的运行可能会使账户处于异常状态（未完成的结账、放弃的购物车），您不希望在真实用户身上清理这些状态。

### 文件（Files）— 用于上传或附加内容的旅程

当旅程需要上传、附加或引用用户提供的内容时，附加**文件** — 头像照片、PDF收据、短音频片段。

Mini会在运行开始前将文件预加载到测试设备上。然后，代理会像真实用户一样从设备的图库、文件应用或文档选择器中选取它们。

支持的类型：图片、文档、视频、音频。

从仪表板中的故事详情附加文件，或在从IDE编写时通过MCP服务器附加。

### 依赖关系（Dependencies）— 用于需要先通过设置故事的故事

一个故事可以依赖其他故事。当父故事失败时，其依赖项在该次运行中会被跳过，而不是重新运行您已知已损坏的旅程。如果登录失败，检查结账就没有意义。

从故事详情设置依赖关系。完整图表显示在依赖关系视图中。

## 在哪里编写

当您需要手动编写时 — 最常见的是配置文件和文件 — 请参阅[编写用户故事](https://www.minitap.ai/docs/minitest/suite/authoring)了解三种界面（Cursor或Claude、Slack、仪表板）以及何时使用每种界面。

---

> **下一章**：[手动编写用户故事 →](02-authoring-stories.md)
