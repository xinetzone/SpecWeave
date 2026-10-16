# R1 事实簇：构建/启动/配置/打包

> 采集对象：`external/dao/action/kylin-wayland-compositor`（kywc / kylin-wlcom），固定提交 `4df656222427f3cd0101e41d828fb64805e66c15`（分支 openkylin/huanghe）。
> 采集模式：只读。未执行 checkout、未执行任何 git 写操作、未修改源仓库任何文件。
> 证据路径均相对仓库根；行号取自本次磁盘原文。口径标注「脚本」者均在 PowerShell 7 实跑复核。

## 采集范围与计数总览

| 指标 | 值 | 口径 / 命令 |
|---|---|---|
| meson_options.txt 选项数 | 44 | 脚本：`[regex]::Matches((Get-Content meson_options.txt -Raw), "option\('([^']+)'")` = 44，与基线一致 |
| 选项类型分布 | boolean 37 / feature 3 / string 4 | 脚本按 `type :? '...'` 归类（feature：libunwind、libxcb-errors、nls） |
| boolean 默认值 | true 35 / false 2 | 默认 false：`ukui_theme`、`tracy` |
| kylin-wlcom CLI 短选项 | 6（h/d/D/s/v/V） | 脚本/源码：main.c:198 getopt 串 `"hdD:s:vV"`；其中仅 `D`、`s` 带参数 |
| kylin-wlcom 长选项 | 5（help/debug/version/session/verbose） | main.c:38-42 `long_options[]`；`-D` 无对应长选项 |
| `-D` 调试 flag 数 | 6 | main.c:70-82：noxwayland/logtostdout/loginmtime/lognoratelimit/nosessionbinding/nolazyxwayland |
| docs/ENV.md 条目 | 21（其中 KYWC_* 15、XCURSOR_* 2、应用侧 4） | 脚本：星号粗体条目 21；KYWC_* 出现 15 |
| 源码 getenv 调用点 | 27 处 / 24 个去重变量名（合成器本体 17 个 KYWC_* + 7 个标准变量） | 脚本：全仓 `*.c/*.cpp/*.h` grep `getenv\(`；data/wrapper.c:21 为通用变量名遍历不计入 |
| debian 二进制包数 | 5 | 脚本：`Select-String '^Package:' debian/control` = 5；对应 5 个 `.install` 文件 |
| debian changelog 版本条目 | 75 | 脚本：`Select-String '^kylin-wayland-compositor \('` = 75；顶端 `1.3.1-ok36`（huanghe） |
| tools/ 文件数 | 55（不含 translations/）/ 82（含 26 个 .ts 及 meson.build） | 脚本 `Get-ChildItem -Recurse -File`；3 个子工具：wlcctrl、wldialog、magnifier |
| wlcctrl 子命令数 | 42 | 脚本：commands.c 中 `^    { "` 表项 = 42 |
| protocols/*.xml | 34 | 与基线一致 |
| po：LINGUAS / .po | 16 / 27 | 脚本计数非空行与目录文件 |
| data/ 顶层文件 | 9 + udev-rules/ 1 个规则 | 与基线一致 |
| qtkey KeyTbl 有效映射 | 273 条（另有 29 条注释掉） | 脚本：qtkey_mapper.c 中 `^\s*\{ XKB_KEY_` = 273，`// { XKB_KEY_` = 29 |
| src/config C/H 文件 | 9（+ meson.build） | common.c/config.c/config_p.h/kde_global_accel.c/kde_input.c/qtkey_mapper.c/ukui_gsettings.c/ukui_shortcut.c/ukui_view_mode.c |

---

## 项目元信息与版本

### F-R1-001 — meson 工程名 kylin-wayland-compositor，仅 C 语言，声明协议 GPL-1.0-or-later，project version 为 1.3.0
- 证据：meson.build:1-11
- 细节：`project('kylin-wayland-compositor', 'c', license: 'GPL-1.0-or-later', version: '1.3.0', default_options: ['b_ndebug=if-release', 'c_std=c11', 'warning_level=2'])`

### F-R1-002 — 编译时版本字符串 KYWC_VERSION 优先取 dpkg-parsechangelog，其次追加 git 短 hash
- 证据：meson.build:39-54
- 细节：`version` 初值为 project_version；找到 `dpkg-parsechangelog` 时以 `dpkg-parsechangelog -SVersion` 输出覆盖（L42-45）；找到 git 时追加 `".g" + git rev-parse --short=7 HEAD`（L49-51）；最终 `-DKYWC_VERSION="..."`（L54）

### F-R1-003 — debian/changelog 顶端版本为 1.3.1-ok36，发行版代号 huanghe，日期 2026-09-04，维护者 Morose
- 证据：debian/changelog:1-11
- 细节：`kylin-wayland-compositor (1.3.1-ok36) huanghe; urgency=medium`，变更说明 "fix update error"，`Morose <chenlinxiang@kylinos.cn>  Fri, 04 Sep 2026 15:00:18 +0800`；近三条 ok34/ok35/ok36 均为 2026-09 月条目

### F-R1-004 — 主可执行文件名为 kylin-wlcom，由编译宏 TARGET_NAME 注入
- 证据：meson.build:315-325；src/main.c:45
- 细节：root `executable('kylin-wlcom', ..., c_args: '-DTARGET_NAME="kylin-wlcom"')`；usage 字符串 `"Usage: " TARGET_NAME " [options] [command]\n"`

### F-R1-005 — 源码头部统一使用 SPDX 双行声明（KylinSoft Co., Ltd. / GPL-1.0-or-later）
- 证据：src/main.c:1-3；src/server.c:1-3；src/config/config.c:1-3；data/wrapper.c:1-3（年份 2025）；tools/wlcctrl/main.c:1-3（年份 2025）
- 细节：main.c/server.c/config.c 为 `SPDX-FileCopyrightText: 2023 KylinSoft Co., Ltd.`；wldialog Main.cpp 为 2026 年；ukui_gsettings.c/ukui_shortcut.c/ukui_view_mode.c 为 2024 年

### F-R1-006 — debian/copyright 为 6 行 DEP-5 简版，仅声明全局一条 Files: * 记录
- 证据：debian/copyright:1-6
- 细节：`Format: .../copyright-format/1.0/`；`Upstream-Contact: chenlinxiang@kylinos.cn`；`Files: *` / `Copyright: 2023, KylinSoft Co., Ltd.` / `License: GPL-1.0-or-later`

### F-R1-007 — LICENSES/ 目录含 4 个协议全文文件
- 证据：LICENSES/GPL-1.0-or-later.txt（12335B）、LGPL-2.1-or-later.txt（26142B）、MIT-CMU.txt（1157B）、MulanPSL-2.0.txt（9363B，木兰宽松许可证第2版）
- 细节：脚本读取各文件首行确认协议文本类型

## 依赖与版本约束

### F-R1-008 — wlroots 依赖固定在 0.17 系列，且以一组 default_options 约束其 subproject 构建
- 证据：meson.build:56-61
- 细节：`dependency('wlroots', default_options: ['default_library=static', 'examples=false', 'renderers=vulkan', 'backends=x11', 'xwayland=disabled', 'session=disabled'], version: ['>=0.17.0', '<0.18.0'])`；L63 全局 `-DWLR_USE_UNSTABLE`

### F-R1-009 — 根 meson 声明的核心依赖及版本下限
- 证据：meson.build:74-97
- 细节：wayland-server `>=1.23.0`（L74）、wayland-protocols `>=1.36`（L75）、xkbcommon 无版本（L76）、libdrm（L77）、libinput `>=1.19`（L78）、pixman-1（L79）、json-c `>=0.13`（L81）、libsystemd（变量 sdbus，L82）、librsvg-2.0 `>=2.46`（L89）、libudev（L92）、gbm `>=21.1`（L94）、libdisplay-info（L96）、libpipewire-0.3（L97）；另有 m/dl/rt/threads、cairo/pango/pangocairo/libjpeg/libpng

### F-R1-010 — libunwind 为 feature(auto) 可选依赖，经 HAVE_LIBUNWIND 宏条件编译
- 证据：meson.build:93、178；src/util/debug.c:12、83-92
- 细节：`dependency('libunwind', required: get_option('libunwind'))`；启用时 `debug_backtrace()` 用 libunwind（`#define UNW_LOCAL_ONLY`），否则回退 glibc `backtrace()`（BACKTRACE_SIZE 256，配合 dladdr）

### F-R1-011 — tracy 为默认关闭的可选 profiler 依赖，版本限定 0.11 系列
- 证据：meson.build:218-225；meson_options.txt:198-202
- 细节：启用时 `dependency('tracy', default_options: ['default_library=static'], version: ['>=0.11.0','<0.12.0'])`，加 `-DTRACY_ENABLE` 并入 wlcom_deps

### F-R1-012 — ukui_gsettings 条件引入 glib-2.0 >= 2.64
- 证据：src/config/meson.build:33-39
- 细节：`if have_ukui_gsettings` 时 `glib = dependency('glib-2.0', version: '>= 2.64')` 并加入 wlcom_deps；对应源文件直接 `#include <gio/gio.h>`（ukui_gsettings.c:6）

### F-R1-013 — xwayland 子构建固定拉取 9 个 xcb 库并探测 xwayland 程序变量
- 证据：src/xwayland/meson.build:1-58
- 细节：`xwayland_required` 字典含 xcb、xcb-composite、xcb-ewmh、xcb-icccm、xcb-render、xcb-res、xcb-shape、xcb-xfixes、xcb-sync（L35-45）；libxcb-errors 可选（L46-48、56）；`dependency('xwayland', required: false, fallback: 'xserver', default_options: ['werror=false','xvfb=false'])`（L3-11）

### F-R1-014 — XWAYLAND_PATH 宏默认 /usr/bin/Xwayland，并导出 4 个 HAVE_XWAYLAND_* 特性宏
- 证据：src/xwayland/meson.build:13-32
- 细节：特性名 listenfd/no_touch_pointer_emulation/force_xrandr_emulation/terminate_delay（L13-18）；set_quoted XWAYLAND_PATH（L21、27）、set10 HAVE_XWAYLAND_<NAME>（L24、29）、HAVE_XCB_ERRORS（L32）

### F-R1-015 — xwayland 源文件集合含 12 个 C 文件加 selection/ 子目录
- 证据：src/xwayland/meson.build:62-76；条件门控 src/meson.build:23-25
- 细节：config.c/eavesdrops.c/grab.c/shell.c/server.c/sockets.c/unmanaged.c/view.c/xauth.c/xwayland.c/xwm.c + `subdir('selection')`；src/meson.build 中 `if have_xwayland` 才进入

### F-R1-016 — debian/control Build-Depends 与 meson 依赖存在版本/项目差异
- 证据：debian/control:5-33
- 细节：构建依赖含 debhelper-compat (=13)、meson (>=0.59.0)、libwlroots-dev (>= 0.17.4-ok19)、libjson-c-dev (>=0.15)、scdoc、quilt、hwdata、qtbase5-dev/qtbase5-private-dev/qtdeclarative5-dev/qttools5-dev/qtquickcontrols2-5-dev、libgsettings-qt-dev、libkysdk-waylandhelper-dev、libeis-dev、libei-dev、libpipewire-0.3-dev、libepoxy-dev、libssl-dev、libxcb-shape0-dev 等；Standards-Version 4.6.2

### F-R1-017 — README 运行时依赖清单与 meson 实际依赖不一致（README 列 libseat，meson 未声明 libseat）
- 证据：README.md:30-36；meson.build:74-97
- 细节：README 列 "wlroots, wayland, libinput, xkbcommon / libseat, libdrm, libsystemd, librsvg-2.0 / cairo, pango, pangocairo, pixman-1 / gbm, json-c, libudev / xwayland, xcb (optional)"；meson 中无 libseat dependency，且 wlroots 以 `session=disabled` 构建（meson.build:59）；meson 另含 README 未列的 libdisplay-info、libpipewire、libunwind
- 备注：差异本身为客观事实；"是否遗漏"属推断，V 阶段再判

## meson 选项（44 个全量）

### F-R1-018 — meson_options.txt 共 44 个 option，脚本复核与基线一致
- 证据：meson_options.txt:1-259
- 细节（逐名，脚本顺序）：plugin_directory、libunwind、xwayland、libxcb-errors、examples、nls、libkywc、drm_lease_device、alpha_modifier、kde_output、kde_virtual_desktop、wlr_output、wlr_foreign_toplevel、wlr_layer_shell、kde_global_accel、kde_input、kde_plasma_shell、kde_plasma_window_management、kde_blur、kde_slide、ukui_screenshot、ukui_shortcut、ukui_gsettings、ukui_theme、kde_keystate、kde_clipboard、ukui_watermark、ukui_shell、ukui_window_management、ukui_output、ukui_blur、ukui_effect、ukui_startup、tracy、ukui_view_mode、ukui_output_config、ukui_background、xdg_toplevel_icon、xdg_toplevel_tag、extra_icon_path、extra_apps_path、extra_pixmap_path、tools、portal

### F-R1-019 — 选项类型分布为 37 boolean、3 feature（libunwind/libxcb-errors/nls）、4 string
- 证据：meson_options.txt:7-11（libunwind feature）、18-22（libxcb-errors feature）、30-34（nls feature）、1-5/234-247（4 个 string）
- 细节：string 选项为 plugin_directory（value `''`）、extra_icon_path、extra_apps_path、extra_pixmap_path（后三者声明中无 value 字段）

### F-R1-020 — 37 个 boolean 中 35 个默认 true，仅 ukui_theme 与 tracy 默认 false
- 证据：meson_options.txt:138-142（ukui_theme value false，"Enable ukui widget theme support"）、198-202（tracy value false）
- 细节：脚本统计 value:true=35、value:false=2

### F-R1-021 — 每个协议/功能选项都映射为 -DHAVE_* 0/1 编译宏（32 个 HAVE 宏）
- 证据：meson.build:177-210
- 细节：如 `-DHAVE_KDE_GLOBAL_ACCEL=@0@`、`-DHAVE_UKUI_SHORTCUT=`、`-DHAVE_XDG_TOPLEVEL_TAG=` 等；xwayland 单独产出 `-DHAVE_XWAYLAND=`（meson.build:69-72）；libunwind 用 found() 结果（L178）

### F-R1-022 — 三个 extra_* string 选项经 -D 宏同时传给 C 与 C++
- 证据：meson.build:212-216
- 细节：`-DEXTRA_ICON_PATH="..."`、`-DEXTRA_APPS_PATH="..."`、`-DEXTRA_PIXMAP_PATH="..."`，`language: ['c','cpp']`

### F-R1-023 — plugin_directory 为空时回退 ${prefix}/lib/kylin-wlcom/plugins，并经 PLUGIN_DIR 宏传入
- 证据：meson.build:99-103
- 细节：`plugindir = get_option('plugin_directory')`；空串时 `'@0@/lib/kylin-wlcom/plugins'.format(get_option('prefix'))`；`-DPLUGIN_DIR="..."`

### F-R1-024 — debian 打包固定覆盖两项选项/构建类型
- 证据：debian/rules:10-11
- 细节：`override_dh_auto_configure: dh_auto_configure -- -Dukui_theme=true --buildtype=debugoptimized`（上游默认 ukui_theme=false）

### F-R1-025 — nls 实际可用性由 msgfmt 程序探测决定，独立于 nls feature 选项值
- 证据：meson.build:227-234
- 细节：`msgfmt = find_program('msgfmt', required: get_option('nls'))`；`-DHAVE_NLS=<found:int>`；仅 `msgfmt.found()` 时 `subdir('po')`

### F-R1-026 — 条件子目录门控：libkywc/examples/tools/portal 分别由同名选项控制
- 证据：meson.build:239-253
- 细节：`if have_libkywc: subdir('libkywc')`；examples→subdir('examples')；tools→subdir('tools')；portal→subdir('portal')；固定 subdir 为 data（L230）、protocols（L236）、src（L237）

## 编译期特性探测、子目录与链接

### F-R1-027 — 针对 libinput 头文件做 3 个符号探测并生成 HAVE 宏
- 证据：meson.build:105-117
- 细节：`cc.has_header_symbol('libinput.h','LIBINPUT_EVENT_RAW_TAP')`→HAVE_LIBINPUT_RAW_TAP；`libinput_device_config_zone_gesture_is_available`→HAVE_LIBINPUT_ZONE_GESTURE；`libinput_device_config_gesture_pinch_is_available`→HAVE_LIBINPUT_GESTURE_PINCH_CONFIG

### F-R1-028 — 针对系统头做 2 个存在性探测
- 证据：meson.build:119-123
- 细节：`cc.has_header('sys/eventfd.h')`→HAVE_EVENTFD；`cc.has_header('linux/sync_file.h')`→HAVE_LINUX_SYNC_FILE

### F-R1-029 — 根 meson 固定开启一组 C 警告参数，release 时再压制未用变量警告
- 证据：meson.build:15-37
- 细节：`cc.get_supported_arguments([...])` 含 -Wundef、-Wlogical-op、-Wstrict-prototypes、-Wimplicit-fallthrough=2、-Wstrict-aliasing=2、-Wmissing-prototypes、-Walloca、-Wunused-macros、-Wno-unused-parameter 等 15 项；buildtype==release 时加 -Wno-unused-variable/-Wno-unused-but-set-variable

### F-R1-030 — src/meson.build 聚合 main.c/server.c 并按 13 个固定子目录 + 条件 xwayland 组装
- 证据：src/meson.build:1-25
- 细节：固定 subdir 顺序 util→backend→config→effect→input→output→painter→plugin→render→scene→security→theme→view→widget（L7-21）；xwayland 条件（L23-25）

### F-R1-031 — 主可执行文件启用 export_dynamic 并以版本脚本限制导出符号
- 证据：meson.build:311-325
- 细节：`symbols_file = 'wlcom.syms'`，link_args `-Wl,--version-script,...`、link_depends wlcom.syms；wlcom.syms 内容 5 行：`global: kywc_*; local: *;`（仅导出 kywc_ 前缀符号）

### F-R1-032 — configure_file 产出空的 kywc_config.h（internal_config 仅在子目录中被填充）
- 证据：meson.build:67、306-309；src/xwayland/meson.build:21-32
- 细节：根处 `internal_config = configuration_data()` 后未直接 set 任何键；XWAYLAND_PATH、HAVE_XWAYLAND_*、HAVE_XCB_ERRORS 在 xwayland/meson.build 写入；输出名 kywc_config.h

### F-R1-033 — wlcom_deps 聚合 20+ 依赖供主程序链接
- 证据：meson.build:127-134
- 细节：列表含 wayland_server/wayland_protos/wlroots/xkbcommon/drm/input/udev/dispinfo/pixman/jsonc/sdbus/math/dl/rt/thread/unwind/cairo/pango/pangocairo/rsvg/jpeg/png/pipewire

### F-R1-034 — meson 配置结束时打印两段 summary（Directories 与 Configuration）
- 证据：meson.build:255-304
- 细节：Directories 段输出 prefix、plugin；Configuration 段以 bool_yn 输出 examples/tools/libunwind/xwayland/nls/libkywc 及全部协议开关与 3 个 extra 路径

### F-R1-035 — protocols/meson.build 无条件字典含 32 个协议键，另有约 27 个条件追加键
- 证据：protocols/meson.build:4-41（脚本统计 2 空格缩进键 32 个）、43-178（if 块内 4 空格缩进追加）
- 细节：基础字典 25 个（L4-30）+ kywc/wlr-screencopy 7 个（L32-41）；条件块覆盖 drm-lease/alpha-modifier/kde-*/ukui-*/xwayland-shell 等；have_ukui_background 块再次写入 `linux-dmabuf-v1` 键（L163，与 L24 同名同值，字典键重复）

