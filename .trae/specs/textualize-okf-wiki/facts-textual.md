---
source: external/dao/action/Textualize/textual/src/textual/
stage: R（事实采集）
generated: 2026-09-01
fact_prefix: F-T-
path_base: 相对路径基于 textual 仓库根目录（external/dao/action/Textualize/textual/）
---

# Textual 源码事实清单（R 阶段）

> 零推测事实。每条事实标注来源文件相对路径与（必要时）行号。行号为采集时点快照。

## message.py — 消息基类

- **F-T-001** `Message` 类定义于 `src/textual/message.py:23`，`__slots__ = ["_sender", "time", "_forwarded", "_no_default_action", "_stop_propagation", "_prevent"]`。
- **F-T-002** `Message` 类变量：`ALLOW_SELECTOR_MATCH: ClassVar[set[str]] = set()`、`bubble: ClassVar[bool] = True`、`verbose: ClassVar[bool] = False`、`no_dispatch: ClassVar[bool] = False`、`namespace: ClassVar[str] = ""`、`handler_name: ClassVar[str]`。（`src/textual/message.py:35-44`）
- **F-T-003** `Message.__init_subclass__(cls, bubble=True, verbose=False, no_dispatch=False, namespace=None)` 自动生成 `cls.handler_name = f"on_{name}"`；name 由类限定名经 `camel_to_snake` 拼接，深层嵌套类只保留最后两段（如 `A.B.C.D` → `C.D`）。（`src/textual/message.py:62-86`）
- **F-T-004** `Message.__post_init__` 将 `_sender` 设为 `active_message_pump.get(None)`，`time` 设为 `_time.get_time()`，并初始化 `_forwarded=False`、`_no_default_action=False`、`_stop_propagation=False`、`_prevent: set[type[Message]] = set()`。（`src/textual/message.py:50-58`）
- **F-T-005** `Message.prevent_default(prevent: bool = True) -> Message` 设置 `_no_default_action` 并返回 self；`Message.stop(stop: bool = True) -> Message` 设置 `_stop_propagation` 并返回 self。（`src/textual/message.py:131-149`）
- **F-T-006** `Message.can_replace(message: Message) -> bool` 默认返回 `False`；`Message.control` 属性默认返回 `None`；`Message.set_sender(sender) -> Self` 显式设置发送者。（`src/textual/message.py:89-129`）
- **F-T-007** `Message._bubble_to(widget)` 先将 `_no_default_action` 重置为 `False`，再调用 `widget.post_message(self)`。（`src/textual/message.py:151-158`）

## message_pump.py — 消息泵

- **F-T-008** `MessagePump(metaclass=_MessagePumpMeta)` 定义于 `src/textual/message_pump.py:115`，构造签名 `__init__(self, parent: MessagePump | None = None)`；模块异常类：`CallbackError`（:59）、`MessagePumpClosed`（:63）。
- **F-T-009** `MessagePump.set_timer(delay, callback=None, *, name=None, pause=False) -> Timer`（:378）与 `set_interval(interval, callback=None, *, name=None, repeat=0, pause=False) -> Timer`（:418）。
- **F-T-010** `MessagePump.post_message(message) -> bool`：`_closing or _closed` 时返回 False；`check_message_enabled(message)` 失败时返回 False；调用线程与 `self._thread_id` 不同时经 `loop.call_soon_threadsafe(self._message_queue.put_nowait, message)` 投递；缺少 `_prevent` 属性时抛 `RuntimeError`（提示忘记调用 `super().__init__()`）。（`src/textual/message_pump.py:860-888`）
- **F-T-011** `MessagePump._dispatch_message(message)`：`message.no_dispatch` 为真时直接返回；`isinstance(message, Event)` 走 `on_event`，否则走 `_on_message`；整个派发包裹在 `self.prevent(*message._prevent)` 上下文中。（`src/textual/message_pump.py:707-741`）
- **F-T-012** `MessagePump._get_dispatch_methods(method_name, message)` 沿 `self.__class__.__mro__` 先派发 `_decorated_handlers`（`@on` 装饰器注册），再回退到 `on_<handler_name>` 命名约定方法；`message._no_default_action` 置位时终止 MRO 遍历。（`src/textual/message_pump.py:743-800`）
- **F-T-013** `MessagePump.prevent(*message_types)` 是上下文管理器（`Generator[None, None, None]`），向 `_prevent_message_types_stack` 压入被阻止的消息类型集合。（`src/textual/message_pump.py:199`）
- **F-T-014** `MessagePump` 提供 `call_later(callback, *args, **kwargs) -> bool`（:490）、`call_next(callback, ...) -> None`（:507）、`call_after_refresh(callback, ...) -> bool`（:451）、`check_idle() -> None`（:841）、`wait_for_refresh() -> bool`（:469）。
- **F-T-015** `_process_messages_loop` 从队列取消息后，用 `message.can_replace(pending)` 合并可替代的后续消息；派发异常时调用 `self.app._handle_exception(error)` 并 break；每条消息派发后 `message_signal.publish(message)`。（`src/textual/message_pump.py:634-694`）
- **F-T-016** `MessagePump` 实例属性（`__init__`）：`_running`、`_closing`、`_closed`、`_disabled_messages: set[type[Message]]`、`_pending_message`、`_task`、`_timers: WeakSet[Timer]`、`_last_idle`、`_max_idle`、`_is_mounted`、`_next_callbacks: list[events.Callback]`、`_thread_id`、`message_signal: Signal[Message]`。（`src/textual/message_pump.py:118-146`）

