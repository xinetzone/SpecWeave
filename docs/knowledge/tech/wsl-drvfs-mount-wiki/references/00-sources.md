---
type: Reference
title: WSL DrvFs 挂载教程信源登记
description: 本教程束的全部信源登记，含微软官方归档博文（主信源）、博文评论区社区反馈与现代 WSL 官方文件系统文档（V 阶段补充信源）
tags: [wsl, drvfs, mount, sources, reference]
generated:
  by: agent-trae
  at: "2026-10-13T20:05:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-13T20:40:00+08:00"
status: draft
stale_after: "2027-10-13"
sources:
  - id: S-000
    resource: /references/00-sources.md
    title: 本文件（信源自登记）
---

# WSL DrvFs 挂载教程信源登记

本文件登记 OKF 教程束 `wsl-drvfs-mount-wiki` 引用的全部信源。所有概念文档的 `sources` 字段均指向本文件中的信源条目，保证事实可溯源。

## 信源清单

| 信源 ID | 标题 | 类型 | 获取方式 | 稳定性 |
|---|---|---|---|---|
| S-001 | File System Improvements to the Windows Subsystem for Linux | 微软官方归档博文（主信源） | https://learn.microsoft.com/zh-cn/archive/blogs/wsl/file-system-improvements-to-the-windows-subsystem-for-linux | stable（归档页） |
| S-002 | WSL 系列背景文章（架构概览 / pico 进程 / 系统调用 / 文件系统支持） | 微软官方博客（2016 系列，博文内引用） | 经 S-001 正文链接引用，本束未逐篇抓取 | referenced-only |
| S-003 | S-001 博文评论区（2017-04 至 2017-10） | 社区一手反馈 | S-001 页面 Comments 区段，抓取时间 2026-10-13 | stable（归档页） |
| S-004 | WSL Release Notes（build 16176 条目） | 微软官方发行说明 | 经 S-001 正文链接引用（msdn release notes），本束未逐篇抓取 | referenced-only |
| S-005a | 跨 Windows 和 Linux 文件系统工作 | 微软官方现行文档 | https://learn.microsoft.com/zh-cn/windows/wsl/filesystems（页面标注更新于 2025-06-11） | living-doc（持续更新） |
| S-005b | WSL 中的高级设置配置（wsl.conf / .wslconfig） | 微软官方现行文档 | https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config | living-doc（持续更新） |
| S-005c | 在 WSL 2 中挂载 Linux 磁盘（wsl --mount） | 微软官方现行文档 | https://learn.microsoft.com/zh-cn/windows/wsl/wsl2-mount-disk | living-doc（持续更新） |

## 信源说明

### S-001 主信源：微软官方归档博文

- 标题：**File System Improvements to the Windows Subsystem for Linux**
- 署名：Posted on behalf of **Sven Groot**
- 对应版本：Windows Insider **build 16176**（2017 年 4 月）
- 内容结构：Summary / Mounting DrvFs / Mounting network locations / Volumes mounted on empty NTFS folders / DrvFs behavior for different file systems / Comments
- 本束概念文档 `00`～`04` 的全部命令、行为描述均以该信源为准；事实台账见 [R 阶段事实清单](01-fact-ledger.md)（F-001～F-033）。

### S-002 WSL 系列背景文章

S-001 开头声明其属于 WSL 系列文章，并链接四篇 2016 年背景材料：架构概览、pico 进程介绍、WSL 系统调用、WSL 文件系统支持。本束仅登记其存在与定位（理解 DrvFs 在 WSL 架构中的位置），不逐篇引用其中事实。

### S-003 博文评论区社区反馈

S-001 评论区保留了 2017-04 至 2017-10 的读者问答，是「功能落地时真实踩坑」的一手记录，包括：非 Insider build 报 `unknown filesystem type 'drvfs'`、`/etc/fstab` 不会在新会话自动挂载、跨文件系统小文件 I/O 性能反馈、exFAT 盘误用路径语法的案例、凭据缺失时挂载无报错但目录不存在等。

评论区为**非权威信源**：其中命令用法与系统版本信息已与正文交叉核对后才纳入教程（对应事实 F-026～F-033 在事实台账中明确标注「评论区」），性能评价为主观基准，只作现象记录，不作为因果结论。

### S-004 WSL Release Notes（build 16176）

S-001 正文以链接形式指向 release notes 的 build 16176 条目。本束仅引用「该功能随 build 16176 发布」这一由正文明确陈述的事实，不引用 release notes 其他条目。

### S-005 现代 WSL 官方文档组（V 阶段补充，抓取于 2026-10-13）

S-001 是 2017 年的能力引入点，距今跨越多个 WSL 代际。对抗审查（V 阶段）提出「纯历史内容对 2026 年读者存在时代错位风险」后，补充抓取微软现行官方文档作为现代演进事实的信源，用于 `concepts/05` 中「现代 WSL 演进」一节。三篇分工：

- **S-005a**《跨 Windows 和 Linux 文件系统工作》：跨文件系统性能布局建议（文件放正在使用的系统一侧）、`\\wsl$` 与 `explorer.exe .`、互操作与 WSLENV（17063+）；页面标注更新于 2025-06-11。
- **S-005b**《WSL 中的高级设置配置》：`/etc/wsl.conf` 的 `[automount]` 段（`enabled`/`root`/`options`/`mountFsTab`）与 DrvFs 自动挂载选项（`uid`/`gid`/`umask`/`fmask`/`dmask`/`metadata`/`case`）；`wsl.conf` 按发行版生效，`.wslconfig` 全局生效。
- **S-005c**《在 WSL 2 中挂载 Linux 磁盘》：管理员 PowerShell 下 `wsl --mount <Disk>` 直挂物理磁盘/VHD（`--partition`/`--type`（默认 ext4）/`--options`/`--name`/`--bare`/`--vhd`/`--unmount`）及其限制（不支持 USB/闪存/SD 读卡器、不能挂在用盘与 Windows 安装盘、仅内核原生文件系统、其余经 `--bare`+FUSE）。

以上均为持续更新的活文档，引用内容以 2026-10-13 抓取为准，到期复评优先复核该组信源。

## 信源稳定性说明

本束无临时克隆目录或 `file:///` 绝对路径引用。S-001/S-003 为 Microsoft Learn 归档页（archive 路径），稳定性高；S-005a/b/c 为活文档，已在引用处标注抓取日期，到期复评优先复核该组信源。

## 相关文档

- [R 阶段事实清单](01-fact-ledger.md)
- [对抗审查记录](02-adversarial-review.md)
- [教程总览](../index.md)
