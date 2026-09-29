---
type: Pattern
id: "wsl-import-memory-triage-sparse-vhd"
title: WSL 导入内存分诊与稀疏 VHD 决策模式
version: 1.0
date: 2026-09-29
maturity: L1
tags: [WSL, Windows, VHDX, sparse, memory, troubleshooting, openkylin]
source: "openKylin 3.0 WSL 安装与稀疏 VHD 启用本机实测（session sc-20260929-openkylin-wsl-install-sparse）"
---

# WSL 导入内存分诊与稀疏 VHD 决策模式

> 适用于 Windows 10/11 + WSL2。包含两个配套模式：**模式一：非确定性导入失败的内存分诊法**（处理 `RegisterDistro/E_UNEXPECTED` 与 `CreateVm/E_ABORT`）；**模式二：稀疏 VHD 的双问题决策法**（区分"未来自动回收"与"立即压缩存量"）。

## 适用边界

**适用于**：

- `wsl --install --from-file` 或 `wsl --import` 报 `Wsl/Service/RegisterDistro/E_UNEXPECTED`（灾难性故障）
- `wsl --import` 秒败报 `Wsl/Service/RegisterDistro/CreateVm/E_ABORT`（已中止操作）
- 同一导入命令反复失败，但 ext4.vhdx 每次停在**不同**写入进度
- 宿主机内存偏紧（本机实测：空闲 0.8 GB 时导入失败、约 4.5 GB 时成功，失败与成功之间的经验下界未测定；约 2~3 GB 仅为两点之间的经验启发值，非官方阈值），或并行运行 IDE/AI 工具多进程、多套安全软件
- 需要决定是否对现有 VHD 启用 sparse、或删除大量文件后如何向宿主机回收空间

**不适用于**：

- 失败位置稳定复现且归档完整性校验失败（应优先按损坏包处理，参见 [wsl-distro-install-migration-guide.md](wsl-distro-install-migration-guide.md) 的文件头/大小校验）
- 发行版可以启动、仅内部 apt/网络异常（属发行版内问题，非注册阶段故障）
- 需要迁移发行版位置（走 export → unregister → import，见 [wsl-distro-install-migration-guide.md](wsl-distro-install-migration-guide.md) 模式二）
- 磁盘空间立即回收的通用场景（应使用 [wsl-docker-storage-cleanup-five-step-method.md](wsl-docker-storage-cleanup-five-step-method.md) 与 diskpart compact）

---

## 模式一：非确定性导入失败的内存分诊法

### 核心步骤

1. **记录失败指纹**：保存错误码、失败阶段（RegisterDistro / CreateVm）、耗时（秒败还是中途败）、ext4.vhdx 残留大小。重复执行一次，对比 VHD 停止位置是否变化——位置漂移即进入本模式。
2. **先验归档，排除损坏假设**：核对文件大小（openKylin 3.0 WSL 最小镜像约 336 MB）与 gzip 魔数 `1F 8B`；对 .wsl 做归档列出/完整性遍历；能完整列出条目即排除包损坏。
3. **采样内存水位**：
   ```powershell
   Get-CimInstance Win32_OperatingSystem |
     Select-Object @{N='FreePhysGB';E={[math]::Round($_.FreePhysicalMemory/1MB,2)}},
                   @{N='FreeVirtGB';E={[math]::Round($_.FreeVirtualMemory/1MB,2)}}
   Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 8 Name,Id,
     @{N='WS_MB';E={[math]::Round($_.WorkingSet64/1MB)}}
   ```
   本机实测：空闲 0.8 GB 时秒败 `E_ABORT`；`wsl --shutdown` 释放后 4.5 GB 时 8 秒导入成功。这两个是**导入操作仅有的两个观测点**，之间的经验下界未测定；2.6 GB 是另一次稀疏化操作前的采样，不能当作导入数据点。所有数字均为本机实测，非官方阈值。
4. **释放 WSL 虚拟机内存**：`wsl --shutdown`，等待 3 秒后复测水位。WSL2  Utility VM 占用在发行版全部 Stopped 后仍可能保留，shutdown 是显式归还手段。
5. **降低导入期内存峰值**：将 gzip 形态的 .wsl 用流式解压预先展开为纯 tar，再 `wsl --import <名称> <目录> rootfs.tar --version 2`，使导入阶段不再承担解压工作。以下脚本在 PowerShell 7 下运行（Windows PowerShell 5.1 需先 `Add-Type -AssemblyName System.IO.Compression`）；用 try/finally 保证异常时不残留文件句柄与半成品 tar：
   ```powershell
   $src = "d:\path\distro.wsl"; $dst = "d:\path\rootfs.tar"
   $in = $gz = $out = $null
   try {
     $in  = [System.IO.File]::OpenRead($src)
     $gz  = New-Object System.IO.Compression.GzipStream($in, [System.IO.Compression.CompressionMode]::Decompress)
     $out = [System.IO.File]::Create($dst)
     $gz.CopyTo($out)
   } finally {
     if ($out) { $out.Dispose() }; if ($gz) { $gz.Dispose() }; if ($in) { $in.Dispose() }
   }
   ```
