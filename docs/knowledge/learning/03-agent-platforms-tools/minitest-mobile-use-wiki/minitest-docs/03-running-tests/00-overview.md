---
title: "测试运行总览"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/runs"
date: "2026-07-07"
tags: ["minitest", "test-runs", "builds", "运行测试", "构建版本"]
summary: "测试运行章节导航，包含如何提供应用构建、触发测试运行和阅读运行报告。"
---

# 测试运行

一次运行（Run）会获取您的测试套件（或其中一部分），在虚拟设备上针对一个构建版本执行。本章介绍如何提供应用构建、触发测试运行以及如何解读运行报告。

## 章节导航

| 序号 | 标题 | 内容概要 | 文件 |
|---|---|---|---|
| 1 | 提供应用构建 | 两种提供构建的方式：GitHub自动构建和CLI手动上传，以及Web预览URL配置 | [01-providing-builds.md](01-providing-builds.md) |
| 2 | 触发运行 | 从仪表板、Slack、GitHub Actions、CLI四种方式触发测试运行 | [02-triggering-runs.md](02-triggering-runs.md) |
| 3 | 阅读运行报告 | 运行报告的结构、判定结果、验收标准列表、视频时间线和修复提示 | [03-reading-run-report.md](03-reading-run-report.md) |

## 运行流程概览

```
提供构建 → 触发运行 → Mini在虚拟设备执行 → 查看运行报告 → 问题分类
```

### 提供构建的两种方式

1. **GitHub自动构建**：连接仓库后，Mini在需要时自动拉取代码、编译iOS和Android版本
2. **CLI手动上传**：在本地或自有CI中构建后，通过CLI上传`.apk`或`.ipa`文件

### 触发运行的四种方式

1. **仪表板**：点击**Run tests**按钮，选择构建和故事后启动
2. **Slack**：通过`@mini run`命令在频道中触发
3. **GitHub Actions**：配置`minitest-trigger` Action，在PR时自动运行
4. **CLI**：使用`minitest run`命令从命令行触发

---

> **开始阅读**：[第1章 — 提供应用构建 →](01-providing-builds.md)
