---
title: "openKylin 3.0 Desktop WSL 桌面启动与日常使用教程（Windows 10/11 实测）"
date: 2026-10-08
category: "tech"
tags:
  - openkylin
  - wsl
  - desktop-wsl
  - xrdp
  - ukui
  - quickstart
  - tutorial
status: "verified"
security_level: "public"
source: "2026-10-08 本机实测（Windows 10.0.26220 + WSL 3.0.2.0 + openKylin 3.0 Desktop WSL 镜像）；方法论 session sc-20261008-openkylin-desktop-wsl-install。安装与选型见 [双 WSL 镜像对照与选型参考](wsl-dual-image-selection.md)，黑屏排障见同文 §5.1。"
---

# openKylin 3.0 Desktop WSL 桌面启动与日常使用教程

> 这份教程只解决一件事：**每天怎么打开 openKylin 桌面、用完怎么关、出问题怎么办**。前提是你已经按 [双 WSL 镜像对照与选型参考](wsl-dual-image-selection.md) 导入了名为 `openKylin-3.0-desktop` 的发行版（2026-10-08 本机已导入并验证）。零基础友好，全部步骤可照抄。

---

## 1. 30 秒理解：为什么不能"直接点图标"

openKylin 桌面运行在 WSL2 虚拟机里，你的 Windows 和它之间隔着三层：

```
Windows 桌面
   │  ① mstsc（远程桌面连接，端口 localhost:3390）
   ▼
xrdp 服务（Linux 侧，开机自启）
   │  ② 提供 UKUI 图形桌面
   ▼
openKylin-3.0-desktop 发行版（WSL2，不用时处于"已停止"状态）
```

所以打开桌面需要两步：**先让发行版运行起来（约 3 秒）→ 再用 mstsc 连 3390 端口**。第 3 节的一键启动器会把这两步合成"双击一个图标"。

> 连接地址统一用 **`localhost:3390`**（不要用文档里的 `172.25.x.x` 内网 IP——WSL 重启后 IP 会变，localhost 转发永不漂移，2026-10-08 实测可用）。

---

## 2. 一次性准备（只做一次）

### 2.1 确认发行版已导入

PowerShell 执行（普通权限即可）：

```powershell
$wsl = "$env:WINDIR\System32\wsl.exe"
& $wsl -l -v
```

列表里应能看到 `openKylin-3.0-desktop`，VERSION 为 2。没有 → 先回到[安装文档](wsl-dual-image-selection.md) §5 完成导入。

### 2.2 确认黑屏补丁已存在（重要）

该镜像**首次登录会黑屏**（窗口管理器冷启动问题，根因与修复见[双镜像文档 §5.1](wsl-dual-image-selection.md)）。本机已于 2026-10-08 修复。换新机器或重新导入后，先检查：

```powershell
& $wsl -d openKylin-3.0-desktop -- cat /home/openkylin/.xsession
```

输出里包含 `XDG_RUNTIME_DIR` 和 `kwin_x11` 两行即已修复；若只输出一行 `ukui-session` 或文件不存在，先按 [§5.1 修复脚本](wsl-dual-image-selection.md)处理再继续。

### 2.3 准备好你的登录信息

| 项 | 值 |
|---|---|
| Session（会话类型） | **xorg**（登录窗下拉手动选） |
| 用户名 | `openkylin` |
| 初始密码 | `openkylin`（**第 5 节会教你改掉**） |

---

## 3. 日常启动（三种方式，按推荐排序）

### 方式 A：一键启动器（推荐，双击图标全自动）

启动器 = 一个 PowerShell 脚本 + 一个双击包装。它会自动完成：启动发行版 → 等 3390 端口就绪 → 弹出远程桌面。

**第 1 步**：新建文件 `C:\Users\xinzo\openKylin桌面\启动openKylin桌面.ps1`（目录随意），内容：

