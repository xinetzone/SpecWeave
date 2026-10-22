---
type: Reference
id: "openkylin-kywc-display-architecture"
title: "openKylin 3 显示服务器双栈：kylin-wayland-compositor 与 KWin/Xorg 源码剖析（huanghe 本机核验）"
category: "tech"
tags:
  - openkylin
  - wayland
  - kywc
  - wlroots
  - kwin
  - ukui
  - wsl
  - source-analysis
date: "2026-10-08"
last_updated: "2026-10-08"
status: "verified"
author: "SpecWeave Agent（方法论编排 session sc-20261008-openkylin-source-deepdive）"
summary: "以 openKylin-3.0-desktop WSL（huanghe）本机包/会话/设备只读核验结合 Gitee kylin-wayland-compositor（openkylin/huanghe 分支）源码审阅，还原 openKylin 3 的显示服务器双栈：物理态默认 Wayland 合成器 kywc（基于 wlroots 0.17 的 C 项目，drm/fbdev/嵌套三后端、兼容 KDE Plasma 与 UKUI 私有协议、用户态 systemd 拉起 ukui-session），与 xrdp/Xorg 路径使用的 KWin 5.24 X11 栈并存；并以 WSL 无 /dev/dri、无 /dev/fb*、仅有 /dev/dxg + WSLg weston(rdp-backend) 的设备事实，界定 WSL 用户实际处于 X11 孤岛，kywc 嵌套 WSLg 仅源码可行而未实测。"
security_level: "public"
knowledge_type: "conditional"
validation_status: "verified"
source: "一手信源：① openKylin-3.0-desktop WSL（huanghe，WSL 3.0.2.0/内核 6.18.40）本机 dpkg/apt、/usr/share/{wayland-sessions,xsessions}、systemd user 单元、/dev 设备节点、/mnt/wslg/weston.log 只读核验（2026-10-08）；② Gitee openKylin/kylin-wayland-compositor 仓库 openkylin/huanghe 分支浅克隆（1.3.1-ok33 世代，3652 提交），审阅 src/backend、protocols/、data/、docs/PROTOCOLS.md、docs/ENV.md、meson_options.txt。采集于 2026-10-08。范围限定 openKylin 3（huanghe）。"
---

# openKylin 3 显示服务器双栈：kywc 与 KWin/Xorg

> 落机阶段我们在 xrdp 桌面里遇到的 WM 是 KWin（[F-055/F-057](wsl-dual-image-selection.md)），而 openKylin 3 发布稿与源码仓库的"默认显示服务器"却是另一个名字——**kylin-wayland-compositor（kywc）**。本文用本机包事实 + huanghe 分支源码回答：openKylin 3 到底有几个显示服务器、各走什么路径、为什么我们在 WSL 里见到的是 KWin 而不是 kywc。
>
> 姊妹篇：[AI 子系统源码架构剖析](ai-subsystem-source-architecture.md)。范围限定 openKylin 3（huanghe）。

## 1. 结论先行

1. openKylin 3 **同机安装两套显示服务器**：Wayland 侧 `kylin-wayland-compositor 1.3.1-ok33`（kywc，wlroots 0.17 系，纯 C，不依赖 Qt/GTK），X11 侧 `kwin-x11 5.24.4`（KDE KWin，UKUI 旧会话）；会话描述符各一个：`wayland-sessions/kylin-wlcom.desktop` 与 `xsessions/ukui.desktop`。
2. kywc 是**物理/硬件态默认**：登录器选 "Kylin Wlcom" → `kylin-wlcom-wrapper` 经 **systemd 用户总线**拉起 `kylin-wlcom.target/.service`，`ExecStart=kylin-wlcom -s ukui-session`；后端自动选择为**嵌套优先（WAYLAND_DISPLAY/DISPLAY 存在时走 wlroots 嵌套）→ DRM（多 GPU 选择）→ fbdev 兜底**。
3. 为承载 Qt 技术栈的 UKUI，kywc 实现了**大量 KDE Plasma 兼容协议**（plasma-shell、plasma-window-management、kde-output、blur/slide 等）外加 7 个 UKUI 私有协议与 5 个 kywc 私有协议——它不是 wlroots 演示合成器，而是按 UKUI 桌面需求量身定制的产品级合成器。
4. **本 WSL 设备面不满足 kywc 硬件后端**：无 `/dev/dri`、无 `/dev/fb*`，仅有 DXGI 透传 `/dev/dxg`；WSLg 是系统发行版里 weston 9.0（rdp-backend + rdprail-shell）。我们落机走的 xrdp→Xorg(xorgxrdp)→KWin 路径完全不经过 kywc。
5. kywc 源码存在嵌套分支，理论上可作为 WSLg weston 的嵌套客户端启动，**但未实测，不能宣称可用**（父合成器是 RDP rail 壳，存在输出/输入协议约束）；WSL 上桌面问题的排查经验不能在两套会话间直接搬运。

