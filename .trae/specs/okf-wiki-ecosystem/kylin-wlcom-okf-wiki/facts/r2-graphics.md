# R2 事实簇：后端/渲染/场景/输出

> 工作底稿（无 frontmatter）。仓库：`external/dao/action/kylin-wayland-compositor`（下称 kywc），固定提交 `4df656222427f3cd0101e41d828fb64805e66c15`（本会话 `git rev-parse HEAD` 复核，工作区干净）。
> 证据路径均为相对仓库根的路径，行号以 Read 工具 cat -n 为准。`wlr_*`/`wl_*`/`EGL*`/`GBM*`/`drm*`(libdrm) 等为外部符号（wlroots 0.17 / libwayland / EGL / GBM / libdrm），本簇只记 kywc 调用点。零推断：凡涉及目的/意图的表述均单列 `- 备注：` 并注明依据（源码注释/日志/函数名）。

## 采集范围与计数总览

**文件数（PowerShell 口径：`Get-ChildItem -Recurse -File -Include *.c,*.h`）**

| 目录 | .c/.h 数 |
|---|---|
| src/backend | 34 |
| src/render | 26 |
| src/scene | 17（16 个 .c，含 meson 条件编译的 alpha_modifier.c；另有 scene_p.h） |
| src/output | 13（12 个 .c + output_p.h） |
| src/painter | 4（image.c/painter.c/render.c/painter_p.h） |
| include/backend | 6（backend.h/drm.h/eis.h/fbdev.h/libinput.h/session.h） |
| include/render | 11（allocator/drm_syncobj/drm_syncobj_merger/drm_syncobj_v1/egl/opengl/pass/pixel_format/pixman/profile/renderer 各 .h） |
| include/scene | 9 |
| 另有 include/painter.h（include 根，107 行） | — |

**Shader 文件数（`Get-ChildItem -Path src\backend\drm\shaders,src\render\opengl\shaders,src\scene\shaders -File`，三目录合计 29 个文件含 1 个 meson.build）**

- DRM blit shader：`src/backend/drm/shaders/` 4 个（tex.vert/tex.frag/tex_oes.frag/tex_yuv.frag）
- GL render shader：`src/render/opengl/shaders/` 19 个条目 = 18 个 .vert/.frag + meson.build（quad/quad_ex/quad_stroke、tex_common/tex_ex/tex_external/tex_external_ex/tex_mix/tex_rgba/tex_rgba_ex/tex_rgbx/tex_rgbx_ex、linear_gradient/linear_gradient_stroke 各自配对）
- scene shader：`src/scene/shaders/` 4 个（decoration.frag 49 行/decoration.vert 8/shadow.frag 74/shadow.vert 11，meson embed 生成 `*_str.h`）
- 合计 shader 源文件 26 个（4+18+4）

**KYWC_* 环境变量（口径：`Get-ChildItem -Path src,include -Recurse -Include *.c,*.h | Select-String 'getenv\("KYWC'`，20 个调用点、16 个唯一变量名）**

图形簇相关 14 个：KYWC_BACKEND、KYWC_DRM_DEVICES（2 处）、KYWC_FB_DEVICES、KYWC_DRM_NO_ATOMIC、KYWC_DRM_NO_MODIFIERS、KYWC_RENDERER（renderer.c 与 egl.c 各 1 次）、KYWC_RENDERER_ALLOW_SOFTWARE、KYWC_EGL_NO_MODIFIERS、KYWC_ENABLE_TIMELINE、KYWC_SOFTWARE_COLOR、KYWC_DISABLE_DIRECT_SCANOUT、KYWC_OUTPUT_FILL_WALLPAPER、KYWC_USE_LAYOUT_MANAGER、KYWC_FORCE_QUIRKS（src/util/quirks.c:46，不在本簇目录但被 allocator/egl 消费）。非图形：KYWC_LOG_LEVEL、KYWC_XWAYLAND（2 处）。

**像素格式表**：`src/render/pixel_format.c` 中 `.drm_format =` 赋值 35 处（口径：`Select-String -Path src\render\pixel_format.c -Pattern '\.drm_format =' | Measure`）；另有外部 YUV 格式数组（pixel_format.c:257-268，17 个基础 + P010/P012/P016 条件编译）。

**行数口径说明**：`Get-Content | Measure-Object -Line` 结果系统性小于 Read 工具 cat -n（如 thumbnail.c 计数 1556 实际 1849 行、output.c 计数 880 实际 1041），本文件所有行号以 Read cat -n 为准。

**事实总数：178 条**（F-R2-001 ~ F-R2-178），分 15 组：后端接口与自动选择 12 / DRM 后端 24 / fbdev 6 / session-logind 7 / EIS 7 / renderer 选择 11 / allocator 与 GBM 9 / drm_syncobj 9 / 渲染 pass 与 profile 8 / 像素格式 6 / scene 树 18 / surface 与 xdg_shell 10 / decoration 与图形节点 20 / 输出管理与热插拔 24 / painter 7。

---

## 一、后端接口与自动选择（F-R2-001 ~ 012）

### F-R2-001 — 后端等待超时常量与 GPU 上限
- 证据：src/backend/backend.c:23-25
- 细节：`WAIT_SESSION_TIMEOUT=10000`（毫秒）、`WAIT_GPU_TIMEOUT=5000`、`MAX_NUM_GPUS=8`。

### F-R2-002 — framebuffer 设备列表来自 KYWC_FB_DEVICES
- 证据：src/backend/backend.c:68
- 细节：find_framebuffer_devices 读取 `getenv("KYWC_FB_DEVICES")`，按冒号分割为设备路径列表。

### F-R2-003 — DRM 设备列表来自 KYWC_DRM_DEVICES
- 证据：src/backend/backend.c:291
- 细节：find_gpus 读取 `getenv("KYWC_DRM_DEVICES")`；同文件 L421 附近 `if (!getenv("KYWC_DRM_DEVICES"))` 时才创建 drm_backend_monitor（backend.c:421-423）。

### F-R2-004 — 自动发现 DRM 卡走 udev 枚举
- 证据：src/backend/backend.c:171-189
- 细节：enumerate_drm_cards 用 udev enumerate subsystem "drm"、sysname 匹配 `card[0-9]*`、使用 DRM_PRIMARY_MINOR_NAME，经 `drmIsKMS` 过滤并按 udev ID_SEAT 与当前 seat 匹配。

### F-R2-005 — 无设备时等待 session 新设备事件，5 秒超时
- 证据：src/backend/backend.c（find_gpus 等待段，WAIT_GPU_TIMEOUT）
- 细节：枚举无结果时在 session->events.new_dev 上等待，超时即失败。
- 备注：5 秒取值来自 WAIT_GPU_TIMEOUT 常量（F-R2-001）。

### F-R2-006 — 主 GPU 选择按属性优先级
- 证据：src/backend/backend.c:208-266
- 细节：pick_main_gpu 使用 enum gpu_prop_map，优先级序列为 boot_display → boot_vga → 首个 PCI 设备；L222-266 含 USB 设备特殊处理分支。

### F-R2-007 — backend_autocreate 先判定嵌套（nested）环境
- 证据：src/backend/backend.c:427-430
- 细节：检测 WAYLAND_DISPLAY/WAYLAND_SOCKET/DISPLAY 任一存在即调用外部符号 `wlr_backend_autocreate(display, NULL)` 直接返回。
- 备注：即嵌套于 Wayland/X11 会话时整体走 wlroots 自带后端。

### F-R2-008 — 原生路径创建 multi backend + session
- 证据：src/backend/backend.c:431-453
- 细节：否则创建 multi backend 与 session；L453 `getenv("KYWC_BACKEND")` 值为 "fbdev" 时 use_fbdev_backend。

### F-R2-009 — DRM 创建失败回退 fbdev，libinput 加入 multi
- 证据：src/backend/backend.c:457、src/backend/backend.c:469
- 细节：非 fbdev 偏好下 DRM backend 创建失败则创建 fbdev backend；随后 `libinput_backend_create` 结果加入 multi backend。

### F-R2-010 — backend_support_timeline 仅汇总 DRM 后端
- 证据：src/backend/backend.c:501-511
- 细节：遍历 multi backend 内各 backend，对 DRM backend 调 drm_backend_support_timeline。

### F-R2-011 — EIS 与 headless 不在 backend_autocreate 内创建
- 证据：src/backend/backend.c:427-484
- 细节：backend_autocreate 函数体内仅出现 wlr_backend_autocreate / DRM / fbdev / libinput；无 eis_backend_create 调用。
- 备注：eis_backend_create 的调用点位于 server 初始化簇，本簇未覆盖（见疑点 7）。

### F-R2-012 — 后端类型名表
- 证据：src/output/output.c:227
- 细节：后端判定使用名称表 {"none","drm","headless","fbdev"}；嵌套后端（wayland/X11）不出现在该表中。

## 二、DRM 后端（F-R2-013 ~ 036）

### F-R2-013 — DRM backend_impl 的 start 与 buffer caps
- 证据：src/backend/drm/backend.c:69-74、src/backend/drm/backend.c:28-31
- 细节：backend_impl.start 调用 drm_scan_connectors(..., NULL)；get_buffer_caps 返回 WLR_BUFFER_CAP_DMABUF|SHM|DATA_PTR 三位；另实现 get_drm_fd。

### F-R2-014 — 设备变更在 session 非激活与激活时处理不同
- 证据：src/backend/drm/backend.c:89-113
- 细节：handle_device_change：session 非 active 时 HOTPLUG→drm_update_connector；active 时 HOTPLUG→drm_scan_connectors、LEASE→drm_scan_leases。

### F-R2-015 — timeline 支持的三级判定
- 证据：src/backend/drm/backend.c:167-187
- 细节：drm_backend_support_timeline：LEGACY 模式返回 false；存在 mgpu_renderer 时检查 renderer_support_timeline；并在非 master fd 上 `drmGetCap(DRM_CAP_SYNCOBJ_TIMELINE)==1`。

### F-R2-016 — DRM backend 创建时初始化多 GPU 渲染器与 lease 设备
- 证据：src/backend/drm/backend.c:189-239
- 细节：存在 parent 时调 drm_mgpu_renderer_init；L237 调 `drm_lease_device_v1_create`。

### F-R2-017 — 非 master fd 获取方式
- 证据：src/backend/drm/backend.c:147-165
- 细节：drm_backend_get_non_master_fd 重新 open 节点并 `drmDropMaster`。

### F-R2-018 — KMS 模式枚举仅原子/传统两种
- 证据：src/backend/drm/drm_p.h:28-31
- 细节：enum drm_kms_mode { ATOMIC=0, LEGACY }。

### F-R2-019 — output_state 字段位掩码 9 位
- 证据：src/backend/drm/drm_p.h:33-43
- 细节：enum drm_output_state_field：BRIGHTNESS(1<<1)、GAMMA_LUT、RGB_CTM、DAMAGE、RGB_RANGE、OVERSCAN、SCALING_MODE、SIGNAL_TIMELINE、WAIT_TIMELINE。

