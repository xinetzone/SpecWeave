---
id: "vhdx-two-phase-recovery-sop"
title: "VHDX 二相回收 SOP（sparse 在线相 ↔ compact 离线相）"
type: "process-pattern"
maturity: "L2-已验证"
maturity_note: "案例1：C盘治理 20260828，离线相单次回收 20.4GB（32.31GB→11.93GB），sparse互斥坑完整实证；案例2：docker-cache-to-wsl-migration-20260818 的 vhdx 迁移处理。1 次完整正向应用 + 1 次相关案例"
created: "2026-08-28"
last_updated: "2026-08-28"
source:
  - "retrospective-c-drive-vhdx-recovery-20260828（模式1 + 洞察2/3）"
related_patterns:
  - "ops-sop-standard-template.md"
tags: ["wsl2", "vhdx", "diskpart", "sparse-vhd", "fstrim", "podman-machine", "disk-space", "windows"]
validation_count: 2
reuse_count: 0
documentation_level: "standard"
---

# VHDX 二相回收 SOP（sparse 在线相 ↔ compact 离线相）

## 触发场景

- WSL2 发行版 / Podman machine / Hyper-V 虚拟磁盘的 `ext4.vhdx` 文件大小远超内部实际用量（差值 >5GB 值得处理）
- 系统盘（通常是C盘）空间紧张，需要把 vhdx 空洞归还宿主
- 容器/发行版内已删除大量数据（如清理镜像），但宿主侧空间未归还

**不适用于**：vhdx 大小与内部用量基本一致（无空洞可回收）；系统盘空间充裕（收益低于停机成本）；vhdx 位于可轻松扩容的数据盘。

## 前置知识（问题本质）

vhdx 是**只增不减**的虚拟磁盘容器。客体内删除文件只是 ext4 元数据操作；块归还宿主需要两步显式触发：

1. **TRIM**（`fstrim`）：把空闲块标记为 VHDX 未映射（元数据记账）
2. **物理回收**（二选一，互斥）：
   - **在线相（sparse）**：NTFS 稀疏属性使后续 TRIM 直接穿透归还宿主空间
   - **离线相（compact）**：`diskpart compact vdisk` 重写文件丢弃未映射块

⚠️ **核心约束：sparse 属性与 diskpart compact 互斥**——compact 会拒绝稀疏文件（报「文件不能是稀疏文件」）。两条路径二选一，不可叠加。

## 决策树

```
能否接受 wsl --shutdown（所有发行版+容器中断几分钟）？
├─ 否（在线场景）→ 相位A：sparse 在线路径
└─ 是（离线场景）→ 相位B：compact 离线路径（回收更彻底，推荐）
```

补充判断：
- 曾执行过 `--set-sparse`？→ 走相位B前必须先清 sparse 标志（步骤 B2）
- 首次治理且追求简单？→ 直接相位B，跳过 sparse 永不踩互斥坑

---

## 相位A：sparse 在线路径（免停机）

> 前提：WSL ≥ 2.x 且支持 `wsl --manage` 子命令（本机 2.9.3 验证；旧版无 `--set-sparse`）。注意：一旦转 sparse，将来走相位B前必须先清标志（B2）。

```powershell
# A1. 转稀疏（--allow-unsafe 为兼容性标志，WSL 2.x 官方支持）
wsl --manage <发行版名> --set-sparse true --allow-unsafe

# A2. 触发一次归还
wsl -d <发行版名> -u root -- fstrim -v /

# A3. 验证：宿主侧实际占用（逻辑大小不变，看 on-disk）
# PowerShell 查 size-on-disk：
fsutil file layout <vhdx路径> | Select-String "Sparse"
```

**生效条件（本案例观察）**：转 sparse 后仅归还 0.1GB——既有空洞未归还。两种解释并存：①sparse 转换不会对已存在的 unmapped 块重写 NTFS 分配；②删除时机的 TRIM 已被记账（F-033 二次 fstrim 同样无效）。**无论机制为何，可操作结论是：存量空洞必须走相位B回收，sparse 只对今后的删除+trim 生效。**

**撤销 sparse**：`wsl --manage <发行版名> --set-sparse false --allow-unsafe` 可逆转换；若跳过撤销直接走相位B，必须在 B2 用 `fsutil sparse setflag ... 0` 清标志，否则 compact 报错。

**适用**：活跃开发环境、不能中断的服务、把 sparse 作为长期策略（此后每次发行版内清理+trim 都即时生效）。

## 相位B：compact 离线路径（推荐，回收彻底）

### B0. 前置条件

- ✅ 管理员权限终端（diskpart 需要）
- ✅ 所有并行会话停止操作 WSL/Podman（否则句柄撞车，本案例实证 F-029）
- ✅ 记录 vhdx 路径与当前大小、发行版内部 `df -h /` 实际用量（用于 B5 验收）

vhdx 路径发现（注册表）：