## 2. 双栈同机事实（huanghe 包/会话核验）

| 事实项 | Wayland 栈 | X11 栈 |
|---|---|---|
| 合成器/WM 包 | `kylin-wayland-compositor 1.3.1-ok33`（候选 1.3.1-ok36），配套 `-client`（libkywc）、`-tools`、`xdg-desktop-portal-wlcom` | `kwin-x11 4:5.24.4-ok11~0731.1`（+kwin-common/data、libkwineffects/libkwinglutils） |
| 技术基线 | wlroots `libwlroots12 0.17.4`，wayland 1.26，libinput/libdrm/libseat，pipewire，libeis | Qt 5.15（kwayland/qtwayland 共存，供 XWayland 与混合迁移期使用） |
| 会话入口 | `/usr/share/wayland-sessions/kylin-wlcom.desktop` → `Exec=kylin-wlcom-wrapper` | `/usr/share/xsessions/ukui.desktop` |
| 可执行 | `/usr/bin/kylin-wlcom`（+wrapper） | `/usr/bin/kwin_x11` |
| 进程拉起 | **systemd 用户单元** `/usr/lib/systemd/user/kylin-wlcom.{service,target}`（`systemctl status` 默认查系统单元故"找不到"） | 会话脚本 `startwm.sh`→`ukui-session` 拉起（落机 F-057 链路） |
| X 兼容 | 内建 xwayland（默认开启、lazy 启动，`-Dnoxwayland` 可关） | 原生 X11 |
| 本机使用情况 | 已安装、未运行（无硬件后端、未从 WSLg 嵌套启动） | xrdp 登录实际使用（F-055/F-057） |

辅助包：`grim`/`wl-Clipboard`（Wayland 截图剪贴板）、`xwayland 24.1`、`libva-wayland2` 等均已就位——Wayland 用户态生态是完整安装的。

## 3. kywc 架构（源码：openkylin/huanghe 分支）

### 3.1 项目身份

- 定位（README 原文）："基于 wlroots 编写的 wayland 合成器……作为默认显示服务器随 openKylin 系统发布"；致谢参考 wlroots/sway/wayfire/labwc。
- 规模与活跃度：C 95.8%、C++ 1.8%、Meson 0.9%；3652 次提交、92 个标签、11 个分支；取证当天仍有 hourly 提交（朝鲜语 Weblate 翻译等）。
- 许可：GPL-1.0-or-later（`LICENSES/` 另含 LGPL-2.1、MIT-CMU、MulanPSL-2.0 片段许可）。
- 打包：meson + debhelper，源内 `debian/`，huanghe 变更日志显示 1.3.1-ok30~ok33 为 2026-08 密集打包（ok33 "fix build package"，2026-08-20）。

### 3.2 后端自动选择（src/backend/backend.c）

`backend_autocreate()` 三级策略：

1. **嵌套优先**：若环境存在 `WAYLAND_DISPLAY`/`WAYLAND_SOCKET`/`DISPLAY`，直接 `wlr_backend_autocreate()`——由 wlroots 自行选 Wayland 或 X11 嵌套后端，不需要 logind session；
2. **DRM 为主**：否则创建 multi backend，枚举 `drm` 子系统 render node 且要求 `drmIsKMS()`；主 GPU 优先级为 boot_display → boot_vga → 首个 PCI → USB（源码注释显式照顾国产/D3000M 与 UDL USB 显卡场景），支持多 GPU 与热插拔等待（5s）、logind session 激活等待（10s）；
3. **fbdev 兜底**：DRM 失败或 `KYWC_BACKEND=fbdev` 时枚举 `fb[0-9]*`（`KYWC_FB_DEVICES` 可指定）；再叠加 libinput 输入后端。