### F-R2-020 — KMS 属性枚举规模
- 证据：src/backend/drm/drm_p.h:45-95
- 细节：enum drm_crtc_prop 7 项；enum drm_plane_prop 19 项（含 IN_FENCE_FD、HOTSPOT_X/Y、COLOR_ENCODING、COLOR_RANGE、FB_DAMAGE_CLIPS）；enum drm_connector_prop 14 项（含 BRIGHTNESS、"Broadcast RGB"、OVERSCAN、"scaling mode"）。属性名字符串表见 src/backend/drm/properties.c:14-61（crtc_infos/plane_infos/connector_infos 三张表）。

### F-R2-021 — 多 GPU blit 表面模式四种
- 证据：src/backend/drm/drm_p.h:192-213
- 细节：enum drm_surface_blit_mode { NONE, RENDER, COPY, RENDER_COPY }；struct drm_surface 含 render_swapchain/copy_swapchain/timeline/point 等字段。

### F-R2-022 — drm_connector 私有字段
- 证据：src/backend/drm/drm_p.h:318-360
- 细节：含 name[24]、edid、brightness、rgb_range、overscan、scaling_mode、cursor_*、state、adaptive_sync_supported、has_none_mode、max_bpc_bounds[2]。

### F-R2-023 — drm_device 私有字段
- 证据：src/backend/drm/drm_p.h:394-428
- 细节：含 fd、name、addfb2_modifiers、supports_tearing_page_flips、cursor_width/height、mode、drm_event、mgpu_renderer、crtcs/planes/connectors/page_flips/fbs 链表头、session_active。

### F-R2-024 — drm_check_features 的必需能力与环境开关
- 证据：src/backend/drm/drm.c:54-116
- 细节：cursor 尺寸默认 64；DRM_CLIENT_CAP_UNIVERSAL_PLANES 为必需；CRTC_IN_VBLANK_EVENT 与 TIMESTAMP_MONOTONIC 为必需；L79 `getenv("KYWC_DRM_NO_ATOMIC")=="1"` → LEGACY。

### F-R2-025 — modifiers 与 tearing 能力探测
- 证据：src/backend/drm/drm.c:105-116
- 细节：L105 `getenv("KYWC_DRM_NO_MODIFIERS")=="1"` 禁用 modifiers，否则查 DRM_CAP_ADDFB2_MODIFIERS；tearing：LEGACY 查 DRM_CAP_ASYNC_PAGE_FLIP，ATOMIC 查 DRM_CAP_ATOMIC_ASYNC_PAGE_FLIP；另使能 DRM_CLIENT_CAP_CURSOR_PLANE_HOTSPOT。

### F-R2-026 — 传统模式下用 drmModeSetCursor 探测补 cursor plane
- 证据：src/backend/drm/drm.c（add_cursor_plane / init_planes）
- 细节：legacy 路径以 ARGB8888 LINEAR 格式尝试 drmModeSetCursor，成功则补登一个 cursor plane。

### F-R2-027 — CRTC 再分配为二分图匹配且保护已启用输出
- 证据：src/backend/drm/drm.c:715-815
- 细节：reallocate_crtcs 调 drm_util_match_obj 做匹配；禁止给已启用 connector 更换或夺取 CRTC。

### F-R2-028 — 主平面 blit 触发条件与 YUYV 宽度折半
- 证据：src/backend/drm/drm.c:912-1020
- 细节：drm_connector_state_update_primary_fb 依次做 hw_brightness/hw_color_temp/hw_color_filter 三判定（drm_output_use_hw_*）；need_primary_blit 成立条件含：非 main_gpu、硬件不支持色彩、use_yuyv、allocator 为 SHM；满足时调 drm_surface_blit；YUYV 路径缓冲宽度为像素宽/2。

### F-R2-029 — page flip 事件交换缓冲并带 present flags
- 证据：src/backend/drm/drm.c:1630-1716
- 细节：handle_page_flip 将 queued_fb 置为 current_fb、signal release timeline；present flags 为 VSYNC|HW_CLOCK|HW_COMPLETION，非 parent（非多 GPU 子设备）时追加 ZERO_COPY；drmEventContext version=3，处理函数 page_flip_handler2（L1701-1716）。

### F-R2-030 — 连接器扫描与 new_output 发出
- 证据：src/backend/drm/drm.c:1805-1937
- 细节：drm_scan_connectors 维护 seen 数组；LINK_STATUS_BAD 触发断开；分别处理 connect/disconnect；新输出在 L1935 emit `events.new_output`。

### F-R2-031 — session 失活时与 VT 切回时的连接器处理
- 证据：src/backend/drm/drm.c:1734-1803
- 细节：drm_update_connector（L1734-1776）用于 session inactive 期间的变更；drm_restore_connectors（L1778-1803）用于 VT 切回。

### F-R2-032 — 连接器连接时的过滤与属性采集
- 证据：src/backend/drm/drm.c:1391-1574
- 细节：drm_connector_connect 跳过 INTERLACE 模式；读取 EDID blob 并经 drm_util_parse_edid 解析；采集 max_bpc、VRR_CAPABLE、rgb_range/overscan/scaling_mode（属性值 "None" 记录为 has_none_mode）；subconnector 仅保留 "Native"。

### F-R2-033 — lease 对象集合与每输出上限
- 证据：src/backend/drm/drm.c:2077-2147、src/backend/drm/drm.c:2187-2216
- 细节：drm_create_lease 调 drmModeCreateLease，objects 为 connector+crtc+primary plane+cursor plane，每输出最多 4 个对象；drm_scan_leases 扫描已有 lease。

### F-R2-034 — 原子提交属性集合与 IN_FENCE_FD 来源
- 证据：src/backend/drm/kms.c:751-848、src/backend/drm/kms.c:640-647、src/backend/drm/kms.c:850-898
- 细节：atomic_connector_add 设置 CRTC_ID/LINK_STATUS_GOOD/CONTENT_TYPE_GRAPHICS/max_bpc/ACTIVE/MODE_ID/brightness/rgb_range/overscan/scaling_mode/GAMMA_LUT/CTM/VRR_ENABLED 及 plane props、FB_DAMAGE_CLIPS、IN_FENCE_FD、hotspot；wait_timeline 经 `drm_syncobj_timeline_export_sync_file` 导出 sync_file 再写入 IN_FENCE_FD（L640-647）；atomic_kms flags 为 TEST_ONLY/ALLOW_MODESET/NONBLOCK（L850-882）；plane src 坐标为 16.16 定点，YUYV 时 width*2（L707-732）；plane_set_color_properties 硬编码 BT601 + LIMITED 范围（枚举拼写为 LIMITTED，kms.c:102-105）；drm_kms_commit 按 drm->mode 分派，default 分支 `return true`（L897，见疑点 5）。

### F-R2-035 — framebuffer 添加三级回退与 poisoned addon
- 证据：src/backend/drm/fb.c:26-76
- 细节：get_fb_for_bo 依次尝试 drmModeAddFB2WithModifiers / drmModeAddFB2 / legacy drmModeAddFB；use_yuyv 时 width*2 且格式 DRM_FORMAT_YUYV；addon 名 "drm_fb" 与 "drm_poisoned_fb"（poison_buffer）；drmModeCloseFB 失败回退 drmModeRmFB。

### F-R2-036 — DRM 输出色彩：色温表、CTM/LUT 路径与软件色彩强制开关
- 证据：src/backend/drm/output.c:24-267、src/backend/drm/output.c:269-351、src/backend/drm/output.c:441、src/backend/drm/output.c:755-908
- 细节：blackbody_color[] 表覆盖 1000K-25100K（注释标注源自 Redshift colorramp.c）；内置 6 个 4x4 矩阵 default/grayscale/invert/protanopia/deuteranopia/tritanopia（L269-309）；fill_gamma_ramp_with_color_temp（L329-351）；L441 `getenv("KYWC_SOFTWARE_COLOR")=="1"` 强制软色彩；drm_output_use_hw_brightness/color_temp/color_filter（L755-844）依据 kywc_output_state.color_feature（DISABLE/SOFTCOLOR/SOFTGAMMA/SOFTCTM），INVERT 滤镜不走硬件；wlr_output_get_color_capabilities（L885-908）在 OpenGL renderer 下直接返回全部三项能力，否则 probe CRTC 属性；CTM 值编码为 S31.32 sign-magnitude（L427-434）；quirks 含 QUIRKS_MASK_DISABLE_GAMMA/DISABLE_CTM/YUYV_MODE（drm_output_yuyv_enabled L910-918）。

## 三、fbdev 后端（F-R2-037 ~ 042）

### F-R2-037 — fbdev backend caps 与启动时输出上报
- 证据：src/backend/fbdev/backend.c:23-26
- 细节：caps = DATA_PTR|SHM；backend_start emit new_output；session active 时对 output 做 reenable + damage_whole，否则离屏。

### F-R2-038 — fbdev 私有结构
- 证据：src/backend/fbdev/fbdev_p.h
- 细节：fbdev_backend/fbdev_mode/fbdev_screeninfo/fbdev_output；fbdev_output 含 frame_timer、frame_delay、fd、dpms_mode_support、mmap 的 fb 指针。

### F-R2-039 — 像素格式由屏幕信息推算
- 证据：src/backend/fbdev/fbdev.c:45
- 细节：calculate_drm_format（L45）根据 screen info 转换 DRM 格式；同文件含 fbdev_query_screen_info、fbdev_dpms_set。

### F-R2-040 — test/commit 与输出创建
- 证据：src/backend/fbdev/fbdev.c:504、src/backend/fbdev/fbdev.c:531、src/backend/fbdev/fbdev.c:584
- 细节：fbdev_output_test L504、fbdev_output_commit L531、fbdev_output_create L584。

### F-R2-041 — present 事件经 idle 源延迟发送
- 证据：src/backend/fbdev/fbdev.c:387-423
- 细节：output_defer_present 构造 deferred_present_event，用 `wlr_event_loop_add_idle` 在空闲回调中调外部符号 wlr_output_send_present；监听 output destroy 取消事件。

### F-R2-042 — 提交时按 damage 矩形拷贝 shadow framebuffer
- 证据：src/backend/fbdev/fbdev.c:425-459
- 细节：fbdev_output_state_update_fb 通过 wlr_buffer_begin_data_ptr_access(READ) 取数据，断言 stride == x_resolution*bits_per_pixel/8；WLR_OUTPUT_STATE_DAMAGE 时与全屏区求交，按 pixman 矩形逐个拷贝（line_length 含 padding）。

## 四、session / logind（F-R2-043 ~ 049）

### F-R2-043 — session 接口 7 回调且仅 logind 一种实现
- 证据：src/backend/session/session_p.h
- 细节：session_interface 含 destroy/open/close/change_vt/seat_name/get_fd/dispatch 共 7 回调；仓内仅有 logind_create，无 direct/noop 实现。

