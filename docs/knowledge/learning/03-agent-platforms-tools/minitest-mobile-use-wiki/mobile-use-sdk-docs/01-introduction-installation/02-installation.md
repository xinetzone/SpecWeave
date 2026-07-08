---
title: "安装指南"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/installation"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/01-introduction-installation/02-installation.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "installation", "setup"]
summary: "Mobile Use SDK安装指南，包含系统要求、SDK安装和设备连接配置。"
---
# 安装指南

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/installation

本指南涵盖使用Mobile Use SDK的通用设置步骤，无论您选择**平台模式**还是**本地模式**。

## 前置条件

在安装Mobile Use SDK之前，请确保您具备以下条件：

### Python环境

Python 3.12或更高版本

```shellscript
python --version
# 应显示3.12.x或更高版本
```

### 本地Android自动化

- Android SDK Platform Tools（包含ADB）
- Android设备或模拟器
- 已启用USB调试

### 本地iOS自动化

- macOS系统（必需）
- Xcode命令行工具
- [idb (iOS Development Bridge)](https://fbidb.io/docs/installation/#idb-companion) - Facebook的iOS自动化工具
- iOS模拟器或物理设备

> 物理iOS设备的详细设置请参阅[iOS真机设置](../02-quickstarts/05-physical-ios-setup.md)。

## 环境设置

### 1. 安装SDK

```shellscript
pip install minitap-mobile-use
```

我们强烈推荐使用[UV](https://docs.astral.sh/uv/)来管理您的项目和包依赖。

### 2. 设置设备访问

#### Android设备配置

##### 启用开发者选项

1. 进入 **设置 → 关于手机**
2. 连续点击**版本号**7次以启用开发者选项
3. 在**开发者选项**中，启用**USB调试**

##### 验证ADB连接

```shellscript
adb devices
```

您应该能看到列出的设备。

无线调试方式：

```shellscript
adb tcpip 5555
adb connect <device_ip>:5555
```

#### iOS设备连接

1. 使用USB线将iOS设备连接到Mac
2. 当提示时，在iOS设备上信任此电脑
3. 安装所需依赖：

```shellscript
brew install libimobiledevice
```

##### 验证连接

```shellscript
idevice_id -l
```

## 配置

完成上述步骤后，您需要根据所选择的使用方式配置环境：

- **本地开发**：请参阅[本地快速开始](../02-quickstarts/01-local-quickstart.md)配置LLM设置
- **平台模式**：请参阅[平台快速开始](../02-quickstarts/02-platform-quickstart.md)配置平台凭证
- **云设备**：请参阅[云设备快速开始](../02-quickstarts/03-cloud-quickstart.md)
- **BrowserStack**：请参阅[BrowserStack快速开始](../02-quickstarts/04-browserstack-quickstart.md)

---

> **下一步**：选择适合您的[快速开始指南](../02-quickstarts/00-overview.md)开始使用。