渲染器可选 `KYWC_RENDERER=gl|gles2|pixman|vulkan`，允许 `KYWC_RENDERER_ALLOW_SOFTWARE`（llvmpipe）；DRM 侧有原子提交/modifiers/色彩管理/直扫（direct scanout）开关（docs/ENV.md）。另有 **EIS 后端**（libeis，配合 portal 的远程桌面输入注入）与独立 logind session 层。

### 3.3 会话拉起链路：wrapper → user systemd → ukui-session

`kylin-wlcom-wrapper`（data/wrapper.c，很小的 C 程序，只链 libsystemd）：

1. 连接**用户级 D-Bus**（`sd_bus_open_user`）；
2. 向 systemd 管理器 `StartUnit("kylin-wlcom.target", "replace")`；target `Requires/BindsTo` service；service 定义 `ExecStart=kylin-wlcom -s ukui-session`、`Slice=session.slice`、`Before=graphical-session.target`；
3. 主动把 `XAUTHORITY`、`WAYLAND_DISPLAY`、`WAYLAND_SOCKET` 及 `XDG_*` 从 systemd 管理器环境中 `UnsetEnvironment`（保证合成器不继承登录器残留环境）；
4. 订阅 target 的 `PropertiesChanged`，target 转 inactive 即退出。

这与 X11 侧靠 `startwm.sh`+`ukui-session` 直接 fork 的模型完全不同——Wayland 桌面的生命周期由 **systemd user 实例**托管。

### 3.4 协议面：以 KDE 兼容层托住 UKUI

docs/PROTOCOLS.md 与 protocols/ 源文件的交集显示：

- **标准**：xdg_wm_base v5、presentation、viewporter、cursor-shape、fractional-scale、tearing-control、security-context、drm-syncobj、xdg-activation/dialog/toplevel-drag 等较新 staging 协议；linux-dmabuf v4、screencopy、layer-shell、foreign-toplevel、data-control、primary-selection、relative-pointer、pointer-gestures、tablet v2、text-input v1/v2/v3；
- **KDE Plasma 兼容**（Qt/UKUI 生态所需）：plasma-shell、plasma-window-management（17 个事件）、kde-output-management/device、kde-primary-output、kde-blur、kde-slide、kde-keystate、plasma-virtual-desktop、server-decoration；
- **UKUI 私有**（上游 `kylin-wayland-protocols`）：ukui-shell、ukui-window-management、ukui-output-management、ukui-blur、ukui-effect、ukui-background、ukui-startup；
- **kywc 私有**：kywc-capture/output/security/toplevel/workspace 五个 manager v1；
- xwayland-shell v1 已支持，X11 应用经 XWayland 纳入同一窗口管理。

### 3.5 桌面配套

- **portal 后端** `xdg-desktop-portal-wlcom`：screenshot/screencast（pipewire 流）/remote desktop/input capture（libeis）/access，配置 `org.freedesktop.impl.portal.desktop.wlcom.service`；
- **libkywc 客户端库**：toplevel/workspace/output/capture/stream/thumbnail C API（`-client` 包），供 UKUI 组件与 examples/ 内 QML 示例（缩略图、特效测试、虚拟桌面等）调用；
- **特效/输入**：魔法灯、模糊、滑动、缩放、水印、鼠标轨迹/定位、调色、showfps 等（GLSL shaders 内建）；触摸板/屏手势、全局快捷键、输入法 v2/v3、多指针/瞬态 seat；
- 文档化已知问题仅 1 条：部分不按 SDK 设置的应用出现双标题栏（应用侧需改）。

## 4. 为什么本 WSL 的桌面是 KWin 而不是 kywc

设备面三条硬事实（2026-10-08 本机）：

1. `ls /dev/dri` → **不存在**；`ls /dev/fb*` → **不存在**；仅有 `/dev/dxg`（Windows DXGI 透传，非 Linux DRM/KMS、非 fbdev）；
2. WSLg 真实形态（`/mnt/wslg/weston.log`）：系统发行版内 **weston 9.0.0，`--backend=rdp-backend.so --shell=rdprail-shell.so --socket=wayland-0 --xwayland`**——wayland-0 是 RDP rail 模式的 weston，不是通用嵌套宿主；
3. 我们的交互桌面链路（F-055/F-057）：Windows mstsc → xrdp:3390 → **xorgxrdp Xorg** → ukui.desktop 会话 → **KWin X11**。

