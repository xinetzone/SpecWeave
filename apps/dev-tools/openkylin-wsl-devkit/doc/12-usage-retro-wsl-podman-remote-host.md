---
type: "Report"
title: "三路用法复盘：WSL、Podman 与 10.16.11.3 的取舍边界"
report_version: "v1.0"
date: "2026-11-06"
status: "final（事实截至 2026-11-06 11:00）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
methodology: "seven-concepts-cmd（F→V→I→E→C）"
source: "本轮现场复核（2026-11-06，Windows 侧 `wsl -l -v`/`fsutil`/`Get-Volume`，服务器侧 `podman`/`df`/`du`）＋ 10 号与 11 号复盘已固化事实"
---

# 三路用法复盘：WSL、Podman 与 10.16.11.3 的取舍边界

> **本篇职责**：把这一路试出来的事实，沉淀为「什么场景该走哪条路、每条路的边界在哪、哪些约束不可绕过」。这是一份**面向未来用法**的复盘，不是里程碑复盘——10 号讲「为什么从 WSL 转向远端」，11 号讲「EOL/CRLF 与远程连接如何收口」，本篇只回答「下次动手时怎么选、怎么验」。
> **本篇不负责**：方案级决策依据见[09-1](09-1-backend-and-decision.md)；挂载与 UID 细节见[09-2](09-2-mounts-uid-storage.md)；工具链供给见[09-3](09-3-toolchain-provisioning.md)；构建命令见[09-4](09-4-build-and-verify.md)；验收判定见[09-5](09-5-acceptance-and-evidence.md)；风险与待办见[09-6](09-6-risks-todos-changelog.md)；历史转折见[10 号](10-milestone-retro-remote-podman.md)与[11 号](11-milestone-retro-eol-and-remote-connection.md)。

## 0. 结论摘要

- **一句话**：WSL、Podman、10.16.11.3 **不是同一层的竞品**。WSL 提供「Windows 上的 Linux 内核与 VM 边界」，Podman 提供「进程与镜像边界」，10.16.11.3 提供「块存储与 15 TB 数据平面」。把它们放在一起比「谁更省」，问题本身就问错了层。
- **真正的硬约束只有四条**：① VHDX 必须落在本地固定盘（DriveType=3，`wsl --import` 强制）；② overlay 要求底层具备 d_type / user xattr / hardlink / flock（SMB 不具备）；③ bind 可写的前提是容器 uid 与宿主 uid 对齐（实测 1006）；④ 镜像层不承载构建产物时，运行期依赖由卷提供，卷即隐式运行时依赖。
- **当前选择的四条**（可改，不是硬约束）：默认连接指向 `remote-ai`；graphroot 经软链落在 XFS；基镜像用 `3.0` 而非 `3.0-minimal`；审计脚本取 10 项静态口径。
- **最该带走的一条判断**：**「谁的分区余量最稀缺，就把负载放在另一侧」**。Windows 侧 D: 只剩 30.62 GB（`Get-Volume`），服务器 XFS 尚有 293.28 GiB 可用（`df -B1`，已用 99%）——所以构建必须去远端；但反过来若 D: 扩容到 TB 级，「全远端」就不再必然更省。
- **最容易反复踩的一脚**：这台服务器上的 `podman` **不是一个二进制，而是一个按用户分流的包装器**。`ai` 用户落到 conda py313 的 5.6.2 并叠加 `containers-5.conf`，其他用户落到 `/usr/bin/podman` 3.4.4。直接写绝对路径 `/usr/bin/podman`，拿到的是 3.4.4（本次即出现 `podman info` 模板字段不存在）。

**五条核心结论**

1. 构建负载应放远端，理由是 Windows 本地盘余量（30.62 GB）比服务器（293.28 GiB）稀缺两个数量级，不是「远端更快」。
2. WSL 的价值不是「跑容器」，而是「提供 systemd、独立内核、drvfs 跨文件系统挂载」——这三项 Podman 一项都给不了。
3. 镜像层与卷是**不可变 / 可变**的分工。镜像层零 tvm/xmnn 实体（B1 断言）意味着镜像不能独立交付，这不是缺陷，是必须写进契约的取舍。
4. 所有体积结论只认字节数。`podman images` 的 `26 GB` 与 `inspect .Size` 的 `25,976,321,159 B` 是同一件事（24.19 GiB），混读单位会制造假矛盾。
5. 自检脚本必须先做「能力探测」再谈健康度：`podman system df` 在本机直接报错、`podman ps` 只打印帮助，这两条都不能当健康判据。

## 1. 范围、口径与事实基线

### 1.1 三条路（加一条对照路）的定义

本文件用词固定如下，避免后文歧义：

