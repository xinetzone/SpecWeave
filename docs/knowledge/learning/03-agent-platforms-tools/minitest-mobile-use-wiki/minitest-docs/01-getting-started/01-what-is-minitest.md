---
title: "什么是miniTest"
category: "learning"
source: "https://www.minitap.ai/docs/minitest/get-started"
date: "2026-07-07"
tags: ["minitest", "ai-qa", "产品介绍", "overview"]
summary: "miniTest是一款AI驱动的移动端QA测试平台，无需组建QA团队即可为iOS和Android应用提供自动化测试覆盖。"
---

> 来源：https://www.minitap.ai/docs/minitest/get-started

# 什么是miniTest

**Mobile QA coverage you don't have to hire for.**

（无需招聘QA团队即可获得的移动端QA测试覆盖）

如果您正在发布iOS或Android应用却没有自己的QA团队，miniTest正是为您量身打造。Mini是其背后的AI QA工程师代理，它会选择一个构建版本，在虚拟设备上运行您关注的用户故事，并在每次运行结束时给出明确的判定结果。

## 测试结果判定

### ✅ 通过（Passed）

一切正常运行。该构建版本可以安全发布。

### ❌ 失败或 ⚠️ 警告（Failed or Warning）

Mini发现了一个bug。您将获得：
- 问题发生时的设备视频录像
- 详细的复现步骤
- 设备日志
- 可直接粘贴到Cursor或Claude中的修复提示

## 工作原理

miniTest的工作流程如下：

1. **提供构建版本**：通过GitHub自动构建或手动上传应用构建包
2. **编写用户故事**：描述用户在应用中的操作旅程和验收标准
3. **Mini在虚拟设备上执行**：AI代理Mini在云端iOS或Android模拟器上自动操作应用
4. **获得测试报告**：包含每个验收标准的判定结果、视频证据和修复建议

## 后续学习路径

- **认识Mini代理**：了解每次运行、每个问题分类线程、每条Slack消息背后的AI代理
  → [认识Mini](02-meet-mini.md)

- **快速开始**：在虚拟设备上运行您的第一个用户故事（约15分钟）
  → [快速开始](03-quickstart.md)

- **用户故事解析**：了解用户故事的结构，以及验收标准如何成为测试的真实依据
  → [用户故事解析](../02-suite-management/01-anatomy-of-user-story.md)

- **阅读运行报告**：了解代理运行后您将花费最多时间查看的界面
  → [阅读运行报告](../03-running-tests/03-reading-run-report.md)

---

> **下一章**：[认识Mini代理 →](02-meet-mini.md)