### F-R2-044 — 激活超时为 0 且只尝试 logind
- 证据：src/backend/session/session.c:22、src/backend/session/session.c:64-65
- 细节：ACTIVATION_TIMEOUT=0；session_init 只尝试 logind；L64 `setenv("XDG_SESSION_TYPE","wayland")`。

### F-R2-045 — udev 监视器过滤 drm 子系统
- 证据：src/backend/session/session.c:260、src/backend/session/session.c:156-222
- 细节：udev monitor filter 为 "drm"；handle_udev_event：add→events.new_dev、change→read_udev_change_event、remove→session_device_destroy；按 devnum 去重。

### F-R2-046 — udev change 事件分类
- 证据：src/backend/session/session.c:128-154
- 细节：read_udev_change_event：HOTPLUG=1 且含 CONNECTOR/PROPERTY 变化、LEASE=1。枚举定义见 include/backend/session.h（SESSION_DEVICE_HOTPLUG=1、LEASE）。

### F-R2-047 — 公共 session 结构与事件
- 证据：include/backend/session.h
- 细节：struct session 含 active、seat[256]、udev/mon/devices 与 events（active、new_dev、destroy）；struct session_device 含 fd/dev 与 change/destroy 事件。

### F-R2-048 — logind 走 sd-bus 的固定服务名
- 证据：src/backend/session/logind.c:22-26、src/backend/session/logind.c:51-62
- 细节：logind_dst="org.freedesktop.login1"、path="/org/freedesktop/login1"，接口 Seat/Session/Manager；destroy 时在 pthread_mutex 保护下异步调用 Session.ReleaseControl（L55-60）。

### F-R2-049 — logind 实现规模与总线轮询
- 证据：src/backend/session/logind.c（全文 543 行，函数索引 23 个，L38-543）、src/backend/session/logind.c:71-85
- 细节：含 open_device/close_device/change_vt/pause_device/properties_changed/add_signal_matches/find_session_path/find_seat_path/get_display_session/set_type/logind_create 等；check_pending_events 用 sd_bus_get_n_queued_read/write 判定挂起消息。

## 五、EIS（libeis 虚拟输入）（F-R2-050 ~ 056）

### F-R2-050 — EIS context 类型与后端结构
- 证据：src/backend/eis/eis_p.h
- 细节：enum eis_context_type { NORMAL=0, REMOTE_DESKTOP, INPUT_CAPTURE }；struct eis_backend 含 layout/contexts/capture_manager/capabilities/active_capture/filter_locks；barrier 方向 VERTICAL=0/HORIZONTAL=1；eis_context_client 含 pointer + absolute（两个 wlr_pointer）与 keyboard。

### F-R2-051 — InputCaptureManager D-Bus 接口
- 证据：src/backend/eis/backend.c:66、src/backend/eis/backend.c:84-85
- 细节：vtable 方法 "AddInputCapture"("u"→"o")、"RemoveInputCapture"；对象路径 `/com/kylin/Wlcom/EIS/InputCapture`，接口 `com.kylin.Wlcom.EIS.InputCaptureManager`。

### F-R2-052 — 调试 socket 环境变量
- 证据：src/backend/eis/backend.c:93
- 细节：`getenv("KYWC_EIS_SOCKET")` 作为 EIS 监听 socket 名。

### F-R2-053 — backend_start 固定创建 REMOTE_DESKTOP context
- 证据：src/backend/eis/backend.c:100
- 细节：eis_context_create(backend, EIS_CONTEXT_TYPE_REMOTE_DESKTOP, backend->capabilities, NULL)。

### F-R2-054 — 能力位不含 touch
- 证据：src/backend/eis/backend.c:150-153
- 细节：capabilities = POINTER|POINTER_ABSOLUTE|KEYBOARD|SCROLL|BUTTON；L150 注释 "touch is not support current"。

### F-R2-055 — per-context D-Bus 对象与信号
- 证据：src/backend/eis/context.c:132-136、src/backend/eis/context.c:171、src/backend/eis/context.c:238-258
- 细节：REMOTE_DESKTOP 注册 `/com/kylin/Wlcom/EIS/RemoteDesktop`；InputCapture context 路径按 `/com/kylin/Wlcom/EIS/InputCapture/%d` 计数生成（L253）；信号 Activated/Deactivated/Disabled 接口名 com.kylin.Wlcom.EIS.InputCapture；connect_to_eis/enable/disable/release 在同文件。

### F-R2-056 — 输入过滤挂载点
- 证据：src/backend/eis/filter.c:125、src/backend/eis/filter.c:165
- 细节：backend_handle_event（L125）挂接输入事件过滤；eis_backend_lock_filter（L165）；barrier hit_test 在同文件。

## 六、renderer 选择（F-R2-057 ~ 067）

### F-R2-057 — renderer 自动选择顺序与回退
- 证据：src/render/renderer.c:27-68
- 细节：L30 读 `getenv("KYWC_RENDERER")`："pixman"→pixman_renderer_create；"vulkan"→`wlr_vk_renderer_create_with_drm_fd`（WLR_HAS_VULKAN_RENDERER 条件，L41-46）；默认走 opengl_renderer_create_with_drm_fd（L48）；硬件创建失败 L52-55 回退 pixman；成功后 renderer_config_init；PROFILE_RENDER_CREATE 打点。
- 备注："gl"/"gles2" 字串在 renderer.c 无显式分支（落入默认 GL），二次解释发生在 egl.c（见 F-R2-061、疑点 1）。

### F-R2-058 — wl_display 侧初始化 buffer 协议
- 证据：src/render/renderer.c:70-101
- 细节：init_wl_shm、single_pixel_buffer_manager_create；L82 `getenv("KYWC_ENABLE_TIMELINE")=="1"` 且 renderer_support_timeline 与 backend_support_timeline 均真时调 drm_syncobj_manager_v1_create；`wlr_linux_dmabuf_v1_create_with_renderer`（version 4）；wayland_buffer_create 失败时回退 wayland_drm_create。

### F-R2-059 — timeline 支持仅 OpenGL
- 证据：src/render/renderer.c:160-168
- 细节：renderer_support_timeline 返回 egl->support_timeline；pixman/vk 路径无此判定。

### F-R2-060 — renderer 缓冲区类型与上传
- 证据：src/render/renderer.c:128-143、src/render/renderer.c:170-211
- 细节：renderer_create_buffer：pixman→SHM，否则 GBM，带 NO_SCANOUT flag；renderer_upload_pixels L170-211；render_buffer_is_opaque 对 single-pixel 1x1 ARGB 有特例；renderer_is_software L145-158。

### F-R2-061 — EGL 内 GL/GLES2 API 选择与 quirks
- 证据：src/render/opengl/egl.c:593-619
- 细节：egl.c 再次 `getenv("KYWC_RENDERER")`："gl"→try_opengl_api，"gles2"→try_gles_api，失败即返回 false；未指定时按 QUIRKS_MASK_PREFER_OPENGL 决定尝试顺序（该 quirk 先 GL 后 GLES2，否则先 GLES2 后 GL）；L619 `egl->is_gles = !epoxy_is_desktop_gl()`。

### F-R2-062 — EGL modifiers 与软件渲染许可开关
- 证据：src/render/opengl/egl.c:200-204、src/render/opengl/egl.c:392-398
- 细节：L200 `getenv("KYWC_EGL_NO_MODIFIERS")` 禁用 EGL modifiers；L392 `getenv("KYWC_RENDERER_ALLOW_SOFTWARE")` 控制软件 GL（llvmpipe/softpipe）是否被接受。

### F-R2-063 — GL renderer 拒绝软件光栅器
- 证据：src/render/opengl/renderer.c:636-645、src/render/opengl/renderer.c:672、src/render/opengl/renderer.c:975
- 细节：create 路径检查 GL_RENDERER 字符串含 "softpipe" 或以 "llvmpipe" 开头（L644-645，`!egl->is_software` 前提）；L672 处理 BGRA8888 扩展；create_with_drm_fd 在 L975。

### F-R2-064 — Renderer D-Bus 配置接口
- 证据：src/render/config.c:1-51
- 细节：对象路径 `/com/kylin/Wlcom/Renderer`、接口 `com.kylin.Wlcom.Renderer`；方法 IsHardwareRendering→b、GetRendererName→s；名字集合 "gles2"/"gl"/"vulkan"/"pixman"，其中 is_gles 判定为 `r->egl->is_gles ? "gles2" : "gl"`。

### F-R2-065 — 多 GPU renderer 初始化的 GL 优先与 pixman 兜底
- 证据：src/backend/drm/renderer.c:32、src/backend/drm/renderer.c:50-102
- 细节：MAX_QUADS=86（L32）；drm_mgpu_renderer_init 先 opengl_renderer_create_with_drm_fd，失败或无 texture formats 时 drm_mgpu_renderer_with_pixman（L50-70）。

### F-R2-066 — 多 GPU blit shader 与 uniform 集合
- 证据：src/backend/drm/renderer.c:172-202、src/backend/drm/renderer.c:204-327
- 细节：create_opengl_shader 编译 tex.vert 与 tex_frag/tex_oes_frag/tex_yuv_frag 之一；uniform：in_position/size/contrast/whitepoint/color_matrix/brightness/tex/pixel_offset_x；render_surface_texture 按 damage 分批（每批最多 86 四边形），wait_timeline 经 export sync_file → egl_create_sync/wait。

### F-R2-067 — blit 提交、swapchain 与缓冲类型
- 证据：src/backend/drm/renderer.c:381-438、src/backend/drm/renderer.c:487-544、src/backend/drm/renderer.c:626-628、src/backend/drm/renderer.c:671、src/backend/drm/renderer.c:676-814
- 细节：blit_buffer_with_opengl 用 wlr_renderer_begin_buffer_pass（带 signal_timeline/point），render_pass_add_rect/submit 带 output->quirks；surface_swapchain_create 在 test_swapchain 失败后去 modifier 重试（L487-544）；pixman renderer 用 DUMB 缓冲、否则 GBM（L626-628），copy swapchain 恒为 DUMB（L671）；drm_surface_init 中 need_render = (renderer 是 opengl)，timeline 创建条件为 backend_support_timeline && renderer_support_timeline && drm_fd>=0（L753-761）；drm_surface_blit（L766-814）RENDER→GL blit、COPY→readpixels 到 dumb buffer。

## 七、allocator 与 GBM（F-R2-068 ~ 076）

### F-R2-068 — allocator 缓冲类型与 flags 枚举
- 证据：include/render/allocator.h
- 细节：enum allocator_buffer_type { GBM, DUMB, SHM, MEM }；flags 含 AUTO/RENDERING/NO_SCANOUT/CURSOR/LINEAR/SINGLE_PLANE。

### F-R2-069 — DRM 节点重开与鉴权
- 证据：src/render/allocator/allocator.c:35-94
- 细节：reopen_drm_node：master 时空 lease → render node → drmAuthMagic。

