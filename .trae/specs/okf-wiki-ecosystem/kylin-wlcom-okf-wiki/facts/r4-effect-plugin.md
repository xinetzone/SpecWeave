# R4 特效/插件/安全簇 — 源码事实采集

## 一、采集范围与计数总览

### F-R4-001 — 采集对象为固定提交上的只读源码树
- 证据：仓库根（git rev-parse HEAD 输出）
- 细节：仓库路径 `external/dao/action/kylin-wayland-compositor`（下文证据路径均相对该根）；HEAD = `4df656222427f3cd0101e41d828fb64805e66c15`；采集覆盖 src/effect（40 个 .c + shaders/）、src/plugin（含 security/）、src/security、include/kywc、include/effect、include/security、protocols/ 及相关 meson.build。
- 备注：本次采集未对仓库做任何写操作；仅本事实文件为落盘产出物。

### F-R4-002 — src/effect 目录下共有 40 个 C 源文件
- 证据：计数命令 `(Get-ChildItem src\effect\*.c).Count` 输出 `40`（pwsh7，仓库根执行）
- 细节：无条件编译 36 个（meson 两段 files()），条件编译 4 个（screenshot.c / watermark.c / slide.c / ukui_effect.c）。

### F-R4-003 — shader 源文件共 14 个（7 对 vert/frag）
- 证据：计数命令 `(Get-ChildItem src\effect\shaders\*.vert,src\effect\shaders\*.frag).Count` 输出 `14`；src/effect/shaders/meson.build:1-16
- 细节：blur_down/blur_up/blur_up_last/circle_progressbar/magic_lamp/shape_color/tap_ripple 各一对 .vert+.frag。

### F-R4-004 — 内置安全子系统与插件目录文件计数
- 证据：`(Get-ChildItem src\security\*.c).Count` 输出 `5`；`(Get-ChildItem src\plugin\ -Recurse -File).Count` 输出 `9`
- 细节：src/security 5 个 .c（global_filter.c/ky_security.c/protector.c/security.c/security_context.c）+ security_p.h；src/plugin 9 文件 = config.c/interface.c/plugin.c/plugin_p.h/meson.build + security/{security.c,gui.cpp,security.xml,meson.build}。

### F-R4-005 — 40 个特效 .c 全部静态编入主程序 wlcom，无任何内置特效以 .so 插件形式安装
- 证据：src/effect/meson.build:1-65（所有片段均为 `wlcom_sources += files(...)`）；src/plugin/security/meson.build:86-95（全树唯一 shared_module 为 security 插件）
- 细节：effect 目录无任何 shared_module()/install_dir 指向 plugindir 的构建片段。

## 二、构建边界（meson）

### F-R4-006 — 34 个 effect .c 无条件加入 wlcom_sources
- 证据：src/effect/meson.build:1-36
- 细节：action/animator/blur/blurrer/capture/circle_progressbar/color_filter/color_picker/config/effect/fade/locate_pointer/magic_lamp/mouse_click/mouse_trail/move/output_transform/showfps/showkey/scale/shake_cursor/shake_view/snapshot/stream/tap_ripple/touch_click/touch_long/touch_trail/trail/translation/transform/wallpaper/wlr_screencopy/zoom。

### F-R4-007 — ky_capture.c 与 ky_stream.c 为第二段无条件编译块
- 证据：src/effect/meson.build:38-41
- 细节：`wlcom_sources += files('ky_capture.c','ky_stream.c')`，无条件开关。

### F-R4-008 — screenshot.c 仅在 have_ukui_screenshot 为真时编译
- 证据：src/effect/meson.build:43-47
- 细节：`if have_ukui_screenshot` 包裹 files('screenshot.c')。

### F-R4-009 — watermark.c 仅在 have_ukui_watermark 为真时编译
- 证据：src/effect/meson.build:49-53
- 细节：注意 wallpaper.c 在无条件块（:33），watermark.c 在条件块，两者文件名不同。

### F-R4-010 — slide.c 仅在 have_kde_slide 为真时编译
- 证据：src/effect/meson.build:55-59

### F-R4-011 — ukui_effect.c 仅在 have_ukui_effect 为真时编译
- 证据：src/effect/meson.build:61-65

### F-R4-012 — 14 个 shader 经 embed 程序在构建期生成同名下划线化 .h 头并编入 wlcom_sources
- 证据：src/effect/shaders/meson.build:18-29
- 细节：`output = name.underscorify() + '.h'`；custom_target command=[embed, var]，feed:true、capture:true；:67 `subdir('shaders')`。

### F-R4-013 — src/plugin 三 .c 编入主程序并下钻 security 子目录
- 证据：src/plugin/meson.build:1-7
- 细节：config.c/interface.c/plugin.c 进 wlcom_sources，随后 subdir('security')。

### F-R4-014 — security 插件构建依赖 C++ 与 Qt5，缺失即 subdir_done 跳过
- 证据：src/plugin/security/meson.build（required:false 检测 cpp 与 qt5 Core/Gui/Widgets 及 Gui private_headers，缺任一依赖则 subdir_done）
- 细节：该跳过只影响 src/plugin/security 下的 security 插件与 gui 可执行文件，不影响 src/security 内置子系统。

### F-R4-015 — security.xml 经 wayland_scanner 生成三类代码
- 证据：src/plugin/security/meson.build:5-24
- 细节：private-code/server-header/client-header 三种生成产物。

### F-R4-016 — security 插件为全树唯一 shared_module，且与 gui 程序均不安装
- 证据：src/plugin/security/meson.build:57-64（gui executable install:false）、:86-95（`shared_module('security', ..., name_prefix:'', install_dir: plugindir, install:false)`，链接 util_static）
- 细节：name_prefix:'' 使产物名为 security.so 而非 libsecurity.so。

### F-R4-017 — src/security 5 个 .c 无条件编入主程序
- 证据：src/security/meson.build:1-6
- 细节：global_filter/ky_security/protector/security/security_context 进 wlcom_sources。

### F-R4-018 — 插件目录由构建选项 plugin_directory 决定并经 -DPLUGIN_DIR 注入 C 编译
- 证据：meson.build:99-103
- 细节：`plugindir = get_option('plugin_directory')`，空值回退 `<prefix>/lib/kylin-wlcom/plugins`；`add_project_arguments('-DPLUGIN_DIR="@0@"'.format(plugindir), language:'c')`。

## 三、插件 ABI/API 契约（include/kywc/plugin.h、include/plugin.h）

### F-R4-019 — 版本号打包宏 PLUGIN_VERSION_NUMERIC 与三段 GET 宏
- 证据：include/kywc/plugin.h:14-18
- 细节：PLUGIN_VERSION_NUMERIC(major,minor,micro) 与 GET_PLUGIN_MAJOR_VERSION/MINOR_VERSION/MICRO_VERSION。

### F-R4-020 — ABI 版本打包/解包宏
- 证据：include/kywc/plugin.h:20-24
- 细节：ABI_VERSION(major,minor)、GET_ABI_MAJOR、GET_ABI_MINOR。

### F-R4-021 — 插件厂商标识串默认值
- 证据：include/kywc/plugin.h:27-29
- 细节：`PLUGININVENDORSTRING` 默认字面值 `"KylinSoft Multimedia"`（未定义时）。

