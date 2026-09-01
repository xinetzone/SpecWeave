---
name: wsl-ops-cmd
version: 1.0.0
description: 'WSL2 主机层运维（磁盘/GPU/Docker自启/IDE缓存）技能门面。当用户提到"WSL磁盘空间不足"、"ext4.vhdx压缩"、"C/D盘爆红"、"Docker清理/prune/孤儿卷/build cache爆满"、"WSL Docker GPU不可用"、"--gpus all报错"、"could not select device driver"、"nvidia-smi"、"nvidia-container-toolkit"、"wsl --shutdown后Docker不自启"、"wsl.conf boot配置"、"setsid dockerd"、"Trae缓存清理/索引重建"、"fstrim"、"WSL发行版维护"时，必须使用此技能。封装4个成熟脚本（compress-wsl-vhdx/Restart-WslDockerGpu/setup-wsl-docker-gpu/cleanup-trae-cache）与两套L2/L1模式（存储清理五步法、GPU三层分诊），提供跨Shell安全铁律与分层诊断SOP。不要手动凭Docker桌面版经验操作WSL原生Docker——本技能封装了三层Shell陷阱、保护带红线与幂等修复路径。'
argument-hint: "[WSL运维任务：GPU分诊|磁盘清理|VHDX压缩|Docker自启|Trae缓存]"
user-invocable: true
paths:
  - ".agents/skills/wsl-ops-cmd/**"
  - ".agents/scripts/compress-wsl-vhdx.ps1"
  - ".agents/scripts/Restart-WslDockerGpu.ps1"
  - ".agents/scripts/setup-wsl-docker-gpu.sh"
  - ".agents/scripts/cleanup-trae-cache.ps1"
title: WSL2 主机层运维（GPU/磁盘/Docker自启/缓存）
x-toml-ref: "../../../.meta/toml/.agents/skills/wsl-ops-cmd/SKILL.toml"
---
# wsl-ops-cmd — WSL2 主机层运维技能门面

## 1. Skill ID

`wsl-ops-cmd`（脚本命令门面；封装 `.agents/scripts/` 下 4 个 WSL 维护脚本 + 两套已验证模式）

## 2. 功能描述

本技能覆盖 **WSL2 主机层** 四大运维场景：

| 场景 | 核心脚本/模式 | 典型收益 |
|---|---|---|
| Docker GPU 三层分诊修复 | `Restart-WslDockerGpu.ps1` + `setup-wsl-docker-gpu.sh` | 5 分钟定位 L1/L2/L3 失败层，幂等修复 |
| Docker 存储清理五步法 | 模式 `wsl-docker-storage-cleanup-five-step-method`（L2-validated，3 案例） | 案例回收 160GB，活跃容器零损伤 |
| VHDX 物理压缩 | `compress-wsl-vhdx.ps1` | Linux 内释放后 Windows 侧真正回收磁盘 |
| Trae IDE 缓存清理 | `cleanup-trae-cache.ps1` | 安全释放索引/缓存（设置与记录受保护） |

**姊妹技能边界（路由互链，禁止重复封装）**：

| 技能 | 职责 | 本技能不覆盖 |
|---|---|---|
| [jpman-podman-ops](../jpman-podman-ops/SKILL.md) | Podman 容器日常驾驶（jpman start/stop/machine ssh/保活） | podman machine、容器生命周期 |
| [docker-cache-cmd](../docker-cache-cmd/SKILL.md) | Docker 镜像 tar.gz 灾备缓存（save/load） | 镜像归档备份 |
| [docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md) | 镜像→WSL 发行版转换（wsl --import/export，含 `restore-wsl-from-cache.ps1`） | 发行版导入导出 |
| 本技能 wsl-ops-cmd | WSL 主机层：GPU/磁盘/Docker 自启/IDE 缓存 | — |

> **为什么需要独立门面而不是把命令散在对话里？** WSL 运维的事故率不来自命令本身，而来自三层 Shell 跨界（PowerShell↔wsl.exe↔bash）的解析陷阱、daemon 不可达时的跳跃结论、以及保护带误删。两个真实案例中"已清理 80GB"实际回收 0 字节——命令"没报错"不等于执行了。门面把这些铁律前置到触发时刻。

