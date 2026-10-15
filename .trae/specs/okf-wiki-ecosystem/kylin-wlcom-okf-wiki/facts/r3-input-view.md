# R3 事实簇：输入/视图/工作区/widget/xwayland/theme/util

## 采集范围与计数总览

### F-R3-001 — 仓库固定提交为 4df656222427f3cd0101e41d828fb64805e66c15，分支 openkylin/huanghe
- 证据：`git rev-parse HEAD` 输出 `4df656222427f3cd0101e41d828fb64805e66c15`；`git log -1` 主题 `Translated using Weblate (Dari)`
- 细节：采集全程只读，未执行 checkout/任何写操作；证据路径均相对仓库根。

### F-R3-002 — R3 六簇源码文件数以 src 目录（含子目录、递归）实测：input 31 .c + 4 私有 .h；view 40 .c + 1 私有 .h；widget 3 .c + 1 私有 .h；xwayland 15 .c + 1 私有 .h；theme 4 .c + 1 私有 .h；util 24 .c
- 证据：计数命令 `Get-ChildItem src/$d -File -Filter *.c` + Python `glob.glob(d+"/**/*.c",recursive=True)`
- 细节：命令原文：`python -c "import glob; ... glob.glob('src/input/**/*.c',recursive=True)"`；输出 `src/input .c=31 .h=4 / src/view .c=40 .h=2 / src/widget .c=3 .h=1 / src/theme .c=4 .h=1 / src/util .c=24 .h=0 / src/xwayland .c=15 .h=1`（glob 的 .h 数含子目录口径差异见 F-R3-003）。

### F-R3-003 — 六簇私有头文件位于 src：input_p.h、text_input_v1.h、text_input_v2.h、text_input_v3.h（4）；view_p.h（1）；widget_p.h（1）；xwayland_p.h（1）；theme_p.h（1）；util 无私有头
- 证据：目录枚举 `src/input/*.h`、`src/view/view_p.h`、`src/widget/widget_p.h`、`src/xwayland/xwayland_p.h`、`src/theme/theme_p.h`
- 细节：对应公开头在 include/input（10 个 .h）、include/view（view.h/workspace.h/action.h）、include/widget（3）、include/xwayland（3）、include/theme.h、include/util（24 个 .h）。

### F-R3-004 — view 簇含子目录 src/view/tile（tile_assist.c、tile_linkage.c、tile_manager.c 共 3 .c），顶层 37 .c；xwayland 簇含子目录 src/xwayland/selection（selection.c、incoming.c、outgoing.c、dnd.c 共 4 .c），顶层 11 .c
- 证据：`Get-ChildItem -Recurse src/view,src/xwayland -Directory`；`src/xwayland/meson.build:62-76`（列 11 个 .c 后 `subdir('selection')`）
- 细节：37+3=40；11+4=15。theme 簇另有非 C 数据子目录 src/theme/icons（meson.build:13 `subdir('icons')`，glob *.c 不计入）。

### F-R3-005 — 任务书给的基线口径（input35/view42/widget4/xwayland16/theme5/util24）按“src 内 .c+.h 总数”核对：input 35、widget 4、xwayland 16、theme 5、util 24 完全一致；view 为 40 .c + 1 .h = 41（另有 tile/meson.build 等构建文件），与基线 42 差 1
- 证据：F-R3-002/F-R3-004 的计数结果
- 备注：差异来自计数口径（是否含 meson.build 或 tile 子目录构建文件），此为客观差异陈述，非错误判定；详见 D-R3-01。

### F-R3-006 — function_id 枚举实测 64 个有效功能 ID（不含 FUNC_ID_NONE 与 FUNC_ID_COUNT）
- 证据：include/input/function.h:11-78；脚本计数输出 `function_id(excl NONE,COUNT): 64`
- 细节：命令口径：正则提取 `enum function_id { ... }` 内全部 `FUNC_ID_*` 标识符后减 2（NONE、COUNT）；枚举自 FUNC_ID_NONE(0) 至 FUNC_ID_BRIGHTNESS_CONTROL，FUNC_ID_COUNT 为哨兵。

### F-R3-007 — key_binding_type 枚举实测 19 个真实类型（不含 CUSTOM_DEF 起的首尾哨兵）；window_action 枚举实测 21 个真实动作
- 证据：include/kywc/binding.h:82-104；include/view/action.h:13-36；脚本输出 `key_binding_type real: 19`、`window_action real: 21`
- 细节：key_binding_type 从 KEY_BINDING_TYPE_CUSTOM_DEF(0) 到 KEY_BINDING_TYPE_ZOOM，KEY_BINDING_TYPE_NUM=20；window_action 从 WINDOW_ACTION_MINIMIZE(1) 到 WINDOW_ACTION_CAPTURE（WINDOW_ACTION_NONE=0）。

### F-R3-008 — xwayland 源文件构建清单为 11 个顶层 .c，由 meson 显式枚举
- 证据：src/xwayland/meson.build:62-74
- 细节：清单字符串：`config.c, eavesdrops.c, grab.c, shell.c, server.c, sockets.c, unmanaged.c, view.c, xauth.c, xwayland.c, xwm.c`；同文件 :13-18 声明 xwayland 特性探测名 `listenfd, no_touch_pointer_emulation, force_xrandr_emulation, terminate_delay`；:21/:27 XWAYLAND_PATH 默认 `/usr/bin/Xwayland`。

## libinput 事件接入与分发

### F-R3-009 — libinput 后端运行独立线程 `libinput_thread_func`，线程内 epoll_wait libinput fd，取到事件后在 mutex 内调用 handle_libinput_event，再用 eventfd 通知主线程
- 证据：src/backend/libinput/backend.c:121-152
- 细节：外部符号（libinput）：`libinput_dispatch`（:135）、`libinput_get_event`（:143）、`libinput_event_destroy`（:145）；通知用 `eventfd_write(backend->notify_fd, 1)`（:151），并以 `atomic_exchange(&backend->notify_pending, true)` 去重（:150，注释称 KWin pattern）。

### F-R3-010 — 主线程通过 wl_event_loop_add_fd 注册 notify_fd，回调 handle_input_batch 内调用 dispatch_input_events 排空队列
- 证据：src/backend/libinput/backend.c:189-197、245-247
- 细节：`wl_event_loop_add_fd(backend->event_loop, backend->notify_fd, WL_EVENT_READABLE, handle_input_batch, backend)`（:245-247，外部符号 wl_server）；handle_input_batch 先 `eventfd_read` 再 `atomic_store(...false)` 后 `dispatch_input_events(backend)`（:192-195）。

### F-R3-011 — libinput 事件不直接发 wlr 信号，而是先入 SPSC 无锁队列：handle_keyboard_key 组装 INPUT_EVENT_KEYBOARD_KEY 后 queue_input_event
- 证据：src/backend/libinput/keyboard.c:56-74
- 细节：外部符号 libinput：`libinput_event_get_keyboard_event`（:58）、`libinput_event_keyboard_get_key_state/get_key/get_time_usec`（:61,:67,:69）；入队结构体字段 `.key = { .key = ..., .pressed = ... }`，时间经 `usec_to_msec`（:67）。

### F-R3-012 — 队列实现是链式扩容的无锁 SPSC ring（util/spsc_chain），单槽容量 INPUT_QUEUE_CAPACITY=64，事件内联存储无逐事件 malloc
- 证据：src/backend/libinput/input_queue.h:14-23、147-157；include/util/spsc_chain.h:11-20
- 细节：注释原文 “Producer: libinput thread (input_queue_push) / Consumer: main thread (input_queue_pop)”；`input_queue_init` 调 `spsc_chain_create(sizeof(struct input_event), 64)`（:155）；满时在 head 链接新节点。

### F-R3-013 — backend 私有枚举 input_event_type 覆盖 33 种事件（DEVICE_ADDED/REMOVED、KEYBOARD_KEY、POINTER 4 种、TOUCH 5 种、SWITCH、手势 8 种、tablet 7 种、RAW_TAP、ZONE 3 种）
- 证据：src/backend/libinput/input_queue.h:25-60
- 细节：与 include/input/input.h:19-56 的同名枚举是两套定义（后者用 100/200/300… 分段编号），见 D-R3-02；队列事件联合体含 key/motion/button/axis/touch/gesture/sw/tablet_axis/tablet_proximity/tablet_tip/tablet_button/tablet_pad/raw_tap/zone_gestesture 等字段（input_queue.h:62-145）。

### F-R3-014 — handle_libinput_event 是 libinput 事件类型总分发，switch 覆盖设备增删与全部指针/触摸/手势/tablet/switch 事件；POINTER_AXIS 旧事件被显式忽略（注释要求改用 SCROLL_*）
- 证据：src/backend/libinput/events.c:231-356
- 细节：case 列表含 LIBINPUT_EVENT_DEVICE_ADDED→handle_device_added（:243）、KEYBOARD_KEY→handle_keyboard_key（:249）、POINTER_MOTION→handle_pointer_motion（:252）、POINTER_BUTTON→handle_pointer_button（:258）、SCROLL_WHEEL/FINGER/CONTINUOUS→handle_pointer_axis_value120（:264-271）、TOUCH_DOWN→handle_touch_down（:273）、TABLET_TOOL_*（:288-308）、TABLET_PAD_*（:300-307）、SWITCH_TOGGLE（:309）、GESTURE_*（:312-335）；:261-263 注释 “This event must be ignored in favour of the SCROLL_* events”。

### F-R3-015 — 设备热插拔在分发线程同步处理：handle_device_added 按 6 种能力初始化 wlr 设备实现，并先 queue DEVICE_ADDED 事件
- 证据：src/backend/libinput/events.c:59-110
- 细节：能力判定外部符号 libinput：`libinput_device_has_capability(dev, LIBINPUT_DEVICE_CAP_KEYBOARD/POINTER/TOUCH/TABLET_TOOL/TABLET_PAD/SWITCH)`（:84-105），分别调 init_device_keyboard/pointer/touch/tablet_tool/tablet_pad/switch_device；:108-109 发 `INPUT_EVENT_DEVICE_ADDED`。

### F-R3-016 — dispatch_input_events 在主线程把队列事件翻译成 wlr 设备信号：键盘调 wlr_keyboard_notify_key，指针/触摸/手势/tablet 发 wl_signal_emit_mutable 到对应 wlr 设备 events
- 证据：src/backend/libinput/events.c:358-699
- 细节：键盘分支构造 wlr_keyboard_key_event 并调外部符号 `wlr_keyboard_notify_key(&dev->keyboard, &key_ev)`（:405）；指针 motion 发 `&dev->pointer.events.motion`（:416），button 发 `.button`（:436），每批后发 frame（:417,:437,:449）；触摸 down/up/motion/cancel/frame 在 :463-497；手势 swipe/pinch/hold 在 :506-575；switch 在 :499-504。

### F-R3-017 — DEVICE_ADDED 在分发阶段发 backend->events.new_input 信号，DEVICE_REMOVED 调 wlr_input_device 系列 finish 并销毁设备
- 证据：src/backend/libinput/events.c:368-395；销毁逻辑 destroy_libinput_input_device events.c:15-42
- 细节：new_input 对每种 impl `wl_signal_emit_mutable(&backend->backend.events.new_input, &dev->xxx.base)`（:370,:373,:376,:380,:383,:386）；destroy 按 impl 调外部符号 `wlr_keyboard_finish/wlr_pointer_finish/wlr_touch_finish/wlr_switch_finish/wlr_tablet_tool_finish/wlr_tablet_pad_finish`（events.c:18-34）。

### F-R3-018 — libinput 后端初始化（backend_start）在起线程前同步 dispatch 一次并派发首批设备，无设备时仅 WARN
- 证据：src/backend/libinput/backend.c:199-233
- 细节：:204-205 外部符号 `libinput_udev_create_context(&libinput_impl,...)`，:211 `libinput_udev_assign_seat`；:229-231 “No input devices during libinput backend initialization”。

