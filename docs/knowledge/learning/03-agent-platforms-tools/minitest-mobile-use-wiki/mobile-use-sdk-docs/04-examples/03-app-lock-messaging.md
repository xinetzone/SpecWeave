---
title: "应用锁消息示例"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/examples/app-lock-messaging"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "examples", "app-lock", "messaging"]
summary: "演示如何使用 App Lock 功能，确保自动化任务始终在特定应用（如 WhatsApp）内执行。"
---

# 应用锁消息示例

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/examples/app-lock-messaging

本示例演示如何使用应用锁（App Lock）功能将自动化限制在特定应用内（本例为 WhatsApp）。即使用户意外导航离开，应用锁也能确保 Agent 保持在消息应用中。

本示例代码可在 GitHub 获取：[app_lock_messaging.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/app_lock_messaging.py)

## 示例功能

本示例自动完成以下任务：
1. 打开 WhatsApp
2. 向多个联系人发送节日祝福消息
3. 如果用户意外离开 WhatsApp，自动重新启动应用
4. 返回发送结果的结构化数据

## 核心概念

### 应用锁
限制执行在特定应用包名/Bundle ID 内

### 自动重启
如果用户意外导航离开，Agent 会重新启动应用

### Builder 模式
使用 TaskRequestBuilder 进行高级配置

### 结构化输出
使用 Pydantic 返回类型化结果

## 完整代码

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

class MessageResult(BaseModel):
    """消息任务的结构化结果。"""

    messages_sent: int = Field(..., description="成功发送的消息数量")
    contacts: List[str] = Field(..., description="收到消息的联系人列表")
    success: bool = Field(..., description="是否所有消息都成功发送")

async def main() -> None:
    # 使用默认配置创建 Agent
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)

    try:
        await agent.init()

        # 使用应用锁保持在 WhatsApp 中执行
        # 这确保 Agent 留在应用内，必要时会重新启动
        task = (
            agent.new_task(
                "Send 'Happy New Year!' message to Alice, Bob, and Charlie on WhatsApp"
            )
            .with_name("send_new_year_messages")
            .with_locked_app_package("com.whatsapp")  # 锁定到 WhatsApp
            .with_output_format(MessageResult)
            .with_max_steps(600)  # 消息任务可能需要更多步骤
            .build()
        )

        print("Sending messages with app lock enabled...")
        print("The agent will stay in WhatsApp and relaunch if needed.\n")

        result = await agent.run_task(request=task)

        if result:
            print("\n=== Messaging Complete ===")
            print(f"Messages sent: {result.messages_sent}")
            print(f"Contacts: {', '.join(result.contacts)}")
            print(f"Success: {result.success}")
        else:
            print("Failed to send messages")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## 代码详解

### 1. 定义输出结构

```python
class MessageResult(BaseModel):
    messages_sent: int = Field(..., description="Number of messages successfully sent")
    contacts: List[str] = Field(..., description="List of contacts messaged")
    success: bool = Field(..., description="Whether all messages were sent successfully")
```

清晰的字段描述帮助 LLM 准确提取数据。

### 2. 创建 Agent 配置

```python
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

确保您的 `llm-config.defaults.jsonc` 包含 Contextor 代理配置以支持应用锁功能。

### 3. 使用应用锁构建任务

```python
task = (
    agent.new_task("Send 'Happy New Year!' message to Alice, Bob, and Charlie on WhatsApp")
    .with_name("send_new_year_messages")
    .with_locked_app_package("com.whatsapp")  # 锁定到 WhatsApp
    .with_output_format(MessageResult)
    .with_max_steps(600)
    .build()
)
```

关键点：
- `with_locked_app_package()` 使用 WhatsApp 包名激活应用锁
- 使用完整的包名（Android: `com.whatsapp`，iOS: `com.whatsapp`）
- 对于包含多次交互的复杂任务，考虑增加 `max_steps`

### 4. 运行任务并处理结果

```python
result = await agent.run_task(request=task)

if result:
    print(f"Messages sent: {result.messages_sent}")
    print(f"Contacts: {', '.join(result.contacts)}")
