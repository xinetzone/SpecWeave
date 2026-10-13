---
type: Reference
title: R 阶段事实清单（F-001～F-036）
description: 七概念方法论 R（复盘/事实采集）阶段产出，从微软官方归档博文、评论区及 V 阶段补充的现代官方文档中逐条登记的客观事实，不含因果推断
tags: [wsl, drvfs, mount, fact-ledger, retrospective]
generated:
  by: agent-trae
  at: "2026-10-13T20:08:00+08:00"
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
    title: 博文评论区社区反馈（2017-04～2017-10）
  - id: S-005a
    resource: /references/00-sources.md
    title: 跨 Windows 和 Linux 文件系统工作（现代官方文档）
  - id: S-005b
    resource: /references/00-sources.md
    title: WSL 高级设置配置 wsl.conf（现代官方文档）
  - id: S-005c
    resource: /references/00-sources.md
    title: 在 WSL 2 中挂载 Linux 磁盘 wsl --mount（现代官方文档）
---

# R 阶段事实清单（F-001～F-036）

> 七概念方法论 **R（Retrospective 事实采集）** 阶段产出。采集时间：2026-10-13。采集对象：[S-001] 微软官方归档博文全文（含正文五节）、[S-003] 同页评论区，以及 V 阶段采纳审查意见后补充抓取的 [S-005a/b/c] 现代官方文档（登记 F-032～F-036 五条演进事实）。
>
> **G1 纪律**：本清单只登记客观陈述，不出现「因为 / 导致 / 所以 / 由于 / 从而」等因果推断词；因果与解释在 I 阶段（洞察）中另行给出。每条事实标注信源与置信度：**A=官方正文权威陈述**，**B=官方背景链接或评论区交叉核对后采纳**，**C=评论区单源（仅作现象登记）**。

## A. 博文元信息与发布背景

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-001 | 博文标题为 *File System Improvements to the Windows Subsystem for Linux*，发布于 Microsoft Learn 的 WSL 博客归档，署名「Posted on behalf of Sven Groot」 | S-001 | A |
| F-002 | 博文所述功能随 Windows Insider **build 16176** 提供，正文链接到该 build 的 WSL release notes | S-001/S-004 | A |
| F-003 | 博文声明该文属于 WSL 系列文章，系列背景材料含：架构概览、pico 进程介绍、WSL 系统调用、WSL 文件系统支持（2016 年发布） | S-001/S-002 | A |

## B. 能力变更总览（Summary）

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-004 | build 16176 之前，WSL 在启动 Bash 时自动挂载全部**固定 NTFS 驱动器（fixed NTFS drives）** | S-001 | A |
| F-005 | build 16176 之前不支持挂载可移动驱动器、网络位置等附加存储 | S-001 | A |
| F-006 | build 16176 起，WSL 允许使用 **DrvFs** 文件系统**手动挂载** Windows 驱动器 | S-001 | A |
| F-007 | 同期新增对 FAT 等其他文件系统的支持 | S-001 | A |
| F-008 | 同期新增网络位置挂载支持；博文列举的可访问对象含可移动 USB 盘、CD 光盘以及 Windows 可达的任意网络位置 | S-001 | A |

## C. 手动挂载 DrvFs（Mounting DrvFs）

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-009 | 挂载可移动盘 D: 到 `/mnt/d` 的命令序列为 `sudo mkdir /mnt/d` 后执行 `sudo mount -t drvfs D: /mnt/d`，挂载后可在 `/mnt/d` 访问该盘文件 | S-001 | A |
| F-010 | 卸载命令为 `sudo umount /mnt/d`；博文给出的使用时机是安全移除设备之前 | S-001 | A |
| F-011 | 博文公开发布版本中曾遗漏 `sudo mkdir /mnt/d` 步骤，经评论指出后作者回复「Good catch. I have updated the instructions.」并补入正文 | S-001 评论区 | B |

