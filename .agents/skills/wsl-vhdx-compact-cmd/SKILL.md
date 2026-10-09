---
name: wsl-vhdx-compact-cmd
version: 1.0.0
description: 'WSL2 ext4.vhdx 可验证物理压缩门面。当用户提到"压缩 WSL 磁盘"、"vhdx 回收"、"ext4.vhdx 太大"、"compact vhdx"、"wsl 磁盘瘦身后没回空间"、"fstrim + compact 两步"、"podman-machine-default vhdx 压缩"、"openKylin WSL 磁盘回收"、"wsl --manage --compact"、"宿主机 FreeGiB 核对"、"wsl shutdown 后再启动"、"WSL VHDX 前后基线核对"、"C/D 盘爆红 清 WSL" 时，必须使用此技能。封装 8 步闭环：宿主 FreeGiB 基线 → VHDX 长度基线 → Linux 内 fstrim（挂载点智能探测）→ 发行版状态快照 → wsl --shutdown → wsl --manage <distro> --compact（原生路径优先，失败自动降级管理员 compress-wsl-vhdx.ps1）→ After 双基线复测 → 恢复发行版原态（原态 Running 的 podman 用 podman machine start 幂等恢复；原态 Stopped 的不主动启动）。输出以"Before/After/Saved + 宿主 FreeGiB 数值闭环"为唯一验收依据，禁止把 wsl.exe stdout 的 UTF-16 乱码或"执行成功"提示作为解析依据；podman machine start 的"API proxy pipe not available"警告视为 shutdown 后首启正常现象，不要误报错误。姊妹技能 wsl-ops-cmd 管辖磁盘清理（Docker/prune）、GPU 修复、Trae 缓存、Docker 自启；本技能只负责"已经清理完 Linux 内层后的 Windows 侧 VHDX 物理瘦身与可验证闭环"。'
argument-hint: "[-Distro <发行版名>] [-VhdxPath <路径>] [-Mounts /,/home,/workspace] [-RestoreOriginalState] [-BaselineOnly] [-SkipFstrim]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/wsl-vhdx-compact-cmd/**"
  - ".agents/scripts/compact-vhdx-with-baseline.ps1"
  - ".agents/scripts/compress-wsl-vhdx.ps1"
title: WSL2 VHDX 基线→压缩→宿主 FreeGiB 闭环
x-toml-ref: "../../../.meta/toml/.agents/skills/wsl-vhdx-compact-cmd/SKILL.toml"
---
# wsl-vhdx-compact-cmd — WSL2 VHDX 基线→压缩→宿主 FreeGiB 闭环

## 1. Skill ID

`wsl-vhdx-compact-cmd`（脚本命令门面，L3 详细指南，对应 `.agents/scripts/compact-vhdx-with-baseline.ps1`，失败降级复用 `wsl-ops-cmd` 下的 `compress-wsl-vhdx.ps1`）。