### F-R4-022 — 唯一插件 flag 位 KYWC_PLUGIN_FIXED
- 证据：include/kywc/plugin.h:31-33
- 细节：`#define KYWC_PLUGIN_FIXED (1 << 0)`。

### F-R4-023 — struct kywc_plugin_info 含 7 个字段
- 证据：include/kywc/plugin.h:35-44
- 细节：const char *name、*vendor、*class、*description；uint32_t version、abi_version、flags。

### F-R4-024 — 选项值为 5 选 1 联合 option_value
- 证据：include/kywc/plugin.h:46-51
- 细节：int32_t i、double f、const char *str、void *ptr 等联合成员。

### F-R4-025 — option_type 枚举含 5 个值
- 证据：include/kywc/plugin.h:53-59
- 细节：int/float/string/对象指针等共 5 个枚举常量。

### F-R4-026 — struct kywc_plugin_option 含 name/value/type/token 四字段
- 证据：include/kywc/plugin.h:61-66
- 细节：int32_t token 作为选项标识。

### F-R4-027 — 三个插件回调函数指针 typedef
- 证据：include/kywc/plugin.h:111、:116、:121
- 细节：`bool (*plugin_setup_func)(void *plugin, void **teardown_data)`；`void (*plugin_teardown_func)(void *teardown_data)`；`void (*plugin_option_func)(struct kywc_plugin_option *option)`。

### F-R4-028 — 插件必须导出符号 `<name>_plugin_data`，类型 struct kywc_plugin_data，5 字段
- 证据：include/kywc/plugin.h:123-133
- 细节：注释原文 "plugins need export this data symbol: xxx_plugin_data"、"max options number is 64"；字段 info/options/setup/option/teardown，options 注释 "read only, maybe null"。

### F-R4-029 — struct kywc_plugin_hooks 含 3 个钩子函数指针
- 证据：include/kywc/plugin.h:140-144
- 细节：new_view(const struct kywc_view*)、new_output(const struct kywc_output*)、layout_damage(const pixman_region32_t*)。

### F-R4-030 — struct kywc_plugin_interface 含 2 个数据字段 + 15 个函数指针字段
- 证据：include/kywc/plugin.h:155-198
- 细节：数据字段 display、abi_version；函数指针依次为 set_hooks、security_add_global_filter、security_remove_global_filter、security_view_create、security_output_create、security_selection_create、security_set_user_data、security_get_user_data、security_set_decision、security_ref、security_unref、security_set_protector_mode、security_set_protector_color(r,g,b,a float)、security_set_protector_image(width,height,data)、get_default_seat。

### F-R4-031 — 接口获取函数声明
- 证据：include/kywc/plugin.h:200
- 细节：`const struct kywc_plugin_interface *kywc_plugin_get_interface(void);`。

### F-R4-032 — 内部 struct plugin 记录加载全生命周期状态
- 证据：include/plugin.h:14-44
- 细节：字段含 name/path/info/options/setup/option/teardown/handle/teardown_data/interface/hooks/entries/loaded/enabled/invalid 及 wl_list link。

## 四、插件加载器（src/plugin/plugin.c）

### F-R4-033 — 仅接受 .so 后缀文件（大小写不敏感）
- 证据：src/plugin/plugin.c:20-29
- 细节：strlen(name)-3 定位后缀，`strcasecmp(name + index, ".so") != 0` 即返回 NULL。

### F-R4-034 — 插件名取文件名去掉 .so 后缀
- 证据：src/plugin/plugin.c:46-47
- 细节：`plugin->name = strndup(name, index); plugin->path = strdup(fullpath);`。

### F-R4-035 — scan_all_plugins 对 PLUGIN_DIR 做单层目录扫描
- 证据：src/plugin/plugin.c:75-85
- 细节：file_for_each 遍历；日志字面值 "Search all plugins in %s"。

### F-R4-036 — plugin_manager_rescan_plugin 存在重扫描入口
- 证据：src/plugin/plugin.c:87-90

### F-R4-037 — dlopen 使用 RTLD_NOW | RTLD_GLOBAL
- 证据：src/plugin/plugin.c:243-245
- 细节：注释 "use RTLD_NOW to check symbols in plugin"；失败置 plugin->invalid=true，日志 "Failed to load %s: %s"。

### F-R4-038 — 导出符号名按 "%s_plugin_data" 动态拼接后 dlsym
- 证据：src/plugin/plugin.c:252-259
- 细节：string_create("%s_plugin_data", plugin->name)，dlsym 后 free(symbol)。

### F-R4-039 — pdata/info/setup/teardown 任一为空即判无效
- 证据：src/plugin/plugin.c:260-266
- 细节：判定 `!pdata || !pdata->info || !pdata->setup || !pdata->teardown`，日志 "%s: invalid symbol"。

### F-R4-040 — ABI 兼容规则：major 必须相等，minor 不得高于管理器
- 证据：src/plugin/plugin.c:268-277
- 细节：判定式 `major != plugin_manager->abi_version.major || minor > plugin_manager->abi_version.minor`；注释原文 "major equal and minor not older"。

### F-R4-041 — 管理器 ABI 版本硬编码为 1.0
- 证据：src/plugin/plugin.c:333-334
- 细节：major=1、minor=0；:337 日志 "Plugin manager is created with ABI verison %d.%d"（verison 为源码拼写）。

### F-R4-042 — FIXED flag 或配置判定 plugin_need_load 决定是否加载
- 证据：src/plugin/plugin.c:279-284；src/plugin/config.c:288-300
- 细节：`force |= pdata->info->flags & KYWC_PLUGIN_FIXED; if (!force && !plugin_need_load(plugin)) ...`；plugin_need_load 缺省返回 true。

### F-R4-043 — 加载时合并选项、调用 setup；卸载按 teardown 顺序回收并 dlclose
- 证据：src/plugin/plugin.c:295-296（plugin_merge_options）、:390（setup 调用）、:395-397（teardown）、:408（unload dlclose）
- 细节：plugin_manager_create 中 :340-349 先 scan_all_plugins 再加载，加载失败即 unload；插件创建顺序等于目录扫描顺序。

## 五、插件 hook 桥与接口填充（interface.c、plugin_p.h）

### F-R4-044 — hook 点枚举共 3 个真实点 + LAST 哨兵
- 证据：src/plugin/plugin_p.h:10-21
- 细节：PLUGIN_HOOK_NEW_VIEW=0、NEW_OUTPUT、LAYOUT_DAMAGE、LAST=3；struct plugin_hook 含 listener/point/ref_count。

### F-R4-045 — hook 分发遍历所有 loaded&&enabled&&hooks 的插件
- 证据：src/plugin/interface.c:14-45
- 细节：plugin_hook_point_handler 中 wl_list_for_each_safe，按 hook->point switch 调对应非空函数指针。

### F-R4-046 — LAYOUT_DAMAGE 分支缺 break，落入空 default
- 证据：src/plugin/interface.c:37-42
- 细节：case PLUGIN_HOOK_LAYOUT_DAMAGE 调 layout_damage 后直接进入 `default: break;`。

### F-R4-047 — 3 个 hook 分别接到 view/output/layout-damage 三类全局监听
- 证据：src/plugin/interface.c:91-103
- 细节：kywc_view_add_new_listener、output_manager_add_new_enabled_listener、output_manager_add_layout_damage_listener。

