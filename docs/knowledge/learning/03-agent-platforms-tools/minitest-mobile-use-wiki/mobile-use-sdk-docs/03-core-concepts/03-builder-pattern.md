---
title: "Builder模式"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/builders"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/03-builder-pattern.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "builder-pattern", "fluent-api"]
summary: "Mobile Use SDK Builder模式详解，提供流式、类型安全的API来配置Agent和任务。"
---
# Builder模式

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/builders

Mobile Use SDK提供builder类，提供流式、类型安全的方式来配置Agent和任务。Builder使复杂配置更具可读性，并有助于防止错误。

## 为什么使用Builder？

### 可读性好
链式方法调用实现清晰、自文档化的代码

### 类型安全
在开发时捕获配置错误

### 灵活性强
无需重写代码即可轻松调整配置

### 可发现性
IDE自动补全显示所有可用选项

---

## Builder总览

SDK通过`Builders`对象提供对builders的访问：

```python
from minitap.mobile_use.sdk.builders import Builders

# Agent配置
agent_config = Builders.AgentConfig...

# 任务默认值
task_defaults = Builders.TaskDefaults...
```

---

## Agent Config Builder

配置Agent如何连接到设备和服务器：

### 基本用法

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile

profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)

agent = Agent(config=config)
```

### 可用方法

#### with_default_profile

设置任务的默认Agent配置文件

```python
config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)
```

#### add_profile / add_profiles

注册其他配置文件

```python
config = (
    Builders.AgentConfig
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .build()
)
```

#### for_device

定位到特定设备而非自动检测

```python
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(
        platform=DevicePlatform.ANDROID,
        device_id="emulator-5554"
    )
    .build()
)
```

#### with_adb_server

配置ADB服务器连接

```python
config = (
    Builders.AgentConfig
    .with_adb_server(host="localhost", port=5037)
    .build()
)
```

#### with_default_task_config

为所有任务设置默认配置

```python
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

config = (
    Builders.AgentConfig
    .with_default_task_config(task_defaults)
    .build()
)
```

### 完整示例

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile, DevicePlatform

# 创建配置文件
fast_profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
accurate_profile = AgentProfile(name="accurate", from_file="accurate-config.jsonc")

# 配置任务默认值
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

# 构建全面的Agent配置
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .with_adb_server(host="localhost", port=5037)
    .with_default_task_config(task_defaults)
    .build()
)

agent = Agent(config=config)
```

---

## Task Request Builder

创建详细的任务配置：

### 基本用法

```python
task = (
    agent.new_task("Open settings and check notifications")
    .with_name("check_notifications")
    .build()
)

result = await agent.run_task(request=task)
```

### 可用方法

#### with_name

设置用于日志记录的描述性名称

```python
task = agent.new_task(goal).with_name("my_task").build()
```

#### with_max_steps

限制操作次数

```python
task = agent.new_task(goal).with_max_steps(300).build()
```

#### with_output_format

指定Pydantic模型用于输出

```python
task = (
    agent.new_task(goal)
    .with_output_format(MyModel)
    .build()
)
```

#### with_output_description

描述预期输出格式

```python
task = (
    agent.new_task(goal)
    .with_output_description("A comma-separated list")
    .build()
)
```

#### using_profile

使用特定的Agent配置文件

```python
task = (
    agent.new_task(goal)
    .using_profile("accurate")
    .build()
)
```

#### with_trace_recording

启用执行追踪

```python
from pathlib import Path

task = (
    agent.new_task(goal)
    .with_trace_recording(enabled=True, path=Path("/tmp/traces"))
    .build()
)
```

#### with_llm_output_saving

将最终LLM输出保存到文件

```python
task = (
    agent.new_task(goal)
    .with_llm_output_saving(path="/tmp/output.json")
    .build()
)
```

#### with_thoughts_output_saving

将Agent推理保存到文件

```python
task = (
    agent.new_task(goal)
    .with_thoughts_output_saving(path="/tmp/thoughts.txt")
    .build()
)
```

### 完整示例

```python
from pathlib import Path
from pydantic import BaseModel, Field

class EmailSummary(BaseModel):
    total: int = Field(..., description="Total number of emails")
    unread: int = Field(..., description="Number of unread emails")

task = (
    agent.new_task("Open Gmail and analyze my inbox")
    .with_name("gmail_analysis")
    .with_max_steps(400)
    .with_output_format(EmailSummary)
    .using_profile("accurate")
    .with_trace_recording(enabled=True, path=Path("/tmp/gmail-trace"))
    .with_llm_output_saving(path="/tmp/gmail-output.json")
    .with_thoughts_output_saving(path="/tmp/gmail-thoughts.txt")
    .build()
)

result = await agent.run_task(request=task)
```

---

## Task Defaults Builder

设置适用于所有任务的默认值：

```python
from minitap.mobile_use.sdk.builders import Builders

# 配置默认值
defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .with_trace_recording(enabled=True)
    .build()
)

# 应用到Agent
config = (
    Builders.AgentConfig
    .with_default_task_config(defaults)
    .build()
)

agent = Agent(config=config)

# 所有任务将继承这些默认值
await agent.run_task(goal="Any task here")
```

---

## 方法链式调用

Builders使用方法链式调用实现流式配置：

```python
# 每个方法返回builder实例
result = (
    agent.new_task("My goal")
    .with_name("task_1")          # 返回TaskRequestBuilder
    .with_max_steps(300)          # 返回TaskRequestBuilder
    .with_trace_recording(True)   # 返回TaskRequestBuilder
    .build()                      # 返回TaskRequest
)
```

链式调用多个方法时使用括号和换行符以提高可读性。

## 类型安全

Builders提供编译时类型检查：

```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    value: str

# 类型安全：MyOutput或None
task = agent.new_task(goal).with_output_format(MyOutput).build()
result: MyOutput | None = await agent.run_task(request=task)

# 可以安全访问字段
if result:
    print(result.value)  # IDE知道'value'存在
```

---

## 对比：使用 vs 不使用Builder

### ✅ 使用Builder

```python
task = (
    agent.new_task("Check notifications")
    .with_name("notification_check")
    .with_max_steps(200)
    .with_trace_recording(True)
    .build()
)

result = await agent.run_task(request=task)
```

✅ 清晰可读
✅ 类型安全
✅ 易于修改

### ❌ 不使用Builder

```python
# 直接方法调用，参数众多
result = await agent.run_task(
    goal="Check notifications",
    name="notification_check",
    # max_steps需要TaskRequest...
    # 追踪记录需要TaskRequest...
)
```

❌ 直接调用选项有限
❌ 可发现性差
❌ 难以自定义

---

## 最佳实践

### 复杂配置使用Builder

当需要多个配置选项时，Builder效果最佳

### 简单任务可以使用直接调用

对于基本任务，`agent.run_task(goal="...")`就足够了

### 创建可重用配置

一次构建常用配置并重用它们

### 利用IDE自动补全

让您的IDE建议可用的builder方法

---

## 下一步

- [Agent SDK参考](../05-sdk-reference/01-agent-class.md) - 详细的Agent SDK参考
- [Task Builder SDK参考](../05-sdk-reference/03-task-request-builder.md) - 完整的TaskRequestBuilder参考