### F-R3-019 — 线程挂起/恢复通过第二根 eventfd + spsc_chain 命令队列下发 LIBINPUT_CMD_SUSPEND/RESUME/STOP
- 证据：src/backend/libinput/backend.c:153-183
- 细节：外部符号 `libinput_suspend`（:167）、`libinput_resume`（:165）；命令链容量常量 `LIBINPUT_CMD_QUEUE_CAPACITY`（:238）。

### F-R3-020 — 后端私有 zone gesture（边缘区域手势）与 raw_tap 是条件编译特性：HAVE_LIBINPUT_RAW_TAP / HAVE_LIBINPUT_ZONE_GESTURE
- 证据：src/backend/libinput/events.c:119-131、133-229、336-351、663-695
- 细节：zone_from_libinput 把 `LIBINPUT_ZONE_GESTURE_ZONE_LEFT_EDGE/RIGHT_EDGE/TOP_EDGE/OUTSIDE` 映射为 POINTER_ZONE_GESTURE_*（events.c:134-156）；INPUT_EVENT_RAW_TAP/ZONE_* 由 input_queue.h:55-59 定义。

### F-R3-021 — 键盘设备 impl 名为 “libinput-keyboard”，LED 下沉到 libinput_device_led_update
- 证据：src/backend/libinput/keyboard.c:20-39
- 细节：`const struct wlr_keyboard_impl libinput_keyboard_impl = { .name = "libinput-keyboard", .led_update = keyboard_set_leds }`（:26-29，外部符号接口 wlr）；init_device_keyboard 调外部符号 `wlr_keyboard_init`（:35）。

## seat

### F-R3-022 — input_manager_create 是输入子系统总装配函数，按序创建后端监听、虚拟设备管理器、各类协议全局、bindings/IME/触摸/tablet 等子管理器，最后建默认 seat “seat0”
- 证据：src/input/input.c:785-871
- 细节：:810-811 监听 `server->backend->events.new_input`→handle_new_input；:813-816 创建 eis backend（`eis_backend_create`）并加入 multi backend；:818 wlr_virtual_pointer_manager_v1_create；:823 wlr_virtual_keyboard_manager_v1_create；:828 pointer_gestures；:829 relative_pointer；:831 shortcuts_inhibit；:836 pointer_constraints；:841 cursor_shape(version 1)；:846-864 依次 function_manager_init / input_manager_config_init / selection_manager_create / input_monitor_create / bindings_create / input_method_manager_create / touch/tablet/kde_keystate/kde_clipboard/transient_seat/global_shortcuts/global_gestures/idle/idle_inhibit；:867 `seat_create(input_manager, "seat0")`。

### F-R3-023 — 后端 new_input 信号→handle_new_input→input_create：设备名格式为 “type:vendor:product:name”，EIS 设备为 “V_<name>”
- 证据：src/input/input.c:593-611
- 细节：外部符号 `wlr_input_device_is_eis`（:598）；名字由 `kywc_identifier_generate("%d:%d:%d:%s", type, vendor, product, name)`（:601-602）或 `"V_%s"`（:599）生成。

### F-R3-024 — 虚拟指针/虚拟键盘有独立 new_virtual_pointer/new_virtual_keyboard 监听，名字一律 “V_” 前缀，并应用 suggested_seat/suggested_output
- 证据：src/input/input.c:613-665、818-826
- 细节：handle_new_virtual_pointer 读取 `event->suggested_seat->name`、`event->suggested_output->name` 并 input_set_state（:631-640）；handle_new_virtual_keyboard 同步到 keyboard->seat（:660-664）；虚拟判定字符串前缀 `strncmp(input->name, "V_", 2) == 0`（input.c:272，见 input_get_prop）。

### F-R3-025 — seat_create 创建 wlr_seat、cursor、一个虚拟 keyboard group 容器，默认 cursor_size=24，默认数字锁 INPUT_KEY_NUMLOCK，锁模式 LOCK_MODE_KEY_CUSTOM
- 证据：src/input/seat.c:115-180
- 细节：:122 外部符号 `wlr_seat_create(display, name)`；:164 `seat->state.cursor_size = 24`；:165-166 `keyboard_lock_mode = LOCK_MODE_KEY_CUSTOM`、`keyboard_lock = INPUT_KEY_NUMLOCK`；:171 cursor_create、:172 keyboard_create(seat,NULL)、:173 cursor_set_hidden(true)。

### F-R3-026 — seat 能力按设备类型聚合：TOUCH 同时置 TOUCH|POINTER；POINTER 与 TABLET_TOOL 置 POINTER；KEYBOARD 置 KEYBOARD；SWITCH/TABLET_PAD 不贡献能力
- 证据：src/input/seat.c:189-222
- 细节：外部符号 `wlr_seat_set_capabilities`（:213）；能力变化发 `seat->events.capability`（:220）；指针能力消失时自动隐藏光标（:214-216）。

### F-R3-027 — seat_add_input 按设备类型分流：POINTER/TOUCH/TABLET_TOOL 进 cursor（curosr_add_input），KEYBOARD 进 keyboard_add_input
- 证据：src/input/seat.c:224-245
- 细节：函数名 `curosr_add_input` 为源码原始拼写（seat.c:233，声明 include/input/cursor.h:149）；移除路径 seat_remove_input:247-273。

### F-R3-028 — seat 维护三类内部 grab：pointer/keyboard/touch，启动新 grab 时取消旧 grab
- 证据：src/input/seat.c:295-366；接口定义 include/input/seat.h:16-54
- 细节：seat_start_pointer_grab 另把 `seat->cursor->hold_mode = false`（:312）；seat_start_touch_grab 调 `seat_cancel_touch_points(seat, touch_grab->serial)`（:358）；seat 销毁时对三类 grab 调 interface->cancel（seat.c:81-89）。

### F-R3-029 — seat_focus_surface 是键盘焦点中枢：同时联动 shortcuts inhibitor、tablet 焦点、IME 焦点、pointer constraint
- 证据：src/input/seat.c:406-441
- 细节：:408 `view_manager_update_input_panel_layer(surface)`；:417/:419 外部符号 `wlr_keyboard_shortcuts_inhibitor_v1_deactivate/activate`；:428 `wlr_seat_keyboard_notify_enter`（grab 时不传 keycodes，:429-430）；:438-440 依次 `tablet_set_focus / input_method_set_focus / cursor_constraint_set_focus`。

### F-R3-030 — server start/active 时 seat 同步键盘并补发锁定键（Caps/Num/Scroll）
- 证据：src/input/seat.c:21-51
- 细节：无硬件键盘时先用空 rules 编译 keymap 并 `wlr_keyboard_set_keymap`（:25-29）；:31 `wlr_seat_set_keyboard`；:34-44 通过 seat_feed_keyboard_key 补发 KEY_CAPSLOCK/KEY_NUMLOCK/KEY_SCROLLLOCK。

### F-R3-031 — seat 提供合成输入 API（feed motion/button/axis/key），供动作系统与外部调用注入事件
- 证据：src/input/seat.c:443-482
- 细节：seat_feed_pointer_button→cursor_feed_button（:455）后 `wlr_seat_pointer_notify_frame`（:457，外部符号 wlr）；seat_feed_keyboard_key 在 seat 自有键盘无物理设备时遍历 seat->keyboards 选一个非空 group 发送（:472-481）。

### F-R3-032 — 全部输入事件先过 input_event_filter：该过滤器先通知 idle_manager_notify_activity，再调用可安装的 event_filter_func_t（event_filter 由 input_manager_set_event_filter 设置）
- 证据：src/input/input.c:1003-1026
- 细节：封装 struct input_event { seat, input, type, event }（:1018-1023）；类型枚举见 include/input/input.h:19-56（INPUT_EVENT_KEYBOARD_KEY=100 分段）。

## keyboard 与 xkb

### F-R3-033 — 物理 wlr_keyboard 的 key/modifiers 信号接 keyboard_handle_key/keyboard_handle_modifiers，内部维护按下 keysym 列表（上限 MAX_PRESSED_KEY=10）
- 证据：src/input/keyboard.c:396-427、473-476；include/input/keyboard.h:10-17
- 细节：keycode→keysym 用外部符号 xkb `xkb_state_key_get_syms(wlr_keyboard->xkb_state, key + 8, &keysyms)`（keyboard.c:166，+8 为 evdev 偏移）；keyboard_state_add_key 去重且上限 10（:107-115）。

### F-R3-034 — 修饰名表支持 11 个名称到 WLR_MODIFIER_* 位的映射（Shift/Caps/Ctrl/Alt/Num/Mod3/Win/Logo/Mod5 等），匹配用 strcasecmp
- 证据：src/input/keyboard.c:20-45
- 细节：重复名 “Ctrl” 与 XKB_MOD_NAME_CTRL 都映射 WLR_MODIFIER_CTRL（:26-27），“Win”/XKB_MOD_NAME_LOGO→WLR_MODIFIER_LOGO（:32-33），XKB_MOD_NAME_NUM→WLR_MODIFIER_MOD2（:30）。

### F-R3-035 — VT 切换在 keysym 解析阶段拦截：XKB_KEY_XF86Switch_VT_1..12 调 input_manager_switch_vt 并返回 false 中止后续处理
- 证据：src/input/keyboard.c:173-179；input_manager_switch_vt src/input/input.c:1055-1069
- 细节：:176 `input_manager_switch_vt(keysym - XKB_KEY_XF86Switch_VT_1 + 1)`；input.c:1065 外部 session 符号 `session_change_vt`。

### F-R3-036 — keyboard_feed_key 的消费优先级：IME 注入键直发 wlr_seat → 绑定匹配 → grab（可 bypass）→ bindings_handle_key_binding → IME 处理 → wlr_seat_keyboard_notify_key
- 证据：src/input/keyboard.c:269-348
- 细节：:282-286 keyboard_is_from_input_method 时仅 set keyboard + notify key 后 return；:313 bypass 位 KEY_BINDING_BYPASS_GRAB；:331 `bindings_handle_key_binding`；:341 `input_method_handle_key`；:346-347 外部符号 `wlr_seat_set_keyboard`+`wlr_seat_keyboard_notify_key`。

### F-R3-037 — seat keyboard_key 信号携带 consumed 标志：VT 切换、激活的 inhibitor、命中 binding、binding_state 同键均记为 consumed
- 证据：src/input/keyboard.c:294-303
- 细节：struct seat_keyboard_key_event.consumed 字段见 include/input/seat.h:76-82。

### F-R3-038 — 按键重复由合成器自管 wl_event_loop timer：delay 取 wlr_keyboard->repeat_info.delay，周期 1000/rate，仅物理键盘创建 timer
- 证据：src/input/keyboard.c:205-245、429-444、468-471
- 细节：keyboard_create 中 `if (!keyboard->is_virtual)` 才 `wl_event_loop_add_timer(..., keyboard_handle_repeat, keyboard)`（:468-470，外部符号 wl）；repeat 回调先排队下次再 keyboard_feed_key pressed（:435-441）。

### F-R3-039 — xkb keymap 用 xkb_context_new(XKB_CONTEXT_NO_SECURE_GETENV) + xkb_keymap_new_from_names 按 rules/model/layout/variant/options 编译；keymap 缓存于 input_manager.keymaps 链表，首个默认 keymap 编译通过 queue_add_job 异步预热
- 证据：src/input/keyboard.c:673-687；src/input/input.c:738-808
- 细节：struct keymaps_rules 五字段见 include/input/input.h:58-64；input.c:806 `queue_add_job(server->queue,..., compile_keymap,NULL)`，失败则同步 compile_keymap（:807）；缓存比较 keyboard_check_keymap_rules（:746）；失败日志 “Keymap compile failed, text input is broken”（:757）。

### F-R3-040 — 新键按下时若物理键盘的 keymap/repeat 变化，会先 seat_remove_input 再重加，以适配 keyboard group
- 证据：src/input/input.c:893-919（_input_set_state）
- 细节：:906-910 条件 `!input->prop.is_virtual && wlr_keyboard->group && (keymap_changed||repeat_info_changed)`；:914 外部符号 `wlr_keyboard_set_keymap`，:917 `wlr_keyboard_set_repeat_info`。

