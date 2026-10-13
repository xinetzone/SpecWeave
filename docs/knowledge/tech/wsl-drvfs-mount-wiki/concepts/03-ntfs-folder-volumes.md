---
type: Concept
id: C-03
title: 挂载无盘符卷：空 NTFS 文件夹挂载点
description: Windows 中可把卷挂载到空 NTFS 文件夹而非分配盘符；WSL 仅自动挂载有盘符卷，此类卷需以挂载点路径为源用 drvfs 手动挂载，且源必须是卷挂载点而非任意目录
tags: [wsl, drvfs, ntfs, mount-point, volume, bind-mount]
generated:
  by: agent-trae
  at: "2026-10-13T20:18:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-13T20:40:00+08:00"
status: draft
stale_after: "2027-10-13"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: File System Improvements to the Windows Subsystem for Linux（微软官方归档博文）
---

# 挂载无盘符卷：空 NTFS 文件夹挂载点

本节对应博文 *Volumes mounted on empty NTFS folders* 一节，处理一类容易被忽略的存储：**没有盘符、挂载在空 NTFS 文件夹上的卷**。

## 背景：什么是「挂载到空 NTFS 文件夹的卷」

Windows 支持不给卷分配盘符（如 `D:`），而是把它挂载到一个空的 NTFS 文件夹（如 `C:\mountpoint`）。访问该文件夹即访问该卷。WSL 的**自动挂载只认带盘符的卷**，因此该能力上线前，这类卷在 WSL 中完全无法访问（F-019）。

典型场景：第二块硬盘不分配盘符、挂载到 C 盘上的一个空文件夹（评论区有读者正是因此特性而受益）。

## 挂载命令

以卷的 NTFS 挂载点路径作为 drvfs 的源：

```bash
sudo mkdir /mnt/myvolume
sudo mount -t drvfs 'C:\mountpoint' /mnt/myvolume
```

注意源参数是 **Windows 路径**（反斜杠、盘符前缀），同样需要单引号包裹防止 shell 转义（F-020）。

## 关键约束：源必须是卷挂载点，不能是任意目录

博文明示一条硬约束（F-021）：

> 指定的路径必须是一个挂载点（mount point）；不能把任意目录当作一个 drvfs 实例的根。

也就是说，`C:\mountpoint` 必须是在 Windows 磁盘管理中真正「挂载卷到空文件夹」形成的卷挂载点，而不能只是 `C:\Users\someone\downloads` 这样的普通目录——后者不是一个独立卷，drvfs 不会以它为根建立挂载实例。

### 想映射任意目录怎么办：用 bind mount

如果目标是「把 Windows 侧某个普通目录挂到 WSL 里的另一个位置」，不需要 drvfs，使用 Linux 原生 **bind mounts** 即可（F-021）：

```bash
# 前提：上层卷已经以 drvfs 挂载（如自动挂载的 /mnt/c）
sudo mount --bind /mnt/c/Users/someone/downloads /mnt/mydir
```

两种机制的分工：

| 需求 | 机制 | 源的身份 |
|---|---|---|
| 把一个无盘符的 Windows 卷接入 WSL | `mount -t drvfs 'C:\mountpoint'` | NTFS 卷挂载点（一个卷） |
| 在 WSL 目录树内换个位置访问已挂载内容 | `mount --bind` | 任意已可见目录 |

## 相关概念

- [00 概览：drvfs 的设备是 Windows 路径名](00-overview.md)
- [01 DrvFs 手动挂载驱动器](01-drvfs-manual-mount.md)