### F-R1-036 — 每个协议均用 wayland-scanner 生成 private-code 与 server-header 并直接加入 wlcom_sources
- 证据：protocols/meson.build:183-211
- 细节：`wayland_scanner` 经 find_program 获取（L2）；code 命令 `private-code`、server 头 `server-header` 均并入主程序源；client-header `build_by_default: false`（L200-206），仅被 libkywc/tools/examples 引用时构建

## main 启动序列与 CLI

### F-R1-037 — main.c 持有文件级静态 struct server，6 个 options 默认全为 true，session_pid 初值 -1
- 证据：src/main.c:25-36
- 细节：`.options = { .enable_xwayland=true, .log_to_file=true, .log_in_realtime=true, .log_rate_limit=true, .binding_session=true, .lazy_xwayland=true }`，`.session_pid=-1`；另有 `static int exit_value = 0`

### F-R1-038 — 命令行接口：5 个长选项 + 6 个短字符，usage 文本不含 -D
- 证据：src/main.c:38-52、196-227
- 细节：long_options = help(h)/debug(d)/version(v)/session(s,required)/verbose(V)；getopt 短串 `"hdD:s:vV"`（L198）；usage[] 仅列出 h/d/s/v/V 五项（L44-52），未文档化 -D

### F-R1-039 — -D 扩展调试 flag 共 6 个，未知名仅打印 "Unknown debug flag"
- 证据：src/main.c:68-85
- 细节：`static void enable_debug_flag(struct server *server, const char *flag)`；"noxwayland"→enable_xwayland=false；"logtostdout"→log_to_file=false；"loginmtime"→log_in_realtime=false；"lognoratelimit"→log_rate_limit=false；"nosessionbinding"→binding_session=false；"nolazyxwayland"→lazy_xwayland=false
- 函数签名：`static void enable_debug_flag(struct server *server, const char *flag)`（main.c:68）

### F-R1-040 — 日志级别三档：默认 KYWC_WARN，-d 为 KYWC_DEBUG，-V 为 KYWC_INFO
- 证据：src/main.c:234-239
- 细节：`enum kywc_log_level level = KYWC_WARN; if (enable_debug) level=KYWC_DEBUG; else if (enable_verbose) level=KYWC_INFO;`

### F-R1-041 — main 函数级启动顺序（行号链）
- 证据：src/main.c:184-289
- 细节，顺序：setlocale(LC_ALL,"")+setlocale(LC_NUMERIC,"C")（186-187）→HAVE_NLS 时 nls_setup_message(TARGET_NAME, locales, ARRAY_SIZE(locales))（189-191）→getopt_long 循环解析（196-227）→detect_suid()（230-232）→logger_init(level, log_to_file?"kylin-wlcom.log":NULL, log_in_realtime)（240-241）→logger_set_rate_limit(rate_limit?5000:0, 10)（242）→limit_set_nofile()（247）→set_signal 注册 SIGPIPE(IGN)/SIGINT/SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGABRT（250-258）→server_init(&server)（260）→server_start(&server)（265）→set_signal(SIGCHLD, child_handler)（271）→有 session_process 时 wl_event_loop_add_idle(start_session)（273-275）→server_run(&server)（277）→SIGCHLD 恢复默认、SIGTERM/SIGKILL 清理 session 子进程（279-285）→server_finish（288）→logger_finish（289）
- 函数签名：`int main(int argc, char *argv[])`（main.c:184）