### F-R3-041 — modifiers 事件先给 bindings_handle_key_binding_modifiers（松修饰即结束绑定），再给 IME，最后发 seat 信号与 wlr_seat
- 证据：src/input/keyboard.c:350-374
- 细节：:366 `input_method_handle_modifiers(keyboard)` 返回 true 则吞掉；:369 发 seat->events.keyboard_modifiers；:373 外部符号 `wlr_seat_keyboard_notify_modifiers`。

### F-R3-042 — keyboard_get_key_binding 在有 activated_inhibitor、或非按下且非“纯修饰释放”时不找绑定；按下带 ACTIVE/INACTIVE/REPEAT 选项，释放仅 INACTIVE
- 证据：src/input/keyboard.c:184-203
- 细节：trigger_options 组合见 :198-201。

## keyboard_group

### F-R3-043 — 物理键盘按 keymap_string 与 repeat_info 归组：同 keymap 同 rate/delay 的设备加入同一 keyboard_group，虚拟键盘不入组
- 证据：src/input/keyboard.c:481-538
- 细节：比较 keyboard_keymaps_match（用外部字段 wlr_keyboard.keymap_string 字符串比较，:639-651）；空组复用并 set_keymap/set_repeat_info（:514-525）；否则 keyboard_create(seat,NULL) 新建组（:528）。

### F-R3-044 — keyboard_group 是名为 “keyboard-group” 的自定义 wlr_keyboard_impl，带按键引用计数去重、修饰/keymap/repeat 同步
- 证据：src/input/keyboard_group.c:58-85、87-152
- 细节：外部符号 `wlr_keyboard_init(&group->keyboard, &impl, "keyboard_group")`（:71）；process_key 用 keyboard_group_key 计数，同键重复按下不入组键盘（:97-105）；handle_keyboard_key 仅在 process_key 返回 true 时 `wlr_keyboard_notify_key(&group->keyboard,...)`（:130-132）。

### F-R3-045 — 组 LED 更新会强制 scroll lock 状态并同步到所有成员设备；scroll_lock 计数保存在 group（值 2 为按下过渡）
- 证据：src/input/keyboard_group.c:35-56；src/input/keyboard.c:247-267
- 细节：keyboard_update_lock 仅处理 KEY_SCROLLLOCK，pressed 时 group->scroll_lock=2 并置 WLR_LED_SCROLL_LOCK（keyboard.c:258-260），注释说明用于绕过 wlr_keyboard_led_update 检查（:263）。

### F-R3-046 — keyboard_group_pick_keyboard 优先返回组内首个物理设备，组空时返回组键盘自身；keyboard_send_key 通过它注入合成键
- 证据：src/input/keyboard_group.c:340-348；src/input/keyboard.c:591-608

## IME 注册点（input-method/text-input/virtual-keyboard）

### F-R3-047 — input-method v2 全局由 wlr 实现创建：wlr_input_method_manager_v2_create(server->display)
- 证据：src/input/text_input.c:843
- 细节：外部符号（wlroots）`wlr_input_method_manager_v2_create`；manager 字段 `struct wlr_input_method_manager_v2 *input_method`（text_input.c:28）。

### F-R3-048 — text-input v3 全局为合成器自有实现，text_input_manager_v3_create 内 wl_global_create 注册 zwp_text_input_manager_v3_interface，version 1
- 证据：src/input/text_input.c:844；src/input/text_input_v3.c:280-296（:292 wl_global_create）
- 细节：接口实现表 `static const struct zwp_text_input_manager_v3_interface text_input_manager_impl`（text_input_v3.c:248）。

### F-R3-049 — text-input v2 全局同为自有实现，wl_global_create 注册 zwp_text_input_manager_v2_interface，version 1
- 证据：src/input/text_input.c:845；src/input/text_input_v2.c:285-296（:296）
- 细节：`zwp_text_input_manager_v2_interface`（text_input_v2.c:296）。

### F-R3-050 — text-input v1 全局同为自有实现，wl_global_create 注册 zwp_text_input_manager_v1_interface，version 1；注释说明 v1 的 create_text_input 请求不带 seat
- 证据：src/input/text_input.c:847-848；src/input/text_input_v1.c:283-294（:294）
- 细节：注释原文 “no seat in text_input_v1 create_text_input request”（text_input.c:847）。

### F-R3-051 — virtual-keyboard 全局由 wlr 实现创建：wlr_virtual_keyboard_manager_v1_create(server->display)，new_virtual_keyboard 信号接 handle_new_virtual_keyboard
- 证据：src/input/input.c:823-826
- 细节：外部符号（wlroots）；input_p.h:64 字段类型 `struct wlr_virtual_keyboard_manager_v1 *virtual_keyboard`。

### F-R3-052 — 每个 seat 在 new_seat 时创建独立 input_method_relay，挂接 input_method v2、text_input v2/v3 的 new/destroy 信号；text_input v1 由 manager 统一挂接
- 证据：src/input/text_input.c:785-818、849-852
- 细节：relay 保存 text_inputs/input_popups 链表（:796-797）并写入 seat->relay（:798）。

### F-R3-053 — 键盘焦点变化经 seat_focus_surface→input_method_set_focus 下发到 IME 中继
- 证据：src/input/seat.c:439；src/input/text_input.c:878（input_method_set_focus 定义）
- 细节：text_input_match_surface 按 wl_client 相等匹配 v3/v2，v1 另要求 surface 相等（text_input.c:863-876，外部符号 wl_resource_get_client）。

### F-R3-054 — 来自 IME 的键在 keyboard_feed_key 入口识别后直接转发 wlr_seat，不走绑定；普通键在绑定未命中后交给 input_method_handle_key/handle_modifiers
- 证据：src/input/keyboard.c:281-286、341-344、366-368；text_input.c:924-951
- 细节：keyboard_is_from_input_method 定义 text_input.c:951；input_method keyboard grab 处理 handle_input_method_grab_keyboard text_input.c:549-560。

### F-R3-055 — IME 候选/弹出表面（input_popup）作为场景节点接入输入分发，实现 hover/click/leave 与 get_root 回调
- 证据：src/input/text_input.c:618-650、650-684
- 细节：input_popup_hover/click/leave 见 :618/:626/:632；input_event_node 由 input/event.h:24-64 定义；handle_new_popup_surface :650。

## cursor 与软件光标 quirks

### F-R3-056 — cursor_create 创建 wlr_cursor 并 attach output_layout，挂接 wlr_cursor 的 motion/absolute/button/axis/frame、swipe/pinch/hold begin-update-end、touch up/down/motion/cancel/frame、tablet tool axis/proximity/tip/button 共 21 个信号，以及 wlr_seat 的 request_set_cursor
- 证据：src/input/cursor.c:892-971
- 细节：外部符号（wlroots）：`wlr_cursor_create`（:899）、`wlr_cursor_attach_output_layout`（:911）；信号注册区间 :921-966。

### F-R3-057 — 指针设备通过 wlr_cursor_attach_input_device 挂到 seat 光标；触摸默认映射到主输出
- 证据：src/input/cursor.c:1025-1035；src/input/input.c:403-407
- 细节：input_create 中 touch 设备默认 `state.mapped_to_output = primary->name`（input.c:404-406）；移除调 `wlr_cursor_detach_input_device`（cursor.c:1034）。

### F-R3-058 — 运动事件链：cursor_handle_motion→cursor_feed_motion（先发 relative_pointer，再应用 constraint，cursor_move，pointer_grab，最后 _cursor_feed_motion 做场景命中与 hover/leave 分发）
- 证据：src/input/cursor.c:288-301、129-149、74-123
- 细节：外部符号 `wlr_relative_pointer_manager_v1_send_relative_motion`（:132）；场景命中 `scene_node_at(&seat->scene->tree.node, lx, ly, &sx,&sy)`（:63-64）；hover 回调 inode->impl->hover（:109）；无子节点时 cursor_set_image(CURSOR_DEFAULT)+seat_notify_leave（:115-122）。

### F-R3-059 — 按钮事件链：cursor_handle_button→cursor_feed_button：先发 seat cursor_button 信号，再交给 pointer_grab，再更新 focus 节点并分发 inode->impl->click，双击判定窗口 double_click_time
- 证据：src/input/cursor.c:317-330、183-286
- 细节：双击条件 `!changed && button==last_button && time-last_click_time < double_click_time`（:264-266）；CLICK_STATE_DOUBLE/FOCUS_LOST/NONE 定义 include/input/event.h:10-17；wlr_seat 有 grab 时仅 seat_notify_button（:211-214）。

### F-R3-060 — cursor_image 名称表实测 35 项（"none" 起始，含 default/pointer/wait/各方向 resize/zoom-in 等），与 cursor_name 枚举一一对应
- 证据：src/input/cursor.c:32-39；include/input/cursor.h:12-57；脚本计数 `cursor_image count: 35`
- 细节：设置图像调外部符号 `wlr_cursor_set_xcursor(cursor->wlr_cursor, cursor->xcursor_manager, cursor_image[name])`（cursor.c:1056），CURSOR_NONE 调 `wlr_cursor_unset_image`（:1054）。

### F-R3-061 — xcursor 主题取自环境变量 XCURSOR_THEME/XCURSOR_SIZE，缺省回落 seat 配置；seat 默认配置 cursor_size 24
- 证据：src/input/cursor.c:913-919；src/input/seat.c:164
- 细节：cursor_set_xcursor_manager 调外部符号 `wlr_xcursor_manager_create(theme,size)`（cursor.c:877），变化时 cursor_rebase（:879）并发 cursor_configure 信号（:889）。

### F-R3-062 — 客户端光标表面（set_cursor 请求）受 image_locks/hidden/grab/焦点 client 校验；XWayland 客户端的光标表面做 unscale 并监听 client_commit 修正几何
- 证据：src/input/cursor.c:835-851、807-833、775-795
- 细节：xwayland_check_client 为真时 hotspot 经 `xwayland_unscale`（:813-814），commit 回调按 1/scale 缩放 pending width/height/damage/dx/dy（:785-794）。

### F-R3-063 — pointer constraint（locked/confined）自有完整状态机：active/pending 两槽，按区域检查激活，LOCKED 直接吞运动，CONFINED 用 wlr_region_confine 裁剪
- 证据：src/input/cursor.c:1179-1430
- 细节：外部符号 `wlr_pointer_constraints_v1_constraint_for_surface`（:1426）、`wlr_region_confine`（:1348）、`wlr_pointer_constraint_v1_send_activated/deactivated`（:1240,:1205）；生命周期 ONESHOT 常量 `ZWP_POINTER_CONSTRAINTS_V1_LIFETIME_ONESHOT`（:1278）。

### F-R3-064 — 软件光标 quirk 位为 QUIRKS_MASK_SOFTWARE_CURSOR(1<<1)，命中表含 nouveau、virtio_gpu(Mesa Project)、vmwgfx、linlondp(ARM)
- 证据：include/util/quirks.h:10-22；src/util/quirks.c:28-38
- 细节：quirks 表条目原文：`{ "nouveau", NULL, QUIRKS_MASK_SOFTWARE_CURSOR | QUIRKS_MASK_DISABLE_CTM }`、`{ "virtio_gpu", "Mesa Project", ...|QUIRKS_MASK_EXPLICIT_SYNC }`、`{ "vmwgfx", NULL, ... }`、`{ "linlondp", "ARM", ... }`。

### F-R3-065 — 软件光标的消费点：output 初始化按 output->quirks 调 wlr_output_lock_software_cursors(true)；fbdev 后端恒锁；截图/zoom 效果临时加解锁
- 证据：src/output/output.c:661-662；src/backend/fbdev/fbdev.c:616；src/effect/capture.c:410,673,965；src/effect/zoom.c:551,577
- 细节：外部符号 `wlr_output_lock_software_cursors`；场景侧 `scene_render_target_add_software_cursors`（src/scene/render.c:207、src/scene/output.c:331）。

### F-R3-066 — 轴事件应用 per-device scroll_factor，并对相同 time_msec 做 “fix zwcada2023 crash” 兼容补发 frame
- 证据：src/input/cursor.c:353-374
- 细节：:363 注释原文 “workaround to fix zwcada2023 crash”；delta/discrete 均乘 input->state.scroll_factor（:372-373，roundf）；axis 分发优先 inode->impl->axis，否则 `wlr_seat_pointer_notify_axis`（:342-350）。

### F-R3-067 — cursor 支持触摸/tablet 工具模拟鼠标：touch down 合成 BTN_LEFT 按下并隐藏光标；tablet tip 合成 BTN_LEFT、tablet 按键合成 BTN_RIGHT
- 证据：src/input/cursor.c:535-642、394-533
- 细节：touch down：cursor_set_hidden(true)（:571）+ cursor_feed_button(BTN_LEFT,true)（:581）；tip up 时补一次 tip 上报注释 “workaround to send a tool-tip up”（:473-474）。

### F-R3-068 — cursor_rebase_all 遍历所有 seat，在非 grab、无按键时按场景节点一致性决定是否 rebase；workspace 切换与 view map 后均调用
- 证据：src/input/cursor.c:1094-1126；src/view/workspace.c:700；src/view/view.c:709
- 细节：注释指出 ssd 等节点销毁导致 hover 为 NULL 时也需 rebase（cursor.c:1112-1115）。

## pointer / touch / tablet / gesture

### F-R3-069 — 触摸点管理在 touch.c：touch_handle_down 找 surface、处理 grab、wlr_seat_touch_notify_down；motion/up/cancel 对应 wlr_seat_touch_*；多点触发展发 touchscreen 手势
- 证据：src/input/touch.c:542-642、747-916
- 细节：外部符号 `wlr_seat_touch_has_grab`（:567）、`wlr_seat_touch_notify_down/motion/up/cancel`（:578,:626,:796,:889,:916）、`wlr_seat_touch_point_focus`（:792,:856）；手势 gesture_state_update(SWIPE/PINCH, GESTURE_DEVICE_TOUCHSCREEN)（:812,:819）。

### F-R3-070 — 触摸边缘由 touch_calc_edge 计算，touch_gesture_begin 以该 edge 开始 gesture_state；touch_reset_gesture 供 grab 取消
- 证据：src/input/touch.c:110-219、352-376
- 细节：touch_manager_create 在 :386（input.c:853 调用）；touch 自己的 gesture_state 初始化 :349。

### F-R3-071 — seat_cancel_touch_points 在 touch grab 启动时取消不属该 grab serial 的触点
- 证据：src/input/touch.c:920-…；调用点 src/input/seat.c:358

### F-R3-072 — tablet v2 全局由 wlr 创建 wlr_tablet_v2_create(display)；工具/pad 按输入设备创建 wlr_tablet_v2_tablet(_tool/_pad)
- 证据：src/input/tablet.c:396、133-153、185-201、311-335
- 细节：外部符号（wlroots）：:149 `wlr_tablet_tool_create`、:201 `wlr_tablet_create`、:328 `wlr_tablet_pad_create`；pad 事件转发 `wlr_tablet_v2_tablet_pad_notify_mode/button/strip/ring`（:267-306）。

### F-R3-073 — 手势状态机四阶段 BEFORE/TRIGGER/AFTER/STOP：swipe 超阈值触发，touchpad 阈值 10、touchscreen 0.15；hold/tap 用 timer（默认 200ms、touchpad 20/1ms、触屏 hold 800ms）
- 证据：src/input/gesture.c:14-27、49-165、210-244
- 细节：常量 GESTURE_DEFAULT_TIMEOUT=200、GESTURE_TOUCHPAD_TIMEOUT=20、GESTURE_TOUCHPAD_TAP_TIMEOUT=1、GESTURE_TOUCHSCREEN_HOLD_TIMEOUT=800（:14-17）；阈值 :25-27；pinch 方向阈值 min_rotation=5、min_scale_delta=0.1（:52-53）。

### F-R3-074 — 手势触发/跟随/停止均调 bindings_handle_gesture_binding，handled 状态影响是否向客户端取消（pointer_gestures 协议）
- 证据：src/input/gesture.c:106、135、151、293-296；src/input/cursor.c:644-773
- 细节：cursor_handle_swipe_end 发外部符号 `wlr_pointer_gestures_v1_send_swipe_end(..., cancelled || handled)`（cursor.c:690-691），pinch/hold 同理（:740,:772）。

### F-R3-075 — touchpad 三类 wlr 手势在 cursor.c 转成 gesture_state（SWIPE/PINCH/HOLD，设备固定 GESTURE_DEVICE_TOUCHPAD，edge NONE），同时转发 wlr_pointer_gestures_v1
- 证据：src/input/cursor.c:644-773
- 细节：begin 调 gesture_state_begin（如 :654-655），update 调 gesture_state_update（:670-671），end 调 gesture_state_end（:687-688）。

## binding 快捷键解析

### F-R3-076 — 快捷键字符串语法：以 “+” 连接修饰与键名，可追加 “:no” 后缀关闭重复触发；键名经 xkb_keysym_from_name(CASE_INSENSITIVE) 解析并统一转小写
- 证据：src/input/binding.c:237-291
- 细节：:255 先按 “:” split，第二段 == "no" 时清 KEY_BINDING_TRIGGER_IN_REPEAT（:256-258）；:262 按 “+” split；:275 外部符号 xkb `xkb_keysym_from_name`，:276 `xkb_keysym_to_lower`。

### F-R3-077 — bindings 按 KEY_BINDING_TYPE_NUM 个 keysyms_binding 桶与 GESTURE_DEVICE_COUNT 个 gesture 组组织，位图 keysyms_binding_masks 快速跳过被整类屏蔽的类型
- 证据：src/input/binding.c:67-81、475-496
- 细节：键绑定注册入桶 :389-394，类型无锁时置位 mask；查询 bindings_get_key_binding 先看 mask（:517-520）。

### F-R3-078 — key_binding_table 给出 20 个类型名字符串（含尾项 WLCOM_ALL），供 kywc_key_binding_type_by_name 解析配置
- 证据：src/input/binding.c:128-153
- 细节：字符串如 "WLCOM_SWITCH_WORKSPACE"（:135）、"WLCOM_WINDOW_ACTION_CLOSE"（:138）、"WLCOM_ALL"（:152）；未知名回落 KEY_BINDING_TYPE_CUSTOM_DEF（:1338）。

### F-R3-079 — 键绑定匹配条件：类型桶启用、绑定未被 block、options 含触发位、last_modifiers 精确相等、keysym 在按下列表中；无 keysym 的绑定（纯修饰）需 modifier_only_released
- 证据：src/input/binding.c:498-556
- 细节：match_key_binding 遍历 pressed_keysyms 比较 `xkb_keysym_to_lower`（:502）；修饰判定 `keyboard_state->last_modifiers ^ binding->info.modifiers`（:533）。

### F-R3-080 — 键绑定有 ACTIVE/REPEAT/INACTIVE 三阶段回调，bindings_handle_key_binding 负责激活、重复、失活的完整状态推进
- 证据：src/input/binding.c:586-649；枚举 include/kywc/binding.h:106-117
- 细节：ACTIVE 回调 :634，REPEAT :617，INACTIVE（释放）:598；keyboard_binding_state 记录当前 binding/key/active_emitted（include/input/keyboard.h:19-25）。

### F-R3-081 — 手势字符串语法 `<type>:<device>:<fingers>:<direction>[:edge][:stages][:follow_threshold][:follow_directions]`，段数 4-8
- 证据：src/input/binding.c:849-936
- 细节：type 取词 tap/hold/pinch/swipe（:873-888，tap 在无 HAVE_LIBINPUT_RAW_TAP 时退化为 HOLD，:874-878）；device 取 touch/touchpad（:8891-898）；direction 词 none/up/down/left/right/inward/outward/clockwise/counterclockwise（:766-799）；edge 词 top/bottom/left/right（:801-820）；stage 词 before/trigger/after/stop（:822-847）。

### F-R3-082 — 手势合法性规则：pinch 至少 2 指且不能带 edge；touchpad tap 至少 3 指；touchpad 普通 swipe 至少 3 指；触屏单指 swipe 必须带 edge；触屏边缘 swipe 方向须与 edge 相对
- 证据：src/input/binding.c:938-985
- 细节：逐条 if 判定，非法返回 false 并记录 “Gesture checks are illega”（:1014，源码原文拼写）。

### F-R3-083 — 手势身份 id 由 device/fingers/type/direction/edge 位域打包（GESTURE_ID_* 位移宏），同组内 id 唯一才允许注册
- 证据：src/input/binding.c:987-999、1044-1068；位域 include/kywc/binding.h:31-41
- 细节：edge 4 位（shift0）、direction 8 位（shift4）、type 4 位（shift12）、fingers 4 位（shift16）、device 4 位（shift20）。

### F-R3-084 — 绑定支持三级 block：全部键绑定 keysym_bindings_block、按类型 type_nlocks、单绑定 nblocks；手势支持单绑定与按设备 block
- 证据：src/input/binding.c:1277-1320、1228-1262
- 细节：block_all 首次为 1 时对全部类型发 cancel（:1281-1284）；block_type 操作 mask 与 type_nlocks（:1292-1307）。

### F-R3-085 — 绑定 desc 全局唯一：注册前 is_key_binding_desc_unique 跨所有类型检查，(modifiers,keysym) 也做冲突告警但不阻止同 desc 场景
- 证据：src/input/binding.c:214-235、353-374
- 细节：冲突日志格式 “Keybind %s(%s) is already registered by %s(%s)”（:365）。

## action 动作表

### F-R3-086 — 内置动作类型枚举 action_type：NONE/DBUS_ACTION/RUN_COMMAND/SEND_BUTTON/SEND_KEY；按键动作 PRESS(1)/RELEASE(2)/CLICK(3)
- 证据：src/input/action.c:23-41
- 细节：DBUS 总线类型 dbus_type：SESSION/SYSTEM（:39）；input_type：KEYBOARD/GESTURE（:37）。

### F-R3-087 — 动作配置来自名为 “InputAction” 的 config（JSON 键 keyboards/gestures），并在 D-Bus 路径 /com/kylin/Wlcom/InputAction 接口 com.kylin.Wlcom.InputAction 注册 ListAllActions 方法
- 证据：src/input/action.c:163-164、562-566、764-771
- 细节：SD_BUS_METHOD("ListAllActions","","a(ss)",...)（:564）；JSON actiontype 取值 "dbus"/"command"/"button"/"key"（:493-501）。

### F-R3-088 — SEND_KEY 动作按 modifiers 先按、keys 再按、反向顺序释放；SEND_BUTTON 先合成移动再按下释放并 leave
- 证据：src/input/action.c:299-336
- 细节：键码串支持 ":press"/":release" 后缀（:211-217）；seat_feed_keyboard_key/seat_feed_pointer_button 为注入入口。

### F-R3-089 — 内置键码表 31 项（a-z、Tab、Super_L/R、Alt_L/R、方向键、Shift/Control 左右），按键名 strcasecmp 匹配；鼠标码表 5 项 left/right/middle/back/forward
- 证据：src/input/action.c:110-161
- 细节：如 { "Super_L", KEY_LEFTMETA }（:141）、{ "Tab", KEY_TAB }（:140）；btncode_maps 含 BTN_LEFT/RIGHT/MIDDLE/BACK/FORWARD（:159-160，外部符号 linux/input-event-codes.h）。

### F-R3-090 — 内置快捷键仅 1 条："Win:no" → desc "ukui_menu_show" → FUNC_ID_SHOW_UKUI_MENU
- 证据：src/input/action.c:949-955、957-973
- 细节：builtin_actions_create 注册时回调统一为 function_manager_handle_key_binding（:969）。

### F-R3-091 — 内置手势表实测 13 条，覆盖触屏 1/3/4 指 hold/swipe、touchpad 1 指边缘滑动（亮度/进度/音量）、3 指 tap/swipe、4 指 tap
- 证据：src/input/action.c:773-947；脚本计数 `input builtin gestures entries: 13`
- 细节：示例 desc 字符串："touchpad_(3)fingers_swipe_left"→FUNC_ID_WINDOWS_SWITCH_BACKWARD（:869-870）、"touchscreen_(1)fingers_hold"→FUNC_ID_SIMULATE_RIGHTBTN（:796-797）、"touchpad_(4)fingers_tap"→FUNC_ID_SHOW_UKUI_SIDEBAR（:932-933）；touchpad 边缘 1 指 follow_threshold=50.0，触屏 3 指为 0.15。

### F-R3-092 — 配置型绑定（FUNC_ID_CONFIG）的键/手势绑定在 action.c 内创建并注册，注册失败的用户配置项会从 JSON 删除
- 证据：src/input/action.c:632-648、715-731、734-762
- 细节：user=true 时 `json_object_object_del(keyboard_obj,keybind)`（:642）/gesture_obj（:725）；系统配置 sys_json 先读，用户 json 后读（:742-760）。

### F-R3-093 — function 总表 functions[] 为每个 FUNC_ID 给出 (func_id, key_binding_type, desc, l10n_name) 四元组，desc 为英文短语
- 证据：src/input/function.c:491-~890
- 细节：示例 {FUNC_ID_SWITCH_LEFT_WORKSPACE, KEY_BINDING_TYPE_SWITCH_WORKSPACE, "Switch to Left Workspace", NULL}（:528-533）；FUNC_ID_CONFIG→KEY_BINDING_TYPE_CUSTOM_CONFIG/"Custom Configure Function"（:510-515）。

### F-R3-094 — function 多语言表 function_translation[FUNC_ID_COUNT][LANG_COUNT] 提供各功能本地化名称
- 证据：src/input/function.c:33-489
- 细节：:30-31 D-Bus 路径/接口常量 "/com/kylin/Wlcom/FunctionManager"、"com.kylin.Wlcom.FunctionManager"；ListFunctions 方法 :1090-1118、vtable :1118-1122。

### F-R3-095 — 键功能总分发 function_manager_handle_key_binding：FUNC_ID_CONFIG→input_action；FUNC_ID_CUSTOM→global_shortcuts；SWITCH_*WORKSPACE→workspace_manager；窗口/桌面类→view_manager；滤镜/缩放→effect_manager；UKUI 菜单/亮度→D-Bus
- 证据：src/input/function.c:1336-1403
- 细节：:1358 workspace_manager_handle_function；:1383 view_manager_handle_function；:1389 effect_manager_handle_function；:1392 ukui_menu_show（D-Bus "org.ukui.menu" "/org/ukui/menu" "WinKeyResponse"，:1164-1167）。

### F-R3-096 — 手势功能总分发 function_manager_handle_gesture_binding 额外处理 windows switch（合成 Alt+Tab 序列）、媒体键、侧边栏、全局搜索、模拟三键等
- 证据：src/input/function.c:1405-1526
- 细节：ukui_windows_switch_internal 在 TRIGGER 阶段按下 KEY_LEFTALT（+LEFTSHIFT）并 KEY_TAB，AFTER 发方向键，STOP 松 Alt（:1293-1322）；媒体动作用 D-Bus 调 org.ukui.SettingsDaemon MediaKeys.externalDoActionWithName（:1172-1179），动作字符串如 "VOLUME_UP_KEY"/"BRIGHT_UP_KEY"（:1214,:1246）。

### F-R3-097 — 全局快捷键/全局手势并非 Wayland 协议全局，而是基于 D-Bus 名称占用（org.freedesktop.DBus NameOwnerChanged match）的会话机制
- 证据：src/input/global_shortcuts.c:1218-1220；src/input/global_gestures.c:214-216
- 细节：match 规则字符串含 "sender='org.freedesktop.DBus'...interface='org.freedesktop.DBus'..."；配置名分别为 "Shortcuts"（global_shortcuts.c:1511）与 "Gestures"（global_gestures.c:614）。

## data_device 与 primary_selection / DND

### F-R3-098 — wl_data_device_manager 为合成器自有实现，DATA_DEVICE_MANAGER_VERSION=3，于 selection_manager_create 时 wl_global_create
- 证据：src/input/data_device.c:24、1500、1524；src/input/selection.c:322
- 细节：:1524 `wl_global_create(display, &wl_data_device_manager_interface, 3, ...)`（外部 wayland 接口）；selection_manager_create 同函数还创建 primary selection、data control、toplevel drag（selection.c:322-325）。

### F-R3-099 — data_source 抽象带安全闸门 allow_read/allow_drop/allow_write/allow_start_drag，拖放动作经 dnd_drop/dnd_finish/dnd_action 回调
- 证据：src/input/data_device.c:93-233；include/input/data_device.h:14-48、124-156
- 细节：struct data_source_impl 回调 send/accept/destroy/dnd_drop/dnd_finish/dnd_action/client（data_device.h:38-48）。

### F-R3-100 — DnD 在合成器内实现 pointer/keyboard/touch 三套 grab 接口，drag_create 后由 grab 把 motion/button/touch 事件转为拖放焦点与 drop
- 证据：src/input/data_device.c:996-1247、1249-1301
- 细节：drag_handle_pointer_motion 调 drag_set_focus（:1009,:774）；drag_drop :1033；touch grab 接口 drag_handle_touch_down/motion/up/enter/cancel（:1107-1169）；drag_icon_create :963。

### F-R3-101 — zwp_primary_selection_device_manager_v1 为合成器自有实现，wl_global_create version 1
- 证据：src/input/primary_selection.c:605；src/input/selection.c:323
- 细节：manager 内引用外部符号 `wlr_primary_selection_v1_device_manager`（primary_selection.c:571）作接口适配；源类型 struct primary_selection_source（include/input/seat.h:90）。

### F-R3-102 — zwlr_data_control_manager_v1 自有全局 version 1；xdg_toplevel_drag_manager_v1 自有全局 version 1
- 证据：src/input/wlr_data_control.c:751；src/input/toplevel_drag.c:219-226
- 细节：toplevel_drag 接口字符串 `xdg_toplevel_drag_manager_v1_interface`（toplevel_drag.c:226）。

### F-R3-103 — selection 子系统为每个 seat 挂接 request/start_drag 与 wlr_seat keyboard focus_change（注释修正 wlr_seat_keyboard_enter 的 selection 发送）
- 证据：src/input/selection.c:280-305
- 细节：:302 注释原文 “fix seat_client_send_selection in wlr_seat_keyboard_enter”；selection_handle_cursor_move 在光标移动中更新拖放（selection.c:336，调用点 cursor.c:113）。

### F-R3-104 — 另有 org_kde_kwin_idle、ext_idle_notifier_v1、org_kde_kwin_keystate、ext_transient_seat_manager_v1 等全局
- 证据：src/input/idle.c:361-368；src/input/kde_keystate.c:317；src/input/transient_seat.c:153
- 细节：idle_inhibit 用外部 wlr `wlr_idle_inhibit_v1_create`（src/input/idle_inhibit.c:175）。

## view/toplevel 状态机

### F-R3-105 — kywc_view 状态字段：mapped/minimized/maximized/fullscreen/activated/tiled/kept_above/kept_below/sticky/skip_taskbar/skip_switcher/demands_attention/modal；角色枚举 16 种（NORMAL 到 AUTHENTICATION）
- 证据：include/kywc/view.h:46-64、117-211
- 细节：角色含 KYWC_VIEW_ROLE_DESKTOP/PANEL/ONSCREENDISPLAY/NOTIFICATION/TOOLTIP/.../INPUTPANEL/SCREENLOCK/WATERMARK/APPLETPOPUP/SWITCHER/AUTHENTICATION（:46-64）；能力位 12 个（:87-101），宏判定 IS_MINIMIZABLE/MAXIMIZABLE/CLOSEABLE 等（:71-85）。

### F-R3-106 — view 派生结构含 surface/tree/surface_tree、parent/children、view_proxies（多工作区）、saved geometry/tiled/output、pending configure、icon_name、interactive_moving 等
- 证据：include/view/view.h:104-196
- 细节：view_configure_state 含 action/geometry/configure_serial/configure_timeout（:88-97）；enum view_action 位掩码 ACTIVATE/FULLSCREEN/MAXIMIZE/RESIZE/TILE/MINIMIZE/MOVE（:67-76）。

### F-R3-107 — view 实现接口 view_impl 含 ping/configure/close_popups/close/destroy/configure_timeout/update_usable_area/get_icon_buffer 共 8 个回调；xdg 与 xwayland 各有一份 impl
- 证据：include/view/view.h:198-208；src/view/xdg_shell.c（xdg_view 系列）；src/xwayland/view.c:334（xwl_surface_impl）
- 细节：xwayland 侧 const struct view_impl xwl_surface_impl（xwayland/view.c:334）。

### F-R3-108 — view_init 在 view_manager.views 插入视图、在 LAYER_NORMAL 层建树（默认 disable）、设定初始 output、角色置 NORMAL 并发 new_view 信号
- 证据：src/view/view.c:375-446
- 细节：:425-428 scene_tree_create + scene_node_set_enabled(false)；:430 input_current_output 取初始输出；:445 发 view_manager->events.new_view。

### F-R3-109 — view_map 状态机：发 premap → 模式 view_map 钩子 → enable 树节点（非 minimized）→ mapped=true → pending configure → 设输出 → activate → set_focus → 圆角 → map/new_mapped_view 信号 → view_enter → 取消 show-desktop → cursor_rebase_all
- 证据：src/view/view.c:621-710
- 细节：:633 `scene_node_set_enabled(&view->tree->node, !minimized)`；:635 mapped=true；:654 kywc_view_activate；:656 view_set_focus；:692/:693 发 map 与 new_mapped_view；:695-698 对每个 proxy 发 workspace->events.view_enter。

### F-R3-110 — xdg toplevel map 由 wlr xdg_surface map 信号触发 xdg_view_handle_map → view_map；map 时集中挂 request_move/resize/minimize/maximize/fullscreen/show_window_menu/set_parent/set_title/set_app_id 信号
- 证据：src/view/xdg_shell.c:537-584
- 细节：外部符号 wlr：wlr_xdg_toplevel_set_fullscreen/maximized/tiled/size（xdg_shell.c:180-208）、wlr_xdg_toplevel_send_close（:125）。

### F-R3-111 — view 的指针输入经 input_event_node_impl 接入：xdg_view_hover/click/leave，click 调 seat_notify_button 后 view_click
- 证据：src/view/xdg_shell.c:54-114
- 细节：input_event_node_create 把场景节点与 impl 绑定（src/input/event.c:16-37），node data 向上查找逻辑 input_event_node_from_node（event.c:39-50）。

### F-R3-112 — view_click/view_hover 转发给当前 view_mode（stack_mode/tablet_mode）；stack_mode 下按下即 kywc_view_activate + view_set_focus
- 证据：src/view/view.c:2711-2724；src/view/stack_mode.c:197-206、254-273
- 细节：view_mode_interface 含 view_click/view_hover 等 14 个钩子（src/view/view_p.h:16-48）；stack_mode_impl.name = "stack_mode"（stack_mode.c:255）。

### F-R3-113 — view_do_activate→view_set_activated 链路驱动 wlr 焦点与 layer 重排；view_set_focus 最终 seat_focus_surface(seat, view->surface)
- 证据：src/view/view.c:1470-1552、1684-1706
- 细节：view_set_focus 有全局认证视图拦截（:1690-1693）、模态后代替换（:1695-1698）、FOCUSABLE 能力检查（:1700），随后 seat_focus_surface + view_send_ping（:1704-1705）。

### F-R3-114 — tiled/maximized/fullscreen/minimized 状态变更均有 do_* 实现并发出对应 kywc_view 事件；几何优先走 view_manager.impl（mode 钩子）
- 证据：src/view/view.c:1708-1953；事件字段 include/kywc/view.h:159-210
- 细节：view_get_tiled_geometry 处理 NONE/CENTER/ALL 与 8 方向，并回调 view_manager->impl.get_tiled_geometry（view.c:448-488）；KYWC_TILE_* 枚举见 include/kywc/view.h:24-36。

### F-R3-115 — 窗口动作总分发 window_action 覆盖 21 个 WINDOW_ACTION：最小化/最大化/关闭（直接调 kywc_view_*），MOVE/RESIZE 移光标并 window_begin_*，菜单仅 SSD title 非全屏时显示，贴靠/half-screen/跨输出/截图各自处理
- 证据：src/view/action.c:250-317
- 细节：WINDOW_ACTION_MENU 条件 `kywc_view->ssd & KYWC_SSD_TITLE && !fullscreen`（:287）；跨屏 view_send_to_output 在 fullscreen/modal 时直接返回（:200）。

### F-R3-116 — function_id→window_action 映射表 view_manager_get_window_action 覆盖 16 个 FUNC_ID（最大化/最小化/关闭/菜单/截图/8 贴靠/4 跨屏）
- 证据：src/view/action.c:336-376
- 细节：未命中返回 WINDOW_ACTION_NONE（:374）；view_manager_handle_window_action 限定 NORMAL/AUTHENTICATION 角色，认证视图只允许 CLOSE（:319-334）。

### F-R3-117 — view 层（layer）枚举 18 层，从 DESKTOP 到 ON_SCREEN_DISPLAY，INPUT_PANEL(12) 专放 IME 表面；焦点变化时 view_manager_update_input_panel_layer 抬升该层
- 证据：include/view/view.h:20-59；src/view/view.c:1657-1682
- 细节：workspace 内仅建 BELOW/NORMAL/ABOVE 三棵子树（src/view/workspace.c:566-575）；层名注释标注 kwin layer 来源（view.h:19）。

### F-R3-118 — 窗口内置快捷键 16 条（window_shortcuts[]）：Alt+F10/F9/F4/F3、win+方向贴靠、win+alt+方向半屏、win+shift+方向跨屏、ctrl+shift+方向跨屏最大化
- 证据：src/view/action.c:28-50；脚本计数 16
- 细节：desc 字符串如 "window_maximized"/"window_closed"/"window_tile_top"/"window_send_left_maximize"（:33-49）；window_actions_create 注册（:475-492）。

### F-R3-119 — view_manager 内置快捷键 6 条与手势 8 条：win+d/h/m/g/shift+m/home 桌面操作；3/4 指 touchpad/touchscreen 上下滑出多任务/显桌面
- 证据：src/view/action.c:494-505、507-615、617-652
- 细节：键如 { "win+d:no", "desktop_toggle_visibility", FUNC_ID_TOGGLE_DESKTOP_VISIBILITY }（:499）；手势 desc "touchpad_(3)fingers_swipe_up"→FUNC_ID_MULTI_TASKVIEW（:528-529）。

### F-R3-120 — SSD 枚举 KYWC_SSD_NONE/TITLE(1)/BORDER(2)/RESIZE(4)/ALL=7；圆角半径取自 theme->window_radius，有 SSD title 时去顶部圆角
- 证据：include/kywc/view.h:38-44；src/view/view.c:510-541
- 细节：csd_round_corner 配置关闭时要求 ssd != NONE 才圆角（view.c:531-533）；全屏/最大化/tiled 不圆角（:530）。

### F-R3-121 — 特殊 view 功能（显桌面/多任务/最大化遍历/平板任务栏/贴靠手势）在 view_manager_handle_special_function 先行处理
- 证据：src/view/view/action.c:390-460
- 细节：FUNC_ID_MULTI_TASKVIEW 通过 D-Bus 调 org.kylin.switch /MultitaskView show/hide（:52-58）；maximize_switcher_show（:417）。

## workspace 与虚拟桌面

### F-R3-122 — MAX_WORKSPACES=15；工作区结构含 uuid/name/3 个 layer/view_proxies/position/activated 与 6 个信号
- 证据：include/view/workspace.h:10、19-43
- 细节：view_proxy 同时挂 view 与 workspace 两条链表并持有挂载 scene_tree（:45-55）。

### F-R3-123 — workspace_manager 持有 current、workspaces 数组、count/rows/columns，默认 rows=2，列数按 count/rows 向上取整
- 证据：src/view/workspace.c:24-42、415-444、370-379
- 细节：workspaces 数组分配大小 MAX_WORKSPACES（:423）；workspace_manager_update_count：columns=ceil(count/rows)（:372-378）。

### F-R3-124 — 默认工作区数量为 4，配置键为 "num_workspaces" 与 "workspace_names"，配置名 "Views"
- 证据：src/view/view.c:2980（num_workspaces=4）；src/view/config.c:358、373-381、465-467
- 细节：server ready 时先创建并激活第 0 个，再按 state.num_workspaces 建其余（workspace.c:404-413）；无名时用 tr("Desktop")+position+1（workspace.c:505-507）。

### F-R3-125 — workspace_create 建 3 棵 layer 子树（BELOW/NORMAL/ABOVE），角色 SCENE_ROLE_WORKSPACE，默认 disable，position 插入并移位后续工作区，生成 uuid
- 证据：src/view/workspace.c:541-594
- 细节：达 MAX_WORKSPACES 拒绝创建（:544）；插入后对 i 移位并更新 position（:579-585）；发 new_workspace 信号并 auto_add sticky 视图（:589-591,:514-527）。

### F-R3-126 — workspace_activate：旧工作区失活（disable 树、重挂 proxy）、关 show-desktop、置 current、激活顶层 view、cursor_rebase_all、发 active_workspace
- 证据：src/view/workspace.c:660-703
- 细节：view_activate_topmost(true)（:698）；日志 “Workspace %s(%d) is activated”（:702）。

### F-R3-127 — 工作区切换快捷键 8 条：Ctrl+Alt+Left/Right、Win+ctrl+Left/Right、Ctrl+F1..F4；F1-F4 在代码内映射为 switch_to(4..7)→position 0..3
- 证据：src/view/workspace.c:46-59、81-106、304-321
- 细节：注释 “add ctrl+f1...f4 to workspace”，`pending = switch_workspace - 4`（:93）；方向边界由 workspace_manager_can_switch_direction 判定（:61-79）。

### F-R3-128 — 4 指左右滑动（touchpad/touchscreen）切换工作区，4 阶段全启用（BEFORE|TRIGGER|AFTER|STOP），id 为 SWITCH_LEFT/RIGHT_WORKSPACE_GESTURE
- 证据：src/view/workspace.c:108-168
- 细节：touchpad 位移除以 300.0，触屏除以 1.0（:183,:187）；阈值常量 TRANSLATION_THRESHOLD=0.35、边缘回缩系数 0.2（:21-22）。

### F-R3-129 — workspace_manager_handle_function 支持新建/删除工作区：删除仅在 count>1 时删最后一个；新建在 count 位置
- 证据：src/view/workspace.c:289-333
- 细节：FUNC_ID_NEW_WORKSPACE→workspace_create(NULL, count)（:297）；DEL 先 workspace_by_position(count-1)（:300-301）。

### F-R3-130 — 工作区删除时 fix_workspace 修正后续 position/名字、激活相邻工作区，并把视图全部迁到激活工作区
- 证据：src/view/workspace.c:596-658
- 细节：视图迁移 view_add_workspace + view_set_current_proxy + view_proxy_destroy（:621-628）。

### F-R3-131 — 同时提供 ky_workspace（自有 kywc 协议）与 kde plasma virtual desktop 两套工作区对外协议
- 证据：src/view/workspace.c:437-439
- 细节：ky_workspace_manager_create（:437）；kde_virtual_desktop_management_create 受 HAVE_KDE_VIRTUAL_DESKTOP 条件保护（:439，桩定义 view_p.h:241-249）；协议 XML 见 protocols/plasma-virtual-desktop.xml、protocols/kywc-workspace-v1.xml（文件名枚举自 protocols/ 目录）。

## widget 机制

### F-R3-132 — widget 是挂在 scene_tree 下的自绘 scene_buffer 封装：widget_create(parent) 建树，绘制经 painter_draw_buffer(buffer) 用 struct draw_info 描述
- 证据：src/widget/widget.c:20-65、487-501；include/widget/widget.h:10-17
- 细节：draw_info 字段含 solid_rgba/hover_rgba/border/corner/text/shortcut/font/align 等（widget.c:22-46）；重绘 painter_buffer_redraw（:50）。

### F-R3-133 — widget 支持文本/快捷键/字体/对齐、hover/enabled、固定/最大尺寸、auto_resize、背景/前景/hover 色、边框、圆角、透明度、模糊等属性 API
- 证据：include/widget/widget.h:17-54；src/widget/widget.c:207-443
- 细节：hover 图像利用 buffer 上下半区（widget_buffer_get_size 中 y=scaled_h/2，widget.c:74-79）。

### F-R3-134 — menu 由 menu_item 链表 + 子菜单构成，root menu show/hide 时持有 pointer/keyboard/touch 三类 grab
- 证据：include/widget/menu.h:18-121；src/widget/menu.c:1081-1121
- 细节：struct menu 含 pointer_grab/keyboard_grab/touch_grab（menu.h:75-77）；item 动作回调签名 `bool (*action)(struct menu_item*, uint32_t key, void *data)`（:35）；ITEM_TYPE_NORMAL/FLIP_UP/FLIP_DOWN（:12-16）。

### F-R3-135 — menu 支持阴影/模糊装饰（scene_decoration）、超出输出翻转项（flip_up/flip_down）、淡入淡出开关、主题更新重绘
- 证据：include/widget/menu.h:43-68；src/widget/menu.c:1097（menu_set_fade_enabled）
- 细节：menu 带 theme_update/output_disable 监听（menu.h:59-61）。

## XWayland 启动与 xwm

### F-R3-136 — xwayland_manager_create 受 server->options.enable_xwayland 门控；创建 xwayland_shell_v1 并加 security 全局过滤（仅 XWayland client 可见）；options lazy/enable_wm/terminate_delay
- 证据：src/xwayland/xwayland.c:71-130
- 细节：:84 eavesdrops_key_mode 默认 ALL_KEYS_WITH_MODIFIER；:88 xwayland_shell_v1_create；:95 security_add_global_filter；:97-101 `{.lazy=lazy_xwayland,.enable_wm=true,.terminate_delay=lazy?10:0}`。

### F-R3-137 — XWayland server ready 后 xwm_create(wm_fd[0]) 并 xwm_set_seat(seat0)；start 时把 shell v1 client 绑定为 XWayland client；环境变量 DISPLAY 被 setenv 为 display_name
- 证据：src/xwayland/xwayland.c:37-56、116-122
- 细节：:40 `xwayland_shell_v1_set_client(...server->client)`（外部 wlr 符号）；:120 setenv("DISPLAY",...)。

### F-R3-138 — Xwayland 子进程 argv 固定含 -rootless -core -terminate，listenfd 两套（HAVE_XWAYLAND_LISTENFD），-displayfd 通知，-wm 传 WM fd，可选 -auth/-noTouchPointerEmulation/-force-xrandr-emulation
- 证据：src/xwayland/server.c:45-109
- 细节：WAYLAND_SOCKET 经 setenv 传入（:113-115）；Xwayland 路径可由环境变量 KYWC_XWAYLAND 覆盖（server.c:135）；XWAYLAND_PATH 编译期默认 /usr/bin/Xwayland（meson.build:21,27）。

### F-R3-139 — server 采用两次 fork + displayfd 读就绪管道；XAUTHORITY 由 generate_xauthority_file 生成并 setenv；支持 lazy 重启
- 证据：src/xwayland/server.c:253-325、392-434、472-518
- 细节：:509-511 生成 xauthority 并 setenv("XAUTHORITY")，失败 unsetenv（:514）；进程退出后 lazy 时 server_start_lazy 重启（:225-227）。

### F-R3-140 — xwm_create：xcb_connect_to_fd(wm_fd)、wl_event_loop_add_fd 挂 x11_event_handler、取 atoms/shape/xfixes/sync/xres 扩展、root 窗事件掩码、composite manual 重定向、写 _NET_SUPPORTED、条件开 xfixes terminate 模式
- 证据：src/xwayland/xwm.c:3202-3289
- 细节：事件掩码 SUBSTRUCTURE_NOTIFY|SUBSTRUCTURE_REDIRECT|PROPERTY_CHANGE（:3251-3255）；:3257-3258 `xcb_composite_redirect_subwindows(...XCB_COMPOSITE_REDIRECT_MANUAL)`；xfixes>=6 且 terminate_delay>0 时 set_client_disconnect_mode TERMINATE（:3283-3287）。

### F-R3-141 — xwm 初始化三个 selection：CLIPBOARD、PRIMARY、XdndSelection；创建 WM 窗口（持有 WM_S0/_NET_WM_CM_S0 selection owner）、no_focus 窗口、guard 窗口
- 证据：src/xwayland/xwm.c:3293-3295、2937-2962、3169-3200、3314-3316
- 细节：WM 窗口名 "wlcom wm"（:2939），guard 窗口名 "wlcom guard window"（:3196）；_NET_SUPPORTING_WM_CHECK 互相指向（:2950-2956）。

### F-R3-142 — xwm 监听 compositor new_surface 与 xwayland shell new_surface，并挂 max_scale、active_workspace、activate_view 三个外部变化
- 证据：src/xwayland/xwm.c:3297-3312
- 细节：view 激活到 wayland 窗口时清 X11 焦点（xwm_handle_activate_view，:3153-3167）。

### F-R3-143 — x11_event_handler 是 X11 事件总分发：selection 事件优先，然后 shape/sync alarm、create/destroy/configure/map/unmap/property/client_message/focus_in/reparent/error
- 证据：src/xwayland/xwm.c:2306-2378
- 细节：xwm_handle_selection_event 先于其它（:2321）；map request :2348、map_notify :2351、unmap :2354、property :2357、client_message :2360、focus_in :2363。

### F-R3-144 — atom_map 实测覆盖约 90 个 X11 atom，分 NET_SUPPORTED/NET_WM_STATE/WM 协议/窗口类型/startup/stacking/selection/Xdnd/sync 等组，每个 atom 可挂 surface_property/client_message/net_wm_state 三类处理器
- 证据：src/xwayland/xwm.c:2622-2784；解析 xwm_get_atoms :2786-2812
- 细节：窗口类型含 _NET_WM_WINDOW_TYPE_DESKTOP/DOCK/.../NOTIFICATION/NORMAL 与 UKUI 私有 _UKUI_NET_WM_WINDOW_TYPE_SYSTEMWINDOW/INPUTPANEL/LOGOUT/SCREENLOCK/WATERMARK（:2726-2731）。

### F-R3-145 — _NET_WM_STATE 12 个状态双向同步：modal/fullscreen/max_vert/max_horz/hidden/sticky/skip_taskbar/above/below/demands_attention/skip_switcher/focused，状态变化写 _NET_WM_STATE 属性
- 证据：src/xwayland/xwm.c:215-260、1820-2008
- 细节：xsurface_set_net_wm_state 组属性数组（:215-260）；client message 动作 REMOVE(0)/ADD(1)/TOGGLE(2)（:1792-1818）。

### F-R3-146 — _NET_WM_MOVERESIZE 9 个方向码映射到 resize/move，CANCEL(11) 取消交互
- 证据：src/xwayland/xwm.c:1724-1790
- 细节：宏 _NET_WM_MOVERESIZE_SIZE_TOPLEFT=0…MOVE=8、CANCEL=11（:1724-1735）。

### F-R3-147 — XWayland 视图自有 view_impl（xwl_surface_impl）与 input_event_node_impl（hover/click/leave/get_root/get_toplevel），请求 move/resize/minimize/maximize/fullscreen/activate/sticky/above/below 等 1:1 映射 view_mode 钩子
- 证据：src/xwayland/view.c:23-100、334-344、525-663
- 细节：xwayland_view_click 同样调 view_click（:65-75）；view_surface_request_move :564。

### F-R3-148 — XWayland 整屏缩放：xwm->scale 取 output_manager_get_max_scale；xwayland_scale/unscale 用 256 定点整数运算；XWayland 客户端光标 surface 与 workarea 均做缩放
- 证据：src/xwayland/xwayland.c:158-188、199-213；src/xwayland/xwm.c:3112-3134
- 细节：xwm_update_xresources 写 Xft.dpi=scale*96、Xcursor.size/theme 到 RESOURCE_MANAGER（xwm.c:3038-3055）。

### F-R3-149 — xwm 通过 Xres（xcb_res ≥1.2）读取客户端 PID（_NET_WM_PID 之外的通道），ping 超时 10000ms
- 证据：src/xwayland/xwm.c:74-99、2882-2906、3220；xwayland_get_pid_from_wlr_surface src/xwayland/xwayland.c:215-226
- 细节：ping_timeout=10000（:3220）；ping 仅对支持 _NET_WM_PING 的窗口发送（xwayland_surface_ping :3437-3464）。

### F-R3-150 — override-redirect 窗口由 unmanaged.c 处理，restack 对 OR 窗口跳过且避免越过最顶层受管窗口；guard_window 作为层叠底锚
- 证据：src/xwayland/xwm.c:3325-3369；src/xwayland/unmanaged.c（文件存在，meson.build:69）
- 细节：注释 “X11 clients expect their override_redirect windows to stay on top”（xwm.c:3338-3339）。

### F-R3-151 — 键窃听（eavesdrops）支持模式 NONE_KEYS 与 ALL_KEYS_WITH_MODIFIER（默认），并保证转发给 Xwayland 的按下键一定收到释放
- 证据：src/xwayland/eavesdrops.c:23-24、140-204；src/xwayland/xwayland.c:84
- 细节：注释原文 “keycodes that have been forwarded to Xwayland and are still pressed. Their release events must always be forwarded to keep Xwayland's …”（eavesdrops.c:23-24）；eavesdrops_manager_create 于 xwm_create 末调用（xwm.c:3320）。

### F-R3-152 — _NET_WORKAREA 由 output_layout_get_workarea 经 xwayland_scale 后写单屏工作区；_NET_SHOWING_DESKTOP 与 wm changestate 等 client message 均有处理器
- 证据：src/xwayland/xwayland.c:199-213；src/xwayland/xwm.c:3505-3523、2055-2165
- 细节：xwm_set_workareas 每区 4 个 uint32（x,y,w,h）（:3505-3522）。

### F-R3-153 — Java 兼容：root 窗 _NET_WM_NAME 写 "LG3D"，注释说明 wlcom 非 reparenting WM 的空白窗 workaround
- 证据：src/xwayland/xwm.c:2918-2929
- 细节：注释原文 “workaround to fix java apps show blank window / wlcom is not a reparenting window manager / or set _JAVA_AWT_WM_NONREPARENTING=1”。

## xwm 窗口映射与选择/DND

### F-R3-154 — map_request/map_notify/unmap_notify 驱动 xwayland_surface 的受管状态与 withdrawn；property_notify 集中分派各 atom 处理器
- 证据：src/xwayland/xwm.c:1613-1672
- 细节：withdrawn 时按 EWMH 删除 _NET_WM_STATE（xwayland_surface_set_withdrawn :1595-1611，注释 :1600）。

### F-R3-155 — xwm selection 初始化对 CLIPBOARD/PRIMARY/XdndSelection 设三类 xfixes selection event mask；选择事件统一入口 xwm_handle_selection_event
- 证据：src/xwayland/selection/selection.c:153-220
- 细节：mask 为 SET_SELECTION_OWNER|SELECTION_WINDOW_DESTROY|SELECTION_CLIENT_CLOSE（:215-217）；xwm_selection_finish 三选择在 xwm_destroy 收尾（xwm.c:2539-2541）。

### F-R3-156 — Wayland↔X11 选择双向桥：incoming（X11→Wayland，含 INCR）、outgoing（Wayland→X11）；data_source_is_xwayland/primary_selection_source_is_xwayland 判定来源
- 证据：src/xwayland/selection/incoming.c:162、245、330、484、568；src/xwayland/selection/outgoing.c:64、161、388、511
- 细节：xwm_handle_xfixes_selection_notify（incoming.c:568）；xwm_send_incr_chunk（outgoing.c:161）；xwm 销毁时清理 X11 来源的 seat selection（xwm.c:2546-2554）。

### F-R3-157 — Xdnd 协议在 dnd.c 实现：client message 入口 xwm_handle_selection_client_message，Wayland 拖入 X 窗时 start_drag 挂接，含 dnd status/position/enter/leave/drop/finished 发送
- 证据：src/xwayland/selection/dnd.c:264、510、532、610-714
- 细节：日志字符串 “Wayland drag dropped over an Xwayland window”（:510）、“Wayland drag cancelled over an Xwayland window”（:532）；xwm_seat_handle_start_drag :610；xwm_send_dnd_status/finish :687/:714。

## theme 加载

### F-R3-158 — 主题配置名 "theme"，D-Bus 路径 /com/kylin/Wlcom/Theme、接口 com.kylin.Wlcom.Theme
- 证据：src/theme/config.c:13、97-101
- 细节：config_manager_add_config("theme")（:97）+ dbus_register_object（:101）。

### F-R3-159 — struct theme 含亮/暗类型、激活/非激活边框/背景/文字色、双层 shadow、modal mask、渐变状态色、字体、accent、窗口/菜单圆角、opacity(0-100)、button_width/icon_size/title_height 等
- 证据：include/theme.h:103-161
- 细节：THEME_MAX_SHADOW_LAYERS=2（:10）；theme_type DEFAULT(LIGHT)=0/DARK=1（:17-22）；更新掩码 11 位（:45-69）。

### F-R3-160 — UKUI 主题 token 目录固定 /usr/share/config/theme/token
- 证据：src/theme/ukui_theme.c:57
- 细节：#define THEME_DIR 字符串原样；同文件负责把颜色转 SVG path 字符串（:209,:226 等 fprintf 模式）。

### F-R3-161 — 图标搜索路径 ICONPATH/APPPATH/PIXMAPPATH 含 ~/.icons、/usr/share/icons、~/.local/share/applications、/usr/share/applications、/usr/share/pixmaps；fallback 主题名 "hicolor"，图标用 hash_table 缓存（普通表上限 2000，fallback 200）
- 证据：src/theme/icon.c:24-28、549-550；src/theme/theme_p.h:10
- 细节：ICONPATH="~/.icons:~/.local/share/icons:/usr/share/icons:" EXTRA_ICON_PATH（icon.c:24）；hash_table_set_max_entries(icons, name?2000:200)（:550）；inotify 监听 hicolor 变化 handle_hicolor（:477）。

### F-R3-162 — 12 种主题按钮类型（最小化/最大化/还原/关闭 × 正常/hover/clicked），buffer 经 theme_button_buffer_load 获取
- 证据：include/theme.h:30-43、185-187

## util 基础设施

### F-R3-163 — spsc_chain 提供 create/destroy/push/pop 四 API，链式无锁 SPSC，元素定长、容量固定、溢出在 head 挂新节点
- 证据：include/util/spsc_chain.h:22-30；消费方 src/backend/libinput/input_queue.h:153-175 与 backend.c:158（命令链）

### F-R3-164 — queue 是线程池作业队列：queue_create(max_jobs,num_threads,global_data)、queue_add_job(queue,job,fence,execute)、queue_fence_init/wait/finish；keymap 预热即经此提交
- 证据：include/util/queue.h:12-45；调用 src/input/input.c:806

