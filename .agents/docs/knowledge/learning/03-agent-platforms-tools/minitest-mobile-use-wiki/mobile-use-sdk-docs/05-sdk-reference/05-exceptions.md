---
title: "异常处理"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/exceptions"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/05-exceptions.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "sdk", "exceptions", "error-handling", "debugging"]
summary: "mobile-use SDK 中的异常类参考，包括异常层次结构、常见原因、解决方案和最佳实践。"
---
# 异常处理

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/exceptions

mobile-use SDK 异常类参考。

## 导入

```python
from minitap.mobile_use.sdk.types.exceptions import (
    MobileUseError,
    AgentError,
    AgentProfileNotFoundError,
    AgentTaskRequestError,
    AgentNotInitializedError,
    AgentInvalidApiKeyError,
    DeviceError,
    DeviceNotFoundError,
    ServerError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    PlatformServiceError,
)
```

## 异常层次结构

```text
MobileUseError (基类)
├── AgentError
│   ├── AgentNotInitializedError
│   ├── AgentTaskRequestError
│   │   ├── AgentProfileNotFoundError
│   │   └── AgentInvalidApiKeyError
├── DeviceError
│   └── DeviceNotFoundError
├── ServerError
│   └── ServerStartupError
├── ExecutableNotFoundError
├── PlatformServiceUninitializedError
└── PlatformServiceError
```

## 基类异常

### MobileUseError

所有 SDK 错误的基类异常。

```python
from minitap.mobile_use.sdk.types.exceptions import MobileUseError

try:
    await agent.run_task(goal="...")
except MobileUseError as e:
    print(f"SDK 错误: {e}")
```

使用此异常可以捕获任何与 SDK 相关的错误。

---

## Agent 异常

### AgentError

Agent 相关错误的基类异常。

```python
from minitap.mobile_use.sdk.types.exceptions import AgentError

try:
    await agent.run_task(goal="...")
except AgentError as e:
    print(f"Agent 错误: {e}")
```

---

### AgentNotInitializedError

在初始化之前调用 Agent 方法时引发。

**常见原因：** 在 `init()` 之前调用 `run_task()`

```python
from minitap.mobile_use.sdk.types.exceptions import AgentNotInitializedError

agent = Agent()

try:
    # 这将引发 AgentNotInitializedError
    await agent.run_task(goal="Check notifications")
except AgentNotInitializedError:
    print("Agent 未初始化。请先调用 agent.init()。")
```

**解决方案：**

```python
agent = Agent()
agent.init()  # 先初始化
await agent.run_task(goal="Check notifications")
```

---

### AgentProfileNotFoundError

指定的配置文件未找到时引发。

**常见原因：** 使用了未注册的配置文件名称

```python
from minitap.mobile_use.sdk.types.exceptions import AgentProfileNotFoundError

try:
    await agent.run_task(
        goal="Some task",
        profile="non_existent_profile"
    )
except AgentProfileNotFoundError as e:
    print(f"配置文件未找到: {e}")
```

**解决方案：**

```python
# 确保配置文件已注册
profile = AgentProfile(name="my_profile", from_file="config.jsonc")
config = Builders.AgentConfig.add_profile(profile).build()
agent = Agent(config=config)
```

---

### AgentTaskRequestError

任务请求验证错误时引发。

**常见原因：**
- 无效的任务配置
- 参数冲突

```python
from minitap.mobile_use.sdk.types.exceptions import AgentTaskRequestError

try:
    # 无效配置
    task = agent.new_task("").build()  # 空目标
except AgentTaskRequestError as e:
    print(f"无效的任务请求: {e}")
```

---

### AgentInvalidApiKeyError

Minitap API 密钥无效或未授权时引发。

**常见原因：**
- API 密钥不正确
- API 密钥已过期
- API 密钥未设置

```python
from minitap.mobile_use.sdk.types.exceptions import AgentInvalidApiKeyError
from minitap.mobile_use.sdk.types import PlatformTaskRequest

try:
    # 使用无效的 API 密钥
    result = await agent.run_task(
        request=PlatformTaskRequest(
            task="check-notifications",
            api_key="invalid_key"
        )
    )
except AgentInvalidApiKeyError:
    print("API 密钥无效。请从 https://platform.mobile-use.ai/api-keys 获取新密钥")
```

