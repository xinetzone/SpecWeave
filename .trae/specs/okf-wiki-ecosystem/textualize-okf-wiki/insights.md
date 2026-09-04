---
stage: I
generated: 2026-09-01
inputs:
  - facts-rich.md (F-R-001..089, 89 条)
  - facts-textual.md (F-T-001..115, 115 条)
  - facts-satellites-1.md (F-FM-01..22 / F-TL-01..24 / F-TG-01..30 / F-RC-01..24, 100 条)
  - facts-satellites-2.md (F-SD-01..18 / F-SV-01..20 / F-SW-01..20, 58 条)
  - facts-ecosystem.md (F-ECO-01..15, 15 条)
total_facts: 377
---

# insights.md — Textualize 生态架构洞察与知识地图（I 阶段）

> 所有洞察仅基于 facts-*.md 中已登记的事实编号；每条证据均可回溯到源码文件。
> 无事实支撑的表述一律不写入本文档。

## 1. 核心洞察（5 个四元组）

### 洞察 1：rich 的渲染体系是"协议驱动的递归归约"——一切皆 renderable，终点是扁平 Segment 流

- **陈述**：rich 没有中心化的组件树或虚拟 DOM。`RenderableType = Union[ConsoleRenderable, RichCast, str]`（F-R-039），任何实现 `__rich__` 或 `__rich_console__` 的对象都可渲染；`Console.render` 对产出逐项判断，非 `Segment` 的结果递归再渲染（F-R-046）；最终货币是三元组 `Segment(text, style, control)`（F-R-024），18 个类方法全部操作 `Iterable[Segment]` 流（F-R-025）。
- **证据**：
  - F-R-001/F-R-002：`is_renderable` 三条件判定；`rich_cast` while 循环反复调用 `__rich__()`，用 `rich_visited_set` 防类型循环，用模块级乱码常量 `_GIBBERISH` 做哨兵返回 `repr()`
  - F-R-039：两个 `@runtime_checkable` Protocol 定义渲染协议
  - F-R-046：`Console.render` 递归路径（递归前 `reset_height()`）
  - F-R-024/F-R-025：Segment 结构与批量流式操作（`split_lines`/`adjust_line_length`/`divide` 等）
  - F-R-005/F-R-006：测量协议 `__rich_measure__` 同构嵌入（`Measurement.get` → `measure_renderables` 取 min/max 组合）
- **反常识点**：字符串本身就是一种 renderable（F-R-039 的 Union 含 `str`，F-R-046 中 str 经 `render_str` 处理）；防无限递归不靠深度计数而靠"已访问类型集合 + 随机属性名哨兵"（F-R-002）。Table/Panel/Markdown 等"组件"并非特殊机制，只是实现协议的普通对象（F-R-052/F-R-085/F-R-061 均实现 `__rich_console__`）。
- **行动建议**：rich 概念文档以「协议 → Console.render 递归 → Segment 流」为主线开篇（01/12 篇），所有组件文档统一表述为"协议的实现样例"，避免读者误以为存在组件注册机制。

### 洞察 2：textual = rich 渲染核 + 异步消息泵——DOM 树本质是"每个节点一台消息泵"的 actor 树

- **陈述**：textual 的继承链为 `MessagePump ← DOMNode ← Widget ← Screen`、`MessagePump ← DOMNode ← App`（F-T-112）。UI 的一切变化都经由消息：`post_message` 投递（跨线程时走 `loop.call_soon_threadsafe`，F-T-010），消息循环用 `can_replace` 合并同类消息后派发（F-T-015），Event 走 `on_event`、Message 走 `_on_message`（F-T-011）。reactive 属性变更最终也落到 `obj.refresh(...)` 并置脏区等待下一 idle（F-T-020、F-T-114）。
- **证据**：
  - F-T-112：完整继承链
  - F-T-008/F-T-016：`MessagePump` 构造与实例属性（`_message_queue` 相关状态、`_timers: WeakSet`、`message_signal`）
  - F-T-010/F-T-011/F-T-015：投递、派发、消息循环与合并
  - F-T-001..007：Message 基类（`bubble`/`no_dispatch`/`prevent_default`/`stop`/`_bubble_to`）
  - F-T-030：生命周期事件（Load/Idle/Mount/Unmount 等）全部 `bubble=False`，即生命周期不冒泡、交互冒泡
