---
title: "智能通知助手"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/examples/smart-notification-assistant"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "examples", "advanced", "profiles", "builder-pattern", "tracing"]
summary: "高级示例，展示多 Profile 配置、TaskRequestBuilder、追踪录制和健壮的异常处理。"
---

# 智能通知助手

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/examples/smart-notification-assistant

本示例演示了适用于更复杂自动化场景的高级 SDK 功能。它会分析通知并根据通知内容采取相应操作。

本示例代码可在 GitHub 获取：[smart_notification_assistant.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/smart_notification_assistant.py)

## 示例功能

本示例自动完成以下任务：
1. 打开通知面板
2. 滚动查看前 3 条未读通知
3. 分析每条通知的应用名称、标题和内容
4. 将消息应用或邮件标记为高优先级
5. 在备忘录应用中创建通知摘要笔记

## 高级特性

### 多 Profile
为不同任务使用不同的 LLM 配置

### TaskRequestBuilder
使用 Builder 模式进行高级任务配置

### 追踪录制
捕获屏幕截图和执行步骤

### 异常处理
针对特定异常的健壮错误处理

## 完整代码

```python
import asyncio
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.types.exceptions import AgentError

class NotificationPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Notification(BaseModel):
    """单条通知详情。"""

    app_name: str = Field(..., description="发送通知的应用名称")
    title: str = Field(..., description="通知的标题/头部")
    message: str = Field(..., description="通知的消息内容")
    priority: NotificationPriority = Field(
        default=NotificationPriority.MEDIUM, description="通知的优先级级别"
    )

class NotificationSummary(BaseModel):
    """所有通知的摘要。"""

    total_count: int = Field(..., description="找到的通知总数")
    high_priority_count: int = Field(0, description="高优先级通知的数量")
    notifications: list[Notification] = Field(
        default_factory=list, description="单条通知的列表"
    )

def get_agent() -> Agent:
    # 创建两个专用 Profile：
    # 1. 用于详细检查任务的分析器 Profile
    analyzer_profile = AgentProfile(
        name="analyzer",
        llm_config=LLMConfig(
            planner=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
            orchestrator=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
            cortex=LLMWithFallback(
                provider="openai",
                model="o4-mini",
                fallback=LLM(provider="openai", model="gpt-5"),
            ),
            executor=LLM(provider="openai", model="gpt-5-nano"),
            utils=LLMConfigUtils(
                outputter=LLM(provider="openai", model="gpt-5-nano"),
                hopper=LLM(provider="openai", model="gpt-4.1"),
            ),
        ),
    )

    # 2. 用于快速操作的动作 Profile
    action_profile = AgentProfile(
        name="note_taker",
        llm_config=LLMConfig(
            planner=LLM(provider="openai", model="o3"),
            orchestrator=LLM(provider="google", model="gemini-2.5-flash"),
            cortex=LLMWithFallback(
                provider="openai",
                model="o4-mini",
                fallback=LLM(provider="openai", model="gpt-5"),
            ),
            executor=LLM(provider="openai", model="gpt-4o-mini"),
            utils=LLMConfigUtils(
                outputter=LLM(provider="openai", model="gpt-5-nano"),
                hopper=LLM(provider="openai", model="gpt-4.1"),
            ),
        ),
    )

    # 配置默认任务设置
    task_defaults = Builders.TaskDefaults.with_max_steps(200).build()

    # 配置 Agent
    config = (
        Builders.AgentConfig
        .add_profiles(profiles=[analyzer_profile, action_profile])
        .with_default_profile(profile=action_profile)
        .with_default_task_config(config=task_defaults)
        .build()
    )
    return Agent(config=config)

async def main():
    # 设置带时间戳的追踪目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    traces_dir = f"/tmp/notification_traces/{timestamp}"
    agent = get_agent()

    try:
        # 初始化 Agent
        await agent.init()

        print("Checking for notifications...")

        # 任务 1：使用分析器 Profile 获取并分析通知
        notification_task = (
            agent.new_task(
                goal="Open the notification panel (swipe down from top). "
                "Scroll through the first 3 unread notifications. "
                "For each notification, identify the app name, title, and content. "
                "Tag messages from messaging apps or email as high priority."
            )
            .with_output_format(NotificationSummary)
            .using_profile("analyzer")
            .with_name("notification_scan")
            .with_max_steps(400)
            .with_trace_recording(enabled=True, path=traces_dir)
            .build()
        )

        # 使用适当的异常处理执行任务
        try:
            notifications = await agent.run_task(request=notification_task)

            # 显示结构化结果
            if notifications:
                print("\n=== Notification Summary ===")
                print(f"Total notifications: {notifications.total_count}")
                print(f"High priority: {notifications.high_priority_count}")

                # 任务 2：创建笔记存储通知摘要
                response = await agent.run_task(
                    goal="Open my Notes app and create a new note summarizing the following "
                    f"information:\n{notifications}",
                    name="email_action",
                    profile="note_taker",
                )
                print(f"Action result: {response}")

            else:
                print("Failed to retrieve notifications")

        except AgentError as e:
            print(f"Agent error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")
            raise

    finally:
        # 清理
        await agent.clean()
        print(f"\nTraces saved to: {traces_dir}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 代码详解

### 1. 定义输出结构

```python
class NotificationPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Notification(BaseModel):
    app_name: str
    title: str
    message: str
    priority: NotificationPriority