### F-R2-070 — allocator_create 选择顺序
- 证据：src/render/allocator/allocator.c:232-280
- 细节：backend 与 renderer 均支持 DMABUF → GBM；需要 drmIsMaster 且 quirks 含 QUIRKS_MASK_PREFER_DRM_DUMB（caps 追加）时走 DRM dumb；无 buffer_caps 时 SHM 兜底；quirks 来自 quirks_by_backend(drm_fd)。

### F-R2-071 — kywc 自有 swapchain 容量与 slot age
- 证据：src/render/allocator/swapchain.c
- 细节：SWAPCHAIN_CAP=4（kywc 自有定义，区别于 wlr 原生 WLR_SWAPCHAIN_CAP）；slot 记录 age（L176-177 注释引用 EGL_EXT_buffer_age）。

### F-R2-072 — GBM usage flags 映射与 SCANOUT 失败回退
- 证据：src/render/allocator/gbm.c:133-178
- 细节：gbm_usage_from_flags 默认 GBM_BO_USE_SCANOUT，RENDERING/CURSOR/LINEAR 追加对应位，NO_SCANOUT 去掉 SCANOUT；SCANOUT 分配失败回退加 RENDERING 重试（L170-178）。

### F-R2-073 — GBM 单平面格式查询与缓冲创建
- 证据：src/render/allocator/gbm.c:256、src/render/allocator/gbm.c:291
- 细节：query_single_plane_formats（L256）；gbm_buffer_create（L291）。

### F-R2-074 — dumb/shm/mem 三类分配器入口
- 证据：src/render/allocator/drm_dumb.c:64、src/render/allocator/drm_dumb.c:197-214、src/render/allocator/shm.c:111、src/render/allocator/mem.c:59
- 细节：dumb_buffer_create/dumb_alloc_destroy/dumb_alloc_create；allocator_create_shm_buffer(width,height,format)；allocator_create_mem_buffer(width,height,format)。

### F-R2-075 — 非 master fd 用于 quirks 查询与软件光标锁定
- 证据：src/output/output.c:651-666
- 细节：output_init_quirks 仅对 DRM 执行：drm_backend_get_non_master_fd + quirks_by_backend；QUIRKS_MASK_SOFTWARE_CURSOR 时调 wlr_output_lock_software_cursors。

### F-R2-076 — quirks 强制开关
- 证据：src/util/quirks.c:46
- 细节：`getenv("KYWC_FORCE_QUIRKS")` 解析后强制 quirks 位。
- 备注：quirks.c 不在本簇目录，但 QUIRKS_MASK_PREFER_DRM_DUMB/PREFER_OPENGL/DISABLE_GAMMA/DISABLE_CTM/YUYV_MODE/SOFTWARE_CURSOR/DISABLE_DIRECT_SCANOUT 在本簇多处被消费。

## 八、drm_syncobj（F-R2-077 ~ 085）

### F-R2-077 — timeline 对象与 waiter
- 证据：include/render/drm_syncobj.h
- 细节：struct drm_syncobj_timeline 含 drm_fd/handle/n_refs；waiter 含 ev_fd/event_source/callback；API：create/export/import/ref/unref/transfer/signal/check/waiter_init/export_sync_file/import_sync_file。

### F-R2-078 — 实现关键函数行号
- 证据：src/render/drm_syncobj.c:34、src/render/drm_syncobj.c:111、src/render/drm_syncobj.c:136、src/render/drm_syncobj.c:215
- 细节：create L34、export_sync_file L111、import_sync_file L136、waiter_init L215。

### F-R2-079 — merger 聚合多个 sync fd
- 证据：include/render/drm_syncobj_merger.h
- 细节：merger 含 dst_timeline/point/sync_fd/n_refs；接口 add/add_sync_file（实现在 merger.c）。

### F-R2-080 — wayland 协议 surface 状态
- 证据：include/render/drm_syncobj_v1.h
- 细节：drm_syncobj_surface_v1_state 含 acquire/release 的 point+timeline、release_merger、committed；manager_v1 含 drm_fd/global；接口 manager_v1_create/get_surface_state/state_signal_release_with_buffer/add_release_point。

### F-R2-081 — 协议处理器
- 证据：src/render/drm_syncobj_v1.c:106-149、src/render/drm_syncobj_v1.c:327-404
- 细节：surface set_acquire_point（L106）、set_release_point（L125）；manager get_surface（L327）、import_timeline（L374）、bind L406。

### F-R2-082 — wlr_surface_synced 接入
- 证据：src/render/drm_syncobj_v1.c:167-209
- 细节：surface_synced_finish_state/move_state/commit 三回调（L167/175/189），随 wlr_surface commit 轮换 acquire/release 状态。

### F-R2-083 — buffer release 锁与 signal
- 证据：src/render/drm_syncobj_v1.c:245-326、src/render/drm_syncobj_v1.c:496-540
- 细节：lock_surface_commit（L245）+ surface_handle_client_commit（L280）；release_signaller_handle_buffer_release（L496）；state_signal_release_with_buffer L505、state_add_release_point L524。

### F-R2-084 — eventfd 支持探测
- 证据：src/render/drm_syncobj_v1.c:428-496
- 细节：check_syncobj_eventfd(int drm_fd)。

### F-R2-085 — scene 输出侧双 timeline
- 证据：src/scene/output.c:151-168
- 细节：scene_output_create 在 wlr_backend_get_drm_fd>=0 且 renderer/backend 均支持 timeline 时创建 in/out 两条 drm_syncobj_timeline；失败回退 implicit 并 log；destroy 时对两条 timeline signal(UINT64_MAX)。

## 九、渲染 pass 与 profile（F-R2-086 ~ 093）

### F-R2-086 — 扩展 render pass 数据结构
- 证据：include/render/pass.h:1-99
- 细节：render_round_corner（rb/rt/lb/lt）；render_color_stop、render_linear_gradient（x0,y0,x1,y1 + 2 stops）；render_texture_mix_options；enum render_texture_repeat_mode { NONE, NORAML[原文拼写], CLAMP, MIRROR, DECAL }；render_texture_options 在 wlr 基础选项外包 radius/force_opaque/rotation_angle/repeat_mode/mix_options/wait_timeline；render_rect_options 含 transform/radius/rotation/stroke_width/linear_gradient；render_pass_impl 三回调 submit/add_texture/add_rect。

### F-R2-087 — pass 分派与 save/restore
- 证据：src/render/pass.c
- 细节：dispatch 到 opengl/pixman 各自实现，不支持时回退 wlr 原生选项；提供 render_pass_save/restore。

### F-R2-088 — profile 宏受 TRACY_ENABLE 条件编译
- 证据：include/render/profile.h
- 细节：TRACY_ENABLE 定义时 PROFILE_RENDER_* 映射到 Tracy zone，否则为空宏；实现在 src/render/profile.c；调用点如 renderer.c PROFILE_RENDER_CREATE、scene.c PROFILE_ZONE、output.c PROFILE_RENDER_COLLECT。

### F-R2-089 — scene 目标清屏色
- 证据：src/scene/render.c:124
- 细节：scene_render_target_clear_buffer 清屏色 {0,0,0,1}，清除区域为 damage−invisible。

### F-R2-090 — 安全鉴权裁剪渲染区
- 证据：src/scene/render.c:146-205
- 细节：scene_render_damage_in_target 先 security_check_output 与 SECURITY_ACCESS_OUTPUT 鉴权；无权限时裁掉对应逻辑区域；随后 scene_output_render_begin→根 scene_node_render→render_end。

### F-R2-091 — 软件光标叠加
- 证据：src/scene/render.c:207-269
- 细节：scene_render_target_add_software_cursors 遍历 output->cursors，跳过 disabled/不可见/==hardware_cursor 的光标；坐标换算 L237-239；使用 wlr 原生 wlr_render_pass_add_texture。

### F-R2-092 — 模糊挂载两处入口
- 证据：src/scene/render.c:298-349、src/scene/render.c:351-526
- 细节：scene_render_target_add_blur 调 blur_render_with_target（effect 簇）；scene_render_target_add_texture_with_blur 组装 kywc render_texture_options（radius 乘 scale、rotation_angle、mix_options），blur 区做纹理坐标→帧缓冲坐标多级缩放；注释说明 blur 不支持旋转（include/scene/render.h 结构注释）。

### F-R2-093 — 缩放长度差分校正
- 证据：src/scene/render.c:19、src/scene/render.c:24-121
- 细节：scale_length 用 round 差分校正小数缩放；scene_render_box/region/point（L24-74）、scene_render_buffer_region（L82-121）做 src→dst 区域映射。

## 十、像素格式（F-R2-094 ~ 099）

### F-R2-094 — pixel_format 结构携带 GL 与 pixman 双映射
- 证据：include/render/pixel_format.h
- 细节：struct pixel_format 含 drm_format/bytes_per_block/block_width/block_height/has_alpha/gl_internalformat/gl_format/gl_type/pixman_format；提供 GL↔pixman 双向查询 API。

### F-R2-095 — 格式表规模
- 证据：src/render/pixel_format.c:19-249
- 细节：`.drm_format =` 赋值 35 处（脚本口径）；覆盖 ARGB/XRGB/XBGR/ABGR/RGBX/RGBA/BGRX/BGRA 8888、R8/GR88/RGB888/BGR888、4444/5551/1555/565 系列、2101010 系列、16161616(F)、YVYU/VYUY。

### F-R2-096 — 外部 YUV 格式数组
- 证据：src/render/pixel_format.c:257-268
- 细节：YUYV/UYVY/NV12/NV21/NV16/NV61/NV24/NV42/YUV410/YVU410/YUV411/YVU411/YUV420/YVU420/YUV422/YVU422/YUV444/YVU444 共 18 个（数组 17 项基数），另 `#ifdef DRM_FORMAT_P010/P012/P016` 条件追加。

### F-R2-097 — 注释说明 DRM/GL 字节序对应
- 证据：src/render/pixel_format.c:15
- 细节：注释声明 DRM_FORMAT_ARGB8888 实际兼容 GL_BGRA_EXT。

### F-R2-098 — max_bpc 按格式推导
- 证据：src/backend/drm/kms.c:107-123
- 细节：max_bpc_for_format：101010 格式→10、161616→16、默认 8。

### F-R2-099 — YUYV scanout 时的格式与宽度处理
- 证据：src/backend/drm/fb.c:26-76、src/backend/drm/drm.c:912-1020
- 细节：use_yuyv 时 AddFB 使用 DRM_FORMAT_YUYV 且缓冲宽度折半（见 F-R2-028/F-R2-035）；quirk 开关 QUIRKS_MASK_YUYV_MODE，判定函数 drm_output_yuyv_enabled（src/backend/drm/output.c:910-918）。

## 十一、scene 树（F-R2-100 ~ 117）

### F-R2-100 — 节点接口 10 回调
- 证据：include/scene/scene.h:74-116
- 细节：struct scene_node_interface：accept_input/update_outputs/collect_damage/get_opaque_region/get_round_corner/render/get_bounding_box/get_affected_bounding_box/push_damage/destroy。

### F-R2-101 — 节点类型仅 3 种
- 证据：include/scene/scene.h:119-123
- 细节：enum scene_node_type { TREE, RECT, BUFFER }。

### F-R2-102 — 角色类型枚举 22 个实体
- 证据：include/scene/scene.h:126-158
- 细节：NONE/ROOT/LAYER/WORKSPACE/VIEW_PROXY/VIEW/XDG_TOPLEVEL/XDG_POPUP/XDG_SURFACE/SUBSURFACE/XWAYLAND_WINDOW/XWAYLAND_UNMANAGED/LAYER_SURFACE/DRAG_ICON/SURFACE/SSD/SSD_TITLEBAR/SSD_BUTTONS/MENU/SUBMEBU[原文拼写]/MENU_ITEM/WALLPAPER/DECO/SNAPSHOT/LAST。

### F-R2-103 — 损伤类型与角点索引
- 证据：include/scene/scene.h:160-174
- 细节：enum scene_damage_type { NONE=0, HARMLESS=1<<0, HARMFUL=1<<1, BOTH=(1<<2)-1 }；scene_round_corner_index RB/RT/LB/LT。

### F-R2-104 — bbox 类型与模糊类型
- 证据：include/scene/scene.h:176-201
- 细节：scene_bounding_type 4 值（含 WITHOUT_SSD_SHADOW=3）；scene_blur_type { REALTIME, WALLPAPER, SCREENLOCK }；struct blur_info L193-201；scene_add_effect_event L203-210。

### F-R2-105 — scene_node 字段
- 证据：include/scene/scene.h:217-271
- 细节：parent/link/type/role{type,impl,data}/enabled/input_bypassed/force_damage_event/x,y/radius[4]/damage_type/last_enabled/has_effect/has_blur/blur/extend_render_region/visible_region/input_region/clip_region/impl/events{damage,destroy,add_effect}/addons/data/sent_dmabuf_feedback。

### F-R2-106 — scene 与 scene_output 字段
- 证据：include/scene/scene.h:278-293、include/scene/scene.h:364-408
- 细节：struct scene 含 tree/tree_destroy/outputs/collected_damage/collected_invisible/pushed_damage/linux_dmabuf_v1；scene_output 含 wlr_output/scene/addon/addons/buffer/wlr_damage_ring/collected_damage/frame_damage/geometry/output_configure/in_timeline+in_point/out_timeline+out_point/viewport{src,dst_width,height}/events{viewport,frame,destroy}/index(uint8)/prev_scanout/direct_scanout/output_damage/output_needs_frame。

### F-R2-107 — scene_buffer 字段与 5 信号
- 证据：include/scene/scene.h:320-362
- 细节：buffer/texture 均可 NULL、renderer_destroy、src_box、dst_width/height、transform、repeat_mode、opacity、opaque_region、primary_output、active_outputs(uint64 位图)、wait_timeline/wait_point、point_accepts_input；信号 outputs_update/output_enter/output_leave/output_sample/frame_done；prev_feedback_options。

### F-R2-108 — 默认回调报错并 assert
- 证据：src/scene/scene.c:24-78
- 细节：node_accept_input/update_outputs/collect_damage/render/get_bounding_box 默认实现均 kywc_log(ERROR)+assert(false)；默认 get_opaque_region 清空区域（L47）。

### F-R2-109 — 节点初始化默认值与模糊默认参数
- 证据：src/scene/scene.c:145-183
- 细节：scene_node_init：enabled=true、damage_type=HARMFUL；blur 默认 iterations=4、offset=5.5f、alpha=1.0f（L151-153）；节点插入 parent->children 尾部。

### F-R2-110 — 角色名表与类型名表
- 证据：src/scene/scene.c:191-217
- 细节：角色名表中 SUBMEBU 对应字符串 "submenu"（L211）；types[]={"tree","rect","buffer"}（L217）。

### F-R2-111 — tree 输入逆序、render 跳过特效子节点
- 证据：src/scene/scene.c:255、src/scene/scene.c:328-346
- 细节：tree accept_input 逆序遍历子节点；tree render 在 DISABLE_SUBEFFECT_NODE 时跳过 has_effect 子节点（L338），并调 security_target_add_node（L345）。

### F-R2-112 — 圆角继承用 INT_MIN/MAX 哨兵
- 证据：src/scene/scene.c:407-457、src/scene/scene.c:1050
- 细节：tree_get_round_corner 做哨兵比较；scene_node_get_radius 要求角点落在 WITHOUT_SSD_SHADOW bbox 四角，否则 radius 归 0。

### F-R2-113 — scene 根创建与损伤推送
- 证据：src/scene/scene.c:540、src/scene/scene.c:499-522
- 细节：scene_create 根角色 SCENE_ROLE_ROOT 并覆写 destroy/push_damage；scene_push_damage：HARMLESS 且 damage_node->last_enabled 时与 visible_region 求交后 scene_add_damage，否则 scene_damage_outputs 并并入 pushed_damage。

### F-R2-114 — 损伤收集按输出几何/视口分发
- 证据：src/scene/scene.c:613-649
- 细节：scene_collect_damage 带 PROFILE_ZONE；仅 pushed_damage 非空才收集；按每个 output geometry/viewport 求交分发。

### F-R2-115 — 使能/位置/重父节点规则
- 证据：src/scene/scene.c:666-772
- 细节：scene_node_destroy 先 emit destroy；set_enabled 前后各推一次 HARMFUL 损伤（L678）；force_damage_event 为计数器（L694）；set_position 后 update_outputs（L708）；reparent 含祖先环 assert（L772）。

### F-R2-116 — 模糊参数合并规则与可见性判定
- 证据：src/scene/scene.c:924、src/scene/scene.c:971-1036、src/scene/scene.c:1078、src/scene/scene.c:1127-1174
- 细节：set_blur_opacity 存储 `pow(opacity, 0.4)`；node_for_each_enabled/get_node_blur_info：iterations/offset 取最大、alpha 取最小、type 取最底层非 REALTIME；scene_node_is_visible：tree=有子节点、rect=color[3]!=0、buffer=有 buffer 且 opacity!=0；ENABLE_SECURITY 时 scene_node_render 走 security_render_node；scene_corner_region 为四角矩形并集 +1px 抗锯齿边。

### F-R2-117 — set_input_region/clip_region/blur/radius 的节点类型 assert
- 证据：src/scene/scene.c（各 setter）
- 细节：上述 setter 均 assert 节点类型为 RECT 或 BUFFER（tree 节点不支持）。

## 十二、surface 与 xdg_shell（F-R2-118 ~ 127）

### F-R2-118 — scene_surface 结构与 addon
- 证据：include/scene/surface.h:10-27、src/scene/surface.c:278-335
- 细节：struct scene_surface 含 buffer/surface/addon/node_addon、8 个 listener、buffer_default_impl；scene_surface_create 角色 SCENE_ROLE_SURFACE；surface_map 用 wl_signal_add_next（L321）；两个 addon："scene_surface"（挂 buffer node）与 "scene_surface_node"（挂 wlr_surface）；wlr_surface_try_from_node L335。

### F-R2-119 — 分数缩放通知
- 证据：src/scene/surface.c:30
- 细节：outputs_update 取 surface 当前输出最大 scale，调 wlr_fractional_scale_v1_notify_scale 与 wlr_surface_set_preferred_buffer_scale(ceil)。

### F-R2-120 — output_sample 处理 release point 与 zero_copy
- 证据：src/scene/surface.c:55-75
- 细节：仅主输出处理；drm_syncobj_v1_get_surface_state→add_release_point(timeline, point, event_loop)；调 scene_surface_presented_on_output(zero_copy=direct_scanout)。

### F-R2-121 — SHM 纹理复用锁计数
- 证据：src/scene/surface.c:92-114
- 细节：n_ignore_locks++/-- 配合 client_buffer_mark_next_can_damage；注释（L92-95）说明 wlr_scene 无条件 lock，故此处绕过。

### F-R2-122 — timeline 与 surface 状态映射
- 证据：src/scene/surface.c:116-176
- 细节：set_buffer_with_timeline 将 acquire_timeline/acquire_point 传给 scene_buffer_set_timeline；set_buffer_with_surface_state 映射 OPAQUE_REGION、viewport（VIEWPORT|BUFFER|SCALE|TRANSFORM）、buffer_damage。

### F-R2-123 — scale 三级换算
- 证据：src/scene/surface.c:364-405
- 细节：scene_surface_get_scale：surface scale→buffer/逻辑比→输出 scale 取最大；注释 L41-52 解释分数缩放协议。

### F-R2-124 — xdg_shell 节点结构与角色
- 证据：src/scene/xdg_shell.c:11-20、src/scene/xdg_shell.c:41、src/scene/xdg_shell.c:72-96
- 细节：struct scene_xdg_surface 含 tree/xdg_surface/surface_tree/4 listener；update_position 用 wlr_xdg_surface_get_geometry 取负偏移（popup 用 current.geometry）；create 建外层 tree + scene_subsurface_tree_create，surface_tree 角色 SCENE_ROLE_XDG_SURFACE（L96）。

### F-R2-125 — subsurface 树结构与圆角继承
- 证据：src/scene/subsurface.c:21-40、src/scene/subsurface.c:42-80
- 细节：struct scene_subsurface_tree 含 tree/surface/scene_surface/6 listener/parent/surface_addon；subsurface_get_radius：子表面距父表面各角距离小于父 radius 时继承圆角。

### F-R2-126 — subsurface 排序与递归创建
- 证据：src/scene/subsurface.c:82-158、src/scene/subsurface.c:206-319
- 细节：subsurface_collect_damage 覆写为先算 radius 再调默认 collect_damage；subsurface_tree_reconfigure 按 current.subsurfaces_below/above 排序定位（L172 注释 TODO 可优化）；addon 名 "scene_subsurface_tree"（L206）；create_subsurface 角色 SCENE_ROLE_SUBSURFACE、enabled 初值=mapped；scene_surface_tree_create 递归（below 先于 above，L253）；scene_subsurface_tree_create L316。

### F-R2-127 — scene_buffer 主输出选择与纹理缓存
- 证据：src/scene/buffer.c:28、src/scene/buffer.c:46、src/scene/buffer.c:120-214、src/scene/buffer.c:304-341
- 细节：buffer_get_dest_size dst 优先、90/270 变换交换宽高；不透明条件 opacity==1 且 render_buffer_is_opaque 或显式 opaque_region；buffer_update_outputs 主输出=重叠面积最大、active_outputs 位图 `1ull<<index`、outputs_array[64] 定长、assert 有 active 必有 primary（L188）；wlr_client_buffer 直接取 client_buffer->texture，否则 wlr_texture_from_buffer 缓存并监听 renderer destroy。

## 十三、decoration 与图形节点（F-R2-128 ~ 147）

### F-R2-128 — scene_buffer 渲染：混合模式、安全分支与 output_sample
- 证据：src/scene/buffer.c:343-534
- 细节：ENABLE_SECURITY 时 security_get_region→security_render，否则 security_target_add_buffer（L372-416）；blend 按 opaque 求交选 PREMULTIPLIED/NONE（L467-468）；radius 与 repeat 的 src_box 均先乘 scale（L471-493）；blur 挂载 L495-506；render_pass_add_texture L508；output_sample 事件 release=in_timeline/in_point、direct_scanout=false（L515-523）；非 scanout dmabuf feedback（main_renderer，scanout_primary_output=NULL）L525-533。

### F-R2-129 — set_buffer_with_damage 损伤粒度
- 证据：src/scene/buffer.c:626-649、src/scene/buffer.c:783-795、src/scene/buffer.c:808-838
- 细节：尺寸不变时按 damage 映射（wlr_fbox_transform/wlr_region_scale_xy）推 HARMLESS；尺寸变化或 buffer get-or-lost 推 BOTH；set_timeline L697 带引用计数；opacity 跨越 0/1 推 BOTH 否则 HARMLESS；send_dmabuf_feedback 经 scene_surface_try_from_buffer 找 surface、memcmp 去重后 wlr_linux_dmabuf_v1_set_surface_feedback；scene_buffer_is_clipped 判定 src_box 非常值或 clip 未覆盖全盒。

### F-R2-130 — decoration mask 与边框类型枚举
- 证据：src/scene/decoration.h:10-26
- 细节：enum decoration_mask 8 方位位 + ALL=(1<<8)-1；decoration_border_type OUTER=0/INNER=1。

### F-R2-131 — decoration 基于 scene_rect 并持有 6 区域
- 证据：src/scene/decoration.c:42-97
- 细节：struct scene_decoration 首个成员为 struct scene_rect rect；含 pending_cause/mask/opacity/border_type/surface_width,height/surface_color[4]/surface_blurred/border_thickness/title_height/border_color/title_color/resize_width/round_corner_radius[4]/shadows_size/shadows[THEME_MAX_SHADOW_LAYERS]/render_box 与 6 个区域（surface/title/border/round_corner/pure_clip/clip）/surface_accept_input。

### F-R2-132 — 装饰/阴影 shader 为全局 GL program 单例
- 证据：src/scene/decoration.c:100-200
- 细节：两个全局 program；装饰 uniform：inUV/uv2ndc/inverseTransform/antiAliasing/aspect/rect/roundRadius/borderThickness/borderColor/titleHeight/titleColor；阴影 uniform：size/sigma/color/rect/roundRadius/windowAntiAliasing/windowAspect/windowRect/windowRoundRadius；scene_decoration_create_opengl_shader 嵌入 decoration/shadow 的 vert+frag，失败置 -1。

### F-R2-133 — mask 切区与 8 种 transform 窗口盒
- 证据：src/scene/decoration.c:202-319
- 细节：get_render_region_with_mask 按 mask 切左右上下渲染区；get_window_box_from_surface_box 覆盖 8 种 wl_output_transform 分支（含 FLIPPED*），各带 "rotation correct" 修正。

### F-R2-134 — 阴影 sigma 系数与绘制细节
- 证据：src/scene/decoration.c:321-521
- 细节：scene_decoration_opengl_render 按 clip rects 组 6 顶点/矩形；阴影逆序绘制（L455）；模糊半径→高斯 sigma 系数 0.424660891（L472 注释 =1/(2·sqrt(2ln2))）；border 用 floor scale、title 用 round；1px 抗锯齿 = 0.5/half_height。

### F-R2-135 — 区域更新与 INNER/OUTER 差异
- 证据：src/scene/decoration.c:523-689
- 细节：update_region（L568）：INNER 时 surface 区减 2*border、title 从 0 起；OUTER 时整体内缩 border；scene_decoration_update（L604-689）在 size<=0 时延迟 pending_cause；render_box = window 盒并所有 shadow 盒；尺寸变化推 BOTH 并清除颜色 cause。

### F-R2-136 — 输入热区与不透明区域
- 证据：src/scene/decoration.c:703、src/scene/decoration.c:749-761
- 细节：accept_input resize 热区 off=resize_width?:border，surface_accept_input=false 时减去 surface 区；注释说明 border 不计入不透明区（防止下层窗口可见区碎裂）；title/surface 在 opacity 乘积==1 时不透明并减去圆角。

### F-R2-137 — 渲染回退与创建默认值
- 证据：src/scene/decoration.c:905-1073、src/scene/decoration.c:1141-1185
- 细节：GL 可用走自定义 shader（先 blur 后 opengl_render），否则回退 render_pass_add_rect 画 surface/title/border；create 默认 OUTER、opacity=1.0、初始 color {0,0,0,0.25}、角色 SCENE_ROLE_DECO。

### F-R2-138 — 软渲染下圆角/阴影 setter 静默无效
- 证据：src/scene/decoration.c（set_round_corner_radius/shadow_count/shadow）
- 细节：三个 setter 在 gl_shader.program<0 时直接 return；shadow 数量上限 THEME_MAX_SHADOW_LAYERS；set_surface_color 末尾连带置 surface_accept_input=true（L1333）。

### F-R2-139 — get_affected_bounding_box 区分阴影
- 证据：src/scene/decoration.c:1099
- 细节：bbox 类型为 WITHOUT_SSD_SHADOW 时 OUTER 边框外扩、title 上移。

### F-R2-140 — rect 节点不透明与渲染
- 证据：src/scene/rect.c:63、src/scene/rect.c:163-240、src/scene/rect.c:284-343
- 细节：不透明仅 color[3]==1，再减 clip 与圆角；scene_rect_render 组 render_rect_options（radius 乘 scale、alpha!=1 用 PREMULTIPLIED 否则 NONE）；blur 挂载 L220-232（L223 `.node_ly = geo.x`，见疑点 10）；create L307 推 HARMFUL；set_size 缩小时先推后改、放大后补推；set_color alpha 跨 0/1 推 BOTH。

### F-R2-141 — linear_gradient 仅 OpenGL 生效
- 证据：src/scene/linear_gradient.c:13-17、src/scene/linear_gradient.c:19-91、src/scene/linear_gradient.c:119-202、src/scene/linear_gradient.c:244-251
- 细节：struct scene_linear_gradient 首成员 rect + render_linear_gradient；GL 路径起止点经 scene_render_point 变换、blend NONE；非 wlr_renderer_is_opengl 时只画背景 rect；rect_center_ray_intersect 为 0.5 中心射线与单位盒求交（L175）；set_linear(degree)：radian=(90-degree)·π/180，dir_y 除 aspect；固定 2 个 color stop（set_color_stop_0/1）。

### F-R2-142 — stroke_rect 环形区域
- 证据：src/scene/stroke_rect.c:13-19、src/scene/stroke_rect.c:24-69、src/scene/stroke_rect.c:81-144
- 细节：struct scene_stroke_rect 含 rect/radius[4]/stroke_width；update_region 构造外盒减内盒并四个圆角的环形区，同时设 input_region 与 clip_region；render 用 render_rect_options.stroke_width=stroke_width*scale；SPDX 年份 2026。

### F-R2-143 — 动画节点跟随输出 frame
- 证据：src/scene/animation.c:13-44、src/scene/animation.c:46-119、src/scene/animation.c:183-215
- 细节：enum animation_mask POSITION=1<<0/SIZE=1<<1；animation_state{start,duration(ms),src,dst}；animation_entity 含 node/addon/kywc_output/output_frame/mask/state[4]；实体输出跟随 kywc_output_at_point，监听 scene_output events.frame；percent=elapse/duration 经 animation_value 插值；到位清 mask（POSITION 用 state[0]、SIZE 用 state[1]）；动画进行中重复请求直接 return；animation=NULL 时即时到位；addon 名 "animation_entity"。

### F-R2-144 — alpha-modifier 协议
- 证据：src/scene/alpha_modifier.c（全文 213 行）
- 细节：alpha-modifier-v1-protocol，ALPHA_MODIFIER_VERSION=1，meson 开关 have_alpha_modifier；multiplier=(double)uint32/UINT32_MAX（L96）；surface commit 时 scene_buffer_set_opacity（一次性监听 L83-84）；destroy 时 opacity 复位 1.0（L67-70）；错误码 NO_SURFACE/ALREADY_CONSTRUCTED；addon "wp_alpha_modifier_surface_v1"。

### F-R2-145 — tearing-control 协议
- 证据：src/scene/tearing_control.c（全文 219 行）
- 细节：tearing-control-v1，TEARING_CONTROL_MANAGER_VERSION=1；每 surface current/pending 两个 hint，commit 时 current=pending（L96-100）；addon "wp_tearing_control_v1"；重复创建报 TEARING_CONTROL_EXISTS；manager 为文件级单例（surface_hints 链表）；scene_surface_is_tearing_allowed（L190，current==PRESENTATION_HINT_ASYNC）；scene_is_tearing_needed（L205，遍历全部 hint）。

### F-R2-146 — presentation-time 协议
- 证据：src/scene/presentation_time.c（全文 324 行）
- 细节：PRESENTATION_VERSION=2，clock CLOCK_MONOTONIC（L210）；presentation_feedback 含 resources 链表/output/3 个 output listener/output_committed/commit_seq/zero_copy；surface current/pending 双 feedback 在 commit 时轮换（L135-142）；v1 客户端遇 VRR enabled 强制 refresh=0（L272-275）；zero_copy=false 时清 ZERO_COPY kind（L276-278）；scene_surface_presented_on_output L306 由 surface.c output_sample 调用；addon "wlr_presentation_surface"；presentation_create 失败分支 L234 为 `return NULL;`（函数签名返回 bool，见疑点 12）。

