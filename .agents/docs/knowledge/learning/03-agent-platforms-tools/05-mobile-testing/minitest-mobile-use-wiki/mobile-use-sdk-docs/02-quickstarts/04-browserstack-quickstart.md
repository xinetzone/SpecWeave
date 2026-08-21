---
title: "BrowserStack快速开始"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/browserstack-quickstart"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/04-browserstack-quickstart.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "quickstart", "browserstack", "ios"]
summary: "BrowserStack快速开始指南，使用云端真实物理iOS设备运行移动自动化，无需本地硬件。"
---
# BrowserStack快速开始

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/browserstack-quickstart

本指南介绍使用**BrowserStack**在云端真实物理iOS设备上运行移动自动化，无需本地硬件。

**寻找其他选项？** 请查看[本地快速开始](01-local-quickstart.md)了解本地设备、[云设备快速开始](03-cloud-quickstart.md)了解Minitap云设备，或[iOS真机设置](05-physical-ios-setup.md)了解USB连接设备。

## 什么是BrowserStack？

BrowserStack App Automate提供对云端真实物理iOS设备的访问。主要优势：

### 真实物理设备

在实际的iPhone和iPad上测试，而非模拟器

### 无需本地硬件

无需拥有或维护iOS设备

### CI/CD就绪

非常适合自动化测试流水线

### 跨设备测试

访问多种设备型号和iOS版本

---

## 前置条件

