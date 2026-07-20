---
id: wsl-wiki-00-overview
title: "WSL 概述与核心概念"
source: "spec:create-wsl-wiki-tutorial"
date: "2026-07-20"
category: "learning"
tags: ["wsl", "wsl2", "overview", "windows-subsystem-for-linux", "introduction"]
---

# WSL 概述与核心概念

## 1. WSL 是什么

WSL（Windows Subsystem for Linux，Windows 下的 Linux 子系统）是微软官方推出的兼容层，允许用户在 Windows 操作系统上原生运行 Linux 二进制可执行文件（ELF 格式）。它无需传统双系统启动或第三方虚拟机软件，即可在 Windows 中获得完整的 Linux 环境体验。

WSL 由微软与 Canonical 等 Linux 发行版厂商合作开发，深度集成于 Windows 内核，实现了 Windows 与 Linux 之间的无缝互操作。

## 2. WSL1 vs WSL2 对比

WSL 经历了两个主要版本迭代，两者在架构设计上有本质区别：

| 对比维度 | WSL1 | WSL2 |
|---------|------|------|
| **架构** | 翻译层（syscall 翻译） | 轻量级虚拟机（真实 Linux 内核） |
| **Linux 内核** | 无，通过 Windows 内核模拟 | 完整 Linux 内核（微软定制版本） |
| **跨文件系统性能** | Windows 文件系统访问快 | Linux 文件系统访问快，跨系统有性能损耗 |
| **系统调用兼容性** | 部分系统调用不支持 | 100% 系统调用兼容 |
| **systemd 支持** | 不支持 | 完整支持（需配置） |
| **网络模型** | 与 Windows 共享 IP 地址 | 独立 NAT 网络（或 Mirrored 模式） |
| **启动速度** | 极快（秒级） | 快（数秒） |
| **资源占用** | 极低 | 按需分配，内存可回收 |
| **推荐程度** | 已废弃，仅兼容旧场景 | 当前推荐版本 |

**关键结论**：所有新用户都应使用 WSL2。WSL1 仅保留用于需要极致跨文件系统性能的特殊场景。

## 3. 核心特性

### 3.1 无缝互操作（Interop）

WSL 实现了 Windows 与 Linux 之间的命令互调用：
- 在 Linux 终端中可直接运行 Windows 程序（如 `notepad.exe`、`code .`）
- 在 Windows PowerShell/cmd 中可直接调用 Linux 命令（如 `wsl ls -la`）
- 通过 binfmt_misc 机制实现自动识别执行

### 3.2 文件系统互访问

- **Windows 访问 Linux 文件**：通过 `\\wsl.localhost\<发行版名>\` 或 `\\wsl$\<发行版名>\` UNC 路径访问
- **Linux 访问 Windows 文件**：Windows 驱动器自动挂载到 `/mnt/c/`、`/mnt/d/` 等路径
- WSL2 使用 Plan9 文件服务器实现跨系统文件共享（WSL1 使用 DrvFs）

### 3.3 GPU 计算支持

WSL2 原生支持 GPU 硬件加速：
- NVIDIA CUDA、DirectML 等计算框架可在 WSL 内直接使用
- 支持机器学习/深度学习工作负载（PyTorch、TensorFlow 等）
- 显卡驱动需在 Windows 侧安装，WSL 内自动识别

### 3.4 WSLg（GUI 应用支持）

WSLg（WSL GUI）允许直接在 WSL 中运行 Linux 图形界面应用：
- 无需配置 X Server
- 支持 Wayland 和 X11 协议
- Linux GUI 应用窗口直接显示在 Windows 桌面，与原生应用体验一致
- 支持音频输出、麦克风输入、摄像头等外设

### 3.5 systemd 支持

WSL2 完整支持 systemd（系统和服务管理器）：
- 通过在 `/etc/wsl.conf` 中配置 `[boot] systemd=true` 启用
- 支持 `systemctl` 命令管理服务
- 兼容依赖 systemd 的软件（如 Docker、snap 包等）

## 4. 适用场景

WSL 适合以下开发与工作场景：

| 场景 | 说明 |
|-----|------|
| **Web 开发** | 使用 Linux 原生工具链（Node.js、Python、Ruby、Go 等）开发 Web 应用 |
| **容器/Docker** | 在 WSL2 中原生运行 Docker Desktop、Kubernetes 等容器环境（性能接近原生 Linux） |
| **数据科学** | 运行 Jupyter Notebook、PyTorch/TensorFlow 等机器学习框架，配合 GPU 加速 |
| **跨平台测试** | 在同一台机器上同时测试 Windows 和 Linux 平台的软件行为 |
| **学习 Linux** | 在 Windows 环境中学习 Linux 命令行、Shell 脚本、系统管理，无需额外硬件或虚拟机 |
| **开源贡献** | 直接在 Linux 环境下构建和测试开源项目，避免 Windows 兼容性问题 |
| **DevOps 工作流** | 运行 Ansible、Terraform、kubectl 等 DevOps 工具，获得与生产环境一致的运行时 |

## 5. 版本说明

### 5.1 WSL2：当前推荐版本

- 所有新安装的 WSL 默认使用 WSL2
- 持续获得微软官方更新与功能增强
- 支持本文档提到的所有高级特性（WSLg、systemd、GPU、容器等）

### 5.2 WSL Container API (WSLC)

- **当前状态**：Preview（预览版）
- **GA（正式发布）计划**：2026 年秋季
- Preview 期间 API 可能发生不兼容变更，仅建议用于可行性评估，请勿部署到生产环境
- WSLC 提供类 Docker 的容器管理能力，支持 C/C#/C++ 三语言 SDK 投影，详见后续章节

## 6. WSL 与传统虚拟机的区别

WSL2 虽然使用了轻量级虚拟机技术，但与传统 VMware、VirtualBox 等虚拟机有本质区别：

| 对比维度 | WSL2 | 传统虚拟机 |
|---------|------|-----------|
| **启动速度** | 数秒内启动 | 数十秒到数分钟 |
| **内存占用** | 按需分配，自动回收，空闲时占用极低 | 固定分配或预分配，启动即占用 |
| **CPU 占用** | 仅运行 Linux 进程时占用 | 整个虚拟机 OS 持续运行占用 |
| **系统集成度** | 深度集成：文件互访、命令互调、网络共享、GUI 原生显示 | 隔离运行：需通过共享文件夹、网络端口映射、剪贴板共享等方式交互 |
| **管理成本** | 零管理：自动内核更新、自动网络配置 | 需要手动管理：安装 OS、配置网络、安装更新、分配资源 |
| **许可成本** | 免费（WSL 本身免费，Linux 发行版多数免费） | 多数需要商业授权（VMware Workstation Pro 等） |
| **隔离性** | 中等（VM 级隔离但深度集成） | 强（完全隔离的硬件虚拟化） |

**总结**：WSL2 兼顾了虚拟机的完整 Linux 兼容性与接近原生应用的轻量级体验，是 Windows 平台进行 Linux 开发的最佳选择。如果需要强隔离的独立环境（如运行不可信软件、测试特定内核模块），仍建议使用传统虚拟机。

---

- ← [返回目录](README.md) | [下一章：安装与发行版管理](01-installation.md) →
