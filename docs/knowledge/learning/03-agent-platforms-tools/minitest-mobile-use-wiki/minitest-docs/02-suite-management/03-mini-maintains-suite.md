---
title: "Mini自动维护套件"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite"
date: "2026-07-07"
tags: ["minitest", "self-maintenance", "自动维护", "套件管理", "ai-maintenance"]
summary: "介绍Mini如何自动读取代码库、生成初始测试套件、添加新功能测试、停用旧功能测试，保持套件与应用同步。"
---

> 来源：https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite

# Mini自动维护套件

测试套件编写容易，保持准确性很难。您的应用在不断变化，套件必须随之变化。

**Mini的自维护功能**正是保持两者同步的机制。Mini读取您的代码库，生成套件的初始版本，并在您发布时保持其最新状态。添加功能时，它会为其起草故事。移除功能时，故事被停用。重塑屏幕时，它会重写标准以匹配新界面。

**需要GitHub集成。**自维护功能读取您的仓库以检测更改。如果没有激活并指向正确仓库的[GitHub集成](https://www.minitap.ai/docs/minitest/integrations/github)，Mini将没有可以监控的内容。

## 覆盖范围

### 微观漂移（Microscopic drift）

按钮重命名、标签调整、表单重新排序。故事保留；标准被重写以匹配当前屏幕上的内容。

### 宏观漂移（Macroscopic drift）

整个功能被移除、新旅程发布。故事被添加或停用。

### 连接组织（Connective tissue）

故事之间的依赖关系自动连接。现有配置文件被链接到需要它们的旅程。

## 工作原理

Mini监控**默认分支**（大多数情况下是`main`）上的提交。当差异有意义时，它会在后台更新套件：起草新故事、停用过时的故事、重写标准以匹配新UI。

您不需要触发它，也不需要审查每个更改。您只需持续发布即可。

## 需要手动处理的内容

有两件事Mini无法仅从代码中推断：

### 新配置文件

如果新旅程需要新身份（测试付费墙的`Pro user`、设置屏幕的`Admin`），系统会提示您提供凭据。现有配置文件会自动链接。

### 设备文件

要上传的照片、要附加的PDF、要播放的音频 — 仓库之外的任何内容。您需要手动附加这些。

两者都可以从[仪表板、IDE或Slack](https://www.minitap.ai/docs/minitest/suite/authoring)完成。

---

> **返回章节**：[测试套件管理总览 →](00-overview.md)
>
> **下一章**：[测试运行 →](../03-running-tests/00-overview.md)
