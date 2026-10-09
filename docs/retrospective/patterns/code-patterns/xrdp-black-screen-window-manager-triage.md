---
type: Pattern
id: "xrdp-black-screen-window-manager-triage"
title: "xrdp 黑屏三层分诊法（连接/会话/窗口管理器）"
version: 1.0
date: 2026-10-08
maturity: L1
validation_count: 1
reuse_count: 0
tags: [xrdp, black-screen, window-manager, kwin, ukui, wsl, XDG_RUNTIME_DIR, xsession, triage, remote-desktop]
source: "openKylin 3.0 Desktop WSL 首登纯黑屏排障实操（方法论编排 session sc-20261008-openkylin-desktop-wsl-install，Win10 26220 + WSL 3.0.2.0）"
related_patterns:
  - "wsl-import-memory-triage-sparse-vhd"
  - "wsl-distro-install-migration-guide"
  - "large-archive-remote-preflight"
  - "build-failure-layered-triage"
---

# xrdp 黑屏三层分诊法（连接 / 会话 / 窗口管理器）

> 远程桌面（xrdp/VNC）**认证通过、连接成功，但进入后整屏纯黑**——此时最容易犯的错是凭"黑屏"二字猜显卡、重装、重启。本模式要求先用进程与日志证据把故障钉死在三个失效层之一：**连接层（端口/服务）→ 会话层（X server/桌面会话）→ 窗口管理器层（合成器）**，再在对应层做最小、可逆的修复。来源案例证明：任务栏/桌面图标进程全部存活、唯独窗口管理器 KWin 因 `XDG_RUNTIME_DIR` 被启动脚本清掉而冷启动不驻留，表面现象就是黑屏，与显卡和安装完整性无关。

## 适用边界

**适用于**：

- xrdp（或同类 RDP/VNC 网关）登录窗能连上、认证通过，但登录后黑屏、无壁纸无任务栏，或只有部分桌面元素；
- 桌面环境采用独立窗口管理器/合成器（KWin、Mutter/ukwm、Xfwm4、Marco、Openbox 等），且会话管理器负责按需拉起它；
- WSL2/容器等**虚拟图形栈 + 定制启动脚本**环境（启动脚本常 `unset` 部分环境变量、WM 冷启动时序敏感）；
- 需要判断"该修服务、修会话还是修 WM"，避免无证据重启/重装的排障场景。

**不适用于**：

- 连接根本建立不了（端口不通、认证失败、立即断连）——这是连接层之前的问题，先查防火墙/端口/密码，不在本模式范围；
- 花屏、分辨率异常、输入设备失灵等非"黑屏"显示问题；
- 物理机直连桌面（无远程会话脚本层，`XDG_RUNTIME_DIR` 被清这一主因不存在）；
- 会话整体崩溃（Xorg 反复退出、登录后立刻被踢回登录窗）——应先看 Xorg 日志与 `.xsession-errors` 的致命错误，本模式的"WM 单独缺失"前提不成立。

## 核心步骤（五步法）

### 1. 证伪连接层：服务、端口、转发都通

黑屏≠连不上。先排除"其实没连上"：

```bash
systemctl is-active xrdp xrdp-sesman        # 两者都应 active
ss -lnt | grep 3390                          # 应有 *:3390 LISTEN
```

Windows 宿主侧再测一次转发（WSL 场景）：`Test-NetConnection 127.0.0.1 -Port 3390` 应 `TcpTestSucceeded=True`。三项都通而仍黑屏，故障在会话内部，禁止再动防火墙/重装 xrdp。

### 2. 区分会话层：X server 与桌面会话是否活着

```bash
pgrep -a -x Xorg                             # 有 Xorg :10 且稳定 = 显示服务器在
pgrep -a -x ukui-session                     # GNOME 系换 gnome-session，XFCE 换 xfce4-session
ps -ef | grep -E "panel|desktop|session" | grep -v grep
```

- Xorg 不在或反复重启 → 会话层故障，读 `~/.xorgxrdp.*.log` 的 `(EE)` 行；
- Xorg 在、桌面会话在、面板/桌面图标进程也在 → **会话已成功起来，问题只可能在窗口管理器**，进入步骤 3。这是本模式最关键的分流信号：**"桌面组件活着但黑屏"几乎等价于"没有合成器绘制根窗口"**。

### 3. 定位窗口管理器层：WM 进程在不在、叫什么、为何没起

