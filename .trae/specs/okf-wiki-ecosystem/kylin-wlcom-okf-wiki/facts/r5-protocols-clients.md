# R5 事实清单：protocols / libkywc / portal / examples / i18n

- 采集对象：external/dao/action/kylin-wayland-compositor（下文路径均相对该仓库根）
- 固定提交：4df656222427f3cd0101e41d828fb64805e66c15（分支 openkylin/huanghe）
- 采集方式：只读，未做 checkout/修改；XML 字段由 ElementTree 解析，计数由脚本复核
- 项目元数据：meson.build:1-11，project='kylin-wayland-compositor'，version='1.3.0'，license GPL-1.0-or-later，c_std=c11

## 采集范围与计数总览

### F-R5-001 — protocols/ 下 XML 文件数为 34
- 证据：protocols/*.xml（脚本口径：`len(glob('protocols/*.xml'))` = 34）
- 细节：34 个 XML 共声明 77 个 interface（脚本对每个 XML 的 `<interface>` 节点求和）

### F-R5-002 — protocols/meson.build 字典内含 29 个固定协议键 + 多个 meson 选项条件块
- 证据：protocols/meson.build:4-178
- 细节：基础 dict（L4-30）25 键，追加 dict（L32-41）7 键（6 个 kywc + wlr-screencopy）；条件块键：drm-lease（have_drm_lease_device，L43-47）、alpha-modifier（have_alpha_modifier，L49-53）、kde 4 个（have_kde_output，L55-62）、plasma-virtual-desktop（L64-68）、wlr-output-power（L70-74）、wlr-layer-shell（L76-80）、plasma-shell（L82-86）、plasma-window-management（L88-92）、kde-blur（L94-98）、kde-slide（L100-104）、kde-keystate（L106-110）、ukui-shell（L112-116）、ukui-window-management（L118-122）、ukui-output（L124-128）、ukui-blur（L130-134）、ukui-effect（L136-140）、ukui-startup（L142-146）、xdg-toplevel-icon（L148-152）、virtual-keyboard + wlr-virtual-pointer（have_tools，L154-159）、ukui-background + 重复 linux-dmabuf-v1（have_ukui_background，L161-166）、xwayland-shell（have_xwayland，L168-172）、xdg-toplevel-tag（L174-178）

### F-R5-003 — libkywc/ 下 C/H 文件 17 个
- 证据：libkywc/（脚本口径 glob('libkywc/*.{c,h}') = 17）
- 细节：13 个 .c（libkywc.c、output.c、toplevel.c、thumbnail.c、workspace.c、cursor.c、stream.c、buffer.c、kywc_capture.c、kywc_output.c、kywc_toplevel.c、kywc_workspace.c、kywc_stream.c）+ 4 个 .h（libkywc.h、libkywc_p.h、provider.h、buffer.h）；另有 kywc.syms、meson.build

### F-R5-004 — portal/ 下 C/H 文件 14 个，data/ 下 4 个单元文件
- 证据：portal/meson.build:1-13；portal/data/
- 细节：11 个 .c（access/ei_sender/main/input_capture/remote_desktop/request/session/screenshot/screencast/stream/wayland）+ 3 个 .h（portal.h、ei_sender.h、stream.h）=14；data 为 wlcom.portal、org.freedesktop.impl.portal.desktop.wlcom.service、xdg-desktop-portal-wlcom.service、ukui-portals.conf

### F-R5-005 — examples/ 下 C/CPP/H 文件 34 个
- 证据：examples/**/*.{c,h,cpp}（脚本口径：.c=14、.h=6、.cpp=14，合计 34）
- 细节：根目录 9 个 .c；lib/ 5 个 .c + 2 个 .h；gui/ 14 个 .cpp + 4 个 .h

### F-R5-006 — po/ 主域 .po 27 个、LINGUAS 列 16 语言；portal/po 子域 .po 19 个、LINGUAS 列 1 语言
- 证据：po/*.po（27）、po/LINGUAS（16 行）；portal/po/*.po（19）、portal/po/LINGUAS（1 行 zh_CN）
- 细节：主 LINGUAS 16 码：zh_CN、zh_TW、zh_HK、zh_Hant、bo_CN、ug、kk、ky、mn、ms、de_DE、es_ES、fr_FR、th、vi、ar

### F-R5-007 — libkywc 共享库源码中非 static 的 kywc_* 函数定义为 67 个，与 libkywc.h 声明一一对应
- 证据：脚本对 libkywc/*.c（排除 buffer.c）正则计数非 static `kywc_*(` 定义 = 67；libkywc.h 函数声明 = 67
- 细节：差额为空（declared not defined=[]，defined not declared 仅 static 函数）；另有 static kywc_context_init_providers（libkywc.c:36）、static kywc_stream_create（stream.c:72）不导出

### F-R5-008 — docs/PROTOCOLS.md 共 10 个分节、118 个数据行
- 证据：docs/PROTOCOLS.md:6-180（脚本统计以 `| ` 开头、排除表头/分隔行）
- 细节：Wayland core 7、stable 3、staging 20、unstable 24、wlr 10、kde 24、weston 10、external 8、ukui 7、kywc 5

### F-R5-009 — 主程序可执行文件名为 kylin-wlcom，链接两个版本脚本之一 wlcom.syms
- 证据：meson.build:311-325
- 细节：executable('kylin-wlcom', …, export_dynamic: true, link_args: '-Wl,--version-script,…/wlcom.syms', c_args: '-DTARGET_NAME="kylin-wlcom"')；wlcom.syms 位于仓库根（非 src/）

### F-R5-010 — wlcom.syms 内容与 libkywc/kywc.syms 完全相同
- 证据：wlcom.syms:1-6；libkywc/kywc.syms:1-6
- 细节：两文件均为 `{ global: kywc_*; local: *; };`
- 备注：主程序二进制因此导出 kywc_* ABI（include/kywc/*.h 声明的插件 ABI，如 kywc_key_binding_create），供 dlopen 插件使用；意图性陈述，依据为版本脚本文本与 examples/simple_plugin.c 的调用

### F-R5-011 — 关键依赖版本基线
- 证据：meson.build:56-97
- 细节：wlroots >=0.17.0,<0.18.0（default_options: renderers=vulkan, backends=x11, xwayland=disabled, session=disabled）；wayland-server >=1.23.0；wayland-protocols >=1.36；libinput >=1.19；json-c >=0.13；gbm >=21.1；librsvg-2.0 >=2.46；libpipewire-0.3；libsystemd(sd-bus)；编译期 -DWLR_USE_UNSTABLE（meson.build:63）

### F-R5-012 — NLS 为编译期嵌入，非运行时读 /usr/share/locale
- 证据：po/meson.build:12-47；data/meson.build:21（embed = executable('embed', 'embed.c')）；po/locales.h.in:1-8
- 细节：每语言 .po 经 msgfmt 生成 .mo，再经宿主工具 embed 转成 `<lang>_mo.h` 字节数组，configure_file 注入 locales.h 的 `static const struct locale locales[] = { {"<lang>", <lang>_mo, sizeof-1}, … }`；portal 侧同构（portal/po/meson.build:1-47）；编译宏 HAVE_NLS（meson.build:227-228、232-233）

## 协议 XML 清单与族属（34 个逐一）

> 族属口径：wayland（wayland/xdg 系上游不稳定协议）、wlr（wlroots）、kde（plasma-wayland-protocols）、ukui（openkylin kylin-wayland-protocols）、kywc（自研）、external（wl_drm）。interface 数/最高 version 由 XML 解析。

### F-R5-013 — blur.xml，族属 kde，2 interface，最高 v1
- 证据：protocols/blur.xml；注册点 src/view/kde_blur.c:262
- 细节：org_kde_kwin_blur_manager(v1, req2)、org_kde_kwin_blur(v1, req3)；meson 键 org-kde-kwin-blur-manager，门控 have_kde_blur（protocols/meson.build:94-98）

### F-R5-014 — dpms.xml，族属 kde，2 interface，最高 v1
- 证据：protocols/dpms.xml；注册点 src/output/kde_output.c:1128
- 细节：org_kde_kwin_dpms_manager(v1, req1)、org_kde_kwin_dpms(v1, req2/ev3/enum1)；meson 键 org-kde-kwin-dpms-manager（门控 have_kde_output，L60）

### F-R5-015 — drm.xml，族属 external，1 interface，wl_drm v2
- 证据：protocols/drm.xml；注册点 src/render/wayland_drm.c:282
- 细节：wl_drm(v2, req4/ev4/enum3)；meson 键 wl-drm（L5）；服务端 wl_global_create(…,&wl_drm_interface,WLR_DRM_VERSION,…,drm_bind)

### F-R5-016 — idle.xml，族属 kde，2 interface，最高 v1
- 证据：protocols/idle.xml；注册点 src/input/idle.c:368
- 细节：org_kde_kwin_idle(v1, req1)、org_kde_kwin_idle_timeout(v1, req2/ev2)；同文件 idle.c:361 另注册 wayland-protocols 的 ext_idle_notifier_v1

### F-R5-017 — kde-keystate.xml，族属 kde，1 interface，org_kde_kwin_keystate v5
- 证据：protocols/kde-keystate.xml；注册点 src/input/kde_keystate.c:317
- 细节：req2（states/fetchStates）、ev1（stateChanged）、enum2（key 3 项 capslock/numlock/scrolllock，state  unlocked/locked）

### F-R5-018 — kde-output-device-v2.xml，族属 kde，2 interface，最高 v8
- 证据：protocols/kde-output-device-v2.xml；注册点 src/output/kde_output.c:900
- 细节：kde_output_device_v2(v8, ev25/enum7)、kde_output_device_mode_v2(v1, ev4)

### F-R5-019 — kde-output-management-v2.xml，族属 kde，2 interface，最高 v9
- 证据：protocols/kde-output-management-v2.xml；注册点 src/output/kde_output.c:1096
- 细节：kde_output_management_v2(v9, req1 create_configuration)、kde_output_configuration_v2(v9, req21/ev2/enum5)

### F-R5-020 — kde-primary-output-v1.xml，族属 kde，1 interface，kde_primary_output_v1 v2
- 证据：protocols/kde-primary-output-v1.xml；注册点 src/output/kde_output.c:1114
- 细节：req1（set_primary_output）、ev1（primary_output）

### F-R5-021 — kywc-capture-v1.xml，族属 kywc，3 interface，最高 v2
- 证据：protocols/kywc-capture-v1.xml；注册点 src/effect/ky_capture.c:614（wl_global_create version=2）
- 细节：kywc_capture_manager_v1(v2, req5：capture_output/capture_workspace/capture_toplevel/capture_cursor/destroy)；kywc_capture_frame_v1(v2, req2 destroy/release_buffer，ev5 failed/cancelled/buffer/buffer_with_plane/buffer_done，enum flags: dmabuf/reused)；kywc_capture_cursor_v1(v2, req1, ev4 enter/leave/position/hotspot)

### F-R5-022 — kywc-output-v1.xml，族属 kywc，3 interface，最高 v1
- 证据：protocols/kywc-output-v1.xml；注册点 src/output/ky_output.c:659
- 细节：kywc_output_manager_v1(req1 stop；ev4 output/primary/done/finished)；kywc_output_v1(req1 destroy；ev17 含 name/make/model/serial_number/description/physical_size/mode/capabilities/enabled/current_mode/position/transform/scale/power/brightness/color_temp/finished；enum capability: power/brightness/color_temp)；kywc_output_mode_v1(req1；ev4 size/refresh/preferred/finished)

### F-R5-023 — kywc-security-v1.xml，族属 kywc，2 interface，最高 v1
- 证据：protocols/kywc-security-v1.xml；注册点 src/security/ky_security.c:369
- 细节：kywc_security_manager_v1(req3 destroy/get_security_for_surface/get_security_for_output)；kywc_security_v1(req3 destroy/enable/disable；ev4 failed/cancelled/enabled/touched)

### F-R5-024 — kywc-stream-v1.xml，族属 kywc，2 interface，最高 v1
- 证据：protocols/kywc-stream-v1.xml；注册点 src/effect/ky_stream.c:213
- 细节：kywc_stream_manager_v1(req3 stream_output/stream_toplevel/destroy；enum pointer: hidden/embedded/metadata)；kywc_stream_v1(req1 destroy；ev3 failed/cancelled/created(uint32 node))
- 备注：XML 第 2 行 `<protocol name="kywc_capture_v1">` 与 kywc-capture-v1.xml 的 protocol 名相同，见 F-R5-170

### F-R5-025 — kywc-toplevel-v1.xml，族属 kywc，2 interface，最高 v1
- 证据：protocols/kywc-toplevel-v1.xml；注册点 src/view/ky_toplevel.c:812
- 细节：kywc_toplevel_manager_v1(req1 stop；ev2 toplevel/finished)；kywc_toplevel_v1(req15，含 set_maximized/unset_*/activate/close/enter_workspace/leave_workspace/move_to_workspace/move_to_output/set_position/set_size；ev13 含 closed/done/title/app_id/primary_output/workspace_enter/workspace_leave/capabilities/state/parent/icon/geometry/pid；enum capability: skip_taskbar/skip_switcher；enum state: maximized/minimized/activated/fullscreen)