### F-R2-147 — thumbnail 子系统
- 证据：src/scene/thumbnail.h:1-85、src/scene/thumbnail.c:1-1849
- 细节：enum thumbnail_option 7 位（DISABLE_DECOR/DISABLE_SHADOW/DISABLE_ROUND_CORNER/ENABLE_SINGLE_PLANE/ENABLE_SECURITY/ENABLE_STYLE_EFFECT/WITHOUT_SUBEFFECT_NODE）；thumbnail_interface 4 回调 update(buffer,buffer_changed,data)/cancel/buffer/client；5 种类型 NODE/VIEW/WORKSPACE/OUTPUT（L21-27）；thumbnail_buffer 双缓冲（buffer/shadow）+共享链表+single_plane+own_buffer+buffer_changed/was_damaged/has_content/need_destroy/can_destroy；4 类 buffer 子类 node/view/workspace（含 6 个 view listener 的 entry）/output（state_readonly 冻结）；thumbnail_output 监听 frame/destroy/power 并有断电假帧 timer；manager 单例持 4 类 thumbnail 链表与 outputs；schedule_frame 在输出禁用且 force 时按 1000000/refresh µs（默认 60000）定假帧定时器（L176）；非 renderable 客户端缓冲用 renderer_create_buffer(ARGB8888, single_plane) 建 shadow + wlr_renderer_read_pixels + begin_data_ptr_access 回拷（L257-315）；4 个 render 函数 begin_buffer_pass→清 {0,0,0,0} NONE→固定 options（DISABLE_VISIBILITY|DISABLE_BLUR|DISABLE_EFFECT|ENABLE_FORCE_OPAQUE；output 版仅 DISABLE_VISIBILITY|FORCE_OPAQUE L1231）→临时强制 source_node->enabled=true 渲染后还原（L480-483）；workspace 渲染逆序遍历 view_proxies，跳过 unmapped/minimized/skip_switcher/异输出 view（L902-915），DISABLE_DECOR 时用 surface_tree；thumbnail_buffer_render 以 was_damaged/force_update 门控并以 can_destroy 包裹 update 回调（L1660-1721）；thumbnail_output_handle_frame 每帧轮询 4 类链表（L1726）；thumbnail_update 只取第一个 output（L1751）；handle_new_enabled_output L1792；thumbnail_manager_create L1828（output_manager_add_new_enabled_listener L1842）。

## 十四、输出管理与热插拔（F-R2-148 ~ 171）

### F-R2-148 — output_manager 接口与结构
- 证据：src/output/output_p.h:14-55
- 细节：output_manager_interface 单回调 get_configures(bool output_removed)；struct output_manager 含 server/outputs/configure_outputs 链表/fallback_output/primary_output/pending_primary/max_scale/6 事件（new_output/new_enabled_output/primary_output/configured/layout_damage/max_scale）/config/layout_config/impl/7 listener（new_output/configured/backend_destroy/server_start/destroy/suspend/hibernate/resume）/outputs_layout[UUID_SIZE]/has_layout_manager/initial_configured。

### F-R2-149 — 条件编译的协议初始化
- 证据：src/output/output_p.h:98-146
- 细节：xdg_output 无开关；ky_output 无开关；kde_output_management 需 HAVE_KDE_OUTPUT；wlr_output_management 需 HAVE_WLR_OUTPUT；ukui_output_management 需 HAVE_UKUI_OUTPUT；ukui_output_config_init 需 HAVE_UKUI_OUTPUT_CONFIG；ukui_background_manager_create 需 HAVE_UKUI_BACKGROUND。

### F-R2-150 — struct output 字段
- 证据：include/output.h:34-82
- 细节：base(kywc_output)/wlr_output/scene_output/layout_output/frame_timer/link/manager/configure_link/pending_state/geometry/usable_area/6 事件（configure/disable/geometry/usable_area/update_usable_area/update_late_usable_area）/5 listener（present/frame/commit/destroy/request_state）/color_temp/brightness/color_feature/color_filter/vrr_policy/quirks/state_usable/hardware_color/frame_timer_pending/scene_commit/has_pending。

### F-R2-151 — 配置事件类型与状态变化位
- 证据：include/output.h:12-26、src/output/output.c:341-395
- 细节：enum configure_type { NONE, INIT, UPDATE }；output_get_state_changes 产出 13 类变化位：ENABLE/POWER/MODE/TRANSFORM/SCALE/VRR_POLICY/POSITION/BRIGHTNESS/COLOR_TEMP/OVERSCAN/COLOR_FEATURE/COLOR_FILTER/SCALING_MODE/RGB_RANGE。

### F-R2-152 — fallback 输出名与查询
- 证据：src/output/output.c:24、src/output/output.c:28-50、src/output/output.c:85
- 细节：FALLBACK_OUTPUT "FALLBACK"；kywc_output_by_name/by_uuid；output_from_wlr_output 即 wlr_output->data。

### F-R2-153 — 帧调度门控与 10ms 定时器
- 证据：src/output/output.c:96、src/output/output.c:132、src/output/output.c:148-162
- 细节：output_schedule_frame 门控 server->active；schedule_frame_timer 为 10ms 定时器；for_each_output 按 enabled 过滤；has_actual_outputs 判定存在非 fallback 输出。

### F-R2-154 — output 属性上报与模式合成
- 证据：src/output/output.c:254-308
- 细节：output_get_prop 用 wlr_output_is_drm/is_headless/is_fbdev 判定后端；capabilities 初值 POWER 再或 VRR/RGB_RANGE/OVERSCAN/SCALING_MODE/wlr_output_get_color_capabilities；modes 为空（wayland nested）时合成当前模式为 preferred 模式（L294-307）。

### F-R2-155 — VRR/tearing 尝试
- 证据：src/output/output.c:422-458
- 细节：attempt_vrr：NEVER 或 AUTO 且非全屏→关，否则开；attempt_tearing：state->tearing_page_flip=true 后 test，失败回 false。

### F-R2-156 — usable_area 变化联动 xwayland
- 证据：src/output/output.c:476-515
- 细节：usable_area 变化时调 xwayland_update_workarea()（L493）。

### F-R2-157 — output_update_state 同步中枢
- 证据：src/output/output.c:517-649
- 细节：commit 后状态同步：scene_output 生命周期绑定 layout_output（L554-560，assert 同生共灭）；几何变化→output_manager_sort_outputs；ENABLE/SCALE→更新 max_scale；write_config；TRANSFORM→OUTPUT_TRANSFORM_EFFECT_ROTATE，POSITION/SCALE→SCALE 效果（L578-582）；emit configure（L589）；随后依次发 on/off/new_enabled_output/geometry/usable/power/brightness/color_temp/color_filter/mode/transform/scale/position。

### F-R2-158 — 输出 uuid 生成
- 证据：src/output/output.c:234-246、src/output/output.c:668-675
- 细节：EDID 提供 base64（kywc_identifier_base64_generate）；uuid 为 description="make model serial (name)" 的 md5。

### F-R2-159 — 输出销毁触发重配置
- 证据：src/output/output.c:677-732
- 细节：handle_output_destroy：get_configures(true) + add_pending disable + 对其余输出重新 configure；释放 modes/edid/uuid。

### F-R2-160 — present/frame/commit 事件处理
- 证据：src/output/output.c:734-798
- 细节：handle_output_present：scene_commit=false，has_pending 时合并 configure（PROFILE_RENDER_COLLECT）；handle_output_frame：has_pending 置 frame_pending=true 跳过，否则 scene_output_commit + CLOCK_MONOTONIC 取时 send_frame_done（L754）；handle_output_commit：scene_output->frame_damage 非空时 emit layout_damage；handle_request_state 仅处理 WLR_OUTPUT_STATE_MODE（custom_mode 或 mode，L800）。

### F-R2-161 — handle_new_output 热插拔入口
- 证据：src/output/output.c:826-912
- 细节：消费 backend new_output：non_desktop 跳过；wlr_output_init_render；接线 5 listener；初始化 11 个 kywc 事件 + 6 个 output 事件；默认 brightness=100、color_temp=6500（L885-886）；output_add_custom_modes（注释 eDP/LVDS）；headless 且名 "FALLBACK" 记为 fallback_output；emit new_output（L907）→get_configures(false)→configure_outputs。

### F-R2-162 — 挂起/休眠/恢复
- 证据：src/output/output.c:914-923
- 细节：server_start assert primary_output 且置 initial_configured=true；suspend 注释掉断电逻辑，实际销毁全部 wlr_output->swapchain；hibernate 断电；resume 损整或重新上电。

### F-R2-163 — output_manager_create 内建 headless fallback
- 证据：src/output/output.c:987-1041
- 细节：创建 headless backend 加入 multi，添加 1920x1080 命名 "FALLBACK" 的输出（L1019-1023）；监听 backend events.new_output；L1028 `getenv("KYWC_USE_LAYOUT_MANAGER")=="1"` → has_layout_manager；output_manager_config_init + ukui_output_config_init；创建 6 个协议（xdg_output/ky_output 无条件，kde/wlr_output/ukui_output/ukui_background 带 HAVE_ 开关）。

### F-R2-164 — 首选模式与 PPI 自适应缩放
- 证据：src/output/configure.c:20-103
- 细节：output_preferred_mode 取第一个 preferred 否则链表头；get_screen_factor 按物理英寸 <12→20.0、<20→24.5、其余 28.0；get_scale_level 量化为 1.0/1.25/1.5/2.0；output_preferred_scale 用对角 ppi 与 factor 计算 scale_factor；output_fill_preferred_state：enabled=power=true、首选模式/缩放、fallback 坐标 (0,0) 其余 (-1,-1)、transform NORMAL、brightness 缺省 100 且 CLAMP 10-100、color_temp 缺省 6500 且 CLAMP 1000-25000（宏 L17-18，COLORTEMP_CLAMP 对 <1000 回退 6500）。

### F-R2-165 — pending 链表管理
- 证据：src/output/configure.c:153-183
- 细节：output_manager_set_pending_primary；output_manager_add_pending_state 将输出插入 configure_outputs 链表并 log "pending"；clear_pending_configures 清空并 assert 空。

### F-R2-166 — 模式设置失败逐级回退
- 证据：src/output/configure.c:191-244
- 细节：output_find_best_mode 同宽高下取 refresh 相等否则最大；output_state_set_mode 无配置时 wlr_output_preferred_mode，找不到精确模式用 custom_mode；wlr_output_test_state 失败则遍历其余模式逐个 test。

### F-R2-167 — 新 swapchain 首帧填充与壁纸开关
- 证据：src/output/configure.c:246-303
- 细节：output_acquire_buffer 调外部 wlr_swapchain_acquire；L254 `getenv("KYWC_OUTPUT_FILL_WALLPAPER")=="1"` 时 theme_manager_get_background 取背景图/色并启用 "wallpaper" effect（mode=0）；否则 render_pass_add_rect 清色；render_pass_submit(pass, output->quirks) 后 wlr_output_state_set_buffer。

### F-R2-168 — output_set_state 提交流程与等 pageflip
- 证据：src/output/configure.c:305-397
- 细节：destroying 时仅 layout+update_state；按 state_changed/mode_changed/params_changed 组装 wlr_output_state；DRM 启用中同尺寸且 scene_commit 时置 has_pending=true 并等待 pageflip（L337-343，log "Drm output commit need waiting for pageflip"）；wlr_output_configure_primary_swapchain；色彩变化时 wlr_output_is_hardware_color_allowed 决定整损（scene_output_damage_whole）或 schedule_frame；最后 output_set_layout + output_update_state。