```bash
# 3a. WM 进程是否存在（不同桌面换名字：kwin_x11 / mutter / ukwm / xfwm4 / marco / openbox）
pgrep -a -x kwin_x11 || echo "WM 未运行"

# 3b. 系统期望的 WM 是哪个、装没装
update-alternatives --display x-window-manager 2>/dev/null
dpkg -l | grep -iE "kwin|mutter|ukwm|xfwm|marco"
gsettings get org.ukui.session.required-components windowmanager 2>/dev/null  # UKUI

# 3c. 会话管理器有没有尝试拉起 WM（关键日志）
grep -iE "wm start command|window.manager|kwin|XDG_RUNTIME_DIR" \
  ~/.config/<session-manager>/*.log ~/.xsession-errors 2>/dev/null | head -20
```

判定：WM 包已装、alternatives 指向正确、日志显示会话**曾尝试启动但进程没驻留**，且日志伴随 `XDG_RUNTIME_DIR not set` 之类环境告警 → 冷启动环境/时序问题（步骤 4）。若 WM 包压根没装，那是镜像裁剪问题，`apt install` 对应 WM 即可，不套用步骤 4。

### 4. 抓根因：检查启动脚本是否清掉了 WM 依赖的环境

xrdp 场景的高发根因是会话启动脚本清理环境。直接看：

```bash
grep -nE "unset|XDG_RUNTIME_DIR|Xsession" /etc/xrdp/startwm.sh
```

来源案例中该脚本含 `unset XDG_RUNTIME_DIR`，会话管理器日志同时告警 `XDG_RUNTIME_DIR not set, defaulting to '/var/tmp/runtime-<user>'`，WM 在 Xorg ready 仅约 1 秒后被拉起、因运行时目录无效而退出，且会话**不会二次拉起** → 黑屏。验证手段：在同一个已就绪的 X 上手动 `DISPLAY=:10 kwin_x11 --replace`，若能稳定常驻，即证明是**冷启动环境/时序**而非 GL/兼容问题——这一步同时充当修复前的假设验证，别跳过。

### 5. 用户级修复：补环境 + 幂等看门狗（不改系统文件、可回滚）

优先改用户自己的 `~/.xsession`（先 `cp ~/.xsession ~/.xsession.bak` 备份），不要直接改 `/etc/xrdp/startwm.sh`（系统文件升级会被覆盖、且影响所有用户）。已验证的模板（KWin/UKUI）：

```sh
#!/bin/sh
# 补回被 xrdp startwm.sh unset 的运行时目录；WM 冷启动失败时前 15 秒幂等补拉
[ -z "$XDG_RUNTIME_DIR" ] && export XDG_RUNTIME_DIR="/run/user/$(id -u)"
(
  sleep 3
  for n in 1 2 3 4 5 6; do
    pgrep -x kwin_x11 >/dev/null 2>&1 && exit 0   # WM 已在跑：立即退出，绝不重复启动
    kwin_x11 --replace >/tmp/wm-watchdog.log 2>&1 &
    sleep 2
  done
) &
exec ukui-session                                 # 换成你的会话入口（gnome-session/startxfce4…）
```

其他桌面替换三处：`pgrep -x`/命令行里的 WM 名、最后的会话入口；通用探测可用 `WM=$(update-alternatives --query x-window-manager | awk '/Value:/{print $2}')`。

**修复后必须用证据验证，不能"看着亮了"就算完**：结束旧会话（见下）→ 重新登录 → 确认：

```bash
# ① WM 存活，且父进程链指向会话管理器（说明是会话自己拉起的，不是只靠看门狗）
pid=$(pgrep -x kwin_x11)
for i in 1 2 3 4; do ps -o pid,ppid,args= -p "$pid"; pid=$(ps -o ppid= -p "$pid" | tr -d ' '); done
# 期望链：kwin_x11 ← <session-manager-server> ← <session> ← xrdp-sesexec
# ② 环境变量正确
tr '\0' '\n' < /proc/$(pgrep -x kwin_x11)/environ | grep XDG_RUNTIME_DIR
```

结束旧会话的命令要用**精确进程名匹配**：`pkill -u <user> -x Xorg`。禁止 `pkill -f "Xorg :10"` 这类全命令行匹配——在 `sh -c '...'` 内执行时，`-f` 会匹配到承载命令的 shell 自身命令行，把取证 shell 一起杀掉（来源案例真实踩中）。

> 看门狗首次补拉若与会话自启撞车，日志里出现一条 `FATAL ERROR while trying to open display :10.0` 属正常竞态（显示已被在位 WM 占用），循环检测到 WM 在位即退出，不产生第二个 WM。

## 反模式（均来自本案例实操）