- BrowserStack账户（注册[BrowserStack](https://www.browserstack.com/)获取免费试用）
- BrowserStack用户名和访问密钥（从[Account Settings](https://www.browserstack.com/accounts/settings)获取）
- 上传到BrowserStack的iOS应用（.ipa文件）
- 在继续之前，请确保您已完成[安装指南](../01-introduction-installation/02-installation.md)中的步骤

---

## 创建您的第一个BrowserStack自动化

### 基本示例

```python
import asyncio
import os
from pydantic import SecretStr

from minitap.mobile_use.clients.ios_client_config import BrowserStackClientConfig
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import AgentConfigBuilder

async def main():
    # 从环境变量获取凭证
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")

    if not username or not access_key:
        print("Error: Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
        return

    # 配置BrowserStack连接
    browserstack_config = BrowserStackClientConfig(
        username=username,
        access_key=SecretStr(access_key),
        device_name="iPhone 17",              # 要使用的设备
        platform_version="26",              # iOS版本
        app_url="bs://your_app_hash_here",  # 您上传的应用
        build_name="mobile-use-demo",       # 可选：用于组织会话
        session_name="My First Automation", # 可选：会话标识符
    )

    # 为BrowserStack构建Agent配置
    agent_config = AgentConfigBuilder().for_browserstack(browserstack_config).build()
    agent = Agent(config=agent_config)

    try:
        # 初始化Agent（创建BrowserStack会话）
        print("Initializing BrowserStack session...")
        await agent.init()
        print("Session created successfully!")

        # 运行您的自动化任务
        result = await agent.run_task(
            goal="Fill the login form with test data",
        )

        print(f"Task Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 清理（结束BrowserStack会话）
        await agent.clean()
        print("Session ended.")

if __name__ == "__main__":
    asyncio.run(main())
```

### 运行脚本

```shellscript
# 设置您的凭证
export BROWSERSTACK_USERNAME="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"

# 运行自动化
python browserstack_demo.py
```

---

## 配置选项

### BrowserStackClientConfig

| 参数 | 类型 | 必需 | 描述 |
| --- | --- | --- | --- |
| `username` | `str` | ✅ | 您的BrowserStack用户名 |
| `access_key` | `SecretStr` | ✅ | 您的BrowserStack访问密钥 |
| `device_name` | `str` | ✅ | 设备名称（例如，"iPhone 17"、"iPhone 16 Pro"） |
| `platform_version` | `str` | ✅ | iOS版本（例如，"17"、"18"、"26"） |
| `app_url` | `str` | ✅ | BrowserStack应用URL（bs://...） |
| `hub_url` | `str \| None` | ❌ | 自定义hub URL（默认为BrowserStack云） |
| `project_name` | `str \| None` | ❌ | 用于组织会话的项目名称 |
| `build_name` | `str \| None` | ❌ | 用于分组会话的构建名称 |
| `session_name` | `str \| None` | ❌ | 人类可读的会话名称 |

### 可用设备

BrowserStack支持广泛的iOS设备。一些热门选项：

| 设备 | 示例`device_name` | 可用iOS版本 |
| --- | --- | --- |
| iPhone 17 Pro Max | `"iPhone 17 Pro Max"` | 26 |
| iPhone 17 Pro | `"iPhone 17 Pro"` | 26 |
| iPhone 17 | `"iPhone 17"` | 26 |
| iPhone 16 Pro Max | `"iPhone 16 Pro Max"` | 18 |
| iPhone 16 Pro | `"iPhone 16 Pro"` | 18 |
| iPhone 16 | `"iPhone 16"` | 18 |
| iPhone 15 Pro Max | `"iPhone 15 Pro Max"` | 17, 26 |
| iPhone 15 Pro | `"iPhone 15 Pro"` | 17 |
| iPhone 15 | `"iPhone 15"` | 17, 26 |
| iPad Pro 13 2025 | `"iPad Pro 13 2025"` | 26 |
| iPad Pro 11 2025 | `"iPad Pro 11 2025"` | 26 |
| iPad Air 6 | `"iPad Air 6"` | 17 |

查看[BrowserStack设备列表](https://www.browserstack.com/list-of-browsers-and-platforms/app_automate?tab=ios-listing)获取完整的可用设备列表。

---

## 环境变量

为安全起见，将您的凭证存储为环境变量：

```shellscript
BROWSERSTACK_USERNAME=your_username
BROWSERSTACK_ACCESS_KEY=your_access_key
```

然后在脚本中加载它们：

```python
import os
from pydantic import SecretStr

username = os.environ.get("BROWSERSTACK_USERNAME")
access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")

browserstack_config = BrowserStackClientConfig(
    username=username,
    access_key=SecretStr(access_key),
    # ... 其他选项
)
```

切勿提交`.env`文件或在代码中硬编码凭证。请将`.env`添加到`.gitignore`中。

---

## 查看会话结果

运行自动化后，您可以在BrowserStack仪表板中查看详细的会话信息：

1. 导航到[BrowserStack App Automate Dashboard](https://app-automate.browserstack.com/)
2. 通过构建名称或会话名称找到您的会话
3. 查看：
    - 会话视频录制
        - 每步截图
        - 设备日志
        - 网络日志

会话启动时也会记录会话URL：

```text
View session: https://app-automate.browserstack.com/dashboard/sessions/{session_id}
```

---

## 支持的操作

BrowserStack客户端支持以下操作：

| 操作 | 方法 | 描述 |
| --- | --- | --- |
| **点击** | `tap(x, y)` | 在坐标处点击 |
| **滑动** | `swipe(x1, y1, x2, y2)` | 滑动手势 |
| **截图** | `screenshot()` | 捕获屏幕 |
| **输入文本** | `text("hello")` | 输入文本 |
| **启动应用** | `launch(bundle_id)` | 通过包ID启动应用 |
| **终止应用** | `terminate(bundle_id)` | 关闭应用 |
| **打开URL** | `open_url(url)` | 打开URL |
| **按下按钮** | `button(type)` | 按下硬件按钮（home、音量） |
| **UI层次结构** | `describe_all()` | 获取UI元素树 |

某些操作（如`app_current()`和`install()`）在BrowserStack上不受支持。应用必须预先上传到BrowserStack。

---

## 带结构化输出的完整示例

```python
import asyncio
import os
from pydantic import BaseModel, Field, SecretStr

from minitap.mobile_use.clients.ios_client_config import BrowserStackClientConfig
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import AgentConfigBuilder

class LoginResult(BaseModel):
    success: bool = Field(..., description="Whether login was successful")
    username_entered: str = Field(..., description="The username that was entered")
    error_message: str | None = Field(None, description="Error message if login failed")

async def main():
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")

    browserstack_config = BrowserStackClientConfig(
        username=username,
        access_key=SecretStr(access_key),
        device_name="iPhone 17",
        platform_version="26",
        app_url="bs://your_app_hash",
        build_name="structured-output-demo",
    )

    agent_config = AgentConfigBuilder().for_browserstack(browserstack_config).build()
    agent = Agent(config=agent_config)

    try:
        await agent.init()

        result = await agent.run_task(
            goal="Enter username 't**@*********' and password 'Test123!' then tap the login button",
            output=LoginResult,
        )

        if result:
            print(f"Login successful: {result.success}")
            print(f"Username entered: {result.username_entered}")
            if result.error_message:
                print(f"Error: {result.error_message}")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 故障排除

**会话无法启动**

**可能原因**：

- 凭证无效
- app_url无效
- 设备/操作系统组合不可用

**解决方案**：

1. 验证您的用户名和访问密钥
2. 重新上传您的应用并获取新的`app_url`
3. 查看[BrowserStack设备列表](https://www.browserstack.com/list-of-browsers-and-platforms/app_automate)了解有效的设备/操作系统组合

**应用无法启动**

**可能原因**：

- 应用未正确签名
- 应用与所选iOS版本不兼容

**解决方案**：

1. 确保您的.ipa已签名用于分发
2. 尝试与您应用的最低部署目标匹配的其他iOS版本

**超时错误**

**元素未找到**

---

## 最佳实践

### 使用环境变量

切勿硬编码凭证 - 使用环境变量或密钥管理

### 组织会话

使用`build_name`和`session_name`轻松组织和查找会话

### 处理清理

始终使用try/finally确保调用`agent.clean()`

### 检查设备可用性

运行测试前验证设备/操作系统组合

---

## 下一步

- [本地快速开始](01-local-quickstart.md) - 设置本地设备自动化
- [云设备](03-cloud-quickstart.md) - 使用Minitap的云设备
- [SDK参考](../05-sdk-reference/00-overview.md) - 完整Agent API文档
- [使用示例](../04-examples/00-overview.md) - 更多自动化示例