### F-R4-048 — hook 引用计数支持多插件订阅同一点
- 证据：src/plugin/interface.c:67-104

### F-R4-049 — set_hooks 每个插件只允许设置一次
- 证据：src/plugin/interface.c:126-135

### F-R4-050 — interface 各函数指针在 :160-198 赋值，security_set_decision 未被赋值
- 证据：src/plugin/interface.c:160-198
- 细节：赋值集合含 set_hooks/security_add/remove_global_filter/security_view/output/selection_create/get_user_data/set_user_data/ref/unref/protector_mode/color/image/get_default_seat；头文件声明的 security_set_decision 不在赋值列表中。

## 六、插件配置 D-Bus（src/plugin/config.c）

### F-R4-051 — 插件管理 D-Bus 对象路径与接口名
- 证据：src/plugin/config.c:10-11
- 细节：path `/com/kylin/Wlcom/Plugin`，interface `com.kylin.Wlcom.Plugin`。

### F-R4-052 — vtable 暴露 6 个方法且全部 UNPRIVILEGED
- 证据：src/plugin/config.c:241-250
- 细节：ListAllPlugins(b)→a(sbb)、PrintPluginInfo(s)→sssuu、PrintPluginConfig(s)→s、LoadPlugin(sb)、EnablePlugin(sb)、SetPluginOption(ssv)。

### F-R4-053 — 持久化配置节名为 "plugins"，JSON 结构 {enabled, options}
- 证据：src/plugin/config.c:254（配置名 "plugins"）、:95-98（JSON 字段 enabled/options）

### F-R4-054 — FIXED 插件拒绝 unload 与 disable
- 证据：src/plugin/config.c:132-136、:162-166

### F-R4-055 — SetPluginOption 非 string 分支存在 union 整体赋值写法
- 证据：src/plugin/config.c:229
- 细节：`entry->option.value.str = opt.value.str;`（联合成员赋值，源码原样）。

## 七、security 插件（src/plugin/security/）

### F-R4-056 — 插件导出符号 security_plugin_data，FIXED 插件
- 证据：src/plugin/security/security.c:504-520
- 细节：info：name="security"、vendor=PLUGINVENDORSTRING、class="security"、description="security demo"、version=PLUGIN_VERSION_NUMERIC(1,0,0)、abi_version=ABI_VERSION(1,0)、flags=KYWC_PLUGIN_FIXED；data 的 options=NULL、option=NULL，setup=security_plugin_setup、teardown=security_plugin_teardown。

### F-R4-057 — 注册自定义快捷键 "Alt+Shift+d:no"
- 证据：src/plugin/security/security.c:452-461
- 细节：描述串 "Show security gui"，FUNC_ID_CUSTOM，注册类型 KEY_BINDING_TYPE_CUSTOM_DEF。

### F-R4-058 — GUI 进程经 memfd_create + 双 fork + setsid + /proc/self/fd 启动
- 证据：src/plugin/security/security.c:51-135
- 细节：memfd_create 名字 "gui_app"；execl 路径形如 /proc/self/fd/<fd>。

### F-R4-059 — Wayland 连接经 socketpair 以 WAYLAND_SOCKET 传给 GUI
- 证据：src/plugin/security/security.c:51-135
- 细节：socketpair 一端置子进程 WAYLAND_SOCKET 环境变量。

### F-R4-060 — 访问判定读取客户端环境变量 LAUNCHED_FROM
- 证据：src/plugin/security/security.c:161-163、:233-239、:293

### F-R4-061 — new_view hook 对带 LAUNCHED_FROM 的 view 创建 SOFT_DENY security
- 证据：src/plugin/security/security.c:269-303
- 细节：:291-303 为创建 SOFT_DENY 的实际调用段。

### F-R4-062 — selection 创建 SOFT_DENY
- 证据：src/plugin/security/security.c:484-486

### F-R4-063 — kywc_security_configuration_v1 global 经 global filter 仅对 gui client 可见
- 证据：src/plugin/security/security.c:382-386、:481

### F-R4-064 — 处理 3 个 protector 请求：mode/color/image
- 证据：src/plugin/security/security.c:311-360
- 细节：color 的 UINT32 分量除以 UINT32_MAX 转 float；image 经 mmap 并按 width*height*4 校验大小。

### F-R4-065 — gui.cpp 为 Qt5 程序，registry 中只 bind kywc_security_configuration_v1
- 证据：src/plugin/security/gui.cpp:5-30（Qt 头包含 QApplication/QColorDialog/QImage/QSocketNotifier 等）、:39-46（registry handler 比较 kywc_security_configuration_v1_interface.name 并 wl_registry_bind(...,1)）、:63（QApplication app）
- 细节：:402 调 kywc_security_configuration_v1_set_protector_color，:439 调 set_protector_image(fd,width,height)，:450 调 set_protector_mode。

## 八、security 插件协议（src/plugin/security/security.xml）

### F-R4-066 — 协议仅 1 个接口 kywc_security_configuration_v1，version=1
- 证据：src/plugin/security/security.xml:2、:8
- 细节：协议名 kywc_security_configuration_v1；版权 SPDX 为 MulanPSL-2.0（:3-5）。

### F-R4-067 — 接口 4 个请求：destroy 与 3 个 set_protector_*
- 证据：src/plugin/security/security.xml:12-52
- 细节：destroy(type=destructor)、set_protector_mode(mode uint enum)、set_protector_color(r/g/b/a 四个 uint)、set_protector_image(image fd,width uint,height uint)。

### F-R4-068 — protector_mode 枚举 3 值
- 证据：src/plugin/security/security.xml:15-19
- 细节：fill_none=0（summary "transparent"）、fill_color=1、fill_image=2。

### F-R4-069 — 颜色约定为预乘 alpha、uint 按百分比解释
- 证据：src/plugin/security/security.xml:27-42
- 细节：描述原文 "The r, g, b and a arguments valid range is from UINT32_MIN (0) to UINT32_MAX (0xffffffff)"、"should be interpreted as a percentage"；image 强制 DRM_FORMAT_ARGB8888（:47）。

## 九、内置安全子系统（src/security、include/security）

### F-R4-070 — security_action 枚举 6 值
- 证据：include/security/security.h:18-29
- 细节：ACCESS_NODE、ACCESS_OUTPUT、WRITE_SELECTION、READ_SELECTION、START_DRAG、DROP。

### F-R4-071 — security_decision 枚举 4 值
- 证据：include/security/security.h:31-36
- 细节：ALLOW、SOFT_ALLOW、SOFT_DENY、DENY。

### F-R4-072 — struct security_interface 含 access/notify/destroy 三回调
- 证据：include/security/security.h:79-86

### F-R4-073 — 头文件提供 inline security_action_client 与 3 个 create_for_* 构造
- 证据：include/security/security.h:93-110（inline）、:113-121（create_for_view/output/selection）

### F-R4-074 — 安全 API：selection 检查/access/ref/unref/set_decision
- 证据：include/security/security.h:124-138

### F-R4-075 — security_manager_create 与 global filter API 声明
- 证据：include/security/security.h:140、:143-148

### F-R4-076 — security_context_state 含 sandbox_engine/app_id/instance_id
- 证据：include/security/security.h:151-155

### F-R4-077 — protector_mode 3 值与 3 个 setter 声明
- 证据：include/security/security.h:160-170

