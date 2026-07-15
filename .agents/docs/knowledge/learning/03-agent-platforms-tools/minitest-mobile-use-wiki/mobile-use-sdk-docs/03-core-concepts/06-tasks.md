---
title: "任务与任务请求"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/tasks"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/06-tasks.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "tasks", "structured-output", "workflows"]
summary: "任务与任务请求详解，包括目标定义、结构化输出、任务配置选项、Builder模式和多步工作流。"
---
# 任务与任务请求

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/tasks

任务代表要在移动设备上执行的自动化工作流。它们使用自然语言目标定义，并可返回结构化、类型安全的结果。

## 任务特性

### 基于目标
使用自然语言定义您想要完成什么

### 可追踪
记录执行过程用于调试和可视化

### 结构化输出
返回类型化的Pydantic模型

---

## Platform任务

**使用Platform？** 在[platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks)上创建任务，并使用`PlatformTaskRequest`执行它们。

### 创建Platform任务

1. 转到Platform上的[**Tasks**](https://platform.mobile-use.ai/tasks)
2. 点击**Create Task**
3. 配置任务详情：
    - **Name**：唯一标识符（例如`check-notifications`）
        - **Agent Prompt**：详细指令
        - **Output Description**：可选的结构化输出格式
        - **Locked App Package**：可选的应用包名以限制执行（例如`com.whatsapp`）
4. 在代码中使用：

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

result = await agent.run_task(
    request=PlatformTaskRequest(task="check-notifications")
)
```

### 带结构化输出的Platform任务

```python
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk.types import PlatformTaskRequest

class NotificationSummary(BaseModel):
    total: int = Field(..., description="Total notifications")
    unread: int = Field(..., description="Unread count")

result = await agent.run_task(
    request=PlatformTaskRequest[NotificationSummary](
        task="check-notifications",
        profile="fast"  # 可选：使用特定platform配置文件
    )
)

if result:
    print(f"Total: {result.total}, Unread: {result.unread}")
```

### 带锁定应用包的Platform任务

在Platform上创建任务时，您可以指定**Locked App Package**以将Agent限制在特定应用：

```text
Name: send-whatsapp-message
Agent Prompt: Send the message "<message>" to <contact> on WhatsApp
Locked App Package: com.whatsapp
```

任务将显示带有锁定包名的🔒指示符。

**使用`<locked-app-package>`占位符：**

您可以在Agent提示中使用`<locked-app-package>`占位符引用锁定的应用包：

```text
Open <locked-app-package> and navigate to settings
```

此占位符将在执行时自动替换为配置的包名。

### Platform任务优势

- **集中管理**：在Platform上更新任务提示，无需重新部署代码
- **内置可观测性**：在Platform上查看执行详情、成本和Agent思考
- **团队协作**：在组织内共享任务
- **版本控制**：随时间追踪任务配置的更改

---

## 本地任务

对于本地开发，直接在代码中定义任务：

### 简单字符串输出

运行本地任务的最基本方式：

```python
result = await agent.run_task(
    goal="Open settings and enable dark mode"
)
print(result)  # 字符串输出
```

### 使用Pydantic的结构化输出

获取类型安全、经过验证的输出：

```python
from pydantic import BaseModel, Field

class ThemeSettings(BaseModel):
    dark_mode_enabled: bool = Field(..., description="Whether dark mode is enabled")
    theme_name: str = Field(..., description="Name of the current theme")

result = await agent.run_task(
    goal="Check the current theme settings",
    output=ThemeSettings
)

print(f"Dark mode: {result.dark_mode_enabled}")
print(f"Theme: {result.theme_name}")
```

### 带输出描述

为非结构化输出提供指导：

```python
result = await agent.run_task(
    goal="Find all my unread emails",
    output="A comma-separated list of email subjects"
)
```

---

## 任务选项

### 命名任务

为任务提供描述性名称用于日志记录：

```python
await agent.run_task(
    goal="Send a message to John",
    name="send_message_john"
)
```

### 使用不同配置文件

为特定任务切换Agent配置文件：

```python
await agent.run_task(
    goal="Analyze this complex form",
    profile="detail_oriented"  # 使用不同的LLM配置
)
```

### 最大步数

控制Agent可以执行的操作数量：

```python
task = (
    agent.new_task("Complete checkout process")
    .with_max_steps(500)  # 默认值为400
    .build()
)

await agent.run_task(request=task)
```

### 应用锁

将任务执行限制在特定应用：

```python
task = (
    agent.new_task("Send a message to Alice")
    .with_locked_app_package("com.whatsapp")  # Android包名或iOS bundle ID
    .build()
)

await agent.run_task(request=task)
```

启用应用锁时，Agent将：
- 开始前验证应用已打开
- 如果不在前台，尝试启动它
- 执行期间监控应用更改
- 必要时自动重新启动

---

## 任务Builder模式

对于高级配置，使用builder模式：

```python
task_request = (
    agent.new_task("Open settings and check notifications")
    .with_name("check_notification_settings")
    .with_max_steps(300)
    .with_output_description("Summary of notification settings")
    .with_locked_app_package("com.android.settings")
    .with_trace_recording(enabled=True)
    .build()
)

result = await agent.run_task(request=task_request)
```

---

## 追踪和调试

启用追踪记录以捕获截图和执行步骤：

```python
from pathlib import Path

task = (
    agent.new_task("Navigate to profile settings")
    .with_trace_recording(
        enabled=True,
        path=Path("/tmp/my-traces")
    )
    .build()
)

await agent.run_task(request=task)
```

追踪包括每步截图，便于调试失败的任务。

---

## 保存输出

### 保存LLM输出

将最终LLM响应保存到文件：

```python
task = (
    agent.new_task("Extract product information")
    .with_llm_output_saving(path="/tmp/llm_output.json")
    .build()
)
```

### 保存Agent思考

捕获Agent的推理过程：

```python
task = (
    agent.new_task("Book a restaurant reservation")
    .with_thoughts_output_saving(path="/tmp/agent_thoughts.txt")
    .build()
)
```

---

## 复杂输出结构

定义复杂的嵌套输出结构：

```python
from pydantic import BaseModel, Field
from typing import List

class Email(BaseModel):
    sender: str
    subject: str
    preview: str
    is_unread: bool

class InboxSummary(BaseModel):
    total_emails: int = Field(..., description="Total number of emails")
    unread_count: int = Field(..., description="Number of unread emails")
    emails: List[Email] = Field(..., description="List of recent emails")

result = await agent.run_task(
    goal="Open Gmail and analyze my inbox",
    output=InboxSummary
)

for email in result.emails:
    if email.is_unread:
        print(f"Unread: {email.subject} from {email.sender}")
```

---

## 任务执行流程

任务执行遵循以下流程：

1. **初始化**：验证任务配置，准备环境
2. **规划**：Planner将目标分解为子目标
3. **执行循环**：
   - Contextor收集设备状态
   - Cortex分析屏幕并做出决策
   - Executor执行操作
   - 重复直到目标完成或达到最大步数
4. **输出提取**：Outputter生成结构化结果
5. **清理**：保存追踪记录，释放资源

---

## 最佳实践

### 目标要具体

```python
# ✅ 好 - 具体
goal="Open Weather app, check temperature for New York, and tell me if it will rain tomorrow"

# ❌ 不好 - 模糊
goal="Check weather"
```

### 使用Pydantic进行结构化输出

定义清晰的字段描述以帮助LLM理解要提取什么

```python
class WeatherInfo(BaseModel):
    temperature: float = Field(..., description="Current temperature in Celsius")
    will_rain_tomorrow: bool = Field(..., description="Whether rain is forecast for tomorrow")
```

### 将复杂任务分解为简单任务

与其运行一个复杂任务，不如按顺序运行多个简单任务

```python
# 步骤1：导航
await agent.run_task(goal="Open banking app and go to transactions")

# 步骤2：提取数据
transactions = await agent.run_task(
    goal="Get the last 5 transactions",
    output=TransactionList
)
```

### 调试时启用追踪

开发或调试任务时始终启用追踪

```python
task = agent.new_task(goal).with_trace_recording(enabled=True).build()
```

---

## 示例：多步工作流

### Platform模式

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

class ShoppingResults(BaseModel):
    products: List[Product]
    total_found: int

async def shop_online():
    agent = Agent()
    agent.init()
    
    try:
        # 步骤1：搜索（在Platform上配置的任务）
        await agent.run_task(
            request=PlatformTaskRequest(task="search-products")
        )
        
        # 步骤2：提取结果（在Platform上配置的任务）
        results = await agent.run_task(
            request=PlatformTaskRequest[ShoppingResults](
                task="extract-product-results"
            )
        )
        
        # 步骤3：过滤和操作
        for product in results.products:
            if product.in_stock and product.price < 50:
                print(f"Good deal: {product.name} - ${product.price}")
        
    finally:
        agent.clean()
```

### 本地模式

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from minitap.mobile_use.sdk import Agent

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

class ShoppingResults(BaseModel):
    products: List[Product]
    total_found: int

async def shop_online():
    agent = Agent(...)  # 使用本地配置文件配置
    agent.init()
    
    try:
        # 步骤1：搜索
        await agent.run_task(
            goal="Open Amazon app and search for 'bluetooth headphones'",
            name="search_products"
        )
        
        # 步骤2：提取结果
        results = await agent.run_task(
            goal="Get the first 5 product results with names, prices, and availability",
            output=ShoppingResults,
            name="extract_products"
        )
        
        # 步骤3：过滤和操作
        for product in results.products:
            if product.in_stock and product.price < 50:
                print(f"Good deal: {product.name} - ${product.price}")
        
    finally:
        agent.clean()
```

---

## 下一步

- [Agent配置](05-agent-profiles.md) - 自定义Agent行为
- [Task Builder SDK参考](../05-sdk-reference/03-task-request-builder.md) - 详细的任务配置SDK
- [使用示例](../04-examples/00-overview.md) - 真实世界的任务示例