```powershell
# openKylin Desktop WSL 一键启动器（2026-10-08 实测）
$ErrorActionPreference = 'Stop'
$distro = 'openKylin-3.0-desktop'
$wsl    = "$env:WINDIR\System32\wsl.exe"

Write-Host "[1/3] 启动发行版 $distro ..." -ForegroundColor Cyan
& $wsl -d $distro -- /bin/true   # 触发开机，systemd 会自动拉起 xrdp

Write-Host "[2/3] 等待远程桌面服务（3390）就绪 ..." -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds(40)
do {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect('127.0.0.1', 3390, $null, $null)
        $ready = $iar.AsyncWaitHandle.WaitOne(600)
        if ($ready) { $client.EndConnect($iar); $ok = $true } else { $ok = $false }
    } catch { $ok = $false } finally { $client.Close() }
    if (-not $ok) { Start-Sleep -Milliseconds 800 }
} until ($ok -or (Get-Date) -gt $deadline)

if (-not $ok) { Write-Host "3390 端口 40 秒内未就绪，请检查 xrdp：wsl -d $distro -- systemctl status xrdp" -ForegroundColor Red; pause; exit 1 }

Write-Host "[3/3] 打开远程桌面 ..." -ForegroundColor Cyan
Start-Process mstsc.exe -ArgumentList '/v:localhost:3390'
```

**第 2 步**：同目录新建 `启动openKylin桌面.cmd`（双击入口，绕开执行策略），内容**纯英文/ASCII，避免中文批处理编码坑**：

```bat
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0启动openKylin桌面.ps1"
```

**第 3 步**：右键这个 `.cmd` → 发送到 → 桌面快捷方式（可再右键快捷方式改图标、重命名为"openKylin 桌面"）。以后**双击桌面图标即可**。

> 说明：发行版已在运行时，脚本也能正常工作（第 1 步是幂等的，端口检测会立刻通过）。

### 方式 B：手动两步（不想建启动器时）

```powershell
# ① 启动发行版（任何命令都会触发开机）
& "$env:WINDIR\System32\wsl.exe" -d openKylin-3.0-desktop -- /bin/true
# ② 打开远程桌面
Start-Process mstsc.exe -ArgumentList '/v:localhost:3390'
```

或直接 `Win+R` 输入 `mstsc` 回车，计算机栏填 `localhost:3390`。

### 方式 C：保存 .rdp 文件（发行版已在运行时最快）

新建文本文件改名为 `openKylin.rdp`，内容：

```ini
full address:s:localhost:3390
username:s:openkylin
prompt for credentials:i:0
desktopwidth:i:1600
desktopheight:i:900
session bpp:i:32
redirectclipboard:i:1
redirectprinters:i:0
redirectdrives:i:0
audiomode:i:0
```

双击即连（仍需发行版处于运行中，所以日常更推荐方式 A）。想保存密码免输入：先在 mstsc 里勾"记住我"；或命令行 `cmdkey /add:localhost:3390 /user:openkylin /pass:你的新密码`（改密码后再做，见第 5 节）。

---

## 4. 登录进入 UKUI 桌面（逐屏指引）

### 4.1 首次连接的证书提示（一次性，可根治）

mstsc 首次连接默认会弹黄色警告"**无法验证此远程计算机的身份**"，原因有二：① 请求的是 `localhost`，而 xrdp 默认自签证书的名字是 `localhost.localdomain`（名称不匹配）；② 证书由 xrdp 自签，Windows 不信任颁发者。流量在本机回环、不出网卡，所以这两条都不代表真实安全风险。

**推荐：根治（一劳永逸，本机已于 2026-10-08 验证，之后直进登录窗、不再弹警告）**。三步走，需在 WSL 内 root 权限操作：

