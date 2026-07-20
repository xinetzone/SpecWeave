---
id: "wsl-wiki-index"
title: "WSL 完整 Wiki 教程"
source: "spec:create-wsl-wiki-tutorial"
date: "2026-07-20"
category: "learning"
tags: ["wsl", "windows-subsystem-for-linux", "wsl2", "linux", "tutorial", "wiki"]
---

# WSL 完整 Wiki 教程

本教程是 WSL（Windows Subsystem for Linux）的系统性学习 wiki，从基础概念到高级架构、从 CLI 命令到 Container API 集成，全方位覆盖 WSL 技术栈，帮助开发者在 Windows 平台高效使用和集成 Linux 环境。

## 适用读者

- **开发者**：需要在 Windows 上使用 Linux 开发环境的软件工程师
- **系统工程师**：负责 Windows/Linux 混合环境部署与运维的技术人员
- **API 集成开发者**：需要集成 WSL Container API（WSLC）进行容器管理与进程编排的开发者
- **技术爱好者**：对 Windows 与 Linux 互操作技术感兴趣的学习者

<!-- README_INDEX_START -->
## 📄 章节列表

| 编号 | 文件 | 章节标题 | 核心内容 |
|------|------|---------|---------|
| 00 | [00-overview.md](00-overview.md) | WSL 概述与核心概念 | WSL是什么、WSL1 vs WSL2、核心特性、适用场景、WSLC preview标注 |
| 01 | [01-installation.md](01-installation.md) | 安装与发行版管理 | 系统要求、安装步骤、发行版管理、升级WSL2 |
| 02 | [02-quickstart.md](02-quickstart.md) | 快速开始 | 5分钟上手、基本命令、第一个Linux程序、互操作体验 |
| 03 | [03-cli-reference.md](03-cli-reference.md) | CLI 完整命令参考 | wsl.exe命令树、wslc.exe容器CLI、主名/别名说明、CLI架构四层模型 |
| 04 | [04-architecture.md](04-architecture.md) | 核心架构与进程模型 | Windows/Linux组件、六大核心进程、COM+hvsocket通信、5条hvsocket通道拓扑、2张Mermaid架构图 |
| 05 | [05-filesystem-interop.md](05-filesystem-interop.md) | 文件系统互操作 | DrvFs/Plan9、\\wsl$访问、双mount命名空间、权限映射、binfmt机制、3张Mermaid流程图 |
| 06 | [06-wslc-api.md](06-wslc-api.md) | WSL Container API 三语言编程接口 | Session/Container/Process模型、C/C++/C#三语言投影、端到端代码示例、错误处理、3张Mermaid图 |
| 07 | [07-network-config-systemd.md](07-network-config-systemd.md) | 网络、配置管理与systemd | NAT/Mirrored网络模式、DNS隧道、端口转发、wsl.conf/.wslconfig配置、systemd fork流程、3张Mermaid图 |
| 08 | [08-debugging-dev-env.md](08-debugging-dev-env.md) | 调试诊断与开发环境搭建 | 日志收集、ETL追踪、debug-shell、VS Code Remote、GPU/CUDA、Docker、Git配置 |
| 09 | [09-best-practices-faq.md](09-best-practices-faq.md) | 最佳实践与FAQ | 文件系统/内存/网络/安全最佳实践、安装/启动/网络/文件/性能/互操作/GPU/systemd常见问题 |
| 10 | [10-glossary-references.md](10-glossary-references.md) | 术语表与参考资料 | 50+核心术语中英文对照、官方文档/源码/博客/工具参考、交叉引用导航 |

<!-- README_INDEX_END -->

## 📖 阅读路径建议

- **新手入门**：建议按顺序阅读 `00→01→02→03→04`，建立完整基础认知
- **有基础读者**：可根据实际需求跳读对应章节，CLI参考、架构、最佳实践可作为案头手册查阅
- **API 开发者**：重点阅读 `04→06→10` 章节，理解架构与API集成细节

## 🔗 关联文档（扩展阅读）

- [WSL 学习路径规划](../wsl-learning-plan.md)
- [WSL CLI 与架构 Wiki](../wsl-cli-and-architecture-wiki.md)

---

- [🏠 返回上级：系统基础设施](../README.md)