## 3. 何时触发

**主触发词**：
- WSL 磁盘空间：`WSL磁盘满`、`C/D盘爆红`、`ext4.vhdx 太大`、`vhdx压缩`、`fstrim`、`docker system df`、`build cache 爆满`、`孤儿卷`、`prune`、`清理WSL废弃容器镜像`
- Docker GPU：`--gpus all 报错`、`could not select device driver`、`capabilities: [[gpu]]`、`nvidia-smi`、`nvidia-container-toolkit`、`nvidia-ctk`、`容器内看不到GPU`、`WSL GPU直通`
- Docker 自启：`wsl --shutdown 后 Docker 没了`、`wsl.conf boot`、`dockerd 不自启`、`setsid`、`containerd 启动`
- IDE 缓存：`Trae 缓存清理`、`Trae 占空间`、`.ckg 索引`、`清理 Trae CN/SOLO/Qoder 缓存`

**不触发**：Podman 容器日常操作（→ jpman-podman-ops）；镜像灾备与 WSL 发行版导入导出（→ docker-cache-cmd / docker-wsl-bridge-cmd）；生产 K8s/Swarm 集群清理（禁止手动脚本化）。

## 4. 任务路由决策树

```
用户的WSL运维诉求是什么？
├─ 磁盘空间不足（盘爆红/vhdx膨胀）
│   ├─ 空间被Docker占用（docker system df 可查）→ SOP-B 五步法清理 → 收尾接 VHDX 压缩
│   ├─ 空间被Trae IDE缓存占用 → SOP-D cleanup-trae-cache.ps1（先 -DryRun）
│   └─ Linux内已清理但Windows侧空间没回来 → SOP-B 第6步 compress-wsl-vhdx.ps1
├─ Docker GPU 问题（--gpus报错/容器内无GPU）
│   └─ SOP-A：先 -Diagnose 三层诊断 → 按失败层修复 → Restart 重启验证
├─ wsl --shutdown/重启后Docker不自启
│   └─ SOP-C：wsl.conf [boot] 持久化 + setsid 进程启动（setup.sh 幂等全自动）
└─ 诉求其实是容器/镜像层？
    ├─ Podman容器起停/进入 → jpman-podman-ops
    └─ 镜像备份/转WSL发行版 → docker-cache-cmd / docker-wsl-bridge-cmd
```

## 5. 环境前置

> **执行目录约定**：下文 Windows 命令中的相对路径 `.agents/scripts/...` 均以 **SpecWeave 项目根**为当前目录；在其他目录执行时改用完整路径。脚本参数可能随版本演进，执行前可用 `Get-Help .agents/scripts/<脚本>.ps1` 或 `bash setup-wsl-docker-gpu.sh --help` 核对当前实际参数。

### 5.1 执行位置与权限矩阵（用错位置是第一类错误）

| 脚本 | 在哪运行 | 权限 | PowerShell 版本 |
|---|---|---|---|
| `Restart-WslDockerGpu.ps1` | Windows PowerShell | 普通用户 | **5.1 兼容**（PWSH7-EXEMPT 有意设计） |
| `cleanup-trae-cache.ps1` | Windows PowerShell | 普通用户 | pwsh 7.4+（脚本自校验，不符给 winget 安装提示） |
| `compress-wsl-vhdx.ps1` | Windows PowerShell | **必须管理员**（#Requires -RunAsAdministrator） | pwsh 7.4+ |
| `setup-wsl-docker-gpu.sh` | **WSL 内 bash**（Ubuntu 24.04/26.04） | **sudo/root** | bash，set -euo pipefail |

> **为什么 setup.sh 在 WSL 内而其他在 Windows？** 它要改的是 Linux 侧的 apt 源、/etc/docker/daemon.json、/etc/wsl.conf 并启动 containerd/dockerd；而 Restart-Gpu.ps1 负责 `wsl --shutdown` + 跨层验证，是 Windows 侧编排器。两者配套：sh 修内部，ps1 管重启与验证。

### 5.2 默认参数（执行前核对，用错发行版名是常见失误）