6. **水位恢复后原路径重试**：不要先换路径——本模式实测更换目录不改变结果，反而损失"路径因素"的判据；成功后立即执行验收（见步骤 7）。
7. **成功后五点验收**：`wsl -l -v`（名称/版本/默认发行版未被改变）；`cat /etc/os-release`；`whoami`/`id -u`；`df -h /` 与包管理器列表；清理临时 tar 与残留目录。确认默认发行版星标仍属于预期对象。

### 反模式（均来自本次实测教训）

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 看到 `E_UNEXPECTED（灾难性故障）` 就判定包损坏并反复重下 | 浪费带宽与时间；最可能的资源因素（内存压力）未解除，重试大概率再败 | 步骤 1-2 先比对失败位置稳定性、验归档完整性 |
| 2 | 失败后立刻更换安装目录/盘符继续试 | 引入路径变量污染判据；本案例换路径后错误码反而变化 | 固定变量，先采样资源水位并 `wsl --shutdown` |
| 3 | 不采样内存、凭"我电脑内存很大"继续重试 | 空闲内存与物理总量无关；IDE 多进程 + 杀软常驻时 16/32 GB 物理内存也可能只剩 1 GB | 步骤 3 以实测 `FreePhysicalMemory` 为准 |
| 4 | 忽略错误前的 `--shutdown` 前置，发行版仍在 Running 时做重型 manage/import | VM 内存未释放，在低水位上叠加操作 | 导入与稀疏化前统一 shutdown + 等待 + 复测 |
| 5 | 成功后不验收、不清理中间产物（rootfs.tar、自测发行版） | 默认发行版被改、临时目录长期占空间、残留 VHD 与注册项不一致 | 执行步骤 7 五点验收并删除中间文件；`D:\WSL` 等他系统数据目录先识别再避让 |

### 检验标准

- 重复导入失败时，能在 2 次采样内回答三问：失败位置是否漂移？当前空闲物理内存多少？shutdown 后恢复到多少？
- 成功导入的验收记录包含默认发行版星标截图/文本证据（防止安装动作改变用户的默认 WSL 环境）。
- 全部临时文件已删除，源 .wsl 包按重建兜底需要保留或显式标记可删。

---

## 模式二：稀疏 VHD 的双问题决策法

### 决策表：先分清你要解决的是哪个问题

| 问题 | 手段 | 数据损坏风险 | 生效时点 |
|---|---|---|---|
| 今后在 WSL 内删除文件，希望**自动**归还宿主机空间 | `wsl --manage <distro> --set-sparse true [--allow-unsafe]` | 现有含数据 VHD 需 `--allow-unsafe`，官方提示有潜在损坏风险 | 设置成功后的未来删除 |
| 已经删除了大量文件，要**立即**缩小当前 VHD | `wsl --shutdown` → diskpart：`attach vdisk readonly` → `compact vdisk` → `detach vdisk` | 只读挂载压缩，无元数据重写 | 操作当下 |

> WSL 2.9.3 对**已含数据的现有 VHD** 直接执行 `--set-sparse true` 会返回 `Wsl/Service/E_INVALIDARG`，中文提示"由于潜在的数据损坏，目前已禁用稀疏 VHD 支持"，并给出 `--allow-unsafe` 强制方式；这是官方安全策略而非故障。

### 启用 sparse 的安全步骤

1. **三问定级**（决定是否允许使用 `--allow-unsafe`）：
   - VHD 内是否存在不可重建的用户数据？
   - 是否有完整源包/备份，重建成本是多少？（全新发行版 + 源包保留 + 8 秒导入 = 低风险的典型情形）
   - 操作期间能否保证不断电、不强制关机？
2. **前置准备**：`wsl --shutdown`；采样空闲内存（避开低水位；本机稀疏化成功前的实测水位为 2.6 GB，但该点只代表"本操作成功时的水位"，不构成阈值结论）；确认所有发行版 Stopped。
3. **执行与强制**：先执行不带 `--allow-unsafe` 的命令读取官方拦截文本；确认风险后执行：
   ```powershell
   wsl --manage <DistroName> --set-sparse true --allow-unsafe
   ```
4. **复验标志**：用全路径执行（PATH 被裁剪时裸命令可能无法解析）：
   ```powershell
   & "$env:WINDIR\System32\fsutil.exe" sparse queryflag "$installDir\ext4.vhdx"
   ```
   应输出 "This file is set as sparse"。
5. **复验完整性与占用**：启动发行版执行 `whoami`、`df -h /`、包管理器查询；区分逻辑大小与实际占用——PowerShell 的 `(Get-Item).Length` 只是逻辑大小，实际占用需用 `GetCompressedFileSizeW`：
   ```powershell
   $vhd = "$installDir\ext4.vhdx"   # 换成实际的 VHD 完整路径
   if (-not ('DiskApi' -as [type])) {
     Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
     public static class DiskApi { [DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]
     public static extern uint GetCompressedFileSize(string n,out uint h); }'
   }
   $h=[uint32]0; $l=[DiskApi]::GetCompressedFileSize($vhd,[ref]$h)
   if ($l -eq 0xFFFFFFFF) {
     $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
     throw "GetCompressedFileSize 调用失败，Win32 错误码：$err"
   }
   $actual=([uint64]$h -shl 32) -bor [uint64]$l
   $logical=(Get-Item $vhd).Length
   "逻辑大小: {0:N1} MB; 实际占用: {1:N1} MB" -f ($logical/1MB), ($actual/1MB)
   ```