## reactive.py — 响应式描述符

- **F-T-017** `Reactive(Generic[ReactiveType])` 构造签名：`__init__(default, *, layout=False, repaint=True, init=False, always_update=False, compute=True, recompose=False, bindings=False, toggle_class=None)`。（`src/textual/reactive.py:142-154`）
- **F-T-018** `reactive(Reactive)` 子类与基类唯一差异为 `init=True`（基类 `init=False`）；`var(Reactive)` 子类固定传 `layout=False, repaint=False`，签名为 `__init__(default, init=True, always_update=False, bindings=False, toggle_class=None)`。（`src/textual/reactive.py:437-502`）
- **F-T-019** `Reactive.__get__(obj, obj_type)`：`obj` 缺少 `id` 属性时抛 `ReactiveError`；对象存在 `compute_<name>` 方法时每次读取都调用该计算方法并刷新内部存储值。（`src/textual/reactive.py:290-315`）
- **F-T-020** `Reactive._set(obj, value, always=False)` 流程：依次调用 `_validate_<name>` 与 `validate_<name>`（若存在）→ 按 `toggle_class` 切换类 → 值变化（或 `always`/`always_update`）时写入内部值、调用 `_check_watchers`、按需 `_compute`、`bindings=True` 时 `refresh_bindings()`、按 `_layout/_repaint/_recompose` 标志调用 `obj.refresh(...)`。（`src/textual/reactive.py:316-369`）
- **F-T-021** 对带 `compute_<name>` 方法的 reactive 赋值抛 `AttributeError`（"reactive attributes with a compute method are read-only"）。（`src/textual/reactive.py:330-333`）
- **F-T-022** 模块级异常与工具：`ReactiveError`（:51）、`TooManyComputesError(ReactiveError)`（:55）、`Initialize(Generic)` 包装回调（:59）、`_Mutated`（:44）、`invoke_watcher(...)`（:90）、`_watch(node, obj, attribute_name, callback, *, init=True)` 将 watcher 注册到对象的 `__watchers` 字典（:505-532）。
- **F-T-023** `Reactive._initialize_reactive(obj, name)`：内部存储名为 `_reactive_{name}`；`init=True` 且存在计算方法时以计算方法结果作默认值；`toggle_class` 在初始化时按默认值真值性 `set_class`。（`src/textual/reactive.py:196-228`）

## binding.py — 按键绑定

- **F-T-024** `Binding` 是冻结 dataclass，字段：`key: str`、`action: str`、`description: str = ""`、`show: bool = True`、`key_display: str | None = None`、`priority: bool = False`、`tooltip: str = ""`、`id: str | None = None`、`system: bool = False`、`group: Group | None = None`；嵌套冻结 dataclass `Binding.Group` 含 `description: str = ""`、`compact: bool = False`。（`src/textual/binding.py:55-98`）
- **F-T-025** `Binding.parse_key() -> tuple[list[str], str]` 以 `"+"` 分割 `self.key` 返回 `(修饰键列表, 键)`；`Binding.with_key(key, key_display=None)` 经 `dataclasses.replace` 返回新绑定。（`src/textual/binding.py:100-119`）
- **F-T-026** `Binding.make_bindings(bindings)`：2/3 元组转 `Binding`（其他长度抛 `BindingError`）；逗号分隔键（如 `"j,down"`）展开为多个 `Binding`；空键抛 `InvalidBinding`；单字符键经 `_character_to_key` 转换。（`src/textual/binding.py:121-168`）
- **F-T-027** `BindingsMap` 类（:185）方法：`bind(...)`（:346）、`get_bindings_for_key(key) -> list[Binding]`（:378）、`merge(bindings)` classmethod（:255）、`apply_keymap(keymap) -> KeymapApplyResult`（:270）、`shown_keys` 属性（:336）、`from_keys` classmethod（:228）、`copy()`（:241）。
- **F-T-028** 模块异常：`BindingError`（:42）、`NoBinding`（:46）、`InvalidBinding`（:50）；`ActiveBinding` 是 NamedTuple（:171）；`KeymapApplyResult` 是 NamedTuple（:396）。

## events.py — 事件体系

- **F-T-029** `Event(Message)` 是所有事件的基类（`src/textual/events.py:39`）；`InputEvent(Event)` 是输入事件基类（:256）。
- **F-T-030** 生命周期事件均以 `bubble=False` 声明：`Load`（:66）、`Idle`（:78）、`Resize`（:100）、`Compose`（:156，verbose=True）、`Mount`（:167）、`Unmount`（:175）、`Show`（:183）、`Hide`（:191）、`Ready`（:206）。
- **F-T-031** `Key(InputEvent)`：`__slots__ = ["key", "character"]`，构造 `__init__(key: str, character: str | None)`；`character` 为 None 时取 `key if len(key) == 1 else None`；属性 `name`（`_key_to_identifier(key).lower()`）、`is_printable`、`aliases`、`name_aliases`。（`src/textual/events.py:261-316`）
- **F-T-032** `MouseEvent(InputEvent, bubble=True)` 构造参数：`widget, x, y, delta_x, delta_y, button, shift, meta, ctrl, screen_x=None, screen_y=None, style=None`；`screen_x/screen_y` 缺省时取 `x/y`。（`src/textual/events.py:331-370`）
- **F-T-033** 鼠标事件子类均声明 `bubble=True`：`MouseMove`（:572）、`MouseDown`（:581）、`MouseUp`（:590）、`MouseScrollDown`（:599）、`MouseScrollUp`（:608）、`MouseScrollRight`（:617）、`MouseScrollLeft`（:626）、`Click`（:634）。
- **F-T-034** 焦点事件：`Focus(bubble=False)`（:799）、`Blur(bubble=False)`（:821）、`AppFocus(bubble=False)`（:829）、`AppBlur(bubble=False)`（:841）、`DescendantFocus(bubble=True, verbose=True)`（:854）、`DescendantBlur(bubble=True, verbose=True)`（:871）。
- **F-T-035** 其他事件：`Timer(Event, bubble=False, verbose=True)`（:723）、`Enter(bubble=True)`（:750）、`Leave(bubble=True)`（:774）、`Paste(bubble=True)`（:888）、`ScreenResume(bubble=False)`（:912）、`ScreenSuspend(bubble=False)`（:926）、`Print(bubble=False)`（:935）、`DeliveryComplete(bubble=False)`（:963）、`DeliveryFailed(bubble=False)`（:982）、`TextSelected(bubble=True)`（:995）、`MouseCapture/MouseRelease(bubble=False)`（:215/:237）、`Callback(Event, bubble=False, verbose=True)`（:44）。

