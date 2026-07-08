---
title: "iOS真机设置"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/physical-ios-quickstart"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/05-physical-ios-setup.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "ios", "physical-device", "webdriveragent"]
summary: "USB连接物理iOS设备的一次性设置指南，使用WebDriverAgent (WDA)进行自动化。"
---
# iOS真机设置

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/physical-ios-quickstart

本指南介绍使用WebDriverAgent (WDA)自动化USB连接的物理iOS设备所需的一次性设置。

**寻找其他选项？** 请查看[本地快速开始](01-local-quickstart.md)了解Android/iOS模拟器，或[云设备快速开始](03-cloud-quickstart.md)了解零设置云设备。

在继续之前，请确保您已完成[安装指南](../01-introduction-installation/02-installation.md)中的步骤。

## 您需要准备什么

### 带Xcode的macOS

代码签名和构建WDA所必需

### 物理iOS设备

通过USB线连接的iPhone或iPad

### Node.js & npm

用于安装Appium和驱动程序

### Apple开发者账户

免费账户即可 - 需要代码签名

---

## 一次性设置

WebDriverAgent (WDA)是Facebook开发的开源项目，允许在iOS设备上进行UI自动化。设置物理iOS设备需要以下一次性步骤：

1. **安装依赖工具**：
   - 使用Homebrew安装libimobiledevice：`brew install libimobiledevice`
   - 安装ideviceinstaller和iproxy：`brew install ideviceinstaller`

2. **设置Appium和WebDriverAgent**：
   - 使用npm安装Appium：`npm install -g appium`
   - 安装XCUITest驱动：`appium driver install xcuitest`

3. **配置WebDriverAgent**：
   - 找到WebDriverAgent项目路径（通常在Appium安装目录中）
   - 使用Xcode打开WebDriverAgent.xcodeproj
   - 为WebDriverAgentRunner目标配置代码签名
   - 选择您的Apple开发者团队
   - 修改Bundle Identifier为唯一值

4. **设备准备**：
   - 在iOS设备上启用开发者模式（设置 → 隐私与安全性 → 开发者模式）
   - 信任您的开发证书（设置 → 通用 → VPN与设备管理）
   - 通过USB连接设备，确保在Xcode中可见

**提示**：mobile-use SDK在初始化时可以自动管理iproxy和WDA启动，无需手动运行Appium服务器。

---

## 使用您的物理iOS设备

完成一次性设置后，mobile-use会自动处理一切：

- ✅ 启动**iproxy**进行USB端口转发
- ✅ 通过xcodebuild构建并运行**WebDriverAgent**
- ✅ 连接到WDA并等待就绪
- ✅ 脚本退出时清理进程

### 基本示例

```python
import asyncio
from minitap.mobile_use.sdk import Agent

async def main():
    # 创建Agent - 自动检测连接的iOS设备
    agent = Agent()
    
    # 初始化 - WDA、iproxy和xcodebuild自动启动
    await agent.init()
    
    # 在您的物理设备上运行任务
    result = await agent.run_task(
        goal="Open Safari and search for 'mobile automation'",
    )
    
    print(f"Task completed: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

Agent会自动检测您连接的iOS设备。除非连接了多个设备，否则无需UDID！

### 多个设备

如果连接了多个设备，请指定要使用的设备：

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    config = (
        Builders.AgentConfig
        .for_device("YOUR_DEVICE_UDID", platform="ios")
        .build()
    )
    
    agent = Agent(config=config)
    await agent.init()
    
    # 您的自动化代码
```

如何查找您的设备UDID

```shellscript
# 方式1：使用idevice_id
idevice_id -l

# 方式2：使用Xcode
# Window → Devices and Simulators → 选择您的设备
# UDID显示在设备信息中
```

---

## 高级配置

### 外部管理WDA

对于调试或自定义设置，您可以禁用自动启动并手动管理iproxy/WDA：

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.clients.ios_client_config import IosClientConfig, WdaClientConfig

async def main():
    # 创建配置以禁用自动启动
    ios_config = IosClientConfig(
        wda=WdaClientConfig(
            auto_start_iproxy=False,  # 不自动启动iproxy
            auto_start_wda=False,      # 不自动启动WDA
            wda_url="http://localhost:8100"
        )
    )

    config = (
        Builders.AgentConfig
        .for_device("YOUR_DEVICE_UDID", platform="ios")
        .with_ios_client_config(ios_config)
        .build()
    )

    agent = Agent(config=config)
    await agent.init()
    
    # 您的自动化代码
```

禁用自动启动时，手动启动所需进程：

```shellscript
# 启动USB端口转发
iproxy 8100 8100 -u YOUR_DEVICE_UDID
```

可用的WDA配置选项

| 选项 | 类型 | 默认值 | 描述 |
| --- | --- | --- | --- |
| `auto_start_iproxy` | `bool` | `True` | 自动启动USB端口转发 |
| `auto_start_wda` | `bool` | `True` | 通过xcodebuild自动构建和运行WDA |
| `wda_url` | `str` | `"http://localhost:8100"` | WDA服务器URL |
| `wda_project_path` | `str \| None` | `None` | WebDriverAgent.xcodeproj的自定义路径 |
| `wda_startup_timeout` | `float` | `120.0` | 等待WDA启动的最大秒数 |

---

## 工作原理

WDA包装器自动管理iproxy和xcodebuild进程，在脚本退出时清理它们。

## 获取设备UDID

```shellscript
# 列出连接的设备
idevice_id -l

# 或使用Xcode
# Window → Devices and Simulators → 选择您的设备
```

---

## 故障排除

**"Untrusted Developer"错误**

在设备上转到设置 → 通用 → VPN与设备管理，信任开发者证书。

**"A valid provisioning profile was not found"**

确保在Xcode中为WebDriverAgentRunner目标选择了正确的开发团队，并且Bundle Identifier是唯一的。

**"iPhone is locked"错误**

解锁您的iOS设备并保持屏幕亮起，直到WDA安装完成。

**构建失败或xcodebuild错误**

- 确保Xcode已更新到最新版本
- 清理构建文件夹：Xcode → Product → Clean Build Folder
- 确保iOS设备已启用开发者模式
- 检查设备上是否有足够的可用空间

**连接超时或WDA无响应**

**故障排除步骤**：

1. 验证WDA正在设备上运行（您应该看到WDA屏幕）
2. 检查iproxy是否正在运行：`ps aux | grep iproxy`
3. 手动测试WDA：`curl http://localhost:8100/status`
4. 重启设备并重试
5. 在配置中增加超时：`wda_startup_timeout=180.0`

更多故障排除帮助，请查看[故障排除指南](../06-troubleshooting/01-troubleshooting.md)或加入我们的[Discord社区](https://discord.gg/6nSqmQ9pQs)。

---

## 下一步

- [探索示例](../04-examples/00-overview.md) - 查看真实世界的自动化示例
- [学习核心概念](../03-core-concepts/00-overview.md) - 了解任务、配置文件和构建器
- [Platform集成](02-platform-quickstart.md) - 使用Minitap Platform添加可观测性
- [SDK参考](../05-sdk-reference/00-overview.md) - 深入了解完整的API文档