### F-R5-026 — kywc-workspace-v1.xml，族属 kywc，2 interface，最高 v1
- 证据：protocols/kywc-workspace-v1.xml；注册点 src/view/ky_workspace.c:339
- 细节：kywc_workspace_manager_v1(req2 create_workspace/stop；ev3 workspace/done/finished)；kywc_workspace_v1(req5 destroy/set_position/activate/remove/set_name；ev5 name/position/activated/deactivated/removed)

### F-R5-027 — plasma-shell.xml，族属 kde，2 interface，最高 v8
- 证据：protocols/plasma-shell.xml；注册点 src/view/kde_plasma_shell.c:435
- 细节：org_kde_plasma_shell(v8, req1 get_surface)；org_kde_plasma_surface(v8, req11/ev2/enum3)

### F-R5-028 — plasma-virtual-desktop.xml，族属 kde，2 interface，最高 v2
- 证据：protocols/plasma-virtual-desktop.xml；注册点 src/view/kde_virtual_desktop.c:284
- 细节：org_kde_plasma_virtual_desktop_management(v2, req3：request_create_virtual_desktop/request_remove_virtual_desktop/get_virtual_desktop；ev4)；org_kde_plasma_virtual_desktop(v1, req1/ev6)

### F-R5-029 — plasma-window-management.xml，族属 kde，5 interface，最高 v17
- 证据：protocols/plasma-window-management.xml；注册点 src/view/kde_plasma_window.c:931
- 细节：org_kde_plasma_window_management(v17, req4/ev6/enum2)、org_kde_plasma_window(v17, req15/ev17)、org_kde_plasma_activation_feedback(v1)、org_kde_plasma_activation(v1)、org_kde_plasma_stacking_order(v17, ev2)

### F-R5-030 — slide.xml，族属 kde，2 interface，最高 v1
- 证据：protocols/slide.xml；注册点 src/view/kde_slide.c:257
- 细节：org_kde_kwin_slide_manager(v1, req2)、org_kde_kwin_slide(v1, req4/enum1)；门控 have_kde_slide

### F-R5-031 — text-input-unstable-v2.xml，族属 wayland(unstable)，2 interface，最高 v1
- 证据：protocols/text-input-unstable-v2.xml；注册点 src/input/text_input_v2.c:296
- 细节：zwp_text_input_v2(req10/ev15/enum6)、zwp_text_input_manager_v2(req2)；同仓另有 v1（src/input/text_input_v1.c:294）与 v3（text_input_v3.c:292），二者 XML 取自 wayland-protocols pkgdatadir（protocols/meson.build:10、12）

### F-R5-032 — ukui-background-v1.xml，族属 ukui，2 interface，最高 v1
- 证据：protocols/ukui-background-v1.xml；注册点 src/output/ukui_background.c:262
- 细节：ukui_background_manager_v1(req2 destroy/create_background；enum2)、ukui_background_v1(req2 destroy/set_buffer；ev1)；门控 have_ukui_background

### F-R5-033 — ukui-blur-v1.xml，族属 ukui，2 interface，最高 v3
- 证据：protocols/ukui-blur-v1.xml；注册点 src/view/ukui_blur.c:343
- 细节：ukui_blur_manager_v1(v3, req2/enum1)、ukui_blur_surface_v1(v3, req5/enum1)

### F-R5-034 — ukui-effect-v1.xml，族属 ukui，4 interface，最高 v1
- 证据：protocols/ukui-effect-v1.xml；注册点 src/effect/ukui_effect.c:710
- 细节：ukui_effect_v1(req4/ev2/enum2)、animation_curve_v1(req1)、fade_effect_v1(req6/enum1)、slide_effect_v1(req5/enum2)

### F-R5-035 — ukui-output-v1.xml，族属 ukui，2 interface，最高 v1
- 证据：protocols/ukui-output-v1.xml；注册点 src/output/ukui_output.c:281
- 细节：ukui_output_management_v1(req1 destroy；ev2 primary_output/output)、ukui_output_v1(req1 destroy；ev3 geometry/available_mode/logical_mode)

### F-R5-036 — ukui-shell-v1.xml，族属 ukui，3 interface，最高 v4
- 证据：protocols/ukui-shell-v1.xml；注册点 src/view/ukui_shell.c:1248
- 细节：ukui_shell_v1(v4, req3/ev2/enum1)、ukui_surface_v1(v4, req15/ev2/enum4)、ukui_decoration_v1(v4, req3/enum2)

### F-R5-037 — ukui-startup-v2.xml，族属 ukui，2 interface，最高 v1
- 证据：protocols/ukui-startup-v2.xml；注册点 src/view/ukui_startup.c:230
- 细节：ukui_startup_management_v2(req2 startup/destroy)、ukui_startup_info_v2(req4)

### F-R5-038 — ukui-window-management.xml，族属 ukui，5 interface，最高 v3
- 证据：protocols/ukui-window-management.xml；注册点 src/view/ukui_window.c:1243
- 细节：ukui_window_management(v3, req3/ev4/enum1)、ukui_window(v3, req17/ev17/enum1)、org_ukui_activation_feedback(v3)、org_ukui_activation(v3)、org_ukui_stacking_order(v3, ev2)

### F-R5-039 — virtual-keyboard-unstable-v1.xml，族属 wayland(unstable)，2 interface，最高 v1
- 证据：protocols/virtual-keyboard-unstable-v1.xml；注册点 src/input/input.c:823
- 细节：zwp_virtual_keyboard_v1(req4/enum1)、zwp_virtual_keyboard_manager_v1(req1 create_virtual_keyboard)；服务端用 wlroots 助手 wlr_virtual_keyboard_manager_v1_create(display) 创建全局；门控 have_tools；客户端工具 tools/wlcctrl/wlcctrl.c:20-22 绑定之

### F-R5-040 — wlr-data-control-unstable-v1.xml，族属 wlr，4 interface，最高 v2
- 证据：protocols/wlr-data-control-unstable-v1.xml；注册点 src/input/wlr_data_control.c:751
- 细节：zwlr_data_control_manager_v1(v2, req3)、device_v1(v2, req3/ev4/enum1)、source_v1(v1, req2/ev2/enum1)、offer_v1(v1, req2/ev1)