## dom.py — DOM 节点

- **F-T-036** `DOMNode(MessagePump)` 定义于 `src/textual/dom.py:135`，构造签名 `__init__(*, name=None, id=None, classes=None)`；`id` 与 `classes` 经 `check_identifiers` 校验；实例创建 `_nodes: NodeList`、`_css_styles: Styles`、`_inline_styles: Styles`、`styles: RenderStyles(self, _css_styles, _inline_styles)`、`_component_styles: dict[str, RenderStyles]`、`_bindings`（`_merged_bindings.copy()` 或空 `BindingsMap`）、`_query_one_cache: LRUCache(1024)`。（`src/textual/dom.py:188-236`）
- **F-T-037** `DOMNode.__init_subclass__(inherit_css=True, inherit_bindings=True, inherit_component_classes=True)`：沿 MRO 收集 `Reactive` 实例到 `cls._reactives`；计算 `cls._merged_bindings`、`cls._css_type_names`、`cls._computes`（以 `_compute_`/`compute_` 开头的方法名，去前缀后存集合）。（`src/textual/dom.py:565-599`）
- **F-T-038** 查询 API：`query(selector=None) -> DOMQuery`（:1397）、`query_children`（:1425）、`query_one`（:1462）、`query_one_optional`（:1548）、`query_exactly_one`（:1585）、`query_ancestor`（:1665）；selector 可为字符串或 Widget 类型。
- **F-T-039** CSS 类操作：`has_class(*class_names) -> bool`（:1728）、`set_class(add, *class_names, update=True) -> Self`（:1739）、`set_classes(classes)`（:1794）、`add_class(*class_names, update=True)`（:1817）、`remove_class(*class_names, update=True)`（:1835）、`toggle_class(*class_names)`（:1853）。
- **F-T-040** `DOMNode.set_reactive(reactive, value) -> None` 设置 reactive 值且不调用 validators 或 watchers（docstring 明示）。（`src/textual/dom.py:249-252`）
- **F-T-041** `DOMNode.watch(obj, attribute_name, callback, init=True) -> None` 监听另一对象上的 reactive 属性变化。（`src/textual/dom.py:1256-1262`）
- **F-T-042** `DOMNode._post_mount()` 调用 `Reactive._initialize_object(self)`；`get_component_styles(*names) -> RenderStyles` 在 name 不在 `_component_styles` 时抛 `KeyError`。（`src/textual/dom.py:601-631`）
- **F-T-043** 模块异常：`BadIdentifier`（:85）、`DOMError`（:105）、`NoScreen(DOMError)`（:109）；`_ClassesDescriptor`（:113）管理类集合。
- **F-T-044** `DOMNode.check_action(action, parameters) -> bool | None` 是动态动作/绑定的钩子方法。（`src/textual/dom.py:1909`）

## widget.py — Widget 基类