```

结果类型化为 `MessageResult | None` 以确保类型安全。

## 查找应用包名

### Android

**WhatsApp:**

```shellscript
adb shell pm list packages | grep whatsapp
# 输出: package:com.whatsapp
```

**其他应用:**

```shellscript
adb shell pm list packages | grep [app-name]
```

### iOS

**常用 Bundle ID:**

- WhatsApp: `com.whatsapp`
- Telegram: `ph.telegra.Telegraph`
- 信息: `com.apple.MobileSMS`
- Instagram: `com.burbn.instagram`

## LLM 配置

确保您的 `llm-config.defaults.jsonc` 包含 Contextor 配置：

```jsonc
{
  "contextor": {
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  // ... 其他代理配置
}
```

## 运行示例

确保已：
1. 设备上安装了 WhatsApp
2. WhatsApp 已登录并可以发送消息
3. 配置了包含 Contextor 的 LLM 配置文件

运行命令：

```shellscript
python app_lock_messaging.py
```

## 预期输出

```text
Sending messages with app lock enabled...
The agent will stay in WhatsApp and relaunch if needed.

=== Messaging Complete ===
Messages sent: 3
Contacts: Alice, Bob, Charlie
Success: True
```

## 应用锁工作原理

当您启用应用锁时：

1. **初始启动**：Agent 验证 WhatsApp 是否已打开，如未打开则启动它
2. **运行时监控**：Contextor 代理在每一步监控应用变化
3. **智能决策**：如果用户离开 WhatsApp，Contextor 会决定：
   - 允许偏离（例如 OAuth 流程、系统对话框）
   - 重新启动应用（例如意外导航）
4. **完成**：任务继续执行直到目标达成

---

## 平台应用锁

除了在代码中配置应用锁，您也可以在平台上配置：

### 在平台上配置

在 [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks) 创建任务时：

```text
Name: send-whatsapp-message
Agent Prompt: Send "<message>" to <contact> on WhatsApp
Locked App Package: com.whatsapp
```

任务将显示 🔒 图标，表示已锁定包名。

### 通过 SDK 执行

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

# 平台上配置的应用锁会自动应用
result = await agent.run_task(
    request=PlatformTaskRequest(task="send-whatsapp-message")
)
```

`PlatformTaskRequest` **不支持**通过 SDK 覆盖 `locked_app_package`。要更改锁定的应用，请更新平台任务配置。

### 通过云端执行（无代码）

您也可以直接从平台 UI 运行带应用锁的任务：

1. 前往 [**Tasks**](https://platform.mobile-use.ai/tasks)
2. 点击任务卡片上的 **Run**（显示 🔒 图标）
3. 选择 **Cloud Execution** 标签
4. 选择 LLM Profile 和云设备
5. 点击 **Run Task**

当您希望在所有执行中保持一致的应用限制而无需更改代码时，平台应用锁是理想选择。

## 自定义想法

### 锁定到不同应用

```python
# Telegram
.with_locked_app_package("org.telegram.messenger")

# Signal
.with_locked_app_package("org.signal.android")
```

### 发送给多个联系人

```python
contacts = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
contact_list = ", ".join(contacts)

task = agent.new_task(
    f"Send 'Happy New Year!' to {contact_list} on WhatsApp"
).with_locked_app_package("com.whatsapp")
```

### 使用特定 Profile

```python
# 使用特定 Profile 以获得更高准确性
task = (
    agent.new_task("Send messages to Alice, Bob, Charlie")
    .with_locked_app_package("com.whatsapp")
    .using_profile("accurate")  # 使用更强大的模型
)
```

## 故障排除

### 应用无法启动

```text
Error: Failed to launch com.whatsapp after 3 attempts
```

**解决方案：**

- 验证 WhatsApp 已安装：`adb shell pm list packages | grep whatsapp`
- 确保设备已解锁
- 检查包名是否正确
- 尝试手动启动：`adb shell monkey -p com.whatsapp 1`

### Agent 反复重启应用

如果 Agent 不断重启 WhatsApp：

- 检查 Agent 思考过程，了解它为什么离开
- 任务可能需要在 WhatsApp 外执行操作（例如验证）
- 考虑为该特定操作移除应用锁

## 下一步

- **任务与任务请求**：了解更多任务配置选项
- **Agent 配置**：配置 Contextor 代理设置
- **智能通知助手**：探索更高级的示例