### F-R5-041 — wlr-layer-shell-unstable-v1.xml，族属 wlr，2 interface，最高 v4
- 证据：protocols/wlr-layer-shell-unstable-v1.xml；注册点 src/view/wlr_layer_shell.c:564
- 细节：zwlr_layer_shell_v1(v4, req2 get_layer_surface/destroy；enum2 error/layer)、zwlr_layer_surface_v1(v4, req9 set_size/set_anchor/set_exclusive_zone/set_margin/set_keyboard_interactivity/get_popup/ack_configure/destroy/set_layer；ev2 configure/closed；enum3 keyboard_interactivity/error/anchor)；服务端 wlr_layer_shell_v1_create(server->display, 4)（外层函数 wlr_layer_shell_manager_create，L557）

### F-R5-042 — wlr-output-power-management-unstable-v1.xml，族属 wlr，2 interface，最高 v1
- 证据：protocols/wlr-output-power-management-unstable-v1.xml；注册点 src/output/wlr_output.c:191
- 细节：zwlr_output_power_manager_v1(req2 get_output_power/destroy；ev2 mode/failed；enum2 mode)、zwlr_output_power_v1(req2 set_mode/destroy；ev2 mode/failed；enum2)；服务端 wlr_output_power_manager_v1_create(display)

### F-R5-043 — wlr-screencopy-unstable-v1.xml，族属 wlr，2 interface，最高 v3
- 证据：protocols/wlr-screencopy-unstable-v1.xml；注册点 src/effect/wlr_screencopy.c:443
- 细节：zwlr_screencopy_manager_v1(v3, req3 capture_output/capture_output_region/destroy)、zwlr_screencopy_frame_v1(v3, req3 copy/destroy/copy_with_damage；ev7 buffer/flags/ready/failed/damage/linux_dmabuf/buffer_done；enum2)；全局 version 固定 3

### F-R5-044 — wlr-virtual-pointer-unstable-v1.xml，族属 wlr，2 interface，最高 v2
- 证据：protocols/wlr-virtual-pointer-unstable-v1.xml；注册点 src/input/input.c:818
- 细节：zwlr_virtual_pointer_v1(v2, req9 motion/motion_absolute/button/axis/frame/axis_source/axis_stop/axis_discrete/destroy；enum1)、manager_v1(v2, req3 create_virtual_pointer/destroy/create_virtual_pointer_with_output)；wlr_virtual_pointer_manager_v1_create(display)；tools/wlcctrl/wlcctrl.c:24-26 客户端绑定

### F-R5-045 — xdg-toplevel-icon-v1.xml，族属 wayland(staging)，2 interface，最高 v1
- 证据：protocols/xdg-toplevel-icon-v1.xml；注册点 src/view/xdg_toplevel_icon.c:352
- 细节：xdg_toplevel_icon_manager_v1(req3 destroy/create_icon/set_icon；ev2 icon_size/done)、xdg_toplevel_icon_v1(req3 destroy/set_name/add_buffer；enum1)

### F-R5-046 — xdg-toplevel-tag-v1.xml，族属 wayland(staging)，1 interface，xdg_toplevel_tag_manager_v1 v1
- 证据：protocols/xdg-toplevel-tag-v1.xml；注册点 src/view/xdg_toplevel_tag.c:105
- 细节：manager req3：destroy、set_toplevel_tag、set_toplevel_description；无事件；只含 manager 单接口（无配套 tag 对象 interface）

## 代码生成与全局注册机制

### F-R5-047 — 每个协议经 wayland-scanner 生成三件产物
- 证据：protocols/meson.build:183-211
- 细节：foreach name,path：`<key>_c` = wayland-scanner private-code → '@BASENAME@-protocol.c'；`<key>_server_h` = server-header → '@BASENAME@-protocol.h'；`<key>_client_h` = client-header → '@BASENAME@-client-protocol.h'（build_by_default: false）；前两者加入 wlcom_sources，三者分别入 protocols_code/protocols_server_header/protocols_client_header 字典

### F-R5-048 — 本地 XML 头文件命名实例
- 证据：libkywc/kywc_capture.c:9、kywc_output.c:8、kywc_stream.c:8、kywc_toplevel.c:8、kywc_workspace.c:8
- 细节：include 名分别为 "kywc-capture-v1-client-protocol.h"、"kywc-output-v1-client-protocol.h"、"kywc-stream-v1-client-protocol.h"、"kywc-toplevel-v1-client-protocol.h"、"kywc-workspace-v1-client-protocol.h"（与 @BASENAME@ 规则一致）

### F-R5-049 — 自研协议服务端直接 wl_global_create 注册并手写 bind
- 证据：src/effect/ky_capture.c:614、ky_stream.c:213、src/security/ky_security.c:369、src/output/ky_output.c:659、src/view/ky_toplevel.c:812、ky_workspace.c:339、src/effect/ukui_effect.c:710
- 细节：如 wl_global_create(server->display, &kywc_capture_manager_v1_interface, 2, …, …_bind)；ukui_effect 末参显式 ukui_effect_bind

### F-R5-050 — 部分上游协议由 wlroots 助手函数内部创建全局，compositor 不直接 wl_global_create
- 证据：src/input/input.c:818、823、828、829、831、836；src/output/wlr_output.c:187、191；src/view/wlr_layer_shell.c:564；src/view/view.c:2893；src/view/wlr_foreign_toplevel.c:307；src/input/idle_inhibit.c:175；src/input/tablet.c:396；src/xwayland/xwayland.c:88；src/server.c:284、285
- 细节：wlr_virtual_pointer_manager_v1_create、wlr_virtual_keyboard_manager_v1_create、wlr_pointer_gestures_v1_create、wlr_relative_pointer_manager_v1_create、wlr_keyboard_shortcuts_inhibit_v1_create、wlr_pointer_constraints_v1_create、wlr_output_manager_v1_create、wlr_output_power_manager_v1_create、wlr_layer_shell_v1_create(display,4)、wlr_xdg_foreign_registry_create、wlr_foreign_toplevel_manager_v1_create、wlr_idle_inhibit_v1_create、wlr_tablet_v2_create、xwayland_shell_v1_create、wlr_viewporter_create、wlr_fractional_scale_manager_v1_create

### F-R5-051 — 其余本地 XML 注册点（upstream/wlr 协议但 compositor 手写 bind）
- 证据：src/input/data_device.c:1524（wl_data_device_manager v3）；src/input/primary_selection.c:605；src/input/wlr_data_control.c:751；src/input/transient_seat.c:153；src/input/toplevel_drag.c:226；src/input/text_input_v1.c:294、text_input_v2.c:296、text_input_v3.c:292；src/output/xdg_output.c:291；src/render/single_pixel.c:183；src/render/drm_syncobj_v1.c:463；src/render/renderer.c:88；src/render/wayland_drm.c:282；src/scene/tearing_control.c:174；src/scene/presentation_time.c:228；src/scene/alpha_modifier.c:201；src/security/security_context.c:422；src/view/ext_foreign_toplevel.c:222；src/view/xdg_dialog.c:186；src/view/xdg_activation.c:204（wlr 助手）；src/xwayland/shell.c:163；src/backend/drm/lease.c:665
- 细节：linux-dmabuf 走 wlr_linux_dmabuf_v1_create_with_renderer(wl_display, 4, renderer)（renderer.c:88）

### F-R5-052 — src/ 内还存在第 35 个 XML（不在 protocols/ 34 个清单内）
- 证据：src/plugin/security/security.xml:1-55；消费点 src/plugin/security/security.c:362、373、466
- 细节：protocol name="kywc_security_configuration_v1"，interface kywc_security_configuration_v1 v1，req4（destroy、set_protector_mode、set_protector_color、set_protector_image），enum protector_mode: fill_none(0)/fill_color(1)/fill_image(2)；版权 SPDX MulanPSL-2.0（security.xml:3-6，区别于其余文件的 GPL-1.0-or-later 头）；wl_global_create 位于 security.c:466

## PROTOCOLS.md 矩阵对账

### F-R5-053 — kywc 分节仅列 5 行，缺 kywc_stream_manager_v1
- 证据：docs/PROTOCOLS.md:172-180 vs protocols/kywc-stream-v1.xml、src/effect/ky_stream.c:213
- 细节：文档列 capture(v2)/output(v1)/security(v1)/toplevel(v1)/workspace(v1)；stream manager v1 在 XML、meson、libkywc、portal 中均存在，文档未列；详见 F-R5-169

### F-R5-054 — staging 表 20 行中 xwayland_shell_v1 重复出现两次
- 证据：docs/PROTOCOLS.md:47 与 docs/PROTOCOLS.md:52
- 细节：两行内容均为 `| xwayland_shell_v1 | 1 |`；去重后 staging 唯一协议 19 个

### F-R5-055 — staging 表标 no 的 2 项
- 证据：docs/PROTOCOLS.md:34（wp_content_type_manager_v1 = no）、docs/PROTOCOLS.md:39（ext_session_lock_manager_v1 = no）
- 细节：两行说明列均为 "1"；Grep src/ 未见对应 *_interface 全局注册