### F-R1-042 -h/-v 直接 printf 后 exit(EXIT_SUCCESS)，解析失败打印 usage 到 stderr 并退出失败
- 证据：src/main.c:203-206、216-219、223-226
- 细节：-v 输出 `TARGET_NAME " version " KYWC_VERSION`（L217）

### F-R1-043 — SUID 检测拒绝启动：euid/egid 为 0 且与 uid/gid 不同即打印拒绝信息
- 证据：src/main.c:54-66、229-232
- 细节：`static bool detect_suid(void)`；输出字面值 "SUID operation is no longer supported, refusing to start."；注释 `/* SUID operation is deprecated, so block it for now */`

### F-R1-044 — 崩溃信号处理调用 debug_backtrace()，重置 SIGABRT 默认处置后 abort()
- 证据：src/main.c:109-138
- 细节：`static void sig_handler(int signo, siginfo_t *sip, void *unused)`；SIGSEGV/SIGBUS/SIGILL/SIGFPE/SIGABRT 分支记录 "Caught %s(%u) at address %p"、调 `debug_backtrace()`、`set_signal(SIGABRT, SIG_DFL); abort();`；SIGINT 在 server.terminate 后重复到达直接 return（L111-113）

### F-R1-045 — set_signal 以 sigaction + SA_SIGINFO 安装处理器，非 IGN 时 sa_mask 加入自身信号
- 证据：src/main.c:97-107
- 细节：`static void set_signal(int sig, void *handler)`；sigemptyset；handler!=SIG_IGN 时 sigaddset；act.sa_sigaction=handler；act.sa_flags=SA_SIGINFO

### F-R1-046 — terminate() 在 ready 前直接 exit，ready 后通过 wl_display_terminate 走优雅退出
- 证据：src/main.c:87-95
- 细节：`static void terminate(int exit_code)`；保存 exit_code 到文件级变量；server_run 返回后由 main 读取（L291 `return exit_value`）

### F-R1-047 — SIGCHLD 处理器只关心 session_pid，binding_session=true 时会话退出即终止合成器
- 证据：src/main.c:140-168
- 细节：`static void child_handler(int signo, siginfo_t *sip, void *unused)`；区分 CLD_EXITED/CLD_KILLED/CLD_DUMPED 日志；调用 `spawn_wait(server.session_pid)` 后置 session_pid=-1；binding_session 时记录 `TARGET_NAME " abort..."` 并 terminate(EXIT_SUCCESS)

### F-R1-048 — start_session 作为 wl_event_loop idle 回调，spawn 失败且绑定时终止
- 证据：src/main.c:170-182
- 细节：`static void start_session(void *data)`；`server.session_pid = spawn_session(server.session_process)`；失败日志 "Session %s start failed%s"（binding 时追加 ", abort"）

### F-R1-049 — spawn_session 用 wordexp(WRDE_NOCMD) 解析命令、fork+setsid+execvp，非 DEBUG 时关闭子进程 stdout/stderr
- 证据：src/util/spawn.c:232-278；声明 include/util/spawn.h:15
- 细节：签名 `pid_t spawn_session(const char *session)`；子进程 setsid()、sigfillset 后 SIG_UNBLOCK、`limit_unset_nofile()`、打开 /dev/null，`if (kywc_log_get_level() < KYWC_DEBUG) dup2(devnull, STDOUT/STDERR)`，execvp(argv[0],argv)

### F-R1-050 — limit_set_nofile 将 RLIMIT_NOFILE 当前软限制抬到硬限制
- 证据：src/util/limit.c:14-31
- 细节：`void limit_set_nofile(void)`；getrlimit 保存 original_nofile_rlimit；new_rlimit.rlim_cur=rlim_max；setrlimit；配套 limit_unset_nofile（L33-42）与 limit_set_cloexec（L44-61）

## server 结构与生命周期

### F-R1-051 — struct server 字段分组：核心状态/options/events/sources/会话/wlroots 对象/场景/队列/会话进程/VT/inhibitor
- 证据：include/server.h:13-68
- 细节（代表字段+行号）：`struct wl_display *display`（14）、`struct wl_event_loop *event_loop`（15）、`bool ready, start, terminate, active`（16）；options 子结构 6 bool（18-26）；events 8 个 wl_signal：ready/start/terminate/destroy/suspend/hibernate/resume/active（28-38）；sources.sighup/sigterm（40-44）；`struct session *session`+session_active（46-47）；renderer/pixman_renderer/allocator/backend/linux_dmabuf_v1/compositor（49-54）；`struct scene *scene`、`struct wlr_output_layout *layout`（56-57）；`struct queue *queue`（59）；session_process/session_pid（61-62）；`unsigned vtnr`（64）；`int inhibitor; bool need_inhibit`（66-67）

### F-R1-052 — server 公开 API 共 6 个函数
- 证据：include/server.h:70-83
- 细节：`bool server_init(struct server *server)`、`bool server_start(struct server *server)`、`void server_run(struct server *server)`、`void server_finish(struct server *server)`、`void server_add_destroy_listener(struct server *, struct wl_listener *)`、`struct wlr_renderer *server_get_pixman_renderer(struct server *)`

### F-R1-053 — server_init 函数级调用顺序
- 证据：src/server.c:303-352
- 细节：wl_display_create（305）→wl_display_get_event_loop（306）→wl_display_set_default_max_buffer_size(display, 1024*1024)（307）→8 个 wl_signal_init（309-316）→wl_event_loop_add_signal SIGHUP/SIGTERM→handle_exit（319-322）→session_active 监听器初始化（324-325）→dbus_context_create(server)（327）→server_init_power(server)（328）→queue_create(64, 4, server)（330）→config_manager_create（332）→security_manager_create（333）→theme_manager_create（334）→wlroots_server_init（336）→output_manager_create（340）→input_manager_create（341）→view_manager_create（342）→xwayland_manager_create（343）→effect_manager_create（345）→plugin_manager_create（346）→ready=true 并发 ready 信号（348-349）
- 函数签名：`bool server_init(struct server *server)`（server.c:303）

### F-R1-054 — wlroots_server_init 内部顺序与 wlroots API 版本细节
- 证据：src/server.c:236-289
- 细节：wlr_log_init(WLR_DEBUG, kywc_log_callback)（239）→backend_autocreate(display, &session)（241）→session active 监听器+server_get_active_vt，嵌套后端 active=true（247-254）→renderer_autocreate(backend, server)（256）→allocator_create（262）→`wlr_compositor_create(display, 6, renderer)`（269，version 参数 6）→wlr_subcompositor_create（270）→renderer_init_wl_display（272-273）→wlr_output_layout_create（275）→scene_create（276）→tearing_control_manager_v1_create（281）→presentation_create（282）→wlr_viewporter_create（284）→wlr_fractional_scale_manager_v1_create(display, 1)（285）→alpha_modifier_v1_create（286）

### F-R1-055 — server_start 添加 wayland socket 并自行 setenv WAYLAND_DISPLAY，再启动 backend
- 证据：src/server.c:354-378
- 细节：`wl_display_add_socket_auto`（357）；`setenv("WAYLAND_DISPLAY", socket, 1)`（363），失败仅 KYWC_ERROR 日志；`wlr_backend_start`（369）；成功后置 start=true 发 start 信号（374-375）

### F-R1-056 — server_run 仅记录一行日志后进入 wl_display_run
- 证据：src/server.c:380-385
- 细节：日志 "Running wayland compositor on wayland display '%s'"，参数 `getenv("WAYLAND_DISPLAY")`

### F-R1-057 — server_finish 逆序销毁并断言 8 个信号监听器链表为空
- 证据：src/server.c:387-432
- 细节：terminate=true（389）→wlr_log_init 换空回调 kywc_log_callback_dumb（391）→移除 session_active/sighup/sigterm（393-396）→发 terminate（398）→queue_destroy（400）→wl_display_destroy_clients（402）→xwayland_manager_destroy（404）→wl_display_destroy（406）→发 destroy（409）→8 个 assert(wl_list_empty(...))（411-418）→scene_node_destroy/layout/allocator/renderer 销毁（421-427）→`pango_cairo_font_map_set_default(NULL)`（429）

### F-R1-058 — destroy 监听器用头插法实现"后进先出"
- 证据：src/server.c:171-175；include/server.h:78-81
- 细节：`void server_add_destroy_listener(...)` 内 `wl_list_insert(&signal->listener_list, &listener->link)`；头文件注释 "first-in last-out signal for server finish"

### F-R1-059 — server 内部电源管理对接 org.freedesktop.login1，含 sleep inhibitor 句柄管理
- 证据：src/server.c:43-77
- 细节：常量 service "org.freedesktop.login1"、path "/org/freedesktop/login1"、interface "org.freedesktop.login1.Manager"（43-45）；`server_create_inhibitor` 调 dbus Call "Inhibit"，参数 "ssss"："sleep"、TARGET_NAME、"Power off outputs when hibernate"、"delay"（74-76）；取到的 fd 经 fcntl F_DUPFD_CLOEXEC 复制到最小 fd 3（64）

### F-R1-060 — 通过 Introspect XML 中是否含 PrepareForSuspend/PrepareForHibernate 字符串决定 need_inhibit
- 证据：src/server.c:135-169
- 细节：`server_init_power` 先 inhibitor=-1，dbus_context_get_bus(true)（系统总线）；Introspect 后 `strstr(xml,"PrepareForSuspend") || strstr(xml,"PrepareForHibernate")`（152-154）；无条件 match PrepareForSleep（158）；need_inhibit 时创建 inhibitor 并再 match PrepareForSuspend/PrepareForHibernate（161-168）

### F-R1-061 — 三个 D-Bus 信号处理器分别发 suspend/hibernate/resume wl_signal 并管理 inhibitor fd
- 证据：src/server.c:79-133
- 细节：handle_prepare_for_sleep（签名 `static int ...(sd_bus_message*, void*, sd_bus_error*)`，L79）going_down=false 时 server_create_inhibitor + emit resume；handle_prepare_for_suspend（L98）下行时 emit suspend 并 drop_inhibitor；handle_prepare_for_hibernate（L116）下行时 emit hibernate 并 drop；注释 `/* "b" apparently reads into an int, not a bool */`

### F-R1-062 — VT 号从 /sys/class/tty/tty0/active 解析，失败置 0
- 证据：src/server.c:215-225
- 细节：`static void server_get_active_vt(struct server *server)`；sysfs_read_data 读 64 字节缓冲，`sscanf(buf, "tty%u", &server->vtnr)`

### F-R1-063 — handle_exit 是 wl_event_loop 信号源回调（SIGHUP/SIGTERM），与 main.c 的 sigaction 两套并存
- 证据：src/server.c:291-301、319-322
- 细节：签名 `static int handle_exit(int signal, void *data)`；ready 前 exit(EXIT_SUCCESS)，否则 wl_display_terminate；日志 "Received signal %s(%u), exit..."

