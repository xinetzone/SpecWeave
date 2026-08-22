---
title: "TaskRequestBuilder"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/task-request-builder"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/03-task-request-builder.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "sdk", "builder", "tasks", "api"]
summary: "TaskRequestBuilder 类提供流式接口用于配置带详细选项的任务请求。"
---
# TaskRequestBuilder

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/task-request-builder

`TaskRequestBuilder` 类提供流式接口用于配置带详细选项的任务请求。

## 导入

```python
# 通过 agent.new_task() 访问
task_builder = agent.new_task("Your goal here")

# 或直接导入
from minitap.mobile_use.sdk.builders import TaskRequestBuilder
```

## 创建 Builder

使用 `agent.new_task()` 创建 Builder：

```python
task = agent.new_task("Open settings and check notifications")
```

## 方法

### with_name

设置任务的描述性名称（用于日志和追踪）。

```python
def with_name(self, name: str) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | `str` | 是 | 用于标识的任务名称 |

```python
task = agent.new_task(goal).with_name("notification_check")
```

---

### with_max_steps

设置任务可以执行的最大步骤（动作）数。

```python
def with_max_steps(self, max_steps: int) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `max_steps` | `int` | 是 | `400` | 最大步骤数 |

```python
task = agent.new_task(goal).with_max_steps(500)
```

每个步骤对应 Agent 执行的一个动作（点击、滑动等）。

---

### with_output_format

指定 Pydantic 模型类用于结构化、类型安全的输出。

```python
def with_output_format(
    self, 
    output_format: type[TNewOutput]
) -> TaskRequestBuilder[TNewOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `output_format` | `type[BaseModel]` | 是 | 定义输出结构的 Pydantic 模型类 |

```python
from pydantic import BaseModel, Field

class EmailSummary(BaseModel):
    total: int = Field(..., description="Total emails")
    unread: int = Field(..., description="Unread count")

task = (
    agent.new_task("Check my inbox")
    .with_output_format(EmailSummary)
)
```

使用详细的字段描述帮助 LLM 提取正确的数据。

---

### with_output_description

提供预期输出格式的自然语言描述。

```python
def with_output_description(self, description: str) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `description` | `str` | 是 | 预期输出格式的描述 |

```python
task = (
    agent.new_task("List my contacts")
    .with_output_description("A comma-separated list of contact names")
)
```

---

### using_profile

指定此任务使用哪个 Agent Profile。

```python
def using_profile(self, profile: str | AgentProfile) -> TaskRequestBuilder[TOutput]
```

Profile 名称（字符串）或 AgentProfile 实例。

```python
# 使用 Profile 名称
task = agent.new_task(goal).using_profile("accurate")

# 使用 Profile 实例
from minitap.mobile_use.sdk.types import AgentProfile
profile = AgentProfile(name="fast", from_file="fast.jsonc")
task = agent.new_task(goal).using_profile(profile)
```

---

### with_trace_recording

启用或禁用执行追踪用于调试和可视化。

```python
def with_trace_recording(
    self, 
    enabled: bool = True, 
    path: str | Path | None = None
) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | `bool` | `True` | 是否启用追踪录制 |
| `path` | `str \| Path` | 临时目录 | 保存追踪的目录路径 |

```python
from pathlib import Path

task = (
    agent.new_task(goal)
    .with_trace_recording(enabled=True, path=Path("/tmp/my-traces"))
)
```

追踪包括每一步的屏幕截图，使调试更加容易。

---

### with_llm_output_saving

配置保存最终 LLM 输出的位置。

```python
def with_llm_output_saving(self, path: str) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | `str` | 是 | LLM 输出将保存到的文件路径（将被覆盖） |

```python
task = (
    agent.new_task(goal)
    .with_llm_output_saving(path="/tmp/llm_output.json")
)
```

---

### with_thoughts_output_saving

配置保存 Agent 思考过程的位置。

```python
def with_thoughts_output_saving(self, path: str) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | `str` | 是 | Agent 思考将保存到的文件路径（将被覆盖） |

```python
task = (
    agent.new_task(goal)
    .with_thoughts_output_saving(path="/tmp/agent_thoughts.txt")
)
```

Agent 思考揭示推理过程，有助于理解决策。

---

### without_llm_output_saving

禁用 LLM 输出保存（如果之前已启用）。

```python
def without_llm_output_saving(self) -> TaskRequestBuilder[TOutput]
```

```python
task = agent.new_task(goal).without_llm_output_saving()
```

---

### without_thoughts_output_saving

禁用 Agent 思考保存（如果之前已启用）。

```python
def without_thoughts_output_saving(self) -> TaskRequestBuilder[TOutput]
```

```python
task = agent.new_task(goal).without_thoughts_output_saving()
```

---

### with_locked_app_package

将任务执行锁定到特定应用包名（Android）或 Bundle ID（iOS）。

```python
def with_locked_app_package(self, package_name: str) -> TaskRequestBuilder[TOutput]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `package_name` | `str` | 是 | 应用包名（Android）或 Bundle ID（iOS） |