```powershell
Get-ChildItem HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss |
  ForEach-Object { $p = Get-ItemProperty $_.PSPath;
    "$($p.DistributionName) => $($p.BasePath)\ext4.vhdx" }
```

### B1. 客体内清理 + TRIM

```powershell
# 删除发行版/容器内不需要的数据后：
wsl -d <发行版名> -u root -- fstrim -v /
```

### B2. 若曾设 sparse：清除稀疏标志（关键！互斥坑）

```powershell
fsutil sparse setflag <vhdx路径> 0
```

### B3. 关闭 WSL 全家桶

```powershell
wsl --shutdown
Start-Sleep -Seconds 3
# 杀残余用户态进程
Get-Process wslhost, wslrelay -ErrorAction SilentlyContinue | Stop-Process -Force
# 停两个服务（只停 wslservice 不够，vmcompute 也持有句柄）
Stop-Service wslservice -Force
Stop-Service vmcompute -Force
Start-Sleep -Seconds 3
```

### B4. diskpart 压缩

```powershell
# 写入脚本文件（交互式 diskpart 不适合自动化）
@"
select vdisk file="<vhdx路径>"
attach vdisk readonly
compact vdisk
detach vdisk
"@ | Out-File -Encoding ascii compact.txt
diskpart /s compact.txt
```

### B5. 恢复服务 + 验收

```powershell
Start-Service vmcompute
Start-Service wslservice
# 按项目约定挂保活进程（防 vmIdleTimeout 自动关机）
wsl -d <发行版名> -- sleep infinity   # 后台挂起
```

**验收标准**：compact 后 vhdx 逻辑大小 ≈ 内部实际用量（偏差 <5%）。本案例：11.93GB = 11.93GB 完全一致——完全一致属理想结果而非普遍预期，只要偏差 <5% 即合格。

---

## 验证（两相位通用）

| 检查项 | 命令 | 预期 |
|--------|------|------|
| 客体内实际用量 | `wsl -d <发行版> -- df -h /` | 回收基准值 |
| vhdx 逻辑大小 | `(Get-Item <vhdx>).Length / 1GB` | 相位B后 ≈ df 值 |
| C盘剩余空间 | `Get-PSDrive C` | 显著增加 |
| 环境恢复 | `wsl -l -v` 全部 Stopped→Running | 容器 healthy |

## 故障排查

| 症状 | 根因 | 处置 |
|------|------|------|
| compact 报「文件被另一程序使用」 | wslservice/vmcompute 未停；或并行会话拉起了 machine | 重走 B3，确认无并行操作后重试 |
| compact 报「文件不能是稀疏文件」 | vhdx 带 sparse 属性 | 执行 B2 清标志后重试 |
| fstrim 显示 trimmed 大但宿主无变化 | TRIM 仅元数据记账，删除时机的 TRIM 已消耗 | 走相位B物理回收；或 sparse 模式下等**下一次**删除+trim |
| `--set-sparse` 报需要 `--allow-unsafe` | WSL 版本要求显式确认 | 加 `--allow-unsafe` 参数 |
| 服务恢复后容器首次 start 失败（connection reset） | systemd 未就绪 | 等待 10 秒重试一次（本案例 F-030） |
| `podman system prune` 报 image in use | 容器引用镜像 | 先 `podman rm -af` 或直接 `podman rmi -af --force` |

## 反模式

| 反模式 | 后果 | 实证 |
|--------|------|------|
| ❌ 先 set-sparse 再 compact（双保险直觉） | compact 直接报错，白停一轮服务 | F-024 |
| ❌ 只停 wslservice 不停 vmcompute | vhdx 句柄仍被持有，compact 失败 | F-023 |
| ❌ 压缩窗口期并行会话操作 WSL | 句柄竞争，间歇性失败难排查 | F-029 |
| ❌ 删除数据后反复 fstrim 指望归还 | 已记账块二次 trim 无效果 | F-033 |
| ❌ 普通用户 du 排查 vhdx 内部占用 | root-only 目录不可见，严重低估（7.3GB vs 32GB） | F-006 |

## 实际案例

### 案例1：C盘 vhdx 治理（2026-08-28，正向完整应用）

- **场景**：C盘剩余 3.3GB 濒临耗尽；podman-machine-default vhdx 膨胀至 33.04GB（内部实际 11.93GB）
- **路径**：先误入相位A（sparse 转换成功但 fstrim 仅归还 0.1GB），后切相位B（清 sparse 标志 → 停 wslservice+vmcompute → diskpart compact）
- **结果**：32.31GB → **11.93GB**（回收 20.4GB），与内部用量完全一致；C盘剩余升至 73.79GB
- **教训**：踩中 sparse/compact 互斥坑（F-024）、vmcompute 句柄坑（F-023）、并行会话撞车坑（F-029）——均已转化为本 SOP 反模式与故障排查条目
- **来源**：[retrospective-c-drive-vhdx-recovery-20260828](../../reports/environment-setup/retrospective-c-drive-vhdx-recovery-20260828/README.md)