| 代号 | 形态 | 提供的边界 | 2026-11-06 现场状态 |
|---|---|---|---|
| **A 路** | WSL2 发行版 `openkylin-test`（VHDX on `D:\WSL`） | 内核 / VM 边界 | Stopped（`wsl -l -v`） |
| **B 路** | Windows Podman 客户端 + podman machine（WSL 后端） | 进程 / 镜像边界（本地） | 两台 machine 均未运行（`podman machine ls`） |
| **C 路** | 任意客户端 → SSH → 10.16.11.3 的 rootless Podman 5.6.2 | 进程 / 镜像边界（远端） | 多个容器在跑（`podman container ps --all`） |
| **D 路** | 直接在 10.16.11.3 宿主上跑进程（非容器） | 无隔离，仅文件系统边界 | 常驻可用 |

> 说明：B 路与 C 路才是同层比较（都是 Podman），A 路与它们不同层。历史上把 A 路当「B 路的廉价替代」来评估，是 10 号复盘里最主要的判断偏差来源。

### 1.2 事实基线（R）

| # | 事实 | 测量口径 | 采集时间 |
|---|---|---|---|
| R-01 | WSL 发行版 `openkylin-test`，Version 2，State=Stopped | `wsl -l -v` | 2026-11-06 |
| R-02 | `D:\WSL\openkylin-test\ext4.vhdx` 长度 **1,399,848,960 B**（1.30 GiB），属性含 `SparseFile`，`fsutil sparse queryflag` 返回 "This file is set as sparse" | `Get-Item.Length` + `fsutil` | 2026-11-06 |
| R-03 | D: 为 NTFS，总 **112.28 GB**，可用 **30.62 GB** | `Get-Volume` | 2026-11-06 |
| R-04 | `.wsl` 包 `D:\WSL\import\openKylin-3.0-wsl-amd64.wsl` = **352,431,812 B**；服务器同名文件同尺寸；desktop 包 = **6,592,986,686 B**（另有 `-old` 同尺寸副本） | `Get-Item.Length` / `stat -c %s` | 2026-11-06 |
| R-05 | 该包解压后 rootfs = **1,182,607,360 B** | 前序实测（解压后 tar 流字节数），本轮未复测 | 2026-11 前序 |
| R-06 | 向 WSL 内写入 1 GiB 后，VHDX 文件长度 Δ=0 | 写入前后 `Get-Item.Length` 差值，单次观测 | 2026-11 前序 |
| R-07 | WSL 内**无** gcc / sshd / conda；`/etc/wsl.conf` 自带 `systemd=true`；drvfs 挂载 `/media/pc/data/ai` 由 systemd mount unit 持久化 | 前序实测，本轮未复测 | 2026-11 前序 |
| R-08 | `wsl --import` 只接受本地固定盘（DriveType=3）；`S:` 为 DriveType=4（网络盘） | 10 号报告已固化 | 2026-11-01 |
| R-09 | `vmcompute` / `wslservice` 以 SYSTEM 身份持有导入包独占句柄，非管理员会话无法释放 | 10 号 / 11 号已固化 | 2026-11-02 |
| R-10 | Windows Podman **5.8.1**；machine 两台：`podman-machine-default`（last up 3 weeks ago）、`machine-os`（Never），均 4 CPU / 2 GiB / 100 GiB | `podman machine ls` | 2026-11-06 |
| R-11 | 服务器 `podman` 是 POSIX sh 分流包装器（`/usr/local/bin/podman`、`/home/ai/.local/bin/podman`）：`ai` → conda py313 的 **5.6.2** + `CONTAINERS_CONF_OVERRIDE=~/.config/containers/containers-5.conf`；其他用户 → `/usr/bin/podman` **3.4.4** | `cat` 两个包装器 + 三次 `--version` | 2026-11-06 |
| R-12 | 服务器 Podman 5.6.2：`Rootless=true`，`GraphDriver=overlay`，`GraphRoot=/home/ai/.local/share/containers/storage`；`readlink -f` 指向 `/media/pc/data/ai/.agents/podman-storage/storage` | `podman info --format` + `readlink -f` | 2026-11-06 |
| R-13 | `podman images` SIZE（十进制 GB）：`openkylin:3.0` **26 GB**、`openkylin-npu-toolchain:3.0` **14 GB**、`3.0-minimal` **2.37 GB**、`3.0-minimal-gcc` **1.46 GB**；另有 `<none>` 13.7 / 1.86 / 1.19 GB | `podman images` | 2026-11-06 |
| R-14 | `inspect .Size`（字节）：`25,976,321,159` / `14,044,799,709` / `2,365,215,839` | `podman image inspect --format '{{.Size}}'` | 2026-11-06 |
| R-15 | 卷 `npu-build` 数据目录 **7,309,844,950 B**（6.81 GiB） | `du -sb <mountpoint>/_data` | 2026-11-06 |
| R-16 | graphroot 全树 **46,658,270,520 B**（43.45 GiB），多处 Permission denied → **下界** | `du -sb <graphroot>` | 2026-11-06 |
| R-17 | `/media/pc/data`：总 15,998,762,643,456 B，可用 **314,910,449,664 B**（293.28 GiB），Use 99%；`/`：总 243,936,256,000 B，可用 **13,608,550,400 B**（12.67 GiB），Use 95%；`/home/ai` 落在 `/` | `df -B1` | 2026-11-06 |
| R-18 | `podman system df` 报 `lstat /run/user/1006/libpod/tmp/infra-container: no such file or directory`。另一条：用 `/usr/bin/podman`（3.4.4）执行 `info` 时报警 `OCI Runtime crun130 is in use by a container, but is not available`，并把运行时回退为 `crun`；而 5.6.2 下 `info` 正常返回 `crun130 /home/ai/.local/bin/crun`。根因：`crun130` 只定义在 `containers-5.conf`（`crun130=["/home/ai/.local/bin/crun"]`，该软链指向存在的 `crun-1.30.1`，可执行）；3.4.4 不读该覆盖文件，因而不认识该运行时名 | `podman info` 原文 + `grep` 配置原文 + `ls -l` soft link | 2026-11-06 |
| R-19 | 容器：`npu-toolchain` **Up 3 days**、`npu-toolchain-minimal` **Up 25 hours**、`native-dev` / `agent-monetize-dev` **Up 3 weeks**、`9514ffe234c3-infra` Created | `podman container ps --all` | 2026-11-06 |
| R-20 | 审计脚本共 12 处 `check`：A1–A7（7）、B1–B3（3）、C1–C2（2）。默认口径 **10 项**，`--with-volume` 为 **12 项** | `grep -n 'check "' audit-image-contract.sh` | 2026-11-06 |
| R-21 | 镜像层内零 `libtvm.so` / `tvm` / `xmnn` 实体，仅 `.pth` 指针；实体全在卷内 | B1 断言 + `du -sb` 卷 | 2026-11-04 起 |
| R-22 | `podman ps` 打印帮助且不列容器；`podman container ps --all` 正常 | 两次复现（`ps` / `ps -a` / `ps --all`） | 2026-11-06 |
| R-23 | EOL/CRLF 残留 **3,275** 处 | 逐文件行尾扫描（11 号口径） | 2026-11-04 |