```bash
# 在 PowerShell 里以 root 执行（或先 wsl -d openKylin-3.0-desktop -u root 进入）
# 注意把 CER_DIR 改成你 Windows 用户名对应的实际目录
$wsl -d openKylin-3.0-desktop -u root -e bash -c '
set -e
PEM=/etc/ssl/certs/ssl-cert-snakeoil.pem
KEY=/etc/ssl/private/ssl-cert-snakeoil.key
CER_DIR=/mnt/c/Users/xinzo/openKylin桌面
cp -a "$PEM" "${PEM}.bak-$(date +%Y%m%d)"; cp -a "$KEY" "${KEY}.bak-$(date +%Y%m%d)"
# 重签：CN=localhost，SAN 覆盖本机回环全部名字 + IPv4，有效期 10 年
openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
  -keyout "$KEY" -out "$PEM" -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,DNS:localhost.localdomain,DNS:$(hostname),IP:127.0.0.1"
chown root:root "$PEM"; chmod 644 "$PEM"
chown root:ssl-cert "$KEY"; chmod 640 "$KEY"
systemctl restart xrdp xrdp-sesman
# 导出 DER 到 Windows 供信任
mkdir -p "$CER_DIR"
openssl x509 -in "$PEM" -outform DER -out "$CER_DIR/xrdp-localhost.cer"
'
```

然后在 Windows PowerShell（普通权限即可，导入的是**当前用户**存储，不需要管理员）：

```powershell
certutil -user -addstore -f Root "C:\Users\xinzo\openKylin桌面\xrdp-localhost.cer"
# 会弹"安全性警告"确认框 → 核对颁发者是 CN=localhost → 点【是】
```

下次双击启动器即直接进入 xrdp 登录窗，黄色警告永不再现。回滚：`cp` 还原两个 `.bak-<日期>` 文件后 `systemctl restart xrdp`，并在 `certmgr.msc`（当前用户）→ 受信任的根证书颁发机构里删除 `CN=localhost`。

**临时方案（不想改证书）**：在黄色警告框勾"**不再询问我是否连接到此计算机**"→ 点【**是**】，本机体验同样可用，只是证书不被信任的提示被记住而非消除。

### 4.2 xrdp 登录窗（每次连接）

1. 出现深色 **xrdp 登录窗**，三个地方：
   - **Session** 下拉：选 **`xorg`**（默认常是 Xvnc，务必改）；
   - **username**：`openkylin`；
   - **password**：`openkylin`（已改过则填新密码）；
2. 点【**OK**】；
3. 头几秒可能短暂黑屏（窗口管理器在启动，本机已加看门狗兜底），随后进入 UKUI 桌面——壁纸、底部任务栏、开始菜单、桌面图标齐全（2026-10-08 实测）；
4. 若持续黑屏超过 15 秒：看第 7 节 FAQ，不要反复重连。

---

## 5. 登录后第一件事：改掉默认密码

开始菜单打开"终端"（或在桌面空白处右键找终端），执行：

```bash
passwd
```

依次输入：旧密码 `openkylin` → 新密码两遍。**输入时屏幕不显示任何字符是 Linux 正常行为**，盲打完回车即可。改完牢记，忘记了可用第 7 节的重置命令。

---

## 6. 用完怎么关（四种"关"法区别很大）

| 操作 | 效果 | 什么时候用 |
|---|---|---|
| 直接关 mstsc 窗口（×） | **断开**会话，桌面在后台继续跑（下载、进程不断），重连恢复原样 | 临时切走、稍后回来 |
| UKUI 开始菜单 → 注销 | 结束图形会话（程序关闭），发行版仍运行 | 桌面卡死想重开图形会话 |
| `wsl --terminate openKylin-3.0-desktop` | **停止发行版**，释放其占用的内存 | 当天用完，推荐 |
| `wsl --shutdown` | 停止**所有** WSL 发行版（含 podman-machine 等） | 需要全局重置 WSL 网络/内核时 |

重新开始：再双击方式 A 的桌面图标即可，数据都在。

---

## 7. 常见问题速查

