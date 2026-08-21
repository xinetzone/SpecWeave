---
title: "使用示例"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/examples"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/00-overview.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "examples", "tutorial"]
summary: "Mobile Use SDK 使用示例总览，包含从简单到进阶的多个完整示例。"
---
# 使用示例

本章提供多个完整的 Mobile Use SDK 使用示例，从简单入门到高级功能演示，帮助您快速掌握 SDK 的实际应用。

## 示例列表

| 示例 | 说明 | 核心概念 | 文件 |
|------|------|----------|------|
| 简单照片整理器 | 最基础的入门示例，无需 Builder 或复杂配置 | 默认配置、结构化输出、资源清理 | [01-simple-photo-organizer.md](01-simple-photo-organizer.md) |
| 智能通知助手 | 高级示例，展示多 Profile、任务构建器、追踪录制 | 多 Profile、TaskRequestBuilder、追踪、异常处理 | [02-smart-notification-assistant.md](02-smart-notification-assistant.md) |
| 应用锁消息示例 | 演示 App Lock 功能，限制在特定应用内执行 | App Lock、自动重启、Builder 模式 | [03-app-lock-messaging.md](03-app-lock-messaging.md) |
| 平台任务示例 | 使用 Minitap 平台进行集中式任务编排 | 平台配置、统一 API Key、云端可观测性 | [04-platform-task-example.md](04-platform-task-example.md) |
| 视频录制分析 | 录制并分析设备屏幕上的视频内容 | 视频录制工具、Gemini 视频模型、ffmpeg | [05-video-recording-analysis.md](05-video-recording-analysis.md) |

## 学习路径建议

### 初学者路径
1. 先从 **简单照片整理器** 开始，了解基本的 Agent 创建和任务执行流程
2. 学习如何使用 Pydantic 模型获取结构化输出
3. 掌握 `try/except/finally` 资源清理模式

### 进阶路径
1. 学习 **智能通知助手**，掌握多 Profile 配置和 Builder 模式
2. 了解如何启用追踪录制进行调试
3. 学习特定异常的处理方式

### 功能专项
- **应用锁功能**：参考应用锁消息示例
- **平台集成**：参考平台任务示例
- **视频分析**：参考视频录制分析示例

## 示例代码来源

所有示例代码均可在 GitHub 仓库中找到：
- [simple_photo_organizer.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/simple_photo_organizer.py)
- [smart_notification_assistant.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/smart_notification_assistant.py)
- [app_lock_messaging.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/app_lock_messaging.py)
- [video_transcription_example.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/video_transcription_example.py)