- **反常识点**：Widget 不是被"绘制"的，而是被"派发消息"的；定时器也是消息（`Timer(Event, bubble=False)`，F-T-035）。冒泡是默认行为（`bubble: ClassVar[bool] = True`，F-T-002），而鼠标事件显式声明 `bubble=True`（F-T-033）、焦点事件显式 `bubble=False`（F-T-034）——冒泡与否是逐消息类声明的协议而非框架硬编码。
- **行动建议**：textual 文档以「消息生命周期」为骨架（14 篇）：定义 Message 子类 → 自动生成 handler 名 → post → 队列合并 → MRO 派发；再讲 reactive 如何汇入同一刷新链路（15 篇）。

### 洞察 3：约定即注册——`__init_subclass__` 元编程贯穿 textual，类定义本身就是接线

- **陈述**：用户从不手写接线代码：`Message.__init_subclass__` 自动按 `camel_to_snake` 生成 `handler_name = f"on_{name}"`（F-T-003）；`DOMNode.__init_subclass__` 沿 MRO 收集 Reactive、合并 BINDINGS、收集 `compute_` 方法（F-T-037）；派发时 `@on` 装饰器注册的处理器优先于 `on_<name>` 命名约定（F-T-012、F-T-113）。
- **证据**：
  - F-T-003：深层嵌套类只保留最后两段（`A.B.C.D` → `C.D`）
  - F-T-012：沿 `__mro__` 先 `_decorated_handlers` 后命名约定；`_no_default_action` 置位终止 MRO 遍历
  - F-T-037：`inherit_css/inherit_bindings/inherit_component_classes` 三个继承开关
  - F-T-019/F-T-023：reactive 内部存储名 `_reactive_{name}`；`compute_<name>` 每次读取都重新计算
  - F-T-021：对带 compute 方法的 reactive 赋值抛 `AttributeError`（只读）
  - F-T-010：忘记调用 `super().__init__()` 时 `post_message` 抛 `RuntimeError` 并给出提示
- **反常识点**：魔法有精确的失效边界——嵌套消息类名只取最后两段（F-T-003）；compute reactive 是隐式只读的（F-T-021）；`prevent_default` 的生效机制是派发时包一层 `prevent` 上下文（F-T-011/F-T-013）而非修改消息本身。这些"暗规则"是用户踩坑高发区。
- **行动建议**：在 14/15/17 篇各设「约定与陷阱」小节，逐条列出自动生成规则（handler 名、存储名、合并规则）与对应异常（`AttributeError`/`RuntimeError`/`ReactiveError`），全部挂事实编号。

### 洞察 4：TUI 变 Web 应用靠"换驱动 + 二进制管道协议"，应用代码零改动

- **陈述**：textual 的 Driver 是抽象层（`Driver(ABC)`，抽象方法 `write`/`start_application_mode` 等，F-T-105），子类含 Linux/Windows/Web/Headless/Inline 五种（F-T-108）。textual-serve 与 textual-web 把应用作为子进程启动（`create_subprocess_shell`，F-SV-08/F-SW-14），仅通过环境变量 `TEXTUAL_DRIVER="textual.drivers.web_driver:WebDriver"` + `TEXTUAL_FPS=60` + `TEXTUAL_COLOR_SYSTEM=truecolor` + `COLUMNS/ROWS` 切换运行形态（F-SV-07/F-SW-14），再以「1 字节 type + 4 字节 big-endian size + payload」的包协议桥接 WebSocket ↔ stdio（F-SV-09/F-SV-10/F-SW-15，type 含 `D`/`M`/`P`），`__GANGLION__` 行作握手（F-SV-10/F-SW-15）。
- **证据**：
  - F-T-105/F-T-106/F-T-108：Driver 抽象、线程安全投递、五个子类
  - F-SV-07/F-SW-14：两处独立实现设置完全相同的驱动环境变量
  - F-SV-09/F-SV-10：包编码与 `readexactly` 读包循环；stderr 独立任务读取
  - F-SV-16：`_binary_encode` 基于 Bencode 扩展（None→`N`、bool→`T/F`、int→`i%ie`）
  - F-SV-20：README 自述 "Every Textual application is now a web application."、"With 3 lines of code"；`examples/serve.py` 全文 3 行
  - F-SW-11：`packets.py` 由 `packets.yml` 模板自动生成、"Do not hand edit"，18 个 PacketType
