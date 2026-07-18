---
title: "测试套件管理总览"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/suite"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/minitest-docs/02-suite-management/00-overview.toml"
date: "2026-07-07"
tags: ["minitest", "test-suite", "用户故事", "套件管理"]
summary: "测试套件管理章节导航，包含用户故事结构、手动编写方法和Mini自动维护机制。"
---
# 测试套件管理

测试套件（Suite）是miniTest为您的应用运行的所有用户故事的集合。本章介绍用户故事的结构、如何手动编写测试故事，以及Mini如何自动维护套件与应用同步。

## 章节导航

| 序号 | 标题 | 内容概要 | 文件 |
|---|---|---|---|
| 1 | 用户故事解析 | 用户故事的组成部分、验收标准规则、配置文件、附件和依赖关系 | [01-anatomy-of-user-story.md](01-anatomy-of-user-story.md) |
| 2 | 手动编写用户故事 | 在仪表板、Slack、IDE（Cursor/Claude）三种界面中编写和编辑故事 | [02-authoring-stories.md](02-authoring-stories.md) |
| 3 | Mini自动维护套件 | Mini如何读取代码库自动生成和更新测试套件，保持与应用同步 | [03-mini-maintains-suite.md](03-mini-maintains-suite.md) |

## 核心概念

### 用户故事（User Story）

用户故事是对应用中一段用户旅程的描述，用人类可读的语言编写。Mini将其同时作为测试脚本和断言列表。

### 验收标准（Acceptance Criteria）

每个用户故事包含若干验收标准，每条标准是一个可观察的条件，Mini在运行时根据观察到的情况判定通过（PASS）或失败（FAIL）。

### Mini的自维护能力

**大部分套件维护工作由Mini自动完成**：编写标准、拆分捆绑的断言、停用过时的故事、连接依赖关系。需要手动处理的只有两项：
- **配置文件（Profiles）**：Mini无法猜测您的登录凭据
- **设备文件（Files）**：Mini无法生成您的旅程需要上传的PDF和照片

---

> **开始阅读**：[第1章 — 用户故事解析 →](01-anatomy-of-user-story.md)