### F-R4-078 — security.c 内部定义 security/security_object/security_buffer 三结构
- 证据：src/security/security.c:22-65

### F-R4-079 — 两类 wlr_addon 名字串
- 证据：src/security/security.c:148-151（"security_object"）、:418-421（"security_buffer"）

### F-R4-080 — SOFT_ALLOW 须实现 notify，SOFT_DENY 须实现 access
- 证据：src/security/security.c:233-237

### F-R4-081 — manager 启动按固定顺序创建 4 子系统
- 证据：src/security/security.c:723-726
- 细节：global_filter → ky_security → protector → security_context。

### F-R4-082 — global_filter 调用 wl_display_set_global_filter
- 证据：src/security/global_filter.c:103
- 细节：filter_global 在无注册 filter 时返回 true（:39-42）；内置规则处仅 TODO 注释（:37）。

### F-R4-083 — ky_security.c 实现 kywc-security-v1 协议，manager global 版本 1
- 证据：src/security/ky_security.c:369-370；protocols/kywc-security-v1.xml

### F-R4-084 — security 对象处理 enable/disable/destroy 三请求
- 证据：src/security/ky_security.c:172-176
- 细节：默认决策为 DENY（enabled=true 初值，:270-271、:320-321）。

### F-R4-085 — touched 事件载荷格式 "%s(%d)"
- 证据：src/security/ky_security.c:88-90
- 细节：以 (comm, pid) 拼成 "进程名(pid)" 字串发送。

### F-R4-086 — surface 须 map 后取祖先节点，排除 WORKSPACE/LAYER/VIEW_PROXY 角色
- 证据：src/security/ky_security.c:198-206
- 细节：事件含 enabled/failed/cancelled/touched（protocols/kywc-security-v1.xml:50-84）。

### F-R4-087 — protector 默认模式 FILL_IMAGE、默认颜色白色
- 证据：src/security/protector.c:268-269

### F-R4-088 — 缺省保护图为 200x100 缓冲，monospace 字体、红色 30px 文字 "SECURITY"
- 证据：src/security/protector.c:39-51
- 细节：painter_draw_buffer 绘制，text 字面值 "SECURITY"，font "monospace"。

### F-R4-089 — security_set_protector_color 实参顺序 (r,g,b,a) 但结构体按 {r,b,g,a} 赋值
- 证据：src/security/protector.c:288-295
- 细节：:294 源码原文 `protector->color = (struct wlr_render_color){ r, b, g, a };`（g、b 位置交换，见疑点）。

### F-R4-090 — 安全视图圆角四值 {12,12,12,12}
- 证据：src/security/protector.c:197

### F-R4-091 — node->has_effect 时跳过 security 渲染
- 证据：src/security/protector.c:222-225

### F-R4-092 — security_context 实现 wp_security_context_v1
- 证据：src/security/security_context.c:322-349（create_listener 校验 listen_fd：fstat S_ISSOCK + getsockopt SO_ACCEPTCONN 须为 listening socket）、:206-210（嵌套 context 禁止）、:431（context global 自身加 filter：已持 context 的 client 不再见该 global）

### F-R4-093 — render.h 声明安全渲染检查与 target/region 接口
- 证据：include/security/render.h
- 细节：security_check_node/output/buffer、target_add_*、security_get_region、security_render/node 等声明。

## 十、protocols/kywc-security-v1.xml

### F-R4-094 — 协议含 2 个接口
- 证据：protocols/kywc-security-v1.xml:8（kywc_security_manager_v1 version=1）、:39（kywc_security_v1 version=1）

### F-R4-095 — manager 接口 3 请求：destroy、get_security_for_surface、get_security_for_output
- 证据：protocols/kywc-security-v1.xml:14-37

### F-R4-096 — security 对象接口 3 请求 + 4 事件
- 证据：protocols/kywc-security-v1.xml:44-84
- 细节：请求 destroy(destructor)/enable/disable；事件 failed/cancelled/enabled/touched。

## 十一、effect 框架核心（effect.c/effect.h/effect_p.h/config.c）

### F-R4-097 — effect_option 结构定义
- 证据：include/effect/effect.h:26-34

### F-R4-098 — struct effect_interface 含 17 个钩子函数指针
- 证据：include/effect/effect.h:36-66
- 细节：entity_create/destroy/enable（3）、entity_bounding_box/clip_region/opaque_region（3）、node_push_damage/node_render/node_destroy（3）、frame_render_pre/begin/render/end/post（5）、configure、allow_direct_scanout、allow_enabled（3），合计 17。

### F-R4-099 — effect_category 枚举 5 值
- 证据：include/effect/effect.h:68-74
- 细节：UNKNOWN=0、STYLE、ACTION、SCENE、UTILS。

### F-R4-100 — effect_action 为位掩码，TRANSFORM=(1<<8)-1 与 SHAKE=1<<8 同值边界相邻
- 证据：include/effect/effect.h:76-89
- 细节：MAP=1<<0、UNMAP=1<<1、MOVE=1<<2、RESIZE=1<<3、MAXIMIZE=1<<4、MAXIMIZE_RESTORE=1<<5、MINIMIZE=1<<6、MINIMIZE_RESTORE=1<<7、TRANSFORM=(1<<8)-1（=255）、SHAKE=1<<8、ACTIVATE=1<<9。

### F-R4-101 — struct effect 链表/实体/名字等核心字段
- 证据：include/effect/effect.h:91-113
- 细节：wl_list link、wl_list entities（effect_entity->link）、const char *name 等。

### F-R4-102 — 优先级规则注释：值越大优先级越高、位于链表尾，渲染逆序
- 证据：include/effect/effect.h:121-132

### F-R4-103 — effect_chain/slot/entity/node_effect_chain 结构
- 证据：include/effect/effect.h:115-168

### F-R4-104 — 内部 effect_type 枚举含 NODE/VIEW/SCENE 三类
- 证据：src/effect/effect.c:17-22
- 细节：NONE=0、NODE=1<<0、VIEW=1<<1、SCENE=1<<2。

### F-R4-105 — get_effect_types 只置 SCENE 与 NODE 两位，VIEW 从未被赋值
- 证据：src/effect/effect.c:26-38（:34 types|=EFFECT_TYPE_SCENE；:38 types|=EFFECT_TYPE_NODE）；全树 EFFECT_TYPE_VIEW 仅出现在枚举定义处（effect.c:20）
- 细节：grep `EFFECT_TYPE_VIEW` 全 src/effect 仅命中 :20 定义行，无使用点。

### F-R4-106 — node 链 addon 名 "node_effect_chain"
- 证据：src/effect/effect.c:238-241

### F-R4-107 — scene_node_interface 被 effect 层包装替换 9 个回调
- 证据：src/effect/effect.c:566-577

### F-R4-108 — effect_create 工厂签名 (name,priority,enabled,impl,data)
- 证据：src/effect/effect.c:953-978

### F-R4-109 — effect_manager_create 先建 8 个内部 manager 再建 ukui_effect
- 证据：src/effect/effect.c:1011-1032
- 细节：:1021-1029 依次 action_effect_manager/animation_manager/thumbnail_manager/snapshot/capture/ky_capture/stream/ky_stream/wlr_screencopy 共 9 个 create 调用，:1032 ukui_effect_create。