### 1.3 测量口径与已知偏差

| 口径 | 含义 | 已知偏差 |
|---|---|---|
| `df -B1` 差 | 块级可用字节差 | 准；但相邻命令间有其他进程写入时会有噪声，故余量一律取同一时刻 |
| `du -sb` | 目录下文件字节和 | 软链不跟随；**权限拒绝的目录静默跳过** → 结果是下界（R-16 即下界） |
| `podman images` SIZE | 十进制 GB，四舍五入 | 与 GiB 混读会得到「矛盾」（见 V6） |
| `podman image inspect .Size` | 未压缩层字节和 | 与容器内 `du` 口径不同，不可互换 |
| 容器内 `du -sb --one-file-system /` | 排除 bind 挂载与卷 | 只反映镜像层，不含卷内容 |
| `Get-Item.Length`（VHDX） | 文件逻辑长度 | sparse 文件的实际磁盘占用需另查分配大小，本轮未测 |
| `wsl -l -v` | 瞬时状态 | Stopped 只代表查询时刻 |
| `podman machine ls` 的 LAST UP | 相对时间 | 精度到周，不能当精确停机时刻 |

## 2. 第一性原理（F）：四组区分如何决定路线

### 2.1 本地盘 vs 网络盘

**这条区分直接判死了 A 路的一个落点选项**。`wsl --import` 要求目标卷是本地固定磁盘（DriveType=3），而 `S:` 是网络映射盘（DriveType=4），实测被拒（R-08）。于是 A 路只剩下 D: 一个可选落点，而 D: 只有 112.28 GB / 可用 30.62 GB（R-03）。

反过来，C 路不受这条约束——它的「落盘」发生在服务器的本地块设备上，与 Windows 盘符无关。**同一份「磁盘放哪儿」的问题，在 A 路是硬约束，在 C 路不是问题**，这就是两条路不同层的直接后果。

### 2.2 块存储 vs 共享文件系统

overlay 驱动要求底层提供四项能力：d_type、user xattr、hardlink、flock。SMB/CIFS 不具备完整语义，落到 SMB 上的 graphroot 会回退 vfs——空间与性能代价同时上升。

实测两侧都满足：服务器 graphroot 落在 `/dev/sda1` 的 XFS 上，`GraphDriverName=overlay`（R-12）；drvfs 挂载虽能读写，但元数据缓存会造成「宿主侧看不到刚写的文件」这类假象（前序实测）。

