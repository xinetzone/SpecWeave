---
type: Concept
id: C-05
title: 版本边界与现代 WSL 演进
description: drvfs 手动挂载能力曾与 Windows build 强绑定（16176 引入、16299 正式渠道）；现代 WSL 已演进至 wsl.conf 自动挂载配置、DrvFs metadata 权限选项、WSL 2 的 wsl --mount 物理磁盘直挂与按侧布局的性能建议
tags: [wsl, drvfs, wsl2, wslconf, automount, wsl-mount, versioning]
generated:
  by: agent-trae
  at: "2026-10-13T20:30:00+08:00"
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

# 版本边界与现代 WSL 演进

本节解决两个问题：①读懂 2017 年博文命令的**版本前提**与历史报错；②这些能力在**现代 WSL（WSL 2 时代）**中的对应形态。现代部分事实全部来自 V 阶段补充信源 S-005a/b/c（2026-10-13 抓取）。

## 一、版本边界：能力曾随 Windows build 发布

博文命令对应 Windows Insider **build 16176**（F-002）。评论区现场记录（F-027）：

- build 15063（创意者更新正式版）+ Ubuntu 16.04/14.04 用户执行挂载得到 `mount: unknown filesystem type 'drvfs'`；
- 有用户升级到 build 16299.15 后反馈「working now」。

关键认知（洞察 I-4）：**WSL 1 时代该能力由 Windows 内核侧提供，不随发行版包分发**——在 Ubuntu 内执行 `apt-get update` 无法获得 drvfs 文件系统类型。排查顺序应是先查 Windows 版本（CMD/PowerShell 执行 `ver`，或「运行」中执行 `winver`），再查发行版。

> 在现代 Windows 10/11 中，drvfs 手动挂载（本教程 01～03 的命令）在 WSL 1 与 WSL 2 中均为既有能力，不再需要 Insider build。

## 二、`/etc/fstab` 自动化：历史问题与现代答案

博文发布当月就有读者问：能否用 fstab 自动挂载网络盘？评论区记录显示 16299 时代 fstab 条目可手动挂载，但**新开会话不自动生效**（F-028，C 级信源）。

现代答案在 `/etc/wsl.conf`（按发行版生效，F-032）：

```ini
[automount]
enabled=true          # 默认 true：固定盘自动挂到 DrvFs 的 /mnt 下
root=/mnt/            # 默认 /mnt/，自动挂载的根目录
options=""            # 仅接受 DrvFs 专属选项，追加到默认挂载选项串
mountFsTab=true       # 默认 true：启动时处理 /etc/fstab（可在此声明 SMB 共享）
```

`mountFsTab=true` 意味着现代 WSL 启动时会处理 `/etc/fstab`，博文时代「fstab 不自动执行」的问题已有正式配置位。改完配置需等发行版子系统完全停止后重启（官方文档称约 8 秒规则）。

### DrvFs 挂载选项：权限与大小写的现代化补救

博文记录的「网络盘恒报 0777」「不区分大小写」在现代有了选项级控制手段（F-033）：

| 选项 | 默认 | 作用 |
|---|---|---|
| `metadata` | disabled | 开启后向 Windows 文件写入元数据以支持 Linux 系统权限 |
| `uid` / `gid` | 默认用户（通常 1000） | 挂载内文件的属主/属组 |
| `umask` / `fmask` / `dmask` | 022 / 000 / 000 | 全部对象 / 文件 / 目录排除权限的八进制掩码（元数据挂载下适用） |
| `case` | off | `off`/`dir`/`force`，控制大小写敏感目录标志（详见官方 case-sensitivity 文档） |

wsl.conf 示例（F-033 所引官方示例）：

```ini
[automount]
enabled=true
root=/
options="metadata,uid=1003,gid=1003,umask=077,fmask=11,case=off"
mountFsTab=true
```

注意：这些选项改变的是 drvfs 的呈现方式，底层 FAT/网络共享不支持的能力（如真实符号链接）不会因此出现。

## 三、WSL 2 的新路径：`wsl --mount` 物理磁盘直挂