| 项 | 默认值 | 覆盖方式 |
|---|---|---|
| Restart-Gpu 发行版 | `Ubuntu` | `-Distro Ubuntu-26.04` |
| compress-vhdx 发行版/路径 | `Ubuntu-24.04` / `D:\WSL\Ubuntu\ext4.vhdx` | `-DistroName` / `-VhdxPath` |
| GPU apt 镜像源 | USTC（国内推荐） | `--mirror official` |
| Trae 清理范围 | 仅最大变体 | `-IncludeAllVersions` |

发行版真实名称用 `wsl -l -v` 核对（注意输出为 UTF-16 带 null 字节，脚本已处理；手动复制时去掉空字符）。

### 5.3 GPU 前置条件

- Windows 侧已装 NVIDIA 驱动 **≥ 470.x**（驱动只装 Windows 侧，**不要**在 WSL 内装 NVIDIA 驱动）；WSL2（`wsl --version` 需 2.0+）；amd64 架构
- 适用 **WSL 原生 Docker Engine**；Docker Desktop for Windows 的 GPU 由其自管，本 SOP 不适用
- WSL1 不支持 GPU 直通

## 6. SOP-A：Docker GPU 三层分诊修复

### 步骤 0：定位发行版与现象

确认报错原文：`could not select device driver "" with capabilities: [[gpu]]`（L2/L3 缺失）、`nvml error: driver not loaded`（L1）、`nvidia-container-runtime: not found`（L2 PATH）。

### 步骤 1：纯诊断（不重启，先定位失败层）

```powershell
# Windows PowerShell，普通用户，兼容 PS5.1
pwsh -File .agents/scripts/Restart-WslDockerGpu.ps1 -Diagnose -Distro Ubuntu
# 或 WSL 内等价：sudo bash .agents/scripts/setup-wsl-docker-gpu.sh --verify
```

输出四层结果：L1 驱动层（nvidia-smi）/ L2 工具层（nvidia-container-runtime + nvidia-container-toolkit 包 + nvidia-ctk 三检）/ L3 运行时层（docker info 的 Runtimes 含 nvidia）/ GPU 容器端到端。

> **为什么必须先诊断再动手？** WSL 自动透传 GPU 只到 L1——`nvidia-smi` 正常 ≠ Docker 能用 GPU。L2（toolkit 安装）与 L3（runtime 注册 + wsl.conf 持久化）全是手动层。不定位层级就重装/重启，往往在错误层反复操作数小时。

### 步骤 2：按失败层修复

| 失败层 | 含义 | 修复动作 |
|---|---|---|
| L1 FAIL | WSL 内看不到驱动 | 检查 Windows 侧 NVIDIA 驱动与设备管理器；`ls /usr/lib/wsl/lib/libcuda*`；`wsl --shutdown` 后重试；仍失败先修 Windows 驱动（L1 不通时 setup.sh 会直接拒绝继续） |
| L2 FAIL | toolkit 未装/不全 | **目标发行版内**跑完整配置（幂等）：先 `wsl -d <Distro>` 进入目标发行版（setup.sh 操作的是当前所在发行版，无发行版参数，进错发行版会装错地方），再 `sudo bash .agents/scripts/setup-wsl-docker-gpu.sh`（默认 USTC 源） |
| L3 FAIL | daemon 未运行或 runtime 未注册 | 同上脚本自动完成：备份 daemon.json → `nvidia-ctk runtime configure`（**合并**非覆盖）→ 配置 wsl.conf [boot] → setsid 启动 containerd/dockerd |
| 容器测试 FAIL | L3 过但容器内无 GPU | 查 `/var/log/dockerd.log` 的 nvidia 错误、`which nvidia-container-runtime`、daemon.json 中 runtime path；重跑 setup.sh |