**判断顺序应当是：先探测文件系统能力，再选存储驱动**。这不是配置项，是能力探测项。

### 2.3 镜像层 vs 卷

镜像层不可变、按层共享、可被 `save`/`load` 搬运；卷可变、按名引用、只存在于本机。实测分工非常清楚：

- 镜像层：`openkylin-npu-toolchain:3.0` 报 14 GB（`podman images`）/ 14,044,799,709 B（`inspect .Size`），但**层内没有任何 tvm/xmnn 实体**，只有 `.pth` 指针（R-21）。
- 卷：`npu-build` 承载 llvm22 / tvm / xmnn，`du -sb` = 7,309,844,950 B（R-15）。

**结论**：镜像负责「环境」，卷负责「产物」。一旦把产物放进卷，镜像就**不能独立交付**——换机 `save`/`load` 过去仍然 `import tvm` 失败。这条后果必须显式写进契约（B1 断言 + 09-4 的挂载契约），否则三个月后没人记得。

### 2.4 进程边界 vs 文件系统边界

容器只隔离进程与命名空间，**文件系统是穿透的**：bind 把宿主目录带进容器，能不能写由宿主 uid 权限决定。实测契约是容器内运行用户 = 宿主 uid `1006`（`--userns=keep-id`），挂载探针文件权限必须是 `700 1006`。

这解释了一个常见误判：容器「写不进去」时，第一反应是查容器配置，但真正的决定因素是宿主目录属主与权限。**挂载是容器的边界交点，也是唯一需要双侧同时验证的地方**（宿主看得到、容器写得出、属主对得上）。

### 2.5 把「硬约束」与「当前选择」分开

| 类别 | 条目 | 依据 | 能否改 |
|---|---|---|---|
| **硬约束** | VHDX 必须在本地固定盘 | R-08 | 否（Windows 语义） |
| **硬约束** | overlay 要求 d_type / xattr / hardlink / flock | R-12 反向推论 | 否（驱动语义） |
| **硬约束** | bind 可写要求容器 uid = 宿主 uid | 探针 700/1006 | 否（除非改 UID 映射） |
| **硬约束** | 产物进卷 → 镜像不自足 | R-21 | 否（逻辑后果） |
| **当前选择** | 默认连接 = `remote-ai` | 连接配置 | 是 |
| **当前选择** | graphroot 经软链落 XFS | R-12 | 是（但要迁移数据） |
| **当前选择** | 基镜像 `3.0` 而非 `3.0-minimal` | 镜像清单 | 是 |
| **当前选择** | 审计取 10 项静态口径 | R-20 | 是（可扩） |
| **当前选择** | Windows 侧保留 WSL 发行版 | R-01 | 是（可注销） |

把这两类混在一起，就会得出「远端必须用、WSL 必须废」这种过度结论——实际上只有前四行不可协商。

## 3. 对抗审查（V）：七个攻击点

### V1「全远端一定更省」——**不成立**

省钱的对象错了。C 路省下的是 Windows 侧最稀缺的资源：D: 可用 30.62 GB（R-03）、两台 machine 各配置 2 GiB 内存（R-10，未运行即未占用）。但成本转移到了服务器：graphroot 已占 43.45 GiB 以上（R-16，下界），XFS 已用 99%（R-17），根分区只剩 12.67 GiB。

更关键的是**可观测性反而变差**：远端 `podman system df` 直接报错（R-18）、`podman ps` 打不出列表（R-22），只剩 `images` / `inspect` / `container ps` / `du` 可用。

正确表述：**在当前余量结构下，构建放远端更省**；判据是「谁的分区余量最稀缺」，不是「远端」这个方向本身。

### V2「WSL 只是 Podman 的劣化替代」——**不成立**

二者不同层。WSL 提供的能力 Podman 一项都给不了：

- 独立内核与 systemd（`/etc/wsl.conf` 自带 `systemd=true`，R-07）；
- 完整发行版用户空间（可装 gcc/sshd/conda，虽然当前未装）；
- drvfs 跨文件系统挂载，把 15 TB 共享盘映射进 Linux 路径；
- 整个 VM 只花 1.30 GiB 磁盘（R-02，稀疏）。

而 Podman 提供的镜像分层、卷、rootless 隔离，在 WSL 里面同样能装一份。

真正的同层替代关系是「**WSL 内跑 Podman**」vs「**远端跑 Podman**」——10 号复盘比的正是这一层，结论也只对这一层成立。把边界层级不同的两件事做优劣比较，是这次复盘最该纠正的思维习惯。

### V3「把构建产物放卷里，掩盖了镜像不可复现」——**部分成立**

成立的部分：镜像层零 tvm/xmnn 实体（R-21），`podman save` 出去的镜像不含卷内容，换一台机器 `import tvm` 必失败。镜像**不是**自足交付物。