## D. 网络位置挂载（Mounting network locations）

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-012 | 网络位置可先在 Windows 中映射为网络驱动器，再按普通驱动器方式在 WSL 中挂载 | S-001 | A |
| F-013 | 网络位置也可不映射盘符，直接以 UNC 路径挂载：`sudo mount -t drvfs '\\server\share' /mnt/share` | S-001 | A |
| F-014 | UNC 路径必须用**单引号**包裹以免除反斜杠转义；不加单引号时须将反斜杠双写（示例写法 `\\server\share`） | S-001 | A |
| F-015 | WSL 不提供为连接网络共享指定凭据（credentials）的手段 | S-001 | A |
| F-016 | 需要以其他凭据连接服务器时，须在 Windows 侧指定，途径有三：在文件资源管理器中访问该共享、使用 Windows 凭据管理器、使用 `net use` 命令 | S-001 | A |
| F-017 | `net use` 可经 interop 在 WSL 内以 `net.exe use` 调用；`net.exe help use` 可查看该命令用法 | S-001 | A |
| F-018 | 评论区有用户记录：执行 drvfs 挂载命令无任何报错，但挂载点不可访问（`ls` 报 No such file or directory），且同一命令重复执行后 mount 列表重复出现条目；该场景对应需要凭据的共享 | S-003 | C |

## E. 挂载到空 NTFS 文件夹的卷（Volumes mounted on empty NTFS folders）

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-019 | Windows 中存在没有盘符、改为挂载到空 NTFS 文件夹的卷；WSL 仅自动挂载带盘符的卷，该能力上线前此类卷在 WSL 中无法访问 | S-001 | A |
| F-020 | 此类卷在 WSL 中的挂载方式是以其 NTFS 挂载点路径为源：`sudo mount -t drvfs 'C:\\mountpoint' /mnt/myvolume` | S-001 | A |
| F-021 | drvfs 源路径必须是卷挂载点，不能以任意目录作为一个 drvfs 实例的根；若要实现任意目录映射，可使用 bind mounts | S-001 | A |

## F. 不同底层文件系统的 DrvFs 行为差异

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-022 | 博文明示：drvfs 的行为随底层文件系统不同而略有差异，并非所有特性在所有文件系统上均可用 | S-001 | A |
| F-023 | FAT 文件系统不区分大小写，不支持硬链接（hard links）与符号链接（symbolic links） | S-001 | A |
| F-024 | 网络文件系统上，DrvFs 不在文件上设置正确的 Linux 权限位，全部文件报告为完全访问权限 **0777** | S-001 | A |
| F-025 | 网络文件系统上，判断对某文件是否真正具备访问权限的唯一方法是尝试打开该文件 | S-001 | A |
| F-026 | 网络文件系统同样不区分大小写、不支持符号链接 | S-001 | A |

## G. 评论区：版本可用性、自动化与限制（2017 年现场记录）

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-027 | 多名评论者在 Ubuntu 16.04 / 14.04 上执行挂载得到 `mount: unknown filesystem type 'drvfs'`；登记的 Windows 版本为 10.0.15063（非 Insider）；有用户升级至 10.0.16299.15 后反馈「working now」 | S-003 | B |
| F-028 | 有用户在 16299.15 上记录：网络共享写入 `/etc/fstab`（写法 `\\server\path\to\share /mnt/h drvfs defaults 0 0`）后可手动挂载，但新开 WSL 会话不会自动挂载 | S-003 | C |
| F-029 | 评论区存在大量小文件 I/O 性能反馈：有用户称 tar/解压、启动 Apache、`make` 无变更检查等场景 WSL 慢于同机 VirtualBox 虚拟机；亦有评论提及杀毒软件对大量小文件访问存在可观影响。均为主观基准，无统一测量方法 | S-003 | C |
| F-030 | 有用户记录 exFAT 外接 SSD 案例：执行 `sudo mount -t drvfs 'U:Windows' /mnt/u` 后，WSL 与 Windows 两侧各自创建的文件互不可见（该命令的源路径写法与正文范式不一致） | S-003 | C |
| F-031 | 评论区集中出现的能力诉求与回应：FUSE/sshfs、NFS 挂载、USB 串口设备；官方账号回复 USB 串口设备已在 Insider build 中支持并给出链接 aka.ms/b0o8l9；另有 Fortran 程序生成含冒号 `:` 文件名在 Windows 文件系统上触发 I/O 错误的记录、对 MAX_PATH 限制的提问（正文未答复） | S-003 | C |