- **反常识点**：浏览器里的"终端"不是重写渲染器，而是 xterm.js 前端 + 子进程真 TUI 的字节流转发（F-SV-17 模板引用 `xterm.css`/`textual.js`）；文件下载走自定义分块协议（`deliver_chunk`/`deliver_chunk_request`，F-SV-12/F-SV-14），chunk 超时仅 4 秒（`DOWNLOAD_TIMEOUT = 4`，F-SV-13）。textual-serve 官方定位即"自托管版 textual-web"（F-SV-20）。
- **行动建议**：25/26 篇以「Driver 抽象 → 环境变量注入 → 包协议 → 下载管理」为叙事链，并在 19 篇（Driver 层）预埋 `TEXTUAL_DRIVER` 钩子；示例文档直接复刻 3 行 serve（examples/textual-serve-hello.md）。

### 洞察 5：12 个仓库是一个分形——卫星工具全部复用 rich/textual 原语，且自身就是教学材料

- **陈述**：卫星仓库不重新实现渲染/高亮/组件，而是直接继承或内嵌核心库原语：toolong 的 `LogHighlighter(RegexHighlighter)` 复用 `_combine_regex` 与 ipv4/ipv6/uuid/bool/number/str/path 命名组（F-TL-23），与 rich 的 `ReprHighlighter`（F-R-016）同构；trogon 的 `CommandBuilder` 直接用 `ReprHighlighter()`（F-TG-06）；frogmouth 的 Viewer 直接 yield rich/textual 的 `Markdown` 组件并定制 `parser_factory`（F-FM-05）；textual-dev 的 `DevtoolsConsole(Console)` 只设 `record=True` 再导出 segments（F-SD-13）；textual-demo 的 `run.py` 全文仅实例化 `textual.demo.DemoApp` 并 `run()`（F-ECO-03）。
- **证据**：
  - F-TL-23 ↔ F-R-016/F-R-012：高亮器复制-改造关系（toolong 甚至注释掉了 url 组、`>=10_000` 字符直接跳过）
  - F-TG-06/F-TG-12：trogon 通过 `introspect_click_app` 反射 Click 命令树生成表单，退出时 `os.execvp` 执行拼好的 CLI 字符串（F-TG-04）
  - F-FM-05/F-FM-15：frogmouth 复用 Markdown 组件 + 16 项 omnibox 别名命令
  - F-RC-01：rich-cli 依赖 `rich>=12.4,<13.0` 且钉住 `textual>=0.1.18,<0.2.0`（其 `PagerApp` 是早期 textual 应用，F-RC-23）
  - F-ECO-04：textual-demo README 自述 "A demonstration and teaching aid"
  - F-ECO-13..15：.github 仓库仅含 profile README（"Move at terminal velocity."）
- **反常识点**：卫星工具不是"产品副产品"，而是核心库的 dogfooding 与能力展示面——每个工具恰好示范一类机制（toolong=mmap 扫描+自适应时间戳格式轮转，F-TL-10/F-TL-13；trogon=反射式表单生成，F-TG-12；textual-dev=WebSocket 开发控制台，F-SD-09..12；rich-cli=rich 全渲染能力的 CLI 暴露，F-RC-13..16）。rich-cli 钉住旧版 textual 说明生态内版本耦合并非铁板一块（F-RC-01）。
- **行动建议**：20-26 篇每篇固定两节：「复用了哪些核心原语」（显式引用 F-R/F-T 编号）+「本工具示范的独有机制」；00 篇用依赖 DAG 图呈现三层结构（rich → textual → 卫星）。

## 2. 知识地图与学习路径

```
                    ┌──────────────────────────────┐
                    │ 00 生态总览（鸟瞰，首尾各读一遍） │
                    └──────────────┬───────────────┘
                                   ▼
   阶段1 入门 ──────────► 01 rich 协议与 Console ─► 02 Text 与标记语言
                                   ▼
   阶段2 rich 核心 ─────► 03 样式 ─► 04 高亮 ─► 05 Segment与测量 ─►
                          06 Table ─► 07 Panel/Box ─► 08 Markdown ─►
                          09 Progress ─► 10 Live ─► 11 Layout ─► 12 渲染管线深潜
                                   ▼
   阶段3 textual 核心 ──► 13 App 入口 ─► 14 消息系统 ─► 15 Reactive ─►
                          16 DOM/Widget/内置组件 ─► 17 事件与绑定 ─►
                          18 Screen 栈 ─► 19 CSS/Worker/Driver
                                   ▼
   阶段4 卫星工具 ──────► 20 rich-cli ─► 21 frogmouth ─► 22 toolong ─►
                          23 trogon ─► 24 textual-dev ─► 25 textual-serve ─► 26 textual-web
                                   ▼
   阶段5 生态总览（回环）► 重读 00 + references/index：依赖 DAG、版本矩阵、协议复用图谱
```