**解决方案：**

```python
# 在 .env 中设置有效的 API 密钥
MINITAP_API_KEY=your_valid_key_here
MINITAP_BASE_URL=https://platform.mobile-use.ai/api/v1  # 可选，这是默认值
```

---

## 设备异常

### DeviceError

设备相关错误的基类异常。

```python
from minitap.mobile_use.sdk.types.exceptions import DeviceError

try:
    agent.init()
except DeviceError as e:
    print(f"设备错误: {e}")
```

---

### DeviceNotFoundError

未找到设备或设备断开连接时引发。

**常见原因：**
- 没有设备连接
- USB 调试未启用
- 操作期间设备拔出

```python
from minitap.mobile_use.sdk.types.exceptions import DeviceNotFoundError

try:
    agent.init()
except DeviceNotFoundError:
    print("未找到设备。请连接设备并启用 USB 调试。")
```

**解决方案：**

1. **检查设备连接：**

```shellscript
# Android
adb devices

# iOS
idevice_id -l
```

2. **启用 USB 调试**（Android）
3. **显式指定设备：**

```python
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="your_device_id")
    .build()
)
```

---

## 服务器异常

### ServerError

服务器相关错误的基类异常。

```python
from minitap.mobile_use.sdk.types.exceptions import ServerError

try:
    agent.init()
except ServerError as e:
    print(f"服务器错误: {e}")
```

---

### ServerStartupError

服务器启动失败时引发。

**常见原因：**
- 端口已被占用
- 缺少依赖项（Android 需要 ADB，iOS 需要 idb）
- 权限问题

```python
from minitap.mobile_use.sdk.types.exceptions import ServerStartupError

try:
    agent.init()
except ServerStartupError as e:
    print(f"启动服务器失败: {e}")
```

**解决方案：**

1. **强制清理僵尸服务器：**

```python
agent.clean(force=True)  # 清理现有服务器
agent.init()
```

2. **验证平台工具已安装：**

```shellscript
# Android
adb version

# iOS
idb --help
```

---

## 可执行文件异常

### ExecutableNotFoundError

在 PATH 中未找到所需的系统可执行文件时引发。

**常见原因：**
- 未安装 `adb`（用于 Android）
- 未安装 `idb`（用于 iOS）
- 未安装 `xcrun`（用于 macOS 上的 iOS）

```python
from minitap.mobile_use.sdk.types.exceptions import ExecutableNotFoundError

try:
    agent.init()
except ExecutableNotFoundError as e:
    print(f"缺少可执行文件: {e}")
```

**解决方案：**

1. **安装 ADB**（用于 Android）：

```shellscript
# 访问: https://developer.android.com/tools/adb
# 或使用包管理器
brew install android-platform-tools  # macOS
sudo apt install adb                 # Linux
```

2. **安装 idb**（用于 iOS）：

```shellscript
brew install idb-companion
```

3. **安装 Xcode 命令行工具**（用于 iOS）：

```shellscript
xcode-select --install
```

---

## 平台异常

### PlatformServiceUninitializedError

在未正确初始化的情况下尝试使用平台功能时引发。

**常见原因：**
- 环境中未设置 `MINITAP_API_KEY`
- PlatformTaskRequest 中未提供 API 密钥
- 平台服务未配置

```python
from minitap.mobile_use.sdk.types.exceptions import PlatformServiceUninitializedError
from minitap.mobile_use.sdk.types import PlatformTaskRequest

try:
    # 缺少 API 密钥
    result = await agent.run_task(
        request=PlatformTaskRequest(task="check-notifications")
    )
except PlatformServiceUninitializedError:
    print("平台服务未初始化。请在 .env 中设置 MINITAP_API_KEY")
```

**解决方案：**

```shellscript
# 添加到 .env 文件
MINITAP_API_KEY=your_api_key_here
MINITAP_BASE_URL=https://platform.mobile-use.ai/api/v1  # 可选，这是默认值
```

