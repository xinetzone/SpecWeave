---
id: "wsl-wiki-10-glossary-references"
title: "术语表与参考资料"
source: "spec:create-wsl-wiki-tutorial"
date: "2026-07-20"
category: "learning"
tags: ["wsl", "glossary", "references", "terminology", "cross-reference"]
---

# 术语表与参考资料

## 第一部分：术语表（Glossary）

按字母顺序排列的 WSL 核心术语定义。

- **ABI (Application Binary Interface, 应用程序二进制接口)**：操作系统与应用程序之间的二进制级接口约定，定义了函数调用约定、数据类型布局、系统调用号等。WSLC API 严格遵循 ABI 兼容性承诺。[→第6章](06-wslc-api.md)
- **binfmt_misc**：Linux 内核子系统，允许注册任意可执行文件格式的解释器。WSL 通过 binfmt_misc 实现 Windows PE 二进制文件在 Linux 中的直接执行。[→第3章](03-cli-reference.md)
- **COM (Component Object Model, 组件对象模型)**：Windows 平台的组件对象模型与进程间通信机制，wsl.exe 通过 COM 接口 `ILxssUserSession` 调用 wslservice.exe 服务。[→第4章](04-architecture.md)
- **cgroup (Control Group, 控制组)**：Linux 内核功能，用于限制、统计和隔离进程组的资源使用（CPU、内存、磁盘IO等），是容器技术的基础。WSL2 使用 cgroup v2。[→第7章](07-network-config-systemd.md)
- **Container（WSL容器）**：WSL Container API 管理的轻量级容器实例，与传统 Docker 容器不同，WSL 容器直接复用 WSL2 轻量级虚拟机内核，启动速度更快、资源开销更低。[→第6章](06-wslc-api.md)
- **CUDA (Compute Unified Device Architecture)**：NVIDIA 推出的并行计算平台与编程模型，WSL2 原生支持 CUDA，可在 Linux 环境中直接调用 Windows 主机 GPU 进行加速计算。[→第8章](08-debugging-dev-env.md)
- **DNS Tunneling（DNS隧道）**：WSL Mirrored 网络模式下的 DNS 解析优化技术，将 Linux 中的 DNS 请求通过隧道转发到 Windows 主机解析，避免 NAT 模式下的 DNS 配置同步问题。[→第7章](07-network-config-systemd.md)
- **DrvFs (Drive File System)**：WSL 用于挂载 Windows 磁盘分区的文件系统驱动，挂载点通常为 `/mnt/c/`、`/mnt/d/` 等，支持 Windows/Linux 文件名和权限互转。[→第5章](05-filesystem-interop.md)
- **GNS (Guest Network Service, 客机网络服务)**：运行在 WSL2 Linux 虚拟机内的网络服务组件，负责处理网络数据包转发、DNS 配置、端口映射等网络相关任务，与 Windows 主机侧的网络组件协同工作。[→第4章](04-architecture.md)
- **hvsocket (Hyper-V Socket)**：Hyper-V 提供的跨虚拟机/主机高效通信机制，基于 AF_HYPERV 地址族，WSL2 使用 hvsocket 作为 Windows 与 Linux 虚拟机之间的主要 IPC 通道。[→第4章](04-architecture.md)
- **init (WSL init 进程)**：WSL2 Linux 虚拟机内的 PID 1 进程（位于 `/init`），是所有 Linux 进程的祖先，负责初始化系统环境、启动用户 shell、处理 Windows/Linux 互操作请求。[→第4章](04-architecture.md)
- **Interop（互操作）**：Windows 与 Linux 子系统之间的交互能力总称，包括文件系统互访问、进程跨系统调用、网络互通、剪贴板共享等核心特性。[→第2章](02-quickstart.md)
- **mini_init**：WSL init 进程的精简版本，在容器模式（WSLC）下运行，不包含完整系统初始化逻辑，仅提供容器进程管理和基础互操作能力。[→第4章](04-architecture.md)
- **Mirrored Networking（镜像网络模式）**：WSL2 新增的网络模式（Windows 11 22H2+），让 Linux 虚拟机与 Windows 主机共享同一网络栈，拥有相同的 IP 地址和网络接口，解决 NAT 模式下的网络连通性问题。[→第7章](07-network-config-systemd.md)
- **/mnt/c/ (DrvFs挂载点)**：DrvFs 在 WSL 中的默认挂载路径，Windows C盘通过该路径在 Linux 中访问，性能略低于原生 Linux 文件系统但兼容性最佳。[→第5章](05-filesystem-interop.md)
- **Mount Namespace（挂载命名空间）**：Linux 命名空间的一种，用于隔离进程看到的文件系统挂载点视图。WSL 为每个分发版维护独立的挂载命名空间，确保不同 Linux 环境互不干扰。[→第5章](05-filesystem-interop.md)
- **NAT (Network Address Translation, 网络地址转换)**：WSL2 默认网络模式，Linux 虚拟机运行在私有 NAT 网络后，通过 Windows 主机进行网络地址转换访问外部网络，配置简单但存在端口转发等局限性。[→第7章](07-network-config-systemd.md)
- **p9rdr.sys (Plan 9 Redirector Driver)**：Windows 内核模式驱动，实现 Plan 9 (9P) 协议客户端，负责将 WSL2 Linux 文件系统作为网络重定向器挂载到 Windows，使 Windows 可通过 UNC 路径访问 Linux 文件。[→第4章](04-architecture.md)
- **Plan 9 (9P, 九号计划文件系统协议)**：源自贝尔实验室 Plan 9 操作系统的网络文件系统协议，WSL 使用 9P 协议实现 Windows ↔ Linux 双向文件系统共享：Linux 访问 Windows 用 DrvFs，Windows 访问 Linux 用 p9rdr.sys + 9P。[→第5章](05-filesystem-interop.md)
- **Process（WSLC Process）**：WSL Container API 中的进程对象，代表在 WSL 容器内运行的单个 Linux 进程，支持启动、终止、等待、获取输出流、设置环境变量等操作。[→第6章](06-wslc-api.md)
- **RAII (Resource Acquisition Is Initialization, 资源获取即初始化)**：C++ 编程范式，利用对象构造/析构函数自动管理资源生命周期。WSLC C++ API 封装大量使用 RAII 模式确保句柄和资源正确释放。[→第6章](06-wslc-api.md)
- **relay (WSL relay 进程)**：WSL 互操作中继组件，运行在 Linux 侧，负责接收 Windows 启动 Linux 进程的请求并转发给 init 进程处理，同时将进程输出回传到 Windows。[→第4章](04-architecture.md)
- **resolv.conf**：Linux 系统 DNS 解析配置文件，位于 `/etc/resolv.conf`。WSL 默认自动生成该文件，在启用 systemd 或自定义网络配置时需要注意配置覆盖问题。[→第7章](07-network-config-systemd.md)
- **Session（WSLC Session）**：WSL Container API 的顶层对象，代表一个 WSL 用户会话环境，包含一个或多个 Container，负责管理会话生命周期、用户身份验证和全局配置。[→第6章](06-wslc-api.md)
- **systemd**：现代 Linux 发行版默认的 init 系统与服务管理器，负责系统启动、服务管理、设备管理、日志收集等。WSL 默认使用自有 init，需显式配置启用 systemd。[→第7章](07-network-config-systemd.md)
- **UNC Path (Universal Naming Convention, 通用命名约定路径)**：Windows 网络资源路径格式，以 `\\` 开头。WSL Linux 文件系统通过 UNC 路径 `\\wsl.localhost\`（旧称 `\\wsl$`）在 Windows 资源管理器中访问。[→第5章](05-filesystem-interop.md)
- **VM (Virtual Machine, 虚拟机)**：通过硬件虚拟化技术创建的隔离计算环境。WSL2 使用轻量级、优化过的 Hyper-V 虚拟机运行完整 Linux 内核，相比传统虚拟机启动更快、内存占用更低。[→第0章](00-overview.md)
- **\\wsl.localhost\\ (\\wsl$)**：Windows 访问 WSL Linux 文件系统的 UNC 路径前缀，旧版 Windows 使用 `\\wsl$\`，新版统一为 `\\wsl.localhost\`，后接分发版名称即可访问对应文件系统。[→第5章](05-filesystem-interop.md)
- **.wslconfig**：WSL 全局配置文件，位于 Windows 用户目录 `%USERPROFILE%\.wslconfig`，影响所有 WSL2 分发版的全局设置，包括内存、CPU、交换空间、网络模式、GUI 应用支持等。[→第7章](07-network-config-systemd.md)
- **wsl.conf**：WSL 单分发版配置文件，位于 Linux 内 `/etc/wsl.conf`，仅影响当前分发版的行为，包括自动挂载设置、互操作配置、用户账户、启动命令等。[→第7章](07-network-config-systemd.md)
- **WSL1 (Windows Subsystem for Linux v1)**：WSL 第一代架构，通过翻译层将 Linux 系统调用实时转换为 Windows NT 系统调用，无需虚拟机，性能接近原生但兼容性有限（不支持内核模块、Docker 等）。[→第0章](00-overview.md)
- **WSL2 (Windows Subsystem for Linux v2)**：WSL 当前默认架构，基于轻量级 Hyper-V 虚拟机运行完整真实 Linux 内核，提供 100% 系统调用兼容性，支持 Docker、CUDA、WSLg 等全部特性。[→第0章](00-overview.md)
- **WSLg (WSL GUI Subsystem)**：WSL 图形界面支持子系统，允许 Linux GUI 应用直接在 Windows 桌面运行，无需安装 X Server，支持音频、剪贴板、GPU 加速等完整桌面体验。[→第0章](00-overview.md)
- **wslc.exe (WSL Container CLI)**：WSL Container API 配套的命令行工具，用于通过 CLI 管理 WSL 容器、会话和进程，是 WSLC API 的命令行前端。[→第3章](03-cli-reference.md)
- **WSLC (WSL Container API)**：WSL 容器编程接口（preview 阶段），提供 C/C++/C# 等多语言 SDK，允许第三方应用以编程方式创建和管理 WSL 会话、容器和进程，而非通过 wsl.exe 命令行调用。[→第6章](06-wslc-api.md)
- **wslservice.exe**：运行在 Windows 本地系统账户下的 WSL 核心系统服务，负责管理 WSL 虚拟机生命周期、分发版安装/卸载、COM 接口暴露、跨系统通信调度等核心功能。[→第4章](04-architecture.md)
- **WSL**：Windows Subsystem for Linux 的缩写，微软在 Windows 上原生运行 Linux 二进制可执行文件的兼容层，支持完整 Linux 命令行环境、工具链和应用程序，无需双系统或传统虚拟机。[→第0章](00-overview.md)
- **HRESULT**：Windows COM/Win32 API 标准错误返回码类型，32位整数，包含严重级别、设施代码和错误编号。WSLC API 使用 HRESULT 作为统一错误码。[→第6章](06-wslc-api.md)
- **LxssUserSession**：WSL COM 接口名称（`ILxssUserSession`），是 wsl.exe 与 wslservice.exe 之间的主要编程接口，暴露分发版管理、会话创建、命令执行等核心方法。[→第4章](04-architecture.md)

## 第二部分：参考资料（References）

### 1. 官方文档

- **Microsoft WSL 官方文档**：<https://learn.microsoft.com/en-us/windows/wsl/> — 微软官方 WSL 文档入口，包含安装、配置、命令参考、故障排查等完整内容，推荐首选阅读
- **WSL GitHub 开源仓库**：<https://github.com/microsoft/WSL> — WSL 组件（Windows 侧用户态工具与服务）开源代码仓库，可提交 Issue、查看源码、追踪 Release
- **WSL Container API 文档**：Microsoft 官方 API 参考（preview 阶段，随 SDK 发布）— WSLC API 详细参考，包含接口定义、数据结构、示例代码
- **WSL 发布日志**：<https://github.com/microsoft/WSL/releases> — GitHub Releases 页面，每个版本的新特性、修复、已知问题详细说明

### 2. 架构与源码参考

WSL 核心代码位于 [microsoft/WSL](https://github.com/microsoft/WSL) 仓库，关键目录：
- `src/linux/`：Linux 侧用户态工具（init、interop relay、GNS 等）
  - `src/linux/init/mini_init/`：容器模式下的精简 init 进程入口
  - `src/linux/init/init.cpp`：标准模式下 WSL init 主逻辑实现
- `src/windows/`：Windows 侧组件（wslservice、wsl.exe CLI、p9rdr 等）
  - `src/windows/cli/`：wsl.exe 和 wslc.exe 命令行解析与实现（CLI 四层架构）
  - `src/windows/service/`：wslservice.exe 核心服务逻辑
- `src/shared/`：Windows/Linux 共享头文件与公共定义

### 3. 技术博客与文章

- 微软官方 WSL 博客：<https://devblogs.microsoft.com/commandline/> — Windows Command Line 团队博客，发布 WSL 新特性公告、深度技术文章
- WSL 架构深度解析系列：社区与微软官方发布的 WSL 内部机制剖析文章，覆盖进程模型、文件系统、网络、互操作等核心技术细节
- WSLg 技术详解：WSLg 架构与实现原理文章，讲解 Weston 合成器、RDP 远程、音频重定向等图形栈设计

### 4. 相关工具与生态

- **Windows Terminal**：<https://aka.ms/terminal> — 微软现代终端应用，WSL 最佳命令行宿主，支持多标签、自定义主题、GPU 文本渲染
- **VS Code Remote - WSL**：<https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl> — VS Code WSL 远程开发扩展，实现在 Windows 中无缝编辑和调试 Linux 文件
- **Docker Desktop WSL2 后端**：Docker Desktop 使用 WSL2 作为原生后端（替代旧 Hyper-V VM），提供更好的文件系统性能和互操作性
- **NVIDIA CUDA on WSL**：<https://docs.nvidia.com/cuda/wsl-user-guide/> — NVIDIA 官方 CUDA on WSL 用户指南，包含驱动安装、环境配置、ML/AI 框架使用说明

## 第三部分：交叉引用导航

按学习路径和主题快速跳转：

### 入门篇
[概述](00-overview.md) → [安装与发行版管理](01-installation.md) → [快速开始](02-quickstart.md)

### 命令与架构篇
[CLI 完整命令参考](03-cli-reference.md) → [核心架构与进程模型](04-architecture.md) → [文件系统互操作](05-filesystem-interop.md)

### API 与进阶篇
[WSL Container API](06-wslc-api.md) → [网络与systemd配置](07-network-config-systemd.md) → [调试与开发环境](08-debugging-dev-env.md)

### 实战与参考篇
[最佳实践与FAQ](09-best-practices-faq.md) → **[术语表与参考资料](10-glossary-references.md)（当前页）**

回到[完整目录](README.md)

## 第四部分：教程版本与来源说明

- **教程版本**：v1.0
- **创建日期**：2026-07-20
- **整合来源**：
  - [WSL系统学习计划](../wsl-learning-plan.md)：架构/进程/网络/文件系统/开发环境知识体系
  - [WSL CLI与架构参考手册](../wsl-cli-and-architecture-wiki.md)：CLI命令树/Container API/四层架构细节
- **状态标注**：WSL Container API (WSLC) 相关内容处于 preview 阶段，GA 计划 2026 年秋季，API 接口可能发生变更。生产环境集成前请参考最新官方 SDK 文档。

---

← [上一章：最佳实践与FAQ](09-best-practices-faq.md) | [返回目录](README.md)