WSL 2 提供了与 drvfs **互补**的另一条挂载路径：在**管理员 PowerShell/CMD** 中把物理磁盘直接附加给 WSL 2（F-035）：

```powershell
# 1. 标识磁盘（DeviceID 形如 \\.\PHYSICALDRIVE0）
Get-CimInstance -Query "SELECT * from Win32_DiskDrive"

# 2. 挂载（省略 --type 默认 ext4；省略 --partition 整盘作单卷）
wsl --mount \\.\PHYSICALDRIVE2 --partition 1 --type ext4

# 3. 卸载
wsl --unmount \\.\PHYSICALDRIVE2
```

常用参数：`--partition <Index>`、`--type <Type>`（默认 ext4，可指定如 vfat）、`--options <Opts>`（仅文件系统专属选项；`ro`/`rw`/`noatime` 等通用选项不支持）、`--name <Name>`（Store 版 WSL，自定义挂载点名）、`--vhd <path>`（Store 版直挂 VHD）、`--bare`（只附加块设备不挂载）。

限制（F-036，务必先读）：

- 需要管理员权限；**不支持 USB/闪存盘/SD 读卡器**——这类外设走 USB/USBIPD 路径（官方「连接 USB 设备」文档）；
- 不能挂载正在使用的磁盘或其分区（即使只请求一个分区也会附加整盘），**不能挂载 Windows 安装磁盘**；
- 只能挂载 WSL 内核原生支持的文件系统（不能调用 ntfs-3g 等用户态驱动）；内核不直接支持的文件系统，先 `--bare` 附加，再在 WSL 内用 FUSE 驱动挂载。

### 与博文 drvfs 路径的分工

| 需求 | 路径 |
|---|---|
| 访问 Windows 侧的盘/共享（NTFS、FAT、SMB、光驱、无盘符卷） | 博文命令：WSL 内 `sudo mount -t drvfs ...`（本教程 01～03） |
| 让 WSL 2 原生访问 Windows 不支持的 Linux 格式磁盘（ext4 等） | `wsl --mount`（Windows 侧发起） |
| U 盘 / SD 卡等 USB 存储 | 先经 USB/USBIPD 附加，再视格式选择上述路径（不是 `wsl --mount` 直接支持） |

## 四、性能布局：现代官方建议

S-005a 的建议明确（F-034）：避免跨操作系统混用文件，除非有特定理由——

- 在 Linux 命令行工作：项目放 WSL 文件系统（`/home/<user>/`，Windows 侧经 `\\wsl$` 或 `\\wsl.localhost` 访问）；
- 在 Windows 命令行工作：项目放 Windows 文件系统（`C:\Users\...`，WSL 侧经 `/mnt/c/...`）。

这条官方建议与博文评论区的小文件 I/O 主观反馈（F-029）方向一致，但属于现行权威指引，可直接作为工作负载布局依据。

## 五、博文时代未竟诉求的去向（速查）

博文评论区的诉求（F-031 登记）在 WSL 2 时代的总体去向（仅高层指引，具体操作以现行官方文档为准）：

- **FUSE / sshfs**：WSL 2 使用完整 Linux 内核并支持用户态 FUSE；另可对不支持的磁盘文件系统走 `--bare` + FUSE（F-036）。
- **NFS**：WSL 2 内核内置常见网络文件系统能力，可在发行版内按标准 Linux 方式挂载，不再依赖 drvfs。
- **USB 串口/USB 设备**：走官方 USB/USBIPD（usbipd-win）附加路径；2017 年评论中提及的 Insider build 串口支持是 WSL 1 时代的早期方案。
- **冒号文件名 / MAX_PATH**：属于 Windows 文件系统命名与路径长度规则问题，与 drvfs 无直接关系；把工作负载放在 WSL 原生 ext4 一侧即可规避。

## 相关概念

- [00 概览与时代定位](00-overview.md)
- [01 DrvFs 手动挂载驱动器](01-drvfs-manual-mount.md)
- [02 挂载 UNC 网络位置与凭据边界](02-network-mount.md)
- [04 不同底层文件系统的语义差异](04-filesystem-semantics.md)