- **F-T-045** `Widget(DOMNode)` 定义于 `src/textual/widget.py:283`；类变量：`COMPONENT_CLASSES: ClassVar[set[str]] = set()`、`BORDER_TITLE: ClassVar[str] = ""`、`BORDER_SUBTITLE: ClassVar[str] = ""`、`ALLOW_MAXIMIZE: ClassVar[bool | None] = None`、`ALLOW_SELECT: ClassVar[bool] = True`、`FOCUS_ON_CLICK: ClassVar[bool] = True`、`BLANK: ClassVar[bool] = False`、`can_focus: bool = False`、`can_focus_children: bool = True`。（`src/textual/widget.py:310-340`）
- **F-T-046** Widget 类级 reactive 属性：`expand = Reactive(False)`、`shrink = Reactive(True)`、`auto_links = Reactive(True)`、`disabled = Reactive(False)`、`hover_style = Reactive(Style, repaint=False)`、`loading = Reactive(False)`、`virtual_size = Reactive(Size(0, 0), layout=True)`、`has_focus = Reactive(False, repaint=False)`、`mouse_hover = Reactive(False, repaint=False)`、`scroll_x/scroll_y = Reactive(0.0, repaint=False, layout=False)`、`scroll_target_x/scroll_target_y = Reactive(0.0, repaint=False)`、`show_vertical_scrollbar/show_horizontal_scrollbar = Reactive(False, layout=True)`。（`src/textual/widget.py:341-382`）
- **F-T-047** `Widget._PSEUDO_CLASSES` 字典映射 19 个伪类到 lambda：hover、focus、blur、can-focus、disabled、enabled、dark、light、focus-within、inline、ansi、nocolor、first-of-type、last-of-type、first-child、last-child、odd、even、empty。（`src/textual/widget.py:392-412`）
- **F-T-048** `Widget.refresh(*regions, repaint=True, layout=False, recompose=False) -> Self`：`recompose=True` 时置 `_recompose_required` 并 `call_next(self._check_recompose)` 后直接返回；未挂载时仅置 `_repaint_required`；挂载后清 `_layout_cache`、`repaint` 时 `_set_dirty(*regions)` 并清尺寸缓存。（`src/textual/widget.py:4324-4376`）
- **F-T-049** `Widget.mount(*widgets, before=None, after=None) -> AwaitMount`（`src/textual/widget.py:1424`）；`AwaitMount` 类定义于 `src/textual/widget.py:128`；`AwaitRemove` 定义于 `src/textual/await_remove.py:19`；`AwaitComplete` 定义于 `src/textual/await_complete.py:17`。
- **F-T-050** `Widget.remove() -> AwaitRemove`（:4378）、`Widget.focus(scroll_visible=True) -> Self`（:4579）、`Widget.blur() -> Self`（:4600）、`Widget.capture_mouse(capture=True) -> None`（:4614）、`Widget.move_child(...)`（:1610）、`Widget.compose() -> ComposeResult`（:1679）。
- **F-T-051** 滚动 API（均为 Widget 方法）：`scroll_to`（:2859）、`scroll_relative`（:2926）、`scroll_home`（:2968）、`scroll_end`（:3012）、`scroll_left`（:3080）、`scroll_right`（:3157）、`scroll_down`（:3234）、`scroll_up`（:3312）、`scroll_page_up/down/left/right`（:3389/:3422/:3455/:3490）、`scroll_to_widget`（:3525）、`scroll_to_region`（:3612）、`scroll_visible`（:3721）、`scroll_to_center`（:3780）。
- **F-T-052** `Widget.render() -> RenderResult` 默认返回 `self.label`；`get_content_width(container: Size, viewport: Size) -> int`（:1881）与 `get_content_height(container, viewport, width) -> int`（:1912）可被子类覆盖；`_get_box_model`（:1736）计算盒模型。
- **F-T-053** Widget watcher 示例：`watch_hover_style`（:1945）、`watch_scroll_x`（:1953）、`watch_scroll_y`（:1959）、`watch_has_focus`（:4086）、`watch_disabled`（:4090）。

## screen.py — 屏幕

- **F-T-054** `Screen(Generic[ScreenResultType], Widget)` 定义于 `src/textual/screen.py:148`；类变量：`AUTO_FOCUS: ClassVar[str | None] = None`（:151）、`CSS: ClassVar[str] = ""`（:159）、`CSS_PATH: ClassVar[CSSPathType | None] = None`（:165）、`COMPONENT_CLASSES = {"screen--selection"}`（:172）。
- **F-T-055** `Screen.BINDINGS`（:269-273）：`tab → app.focus_next`、`shift+tab → app.focus_previous`、`ctrl+c,super+c → screen.copy_text`，均 `show=False`。
- **F-T-056** Screen reactive 属性：`focused: Reactive[Widget | None] = Reactive(None)`（:229）、`stack_updates: Reactive[int] = Reactive(0, repaint=False)`（:232）、`maximized: Reactive[Widget | None] = Reactive(None, layout=True)`（:251）、`selections: var[dict[Widget, Selection]] = var(dict)`（:254）。
- **F-T-057** `Screen.__init__(name=None, id=None, classes=None)`：置 `_modal = False`，创建 `Compositor()`、`_dirty_widgets: set[Widget]`、`_callbacks`、`_result_callbacks: list[ResultCallback]`、`_tooltip_widget/_tooltip_timer`，并将 `CSS_PATH` 解析为相对路径列表。（`src/textual/screen.py:275-308`）
- **F-T-058** `Screen.dismiss(result=None) -> AwaitComplete`：调用 `_result_callbacks[-1]` 后执行 `self.app.pop_screen()`；设置 `pre_await` 回调，在屏幕自身消息处理器中 await 时抛 `ScreenError`。（`src/textual/screen.py:2048`）
- **F-T-059** `Screen.focus_next(selector="*") -> Widget | None`（:897）、`focus_previous(selector="*") -> Widget | None`（:914）、`get_widget_at(x, y) -> tuple[Widget, Region]`（:633）；动作：`action_copy_text`（:985）、`action_maximize`（:993）、`action_minimize`（:998）、`action_blur`（:1002）。

## app.py — 应用

