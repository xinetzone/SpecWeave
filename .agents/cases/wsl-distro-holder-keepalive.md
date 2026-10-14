---
id: "cases-wsl-distro-holder-keepalive"
title: "WSL2 发行版跨命令保活：WMI detached holder 绕过工具宿主 Job 回收"
source: "2026-10-13 okw desktop launch 托管用户名修复零基线端到端验证（会话 sc-20261013-wsl-holder-keepalive）"
x-toml-ref: "../../.meta/toml/.agents/cases/wsl-distro-holder-keepalive.toml"
---
# WSL2 发行版跨命令保活案例：WMI detached holder 绕过工具宿主 Job 回收

> **成熟度：L1**（单次实战验证，2026-10-13）。升 L2 条件：在第 2 个独立场景（候选：jpman 容器或 compose-overlay 叠加栈的跨命令浸泡/GUI 验证）复用成功，并在文末「复用记录」回填 `reuse_count` 与场景链接。

## 1. 一句话结论

在 TRAE（及一切以 Windows Job Object 托管命令进程树的 agent 宿主）中跨多条 Shell 命令验证 WSL2 长会话/GUI 时，每条命令结束都会终止其启动的 `wsl.exe`/`wslhost.exe`，使发行版失去最后一个 console attach 而被**干净关机**（`.wslconfig` 的 `vmIdleTimeout=-1` 挡不住）。用 WMI `Win32_Process.Create` 启动一个父进程为 `WmiPrvSE.exe`、脱离 agent Job 的**有界 holder**（`wsl -d <D> sleep N`）即可保活。

## 2. 何时翻到本案例

- 需要跨多条 Shell 命令保持 WSL2 发行版存活：GUI 端到端（如 mstsc/xrdp 窗口必须跨越「启动命令」与「截屏命令」两条命令）、长时构建/浸泡测试、跨命令日志/状态对账。
- 症状组合：服务在 guest 内自测健康；Windows→localhost 转发时通时断；guest journal 出现完整的干净关机序列。

## 3. 现象与实测证据（2026-10-13）

- **节律**：每条 Shell 命令结束后约 6–17 秒，发行版被终止。当日 17:19:05、17:20:32、17:21:11 三次 `sesman asked to terminate` 均与命令结束时刻对齐；17:21:11 一次恰好杀掉刚建立 13 秒的 xrdp 登录会话（xrdp.log：`Received termination signal`）。
- **journal 铁证（干净关机，非崩溃）**：

  ```text
  WSL (2 - init-systemd(openKylin-3.0-desktop)) ERROR: InitTerminateInstanceInternal:2901:
  systemctl poweroff did not terminate the instance in 10000 ms, calling reboot(RB_POWER_OFF)
  ```

  随后 `finalrd`/`prefinalrd`、系统服务批量 `Stopping`——这是 WSL init 主导的正常关机路径，不是段错误/崩溃。
- **配置排除**：`C:\Users\<u>\.wslconfig` 已设 `vmIdleTimeout=-1`（禁用空闲回收），关机照样发生 → 与空闲超时无关。
- **relay 失活分层证据**：发行版被反复重启后 Windows 侧 `Test-NetConnection 127.0.0.1 -Port 3390` 持续 **False**；同一时刻 guest 内 `timeout 2 bash -c '</dev/tcp/127.0.0.1/3390'` **成功**（xrdp 健康在听）——断在 Windows→WSL 的 localhost relay，不在服务。
- **反向验证（holder 有效性）**：holder 存活的 40 秒跨命令窗口内，sesman PID/启动时间不变（PID 1159，17:26:17 起）、Windows 侧 relay 持续 True。

## 4. 根因机制

1. agent 工具宿主把每条 Shell 命令的进程树放进一个 Windows Job Object，命令结束即关闭/回收该 Job。
2. 命令内启动的 `wsl.exe`（及其 `wslhost.exe` 同伴）作为 Job 内进程随之终止；`Start-Process` 后台启动**无效**——父进程仍属同一 Job。
3. WSL2 发行版生命周期关联 console attach：最后一个 attach 消失后，WSL init 收到终止指令，执行 `systemctl poweroff`（10 秒未退出则 `reboot(RB_POWER_OFF)` 兜底）。
4. 发行版快速重启还会使 localhost relay 挂钩失败（WSL2 已知竞态），表现为「guest 内通、Windows 侧不通」。
5. WMI `Win32_Process.Create` 的新进程父进程是系统服务 `WmiPrvSE.exe`，不在 agent Job 内 → 命令结束不被回收，其持有的 console attach 使发行版存活。

## 5. 三层分诊法（先判层，勿盲目重启）

| 层 | 命令 | 判读 |
|---|---|---|
| ① guest 服务 | `wsl.exe -d <D> -u root -- bash -c "timeout 2 bash -c '</dev/tcp/127.0.0.1/<PORT>' && echo GUEST_OK"` | 通 = 服务健康，问题不在 guest |
| ② Windows relay | `(Test-NetConnection 127.0.0.1 -Port <PORT> -WarningAction SilentlyContinue).TcpTestSucceeded` | False 而①通 = relay 失活 |
| ③ 关机归因 | `wsl.exe -d <D> -u root -- journalctl --since "<HH:MM>" --no-pager` 搜 `InitTerminateInstanceInternal`，并与命令结束时刻对表 | 干净 poweroff = attach 被回收；段错误/OOM 才是崩溃 |

