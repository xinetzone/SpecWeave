---
type: Concept
id: C-00
title: WSL DrvFs 手动挂载能力概览与时代定位
description: DrvFs 是 WSL 访问 Windows 存储命名空间的桥接文件系统；2017 年 build 16176 引入手动挂载，覆盖可移动盘、FAT、光驱、UNC 网络位置与无盘符 NTFS 卷
tags: [wsl, drvfs, mount, overview, filesystem]
generated:
  by: agent-trae
  at: "2026-10-13T20:12:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-13T20:40:00+08:00"
status: draft
stale_after: "2027-10-13"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: File System Improvements to the Windows Subsystem for Linux（微软官方归档博文）
  - id: S-005a
    resource: /references/00-sources.md
    title: 跨 Windows 和 Linux 文件系统工作（现代官方文档）
  - id: S-005b
    resource: /references/00-sources.md
    title: WSL 高级设置配置 wsl.conf（现代官方文档）
  - id: S-005c
    resource: /references/00-sources.md
    title: 在 WSL 2 中挂载 Linux 磁盘（现代官方文档）
---

# WSL DrvFs 手动挂载能力概览

## 一句话定位

**DrvFs 是 WSL 把 Windows 存储命名空间（盘符、UNC 路径、NTFS 挂载点）桥接进 Linux 目录树的文件系统类型**；`mount -t drvfs` 是 2017 年 Windows Insider build 16176 引入的手动挂载入口，使 WSL 从「只看得见固定 NTFS 盘」扩展到「看得见 Windows 能看见的全部存储」。

## 时代定位（先读）

本教程主干内容来自一篇 **2017 年 4 月的官方归档博文**，记录的是该能力的**引入时点**：

- 当时 WSL 仅随 Windows Insider build 16176 提供此功能，正式版用户（build 15063）执行会得到 `mount: unknown filesystem type 'drvfs'`，build 16299 起进入正式渠道（F-027）。
- 这些命令在**现代 WSL（含 WSL 2）中仍然有效**，但周边能力已大幅演进：`/etc/wsl.conf` 自动挂载配置、drvfs 元数据/权限选项、`wsl --mount` 挂载物理磁盘等。现代演进统一收口在 [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)，请勿把 2017 年的限制当作现代 WSL 的限制。

## 能力边界：build 16176 改变了什么

| 存储对象 | build 16176 之前 | build 16176 起 |
|---|---|---|
| 固定 NTFS 驱动器（有盘符） | 启动 Bash 时自动挂载到 `/mnt/<盘符>`（F-004） | 同左，另可手动重挂 |
| 可移动 USB 盘、CD/DVD 光驱 | 不支持（F-005） | `mount -t drvfs <盘符>: /mnt/x` 手动挂载（F-006/F-008） |
| FAT / exFAT 等非 NTFS 文件系统 | 不支持 | 经 drvfs 访问，语义有降级（F-007，见 [04](04-filesystem-semantics.md)） |
| UNC 网络共享（`\\server\share`） | 不支持 | 直接挂载，凭据在 Windows 侧管理（F-008，见 [02](02-network-mount.md)） |
| 挂载到空 NTFS 文件夹的无盘符卷 | 不支持（自动挂载只认盘符） | 以 NTFS 挂载点路径为源挂载（F-019/F-020，见 [03](03-ntfs-folder-volumes.md)） |

## 三个核心心智模型（I 阶段洞察）

1. **drvfs 的「设备」是 Windows 路径名，不是 Linux 块设备。** 同一个 `mount -t drvfs` 的源可以是 `D:`、`\\server\share` 或 `C:\mountpoint`——它不是某一种磁盘格式，而是「借 Windows 存储栈访问」的适配层。在 WSL 中找不到某存储时，先问「它在 Windows 侧叫什么名字」，而非寻找内核文件系统驱动（详见 [01](01-drvfs-manual-mount.md)）。
2. **权限位与大小写在 drvfs 上是「显示语义」，须以实际打开结果为准。** 网络挂载上所有文件恒报 `0777`，FAT 与网络文件系统不区分大小写、不支持符号链接。依赖权限位做判断的 Linux 工具链会基于失真元数据运行（详见 [04](04-filesystem-semantics.md)）。
3. **网络共享的认证边界在 Windows 侧，不在挂载命令里。** drvfs 没有 `username=`/`password=` 选项；挂载「成功」但目录不可见，通常是 Windows 侧尚未建立认证会话（详见 [02](02-network-mount.md)）。

## 适用与不适用

**适用：**

- 在 WSL 中读取 U 盘、移动硬盘、光盘、第二块硬盘（含挂载到 NTFS 空文件夹的卷）
- 访问公司 SMB 共享 / NAS 的 `\\server\share`，且认证可由 Windows 侧统一管理
- 需要把 Windows 侧已有的存储位置接入 Linux 工具链临时处理

**不适用 / 需另寻方案：**

- 需要真实 Linux 权限语义、符号链接、硬链接、大小写敏感的工作负载 → 放入 WSL 原生 ext4 根文件系统
- NFS、FUSE/sshfs 等非 Windows 存储栈协议（博文时代不支持，见 [05](05-version-and-modern-wsl.md) 的演进说明）
- 追求小文件密集 I/O 性能的编译/解压工作负载跨文件系统运行（见 [04](04-filesystem-semantics.md) 性能注意与 [05](05-version-and-modern-wsl.md) 现代官方建议）

## 环境前提

- Windows 10 build 16176+（2017 年条件）；现代 Windows 10/11 的 WSL 1 与 WSL 2 均支持 drvfs 手动挂载。
- WSL 内具备 sudo 权限；挂载点目录需自行 `mkdir` 创建。
- 命令在 WSL 内的 Bash 执行；涉及网络凭据时可经 interop 调用 `net.exe`。

## 相关概念

- [01 DrvFs 手动挂载驱动器](01-drvfs-manual-mount.md)
- [02 挂载 UNC 网络位置与凭据边界](02-network-mount.md)
- [03 挂载无盘符 NTFS 卷](03-ntfs-folder-volumes.md)
- [04 不同底层文件系统的语义差异](04-filesystem-semantics.md)
- [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)