setup.sh 关键行为（全部幂等，可重复执行）：
- apt 源直接写入已展开的架构名（`deb .../stable/deb/amd64 /`），**规避官方 list 文件中 `$(ARCH)` 不展开导致 "Unable to locate package" 的坑**；GPG keyring 存 `/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg`
- 改 daemon.json / wsl.conf 前自动备份为 `.bak.<时间戳>`
- wsl.conf 写入 `[boot] command="nohup containerd ... & sleep 2; nohup dockerd ..."`（新建文件还含 `[network] generateResolvConf=false` 与 `[automount] options="metadata,umask=0022,fmask=0011"`）；旧 [boot] 段先移除再追加
- 无 systemd 环境用 `setsid containerd` → `setsid dockerd`（pgrep 去重），最多等 20s `docker info` 就绪

### 步骤 3：重启 WSL 并端到端验证

```powershell
# setup.sh 完成后必须做：wsl.conf [boot] 只有 wsl --shutdown 才能生效
pwsh -File .agents/scripts/Restart-WslDockerGpu.ps1 -Distro Ubuntu
# 脚本自动：wsl --shutdown → 等8s → 唤醒 → 等20s boot → 四层验证（含 docker run --rm --gpus all ubuntu:22.04 nvidia-smi）
```

全 PASS 退出码 0；任一 FAIL 退出码 1 并打印分层排查指南。验证参数：`-NoContainerTest` 跳过容器测试（无网络拉镜像时）、`-ShutdownWaitSeconds`/`-BootWaitSeconds` 可调。

> **为什么用脚本重启而不是手动 wsl --shutdown？** 关闭 WSL 终端窗口 ≠ 停止 WSL 虚拟机；只有 `wsl --shutdown` 是真重启。脚本还保证 shutdown 后留足 boot 等待（默认 8s+20s），并立即跑四层验证形成闭环——手动操作最常见的失误是 shutdown 后立刻测试，boot 命令还没跑完。

## 7. SOP-B：磁盘空间清理（五步法 + VHDX 压缩）

> 来源模式：`wsl-docker-storage-cleanup-five-step-method`（L2-validated，3 案例跨环境验证，单次回收 160GB）。以下为执行要点；完整脚本片段见模式文档。

### 铁律前置：所有 bash 命令封在同一个 wsl 调用内

```powershell
# 正确形态：全部 bash 语义（含 $()、管道、&&、xargs 替代）在 bash -c 内部
wsl.exe -d Ubuntu -e bash -c 'docker ps -q > /tmp/cids.txt; echo RUN=$(wc -l < /tmp/cids.txt)'
```

> **为什么？** PowerShell（Layer 1）会在传给 wsl.exe 前展开 `$(...)`——Windows PowerShell 里 `$(docker ps -q)` 要么报错要么展开为空，导致 `docker rm` 收到空参数静默"成功"；`xargs` 是 Linux 命令，PowerShell 不存在。两个真实案例因此假称"已清理 80GB"实际 0 字节回收。删除类命令一律用"两步法"：先在 bash -c 内收集 ID 存变量/文件 → 再显式传参删除。

### 第1步：预检 + 快照（daemon 不可达必须 ABORT）

在 WSL 内（或单个 `wsl -e bash -c`）执行：`docker info` 探 daemon **真实状态**（看输出不看返回码）；不可达只输出诊断（检查 WSL 是否启动、发行版是否正确、dockerd 是否运行），**绝不写清理结论**——"Cannot connect to daemon" = 无法列举资源 ≠ 资源不存在。

可达则快照到 `/tmp/cleanup_snapshot_<TS>.txt`：运行中容器（`docker ps --no-trunc`）、每个运行容器的 inspect（CID/IMG/IMG_NAME）、LINKS≥1 的卷、`docker system df` 基线。

### 第2步：划分三层保护带（从快照提取红线）

| 保护带 | 判定 | 处置 |
|---|---|---|
| 🔴 绝对红线 | 运行中容器 + 其引用镜像 ID + LINKS≥1 的卷 + 容器网络 | 禁止任何删除 |
| 🟡 保守保留 | <24h 的非实验 TAG、基础 OS 镜像（ubuntu/alpine）、工具镜像（hadolint/buildx） | 默认不删（删了下次构建冷启动 30-60min） |
| 🟢 清理目标 | 停止/死亡容器、ACTIVE<10% 的 Build Cache、LINKS=0 卷、>24h 且 CONTAINERS=0 的实验 TAG | 默认全清 |