### F-R1-064 — wlroots 日志经 kywc_log_callback 做枚举映射，结束时换空回调静默
- 证据：src/server.c:189-213
- 细节：WLR_SILENT/ERROR/INFO/DEBUG → KYWC_SILENT/ERROR/INFO/DEBUG，默认 KYWC_WARN；`kywc_log_callback_dumb` 为空函数体（L212-213）

### F-R1-065 — server_get_pixman_renderer 在主渲染器非 pixman 时惰性创建独立 pixman 渲染器
- 证据：src/server.c:177-187
- 细节：wlr_renderer_is_pixman_renderer 判断；缓存于 server->pixman_renderer，创建函数 pixman_renderer_create()

## 配置子系统（src/config/）

### F-R1-066 — struct config 与 config_manager 分别定义在公共头和私有头
- 证据：include/config.h:13-21；src/config/config_p.h:10-20
- 细节：`struct config { struct wl_list link; json_object *json; json_object *sys_json; struct { struct wl_signal destroy; } events; }`；config_manager 含 server/wl_list configs/file/user json/sys_json/server_ready/server_destroy

### F-R1-067 — 用户配置文件路径为 ~/.config/kylin-wlcom/config.json，目录不存在时 mkdir(0770)
- 证据：src/config/config.c:18-40
- 细节：`static const char *check_config_file(void)`；string_expand_path("~/.config/" TARGET_NAME "")；`mkdir(config_dir, S_IRWXU | S_IRWXG)`；文件名 "config.json"

### F-R1-068 — 系统默认配置固定从 /etc/kylin-wlcom/config.json 读取，缺失仅 WARN
- 证据：src/config/config.c:93-98
- 细节：`json_object_from_file("/etc/" TARGET_NAME "/config.json")`；日志 "Get the sys default config from the etc directory"、"The default config does not exist"

### F-R1-069 — 用户 json 读取失败时新建空 object；配置在 server destroy 时回盘
- 证据：src/config/config.c:100-103、42-50、52-69
- 细节：`config_manager_sync()` 用 `json_object_to_file_ext(..., JSON_C_TO_STRING_SPACED | JSON_C_TO_STRING_PRETTY)`；handle_server_destroy 先销毁所有 config、sync、json_object_put 用户与系统 json、free file

### F-R1-070 — config_manager_create 挂接 server ready/destroy 两个监听并立即执行 common_init
- 证据：src/config/config.c:81-116
- 细节：签名 `struct config_manager *config_manager_create(struct server *server)`（L81，文件级单例 static config_manager，L16）；ready 监听器 wl_signal_add（L109）；destroy 走 server_add_destroy_listener（L111）；末尾 config_manager_common_init（L113）

### F-R1-071 — server ready 时创建 6 个输入/配置管理器
- 证据：src/config/config.c:71-79
- 细节：handle_server_ready 依次 `input_action_manager_create`、`kde_global_accel_manager_create`、`kde_input_manager_create`、`ukui_gsettings_create`、`ukui_shortcut_manager_create`、`ukui_view_mode_manager_create`（后 5 个在 config_p.h 中有 HAVE_* 关闭时的 inline 空实现，config_p.h:24-72）

### F-R1-072 — config_manager_add_config 按 name 取用户/系统 json 子对象，用户侧缺失即新建并挂回
- 证据：src/config/config.c:118-141
- 细节：签名 `struct config *config_manager_add_config(const char *name)`；name 非 NULL 时 json_object_object_get 用户 json，缺失则 json_object_new_object + object_add；sys_json 侧只 get 不建；新 config 插入 configs 链表

### F-R1-073 — 全仓调用 add_config 的配置段名共 12 个（大小写不统一）
- 证据：src/input/config.c:1267("Inputs")、1274("Seats")；src/input/action.c:766("InputAction")；src/input/global_gestures.c:614("Gestures")；src/input/global_shortcuts.c:1511("Shortcuts")；src/output/config.c:561("layouts")、574("outputs")；src/effect/config.c:166("Effects")；src/plugin/config.c:254("plugins")；src/theme/config.c:97("theme")；src/view/config.c:358("Views")；src/xwayland/config.c:47("Xwayland")
- 细节：脚本 grep `config_manager_add_config\(` 全 src 得 13 行（1 行为定义）

### F-R1-074 — 出厂 data/config.json 仅含 7 个顶层键
- 证据：data/config.json:1-12
- 细节：`theme`（`{"type": 0, "icon_theme_name": "ukui-icon-theme-default"}`）、`outputs`、`layouts`、`Inputs`、`Seats`、`InputAction`、`plugins`，后 6 个为空对象；Gestures/Shortcuts/Effects/Views/Xwayland 段不在出厂文件中

### F-R1-075 — common.c 在 com.kylin.Wlcom 的 /com/kylin/Wlcom 注册 5 个无特权 D-Bus 方法
- 证据：src/config/common.c:13-14、91-99、109-120
- 细节：service_path="/com/kylin/Wlcom"、service_interface="com.kylin.Wlcom"；vtable 方法 SetLogLevel("u")、SetLogRateLimit("uu")、PrintConfig(→"s")、TrimMemory("b")、LogScene("u")，全部 SD_BUS_VTABLE_UNPRIVILEGED；注册时 bus 参数传 NULL（dbus_register_object 第一参）

### F-R1-076 — SetLogLevel 校验范围并返回固定错误文案
- 证据：src/config/common.c:21-34
- 细节：`if (level < KYWC_LOG_LEVEL_LAST) logger_set_level(level)`；否则 SD_BUS_ERROR_INVALID_ARGS，消息字面值 "Invalid args, please input [0-5]."

### F-R1-077 — TrimMemory 通过 5 秒周期定时器调用 malloc_trim(4096)
- 证据：src/config/common.c:52-78
- 细节：handle_timeout 内 `wl_event_source_timer_update(config.timer, 5000); malloc_trim(4096);`；开关切换时创建/移除 timer；`#include <malloc.h>`（L5）

### F-R1-078 — LogScene 调用 scene_node_log 打印场景树
- 证据：src/config/common.c:80-89
- 细节：`scene_node_log(&cm->server->scene->tree.node, depth)`，depth 由 u 参数给出

### F-R1-079 — kde_global_accel 实现 org.kde.kglobalaccel 两套 vtable，注释标注仅支持 kglobalaccel >= 5.90
- 证据：src/config/kde_global_accel.c:247-251、678-693、1159-1187、1240-1264
- 细节：bus "org.kde.kglobalaccel"、path "/kglobalaccel"、interface "org.kde.KGlobalAccel"、组件 interface "org.kde.kglobalaccel.Component"、path 前缀 "/component"；manager_create 签名 `bool kde_global_accel_manager_create(struct config_manager *config_manager)`（L1240）

### F-R1-080 — KGlobalAccel 注册表 vtable 含 1 个信号与 16 个方法
- 证据：src/config/kde_global_accel.c:1160-1187
- 细节：信号 yourShortcutsChanged("asa(ai)")；方法 actionList/activateGlobalShortcutContext/allActionsForComponent/allComponents/allMainComponents/blockGlobalShortcuts/defaultShortcutKeys/doRegister/getComponent/globalShortcutAvailable/globalShortcutsByKey/setForeignShortcutKeys/setInactive/setShortcutKeys/shortcutKeys/unregister，签名串如 setShortcutKeys "asa(ai)u"→"a(ai)"、globalShortcutsByKey "(ai)i"→"a(ssssssaiai)"

### F-R1-081 — Component vtable 含 3 个信号、2 个 CONST 属性、7 个方法
- 证据：src/config/kde_global_accel.c:678-693
- 细节：信号 globalShortcutPressed/globalShortcutRepeated/globalShortcutReleased，载荷 "ssx"（L680-682，发射点 L450-469）；属性 friendlyName、uniqueName（CONST）；方法 allShortcutInfos/cleanUp/getShortcutContexts/invokeShortcut/isActive/shortcutNames；错误名 "org.kde.kglobalaccel.NoSuchComponent"（L952）

### F-R1-082 — global_shortcut 等 4 个核心结构体与 Qt 修饰位枚举
- 证据：src/config/kde_global_accel.c:26-42、190-243
- 细节：enum Key 含 NoModifier=0、ShiftModifier=0x02000000、ControlModifier=0x04000000、AltModifier=0x08000000、MetaModifier=0x10000000、KeypadModifier=0x20000000、GroupSwitchModifier=0x40000000、KeyboardModifierMask=0xfe000000、KeyMask=~mask；struct global_shortcut_registry（components+2 listener）、global_shortcut_component（dbus_path/unique_name/friendly_name/contexts/current）、global_shortcut_context、global_shortcut（binding/key/default_key/is_present/is_registered/is_fresh/is_grab）

### F-R1-083 — actionId 字段索引与 SetShortcutFlag 枚举值
- 证据：src/config/kde_global_accel.c:176-188
- 细节：enum actionIdFields { ComponentUnique=0, ActionUnique=1, ComponentFriendly=2, ActionFriendly=3 }；enum SetShortcutFlag { SetPresent=2, NoAutoloading=4, IsDefault=8, IsGrab=16 }

### F-R1-084 — 内置组件名为 TARGET_NAME，合成器内建 key_binding 会被注册进 kglobalaccel
- 证据：src/config/kde_global_accel.c:1205-1238、1256-1258
- 细节：`static const char *component_builtin = TARGET_NAME`；kglobalaccel_builtin_shortcut 跳过 FUNC_ID_CUSTOM；创建时 `kywc_key_binding_add_registered_listener` 并 `kywc_key_binding_for_each` 全量遍历；qtkey 计算 `modifiers_to_qtkey(info->modifiers) | keysym_to_qtkey(info->keysym)`（L1228）

### F-R1-085 — QtKey↔xkb keysym 双向转换：快速路径 + 对生成表 bsearch
- 证据：src/config/kde_global_accel.c:51-169
- 细节：签名 `static uint32_t qtkey_to_keysym(int32_t key)`（L77）、`static uint32_t keysym_to_qtkey(int32_t keysym)`（L140）、qtkey_to_modifiers/modifiers_to_qtkey（L51、L114）；ASCII<0x1000 用 tolower/toupper；F1-F35/R15 区间线性映射；其余 bsearch qtkey_map_table/keysym_map_table；失败 KYWC_WARN "Cannot covert qtkey..."（源码拼写 "covert"）

### F-R1-086 — qtkey_mapper.c 是构建期代码生成器，KeyTbl 有效 273 条，输出两张排序表
- 证据：src/config/qtkey_mapper.c:541-864、866-897、892-894；src/config/meson.build:7-15
- 细节：脚本统计 `{ XKB_KEY_` 开头 273 条、注释行 29 条；main 签名 `int main(int argc, char *argv[])`（L894）；stdout 生成头注 "/* Generated by qtkey-mapper */"、结构 `static const struct qtkey_map { unsigned int qtkey; unsigned int keysym; }`，表名 qtkey_map_table（跳过 OnlyXkb2Qt 条目）与 keysym_map_table（全量），COLS=3；meson 以 `executable('qtkey-mapper','qtkey_mapper.c')` + custom_target(capture:true) 生成 qtkey_map_table.h

### F-R1-087 — qtkey_mapper 内嵌完整 Qt::Key 枚举表（misc/cursor/modifier/function/extra/ASCII 等）
- 证据：src/config/qtkey_mapper.c:11-540
- 细节：如 Key_Escape=0x01000000、Key_Tab=0x01000001、Key_F1=0x01000030…Key_F35=0x01000052、Key_Super_L/R、Key_Space=0x20；含 XF86 多媒体键（XKB_KEY_XF86AudioMicMute、XF86Launch0-F 等，L800-863）

