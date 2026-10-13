---
type: Concept
id: C-01
title: DrvFs 手动挂载驱动器（U盘、移动盘、光驱）
description: 使用 sudo mount -t drvfs 将 Windows 盘符挂载到 WSL 目录树，含建点、挂载、安全卸载三步与命令历史修正
tags: [wsl, drvfs, mount, removable-drive, usb]
generated:
  by: agent-trae
  at: "2026-10-13T20:14:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-13T20:40:00+08:00"
status: draft
stale_after: "2027-10-13"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: File System Improvements to the Windows Subsystem for Linux（微软官方归档博文）
  - id: S-003
    resource: /references/00-sources.md
    title: 博文评论区社区反馈
---

# DrvFs 手动挂载驱动器

本节对应博文 *Mounting DrvFs* 一节：用标准 Linux `mount` 命令，以 `drvfs` 为文件系统类型，把任意 Windows 盘符接入 WSL 目录树。

## 三步操作

以把可移动驱动器 `D:` 挂载到 `/mnt/d` 为例：

```bash
# 1. 创建挂载点目录（独立步骤，不会自动生成）
sudo mkdir /mnt/d

# 2. 以 drvfs 类型挂载 Windows 盘符
sudo mount -t drvfs D: /mnt/d
```

挂载成功后，D 盘文件出现在 `/mnt/d`。

```bash
# 3. 用完卸载（例如要在 Windows 侧安全弹出设备前）
sudo umount /mnt/d
```

## 要点说明

- **盘符写法**：源参数是 Windows 盘符加大写冒号（`D:`），不是 `/dev/...` 设备路径。这体现了「drvfs 的设备是 Windows 路径名」的心智模型（见 [00 概览](00-overview.md)）。
- **挂载点必须预先存在**：`mount` 不会替你创建目录。该文初版曾遗漏 `sudo mkdir /mnt/d`，经读者指出后作者补入正文（F-011）——照抄网上缺步版本会直接失败。
- **固定盘同样适用**：虽然固定 NTFS 盘通常已由 WSL 自动挂载，手动挂载可用于更换挂载位置或重挂。
- **卸载后可安全移除**：先 `umount` 再在 Windows 侧弹出，可避免文件句柄占用。

## 适用对象

博文列举此命令可访问：可移动 USB 盘、CD/DVD 光盘，以及系统中的任意驱动器（F-008）。底层是 FAT/exFAT 的 U 盘也能挂载，但语义有降级（不区分大小写、不支持链接），见 [04 不同底层文件系统的语义差异](04-filesystem-semantics.md)。

## 常见报错

| 现象 | 对应原因（按博文时代记录） | 处理 |
|---|---|---|
| `mount: unknown filesystem type 'drvfs'` | Windows 版本早于 build 16176（正式版 15063 无此能力）（F-027） | 升级 Windows build；在发行版内 `apt-get update` **无效**，能力随 Windows 内核提供，见 [05](05-version-and-modern-wsl.md) |
| `mount point does not exist` 类错误 | 未先执行 `sudo mkdir /mnt/d` | 先建挂载点 |

现代 WSL 的自动挂载配置（`/etc/wsl.conf`）与 `wsl --mount` 物理磁盘直挂见 [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)。

## 相关概念

- [00 概览与三个心智模型](00-overview.md)
- [02 挂载 UNC 网络位置](02-network-mount.md)
- [04 文件系统语义差异](04-filesystem-semantics.md)
- [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)