辅助基线（实例存活判据）：操作前记 `wsl.exe -d <D> -u root -- ps -o pid,lstart,cmd -C xrdp-sesman` 的 PID+启动时间，跨命令复查 **PID 不变**才是同一实例存活（服务重启会换 PID）。

> PowerShell 陷阱：`Test-NetConnection` 默认可能走 `::1`，必须显式 `127.0.0.1`；`wsl ... | tail` 管道在 PowerShell 中易被误解析，直接用 `wsl -- tail` 传参，不要加 Windows 侧管道。

## 6. 解法 SOP：WMI detached holder

**启动**（PowerShell；该命令与后续所有 holder/GUI 相关命令均须在非沙箱下执行，见 §7）：

```powershell
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create `
  -Arguments @{ CommandLine = 'wsl.exe -d <DISTRIBUTION> -u root sleep 600' }
# ReturnValue = 0 即创建成功；$r.ProcessId 为脱离 agent Job 的 holder PID
```

**三重存活判据**（在下一条命令里验证，三者全真才算保活成立）：

```powershell
Get-Process -Id <holderPid> -ErrorAction SilentlyContinue        # 1 holder 仍在
wsl.exe -d <D> -u root -- ps -o pid,lstart,cmd -C xrdp-sesman   # 2 服务 PID/启动时间未变
(Test-NetConnection 127.0.0.1 -Port 3390 -WarningAction SilentlyContinue).TcpTestSucceeded  # 3 relay 通
```

**收尾**：`Stop-Process -Id <holderPid> -Force`。holder 消失后发行版按 WSL 正常语义回收（实测回到 Stopped，同机其他发行版不受影响）。

## 7. 使用纪律（硬约束）

1. **holder 必须有界**：`sleep 600` 按任务预估时长设定，禁止无限 `sleep`；任务结束必须 `Stop-Process`，不留游离 `wsl.exe`。
2. **必须非沙箱执行**：沙箱 Job 同样回收进程树，且 WMI Create 跨会话需要非沙箱权限；mstsc 等 GUI 进程同理——沙箱内启动的 GUI 会在命令结束被 Job 回收。
3. **relay 已失活时 holder 不能复活转发**：先 `wsl.exe --shutdown` 冷启动（会停止**全部**发行版，含 podman-machine 等，执行前必须向用户说明影响并获认可），冷启后端口通常 5 秒级恢复，再上 holder。
4. **holder 只保活，不代替就绪检查**：冷启/启动后仍须轮询服务 `active` + 端口可达，再跑 GUI 或验证。
5. **端口不通时不要反复重启 mstsc/发行版**：先按 §5 区分服务层、relay 层、attach 层，对症下药。

## 8. 误诊清单

| 误判 | 事实 |
|---|---|
| 「vmIdleTimeout 太短导致关机」 | `-1`（禁用）也发生，根因是 Job 回收 console |
| 「发行版崩溃了」 | journal 是 WSL init 主导的干净 poweroff 序列，无崩溃特征 |
| 「xrdp/服务坏了」 | guest 内 `/dev/tcp` 自测成功即可证伪 |
| 「Start-Process 后台启动就能保活」 | 父进程仍在同一 Job，命令结束同归于尽 |
| 「relay 坏了只能重启 WSL」 | 冷启动可恢复 relay，但 attach 回收必须靠 detached holder，二者是两层问题 |

## 9. 适用边界与复用面

- **适用**：Job-Object 类 agent 宿主 + WSL2 环境下，跨多条命令的实例保活、GUI 自动化、长浸泡验证。候选复用场景：okw desktop GUI 验证（[openkylin-wsl-devkit Skill](../skills/openkylin-wsl-devkit/SKILL.md)）、jpman 容器跨命令运维、client compose 叠加栈浸泡与双端端口验证。
- **不适用**：单条命令内能完成的操作（无需 holder）；用户日常手动使用 WSL（无 Job 回收问题）；需要变更系统服务自启逻辑的需求（本方案零配置、纯进程技巧，不替代系统配置修复）。

## 10. 证据溯源

- 场景：okw `desktop launch` 托管用户名修复（`DEFAULT_LOGIN_USER="openkylin"`）的零注册表记忆基线第二轮端到端验证。
- 关键时点（2026-10-13）：
  - 17:26:15 WMI holder（PID 42888）启动，`ReturnValue=0`；
  - 17:27:26 跨过一条命令边界：holder 存活，sesman 仍为 PID 1159 / 17:26:17 未重启，relay `True`；
  - 17:28:30 sesman 增量日志：`Received system login request ... for user: openkylin` → `Access permitted` → `logged in` → Xorg `:10`，mstsc 进入 openKylin 桌面；
  - 收尾 `Stop-Process` 后 `wsl -l -v` 三发行版均回 Stopped，holder 无残留。
- 规范呼应：[AGENTS.md 启动协议](../../AGENTS.md)要求环境类结论以当轮读回证据为准；本案例正是「命令结束后环境被宿主回收」这一反直觉行为的取证与处置样本。

## 复用记录

- 2026-10-13 首立（L1）：okw desktop 零基线端到端验证，reuse_count = 1。