对照 §3.2 的后端策略：DRM 与 fbdev 两条路在本机无设备节点，必然失败；唯一可能的嵌套路要求 kywc 以 WAYLAND_DISPLAY=wayland-0 连入 WSLg 的 weston——源码支持，但 rdprail-shell 是为 Windows 窗口托盘化设计的定制 shell，能否正确托管一个完整嵌套桌面（全屏 surface、输入、portal）**没有验证过**，本文只登记为"源码级可行的 POC 候选"，不作为可用结论。

## 5. V 对抗审查：边界与误判排除

1. **不把"默认显示服务器"读成"WSL 默认"**：kywc 的默认性针对物理机/虚拟机 DRM 态；在 xrdp/WSL 这条远程 X11 路径上，事实默认是 KWin。发布材料未区分会话类型，是双栈混淆的根源。
2. **嵌套可行性未实测**：`backend_autocreate` 的嵌套分支是源码事实；"能在 WSLg 出图"是运行时命题，二者不得合并下结论。真要验证需另起 POC（在 WSLg 会话内以普通用户启动 `kylin-wlcom`，观察能否得到嵌套窗口与输入）。
3. **版本快照口径**：1.3.1-ok33 为已装、ok36 为候选（取证时 huanghe main 已有更新）；本文源码注释/协议清单以 huanghe 分支近 tip 为准，ok33 个别 backport 差异未逐文件比对。
4. **黑屏修复不可跨栈套用**（与 F-057 的关系）：F-057 的修复点是 X11 会话 `startwm.sh` unset `XDG_RUNTIME_DIR` 导致 KWin 不驻留；kywc 路径由 wrapper+systemd user 管理，wrapper 本身就主动清理继承环境并依赖 user manager 提供 `XDG_RUNTIME_DIR`——两套会话的环境契约不同，Wayland 侧若出黑屏需按 kywc 链路（`~/.log/kylin-wlcom.log`、user journal、`KYWC_LOG_LEVEL=DEBUG`）重新取证，不能照搬 `~/.xsession` 看门狗。
5. **GPU 加速表述克制**：本机 `/dev/dxg` + Microsoft Basic Render Driver 意味着即使跑起嵌套 kywc，Linux 侧 GL 也走 WSLg 的软件/半虚拟路径，`vulkan/gles2` 渲染器表现不能按物理 GPU 预期。

## 6. 对适配者的可操作要点

- 判断客户/应用运行在哪套栈：看会话类型（`XDG_SESSION_TYPE=wayland|x11`）与 `WAYLAND_DISPLAY`/`DISPLAY`，不要只看 UKUI 版本号；
- 物理机适配 kywc：关注点是 DRM/KMS 兼容性（可用 `KYWC_DRM_DEVICES` 指定、`KYWC_DRM_NO_ATOMIC` 排障）、无 KMS 的国产老卡走 fbdev、多 GPU 用 boot_vga 优先级；日志 `$HOME/.log/kylin-wlcom.log` 或 `-Dlogtostdout`；
- 应用侧窗口/特效/截图：Wayland 下必须走协议（plasma/ukui/xdg-desktop-portal），无 X11 那种直接抓屏/改窗口的通道；不按 SDK 做自绘标题栏会双标题栏；
- WSL/远程桌面场景：openKylin 3 当前可靠路径仍是 xrdp+Xorg+KWin（见[桌面启动教程](wsl-desktop-startup-tutorial.md)），不要预期 kywc 可用。

## 7. 相关文档

- [双 WSL 镜像对照与选型参考](wsl-dual-image-selection.md)——F-055/F-057 交互桌面与黑屏排障
- [openKylin 桌面启动与日常使用教程](wsl-desktop-startup-tutorial.md)——xrdp+Xorg 路径日常操作
- [AI 子系统源码架构剖析](ai-subsystem-source-architecture.md)——同批源码核验姊妹篇
- [04 桌面使用](../concepts/04-desktop-usage.md)——文档站桌面功能导读
- [信源台账](source-inventory.md)——S35

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R3 | event=CONCEPT_COMPLETED | session=sc-20261008-openkylin-source-deepdive | msg=显示栈R完成：双服务器/kywc后端与会话/协议矩阵/WSL设备边界 | ctx={"facts":"F-078~F-086"}
```