### F-R5-056 — XML 与文档版本一致项抽查（kywc/ukui/wlr/kde）
- 证据：docs/PROTOCOLS.md:89-98、106-128、162-180 对 protocols/*.xml 解析结果
- 细节：一致：zwlr_data_control_manager_v1 2、layer_shell 4、output_power 1、screencopy 3、virtual_pointer 2；org_kde_kwin_blur 1、dpms 1、idle 1、keystate 5、primary_output 2、plasma_virtual_desktop 2、plasma_shell 8、plasma_window_management 17、slide 1；ukui_blur 3、output 1、shell 4、window_management 3、startup 1、effect 1、background 1；kywc_capture 2、其余 1

### F-R5-057 — kde_output_device_v2 / management_v2 文档“支持 8/9、说明列 12”
- 证据：docs/PROTOCOLS.md:112-113；XML kde-output-device-v2.xml（v8）、kde-output-management-v2.xml（v9）
- 细节：本地 vendored XML 最高 interface version 分别为 8 和 9；文档说明列 12 对应上游 plasma-wayland-protocols 版本号，非本仓 XML 版本

### F-R5-058 — wlr 分节中 foreign_toplevel(v3) 与 output_manager(v4) 无本地 XML
- 证据：docs/PROTOCOLS.md:91、95；src 注册点 src/view/wlr_foreign_toplevel.c:307、src/output/wlr_output.c:187
- 细节：二者通过 wlroots 安装头 wlr/types/wlr_foreign_toplevel_management_v1.h、wlr_output_management_v1.h 由 wlroots 内部生成代码注册，protocols/ 与 protocols/meson.build 均无对应键

### F-R5-059 — external 表 3 项与本地 XML/代码对账一致
- 证据：docs/PROTOCOLS.md:150、153-155；protocols/drm.xml、text-input-unstable-v2.xml、virtual-keyboard-unstable-v1.xml
- 细节：wl_drm=2（XML v2，wayland_drm.c:282 WLR_DRM_VERSION）；zwp_input_method_manager_v2=1（wlr 助手体系，无本地 XML）；zwp_virtual_keyboard_manager_v1=1；zwp_text_input_manager_v2=1；标 no：wl_eglstream、wl_eglstream_controller、qt_surface_extension、gtk_shell1

### F-R5-060 — Wayland core 表 wl_seat 行“支持 6、说明 9”
- 证据：docs/PROTOCOLS.md:15
- 细节：wl_compositor 6、wl_shm 1、wl_data_device_manager 3、wl_seat 6(说明9)、wl_output 4、wl_subcompositor 1，wl_shell 标 deprecated；这些 core 全局由 wlroots 在 wl_display 上创建，src/ 无对应 XML

### F-R5-061 — weston 分节 10 项全部标 no
- 证据：docs/PROTOCOLS.md:133-144
- 细节：ivi_surface、ivi_hmi_controller、text_cursor_position、weston_content_protection、weston_debug_v1、weston_desktop_shell、weston_direct_display_v1、weston_capture_v1、weston_test、weston_touch_calibration 均 no

### F-R5-062 — unstable 表 24 行中 5 项标 no/-
- 证据：docs/PROTOCOLS.md:59-82
- 细节：no：zwp_fullscreen_shell_v1、zwp_input_method_context_v1、zwp_linux_explicit_synchronization_v1(deprecated)、zwp_xwayland_keyboard_grab_manager_v1；“-”：zwp_tablet_manager_v1（说明 v2，代码 tablet.c:396 wlr_tablet_v2_create）、xdg_shell/zxdg_shell_v6（说明 xdg_wm_base）

## libkywc 定位与 provider 机制

### F-R5-063 — libkywc 构建为共享库 libkywc.so（soname 随项目版本），仅安装 1 个头文件
- 证据：libkywc/meson.build:48-65
- 细节：shared_library('kywc', files_libkywc, c_args '-fvisibility=default', version: meson.project_version()=1.3.0, install true)；install_headers('libkywc.h')；pkgconfig.generate 描述 'Kylin wayland compositor client library'，url https://gitee.com/openkylin/kylin-wayland-compositor（生成 kywc.pc）；依赖仅 wayland_client + libm

### F-R5-064 — libkywc 链入的协议代码为 5 个 kywc 协议 client 端
- 证据：libkywc/meson.build:18-29
- 细节：protos = kywc-capture-manager-v1、kywc-output-manager-v1、kywc-toplevel-manager-v1、kywc-workspace-manager-v1、kywc-stream-manager-v1，foreach 加入 protocols_code[p] + protocols_client_header[p]；不含 security

### F-R5-065 — libkywc 编译源 12 个 .c（11 入 files_libkywc + libkywc.c；buffer.c 不入共享库）
- 证据：libkywc/meson.build:2-16
- 细节：核心：libkywc.c、output.c、toplevel.c、thumbnail.c、workspace.c、cursor.c、stream.c；providers：kywc_capture.c、kywc_output.c、kywc_toplevel.c、kywc_workspace.c、kywc_stream.c

### F-R5-066 — 另有静态库 libkywc_buffer.a（kywc_buffer），build_by_default false
- 证据：libkywc/meson.build:31-42
- 细节：源 buffer.c/buffer.h；依赖 epoxy + libpng；declare_dependency 名 kywc_buffer；被 portal（portal/meson.build:19）与 examples thumbnail/pipewire（examples/meson.build:47、73）静态链入

### F-R5-067 — 能力位枚举 kywc_context_capability 共 7 位
- 证据：libkywc/libkywc.h:21-30
- 细节：OUTPUT=1<<0、TOPLEVEL=1<<1、WORKSPACE=1<<2、THUMBNAIL=1<<3、THUMBNAIL_EXT=1<<4（multi-plane）、CURSOR=1<<5、STREAM=1<<6

### F-R5-068 — provider 表 7 项，能力位到 wl 接口名静态映射
- 证据：libkywc/provider.h:20-32
- 细节：WORKSPACE→"kywc_workspace_manager_v1"(_kywc_workspace_init)、OUTPUT→"kywc_output_manager_v1"、TOPLEVEL→"kywc_toplevel_manager_v1"、THUMBNAIL/THUMBNAIL_EXT/CURSOR 三项均→"kywc_capture_manager_v1"(_kywc_capture_init)、STREAM→"kywc_stream_manager_v1"

### F-R5-069 — provider 初始化 5 个内部函数
- 证据：libkywc/provider.h:10-18
- 细节：_kywc_workspace_init/_kywc_output_init/_kywc_toplevel_init/_kywc_capture_init/_kywc_stream_init，签名 bool (*)(kywc_context*, enum kywc_context_capability)

### F-R5-070 — context 创建即两次 wl_display_roundtrip，registry 全局事件驱动 provider bind
- 证据：libkywc/libkywc.c:12-24、36-50、52-84
- 细节：registry_handle_global 遍历 ctx->pending_providers 调 provider->bind()，成功后移到 providers 链；kywc_context_init_providers 按 ctx->capabilities 位调 provider->init；THUMBNAIL_EXT 位置位时清掉 THUMBNAIL 位（L55-57）

### F-R5-071 — kywc_context_create 连接命名 display，create_by_display 接入既有 display
- 证据：libkywc/libkywc.c:52-101
- 细节：kywc_context_create(name, capabilities, impl, data) 内 wl_display_connect(name)，失败 fprintf "connect to wayland compositor failed"，成功 own_display=true；context_interface 回调 create/destroy/new_output/new_toplevel/new_workspace（libkywc.h:32-39）

### F-R5-072 — 各 provider bind 版本钳制为 1（capture 扩展除外）
- 证据：libkywc/kywc_output.c:258-262、kywc_toplevel.c:281-285、kywc_workspace.c:147-151、kywc_stream.c:79-85、kywc_capture.c:229-237
- 细节：output/toplevel/workspace/stream：`version_to_bind = version <= 1 ? version : 1`；capture：`(version > 1 && extend) ? version : 1`（extend 对 THUMBNAIL_EXT 能力），strcmp 命中各自 *_manager_v1_interface.name 后 wl_registry_bind

### F-R5-073 — capture provider 消费 frame 与 cursor 两类对象
- 证据：libkywc/kywc_capture.c:98-205
- 细节：frame_listener（failed/cancelled/buffer，L98）调 kywc_capture_frame_v1_release_buffer（L30）；manager 请求 capture_output(L122)/capture_workspace(L136)/capture_toplevel(L150, without_decoration 参数)/capture_cursor(L203)；frame 版本经 kywc_capture_frame_v1_get_version 判定多平面（L64）

### F-R5-074 — stream provider 把协议 created(node) 事件透传为 ready 回调
- 证据：libkywc/kywc_stream.c:33-43、52-74
- 细节：kywc_stream_v1_listener failed/cancelled→ky_stream_destroy，created(uint32 node)→ky_stream_ready(stream, node)；manager 请求 stream_output/stream_toplevel 带 cursor_mode 参数

### F-R5-075 — 私有头 libkywc_p.h 定义 6 组 manager/对象内部结构与 ky_* 内部函数
- 证据：libkywc/libkywc_p.h:10-388
- 细节：_kywc_context 含 display/registry/own_display/capabilities/providers/pending_providers 及 workspace/output/toplevel/thumbnail/cursor/stream 六个 manager 指针；ky_context_add_provider（L40）按能力单例去重（libkywc.c:188-225）

### F-R5-076 — 公开数据模型：workspace/output/toplevel 三个 _kywc_* 快照结构
- 证据：libkywc/libkywc.h:75-80、136-155、199-221
- 细节：_kywc_workspace{uuid,name,position,activated}；_kywc_output 含 uuid/name/make/model/serial/description/physical_size/capabilities/modes 链表/mode/x,y,w,h/transform/scale( float)/enabled,power,primary/brightness/color_temp；_kywc_toplevel 含 uuid/title/app_id/icon/parent/primary_output/workspaces[MAX_WORKSPACES=15]（L197）/几何/activated,minimized,maximized,fullscreen/pid

### F-R5-077 — 三组 state_mask 位掩码
- 证据：libkywc/libkywc.h:82-86（workspace 3 位）、157-167（output 9 位 ENABLED…COLOR_TEMP）、223-236（toplevel 12 位 APP_ID…SIZE）
- 细节：output mask 含 POWER/PRIMARY/BRIGHTNESS/COLOR_TEMP；toplevel mask 含 ICON/POSITION/SIZE

### F-R5-078 — thumbnail 缓冲描述支持 memfd 与 dmabuf（含 4 plane）
- 证据：libkywc/libkywc.h:304-330
- 细节：kywc_thumbnail_buffer{fd, format(DRM fourcc), width,height,offset,stride,modifier,flags,n_planes,planes[4]{fd,offset,stride}}；flags：IS_DMABUF=1<<0、IS_REUSED=1<<1；type 枚举 OUTPUT/TOPLEVEL/WORKSPACE（L292-296）

### F-R5-079 — cursor 与 stream 公开模型
- 证据：libkywc/libkywc.h:389-447
- 细节：kywc_cursor{struct wl_seat *seat; kywc_thumbnail *thumbnail}，回调 position/hotspot/enter/leave/destroy（L394-400）；kywc_stream{type, cursor_mode, source_uuid}，cursor_mode 枚举 HIDDEN/EMBEDDED/METADATA（L424-428），回调 ready(uint32 node)/destroy

## libkywc 公开 API（kywc.syms 导出，67 个，按组）

### F-R5-080 — context 组 9 个
- 证据：libkywc/libkywc.h:44-70
- 细节：kywc_context_create(L44)、kywc_context_create_by_display(L49)、kywc_context_get_display(L52)、kywc_context_set_user_data(L54)、kywc_context_get_user_data(L56)、kywc_context_get_fd(L61)、kywc_context_process(L63)、kywc_context_dispatch(L68)、kywc_context_destroy(L70)

### F-R5-081 — workspace 组 11 个
- 证据：libkywc/libkywc.h:93-118
- 细节：set_interface(93)、context_for_each_workspace(99, 迭代器类型 kywc_workspace_iterator_func_t L97)、context_find_workspace(102)、get_context(104)、create(106)、remove(108)、set_position(110)、set_name(112)、activate(114)、set/get_user_data(116/118)

### F-R5-082 — output 组 6 个
- 证据：libkywc/libkywc.h:174-187
- 细节：set_interface(174)、for_each_output(178)、get_context(181)、find_output(183)、set/get_user_data(185/187)；output capability 枚举 POWER/BRIGHTNESS/COLOR_TEMP（L123-127）；kywc_output_mode{width,height,refresh(mHz),preferred}(L129-134)

### F-R5-083 — toplevel 组 21 个
- 证据：libkywc/libkywc.h:243-287
- 细节：set_interface(243)、for_each_toplevel(248)、get_context(251)、find_toplevel(253)、has_children(255)、set/unset_maximized(257/259, 均带 const char *output)、set/unset_minimized(261/263)、set/unset_fullscreen(265/267)、activate(269)、close(271)、enter/leave_workspace(273/275)、move_to_workspace(277)、move_to_output(279)、set_position(281)、set_size(283)、set/get_user_data(285/287)

### F-R5-084 — thumbnail 组 9 个
- 证据：libkywc/libkywc.h:355-387
- 细节：kywc_thumbnail_create(355, 通用)、create_from_output(359)、create_from_toplevel(363, 带 bool without_decoration)、create_from_workspace(368, 需 output_uuid)、get_context(373)、set/get_user_data(375/377)、release(382, bool wants_buffer)、destroy(387)

### F-R5-085 — cursor 组 5 个
- 证据：libkywc/libkywc.h:402-414
- 细节：kywc_cursor_create(402, 参数含 struct wl_seat*)、create_from_thumbnail(405)、set/get_user_data(410/412)、destroy(414)

### F-R5-086 — stream 组 6 个
- 证据：libkywc/libkywc.h:441-455
- 细节：create_from_output(441)、create_from_toplevel(445)（参数 source_uuid + enum kywc_stream_cursor_mode + impl + data）、get_context(449)、set/get_user_data(451/453)、destroy(455)

### F-R5-087 — kywc.syms 为通配版本脚本，67 个导出由源码非 static 定义决定
- 证据：libkywc/kywc.syms:1-6；libkywc/meson.build:44-53
- 细节：`global: kywc_*; local: *;`，经 -Wl,--version-script 传入；脚本口径：libkywc/*.c 排除 buffer.c 后非 static kywc_* 定义 = 67；buffer.c 的 9 个非 static kywc_buffer_* 只进静态库，不进 libkywc.so 链接单元

### F-R5-088 — kywc_buffer 静态库 9 个对外函数（buffer.h 声明）
- 证据：libkywc/buffer.h:10-42
- 细节：kywc_buffer_helper_create(10)、destroy(12)、helper_import_thumbnail(14-16)、helper_destroy_buffers(18)、write_to_file(20-21, PNG 落盘)、get_pixel(23)、read_pixels(25-26)、buffer_destroy(28)、helper_get_format(41-42)；另含 struct buffer_format{format,len,capacity,modifiers}(30-39)；buffer.c 内 import/export_dmabuf/memfd 4 个为 static（buffer.c:444、538、557、578）

## portal 主体与 xdg-desktop-portal 接口

### F-R5-089 — portal 可执行文件 xdg-desktop-portal-wlcom，装入 libexecdir
- 证据：portal/meson.build:28-35
- 细节：11 个 .c 编译为单个 executable；include wlcom_inc；依赖 wayland_client、libsystemd(sd-bus)、libkywc、util、kywc_buffer、json-c(>=0.13)、libei-1.0、xkbcommon；无 libpipewire 依赖

### F-R5-090 — D-Bus 服务名（程序内常量与总线名获取）
- 证据：portal/main.c:15、62-113
- 细节：service_name="org.freedesktop.impl.portal.desktop.wlcom"；sd_bus_open_user + sd_bus_request_name(flags 默认 SD_BUS_NAME_ALLOW_REPLACEMENT，-r 追加 REPLACE_EXISTING)；订阅 NameOwnerChanged match；bus fd 挂入自研 event_loop

### F-R5-091 — 命令行 5 选项
- 证据：portal/main.c:17-31、128-156
- 细节：-h/--help、-d/--debug(KYWC_DEBUG)、-v/--version(打印 KYWC_VERSION)、-r/--replace、-V/--verbose(KYWC_INFO)；默认日志级 KYWC_WARN，logger_init(level, NULL, true) 实时 stdout

### F-R5-092 — 初始化顺序：dbus→wayland→remote_desktop→input_capture→access→screenshot→screencast
- 证据：portal/main.c:177-210；shutdown 逆序（main.c:223-228）
- 细节：任一失败 goto shutdown；主循环 event_loop_dispatch(…, 1000)（L216）

### F-R5-093 — portal 复用 libkywc 4 项能力
- 证据：portal/wayland.c:143-146
- 细节：capabilities = KYWC_CONTEXT_CAPABILITY_OUTPUT | THUMBNAIL_EXT | TOPLEVEL | STREAM；kywc_context_create_by_display；context_impl 监听 new_output/new_toplevel（L114-119）；output 状态变化联动 input_capture ZonesChanged、screenshot/stream 的 changed 信号（wayland.c:16-31）

### F-R5-094 — org.freedesktop.impl.portal.RemoteDesktop，version=2，AvailableDeviceTypes=3
- 证据：portal/remote_desktop.c:20-21、1106-1146
- 细节：vtable：property AvailableDeviceTypes(u, CONST)、version(u)=2；方法 13 个：CreateSession(oosa{sv})→ua{sv}、SelectDevices、Start(oossa{sv})、NotifyPointerMotion/MotionAbsolute/Button/Axis/AxisDiscrete、NotifyKeyboardKeycode/Keysym、NotifyTouchDown/Motion/Up、ConnectToEIS(osa{sv})→h；除 Start 外几乎全标 SD_BUS_VTABLE_UNPRIVILEGED；devices=3 注释 keyboard and pointer

### F-R5-095 — org.freedesktop.impl.portal.InputCapture，version=1，SupportedCapabilities=3
- 证据：portal/input_capture.c:18-19、843-868
- 细节：方法 7：CreateSession、GetZones、SetPointerBarriers(…aa{sv}u)、Enable、Disable、Release、ConnectToEIS→h；信号 4：Disabled、Activated、Deactivated、ZonesChanged（签名 oa{sv}）；capabilities=3 注释 keyboard and pointer；对象路径 /org/freedesktop/portal/desktop

### F-R5-096 — org.freedesktop.impl.portal.ScreenCast，version=5
- 证据：portal/screencast.c:12-13、451-471
- 细节：property AvailableSourceTypes = SOURCE_TYPE_MONITOR|WINDOW = 1|2 = 3；AvailableCursorModes = HIDDEN|EMBEDDED = 1|2 = 3；version=5；方法 CreateSession/SelectSources/Start；默认 source MONITOR、默认 cursor Hidden（screencast.c:217-219）

### F-R5-097 — org.freedesktop.impl.portal.Screenshot，version=2
- 证据：portal/screenshot.c:16-17、559-569
- 细节：方法 Screenshot(ossa{sv})→ua{sv}、PickColor(ossa{sv})→ua{sv}（UNPRIVILEGED）；property version=2

### F-R5-098 — org.freedesktop.impl.portal.Access 仅 1 方法且无 version 属性
- 证据：portal/access.c:13、234-244
- 细节：vtable 仅 SD_BUS_METHOD("AccessDialog", "osssssa{sv}", "ua{sv}", handle_access_dialog, UNPRIVILEGED)；无 version property、无 init 状态字段（portal_access_fini 为空，access.c:252-254）

### F-R5-099 — org.freedesktop.impl.portal.Session / Request 子对象
- 证据：portal/session.c:14、41、53-56、133；portal/request.c:10、36、48
- 细节：两者均实现方法 Close("")、UNPRIVILEGED；session 关闭时发 org.freedesktop.impl.portal.Session Closed 信号（session.c:133）；portal_session_type 枚举 REMOTE_DESKTOP=0/INPUT_CAPTURE/SCREENCAST（portal.h:24-28）；响应码 SUCCESS=0/CANCELLED=1/ENDED=2（portal.h:18-22）

### F-R5-100 — portal_session 联合体区分三类会话
- 证据：portal/portal.h:94-137
- 细节：input_capture 子结构含 input_capture_path、barriers(wl_array)、zone_set；remote_desktop 子结构含 select_devices、persist_mode、restore_data、ei_sender、clipboard_enabled、screen_share_enabled、streams 链、screencast_selection、stream_counts；screencast 子结构含 persist_mode/restore_data/streams/select/stream_counts

### F-R5-101 — EI（libei）输入注入：ei_sender
- 证据：portal/ei_sender.h:8、24-56；portal/ei_sender.c:260-294
- 细节：struct ei_sender{eis_fd, struct ei*, ei_seat*, pointer, abs_pointer, keyboard, sequence_num, xkb_keyboard, event_loop}；ei_new_sender(NULL) + ei_setup_backend_fd(ei, eis_fd)（ei_sender.c:284、290）；seat 绑定 EI_DEVICE_CAP_POINTER|EI_DEVICE_CAP_KEYBOARD（ei_sender.c:162）；导出 pointer_motion/motion_absolute/button/axis/axis_discrete/keycode/keysym

### F-R5-102 — EIS fd 由 portal 向合成器 D-Bus 调用取得
- 证据：portal/remote_desktop.c:1088-1089；portal/input_capture.c:21-22、156
- 细节：RemoteDesktop 调总线名 "com.kylin.Wlcom"、路径 "/com/kylin/Wlcom/EIS/RemoteDesktop"、接口 "com.kylin.Wlcom.EIS.RemoteDesktop"、方法 ConnectToEIS；InputCapture 对应 "com.kylin.Wlcom.EIS.InputCapture"（路径 /com/kylin/Wlcom/EIS/InputCapture）；返回 h 类型 fd 原样回给 xdg-desktop-portal 前端（remote_desktop.c:1095-1101）

### F-R5-103 — xkb 键映射在 portal 进程内
- 证据：portal/ei_sender.h:12-16；portal/meson.build:20（xkbcommon 依赖）
- 细节：struct xkb_keyboard{context, keymap, state}；NotifyKeyboardKeycode/Keysym 经此转换后由 ei 发送

## PipeWire 串流

### F-R5-104 — portal 不链接 libpipewire；PipeWire node id 经 kywc-stream 协议透传
- 证据：portal/meson.build:17-21（无 pipewire）；portal/stream.c:181-215、1006
- 细节：handle_stream_ready(kywc_stream*, uint32_t node) 把 node 存入 portal_stream->node；Start 回复以 sd_bus_message_append(reply, "u", stream->node) 输出 PipeWire 节点号（stream.c:1006）；node 由合成器侧 src/effect/ky_stream.c 经 kywc_stream_v1 created 事件给出

### F-R5-105 — portal stream 源类型/光标模式枚举
- 证据：portal/stream.h:10-20
- 细节：SOURCE_TYPE_MONITOR=1、WINDOW=2、VIRTUAL=4；CURSOR_MODE_HIDDEN=1、EMBEDDED=2、METADATA=4；映射到 libkywc：EMBEDDED→KYWC_STREAM_CURSOR_MODE_EMBEDDED，其余→HIDDEN（stream.c:310-311、screencast.c:370-371；METADATA 未映射）

### F-R5-106 — portal 按 source type 调 kywc_stream_create_from_output/toplevel
- 证据：portal/stream.c:323-352
- 细节：同一函数内两个 output 分支（L323、327）与两个 toplevel 分支（L348、352），分别对应 remote_desktop/screencast 会话路径

### F-R5-107 — portal 选择 UI 经独立进程 wldialog（unix socket + JSON）
- 证据：portal/stream.c:922、screenshot.c:495、access.c:196、input_capture.c:328、remote_desktop.c:623
- 细节：spawn_dialog("wldialog")（声明于 src/util/spawn.c:120）返回 socket_fd，dialog_send_request/dialog_get_reply 用 json-c；remote_desktop 在 SelectDevices 还通过 org.freedesktop.Notifications.Notify 发通知（remote_desktop.c:604-605）

### F-R5-108 — Screenshot 用 libkywc thumbnail + kywc_buffer 写临时 PNG
- 证据：portal/screenshot.c:37-71、331-357、516
- 细节：thumbnail_handle_buffer → mkstemps(path,4) → kywc_buffer_helper_import_thumbnail → kywc_buffer_write_to_file(…, path)；源区分 toplevel（create_from_toplevel，L353）与 output（create_from_output，L357）

## portal data 单元与启动方式

### F-R5-109 — wlcom.portal 声明 5 个接口、UseIn=UKUI
- 证据：portal/data/wlcom.portal:1-4
- 细节：DBusName=org.freedesktop.impl.portal.desktop.wlcom；Interfaces=RemoteDesktop;InputCapture;ScreenCast;Screenshot;Access（org.freedesktop.impl.portal 前缀）；meson 装到 /usr/share/xdg-desktop-portal/portals（portal/meson.build:47-50）

### F-R5-110 — ukui-portals.conf 将 5 接口首选指向 wlcom
- 证据：portal/data/ukui-portals.conf:1-7
- 细节：[preferred] default=ukui；RemoteDesktop/InputCapture/ScreenCast/Screenshot/Access 各 =wlcom；装到 /usr/share/xdg-desktop-portal（meson.build:52-54）

### F-R5-111 — systemd user 单元
- 证据：portal/data/xdg-desktop-portal-wlcom.service:1-11；meson.build:37-40（装 /usr/lib/systemd/user）
- 细节：Description "Xdg Desktop Portal For UKUI"；PartOf/After graphical-session.target；ConditionEnvironment=WAYLAND_DISPLAY；Type=dbus，BusName=org.freedesktop.impl.portal.desktop.wlcom；ExecStart=/usr/libexec/xdg-desktop-portal-wlcom；Restart=on-failure

### F-R5-112 — D-Bus service activation 文件
- 证据：portal/data/org.freedesktop.impl.portal.desktop.wlcom.service:1-4；meson.build:42-45（装 /usr/share/dbus-1/services）
- 细节：Name=org.freedesktop.impl.portal.desktop.wlcom；Exec=/usr/bin/xdg-desktop-portal-wlcom；SystemdService=xdg-desktop-portal-wlcom.service

### F-R5-113 — portal i18n 域 xdg-desktop-portal-wlcom
- 证据：portal/main.c:120-122；portal/po/xdg-desktop-portal-wlcom.pot；portal/po/POTFILES.in:1-6
- 细节：HAVE_NLS 时 nls_setup_message("xdg-desktop-portal-wlcom", locales, ARRAY_SIZE(locales))；POTFILES 仅 6 文件：access/input_capture/remote_desktop/screenshot/screencast/stream.c

## wlu 示例库

### F-R5-114 — libwlu 静态库：5 源 + 3 协议
- 证据：examples/lib/meson.build:1-18
- 细节：src/buffer.c、display.c、input.c、window.c、wlu.c；协议 xdg-shell、xdg-decoration、linux-dmabuf-v1（取 protocols_code/client_header）；依赖 wayland-client、pixman-1、libdrm、gbm、egl、glesv2

### F-R5-115 — wlu display 组 API
- 证据：examples/lib/include/wlu.h:22-50
- 细节：wlu_display_create(callbacks, flags)（flag WLU_DISPLAY_CREATE_EGL=1）、destroy、supports_egl、get_wl_display、get_wl_compositor、get_xdg_wm_base、run、exit；回调 registry_global/registry_global_remove（L27-32）

### F-R5-116 — wlu window 组 API 与创建标志
- 证据：examples/lib/include/wlu.h:52-129
- 细节：wlu_window_create_info{display,callbacks,app_id,width,height,format,title,flags}；flags RESIZABLE/TRANSPARENT/DECORATION/GL/GLES（L56-63）；回调 create/destroy/resize/keyboard/pointer_motion/pointer_button；get_wl_surface/xdg_surface/xdg_toplevel、maximized/minimized 控制、request_draw/damage；WLU_SWAPCHAIN_COUNT=2

### F-R5-117 — wlu buffer/draw 组 API
- 证据：examples/lib/include/wlu.h:131-199
- 细节：buffer 类型 SHM/DMABUF_GL（VK 注释）；wlu_buffer_create/destroy/get_width/get_type/get_shm_data/get_gl_fbo/get_gl_texture；import_shmbuf/import_shmbuf_gl/import_dmabuf；WLU_MAX_DMABUF_PLANES=4；draw：wlu_draw_init/wlu_draw_texture(options{texture,target,src,dst})/wlu_draw_fini

## 独立示例程序（examples/ 根目录 9 个 .c）

### F-R5-118 — output-doctor（output_doctor.c，1039+ 行）
- 证据：examples/meson.build:7-16；examples/output_doctor.c:1021-1037、12-16
- 细节：门控 have_kde_output；链接 5 协议生成码（kde-output-management-v2、kde-output-device-v2、kde-primary-output-v1、org-kde-kwin-dpms-manager、xdg-output-unstable-v1）；CLI：--monitor/--output/--on/--off/--dpms/--mode WxH@refresh/--primary/--preferred/--pos/--transform/--scale/--overscan/--vrr-policy/--rgb-range；调 kde_output_configuration_v2_*（enable/mode/transform/position/scale/overscan/set_vrr_policy/set_rgb_range/set_primary_output/apply，output_doctor.c:241-298）

### F-R5-119 — virtual-desktop（virtual_desktop.c）
- 证据：examples/meson.build:18-25；examples/virtual_desktop.c:161-166、271、288
- 细节：门控 have_kde_virtual_desktop；协议 org-kde-plasma-virtual-desktop-management；usage "virtual-desktop [option]"（L205）；request_create_virtual_desktop / request_remove_virtual_desktop / get_virtual_desktop；management_listener（L147）

### F-R5-120 — monitor（monitor.c）
- 证据：examples/meson.build:27-32；examples/monitor.c:120-131
- 细节：仅依赖 libkywc；caps = WORKSPACE|OUTPUT|TOPLEVEL；printf 打印 output/toplevel/workspace 状态，toplevel 行含 kywc_toplevel_has_children（monitor.c:89）；kywc_context_dispatch 阻塞

### F-R5-121 — ukui-effect-test（ukui-effect-test.c）
- 证据：examples/meson.build:34-42；examples/ukui-effect-test.c:20-23、268、305、497
- 细节：门控 have_ukui_effect；协议 ukui-effect-v1 + xdg-shell + xdg-decoration；依赖 librt；自建 shm 窗口（sys/mman）；调用 create_fade_effect(L268)、create_slide_effect(L305)、create_animation_curve(L497/536)；监听 builtin_animation_curves/done（L157-180）

### F-R5-122 — thumbnail（thumbnail.c）
- 证据：examples/meson.build:44-49；examples/thumbnail.c:184-228
- 细节：依赖 libkywc + kywc_buffer + libwlu；参数 `<output|toplevel|workspace> <id> [output_id]`（workspace 需第 4 参）；caps=THUMBNAIL_EXT；wlu_display_create(…, WLU_DISPLAY_CREATE_EGL) 提供 EGL 显示后 kywc_context_create_by_display

### F-R5-123 — kde_keystate（kde_keystate.c）
- 证据：examples/meson.build:51-58；examples/kde_keystate.c:12-73
- 细节：门控 have_kde_keystate；绑定 org_kde_kwin_keystate（取 registry version）；org_kde_kwin_keystate_fetchStates() + stateChanged 监听（L18、64-65）

### F-R5-124 — alpha_modifier（alpha_modifier.c）
- 证据：examples/meson.build:60-68；examples/alpha_modifier.c:11-13、59-68、95
- 细节：门控 have_alpha_modifier；依赖 libwlu + cairo；绑定 wp_alpha_modifier_v1，wp_alpha_modifier_v1_get_surface 后 wp_alpha_modifier_surface_v1_set_multiplier(surface, factor*UINT32_MAX)（L95）

### F-R5-125 — pipewire（pipewire.c）
- 证据：examples/meson.build:70-75；examples/pipewire.c:9-13、382-443
- 细节：依赖 libkywc + kywc_buffer + libpipewire-0.3；参数 `<output|toplevel> <uuid> [avoid_dmabufs 0|1]`（L387-406）；pw_init/pw_main_loop_new，pw_stream_new_simple(…,"video-play",…)（L332）；caps=KYWC_CONTEXT_CAPABILITY_STREAM，ready 后把 kywc fd 用 pw_loop_add_io 并入 PipeWire loop；创建 stream 时 cursor_mode=HIDDEN

### F-R5-126 — simple_plugin（simple_plugin.c）为共享模块而非可执行程序
- 证据：examples/meson.build:95-103；examples/simple_plugin.c:12-19、171-177
- 细节：shared_module('simple', name_prefix:'', install_dir: plugindir, install:false)；导出 struct kywc_plugin_data simple_plugin_data{info,options,setup,option,teardown}；info：name "simple"、class "example"、PLUGIN_VERSION_NUMERIC(1,0,0)、ABI_VERSION(1,0)；注册 6 个 key_binding（Alt+t 等）与 7 个 gesture_binding（pinch/swipe 串，simple_plugin.c:33-54）；调 kywc_key_binding_create/register、kywc_gesture_binding_create_by_string/register、kywc_plugin_get_option_*

## gui QML 客户端结构

### F-R5-127 — gui 目录 6 个 Qt 可执行目标，缺 C++/Qt5 时整个 subdir 跳过
- 证据：examples/gui/meson.build:1-22
- 细节：add_languages('cpp', required:false) + qt5 dependency(required:false)（Core/Gui/Widgets/Qml/Quick/QuickWidgets，另取 Gui private_headers）；不满足 subdir_done()

### F-R5-128 — kywc-gui（安装）：QMainWindow 三标签表
- 证据：examples/gui/meson.build:38-48；examples/gui/main.cpp:8-15；examples/gui/widget.h:18-89
- 细节：源 main.cpp/context.cpp/ui.cpp/workspace.cpp/output.cpp/toplevel.cpp/thumbnail.cpp/ThumbnailItem.cpp/ThumInfo.cpp + qml.qrc；依赖 qt5 + libkywc + egl + glesv2 + libdrm；MainWindow 含 3 个 QTableWidget（workspace/output/toplevel）与全套 toplevel 操作槽（max/min/fullscreen/activate/close/position/size/enter-leave workspace/send to output/缩略图）

### F-R5-129 — Context C++ 类封装 kywc_context，QSocketNotifier 集成 Qt 事件循环
- 证据：examples/gui/context.cpp:75-138
- 细节：setup(capabilities) 内 kywc_context_create(NULL,…)，或对既有 display 用 create_by_display（L78-80）；QSocketNotifier(kywc_context_get_fd(ctx), Read)（L115）；提供 find_workspace/find_output/find_toplevel（L156-172）

### F-R5-130 — children 目标（不安装）
- 证据：examples/gui/meson.build:50-61；examples/gui/children.cpp
- 细节：单文件 children.cpp（moc_sources），仅依赖 qt5；对应 libkywc 的 kywc_toplevel_has_children/parent 关系演示面

### F-R5-131 — thumbnail 目标（安装）：QML + QQuickWidget 缩略图查看器
- 证据：examples/gui/meson.build:63-78；examples/gui/ThumMain.cpp:16-60；examples/gui/main.qml:1-16；qml.qrc:1-7
- 细节：qmlRegisterType<ThumbnailItem>("MyComponents",1,0,"ThumbnailItem")；setContextProperty("dataInfo", &thum)；main.qml 仅 Rectangle 内填满 ThumbnailItem{thumInfo: dataInfo}；qml.qrc 只内嵌 main.qml；复用 context/workspace/output/toplevel/thumbnail/ThumbnailItem/ThumInfo

### F-R5-132 — ukui-blur 目标（不安装）
- 证据：examples/gui/meson.build:80-94；examples/gui/ukui_blur.cpp:192-194
- 细节：链 protocols_code['ukui-blur']（meson 键 ukui-blur → ukui-blur-v1.xml）；QPlatformNativeInterface 取 wl 原生资源

### F-R5-133 — security 目标（不安装）：kywc-security 协议客户端
- 证据：examples/gui/meson.build:96-110；examples/gui/security.cpp:148-156、243-245
- 细节：链 protocols_code['kywc-security-manager-v1']；QScreen 列表 + screenAdded/screenRemoved；QGuiApplication::platformNativeInterface()->nativeResourceForScreen/Window（security.cpp:29、56）

### F-R5-134 — ukui-background 目标（不安装，门控 have_ukui_background）
- 证据：examples/gui/meson.build:112-135；examples/gui/ukui_background.cpp:988-990
- 细节：链 ukui-background-v1 + linux-dmabuf-v1 两组生成码；依赖 wayland_client/libdrm/gbm（gbm 缺失时 declare_dependency 占位，L113-116）

### F-R5-135 — gui 缩略图走 EGLImage/GL 纹理路径
- 证据：examples/gui/ThumbnailItem.cpp:13、143、175
- 细节：include QGuiApplication；nativeResourceForWindow + nativeResourceForIntegration("egldisplay")；qt5dep_priv 取 Gui 私有头（meson.build:13-18）

## i18n 体系与语言数

### F-R5-136 — 主翻译域 kylin-wayland-compositor：27 .po
- 证据：po/kylin-wayland-compositor.pot；po/*.po
- 细节：27 语言文件：ar、bo_CN、de_DE、es_ES、fr_FR、id、it、ja、khb_CN、kk、ko_KP、ky、lo、mn、ms、my、pt、ru、th、tr、ug、ur、vi、zh_CN、zh_HK、zh_Hant、zh_TW

### F-R5-137 — 实际编译嵌入仅 LINGUAS 的 16 语言
- 证据：po/LINGUAS:1-16；po/meson.build:3-30
- 细节：zh_CN/zh_TW/zh_HK/zh_Hant/bo_CN/ug/kk/ky/mn/ms/de_DE/es_ES/fr_FR/th/vi/ar；脚本逐行 fs.read().strip().split('\n')

### F-R5-138 — 11 个 .po 不在 LINGUAS
- 证据：po/*.po 与 po/LINGUAS 集合差（脚本）
- 细节：id、it、ja、khb_CN、ko_KP、lo、my、pt、ru、tr、ur 有 .po 但不参与 mo 嵌入/locales 表

### F-R5-139 — 主 POTFILES.in 仅 4 个源文件
- 证据：po/POTFILES.in:1-4
- 细节：src/view/action.c、src/view/ssd.c、src/view/window_menu.c、src/view/killer.c；meson 未引用 POTFILES.in（Grep 仅 po/meson.build 的 msgfmt/embed 命中），更新 pot 靠外部 gettext 工具链

### F-R5-140 — portal 翻译域：19 .po，LINGUAS 仅 zh_CN
- 证据：portal/po/*.po（19）；portal/po/LINGUAS:1
- 细节：19 个：ar、de、es、fr、id、it、ja、khb_CN、ko_KP、lo、ms、my、pt、ru、th、tr、ur、vi、zh_CN；语言码与主域不同（de 对 de_DE、es 对 es_ES、fr 对 fr_FR）；仅 zh_CN 被嵌入

### F-R5-141 — locales.h.in 模板两域同构
- 证据：po/locales.h.in:1-8；portal/po/locales.h.in（同内容）
- 细节：包含 util/nls.h 与 @LOCALES@ 占位；生成结构 `static const struct locale locales[]`（struct locale 定义于 include/util/nls.h，消费方 portal/main.c:121 nls_setup_message(domain, locales, ARRAY_SIZE(locales))）

## 补充事实（构建门控与包边界）

### F-R5-142 — meson 选项汇总中协议特性开关 30+ 项
- 证据：meson.build:261-302
- 细节：summary Configuration 段列出 xwayland、kde_output、kde_virtual_desktop、wlr_output、wlr_foreign_toplevel、wlr_layer_shell、kde_global_accel、kde_input、kde_plasma_shell、kde_plasma_window_management、kde_blur、kde_slide、ukui_screenshot、ukui_gsettings、ukui_theme、kde_keystate、kde_clipboard、ukui_watermark、ukui_shell、ukui_window_management、ukui_output、ukui_blur、ukui_effect、ukui_startup、ukui_view_mode、ukui_output_config、ukui_background、xdg_toplevel_icon、xdg_toplevel_tag、libkywc、examples、tools、nls

### F-R5-143 — debian 分包覆盖 client/examples/tools/portal
- 证据：debian/kylin-wayland-compositor-client.install、kylin-wayland-compositor-examples.install、kylin-wayland-compositor-tools.install、xdg-desktop-portal-wlcom.install、kylin-wayland-compositor.install
- 细节：5 个 .install 文件；portal 独立包名 xdg-desktop-portal-wlcom

### F-R5-144 — tools/wlcctrl 是 virtual keyboard/pointer 的纯客户端
- 证据：tools/wlcctrl/wlcctrl.c:20-26
- 细节：registry 中按名匹配 zwp_virtual_keyboard_manager_v1_interface.name / zwlr_virtual_pointer_manager_v1_interface.name 并 bind；解释 protocols/meson.build 中两协议键挂在 have_tools 下（L154-159）

## 疑点与矛盾

### F-R5-145 — 【双源差异】PROTOCOLS.md kywc 表缺 kywc_stream_manager_v1
- 证据：docs/PROTOCOLS.md:172-180（5 行）对比 protocols/kywc-stream-v1.xml、src/effect/ky_stream.c:213、libkywc/provider.h:31、portal/wayland.c:144
- 细节：文档 kywc 分节 5 行（capture/output/security/toplevel/workspace），stream 协议在 XML/meson（键 kywc-stream-manager-v1）/服务端全局/客户端库/portal 全链路存在；同节也未提 kywc_security_configuration_v1（见 F-R5-149）

### F-R5-146 — 【文档重复】xwayland_shell_v1 在 staging 表出现两行
- 证据：docs/PROTOCOLS.md:47、docs/PROTOCOLS.md:52
- 细节：两处均记 version 1；meson 中 xwayland-shell-v1 键仅一次（protocols/meson.build:168-172），src 注册点 xwayland/shell.c:163 与 wlr 助手 xwayland.c:88

### F-R5-147 — 【XML 异常】kywc-stream-v1.xml 的 protocol name 属性误写
- 证据：protocols/kywc-stream-v1.xml:2
- 细节：`<protocol name="kywc_capture_v1">`，与 protocols/kywc-capture-v1.xml:2 的 protocol name 完全相同；接口名本身正确（kywc_stream_manager_v1/kywc_stream_v1），wayland-scanner 输出按 @BASENAME@ 命名故无文件冲突；性质判据为两文件同名字段，意图层面疑为复制粘贴遗漏（无作者注释可引）

### F-R5-148 — 【meson 键重复】linux-dmabuf-v1 在字典中出现两次
- 证据：protocols/meson.build:24（基础 dict）与 protocols/meson.build:163（have_ukui_background 块 `protocols += { 'linux-dmabuf-v1': … }`）
- 细节：两处值同为 wl_protocol_dir/'stable/linux-dmabuf/linux-dmabuf-v1.xml'；Meson 对 dict 重复键合并的行为依版本而定，若 have_ukui_background=true 触发 += 合并存在报错风险（本次为静态阅读，未配置构建验证）

### F-R5-149 — 【清单边界】src/plugin/security/security.xml 在 protocols/ 34 个之外
- 证据：src/plugin/security/security.xml:1-55；src/plugin/security/security.c:466
- 细节：第 35 个自研协议 kywc_security_configuration_v1（v1，protector_mode fill_none/color/image）；其代码生成在 src/plugin/security/meson.build 自定义，未进 protocols/meson.build 总表；PROTOCOLS.md 亦无记录；许可头 MulanPSL-2.0 与全仓 GPL-1.0-or-later 主流头不同（security.xml:3-6）

### F-R5-150 — 【打包路径不一致】portal 激活路径三处不一
- 证据：portal/data/xdg-desktop-portal-wlcom.service:10（ExecStart=/usr/libexec/xdg-desktop-portal-wlcom）；portal/data/org.freedesktop.impl.portal.desktop.wlcom.service:3（Exec=/usr/bin/xdg-desktop-portal-wlcom）；portal/meson.build:33（install_dir: get_option('libexecdir')）
- 细节：meson 实际安装到 ${libexecdir}（Debian 系通常 /usr/libexec），D-Bus service 激活写 /usr/bin；systemd 单元写 /usr/libexec；D-Bus 激活与 systemd 激活二选一时可执行路径解析结果不同

### F-R5-151 — 【接口对账】Access vtable 无 version 属性
- 证据：portal/access.c:234-239；对比 remote_desktop.c:1111、input_capture.c:846、screencast.c:457、screenshot.c:559
- 细节：xdg-desktop-portal impl 接口约定的 version(u) 属性在其余 4 接口均存在，Access 缺失；wlcom.portal Interfaces= 行与代码实现接口集合对账一致（RemoteDesktop/InputCapture/ScreenCast/Screenshot/Access 五个，portal.h init 函数齐全），无多无少

### F-R5-152 — 【i18n 口径】.po 数与 LINGUAS 数显著不等（两域皆然）
- 证据：主域 27 .po vs LINGUAS 16（po/LINGUAS）；portal 域 19 .po vs LINGUAS 1（portal/po/LINGUAS:1）
- 细节：主域 11 个 .po 不编译；portal 域除 zh_CN 外 18 个 .po 不编译；且两域语言码命名不一致（de_DE vs de 等）；POTFILES 覆盖极小（主域 4 文件、portal 6 文件），主合成器大量用户可见字符串不在 POTFILES

### F-R5-153 — 【文档族属】PROTOCOLS.md 把 zwp_text_input_manager_v2、zwp_virtual_keyboard_manager_v1 放入 external 节
- 证据：docs/PROTOCOLS.md:146-156
- 细节：二者 XML 实际随仓 vendored（protocols/text-input-unstable-v2.xml、protocols/virtual-keyboard-unstable-v1.xml），族属按来源应是 wayland unstable；文档 external 节同时混入 wayland-protocols 不稳定协议与 weston 外部协议，分类口径混杂（事实层仅记录分节位置，不评价动机）

### F-R5-154 — 【文档备注列】kde blur/plasma-shell 行备注 "ukui"
- 证据：docs/PROTOCOLS.md:106（org_kde_kwin_blur_manager，备注 ukui）、docs/PROTOCOLS.md:121（org_kde_plasma_shell，备注 ukui）
- 细节：仓内同时存在 kde 版 blur（protocols/blur.xml，src/view/kde_blur.c）与 ukui 版 blur（protocols/ukui-blur-v1.xml，src/view/ukui_blur.c）两套协议；文档以备注列标注消费方，未给出进一步说明文本

### F-R5-155 — 【文档 no 标记口径】staging/unstable 表“支持情况=no”但仍保留版本说明列数字
- 证据：docs/PROTOCOLS.md:34、39、59、61、65、82
- 细节：wp_content_type_manager_v1(no,说明1)、ext_session_lock_manager_v1(no,1)、zwp_fullscreen_shell_v1(no,1)、zwp_input_method_context_v1(no,1)、zwp_linux_explicit_synchronization_v1(no,deprecated)、zwp_xwayland_keyboard_grab_manager_v1(no,1)；“说明”列对 no 行仍填序号 1，表头未定义该列语义

### F-R5-156 — 【portal 枚举】METADATA 光标模式声明但未映射
- 证据：portal/stream.h:16-20；portal/stream.c:310-311；portal/screencast.c:370-371
- 细节：CURSOR_MODE_METADATA=4 在枚举中存在，ScreenCast AvailableCursorModes 仅上报 HIDDEN|EMBEDDED=3；映射函数只处理 EMBEDDED→EMBEDDED、其余一律 HIDDEN；libkywc 协议端 enum 含 hidden/embedded/metadata（protocols/kywc-stream-v1.xml pointer enum）
