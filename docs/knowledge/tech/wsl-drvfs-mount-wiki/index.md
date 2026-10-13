---
okf_version: "0.2"
title: WSL DrvFs 挂载与跨文件系统访问教程
description: 基于微软官方归档博文（2017，build 16176）系统梳理 WSL 用 DrvFs 手动挂载 Windows 盘、UNC 网络共享与无盘符 NTFS 卷的完整方法，并经 V 阶段对抗审查补充现代 WSL（wsl.conf、metadata、wsl --mount）演进对照
tags: [wsl, drvfs, mount, unc, smb, ntfs, filesystem, tutorial]
status: draft
stale_after: "2027-10-13"
source: https://learn.microsoft.com/zh-cn/archive/blogs/wsl/file-system-improvements-to-the-windows-subsystem-for-linux
---

# WSL DrvFs 挂载与跨文件系统访问教程

> 在 WSL 中手动挂载 Windows 可移动盘、光驱、UNC 网络共享与无盘符 NTFS 卷的完整教程：命令范式、凭据边界、不同底层文件系统的语义差异，以及 2017 年原始能力与现代 WSL（WSL 2、wsl.conf、`wsl --mount`）的版本对照。史实部分逐条溯源至微软官方归档博文（36 条编号事实），现代部分引用现行官方文档（2026-10-13 抓取）。

---

## 导航

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```

| 类别 | 文档 | 说明 |
|------|------|------|
| **概览** | [能力概览与时代定位](concepts/00-overview.md) | 能力边界矩阵、三个核心心智模型 |
| **核心** | [DrvFs 手动挂载驱动器](concepts/01-drvfs-manual-mount.md) | U 盘 / 移动盘 / 光驱，建点—挂载—卸载三步 |
| **核心** | [挂载 UNC 网络位置与凭据边界](concepts/02-network-mount.md) | 单引号规则、`net.exe use` 预认证、无报错失败排查 |
| **进阶** | [挂载无盘符 NTFS 卷](concepts/03-ntfs-folder-volumes.md) | 空 NTFS 文件夹挂载点、与 bind mount 的分工 |
| **语义** | [不同底层文件系统的语义差异](concepts/04-filesystem-semantics.md) | 0777 权限位、大小写、链接支持矩阵、性能注意 |
| **版本** | [版本边界与现代 WSL 演进](concepts/05-version-and-modern-wsl.md) | build 门槛、wsl.conf、metadata 选项、`wsl --mount` |
| **信源** | [信源登记](references/00-sources.md) | S-001～S-005c，含抓取日期与稳定性分级 |
| **审查** | [R 阶段事实清单](references/01-fact-ledger.md) | F-001～F-036，A/B/C 置信度 |
| **审查** | [V 阶段对抗审查记录](references/02-adversarial-review.md) | 4 视角 8 条意见，采纳 5 条修正 |
| **日志** | [变更日志](log.md) | 七概念各阶段产出与质量门记录 |

## 学习路径建议

1. **3 分钟建立心智**：先读本页「三条必须先知道的结论」→ [00 概览](concepts/00-overview.md) 的能力边界表。
2. **照着挂载一个盘**：[01 DrvFs 手动挂载驱动器](concepts/01-drvfs-manual-mount.md)，三步命令即可完成。
3. **挂网络共享**：[02 挂载 UNC 网络位置](concepts/02-network-mount.md)，重点读凭据边界与失败排查。
4. **踩坑前先读语义**：涉及权限、大小写、软链、编译性能时读 [04 语义差异](concepts/04-filesystem-semantics.md)。
5. **现代 WSL 用户**：直接读 [05 版本边界与现代 WSL 演进](concepts/05-version-and-modern-wsl.md)，确认自动化挂载、权限元数据与物理磁盘直挂的现行做法。

## 三条必须先知道的结论

1. **drvfs 的「设备」是 Windows 路径名，不是 Linux 块设备。** `D:`、`\\server\share`、`C:\mountpoint` 都是同一条 `sudo mount -t drvfs <源> <挂载点>` 的合法源；WSL 里看不到某存储时，先问「它在 Windows 侧叫什么」（见 [01](concepts/01-drvfs-manual-mount.md)、[02](concepts/02-network-mount.md)、[03](concepts/03-ntfs-folder-volumes.md)）。
2. **网络共享的凭据在 Windows 侧，且「挂载无报错」不等于挂载成功。** drvfs 没有 `username=`/`password=` 选项；先用资源管理器、凭据管理器或 `net.exe use` 建立认证会话，再挂载，并以实际打开文件验证（见 [02](concepts/02-network-mount.md)）。
3. **本教程的命令 2017 年引入、在现代 WSL 中依然有效，但周边能力已换代。** 开机自动挂载（`/etc/wsl.conf` 的 `mountFsTab`）、权限元数据（`metadata` 选项）、Linux 格式物理盘直挂（管理员 `wsl --mount`）有现代正式方案，不要把 2017 年的限制当现状（见 [05](concepts/05-version-and-modern-wsl.md)）。

---

**信源**：[File System Improvements to the Windows Subsystem for Linux](https://learn.microsoft.com/zh-cn/archive/blogs/wsl/file-system-improvements-to-the-windows-subsystem-for-linux)（微软官方归档博文，Sven Groot，对应 Windows Insider build 16176）；现代演进引自 [跨 Windows 和 Linux 文件系统工作](https://learn.microsoft.com/zh-cn/windows/wsl/filesystems)、[WSL 高级设置配置](https://learn.microsoft.com/zh-cn/windows/wsl/wsl-config)、[在 WSL 2 中挂载 Linux 磁盘](https://learn.microsoft.com/zh-cn/windows/wsl/wsl2-mount-disk)。

**规范**：OKF v0.2（Open Knowledge Format）｜七概念方法论链路 R→I→E→V→C，session `sc-20261013-wsl-drvfs-mount-wiki`
