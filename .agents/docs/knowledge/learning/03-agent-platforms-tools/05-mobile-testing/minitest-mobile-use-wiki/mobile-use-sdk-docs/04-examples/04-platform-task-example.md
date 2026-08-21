---
title: "平台任务示例"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/examples/platform-task-example"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/04-platform-task-example.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "examples", "platform", "cloud"]
summary: "演示如何使用 Minitap 平台进行集中式任务编排、统一 API Key 管理和云端可观测性。"
---
# 平台任务示例

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/examples/platform-task-example

本示例演示如何将 mobile-use SDK 与 [Minitap Platform](https://platform.mobile-use.ai/) 配合使用，实现集中式任务编排和可观测性。

## 示例功能

本示例演示：
1. 使用平台配置的任务
2. 在不同 LLM Profile 之间切换
3. 使用 Pydantic 模型获取类型安全的结构化输出
4. 平台错误的异常处理
5. 本地追踪录制与平台可观测性结合

## 核心概念

### 平台配置
任务和 Profile 在 Web UI 上管理

### 统一 API Key
单个 API Key 用于所有 LLM 提供商

### 云端可观测性
在线查看任务运行、追踪和分析数据

### 类型安全
使用 Pydantic 模型进行结构化输出

### 应用锁
限制任务执行在特定应用内

### 云端执行
从 UI 在云设备上运行任务

## 前置条件

在运行本示例之前，请完成 [平台快速开始](https://www.minitap.ai/docs/mobile-use-sdk/platform-quickstart)。

## 完整代码

```python
import asyncio
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest, DevicePlatform
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types.exceptions import PlatformServiceError

# 定义输出结构
class Email(BaseModel):
    sender: str = Field(..., description="邮件发件人名称/地址")
    subject: str = Field(..., description="邮件主题")
    is_unread: bool = Field(..., description="邮件是否未读")

class EmailSummary(BaseModel):
    total_emails: int = Field(..., description="邮件总数")
    unread_count: int = Field(..., description="未读邮件数量")
    recent_emails: List[Email] = Field(
        default_factory=list,
        description="最近邮件列表"
    )

class MeetingInfo(BaseModel):
    title: str = Field(..., description="会议标题")
    date: str = Field(..., description="会议日期")
    time: str = Field(..., description="会议时间")
    attendees: List[str] = Field(..., description="参会人列表")
    confirmed: bool = Field(..., description="会议是否已确认")

async def main():
    """
    演示 Minitap Platform 使用的主执行函数。
    
    本示例展示：
    1. 使用平台配置的任务
    2. 在不同 LLM Profile 之间切换
    3. 带类型安全的结构化输出
    4. 平台错误的错误处理
    """
    
    # 验证 API Key 已配置
    if not os.getenv("MINITAP_API_KEY"):
        print("❌ Error: MINITAP_API_KEY environment variable not set")
        print("   Get your API key from: https://platform.mobile-use.ai/api-keys")
        return
    
    print("🚀 Starting platform task example...\n")
    
    # 使用特定设备配置 Agent
    config = (
        Builders.AgentConfig
        .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
        .build()
    )
    
    agent = Agent(config=config)
    
    try:
        # 初始化 Agent
        print("📱 Initializing agent...")
        if not await agent.init():
            print("❌ Failed to initialize agent")
            return
        print("✅ Agent initialized\n")
        
        # ===================================================================
        # 任务 1：邮件摘要（使用 "default" Profile）
        # ===================================================================
        print("=" * 60)
        print("TASK 1: Email Summary")
        print("=" * 60)
        print("Profile: default")
        print("Task: email-summary (configured on platform)")
        print()
        
        try:
            email_result = await agent.run_task(
                request=PlatformTaskRequest[EmailSummary](
                    task="email-summary",
                    profile="default",
                    # 本地追踪录制（除平台外）
                    record_trace=True,
                    trace_path=Path(f"/tmp/platform-traces/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                )
            )
            
            if email_result:
                print("✅ Email summary retrieved:")
                print(f"   Total emails: {email_result.total_emails}")
                print(f"   Unread: {email_result.unread_count}")
                print(f"\n   Recent emails:")
                for i, email in enumerate(email_result.recent_emails[:5], 1):
                    status = "📬" if email.is_unread else "📭"
                    print(f"   {i}. {status} {email.sender}: {email.subject}")
            else:
                print("⚠️  No result returned")
        
        except PlatformServiceError as e:
            print(f"❌ Platform error: {e}")
            print("   Check that 'email-summary' task exists on platform")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()
        
        # ===================================================================
        # 任务 2：安排会议（使用 "accurate" Profile）
        # ===================================================================
        print("=" * 60)
        print("TASK 2: Schedule Meeting")
        print("=" * 60)
        print("Profile: accurate (more powerful models)")
        print("Task: schedule-meeting (configured on platform)")
        print()
        
        try:
            meeting_result = await agent.run_task(
                request=PlatformTaskRequest[MeetingInfo](
                    task="schedule-meeting",
                    profile="accurate",  # 使用更强大的 Profile
                    record_trace=True,
                    trace_path=Path(f"/tmp/platform-traces/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                )
            )
            
            if meeting_result:
                print("✅ Meeting scheduled:")
                print(f"   Title: {meeting_result.title}")
                print(f"   Date: {meeting_result.date}")
                print(f"   Time: {meeting_result.time}")
                print(f"   Attendees: {', '.join(meeting_result.attendees)}")
                print(f"   Confirmed: {'✅' if meeting_result.confirmed else '⏳'}")
            else:
                print("⚠️  No result returned")
        
        except PlatformServiceError as e:
            print(f"❌ Platform error: {e}")
            print("   Check that 'schedule-meeting' task exists on platform")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()
        
        # ===================================================================
        # 摘要
        # ===================================================================
        print("=" * 60)
        print("📊 Summary")
        print("=" * 60)
        print("✓ View task runs at: https://platform.mobile-use.ai/task-runs")
        print("✓ See execution timelines, screenshots, and agent thoughts")
        print("✓ Analyze performance and debug failures")
        print()
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    
    finally:
        print("🧹 Cleaning up...")
        await agent.clean()
        print("✅ Done!\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## 代码详解

### 1. 定义输出结构

```python
class EmailSummary(BaseModel):
    total_emails: int
    unread_count: int
    recent_emails: List[Email]
```

即使任务在平台上配置，您仍然可以定义 Pydantic 模型以获得类型安全的结果。

### 2. 验证 API Key

```python
if not os.getenv("MINITAP_API_KEY"):
    print("Error: MINITAP_API_KEY not set")
    return
```

在运行任务之前始终检查 API Key 是否已配置。

### 3. 使用不同的 Profile

```python
# 简单任务使用快速、经济高效的 Profile
email_result = await agent.run_task(
    request=PlatformTaskRequest[EmailSummary](
        task="email-summary",
        profile="default"
    )
)

# 复杂任务使用强大的 Profile
meeting_result = await agent.run_task(
    request=PlatformTaskRequest[MeetingInfo](
        task="schedule-meeting",
        profile="accurate"
    )
)
```

### 4. 处理平台错误

```python
try:
    result = await agent.run_task(request=PlatformTaskRequest(...))
except PlatformServiceError as e:
    print(f"Platform error: {e}")
    # 任务未找到、Profile 未找到、认证错误等
except Exception as e:
    print(f"Other error: {e}")
```

## 运行示例

确保已：
1. 设置了 `MINITAP_API_KEY` 环境变量
2. 在平台上创建了所需的任务
3. 连接了 Android 设备或模拟器

运行命令：

```shellscript
python platform_task_example.py
```

## 预期输出

```text
🚀 Starting platform task example...

📱 Initializing agent...
✅ Agent initialized

============================================================
TASK 1: Email Summary
============================================================
Profile: default
Task: email-summary (configured on platform)

✅ Email summary retrieved:
   Total emails: 23
   Unread: 5

   Recent emails:
   1. 📬 j***@***********: Project Update
   2. 📬 s****@*******: Meeting Tomorrow
   3. 📭 n**************@*******: Weekly Digest
   4. 📬 b***@***********: Urgent: Review Needed
   5. 📭 n**********@*******: Latest Tech News

============================================================
TASK 2: Schedule Meeting
============================================================
Profile: accurate (more powerful models)
Task: schedule-meeting (configured on platform)

✅ Meeting scheduled:
   Title: Q4 Planning Session
   Date: 2024-10-15
   Time: 14:00
   Attendees: John, Sarah, Mike
   Confirmed: ✅

============================================================
📊 Summary
============================================================
✓ View task runs at: https://platform.mobile-use.ai/task-runs
✓ See execution timelines, screenshots, and agent thoughts
✓ Analyze performance and debug failures

🧹 Cleaning up...
✅ Done!
```

## 在平台上查看

运行后，访问平台查看详细执行信息：

### 任务运行列表
- 所有任务运行及其状态
- 按任务、状态、日期筛选
- 快速状态概览

### 运行详情
- 执行时间线
- 分步进度
- Agent 思考与推理
- 屏幕截图（如果启用追踪）
- 最终输出
- 错误详情（如果失败）

### 分析
- 成功率
- 平均执行时间
- 最常用任务
- 错误模式

## 平台任务配置

要使本示例正常工作，请在平台上创建以下任务：

### 邮件摘要任务

```text
Name: email-summary
Description: Check and summarize recent emails

Input Prompt:
Open the Gmail app. Navigate to the inbox and check recent emails.
Count total emails and unread emails. Get details (sender, subject, 
unread status) for the 5 most recent emails.

Output Description:
JSON object with total_emails, unread_count, and a list of recent 
emails with sender, subject, and is_unread fields.

Options:
- Enable Tracing: ✅
- Max Steps: 400
```

### 安排会议任务

```text
Name: schedule-meeting
Description: Schedule a calendar meeting

Input Prompt:
Open the Calendar app. Create a new event titled "Q4 Planning Session"
for tomorrow at 2 PM. Add John, Sarah, and Mike as attendees.
Confirm the meeting is created.

Output Description:
JSON object with meeting title, date, time, list of attendees,
and confirmation status.

Options:
- Enable Tracing: ✅
- Max Steps: 500
```

## 使用锁定应用包名运行

您可以将任务执行锁定到特定应用，确保 Agent 留在该应用内：

### 在平台上

创建任务时，指定 **Locked App Package** 字段：

```text
Name: whatsapp-message
Agent Prompt: Send a message to <contact> saying "<message>"
Locked App Package: com.whatsapp
```

### 通过 SDK

使用配置的应用锁执行平台任务：

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

# 平台上配置的应用锁会自动应用
result = await agent.run_task(
    request=PlatformTaskRequest(task="whatsapp-message")
)
```

`PlatformTaskRequest` **不支持**通过 SDK 覆盖 `locked_app_package`。应用锁必须在平台任务本身上配置。

---

## 云端执行（无需代码）

除了通过 SDK 运行任务，您还可以直接从平台 UI 执行：

### 本地 SDK 与云端执行对比

| 方面 | 本地 SDK | 云端执行 |
| --- | --- | --- |
| **设置** | Python + SDK 安装 | 无 |
| **设备** | 物理设备/模拟器 | 云端管理 |
| **适用场景** | 开发、CI/CD | 快速测试、无代码用户 |
| **自定义** | 完全编程控制 | 仅 UI 配置 |

云端执行非常适合非技术团队成员或无需本地环境设置的快速测试。

---

## 自定义想法

### 添加更多任务

在平台上创建更多任务，然后从 SDK 调用它们。

### 创建专用 Profile

为不同类型的任务创建专用 Profile。

### 本地 + 平台混合

```python
# 快速本地测试
await agent.run_task(
    request=TaskRequest(goal="Quick test")
)

# 通过平台进行生产
await agent.run_task(
    request=PlatformTaskRequest(task="production-task")
)
```

### 定时执行

```python
import schedule

async def check_emails():
    result = await agent.run_task(
        request=PlatformTaskRequest(task="email-summary")
    )
    # 处理结果...

schedule.every().hour.do(lambda: asyncio.run(check_emails()))
```

## 展示的优势

### 集中配置
无需更改代码即可修改任务提示词

### 统一 API Key
一个 Key 用于所有 LLM 提供商

### 云端可观测性
在一个仪表板中查看所有运行

### Profile 切换
轻松在模型配置之间切换

### 类型安全
Pydantic 模型确保数据完整性

### 团队协作
与团队共享任务和 Profile

## 故障排除

### 任务未找到错误

```text
PlatformServiceError: Failed to get task: 404
```

**解决方案：**

- 验证任务名称完全匹配（区分大小写）
- 检查任务是否存在于 [https://platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks)
- 确保您使用的是正确的 API Key

### Profile 未找到错误

```text
PlatformServiceError: Failed to get agent profile: 404
```

**解决方案：**

- 检查 Profile 名称拼写
- 验证 Profile 是否存在于 [https://platform.mobile-use.ai/llm-profiles](https://platform.mobile-use.ai/llm-profiles)
- 尝试使用 "default" Profile

### 认证错误

```text
PlatformServiceError: Please provide an API key
```

**解决方案：**

```shellscript
# 设置环境变量
export MINITAP_API_KEY="your_key"

# 或传递给 agent.init()
await agent.init(api_key="your_key")
```

## 下一步

- **平台快速开始**：完整的平台设置指南
- **类型参考**：PlatformTaskRequest 类型文档
- **本地示例**：与本地方法对比
- **仪表板**：打开 Minitap Platform