### F-R4-110 — 内置特效按固定顺序分 4 组创建（共 26 个 _effect_create 调用）
- 证据：src/effect/effect.c:1043-1068
- 细节：组1 showfps/blur/screenshot/watermark/move/scale；组2 mouse_click/mouse_trail/touch_click/touch_long/touch_trail；组3 fade/slide/translation/output_transform/color_filter；组4 shake_cursor/shake_view/locate_pointer/magic_lamp/zoom/node_transform/color_picker。

### F-R4-111 — showkey 与 wallpaper 在 server_ready 回调中创建
- 证据：src/effect/effect.c:991-995（调用位于 :993-994）

### F-R4-112 — time_scale 默认 1.0，下限 0.1
- 证据：src/effect/effect.c:1018（默认 1.0）、:1079、:1088（下限校验 0.1）；src/effect/config.c:150-162（D-Bus 入参范围 0.1–20）

### F-R4-113 — 功能键分发 4 个 FUNC_ID
- 证据：src/effect/effect.c:1104-1122

### F-R4-114 — 5 个 scene_output_render_* 包装点
- 证据：src/effect/effect.c:1188-1226
- 细节：frame_render 阶段钩子返回 true 表示特效接管整帧渲染。

### F-R4-115 — effect 配置 D-Bus path/interface 与 5 方法
- 证据：src/effect/config.c:10-12、:150-162、:171
- 细节：path `/com/kylin/Wlcom/Effect`、interface `com.kylin.Wlcom.Effect`；ListAllEffects→a(sub)、EnableEffect(sb)、PrintEffectOptions(s)→s、SetEffectOption(ssv)、SetEffectTimeScale(d)→d。

### F-R4-116 — 特效强制启用键 "force_enabled"，缺省 -1；配置节 "Effects"
- 证据：src/effect/config.c:9（ENABLED_KEY="force_enabled"）、:191-199（缺省 -1）、:166（节名 "Effects"）

## 十二、action_effect 与 animator

### F-R4-117 — action_effect_type 枚举 NONE/FADE/SLIDE
- 证据：include/effect/action.h:15-19

### F-R4-118 — action 选项步骤枚举 ADD=0/SURFACE=1/CONFIRM=2
- 证据：include/effect/action.h:47-51
- 细节：代码实际使用 ADD 与 CONFIRM 两步骤。

### F-R4-119 — action_effect_interface 3 钩子
- 证据：include/effect/action.h:53-59
- 细节：init_options、add_to_node、add_to_view；node/view_add_action_effect 实现于 src/effect/action.c:123-155；action_effect_create 于 action.c:28、action_effect_manager_create 于 :69。

### F-R4-120 — 动画对象空闲池上限 30
- 证据：src/effect/animator.c:19
- 细节：`#define UNUSED_ANIMATION_MAX_COUNT (30)`，入池判断 :297。

### F-R4-121 — 10 种动画类型（CUSTOM + 9 预设曲线），控制点为静态表
- 证据：src/effect/animator.c:29-36
- 细节：表项依次 {0,0}/{1,1}（LINER）、{0.25,0.1}/{0.25,1}（EASE）、{0.42,0}/{1,1}（EASE_IN）、{0,0}/{0.58,1}（EASE_OUT）、{0.42,0}/{0.58,1}（EASE_IN_OUT）、{0.3,0.15}/{0.1,1}（30_15_10_100）、{0,0.4}/{0.2,1}（0_40_20_100）、{0.33,0}/{1,0.75}（33_0_100_75）、{0.3,0.02}/{0.08,1}（30_2_8_100）。

### F-R4-122 — animator 属性掩码 6 位
- 证据：src/effect/animator.c:38-47
- 细节：ALPHA=1<<0、ANGLE=1<<1、GEOMETRY_X=1<<2、GEOMETRY_Y=1<<3、GEOMETRY_W=1<<4、GEOMETRY_H=1<<5、ALL=(1<<6)-1。

### F-R4-123 — 三次贝塞尔求 t 用 Newton-Raphson，8 次迭代、1e-6 阈值
- 证据：src/effect/animator.c:79-127

### F-R4-124 — animation_manager_create 与动画取用边界
- 证据：src/effect/animator.c:216（manager create）、:203（get 时 type<=CUSTOM || type>=ANIMATION_TYPES 拒绝）、:276（CUSTOM 动画 _animation_create）

## 十三、transform 体系

### F-R4-125 — transform_effect_create 是对 effect_create 的包装，category=ACTION，软件渲染器下默认禁用
- 证据：src/effect/transform.c:236-270（:250 软件渲染器判定、:253 effect_create）

### F-R4-126 — 内置 node transform 名 "transform_effect"，priority 98，支持 EFFECT_ACTION_TRANSFORM
- 证据：src/effect/transform.c:778-788（:782 transform_effect_create(..., "transform_effect", 98, NULL)）

### F-R4-127 — transform 选项/4 种 geometry_type/anchor 定义
- 证据：include/effect/transform.h:16-62

### F-R4-128 — transform_effect_interface 4 钩子
- 证据：include/effect/transform.h:64-72
- 细节：update_transform_options、add_new_effect、enable、destroy。

### F-R4-129 — transform impl 实际挂 7 个 effect_interface 钩子
- 证据：src/effect/transform.c:426-435
- 细节：entity_bounding_box、node_push_damage、node_render、frame_render_pre、frame_render_post、configure、allow_direct_scanout。

## 十四、35 个特效/管理器 .c 逐文件注册事实

### F-R4-130 — blur.c：blur_effect_create 注册 ("blur",999,true)，STYLE 类 scene 特效
- 证据：src/effect/blur.c:709（create）、:702-707（blur_impl）、:724（effect_create）
- 细节：impl 挂 frame_render_begin=blur_frame_render_begin、frame_render_end=blur_frame_render_end、frame_render_post=blur_frame_render_post、configure=handle_blur_effect_configure。

### F-R4-131 — blurrer.c：blurrer_create 仅 OpenGL 后端下创建，构建 3 个着色器程序
- 证据：src/effect/blurrer.c:580（create）、:582（OpenGL 判定）、:505-550（create_blur_shaders，:514/:524/:533 三程序）

### F-R4-132 — magic_lamp.c：magic_lamp_effect_create 注册 ("magic_lamp",5,true)
- 证据：src/effect/magic_lamp.c:666（create）、:656-663（effect_impl）、:677（effect_create）、:682-684（support MINIMIZE|MINIMIZE_RESTORE，ACTION 类）
- 细节：:691-694 ANIMATION_TYPE_LINER、subdiv_count=32、subdiv_count2=8；着色器程序创建 :371；subquads_size=32*8（:779）。

### F-R4-133 — fade.c：fade_effect_create 同时注册 action_effect(FADE) 与 transform_effect "fade"
- 证据：src/effect/fade.c:362（create）、:368-370（action_effect_create(ACTION_EFFECT_FADE, MAP|UNMAP, ...)）、:372-374（transform_effect_create(...,"fade",10,...)）

### F-R4-134 — slide.c（HAVE_KDE_SLIDE）：slide_effect_create 注册 action SLIDE 与 transform "slide",5
- 证据：src/effect/slide.c:276（create）、:283-285（ACTION_EFFECT_SLIDE, MAP|UNMAP）、:287-288（"slide",5）
- 细节：:255-259 将系统窗重定父到 LAYER_NORMAL。