仅指定包名，不要指定应用的完整路径或 Activity 名称。

启用时：
- 在开始前验证应用是否已打开
- 如果应用不在前台，尝试启动应用
- 在执行期间监控应用变化
- 如果用户意外离开应用，自动重新启动

**Android 示例：**

```python
task = agent.new_task("Send a message")
    .with_locked_app_package("com.whatsapp")
    .build()
```

**iOS 示例：**

```python
task = agent.new_task("Send a message")
    .with_locked_app_package("com.apple.MobileSMS")
    .build()
```

应用锁功能要求在您的 LLM Profile 中配置 Contextor 代理。使用 `adb shell pm list packages`（Android）或查阅 iOS 文档查找正确的包名/Bundle ID。

---

### build

构建并返回最终的 `TaskRequest` 对象。

```python
def build(self) -> TaskRequest[TOutput]
```

#### 返回值

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `task_request` | `TaskRequest[TOutput]` | 构建好的准备执行的任务请求 |

```python
task_request = (
    agent.new_task("Your goal")
    .with_name("my_task")
    .build()
)

# 执行任务
result = await agent.run_task(request=task_request)
```

## 完整示例

```python
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

class AppInfo(BaseModel):
    name: str = Field(..., description="App name")
    version: str = Field(..., description="App version")
    size_mb: float = Field(..., description="App size in MB")

async def main():
    # 设置 Agent
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)
    
    try:
        agent.init()
        
        # 构建综合任务配置
        task = (
            agent.new_task("Go to App Store, search for Instagram, and get app details")
            .with_name("instagram_info")
            .with_max_steps(500)
            .with_output_format(AppInfo)
            .using_profile("default")
            .with_locked_app_package("com.android.vending")  # 锁定到 Google Play 商店
            .with_trace_recording(enabled=True, path=Path("/tmp/instagram-trace"))
            .with_llm_output_saving(path="/tmp/instagram-output.json")
            .with_thoughts_output_saving(path="/tmp/instagram-thoughts.txt")
            .build()
        )
        
        # 执行
        result = await agent.run_task(request=task)
        
        if result:
            print(f"App: {result.name}")
            print(f"Version: {result.version}")
            print(f"Size: {result.size_mb} MB")
        
    finally:
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## 方法链式调用

所有 Builder 方法（除了 `build()`）都返回 Builder 实例，允许流式方法链式调用：

```python
task = (
    agent.new_task("Goal")
    .with_name("task_1")              # 返回 TaskRequestBuilder
    .with_max_steps(400)              # 返回 TaskRequestBuilder
    .with_output_format(MyModel)      # 返回 TaskRequestBuilder
    .with_trace_recording(True)       # 返回 TaskRequestBuilder
    .build()                          # 返回 TaskRequest
)
```

## 类型安全

Builder 维护输出的类型信息：

```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    value: str

# Builder 知道输出类型
task_builder = agent.new_task(goal).with_output_format(MyOutput)

# TaskRequest 类型化为 TaskRequest[MyOutput]
task_request = task_builder.build()

# 结果类型化为 MyOutput | None
result: MyOutput | None = await agent.run_task(request=task_request)
```

## 对比

### 使用 Builder

```python
task = (
    agent.new_task("Check notifications")
    .with_name("notif_check")
    .with_max_steps(300)
    .with_trace_recording(True)
    .with_output_format(NotificationSummary)
    .build()
)

result = await agent.run_task(request=task)
```

✅ 完全控制所有选项  
✅ 类型安全  
✅ 自文档化

### 直接调用

```python
result = await agent.run_task(
    goal="Check notifications",
    name="notif_check",
    output=NotificationSummary
)
```

✅ 简单任务更简单  
❌ 可用选项有限  
❌ 无法配置追踪、最大步骤等

## 下一步

- **Agent SDK**：了解 Agent 类
- **类型**：探索 TaskRequest 和其他类型