不成立的部分：这不是「被掩盖」，而是「被显式化」。B1 断言（镜像内不得有实体）+ C1 断言（`libLLVM` 必须解析到卷内 `llvm22`）把这条后果写成了可执行契约；09-4 的挂载契约又规定了「卷 + bind 缺一即 A3/A4/A5/A8/A9 FAIL」。

所以准确表述是：**不可复现是设计取舍，不是隐藏缺陷；风险从「无人知晓」转为「文档与断言必须同步维护」**。反证条件也明确——若哪天 B1 被删、或卷内容没有清单，这条就退化为真正的掩盖。

### V4「99% 的盘还能不能算可用」——**部分成立**

数学上可用：`df -B1` 显示可用 314,910,449,664 B ≈ 293.28 GiB（R-17），装一个 26 GB 报数的镜像（R-13）绰绰有余。

工程上不可轻信：99% 的 XFS 没有配额，任何一次 `podman build` + `load` 都可能吃掉数十 GB；而 `podman system df` 不可用（R-18），意味着**你不知道层占用，只能靠 `du` 现场算**。

结论：可用，但必须用**绝对阈值门禁**（如「XFS 可用 ≥ 50 GB 才允许启动新构建」），而不是百分比。百分比在 99% 附近几乎没有分辨率——从 99.0% 到 99.9%，剩余空间会从 293 GiB 掉到 29 GiB，而百分比只动了 0.9。

### V5「审计脚本 10 项 PASS 等于环境健康」——**不成立**

审计的判定对象是**镜像静态内容**：A1–A7 验「该有的在」，B1–B3 验「不该有的不在」，`--with-volume` 追加 C1–C2（R-20）。它不覆盖：

- 运行态（容器是否在跑、进程是否健康）；
- 卷内容完整性（C1 只验 `libLLVM` 解析路径）；
- 磁盘余量、SSH 连通性、drvfs 缓存、EOL/CRLF（R-23 的 3,275 处完全在审计视野之外）。

最有力的反证就在同一时刻：审计可以全 PASS，而 `podman system df` 正在报错（R-18）、`podman ps` 打不出容器列表（R-22）。所以 PASS 的含义必须写死为「**镜像静态内容符合契约**」，不能外推为「环境健康」。

### V6（补充）「13 与 26 的体积矛盾说明统计不可信」——**不成立**

本轮对同一对象做了双口径实测：`podman images` 报 `26 GB`（R-13），`inspect .Size` 报 `25,976,321,159 B`（R-14）。换算：25,976,321,159 B = 24.19 GiB = 25.98 GB（十进制），与 `26 GB` 的差异来自四舍五入，**小于 0.1%**。`14 GB ↔ 14,044,799,709 B` 同理。

历史上的「13 与 26」在本轮无法复现——可能是不同镜像版本并存，也可能是 GiB/GB 混读。**处置方式不变：所有体积只记字节数，展示层再换算**。

### V7（补充）「graphroot 在 `/media/pc/data` 就等于落在 XFS」——**成立，但有前提**

`podman info` 报的 GraphRoot 是 `/home/ai/.local/share/containers/storage`（R-12），看起来落在根分区（只剩 12.67 GiB）。实际 `readlink -f` 指向 `/media/pc/data/ai/.agents/podman-storage/storage`，是 XFS。

前提是**软链存在**。工作区红线明确禁止改名 `.agents/podman-storage/`，正是因为这条链被硬编码引用。任何重建家目录、清理 `.local/share` 的操作，都会让 podman「看不见」全部镜像与卷——数据还在，入口断了。

### V8（补充）「这台机器上的 podman 就是 podman」——**不成立**

`/usr/local/bin/podman` 与 `/home/ai/.local/bin/podman` 都是分流脚本（R-11）：

- `id -un = ai` → conda py313 的 **5.6.2**，并注入 `XDG_RUNTIME_DIR=/run/user/1006`、`CONTAINERS_CONF_OVERRIDE=containers-5.conf`，以及「幂等预置 `image_copy_tmp_dir`」；
- 其他用户 → `/usr/bin/podman` **3.4.4**。

本次实测就踩到了两处：用 `/usr/bin/podman info --format '{{.Host.PodmanVersion}}'` 直接报「模板字段不存在」（3.4.4 的字段路径不同）；用 `/usr/bin/podman info` 还会报 `OCI Runtime crun130 ... is not available` 并把运行时**回退为 `crun`**（R-18）——因为 `crun130` 只写在 3.4.4 不读的 `containers-5.conf` 里。而登录 shell 里的 `podman --version` 是 5.6.2，运行时即 `crun130`。

**结论**：在这台机器上，写脚本要么用 `podman`（依赖 PATH），要么同时锁定版本断言；写死 `/usr/bin/podman` 会静默降级到 3.4.4。

### 3.9 审查结果汇总

| # | 攻击点 | 判定 | 一句话理由 |
|---|---|---|---|
| V1 | 全远端一定更省 | **不成立** | 省的是 Windows 盘，费的是 XFS 与可观测性 |
| V2 | WSL 是 Podman 的劣化替代 | **不成立** | 内核/VM 边界 ≠ 进程/镜像边界 |
| V3 | 卷承载产物掩盖镜像不可复现 | **部分成立** | 不可复现是事实，但已被 B1/C1 显式化 |
| V4 | 99% 的盘仍可用 | **部分成立** | 绝对值够，百分比无分辨率，须用绝对阈值 |
| V5 | 审计 10 项 PASS = 环境健康 | **不成立** | 只覆盖镜像静态内容 |
| V6 | 体积报数矛盾 | **不成立** | 十进制/二进制混读 |
| V7 | graphroot 在 XFS | **成立（有前提）** | 依赖软链不断 |
| V8 | podman 是单一二进制 | **不成立** | 按用户分流，两版本并存 |

## 4. 洞察（I）：条件 → 结论 → 依据

**I1｜需要内核级能力（systemd、网络命名空间、独立内核）**
→ 选 WSL，不要把这类需求塞进容器。
→ 依据：`/etc/wsl.conf` 自带 `systemd=true`（R-07）；rootless 容器内无法起 systemd，这是设计前提而非配置缺失。

**I2｜需要跑构建，且 Windows 本地盘余量是最稀缺资源**
→ 选远端（C 路）。
→ 依据：D: 可用 30.62 GB（R-03）vs XFS 可用 293.28 GiB（R-17），差两个数量级。

**I3｜构建产物大于 1 GB 且需要跨会话复用**
→ 放卷，不进镜像层；同时在镜像里留下指针（`.pth`）。
→ 依据：镜像层零 tvm/xmnn 实体、卷 6.81 GiB（R-15 / R-21）；这条分工把镜像体积从「随产物膨胀」变成「恒定环境」。

**I4｜需要判断「磁盘够不够」**
→ 用绝对可用字节 + 增长速率，不用百分比。
→ 依据：99% 时仍有 293.28 GiB（R-17），百分比在饱和区没有分辨率（V4）。

**I5｜需要判断「镜像多大」**
→ 只认 `inspect .Size` 的字节数，展示层再换算。
→ 依据：`26 GB` 与 `25,976,321,159 B` 是同值异单位（R-13 / R-14），混读会制造假矛盾（V6）。

**I6｜需要长期驻留（天级及以上）**
→ 用远端容器，并显式声明重启策略或交给宿主 systemd；不要指望 Podman machine 自动活着。
→ 依据：远端 `npu-toolchain` 已 Up 3 days（R-19），而 Windows 侧两台 machine 均未运行（R-10）。

**I7｜需要判断同一份文件在两侧的状态**
→ 以服务器侧命令为准，SMB 侧只作参考。
→ 依据：SMB 存在内容缓存与 d_type/xattr 缺失（前序实测），元数据可能滞后；而服务器侧是本地块设备。

**I8｜受限网络内要补工具链**
→ 从宿主复制（`podman cp` / `tar | exec tar -x`），不要在容器内 apt/pip 装大包。
→ 依据：09-3 已固化——容器内无 apt 源，conda-forge 的 llvmdev 大包不可达，仅有 `mirrors.ustc.edu.cn` 与 `mirrors.aliyun.com` 白名单。

**I9｜要写任何自检或巡检脚本**
→ 先做能力探测（版本 / 容器列表 / 卷），再谈健康度。
→ 依据：`podman system df` 报错、`podman ps` 只打印帮助（R-18 / R-22），而 `container ps`、`images`、`volume inspect` 均正常。

**I10｜要在脚本里调用 podman**
→ 用 `podman`（走 PATH）并断言版本，或显式接受 3.4.4 的行为差异；不要写死 `/usr/bin/podman`。
→ 依据：分流包装器（R-11），写死绝对路径会静默降级。

## 5. 萃取（E）：可复用手法与一次性结论

### 5.1 可复用的检查手法

