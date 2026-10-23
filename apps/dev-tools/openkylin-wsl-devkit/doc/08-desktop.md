---
type: "Tutorial"
title: "okw 桌面：UKUI（xrdp/WSL）预检、补齐与验收"
---

# okw 桌面：UKUI（xrdp/WSL）预检、补齐与验收

`okw desktop` 把 openKylin 桌面 WSL 镜像上**已实测**的桌面链路封装为 CLI：发行版内预装的 UKUI 桌面经 xrdp（默认端口 **3390**）供 Windows 侧 `mstsc` 连接。本文说明三步流程、它补齐什么、以及为什么**不安装桌面套件**。

> **先确认 `<name>`**：下文 `<name>` 是**已预装桌面的** openKylin Desktop WSL 发行版名称（如 `openKylin-3.0-desktop`）。先在 PowerShell 运行 `wsl -l -v` 查看并把 `NAME` 原样填入。最小镜像（无 xrdp）不适用本命令。

## 桌面链路是什么

打开桌面需要两步：让发行版运行起来 → 从 Windows 用远程桌面连 `localhost:3390`。

```text
Windows 桌面
   │  mstsc（远程桌面连接，localhost:3390）
   ▼
xrdp / xrdp-sesman（发行版内，systemd 拉起）
   │
   ▼
openKylin-3.0-desktop（WSL2，未用时为 Stopped）
```

连接地址统一用 **`localhost:3390`**：WSL 重启后内网 IP 会漂移，`localhost` 转发稳定（2026-10-08 实测）。登录窗 **Session 下拉务必选 `xorg`**，用户名 `openkylin`，初始密码 `openkylin`（首登后立即 `passwd` 修改）。

## 命令流程

```text
okw desktop launch   <name>
okw desktop preflight <name>
okw desktop install  <name> --yes
okw desktop verify   <name>
```

1. `launch` **一键启动**：启动发行版（幂等）→ 等 `localhost:<port>` 就绪 → 拉起 `mstsc`。这是最常用的命令——因为「连不上」的首要原因通常就是发行版处于 `Stopped`（见下节 FAQ）。
2. `preflight`（只读）检查结构项（发行版/WSL2/openKylin 身份/systemd）与运行时项（xrdp 与 xrdp-sesman 服务、发行版内 `:3390` 监听、默认用户 UID、`~/.xsession` 看门狗补丁）；不写文件、不改服务。
3. `install` 必须显式提供 `--yes`。省略时仅打印副作用清单，以退出码 2 中止，不做写入。
4. `verify`（只读）在 preflight 同一批检查之上，附加**Windows 侧 `localhost:<port>` 回环可达性**。

退出码：`0` 全通过 / `1` 有 FAIL（按中文指引修复后重试）/ `2` 用法错误或 `install` 缺 `--yes`。

## install 会执行什么

提供 `--yes` 后，工具依次执行（仅在**已预装**桌面的镜像上）：

1. 结构门：发行版/WSL2/openKylin/systemd 必须就绪，且发行版内存在 `xrdp` 可执行文件；否则 FAIL 中止（不会去 `apt` 安装桌面套件）。
2. 以 **root** 身份 `systemctl enable --now xrdp xrdp-sesman`（幂等启用并启动）。
3. 以**默认用户**身份补齐 `~/.xsession`：若已含 `XDG_RUNTIME_DIR` 与 `kwin_x11` 标记则跳过；否则先 `cp` 备份为 `~/.xsession.bak-<时间戳>`，再写入首登黑屏看门狗补丁（可逆）。
4. 只读复验桌面链路就绪度。

> 回滚：`cp ~/.xsession.bak-<时间戳> ~/.xsession` 后重连即可。

## 为什么需要 `~/.xsession` 看门狗

openKylin 3.0 Desktop WSL 镜像**首次登录会纯黑屏**（xrdp 登录窗认证通过、窗口连上，但进入后整屏黑、无任务栏）。根因是 KWin 窗口管理器（`kwin_x11`）冷启动不驻留：`/etc/xrdp/startwm.sh` 在启动会话前 `unset XDG_RUNTIME_DIR`，`kwin_x11` 回退到无效运行时目录、冷启动即退出，而会话不会二次拉起。

修复（用户级、可逆、不动系统文件、不装包）：在 `~/.xsession` 补回 `XDG_RUNTIME_DIR`，并加一个前 ~15 秒、仅在 WM 缺失时幂等补拉的看门狗，最后 `exec ukui-session`。`okw desktop install` 正是落地这段实测脚本。

```sh
#!/bin/sh
[ -z "$XDG_RUNTIME_DIR" ] && export XDG_RUNTIME_DIR="/run/user/$(id -u)"
(
  sleep 3
  for n in 1 2 3 4 5 6; do
    pgrep -x kwin_x11 >/dev/null 2>&1 && exit 0
    kwin_x11 --replace >/tmp/kwin-watchdog.log 2>&1 &
    sleep 2
  done
) &
exec ukui-session
```

## 常见问题：mstsc 提示「无法连接到远程计算机」

**首要原因：发行版处于 `Stopped`。** WSL2 发行版是**按需启动**的（无运行进程/闲置后会停），发行版一停，xrdp 随之停止，`localhost:3390` 自然没有监听——这与「没装好」无关。

处置顺序：

1. 先启动发行版（任何命令都会触发开机）：`wsl -d <name> -- /bin/true`，或双击你自己的一键启动器。
2. 等 `:3390` 就绪（首次约数秒）后再连；`okw desktop verify <name>` 会**连带 Windows 侧回环端口**一起检查，全 PASS 即代表已可连。
3. 仍连不上时：若改过 `/etc/xrdp/xrdp.ini` 的端口，用 `okw desktop verify <name> --port <端口>` 复核；服务异常可在发行版内 `systemctl status xrdp`，重启 `sudo systemctl restart xrdp`。

> 根因与完整启动/关闭语义见 [Desktop WSL 桌面启动教程](../../../../docs/knowledge/tech/openkylin/docs-wiki/references/wsl-desktop-startup-tutorial.md)（§1 为什么不能「直接点图标」、§3 日常启动、§6 用完怎么关）。

## 边界

- `okw desktop` **不安装桌面套件**、不改软件源、不改 `wsl.conf`、不推送凭据；只作用于**已预装**桌面的 Desktop WSL 镜像。
- 不自动下载或导入镜像；选型与导入见[双 WSL 镜像对照与选型参考](../../../../docs/knowledge/tech/openkylin/docs-wiki/references/wsl-dual-image-selection.md)。
- 桌面使用的证书提示、登录、关机语义与 FAQ 见[桌面环境与基础使用](../../../../docs/knowledge/tech/openkylin/docs-wiki/concepts/04-desktop-usage.md)与 [Desktop WSL 桌面启动教程](../../../../docs/knowledge/tech/openkylin/docs-wiki/references/wsl-desktop-startup-tutorial.md)。

> 上一篇：[AI 栈：本地 OCR](07-ai-stack.md)

## 相关页面

- [文档首页](index.md)：工具定位、环境要求与全部主题入口。
- [命令参考](02-command-reference.md)：`okw desktop` 的命令速查与端口说明。
- [AI 栈（本地离线 OCR）](07-ai-stack.md)：同为「预检 → 显式补齐 → 只读验收」结构。