### F-R4-135 — scale.c：scale_effect_create 注册 transform "scale",5，支持 5 种动作，crossfade 需 OpenGL
- 证据：src/effect/scale.c:177（create）、:185（OpenGL crossfade 判定）、:186-188（support RESIZE/MAXIMIZE/MAXIMIZE_RESTORE/MINIMIZE/MINIMIZE_RESTORE）、:189-190（"scale",5）
- 细节：enum scale_action 4 值（include/effect/scale.h:10-15）。

### F-R4-136 — translation.c：translation_effect_create 注册 ("translation",105,enable)，SCENE 类
- 证据：src/effect/translation.c:319（create）、:310-316（effect_impl 挂 frame_render_pre/render/post+configure+allow_direct_scanout）、:330（enable=非软件渲染器）、:331（effect_create）
- 细节：duration=400（:326）、category SCENE（:338）；场景为 workspace 切换（include/effect/translation.h）。

### F-R4-137 — output_transform.c：注册 ("output_transform",105,true)，SCENE 类，仅 OpenGL
- 证据：src/effect/output_transform.c:734（create）、:725-731（effect_impl：frame_render_pre/frame_render/frame_render_post+configure+allow_direct_scanout）、:736（OpenGL 判定）、:745（effect_create）、:752（SCENE）
- 细节：scale_duration 默认 1400（:758-759）；type SCALE/ROTATE（include/effect/output_transform.h:10-13）。

### F-R4-138 — move.c：move_effect_create 注册 ("move",0,false)，impl 仅 configure
- 证据：src/effect/move.c:207（create）、:203-204（move_effect_impl 仅 configure）、:214（effect_create）
- 细节：move_proxy API（include/effect/move.h：proxy create/destroy/move/resize）。

### F-R4-139 — shake_view.c：shake_view_effect_create 注册 ("shake_view",0,true)，impl 仅 configure
- 证据：src/effect/shake_view.c:236（create）、:232-233（impl）、:243（effect_create）
- 细节：:202 使用 wl_event_loop 定时器；对外 view_add_shake_effect API。

### F-R4-140 — shake_cursor.c：注册 ("shake_cursor",110,false)，UTILS 类 scene 特效
- 证据：src/effect/shake_cursor.c:478（create）、:470-475（impl：frame_render_pre/end/post+configure+allow_direct_scanout）、:485（effect_create）、:493（scene_add_effect）

### F-R4-141 — locate_pointer.c：注册 ("locate_pointer",111,false)，UTILS 类 scene 特效
- 证据：src/effect/locate_pointer.c:327（create）、:319-324（impl：frame_render_pre/end/post+configure+allow_direct_scanout）、:335（effect_create）
- 细节：选项 "long_press_timeout"（:285、:352）；RADIUS 常量。

### F-R4-142 — showfps.c：注册 ("showfps",112,false)，UTILS 类 scene 特效
- 证据：src/effect/showfps.c:353（create）、:345-350（impl：frame_render_begin/end/post+configure+allow_direct_scanout）、:360（effect_create）
- 细节：选项 always_repaint 默认 true、allow_direct_scanout 默认 false（:376-378）。

### F-R4-143 — showkey.c：注册 ("showkey",106,true)，enable 时注册 D-Bus 两方法，impl 仅 configure
- 证据：src/effect/showkey.c:754（create）、:740-741（impl）、:760-761（effect_create）、:712-713（dbus_register_object path `/com/kylin/Wlcom/Showkey`、iface `com.kylin.Wlcom.Showkey`）
- 细节：vtable :684-685 createShowkey("uuuu"→b)、destroyShowkey；keycode_maps 经 qsort（:772）。

### F-R4-144 — color_filter.c：注册 ("color_filter",200,true)，D-Bus 8 方法
- 证据：src/effect/color_filter.c:286（create）、:282-283（effect_impl 仅 configure）、:293（effect_create）、:13-14（bus "org.ukui.KWin"、path "/ColorFilter"）、:198-210（vtable）、:303（dbus_register_object）
- 细节：8 方法 availableColorFilter/setColorFilter/getCurrentColorFilter/open/close/isEnabled/isShortCutEnabled/setShortCutEnabled；过滤名数组首项 "None","GrayScale","Invert"（:31）；默认 type KYWC_OUTPUT_COLOR_FILTER_PROTANOPIA（:217、:220）；快捷键 "Win+Ctrl+c"、FUNC_ID_TOGGLE_COLOR_FILTER、KEY_BINDING_TYPE_COLOR_FILTER（:306-311）；信号 statusChanged/colorFilterTypeChanged/colorFilterShortCutEnabledChanged（:63-78）。

### F-R4-145 — color_picker.c：注册 ("color_picker",116,true)，scene 特效 + D-Bus
- 证据：src/effect/color_picker.c:722（create）、:715-719（impl：frame_render_pre/end+configure+allow_direct_scanout）、:730（effect_create）、:70-71（iface `com.kylin.Wlcom.ColorPicker`、path "/ColorPicker"）、:669（dbus_register_object）、:677（unregister）
- 细节：PickColor() 返回 "ddd"（:662）。

### F-R4-146 — zoom.c：注册 ("zoom",122,false)，D-Bus org.ukui.Magnifier 8 方法 + 5 快捷键
- 证据：src/effect/zoom.c:926（create）、:919-923（impl：frame_render_pre/end+configure+allow_direct_scanout）、:933（effect_create）、:24-26（iface "org.ukui.Magnifier"、path "/Magnifier"、command "kylin-magnifier"）
- 细节：8 方法 :786-793 StartZoom(uu)→b/SetMagnifierMode(u)/ZoomIn/ZoomOut/IsZooming→b/GetScale→i/GetType→i/StopZoom；5 快捷键 :95-99 "Win+Equal:no"/"Win+Minus:no"/"Win+KP_Add:no"/"Win+KP_Subtract:no"/"Win+Escape:no"；对外 effect_zoom_in/out/exit 三全局函数。

### F-R4-147 — mouse_click.c：mouse_click_effect_create 经 tap_ripple 工厂注册 ("mouse_click",100,false)
- 证据：src/effect/mouse_click.c:121（create）、:142-143（tap_ripple_effect_create）
- 细节：options size=50、color{1,0.2,0.2}、duration=600、start_radius 0.5/end_radius 0.0/attenuation 0.4→0.8（:131-140）；:29-40 监听 seat cursor button，按下 remove_all + add_point（id=0）。

### F-R4-148 — mouse_trail.c：经 trail 工厂注册 ("mouse_trail",100,false)
- 证据：src/effect/mouse_trail.c:120（create）、:138-139（trail_effect_create）
- 细节：color{0.6,0.12,0.12,0.6}、thickness 8.0、life_time 120（:130-136）；监听 motion，id=0。

### F-R4-149 — touch_click.c：经 tap_ripple 工厂注册 ("touch_click",100,false)
- 证据：src/effect/touch_click.c:123（create）、:144-145
- 细节：size=80、color 白、duration 500（:133-142）。

### F-R4-150 — touch_long.c：经 circle_progressbar 工厂注册 ("touch_long",102,true)
- 证据：src/effect/touch_long.c:158（create）、:172-173
- 细节：size=100、animate_delay=200、duration=800（:167-170）。

