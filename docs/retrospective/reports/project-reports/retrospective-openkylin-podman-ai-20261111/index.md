---
type: retrospective
title: openKylin + Podman + AI 全面复盘与洞察
date: 2026-11-11
status: final
methodology: seven-concepts (R→F→V→I→E→C)
source: 现场实测（2026-11-11）+ 仓库文件
---

# openKylin + Podman + AI 全面复盘与洞察

覆盖 openKylin/WSL、Podman 存储与 AI 资产三轴，基于 2026-11-11 现场 40 条事实，相对既有三篇复盘新增存储路径、交付等级与证据等级三项内容。

## 0. 范围与增量关系

本报告的三轴范围：

- **openKylin 轴**：Windows 侧 WSL 宿主、WSL 内的发行版与桌面栈、服务器宿主三处现场状态。
- **Podman 轴**：服务器 rootless Podman 的存储布局、卷与镜像清单、命名空间映射、远程连接配置。
- **AI 轴**：SpecWeave 工作区内的规格、复盘、技能、临时主题与 devkit 源码的存量与索引状态。

与既有三篇复盘的关系：三篇同属 `openkylin-wsl-devkit/doc/`，分别记录「WSL→远程 Podman 的里程碑转向」「EOL/CRLF 与远程连接收口」「WSL/Podman/远程主机的三路用法」，均为过程叙事。本报告不复述其过程，只做三件事：其一，把三轴现状重测为统一编号的事实基线（R 段）；其二，把三篇中的结论拆为「保留/降级/推翻」（V 段 C 表）；其三，抽出可迁移的选路方法与证据等级约定（E 段、I4）。

**易变项声明**：容量数值（F-A5、F-A6、F-B3）、镜像与容器清单（F-B9、F-B10）、连接配置（F-B12）、临时主题计数（F-C10）随时间漂移，引用时须注明采集日期 2026-11-11。

**稳定项声明**：文件系统类型与挂载语义（F-A7、F-B5、F-B6）、rootless 用户命名空间映射结构（F-B11）、WSL 导入接口的路径约束（F-A4）、overlay 的语义要求（F-B5）在版本不变的前提下可长期引用。

本报告引用的原结论编号沿用其来源复盘的编号前缀，便于逐条回溯：

| 原结论编号前缀 | 来源复盘 |
|---|---|
| C10-* | 10-milestone-retro-remote-podman（远端 Podman 里程碑） |
| C11-* | 11-milestone-retro-eol-and-remote-connection（EOL 与远程连接收口） |
| C12-* | 12-usage-retro-wsl-podman-remote-host（WSL/Podman/远程主机三路用法） |

三篇均位于 `openkylin-wsl-devkit/doc/`，本报告只引用其结论编号，不复制其正文段落。

## R 复盘：现场事实基线（G1 事实门）

R 段按三轴采集，编号规则为 `F-<轴>-<序号>`：A 轴走 Windows 与 WSL 两条通道，B 轴全部在服务器上取得，C 轴来自仓库文件与本地命令。每条事实只记录观测值、采集通道与可复查的命令或路径，判断留给 F 段与 I 段。

### 表 R-0 三轴与采集通道对照

| 轴 | 采集通道 | 事实条数 |
|---|---|---|
| openKylin | Windows、WSL、服务器 | 12 |
| Podman | 服务器 | 14 |
| AI | 仓库文件、命令 | 14 |

### 表 R-1 openKylin 轴（12 条）

| 编号 | 事实陈述 | 采集通道 | 命令或文件路径 |
|---|---|---|---|
| F-A1 | WSL 发行版清单 1 项：openkylin-test，Stopped，VERSION 2；WSL 3.0.3.0，内核 6.18.54.1-1，WSLg 1.0.79，Windows 10.0.19044.7807 | Windows | `wsl -l -v`、`wsl --version` |
| F-A2 | openkylin-test 的 os-release：NAME="openKylin"，VERSION_ID="3.0"，PRETTY_NAME="openKylin 3.0"，VERSION_CODENAME=huanghe | WSL | `cat /etc/os-release` |
| F-A3 | 内核 6.18.54.1-microsoft-standard-WSL2，架构 x86_64 | WSL | `uname -r`、`uname -m` |
| F-A4 | BasePath=D:\WSL\openkylin-test，ext4.vhdx 体积 1.46 GB，LastWriteTime 2026-11-11 10:47:24 | Windows | 注册表 Lxss、`Get-ChildItem` |
| F-A5 | D: NTFS 112.28 GB，可用 29.08 GB；C: NTFS 119.41 GB，可用 16.53 GB | Windows | `Get-Volume` |
| F-A6 | `/dev/nvme0n1p5` 228G，已用 204G，可用 13G，95%，挂载 `/`；`/dev/sda1` 15T，已用 15T，可用 306G，98%，挂载 `/media/pc/data` | 服务器 | `df -h` |
| F-A7 | sda1 为 xfs，nvme0n1p5 为 ext4 1.0，nvme0n1p2 为 vfat FAT32，挂载 /boot/efi | 服务器 | `lsblk -f` |
| F-A8 | devkit 实际路径 `/media/pc/data/ai/notebook/dev/libs/AI/apps/dev-tools/openkylin-wsl-devkit`；其下无 `knowledge-base/` 目录，该路径 `*.md` 计数 0 | 服务器 | `find` |
| F-A9 | devkit 目录 `*.md` 合计 33 个；`doc/` 顶层 25 个文件，其中 md 20 个、html 3 个（10/11/12），另有 conf.py、requirements.txt | 服务器 | `find`、`ls` |
| F-A10 | openkylin 知识目录为 `docs/knowledge/tech/openkylin`，其下 `*.md` 31 个 | 服务器 | `find` |
| F-A11 | openkylin-test 内 xrdp：`command -v` 无输出、unit 文件不存在、`is-enabled` 为 not-found、`is-active` 为 inactive | WSL | `command -v xrdp`、`systemctl is-enabled/is-active xrdp` |
| F-A12 | openkylin-test 内 `^ii +xrdp` 计数 0、`^ii +ukui` 计数 0；PID 1 为 systemd，`is-system-running` 为 running；`/etc/systemd/system/media-pc-data-ai.mount` 存在（253 字节，11-05 12:11） | WSL | `dpkg -l`、`systemctl is-system-running`、`stat` |

口径说明：本表 12 条事实的采集日期均为 2026-11-11，采集通道见各行；F-A5 为 Windows 侧卷余量，F-A6 为服务器侧余量，两者分别对应各自的构建位置，不可直接相加或互换引用；F-A4 的 vhdx 体积与 F-A5 的 D: 余量为不同量纲对象。

### 表 R-2 Podman 轴（14 条）

