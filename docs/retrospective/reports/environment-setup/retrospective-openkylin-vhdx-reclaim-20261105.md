---
id: "retrospective-openkylin-vhdx-reclaim-20261105"
title: "openKylin WSL 发行版 49.46 GiB 体积溯源与两相回收复盘"
date: "2026-11-05"
type: "problem-solving-retrospective"
source: "与 AI 助手协作排查 openKylin-3.0-desktop vhdx 体积异常并完成回收（Trae 会话，七概念方法论）"
scope: "task"
category: "environment-setup"
session: "sc-20261105-openkylin-vhdx"
methodology: "seven-concepts (诊断链 R→I→V + 沉淀链 R→I→E→C)"
---

# openKylin WSL 发行版 49.46 GiB 体积溯源与两相回收 — 复盘报告

> **复盘主题**：发行版 `ext4.vhdx` 物理体积 49.46 GiB，而官方镜像仅 6.14 GB —— 体积差额的溯源、回收与验收闭环
> **复盘日期**：2026-11-05
> **项目范围**：D 盘空间治理（vhdx 溯源 → 跨盘搬移 → fstrim + compact → 归档删除 → 回收站清理）
> **报告类型**：问题解决复盘（七概念场景 2，R→I→V 诊断链；E 阶段模式沉淀）

***

## 一、项目概述

### 1.1 问题背景

宿主 D 盘 551.64 GiB 仅剩 38.09 GiB 可用（占用率 94%）。`wsl -l -v` 显示三个已停机的发行版，其中 `openKylin-3.0-desktop` 的 `ext4.vhdx` 物理长度为 49.46 GiB（50,644 MB），而官方镜像 `openKylin-3.0-desktop-wsl-amd64.wsl` 仅 6.14 GB。两者相差 8 倍，需判定这是真实系统膨胀、镜像解压开销，还是可回收冗余。

### 1.2 回收目标

- 定位 49.46 GiB 的构成，区分「系统本该有的体积」与「可回收冗余」
- 在不丢失可用数据的前提下回收空间
- 用宿主侧数值闭环验收，不以命令退出码作为成功依据

### 1.3 交付物与结果