### 案例2：docker-cache-to-wsl-migration（2026-08-18，相关案例）

- **场景**：Docker 镜像缓存迁移至 WSL 过程中的 vhdx 处理
- **路径**：vhdx 迁移场景下对 sparse/compact 二相模型的部分应用
- **来源**：[retrospective-docker-cache-to-wsl-migration-20260818](../../reports/environment-setup/retrospective-docker-cache-to-wsl-migration-20260818/README.md)

## 迁移示例（跨场景）

同一"在线归还 ↔ 离线重写"二相模型适用于：

| 场景 | 在线相 | 离线相 |
|------|--------|--------|
| Hyper-V 代管虚拟机磁盘收缩 | sparse VHD + 客体内 trim | `Optimize-VHD -Path <vhdx> -Mode Full`（需停机） |
| Windows Dev Drive | ReFS 稀疏/trim 穿透 | 离线压缩工具 |
| Docker Desktop（WSL 后端） | sparse + `wsl --shrink` 在线回收 | 停 Docker Desktop 后 diskpart compact |
| 任何 NTFS 宿主 + 动态虚拟磁盘 | 宿主稀疏属性 | 宿主侧离线重写（qemu-img convert、`Optimize-VHD` 等） |

**本质**：虚拟磁盘文件"只增不减"，客体删除→元数据记账（TRIM）→物理回收，三步缺一不可；在线/离线两条回收路径互斥二选一。

## 失败案例（20260828 真实实证，防成功偏误）

| # | 失败尝试 | 报错/现象 | 教训 |
|---|---------|-----------|------|
| 1 | 只跑 fstrim 指望回收 21GB | trimmed 声明 967GiB，宿主归还 0.1GB | TRIM 是元数据记账，物理回收必须 compact 或 sparse 穿透 |
| 2 | 转 sparse 后再跑 fstrim | 仅归还 0.1GB | sparse 只对**转换后新产生**的 TRIM 生效，存量空洞不归还 |
| 3 | 停 wslservice 后直接 compact | 「文件被另一程序使用」 | vmcompute 也持有句柄，必须两个服务都停 |
| 4 | 双服务全停后 compact | 「文件不能是稀疏文件」 | sparse 属性与 compact 互斥，需先 fsutil 清标志 |
| 5 | 压缩窗口期间另一会话 podman machine start | 句柄竞争，第一次压缩失败 | 压缩期间必须独占，禁止并行 WSL 操作 |

> 五次失败均发生在同一次治理任务中——本 SOP 的每个步骤都是踩坑后修正的结果，不是先验设计。

## 不适用/反目标/边界场景（≥3类，防确认偏误）

| 类别 | 场景 | 不适用原因 |
|------|------|-----------|
| 反目标1 | vhdx 大小 ≈ 内部用量（差值 <5GB） | 无空洞可回收，compact 收益趋近于零，停机成本反而为负收益 |
| 反目标2 | 系统盘空间充裕（剩余 >20%） | 收益低于停机与操作风险，建议等空间紧张时再治理 |
| 反目标3 | 共享/生产 WSL 环境（多人同时使用） | 相位B需要全量 shutdown + 服务停止，影响所有用户；应改用相位A或变更窗口执行 |
| 边界1 | vhdx 含未提交的容器现场（运行中任务） | shutdown 会中断任务，需先等任务完成或确认可中断 |
| 边界2 | WSL 旧版本（无 --manage --set-sparse） | 相位A不可用，只能走相位B |
| 边界3 | BitLocker/加密卷上的 vhdx | compact 行为未验证，建议先快照再操作 |

## 早期预警信号（≥5个）

| 信号 | 判定阈值 | 含义 |
|------|---------|------|
| 系统盘剩余 <10% | Windows 开始告警 | 立即排查 vhdx 占用 |
| `podman system df` 容器可写层 >10GB | 嵌套构建嫌疑 | 容器内有隐形写入（嵌套引擎/构建缓存） |
| vhdx 逻辑大小 - 内部 df 用量 >5GB | 空洞率 >15% | 值得走本 SOP 回收 |
| 压缩后 vhdx 快速回升 | 一个月内回到压缩前水位 | 存在持续写入源（日志/缓存未外置），需治本而非反复压缩 |
| 删除镜像后 C盘剩余不变 | prune 前后无差异 | TRIM 记账未物理回收，走相位B |

## 关联文档

- 复盘报告：[retrospective-c-drive-vhdx-recovery-20260828](../../reports/environment-setup/retrospective-c-drive-vhdx-recovery-20260828/README.md)
- 模板：[ops-sop-standard-template.md](ops-sop-standard-template.md)
- 相关约定：`.wslconfig` 中 `vmIdleTimeout=-1` 防自动关机（项目记忆）