6. **收尾**：`wsl --terminate <distro>` 释放 VM 内存；记录"逻辑 vs 实际"两组数字作为基线。

### 反模式

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 期望 sparse 设置后文件立刻变小 | 对全有效数据的全新 VHD 实测仅差约 24 MB（1317 vs 1293.4 MB），误以为操作失败而反复折腾 | 先查 VHD 内部有无空闲块；立即回收走 diskpart compact |
| 2 | 不读拦截提示、直接照抄网上命令加 `--allow-unsafe`，对存有用户数据的系统执行 | 元数据重写期断电/崩溃可能损坏文件系统 | 三问定级；有数据系统先 `wsl --export` 备份或改走 diskpart |
| 3 | 用 `Get-Item.Length` 评估稀疏化效果 | 逻辑大小不反映稀疏洞，得出"没生效"的错误结论 | 用 `GetCompressedFileSizeW` 取实际占用 |
| 4 | 在发行版 Running 状态执行 manage/压缩 | 文件被占用，attach 拒绝访问或设置失败 | 统一先 `wsl --shutdown` |

### 检验标准

- `fsutil sparse queryflag` 明确返回 sparse 已设置；发行版启动与文件系统命令全部正常。
- 文档/沟通中同时给出逻辑大小与实际占用两个数字，并写明"收益发生在未来删除时"。
- 若选择 diskpart 路径，压缩前后各取一次 VHD 大小并保留对比记录。

---

## 跨场景迁移

- **其他 VHDX/VHD 消费者**（Hyper-V 虚拟机、Docker Desktop 的 ext4.vhdx、podman machine）：动态扩展磁盘"只增不减"与稀疏/压缩二元选择是同一问题模型，"逻辑大小 vs 实际占用""未来策略 vs 当下压缩"的区分直接适用；可迁移到容器镜像层清理后的磁盘回收决策，参见 [wsl-docker-storage-cleanup-five-step-method.md](wsl-docker-storage-cleanup-five-step-method.md)。
- **通用资源型故障分诊**：任何"失败位置非确定性 + 错误措辞严重"的操作（大文件解压、数据库恢复、容器导入）都可套用步骤 1-4——先验证输入物完整性，再采样资源水位，最后在资源释放后原路径重试，而不是更换输入物或目标位置。

## 成熟度与证据

- **L1（单案例实测，公开互证待登记）**：本模式基于 2026-09-29 本机单环境实测（Windows 10 19044 / WSL 2.9.3.0 / openKylin 3.0 amd64，5 次导入尝试 + 1 次稀疏化）。2026 年 9 月的公开检索可见记录相同 `--set-sparse` 拦截信息与 `--allow-unsafe`/diskpart 两条路径的中文技术文章，但具体出处 URL 尚未登记，故暂不计入正式互证。环境混杂因素声明：本机常驻奇安信、腾讯电脑管家、Defender 三套安全软件，未做加白/拦截日志对照，内存压力是失败最可能但非唯一的解释；`wsl --shutdown` 同时改变内存水位与 WSL 服务状态，二者未做对照分离。内存水位数值尚无第二环境复测。
- 升级 L2 条件：在另一台主机或 WSL 版本上复现"低水位失败 → shutdown 恢复 → 成功"的完整对照（最好带尝试全程内存曲线），或取得两个以上不同发行版的同类案例；同时登记 2 篇以上可核查的公开互证出处。

## 参考资料

- 复盘报告：[openKylin 3.0 WSL 导入排障与稀疏 VHD 启用复盘](../../reports/task-reports/retrospective-openkylin-wsl-install-sparse-20260929/retrospective-report.md)
- 实操教程：[openKylin 3.0 WSL 安装与稀疏 VHD 实操指南](../../../knowledge/tech/openkylin/wsl-install-sparse-vhd-guide.md)
- 相邻模式：[WSL 发行版安装、迁移与配置速查手册](wsl-distro-install-migration-guide.md)
- Microsoft WSL 基本命令：https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands

<!-- changelog -->
- 2026-09-29 | feat | 初始版本：基于 openKylin 3.0 WSL 安装实测萃取内存分诊法与稀疏 VHD 双问题决策法
- 2026-09-29 | fix | V 阶段对抗审查后修复：磁盘占用测量片段补 `$vhd` 赋值与输出（P0）；"同一根因"统一降级为"最可能的共同资源因素"；阈值标注改为 0.8/4.5 两点实测并将 2.6 GB 明确为稀疏化场景；解压片段补 PowerShell 7 前提与 try/finally；补杀软混杂因素声明；公开互证标注为待登记