### F-R2-169 — configure_outputs 启用/禁用排序与全禁用拒绝
- 证据：src/output/configure.c:405-592
- 细节：primary fixup 逻辑（pending_primary 禁用时清空、自动修正到首个 enabled 输出）；单输出/双输出含 fallback 时坐标修正为 0；所有实际输出将被禁用时拒绝配置（L490-493）；配置顺序：先已启用输出的状态变更→再新启用输出→必要时启用 fallback→切换 primary→最后禁用输出；finish 段兜底 primary 与 fallback；emit configured（INIT/UPDATE）；output_set_color_feature/filter/temp/brightness/power 与 power_outputs 为直接入口（L594-701，温度/亮度带 CLAMP）。

### F-R2-170 — 配置持久化（JSON 两份配置 + D-Bus）
- 证据：src/output/config.c:9-145、src/output/config.c:147-232、src/output/config.c:234-453、src/output/config.c:455-581
- 细节：D-Bus 路径 `/com/kylin/Wlcom/Output`、接口 `com.kylin.Wlcom.Output`，8 个 UNPRIVILEGED 方法：ListAllOutputs("a(ss)"，仅 DRM 输出)、GetCapabilities、GetHardwareCursor、SetBrightness、SetColortemp、SetDirectScanout（直接写 scene_output->direct_scanout）、SetColorFilter、SetColorFeature；output_read/write_config 读写 "outputs" JSON（键 uuid/enabled/width/height/refresh/transform/scale/lx/ly/brightness/color_temp，read 时 uuid 必须匹配）；布局配置键为 `<layout_uuid>:<output_uuid>`（UUID_SIZE*2），多输出 layout uuid = 排序后输出 uuid 拼接的 md5，单输出即其自身 uuid（output_manager_generate_layout L383-453）；has_layout_manager 时 get_configures=output_manager_get_layout_configs（读 "layouts"），否则 fallback_default_configure；CONFIGURE_TYPE_UPDATE 后 output_manager_save_layouts；output_manager_config_init 注册 "outputs" 配置与 D-Bus 对象。

### F-R2-171 — 布局排序/自动摆放/镜像/工作区
- 证据：src/output/layout.c:10-267
- 细节：output_edge_position 四边取边外 1px；output_at_layout_edge 用 wlr_output_layout_contains_point；左右导航按 outputs 链表顺序找前/后启用输出（TOP/BOTTOM 返回 NULL）；output_state_is_mirror_mode：所有启用输出 geometry 相同；kywc_output_at_point 用 closest_point+output_at；output_layout_get_workarea 仅收缩与 layout 外边缘对齐的 usable 边；output_manager_sort_outputs 按 (x,y) 字典序插入排序（已排序则跳过）；output_set_layout：禁用则 wlr_output_layout_remove；lx/ly==-1 走 wlr_output_layout_add_auto 并置 auto_configured=false，否则坐标变化时 wlr_output_layout_add。

## 十五、painter（F-R2-172 ~ 178）

### F-R2-172 — painter_buffer 为 wlr_buffer 实现
- 证据：src/painter/painter_p.h:14-24、src/painter/painter.c:13-52
- 细节：struct painter_buffer 首成员 struct wlr_buffer base，含 stride（=width*4）、scale、dst_width/dst_height、data、own_data；wlr_buffer_impl 仅实现 destroy/begin_data_ptr_access/end_data_ptr_access；begin_data_ptr_access 固定上报 DRM_FORMAT_ARGB8888。

### F-R2-173 — 缓冲按 scale  ceil 分配
- 证据：src/painter/painter.c:54-87
- 细节：painter_buffer_create：own_data = (data==NULL)，data 为空时 malloc(stride*height)；scale 为 0 时记 1.0；dst_* 为 0 时取物理尺寸；painter_create_buffer(width,height,scale) 以 ceil(width*scale)、ceil(height*scale) 建缓冲。

### F-R2-174 — draw_buffer 尺寸自动测量与图像载入
- 证据：src/painter/painter.c:89-151
- 细节：painter_get_buffer_size：pixel.data 存在用其尺寸；auto_resize 且有文本时用 text_get_size 测量（AUTO_RESIZE_EXTEND 高+14、宽+18 并强制居中，L102-106），并清掉 TEXT_ATTR_SUBMENU|CHECKED；hover_rgba 存在时高度翻倍（"draw hover together"）；无 pixel 数据且 info->image 非空时调 image_read_from_file。

### F-R2-175 — redraw 固定回未缩放尺寸与写文件回退
- 证据：src/painter/painter.c:153-200
- 细节：painter_buffer_redraw 把 info 的 width/height/scale 重置为缓冲的 dst 值再渲染；painter_buffer_write_to_file 对非 painter_buffer 临时构造结构并经 wlr_buffer_begin_data_ptr_access(WRITE) 取数据后写出。

### F-R2-176 — cairo/pango 渲染管线
- 证据：src/painter/render.c:20-63、src/painter/render.c:336-384
- 细节：FONT_WEIGHT 固定 500；text_get_size/text_get_metrics 用 pango_font_description + PangoContext（metrics ascent/descent 除以 1024）；render_buffer：own_data 且非 image 时 memset 清零；cairo_image_surface_create_for_data 格式 CAIRO_FORMAT_ARGB32，cairo_surface_set_device_scale；绘制顺序 svg→color(solid/hover/border)→text；hover 时上下两半（upper/lower）分别绘制；CAIRO_OPERATOR_SOURCE。

### F-R2-177 — 文本/圆角/边框/SVG 绘制细节
- 证据：src/painter/render.c:65-298、src/painter/render.c:300-334
- 细节：draw_text 支持 SLANT 斜体、CHECKED("✓")、SUBMENU(">"/"<" RTL 反向)、shortcut、ACCEL（g_markup_escape_text + set_markup_with_accel）、RTL 布局、中段省略（PANGO_ELLIPSIZE_MIDDLE）；draw_color 按 corner_mask 用 cairo_arc 拼圆角、hover 内缩 10%、border 按 border_mask 四边分别 stroke 并在圆角处弧线衔接；draw_svg 先跳空白再校验首字节 '<'，经 rsvg_handle_new_from_data + rsvg_handle_render_document 按 viewport 渲染（librsvg 头外包 GCC diagnostic 以忽略 -Wexpansion-to-defined）。

### F-R2-178 — 图像解码/编码支持格式
- 证据：src/painter/image.c:33-93、src/painter/image.c:141-229、src/painter/image.c:259-384、src/painter/image.c:449-519、src/painter/image.c:521-649、src/painter/meson.build:1-5
- 细节：按文件头魔术数分派：PNG（8 字节签名）→libpng 内存解码（setjmp 错误处理、palette/gray/tRNS/16bit/strip/filler 后处理、premultiply_data 行回调做预乘）；JPEG（FFD8）→libjpeg/libjpeg-turbo 内存解码（turbo 用 JCS_EXT_BGRA，非 turbo 手工 RGB→ARGB，灰度手工扩 ARGB）；ICO（00 00 01 00）→目录项中选 bpp==32 最佳/最大尺寸（256 记 0），内嵌 PNG 或 BMP；BMP（"BM"）→仅接受 BITMAPINFOHEADER(0x28)/32bpp/无压缩，支持负高顶向下；XPM（"/* XPM */"）→按行解析（宽高上限 1024、"None" 色为透明、#rrggbb、自定义 hash_table）；编码仅 PNG（PNG_ALPHA_PREMULTIPLIED + PNG_GAMMA_LINEAR + set_bgr）或 BMP（32bpp、height 取负使文件内底向上），按文件名后缀 3 字符选择；meson 将 image.c/painter.c/render.c 加入 wlcom_sources。

---

## 疑点与矛盾

1. **KYWC_RENDERER 双重 getenv**：src/render/renderer.c:30 只区分 "pixman"/"vulkan"/默认 GL，"gl"/"gles2" 无显式分支；GL/GLES2 的二次解释在 src/render/opengl/egl.c:593-618 再次 `getenv("KYWC_RENDERER")`。同一变量两处读取、两处分支集合不一致。
2. **枚举拼写**：src/backend/drm/drm_p.h 中 DRM_COLOR_ENCODDING_BT709、DRM_COLOR_RANGE_LIMITTED（src/backend/drm/kms.c:102-105 同拼写）；include/render/pass.h 中 RENDER_TEXTURE_REPEAT_NORAML；include/scene/scene.h:154 附近 SCENE_ROLE_SUBMEBU（字符串表 src/scene/scene.c:211 正确写 "submenu"）。
3. **drm_kms_commit default 分支 return true**：src/backend/drm/kms.c:897，未识别模式时提交被视为成功。
4. **多 GPU format 不匹配仅 log**：src/backend/drm/drm.c:1055-1061，格式不匹配不返回失败。
5. **EIS 不进入 backend_autocreate**：src/backend/backend.c:427-484 无 eis_backend_create；调用点应在 server 初始化簇，本簇未覆盖。
6. **drm_p.h:189 TODO**："match each source buffer with its backend buffer"，多 GPU buffer 匹配仍为待办。
7. **两套 swapchain 并存**：scene_output_do_render 用 wlr 原生 wlr_output->swapchain（wlr_swapchain_acquire，WLR_SWAPCHAIN_CAP，src/scene/output.c:273-399）；多 GPU blit 用 kywc 自有 swapchain（SWAPCHAIN_CAP=4，src/render/allocator/swapchain.c）。
8. **rect.c blur 坐标疑似笔误**：src/scene/rect.c:223 `.node_ly = geo.x`（ly 赋成 x，对照应为 geo.y；已二次回读确认源码如此）。
9. **软渲染装饰静默失效**：scene_decoration 的 set_round_corner_radius/shadow_count/shadow 在 gl_shader.program<0 时直接 return，软渲染下圆角/阴影接口无操作且无日志。
10. **bool 函数 return NULL**：src/scene/presentation_time.c:221 签名 `bool presentation_create`，失败分支 L234 为 `return NULL;`（已回读 L221-241 确认）。
11. **scene_output index 上限 64**：index 为 uint8 且 assert <64、active_outputs 为 uint64 位图（include/scene/scene.h:364-408、src/scene/output.c:113-127、src/scene/buffer.c:120-214）；超过 64 个输出触发 assert。
12. **GetRendererName 的 is_gles 判定**：src/render/config.c 以 `r->egl->is_gles ? "gles2" : "gl"` 命名，pixman/vk 路径另返回固定字串。
13. **行数统计口径偏差**：PowerShell `Get-Content | Measure-Object -Line` 系统性小于 Read cat -n（多文件偏差数百行，原因未查明）；本底稿行号一律以 Read cat -n 为准，计数命令口径已在总览注明。
14. **COLORTEMP_CLAMP 边界不对称**：src/output/configure.c:17 宏对 <1000 的值回退为 6500（而非钳到 1000），>25000 才钳到 25000；output_fill_preferred_state 与 output_set_color_temp 均使用该宏。
15. **image.c PNG reader 边界检查**：src/painter/image.c:105 条件为 `reader->position + size < reader->size`（严格小于），末段恰等于剩余长度时会报 "No data in PNG reader"，疑似应为 `<=`，未做运行验证。