### F-R1-088 — kde_input 在总线上暴露 KWin InputDeviceManager 与每设备 InputDevice 对象
- 证据：src/config/kde_input.c:17-20、61-65、727-745
- 细节：常量 service_path "/org/kde/KWin/InputDevice"、kde_input_path 前缀 "/org/kde/KWin/InputDevice/"、interface "org.kde.KWin.InputDeviceManager"、设备 interface "org.kde.KWin.InputDevice"；create 签名 `bool kde_input_manager_create(struct config_manager *)`（L727），注册 bus 名 "org.kde.KWin"（L734）

### F-R1-089 — Manager vtable 仅 1 个属性 devicesSysNames("as")，设备增删发 deviceAdded/deviceRemoved("s") 信号
- 证据：src/config/kde_input.c:46-65、653、710
- 细节：current_state 回调遍历 manager->inputs 追加 sys_name；kde_input_destroy 发 deviceRemoved；handle_new_kde_input 路径发 deviceAdded（L710）

### F-R1-090 — 每设备 vtable 含 37 个属性，其中 9 个可写（KDE_WPROP）
- 证据：src/config/kde_input.c:596-647（脚本 grep KDE_PROP/KDE_WPROP 表项）
- 细节：只读代表：pointer/keyboard/touchpad/touch/tabletTool/tabletPad/switchDevice（"b"）、name/sysName（"s"）、product/vendor（"i"）、supports*/default* 系列、tapFingerCount（L596-644）；可写 9 个：enabled、pointerAcceleration、leftHanded、pointerAccelerationProfileAdaptive、naturalScroll、tapToClick、scrollTwoFinger、scrollEdge、disableWhileTyping、outputName（outputName 为 "s"，L646）；宏 KDE_PROP/KDE_WPROP 统一带 EMITS_CHANGE（L22-26）

### F-R1-091 — 设备类型判定基于 input->prop.type 枚举，touchpad 额外要求 tap_finger_count 非零
- 证据：src/config/kde_input.c:67-128
- 细节：is_pointer 比较 WLR_INPUT_DEVICE_POINTER（L76）；is_touchpad 为 POINTER 且 `input->prop.tap_finger_count`（L92-93）；另有 keyboard/touch/tablet_tool/tablet_pad/switch 判定

### F-R1-092 — sys_name 去重：同名设备追加 `_<递增 index>` 后缀
- 证据：src/config/kde_input.c:667-679
- 细节：`static void kde_input_set_name(struct kde_input *, const char *name)`；static int index；`kywc_identifier_generate("%s_%d", name, ++index)`

### F-R1-093 — ukui_gsettings 监听三类 GSettings schema：鼠标、风格、背景
- 证据：src/config/ukui_gsettings.c:18-44、49-75
- 细节：struct ukui_settings 分 cursor/style/background 三组 + destroy listener；schema  id："org.ukui.peripherals-mouse"、"org.ukui.style"、"org.mate.background"（L56、62、72）；GPath：/org/ukui/desktop/peripherals/mouse/（长 36）、/org/ukui/style/（16）、/org/mate/desktop/background/（29）（L49-54）

### F-R1-094 — ukui_gsettings 键名清单（鼠标 4、风格 9、背景 3）
- 证据：src/config/ukui_gsettings.c:57-75
- 细节：鼠标 cursor-theme/cursor-size/locate-pointer/shake-cursor；风格 style-name/icon-theme-name/widget-theme-name/system-font/system-font-size/theme-color/window-radius/menu-transparency；背景 picture-filename/picture-options/primary-color

### F-R1-095 — 主题色支持两种格式："r,g,b,a" 字符串与 7 个旧版命名色
- 证据：src/config/ukui_gsettings.c:77-84、177-196
- 细节：ukui_accent_colors 表 daybreakBlue=0x3790FA、jamPurple=0x722ED1、magenta=0xEB3096、sunRed=0xF3222D、sunsetOrange=0xF68C27、dustGold=0xF9C53D、polarGreen=0x52C429；sscanf "%hhu,%hhu,%hhu,%f" 成功 4 项即 color_to_uint24，否则查表

### F-R1-096 — 背景 picture-options 支持 6 个字符串，未匹配回退 STRETCHED
- 证据：src/config/ukui_gsettings.c:86-93、248-257
- 细节：scaled/wallpaper/centered/stretched/zoom/spanned 映射 enum background_option；`options_strings_to_option` 默认 BACKGROUND_OPTION_STRETCHED

### F-R1-097 — 运行时变更走 ca.desrt.dconf.Writer Notify 信号按路径前缀分发
- 证据：src/config/ukui_gsettings.c:293-324、429
- 细节：dconf_notify 读 prefix('s')+array 'as'，拼 `"%s%s"` 得 key，strncmp 三个 path 常量长度分发；create 中 `dbus_match_signal(NULL, "/ca/desrt/dconf/Writer/user", "ca.desrt.dconf.Writer", "Notify", ...)`

### F-R1-098 — 初始化时遍历 schema 全部键主动回调一次；schema 不存在返回 NULL
- 证据：src/config/ukui_gsettings.c:97-101、326-350、405-436
- 细节：is_schema_installed 用 g_settings_schema_source_get_default + lookup(...,TRUE)；init_schema_settings 签名含 handler 函数指针，g_settings_schema_list_keys 后逐键回调；create 签名 `bool ukui_gsettings_create(struct config_manager *)`（L405），cursor 与 style 均失败时整体返回 false（L416-420）

### F-R1-099 — 壁纸优先尝试 Accounts D-Bus 的 BackgroundFile 属性（标注 Bug #572421 workaround）
- 证据：src/config/ukui_gsettings.c:375-403、422-423
- 细节：ukui_try_dbus_background 调系统总线 "org.freedesktop.Accounts" FindUserById("x", getuid())，再取 org.freedesktop.Accounts.User 的 BackgroundFile；命中置 use_dbus_background=true；注释原文 `/* workaround: Bug: #572421, try dbus background first */`

### F-R1-100 — locate-pointer/shake-cursor 两个 gsettings 键直接开关同名 effect
- 证据：src/config/ukui_gsettings.c:103-120
- 细节：`effect_by_name("locate_pointer")`/`effect_by_name("shake_cursor")` + effect_set_enabled

### F-R1-101 — window-radius 键按 schema 实际类型分字符串 "win,menu" 与 int 两种读法
- 证据：src/config/ukui_gsettings.c:198-214、233-242
- 细节：window_radius_is_string 时 sscanf "%d,%d"；theme_manager_set_corner_radius(window_radius, menu_radius)；类型探测用 g_settings_schema_key_get_value_type 与 G_VARIANT_TYPE_STRING 比较

### F-R1-102 — ukui_shortcut 对接 org.ukui.settingsDaemon.shortcut，维护每服务黑白名单
- 证据：src/config/ukui_shortcut.c:15-31、191-210
- 细节：service_path "/org/ukui/settingsDaemon/shortcut"、interface "org.ukui.settingsDaemon.shortcut"；struct shortcut_service { name; uint32_t black_mask; uint32_t white_mask; bool block_all; wl_list link }；create 签名 `bool ukui_shortcut_manager_create(struct config_manager *)`（L191）

### F-R1-103 — 通过监听 NameOwnerChanged 感知 org.ukui.settingsDaemon* 服务上下线
- 证据：src/config/ukui_shortcut.c:160-177、193-194
- 细节：match 串 "type=signal,interface=org.freedesktop.DBus,member=NameOwnerChanged"；strncmp(name,"org.ukui.settingsDaemon",23)；old_owner 空串→create，new_owner 空串→destroy

### F-R1-104 — 服务创建时同步调用 blockShortcuts/unblockShortcuts 两个 D-Bus 方法
- 证据：src/config/ukui_shortcut.c:139-158
- 细节：dbus_call_method(name, path, interface, "blockShortcuts"/"unblockShortcuts", handler, service)；日志中拼写 "bolckShortcuts"（L148）

### F-R1-105 — block 数组经 kywc_key_binding_type_by_name 映射类型；特殊类型 KEY_BINDING_TYPE_NUM 表示全拦
- 证据：src/config/ukui_shortcut.c:35-65、67-100
- 细节：block handler 遇 KEY_BINDING_TYPE_NUM → kywc_key_binding_block_all(true) 并 break；其余 kywc_key_binding_block_type(type,true) 并记 black_mask；unblock 遍历 KEY_BINDING_TYPE_CUSTOM_DEF…NUM，白名单缺失的类型全部 block

### F-R1-106 — 服务销毁时恢复被 block 的类型与 all 状态
- 证据：src/config/ukui_shortcut.c:102-126
- 细节：shortcut_service_destroy 逐类型 kywc_key_binding_block_type(i,false)，block_all 时 kywc_key_binding_block_all(false)，wl_list_remove 后 free name/service

### F-R1-107 — ukui_view_mode 监听平板模式切换，bool 映射为 "tablet_mode"/"stack_mode"
- 证据：src/config/ukui_view_mode.c:11-42
- 细节：bus/interface 均 "com.kylin.statusmanager.interface"，path "/"；信号 "mode_change_signal"，初始主动调方法 "get_current_tabletmode"；handle_mode_change_signal 读 "b"，`view_manager_set_view_mode(tablet_mode ? "tablet_mode" : "stack_mode")`；create 签名 `bool ukui_view_mode_manager_create(struct config_manager *)`（L25）

## 日志

### F-R1-108 — logger 默认级别 KYWC_WARN，单文件上限 1 MiB，超限按时间戳轮转重命名
- 证据：src/util/logger.c:19-26、179-212
- 细节：`#define MAX_FILE_SIZE (1024*1024)`；rotate_file_if_needed 用 fstatat(AT_SYMLINK_NOFOLLOW)，新名 `"%s.%s"` strftime "%Y%m%d_%H%M%S"，renameat 同目录

### F-R1-109 — 默认日志文件路径 $HOME/.log/kylin-wlcom.log，目录不存在时 mkdir(0770)，fopen 模式 "ae"
- 证据：src/util/logger.c:214-263；src/main.c:240-241
- 细节：`void logger_init(enum kywc_log_level level, const char *file, bool realtime)`；file 无效字符串时 log_fp=stdout（L221-224）；string_expand_path("~/.log")（L226）；open(log_dir, O_RDONLY|O_DIRECTORY|O_CLOEXEC)；`fopen(log_path, "ae")` 注释 "appending mode with O_CLOEXEC"（L257）

### F-R1-110 — 日志时间戳两种模式：真实本地时间 vs CLOCK_MONOTONIC；输出到 stdout 时带 ANSI 颜色
- 证据：src/util/logger.c:34-42、98-113
- 细节：log_in_realtime 时 `[%Y-%m-%d %H:%M:%S]`，否则 `[%H:%M:%S.%f]` 单调时钟；level_colors 六档（FATAL 反白红、ERROR 亮红、WARN 亮紫、INFO 亮蓝、DEBUG 亮灰）；文件输出用 level_headers 文本标签 [FATAL]/[ERROR]/[WARN]/[INFO]/[DEBUG]

### F-R1-111 — 速率限制默认 interval=5000ms、burst=10，TLS 每线程独立，抑制数定期汇报
- 证据：src/util/logger.c:25-32、44-79、280-284；src/main.c:242
- 细节：`static __thread struct { uint32_t start; uint32_t printed; uint32_t missed; } ratelimit_state`；burst=0 全禁、interval=0 不限；logger_set_rate_limit 夹取 MIN(interval,10000)、MIN(burst,1000)；抑制输出 "[Log Ratelimited] : %d messages suppressed in %d ms"