### F-R4-151 — touch_trail.c：经 trail 工厂注册 ("touch_trail",100,false)
- 证据：src/effect/touch_trail.c:140（create）、:158-159
- 细节：color{0.4,0.4,0.4,0.4}、thickness 8、life 100（:150-156）。

### F-R4-152 — tap_ripple.c：基类工厂，SCENE 类，仅 OpenGL
- 证据：src/effect/tap_ripple.c:266（tap_ripple_effect_create）、:271（OpenGL 判定）、:281（effect_create(name,priority,enabled,...)）、:258-263（effect_impl：frame_render_begin/end/post+configure+allow_direct_scanout）、:286（category SCENE）

### F-R4-153 — trail.c：基类工厂，shape_color 着色器，SCENE 类，仅 OpenGL
- 证据：src/effect/trail.c:332（trail_effect_create）、:338（OpenGL 判定）、:347（effect_create）、:324-329（impl：frame_render_begin/end/post+configure+allow_direct_scanout）、:353（SCENE）、:64（着色器程序创建）

### F-R4-154 — circle_progressbar.c：基类工厂，仅 OpenGL
- 证据：src/effect/circle_progressbar.c:268（create）、:259-264（effect_impl：frame_render_begin/end/post+configure+allow_direct_scanout）、:282（effect_create）、:57（着色器程序创建）

### F-R4-155 — shape.h 给出三套 options/interface/create 签名
- 证据：include/effect/shape.h
- 细节：tap_ripple/trail/circle_progressbar 各自 options 结构、interface 与 create 函数声明。

### F-R4-156 — screenshot.c（HAVE_UKUI_SCREENSHOT）：非 effect_create，注册两套兼容 D-Bus
- 证据：src/effect/screenshot.c:262（screenshot_effect_create）、:264（dbus_register_object registry_bus/path/iface）、:269-270（兼容 "org.kde.KWin"/"org.kde.kwin.Screenshot"）
- 细节：主总线/路径 :14-16："org.ukui.KWin"、"/Screenshot"、"org.ukui.kwin.Screenshot"；vtable 4 方法 :245-253 screenshotFullscreen("")→s、screenshotFull(bb)、screenshotOutput(sbb)、screenshotArea(iiiibb)；兼容名单方法 screenshotFullscreen(b)；输出路径模板 :63 `/tmp/kywc_screenshot_XXXXXX.bmp`（rand_generate 替换 4 字符）；CAPTURE_NEED_PRIVATE_BUFFER（:189）；伪造 CLIENT_TYPE_DBUS 客户端并带 pid/uid/gid（:81-92）；源码函数名含 sceenshot_handle_capture_client/screnshot_get_credentials 拼写。

### F-R4-157 — wallpaper.c：注册 ("wallpaper",0,false)，server_ready 时创建
- 证据：src/effect/wallpaper.c:397（create）、:393-394（wallpaper_effect_impl 仅 configure）、:404（effect_create）
- 细节：:329-337 监听 new_enabled_output 与 theme background_update；:309 theme_manager_get_background(&color)。

### F-R4-158 — watermark.c（HAVE_UKUI_WATERMARK）：注册 ("watermark",0,true)，UTILS 类，allow_enabled 恒 false
- 证据：src/effect/watermark.c:583（create）、:578-580（watermark_effect_impl：configure+allow_enabled）、:591（effect_create）、:599（UTILS）、:573-576（handle_allow_enabled 恒 false）
- 细节：两套 D-Bus：:435-436 "org.ukui.KWin"/"/Watermark"/"org.ukui.kwin.Watermark"（updateWatermark "sd"、updateWatermarkEx "sdiiib"）；:526-538 `/com/kylin/Wlcom/Watermark`（createWatermark "sdiiib"→s、updateWatermark "ssdiiib"→b、destroyWatermark "s"），全部 SD_BUS_VTABLE_UNPRIVILEGED。

### F-R4-159 — ukui_effect.c：ukui_effect_create 发布 ukui_effect_v1 global v1，surface 以 addon 挂载
- 证据：src/effect/ukui_effect.c:702（create）、:709-710（wl_global_create(...,&ukui_effect_v1_interface,1,...,ukui_effect_bind)）
- 细节：:666-700 action options 调整回调；选项掩码 EFFECT_OPTION_XY/TYPE/SIZE/ANIMATION/DURATION/ALPHA/OFFSET。

### F-R4-160 — capture.c：capture_manager_create 为内部 manager（无 wayland global）
- 证据：src/effect/capture.c:1277
- 细节：outputs/buffers 链表；include/effect/capture.h 定义 5 个 CAPTURE_NEED_* 位、capture_interface 4 回调（update/cancel/buffer/client）、create_from_output/area/fullscreen、capture_write_file。

### F-R4-161 — snapshot.c：snapshot_manager_create 为内部快照 manager
- 证据：src/effect/snapshot.c:992
- 细节：include/effect/snapshot.h:19-38 SNAPSHOT_* option 位、anchor、create_from_node/view、set_dst_box/anchors/opacity/mixed_snapshot、snapshot_render、create_scene_buffer。

### F-R4-162 — stream.c：stream_manager_create 为内部 manager，像素格式两种
- 证据：src/effect/stream.c:979、:995
- 细节：DRM_FORMAT_ARGB8888 / DRM_FORMAT_XRGB8888；include/effect/stream.h：STREAM_NEED_CURSOR、interface ready/cancel/client、create_for_output/view。

### F-R4-163 — ky_capture.c：发布 kywc_capture_manager_v1 global，version=2
- 证据：src/effect/ky_capture.c:607（ky_capture_manager_create）、:614（wl_global_create(...,&kywc_capture_manager_v1_interface,2,...)）、:571（impl 起始）

### F-R4-164 — ky_stream.c：发布 kywc_stream_manager_v1 global，version=1
- 证据：src/effect/ky_stream.c:206（create）、:213（wl_global_create(...,1,...)）

### F-R4-165 — wlr_screencopy.c：发布 zwlr_screencopy_manager_v1 global，version=3
- 证据：src/effect/wlr_screencopy.c:436（wlr_screencopy_manager_create）、:443（wl_global_create(...,&zwlr_screencopy_manager_v1_interface,3,...)）

## 十五、14 个 shader 的引用点映射

### F-R4-166 — blur_down.vert/blur_down.frag：blurrer.c include 并建 down 程序
- 证据：src/effect/blurrer.c:17-22（6 个 blur shader 头 include）、:514（opengl_create_program，blur_down）

### F-R4-167 — blur_up.vert/blur_up.frag：blurrer.c :524 创建 up 程序
- 证据：src/effect/blurrer.c:17-22、:524

### F-R4-168 — blur_up_last.vert/blur_up_last.frag：blurrer.c :533 创建 up_last 程序
- 证据：src/effect/blurrer.c:17-22、:533、:539-546
- 细节：up_last uniform：dstBox/sdfUvRotation/alpha/antiAliasing/aspect/roundCornerRadius；通用 uniform（:492-501）pos/frambufferSize（源码拼写）/texClamp/halfpixel/offset/texture。

### F-R4-169 — circle_progressbar.vert、circle_progressbar.frag：circle_progressbar.c include 并创建程序
- 证据：src/effect/circle_progressbar.c:15-16（include）、:57（opengl_create_program）

