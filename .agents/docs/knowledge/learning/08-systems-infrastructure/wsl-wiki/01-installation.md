---
id: wsl-wiki-01-installation
title: "安装与发行版管理"
source: "spec:create-wsl-wiki-tutorial"
date: "2026-07-20"
category: "learning"
tags: ["wsl", "installation", "setup", "distribution", "upgrade", "wsl2"]
---

# 安装与发行版管理

本章介绍 WSL 的系统要求、安装步骤、发行版管理命令以及常见安装问题排查。

## 1. 系统要求

安装 WSL2 前，请确保你的 Windows 系统满足以下要求：

| 要求项 | 最低版本 |
|-------|---------|
| **操作系统** | Windows 10 版本 2004+（内部版本 19041 及更高版本）或 Windows 11 |
| **虚拟化** | 必须在 BIOS/UEFI 中启用硬件虚拟化（Intel VT-x 或 AMD-V） |
| **权限** | 管理员权限（用于启用 Windows 功能） |

> **注意**：Windows 10 版本 1903/1909 等旧版本仅支持 WSL1，无法使用 WSL2 的完整功能。建议升级到 Windows 10 2004+ 或 Windows 11。

### 检查系统版本

在 PowerShell 中运行以下命令检查 Windows 版本：

```powershell
winver
```

或在命令行中查看：

```powershell
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

### 检查虚拟化是否启用

在任务管理器的"性能" → "CPU"页面，查看右下角"虚拟化"是否显示为"已启用"。若未启用，需重启电脑进入 BIOS/UEFI 设置，开启 Intel VT-x（Intel 平台）或 SVM Mode（AMD 平台）选项。

## 2. 一键安装（推荐）

对于满足系统要求的 Windows 10 2004+ 或 Windows 11，使用一键安装命令是最简单的方式：

1. **以管理员身份打开 PowerShell**：
   - 在开始菜单搜索"PowerShell"
   - 右键选择"以管理员身份运行"

2. **运行一键安装命令**：

```powershell
wsl --install
```

该命令将自动完成以下操作：
- 启用"适用于 Linux 的 Windows 子系统"功能
- 启用"虚拟机平台"功能
- 下载并安装最新的 WSL2 Linux 内核
- 设置 WSL2 为默认版本
- 下载并安装 Ubuntu（默认发行版）

3. **重启电脑**：安装完成后，根据提示重启计算机。

4. **首次启动设置**：重启后，Ubuntu 会自动启动，提示你创建 Linux 用户名和密码（此用户名密码与 Windows 账户独立）。

> **提示**：`wsl --install` 命令需要 Windows 10 2004+ 或 Windows 11。如果你的系统版本较旧，请使用下一节的手动安装步骤。

## 3. 手动安装步骤

如果一键安装失败或需要自定义安装选项，可以按照以下步骤手动安装：

### 步骤 1：启用 WSL 功能

以管理员身份打开 PowerShell，运行：

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

### 步骤 2：启用虚拟机平台功能

```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

### 步骤 3：重启电脑

必须重启电脑才能使功能启用生效：

```powershell
Restart-Computer
```

### 步骤 4：下载并安装 WSL2 内核更新包

根据你的系统架构下载对应的内核更新包：
- **x64（Intel/AMD 64位）**：从微软官网下载 WSL2 Linux 内核更新包
- **ARM64（骁龙/ARM处理器）**：下载 ARM64 版本的内核更新包

安装下载的 `.msi` 安装包，按照向导完成安装。

### 步骤 5：设置 WSL2 为默认版本

重启后，在 PowerShell 中运行：

```powershell
wsl --set-default-version 2
```

### 步骤 6：安装 Linux 发行版

从 Microsoft Store 搜索并安装你喜欢的 Linux 发行版：
- **Ubuntu**（推荐，最新 LTS 版本）
- **Debian**
- **Fedora Remix for WSL**
- **Arch Linux**（第三方发行版）
- **openSUSE Leap**
- **Kali Linux**

安装完成后，从开始菜单启动发行版，等待安装完成并设置用户名密码。

## 4. 发行版管理

WSL 支持同时安装多个 Linux 发行版，并提供了完整的发行版管理命令。

### 4.1 列出可用发行版

查看在线可安装的发行版列表：

```powershell
wsl --list --online
```

或使用短别名：

```powershell
wsl -l -o
```

输出示例：

```
以下是可安装的有效分发的列表。
使用 'wsl.exe --install <Distro>' 安装。

NAME                                   FRIENDLY NAME
Ubuntu                                 Ubuntu
Debian                                 Debian GNU/Linux
kali-linux                             Kali Linux Rolling
Ubuntu-18.04                           Ubuntu 18.04 LTS
Ubuntu-20.04                           Ubuntu 20.04 LTS
Ubuntu-22.04                           Ubuntu 22.04 LTS
Ubuntu-24.04                           Ubuntu 24.04 LTS
OracleLinux_7_9                        Oracle Linux 7.9
...
```