- **F-T-060** `App(Generic[ReturnType], DOMNode)` 定义于 `src/textual/app.py:296`；类变量：`CSS: ClassVar[str] = ""`（:299）、`MODES: ClassVar[dict[str, str | Callable[[], Screen]]] = {}`（:361）、`DEFAULT_MODE: ClassVar[str] = "_default"`（:390）、`SCREENS: ClassVar[dict[str, Callable[[], Screen[Any]]]] = {}`（:393）、`AUTO_FOCUS: ClassVar[str | None] = "*"`（:396）、`ALLOW_SELECT: ClassVar[bool] = True`（:403）、`TITLE: str | None = None`（:413）、`SUB_TITLE`（:420）、`ENABLE_COMMAND_PALETTE: ClassVar[bool] = True`（:427）、`NOTIFICATION_TIMEOUT: ClassVar[float] = 5`（:430）、`COMMAND_PALETTE_BINDING: ClassVar[str] = "ctrl+p"`（:441）、`CLICK_CHAIN_TIME_THRESHOLD: ClassVar[float] = 0.5`（:450）、`CLOSE_TIMEOUT: float | None = 5.0`（:467）、`TOOLTIP_DELAY: float = 0.5`（:470）。
- **F-T-061** App 默认 `BINDINGS`（:454-464）：`ctrl+q → quit`（show=False, priority=True）、`ctrl+c → help_quit`（show=False, system=True）。
- **F-T-062** `App.__init__(driver_class=None, css_path=None, watch_css=False, ansi_color=None)`（:572-578）；`features` 由 `parse_features(os.getenv("TEXTUAL", ""))` 解析；构造时 `super().__init__(classes=self.DEFAULT_CLASSES)`。
- **F-T-063** `App.run(*, headless=False, inline=False, inline_no_clear=False, mouse=True, size=None, auto_pilot=None, loop=None) -> ReturnType | None`（:2308）；`App.run_async(...)`（:2220）参数相同（无 `loop`），内部调用 `app._process_messages(...)`，结束时 `await asyncio.shield(app._shutdown())`，返回 `app.return_value`。
- **F-T-064** `App.push_screen(screen, callback=None, wait_for_dismiss=False, *, mode=None) -> AwaitMount | asyncio.Future`（:2895）：向原活动屏幕发 `events.ScreenSuspend()`、向新屏幕发 `events.ScreenResume()`；`mode` 未知抛 `UnknownModeError`；`wait_for_dismiss=True` 且不在 worker 中抛 `NoActiveWorker`；最后 `screen_change_signal.publish(next_screen)`。
- **F-T-065** `App.pop_screen() -> AwaitComplete`（:3096）、`switch_screen(screen) -> AwaitComplete`（:3001）、`install_screen(screen, name) -> None`（:3036）、`get_default_screen() -> Screen`（:1380）、`compose() -> ComposeResult`（:1393）。
- **F-T-066** `App.exit(result=None, return_code=0, message=None) -> None`（:1270）：置 `_exit=True`、存 `_return_value/_return_code`、`post_message(messages.ExitApp())`。
- **F-T-067** `App.notify(message, *, title="", severity="information", timeout=None, markup=True) -> None`（:4621）；docstring 声明该方法线程安全；severity 取值 information/warning/error。
- **F-T-068** App reactive 属性：`title: Reactive[str] = Reactive("", compute=False)`（:548）、`sub_title: Reactive[str] = Reactive("", compute=False)`（:550）、`app_focus = Reactive(True, compute=False)`（:553）、`theme: Reactive[str] = Reactive(constants.DEFAULT_THEME)`（:560）、`ansi_theme_dark = Reactive(MONOKAI, init=False)`（:563）、`ansi_theme_light = Reactive(ALABASTER, init=False)`（:566）、`ansi_color: Reactive[bool | None] = Reactive(None)`（:569）。
- **F-T-069** `App.switch_mode(mode) -> AwaitMount`（:2630，未知 mode 抛 `UnknownModeError`）；`App.remove_mode(mode) -> AwaitComplete`（:2699，移除活动 mode 抛 `ActiveModeError`）。
- **F-T-070** `App.call_from_thread(callback, *args, **kwargs)`（:1788）从其他线程调度回调；`async App.run_action(action, default_namespace=None, namespaces=None) -> bool`（:4223）；`App.set_focus(widget, scroll_visible=True)`（:3150）；`App.capture_mouse(widget)`（:3222）；`App.workers` 属性返回 `WorkerManager`（:959）。
- **F-T-071** `App.focused` 属性返回 `self.screen.focused`（:1290-1299）。

## worker.py / worker_manager.py / _work_decorator.py — 后台工作

- **F-T-072** `Worker(Generic[ResultType])` 定义于 `src/textual/worker.py:119`，构造签名 `__init__(node, work, *, name="", group="default", description="", exit_on_error=True, thread=False)`；`description` 超 1000 字符截断加 `"..."`；构造末尾 `post_message(self.StateChanged(self, self._state))`。
- **F-T-073** `WorkerState(enum.Enum)`：`PENDING=1`、`RUNNING=2`、`CANCELLED=3`、`ERROR=4`、`SUCCESS=5`。（`src/textual/worker.py:82-94`）
- **F-T-074** `Worker.StateChanged(Message, bubble=False, namespace="worker")` 携带 `worker` 与 `state` 字段。（`src/textual/worker.py:123`）
- **F-T-075** `Worker.run() -> ResultType` 按 `_thread_worker` 分派 `_run_threaded()` 或 `_run_async()`（:346）；`Worker.cancel()` 置 `_cancelled=True`、取消 `_task`、`cancelled_event.set()`（:416）；`Worker.wait()` 在 worker 内部调用抛 `DeadlockError`，PENDING 状态抛 `WorkerError`，ERROR 抛 `WorkerFailed`，CANCELLED 抛 `WorkerCancelled`（:423）。
- **F-T-076** 模块异常：`WorkerError`（:45）、`WorkerFailed(WorkerError)`（:49）、`WorkerCancelled(WorkerError)`（:61）；`WorkType` TypeAlias 为协程可调用/同步可调用/`Awaitable` 的 Union（:100-104）。
- **F-T-077** `WorkerManager`（`src/textual/worker_manager.py:24`）方法：`add_worker`（:65）、`start_all`（:129）、`cancel_all`（:134）、`cancel_group(node, group) -> list[Worker]`（:139）、`cancel_node(node) -> list[Worker]`（:158）、`async wait_for_complete(workers=None)`（:172）；构造接收 `app: App`。
- **F-T-078** `work` 装饰器（`src/textual/_work_decorator.py:74`）签名：`work(method=None, *, name="", group="default", exit_on_error=True, exclusive=False, description=None, thread=False)`；非协程函数未设 `thread=True` 时抛 `WorkerDeclarationError`（:112-115）。

## css/styles.py — 样式对象

- **F-T-079** 类层次：`RulesMap(TypedDict, total=False)`（:88）、`StylesBase`（:223）、`Styles(StylesBase)`（:886，含 `_rules: RulesMap` 字段）、`RenderStyles(StylesBase)`（:1334）。（`src/textual/css/styles.py`）
- **F-T-080** `StylesBase.ANIMATABLE` 集合（:226）包含：offset、padding、margin、width、height、min_width、min_height、max_width、max_height、auto_color、color、background、background_tint、opacity、position、text_opacity、tint、scrollbar 系列、link 系列、text_wrap、text_overflow、line_pad 等。
- **F-T-081** `StylesBase` 属性描述符示例：`display = StringEnumProperty(VALID_DISPLAY, "block", layout=True, display=True)`、`visibility = StringEnumProperty(VALID_VISIBILITY, "visible", layout=True)`、`layout = LayoutProperty()`、`color = ColorProperty(Color(255, 255, 255))`、`background = ColorProperty(Color(0, 0, 0))`、`opacity = PercentProperty(1.0)`、`padding = SpacingProperty(0)`、`margin = SpacingProperty(0)`、`width/height/min_*/max_* = ScalarProperty(None)`、`dock = StringEnumProperty(("top","right","bottom","left","none"), "none")`、`overflow_x/overflow_y = StringEnumProperty(("auto","hidden","visible"), "auto")`、`grid_size_rows/grid_size_columns = IntegerProperty(1)`、`box_sizing = StringEnumProperty(("content-box","border-box"), "content-box")`、`pointer = StringEnumProperty(("default","text","pointer","not-allowed"), "default")`。
- **F-T-082** `Styles.parse(css, read_from, *, node=None)` classmethod 解析 CSS 字符串返回 `Styles`（:772）；`get_transition(rule)` 仅当 `rule in cls.ANIMATABLE` 时从 `self.transitions` 返回过渡（:799-803）。

## css/stylesheet.py — 样式表

- **F-T-083** `Stylesheet.__init__(*, variables=None)`（`src/textual/css/stylesheet.py:145`）：初始化 `_rules: list[RuleSet]`、`_rules_map`、`_variables`、`source: dict[CSSLocation, CssSource]`、`_require_parse`、`_invalid_css`、`_parse_cache: LRUCache(64)`、`_style_parse_cache: LRUCache(1024 * 4)`。
- **F-T-084** `Stylesheet.add_source(css, read_from=None, is_default_css=False, tie_breaker=0, scope="")`（:333）：`read_from` 缺省为 `("", str(hash(css)))`；同位置相同 CSS 内容去重（仅更新 tie_breaker）；调用后置 `_require_parse = True`、`_rules_map = None`。
- **F-T-085** `Stylesheet.apply(node, *, animate=False, cache=None)`（:470）：按 `node._selector_names` 过滤规则，对每条匹配规则的声明按 `Specificity6` 降序排序取最高优先级值构建 `rules_map`，最终 `node._css_styles.merge_rules(rules_map)`；同时设置节点标志 `_has_hover_style`（含 "hover" 伪类）、`_has_focus_within`、`_has_order_style`、`_has_odd_or_even`。
- **F-T-086** `Stylesheet` 其他方法：`read(filename)`（:288）、`read_all(paths)`（:308）、`parse()`（:372）、`parse_style(style_text)`（:223）、`replace_rules(...)`（:636）、`update(root, animate=False)`（:703）、`update_nodes(nodes, animate=False)`（:713）；异常 `StylesheetParseError(StylesheetError)`（:34）、`StylesheetErrors`（:44，渲染错误面板含行号代码片段）。

## widgets/_button.py — Button

- **F-T-087** `Button(Widget, can_focus=True)` 定义于 `src/textual/widgets/_button.py:39`，`ALLOW_SELECT = False`；reactive：`label = reactive("", init=False)`、`variant = reactive("default", init=False)`、`compact = reactive(False, toggle_class="-textual-compact")`、`flat = reactive(False)`。
- **F-T-088** `Button.__init__(label=None, variant="default", *, name=None, id=None, classes=None, disabled=False, tooltip=None, action=None, compact=False, flat=False)`（:331）：`label is None` 时取 `self.css_identifier_styled`；`set_reactive(Button.label, Content.from_text(label))`；`active_effect_duration = 0.2`。
- **F-T-089** `Button.Pressed(Message)` 携带 `button` 属性与 `control` 属性（返回 button）；`Button.press() -> Self`：`disabled or not self.display` 时直接返回；`action is None` 时 `post_message(Button.Pressed(self))`，否则 `call_later(self.app.run_action, self.action, default_namespace=self._parent)`；`_on_click` 先 `event.stop()`。（`src/textual/widgets/_button.py:416-440`）
- **F-T-090** `Button` 类方法 `success`（:456）、`warning`（:491）、`error`（:526）创建对应变体按钮；`validate_variant` 对非法变体抛 `InvalidButtonVariant`（:388-393）；`watch_variant` 移除 `-{old}` 类并添加 `-{new}` 类（:395-397）；`watch_flat` 切换 `-style-flat`/`-style-default` 类（:399-401）。