### F-R4-170 — magic_lamp.vert、magic_lamp.frag：magic_lamp.c include 并创建程序
- 证据：src/effect/magic_lamp.c:25-26、:371

### F-R4-171 — shape_color.vert、shape_color.frag：trail.c include 并创建程序
- 证据：src/effect/trail.c:18-19、:64

### F-R4-172 — tap_ripple.vert、tap_ripple.frag：tap_ripple.c include 并创建程序
- 证据：src/effect/tap_ripple.c:21-22、:62

## 十六、include/kywc 公共导出头（7 个）

### F-R4-173 — boxes.h：整型/浮点两种 box 结构 + 内联几何工具
- 证据：include/kywc/boxes.h:12（`#define KYWC_API static __attribute__((unused)) inline`）、:15-21（struct kywc_box{int x,y,width,height}、struct kywc_fbox{double...}）
- 细节：:23-88 内联 kywc_box_adjust/adjust_ex/adjusted/adjusted_ex/contains_point/equal/empty/not_empty/contains_box 与 fbox_empty/not_empty；:93-109 外部定义 kywc_fbox_equal/kywc_box_intersects/intersection/box_transform/fbox_transform。

### F-R4-174 — output.h：8 组枚举描述输出能力与状态
- 证据：include/kywc/output.h:15-86
- 细节：vrr_policy 3 值（:15-19）、capability 8 位（POWER/BRIGHTNESS/COLOR_TEMP/COLOR_FILTER/VRR/RGB_RANGE/OVERSCAN/SCALING_MODE，:21-30）、color_filter 6 值含 NONE/GRAYSCALE/INVERT/PROTANOPIA/DEUTERANOPIA/TRITANOPIA（:32-39）、scaling_mode 4 值、rgb_range 3 值、color_feature 5 值、backend 4 值（NONE/DRM/HEADLESS/FBDEV）、state_field 16 位（:69-86）。

### F-R4-175 — output.h：struct kywc_output_state/prop/output 与 8 个输出函数
- 证据：include/kywc/output.h:88-147（state 含 width/height/refresh(mHz)、scale、brightness、color_temp、overscan range[0,100]；prop 含 make/model/serial/edid(base64)/edid_hash(md5)；output 含 name/uuid/destroying 与 11 个 events 信号 on/off/scale/transform/mode/position/power/brightness/color_temp/color_filter/destroy）、:149-163
- 细节：8 函数 kywc_output_add_new_listener/add_primary_listener/get_primary/effective_geometry/contains_point/at_point/by_name/by_uuid。

### F-R4-176 — view.h：role 17 枚举器、capabilities 12 位、events 23 信号
- 证据：include/kywc/view.h:46-64（ROLE_UNDEF=-1 + NORMAL=0..AUTHENTICATION=16 共 17 枚举器）、:87-101（12 个能力位 1<<0..1<<11 及 CAPABILITIES_ALL=(1<<12)-1）、:161-209（events 内 23 个 wl_signal）
- 细节：:66-85 11 个 IS/NEED 宏；:117-211 struct kywc_view；:216 起 kywc_view_add_new_listener 注释 "listen new_view signal for xdg-shell and xwayland-shell"。

### F-R4-177 — binding.h：key_binding_type 21 个枚举器（含 NUM 哨兵）
- 证据：include/kywc/binding.h:82-104
- 细节：CUSTOM_DEF=0 至 ZOOM=19 共 20 个实际类型 + KEY_BINDING_TYPE_NUM=20；另 key_binding_stage 3 值（:106-110）、key_binding_option 4 位（:112-117）、gesture stage（:78 附近 GESTURE_STAGE_STOP=1<<3）；全头声明 kywc_key_binding_*/kywc_gesture_binding_* create/register/update/block 等 API。

### F-R4-178 — identifier.h：UUID_SIZE=37，8 个标识/编码函数
- 证据：include/kywc/identifier.h
- 细节：generate/time_generate/rand_generate/uuid/md5/base64 等 8 个函数声明。

### F-R4-179 — log.h：6 个日志级别加 SILENT/LAST
- 证据：include/kywc/log.h
- 细节：kywc_log/kywc_vlog/ratelimited 接口与配套宏。

## 十七、疑点与矛盾

1. **protector 颜色通道顺序疑似交换**：src/security/protector.c:288 函数签名为 `(float r, float g, float b, float a)`，:294 赋值体却是 `(struct wlr_render_color){ r, b, g, a }`——第 2、3 实参交换。若 wlr_render_color 字段顺序确为 r,g,b,a，则 green/blue 通道被对调（源码原文，未做运行时验证）。
2. **interface.c LAYOUT_DAMAGE 缺 break**：src/plugin/interface.c:37-41，case 执行后落入 `default: break;`，功能无影响但风格可疑。
3. **security 插件与 gui 均 install:false**：src/plugin/security/meson.build:57-64、:86-95，shared_module('security') 不安装到 plugindir，而运行时 plugin_manager 只扫描 PLUGIN_DIR（plugin.c:75-85）；默认安装产物中该 FIXED 插件是否落位存在构建/部署差距（开发态构建树可被扫描到的可能未验证）。
4. **security 插件构建依赖 Qt5/C++，缺即 subdir_done**：src/plugin/security/meson.build 条件块；跳过不影响 src/security 内置 ky_security/protector/global_filter/security_context（src/security/meson.build:1-6 无条件编译），编译边界相互独立。
5. **ABI 校验实现比注释更严格**：plugin.c:268 注释 "major equal and minor not older"，:271 实现为插件 minor `>` 管理器 minor 即拒绝（即管理器 1.0 只接受 1.0）；管理器 ABI 硬编码（plugin.c:333-334）。
6. **kywc_plugin_interface 声明的 security_set_decision 在 interface.c 填充段缺失**：include/kywc/plugin.h:185 有该字段，src/plugin/interface.c:160-198 未见赋值；插件经 interface 调用该指针可能为 NULL（调用侧 NULL 检查情况本次未全量核实）。
7. **EFFECT_TYPE_VIEW 定义但无使用点**：src/effect/effect.c:20 定义，get_effect_types 只置 SCENE(:34)/NODE(:38)，全目录 grep 无其他引用。
8. **拼写问题（源码原样）**：blur uniform 名 `frambufferSize`（blurrer.c:492-501，须与 shader 内字面值一致）；plugin 日志 "ABI verison"（plugin.c:337）；screenshot.c 函数名 `sceenshot_handle_capture_client`、`screnshot_get_credentials`。
9. **effect_interface 钩子计数**：逐行清点 include/effect/effect.h:36-66 为 **17 个**函数指针（早期采集摘要曾记 15，以源码为准）；同理 view.h role 为 17 个枚举器、events 为 23 个信号（早期摘要 18/24 不准，已在 F-R4-176 按源码更正）。
10. **文件数与编译数口径**：任务口径"40 个 effect .c"与文件系统一致（`(Get-ChildItem src\effect\*.c).Count`=40）；但 meson 在 4 个特性开关关闭时只编译 36 个（34+ky_capture+ky_stream），screenshot/watermark/slide/ukui_effect 不参与编译；全部 40 个均无插件化安装路径。
11. **config.c union 赋值**：src/plugin/config.c:229 非 string 分支写 `entry->option.value.str = opt.value.str;`，依赖 union 共享存储，源码原样，未发现配套注释说明。