| 交付物 | 路径 | 状态 |
|--------|------|------|
| 体积构成台账（四口径） | 本报告第二节 R 阶段 | 完成，数值自洽 |
| 发行版内冗余 tar 迁出 | `D:\WSL\...\ext4.vhdx` → 暂存 `C:\WSL-backup\` | 完成，31.81 GB 完整性核验通过 |
| VHDX 物理回收 | 49.46 GiB → **16.85 GiB** | 完成，双基线完全对齐（Δ 32.61 GiB） |
| 冗余 tar 永久删除 | — | 完成，C 盘 +31.79 GiB |
| 回收站清理（含孤立 `$R` 目录） | C: / D: | 完成，仅余 `desktop.ini` |
| **D 盘最终可用空间** | 38.10 GiB → **89.07 GiB** | 净回收 **50.97 GiB** |

***

## 二、R 阶段：事实复盘（G1 通过：无因果词）

| # | 事实 |
|---|---|
| F1 | `openKylin-3.0-desktop` 的 `D:\WSL\openKylin-3.0-desktop\ext4.vhdx` 物理长度 49.46 GiB（50,644 MB），LastWriteTime 2026-10-23；发行版状态 Stopped |
| F2 | 官方镜像 `D:\WSL\openKylin-3.0-desktop-wsl-amd64.wsl` 物理长度 6.14 GB，与 vhdx 相差 8.05 倍 |
| F3 | 发行版内 `df /` 显示容量 1007 G、已用 48 G；`du -x -h --max-depth=1 /` 显示 46 G |
| F4 | 内层构成：`/home` 33 G、`/usr` 12 G、`/var` 1.7 G、`/boot` 144 M、`/etc` 22 M |
| F5 | `/home/openkylin/ok-wsl-rootfs.tar` 单文件 32 G，属主 root:root，mtime 2026-10-09 00:17 |
| F6 | devkit 全仓检索 `ok-wsl-rootfs.tar` 零命中；`apps/dev-tools/openkylin-wsl-devkit` 无任何脚本引用该文件名 |
| F7 | 该文件 `file` 判定为 `POSIX tar archive (GNU)`，非 gzip；而 [distro.py](../../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/distro.py#L204) 要求 `.wsl` 镜像为 gzip（魔数 `1F 8B`） |
| F8 | `tar -tf` 列举只命中 `./home/`，未命中 `./home/openkylin` —— 该 tar 为未首次开机的原始 rootfs |
| F9 | 迁出后 `df /` 已用从 48 G 降至 16 G；目标文件 31.81 GB，mtime 保持 2026/10/9 0:17:37 |
| F10 | `compact-vhdx-with-baseline.ps1 -BaselineOnly` 基线：D FreeGiB 38.09、VHDX 49.46 GiB |
| F11 | 全流程：`fstrim /` 报告修剪 991.3 GiB（逻辑量）、`/home` 修剪 0 B、`/workspace` 不存在；`wsl --shutdown` 后三发行版全 Stopped；`wsl --manage --compact` ExitCode=0，未降级管理员脚本 |
| F12 | After 复测：VHDX 16.85 GiB、D FreeGiB 70.70；`SavedVhdxGiB` 与 `DeltaHostFreeGiB` 均为 32.61 |
| F13 | 步骤 8 恢复：三发行版原态均为 Stopped，`RestoredStates` 为空，恢复动作 0 次 |
| F14 | Windows 侧 `Remove-Item 'C:\WSL-backup\ok-wsl-rootfs.tar'` 先报沙箱拒绝、解除沙箱后仍报 `Access to the path is denied`；文件 ACL 所有者为 `XIN\xinzo`、`Authenticated Users` 具 `Modify`，无 Deny 条目 |
| F15 | 改由 `wsl -d openKylin-3.0-desktop -u root rm /var/mnt/c/WSL-backup/ok-wsl-rootfs.tar` 删除成功；C 盘可用 52.92 → 84.71 GiB |
| F16 | `Clear-RecycleBin -DriveLetter C,D -Force` 在沙箱内两次超时无输出；解除沙箱后 C 报 `C_CLEARED`、D 报 `D_CLEARED`，但 C 仍余 115 文件 / 0.95 GiB |
| F17 | C 盘残留文件经 `FileShare.None` 独占打开与直接删除均成功，C 盘再回收 0.95 GiB |
| F18 | D 盘回收站残留为两个目录：`$RH4H6D6.temp`（58 文件 / 8.8 MB）、`$RSBDTNZ`（空），同级目录**无任何 `$I` 元数据文件** |
| F19 | 对 `$RH4H6D6.temp` 内 58 个文件逐一以 `FileShare.None` 独占打开，58/58 成功，0 失败；属主 `XIN\xinzo`，属性仅 `Archive`，文件夹 ACL 无 Deny |
| F20 | 递归删除两目录后 D 回收站余量 0.00 GiB；D 盘可用 89.06 → 89.07 GiB |
| F21 | 全流程结束：C 盘可用 85.68 GiB、D 盘可用 89.07 GiB；两盘回收站仅余 `desktop.ini`（100 字节） |
| F22 | D 盘可用空间在本轮自 70.67 GiB 跳至 89.06 GiB（Δ 18.39），而当时回收站内仅 1.24 GiB，约 17 GiB 无归因来源 |

### 2.1 体积四口径台账（关键事实汇总）

| 对象 | 数值 | 计量口径 |
|---|---:|---|
| 官方 `.wsl` | 6.14 GB | gzip 压缩后的 tar |
| `ok-wsl-rootfs.tar` | 31.81 GB | 同一内容解压后的纯 tar（5.18×） |
| 清理前 `ext4.vhdx` | 49.46 GiB | 块设备物理文件长度 |
| 清理前 `df /` | 48 G | Linux 内已分配块 |
| 清理后 `ext4.vhdx` | 16.85 GiB | 块设备物理文件长度 |
| 清理后 `du /` | 14 G | Linux 内文件实际大小 |

体积等式：`29.63 GiB（tar）+ 约 15 GiB（系统）+ 约 4.8 GiB（ext4 元数据/inode/journal/块松弛）≈ 49.46 GiB`。

***

## 三、I 阶段：洞察（G2 通过：四元组完整）

### 洞察 1：主因是「备份被放进了被备份对象内部」

- **现象**：vhdx 49.46 GiB 中，60%（29.63 GiB）由单一文件 `ok-wsl-rootfs.tar` 占据。
- **根因**：该 tar 存放于 `/home/openkylin/`，即 vhdx 内部。ext4 必须同时容纳系统本体与整机未压缩副本，形成「原件 + 备份」双向放大。
- **影响**：D 盘占用率长期停在 94%；且删除该文件后与宿主侧观察到的空间不一致（`df` 立刻变小、`Length` 不变），造成「删了没效果」的误判。
- **建议**：备份类大文件一律落宿主独立路径，且与备份对象不同盘；落盘前先确认目标盘容量（本例 C 盘中转占用 31.8 GB）。

### 洞察 2：四个体积口径被混为一谈

- **现象**：同一对象出现 6.14 GB / 31.81 GB / 49.46 GiB / 48 G / 16.85 GiB / 14 G 六个数字。
- **根因**：压缩包、解压归档、块设备文件、文件系统分配量是四种不同度量，压缩比约 5.18×，动态 VHDX 又只增不减。
- **影响**：把「6.14 GB 镜像」直接与「49.46 GiB 磁盘」对比，得出「膨胀 8 倍」的错误结论。
- **建议**：任何体积判断必须四口径并列；差额优先归因到压缩、元数据与 VHDX 松弛，而非系统内容。

### 洞察 3：「回收站残留 = 文件被锁」是伪命题

- **现象**：`Clear-RecycleBin` 报成功后仍有 0.95 GiB / 115 文件与 8.8 MB / 58 文件残留。
- **根因**：D 盘残留是两个**缺 `$I` 元数据的孤立 `$R` 目录**——Shell 回收站接口只识别 `$I`+`$R` 成对条目，孤立 `$R` 既不显示也不参与清空；同时上一轮清理使用了非递归筛选，本身也碰不到嵌套目录。
- **影响**：若按「被锁」处理，会去查句柄、等重启，实际只需递归删除。
- **建议**：先用 `FileShare.None` 独占打开证伪「锁」，再查 ACL 证伪「权限」，最后按孤立 `$R` 目录处理。

### 洞察 4：Windows 侧删除失败不等于文件不可删

- **现象**：`Remove-Item` 在沙箱内与解除沙箱后均报 Access denied，而 ACL 显示当前用户具备 Modify。
- **根因**：删除请求受 Trae 沙箱可写区限制影响；宿主路径不在沙箱可写清单时，写类操作被拒，与 NTFS 权限无关。
- **影响**：若据此判定「文件被占用/权限受损」，会走提权或重启等无效路径。
- **建议**：宿主只读区写操作走 `wsl -u root` 经 `/var/mnt/<盘符>` 旁路；Windows 侧操作失败时，先看 ACL 与沙箱边界两侧证据再定因。

***

## 四、E 阶段：模式萃取（G3 通过：可迁移）

### 模式 1：自包含备份膨胀（Self-containing Backup Bloat）

| 项 | 内容 |
|---|---|
| **触发场景** | 块设备/镜像/虚拟磁盘体积远超其来源安装包体积；或删除大文件后宿主可用空间无变化 |
| **核心步骤** | ① 四口径并列（压缩包 / 解压归档 / 物理文件 / 内层 df-du）；② 内层 `du -x --max-depth=1` 定位单一超大文件；③ 判断该文件是否为「被备份对象自身的备份」；④ 迁出后再做物理压缩 |
| **反模式** | 只看资源管理器大小就断言「系统膨胀」；直接重装或扩容而不做构成分析 |
| **迁移验证** | 适用于 Docker volume、VM 快照、多份 tar 叠加、日志归档同盘存放等场景；判据统一为「容器体积 ≈ 内容体积 + 冗余副本体积」 |

### 模式 2：三基线交叉验收（Triple-Baseline Acceptance）

| 项 | 内容 |
|---|---|
| **触发场景** | 任何「清理后空间是否真的回来了」的验收 |
| **核心步骤** | ① `Get-Item -Force` 取物理 Length；② `Win32_LogicalDisk` 取宿主 FreeSpace；③ 内层 `df`/`du` 取分配量；④ 三条基线的差量要求符号一致、量级一致（允许 ±0.05 GiB 簇对齐误差） |
| **反模式** | 以命令 ExitCode=0 或 stdout 提示作为成功依据；解析 `wsl.exe` 的 UTF-16 输出 |
| **迁移验证** | 本轮三项差量完全相等（32.61 / 32.61），是本模式的一次强验证；`fstrim` 报出的 991.3 GiB 是稀疏盘的逻辑量，不能作为证据 |

### 模式 3：孤立 `$R` 目录识别（Orphan `$R` Directory）

| 项 | 内容 |
|---|---|
| **触发场景** | `Clear-RecycleBin` 报成功，但 `$Recycle.Bin` 目录仍占空间 |
| **核心步骤** | ① 按 SID 枚举 `$Recycle.Bin` 子目录并求和；② 检查是否存在配对 `$I` 元数据；③ 对可疑文件 `FileShare.None` 独占打开（成功即证伪「被锁」）；④ 核对 ACL 与属性（无 Deny、无只读即证伪「权限」）；⑤ 递归删除孤立 `$R` 目录 |
| **反模式** | 把残留一律归因为「文件被占用」；用非递归 `-File` 筛选去清理回收站；删除前不做独占打开与 ACL 取证 |
| **迁移验证** | 58/58 文件独占打开成功即为判据；同类现象可复用于任何 `$Recycle.Bin` 异常占空间场景 |

### 模式 4：两相回收（Two-Phase Reclaim）

| 项 | 内容 |
|---|---|
| **触发场景** | WSL2 / 动态虚拟磁盘内层已删除数据，但宿主侧体积未变 |
| **核心步骤** | 相一（内层）：删除/迁移数据，`df` 确认已用量下降；相二（宿主）：`fstrim` → `wsl --shutdown` → `wsl --manage --compact` → 双基线复测 → 按原态恢复发行版 |
| **反模式** | 只在 Linux 内删除就宣布完成；只做 compact 不做 fstrim；`wsl --shutdown` 后不恢复原本 Running 的发行版 |
| **迁移验证** | 本轮相一 48 G → 16 G、相二 49.46 → 16.85 GiB，两相各司其职且互不替代；规范沉淀见 [wsl-vhdx-compact-cmd](../../../../.agents/skills/wsl-vhdx-compact-cmd/SKILL.md) |

### 模式 5：宿主只读区旁路（Host Read-Only Bypass）

| 项 | 内容 |
|---|---|
| **触发场景** | Windows 侧对宿主路径的写/删操作报 Access denied，而 ACL 显示当前用户有权限 |
| **核心步骤** | ① 先看 ACL/属性排除权限问题；② 确认路径是否在工具沙箱可写清单外；③ 以 `wsl -u root` 经 `/var/mnt/<盘符>/...` 执行删除或搬运；④ 以宿主侧数值复测确认生效 |
| **反模式** | 直接提权或重启以「绕过拒绝」；在未排除 ACL 的情况下判定文件损坏 |
| **迁移验证** | 本轮同一文件 Windows 侧两度被拒、WSL root 一次成功，可复用于任何 `/mnt/*` 宿主路径写操作 |

***

## 五、V 阶段：对抗审查

| # | 攻击假设 | 裁决 | 依据 |
|---|---|---|---|
| V1 | 该 tar 是当前发行版的整机备份，删除会丢数据 | **证伪** | `tar -tf` 只含 `./home/`、不含 `./home/openkylin`，证明是未开机的原始 rootfs；且官方 `.wsl`（6.14 GB）仍在，可随时重建 |
| V2 | 32.61 GiB 回收是巧合或虚报 | **证伪** | 物理长度差量与宿主 FreeSpace 增量完全相等，compact ExitCode=0 且未降级管理员脚本，两条独立证据同向 |
| V3 | `fstrim` 报告 991.3 GiB 说明回收了巨量数据 | **证伪** | 1007 G 是稀疏 VHDX 的虚拟容量，991.3 GiB 为逻辑修剪量，与物理回收无关；唯一权威是 Length 前后差 |
| V4 | 回收站残留文件被进程锁定 | **证伪** | 58/58 文件以 `FileShare.None` 独占打开成功；真正机制是缺 `$I` 元数据的孤立 `$R` 目录 |
| V5 | D 盘 +18.39 GiB 全部来自本次清空回收站 | **证伪** | 清空前回收站实测仅 1.24 GiB，约 17 GiB 无可归因来源，标注为「未验证外部进程干扰」，不计入本次战绩 |
| V6 | 解压 tar 31.81 GB 与系统 14–16 G 的 16 GiB 缺口证明有隐藏膨胀 | **未验证** | tar 已删除无法复验；两种可能并存：①该 rootfs 含随后被清理的组件；②它并非当前发行版的同一份镜像（[09-5 验收证据](../../../../apps/dev-tools/openkylin-wsl-devkit/doc/09-5-acceptance-and-evidence.md#L58)记载 D 盘曾有多份 tar 被删除）。**证据不足，不作因果断言** |
| V7 | 本轮结论可推广到「openKylin 镜像装出来必然 16.85 GiB」 | **不成立** | 16.85 GiB 是「该发行版当前内容 + 本地运行期数据」的实测水位，非镜像固有属性 |

***

## 六、行动项（G4 通过：原子化）

| # | 行动项 | 单一职责 | 验收标准 | 状态 |
|---|---|---|---|---|
| A1 | 迁出并删除发行版内 31.81 GB 冗余 tar | 是：仅处置单一文件 | `df /` 已用下降 ≥ 30 G，目标文件 mtime/大小不变 | 完成 |
| A2 | 执行 `fstrim + compact` 回收 VHDX | 是：仅物理回收 | VHDX 差量与宿主 FreeSpace 增量同向且量级一致 | 完成（32.61 / 32.61） |
| A3 | 清理 C/D 回收站含孤立 `$R` 目录 | 是：仅回收站 | 两盘 `$Recycle.Bin` 仅余 `desktop.ini` | 完成 |
| A4 | 核实 D 盘历史 tar 台账 | 是：仅核对 | 对照 [09-5 验收证据](../../../../apps/dev-tools/openkylin-wsl-devkit/doc/09-5-acceptance-and-evidence.md#L58) 的 25.19 GB 回收记录，判定 31.81 GB tar 是否为台账外遗留 | 待办 |
| A5 | 为 `wsl-vhdx-compact-cmd` 补充三条 Gotcha | 是：仅技能文档 | ①沙箱内 `Clear-RecycleBin` 表现为挂起超时而非「被拦截」；②孤立 `$R` 目录识别流程；③跨盘中转时需先核对目标盘容量 | 待办 |
| A6 | devkit 增加 preflight 告警 | 是：仅一项检查 | 发行版内存在 >1 GB 的 `.tar`/`.tar.gz` 时在 `okw` 预检中输出告警 | 待办 |
| A7 | 清理空的 `C:\WSL-backup` 目录 | 是：仅一个空目录 | 目录不存在且 C 盘可用量不变 | 待授权 |

***

## 七、结论

1. **49.46 GiB 的构成已完全量化**：约 15 GiB 是系统本体，约 4.8 GiB 是 ext4 元数据开销，**29.63 GiB 是一个被错放在发行版内部的 rootfs 备份**。所谓「8 倍膨胀」是四口径混用造成的错觉，其中一半以上是可回收冗余。
2. **回收结果可验证**：D 盘 38.10 → 89.07 GiB（净 +50.97 GiB），其中 32.61 GiB 来自 VHDX 物理压缩、31.79 GiB 来自 tar 删除（两者作用在不同盘，不重复计算）；C 盘 86.70 → 85.68 GiB（中转后再删除，净损约 1 GiB 为其他进程波动）。
3. **系统水位正常**：当前 `du /` 14 G（`df` 16 G），构成 `/usr` 12 G + `/var` 1.6 G + `/home` 184 M + `/boot` 144 M，属桌面发行版正常范围，无需继续优化。
4. **本轮暴露的流程缺陷**：一是把备份放在被备份对象内部；二是验收曾依赖命令提示而非数值基线；三是回收站清理使用了非递归筛选，导致孤立 `$R` 目录残留；四是路径核对出现 `C:\WSL\backup` 与 `C:\WSL-backup` 的误判（连字符被当作路径分隔），导致一次错误的「文件不存在」结论。
5. **未闭合项**：解压 tar 与当前系统 16 GiB 的体积缺口因 tar 已删除而无法复核，A4 行动项用于在历史台账中追溯，未经验证前不写入知识库结论。