| 阶段 | 目标 | 文档 | 配套示例 |
|------|------|------|---------|
| 1 入门 | 建立生态方位感 + 第一次 rich 输出 | 00、01、02 | examples/rich-console-markup.md |
| 2 rich 核心 | 掌握协议→Segment 全渲染链 | 03-12 | examples/rich-table-panel.md、examples/rich-progress-track.md |
| 3 textual 核心 | 掌握消息驱动 TUI 编程模型 | 13-19 | examples/textual-minimal-app.md、examples/textual-reactive-counter.md、examples/textual-widget-messages.md |
| 4 卫星工具 | 按机制类型选读 7 仓库 | 20-26 | examples/trogon-tui-decorator.md、examples/textual-serve-hello.md |
| 5 生态总览 | 回环整合：复用关系与选型 | 重读 00 | — |

## 3. 概念文档清单（27 篇，concepts/）

> 覆盖原则：377 条事实每条恰好被一篇概念文档主覆盖；跨文档引用允许但不重复主覆盖。

### 3.1 生态总览（1 篇）

| 文件名 | 标题 | 覆盖事实 |
|--------|------|---------|
| `00-ecosystem-overview.md` | Textualize 生态总览：12 仓库依赖图谱与深度分层 | F-ECO-01..15；依赖与版本横切：F-RC-01、F-FM-01、F-TL-01、F-TG-01、F-SD-01、F-SV-01、F-SW-01、F-SV-20、F-SW-03、F-SW-05 |

### 3.2 rich 入门与核心（01-05，5 篇）

| 文件名 | 标题 | 覆盖事实 |
|--------|------|---------|
| `01-rich-console-and-protocol.md` | rich 入门：渲染协议与 Console | F-R-001..002、F-R-036..039、F-R-042..045、F-R-049 |
| `02-rich-text-and-markup.md` | Text 对象与控制台标记语言 | F-R-007..011、F-R-027..035 |
| `03-rich-style-system.md` | Style 样式系统与位掩码属性 | F-R-019..022 |
| `04-rich-highlighters.md` | Highlighter 体系：从正则到 ReprHighlighter | F-R-012..018 |
| `05-rich-segment-and-measure.md` | Segment 渲染货币与 Measurement 测量协议 | F-R-003..006、F-R-023..026 |

### 3.3 rich 进阶（06-12，7 篇）

| 文件名 | 标题 | 覆盖事实 |
|--------|------|---------|
| `06-rich-table.md` | Table：Column/Row 数据模型与宽度计算 | F-R-050..056 |
| `07-rich-panel-and-box.md` | Panel 与 Box：32 字符盒模型与 18 种边框 | F-R-085..089 |
| `08-rich-markdown.md` | Markdown：MarkdownIt 令牌到元素类的映射 | F-R-057..062 |
| `09-rich-progress.md` | Progress：任务、采样窗口与列插件体系 | F-R-063..078 |
| `10-rich-live.md` | Live：刷新线程与 RenderHook 拦截 | F-R-079..080 |
| `11-rich-layout.md` | Layout：row/column 分割器与区域映射 | F-R-081..084 |
| `12-rich-render-pipeline-and-export.md` | 渲染管线深潜：递归渲染、钩子、捕获与 HTML/SVG 导出 | F-R-040..041、F-R-046..048 |

### 3.4 textual 核心（13-19，7 篇）

| 文件名 | 标题 | 覆盖事实 |
|--------|------|---------|
| `13-textual-app-entry.md` | App 入口：类变量契约、run 循环与 notify | F-T-060..063、F-T-066..067、F-T-071 |
| `14-textual-message-system.md` | 消息系统：Message/MessagePump 与派发约定 | F-T-001..016、F-T-113 |
| `15-textual-reactive.md` | Reactive：validate→watcher→compute→refresh 链路 | F-T-017..023、F-T-040..041、F-T-114 |
| `16-textual-dom-widget-builtin.md` | DOMNode、Widget 与内置组件剖析（Button/Input/DataTable/TextArea） | F-T-036..039、F-T-042..043、F-T-045..053、F-T-087..104、F-T-112 |
| `17-textual-events-bindings.md` | 事件体系、按键绑定与 @on 装饰器 | F-T-024..035、F-T-044、F-T-110 |
| `18-textual-screen-stack.md` | Screen 栈：模式、焦点管理与屏幕切换 | F-T-054..059、F-T-064..065、F-T-068..069 |
| `19-textual-css-worker-driver.md` | CSS 引擎、Worker 后台任务与 Driver 驱动层 | F-T-070、F-T-072..086、F-T-105..109、F-T-111、F-T-115 |

