---
title: "故障排除与反馈"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/troubleshooting"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "troubleshooting", "debugging", "feedback", "support"]
summary: "故障排除与反馈章节包含常见问题诊断、解决方案和反馈指南。"
---

# 故障排除与反馈

本章节帮助您诊断和解决使用 Mobile Use SDK 时遇到的常见问题，并提供了向开发团队提供反馈的指南。

## 章节导航

| 页面 | 说明 |
|------|------|
| [常见问题排查](./01-troubleshooting.md) | 设备连接、服务器、任务执行、LLM/API、系统环境等常见问题的诊断和解决方案 |
| [反馈指南](./02-providing-feedback.md) | 如何提交 Bug 报告、功能建议，以及获取社区支持 |

## 快速参考

在遇到问题时，可以先尝试以下快速解决方案：

### 清理僵尸服务器
```python
agent.clean(force=True)
agent.init()
```

### 检查设备连接
```shellscript
# Android
adb devices

# iOS
idevice_id -l
```

### 启用调试日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 启用追踪
```python
task = agent.new_task(goal).with_trace_recording(True).build()
```

### 重置 ADB
```shellscript
adb kill-server
adb start-server
```

## 相关资源

- [异常处理参考](../05-sdk-reference/05-exceptions.md) - 详细的异常类说明
- [SDK 参考](../05-sdk-reference/00-overview.md) - 完整的 SDK API 文档
- [使用示例](../04-examples/00-overview.md) - 可运行的代码示例