| 编号 | 事实陈述 | 采集通道 | 命令或文件路径 |
|---|---|---|---|
| F-B1 | podman 5.6.2，二进制 `/usr/local/bin/podman` | 服务器 | `podman --version`、`command -v podman` |
| F-B2 | graphRoot=`/home/ai/.local/share/containers/storage`，graphDriverName=overlay，volumePath=`/media/pc/data/ai/.agents/podman-storage/storage/volumes`，runRoot=`/run/user/1006/containers`，configFile=`/home/ai/.config/containers/storage.conf`，transientStore=false，databaseBackend=boltdb | 服务器 | `podman info --format '{{json .Store}}'` |
| F-B3 | graphRootAllocated 15,998,762,643,456 B（≈15.9 TB），graphRootUsed 15,670,955,810,816 B（≈15.67 TB） | 服务器 | `podman info --format '{{json .Store}}'` |
| F-B4 | rootless=true；cgroup v2 / cgroupfs / controllers [memory,pids]；`stat -fc %T /sys/fs/cgroup`=cgroup2fs；netavark 1.15.2；crun 1.30.1 | 服务器 | `podman info`、`stat -fc %T /sys/fs/cgroup` |
| F-B5 | graphStatus：Backing Filesystem xfs、Native Overlay Diff true、Supports d_type true、Supports shifting false、Supports volatile true、Using metacopy false | 服务器 | `podman info` |
| F-B6 | `/media/pc/data` 挂载项 `xfs (rw,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota)`；`stat -f` 对两路径返回 type=xfs bsize=4096；`xfs_info` 不存在，ftype 无直接取值，仅有 Supports d_type=true 间接证据 | 服务器 | `mount`、`stat -f`、`command -v xfs_info` |
| F-B7 | `/home/ai/.local/share/containers/storage` 与 `/media/pc/data/ai/podman-storage/storage` 均指向 `/media/pc/data/ai/.agents/podman-storage/storage`；前者为目录软链，后者目录内仅此一个软链条目 | 服务器 | `ls -ld`、`readlink -f` |
| F-B8 | `podman volume ls` 19 个卷：5 个 64 位十六进制匿名卷，命名卷含 agent-monetize-dev_* 3 个、native-dev_* 4 个、xmnn-dev_* 3 个、xmnn-runtime_xmnn-ssh-host-keys、npu-build | 服务器 | `podman volume ls` |
| F-B9 | `podman images` 13 行、按 ID 去重 12 个；`podman info` 的 imageStore.number=58；openKylin 相关标签实存 `localhost/openkylin:3.0`（26 GB）、`:3.0-minimal`（2.37 GB）、`:3.0-minimal-gcc`（1.46 GB）、`localhost/openkylin-npu-toolchain:3.0`（14 GB）、`:3.0-minimal`（2.51 GB）、`:3.0-minimal-r1`（2.51 GB），另有 3 个 `<none>:<none>` | 服务器 | `podman images`、`podman info` |
| F-B10 | `podman ps -a` 5 条：`9514ffe234c3-infra` 为 Created；npu-toolchain-minimal / npu-toolchain / native-dev / agent-monetize-dev 为 `Up 4 days`；containerStore number=5、running=4、stopped=1 | 服务器 | `podman ps -a`、`podman info` |
| F-B11 | `/etc/subuid`、`/etc/subgid` 中 ai 映射均为 `493216:65536`（文件内 14 条用户记录）；`podman unshare cat /proc/self/uid_map` 输出 `0 1006 1`、`1 493216 65536`；宿主 uid=1006 | 服务器 | `cat /etc/subuid`、`podman unshare cat /proc/self/uid_map` |
| F-B12 | `podman system connection ls` 无数据行；`~/.config/containers/podman-connections.json` 为 `{"Connection":{},"Farm":{}}`（28 B）；同目录有 containers.conf(292B)、containers-5.conf(1670B)、containers-5.conf.bak-20261009(1469B)、policy.json、registries.conf、podman/ 子目录 | 服务器 | `podman system connection ls`、`ls -l ~/.config/containers/` |
| F-B13 | `du -x -sh`：`storage/overlay` 39G、`storage/volumes` 7.0G，为下限（100 余子目录 Permission denied）；`du -sh` 软链路径返回 0 | 服务器 | `du -x -sh`、`du -sh` |
| F-B14 | `podman system df` 失败，报 `lstat /run/user/1006/libpod/tmp/infra-container: no such file or directory` | 服务器 | `podman system df` |

口径说明：本表 14 条事实的采集日期均为 2026-11-11，采集通道均为服务器侧；F-B3 的 graphRootAllocated 描述整个底层文件系统的容量，F-B13 的 39G 与 7.0G 描述容器目录的占用，两者不是同一对象；F-B9 的「13 行 / 去重 12 / number 58」是三种统计口径，引用时须写明取哪一种。

### 表 R-3 AI 轴（14 条）