### 第3步：按序清理（顺序不可乱）

1. **停止容器**：`docker ps -aq --filter status=exited --filter status=created --filter status=dead` 收集 ID → `docker rm -fv <IDs>`（-fv 连带匿名卷）
2. **Build Cache（大头）**：确认 `docker system df` 中 Build Cache ACTIVE≈0 后，`docker builder prune -a -f`（**必须 -a**，不加 -a 只删几 KB dangling；案例 75.2GB 中 71.68GB 靠 -a 清掉）；有 buildx 再 `docker buildx prune -a -f`
3. **孤儿卷**：从 `docker system df -v` 提取 LINKS=0 卷名，剔除快照中 LINKS≥1 保护卷 → `docker volume rm <显式列表>`
4. **废弃镜像 TAG**：分两批——同仓库多 TAG 用白名单 KEEP 反选（如保留 `:latest` 与发布 TAG）；明确不用的系列镜像写显式删除列表。**永远避免** `docker system prune -a --volumes` 一键全清（跳过保护带判断）

### 第4步：三重存活验证（任一失败立即停止并回滚）

1. Docker 状态层：`docker ps` 中红线容器仍 `Up (healthy)`，数量不减
2. 进程可达层：`docker exec <name> hostname` + 业务端口 LISTEN 检查
3. 网络握手层：WSL 内 `timeout 5 bash -c 'echo > /dev/tcp/127.0.0.1/<端口>'` 或 PowerShell `Test-NetConnection`

### 第5步：核验与报告

前后 `docker system df` 对比（Build Cache 应降≥70%）；卷总数应 = LINKS≥1 数（案例 128→7）；停止容器允许 ≤1 个 SIZE=0B 残影。

**僵尸容器残影**：`docker ps -aq` 可见但 inspect/rm 报 "No such container" 且 SIZE=0B，是 dockerd boltdb 与 overlayFS 不同步（强关 WSL/断电所致），**不占空间，重启 dockerd 自愈**——不要为 0B 残影重启 WSL 打断业务容器，报告中标注即可。

### 第6步：VHDX 物理压缩（Windows 侧可见空间回收）

Linux 内清理后 ext4.vhdx **不会自动缩小**。需要 Windows 侧真正回收时：

```powershell
# 必须"以管理员身份运行"PowerShell；pwsh 7.4+
pwsh -File .agents/scripts/compress-wsl-vhdx.ps1 -DistroName Ubuntu-26.04 -VhdxPath "D:\WSL\Ubuntu\ext4.vhdx"
# 脚本四步：WSL内 fstrim -av 标记空闲块 → wsl --shutdown → compact → 报告 Before/After/Saved%
```

