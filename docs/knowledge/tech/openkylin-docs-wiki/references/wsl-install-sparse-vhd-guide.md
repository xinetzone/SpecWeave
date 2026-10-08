---
title: "openKylin 3.0 WSL 安装与稀疏 VHD 实操指南（Windows 10 实测）"
date: 2026-09-29
category: "tech"
tags:
  - openkylin
  - wsl
  - windows
  - vhdx
  - sparse
  - troubleshooting
status: "verified"
security_level: "public"
source: "2026-09-29 本机实测（Windows 10.0.19044 + WSL 2.9.3.0 + openKylin 3.0 huanghe amd64），方法论 session sc-20260929-openkylin-wsl-install-sparse"
---

# openKylin 3.0 WSL 安装与稀疏 VHD 实操指南

> **范围声明**：本文仅覆盖官方 **336 MB 最小 WSL 镜像**（命令行形态）的本机实测。openKylin 3.0 另提供 6.14 GiB 的 **Desktop WSL 桌面镜像**（含 xrdp + UKUI），两镜像的精确对照、桌面镜像分层磁盘规划（事前建议跨盘 20 GiB 起步／同盘 25～30 GiB／手动解压排障 45～50 GiB；2026-10-08 实测同盘峰值仅 19.2 GiB）、官方远程桌面接入流程与验收清单见 [双 WSL 镜像对照与选型参考](wsl-dual-image-selection.md)——该文档的桌面镜像已于 **2026-10-08 落机实测**（51.6 秒导入、1900 包、VHD 13.01 GiB、xrdp 服务 active；仅交互 UKUI 登录观感待用户首登确认）。
>
> 本指南指导你在 Windows 10/11 上用官方 **336 MB 最小 WSL 镜像**离线安装 openKylin 3.0，完成发行版验收，并在理解风险的前提下决定是否启用稀疏 VHD。
>
> 这是 [openKylin 全面调研报告](project-overview.md) §7.2"最小试用路径"第 1 条的**实测落地篇**——调研报告编写时该路径标注为"未实测"，本文补上完整命令、排障过程与验收记录。

---

## 1. 你会得到什么

- 一个名为 `openKylin-3.0` 的 WSL2 发行版：openKylin 3.0（代号 huanghe）、默认普通用户 `openkylin`（UID 1000）、systemd 已启用、约 405 个预装软件包。
- 一个位于非系统盘的 `ext4.vhdx`（安装后约 1.3 GB），可选择启用稀疏标志。
- 一套对 `E_UNEXPECTED` / `E_ABORT` 导入失败的排障流程（本机实测 4 次失败后的成功路径）。

**环境基线（实测机）**：Windows 10.0.19044、WSL 2.9.3.0、内核 6.18.35.2-1、x86_64。镜像来源为 openKylin 官网下载中心的 openKylin 3.0 WSL 最小镜像（`openKylin-3.0-wsl-amd64.wsl`，352,431,812 字节 / 336.1 MB）。

> 前置知识：`.wsl` 文件本质是 **gzip 压缩的 tar 归档**（文件头魔数 `1F 8B`），不是 APPX/ZIP，无需安装器，通过 `wsl --import` 或 `wsl --install --from-file` 注册。

---

## 2. 安装前检查（5 分钟）

```powershell
# 若 wsl 命令无法识别（PATH 被裁剪的环境），用全路径：
$wsl = "$env:WINDIR\System32\wsl.exe"
$env:WSL_UTF8 = 1   # 避免中文输出乱码

& $wsl --version     # 确认 WSL ≥ 2.x
& $wsl -l -v         # 记录现有发行版与默认发行版（带 * 的那个）
```

| 检查项 | 期望 | 不满足时 |
|---|---|---|
| WSL 版本 | 2.x（本机 2.9.3.0） | `wsl --update` |
| 默认版本 | WSL2 | `wsl --set-default-version 2` |
| 目标盘剩余空间 | ≥ 3 GB（镜像 336 MB + VHD 约 1.3 GB + 解压临时文件约 1.1 GB） | 换盘或先清理 |
| 空闲物理内存 | 建议 ≥ 3 GB（**经验启发值**：仅来自本机 0.8 GB 失败 / 4.5 GB 成功两点观测，非官方阈值，下界未测定） | 关闭重型程序后 `wsl --shutdown` 再查 |