| # | 手法 | 怎么做 | 通过判据 |
|---|---|---|---|
| M1 | 三步能力探测 | `podman --version` → `podman info --format '{{.Host.Security.Rootless}}'` → `podman container ps --all` | 版本符合预期、`true`、能列出容器 |
| M2 | 双口径体积记录 | 同时记 `podman images` 与 `inspect .Size`，只把字节数写进结论 | 两口径换算误差 < 1% |
| M3 | 绝对余量门禁 | `df -B1` 取可用字节，设两个阈值（XFS ≥ 50 GB、根 ≥ 5 GiB） | 均高于阈值 |
| M4 | 挂载契约探针 | 容器内写探针文件，`stat -c '%a %u'` | `700 1006`，且宿主侧可见 |
| M5 | 卷占用实测 | `du -sb <mountpoint>/_data` | 与上一次记录同量级 |
| M6 | graphroot 落点验证 | `readlink -f /home/ai/.local/share/containers/storage` | 指向 `.agents/podman-storage/storage` |
| M7 | 镜像静态契约审计 | `bash scripts/audit-image-contract.sh` | `exit=0`，`total=10 pass=10`（带卷 12） |
| M8 | 容器清单用长路径 | `podman container ps --all` | 有输出，不打印帮助 |
| M9 | VHDX 三查 | `wsl -l -v` + `Get-Item.Length` + `fsutil sparse queryflag` | Version=2、长度合理、sparse 已设 |
| M10 | 分层落盘 | 环境进层、产物进卷、指针进层（`.pth`） | B1 零实体 + C1 解析到卷 |
| M11 | 提交前基线 | `git status --porcelain` + `rev-list --left-right --count` | 仅预期文件变动 |

### 5.2 一次性结论（只对 2026-11-06 这个现场成立，不要外推）

- D: 可用 30.62 GB、两台 machine 均未运行（R-03 / R-10）。
- XFS 已用 99%、可用 293.28 GiB；根分区可用 12.67 GiB（R-17）。
- 当前镜像清单与体积（26 / 14 / 2.37 / 1.46 GB 等，R-13）。
- `npu-toolchain` Up 3 days、`npu-toolchain-minimal` Up 25 hours（R-19）。
- `crun130` 只定义在 `containers-5.conf` 中；3.4.4 读不到该覆盖文件，会把运行时回退为 `crun`（R-18）——这是版本分流的后果，不是坏二进制。
- EOL/CRLF 残留 3,275 处（R-23），是治理进度快照。

### 5.3 反模式

1. **用 `podman images` 的 GB 数字做容量规划**——十进制与二进制混读会差 7%，且掩盖真实字节。
2. **用 `podman ps` 判断容器状态**——本机会打印帮助（R-22），看起来「没有容器」。
3. **用 `podman system df` 做存储统计**——本机直接报错（R-18），且即使正常也含 infra 容器瑕疵。
4. **写死 `/usr/bin/podman`**——静默降级到 3.4.4（R-11）。
5. **把 `/home/ai/.local/share/containers/storage` 当真实路径做备份或清理**——它是软链入口（R-12 / V7）。
6. **在容器内 apt/pip 装大工具链**——网络白名单不允许，且会把镜像撑大（09-3）。
7. **把构建产物写回 bind 挂载的工作区**——会污染源码树，且 `du` 统计被 15 TB 共享盘淹没。
8. **用百分比判断磁盘可用性**——99% 附近没有分辨率（V4）。

## 6. 交付（C）：分场景决策表与开工检查清单

### 6.1 分场景决策表

| 场景 | 首选 | 次选 | 不要选 | 判定依据 |
|---|---|---|---|---|
| 只跑 CPU 构建（tvm / xmnn），产物落卷 | **C 路**：远端 `npu-toolchain` 容器 + `npu-build` 卷 | D 路：远端宿主直接跑 | A 路：WSL 内跑（无 gcc/conda，且 D: 仅 30.62 GB） | R-07 / R-03 / R-15 |
| 需要 systemd / 内核模块 / 网络命名空间实验 | **A 路**：WSL2 `openkylin-test`（`systemd=true`） | D 路：远端宿主 systemd | 容器内起 systemd（rootless 不允许） | R-07 |
| 需要长期驻留（天级及以上） | **C 路** + 显式重启策略或宿主 systemd | D 路：宿主服务 | B 路：Podman machine（默认不运行） | R-19 / R-10 |
| 只是临时验证一条命令 | **C 路**：`podman run --rm --network none` | A 路：WSL 一次性命令 | 新建 machine / 重新 import 发行版 | R-10 / R-08 |
| 需要在 Windows 侧看图形桌面 | **A 路**：桌面发行版 + xrdp | — | 远端容器（无 X 服务） | 08 文档 |
| 需要读写 15 TB 共享数据 | **C 路 / D 路**：服务器本地 XFS 直读 | A 路：drvfs 挂载（有缓存与语义损耗） | 在 SMB 上直接跑构建 | R-17 / 2.2 |
| 完全离线、不能拉镜像 | **C 路**：镜像与卷已就位 | — | 任何需要 `pull` 的路径 | 09-3 |
| 需要 root 权限改宿主配置 | **D 路**：远端宿主会话 | — | 容器内提权（rootless 不可能） | 设计前提 |
| 需要在 Windows 桌面上双击运行 Linux 工具 | **A 路** | **B 路** | — | R-01 / R-10 |