或直接提供 API 密钥：

```python
result = await agent.run_task(
    request=PlatformTaskRequest(
        task="check-notifications",
        api_key="your_api_key_here"
    )
)
```

---

### PlatformServiceError

平台服务相关错误的基类异常。

**常见原因：**
- 网络连接问题
- 平台 API 错误
- 平台上的任务配置无效

```python
from minitap.mobile_use.sdk.types.exceptions import PlatformServiceError

try:
    result = await agent.run_task(
        request=PlatformTaskRequest(task="my-task")
    )
except PlatformServiceError as e:
    print(f"平台服务错误: {e}")
```

**解决方案：**

1. 检查网络连接
2. 验证任务在平台上存在
3. 在 [platform.mobile-use.ai](https://platform.mobile-use.ai/) 检查平台状态

---

## 异常处理最佳实践

### 1. 始终清理资源

```python
agent = Agent()

try:
    agent.init()
    await agent.run_task(goal="...")
except MobileUseError as e:
    print(f"错误: {e}")
finally:
    agent.clean()  # 始终清理
```

### 2. 处理特定异常

```python
from minitap.mobile_use.sdk.types.exceptions import (
    AgentNotInitializedError,
    DeviceNotFoundError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    AgentInvalidApiKeyError,
)

try:
    agent.init()
    await agent.run_task(goal="...")
    
except ExecutableNotFoundError as e:
    print(f"缺少所需可执行文件: {e}")
    
except DeviceNotFoundError:
    print("请连接设备")
    
except ServerStartupError:
    print("服务器启动失败。尝试 agent.clean(force=True)")
    
except AgentNotInitializedError:
    print("请先调用 agent.init()")
    
except PlatformServiceUninitializedError:
    print("平台服务未初始化。请设置 MINITAP_API_KEY")
    
except AgentInvalidApiKeyError:
    print("API 密钥无效。请访问 https://platform.mobile-use.ai/api-keys")
    
except Exception as e:
    print(f"意外错误: {e}")
    raise
```

### 3. 检查初始化状态

```python
agent = Agent()

if not agent.init():
    print("初始化失败")
    exit(1)

# 安全地继续
await agent.run_task(goal="...")
```

### 4. 重试逻辑

```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        agent.init()
        break
    except ServerStartupError:
        if attempt < max_retries - 1:
            print(f"重试 {attempt + 1}/{max_retries}")
            agent.clean(force=True)
            time.sleep(2)
        else:
            raise
```

## 完整示例

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types.exceptions import (
    AgentNotInitializedError,
    DeviceNotFoundError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    AgentInvalidApiKeyError,
    MobileUseError,
)

async def main():
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)
    
    try:
        # 带错误处理的初始化
        if not agent.init():
            print("初始化 Agent 失败")
            return
        
        # 运行任务
        result = await agent.run_task(
            goal="Check notifications",
            name="notification_check"
        )
        
        print(f"结果: {result}")
        
    except ExecutableNotFoundError as e:
        print(f"错误: 缺少所需可执行文件: {e}")
        print("安装所需工具（Android 需要 adb，iOS 需要 idb）")
        
    except DeviceNotFoundError:
        print("错误: 未找到设备。请连接设备。")
        
    except ServerStartupError:
        print("错误: 启动服务器失败。请先清理。")
        print("运行: agent.clean(force=True)")
        
    except AgentNotInitializedError:
        print("错误: Agent 未正确初始化。")
        
    except PlatformServiceUninitializedError:
        print("错误: 平台服务未初始化。")
        print("请在 .env 文件中设置 MINITAP_API_KEY")
        
    except AgentInvalidApiKeyError:
        print("错误: Minitap API 密钥无效。")
        print("从 https://platform.mobile-use.ai/api-keys 获取有效密钥")
        
    except MobileUseError as e:
        print(f"SDK 错误: {e}")
        
    except Exception as e:
        print(f"意外错误: {type(e).__name__}: {e}")
        raise
        
    finally:
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## 下一步

- **故障排除**：常见问题和解决方案
- **Agent SDK**：Agent 类参考