- compact 双路径自动降级：优先 Hyper-V（Mount-VHD -ReadOnly → Optimize-VHD -Mode Full → Dismount-VHD），无 Hyper-V 模块时降级 diskpart（select/attach readonly/compact/detach）
- WSL 已无法启动时加 `-SkipFstrim`；fstrim 失败仅 WARN 不阻断
- vhdx 路径用 `wsl --manage`/注册表或默认 `%LOCALAPPDATA%\Packages\CanonicalGroupLimited...\LocalState\ext4.vhdx` 核对；自定义安装目录在 `D:\WSL\<distro>\`
- 日常预防：WSL 内定期 `sudo fstrim -av`

## 8. SOP-C：Docker 开机自启持久化（wsl.conf + setsid）

现象：`wsl --shutdown` 或 Windows 重启后 Docker 不自启。根因通常是两层之一缺失：

1. **配置持久化层**：`/etc/wsl.conf` 缺 `[boot]` 段 → 跑 `sudo bash setup-wsl-docker-gpu.sh` 幂等写入（脚本自动备份旧文件、替换旧 [boot] 段）
2. **进程启动层**：WSL 无 systemd（`ps -p 1 -o comm=` 输出 `init`）时，手动启动必须用 setsid：

```bash
# 正确：setsid 放入新会话组，完全脱离控制终端
sudo setsid containerd > /var/log/containerd.log 2>&1 < /dev/null &
sleep 2; sudo setsid dockerd > /var/log/dockerd.log 2>&1 < /dev/null &
# 错误：nohup 只忽略 SIGHUP，WSL 会话结束时的其他信号仍会杀死进程；systemctl 在无 systemd 环境"无报错但没效果"
```

若 `ps -p 1 -o comm=` 输出 `systemd`（用户自行在 Ubuntu 发行版启用 systemd=true），则改用 `sudo systemctl enable --now docker containerd`。

> **注意区分**：禁止给 **podman-machine-default** 发行版设 systemd=true（Podman Issue #28341 不支持）——那是 Podman machine 内部发行版，归 jpman-podman-ops 管辖；本 SOP 的 wsl.conf 指用户自己的 Ubuntu Docker 发行版。

改完 wsl.conf 唯一生效方式：Windows PowerShell 执行 `wsl --shutdown`（会关闭**所有**发行版进程，先确认无未保存工作），重开终端后 `docker info` 应立即可用。排障看 `/var/log/dockerd-boot.log`、`/var/log/containerd-boot.log`；daemon.json 合法性用 `python3 -m json.tool /etc/docker/daemon.json` 验证。

## 9. SOP-D：Trae IDE 缓存清理

> **⚠️ 操作悖论（必读）**：AI 会话本身运行在 Trae 进程内，而清理要求 Trae 完全退出——不能在当前 Trae 集成终端里"边开边清"（进程检测会拦截，且索引/缓存文件被锁定）。正确姿势：在 **Trae 外**打开独立 PowerShell 窗口（开始菜单→PowerShell 7）执行，清理完毕后再启动 Trae。先 `-DryRun` 预览，确认释放量值得重启再动手。

```powershell
# 在 Trae 外的独立 PowerShell 窗口执行；pwsh 7.4+；先预览
pwsh -File D:\spaces\SpecWeave\.agents\scripts\cleanup-trae-cache.ps1 -DryRun
# 确认后执行（默认只清最大变体；五变体全清加 -IncludeAllVersions；-Force 跳过确认）
pwsh -File D:\spaces\SpecWeave\.agents\scripts\cleanup-trae-cache.ps1
```

- 覆盖 5 变体：Trae / Trae CN / TRAE SOLO / TRAE SOLO CN / Qoder
- 清理目标：Roaming 下 13 类缓存（`.ckg` 代码索引库——会重建、logs、Cache、CachedData、GPUCache、WebStorage 等）+ LocalAppData 下 >100MB 的变体目录
- **受保护（脚本内置 -like 匹配，命中即跳过）**：settings.json、keybindings.json、snippets、globalStorage/state.vscdb、storage.json、extensions/、Workspaces/
- 运行前检测 Trae 进程（含 trae-sandbox），运行中会提示先关闭；文件锁定报错时确认所有 Trae 进程完全退出后重试
- 清理后重启 Trae，索引自动重建（首次加载偏慢属正常）

## 10. 安全检查清单

执行任何 WSL 运维动作前逐项确认：

- [ ] `wsl --shutdown` 前已确认所有发行版无未保存工作（该命令关闭全部 WSL 进程）
- [ ] compress-vhdx 已在**管理员** PowerShell 中运行，且 `-VhdxPath`/`-DistroName` 与 `wsl -l -v` 实际发行版核对一致
- [ ] 存储清理第1步快照已完成且 `DAEMON=OK`；daemon 不可达时已 ABORT，未写任何清理结论
- [ ] 🔴 保护带清单（运行容器 ID/引用镜像 ID/LINKS≥1 卷）已从快照提取，删除命令均为显式列表、无 `$(docker ps -q)` 跨界展开
- [ ] 未使用 `docker system prune -a --volumes` 一键全清；Build Cache 已确认 ACTIVE≈0 才加 `-a`
- [ ] Trae 缓存清理已先跑 `-DryRun` 预览，且知晓 settings/extensions/聊天记录受保护不会被删
- [ ] 修改 daemon.json/wsl.conf 前有备份（setup.sh 自动 `.bak.<时间戳>`，手动改前自行 cp）
- [ ] 清理后已完成三重存活验证（容器状态/进程端口/TCP 握手），失败即停并回滚
- [ ] 生产 K8s/Swarm 环境未使用本技能任何清理脚本；关键业务容器数据已先 `docker commit`/`docker cp` 备份

## 11. 常见错误处理

| 错误信息/现象 | 层级/根因 | 处理 |
|---|---|---|
| `could not select device driver "" with capabilities: [[gpu]]` | L2 或 L3 缺失 | SOP-A 步骤1 诊断；L2 装 toolkit，L3 跑 `nvidia-ctk runtime configure --runtime=docker` 后重启 Docker |
| `nvml error: driver not loaded` | L1：WSL 看不到驱动 | Windows 侧更新 NVIDIA 驱动；`wsl --shutdown` 重试；确认 WSL2 2.0+；勿在 WSL 内装驱动 |
| `nvidia-container-runtime: not found` | L2 PATH/未装全 | `which nvidia-container-runtime`；重跑 setup.sh；查 daemon.json runtime path |
| apt 报 `Unable to locate package nvidia-container-toolkit` | apt 源 `$(ARCH)` 未展开/URL 不通 | `cat /etc/apt/sources.list.d/nvidia-container-toolkit.list` 确认无 `$(ARCH)` 字面量（应为 amd64）；`sudo apt update`；用 `--mirror ustc` |
| wsl 重启后 Docker 不自启 | wsl.conf [boot] 缺失/未 shutdown | SOP-C：setup.sh 写 [boot] → PowerShell `wsl --shutdown` → 查 dockerd-boot.log |
| `docker info` 报 Cannot connect to daemon | daemon 未启动/发行版错/ WSL 未启动 | **不得结论"已清理"**；`ps aux \| grep dockerd`；setsid 手动启动；确认 `-Distro` 正确 |
| PowerShell 执行 docker 清理"成功"但空间没变 | 三层 Shell 跨界，`$()` 展开为空 | 全部命令封进单个 `wsl -e bash -c '...'`；两步法显式传参（见 SOP-B 铁律） |
| 清理后 Windows 侧磁盘空间没回来 | vhdx 不会自动缩小 | SOP-B 第6步：管理员跑 compress-wsl-vhdx.ps1 |
| `docker ps -aq` 有容器但 rm 报 No such container | dockerd 索引残影，SIZE=0B | 不占空间，dockerd 重启自愈，报告标注即可，勿重启 WSL |
| Trae 清理后文件锁报错/索引不见 | 进程未完全退出/索引重建中 | 确认所有 Trae 进程退出后重试；重启 Trae 等索引重建（首次慢） |
| setup.sh 报 L1 失败拒绝继续 | nvidia-smi 不可用 | 先修 Windows 侧驱动，L1 不通时 L2/L3 配置无意义 |

## 12. Gotchas

**执行环境类**
1. 三个 ps1 脚本的 PowerShell 版本要求不同：Restart-Gpu **兼容 5.1**（有意为之，系统维护场景不能依赖 pwsh7），compress-vhdx 与 cleanup-trae-cache **要求 7.4+**（脚本自校验并给安装提示）；用错版本会在参数解析处报晦涩错误
2. compress-vhdx 必须管理员（Hyper-V/diskpart 都需要提升权限）；其余脚本普通用户即可——不要为图省事全程管理员 PowerShell
3. setup-wsl-docker-gpu.sh 必须在 **WSL 内**用 sudo bash 跑；在 Windows PowerShell 里跑 bash 脚本会得到语法错误
4. 默认发行版名三个脚本各不相同（Ubuntu / Ubuntu-24.04），执行前用 `wsl -l -v` 核对并显式传参

**GPU/Docker 类**
5. NVIDIA 驱动只装 Windows 侧——在 WSL 内 `apt install nvidia-driver` 是错误操作，WSL GPU 库由 `/usr/lib/wsl/lib` 自动透传
6. `nvidia-ctk runtime configure` 是**合并**配置不覆盖已有 runtimes，但改前仍应备份 daemon.json；改完必须重启 dockerd 才加载
7. 无 systemd 的 WSL 里 `systemctl restart docker` 不报错但**没效果**；`nohup dockerd &` 关终端就死——setsid 是唯一正确原语
8. Docker Desktop for Windows 不归本技能管：它有自己的 WSL2 集成后端与 GPU 管理，两套 daemon 并存本身就是问题（参见 wsl2-docker-selection-decision 模式）
9. Podman GPU 走 CDI（`nvidia-ctk cdi generate` → `podman run --device nvidia.com/gpu=all`），不用 Docker runtime 那套；Podman 场景转 jpman-podman-ops

**清理/磁盘类**
10. `docker builder prune` 不加 `-a` 只删 dangling 几 KB，70GB 级缓存全靠 `-a`；但 `-a` 前必须确认 Build Cache ACTIVE≈0
11. `docker compose down` 默认不删卷、`docker rm` 不带 `-v` 不删匿名卷——孤儿卷是每轮 up 累积的，清理要显式 `docker volume rm` LINKS=0 列表
12. fstrim/prune 释放的是 ext4 文件系统内空间，ext4.vhdx 物理文件只增不减；不跑 compact，Windows 侧磁盘告警不会消失
13. `wsl --shutdown` 影响**所有**发行版（不只是 -Distro 指定的那个），执行前检查其他发行版是否在跑任务
14. cleanup-trae-cache 不能在 Trae 集成终端里跑——AI 会话本身就是 Trae 进程，脚本检测到运行中进程会拦截；必须在 Trae **外**独立 PowerShell 窗口执行，清完再启动 Trae（`.ckg` 索引重建期间首次加载偏慢）
15. setup-wsl-docker-gpu.sh 没有发行版参数，它配置的是"当前所在发行版"——先 `wsl -l -v` 核对名称、`wsl -d <目标>` 进入后再 sudo 执行，进错发行版会把 toolkit/boot 配到无关环境

## 13. 关键参考速查

| 参考 | 路径 | 何时查 |
|---|---|---|
| 存储清理五步法（L2-validated，完整脚本片段） | [wsl-docker-storage-cleanup-five-step-method.md](../../../docs/retrospective/patterns/code-patterns/wsl-docker-storage-cleanup-five-step-method.md) | 执行 SOP-B 需要完整快照/awk 脚本 |
| GPU 三层分诊模式（L1-draft，8 步 + 回滚 5 步） | [wsl-docker-gpu-triage.md](../../../docs/retrospective/patterns/code-patterns/wsl-docker-gpu-triage.md) | GPU 手动修复/回滚/Podman CDI 迁移 |
| WSL 命令安全（三层 Shell 模型） | patterns/code-patterns/wsl-docker-command-safety.md | 跨层命令写法疑问 |
| Desktop vs 原生 Docker 选型 | patterns/code-patterns/wsl2-docker-selection-decision.md | daemon 不可达且怀疑双 daemon 并存 |
| GPU 修复复盘来源 | `docs/retrospective/reports/environment-setup/retrospective-wsl-docker-gpu-fix-20260815/` | 追溯案例细节 |
| 姊妹技能 | [jpman-podman-ops](../jpman-podman-ops/SKILL.md)、[docker-cache-cmd](../docker-cache-cmd/SKILL.md)、[docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md) | 容器驾驶/镜像灾备/发行版转换 |
| NVIDIA 官方文档 | https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html | toolkit 版本与官方源 |
| USTC 镜像帮助 | https://mirrors.ustc.edu.cn/help/libnvidia-container.html | 国内网络 apt 源异常 |

## 14. Changelog

- **v1.0.0** (2026-08-29): 初始版本。封装 4 脚本（compress-wsl-vhdx / Restart-WslDockerGpu / setup-wsl-docker-gpu / cleanup-trae-cache）+ 五步法（L2）与 GPU 三层分诊（L1）两模式；四大 SOP（GPU 分诊/存储清理+VHDX/Docker 自启/Trae 缓存）；三层 Shell 安全铁律；9 项安全清单、11 行错误表、15 条 Gotchas；与 jpman-podman-ops/docker-cache-cmd/docker-wsl-bridge-cmd 边界互链。经 V 阶段 4 视角对抗审查：补 setup.sh 发行版归属提示、项目根/help 约定、Trae 自清理操作悖论警示。