记下当前的**默认发行版**——安装新发行版不应改变它，验收时要复核星标。

---

## 3. 标准安装路径

### 3.1 放置镜像并创建目录

```powershell
$envs = "d:\AI\.chaos\envs"                 # 按你的实际位置修改
$wslFile = "$envs\openKylin-3.0-wsl-amd64.wsl"
$installDir = "$envs\openKylin-3.0"
New-Item -ItemType Directory -Path $installDir -Force | Out-Null

# 校验镜像：约 336 MB，文件头应为 1F-8B（gzip）
(Get-Item $wslFile).Length / 1MB
Format-Hex $wslFile -Count 2
```

### 3.2 注册发行版（两种方式任选其一）

```powershell
# 方式 A：from-file 直接注册（WSL 新版）
& $wsl --install --from-file $wslFile --location $installDir `
       --name openKylin-3.0 --version 2 --no-launch

# 方式 B：经典 import（gzip tar 可直接喂给 import）
& $wsl --import openKylin-3.0 $installDir $wslFile --version 2
```

顺利时整个过程数秒到一两分钟。若报错，**不要立刻重试**，转 §4。

### 3.3 验收（5 项）

```powershell
# ① 发行版在列、WSL2；默认发行版星标未被改变
& $wsl -l -v
# ② 系统版本：VERSION="3.0 (huanghe)"
& $wsl -d openKylin-3.0 -- cat /etc/os-release
# ③ 用户/UID/根分区/软件包计数（注意 405 的口径是 dpkg-query，
#    `dpkg -l | wc -l` 含 5 行表头会输出 410，勿据此误判）
& $wsl -d openKylin-3.0 -- /bin/bash -lc 'echo "user=$(whoami) uid=$(id -u)"; df -h / | tail -1; echo "pkgs=$(dpkg-query -W | wc -l)"'
# ④ 默认用户与 systemd 配置
& $wsl -d openKylin-3.0 -- cat /etc/wsl.conf
# ⑤ 用完释放 VM 内存
& $wsl --terminate openKylin-3.0
```

本镜像验收记录：默认用户 `openkylin`（UID 1000，无需手动建用户）、内核 `6.18.35.2-microsoft-standard-WSL2`、软件包 405（`dpkg-query -W | wc -l`）；`/etc/wsl.conf` 已含 `[user] default=openkylin` 与 `[boot] systemd=true`；注册前后默认发行版均未改变。

> 若你导入的是其他社区 WSL 镜像、登录后是 root，请按 [WSL 发行版安装、迁移与配置速查手册](../../../../retrospective/patterns/code-patterns/wsl-distro-install-migration-guide.md) 模式三配置 `/etc/wsl.conf` 的 `[user] default=`，并在 PowerShell 侧 `wsl --terminate` 使其生效。

---

## 4. 排障：导入报 E_UNEXPECTED / E_ABORT（实测排障路径）

> 本节命令沿用 §2 的 `$wsl` 与 §3.1 的 `$envs`、`$installDir` 变量；若另开会话请先重新赋值。

### 4.1 症状与判别

本机连续遇到：

| 尝试 | 命令形态 | 错误码 | 持续/进度 |
|---|---|---|---|
| 1 | `--install --from-file`（.wsl） | `Wsl/Service/RegisterDistro/E_UNEXPECTED` | 数秒，VHD 停在 62 MB |
| 2 | `--import`（.wsl） | `RegisterDistro/E_UNEXPECTED` | VHD 停在 262 MB |
| 3 | `--import`（解压后的 tar） | `RegisterDistro/E_UNEXPECTED` | VHD 停在 336 MB |
| 4 | `--import`（换目录 D:\WSL） | `RegisterDistro/CreateVm/E_ABORT` | 约 1 秒秒败 |
| 5 | `--import`（原目录，释放内存后） | **成功** | **8 秒** |

**关键判别特征**：三次 `E_UNEXPECTED` 的 VHD 停止位置各不相同（62/262/336 MB）。失败位置不固定，是与运行时资源压力（本机最可能是内存不足）强相关的信号；安装包损坏的失败位置通常稳定复现。需要说明：本机常驻三套安全软件（奇安信、腾讯电脑管家、Defender），未做加白/拦截日志对照，内存为最可能但非唯一解释；且 `wsl --shutdown` 同时释放内存并重置 WSL 服务，两者未做对照分离。

### 4.2 修复步骤（按顺序执行）

1. **先排除包损坏**：文件大小与官网一致 + 归档可完整列出条目（本机 27,930 条）即排除，不要重下。
2. **采样内存**（秒败 `E_ABORT` 那次实测空闲物理内存仅 0.8 GB，Trae 多进程约占 3.1 GB）：
   ```powershell
   Get-CimInstance Win32_OperatingSystem |
     Select-Object @{N='FreePhysGB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}
   ```
3. **释放内存**：`wsl --shutdown`，等 3 秒后重测（本机恢复到约 4.5 GB 后同命令导入成功）；必要时关闭占内存最大的 IDE/浏览器进程。
4. **降低导入期内存峰值**：把 gzip .wsl 预解压为纯 tar 再导入。以下脚本适用于 PowerShell 7（Windows PowerShell 5.1 需先 `Add-Type -AssemblyName System.IO.Compression`）；tar 路径可自定义，下例放在 `$envs` 根（复盘实测时临时产物位于独立工作目录，位置不影响结论）：
   ```powershell
   $src = "$envs\openKylin-3.0-wsl-amd64.wsl"; $tar = "$envs\rootfs.tar"
   $in = $gz = $out = $null
   try {
     $in  = [System.IO.File]::OpenRead($src)
     $gz  = New-Object System.IO.Compression.GzipStream($in,[System.IO.Compression.CompressionMode]::Decompress)
     $out = [System.IO.File]::Create($tar)
     $gz.CopyTo($out)
   } finally {
     if ($out) { $out.Dispose() }; if ($gz) { $gz.Dispose() }; if ($in) { $in.Dispose() }
   }
   & $wsl --import openKylin-3.0 $installDir $tar --version 2
   ```
5. **在原路径重试**，成功后回到 §3.3 验收，并删除临时 `rootfs.tar`。

> 详细的判读规则（错误码分段语义、失败指纹记录、反模式清单）见沉淀模式：[WSL 导入内存分诊与稀疏 VHD 决策模式](../../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)。

---

## 5. 稀疏 VHD：先决定你要解决哪个问题

VHDX 虚拟磁盘**只增不减**：在 WSL 里删除文件后，宿主看到的 `ext4.vhdx` 不会自动变小。两条解决路径对应两个不同问题：

| 你的诉求 | 用什么 | 风险 | 何时生效 |
|---|---|---|---|
| 今后删文件时**自动**回收空间 | sparse 稀疏标志 | 现有 VHD 需 `--allow-unsafe` 强制开启，官方提示有潜在损坏风险 | 未来删除时 |
| 已经删了很多文件，要**立即**缩小 VHD | diskpart 只读挂载 + `compact vdisk` | 无元数据重写，风险低 | 操作当下 |

### 5.1 启用稀疏标志（含官方拦截处理）

WSL 2.9.3 对**已有数据的现有 VHD** 直接设置会被拒绝：

```text
由于潜在的数据损坏，目前已禁用稀疏 VHD 支持。
错误代码: Wsl/Service/E_INVALIDARG
```

执行前三问定级：① VHD 内有无不可重建的用户数据？② 有无源包/备份、重建多久？（本机全新系统 + 源包保留 + 8 秒可重建，故风险可接受）③ 操作时能否保证不断电？

```powershell
# 1) 全部停掉
& $wsl --shutdown; Start-Sleep 3
# 2) 复测空闲内存（本机稀疏化前实测约 2.6 GB；避开明显低水位）
Get-CimInstance Win32_OperatingSystem |
  Select-Object @{N='FreePhysGB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}
# 3) 先裸执行一次，亲眼读到官方拦截文本（E_INVALIDARG 提示），完成风险确认
& $wsl --manage openKylin-3.0 --set-sparse true
# 4) 经三问定级、确认接受风险后，再追加 --allow-unsafe 强制执行
& $wsl --manage openKylin-3.0 --set-sparse true --allow-unsafe
# 5) 复验标志（PATH 被裁剪时 fsutil 也用全路径）
& "$env:WINDIR\System32\fsutil.exe" sparse queryflag "$installDir\ext4.vhdx"  # 期望：This file is set as sparse
# 6) 复验发行版完整性
& $wsl -d openKylin-3.0 -- /bin/bash -lc 'whoami; df -h / | tail -1'
& $wsl --terminate openKylin-3.0
```

**预期管理**：本机设置后逻辑 1,317 MB、实际占用 1,293.4 MB，仅差约 24 MB——全新系统内部全是有效数据，当下本就没有空间可回收。稀疏标志的价值在**以后**删除大文件时自动归还 D 盘空间。

> 注意：`(Get-Item).Length` 是逻辑大小，不反映稀疏洞；查真实占用要用 `GetCompressedFileSizeW`，完整脚本见[沉淀模式](../../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md) §模式二。

### 5.2 立即压缩存量（无损坏风险的替代路径）

当你已经在 WSL 内删除大量数据、希望马上收回宿主空间时使用。**需以管理员身份启动终端**（diskpart 的 `attach`/`compact` 要求提权）：

```text
wsl --shutdown
diskpart
  select vdisk file="D:\...\openKylin-3.0\ext4.vhdx"
  attach vdisk readonly
  compact vdisk
  detach vdisk
  exit
```

压缩前记录 VHD 大小，压缩后对比。该路径不需要 `--allow-unsafe`。

---

## 6. 常见问题

**Q1：`--import` 报 `E_UNEXPECTED`，是不是镜像坏了？**
先看多次失败的 VHD 停止位置是否漂移。位置不固定 → 优先按 §4 查内存；位置固定且归档校验失败才考虑重下。

**Q2：秒败 `CreateVm/E_ABORT` 是什么？**
VM 没创建起来。本机实测该次尝试时空闲物理内存约 0.8 GB；`wsl --shutdown` 后水位恢复、同形态命令导入成功。按本机时序证据，它与 `E_UNEXPECTED` 更可能是同一资源因素（内存压力）在不同阶段的表现，但前三次失败未做同期内存采样，此结论为最可能解释而非排他性定论（详见 §4.1 说明）。

**Q3：会改掉我的默认 WSL 发行版吗？**
不会。`--import`/`--install --from-file` 不改变默认发行版；验收时核对 `wsl -l -v` 的星标即可。如误改，用 `wsl --set-default <名称>` 改回。

**Q4：PATH 里没有 wsl、输出中文乱码怎么办？**
用全路径 `$env:WINDIR\System32\wsl.exe`，并在会话开头设 `$env:WSL_UTF8=1`。

**Q5：rootfs.tar、失败的残留 vhdx 要删吗？**
成功验收后临时 tar 可删；失败遗留的 ext4.vhdx 在对应发行版未注册成功时可直接清理。源 `.wsl` 建议保留作为重建兜底（重新导入约 8 秒）。

**Q6：如何卸载？**
`wsl --unregister openKylin-3.0` 会删除该发行版全部数据与 VHD，执行前确认不再需要。

---

## 7. 参考资料

- [openKylin 全面调研：从桌面根社区到 Agent OS](project-overview.md)（§7.2 最小试用路径、§8 局限 5）
- [WSL 导入内存分诊与稀疏 VHD 决策模式](../../../../retrospective/patterns/code-patterns/wsl-import-memory-triage-sparse-vhd.md)
- [WSL 发行版安装、迁移与配置速查手册](../../../../retrospective/patterns/code-patterns/wsl-distro-install-migration-guide.md)
- [openKylin 3.0 WSL 导入排障复盘报告](../../../../retrospective/reports/task-reports/retrospective-openkylin-wsl-install-sparse-20260929/retrospective-report.md)
- Microsoft WSL 基本命令：https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands
