---
title: "可观测性与追踪"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/observability"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/04-observability.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "observability", "tracing", "debugging"]
summary: "Mobile Use SDK可观测性功能详解，包括本地追踪记录、Platform GIF上传、调试工具和执行可视化。"
---
# 可观测性与追踪

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/observability

Minitap提供强大的可观测性功能，帮助您调试和理解任务执行过程。无论在本地还是Platform上运行，您都可以捕获Agent行为的详细追踪记录。

## 概述

- **本地追踪**：保存截图和操作日志到本地文件系统
- **Platform GIF上传**：动画GIF自动上传到Platform以便轻松查看

## 工作原理

当`record_trace=True`（默认值）时：
1. 从截图创建本地GIF动画
2. 对于Platform任务，GIF自动上传到云存储
3. 即使上传失败，本地GIF始终会保存
4. 通过API密钥进行访问控制 - 只有您可以查看您的追踪记录

---

## 本地追踪记录

启用追踪记录以在本地保存截图和操作日志。

### 基本用法

```python
task = (
    agent.new_task("Check my notifications")
    .with_trace_recording(enabled=True)
    .build()
)

result = await agent.run_task(request=task)
```

### 自定义路径

```python
from pathlib import Path

task = (
    agent.new_task("Open settings")
    .with_trace_recording(
        enabled=True,
        path=Path("./my-traces")
    )
    .build()
)
```

### 保存内容

本地追踪包括：
- **trace.gif**：显示整个执行过程的动画GIF。它是每个Agent步骤后拍摄的截图汇编。
- **steps.json**：运行期间Agent思考和推理的汇编，包含时间戳。

---

## Platform GIF上传

运行Platform任务时，追踪记录会自动上传到Minitap云存储，以便在Web UI中轻松查看。

### 自动上传（默认）

Platform任务默认上传GIF追踪。您无需指定`record_trace=True`：

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

# record_trace默认为True - GIF自动在本地创建并上传
result = await agent.run_task(
    request=PlatformTaskRequest(task="my-task-name")
)

# 控制台输出：
# 🌐 View on platform: https://platform.mobile-use.ai/task-runs/abc123
```

### 禁用上传（可选）

要禁用云上传同时保留本地GIF创建，设置`record_trace=False`：

```python
result = await agent.run_task(
    request=PlatformTaskRequest(
        task="my-task-name",
        record_trace=False  # 跳过云上传，本地GIF仍然创建
    )
)
```

### 手动任务

手动任务（使用`ManualTaskConfig`）也支持GIF上传：

```python
from minitap.mobile_use.sdk.types import (
    PlatformTaskRequest,
    ManualTaskConfig
)

result = await agent.run_task(
    request=PlatformTaskRequest(
        task=ManualTaskConfig(
            goal="Check Android version",
            task_name="version_check"
        )
        # record_trace默认为True（省略）
    )
)
```

---

## 查看Platform追踪

### SDK运行列表

导航到[SDK Runs](https://platform.mobile-use.ai/sdk-runs)查看所有任务执行及GIF预览：

每个运行卡片显示：
- 任务状态
- 执行时长
- 使用的LLM配置文件
- GIF缩略图预览

### 任务运行详情

点击"View details"查看完整执行追踪：

详情页面包括：
- 输入提示和输出
- 可播放的执行GIF
- 开始时间和持续时间
- LLM配置文件配置
- Agent思考和推理

使用GIF播放器逐步查看执行过程，识别问题发生的位置。

---

## 配置参考

### PlatformTaskRequest参数

| 参数 | 类型 | 默认值 | 描述 |
|---|---|---|---|
| `record_trace` | `bool` | `true` | 控制GIF创建和上传。当`True`（默认）时，在本地创建GIF并上传到Platform。设置为`False`禁用云上传（本地GIF仍创建） |
| `trace_path` | `Path` | 系统临时目录 | 保存追踪文件的本地目录 |

### 示例

```python
import asyncio
from pathlib import Path
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

async def main():
    agent = Agent()
    agent.init()

    result = await agent.run_task(
        request=PlatformTaskRequest(
            task="check-notifications",
            profile="default",
            # 如果省略，record_trace默认为True。
            # 自定义本地路径使用trace_path=Path("./local-traces")，省略则存储在临时文件夹。
        )
    )

    print(f"Result: {result}")
    agent.clean()

asyncio.run(main())
```

### 控制台输出

```shellscript
[INFO] 📂✅ Traces located in: /tmp/mobile-use-traces/notification_check_success_20250121_083345
[INFO] 🌐 View on platform: https://platform.mobile-use.ai/task-runs/cm73x8e9q0001l508xyz123
```

---

## 故障排除

### 上传失败

如果GIF上传失败，请检查：

**文件大小限制**

最大GIF大小为**300MB**。长时间运行的任务（+1小时）可能超过此限制。在任务配置中减少`max_steps`或拆分为多个较短的任务。

### 验证上传成功

检查控制台输出中的Platform URL：

```shellscript
🌐 View on platform: https://platform.mobile-use.ai/task-runs/{id}
```

如果看到此消息，说明上传成功。点击链接查看您的追踪记录。

### Platform上缺少GIF

如果GIF未出现在Platform上：
1. **检查任务状态** - GIF上传在任务完成后发生
2. **确认record_trace=True** - 默认值为true，但确认未被禁用
3. **检查控制台是否有错误** - 查找上传失败消息
4. **刷新页面** - 浏览器缓存可能显示旧数据

---

## 最佳实践

追踪功能默认启用以便于调试。在处理敏感数据或在生产环境运行大量任务时禁用它：

```python
# 处理敏感数据时禁用
result = await agent.run_task(
    request=PlatformTaskRequest(
        task="sensitive-task",
        record_trace=False  # 不记录GIF
    )
)
```

---

## 下一步

- [Platform快速开始](../02-quickstarts/02-platform-quickstart.md) - 了解更多Platform任务执行
- [Task Request Builder](../05-sdk-reference/03-task-request-builder.md) - 探索所有任务配置选项
- [故障排除](../06-troubleshooting/01-troubleshooting.md) - 常见问题和解决方案
- [使用示例](../04-examples/00-overview.md) - 查看完整工作示例