## H. V 阶段补充：现代 WSL 演进事实（2026-10-13 抓取）

| 编号 | 事实 | 信源 | 置信度 |
|---|---|---|---|
| F-032 | 现代 WSL 提供 `/etc/wsl.conf`（按发行版生效）的 `[automount]` 配置段：`enabled`（默认 true，固定盘自动挂到 DrvFs 的 `/mnt` 下）、`root`（默认 `/mnt/`）、`options`（仅接受 DrvFs 专属选项，追加到默认挂载选项串）、`mountFsTab`（默认 true，启动时处理 `/etc/fstab`，可在其中声明 SMB 共享等额外文件系统实现开机自动挂载） | S-005b | A |
| F-033 | DrvFs 自动挂载选项含 `uid`/`gid`（默认取发行版默认用户，通常 1000）、`umask`（默认 022）、`fmask`、`dmask`、`metadata`（默认 disabled，开启后向 Windows 文件写入元数据以支持 Linux 权限）、`case`（`off`/`dir`/`force`，默认 off）；官方说明 umask/fmask 等掩码选项在以元数据方式挂载时适用 | S-005b | A |
| F-034 | 现代官方文档明确性能布局建议：避免跨操作系统使用文件，除非有特定理由；在 Linux 命令行工作则文件放 WSL 文件系统（如 `/home/<user>/Project`），在 Windows 命令行工作则放 Windows 文件系统；在 WSL 路径中看到 `/mnt/` 即表示正在使用已挂载驱动器，项目文件直接放 `\\wsl$` 一侧更快 | S-005a | A |
| F-035 | WSL 2 支持在管理员 PowerShell/CMD 中执行 `wsl --mount <Disk>` 直挂物理磁盘：省略 `--type` 时默认按 ext4 挂载；支持 `--partition <Index>`（省略则整盘作单卷）、`--options <Opts>`（仅文件系统专属选项，`ro`/`rw`/`noatime` 等通用选项不支持）、`--name <Name>`（仅 Store 版 WSL）、`--bare`（只附加不挂载，供 FUSE 等驱动使用）、`--vhd <path>`（Store 版直挂 VHD）；卸载为 `wsl --unmount [DiskPath]`；磁盘标识可用 `Get-CimInstance -Query "SELECT * from Win32_DiskDrive"`，路径形如 `\\.\PHYSICALDRIVE*` | S-005c | A |
| F-036 | `wsl --mount` 的限制：需要管理员权限；不支持 USB/闪存驱动器/SD 读卡器（此类外设走 USB/USBIPD 路径）；不能挂载正在使用的磁盘或其分区（即使只请求一个分区也会附加整盘）、不能挂载 Windows 安装磁盘；只能挂载 WSL 内核原生支持的文件系统（无法借 ntfs-3g 等已装驱动），内核不直接支持的文件系统经 `--bare` 附加后在 WSL 内调用 FUSE 驱动挂载 | S-005c | A |

## G1 质量门自检

- [x] 事实条数 36 ≥ 20
- [x] 逐条复核无因果推断词（因果解释全部后移至 I 阶段）
- [x] 每条事实有信源编号与置信度标注
- [x] 评论区单源事实（C 级）与官方正文事实（A 级）显式区分，C 级条目不进命令范式、只作排错现象
- [x] 现代事实（F-032～F-036）由独立现行信源 S-005a/b/c 承载，与 2017 年史实分离登记

**G1 结论：通过。**