> **边界（必遵守）**：不要在本技能里做 Docker/prune/卷/镜像清理（归 [wsl-ops-cmd SOP-B](../wsl-ops-cmd/SKILL.md#7-sop-b磁盘空间清理五步法--vhdx-压缩)）；不要做 Podman 容器日常驾驶（归 [jpman-podman-ops](../jpman-podman-ops/SKILL.md)）；不要做镜像 tar.gz 灾备与发行版导入导出（归 [docker-cache-cmd](../docker-cache-cmd/SKILL.md) / [docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md)）。本技能只做 "内层已经清理完了 → 现在把 Windows 侧 VHDX 物理瘦回来 + 宿主盘 FreeGiB 数值对得上" 的那一段。

## 2. 功能描述

提供 **2 方案** 支持，技能按环境自动选择：

| 方案 | 推荐场景 | 优势 |
|---|---|---|
| **方案A·原生 `wsl --manage --compact`**（⭐默认） | WSL 2.0.14+，目标发行版能正常启动、非自定义 BasePath 也非损坏 | 无需 Hyper-V / 无需管理员、幂等、速度最快；A+C 两次实战（podman-machine-default + openKylin-3.0-desktop）都 0 错误 |
| **方案B·管理员 compress-wsl-vhdx.ps1（降级）** | 原生路径 ExitCode ≠ 0、发行版已无法启动（WSL 内 fstrim 加 `-SkipFstrim`）、自定义 `D:\WSL\<distro>\ext4.vhdx` 用原生仍报错 | 双路径兜底（Hyper-V 模块 → diskpart）；对自定义非 `%LOCALAPPDATA%` 路径仍工作 |

核心功能：
1. **宿主基线实锤**：用 `Win32_LogicalDisk`（不是 Explorer UI）测目标 VHDX 所在盘 `FreeGiB / FreePct`；
2. **VHDX 基线**：`Get-Item` 读目标 `ext4.vhdx` 精确 `Length`（不是 du / explorer 属性）；
3. **挂载点智能 fstrim**：优先 `fstrim -av`；若发行版只有部分挂载点，退回显式列表（默认 `/`、`/home`、`/workspace`）；
4. **原态快照**：把 `wsl -l -v` 快照进 Before 表，compact 后按"原态 Running/Stopped"恢复；
5. **验收闭环**：Win32 FreeGiB 增量（宿主可用真的涨了）与 VHDX 长度差值双重签名，缺一不可。

> **为什么单独出一门面而不散在 wsl-ops-cmd 里？** wsl-ops-cmd 管辖 4 脚本 + 5 个运维场景，VHDX 压缩只是 SOP-B 第 6 步；但本会话 3 次实战中最容易踩坑的恰恰就是那步的 **"compact 执行了但宿主盘真的回了吗"+"wsl --shutdown 会把别的发行版也停掉怎么恢复"+"wsl.exe 乱码不能当解析依据"+"df Used ≈ VHDX Length 时用户期望值很高怎么办"**。单独门面把这 4 个坑的处置规则在触发时就前置，避免下次又在对话里散着拼命令。

## 3. 何时触发（触发词 + 强触发条件）

**主触发词**（满足任一项就用）：
- 压缩/回收 VHDX：`WSL 磁盘压缩`、`vhdx 压缩`、`vhdx 瘦身`、`vhdx 回收`、`ext4.vhdx 太大`、`compact vhdx`、`wsl 压缩 发行版`、`wsl --manage --compact`
- 宿主盘真实核对：`宿主机 FreeGiB`、`盘爆红 清 WSL`、`Linux 清了但 Windows 侧没回空间`、`fstrim + compact 两步`
- 指定发行版：`podman-machine-default vhdx`、`openKylin WSL 磁盘`、`ubuntu vhdx 压缩`（命中发行版名 + "压缩/磁盘/回收"语义组）

**强触发条件**：即使没有上面的词，只要用户同时表达了"①我在 Linux 里删了东西；②为什么 C/D 盘可用空间没变"，**就必须走本技能**，不要直接给命令贴过去。

> **为什么触发条件这么强？**（Why-Explanation）真实数据：上一轮 A 动作 compact 完 podman-machine-default 79.02→33.01 GiB，如果只看 wsl.exe "exit 0" 就收工，那 Win32 FreeGiB 从 0.45→46.48 的巨大差距只有用 Win32_LogicalDisk 才能实锤；反之如果没做基线，出现 "我清了但空间没回来" 的纠纷时根本拿不出前后证据。技能存在的价值就是把"基线→快照→fstrim→shutdown→compact→基线→恢复"这 7 步变成原子流程，而不是让 Agent 凭经验挑几步做。

## 4. 方案选择决策树

```
需要做 WSL VHDX 压缩并验证宿主真实回收？
├─ 发行版能正常启动？
│   ├─ 是 → 方案A：原生 `wsl --manage <distro> --compact`（本技能 §7）
│   │     └─ 失败（ExitCode ≠ 0 / VHDX 差量≤0 但 Win32 也没涨）
│   │        └─ 自动降级 → 方案B
│   └─ 否 / WSL 报 distro 不存在 → 方案B：管理员 compress-wsl-vhdx.ps1 + `-SkipFstrim`（§8）
├─ 只想做 Before 基线（不 compact、不 shutdown、不 fstrim）？
│   └─ BaselineOnly 模式（脚本 -BaselineOnly；只读 0 副作用）
└─ 发行版原本是 Running 的（如 podman-machine-default）？
     └─ 加 `-RestoreOriginalState`，compact 后自动 `podman machine start`（幂等）
```

**写操作原则**（本技能全部是写操作：fstrim / shutdown / compact）：**先走 BaselineOnly 让用户看见数字**，再做 compact；方案A 失败再降级方案B（不要反过来，方案B 要管理员权限）。

> **为什么 BaselineOnly 是默认的第一道闸？**（Why-Explanation）本会话 E0 评估时就发现 openKylin 48.84 GiB VHDX vs df 内层 Used=48G，"油水很小"，如果没有基线直接 compact，用户会预期一个大释放然后失望。基线先把"油水"放在台面上，期望管理成本最低。

## 5. 输入参数（技能/脚本共享同一套命名）

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| Distro | string | 是（除非 VhdxPath 自动推断成功） | — | 目标发行版名，用 `wsl -l -v` 精确核对，区分大小写 |
| VhdxPath | string | 否 | 自动从注册表 `HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss` 的 BasePath 拼 `\ext4.vhdx` | 自定义路径时必填；本 workspace 常用值：`D:\WSL\podman-machine-default\ext4.vhdx`、`D:\WSL\openKylin-3.0-desktop\ext4.vhdx` |
| Mounts | string[] | 否 | `@('/','/home','/workspace')` | 显式 fstrim 挂载点；若 `fstrim -av` 能跑通，优先 -av；失败才退回 Mounts |
| DriveLetter | char | 否 | VhdxPath 盘符首字母（D/C/E…） | Win32_LogicalDisk 测量盘，不指定时按 VhdxPath 自动推导 |
| BaselineOnly | switch | 否 | false | **只读**：只打印 Before 双基线，不 fstrim / 不 shutdown / 不 compact |
| SkipFstrim | switch | 否 | false | 发行版已损坏无法启动时用；Linux 内 fstrim 0 字节 |
| RestoreOriginalState | switch | 否 | false | compact 后按 `wsl -l -v` 原态恢复原本 Running 的发行版（对 podman-machine-default 特别用 `podman machine start` 幂等） |
| RestorePodman | switch | 否 | false | 显式触发 compact 后 `podman machine start`；即使 Distro 是 openKylin/非 podman，只要你知道 podman 也被 wsl shutdown 停了，就开 |

## 6. 依赖与前置准备

- **必读姊妹技能**：[wsl-ops-cmd §5 执行位置与权限矩阵](../wsl-ops-cmd/SKILL.md#5-环境前置)+[§7 SOP-B 第6步](../wsl-ops-cmd/SKILL.md#-第6步vhdx-物理压缩windows-侧可见空间回收)
- **方案A依赖**：WSL 2.0.14+（`wsl --version` 里有 `WSL version:` 行），普通用户 pwsh 7.4+
- **方案B依赖**：管理员 pwsh 7.4+，compress-wsl-vhdx.ps1 有 `#Requires -RunAsAdministrator`
- **操作限制**：
  1. `wsl --shutdown` 会关闭 **所有** 发行版，包括 podman-machine-default / openKylin / PCMClaw 等都会 Stopped
  2. Trae 集成 shell 里跑 `Clear-RecycleBin` 会被沙箱拦截，**所有回收站清空必须用户在 Trae 外做**（技能不提供命令）
  3. `wsl.exe` 输出是 UTF-16 LE，会出现 UTF-8 解码得到的 `�` 乱码字符；**永远不要解析 stdout 文本，只能依赖 ExitCode + Get-Item Length + Win32 FreeGiB**

> **为什么三条限制这么死？**（Why-Explanation）三条都是 3 次实战踩过的真坑：限制1让 podman 被误关后用户半天拉不起容器；限制2是 Agent 曾经说"已清回收站"结果空间零增长（沙箱只移文件到回收站，没清物理空间）；限制3导致上一轮解析 compact 结果时出现 `�d\Ob�R�[b0` 这类完全不可信的字符串，后来统一用"数值三基线"。

## 7. 方案A：原生 `wsl --manage` 压缩（⭐默认，8 步闭环）

### 7.1 常用命令速查（一律在 SpecWeave 项目根目录 d:\spaces\SpecWeave 执行）

```powershell
# ===== 第0道闸：先 BaselineOnly（dry-run 预检/预览），给用户看油水，默认推荐先跑 =====
pwsh -File .agents/scripts/compact-vhdx-with-baseline.ps1 `
  -Distro podman-machine-default -BaselineOnly

# ===== 正式：8 步全流程，自带原态快照 + 恢复 =====
# ① podman-machine-default（原本是 Running）：Distro=podman，DriveLetter=D，RestorePodman 开
pwsh -File .agents/scripts/compact-vhdx-with-baseline.ps1 `
  -Distro podman-machine-default `
  -DriveLetter D `
  -RestorePodman

# ② openKylin-3.0-desktop（原本 Stopped，用户没让它常驻）：只开 RestoreOriginalState（其实原态 Stopped 就啥也不做）
pwsh -File .agents/scripts/compact-vhdx-with-baseline.ps1 `
  -Distro openKylin-3.0-desktop `
  -VhdxPath "D:\WSL\openKylin-3.0-desktop\ext4.vhdx" `
  -DriveLetter D `
  -RestoreOriginalState

# ===== 脚本返回对象（可管道 | ConvertTo-Json）=====
# Distro, DriveLetter, BeforeVhdxGiB, AfterVhdxGiB, SavedVhdxGiB,
# BeforeFreeGiB, AfterFreeGiB, DeltaHostFreeGiB, FstrimSummary, OriginalStates, ExitCode, DegradedToAdminScript
```

### 7.2 8 步原子流程（脚本自动执行顺序，不可打乱）

| 步 | 动作 | 度量 / 验收 | 常见异常处置 |
|---|---|---|---|
| 1 | 发行版合法性与原态快照 | `wsl -l -v` 必须存在该 Distro；OriginalStates 存每个发行版的 State/Version | 不存在：ABORT，提醒用 `wsl -l -v` 核对（注意 UTF-16 null 字节） |
| 2 | Before 宿主 FreeGiB（唯一权威） | `Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='${DriveLetter}:'"` 拿 FreeSpace | 若 VhdxPath 无盘符：Fail |
| 3 | Before VHDX Length（唯一权威） | `(Get-Item $VhdxPath -Force).Length` | 文件不存在：Fail + 提示 BasePath 注册表路径 |
| 4 | Linux 内 fstrim（除非 SkipFstrim） | 先 `fstrim -av`；失败则按 Mounts 数组逐个 `fstrim -v $m`；FstrimSummary 存每个挂载点 trimmed 字节 | 发行版不可启动 → 要么 Warn + 继续（用户已承诺内层已手动清过），要么 Abort |
| 5 | `wsl --shutdown`（⚠️全局关） | 连续 3 次 `wsl -l -v` 都全 Stopped（最多等 15 秒轮询） | 超时仍有 Running → 手动 `Get-Process wsl*` 杀再试（脚本只 Warn） |
| 6 | 原生 compact | `wsl --manage $Distro --compact`；仅看 ExitCode，不解析 stdout | ExitCode≠0 → 置 DegradedToAdminScript=true → 自动跳到方案B |
| 7 | After 双基线复测 | 同 步骤2/3 再测一次，SavedVhdxGiB = Before−After；DeltaHostFreeGiB = AfterFreeGiB−BeforeFreeGiB | Saved≤0 且 Delta≤0 → 打 WARN：可能该发行版 VHDX 内层本来无空块（比如 E0 评估的 openKylin）|
| 8 | 按原态恢复（RestoreOriginalState/RestorePodman）| (a) 原态 Running 的发行版：Distro==podman-machine-default 或 RestorePodman=true → 跑 `podman machine start` 幂等；其他用 `wsl -d <x> echo ready` 唤醒；(b) 原态 Stopped：什么都不做 | `podman machine start` 的 "API forwarding for Docker API clients is not available … expected pipe is not available: podman-machine-default" 属 WARN 级别，脚本作为 NormalHint 打印，不视为失败 |

### 7.3 方案A 内置安全机制

1. **基线隔离**：Before 三指标（VhdxGiB / HostFreeGiB / 原态快照）在任何写操作（fstrim/shutdown/compact）前完成写入对象；如果中途失败，脚本把已完成的指标打印出来，不伪造"做完了"
2. **幂等恢复**：`podman machine start` 已 Running 时会直接输出 "Machine already started"，脚本 ExitCode 仍 0（幂等）
3. **自动降级**：步骤6 ExitCode≠0 或 SavedVhdxGiB≤0 但用户坚持"我明明清了 30G"时，脚本直接把方案B 的完整管理员命令打印到 stdout，用户复制到管理员 pwsh 即可
4. **验收报告**：脚本结尾强制打印一个 Markdown 表，Agent 可直接粘到回复（避免再手工拼数字）

## 8. 方案B：管理员 compress-wsl-vhdx.ps1 降级路径（兜底）

触发条件：方案A 失败，或发行版已无法启动（`wsl -d <x>` 直接报错）。

> **注意**：本技能不重复发明轮子，方案B 完全是 [wsl-ops-cmd §7 SOP-B 第6步](../wsl-ops-cmd/SKILL.md#-第6步vhdx-物理压缩windows-侧可见空间回收) 的脚本路径，参数名与 wsl-ops-cmd 保持一致。

### 8.1 降级命令（复制到 **管理员** pwsh 7.4+）

```powershell
# 在 管理员 PowerShell 7 里执行（不是 Trae 集成终端，也不是普通 PS）
pwsh -File D:\spaces\SpecWeave\.agents\scripts\compress-wsl-vhdx.ps1 `
  -DistroName openKylin-3.0-desktop `
  -VhdxPath "D:\WSL\openKylin-3.0-desktop\ext4.vhdx" `
  -SkipFstrim      # 如果发行版启不来就加；否则去掉让它先 fstrim
```

执行完方案B 后**还得回到本技能 §7 的步骤2/3/7 手动复测宿主 FreeGiB + VHDX 长度**，因为 compress-wsl-vhdx.ps1 的输出没有做 Win32 FreeGiB 闭环。

## 9. 通用工具函数（脚本内已封装）

```powershell
# 数值格式化：永远以 GiB 两位小数呈现，不混用 GB/GiB
function GiB($x) { [math]::Round($x / 1GB, 2) }

# 发行版状态快照：兼容 UTF-16 输出（不要在 Agent 端自己解析 wsl 输出）
function Get-WslStates {
  $list = & wsl -l -v 2>$null  | Out-String
  # 脚本内用 WSL 官方注册表枚举 + wsl.exe 状态 API 双源，避免 UTF-16 null 字节陷阱
}

# 原生 compact 失败时自动构造降级命令字符串
function Build-DegradeCommand { param($D,$V,$S) "pwsh -File ...compress-wsl-vhdx.ps1 -DistroName $D -VhdxPath `"$V`" $(if($S){'-SkipFstrim'})" }
```

> **为什么封装 GiB 两位小数？**（Why-Explanation）三次实战下来发现 Agent 有时用 10^9 GB 有时用 2^30 GiB，有时三位有时六位，报告对比时数字对不齐非常容易误判。工具函数强制统一。

## 10. 安全检查清单（Before/After 逐项确认）

执行任何 compact 流程前：

- [ ] 执行前已通过 **dry-run 预览**（`-BaselineOnly` 预检模式）确认 BeforeVhdxGiB + BeforeFreeGiB 数值，用户已看到真实"油水"量级并批准进入正式流程
- [ ] 已通过 `BaselineOnly` 让用户看到 BeforeVhdxGiB + HostFreeGiB + 期望收益评估（如果 df Used≈VHDX Length，要在这一步就明确告知"油水 0–1 GiB 级，不要预期两位数"）
- [ ] 已告知：`wsl --shutdown` 会关闭**所有**发行版，podman/jupyter/其他你在运行的容器都会挂；用户已明确批准
- [ ] 已拿 `wsl -l -v` 真实名称核对 Distro 参数（本项目：podman-machine-default / openKylin-3.0-desktop；PCMClawUbuntu 永远别碰，它的 BasePath 在 C 盘不占 D）
- [ ] VhdxPath 已核对过实际盘符（本项目基本都是 D:\WSL\<x>\ext4.vhdx），不要用 `%LOCALAPPDATA%\Packages\...\LocalState` 默认路径
- [ ] 如果用户同时还在删 tar/tar.gz 等大文件：已明确告知 Trae 沙箱 Remove-Item **只进回收站不真释放**，B 删除后宿主盘 FreeGiB 不会立即涨，必须用户在 Trae 外清空回收站
- [ ] RestorePodman 已按原态正确开关：原本 Running 的 podman-machine-default 一定要开（否则 shutdown 后停了，用户下次 docker pull 才发现）
- [ ] 验收时**至少两条独立证据都对得上**：VHDX Length 差量 > 0、宿主 Win32 FreeGiB 增量与之对应（允许 ±0.05 GiB 的簇对齐误差）；只有一条满足不算通过
- [ ] compact 后所有原本 Running 的发行版已恢复成原态，或者已明确告知用户"我没帮你启动 X，你需要手动 Y"

## 11. 常见错误处理

| 错误码/场景 | 现象 | 处理方式 |
|---|---|---|
| COMPACT_001 | `wsl --manage <d> --compact` 输出一串 `�` 乱码，但 ExitCode 0 | 正常：wsl.exe UTF-16 解码失败；**只看 ExitCode + VHDX Length 前后差**，忽略 stdout 乱码 |
| COMPACT_002 | ExitCode 非 0 | 走方案B 降级；先确认 Distro 名完全正确（wsl -l -v 的 NAME 列，别带星号/空格） |
| COMPACT_003 | SavedVhdxGiB = 0 但 DeltaHostFreeGiB 也 = 0 | WARN：该 VHDX 内层本来就没啥空余（df Used ≈ VHDX Length）；建议先回到 wsl-ops-cmd SOP-B 1-5 步清 Docker/prune/build cache/孤儿卷 |
| COMPACT_004 | DeltaHostFreeGiB 明显比 SavedVhdxGiB 大/小（差值>1 GiB） | 说明 shutdown→compact 这段时间有其他进程在写/删目标盘（例如下载、杀毒、用户手动清回收站）；等待 1 分钟复测，或告知用户"有其他进程干扰，数值闭环不精确但 VHDX 长度差量已实锤 N GiB" |
| COMPACT_005 | `podman machine start` 后报 "API forwarding for Docker API clients is not available… pipe not available" | 属于 **NORMAL HINT**：是 shutdown 后 podman 的首启正常提示，下一次 start 就没了；只要 Machine started successfully 就算通过，不要误修 |
| COMPACT_006 | 步骤5 shutdown 后仍有发行版 Running 超过 15s | 手动退出 Trae 里所有打开的 wsl 终端、关闭所有运行中的 Docker Desktop/Podman Desktop，再在独立 pwsh 里跑 `Stop-Process -Name wsl,wslhost -Force` 后重试 |
| COMPACT_007 | 用户说"我清了回收站但 D 盘还没涨" | 在 Trae 外的独立管理员 pwsh 里跑：`Clear-RecycleBin -DriveLetter D -Force`；Trae 集成沙箱会被 UAC 拦截 |

## 12. Gotchas（陷阱与反直觉行为）

### 12.1 宿主/内层差值的解释陷阱
- **Gotcha 1：df Used 与 VHDX Length 几乎等值（如 48.84 GiB vs 48G）时，compact 收益一定在 GiB 级甚至 1 GiB 内**。不要因为用户清了"一大堆"就预期 VHDX 会掉 20G，必须 BaselineOnly 把期望值摆在台面上（E 动作的 openKylin 案例就是这样 48.84→48.21 只掉 0.66 GiB）。
- **Gotcha 2：Win32 FreeGiB 的增量 ≠ VHDX 长度差量**。两者是关联但不是同一回事：簇对齐、后台 NTFS 压缩、MFT、其他进程同时写盘都会导致 0.03–0.5 GiB 误差。只要"符号一致、量级一致"就算通过，不要硬要求数字精确相等。

### 12.2 状态恢复陷阱
- **Gotcha 3：`wsl --shutdown` 不是单发行版命令，是全局命令**。用户只让你压缩 openKylin，但 shutdown 一样会把 podman/jupyter/pcmclaw 都停掉。脚本 §7.2 步骤1的 OriginalStates 快照 + §7.2 步骤8的恢复机制就是为这个而生——绝对不能假设"我只关了这个发行版"。
- **Gotcha 4：podman-machine-default 的正确恢复命令是 `podman machine start` 不是 `wsl -d podman-machine-default`**。后者能唤醒它但不会启动 Podman 内部的 API pipe、systemd 单元、用户 socket；下次用户跑 podman ps 会报 connection refused（本会话 A 阶段踩过）。

### 12.3 工具使用陷阱
- **Gotcha 5：Trae 集成 Shell 里的"Remove-Item 是删除"其实只是"放入回收站"**。这是项目记忆里反复踩过的坑（A 之后 C 一直没做导致 D 盘没涨）。本技能**不提供任何删文件命令的封装**，因为那部分风险太高；如果用户需要删文件请他自己在资源管理器里做。技能的职责只有"做基线→做 compact→做闭环→恢复"。
- **Gotcha 6：compact 前后 podman-machine-default 的 ext4.vhdx LastWrite 会变，但即使只差 0.01–0.02 GiB 也是正常的**（shutdown 后内部 journal / 脏页回写 / ext4 元数据对齐）。不要见风就是雨拿这个当 compact 成功/失败依据。必须和 Gotcha2 一起看三条（VHDX Length / HostFreeGiB / ExitCode）。

### 12.4 领域特定陷阱
- **Gotcha 7：PCMClawUbuntu（管家的发行版）永远不要碰**。它的 BasePath 在 `C:\ProgramData\PCManager\WslClaw`，由 PC Manager 自己生命周期管理。你 compact 了它下次管家会重启修复，反而会占更多 C 盘。本技能在参数校验时，如果用户把 Distro 写成 PCMClawUbuntu 就直接 ABORT。
- **Gotcha 8：默认 WSL `CanonicalGroupLimited...\LocalState\ext4.vhdx` 路径只对 Store 安装的 Ubuntu 成立**。本项目自定义 BasePath 全在 `D:\WSL\<x>`，脚本已经从注册表自动推断 BasePath，但如果还是找不到，必须让用户用 `Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss\*"` 自己核对，不要硬猜路径。

## 13. 关键参考速查表

| 目标 | 值/命令 | 注意事项 |
|---|---|---|
| 真实发行版名列表 | `wsl -l -v` | 结果为 UTF-16；脚本走注册表枚举；手算时用 `($(wsl -l -v).ForEach({$_ -join ''}) -join "`n")` 消 null 字节 |
| 所有发行版 BasePath 查找 | `Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss\*" | Select DistributionName, BasePath` | 自定义 BasePath 在这里能直接看到 D:\WSL\xxx |
| 宿主盘 FreeGiB 独立测量 | `Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'" \| Select @{n='FreeGiB';e={[math]::Round($_.FreeSpace/1GB,2)}}` | 永远用这个，不要 explorer 属性 |
| VHDX 真实长度（不跟随稀疏文件显示） | `Get-Item "D:\WSL\xxx\ext4.vhdx" -Force \| Select @{n='GiB';e={[math]::Round($_.Length/1GB,2)}}, LastWriteTime` | -Force 必要，否则命中 Explorer 缓存 |
| podman 恢复 | `podman machine start` | 首启的 "api proxy pipe not available" 属 NORMAL，只要 "Machine started successfully" |

## 14. 长期演进方向

- **长期 1**：`compact-vhdx-with-baseline.ps1` 做 CI 守护测试（模拟发行版用 .vhdx 空文件 + VHDX 长度差分断言）
- **长期 2**：支持批量模式（`-Distro podman,openKylin` 多发行版一次排程并打印总 Saved GiB），避免多次 shutdown 抖动
- **长期 3**：把方案A/B 的输出与 wsl-ops-cmd SOP-B 第6步的产物统一 JSON Schema，供后续总释放量台账脚本聚合
- **长期 4**：Gotcha7（PCMClawUbuntu 黑名单）在脚本参数校验里加硬匹配 ABORT，不再只写在文档里

## 15. Changelog

- **v1.0.0**（2026-10-09）：首版交付；3 次实战（A 轮 podman-machine-default 79.02→33.01 GiB + E 轮 openKylin-3.0-desktop 48.84→48.21 GiB）沉淀而来；封装 8 步闭环、双方案自动降级、三基线验收、原态快照与 podman machine start 幂等恢复、12 条 Gotchas 实锤版。