class NotificationSummary(BaseModel):
    total_count: int
    high_priority_count: int
    notifications: list[Notification]
```

使用枚举类型表示优先级，确保 LLM 只返回有效值。嵌套的 Pydantic 模型支持复杂的数据结构。

### 2. 创建专用 Profile

```python
analyzer_profile = AgentProfile(
    name="analyzer",
    llm_config=LLMConfig(
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",  # 强大的分析模型
            fallback=LLM(provider="openai", model="gpt-5")
        ),
        # ... 其他组件
    )
)

action_profile = AgentProfile(
    name="note_taker",
    llm_config=LLMConfig(
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",
            fallback=LLM(provider="openai", model="gpt-5")
        ),
        # ... 其他组件
    )
)
```

**分析器 Profile**：使用强大的模型进行详细检查  
**动作 Profile**：针对快速操作进行优化

### 3. 使用多 Profile 配置 Agent

```python
config = (
    Builders.AgentConfig
    .add_profiles(profiles=[analyzer_profile, action_profile])
    .with_default_profile(profile=action_profile)
    .with_default_task_config(config=task_defaults)
    .build()
)
```

### 4. 使用高级选项构建任务

```python
notification_task = (
    agent.new_task(goal)
    .with_output_format(NotificationSummary)  # 结构化输出
    .using_profile("analyzer")                 # 指定 Profile
    .with_name("notification_scan")            # 任务名称
    .with_max_steps(400)                       # 步骤限制
    .with_trace_recording(enabled=True, path=traces_dir)  # 追踪
    .build()
)
```

### 5. 使用异常处理执行

```python
try:
    notifications = await agent.run_task(request=notification_task)
    # 处理结果...
    
except AgentError as e:
    print(f"Agent error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

分别捕获 `AgentError` 和通用异常，提供更精确的错误处理。

## 运行示例

确保已：
1. 配置了所需的 LLM API Key（OpenAI、OpenRouter、Google）
2. 设备上有通知和备忘录应用

运行命令：

```shellscript
python smart_notification_assistant.py
```

## 预期输出

```text
Checking for notifications...

=== Notification Summary ===
Total notifications: 3
High priority: 2

Action result: Note created successfully with notification summary.

Traces saved to: /tmp/notification_traces/20241009_1730
```

## 核心概念演示

### Profile 切换

不同任务使用针对其用途优化的不同 Profile：

```python
# 分析任务使用 "analyzer" Profile
await agent.run_task(goal="Analyze notifications", profile="analyzer")

# 动作任务使用 "note_taker" Profile
await agent.run_task(goal="Create note", profile="note_taker")
```

### Task Builder 模式

复杂配置通过优雅的链式调用处理：

```python
task = (
    agent.new_task(goal)
    .with_output_format(MyModel)
    .with_max_steps(400)
    .with_trace_recording(True)
    .build()
)
```

### 追踪录制

捕获执行过程用于调试：
- 每一步的屏幕截图
- Agent 的决策过程
- 动作执行结果

这对于理解问题发生的原因非常宝贵！

### 嵌套 Pydantic 模型

带验证的复杂数据结构：

```python
class NotificationSummary(BaseModel):
    notifications: list[Notification]  # 嵌套模型列表
```

## 追踪分析

运行后，检查追踪文件：

```shellscript
# 列出追踪文件
ls /tmp/notification_traces/20241009_1730/

# 查看结构
notification_scan/
├── step_001_screenshot.png
├── step_002_screenshot.png
├── step_003_screenshot.png
└── execution_log.json
```

每张屏幕截图显示 Agent 在该步骤看到的内容，帮助调试问题。

## 自定义想法

### 回复高优先级消息

```python
# 回复高优先级消息
for notif in notifications.notifications:
    if notif.priority == NotificationPriority.HIGH:
        await agent.run_task(
            goal=f"Reply to {notif.app_name} message: '{notif.title}'",
            profile="action_profile"
        )
```

### 定时检查

```python
# 仅在工作时间检查
from datetime import datetime

hour = datetime.now().hour
if 9 <= hour <= 17:
    notifications = await agent.run_task(request=notification_task)
```

### 按应用筛选

```python
goal = (
    "Open notification panel. "
    "Find notifications from WhatsApp and Gmail only. "
    "Ignore all other apps."
)
```

## 最佳实践

### 分离 Profile
为分析和动作使用不同的 Profile

### 描述性命名
为任务命名以便于调试

### 启用追踪
在开发过程中始终启用追踪

### 特定异常
分别捕获 AgentError 与通用异常

## 下一步

- **核心概念**：深入了解 Profile 和 Builder
- **SDK 参考**：完整的 TaskRequestBuilder 参考