| # | 反模式 | 后果 | 正确做法 |
|---|---|---|---|
| 1 | 一见黑屏就 `wsl --shutdown`、重装发行版、重下镜像 | 销毁现场、且根因在用户会话脚本层时重装多少次都复发；来源案例的镜像校验完全正常 | 先走五步：连接→会话→WM 三层证伪，把故障钉死在一层再动手 |
| 2 | 手动 `kwin_x11 --replace` 把画面救亮就收工 | 只是把当前会话救活，下次登录 WM 冷启动照样失败、照样黑屏 | 手动拉起只作为步骤 4 的**假设验证**；根治必须落到 `~/.xsession` 并经重登验证 |
| 3 | 看门狗不做在位检测、无限循环拉起 WM | 同时刻可能存在多个 WM 抢 X server，制造新的竞态与闪屏 | 循环有上限（6 次/约 15 秒），每次先 `pgrep -x` 在位即 `exit 0`，保证幂等 |
| 4 | 凭"黑屏"直觉判定显卡/GL 驱动问题，去装 DRI/llvmpipe | 来源案例 WM 进程压根不存在，GL 再怎么调也没有合成器；装包还污染环境 | 步骤 2/3 先回答"WM 进程在不在"，进程缺失优先查拉起链与环境，而非渲染后端 |
| 5 | 直接编辑 `/etc/xrdp/startwm.sh` 注释掉 `unset` | 改系统文件影响全部用户、包升级时被静默覆盖，排障痕迹不可追溯 | 用户级 `~/.xsession` 补环境变量（先备份）；系统级修改只能作为最后手段并登记 |
| 6 | 用 `pkill -f <带空格的命令行>` 在 `sh -c` 内结束会话 | `-f` 全命令行匹配会命中执行命令的 shell 自身，取证/修复脚本中途自杀、输出中断 | 一律 `pkill -x <精确进程名>`；复杂匹配先 `pgrep -a` 预演确认命中集 |

## 检验标准

- 能用一条 `pgrep -x <WM名>` 明确回答黑屏属于三层中的哪一层，并有对应日志行佐证，不靠猜测；
- 修复前有"在就绪 X 上手动拉起 WM 能否常驻"的对照实验，区分冷启动时序问题与兼容/缺包问题；
- 修复落在用户家目录、有备份、可一键回滚（`cp ~/.xsession.bak ~/.xsession`），不改系统文件、不装无关包；
- 重登后以**父进程链 + `/proc/<pid>/environ`** 证实 WM 由会话正常拉起、环境正确，而不仅是"这次亮了"；
- 看门狗有次数/时间上限与在位即退的幂等保证。

## 跨域迁移

- **GNOME（mutter）/ XFCE（xfwm4）/ MATE（marco）on xrdp**：三层分诊完全同构，仅替换会话名、WM 名与日志目录；`unset XDG_RUNTIME_DIR` 是 Debian 系 xrdp `startwm.sh` 的通用写法，同类故障在其他发行版可复用同一根因检查；
- **VNC/其他远程桌面网关黑屏**：连接层（VNC 端口）→ 会话层（Xvnc + 会话）→ WM 层的分流不变，换日志名与端口即可；
- **WSLg 单应用无窗口/白屏**：虽然形态是"单应用集成"而非整桌面，"先证伪 DISPLAY/Wayland 通道、再看目标进程、再看合成/渲染依赖"的分层取证顺序同源；
- **更一般的"服务 active 但功能不可用"**：与 [build-failure-layered-triage.md](build-failure-layered-triage.md)、[wsl-import-memory-triage-sparse-vhd.md](wsl-import-memory-triage-sparse-vhd.md) 共享同一元原则——状态灯/进程存在是最浅一层证据，沿调用链逐层取证（连接→会话→组件），在证据指向的层修复，其余层不动。

## 成熟度

**L1（单案例待验证）**：本模式完整形成于 openKylin 3.0 Desktop WSL（UKUI 4.x + KWin 5.24 + xrdp，WSL 3.0.2.0）首登黑屏一例，五步全部走通；反模式 2（手动救活≠根治，故继续落到 .xsession）与 6（`pkill -f` 误杀取证 shell）在同一案例真实触发，1/4（盲目重启重装、猜 GL 装驱动）为流程中主动规避的高发诱惑。升级 L2 需在**异构桌面/异构网关**再验证至少一例（优先：GNOME+mutter on xrdp，或非 WSL 的纯虚拟机 xrdp 场景），确认 WM 名映射表、会话日志路径与 `XDG_RUNTIME_DIR` 根因在不同组合下仍然成立。