### F-R1-112 — KYWC_LOG_LEVEL 环境变量接受 6 个大写级别字面值，非法值回退原级别并打 stderr
- 证据：src/util/logger.c:153-177
- 细节：detect_log_level 内 strcmp DEBUG/INFO/WARN/ERROR/FATAL/SILENT；错误提示 "logger: env error, support (DEBUG|INFO|WARN|ERROR|FATAL|SILENT)"

### F-R1-113 — D-Bus 可在运行时改级别/限速，logger_finish 刷新并关闭文件
- 证据：src/util/logger.c:265-295；src/config/common.c:21-43
- 细节：logger_set_level 切换时发一条 KYWC_SILENT 日志；logger_finish fflush+fclose+置 NULL

## 环境变量（docs/ENV.md 与源码 getenv 双源对账）

### F-R1-114 — 合成器源码共 24 个去重环境变量名、27 个 getenv 调用点（脚本全仓 grep）
- 证据：脚本：全仓 grep `getenv\(`（*.c/*.cpp/*.h），命中 17 个文件 27 行
- 细节（KYWC_* 17 个，变量名:文件:行）：KYWC_FB_DEVICES(backend/backend.c:68)、KYWC_DRM_DEVICES(backend/backend.c:291、421)、KYWC_BACKEND(backend/backend.c:453)、KYWC_DRM_NO_ATOMIC(backend/drm/drm.c:79)、KYWC_DRM_NO_MODIFIERS(backend/drm/drm.c:105)、KYWC_SOFTWARE_COLOR(backend/drm/output.c:441)、KYWC_EGL_NO_MODIFIERS(render/opengl/egl.c:200)、KYWC_RENDERER_ALLOW_SOFTWARE(egl.c:392)、KYWC_RENDERER(egl.c:594、render/renderer.c:30)、KYWC_LOG_LEVEL(util/logger.c:157)、KYWC_FORCE_QUIRKS(util/quirks.c:46)、XCURSOR_THEME/XCURSOR_SIZE(input/cursor.c:913-914，属标准 X 变量非 KYWC 前缀)、KYWC_OUTPUT_FILL_WALLPAPER(output/configure.c:254)、KYWC_USE_LAYOUT_MANAGER(output/output.c:1028)、KYWC_ENABLE_TIMELINE(render/renderer.c:82)、KYWC_XWAYLAND(xwayland/server.c:133、479)、KYWC_EIS_SOCKET(backend/eis/backend.c:93)、KYWC_DISABLE_DIRECT_SCANOUT(scene/output.c:141)；标准变量另有 WAYLAND_DISPLAY(backend.c:430、src/server.c:383)、WAYLAND_SOCKET(backend.c:430)、DISPLAY(backend.c:430)、XDG_RUNTIME_DIR(util/nls.c:84)、XDG_SESSION_ID(backend/session/logind.c:506)

### F-R1-115 — docs/ENV.md 共 21 个条目：15 个 KYWC_*、2 个 XCURSOR、4 个应用侧变量
- 证据：docs/ENV.md:1-44（脚本：粗体条目 21，KYWC_* 15）
- 细节：日志 1（KYWC_LOG_LEVEL）；显示 7（KYWC_BACKEND/KYWC_FB_DEVICES/KYWC_DRM_DEVICES/KYWC_DRM_NO_ATOMIC/KYWC_DRM_NO_MODIFIERS/KYWC_SOFTWARE_COLOR/KYWC_OUTPUT_FILL_WALLPAPER）；渲染 4（KYWC_RENDERER 取值 gl/gles2/pixman/vulkan、KYWC_EGL_NO_MODIFIERS、KYWC_RENDERER_ALLOW_SOFTWARE、KYWC_ENABLE_TIMELINE）；输出 2（KYWC_DISABLE_DIRECT_SCANOUT、KYWC_USE_LAYOUT_MANAGER）；应用 4（DRI_PRIME、__VK_LAYER_NV_optimus、__NV_PRIME_RENDER_OFFLOAD、__GLX_VENDOR_LIBRARY_NAME）；其他 3（XCURSOR_THEME、XCURSOR_SIZE、KYWC_FORCE_QUIRKS）

### F-R1-116 — ENV.md 与源码对账：15 个 KYWC 文档条目均能在源码找到 getenv；文档另列 4 个应用侧变量合成器源码不读取
- 证据：docs/ENV.md:31-43 vs 全仓 getenv grep
- 细节：DRI_PRIME/__VK_LAYER_NV_optimus/__NV_PRIME_RENDER_OFFLOAD/__GLX_VENDOR_LIBRARY_NAME 在 src/、libkywc/、portal/、tools/、examples/ 的 C/C++ 中无 getenv 命中（ENV.md:33 原文注明"这部分环境变量供应用程序使用，例如vkcube，glmark2，glxgears，glxinfo等"）

### F-R1-117 — 源码存在但 ENV.md 未列的合成器变量：KYWC_XWAYLAND、KYWC_EIS_SOCKET（另有 5 个标准变量未列）
- 证据：src/xwayland/server.c:133、479；src/backend/eis/backend.c:93；docs/ENV.md 全文
- 细节：KYWC_XWAYLAND 作为 Xwayland 可执行路径读取（L133 `const char *xwayland_path = getenv("KYWC_XWAYLAND")`，L479 未设置且 XWAYLAND_PATH 不可执行时有分支）；KYWC_EIS_SOCKET 为 EIS 后端 socket 名（backend/eis/backend.c:93）；未列标准变量：WAYLAND_DISPLAY、WAYLAND_SOCKET、DISPLAY、XDG_RUNTIME_DIR、XDG_SESSION_ID
- 备注："应否补文档"属推断，仅记录差异

### F-R1-118 — ENV.md 对开关类变量统一以"默认关闭，置1生效"措辞（源码判定细节留 R2/R3）
- 证据：docs/ENV.md:14-17、24、28-29、44
- 细节：原文例子 KYWC_DRM_NO_ATOMIC "设置DRM后端禁用原子提交，默认关闭"；KYWC_ENABLE_TIMELINE "开启drm_syncobj_v1协议，默认关闭，置1生效"；KYWC_FORCE_QUIRKS "输入要求十进制，如2，表示强制软件鼠标"（ENV.md:44）

### F-R1-119 — KYWC_BACKEND 源码仅识别精确值 "fbdev"，DRM 失败自动回退 fbdev
- 证据：src/backend/backend.c:453-467
- 细节：`const char *env = getenv("KYWC_BACKEND"); bool use_fbdev_backend = env && strcmp(env,"fbdev")==0;`；非 fbdev 时 attempt_drm_backend 失败日志 "Failed to open any drm device, fallback to fbdev"；与 ENV.md:11 "可选值为：fbdev" 一致

### F-R1-120 — XDG_RUNTIME_DIR 被 NLS 子系统用于写入内嵌 mo 数据并 bindtextdomain
- 证据：src/util/nls.c:78-106
- 细节：nls_setup_message(domain, locales, size) 要求 runtime_dir 非空且首字符为 '/'；目标文件路径 `"%s/%s"`（$XDG_RUNTIME_DIR/<domain>）；bindtextdomain(domain, dir)、bind_textdomain_codeset(domain,"UTF-8")、textdomain(domain)

### F-R1-121 — wrapper.c 按名清理环境：DISPLAY/XAUTHORITY/WAYLAND_DISPLAY/WAYLAND_SOCKET 与全部 XDG_ 前缀
- 证据：data/wrapper.c:13-25
- 细节：env_needs_drop 切开 '='，仅当当前进程 getenv(env)==NULL 且名字命中四个精确名或 strncmp(env,"XDG_",4)==0 才保留到待删除列表，再经 systemd User Manager UnsetEnvironment 下发（L74-92）

## data/ 资产（udev / systemd / desktop / wrapper / embed / man）

### F-R1-122 — data/meson.build 安装 6 类资产到 5 个绝对路径
- 证据：data/meson.build:1-55
- 细节：udev 规则 → /usr/lib/udev/rules.d（L1-4）；desktop → /usr/share/wayland-sessions（L6-9）；service+target → /usr/lib/systemd/user（L11-14）；config.json → /etc/kylin-wlcom/（L16-19）；构建 embed 与 kylin-wlcom-wrapper 两个可执行文件（L21-29，wrapper 链接 sdbus，install true）；scdoc 存在时生成 2 个 man1（L31-54）

### F-R1-123 — kylin-wlcom.desktop 会话项 Exec 指向 wrapper 而非合成器本体
- 证据：data/kylin-wlcom.desktop:1-5
- 细节：`[Desktop Entry] Name=Kylin Wlcom / Comment=The Kylin Wayland Compositor / Exec=kylin-wlcom-wrapper / Type=Application`（无 Name[zh] 等本地化键）

### F-R1-124 — kylin-wlcom.service 用户单元 ExecStart 为 kylin-wlcom -s ukui-session
- 证据：data/kylin-wlcom.service:1-8
- 细节：[Unit] Description="kylin wayland compositor"、Before=graphical-session.target、PartOf=kylin-wlcom.target；[Service] ExecStart=kylin-wlcom -s ukui-session、Slice=session.slice

### F-R1-125 — kylin-wlcom.target 仅两行 Requires/BindsTo service
- 证据：data/kylin-wlcom.target:1-3
- 细节：`Requires=kylin-wlcom.service`、`BindsTo=kylin-wlcom.service`

### F-R1-126 — udev 规则将 graphics 子系统设备节点设为 video 组 0666
- 证据：data/udev-rules/90-framebuffer.rules:1
- 细节：单行 `SUBSYSTEM=="graphics", GROUP="video", MODE="0666"`

### F-R1-127 — kylin-wlcom-wrapper 是用户总线 sd-bus/sd-event 程序，无命令行参数
- 证据：data/wrapper.c:198-243；data/kylin-wlcom-wrapper.1.scd:19-21
- 细节：main 流程 sd_bus_open_user（203）→sd_event_default（210）→sd_bus_attach_event（216）→sd_event_add_signal(SIGTERM|SD_EVENT_SIGNAL_PROCMASK)（222）→drop_session_envs（224）→start_target（226）→sd_event_loop（231）→退出时 stop_target（236）；man 页原文 "The program takes no command-line arguments."

### F-R1-128 — wrapper 启停均通过 systemd Manager D-Bus（StartUnit/StopUnit，mode "replace"）
- 证据：data/wrapper.c:138-187
- 细节：start_target StartUnit "ss" target,"replace"；sd_bus_path_encode("/org/freedesktop/systemd1/unit", target,...) 后 match PropertiesChanged；调 Manager.Subscribe；target ActiveState=="inactive" 时退出事件循环（L127-132）；stop_target StopUnit；静态 target 字符串 "kylin-wlcom.target"（L11）

### F-R1-129 — wrapper 全部输出走 sd_journal_print
- 证据：data/wrapper.c:34、71、128、144、148、191、205 等
- 细节：man 页原文查看方式 `journalctl --user -t kylin-wlcom-wrapper`（kylin-wlcom-wrapper.1.scd:27）；典型消息 "Unset environment %s"、"Target %s is inactive, Exiting..."、"Caught signal %d, Exiting..."

### F-R1-130 — embed 是通用 stdin→C 字节数组生成器，变量名可由 argv[1] 指定，默认 data
- 证据：data/embed.c:9-46；data/meson.build:21
- 细节：签名 `int main(int argc, char *argv[])`；COLS=16；输出 `static const char <varname>[] = {` + 0xHH 十六进制 + 末尾追加 0x00 NUL；全仓 9 个 meson.build 使用（po、portal/po、drm shaders、effect shaders、opengl shaders、scene shaders、plugin/security 嵌入 gui_exe、theme/icons）

### F-R1-131 — 主 man 页仅文档化 h/d/s/v/V 五个选项，未收录 -D 与六个 debug flag
- 证据：data/kylin-wlcom.1.scd:16-31
- 细节：scd 小节 OPTIONS 列 --help/--debug/--session/--version/--verbose；NAME 行 "kylin-wlcom - Default Wayland compositor for Kylin OS"；AUTHORS "Kylin OS Development Team"；wrapper man 描述其为 "systemd user session manager"，记录典型启动 "exec /usr/bin/kylin-wlcom-wrapper"（wrapper.1.scd:33）

## debian 打包

### F-R1-132 — 源码包元数据：Source kylin-wayland-compositor，Section x11，Priority optional，Maintainer Morose
- 证据：debian/control:1-4
- 细节：Maintainer `Morose <chenlinxiang@kylinos.cn>`；Standards-Version 4.6.2（control:34）

### F-R1-133 — 5 个二进制包：主包/client/tools/examples/portal
- 证据：debian/control:36-106（脚本计数 ^Package: = 5）
- 细节：kylin-wayland-compositor（Architecture: any）、kylin-wayland-compositor-client（Depends 主包）、kylin-wayland-compositor-tools（Architecture linux-any，Depends 主包+client）、kylin-wayland-compositor-examples（linux-any）、xdg-desktop-portal-wlcom（linux-any，Depends xdg-desktop-portal，Conflicts xdg-desktop-portal-wlr）

### F-R1-134 — 主包 Replaces 旧 tools 包并 Breaks effects 包
- 证据：debian/control:41-42
- 细节：`Replaces: kylin-wayland-compositor-tools (<< 1.3.1-ok34)`、`Breaks: kylin-wayland-compositor-effects`

### F-R1-135 — rules 使用 dh + meson + quilt，配置阶段强制 ukui_theme=true 与 debugoptimized
- 证据：debian/rules:1-19
- 细节：`%: dh $@ --buildsystem=meson --with quilt`；include /usr/share/dpkg/pkg-info.mk；SUPPORT 变量定义后未见使用（L5）；override_dh_auto_install 用 --destdir=debian/tmp（L13-14）；dh_clean 额外 rm -rf debian/build build-source（L16-19）

### F-R1-136 — 主包 install 清单 10 行，含两个 Qt 工具二进制 kylin-magnifier 与 wldialog
- 证据：debian/kylin-wayland-compositor.install:1-10
- 细节：usr/bin/kylin-wlcom、usr/bin/kylin-wlcom-wrapper、usr/bin/kylin-magnifier、usr/bin/wldialog、usr/lib/udev/rules.d/、usr/share/wayland-sessions/、etc/kylin-wlcom/、usr/lib/systemd/user/kylin-wlcom*、两个 man1 页

### F-R1-137 — tools 包只装 wlcctrl 及其 man；client 包用通配符收 so/include/pkgconfig
- 证据：debian/kylin-wayland-compositor-tools.install:1-2；debian/kylin-wayland-compositor-client.install:1-3
- 细节：tools：usr/bin/wlcctrl、usr/share/man/man1/wlcctrl.1；client：usr/lib/*/lib*.so*、usr/include、usr/lib/*/pkgconfig

### F-R1-138 — examples 包装 kywc-gui 与 thumbnail；portal 包装 libexec 程序、用户服务、dbus 与 portals 配置
- 证据：debian/kylin-wayland-compositor-examples.install:1-2；debian/xdg-desktop-portal-wlcom.install:1-5
- 细节：examples：usr/bin/kywc-gui、usr/bin/thumbnail；portal：usr/lib/systemd/user/xdg-desktop-portal-wlcom.service、usr/libexec/xdg-desktop-portal-wlcom、usr/share/dbus-1/services、usr/share/xdg-desktop-portal、usr/share/xdg-desktop-portal/portals

### F-R1-139 — debian 辅助文件：source format 3.0 (native)、gbp xz 压缩、watch 仅 version=3
- 证据：debian/source/format:1、debian/gbp.conf:1-2、debian/watch:1
- 细节：`3.0 (native)`；`[DEFAULT] compression=xz`；watch 无任何 uscan/watch 规则行（仅 version=3）

### F-R1-140 — changelog 共 75 个版本条目，全部针对发行版 huanghe，近期主题为重建与小修
- 证据：debian/changelog:1-229（脚本计数 75）
- 细节：抽样：ok36/ok35 "fix update error"（2026-09-04）、ok34 Commit 08377060、ok33 "fix build package"、ok30 "rebuild with dbgsym"、ok28 "fix generate xauthority file"、ok27/ok26 "rebuild with new libinput"；全部 urgency=medium、署名 Morose

## tools/（3 个子工具）

### F-R1-141 — tools/meson.build 固定进入 3 个子目录 magnifier/wlcctrl/wldialog
- 证据：tools/meson.build:1-3；根门控 meson.build:247-249（have_tools）
- 细节：脚本计数 tools/ 文件 55（不含 magnifier/translations/），含翻译共 82

### F-R1-142 — wlcctrl 为纯 C 命令行工具，11 个 C 源 + 2 个虚拟输入协议，链接 libkywc
- 证据：tools/wlcctrl/meson.build:1-26
- 细节：源 main/commands/window/workspace/capture/input/seat/output/wlcctrl/cursor/keyboard；协议 virtual-keyboard-unstable-v1、wlr-virtual-pointer-unstable-v1；依赖 wayland_client/libkywc/xkbcommon/kywc_buffer/util；scdoc 生成 wlcctrl.1（L28-42）

### F-R1-143 — wlcctrl 命令表 42 条，按 caps/needs 惰性初始化 wayland/kywc 运行时
- 证据：tools/wlcctrl/commands.c:23-87（脚本计数 42）；tools/wlcctrl/main.c:161-202
- 细节：命令分组——列表类 list/outputs/workspace；窗口 18 个（getactivewindow/search/getwindowname/getwindowgeometry/getwindowstatus/windowkill/windowclose/windowminimize/windowmaximize/windowfullscreen/windowactivate/windowmap/windowmove/windowsize/windowenter/windowleave/movewindowtoworkspace/movewindowtooutput/windowcapture）；工作区 4（workspaceadd[OPTIONAL]/workspaceremove/workspaceactive/workspacecapture）；截图输出 4（getdisplaygeometry/fullscreencapture/setarea/getpixelcolor）；鼠标 6（mousemove/mousebutton/mousepress/mouserelease/scroll/getmouselocation）；键盘 4（keystring/key/keydown/keyup）；exec/sleep；main 汇总 caps|needs 后 init_runtime，版本宏 WLCCTRL_MAJOR/MINOR/PATCH=1.0.0（main.c:17-19）

### F-R1-144 — wlcctrl 选项：短串 lo:x:y:w:h:v，长选项动态生成（每命令一个 --name）外加 help/version/path
- 证据：tools/wlcctrl/main.c:120-141、227-264
- 细节：build_long_options 分配 command_count+3 个 option；ARG_NONE→no_argument 其余 required_argument；ARG_OPTIONAL 裸用且下一 token 以 '-' 开头时自动插入默认参数 "1"（preprocess_argv L87-117）；短参 -o output uuid、-x/-y、-w/-h、-l list、-v version

### F-R1-145 — wlcctrl 按命令在命令行出现的顺序依次执行，任一失败即停止并返回非 0
- 证据：tools/wlcctrl/main.c:283-288；tools/wlcctrl/README.md:11-16
- 细节：main 循环 actions[].cmd->run；README 原文 "命令按命令行中出现的顺序依次执行"、"任一命令执行失败时立即停止"；README 内 "wlrcctrl" 为拼写（README.md:25）

### F-R1-146 — wldialog 是 Qt5(C++/QML) 对话框工具，缺 C++ 编译器或 Qt5 私有头时静默跳过构建
- 证据：tools/wldialog/meson.build:1-21、32-74
- 细节：`add_languages('cpp', native:false, required:false)` 失败 subdir_done；qt5 modules Core/Widgets/Gui/Network/Quick/QuickControls2/Qml + Gui private_headers，任一缺失 subdir_done；moc 7 个头、Resources.qrc；9 个 cpp；依赖 gsettings-qt（magnifier/meson.build:16 定义的 gsettings_dep）、kysdk-ukuiwindowhelper（可选，found 时加 -DKYSDK_IS_SUPPORT，L61-63）

### F-R1-147 — wldialog 协议：xdg-dialog/xdg-foreign-v2/xdg-shell；经 socket fd 收发 JSON（DialogSocket.json 1.0）
- 证据：tools/wldialog/meson.build:23-30；tools/wldialog/DialogSocket.json:1-40；tools/wldialog/Main.cpp:21-70
- 细节：DialogSocket.json 键 protocol_version "1.0"、description "客户端与 wldialog 通信的协议标准"；根键 control/dialog 互斥、update 更新请求、对话框一次性（rules 五条，L7-12）；control.action 0=请求关闭进程，1/2 保留；Main.cpp enum class ButtonResult { ALLOW=0, DENY, CLOSED }、QSocketNotifier 读 fd、writeToSocket 发 Compact JSON

### F-R1-148 — 合成器侧由 view/killer.c 以 spawn_dialog("wldialog") 拉起该工具
- 证据：src/view/killer.c:65、221、244
- 细节：注释 "Send close request to wldialog"（L65）；L221 注释 "wldialog can import it and set itself as a modal child of it."；`dialog->dialog_socket = spawn_dialog("wldialog")`（L244）

### F-R1-149 — kylin-magnifier 为 Qt5 Widgets/DBus 工具，两个 D-Bus XML 经 qdbusxml2cpp 生成代码
- 证据：tools/magnifier/meson.build:1-70
- 细节：qt5 modules Core/DBus/Widgets/Gui；gsettings_dep=`dependency('gsettings-qt')`（必需，L16）；xml_file 映射 org_ukui_Magnifier←org.ukui.Magnifier.xml、com_kylin_Wlcom_Effect←com.kylin.Wlcom.Effect.xml（L24-27）；qdbusxml2cpp 参数 -p/-N/-i dbus_interface_date.h（L31-40）；产物名 kylin-magnifier（L64）；translations 子目录 26 个 .ts + translations.qrc.in

### F-R1-150 — org.ukui.Magnifier 接口含 StartZoom/SetMagnifierMode/ZoomIn/ZoomOut 等方法
- 证据：tools/magnifier/org.ukui.Magnifier.xml:4-40
- 细节：StartZoom(mode:u, scale:u)→success:b；注释内 enum zoom_type { ZOOM_OUTPUT=0, ZOOM_WINDOW }；SetMagnifierMode(mode:u)→b；ZoomIn/ZoomOut→b

## 文档、代码风格、NOTICE、i18n 与其余构建事实

### F-R1-151 — README 为中文项目说明，列 8 项功能特点，编译命令含 meson install --skip-subprojects
- 证据：README.md:1-66
- 细节：自述"基于wlroots编写的wayland合成器""作为默认显示服务器随openKylin系统发布"（L3-5）；功能第 4 条"支持input-method v2和text-input v1/v2/v3"（L18）；第 8 条"支持x11/wayland嵌套运行，支持drm和fbdev显示后端"（L26）；构建三行 meson setup/ninja/meson install（L44-46）；致谢 wlroots/sway/wayfire/labwc 四个项目链接（L89-104）

### F-R1-152 — README 记录的程序参数与源码不完全一致（-D 仅列 3 个 flag，长选项写法有误）
- 证据：README.md:49-64；src/main.c:38-42、70-82
- 细节：README 写 `"-D, --debug <options>    noxwayland or logtostdout."` 并仅举 -Dnoxwayland/-Dlogtostdout/-Dloginmtime 三例（L54、L61-63）；源码 -D 无长选项形式（long_options 无 debug 带参数项），且共 6 个 flag；默认日志路径 README "$HOME/.log/kylin-wlcom.log"（L66）与 logger.c:226 一致

### F-R1-153 — CONTRIBUTING 含手动/嵌套/ASAN 调试流程与提交风格要求
- 证据：docs/CONTRIBUTING.md:1-108
- 细节：手动启动 `sudo systemctl stop lightdm` 后 `kylin-wlcom -s ukui-session`（L15-21）；嵌套运行用 WAYLAND_DISPLAY=[display]（L28-35）；ASAN/UBSAN `meson setup build -Dbuildtype=debug -Db_sanitize=address,undefined`（L41）；valgrind（L46）；Qt 程序 `QT_QPA_PLATFORM=wayland QT_QPA_PLATFORMTHEME=ukui`（L78）；commit 示例 "view: mark mapped before configure"，要求模块前缀、无句号（L97-107）

### F-R1-154 — KNOWN_ISSUES.md 仅 1 条已知问题（ukui 应用双标题栏）
- 证据：docs/KNOWN_ISSUES.md:1-3
- 细节：标题 "# ukui应用显示双标题栏"，正文 "部分应用未使用sdk接口进行设置，需要应用进行修改"

### F-R1-155 — .clang-format 基于 LLVM，4 空格缩进，Linux 花括号，列宽 100
- 证据：.clang-format:1-22
- 细节：BasedOnStyle: LLVM、IndentWidth: 4、BreakBeforeBraces: Linux、AllowShortFunctionsOnASingleLine: Inline、Cpp11BracedListStyle: false、ColumnLimit: 100、SpaceBeforeParens: ControlStatementsExceptForEachMacros；ForEachMacros 列 12 个宏（wl_list/wl_array/wl_resource/json_object_object_foreach/xorg_list/udev_list/hash_table 系列）

### F-R1-156 — NOTICE 声明 3 个第三方来源（redshift/wlroots/sway），其中 2 个被列文件在当前树不存在
- 证据：NOTICE:13-102
- 细节：redshift 段列 "Files: src/output/gamma.c"（NOTICE:15）；wlroots 段列 18 个文件含 src/render/shm_buffer.c（NOTICE:48）；脚本 Test-Path 验证 src/output/gamma.c=False、src/render/shm_buffer.c=False；sway 段列 src/input/text_input.c（NOTICE:82，该文件存在）；wlroots/sway 许可文本为 MIT 样式，redshift 段引用 GPL "version 3 ... or any later version"

### F-R1-157 — po/ 目录 27 个 .po 但 LINGUAS 只启用 16 种语言；mo 在构建期经 embed 转 C 数组内嵌
- 证据：po/LINGUAS:1-16；po/meson.build:1-47（脚本计数 .po=27）
- 细节：LINGUAS 16 行：zh_CN/zh_TW/zh_HK/zh_Hant/bo_CN/ug/kk/ky/mn/ms/de_DE/es_ES/fr_FR/th/vi/ar；每种语言 msgfmt 生成 .mo（L13-18），embed 生成 <lang>_mo.h（L20-27），locales.h 由 locales.h.in 配置生成，表项 `{ "@lang@", @lang@_mo, sizeof(@lang@_mo) - 1 }`（L36）；README:68-77 记录 pot 更新 target `meson compile kylin-wayland-compositor-pot`

### F-R1-158 — libkywc 产出共享库 libkywc.so（版本=project version）与静态 kywc_buffer，安装头文件与 pkg-config
- 证据：libkywc/meson.build:1-72
- 细节：shared_library('kywc', ...) c_args '-fvisibility=default'，版本脚本 kywc.syms（`kywc_*` 导出），version meson.project_version()（L48-57）；静态库 kywc_buffer（buffer.c/buffer.h，依赖 epoxy/png，build_by_default:false，L33-38）；install_headers('libkywc.h')（L65）；pkgconfig description 'Kylin wayland compositor client library'，url 'https://gitee.com/openkylin/kylin-wayland-compositor'（L67-72）；5 个 manager 协议 kywc-capture/output/toplevel/workspace/stream-manager-v1（L18-24）

### F-R1-159 — portal 子产物安装到 libexec，依赖 libei-1.0，附 4 个数据资产
- 证据：portal/meson.build:1-55
- 细节：11 个 C 源（access/ei_sender/main/input_capture/remote_desktop/request/session/screenshot/screencast/stream/wayland）；依赖 wayland_client/sdbus/libkywc/util/kywc_buffer/jsonc/libei-1.0/xkbcommon（L15-21）；安装 xdg-desktop-portal-wlcom.service 到 user 单元、org.freedesktop.impl.portal.desktop.wlcom.service 到 dbus-1/services、wlcom.portal 到 portals、ukui-portals.conf 到 xdg-desktop-portal

### F-R1-160 — examples 产物默认仅构建不安装；gui 子目录的 kywc-gui 与 thumbnail 例外 install:true
- 证据：examples/meson.build:77-103；examples/gui/meson.build:38-78
- 细节：foreach 中 executable 无 install 参数（仅 build_by_default:true，examples/meson.build:84-90）；simple 为 shared_module('simple',..., install:false)（L95-103）；gui 内 kywc-gui（L38-48）、thumbnail（L68-78，源为 ThumMain.cpp 等 Qt 代码）install:true；children/ukui-blur/security/ukui-background 均 install:false

### F-R1-161 — examples/gui 与 wldialog/magnifier 共享同一套 Qt5 可选模式：无 C++/Qt5 即 subdir_done
- 证据：examples/gui/meson.build:1-22
- 细节：qt5 modules Core/Gui/Widgets/Qml/Quick/QuickWidgets + Gui 私有头；依赖 egl/glesv2/libdrm/libkywc；cpp_args 统一 -Wno-unused-parameter

### F-R1-162 — 构建期存在第二处 wldialog 同名机制：security 插件把 gui.cpp 编译出的可执行文件整体嵌入
- 证据：src/plugin/security/meson.build:57、73-75；src/plugin/security/security.c:22、60-61
- 细节：gui_exe = executable(...) 后经 embed 生成 gui_exe.h；security.c `#include "gui_exe.h"` 并 `write(fd, gui_exe, sizeof(gui_exe))` 将内嵌 ELF 写出执行（与 tools/wldialog 是两个不同二进制）

## 疑点与矛盾

### D-R1-01 — meson 工程版本 1.3.0 与 debian changelog 版本 1.3.1-ok36 不一致
- 证据：meson.build:5（version: '1.3.0'）；debian/changelog:1（1.3.1-ok36）
- 细节：meson.build:40-46 在 dpkg-parsechangelog 存在时会用 changelog 版本覆盖，故 Debian 构建产物 KYWC_VERSION 实际为 1.3.1-ok36[.g<hash>]；非 Debian 环境直编为 1.3.0[.g<hash>]。属事实差异，是否问题留 V 阶段

### D-R1-02 — README 依赖清单列 libseat，根 meson 未声明且 wlroots 以 session=disabled 构建
- 证据：README.md:33；meson.build:59、74-97
- 细节：全根 meson 无 `dependency('libseat'`；会话实现见 src/backend/session/（logind），细节属 R2 范围

### D-R1-03 — README/文档的 -D 用法与源码不符：长选项名缺失、flag 数量少 3 个
- 证据：README.md:54、61-63；src/main.c:38-42、70-82；data/kylin-wlcom.1.scd:16-31
- 细节：README 写 "-D, --debug <options>"，源码 long_options 中 --debug 是 no_argument（对应 -d），-D 只有短形式；README 仅文档化 3/6 个 flag（缺 lognoratelimit/nosessionbinding/nolazyxwayland）；man 页完全未提 -D

### D-R1-04 — ENV.md 缺 KYWC_XWAYLAND、KYWC_EIS_SOCKET 两个合成器实际读取的变量
- 证据：docs/ENV.md 全文；src/xwayland/server.c:133、479；src/backend/eis/backend.c:93
- 细节：同时 ENV.md 的 4 个应用侧变量（DRI_PRIME 等）合成器自身代码不读取（文档已自述供应用使用，算口径差而非硬矛盾）

### D-R1-05 — NOTICE 列出的 src/output/gamma.c 与 src/render/shm_buffer.c 在固定提交树中不存在
- 证据：NOTICE:15、48；脚本 Test-Path 两路径均为 False；全树 glob 无 gamma.c/shm_buffer.c
- 细节：可能为重构后 NOTICE 未同步；属法律文本与代码树漂移，建议 V 阶段全量核对 NOTICE 文件清单

### D-R1-06 — po 目录 27 个 .po 与 LINGUAS 16 种语言不一致（11 个 .po 不参与构建）
- 证据：po/LINGUAS（16 非空行）；脚本 Get-ChildItem po/*.po=27；po/meson.build:3-8（仅遍历 LINGUAS）
- 细节：未启用语言可由两份清单 diff 得到（如 ja.po、ko_KP.po、lo.po、my.po、pt.po、ru.po、tr.po、ur.po、khb_CN.po、id.po、it.po 等存在于目录但不在 LINGUAS——精确差集 V 阶段再核）

### D-R1-07 — protocols/meson.build 中 'linux-dmabuf-v1' 键被赋值两次
- 证据：protocols/meson.build:24（基础字典，指向 wayland-protocols stable 路径）、161-166（have_ukui_background 块内再次同键同值）
- 细节：Meson dict 重复键后写覆盖；两处值字面相同，当前无行为差异，属冗余

### D-R1-08 — 主包安装了 tools 选项构建出的两个 Qt 二进制（kylin-magnifier/wldialog），而 -tools 包仅装 wlcctrl
- 证据：debian/kylin-wayland-compositor.install:3-4；tools/magnifier/meson.build:64；tools/wldialog/meson.build:65-66；debian/control:65-79
- 细节：打包归属与 meson 子目录划分（tools/）不一致；若 -Dtools=false，主包 install 清单将找不到这两个文件（Debian rules 未关 tools，默认 true，故实际不触发）

### D-R1-09 — debian/rules 中 SUPPORT 变量定义后未使用
- 证据：debian/rules:5
- 细节：`SUPPORT = https://www.debian.org/support`，全文件无引用

### D-R1-10 — examples 顶层 thumbnail（examples/thumbnail.c）与 gui 内 thumbnail（ThumMain.cpp）同名目标，仅后者安装
- 证据：examples/meson.build:44-49（不安装）；examples/gui/meson.build:68-78（install:true）；debian/kylin-wayland-compositor-examples.install:2
- 细节：两者输出文件名均为 thumbnail（位于不同构建子目录）；Debian 包拿到的是 Qt GUI 版本