### 6.2 下次开工前 5 分钟检查清单

逐条执行，任一条不符先停下来归因，不要「先跑起来再说」。

1. **身份与版本**：`podman --version` → 期望 `5.6.2`；若看到 `3.4.4`，说明走到了 `/usr/bin/podman`（R-11）。
   通过判据：版本正确；失败含义：后续所有体积与行为结论都不可信。
2. **权限模型**：`podman info --format '{{.Host.Security.Rootless}}'` → 期望 `true`。
   失败含义：当前不是 rootless 会话，挂载与 UID 结论全部失效。
3. **存储落点**：`readlink -f /home/ai/.local/share/containers/storage` → 期望 `/media/pc/data/ai/.agents/podman-storage/storage`（R-12）。
   失败含义：软链断了，podman 会看到一个空存储。
4. **余量**：`df -B1 /media/pc/data /` → XFS 可用 ≥ 50 GB、根可用 ≥ 5 GiB（R-17）。
   失败含义：本次构建有把分区写满的风险，先清理或换目标。
5. **能力探测**：`podman container ps --all`、`podman images`、`podman volume inspect npu-build` 三条都要有数据（R-19 / R-13 / R-15）。
   失败含义：容器运行时或存储不可用；注意**不要**用 `podman ps` 或 `podman system df` 作为判据（R-18 / R-22）。
6. **挂载契约**：容器内探针 `stat -c '%a %u'` → `700 1006`，且文件在宿主侧可见。
   失败含义：bind 或 `--userns=keep-id` 未生效，构建产物会写到错误属主。
7. **静态契约**：`bash scripts/audit-image-contract.sh` → `exit=0`、`total=10 pass=10`（带卷 12，R-20）。
   失败含义：镜像内容与规格不符；注意这只证明镜像，不证明环境（V5）。
8. **WSL 侧（仅当本次要用 A 路）**：`wsl -l -v` → Version=2；`fsutil sparse queryflag D:\WSL\openkylin-test\ext4.vhdx` → 已设 sparse（R-01 / R-02）。
   失败含义：发行版状态异常或 VHDX 已失去稀疏属性，磁盘增长会失控。
9. **版本控制基线**：`git status --porcelain` → 仅预期文件；`git rev-list --left-right --count origin/main...HEAD` 与开工前记录一致（M11）。
   失败含义：工作区有其他未预期改动，后续提交可能混入。

### 6.3 本文件状态

- 本文件（Markdown 与同名 HTML）按委托要求**未提交 Git、未 push**；`doc/index.md` 与 09 入口的登记同属工作区改动，同样未提交。
- 未删除、未移动任何既有文件；未触碰 `vendor/awesome-okf`；未改动此前 9 条未推送提交。

## 7. 不确定性与证伪条件

| # | 不确定项 | 现状 | 怎样才能证伪/确认 |
|---|---|---|---|
| U1 | VHDX 写入 1 GiB 后 Δ=0 是否可外推 | 单次观测（R-06） | 连续写入 10 GiB 并分段记录长度；若线性增长则「写入不膨胀」不成立 |
| U2 | `podman ps` 打印帮助的根因 | 两次复现（R-22），未归因 | 在干净 `env -i` 下复跑；若恢复正常则为环境/包装器问题，否则为该构建裁剪 |
| U3 | 历史「13 与 26 GiB」冲突 | 本轮无法复现（V6） | 找到当时的镜像 ID 与命令原文；否则只能按单位混读解释 |
| U4 | 解压后 rootfs 1,182,607,360 B | 前序实测，本轮未复测（R-05） | 重新解压并 `wc -c` |
| U5 | graphroot 43.45 GiB 的下界误差 | 权限拒绝目录数未统计（R-16） | 以 root 或有权限的身份复跑 `du -sb`，差值即误差量级 |
| U6 | 「全远端更省」依赖 D: 余量假设 | 依赖 30.62 GB 这一现场值 | 若 D: 扩容到 TB 级，结论应重新评估（V1） |
| U7 | 审计 10 项与 `verify.sh` 14 项口径不同 | 11 号已披露 | 两套口径不可互相替代，任何「通过率」必须注明口径 |

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [09-2 挂载与 UID 策略](09-2-mounts-uid-storage.md)
- [09-3 工具链供给](09-3-toolchain-provisioning.md)
- [09-5 验收标准与实测证据](09-5-acceptance-and-evidence.md)
- [10 里程碑复盘（WSL → 远程 Podman）](10-milestone-retro-remote-podman.md)
- [11 里程碑复盘（EOL/CRLF 治理与远程连接收口）](11-milestone-retro-eol-and-remote-connection.md)
- [文档站点首页](index.md)