### 4.2 安装指定发行版

安装特定的发行版（使用 `NAME` 列中的名称）：

```powershell
wsl --install -d Ubuntu-24.04
```

### 4.3 列出已安装发行版

查看已安装的发行版及其状态：

```powershell
wsl --list --verbose
```

或短别名：

```powershell
wsl -l -v
```

输出示例：

```
  NAME            STATE           VERSION
* Ubuntu          Running         2
  Debian          Stopped         2
  Ubuntu-24.04    Stopped         2
```

- **`*` 星号**：标记默认发行版
- **STATE**：运行状态（Running/Stopped）
- **VERSION**：WSL 版本（应为 2）

### 4.4 设置默认发行版

设置默认启动的发行版：

```powershell
wsl --set-default Ubuntu-24.04
```

或短别名：

```powershell
wsl -s Ubuntu-24.04
```

### 4.5 设置发行版使用 WSL2

如果某个发行版使用 WSL1，可以转换为 WSL2：

```powershell
wsl --set-version <DistroName> 2
```

例如：

```powershell
wsl --set-version Ubuntu 2
```

转换过程需要数分钟，取决于发行版大小。

### 4.6 注销/删除发行版

要彻底删除一个发行版（包括其中的所有文件、数据和软件），使用 `--unregister` 命令：

```powershell
wsl --unregister Debian
```

> **警告**：此操作会删除该发行版内的所有数据，且不可恢复！请确保已备份重要文件。

## 5. WSL 版本管理

### 5.1 更新 WSL

更新 WSL 到最新版本：

```powershell
wsl --update
```

更新后可能需要重启 WSL：

```powershell
wsl --shutdown
```

### 5.2 检查 WSL 版本

查看当前安装的 WSL 版本信息：

```powershell
wsl --version
```

输出示例：

```
WSL 版本： 2.2.4.0
内核版本： 5.15.146.1-2
WSLg 版本： 1.0.60
MSRDC 版本： 1.2.5105
Direct3D 版本： 1.611.1-81528511
DXCore 版本： 10.0.25131.1002-220531-1700.rs-onecore-base2-hyp
Windows 版本： 10.0.22631.3880
```

### 5.3 回滚更新

如果更新后出现问题，可以回滚到上一版本：

```powershell
wsl --update --rollback
```

### 5.4 查看 WSL 状态

查看 WSL 整体状态：

```powershell
wsl --status
```

输出示例：

```
默认版本：2
适用于 Linux 的 Windows 子系统最后更新于 2026/7/1
适用于 Linux 的 Windows 子系统内核可以使用 'wsl --update' 手动更新，但建议通过 Windows Update 自动更新。
...
```

## 6. 常见安装问题

### 6.1 虚拟化未启用

**现象**：安装 WSL2 时提示"请启用虚拟机平台 Windows 功能"或无法启动 WSL2 发行版。

**解决方案**：
1. 重启电脑，进入 BIOS/UEFI 设置（通常按 Del、F2、F10 等键）
2. 找到 CPU 配置相关选项
3. 启用 "Intel Virtualization Technology"（Intel VT-x）或 "SVM Mode"（AMD-V）
4. 保存设置并重启

### 6.2 0x80070003 错误

**现象**：安装发行版时出现错误 0x80070003。

**解决方案**：
1. 确保 Windows Subsystem for Linux 和 VirtualMachinePlatform 功能已启用
2. 重启电脑后再次尝试
3. 检查 Windows 更新，安装所有最新补丁
4. 以管理员身份运行 PowerShell，执行 `wsl --update`

### 6.3 安装后无法启动

**现象**：从开始菜单点击发行版后窗口立即关闭或报错。

**解决方案**：
1. 检查是否已安装 WSL2 内核更新包
2. 运行 `wsl --set-default-version 2`
3. 查看发行版状态：`wsl -l -v`，确认 VERSION 列显示为 2
4. 如果显示为 1，手动转换：`wsl --set-version <DistroName> 2`

### 6.4 WSL2 要求内核更新

**现象**：提示"WSL 2 需要更新其内核组件"。

**解决方案**：
1. 下载并安装最新的 WSL2 Linux 内核更新包（从微软官网）
2. 安装完成后重启 WSL：`wsl --shutdown`
3. 再次尝试启动发行版

### 6.5 参考已安装的发行版不显示

**现象**：`wsl -l -v` 不显示刚刚安装的发行版。

**解决方案**：
1. 等待几分钟，首次安装可能需要时间完成初始化
2. 从开始菜单手动点击一次发行版完成首次设置
3. 若仍不显示，尝试重启 WSL：`wsl --shutdown`

---

- ← [上一章：WSL 概述与核心概念](00-overview.md) | [返回目录](README.md) | [下一章：快速开始](02-quickstart.md) →