| 现象 | 处置 |
|---|---|
| mstsc 提示连不上/找不到计算机 | 发行版没启动：先跑第 3 节方式 B 的第 ① 步；再查端口：`wsl -d openKylin-3.0-desktop -- systemctl status xrdp`，挂了就 `wsl -d openKylin-3.0-desktop -u root -- systemctl restart xrdp` |
| 认证通过但**持续黑屏** | 窗口管理器没起来：90% 是 §2.2 的补丁没打；完整判别与修复见[双镜像文档 §5.1](wsl-dual-image-selection.md) 与 [xrdp 黑屏三层分诊法](../../../../retrospective/patterns/code-patterns/xrdp-black-screen-window-manager-triage.md) |
| 登录后**闪退回登录窗** | 会话启动即崩溃：在 WSL 里看 `tail -50 ~/.xsession-errors`，常见为磁盘满（见下行） |
| 忘记 openkylin 密码 | PowerShell 执行：`wsl -d openKylin-3.0-desktop -u root -- passwd openkylin`，直接设新密码 |
| 想改窗口大小/全屏 | mstsc 连接前点"显示选项"→ 显示标签拖分辨率，或全屏连接；.rdp 改 `desktopwidth/height` |
| 剪贴板互通 | 默认已开（`redirectclipboard:i:1`，xrdp-chansrv 提供）；失效时在 mstsc"本地资源"勾选剪贴板，重连 |
| 访问 Windows 文件 | Linux 内自动挂载：C 盘 `/mnt/c`、D 盘 `/mnt/d` |
| D 盘越来越大 | VHD 只增不减：先在 WSL 内清理，再 `wsl --shutdown` 后 `wsl --manage openKylin-3.0-desktop --compact`（实测可用） |
| 3390 端口被占/想换端口 | 改 `/etc/xrdp/xrdp.ini` 的 `port=` 后 `systemctl restart xrdp`，同步改启动器地址 |

安全红线：① 不要把 3390 映射到公网；② 改完弱口令再考虑长期使用；③ 长期挂着不用就 `wsl --terminate`。

---

## 8. 命令速查卡（PowerShell）

```powershell
$wsl = "$env:WINDIR\System32\wsl.exe"; $env:WSL_UTF8 = 1

& $wsl -l -v                                         # 看发行版状态
& $wsl -d openKylin-3.0-desktop -- /bin/true        # 开机（幂等）
& $wsl -d openKylin-3.0-desktop                      # 进命令行（exit 退出，桌面不受影响）
& $wsl -d openKylin-3.0-desktop -u root -- systemctl restart xrdp   # 重启远程桌面服务
& $wsl --terminate openKylin-3.0-desktop            # 停用本发行版
Start-Process mstsc.exe -ArgumentList '/v:localhost:3390'           # 连接桌面
```

---

## 9. 相关文档

- [openKylin 3.0 双 WSL 镜像对照与选型参考](wsl-dual-image-selection.md)（安装导入、§5 官方流程、§5.1 黑屏修复、磁盘规划）
- [openKylin 3.0 WSL 安装与稀疏 VHD 实操指南](wsl-install-sparse-vhd-guide.md)（336M 最小镜像安装、VHD 压缩与稀疏化）
- [xrdp 黑屏三层分诊法（模式）](../../../../retrospective/patterns/code-patterns/xrdp-black-screen-window-manager-triage.md)
```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261008-openkylin-desktop-startup-tutorial | msg=教程交付：Desktop WSL 日常启动 | ctx={"scenario":"knowledge","chain":"R-C（轻量，事实已实测）"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G4 | event=GATE_PASSED | session=sc-20261008-openkylin-desktop-startup-tutorial | msg=单一职责教程：启动器三方式+逐屏登录+关闭语义+FAQ+速查卡，全部锚定已实测命令
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=C4 | event=CERT_FIXED | session=sc-20261008-openkylin-desktop-wsl-install | msg=证书警告根治：重签CN=localhost/SAN覆盖localhost+127.0.0.1(原snakeoil备份)+导入CurrentUser根，重连直进登录窗无警告；教程§4.1/双镜像§5步骤7同步
```