## widgets/_input.py — Input

- **F-T-091** `Input(ScrollView)` 定义于 `src/textual/widgets/_input.py:71`；`BINDING_GROUP_TITLE = "Input"`（:74）；reactive：`value: Reactive[str] = reactive("", init=False)`（:253）、`selection = reactive(Selection.cursor(0))`（:265）、`placeholder = reactive("")`、`password = reactive(False)`、`_suggestion = reactive("")`、`restrict = var["str | None"](None)`、`type = var[InputType]("text")`、`max_length = var["int | None"](None)`、`valid_empty = var(False)`、`compact = reactive(False, toggle_class="-textual-compact")`。
- **F-T-092** `Input.__init__(value=None, placeholder="", highlighter=None, password=False, *, restrict=None, type="text", max_length=0, suggester=None, validators=None, validate_on=None, valid_empty=False, select_on_focus=True, name=None, id=None, classes=None, disabled=False, tooltip=None, compact=False)`（:354）；`validators` 单实例自动包装为列表；`validate_on` 缺省为全部可能值集合。
- **F-T-093** Input 消息（均为 `@dataclass` Message，含 `control` 属性）：`Changed`（:287，字段 input/value/validation_result）、`Submitted`（:310）、`Blurred`（:332）。
- **F-T-094** `Input.COMPONENT_CLASSES = {"input--cursor", "input--placeholder", "input--suggestion", "input--selection"}`；`cursor_position` 属性对应 `selection.end`；BINDINGS 含 `enter → submit`、`home,ctrl+a → home`、`ctrl+x/c/v → cut/copy/paste` 等（均 show=False）。
- **F-T-095** `Input.validate_selection(selection) -> Selection`（:512）与 `Input.validate(value) -> ValidationResult | None`（:570）。

## widgets/_data_table.py — DataTable

- **F-T-096** `DataTable(ScrollView, Generic[CellType], can_focus=True)` 定义于 `src/textual/widgets/_data_table.py:268`；reactive：`show_header = Reactive(True)`、`show_row_labels = Reactive(True)`、`fixed_rows = Reactive(0)`、`fixed_columns = Reactive(0)`、`zebra_stripes = Reactive(False)`、`header_height = Reactive(1)`、`show_cursor = Reactive(True)`、`cursor_type: Reactive[CursorType] = Reactive("cell")`、`cell_padding = Reactive(1)`、`cursor_coordinate = Reactive(Coordinate(0, 0), repaint=False, always_update=True)`、`hover_coordinate`（同构）。
- **F-T-097** `DataTable.add_column(label, *, width=None, key=None, default=None) -> ColumnKey`（:1611）：key 已存在抛 `DuplicateKey`；`width is None` 时列宽取内容测量宽度且 `auto_width=True`。`add_row(*cells, height=1, key=None, label=None) -> RowKey`（:1669）：cells 数超过列数抛 `ValueError`；首个单元格可用时发 `CellHighlighted`。
- **F-T-098** DataTable 消息类：`CellHighlighted`（:435）、`CellSelected`（:472）、`RowSelected`（:536）、`HeaderSelected`（:623）。
- **F-T-099** DataTable 数据 API：`update_cell`（:871）、`update_cell_at`（:915）、`get_cell(row_key, column_key)`（:932）、`get_cell_at(coordinate)`（:950）、`get_cell_coordinate`（:965）、`clear(columns=False) -> Self`（:1582）、`add_columns`（:1738）、`add_rows(rows) -> list[RowKey]`（:1776）、`remove_row(row_key)`（:1793，不存在抛 `RowDoesNotExist`）、`remove_column(column_key)`（:1832，不存在抛 `ColumnDoesNotExist`）。
- **F-T-100** DataTable BINDINGS：enter→select_cursor、up/down/left/right→cursor_*、pageup/pagedown→page_*、ctrl+home/ctrl+end→scroll_top/scroll_bottom、home/end→scroll_home/scroll_end（均 show=False）；COMPONENT_CLASSES 含 datatable--cursor、datatable--header、datatable--fixed、datatable--odd-row、datatable--even-row 等 9 项。

## widgets/_text_area.py — TextArea

- **F-T-101** `TextArea(ScrollView)` 定义于 `src/textual/widgets/_text_area.py:112`；reactive：`language = reactive(None, always_update=True, init=False)`（:460）、`theme = reactive("css", always_update=True, init=False)`（:471）、`selection = reactive(Selection.cursor(0), init=False)`（:479）、`show_line_numbers = reactive(False, init=False)`（:493）、`indent_width = reactive(4, init=False)`（:501）、`soft_wrap = reactive(True, init=False)`（:514）、`read_only = reactive(False)`（:517）。
- **F-T-102** `TextArea.__init__(text="", *, language=None, theme="css", soft_wrap=True, tab_behavior="focus", read_only=False, show_cursor=True, show_line_numbers=False, line_number_start=1, max_checkpoints=50, name=None, id=None, classes=None, disabled=False, tooltip=None, compact=False, highlight_cursor_line=True, placeholder="")`（:584）；构造中创建 `EditHistory(max_checkpoints, checkpoint_timer=2.0, checkpoint_max_characters=100)`、`Document(text)`、`WrappedDocument`、`DocumentNavigator`；`indent_type` 默认 `"spaces"`。
- **F-T-103** TextArea 消息：`Changed(Message)`（:554）与 `SelectionChanged(Message)`（:570），均为 `@dataclass` 且含 `control` 属性；编辑 API：`get_text_range(start, end) -> str`（:1658）、`move_cursor`（:2052）、`move_cursor_relative`（:2085）、`replace`（:2513）、`insert_text_at_cursor(text)`。
- **F-T-104** `TextAreaLanguage` 类（:99）含 `language: Language | None` 字段；`TextArea._languages` 字典存放用户经 `register_language` 注册的语言。

## driver.py 与 drivers/ — 驱动层

- **F-T-105** `Driver(ABC)` 定义于 `src/textual/driver.py:17`，构造签名 `__init__(app, *, debug=False, mouse=True, size=None)`；抽象方法：`write(data: str)`、`start_application_mode()`、`disable_input()`、`stop_application_mode()`；属性 `is_headless`/`is_inline`/`is_web`/`can_suspend` 默认均返回 `False`。
- **F-T-106** `Driver.send_message(message)` 经 `asyncio.run_coroutine_threadsafe(self._app._post_message(message), loop=self._loop)` 投递（:67-75）；`Driver.process_message(message)` 按 `cursor_origin` 偏移修正 `MouseEvent` 坐标，维护 `_down_buttons` 列表，并在按住按键的 MouseMove 中补发 MouseUp（:77-132）。
- **F-T-107** `Driver` 其他成员：`suspend_application_mode()`/`resume_application_mode()`（:157/:166）、`no_automatic_restart()` 上下文管理器（:177）、`open_url(url, new_tab=True)`（:195）、`deliver_binary(binary, *, delivery_key, save_path, open_method="download", encoding=None, mime_type=None, name=None)`（:208，线程中分块写文件，成功/失败分别发 `DeliveryComplete`/`DeliveryFailed`）、内嵌事件 `Driver.SignalResume(events.Event)`（:174）。
- **F-T-108** 驱动子类：`LinuxDriver(Driver)`（`src/textual/drivers/linux_driver.py:38`，含 `_enable_mouse_support`、`_enable_bracketed_paste`、`start_application_mode`、`stop_application_mode`、`run_input_thread`、`process_message`、`can_suspend` 等）、`LinuxInlineDriver(Driver)`（`src/textual/drivers/linux_inline_driver.py:28`）、`WindowsDriver(Driver)`（`src/textual/drivers/windows_driver.py:16`）、`WebDriver(Driver)`（`src/textual/drivers/web_driver.py:41`，`is_web` 返回 True，另有 `write_meta`、`on_meta`、`open_url`、`deliver_binary`、`_on_meta`）、`HeadlessDriver(Driver)`（`src/textual/drivers/headless_driver.py:10`，`is_headless` 返回 True）。
- **F-T-109** `src/textual/drivers/_input_reader.py` 按 `sys.platform == "win32"` 从 `_input_reader_windows` 或 `_input_reader_linux` 导入 `InputReader`；`src/textual/drivers/win32.py` 定义 Win32 结构体 `COORD`、`KEY_EVENT_RECORD`、`MOUSE_EVENT_RECORD`、`WINDOW_BUFFER_SIZE_RECORD`、`INPUT_RECORD` 与函数 `set_console_mode`、`get_console_mode`、`enable_application_mode`、`wait_for_handles` 及 `EventMonitor(threading.Thread)`。

## _on.py 与 pilot.py — 处理器装饰器与测试驾驶

- **F-T-110** `on(message_type: type[Message], selector: str | None = None, **kwargs: str)` 装饰器（`src/textual/_on.py:24`）声明消息处理器，可对消息 `control` 暴露的 widget 做 CSS 选择器匹配；模块异常 `OnDecoratorError`（:13）。
- **F-T-111** `Pilot(Generic[ReturnType])`（`src/textual/pilot.py:62`）构造接收 `app: App[ReturnType]`；异步方法：`press(*keys)`（:76）、`click(...)`（:192）、`hover(...)`（:349）、`pause(delay=None)`（:535）；`App.run_async` 在 `auto_pilot` 非空时创建 `Pilot(app)` 并在任务中执行回调（`src/textual/app.py:2258-2277`）。

## 交叉事实（消息流与继承链）

- **F-T-112** 继承链：`Message` ← `Event` ← 各事件；`MessagePump` ← `DOMNode` ← `Widget` ← `Screen`；`MessagePump` ← `DOMNode` ← `App`（`src/textual/message.py`、`events.py`、`message_pump.py`、`dom.py`、`widget.py`、`screen.py`、`app.py` 的类声明行）。
- **F-T-113** 消息分发命名约定：`Message.__init_subclass__` 生成 `handler_name`（F-T-003），`MessagePump._get_dispatch_methods` 以 `on_<handler_name>` 查找处理器（F-T-012），`@on` 装饰器注册的处理器优先于命名约定（`src/textual/message_pump.py:761-800`）。
- **F-T-114** reactive 更新链路：`Reactive._set` → `validate_<name>` → `_check_watchers` → `_compute` → `obj.refresh(repaint/layout/recompose)`（F-T-020）；`Widget.refresh` 置脏区并 `check_idle()`，实际刷新在下一 idle 事件执行（`src/textual/widget.py:4324-4376` docstring）。
- **F-T-115** CSS 应用链路：`Stylesheet.add_source` → `parse()` → `apply(node)` 按特异性合并到 `node._css_styles`（`RulesMap`）→ `DOMNode.styles`（`RenderStyles`）合并 `_css_styles` 与 `_inline_styles`（`src/textual/css/stylesheet.py:470`、`src/textual/dom.py:206-211`）。