| 编号 | 事实陈述 | 采集通道 | 命令或文件路径 |
|---|---|---|---|
| F-C1 | `.trae/specs` 下 spec 目录 29 个 | 仓库文件 | `find .trae/specs -maxdepth 1 -type d` |
| F-C2 | 命中 openkylin/podman/container/wsl/rtos-usb/python-env 的 8 个：atomize-openkylin-wsl-devkit-doc、deploy-openkylin-wsl-thin-dev、integrate-rtos-usb-python、native-dev-bscheme-podman-sock、python-env-config、retrospect-openkylin-podman-ai、run-npu-toolchain-in-openkylin-podman、validate-containers-openkylin-wsl | 仓库文件 | 目录名匹配 |
| F-C3 | `docs/retrospective/reports` 下分类子目录 22 个，二级报告目录合计 293 个 | 仓库文件 | `find` |
| F-C4 | 其中 4 个分类无二级目录仅平铺文件：exported 19、feature-development 3、adversarial-reviews 3、2026-11-02-support-agent-ui-redesign-assets 5 | 仓库文件 | `find`、`ls` |
| F-C5 | project-reports 下报告目录 19 个 | 仓库文件 | `find` |
| F-C6 | environment-setup 下报告目录 7 个 | 仓库文件 | `find` |
| F-C7 | `.agents/skills` 一级技能目录 9 个 | 仓库文件 | `find` |
| F-C8 | `notebook/dev/libs/AI/.agents/skills` 一级技能目录 223 个 | 仓库文件 | `find` |
| F-C9 | `.agents/docs/workspace-entry` 文件 10 个（00–09） | 仓库文件 | `ls` |
| F-C10 | `.temp` 根层主题目录 41 个；`_index.md` 登记表 50 项 = 常驻治理层 1 + 已封存删源 9 + 现场主题 40；另有未登记目录 tirx-deploy-dist-20261110 | 仓库文件 | `ls`、`cat .temp/_index.md` |
| F-C11 | devkit 一级条目 8 项：apps、doc、src、tests、pyproject.toml、README.md、.pytest_cache、.coverage | 仓库文件 | `ls -a` |
| F-C12 | `src/okw` 顶层 `*.py` 12 个，递归 26 个 | 仓库文件 | `find` |
| F-C13 | devkit 无 `.git`，所属仓库根为 `notebook/dev/libs/AI`，`git status --porcelain` 输出 0 行 | 仓库文件 | `ls -a`、`git rev-parse --show-toplevel`、`git status --porcelain` |
| F-C14 | devkit `doc/` 含 10/11/12 三篇复盘 md 及同名 html，另有 01–09 系列文档 | 仓库文件 | `ls doc/` |

口径说明：本表 14 条事实的采集日期均为 2026-11-11，采集通道为仓库文件与本地命令；F-C1 统计的是 spec 一级目录，F-C3 统计的是报告二级目录，F-C7 与 F-C8 分属两个不同层级的技能目录（前者为工作区 `.agents/skills`，后者为 SpecWeave 子体系内 `.agents/skills`），三组计数不可互相校验。

**G1 事实门判定**：事实条数 40 ≥ 20，且 openKylin（12）、Podman（14）、AI（14）三轴均有覆盖，事实陈述仅描述观测值，未含因果推断。**通过。**

## F 第一性原理：硬约束与当前选择

F 段把 R 段观测值拆成两类：**硬约束**是不随运维偏好改变的技术边界，只能被推翻、不能被绕过；**当前选择**是当前实现方式，可在代价可接受时改动。混淆两者会把「配置没改」误当作「技术上做不到」。

### 表 A 硬约束

| 编号 | 约束 | 判据 | 推翻条件 |
|---|---|---|---|
| F1 | 容器存储的底层语义约束：overlay 需 d_type + xattr + hardlink + flock；XFS（attr2, inode64）满足，网络盘/NTFS/9p 不满足 | F-B5、F-B6 | 换用不依赖 overlay 的驱动（vfs）且能接受体积与性能代价 |
| F2 | rootless 用户命名空间约束：需 subuid/subgid 区间，容器内 uid0 映射宿主 uid1006 | F-B4、F-B11 | 改 rootful 或换 userns 模式 |
| F3 | WSL 导入接口约束：只接受本地固定盘路径（DriveType=3），网络盘（DriveType=4）被拒 | C10-1、F-A4（vhdx 落 D:\WSL） | 改用 `wsl --mount` 或其他虚拟化载体 |
| F4 | 镜像分层体积约束：体积≈基础层+应用层，基础层不可按包拆（tarball 导入）；只放指针则镜像不自包含 | C11-4、F-B9、C12-2 | 改用 apt 源直装重建基础层或改用 OCI 分片交付 |
| F5 | 工具解析约束：按用户名解析 podman 会得到不同版本（写死 /usr/bin/podman 会降级到 3.4.4） | C12-4、F-B1（/usr/local/bin） | 统一 PATH 与封装脚本 |
| F6 | 容量约束：`/` 可用 13G、`/media/pc/data` 可用 306G、C: 16.53G、D: 29.08G（时点量，2026-11-11） | F-A5、F-A6 | 扩容或清理后重新测量 |

### 表 B 当前选择（可改，非约束）