### 3.5 卫星工具（20-26，7 仓库各 1 篇）

| 文件名 | 标题 | 覆盖事实 |
|--------|------|---------|
| `20-rich-cli.md` | rich-cli：rich 全能力的命令行暴露面 | F-RC-01..24 |
| `21-frogmouth.md` | frogmouth：终端 Markdown 浏览器（omnibox/历史/书签/forge 快览） | F-FM-01..22 |
| `22-toolong.md` | toolong：mmap 日志扫描、时间戳自适应与双平台 watcher | F-TL-01..24 |
| `23-trogon.md` | trogon：Click 内省到 TUI 表单的自动生成 | F-TG-01..30 |
| `24-textual-dev.md` | textual-dev：devtools 控制台、CLI 子命令与输出重定向 | F-SD-01..18 |
| `25-textual-serve.md` | textual-serve：三行代码把 TUI 变成 Web 应用 | F-SV-01..20 |
| `26-textual-web.md` | textual-web：ganglion 客户端、包协议与托管发布 | F-SW-01..20 |

### 3.6 覆盖度核对

| 事实文件 | 编号范围 | 条数 | 主覆盖文档 |
|---------|---------|------|-----------|
| facts-rich.md | F-R-001..089 | 89 | 01-12（全部分配，见 3.2/3.3） |
| facts-textual.md | F-T-001..115 | 115 | 13-19（全部分配，见 3.4） |
| facts-satellites-1.md | F-FM/F-TL/F-TG/F-RC | 100 | 21/22/23/20 |
| facts-satellites-2.md | F-SD/F-SV/F-SW | 58 | 24/25/26 |
| facts-ecosystem.md | F-ECO-01..15 | 15 | 00 |
| **合计** | | **377** | 27 篇概念文档 |

## 4. 示例文档清单（8 篇，examples/）

| 文件名 | 标题 | 依据事实 |
|--------|------|---------|
| `rich-console-markup.md` | rich 示例：Console.print 与标记语言样式 | F-R-042..044（print 签名）、F-R-011（markup render）、F-R-019..020（Style.parse/from_color） |
| `rich-table-panel.md` | rich 示例：Table + Panel + box 组合排版 | F-R-052..055（Table 构造/add_column/add_row）、F-R-085（Panel）、F-R-087..089（Box 常量） |
| `rich-progress-track.md` | rich 示例：track 一行进度条与自定义列 | F-R-077（模块级 track）、F-R-075（Progress.track）、F-R-069..070（构造与默认列） |
| `textual-minimal-app.md` | textual 示例：最小 App + compose + 事件处理 | F-T-060/063（App/run）、F-T-050（compose）、F-T-110（@on）、F-T-003（handler 名生成） |
| `textual-reactive-counter.md` | textual 示例：reactive 计数器与 watch 回调 | F-T-017..020（Reactive 构造/_set）、F-T-022（_watch）、F-T-048（refresh） |
| `textual-widget-messages.md` | textual 示例：Button.Pressed 与 Input.Submitted 消息流 | F-T-087..090（Button）、F-T-091..093（Input 消息）、F-T-005（stop/prevent_default） |
| `trogon-tui-decorator.md` | 卫星示例：@tui 装饰器为 Click CLI 生成 TUI | F-TG-05（tui 装饰器）、F-TG-17（typer init_tui）、F-TG-03..04（Trogon 构造与 execvp） |
| `textual-serve-hello.md` | 卫星示例：3 行代码发布 TUI 到浏览器 | F-SV-20（examples/serve.py 全文）、F-SV-02（Server 构造）、F-SV-18（serve 启动） |

## 5. 规划数量汇总

| 类别 | 数量 |
|------|------|
| 核心洞察（四元组） | 5 |
| 概念文档（concepts/） | 27（00 生态总览 ×1 + rich ×12 + textual ×7 + 卫星 ×7） |
| 示例文档（examples/） | 8（rich ×3 + textual ×3 + 卫星 ×2） |
| **内容文档合计** | **35** |

> E 阶段另需生成：references/ 信源登记 12 篇 + references/index.md、concepts/index.md、examples/index.md、根 index.md、log.md（骨架文件不计入上述 35 篇内容文档）。