### F-R3-165 — dbus 封装基于 sd-bus，同时打开 system 与 user 总线；提供 call_method/call_methodv（session）、call_system_method(v)、notify、match/信号、对象注册
- 证据：include/util/dbus.h:20-56；src/util/dbus.c:106-110（sd_bus_open_system/sd_bus_open_user）、208
- 细节：外部符号 libsystemd `sd_bus_open_system`（dbus.c:106）、`sd_bus_open_user`（:110）。

### F-R3-166 — spawn 系列：spawn_shell/spawn_invoke 经 fork+"/bin/sh -c" 执行；spawn_dialog 返回 fd 走 JSON 请求；spawn_client 建 wl_client
- 证据：include/util/spawn.h:15-27；src/util/spawn.c:46、64、120
- 细节：argv[] = { "/bin/sh", "-c", command, NULL }（spawn.c:46）；双 fork 模式（:44,:88,:176）。

### F-R3-167 — dialog 工具在 socket fd 上收发 JSON（dialog_send_request/dialog_close/dialog_get_reply）
- 证据：include/util/dialog.h:11-13；src/util/dialog.c:17、117、126

### F-R3-168 — 动画系统支持三种缓动类型 FUNCTION/BEZIER/HERMITE，内置 quad/cubic in/out/inout 6 个函数；animtr 按 elapsed_time 推进多 channel
- 证据：include/util/anim.h:11-84

### F-R3-169 — hash_table 支持 pointer/string/int 三类键，自定义 hash/equal，带容量上限与逐 entry 遍历
- 证据：include/util/hash_table.h:11-55；使用方 src/theme/icon.c:549

### F-R3-170 — matrix 提供 mat3（3x3）恒等/缩放/平移/乘/旋转/翻转与 framebuffer、logic→ndc、output transform 求逆等几何工具
- 证据：include/util/matrix.h:13-67；vec2 几何辅助在 include/util/vec2.h（文件存在，24 个 util 公开头之一）

### F-R3-171 — 时间工具 current_time_msec/current_time_nsec/timespec_diff_usec/usec_to_msec，事件循环包装 event_loop_create/add_fd/dispatch
- 证据：include/util/time.h:11-20；include/util/event.h:8-25
- 细节：event.h:8-13 自有 enum 事件掩码（非 wl 事件循环）。

### F-R3-172 — quirks 共 11 位：MASTER_FD/SOFTWARE_CURSOR/EXPLICIT_SYNC/NO_MODIFIERS/EGL_WAYLAND/PREFER_OPENGL/DISABLE_DIRECT_SCANOUT/DISABLE_GAMMA/DISABLE_CTM/YUYV_MODE/PREFER_DRM_DUMB，按 backend(renderer) 与 vendor 两条路径查询
- 证据：include/util/quirks.h:10-26
- 细节：消费跨 src/output、src/backend/fbdev、src/effect（见 F-R-065）。

### F-R3-173 — 其余 util：string_split/string_create 等字符串工具（绑定解析大量使用）、file 工具（XDG 图片目录/配置解析/目录遍历）、client 安全信息（pid/uid/gid/comm，client.h:10-26）、identifier（uuid/md5/base64/时间命名，identifier.h:8-42）、limit（nofile/cloexec）、nls、color、debug_backtrace、drm_format、wayland 辅助
- 证据：include/util/string.h、include/util/file.h:11-42、include/util/client.h、include/kywc/identifier.h:17-41、include/util/limit.h:10-14、include/util/{nls,color,debug,drm_format,wayland}.h
- 细节：file_get_xdg_pictures_dir 被窗口截图保存路径使用（src/view/action.c:124）。

## 完整事件链（端到端）

### F-R3-174 — 【键盘链·一句话】libinput 线程 handle_keyboard_key 入 SPSC 队列 → 主线程 dispatch_input_events 发 wlr_keyboard key → keyboard_handle_key/keyboard_feed_key 匹配 bindings → function_manager_handle_key_binding → workspace_manager_handle_function 或 view_manager_handle_function/window_action 改变 view/workspace
- 证据（逐跳函数名+行号）：
  - src/backend/libinput/keyboard.c:56 `handle_keyboard_key` → :73 `queue_input_event`
  - src/backend/libinput/events.c:397-406 case INPUT_EVENT_KEYBOARD_KEY → 外部符号 `wlr_keyboard_notify_key`
  - src/input/keyboard.c:396 `keyboard_handle_key` → :413 `keyboard_feed_key`（:269）
  - src/input/keyboard.c:190 `keyboard_get_key_binding` → src/input/binding.c:510 `bindings_get_key_binding`
  - src/input/binding.c:634（ACTIVE 阶段）调用注册 action = src/input/function.c:1336 `function_manager_handle_key_binding`
  - 工作区：src/input/function.c:1358 `workspace_manager_handle_function` → src/view/workspace.c:289（:305 switch_to）→ :81 `workspace_manager_switch_to` → :104 `workspace_activate`
  - 窗口：src/input/function.c:1383 `view_manager_handle_function` → src/view/action.c:462 → :319 `view_manager_handle_window_action` → :250 `window_action` → 外部 API `kywc_view_set_minimized/toggle_maximized/close`（:259-265）
- 细节：注册回调的绑定点：view/action.c:485-486、workspace.c:345-346、input/action.c:638-639 均把 `function_manager_handle_key_binding` 作为 binding->action。

### F-R3-175 — 【指针链·一句话】libinput POINTER_BUTTON 入队 → 主线程发 wlr_pointer.button → wlr_cursor 汇聚后 cursor_handle_button→cursor_feed_button 做场景命中并调节点 click → xdg_view_click→view_click→stack_mode_view_click→kywc_view_activate/view_set_focus→seat_focus_surface→wlr_seat 焦点
- 证据（逐跳函数名+行号）：
  - src/backend/libinput/events.c:258 case LIBINPUT_EVENT_POINTER_BUTTON→handle_pointer_button（src/backend/libinput/pointer.c）→ queue；events.c:429-437 INPUT_EVENT_POINTER_BUTTON→`wl_signal_emit_mutable(&dev->pointer.events.button,...)`+frame
  - 设备挂载：src/input/cursor.c:925 wlr_cursor events.button→`cursor_handle_button`（cursor.c:317）
  - src/input/cursor.c:328 `cursor_feed_button`（:183）→ :272-275 `inode->impl->click(...)`
  - src/view/xdg_shell.c:82 `xdg_view_click` → :88 `view_click`
  - src/view/view.c:2711 view_click→ mode 钩子 → src/view/stack_mode.c:197 `stack_mode_view_click` → :203 `kywc_view_activate`、:204 `view_set_focus`
  - src/view/view.c:1684 view_set_focus → :1704 `seat_focus_surface` → src/input/seat.c:406（:428 `wlr_seat_keyboard_notify_enter`，:439 input_method_set_focus）
- 细节：hover 路径并行存在：cursor.c:299 cursor_feed_motion→:148 _cursor_feed_motion→:109 inode->impl->hover=xdg_view_hover（xdg_shell.c:54）→ seat_notify_motion（:66）→ wlr_seat_pointer_notify_enter/motion（seat.c:374-385）。

### F-R3-176 — 【手势链·一句话】libinput GESTURE_SWIPE_* 入队 → wlr_pointer 手势信号 → cursor_handle_swipe_* 调 gesture_state_begin/update/end → gesture_state_trigger 调 bindings_handle_gesture_binding → function_manager_handle_gesture_binding → view/workspace 变化或合成 Alt+Tab/媒体 D-Bus
- 证据（逐跳函数名+行号）：
  - src/backend/libinput/events.c:312-335（handle_pointer_swipe_*→queue；dispatch :506-545 发 pointer.events.swipe_*）
  - src/input/cursor.c:644 `cursor_handle_swipe_begin` → :654 `gesture_state_begin`；:660 update→:670 `gesture_state_update`；:677 end→:687 `gesture_state_end`
  - src/input/gesture.c:106/:135/:151 `bindings_handle_gesture_binding`（定义 src/input/binding.c:1070）→ :1140 binding->action
  - action= src/input/function.c:1405 `function_manager_handle_gesture_binding` → :1426 workspace_manager_handle_function 或 :1455 view_manager_handle_function；:1460 ukui_windows_switch_by_shortcut（:1293 合成键序列）
- 细节：未被合成器消费的手势继续发客户端协议 wlr_pointer_gestures_v1_send_swipe/pinch/hold（cursor.c:656,690-691 等）。

## 疑点与矛盾

### D-R3-01 — view 簇文件计数与任务书基线差 1
- 证据：F-R3-002/F-R3-004 实测 src/view 顶层 37 .c + tile/ 3 .c + view_p.h = 41 个 C 源/头；任务书基线为 view42
- 备注：客观口径差异，可能把 src/view/tile/meson.build 或其它非 C 文件计入；本簇以实测 41 个 C 文件为准。

### D-R3-02 — 存在两套同名 enum input_event_type / struct input_event，取值不兼容
- 证据：src/backend/libinput/input_queue.h:25-60（从 1 顺序编号，跨线程队列载荷）与 include/input/input.h:19-56（100/200/…/700 分段，过滤器事件标识）
- 备注：两者作用域不同（backend 队列 vs 合成器过滤器），同名靠分属不同翻译单元/TU 不冲突；此为源码事实，无文档说明二者关系，属阅读风险点。

### D-R3-03 — compose/dead key 未实现
- 证据：src/input/keyboard.c:80 注释 `// TODO: compose and dead key support`
- 备注：源码自述 TODO，功能缺口为客观事实。

### D-R3-04 — input_destroy 的 switch 中 KEYBOARD 分支缺 break，存在落入 default 的写法
- 证据：src/input/input.c:494-508
- 细节：case WLR_INPUT_DEVICE_KEYBOARD 结束（:507 wlr_keyboard_finish）后无 break，紧接 `default: break;`（:503-508）；当前因 default 为空无行为差异，仅记录代码事实。

### D-R3-05 — 工作区直切快捷键只有 Ctrl+F1..F4（4 个），但 MAX_WORKSPACES=15、默认数 4 且可动态新建
- 证据：src/view/workspace.c:55-58（仅 01-04）；include/view/workspace.h:10；src/view/view.c:2980
- 备注：超出 4 个的工作区只能由协议/手势切换，此为代码事实，非推断其设计意图。

### D-R3-06 — X11 atom "_KWIN_UKUI_DECORAION" 为源码自认的历史拼写错误
- 证据：src/xwayland/xwm.c:2680-2681
- 细节：注释原文 “it has been misspelled since V10”。

### D-R3-07 — global_shortcuts/global_gestures 名字易误解为 Wayland 全局，实际为 D-Bus 名称会话机制，不创建 wl_global
- 证据：src/input/global_shortcuts.c:1218-1220；src/input/global_gestures.c:214-216；全簇 grep 无对应 wl_global_create
- 备注：供协议簇核对时避免把它登记为 Wayland 协议注册点。

### D-R3-08 — 输入热路径中存在针对具体客户端的硬编码兼容处理（zwcada2023、Java LG3D）
- 证据：src/input/cursor.c:363-368（“workaround to fix zwcada2023 crash”）；src/xwayland/xwm.c:2918-2929（LG3D）
- 备注：仅记录字符串与位置，不评价其正确性。

### D-R3-09 — xdg_view_hover 中边界裁剪两行被注释掉
- 证据：src/view/xdg_shell.c:73-74
- 细节：`// sx = sx < 0 ? 0 : ...` 两行注释；记录为待确认的死代码。

### D-R3-10 — “软件光标 quirks” 的真正执行点不在 input 簇而在 output/fbdev/effect；input 簇内仅见 XWayland 客户端光标 surface 与 axis 的两处 workaround
- 证据：src/output/output.c:661-662；src/backend/fbdev/fbdev.c:616；src/util/quirks.c:28-38；src/input/cursor.c:363-368、775-833
- 备注：quirks 表本身在 util 簇，跨簇事实，供 R2/R4 簇串联。