| 编号 | 现状 | 可改空间 | 改动代价 |
|---|---|---|---|
| S1 | graphRoot 经符号链接落到 XFS（F-B7） | 改为单一实路径或换成独立数据盘 | 需迁移 46G 下限数据，迁移期间 Podman 停机 |
| S2 | volumePath 与 graphRoot 分列两处（F-B2） | 收敛到 graphRoot 下的默认位置 | 需搬迁卷数据并改 storage.conf，`du` 才能一次量全 |
| S3 | databaseBackend=boltdb、cgroupfs（F-B2、F-B4） | 换 sqlite、换 systemd cgroup 驱动 | 需重建容器状态，容器需重启 |
| S4 | 远程接入未配置，connection 为空（F-B12） | 配置 `podman system connection add` 或 SSH 直连 | 低，属新增配置，无存量迁移 |
| S5 | openkylin-test 未装桌面与 xrdp（F-A11、F-A12） | 按 devkit `desktop install` 补齐桌面栈 | 中，受 WSL 与源可用性限制，且需 `--yes` 确认 |

### 表 C 新方案选路表

| 场景 | 推荐路径 | 必查项 |
|---|---|---|
| 容器存储落盘 | 直接放在 XFS 挂载点下的单一实路径，不用软链拼接 | F-B5 d_type 为 true、F-B6 挂载含 attr2/inode64、目标挂载余量大于镜像总量两倍 |
| 镜像构建主机选择 | 优先在 `/media/pc/data`（余 306G）一侧构建，`/` 侧只放运行时空壳 | F-A6 两处余量、F-B13 现有占用、构建所需基础层体积 |
| WSL 发行版导入位置 | 落本地固定盘（D:\WSL），不落网络盘 | F-A4 BasePath 的 DriveType、F-A5 对应盘余量 |
| 工具链镜像交付方式 | 先声明等级：L0 指针（依赖宿主挂载）、L1 自包含（实体入层）、L2 离线包（tar + 校验） | F-B9 镜像体积与层结构、C12-2 层内实体清单、接收方是否存在 `/media/pc/data` |
| 远程 podman 接入 | SSH 直连 + 远程 `podman` 全路径，不依赖 connection 配置 | F-B12 connection 是否为空、F-B1 二进制路径、F5 版本一致性 |

## V 对抗审查（V 门）

V 段对 R 段与 F 段的结论做反向质询。每一条意见都必须能落到某个事实编号或原结论编号上，不接受无法复查的泛泛质疑；C 表则把三篇既有复盘的结论逐条判定为保留、降级或推翻。

### 魔鬼代言人

> **V1（魔鬼代言人）**：F-B3 的 graphRootAllocated 15.9 TB 与 F-A6 的 sda1 15T 总量并列出现，若据此宣称「容器占用 15.9 TB」，核算的是整个文件系统而非容器数据；必须与 F-B13 的 39G+7.0G 下限同时呈现，否则结论放大两个数量级。

> **V2（魔鬼代言人）**：F-B9 同时给出 `podman images` 去重 12、imageStore.number=58、`podman ps -a` 5 条容器与 19 个卷，任何一个「镜像/容器数量」的单值表述都可被另一口径反驳；报告若不给口径定义，读者必然误判（对应行动 A3）。

### 新人视角

> **V3（新人视角）**：F-A8 显示 devkit 下不存在 `knowledge-base/`，F-A10 显示知识与在 `docs/knowledge/tech/openkylin`；若沿用旧文档给出的相对路径找知识库，新人第一次检索即落空，路径事实应写在首次出现处而非放在附注。

### 老板视角

> **V4（老板视角）**：按 F-A6，`/` 仅余 13G、`/media/pc/data` 余 306G，而 F-B13 的 46G 只是下限；在完整占用数字出来之前，任何「扩容」或「清理已完成」的汇报都不成立，应被 A1 的 census 阻断。

> **V5（老板视角）**：F-B10 有 4 个容器 Up 4 days，F-B14 的 `podman system df` 直接失败；资源账不闭合时，「这些容器占多少、能否下线」在管理层面无答案，属于可观测性缺口而非使用问题。

### 未来视角

> **V6（未来视角）**：F-C10 记载 41 个根层主题、40 个现场主题与 1 个未登记目录；若半年内仍无退役与索引机制，本报告 C 表中「保留」类结论将继续静默过期，重演 C10 被 F-C13 推翻的情形。

### 对既有复盘的证伪检查

| 原结论编号 | 分类 | 理由 | 补证方式 |
|---|---|---|---|
| C10-1「网络盘 DriveType=4 不可 wsl --import」 | 保留 | 有实测依据 | 仅测 SMB 一种，需补 iSCSI/本地 NTFS 对照 |
| C10「doc/*.md 未跟踪」 | 推翻 | 本次 `git status --porcelain` 为 0 行（F-C13） | 无需补证 |
| C10-3「libtvm.so 链接 LLVM 21 而门禁 22，import 成功属假通过」 | 保留 | 版本错配可复现 | 补 ldd 与版本门禁的自动化断言 |
| C11-4「14 GB 镜像中 13 GB 为单层」 | 保留（限 tarball 导入场景） | 与 F-B9 的 14 GB 标签一致 | 用 apt 直装重建后复测 |
| C11-5「全仓 3,275 个 CRLF 文件」 | 降级 | 单点快照、无对照组、随提交漂移 | 纳入月度快照并给区间 |
| C12-2「镜像层零 tvm/xmnn 实体、仅 .pth 指针，故不能独立交付」 | 保留 | 与 F-B9 的 26 GB 标签并列成立 | 给出交付等级声明（A4） |
| C12-5「podman system df 报 infra-container 缺失」 | 保留 | 本次再复现（F-B14） | 登记为已知缺陷（A2） |
| C12-1「构建放远端判据是 D: 30.62 GB vs XFS 293.28 GiB」 | 降级为时点判断 | 本次 D: 可用 29.08 GB、XFS 可 306G（F-A5、F-A6），量值已变 | 每次决策前重新测量 |

**V 门判定**：魔鬼代言人、新人、老板、未来四视角全覆盖；意见 6 条 ≥ 5 条；每条均指向事实编号（F-*）或原结论编号（C*）。**通过。**

## I 洞察（G2 洞察门）

I 段是本报告唯一允许展开因果推理的部分。四条洞察按统一四元组书写：现象只引用 R 段编号，根因给出机制解释，影响说明代价发生在哪一步，建议落到 C 段的具体行动。

### I1 容器存储三路径分裂

**现象描述**：F-B2 的 graphRoot 为家目录路径，F-B7 显示该路径实为软链、真实数据在 `/media/pc/data/ai/.agents/podman-storage/storage`，同时 volumePath 单独指向同一物理目录的 volumes 子项；F-B13 的 `du` 只得 46G 下限且 `du -sh` 软链路径返回 0；F-B14 的 `podman system df` 直接失败。

**根因分析**：容量压力下用软链把 graphRoot 迁到数据盘，volumePath 又按配置单独指定，两条路径在配置层分裂为三个可见入口，物理位置不唯一；`podman system df` 依赖 runRoot 下的临时条目，该条目缺失时整条统计链路中断。

**影响评估**：容量核算只能得到下限，清理无法验证是否清干净，镜像与卷的真实占用不可回答；F-B3 的 15.9 TB 更易被误读为容器占用。

**改进建议**：执行 A1，把容器存储收敛为单一物理路径并做一次完整 census。

### I2 能力与交付边界倒挂（跨 Podman × AI）

**现象描述**：F-B9 显示 `localhost/openkylin:3.0` 达 26 GB、`openkylin-npu-toolchain:3.0` 达 14 GB；C12-2 显示镜像层内零 tvm/xmnn 实体、仅 .pth 指针；C11-4 显示 14 GB 中 13 GB 为单层基础层。

**根因分析**：为绕开镜像体积与构建时长，把工具链实体外置到宿主挂载目录，镜像内只保留指针；指针在构建机上有效，在交付对象处失效。

**影响评估**：镜像不具备离线交付能力，环境恢复依赖 `/media/pc/data` 存在且内容未变；体积与能力呈反向关系——镜像越大，可迁移的能力反而越少。

**改进建议**：执行 A4，在 `doc/05-openkylin-dev-container.md` 建立 L0/L1/L2 交付等级声明，对 6 个实存标签逐一给级。

### I3 资产密度与管理带宽不匹配（跨 AI × openKylin）

**现象描述**：F-C3 的二级报告目录 293 个、F-C8 的技能目录 223 个、F-C10 的根层主题 41 个与未登记目录 1 个、F-A10 的知识文档 31 篇，同处一个工作区。

**根因分析**：报告、技能与临时主题的产出速度快于索引维护与退役机制，登记表与实际目录各自增长，缺少「过期即标记」的触发点。

**影响评估**：检索成本随存量线性上升；旧结论（如 C10 的未跟踪判断）在无复核触发条件时静默过期，并与现场事实冲突。

**改进建议**：执行 A5 为既有复盘补证据等级与复核触发条件，A6 以只读快照脚本固化现场事实，降低人工核对带宽。

### I4 验证强度不均（跨三轴）

**现象描述**：11 号复盘有反事实对照组（C11-1、C11-2），10 号与 12 号多为单点实测（C10-1、C12-5）；三者均以「已验证」表述结论。

**根因分析**：缺少统一的证据等级约定，验证手段随当时条件变化，而表述口径未随手段分层。

**影响评估**：同样标注「已验证」的结论可靠性不等，读者无法按表述判断该结论是否可独立复现。

**改进建议**：执行 A5，引入证据等级约定——**E0** 文档推断（无实测）、**E1** 单点实测（一次观测，无对照）、**E2** 对照实测（有反事实或双通道比对）、**E3** 可重复脚本化（一条命令可复现并产出可 diff 结果），要求每条结论标注等级。

**G2 洞察门判定**：洞察 4 条 ≥ 3 条；其中跨轴洞察 I2（Podman × AI）、I3（AI × openKylin）、I4（三轴）共 3 条 ≥ 2 条。**通过。**

## E 模式萃取（G3 模式门）

E 段把本次的判断过程压缩为可复用方法。六步法是正向路径，反模式清单是负向清单，跨场景迁移说明哪些步骤可原样搬运、哪些需要重测判据。

### 模式：环境选路六步法

1. **存量盘点**：采集容量、文件系统、挂载类型、网络盘边界；产出是一张带编号的事实表（对标 R 段表 R-1/R-2）。
2. **硬约束过滤**：按 overlay 语义、userns 映射、导入接口、分层体积四类约束排除不可行路径；产出是被排除路径清单及其判据编号。
3. **交付等级声明**：先确定 L0 指针 / L1 自包含 / L2 离线包；产出是一句可验收的交付口径，避免后续对「可用」各说各话。
4. **单点实测加反事实对照**：至少补一条反向对照实验；产出是「真通过 / 假通过」的区分结论（对标 C10-3 的 LLVM 版本错配）。
5. **容量与可清理性核算**：路径唯一化，确保一条 `du` 或 `df` 能量全；产出是可复核的占用数字与清理边界。
6. **结论登记时间戳与复核触发条件**：每条结论附采集日期与失效条件；产出是可被下一次复盘直接比对的基线。

适用边界：六步法面向「在一台主机上把容器环境落位并交付」这一类问题；纯应用层调试、纯代码重构不适用，后者只需单点实测与回归即可。

### 反模式清单

- **P1 在网络盘/SMB 放容器存储或 VHDX**：触发场景是为省本地盘空间把 graphRoot 或 vhdx 指到共享盘；后果是 overlay 语义不满足或 `wsl --import` 被拒，环境起不来。
- **P2 用软链拼存储后依赖 `du` 报数**：触发场景是迁移后沿用原路径；后果是 `du` 返回 0 或拒绝跨设备统计，容量结论不可信（F-B13）。
- **P3 把 import/启动成功当可用**：触发场景是以「容器起来了、import 无报错」作为验收；后果是掩盖版本错配型假通过（C10-3）。
- **P4 只做单点实测就标注「已验证」**：触发场景是时间紧只跑一次；后果是结论等级失真，后续被单点反例推翻（C11-5）。
- **P5 在根分区余量 <20 G 的主机上做多层镜像构建**：触发场景是沿用默认工作目录；后果是构建中途失败或写满系统盘（F-A6 的 13G）。

### 跨场景迁移

- **异构 Linux 主机**：六步法不变，仅替换 F1/F2 的判据取值——重测 `podman info` 的 graphStatus 与 subuid/subgid 区间，其余步骤照用。
- **其他容器引擎**：Docker 的 `data-root` 与本例的 graphRoot 属同类问题，P1/P2/P5 同样适用，只需把判据命令换成 `docker info`。
- **其他发行版 WSL**：导入位置约束（F3）与桌面栈 Install 判据（S5）可直接复用，发行版差异只影响包名与源地址。

**G3 模式门判定**：环境选路六步法 6 步完整且每步含「做什么/产出」；反模式 5 条均含触发场景与后果；跨场景迁移 3 条。**通过。**

## C 原子化行动（G4 行动门）

行动按「先量全、再修表、后清理」排序：A1 先给出可信容量，A2 修复统计入口，A3 处理悬空镜像，A4 与 A5 只动文档，A6 依赖 A1、A2 落地后固化快照。A4、A5、A6 可并行推进。

| 编号 | 行动（单一职责） | Owner | 验收标准（可一条命令判定） | 依赖/可并行 | 是否需人类批准 |
|---|---|---|---|---|---|
| A1 | 统一容器存储为单一物理路径并做容量 census | 环境维护者 | 对唯一路径执行 `du -sx` 得完整数值且无 Permission denied；`podman info` 的 graphRoot/volumePath 位于同一挂载点 | 无 | 是 |
| A2 | 修复或正式登记 `podman system df` 的 infra-container 缺失 | Podman 维护者 | `podman system df` 返回 rc=0，或缺陷登记条目存在且被引用 | 依赖 A1 | 是 |
| A3 | 清理 `<none>` 悬空镜像并核对 imageStore.number(58) 与 `podman images` 去重(12) 的口径差异 | Podman 维护者 | 两处计数一致，或差异有书面解释并落文档 | 无 | 是（含删除） |
| A4 | 为 openKylin 交付物建立 L0/L1/L2 交付等级声明并写入 `doc/05-openkylin-dev-container.md` | 文档维护者 | 该文档含判定表且对 6 个实存标签各给出等级 | 无 | 否 |
| A5 | 给三篇既有复盘补「证据等级（E0–E3）+ 复核触发条件」栏 | 复盘维护者 | 三篇各 ≥1 处标注，且与本报告 C 表结论一致 | 无 | 否 |
| A6 | 建立只读环境事实快照脚本（df/Get-Volume、podman info、镜像清单） | 环境维护者 | 单条命令产出可 diff 的 markdown 表，连跑两次无报错 | 依赖 A1、A2 | 否 |

**G4 行动门判定**：行动 6 项，每项单一职责、含 Owner 与可一条命令判定的验收标准，依赖关系标注完整。**通过。**

A1/A3 涉及配置变更与删除，须人类批准后方可执行。

反模式 P1–P5 的逐条整改步骤（识别信号、修复命令、防复发门禁、验收判据、责任与回滚）见[反模式 P1–P5 整改方案](actionable-items.md)。

## 质量门通过记录

各门的判定依据均可在正文中找到对应编号；表中「实测值」列取自本报告自身的计数，不作外部引用。判定口径为「标准满足即通过」，不设加权评分，避免用分数掩盖某一门的缺失。

| 门 | 标准 | 实测值 | 结论 |
|---|---|---|---|
| G1 事实门 | 事实 ≥20 条且三轴覆盖 | 40 条（openKylin 12 / Podman 14 / AI 14） | 通过 |
| V 门 | 四视角全覆盖、意见 ≥5 条 | 4 视角 / 6 条 / C 表 8 行 | 通过 |
| G2 洞察门 | 洞察 ≥3 条，跨轴 ≥2 条 | 4 条 / 跨轴 3 条 | 通过 |
| G3 模式门 | 模式步骤完整、反模式 ≥3、迁移 ≥2 | 6 步 / 5 条反模式 / 3 条迁移 | 通过 |
| G4 行动门 | 每项含 Owner 与可判定验收 | 6 项 / 6 项具备 | 通过 |

## 参考

以下路径均相对本报告目录书写，可直接在仓库内解析。

- [10-milestone-retro-remote-podman.md](../../../../../apps/dev-tools/openkylin-wsl-devkit/doc/10-milestone-retro-remote-podman.md)
- [11-milestone-retro-eol-and-remote-connection.md](../../../../../apps/dev-tools/openkylin-wsl-devkit/doc/11-milestone-retro-eol-and-remote-connection.md)
- [12-usage-retro-wsl-podman-remote-host.md](../../../../../apps/dev-tools/openkylin-wsl-devkit/doc/12-usage-retro-wsl-podman-remote-host.md)
- [openKylin WSL 开发工具包文档索引](../../../../../apps/dev-tools/openkylin-wsl-devkit/doc/index.md)
- [Project Reports 索引](../index.md)

```{toctree}
:maxdepth: 1
:hidden:

actionable-items
```